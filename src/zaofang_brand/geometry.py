"""Shared drawing primitives: Bevel strokes, cut boxes, SVG path data."""
from math import hypot

from shapely.geometry import LineString, Polygon, box
from shapely.geometry.base import BaseGeometry

DIRS = {"/": (1, -1), "\\": (1, 1), "-": (1, 0), "|": (0, 1)}

Pt = tuple[float, float]


def halfplane(p: Pt, cut: str, inward: Pt, L: float = 400) -> Polygon:
    """The half-plane bounded by the cut line through p, on the side `inward` points to."""
    cx, cy = DIRS[cut]
    n = hypot(cx, cy)
    cx, cy = cx / n, cy / n
    nx, ny = -cy, cx
    if nx * inward[0] + ny * inward[1] < 0:
        nx, ny = -nx, -ny
    a, b = (p[0] - cx * L, p[1] - cy * L), (p[0] + cx * L, p[1] + cy * L)
    return Polygon([a, b, (b[0] + nx * L, b[1] + ny * L), (a[0] + nx * L, a[1] + ny * L)])


def stroke(pts: list[Pt], ca: str | None, cb: str | None, T: float) -> BaseGeometry:
    """A polyline of width T. Each end is square (None) or cut along "/", "\\", "-" or "|"."""
    (x0, y0), (x1, y1) = pts[0], pts[1]
    (x2, y2), (x3, y3) = pts[-2], pts[-1]
    da, db = (x0 - x1, y0 - y1), (x3 - x2, y3 - y2)
    la, lb = hypot(*da), hypot(*db)
    ua, ub = (da[0] / la, da[1] / la), (db[0] / lb, db[1] / lb)
    ext = list(pts)
    if ca:
        ext[0] = (x0 + ua[0] * T, y0 + ua[1] * T)
    if cb:
        ext[-1] = (x3 + ub[0] * T, y3 + ub[1] * T)
    g = LineString(ext).buffer(T / 2, cap_style="flat", join_style="mitre", mitre_limit=5)
    # cut only near the end, so a polyline that turns back is not clipped elsewhere
    for p, cut, u in ((pts[0], ca, ua), (pts[-1], cb, ub)):
        if cut:
            near = box(p[0] - 1.6 * T, p[1] - 1.6 * T, p[0] + 1.6 * T, p[1] + 1.6 * T)
            g = g.difference(near.difference(halfplane(p, cut, (-u[0], -u[1]))))
    return g


def point_end(g: BaseGeometry, p: Pt, inward: Pt) -> BaseGeometry:
    """Cut an end to a right-angled point at p."""
    return g.intersection(halfplane(p, "/", inward)).intersection(halfplane(p, "\\", inward))


def cbox(x0: float, y0: float, x1: float, y1: float, tl: float = 0, tr: float = 0, br: float = 0, bl: float = 0) -> Polygon:
    """A box with its corners cut at 45 degrees."""
    return Polygon([(x0 + tl, y0), (x1 - tr, y0), (x1, y0 + tr), (x1, y1 - br), (x1 - br, y1),
                    (x0 + bl, y1), (x0, y1 - bl), (x0, y0 + tl)])


def ring(outer: Polygon, T: float) -> BaseGeometry:
    return outer.difference(outer.buffer(-T, join_style="mitre"))


def dnotch(x0: float, y0: float, x1: float, y1: float, c: float) -> Polygon:
    """The cursor block: top-left and bottom-right corners cut at 45 degrees."""
    return Polygon([(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c)])


def _ring_d(coords) -> str:
    pts = list(coords)[:-1]
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def to_d(geom: BaseGeometry) -> str:
    polys = [g for g in getattr(geom, "geoms", [geom]) if g.geom_type == "Polygon" and not g.is_empty]
    out = []
    for p in polys:
        p = p.simplify(.04)
        out.append(_ring_d(p.exterior.coords) + "".join(_ring_d(i.coords) for i in p.interiors))
    return "".join(out)
