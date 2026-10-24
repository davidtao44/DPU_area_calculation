# DPU y formatos integrados

La aplicación mide las once DPU de
`ParametricTensorCoreUnit/DPU_Performance_Area_Comparison/src`, con los wrappers
registrados originales y los Liberty typical de IHP130, Nangate45 y Nangate15.
No se modifica el RTL para reemplazar su aritmética o reducir su área.

**Estado de validación:** diez DPU completaron las tres tecnologías (30 casos).
LNS16 está integrada como perfil, pero sus tres mapeos siguen pendientes: las
pruebas se detuvieron por presión de recursos en el equipo. Ver
[evidencia parcial](validation/dpu-matrix-20261018/README.md).

## Selección y fronteras de medición

En **Diseño y formato numérico** se escoge la variante existente. A continuación
se selecciona la tecnología y se pulsa **Calcular área**. Cada evaluación mide
un top, un formato y una biblioteca. No es una DPU con formato dinámico.

| `design_id` | Top | Bits A/B | Bits C/R | Bits de registros declarados |
|---|---|---:|---:|---:|
| `int8_16` | `INT8_16_DPU_perf_top` | 8 | 16 | 96 |
| `int16_32` | `INT16_32_DPU_perf_top` | 16 | 32 | 192 |
| `fxp8_16` | `FXP8_16_DPU_perf_top` | 8 | 16 | 96 |
| `fxp16_32` | `FXP16_32_DPU_perf_top` | 16 | 32 | 192 |
| `fp8` | `FP8_DPU_perf_top` | 8 | 8 | 80 |
| `fp16` | `FP16_DPU_perf_top` | 16 | 16 | 160 |
| `fp32` | `FP32_DPU_perf_top` | 32 | 32 | 320 |
| `posit8` | `POSIT8_DPU_perf_top` | 8 | 8 | 80 |
| `posit16` | `POSIT16_DPU_perf_top` | 16 | 16 | 160 |
| `posit32` | `POSIT32_DPU_perf_top` | 32 | 32 | 320 |
| `lns16` | `LNS16_DPU_perf_top` | 16 | 16 | 160 |

Los wrappers tienen ocho registros de operandos, uno de acumulador y uno de
salida: `8 × bits(A/B) + 2 × bits(C/R)`. Los registros eliminados legítimamente
por optimización no se cuentan como celdas. El reporte muestra los FF realmente
mapeados; no convierte automáticamente bits declarados en área.

En enteros se comprueba además el número esperado de FF del perfil. Para las
otras familias se exige estado registrado dentro del límite declarado,
ausencia de latches/macros y coincidencia funcional de las salidas. La
validación por vectores no constituye equivalencia formal.

## Perfiles y fuentes

Los perfiles revisados se encuentran en
[designs.py](../backend/src/area_lab/infrastructure/designs.py): top, biblioteca
VHDL, fuentes ordenadas, wrapper, anchos, familia y referencia de validación.
La infraestructura interpreta esos perfiles; el dominio no depende de GHDL,
Yosys, FastAPI ni SQLite.

`scripts/prepare_assets.py` utiliza esos mismos perfiles para copiar las
fuentes. Preserva las rutas de `needed_flopoco_files`, sin aplanar archivos con
nombres iguales de diferentes formatos. Las fuentes aritméticas se analizan en
`<design_id>_lib`; cada wrapper se analiza en `work`, como en el repositorio.
Cada evaluación tiene su propio directorio y conserva sus fuentes bajo
`sources/rtl/<design_id>/`, también incluidas en el ZIP.

Posit16 y Posit32 repiten algunos helpers idénticos entre sus archivos de suma
y multiplicación. GHDL LLVM generaba símbolos de enlace duplicados al analizar
esos archivos completos. Sus perfiles usan `unique_ghdl_units`: el parser de
`ghdl --chop` separa entidades y arquitecturas en `compilation/*.vhdl`, se
comprueba identidad **byte a byte** de cada unidad repetida y se compila una
sola copia. Una repetición diferente detiene la evaluación. No se aplican
parches al RTL ni opciones de linker que oculten definiciones conflictivas.
El manifiesto registra unidades, hashes y reutilizaciones; el ZIP incluye
tanto los snapshots originales como las unidades de compilación derivadas.

El manifiesto registra hashes del RTL, Liberty, estímulos, resultados RTL y
vectores esperados. La base SQLite y los reportes anteriores permanecen
compatibles; no se requiere migración ni otro contenedor.

## Qué significa la validación

Se generan **256 estímulos deterministas por diseño**, con semilla `20261005`.
Incluyen casos dirigidos por familia, actividad en cada lane y palabras
aleatorias de los anchos correspondientes. Cada estímulo se mantiene durante
dos flancos de subida para capturar el resultado del wrapper registrado. En
LNS16 se intercalan palabras crudas con operandos normales de signos variados
y magnitud entre 0,25 y 4, para ejercitar las tablas de corrección además de
las rutas de excepción.

1. GHDL simula el RTL original y escribe `rtl-results.txt`.
2. Se exige el número completo de resultados, sin X, Z u otros bits indefinidos.
3. Para INT8 e INT16, Python verifica independientemente el producto punto
   firmado reducido módulo `2^bits(R)`. Un fallo detiene la evaluación.
4. Se construye `vectors.txt` con los estímulos y las salidas RTL esperadas.
5. GHDL genera Verilog; Yosys mapea contra el Liberty seleccionado.
6. Icarus simula esa netlist y exige **igualdad bit a bit** con el RTL para
   todos los estímulos. No se aplican tolerancias numéricas.

Para FXP, FP, Posit y LNS, `reference=rtl_bit_exact` significa preservación de
la implementación original durante la conversión y el mapeo. No es una
referencia matemática independiente de esas aritméticas. El reporte declara
`numerical_accuracy=not_assessed`; no calcula error relativo o exactitud de una
red neuronal. Los experimentos de error del repositorio constituyen otro
estudio y no se presentan como ejecutados por esta aplicación.

Particularidades que se conservan:

- FXP8/16: 5/10 bits fraccionarios; FXP16/32: 10/20, según los operadores.
- FP8: e4m3 de los operadores FloPoCo; no se sustituye por `e4m3fn` de software.
- FP16: e5m10; FP32: e8m23. Se mantiene la cadena de FMA y su redondeo original.
- Posit8: `es=0`; Posit16: `es=1`; Posit32: `es=2`. En Posit16, los nombres
  `posit16_0_*` son históricos: el DPU instancia `PositMult_16_1_F0_uid2` y el
  sumador también contiene decodificadores `PositDecoder_16_1`. Se conservan
  los árboles de suma y los bytes originales de todas las fuentes.
- LNS16: `wE=4`, `wF=9`, bits de excepción y tablas de corrección originales.

Los controles de área continúan exigiendo celdas reconocidas y mapeadas, área
válida y coincidencia de la suma por celda con `stat -liberty`. Las ROM se
reducen a lógica; no se introducen macros SRAM. Se excluyen conexiones,
placement, routing, STA, clock tree y área de chip completo.

## Comparaciones en la interfaz

- **Tecnologías para la DPU seleccionada:** una última evaluación válida por
  biblioteca, siempre del mismo `design_id` elegido en el formulario.
- **Formatos en una tecnología:** una última evaluación válida por DPU,
  filtrada por la biblioteca escogida en la comparación.

El historial y el reporte identifican el formato realmente evaluado. Comparar
formatos implica comparar circuitos, anchos y cantidades de registros distintos;
no demuestra igualdad de precisión, frecuencia o rendimiento.

## Uso por API

```bash
curl -X POST http://localhost:8000/api/v1/experiments \
  -H 'Content-Type: application/json' \
  -d '{"design_id":"fp16","technology_id":"nangate45"}'
```

Se conservan los endpoints de historial, logs, CSV y ZIP. La API acepta solo
los identificadores registrados, sin rutas o comandos arbitrarios. Omitir
`design_id` conserva el valor predeterminado `int8_16` para clientes anteriores.

Para reconstruir la imagen con los nuevos perfiles y snapshots:

```bash
docker compose up --build -d
```

## Pruebas y alcance restante

La integración EDA está parametrizada para los **33 casos DPU/tecnología** en
[test_pipeline_integration.py](../backend/tests/test_pipeline_integration.py).
Los resultados efectivamente obtenidos y los límites del entorno se documentan
en [VALIDACION.md](VALIDACION.md).

Se prueban también aceptación HTTP de todos los diseños, rechazo de salidas
RTL indefinidas/incompletas o aritmética entera incorrecta, selección de DPU y
filtrado de comparaciones en React. La integración de TCU completas, octets y
otros tops de sistema sigue fuera de esta ampliación.
