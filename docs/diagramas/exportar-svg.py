"""Export the SVG of delivered Archify HTML; optionally rasterize using librsvg."""

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=("light", "dark"), default="light")
    parser.add_argument("--width", type=int, default=1600)
    args = parser.parse_args()
    if args.width <= 0:
        parser.error("--width debe ser positivo")
    root = Path(__file__).resolve().parent
    destination = root / "exportaciones"
    destination.mkdir(exist_ok=True)
    records = []
    rasterizer = shutil.which("rsvg-convert")
    for name in (
        "01_ARQUITECTURA",
        "02_EVALUACION",
        "03_COMANDOS",
        "04_PRUEBAS_COMPONENTES",
    ):
        source = root / f"{name}.html"
        text = source.read_text()
        svg = re.search(r"<svg\b[\s\S]*?</svg>", text).group(0)
        css = re.search(r"<style[^>]*>([\s\S]*?)</style>", text).group(1)
        palette = re.search(
            rf'\[data-theme="{args.theme}"\]\s*\{{([^}}]+)\}}', css
        ).group(1)
        variables = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", palette))
        font = re.search(r"body\s*\{[^}]*font-family\s*:\s*([^;]+);", css).group(1)
        css = re.sub(
            r"var\((--[\w-]+)(?:,\s*([^)]*))?\)",
            lambda m: variables.get(m[1], m[2] or "initial").strip(),
            css,
        )
        svg = svg.replace(
            "<svg ",
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'data-theme="{args.theme}" font-family="{html.escape(font, quote=True)}" ',
            1,
        )
        position = svg.index(">") + 1
        svg = (
            svg[:position]
            + "<style>"
            + html.escape(css)
            + '</style><rect width="100%" height="100%" fill="'
            + variables["--bg"].strip()
            + '"/>'
            + svg[position:]
        )
        output = destination / f"{name}.svg"
        output.write_text(svg)
        if rasterizer:
            subprocess.run(
                [
                    rasterizer,
                    "-w",
                    str(args.width),
                    "-o",
                    str(destination / f"{name}.png"),
                    str(output),
                ],
                check=True,
            )
        records.append(
            {
                "name": name,
                "source_html_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "svg_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "kind": "static-svg-export",
                "theme": args.theme,
                "browser_screenshot": False,
                "rasterizer": "rsvg-convert" if rasterizer else None,
                "width": args.width,
            }
        )
        print(f"{name}: SVG" + (" + PNG" if rasterizer else ""))
    (root / "validacion" / "exportaciones.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
