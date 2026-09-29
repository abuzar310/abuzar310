#!/usr/bin/env python3
"""Terminal profile.sh --live banner with a dithered GitHub-avatar portrait.

Layout matches emmi-lili: VISUAL.MAP (300×340 / 1-bit) on the left,
SYSTEM.INFO rows on the right. Portrait source is the public GitHub avatar.
Pillow only — no numpy/scipy.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/avatar.jpg"
ASSETS = ROOT / "assets"

W, H = 1180, 610
GRID_W, GRID_H = 300, 340
# Portrait lattice origin inside the VISUAL.MAP frame (same as emmi-lili).
OX, OY = 74, 154

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
        "panel2": "#1c1917",
        "line": "#3f2a14",
        "muted": "#a8a29e",
        "text": "#f5f0e8",
        "portrait": "#f5a524",
        "chrome": "#fbbf24",
        "accent": "#f5a524",
        "shadow": "#0a0908",
    },
    "light": {
        "bg": "#faf9f7",
        "panel": "#ffffff",
        "panel2": "#f5f0e8",
        "line": "#e7d5b8",
        "muted": "#78716c",
        "text": "#1c1917",
        "portrait": "#92400e",
        "chrome": "#b45309",
        "accent": "#b45309",
        "shadow": "#d6c4a8",
    },
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def floyd_steinberg(gray: list[list[int]]) -> list[list[bool]]:
    """Serpentine 1-bit Floyd–Steinberg. True = lit pixel."""
    height = len(gray)
    width = len(gray[0])
    work = [[p / 255.0 for p in row] for row in gray]
    out = [[False] * width for _ in range(height)]
    for y in range(height):
        left_to_right = y % 2 == 0
        xs = range(width) if left_to_right else range(width - 1, -1, -1)
        direction = 1 if left_to_right else -1
        for x in xs:
            old = work[y][x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y][x] = bool(new)
            err = old - new
            nx = x + direction
            if 0 <= nx < width:
                work[y][nx] += err * 7 / 16
            if y + 1 < height:
                if 0 <= x - direction < width:
                    work[y + 1][x - direction] += err * 3 / 16
                work[y + 1][x] += err * 5 / 16
                if 0 <= nx < width:
                    work[y + 1][nx] += err * 1 / 16
    return out


def prepare_portrait() -> Image.Image:
    """Cover-crop the square GitHub avatar into the 300×340 VISUAL.MAP lattice."""
    src = ImageOps.exif_transpose(Image.open(SOURCE)).convert("RGB")
    # Scale to cover, then center-crop. Face/body stay; chair sides trim a little.
    scale = max(GRID_W / src.width, GRID_H / src.height)
    resized = src.resize(
        (max(1, round(src.width * scale)), max(1, round(src.height * scale))),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - GRID_W) // 2
    top = max(0, (resized.height - GRID_H) // 2 - 8)  # slight lift so the face sits higher
    crop = resized.crop((left, top, left + GRID_W, top + GRID_H))
    gray = ImageOps.grayscale(crop)
    gray = ImageOps.equalize(gray)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=175, threshold=1))
    return gray


def portrait_points() -> list[tuple[int, int]]:
    gray = prepare_portrait()
    pixels = list(gray.get_flattened_data())
    grid = [pixels[y * GRID_W : (y + 1) * GRID_W] for y in range(GRID_H)]
    bits = floyd_steinberg(grid)
    # Cream cat on a dark chair: keep lit pixels so the subject is the dots.
    return [(OX + x, OY + y) for y, row in enumerate(bits) for x, lit in enumerate(row) if lit]


def point_path(points: list[tuple[int, int]]) -> str:
    unique = sorted(set(points), key=lambda p: (p[1], p[0]))
    chunks: list[str] = []
    i = 0
    while i < len(unique):
        x0, y = unique[i]
        x1 = x0
        i += 1
        while i < len(unique) and unique[i][1] == y and unique[i][0] <= x1 + 1:
            x1 = unique[i][0]
            i += 1
        chunks.append(f"M{x0} {y}h{x1 - x0 + 1}")
    return "".join(chunks)


def text_width(text: str, font_size: float) -> float:
    return len(text) * font_size * 0.605


def dotted_leader(x1: float, x2: float, y: float) -> str:
    if x2 <= x1:
        return ""
    return "".join(f"M{x:.0f} {y:.0f}h1" for x in range(int(x1), int(x2), 5))


def render(theme: str, points: list[tuple[int, int]]) -> str:
    t = THEMES[theme]
    path = point_path(points)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        '<title id="title">Mohammed Abuzar — profile.sh --live</title>',
        '<desc id="desc">Terminal profile with a dithered GitHub-avatar portrait.</desc>',
        "<defs>",
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">'
        f'<feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="{t["shadow"]}" '
        'flood-opacity=".28"/></filter>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%">'
        f'<feGaussianBlur stdDeviation="3" result="b"/><feFlood flood-color="{t["chrome"]}" '
        'flood-opacity=".35"/><feComposite in2="b" operator="in"/>'
        '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<clipPath id="visualClip"><rect x="49" y="124" width="390" height="414" rx="3"/></clipPath>',
        "</defs>",
        f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>',
        f'<rect x="13" y="13" width="1154" height="584" rx="13" fill="{t["panel"]}" '
        f'stroke="{t["line"]}" filter="url(#shadow)"/>',
        f'<path d="M13 62H1167" stroke="{t["line"]}"/>',
        '<circle cx="38" cy="38" r="6" fill="#FF5F57"/>'
        '<circle cx="59" cy="38" r="6" fill="#FEBC2E"/>'
        '<circle cx="80" cy="38" r="6" fill="#28C840"/>',
        f'<text x="590" y="43" text-anchor="middle" fill="{t["muted"]}" '
        'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" '
        'letter-spacing=".4">profile.sh --live</text>',
        f'<rect x="35" y="88" width="418" height="472" rx="6" fill="{t["panel2"]}" '
        f'stroke="{t["line"]}"/>',
        f'<path d="M35 124H453" stroke="{t["line"]}"/>',
        f'<text x="49" y="111" fill="{t["chrome"]}" '
        'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" '
        'font-weight="700" letter-spacing="1.2">VISUAL.MAP</text>',
        f'<text x="438" y="111" text-anchor="end" fill="{t["muted"]}" '
        'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">'
        "300×340 / 1-BIT</text>",
        f'<path d="M49 141h12M49 141v12M439 141h-12M439 141v12M49 539h12M49 539v-12'
        f'M439 539h-12M439 539v-12" fill="none" stroke="{t["chrome"]}" opacity=".55"/>',
        '<g clip-path="url(#visualClip)" shape-rendering="crispEdges">',
        # Static 1-bit face so GitHub's first-frame raster still shows the avatar.
        f'<path d="{path}" fill="none" stroke="{t["portrait"]}" stroke-width="1" '
        'opacity=".94"/>',
    ]
    parts.extend(
        [
            "</g>",
            f'<text x="58" y="551" fill="{t["muted"]}" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10">'
            f"PTS {len(points):05d} · FS/SERPENTINE · GH AVATAR</text>",
            f'<rect x="474" y="88" width="672" height="472" rx="6" fill="{t["panel2"]}" '
            f'stroke="{t["line"]}"/>',
            f'<path d="M474 124H1146" stroke="{t["line"]}"/>',
            f'<text x="490" y="111" fill="{t["chrome"]}" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" '
            'font-weight="700" letter-spacing="1.2">SYSTEM.INFO</text>',
            '<g filter="url(#glow)"><circle cx="888" cy="106" r="4" fill="#FF4D5A">'
            '<animate attributeName="opacity" values="1;.3;1" dur="1.6s" '
            'repeatCount="indefinite"/></circle></g>',
            '<text x="900" y="111" fill="#FF4D5A" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="12" '
            'font-weight="700">LIVE</text>',
            f'<rect x="960" y="94" width="168" height="24" rx="12" fill="{t["chrome"]}" '
            f'opacity=".16" stroke="{t["chrome"]}"/>',
            f'<text x="1044" y="111" text-anchor="middle" fill="{t["chrome"]}" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="14" '
            'font-weight="700">@abuzar310</text>',
        ]
    )

    value_right = 1127.0
    row_y = 158.0
    for label, value in ROWS:
        value_len = text_width(value, 14)
        label_len = text_width(label, 14)
        leader_start = 491 + label_len + 12
        leader_end = value_right - value_len - 12
        parts.extend(
            [
                f'<text x="491" y="{row_y:.0f}" fill="{t["muted"]}" '
                'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="14">'
                f"{esc(label)}</text>",
                f'<path d="{dotted_leader(leader_start, leader_end, row_y - 4)}" '
                f'fill="none" stroke="{t["line"]}" stroke-width="1" '
                'shape-rendering="crispEdges"/>',
                f'<text x="{value_right:.0f}" y="{row_y:.0f}" text-anchor="end" '
                f'fill="{t["text"]}" font-family="ui-monospace,SFMono-Regular,Consolas,'
                f'monospace" font-size="14" textLength="{value_len:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{esc(value)}</text>',
            ]
        )
        row_y += 26

    parts.extend(
        [
            f'<path d="M490 530H1130" stroke="{t["line"]}"/>',
            f'<text x="491" y="548" fill="{t["accent"]}" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">'
            "● ALL SYSTEMS NOMINAL</text>",
            f'<text x="1128" y="548" text-anchor="end" fill="{t["muted"]}" '
            'font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">'
            "UTC+5:30 · INDIA NODE</text>",
            "</svg>",
        ]
    )
    return "".join(parts)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing GitHub avatar: {SOURCE}")
    ASSETS.mkdir(parents=True, exist_ok=True)
    points = portrait_points()
    if len(points) < 2000:
        raise SystemExit(f"portrait too sparse: {len(points)} dots")
    for theme in ("dark", "light"):
        dest = ASSETS / f"banner-{theme}.svg"
        svg = render(theme, points)
        dest.write_text(svg, encoding="utf-8")
        print(f"wrote {dest}  ({dest.stat().st_size / 1024:.1f} KiB, {len(points)} dots)")


if __name__ == "__main__":
    main()
