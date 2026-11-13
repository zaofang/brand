"""Stickers and print: CMYK PDFs for the printer and SVG previews, in print/.
Needs the `print` extra and network on first run (fonts are fetched into .cache/fonts): uv run --extra print scripts/press.py"""
import urllib.request
from collections.abc import Callable
from pathlib import Path

from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry

from zaofang_brand import logos
from zaofang_brand.geometry import dnotch
from zaofang_brand.press import Font, Page, write_pdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "print"
CACHE = ROOT / ".cache/fonts"
FONTS = {"DMMono-Regular.ttf": "ofl/dmmono/DMMono-Regular.ttf", "NotoSansSC.ttf": "ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"}
STICKER_BLEED = 2.0  # artwork past the die
MONO_EM = 2.65       # 7.5 pt


def font(name: str, wght: int | None = None) -> Font:
    p = CACHE / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/google/fonts/main/{FONTS[name]}", p)
    return Font(p, wght)


MONO, HANS = font("DMMono-Regular.ttf"), font("NotoSansSC.ttf", 400)


def mitre(g: BaseGeometry, d: float) -> BaseGeometry:
    """Offset that keeps 0/45/90 edges at 0/45/90."""
    return g.buffer(d, join_style="mitre", mitre_limit=3)


def put(page: Page, logo: logos.Logo, x: float, y: float, *, w: float | None = None, h: float | None = None,
        on: str = "ground") -> tuple[float, float]:
    """Draw logo with its top-left at (x, y), scaled to width w or height h. Returns the drawn size."""
    x0, y0, x1, y1 = logo.bounds
    s = w / (x1 - x0) if w else h / (y1 - y0)
    t = lambda g: affinity.affine_transform(g, [s, 0, 0, s, x - x0 * s, y - y0 * s])  # noqa: E731
    if not logo.ink.is_empty:
        page.fill("paper" if on == "ground" else "ground", t(logo.ink))
    if logo.block is not None:
        page.fill("amber", t(logo.block))
        page.fill("ground", t(logo.sel))
    return (x1 - x0) * s, (y1 - y0) * s


def text(page: Page, f: Font, s: str, x: float, y: float, role: str, size: float = MONO_EM, anchor: str = "start") -> None:
    if anchor == "end":
        x -= f.width(s, size)
    page.fill(role, f.ops(s, x, y, size))


# Stickers: each draws itself at (x, y) and returns its die ----------------------------------------------
Sticker = Callable[[Page, float, float], BaseGeometry]


def cursor(page: Page, x: float, y: float) -> BaseGeometry:
    """The cursor alone: a blank amber block, the proportions of the type-on cursor."""
    die = dnotch(x, y, x + 12, y + 29, 3)
    page.fill("amber", mitre(die, STICKER_BLEED))
    return die


def fang(page: Page, x: float, y: float, size: float, block: bool = True) -> None:
    """坊 in the cursor block (the favicon drawing), size mm square."""
    fav, s = logos.favicon(), size / 100
    if block:
        page.fill("amber", affinity.affine_transform(fav.block, [s, 0, 0, s, x, y]))
    page.fill("ground", affinity.affine_transform(fav.sel, [s, 0, 0, s, x, y]))


def fang_block(size: float) -> Sticker:
    def draw(page: Page, x: float, y: float) -> BaseGeometry:
        die = dnotch(x, y, x + size, y + size, 18.4 * size / 100)
        page.fill("amber", mitre(die, STICKER_BLEED))
        fang(page, x, y, size, block=False)
        return die
    return draw


MARK_W, MARK_OFFSET = 60.0, 3.2


def _contour(w: float) -> tuple[BaseGeometry, tuple[float, float]]:
    """造坊's die: the strokes offset with mitred joins, holes filled, small notches closed. Returns it and the mark's origin."""
    m = logos.mark()
    x0, y0, x1, y1 = m.bounds
    s = w / (x1 - x0)
    g = affinity.affine_transform(m.ink.union(m.block), [s, 0, 0, s, -x0 * s, -y0 * s])
    c = mitre(mitre(Polygon(mitre(g, MARK_OFFSET).exterior), 2), -2)
    cx, cy = c.bounds[:2]
    return affinity.translate(c, -cx, -cy), (-cx, -cy)


def mark_contour(page: Page, x: float, y: float) -> BaseGeometry:
    c, (mx, my) = _contour(MARK_W)
    die = affinity.translate(c, x, y)
    page.fill("ground", mitre(die, STICKER_BLEED))
    put(page, logos.mark(), x + mx, y + my, w=MARK_W)
    return die


STAMP_W, STAMP_H = 64.0, 20.0


def stamp(page: Page, x: float, y: float) -> BaseGeometry:
    """The sub-project stamp: 坊 block, then the stamp line in English and Chinese, on paper."""
    die = box(x, y, x + STAMP_W, y + STAMP_H)
    page.fill("paper", mitre(die, STICKER_BLEED))
    fang(page, x + 3, y + 3, 14)
    text(page, MONO, "a zaofang project", x + 21, y + 9.1, "ground", 3.4)
    text(page, HANS, "造坊出品", x + 21, y + 15.3, "muted", 3.4)
    return die


def single(fn: Sticker, w: float, h: float) -> Page:
    p = Page(w, h, STICKER_BLEED)
    p.cut(fn(p, 0, 0))
    return p


# Print ---------------------------------------------------------------------------------------------------
def calling_card() -> list[Page]:
    W, H = 85.0, 55.0
    front, back = Page(W, H), Page(W, H)
    front.fill("ground", box(-3, -3, W + 3, H + 3))
    m = logos.mark()
    mw = 34.0
    mh = mw * (m.bounds[3] - m.bounds[1]) / (m.bounds[2] - m.bounds[0])
    put(front, m, (W - mw) / 2, (H - mh) / 2, w=mw)
    back.fill("paper", box(-3, -3, W + 3, H + 3))
    put(back, logos.wordmark(), 7, 7, h=8, on="paper")
    for i, (s, role) in enumerate((("github.com/zaofang", "ground"), ("zaofang.sh", "ground"), ("yan", "muted"))):
        text(back, MONO, s, 7, 39 + i * 4.6, role)
    return [front, back]


def sheet() -> Page:
    """A6 kiss-cut sheet: two cursors flanking 坊, 造坊 below, the stamp at the foot. The backing is unprinted."""
    W, H = 105.0, 148.0
    p = Page(W, H, 0)
    blk = 29.0
    row = 12 + 12 + blk + 12 + 12  # cursor, gap, block, gap, cursor
    x = (W - row) / 2
    p.cut(cursor(p, x, 12))
    p.cut(fang_block(blk)(p, x + 24, 12))
    p.cut(cursor(p, x + 24 + blk + 12, 12))
    c, _ = _contour(MARK_W)
    cw, ch = c.bounds[2], c.bounds[3]
    p.cut(mark_contour(p, (W - cw) / 2, 12 + blk + 12))
    p.cut(stamp(p, (W - STAMP_W) / 2, 12 + blk + 12 + ch + 12))
    return p


def main() -> None:
    c, _ = _contour(MARK_W)
    pieces = {
        "sticker-cursor": ([single(cursor, 12, 29)], "Zaofang sticker: cursor"),
        "sticker-fang": ([single(fang_block(40), 40, 40)], "Zaofang sticker: fang block"),
        "sticker-mark": ([single(mark_contour, c.bounds[2], c.bounds[3])], "Zaofang sticker: mark, contour cut"),
        "sticker-stamp": ([single(stamp, STAMP_W, STAMP_H)], "Zaofang sticker: maker's stamp"),
        "sticker-sheet-a6": ([sheet()], "Zaofang kiss-cut sheet, A6"),
        "calling-card": (calling_card(), "Zaofang calling card"),
    }
    for name, (pages, title) in pieces.items():
        write_pdf(OUT / f"{name}.pdf", pages, title)
        for i, pg in enumerate(pages):
            suffix = "" if len(pages) == 1 else ("-front", "-back")[i]
            (OUT / f"{name}{suffix}.svg").write_text(pg.svg())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
