"""Build the file-level custom firmware pack from a scanner card dump.

    python tools/build_cfw.py <dump folder> <output folder>

Writes only the files that differ from stock, laid out like the card.
"""
import json, os, shutil, sys

DUMP, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOME_SE = {
    "0000": "Huvudmeny", "0007": "Knappljud", "0008": "Genvägar", "0009": "Skärmtest",
    "0010": "Knapptest", "0011": "Språket har ställts in!", "0015": "Fordon",
    "0016": "Ändra genväg för F1", "0017": "Ändra genväg för F2", "0018": "Ändra genväg för F3",
    "0019": "Genväg F1 har sparats!", "0020": "Genväg F2 har sparats!", "0021": "Genväg F3 har sparats!",
    "0022": "AV", "0023": "PÅ",
    "0024": "Tryck på valfri knapp för att starta testet. Tryck två gånger på [BACK] för att avsluta",
    "0039": "Läser in data, vänta…", "0040": "Inga fordon hittades i området %s!",
    "0041": "Dataström", "0042": "BOOT-version", "0043": "Inga fordon tillgängliga!",
    "0044": "Fordonsprogrammet %s är inte auktoriserat. Uppdatera det från 'Download Page'.",
    "0072": "1.Ta ut TF-kortet ur enheten och sätt det i kortläsaren.\n"
            "2.Anslut kortläsaren till datorn och uppdatera med uppdateringsverktyget.\n"
            "3.Sätt tillbaka TF-kortet i enheten när uppdateringen är klar.",
    "0112": "Registrera användaruppgifterna, aktivera enheten och ladda ner diagnosdata för %s med uppgraderingsverktyget",
    "0114": "Batteritest", "0115": "SÖK FELKOD",
}
CREDIT = "CFW by Mirrox"
CFW_NAME = "mirrox-cfw 1.1"
DIAG_SE = {
    "0054": "Avstängning", "0055": "Stängs av om ", "0056": " sekunder",
    "1016": "Tangentbord", "1019": "Radera", "1023": "Sida upp", "1024": "Sida ned",
    "1025": "Fäll ned", "1026": "Fäll upp", "1046": "Realtidsdata", "1062": "Programmering",
    "1063": "Utlösare", "1070": "ECU-ID", "1071": "AKTIVERINGS-ID",
    "1072": "Decimalt", "1073": "Hexadecimalt",
}

def dumps(d):
    return json.dumps(d, ensure_ascii=False, separators=(',', ':')).encode('cp1252')

def patch(rel, changes, append=None):
    raw = open(os.path.join(DUMP, rel), 'rb').read()
    d = json.loads(raw.decode('cp1252'))
    assert dumps(d) == raw, rel + ': cannot reproduce the stock file byte for byte'
    en = json.loads(open(os.path.join(DUMP, os.path.dirname(rel), 'en.cbf'), 'rb').read().decode('cp1252'))
    for k, v in changes.items():
        assert d[k] == en[k], (rel, k, 'already translated')
        assert d[k].count('%') == v.count('%'), (rel, k, 'placeholder mismatch')
        d[k] = v
    for k in append or ():          # About copyright row is one line: keep Foxwell's notice, add the credit
        d[k] = d[k].replace(' All rights reserved.', '') + ' | ' + CREDIT
    if append:
        d['0000'] = d['0000'] + '  //  ' + CFW_NAME      # home title bar
    dst = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(dumps(d))
    print(rel, len(changes), 'texts translated')

patch('Res/Language/home/se.cbf', HOME_SE, append=['0030'])
patch('Res/Language/home/en.cbf', {}, append=['0030'])
patch('Res/Language/Diagnostic/se.cbf', DIAG_SE)

# the whole dark theme goes in too, so its white pixels can be made off-white below
shutil.copytree(os.path.join(HERE, 'Picture_dark'), os.path.join(OUT, 'Res', 'Theme', 'Picture'), dirs_exist_ok=True)

src = os.path.join(HERE, 'Focus_extra_dark', 'home')
dst = os.path.join(OUT, 'Res', 'Theme', 'Picture', 'home')
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    # Outside the card shape the highlighted tile must equal the normal tile pixel for pixel,
    # so nothing light is left behind if the scanner only repaints part of the cell.
    hi = bytearray(open(os.path.join(src, f), 'rb').read())
    lo = open(os.path.join(HERE, 'Picture_dark', 'home', f[len('focus_'):]), 'rb').read()
    assert len(hi) == len(lo) and hi[:54] == lo[:54]
    w, h, row = 120, 106, 360
    bg = lo[54:57]
    for y in range(h):
        px = [lo[54 + y * row + x * 3: 57 + y * row + x * 3] == bg for x in range(w)]
        for x in range(w):
            # background pixel, or within 1 px of one (the card's soft edge)
            near = any(px[max(0, x - 1): x + 2])
            if not near and 0 < y < h - 1:
                o = 54 + x * 3
                near = lo[o + (y - 1) * row: o + (y - 1) * row + 3] == bg or lo[o + (y + 1) * row: o + (y + 1) * row + 3] == bg
            if near:
                o = 54 + y * row + x * 3
                hi[o:o + 3] = lo[o:o + 3]
    open(os.path.join(dst, f), 'wb').write(hi)
print(len(os.listdir(src)), 'focus tiles written')

# car-brand pictures, then make every pure white pixel off-white (see tools/no_white.py)
import subprocess
tools = os.path.join(HERE, 'tools')
subprocess.check_call([sys.executable, os.path.join(tools, 'dark_vehicles.py'), os.path.join(DUMP, 'Vehicles'), os.path.join(OUT, 'Vehicles')])
subprocess.check_call([sys.executable, os.path.join(tools, 'no_white.py'), OUT])

# colour overrides, and the patched Home.bin (not kept in the repository: it is Foxwell's program)
shutil.copy(os.path.join(HERE, 'theme_dark.txt'), os.path.join(OUT, 'Res', 'Theme', 'theme.txt'))
os.makedirs(os.path.join(OUT, 'Home'), exist_ok=True)
subprocess.check_call([sys.executable, os.path.join(tools, 'patch_home.py'),
                       os.path.join(DUMP, 'Home', 'Home.bin'), os.path.join(OUT, 'Home', 'Home.bin')])
