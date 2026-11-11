"""造坊 in the Bevel cut: strokes only at 0, 45 and 90 degrees, ends cut on the diagonal, joints opened by a hairline gap.

Coordinates are stroke centrelines in a 100-unit em. Each stroke is (points, start cut, end cut);
a box is ("box", x0, y0, x1, y1, corner cut).
"""
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from .geometry import stroke

BEVEL = {
    "坊": [
        ([(3, 40), (33, 40)], None, "/"),
        ([(19, 12), (19, 74)], "-", None),
        ([(3, 90), (33, 60)], "-", "|"),
        ([(63, 5), (73, 15)], "-", "-"),
        ([(41, 28), (93, 28)], None, "/"),
        ([(59, 28), (59, 68), (41, 86)], None, None),
        ([(69, 52), (87, 52), (87, 92)], "|", "/"),
    ],
    "造": [
        ([(9, 11), (19, 21)], "-", "-"),
        ([(3, 42), (21, 42), (21, 73), (37, 89), (95, 89)], None, "/"),
        ([(21, 73), (5, 89)], None, None),
        ([(55, 1), (43, 13)], "-", None),
        ([(43, 18), (88, 18)], None, "/"),
        ([(66, 2), (66, 34)], "-", None),
        ([(33, 34), (95, 34)], None, "/"),
        ("box", 43, 50, 85, 71, 11),
    ],
}


def _box(x0: float, y0: float, x1: float, y1: float, c: float, T: float) -> BaseGeometry:
    h = T / 2
    outer = Polygon([(x0 - h, y0 - h), (x1 + h, y0 - h), (x1 + h, y1 + h - c), (x1 + h - c, y1 + h), (x0 - h, y1 + h)])
    return outer.difference(box(x0 + h, y0 + h, x1 - h, y1 - h))


def bevel(ch: str, T: float = 12) -> BaseGeometry:
    """One character in the 100-unit em."""
    parts = [_box(*s[1:], T) if s[0] == "box" else stroke(s[0], s[1], s[2], T) for s in BEVEL[ch]]
    return unary_union(parts)


def placed(ch: str, size: float, x: float, y: float) -> BaseGeometry:
    """The character scaled to `size` with its em box's top-left at (x, y)."""
    return affinity.affine_transform(bevel(ch), [size / 100, 0, 0, size / 100, x, y])
