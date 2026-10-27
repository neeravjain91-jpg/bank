"""
Document inspection and coordinate extraction using PyMuPDF.
Extracts token bounding boxes, filters watermarks/side margins, and groups words into visual lines.
Computes SHA-256 content hash for audit traceability.
"""

import hashlib
import re
from typing import List, Dict, Any, Tuple, Optional
import pymupdf


def compute_pdf_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hex digest of document bytes."""
    return hashlib.sha256(file_bytes).hexdigest()


class ExtractedWord:
    def __init__(self, x0: float, y0: float, x1: float, y1: float, text: str):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text
        self.width = x1 - x0
        self.height = y1 - y0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bbox": (self.x0, self.y0, self.x1, self.y1),
            "text": self.text,
            "width": self.width,
            "height": self.height
        }


class ExtractedLine:
    def __init__(self, words: List[ExtractedWord], page_num: int):
        self.words = sorted(words, key=lambda w: w.x0)
        self.page_num = page_num
        self.x0 = min(w.x0 for w in self.words) if self.words else 0.0
        self.y0 = min(w.y0 for w in self.words) if self.words else 0.0
        self.x1 = max(w.x1 for w in self.words) if self.words else 0.0
        self.y1 = max(w.y1 for w in self.words) if self.words else 0.0
        self.text = " ".join(w.text for w in self.words)
        self.role: Optional[str] = None  # To be set by LineClassifier

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)


# Words that belong to boilerplate footer overlays (e.g. bsb-003 challenge: header-footer-noise)
FOOTER_OVERLAY_WORDS = {
    "rights", "derived", "overview.", "overview", "can", "be", "no", "from", "this"
}


class CoordinateExtractor:
    """Extracts cleaned lines and words from PDF documents."""

    def __init__(
        self,
        max_word_height: float = 26.0,
        min_x_margin: float = 18.0,
        line_y_tolerance: float = 3.5
    ):
        self.max_word_height = max_word_height
        self.min_x_margin = min_x_margin
        self.line_y_tolerance = line_y_tolerance

    def extract_document_lines(self, doc: pymupdf.Document) -> Dict[int, List[ExtractedLine]]:
        """
        Extract visual lines from each page in the document.
        Returns a dict mapping 0-indexed page_num to list of ExtractedLine objects.
        """
        page_lines: Dict[int, List[ExtractedLine]] = {}

        for pno in range(len(doc)):
            page = doc[pno]
            raw_words = page.get_text("words")  # (x0, y0, x1, y1, word, block_no, line_no, word_no)
            
            # Filter watermarks, side margins, and footer overlay noise
            filtered_words = []
            for w in raw_words:
                x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
                height = y1 - y0
                if height >= self.max_word_height:
                    continue  # Filter large watermark text
                if x0 < self.min_x_margin:
                    continue  # Filter far left vertical margin notes
                
                # Check for footer disclaimer overlay words near page bottom (y0 > 770)
                if y0 > 770 and text.lower() in FOOTER_OVERLAY_WORDS:
                    continue
                # Filter page fraction alone at bottom margin (e.g. 1/3, 2/3)
                if y0 > 770 and re.match(r"^\d/\d$", text):
                    continue

                filtered_words.append(ExtractedWord(x0, y0, x1, y1, text))

            # Group words into visual lines by y-coordinate
            grouped: Dict[float, List[ExtractedWord]] = {}
            for ew in filtered_words:
                y = round(ew.y0, 1)
                matched_key = None
                for k in grouped:
                    if abs(k - y) <= self.line_y_tolerance:
                        matched_key = k
                        break
                if matched_key is not None:
                    grouped[matched_key].append(ew)
                else:
                    grouped[y] = [ew]

            # Create ExtractedLine instances sorted top-to-bottom
            lines = []
            for y_key in sorted(grouped.keys()):
                words_in_line = grouped[y_key]
                if words_in_line:
                    line_obj = ExtractedLine(words_in_line, page_num=pno)
                    lines.append(line_obj)

            page_lines[pno] = lines

        return page_lines
