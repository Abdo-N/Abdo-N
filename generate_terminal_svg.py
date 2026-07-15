#!/usr/bin/env python3
"""
Generates an animated "typing terminal" SVG for a GitHub profile README.
Renders two themes (dark/light) so the README's <picture> tag can pick
the right one via prefers-color-scheme.

Run locally:
    python3 generate_terminal_svg.py

Run in CI (pulls live GitHub stats):
    GITHUB_TOKEN=xxx python3 generate_terminal_svg.py --live
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    import urllib.request
except ImportError:
    urllib = None

# ---------------------------------------------------------------------------
# EDIT THIS: your content. Each tuple is (label, value, color_class).
# color_class options: "cmd" (prompt), "key" (green label), "val" (white text),
# "accent" (cyan), "dim" (gray), "blank" (empty line)
# ---------------------------------------------------------------------------
GITHUB_USER = "Abdo-N"

def build_lines(stats):
    L = []
    # --- header (full width) ---
    L.append(("cmd", "~", "neofetch --profile", 0))
    L.append(("blank", "", "", 0))
    L.append(("title", "", "abdelrahman nader", 0))
    L.append(("kv", "Role", "CSEN Student @ GUC", 0))
    L.append(("kv", "Edu", "B.Sc. Computer Engineering, GUC", 0))
    L.append(("kv", "Focus", "Full-Stack (MERN) · CLI Tools · Data Analysis", 0))
    L.append(("blank", "", "", 0))

    # --- left column ---
    L.append(("section", "", "~/stack", 1))
    L.append(("kv", "Lang", "Java · Python · C · JS · TS · SQL", 1))
    L.append(("kv", "Also", "Haskell", 1))
    L.append(("kv", "Web", "React · Express · Node.js · MongoDB", 1))
    L.append(("kv", "Tools", "Git · Linux · Pandas · NumPy · SQLite", 1))
    L.append(("kv", "", "JavaFX · Unity", 1))

    # --- right column ---
    L.append(("section", "", "~/experience", 2))
    L.append(("kv", "IEEE", "SE Committee, GUC Student Branch (2025-)", 2))
    L.append(("kv", "VectorGSC", "Game Dev, Vector Game Studio Club (2024)", 2))
    L.append(("section", "", "~/projects", 2))
    L.append(("kv", "DoorDash", "Java/JavaFX board game, MVC", 2))
    L.append(("kv", "ReservationEngine", "Haskell + Prolog scheduler", 2))
    L.append(("kv", "CSV-Parser-Analyzer", "Java CLI, sort/filter/export", 2))
    L.append(("kv", "Movie_recommender", "Python/Pandas/SQLite CLI", 2))
    L.append(("kv", "MovieRecommender-MERN", "in progress: MERN rewrite", 2))

    # --- footer (full width) ---
    L.append(("section", "", "~/reach", 3))
    L.append(("kv", "GitHub", "github.com/Abdo-N", 3))
    L.append(("kv", "LinkedIn", "linkedin.com/in/abdelrahman-morad", 3))
    L.append(("blank", "", "", 3))
    L.append(("cmd", "~", "echo $STATUS", 3))
    L.append(("val", "", "open to software engineering / data internships", 3))
    L.append(("footer", "", f"last updated {stats.get('updated', '')}", 3))
    return L


def fetch_live_stats():
    stats = {"public_repos": "-", "followers": "-"}
    if urllib is None:
        return stats
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{GITHUB_USER}",
            headers={"Accept": "application/vnd.github+json"},
        )
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            stats["public_repos"] = data.get("public_repos", "-")
            stats["followers"] = data.get("followers", "-")
    except Exception as e:
        print(f"warning: could not fetch live stats ({e})", file=sys.stderr)
    return stats


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
THEMES = {
    "dark": {
        "bg": "#0d1117", "chrome": "#161b22", "border": "#30363d",
        "cmd": "#58a6ff", "key": "#3fb950", "val": "#c9d1d9",
        "accent": "#79c0ff", "dim": "#8b949e", "title": "#f0f6fc",
        "dot1": "#ff5f56", "dot2": "#ffbd2e", "dot3": "#27c93f",
    },
    "light": {
        "bg": "#ffffff", "chrome": "#f6f8fa", "border": "#d0d7de",
        "cmd": "#0969da", "key": "#116329", "val": "#24292f",
        "accent": "#0550ae", "dim": "#57606a", "title": "#1f2328",
        "dot1": "#ff5f56", "dot2": "#ffbd2e", "dot3": "#27c93f",
    },
}

FONT = "SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"
CHAR_W = 8.6          # approx monospace advance width at 14px
LINE_H = 21
PAD_X = 20
PAD_TOP = 46
COL_GAP = 36

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def kv_label(label):
    if not label:
        return "         "
    return label.ljust(10) if len(label) < 10 else label + " "


def line_text(kind, label, value):
    if kind == "cmd":
        return f"{label} $ {value}"
    if kind == "kv":
        return f"{kv_label(label)}{value}"
    return value


def render_svg(lines, theme_name):
    t = THEMES[theme_name]

    header = [l for l in lines if l[3] == 0]
    left = [l for l in lines if l[3] == 1]
    right = [l for l in lines if l[3] == 2]
    footer = [l for l in lines if l[3] == 3]

    left_w = max(len(line_text(k, lb, v)) for k, lb, v, c in left) * CHAR_W
    right_w = max(len(line_text(k, lb, v)) for k, lb, v, c in right) * CHAR_W
    header_w = max(len(line_text(k, lb, v)) for k, lb, v, c in header) * CHAR_W
    footer_w = max(len(line_text(k, lb, v)) for k, lb, v, c in footer) * CHAR_W

    col_body_w = max(left_w, header_w, footer_w) if False else None
    width = int(max(header_w, footer_w, left_w + right_w + COL_GAP) + PAD_X * 2 + 20)
    width = max(width, 780)

    right_x = PAD_X + int(left_w) + COL_GAP
    col_rows = max(len(left), len(right))

    header_h = len(header) * LINE_H
    cols_h = col_rows * LINE_H
    footer_h = len(footer) * LINE_H
    height = PAD_TOP + header_h + cols_h + footer_h + 30

    body = []
    delay = 0.0
    last_end_x, last_y = PAD_X, PAD_TOP

    def emit(kind, label, value, x, y):
        nonlocal delay, last_end_x, last_y
        if kind == "blank":
            return
        text = line_text(kind, label, value)
        color = {
            "cmd": t["cmd"], "title": t["title"], "section": t["accent"],
            "kv": t["val"], "val": t["key"], "footer": t["dim"],
        }.get(kind, t["val"])

        nchars = max(len(text), 1)
        dur = max(nchars * 0.013, 0.06)
        # SMIL opacity fade-in per line: this is well supported when the SVG
        # is embedded via <img>, and unlike a clip-path character reveal it
        # can never freeze on a half-typed word if paused mid-animation.
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.2f}s" dur="0.1s" fill="freeze"/>'
        )

        if kind == "kv":
            key_part = esc(kv_label(label))
            val_part = esc(value)
            span = (
                f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="14">'
                f'<tspan fill="{t["key"]}">{key_part}</tspan>'
                f'<tspan fill="{t["val"]}">{val_part}</tspan></text>'
            )
        else:
            span = (
                f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="14" '
                f'fill="{color}">{esc(text)}</text>'
            )
        body.append(f'<g opacity="0">{span}{anim}</g>')
        delay += dur
        last_end_x = x + nchars * CHAR_W
        last_y = y

    y = PAD_TOP
    for kind, label, value, col in header:
        emit(kind, label, value, PAD_X, y)
        y += LINE_H
    header_bottom = y

    ly = header_bottom
    for kind, label, value, col in left:
        emit(kind, label, value, PAD_X, ly)
        ly += LINE_H

    ry = header_bottom
    for kind, label, value, col in right:
        emit(kind, label, value, right_x, ry)
        ry += LINE_H

    fy = header_bottom + col_rows * LINE_H
    for kind, label, value, col in footer:
        emit(kind, label, value, PAD_X, fy)
        fy += LINE_H

    cursor_delay = delay

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text{{font-family:{FONT};}}</style>
<rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>
<rect x="0" y="0" width="{width}" height="30" rx="10" fill="{t["chrome"]}"/>
<rect x="0" y="20" width="{width}" height="10" fill="{t["chrome"]}"/>
<circle cx="20" cy="15" r="6" fill="{t["dot1"]}"/>
<circle cx="40" cy="15" r="6" fill="{t["dot2"]}"/>
<circle cx="60" cy="15" r="6" fill="{t["dot3"]}"/>
<text x="{width/2}" y="19" font-family="{FONT}" font-size="12" fill="{t["dim"]}" text-anchor="middle">Abdo-N</text>
{''.join(body)}
<rect x="{last_end_x + 2:.1f}" y="{last_y - 11}" width="8" height="14" fill="{t["val"]}" opacity="0">
<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.001;0.001;0.5;0.5;1" dur="1s" begin="{cursor_delay:.2f}s" repeatCount="indefinite"/>
</rect>
</svg>'''
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="fetch live GitHub stats")
    ap.add_argument("--outdir", default="assets")
    args = ap.parse_args()

    stats = fetch_live_stats() if args.live else {"public_repos": "-", "followers": "-"}
    stats["updated"] = datetime.now(timezone.utc).strftime("%d %b %Y")

    lines = build_lines(stats)
    os.makedirs(args.outdir, exist_ok=True)
    for theme in ("dark", "light"):
        svg = render_svg(lines, theme)
        path = os.path.join(args.outdir, f"terminal-{theme}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
