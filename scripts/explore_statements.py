import json
import os
import sys
import pymupdf

# ensure stdout handles utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def explore():
    statements = ['bsb-001', 'bsb-002', 'bsb-003', 'bsb-004', 'bsb-005']
    for sid in statements:
        pdf_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/{sid}-statement.pdf"
        info_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/statement-info.json"
        if not os.path.exists(pdf_path) or not os.path.exists(info_path):
            print(f"Skipping {sid}, not found")
            continue
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        
        doc = pymupdf.open(pdf_path)
        print("="*60)
        print(f"Statement ID: {sid} | Bank: {info.get('bank')} | Pages: {len(doc)} | Expected Txns: {info.get('transactionCount')}")
        print(f"Currency: {info.get('currency')} | DateFormat: {info.get('dateFormat')}")
        print("Columns:", [c['label'] for c in info.get('columns', [])])
        print("Challenges:", info.get('challenges', []))
        
        for pno in range(len(doc)):
            page = doc[pno]
            text = page.get_text()
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            print(f"  Page {pno+1}: {len(lines)} non-empty lines")
            # print sample lines
            table_lines = [l for l in lines if any(char.isdigit() for char in l) and len(l) > 10][:3]
            print(f"    Sample data lines: {table_lines}")

if __name__ == '__main__':
    explore()
