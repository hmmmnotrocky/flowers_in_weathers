#!/usr/bin/env python3
"""
Generate a 180×180 PNG icon from the Flower.astro-style flower:
one flower, 5 petals, no stem, on website background color (#ffdab9).
Run from project root: python scripts/make_apple_touch_icon.py
Requires: pip install cairosvg
"""

import math
import os

# Website background (peach) at 100% opacity
BG_COLOR = "#ffdab9"

# Output path (from project root)
OUTPUT_PATH = "public/apple-touch-icon.png"
SIZE = 180


def polar(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """Same as Flower.astro: angle 0 = up, clockwise."""
    rad = (angle_deg - 90) * math.pi / 180
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def make_petal_path(cx: float, cy: float, petal_width: float, angle: float) -> str:
    """One petal as cubic Bezier (same as Flower.astro)."""
    c1 = polar(cx, cy, petal_width, angle - 20)
    c2 = polar(cx, cy, petal_width, angle + 20)
    return (
        f"M {cx} {cy} "
        f"C {c1[0]} {c1[1]} {c2[0]} {c2[1]} {cx} {cy}"
    )


def hsl_to_hex(h: float, s_pct: float, l_pct: float) -> str:
    """HSL (0-360, 0-100, 0-100) to #rrggbb for reliable PNG rendering."""
    s = s_pct / 100.0
    l = l_pct / 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return "#{:02x}{:02x}{:02x}".format(
        int(round((r + m) * 255)),
        int(round((g + m) * 255)),
        int(round((b + m) * 255)),
    )


def main() -> None:
    # One flower, 5 petals, centered in 180×180 — larger flower
    cx, cy = SIZE / 2, SIZE / 2
    petals = 8
    petal_width = 80  # larger so flower fills more of the icon
    center_radius = petal_width * 0.14  # larger centre circle

    # Orange hue for petals; center circle is hue - 20
    hue_flower = 30
    hue_center = hue_flower - 20  # 10, more yellow-orange
    petal_color = hsl_to_hex(hue_flower, 70, 50)
    center_color = hsl_to_hex(hue_center, 65, 45)

    segment = 360 / petals
    starting_angle = 0
    paths = []
    for j in range(petals):
        angle = segment * j + starting_angle
        paths.append(make_petal_path(cx, cy, petal_width, angle))

    path_d = " ".join(paths)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <rect width="100%" height="100%" fill="{BG_COLOR}"/>
  <g fill="{petal_color}" stroke="{petal_color}" stroke-width="2">
    {''.join(f'<path d="{p}"/>' for p in paths)}
  </g>
  <circle cx="{cx}" cy="{cy}" r="{center_radius}" fill="{center_color}"/>
</svg>
'''

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    try:
        import cairosvg
        cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            write_to=OUTPUT_PATH,
            output_width=SIZE,
            output_height=SIZE,
        )
        print(f"Wrote {OUTPUT_PATH}")
    except ImportError:
        svg_path = OUTPUT_PATH.replace(".png", ".svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Wrote {svg_path} (cairosvg not installed; run: pip install cairosvg, then re-run to get PNG)")
        print("Or convert manually: cairosvg -o public/apple-touch-icon.png -W 180 -H 180 public/apple-touch-icon.svg")


if __name__ == "__main__":
    main()
