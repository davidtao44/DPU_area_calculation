# Revisión técnica del pipeline ASIC Area Lab

Fecha: **19 de octubre de 2026**. Alcance revisado: área de celdas de las DPU
registradas integradas. La revisión no ejecutó nuevas síntesis ni reconstruyó
Docker. Se inspeccionaron el código actual y los artefactos conservados de
ejecuciones anteriores; se ejecutaron únicamente pruebas ligeras de software.

## Dictamen

El método implementado es adecuado para obtener una **estimación prelayout del
área nominal de celdas de una implementación concreta**, con una biblioteca y
política de mapeo identificadas. La cuenta de las 30 combinaciones completas
resultó coherente con los Liberty suministrados y con los `stat.json` guardados.
Los vectores y logs conservados respaldan una validación funcional finita.

Esta conclusión **no equivale a certificar todo el sistema**: faltan los tres
casos LNS16, el archivo compacto no incluye las netlists completas, y no se
ejecutaron equivalencia formal, STA o implementación física. Tampoco se ha
validado con un oráculo matemático independiente la exactitud de FXP, FP,
Posit y LNS. Su referencia es el RTL original.

La sustentación correcta para una reunión o publicación es:

> Se estima el área nominal de las celdas de la DPU y su wrapper registrados,
> sintetizados con la biblioteca y política documentadas. La cuenta se puede
> reconstruir por tipo de celda y se documentó preservación funcional para los
> estímulos ejercitados, con un control matemático adicional para los enteros.

## Qué se comprobó ahora

El script [auditar_evidencias.py](auditar_evidencias.py) es reproducible y no
invoca herramientas EDA. El resultado completo está en
[auditoria_evidencias.json](auditoria_evidencias.json) y
[auditoria_evidencias.csv](auditoria_evidencias.csv).

| Control de esta revisión | Resultado observado |
|---|---|
| Originales y snapshots del manifiesto de assets | 44 archivos coincidentes por SHA-256 |
| Combinaciones completas | 30: diez DPU × tres bibliotecas |
| Perfiles, tecnologías y manifiestos | Compatibles con el catálogo actual; la ausencia histórica de `compilation` se normaliza a `files` |
| Conteos de tipos de celda | Coinciden entre filas del reporte y `stat.json` |
| Área de cada tipo | Coincide con el Liberty seleccionado |
| Suma total y áreas por categoría | Coincidentes; desacuerdo numérico observado: 0 |
| Estímulos, salidas y vectores | 256 por caso; hashes y asociación entrada/salida verificados |
| Oráculo entero recalculado | 1.536 resultados INT8/INT16 correctos bajo reducción modular |
| Logs originales conservados | Dos marcadores `VALIDATION_OK 256` por caso y comandos de conversión, síntesis y simulación |
| Unidades derivadas Posit16/32 | Hashes coincidentes con sus manifiestos |
| Pruebas backend actuales | 20 aprobadas; integraciones EDA excluidas |
| Pruebas frontend actuales | 42 aprobadas, incluidos contratos de los 30 reportes reales |

Los 7.680 vectores RTL y 7.680 mapped mencionados son **ejecuciones
documentadas de estímulos**, no una nueva simulación hoy ni muestras aleatorias
independientes entre tecnologías. Los conjuntos se reutilizan por diseño.

## Cadena de cálculo revisada

1. **Selección controlada.** `designs.py` define top, anchos, wrapper, fuentes,
   biblioteca VHDL, referencia y control de FF. `catalog.py` define el Liberty.
   La API acepta identificadores enumerados; no permite comandos o rutas libres.
2. **Identidad de entradas.** `prepare_assets.py` copia los originales. El run
   captura nuevamente fuentes, Liberty, versiones, política y hashes. El commit
   ayuda a identificar el repositorio, pero los hashes describen los bytes
   concretos incluso si existían cambios locales.
3. **Análisis y simulación VHDL.** GHDL analiza operadores y DPU en su biblioteca
   de perfil, y el wrapper en `work`. El testbench ejerce el circuito registrado
   durante dos flancos por estímulo y rechaza salidas indefinidas.
4. **Control matemático de enteros.** Python calcula el producto punto con signo
   módulo `2^bits(R)`. Para las otras familias, las salidas originales del RTL
   sirven de referencia de preservación, sin sustituir sus reglas por floats
   de software o por una matemática no demostrada.
5. **Conversión.** `ghdl --synth --out=verilog` genera `design.v`. GHDL documenta
   su síntesis como experimental; por eso no se acepta la conversión únicamente
   por su código de salida. Fuente: [GHDL Synthesis](https://ghdl.github.io/ghdl/using/Synthesis.html).
6. **Síntesis y mapeo.** Yosys ejecuta `synth -flatten -noabc`, `dfflibmap` y
   `abc -liberty` con el mismo archivo. No hay frecuencia objetivo ni PnR.
   Se borra solo `$scopeinfo`, metadato de depuración. Los tipos hardware
   desconocidos provocan un fallo; no se eliminan para producir una cifra.
7. **Cuenta de área.** Para cada tipo se calcula `cantidad × area` con Decimal,
   y se suman categorías basadas en grupos semánticos `ff`, `latch` y `memory`.
   Se rechazan memorias pendientes y tipos sin área. Se compara con
   `stat -liberty`. Fuente: [Yosys stat](https://yosyshq.readthedocs.io/projects/yosys/en/v0.50/cmd/stat.html).
8. **Comparación mapeada.** Yosys genera modelos funcionales del mismo Liberty;
   Icarus compila `mapped.v` con esos modelos. Se exige igualdad bit a bit,
   sin aceptar X/Z. No se carga SDF: el resultado no representa una validación
   temporal. Fuente: [Icarus Verilog](https://steveicarus.github.io/iverilog/usage/getting_started.html).
9. **Publicación.** El servicio publica el reporte tras los controles; si falla
   un paso, persiste el diagnóstico. El CSV requiere `succeeded`. La interfaz
   solo compara resultados exitosos y filtra por diseño o tecnología.

`check -assert` es un control estructural, no una prueba funcional. Yosys lo
documenta como detección de problemas evidentes de drivers y bucles.
[Documentación de check](https://yosyshq.readthedocs.io/projects/yosys/en/0.45/cmd/check.html).

## Por qué la cuenta es defendible y qué depende de ella

Para una netlist mapeada fija y una biblioteca fija, sumar el área de cada
instancia es una definición operacional clara de área nominal de celdas. El
resultado no procede de una predicción del modelo de lenguaje, del número de
LUT FPGA, del tamaño de un archivo ni de una regla cuadrática por nodo.

Comparar con `stat` detecta errores de agregación o selección. Ambas cuentas
comparten la biblioteca y la implementación; por ello **no son dos
caracterizaciones físicas independientes**. Si la biblioteca usa una
convención o caracterización inadecuada, ambas pueden compartir esa limitación.

La comparación RTL/netlist añade evidencia sobre preservación del circuito en
los casos ejercitados. Puede compartir errores del RTL original; el oráculo
matemático entero reduce ese riesgo en INT. Ningún conjunto finito aquí
presentado constituye equivalencia formal. [EQY](https://yosyshq.readthedocs.io/projects/eqy/en/latest/)
es una herramienta posible para otro nivel de comprobación; no se ejecutó.

Los hashes prueban identidad respecto a las referencias conservadas. No son
firmas externas, no acreditan por sí solos una ejecución y no impiden una
alteración coordinada de todos los archivos. Logs, scripts, resultados,
entradas y revisión independiente se complementan.

## Bibliotecas y unidades

El programa usa exclusivamente los siguientes typical, a 25 °C:

| Tecnología | Voltaje | Archivo original |
|---|---:|---|
| IHP SG13G2 130 nm | 1,20 V | `130nm/lib/sg13g2_stdcell_typ_1p20V_25C.lib` |
| Nangate45 | 1,10 V | `NangateOpenCellLibrary_PDKv1_3_v2010_12/Front_End/Liberty/NLDM/NangateOpenCellLibrary_typical.lib` |
| Nangate15 | 0,80 V | `15nm/NLDM/NanGate_15nm_OCL_typical_conditional_nldm.lib` |

Las rutas son relativas a `syn_libraries`. Los tres originales y snapshots
coinciden por SHA-256. Otros corners y variantes de modelo están inventariados
en el Excel y no se habilitan automáticamente.

El atributo Liberty `area` no implica una unidad física universal. En este
estudio la presentación usa la convención µm², respaldada por:

- Nangate45: databook suministrado,
  `Front_End/Doc/Databook/Profilings/prof_area_NangateOpenCellLibrary_typical_typical.html`,
  que etiqueta los perfiles como `um2`.
- Nangate15: Martins et al., ISPD 2015, tabla 2, `Cell Area (µm²)`, DOI
  [10.1145/2717764.2717783](https://doi.org/10.1145/2717764.2717783).
  El README suministrado cita esta publicación. La fuente y su alcance están
  documentados en la ficha F10.
- IHP: la celda `sg13g2_a21oi_2` del
  [LEF oficial](https://raw.githubusercontent.com/IHP-GmbH/IHP-Open-PDK/main/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef)
  mide `3.84 BY 3.78`, cuyo producto es `14.5152`, coincidente con el Liberty
  suministrado y su PDF. La documentación IHP define las dimensiones de layout
  en micrómetros. Es corroboración de convención para una celda; no una
  auditoría completa de geometrías o versiones.

IHP se vincula con un proceso fabricado; su PDK abierto figura como preview.
Nangate45/FreePDK45 y Nangate15/FreePDK15 son referencias predictivas de
investigación. No se interpreta ninguno de estos resultados como medición del
die final ni se equipara un kit predictivo con un proceso comercial homónimo.
[Fuentes y límites completos](FUENTES_VERIFICADAS.md).

## Hallazgos que condicionan las conclusiones

| Prioridad | Hallazgo | Acción recomendada; no ejecutada en esta revisión |
|---|---|---|
| Alta | LNS16 no tiene tres reportes finales | Cerrar sus casos con memoria y tiempo acotados; no extrapolar valores |
| Alta | Archivo compacto sin `mapped.v`, `mapped.json`, `design.v` ni `cells_sim.v` | Conservar el ZIP completo en las próximas corridas |
| Alta si se afirma exactitud | FXP/FP/Posit/LNS usan oráculo del propio RTL | Añadir referencia matemática independiente para esa pregunta |
| Media | Falta digest integral de código, scripts e imagen en el manifiesto histórico | Capturarlos por corrida y congelar también imágenes base |
| Media | Comparaciones filtran IDs, no hashes/políticas | Evitar mezclar cohortes tras cambiar código, corner o biblioteca |
| Operativa | El runner local limita tiempo, pero no memoria | Usar un entorno con límites de recursos y medir antes de ampliar LNS |

Las netlists faltantes se identificaron al enumerar el archivo real. La
auditoría actual cruza el reporte con `stat.json` y los Liberty; **no se pudo
recontar desde `mapped.json` ni repetir la simulación de esas netlists**. Los
logs acreditan la evidencia guardada, no reemplazan una nueva ejecución.

Compose declara 4 GB, 2 CPU, 128 PIDs y 900 s por comando. Esos límites de
memoria no se aplican a un ensayo que invoca las herramientas directamente en
la máquina. Aumentar el timeout no demuestra que exista memoria suficiente.

## Qué permanece fuera de lo demostrado

- Área de cables, core, die, pads, clock tree y cualquier implementación PnR.
- Cierre de timing, frecuencia alcanzable, potencia o rendimiento comparable.
- Óptimo global de área: ABC emplea heurísticas de optimización y mapeo.
  [Berkeley ABC](https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm).
- Equivalencia funcional exhaustiva de todo estado/entrada.
- Exactitud matemática independiente de las familias no enteras.
- Validación de TCU completas, octets o todos los RTL del repositorio.
- Build Docker reciente e interacción de navegador comprobados en esta sesión.

La aprobación sugerida es del **método delimitado y de las cuentas auditadas**.
Las afirmaciones adicionales deben vincularse con pruebas y artefactos que
realmente existan.
