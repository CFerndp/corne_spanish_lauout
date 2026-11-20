# Modo juego

Una capa pensada para jugar con **la mano izquierda en el teclado y la derecha en el
ratón**, como en World of Warcraft y la mayoría de juegos de acción o rol. La mano
izquierda queda adaptada al juego y la derecha sigue igual que siempre, para el chat.

## Entrar y salir

**SYM + Esc** activa y desactiva el modo juego, como un interruptor:

1. Mantén **SYM** (pulgar derecho).
2. Pulsa **Esc** (arriba a la izquierda).
3. Suelta las dos. Ya estás en modo juego y no hace falta mantener nada.

Para salir, lo mismo: **SYM + Esc** otra vez.

- **Al desenchufar el teclado vuelve siempre al modo normal.** Si alguna vez no sabes en qué
  modo estás, es la forma segura de volver.
- **Para saber en qué modo estás**, pulsa Bloq Mayús: en modo juego hace de Shift y no
  activa las mayúsculas.

## La mano izquierda

```
 ┌─────┬───┬───┬───┬───┬───┐┌─────┐
 │ Esc │ Q │ W │ E │ R │ T ││ Tab │   columna interior: teclas que se
 ├─────┼───┼───┼───┼───┼───┤├─────┤   pulsan sueltas, así no importa
 │Shift│ A │ S │ D │ F │ G ││Enter│   estirar el índice
 ├─────┼───┼───┼───┼───┼───┤└─────┘
 │ Alt │ Z │ X │ C │ V │ B │
 └─────┴───┴───┴───┴───┴───┘
              ┌────┐┌─────┐┌────┐
              │Ctrl││Space││G-FN│   pulgares
              └────┘└─────┘└────┘
```

| Tecla | Dedo | Para qué |
|---|---|---|
| **Shift**, **Alt** | meñique | modificadores: Shift + 1, Alt + Q… |
| **Ctrl** | pulgar | modificador |
| **Space** | pulgar | saltar |
| **G-FN** | pulgar, el de dentro | mantener para números y F1–F5 |
| **Tab** | índice, estirando | cambiar de objetivo |
| **Enter** | índice, estirando | abrir el chat |

Los tres modificadores quedan en posiciones de reposo, así que cualquier combinación
modificador + habilidad sale sin mover la mano.

## G-FN: números y F1–F5

Mientras mantienes **G-FN**, la mano izquierda cambia a:

```
  ▽   1   2   3   4   5
  ▽  F1  F2  F3  F4  F5      F1–F5: objetivos de grupo en muchos juegos
  ▽   6   7   8   9   0
```

Mientras la mantienes, W, A, S y D dejan de mover al personaje. Usa G-FN para lo que
pulsas de vez en cuando y deja las habilidades de la rotación en las letras.

## La mano derecha

Es la misma que en el modo normal: puedes escribir en el chat sin salir del modo juego.
**SYM** funciona igual, con todos los símbolos.

## Cómo configurar el juego

La idea es que el teclado ponga teclas cómodas y que **las habilidades se asignen dentro
del juego**:

- Asigna las habilidades a las teclas alrededor de W A S D: **Q E R T F G Z X C V**.
- Con **Shift, Ctrl y Alt** cada una da 4 combinaciones: unas 40 habilidades sin estirar la
  mano hacia los números.
- Deja **1–0** (con G-FN) para lo que usas poco: consumibles, monturas, profesiones.

Ejemplo en World of Warcraft: Q E R F como habilidades principales, Shift + Q E R F para la
segunda barra, Ctrl + Q E R F para defensivas, Tab para cambiar de objetivo y G-FN + F1–F5
para seleccionar a los miembros del grupo.

## Limitaciones

- **La capa FN** (F6–F12 y multimedia) no está disponible en modo juego. Sal con SYM + Esc
  si la necesitas.
- **La capa NUM** tampoco: su pulgar es Space en modo juego. Los números están en G-FN.
- **Super** está en el pulgar derecho, lejos de la mano de juego, para no activar atajos del
  sistema por accidente.

## Cómo está hecho

Son tres capas en [`spec.py`](../spec.py): `L4` (GAME), `L5` (GAME-FN) y `L6` (una copia de
SYM). La copia de SYM hace falta por cómo funcionan las capas en QMK; el detalle está en
[`diseno.md`](diseno.md#modo-juego).
