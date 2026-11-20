# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools", "shapely"]
# ///
# -*- coding: utf-8 -*-
"""Genera keycaps MX ergonomicos para el Corne con SolidCraft (solidcraft-cli).

Cada tecla se describe como un script de comandos SolidCraft (JSON) y se ejecuta sin
ventana. Cuerpos por tecla, uno por color del ACE Pro:
  cap  -> cuerpo de la tecla       (filamento 1)
  base -> leyenda de la capa 0     (filamento 2)
  num  -> leyenda de la capa 1     (filamento 3)
  sym  -> leyenda de la capa 2     (filamento 4)
Las leyendas van incrustadas a ras del dish (inlay), no en relieve. Sus contornos salen
de glyphs.py, ya engordados para FDM con boquilla de 0,4 (ver alli las reglas).

Uso (uv instala fonttools y shapely):
  uv run keycaps/build_caps.py                  # las 46 teclas + placa
  uv run keycaps/build_caps.py --keys r1c4      # solo F
  uv run keycaps/build_caps.py --probe          # probeta de holgura del vastago
  uv run keycaps/build_caps.py --check          # solo comprueba las leyendas, sin CAD
  uv run keycaps/build_caps.py --preview        # ademas, una captura PNG por tecla
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from glyphs import MIN_GAP, PRINT_MIN, legend, raw_text, thin_fraction  # noqa: E402
from legends import keys as all_keys  # noqa: E402
from mesh3mf import (fill_small_holes, group_by_color, merge, open_edges, read_3mf,  # noqa: E402
                     write_3mf, write_stl)  # noqa: E402

OUT = os.path.join(HERE, "out")
CLI = shutil.which("solidcraft-cli") or os.path.expanduser("~/.local/bin/solidcraft-cli")

# ---------------------------------------------------------------- parametros
P = dict(
    BASE=18.0,          # lado inferior (paso MX 19.05 -> ~1 mm de hueco)
    BASE_R=1.2,         # radio de esquina abajo
    TOP=13.6,           # lado del tope
    TOP_R=2.2,          # radio de esquina del tope
    WALL=1.4,           # pared lateral
    TOP_THICK=1.6,      # techo bajo el punto mas hondo del dish
    DISH_R=40.0,        # radio del dish esferico
    DISH_D=0.5,         # profundidad del dish en el centro
    DOME_RISE=0.8,      # pulgares: lo que sube la cupula convexa
    # Vastago medido en un keycap impreso en la misma impresora que ya encajaba bien
    # (cilindro 5,5, cruz 4,0 x 1,5 mm) y validado imprimiendo estas teclas
    STEM_D=5.5,         # cilindro del vastago
    CROSS_L=4.0,        # brazo de la cruz (a ras con el vastago MX: es lo que sujeta)
    CROSS_W=1.5,        # ancho del brazo (MX real ~1,17: +0,33 de holgura)
    CROSS_DEPTH=4.0,    # profundidad de la cruz
    STEM_CLEAR=0.0,     # holgura extra sobre la cruz (la probeta prueba -0,05 .. +0,10)
    INLAY=1.0,          # profundidad de la leyenda incrustada. Con menos no habia ninguna capa
                        # en la que una subleyenda estuviera entera en las filas inclinadas
    H_BASE=4.2,         # altura de mayuscula de la leyenda base
    H_SUB=3.6,          # altura de las subleyendas (mas pequeñas, los trazos no se imprimen)
    TEXT_MARGIN=1.3,    # margen de texto al borde del tope
    Y_BASE=2.2,         # centro vertical de la leyenda base (sobre el centro del tope)
    Y_SUB=-3.3,         # centro vertical de las subleyendas
    SUB_GAP=1.0,        # hueco minimo entre las dos subleyendas
    HOMING_R=0.55,      # barra de posicion en F y J
    HOMING_L=4.0,
)

# perfil por fila: (altura en el centro del tope, inclinacion en grados)
# inclinacion > 0: el tope mira hacia ti (fila de arriba); < 0: mira hacia fuera.
ROWS = {
    0: (9.4, 8.0),
    1: (8.4, 0.0),   # fila base: la mas baja y plana
    2: (8.9, -6.0),
    3: (8.9, -6.0),  # teclas de la fila 3 que NO son de pulgar: como la fila 2
}
# Perfil PLANO (--flat): todas las teclas con el tope plano, horizontal y a la misma altura.
# Asi las leyendas de las 46 teclas caen en las mismas pocas capas: ~12 cambios de color
# en vez de ~100. Se pierde la forma esculpida (filas, dish, cupula).
# El tope y el fondo de la leyenda caen en fronteras de capa del perfil oficial de la Kobra S1
# (primera capa 0,2 mm, resto a 0,12): 0,2 + 68*0,12 = 8,36 y 8,36 - 3*0,12 = 8,00.
FLAT = dict(H=8.36, INLAY=0.36)  # 0,36 = exactamente 3 capas de 0,12
FLAT_MODE = False                # lo activa --flat

THUMB_H = 8.4  # pulgares: altura en el borde; la cupula sube DOME_RISE por encima

# Teclas de pulgar (cupula convexa): Ctrl NUM Enter | Space SYM Super. Confirmado en Vial.
THUMB = {(3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8)}
# Pulgar mas interior (Enter, Space): 1,5u, alargado hacia ti (eje y de la tecla), como en
# el Corne v4 / W-Corne v4.1 (build guide: 40 x 1u + 2 x 1,5u).
LONG = {(3, 5), (3, 6)}
U_PITCH = 19.05

# La fila 3 de la matriz tambien guarda teclas que fisicamente estan en otras filas
# (confirmado en Vial): su perfil es el de su fila fisica.
PHYS_ROW = {(3, 0): 0, (3, 1): 1,                 # columna interior izq. (junto a T, G)
            (3, 9): 0, (3, 10): 1, (3, 11): 2}    # columna exterior der. (meñique)

HOMING = {(1, 4), (1, 8)}  # F y J

# glifos que son solo puntos/rayas/acentos: se agrandan (el ancho sigue limitando)
THIN = set(".,:;'`-_\"!¡^~´¨")  # | y \\ no: ya son mas altos que una mayuscula
THIN_SCALE = 1.3
# fraccion maxima del area de una leyenda con trazo < PRINT_MIN. El STL real sale un poco
# peor que el diseño (malla, tope curvo): check_stl.py pide <= 15 %, aqui se deja margen
THIN_MAX = 0.10  # fraccion del area de una leyenda por debajo de CLEAN_MIN (LOOSE: PRINT_MIN)
# leyendas que necesitan mas altura para que sus trazos se impriman
SIZE = {"%": 4.0, "#": 4.4, "@": 4.2, "$": 3.2}  # $ mas pequeño: a 3,6 sus huecos no dejan engordar
# glifos con huecos tan cerrados que no llegan a CLEAN_MIN a ningun tamaño que quepa: para
# ellos solo se exige el minimo que el slicer no descarta (PRINT_MIN)
LOOSE = {"%"}
BASE_THIN_SCALE = 1.15  # las leyendas base de solo signos (", ;") crecen menos: ya son grandes

# colores de las capturas (los reales los pones en el slicer)
COLORS = {"cap": "#3b4252", "base": "#eceff4", "num": "#88c0d0", "sym": "#ebcb8b"}

PROBE_CLEARANCES = [-0.05, 0.00, 0.05, 0.10]  # alrededor de la cruz validada (0)


# ---------------------------------------------------------------- geometria
def vadd(a, b, k=1.0):
    return [a[i] + k * b[i] for i in range(3)]


def r3(v):
    return [round(x, 4) for x in v]


class Script:
    def __init__(self):
        self.cmds = []
        self.n = 0

    def add(self, command, **params):
        self.cmds.append({"command": command, "params": params})

    def name(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    def rrect_sketch(self, plane, w, r, l=None):
        """Rectangulo redondeado de w (eje x) por l (eje y; por defecto cuadrado)."""
        l = w if l is None else l
        name = self.name("sk")
        self.add("sketch.create", plane=plane, name=name)
        self.add("sketch.rectangle.rounded", p0=[-w / 2, -l / 2], p1=[w / 2, l / 2], radius=r)
        self.add("sketch.finish")
        return name

    def polys_join(self, plane, polys, body):
        """Extruye los contornos de una leyenda uniendolos al cuerpo `body` (una placa
        auxiliar en el aire). Con operation=new saldria un cuerpo por cada trozo."""
        sk = self.name("tx")
        self.add("sketch.create", plane=plane, name=sk)
        for ext, holes in polys:
            for ring in [ext] + holes:
                self.add("sketch.line", points=ring, closed=True, connect=False)
        self.add("sketch.finish")
        self.add("solid.extrude", sketch=sk, distance=11, direction="negative",
                 operation="join", targets=[body])

def key_extra(row, col):
    """Alargamiento en y (mm) de la tecla: 0 en 1u, 0,5u en las de 1,5u."""
    return 0.5 * U_PITCH if (row, col) in LONG else 0.0


def frame(tilt_deg, h):
    t = math.radians(tilt_deg)
    x = [1.0, 0.0, 0.0]
    y = [0.0, math.cos(t), math.sin(t)]
    n = [0.0, -math.sin(t), math.cos(t)]
    o = [0.0, 0.0, h]
    return o, x, y, n


def plane(o, x, y):
    return {"origin": r3(o), "x_dir": r3(x), "y_dir": r3(y)}


def layout_legends(base, num, sym):
    """Contornos de las leyendas de una tecla, en coordenadas del tope (mm).
    Devuelve [(cuerpo, poligonos, info)]."""
    p = P
    usable = p["TOP"] - 2 * p["TEXT_MARGIN"]
    half = usable / 2
    out = []

    def size(text, h, base=False):
        h = SIZE.get(text, h)
        if all(ch in THIN or ch == " " for ch in text):
            h *= BASE_THIN_SCALE if base else THIN_SCALE
        return h

    def centred(polys, y):
        """Centra verticalmente la tinta en y."""
        ys = [pt[1] for e, hs in polys for ring in [e] + hs for pt in ring]
        dy = y - (min(ys) + max(ys)) / 2
        return [([[x, v + dy] for x, v in e], [[[x, v + dy] for x, v in r] for r in hs])
                for e, hs in polys]

    if base:
        polys, info = legend(base, size(base, p["H_BASE"], True), usable, "center", (0, 0))
        out.append(("base", centred(polys, p["Y_BASE"]), info))
    # las dos subleyendas se reparten el ancho segun lo que ocupa cada una a su tamaño
    def natural(t):
        if not t:
            return 0.0
        g, _ = raw_text(t, size(t, p["H_SUB"]))
        return max(g.bounds[2] - g.bounds[0], 0.5)
    n_num, n_sym = natural(num), natural(sym)
    room = usable - (p["SUB_GAP"] if num and sym else 0)
    if num:
        polys, info = legend(num, size(num, p["H_SUB"]), room * n_num / (n_num + n_sym),
                             "left", (-half, 0))
        out.append(("num", centred(polys, p["Y_SUB"]), info))
    if sym:
        polys, info = legend(sym, size(sym, p["H_SUB"]), room * n_sym / (n_num + n_sym),
                             "right", (half, 0))
        out.append(("sym", centred(polys, p["Y_SUB"]), info))
    return out


def check_legends(layout, extra=0.0):
    """Reglas de impresion: trazos imprimibles, huecos, dentro del tope, sin tocarse."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    p = P
    lim = box(-p["TOP"] / 2 + 0.6, -p["TOP"] / 2 + 0.6 - extra / 2,
              p["TOP"] / 2 - 0.6, p["TOP"] / 2 - 0.6 + extra / 2)
    problems, geoms = [], {}
    for body, polys, info in layout:
        g = unary_union([Polygon(e, hs) for e, hs in polys])
        geoms[body] = g
        if info["text"] in LOOSE:
            thin = thin_fraction(g, PRINT_MIN)
            if thin > THIN_MAX:
                problems.append(f"{body} {info['text']!r}: {thin:.0%} por debajo de {PRINT_MIN} mm")
        elif info["thin"] > THIN_MAX:
            problems.append(f"{body} {info['text']!r}: {info['thin']:.0%} de trazo demasiado fino")
        if info["gap"] < MIN_GAP - 0.02:
            problems.append(f"{body} {info['text']!r}: hueco de {info['gap']:.2f} mm")
        if not lim.contains(g):
            problems.append(f"{body} {info['text']!r}: se sale del tope")
    names = list(geoms)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = geoms[names[i]].distance(geoms[names[j]])
            if d < MIN_GAP + 0.05:
                problems.append(f"{names[i]} y {names[j]} a {d:.2f} mm")
    return problems


def cap_script(row, col, base, num, sym, clearance=None, notches=0):
    p = P
    thumb = (row, col) in THUMB and not FLAT_MODE
    if FLAT_MODE:
        h, tilt = FLAT["H"], 0.0
    else:
        h, tilt = (THUMB_H, 0.0) if thumb else ROWS[PHYS_ROW.get((row, col), row)]
    extra = key_extra(row, col)          # lo que se alarga en y una tecla de 1,5u
    BL, TL = p["BASE"] + extra, p["TOP"] + extra
    o, x, y, n = frame(tilt, h)
    s = Script()

    # --- cuerpo exterior: loft de rectangulo redondeado abajo -> tope inclinado
    top_h = h + (p["DOME_RISE"] if thumb else 0.0)
    o_top = vadd(o, n, top_h - h)
    # en los pulgares el loft sube 0.3 mm de mas: la esfera de la cupula (polo en top_h)
    # queda estrictamente por debajo de la tapa del loft, sin tangencias
    o_loft = vadd(o_top, n, 0.3) if thumb else o_top
    sk_b = s.rrect_sketch("XY", p["BASE"], p["BASE_R"], BL)
    sk_t = s.rrect_sketch(plane(o_loft, x, y), p["TOP"], p["TOP_R"], TL)
    s.add("solid.loft", sections=[{"sketch": sk_b}, {"sketch": sk_t}],
          operation="new", body_name="cap")

    # --- superficie superior
    R = p["DISH_R"]
    if thumb:
        # cupula: interseccion con una esfera cuyo polo esta en el tope
        c = vadd(o_top, n, -R)
        s.add("solid.sphere", radius=R, center=r3(c), operation="intersect", targets=["cap"])
        surf_center, surf_R, skin = c, R, "dome"
        if extra:
            # 1,5u: la esfera baja mas en las esquinas lejanas; el techo se mide desde ahi
            d = math.hypot(p["TOP"] / 2, TL / 2) - p["TOP_R"] * 0.3
            lowest_top = top_h - (R - math.sqrt(R * R - d * d))
        else:
            lowest_top = h - 0.6  # borde de la cupula, aprox.
    elif FLAT_MODE:
        c, surf_center, surf_R, skin = None, None, None, "flat"
        lowest_top = h
    else:
        c = vadd(o, n, R - p["DISH_D"])
        s.add("solid.sphere", radius=R, center=r3(c), operation="cut", targets=["cap"])
        surf_center, surf_R, skin = c, R, "dish"
        lowest_top = h - p["DISH_D"]

    # --- hueco interior: misma conicidad que el exterior, pared WALL
    hollow_from = len(s.cmds)
    roof = lowest_top - p["TOP_THICK"]              # altura del techo (en el eje)
    k = roof / top_h                                # fraccion de altura
    w_roof = p["BASE"] + (p["TOP"] - p["BASE"]) * k - 2 * p["WALL"]
    l_roof = BL + (TL - BL) * k - 2 * p["WALL"]
    o_roof = [o_top[i] * k for i in range(3)]       # sobre la recta base->tope
    # plano del techo paralelo al tope
    sk_ib = s.rrect_sketch(plane([0, 0, -0.5], [1, 0, 0], [0, 1, 0]),
                           p["BASE"] - 2 * p["WALL"] + 0.1, max(p["BASE_R"] - 0.4, 0.3),
                           BL - 2 * p["WALL"] + 0.1)
    sk_it = s.rrect_sketch(plane(o_roof, x, y), w_roof, max(p["TOP_R"] - 0.6, 0.4), l_roof)
    s.add("solid.loft", sections=[{"sketch": sk_ib}, {"sketch": sk_it}],
          operation="cut", targets=["cap"])

    # --- vastago MX: cilindro + cruz
    s.add("solid.cylinder", diameter=p["STEM_D"], height=roof + 0.8, base=[0, 0, 0],
          operation="join", targets=["cap"])
    clr = p["STEM_CLEAR"] if clearance is None else clearance
    L, W, D = p["CROSS_L"] + clr, p["CROSS_W"] + clr, p["CROSS_DEPTH"]
    s.add("solid.box", length=L, width=W, height=D + 1, center=[0, 0, (D - 1) / 2],
          operation="cut", targets=["cap"])
    s.add("solid.box", length=W, width=L, height=D + 1, center=[0, 0, (D - 1) / 2],
          operation="cut", targets=["cap"])

    hollow_to = len(s.cmds)

    # --- muescas de la probeta (en el borde trasero inferior: 1..4)
    for i in range(notches):
        xx = (i - (notches - 1) / 2) * 1.6
        s.add("solid.box", length=0.8, width=1.2, height=1.2,
              center=[xx, p["BASE"] / 2, 0], operation="cut", targets=["cap"])

    # --- barra de posicion (F, J)
    if (row, col) in HOMING and not thumb:
        v = -1.6
        if FLAT_MODE:
            hc = vadd(o, y, v)                      # eje de la barra sobre el tope plano
        else:
            sag = R - math.sqrt(R * R - v * v)
            hc = vadd(vadd(o, y, v), n, -(p["DISH_D"] - sag))
        base_pt = vadd(hc, x, -p["HOMING_L"] / 2)
        s.add("solid.cylinder", radius=p["HOMING_R"], height=p["HOMING_L"],
              base=r3(base_pt), axis=[1, 0, 0], operation="join", targets=["cap"])

    # --- leyendas incrustadas
    tp = plane(vadd(o_top, n, 5.5), x, y)  # plano de texto por encima de la placa
    legends = layout_legends(base, num, sym)

    for body, polys, _info in legends:
        # 1) placa auxiliar en el aire + columnas de texto unidas a ella (un solo cuerpo)
        # 2) recortar a INLAY mm bajo la superficie (sigue sobresaliendo al aire)
        # 3) vaciar ese hueco en la tecla  4) quitar lo que sobresale (y la placa).
        # Asi ningun booleano trabaja con caras coincidentes.
        c = r3(surf_center) if surf_center else None
        # placa entre +3 y +5 mm sobre el tope: dentro de la esfera del dish (se va al recortar)
        # y fuera de la de la cupula, para cualquier inclinacion de fila
        s.add("solid.box", length=15, width=15, height=2.0, center=[0, 0, round(top_h + 4.0, 4)],
              operation="new", body_name=body)
        s.polys_join(tp, polys, body)
        if skin == "flat":
            # columnas -> lamina de INLAY bajo el tope que sigue sobresaliendo al aire
            s.add("solid.box", length=30, width=40, height=10.0,
                  center=[0, 0, round(top_h - FLAT["INLAY"] - 5.0, 4)],
                  operation="cut", targets=[body])
        elif skin == "dish":
            s.add("solid.sphere", radius=surf_R + p["INLAY"], center=c,
                  operation="intersect", targets=[body])
        else:
            s.add("solid.sphere", radius=surf_R - p["INLAY"], center=c,
                  operation="cut", targets=[body])
        s.add("solid.combine", target="cap", tools=[body], operation="cut", keep_tools=True)
        if skin == "flat":
            s.add("solid.box", length=30, width=40, height=10.0,
                  center=[0, 0, round(top_h + 5.0, 4)], operation="cut", targets=[body])
        else:
            s.add("solid.sphere", radius=surf_R, center=c,
                  operation="cut" if skin == "dish" else "intersect", targets=[body])

    if thumb:
        # En los pulgares (cupula) el kernel no siempre admite restar la leyenda despues de
        # hacer el hueco y la cruz ("shell boundaries intersect or touch"): se vacian al final.
        hollow = s.cmds[hollow_from:hollow_to]
        s.cmds = s.cmds[:hollow_from] + s.cmds[hollow_to:] + hollow

    bodies = ["cap"] + [lg[0] for lg in legends]
    return s.cmds, bodies


# ---------------------------------------------------------------- ejecucion
PITCH = 21.0  # separacion en la placa de impresion (18 mm de tecla + 3 mm)


def run(cmds, stem, preview, extra=0.0):
    """Construye una tecla en SolidCraft y deja out/raw/<stem>.3mf con todos sus cuerpos."""
    raw = os.path.join(OUT, "raw", stem + ".3mf")
    cmds = cmds + [{"command": "file.export_3mf",
                    "params": {"path": raw, "quality": "fine", "objects": "body"}}]
    script = os.path.join(OUT, "scripts", stem + ".json")
    with open(script, "w") as f:
        json.dump({"commands": cmds}, f, ensure_ascii=False, indent=1)
    sc = os.path.join(OUT, "sc", stem + ".sc")
    r = subprocess.run([CLI, "run", script, "--save", sc], capture_output=True, text=True)
    if r.returncode != 0:
        return stem, False, (r.stderr or r.stdout)[-1500:]
    try:
        bodies = {n: fill_small_holes(m)[0] for n, m in read_3mf(raw).items()}
        parts = group_by_color(bodies)
    except Exception as e:  # noqa: BLE001
        return stem, False, f"post-proceso: {e}"
    problems, warnings = check(bodies, extra)
    if problems:
        return stem, False, "; ".join(problems)
    write_3mf(os.path.join(OUT, "keys", stem + ".3mf"), [(stem, parts)])
    for color, mesh in parts.items():
        write_stl(os.path.join(OUT, "stl", f"{stem}.{color}.stl"), mesh)
    if preview:  # reabre el diseno (lo recalcula): lento, opcional
        args = [CLI, "snapshot", "--in", sc, "--out", os.path.join(OUT, "png", stem + ".png"),
                "--view", "iso", "--no-grid", "--no-axes", "--width", "800", "--height", "600"]
        for name in read_3mf(raw):
            args += ["--body", f"{name}:color={COLORS[re.sub(r' [(][0-9]+[)]$', '', name)]}"]
        subprocess.run(args, capture_output=True, text=True)
    return stem, True, "; ".join(warnings)


def check(bodies, extra=0.0):
    """Malla estanca, nada fuera de la huella de la tecla, leyendas pegadas al tope."""
    out, warn = [], []
    ylim = 9.1 + extra / 2
    zr = {}
    for name, (vs, ts) in bodies.items():
        if re.match(r"cap \(\d+\)$", name):
            out.append(f"el cuerpo de la tecla salio partido: {name}")
        if (k := open_edges((vs, ts))):
            # tras fill_small_holes solo quedan grietas degeneradas (<0.1 mm) que el
            # slicer repara; mas de 12 aristas ya seria un agujero de verdad
            (out if k > 12 else warn).append(f"aviso {name}: {k} aristas abiertas tras reparar")
        xs, ys, zs = zip(*vs)
        if min(xs) < -9.1 or max(xs) > 9.1 or min(ys) < -ylim or max(ys) > ylim \
                or min(zs) < -0.05 or max(zs) > 12:
            out.append(f"{name}: fuera de la huella {[round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)]}")
        zr[name] = (min(zs), max(zs))
    cz = zr.get("cap")
    for name, (lo, hi) in zr.items():
        if name != "cap" and cz and not (lo < cz[1] and hi > cz[0]):
            out.append(f"{name}: flota fuera de la tecla")
    return out, warn


def plate(entries, name):
    """entries: [(stem, (x, y))] -> placa con un objeto de 4 partes + un STL por color."""
    per_color = {}
    for stem, off in entries:
        raw = os.path.join(OUT, "raw", stem + ".3mf")
        bodies = {n: fill_small_holes(m)[0] for n, m in read_3mf(raw).items()}
        for color, mesh in group_by_color(bodies).items():
            per_color.setdefault(color, ([], []))
            per_color[color][0].append(mesh)
            per_color[color][1].append(off)
    parts = {c: merge(m, o) for c, (m, o) in per_color.items()}
    write_3mf(os.path.join(OUT, f"{name}.3mf"), [(name, parts)])
    for color, mesh in parts.items():
        write_stl(os.path.join(OUT, f"{name}.{color}.stl"), mesh)
    return sorted(parts)


PLATE_HALF_GAP = 9.0  # mm extra entre mitades: sitio para Enter (1,5u)


def plate_pos(row, col):
    """Mitad izquierda arriba, mitad derecha debajo: 6 x 8 teclas ~ 126 x 177 mm.
    Enter (1,5u, [3][5]) baja la mitad del hueco extra: 3 mm libres arriba (B) y abajo (P).
    Space (1,5u, [3][6]) no estorba: encima tiene el agujero [2][6] y debajo nada."""
    half, c = (0, col) if col < 6 else (1, col - 6)
    gy = half * 4 + row
    y = (3.5 - gy) * PITCH + (PLATE_HALF_GAP / 2 if half == 0 else -PLATE_HALF_GAP / 2)
    if (row, col) == (3, 5):
        y -= PLATE_HALF_GAP / 2
    return (c - 2.5) * PITCH, y


def safe(s):
    return "".join(ch if ch.isalnum() else "_" for ch in s.encode("ascii", "replace").decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", nargs="*", help="p.ej. r1c4 r3c6")
    ap.add_argument("--probe", action="store_true", help="probeta de holgura del vastago")
    ap.add_argument("--preview", action="store_true", help="captura PNG por tecla (lento)")
    ap.add_argument("--plate-only", action="store_true", help="solo rehacer la placa")
    ap.add_argument("--check", action="store_true", help="solo comprobar las leyendas")
    ap.add_argument("--flat", action="store_true",
                    help="perfil plano: tope horizontal a la misma altura (salida en out_flat/)")
    ap.add_argument("-j", type=int, default=8)
    a = ap.parse_args()
    global OUT, FLAT_MODE
    if a.flat:
        FLAT_MODE = True
        OUT = os.path.join(HERE, "out_flat")

    # las leyendas se comprueban siempre antes de gastar tiempo de CAD
    bad_legends = 0
    for k in ([] if a.probe else all_keys()):
        kid = f"r{k['row']}c{k['col']}"
        if a.keys and kid not in a.keys:
            continue
        lay = layout_legends(k["base"], k["num"], k["sym"])
        probs = check_legends(lay, key_extra(k["row"], k["col"]))
        if a.check:
            desc = "  ".join(f"{b}={i['text']!r}@{i['height']:.1f}+{i['grow']:.2f}" for b, _, i in lay)
            print(("MAL " if probs else "ok  ") + f"{kid:6} {desc}")
        for pr in probs:
            print(f"     {kid}: {pr}")
        bad_legends += bool(probs)
    if a.check:
        print(f"{bad_legends} teclas con problemas de leyenda")
        sys.exit(1 if bad_legends else 0)
    if bad_legends:
        sys.exit("hay leyendas que no se imprimirian bien: corrigelas antes (--check)")

    for d in ("raw", "keys", "stl", "sc", "png", "scripts"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    jobs, layout = [], []
    if a.probe:
        for i, clr in enumerate(PROBE_CLEARANCES):
            stem = f"probe_{i + 1}_clr{int(round(clr * 100)):02d}"
            cmds, _ = cap_script(1, 3, None, None, None, clearance=clr, notches=i + 1)
            jobs.append((cmds, stem, 0.0))
            layout.append((stem, ((i - 1.5) * PITCH, 0.0)))
    else:
        for k in all_keys():
            kid = f"r{k['row']}c{k['col']}"
            if a.keys and kid not in a.keys:
                continue
            cmds, _ = cap_script(k["row"], k["col"], k["base"], k["num"], k["sym"])
            stem = f"{kid}_{safe(k['base'] or '')}"
            jobs.append((cmds, stem, key_extra(k["row"], k["col"])))
            layout.append((stem, plate_pos(k["row"], k["col"])))

    bad = []
    if not a.plate_only:
        with ThreadPoolExecutor(a.j) as ex:
            res = list(ex.map(lambda j: run(j[0], j[1], a.preview, j[2]), jobs))
        bad = [r for r in res if not r[1]]
        for stem, ok, msg in res:
            print(("OK   " if ok else "FAIL ") + stem + ("  (aviso)" if ok and msg else ""))
            if msg:
                print("     " + msg.replace("\n", "\n     "))
        print(f"{len(res) - len(bad)}/{len(res)} teclas")

    done = [e for e in layout if os.path.exists(os.path.join(OUT, "raw", e[0] + ".3mf"))]
    if done and not a.keys:
        name = "plate_probe" if a.probe else "plate_corne"
        colors = plate(done, name)
        print(f"placa: out/{name}.3mf ({len(done)} teclas; partes: {', '.join(colors)})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
