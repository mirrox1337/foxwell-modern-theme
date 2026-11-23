"""Replace pure white pixels in 24-bit BMPs with (254,254,254), in place.

    python tools/no_white.py <folder> [<folder> ...]

Working theory (from testing on a scanner): the firmware treats pure white as transparent when it
draws a picture, so white text and icons show whatever is behind them. Off-white draws solid.
"""
import os, sys

def fix(path):
    raw = bytearray(open(path, 'rb').read())
    if raw[:2] != b'BM' or raw[28] != 24:
        return 0
    off = int.from_bytes(raw[10:14], 'little')
    w = int.from_bytes(raw[18:22], 'little'); h = abs(int.from_bytes(raw[22:26], 'little', signed=True))
    stride = (w * 3 + 3) & ~3
    n = 0
    for y in range(h):
        row = off + y * stride
        seg = raw[row:row + w * 3]
        if b'\xff\xff\xff' not in seg:
            continue
        for x in range(0, w * 3, 3):
            if seg[x] == 255 and seg[x + 1] == 255 and seg[x + 2] == 255:
                raw[row + x:row + x + 3] = b'\xfe\xfe\xfe'; n += 1
    if n:
        open(path, 'wb').write(raw)
    return n

if __name__ == '__main__':
    files = pixels = 0
    for top in sys.argv[1:]:
        for root, _, names in os.walk(top):
            for f in names:
                if f.lower().endswith('.bmp'):
                    n = fix(os.path.join(root, f))
                    files += bool(n); pixels += n
    print(files, 'pictures changed,', pixels, 'white pixels made off-white')
