#!/usr/bin/env bash
# Ejecutar desde una terminal del usuario, fuera del entorno de solo lectura.
# Elimina cachés; no elimina node_modules, proyectos, respaldos ni volúmenes.
set -euo pipefail

if [[ $(id -u) -eq 0 ]]; then
  echo 'Ejecuta este script con tu usuario normal, sin anteponer sudo.' >&2
  exit 1
fi

echo 'Espacio antes de la limpieza:'
df -h /

python3 - <<'PY'
from pathlib import Path
import shutil

user_dir = Path.home()
targets = [
    '.cache',
    '.npm/_cacache',
    '.npm/_npx',
    '.npm/_logs',
    '.bun/install/cache',
    '.gradle/caches',
    '.cargo/registry/cache',
    '.composer/cache',
    '.config/Composer/cache',
]
browser_caches = {'Cache', 'Code Cache', 'GPUCache', 'ShaderCache', 'GrShaderCache'}
for relative in ['.config/chromium', '.config/google-chrome', '.config/BraveSoftware/Brave-Browser']:
    browser = user_dir / relative
    if browser.is_dir() and not browser.is_symlink():
        for profile in browser.iterdir():
            if profile.is_dir() and not profile.is_symlink():
                for name in browser_caches:
                    targets.append(str((profile / name).relative_to(user_dir)))

failures = []
for relative in targets:
    path = user_dir / relative
    if not path.exists() or path.is_symlink():
        continue
    print(f'Limpiando {path}', flush=True)
    try:
        for child in path.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink(missing_ok=True)
    except OSError as error:
        failures.append(str(path))
        print(f'No se pudo completar {path}: {error}')
if failures:
    print(f'Carpetas pendientes: {len(failures)}')
PY

if command -v pnpm >/dev/null 2>&1; then
  pnpm store prune || echo 'No se pudo completar la limpieza del almacén pnpm.'
fi

if command -v pacman >/dev/null 2>&1; then
  echo 'Limpiando paquetes descargados; sudo puede solicitar tu contraseña.'
  sudo pacman -Scc --noconfirm || echo 'Queda pendiente la caché de paquetes del sistema.'
fi

if command -v docker >/dev/null 2>&1; then
  echo 'Limpiando únicamente la caché de construcción de Docker.'
  sudo docker builder prune --all --force || echo 'Queda pendiente la caché de construcción Docker.'
fi

echo 'Espacio después de la limpieza:'
df -h /
