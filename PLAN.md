# Plan de capas — Corne (Pilot W-CORNE) en español, orientado a desarrollo

Estado: **pendiente de validación**. Nada se ha escrito todavía sobre un `.vil` nuevo.

## 0. Punto de partida (hechos verificados)

| Dato | Valor | Cómo se ha comprobado |
|---|---|---|
| Teclado | `Pilot W-CORNE`, VID `55D4` PID `0461` | `/sys/bus/usb/devices/*/product` |
| Firmware | Vial, protocolo 6 / VIA 9, 8 capas, 32 tap-dance, 32 combos | `spanish_layout.vil` |
| Matriz en el `.vil` | 4 filas × 12 columnas; sin tecla en `[2][6]` y `[3][2]` (46 teclas) | parseo del JSON |
| Layout del SO | **`es`** (Hyprland `kb_layout = es`, `localectl` → X11 Layout `es`) | `~/.config/hypr/input.conf` |
| Compose | `kb_options = compose:caps` → **Bloq. Mayús es la tecla Compose** | mismo fichero |

Consecuencia clave: el firmware envía *posiciones físicas tipo US* y el SO las traduce con
`es`. Por eso todos los símbolos se generan con combinaciones `LSFT(...)` / `RALT(...)`
sobre teclas US, no con "el símbolo" directamente.

## 1. Tabla `es` verificada (de `/usr/share/X11/xkb/symbols/{es,latin,pc}`)

| Tecla QMK | normal | + Shift | + AltGr (`RALT`) |
|---|---|---|---|
| `KC_GRAVE` | º | ª | **\\** |
| `KC_1` … `KC_0` | 1…0 | ! " · $ % & / ( ) = | 1→**\|** 2→**@** 3→**#** 4→**~** 5→½ 6→¬ 7→**{** 8→**[** 9→**]** 0→**}** |
| `KC_MINUS` | ' | ? | **\\** |
| `KC_EQUAL` | ¡ | ¿ | (cedilla muerta) |
| `KC_LBRACKET` | **` (muerta)** | **^ (muerta)** | [ |
| `KC_RBRACKET` | + | * | ] |
| `KC_SCOLON` | **ñ** | Ñ | ~ (muerta) |
| `KC_QUOTE` | **´ (muerta)** | **¨ (muerta)** | { |
| `KC_BSLASH` | ç | Ç | } |
| `KC_COMMA` | , | ; | • |
| `KC_DOT` | . | : | · |
| `KC_SLASH` | **-** | **_** | — |
| `KC_NONUS_BSLASH` | **<** | **>** | \| |

Dos hallazgos que vertebran el diseño:

1. **`RALT(7/8/9/0)` = `{ [ ] }`**. Los cuatro corchetes en la fila numérica, un solo
   modificador, dedos índice→meñique en orden. Es mejor ruta que `AC11`/`BKSL`.
2. **`~` NO es tecla muerta** en Linux/`es`: `RALT(KC_4)` escribe `~` directo.
   (Ojo: `RALT(KC_SCOLON)` sí es tilde muerta — no usar.)
   En cambio **`` ` `` y `^` SÍ son muertas** → hay que pulsar espacio detrás.

## 2. Qué está roto hoy para programar

- **`'` (apóstrofo) está mal colocado**: `[3][10]` es `KC_QUOTE`, que en `es` es la tilde
  aguda muerta (´), no el apóstrofo. El apóstrofo (`KC_MINUS`) solo se alcanza hoy con
  `MO(1)` + la tecla de retroceso. Pasa a la fila base de SYM, bajo el meñique derecho.
- **`/` no está en ninguna capa** (es `LSFT(KC_7)`): rutas, cierres de etiqueta, divisiones.
- **`<` y `>` no existen**: hacen falta `KC_NONUS_BSLASH` / `LSFT(KC_NONUS_BSLASH)`.
- La capa 1 tiene restos de plantilla del fabricante (`KC_D/F/G` sueltos en la fila de
  flechas, `LSFT(KC_9)` duplicado) y las capas 2–7 están vacías.

## 3. Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Mantener `MO(1)` y `MO(2)` donde están | son los pulgares actuales; no se toca la memoria muscular |
| `MO(1)` = **NUM/NAV** (como hoy), `MO(2)` = **SYM** | la capa 1 actual ya es números + flechas |
| `MO(1)`+`MO(2)` = **capa 3** (FN/media/sistema) | `MO(3)` colocado en la posición del otro pulgar dentro de cada capa |
| Mantener `Bloq. Mayús` en `[1][0]` | es la tecla **Compose** del sistema; sustituirla rompería acentos y símbolos raros |
| Mantener `´ ¨` (`KC_QUOTE`) en la base | es *la* tecla del español: á é í ó ú ü. El `'` va a SYM |
| **Sin home-row mods** en v1 | 46 teclas con Shift/Ctrl dedicados; los HRM cuestan semanas de reentreno y fallan al teclear rápido. Queda anotado como posible v2 |
| Fila superior de SYM = fila numérica con Shift (`! " # $ % & / ( ) =`) | mnemotecnia: misma posición que los números de la capa 1 |
| `` ` `` y `^` como teclas muertas (sin macro) en v1 | ver §5 |
| `AltGr` (`KC_RALT`) se mantiene en `[1][6]` de la capa 1 | es la vía de escape para cualquier símbolo `es` que no esté mapeado, y hace de Alt derecho en atajos |
| `RCTRL` se queda en `[0][6]` | es el único Ctrl de la mano derecha: sin él, `Ctrl`+dígito en la capa NUM cae en el mismo dedo. `< >` vive en SYM, que es suficiente |

## 4. Las capas

Ver el diagrama: [`docs/corne-es-layout.svg`](docs/corne-es-layout.svg)
(regenerable con `python3 render_diagram.py`; la fuente de verdad es `spec.py`).

- **Capa 0 · BASE** — QWERTY. `Ñ` en su sitio, `- _` en la posición de `/`, `, ;` y `. :`.
  La tecla interior derecha sigue siendo `RCTRL`; `< >` está en SYM.
- **Capa 1 · NUM/NAV** (pulgar izq.) — números 1–0 arriba; flechas en `HJKL`;
  `Home/PgDn/PgUp/End` debajo; mods (`Super/Alt/Shift/Ctrl`) en la fila base izquierda para
  combinar con las flechas (selección por palabras, etc.); `Undo/Cut/Copy/Paste/Redo` en `ZXCVB`.
- **Capa 2 · SYM** (pulgar der.) — símbolos de programación. Fila base derecha: `{ [ ] }` y `'`;
  fila base izquierda: `\ _ - + *`; interior: `|`; abajo: `` ` `` `^` `<` `>` `~` y `@ : ; ? ¿`.
- **Capa 3 · FN/MEDIA/SYS** (ambos pulgares) — F1–F12, multimedia, brillo, `º ª`, `€`, `ç Ç`,
  `¡ ¿`, `PrtSc` y `QK_BOOT` en la esquina inferior derecha (para flashear).

## 5. Dos cosas que hay que decidir contigo

### (a) Geometría: 7 teclas sin confirmar

El `.vil` describe 46 posiciones, no las 42 de un Corne clásico. Las 30 letras fijan casi
toda la matriz, pero estas 7 posiciones no se pueden deducir del fichero
(aparecen marcadas con `?` y borde discontinuo en el diagrama):

```
[0][6] = RCTRL     [1][6] = RSHIFT        (columna interior derecha)
[3][0] = LALT      [3][1] = TAB           (abajo a la izquierda)
[3][9] = BSPC      [3][10] = ´   [3][11] = SUPR   (abajo a la derecha)
```

No te fíes del dibujo para contestar: la fila de pulgares está dibujada alineada a la
matriz, no a la forma real del cluster. La manera limpia de resolverlo es una de estas dos:

1. **Vial → pestaña «Matrix tester»**: pulsas una tecla física y te marca la celda de la
   matriz que se activa. Con hacerlo sobre esas 7 teclas queda cerrado sin inferencias.
2. **Una foto del teclado**: resuelve de un golpe si son 42 o 46 teclas y cómo es el cluster.

**Pregunta:** ¿puedes pasarme el resultado del matrix tester para esas 7, o una foto?

### (b) Teclas muertas `` ` `` y `^`

El backtick es imprescindible (markdown, shell). Dos opciones:

1. **v1 sin macros**: `` ` `` = `KC_LBRACKET` y `^` = `LSFT(KC_LBRACKET)`, pulsando espacio
   después. Funciona siempre, cuesta una pulsación extra.
2. **Con macro** (` + espacio en una sola tecla): hace falta conocer el formato exacto de
   `macro` en el `.vil` v1. Los 16 slots están vacíos, así que no hay ejemplo del que copiar.
   Si creas **una macro cualquiera en Vial** (dos pulsaciones), la guardas y me pasas el
   fichero, lo deduzco de un diff y lo implemento sin adivinar.

Recomendación: v1 con la opción 1, y la 2 cuando tengamos el ejemplo.

## 6. Implementación (tras la validación)

1. `git commit` del original intacto como baseline.
2. `build_vil.py`: carga `baseline/spanish_layout.original.vil` con `json.load`, sustituye
   **solo** `layout` a partir de `spec.py` y vuelca con `json.dump`. No se reconstruye el
   fichero desde cero: `uid`, `tap_dance`, `combo`, `key_override`, `settings`,
   `encoder_layout`, `layout_options`, protocolos y las 8 capas se conservan tal cual.
3. Test de ida y vuelta: volcar sin cambios debe reproducir exactamente el JSON original.
4. Salida: `corne_es_dev.vil` → se carga en Vial con *Load saved layout*.
5. `README.md` con la chuleta y cómo regenerar.

**Pendiente logístico:** `vial` no está en el `PATH` pero el log dice que lo ejecutaste hoy
(12:12 y 12:23). ¿Cómo lo lanzas — AppImage, Flatpak? Sin eso el `.vil` no sirve de nada.
