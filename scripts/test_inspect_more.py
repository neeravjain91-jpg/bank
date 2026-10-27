import pymupdf
import sys
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

for sid in ['bsb-003', 'bsb-004', 'bsb-005']:
    pdf_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/{sid}-statement.pdf"
    info_path = f"data/bankstatemently_benchmark/datasets/basic/{sid}/statement-info.json"
    with open(info_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    print("="*60)
    print(f"Statement: {sid} ({meta['bank']}) - Expected txns: {meta['transactionCount']}")
    doc = pymupdf.open(pdf_path)
    for pno in range(len(doc)):
        page = doc[pno]
        words = page.get_text('words')
        clean = [w for w in words if (w[3] - w[1]) < 25 and w[0] > 20]
        by_y = {}
        for w in clean:
            y = round(w[1], 1)
            matched = False
            for k in by_y:
                if abs(k - y) < 3.0:
                    by_y[k].append(w)
                    matched = True
                    break
            if not matched:
                by_y[y] = [w]
        lines = [f"{y:5.1f} | {' '.join(w[4] for w in sorted(by_y[y], key=lambda x: x[0]))}" for y in sorted(by_y.keys())]
        # print first few and last few lines
        print(f"  P{pno+1}: total {len(lines)} lines")
        for l in lines[:5]:
            print(f"    {l}")
