import pymupdf
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

doc = pymupdf.open('data/bankstatemently_benchmark/datasets/basic/bsb-002/bsb-002-statement.pdf')
page = doc[2] # page 3 (0-indexed)
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

for y in sorted(by_y.keys()):
    if 140 <= y <= 750:
        row = sorted(by_y[y], key=lambda x: x[0])
        print(f"y={y:5.1f} | {' '.join(w[4] for w in row)}")
