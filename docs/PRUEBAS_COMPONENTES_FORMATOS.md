# Pruebas por componente y formato numérico

**El programa admite las once DPU registradas mediante perfiles revisados.**
Octets y TCU todavía requieren adaptar sus interfaces, secuencias y controles.
El estado actual está en [DPU_FORMATOS.md](DPU_FORMATOS.md).

Diagrama: [HTML interactivo](diagramas/04_PRUEBAS_COMPONENTES.html),
[SVG](diagramas/exportaciones/04_PRUEBAS_COMPONENTES.svg) y
[PNG](diagramas/exportaciones/04_PRUEBAS_COMPONENTES.png).

El diagrama conserva la **propuesta anterior a la ampliación de las DPU**.
Sus referencias a otras DPU pendientes son históricas. Las pruebas de octets,
TCU e integración continúan siendo propuestas, sin ejecución en la aplicación.

## 1. Qué se prueba actualmente

| Aspecto | Implementación actual |
|---|---|
| Diseños | Once DPU, cada una con su wrapper registrado original |
| Estímulos | 256 casos dirigidos y deterministas por formato |
| Referencia entera | Producto punto firmado módulo 2^bits(R), INT8 e INT16 |
| Otras referencias | Oráculo RTL original; precisión numérica independiente no evaluada |
| Simulación RTL | GHDL y testbench parametrizado por top/anchos |
| Simulación mapeada | Icarus y comparación bit a bit, sin tolerancias |
| Estado | Controles por perfil; rechaza latches y macros en estas DPU |
| Área | Suma por celda contrastada con `stat -liberty` |
| Tecnologías | IHP130, Nangate15 y Nangate45, condiciones typical |

Las pruebas por vectores no demuestran equivalencia formal ni cierre temporal.

## 2. Pruebas según el nivel de componente

Cada fila combina su suite con la referencia de la familia numérica que
realmente soporte el top. No se supone que todas las variantes del repositorio
implementen los once formatos.

| Componente | Pruebas funcionales y de protocolo | Qué adaptar |
|---|---|---|
| Multiplicador o sumador aislado | Operación elemental, signos, límites, anchos y casos numéricos de su familia | Puertos, operación de referencia y testbench del operador |
| DPU combinacional por formato | Producto punto, acumulador, signos, cancelación, límites y resultado codificado | Codec, orden de operaciones, anchos y testbench sin wrapper |
| DPU con wrapper registrado | Pruebas aritméticas + captura de operandos, latencia, secuencia de resultados y reset/enable si existen | Puertos de reloj/control y contrato de ciclos; los 96 FF solo corresponden al wrapper INT8 actual |
| DPU paramétrica | Cada combinación válida de tipo/ancho, selección de ruta y cambios de modo permitidos por el RTL | Inventario de modos, códigos de selectores y referencia por modo |
| Arreglo de DPU / octet | Resultados por lane, operandos diferentes por lane, aislamiento entre lanes, carga/lectura de buffers, reset y acumuladores | Arrays, número de lanes, organización de buffers y secuencia de control |
| TCU individual | Fragmentos y secuencias HMMA step0/step1, resultado matricial, acumulación encadenada, `start`, `busy`, `done` y señales adicionales expuestas | Testbench de secuencias, packing/despacking y referencia matricial que respete el datapath |
| Wrapper dual | Pruebas TCU + ejecución simultánea de ambos datapaths, aislamiento de operandos/resultados y control compartido | Dos bancos de entradas, cuatro octets y reconstrucción de resultados según la variante |
| Integración Klessydra / FlexGrip | Protocolos de la interfaz del top, distribución de operandos, resultados/writeback y stall cuando formen parte de la jerarquía medida | Emular el host y comprobar las señales que el top exponga; no incluir automáticamente el CPU/GPU completo |

Los resets, enables, señales de validación y modos inválidos solo se prueban
según lo que define cada interfaz. No se agregan puertos ni estados al hardware
para acomodar un testbench genérico.

En TCU, la referencia debe seguir los fragmentos, orden de acumulación y
redondeos del RTL. Una operación ideal de matrices en alta precisión sirve para
estudiar error numérico, pero no reemplaza por sí sola el modelo funcional del
datapath y su secuencia de instrucciones.

## 3. Pruebas según la familia numérica

| Familia y formatos del inventario DPU | Casos dirigidos propuestos | Referencia necesaria |
|---|---|---|
| INT8_16, INT16_32 | Cero, positivos/negativos, mínimos/máximos, productos de signos distintos, acumulación y overflow | Enteros exactos con el ancho y la política de overflow definidos por cada RTL |
| FXP8_16, FXP16_32 | Escala binaria, valores separados por un LSB, cuantización, truncamiento/redondeo, límites y overflow | Codec de punto fijo y ubicación real del punto binario; no tratar los bits como enteros sin escala |
| FP8, FP16, FP32 | Cero/signo, exponentes y mantisas límite, cancelación y redondeo; casos especiales únicamente según la implementación | Encoding y aritmética concretos del RTL, incluidos orden de operaciones y redondeos |
| Posit8, Posit16, Posit32 | Cero, extremos, régimen/exponente, cambios de escala y NaR si corresponde | Codec con los parámetros `n` y `es` del diseño y sus reglas aritméticas |
| LNS16 | Cero/signo, productos en dominio logarítmico, sumas/restas, cancelación y límites de las tablas de corrección | Encoding LNS y aproximaciones/correcciones implementadas; no usar directamente la referencia entera |

También se usan vectores aleatorios reproducibles, con rangos, semilla y
distribución documentados. El tamaño del corpus debe decidirse según cobertura
y recursos: 256 es el piloto actual; el repositorio tiene un estudio separado
con 10.000 vectores por formato.

**No se presupone soporte IEEE completo en todas las variantes FP**, ni una
política común de saturación, subnormales, infinitos o redondeo. Esas propiedades
se obtienen de los RTL y los codecs de cada diseño antes de definir sus oráculos.

## 4. Corrección del circuito y error numérico son controles diferentes

1. **Corrección funcional de referencia:** definir el resultado codificado
   esperado, respetando operación, anchos, excepciones y redondeos del diseño.
2. **Preservación durante síntesis:** aplicar los mismos estímulos al RTL y a
   la netlist y comparar bits y ciclos en las ventanas donde las salidas sean
   válidas. Comparar también reset y señales de control que correspondan.
3. **Error numérico:** decodificar el resultado y compararlo con una referencia
   matemática de alta precisión para medir cuantización y aproximaciones.

Una tolerancia de error numérico no debe ocultar diferencias funcionales
introducidas por la conversión o el mapeo. Las clases de resultado especial
deben manejarse explícitamente; no se comparan NaN/NaR como números ordinarios.

MAE/RMSE u otras métricas de precisión, las campañas de inyección de fallos y
la equivalencia formal pueden ser estudios adicionales. No se convierten en
requisitos nuevos del alcance de área sin acordar esa ampliación.

## 5. Controles ASIC comunes a los perfiles

| Etapa | Control |
|---|---|
| Elaboración | Top, paquetes, bibliotecas y generics correctos; fuentes y versiones registradas |
| RTL | Aritmética y protocolo correctos para el perfil y los modos realmente soportados |
| Conversión | Verilog sintetizable y conservación del comportamiento; una prueba intermedia puede aislar errores de conversión |
| Mapeo | Referencias resueltas, operadores genéricos eliminados mediante mapeo y modelos completos de las celdas utilizadas |
| Estado y memoria | Revisar FF, latches y memorias según el diseño; detectar inferencias inesperadas, sin prohibir todo estado diferente del piloto |
| Netlist | Repetir los estímulos y comparar resultados y control con el RTL |
| Área | Suma completa por tipo, unidades verificadas, desglose y coincidencia con `stat -liberty`, sin doble conteo |
| Reporte | Identificar top/configuración, modo estático o dinámico, tecnología, corner, hashes, política y controles realizados |

Para TCU se debe revisar el soporte de mapeo de latches y la representación
del almacenamiento. Si no hay una macro equivalente, se mide la implementación
con estado y lógica de acceso. Si se usan macros, hacen falta modelos de área
y simulación y una regla de mapeo compatible con puertos, reset y latencia.

Las conexiones se conservan en la netlist para comprobar la función, pero no
se calcula área de cableado ni se ejecuta place & route. STA sigue fuera del
piloto actual.

## 6. Cambios implementados y ampliaciones pendientes

La integración de las DPU ya generalizó catálogo, contrato HTTP, selector React,
fuentes por biblioteca, anchos de testbench, referencias, controles de estado,
comparaciones e inclusión de fuentes en los artefactos. El detalle está en
[DPU_FORMATOS.md](DPU_FORMATOS.md). La infraestructura FastAPI, cola y SQLite se
conserva en un solo contenedor.

Los recursos del piloto se ampliaron a 900 s/comando y 4 GB de límite Docker:
FXP16/32 con IHP130 alcanzó el límite anterior de 180 s. Las TCU aún necesitan
perfiles de interfaces arrays, generics, protocolos y almacenamiento, no solo
una nueva entrada de catálogo. No se garantiza que cualquier entidad VHDL del
repositorio pueda medirse sin adaptar su validación.

## 7. Cómo organizar el barrido

Para DPU aisladas por formato, el caso es:

```text
top DPU/formato + fuentes + interfaz + biblioteca tecnológica + suite de pruebas
```

La suite EDA incluye once tops DPU por tres tecnologías: 33 casos de mapeo.
Los resultados efectivamente ejecutados se registran en [VALIDACION.md](VALIDACION.md).
Las variantes de octets y TCU no están incluidas en esos 33 casos.

Para una TCU completa con selección dinámica:

```text
top TCU/configuración + tecnología → una netlist y un área
                               ↳ probar todos los modos soportados
```

Los modos son casos de validación del mismo hardware. No producen áreas
diferentes por cambiar el formato ejecutado. Un top especializado con selectores
constantes sería otra variante y tendría que identificarse como tal.

El alcance TCU sigue referido a sus tops existentes: `TCU_Branch` en Klessydra
(configuración actual de 16 harts) y `dualTensorCoreWrapper` en FlexGrip. El
testbench puede emular datos del host sin incluir automáticamente su register
file externo ni el CPU/GPU completo en la medición.

## 8. Trabajo del repositorio que puede reutilizarse

- [Análisis DPU por formato](../../ParametricTensorCoreUnit/DPU_Error_Analysis/DPU_Error_Analysis_README.md): generadores, codecs, referencias y testbenches. Es un flujo separado, no integrado automáticamente en ASIC Area Lab.
- [Testbenches DPU](../../ParametricTensorCoreUnit/DPU_Error_Analysis/testbenches/): pruebas por los once formatos del inventario.
- [TCU FP16](../../ParametricTensorCoreUnit/parametricTCUrel0/tensorCorewithFSMFP16_8instrTB.vhd): secuencias HMMA step0/step1 y acumulación encadenada sobre dos octets.
- [TCU dual INT8](../../ParametricTensorCoreUnit/doubleParametricTCUsRel0/doubleTensorCorewithFSMint8_4setsOfstep01_tb.vhd): ambos datapaths, cuatro octets y reconstrucción matricial.
- [Configuración Klessydra](../../ParametricTensorCoreUnit/Klessydra_TCU_Area_Analysis/scripts/run_synth_full_parametric_tcu.tcl): top, bibliotecas y `THREAD_POOL_SIZE=16`.
- [Configuración FlexGrip](../../ParametricTensorCoreUnit/FlexGripPlus_TCU_Area_Analysis/scripts/run_synth_full_parametric_tcu.tcl): top y bibliotecas de la integración dual.

Los testbenches inspeccionados incluyen rutas absolutas Windows y comentarios
de selectores que requieren revisión. Reutilizarlos implica adaptar sus rutas
y confirmar los códigos/contratos contra el RTL elegido; su existencia no
demuestra que ya funcionen en GHDL o contra la netlist ASIC.

Evidencia de la especialización actual:
[catálogo](../backend/src/area_lab/infrastructure/catalog.py),
[contrato API](../backend/src/area_lab/api/schemas.py),
[testbenches y vectores](../backend/src/area_lab/infrastructure/validation.py),
[síntesis y controles](../backend/src/area_lab/infrastructure/synthesis.py),
[selección frontend](../frontend/src/features/experiments/ExperimentForm.tsx) y
[envío del diseño](../frontend/src/App.tsx).

