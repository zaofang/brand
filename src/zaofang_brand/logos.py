"""Logo compositions. Each is three layers in one coordinate space: ink, the cursor block, and the ink inside the block."""
from dataclasses import dataclass

from shapely import affinity
from shapely.geometry import GeometryCollection
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from . import hanzi, latin
from .geometry import dnotch, to_d

HANZI_SCALE, HANZI_TOP = .96, latin.ASC  # 造坊 spans ascender to descender of zaofang
HANZI_PAD = 2.5 / 43 * 100  # block margin around 坊, in em units
FANG_X = 110.5  # 坊's em origin; leaves a hairline of ground between 造 and the block
LOCKUP_GAP = 40.0
MARGIN = 8.0
EMPTY = GeometryCollection()


@dataclass
class Logo:
    ink: BaseGeometry
    block: BaseGeometry | None = None
    sel: BaseGeometry | None = None

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return unary_union([g for g in (self.ink, self.block) if g is not None]).bounds


def _hanzi(cursor: bool = True) -> Logo:
    zao, fang = hanzi.placed("造", 100, 0, 0), hanzi.placed("坊", 100, FANG_X, 0)
    block = dnotch(FANG_X - HANZI_PAD, -HANZI_PAD, FANG_X + 100 + HANZI_PAD, 100 + HANZI_PAD, 20)
    t = [HANZI_SCALE, 0, 0, HANZI_SCALE, 0, HANZI_TOP]
    place = lambda g: affinity.affine_transform(g, t)  # noqa: E731
    if not cursor:
        return Logo(place(unary_union([zao, fang])))
    return Logo(place(zao), place(block), place(fang))


def mark() -> Logo:
    """造坊 with the cursor on 坊."""
    return _hanzi()


def wordmark(tones: bool = False) -> Logo:
    """zaofang with the cursor over fang; with tones, zàofáng."""
    g, spans = latin.word()
    if tones:
        g = g.union(latin.tones(g, spans))
    block = latin.cursor(spans)
    return Logo(g.difference(block), block, g.intersection(block))


def lockup(tones: bool = False) -> Logo:
    """造坊 and zaofang side by side. One cursor per composition: it sits on 坊, the same syllable as fang."""
    h = _hanzi()
    g, spans = latin.word()
    if tones:
        g = g.union(latin.tones(g, spans))
    g = affinity.translate(g, h.bounds[2] + LOCKUP_GAP, 0)
    return Logo(unary_union([h.ink, g]), h.block, h.sel)


def avatar() -> Logo:
    """坊 in the cursor block, inset on a square ground (the ground is drawn by the writer). 100-unit square."""
    return Logo(EMPTY, dnotch(8, 8, 92, 92, 14.4), hanzi.placed("坊", 72, 14, 14))


def favicon() -> Logo:
    """坊 in a full-bleed cursor block. 100-unit square, transparent outside the block."""
    return Logo(EMPTY, dnotch(0, 0, 100, 100, 18.4), hanzi.placed("坊", 72, 14, 14))


def svg(logo: Logo, colours: dict[str, str] | None, *, view: tuple[float, float, float, float] | None = None,
        background: str | None = None, title: str = "zaofang") -> str:
    """colours: {"ink", "accent", "sel"}; None draws a single-colour mark in currentColor with the selection knocked out."""
    x0, y0, x1, y1 = view or (lambda b: (b[0] - MARGIN, b[1] - MARGIN, b[2] + MARGIN, b[3] + MARGIN))(logo.bounds)
    w, h = x1 - x0, y1 - y0
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>')
    bg = f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{background}"/>' if background else ""
    if colours is None:
        shape = logo.ink if logo.block is None else unary_union([g for g in (logo.ink, logo.block.difference(logo.sel)) if not g.is_empty])
        return f'{head}{bg}<path d="{to_d(shape)}" fill="currentColor" fill-rule="evenodd"/></svg>\n'
    body = f'<path d="{to_d(logo.ink)}" fill="{colours["ink"]}"/>' if not logo.ink.is_empty else ""
    if logo.block is not None:
        body += f'<path d="{to_d(logo.block)}" fill="{colours["accent"]}"/><path d="{to_d(logo.sel)}" fill="{colours["sel"]}"/>'
    return f"{head}{bg}{body}</svg>\n"
