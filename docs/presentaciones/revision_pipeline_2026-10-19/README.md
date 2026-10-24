# Pipeline ASIC Area Lab · revisión GIRA · 19/10/2026

- [PowerPoint editable](Revision_pipeline_ASIC_GIRA.pptx): 53 diapositivas,
  diagramas nativos, dos gráficos editables, logo original `gira.png` y notas.
- [PDF de lectura](Revision_pipeline_ASIC_GIRA.pdf): la misma geometría y
  contenido, exportados con PDFKit; no es una captura del motor PowerPoint.
- [Sustentación y auditoría](AUDITORIA_PIPELINE.md).
- [Guion para la exposición](GUION.md).
- [Fuentes primarias verificadas](FUENTES_VERIFICADAS.md).
- [Auditoría JSON](auditoria_evidencias.json) y [CSV](auditoria_evidencias.csv).
- [Revisión visual y de geometría](revision_visual.json).

La presentación distingue capacidad de una herramienta, comportamiento del
código, evidencia conservada y trabajo pendiente. No reemplaza el PowerPoint
histórico de propuesta. El RTL y la aplicación no se modificaron para crearla.

## Alcance de la comprobación

Se auditaron los 30 paquetes completos conservados, se compararon 44 entradas
con sus originales, se recalcularon 1.536 resultados enteros y se ejecutaron
20 tests backend sin integración y 42 tests frontend. No se ejecutó nueva
síntesis, PnR, STA, formal, build Docker ni revisión de navegador.

LNS16 sigue pendiente. Las netlists de las 30 corridas no están en el archivo
compacto: la auditoría usa el desglose del reporte, stat, Liberty, vectores y
logs. Ese límite se muestra expresamente en la exposición.

## Reproducir los entregables

Python 3.12+, Node, las dependencias de `package.json` y fuentes Liberation.
Desde esta carpeta:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 auditar_evidencias.py
PYTHONDONTWRITEBYTECODE=1 python3 preparar_contenido.py
npm ci
node generar_presentacion.cjs
```

La auditoría solo lee artefactos. Los generadores no ejecutan herramientas EDA.
Se necesita el árbol original del workspace, incluido `gira.png`, para resolver
fuentes, bibliotecas y logo. `contenido.json` es la fuente editable del texto;
`modelo_visual.json` conserva la geometría común de PPTX y PDF.

Se comprobó que el PPTX es un ZIP íntegro con sus 53 diapositivas y notas;
los XML y gráficos fueron inspeccionados y los valores se contrastaron con el
JSON auditado. El PDF se revisó mediante imágenes de sus páginas. No se afirma
una comprobación visual del render específico de PowerPoint/LibreOffice.
