import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor
from app.models.line_classifier import LineClassifier

doc = pymupdf.open('data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf')
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)
clf = LineClassifier()

page2 = lines[1]
pw = doc[1].rect.width
ph = doc[1].rect.height
prev_role = None

for l in page2:
    if l.y0 > 182:
        role = clf.predict_role(l.text, l.bbox, pw, ph, prev_role)
        prev_role = role
        print(f"y={l.y0:5.1f} | role={role:25s} | text={l.text[:50]}")
