import os, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
from app.extraction.coordinate_extractor import CoordinateExtractor
from app.extraction.profiles import get_profile
from app.extraction.table_detector import TableDetector
from app.extraction.assembler import TransactionAssembler

doc = pymupdf.open("data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf")
ce = CoordinateExtractor()
lines = ce.extract_document_lines(doc)
profile = get_profile("harbour_bank")
assembler = TransactionAssembler(profile=profile)

# Check line 19 on page 1
l19 = [l for l in lines[0] if "20 janv" in l.text][0]
print("Line 19 text:", l19.text)
pw = doc[0].rect.width
ph = doc[0].rect.height
role = assembler.line_classifier.predict_role(l19.text, l19.bbox, pw, ph)
print("Role:", role)
tab = assembler.table_detector.detect_table_on_page(lines[0], pw, 0)
row = assembler._init_transaction_row(l19, tab)
print("Original data:", row["original_data"])
txn = assembler._finalize_transaction(row)
print("Finalized txn:", txn)

# Check line on page 2: netflix
l_net = [l for l in lines[1] if "NETFLIX" in l.text][0]
print("Netflix line text:", l_net.text)
role_net = assembler.line_classifier.predict_role(l_net.text, l_net.bbox, pw, doc[1].rect.height)
print("Role Netflix:", role_net)
tab2 = assembler.table_detector.detect_table_on_page(lines[1], pw, 1)
row_net = assembler._init_transaction_row(l_net, tab2)
print("Netflix original data:", row_net["original_data"])
txn_net = assembler._finalize_transaction(row_net)
print("Netflix finalized txn:", txn_net)
