"""Per-site "no prices" switch.

The template quotes starting prices on product cards, service pages, the FAQ and in Service schema.
A location can turn all of that off in data/locations.json with
    "no_prices": true
and every own price in its built pages is removed or rewritten (copy, FAQ HTML + JSON-LD, schema offers).
Also drop the "how-much-does-a-locksmith-cost" post from the location's "blog" list.
Prices that describe other companies' bait ads in the blog ("$19 service call") are left alone.
"""
import re
from pathlib import Path

RULES = [
    # product cards and service page badges
    (r"<p>From \$\d+ · ([^<]*)</p>", r"<p>\1</p>"),
    (r" · from \$\d+", ""),
    (r"From (?:<b>)?\$\d+(?:</b>)? · Free estimate", "Free estimate"),
    # Service schema offers
    (r',"offers":\{"@type":"Offer","price":"\d+","priceCurrency":"USD","priceSpecification":\{[^}]*\}\}', ""),
    # headings
    (r"Popular services and starting prices", "Popular locksmith services"),
    # FAQ answers (HTML and JSON-LD share the wording)
    (r"It depends on the job\. At ([^.]*?) a house or car lockout starts at \$\d+, lock rekeying at \$\d+ per lock, key duplication at \$\d+ and car key replacement at \$\d+\. The technician",
     r"It depends on the job: the lock or key type, the vehicle and the hardware involved. At \1 the technician"),
    (r"Car lockouts in ([^.]*?) start at \$\d+\. That covers opening", r"A car lockout call in \1 covers opening"),
    (r"House, apartment and bedroom-door lockouts start at \$\d+\. We pick", "For house, apartment and bedroom-door lockouts we pick"),
    (r" Car key replacement starts at \$\d+\.", ""),
    (r"Key fob programming starts at \$\d+, and we can supply", "We can supply"),
    (r"Rekeying starts at \$\d+ per lock plus the service call\. A typical", "Rekeying is priced per lock plus the service call, and you get the total before we start. A typical"),
    (r"Safe opening starts at \$\d+, and we can reset", "After opening we can reset"),
    (r"cut and program the key on site, and car key replacement starts at \$\d+\.", "and cut and program the key on site."),
]


def apply(site_dir: Path, on):
    if not on:
        return
    rs = [(re.compile(p), r) for p, r in RULES]
    for f in site_dir.rglob("*.html"):
        s = f.read_text()
        t = s
        for p, r in rs:
            t = p.sub(r, t)
        if t != s:
            f.write_text(t)
