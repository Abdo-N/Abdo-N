#!/usr/bin/env python3
"""
Generates a blueprint / technical-drawing style hero banner for a GitHub
profile README. Renders two themes (dark/light) so the README's <picture>
tag can pick the right one via prefers-color-scheme.

Run:
    python3 generate_blueprint_svg.py
"""
import os
from datetime import datetime, timezone

NAME = "ABDELRAHMAN NADER"
SUBTITLE = "COMPUTER ENGINEER  —  GUC"
CALLOUT = "FULL-STACK ENGINEERING  ·  CLI TOOLING  ·  DATA ANALYSIS"
DWG_NO = "DWG NO. ABDO-N-001"

THEMES = {
    "dark": {
        "paper": "#0a1a2b",
        "ink": "#dbe9f4",
        "ink_dim": "#4a6b85",
        "cyan": "#5fd4ff",
        "grid": "#16324a",
    },
    "light": {
        "paper": "#eef3f7",
        "ink": "#12324a",
        "ink_dim": "#6f8aa0",
        "cyan": "#0f7fa8",
        "grid": "#c9d8e3",
    },
}

FONT = "SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"
WIDTH = 900
HEIGHT = 210
MARGIN = 14
GRID_STEP = 24


def crosshair(cx, cy, size, color):
    h = size / 2
    return (
        f'<line x1="{cx-h}" y1="{cy}" x2="{cx+h}" y2="{cy}" stroke="{color}" stroke-width="1"/>'
        f'<line x1="{cx}" y1="{cy-h}" x2="{cx}" y2="{cy+h}" stroke="{color}" stroke-width="1"/>'
    )


def render(theme_name):
    t = THEMES[theme_name]
    date = datetime.now(timezone.utc).strftime("%d %b %Y")

    grid_lines = []
    x = MARGIN
    while x <= WIDTH - MARGIN:
        grid_lines.append(
            f'<line x1="{x}" y1="{MARGIN}" x2="{x}" y2="{HEIGHT-MARGIN}" '
            f'stroke="{t["grid"]}" stroke-width="0.5"/>'
        )
        x += GRID_STEP
    y = MARGIN
    while y <= HEIGHT - MARGIN:
        grid_lines.append(
            f'<line x1="{MARGIN}" y1="{y}" x2="{WIDTH-MARGIN}" y2="{y}" '
            f'stroke="{t["grid"]}" stroke-width="0.5"/>'
        )
        y += GRID_STEP

    corners = "".join(
        crosshair(cx, cy, 14, t["cyan"])
        for cx, cy in (
            (MARGIN, MARGIN),
            (WIDTH - MARGIN, MARGIN),
            (MARGIN, HEIGHT - MARGIN),
            (WIDTH - MARGIN, HEIGHT - MARGIN),
        )
    )

    dim_x1, dim_x2, dim_y = 140, WIDTH - 140, 152
    dim_len = dim_x2 - dim_x1

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
text {{ font-family: {FONT}; }}
.rise {{ animation: rise 0.7s ease-out both; }}
.rise-d {{ animation: rise 0.7s ease-out 0.15s both; }}
.draw {{ stroke-dasharray: {dim_len}; stroke-dashoffset: {dim_len}; animation: draw 0.9s ease-out 0.5s forwards; }}
.tick {{ opacity: 0; animation: fade 0.3s ease-out 1.3s forwards; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .rise, .rise-d, .draw, .tick {{ animation: none; opacity: 1; stroke-dashoffset: 0; }}
}}
</style>
<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="{t["paper"]}"/>
<rect x="{MARGIN}" y="{MARGIN}" width="{WIDTH-2*MARGIN}" height="{HEIGHT-2*MARGIN}" fill="none" stroke="{t["ink_dim"]}" stroke-width="1"/>
{''.join(grid_lines)}
{corners}
<text x="{MARGIN+16}" y="{MARGIN+22}" font-size="10" letter-spacing="1.5" fill="{t["ink_dim"]}">{DWG_NO}</text>
<text x="{WIDTH-MARGIN-16}" y="{MARGIN+22}" font-size="10" letter-spacing="1.5" fill="{t["ink_dim"]}" text-anchor="end">REV A &#183; {date}</text>
<text class="rise" x="{WIDTH/2}" y="98" font-size="32" font-weight="700" letter-spacing="4" fill="{t["ink"]}" text-anchor="middle">{NAME}</text>
<text class="rise-d" x="{WIDTH/2}" y="124" font-size="13" letter-spacing="3" fill="{t["cyan"]}" text-anchor="middle">{SUBTITLE}</text>
<text x="{WIDTH/2}" y="{dim_y-10}" font-size="11" letter-spacing="0.5" fill="{t["ink_dim"]}" text-anchor="middle">{CALLOUT}</text>
<line class="draw" x1="{dim_x1}" y1="{dim_y}" x2="{dim_x2}" y2="{dim_y}" stroke="{t["ink_dim"]}" stroke-width="1"/>
<line class="tick" x1="{dim_x1}" y1="{dim_y-5}" x2="{dim_x1}" y2="{dim_y+5}" stroke="{t["ink_dim"]}" stroke-width="1"/>
<line class="tick" x1="{dim_x2}" y1="{dim_y-5}" x2="{dim_x2}" y2="{dim_y+5}" stroke="{t["ink_dim"]}" stroke-width="1"/>
</svg>'''
    return svg


def main():
    outdir = "assets"
    os.makedirs(outdir, exist_ok=True)
    for theme in ("dark", "light"):
        svg = render(theme)
        path = os.path.join(outdir, f"blueprint-{theme}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
