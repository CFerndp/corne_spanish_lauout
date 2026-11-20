# -*- coding: utf-8 -*-
"""Leyendas impresas de cada tecla, derivadas de spec.py.

spec.py es la fuente de verdad del .vil y no se toca: aqui solo se traducen sus
etiquetas a versiones cortas que caben en el tope de una tecla de ~13 mm y que la
fuente (JetBrainsMono Nerd Font Bold) tiene como glifo.

Cada tecla lleva hasta tres leyendas, cada una en su color (ACE Pro):
  base -> centro del tope          (capa 0)
  num  -> abajo a la izquierda     (capa 1 · NUM/NAV)
  sym  -> abajo a la derecha       (capa 2 · SYM)
La capa 3 (FN) no se imprime: los F1-F12 siguen a los numeros y no cabe un 5º color.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from spec import L0, L1, L2  # noqa: E402

# etiqueta de spec.py -> texto impreso (lo que no aparece aqui se imprime tal cual)
PRINT = {
    "Shift": "⇧",
    "Tab": "⇥",
    "Enter": "⏎",
    "Space": "Spc",  # ␣ deja la malla de la tecla de 1,5u con caras internas (kernel)
    "Bksp": "⌫",
    "Game": "\uf11b",  # mando (Nerd Font): SYM + Esc = modo juego
    "Caps": "Bloq",  # Bloq Mayús; "Caps" pega la a y la p al engordar
    "Supr": "Supr",  # ⌦ se confunde con ⌫ a este tamaño
    "Super": "",  # logo de Arch (Nerd Font)
    "NUM\nNAV": "NUM",
    "FN": "Fn",
    "AltGr": "⌥",  # como Alt: es el Alt de la derecha. "AG" no cabe con trazo limpio
    "Undo": "^Z",
    "Cut": "^X",
    "Copy": "^C",
    "Paste": "^V",
    "Redo": "\uf01e",  # ↻ (Nerd Font): ⇧^Z no cabe con trazos imprimibles
    "Home": "↖",
    "End": "↘",
    "Menu": "☰",
    "Ins": "In",
    "` +esp": "`",
    "^ +esp": "^",
    "´ ¨": "´¨",
    "PgUp": "PU",
    "PgDn": "PD",
}

# en las subleyendas (letra pequena) los modificadores van como simbolo
PRINT_SUB = {"Ctrl": "⌃", "Alt": "⌥", "Shift": "⇧"}

SKIP = {"-1", "KC_TRNS"}


def _label(layer, r, c, sub=False):
    code, label = layer[r][c]
    if code in SKIP:
        return None
    if sub and label in PRINT_SUB:
        return PRINT_SUB[label]
    return PRINT.get(label, label)


def keys():
    """Lista de teclas fisicas: dict(row, col, base, num, sym)."""
    out = []
    for r in range(4):
        for c in range(12):
            if L0[r][c][0] == "-1":
                continue
            out.append(dict(row=r, col=c, base=_label(L0, r, c),
                            num=_label(L1, r, c, True), sym=_label(L2, r, c, True)))
    return out


if __name__ == "__main__":
    ks = keys()
    for k in ks:
        print(f"r{k['row']}c{k['col']:<2} base={k['base']!s:6} num={k['num']!s:6} sym={k['sym']!s:6}")
    print(len(ks), "teclas")
