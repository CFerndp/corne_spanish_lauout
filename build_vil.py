# -*- coding: utf-8 -*-
"""Genera corne_es_dev.vil parcheando el .vil original.

No se reconstruye el fichero: se carga el original, se sustituye unicamente
`layout` y se vuelca. Asi `uid`, `tap_dance`, `combo`, `key_override`,
`settings`, `encoder_layout`, `layout_options` y los protocolos sobreviven
exactamente igual.
"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from spec import LAYERS, HOLE

BASE = os.path.join(HERE, "baseline", "spanish_layout.original.vil")
OUT = os.path.join(HERE, "corne_es_dev.vil")

# Keycodes que ya aparecen en el fichero original: soporte garantizado.
def known_codes(data):
    seen = set()
    for layer in data["layout"]:
        for row in layer:
            for kc in row:
                if isinstance(kc, str):
                    seen.add(kc)
    return seen


def main():
    raw = open(BASE, encoding="utf-8").read()
    base = json.loads(raw)

    # 1. Ida y vuelta: volcar sin tocar nada debe reproducir el original byte a byte.
    assert json.dumps(base) == raw.strip(), "el volcado no reproduce el original"

    new = copy.deepcopy(base)
    safe = known_codes(base)
    novel = set()

    for li, (name, _note, grid) in enumerate(LAYERS):
        assert len(grid) == 4 and all(len(r) == 12 for r in grid), name
        for r, row in enumerate(grid):
            for c, (code, _label) in enumerate(row):
                orig = base["layout"][li][r][c]
                if (code, _label) == HOLE:
                    # posicion sin tecla fisica: tiene que serlo tambien en el original
                    assert orig == -1, f"capa {li} [{r}][{c}]: HOLE sobre tecla real"
                    new["layout"][li][r][c] = -1
                else:
                    assert orig != -1, f"capa {li} [{r}][{c}]: tecla sobre posicion vacia"
                    new["layout"][li][r][c] = code
                    if code not in safe:
                        novel.add(code)

    # 2. Estructura intacta salvo `layout`.
    for k in base:
        if k != "layout":
            assert new[k] == base[k], f"campo alterado: {k}"
    assert len(new["layout"]) == len(base["layout"]) == 8
    for li in range(8):
        for r in range(4):
            for c in range(12):
                a, b = new["layout"][li][r][c], base["layout"][li][r][c]
                assert (a == -1) == (b == -1), f"agujero movido en [{li}][{r}][{c}]"

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(new, f)

    print(f"escrito {OUT}")
    print(f"capas modificadas: {len(LAYERS)} de 8 (5-8 se quedan transparentes)")
    if novel:
        print("\nkeycodes que no estaban en el original (revisar en Vial que se "
              "muestren bien al cargar):")
        for kc in sorted(novel):
            print("  -", kc)


if __name__ == "__main__":
    main()
