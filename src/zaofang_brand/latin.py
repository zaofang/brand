"""zaofang, drawn on the Bevel rules: long f, double-storey a, optical spacing, double-notch cursor over "fang".

Coordinates: baseline y = 0, x-height -50, ascender -72, descender +24. Stroke T = 10.
"""
from shapely import affinity
from shapely.geometry import LineString, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from .geometry import cbox, dnotch, ring, stroke

T = 10.0
XH, ASC, DSC = -50.0, -72.0, 24.0
WORD = "zaofang"
KERN = {"fa": 4.0}  # a's bowl meets f's stem lower than the band average sees; without this, fa reads as one letter
BLOCK_TOP, BLOCK_BOT, BLOCK_PAD, BLOCK_CUT = -84.0, 34.0, 6.0, 20.0


def letters() -> dict[str, BaseGeometry]:
    h, c, asc = T / 2, T * 1.2, XH - 20
    W = 4 * T
    z = unary_union([box(0, XH, W, XH + T), box(0, -T, W, 0),
                     Polygon([(W - T * 1.414, XH + T), (W, XH + T), (T * 1.414, -T), (0, -T)])]).intersection(box(0, XH, W, 0))
    z = z.difference(Polygon([(W - T, 0), (W + 1, 0), (W + 1, -T - 1)]))
    # double-storey a, so it can never be read as o; its top starts on the same slant as f's crossbar ends
    wa, c2, bt = 3.6 * T, T * .9, XH * .58
    a = unary_union([stroke([(.9 * T, XH + h), (wa - h - .8 * T, XH + h), (wa - h, XH + h + .8 * T), (wa - h, -h)], "/", "/", T),
                     ring(cbox(0, bt, wa, 0, tl=c2, bl=c2), T)])
    o = ring(cbox(0, XH, W, 0, c, c, c, c), T)
    sx = 1.5 * T
    f = unary_union([stroke([(sx, DSC - h), (sx, asc + 12), (sx + 12, asc), (sx + 2.4 * T, asc)], "/", "/", T),
                     stroke([(sx - 1.5 * T + h, XH + h), (sx + 1.2 * T, XH + h)], None, "/", T)])
    wn = 3.8 * T
    n = unary_union([stroke([(h, XH), (h, -h)], None, "/", T),
                     stroke([(h, XH + 19), (h + 14, XH + h), (wn - h - 5, XH + h), (wn - h, XH + h + 5), (wn - h, -h)], None, "/", T)])
    wg = 3.8 * T
    g = unary_union([ring(cbox(0, XH, wg, -2, tl=c, bl=c), T),
                     stroke([(wg - h, XH), (wg - h, DSC - 12), (wg - h - 10, DSC - 2), (4, DSC - 2)], None, None, T)])
    return dict(z=z, a=a, o=o, f=f, n=n, g=g)


def _profile(g: BaseGeometry, side: str, ys) -> list[float | None]:
    out = []
    for y in ys:
        hit = g.intersection(LineString([(-1e3, y), (1e3, y)]))
        if hit.is_empty:
            out.append(None)
            continue
        xs = [p[0] for geom in getattr(hit, "geoms", [hit]) for p in geom.coords]
        out.append(max(xs) if side == "r" else min(xs))
    return out


def advances(L: dict[str, BaseGeometry], word: str = WORD, target: float = 16, depth: float = 6, min_gap: float = 8) -> list[float]:
    """Place each letter so the mean white across the x-height, capped at `depth` into each side, is `target`.

    Beside f the rows of its crossbar are left out and the cap is deeper, so the gap is judged from the stem.
    """
    band = [XH + .5 + i for i in range(int(-XH))]
    xs, x = [0.0], 0.0
    for a, b in zip(word, word[1:]):
        A, B = L[a], L[b]
        ys, dep = band, depth
        if "f" in (a, b):
            ys, dep = [y for y in band if y > XH + T + 2], depth * 2.4
        ra, lb = _profile(A, "r", ys), _profile(B, "l", ys)
        amax = max([r for r in ra if r is not None] or [A.bounds[2]])
        bmin = min([v for v in lb if v is not None] or [B.bounds[0]])
        gaps = [(bmin + dep if v is None else min(v, bmin + dep)) - (amax - dep if r is None else max(r, amax - dep)) for r, v in zip(ra, lb)]
        d = target - sum(gaps) / len(gaps)
        full = list(zip(_profile(A, "r", range(int(ASC), int(DSC) + 1)), _profile(B, "l", range(int(ASC), int(DSC) + 1))))
        tight = min((v + d - r) for r, v in full if r is not None and v is not None)
        if tight < min_gap:
            d += min_gap - tight
        x += d + KERN.get(a + b, 0.0)
        xs.append(x)
    return xs


def placed() -> list[BaseGeometry]:
    """Each letter of zaofang in its set position."""
    L = letters()
    return [affinity.translate(L[ch], x, 0) for ch, x in zip(WORD, advances(L))]


def word() -> tuple[BaseGeometry, list[tuple[float, float]]]:
    """The set word and each letter's horizontal span."""
    parts = placed()
    return unary_union(parts), [(p.bounds[0], p.bounds[2]) for p in parts]


def cursor(spans: list[tuple[float, float]], sel: tuple[int, int] = (3, 7)) -> Polygon:
    """The double-notch block over letters sel[0]:sel[1] ("fang")."""
    a = max(spans[sel[0]][0] - BLOCK_PAD, (spans[sel[0] - 1][1] + spans[sel[0]][0]) / 2)
    b = spans[sel[1] - 1][1] + BLOCK_PAD
    return dnotch(a, BLOCK_TOP, b, BLOCK_BOT, BLOCK_CUT)


def tones(g: BaseGeometry, spans: list[tuple[float, float]], s: float = 13.0, top: float = ASC - 1, f_gap: float = 7.0) -> BaseGeometry:
    """zàofáng: right-angle chips, the piece a 45-degree cut takes off a corner, hung from the ascender line.

    Each chip sits on its letter's optical centre (the centroid of the letter's x-height band). á moves right if it would
    come within `f_gap` of f.
    """
    f_geom = g.intersection(box(spans[3][0] - 20, -200, spans[3][1], 200))
    out = []
    for i, tone in ((1, "grave"), (4, "acute")):
        y0, y1 = top, top + s
        m = Polygon([(0, y0), (s, y0), (s, y1)] if tone == "grave" else [(0, y0), (s, y0), (0, y1)])
        centre = g.intersection(box(spans[i][0], XH, spans[i][1], 0)).centroid.x
        m = affinity.translate(m, centre - m.centroid.x, 0)
        gap = m.distance(f_geom)
        if gap < f_gap:
            m = affinity.translate(m, f_gap - gap, 0)
        out.append(m)
    return unary_union(out)

