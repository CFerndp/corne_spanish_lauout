# /// script
# requires-python = ">=3.10"
# dependencies = ["shapely"]
# ///
# -*- coding: utf-8 -*-
"""Comprueba en los STL generados que las leyendas se pueden imprimir con boquilla de 0,4.

Corta cada leyenda (base/num/sym) a media profundidad, igual que hara el slicer en una
capa, y mide que fraccion del area cabe en un trazo de PRINT_MIN (0,58 mm): lo que no
cabe, el generador de paredes "classic" lo descarta. Es la comprobacion independiente
del CAD: glyphs.py ya diseña para esto, aqui se mira lo que de verdad ha salido.

    uv run keycaps/check_stl.py                 # todas las teclas de out/stl
    uv run keycaps/check_stl.py r1c4 r3c5       # solo esas
    uv run keycaps/check_stl.py --flat          # las del perfil plano (out_flat/)
"""
import glob
import os
import struct
import sys

from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = "out_flat" if "--flat" in sys.argv else "out"
PRINT_MIN = 0.58   # por debajo, el slicer lo descarta
CLEAN_MIN = 0.80   # por debajo, sale en borron
LIMIT = 0.15       # fraccion maxima de area por debajo de PRINT_MIN
CLEAN_LIMIT = 0.20 # fraccion maxima de area por debajo de CLEAN_MIN (aviso)


def read_stl(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    return [struct.unpack("<12f", d[84 + 50 * i:84 + 50 * i + 48])[3:] for i in range(n)]


def section(tris, z):
    """Seccion de la malla en z como geometria (par-impar sobre los lazos cerrados)."""
    segs = []
    for t in tris:
        p = (t[0:3], t[3:6], t[6:9])
        pts = []
        for a, b in ((p[0], p[1]), (p[1], p[2]), (p[2], p[0])):
            if (a[2] - z) * (b[2] - z) < 0:
                k = (z - a[2]) / (b[2] - a[2])
                pts.append((round(a[0] + k * (b[0] - a[0]), 5), round(a[1] + k * (b[1] - a[1]), 5)))
        if len(pts) == 2 and pts[0] != pts[1]:
            segs.append(pts)
    # encadenar segmentos en lazos
    adj = {}
    for a, b in segs:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen, loops = set(), []
    for start in adj:
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = [q for q in adj[cur] if q != prev and (q not in seen or q == start)]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            if cur == start:
                break
            seen.add(cur)
            loop.append(cur)
        if len(loop) >= 3:
            loops.append(loop)
    g = Polygon()
    for lp in loops:
        g = g.symmetric_difference(Polygon(lp).buffer(0))
    return g


def check(path):
    """La leyenda va incrustada bajo un tope curvo: un corte horizontal a media
    altura solo toca parte de ella. Se usa la capa de mayor area, donde la leyenda esta
    entera: es la que el slicer tiene que rellenar con el trazo completo."""
    tris = read_stl(path)
    zs = [t[i] for t in tris for i in (2, 5, 8)]
    z0, z1 = min(zs), max(zs)
    best = None
    for i in range(1, 12):
        g = section(tris, z0 + i / 12 * (z1 - z0))
        if not g.is_empty and (best is None or g.area > best.area):
            best = g
    if best is None or best.area < 1e-3:
        return 1.0, 1.0
    def frac(w):
        kept = best.buffer(-w / 2).buffer(w / 2)
        return max(0.0, 1 - kept.area / best.area)
    return frac(PRINT_MIN), frac(CLEAN_MIN)


def main():
    pats = [a for a in sys.argv[1:] if a != "--flat"] or [""]
    files = sorted({f for p in pats for f in glob.glob(os.path.join(HERE, OUTDIR, "stl", f"{p}*.stl"))
                    if not f.endswith(".cap.stl")})
    bad = 0
    for f in files:
        w, c = check(f)
        ok = w <= LIMIT
        bad += not ok
        tag = "MAL" if not ok else ("aviso" if c > CLEAN_LIMIT else "ok")
        print(f"{tag:5} {w:4.0%} se pierde  {c:4.0%} borroso  {os.path.basename(f)}")
    print(f"{len(files)} leyendas, {bad} con trazos que el slicer descartaria")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
