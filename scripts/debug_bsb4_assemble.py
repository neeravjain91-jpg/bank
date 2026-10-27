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

txns, accs, op, cl = assembler.assemble(doc, lines)
print(f"Silk Road Assemble returned: {len(txns)} transactions!")
