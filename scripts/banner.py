#!/usr/bin/env python3
"""Terminal-style profile.sh --live banner. Stdlib only."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

ROWS = [
    ("Subject", "Mohammed Abuzar"),
    ("Role", "Full Stack Developer · Systems Engineer"),
    ("Origin", "India"),
    ("Focus", "Web apps · business tooling · open source"),
    ("Status", "Building + Shipping"),
    ("ToolChain", "Cursor · Git · Vercel"),
    ("Core.Lang", "TypeScript · JavaScript · Dart · Python"),
    ("Core.Frontend", "React · Next.js · Tailwind"),
    ("Core.Backend", "Node · PostgreSQL · Supabase"),
    ("Core.Mobile", "Flutter · Android"),
    ("Grid.GitHub", "abuzar310"),
    ("Grid.X", "@AbuzarFiroz01"),
    ("Grid.Instagram", "@abuzaru1"),
]

THEMES = {
    "dark": {
        "bg": "#0c0b09",
        "panel": "#171512",
        "line": "#3f2a14",
        "muted": "#a8a29e",
        "text": "#f5f0e8",
        "accent": "#f5a524",
        "chrome": "#fbbf24",
        "dim": "#78716c",
    },
    "light": {
        "bg": "#faf9f7",
        "panel": "#ffffff",
        "line": "#e7d5b8",
        "muted": "#78716c",
        "text": "#1c1917",
        "accent": "#b45309",
        "chrome": "#92400e",
        "dim": "#a8a29e",
    },
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(theme: str) -> str:
    c = THEMES[theme]
    w, h = 1180, 520
    pad, row_h, key_w = 36, 28, 200
    top = 88
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="profile.sh --live" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{w}" height="{h}" rx="16" fill="{c["bg"]}"/>',
        f'<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="12" fill="{c["panel"]}" stroke="{c["line"]}"/>',
        f'<circle cx="44" cy="46" r="6" fill="#ef4444"/><circle cx="64" cy="46" r="6" fill="#f59e0b"/><circle cx="84" cy="46" r="6" fill="#22c55e"/>',
        f'<text x="110" y="51" font-size="13" fill="{c["dim"]}">abuzar310 — profile.sh --live</text>',
        f'<line x1="16" y1="68" x2="{w-16}" y2="68" stroke="{c["line"]}"/>',
        f'<text x="{pad}" y="{top}" font-size="15" fill="{c["chrome"]}">$ profile.sh --live</text>',
    ]
    for i, (key, val) in enumerate(ROWS):
        y = top + 28 + i * row_h
        delay = 0.08 * i
        parts.append(
            f'<text x="{pad}" y="{y}" font-size="14" fill="{c["muted"]}">{esc(key)}</text>'
            f'<text x="{pad+key_w}" y="{y}" font-size="14" fill="{c["text"]}">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay:.2f}s" fill="freeze"/>'
            f'{esc(val)}</text>'
        )
    parts.append(
        f'<text x="{pad}" y="{h-36}" font-size="12" fill="{c["accent"]}">'
        f'Build with copper · @abuzar310</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        dest = ASSETS / f"banner-{theme}.svg"
        dest.write_text(render(theme), encoding="utf-8")
        print(f"wrote {dest}")


if __name__ == "__main__":
    main()
