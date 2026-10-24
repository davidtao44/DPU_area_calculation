# Fuentes locales de los diagramas

## Pruebas por componente y formato

El cuarto diagrama representa una propuesta de ampliación. Su matriz y la
evidencia de las especializaciones a INT8 están en
[PRUEBAS_COMPONENTES_FORMATOS.md](../PRUEBAS_COMPONENTES_FORMATOS.md).
Los archivos del repositorio citados allí aportan interfaces, codecs y
testbenches existentes; no se afirma que sus pruebas ya estén portadas al
pipeline ASIC de la aplicación.

Los diagramas describen el código leído del ejemplo. No se atribuye este código a un repositorio público diferente. La siguiente lista respalda los componentes del grafo de arquitectura.

## navegador

- [frontend/src/App.tsx](../../frontend/src/App.tsx)
- [frontend/src/shared/api.ts](../../frontend/src/shared/api.ts)

## api

- [backend/src/area_lab/main.py](../../backend/src/area_lab/main.py)
- [backend/src/area_lab/api/routes.py](../../backend/src/area_lab/api/routes.py)

## aplicacion

- [backend/src/area_lab/application/services.py](../../backend/src/area_lab/application/services.py)

## dominio

- [backend/src/area_lab/domain/models.py](../../backend/src/area_lab/domain/models.py)

## puertos

- [backend/src/area_lab/domain/ports.py](../../backend/src/area_lab/domain/ports.py)

## worker

- [backend/src/area_lab/application/services.py](../../backend/src/area_lab/application/services.py)

## adaptador

- [backend/src/area_lab/infrastructure/synthesis.py](../../backend/src/area_lab/infrastructure/synthesis.py)

## herramientas

- [backend/src/area_lab/infrastructure/process_runner.py](../../backend/src/area_lab/infrastructure/process_runner.py)
- [backend/src/area_lab/infrastructure/validation.py](../../backend/src/area_lab/infrastructure/validation.py)

## repositorio

- [backend/src/area_lab/infrastructure/sqlite_repository.py](../../backend/src/area_lab/infrastructure/sqlite_repository.py)

## assets

- [backend/src/area_lab/infrastructure/catalog.py](../../backend/src/area_lab/infrastructure/catalog.py)
- [assets/manifest.json](../../assets/manifest.json)

## Detalle del recorrido y comandos

- [Servicios y cola](../../backend/src/area_lab/application/services.py).
- [Adaptador de síntesis y script Yosys](../../backend/src/area_lab/infrastructure/synthesis.py).
- [Testbenches y validación](../../backend/src/area_lab/infrastructure/validation.py).
- [Clasificación y suma de áreas](../../backend/src/area_lab/infrastructure/liberty.py).
- [Dockerfile y etapas de construcción](../../Dockerfile).
- [Compose y límites configurados](../../compose.yaml).

Los enlaces son relativos a esta documentación. `validacion/fuentes-locales.json` conserva los hashes del código inspeccionado. Los grafos son una explicación del flujo, no prueba de construcción Docker ni de nueva síntesis.
