import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor
from app.extraction.profiles import get_profile
from app.extraction.assembler import TransactionAssembler

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)
profile = get_profile("harbour_bank")
assembler = TransactionAssembler(profile=profile)

# Run step-by-step
txns, accounts, op, cl = assembler.assemble(doc, lines)
print("Finished assemble. Transactions added:")
for idx, t in enumerate(txns):
    print(f"[{idx+1:2d}] {t.date} | {t.amount} | {t.description}")
