# Diseño del layout

Por qué cada tecla está donde está. La fuente de verdad es [`spec.py`](../spec.py); este
documento explica las decisiones.

## Punto de partida

| Dato | Valor |
|---|---|
| Teclado | Pilot W-CORNE (USB `55D4:0461`), Corne v4.1 de 46 teclas |
| Firmware | Vial (protocolo 6 / VIA 9): 8 capas, 32 tap-dance, 32 combos |
| Matriz en el `.vil` | 4 filas × 12 columnas, sin tecla en `[2][6]` ni `[3][2]` |
| Sistema | Linux con distribución de teclado `es` (xkb) |

**Consecuencia clave:** el firmware envía *posiciones de un teclado US* y el sistema las
traduce con `es`. Por eso todos los símbolos se generan con combinaciones `LSFT(...)` /
`RALT(...)` sobre teclas US, no con "el símbolo" directamente.

### Posiciones físicas

La matriz del `.vil` no coincide con la forma física en la fila de abajo. Confirmado con la
pestaña *Keymap* de Vial:

```
   MITAD IZQUIERDA                             MITAD DERECHA
[0][0] … [0][5]  [3][0]                  [0][6]  [0][7] … [0][11]  [3][9]
[1][0] … [1][5]  [3][1]                  [1][6]  [1][7] … [1][11]  [3][10]
[2][0] … [2][5]                                  [2][7] … [2][11]  [3][11]
            [3][3] [3][4] [3][5]    [3][6] [3][7] [3][8]
```

- `[3][0]` y `[3][1]`: columna interior izquierda, junto a T y G.
- `[0][6]` y `[1][6]`: columna interior derecha, junto a Y y H.
- `[3][9..11]`: columna exterior derecha, bajo el meñique.
- Pulgares: `[3][3..5]` y `[3][6..8]`. Los más interiores (`[3][5]` y `[3][6]`) son de 1,5u.

## Tabla `es` verificada

Sacada de `/usr/share/X11/xkb/symbols/{es,latin,pc}`:

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

Detalles que condicionan el diseño:

- **`~` no es tecla muerta** en Linux con `RALT(KC_4)`. `RALT(KC_SCOLON)` sí lo es: no se usa.
- **`` ` `` y `^` sí son muertas**: hay que pulsar espacio después.
- **Corchetes por las rutas serigrafiadas**: `{ [ ] }` salen con AltGr sobre las teclas
  `´`, `` ` ``, `+` y `ç`, que es lo que trae impreso un teclado español físico. En Linux
  `RALT(7/8/9/0)` hace lo mismo, pero solo las rutas serigrafiadas funcionan también en
  Windows y macOS.

## Decisiones

| Decisión | Motivo |
|---|---|
| NUM (`MO(1)`) y SYM (`MO(2)`) en los pulgares centrales | son las capas que más se usan |
| NUM + SYM a la vez = capa FN | `MO(3)` en la posición del otro pulgar dentro de cada capa |
| Fila superior de SYM = la fila numérica con Shift (`! " # $ % & / ( ) =`) | misma posición que los números de NUM: se aprende sola |
| Bloq Mayús se mantiene | en muchas configuraciones de Linux es también la tecla Compose |
| `´ ¨` en la base | es *la* tecla del español: á é í ó ú ü. El apóstrofo `'` va a SYM |
| Modificadores en `A S D F` de la capa NUM | para combinarlos con las flechas (seleccionar por palabras, etc.) |
| AltGr en la capa NUM | vía de escape para cualquier símbolo de `es` que no esté mapeado |
| Ctrl interior derecho | sin él, Ctrl + dígito (pestañas) cae en el mismo dedo con NUM |
| Sin *home row mods* | 46 teclas dan sitio a Shift y Ctrl propios; los HRM cuestan semanas de adaptación |
| `` ` `` y `^` como teclas muertas, sin macro | funciona siempre, a costa de una pulsación extra |

## Modo juego

Cómo se usa: [`modo-juego.md`](modo-juego.md). Aquí, por qué está hecho así.

- **Capa 4 · GAME**: mano izquierda adaptada al juego, mano derecha igual que BASE.
  Los modificadores van al meñique (Shift, Alt) y al pulgar (Ctrl); Tab y Enter, que se
  pulsan sueltos, a la columna interior, donde estirar el índice no molesta.
- **Capa 5 · GAME-FN**: números y F1–F5 bajo la mano izquierda.
- **Capa 6 · SYM dentro del juego**: copia de SYM. Hace falta porque en QMK manda la capa
  activa de número más alto. GAME (4) queda por encima de SYM (2) y taparía la tecla de
  salida; dentro del juego, el pulgar de SYM lleva a la capa 6, que sí está por encima.
- Se entra y se sale con `TG(4)` en la Esc de las capas 2 y 6 (SYM + Esc). `TG` no se
  guarda: al desenchufar, el teclado vuelve a BASE.

## Cómo se genera el `.vil`

`build_vil.py` carga `baseline/spanish_layout.original.vil`, sustituye **solo** `layout`
con lo que dice `spec.py` y vuelca el JSON. Antes comprueba:

- que volcar el original sin cambios lo reproduce byte a byte;
- que `uid`, `tap_dance`, `combo`, `key_override`, `settings`, `encoder_layout`,
  `layout_options` y los protocolos no cambian;
- que ninguna tecla cae en una posición sin tecla física.
