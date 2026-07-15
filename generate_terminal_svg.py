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
    L.append(("cmd", "~", "neofetch --profile"))
    L.append(("blank", "", ""))
    L.append(("title", "", "abdelrahman nader"))
    L.append(("kv", "Role", "CSEN Student @ GUC"))
    L.append(("kv", "Edu", "B.Sc. Computer Engineering, German University in Cairo"))
    L.append(("kv", "Focus", "Full-Stack (MERN) · CLI Tools · Data Analysis"))
    L.append(("blank", "", ""))
    L.append(("section", "", "~/stack"))
    L.append(("kv", "Lang", "Java | Python | C | JavaScript | TypeScript | SQL"))
    L.append(("kv", "Also", "Haskell | Prolog"))
    L.append(("kv", "Web", "React | Express.js | Node.js | MongoDB"))
    L.append(("kv", "Tools", "Git | Linux | Pandas | NumPy | SQLite | JavaFX | Unity"))
    L.append(("blank", "", ""))
    L.append(("section", "", "~/experience"))
    L.append(("kv", "IEEE", "SE Committee Member, GUC Student Branch (2025-)"))
    L.append(("kv", "VectorGSC", "Game Dev, Vector Game Studio Club (2024)"))
    L.append(("blank", "", ""))
    L.append(("section", "", "~/projects"))
    L.append(("kv", "DoorDash", "Java/JavaFX board game, MVC, CSV-driven content"))
    L.append(("kv", "ReservationEngine", "Haskell + Prolog constraint-based scheduler"))
    L.append(("kv", "CSV-Parser-Analyzer", "Java CLI, sort/filter/stats/export"))
    L.append(("kv", "Movie_recommender", "Python/Pandas/SQLite CLI, MovieLens data"))
    L.append(("kv", "MovieRecommender-MERN", "in progress: full MERN rewrite"))
    L.append(("blank", "", ""))
    L.append(("section", "", "~/stats"))
    L.append(("kv", "Repos", str(stats.get("public_repos", "-"))))
    L.append(("kv", "Followers", str(stats.get("followers", "-"))))
    L.append(("blank", "", ""))
    L.append(("section", "", "~/reach"))
    L.append(("kv", "GitHub", "github.com/Abdo-N"))
    L.append(("kv", "LinkedIn", "linkedin.com/in/abdelrahman-morad"))
    L.append(("blank", "", ""))
    L.append(("cmd", "~", "echo $STATUS"))
    L.append(("val", "", "open to software engineering / data internships"))
    L.append(("footer", "", f"last updated {stats.get('updated', '')}"))
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
CHAR_W = 8.4          # approx monospace advance width at 14px
LINE_H = 21
PAD_X = 20
PAD_TOP = 46
WIDTH = 720

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_svg(lines, theme_name):
    t = THEMES[theme_name]
    height = PAD_TOP + LINE_H * len(lines) + 24

    body_lines = []
    delay = 0.0
    total_chars = 0

    style_rules = []
    for i, (kind, label, value) in enumerate(lines):
        y = PAD_TOP + i * LINE_H
        if kind == "blank":
            continue

        if kind == "cmd":
            text = f"{label} $ {value}"
            color = t["cmd"]
        elif kind == "title":
            text = value
            color = t["title"]
        elif kind == "section":
            text = value
            color = t["accent"]
        elif kind == "kv":
            text = f"{label:<10}{value}"
            color = t["val"]
        elif kind == "val":
            text = value
            color = t["key"]
        elif kind == "footer":
            text = value
            color = t["dim"]
        else:
            text = value
            color = t["val"]

        nchars = max(len(text), 1)
        dur = max(nchars * 0.028, 0.12)
        cls = f"tl{i}"
        # steps() reveal via clip-path width animation, discrete per character
        style_rules.append(
            f".{cls}{{clip-path:inset(0 100% 0 0);"
            f"animation:reveal{i} {dur:.2f}s steps({nchars},end) forwards;"
            f"animation-delay:{delay:.2f}s;}}"
        )
        style_rules.append(f"@keyframes reveal{i}{{to{{clip-path:inset(0 0 0 0);}}}}")

        if kind == "kv":
            key_part = esc(label.ljust(10))
            val_part = esc(value)
            span = (
                f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="14">'
                f'<tspan fill="{t["key"]}">{key_part}</tspan>'
                f'<tspan fill="{t["val"]}">{val_part}</tspan></text>'
            )
        else:
            span = (
                f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="14" '
                f'fill="{color}">{esc(text)}</text>'
            )

        body_lines.append(f'<g class="{cls}">{span}</g>')
        delay += dur * 0.55
        total_chars += nchars

    cursor_delay = delay + 0.1

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
<style>
text{{font-family:{FONT};}}
.cursor{{fill:{t["val"]};opacity:0;animation:blink 1s steps(1) {cursor_delay:.2f}s infinite;}}
@keyframes blink{{0%,49%{{opacity:1;}}50%,100%{{opacity:0;}}}}
{''.join(style_rules)}
</style>
<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>
<rect x="0" y="0" width="{WIDTH}" height="30" rx="10" fill="{t["chrome"]}"/>
<rect x="0" y="20" width="{WIDTH}" height="10" fill="{t["chrome"]}"/>
<circle cx="20" cy="15" r="6" fill="{t["dot1"]}"/>
<circle cx="40" cy="15" r="6" fill="{t["dot2"]}"/>
<circle cx="60" cy="15" r="6" fill="{t["dot3"]}"/>
<text x="{WIDTH/2}" y="19" font-family="{FONT}" font-size="12" fill="{t["dim"]}" text-anchor="middle">abdo@guc: ~</text>
{''.join(body_lines)}
<rect class="cursor" x="{PAD_X}" y="{PAD_TOP + (len([l for l in lines if l[0]!='blank'])-1)*LINE_H - 11}" width="8" height="14"/>
</svg>'''
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="fetch live GitHub stats")
    ap.add_argument("--outdir", default="assets")
    args = ap.parse_args()

    stats = fetch_live_stats() if args.live else {"public_repos": "-", "followers": "-"}
    stats["updated"] = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

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
