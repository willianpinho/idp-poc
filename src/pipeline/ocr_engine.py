"""OCR engine using pytesseract for scanned/image PDFs."""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OCRPageResult:
    page_number: int
    text: str
    confidence: float  # 0.0 - 1.0


@dataclass
class OCRResult:
    pages: list[OCRPageResult] = field(default_factory=list)
    engine: str = "tesseract"
    applied: bool = False
    pages_applied: list[int] = field(default_factory=list)

    @property
    def average_confidence(self) -> float:
        if not self.pages:
            return 0.0
        return sum(p.confidence for p in self.pages) / len(self.pages)


def run_ocr(pdf_bytes: bytes, pages_to_ocr: list[int] | None = None) -> OCRResult:
    """Run OCR on specified pages of a PDF.

    Args:
        pdf_bytes: Raw PDF file bytes
        pages_to_ocr: List of 0-indexed page numbers to OCR. If None, OCR all pages.

    Returns:
        OCRResult with extracted text and confidence scores per page.
    """
    result = OCRResult()

    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError:
        logger.warning("pytesseract or pdf2image not installed, skipping OCR")
        return result

    try:
        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes, dpi=300)
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        return result

    for i, image in enumerate(images):
        if pages_to_ocr is not None and i not in pages_to_ocr:
            continue

        try:
            # Get text with confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Extract text
            text_parts = []
            confidences = []
            for j, conf in enumerate(data["conf"]):
                conf_val = int(conf) if conf != -1 else 0
                if conf_val > 0:
                    text_parts.append(data["text"][j])
                    confidences.append(conf_val)

            text = " ".join(t for t in text_parts if t.strip())
            avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            result.pages.append(
                OCRPageResult(
                    page_number=i,
                    text=text,
                    confidence=round(avg_conf, 3),
                )
            )
            result.pages_applied.append(i)
            result.applied = True

        except Exception as e:
            logger.error(f"OCR failed for page {i}: {e}")
            result.pages.append(
                OCRPageResult(
                    page_number=i,
                    text="",
                    confidence=0.0,
                )
            )

    return result
