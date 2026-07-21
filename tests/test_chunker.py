"""Tests for the sliding-window text chunker used by the RAG pipeline."""

from src.pipeline.chunker import chunk_text, estimate_tokens


class TestEstimateTokens:
    def test_estimates_roughly_one_token_per_four_chars(self):
        assert estimate_tokens("a" * 40) == 10

    def test_empty_string_is_zero_tokens(self):
        assert estimate_tokens("") == 0


class TestChunkTextEdgeCases:
    def test_empty_pages_list_returns_no_chunks(self):
        assert chunk_text([]) == []

    def test_pages_with_only_whitespace_return_no_chunks(self):
        assert chunk_text(["   ", "\n\n"]) == []

    def test_single_page_shorter_than_window_produces_one_chunk(self):
        chunks = chunk_text(["short document text"], chunk_size=512, chunk_overlap=50)

        assert len(chunks) == 1
        assert chunks[0].index == 0
        assert chunks[0].content == "short document text"
        assert chunks[0].page_numbers == [0]
        assert chunks[0].token_count == estimate_tokens("short document text")


class TestChunkTextSlidingWindow:
    def _long_unbroken_text(self, length: int) -> str:
        # No spaces/newlines/periods so the sentence-boundary search inside
        # chunk_text() cannot find a break point -- this makes chunk
        # boundaries land at exact, predictable character offsets.
        return "A" * length

    def test_splits_into_multiple_overlapping_chunks(self):
        # chunk_size=10 tokens -> 40 chars, chunk_overlap=2 tokens -> 8 chars.
        pages = [self._long_unbroken_text(100)]
        chunks = chunk_text(pages, chunk_size=10, chunk_overlap=2)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.content) <= 40

        # Consecutive chunks must overlap: the tail of chunk[i] reappears at
        # the head of chunk[i + 1].
        for prev_chunk, next_chunk in zip(chunks, chunks[1:]):
            overlap_tail = prev_chunk.content[-8:]
            assert overlap_tail in next_chunk.content

    def test_first_and_last_chunk_capture_the_true_boundaries(self):
        # Distinct markers at the start and end let us prove the algorithm
        # doesn't truncate the tail or misalign the head -- a uniform-char
        # string can't detect that, since every substring looks identical.
        text = "HEAD" + ("x" * 92) + "TAIL"
        chunks = chunk_text([text], chunk_size=10, chunk_overlap=2)

        assert chunks[0].content.startswith("HEAD")
        assert chunks[-1].content.endswith("TAIL")

    def test_exact_multiple_of_chunk_size_does_not_produce_trailing_empty_chunk(self):
        # 80 chars is exactly 2x the 40-char window.
        pages = [self._long_unbroken_text(80)]
        chunks = chunk_text(pages, chunk_size=10, chunk_overlap=0)

        assert all(chunk.content for chunk in chunks)
        assert sum(len(c.content) for c in chunks) == 80

    def test_explicit_zero_overlap_is_respected_not_silently_replaced(self):
        # Regression test: chunk_overlap=0 was being replaced by
        # settings.chunk_overlap (50) because `0 or default` treats 0 as
        # falsy. That collapsed the sliding window to a 1-char step and
        # produced dozens of near-duplicate chunks instead of exactly 2.
        pages = [self._long_unbroken_text(80)]
        chunks = chunk_text(pages, chunk_size=10, chunk_overlap=0)

        assert len(chunks) == 2
        assert chunks[0].content == "A" * 40
        assert chunks[1].content == "A" * 40

    def test_indices_are_sequential(self):
        pages = [self._long_unbroken_text(200)]
        chunks = chunk_text(pages, chunk_size=10, chunk_overlap=2)

        assert [c.index for c in chunks] == list(range(len(chunks)))


class TestChunkTextPageTracking:
    def test_tracks_originating_page_for_single_page_chunk(self):
        chunks = chunk_text(["page one content"], chunk_size=512, chunk_overlap=50)
        assert chunks[0].page_numbers == [0]

    def test_chunk_spanning_multiple_short_pages_lists_all_pages(self):
        pages = ["first page", "second page", "third page"]
        chunks = chunk_text(pages, chunk_size=512, chunk_overlap=50)

        # All three short pages fit inside a single 512-token window.
        assert len(chunks) == 1
        assert chunks[0].page_numbers == [0, 1, 2]
