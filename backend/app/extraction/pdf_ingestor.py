import fitz  # PyMuPDF
import os
from typing import Any, List, Dict

class PDFIngestor:
    def __init__(self, use_ocr_fallback: bool = True):
        self.use_ocr_fallback = use_ocr_fallback

    def extract_text_page_aware(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text page by page.
        Returns a list of dicts: [{'page': 1, 'text': '...', 'ocr_used': False}]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        doc = fitz.open(pdf_path)
        pages_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            ocr_used = False

            # If text is too short, run OCR fallback
            if len(text) < 50 and self.use_ocr_fallback:
                text = self._run_ocr_fallback(page)
                ocr_used = True

            pages_content.append({
                "page": page_num + 1,
                "text": text,
                "ocr_used": ocr_used
            })

        doc.close()
        return pages_content

    def _run_ocr_fallback(self, page) -> str:
        """Pluggable OCR via Tesseract (pytesseract)."""
        try:
            import pytesseract
            from PIL import Image
            import io

            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            print(f"OCR fallback failed on page: {str(e)}")
            return ""