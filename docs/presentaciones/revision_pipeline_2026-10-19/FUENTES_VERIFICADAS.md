# Fuentes primarias verificadas para la revisión de ASIC Area Lab

Fecha de consulta de **todas** las referencias: **19 de octubre de 2026**. Se abrieron las páginas indicadas mediante navegación web. Los enlaces de documentación con una versión fija describen esos comandos; **no identifican la versión realmente instalada**, que debe obtenerse del manifiesto de cada experimento. Las fichas distinguen capacidad documentada, interpretación metodológica y evidencia local pendiente de auditoría.

Este documento no contiene resultados de síntesis nuevos. No se ejecutaron herramientas EDA, compilaciones ni contenedores para esta investigación. La documentación externa respalda el método; los archivos locales deben respaldar cada resultado concreto.

## Referencias para el procesamiento de hardware

### [F01] GHDL: análisis, elaboración y síntesis

- **Título:** GHDL — Synthesis.
- **Autor institucional:** proyecto GHDL.
- **URL:** <https://ghdl.github.io/ghdl/using/Synthesis.html>.
- **Respalda:** `--synth` elabora para síntesis y `--out=verilog` genera una netlist Verilog. GHDL documenta su núcleo de síntesis como experimental y el resultado como entrada no optimizada para otras herramientas.
- **Límite:** convertir VHDL a Verilog no calcula por sí solo el área de celdas de una tecnología ni certifica equivalencia exhaustiva.
- **Aplicación a revisar localmente:** llamadas `ghdl -a`, `-e`, `-r` y `--synth`; no confundir el ejecutable usado con el plugin de Yosys, que es otra integración posible.

### [F02] Yosys: síntesis genérica y mapeo tecnológico

- **Título:** Yosys — synth; Technology mapping.
- **Autor institucional:** YosysHQ.
- **URLs:** <https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html> y <https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html>.
- **Respalda:** `-flatten` aplana; `-noabc` pospone ABC; `dfflibmap` mapea estado y `abc -liberty` lógica.
- **Límite:** síntesis lógica no equivale a implementación física.

### [F03] Yosys: lectura de Liberty y modelos de simulación

- **Título:** read_liberty — read cells from liberty file.
- **Autor institucional:** YosysHQ.
- **URL:** <https://yosyshq.readthedocs.io/projects/yosys/en/0.41/cmd/read_liberty.html>.
- **Respalda:** `-lib` importa cajas negras; omitirlo permite importar funciones.
- **Límite:** ignorar funciones ausentes exige comprobar las celdas realmente usadas.

### [F04] Yosys: estadística de área

- **Título:** stat — print some statistics.
- **Autor institucional:** YosysHQ.
- **URL:** <https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html>.
- **Respalda:** `stat -liberty` utiliza áreas de esa biblioteca; `-json` produce estadística estructurada.
- **Límite:** no mide área de interconexión ni die.

### [F05] Yosys: comprobaciones estructurales

- **Título:** check — check for obvious problems in the design.
- **Autor institucional:** YosysHQ.
- **URL:** <https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html>.
- **Respalda:** detecta bucles, drivers incompatibles y señales sin driver; `-assert` falla ante problemas.
- **Límite:** no prueba equivalencia funcional.

### [F06] Berkeley ABC: optimización y mapeo

- **Título:** ABC: A System for Sequential Synthesis and Verification.
- **Autor institucional:** Berkeley Verification and Synthesis Research Center; Berkeley Logic Synthesis and Verification Group.
- **URL:** <https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm>.
- **Respalda:** ABC representa y transforma lógica, realiza mapeo a celdas y describe recuperación/minimización heurística de área.
- **Límite:** no afirmar mínimo global de área. Tener funciones de verificación disponibles no significa que una invocación de mapeo las haya ejecutado.
- **Aplicación a revisar localmente:** script de ABC generado por Yosys, biblioteca objetivo y versión del binario; no inferir que se usó el flujo completo de ABC independiente.

### [F07] Icarus Verilog y vvp: simulación de la netlist

- **Título:** Getting Started With Icarus Verilog.
- **Autor institucional:** proyecto Icarus Verilog.
- **URL:** <https://steveicarus.github.io/iverilog/usage/getting_started.html>.
- **Respalda:** `iverilog` compila el diseño y `vvp` ejecuta la simulación compilada.
- **Límite:** una simulación recorre los estímulos suministrados. El hecho de usar Icarus no demuestra cobertura exhaustiva, precisión aritmética independiente ni cumplimiento temporal.
- **Aplicación a revisar localmente:** para describir la simulación como funcional sin retardos caracterizados, confirmar que los modelos generados y la invocación no incorporan SDF ni arcos temporales. Esta conclusión depende del código local, no solamente del nombre del simulador.

## Referencias para las bibliotecas de tecnología

### [F08] IHP SG13G2: proceso real de 130 nm y estado del PDK abierto

- **Título:** IHP Open Source PDK — README; Process Specifications.
- **Autor institucional:** IHP GmbH.
- **URLs:** <https://github.com/IHP-GmbH/IHP-Open-PDK> y <https://ihp-open-pdk-docs.readthedocs.io/en/main/process_specs/process_specs.html>.
- **Respalda:** SG13G2 incorpora CMOS de 0,13 µm en una tecnología BiCMOS; el README distingue proceso con diseños fabricados y publicación abierta en estado preview. Describe lógica digital de 1,2 V.
- **Límite:** origen en un proceso real no convierte una estimación de celdas en medición de silicio, tape-out verificado o PDK abierto certificado para producción.
- **Aplicación a revisar localmente:** el archivo `sg13g2_stdcell` seleccionado, su corner, `nom_voltage`, `nom_temperature` y hash. El nominal del archivo concreto prevalece sobre una descripción general.

### [F09] Nangate45 / FreePDK45: tecnología genérica predictiva

- **Título:** FreePDK45 — recursos y FreePDK45 Manual.
- **Autor institucional:** North Carolina State University, EDA.
- **URL:** <https://eda.ncsu.edu/freepdk/freepdk45/>.
- **Respalda:** NCSU relaciona Nangate con FreePDK45 v1.3. El manual describe tecnología genérica de 45 nm basada en publicaciones, modelos predictivos y escalado de reglas.
- **Límite:** no corresponde a una biblioteca de una fundición comercial concreta ni implica área medida tras fabricación.
- **Aplicación a revisar localmente:** emplear el Liberty textual y la distribución cuyo README declare esa procedencia. Los nombres similares y la extensión `.lib` no bastan para identificar un archivo válido.

### [F10] Nangate15 / FreePDK15: kit predictivo FinFET de investigación

- **Título:** FreePDK15; Development of a Predictive Process Design kit for 15-nm FinFETs: FreePDK15.
- **Autores:** NCSU EDA; Kirti Bhanushali, Chinmay Tembe y W. Rhett Davis, arXiv:2009.04600, 2020.
- **URLs:** <https://eda.ncsu.edu/freepdk15/> y <https://arxiv.org/abs/2009.04600>.
- **Respalda:** NCSU enlaza la biblioteca Nangate15 y el artículo de sus autores caracteriza FreePDK15 como kit predictivo para investigación y universidades.
- **Límite:** no afirmar equivalencia con un nodo comercial llamado 15 nm; tampoco derivar razones de área solamente de 130/45/15.
- **Aplicación a revisar localmente:** confirmar que el `.lib` anexado pertenece a esa distribución y documentar la arquitectura, celda y condiciones que efectivamente se usaron.
- **Publicación original de la biblioteca:** M. Martins, J. M. Matos, R. P. Ribas, A. Reis, G. Schlinker, L. Rech y J. Michelsen, *Open Cell Library in 15nm FreePDK Technology*, ISPD 2015, pp. 171–178, DOI <https://doi.org/10.1145/2717764.2717783>. El editor ACM no permitió acceso directo en esta consulta. Sí se consultó la copia subida por los autores en <https://www.researchgate.net/publication/274254091_Open_Cell_Library_in_15nm_FreePDK_Technology>. Su sección 5, tabla 2, etiqueta explícitamente **Cell Area (µm²)** para 15 nm OCL y 45 nm OCL, ambas typical, con 0,8 V y 1,1 V respectivamente. Esto respalda la convención de la familia 15 nm OCL; **los resultados del benchmark del artículo no son resultados de este proyecto**.

### [F11] Unidades geométricas: documentación primaria y evidencia suministrada

- **Título:** IHP SG13G2 — Layout Rules, General.
- **Autor institucional:** IHP GmbH.
- **URL:** <https://ihp-open-pdk-docs.readthedocs.io/en/latest/layout_rules/01_general.html>.
- **Respalda:** las dimensiones de layout de IHP se expresan en micrómetros.
- **Límite:** esa afirmación dimensional no define una unidad universal para el atributo `area` de cualquier Liberty. Se necesita comprobar la convención de cada biblioteca.
- **Evidencia primaria local identificada:** el databook suministrado de Nangate45 etiqueta sus perfiles de área como `um2`: `syn_libraries/NangateOpenCellLibrary_PDKv1_3_v2010_12/Front_End/Doc/Databook/Profilings/prof_area_NangateOpenCellLibrary_typical_typical.html`.
- **Nangate15:** la tabla 2 de Martins et al. [F10] aporta evidencia primaria explícita de área de celdas en µm² para esta familia. El `Readme.txt` suministrado en `syn_libraries/15nm/` cita precisamente ese artículo. La identidad de la familia está respaldada; no se obtuvo una declaración de unidad dentro del Liberty particular ni su LEF original para comprobar cada celda.
- **Corroboración geométrica IHP:** LEF oficial de la misma familia: <https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef>. `sg13g2_a21oi_2` declara `SIZE 3.84 BY 3.78`; el Liberty suministrado `syn_libraries/130nm/lib/sg13g2_stdcell_typ_1p20V_25C.lib`, línea 2278, declara `area : 14.5152`. Su producto es 14,5152, coincidente con el PDF local de ese mismo corner. La documentación dimensional IHP de arriba establece µm. Es corroboración física de una celda, **no auditoría completa de todas las geometrías ni identidad de versiones del PDK**.

## Referencias para la plataforma de ejecución

### [F12] OSS CAD Suite: distribución de herramientas EDA

- **Título:** OSS CAD Suite — README.
- **Autor institucional:** YosysHQ.
- **URL:** <https://github.com/YosysHQ/oss-cad-suite-build>.
- **Respalda:** distribución binaria que incluye herramientas de síntesis, simulación y verificación; lista Yosys, ABC, GHDL e Icarus, entre otras.
- **Límite:** estar incluido no implica estar invocado. La disponibilidad de herramientas formales y PnR no significa que este pipeline las use.
- **Aplicación a revisar localmente:** fecha de release y SHA256 del paquete fijados en Dockerfile; versiones reales del manifiesto. El README actual puede diferir del paquete congelado.

### [F13] FastAPI: API y validación de solicitudes

- **Título:** FastAPI — documentación oficial.
- **Autor institucional:** proyecto FastAPI.
- **URL:** <https://fastapi.tiangolo.com/>.
- **Respalda:** framework Python para APIs, con esquemas, validación de datos y documentación OpenAPI.
- **Límite:** validar IDs o tipos JSON no valida matemáticamente un circuito. Los trabajos de síntesis y su cola son comportamiento implementado por la aplicación.

### [F14] React: interfaz basada en componentes

- **Título:** React — Quick Start.
- **Autor institucional:** equipo React.
- **URL:** <https://react.dev/learn>.
- **Respalda:** construcción de interfaces mediante componentes, propiedades y estado.
- **Límite:** presentar una gráfica correctamente no certifica el cálculo que la alimenta. Revisar el origen del reporte, filtros y selección de experimentos.

### [F15] Vite: desarrollo y empaquetado del frontend

- **Título:** Vite — Getting Started.
- **Autor institucional:** equipo Vite.
- **URL:** <https://vite.dev/guide/>.
- **Respalda:** servidor de desarrollo y comando de construcción que produce recursos para producción.
- **Límite:** no necesita permanecer como servicio dentro del contenedor de producción si otra aplicación sirve sus archivos compilados; esto debe confirmarse en Dockerfile y FastAPI locales.

### [F16] SQLite: persistencia embebida

- **Título:** SQLite Is Serverless.
- **Autor institucional:** proyecto SQLite.
- **URL:** <https://sqlite.org/serverless.html>.
- **Respalda:** SQLite funciona como biblioteca dentro del proceso y no requiere un servidor independiente.
- **Límite:** un archivo de base de datos no preserva por sí solo todos los artefactos de una ejecución. Deben auditarse rutas persistidas, volumen, transacciones y estado de trabajos.

### [F17] Docker y Compose: empaquetado y ejecución reproducible

- **Título:** What is Docker?
- **Autor institucional:** Docker Inc.
- **URL:** <https://docs.docker.com/get-started/docker-overview/>.
- **Respalda:** imágenes y contenedores empaquetan y ejecutan aplicaciones; Compose administra conjuntos de contenedores. La configuración de ejecución también forma parte del contenedor.
- **Límite:** empaquetar mejora la consistencia del entorno; no prueba corrección del RTL, ni garantiza resultados idénticos sin fijar entradas, herramientas y política. Un `Dockerfile` presente no acredita un build reciente exitoso.

## Referencia para distinguir prueba finita y prueba formal

### [F18] EQY: equivalencia formal como verificación adicional

- **Título:** Equivalence Checking with Yosys (EQY) Documentation.
- **Autor institucional:** YosysHQ.
- **URL:** <https://yosyshq.readthedocs.io/projects/eqy/en/latest/>.
- **Respalda:** EQY implementa comprobación formal de equivalencia.
- **Límite:** no atribuir este nivel de prueba al pipeline sin una ejecución acreditada.

## Referencias adicionales del stack de software

Estas piezas transportan, validan u organizan datos; **ninguna calcula por sí misma el área ASIC**. Consulta: 19 de octubre de 2026.

### [F19] Python: orquestación y procesos externos

- **Título y autor:** Python 3.12 — subprocess; Python Software Foundation.
- **URL:** <https://docs.python.org/3.12/library/subprocess.html>.
- **Respalda:** la biblioteca estándar permite iniciar procesos externos, recoger su salida y manejar errores o tiempos máximos. **Límite:** Python ejecuta la lógica programada; su uso no certifica el algoritmo de área ni las herramientas invocadas.

### [F20] Pydantic: contratos de datos de la API

- **Título y autor:** Pydantic Validation — Models; equipo Pydantic.
- **URL:** <https://pydantic.dev/docs/validation/latest/concepts/models/>.
- **Respalda:** los modelos aplican tipos y restricciones a estructuras de datos; pueden convertir entradas según configuración. **Límite:** la validación de esquema no prueba la veracidad física o matemática de los valores aceptados.

### [F21] Uvicorn: servidor ASGI

- **Título y autor:** Uvicorn — README; equipo Uvicorn.
- **URL:** <https://github.com/Kludex/uvicorn> (destino actual de la redirección desde `encode/uvicorn`).
- **Respalda:** servidor ASGI para ejecutar aplicaciones web Python. **Límite:** servir peticiones FastAPI no sintetiza circuitos ni valida reportes; la cola de trabajos y los subprocesos dependen del código de la aplicación. Se verificó el repositorio oficial porque los dominios de documentación no respondieron a la herramienta web.

### [F22] TypeScript: comprobación estática del frontend

- **Título y autor:** The TypeScript Handbook; Microsoft/equipo TypeScript.
- **URL:** <https://www.typescriptlang.org/docs/handbook/intro.html>.
- **Respalda:** añade un sistema de tipos para comprobar programas JavaScript antes de ejecutarlos. **Límite:** los tipos estáticos no validan por sí solos el JSON recibido en ejecución ni la exactitud de un área.

### [F23] Zod: validación de datos en ejecución

- **Título y autor:** Zod — Intro; equipo Zod.
- **URL:** <https://zod.dev/>.
- **Respalda:** biblioteca de esquemas para analizar y validar datos en ejecución, con inferencia de tipos TypeScript. **Límite:** un reporte que cumple el esquema puede contener valores incorrectos; deben contrastarse con los artefactos de síntesis.

### [F24] TanStack Query: datos remotos, caché y sondeo

- **Título y autor:** TanStack Query — Overview; Important Defaults; equipo TanStack.
- **URLs:** <https://tanstack.com/query/latest/docs/framework/react/overview> y <https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults>.
- **Respalda:** administra consulta y caché de datos remotos; `refetchInterval` permite consultas periódicas. **Límite:** sondear estados o reutilizar respuestas no ejecuta síntesis por sí solo, no calcula área ni demuestra que un resultado esté actualizado; hay que revisar claves e invalidación locales.

## Argumento metodológico defendible

Las siguientes son **inferencias metodológicas propias**, cuya aplicación debe comprobarse con código y artefactos locales:

1. **Trazabilidad de entrada:** un hash identifica exactamente la instantánea de RTL y Liberty utilizada. No demuestra que el diseño original sea correcto; impide confundir qué se midió.
2. **Medición definida:** para una netlist mapeada `N`, sumar `area(tipo(c))` para cada instancia `c` proporciona el área de celdas de **esa implementación bajo esa biblioteca**. La descomposición combinacional/secuencial requiere clasificar cada tipo de celda, no deducirla por su nombre.
3. **Comprobación contable:** comparar una suma por instancias con `stat -liberty` detecta errores del reporte. Ambas usan la misma biblioteca/netlist: es un control aritmético parcialmente independiente, no una segunda caracterización física.
4. **Comprobación funcional:** comparar las respuestas originales VHDL con la netlist verifica preservación en los casos ejecutados. Una referencia matemática independiente para INT aporta un control adicional que un oráculo basado en el propio RTL no aporta.
5. **Precisión de la conclusión:** los datos pueden ser reales, reproducibles y apropiados como estimaciones de área de celdas, sin ser mediciones del área final de un chip ni pruebas exhaustivas de corrección.
6. **Comparación:** conservar top, límites de registros, versiones y script hace comparables las ejecuciones. Cambiar tecnología también cambia catálogo, arquitecturas y caracterización de celdas; cambiar formato cambia semántica y anchos. Una gráfica no aísla automáticamente el efecto del nodo o de la precisión numérica.

## Afirmaciones que la presentación debe evitar

- «256 vectores prueban equivalencia formal».
- «El nombre típico hace que los tres procesos tengan las mismas condiciones físicas».
- «15 nm ocupa exactamente `(15/45)^2` del área de 45 nm».
- «El valor de `area` siempre viene definido por Liberty en µm²».
- «ABC garantiza el diseño de menor área posible».
- «No se consideran conexiones, por tanto pueden omitirse los cables lógicos de la netlist». Las conexiones lógicas sí son necesarias; se excluye **su área física**.
- «Tener resultados INT correctos prueba que FP, Posit o LNS tienen exactitud matemática validada».
- «Tener instalado un paquete de herramientas prueba que se ejecutaron todas sus verificaciones».
- «Tres tecnologías integradas implican que todos los corners suministrados ya fueron ejecutados».
