"""Pixelizes raw AI art into game sprites and writes review contact sheets.

  creatures: art-src/raw/creatures/NNN_name.png -> assets/images/creatures/NNN.png (64x64)
  trainers:  art-src/raw/trainers/<key>.png     -> assets/images/trainers/<key>.png (56x72)
  battle:    art-src/raw/battle/<env>.png        -> assets/images/battle/<env>.png (256x108)
  title:     art-src/raw/title/*.png             -> assets/images/ui/title_bg.png (256x144)

Run: python3 tools/art/process_art.py [creatures|trainers|battle|title|all]
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from pixelize import pixelize  # noqa: E402

RAW = os.path.join(ROOT, "art-src", "raw")
OUT = os.path.join(ROOT, "assets", "images")
PREV = os.path.join(ROOT, "art-src", "previews")


def sheet(images, cell, cols, path, bg=(196, 226, 196, 255), labels=None):
    rows = (len(images) + cols - 1) // cols
    s = Image.new("RGBA", (cols * cell[0], rows * (cell[1] + 14)), bg)
    d = ImageDraw.Draw(s)
    for i, im in enumerate(images):
        x = (i % cols) * cell[0]
        y = (i // cols) * (cell[1] + 14)
        big = im.resize(cell, Image.NEAREST)
        s.alpha_composite(big, (x, y))
        if labels:
            d.text((x + 2, y + cell[1]), labels[i], fill=(40, 30, 60, 255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    s.save(path)


def creatures():
    src = os.path.join(RAW, "creatures")
    dst = os.path.join(OUT, "creatures")
    os.makedirs(dst, exist_ok=True)
    done, labels = [], []
    for f in sorted(os.listdir(src)):
        if not f.endswith(".png") or not f[:3].isdigit():
            continue
        img = pixelize(Image.open(os.path.join(src, f)), (64, 64), colors=24)
        img.save(os.path.join(dst, f"{f[:3]}.png"))
        done.append(img)
        labels.append(f[:-4])
    if done:
        sheet(done, (128, 128), 8, os.path.join(PREV, "creatures_sheet.png"), labels=labels)
    print(f"creatures: {len(done)}")


def trainers():
    src = os.path.join(RAW, "trainers")
    dst = os.path.join(OUT, "trainers")
    os.makedirs(dst, exist_ok=True)
    done, labels = [], []
    for f in sorted(os.listdir(src)):
        if not f.endswith(".png"):
            continue
        img = pixelize(Image.open(os.path.join(src, f)), (56, 72), colors=28)
        img.save(os.path.join(dst, f))
        done.append(img)
        labels.append(f[:-4])
    if done:
        sheet(done, (112, 144), 9, os.path.join(PREV, "trainers_sheet.png"), labels=labels)
    print(f"trainers: {len(done)}")


def scenic(kind, size, colors):
    src = os.path.join(RAW, kind)
    if not os.path.isdir(src):
        return []
    out = []
    for f in sorted(os.listdir(src)):
        if not f.endswith(".png"):
            continue
        img = Image.open(os.path.join(src, f)).convert("RGB")
        w, h = img.size
        target_ratio = size[0] / size[1]
        if w / h > target_ratio:
            nw = int(h * target_ratio)
            img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / target_ratio)
            img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        small = img.resize(size, Image.BOX).quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGBA")
        out.append((f, small))
    return out


def battle():
    dst = os.path.join(OUT, "battle")
    os.makedirs(dst, exist_ok=True)
    items = scenic("battle", (256, 108), 40)
    for f, im in items:
        im.save(os.path.join(dst, f))
    if items:
        sheet([im for _, im in items], (512, 216), 2, os.path.join(PREV, "battle_sheet.png"), labels=[f for f, _ in items])
    print(f"battle backgrounds: {len(items)}")


def title():
    items = scenic("title", (256, 144), 48)
    os.makedirs(os.path.join(OUT, "ui"), exist_ok=True)
    for f, im in items:
        name = "title_bg.png" if f.startswith("title_bg") else f
        im.save(os.path.join(OUT, "ui", name))
    print(f"title art: {len(items)}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("creatures", "all"):
        creatures()
    if what in ("trainers", "all"):
        trainers()
    if what in ("battle", "all"):
        battle()
    if what in ("title", "all"):
        title()
