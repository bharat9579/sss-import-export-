"""Render the 1200x630 social share images in assets/img/og/ from seo.json.

Needs Playwright (WebKit) and Pillow, which the static build does not:
    pip install playwright pillow && playwright install webkit
    python tools/og_images.py
"""
import asyncio
import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
SEO = json.loads((ROOT / 'assets/data/seo.json').read_text())
DOMAIN = urlparse(SEO['business']['domain']).netloc.upper()
FOUNDED = SEO['business']['founded']

TEMPLATE = '''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700&display=swap" rel="stylesheet">
<style>html,body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:'Plus Jakarta Sans',sans-serif}
.bg{position:absolute;top:0;bottom:0;right:0;left:LEFT;background:url(BG) center/cover}
.sh{position:absolute;inset:0;background:SHADE}
.in{position:absolute;left:72px;top:64px;bottom:64px;width:640px;display:flex;flex-direction:column;color:#F4F1E6}
.logo{display:flex;align-items:center;gap:16px}.logo img{width:64px;height:64px;background:#fff;border-radius:16px;padding:4px;box-sizing:border-box}
.logo b{font-size:28px;font-weight:700;letter-spacing:-.01em}.logo small{display:block;font-size:13px;letter-spacing:.24em;color:#F8E58C;font-weight:500;margin-top:2px}
h1{margin:auto 0 0;font-size:58px;line-height:1.05;font-weight:300;letter-spacing:-.035em;color:#FBFAF5}
p{margin:22px 0 0;font-size:24px;color:#F8E58C;font-weight:500}
.d{margin-top:34px;font-size:18px;letter-spacing:.12em;color:#B6C2D6}</style></head><body>
<div class="bg"></div><div class="sh"></div><div class="in"><div class="logo"><img src="LOGO"><div><b>SSS Import Export</b><small>THIRD GENERATION · SINCE FOUNDED</small></div></div>
<h1>TITLE</h1><p>SUB</p><div class="d">DOMAIN</div></div></body></html>'''
FULL = ('0', 'linear-gradient(90deg,rgba(0,21,48,.96) 0%,rgba(0,21,48,.86) 45%,rgba(0,21,48,.25) 100%)')
SPLIT = ('440px', 'linear-gradient(90deg,#001530 0%,#001530 40%,rgba(0,21,48,.55) 62%,rgba(0,21,48,.05) 100%)')


def jobs():
    yield ('sss-import-export-og-cover', 'hero/nashik-red-onion-big', 'Trusted importer &amp; exporter from India',
           'Onion · Fresh produce · Grains · Spices · Powders', SPLIT)
    yield ('indian-products-exporter-range', 'categories/fresh-vegetables-exporter-india-1600',
           '33 Indian products, every grade', 'Vegetables · Fruits · Spices · Herbs · Powders', FULL)
    for pg in SEO['pages']:
        yield (pg['image'].split('/', 1)[1], pg['image'] + '-1600', pg['h1'][0].upper() + pg['h1'][1:], pg['h1_em'], FULL)


async def main():
    out_dir = ROOT / 'assets/img/og'
    out_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.webkit.launch()
        page = await browser.new_page(viewport={'width': 1200, 'height': 630})
        with tempfile.TemporaryDirectory() as tmp:
            for name, img, title, sub, (left, shade) in jobs():
                html = (TEMPLATE.replace('BG', (ROOT / 'assets/img' / (img + '.webp')).as_uri())
                        .replace('LOGO', (ROOT / 'assets/img/logo-mark-256.png').as_uri())
                        .replace('LEFT', left).replace('SHADE', shade).replace('TITLE', title).replace('SUB', sub)
                        .replace('DOMAIN', DOMAIN).replace('FOUNDED', FOUNDED))
                src = Path(tmp) / 'og.html'
                src.write_text(html)
                await page.goto(src.as_uri())
                await page.wait_for_timeout(900)
                png = Path(tmp) / 'og.png'
                await page.screenshot(path=str(png))
                Image.open(png).convert('RGB').save(out_dir / f'{name}.jpg', quality=82, optimize=True, progressive=True)
                print('wrote', f'assets/img/og/{name}.jpg')
        await browser.close()


asyncio.run(main())
