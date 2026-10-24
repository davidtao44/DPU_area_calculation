# Guion y notas de la presentación

53 diapositivas: 37 principales y 16 anexos. Exposición detallada sugerida: 35–45 minutos; usar los anexos para preguntas.

## 01 · Del VHDL al área ASIC: qué medimos y qué podemos demostrar

Esta presentación describe el programa tal como existe al 19 de octubre de 2026. Su objetivo es someter el método y las evidencias a revisión, no defender una certeza absoluta. Se volvió a auditar el archivo conservado de 30 combinaciones, sin ejecutar nuevas síntesis. Los diagramas representan módulos y comandos reales. El argumento defendible es que se obtiene una estimación prelayout de área de celdas de una implementación registrada concreta. La corrección física final, la equivalencia exhaustiva y la precisión matemática de todas las familias siguen fuera de lo demostrado.

Evidencia: Ver auditoría.



## 02 · La base metodológica es defendible; la validación sigue siendo parcial

La auditoría realizada hoy recalcula sumas y hashes de los archivos conservados. No es una nueva ejecución de GHDL o Yosys. Los 30 casos corresponden a diez diseños por tres tecnologías. LNS16 figura en el catálogo, pero no tiene tres reportes completos. Las pruebas ligeras de software pasaron hoy:20 backend y 42 frontend. Es razonable aceptar la metodología como estudio exploratorio de área de celdas, condicionando la publicación de conclusiones fuertes a completar la cadena de artefactos y delimitar la exactitud funcional.

Evidencia: auditoria_evidencias.json · pruebas ligeras 19/10/2026



## 03 · La magnitud de interés es la suma de áreas de las celdas mapeadas

Área de celdas significa sumar las áreas nominales de los tipos de celdas que aparecen en la netlist. Se incluyen los FF del wrapper registrado. Las conexiones lógicas son indispensables para definir el circuito, aunque se excluya el área física de los cables. No se realiza placement ni routing; por tanto no existe evidencia sobre utilización, congestión, die o cierre temporal. El resultado se refiere a esta netlist bajo esta biblioteca y esta política de mapeo, no al menor circuito posible ni al tamaño final de un chip.

Evidencia: infrastructure/liberty.py · summarize_netlist()

[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F06] Berkeley ABC: optimización y mapeo — https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm

## 04 · El objeto medido son once DPU registradas ya existentes

Los perfiles se obtuvieron del subproyecto DPU_Performance_Area_Comparison. No son nuevas arquitecturas inventadas para la presentación. Cada top tiene su wrapper original y anchos concretos. DPU designa aquí cuatro productos y acumulación, con las particularidades de cada implementación. La aplicación actual no integra octets ni TCU completas. La descripción de la jerarquía más amplia del repositorio no debe confundirse con el alcance realmente ejecutable.

Evidencia: infrastructure/designs.py · assets/manifest.json



## 05 · El wrapper establece la frontera de área y la latencia observable

En INT8/16 hay ocho operandos de 8 bits y un acumulador de 16 bits registrados:80 bits de entrada. Se añade un registro de salida de 16 bits, para96 bits declarados. La lógica de la DPU se conserva. Los valores de 96 FF en INT8 y192 FF en INT16 son controles estrictos del perfil; otras familias permiten optimizaciones de bits no observables, siempre que quede estado y pase la comparación funcional. Dos flancos permiten capturar entradas y después la salida correspondiente, sin que ello imponga una frecuencia realizable.

Evidencia: assets/rtl/int8_16/INT8_16_DPU_perf_top.vhd · validation.py



## 06 · Diseño y tecnología se eligen antes de crear el trabajo

El usuario selecciona un design_id que ya determina formato, top, anchos, archivos y biblioteca VHDL. No se cambia un parámetro de formato dentro del mismo hardware después de sintetizar. El technology_id selecciona un Liberty específico. La API acepta únicamente IDs enumerados y rechaza campos arbitrarios; por tanto el navegador no envía un comando de shell ni una ruta para ejecutar. La solicitud crea un UUID y devuelve202. Los resultados llegan por consulta posterior.

Evidencia: ExperimentForm.tsx · api/schemas.py · ExperimentService.submit()

[F13] FastAPI: API y validación de solicitudes — https://fastapi.tiangolo.com/
[F14] React: interfaz basada en componentes — https://react.dev/learn

## 07 · Las tres bibliotecas activas corresponden a condiciones typical

Se contrastaron el catálogo, el manifiesto de assets y los campos nominales de cada archivo. Los tres snapshots son copias idénticas a los originales por SHA-256. En IHP se usa1.20V; la otra biblioteca typical de 1.50V no es la seleccionada. Nangate45 usa el paquete base, Front_End/Liberty/NLDM, no Low_Power ni un binario .db. Las condiciones nominales son distintas entre nodos: same typical no significa mismo proceso ni misma tensión física.

Evidencia: infrastructure/catalog.py · scripts/prepare_assets.py

[F08] IHP SG13G2: proceso real de 130 nm y estado del PDK abierto — https://github.com/IHP-GmbH/IHP-Open-PDK, https://ihp-open-pdk-docs.readthedocs.io/en/main/process_specs/process_specs.html
[F09] Nangate45 / FreePDK45: tecnología genérica predictiva — https://eda.ncsu.edu/freepdk/freepdk45/
[F10] Nangate15 / FreePDK15: kit predictivo FinFET de investigación — https://eda.ncsu.edu/freepdk15/, https://arxiv.org/abs/2009.04600, https://doi.org/10.1145/2717764.2717783, https://www.researchgate.net/publication/274254091_Open_Cell_Library_in_15nm_FreePDK_Technology

## 08 · Un proceso real y un kit predictivo sostienen conclusiones distintas

La fuente de una biblioteca importa tanto como su nodo. IHP130 está vinculado al proceso SG13G2, pero el PDK abierto se publica como preview y el programa no hace un tape-out. FreePDK45 y FreePDK15 son plataformas genéricas predictivas de investigación, apropiadas para estudiar implementaciones bajo esas reglas y celdas. No son una promesa de área de un proceso comercial arbitrario llamado45 o15nm. El nombre de nodo tampoco permite extrapolar por el cuadrado de la longitud.

Evidencia: Ver auditoría.

[F08] IHP SG13G2: proceso real de 130 nm y estado del PDK abierto — https://github.com/IHP-GmbH/IHP-Open-PDK, https://ihp-open-pdk-docs.readthedocs.io/en/main/process_specs/process_specs.html
[F09] Nangate45 / FreePDK45: tecnología genérica predictiva — https://eda.ncsu.edu/freepdk/freepdk45/
[F10] Nangate15 / FreePDK15: kit predictivo FinFET de investigación — https://eda.ncsu.edu/freepdk15/, https://arxiv.org/abs/2009.04600, https://doi.org/10.1145/2717764.2717783, https://www.researchgate.net/publication/274254091_Open_Cell_Library_in_15nm_FreePDK_Technology

## 09 · El inventario suministrado es mayor que el catálogo habilitado

El Excel elaborado previamente separa33 combinaciones habilitadas de 121propuestas. Existen14Liberty NLDM base: seisIHP, cincoNangate45 y tresNangate15. Solo tres son los snapshots activos. Los otros once requieren crear perfiles y revisar simulación y mapeo. Hay53 archivos .lib de inventario, excluyendo metadatos Apple. CCS/ECSM y Low_Power se listan, pero no se cuentan automáticamente como estudios físicos independientes ni se mezclan con el paquete base.

Evidencia: docs/experimentos/Plan_experimentos_DPU_ASIC_2026-10-19.xlsx



## 10 · La aplicación separa decisiones de dominio de herramientas externas

ExperimentService depende de dos protocolos del dominio: ExperimentRepository y SynthesisGateway. Los adaptadores concretos SQLiteExperimentRepository y Ghdl YosysSynthesis implementan esas fronteras. create_app es la raíz de composición. FastAPI expone el caso de uso; React consume contratos JSON; el dominio no importa FastAPI ni SQLite. El adaptador de síntesis orquesta herramientas y recoge reportes. Esta separación mejora la trazabilidad y permite probar fallos con un gateway simulado, pero por sí sola no demuestra la validez científica del área.

Evidencia: domain/ports.py · application/services.py · main.py



## 11 · Un solo contenedor reúne API, frontend compilado y herramientas EDA

La construcción tiene tres etapas: Node compila React/Vite; una etapa descarga la suite EDA fijada y verifica su SHA; el runtime PythonTrixie recibe ambos resultados. FastAPI sirve el frontend de producción. SQLite está embebido y no hay un servidor PostgreSQL adicional. El volumen /app/data conserva la base y las carpetas runs. Vite no es un servicio extra de producción. El acceso a Docker quedó bloqueado en esta sesión; no se usa la existencia del Dockerfile como evidencia de un build reciente exitoso.

Evidencia: Dockerfile · compose.yaml · main.py

[F12] OSS CAD Suite: distribución de herramientas EDA — https://github.com/YosysHQ/oss-cad-suite-build
[F15] Vite: desarrollo y empaquetado del frontend — https://vite.dev/guide/
[F16] SQLite: persistencia embebida — https://sqlite.org/serverless.html
[F17] Docker y Compose: empaquetado y ejecución reproducible — https://docs.docker.com/get-started/docker-overview/

## 12 · El trabajo avanza por estados y publica el área al terminar los controles

La cola admite cuatro pendientes y un worker ejecuta trabajos mediante asyncio.to_thread, de modo que las herramientas no bloquean el loop HTTP. Los estados de progreso van de preparing a reporting. Un error genera failed y conserva el diagnóstico. Al reiniciar, los registros queued o running se marcan interrupted y no se reanudan automáticamente. La API de CSV exige succeeded. Las pruebas de aceptación de API usan un gateway falso para probar el flujo de estados; no se cuentan como síntesis reales.

Evidencia: ExperimentService.work() / _execute() · sqlite_repository.py · api/routes.py



## 13 · Una ejecución conecta entradas, referencia RTL, mapeo y reporte

Este diagrama resume una ejecución real. Se elige perfil y Liberty, se copian y registran entradas, y GHDL simula el RTL para producir la referencia. Luego se convierte a Verilog, se sintetiza y mapea en Yosys, y se obtiene la netlist. Se comprueban conteos y áreas con Liberty y stat antes de simular la netlist contra la referencia RTL. Solo después se publica el reporte. La flecha de referencia es un flujo de datos adicional, no otra fase de síntesis. Cualquier fallo detiene la publicación de área válida. Las fuentes y dependencias son locales a un UUID; no se sustituye ningún resultado faltante por una estimación inventada.

Evidencia: GhdlYosysSynthesis.run() · validation.py · liberty.py

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html
[F02] Yosys: síntesis genérica y mapeo tecnológico — https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html, https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html
[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F07] Icarus Verilog y vvp: simulación de la netlist — https://steveicarus.github.io/iverilog/usage/getting_started.html

## 14 · El perfil del diseño evita seleccionar archivos o anchos a mano

El perfil contiene todos los parámetros variables que el adaptador necesita. El mismo registro también gobierna la preparación de assets, reduciendo el riesgo de divergencia. Estos son campos reales del perfil INT8, resumidos para la diapositiva. source_files se mantiene ordenado y relativo a assets. Un design_id también define su referencia funcional. No hay un selector libre de nombres de entidad, ni se infiere el formato por analizar un archivo con un patrón genérico.

Evidencia: infrastructure/designs.py · domain/models.py



## 15 · Cada ejecución conserva la identidad de sus entradas

prepare_assets copia bytes del subrepositorio y Liberty originales sin reescribirlos. El manifiesto de assets incluye commit y hashes; el propio manifiesto advierte que el commit no sustituye al hash si hay cambios locales. Cada run vuelve a copiar los archivos a sources y el Liberty a cells.lib. El manifiesto del experimento añade versiones y hashes de estímulos y resultados. Un SHA identifica bytes y detecta diferencias con una referencia retenida; no constituye firma de una tercera parte ni prueba de que nadie haya modificado toda la cadena.

Evidencia: prepare_assets.py · synthesis.py · manifest.json



## 16 · GHDL analiza las dependencias y el wrapper en bibliotecas separadas

GHDL es una herramienta de análisis, elaboración y simulación VHDL que también ofrece síntesis. En este programa es un ejecutable, no una librería Python ni un servidor aparte. El adaptador ejecuta el análisis de fuentes en la biblioteca del perfil y el wrapper en work, de acuerdo con sus declaraciones library/use. Las opciones std=08, fsynopsys y fexplicit son las realmente usadas para este RTL. Una mala dependencia falla antes de medir área. La conversión de síntesis es otra llamada posterior.

Evidencia: infrastructure/vhdl.py · synthesis.py

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html

## 17 · Posit16 y Posit32 requieren resolver helpers duplicados sin alterar su RTL

El backend LLVM de GHDL genera objetos por archivo. Los archivos FloPoCo de suma y multiplicación repiten helpers, lo que producía símbolos duplicados al enlazar la simulación nativa. La infraestructura usa el parser ghdl --chop para separar unidades. Si dos unidades con el mismo nombre son idénticas byte a byte, se conserva una copia; si difieren, se falla. No se usa una opción de linker que oculte conflictos y los snapshots originales se conservan. Las seis ejecuciones Posit16/32 completas documentan esta política y sus unidades derivadas.

Evidencia: infrastructure/vhdl.py · compilation/*.vhdl · manifiestos Posit16/32



## 18 · El RTL produce la referencia y los enteros tienen un oráculo adicional

write_vectors genera 256 estímulos con semilla 20261005. Se incluyen extremos, signos, actividad por lane y palabras aleatorias. GHDL debe producir 256 resultados definidos. Para INT8 e INT16 Python comprueba además un producto punto con signo, reducido módulo 2^bits(R). Para FXP, FP, Posit y LNS, el esperado sale del RTL suministrado: la prueba verifica preservación del comportamiento, no demuestra que la aritmética original coincida con una matemática ideal. Los formatos no se reinterpretan usando floats de Python.

Evidencia: validation.py · write_vectors() / check_rtl_results()



## 19 · Dos flancos por estímulo respetan el wrapper registrado

El testbench asigna los operandos, genera un primer flanco para capturar entradas y un segundo para registrar el resultado. Después rechaza salidas indefinidas y las escribe como hexadecimal. Los pequeños waits garantizan el orden de eventos de simulación; no son una restricción de síntesis y no demuestran que la lógica alcance 50 MHz. La simulación mapped utiliza la misma secuencia lógica de flancos, pero no hay SDF ni modelos de retardos de celda.

Evidencia: validation.py · VHDL_TESTBENCH / VERILOG_TESTBENCH

[F07] Icarus Verilog y vvp: simulación de la netlist — https://steveicarus.github.io/iverilog/usage/getting_started.html

## 20 · GHDL genera Verilog para que Yosys pueda sintetizar el diseño

El programa usa el frontend standalone de GHDL. No invoca un plugin de GHDL dentro de Yosys. --synth elabora el top y --out=verilog escribe design.v. La documentación de GHDL declara experimental su motor de síntesis; por eso la conversión no se acepta solo porque terminó con código 0. La netlist final se compara con el RTL mediante simulación. No se calcula área en esta fase y el tamaño de design.v en disco no se usa como área física.

Evidencia: synthesis.py · fase converting

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html

## 21 · El script de Yosys hace explícita la política de síntesis y mapeo

Este fragmento reproduce el script generado para INT8. read_liberty -lib declara tipos de celdas como cajas negras para el mapeo; synth aplana y sintetiza, posponiendo ABC mediante -noabc. Después se mapean los FF y la lógica con la misma biblioteca. Se retira únicamente scopeinfo, un metadato, no hardware desconocido. check -assert añade un control estructural y write_json/write_verilog guardan la implementación. stat usa el mismo Liberty. No hay objetivo de frecuencia, lectura SDC, PnR o comando formal.

Evidencia: synthesis.py · synth.ys

[F02] Yosys: síntesis genérica y mapeo tecnológico — https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html, https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html
[F03] Yosys: lectura de Liberty y modelos de simulación — https://yosyshq.readthedocs.io/projects/yosys/en/0.41/cmd/read_liberty.html
[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F05] Yosys: comprobaciones estructurales — https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html

## 22 · dfflibmap y ABC eligen celdas tecnológicas para funciones diferentes

Yosys transforma el diseño en operadores y lógica genérica. dfflibmap resuelve los elementos secuenciales soportados por la biblioteca, con las inversiones o lógica que resulten necesarias. ABC realiza optimización y mapeo combinacional dentro de Yosys; no es un servicio separado del sistema. La biblioteca fija qué puertas y tamaños de drive están disponibles. El resultado depende de heurísticas y del catálogo; la ausencia de un objetivo temporal explícito no demuestra un óptimo global de área.

Evidencia: synth.ys · logs de ABC en run.log.gz

[F02] Yosys: síntesis genérica y mapeo tecnológico — https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html, https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html
[F06] Berkeley ABC: optimización y mapeo — https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm

## 23 · El cálculo de área puede reconstruirse celda por celda

El ejemplo usa el reporte real INT8/16 con Nangate45. Cada fila representa un tipo de celda con su multiplicidad y su área de biblioteca. Los restantes tipos combinacionales se agrupan solo para legibilidad de la diapositiva; el reporte CSV conserva cada tipo. Los 96 DFF_X1 aportan 434.112 unidades de área. Al sumar todas las instancias se obtiene 7578.872, igual a stat -liberty. La unidad física se respalda con el databook original, que etiqueta um2; el estándar Liberty no impone una unidad universal para todos los paquetes.

Evidencia: int8_16/nangate45/report.json · stat.json · cells.lib

[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F11] Unidades geométricas: documentación primaria y evidencia suministrada — https://ihp-open-pdk-docs.readthedocs.io/en/latest/layout_rules/01_general.html, https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef

## 24 · La clasificación distingue lógica, FF, latches y macros por semántica

El lector local elimina comentarios preservando cadenas y recorre los bloques cell. Exige area finita no negativa y nombres únicos. La categoría se obtiene por grupos ff/ff_bank, latch/latch_bank y memory; no por reconocer letras en el nombre de una celda. El resumen cuenta tipos del módulo top aplanado, rechaza memorias sin mapear y tipos que no aparecen en Liberty. Los tres catálogos concretos han sido revisados; este parser acotado no se presenta como un parser universal de todo Liberty posible.

Evidencia: infrastructure/liberty.py · read_cells() / summarize_netlist()



## 25 · La netlist se contrasta con el RTL usando modelos del mismo Liberty

Yosys importa funciones del Liberty sin-lib y genera cells_sim.v. Las opcionesignore_miss permiten omitir definiciones no soportadas del catálogo; si una celda utilizada falta o no elabora correctamente, Icarus o la comparación debe fallar. El mismo conjunto de vectores se usa contra mapped.v y se exige igualdad de cuatro estados mediante!==. Se comprueba además el marcador de 256 casos. Esta simulación es funcional sin SDF; los retrasos del testbench no caracterizan caminos de silicio.

Evidencia: validation.py · validate_mapped() · simulation_cells.ys

[F03] Yosys: lectura de Liberty y modelos de simulación — https://yosyshq.readthedocs.io/projects/yosys/en/0.41/cmd/read_liberty.html
[F07] Icarus Verilog y vvp: simulación de la netlist — https://steveicarus.github.io/iverilog/usage/getting_started.html

## 26 · La confianza surge de controles complementarios, con límites distintos

No existe un único control que convierta todos los datos en verdad física. La identidad de bytes conecta una corrida con sus entradas. La cuenta por tipos conecta su área con el catálogo. La comparación con stat reduce errores del adaptador, pero ambas cuentas comparten la caracterización física de Liberty. La simulación limita regresiones en los casos recorridos. El oráculo entero añade independencia respecto al propio RTL. Formal, STA y PnR aportarían otros niveles, que este sistema no ha ejecutado.

Evidencia: auditar_evidencias.py · synthesis.py · validation.py

[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F05] Yosys: comprobaciones estructurales — https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html
[F18] EQY: equivalencia formal como verificación adicional — https://yosyshq.readthedocs.io/projects/eqy/en/latest/

## 27 · El reporte conserva datos de cálculo y datos de procedencia

La salida JSON integra áreas, conteos, tecnología, formato y validación junto al manifiesto. El CSV expone las filas por tipo de celda. SQLite conserva el estado y el reporte del experimento; la carpeta del run conserva fuentes, scripts y netlists. El ZIP de la aplicación reúne esos archivos y las fuentes anidadas, incluidas las unidades derivadasPosit. Los datos de validación histórica guardados en docs no se insertan automáticamente como trabajos ficticios en la base.

Evidencia: synthesis.py · api/routes.py · sqlite_repository.py

[F16] SQLite: persistencia embebida — https://sqlite.org/serverless.html

## 28 · La comparación de la interfaz aplica filtros concretos

ComparisonPanel ofrece dos modos. En tecnología filtra el design_id elegido y toma la última evaluación exitosa por technology_id. En formatos filtra una tecnología y toma la última exitosa por design_id. Se ordena por fecha, no por orden accidental de la lista. Actualmente no agrupa por hashes de script o biblioteca; para series futuras con versiones diferentes se debe comprobar la cohorte antes de comparar. La vista no simula datos ni precarga resultados. La lista de API devuelve los últimos100experimentos, lo que también limita el historial visible.

Evidencia: ComparisonPanel.tsx · contracts.ts · repository.list(limit=100)

[F14] React: interfaz basada en componentes — https://react.dev/learn

## 29 · La evidencia completa alcanza 30 de las 33 combinaciones planeadas

La matriz se construye leyendo qué report.json existen en el archivo, no asignando estados por conveniencia. Cada verde dispone de reportes, manifiesto, stat, vectores y dos marcadores de validación en un log. LNS16 no tiene esos tres reportes finales y se muestra como pendiente, sin área0ni valor interpolado. Son7680ejecuciones de vectores documentadas en RTL y otras 7680enmapped; las tecnologías comparten conjuntos de estímulos por diseño y no deben venderse como7680muestras aleatorias independientes.

Evidencia: docs/validation/dpu-matrix-20261018/ · auditoria_evidencias.json



## 30 · El ejemplo INT8 muestra valores existentes y su fuente verificable

El gráfico contiene exclusivamente los tres reportes almacenados de INT8/16. Las cifras se cargan del archivo auditado, no se escriben a mano como resultados. Todos incluyen96 FF, el mismo RTL y la política indicada, pero catálogos, tensiones y tecnología son diferentes. La diferencia no permite concluir que la razón de áreas siga la leycuadrática del nodo ni que rindan igual. El valor es el área nominal total de celdas de la implementación mapeada.

Evidencia: int8_16/{ihp130,nangate45,nangate15}/report.json

[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html

## 31 · Dentro de Nangate45, el formato cambia la implementación y el área

Esta gráfica usa los diez reportesNangate45completos. La tecnología queda fija para facilitar la lectura de diferencias entre implementaciones. Sin embargo los anchos, cantidad de registros, aritmética y redondeo no son iguales. No se afirma que la menor área represente mejor precisión o eficiencia de una aplicación. LNS16 se omite del gráfico de valores porque no tiene un reporte final; su ausencia se explicita en lugar de fabricar un resultado.

Evidencia: auditoria_evidencias.json · casos nangate45



## 32 · La auditoría volvió a comprobar el archivo sin ejecutar EDA

auditar_evidencias.py recorre únicamente artefactos guardados y los inputs actuales. Verifica hashes de originales y snapshots, identidad de manifiestos, perfiles, conteos de tipos contra stat, unidades derivadas Posit, hashes y vinculación de vectores. Recalcula las áreas con Decimal desde los tres Liberty y verifica salidas enteras. El máximo desacuerdo contable observado al recalcular es0bajo esta serialización. Las 20 pruebas backend y 42 frontend se ejecutaron hoy; las 30integracionesEDA pertenecen al archivo anterior, no a nuevas corridas.

Evidencia: auditar_evidencias.py · auditoria_evidencias.json/.csv · pytest/vitest 19/10



## 33 · El archivo compacto permite auditar cuentas, pero no repetir toda la simulación

Tras el episodio de presión de memoria se compactaron los temporales para liberar recursos. Se conservaron reportes, scripts, entradas de prueba, resultados y logs; no se conservaron mapped.v, mapped.json, design.v ni cells_sim.v de esas30 corridas. Por ello hoy se cruza el desglose del reporte con stat y la biblioteca, pero no se vuelve a contar desde mapped.json ni se ejecuta la netlist. La aplicación sí está diseñada para incluir netlists en el ZIP al final de un run; para una publicación se debe retener ese paquete completo.

Evidencia: Inventario real de docs/validation/dpu-matrix-20261018/



## 34 · LNS16 expuso un límite de recursos del entorno de pruebas

LNS16 contiene tablas de corrección que aumentan la carga de conversión y optimización. Los ensayos locales coincidieron con presión de RAM y swap y fueron detenidos. El runner limita tiempo y mata el grupo al excederlo, pero no impone un límite de memoria al proceso local. Compose declara4 GB,2 CPUy128 PIDs para el contenedor; esos límites no se aplicaban a los ensayos ejecutados directamente en la máquina. No se debe afirmar que aumentar timeout soluciona el problema ni que4 GB bastan paraLNS. No se asignan resultados a sus tres casos pendientes.

Evidencia: process_runner.py · Settings · compose.yaml · lns16-incomplete/



## 35 · La calidad del método depende de cerrar cuatro brechas concretas

La revisión encontró una base coherente y límites que conviene tratar como acciones, no como notas escondidas. Primero, retener artefactos completos y un digest de código, imagen y script por corrida; el manifiesto actual no guarda todo eso. Segundo, cerrar la cobertura pendiente de LNS sin volver a saturar la máquina. Tercero, separar preservación de RTLde exactitud matemática y desarrollar un oráculo independiente si se quiere hacer esa afirmación sobre otras familias. Cuarto, agrupar comparaciones por hashes y política además deID. Formal oSTAson trabajos adicionales solo si las preguntas de investigación requieren ese alcance.

Evidencia: Hallazgos de la auditoría de código y evidencias



## 36 · La conclusión debe nombrar implementación, biblioteca y nivel de prueba

Una formulación rigurosa es: para la DPU y wrapper concretos, con snapshots y condiciones identificados, este flujo produjo una implementación mapeada cuyo área nominal de celdas es la suma auditada de sus instancias. Se documentó preservación funcional para256 estímulos y una referencia modular independiente en los perfiles enteros. No debe decirse que se demostró área final del chip, mínimo global, equivalencia exhaustiva, frecuencia objetivo ni precisión numérica independiente de todas las familias. El valor de la presentación es permitir a un revisor aceptar o refutar cada eslabón con evidencia.

Evidencia: Código auditado + 30 paquetes de evidencia

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html
[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F06] Berkeley ABC: optimización y mapeo — https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm
[F18] EQY: equivalencia formal como verificación adicional — https://yosyshq.readthedocs.io/projects/eqy/en/latest/

## 37 · La revisión necesita decisiones sobre evidencia y alcance

Estas preguntas llevan a decisiones técnicas concretas. El grupo puede aprobar el alcance de celdas y wrappers, decidir si la caracterizaciónpredictiva es suficiente para el objetivo académico y definir el estándar de conservación de artefactos. También debe decidir si quiere comparar solo área o añadir precisión, potencia o frecuencia, lo que requeriría otros controles y experimentos. Las propuestas adicionales delExcel no se habilitan ni ejecutan por presentar esta diapositiva.

Evidencia: Ver auditoría.



## 38 · Anexo A · El mapa de archivos conecta cada afirmación con su implementación

Las rutas son relativas a asic-area-lab. Estos archivos conectan las decisiones de selección, ejecución, validación y representación. Se pueden abrir durante la reunión para revisar una cifra concreta. Los hashes del código guardados en auditoria_evidencias.json identifican la versión inspeccionada hoy. No son un digest de aplicación capturado cuando se ejecutaron las síntesis anteriores.

Evidencia: backend/src/area_lab/ · frontend/src/



## 39 · Anexo B · Los comandos de simulación RTL quedan registrados

El testbench se analiza en work e instancia el wrapper. La opción -e elabora y enlaza el ejecutable de simulación con el backend LLVM; por eso se requieren compilador C, linker y zlib de desarrollo. La ejecución -r falla ante aserciones. --ieee-asserts=disable-at-0 suprime avisos IEEE de inicialización; no desactiva los controles de las salidas muestreadas. Python comprueba además cantidad y definición de resultados.

Evidencia: validation.py · validate_rtl()

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html

## 40 · Anexo C · La memoria y los registros tienen una política explícita

Los perfiles miden DPU combinacionales con wrappers registrados. LNS16 incluye tablas ROM de corrección que se reducen a lógica. No se utiliza una macro SRAM ni una memoria comercial. El resumen rechaza memorias sin mapear, macros y latches inesperados. Si se decide estudiar macros, se necesitarán biblioteca, modelo funcional y política de mapeo específicos. Los bits de registros declarados no siempre equivalen a FF mapeados: una optimización puede eliminar estado no observable.

Evidencia: synthesis.py · memory_policy · summarize_netlist()



## 41 · Anexo D · Las API permiten seguir y auditar un experimento

La API valida UUID y busca los artefactos en la carpeta de ese experimento. El log HTTP expone como máximo los últimos 100 KB; el ZIP conserva el log completo. El CSV exige estado succeeded. El ZIP rechaza trabajos queued o running, pero admite diagnósticos de trabajos fallidos. Una cola llena devuelve 429; solicitudes fuera del contrato se rechazan antes de ejecutar comandos. El estado health=ok acredita respuesta HTTP, no una prueba del circuito.

Evidencia: api/routes.py · main.py



## 42 · Anexo E · Tabla trazable de áreas documentadas

Las cifras se cargan de los reportes auditados. Se conservan seis decimales para identificar los valores serializados, no para afirmar esa exactitud física. Cada valor tiene reporte, stat y log. Los corners tienen condiciones nominales propias y la política de mapeo indicada. La convención de unidades de las bibliotecas se documenta en las fuentes. LNS16 permanece pendiente: no se usa cero ni una interpolación para llenar esa fila.

Evidencia: auditoria_evidencias.csv · tabla generada desde report.json

[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F11] Unidades geométricas: documentación primaria y evidencia suministrada — https://ihp-open-pdk-docs.readthedocs.io/en/latest/layout_rules/01_general.html, https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef

## 43 · Anexo F · Release fijada no significa imagen completamente identificada

El Dockerfile fija OSS CAD Suite 2026-09-04 y el SHA-256 del archivo descargado. Esto ayuda a repetir las herramientas, pero no captura por sí solo el entorno completo. El manifiesto histórico aún no contiene digest final de imagen, hash integral del código y hash de cada script. Las imágenes base se referencian por etiqueta. Se deben preservar los identificadores completos de las versiones de desarrollo, sin sustituirlos por una versión estable actual.

Evidencia: Dockerfile · manifest.tool_versions · auditoria_evidencias.json

[F12] OSS CAD Suite: distribución de herramientas EDA — https://github.com/YosysHQ/oss-cad-suite-build
[F17] Docker y Compose: empaquetado y ejecución reproducible — https://docs.docker.com/get-started/docker-overview/

## 44 · Anexo G · La comprobación del build detecta fallos reales del toolchain

El runtime incluye build-essential y zlib1g-dev porque GHDL LLVM necesita cc y el enlace -lz. Trixie proporciona la versión de glibc que necesita el runtime de la suite fijada. El build ejecuta check_toolchain.py como usuario sin root y comprueba análisis, elaboración, simulación y conversión de un circuito pequeño. Puede detectar una instalación rota aunque --version funcione. No sustituye simular cada DPU ni garantiza memoria suficiente para LNS16.

Evidencia: Dockerfile · scripts/check_toolchain.py



## 45 · Anexo H · Cómo repetir la auditoría sin sintetizar

La auditoría lee únicamente artefactos guardados y recalcula hashes, asociaciones de vectores y áreas. No abre un servidor ni una cola de trabajos. Las pruebas nonintegration usan gateways simulados o funciones pequeñas; se excluyen las integraciones que invocan herramientas EDA. Las pruebas frontend verifican contratos y filtros de presentación. Hoy pasaron 20 pruebas backend y 42 frontend, además de la auditoría estática de los 30 paquetes completos.

Evidencia: auditar_evidencias.py · backend/tests · frontend/src/**/*.test.*



## 46 · Anexo I · El backend coordina y persiste; las herramientas EDA calculan

Python implementa los casos de uso, la ejecución de procesos y la cuenta de área. Uvicorn es el servidor ASGI que aloja FastAPI; no es un motor de síntesis. FastAPI y Pydantic validan las solicitudes y estructuran las respuestas. SQLite conserva trabajos y reportes dentro del proceso, con modo WAL y una conexión por operación. Docker empaqueta el entorno y Compose declara recursos y volumen. La validez del dato de área depende de los adaptadores EDA y del cálculo auditado, no de elegir un framework web concreto.

Evidencia: Dockerfile · main.py · api/schemas.py · hooks.ts · shared/api.ts

[F19] Python: orquestación y procesos externos — https://docs.python.org/3.12/library/subprocess.html
[F20] Pydantic: contratos de datos de la API — https://pydantic.dev/docs/validation/latest/concepts/models/
[F21] Uvicorn: servidor ASGI — https://github.com/Kludex/uvicorn
[F13] FastAPI: API y validación de solicitudes — https://fastapi.tiangolo.com/
[F16] SQLite: persistencia embebida — https://sqlite.org/serverless.html
[F17] Docker y Compose: empaquetado y ejecución reproducible — https://docs.docker.com/get-started/docker-overview/

## 47 · Anexo J · El frontend valida contratos y representa reportes reales

React construye la interfaz por componentes. TypeScript comprueba tipos durante desarrollo y construcción; no valida por sí solo JSON que llega por red. Zod comprueba los contratos de respuesta en ejecución antes de representarlos. TanStack Query gestiona consultas, estados y caché; el código refresca experimentos cada1500ms cuando hay trabajo activo, y cada5000ms en caso contrario. Vite compila archivos estáticos de producción que sirve FastAPI. Ninguna de estas piezas calcula área de puertas ni acredita corrección del circuito.

Evidencia: Dockerfile · main.py · api/schemas.py · hooks.ts · shared/api.ts

[F14] React: interfaz basada en componentes — https://react.dev/learn
[F15] Vite: desarrollo y empaquetado del frontend — https://vite.dev/guide/
[F22] TypeScript: comprobación estática del frontend — https://www.typescriptlang.org/docs/handbook/intro.html
[F23] Zod: validación de datos en ejecución — https://zod.dev/
[F24] TanStack Query: datos remotos, caché y sondeo — https://tanstack.com/query/latest/docs/framework/react/overview, https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults

## 48 · Anexo K · Referencias oficiales del procesamiento de hardware · 1

Las fuentes describen capacidades y límites de las herramientas, no prueban que todas esas capacidades se hayan ejecutado. Los comandos concretos y sus versiones están en cada manifiesto y log. FUENTES_VERIFICADAS.md conserva autor, fecha de consulta, enlaces y límite de cada afirmación. No se atribuyen pruebas formales a la aplicación por tener herramientas que podrían realizarlas.

Evidencia: Ver auditoría.

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html
[F02] Yosys: síntesis genérica y mapeo tecnológico — https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html, https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html
[F03] Yosys: lectura de Liberty y modelos de simulación — https://yosyshq.readthedocs.io/projects/yosys/en/0.41/cmd/read_liberty.html
[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F05] Yosys: comprobaciones estructurales — https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html
[F06] Berkeley ABC: optimización y mapeo — https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm
[F07] Icarus Verilog y vvp: simulación de la netlist — https://steveicarus.github.io/iverilog/usage/getting_started.html
[F18] EQY: equivalencia formal como verificación adicional — https://yosyshq.readthedocs.io/projects/eqy/en/latest/

## 49 · Anexo K · Referencias oficiales del procesamiento de hardware · 2

Las fuentes describen capacidades y límites de las herramientas, no prueban que todas esas capacidades se hayan ejecutado. Los comandos concretos y sus versiones están en cada manifiesto y log. FUENTES_VERIFICADAS.md conserva autor, fecha de consulta, enlaces y límite de cada afirmación. No se atribuyen pruebas formales a la aplicación por tener herramientas que podrían realizarlas.

Evidencia: Ver auditoría.

[F01] GHDL: análisis, elaboración y síntesis — https://ghdl.github.io/ghdl/using/Synthesis.html
[F02] Yosys: síntesis genérica y mapeo tecnológico — https://yosyshq.readthedocs.io/projects/yosys/en/v0.54/cmd/synth.html, https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html
[F03] Yosys: lectura de Liberty y modelos de simulación — https://yosyshq.readthedocs.io/projects/yosys/en/0.41/cmd/read_liberty.html
[F04] Yosys: estadística de área — https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html
[F05] Yosys: comprobaciones estructurales — https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html
[F06] Berkeley ABC: optimización y mapeo — https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm
[F07] Icarus Verilog y vvp: simulación de la netlist — https://steveicarus.github.io/iverilog/usage/getting_started.html
[F18] EQY: equivalencia formal como verificación adicional — https://yosyshq.readthedocs.io/projects/eqy/en/latest/

## 50 · Anexo L · Referencias de tecnología y plataforma · 1

Las fuentes primarias distinguen proceso fabricado y kit predictivo. Las referencias de plataforma describen API, interfaz, empaquetado y persistencia; no calculan el área. El README suministrado de Nangate15 cita el artículo de Martins y el databook de Nangate45 etiqueta áreas en um2. El documento de fuentes explica el respaldo de unidades y los límites de correspondencia entre versiones.

Evidencia: Ver auditoría.

[F08] IHP SG13G2: proceso real de 130 nm y estado del PDK abierto — https://github.com/IHP-GmbH/IHP-Open-PDK, https://ihp-open-pdk-docs.readthedocs.io/en/main/process_specs/process_specs.html
[F09] Nangate45 / FreePDK45: tecnología genérica predictiva — https://eda.ncsu.edu/freepdk/freepdk45/
[F10] Nangate15 / FreePDK15: kit predictivo FinFET de investigación — https://eda.ncsu.edu/freepdk15/, https://arxiv.org/abs/2009.04600, https://doi.org/10.1145/2717764.2717783, https://www.researchgate.net/publication/274254091_Open_Cell_Library_in_15nm_FreePDK_Technology
[F11] Unidades geométricas: documentación primaria y evidencia suministrada — https://ihp-open-pdk-docs.readthedocs.io/en/latest/layout_rules/01_general.html, https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef
[F12] OSS CAD Suite: distribución de herramientas EDA — https://github.com/YosysHQ/oss-cad-suite-build
[F13] FastAPI: API y validación de solicitudes — https://fastapi.tiangolo.com/
[F14] React: interfaz basada en componentes — https://react.dev/learn
[F15] Vite: desarrollo y empaquetado del frontend — https://vite.dev/guide/
[F16] SQLite: persistencia embebida — https://sqlite.org/serverless.html
[F17] Docker y Compose: empaquetado y ejecución reproducible — https://docs.docker.com/get-started/docker-overview/

## 51 · Anexo L · Referencias de tecnología y plataforma · 2

Las fuentes primarias distinguen proceso fabricado y kit predictivo. Las referencias de plataforma describen API, interfaz, empaquetado y persistencia; no calculan el área. El README suministrado de Nangate15 cita el artículo de Martins y el databook de Nangate45 etiqueta áreas en um2. El documento de fuentes explica el respaldo de unidades y los límites de correspondencia entre versiones.

Evidencia: Ver auditoría.

[F08] IHP SG13G2: proceso real de 130 nm y estado del PDK abierto — https://github.com/IHP-GmbH/IHP-Open-PDK, https://ihp-open-pdk-docs.readthedocs.io/en/main/process_specs/process_specs.html
[F09] Nangate45 / FreePDK45: tecnología genérica predictiva — https://eda.ncsu.edu/freepdk/freepdk45/
[F10] Nangate15 / FreePDK15: kit predictivo FinFET de investigación — https://eda.ncsu.edu/freepdk15/, https://arxiv.org/abs/2009.04600, https://doi.org/10.1145/2717764.2717783, https://www.researchgate.net/publication/274254091_Open_Cell_Library_in_15nm_FreePDK_Technology
[F11] Unidades geométricas: documentación primaria y evidencia suministrada — https://ihp-open-pdk-docs.readthedocs.io/en/latest/layout_rules/01_general.html, https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef
[F12] OSS CAD Suite: distribución de herramientas EDA — https://github.com/YosysHQ/oss-cad-suite-build
[F13] FastAPI: API y validación de solicitudes — https://fastapi.tiangolo.com/
[F14] React: interfaz basada en componentes — https://react.dev/learn
[F15] Vite: desarrollo y empaquetado del frontend — https://vite.dev/guide/
[F16] SQLite: persistencia embebida — https://sqlite.org/serverless.html
[F17] Docker y Compose: empaquetado y ejecución reproducible — https://docs.docker.com/get-started/docker-overview/

## 52 · Anexo M · Fuentes de lenguajes, servidor y validadores · 1

Estas referencias oficiales respaldan las funciones de las tecnologías auxiliares. Se distingue validación de tipos y contratos de la validación funcional del hardware. Los archivos de dependencias del proyecto identifican las versiones instaladas; esta bibliografía describe las capacidades de cada proyecto, no demuestra una ejecución de síntesis.

Evidencia: Ver auditoría.

[F19] Python: orquestación y procesos externos — https://docs.python.org/3.12/library/subprocess.html
[F20] Pydantic: contratos de datos de la API — https://pydantic.dev/docs/validation/latest/concepts/models/
[F21] Uvicorn: servidor ASGI — https://github.com/Kludex/uvicorn
[F22] TypeScript: comprobación estática del frontend — https://www.typescriptlang.org/docs/handbook/intro.html
[F23] Zod: validación de datos en ejecución — https://zod.dev/
[F24] TanStack Query: datos remotos, caché y sondeo — https://tanstack.com/query/latest/docs/framework/react/overview, https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults

## 53 · Anexo M · Fuentes de lenguajes, servidor y validadores · 2

Estas referencias oficiales respaldan las funciones de las tecnologías auxiliares. Se distingue validación de tipos y contratos de la validación funcional del hardware. Los archivos de dependencias del proyecto identifican las versiones instaladas; esta bibliografía describe las capacidades de cada proyecto, no demuestra una ejecución de síntesis.

Evidencia: Ver auditoría.

[F19] Python: orquestación y procesos externos — https://docs.python.org/3.12/library/subprocess.html
[F20] Pydantic: contratos de datos de la API — https://pydantic.dev/docs/validation/latest/concepts/models/
[F21] Uvicorn: servidor ASGI — https://github.com/Kludex/uvicorn
[F22] TypeScript: comprobación estática del frontend — https://www.typescriptlang.org/docs/handbook/intro.html
[F23] Zod: validación de datos en ejecución — https://zod.dev/
[F24] TanStack Query: datos remotos, caché y sondeo — https://tanstack.com/query/latest/docs/framework/react/overview, https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults
