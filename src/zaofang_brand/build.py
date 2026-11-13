"""Write every brand file from the drawing code and the palette. Run: uv run zaofang-brand"""
import json
from pathlib import Path

from . import latin, logos
from .geometry import dnotch, to_d
from .palette import ANSI, ANSI_NAMES, FONTS, RAMPS, SYNTAX, TERMINAL, TYPE_SCALE, UI

ROOT = Path(__file__).resolve().parents[2]
ON_DARK = dict(ink=UI["text"][0], accent=UI["accent"][0], sel=UI["bg"][0])
ON_LIGHT = dict(ink=UI["text"][1], accent=UI["accent"][1], sel=UI["text"][1])
NAME = "Zaofang Lamplight"


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# Logos -----------------------------------------------------------------------------------------------
def build_logos() -> None:
    sets = {"lockup": (logos.lockup(), "造坊 zaofang"), "lockup-tones": (logos.lockup(tones=True), "造坊 zàofáng"),
            "mark": (logos.mark(), "造坊"), "wordmark": (logos.wordmark(), "zaofang"),
            "wordmark-tones": (logos.wordmark(tones=True), "zàofáng")}
    for name, (logo, title) in sets.items():
        write(f"logo/{name}-on-dark.svg", logos.svg(logo, ON_DARK, title=title))
        write(f"logo/{name}-on-light.svg", logos.svg(logo, ON_LIGHT, title=title))
        write(f"logo/{name}-mono.svg", logos.svg(logo, None, title=title))
    sq = (0, 0, 100, 100)
    write("logo/avatar.svg", logos.svg(logos.avatar(), ON_DARK, view=sq, background=UI["bg"][0], title="坊"))
    write("logo/avatar-light.svg", logos.svg(logos.avatar(), ON_LIGHT, view=sq, background=UI["bg"][1], title="坊"))
    write("logo/favicon.svg", logos.svg(logos.favicon(), ON_DARK, view=sq, title="坊"))


def _dots(fid: str, colour: str, step: int = 24, opacity: float = .09) -> tuple[str, str]:
    defs = (f'<pattern id="{fid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step / 2}" cy="{step / 2}" r="1.3" fill="{colour}" fill-opacity="{opacity}"/></pattern>')
    return defs, f'<rect width="100%" height="100%" fill="url(#{fid})"/>'


def banner(mode: int, w: int = 1280, h: int = 320, logo_w: float = 560) -> str:
    """README banner: the lockup with tones (a large use) centred on the ground, over a dot grid."""
    logo = logos.lockup(tones=True)
    x0, y0, x1, y1 = logo.bounds
    s = logo_w / (x1 - x0)
    tx, ty = (w - logo_w) / 2 - x0 * s, (h - (y1 - y0) * s) / 2 - y0 * s
    c = ON_DARK if mode == 0 else ON_LIGHT
    defs, dots = _dots("d", UI["text"][mode])
    inner = (f'<path d="{to_d(logo.ink)}" fill="{c["ink"]}"/><path d="{to_d(logo.block)}" fill="{c["accent"]}"/>'
             f'<path d="{to_d(logo.sel)}" fill="{c["sel"]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="造坊 zàofáng">'
            f'<title>造坊 zàofáng</title><defs>{defs}</defs><rect width="100%" height="100%" fill="{UI["bg"][mode]}"/>{dots}'
            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{inner}</g></svg>\n')


def build_banners() -> None:
    write("social/readme-banner-dark.svg", banner(0))
    write("social/readme-banner-light.svg", banner(1))


# Motion ----------------------------------------------------------------------------------------------
TYPE_TIMES = [0.35, 0.47, 0.56, 0.71, 0.82, 0.95, 1.05]  # seconds; uneven, like a person typing
BLINK, BLINKS = 1.06, 5  # stops after about five seconds, then stays solid


def typeon_svg() -> str:
    """zaofang typed letter by letter, a block cursor stepping after each one, then blinking after the word."""
    parts = latin.placed()
    right = [p.bounds[2] for p in parts]
    cur_w, gap = 28.0, 10.0
    cursor = dnotch(0, -64, cur_w, 4, 7)
    x0 = parts[0].bounds[0] - 8
    x1 = right[-1] + gap + cur_w + 8
    end = TYPE_TIMES[-1]
    total = end + BLINK * BLINKS
    letters_css = "".join(f".l{i}{{animation:show 0s {t}s both}}" for i, t in enumerate(TYPE_TIMES))
    stops = [(0.0, 0.0)] + [(t, right[i] + gap) for i, t in enumerate(TYPE_TIMES)]
    kf = "".join(f"{t / total * 100:.3f}%{{transform:translateX({x:.2f}px)}}" for t, x in stops) + f"100%{{transform:translateX({stops[-1][1]:.2f}px)}}"
    blink_start = end + .3
    css = (f"@keyframes show{{from{{opacity:0}}to{{opacity:1}}}}"
           f"@keyframes move{{{kf}}}"
           f"@keyframes blink{{0%,49.9%{{opacity:1}}50%,100%{{opacity:0}}}}"
           f".l{{opacity:0}}{letters_css}"
           f".c{{animation:move {total:.2f}s steps(1,end) both}}"
           f".c path{{animation:blink {BLINK}s {blink_start:.2f}s {BLINKS} step-end}}"
           f"@media (prefers-reduced-motion:reduce){{.l,.c,.c path{{animation:none;opacity:1}}.c{{transform:translateX({stops[-1][1]:.2f}px)}}}}")
    letters_svg = "".join(f'<path class="l l{i}" d="{to_d(p)}" fill="{UI["text"][0]}"/>' for i, p in enumerate(parts))
    w, h = x1 - x0, latin.BLOCK_BOT - latin.BLOCK_TOP + 16
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {latin.BLOCK_TOP - 8:.2f} {w:.2f} {h:.2f}" width="{w * 2:.0f}" height="{h * 2:.0f}" '
            f'role="img" aria-label="zaofang"><title>zaofang</title><style>{css}</style>'
            f'<rect x="{x0:.2f}" y="{latin.BLOCK_TOP - 8:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{UI["bg"][0]}"/>'
            f'{letters_svg}<g class="c"><path d="{to_d(cursor)}" fill="{UI["accent"][0]}"/></g></svg>\n')


SPLASH = r"""#!/bin/sh
# zaofang CLI splash: types the name, then blinks a block cursor three times and leaves it on.
# Truecolor escapes; terminals without truecolor show the nearest colour.
ink='\033[38;2;240;231;213m'; amber='\033[38;2;240;164;69m'; reset='\033[0m'
printf '\033[?25l'
for ch in z a o f a n g; do printf "${ink}%s${reset}" "$ch"; sleep 0.09; done
printf ' '
for i in 1 2 3; do printf "${amber}\342\226\210${reset}"; sleep 0.53; printf '\b \b'; sleep 0.53; done
printf "${amber}\342\226\210${reset}\n\033[?25h"
"""


def build_motion() -> None:
    write("motion/typeon.svg", typeon_svg())
    write("motion/splash.sh", SPLASH)
    (ROOT / "motion/splash.sh").chmod(0o755)


# Tokens ----------------------------------------------------------------------------------------------
def build_tokens() -> None:
    def block(i: int) -> str:
        rows = [f"  --zf-{k}: {v[i]};" for k, v in UI.items()] + [f"  --zf-code-{k}: {v[i]};" for k, v in SYNTAX.items()]
        rows += [f"  --zf-{h}-{n}: {c};" for h, r in RAMPS[("dark", "light")[i]].items() for n, c in enumerate(r, 1)]
        return "\n".join(rows)
    fonts = "\n".join(f"  --zf-font-{k}: {v};" for k, v in FONTS.items())
    scale = "\n".join(f"  --zf-size-{k}: {v};" for k, v in TYPE_SCALE.items())
    css = f"""/* Zaofang Lamplight tokens. Dark first: dark on :root, light under prefers-color-scheme and [data-theme="light"]. */
:root {{
{block(0)}
{fonts}
{scale}
  color-scheme: dark;
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
{block(1).replace("  --", "    --")}
    color-scheme: light;
  }}
}}
:root[data-theme="light"] {{
{block(1)}
  color-scheme: light;
}}
"""
    write("tokens/tokens.css", css)
    col = lambda v: {"$type": "color", "$value": v}  # noqa: E731
    tokens = {"color": {mode: {**{k: col(v[i]) for k, v in UI.items()}, "code": {k: col(v[i]) for k, v in SYNTAX.items()},
                               "ansi": {str(n): col(c) for n, c in enumerate(ANSI[mode])},
                               "ramp": {h: {str(n): col(c) for n, c in enumerate(r, 1)} for h, r in RAMPS[mode].items()}}
                        for i, mode in enumerate(("dark", "light"))},
              "font": {k: {"$type": "fontFamily", "$value": [f.strip().strip("'") for f in v.split(",")]} for k, v in FONTS.items()},
              "size": {k: {"$type": "dimension", "$value": v} for k, v in TYPE_SCALE.items()}}
    write("tokens/tokens.json", json.dumps(tokens, indent=2, ensure_ascii=False) + "\n")


# Terminal themes -------------------------------------------------------------------------------------
def build_terminal() -> None:
    for mode, i in (("dark", 0), ("light", 1)):
        t, a, n = TERMINAL[mode], ANSI[mode], f"zaofang-lamplight-{mode}"
        write(f"themes/ghostty/{n}", "".join(f"palette = {k}={c}\n" for k, c in enumerate(a))
              + f"background = {t['bg']}\nforeground = {t['fg']}\ncursor-color = {t['cursor']}\ncursor-text = {t['cursor_text']}\n"
                f"selection-background = {t['sel_bg']}\nselection-foreground = {t['sel_fg']}\n")
        write(f"themes/alacritty/{n}.toml",
              f"[colors.primary]\nbackground = \"{t['bg']}\"\nforeground = \"{t['fg']}\"\n\n"
              f"[colors.cursor]\ncursor = \"{t['cursor']}\"\ntext = \"{t['cursor_text']}\"\n\n"
              f"[colors.selection]\nbackground = \"{t['sel_bg']}\"\ntext = \"{t['sel_fg']}\"\n\n"
              + "[colors.normal]\n" + "".join(f"{nm} = \"{a[k]}\"\n" for k, nm in enumerate(ANSI_NAMES))
              + "\n[colors.bright]\n" + "".join(f"{nm} = \"{a[k + 8]}\"\n" for k, nm in enumerate(ANSI_NAMES)))
        write(f"themes/kitty/{n}.conf",
              f"background {t['bg']}\nforeground {t['fg']}\ncursor {t['cursor']}\ncursor_text_color {t['cursor_text']}\n"
              f"selection_background {t['sel_bg']}\nselection_foreground {t['sel_fg']}\n" + "".join(f"color{k} {c}\n" for k, c in enumerate(a)))
        q = lambda xs: ", ".join(f'"{x}"' for x in xs)  # noqa: E731
        write(f"themes/wezterm/{n}.toml",
              f"[colors]\nbackground = \"{t['bg']}\"\nforeground = \"{t['fg']}\"\ncursor_bg = \"{t['cursor']}\"\ncursor_fg = \"{t['cursor_text']}\"\n"
              f"cursor_border = \"{t['cursor']}\"\nselection_bg = \"{t['sel_bg']}\"\nselection_fg = \"{t['sel_fg']}\"\n"
              f"ansi = [{q(a[:8])}]\nbrights = [{q(a[8:])}]\n\n[metadata]\nname = \"{NAME} {mode.title()}\"\n")
    wt = []
    for mode in ("dark", "light"):
        t, a = TERMINAL[mode], ANSI[mode]
        names = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
        s = {"name": f"{NAME} {mode.title()}", "background": t["bg"], "foreground": t["fg"], "cursorColor": t["cursor"],
             "selectionBackground": t["sel_bg"]}
        s |= {nm: a[k] for k, nm in enumerate(names)} | {"bright" + nm.title(): a[k + 8] for k, nm in enumerate(names)}
        wt.append(s)
    write("themes/windows-terminal/schemes.json", json.dumps({"schemes": wt}, indent=2) + "\n")


# Editor themes ---------------------------------------------------------------------------------------
def _alpha(h: str, a: float) -> str:
    return f"{h}{round(a * 255):02X}"


def vscode_theme(i: int) -> dict:
    u = {k: v[i] for k, v in UI.items()}
    s = {k: v[i] for k, v in SYNTAX.items()}
    a = ANSI["dark" if i == 0 else "light"]
    term = {f"terminal.ansi{'Bright' if k >= 8 else ''}{['Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White'][k % 8]}": c
            for k, c in enumerate(a)}
    colors = {
        "editor.background": u["bg"], "editor.foreground": u["text"], "editorCursor.foreground": TERMINAL["dark" if i == 0 else "light"]["cursor"],
        "editorCursor.background": u["on-accent"], "editor.selectionBackground": u["selection"],
        "editor.lineHighlightBackground": _alpha(u["surface"], .6), "editorLineNumber.foreground": u["border"] if i == 0 else u["text-muted"],
        "editorLineNumber.activeForeground": u["text"], "editorBracketMatch.border": u["accent"], "editorBracketMatch.background": "#00000000",
        "editor.findMatchBackground": _alpha(u["accent"], .55), "editor.findMatchHighlightBackground": _alpha(u["accent"], .22),
        "editorWhitespace.foreground": u["border"], "editorIndentGuide.background1": u["surface-2"], "editorIndentGuide.activeBackground1": u["border"],
        "editorGutter.background": u["bg"], "editorError.foreground": u["error"], "editorWarning.foreground": u["warning"],
        "editorInfo.foreground": u["info"], "focusBorder": u["link"], "foreground": u["text"], "descriptionForeground": u["text-muted"],
        "textLink.foreground": u["link"], "textLink.activeForeground": u["link"], "errorForeground": u["error"],
        "sideBar.background": u["bg"], "sideBar.foreground": u["text-muted"], "sideBar.border": u["surface"],
        "sideBarSectionHeader.background": u["bg"], "sideBarTitle.foreground": u["text"],
        "activityBar.background": u["bg"], "activityBar.foreground": u["text"], "activityBar.inactiveForeground": u["text-muted"],
        "activityBarBadge.background": u["accent"], "activityBarBadge.foreground": u["on-accent"], "activityBar.border": u["surface"],
        "statusBar.background": u["surface"], "statusBar.foreground": u["text-muted"], "statusBar.border": u["surface"],
        "statusBarItem.remoteBackground": u["accent"], "statusBarItem.remoteForeground": u["on-accent"],
        "titleBar.activeBackground": u["bg"], "titleBar.activeForeground": u["text"], "titleBar.inactiveBackground": u["bg"],
        "tab.activeBackground": u["bg"], "tab.inactiveBackground": u["surface"], "tab.activeForeground": u["text"],
        "tab.inactiveForeground": u["text-muted"], "tab.activeBorderTop": u["accent"], "tab.border": u["surface"],
        "editorGroupHeader.tabsBackground": u["surface"], "panel.background": u["bg"], "panel.border": u["surface-2"],
        "terminal.background": u["bg"], "terminal.foreground": u["text"], "terminalCursor.foreground": TERMINAL["dark" if i == 0 else "light"]["cursor"],
        "button.background": u["accent"], "button.foreground": u["on-accent"], "button.hoverBackground": u["accent"],
        "input.background": u["surface"], "input.border": u["border"], "input.foreground": u["text"], "input.placeholderForeground": u["text-muted"],
        "dropdown.background": u["surface"], "dropdown.border": u["border"], "badge.background": u["surface-2"], "badge.foreground": u["text"],
        "list.activeSelectionBackground": u["selection"], "list.activeSelectionForeground": u["text"], "list.hoverBackground": u["surface"],
        "list.inactiveSelectionBackground": u["surface"], "list.highlightForeground": u["link"],
        "gitDecoration.addedResourceForeground": u["success"], "gitDecoration.modifiedResourceForeground": u["chart"],
        "gitDecoration.deletedResourceForeground": u["error"], "gitDecoration.untrackedResourceForeground": u["success"],
        "editorWidget.background": u["surface"], "editorWidget.border": u["border"], "scrollbarSlider.background": _alpha(u["border"], .5),
        **term,
    }

    def rule(scope, key, style=None):
        r = {"scope": scope, "settings": {"foreground": s[key]}}
        if style:
            r["settings"]["fontStyle"] = style
        return r
    tokens = [
        rule(["comment", "punctuation.definition.comment"], "comment", "italic"),
        rule(["keyword", "storage.type", "storage.modifier", "keyword.control", "keyword.other"], "keyword"),
        rule(["entity.name.function", "support.function", "meta.function-call.generic"], "function"),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class", "storage.type.primitive", "entity.other.inherited-class"], "type"),
        rule(["string", "string.quoted", "punctuation.definition.string"], "string"),
        rule(["constant.numeric", "constant.language", "constant.character", "constant.other"], "number"),
        rule(["variable", "variable.parameter", "variable.other"], "variable"),
        rule(["punctuation", "keyword.operator", "meta.brace"], "punctuation"),
        rule(["invalid", "invalid.illegal"], "invalid", "underline"),
        rule(["markup.heading", "entity.name.section"], "keyword", "bold"),
        rule(["markup.inline.raw", "markup.fenced_code"], "string"),
        rule(["markup.underline.link", "markup.link"], "keyword", "underline"),
        {"scope": "markup.italic", "settings": {"fontStyle": "italic"}},
        {"scope": "markup.bold", "settings": {"fontStyle": "bold"}},
    ]
    semantic = {"function": s["function"], "method": s["function"], "type": s["type"], "class": s["type"], "interface": s["type"],
                "enum": s["type"], "keyword": s["keyword"], "string": s["string"], "number": s["number"], "variable": s["variable"],
                "parameter": s["variable"], "property": s["variable"], "comment": {"foreground": s["comment"], "italic": True}}
    return {"name": f"{NAME} {'Dark' if i == 0 else 'Light'}", "type": "dark" if i == 0 else "light", "semanticHighlighting": True,
            "colors": colors, "tokenColors": tokens, "semanticTokenColors": semantic}


def build_vscode() -> None:
    files = []
    for i, mode in enumerate(("dark", "light")):
        fn = f"themes/zaofang-lamplight-{mode}-color-theme.json"
        write(f"themes/vscode/{fn}", json.dumps(vscode_theme(i), indent=2) + "\n")
        files.append({"label": f"{NAME} {mode.title()}", "uiTheme": "vs-dark" if i == 0 else "vs", "path": f"./{fn}"})
    pkg = {"name": "zaofang-lamplight", "displayName": NAME, "description": "Zaofang's Lamplight colours: teal-black, warm paper, one amber cursor.",
           "version": "1.0.0", "publisher": "zaofang", "engines": {"vscode": "^1.80.0"}, "categories": ["Themes"],
           "contributes": {"themes": files}}
    write("themes/vscode/package.json", json.dumps(pkg, indent=2) + "\n")


def nvim_lua() -> str:
    def table(i: int) -> str:
        vals = {k.replace("-", "_"): v[i] for k, v in UI.items()} | {"c_" + k: v[i] for k, v in SYNTAX.items()}
        vals["cursor"] = TERMINAL["dark" if i == 0 else "light"]["cursor"]
        return "{ " + ", ".join(f'{k} = "{v}"' for k, v in vals.items()) + " }"
    ansi = lambda m: "{ " + ", ".join(f'"{c}"' for c in ANSI[m]) + " }"  # noqa: E731
    return f'''-- Zaofang Lamplight for Neovim. Follows 'background': dark by default, light when set to light.
local palettes = {{
  dark = {table(0)},
  light = {table(1)},
}}
local ansi = {{ dark = {ansi("dark")}, light = {ansi("light")} }}

vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
vim.g.colors_name = "zaofang"
local mode = vim.o.background == "light" and "light" or "dark"
local c = palettes[mode]
for i, col in ipairs(ansi[mode]) do vim.g["terminal_color_" .. (i - 1)] = col end

local function hl(group, opts) vim.api.nvim_set_hl(0, group, opts) end
hl("Normal", {{ fg = c.text, bg = c.bg }})
hl("NormalFloat", {{ fg = c.text, bg = c.surface }})
hl("FloatBorder", {{ fg = c.border, bg = c.surface }})
hl("Cursor", {{ fg = c.on_accent, bg = c.cursor }})
hl("CursorLine", {{ bg = c.surface }})
hl("CursorLineNr", {{ fg = c.text }})
hl("LineNr", {{ fg = c.text_muted }})
hl("SignColumn", {{ bg = c.bg }})
hl("Visual", {{ bg = c.selection }})
hl("Search", {{ fg = c.on_accent, bg = c.accent }})
hl("IncSearch", {{ fg = c.on_accent, bg = c.accent, bold = true }})
hl("CurSearch", {{ link = "IncSearch" }})
hl("MatchParen", {{ fg = c.accent_text, bold = true, underline = true }})
hl("Todo", {{ fg = c.on_accent, bg = c.accent, bold = true }})
hl("StatusLine", {{ fg = c.text_muted, bg = c.surface }})
hl("StatusLineNC", {{ fg = c.text_muted, bg = c.bg }})
hl("WinSeparator", {{ fg = c.surface_2 }})
hl("Pmenu", {{ fg = c.text, bg = c.surface }})
hl("PmenuSel", {{ fg = c.text, bg = c.selection }})
hl("TabLine", {{ fg = c.text_muted, bg = c.surface }})
hl("TabLineSel", {{ fg = c.text, bg = c.bg }})
hl("TabLineFill", {{ bg = c.surface }})
hl("Title", {{ fg = c.text, bold = true }})
hl("Directory", {{ fg = c.link }})
hl("NonText", {{ fg = c.border }})
hl("Whitespace", {{ fg = c.border }})
hl("Comment", {{ fg = c.c_comment, italic = true }})
hl("Constant", {{ fg = c.c_number }})
hl("String", {{ fg = c.c_string }})
hl("Character", {{ fg = c.c_string }})
hl("Identifier", {{ fg = c.c_variable }})
hl("Function", {{ fg = c.c_function }})
hl("Statement", {{ fg = c.c_keyword }})
hl("Keyword", {{ fg = c.c_keyword }})
hl("PreProc", {{ fg = c.c_keyword }})
hl("Type", {{ fg = c.c_type }})
hl("Special", {{ fg = c.link }})
hl("Operator", {{ fg = c.c_punctuation }})
hl("Delimiter", {{ fg = c.c_punctuation }})
hl("Underlined", {{ fg = c.link, underline = true }})
hl("Error", {{ fg = c.error }})
hl("ErrorMsg", {{ fg = c.error }})
hl("WarningMsg", {{ fg = c.warning }})
hl("DiagnosticError", {{ fg = c.error }})
hl("DiagnosticWarn", {{ fg = c.warning }})
hl("DiagnosticInfo", {{ fg = c.info }})
hl("DiagnosticHint", {{ fg = c.text_muted }})
hl("DiagnosticOk", {{ fg = c.success }})
hl("DiagnosticUnderlineError", {{ undercurl = true, sp = c.error }})
hl("DiagnosticUnderlineWarn", {{ undercurl = true, sp = c.warning }})
hl("DiffAdd", {{ fg = c.success }})
hl("DiffChange", {{ fg = c.chart }})
hl("DiffDelete", {{ fg = c.error }})
hl("@comment", {{ link = "Comment" }})
hl("@keyword", {{ link = "Keyword" }})
hl("@function", {{ link = "Function" }})
hl("@function.call", {{ link = "Function" }})
hl("@type", {{ link = "Type" }})
hl("@string", {{ link = "String" }})
hl("@number", {{ link = "Constant" }})
hl("@boolean", {{ link = "Constant" }})
hl("@constant", {{ link = "Constant" }})
hl("@variable", {{ link = "Identifier" }})
hl("@punctuation", {{ link = "Delimiter" }})
hl("@operator", {{ link = "Operator" }})
'''


def main() -> None:
    build_logos()
    build_banners()
    build_motion()
    build_tokens()
    build_terminal()
    build_vscode()
    write("themes/nvim/colors/zaofang.lua", nvim_lua())
    print("wrote", ROOT)


if __name__ == "__main__":
    main()
