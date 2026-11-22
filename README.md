# Raleigh Sites – Surrounding Cities

Static sites for locksmith clients in the Raleigh, NC area (Garner and nearby towns).

- Template: `seattle-template/` (same generator as Seattle-Locksmith-Sites / Charlotte-Locksmith-Sites)
- Data: `seattle-template/data/locations.json` (one entry per domain), `data/reviews/<domain>.json` (real Google reviews only), `data/image_map/<domain>.json`, optional `data/home_extra/<domain>.html`
- Images: `python3 seattle-template/scripts/make_images.py <domain> <dir with logo.png + GBP photos>` → `seattle-template/assets/<domain>/img/`
- Build: `python3 seattle-template/scripts/build.py <domain>` → `sites/<domain>/`
- Deploy: Cloudflare Pages, one project per domain, build output `sites/<domain>`

## Sites
- garner-locksmith.com – Garner Locksmith, Garner NC 27529 (in progress; not built into `sites/` yet – waiting for logo and photos)
