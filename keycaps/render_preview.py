# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow", "fonttools", "shapely"]
# ///
# -*- coding: utf-8 -*-
"""Dibuja keycaps/plate_preview.png a partir de out/plate_corne.3mf.

Vista en perspectiva caballera (ortografica inclinada), sombreado por normal y pintado de
atras adelante. Los colores son los de las capturas de build_caps.py (los reales se ponen
en el slicer).

    uv run keycaps/render_preview.py
    uv run keycaps/render_preview.py --flat     # perfil plano -> out_flat/plate_preview.png
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_caps import COLORS  # noqa: E402
from mesh3mf import read_3mf  # noqa: E402

_FLAT = "--flat" in sys.argv
PLATE = os.path.join(HERE, "out_flat" if _FLAT else "out", "plate_corne.3mf")
OUT = os.path.join(HERE, "out_flat" if _FLAT else "", "plate_preview.png")
TILT = np.radians(38)     # inclinacion de la camara respecto a la vertical
PX_PER_MM = 7.0
SS = 2                    # supermuestreo (se reduce al final: bordes suaves)
BG = (250, 249, 246)
LIGHT = np.array([-0.35, -0.45, 0.82])
LIGHT /= np.linalg.norm(LIGHT)


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def main():
    parts = read_3mf(PLATE)
    # rotacion alrededor de x: la camara mira desde delante y arriba
    c, s = np.cos(TILT), np.sin(TILT)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    polys, depth, fills = [], [], []
    for name, (vs, ts) in parts.items():
        V = np.asarray(vs, float) @ R.T
        T = np.asarray(ts, int)
        a, b, cc = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
        n = np.cross(b - a, cc - a)
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        n[ok] /= ln[ok, None]
        front = ok & (n[:, 2] > 0)                  # solo caras que miran a la camara
        Ln = np.asarray(LIGHT) @ R.T
        shade = 0.35 + 0.65 * np.clip(n[front] @ Ln, 0, 1)
        base = hex_rgb(COLORS[name])
        col = np.clip(base[None, :] * shade[:, None], 0, 255).astype(np.uint8)
        tri = np.stack([a[front], b[front], cc[front]], axis=1)
        polys.append(tri[:, :, :2])
        depth.append(tri[:, :, 2].mean(axis=1))
        fills.append(col)
    P = np.concatenate(polys)
    Z = np.concatenate(depth)
    C = np.concatenate(fills)
    order = np.argsort(Z)                           # de lejos a cerca
    lo, hi = P.reshape(-1, 2).min(0), P.reshape(-1, 2).max(0)
    margin = 8.0
    k = PX_PER_MM * SS
    W, H = (int((hi - lo)[i] * k + 2 * margin * k) for i in (0, 1))
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i in order:
        q = (P[i] - lo + margin) * k
        q[:, 1] = H - q[:, 1]                       # y de imagen hacia abajo
        d.polygon([tuple(p) for p in q], fill=tuple(int(x) for x in C[i]))
    img = img.resize((W // SS, H // SS), Image.LANCZOS)
    img.save(OUT, optimize=True)
    print(OUT, img.size, f"{len(order)} triangulos")


if __name__ == "__main__":
    main()
