# ASIC Area Lab

Aplicación para medir **área de celdas** de las **11 DPU registradas existentes**
en `ParametricTensorCoreUnit`. FastAPI, React + Vite y las herramientas EDA
se empaquetan en **un solo contenedor**. La presentación y el RTL original
no se modificaron.

La explicación completa de selecciones, herramientas, conexiones y reportes
está en [Pipeline paso a paso](docs/PIPELINE_PASO_A_PASO.md).

Los grafos interactivos de contenedor, capas y procesamiento están en
[Diagramas del pipeline](docs/diagramas/index.html), con versiones SVG/PNG y
[recibos de validación](docs/diagramas/README.md).

Los diseños admitidos, anchos y referencias de validación están en
[DPU y formatos integrados](docs/DPU_FORMATOS.md). Las ampliaciones a octets y
TCU están en [Pruebas por componente y formato](docs/PRUEBAS_COMPONENTES_FORMATOS.md).

## Qué hace

- Selecciona una biblioteca: IHP SG13G2 130 nm, Nangate 45 nm o Nangate FreePDK15.
- Selecciona INT8/16, INT16/32, FXP8/16, FXP16/32, FP8, FP16, FP32,
  Posit8, Posit16, Posit32 o LNS16 mediante sus perfiles revisados.
- Analiza el VHDL original y su wrapper con GHDL, conservando sus librerías.
- Simula el RTL con 256 estímulos deterministas por formato y captura sus
  resultados definidos. En INT8 e INT16 comprueba además la referencia
  matemática independiente del producto punto firmado módulo 2^bits(R).
- Genera Verilog con GHDL y mapea lógica y registros con Yosys contra Liberty.
- Rechaza operadores sin mapear, celdas sin área, latches inesperados o
  resultados funcionales incorrectos.
- Simula la netlist mapeada con iverilog usando modelos funcionales generados
  desde el mismo Liberty. Compara los 256 resultados bit a bit con el RTL.
- Suma áreas por tipo de celda y comprueba que coincidan con `stat -liberty`.
- Guarda historial, reportes JSON/CSV, netlists, scripts, hashes y logs.
- Muestra progreso, desglose y comparación de resultados en el frontend.
- Compara tecnologías para una DPU o formatos dentro de una tecnología.

**Alcance:** área combinacional + FF/latches + macros si las hubiera.
Estas DPU no usan macros SRAM: las tablas y ROM se bajan a lógica.
Excluye conexiones, placement, routing, clock tree, pads, floorplan y área del die.
No se impone una frecuencia objetivo ni se ejecuta STA. El mapeo usa la misma
política de ABC para las tres tecnologías; no afirma cierre temporal ni un óptimo
global de área. Los tests por vectores no equivalen a una prueba formal ni a
un estudio de precisión numérica de FP, FXP, Posit o LNS.

## Diseños medidos

Cada perfil conserva su top y wrapper originales. Como ejemplo,
`INT8_16_DPU_perf_top` mantiene el siguiente circuito:

```text
80 bits de registros de entrada → DPU combinacional → 16 bits de registro de salida
R = A0×B0 + A1×B1 + A2×B2 + A3×B3 + C0
```

Incluye el wrapper: **96 flip-flops esperados para INT8/16**. El resto tiene
anchos y controles propios, detallados en [DPU_FORMATOS.md](docs/DPU_FORMATOS.md).
No se sustituyó el multiplicador
FloPoCo por otro operador para obtener un circuito menor. Se mide la implementación
real suministrada; no solo la ecuación matemática.

## Inicio con Docker

Desde esta carpeta:

```bash
docker compose up --build -d
```

- Aplicación: <http://localhost:8000>
- API/OpenAPI: <http://localhost:8000/docs>
- Salud: <http://localhost:8000/api/health>

La primera construcción descarga OSS CAD Suite **2026-09-04** para Linux x64
(aproximadamente 741 MB comprimidos). Su SHA-256 se verifica en el Dockerfile.
El frontend se compila en una etapa Node; FastAPI sirve sus archivos estáticos
en el contenedor final. **Vite es herramienta de desarrollo/construcción**;
no se usa su servidor de desarrollo en el despliegue.

El runtime usa Python 3.12 sobre Debian Trixie e incluye `build-essential`
y `zlib1g-dev`: GHDL LLVM necesita `cc`, el linker y los archivos de enlace
de zlib (`-lz`). El runtime de GHDL suministrado también requiere glibc ≥2.38;
Bookworm ofrece 2.36 y Trixie 2.41. Durante la construcción,
`scripts/check_toolchain.py` verifica análisis, elaboración/enlace, simulación
y generación de Verilog como el usuario sin root del contenedor. Consultar
solo `ghdl --version` no detecta la ausencia de esas dependencias.

Solo hay un servicio en Compose. SQLite está embebido y el volumen
`area-lab-data` conserva historial y artefactos. **PostgreSQL no es necesario**
para un único proceso con una cola de síntesis. El contrato de repositorio
permite incorporar un adaptador PostgreSQL si luego se requiere concurrencia
entre varios procesos o acceso compartido.

```bash
docker compose logs -f area-lab
docker compose down
```

`down` conserva el volumen. No ejecutar `down -v` si se desea conservar el historial.
El contenedor trabaja sin root, con un único worker HTTP y una cola acotada.
Los subprocesos EDA tienen un tiempo máximo configurable de 900 segundos por
comando; Compose permite hasta 4 GB y limita el proceso a 2 CPU. El límite
inicial de 180 segundos resultó insuficiente para FXP16/32. Se mantiene un
solo worker EDA; el plazo de apagado es de 20 minutos. Si no alcanza para
vaciar la cola, los trabajos inconclusos se marcarán interrumpidos al reiniciar.
Si un reinicio interrumpe una evaluación, se marca como interrumpida y puede
crearse otra; los trabajos pendientes no se reanudan automáticamente.

## Organización y arquitectura limpia

```text
asic-area-lab/
├── backend/
│   ├── src/area_lab/
│   │   ├── domain/           # Entidades, errores y puertos; sin FastAPI/SQLite
│   │   ├── application/      # Casos de uso, validación de opciones y cola
│   │   ├── infrastructure/   # Adaptadores SQLite, GHDL/Yosys, Liberty y configuración
│   │   ├── api/              # Rutas HTTP y contratos Pydantic
│   │   └── main.py           # Composition root e inyección de dependencias
│   ├── tests/                # Contratos, fallos, persistencia y pipeline real
│   ├── pyproject.toml
│   ├── requirements.lock
│   └── requirements-dev.lock
├── frontend/
│   ├── src/features/experiments/  # Componentes y hooks de evaluaciones
│   ├── src/shared/               # API, validación Zod, contratos y utilidades
│   ├── src/App.tsx
│   └── package-lock.json
├── assets/
│   ├── rtl/<design_id>/      # Copias idénticas de DPU, helpers y wrappers
│   ├── libraries/            # Liberty suministrados, sin cambios
│   └── manifest.json         # Procedencia, commit y hashes de los snapshots
├── scripts/prepare_assets.py
├── docs/VALIDACION.md
├── Dockerfile
└── compose.yaml
```

`ExperimentService` depende de `ExperimentRepository` y `SynthesisGateway`,
contratos del dominio. SQLite y GHDL/Yosys implementan esos contratos;
`create_app` realiza la composición. El núcleo no importa FastAPI ni una base
de datos concreta. Las operaciones EDA corren fuera del event loop HTTP.

En el frontend, React Query gestiona caché, estados y polling; Zod valida
las respuestas HTTP en ejecución. TypeScript utiliza modo estricto.
Los errores, carga, ausencia de resultados y bibliotecas pendientes tienen
estados explícitos. No hay resultados inventados en la interfaz.

## Tecnologías suministradas

| ID | Biblioteca | Condición inicial | Estado |
|---|---|---|---|
| `ihp130` | IHP SG13G2 | typical, 1,20 V, 25 °C | Disponible |
| `nangate15` | Nangate / FreePDK15 | typical NLDM, 0,80 V, 25 °C | Disponible |
| `nangate45` | Nangate / FreePDK45 | typical NLDM, 1,10 V, 25 °C | Disponible |

No se intercambia IHP por SKY130 ni FreePDK15 por ASAP7. Para 45 nm se usa el
Liberty de texto del paquete `NangateOpenCellLibrary_PDKv1_3_v2010_12`, en
`Front_End/Liberty/NLDM/NangateOpenCellLibrary_typical.lib`. Contiene 134 celdas
con área; su condición nominal es 1,10 V y 25 °C. No se mezclan corners ni se
incluyen los archivos de metadatos `._*` o la extensión `Low_Power`.

Para regenerar las copias y sus hashes desde `../syn_libraries`:

```bash
python3 scripts/prepare_assets.py
```

Los tres Liberty se incluyen en la imagen mediante `COPY assets/`. Si ya se
estaba usando Docker, reconstruir y recrear el servicio con
`docker compose up --build -d`; el volumen conserva el historial. La opción
45 nm se habilita automáticamente a partir del catálogo del backend.

Las áreas son los campos `area` de las celdas Liberty. Se muestran en µm²
siguiendo la convención de estas bibliotecas; la procedencia de esa convención
se registra en el reporte. Liberty no impone por sí solo una unidad física
universal de área. El cálculo usa Decimal y no deriva áreas del número de
nanómetros ni de cantidades de LUT/DSP FPGA.

## Desarrollo local

Python ≥3.12, Node ≥22.12 y OSS CAD Suite en el PATH.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e backend
cd frontend
npm ci
```

Desde la raíz del ejemplo, en terminales separadas:

```bash
make dev-api
make dev-web
```

Frontend: <http://localhost:5173>. Vite redirige `/api` a FastAPI en el puerto 8000.
Si las herramientas no están en PATH, definir
`AREA_LAB_TOOLCHAIN_BIN=/ruta/oss-cad-suite/bin` antes de iniciar el servicio.
Las variables `AREA_LAB_*` pueden cambiar rutas y límites; `.env.example`
documenta los valores, pero no se carga automáticamente.

## API mínima

```bash
curl -X POST http://localhost:8000/api/v1/experiments \
  -H 'Content-Type: application/json' \
  -d '{"design_id":"int8_16","technology_id":"ihp130"}'
```

Devuelve HTTP 202 y un ID. Consultar `/api/v1/experiments/{id}` para el estado.

| Ruta | Uso |
|---|---|
| `GET /api/v1/catalog` | Diseños y tecnologías disponibles |
| `POST /api/v1/experiments` | Crear evaluación |
| `GET /api/v1/experiments` | Últimas 100 evaluaciones |
| `GET /api/v1/experiments/{id}` | Estado y reporte |
| `GET /api/v1/experiments/{id}/logs` | Últimos 100 KB del log |
| `GET /api/v1/experiments/{id}/artifacts` | ZIP de resultados y evidencia |
| `GET /api/v1/experiments/{id}/report.csv` | Desglose por tipo de celda |

La API solo acepta diseños y tecnologías del catálogo. No permite ejecutar
comandos arbitrarios ni recibir rutas de archivos desde el frontend.

## Verificación

```bash
make test
make lint
cd frontend
npm run build
npm run format:check
```

Los tests marcados `integration` ejecutan GHDL/Yosys/iverilog con los tres
Liberty: 33 combinaciones de DPU y tecnología, además de las comprobaciones
de toolchain y compilación. El barrido completo puede tardar varios minutos
por diseño; no ejecuta trabajos en paralelo. Si no están instaladas las
herramientas, las integraciones se omiten explícitamente.
Para comprobar solo lógica de aplicación:

```bash
.venv/bin/python -m pytest backend/tests -m 'not integration'
```

La evidencia de lo realmente verificado y las limitaciones del entorno están
en [docs/VALIDACION.md](docs/VALIDACION.md).

## Referencias

- [GHDL synthesis](https://ghdl.github.io/ghdl/using/Synthesis.html).
- [Yosys: mapping to cell libraries](https://yosyshq.readthedocs.io/projects/yosys/en/v0.56/using_yosys/synthesis/cell_libs.html).
- [FastAPI en contenedores](https://fastapi.tiangolo.com/deployment/docker/).
- [React](https://react.dev/learn) y [Vite](https://vite.dev/guide/).
- [IHP Open PDK](https://github.com/IHP-GmbH/IHP-Open-PDK).
- Martins et al., *Open Cell Library in 15nm FreePDK Technology*, ISPD 2015,
  [DOI: 10.1145/2717764.2717783](https://doi.org/10.1145/2717764.2717783).

Los archivos suministrados conservan sus cabeceras originales. Las copias de RTL
y Liberty siguen sujetas a sus licencias de origen.
