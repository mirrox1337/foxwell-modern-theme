"""Give the car-brand and region pictures under Vehicles/ a dark background.

    python tools/dark_vehicles.py <card dump>/Vehicles <output folder>

Only menu pictures whose corners are white are changed; anything under a Res folder is skipped. Header and trailing bytes are kept.
"""
import os, sys
from collections import deque
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
BG = (10, 15, 28)

def convert(path):
    raw = open(path, 'rb').read()
    im = Image.open(path)
    if im.mode != 'RGB' or raw[28] != 24:
        return None
    w, h = im.size
    px = im.load()
    white = lambda p: min(p) >= 238
    if not all(white(px[x, y]) for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))):
        return raw            # already dark: copied as is, no_white.py handles its white text
    # flood the white background in from the edges
    bgm = [[False] * w for _ in range(h)]
    q = deque((x, y) for x in range(w) for y in (0, h - 1)) + deque((x, y) for y in range(h) for x in (0, w - 1))
    while q:
        x, y = q.popleft()
        if 0 <= x < w and 0 <= y < h and not bgm[y][x] and white(px[x, y]):
            bgm[y][x] = True
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    out = im.copy(); op = out.load()
    for y in range(h):
        for x in range(w):
            if bgm[y][x]:
                op[x, y] = BG
            elif any(bgm[j][i] for j in range(max(0, y - 2), min(h, y + 3)) for i in range(max(0, x - 2), min(w, x + 3))):
                # soft edge: remove the share of white that was blended in
                p = px[x, y]
                t = max(0.0, min(1.0, (min(p) - 40) / 215.0))
                op[x, y] = tuple(int(round(c - t * (255 - b))) if c - t * (255 - b) > 0 else 0 for c, b in zip(p, BG))
    stride = (w * 3 + 3) & ~3
    rows = b''.join(out.crop((0, y, w, y + 1)).tobytes('raw', 'BGR').ljust(stride, b'\0') for y in range(h - 1, -1, -1))
    off = int.from_bytes(raw[10:14], 'little')
    assert off + len(rows) <= len(raw), path
    return raw[:off] + rows + raw[off + len(rows):]

n = 0
for root, _, files in os.walk(SRC):
    if 'Res' in os.path.relpath(root, SRC).split(os.sep):
        continue          # diagnostic illustrations: often black on white, leave them alone
    for f in files:
        if f.lower().endswith('.bmp'):
            p = os.path.join(root, f)
            data = convert(p)
            if data:
                dst = os.path.join(OUT, os.path.relpath(p, SRC))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'wb').write(data); n += 1
print(n, 'pictures converted')
