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

txns, acc, op, cl = assembler.assemble(doc, lines)
print(f"Total extracted: {len(txns)}")
for t in txns:
    if "DEPOT PAIE" in t.description or "NETFLIX" in t.description:
        print("Found:", t.date, t.description, t.amount)
