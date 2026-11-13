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
