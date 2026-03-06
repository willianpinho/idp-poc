"""PDF text extraction using pypdf."""

import io
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFParseResult:
    def __init__(self):
        self.pages: list[str] = []
        self.page_count: int = 0
        self.metadata: dict = {}
        self.has_text: list[bool] = []

    @property
    def full_text(self) -> str:
        return "\n\n".join(self.pages)


def parse_pdf(pdf_bytes: bytes) -> PDFParseResult:
    """Extract text and metadata from a PDF using pypdf."""
    result = PDFParseResult()

    reader = PdfReader(io.BytesIO(pdf_bytes))
    result.page_count = len(reader.pages)

    # Extract metadata
    meta = reader.metadata
    if meta:
        result.metadata = {
            "title": meta.title,
            "author": meta.author,
            "subject": meta.subject,
            "creator": meta.creator,
            "producer": meta.producer,
        }

    # Extract text per page
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        result.pages.append(text)
        has_content = len(text) > 50  # Minimum chars to consider page has text
        result.has_text.append(has_content)
        logger.debug(f"Page {i + 1}: {len(text)} chars, has_text={has_content}")

    return result
