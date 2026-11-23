"""Helpers for the scanner's program files.

    python tools/fwtool.py check  Home.bin            verify the trailing checksum
    python tools/fwtool.py fix    Home.bin            rewrite the checksum after patching
    python tools/fwtool.py decode EOBD.bin out.bin    un-XOR a vehicle program (0x58), or encode it back

Home.bin, DataManager.bin and Update.bin end with a little-endian 32-bit sum of all earlier bytes.
"""
import sys

def csum(d):
    return sum(d[:-4]) & 0xFFFFFFFF

cmd, path = sys.argv[1], sys.argv[2]
d = bytearray(open(path, 'rb').read())
if cmd == 'check':
    want, have = csum(d), int.from_bytes(d[-4:], 'little')
    print(path, 'OK' if want == have else 'BAD', hex(have), hex(want))
    sys.exit(want != have)
elif cmd == 'fix':
    d[-4:] = csum(d).to_bytes(4, 'little')
    open(path, 'wb').write(d)
    print(path, 'checksum set to', hex(csum(d)))
elif cmd == 'decode':
    open(sys.argv[3], 'wb').write(bytes(b ^ 0x58 for b in d))
