import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-003/bsb-003-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)

print("=== Page 1 Lines ===")
for l in lines[0]:
    print(f"  y={l.y0:5.1f} | {l.text}")
