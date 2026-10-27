import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor
from app.extraction.profiles import get_profile
from app.extraction.table_detector import TableDetector

doc = pymupdf.open('data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf')
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)
profile = get_profile("straits_capital")
td = TableDetector(profile=profile)

for pno in range(len(doc)):
    page_lines = lines[pno]
    tab = td.detect_table_on_page(page_lines, doc[pno].rect.width, pno)
    print(f"Page {pno+1}: lines={len(page_lines)}, Table found={tab is not None}")
    if tab:
        print("  Header:", tab.header_line.text)
        print("  Cols:", [(c.role, c.label, c.x0, c.x1) for c in tab.columns])
