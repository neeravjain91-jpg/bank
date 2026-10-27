import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
from app.services.extractor import StatementExtractorService

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

svc = StatementExtractorService()
res = svc.extract_from_path('data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf')

print("="*60)
print(f"Extraction Status: {res.metadata.bank} | Txns: {res.metadata.transaction_count} | Time: {res.metadata.processing_time_seconds}s")
print(f"Reconciled: {res.validation.reconciled} | Total Debits: {res.validation.total_debits} | Total Credits: {res.validation.total_credits}")
print("Discrepancies:", res.validation.discrepancies)
print("Warnings:", res.validation.warnings)
print("="*60)
for idx, t in enumerate(res.transactions):
    print(f"[{idx+1:2d}] {t.date} | {t.direction.upper():6s} | {t.amount:10.2f} | Bal: {t.balance:10.2f} | Cat: {t.category:16s} | Desc: {t.description[:40]}")
