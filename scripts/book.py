"""The brand book, English and Chinese: A4 PDFs built from the palette, the logo files and the drawing code.
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
from zaofang_brand.palette import ANSI, ANSI_NAMES, RAMPS, SYNTAX, TYPE_SCALE, UI, contrast

ROOT = Path(__file__).resolve().parents[1]
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
:lang(zh) p,:lang(zh) li{{line-height:1.8}} :lang(zh) .man .i{{line-height:1.7}}
.chip{{display:inline-block;width:40px;height:22px;vertical-align:middle;outline:1px solid rgba(128,128,128,.35);outline-offset:-1px}}
"""


class Book:
    def __init__(self, title: str) -> None:
        self.title = title
        self.pages: list[str] = []
        self.starts: list[int] = []

    def chapter(self) -> None:
        self.starts.append(self.n)

    @property
    def n(self) -> int:
        return len(self.pages) + 1

    def paper(self, chapter: str, body: str, at: int | None = None) -> None:
        page = (f'<section class="pg paper"><div class="hd"><span class="lab">{self.title}</span>'
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


def build(lang: str) -> str:
    def t(en: str, zh: str) -> str:
        return zh if lang == "zh" else en

    chapters = [t("Name", "名称"), t("Story and voice", "故事与语气"), t("Logo", "标志"), t("Colour", "色彩"), t("Type", "字体"),
                t("Motion", "动效"), t("Motifs", "图形元素"), t("Sub-projects", "子项目"), t("Applications", "应用场景")]
    label = lambda i: f"{i + 1:02} {chapters[i].lower()}"  # noqa: E731
    b = Book(t("zaofang · brand identity", "造坊 · 品牌手册"))
    lockup_vb = viewbox("logo/lockup-on-light.svg")
    rows2 = lambda pairs, w=240: "".join(f'<tr><td style="width:{w}px">{k}</td><td>{v}</td></tr>' for k, v in pairs)  # noqa: E731

    # Cover and contents
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT};{dots(TEXT)}">'
          f'<div style="position:absolute;left:76px;top:76px" class="lab">造坊 · {t("brand identity", "品牌手册")} · {VERSION}</div>'
          f'<div style="position:absolute;left:76px;right:76px;top:430px">{img("logo/lockup-tones-on-dark.svg", "width:100%")}</div>'
          f'<div style="position:absolute;left:76px;bottom:64px;right:76px;display:flex;justify-content:space-between" class="lab">'
          f'<span>zaofang.sh</span><span>github.com/zaofang</span></div></section>')
    b.raw("")  # contents, filled in once page numbers are known

    # 01 Name
    b.chapter()
    b.paper(label(0), opener("01", chapters[0], t("造坊 means making workshop. 造, to make or build; 坊, a workshop.",
                                                  "造坊意为“制造的作坊”：造，制造、建造；坊，作坊。")) +
            f'<div style="display:flex;gap:48px;align-items:end;margin-top:48px">{img("logo/mark-on-light.svg", "height:150px")}'
            f'<div><div style="font:500 44px Newsreader">zàofáng</div><div class="lab">{t("falling, then rising", "降调，然后升调")} · dzow-fahng</div></div></div>'
            + t('<p style="margin-top:28px">坊 reads fáng in the workshop sense, as in 作坊 and 磨坊. Fāng is the street and archway sense.</p>',
                '<p style="margin-top:28px">作坊义的“坊”读 fáng，如作坊、磨坊；fāng 是街坊、牌坊的读音。</p>') +
            f'<h2>{t("Writing the name", "名称的写法")}</h2><table>' + rows2([
                (t("English prose", "英文行文"), "Zaofang"),
                (t("First mention on a page", "英文页面首次出现"), t("Zaofang (造坊)", "Zaofang (造坊)，之后只写 Zaofang")),
                (t("Chinese prose", "中文行文"), "造坊"),
                (t("Logo, handles, URLs, code", "标志、账号、网址、代码"), "<code>zaofang</code>"),
                (t("Tone marks", "声调符号"), t("Large logo uses only; never in URLs, handles, file names, code or typed text",
                                              "仅限大幅标志；不进入网址、账号、文件名、代码和打出的文字"))]) +
            f'</table><p style="margin-top:22px">{t("There is no tagline.", "没有口号。")}</p>')

    # 02 Story and voice
    b.chapter()
    b.paper(label(1), opener("02", chapters[1], t(
                "The workshop, late, with one lamp on. A bench, a few good tools, and work done with more care than anyone asked "
                "for. Projects leave with their own names and a small maker's stamp.",
                "一间深夜还亮着一盏灯的作坊：一张工作台，几件好工具，做得比任何人要求的都更用心。每个项目出门时带着自己的名字，只盖一枚小印。")) +
            t('<p>One person takes the work far too seriously and ships it quietly. Show the work, not the size of the shop. '
              'One bright thing on screen: the amber cursor.</p>',
              '<p>一个人，把作品看得过分认真，安静地交付。展示作品，不展示作坊的规模。屏幕上只有一处亮色：琥珀色光标。</p>') +
            f'<h2>{t("Voice", "语气")}</h2><p>{t("Notes left on the bench: plain, exact, a little dry.", "像留在工作台上的便条：朴素、准确、略带干涩。")}</p>'
            '<ul style="margin-top:12px">' + "".join(f"<li>{x}</li>" for x in [
                t("Address the reader as you, and the tool by its name.", "对读者说“你”，称工具的名字。"),
                t("Avoid we: it implies a team. I only in changelogs, essays and release notes.",
                  "避免“我们”，它暗示一个团队。“我”只用于更新日志、随笔和发布说明。"),
                t("Specific over impressive: numbers, units, versions, dates.", "具体胜过惊艳：数字、单位、版本、日期。"),
                t("Short sentences. No exclamation marks, no emoji. State limits early.", "短句。不用感叹号，不用表情符号。局限写在前面。"),
                t("Dry humour at most once, never at the reader's expense.", "冷幽默至多一次，绝不拿读者开玩笑。")]) + '</ul>'
            f'<div class="grid2" style="margin-top:36px"><div class="rule" style="padding-top:12px"><div class="lab">{t("not", "不要写")}</div>'
            f'<p style="color:#4F6168;margin-top:6px">{t("A blazing-fast, next-gen database.", "极速、新一代数据库。")}</p></div>'
            f'<div class="rule" style="padding-top:12px"><div class="lab">{t("but", "改写为")}</div><p style="margin-top:6px">'
            f'{t("db stores every fact with two clocks: when it was true, and when it was recorded.", "db 为每条事实记录两个时间：它何时为真，何时被记录。")}</p></div></div>')

    # 03 Logo
    b.chapter()
    b.paper(label(2), opener("03", chapters[2], t(
                "Every shape follows the Bevel rule: strokes only at 0, 45 and 90 degrees, ends cut on the diagonal, joints opened "
                "by a hairline gap. One amber cursor block per composition.",
                "所有形状遵循斜切规则：笔画只走 0°、45°、90°，笔端斜切，交接处留一道细缝。一个构图只用一个琥珀色光标块。")) +
            f'<div style="margin-top:72px">{img("logo/lockup-on-light.svg", "width:100%")}</div>'
            f'<div class="lab cap" style="margin-top:16px">{t("Primary lockup", "主组合标")} · logo/lockup-on-light.svg</div>'
            f'<div class="panel" style="background:{BG};margin-top:40px;padding:56px 48px">{img("logo/lockup-on-dark.svg", "width:100%")}</div>'
            f'<div class="lab cap">{t("On dark", "深色底")} · logo/lockup-on-dark.svg</div>')
    b.paper(label(2), f'<h2 style="margin-top:0">{t("Lockup", "组合标")}</h2><p>' + t(
                "造坊 on the left with the cursor on 坊; zaofang on the right without one, because 坊 and fang are the same "
                "syllable. 造坊 is scaled to 0.96 so it spans zaofang from ascender to descender, with a 40-unit gap.",
                "造坊在左，光标落在“坊”上；zaofang 在右，不带光标，因为“坊”与 fang 是同一个音节。造坊缩放到 0.96，"
                "从 zaofang 的上伸线跨到下伸线，间距 40 个单位。") + '</p>'
            f'<div style="margin-top:36px">{img("logo/lockup-tones-on-light.svg", "width:100%")}</div>'
            f'<div class="lab cap" style="margin-top:12px">{t("With tones, for large uses", "带声调，用于大尺寸")} · logo/lockup-tones-on-light.svg</div>'
            '<p style="margin-top:28px">' + t(
                "The everyday lockup is plain. The version with tones is for uses where the Latin is 240 px wide or more: the "
                "site hero, README banners, social cards and print.",
                "日常使用不带声调的组合标。拉丁字标宽度达到 240 px 时使用带声调版本：网站首屏、README 横幅、社交卡片和印刷品。") + '</p>'
            f'<h2>{t("Clear space and size", "留白与尺寸")}</h2><p>' + t(
                "Keep the x-height clear on every side. Below the minimum width, use the avatar or favicon.",
                "四周至少留出一个 x 高度。小于最小宽度时，改用头像或网站图标。") + '</p>'
            + clear_space(lockup_vb) +
            '<table style="margin-top:20px">' + rows2([(t("Lockup", "组合标"), '<span class="mono">120 px · 30 mm</span>'),
                                                       (t("Wordmark", "字标"), '<span class="mono">72 px · 18 mm</span>'),
                                                       (t("造坊 mark", "造坊字标"), '<span class="mono">48 px · 12 mm</span>')]) + '</table>')
    b.paper(label(2), f'<h2 style="margin-top:0">{t("Wordmark", "字标")}</h2><p>' + t(
                "zaofang is drawn, never typed. A long f drops to the descender with a hooked top; a double-storey a never reads as "
                "o. The spacing balances the white between letters, plus 4 units between f and a so it reads zao-fang. f and a "
                "never join. On its own, the wordmark carries the cursor over fang.",
                "zaofang 是绘制的，不是打出来的。长 f 下探到下伸线，顶端带钩；双层 a 绝不会被看成 o。字距按字母间的空白平衡，"
                "并在 f 与 a 之间多留 4 个单位，读作 zao-fang。f 与 a 永不连写。单独使用时，光标覆盖 fang。") + '</p>'
            f'<div style="margin:32px auto 0;width:400px">{img("logo/wordmark-on-light.svg", "width:100%")}</div>'
            '<div class="lab cap" style="text-align:center">logo/wordmark-on-light.svg</div>'
            '<table style="margin-top:28px">' + rows2([
                (t("Baseline, x-height", "基线、x 高度"), f'<span class="mono">0, {-latin.XH:.0f} {t("units", "单位")}</span>'),
                (t("Ascender, descender", "上伸、下伸"), f'<span class="mono">{-latin.ASC:.0f}, {latin.DSC:.0f} {t("units", "单位")}</span>'),
                (t("Stroke", "笔画"), f'<span class="mono">{latin.T:.0f} {t("units", "单位")}</span>'),
                (t("Extra space f to a", "f 与 a 额外间距"), f'<span class="mono">{latin.KERN["fa"]:.0f} {t("units", "单位")}</span>')]) +
            f'</table><h2>{t("Tones", "声调")}</h2><p>' + t(
                "zàofáng is marked with small right-angle chips, the piece a 45-degree cut takes off a corner, each centred over "
                "its a. Large uses only.",
                "zàofáng 的声调是直角小三角，即 45° 切角切下的那一块，居中于各自的 a。仅用于大尺寸场合。") + '</p>'
            f'<div style="margin:24px auto 0;width:400px">{img("logo/wordmark-tones-on-light.svg", "width:100%")}</div>')
    favs = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px">{img("logo/favicon.svg", f"width:{s}px")}'
                   f'<span class="lab">{s}</span></div>' for s in (96, 48, 32, 16))
    b.paper(label(2), f'<h2 style="margin-top:0">{t("Cursor, mark, avatar", "光标、造坊字标、头像")}</h2><p>' + t(
                "The cursor block is a rectangle with its top-left and bottom-right corners cut at 45 degrees. It is always amber, "
                "letters inside it take the ground or ink, and it is the only amber in a logo.",
                "光标块是左上角和右下角 45° 切角的矩形。它永远是琥珀色，块内字母取底色或墨色，是标志里唯一的琥珀色。") + '</p>'
            f'<div style="margin-top:32px">{img("logo/mark-on-light.svg", "height:130px")}</div>'
            f'<div class="lab cap">{t("造坊 mark", "造坊字标")} · logo/mark-on-light.svg</div>'
            f'<div class="grid2" style="margin-top:36px">{panel(img("logo/avatar.svg", "width:180px"), BG, t("Avatar", "头像") + " · logo/avatar.svg")}'
            f'{panel(img("logo/avatar-light.svg", "width:180px"), UI["surface"][L], t("Avatar on paper", "纸色底头像") + " · logo/avatar-light.svg")}</div>'
            f'<div style="display:flex;gap:40px;align-items:end;margin-top:36px">{favs}</div>'
            f'<div class="lab cap">{t("Favicon, full-bleed block", "网站图标，满版光标块")} · logo/favicon.svg, favicon.ico, png/favicon-180.png</div>')
    b.paper(label(2), f'<h2 style="margin-top:0">{t("Versions", "配色版本")}</h2><p>' + t(
                "Three, and only three: on dark with paper letters, on light with ink letters, and single colour with the letters "
                "in the block knocked out.",
                "三种，只有三种：深色底配纸色字母，浅色底配墨色字母，单色版本中块内字母镂空。") + '</p>'
            f'<div style="display:grid;gap:12px;margin-top:28px">'
            f'{panel(img("logo/lockup-on-dark.svg", "width:440px"), BG, t("On dark", "深色底"))}'
            f'{panel(img("logo/lockup-on-light.svg", "width:440px"), UI["surface"][L], t("On light", "浅色底"))}'
            f'{panel(inline("logo/lockup-mono.svg", f"width:440px;color:{INK}"), PAPER, t("Single colour", "单色") + " · currentColor", f"outline:1px solid {UI["border"][L]};outline-offset:-1px")}</div>')
    b.paper(label(2), f'<h2 style="margin-top:0">{t("Never", "禁止")}</h2><p>' + t(
                "Use the files as they are. Anything below needs a new drawing, and the drawings come from <code>src/</code>.",
                "按原样使用文件。下面任何一种都需要重新绘制，而绘制只在 <code>src/</code> 里进行。") + '</p>' + misuse(t) +
            '<ul style="margin-top:28px">' + "".join(f"<li>{x}</li>" for x in [
                t("Do not redraw, stretch, rotate, outline or add effects.", "不要重绘、拉伸、旋转、描边或添加特效。"),
                t("Do not move the cursor or show two.", "不要移动光标，也不要出现两个光标。"),
                t("Do not recolour beyond the three versions.", "不要使用三种配色版本以外的颜色。"),
                t("Do not join f and a, or set zaofang in a font.", "不要连写 f 和 a，也不要用字体打出 zaofang。"),
                t("Do not place the logo on photos or busy patterns.", "不要把标志放在照片或繁杂的图案上。")]) + '</ul>')

    # 04 Colour
    b.chapter()

    def ui_row(k: str) -> str:
        cells = ""
        for m in (D, L):
            v = UI[k][m]
            cr = f'{contrast(v, UI["bg"][m]):.1f}' if k not in ("bg", "surface", "surface-2", "selection", "accent", "on-accent") else ""
            cells += f'<td><span class="chip" style="background:{v}"></span></td><td>{v}</td><td class="m">{cr}</td>'
        return f"<tr><td>{k}</td>{cells}</tr>"
    head = f'<tr class="m"><td></td><td colspan="3">{t("dark", "深色")}</td><td colspan="3">{t("light", "浅色")}</td></tr>'
    prop = (f'<div style="display:flex;height:40px;margin:10px 0 0 48px;outline:1px solid {UI["border"][D]}">'
            f'<div style="flex:70;background:{BG}"></div><div style="flex:25;background:{PAPER}"></div><div style="flex:5;background:{AMBER}"></div></div>'
            f'<div class="i m" style="display:flex;padding-top:4px"><span style="flex:70">70 {t("ground", "底色")}</span>'
            f'<span style="flex:25">25 {t("paper or ink", "纸色或墨色")}</span><span style="flex:5">5</span></div>')
    b.man(chapters[3], f'<div class="s" style="margin-top:0">{t("NAME", "名称")}</div><div class="i">' + t(
              "Lamplight: teal-black ground, warm paper, one amber cursor. Dark first; paper is a full light mode. Neutrals are "
              "tinted, teal in dark and warm in light.",
              "灯下（Lamplight）：青黑底色、暖纸色、一个琥珀色光标。深色模式为主；纸色是完整的浅色模式。中性色带色相：深色偏青，浅色偏暖。") + '</div>'
          f'<div class="s">{t("PROPORTION", "比例")}</div>{prop}'
          f'<div class="s">{t("TOKENS", "变量")}</div><div class="i m">' + t(
              "tokens/tokens.css as --zf-*. Third column: contrast on the ground. Every text colour passes WCAG AA, 4.5:1.",
              "tokens/tokens.css 中的 --zf-*。第三列为相对底色的对比度。所有文字颜色达到 WCAG AA（4.5:1）。") + '</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{head}{"".join(ui_row(k) for k in UI)}</table>'
          f'<div class="s">{t("RULES", "规则")}</div><div class="i">' + t(
              "Amber fills the cursor, the primary button and search hits, and marks warnings. Never large backgrounds, never "
              "body text on paper. Ember is for errors only.",
              "琥珀用于光标、主按钮、搜索命中和警告。不用作大面积背景，不在纸色上作正文。余烬只用于错误。") + '</div>')
    zh_ansi = ["黑", "红", "绿", "黄", "蓝", "品红", "青", "白"]
    ansi = "".join(f'<div style="height:54px;padding:5px 7px;font-size:10.5px;background:{c};color:{BG if i not in (0, 8) else TEXT}">'
                   f'{i} {t(ANSI_NAMES[i % 8], zh_ansi[i % 8])}<br>{c}</div>' for i, c in enumerate(ANSI["dark"]))
    syn = "".join(f'<tr><td>{k}</td><td><span class="chip" style="background:{d}"></span></td><td>{d}</td>'
                  f'<td><span class="chip" style="background:{l}"></span></td><td>{l}</td></tr>' for k, (d, l) in SYNTAX.items())
    s = {k: v[D] for k, v in SYNTAX.items()}
    code = (f'<span style="color:{s["comment"]}"># {t("every fact keeps two clocks", "每条事实记录两个时间")}</span><br>'
            f'<span style="color:{s["keyword"]}">def</span> <span style="color:{s["function"]}">as_of</span>(t: <span style="color:{s["type"]}">Instant</span>, '
            f'limit: <span style="color:{s["type"]}">int</span> = <span style="color:{s["number"]}">100</span>):<br>'
            f'&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{s["keyword"]}">return</span> db.query(<span style="color:{s["string"]}">"facts"</span>, valid=t, limit=limit)')
    b.man(chapters[3], f'<div class="s" style="margin-top:0">ANSI 0-15</div><div class="i m">{t("ANSI red is ember. There is no true red.", "ANSI 红色就是余烬，没有正红。")}</div>'
          f'<div style="margin:10px 0 0 48px;display:grid;grid-template-columns:repeat(8,1fr);gap:3px">{ansi}</div>'
          f'<div class="s">{t("SYNTAX", "语法")}</div><table style="margin:4px 0 0 48px;width:calc(100% - 48px)">{syn}</table>'
          f'<div class="s">{t("EXAMPLE", "示例")}</div><div style="margin-left:48px;background:{UI["surface"][D]};padding:14px 20px">{code}</div>'
          f'<div class="s">{t("CLI", "命令行")}</div><div class="i">' + t(
              "Errors ember, warnings amber, success sage, info tide, secondary text bright black. Respect NO_COLOR. In code, "
              "amber stays out of text: cursor, search hits and the matching bracket only.",
              "错误用余烬，警告用琥珀，成功用鼠尾草绿，信息用潮色，次要文字用亮黑。遵守 NO_COLOR。琥珀不进入代码文字，只标记光标、搜索命中和匹配括号。") + '</div>'
          f'<div class="s">{t("FILES", "文件")}</div><div class="i" style="color:#7DC4D5">themes/ghostty  themes/alacritty  themes/kitty  themes/wezterm<br>'
          'themes/windows-terminal  themes/vscode  themes/nvim</div>')

    zh_hue = {"neutral": "中性", "amber": "琥珀", "ember": "余烬", "tide": "潮色", "sage": "鼠尾草绿", "dusk": "暮色",
              "heather": "石楠", "straw": "麦秆"}

    def ramp_grid(mode: str) -> str:
        rows = "".join(f'<div class="m" style="font-size:10.5px;align-self:center">{t(h, zh_hue[h])}</div>'
                       + "".join(f'<div style="height:24px;background:{c}"></div>' for c in r) for h, r in RAMPS[mode].items())
        nums = "<div></div>" + "".join(f'<div class="m" style="font-size:10px">{n}</div>' for n in range(1, 13))
        return (f'<div style="margin:6px 0 0 48px;display:grid;grid-template-columns:64px repeat(12,1fr);gap:2px">'
                f'{nums}{rows}</div>')
    jobs = [("1-2", t("page and subtle fills", "页面与浅底")), ("3-5", t("component fills: rest, hover, pressed", "组件底色：常态、悬停、按下")),
            ("6-8", t("borders", "边框")), ("9-10", t("solid fill and its hover", "实色填充及其悬停")), ("11", t("text", "文字")),
            ("12", t("strong text", "强调文字"))]
    b.man(chapters[3], f'<div class="s" style="margin-top:0">{t("RAMPS", "色阶")}</div><div class="i">' + t(
              "Twelve steps per hue and per mode, one job each. Steps 1 to 8 tint the mode's own ground toward the hue, so dark "
              "fills stay teal and light fills stay warm. Step 11 is the role colour above; step 9 is the bright value in both modes.",
              "每个色相、每种模式各十二级，每级一个用途。第 1 到 8 级由该模式的底色向色相过渡，所以深色填充保持青色，浅色填充保持暖色。"
              "第 11 级即上文的角色色；第 9 级在两种模式下都是亮色值。") + '</div>'
          '<table class="i" style="margin:8px 0 0 48px">' + "".join(f'<tr><td class="m">{n}</td><td>{j}</td></tr>' for n, j in jobs) + '</table>'
          f'<div class="s">{t("DARK", "深色")}</div>{ramp_grid("dark")}'
          f'<div class="s">{t("LIGHT", "浅色")}</div>{ramp_grid("light")}'
          f'<div class="s">{t("RULES", "规则")}</div><div class="i">' + t(
              "Text sits on steps 1 to 3 at step 11 or 12. Amber steps keep amber's four jobs; ember steps are for errors only. "
              "tokens/tokens.css as --zf-tide-1 to --zf-tide-12, and so on for each hue.",
              "文字用第 11 或 12 级，放在第 1 到 3 级上。琥珀各级仍只做琥珀的四件事；余烬各级只用于错误。"
              "tokens/tokens.css 中为 --zf-tide-1 到 --zf-tide-12，其他色相同理。") + '</div>')

    # 05 Type
    b.chapter()
    spec = lambda font, size, text: f'<div style="font:{font};font-size:{size};line-height:1.15;color:{TEXT}">{text}</div>'  # noqa: E731
    b.man(chapters[4], f'<div class="s" style="margin-top:0">{t("FACES", "字族")}</div><div class="i m">' + t(
              "All SIL Open Font License. Chinese takes over from the matching Latin face.",
              "全部采用 SIL 开源字体许可。遇到汉字时，由对应的中文字体接手。") + '</div>'
          f'<div class="s">Newsreader · Noto Serif SC</div><div class="i">{t("Display and long reading. 500 headings, 400 text.", "展示与长文阅读。标题 500，正文 400。")}'
          f'<div style="margin-top:12px">{spec("500 1px Newsreader", "49px", "Two clocks per fact")}{spec("400 1px Noto Serif SC", "39px", "每条事实两个时间")}</div></div>'
          f'<div class="s">Geist · Noto Sans SC</div><div class="i">{t("Interface: navigation, buttons, labels, short text. 400 and 500.", "界面：导航、按钮、标签、短正文。400、500。")}'
          f'<div style="margin-top:12px">{spec("500 1px Geist", "39px", "Open repository")}{spec("400 1px Noto Sans SC", "31px", "打开仓库")}</div></div>'
          f'<div class="s">DM Mono</div><div class="i">{t("Code, terminal, paths, versions. 400 and 500.", "代码、终端、路径、版本号。400、500。")}'
          f'<div style="margin-top:12px">{spec("400 1px DM Mono", "31px", "uv run zaofang-brand")}</div></div>')
    sample = t("Workshop", "作坊 Workshop")
    scale = "".join(f'<tr><td style="width:60px">{k}</td><td style="width:90px" class="m">{float(v[:-3]) * 16:.1f} px</td>'
                    f'<td style="font:500 {v} Newsreader,\'Noto Serif SC\';line-height:1.15;color:{TEXT}">{sample}</td></tr>' for k, v in reversed(TYPE_SCALE.items()))
    b.man(chapters[4], f'<div class="s" style="margin-top:0">{t("SCALE", "字号")}</div><div class="i m">{t("16 px base, ratio 1.25.", "基准 16 px，比例 1.25。")} --zf-size-*</div>'
          f'<table style="margin:10px 0 0 48px;width:calc(100% - 48px)">{scale}</table>'
          f'<div class="s">{t("SETTINGS", "设置")}</div><div class="i">' + t(
              "Headings 1.15 line height. Interface 16/1.6. Long documents may use Newsreader 18/1.6. Code 14 px. Chinese body text up to 1.7.",
              "标题行高 1.15。界面 16/1.6。长文档可用 Newsreader 18/1.6。代码 14 px。中文正文行高可放宽到 1.7。") + '</div>'
          f'<div class="s">{t("RULES", "规则")}</div><div class="i">' + t(
              "Sentence case. Versions, commands and paths always in DM Mono. The logos are drawings: never set zaofang in a font.",
              "英文标题只大写首字母。版本号、命令和路径一律用 DM Mono。标志是绘制的图形：不要用字体打出 zaofang。") + '</div>')

    # 06 Motion
    b.chapter()
    frames = [(1, "0.35 s"), (3, "0.56 s"), (7, "1.05 s"), (7, t("after 5 s, solid", "5 秒后常亮"))]
    strip = "".join(f'<div><div style="background:{BG};padding:10px">{typed(n)}</div><div class="lab cap">{c}</div></div>' for n, c in frames)
    total = TYPE_TIMES[-1] + BLINK * BLINKS
    ticks = "".join(f'<div style="position:absolute;left:{x / total * 100:.2f}%;top:0;width:2px;height:16px;background:{INK}"></div>' for x in TYPE_TIMES)
    blinks = "".join(f'<div style="position:absolute;left:{(TYPE_TIMES[-1] + .3 + i * BLINK) / total * 100:.2f}%;top:24px;'
                     f'width:{BLINK / 2 / total * 100:.2f}%;height:16px;background:{AMBER}"></div>' for i in range(BLINKS))
    b.paper(label(5), opener("06", chapters[5], t(
                "zaofang types out letter by letter with the cursor stepping after each one. Then the cursor blinks after the word "
                "and stays solid. Typed names carry no tones.",
                "zaofang 逐个字母打出，光标随每个字母前移。打完后光标在单词后闪烁，然后常亮。打出的名字不带声调。")) +
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:40px">{strip}</div>'
            f'<h2>{t("Timing", "时间")}</h2><div style="position:relative;height:44px;margin-top:8px">{ticks}{blinks}</div>'
            f'<div class="lab" style="display:flex;justify-content:space-between"><span>0 s</span><span>{total:.1f} s</span></div>'
            '<p style="margin-top:16px">' + t(
                f"First letter at {TYPE_TIMES[0]} s, the rest 0.09 to 0.15 s apart, done at {TYPE_TIMES[-1]} s. {BLINKS} blinks of "
                f"{BLINK} s, so blinking stops near five seconds (WCAG 2.2.2). With reduced motion, the finished word and a solid "
                "cursor appear at once.",
                f"第一个字母在 {TYPE_TIMES[0]} 秒出现，之后间隔 0.09 到 0.15 秒，{TYPE_TIMES[-1]} 秒打完。闪烁 {BLINKS} 次，每次 {BLINK} 秒，"
                "约五秒后停止（WCAG 2.2.2）。开启减少动态效果时，直接显示完整单词和常亮光标。") + '</p><p>' + t(
                "Interface motion: 150 to 200 ms, ease-out, no bounce. Only the cursor blinks. CLI splash: 90 ms per letter, three "
                "blinks, on first launch or <code>--version</code> only.",
                "界面动效：150 到 200 毫秒，缓出，不回弹。只有光标会闪。命令行启动画面：每个字母 90 毫秒，闪三次，"
                "只在首次启动或 <code>--version</code> 时出现。") + '</p>')

    # 07 Motifs
    b.chapter()
    b.paper(label(6), opener("07", chapters[6], t("No photography, no stock. Three generated motifs, used quietly.",
                                                  "不用照片，不用图库素材。三种程序生成的图形元素，克制地使用。")) +
            f'<div class="grid3" style="margin-top:48px">'
            f'{panel("", BG, t("Dot grid: 1.3 px dots on 24 px, text colour at 9 percent", "点阵：24 px 网格上的 1.3 px 圆点，正文色 9%"), f"height:200px;{dots(TEXT)}")}'
            f'{panel("", PAPER, t("Paper grain: 3 to 5 percent noise, paper only", "纸纹：3% 到 5% 的噪点，只用于纸色"), f"height:200px;{GRAIN};outline:1px solid {UI["border"][L]};outline-offset:-1px")}'
            f'{panel("", UI["surface"][L], t("45-degree cuts: 8 to 12 px on cards", "45° 切角：卡片 8 到 12 px"), "height:200px;clip-path:polygon(24px 0,100% 0,100% calc(100% - 24px),calc(100% - 24px) 100%,0 100%,0 24px)")}</div>'
            '<p style="margin-top:36px">' + t(
                "Diagrams use dusk, tide, sage, heather and straw, with hairline borders. Any future image follows lamplight: one "
                "warm source, low and to one side, deep shadow.",
                "图表使用暮色、潮色、鼠尾草绿、石楠紫和麦秆黄，配细线。将来如需图片，遵循灯下的光：一个暖光源，低而偏向一侧，阴影深。") + '</p><p>' + t(
                "Corners are square or cut at 45 degrees. Never rounded. No gradients, no glows, no starfields.",
                "角要么是直角，要么是 45° 切角，永远不用圆角。不用渐变，不用光晕，不要星空。") + '</p>')

    # 08 Sub-projects
    b.chapter()
    stamp = lambda text, font: (f'<div style="display:flex;align-items:center;gap:10px">{img("logo/avatar.svg", "width:24px")}'  # noqa: E731
                                f'<span style="font:14px {font}">{text}</span></div>')
    b.paper(label(7), opener("08", chapters[7], t("yan, db and what follows get their own name, colour and mark. Zaofang appears only as a stamp.",
                                                  "yan、db 以及以后的项目都有自己的名字、颜色和标志。造坊只以印记的形式出现。")) +
            f'<div class="grid2" style="margin-top:48px">{panel(stamp("a zaofang project", "DM Mono"), UI["surface"][L], t("README, site and docs footers", "README、网站和文档页脚"))}'
            f'{panel(stamp("造坊出品", "Noto Sans SC"), UI["surface"][L], t("In Chinese", "中文"))}</div>'
            f'<div style="margin-top:24px;background:{BG};color:{TEXT};padding:20px 24px" class="mono">$ yan --version<br>yan 0.4.2 · a zaofang project</div>'
            f'<div class="lab cap">{t("The --version line", "--version 输出")}</div>'
            '<ul style="margin-top:32px">' + "".join(f"<li>{x}</li>" for x in [
                t('Stamp: the 坊 avatar at 16 to 24 px, then "a zaofang project" in DM Mono, lowercase.',
                  "印记：16 到 24 px 的“坊”头像，旁边一行 DM Mono 小写文字“a zaofang project”。"),
                t("Sub-projects may share DM Mono and nothing else.", "子项目只可共用 DM Mono。"),
                t("Never lamplight amber, the teal-black ground, the cursor block, the Bevel cut, Newsreader or Geist as their identity.",
                  "不得把灯下琥珀、青黑底色、光标块、斜切体、Newsreader 或 Geist 用作子项目的识别。")]) + '</ul>')

    # 09 Applications
    b.chapter()
    rows = "".join(f'<tr><td style="width:220px">{k}</td><td class="mono" style="font-size:13px">{v}</td></tr>' for k, v in [
        (t("Site header", "网站页头"), t("logo/lockup-on-dark.svg, 28 to 32 px tall", "logo/lockup-on-dark.svg，高 28 到 32 px")),
        (t("Site hero, first visit", "网站首屏，首次访问"), "motion/typeon.svg"),
        (t("Docs", "文档"), t("tokens/tokens.css; code via Shiki with themes/vscode", "tokens/tokens.css；代码经 Shiki 使用 themes/vscode")),
        (t("GitHub org avatar", "GitHub 组织头像"), "logo/png/avatar-512.png"),
        (t("Org README", "组织 README"), "social/readme-banner-dark.svg, -light.svg"),
        (t("Repo social preview", "仓库社交预览"), "social/github-social-preview.png"),
        (t("Link previews", "链接预览"), "social/og-card.png"),
        (t("Favicon", "网站图标"), "logo/favicon.svg, favicon.ico, png/favicon-180.png"),
        (t("Terminals, editors", "终端、编辑器"), "themes/")])
    b.paper(label(8), opener("09", chapters[8], t("Each surface has its file. Use the file; do not rebuild the logo.",
                                                  "每个场景都有对应的文件。使用文件，不要自己重建标志。")) +
            f'<div class="grid2" style="margin-top:40px;align-items:end"><div>{img("social/og-card.png", "width:100%")}<div class="lab cap">{t("Link preview", "链接预览")} · social/og-card.png</div></div>'
            f'<div>{img("social/readme-banner-light.svg", "width:100%")}<div class="lab cap">{t("Org README", "组织 README")} · social/readme-banner-light.svg</div></div></div>'
            f'<table style="margin-top:28px">{rows}</table>')

    # Back cover
    b.raw(f'<section class="pg" style="background:{BG};color:{TEXT}">'
          f'<div style="position:absolute;left:76px;top:76px">{img("logo/avatar.svg", "width:64px")}</div>'
          f'<div style="position:absolute;left:76px;right:76px;bottom:64px;font:12px/1.7 \'DM Mono\',\'Noto Sans SC\';color:{UI["text-muted"][D]}">' + t(
              f"Generated by scripts/book.py from zaofang/brand {VERSION}.<br>Code, tokens and themes: MIT. Logos and the names zaofang "
              "and 造坊 are trademarks; see TRADEMARK.md.<br>Set in Newsreader, Geist, DM Mono, Noto Serif SC and Noto Sans SC, SIL Open Font License.",
              f"由 scripts/book.py 从 zaofang/brand {VERSION} 生成。<br>代码、颜色变量和主题：MIT。标志以及 zaofang、造坊两个名称是商标，见 TRADEMARK.md。"
              "<br>字体：Newsreader、Geist、DM Mono、思源宋体、思源黑体，SIL 开源字体许可。") + '</div></section>')
    toc = "".join(f'<tr><td class="lab" style="width:48px">{i + 1:02}</td><td style="font:500 22px Newsreader,\'Noto Serif SC\'">{c}</td>'
                  f'<td class="lab" style="text-align:right">{p:02}</td></tr>' for i, (c, p) in enumerate(zip(chapters, b.starts)))
    b.paper(t("contents", "目录"), f'<h1>{t("Contents", "目录")}</h1><p style="margin-top:22px">' + t(
                "Zaofang (造坊) is an open-source workshop for computer science tools: yan, a language family, and db, a bitemporal "
                "time-series database. This book sets out how the workshop looks and sounds. Every logo, colour and theme in it is "
                "generated by <code>zaofang/brand</code>; if this book and the repository disagree, the repository is right.",
                "造坊是一间做计算机科学工具的开源作坊：yan，一个语言家族；db，一个双时态时间序列数据库。本手册规定造坊的外观和语气。"
                "书中的标志、颜色和主题都由 <code>zaofang/brand</code> 生成；本手册与仓库不一致时，以仓库为准。") +
            f'</p><table style="margin-top:56px">{toc}</table>', at=2)
    return "".join(b.pages)


def clear_space(vb: list[float], w: float = 400) -> str:
    """The lockup inside its clear space: the x-height on every side. The SVG already carries its MARGIN."""
    pad = (-latin.XH - 8) * w / vb[2]
    return (f'<div style="display:inline-block;padding:{pad:.1f}px;outline:1px dashed {UI["text-muted"][L]};outline-offset:-1px;margin-top:20px">'
            f'<div style="outline:1px solid {UI["border"][L]}">{img("logo/lockup-on-light.svg", f"width:{w}px")}</div></div>')


def misuse(t) -> str:
    logo = img("logo/lockup-on-light.svg", "width:150px")
    cases = [(t("No: stretch", "不要：拉伸"), f'<div style="transform:scaleX(1.35)">{logo}</div>'),
             (t("No: rotate", "不要：旋转"), f'<div style="transform:rotate(-12deg)">{logo}</div>'),
             (t("No: recolour", "不要：改色"), f'<div style="filter:hue-rotate(160deg)">{logo}</div>'),
             (t("No: add effects", "不要：加特效"), f'<div style="filter:drop-shadow(4px 4px 0 {UI["border"][L]})">{logo}</div>'),
             (t("No: set in a font", "不要：用字体打出"), '<div style="font:500 34px Geist,\'Noto Sans SC\'">造坊 zaofang</div>'),
             (t("No: busy ground", "不要：繁杂背景"), f'<div style="padding:10px;{STRIPES}">{logo}</div>')]
    return '<div class="grid3">' + "".join(panel(c, UI["surface"][L], n, "height:130px;overflow:hidden;padding:12px") for n, c in cases) + "</div>"


FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Geist:wght@400;500"
         "&family=DM+Mono:wght@400;500&family=Noto+Serif+SC:wght@400;500&family=Noto+Sans+SC:wght@400&display=swap")


BOOKS = {"en": ("book/zaofang-brand-book.pdf", "Zaofang brand identity"), "zh": ("book/zaofang-brand-book-zh.pdf", "造坊品牌手册")}


async def main() -> None:
    (ROOT / "book").mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for lang, (out, title) in BOOKS.items():
            html = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>'
                    f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>{build(lang)}</body></html>')
            await page.set_content(html, wait_until="networkidle")
            await page.evaluate("document.fonts.ready")
            await page.pdf(path=str(ROOT / out), width="210mm", height="297mm", print_background=True, prefer_css_page_size=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
