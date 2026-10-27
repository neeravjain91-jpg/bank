import os, sys
sys.path.insert(0, os.path.abspath("."))
from app.services.extractor import StatementExtractorService

svc = StatementExtractorService()
res = svc.extract_from_path("data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf")
print(f"Extracted {len(res.transactions)} txns:")
for i, t in enumerate(res.transactions):
    print(f"[{i+1:2d}] {t.date} | {t.direction:6s} | {t.amount:10.2f} | Bal: {t.balance} | Desc: {t.description}")
