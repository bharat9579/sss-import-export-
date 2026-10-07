#!/usr/bin/env python3
"""
SSS Import Export — static build step.

Run after editing products.json or the shared header/footer below:

    python3 tools/build.py

It rewrites the regions between <!-- BEGIN:name --> / <!-- END:name --> markers in
index.html, products.html and contact.html, regenerates assets/js/products-data.js,
and bumps the ?v= cache-busting version on CSS/JS links. Pages stay plain HTML,
so the site deploys as-is (no build needed on the server).
"""
import json, re, time
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'assets/data/products.json').read_text())
CATS = {c['id']: c for c in DATA['categories']}
PRODUCTS = DATA['products']
VERSION = time.strftime('%Y%m%d%H%M')

# Set this once you have a domain, e.g. 'https://www.sssimportexport.com' (no trailing slash),
# then run the build — it fills in canonical/OG/schema URLs and writes sitemap.xml + robots.txt.
SITE_URL = '[SITE_URL]'
SITE_SET = '[' not in SITE_URL

ICON = {
    'arrow': '<svg class="arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'pin': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21Z" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="9.5" r="2.5" stroke="currentColor" stroke-width="2"/></svg>',
    'wa': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.05 2C6.53 2 2.06 6.47 2.06 11.99c0 1.76.46 3.48 1.34 5L2 22l5.13-1.35a9.93 9.93 0 0 0 4.92 1.3h.01c5.51 0 9.99-4.47 9.99-9.99A9.98 9.98 0 0 0 12.05 2Zm5.83 14.15c-.25.69-1.44 1.32-2 1.4-.51.08-1.16.11-1.87-.12-.43-.14-.98-.32-1.69-.62-2.98-1.29-4.93-4.29-5.08-4.49-.15-.2-1.21-1.61-1.21-3.07 0-1.46.77-2.18 1.04-2.48.27-.3.6-.37.8-.37h.57c.18 0 .43-.07.67.51.25.6.84 2.06.92 2.21.07.15.12.32.02.52-.1.2-.15.32-.3.5-.15.17-.31.39-.45.52-.15.15-.3.31-.13.61.17.3.77 1.27 1.65 2.06 1.14 1.01 2.09 1.33 2.39 1.48.3.15.47.12.65-.07.17-.2.74-.87.94-1.16.2-.3.4-.25.67-.15.27.1 1.73.82 2.03.97.3.15.5.22.57.35.07.12.07.72-.18 1.41Z"/></svg>',
    'phone': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.9 21 3 13.1 3 3.9c0-.6.4-1 1-1h3.4c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1L6.6 10.8Z" fill="currentColor"/></svg>',
    'mail': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="m4 7 8 6 8-6" stroke="currentColor" stroke-width="1.7"/></svg>',
    'ig': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5" stroke="currentColor" stroke-width="1.7"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/></svg>',
}


def img_set(folder, name, alt, sizes, eager=False, extra=''):
    base = f'assets/img/{folder + "/" if folder else ""}{name}'
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{base}-800.webp" srcset="{base}-800.webp 800w, {base}-1600.webp 1600w" '
            f'sizes="{sizes}" alt="{escape(alt)}" {loading} decoding="async" width="1600" height="1200"{extra}>')


def contact_href(product):
    return f'contact.html?product={quote(product)}'


# ---------------------------------------------------------------- header
def header(page):
    home = '' if page == 'home' else 'index.html'
    links = [
        ('Home', f'{home}#home' if page == 'home' else 'index.html', page == 'home'),
        ('About', f'{home}#about', False),
        ('Products', 'products.html', page == 'products'),
        ('Quality', f'{home}#quality', False),
        ('Global Reach', f'{home}#global', False),
        ('Contact', 'contact.html', page == 'contact'),
    ]
    ac = ' aria-current="page"'
    nav = ''.join(f'<a href="{h}"{ac if cur else ""}>{t}</a>' for t, h, cur in links)
    menu = ''.join(f'<a class="menu__link" href="{h}"{ac if cur else ""}>{t}</a>' for t, h, cur in links)
    solid = '' if page == 'home' else ' nav--solid'
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <filter id="liquid-glass" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.008 0.012" numOctaves="2" seed="7" result="noise"/>
    <feGaussianBlur in="noise" stdDeviation="2" result="soft"/>
    <feDisplacementMap in="SourceGraphic" in2="soft" scale="26" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
<header class="nav{solid}" id="nav">
  <div class="nav__bar">
    <a href="{'#home' if page == 'home' else 'index.html'}" class="logo" aria-label="SSS Import Export — home">
      <span class="logo__mark" aria-hidden="true">SSS</span>
      <span class="logo__text"><span class="logo__name">SSS Import Export</span><span class="logo__sub">Third generation</span></span>
    </a>
    <nav class="nav__links" aria-label="Main">{nav}</nav>
    <div class="nav__actions">
      <a href="contact.html" class="btn btn--butter btn--sm nav__cta" data-magnetic>Request a Quote</a>
      <button class="nav__toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="menu-scrim" data-menu-close></div>
<nav class="menu" id="menu" aria-label="Mobile">
  {menu}
  <div class="menu__foot">
    <a href="contact.html" class="btn btn--butter">Request a Quote {ICON['arrow']}</a>
    <a href="#" class="btn btn--wa" data-wa>{ICON['wa']} WhatsApp</a>
    <a href="#" class="btn btn--glass" data-tel>{ICON['phone']} Call</a>
  </div>
</nav>'''


# ---------------------------------------------------------------- footer
def footer(page):
    home = '' if page == 'home' else 'index.html'
    cats = ''.join(f'<li><a href="products.html?category={c["id"]}">{c["name"]}</a></li>' for c in DATA['categories'])
    return f'''<footer class="footer on-dark">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <a href="{'#home' if page == 'home' else 'index.html'}" class="logo"><span class="logo__mark" aria-hidden="true">SSS</span><span class="logo__text"><span class="logo__name">SSS Import Export</span><span class="logo__sub">Quality assured · priced for you</span></span></a>
        <p>A 3rd-generation Indian import-export house supplying origin-sourced fresh produce, spices, herbs and powders to buyers in India and abroad.</p>
        <div class="footer__badges" aria-label="Registrations"><span>FSSAI</span><span>APEDA</span><span>IEC</span><span>SPICES BOARD</span></div>
      </div>
      <div>
        <h4>Company</h4>
        <ul class="footer__list">
          <li><a href="{home}#about">About</a></li>
          <li><a href="{home}#quality">Quality</a></li>
          <li><a href="{home}#global">Global Reach</a></li>
          <li><a href="{home}#packaging">Packaging &amp; Shipping</a></li>
          <li><a href="contact.html">Request a Quote</a></li>
        </ul>
      </div>
      <div>
        <h4>Products</h4>
        <ul class="footer__list">{cats}</ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul class="footer__list footer__contact">
          <li>{ICON['pin']}<span data-cfg="address">[ADDRESS]</span></li>
          <li>{ICON['phone']}<a href="#" data-tel data-cfg="phoneDisplay">[PHONE_NUMBER]</a></li>
          <li>{ICON['wa']}<a href="#" data-wa>WhatsApp us</a></li>
          <li>{ICON['mail']}<a href="#" data-mail data-cfg="email">[EMAIL]</a></li>
          <li>{ICON['ig']}<a href="https://instagram.com/sssimportexport" target="_blank" rel="noopener">@sssimportexport</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>&copy; <span data-year>{time.strftime('%Y')}</span> SSS Import Export. All rights reserved.</span>
      <span>IEC: <span class="ph">[IEC_NUMBER]</span> · FSSAI: <span class="ph">[FSSAI_LICENSE_NUMBER]</span></span>
    </div>
  </div>
</footer>
<a href="#" class="wa-fab" data-wa aria-label="Chat with SSS Import Export on WhatsApp">{ICON['wa']}<span class="wa-fab__tip">Chat on WhatsApp</span></a>'''


# ---------------------------------------------------------------- home: category cards
def categories():
    cards = []
    for c in DATA['categories']:
        items = [p['name'].split(' — ')[0] for p in PRODUCTS if p['category'] == c['id']]
        seen = []
        for i in items:
            if i not in seen:
                seen.append(i)
        cards.append(f'''      <article class="cat" data-reveal>
        <div class="cat__img">{img_set('categories', c['image'], c['name'] + ' sourced from India', '(max-width: 640px) 100vw, (max-width: 980px) 50vw, 40vw')}</div>
        <span class="glass cat__origin" data-glass>{ICON['pin']}{escape(c['origins'])}</span>
        <div class="glass cat__body" data-glass>
          <h3>{escape(c['name'])}</h3>
          <p>{escape(c['desc'])}</p>
          <p class="cat__items">{escape(' · '.join(seen))}</p>
          <div class="cat__actions">
            <a href="{contact_href(c['name'])}" class="btn btn--butter btn--sm">Enquire</a>
            <a href="products.html?category={c['id']}" class="btn btn--glass btn--sm">View {escape(c['short'].lower())} {ICON['arrow']}</a>
          </div>
        </div>
      </article>''')
    return '    <div class="cats">\n' + '\n'.join(cards) + '\n    </div>'


# ---------------------------------------------------------------- products page grid
def product_grid():
    cards = []
    for p in PRODUCTS:
        cat = CATS[p['category']]
        search = ' '.join([p['name'], cat['name'], p['origin'], p['state'], ' '.join(p['varieties'])]).lower()
        cards.append(f'''        <article class="pcard" id="{p['id']}" data-id="{p['id']}" data-cat="{p['category']}" data-state="{escape(p['state'])}" data-search="{escape(search)}">
          <div class="pcard__img">{img_set('products', p['id'], p['name'] + ' from ' + p['origin'] + ', ' + p['state'], '(max-width: 380px) 100vw, (max-width: 980px) 50vw, 25vw')}
            <span class="glass pcard__origin" data-glass>{ICON['pin']}{escape(p['origin'])}, {escape(p['state'])}</span>
          </div>
          <div class="pcard__body">
            <span class="pcard__cat">{escape(cat['short'])}</span>
            <h3>{escape(p['name'])}</h3>
            <p>{escape(p['desc'])}</p>
            <div class="pcard__actions">
              <button type="button" class="btn btn--line" data-open="{p['id']}" aria-haspopup="dialog">Details</button>
              <a href="{contact_href(p['name'])}" class="btn btn--oxford">Enquire</a>
            </div>
          </div>
        </article>''')
    return '      <div class="grid-products" id="grid">\n' + '\n'.join(cards) + '\n      </div>'


# ---------------------------------------------------------------- JSON-LD
def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'


ORG = {
    '@context': 'https://schema.org', '@type': 'Organization', 'name': 'SSS Import Export',
    'url': '[SITE_URL]', 'logo': '[SITE_URL]/assets/img/favicon.svg',
    'description': '3rd-generation Indian import-export house supplying origin-sourced fresh vegetables, fruits, spices, herbs and powders.',
    'areaServed': ['India', 'United Arab Emirates', 'Malaysia', 'Vietnam', 'Sri Lanka', 'Australia'],
    'sameAs': ['https://instagram.com/sssimportexport'],
    'knowsAbout': ['Indian spices export', 'Fresh onion export', 'Red chilli powder supply', 'Fresh fruit export', 'Herbs and powders'],
}


def jsonld_products():
    items = []
    for i, p in enumerate(PRODUCTS, 1):
        items.append({'@type': 'ListItem', 'position': i, 'item': {
            '@type': 'Product', 'name': p['name'], 'description': p['desc'],
            'image': f'[SITE_URL]/assets/img/products/{p["id"]}-1600.webp',
            'category': CATS[p['category']]['name'], 'countryOfOrigin': {'@type': 'Country', 'name': 'India'},
            'brand': {'@type': 'Brand', 'name': 'SSS Import Export'}, 'url': f'[SITE_URL]/products#{p["id"]}'}})
    return ld(ORG) + '\n' + ld({'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'SSS Import Export products', 'itemListElement': items})


# ---------------------------------------------------------------- write
def replace_block(html, name, content):
    pat = re.compile(rf'(<!-- BEGIN:{name} -->)(.*?)(<!-- END:{name} -->)', re.S)
    if not pat.search(html):
        return html
    return pat.sub(lambda m: m.group(1) + '\n' + content + '\n' + m.group(3), html)


PAGES = {'index.html': 'home', 'products.html': 'products', 'contact.html': 'contact'}
for fname, page in PAGES.items():
    path = ROOT / fname
    html = path.read_text()
    html = replace_block(html, 'header', header(page))
    html = replace_block(html, 'footer', footer(page))
    html = replace_block(html, 'categories', categories())
    html = replace_block(html, 'product-grid', product_grid())
    html = replace_block(html, 'jsonld-org', ld(ORG))
    html = replace_block(html, 'jsonld-products', jsonld_products())
    html = re.sub(r'(assets/(?:css|js)/[\w.-]+\.(?:css|js))\?v=[\w]+', rf'\1?v={VERSION}', html)
    if SITE_SET:
        html = html.replace('[SITE_URL]', SITE_URL)
    html = html.replace('data-product-count>33<', f'data-product-count>{len(PRODUCTS)}<').replace('data-count="33" data-product-count', f'data-count="{len(PRODUCTS)}" data-product-count')
    path.write_text(html)
    print('built', fname)

(ROOT / 'assets/js/products-data.js').write_text(
    '/* Generated by tools/build.py from assets/data/products.json — do not edit by hand. */\n'
    'window.SSS_DATA = ' + json.dumps(DATA, ensure_ascii=False) + ';\n')
print('wrote assets/js/products-data.js —', len(PRODUCTS), 'products')

base = SITE_URL if SITE_SET else '[SITE_URL]'
today = time.strftime('%Y-%m-%d')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{base}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in ['/', '/products', '/contact']) + '</urlset>\n')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n')
print('wrote sitemap.xml + robots.txt' + ('' if SITE_SET else ' (set SITE_URL in tools/build.py)'))
