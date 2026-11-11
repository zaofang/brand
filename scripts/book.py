"""The brand book: A4 PDF built from the palette, the logo files and the drawing code.
Needs the `png` extra and the SVGs from `uv run zaofang-brand`: uv run --extra png scripts/book.py"""
import asyncio
import base64
import re
import tomllib
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

from zaofang_brand import latin
from zaofang_brand.build import BLINK, BLINKS, TYPE_TIMES
from zaofang_brand.geometry import dnotch, to_d
from zaofang_brand.palette import ANSI, ANSI_NAMES, SYNTAX, TYPE_SCALE, UI, contrast

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "book/zaofang-brand-book.pdf"
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
D, L = 0, 1
BG, PAPER, INK, TEXT = UI["bg"][D], UI["bg"][L], UI["text"][L], UI["text"][D]
AMBER = UI["accent"][D]


def img(rel: str, style: str = "") -> str:
    p = ROOT / rel
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f'<img src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" style="display:block;{style}" alt="">'


def inline(rel: str, style: str) -> str:
    s = re.sub(r' width="[^"]*" height="[^"]*"', "", (ROOT / rel).read_text(), count=1)
    return s.replace("<svg ", f'<svg style="display:block;{style}" ', 1)


def viewbox(rel: str) -> list[float]:
    return [float(v) for v in (ROOT / rel).read_text().split('viewBox="')[1].split('"')[0].split()]


def dots(colour: str) -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="1.3" fill="{colour}" fill-opacity=".09"/></svg>'
    return f"background-image:url('data:image/svg+xml,{quote(svg)}');background-size:24px 24px"


GRAIN = ("background-image:url('data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n"><feTurbulence type="fractalNoise" '
    'baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .08 0 0 0 0 .14 0 0 0 0 .16 0 0 0 .05 0"/>'
    '</filter><rect width="240" height="240" filter="url(#n)"/></svg>') + "')")


STRIPES = ("background-image:url('data:image/svg+xml," + quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"><path d="M0 12L12 0M-3 3L3 -3M9 15L15 9" stroke="{UI["text-muted"][L]}" stroke-width="4"/></svg>') + "')")


def typed(n: int, solid: bool = True) -> str:
    """The type-on animation stopped after n letters, drawn the way motion/typeon.svg draws it."""
    parts = latin.placed()
    gap, cur_w = 10.0, 28.0
    x0, x1 = parts[0].bounds[0] - 8, parts[-1].bounds[2] + gap + cur_w + 8
    cx = parts[n - 1].bounds[2] + gap if n else 0
    letters = "".join(f'<path d="{to_d(p)}" fill="{TEXT}"/>' for p in parts[:n])
    cur = f'<path d="{to_d(dnotch(cx, -64, cx + cur_w, 4, 7))}" fill="{AMBER}"/>' if solid else ""
    h = latin.BLOCK_BOT - latin.BLOCK_TOP + 16
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {latin.BLOCK_TOP - 8:.2f} {x1 - x0:.2f} {h:.2f}" '
            f'style="display:block;width:100%">{letters}{cur}</svg>')


CSS = f"""@page{{size:210mm 297mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font:400 15px/1.6 Geist,'Noto Sans SC',sans-serif;color:{INK}}}
.pg{{width:794px;height:1123px;position:relative;overflow:hidden;break-after:page;background:{PAPER}}}
.paper{{{GRAIN};padding:150px 76px 0}}
.lab,code,.mono{{font-family:'DM Mono',monospace}} code{{white-space:nowrap}}
.lab{{font-size:11px;color:{UI["text-muted"][L]};letter-spacing:.02em}}
.hd{{position:absolute;left:76px;right:76px;top:56px;display:flex;justify-content:space-between;border-top:2px solid {INK};padding-top:10px}}
.ft{{position:absolute;left:76px;right:76px;bottom:48px;display:flex;justify-content:space-between}}
h1{{font:500 61px/1.05 Newsreader,'Noto Serif SC',serif}}
h2{{font:500 31px/1.15 Newsreader,'Noto Serif SC',serif;margin:44px 0 14px}}
h3{{font:500 20px/1.15 Newsreader,'Noto Serif SC',serif;margin:0 0 6px}}
p,li{{font:400 17px/1.6 Newsreader,'Noto Serif SC',serif;max-width:540px}}
p+p{{margin-top:10px}} ul{{list-style:none}} li{{padding-left:18px;position:relative}}
li::before{{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;background:{INK};clip-path:polygon(30% 0,100% 0,100% 70%,70% 100%,0 100%,0 30%)}}
.num{{font:500 120px/1 Newsreader,serif;color:{UI["border"][L]}}}
.rule{{border-top:1px solid {UI["border"][L]}}}
.cut{{clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .grid3{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.panel{{display:grid;place-items:center;padding:28px}}
.cap{{margin-top:6px}}
table{{border-collapse:collapse;width:100%}} td,th{{text-align:left;padding:7px 8px 7px 0;vertical-align:middle;font-weight:400}}
.paper tr{{border-top:1px solid {UI["border"][L]}}} .paper td{{font-size:15px}}
.man{{background:{BG};color:{TEXT};font:13px/1.6 'DM Mono','Noto Sans SC',monospace;padding:118px 64px 0;{dots(TEXT)}}}
.man .mh,.man .mf{{position:absolute;left:64px;right:64px;display:flex;justify-content:space-between;color:{UI["text-muted"][D]}}}
.man .mh{{top:48px}} .man .mf{{bottom:40px}}
.man .s{{font-weight:500;margin:22px 0 6px}} .man .i{{padding-left:48px;color:#C9C1B0}}
.man .m{{color:{UI["text-muted"][D]}}} .man tr{{border-top:1px solid {UI["border"][D]}}} .man td{{padding:4px 8px 4px 0}}
.chip{{display:inline-block;width:40px;height:22px;vertical-align:middle;outline:1px solid rgba(128,128,128,.35);outline-offset:-1px}}
"""


class Book:
    def __init__(self) -> None:
        self.pages: list[str] = []
        self.starts: dict[str, int] = {}

    def chapter(self, name: str) -> None:
        self.starts[name] = self.n

    @property
    def n(self) -> int:
        return len(self.pages) + 1

    def paper(self, chapter: str, body: str, at: int | None = None) -> None:
        page = (f'<section class="pg paper"><div class="hd"><span class="lab">zaofang · brand identity</span>'
                          f'<span class="lab">{chapter}</span></div>{body}<div class="ft"><span class="lab">{chapter}</span>'
                          f'<span class="lab">{(at or self.n):02}</span></div></section>')
        if at:
            self.pages[at - 1] = page
        else:
            self.pages.append(page)

    def man(self, section: str, body: str) -> None:
        self.pages.append(f'<section class="pg man"><div class="mh"><span>ZAOFANG(7)</span><span>{section}</span><span>ZAOFANG(7)</span></div>'
                          f'{body}<div class="mf"><span>zaofang/brand {VERSION}</span><span>{self.n:02}</span></div></section>')

    def raw(self, html: str) -> None:
        self.pages.append(html)


def opener(num: str, title: str, intro: str) -> str:
    return f'<div class="num">{num}</div><h1 style="margin-top:20px">{title}</h1><p style="margin-top:22px">{intro}</p>'


def panel(content: str, bg: str, cap: str, style: str = "") -> str:
    return f'<div><div class="panel" style="background:{bg};{style}">{content}</div><div class="lab cap">{cap}</div></div>'


CHAPTERS = ["Name", "Story and voice", "Logo", "Colour", "Type", "Motion", "Motifs", "Sub-projects", "Applications"]


def build() -> str:
    b = Book()
    lockup_vb = viewbox("logo/lockup-on-light.svg")

    # Cover and contents
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT};{dots(TEXT)}">'
          f'<div style="position:absolute;left:76px;top:76px" class="lab">造坊 · brand identity · {VERSION}</div>'
          f'<div style="position:absolute;left:76px;right:76px;top:430px">{img("logo/lockup-tones-on-dark.svg", "width:100%")}</div>'
          f'<div style="position:absolute;left:76px;bottom:64px;right:76px;display:flex;justify-content:space-between" class="lab">'
          f'<span>zaofang.sh</span><span>github.com/zaofang</span></div></section>')
    b.raw("")  # contents, filled in once page numbers are known

    # 01 Name
    b.chapter("Name")
    b.paper("01 name", opener("01", "Name", "造坊 means making workshop. 造, to make or build; 坊, a workshop.") +
            f'<div style="display:flex;gap:48px;align-items:end;margin-top:48px">{img("logo/mark-on-light.svg", "height:150px")}'
            f'<div><div style="font:500 44px Newsreader">zàofáng</div><div class="lab">falling, then rising · dzow-fahng</div></div></div>'
            '<p style="margin-top:28px">坊 reads fáng in the workshop sense, as in 作坊 and 磨坊. Fāng is the street and archway sense.</p>'
            '<h2>Writing the name</h2><table>'
            '<tr><td style="width:240px">English prose</td><td>Zaofang</td></tr>'
            '<tr><td>First mention on a page</td><td>Zaofang (造坊)</td></tr>'
            '<tr><td>Chinese prose</td><td>造坊</td></tr>'
            '<tr><td>Logo, handles, URLs, code</td><td><code>zaofang</code></td></tr>'
            '<tr><td>Tone marks</td><td>Large logo uses only; never in URLs, handles, file names, code or typed text</td></tr>'
            '</table><p style="margin-top:22px">There is no tagline.</p>')

    # 02 Story and voice
    b.chapter("Story and voice")
    b.paper("02 story and voice", opener("02", "Story and voice", "The workshop, late, with one lamp on. A bench, a few good tools, "
            "and work done with more care than anyone asked for. Projects leave with their own names and a small maker's stamp.") +
            '<p>One person takes the work far too seriously and ships it quietly. Show the work, not the size of the shop. '
            'One bright thing on screen: the amber cursor.</p><h2>Voice</h2><p>Notes left on the bench: plain, exact, a little dry.</p>'
            '<ul style="margin-top:12px"><li>Address the reader as you, and the tool by its name.</li>'
            '<li>Avoid we: it implies a team. I only in changelogs, essays and release notes.</li>'
            '<li>Specific over impressive: numbers, units, versions, dates.</li>'
            '<li>Short sentences. No exclamation marks, no emoji. State limits early.</li>'
            '<li>Dry humour at most once, never at the reader\'s expense.</li></ul>'
            f'<div class="grid2" style="margin-top:36px"><div class="rule" style="padding-top:12px"><div class="lab">not</div>'
            '<p style="color:#4F6168;margin-top:6px">A blazing-fast, next-gen database.</p></div>'
            '<div class="rule" style="padding-top:12px"><div class="lab">but</div><p style="margin-top:6px">db stores every fact with two '
            'clocks: when it was true, and when it was recorded.</p></div></div>')

    # 03 Logo
    b.chapter("Logo")
    b.paper("03 logo", opener("03", "Logo", "Every shape follows the Bevel rule: strokes only at 0, 45 and 90 degrees, ends cut on the "
            "diagonal, joints opened by a hairline gap. One amber cursor block per composition.") +
            f'<div style="margin-top:72px">{img("logo/lockup-on-light.svg", "width:100%")}</div>'
            f'<div class="lab cap" style="margin-top:16px">Primary lockup · logo/lockup-on-light.svg</div>'
            f'<div class="panel" style="background:{BG};margin-top:40px;padding:56px 48px">{img("logo/lockup-on-dark.svg", "width:100%")}</div>'
            '<div class="lab cap">On dark · logo/lockup-on-dark.svg</div>')
    b.paper("03 logo", '<h2 style="margin-top:0">Lockup</h2><p>造坊 on the left with the cursor on 坊; zaofang on the right without one, '
            'because 坊 and fang are the same syllable. 造坊 is scaled to 0.96 so it spans zaofang from ascender to descender, '
            'with a 40-unit gap.</p>'
            f'<div style="margin-top:36px">{img("logo/lockup-tones-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap" style="margin-top:12px">With tones, for large uses · logo/lockup-tones-on-light.svg</div>'
            '<p style="margin-top:28px">The everyday lockup is plain. The version with tones is for uses where the Latin is 240 px wide '
            'or more: the site hero, README banners, social cards and print.</p>'
            '<h2>Clear space and size</h2><p>Keep the x-height clear on every side. Below the minimum width, use the avatar or favicon.</p>'
            + clear_space(lockup_vb) +
            '<table style="margin-top:20px"><tr><td>Lockup</td><td class="mono">120 px · 30 mm</td></tr>'
            '<tr><td>Wordmark</td><td class="mono">72 px · 18 mm</td></tr><tr><td>造坊 mark</td><td class="mono">48 px · 12 mm</td></tr></table>')
    b.paper("03 logo", '<h2 style="margin-top:0">Wordmark</h2><p>zaofang is drawn, never typed. A long f drops to the descender with a '
            'hooked top; a double-storey a never reads as o. The spacing balances the white between letters, plus 4 units between f '
            'and a so it reads zao-fang. f and a never join. On its own, the wordmark carries the cursor over fang.</p>'
            f'<div style="margin:32px auto 0;width:400px">{img("logo/wordmark-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap" style="text-align:center">logo/wordmark-on-light.svg</div>'
            '<table style="margin-top:28px">'
            + "".join(f'<tr><td style="width:240px">{k}</td><td class="mono">{v}</td></tr>' for k, v in [
                ("Baseline, x-height", "0, 50 units"), ("Ascender, descender", f"{-latin.ASC:.0f}, {latin.DSC:.0f} units"),
                ("Stroke", f"{latin.T:.0f} units"), ("Extra space f to a", f"{latin.KERN['fa']:.0f} units")]) +
            '</table><h2>Tones</h2><p>zàofáng is marked with small right-angle chips, the piece a 45-degree cut takes off a corner, '
            'each centred over its a. Large uses only.</p>'
            f'<div style="margin:24px auto 0;width:400px">{img("logo/wordmark-tones-on-light.svg", "width:100%")}</div>')
    favs = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px">{img("logo/favicon.svg", f"width:{s}px")}'
                   f'<span class="lab">{s}</span></div>' for s in (96, 48, 32, 16))
    b.paper("03 logo", '<h2 style="margin-top:0">Cursor, mark, avatar</h2><p>The cursor block is a rectangle with its top-left and '
            'bottom-right corners cut at 45 degrees. It is always amber, letters inside it take the ground or ink, and it is the only '
            'amber in a logo.</p>'
            f'<div style="margin-top:32px">{img("logo/mark-on-light.svg", "height:130px")}</div><div class="lab cap">造坊 mark · logo/mark-on-light.svg</div>'
            f'<div class="grid2" style="margin-top:36px">{panel(img("logo/avatar.svg", "width:180px"), BG, "Avatar · logo/avatar.svg")}'
            f'{panel(img("logo/avatar-light.svg", "width:180px"), UI["surface"][L], "Avatar on paper · logo/avatar-light.svg")}</div>'
            f'<div style="display:flex;gap:40px;align-items:end;margin-top:36px">{favs}</div>'
            '<div class="lab cap">Favicon, full-bleed block · logo/favicon.svg, favicon.ico, png/favicon-180.png</div>')
    b.paper("03 logo", '<h2 style="margin-top:0">Versions</h2><p>Three, and only three: on dark with paper letters, on light with ink '
            'letters, and single colour with the letters in the block knocked out.</p>'
            f'<div style="display:grid;gap:12px;margin-top:28px">'
            f'{panel(img("logo/lockup-on-dark.svg", "width:440px"), BG, "On dark")}'
            f'{panel(img("logo/lockup-on-light.svg", "width:440px"), UI["surface"][L], "On light")}'
            f'{panel(inline("logo/lockup-mono.svg", f"width:440px;color:{INK}"), PAPER, "Single colour · currentColor", f"outline:1px solid {UI["border"][L]};outline-offset:-1px")}</div>'
            )
    b.paper("03 logo", '<h2 style="margin-top:0">Never</h2><p>Use the files as they are. Anything below needs a new drawing, '
            'and the drawings come from <code>src/</code>.</p>' + misuse() +
            '<ul style="margin-top:28px"><li>Do not redraw, stretch, rotate, outline or add effects.</li>'
            '<li>Do not move the cursor or show two.</li><li>Do not recolour beyond the three versions.</li>'
            '<li>Do not join f and a, or set zaofang in a font.</li><li>Do not place the logo on photos or busy patterns.</li></ul>')

    # 04 Colour
    b.chapter("Colour")
    def ui_row(k: str) -> str:
        cells = ""
        for m in (D, L):
            v = UI[k][m]
            cr = f'{contrast(v, UI["bg"][m]):.1f}' if k not in ("bg", "surface", "surface-2", "selection", "accent", "on-accent") else ""
            cells += f'<td><span class="chip" style="background:{v}"></span></td><td>{v}</td><td class="m">{cr}</td>'
        return f"<tr><td>{k}</td>{cells}</tr>"
    head = '<tr class="m"><td></td><td colspan="3">dark</td><td colspan="3">light</td></tr>'
    prop = (f'<div style="display:flex;height:40px;margin:10px 0 0 48px;outline:1px solid {UI["border"][D]}">'
            f'<div style="flex:70;background:{BG}"></div><div style="flex:25;background:{PAPER}"></div><div style="flex:5;background:{AMBER}"></div></div>'
            '<div class="i m" style="display:flex;padding-top:4px"><span style="flex:70">70 ground</span><span style="flex:25">25 paper or ink</span><span style="flex:5">5</span></div>')
    b.man("Colour", f'<div class="s" style="margin-top:0">NAME</div><div class="i">Lamplight: teal-black ground, warm paper, one amber cursor. '
          'Dark first; paper is a full light mode. Neutrals are tinted, teal in dark and warm in light.</div>'
          f'<div class="s">PROPORTION</div>{prop}'
          f'<div class="s">TOKENS</div><div class="i m">tokens/tokens.css as --zf-*. Third column: contrast on the ground. Every text colour passes WCAG AA, 4.5:1.</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{head}{"".join(ui_row(k) for k in UI)}</table>'
          '<div class="s">RULES</div><div class="i">Amber fills the cursor, the primary button and search hits, and marks warnings. '
          'Never large backgrounds, never body text on paper. Ember is for errors only.</div>')
    ansi = "".join(f'<div style="height:54px;padding:5px 7px;font-size:10.5px;background:{c};color:{BG if i not in (0, 8) else TEXT}">'
                   f'{i} {ANSI_NAMES[i % 8]}<br>{c}</div>' for i, c in enumerate(ANSI["dark"]))
    syn = "".join(f'<tr><td>{k}</td><td><span class="chip" style="background:{d}"></span></td><td>{d}</td>'
                  f'<td><span class="chip" style="background:{l}"></span></td><td>{l}</td></tr>' for k, (d, l) in SYNTAX.items())
    s = {k: v[D] for k, v in SYNTAX.items()}
    code = (f'<span style="color:{s["comment"]}"># every fact keeps two clocks</span><br>'
            f'<span style="color:{s["keyword"]}">def</span> <span style="color:{s["function"]}">as_of</span>(t: <span style="color:{s["type"]}">Instant</span>, '
            f'limit: <span style="color:{s["type"]}">int</span> = <span style="color:{s["number"]}">100</span>):<br>'
            f'&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{s["keyword"]}">return</span> db.query(<span style="color:{s["string"]}">"facts"</span>, valid=t, limit=limit)')
    b.man("Colour", f'<div class="s" style="margin-top:0">ANSI 0-15</div><div class="i m">ANSI red is ember. There is no true red.</div>'
          f'<div style="margin:10px 0 0 48px;display:grid;grid-template-columns:repeat(8,1fr);gap:3px">{ansi}</div>'
          f'<div class="s">SYNTAX</div><table style="margin:4px 0 0 48px;width:calc(100% - 48px)">{syn}</table>'
          f'<div class="s">EXAMPLE</div><div style="margin-left:48px;background:{UI["surface"][D]};padding:14px 20px">{code}</div>'
          '<div class="s">CLI</div><div class="i">Errors ember, warnings amber, success sage, info tide, secondary text bright black. Respect NO_COLOR. '
          'In code, amber stays out of text: cursor, search hits and the matching bracket only.</div>'
          '<div class="s">FILES</div><div class="i" style="color:#7DC4D5">themes/ghostty  themes/alacritty  themes/kitty  themes/wezterm<br>'
          'themes/windows-terminal  themes/vscode  themes/nvim</div>')

    # 05 Type
    b.chapter("Type")
    spec = lambda font, size, text: f'<div style="font:{font};font-size:{size};line-height:1.15;color:{TEXT}">{text}</div>'  # noqa: E731
    b.man("Type", '<div class="s" style="margin-top:0">FACES</div><div class="i m">All SIL Open Font License. Chinese takes over from the matching Latin face.</div>'
          f'<div class="s">Newsreader · Noto Serif SC</div><div class="i">Display and long reading. 500 headings, 400 text.'
          f'<div style="margin-top:12px">{spec("500 1px Newsreader", "49px", "Two clocks per fact")}{spec("400 1px Noto Serif SC", "39px", "造坊出品")}</div></div>'
          f'<div class="s">Geist · Noto Sans SC</div><div class="i">Interface: navigation, buttons, labels, short text. 400 and 500.'
          f'<div style="margin-top:12px">{spec("500 1px Geist", "39px", "Open repository")}{spec("400 1px Noto Sans SC", "31px", "打开仓库")}</div></div>'
          f'<div class="s">DM Mono</div><div class="i">Code, terminal, paths, versions. 400 and 500.'
          f'<div style="margin-top:12px">{spec("400 1px DM Mono", "31px", "uv run zaofang-brand")}</div></div>')
    scale = "".join(f'<tr><td style="width:60px">{k}</td><td style="width:90px" class="m">{float(v[:-3]) * 16:.1f} px</td>'
                    f'<td style="font:500 {v} Newsreader;line-height:1.15;color:{TEXT}">Workshop</td></tr>' for k, v in reversed(TYPE_SCALE.items()))
    b.man("Type", f'<div class="s" style="margin-top:0">SCALE</div><div class="i m">16 px base, ratio 1.25. --zf-size-*</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{scale}</table>'
          '<div class="s">SETTINGS</div><div class="i">Headings 1.15 line height. Interface 16/1.6. Long documents may use Newsreader 18/1.6. '
          'Code 14 px. Chinese body text up to 1.7.</div>'
          '<div class="s">RULES</div><div class="i">Sentence case. Versions, commands and paths always in DM Mono. '
          'The logos are drawings: never set zaofang in a font.</div>')

    # 06 Motion
    b.chapter("Motion")
    frames = [(1, "0.35 s"), (3, "0.56 s"), (7, "1.05 s"), (7, "after 5 s, solid")]
    strip = "".join(f'<div><div style="background:{BG};padding:10px">{typed(n)}</div><div class="lab cap">{t}</div></div>' for n, t in frames)
    total = TYPE_TIMES[-1] + BLINK * BLINKS
    ticks = "".join(f'<div style="position:absolute;left:{t / total * 100:.2f}%;top:0;width:2px;height:16px;background:{INK}"></div>' for t in TYPE_TIMES)
    blinks = "".join(f'<div style="position:absolute;left:{(TYPE_TIMES[-1] + .3 + i * BLINK) / total * 100:.2f}%;top:24px;'
                     f'width:{BLINK / 2 / total * 100:.2f}%;height:16px;background:{AMBER}"></div>' for i in range(BLINKS))
    b.paper("06 motion", opener("06", "Motion", "zaofang types out letter by letter with the cursor stepping after each one. "
            "Then the cursor blinks after the word and stays solid. Typed names carry no tones.") +
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:40px">{strip}</div>'
            f'<h2>Timing</h2><div style="position:relative;height:44px;margin-top:8px">{ticks}{blinks}</div>'
            f'<div class="lab" style="display:flex;justify-content:space-between"><span>0 s</span><span>{total:.1f} s</span></div>'
            f'<p style="margin-top:16px">First letter at {TYPE_TIMES[0]} s, the rest 0.09 to 0.15 s apart, done at {TYPE_TIMES[-1]} s. '
            f'{BLINKS} blinks of {BLINK} s, so blinking stops near five seconds (WCAG 2.2.2). With reduced motion, the finished word '
            'and a solid cursor appear at once.</p>'
            '<p>Interface motion: 150 to 200 ms, ease-out, no bounce. Only the cursor blinks. CLI splash: 90 ms per letter, three '
            'blinks, on first launch or <code>--version</code> only.</p>')

    # 07 Motifs
    b.chapter("Motifs")
    b.paper("07 motifs", opener("07", "Motifs", "No photography, no stock. Three generated motifs, used quietly.") +
            f'<div class="grid3" style="margin-top:48px">'
            f'{panel("", BG, "Dot grid: 1.3 px dots on 24 px, text colour at 9 percent", f"height:200px;{dots(TEXT)}")}'
            f'{panel("", PAPER, "Paper grain: 3 to 5 percent noise, paper only", f"height:200px;{GRAIN};outline:1px solid {UI["border"][L]};outline-offset:-1px")}'
            f'{panel("", UI["surface"][L], "45-degree cuts: 8 to 12 px on cards", "height:200px;clip-path:polygon(24px 0,100% 0,100% calc(100% - 24px),calc(100% - 24px) 100%,0 100%,0 24px)")}</div>'
            '<p style="margin-top:36px">Diagrams use dusk, tide, sage, heather and straw, with hairline borders. Any future image '
            'follows lamplight: one warm source, low and to one side, deep shadow.</p>'
            '<p>Corners are square or cut at 45 degrees. Never rounded. No gradients, no glows, no starfields.</p>')

    # 08 Sub-projects
    b.chapter("Sub-projects")
    stamp = (f'<div style="display:flex;align-items:center;gap:10px">{img("logo/avatar.svg", "width:24px")}'
             f'<span class="mono" style="font-size:14px">a zaofang project</span></div>')
    b.paper("08 sub-projects", opener("08", "Sub-projects", "yan, db and what follows get their own name, colour and mark. "
            "Zaofang appears only as a stamp.") +
            f'<div class="grid2" style="margin-top:48px">{panel(stamp, UI["surface"][L], "README, site and docs footers")}'
            f'{panel(f"<div style=\"display:flex;align-items:center;gap:10px\">{img("logo/avatar.svg", "width:24px")}<span style=\"font:14px Noto Sans SC\">造坊出品</span></div>", UI["surface"][L], "In Chinese")}</div>'
            f'<div style="margin-top:24px;background:{BG};color:{TEXT};padding:20px 24px" class="mono">$ yan --version<br>yan 0.4.2 · a zaofang project</div>'
            '<div class="lab cap">The --version line</div>'
            '<ul style="margin-top:32px"><li>Stamp: the 坊 avatar at 16 to 24 px, then "a zaofang project" in DM Mono, lowercase.</li>'
            '<li>Sub-projects may share DM Mono and nothing else.</li>'
            '<li>Never lamplight amber, the teal-black ground, the cursor block, the Bevel cut, Newsreader or Geist as their identity.</li></ul>')

    # 09 Applications
    b.chapter("Applications")
    rows = "".join(f'<tr><td style="width:220px">{k}</td><td class="mono" style="font-size:13px">{v}</td></tr>' for k, v in [
        ("Site header", "logo/lockup-on-dark.svg, 28 to 32 px tall"), ("Site hero, first visit", "motion/typeon.svg"),
        ("Docs", "tokens/tokens.css; code via Shiki with themes/vscode"), ("GitHub org avatar", "logo/png/avatar-512.png"),
        ("Org README", "social/readme-banner-dark.svg, -light.svg"), ("Repo social preview", "social/github-social-preview.png"),
        ("Link previews", "social/og-card.png"), ("Favicon", "logo/favicon.svg, favicon.ico, png/favicon-180.png"),
        ("Terminals, editors", "themes/")])
    b.paper("09 applications", opener("09", "Applications", "Each surface has its file. Use the file; do not rebuild the logo.") +
            f'<div class="grid2" style="margin-top:40px;align-items:end"><div>{img("social/og-card.png", "width:100%")}<div class="lab cap">Link preview · social/og-card.png</div></div>'
            f'<div>{img("social/readme-banner-light.svg", "width:100%")}<div class="lab cap">Org README · social/readme-banner-light.svg</div></div></div>'
            f'<table style="margin-top:28px">{rows}</table>')

    # Back cover
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT}">'
          f'<div style="position:absolute;left:76px;top:76px">{img("logo/avatar.svg", "width:64px")}</div>'
          f'<div style="position:absolute;left:76px;right:76px;bottom:64px;font:12px/1.7 \'DM Mono\';color:{UI["text-muted"][D]}">'
          f'Generated by scripts/book.py from zaofang/brand {VERSION}.<br>Code, tokens and themes: MIT. Logos and the names zaofang and 造坊 are '
          'trademarks; see TRADEMARK.md.<br>Set in Newsreader, Geist, DM Mono, Noto Serif SC and Noto Sans SC, SIL Open Font License.</div></section>')
    rows = "".join(f'<tr><td class="lab" style="width:48px">{i + 1:02}</td><td style="font:500 22px Newsreader">{c}</td>'
                   f'<td class="lab" style="text-align:right">{b.starts[c]:02}</td></tr>' for i, c in enumerate(CHAPTERS))
    b.paper("contents", f'<h1>Contents</h1><p style="margin-top:22px">Zaofang (造坊) is an open-source workshop for computer science tools: '
            f'yan, a language family, and db, a bitemporal time-series database. This book sets out how the workshop looks and '
            f'sounds. Every logo, colour and theme in it is generated by <code>zaofang/brand</code>; if this book and the repository '
            f'disagree, the repository is right.</p><table style="margin-top:56px">{rows}</table>', at=2)

    return "".join(b.pages)


def clear_space(vb: list[float], w: float = 400) -> str:
    """The lockup inside its clear space: the x-height on every side. The SVG already carries its MARGIN."""
    pad = (-latin.XH - 8) * w / vb[2]
    return (f'<div style="display:inline-block;padding:{pad:.1f}px;outline:1px dashed {UI["text-muted"][L]};outline-offset:-1px;margin-top:20px">'
            f'<div style="outline:1px solid {UI["border"][L]}">{img("logo/lockup-on-light.svg", f"width:{w}px")}</div></div>')


def misuse() -> str:
    logo = img("logo/lockup-on-light.svg", "width:150px")
    cases = [("Stretch", f'<div style="transform:scaleX(1.35)">{logo}</div>'),
             ("Rotate", f'<div style="transform:rotate(-12deg)">{logo}</div>'),
             ("Recolour", f'<div style="filter:hue-rotate(160deg)">{logo}</div>'),
             ("Add effects", f'<div style="filter:drop-shadow(4px 4px 0 {UI["border"][L]})">{logo}</div>'),
             ("Set in a font", '<div style="font:500 34px Geist">造坊 zaofang</div>'),
             ("Busy ground", f'<div style="padding:10px;{STRIPES}">{logo}</div>')]
    return '<div class="grid3">' + "".join(panel(c, UI["surface"][L], f"No: {n.lower()}", "height:130px;overflow:hidden;padding:12px") for n, c in cases) + "</div>"


FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Geist:wght@400;500"
         "&family=DM+Mono:wght@400;500&family=Noto+Serif+SC:wght@400;500&family=Noto+Sans+SC:wght@400&display=swap")


async def main() -> None:
    body = build()
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Zaofang brand identity</title>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>{body}</body></html>')
    OUT.parent.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.pdf(path=str(OUT), width="210mm", height="297mm", print_background=True, prefer_css_page_size=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
