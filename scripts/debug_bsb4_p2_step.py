import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.extraction.coordinate_extractor import CoordinateExtractor
from app.extraction.profiles import get_profile
from app.extraction.assembler import TransactionAssembler

doc = pymupdf.open('data/bankstatemently_benchmark/datasets/basic/bsb-004/bsb-004-statement.pdf')
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)
profile = get_profile('silk_road')
assembler = TransactionAssembler(profile=profile)

pno = 1 # Page 2
page_lines = lines[pno]
pw = doc[pno].rect.width
ph = doc[pno].rect.height
pt = assembler.table_detector.detect_table_on_page(page_lines, pw, pno)
print("Page 2 table header y0:", pt.header_y0 if pt else None)

for l in page_lines:
    if pt and l.y0 <= pt.header_y0:
        continue
    candidate_cols = assembler.table_detector._build_column_intervals(l, pw)
    print(f"y={l.y0:.1f} | cand_cols={len(candidate_cols)} | text={l.text[:50]}")
