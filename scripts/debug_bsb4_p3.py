import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-004/bsb-004-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)

for pno in [2, 3, 4]:
    print(f"=== Page {pno+1} ===")
    for l in lines[pno]:
        if any(w in l.text.lower() for w in ["sep", "deposit", "withdrawal", "balance", "total", "hkd", "usd", "account"]):
            print(f"  y={l.y0:5.1f} | {l.text}")
