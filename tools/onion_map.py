"""Generate the onion-belt satellite flyover (SVG) for the legacy section of index.html.

Writes the SVG between <!-- BEGIN:onion-map --> and <!-- END:onion-map --> in index.html.
The base image is assets/img/nashik-onion-belt-satellite-map.webp: Sentinel-2 cloudless 2016 by EOX
(CC BY 4.0), zoom-11 Web Mercator tiles stitched starting at tile SAT_ORIGIN. Town positions
are real coordinates projected into the same space, so pins sit on the right spot.

    python3 tools/onion_map.py
"""
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 800, 1000
ZOOM = 11
SAT_ORIGIN = (1439, 900)            # top-left tile (x, y) of the stitched image
SAT_TILES = (12, 14)                # tiles across, down
SCALE = 0.71                        # SVG units per zoom-11 pixel
CENTER = (20.10, 74.02)             # lat, lon at the middle of the view

# onion-growing towns of the Nashik belt (lat, lon); first entry is the hub
PLACES = [
    ('nashik', 'Nashik', 19.9975, 73.7898, 'below'),
    ('dindori', 'Dindori', 20.2036, 73.8336, 'left'),
    ('vani', 'Vani', 20.3333, 73.8833, 'above'),
    ('pimpalgaon', 'Pimpalgaon', 20.1667, 73.9833, 'right'),
    ('chandwad', 'Chandwad', 20.3297, 74.2461, 'above'),
]


def world(lat, lon):
    n = 2 ** ZOOM * 256
    x = (lon + 180) / 360 * n
    lr = math.radians(lat)
    y = (1 - math.log(math.tan(lr) + 1 / math.cos(lr)) / math.pi) / 2 * n
    return x, y


CX, CY = world(*CENTER)


def xy(lat, lon):
    x, y = world(lat, lon)
    return W / 2 + (x - CX) * SCALE, H / 2 + (y - CY) * SCALE


def arc(a, b, bend):
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    cx, cy = mx - (y2 - y1) * bend, my + (x2 - x1) * bend
    return f'M{x1:.0f},{y1:.0f}Q{cx:.0f},{cy:.0f} {x2:.0f},{y2:.0f}'


def build():
    pos = {key: xy(lat, lon) for key, _, lat, lon, _ in PLACES}
    hub = pos['nashik']
    ix = W / 2 + (SAT_ORIGIN[0] * 256 - CX) * SCALE
    iy = H / 2 + (SAT_ORIGIN[1] * 256 - CY) * SCALE
    iw, ih = SAT_TILES[0] * 256 * SCALE, SAT_TILES[1] * 256 * SCALE
    # camera zooms in towards the middle of the belt
    fx = sum(p[0] for p in pos.values()) / len(pos) / W * 100
    fy = sum(p[1] for p in pos.values()) / len(pos) / H * 100

    out = [f'<svg class="onion-map__svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" role="img" '
           f'aria-labelledby="om-title om-desc" style="--fx:{fx:.1f}%;--fy:{fy:.1f}%">',
           '<title id="om-title">Our onion belt in Nashik district, Maharashtra</title>',
           '<desc id="om-desc">Satellite view of Nashik district zooming in on the onion-growing towns of Nashik, '
           'Dindori, Vani, Pimpalgaon Baswant and Chandwad.</desc>',
           '<defs><filter id="om-shadow" x="-50%" y="-50%" width="200%" height="200%">'
           '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity=".55"/></filter></defs>',
           f'<rect width="{W}" height="{H}" fill="#2a2a22"/>',
           '<g class="om-cam"><g class="om-drift">',
           f'<image class="om-sat" data-href="assets/img/nashik-onion-belt-satellite-map.webp" x="{ix:.1f}" y="{iy:.1f}" '
           f'width="{iw:.1f}" height="{ih:.1f}" preserveAspectRatio="none"/>']

    # routes from each town into the Nashik hub
    out.append('<g class="om-routes">')
    for i, (key, *_rest) in enumerate(PLACES[1:]):
        out.append(f'<path class="om-route" pathLength="1" style="--i:{i}" d="{arc(pos[key], hub, 0.12 if i % 2 else -0.12)}"/>')
    out.append('</g>')

    # pins with label tags
    for i, (key, name, lat, lon, side) in enumerate(PLACES):
        x, y = pos[key]
        hubcls = ' om-pin--hub' if i == 0 else ''
        fs = 21 if i == 0 else 18
        tw = len(name) * fs * 0.58 + 26
        th = fs + 16
        gap = 20
        tx, ty = {'above': (-tw / 2, -gap - th), 'below': (-tw / 2, gap),
                  'left': (-gap - tw, -th / 2), 'right': (gap, -th / 2)}[side]
        out.append(f'<g class="om-pin{hubcls}" data-pin="{key}" data-coord="{lat:.2f}° N, {lon:.2f}° E" '
                   f'style="--i:{i}" transform="translate({x:.0f} {y:.0f})">'
                   '<circle class="om-ripple" r="10"/>'
                   '<circle class="om-dot" r="8" filter="url(#om-shadow)"/><circle class="om-core" r="3.5"/>'
                   f'<g class="om-tag"><rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" rx="{th / 2:.0f}"/>'
                   f'<text x="{tx + tw / 2:.0f}" y="{ty + th / 2 + fs * 0.35:.0f}" text-anchor="middle" '
                   f'font-size="{fs}">{name}</text></g></g>')

    out.append('</g></g>')

    # map furniture stays fixed while the camera moves
    out.append('<g class="om-compass" transform="translate(736 84)"><circle r="24"/>'
               '<path d="M0,-15 L5.5,4 L0,0 L-5.5,4Z"/><text y="-30" text-anchor="middle">N</text></g>')
    km10 = 10 / 111.32 / math.cos(math.radians(CENTER[0])) * (2 ** ZOOM * 256 / 360) * SCALE
    out.append(f'<g class="om-scale" transform="translate({736 - km10 / 2:.0f} 150)"><path d="M0,0H{km10:.0f}M0,-6V6M{km10:.0f},-6V6"/>'
               f'<text x="{km10 / 2:.0f}" y="-12" text-anchor="middle">10 km</text></g>')
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    svg = build()
    page = ROOT / 'index.html'
    html = page.read_text()
    block = f'<!-- BEGIN:onion-map -->\n{svg}\n<!-- END:onion-map -->'
    html, n = re.subn(r'<!-- BEGIN:onion-map -->.*?<!-- END:onion-map -->', lambda m: block, html, flags=re.S)
    if not n:
        raise SystemExit('onion-map markers not found in index.html')
    page.write_text(html)
    print(f'wrote onion map ({len(svg) // 1024} KB)')
