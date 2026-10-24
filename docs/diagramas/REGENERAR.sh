#!/usr/bin/env bash
set -euo pipefail

# Solo genera gráficos; no ejecuta síntesis, Docker ni modifica código de la app.
diagram_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
archify_root="${ARCHIFY_DIR:-/home/davidgonza04/.agents/skills/archify}"
mkdir -p "$diagram_root/validacion"

for diagram_name in 01_ARQUITECTURA 02_EVALUACION 03_COMANDOS 04_PRUEBAS_COMPONENTES; do
    diagram_type=architecture
    if [[ "$diagram_name" == 02_EVALUACION ]]; then
        diagram_type=workflow
    fi
    node "$archify_root/bin/archify.mjs" validate "$diagram_type" \
        "$diagram_root/especificaciones/$diagram_name.json" --quality showcase --json \
        > "$diagram_root/validacion/$diagram_name.composicion.json"
    node "$archify_root/bin/archify.mjs" deliver "$diagram_type" \
        "$diagram_root/especificaciones/$diagram_name.json" \
        "$diagram_root/$diagram_name.html" --quality showcase --json \
        > "$diagram_root/validacion/$diagram_name.entrega.json"
done

python3 "$diagram_root/exportar-svg.py"

