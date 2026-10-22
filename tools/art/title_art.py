"""Composes the title-screen backdrop (256x144, shown x4) from the game's own pixel-art pieces.

A sunset sky over a Bengaluru skyline: Vidhana Soudha, the elevated metro, rooftops with water tanks and a row of
jacaranda trees in the foreground. Run: python3 tools/art/title_art.py
"""
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import tiles  # noqa: E402

W, H = 256, 144


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def silhouette(img, color, alpha=255):
    """Flat-colour version of an RGBA sprite."""
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    px, src = out.load(), img.load()
    for y in range(img.height):
        for x in range(img.width):
            if src[x, y][3] > 40:
                px[x, y] = color + (alpha,)
    return out


def main():
    rnd = random.Random(11)
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    # banded sunset sky (dithered bands look right at GBA resolution)
    stops = [(0, (38, 26, 82)), (40, (112, 58, 128)), (70, (226, 110, 104)), (92, (247, 170, 102)), (110, (252, 214, 140))]
    for y in range(H):
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                t = (y - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                c = lerp(stops[i][1], stops[i + 1][1], t)
                break
        else:
            c = stops[-1][1]
        d.line((0, y, W, y), fill=c + (255,))
    # stars
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(0, 40)
        img.putpixel((x, y), (255, 240, 220, 255))
    # sun
    d.ellipse((168, 74, 200, 106), fill=(255, 226, 150, 255))
    # distant city silhouette
    far = (150, 84, 120)
    x = 0
    while x < W:
        bw, bh = rnd.randint(8, 18), rnd.randint(14, 34)
        d.rectangle((x, 112 - bh, x + bw, 112), fill=far + (255,))
        if rnd.random() < 0.5:
            d.rectangle((x + 2, 112 - bh - 3, x + 5, 112 - bh), fill=(40, 30, 50, 255))  # water tank
        x += bw + rnd.randint(0, 3)
    # Vidhana Soudha in front of the far skyline
    vs, _, _ = tiles.building("vidhana_soudha")
    vs = vs.resize((int(vs.width * 0.62), int(vs.height * 0.62)), Image.NEAREST)
    img.alpha_composite(silhouette(vs, (96, 52, 92)), (40, 116 - vs.height))
    # elevated metro line with a train
    d.rectangle((0, 100, W, 103), fill=(70, 40, 80, 255))
    for px_ in range(6, W, 28):
        d.rectangle((px_, 103, px_ + 3, 118), fill=(70, 40, 80, 255))
    d.rectangle((150, 93, 236, 100), fill=(112, 66, 150, 255))
    for wx in range(153, 234, 6):
        d.rectangle((wx, 95, wx + 3, 97), fill=(255, 214, 140, 255))
    # near rooftops
    near = (58, 34, 66)
    x = -4
    while x < W:
        bw, bh = rnd.randint(16, 30), rnd.randint(10, 20)
        d.rectangle((x, 130 - bh, x + bw, H), fill=near + (255,))
        for wy in range(130 - bh + 4, 128, 6):
            for wx in range(x + 3, x + bw - 2, 6):
                if rnd.random() < 0.45:
                    d.rectangle((wx, wy, wx + 1, wy + 1), fill=(255, 196, 110, 255))
        if rnd.random() < 0.6:
            d.rectangle((x + 4, 130 - bh - 5, x + 9, 130 - bh), fill=(28, 20, 34, 255))
        x += bw + 2
    # jacaranda trees along the bottom
    jac, _ = tiles.prop("jacaranda")
    for tx in range(-8, W, 30):
        img.alpha_composite(jac, (tx + rnd.randint(-3, 3), H - jac.height + 4))
    out = os.path.join(ROOT, "assets", "images", "ui", "title_bg.png")
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
