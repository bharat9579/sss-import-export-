#!/usr/bin/env python3
"""
SSS Import Export — static build step.

Run after editing products.json, seo.json or the shared header/footer below:

    python3 tools/build.py

It rewrites the regions between <!-- BEGIN:name --> / <!-- END:name --> markers in
index.html, products.html and contact.html (including the SEO <head> block), generates
one page per entry in assets/data/seo.json "pages" (products/*.html, industrial/*.html,
services/*.html), regenerates assets/js/products-data.js, sitemap.xml, robots.txt and
vercel.json, and bumps the ?v= cache-busting version on CSS/JS links. Pages stay plain
HTML, so the site deploys as-is (no build needed on the server).

Business details (domain, phone, address, Search Console, Analytics) live in seo.json.
"""
import json, re, time
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'assets/data/products.json').read_text())
SEO = json.loads((ROOT / 'assets/data/seo.json').read_text())
BIZ = SEO['business']
CATS = {c['id']: c for c in DATA['categories']}
PRODUCTS = DATA['products']
BY_ID = {p['id']: p for p in PRODUCTS}
VERSION = time.strftime('%Y%m%d%H%M')
TODAY = time.strftime('%Y-%m-%d')

SITE_URL = BIZ['domain'].rstrip('/')
PAGES_SEO = SEO['pages']
PAGE_FOR_PRODUCT = {pg['product_id']: pg for pg in PAGES_SEO if pg.get('product_id')}


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')


# keyword-based image file names, e.g. assets/img/products/onion-exporter-india-800.webp
for p in PRODUCTS:
    p['img'] = slugify(p['name']) + '-exporter-india'

ICON = {
    'arrow': '<svg class="arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'pin': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21Z" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="9.5" r="2.5" stroke="currentColor" stroke-width="2"/></svg>',
    'wa': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.05 2C6.53 2 2.06 6.47 2.06 11.99c0 1.76.46 3.48 1.34 5L2 22l5.13-1.35a9.93 9.93 0 0 0 4.92 1.3h.01c5.51 0 9.99-4.47 9.99-9.99A9.98 9.98 0 0 0 12.05 2Zm5.83 14.15c-.25.69-1.44 1.32-2 1.4-.51.08-1.16.11-1.87-.12-.43-.14-.98-.32-1.69-.62-2.98-1.29-4.93-4.29-5.08-4.49-.15-.2-1.21-1.61-1.21-3.07 0-1.46.77-2.18 1.04-2.48.27-.3.6-.37.8-.37h.57c.18 0 .43-.07.67.51.25.6.84 2.06.92 2.21.07.15.12.32.02.52-.1.2-.15.32-.3.5-.15.17-.31.39-.45.52-.15.15-.3.31-.13.61.17.3.77 1.27 1.65 2.06 1.14 1.01 2.09 1.33 2.39 1.48.3.15.47.12.65-.07.17-.2.74-.87.94-1.16.2-.3.4-.25.67-.15.27.1 1.73.82 2.03.97.3.15.5.22.57.35.07.12.07.72-.18 1.41Z"/></svg>',
    'phone': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.9 21 3 13.1 3 3.9c0-.6.4-1 1-1h3.4c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1L6.6 10.8Z" fill="currentColor"/></svg>',
    'mail': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="m4 7 8 6 8-6" stroke="currentColor" stroke-width="1.7"/></svg>',
    'ig': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5" stroke="currentColor" stroke-width="1.7"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/></svg>',
    'check': '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}


def img_set(folder, name, alt, sizes, eager=False, extra='', base=''):
    src = f'{base}assets/img/{folder + "/" if folder else ""}{name}'
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{src}-800.webp" srcset="{src}-800.webp 800w, {src}-1600.webp 1600w" '
            f'sizes="{sizes}" alt="{escape(alt)}" {loading} decoding="async" width="1600" height="1200"{extra}>')


def contact_href(product, base=''):
    return f'{base}contact.html?product={quote(product)}'


def page_href(pg, base=''):
    return f'{base}{pg["slug"]}.html'


# ---------------------------------------------------------------- header
def header(page, base=''):
    on_home = page == 'home'
    home = '' if on_home else f'{base}index.html'
    links = [
        ('Home', '#home' if on_home else f'{base}index.html', on_home),
        ('About', f'{home}#about', False),
        ('Products', f'{base}products.html', page in ('products', 'detail')),
        ('Quality', f'{home}#quality', False),
        ('Global Reach', f'{home}#global', False),
        ('Contact', f'{base}contact.html', page == 'contact'),
    ]
    ac = ' aria-current="page"'
    nav = ''.join(f'<a href="{h}"{ac if cur and page != "detail" else ""}>{t}</a>' for t, h, cur in links)
    menu = ''.join(f'<a class="menu__link" href="{h}"{ac if cur and page != "detail" else ""}>{t}</a>' for t, h, cur in links)
    solid = '' if on_home else ' nav--solid'
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
    <a href="{'#home' if on_home else base + 'index.html'}" class="logo" aria-label="SSS Import Export home">
      <img class="logo__full" src="{base}assets/img/sss-import-export-logo-light.png" alt="" width="523" height="180">
    </a>
    <nav class="nav__links" aria-label="Main">{nav}</nav>
    <div class="nav__actions">
      <a href="{base}contact.html" class="btn btn--butter btn--sm nav__cta" data-magnetic>Request a Quote</a>
      <button class="nav__toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="menu-scrim" data-menu-close></div>
<nav class="menu" id="menu" aria-label="Mobile">
  {menu}
  <div class="menu__foot">
    <a href="{base}contact.html" class="btn btn--butter">Request a Quote {ICON['arrow']}</a>
    <a href="#" class="btn btn--wa" data-wa>{ICON['wa']} WhatsApp</a>
    <a href="#" class="btn btn--line-light" data-tel>{ICON['phone']} Call</a>
  </div>
</nav>'''


# ---------------------------------------------------------------- footer
def footer(page, base=''):
    home = '' if page == 'home' else f'{base}index.html'
    prods = ''.join(f'<li><a href="{page_href(pg, base)}">{escape(pg["nav"])}</a></li>'
                    for pg in PAGES_SEO if pg['slug'].startswith('products/'))
    trade = ''.join(f'<li><a href="{page_href(pg, base)}">{escape(pg["nav"])}</a></li>'
                    for pg in PAGES_SEO if not pg['slug'].startswith('products/'))
    return f'''<footer class="footer on-dark">
  <div class="wrap">
    <div class="footer__grid footer__grid--5">
      <div>
        <a href="{'#home' if page == 'home' else base + 'index.html'}" class="logo" aria-label="SSS Import Export home"><img class="logo__full logo__full--footer" src="{base}assets/img/sss-import-export-logo-light.png" alt="" width="523" height="180"></a>
        <p>A 3rd-generation Indian import-export house, established {BIZ['founded']}, supplying onion, fresh produce, grains, spices and powders to buyers in India and abroad.</p>
        <p class="footer__regs">APEDA · IEC</p>
      </div>
      <div>
        <h4>Company</h4>
        <ul class="footer__list">
          <li><a href="{home}#about">About</a></li>
          <li><a href="{home}#quality">Quality</a></li>
          <li><a href="{home}#global">Global Reach</a></li>
          <li><a href="{home}#packaging">Packaging &amp; Shipping</a></li>
          <li><a href="{base}products.html">All Products</a></li>
          <li><a href="{base}contact.html">Request a Quote</a></li>
        </ul>
      </div>
      <div>
        <h4>Products</h4>
        <ul class="footer__list">{prods}</ul>
      </div>
      <div>
        <h4>Trading &amp; Services</h4>
        <ul class="footer__list">{trade}</ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul class="footer__list footer__contact">
          <li>{ICON['pin']}<span data-cfg="address">[ADDRESS]</span></li>
          <li>{ICON['phone']}<a href="#" data-tel data-cfg="phoneDisplay">[PHONE_NUMBER]</a></li>
          <li>{ICON['phone']}<a href="#" data-tel="2" data-cfg="phone2Display">[PHONE_NUMBER]</a></li>
          <li>{ICON['wa']}<a href="#" data-wa>WhatsApp us</a></li>
          <li>{ICON['mail']}<a href="#" data-mail data-cfg="email">[EMAIL]</a></li>
          <li>{ICON['ig']}<a href="{BIZ['instagram']}" target="_blank" rel="noopener">@sssimportexport</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>&copy; <span data-year>{time.strftime('%Y')}</span> SSS Import Export. All rights reserved.</span>
      <span>IEC: <span class="ph">[IEC_NUMBER]</span></span>
    </div>
  </div>
</footer>
<a href="#" class="wa-fab" data-wa aria-label="Chat with SSS Import Export on WhatsApp">{ICON['wa']}<span class="wa-fab__tip">Chat on WhatsApp</span></a>'''


# ---------------------------------------------------------------- home: category cards
def categories():
    cards = []
    for c in DATA['categories']:
        items = [p['name'].split(' (')[0] for p in PRODUCTS if p['category'] == c['id']]
        seen = []
        for i in items:
            if i not in seen:
                seen.append(i)
        cards.append(f'''      <a class="cat" href="products.html?category={c['id']}" data-reveal>
        <div class="cat__img">{img_set('categories', c['image'], c['name'] + ' for export from India', '(max-width: 640px) 100vw, (max-width: 980px) 50vw, 40vw')}</div>
        <div class="cat__body">
          <h3>{escape(c['name'])}</h3>
          <span class="cat__link">Explore {len(seen)} products {ICON['arrow']}</span>
        </div>
      </a>''')
    return '    <div class="cats">\n' + '\n'.join(cards) + '\n    </div>'


# ---------------------------------------------------------------- home: FAQ (visible copy of the FAQPage schema)
def faq_section():
    items = ''.join(f'''
        <details class="faq__item" data-reveal>
          <summary>{escape(q)}<span class="faq__icon" aria-hidden="true"></span></summary>
          <p>{escape(a)}</p>
        </details>''' for q, a in SEO['faq'])
    return f'''<!-- ================= FAQ ================= -->
<section class="section section--white" id="faq" aria-labelledby="faq-title">
  <div class="wrap faq">
    <div class="section-head">
      <p class="eyebrow" data-reveal>FAQ</p>
      <h2 class="h2" id="faq-title" data-reveal>Questions buyers ask. <em>Straight answers.</em></h2>
    </div>
    <div class="faq__list">{items}
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------- products page grid
def product_grid():
    cards = []
    for p in PRODUCTS:
        cat = CATS[p['category']]
        search = ' '.join([p['name'], cat['name'], ' '.join(p['varieties'])]).lower()
        pg = PAGE_FOR_PRODUCT.get(p['id'])
        title = f'<a href="{page_href(pg)}">{escape(p["name"])}</a>' if pg else escape(p['name'])
        cards.append(f'''        <article class="pcard" id="{p['id']}" data-id="{p['id']}" data-cat="{p['category']}" data-search="{escape(search)}">
          <button type="button" class="pcard__img" data-open="{p['id']}" aria-haspopup="dialog" aria-label="View details: {escape(p['name'])}">{img_set('products', p['img'], p['name'] + ' for export from India', '(max-width: 380px) 100vw, (max-width: 980px) 50vw, 25vw')}</button>
          <div class="pcard__body">
            <span class="pcard__cat">{escape(cat['short'])}</span>
            <h3>{title}</h3>
            <div class="pcard__actions">
              <button type="button" class="pcard__link" data-open="{p['id']}" aria-haspopup="dialog">Details</button>
              <a href="{contact_href(p['name'])}" class="pcard__link pcard__link--strong">Enquire {ICON['arrow']}</a>
            </div>
          </div>
        </article>''')
    return '      <div class="grid-products" id="grid">\n' + '\n'.join(cards) + '\n      </div>'


def page_cards(pages, base='', heading_tag='h3'):
    out = []
    for pg in pages:
        folder, name = pg['image'].split('/', 1)
        out.append(f'''      <a class="pp-card" href="{page_href(pg, base)}">
        <span class="pp-card__img">{img_set(folder, name, pg['alt'], '(max-width: 640px) 50vw, 25vw', base=base)}</span>
        <span class="pp-card__body"><span class="pcard__cat">{escape(pg['group'])}</span><{heading_tag}>{escape(pg['name'])}</{heading_tag}><span class="pp-card__more">View {ICON['arrow']}</span></span>
      </a>''')
    return '\n'.join(out)


def more_pages():
    pages = [pg for pg in PAGES_SEO if not pg.get('product_id')]
    return f'''  <section class="section section--white" aria-labelledby="more-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow" data-reveal>More from SSS</p>
        <h2 class="h2" id="more-title" data-reveal>Grains, spices, industrial trading <em>and your own label.</em></h2>
      </div>
      <div class="pp-cards">
{page_cards(pages)}
      </div>
    </div>
  </section>'''


# ---------------------------------------------------------------- SEO head + structured data
def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'


def abs_url(path):
    return SITE_URL + path


def address():
    a = {'@type': 'PostalAddress', 'streetAddress': BIZ['street'], 'addressLocality': BIZ['city'],
         'addressRegion': BIZ['state'], 'addressCountry': 'IN'}
    if BIZ.get('postal_code'):
        a['postalCode'] = BIZ['postal_code']
    return a


def org():
    o = {'@type': 'Organization', '@id': abs_url('/#organization'), 'name': BIZ['name'], 'url': abs_url('/'),
         'logo': abs_url('/assets/img/logo-full.png'),
         'description': f'Third-generation import-export company, established {BIZ["founded"]}, trading FMCG products (onion, fresh vegetables, fruits, grains, spices and dehydrated powders) plus refurbished machines, chemicals, plastics and more, from anywhere to anywhere.',
         'foundingDate': BIZ['founded'], 'slogan': BIZ['slogan'], 'telephone': BIZ['phone'], 'address': address(),
         'contactPoint': [{'@type': 'ContactPoint', 'telephone': t, 'contactType': 'sales', 'areaServed': 'Worldwide', 'availableLanguage': ['English', 'Hindi', 'Marathi']} for t in (BIZ['phone'], BIZ.get('phone2')) if t],
         'sameAs': [u for u in (BIZ['instagram'], BIZ.get('linkedin')) if u],
         'areaServed': BIZ['area_served'],
         'knowsAbout': ['Onion export', 'Fresh vegetables export', 'Spices export', 'Grain export', 'Dehydrated powders',
                        'White label food products', 'Refurbished machinery import', 'Chemicals trading', 'Plastics trading']}
    if BIZ.get('email'):
        o['email'] = BIZ['email']
    return o


def catalog():
    groups = [('Fresh Vegetables & Fruits', ('Fresh Vegetables', 'Fresh Fruits')),
              ('Grains, Spices & Dehydrated Powders', ('Grains', 'Spices', 'Dehydrated Powders')),
              ('Industrial Trading', ('Industrial Trading',))]
    out = []
    for title, keys in groups:
        out.append({'@type': 'OfferCatalog', 'name': title, 'itemListElement': [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Product', 'name': pg['name'], 'url': abs_url('/' + pg['slug'])}}
            for pg in PAGES_SEO if pg['group'] in keys]})
    out.append({'@type': 'OfferCatalog', 'name': 'Services', 'itemListElement': [
        {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n}}
        for n in ('Export from India', 'Import to India', 'Domestic Bulk Supply', 'White Labelling / Private Label')]})
    return {'@type': 'OfferCatalog', 'name': 'Products & Services', 'itemListElement': out}


def home_graph():
    store = {'@type': 'WholesaleStore', '@id': abs_url('/#business'), 'name': BIZ['name'],
             'image': abs_url('/assets/img/' + SEO['home']['og_image']), 'url': abs_url('/'), 'telephone': BIZ['phone'],
             'priceRange': '₹₹', 'parentOrganization': {'@id': abs_url('/#organization')}, 'address': address(),
             'geo': {'@type': 'GeoCoordinates', 'latitude': BIZ['lat'], 'longitude': BIZ['lng']},
             'hasMap': f'https://www.google.com/maps/search/?api=1&query={BIZ["lat"]},{BIZ["lng"]}',
             'hasOfferCatalog': catalog()}
    if BIZ.get('email'):
        store['email'] = BIZ['email']
    site = {'@type': 'WebSite', '@id': abs_url('/#website'), 'url': abs_url('/'), 'name': BIZ['name'],
            'publisher': {'@id': abs_url('/#organization')}, 'inLanguage': 'en'}
    faq = {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in SEO['faq']]}
    return {'@context': 'https://schema.org', '@graph': [org(), store, site, faq]}


def google_tags():
    out = []
    if BIZ.get('google_site_verification'):
        out.append(f'<meta name="google-site-verification" content="{escape(BIZ["google_site_verification"])}">')
    if BIZ.get('ga4_id'):
        gid = escape(BIZ['ga4_id'])
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>\n'
                   f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{gid}');</script>")
    return out


def seo_head(title, description, path, og_title, og_description, og_image, lds, keywords=None, geo=False):
    url = abs_url(path)
    img = abs_url('/assets/img/' + og_image)
    lines = [f'<title>{escape(title)}</title>',
             f'<meta name="description" content="{escape(description)}">']
    if keywords:
        lines.append(f'<meta name="keywords" content="{escape(keywords)}">')
    lines += ['<meta name="robots" content="index, follow, max-image-preview:large">',
              f'<meta name="author" content="{BIZ["name"]}">',
              f'<link rel="canonical" href="{url}">',
              f'<link rel="alternate" hreflang="en" href="{url}">',
              f'<link rel="alternate" hreflang="x-default" href="{url}">']
    if geo:
        lines += [f'<meta name="geo.region" content="{BIZ["state_code"]}">',
                  f'<meta name="geo.placename" content="{BIZ["city"]}, {BIZ["district"]}">',
                  f'<meta name="geo.position" content="{BIZ["lat"]};{BIZ["lng"]}">',
                  f'<meta name="ICBM" content="{BIZ["lat"]}, {BIZ["lng"]}">']
    lines += ['<meta name="theme-color" content="#002147">',
              '<meta property="og:type" content="website">',
              f'<meta property="og:site_name" content="{BIZ["name"]}">',
              f'<meta property="og:title" content="{escape(og_title)}">',
              f'<meta property="og:description" content="{escape(og_description)}">',
              f'<meta property="og:url" content="{url}">',
              f'<meta property="og:image" content="{img}">',
              '<meta property="og:image:width" content="1200">',
              '<meta property="og:image:height" content="630">',
              '<meta property="og:locale" content="en_IN">',
              '<meta name="twitter:card" content="summary_large_image">',
              f'<meta name="twitter:title" content="{escape(og_title)}">',
              f'<meta name="twitter:description" content="{escape(og_description)}">',
              f'<meta name="twitter:image" content="{img}">']
    lines += google_tags()
    lines += [ld(o) for o in lds]
    return '\n'.join(lines)


def head_home():
    h = SEO['home']
    return seo_head(h['title'], h['description'], '/', h['og_title'], h['og_description'], h['og_image'],
                    [home_graph()], keywords=h['keywords'], geo=True)


def head_simple(key, path):
    m = SEO['pages_meta'][key]
    return seo_head(m['title'], m['description'], path, m['title'], m['description'], m['og_image'],
                    [{'@context': 'https://schema.org', **{k: v for k, v in org().items() if k != '@id'}}])


def jsonld_products():
    items = []
    for i, p in enumerate(PRODUCTS, 1):
        pg = PAGE_FOR_PRODUCT.get(p['id'])
        items.append({'@type': 'ListItem', 'position': i, 'item': {
            '@type': 'Product', 'name': p['name'], 'description': p['desc'],
            'image': abs_url(f'/assets/img/products/{p["img"]}-1600.webp'),
            'category': CATS[p['category']]['name'], 'countryOfOrigin': {'@type': 'Country', 'name': 'India'},
            'brand': {'@type': 'Brand', 'name': BIZ['name']},
            'url': abs_url('/' + pg['slug']) if pg else abs_url(f'/products#{p["id"]}')}})
    return ld({'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'SSS Import Export products', 'itemListElement': items})


# ---------------------------------------------------------------- generated product / trading / service pages
def og_name(pg):
    return 'og/' + pg['image'].split('/', 1)[1] + '.jpg'


def page_ld(pg):
    url = abs_url('/' + pg['slug'])
    img = abs_url(f'/assets/img/{pg["image"]}-1600.webp')
    if pg.get('service'):
        main = {'@context': 'https://schema.org', '@type': 'Service', 'name': pg['name'], 'serviceType': pg['name'],
                'description': pg['description'], 'image': img, 'url': url,
                'provider': {'@type': 'Organization', 'name': BIZ['name'], 'url': abs_url('/')},
                'areaServed': BIZ['area_served']}
    else:
        main = {'@context': 'https://schema.org', '@type': 'Product', 'name': pg['name'], 'image': img,
                'description': pg['description'], 'brand': {'@type': 'Brand', 'name': BIZ['name']},
                'countryOfOrigin': 'IN', 'category': pg['group'],
                'offers': {'@type': 'Offer', 'url': url, 'priceCurrency': 'INR',
                           'availability': 'https://schema.org/InStock',
                           'seller': {'@type': 'Organization', 'name': BIZ['name']}}}
    trail = [('Home', abs_url('/'))]
    if pg['slug'].startswith('products/'):
        trail.append(('Products', abs_url('/products')))
    trail.append((pg['name'], url))
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': n, 'item': u} for i, (n, u) in enumerate(trail, 1)]}
    out = [main, crumbs]
    if pg.get('list'):
        out.append({'@context': 'https://schema.org', '@type': 'ItemList', 'name': pg['name'], 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': BY_ID[pid]['name'], 'url': abs_url(f'/products#{pid}')}
            for i, pid in enumerate(pg['list'], 1)]})
    return out


def detail_page(pg):
    base = '../'
    section = pg['slug'].split('/')[0]
    folder, name = pg['image'].split('/', 1)
    crumb = '<a href="../products.html">Products</a><span aria-hidden="true">/</span>' if section == 'products' else ''
    body = ''.join(f'\n          <p>{escape(t)}</p>' for t in pg.get('body', []))
    spec = ''.join(f'\n            <div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in pg['spec'])
    if section == 'products':
        spec += '\n            <div><dt>MOQ</dt><dd><span class="ph">[MOQ]</span>, confirmed per order</dd></div>'
    enquire_name = pg['name']
    wa_text = f'Hi SSS Import Export, I would like a quote for {pg["name"]}.'

    steps = ''
    if pg.get('steps'):
        steps = '''
  <section class="section section--white" aria-labelledby="how-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow" data-reveal>How it works</p>
        <h2 class="h2" id="how-title" data-reveal>Four steps to <em>your own label.</em></h2>
      </div>
      <ol class="pp-steps">''' + ''.join(f'''
        <li data-reveal><span class="pp-steps__n">{i:02d}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></li>''' for i, (t, d) in enumerate(pg['steps'], 1)) + '''
      </ol>
    </div>
  </section>'''

    listing = ''
    if pg.get('list'):
        cards = ''.join(f'''
        <a class="pp-mini" href="../products.html#{pid}">
          <span class="pp-mini__img">{img_set('products', BY_ID[pid]['img'], BY_ID[pid]['name'] + ' for export from India', '(max-width: 640px) 50vw, 20vw', base=base)}</span>
          <span class="pp-mini__name">{escape(BY_ID[pid]['name'])}</span>
        </a>''' for pid in pg['list'])
        listing = f'''
  <section class="section section--white" aria-labelledby="range-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow" data-reveal>The range</p>
        <h2 class="h2" id="range-title" data-reveal>{escape(pg['name'])}, <em>product by product.</em></h2>
      </div>
      <div class="pp-minis">{cards}
      </div>
    </div>
  </section>'''

    related = [x for x in PAGES_SEO if x is not pg and (x['slug'].split('/')[0] == section or section != 'products')][:4]
    if len(related) < 4:
        related += [x for x in PAGES_SEO if x is not pg and x not in related][:4 - len(related)]

    head = seo_head(pg['title'], pg['description'], '/' + pg['slug'], pg['og_title'], pg['og_description'],
                    og_name(pg), page_ld(pg))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
<link rel="icon" href="{base}assets/img/favicon-64.png" type="image/png" sizes="64x64">
<link rel="icon" href="{base}assets/img/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/styles.css?v={VERSION}">
</head>
<body data-page="detail">
{header('detail', base)}

<main id="main">
  <header class="page-head on-dark">
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span aria-hidden="true">/</span>{crumb}<span aria-current="page">{escape(pg['name'])}</span></nav>
      <p class="eyebrow" data-reveal>{escape(pg['group'])}</p>
      <h1 data-reveal>{escape(pg['h1'])}. <em>{escape(pg['h1_em'])}</em></h1>
      <p class="lead" data-reveal>{escape(pg['lead'])}</p>
    </div>
  </header>

  <section class="section pp" aria-labelledby="spec-title">
    <div class="wrap pp__grid">
      <figure class="pp__media" data-reveal>{img_set(folder, name, pg['alt'], '(max-width: 980px) 100vw, 50vw', eager=True, base=base)}</figure>
      <div class="pp__info">
        <h2 class="pp__title" id="spec-title">{escape(pg['name'])}</h2>
        <div class="pp__body">{body}
        </div>
        <dl class="spec">{spec}
        </dl>
        <div class="pp__actions">
          <a href="{contact_href(enquire_name, base)}" class="btn btn--oxford">Enquire about {escape(pg['nav'])}</a>
          <a href="#" class="btn btn--wa" data-wa data-wa-text="{escape(wa_text)}">{ICON['wa']} WhatsApp</a>
        </div>
      </div>
    </div>
  </section>
{steps}{listing}
  <section class="section section--dark pp-why" aria-labelledby="why-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow" data-reveal>Why SSS Import Export</p>
        <h2 class="h2" id="why-title" data-reveal>Trust. Quality. <em>Price.</em></h2>
      </div>
      <ul class="pp-why__list">
        <li data-reveal>{ICON['check']}<h3>Trust</h3><p>A third-generation family business, established {BIZ['founded']}, licensed for import and export.</p></li>
        <li data-reveal>{ICON['check']}<h3>Quality</h3><p>Every lot is graded and checked before it is packed, to the spec you agreed.</p></li>
        <li data-reveal>{ICON['check']}<h3>Price</h3><p>Premium to budget grades, so you can match quality to your market.</p></li>
      </ul>
    </div>
  </section>

  <section class="section" aria-labelledby="related-title">
    <div class="wrap">
      <div class="section-head section-head--split">
        <div>
          <p class="eyebrow" data-reveal>Explore more</p>
          <h2 class="h2" id="related-title" data-reveal>More from <em>SSS Import Export.</em></h2>
        </div>
        <a href="../products.html" class="btn btn--line" data-reveal>All products {ICON['arrow']}</a>
      </div>
      <div class="pp-cards">
{page_cards(related, base)}
      </div>
    </div>
  </section>

  <section class="cta" aria-label="Request a quote">
    <div class="wrap">
      <div class="cta__box on-dark" data-reveal>
        <div>
          <p class="eyebrow">Get today&rsquo;s price</p>
          <h2 class="h2">Tell us what you need. <em>We reply within 24 hours.</em></h2>
          <p class="lead">Share the product, grade, quantity and destination, and we&rsquo;ll come back with availability and price.</p>
        </div>
        <div class="cta__actions">
          <a href="{contact_href(enquire_name, base)}" class="btn btn--butter" data-magnetic>Request a Quote</a>
          <a href="#" class="btn btn--text btn--text-light" data-wa data-wa-text="{escape(wa_text)}">Or chat on WhatsApp</a>
        </div>
      </div>
    </div>
  </section>
</main>

{footer('detail', base)}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js" defer></script>
<script src="{base}assets/js/config.js?v={VERSION}" defer></script>
<script src="{base}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- write
def replace_block(html, name, content):
    pat = re.compile(rf'(<!-- BEGIN:{name} -->)(.*?)(<!-- END:{name} -->)', re.S)
    if not pat.search(html):
        return html
    return pat.sub(lambda m: m.group(1) + '\n' + content + '\n' + m.group(3), html)


HEADS = {'index.html': head_home, 'products.html': lambda: head_simple('products', '/products'),
         'contact.html': lambda: head_simple('contact', '/contact')}
PAGES = {'index.html': 'home', 'products.html': 'products', 'contact.html': 'contact'}
for fname, page in PAGES.items():
    path = ROOT / fname
    html = path.read_text()
    html = replace_block(html, 'seo-head', HEADS[fname]())
    html = replace_block(html, 'header', header(page))
    html = replace_block(html, 'footer', footer(page))
    html = replace_block(html, 'categories', categories())
    html = replace_block(html, 'faq', faq_section())
    html = replace_block(html, 'product-grid', product_grid())
    html = replace_block(html, 'more-pages', more_pages())
    html = replace_block(html, 'jsonld-products', jsonld_products())
    html = re.sub(r'(assets/(?:css|js)/[\w.-]+\.(?:css|js))\?v=[\w]+', rf'\1?v={VERSION}', html)
    html = html.replace('[SITE_URL]', SITE_URL)
    html = html.replace('data-product-count>33<', f'data-product-count>{len(PRODUCTS)}<').replace('data-count="33" data-product-count', f'data-count="{len(PRODUCTS)}" data-product-count')
    path.write_text(html)
    print('built', fname)

for pg in PAGES_SEO:
    out = ROOT / (pg['slug'] + '.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(detail_page(pg))
    print('built', out.relative_to(ROOT))

(ROOT / 'assets/js/products-data.js').write_text(
    '/* Generated by tools/build.py from assets/data/products.json — do not edit by hand. */\n'
    'window.SSS_DATA = ' + json.dumps(DATA, ensure_ascii=False) + ';\n')
print('wrote assets/js/products-data.js —', len(PRODUCTS), 'products')

# sitemap lists only pages that exist; clean URLs are served by vercel.json
urls = [('/', 'daily', '1.0'), ('/products', 'weekly', '0.9'), ('/contact', 'monthly', '0.8')]
for pg in PAGES_SEO:
    sec = pg['slug'].split('/')[0]
    urls.append(('/' + pg['slug'], 'daily' if pg['slug'] == 'products/onion' else ('weekly' if sec == 'products' else 'monthly'),
                 '0.9' if pg['slug'] == 'products/onion' else ('0.8' if sec in ('products', 'services') else '0.7')))
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n'
            for u, c, p in urls) + '</urlset>\n')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
(ROOT / 'vercel.json').write_text(json.dumps({'cleanUrls': True, 'trailingSlash': False}, indent=2) + '\n')
print(f'wrote sitemap.xml ({len(urls)} URLs) + robots.txt + vercel.json')
