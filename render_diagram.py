# -*- coding: utf-8 -*-
"""Genera la chuleta de capas con la forma fisica real del teclado.

Salidas (en docs/):
  corne-es-layout.svg   todas las capas en una sola imagen (la que enseña el README)
  corne-es-layout.pdf   A4, 2 paginas de tarjetas recortables para la pared:
                        escribir (capas 0-3) y jugar (capas 4-6 + tarjeta de ayuda)
                        (requiere rsvg-convert; el PNG se saca igual del SVG)

La geometria (escalonado de columnas, columna interior, pulgares girados) esta medida
sobre la pestaña Keymap de Vial. La correspondencia matriz [r][c] -> tecla fisica esta en PHYS.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec import LAYERS, HOLE

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")

U = 58                 # paso de tecla en px
KS = 52                # lado de la tecla dibujada
HALF_W = 7             # columnas fisicas por mitad (6 + columna interior)
SPLIT = 1.6            # hueco entre mitades, en U
MARGIN = 48

BG, KEY, KEY_TX = "#faf9f6", "#ffffff", "#1c1b19"
BORDER, MUTED = "#cfcdc6", "#8a877e"
ACCENT, ACCENT_BG = "#b4532a", "#fdf0e8"      # teclas que cambian de capa
HELD_BG, HELD_TX = "#3a3833", "#faf9f6"       # tecla que se mantiene para estar en esta capa
TRNS_TX = "#c4c1b8"

# Escalonado vertical de cada columna fisica de la mitad izquierda (0 = meñique exterior,
# 6 = columna interior), en U, medido en Vial. La derecha es su espejo.
STAGGER = [0.38, 0.38, 0.13, 0.0, 0.13, 0.23]
INNER_Y = [0.74, 1.74]
# pulgares de la izquierda, de fuera hacia dentro: (x, y, giro en grados, alto en U)
THUMBS_L = [(3.49, 3.26, 0, 1.0), (4.64, 3.40, 15, 1.0), (5.80, 3.62, 30, 1.25)]


def _phys_left(r, c):
    """(x, y, giro, alto) de la tecla de matriz [r][c] en la mitad izquierda."""
    if r < 3:
        return (c, r + STAGGER[c], 0, 1.0)
    if c in (0, 1):                       # columna interior: [3][0] arriba, [3][1] abajo
        return (6, INNER_Y[c], 0, 1.0)
    return THUMBS_L[c - 3]                # [3][3] [3][4] [3][5]


def _mirror(p):
    x, y, rot, h = p
    return (HALF_W - 1 - x, y, -rot, h)


def _build_phys():
    t = {}
    for r in range(4):
        for c in range(6):
            if (r, c) != (3, 2):
                t[(r, c)] = ("L",) + _phys_left(r, c)
    # mitad derecha, en coordenadas de "mitad izquierda" y luego espejo:
    # columna fisica izquierda k <-> derecha:  meñique exterior(0) = [3][9..11],
    # letras P..Y = matriz 11..7 -> columnas 1..5, interior(6) = [0][6], [1][6]
    for r in range(3):
        for c in range(7, 12):
            k = 12 - c                    # 11 -> 1 (P), 7 -> 5 (Y)
            t[(r, c)] = ("R",) + _mirror((k, r + STAGGER[k], 0, 1.0))
    for r, c in ((3, 9), (3, 10), (3, 11)):
        t[(r, c)] = ("R",) + _mirror((0, (c - 9) + STAGGER[0], 0, 1.0))
    t[(0, 6)] = ("R",) + _mirror((6, INNER_Y[0], 0, 1.0))
    t[(1, 6)] = ("R",) + _mirror((6, INNER_Y[1], 0, 1.0))
    for i, c in enumerate((8, 7, 6)):     # Super (fuera), SYM, Space (dentro)
        t[(3, c)] = ("R",) + _mirror(THUMBS_L[i])
    return t


PHYS = _build_phys()
assert len(PHYS) == 46

BOARD_W = (2 * HALF_W + SPLIT) * U
BOARD_H = 4.95 * U
LAYER_HEAD = 58
LAYER_GAP = 34
LAYER_H = LAYER_HEAD + BOARD_H

# como se llega a cada capa: cada tarjeta recortada tiene que explicarse sola
REACH = {
    0: "Sin pulsar nada",
    1: "Mantén NUM (pulgar izquierdo)",
    2: "Mantén SYM (pulgar derecho)",
    3: "Mantén NUM + SYM a la vez",
    4: "SYM + Esc para entrar · SYM + Esc otra vez para salir",
    5: "Dentro de GAME: mantén G-FN (pulgar izquierdo, el de dentro)",
    6: "Dentro de GAME: mantén SYM (pulgar derecho)",
}

# tecla que se mantiene para llegar a cada capa (se dibuja oscura)
HELD = {1: [(3, 4)], 2: [(3, 7)], 3: [(3, 4), (3, 7)], 5: [(3, 5)], 6: [(3, 7)]}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def draw_layer(x0, y0, li):
    name, _note, grid = LAYERS[li]
    note = REACH[li]
    held = set(HELD.get(li, []))
    o = [f'<text x="{x0}" y="{y0+24}" class="lname">{esc(name)}</text>',
         f'<text x="{x0}" y="{y0+44}" class="lnote">{esc(note)}</text>']
    by = y0 + LAYER_HEAD
    for (r, c), (half, x, y, rot, h) in PHYS.items():
        code, label = grid[r][c]
        assert (code, label) != HOLE
        px = x0 + (x + (HALF_W + SPLIT if half == "R" else 0)) * U + U / 2
        py = by + y * U + U / 2
        w, hh = KS, KS + (h - 1) * U
        is_held = (r, c) in held
        is_layer = code.startswith(("MO(", "TG(", "DF("))
        trns = code == "KC_TRNS"
        if is_held:
            fill, stroke, cls, label = HELD_BG, HELD_BG, "kheld", "mantener"
        elif is_layer:
            fill, stroke, cls = ACCENT_BG, ACCENT, "kmo"
        else:
            fill, stroke, cls = KEY, BORDER, ("ktrns" if trns else "klbl")
        if trns and not is_held:
            label = "▽"
        g = f'<g transform="translate({px:.1f},{py:.1f}) rotate({rot})">'
        o.append(g + f'<rect x="{-w/2}" y="{-hh/2:.1f}" width="{w}" height="{hh:.1f}" rx="7" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/></g>')
        lines = label.split("\n")
        size = 16 if max(len(l) for l in lines) <= 4 else (13 if max(len(l) for l in lines) <= 6 else 11)
        ty0 = 5 - (len(lines) - 1) * 7
        for i, ln in enumerate(lines):
            # el texto no se gira: asi se lee recto y ▽ no parece una flecha
            o.append(f'<text x="{px:.1f}" y="{py + ty0 + i*14:.1f}" class="{cls}" '
                     f'style="font-size:{size}px">{esc(ln)}</text>')
    return o


def svg(width, height, body, bg=BG):
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="DejaVu Sans, Inter, Helvetica, sans-serif">',
            f'<rect width="{width}" height="{height}" fill="{bg}"/>',
            '<style>',
            f'.title{{font-size:28px;font-weight:700;fill:{KEY_TX}}}',
            f'.sub{{font-size:14px;fill:{MUTED}}}',
            f'.lname{{font-size:19px;font-weight:700;fill:{ACCENT}}}',
            f'.lnote{{font-size:13px;fill:{MUTED}}}',
            f'.klbl{{fill:{KEY_TX};text-anchor:middle}}',
            f'.ktrns{{fill:{TRNS_TX};text-anchor:middle}}',
            f'.kmo{{fill:{ACCENT};font-weight:700;text-anchor:middle}}',
            f'.kheld{{fill:{HELD_TX};font-weight:700;text-anchor:middle}}',
            f'.box{{fill:#ffffff;stroke:{BORDER};stroke-width:1.2}}',
            f'.bh{{font-size:15px;font-weight:700;fill:{KEY_TX}}}',
            f'.bt{{font-size:13.5px;fill:{KEY_TX}}}',
            f'.cut{{fill:none;stroke:#9a978e;stroke-width:1.2;stroke-dasharray:7 5}}',
            f'.scis{{font-size:18px;fill:#9a978e}}',
            f'.ctitle{{font-size:15px;font-weight:700;fill:{KEY_TX}}}',
            '</style>']
    return "\n".join(head + body + ['</svg>'])


def info_box(x, y, w, title, lines):
    h = 46 + 21 * len(lines)
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="box"/>',
         f'<text x="{x+18}" y="{y+26}" class="bh">{esc(title)}</text>']
    for i, ln in enumerate(lines):
        o.append(f'<text x="{x+18}" y="{y+50+i*21}" class="bt">{esc(ln)}</text>')
    return o, h


LEGEND = ("▽ = transparente (hace lo de la capa de debajo) · tecla oscura = la que mantienes "
          "para estar en esa capa · naranja = cambia de capa")

TYPING_NOTES = [
    "NUM (pulgar izq.) = números, flechas y modificadores en la fila central.",
    "SYM (pulgar der.) = símbolos de programación.   NUM + SYM a la vez = FN (F1–F12, multimedia).",
    "` y ^ son teclas muertas en «es»: pulsa espacio después para que salgan solas.",
]
GAME_NOTES = [
    "Entrar y salir del modo juego: mantén SYM y pulsa Esc (es un interruptor).",
    "Al desenchufar el teclado vuelve siempre al modo normal.",
    "Mano izquierda en el juego; la derecha es la normal, para el chat (SYM también funciona).",
    "G-FN (pulgar izq. interior) da 1–0 y F1–F5. FN (F6–F12, multimedia) no está en el modo juego.",
]


def page(title, sub, layer_ids, box_title, notes, width=None, height=None):
    width = width or BOARD_W + 2 * MARGIN
    x0 = (width - BOARD_W) / 2
    body = [f'<text x="{x0}" y="{MARGIN+26}" class="title">{esc(title)}</text>',
            f'<text x="{x0}" y="{MARGIN+50}" class="sub">{esc(sub)}</text>',
            f'<text x="{x0}" y="{MARGIN+70}" class="sub">{esc(LEGEND)}</text>']
    y = MARGIN + 92
    box, bh = info_box(x0, y, BOARD_W, box_title, notes)
    body += box
    y += bh + 26
    for li in layer_ids:
        body += draw_layer(x0, y, li)
        y += LAYER_H + LAYER_GAP
    return svg(width, height or int(y + MARGIN - LAYER_GAP), body)


# --- PDF para la pared: tarjetas recortables, una por capa -------------------------
A4W, A4H = 1240, 1754          # A4 vertical a 150 ppp
CARD_PAD = 24
CARD_W = BOARD_W + 2 * CARD_PAD
CARD_H = CARD_PAD + LAYER_H + 12
CARD_GAP = 26                  # hueco entre tarjetas: se corta por las dos lineas


def cut_frame(x, y, w, h):
    """Linea discontinua de corte con unas tijeras en la esquina."""
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="cut"/>',
            f'<rect x="{x+14}" y="{y-11}" width="24" height="22" fill="#ffffff"/>',
            f'<text x="{x+16}" y="{y+7}" class="scis">✂</text>']


def layer_card(x, y, li):
    return cut_frame(x, y, CARD_W, CARD_H) + draw_layer(x + CARD_PAD, y + CARD_PAD - 4, li)


def info_card(x, y):
    sections = [("Leyenda", ["▽ = transparente: hace lo mismo que en la capa de debajo",
                             "Tecla oscura «mantener» = la que mantienes para estar en esa capa",
                             "Naranja = tecla que cambia de capa"]),
                ("Escribir", TYPING_NOTES),
                ("Jugar", GAME_NOTES)]
    o = cut_frame(x, y, CARD_W, CARD_H)
    o.append(f'<text x="{x+CARD_PAD}" y="{y+CARD_PAD+20}" class="lname">'
             f'Corne · layout español · cómo se usa</text>')
    ty = y + CARD_PAD + 52
    for head, lines in sections:
        o.append(f'<text x="{x+CARD_PAD}" y="{ty}" class="ctitle">{esc(head)}</text>')
        ty += 22
        for ln in lines:
            o.append(f'<text x="{x+CARD_PAD+12}" y="{ty}" class="bt">{esc(ln)}</text>')
            ty += 20
        ty += 10
    assert ty < y + CARD_H, "la tarjeta de instrucciones no cabe"
    return o


def card_page(cards):
    """cards = lista de li (int) o "info". Hasta 4 por pagina A4."""
    assert len(cards) <= 4
    x = (A4W - CARD_W) / 2
    y = (A4H - (4 * CARD_H + 3 * CARD_GAP)) / 2
    body = []
    for c in cards:
        body += info_card(x, y) if c == "info" else layer_card(x, y, c)
        y += CARD_H + CARD_GAP
    return svg(A4W, A4H, body, bg="#ffffff")


def main():
    os.makedirs(DOCS, exist_ok=True)
    title = "Corne · layout español para desarrollo"
    sub = "Pilot W-CORNE, 46 teclas · SO en xkb «es»"

    # SVG unico con todo (README)
    combined = page(title, sub, range(len(LAYERS)), "Cómo se usa", TYPING_NOTES + GAME_NOTES)
    path = os.path.join(DOCS, "corne-es-layout.svg")
    open(path, "w", encoding="utf-8").write(combined)
    print(path)

    # PDF A4 para la pared: tarjetas recortables (pagina 1: escribir; pagina 2: jugar + ayuda)
    pages = [card_page([0, 1, 2, 3]), card_page([4, 5, 6, "info"])]
    tmp = []
    for i, s in enumerate(pages):
        p = os.path.join(DOCS, f".page{i+1}.svg")
        open(p, "w", encoding="utf-8").write(s)
        tmp.append(p)
    pdf = os.path.join(DOCS, "corne-es-layout.pdf")
    try:
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf] + tmp, check=True)
        subprocess.run(["rsvg-convert", "-w", "2000", "-o",
                        os.path.join(DOCS, "corne-es-layout.png"), path], check=True)
        print(pdf)
    except FileNotFoundError:
        print("rsvg-convert no esta instalado: solo se ha generado el SVG")
    finally:
        for p in tmp:
            os.remove(p)


if __name__ == "__main__":
    main()
