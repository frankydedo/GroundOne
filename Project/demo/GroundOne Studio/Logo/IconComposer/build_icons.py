"""Build Icon Composer documents (.icon) for the GroundOne Studio glass G.

usage: build_icons.py OUT_DIR [palette ...]
"indigo" (the app icon since 2026-10-26) uses a smooth three-stop gradient in the app's blue family and a clearer glass
G (see SMOOTH and glass_group_v2); the other palettes are the earlier colour-mesh variants.
Each palette gets OUT_DIR/GroundOne-<palette>.icon with two groups:
the glass G on top, the colour-mesh background below (PNG rendered by Quick Look).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PALETTES = {
    "cool":        (["#2F6BFF", "#7B3CFF", "#FF2D6F", "#FF8A1F"], ["#36C4FF", "#FF7AD9", "#FF4FA8", "#FFC93D"]),
    "warm":        (["#4F5BFF", "#B43CF5", "#FF2D6F", "#FF9A2A"], ["#FFD84D", "#FF5FB0", "#3D7BFF", "#7B3CFF"]),
    "lagoon":      (["#00C2FF", "#0A84FF", "#2B4BFF", "#6A3CFF"], ["#5CFFE0", "#7CC4FF", "#3D5BFF", "#B04BFF"]),
    "ultraviolet": (["#1A2BFF", "#5B21FF", "#9B1CFF", "#FF2DB4"], ["#3DA2FF", "#C04BFF", "#6A00FF", "#FF5FD1"]),
    "tangerine":   (["#FFB800", "#FF7A00", "#FF3D57", "#E0257A"], ["#FFE45C", "#FF9E3D", "#FF5F7A", "#C2338F"]),
    "ember":       (["#FF4D2E", "#FF1F6B", "#B0179E", "#5B1FB8"], ["#FFB02E", "#FF4F8B", "#FF3D3D", "#7B2BFF"]),
    "citrus":      (["#C6F432", "#38D97A", "#00BFA5", "#0A84FF"], ["#FFF35C", "#7CFF6B", "#00E0C6", "#2F6BFF"]),
    "pastel":      (["#7FD8FF", "#8FA8FF", "#E6A2FF", "#FFC2A8"], ["#5CD6FF", "#B39CFF", "#FF9EDB", "#FFD36B"]),
}

# one colour family around the app's GroundOne blue (#2A78D6): indigo with a hint of violet -> blue -> cyan
SMOOTH = {
    "indigo": (["#24206E", "#2F4FC9", "#2A8FE0"], "#7A6CFF", "#5FD2FF"),
}

# the G as a filled outline (made by outline_g.py), so a layer fill colours it correctly
GLYPH_SVG = (Path(__file__).with_name("G.svg")).read_text()


def scene_svg(stops, orbs):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip((0, 0.45, 0.78, 1), stops))
    spots = ((230, 210, 260, 0.85), (870, 220, 220, 0.7), (260, 860, 240, 0.75), (850, 840, 250, 0.85))
    c = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" fill-opacity="{a}"/>'
                for (x, y, r, a), col in zip(spots, orbs))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
        f'<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1">{s}</linearGradient>'
        '<filter id="o" filterUnits="userSpaceOnUse" x="-300" y="-300" width="1624" height="1624">'
        '<feGaussianBlur stdDeviation="55"/></filter></defs>'
        f'<rect width="1024" height="1024" fill="url(#b)"/><g filter="url(#o)">{c}</g></svg>\n'
    )


def scene_smooth(stops, glow_tl, glow_br):
    """Diagonal three-stop gradient with two soft glows (top-left, bottom-right) of the same family."""
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip((0, 0.5, 1), stops))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><defs>'
            f'<linearGradient id="b" x1="0.1" y1="0" x2="0.9" y2="1">{s}</linearGradient>'
            f'<radialGradient id="t" cx="0.18" cy="0.12" r="0.6"><stop offset="0" stop-color="{glow_tl}" stop-opacity="0.55"/>'
            f'<stop offset="1" stop-color="{glow_tl}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="r" cx="0.88" cy="0.92" r="0.62"><stop offset="0" stop-color="{glow_br}" stop-opacity="0.75"/>'
            f'<stop offset="1" stop-color="{glow_br}" stop-opacity="0"/></radialGradient>'
            '</defs><rect width="1024" height="1024" fill="url(#b)"/><rect width="1024" height="1024" fill="url(#t)"/>'
            '<rect width="1024" height="1024" fill="url(#r)"/></svg>\n')


def glass_group_v2(glyph_scale=0.86):
    """Clearer liquid glass: full-opacity glass layer with a white fill that fades towards the bottom (the background
    shows through by refraction), coloured shadow, light blur behind; a stronger fill in dark mode keeps it legible."""
    grad = lambda a, b: {"linear-gradient": [f"display-p3:1,1,1,{a}", f"display-p3:1,1,1,{b}"],  # noqa: E731
                         "orientation": {"start": {"x": 0.5, "y": 1.0}, "stop": {"x": 0.5, "y": 0}}}
    return {
        "layers": [{"glass": True, "image-name": "G.svg", "name": "G", "opacity": 1.0,
                    "position": {"scale": glyph_scale, "translation-in-points": [0, 0]},
                    "fill-specializations": [{"value": grad(0.40, 0.95)},
                                             {"appearance": "dark", "value": grad(0.65, 1.0)}]}],
        "specular": True, "lighting": "individual", "blur-material": 0.35,
        "shadow": {"kind": "layer-color", "opacity": 0.65},
        "translucency": {"enabled": True, "value": 0.38},
    }


def render_png(svg_text, dest):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "bg.svg"
        src.write_text(svg_text)
        subprocess.run(["qlmanage", "-t", "-s", "1024", "-o", tmp, str(src)],
                       check=True, capture_output=True)
        Path(tmp, "bg.svg.png").replace(dest)


def icon_json(translucency, glyph_scale):
    return {
        "fill": {"solid": "display-p3:1.00000,1.00000,1.00000,1.00000"},
        "groups": [
            {
                "layers": [{
                    "glass": True,
                    "image-name": "G.svg",
                    "name": "G",
                    "position": {"scale": glyph_scale, "translation-in-points": [0, 0]},
                }],
                "shadow": {"kind": "neutral", "opacity": 0.5},
                "translucency": {"enabled": True, "value": translucency},
                "specular": True,
            },
            {
                "layers": [{"glass": False, "image-name": "Background.png", "name": "Background"}],
            },
        ],
        "supported-platforms": {"circles": ["watchOS"], "squares": "shared"},
    }


def build(out_dir, name, stops, orbs, translucency=0.7, glyph_scale=0.86):
    doc = out_dir / f"{name}.icon"
    assets = doc / "Assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "G.svg").write_text(GLYPH_SVG)
    render_png(scene_svg(stops, orbs), assets / "Background.png")
    (doc / "icon.json").write_text(json.dumps(icon_json(translucency, glyph_scale), indent=2) + "\n")
    return doc


def build_smooth(out_dir, name, stops, glow_tl, glow_br):
    doc = out_dir / f"{name}.icon"
    assets = doc / "Assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "G.svg").write_text(GLYPH_SVG)
    render_png(scene_smooth(stops, glow_tl, glow_br), assets / "Background.png")
    j = icon_json(0.7, 0.86)
    j["groups"][0] = glass_group_v2()
    (doc / "icon.json").write_text(json.dumps(j, indent=2) + "\n")
    return doc


if __name__ == "__main__":
    out = Path(sys.argv[1])
    names = sys.argv[2:] or list(PALETTES) + list(SMOOTH)
    for n in names:
        if n in SMOOTH:
            print(build_smooth(out, f"GroundOne-{n}", *SMOOTH[n]))
        else:
            stops, orbs = PALETTES[n]
            print(build(out, f"GroundOne-{n}", stops, orbs))
