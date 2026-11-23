# Theme notes

Theme by Mirrox — https://github.com/mirrox1337

## How the scanner picks its colors

Found by reading `Home.bin` (firmware V2.23.001 strings). Nothing here has been tested on a device.

## theme.txt

At start-up the firmware fills a built-in table of colors, sizes and font settings, then reads
`/Res/Theme/theme.txt` if it exists and overrides entries from it. The file is JSON with up to four
sections, all optional:

```json
{"skin": {"2": 4293060848}, "dim": {}, "font": {}, "config": {}}
```

- Keys are the entry number as a decimal string.
- Values must be whole decimal numbers (no decimal point, no hex). A color is `0xAARRGGBB` as a decimal number.
- `skin` = colors (62 entries), `dim` = sizes (83 entries), `font` = 13 entries, `config` = 1 entry.

## What the color entries do (as far as traced)

| Entry | Use | Confidence |
|---|---|---|
| 2 | normal text | high - set as text color when an item is not focused |
| 32 | text of the focused item | high |
| 25 | background of the focused item | high |
| 1, 7 | light text (title area) | medium |
| 5 | disabled text | medium |
| 31, 58, 59, 60 | other dark text | medium |
| 0, 14 | background fills | medium |
| 8 | title bar color (same navy as `title.bmp`) | medium |
| 16, 17, 18, 11, 15 | borders, divider lines, frames | low-medium |
| 24, 27 | selected-row highlight | low-medium |
| 28, 29, 30 | pen / graph colors | low |

Entries not listed are not looked up by number anywhere I could find in this file.

## Built-in defaults

| Entry | Default |
|---|---|
| 0 | `#FFFFFF` |
| 1 | `#F5F6F7` |
| 2 | `#000000` |
| 3 | `#2D2D30` |
| 4 | `#ED1C24` |
| 5 | `#B0B0B0` |
| 6 | `#FF0000` |
| 7 | `#FFFFFF` |
| 8 | `#19253D` |
| 9 | `#19253D` |
| 10 | `#F4F4F4` |
| 11 | `#EEEDEE` |
| 12 | `#FF0000` |
| 13 | `#414753` |
| 14 | `#FFFFFF` |
| 15 | `#FFFFFF` |
| 16 | `#A2A2A2` |
| 17 | `#D0D0D0` |
| 18 | `#E0E0E0` |
| 19 | `#FF0000` |
| 20 | `#2B91AF` |
| 21 | `#FFFFFF` |
| 22 | `#3E3E42` |
| 23 | `#A0A0A0` |
| 24 | `#C6D3EA` |
| 25 | `#19325D` |
| 26 | `#264F78` |
| 27 | `#C6D3EA` |
| 28 | `#0000FF` |
| 29 | `#FF0000` |
| 30 | `#5982D9` |
| 31 | `#2D2D30` |
| 32 | `#FFFFFF` |
| 33 | `#2E2E2E` |
| 34 | `#2E2E2E` |
| 35 | `#162C9A` |
| 36 | `#FFD027` |
| 37 | `#101010` |
| 38 | `#1E1E1E` |
| 39 | `#00FF00` |
| 40 | `#F0F0F0` |
| 41 | `#333337` |
| 42 | `#F0F0F0` |
| 43 | `#333337` |
| 44 | `#F0F0F0` |
| 45 | `#F5F6F7` |
| 46 | `#F0F0F0` |
| 47 | `#000000` |
| 48 | `#0B101D` |
| 49 | `#C6D3EA` |
| 50 | `#F0F0F0` |
| 51 | `#000000` |
| 52 | `#3B4F75` |
| 53 | `#FFFFFF` |
| 54 | `#000000` |
| 55 | `#FFFFFF` |
| 56 | `#00FF00` |
| 57 | `#F4F4F4` |
| 58 | `#000000` |
| 59 | `#000000` |
| 60 | `#000000` |
| 61 | `#F4F4F4` |

## Other findings

- The firmware also looks for `focus_<name>.bmp` in `Picture/Home/` (for example `focus_diagnose.bmp`).
- `theme_dark.txt` (made by `tools/modernize.py ... dark`) is the override file for the dark theme.
  Copy it to the device as `/Res/Theme/theme.txt`.

## Hard-coded white in Home.bin (confirmed on a scanner, V2.07.001)

Two colours in the menu grid code ignore `theme.txt`:

- When an item with a picture loses the selection, its frame is redrawn in `0xFFFFFFFF`
  (`mvn r1, #0` before `bl 0x2001abf4`, at 0x20011d64, 0x2003fdc0, 0x20040b48, 0x20041538).
- A text-only item (for example a car brand) gets a white box behind its text (0x2003fb6c).

`tools/patch_home.py` replaces the first four with `ldr r1, [r4, #0x20]` (the item's own background)
and the last with `mov r1, #0xff000000`, then rewrites the checksum. Tested working on a device.
The selected item's frame colour is skin entry 28.

## Vehicle (diagnostic) programs

Each vehicle program has its own copy of the UI code and the same default table, but looks up more
entries than Home does. Traced in `EOBD.bin` (colour getter at file offset 0xa7f7c):

- text: 1, 2, 3, 5, 6, 7, 31, 32, 60 (3 is dark by default and is used for dialog/info text)
- backgrounds: 0, 8, 14, 22, 23, 24, 25, 26, 37, 40, 45, 46, 55, 61
- lines and other drawing: 11, 13, 15, 17, 20, 21, 22, 27, 38, 41, 42, 43, 44, 47; 54/55 look like a text/background pair
