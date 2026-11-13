"""Lamplight: teal-black ground, warm paper, one amber cursor. Every colour Zaofang uses is defined here."""

# role -> (dark, light)
UI = {
    "bg": ("#13242A", "#F2EBDC"),          # ground: teal-black night / warm paper
    "surface": ("#1D333B", "#E6DCCA"),     # cards, code blocks
    "surface-2": ("#2B4148", "#DAD0BF"),   # hover, nested surfaces
    "border": ("#3B5159", "#C8BCA9"),
    "text": ("#F0E7D5", "#15232A"),
    "text-muted": ("#94A9B0", "#4F6168"),
    "accent": ("#F0A445", "#F0A445"),      # the cursor: fills only, the one hot thing on screen
    "on-accent": ("#13242A", "#15232A"),   # text inside the cursor block
    "accent-text": ("#F0A445", "#965808"), # amber as text (warnings); deepened on paper
    "selection": ("#234951", "#E7D5B7"),
    "link": ("#7DC4D5", "#006A7D"),        # tide
    "info": ("#7DC4D5", "#006A7D"),        # tide
    "success": ("#90D192", "#38733C"),     # sage
    "warning": ("#F0A445", "#965808"),     # amber
    "error": ("#F9875E", "#9F4325"),       # ember: errors only, never decoration
    "chart": ("#7DB0E1", "#345F95"),       # dusk
}

# Syntax: the accent stays out of code text; it is reserved for the cursor, search hits and the matching bracket.
SYNTAX = {
    "comment": ("#7F97A0", "#566970"),
    "keyword": ("#7DC4D5", "#006A7D"),     # tide
    "function": ("#7DB0E1", "#345F95"),    # dusk
    "type": ("#CBA1C6", "#7A4475"),        # heather
    "string": ("#90D192", "#38733C"),      # sage
    "number": ("#C3AA48", "#756208"),      # straw
    "variable": ("#F0E7D5", "#15232A"),
    "punctuation": ("#94A9B0", "#4F6168"),
    "invalid": ("#F9875E", "#9F4325"),     # ember
}

# 16-colour terminal palette: normal 0-7, bright 8-15. ANSI red is ember: no true red, which belongs to Yan.
ANSI = {
    "dark": ["#1D333B", "#F9875E", "#90D192", "#F0A445", "#7DB0E1", "#CBA1C6", "#7DC4D5", "#C9C1B0",
             "#50707A", "#FFA481", "#AEE5AF", "#FFBE73", "#9AC6F0", "#E0C2DC", "#9DD9E8", "#F0E7D5"],
    "light": ["#15232A", "#9F4325", "#38733C", "#965808", "#345F95", "#7A4475", "#006A7D", "#DAD0BF",
              "#50707A", "#9F4325", "#38733C", "#965808", "#345F95", "#7A4475", "#006A7D", "#E6DCCA"],
}
TERMINAL = {
    "dark": dict(bg="#13242A", fg="#F0E7D5", cursor="#F0A445", cursor_text="#13242A", sel_bg="#234951", sel_fg="#F0E7D5"),
    "light": dict(bg="#F2EBDC", fg="#15232A", cursor="#B97515", cursor_text="#F2EBDC", sel_bg="#E7D5B7", sel_fg="#15232A"),
}
# Print: role -> (sRGB for previews, CMYK percentages for press). Set by hand for coated stock, total ink 250 or less.
# Not ICC conversions: proof amber and ground before a run. Ground also prints the ink on paper; paper also prints text on ground.
PRINT = {
    "ground": ("#13242A", (80, 45, 40, 85)),
    "paper": ("#F2EBDC", (3, 4, 12, 0)),
    "amber": ("#F0A445", (0, 40, 78, 0)),
    "muted": ("#4F6168", (65, 40, 38, 30)),       # secondary text on paper
    "muted-dark": ("#94A9B0", (42, 20, 22, 4)),   # secondary text on ground
    "die": ("#7DC4D5", (0, 100, 0, 0)),           # previews only; the PDF writes the die as the CutContour spot
}
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

FONTS = {
    "display": "'Newsreader', 'Noto Serif SC', Georgia, serif",
    "text": "'Geist', 'Noto Sans SC', system-ui, -apple-system, 'Segoe UI', sans-serif",
    "mono": "'DM Mono', 'Noto Sans Mono CJK SC', ui-monospace, Menlo, Consolas, monospace",
}
# 16px base, ratio 1.25
TYPE_SCALE = {"xs": "0.8rem", "sm": "0.875rem", "base": "1rem", "lg": "1.25rem", "xl": "1.563rem", "2xl": "1.953rem",
              "3xl": "2.441rem", "4xl": "3.052rem"}


def _lin(c: float) -> float:
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return .2126 * r + .7152 * g + .0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + .05) / (lb + .05)


# Ramps --------------------------------------------------------------------------------------------------
# Twelve steps per hue and mode, one job each: 1-2 page and subtle fills, 3-5 component fills (rest, hover,
# pressed), 6-8 borders, 9 solid fill, 10 solid hover, 11 text, 12 strong text. Steps 1-8 tint the mode's own
# ground toward the hue, so dark fills keep the teal night and light fills keep the paper. 9 is the bright value
# in both modes, as the cursor is; 11 is the value UI already ships. Amber steps keep amber's four jobs.
RAMP_HUES = {"amber": UI["warning"], "ember": UI["error"], "tide": UI["link"], "sage": UI["success"],
             "dusk": UI["chart"], "heather": SYNTAX["type"], "straw": SYNTAX["number"]}
_TINT = {"dark": [.04, .08, .13, .19, .26, .34, .44, .56], "light": [.02, .04, .07, .11, .16, .22, .3, .42]}


def _gam(c: float) -> float:
    return 12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055


def oklab(h: str) -> tuple[float, float, float]:
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l, m, s = ((.4122214708 * r + .5363325363 * g + .0514459929 * b) ** (1 / 3),
               (.2119034982 * r + .6806995451 * g + .1073969566 * b) ** (1 / 3),
               (.0883024619 * r + .2817188376 * g + .6299787005 * b) ** (1 / 3))
    return (.2104542553 * l + .7936177850 * m - .0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + .4505937099 * s,
            .0259040371 * l + .7827717662 * m - .8086757660 * s)


def _srgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l, m, s = ((L + .3963377774 * a + .2158037573 * b) ** 3, (L - .1055613458 * a - .0638541728 * b) ** 3,
               (L - .0894841775 * a - 1.2914855480 * b) ** 3)
    return (4.0767416621 * l - 3.3077115913 * m + .2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s,
            -.0041960863 * l - .7034186147 * m + 1.7076147010 * s)


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(_gam(min(1, max(0, c))) * 255):02X}" for c in rgb)


def mix(x: str, y: str, t: float) -> str:
    """OKLab mix, t=0 is x."""
    return _hex(_srgb(*(p + (q - p) * t for p, q in zip(oklab(x), oklab(y)))))


def shift(h: str, dL: float, chroma: float = 1) -> str:
    """Move lightness by dL and scale chroma, hue held; chroma drops until the colour fits sRGB."""
    L, a, b = oklab(h)
    a, b = a * chroma, b * chroma
    while not all(-1e-4 <= c <= 1 + 1e-4 for c in _srgb(L + dL, a, b)):
        a, b = a * .98, b * .98
    return _hex(_srgb(L + dL, a, b))


def _ramp(dark: str, light: str, mode: str) -> list[str]:
    i = 0 if mode == "dark" else 1
    steps = [mix(UI["bg"][i], (dark, light)[i], t) for t in _TINT[mode]]
    if mode == "dark":
        return steps + [dark, shift(dark, .05), dark, shift(dark, .93 - oklab(dark)[0], .4)]
    return steps + [dark, shift(dark, -.05), light, shift(light, .32 - oklab(light)[0], .7)]


def _neutral(i: int) -> list[str]:
    bg, s1, s2, br, muted, text = (UI[k][i] for k in ("bg", "surface", "surface-2", "border", "text-muted", "text"))
    return [bg, mix(bg, s1, .5), s1, mix(s1, s2, .5), s2, mix(s2, br, .5), br, mix(br, muted, .35),
            mix(br, muted, .6), mix(br, muted, .8), muted, text]


RAMPS = {mode: {"neutral": _neutral(i), **{k: _ramp(*v, mode) for k, v in RAMP_HUES.items()}}
         for i, mode in enumerate(("dark", "light"))}
