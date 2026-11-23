"""Generate a modernized copy of the theme.
  python modernize.py Picture Picture_modern          (light)
  python modernize.py Picture Picture_dark dark       (dark)
Same file names, sizes and 24-bit uncompressed BMP format as the originals."""
import os, shutil, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SRC = sys.argv[1]; DST = sys.argv[2]
SS = 4  # supersampling for smooth shapes

DARK = len(sys.argv) > 3 and sys.argv[3] == 'dark'
if DARK:
    BG, CARD, BORDER = (10, 15, 28), (24, 33, 54), (44, 57, 84)
    INK, ACCENT, ACCENT2 = (226, 232, 240), (59, 130, 246), (37, 99, 235)
    NAVY1, NAVY2 = (17, 26, 48), (30, 58, 138)
    SHADOW, SOFT, TRACK = (3, 6, 14), (36, 48, 74), (44, 57, 84)
    PILL, DISABLED, CBOX, FLAGLINE = (33, 52, 98), (71, 85, 105), (100, 116, 139), (58, 72, 100)
    PREVIEW = 'preview_dark_'
else:
    BG, CARD, BORDER = (238, 242, 247), (255, 255, 255), (222, 228, 237)
    INK, ACCENT, ACCENT2 = (30, 41, 59), (37, 99, 235), (29, 78, 216)
    NAVY1, NAVY2 = (15, 23, 42), (30, 58, 138)
    SHADOW, SOFT, TRACK = (203, 213, 225), (241, 245, 249), (226, 232, 240)
    PILL, DISABLED, CBOX, FLAGLINE = (228, 236, 252), (203, 213, 225), (148, 163, 184), (203, 213, 225)
    PREVIEW = 'preview_'

LABELS = ['Diagnose', 'Service', 'OBDII', 'AutoVIN', 'Battery', 'History', 'Playback', 'Setting']
CREDIT = 'Theme by Mirrox'
CREDIT_URL = 'github.com/mirrox1337'

def hx(s): return tuple(int(s[i:i+2], 16) for i in (1, 3, 5))
PALETTE = {
 'diagnose': ('#60A5FA', '#1D4ED8'), 'specialfunction': ('#A78BFA', '#6D28D9'),
 'eobd': ('#2DD4BF', '#0F766E'), 'eobddtc': ('#FBBF24', '#D97706'),
 'eobdim': ('#38BDF8', '#0369A1'), 'autovin': ('#818CF8', '#4338CA'),
 'batterytest': ('#4ADE80', '#15803D'), 'history': ('#F472B6', '#BE185D'),
 'playback': ('#22D3EE', '#0E7490'), 'update': ('#FB923C', '#C2410C'),
 'setting': ('#94A3B8', '#475569'),
 'about': ('#60A5FA', '#1D4ED8'), 'beep': ('#F472B6', '#BE185D'),
 'crt_test': ('#4ADE80', '#15803D'), 'key_test': ('#A78BFA', '#6D28D9'),
 'language': ('#2DD4BF', '#0F766E'), 'metrology': ('#FBBF24', '#D97706'),
 'shortcut': ('#FB923C', '#C2410C'),
}

FOCUS_DIR = os.path.join(os.path.dirname(DST), 'Focus_extra_dark' if DARK else 'Focus_extra_light')
FOCUS = (37, 99, 235) if DARK else (25, 50, 93)     # same as the firmware's focused-item colour (entry 25)

def save(im, rel, like=None, root=None):
    p = os.path.join(root or DST, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    rel = like or rel
    import io
    buf = io.BytesIO(); im.convert('RGB').save(buf, 'BMP'); pix = buf.getvalue()[54:]
    orig = open(os.path.join(SRC, rel), 'rb').read()
    assert len(orig) >= 54 + len(pix), rel
    # keep the original header and any trailing bytes so the file is byte-for-byte the same layout
    open(p, 'wb').write(orig[:54] + pix + orig[54 + len(pix):])

def grad(size, c1, c2, diag=False, horiz=False):
    w, h = size; g = Image.new('RGB', size); px = g.load()
    for y in range(h):
        for x in range(w):
            if diag: t = (x / max(w-1, 1) + y / max(h-1, 1)) / 2
            elif horiz: t = x / max(w-1, 1)
            else: t = y / max(h-1, 1)
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))
    return g

def rrect_mask(size, box, r):
    m = Image.new('L', (size[0]*SS, size[1]*SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([v*SS for v in box], r*SS, fill=255)
    return m.resize(size, Image.LANCZOS)

def glyph_alpha(im, bg=(255, 255, 255)):
    rgb = im.convert('RGB'); w, h = rgb.size
    diff = ImageChops.difference(rgb, Image.new('RGB', (w, h), bg)).convert('L')
    mx = max(diff.getextrema()[1], 1)
    return diff.point(lambda v: min(255, round(v * 255 / mx)))

def tile(rel, key, focus=False):
    src = Image.open(os.path.join(SRC, rel)); w, h = src.size
    a = glyph_alpha(src)
    bb = a.crop((0, 0, w, 66)).getbbox()
    out = Image.new('RGB', (w, h), BG)
    sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).rounded_rectangle([5, 6, w-5, h-3], 12, fill=60)
    out.paste(SHADOW, (0, 0), sh.filter(ImageFilter.GaussianBlur(3)))
    if focus:   # highlighted card for the selected tile
        out.paste((147, 197, 253), (0, 0), rrect_mask((w, h), (2, 2, w-3, h-4), 13))
        out.paste(FOCUS, (0, 0), rrect_mask((w, h), (4, 4, w-5, h-6), 11))
    else:
        out.paste(BORDER, (0, 0), rrect_mask((w, h), (3, 3, w-4, h-5), 12))
        out.paste(CARD, (0, 0), rrect_mask((w, h), (4, 4, w-5, h-6), 11))
    if bb:
        cx, cy = (bb[0]+bb[2]) / 2, (bb[1]+bb[3]) / 2
        icon = a.crop(bb); iw, ih = icon.size
        sc = min(1.0, 34 / max(iw, ih))
        icon = icon.resize((max(1, round(iw*sc)), max(1, round(ih*sc))), Image.LANCZOS)
        cs = 52; x0, y0 = (w - cs) // 2, 11   # same spot on every tile
        c1, c2 = (hx(c) for c in PALETTE.get(key, ('#60A5FA', '#1D4ED8')))
        if focus: out.paste((255, 255, 255), (x0-2, y0-2), rrect_mask((cs+4, cs+4), (0, 0, cs+3, cs+3), 17))
        out.paste(grad((cs, cs), c1, c2, diag=True), (x0, y0), rrect_mask((cs, cs), (0, 0, cs-1, cs-1), 15))
        iw, ih = icon.size
        out.paste((255, 255, 255), (x0 + (cs-iw)//2, y0 + (cs-ih)//2), icon)
    if focus:
        folder, name = rel.split('/')
        save(out, f'{folder}/focus_{name}', like=rel, root=FOCUS_DIR)
    else:
        save(out, rel)

def shift(im, old, new, ch=(2, 0)):
    """Move one colour family (and its anti-aliased blends) to a new colour."""
    im = im.convert('RGB'); px = im.load(); w, h = im.size
    span = old[ch[0]] - old[ch[1]]
    for y in range(h):
        for x in range(w):
            c = px[x, y]; t = max(0.0, min(1.0, (c[ch[0]] - c[ch[1]]) / span))
            if t > 0.04:
                px[x, y] = tuple(max(0, min(255, round(v + t * (n - o)))) for v, n, o in zip(c, new, old))
    return im

def language_tile(rel):
    src = Image.open(os.path.join(SRC, rel)).convert('RGB'); w, h = src.size
    a = glyph_alpha(src).point(lambda v: 255 if v > 5 else 0)
    fb = a.crop((0, 0, w, 56)).getbbox() or (13, 7, 83, 52)
    out = Image.new('RGB', (w, h), BG)
    out.paste(BORDER, (0, 0), rrect_mask((w, h), (3, 2, w-4, h-3), 10))
    card = Image.new('RGB', (w, h), CARD)
    if DARK:                                                # language name -> light text
        card.paste(INK, (0, 56), glyph_alpha(src.crop((0, 56, w, h))))
    else:
        card.paste(src.crop((0, 56, w, h)), (0, 56))        # keep the language name
    out.paste(card, (0, 0), rrect_mask((w, h), (4, 3, w-5, h-4), 9))
    fw, fh = fb[2]-fb[0], fb[3]-fb[1]
    out.paste(FLAGLINE, (fb[0]-1, fb[1]-1), rrect_mask((fw+2, fh+2), (0, 0, fw+1, fh+1), 7))
    out.paste(src.crop(fb), fb[:2], rrect_mask((fw, fh), (0, 0, fw-1, fh-1), 6))
    save(out, rel)

def on_dark(im, bg, thresh=90):
    """Dark mode: repaint the white area around a picture (reached from its corners)."""
    im = im.convert('RGB')
    if DARK:
        w, h = im.size
        for xy in ((0, 0), (w-1, 0), (0, h-1), (w-1, h-1)):
            if min(im.getpixel(xy)) > 200: ImageDraw.floodfill(im, xy, bg, thresh=thresh)
    return im

def dark_screen(im):
    """Dark mode for full-screen pictures: white -> page background, black -> light, colours kept."""
    im = im.convert('RGB'); px = im.load(); w, h = im.size
    light = (241, 245, 249)
    for y in range(h):
        for x in range(w):
            c = px[x, y]; mx, mn = max(c), min(c)
            if mn == 255: px[x, y] = BG; continue
            wt, sat, blk = mn / 255, (mx - mn) / 255, 1 - mx / 255
            hue = tuple((v - mn) * 255 / (mx - mn) for v in c) if mx > mn else (0, 0, 0)
            px[x, y] = tuple(min(255, round(wt * b + sat * hc + blk * l)) for b, hc, l in zip(BG, hue, light))
    return im

def title(w=480, h=32):
    return grad((w, h), NAVY1, NAVY2, horiz=True)

def chevron(size, direction, color, bg, stroke=2.2, scale=0.32):
    w, h = size; im = Image.new('RGB', (w*SS, h*SS), bg); d = ImageDraw.Draw(im)
    cx, cy, s = w*SS/2, h*SS/2, min(w, h)*SS*scale
    pts = {'left': [(cx+s/2, cy-s), (cx-s/2, cy), (cx+s/2, cy+s)],
           'right': [(cx-s/2, cy-s), (cx+s/2, cy), (cx-s/2, cy+s)],
           'up': [(cx-s, cy+s/2), (cx, cy-s/2), (cx+s, cy+s/2)],
           'down': [(cx-s, cy-s/2), (cx, cy+s/2), (cx+s, cy-s/2)]}[direction]
    d.line(pts, fill=color, width=round(stroke*SS), joint='curve')
    for p in (pts[0], pts[-1]):
        r = stroke*SS/2; d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=color)
    return im.resize(size, Image.LANCZOS)

def main():
    shutil.copytree(SRC, DST, dirs_exist_ok=True)  # untouched assets carried over
    for folder in ('home', 'settings'):
        for f in os.listdir(os.path.join(SRC, folder)):
            tile(f'{folder}/{f}', os.path.splitext(f)[0])
            if folder == 'home': tile(f'{folder}/{f}', os.path.splitext(f)[0], focus=True)

    for f in os.listdir(os.path.join(SRC, 'language')):
        language_tile(f'language/{f}')
    for f in os.listdir(os.path.join(SRC, 'key_test')):       # highlighted key -> accent
        save(on_dark(shift(Image.open(os.path.join(SRC, 'key_test', f)), (44, 80, 159), ACCENT), BG), f'key_test/{f}')
    for f in ('freeze_help', 'freeze_icon_normal', 'freeze_icon_selected', 'help_icon_normal', 'help_icon_selected'):
        save(shift(Image.open(os.path.join(SRC, f + '.bmp')), (0, 114, 255), ACCENT), f + '.bmp')
    lock = shift(Image.open(os.path.join(SRC, 'lock.bmp')), (50, 107, 229), ACCENT)
    if DARK:   # grey plate -> dark plate
        src = Image.open(os.path.join(SRC, 'lock.bmp')).convert('RGB'); lp = lock.load()
        for y in range(24):
            for x in range(24):
                c = src.getpixel((x, y)); t = max(0.0, min(1.0, (c[2] - c[0]) / 179))
                lp[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(CARD, (147, 197, 253)))
    save(lock, 'lock.bmp')
    save(on_dark(shift(Image.open(os.path.join(SRC, 'Notice.bmp')), (211, 79, 29), (245, 158, 11), ch=(0, 2)), CARD), 'Notice.bmp')
    save(on_dark(shift(Image.open(os.path.join(SRC, 'error.bmp')), (189, 28, 32), (239, 68, 68), ch=(0, 2)), CARD), 'error.bmp')
    if DARK:
        for f in ('car.bmp', 'region.bmp'):
            save(Image.new('RGB', Image.open(os.path.join(SRC, f)).size, CARD), f)

    # credit line on the start-up logo screen
    from PIL import ImageFont
    splash = Image.open(os.path.join(SRC, 'foxwell.bmp')).convert('RGB')
    if DARK:
        splash = dark_screen(splash)
        for f in ('foxboot.bmp', 'update.bmp', 'update-old.bmp'):
            save(dark_screen(Image.open(os.path.join(SRC, f))), f)
    try: font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 12)
    except OSError: font = ImageFont.load_default()
    try: small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 11)
    except OSError: small = font
    dr = ImageDraw.Draw(splash)
    for txt, f, y, col in ((CREDIT, font, 38, (148, 163, 184) if DARK else (100, 116, 139)),
                            (CREDIT_URL, small, 22, (100, 116, 139) if DARK else (148, 163, 184))):
        tw = dr.textlength(txt, font=f)
        dr.text(((splash.size[0] - tw) / 2, splash.size[1] - y), txt, font=f, fill=col)
    save(splash, 'foxwell.bmp')

    save(title(), 'title.bmp')
    bu = Image.new('RGB', (480, 244), BG); bu.paste(title(), (0, 0)); save(bu, 'bg_up_light.bmp')
    ba = Image.new('RGB', (480, 272), BG); ba.paste(title(), (0, 0)); save(ba, 'bg_all_light.bmp')
    save(Image.new('RGB', (480, 212), BG), 'language_center_bg_light.bmp')

    bar = Image.new('RGB', (480, 28), CARD); d = ImageDraw.Draw(bar)
    d.line([(0, 0), (479, 0)], fill=BORDER)
    for i in (1, 2): d.line([(160*i, 6), (160*i, 21)], fill=BORDER)
    save(bar, 'button_three.bmp')
    more = Image.new('RGB', (150, 28), CARD)
    more.paste(PILL, (0, 0), rrect_mask((150, 28), (4, 3, 145, 24), 10))
    save(more, 'button_more.bmp')
    for side in ('left', 'right'):
        save(chevron((15, 28), side, ACCENT, CARD, 2.0, 0.28), f'{side}_normal.bmp')
        save(chevron((15, 28), side, DISABLED, CARD, 2.0, 0.28), f'{side}_disable.bmp')
    for dname in ('up', 'down'):
        im = Image.new('RGB', (32, 24), CARD)
        im.paste(ACCENT, (0, 0), rrect_mask((32, 24), (2, 1, 29, 22), 7))
        im.paste(chevron((32, 24), dname, (255, 255, 255), ACCENT, 2.4, 0.22), (0, 0), rrect_mask((32, 24), (6, 4, 25, 19), 3))
        save(im, f'{dname}.bmp')

    tr = Image.new('RGB', (4, 210), CARD); tr.paste(TRACK, (0, 0), rrect_mask((4, 210), (0, 0, 3, 209), 2)); save(tr, 'bg_scroll.bmp')
    sl = Image.new('RGB', (4, 210), TRACK); sl.paste(ACCENT, (0, 0), rrect_mask((4, 210), (0, 0, 3, 209), 2)); save(sl, 'slider.bmp')

    cb = Image.new('RGB', (12, 12), CARD); cb.paste(CBOX, (0, 0), rrect_mask((12, 12), (0, 0, 11, 11), 3))
    cb.paste(CARD, (0, 0), rrect_mask((12, 12), (1.3, 1.3, 9.7, 9.7), 2)); save(cb, 'checkbox_normal.bmp')
    big = 12*SS
    cs = Image.new('RGB', (big, big), CARD); cs.paste(ACCENT, (0, 0), rrect_mask((big, big), (0, 0, big-1, big-1), 3*SS))
    ImageDraw.Draw(cs).line([(2.8*SS, 6.2*SS), (5*SS, 8.4*SS), (9.2*SS, 3.6*SS)], fill=(255, 255, 255), width=round(1.6*SS), joint='curve')
    save(cs.resize((12, 12), Image.LANCZOS), 'checkbox_selected.bmp')

    for f in os.listdir(os.path.join(SRC, 'DTC')):
        name = os.path.splitext(f)[0]
        if len(name) == 2 and name.endswith('F'): continue
        a = glyph_alpha(Image.open(os.path.join(SRC, 'DTC', f)))
        n = Image.new('RGB', (40, 40), CARD); n.paste(SOFT, (0, 0), rrect_mask((40, 40), (2, 2, 37, 37), 9))
        n.paste(INK, (0, 0), a); save(n, f'DTC/{f}')
        s = Image.new('RGB', (40, 40), CARD)
        s.paste(grad((40, 40), (59, 130, 246), ACCENT2, diag=True), (0, 0), rrect_mask((40, 40), (2, 2, 37, 37), 9))
        s.paste((255, 255, 255), (0, 0), a); save(s, f'DTC/{name}F.bmp')

    if DARK:
        # Colour overrides for the firmware's built-in table (it reads /Res/Theme/theme.txt, section "skin").
        # Values are 0xAARRGGBB written as plain decimal integers. See THEME_NOTES.md.
        skin = {
            0: 0xFF000000 | (BG[0] << 16 | BG[1] << 8 | BG[2]),        # window background (was white)
            2: 0xFFE2E8F0,   # normal text (was black)
            5: 0xFF64748B,   # disabled text
            11: 0xFF2C3954, 14: 0xFF182136, 15: 0xFF182136,           # light fills / frames
            16: 0xFF3A4864, 17: 0xFF2C3954, 18: 0xFF2C3954,           # borders and divider lines
            24: 0xFF213462, 27: 0xFF213462,                           # selected-row highlight (was pale blue)
            25: 0xFF2563EB,  # focused item background (text on it stays white)
            28: 0xFF60A5FA,  # pure-blue pen -> lighter blue
            31: 0xFFE2E8F0, 58: 0xFFE2E8F0, 59: 0xFFE2E8F0, 60: 0xFFE2E8F0,   # other dark text
            61: 0xFF182136,  # light panel behind text 60
        }
        import json
        with open(os.path.join(os.path.dirname(DST), 'theme_dark.txt'), 'w', newline=chr(10)) as fh:
            json.dump({'skin': {str(k): v for k, v in sorted(skin.items())}}, fh, separators=(',', ':'))

    # preview mock of the home screen
    mock = Image.open(os.path.join(DST, 'bg_up_light.bmp')).convert('RGB').resize((480, 272))
    mock.paste(Image.new('RGB', (480, 272), BG)); mock.paste(title(), (0, 0))
    order = ['diagnose', 'specialfunction', 'eobd', 'autovin', 'batterytest', 'history', 'playback', 'setting']
    for i, k in enumerate(order):
        sel = i == 0
        t = Image.open(os.path.join(FOCUS_DIR, 'home', 'focus_' + k + '.bmp') if sel else os.path.join(DST, 'home', k + '.bmp'))
        mock.paste(t, ((i % 4)*120, 32 + (i//4)*106))
        lab = LABELS[i]; md = ImageDraw.Draw(mock)     # labels are a mock-up: the scanner draws its own
        lw = md.textlength(lab, font=font)
        md.text(((i % 4)*120 + (120 - lw)/2, 32 + (i//4)*106 + 72), lab, font=font, fill=(255, 255, 255) if sel else INK)
    mock.paste(Image.open(os.path.join(DST, 'button_three.bmp')), (0, 244))
    mock.resize((960, 544), Image.NEAREST).save(os.path.join(os.path.dirname(DST), PREVIEW + 'home.png'))
    Image.open(os.path.join(DST, 'foxwell.bmp')).resize((960, 544), Image.NEAREST).save(os.path.join(os.path.dirname(DST), PREVIEW + 'splash.png'))
    if DARK:
        sheet = Image.new('RGB', (1440, 272), (60, 60, 60))
        for i, f in enumerate(('foxboot.bmp', 'update.bmp', 'update-old.bmp')):
            sheet.paste(Image.open(os.path.join(DST, f)), (i * 480, 0))
        sheet.save(os.path.join(os.path.dirname(DST), PREVIEW + 'boot_and_update.png'))
    lang = Image.new('RGB', (480, 272), BG); lang.paste(title(), (0, 0))
    for i, f in enumerate(sorted(os.listdir(os.path.join(DST, 'language')))[:10]):
        lang.paste(Image.open(os.path.join(DST, 'language', f)), ((i % 5)*96, 32 + (i//5)*75))
    x = 8
    for f in ('DTC/P.bmp', 'DTC/0F.bmp', 'DTC/3.bmp', 'DTC/0.bmp', 'DTC/1.bmp', 'Notice.bmp', 'error.bmp', 'lock.bmp',
              'up.bmp', 'down.bmp', 'checkbox_normal.bmp', 'checkbox_selected.bmp', 'help_icon_normal.bmp', 'freeze_icon_normal.bmp'):
        im = Image.open(os.path.join(DST, f)); lang.paste(im, (x, 190 + (48 - im.size[1])//2)); x += im.size[0] + 6
    lang.paste(Image.open(os.path.join(DST, 'button_three.bmp')), (0, 244))
    lang.resize((960, 544), Image.NEAREST).save(os.path.join(os.path.dirname(DST), PREVIEW + 'language_and_controls.png'))
    kt = Image.open(os.path.join(DST, 'key_test', 'Key_enter.bmp'))
    kt.resize((796, 388), Image.NEAREST).save(os.path.join(os.path.dirname(DST), PREVIEW + 'key_test.png'))

if __name__ == '__main__':
    main()
