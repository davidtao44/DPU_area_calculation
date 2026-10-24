# Verificación del ejemplo

Fecha: 5 de octubre de 2026. Se ejecutó el pipeline real sobre copias idénticas
del RTL y Liberty suministrados. No se modificó el RTL del repositorio ni la
presentación.

## Resultados reales del piloto

Top: `INT8_16_DPU_perf_top`. Mapeo de área sin frecuencia objetivo; incluye
registros de entrada y salida. Valores de área bajo la convención µm² de las
bibliotecas utilizadas.

| Biblioteca | Área combinacional | Área secuencial | Área total | Celdas | FF |
|---|---:|---:|---:|---:|---:|
| IHP SG13G2, 130 nm, typical 1,20 V | 63.615,094200 | 4.528,742400 | 68.143,836600 | 6.489 | 96 |
| Nangate FreePDK15, typical 0,80 V | 773,455872 | 122,683392 | 896,139264 | 2.844 | 96 |

En ambos casos:

- El RTL pasó 256 vectores deterministas contra el producto punto firmado
  reducido a 16 bits, incluidos negativos y overflow.
- La netlist mapeada pasó los mismos 256 vectores con iverilog.
- No quedaron operadores genéricos ni celdas sin área.
- Se conservaron 96 FF; no aparecieron latches ni macros.
- La suma de áreas de celdas coincide con `stat -liberty`.
- `$scopeinfo`, metadato de Yosys, se elimina antes del reporte para no contarlo
  como hardware. No se eliminan operadores hardware desconocidos para forzar
  un reporte válido.

Estos valores son **área de celdas post-síntesis**, no área del core ni del chip.
La diferencia entre bibliotecas refleja áreas de sus celdas y decisiones de
mapeo; no se extrapola una ley de escalado por nodo ni un rendimiento temporal.
La implementación FloPoCo se conserva tal como está en el repositorio.

La carpeta `validation/` contiene los JSON/CSV reales, manifiestos y scripts
de síntesis de estas ejecuciones. Son evidencia de validación, no datos
precargados en el historial de la aplicación.

## Herramientas y controles

- OSS CAD Suite 2026-09-04.
- GHDL 7.0.0-dev; Yosys 0.68+182; iverilog del mismo toolchain.
- **12 tests backend aprobados:** 10 de contratos HTTP, errores, cola,
  persistencia y clasificación, más 2 pruebas de integración EDA reales.
- **6 tests frontend aprobados:** selección de biblioteca, envío, estados sin
  resultados y lectura del contrato de ambos reportes reales.
- Ruff, ESLint y TypeScript estricto.
- Compilación de producción con Vite.
- `docker compose config --quiet` valida la definición del único servicio.
- Dependencias Python fijadas en los lockfiles; frontend fijado mediante
  `package-lock.json`. La instalación final npm reportó cero vulnerabilidades.

## Límites de la verificación

Durante la preparación inicial no se pudo construir ni arrancar Docker desde
este entorno. Los resultados de la tabla anterior se obtuvieron localmente.
Posteriormente, al diagnosticar el fallo reportado por el usuario, se pudo
acceder mediante `docker compose exec` a su contenedor en ejecución. La
corrección y el límite de su comprobación se documentan a continuación.

Las pruebas HTTP se ejecutan con transporte ASGI en memoria. El entorno usa
namespaces de red aislados entre llamadas y restringe los avisos por socket
interno de asyncio entre threads. Por ello el harness de tests mantiene un
temporizador y cierra el executor antes de cerrar el loop; el código de la
aplicación no se alteró para ese entorno.

No se afirma inspección visual en un navegador ni una prueba de interacción
completa de navegador. La interfaz tiene pruebas de componentes, validación
de contratos y compilación de producción.

No se ejecutaron equivalencia formal ni STA, placement o routing. En la
verificación inicial faltaba el Liberty de texto de 45 nm; su incorporación y
validación posterior se documentan a continuación.

## Incorporación de Nangate45 — 18 de octubre de 2026

Se incorporó el archivo de texto ASCII suministrado en
`syn_libraries/NangateOpenCellLibrary_PDKv1_3_v2010_12/Front_End/Liberty/NLDM/NangateOpenCellLibrary_typical.lib`.
El README del paquete identifica Nangate 45 nm, FreePDK45 y modelos PTM.
El Liberty declara condiciones typical, 1,10 V y 25 °C, y contiene 134 celdas
con área. La copia `assets/libraries/nangate45/cells.lib` conserva exactamente
sus bytes; origen y SHA-256 están registrados en `assets/manifest.json`.

Se ejecutó localmente el pipeline completo con el mismo RTL, wrapper, política
de mapeo y 256 vectores del piloto. El catálogo habilita `nangate45` y la API
acepta su selección. React utiliza ese catálogo sin un selector adicional.

| Biblioteca | Área combinacional (µm²) | Área secuencial (µm²) | Área total (µm²) | Celdas | FF |
|---|---:|---:|---:|---:|---:|
| Nangate45, typical 1,10 V, 25 °C | 7.144,760 | 434,112 | 7.578,872 | 6.463 | 96 |

El RTL y la netlist mapeada pasaron los 256 vectores. La suma por celda coincide
con `stat -liberty`; no quedaron celdas desconocidas, latches ni macros.
Los 96 FF se mapearon a `DFF_X1`. El reporte conserva todos los hashes y las
versiones de herramientas; no se modificó el RTL original.

Evidencia: [reporte JSON](validation/nangate45-report.json),
[CSV](validation/nangate45-report.csv),
[manifiesto](validation/nangate45-manifest.json),
[script Yosys](validation/nangate45-synth.ys) y
[log completo](validation/nangate45-run.log).
Estos archivos no se insertan como evaluaciones ficticias en SQLite.

También se repitió la integración EDA de IHP130 y Nangate15, obteniendo las
mismas áreas de la tabla inicial. La suite completa aprobó **16 pruebas backend**,
incluidas las tres tecnologías, y **8 pruebas frontend**, incluidas la selección
de 45 nm y la lectura de su reporte real. Pasaron Ruff, ESLint, TypeScript y la
compilación de producción de Vite.

La verificación fue local, con OSS CAD Suite; no se reconstruyó ni arrancó el
contenedor Docker en esta incorporación. Para incluir el nuevo snapshot en una
imagen existente, ejecutar desde la carpeta del programa:

```bash
docker compose up --build -d
```

Se mantiene el alcance de área de celdas de la DPU INT8/16 registrada. Esta
incorporación no generaliza la aplicación a otras DPU, formatos o TCU, ni añade
STA o diseño físico.

## Corrección de GHDL LLVM: `cc not found`

El log de la evaluación `825b1a2f-ced2-42d9-8a6e-f97164020e50` mostró:

```text
ghdl -a --std=08 -fsynopsys -fexplicit --work=int8_16_lib ...
/opt/eda/oss-cad-suite/libexec/ghdl:error: installation problem: cc not found
```

La imagen slim tenía GHDL instalado, pero carecía del compilador C del sistema
que requiere su backend LLVM. El fallo ocurrió durante el análisis inicial,
antes del mapeo ASIC, y no era causado por el RTL ni por el Liberty.

Se añadió `build-essential` a la imagen final del Dockerfile. También se añadió
`scripts/check_toolchain.py` como comprobación obligatoria durante el build:
analiza un circuito VHDL pequeño, elabora y enlaza su testbench, lo simula y
genera Verilog. Se ejecuta después de `USER area-lab` para comprobar el entorno
real del usuario sin root. Si falla, la construcción se detiene.

Se instaló la dependencia en el contenedor que estaba en ejecución. Se solicitó
una nueva evaluación IHP130 (`9958fc5f-59ad-4936-8ccb-2ba706778bd3`), pero el
usuario detuvo el contenedor antes de poder comprobar su resultado final.
Se mantuvo detenido. **No se afirma una evaluación completa aprobada dentro
de ese contenedor ni una reconstrucción Docker verificada en esta corrección.**

La comprobación nueva de GHDL pasó localmente. Hay una prueba de regresión que
reproduce la ausencia de `cc` y otra que ejecuta el análisis, enlace, simulación
y síntesis de prueba con el toolchain disponible.

Para incorporar permanentemente la corrección al contenedor:

```bash
docker compose up --build -d
```

Después se crea otra evaluación desde la interfaz. El trabajo que quedó en
cola o ejecución al detenerse el servicio se marcará interrumpido al arrancar;
no se reanuda automáticamente. No se borra el volumen de resultados.

## Corrección del enlace: zlib y compatibilidad de glibc

La reconstrucción posterior superó `ghdl -a`, pero el usuario reportó durante
`ghdl -e` el error `/usr/bin/ld: cannot find -lz`. Faltaban los archivos de
desarrollo de zlib, proporcionados por `zlib1g-dev`; disponer de una biblioteca
de runtime `libz.so.1` no basta para resolver la opción de enlace `-lz`.

Se auditó el GHDL fijado, en vez de limitar la corrección al mensaje inmediato:

- `ghdl --bind` y `ghdl --list-link` mostraron las opciones `-ldl`, `-lm` y `-lz`.
- `nm` sobre `libgrt.a` mostró la referencia a `__isoc23_strtol` en `fstapi.o`.
- `readelf` sobre el ejecutable de prueba confirmó `__isoc23_strtol@GLIBC_2.38`.

Debian Bookworm proporciona glibc 2.36, insuficiente para ese símbolo. El
runtime del Dockerfile se cambió a `python:3.12-slim-trixie`, que utiliza
glibc 2.41. Las etapas de construcción del frontend y descarga del toolchain
permanecen en Bookworm; solo transfieren archivos a la imagen final.

Se conservó `build-essential` y se añadió `zlib1g-dev`. La comprobación de
construcción ahora compila y ejecuta un programa C pequeño que enlaza zlib y
el símbolo requerido de glibc, antes de analizar, enlazar, simular y sintetizar
el circuito VHDL de prueba. No se deshabilitó la comprobación que detectó el fallo.

La construcción Docker desde este entorno sigue bloqueada por acceso al
daemon. Las comprobaciones locales verifican el script y las dependencias
de enlace, pero **no equivalen a una construcción Docker aprobada**.

Referencias: [zlib1g-dev](https://packages.debian.org/trixie/zlib1g-dev),
[glibc de Trixie](https://packages.debian.org/trixie/libc6) e
[imágenes Python oficiales](https://github.com/docker-library/official-images/blob/master/library/python).
