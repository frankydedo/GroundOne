"""Outline the stroked G (width 116, round caps/joins) into one filled SVG path."""
import sys
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

C, R, HALF = (512.0, 512.0), 280.0, 58.0
a0, a1 = -np.pi / 4, -2 * np.pi          # arc from -45° counter-clockwise to 0°
t = np.linspace(a0, a1, 720)
arc = LineString(np.c_[C[0] + R * np.cos(t), C[1] + R * np.sin(t)])
tick = LineString([(792.0, 512.0), (573.7, 628.1), (503.0, 557.4)])
shape = unary_union([arc.buffer(HALF, quad_segs=32), tick.buffer(HALF, quad_segs=32)]).simplify(0.15)


def ring(coords):
    pts = list(coords)[:-1]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


d = " ".join([ring(shape.exterior.coords)] + [ring(i.coords) for i in shape.interiors])
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
       f'<path d="{d}" fill="#FFFFFF" fill-rule="evenodd"/></svg>\n')
for out in sys.argv[1:]:
    open(out, "w").write(svg)
print(shape.geom_type, len(shape.interiors), len(svg))
