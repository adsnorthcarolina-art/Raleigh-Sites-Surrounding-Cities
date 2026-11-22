"""Social profile images for one site: avatar + covers sized for each platform.

usage: python3 scripts/make_social.py <domain> <hero.jpg> "<line2>" "<phone>"
  reads assets/<domain>/img/logo.png and the site palette from data/locations.json
  writes assets/<domain>/img/social/{avatar.jpg, fb-cover.jpg, x-header.jpg, yt-banner.jpg}
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from build import PALETTES  # noqa: E402

domain, hero_path, line2, phone = sys.argv[1:5]
loc = next(l for l in json.loads((ROOT / "data" / "locations.json").read_text()) if l["domain"] == domain)
ink, signal, _, _ = PALETTES[loc.get("palette", 0) % len(PALETTES)]
out = ROOT / "assets" / domain / "img" / "social"
out.mkdir(parents=True, exist_ok=True)
logo = Image.open(ROOT / "assets" / domain / "img" / "logo.png").convert("RGBA")
hero = Image.open(hero_path).convert("RGB")
F = ROOT / "template" / "fonts"


def font(name, size):
    return ImageFont.truetype(str(F / name), size)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cover(w, h, safe=None):
    """Photo on the right, ink panel with text on the left. safe = (x0, y0, x1, y1) area that must hold the text."""
    s = max(w / hero.width, h / hero.height)
    im = hero.resize((round(hero.width * s), round(hero.height * s)), Image.LANCZOS)
    # anchor the photo to the right so its subject sits beside the text, not under it
    cx = im.width - w
    im = im.crop((cx, (im.height - h) // 2, cx + w, (im.height - h) // 2 + h)).convert("RGBA")
    x0, y0, x1, y1 = safe or (0, 0, w, h)
    sw, sh = x1 - x0, y1 - y0
    # left-to-right ink gradient over the photo
    grad = Image.new("RGBA", (w, h))
    gd = ImageDraw.Draw(grad)
    c = rgb(ink)
    solid = x0 + int(sw * 0.50)
    fade = x0 + int(sw * 0.80)
    for x in range(w):
        a = 238 if x < solid else max(0, int(238 * (1 - (x - solid) / max(1, fade - solid))))
        gd.line([(x, 0), (x, h)], fill=c + (a,))
    im.alpha_composite(grad)
    d = ImageDraw.Draw(im)
    pad = int(sh * 0.12)
    tx = x0 + pad
    # logo card
    lh = int(sh * 0.22)
    lg = logo.copy()
    lg.thumbnail((int(sw * 0.3), lh))
    cp = int(lh * 0.12)
    card = Image.new("RGBA", (lg.width + cp * 2, lg.height + cp * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=cp, fill=(255, 255, 255, 245))
    card.alpha_composite(lg, (cp, cp))
    ty = y0 + pad
    im.alpha_composite(card, (tx, ty))
    ty += card.height + int(sh * 0.07)
    f1 = font("barlowcondensed-700.woff2", int(sh * 0.13))
    f2 = font("barlow-600.woff2", int(sh * 0.065))
    f3 = font("barlowcondensed-700.woff2", int(sh * 0.12))
    d.text((tx, ty), loc["business"], font=f1, fill=(255, 255, 255))
    ty += int(sh * 0.15)
    d.text((tx, ty), line2, font=f2, fill=rgb(signal))
    ty += int(sh * 0.10)
    d.text((tx, ty), phone, font=f3, fill=(255, 255, 255))
    ty += int(sh * 0.14)
    d.text((tx, ty), "www." + domain, font=f2, fill=(220, 226, 222))
    return im.convert("RGB")


def avatar(size=720):
    im = Image.new("RGB", (size, size), (255, 255, 255))
    lg = logo.copy()
    lg.thumbnail((int(size * 0.84), int(size * 0.84)))
    im.paste(lg, ((size - lg.width) // 2, (size - lg.height) // 2), lg)
    return im


avatar().save(out / "avatar.jpg", quality=92)
# Facebook cover 1640x624; mobile crops the sides, keep text inside the centre ~1300px
cover(1640, 624, (170, 40, 1470, 584)).save(out / "fb-cover.jpg", quality=88)
# X header 1500x500; the avatar overlaps bottom-left, so keep text top/centre
cover(1500, 500, (220, 20, 1300, 380)).save(out / "x-header.jpg", quality=88)
# YouTube banner 2560x1440; safe area for all devices is the centre 1546x423
cover(2560, 1440, (507, 508, 2053, 931)).save(out / "yt-banner.jpg", quality=88)
print("wrote", out)
