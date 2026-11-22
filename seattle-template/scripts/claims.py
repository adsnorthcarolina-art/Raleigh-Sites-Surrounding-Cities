"""Per-site business claims.

The template says every business is licensed and insured, offers a military discount and takes
payment apps (Apple Pay, Google Pay, Zelle, Venmo, Cash App). A location can switch any of these off
in data/locations.json, e.g.
    "claims": {"licensed": false, "military": false, "payment_apps": false}
and every such claim in its built pages (copy, FAQ, schema) is rewritten or removed, so the site
only states what the owner has confirmed. Sites without "claims" are untouched.
"""
import re
from pathlib import Path


def rules(claims, since):
    rs = []
    if claims.get("licensed") is False:
        rs += [
            # FAQ: the North Carolina licensing question is dropped entirely (HTML + JSON-LD)
            (r'<details><summary>Do locksmiths need to be licensed in [^<]+\?</summary><p>.*?</p></details>\s*', ""),
            (r'\{"@type":"Question","name":"Do locksmiths need to be licensed in [^"]+\?","acceptedAnswer":\{"@type":"Answer","text":"[^"]*"\}\},?', ""),
            # FAQ questions
            (r"Are you licensed and insured\?", "Are your technicians background-checked?"),
            (r"Are you a licensed locksmith serving", "Are you a local locksmith serving"),
            # answers / sentences
            (r" is licensed and insured, in business since (\d{4}), and", r" has been in business since \1, and"),
            (r" is licensed and insured, and every technician", f" has been in business since {since}, and every technician"),
            (r"licensed and insured since (\d{4})", r"in business since \1"),
            (r"licensed &amp; insured mobile locksmiths", "mobile locksmiths"),
            (r"licensed & insured mobile locksmiths", "mobile locksmiths"),
            (r"<strong>Licensed, insured, background-checked\.</strong>", "<strong>Background-checked technicians.</strong>"),
            (r"<b>Licensed &amp; insured</b><span>Background-checked", "<b>Background-checked</b><span>Background-checked"),
            (r"<b>Background-checked</b><span>Background-checked technicians, ID shown on arrival\.", "<b>Background-checked</b><span>Every technician shows ID on arrival."),
            (r"<b>Licensed &amp; insured</b><span>Serving", "<b>Local business</b><span>Serving"),
            (r"Licensed &amp; insured · ([Ss])ince", r"Local business · \1ince"),
            (r"Licensed &amp; insured · Serving", "Local business · Serving"),
            (r"Open 24 hours · Licensed &amp; insured", "Open 24 hours · Mobile service"),
            (r" · Licensed &amp; insured", " · Firm price before work starts"),
            (r", licensed and insured", ""),
            (r", arrival times, licensing", ", arrival times"),
            (r"call a licensed local locksmith", "call a trusted local locksmith"),
            # Q&A page: the licensing question above was dropped, so 15 questions become 14
            (r"15 Common Questions", "14 Common Questions"),
            (r"([Tt]he) 15 questions", r"\1 14 questions"),
        ]
    if claims.get("military") is False:
        rs += [
            (r"\s*<div><b>Military discount</b><span>[^<]*</span></div>", ""),
            (r"\s*<li><b>Military discount</b><span>[^<]*</span></li>", ""),
            (r"\s*<li>Military discount</li>", ""),
            (r"Military discount for active duty and veterans on any service — mention it when you book\. ", ""),
            (r" A military discount is available for active-duty service members and veterans when mentioned at booking\.", ""),
            (r"Military discount · ", ""),
            (r" · Military discount", ""),
            (r", military discount", ""),
        ]
    if claims.get("payment_apps") is False:
        rs += [
            (r", Apple Pay, Google Pay, Zelle, Venmo, Cash App", ""),
            (r"<li>Apple Pay</li><li>Google Pay</li><li>Zelle</li><li>Venmo</li><li>Cash App</li>", ""),
            (r"cash, major credit and debit cards, Apple Pay, Google Pay, Zelle, Venmo and Cash App", "cash and major credit and debit cards"),
            (r"cash, all major cards, Apple Pay, Google Pay, Zelle, Venmo and Cash App", "cash and all major cards"),
            (r"cash, card, Apple Pay, Google Pay, Zelle or Venmo", "cash or card"),
        ]
    return rs


def apply(site_dir: Path, claims, since=""):
    if not claims:
        return
    rs = [(re.compile(p, re.S), r) for p, r in rules(claims, since)]
    for f in site_dir.rglob("*"):
        if f.suffix not in (".html", ".xml", ".txt", ".json") or not f.is_file():
            continue
        s = f.read_text()
        t = s
        for p, r in rs:
            t = p.sub(r, t)
        t = t.replace("}},]", "}}]")  # a dropped last FAQ item in JSON-LD
        if t != s:
            f.write_text(t)
