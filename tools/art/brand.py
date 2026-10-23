"""Profile picture sizes, app icons and the favicon, all from docs/brand/profile.png (Kaapup at sunset).

The profile picture is AI art (prompt in art-src/raw/brand/prompt.txt). The 32 and 48 px favicons are cut from its
head; 16 px is too small for that, so it is hand-pixelled below. Run: python3 tools/art/brand.py
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "brand", "profile.png")
ICONS = os.path.join(ROOT, "assets", "icons")

# the head, steam to chin, in profile.png's 1024 px frame
HEAD = (130, 40, 890, 800)

PAL = {
    ".": (0, 0, 0, 0), "P": (86, 33, 116, 255), "Q": (170, 52, 92, 255), "R": (236, 96, 52, 255),
    "o": (30, 8, 12, 255), "h": (255, 252, 240, 255), "s": (214, 210, 206, 255), "S": (150, 142, 146, 255),
    "d": (92, 82, 90, 255), "b": (214, 112, 46, 255), "B": (150, 66, 30, 255), "c": (254, 219, 161, 255),
    "e": (30, 8, 12, 255), "w": (255, 255, 255, 255), "n": (54, 20, 20, 255), "t": (238, 104, 124, 255),
    "m": (252, 226, 180, 255),
}

FAVICON_16 = """
.PPPPPmPPmPPPPP.
PPPPPPPmPPmPPPPP
PPPPPPPooPPPPPPP
PPPPooooooooPPPP
PPPohsshssSSoPPP
PPohsshsssSSdoPP
PoddddddddddddoP
PobBbbbbbbbbBboP
QobBbwebbwebBboQ
QobBbeecceebBboQ
QobBcccnncccBboQ
RobBccottoccBboR
RobBbccooccbBboR
RRooBbccccbBooRR
RRRRoccccccoRRRR
.RRRoccccccoRRR.
"""


def from_grid(grid):
    rows = grid.strip().splitlines()
    im = Image.new("RGBA", (len(rows[0]), len(rows)))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            im.putpixel((x, y), PAL[ch])
    return im


def round_corners(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius, fill=255)
    out = im.copy()
    out.putalpha(mask)
    return out


def maskable(src, scale=0.84):
    """Shrinks the picture so Android's round or squircle mask can't clip the head. The body stays on the bottom
    edge; the rest of the canvas continues the background (a vertical gradient, so edge pixels extend cleanly)."""
    w, h = src.size
    small = src.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    x0, y0 = (w - small.width) // 2, h - small.height
    out = Image.new("RGB", src.size)
    for y in range(h):
        sy = min(max(y - y0, 0), small.height - 1)
        left, right = small.getpixel((0, sy)), small.getpixel((small.width - 1, sy))
        for x in range(w):
            if x < x0:
                out.putpixel((x, y), left)
            elif x >= x0 + small.width:
                out.putpixel((x, y), right)
    for y in range(y0):
        for x in range(x0, x0 + small.width):
            out.putpixel((x, y), small.getpixel((x - x0, 0)))
    out.paste(small, (x0, y0))
    return out


def main():
    src = Image.open(SRC).convert("RGB")
    out = os.path.join(ROOT, "docs", "brand")
    src.resize((400, 400), Image.LANCZOS).save(os.path.join(out, "profile-400.png"), optimize=True)

    os.makedirs(ICONS, exist_ok=True)
    src.resize((512, 512), Image.LANCZOS).save(os.path.join(ICONS, "icon-512.png"), optimize=True)
    src.resize((192, 192), Image.LANCZOS).save(os.path.join(ICONS, "icon-192.png"), optimize=True)
    src.resize((180, 180), Image.LANCZOS).save(os.path.join(ICONS, "apple-touch-icon.png"), optimize=True)
    maskable(src.resize((512, 512), Image.LANCZOS)).save(os.path.join(ICONS, "icon-maskable-512.png"), optimize=True)

    head = src.crop(HEAD).convert("RGBA")
    sizes = [
        from_grid(FAVICON_16),
        round_corners(head.resize((32, 32), Image.LANCZOS), 3),
        round_corners(head.resize((48, 48), Image.LANCZOS), 4),
    ]
    sizes[-1].save(os.path.join(ROOT, "favicon.ico"), format="ICO", sizes=[im.size for im in sizes], append_images=sizes[:-1])
    print("wrote docs/brand/profile-400.png, assets/icons/*, favicon.ico")


if __name__ == "__main__":
    main()
