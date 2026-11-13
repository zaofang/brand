"""Print sheets: one drawing, written as a CMYK PDF for the printer and an sRGB SVG for review.

Units are millimetres, y down, origin at the top-left of the trim. Text is outlined with fontTools (the `print` extra).
"""
from dataclasses import dataclass, field
from pathlib import Path

from shapely.geometry.base import BaseGeometry

from .palette import PRINT

PT = 72 / 25.4
CUT_PT = .25
Op = tuple  # ("M", x, y) | ("L", x, y) | ("C", x1, y1, x2, y2, x, y) | ("Z",)


def geom_ops(g: BaseGeometry) -> list[Op]:
    ops: list[Op] = []
    for p in (q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon" and not q.is_empty):
        for ring in (p.exterior, *p.interiors):
            pts = list(ring.coords)[:-1]
            ops += [("M", *pts[0]), *(("L", *xy) for xy in pts[1:]), ("Z",)]
    return ops


class Font:
    """An OFL face, outlined at a fixed variable-font location."""

    def __init__(self, path: Path, wght: int | None = None):
        from fontTools.ttLib import TTFont
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet(location={"wght": wght} if wght else None)
        self.cmap, self.upem = self.tt.getBestCmap(), self.tt["head"].unitsPerEm

    def width(self, s: str, size: float, tracking: float = 0) -> float:
        return sum(self.glyphs[self.cmap[ord(ch)]].width for ch in s) * size / self.upem + tracking * (len(s) - 1)

    def ops(self, s: str, x: float, y: float, size: float, tracking: float = 0) -> list[Op]:
        """Outlines of s with its baseline at y, starting at x; size is the em in mm."""
        from fontTools.pens.basePen import BasePen
        k = size / self.upem
        out: list[Op] = []

        class Pen(BasePen):
            def _moveTo(self, p): out.append(("M", ox + p[0] * k, y - p[1] * k))
            def _lineTo(self, p): out.append(("L", ox + p[0] * k, y - p[1] * k))
            def _curveToOne(self, a, b, c): out.append(("C", *(v for p in (a, b, c) for v in (ox + p[0] * k, y - p[1] * k))))
            def _closePath(self): out.append(("Z",))

        ox = x
        for ch in s:
            g = self.glyphs[self.cmap[ord(ch)]]
            g.draw(Pen(self.glyphs))
            ox += g.width * k + tracking
        return out


def _svg_d(ops: list[Op]) -> str:
    return "".join(o[0] + " ".join(f"{v:.3f}" for v in o[1:]) for o in ops)


def _pdf_path(ops: list[Op]) -> str:
    op = {"M": "m", "L": "l", "C": "c", "Z": "h"}
    return "\n".join(" ".join(f"{v:.3f}" for v in o[1:]) + (" " if len(o) > 1 else "") + op[o[0]] for o in ops)


@dataclass
class Page:
    """A trimmed piece: w x h at the trim, artwork may run `bleed` past it."""
    w: float
    h: float
    bleed: float = 3.0
    layers: list[tuple[str | None, list[Op]]] = field(default_factory=list)  # (ink role, path); None is the die

    def fill(self, role: str, shape: BaseGeometry | list[Op]) -> None:
        self.layers.append((role, shape if isinstance(shape, list) else geom_ops(shape)))

    def cut(self, shape: BaseGeometry) -> None:
        self.layers.append((None, geom_ops(shape)))

    def svg(self) -> str:
        b = self.bleed
        body = "".join(f'<path d="{_svg_d(ops)}" fill="{PRINT[r][0]}" fill-rule="evenodd"/>' for r, ops in self.layers if r)
        dies = "".join(f'<path d="{_svg_d(ops)}" fill="none" stroke="{PRINT["die"][0]}" stroke-width="{CUT_PT / PT * 1.5:.3f}" '
                       f'stroke-dasharray="1.2 .8"/>' for r, ops in self.layers if r is None)
        trim = (f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="none" stroke="{PRINT["die"][0]}" stroke-width=".1"/>'
                if not dies else "")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-b} {-b} {self.w + 2 * b} {self.h + 2 * b}" '
                f'width="{self.w + 2 * b}mm" height="{self.h + 2 * b}mm">{body}{dies}{trim}</svg>\n')

    def content(self) -> bytes:
        b = self.bleed
        lines = [f"{PT:.5f} 0 0 {-PT:.5f} {b * PT:.3f} {(self.h + b) * PT:.3f} cm"]  # mm, y down, origin at trim
        for role, ops in self.layers:
            if role:
                c, m, y, k = (v / 100 for v in PRINT[role][1])
                lines += [f"{c:.3f} {m:.3f} {y:.3f} {k:.3f} k", _pdf_path(ops), "f*"]
            else:
                lines += ["q /OP gs /CutContour CS 1 SCN", f"{CUT_PT / PT:.4f} w", _pdf_path(ops), "S Q"]
        return "\n".join(lines).encode()


def write_pdf(path: Path, pages: list[Page], title: str) -> None:
    """PDF 1.4, DeviceCMYK fills only, TrimBox and BleedBox on every page, the die as a CutContour spot set to overprint."""
    objs: list[bytes] = []

    def add(body: bytes) -> int:
        objs.append(body)
        return len(objs)

    cat, pages_id, info = add(b""), add(b""), add(f"<< /Title ({title}) /Producer (zaofang-brand) >>".encode())
    tint = add(b"<< /FunctionType 2 /Domain [0 1] /C0 [0 0 0 0] /C1 [0 1 0 0] /N 1 >>")
    cs = add(f"[/Separation /CutContour /DeviceCMYK {tint} 0 R]".encode())
    gs = add(b"<< /Type /ExtGState /OP true /op true /OPM 1 >>")
    kids = []
    for p in pages:
        data = p.content()
        stream = add(b"<< /Length %d >>\nstream\n" % len(data) + data + b"\nendstream")
        W, H = (p.w + 2 * p.bleed) * PT, (p.h + 2 * p.bleed) * PT
        trim = f"[{p.bleed * PT:.3f} {p.bleed * PT:.3f} {(p.w + p.bleed) * PT:.3f} {(p.h + p.bleed) * PT:.3f}]"
        kids.append(add(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {W:.3f} {H:.3f}] /BleedBox [0 0 {W:.3f} {H:.3f}] "
                        f"/TrimBox {trim} /Contents {stream} 0 R "
                        f"/Resources << /ColorSpace << /CutContour {cs} 0 R >> /ExtGState << /OP {gs} 0 R >> >> >>".encode()))
    objs[cat - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()
    objs[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>".encode()
    out, offsets = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"), []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1) + b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, cat, info, xref)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))
