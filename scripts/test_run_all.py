import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
from app.services.extractor import StatementExtractorService

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

svc = StatementExtractorService()

statements = ['bsb-001', 'bsb-002', 'bsb-003', 'bsb-004', 'bsb-005']
total_expected = 0
total_extracted = 0

for sid in statements:
    pdf_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/{sid}-statement.pdf"
    info_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/statement-info.json"
    with open(info_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    exp_txns = meta['transactionCount']
    total_expected += exp_txns
    
    res = svc.extract_from_path(pdf_path, profile_id="auto")
    n_txns = len(res.transactions)
    total_extracted += n_txns
    
    print("="*65)
    print(f"[{sid}] {meta['bank']} ({meta['country']})")
    print(f"  Expected Txns: {exp_txns:2d} | Extracted: {n_txns:2d} | Match: {'YES' if n_txns == exp_txns else 'DIFF'}")
    print(f"  Profile Used : {res.metadata.profile_used} | Bank: {res.metadata.bank}")
    print(f"  Reconciled   : {res.validation.reconciled} | Discrepancies: {res.validation.discrepancy_count}")
    print(f"  Total Debits : {res.validation.total_debits} | Total Credits: {res.validation.total_credits}")
    if res.validation.warnings:
        print(f"  Warnings     : {res.validation.warnings[:2]}")
    if res.transactions:
        t0 = res.transactions[0]
        t_end = res.transactions[-1]
        print(f"  First Txn    : {t0.date} | {t0.direction} {t0.amount} | {t0.description[:35]}")
        print(f"  Last Txn     : {t_end.date} | {t_end.direction} {t_end.amount} | {t_end.description[:35]}")

print("="*65)
print(f"OVERALL SUMMARY: Extracted {total_extracted} / {total_expected} expected transactions.")
