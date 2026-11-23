# Custom firmware pack — Foxwell NT-series, Home V2.07.001

Dark theme, completed Swedish texts, credits and a small `Home.bin` patch, laid out like the scanner's
TF card. Confirmed working on one NT604 Elite; use at your own risk and back up the card first.

## Install

1. Copy the whole card to your PC as a backup.
2. Copy `Res` and `Vehicles` from this folder over the same folders on the card.
3. Build the patched `Home.bin` from your own card (it is not included here):
   `python tools/patch_home.py <card>/Home/Home.bin Home.bin`, keep the original as
   `Home_stock.bin`, and put the patched file in `/Home/`.

To undo, restore your backup. If the scanner does not start after step 3, put the stock `Home.bin` back.

## What changes

| Path | Change |
|---|---|
| `Res/Theme/Picture/` | Dark theme pictures, with pure white made off-white |
| `Res/Theme/Picture/home/focus_*.bmp` | Highlighted tiles for the selected home item |
| `Res/Theme/theme.txt` | Colour overrides for the main menu and the diagnostic programs |
| `Res/Language/home/se.cbf` | 26 untranslated menu texts now Swedish; title tag; credit in the About copyright line |
| `Res/Language/home/en.cbf` | Title tag and credit only |
| `Res/Language/Diagnostic/se.cbf` | 16 untranslated diagnostic texts now Swedish |
| `Vehicles/**/*.bmp` | Car-brand and region pictures on a dark background |
| `Home/Home.bin` (you build it) | Removes the hard-coded white frame left behind by the selection and the white box behind car brand names |

## Known limits

- The start-up logo comes from the scanner's internal flash and cannot be changed from the card.
- The box behind car brand names is black, not the theme's navy.
- Text on the live-data graph is still dark; cause not found yet.
- The diagnostic programs carry their own copy of the patched code and are not patched.

Rebuild everything with `python tools/build_cfw.py <card dump folder> CFW`.
