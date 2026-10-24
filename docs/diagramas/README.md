# Diagramas del pipeline

Abrir [index.html](index.html) en el navegador. La página reúne los cuatro
diagramas, los comandos completos y la diferencia entre construir la imagen
Docker y ejecutar una evaluación. No hace falta arrancar la aplicación.

| Vista | HTML interactivo | SVG | PNG |
|---|---|---|---|
| Contenedor, capas, dominio y persistencia | [01_ARQUITECTURA.html](01_ARQUITECTURA.html) | [SVG](exportaciones/01_ARQUITECTURA.svg) | [PNG](exportaciones/01_ARQUITECTURA.png) |
| Solicitud, cola, worker y estados | [02_EVALUACION.html](02_EVALUACION.html) | [SVG](exportaciones/02_EVALUACION.svg) | [PNG](exportaciones/02_EVALUACION.png) |
| Etapas y comandos de síntesis | [03_COMANDOS.html](03_COMANDOS.html) | [SVG](exportaciones/03_COMANDOS.svg) | [PNG](exportaciones/03_COMANDOS.png) |
| Pruebas por componente y familia numérica | [04_PRUEBAS_COMPONENTES.html](04_PRUEBAS_COMPONENTES.html) | [SVG](exportaciones/04_PRUEBAS_COMPONENTES.svg) | [PNG](exportaciones/04_PRUEBAS_COMPONENTES.png) |

## Contenido y alcance

Los gráficos describen la arquitectura de ASIC Area Lab. Se conservaron sus
artefactos y recibos originales: sus etiquetas de formatos, disponibilidad y recursos corresponden al piloto
INT8 previo a la integración de las once DPU. El código actual se documenta
en [DPU_FORMATOS.md](../DPU_FORMATOS.md).
El estado y resultados actualizados están en [VALIDACION.md](../VALIDACION.md).

- Diseño INT8/16 con wrapper, top `INT8_16_DPU_perf_top` y 96 FF esperados.
- Bibliotecas IHP130, Nangate15 y Nangate45 disponibles en el programa actual.
  Para Nangate45 se incorporó el Liberty NLDM typical de texto del nuevo paquete.
- React ejecutándose en el navegador; FastAPI sirve sus archivos compilados.
- Un contenedor con código de API, aplicación, dominio e infraestructura.
- Contratos `ExperimentRepository` y `SynthesisGateway`, con sus adaptadores.
- SQLite embebido, una cola de memoria y un worker de síntesis.
- GHDL → Verilog → Yosys/ABC → comprobaciones → Icarus → reporte.
- Solo área de celdas: sin routing, floorplan, clock tree ni pads.

El primer grafo muestra relaciones de código y datos. Las flechas discontinuas
de contratos indican uso o implementación de interfaces, no tráfico de red.
Los contratos no son procesos adicionales. Las llamadas al repositorio y la
publicación del resultado están explicadas en la segunda vista.

La segunda vista ilustra el recorrido de una evaluación y sus rechazos/fallos.
La interrupción por reinicio es un evento global: se documenta en la tarjeta de
estados y en el índice, en vez de representarse como una etapa normal del cálculo.

La tercera vista sigue las flechas: primera fila de izquierda a derecha,
segunda de derecha a izquierda y tercera de izquierda a derecha. Los comandos
completos están en los bloques desplegables del índice; algunos rótulos del
grafo se abrevian para conservar legibilidad.

Fuentes y enlaces al código: [FUENTES.md](FUENTES.md).

La cuarta vista es una **guía propuesta de ampliación**, no una declaración de
soporte ya implementado. La matriz detallada y los puntos fijados a INT8 están
en [Pruebas por componente y formato](../PRUEBAS_COMPONENTES_FORMATOS.md).

## Interacción y exportación

Los HTML se generaron con **archify**. Incluyen cambio de tema, zoom, búsqueda,
enfoque de nodos, vistas guiadas y exportación a SVG/PNG. El contenido y la
leyenda de los grafos están en español. Los controles y el atributo de idioma
del visor utilizan el fallback inglés del paquete; no se modificó su runtime
para traducirlo.

Los SVG/PNG incluidos son exportaciones estáticas del SVG de los HTML, con
paleta clara y la familia tipográfica del visor. Los PNG se rasterizaron con
`rsvg-convert` y **no son capturas de un navegador**.

## Validación y límites

Los cuatro candidatos pasaron `validate` y `deliver` con el perfil **showcase**:
**9/9 controles, 0 errores y 0 advertencias**. Los recibos registran SHA-256 y
tamaño de la especificación y del HTML final.

- [Recibo de arquitectura](validacion/01_ARQUITECTURA.entrega.json).
- [Recibo del recorrido](validacion/02_EVALUACION.entrega.json).
- [Recibo de comandos](validacion/03_COMANDOS.entrega.json).
- [Recibo de pruebas](validacion/04_PRUEBAS_COMPONENTES.entrega.json).
- [Resumen y hashes](validacion/resumen.json).

El entorno restringe `spawnSync` de Node. Para ejecutar el CLI original de
archify se usó un adaptador temporal que carga sus renderers y checker en
Worker Threads, conservando la validación y entrega atómica del CLI. No se
modificaron los archivos de la skill, sus validadores ni los controles de calidad.
En una terminal normal, `REGENERAR.sh` utiliza el CLI sin ese adaptador.

La inspección automática `visual-check` **falló por restricciones de Chromium**
(`setsockopt`/`shutdown: Operation not permitted`). No se verificaron sus cuatro
viewports, la contención de la página ni los controles de interacción en un
navegador. Los recibos conservan ese resultado como fallo; no se presenta como
una inspección omitida o aprobada.

Sí se inspeccionaron visualmente las exportaciones estáticas para revisar
etiquetas, flechas y superposiciones. Esa revisión no sustituye la inspección
del HTML en navegador.

La generación de gráficos no ejecutó GHDL, Yosys ni Docker y no modificó la
aplicación, el RTL, las bibliotecas o la presentación.

## Archivos editables y regeneración

`especificaciones/` contiene los cuatro JSON. Para regenerar en un entorno con
archify y Node disponibles:

```bash
bash REGENERAR.sh
```

Puede definirse `ARCHIFY_DIR` si la skill está instalada en otra ruta.
La exportación estática utiliza Python estándar; genera PNG si encuentra
`rsvg-convert`. Los PNG existentes se entregan listos para usar.

La comprobación de navegador puede repetirse después de una entrega exitosa:

```bash
node /ruta/archify/bin/archify.mjs visual-check 01_ARQUITECTURA.html --json
```

Documentación ampliada: [pipeline paso a paso](../PIPELINE_PASO_A_PASO.md).

