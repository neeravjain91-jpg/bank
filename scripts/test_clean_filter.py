import pymupdf
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

doc = pymupdf.open('data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf')
page = doc[1]
words = page.get_text('words')
# filter watermarks and left margin rotated text
clean_words = [w for w in words if (w[3] - w[1]) < 25 and w[0] > 25]

by_y = {}
for w in clean_words:
    y = round(w[1], 1)
    matched = False
    for k in by_y:
        if abs(k - y) < 3.0:
            by_y[k].append(w)
            matched = True
            break
    if not matched:
        by_y[y] = [w]

print('--- Cleaned Lines on Page 2 ---')
for y in sorted(by_y.keys()):
    if 240 <= y <= 730:
        row = sorted(by_y[y], key=lambda x: x[0])
        print(f"y={y:5.1f} | {' '.join(w[4] for w in row)}")
