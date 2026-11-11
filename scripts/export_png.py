"""PNG and ICO exports of the SVGs, plus the social cards. Needs the `png` extra: uv run --extra png scripts/export_png.py"""
import asyncio
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500&family=Geist:wght@400;500"
         "&family=DM+Mono:wght@400;500&display=swap")

SQUARES = [("logo/avatar.svg", "avatar", (256, 512, 1024)), ("logo/avatar-light.svg", "avatar-light", (512,)),
           ("logo/favicon.svg", "favicon", (16, 32, 48, 180, 192, 512))]
WIDE = [("logo/lockup-on-dark.svg", "lockup-on-dark", 1200), ("logo/lockup-on-light.svg", "lockup-on-light", 1200),
        ("logo/lockup-tones-on-dark.svg", "lockup-tones-on-dark", 1200), ("logo/lockup-tones-on-light.svg", "lockup-tones-on-light", 1200),
        ("logo/wordmark-on-dark.svg", "wordmark-on-dark", 1200), ("social/readme-banner-dark.svg", "../../social/readme-banner-dark", 1280),
        ("social/readme-banner-light.svg", "../../social/readme-banner-light", 1280)]


def card(w: int, h: int) -> str:
    lockup = base64.b64encode((ROOT / "logo/lockup-tones-on-dark.svg").read_bytes()).decode()
    return f"""<!doctype html><html><head><link rel="stylesheet" href="{FONTS}"><style>
html,body{{margin:0}} body{{width:{w}px;height:{h}px;background:#13242A;color:#F0E7D5;position:relative;overflow:hidden;
background-image:radial-gradient(rgba(240,231,213,.09) 1.3px,transparent 1.4px);background-size:24px 24px;font-family:Geist,sans-serif}}
img{{position:absolute;left:{w * .08:.0f}px;top:{h * .30:.0f}px;width:{w * .56:.0f}px}}
p{{position:absolute;left:{w * .08:.0f}px;bottom:{h * .12:.0f}px;margin:0;font:500 26px 'DM Mono',monospace;color:#94A9B0;letter-spacing:.02em}}
p b{{color:#F0E7D5;font-weight:500}}</style></head><body><img src="data:image/svg+xml;base64,{lockup}" alt="">
<p><b>yan</b> · <b>db</b> &nbsp; zaofang.sh</p></body></html>"""


async def main() -> None:
    out = ROOT / "logo/png"
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        async def shot(svg: str, w: int, h: int) -> bytes:
            data = base64.b64encode((ROOT / svg).read_bytes()).decode()
            await page.set_viewport_size({"width": w, "height": h})
            await page.set_content(f'<html><body style="margin:0"><img src="data:image/svg+xml;base64,{data}" width="{w}" height="{h}" style="display:block"></body></html>')
            return await page.screenshot(omit_background=True)

        for svg, name, sizes in SQUARES:
            for s in sizes:
                (out / f"{name}-{s}.png").write_bytes(await shot(svg, s, s))
        icons = [Image.open(BytesIO((out / f"favicon-{s}.png").read_bytes())) for s in (16, 32, 48)]
        icons[0].save(ROOT / "logo/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=icons[1:])
        for svg, name, w in WIDE:
            vb = (ROOT / svg).read_text().split('viewBox="')[1].split('"')[0].split()
            h = round(w * float(vb[3]) / float(vb[2]))
            (out / f"{name}.png").write_bytes(await shot(svg, w, h))
        for name, (w, h) in (("og-card", (1200, 630)), ("github-social-preview", (1280, 640))):
            await page.set_viewport_size({"width": w, "height": h})
            await page.set_content(card(w, h))
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(ROOT / f"social/{name}.png"))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
