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

# Let's inspect line processing around line 19
active_table = None
in_progress_row = None
for pno in range(len(doc)):
    page_lines = lines[pno]
    pw = doc[pno].rect.width
    ph = doc[pno].rect.height
    pt = assembler.table_detector.detect_table_on_page(page_lines, pw, pno)
    if pt:
        active_table = pt
    for l in page_lines:
        if active_table is None:
            continue
        if l.page_num == active_table.page_num and l.y0 <= active_table.header_y0:
            continue
        role = assembler.line_classifier.predict_role(l.text, l.bbox, pw, ph)
        is_start = (role == "TRANSACTION_START") or assembler._starts_with_date_pattern(l.text)
        if "20 janv" in l.text or "UBER COURSE" in l.text or "NETFLIX" in l.text:
            print(f"P{pno+1} y={l.y0:.1f} | role={role} | is_start={is_start} | in_prog={in_progress_row is not None} | {l.text[:40]}")
        
        if is_start:
            if in_progress_row is not None:
                t = assembler._finalize_transaction(in_progress_row)
                if "20 janv" in in_progress_row["original_data"].get("Détails", ""):
                    print("  --> Finalizing 20 janv:", t)
            in_progress_row = assembler._init_transaction_row(l, active_table)
            if "20 janv" in l.text:
                print("  --> Initialized 20 janv row:", in_progress_row["original_data"])
