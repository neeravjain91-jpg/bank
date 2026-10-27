import os, sys
sys.path.insert(0, os.path.abspath("."))
import json
from app.services.extractor import StatementExtractorService

svc = StatementExtractorService()
res = svc.extract_from_path("data/bankstatemently_benchmark/datasets/basic/bsb-004/bsb-004-statement.pdf", profile_id="silk_road")
print(f"Silk Road extracted {len(res.transactions)} txns:")
for i, t in enumerate(res.transactions):
    print(f"[{i+1:2d}] {t.date} | {t.account_id:18s} | {t.direction:6s} | {t.amount:10.2f} | Bal: {t.balance} | Desc: {t.description[:35]}")
