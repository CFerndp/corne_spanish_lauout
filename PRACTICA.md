# Cómo aprender este teclado

Lo difícil de un Corne **no son las letras**: siguen siendo QWERTY y las sabes. Lo difícil
son tres cosas, en este orden:

1. **Las columnas rectas.** Tus dedos llevan años moviéndose en diagonal. Esto se corrige
   solo, en 2–3 días, y es lo que más frustra al principio.
2. **Los pulgares.** Pasan de pulsar una tecla (espacio) a pulsar seis y a *mantener* capas.
   Es un músculo nuevo, literalmente.
3. **Los símbolos en la capa SYM.** Es lo único que hay que memorizar de verdad, y lo que
   más tarda: 2–3 semanas hasta que salen sin pensar.

## La regla que más acelera: sin teclado de repuesto

Guarda el otro teclado en un cajón. Alternar entre los dos triplica el tiempo de
adaptación, porque el cerebro mantiene los dos mapas vivos en vez de sustituir uno.

Los días 1 a 3 son malos de verdad (20–30 ppm, frustración alta). A partir del 4 la curva
sube rápido. Si tienes una entrega esa semana, empieza la semana siguiente: el bajón de
productividad es real, dura poco, pero es real.

## Plan por fases

### Fase 1 — días 1–3: solo la capa base

Objetivo: dedos en la fila base y pulgares. **Nada de capas todavía.**

- Imprime el diagrama (`docs/corne-es-layout.png`) y ponlo al lado de la pantalla.
- **No mires el teclado.** Mira el diagrama. Si miras las teclas, aprendes a mirar teclas.
- Sesiones de 15 minutos, dos o tres al día. Mejor que una hora seguida: esto es memoria
  motora, y consolida descansando.
- Texto en castellano normal, con acentos y `ñ`. La tecla `´` (a la derecha del `Super`
  derecho) es la que más se te va a resistir de la base.

### Fase 2 — días 4–7: los pulgares y las capas

Objetivo: que mantener `MO` con el pulgar no te obligue a mover la mano.

Drills concretos, repitiendo la misma secuencia 20 veces hasta que salga sin mirar:

```
Capa NUM:  fechas y números de teléfono; 1024, 3.14, 2026-09-28
Capa SYM:  () => {}    [0]    a.b();    "texto"    /home/user/.config
Capa SYM:  <div></div>    -> =>    !=  ==  &&  ||    #include
Navegación: moverte por un fichero solo con MO(1) y las flechas, sin ratón
```

El de `() => {}` es el que más rendimiento da por minuto invertido.

### Fase 3 — semana 2 en adelante: trabajo real

Ya se aprende programando, no practicando. Pero con una disciplina:

> Cada vez que dudes más de dos segundos, o que un símbolo te salga incómodo, **apúntalo**
> en `notas.md` en vez de aguantarte.

Esas notas son el material de la v2. Un layout se ajusta con datos de uso, no de un tirón
al principio: si `@` te sale mal veinte veces, se mueve; si nunca usas `½`, se quita.

## Herramientas

| Para qué | Qué usar |
|---|---|
| Base, en castellano | [monkeytype](https://monkeytype.com) en español, con *punctuation* y *numbers* activados |
| Letras que fallas más | [keybr](https://keybr.com) — genera texto con tus letras débiles |
| Sin salir de la terminal | `sudo pacman -S ttyper` y luego `ttyper -w 50` |
| Símbolos y código | [typelit.io](https://typelit.io) o, mejor, **reescribe a mano un fichero de tu propio proyecto** |

Lo de reescribir tu propio código no es un truco menor: entrena exactamente la mezcla de
símbolos que tú usas, que no es la de ningún test genérico.

## Expectativas realistas

| Momento | Dónde vas a estar |
|---|---|
| Días 1–3 | 20–30 ppm. Duele. Es normal |
| Final de la semana 1 | ~50–60 % de tu velocidad anterior, la base ya sale sola |
| Semanas 3–4 | recuperas tu velocidad previa |
| A partir de ahí | la superas, porque las manos ya no se mueven del sitio |

Los símbolos van un par de semanas por detrás de las letras. Es lo esperable.

## Dos cosas de tu configuración concreta

- **Los atajos con `Super`**: solo tienes `Super` en el pulgar derecho. Para `Super`+número
  necesitas los dos pulgares a la vez (derecho en `Super`, izquierdo en `MO(1)`) más el
  dedo del dígito. Se puede, pero practícalo aparte el primer día: en Hyprland lo usas
  constantemente.
- **`Ctrl`+dígito** (pestañas del editor y la terminal) va con `Ctrl` interior derecho
  (`[0][6]`, arriba a la derecha) + `MO(1)` con el pulgar izquierdo. Ese es el motivo de que
  ese `Ctrl` siga ahí.

## Ergonomía, que también se aprende

Separa las mitades **al ancho de los hombros** — es la mitad del beneficio de un split y la
gente lo desaprovecha juntándolas. Muñecas rectas, y si puedes inclina las mitades hacia
dentro (*tenting*) con algo debajo del borde interior. Si notas que estiras el meñique para
llegar a algo, esa tecla está mal colocada: anótala.
