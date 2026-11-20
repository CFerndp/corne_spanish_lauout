# Anycubic Slicer Next: cómo imprimir los keycaps

Para la **Kobra S1 + ACE Pro con la boquilla de 0,4 de serie**. Los nombres de las opciones
están sacados del código fuente de Anycubic Slicer Next
([github.com/ANYCUBIC-3D/AnycubicSlicerNext](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext),
versión de febrero de 2026) y de su traducción al español; entre paréntesis, el nombre en
inglés. En otras versiones alguno puede variar.

## Configuración probada

Las teclas de prueba (perfil esculpido) se imprimieron bien con el **perfil de serie**
«0.20mm Standard @Anycubic Kobra S1 0.4 nozzle», sin cambiar nada del encaje. Valores de
ese perfil, leídos de su fichero: primera capa 0,2 mm, ancho de línea 0,42, generador de
perímetros **Clásico**, compensación de pata de elefante 0,075, torre de purga activada.

**No cambies lo que afecta al encaje**: compensación de pata de elefante, compensación XY,
ancho de línea, flujo ni generador de perímetros. Las leyendas están calculadas para el
generador Clásico con líneas de 0,42.

## Paso a paso

1. **Modo avanzado.** Muchas opciones solo aparecen con el interruptor **Avanzado**
   (*Advance*) activado, en la cabecera de **Proceso** (*Process*), en el panel izquierdo.
2. **Importar.** Arrastra **los 4 STL de una tecla o de la placa a la vez**. Cuando pregunte
   si quieres cargarlos como **un solo objeto con varias partes**, di que sí.
3. **Filamentos.** En la lista de objetos, asigna a cada parte su filamento:
   `cap` = 1 (cuerpo), `base` = 2 (letra), `num` = 3 (NUM), `sym` = 4 (SYM).
4. **Comprobar** en la vista previa laminada (*Preview*): en las últimas capas tienen que
   verse las tres leyendas completas, cada una en su color.

## Cosas que alargan mucho la impresión

El tiempo de una impresión multicolor lo marcan los **cambios de color**, que se hacen en
cada capa que tiene leyendas.

- **No uses altura de capa variable** (*Variable layer height*) para suavizar la parte de
  arriba: es justo donde están las leyendas. Con capas de 0,08 ahí, una placa pasa de ~100 a
  ~150 cambios de color. En una prueba con dos teclas, la impresión pasó de ~1 h a 5–6 h.
- **Imprime las teclas de prueba de una en una.** Teclas de filas distintas tienen las
  leyendas a alturas distintas y no comparten capas, así que los cambios se suman. En la
  placa completa pasa lo contrario: las 46 teclas comparten las capas.
- Si quieres imprimir mucho más rápido, usa la **variante plana** (ver
  [`README.md`](README.md)): ~12 cambios de color para toda la placa.

## Si hace falta ajustar algo

No han hecho falta en las pruebas, pero estas opciones existen y sirven para esto:

| Problema | Dónde | Qué hacer |
|---|---|---|
| Vetas de otro color en las leyendas claras | botón **Volúmenes de limpieza** (*Flushing volumes*), en la lista de filamentos | sube los valores de las filas que van del cuerpo a ese color |
| Leyendas pequeñas sin contorno | Proceso → Calidad → Perímetros y superficies (*Walls and surfaces*) → **Sólo un perímetro en las capas superiores** (*Only one wall on top surfaces*) | desactivarlo (en el perfil de serie viene activado) |
| Marca de la costura en la cara delantera | Proceso → Calidad → Costura (*Seam*) → **Posición de la costura** (*Seam position*) | **Trasera** (*Back*) |

## Variante plana

Las leyendas están medidas para caer **exactamente en las 3 últimas capas** con capa de
0,12 y primera capa de 0,2. Con otras alturas de capa pueden ocupar una capa más, pero
siguen siendo muy pocas. En la vista previa, los colores de las leyendas deben aparecer
solo en las últimas capas de las teclas.
