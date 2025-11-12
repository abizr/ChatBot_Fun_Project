from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from docx import Document
from PyPDF2 import PdfReader

from .utils import chunk_text

try:  # pragma: no cover - optional dependency on deployed env
    from pdf2image import convert_from_bytes
except Exception:
    convert_from_bytes = None

try:  # pragma: no cover - optional dependency on deployed env
    import pytesseract
except Exception:
    pytesseract = None


@dataclass
class DocumentBundle:
    text: str
    chunks: List[str]
    metadata: dict
    diagnostics: List[str]


class DocumentIngestor:
    """Handles extraction + chunking for uploaded documents."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120, enable_ocr: bool = True):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.enable_ocr = enable_ocr

    def ingest(self, file_name: str, file_bytes: bytes) -> DocumentBundle:
        suffix = Path(file_name).suffix.lower()
        text = ""
        diagnostics: List[str] = []

        if suffix == ".pdf":
            text, diagnostics = self._extract_pdf(file_bytes)
        elif suffix in {".docx", ".doc"}:
            text, diagnostics = self._extract_docx(file_bytes)
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
            diagnostics.append(f"Processed as plain text ({suffix or 'unknown'}).")

        chunks = chunk_text(text, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        metadata = {
            "file_name": file_name,
            "num_chunks": len(chunks),
            "num_chars": len(text),
        }

        return DocumentBundle(text=text, chunks=chunks, metadata=metadata, diagnostics=diagnostics)

    def _extract_pdf(self, file_bytes: bytes) -> Tuple[str, List[str]]:
        buffer = io.BytesIO(file_bytes)
        diagnostics: List[str] = []
        text_parts: List[str] = []

        try:
            reader = PdfReader(buffer)
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    extracted = page.extract_text() or ""
                    text_parts.append(extracted)
                except Exception as page_error:  # pragma: no cover - page-specific errors are rare
                    diagnostics.append(f"Failed to read text on page {page_num}: {page_error}")
        except Exception as exc:
            diagnostics.append(f"PDF parsing error: {exc}")

        combined = "\n".join(text_parts).strip()
        if combined or not self.enable_ocr:
            return combined, diagnostics

        ocr_text, ocr_diag = self._extract_pdf_with_ocr(file_bytes)
        diagnostics.extend(ocr_diag)
        return ocr_text, diagnostics

    def _extract_pdf_with_ocr(self, file_bytes: bytes) -> Tuple[str, List[str]]:
        diagnostics: List[str] = []
        if not self.enable_ocr:
            diagnostics.append("OCR disabled by configuration.")
            return "", diagnostics
        if convert_from_bytes is None or pytesseract is None:
            diagnostics.append("OCR dependencies missing (pdf2image/pytesseract). Skipping OCR.")
            return "", diagnostics
        try:
            images = convert_from_bytes(file_bytes, dpi=300)
        except Exception as exc:
            diagnostics.append(f"OCR conversion failed: {exc}. Confirm poppler is installed.")
            return "", diagnostics

        ocr_text_parts: List[str] = []
        for page_num, image in enumerate(images, start=1):
            try:
                ocr_text_parts.append(pytesseract.image_to_string(image))
            except Exception as exc:  # pragma: no cover
                diagnostics.append(f"OCR failed on page {page_num}: {exc}")

        diagnostics.append("OCR extraction completed.")
        return "\n".join(ocr_text_parts), diagnostics

    def _extract_docx(self, file_bytes: bytes) -> Tuple[str, List[str]]:
        buffer = io.BytesIO(file_bytes)
        diagnostics: List[str] = []
        try:
            doc = Document(buffer)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs), diagnostics
        except Exception as exc:
            diagnostics.append(f"DOCX parsing error: {exc}")
            return "", diagnostics


__all__ = ["DocumentBundle", "DocumentIngestor"]
