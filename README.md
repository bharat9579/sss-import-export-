# SSS Import Export — website

Premium marketing site for **SSS Import Export**, a 3rd-generation Indian import-export house (fresh vegetables, fruits, spices, herbs and powders).

Plain **HTML + CSS + JavaScript** — no framework, no build step on the server. Animations use **GSAP + ScrollTrigger** and **Lenis** smooth scrolling from a CDN; the site still works fully (with simple fades) if those don't load, and respects *reduce motion*.

## Pages

| File | Page |
|---|---|
| `index.html` | Home — hero, trust strip, legacy timeline, categories, why us, quality process, global reach map, packaging, testimonials, CTA |
| `products.html` | Product catalogue — search, category + origin filters, detail pop-up (shareable links like `products.html?category=spices` and `products.html#cumin`) |
| `contact.html` | Quote request form, WhatsApp, contact details, map placeholder |

## Run it locally

```bash
cd sss-import-export
python3 -m http.server 8090
# open http://localhost:8090
```

Any static server works.

## Edit content

| To change… | Edit | Then |
|---|---|---|
| Phone, WhatsApp, email, address, form endpoint | `assets/js/config.js` | Nothing — refresh |
| Products, categories, origins, grades | `assets/data/products.json` | `python3 tools/build.py` |
| Header, footer, site URL | `tools/build.py` | `python3 tools/build.py` |
| Any other text | The page's `.html` file (outside the `BEGIN/END` markers) | Nothing |
| Colours, type, spacing | Tokens at the top of `assets/css/styles.css` | Nothing |

**`tools/build.py`** (Python 3, no packages needed) regenerates the content between `<!-- BEGIN:x -->` / `<!-- END:x -->` markers: shared header & footer, home category cards, the product grid, schema.org JSON-LD, `assets/js/products-data.js`, `sitemap.xml` and `robots.txt`. It also bumps `?v=` on CSS/JS links so visitors never see stale cached styles. **Don't hand-edit inside the markers** — the build overwrites them.

### Adding a product

1. Add an entry to `assets/data/products.json` (copy an existing one; `category` must match a category `id`).
2. Add two images: `assets/img/products/<id>-800.webp` and `<id>-1600.webp` (4:3 works best).
3. Run `python3 tools/build.py`.

## Design system

- **Colours** — Oxford blue `#002147` / deep `#001530`, butter yellow `#F8E58C` / soft `#FFF6CC`, ivory `#FBFAF5`. Butter yellow is used on Oxford backgrounds (not on white) for AA contrast; text on butter buttons is Oxford.
- **Type** — one family, *Plus Jakarta Sans* 300–800; hierarchy via weight, size, tracking and case; fluid sizes with `clamp()`.
- **Liquid glass** — `.glass` (dark) and `.glass--light`: translucent fill, `backdrop-filter: blur(24px) saturate(180%)`, top highlight, inner glow, layered shadows, plus a cursor-tracked specular highlight. Hero stat cards add an SVG `feTurbulence` + `feDisplacementMap` refractive edge in Chromium browsers; others get the plain blur. Glass always sits over photography or slow-drifting Oxford/butter gradient blobs.
- **Motion** — `cubic-bezier(.22,1,.36,1)`; reveal = fade + 24px rise, staggered; split-word hero headline; parallax; counters; animated trade routes; magnetic CTAs; glass nav on scroll. Disabled under `prefers-reduced-motion`.

## Deploy (Vercel)

1. Push this folder to a GitHub repository.
2. At [vercel.com/new](https://vercel.com/new), import the repository. Framework preset **Other**; leave the build command and output directory **empty**.
3. Deploy. `vercel.json` enables clean URLs (`/products`, `/contact`) and long-term caching for assets. `tools/` and the docs are excluded via `.vercelignore`.

Any static host (Netlify, Cloudflare Pages, GitHub Pages, cPanel) works the same way — upload the folder.

## Before launch

See **[PLACEHOLDERS.md](PLACEHOLDERS.md)** — every value to fill in, and where.

## Credits

Photography: [Pexels](https://www.pexels.com) (free for commercial use). World map built from [Natural Earth](https://www.naturalearthdata.com) data (public domain) via `world-atlas`.

Home hero background: "CMA CGM Seine au port du Havre", Wikimedia Commons, CC0.

Home hero onion photos from [Wikimedia Commons](https://commons.wikimedia.org):
- `hero/onion-big`, "Baramati, Maharashtra, India. 14 onions", Frederick Noronha, CC BY-SA 4.0
- `hero/onion-pile`, "Onions on a trolley in India", Ravi Dwivedi, CC BY-SA 4.0
- `hero/onion-field`, "Onion farming", Gajanan Jagannath Jagdale, CC0
- `hero/onion-gulabi`, "Lasalgaon Manganga Gulabi Onions freshly plucked from a field", Bapu Shinde, CC0

Replace these with the company's own Nashik onion photos when available.

Legacy section satellite flyover: EOxCloudless 2016 (https://cloudless.eox.at) by EOX IT Services GmbH, contains modified Copernicus Sentinel data 2016, CC BY 4.0 (credited in the map caption). Regenerate the map overlay with `python3 tools/onion_map.py`.

## SEO

- Business details, homepage/page titles, FAQ and the 13 product/trading/service pages are defined in `assets/data/seo.json`.
- `python3 tools/build.py` writes the SEO `<head>` (meta, Open Graph, JSON-LD) into every page, generates `products/*.html`, `industrial/*.html`, `services/white-label.html`, and writes `sitemap.xml`, `robots.txt` and `vercel.json` (clean URLs such as `/products/onion`).
- Share images (1200×630) live in `assets/img/og/`.
- New page photos (coconut, rice, machines, chemicals, plastics) are CC0 / public domain from Wikimedia Commons; the white-label image is a mockup made from the site's own photos.

"Why choose us" hover clips in `assets/video/` are cut from public-domain USDA footage on Wikimedia Commons (Potatoes Sorting Montana2026; Fresno Family Farm producer interview; Harvest 20181008-FPAC-KLS-0012; 20201119-TFAA-LSC-0044 port clip) and the CC0 "Truck Driving on Southern Nevada Liteweight Road". Replace with the company's own footage when available.
