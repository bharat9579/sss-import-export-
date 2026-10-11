# Placeholders to fill in before launch

Everything below is marked on the live pages with a **dashed yellow highlight** (`<span class="ph">`) so it's easy to spot. Nothing here was invented — these are the facts only you can supply.

## 1. Contact details — `assets/js/config.js` (edit once, used on every page)

| Setting | What to enter | Example format |
|---|---|---|
| `whatsappNumber` | WhatsApp number, digits only with country code | set: `917350319193` (+91 73503 19193) |
| `phoneDisplay` | Phone number as it should appear | `+91 98765 43210` |
| `phoneDial` | Phone number for tap-to-call | `+919876543210` |
| `email` | Export desk email | `export@yourdomain.com` |
| `address` | Office address (one line) | `Unit 4, …, City PIN, India` |
| `formEndpoint` | *Optional.* Form service URL (Formspree, Web3Forms, Getform…) | `https://formspree.io/f/xxxxxx` |

Until `whatsappNumber` / `email` / `formEndpoint` are set, the WhatsApp and call buttons link to the Contact page, and the quote form explains that submissions aren't connected yet.
How the quote form sends: **formEndpoint** if set → otherwise **WhatsApp** with the enquiry pre-filled → otherwise **email**.

## 2. Website address — `tools/build.py`

| Setting | What to enter |
|---|---|
| `SITE_URL` | Your final domain, e.g. `https://www.sssimportexport.com` (no trailing slash) |

Then run `python3 tools/build.py`. It fills canonical / Open Graph / schema.org URLs (82 places) and writes `sitemap.xml` and `robots.txt`.

## 3. Registrations — footer (`tools/build.py` → `footer()`), then rebuild

| Placeholder | What to enter |
|---|---|
| `[IEC_NUMBER]` | Import Export Code |
| `[FSSAI_LICENSE_NUMBER]` | FSSAI licence number |
| **Badges shown** | FSSAI, APEDA, IEC, Spices Board — **confirm each is actually held**; delete any that aren't (trust strip in `index.html`, footer badges in `tools/build.py`). |
| `[CONFIRM]` ISO / HACCP | Commented out in `index.html` (trust strip). Uncomment **only** if certified. |

## 4. Family story — `index.html` (About / Legacy timeline)

| Placeholder | What to enter |
|---|---|
| `[YEAR]` ×2 | Year the first and second generations started |
| `[GRANDFATHER'S NAME]` | First generation |
| `[FATHER'S NAME]` | Second generation |

## 5. Testimonials

Section removed from the home page at the owner's request (2026-10-11).

## 6. Commercial terms

| Placeholder | Where | What to enter |
|---|---|---|
| `[MOQ]` | Product detail pop-up (`products.html`) | Minimum order quantity — one value, or edit the text to "varies by product" |
| `[OTHER TERMS, e.g. EXW / CFR]` | Packaging & shipping (`index.html`) | Any incoterms beyond FOB / CIF, or delete the line |

## 7. Map — `contact.html`

Replace the striped **"Map embed placeholder"** block with your Google Maps `<iframe>` (add `loading="lazy"` and a `title`).

## 8. Please review (not placeholders, but check them)

- **Product data** — `assets/data/products.json`: varieties, grades and packaging are typical industry options; adjust to exactly what you supply. Origin stories use well-known growing regions (Nashik, Guntur, Unjha, Erode, Ratnagiri…) — confirm they match where you actually buy.
- **Stats** — 7+ years, 3rd generation, 6+ countries come from your brief; the product count updates automatically from the data file.
- **Photos** — all are royalty-free stock (Pexels, free for commercial use, no attribution required). A few are stand-ins: *Ashwagandha* (generic dried roots), *Onion powder* (sliced onion), *Garlic powder* (garlic cloves), *Coriander powder* (coriander & turmeric on spoons). Your own product photos will look better and build more trust.

## SEO settings — `assets/data/seo.json` (then run `python3 tools/build.py`)

| Field | Status |
|---|---|
| `email` | **Empty** — add your business email (also set `email` in `assets/js/config.js`) |
| `linkedin` | **Empty** — add your LinkedIn company page URL |
| `postal_code` | **Empty** — add the pincode for APMC Market, Dindori |
| `google_site_verification` | **Empty** — code from Google Search Console (HTML tag method) |
| `ga4_id` | **Empty** — Google Analytics 4 Measurement ID, e.g. `G-XXXXXXXXXX` |
| Opening hours | Not published; add `openingHoursSpecification` in `tools/build.py` once confirmed |

Search Console and Analytics tags are only added to the pages once these fields are filled in.
