# -*- coding: utf-8 -*-
"""Lectura/escritura minima de 3MF y STL (sin dependencias).

SolidCraft parte una leyenda en varios cuerpos ("num", "num (1)", ...) cuando sus
glifos quedan separados. Aqui se agrupan por color y se escriben:
  - un 3MF por tecla: un objeto con una parte por color
  - un STL por color
  - la placa completa: un objeto con 4 partes (todas las teclas), lista para el ACE Pro
"""
import re
import struct
import zipfile
import xml.etree.ElementTree as ET

NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
COLOR_ORDER = ["cap", "base", "num", "sym"]  # = filamento 1..4


def read_3mf(path):
    """-> {nombre_de_cuerpo: (vertices[(x,y,z)], triangulos[(a,b,c)])}"""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    out = {}
    for obj in root.iter(f"{{{NS}}}object"):
        mesh = obj.find(f"{{{NS}}}mesh")
        if mesh is None:
            continue
        vs = [(float(v.get("x")), float(v.get("y")), float(v.get("z")))
              for v in mesh.iter(f"{{{NS}}}vertex")]
        ts = [(int(t.get("v1")), int(t.get("v2")), int(t.get("v3")))
              for t in mesh.iter(f"{{{NS}}}triangle")]
        out[obj.get("name")] = (vs, ts)
    return out


def group_by_color(bodies):
    """Une 'num', 'num (1)', ... en una sola malla 'num'. Ignora cuerpos auxiliares."""
    groups = {}
    for name, mesh in bodies.items():
        key = re.sub(r" \(\d+\)$", "", name)
        if key not in COLOR_ORDER:
            raise ValueError(f"cuerpo inesperado en el 3MF: {name!r}")
        groups.setdefault(key, []).append(mesh)
    return {k: merge(v) for k, v in groups.items()}


def open_edges(mesh):
    """Aristas que no comparten exactamente 2 triangulos (0 = malla estanca)."""
    from collections import Counter
    e = Counter()
    for a, b, c in mesh[1]:
        for x, y in ((a, b), (b, c), (c, a)):
            e[(min(x, y), max(x, y))] += 1
    return sum(1 for n in e.values() if n != 2)


def fill_small_holes(mesh, max_loop=16):
    """Cierra agujeros pequenos que deja la teselacion de SolidCraft.

    Sigue las semiaristas de borde (a->b sin su b->a) formando lazos y los rellena en
    abanico con la orientacion contraria. Devuelve (malla, lazos_cerrados, lazos_sin_cerrar).
    """
    vs, ts = mesh
    half = set()
    for a, b, c in ts:
        half.update(((a, b), (b, c), (c, a)))
    nxt = {}
    for a, b in half:
        if (b, a) not in half:
            nxt.setdefault(a, []).append(b)
    if not nxt:
        return mesh, 0, 0
    from collections import Counter
    cnt = Counter()
    for a, b, c in ts:
        for x, y in ((a, b), (b, c), (c, a)):
            cnt[(min(x, y), max(x, y))] += 1
    new, closed, failed = list(ts), 0, 0
    remaining = {(a, b) for a, bs in nxt.items() for b in bs}
    out_of = {}
    for a, b in remaining:
        out_of.setdefault(a, []).append(b)
    while remaining:
        a, b = next(iter(remaining))
        path, pos = [a], {a: 0}
        while True:
            remaining.discard((a, b))
            out_of[a].remove(b)
            if b in pos:  # lazo cerrado: path[pos[b]:]
                j = pos[b]
                loop = path[j:]
                for v in loop[1:]:
                    del pos[v]
                path = path[:j + 1]
                ring = [(min(p, q), max(p, q)) for p, q in zip(loop, loop[1:] + loop[:1])]
                if 3 <= len(loop) <= max_loop and all(cnt[e] == 1 for e in ring):
                    for i in range(1, len(loop) - 1):
                        tri = (loop[0], loop[i + 1], loop[i])
                        new.append(tri)
                        for x, y in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                            cnt[(min(x, y), max(x, y))] += 1
                    closed += 1
                else:
                    failed += 1
                if len(path) == 1 and not out_of.get(b):
                    break
            else:
                pos[b] = len(path)
                path.append(b)
            a = b
            if not out_of.get(a):
                failed += 1  # borde abierto que no cierra
                break
            b = out_of[a][0]
    return (vs, new), closed, failed


def merge(meshes, offsets=None):
    vs, ts = [], []
    for i, (mv, mt) in enumerate(meshes):
        dx, dy = offsets[i] if offsets else (0.0, 0.0)
        base = len(vs)
        vs.extend((x + dx, y + dy, z) for x, y, z in mv)
        ts.extend((a + base, b + base, c + base) for a, b, c in mt)
    return vs, ts


def write_stl(path, mesh):
    vs, ts = mesh
    with open(path, "wb") as f:
        f.write(b"corne-es keycap".ljust(80, b" "))
        f.write(struct.pack("<I", len(ts)))
        for a, b, c in ts:
            p, q, r = vs[a], vs[b], vs[c]
            u = [q[i] - p[i] for i in range(3)]
            v = [r[i] - p[i] for i in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            ln = sum(x * x for x in n) ** 0.5 or 1.0
            f.write(struct.pack("<12fH", *(x / ln for x in n), *p, *q, *r, 0))


def _mesh_xml(vs, ts):
    v = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in vs)
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in ts)
    return f"<mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh>"


def write_3mf(path, objects):
    """objects: [(nombre_objeto, {color: malla})] -> cada objeto con una parte por color.

    Cada parte es un <object> con malla y el objeto final los referencia como
    <components>: PrusaSlicer/OrcaSlicer/Anycubic Slicer Next lo cargan como un
    objeto con varias partes, a las que se asigna filamento.
    """
    res, items, nid = [], [], 1
    for oname, parts in objects:
        comp_ids = []
        for color in COLOR_ORDER:
            if color not in parts:
                continue
            vs, ts = parts[color]
            res.append(f'<object id="{nid}" type="model" name="{color}">{_mesh_xml(vs, ts)}</object>')
            comp_ids.append(nid)
            nid += 1
        comps = "".join(f'<component objectid="{i}"/>' for i in comp_ids)
        res.append(f'<object id="{nid}" type="model" name="{oname}"><components>{comps}</components></object>')
        items.append(f'<item objectid="{nid}"/>')
        nid += 1
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS}">'
             '<metadata name="Application">corne-es-layout/keycaps</metadata>'
             f'<resources>{"".join(res)}</resources><build>{"".join(items)}</build></model>')
    ctypes = ('<?xml version="1.0" encoding="UTF-8"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
              '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
