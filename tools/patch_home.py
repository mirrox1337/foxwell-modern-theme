"""Patch Home.bin (V2.07.001) so the dark theme has no hard-coded white left.

    python tools/patch_home.py <stock Home.bin> <patched Home.bin>

The menu grid code paints two things pure white no matter what theme.txt says:
  * the frame around a tile when the selection leaves it, and
  * the box behind a text-only item such as a car brand name.
The frame now uses the item's own background colour; the text box is opaque black.
The trailing checksum (sum of all earlier bytes) is rewritten.
"""
import hashlib, sys

STOCK_SHA1 = 'ab872cf000e869f0d00c7f536f03d7331ee5330c'
BASE = 0x20000000
MVN_R1_WHITE = bytes.fromhex('0010e0e3')          # mvn r1, #0          -> 0xFFFFFFFF
LDR_R1_OWN_BG = bytes.fromhex('201094e5')         # ldr r1, [r4, #0x20] -> the item's background colour
MOV_R1_BLACK = bytes.fromhex('ff14a0e3')          # mov r1, #0xff000000 -> opaque black
PATCHES = [
    (0x20011d64, LDR_R1_OWN_BG),   # frame colour when an item loses the selection (4 variants of the item class)
    (0x2003fdc0, LDR_R1_OWN_BG),
    (0x20040b48, LDR_R1_OWN_BG),
    (0x20041538, LDR_R1_OWN_BG),
    (0x2003fb6c, MOV_R1_BLACK),    # background of the text box in text-only items
]

d = bytearray(open(sys.argv[1], 'rb').read())
assert hashlib.sha1(d).hexdigest() == STOCK_SHA1, 'not the stock V2.07.001 Home.bin this patch was written for'
for addr, new in PATCHES:
    o = addr - BASE
    assert d[o:o + 4] == MVN_R1_WHITE, hex(addr)
    d[o:o + 4] = new
d[-4:] = (sum(d[:-4]) & 0xFFFFFFFF).to_bytes(4, 'little')
open(sys.argv[2], 'wb').write(d)
print(len(PATCHES), 'patches applied, checksum', hex(int.from_bytes(d[-4:], 'little')))
