# -*- coding: utf-8 -*-
"""Contornos de las leyendas, preparados para imprimir en FDM con boquilla de 0,4 mm.

`sketch.text` de SolidCraft dibuja la fuente tal cual: a 2,6 mm de altura algunos trazos
miden 0,4 mm y el slicer (generador de paredes "classic" de Anycubic Slicer Next) los
descarta. Aqui se sacan los contornos de la fuente con fontTools, se engordan con
shapely lo justo para que ningun trazo baje de MIN_STROKE sin cerrar los huecos de las
letras (o, a, @...) ni pegar letras vecinas, y se devuelven como poligonos que
build_caps.py dibuja con `sketch.line`.

Reglas de diseño (linea de extrusion ~0,42 mm con boquilla de 0,4):
  MIN_STROKE = 0,90 mm  trazo al que se intenta llegar engordando (2 lineas completas)
  CLEAN_MIN  = 0,80 mm  por debajo sale en borron (medido en impresiones de prueba)
  PRINT_MIN  = 0,58 mm  por debajo, el slicer (classic) lo descarta: en una prueba, un +
                        de 0,61 salia y un ⌃ de 0,42 no
  MIN_GAP    = 0,40 mm  hueco de color de la tecla entre trazos: ~1 linea
"""
import os
from functools import lru_cache

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.ops import nearest_points, unary_union

# JetBrainsMono Nerd Font Bold (https://www.nerdfonts.com). Otra ruta: variable KEYCAP_FONT
FONT = os.environ.get("KEYCAP_FONT", "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf")
MIN_STROKE = 0.90
CLEAN_MIN = 0.80     # trazo que sale limpio (0,87 bien; 0,7 en borron)
PRINT_MIN = 0.58
MIN_GAP = 0.40
MAX_SPREAD = 0.45    # lo maximo que se separa un trozo (punto de la i, de la !...)
MAX_GROW = 0.30      # lo maximo que se engorda cada lado del trazo (mm)
TRACKING = 0.35     # espacio extra entre letras (mm): al engordar no se pegan
FLAT = 0.02          # tolerancia al aproximar curvas (mm, a la escala final aprox.)


class _FlatPen(BasePen):
    """Recoge los contornos de un glifo como anillos de puntos (curvas aproximadas)."""

    def __init__(self, glyphset, steps=8):
        super().__init__(glyphset)
        self.rings, self.cur, self.steps = [], [], steps

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            a = (1 - t) ** 2
            b = 2 * (1 - t) * t
            c = t * t
            self.cur.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            m = 1 - t
            self.cur.append((m ** 3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t ** 3 * p3[0],
                             m ** 3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t ** 3 * p3[1]))

    def _closePath(self):
        if len(self.cur) >= 3:
            self.rings.append(self.cur)
        self.cur = []

    _endPath = _closePath


@lru_cache(maxsize=1)
def _font():
    f = TTFont(FONT)
    cap = f["OS/2"].sCapHeight or 0.73 * f["head"].unitsPerEm
    return f, f.getGlyphSet(), f.getBestCmap(), cap


def _rings_to_geom(rings):
    """Anillos de TrueType -> geometria con huecos (regla par-impar, como el rasterizado)."""
    g = Polygon()
    for r in rings:
        p = Polygon(r).buffer(0)
        g = g.symmetric_difference(p)
    return g


def raw_text(text, cap_h, tracking=TRACKING):
    """Texto en milimetros: altura de mayuscula = cap_h, origen en el inicio de la linea base.
    tracking: espacio extra entre caracteres, en mm."""
    f, gs, cmap, cap = _font()
    k = cap_h / cap
    parts, x = [], 0.0
    for ch in text:
        if ord(ch) not in cmap:
            raise KeyError(f"la fuente no tiene {ch!r} (U+{ord(ch):04X})")
        name = cmap[ord(ch)]
        pen = _FlatPen(gs)
        gs[name].draw(pen)
        g = _rings_to_geom(pen.rings)
        if not g.is_empty:
            parts.append(affinity.translate(g, xoff=x))
        x += gs[name].width + tracking / k
    geom = unary_union(parts) if parts else Polygon()
    return affinity.scale(geom, k, k, origin=(0, 0)), x * k


def _pieces(g):
    return [p for p in getattr(g, "geoms", [g]) if not p.is_empty]


def inscribed(p):
    """Anchura maxima de un poligono (diametro del mayor circulo inscrito)."""
    lo, hi = 0.0, 2.0
    for _ in range(22):
        m = (lo + hi) / 2
        if p.buffer(-m).is_empty:
            hi = m
        else:
            lo = m
    return 2 * lo


def thin_fraction(g, width):
    """Fraccion del area que NO cabe en un trazo de `width` (0 = todo imprimible)."""
    if g.is_empty:
        return 0.0
    kept = g.buffer(-width / 2).buffer(width / 2)
    return max(0.0, 1 - kept.area / g.area)


def gaps(g):
    """Huecos de color de la tecla: anchura de cada contraforma y distancia entre piezas."""
    ps = _pieces(g)
    out = [inscribed(Polygon(r)) for p in ps for r in p.interiors]
    out += [ps[i].distance(ps[j]) for i in range(len(ps)) for j in range(i + 1, len(ps))]
    return out


def _spread(g, target):
    """Separa las piezas que estan a menos de `target` (el punto de la ! de su palo, las
    dos rayas del =...): mueve la pieza pequeña en la direccion que las une."""
    ps = _pieces(g)
    for _ in range(6):
        moved = False
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                dist = ps[i].distance(ps[j])
                if dist >= target - 1e-3:
                    continue
                a, b = nearest_points(ps[i], ps[j])
                vx, vy = b.x - a.x, b.y - a.y
                n = (vx * vx + vy * vy) ** 0.5
                if n < 1e-6:
                    continue                      # se tocan: se dejan unidas
                step = min(target - dist, MAX_SPREAD)
                small = j if ps[j].area <= ps[i].area else i
                sgn = 1 if small == j else -1
                ps[small] = affinity.translate(ps[small], sgn * vx / n * step, sgn * vy / n * step)
                moved = True
        if not moved:
            break
    return unary_union(ps)


def printable(g):
    """Prepara g para FDM:
    1. contraformas mas estrechas que MIN_GAP: se rellenan (el slicer no imprimiria esa
       pared de tecla y saldria un borron de todos modos);
    2. engorde necesario para acercar los trazos a MIN_STROKE;
    3. las piezas sueltas se separan para que el engorde no las pegue;
    4. se engorda sin que ninguna contraforma que se conserva baje de MIN_GAP.
    Devuelve (geometria, engorde, fraccion por debajo de CLEAN_MIN, hueco minimo)."""
    filled = [Polygon(p.exterior, [r for r in p.interiors if inscribed(Polygon(r)) >= MIN_GAP])
              for p in _pieces(g)]
    g = unary_union(filled)
    need = MAX_GROW
    for d in [i * 0.01 for i in range(0, int(MAX_GROW * 100) + 1)]:
        if thin_fraction(g.buffer(d) if d else g, MIN_STROKE) < 0.10:
            need = d
            break
    g = _spread(g, MIN_GAP + 2 * need)
    holes = [inscribed(Polygon(r)) for p in _pieces(g) for r in p.interiors]
    ps = _pieces(g)
    dists = [ps[i].distance(ps[j]) for i in range(len(ps)) for j in range(i + 1, len(ps))]
    room = min([(x - MIN_GAP) / 2 for x in holes] +
               [max(0.0, (x - MIN_GAP) / 2) for x in dists if x > 1e-6], default=MAX_GROW)
    d = max(0.0, min(need, room, MAX_GROW))
    t = g.buffer(d) if d else g
    return t, d, thin_fraction(t, CLEAN_MIN), min(gaps(t), default=9.0)


def legend(text, cap_h, max_w, align, at):
    """Leyenda lista para dibujar: (poligonos [(exterior, [huecos])], informe).

    cap_h: altura deseada; se reduce si el texto (ya engordado) no cabe en max_w.
    align: center | left | right respecto a at[0]; at[1] es la linea base."""
    h = cap_h
    for _ in range(12):
        raw, _adv = raw_text(text, h)
        geom, grow, thin, gap = printable(raw)
        minx, miny, maxx, maxy = geom.bounds
        if maxx - minx <= max_w + 1e-6:
            break
        h *= max_w / (maxx - minx) * 0.99
    minx, miny, maxx, maxy = geom.bounds
    if align == "center":
        dx = at[0] - (minx + maxx) / 2
    elif align == "left":
        dx = at[0] - minx
    else:
        dx = at[0] - maxx
    geom = affinity.translate(geom, xoff=dx, yoff=at[1])
    geom = geom.simplify(FLAT, preserve_topology=True)
    polys = []
    for p in getattr(geom, "geoms", [geom]):
        if p.is_empty or p.area < 0.01:
            continue
        ext = [list(map(lambda v: round(v, 4), c)) for c in list(p.exterior.coords)[:-1]]
        holes = [[list(map(lambda v: round(v, 4), c)) for c in list(r.coords)[:-1]] for r in p.interiors]
        polys.append((ext, holes))
    info = dict(text=text, height=round(h, 3), grow=round(grow, 3), thin=round(thin, 3),
                gap=round(gap, 3), width=round(maxx - minx, 3))
    return polys, info


if __name__ == "__main__":
    import sys
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 2.6
    for t in sys.argv[2:] or ["⌃", "F", "+", "^Z", "@", "⇥", "&", "¿", "\uf11b", "⇪", "$", "%", "!"]:
        _, i = legend(t, h, 20.0, "center", (0, 0))
        r, _ = raw_text(t, i["height"])
        print(f"{t!r:8} h={i['height']:.2f} engorde={i['grow']:.2f} fino: {thin_fraction(r, MIN_STROKE):4.0%} -> {i['thin']:4.0%}  hueco min {i['gap']:.2f}")
