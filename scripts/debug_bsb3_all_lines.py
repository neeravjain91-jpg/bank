import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-003/bsb-003-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)

for pno in [1, 2]: # Page 2 and 3
    print(f"=== Page {pno+1} ===")
    for l in lines[pno]:
        print(f"  y={l.y0:5.1f} | {l.text}")
