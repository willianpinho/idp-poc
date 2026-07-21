"""Tests for PDF text/metadata extraction, exercised against a real sample
PDF from sample-pdfs/ -- real pypdf parsing, no mocks, no network."""

from pathlib import Path

from src.pipeline.pdf_parser import parse_pdf

SAMPLE_PDF = Path(__file__).parent.parent / "sample-pdfs" / "01_contract_software_development.pdf"


class TestParsePdf:
    def test_extracts_text_from_a_real_pdf(self):
        pdf_bytes = SAMPLE_PDF.read_bytes()
        result = parse_pdf(pdf_bytes)

        assert result.page_count > 0
        assert len(result.pages) == result.page_count
        assert "SOFTWARE DEVELOPMENT AGREEMENT" in result.full_text.upper()

    def test_flags_pages_with_substantial_text_as_has_text(self):
        pdf_bytes = SAMPLE_PDF.read_bytes()
        result = parse_pdf(pdf_bytes)

        assert len(result.has_text) == result.page_count
        assert result.has_text[0] is True

    def test_full_text_joins_pages_with_double_newline(self):
        pdf_bytes = SAMPLE_PDF.read_bytes()
        result = parse_pdf(pdf_bytes)

        assert result.full_text == "\n\n".join(result.pages)
