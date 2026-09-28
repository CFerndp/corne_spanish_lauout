# -*- coding: utf-8 -*-
"""Genera docs/corne-es-layout.svg: una chuleta con las 4 capas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec import LAYERS, HOLE, UNCONFIRMED

KW, KH, GAP, HALF_GAP = 66, 56, 8, 46
ROW_GAP, LAYER_GAP = 8, 44
MARGIN, HEADER = 40, 78

BG, KEY, KEY_TX = "#faf9f6", "#ffffff", "#1c1b19"
BORDER, MUTED = "#cfcdc6", "#8a877e"
ACCENT, ACCENT_BG = "#b4532a", "#fdf0e8"      # capas / MO
WARN, WARN_BG = "#a8791a", "#fdf6e3"          # sin confirmar

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def key_x(col):
    return MARGIN + col * (KW + GAP) + (HALF_GAP if col >= 6 else 0)

BOARD_W = key_x(11) + KW + MARGIN
LAYER_H = HEADER + 4 * KH + 3 * ROW_GAP

def draw_layer(y0, name, note, grid, mark_unconfirmed):
    o = [f'<text x="{MARGIN}" y="{y0+26}" class="lname">{esc(name)}</text>',
         f'<text x="{MARGIN}" y="{y0+50}" class="lnote">{esc(note)}</text>']
    for r, row in enumerate(grid):
        for c, (code, label) in enumerate(row):
            if (code, label) == HOLE:
                continue
            x, y = key_x(c), y0 + HEADER + r * (KH + ROW_GAP)
            unc = mark_unconfirmed and (r, c) in UNCONFIRMED
            is_mo = code.startswith("MO(")
            fill = WARN_BG if unc else (ACCENT_BG if is_mo else KEY)
            stroke = WARN if unc else (ACCENT if is_mo else BORDER)
            dash = ' stroke-dasharray="4 3"' if unc else ""
            o.append(f'<rect x="{x}" y="{y}" width="{KW}" height="{KH}" rx="7" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>')
            lines = label.split("\n")
            cls = "kmo" if is_mo else "klbl"
            size = 17 if max(len(l) for l in lines) <= 5 else 13
            ty = y + KH / 2 + (6 if len(lines) == 1 else -3)
            for i, ln in enumerate(lines):
                o.append(f'<text x="{x+KW/2}" y="{ty+i*15}" class="{cls}" '
                         f'style="font-size:{size}px">{esc(ln)}</text>')
            if unc:
                o.append(f'<text x="{x+KW-7}" y="{y+15}" class="badge">?</text>')
    return o

def main():
    total_h = MARGIN + 96 + len(LAYERS) * (LAYER_H + LAYER_GAP) + 70
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{BOARD_W}" height="{total_h}" '
           f'viewBox="0 0 {BOARD_W} {total_h}" font-family="DejaVu Sans, Inter, Helvetica, sans-serif">',
           f'<rect width="{BOARD_W}" height="{total_h}" fill="{BG}"/>',
           '<style>',
           f'.title{{font-size:30px;font-weight:700;fill:{KEY_TX}}}',
           f'.sub{{font-size:15px;fill:{MUTED}}}',
           f'.lname{{font-size:20px;font-weight:700;fill:{ACCENT}}}',
           f'.lnote{{font-size:13px;fill:{MUTED}}}',
           f'.klbl{{fill:{KEY_TX};text-anchor:middle}}',
           f'.kmo{{fill:{ACCENT};font-weight:700;text-anchor:middle}}',
           f'.badge{{font-size:12px;font-weight:700;fill:{WARN};text-anchor:end}}',
           f'.foot{{font-size:13px;fill:{MUTED}}}',
           '</style>',
           f'<text x="{MARGIN}" y="{MARGIN+24}" class="title">Corne · layout español para desarrollo</text>',
           f'<text x="{MARGIN}" y="{MARGIN+50}" class="sub">'
           f'SO en xkb «es» · ▽ = transparente (cae a la capa inferior) · las teclas con ? están sin confirmar</text>']
    y = MARGIN + 96
    for i, (name, note, grid) in enumerate(LAYERS):
        out += draw_layer(y, name, note, grid, mark_unconfirmed=(i == 0))
        y += LAYER_H + LAYER_GAP
    out.append(f'<text x="{MARGIN}" y="{y+10}" class="foot">'
               f'MO(1)+MO(2) = capa 3 · ` y ^ son teclas muertas en «es»: pulsa espacio después</text>')
    out.append('</svg>')
    docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    os.makedirs(docs, exist_ok=True)
    path = os.path.join(docs, "corne-es-layout.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(path)

if __name__ == "__main__":
    main()
