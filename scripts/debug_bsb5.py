import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)

for pno in [0, 1]:
    print(f"=== Page {pno+1} ===")
    for l in lines[pno]:
        if any(w in l.text.lower() for w in ["janv", "févr", "détails", "solde", "chèques", "dépôts", "$"]):
            print(f"  y={l.y0:5.1f} | {l.text}")
