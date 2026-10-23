"""The logo in every size (profile pictures, app icons, favicon) and the 1200x630 link-preview image.

The logo is the title screen's sunset over Vidhana Soudha, recomposed as a square from the same pieces as
title_art.py: the sun rises behind the central dome, the metro runs in front and jacarandas line the bottom.
It is drawn at 128 px and scaled up by whole pixels. At favicon size the scene is too detailed, so 16 px is
hand-pixelled (dome against the sun) and 32/48 px are cut from the middle of the scene.
Run: python3 tools/art/brand.py
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import tiles  # noqa: E402
from title_art import lerp, silhouette  # noqa: E402

BRAND = os.path.join(ROOT, "docs", "brand")
ICONS = os.path.join(ROOT, "assets", "icons")

PAL = {"a": (38, 26, 82), "b": (75, 42, 108), "c": (112, 58, 128), "d": (170, 84, 116), "f": (255, 214, 140),
       "Y": (255, 226, 150), "V": (96, 52, 92), "N": (58, 34, 66), "L": (167, 139, 214), "H": (214, 196, 240),
       "D": (120, 92, 176)}

FAVICON_16 = """
aaaaaaaaaaaaaaaa
aaaaaYYYYYYaaaaa
bbbYYYYYYYYYYbbb
bbYYYYVVVVYYYYbb
ccYYYVVVVVVYYYcc
ccYYYVVVVVVYYYcc
dVVYYVVVVVVYYVVd
dVVYVVVVVVVVYVVd
VVVVVVVVVVVVVVVV
VVVVVVVVVVVVVVVV
VVfVVfVVVVfVVfVV
VVVVVVVVVVVVVVVV
NNNNNNNNNNNNNNNN
NLLLNNLLLLNNLLLN
LHLLLLHLLLLLHLLL
DDDDDDDDDDDDDDDD
"""


def scene(W, H=None, horizon=None, sun_r=None, seed=11):
    """The title scene, recomposed: Vidhana Soudha at half size, centred, with the sun behind its dome.
    `horizon` (the building's base) and `sun_r` let the wide share card lower the city under its title."""
    rnd = random.Random(seed)
    H = H or W
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    k = H / 144  # title_art.py is 144 px tall; keep its proportions
    shift = 0 if horizon is None else horizon - round(116 * k)
    stops = [(0, (38, 26, 82)), (40 * k, (112, 58, 128)), (70 * k + shift, (226, 110, 104)),
             (92 * k + shift, (247, 170, 102)), (110 * k + shift, (252, 214, 140))]
    for y in range(H):
        c = stops[-1][1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                c = lerp(stops[i][1], stops[i + 1][1], (y - stops[i][0]) / (stops[i + 1][0] - stops[i][0]))
                break
        d.line((0, y, W, y), fill=c + (255,))
    for _ in range(int(40 * W / 256) + 6):
        img.putpixel((rnd.randrange(W), rnd.randrange(0, int(36 * k))), (255, 240, 220, 255))

    vs, _, _ = tiles.building("vidhana_soudha")
    vs = vs.resize((vs.width // 2, vs.height // 2), Image.NEAREST)
    vx, vy = (W - vs.width) // 2, round(116 * k) + shift - vs.height
    cx, cy, r = W // 2, vy + round(vs.height * 0.24), sun_r or round(W * 0.2)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 226, 150, 255))

    base = round(112 * k) + shift
    x = 0
    while x < W:
        bw, bh = rnd.randint(8, 16), rnd.randint(12, 28)
        d.rectangle((x, base - bh, x + bw, base), fill=(150, 84, 120, 255))
        if rnd.random() < 0.5:
            d.rectangle((x + 2, base - bh - 3, x + 5, base - bh), fill=(40, 30, 50, 255))  # water tank
        x += bw + rnd.randint(0, 3)
    img.alpha_composite(silhouette(vs, (96, 52, 92)), (vx, vy))

    deck = round(100 * k) + shift
    d.rectangle((0, deck, W, deck + 3), fill=(70, 40, 80, 255))
    for px_ in range(6, W, 28):
        d.rectangle((px_, deck + 3, px_ + 3, deck + 18), fill=(70, 40, 80, 255))
    train = int(W * 0.62)
    d.rectangle((train, deck - 7, W + 4, deck), fill=(112, 66, 150, 255))
    for wx in range(train + 3, W, 6):
        d.rectangle((wx, deck - 5, wx + 3, deck - 3), fill=(255, 214, 140, 255))

    near = round(130 * k) + shift
    x = -4
    while x < W:
        bw, bh = rnd.randint(14, 26), rnd.randint(8, 16)
        d.rectangle((x, near - bh, x + bw, H), fill=(58, 34, 66, 255))
        for wy in range(near - bh + 4, near - 2, 6):
            for wx in range(x + 3, x + bw - 2, 6):
                if rnd.random() < 0.45:
                    d.rectangle((wx, wy, wx + 1, wy + 1), fill=(255, 196, 110, 255))
        x += bw + 2
    jac, _ = tiles.prop("jacaranda")
    for tx in range(-10, W, 28):
        img.alpha_composite(jac, (tx + rnd.randint(-2, 2), H - jac.height + 8))
    return img


def from_grid(grid):
    rows = grid.strip().splitlines()
    im = Image.new("RGBA", (len(rows[0]), len(rows)))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            im.putpixel((x, y), PAL[ch] + (255,))
    return im


def save(im, path):
    im.convert("RGB").save(path, optimize=True)


def share_card():
    """The 1200x630 link-preview image: the title in the sky over the logo's dome-in-the-sun, at 5x."""
    card = scene(240, 126, horizon=116, sun_r=26).resize((1200, 630), Image.NEAREST)
    text = Image.new("RGBA", card.size)
    d = ImageDraw.Draw(text)
    font = os.path.join(ROOT, "assets", "fonts", "pixelify", "PixelifySans.ttf")

    def write(y, s, size, fill, stroke, shadow=0):
        f = ImageFont.truetype(font, size)
        f.set_variation_by_name("Bold")
        if shadow:
            d.text((600 + shadow, y + shadow), s, font=f, fill=(0, 0, 0, 102), anchor="mm", stroke_width=stroke,
                   stroke_fill=(0, 0, 0, 102))
        d.text((600, y), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill="#3a1f5c")

    write(88, "uru-mon", 150, "#fff4d6", 18, shadow=8)
    write(180, "A  BENGALURU  ADVENTURE", 36, "#ffe9a8", 8)
    card.alpha_composite(text)
    return card


def main():
    os.makedirs(ICONS, exist_ok=True)
    art = scene(128)
    big = art.resize((1024, 1024), Image.NEAREST)
    save(big, os.path.join(BRAND, "profile.png"))
    save(art.resize((512, 512), Image.NEAREST), os.path.join(BRAND, "profile-512.png"))
    save(art.resize((512, 512), Image.NEAREST), os.path.join(ICONS, "icon-512.png"))
    save(big.resize((192, 192), Image.LANCZOS), os.path.join(ICONS, "icon-192.png"))
    save(big.resize((180, 180), Image.LANCZOS), os.path.join(ICONS, "apple-touch-icon.png"))
    # Android masks icons to a circle or squircle: a wider scene keeps the building inside the central 80%
    save(scene(160).resize((640, 640), Image.NEAREST).resize((512, 512), Image.LANCZOS),
         os.path.join(ICONS, "icon-maskable-512.png"))

    middle = art.crop((24, 20, 104, 100))
    sizes = [from_grid(FAVICON_16), middle.resize((32, 32), Image.LANCZOS), middle.resize((48, 48), Image.LANCZOS)]
    sizes[-1].save(os.path.join(ROOT, "favicon.ico"), format="ICO", sizes=[im.size for im in sizes], append_images=sizes[:-1])
    save(share_card(), os.path.join(ICONS, "share.png"))
    print("wrote docs/brand/profile*.png, assets/icons/* (incl. the share.png link preview), favicon.ico")


if __name__ == "__main__":
    main()
