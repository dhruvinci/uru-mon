#!/usr/bin/env python3
"""Original 16 px Bengaluru world art; Pillow is the only runtime dependency.

All public renderers return fresh RGBA images at native resolution. Coordinates
select repeatable ground variations without Python's process-dependent hash or
global random state. Props use transparent backgrounds; collision rows run
top to bottom, columns left to right. Tree crowns can overhang walkable tiles.
Buildings conservatively block their footprint, including every warp door.

Run this file from any directory to write only art-src/previews/tiles_preview.png.
The contact sheet is enlarged with nearest-neighbour sampling, never smoothing.
"""

from pathlib import Path

from PIL import Image, ImageColor, ImageDraw


TILE = 16
OUTLINE = "#2a2230"
CREAM = "#fff0cf"
GRASS = ("#85bf65", "#65a455", "#a4d77b", "#497f49")
WOOD = ("#ba8050", "#87533e", "#dfac6b")
STONE = ("#b9b5b0", "#858b94", "#e0d8c5")
STEEL = ("#9db4bd", "#607785", "#e4f0e6")
WATER = ("#55b9cc", "#388fae", "#a2e5df")
PAINT = {
    "pink": "#efa3ac", "yellow": "#f4d481", "sky blue": "#97c9e5",
    "skyblue": "#97c9e5", "blue": "#97c9e5", "mint": "#a8d6b1",
    "white": "#f1e7ce", "red": "#d97062", "green": "#70af8a",
    "purple": "#a38acb", "grey": "#a8abb6", "gray": "#a8abb6",
}

GROUND_NAMES: list[str] = [
    "grass", "grass_flowers", "tall_grass", "dirt", "road", "road_line_h",
    "road_line_v", "zebra", "pavers", "sand", "wood_floor", "tile_floor",
    "carpet", "cave_floor", "mud", "bridge_h", "bridge_v", "stone_floor",
    "lab_floor", "mat", "stairs",
]

# Five rows, three columns per glyph. No external fonts or host font discovery.
_FONT = {
    "A": "010/101/111/101/101", "B": "110/101/110/101/110",
    "C": "011/100/100/100/011", "D": "110/101/101/101/110",
    "E": "111/100/110/100/111", "F": "111/100/110/100/100",
    "G": "011/100/101/101/011", "H": "101/101/111/101/101",
    "I": "111/010/010/010/111", "J": "001/001/001/101/010",
    "K": "101/101/110/101/101", "L": "100/100/100/100/111",
    "M": "101/111/111/101/101", "N": "101/111/111/111/101",
    "O": "010/101/101/101/010", "P": "110/101/110/100/100",
    "Q": "010/101/101/111/011", "R": "110/101/110/101/101",
    "S": "011/100/010/001/110", "T": "111/010/010/010/010",
    "U": "101/101/101/101/111", "V": "101/101/101/101/010",
    "W": "101/101/111/111/101", "X": "101/101/010/101/101",
    "Y": "101/101/010/010/010", "Z": "111/001/010/100/111",
    "0": "111/101/101/101/111", "1": "010/110/010/010/111",
    "2": "110/001/010/100/111", "3": "110/001/010/001/110",
    "4": "101/101/111/001/001", "5": "111/100/110/001/110",
    "6": "011/100/111/101/111", "7": "111/001/010/010/010",
    "8": "111/101/111/101/111", "9": "111/101/111/001/110",
    " ": "000/000/000/000/000", "-": "000/000/111/000/000",
    "+": "000/010/111/010/000", ".": "000/000/000/000/010",
    ":": "000/010/000/010/000", "/": "001/001/010/100/100",
    "!": "010/010/010/000/010", "?": "110/001/010/000/010",
    "'": "010/010/000/000/000", "(": "001/010/010/010/001",
    ")": "100/010/010/010/100", "&": "010/101/010/101/011",
    "₹": "111/010/111/100/010", "=": "000/111/000/111/000",
}


def _color(value):
    if isinstance(value, str):
        return ImageColor.getcolor(PAINT.get(value.lower(), value), "RGBA")
    values = tuple(value)
    return values if len(values) == 4 else (*values, 255)


def _shade(value, amount):
    r, g, b, a = _color(value)
    return tuple(max(1, min(255, v + amount)) for v in (r, g, b)) + (a,)


def _image(w=16, h=16, color=None):
    return Image.new("RGBA", (w, h), _color(color) if color else (0, 0, 0, 0))


def _pixels(im, pattern, palette, at=(0, 0)):
    rows = pattern.strip().splitlines()
    if len({len(row.strip()) for row in rows}) != 1:
        raise ValueError("Ragged hand-authored pixel grid")
    for y, row in enumerate(rows):
        for x, role in enumerate(row.strip()):
            if role != ".":
                im.putpixel((at[0] + x, at[1] + y), _color(palette[role]))


def text(s: str, color=(255, 255, 255, 255)) -> Image.Image:
    """3x5 text, one-pixel spacing; lowercase folds to uppercase, unknowns to ?.

    Newlines are supported with two pixels of leading. Empty text is a
    transparent 1x5 image, so consumers never receive zero-width PNGs.
    """
    lines = str(s).upper().split("\n")
    im = _image(max(1, max(len(line) * 4 - 1 for line in lines)), len(lines) * 7 - 2)
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            pattern = _FONT.get(char, _FONT["?"]).replace("/", "\n")
            _pixels(im, pattern.replace("0", "."), {"1": color}, (col * 4, row * 7))
    return im


def _label(im, s, box, color=CREAM, background=None):
    """Centre a sign, wrapping whole words instead of shrinking pixel letters."""
    x0, y0, x1, y1 = box
    if background:
        ImageDraw.Draw(im).rectangle(box, fill=background)
    max_chars = max(1, (x1 - x0 + 2) // 4)
    lines, line = [], ""
    for word in s.upper().split():
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = ""
        while len(word) > max_chars:
            if line:
                lines.append(line)
                line = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        line = (line + " " + word).strip()
    if line:
        lines.append(line)
    label = text("\n".join(lines), _color(color))
    if label.height > y1 - y0 + 1:
        raise ValueError(f"Sign {s!r} does not fit its signboard")
    im.alpha_composite(label, (x0 + (x1 - x0 + 1 - label.width) // 2,
                              y0 + (y1 - y0 + 1 - label.height) // 2))


def _seed(x, y, salt=0):
    value = (int(x) * 0x1F123BB5 + int(y) * 0x5F356495 + salt * 0x9E3779B9) & 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 0x45D9F3B) & 0xFFFFFFFF
    return value ^ (value >> 16)


_GRASS = """
................
................
...l............
..l.s...........
................
..........s.....
.........l.l....
................
................
....s...........
...l.l..........
................
...........l....
..........l.s...
................
................
"""
_BLADES = """
...l.......l....
..lgl.l...lgl.l.
..ggl.gl..ggl.gl
.lgsgggs.lgsgggs
.gsssss..gsssss.
..s.s.s...s.s.s.
................
................
.......l.......l
l.l...lgl.l...lg
l.gl..ggl.gl..gg
gggs.lgsgggs.lgs
sss..gsssss..gss
s.s...s.s.s...s.
................
................
"""


def tall_grass_overlay() -> Image.Image:
    """Foreground blade tips at the player's feet, with a transparent upper half."""
    im = _image()
    _pixels(im, _BLADES, {"g": "#4e8d47", "s": GRASS[3], "l": "#9bd273"})
    ImageDraw.Draw(im).rectangle((0, 0, 15, 7), fill=(0, 0, 0, 0))
    return im


def ground(name: str, x: int, y: int) -> Image.Image:
    """Opaque terrain. Texture motifs meet across tile edges without dark borders."""
    if name not in GROUND_NAMES:
        raise ValueError(f"Unknown ground {name!r}; choose from {GROUND_NAMES}")
    if name in _EXTRA_GROUNDS:
        return _ground_extra(name, x, y)
    seed = _seed(x, y)
    if name in ("grass", "grass_flowers", "tall_grass"):
        im = _image(color=GRASS[0] if name != "tall_grass" else "#6aa955")
        motif = _GRASS if name != "tall_grass" else _BLADES
        _pixels(im, motif, {"g": GRASS[1] if name != "tall_grass" else "#4e8d47",
                            "s": GRASS[3] if name == "tall_grass" else GRASS[1],
                            "l": GRASS[2] if name != "tall_grass" else "#9bd273"})
        if name == "grass" and seed % 3:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT if seed % 3 == 1 else Image.Transpose.FLIP_TOP_BOTTOM)
        if name == "grass_flowers":
            d = ImageDraw.Draw(im)
            for fx, fy, c in ((4, 4, "#fff0cf"), (11, 10, "#efa3ac"), (5, 12, "#f4d481")):
                fx += seed % 2
                d.line((fx, fy + 1, fx, fy + 3), fill=GRASS[3])
                d.line((fx - 1, fy, fx + 1, fy), fill=c)
                d.point((fx, fy - 1), fill=c)
                d.point((fx, fy), fill="#d99651")
        return im
    bases = {"dirt": "#cba36c", "sand": "#efd89c", "mud": "#a38260",
             "road": "#68717b", "road_line_h": "#68717b", "road_line_v": "#68717b",
             "zebra": "#68717b", "pavers": "#b5b3b0", "wood_floor": "#c28a58",
             "tile_floor": "#ede4cf", "carpet": "#bc657d", "cave_floor": "#97939d",
             "bridge_h": "#b98050", "bridge_v": "#b98050", "stone_floor": "#c7bdac",
             "lab_floor": "#d2e2e0", "mat": "#cba36c", "stairs": "#b9b5b0"}
    base = bases[name]
    im = _image(color=base)
    d = ImageDraw.Draw(im)
    if name in ("dirt", "sand", "mud", "cave_floor"):
        # Keep texture away from edges: no discontinuous seam when variants meet.
        for i in range(8):
            noise = _seed(x, y, i + 1)
            px, py = 2 + noise % 11, 2 + (noise >> 7) % 11
            d.line((px, py, px + (i % 2), py), fill=_shade(base, 15 if i % 2 else -17))
        if name == "mud":
            d.line((3, 10, 7, 10), fill="#866c58")
            d.line((4, 11, 7, 11), fill="#b79d76")
    elif name.startswith("road") or name == "zebra":
        for px, py in ((3, 3), (11, 5), (6, 12), (13, 13)):
            d.point((px, py), fill="#77818a" if (seed + px) % 2 else "#5c6470")
        if name == "road_line_h":
            d.rectangle((2, 7, 11, 8), fill=CREAM)
        elif name == "road_line_v":
            d.rectangle((7, 2, 8, 11), fill=CREAM)
        elif name == "zebra":
            for px in (1, 9):
                d.rectangle((px, 0, px + 3, 15), fill="#eee7d5")
    elif name == "pavers":
        # An 8x8 interlocking dog-bone paver, repeated with red accents.
        for by in (-8, 0, 8, 16):
            for bx in (-8, 0, 8, 16):
                bx += 4 if (by // 8) % 2 else 0
                c = "#c58271" if ((bx // 4 + by // 8) % 2 == 0) else "#c4c1b6"
                points = [(bx+2, by), (bx+5, by), (bx+5, by+2), (bx+7, by+2),
                          (bx+7, by+5), (bx+5, by+5), (bx+5, by+7), (bx+2, by+7),
                          (bx+2, by+5), (bx, by+5), (bx, by+2), (bx+2, by+2)]
                d.polygon(points, fill=c, outline="#8d9296")
                d.line((bx+2, by+1, bx+4, by+1), fill="#e0d8c5")
    elif name in ("wood_floor", "bridge_h", "bridge_v"):
        for py in range(0, 16, 4):
            d.line((0, py, 15, py), fill=WOOD[1])
            d.line((0, py + 1, 15, py + 1), fill=WOOD[2])
            px = (py * 2) % 16
            d.line((px, py, px, py + 3), fill=WOOD[1])
        if name.startswith("bridge"):
            for py in (0, 13):
                d.rectangle((0, py, 15, py + 2), fill=WOOD[1])
                d.line((0, py, 15, py), fill=WOOD[2])
                for px in (2, 10):
                    d.point((px, py + 1), fill="#e0d8c5")
            if name == "bridge_v":
                im = im.transpose(Image.Transpose.ROTATE_90)
    elif name in ("tile_floor", "lab_floor", "stone_floor"):
        for py in (0, 8):
            for px in (0, 8):
                fill = _shade(base, 6 if (px + py) % 16 else -5)
                d.rectangle((px + 1, py + 1, px + 7, py + 7), fill=fill)
                d.line((px, py, px + 7, py), fill=_shade(base, -24))
                d.line((px, py, px, py + 7), fill=_shade(base, -24))
        if name == "stone_floor":
            d.polygon(((7, 5), (9, 7), (7, 9), (5, 7)), fill="#a99d8e")
        elif name == "lab_floor":
            d.rectangle((1, 1, 2, 2), fill="#edf3e4")
    elif name == "carpet":
        for py in (3, 11):
            for px in (3, 11):
                d.point((px, py), fill="#e09c9c")
                d.point((px + 1, py + 1), fill="#a65370")
    elif name == "mat":
        d.rectangle((1, 3, 14, 12), fill="#b78b59")
        d.rectangle((2, 4, 13, 11), outline="#ebc98c")
        for py in (6, 8, 10):
            d.line((3, py, 12, py), fill="#866345")
    elif name == "stairs":
        for py in range(0, 16, 4):
            d.line((0, py, 15, py), fill=STONE[2])
            d.line((0, py + 3, 15, py + 3), fill=STONE[1])
    return im


def water(n: bool, e: bool, s: bool, w: bool, ne: bool, nw: bool,
          se: bool, sw: bool, x: int, y: int, style: str = "clear", bank: str = "grass") -> Image.Image:
    """Eight-neighbour shoreline: cardinal banks and concave diagonal corners.

    Flags describe water, not land. Cardinal banks take priority; a missing
    diagonal adds an inset only when both incident cardinal neighbours exist.
    """
    pal = _WATER_STYLES[style]
    im = _image(color=pal[0])
    d = ImageDraw.Draw(im)
    for px, py in ((2, 4), (10, 12)):
        d.line((px, py, px + 3, py), fill=pal[2])
        d.point((px + 4, py - 1), fill=pal[2])
        d.line((px + 1, py + 2, px + 4, py + 2), fill=pal[1])
    # Shore material is consistent around every edge. The grass is the same
    # base as ground('grass'); the sandy lip provides separation without ink.
    land, lip = _WATER_BANKS[bank]
    bank = (land, land, lip, pal[1])
    for connected, side in ((n, "n"), (e, "e"), (s, "s"), (w, "w")):
        if not connected:
            for offset, c in reversed(list(enumerate(bank))):
                if side in ("n", "s"):
                    yy = offset if side == "n" else 15 - offset
                    d.line((0, yy, 15, yy), fill=c)
                else:
                    xx = offset if side == "w" else 15 - offset
                    d.line((xx, 0, xx, 15), fill=c)
    for a, b, diag, right, bottom in (
        (n, w, nw, False, False), (n, e, ne, True, False),
        (s, w, sw, False, True), (s, e, se, True, True),
    ):
        if a and b and not diag:
            for yy in range(4):
                for xx in range(4):
                    distance = xx * xx + yy * yy
                    if distance <= 9:
                        # Along either shared edge this is exactly the cardinal
                        # bank profile: two grass pixels, sand, then dark water.
                        c = land if distance <= 1 else lip if distance <= 4 else pal[1]
                        d.point((15 - xx if right else xx, 15 - yy if bottom else yy), fill=c)
        elif not a and not b:
            # Fill the outside square where two banks meet, removing pinholes.
            xx, yy = (12 if right else 0), (12 if bottom else 0)
            d.rectangle((xx, yy, xx + 3, yy + 3), fill=land)
    if bank == "stone":
        # granite embankment blocks along every bank
        for connected, side in ((n, "n"), (e, "e"), (s, "s"), (w, "w")):
            if not connected:
                for k in range(0, 16, 5):
                    if side == "n":
                        d.line((k, 0, k, 1), fill="#8f8574")
                    elif side == "s":
                        d.line((k, 14, k, 15), fill="#8f8574")
                    elif side == "w":
                        d.line((0, k, 1, k), fill="#8f8574")
                    else:
                        d.line((14, k, 15, k), fill="#8f8574")
    return im


def _panel(d, box, color, outline=OUTLINE):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=_color(color), outline=outline)
    if x1 - x0 > 3 and y1 - y0 > 3:
        d.line((x0 + 1, y1 - 1, x1 - 1, y1 - 1), fill=_shade(color, -27))
        d.line((x1 - 1, y0 + 1, x1 - 1, y1 - 1), fill=_shade(color, -27))
        d.line((x0 + 1, y0 + 1, x1 - 2, y0 + 1), fill=_shade(color, 26))


def _window(d, box, grilled=True):
    x0, y0, x1, y1 = box
    _panel(d, box, "#68a8bb")
    d.line((x0 + 1, y0 + 2, x1 - 2, y0 + 2), fill="#b5e5df")
    if grilled:
        for px in range(x0 + 3, x1, 3):
            d.line((px, y0 + 1, px, y1 - 1), fill="#445363")
        d.line((x0 + 1, (y0 + y1) // 2, x1 - 1, (y0 + y1) // 2), fill="#445363")
    d.line((x0 - 1, y1 + 1, x1 + 1, y1 + 1), fill=STONE[2])


def _vessel(d, x, y, width=9, steaming=False):
    d.ellipse((x, y + 5, x + width - 1, y + 8), fill=STEEL[1], outline=OUTLINE)
    _panel(d, (x, y + 2, x + width - 1, y + 6), STEEL[0])
    d.ellipse((x, y, x + width - 1, y + 3), fill=STEEL[2], outline=OUTLINE)
    d.line((x + 2, y + 2, x + width - 3, y + 2), fill=STEEL[0])
    if steaming:
        d.line([(x + 3, y - 2), (x + 2, y - 3), (x + 3, y - 5)], fill=CREAM)
        d.line([(x + 6, y - 2), (x + 5, y - 4), (x + 6, y - 6)], fill=CREAM)


_PROP_SIZES = {
    "tree": (2, 2), "jacaranda": (2, 2), "gulmohar": (2, 2),
    "rain_tree": (3, 3), "banyan": (3, 3), "coconut_palm": (1, 2),
    "bush": (1, 1), "hedge": (1, 1), "flower_bed": (1, 1),
    "rock": (1, 1), "boulder": (2, 2), "lamp_post": (1, 2),
    "bench": (2, 1), "signpost": (1, 1), "trash_bin": (1, 1),
    "water_tank": (1, 1), "fence_h": (1, 1), "fence_v": (1, 1),
    "compound_wall_h": (1, 1), "compound_wall_v": (1, 1), "gate": (1, 1),
    "auto_rickshaw": (2, 2), "car": (2, 2), "scooter": (1, 1),
    "bus_stop": (3, 2), "cow": (2, 1), "statue": (1, 2),
    "fountain": (2, 2), "cricket_stumps": (1, 1), "table": (2, 1),
    "chair": (1, 1), "bed": (1, 2), "tv": (1, 1), "bookshelf": (1, 2),
    "plant_pot": (1, 1), "darshini_counter": (3, 1), "shop_shelf": (2, 1),
    "cloud_kiosk": (1, 2), "stove": (1, 1), "rug": (2, 2),
    "desk": (2, 1), "lab_machine": (1, 2), "sofa": (2, 1),
    "pooja_shelf": (1, 1), "cave_rock": (1, 1), "stalagmite": (1, 1),
    "crate": (1, 1),
}
PROP_NAMES: list[str] = list(_PROP_SIZES)


def _foliage(d, box, palette):
    """Scalloped silhouette, joined interior and small top-left leaf clusters."""
    x0, y0, x1, y1 = box
    width, height = x1 - x0 + 1, y1 - y0 + 1
    lobes = [(0.15, 0.02, 0.67, 0.62), (0.40, 0.12, 0.96, 0.73),
             (0.00, 0.28, 0.55, 0.89), (0.23, 0.35, 0.80, 1.00)]
    boxes = [(x0 + int(a * (width-1)), y0 + int(b * (height-1)),
              x0 + int(c * (width-1)), y0 + int(e * (height-1))) for a,b,c,e in lobes]
    for coords in boxes:
        d.ellipse(coords, fill=OUTLINE)
    for a,b,c,e in boxes:
        d.ellipse((a+1,b+1,c-1,e-1), fill=palette[1])
    for a,b,c,e in boxes:
        d.ellipse((a+2,b+1,c-2,max(b+2,e-4)), fill=palette[0])
    for fx, fy in ((0.27, 0.18), (0.53, 0.27), (0.14, 0.46), (0.37, 0.60), (0.73, 0.45)):
        xx, yy = x0 + int(fx*width), y0 + int(fy*height)
        d.line((xx, yy, xx+2, yy), fill=palette[2])
        d.point((xx+1, yy-1), fill=palette[2])


def _tree(name, im):
    d = ImageDraw.Draw(im)
    width, height = im.size
    mid = width // 2
    _panel(d, (mid-3, height-17, mid+3, height-3), WOOD[1])
    d.line((mid-2,height-15,mid-2,height-4), fill=WOOD[2])
    d.line((mid-4,height-2,mid+5,height-2), fill=OUTLINE)
    palettes = _TREE_PALETTES
    if name == "banyan":
        for xx in (9, 14, 33, 38):
            d.line((xx, 20, xx, 42), fill=OUTLINE)
            d.line((xx+1, 20, xx+1, 41 - xx % 3), fill=WOOD[0])
        d.polygon(((mid-3,28),(mid+3,28),(mid+6,45),(mid-7,45)), fill=WOOD[1], outline=OUTLINE)
        d.line((mid-2,29,mid-4,43), fill=WOOD[2])
    _foliage(d, (1, 1, width-2, height-10), palettes[name])
    if name in ("jacaranda", "gulmohar"):
        for xx, yy in ((7, 14), (14, 5), (24, 13), (18, 20)):
            d.line((xx, yy, xx+2, yy), fill=palettes[name][2])
            d.point((xx+1, yy+1), fill="#ffe0a2")


def prop(name: str, **params) -> tuple[Image.Image, list[list[bool]]]:
    """Render a transparent prop. flower_bed/car accept Pillow colours or hex.

    Unspecified props block every occupied tile. Palms, lamps and statues block
    only their bases; large trees have walk-under crowns. An open gate and rug
    are passable. Unknown names/parameters raise ValueError to catch map typos.
    """
    if name not in _PROP_SIZES:
        raise ValueError(f"Unknown prop {name!r}; choose from {PROP_NAMES}")
    allowed = _PROP_PARAMS.get(name, set())
    if set(params) - allowed:
        raise ValueError(f"Unsupported parameters for {name}: {sorted(set(params) - allowed)}")
    tw, th = _PROP_SIZES[name]
    im = _image(tw * TILE, th * TILE)
    d = ImageDraw.Draw(im)
    collision = [[True for _ in range(tw)] for _ in range(th)]
    if name in _TREE_PALETTES:
        _tree(name, im)
        collision = [[False] * tw for _ in range(th)]
        if tw == 2:
            collision[-1] = [True, True]
        else:
            collision[1][1] = collision[2][1] = True
            if name == "banyan":
                collision[-1] = [True] * 3
    elif name == "coconut_palm":
        collision = [[False], [True]]
        d.polygon(((8,10),(10,10),(9,27),(7,30),(5,30),(7,24)), fill=WOOD[0], outline=OUTLINE)
        for yy in (15,19,23,27):
            d.line((7,yy,9,yy), fill=WOOD[1])
        for points in (((8,9),(3,3),(0,5),(5,6)), ((8,8),(9,1),(14,1),(11,4)),
                       ((8,9),(15,6),(15,11),(12,9)), ((8,9),(3,9),(0,15),(4,12)),
                       ((8,9),(12,12),(15,17),(14,11)), ((8,8),(3,0),(5,0),(9,5))):
            d.polygon(points, fill=GRASS[1], outline=OUTLINE)
            d.line((points[0],points[1]), fill=GRASS[2])
        d.rectangle((7,9,9,11), fill=WOOD[1])
        d.point((7,9), fill=WOOD[2])
    elif name in ("bush", "hedge"):
        if name == "bush":
            _foliage(d, (1,3,14,14), (GRASS[1],GRASS[3],GRASS[2]))
        else:
            _panel(d, (0,3,15,13), GRASS[3])
            d.rectangle((0,4,15,10), fill=GRASS[1])
            for xx in (1,5,9,13):
                d.line((xx,5,xx+1,5), fill=GRASS[2])
                d.point((xx+1,9), fill=GRASS[3])
    elif name == "flower_bed":
        _panel(d, (0,4,15,14), "#bb8065")
        d.rectangle((2,5,13,12), fill="#7d654d")
        color = _color(params.get("color", "#f1a0bd"))
        for xx,yy in ((4,7),(10,6),(7,10),(12,10)):
            d.line((xx,yy,xx,yy+2), fill=GRASS[2])
            d.line((xx-1,yy,xx+1,yy), fill=color)
            d.line((xx,yy-1,xx,yy+1), fill=color)
            d.point((xx,yy), fill="#ffe498")
    elif name in ("rock", "cave_rock", "boulder"):
        size = im.width
        base = "#888398" if name == "cave_rock" else STONE[0]
        d.polygon(((1,size-5),(3,size//2),(size//3,3),(size-7,2),
                   (size-2,size//2),(size-1,size-5),(size-6,size-2),(5,size-2)), fill=base, outline=OUTLINE)
        d.polygon(((3,size//2),(size//3,4),(size-8,3),(size//2,size//2)), fill=_shade(base,31))
        d.polygon(((size//2,size//2),(size-3,size//2),(size-2,size-5),(size-6,size-3),(4,size-3)), fill=_shade(base,-28))
        d.line((size//3,7,size//2,9), fill=_shade(base,-28))
        d.point((size-7,size//2+3), fill=_shade(base,31))
    elif name == "lamp_post":
        collision = [[False],[True]]
        _panel(d, (6,7,9,28), STEEL[1])
        _panel(d, (4,27,11,30), STONE[1])
        d.polygon(((3,3),(7,0),(12,3)), fill=OUTLINE)
        _panel(d, (3,3,12,10), "#ffe399")
        d.line((7,4,7,9), fill=STEEL[1])
    elif name in ("bench", "table", "desk"):
        for xx in (3,25):
            _panel(d,(xx,8,xx+3,14),WOOD[1])
        _panel(d,(1,4,30,10),WOOD[0])
        d.line((3,7,28,7),fill=WOOD[2])
        if name == "bench":
            _panel(d,(1,1,30,5),WOOD[0])
            d.line((3,3,28,3),fill=WOOD[2])
        elif name == "desk":
            _panel(d,(3,1,12,6),CREAM)
            d.line((5,3,10,3),fill=STEEL[1])
            _panel(d,(23,1,27,5),"#b58ac3")
    elif name == "signpost":
        _panel(d,(7,5,9,15),WOOD[1])
        _panel(d,(1,1,14,9),WOOD[0])
        d.line((3,3,11,3),fill=CREAM)
        d.line((3,5,8,5),fill=CREAM)
        d.line((3,7,10,7),fill=CREAM)
    elif name == "trash_bin":
        _panel(d,(4,4,12,14),"#50998b")
        _panel(d,(3,2,13,5),"#71b9a2")
        d.rectangle((6,1,10,2),fill=OUTLINE)
        for xx in (6,9):
            d.line((xx,7,xx,12),fill="#b1d4b7")
    elif name == "water_tank":
        _panel(d,(2,4,13,13),"#414552")
        d.ellipse((2,1,13,6),fill="#555c68",outline=OUTLINE)
        for yy in (7,10):
            d.line((3,yy,12,yy),fill="#6e7780")
        d.rectangle((6,0,9,2),fill=OUTLINE)
        d.line((3,4,3,11),fill="#6e7780")
    elif name.startswith("fence_"):
        for xx in (2,7,12):
            _panel(d,(xx,3,xx+2,14),WOOD[0])
        for yy in (6,10):
            _panel(d,(0,yy,15,yy+2),WOOD[0])
        if name == "fence_v":
            im = im.transpose(Image.Transpose.ROTATE_90)
    elif name.startswith("compound_wall_"):
        _panel(d,(0,4,15,14),"#d5c6a9")
        d.rectangle((0,3,15,5),fill=STONE[2],outline=OUTLINE)
        for yy,xx in ((8,4),(12,11)):
            d.line((0,yy,15,yy),fill="#b1a28d")
            d.line((xx,yy-2,xx,yy),fill="#b1a28d")
        if name == "compound_wall_v":
            im = im.transpose(Image.Transpose.ROTATE_90)
    elif name == "gate":
        collision = [[False]]
        for xx in (0,14):
            _panel(d,(xx,2,xx+1,14),STEEL[1])
        # Leaves swing back along the sides; the centre is visibly open.
        for xx in (3,12):
            d.line((xx,4,xx,11),fill=OUTLINE)
        for yy in (4,10):
            d.line((1,yy+2,3,yy),fill=STEEL[1])
            d.line((12,yy,14,yy+2),fill=STEEL[1])
    elif name in _EXTRA_PROPS:
        _EXTRA_PROPS[name](im, d, collision, **params)
    else:
        _prop_objects(name, params, im, d, collision)
    return im, collision


def _prop_objects(name, params, im, d, collision):
    """Vehicles, furnishings and smaller hand-authored objects."""
    if name in ("auto_rickshaw", "car"):
        for xx in (4,24):
            _panel(d,(xx,8,xx+3,14),"#414552")
            _panel(d,(xx,22,xx+3,28),"#414552")
        color = "#e9b945" if name == "auto_rickshaw" else _color(params.get("color", "#e88779"))
        d.rounded_rectangle((6,2,25,29),radius=4,fill=color,outline=OUTLINE)
        d.line((7,7,7,25),fill=_shade(color,27))
        _window(d,(8,7,23,13),False)
        if name == "auto_rickshaw":
            _panel(d,(6,14,25,24),"#414552")
            d.line((8,15,22,15),fill="#6e7780")
            d.rectangle((9,18,13,22),fill="#bb986c")
            d.rectangle((17,18,22,22),fill="#bb986c")
            d.line((15,15,15,23),fill="#e9b945")
            d.rectangle((10,3,21,5),fill="#f7db7b")
        else:
            _panel(d,(9,15,22,21),color)
            _window(d,(9,22,22,25),False)
        for xx in (8,22):
            d.rectangle((xx,5,xx+1,6),fill=CREAM)
            d.point((xx,27),fill="#c94f58")
        d.line((11,28,20,28),fill=STEEL[1])
    elif name == "scooter":
        _pixels(im,"""
................
......OOO.......
......OsO.......
...OOOOsOOOO....
...OllblsllO....
......ObO.......
.....OlbsO......
.....OlbsO......
.....OsssO......
.....OOOOO......
.....ObbbO......
....OlbbsO......
....ObsssO......
.....OOOO.......
......OsO.......
......OOO.......
""",{"O":OUTLINE,"b":"#80afc4","l":"#bededc","s":"#536879"})
    elif name == "bus_stop":
        _panel(d,(3,9,44,25),"#8eb7bd")
        for xx in (5,20,35):
            _window(d,(xx,10,xx+9,21),False)
        _panel(d,(8,22,36,25),WOOD[0])
        for xx in (3,42):
            _panel(d,(xx,6,xx+2,30),STEEL[1])
        _panel(d,(0,2,47,8),"#b58ac3")
        _label(im,"BUS",(2,3,45,7))
        # The bench spans the bottom-centre tile; the shelter is fully blocked.
    elif name == "cow":
        _pixels(im,"""
................................
.......O.................O..O...
....OOO.OOOOOOOOOOOO.....OsOsO..
...OlwwwwwwwwwwwwwwwOOOOOwwwO...
..OlwwwwsswwwwwwwwwwwwwwwwwO....
..OlwwwsssswwwwwwwwwswOlwwwwsO..
..OlwwwsssswwwwwwwwsswOlwwwwsO..
..OlwwwwsswwwwwwwwwsswOwwOOwsO..
..OwwwwwwwwwwwwwwwwwwwOOOsssO...
..OwwwwwwwwwwwwwwwwwwsO..OOO....
..OwwwwwwwwwwwwwwwwsssO.........
...OwwOOOOOOOOOOOOwwOO..........
...OswO..........OswO...........
...OswO..........OswO...........
...OOOO..........OOOO...........
................................
""",{"O":OUTLINE,"w":"#eee3c8","l":"#fff4d9","s":"#a39483"})
    elif name == "statue":
        collision[:] = [[False],[True]]
        _panel(d,(2,25,13,30),STONE[1])
        _panel(d,(4,21,11,25),STONE[0])
        d.ellipse((5,2,10,8),fill=STONE[0],outline=OUTLINE)
        d.polygon(((5,8),(10,8),(12,18),(9,20),(9,22),(5,22),(5,18),(3,17)),fill=STONE[0],outline=OUTLINE)
        d.line((6,10,5,17),fill=STONE[2])
    elif name == "fountain":
        d.ellipse((1,12,30,29),fill=STONE[1],outline=OUTLINE)
        d.ellipse((2,10,29,25),fill=STONE[2],outline=OUTLINE)
        d.ellipse((5,12,26,23),fill=WATER[0],outline=STONE[1])
        d.arc((7,13,25,23),0,160,fill=WATER[2])
        _panel(d,(13,8,18,19),STONE[0])
        d.ellipse((9,6,22,12),fill=STONE[2],outline=OUTLINE)
        d.line((15,2,15,8),fill=WATER[2],width=2)
        for side in (-1,1):
            d.line([(15,3),(15+side*4,2),(15+side*7,6),(15+side*8,12)],fill=WATER[2])
        d.point((7,16),fill=WATER[2])
        d.point((23,16),fill=WATER[2])
    elif name == "cricket_stumps":
        for xx in (4,7,10):
            _panel(d,(xx,4,xx+1,14),WOOD[2])
        d.line((4,3,11,3),fill=WOOD[1])
        d.point((6,2),fill=CREAM)
        d.point((9,2),fill=CREAM)
    elif name == "chair":
        _panel(d,(3,1,12,8),WOOD[0])
        _panel(d,(2,7,13,12),WOOD[0])
        for xx in (3,11):
            d.line((xx,12,xx,15),fill=OUTLINE)
    elif name == "bed":
        _panel(d,(1,1,14,30),WOOD[1])
        _panel(d,(2,4,13,27),"#f0e5d2")
        _panel(d,(3,5,12,10),CREAM)
        _panel(d,(2,12,13,27),"#7ca7c8")
        d.line((3,14,12,14),fill="#c1dfe3")
        d.line((4,15,4,25),fill="#a7cddd")
        d.line((2,29,13,29),fill=WOOD[2])
    elif name == "tv":
        d.line((7,1,4,0),fill=STEEL[1])
        d.line((8,1,11,0),fill=STEEL[1])
        _panel(d,(1,2,14,12),"#555968")
        _window(d,(3,3,11,10),False)
        d.point((13,10),fill="#efab66")
        d.rectangle((5,13,11,14),fill=OUTLINE)
    elif name in ("bookshelf", "shop_shelf"):
        _panel(d,(1,1,im.width-2,im.height-2),WOOD[0])
        for yy in range(3,im.height-5,8):
            d.rectangle((2,yy,im.width-3,yy+5),fill=WOOD[1])
            for xx in range(3,im.width-3,3):
                c = ("#9ac499","#e8b365","#bc7c89","#81b4c9")[(xx//3+yy)%4]
                d.rectangle((xx,yy+1+(xx%2),xx+1,yy+5),fill=c)
                d.point((xx,yy+3),fill=CREAM)
            d.line((2,yy+6,im.width-3,yy+6),fill=WOOD[2])
    elif name == "plant_pot":
        d.polygon(((4,9),(12,9),(10,15),(6,15)),fill="#c57c57",outline=OUTLINE)
        _panel(d,(3,8,12,10),"#dc9869")
        d.line((8,3,8,8),fill=GRASS[3])
        for box in ((2,2,7,5),(8,0,12,4),(8,5,14,7)):
            d.ellipse(box,fill=GRASS[1],outline=OUTLINE)
        d.line((4,3,6,3),fill=GRASS[2])
    elif name == "darshini_counter":
        _panel(d,(0,8,47,15),STEEL[0])
        d.line((1,9,46,9),fill=STEEL[2])
        for xx in (16,31):
            d.line((xx,11,xx,14),fill=STEEL[1])
        _vessel(d,3,2,10)
        _vessel(d,17,0,10)
        # Three perforated idli trays stacked on a narrow centre spindle.
        d.line((36,1,36,9),fill=STEEL[1])
        for yy in (2,5,8):
            d.ellipse((30,yy,43,yy+3),fill=STEEL[0],outline=OUTLINE)
            for xx in (33,37,41):
                d.point((xx,yy+1),fill=CREAM)
    elif name == "cloud_kiosk":
        _panel(d,(1,1,14,30),"#9bb9c9")
        d.rectangle((0,1,15,7),fill="#635c99",outline=OUTLINE)
        # A tightly tracked 3x5 label fits CLOUD in fifteen pixels, unscaled.
        for i,c in enumerate("CLOUD"):
            _pixels(im,_FONT[c].replace("/","\n").replace("0","."),{"1":CREAM},(i*3,2))
        _window(d,(3,9,12,19),False)
        d.rectangle((5,12,10,15),fill="#e4f0e6")
        d.point((4,14),fill="#e4f0e6")
        _panel(d,(2,21,13,25),STEEL[1])
        for xx in (4,6,8,10):
            d.point((xx,22),fill=CREAM)
        d.rectangle((5,27,10,28),fill=OUTLINE)
    elif name == "stove":
        _panel(d,(1,1,14,14),STEEL[0])
        for xx in (5,10):
            for yy in (4,9):
                d.ellipse((xx-2,yy-1,xx+1,yy+2),fill=OUTLINE)
                d.point((xx,yy),fill=STEEL[1])
        d.line((3,13,12,13),fill=STEEL[2])
    elif name == "rug":
        collision[:] = [[False,False],[False,False]]
        _panel(d,(2,2,29,29),"#ad5f7d")
        d.rectangle((4,4,27,27),outline="#efc382")
        d.rectangle((6,6,25,25),outline="#d99497")
        d.polygon(((15,9),(23,15),(15,23),(8,15)),fill="#efc382")
        d.polygon(((15,12),(19,15),(15,19),(12,15)),fill="#77799f")
        for xx in range(4,29,3):
            d.line((xx,0,xx,1),fill=CREAM)
            d.line((xx,30,xx,31),fill=CREAM)
    elif name == "lab_machine":
        _panel(d,(1,1,14,30),STEEL[0])
        _window(d,(3,3,12,13),False)
        d.line([(4,9),(6,9),(7,6),(8,10),(10,8)],fill="#c3eb9c")
        for yy in (17,21,25):
            d.line((4,yy,10,yy),fill=STEEL[1])
            d.point((12,yy),fill="#e7ad65" if yy==21 else "#a8d679")
    elif name == "sofa":
        _panel(d,(2,1,29,12),"#b67d8e")
        _panel(d,(4,7,27,13),"#d597a2")
        d.line((16,7,16,12),fill="#936478")
        for xx in (1,27):
            _panel(d,(xx,5,xx+3,14),"#c68a99")
    elif name == "pooja_shelf":
        _panel(d,(1,1,14,14),WOOD[0])
        d.polygon(((3,9),(8,3),(12,9)),fill="#e2ad52",outline=OUTLINE)
        d.rectangle((5,5,10,10),fill="#c36353")
        d.line((7,7,8,9),fill="#ffdd8b")
        d.line((4,12,12,12),fill=WOOD[2])
        d.ellipse((7,10,11,12),fill="#eab65d",outline=OUTLINE)
        d.point((9,9),fill="#fff0cf")
    elif name == "stalagmite":
        d.polygon(((1,14),(5,5),(7,10),(10,1),(14,14)),fill="#91879c",outline=OUTLINE)
        d.line((10,4,9,12),fill="#c4b5c9")
        d.line((5,8,4,12),fill="#c4b5c9")
    elif name == "crate":
        _panel(d,(1,1,14,14),WOOD[0])
        d.rectangle((3,3,12,12),outline=WOOD[1])
        d.line((3,3,12,12),fill=WOOD[2],width=2)
        d.line((3,12,12,3),fill=WOOD[1],width=2)
        for xx in (2,13):
            for yy in (2,13):
                d.point((xx,yy),fill=STEEL[2])
    else:
        raise AssertionError(f"Unimplemented prop: {name}")


def _integer(value, name, low, high=None):
    if isinstance(value, bool) or not isinstance(value, int) or value < low or (high is not None and value > high):
        raise ValueError(f"{name} must be an integer in {low}..{high if high is not None else 'infinity'}")
    return value


def interior_wall(width_tiles: int, style: str = "plain") -> Image.Image:
    """Two-tile room wall, with repeatable panelling and a solid skirting board."""
    _integer(width_tiles, "width_tiles", 1)
    if style in _WALL_EXTRA:
        return _interior_wall_extra(width_tiles, style)
    styles = {"plain": "#e7d3b4", "wood": "#bb865c", "lab": "#cbdcdb",
              "palace": "#e4cfa4", "shop": "#c7d8b3", "cave": "#87828e"}
    if style not in styles:
        raise ValueError(f"Unknown wall style {style!r}; choose from {list(styles)}")
    im = _image(width_tiles*TILE,32,styles[style])
    d = ImageDraw.Draw(im)
    for xx in range(0, im.width, 16):
        if style == "wood":
            for px in (xx,xx+8):
                d.line((px,0,px,27),fill=WOOD[1])
                d.line((px+1,0,px+1,26),fill=WOOD[2])
                d.line((px+4,7,px+4,15),fill=WOOD[1])
        elif style == "cave":
            for yy in (0,10,20):
                px = xx + (4 if yy==10 else 0)
                d.polygon(((px,yy+3),(px+4,yy),(px+13,yy+1),(px+15,yy+8),(px+3,yy+9)),
                          fill="#9b939f",outline="#625e70")
                d.line((px+4,yy+1,px+11,yy+2),fill="#b7a9b5")
        else:
            _panel(d,(xx+2,6,xx+13,24),styles[style],_shade(styles[style],-25))
            if style == "palace":
                d.rectangle((xx+4,8,xx+11,22),outline="#b28d56")
                d.polygon(((xx+7,12),(xx+10,15),(xx+7,18),(xx+5,15)),fill="#b28d56")
            elif style == "lab":
                d.line((xx+1,18,xx+15,18),fill="#6c9ca7")
                d.rectangle((xx+5,8,xx+10,10),fill="#f0f2d9")
            elif style == "shop" and (xx//16)%2==0:
                _panel(d,(xx+4,8,xx+11,19),"#f2ddaa")
                d.line((xx+6,11,xx+9,11),fill="#be7660")
                d.line((xx+6,14,xx+9,14),fill="#be7660")
    d.rectangle((0,0,im.width-1,2),fill=_shade(styles[style],-32))
    d.line((0,3,im.width-1,3),fill=_shade(styles[style],25))
    d.rectangle((0,27,im.width-1,31),fill=_shade(styles[style],-40))
    d.line((0,27,im.width-1,27),fill=_shade(styles[style],12))
    d.line((0,31,im.width-1,31),fill=OUTLINE)
    return im


_BUILDING_SIZES = {
    "house": (4,3), "shop": (4,3), "darshini": (4,3), "kirana": (4,3),
    "lab": (6,4), "glass_house": (7,5), "stadium": (8,5),
    "tech_tower": (6,6), "tutor_house": (6,4), "palace": (9,6),
    "hill_pavilion": (6,4), "metro_station": (8,4), "vidhana_soudha": (13,8),
    "temple": (5,5), "syndicate_hq": (6,4), "cave_entrance": (3,2),
    "player_house": (5,4), "rival_house": (5,4),
}


def _tile_roof(im, box):
    x0,y0,x1,y1 = box
    d = ImageDraw.Draw(im)
    inset = min(10,(x1-x0)//5)
    points = ((x0+inset,y0),(x1-inset,y0),(x1,y1-3),(x1,y1),(x0,y1),(x0,y1-3))
    d.polygon(points,fill="#b95946",outline=OUTLINE)
    for yy in range(y0+2,y1-2,4):
        offset = max(1,round(inset*(1-(yy-y0)/(y1-y0-3))))
        d.line((x0+offset,yy,x1-offset,yy),fill="#ec9b63")
        d.line((x0+offset,yy+2,x1-offset,yy+2),fill="#91453f")
        for xx in range(x0+offset+3,x1-offset,6):
            d.line((xx,yy,xx,yy+2),fill="#d67850")
    d.line((x0+inset+1,y0+1,x1-inset-1,y0+1),fill="#ffbc7a")
    d.line((x0+1,y1-2,x1-1,y1-2),fill="#753e3c")
    d.line((x0+1,y1-1,x1-1,y1-1),fill="#d67850")


def _steps(d, box, color=STONE[0]):
    x0,y0,x1,y1 = box
    d.rectangle(box,fill=color,outline=OUTLINE)
    for yy in range(y0+1,y1,3):
        d.line((x0+1,yy,x1-1,yy),fill=_shade(color,25))
        if yy+2<y1:
            d.line((x0+1,yy+2,x1-1,yy+2),fill=_shade(color,-28))


def _arch(d, box, color="#455363", trim=STONE[2]):
    x0,y0,x1,y1 = box
    r = (x1-x0)//2
    d.ellipse((x0,y0,x1,y0+2*r),fill=trim,outline=OUTLINE)
    d.rectangle((x0,y0+r,x1,y1),fill=trim,outline=OUTLINE)
    d.ellipse((x0+2,y0+2,x1-2,y0+2*r-2),fill=color)
    d.rectangle((x0+2,y0+r,x1-2,y1),fill=color)


def _door(im, col, style="wood"):
    """Door or threshold inside its returned bottom-row warp trigger tile."""
    d = ImageDraw.Draw(im)
    x,y = col*TILE,im.height-TILE
    if style == "threshold":
        # The facade already contains a full-height arch or gate. Its threshold
        # is the warp target; do not superimpose a second, miniature doorway.
        pass
    elif style == "metal":
        _panel(d,(x+1,y,x+14,y+13),"#606573")
        for yy in (3,5,7):
            d.line((x+4,y+yy,x+11,y+yy),fill="#9298a0")
        d.point((x+11,y+10),fill="#e9bd51")
    elif style == "glass":
        _window(d,(x+2,y,x+13,y+13),False)
        d.line((x+8,y+1,x+8,y+12),fill=STEEL[2])
        d.point((x+10,y+8),fill=CREAM)
    else:
        _panel(d,(x+3,y,x+12,y+13),WOOD[1])
        d.rectangle((x+5,y+2,x+10,y+6),fill=WOOD[0])
        d.point((x+10,y+9),fill="#f3d484")
    d.line((x+1,y+14,x+14,y+14),fill=STONE[2])
    d.line((x+1,y+15,x+14,y+15),fill=STONE[1])


def _house(im, wall, roof, door_col, two_storey=False, veranda=False):
    d = ImageDraw.Draw(im)
    width,height = im.size
    roof_bottom = 23 if roof=="tile" else 20
    if height>=80:
        roof_bottom=29 if roof=="tile" else 23
    _panel(d,(3,roof_bottom-4,width-4,height-3),wall)
    d.rectangle((4,height-8,width-5,height-4),fill=_shade(wall,-30))
    if two_storey or height>=64:
        for xx in range(10,width-12,16):
            _window(d,(xx,roof_bottom+3,xx+8,roof_bottom+12))
        d.line((4,height-22,width-5,height-22),fill=_shade(wall,-35))
        d.line((4,height-21,width-5,height-21),fill=_shade(wall,24))
    for col in range(width//16):
        if col!=door_col:
            xx = col*16+4
            if 4<=xx and xx+7<width-3:
                _window(d,(xx,height-18,xx+7,height-10))
    if roof=="tile":
        _tile_roof(im,(0,2,width-1,roof_bottom))
    else:
        _panel(d,(1,5,width-2,roof_bottom),"#c9c6b5")
        d.rectangle((4,8,width-5,roof_bottom-4),fill="#a7afa8")
        # Parapet rim and black plastic rooftop tank, not a generic pitched roof.
        d.line((2,6,width-3,6),fill=CREAM)
        d.line((3,roof_bottom-2,width-4,roof_bottom-2),fill=STONE[2])
        im.alpha_composite(prop("water_tank")[0],(width-22,2))
    if veranda:
        _tile_roof(im,(0,height-31,width-1,height-22))
        for xx in (5,23,width-26,width-8):
            _panel(d,(xx,height-22,xx+3,height-6),STONE[2])
        _steps(d,(1,height-6,width-2,height-1),STONE[0])


def _shop(im, sign, awning, eatery=False):
    d = ImageDraw.Draw(im)
    width,height=im.size
    _panel(d,(2,8,width-3,height-3),PAINT["white"])
    _panel(d,(1,2,width-2,16),"#538b67" if eatery else "#526d8d")
    _label(im,sign,(3,3,width-4,15))
    for xx in range(1,width-2,6):
        c = _color(awning) if (xx//6)%2==0 else _color(CREAM)
        d.rectangle((xx,18,min(xx+5,width-2),24),fill=c)
        d.line((xx,25,min(xx+5,width-2),25),fill=_shade(c,-27))
    d.line((1,17,width-2,17),fill=OUTLINE)
    d.line((1,26,width-2,26),fill=OUTLINE)
    _panel(d,(5,28,width-6,height-4),STEEL[0])
    for yy in range(30,height-4,3):
        d.line((6,yy,width-7,yy),fill=STEEL[1])
        d.line((6,yy+1,width-7,yy+1),fill=STEEL[2])
    if eatery:
        _panel(d,(5,height-13,24,height-3),"#be7770")
        _vessel(d,8,height-21,12,True)


def building(kind: str, **params) -> tuple[Image.Image, list[list[bool]], list[tuple[int, int]]]:
    """A building sprite, conservative footprint mask, and blocked warp doors.

    House defaults: 4x3, pink, tiled roof, centre-right door. Shop defaults:
    4x3, SHOP sign, red awning. Fixed landmarks accept no extra parameters.
    Invalid dimensions, roof names, colours and parameters fail explicitly.
    """
    if kind not in _BUILDING_SIZES:
        raise ValueError(f"Unknown building {kind!r}; choose from {list(_BUILDING_SIZES)}")
    allowed = {"w","h","wall","roof","door_x"} if kind=="house" else {"w","sign","awning"} if kind=="shop" else _BUILDING_PARAMS.get(kind, set())
    if set(params)-allowed:
        raise ValueError(f"Unsupported parameters for {kind}: {sorted(set(params)-allowed)}")
    tw,th=_BUILDING_SIZES[kind]
    if kind=="house":
        tw=_integer(params.get("w",tw),"w",3,7)
        th=_integer(params.get("h",th),"h",3,5)
    elif kind=="shop":
        tw=_integer(params.get("w",tw),"w",3,6)
    door_col=_integer(params.get("door_x",tw//2),"door_x",0,tw-1) if kind not in _SIZED_BUILDINGS else 0
    im=_image(tw*TILE,th*TILE)
    doors=[(door_col,th-1)]
    style="wood"
    if kind in ("house","player_house","rival_house","tutor_house"):
        wall=params.get("wall", "mint" if kind=="rival_house" else "yellow" if kind=="tutor_house" else "pink")
        roof=params.get("roof","tile")
        if roof not in ("tile","flat"):
            raise ValueError("roof must be 'tile' or 'flat'")
        _house(im,_color(wall),roof,door_col,kind in ("player_house","rival_house"),kind=="tutor_house")
    elif kind in ("shop","darshini","kirana"):
        sign=str(params.get("sign",{"shop":"SHOP","darshini":"DARSHINI","kirana":"KIRANA"}[kind]))
        awning=_color(params.get("awning","sky blue" if kind=="kirana" else "#c7756b"))
        _shop(im,sign,awning,kind=="darshini")
    elif kind in _EXTRA_BUILDINGS:
        if kind in _SIZED_BUILDINGS:
            lo_w, hi_w, lo_h, hi_h = _SIZED_BUILDINGS[kind]
            tw=_integer(params.get("w",tw),"w",lo_w,hi_w)
            th=_integer(params.get("h",th),"h",lo_h,hi_h)
            im=_image(tw*TILE,th*TILE)
            door_col=_integer(params.get("door_x",tw//2),"door_x",0,tw-1)
        doors,style=_EXTRA_BUILDINGS[kind](im,door_col,**{k:v for k,v in params.items() if k not in ("w","h","door_x")})
    else:
        doors,style=_landmark(kind,im)
    for col,row in doors:
        # The cave mouth already fills its trigger tile. A second little arch
        # would look like a stone door placed inside the natural opening.
        if kind != "cave_entrance" and style != "none":
            _door(im,col,style)
    collision=[[True]*tw for _ in range(th)]
    return im,collision,doors


def _dome(d, box, color, ribs=True):
    x0,y0,x1,y1=box
    middle=(x0+x1)//2
    d.ellipse(box,fill=color,outline=OUTLINE)
    d.rectangle((x0,y0+(y1-y0)//2,x1,y1),fill=color,outline=OUTLINE)
    if ribs:
        for fraction in (0.25,0.5,0.75):
            xx=x0+int((x1-x0)*fraction)
            d.line([(middle,y0+2),(xx,y0+(y1-y0)//2),(xx,y1-1)],fill=_shade(color,-35))
    d.line((x0+2,y1-2,x1-2,y1-2),fill=_shade(color,30))
    d.line((middle,y0-4,middle,y0),fill=OUTLINE)
    d.point((middle,y0-4),fill="#e8b55d")


def _columns(d, xs, top, bottom, color=STONE[2], width=5):
    for xx in xs:
        _panel(d,(xx,top,xx+width,bottom),color)
        _panel(d,(xx-2,top,xx+width+2,top+3),color)
        _panel(d,(xx-2,bottom-3,xx+width+2,bottom),color)


def _landmark(kind, im):
    d=ImageDraw.Draw(im)
    width,height=im.size
    tw,th=width//16,height//16
    doors=[(tw//2,th-1)]
    style="threshold"
    if kind=="lab":
        _panel(d,(4,17,width-5,height-4),"#d7e0d5")
        _panel(d,(1,9,width-2,20),"#a2b8bd")
        d.line((3,11,width-4,11),fill=CREAM)
        _label(im,"URUMON LAB",(5,12,width-6,17),OUTLINE)
        for xx in (9,25,57,73):
            _window(d,(xx,24,xx+12,40),False)
            d.line((xx+6,25,xx+6,39),fill=STEEL[2])
        _panel(d,(35,22,60,44),"#a7c7c8")
        # Original sprout emblem: research into the city's living habitats.
        d.line((47,29,47,38),fill="#4b8263")
        d.ellipse((39,27,47,32),fill="#71ae7b",outline=OUTLINE)
        d.ellipse((47,24,55,30),fill="#a3ce7d",outline=OUTLINE)
        _steps(d,(28,54,67,63))
        doors=[(2,3),(3,3)]
        style="glass"
    elif kind=="glass_house":
        _panel(d,(3,38,width-4,height-4),"#a1d0ca")
        d.polygon(((1,38),(23,23),(width-24,23),(width-2,38)),fill="#addbd2",outline=OUTLINE)
        for xx in range(8,width-8,10):
            d.line((width//2,23,xx,38),fill="#698d8c")
            _window(d,(xx,44,xx+7,65),False)
            d.line((xx+4,45,xx+4,64),fill=STONE[2])
        d.line((3,40,width-4,40),fill=STONE[2],width=2)
        _dome(d,(39,7,73,34),"#b9ded2")
        _panel(d,(39,34,73,73),"#a4ccc5")
        for xx in (44,56,68):
            d.line((xx,35,xx,64),fill=STONE[2])
        _label(im,"GLASS HOUSE",(27,37,85,44),OUTLINE,STONE[2])
        _arch(d,(46,47,66,74),"#699ca6",STONE[2])
        d.line((1,74,width-2,74),fill=STONE[1],width=2)
    elif kind=="stadium":
        # Cricket seating bowl, perimeter wall, scoreboard and two lattice towers.
        d.polygon(((18,25),(37,18),(91,18),(109,25),(119,48),(9,48)),fill="#85b978",outline=OUTLINE)
        for yy in (27,32,37):
            d.line((20,yy,107,yy),fill="#e8d494",width=3)
            for xx in range(22,106,5):
                d.point((xx,yy),fill="#a15e61")
        _panel(d,(3,45,width-4,height-4),"#d2c6a9")
        for xx in range(10,width-12,13):
            _panel(d,(xx,52,xx+8,65),"#a8b7a1")
        _panel(d,(38,20,89,31),"#526a70")
        _label(im,"CHINNASWAMY",(40,22,87,29))
        _arch(d,(46,48,81,76),"#405360","#e4d8b7")
        for xx in range(51,79,5):
            d.line((xx,54,xx,75),fill=STEEL[2])
        for xx in (9,width-18):
            _panel(d,(xx,9,xx+7,48),STEEL[1])
            for yy in range(12,46,7):
                d.line((xx+1,yy,xx+6,yy+6),fill=STEEL[2])
                d.line((xx+6,yy,xx+1,yy+6),fill=STEEL[2])
            _panel(d,(xx-6,1,xx+13,12),STEEL[1])
            for bx in range(xx-3,xx+12,5):
                for by in (4,8):
                    d.rectangle((bx,by,bx+2,by+1),fill="#fff0cf")
        doors=[(3,4),(4,4)]
    elif kind=="tech_tower":
        _panel(d,(10,8,width-11,height-9),"#507d98")
        _panel(d,(5,17,18,height-9),"#b1c3c5")
        for yy in range(12,78,13):
            for xx in range(22,82,12):
                _window(d,(xx,yy,xx+10,yy+10),False)
                if (xx//12+yy//13)%3==0:
                    d.line((xx+2,yy+7,xx+7,yy+2),fill="#c1e2db")
        _panel(d,(23,1,72,11),"#605e94")
        _label(im,"NAMMA TECH",(25,3,70,9))
        _panel(d,(4,80,width-5,86),"#b5c8c9")
        _steps(d,(22,87,73,95))
        doors=[(2,5),(3,5)]
        style="glass"
    elif kind=="palace":
        _panel(d,(17,35,width-18,height-5),"#d8c196")
        _tile_roof(im,(26,17,width-27,39))
        for xx in range(30,width-30,21):
            d.polygon(((xx,42),(xx+9,33),(xx+18,42)),fill="#f0dfba",outline=OUTLINE)
            _panel(d,(xx,42,xx+18,68),"#e2cba3")
            d.line((xx+1,44,xx+17,64),fill=WOOD[1],width=2)
            d.line((xx+17,44,xx+1,64),fill=WOOD[1],width=2)
            _window(d,(xx+5,46,xx+12,57))
        # Round corner turrets, conical roofs and small stone battlements.
        for xx in (3,width-26):
            _panel(d,(xx,22,xx+22,height-5),"#c7af89")
            d.rectangle((xx+2,24,xx+6,height-7),fill="#ead1a1")
            d.polygon(((xx-1,23),(xx+11,2),(xx+24,23)),fill="#8b697d",outline=OUTLINE)
            d.line((xx+11,4,xx+3,21),fill="#b18c9b")
            for yy in (33,55,75):
                _arch(d,(xx+7,yy,xx+14,yy+12),"#627888","#dbc69f")
            for yy in (28,50,71):
                d.line((xx+1,yy,xx+21,yy),fill="#9a876d")
        _panel(d,(57,40,86,78),"#dfc79b")
        for xx in range(57,86,7):
            _panel(d,(xx,35,xx+4,42),"#dfc79b")
        _arch(d,(63,54,80,80),"#5a515e","#f1dfb7")
        _steps(d,(47,83,96,95),"#c2b398")
    elif kind=="hill_pavilion":
        _steps(d,(1,51,width-2,63),"#b5aea0")
        _panel(d,(4,21,width-5,53),"#a5aaa3")
        for xx in (12,37,62):
            _arch(d,(xx,26,xx+21,52),"#596b69","#c7c3ac")
        _columns(d,(6,31,57,83),25,54,"#c7c3ac",4)
        _panel(d,(1,18,width-2,25),"#aaa99a")
        d.polygon(((7,18),(20,10),(76,10),(89,18)),fill="#c7c3ac",outline=OUTLINE)
        _dome(d,(36,4,59,15),"#b2b7a7")
        d.line((3,20,width-4,20),fill="#e1dbc2")
        doors=[(2,3),(3,3)]
    elif kind=="metro_station":
        # Elevated deck leaves daylight below; broad central stair reaches ground.
        for xx in (13,103):
            _panel(d,(xx,28,xx+10,60),"#b2b4ad")
            _panel(d,(xx-3,58,xx+13,62),STONE[1])
        _panel(d,(0,7,width-1,34),"#d1dbd3")
        d.polygon(((0,7),(8,1),(width-9,1),(width-1,7)),fill="#aebdc0",outline=OUTLINE)
        for xx in range(7,width-10,15):
            _window(d,(xx,10,xx+11,21),False)
        d.rectangle((1,25,width-2,29),fill="#8d69a6")
        d.line((1,24,width-2,24),fill="#c3a4cf")
        _label(im,"METRO",(45,9,82,17),CREAM,"#685787")
        _steps(d,(45,35,82,63))
        for xx in (42,84):
            d.line((xx,35,xx,62),fill=OUTLINE,width=2)
            d.line((xx+1,35,xx+1,62),fill=STEEL[2])
        doors=[(3,3),(4,3)]
        style="glass"
    elif kind=="vidhana_soudha":
        _government(im)
        doors=[(5,7),(6,7),(7,7)]
    elif kind=="temple":
        _temple(im)
        doors=[(2,4)]
    elif kind=="syndicate_hq":
        _panel(d,(3,17,width-4,height-4),"#a3a4aa")
        _panel(d,(0,13,width-1,21),"#80838f")
        _panel(d,(8,2,width-9,16),"#4f535f")
        _label(im,"CONCRETE SYNDICATE",(10,3,width-11,14),"#f1cc69")
        for xx in (9,66):
            _window(d,(xx,27,xx+19,42))
        for xx in range(4,width-4,8):
            d.polygon(((xx,46),(xx+4,46),(xx+1,52),(xx-3,52)),fill="#e9bd51")
            d.polygon(((xx+4,46),(xx+8,46),(xx+5,52),(xx+1,52)),fill=OUTLINE)
        d.line((4,53,width-5,53),fill=OUTLINE)
        for xx in (6,width-9):
            _panel(d,(xx,24,xx+2,44),"#c2c0b7")
        doors=[(2,3),(3,3)]
        style="metal"
    elif kind=="cave_entrance":
        d.polygon(((0,30),(2,13),(9,6),(17,2),(31,1),(42,9),(47,22),(47,31)),
                  fill="#96939c",outline=OUTLINE)
        d.polygon(((3,14),(10,7),(19,3),(28,3),(21,11),(10,17)),fill="#c1b6b6")
        d.polygon(((34,8),(42,12),(46,26),(37,23)),fill="#746e83")
        _arch(d,(10,10,37,31),OUTLINE,"#aaa0aa")
        d.line((14,30,33,30),fill="#645b6d")
        d.polygon(((16,13),(19,12),(18,19)),fill="#89818e")
    else:
        raise AssertionError(f"Unimplemented building: {kind}")
    return doors,style


def _government(im):
    d=ImageDraw.Draw(im)
    width=im.width
    pale="#e9dbb5"
    stone="#c9bb98"
    _panel(d,(4,59,width-5,117),pale)
    _panel(d,(1,54,width-2,62),stone)
    for xx in range(10,width-16,15):
        _window(d,(xx,66,xx+9,77))
        _arch(d,(xx,87,xx+10,108),"#786f66",pale)
    # Broad central drum and ribbed dome, framed by smaller corner cupolas.
    _panel(d,(71,43,136,83),pale)
    _panel(d,(82,30,125,48),stone)
    _dome(d,(80,8,127,37),"#e7d7ad")
    for xx in (91,102,113):
        _arch(d,(xx,39,xx+5,47),"#8f9386",pale)
    for xx in (11,47,143,179):
        _panel(d,(xx,47,xx+17,57),pale)
        _dome(d,(xx-1,32,xx+18,48),"#ddd0aa")
        d.line((xx-3,52,xx+20,52),fill="#a99a7e")
    for xx in range(7,width-7,8):
        d.rectangle((xx,51,xx+3,54),fill=pale,outline="#a99a7e")
    d.polygon(((64,72),(104,53),(143,72)),fill=pale,outline=OUTLINE)
    d.line((73,69,104,56,134,69),fill="#fff0cf",width=2)
    d.ellipse((100,60,108,68),fill="#b99a5c",outline=OUTLINE)
    _panel(d,(60,73,147,82),stone)
    _label(im,"VIDHANA SOUDHA",(64,75,143,80),OUTLINE)
    _columns(d,range(12,195,15),83,114,pale,5)
    _steps(d,(50,114,157,127),stone)
    # Wider stair terraces reinforce the grand, low silhouette.
    d.line((36,121,171,121),fill=STONE[2])
    d.line((27,125,180,125),fill=STONE[1])


def _temple(im):
    d=ImageDraw.Draw(im)
    _panel(d,(6,42,73,73),"#b9ac96")
    _steps(d,(3,71,76,79),"#b9ac96")
    # Stepped south-Indian gopura with tiny sculptural niches, not a dome.
    for tier in range(5):
        yy=8+tier*8
        half=7+tier*5
        _panel(d,(40-half,yy,40+half,yy+7),"#d0b998")
        d.line((39-half,yy+7,41+half,yy+7),fill="#86745f")
        for xx in range(36-half,41+half,8):
            if xx>40-half:
                d.rectangle((xx,yy+3,xx+2,yy+5),fill="#8d7868")
                d.point((xx+1,yy+2),fill=CREAM)
    d.line((35,5,45,5),fill=OUTLINE)
    for xx in (36,40,44):
        d.line((xx,2,xx,5),fill="#c09a53")
        d.point((xx,1),fill=CREAM)
    _arch(d,(30,49,49,72),"#4e4853","#dfc8a6")
    _columns(d,(12,61),48,70,"#d4c1a1",4)
    # Nandi: large seated granite bull, hump, horns and a low plinth.
    _panel(d,(51,68,76,75),"#918d89")
    d.polygon(((53,65),(54,59),(59,57),(62,52),(66,54),(67,58),
               (72,56),(75,59),(74,65),(71,67),(55,67)),fill="#4b4c57",outline=OUTLINE)
    d.line((70,57,69,52),fill=OUTLINE,width=2)
    d.line((74,57,76,53),fill=OUTLINE,width=2)
    d.line((56,60,61,59),fill="#777681")
    d.point((73,60),fill="#c8c0ac")
    d.line((66,58,67,63),fill="#d6ad64")


def _town():
    """A small composed neighbourhood exercising shared terrain and prop edges."""
    cols,rows=36,24
    im=_image(cols*TILE,rows*TILE)
    # Tile-space lake includes a bite in its north bank and a small island.
    lake={(x,y) for y in range(15,23) for x in range(24,35)
          if not (x<27 and y<18) and not (29<=x<=30 and 18<=y<=19)}
    for y in range(rows):
        for x in range(cols):
            name="grass"
            if y in (10,14) or x in (15,19):
                name="pavers"
            if 11<=y<=13 or 16<=x<=18:
                name="road"
                if y==12 and not 16<=x<=18:
                    name="road_line_h"
                elif x==17 and not 11<=y<=13:
                    name="road_line_v"
            if x==14 and 11<=y<=13:
                name="zebra"
            if 21<=x<=24 and 5<=y<=8:
                name="grass_flowers"
            tile=ground(name,x,y)
            if (x,y) in lake:
                flags=[(x+dx,y+dy) in lake for dx,dy in ((0,-1),(1,0),(0,1),(-1,0),(1,-1),(-1,-1),(1,1),(-1,1))]
                tile=water(*flags,x,y)
            im.alpha_composite(tile,(x*TILE,y*TILE))
    for x in range(24,35):
        im.alpha_composite(ground("bridge_h",x,20),(x*TILE,20*TILE))
    buildings=[("player_house",2,2,{}),("rival_house",9,2,{}),
               ("darshini",2,7,{}),("kirana",9,7,{}),("lab",27,2,{}),
               ("tutor_house",2,17,{}),("house",10,17,{"w":4,"h":3,"wall":"sky blue","roof":"flat"})]
    objects=[]
    for kind,x,y,params in buildings:
        asset,_,doors=building(kind,**params)
        for dx,dy in doors:
            for py in range(y+dy+1,min(rows,y+dy+3)):
                im.alpha_composite(ground("pavers",x+dx,py),((x+dx)*TILE,py*TILE))
        objects.append((y+asset.height/TILE,x,y,asset))
    for name,x,y in (("jacaranda",0,4),("gulmohar",13,7),("rain_tree",20,1),
                     ("banyan",0,20),("tree",20,16),("coconut_palm",35,17),
                     ("coconut_palm",31,13),("bush",7,5),("flower_bed",8,5),
                     ("bench",21,8),("bus_stop",21,10),("auto_rickshaw",9,12),
                     ("car",25,11),("scooter",18,7),("lamp_post",19,8),
                     ("lamp_post",15,17),("cow",8,22),
                     ("fountain",21,5),("rock",32,22),("cricket_stumps",21,22),
                     ("signpost",25,15),("trash_bin",24,10)):
        asset=prop(name)[0]
        objects.append((y+asset.height/TILE,x,y,asset))
    for x in (2,3,5,6,7,9,10,12,13):
        asset=prop("compound_wall_h")[0]
        objects.append((6.5,x,6,asset))
    for x in (4,11):
        objects.append((6.5,x,6,prop("gate")[0]))
    for _,x,y,asset in sorted(objects,key=lambda item:item[0]):
        im.alpha_composite(asset,(x*TILE,y*TILE))
    return im


def preview() -> Image.Image:
    """Labelled native-resolution atlas of every asset plus a sample town.

    The CLI alone scales this image by three. Water cases include all 16
    cardinal masks, each missing diagonal, concave bays and isolated water.
    Repeated 3x3 ground swatches expose seams; magenta marks warp door tiles
    in a separate footprint strip below each building, not on the artwork.
    """
    width=768
    sheet=_image(width,3400,"#eee4cf")
    d=ImageDraw.Draw(sheet)

    def heading(title,y,detail=None):
        d.rectangle((8,y,width-9,y+13),fill="#3b4854")
        sheet.alpha_composite(text(title),(14,y+4))
        if detail:
            sheet.alpha_composite(text(detail, _color("#6d675f")),(14,y+18))

    heading("URU-MON / BENGALURU WORLD ATLAS",8,"16 PX ORIGINAL PIXEL ART / LIGHT FROM TOP LEFT / PREVIEW AT 3X")
    heading("01 / GROUND - REPEATED 3 X 3",39)
    y0=59
    for i,name in enumerate(GROUND_NAMES):
        x=14+(i%8)*94
        y=y0+(i//8)*66
        sheet.alpha_composite(text(name.replace("_"," "),_color(OUTLINE)),(x,y))
        for dy in range(3):
            for dx in range(3):
                sheet.alpha_composite(ground(name,dx,dy),(x+dx*16,y+9+dy*16))
    y0+=3*66
    heading("02 / WATER - ALL CARDINAL BANKS AND DIAGONAL INSETS",y0)
    cases=[]
    for mask in range(16):
        flags=tuple(bool(mask&(1<<i)) for i in range(4))
        cases.append((f"{mask:02}",(*flags,True,True,True,True)))
    for i,label in enumerate(("NE","NW","SE","SW")):
        diag=[True]*4
        diag[i]=False
        cases.append((label,(True,True,True,True,*diag)))
    cases.extend((("BAY",(True,True,True,True,False,False,False,False)),
                  ("LAKE",(False,False,False,False,False,False,False,False))))
    for i,(label,flags) in enumerate(cases):
        x=14+i*33
        sheet.alpha_composite(text(label,_color(OUTLINE)),(x,y0+19))
        sheet.alpha_composite(water(*flags,i,0),(x,y0+28))
    y0+=54
    heading("03 / PROPS - NATIVE TILE FOOTPRINTS",y0,"RED = BLOCKED / GREEN = WALKABLE; STRIPS BELOW EACH SPRITE")
    y0+=32
    for i,name in enumerate(PROP_NAMES):
        x=14+(i%8)*94
        y=y0+(i//8)*82
        label=text(name.replace("_","\n") if len(name)>19 else name.replace("_"," "),_color(OUTLINE))
        sheet.alpha_composite(label,(x,y))
        asset,grid=prop(name)
        # Subtle checkerboard makes transparent crowns and openings reviewable.
        for yy in range(0,48,8):
            for xx in range(0,48,8):
                d.rectangle((x+xx,y+15+yy,x+xx+7,y+15+yy+7),fill="#ded7bf" if (xx+yy)%16 else "#e7dec5")
        sheet.alpha_composite(asset,(x,y+15))
        for row,values in enumerate(grid):
            for col,blocked in enumerate(values):
                d.rectangle((x+col*4,y+65+row*4,x+col*4+2,y+67+row*4),fill="#bb7173" if blocked else "#6a9c78")
    y0+=((len(PROP_NAMES)+7)//8)*82+4
    heading("04 / INTERIOR WALLS AND COLOUR VARIANTS",y0)
    for i,style in enumerate(("plain","wood","lab","palace","shop","cave")):
        x=14+i*122
        sheet.alpha_composite(text(style,_color(OUTLINE)),(x,y0+19))
        sheet.alpha_composite(interior_wall(6,style),(x,y0+29))
    y0+=70
    for i,(name,params) in enumerate((("car",{"color":"#f3ce70"}),
                                      ("car",{"color":"mint"}),
                                      ("flower_bed",{"color":"#9f83d1"}),
                                      ("flower_bed",{"color":"#f48160"}))):
        x=14+i*94
        sheet.alpha_composite(text(name.replace("_"," "),_color(OUTLINE)),(x,y0))
        sheet.alpha_composite(prop(name,**params)[0],(x,y0+10))
    sheet.alpha_composite(text("GRASS OVERLAY",_color(OUTLINE)),(408,y0))
    sheet.alpha_composite(ground("tall_grass",0,0),(408,y0+12))
    # A simple boot-height marker demonstrates where grass crosses the legs.
    d.rectangle((413,y0+15,419,y0+25),fill="#565c80")
    sheet.alpha_composite(tall_grass_overlay(),(408,y0+12))
    y0+=50
    heading("05 / BUILDINGS - DOORS IN PINK, SOLID FOOTPRINTS IN RED",y0)
    y0+=22
    x,row_height=14,0
    entries=[(kind,{}) for kind in _BUILDING_SIZES]
    entries.extend((("house",{"w":3,"h":3,"wall":"mint","roof":"flat","door_x":0}),
                    ("house",{"w":7,"h":5,"wall":"sky blue","roof":"tile","door_x":6}),
                    ("shop",{"w":3,"sign":"COFFEE","awning":"yellow"})))
    for kind,params in entries:
        asset,grid,doors=building(kind,**params)
        cell_width=max(asset.width+16,len(kind)*4+12)
        cell_height=asset.height+len(grid)*3+30
        if x+cell_width>width-10:
            x=14
            y0+=row_height+7
            row_height=0
        sheet.alpha_composite(text(kind.replace("_"," "),_color(OUTLINE)),(x,y0))
        sheet.alpha_composite(asset,(x,y0+10))
        for gy,row in enumerate(grid):
            for gx,_ in enumerate(row):
                d.rectangle((x+gx*4,y0+asset.height+13+gy*3,x+gx*4+2,y0+asset.height+14+gy*3),
                            fill="#bf64a3" if (gx,gy) in doors else "#ba7d78")
        x+=cell_width
        row_height=max(row_height,cell_height)
    y0+=row_height+12
    heading("06 / A WALK THROUGH THE NEIGHBOURHOOD",y0)
    town=_town()
    final_height=y0+town.height+39
    # Expand only if atlas content grows; no clipping when adding taller assets.
    if final_height>sheet.height:
        expanded=_image(width,final_height,"#eee4cf")
        expanded.alpha_composite(sheet)
        sheet=expanded
    sheet.alpha_composite(town,((width-town.width)//2,y0+22))
    return sheet.crop((0,0,width,final_height))


# =================================================================================================
# Expansion: richer Bengaluru grounds, autotiles, decals, props and buildings.
# Everything below registers itself into the tables used by ground(), prop() and building().
# =================================================================================================

_WATER_STYLES = {
    "clear": WATER,
    "dark": ("#3f7f9a", "#2b5f78", "#7fb8c8"),
    "murky": ("#86a08c", "#62806f", "#c3d3c0"),
    "lotus": ("#4fa8a2", "#357f82", "#9cdcc8"),
    "deep": ("#4c9fc6", "#2f77a0", "#98d6e2"),
}
_WATER_BANKS = {"grass": (GRASS[0], "#d9c991"), "stone": ("#c9bea8", "#a39784"), "cave": ("#97939d", "#6f6878"),
                "sand": ("#efd89c", "#d4bd86"), "dirt": ("#cba36c", "#a98559")}
_TREE_PALETTES = {
    "tree": ("#64ac59", "#39794e", "#99cc70"),
    "jacaranda": ("#a589d2", "#705caa", "#d3b7ef"),
    "gulmohar": ("#e9784f", "#ae4c44", "#ffb56b"),
    "rain_tree": ("#58996a", "#376b53", "#8dc583"),
    "banyan": ("#70a35e", "#446e4c", "#afd180"),
    "tree_dark": ("#4c8f50", "#2c6142", "#79b062"),
    "tree_olive": ("#89aa52", "#5c7c40", "#b9d277"),
    "mango": ("#3f8b4e", "#235a3d", "#6eb060"),
}
for _name in ("tree_dark", "tree_olive", "mango"):
    _PROP_SIZES[_name] = (2, 2)
    PROP_NAMES.append(_name)

_EXTRA_PROPS = {}
_PROP_PARAMS = {"flower_bed": {"color"}, "car": {"color"}}
DECALS = set()
_FG_MASKS = {"rain_tree": [[True, True, True], [True, False, True], [False, False, False]],
             "banyan": [[True, True, True], [True, False, True], [False, False, False]]}


def _register(name, size, params=(), decal=False, fg=None):
    """Adds a prop renderer: fn(im, d, collision, **params) draws into im and may rewrite collision in place."""
    def deco(fn):
        _PROP_SIZES[name] = size
        if name not in PROP_NAMES:
            PROP_NAMES.append(name)
        _EXTRA_PROPS[name] = fn
        if params:
            _PROP_PARAMS[name] = set(params)
        if decal:
            DECALS.add(name)
        if fg is not None:
            _FG_MASKS[name] = fg
        return fn
    return deco


def _walkable(collision):
    collision[:] = [[False] * len(collision[0]) for _ in collision]


def _only(collision, *cells):
    """Block only the listed (col, row) cells."""
    rows, cols = len(collision), len(collision[0])
    collision[:] = [[(c, r) in cells for c in range(cols)] for r in range(rows)]


def prop_fg_mask(name, grid):
    """Cells drawn over the characters: by default every walkable cell that has a blocked cell below it
    (tree crowns, lamp heads, the top of a pole), so walking behind a tall thing hides you behind it."""
    if name in _FG_MASKS:
        return [list(r) for r in _FG_MASKS[name]]
    rows, cols = len(grid), len(grid[0])
    mask = [[False] * cols for _ in range(rows)]
    for gx in range(cols):
        for gy in range(rows):
            if not grid[gy][gx] and any(grid[k][gx] for k in range(gy + 1, rows)):
                mask[gy][gx] = True
    return mask


def _speckle(d, x, y, colors, count, salt=0, margin=1, size=1):
    for i in range(count):
        n = _seed(x, y, salt + i + 1)
        span = 16 - 2 * margin - (size - 1)
        px, py = margin + n % span, margin + (n >> 8) % span
        d.rectangle((px, py, px + size - 1, py), fill=colors[(n >> 16) % len(colors)])


# ------------------------------------------------------------------------------------------------
# grounds
# ------------------------------------------------------------------------------------------------
_EXTRA_GROUNDS = ["footpath", "grass_dark", "dry_grass", "red_earth", "rock_floor", "gravel", "red_oxide",
                  "checker", "granite_floor", "ghat", "forest_floor", "flagstone", "turf", "pitch", "mosaic",
                  "office_carpet", "canopy", "paddy", "tall_grass_dry"]
GROUND_NAMES.extend(_EXTRA_GROUNDS)


def _ground_extra(name, x, y):
    seed = _seed(x, y)
    if name == "tall_grass_dry":
        im = _image(color="#b9a35c")
        _pixels(im, _BLADES, {"g": "#9a8644", "s": "#7a6a34", "l": "#e2cf86"})
        return im
    if name in ("grass_dark", "dry_grass"):
        base, g, l = (("#6ea85b", "#5a944f", "#86bf6b") if name == "grass_dark" else ("#c9b46c", "#a8964f", "#e2d291"))
        im = _image(color=base)
        _pixels(im, _GRASS, {"g": g, "s": g, "l": l})
        if seed % 3:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT if seed % 3 == 1 else Image.Transpose.FLIP_TOP_BOTTOM)
        if name == "dry_grass" and seed % 4 == 0:
            d = ImageDraw.Draw(im)
            d.line((9, 10, 9, 12), fill="#8f9b52")
            d.line((10, 9, 10, 12), fill="#a7b061")
        return im
    if name == "canopy":
        im = _image(color="#3a7046")
        d = ImageDraw.Draw(im)
        for i in range(5):
            n = _seed(x, y, 40 + i)
            cx, cy = n % 14, (n >> 8) % 14
            d.ellipse((cx - 3, cy - 2, cx + 3, cy + 3), fill="#2c5839")
            d.ellipse((cx - 2, cy - 3, cx + 2, cy + 1), fill="#4b8752")
            d.point((cx - 1, cy - 2), fill="#66a05b")
        return im
    bases = {"footpath": "#bcb6aa", "red_earth": "#b8744e", "rock_floor": "#bab1a4", "gravel": "#a69e92",
             "red_oxide": "#a8463b", "checker": "#e8dfcc", "granite_floor": "#cdc6bb", "ghat": "#cfc2a8",
             "forest_floor": "#8a7a50", "flagstone": "#8d8474", "turf": "#7fc262", "pitch": "#d6bd88",
             "mosaic": "#e2dac8", "office_carpet": "#7c8695", "paddy": "#6c9c76"}
    im = _image(color=bases[name])
    d = ImageDraw.Draw(im)
    if name == "footpath":
        if seed % 5 == 0:
            d.rectangle((0, 0, 14, 14), fill="#b4aea2")
        _speckle(d, x, y, ["#a9a397", "#c9c3b7", "#b0aa9e"], 7)
        d.line((15, 0, 15, 15), fill="#8e897f")
        d.line((0, 15, 15, 15), fill="#8e897f")
        d.line((0, 0, 14, 0), fill="#d4cfc4")
        d.line((0, 0, 0, 14), fill="#d0cbbf")
        if seed % 11 == 0:
            d.line([(3, 3), (6, 6), (5, 9), (8, 12)], fill="#8e897f")
        if seed % 13 == 3:
            d.ellipse((5, 6, 10, 10), fill="#aaa396")
    elif name == "red_earth":
        _speckle(d, x, y, ["#a3613f", "#c98a62", "#ad6845", "#cf9168"], 12)
        if seed % 4 == 0:
            px, py = 3 + seed % 9, 3 + (seed >> 5) % 9
            d.rectangle((px, py, px + 1, py), fill="#e3c5a2")
            d.line((px, py + 1, px + 1, py + 1), fill="#8f5236")
    elif name == "rock_floor":
        _speckle(d, x, y, ["#d3c7ba", "#a0978c", "#c6bcaf", "#7d766e"], 14)
        if seed % 6 == 0:
            d.line([(2, 9), (5, 8), (8, 9), (12, 7)], fill="#968d82")
            d.line([(3, 10), (6, 9)], fill="#d6ccbf")
        if seed % 9 == 4:
            d.ellipse((9, 3, 12, 5), fill="#a4ad7d")
    elif name == "gravel":
        for i in range(9):
            n = _seed(x, y, 60 + i)
            px, py = 1 + n % 13, 1 + (n >> 8) % 14
            d.line((px, py, px + 1, py), fill=("#bab2a5", "#b3aa9c", "#c4bcb0")[(n >> 12) % 3])
            d.point((px, py + 1), fill="#948c81")
    elif name == "red_oxide":
        d.line((0, 0, 15, 0), fill="#8b3730")
        d.line((0, 0, 0, 15), fill="#8b3730")
        d.line((3, 12, 9, 6), fill="#b9584c")
        d.line((5, 13, 11, 7), fill="#b0503f")
        _speckle(d, x, y, ["#9b4036", "#b3524a"], 4)
    elif name == "checker":
        for qy in (0, 8):
            for qx in (0, 8):
                dark = ((qx + qy) // 8) % 2 == 0
                d.rectangle((qx, qy, qx + 7, qy + 7), fill="#3d3946" if dark else "#e8dfcc")
                d.line((qx, qy, qx + 6, qy), fill="#4c4757" if dark else "#f6efe0")
    elif name == "granite_floor":
        _speckle(d, x, y, ["#b1aa9f", "#e4ded3", "#8d877f", "#bdb6ab"], 14)
        d.line((15, 0, 15, 15), fill="#a59e94")
        d.line((0, 15, 15, 15), fill="#a59e94")
        d.line((0, 0, 14, 0), fill="#dcd6cc")
    elif name == "ghat":
        for py in range(0, 16, 4):
            d.line((0, py, 15, py), fill="#e2d7bf")
            d.line((0, py + 3, 15, py + 3), fill="#958770")
        _speckle(d, x, y, ["#bdb095", "#c6b99f"], 5)
        if seed % 7 == 0:
            d.line((3, 2, 3, 2), fill="#8fa070")
    elif name == "forest_floor":
        for i in range(9):
            n = _seed(x, y, 20 + i)
            px, py = 1 + n % 13, 1 + (n >> 8) % 13
            c = ("#a48a4c", "#6b5d3a", "#b77a3e", "#61733d", "#c09a55", "#7d6a40")[(n >> 14) % 6]
            d.line((px, py, px + 1, py), fill=c)
            if (n >> 20) % 2:
                d.point((px + 1, py + 1), fill=_shade(c, -25))
        if seed % 3 == 0:
            d.line((11, 4, 11, 6), fill="#5f8c48")
            d.line((12, 5, 12, 6), fill="#78a654")
    elif name == "flagstone":
        sy = 6 + seed % 4
        sx1 = 5 + (seed >> 4) % 6
        sx2 = 4 + (seed >> 8) % 8
        stones = [(0, 0, sx1 - 1, sy - 1), (sx1, 0, 14, sy - 1), (0, sy, sx2 - 1, 14), (sx2, sy, 14, 14)]
        fills = ("#c9bea8", "#bfb49d", "#d2c8b3", "#c4b8a0")
        for i, (a, b, c, e) in enumerate(stones):
            if c - a < 1 or e - b < 1:
                continue
            col = fills[(seed >> (i * 3)) % 4]
            d.rectangle((a, b, c, e), fill=col)
            d.line((a, b, c, b), fill=_shade(col, 18))
            d.point((c, e), fill=_shade(col, -20))
    elif name == "turf":
        if (x // 2) % 2:
            d.rectangle((0, 0, 15, 15), fill="#71b257")
        _speckle(d, x, y, ["#5e9e4c", "#9bd47a"], 6)
    elif name == "pitch":
        _speckle(d, x, y, ["#c4a874", "#e6d3a5", "#cbb07c"], 10)
        if seed % 5 == 0:
            d.line([(4, 5), (6, 7), (6, 10)], fill="#b59a68")
    elif name == "mosaic":
        _speckle(d, x, y, ["#b7a189", "#8b8e96", "#c98370", "#7f9e8c", "#d0c3a9", "#a7a4a0"], 18)
        d.line((15, 0, 15, 15), fill="#cfc6b2")
        d.line((0, 15, 15, 15), fill="#cfc6b2")
    elif name == "office_carpet":
        for qy in (0, 8):
            for qx in (0, 8):
                horiz = ((qx + qy) // 8) % 2 == 0
                d.rectangle((qx, qy, qx + 7, qy + 7), fill="#76808f" if horiz else "#838d9c")
                for k in range(1, 8, 2):
                    if horiz:
                        d.line((qx + 1, qy + k, qx + 6, qy + k), fill="#717b89")
                    else:
                        d.line((qx + k, qy + 1, qx + k, qy + 6), fill="#8b95a3")
    elif name == "paddy":
        for px in (1, 5, 9, 13):
            d.line((px + 1, 0, px + 1, 15), fill="#86b8b0")
            for py in range(1, 16, 4):
                d.line((px, py, px, py + 2), fill="#5f9a48")
                d.line((px + 2, py + 1, px + 2, py + 2), fill="#8cc35f")
                d.point((px + 1, py), fill="#a7d76c")
    return im


# ------------------------------------------------------------------------------------------------
# blocked autotiles: granite masses, cave walls, grassy ledges, fort walls
# ------------------------------------------------------------------------------------------------
_SOLID_PALETTES = {
    # base, mid, dark, light, edge, accent
    "granite": ("#b6ab9d", "#a0958a", "#7f756b", "#d6cdbf", "#584f49", "#8d9662"),
    "cave_wall": ("#7a7287", "#6a6378", "#504a5e", "#9e96aa", "#2f2a3b", "#5f7c70"),
}


def _outline_alpha(im, edge):
    """Every opaque pixel touching a transparent one becomes the edge colour."""
    px = im.load()
    w, h = im.size
    edge = _color(edge)
    marks = []
    for yy in range(h):
        for xx in range(w):
            if px[xx, yy][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = xx + dx, yy + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                    marks.append((xx, yy))
                    break
    for p in marks:
        px[p] = edge


def _round_corners(im, n, s, w, e, radius=5):
    px = im.load()
    for corner, open_ in (((0, 0), not n and not w), ((15, 0), not n and not e),
                          ((0, 15), not s and not w), ((15, 15), not s and not e)):
        if not open_:
            continue
        cx = radius if corner[0] == 0 else 15 - radius
        cy = radius if corner[1] == 0 else 15 - radius
        for yy in range(16):
            for xx in range(16):
                in_corner = (xx < cx if corner[0] == 0 else xx > cx) and (yy < cy if corner[1] == 0 else yy > cy)
                if in_corner and (xx - cx) ** 2 + (yy - cy) ** 2 > radius * radius:
                    px[xx, yy] = (0, 0, 0, 0)


def solid(kind, x, y, n=False, s=False, w=False, e=False, nw=False, ne=False, sw=False, se=False,
          inner=(), deep=False):
    """A 16 px blocked autotile. Flags say whether that neighbour is the same material. Transparent pixels
    (rounded corners, gaps between merlons) let the ground drawn underneath show through.
    inner: sides ("n","s","e","w") that border a walkable top of the same rock (a soft lip, no outline);
    deep: the tile below is rock but open beneath it, so this tile is the upper half of a tall cliff face."""
    seed = _seed(x, y, 7)
    if kind in _SOLID_PALETTES:
        base, mid, dark, light, edge, accent = _SOLID_PALETTES[kind]
        im = _image(color=base)
        d = ImageDraw.Draw(im)
        _speckle(d, x, y, [mid, mid, dark, light], 16, salt=11, margin=0)
        if seed % 5 == 0:
            d.ellipse((3, 4, 6, 6), fill=accent)
            d.point((4, 4), fill=_shade(accent, 25))
        if seed % 4 == 1:
            # exfoliation crack: granite peels in curved sheets
            d.arc((2 + seed % 5, 3, 13, 14), 200, 300, fill=dark)
        if not n:
            d.line((0, 0, 15, 0), fill=edge)
            d.rectangle((0, 1, 15, 3), fill=light)
            d.line((0, 4, 15, 4), fill=_shade(light, -12))
            _speckle(d, x, y, [base, _shade(light, 12)], 4, salt=19, margin=1)
        elif n and not nw and not ne:
            pass
        if not w:
            d.line((1, 0, 1, 15), fill=light)
        if not e:
            d.line((13, 0, 13, 15), fill=mid)
            d.line((14, 0, 14, 15), fill=dark)
        if deep:
            # upper half of a tall cliff face: vertical strata and cracks, lighter than the foot
            for yy in range(3 if not n else 0, 16):
                for xx in range(16):
                    v = (xx * 5 + x * 3 + (yy // 5)) % 7
                    d.point((xx, yy), fill=mid if v < 3 else base if v < 6 else dark)
            for k in range(2):
                cx = 2 + (seed >> (k * 4)) % 12
                d.line((cx, 2, cx + (k * 2 - 1), 15), fill=dark)
        if not s:
            for yy in range(0 if (deep or (n and "n" not in inner)) else 8, 16):
                for xx in range(16):
                    shade = dark if (yy + xx // 3 + (x % 2)) % 4 == 0 else mid if yy < 11 else dark
                    d.point((xx, yy), fill=shade)
            if not deep and not (n and "n" not in inner):
                d.line((0, 8, 15, 8), fill=light if kind == "granite" else mid)
                d.line((0, 9, 15, 9), fill=base)
            if kind == "cave_wall":
                for xx in (3, 9, 13):
                    if (seed >> xx) % 2:
                        d.polygon(((xx - 1, 15), (xx + 1, 15), (xx, 12)), fill=light)
        _round_corners(im, n, s, w, e)
        _outline_alpha(im, edge)
        if not w:
            d.line((0, 0, 0, 15), fill=edge)
        if not e:
            d.line((15, 0, 15, 15), fill=edge)
        if not s:
            d.line((0, 15, 15, 15), fill=edge)
        _round_corners(im, n, s, w, e)
        _outline_alpha(im, edge)
        if "s" in inner:
            d.line((0, 14, 15, 14), fill=mid)
            d.line((0, 15, 15, 15), fill=dark)
        if "n" in inner:
            d.line((0, 0, 15, 0), fill=light)
            d.line((0, 1, 15, 1), fill=_shade(light, -10))
        if "w" in inner:
            d.line((0, 0, 0, 15), fill=mid)
        if "e" in inner:
            d.line((15, 0, 15, 15), fill=mid)
        return im
    if kind == "ledge":
        im = ground("grass", x, y)
        d = ImageDraw.Draw(im)
        if not n:
            d.line((0, 0, 15, 0), fill=GRASS[2])
        if not s:
            d.line((0, 10, 15, 10), fill=GRASS[3])
            d.rectangle((0, 11, 15, 14), fill="#a87e55")
            for xx in range(1, 16, 3):
                d.line((xx, 12, xx, 14), fill="#8c6646")
            d.line((0, 11, 15, 11), fill="#c19669")
            d.line((0, 15, 15, 15), fill="#6e5038")
        if not w:
            d.line((0, 0, 0, 10 if not s else 15), fill=GRASS[3])
        if not e:
            d.line((15, 0, 15, 10 if not s else 15), fill=GRASS[3])
        if not s:
            px = im.load()
            for corner_open, xs in ((not w, (0, 1)), (not e, (15, 14))):
                if corner_open:
                    for yy in range(12, 16):
                        px[xs[0], yy] = (0, 0, 0, 0)
                    px[xs[1], 15] = (0, 0, 0, 0)
        return im
    if kind == "fort_wall":
        base, joint, hi = "#a99f8e", "#6f665b", "#c8beab"
        im = _image(color=base)
        d = ImageDraw.Draw(im)
        for row, yy in enumerate(range(0, 16, 4)):
            off = 4 if (row + y * 4) % 2 else 0
            for xx in range(-off, 16, 8):
                n2 = _seed(x * 4 + xx, y * 4 + row, 3)
                fill = ("#a99f8e", "#9e9483", "#b3a998", "#a49a89")[n2 % 4]
                d.rectangle((xx, yy, xx + 7, yy + 3), fill=fill)
                d.line((xx, yy, xx + 6, yy), fill=hi)
                d.line((xx + 7, yy, xx + 7, yy + 3), fill=joint)
                d.line((xx, yy + 3, xx + 7, yy + 3), fill=joint)
        px = im.load()
        if not n:
            for xx in range(16):
                if (xx + x * 16) % 8 >= 5:
                    for yy in range(0, 4):
                        px[xx, yy] = (0, 0, 0, 0)
            d.line((0, 5, 15, 5), fill="#857b6d")
        if not s:
            d.rectangle((0, 13, 15, 15), fill="#8a8072")
            d.line((0, 13, 15, 13), fill=hi)
        if not w:
            d.line((1, 0, 1, 15), fill=hi)
        if not e:
            d.line((14, 0, 14, 15), fill="#857b6d")
        _outline_alpha(im, OUTLINE)
        if not w:
            d.line((0, 0, 0, 15), fill=OUTLINE)
        if not e:
            d.line((15, 0, 15, 15), fill=OUTLINE)
        if not s:
            d.line((0, 15, 15, 15), fill=OUTLINE)
        if not n:
            for xx in range(16):
                if px[xx, 4][3] and px[xx, 0][3] == 0:
                    px[xx, 4] = _color(OUTLINE)
        return im
    raise ValueError(f"Unknown solid {kind!r}")


def water_overlay(kind, x, y):
    """Transparent overlays for water tiles: drifting foam, or stepping stones you can walk on."""
    im = _image()
    d = ImageDraw.Draw(im)
    seed = _seed(x, y, 5)
    if kind == "foam":
        for i in range(3):
            n = _seed(x, y, 30 + i)
            cx, cy = 3 + n % 10, 3 + (n >> 8) % 10
            r = 2 + (n >> 16) % 3
            d.ellipse((cx - r, cy - r + 1, cx + r, cy + r), fill="#c8cfc6")
            d.ellipse((cx - r, cy - r, cx + r, cy + r - 1), fill="#f2f0e6")
            d.point((cx - 1, cy - r + 1), fill="#ffffff")
            d.point((cx + r - 1, cy), fill="#d6dad2")
    elif kind == "stones":
        for cx, cy in ((4 + seed % 2, 5), (11 - seed % 2, 11)):
            d.ellipse((cx - 4, cy - 2, cx + 4, cy + 3), fill="#5f6a72")
            d.ellipse((cx - 4, cy - 3, cx + 4, cy + 2), fill="#a7a299", outline=OUTLINE)
            d.line((cx - 2, cy - 2, cx + 1, cy - 2), fill="#d2cdc2")
    return im


# ------------------------------------------------------------------------------------------------
# decals: walkable marks drawn on the ground under everything else
# ------------------------------------------------------------------------------------------------
@_register("puddle", (1, 1), decal=True)
def _puddle(im, d, collision):
    _walkable(collision)
    d.ellipse((1, 5, 14, 13), fill="#6f8f9e")
    d.ellipse((2, 5, 13, 11), fill="#8fb4c2")
    d.line((4, 7, 8, 7), fill="#d7eef0")
    d.point((10, 9), fill="#d7eef0")


@_register("pothole", (1, 1), decal=True)
def _pothole(im, d, collision):
    _walkable(collision)
    d.polygon(((2, 7), (5, 4), (11, 4), (14, 8), (12, 12), (4, 12)), fill="#4d535c")
    d.polygon(((4, 7), (6, 6), (11, 6), (12, 9), (10, 10), (5, 10)), fill="#7c97a3")
    d.line((6, 7, 9, 7), fill="#b9d6dc")
    for px, py in ((1, 9), (14, 5), (13, 12)):
        d.point((px, py), fill="#555c66")


@_register("manhole", (1, 1), decal=True)
def _manhole(im, d, collision):
    _walkable(collision)
    d.ellipse((2, 3, 13, 13), fill="#595f68", outline="#454a52")
    for yy in (6, 8, 10):
        d.line((5, yy, 10, yy), fill="#6f767f")


@_register("rangoli", (1, 1), params=("color",), decal=True)
def _rangoli(im, d, collision, color="#e0607a"):
    _walkable(collision)
    c = _color(color)
    d.polygon(((8, 1), (15, 8), (8, 15), (1, 8)), outline="#fff6e4")
    d.polygon(((8, 4), (12, 8), (8, 12), (4, 8)), fill=c)
    d.polygon(((8, 6), (10, 8), (8, 10), (6, 8)), fill="#f4c24f")
    for px, py in ((8, 2), (14, 8), (8, 14), (2, 8), (4, 4), (12, 4), (4, 12), (12, 12)):
        d.point((px, py), fill="#fff6e4")
    d.point((8, 8), fill="#fff6e4")


@_register("rangoli_big", (2, 2), decal=True)
def _rangoli_big(im, d, collision):
    _walkable(collision)
    d.ellipse((1, 1, 30, 30), outline="#fff6e4")
    for i, c in enumerate(("#e0607a", "#f4c24f", "#7fb8e0", "#8fcf7a")):
        a = i * 90
        import math
        cx = 16 + round(8 * math.cos(math.radians(a + 45)))
        cy = 16 + round(8 * math.sin(math.radians(a + 45)))
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=c, outline="#fff6e4")
    d.ellipse((11, 11, 21, 21), fill="#d9534f", outline="#fff6e4")
    d.ellipse((14, 14, 18, 18), fill="#f4c24f")
    for k in range(0, 360, 30):
        import math
        d.point((16 + round(14 * math.cos(math.radians(k))), 16 + round(14 * math.sin(math.radians(k)))), fill="#fff6e4")


@_register("oil_stain", (1, 1), decal=True)
def _oil_stain(im, d, collision):
    _walkable(collision)
    d.ellipse((3, 6, 12, 11), fill=(56, 58, 66, 120))
    d.ellipse((7, 4, 11, 8), fill=(56, 58, 66, 90))


@_register("crack", (1, 1), decal=True)
def _crack(im, d, collision):
    _walkable(collision)
    d.line([(1, 4), (5, 6), (7, 10), (11, 11), (15, 14)], fill=(60, 56, 60, 150))
    d.line([(7, 10), (6, 14)], fill=(60, 56, 60, 120))


@_register("leaves", (1, 1), decal=True)
def _leaves(im, d, collision):
    _walkable(collision)
    for px, py, c in ((3, 3, "#b98a3e"), (10, 5, "#8f9a46"), (6, 10, "#c6763c"), (12, 12, "#a7843f"), (2, 13, "#8f9a46")):
        d.line((px, py, px + 2, py), fill=c)
        d.point((px + 1, py + 1), fill=_shade(c, -30))


@_register("petals", (1, 1), decal=True)
def _petals(im, d, collision):
    _walkable(collision)
    for px, py in ((2, 3), (9, 2), (13, 7), (5, 8), (10, 12), (3, 13), (7, 5), (14, 13)):
        d.point((px, py), fill="#b79be0")
        d.point((px + 1, py), fill="#8f76c4")


@_register("petals_red", (1, 1), decal=True)
def _petals_red(im, d, collision):
    _walkable(collision)
    for px, py in ((3, 2), (10, 4), (13, 9), (6, 7), (9, 12), (2, 12), (12, 14)):
        d.point((px, py), fill="#f08a5d")
        d.point((px + 1, py), fill="#c9503f")


@_register("pebbles", (1, 1), decal=True)
def _pebbles(im, d, collision):
    _walkable(collision)
    for px, py in ((3, 4), (9, 3), (12, 9), (5, 11), (8, 8)):
        d.ellipse((px, py, px + 2, py + 1), fill="#b7b0a6")
        d.line((px, py + 2, px + 2, py + 2), fill=(80, 70, 70, 120))


@_register("grass_tuft", (1, 1), decal=True)
def _grass_tuft(im, d, collision):
    _walkable(collision)
    for px in (5, 9):
        d.line((px, 9, px - 1, 6), fill=GRASS[1])
        d.line((px + 1, 9, px + 1, 5), fill=GRASS[2])
        d.line((px + 2, 9, px + 3, 6), fill=GRASS[1])
        d.line((px - 1, 10, px + 3, 10), fill=(70, 90, 60, 110))


@_register("wildflowers", (1, 1), decal=True)
def _wildflowers(im, d, collision):
    _walkable(collision)
    for px, py, c in ((3, 4, "#f4d481"), (11, 3, "#fff0cf"), (7, 9, "#efa3ac"), (13, 11, "#f4d481"), (3, 12, "#a38acb")):
        d.line((px, py + 1, px, py + 3), fill=GRASS[3])
        d.point((px, py), fill=c)
        d.point((px - 1, py), fill=c)
        d.point((px + 1, py), fill=c)


@_register("mushrooms", (1, 1), decal=True)
def _mushrooms(im, d, collision):
    _walkable(collision)
    for px, py in ((4, 8), (10, 11), (8, 5)):
        d.line((px, py + 1, px, py + 3), fill=CREAM)
        d.ellipse((px - 2, py - 1, px + 2, py + 1), fill="#c9604d", outline=OUTLINE)
        d.point((px - 1, py - 1), fill=CREAM)


@_register("rubble", (1, 1), decal=True)
def _rubble(im, d, collision):
    _walkable(collision)
    for px, py, s in ((2, 4, 3), (9, 3, 2), (6, 9, 3), (12, 10, 2), (3, 12, 2)):
        d.polygon(((px, py + s), (px + 1, py), (px + s + 1, py), (px + s + 1, py + s)), fill="#a79d8f", outline="#6f675e")


@_register("slippers", (1, 1), decal=True)
def _slippers(im, d, collision):
    _walkable(collision)
    for px, c in ((4, "#3d6ea8"), (9, "#c45b4f")):
        d.rounded_rectangle((px, 6, px + 2, 12), radius=1, fill=c, outline=OUTLINE)
        d.line((px, 8, px + 2, 8), fill=CREAM)


@_register("deck_shadow", (1, 1), decal=True)
def _deck_shadow(im, d, collision):
    _walkable(collision)
    d.rectangle((0, 0, 15, 15), fill=(30, 26, 48, 70))


@_register("road_arrow", (1, 1), decal=True)
def _road_arrow(im, d, collision):
    _walkable(collision)
    d.rectangle((3, 7, 10, 8), fill="#eee7d5")
    d.polygon(((10, 4), (14, 8), (10, 11)), fill="#eee7d5")


@_register("ducks", (1, 1), decal=True)
def _ducks(im, d, collision):
    _walkable(collision)
    for px, py in ((3, 5), (10, 10)):
        d.line((px - 1, py + 3, px + 5, py + 3), fill=WATER[2])
        d.ellipse((px, py, px + 5, py + 3), fill="#f1e7ce", outline=OUTLINE)
        d.ellipse((px + 3, py - 3, px + 6, py), fill="#f1e7ce", outline=OUTLINE)
        d.point((px + 7, py - 2), fill="#e9a944")
        d.point((px + 5, py - 2), fill=OUTLINE)


@_register("lotus", (1, 1), decal=True)
def _lotus(im, d, collision):
    _walkable(collision)
    for px, py, r in ((2, 3, 4), (9, 8, 5)):
        d.pieslice((px, py, px + r * 2, py + r * 2 - 2), 20, 340, fill="#5f9c5a", outline="#3f6f45")
    d.polygon(((4, 9), (6, 5), (8, 9)), fill="#f2a6c0", outline="#b85c84")
    d.point((6, 7), fill="#ffe0ea")


@_register("lily_pads", (1, 1), decal=True)
def _lily_pads(im, d, collision):
    _walkable(collision)
    for px, py, r in ((1, 2, 3), (8, 4, 4), (4, 10, 3), (11, 11, 3)):
        d.pieslice((px, py, px + r * 2, py + r * 2 - 1), 30, 330, fill="#6aa65e", outline="#3f6f45")


@_register("foam_bank", (1, 1), decal=True)
def _foam_bank(im, d, collision):
    _walkable(collision)
    for cx, cy, r in ((4, 10, 3), (9, 12, 3), (12, 8, 2), (6, 6, 2)):
        d.ellipse((cx - r, cy - r + 1, cx + r, cy + r), fill="#c8cfc6")
        d.ellipse((cx - r, cy - r, cx + r, cy + r - 1), fill="#f2f0e6")


@_register("hopscotch", (1, 2), decal=True)
def _hopscotch(im, d, collision):
    _walkable(collision)
    c = (250, 246, 236, 200)
    for yy in (2, 9, 16, 23):
        d.rectangle((4, yy, 11, yy + 6), outline=c)
    d.line((8, 9, 8, 15), fill=c)


@_register("mist", (3, 2), decal=False, fg=[[True] * 3, [True] * 3])
def _mist(im, d, collision):
    _walkable(collision)
    for cx, cy, rx, ry, a in ((14, 14, 13, 6, 70), (30, 20, 14, 7, 60), (22, 9, 10, 4, 80)):
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(246, 244, 252, a))


# ------------------------------------------------------------------------------------------------
# street furniture, vehicles and stalls
# ------------------------------------------------------------------------------------------------
_EXTRA_BUILDINGS = {}
_SIZED_BUILDINGS = {}
_BUILDING_PARAMS = {}


@_register("electric_pole", (1, 2))
def _electric_pole(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (6, 2, 9, 30), "#aeaca5")
    d.line((7, 3, 7, 29), fill="#d2d0c8")
    d.line((9, 3, 9, 29), fill="#86847e")
    # cross arms, insulators and a little bracket for the third wire
    d.rectangle((1, 4, 14, 5), fill="#5d6470", outline=OUTLINE)
    for xx in (3, 12):
        d.rectangle((xx - 1, 2, xx, 3), fill=CREAM, outline=OUTLINE)
    d.rectangle((5, 7, 10, 7), fill="#5d6470")
    d.point((7, 6), fill=CREAM)
    # tuition and paying-guest posters pasted on the pole
    d.rectangle((5, 16, 10, 20), fill="#f2e7c9", outline="#b9ad92")
    d.line((6, 17, 9, 17), fill="#c05a4c")
    d.line((6, 19, 8, 19), fill="#7c7768")
    d.rectangle((6, 22, 9, 24), fill="#f0b2bd")
    d.ellipse((4, 29, 11, 31), fill="#8e8b84", outline=OUTLINE)


@_register("transformer_pole", (1, 2))
def _transformer_pole(im, d, collision):
    _electric_pole(im, d, collision)
    _panel(d, (2, 9, 13, 17), "#8f9a96")
    for xx in (4, 7, 10):
        d.line((xx, 10, xx, 16), fill="#6c7774")
    d.rectangle((3, 8, 5, 9), fill=CREAM, outline=OUTLINE)
    d.rectangle((10, 8, 12, 9), fill=CREAM, outline=OUTLINE)
    d.rectangle((5, 12, 10, 14), fill="#e9b945")
    d.point((7, 13), fill=OUTLINE)


@_register("street_lamp", (1, 2))
def _street_lamp(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (5, 8, 7, 29), "#6f8a82")
    d.line((5, 9, 5, 28), fill="#94b0a6")
    d.line([(6, 8), (6, 5), (8, 3), (11, 2)], fill=OUTLINE, width=2)
    d.line([(6, 7), (6, 5), (8, 3)], fill="#94b0a6")
    d.polygon(((9, 1), (15, 1), (14, 4), (10, 4)), fill="#56605e", outline=OUTLINE)
    d.line((11, 5, 14, 5), fill="#ffd27a")
    d.point((12, 6), fill="#ffe9a8")
    _panel(d, (3, 28, 9, 31), STONE[1])


@_register("traffic_light", (1, 2))
def _traffic_light(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (7, 12, 9, 30), "#56606a")
    _panel(d, (3, 1, 12, 14), "#363944")
    for yy, lit, dim in ((3, "#ff6b5c", "#6b3634"), (7, "#7a6338", "#7a6338"), (11, "#3b6b4c", "#3b6b4c")):
        d.ellipse((5, yy - 1, 10, yy + 2), fill=lit, outline=OUTLINE)
        d.line((5, yy - 2, 10, yy - 2), fill=OUTLINE)
    d.point((6, 2), fill="#ffd0c8")
    _panel(d, (5, 28, 11, 31), STONE[1])


@_register("bus_side", (4, 2), params=("color",))
def _bus_side(im, d, collision, color="#4d7fc0"):
    c = _color(color)
    d.rounded_rectangle((1, 3, 62, 27), radius=3, fill=c, outline=OUTLINE)
    d.line((3, 4, 58, 4), fill=_shade(c, 40))
    d.rectangle((2, 17, 61, 19), fill=CREAM)
    d.rectangle((2, 20, 61, 26), fill=_shade(c, -30))
    for xx in range(4, 50, 8):
        d.rectangle((xx, 7, xx + 6, 14), fill="#9fd0dc", outline=OUTLINE)
        d.line((xx + 1, 8, xx + 3, 8), fill="#dff3f0")
        if (xx // 8) % 3 == 1:
            d.ellipse((xx + 2, 10, xx + 4, 13), fill="#6b4f45")
    d.polygon(((52, 6), (60, 6), (61, 17), (52, 17)), fill="#8fc3d2", outline=OUTLINE)
    d.line((54, 8, 58, 8), fill="#dff3f0")
    d.rectangle((44, 18, 50, 26), fill=_shade(c, -45), outline=OUTLINE)
    d.line((47, 19, 47, 25), fill=_shade(c, -10))
    d.rectangle((38, 0, 58, 5), fill="#2f2b36", outline=OUTLINE)
    im.alpha_composite(text("500D", _color("#ffb347")), (41, 1))
    for xx in (8, 44):
        d.ellipse((xx, 21, xx + 10, 31), fill="#2f2b36", outline=OUTLINE)
        d.ellipse((xx + 3, 24, xx + 7, 28), fill="#9aa0a6")
    d.point((61, 22), fill="#fff0a0")
    d.point((2, 22), fill="#d9534f")


@_register("car_side", (2, 1), params=("color",))
def _car_side(im, d, collision, color="#e88779"):
    c = _color(color)
    d.polygon(((8, 2), (21, 2), (25, 7), (30, 8), (30, 12), (1, 12), (1, 8), (5, 7)), fill=c, outline=OUTLINE)
    d.polygon(((9, 3), (14, 3), (14, 7), (6, 7)), fill="#9fd0dc")
    d.polygon(((16, 3), (20, 3), (23, 7), (16, 7)), fill="#9fd0dc")
    d.line((3, 8, 27, 8), fill=_shade(c, 35))
    d.line((2, 11, 29, 11), fill=_shade(c, -30))
    for xx in (4, 20):
        d.ellipse((xx, 9, xx + 6, 15), fill="#2f2b36", outline=OUTLINE)
        d.point((xx + 3, 12), fill="#9aa0a6")
    d.point((29, 9), fill="#fff0a0")
    d.point((1, 9), fill="#d9534f")


@_register("auto_side", (2, 1))
def _auto_side(im, d, collision):
    # Bengaluru auto: black canvas hood, yellow and green body, one wheel up front
    d.polygon(((4, 7), (5, 2), (8, 0), (21, 0), (24, 3), (24, 7)), fill="#33313a", outline=OUTLINE)
    d.line((8, 1, 20, 1), fill="#55525e")
    d.polygon(((3, 7), (27, 7), (30, 9), (30, 12), (2, 12)), fill="#e9b945", outline=OUTLINE)
    d.rectangle((3, 10, 22, 12), fill="#4f9a55")
    d.rectangle((8, 3, 19, 8), fill="#3b3440")
    d.rectangle((10, 6, 17, 8), fill="#bb986c")
    d.line((24, 3, 28, 8), fill=OUTLINE)
    d.line((25, 4, 27, 7), fill="#9fd0dc")
    d.ellipse((24, 10, 29, 15), fill="#2f2b36", outline=OUTLINE)
    d.ellipse((3, 10, 9, 15), fill="#2f2b36", outline=OUTLINE)
    d.point((26, 12), fill="#9aa0a6")
    d.point((6, 12), fill="#9aa0a6")
    d.point((30, 10), fill="#fff0a0")


@_register("scooter_side", (1, 1), params=("color",))
def _scooter_side(im, d, collision, color="#d9534f"):
    c = _color(color)
    d.polygon(((2, 9), (4, 6), (10, 6), (12, 3), (13, 3), (13, 11), (2, 11)), fill=c, outline=OUTLINE)
    d.rectangle((3, 5, 8, 6), fill="#33313a", outline=OUTLINE)
    d.line((12, 2, 14, 2), fill=OUTLINE)
    d.point((14, 5), fill="#fff0a0")
    d.line((4, 8, 9, 8), fill=_shade(c, 35))
    for xx in (1, 10):
        d.ellipse((xx, 10, xx + 4, 14), fill="#2f2b36", outline=OUTLINE)
        d.point((xx + 2, 12), fill="#9aa0a6")


@_register("jeep_side", (2, 1))
def _jeep_side(im, d, collision):
    d.rectangle((3, 1, 21, 7), fill="#56724a", outline=OUTLINE)
    d.rectangle((5, 2, 10, 6), fill="#9fd0dc")
    d.rectangle((13, 2, 19, 6), fill="#9fd0dc")
    d.polygon(((1, 7), (29, 7), (30, 9), (30, 12), (1, 12)), fill="#6b8a52", outline=OUTLINE)
    d.line((2, 8, 28, 8), fill="#8fae6e")
    d.rectangle((23, 3, 28, 7), fill="#6b8a52", outline=OUTLINE)
    d.ellipse((0, 4, 4, 9), fill="#2f2b36", outline=OUTLINE)
    for xx in (4, 21):
        d.ellipse((xx, 9, xx + 6, 15), fill="#2f2b36", outline=OUTLINE)
        d.point((xx + 3, 12), fill="#9aa0a6")
    im.alpha_composite(text("FD", _color(CREAM)), (12, 8))


@_register("bunk_shop", (2, 2))
def _bunk_shop(im, d, collision):
    blue = "#4f86b0"
    _panel(d, (2, 8, 29, 30), blue)
    _panel(d, (0, 1, 31, 9), "#e9b945")
    _label(im, "STORES", (2, 3, 29, 7), OUTLINE)
    d.rectangle((4, 9, 27, 19), fill="#3b3440")
    d.line((5, 15, 26, 15), fill="#7a6a58")
    # strings of crisp packets and a bunch of bananas
    for i, xx in enumerate(range(5, 20, 3)):
        c = ("#e9b945", "#d9534f", "#4fa3d9", "#7fbf5f", "#f08a5d")[i % 5]
        d.rectangle((xx, 9, xx + 1, 13), fill=c)
        d.point((xx, 13), fill=_shade(c, -40))
    d.arc((20, 9, 26, 15), 0, 180, fill="#f4d23c", width=2)
    d.point((23, 10), fill="#6b5a2e")
    for xx in (7, 12, 17):
        d.rectangle((xx, 16, xx + 3, 19), fill="#cfe3e6", outline=OUTLINE)
        d.rectangle((xx + 1, 17, xx + 2, 18), fill=("#e05c6a", "#f4c24f", "#6fbf73")[(xx // 5) % 3])
    _panel(d, (1, 19, 30, 22), WOOD[0])
    d.rectangle((4, 24, 27, 28), fill=_shade(blue, -25))
    d.line((5, 26, 26, 26), fill=_shade(blue, 20))
    d.rectangle((3, 30, 7, 31), fill="#8e5b4a")
    d.rectangle((24, 30, 28, 31), fill="#8e5b4a")


@_register("tea_stall", (2, 2))
def _tea_stall(im, d, collision):
    # blue tarpaulin roof, a steaming kettle, glasses of chai lined up
    d.polygon(((0, 7), (3, 1), (28, 1), (31, 7)), fill="#3f6fb0", outline=OUTLINE)
    for xx in range(5, 28, 6):
        d.line((xx, 2, xx - 1, 6), fill="#5d8dd0")
    _panel(d, (2, 8, 29, 30), "#c99b62")
    d.rectangle((4, 9, 27, 17), fill="#4a3a33")
    _label(im, "TEA", (6, 10, 17, 15), CREAM)
    _vessel(d, 19, 9, 8, True)
    _panel(d, (1, 17, 30, 20), STEEL[0])
    for xx in range(4, 18, 3):
        d.rectangle((xx, 14, xx + 1, 17), fill="#f3e3c2", outline="#9b8a72")
        d.point((xx, 15), fill="#c68a4c")
    for yy in (22, 26):
        d.line((3, yy, 28, yy), fill=WOOD[1])
    d.rectangle((5, 21, 11, 29), fill="#e7d7b8", outline=OUTLINE)
    d.rectangle((6, 23, 10, 27), fill="#d9a35c")
    d.line((6, 22, 10, 22), fill=CREAM)


@_register("coconut_cart", (2, 1))
def _coconut_cart(im, d, collision):
    _panel(d, (1, 7, 30, 11), WOOD[1])
    for cx, cy in ((5, 5), (10, 4), (15, 5), (20, 4), (25, 5), (8, 1), (13, 1), (18, 1), (23, 2)):
        d.ellipse((cx - 3, cy - 1, cx + 2, cy + 3), fill="#6aa04a", outline=OUTLINE)
        d.point((cx - 1, cy), fill="#a7d36e")
    d.ellipse((24, 0, 29, 4), fill="#f3ead2", outline=OUTLINE)
    d.point((26, 1), fill="#6aa04a")
    d.line((28, 6, 31, 2), fill="#9aa0a6", width=2)
    for xx in (5, 22):
        d.ellipse((xx, 10, xx + 5, 15), fill="#33313a", outline=OUTLINE)
        d.point((xx + 2, 12), fill="#9aa0a6")


@_register("flower_stall", (1, 1))
def _flower_stall(im, d, collision):
    d.ellipse((0, 4, 15, 15), fill="#9b6b3e", outline=OUTLINE)
    d.ellipse((2, 5, 13, 12), fill="#6e4a2c")
    for i in range(3):
        d.arc((3 + i, 5 + i, 12 - i, 12 - i), 0, 360, fill=("#fff6e4", "#f4a23c", "#fff6e4")[i])
    d.point((7, 8), fill="#e04f5f")
    d.point((9, 8), fill="#e04f5f")
    for xx in (2, 13):
        d.point((xx, 3), fill="#fff6e4")
        d.point((xx, 2), fill="#f4a23c")


@_register("veg_cart", (2, 1))
def _veg_cart(im, d, collision):
    _panel(d, (1, 7, 30, 11), "#4f86b0")
    piles = (("#d9534f", 5), ("#6fbf4a", 11), ("#b7698e", 17), ("#f2d14c", 23), ("#6fbf4a", 27))
    for c, cx in piles:
        for k, (ox, oy) in enumerate(((-2, 4), (1, 4), (-1, 1))):
            d.ellipse((cx + ox, oy, cx + ox + 3, oy + 3), fill=c, outline=OUTLINE)
        d.point((cx - 1, 2), fill=_shade(c, 50))
    for xx in (5, 22):
        d.ellipse((xx, 10, xx + 5, 15), fill="#33313a", outline=OUTLINE)


@_register("groundnut_stall", (2, 2))
def _groundnut_stall(im, d, collision):
    collision[:] = [[False, False], [True, True]]
    # striped cloth umbrella on a bamboo pole
    d.line((16, 6, 16, 22), fill=WOOD[1], width=2)
    d.pieslice((2, 1, 30, 17), 180, 360, fill="#d9534f", outline=OUTLINE)
    for a in range(195, 345, 30):
        import math
        d.line((16, 9, 16 + round(13 * math.cos(math.radians(a))), 9 + round(8 * math.sin(math.radians(a)))), fill=CREAM)
    d.line((3, 9, 29, 9), fill=OUTLINE)
    # mat with baskets of groundnuts and a little brass scale
    d.rectangle((0, 20, 31, 30), fill="#c9a865", outline=OUTLINE)
    for xx in (1, 21):
        d.line((xx, 21, xx + 9, 21), fill="#e0c486")
    for cx in (7, 18):
        d.ellipse((cx - 6, 18, cx + 6, 29), fill="#8a5a33", outline=OUTLINE)
        d.ellipse((cx - 5, 17, cx + 5, 25), fill="#c99a5e")
        for k in range(5):
            d.point((cx - 3 + k * 2 - (k % 2), 19 + (k % 3) * 2), fill="#7d5532")
    d.line((25, 22, 29, 22), fill="#d6a23c")
    d.line((27, 19, 27, 22), fill=OUTLINE)
    d.ellipse((24, 23, 27, 25), fill="#d6a23c", outline=OUTLINE)
    d.ellipse((27, 23, 30, 25), fill="#d6a23c", outline=OUTLINE)


@_register("garbage_pile", (1, 1))
def _garbage_pile(im, d, collision):
    for box, c in (((1, 7, 9, 15), "#2f2b36"), ((6, 5, 15, 14), "#3b5f8c"), ((3, 3, 10, 10), "#3f3a44")):
        d.ellipse(box, fill=c, outline=OUTLINE)
        d.point((box[0] + 2, box[1] + 2), fill=_shade(c, 45))
    d.line((5, 3, 6, 1), fill=OUTLINE)
    d.line((7, 3, 8, 1), fill=OUTLINE)
    d.rectangle((11, 11, 13, 12), fill="#e9b945")
    d.point((2, 14), fill="#d9534f")
    d.ellipse((12, 3, 15, 6), fill="#8a5a33", outline=OUTLINE)


@_register("dog", (1, 1))
def _dog(im, d, collision):
    _pixels(im, """
................
................
................
................
................
...........OO...
..........OttO..
...OOOOOOOOtttOO
..OtttttttOttwtO
.OtwttttttttttO.
.OttttttttwwtOO.
.OttttttttwwO...
..OOttOOOttwO...
....OO...OOO....
................
................
""", {"O": OUTLINE, "t": "#c68a52", "w": "#f3e3c2"})
    d.point((13, 8), fill=OUTLINE)


@_register("barricade", (1, 1))
def _barricade(im, d, collision):
    for xx in (2, 12):
        d.line((xx, 7, xx - 1, 15), fill=OUTLINE, width=2)
    d.rectangle((0, 3, 15, 9), fill="#f2d14c", outline=OUTLINE)
    for xx in range(-4, 16, 5):
        d.polygon(((xx + 1, 4), (xx + 3, 4), (xx + 6, 8), (xx + 4, 8)), fill="#2f2b36")
    d.rectangle((0, 3, 15, 9), outline=OUTLINE)


@_register("cone", (1, 1))
def _cone(im, d, collision):
    d.polygon(((6, 2), (9, 2), (12, 13), (3, 13)), fill="#f08a3c", outline=OUTLINE)
    d.line((5, 7, 10, 7), fill=CREAM, width=2)
    d.rectangle((2, 13, 13, 15), fill="#d36f2c", outline=OUTLINE)


@_register("milestone", (1, 1))
def _milestone(im, d, collision):
    d.rectangle((3, 7, 12, 15), fill="#f1ead8", outline=OUTLINE)
    d.pieslice((3, 1, 12, 12), 180, 360, fill="#f4c24f", outline=OUTLINE)
    d.line((5, 10, 10, 10), fill=OUTLINE)
    d.line((5, 12, 9, 12), fill="#7c7768")
    d.line((4, 7, 11, 7), fill=OUTLINE)


@_register("hoarding", (3, 2), params=("text", "color"))
def _hoarding(im, d, collision, text="PLOTS FOR SALE", color="#d9534f"):
    collision[:] = [[False] * 3, [True] * 3]
    for xx in (10, 36):
        _panel(d, (xx, 16, xx + 2, 31), "#5d6470")
    _panel(d, (1, 1, 46, 21), "#f1ead8")
    d.rectangle((3, 3, 44, 6), fill=_color(color))
    _label(im, text, (4, 8, 43, 19), OUTLINE)
    d.line((2, 21, 45, 21), fill=OUTLINE)


@_register("notice_board", (1, 1))
def _notice_board(im, d, collision):
    for xx in (2, 12):
        d.line((xx, 9, xx, 15), fill=WOOD[1], width=2)
    _panel(d, (0, 1, 15, 11), WOOD[0])
    d.rectangle((2, 3, 13, 9), fill="#7b9a6a")
    d.rectangle((3, 4, 7, 8), fill=CREAM)
    d.rectangle((9, 4, 12, 7), fill="#f0b2bd")
    d.line((4, 5, 6, 5), fill="#7c7768")
    d.line((4, 7, 6, 7), fill="#7c7768")


@_register("stone_tablet", (1, 1))
def _stone_tablet(im, d, collision):
    d.rounded_rectangle((3, 1, 12, 15), radius=3, fill="#9c968c", outline=OUTLINE)
    d.line((5, 2, 10, 2), fill="#c4beb2")
    for yy in (5, 7, 9, 11):
        d.line((5, yy, 10, yy), fill="#6f6a62")
    d.rectangle((2, 13, 13, 15), fill="#7f7a72", outline=OUTLINE)
    d.point((4, 4), fill="#e9b945")
    d.point((11, 4), fill="#d9534f")


@_register("metro_sign", (1, 1))
def _metro_sign(im, d, collision):
    d.line((7, 9, 7, 15), fill="#56606a", width=2)
    _panel(d, (1, 0, 14, 10), "#7a4aa8")
    _pixels(im, """
O...O
OO.OO
O.O.O
O...O
""".replace("O", "c"), {"c": CREAM}, (5, 3))


@_register("forest_sign", (1, 1))
def _forest_sign(im, d, collision):
    for xx in (2, 12):
        d.line((xx, 9, xx, 15), fill=WOOD[1], width=2)
    _panel(d, (0, 1, 15, 10), "#3f7a4a")
    for yy in (4, 6, 8):
        d.line((3, yy, 12 if yy != 8 else 9, yy), fill=CREAM)


@_register("gate_pillar", (1, 1))
def _gate_pillar(im, d, collision):
    _panel(d, (3, 5, 12, 15), "#e6dcc4")
    d.line((4, 6, 4, 14), fill=CREAM)
    _panel(d, (2, 3, 13, 6), "#d2c5a8")
    d.ellipse((5, 0, 10, 4), fill="#e6dcc4", outline=OUTLINE)


@_register("iron_gate", (2, 1))
def _iron_gate(im, d, collision):
    d.rectangle((1, 3, 30, 14), outline="#2f4a3a")
    for xx in range(3, 30, 3):
        d.line((xx, 3, xx, 14), fill="#3d6650")
        d.point((xx, 2), fill="#d6b04c")
    d.line((1, 8, 30, 8), fill="#3d6650")
    d.line((15, 2, 15, 15), fill=OUTLINE)
    d.line((16, 2, 16, 15), fill=OUTLINE)
    d.rectangle((14, 7, 17, 9), fill="#d6b04c")


@_register("naga_stones", (1, 1))
def _naga_stones(im, d, collision):
    d.rectangle((0, 12, 15, 15), fill="#8f8a80", outline=OUTLINE)
    for xx in (1, 8):
        d.rounded_rectangle((xx, 1, xx + 6, 13), radius=3, fill="#7e7a72", outline=OUTLINE)
        d.line([(xx + 3, 11), (xx + 2, 9), (xx + 4, 7), (xx + 2, 5), (xx + 3, 3)], fill="#b5aea1")
        d.point((xx + 3, 2), fill="#b5aea1")
        d.point((xx + 2, 12), fill="#f4c24f")
        d.point((xx + 4, 12), fill="#d9534f")
    d.line((1, 13, 14, 13), fill="#f4a23c")


@_register("tree_katte", (3, 3))
def _tree_katte(im, d, collision):
    _only(collision, (0, 2), (1, 2), (2, 2), (1, 1))
    # the raised stone platform where the neighbourhood sits under the peepal tree
    d.ellipse((1, 28, 46, 47), fill="#a99d88", outline=OUTLINE)
    d.ellipse((1, 26, 46, 42), fill="#d0c6b2", outline=OUTLINE)
    d.arc((4, 28, 43, 40), 200, 340, fill="#e4dccb")
    _panel(d, (20, 14, 27, 36), WOOD[1])
    d.line((21, 15, 21, 34), fill=WOOD[2])
    d.line((19, 35, 28, 35), fill=OUTLINE)
    _foliage(d, (2, 1, 45, 27), ("#5fa65b", "#3b7a4e", "#9bd06f"))
    for xx, yy in ((10, 8), (30, 6), (20, 14), (36, 16)):
        d.polygon(((xx, yy), (xx + 2, yy - 2), (xx + 4, yy)), fill="#b5dc85")
    # red and yellow threads tied round the trunk, and two snake stones
    d.line((20, 31, 27, 31), fill="#d9534f")
    d.line((20, 32, 27, 32), fill="#f4c24f")
    for xx in (7, 37):
        d.rounded_rectangle((xx, 27, xx + 4, 35), radius=2, fill="#7e7a72", outline=OUTLINE)
        d.point((xx + 2, 30), fill="#f4c24f")


@_register("shrine", (1, 2))
def _shrine(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (2, 12, 13, 30), "#efe6d2")
    d.polygon(((0, 13), (8, 5), (15, 13)), fill="#b95946", outline=OUTLINE)
    d.line((4, 11, 11, 11), fill="#ec9b63")
    d.point((8, 4), fill="#f4c24f")
    d.line((8, 2, 8, 4), fill="#d6a23c")
    _arch(d, (4, 15, 11, 27), "#5a3b3b", "#d9c8a4")
    d.ellipse((6, 19, 9, 23), fill="#e9944c")
    d.point((7, 20), fill="#ffe08a")
    d.line((4, 28, 11, 28), fill="#f4a23c")
    d.rectangle((1, 29, 14, 31), fill="#b6ad9c", outline=OUTLINE)


@_register("well", (1, 2))
def _well(im, d, collision):
    collision[:] = [[False], [True]]
    for xx in (2, 13):
        d.line((xx, 6, xx, 22), fill=WOOD[1], width=2)
    d.line((1, 6, 14, 6), fill=WOOD[1], width=2)
    d.ellipse((6, 4, 9, 9), fill="#7c7768", outline=OUTLINE)
    d.line((8, 9, 8, 21), fill="#c9b78f")
    d.ellipse((0, 18, 15, 31), fill="#a39a8c", outline=OUTLINE)
    d.ellipse((2, 19, 13, 27), fill="#2e4f5c")
    d.line((4, 21, 7, 21), fill="#6fa3b5")
    for xx in range(1, 15, 4):
        d.line((xx, 28, xx + 2, 28), fill="#8a8172")
    d.rectangle((6, 18, 9, 21), fill="#9aa0a6", outline=OUTLINE)


@_register("handpump", (1, 1))
def _handpump(im, d, collision):
    d.ellipse((1, 10, 14, 15), fill="#a8a59c", outline=OUTLINE)
    d.ellipse((4, 11, 10, 14), fill="#7aa6b6")
    _panel(d, (6, 2, 9, 11), "#4f6f8f")
    d.line((9, 3, 14, 1), fill=OUTLINE, width=2)
    d.line((5, 6, 3, 8), fill=OUTLINE, width=2)
    d.rectangle((5, 1, 10, 3), fill="#5f7f9f", outline=OUTLINE)


@_register("post_box", (1, 1))
def _post_box(im, d, collision):
    d.rectangle((4, 4, 11, 14), fill="#c8443a", outline=OUTLINE)
    d.ellipse((3, 0, 12, 7), fill="#d9534f", outline=OUTLINE)
    d.rectangle((4, 4, 11, 6), fill="#d9534f")
    d.line((5, 7, 10, 7), fill=OUTLINE)
    d.line((5, 3, 6, 2), fill="#f08a80")
    d.rectangle((6, 10, 9, 11), fill="#f4c24f")
    d.rectangle((3, 14, 12, 15), fill="#8f2f2a", outline=OUTLINE)


@_register("bench_stone", (2, 1))
def _bench_stone(im, d, collision):
    for xx in (4, 24):
        _panel(d, (xx, 8, xx + 4, 15), "#8f8a80")
    _panel(d, (1, 4, 30, 9), "#b7b0a3")
    d.line((3, 5, 28, 5), fill="#d6cfc2")


@_register("drum_barrel", (1, 1), params=("color",))
def _drum_barrel(im, d, collision, color="#3f6fb0"):
    c = _color(color)
    d.rectangle((3, 3, 12, 14), fill=c, outline=OUTLINE)
    d.ellipse((3, 1, 12, 5), fill=_shade(c, 30), outline=OUTLINE)
    d.ellipse((5, 2, 10, 4), fill=_shade(c, -30))
    for yy in (7, 11):
        d.line((3, yy, 12, yy), fill=_shade(c, -35))
    d.line((4, 6, 4, 13), fill=_shade(c, 40))


@_register("pipe_outlet", (1, 1))
def _pipe_outlet(im, d, collision):
    d.ellipse((1, 1, 14, 12), fill="#a7a49b", outline=OUTLINE)
    d.ellipse((4, 3, 11, 10), fill="#3b3440")
    d.polygon(((5, 9), (10, 9), (12, 15), (3, 15)), fill="#6f6a4e")
    d.line((6, 10, 5, 15), fill="#8f8a62")
    d.point((9, 12), fill="#c8cfc6")


@_register("site_fence_h", (1, 1))
def _site_fence_h(im, d, collision):
    d.rectangle((0, 1, 15, 14), fill="#3f6fa8", outline=OUTLINE)
    for xx in range(1, 16, 3):
        d.line((xx, 2, xx, 13), fill="#6a95c8")
    d.rectangle((0, 11, 15, 14), fill="#f2d14c", outline=OUTLINE)
    for xx in range(-2, 16, 4):
        d.line((xx, 14, xx + 3, 11), fill="#2f2b36")


@_register("site_fence_v", (1, 1))
def _site_fence_v(im, d, collision):
    _site_fence_h(im, d, collision)
    rotated = im.transpose(Image.Transpose.ROTATE_90)
    im.paste(rotated)


@_register("crane", (3, 5), fg=[[True] * 3] * 4 + [[False] * 3])
def _crane(im, d, collision):
    _only(collision, (1, 4))
    yellow = "#e9b945"
    d.rectangle((20, 10, 27, 75), fill=None, outline=OUTLINE)
    for yy in range(10, 74, 6):
        d.line((20, yy, 27, yy + 6), fill=yellow)
        d.line((27, yy, 20, yy + 6), fill=yellow)
    d.line((20, 10, 20, 75), fill=OUTLINE)
    d.line((27, 10, 27, 75), fill=OUTLINE)
    d.line((21, 10, 21, 75), fill=yellow)
    d.line((26, 10, 26, 75), fill="#b98a2c")
    d.polygon(((20, 8), (24, 0), (27, 8)), fill=yellow, outline=OUTLINE)
    d.rectangle((0, 8, 47, 12), outline=OUTLINE, fill=None)
    for xx in range(0, 46, 4):
        d.line((xx, 9, xx + 4, 12), fill=yellow)
    d.line((0, 8, 47, 8), fill=OUTLINE)
    d.line((0, 12, 47, 12), fill=OUTLINE)
    d.line((24, 0, 1, 8), fill=OUTLINE)
    d.line((24, 0, 46, 8), fill=OUTLINE)
    _panel(d, (1, 12, 10, 19), "#8f8a80")
    _panel(d, (28, 12, 34, 18), "#f1ead8")
    d.rectangle((29, 13, 33, 15), fill="#9fd0dc")
    d.line((41, 13, 41, 40), fill=OUTLINE)
    _panel(d, (38, 40, 44, 44), yellow)
    d.arc((39, 43, 44, 49), 270, 180, fill=OUTLINE)
    _panel(d, (14, 74, 33, 79), "#9c968c")


@_register("concrete_mixer", (2, 2))
def _concrete_mixer(im, d, collision):
    for xx in (4, 22):
        d.line((xx, 20, xx + 2, 29), fill="#56606a", width=2)
    d.polygon(((3, 9), (12, 3), (27, 8), (29, 18), (20, 24), (5, 20)), fill="#f08a3c", outline=OUTLINE)
    d.line([(7, 8), (12, 14), (18, 7), (22, 15), (26, 10)], fill="#c9682c")
    d.ellipse((24, 7, 30, 15), fill="#3b3440", outline=OUTLINE)
    d.line((8, 6, 20, 4), fill="#f6ad6a")
    for xx in (4, 22):
        d.ellipse((xx - 2, 25, xx + 4, 31), fill="#2f2b36", outline=OUTLINE)


@_register("pipe_stack", (2, 1))
def _pipe_stack(im, d, collision):
    for cx, cy in ((7, 10), (17, 10), (12, 4), (26, 10)):
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill="#b7b2a6", outline=OUTLINE)
        d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill="#4a4550")
        d.arc((cx - 5, cy - 5, cx + 5, cy + 5), 180, 260, fill="#dcd6ca")


@_register("sand_heap", (2, 1))
def _sand_heap(im, d, collision):
    d.pieslice((1, 3, 30, 28), 180, 360, fill="#d9b670", outline=OUTLINE)
    d.line((1, 15, 30, 15), fill=OUTLINE)
    for px, py in ((8, 10), (14, 7), (20, 11), (24, 13), (11, 13)):
        d.point((px, py), fill="#b8954f")
    d.line((6, 8, 10, 6), fill="#efd38f")
    d.line((24, 2, 20, 12), fill=WOOD[1], width=2)
    d.polygon(((18, 11), (22, 11), (21, 14), (18, 14)), fill="#8a9096", outline=OUTLINE)


@_register("brick_stack", (1, 1))
def _brick_stack(im, d, collision):
    for row, yy in enumerate(range(3, 15, 3)):
        off = 2 if row % 2 else 0
        for xx in range(1 + off, 14, 5):
            d.rectangle((xx, yy, xx + 4, yy + 2), fill="#c0583e", outline="#7d3427")
            d.line((xx + 1, yy, xx + 3, yy), fill="#de8566")


@_register("cement_bags", (1, 1))
def _cement_bags(im, d, collision):
    for box in ((1, 8, 8, 14), (8, 8, 15, 14), (4, 3, 12, 9)):
        d.rounded_rectangle(box, radius=2, fill="#cfccc4", outline=OUTLINE)
        d.line((box[0] + 2, box[1] + 2, box[2] - 2, box[1] + 2), fill="#9a958c")


@_register("dumper", (3, 2))
def _dumper(im, d, collision):
    d.polygon(((1, 4), (32, 4), (32, 20), (4, 20)), fill="#e98d3c", outline=OUTLINE)
    d.polygon(((3, 2), (10, 0), (18, 1), (28, 3), (30, 5), (4, 5)), fill="#8f8574", outline=OUTLINE)
    d.line((5, 9, 30, 9), fill="#f5b06e")
    d.line((5, 15, 30, 15), fill="#c66f2c")
    _panel(d, (33, 6, 46, 22), "#f2d14c")
    d.rectangle((36, 8, 44, 14), fill="#9fd0dc", outline=OUTLINE)
    d.rectangle((2, 20, 46, 24), fill="#3b3440")
    for xx in (5, 18, 36):
        d.ellipse((xx, 20, xx + 9, 29), fill="#2f2b36", outline=OUTLINE)
        d.ellipse((xx + 3, 23, xx + 6, 26), fill="#9aa0a6")


@_register("floodlight", (2, 4))
def _floodlight(im, d, collision):
    _only(collision, (0, 3), (1, 3))
    d.polygon(((12, 14), (20, 14), (24, 62), (8, 62)), fill=None, outline=OUTLINE)
    for yy in range(16, 60, 6):
        w = (yy - 14) // 12
        d.line((12 - w, yy, 20 + w, yy + 6), fill="#9db4bd")
        d.line((20 + w, yy, 12 - w, yy + 6), fill="#9db4bd")
    d.line((12, 14, 8, 62), fill="#607785", width=2)
    d.line((20, 14, 24, 62), fill="#607785", width=2)
    d.polygon(((1, 2), (31, 0), (30, 15), (2, 16)), fill="#4a5462", outline=OUTLINE)
    for row in range(3):
        for col in range(6):
            x0, y0 = 4 + col * 4, 3 + row * 4
            d.rectangle((x0, y0, x0 + 2, y0 + 2), fill="#fff3c4")
            d.point((x0, y0), fill="#ffffff")
    _panel(d, (6, 60, 26, 63), "#9c968c")


def _pillar(d, top, bottom, cap_color):
    _panel(d, (4, top + 6, 11, bottom - 3), "#d5d1c7")
    d.line((5, top + 7, 5, bottom - 4), fill="#ece9e1")
    d.line((10, top + 7, 10, bottom - 4), fill="#aaa69c")
    _panel(d, (0, top, 15, top + 6), cap_color)
    d.line((1, top + 1, 14, top + 1), fill=_shade(cap_color, 25))
    _panel(d, (2, bottom - 3, 13, bottom), "#a8a399")


@_register("metro_pillar", (1, 3))
def _metro_pillar(im, d, collision):
    collision[:] = [[False], [False], [True]]
    _pillar(d, 0, 47, "#c9c5ba")


@_register("flyover_pillar", (1, 3))
def _flyover_pillar(im, d, collision):
    collision[:] = [[False], [False], [True]]
    _pillar(d, 0, 47, "#b9b6ad")
    d.rectangle((5, 20, 10, 26), fill="#e9e3cf", outline="#9c968c")
    d.line((6, 22, 9, 22), fill="#c05a4c")


@_register("double_pillar", (1, 4))
def _double_pillar(im, d, collision):
    collision[:] = [[False], [False], [False], [True]]
    _pillar(d, 0, 63, "#c9c5ba")
    _panel(d, (0, 22, 15, 27), "#b9b6ad")


def _deck(d, y0, metro):
    d.line((0, y0, 15, y0), fill="#e8e5dc")
    d.rectangle((0, y0 + 1, 15, y0 + 2), fill="#cfcbc2")
    if metro:
        d.rectangle((0, y0 + 3, 15, y0 + 8), fill="#9b978f")
        for xx in range(0, 16, 4):
            d.line((xx, y0 + 3, xx, y0 + 8), fill="#857f76")
        d.line((0, y0 + 4, 15, y0 + 4), fill="#5a5f68")
        d.line((0, y0 + 7, 15, y0 + 7), fill="#5a5f68")
    else:
        d.rectangle((0, y0 + 3, 15, y0 + 8), fill="#6b737d")
        d.rectangle((4, y0 + 5, 11, y0 + 6), fill=CREAM)
    d.line((0, y0 + 9, 15, y0 + 9), fill="#e8e5dc")
    d.rectangle((0, y0 + 10, 15, y0 + 23), fill="#dedad0")
    if metro:
        d.rectangle((0, y0 + 13, 15, y0 + 15), fill="#8d4ab8")
        d.line((0, y0 + 13, 15, y0 + 13), fill="#b07ad6")
    else:
        d.line((0, y0 + 12, 15, y0 + 12), fill="#c7c3b8")
    d.rectangle((0, y0 + 20, 15, y0 + 23), fill="#bdb9af")
    d.line((0, y0 + 24, 15, y0 + 24), fill="#8c887f")


@_register("metro_deck_h", (1, 2), fg=[[True], [True]])
def _metro_deck_h(im, d, collision):
    _walkable(collision)
    _deck(d, 0, True)


@_register("flyover_deck_h", (1, 2), fg=[[True], [True]])
def _flyover_deck_h(im, d, collision):
    _walkable(collision)
    _deck(d, 0, False)


@_register("double_deck_h", (1, 3), fg=[[True], [True], [True]])
def _double_deck_h(im, d, collision):
    _walkable(collision)
    _deck(d, 0, True)
    d.rectangle((6, 25, 9, 28), fill="#c9c5ba")
    _deck(d, 22, False)


@_register("security_booth", (1, 2))
def _security_booth(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (1, 8, 14, 30), "#5d86b0")
    d.polygon(((0, 9), (2, 3), (13, 3), (15, 9)), fill="#3d5a7a", outline=OUTLINE)
    _window(d, (3, 11, 12, 18), False)
    d.rectangle((4, 21, 11, 29), fill="#3d5a7a", outline=OUTLINE)
    d.point((10, 25), fill="#f4c24f")


@_register("boom_barrier", (2, 1))
def _boom_barrier(im, d, collision):
    _only(collision, (0, 0))
    _panel(d, (2, 5, 9, 15), "#e9b945")
    d.line((6, 7, 30, 1), fill=OUTLINE, width=3)
    for i in range(6):
        xx = 9 + i * 4
        d.line((xx, 6 - i, xx + 2, 5 - i), fill="#d9534f" if i % 2 else CREAM)
    d.point((5, 8), fill="#d9534f")


# ------------------------------------------------------------------------------------------------
# nature, animals and village life
# ------------------------------------------------------------------------------------------------
@_register("ashoka", (1, 2))
def _ashoka(im, d, collision):
    collision[:] = [[False], [True]]
    d.rectangle((7, 26, 8, 30), fill=WOOD[1])
    d.line((5, 31, 10, 31), fill=OUTLINE)
    d.polygon(((8, 0), (12, 7), (13, 15), (14, 22), (11, 28), (5, 28), (2, 22), (3, 15), (4, 7)), fill="#2f6d3f", outline=OUTLINE)
    d.polygon(((8, 2), (11, 9), (11, 18), (8, 25), (5, 18), (5, 9)), fill="#3f8a4e")
    for yy in range(4, 26, 4):
        d.line((6, yy, 8, yy + 2), fill="#6fb062")
        d.point((10, yy + 1), fill="#559e57")


@_register("bush_tall", (1, 2))
def _bush_tall(im, d, collision):
    collision[:] = [[False], [True]]
    _foliage(d, (1, 6, 14, 30), ("#4f9452", "#2e6443", "#82bb67"))


@_register("eucalyptus", (1, 2))
def _eucalyptus(im, d, collision):
    # tall, pale, peeling trunk under a loose blue-green crown
    collision[:] = [[False], [True]]
    d.polygon(((6, 30), (7, 12), (9, 12), (10, 30)), fill="#e9e3d6", outline=OUTLINE)
    for yy, c in ((15, "#c9b08a"), (20, "#b9c4b0"), (25, "#c9b08a")):
        d.line((8, yy, 9, yy + 2), fill=c)
    d.line((8, 14, 4, 9), fill=OUTLINE, width=2)
    d.line((8, 14, 4, 9), fill="#e9e3d6")
    d.line((8, 13, 12, 8), fill=OUTLINE, width=2)
    d.line((8, 13, 12, 8), fill="#e9e3d6")
    for box in ((0, 3, 8, 11), (7, 0, 15, 9), (3, 0, 11, 6)):
        d.ellipse(box, fill="#557a64", outline=OUTLINE)
    for box in ((1, 3, 7, 9), (8, 1, 14, 7), (4, 1, 10, 5)):
        d.ellipse(box, fill="#7fa88a")
    for px, py in ((3, 5), (10, 3), (6, 2), (12, 5)):
        d.line((px, py, px + 1, py + 2), fill="#b5d1b0")
    d.line((5, 31, 11, 31), fill=OUTLINE)


@_register("bamboo", (2, 2))
def _bamboo(im, d, collision):
    collision[:] = [[False, False], [True, True]]
    for i, xx in enumerate((5, 9, 13, 18, 22, 26)):
        top = 2 + (i * 5) % 7
        d.line((xx, top, xx + (i % 2) - 1, 30), fill="#6fa34a", width=2)
        for yy in range(top + 4, 30, 6):
            d.line((xx - 1, yy, xx + 1, yy), fill="#3f6f35")
    for lx, ly in ((3, 6), (11, 3), (20, 5), (27, 9), (7, 13), (24, 15), (15, 10)):
        d.polygon(((lx, ly), (lx + 5, ly - 2), (lx + 2, ly + 1)), fill="#8cc05a", outline="#3f6f35")
    d.line((2, 31, 29, 31), fill=OUTLINE)


@_register("banana", (1, 2))
def _banana(im, d, collision):
    collision[:] = [[False], [True]]
    d.rectangle((7, 14, 9, 30), fill="#9bb05a", outline=OUTLINE)
    for pts in (((8, 14), (0, 6), (2, 3), (8, 11)), ((8, 13), (15, 4), (14, 1), (8, 10)),
                ((8, 12), (5, 0), (9, 0), (9, 10)), ((8, 16), (1, 18), (0, 14), (7, 14))):
        d.polygon(pts, fill="#76b04a", outline="#2e5a32")
        d.line((pts[0], pts[1]), fill="#a7d36e")
    d.ellipse((9, 15, 13, 21), fill="#6a8a3a", outline=OUTLINE)


@_register("stump", (1, 1))
def _stump(im, d, collision):
    d.polygon(((3, 7), (12, 7), (13, 14), (2, 14)), fill=WOOD[1], outline=OUTLINE)
    d.ellipse((2, 3, 13, 10), fill="#e7c48f", outline=OUTLINE)
    d.ellipse((5, 5, 10, 8), outline="#c49a62")
    d.point((7, 6), fill="#c49a62")
    d.line((4, 10, 4, 13), fill=WOOD[0])
    for xx, yy in ((1, 13), (12, 14), (14, 12)):
        d.point((xx, yy), fill="#d8b47e")


@_register("log", (2, 1))
def _log(im, d, collision):
    d.rounded_rectangle((1, 5, 28, 13), radius=4, fill=WOOD[1], outline=OUTLINE)
    d.line((4, 7, 25, 7), fill=WOOD[0])
    d.line((6, 10, 22, 10), fill="#6e4a38")
    d.ellipse((24, 5, 31, 13), fill="#d9b27c", outline=OUTLINE)
    d.ellipse((26, 7, 29, 11), outline="#b48a5a")
    d.ellipse((9, 3, 13, 6), fill="#6aa04a", outline=OUTLINE)


@_register("reeds", (1, 1))
def _reeds(im, d, collision):
    for xx, top, c in ((2, 4, "#5f9a48"), (5, 1, "#76b04a"), (8, 3, "#5f9a48"), (11, 0, "#76b04a"), (13, 5, "#5f9a48")):
        d.line((xx, top, xx + (1 if xx % 2 else -1), 15), fill=c)
    for xx, yy in ((5, 2), (11, 1)):
        d.rectangle((xx - 1, yy, xx, yy + 3), fill="#8a5a33", outline=OUTLINE)


@_register("termite_mound", (1, 1))
def _termite_mound(im, d, collision):
    d.polygon(((2, 15), (4, 8), (6, 3), (8, 0), (10, 4), (11, 7), (13, 10), (14, 15)), fill="#b06c47", outline=OUTLINE)
    d.line((6, 5, 5, 13), fill="#cf8d63")
    d.point((10, 9), fill="#7f4a32")
    d.point((7, 11), fill="#7f4a32")


@_register("thorn_bush", (1, 1))
def _thorn_bush(im, d, collision):
    _foliage(d, (1, 4, 14, 15), ("#8f9a52", "#5f6a3a", "#b8c071"))
    for xx, yy in ((3, 6), (11, 5), (7, 3), (13, 10)):
        d.line((xx, yy, xx + 1, yy - 2), fill="#7a5a3a")
    d.point((6, 9), fill="#d9534f")
    d.point((10, 11), fill="#d9534f")


@_register("euphorbia", (1, 2))
def _euphorbia(im, d, collision):
    collision[:] = [[False], [True]]
    for xx, top in ((7, 2), (3, 10), (11, 8)):
        d.rounded_rectangle((xx, top, xx + 2, 29), radius=1, fill="#5e9a54", outline=OUTLINE)
        d.line((xx + 1, top + 1, xx + 1, 28), fill="#8cc073")
    d.line((4, 22, 7, 22), fill="#5e9a54")
    d.line((10, 20, 11, 20), fill="#5e9a54")
    d.line((2, 30, 13, 30), fill=OUTLINE)


@_register("boulder_big", (3, 3))
def _boulder_big(im, d, collision):
    d.ellipse((1, 4, 46, 47), fill="#7f756b", outline=OUTLINE)
    d.ellipse((2, 2, 44, 42), fill="#b6ab9d")
    d.ellipse((5, 4, 30, 24), fill="#d3c9bc")
    d.ellipse((8, 6, 20, 14), fill="#e6ded2")
    d.arc((2, 2, 44, 42), 10, 120, fill="#9a8f83", width=3)
    d.arc((10, 14, 40, 44), 300, 30, fill="#9a8f83")
    d.line([(30, 12), (33, 20), (31, 28)], fill="#857b70")
    for px, py in ((14, 26), (24, 32), (36, 18), (18, 34)):
        d.point((px, py), fill="#8d8378")
    d.ellipse((34, 8, 38, 11), fill="#8d9662")
    d.ellipse((30, 30, 46, 46), fill="#a1968a", outline=OUTLINE)
    d.arc((31, 30, 45, 42), 200, 300, fill="#c9bfb2")


@_register("nest_tree", (3, 3), fg=[[True, True, True], [True, False, True], [False, False, False]])
def _nest_tree(im, d, collision):
    _only(collision, (1, 1), (1, 2))
    _panel(d, (20, 22, 27, 44), WOOD[1])
    d.line((21, 23, 21, 42), fill=WOOD[2])
    d.line((18, 45, 30, 45), fill=OUTLINE)
    _foliage(d, (1, 4, 46, 36), ("#6ea85b", "#3f7a4e", "#a2d27a"))
    # untidy twig nests full of chicks, white pelicans and painted storks perched on top
    for nx, ny in ((7, 10), (27, 6), (36, 18)):
        d.ellipse((nx, ny + 3, nx + 9, ny + 7), fill="#8a5a33", outline=OUTLINE)
        d.line((nx + 1, ny + 4, nx + 8, ny + 4), fill="#b98a52")
    for bx, by in ((9, 6), (29, 2)):
        d.ellipse((bx, by, bx + 6, by + 5), fill="#f6f2ea", outline=OUTLINE)
        d.ellipse((bx + 4, by - 3, bx + 7, by), fill="#f6f2ea", outline=OUTLINE)
        d.line((bx + 7, by - 1, bx + 10, by + 2), fill="#e8b25a", width=2)
    for bx, by in ((37, 13), (17, 16)):
        d.ellipse((bx, by, bx + 6, by + 4), fill="#f6f2ea", outline=OUTLINE)
        d.line((bx, by + 3, bx + 3, by + 3), fill="#e48aa4")
        d.line((bx + 1, by + 1, bx + 4, by + 1), fill="#2f2b36")
        d.line((bx + 6, by - 2, bx + 6, by), fill="#f6f2ea")
        d.line((bx + 6, by - 2, bx + 9, by + 1), fill="#e8c25a")
    for px, py in ((4, 30), (40, 32), (16, 33), (30, 34)):
        d.point((px, py), fill="#f6f2ea")


@_register("pelican", (1, 1))
def _pelican(im, d, collision):
    d.line((6, 12, 6, 15), fill="#e8a25a")
    d.line((9, 12, 9, 15), fill="#e8a25a")
    d.ellipse((2, 5, 12, 13), fill="#e6e2da", outline=OUTLINE)
    d.line((3, 9, 9, 11), fill="#a9a59c")
    d.ellipse((9, 1, 13, 5), fill="#f1ede5", outline=OUTLINE)
    d.polygon(((12, 3), (16, 4), (15, 8), (12, 6)), fill="#e8c27a", outline=OUTLINE)
    d.point((11, 2), fill=OUTLINE)


@_register("stork", (1, 1))
def _stork(im, d, collision):
    d.line((6, 10, 6, 15), fill="#e48aa4")
    d.line((8, 10, 9, 15), fill="#e48aa4")
    d.ellipse((2, 4, 11, 11), fill="#f6f2ea", outline=OUTLINE)
    d.line((3, 7, 9, 7), fill="#2f2b36")
    d.line((2, 9, 6, 10), fill="#e48aa4")
    d.line((10, 1, 10, 5), fill="#f6f2ea", width=2)
    d.ellipse((9, 0, 12, 3), fill="#f0c27a", outline=OUTLINE)
    d.line((12, 2, 15, 6), fill="#e8c25a", width=2)


@_register("roof_birds", (2, 1), fg=[[False, False]])
def _roof_birds(im, d, collision):
    _walkable(collision)
    for bx in (3, 18):
        d.ellipse((bx, 6, bx + 7, 11), fill="#f6f2ea", outline=OUTLINE)
        d.line((bx + 6, 2, bx + 6, 6), fill="#f6f2ea", width=2)
        d.ellipse((bx + 5, 1, bx + 8, 4), fill="#f6f2ea", outline=OUTLINE)
        d.line((bx + 8, 3, bx + 11, 6), fill="#e8c25a", width=2)
        d.line((bx + 1, 9, bx + 4, 9), fill="#e48aa4")
        d.line((bx + 3, 11, bx + 3, 14), fill="#e48aa4")


@_register("haystack", (1, 2))
def _haystack(im, d, collision):
    collision[:] = [[False], [True]]
    d.polygon(((8, 4), (14, 18), (15, 29), (1, 29), (2, 18)), fill="#d9b45a", outline=OUTLINE)
    for yy in range(10, 28, 4):
        d.line((4, yy, 12, yy + 1), fill="#b08a3a")
        d.line((3, yy + 2, 6, yy + 2), fill="#f0d27a")
    d.line((8, 0, 8, 6), fill=WOOD[1], width=2)
    d.line((1, 30, 14, 30), fill=OUTLINE)


@_register("buffalo", (2, 1))
def _buffalo(im, d, collision):
    _pixels(im, """
................................
.......................OO....OO.
......................O..OOOO..O
...OOOOOOOOOOOOOOOOOOOOObbbbbbO.
..ObbbbbbbbbbbbbbbbbbbbbbblbbbO.
..ObbbbbbbbbbbbbbbbbbbbbbbbbbbO.
..ObbbbbbbbbbbbbbbbbbbbOObbbbbO.
.OObbbbbbbbbbbbbbbbbbbbO.ObbbO..
.O.ObbbbbbbbbbbbbbbbbbbO..OpO...
...ObbbbbbbbbbbbbbbbbbbO...O....
...ObbOOOOOOOOOOOOOObbO.........
...ObbO............ObbO.........
...ObbO............ObbO.........
...OOOO............OOOO.........
................................
................................
""", {"O": OUTLINE, "b": "#45434e", "l": "#e6e2da", "p": "#9b8f96"})
    d.line((4, 4, 20, 4), fill="#5d5a68")


@_register("monkey", (1, 1))
def _monkey(im, d, collision):
    _pixels(im, """
................
................
.....OOOO.......
....ObbbbO......
...ObffffbO.....
...OffOfOfO.....
...ObffffbO.....
....ObffbO......
...ObbbbbbO.....
..ObbbbbbbbO..O.
..ObbObbObbO.ObO
..ObbObbObbOObO.
...OOObbOOObbO..
.....OOOO.OOO...
................
................
""", {"O": OUTLINE, "b": "#8c7a66", "f": "#e2a89a"})


@_register("hens", (1, 1), decal=True)
def _hens(im, d, collision):
    _walkable(collision)
    for hx, hy, c in ((2, 6, "#f1e7ce"), (9, 9, "#b8653f")):
        d.ellipse((hx, hy, hx + 5, hy + 4), fill=c, outline=OUTLINE)
        d.ellipse((hx + 4, hy - 2, hx + 7, hy + 1), fill=c, outline=OUTLINE)
        d.point((hx + 5, hy - 3), fill="#d9534f")
        d.point((hx + 8, hy), fill="#e8b25a")
        d.line((hx + 2, hy + 5, hx + 2, hy + 6), fill="#e8b25a")


# ------------------------------------------------------------------------------------------------
# parks, hills, temples and ruins
# ------------------------------------------------------------------------------------------------
@_register("fort_arch", (3, 3), fg=[[True] * 3, [True] * 3, [False] * 3])
def _fort_arch(im, d, collision):
    _only(collision, (0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2))
    for row, yy in enumerate(range(4, 48, 4)):
        off = 4 if row % 2 else 0
        for xx in range(-off, 48, 8):
            n = _seed(xx, yy, 9)
            d.rectangle((xx, yy, xx + 7, yy + 3), fill=("#a99f8e", "#9e9483", "#b3a998")[n % 3])
            d.line((xx, yy, xx + 6, yy), fill="#c8beab")
            d.line((xx + 7, yy, xx + 7, yy + 3), fill="#6f665b")
            d.line((xx, yy + 3, xx + 7, yy + 3), fill="#6f665b")
    for xx in range(0, 48, 8):
        d.rectangle((xx, 0, xx + 4, 4), fill="#b3a998", outline=OUTLINE)
    d.rectangle((0, 4, 47, 47), outline=OUTLINE)
    _arch(d, (16, 12, 31, 48), "#3b3440", "#c8beab")
    d.rectangle((17, 30, 30, 47), fill="#5b5148")
    d.line((17, 47, 30, 47), fill="#5b5148")
    d.rectangle((21, 6, 26, 10), fill="#d9c08a", outline=OUTLINE)


@_register("railing_h", (1, 1))
def _railing_h(im, d, collision):
    d.line((0, 5, 15, 5), fill=OUTLINE, width=2)
    d.line((0, 5, 15, 5), fill="#3d6650")
    d.line((0, 10, 15, 10), fill="#3d6650")
    for xx in (1, 8):
        d.line((xx, 4, xx, 14), fill="#2f4a3a", width=2)
        d.point((xx, 3), fill="#d6b04c")


@_register("railing_v", (1, 1))
def _railing_v(im, d, collision):
    _railing_h(im, d, collision)
    im.paste(im.transpose(Image.Transpose.ROTATE_90))


@_register("binoculars", (1, 1))
def _binoculars(im, d, collision):
    d.line((8, 8, 8, 14), fill="#56606a", width=2)
    d.ellipse((4, 13, 12, 15), fill="#8e8b84", outline=OUTLINE)
    d.rounded_rectangle((3, 2, 13, 8), radius=2, fill="#3f6fb0", outline=OUTLINE)
    d.ellipse((4, 3, 7, 6), fill="#2f2b36")
    d.ellipse((9, 3, 12, 6), fill="#2f2b36")
    d.point((5, 4), fill="#9fd0dc")
    d.point((10, 4), fill="#9fd0dc")


@_register("watchtower", (2, 3))
def _watchtower(im, d, collision):
    # one of Kempegowda's four boundary towers: a small granite mantapa on a rock
    _panel(d, (2, 34, 29, 46), "#a39885")
    for xx in range(3, 29, 6):
        d.line((xx, 35, xx, 45), fill="#867b69")
    d.line((3, 40, 28, 40), fill="#867b69")
    _panel(d, (5, 30, 26, 35), "#c2b69f")
    for xx in (7, 13, 18, 24):
        _panel(d, (xx - 1, 16, xx + 1, 30), "#c9bda6")
    d.rectangle((9, 18, 22, 29), fill="#4a3f3a")
    _panel(d, (3, 12, 28, 17), "#b5a991")
    d.polygon(((6, 12), (10, 6), (21, 6), (25, 12)), fill="#c2b69f", outline=OUTLINE)
    d.ellipse((11, 1, 20, 9), fill="#cfc3ab", outline=OUTLINE)
    d.line((15, 0, 15, 2), fill="#d6a23c")
    d.point((15, 0), fill="#f4d481")
    d.line((7, 13, 25, 13), fill="#ddd2bb")


@_register("mantapa", (3, 3), fg=[[True] * 3, [True] * 3, [False] * 3])
def _mantapa(im, d, collision):
    _only(collision, (0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2))
    d.rectangle((2, 40, 45, 47), fill="#b9ad96", outline=OUTLINE)
    d.line((3, 41, 44, 41), fill="#d6cbb4")
    d.rectangle((6, 16, 41, 40), fill="#5a4f48")
    for xx in (5, 39):
        _panel(d, (xx, 14, xx + 4, 41), "#cbbfa7")
        d.rectangle((xx - 1, 14, xx + 5, 16), fill="#b9ad96", outline=OUTLINE)
        d.line((xx + 1, 20, xx + 3, 20), fill="#9d917b")
        d.line((xx + 1, 30, xx + 3, 30), fill="#9d917b")
    _panel(d, (0, 8, 47, 15), "#bfb39b")
    d.line((1, 9, 46, 9), fill="#ddd2bb")
    for xx in range(3, 46, 6):
        d.rectangle((xx, 12, xx + 2, 13), fill="#9d917b")
    d.polygon(((8, 8), (14, 2), (33, 2), (39, 8)), fill="#cbbfa7", outline=OUTLINE)
    d.line((23, 0, 23, 2), fill="#d6a23c")


@_register("yali_pillar", (1, 2))
def _yali_pillar(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (3, 3, 12, 29), "#b8ac94")
    d.rectangle((1, 0, 14, 4), fill="#a69a82", outline=OUTLINE)
    d.rectangle((2, 27, 13, 31), fill="#a69a82", outline=OUTLINE)
    # rearing yali: lion body, curled trunk-snout, rider's spear
    d.polygon(((5, 24), (5, 15), (7, 10), (10, 8), (12, 10), (11, 14), (9, 16), (9, 24)), fill="#cfc3aa", outline="#7d725f")
    d.ellipse((8, 7, 12, 11), fill="#cfc3aa", outline="#7d725f")
    d.arc((10, 9, 14, 14), 270, 90, fill="#7d725f")
    d.point((10, 9), fill=OUTLINE)
    d.line((6, 16, 4, 21), fill="#7d725f")
    d.line((5, 13, 6, 6), fill="#7d725f")
    d.line((4, 26, 11, 26), fill="#9d917b")


@_register("pillar", (1, 2))
def _pillar_plain(im, d, collision):
    collision[:] = [[False], [True]]
    _panel(d, (4, 3, 11, 29), "#c3b8a2")
    d.line((5, 4, 5, 28), fill="#ddd3bf")
    for yy in (9, 15, 21):
        d.rectangle((4, yy, 11, yy + 2), fill="#a99d87")
    d.rectangle((2, 0, 13, 3), fill="#aea28b", outline=OUTLINE)
    d.rectangle((2, 28, 13, 31), fill="#aea28b", outline=OUTLINE)


@_register("broken_pillar", (1, 1))
def _broken_pillar(im, d, collision):
    d.polygon(((4, 15), (4, 5), (6, 3), (8, 6), (10, 2), (11, 4), (11, 15)), fill="#c3b8a2", outline=OUTLINE)
    d.line((5, 6, 5, 14), fill="#ddd3bf")
    d.rectangle((2, 12, 13, 15), fill="#aea28b", outline=OUTLINE)
    d.rectangle((4, 9, 11, 10), fill="#a99d87")


@_register("fallen_slab", (2, 1))
def _fallen_slab(im, d, collision):
    d.polygon(((1, 7), (27, 4), (30, 10), (3, 14)), fill="#b8ac94", outline=OUTLINE)
    d.line((3, 8, 26, 5), fill="#d6cbb4")
    for xx in (9, 17, 24):
        d.line((xx, 6, xx + 1, 12), fill="#9d917b")
    d.ellipse((12, 0, 17, 4), fill="#8d9662")


@_register("carving", (1, 1), params=("motif",))
def _carving(im, d, collision, motif="bull"):
    d.rectangle((1, 1, 14, 14), fill=(60, 50, 64, 90))
    d.rectangle((2, 2, 13, 13), fill=(170, 158, 150, 255), outline=(70, 60, 70, 255))
    c = (110, 98, 98, 255)
    if motif == "bull":
        d.polygon(((3, 11), (4, 7), (8, 6), (10, 4), (12, 6), (12, 11)), fill=c)
        d.line((10, 4, 9, 2), fill=c)
        d.line((12, 5, 13, 3), fill=c)
    elif motif == "elephant":
        d.ellipse((3, 5, 11, 11), fill=c)
        d.line((11, 7, 12, 12), fill=c, width=2)
        d.line((5, 11, 5, 12), fill=c)
        d.line((9, 11, 9, 12), fill=c)
    else:
        d.line([(8, 12), (6, 10), (9, 8), (6, 6), (8, 4)], fill=c, width=2)
        d.ellipse((6, 2, 10, 5), fill=c)
    d.line((3, 3, 12, 3), fill=(205, 196, 188, 255))


@_register("lantern", (1, 1))
def _lantern(im, d, collision):
    for x0, x1 in ((7, 3), (8, 12), (7, 8)):
        d.line((x0, 7, x1, 15), fill="#56606a")
    _panel(d, (4, 1, 11, 7), "#e9b945")
    d.rectangle((5, 2, 10, 5), fill="#fff3c4")
    d.ellipse((2, 0, 13, 9), outline=(255, 230, 150, 120))


@_register("lamp_stand", (1, 2))
def _lamp_stand(im, d, collision):
    collision[:] = [[False], [True]]
    d.rectangle((7, 4, 8, 28), fill="#c9932f", outline=OUTLINE)
    for yy, half in ((6, 5), (12, 6), (18, 5), (24, 6)):
        d.ellipse((8 - half, yy, 8 + half, yy + 2), fill="#d9a23c", outline=OUTLINE)
        d.point((8 - half + 1, yy), fill="#ffd27a")
        d.point((8 + half - 1, yy), fill="#ffd27a")
    d.polygon(((7, 1), (8, 0), (9, 1), (8, 4)), fill="#ffb347")
    d.ellipse((3, 27, 13, 31), fill="#b07f2a", outline=OUTLINE)


@_register("brazier", (1, 1))
def _brazier(im, d, collision):
    for x0, x1 in ((4, 2), (11, 13)):
        d.line((x0, 9, x1, 15), fill=OUTLINE, width=2)
    d.pieslice((2, 3, 13, 13), 0, 180, fill="#6b5a4e", outline=OUTLINE)
    d.polygon(((4, 8), (6, 2), (8, 5), (10, 0), (12, 8)), fill="#f08a3c")
    d.polygon(((6, 8), (8, 4), (10, 8)), fill="#ffd27a")


@_register("bandstand", (3, 3))
def _bandstand(im, d, collision):
    d.polygon(((6, 36), (41, 36), (46, 41), (41, 47), (6, 47), (1, 41)), fill="#b9ad96", outline=OUTLINE)
    d.line((5, 38, 42, 38), fill="#d6cbb4")
    for xx in range(6, 42, 3):
        d.line((xx, 41, xx, 45), fill="#9d917b")
    d.rectangle((6, 20, 41, 36), fill="#4d5a52")
    for xx in (6, 16, 31, 41):
        d.line((xx, 18, xx, 36), fill="#2f4a3a", width=2)
        d.point((xx, 18), fill="#d6b04c")
    d.line((6, 31, 41, 31), fill="#6f8a7a")
    for xx in range(8, 40, 3):
        d.line((xx, 31, xx, 35), fill="#6f8a7a")
    d.polygon(((1, 20), (10, 10), (37, 10), (46, 20)), fill="#6f9a86", outline=OUTLINE)
    d.polygon(((10, 10), (16, 3), (31, 3), (37, 10)), fill="#88b39c", outline=OUTLINE)
    for xx in range(4, 44, 4):
        d.point((xx, 21), fill="#f1e7ce")
    d.line((3, 19, 44, 19), fill="#a6cbb6")
    d.line((23, 0, 23, 3), fill="#d6b04c")
    d.ellipse((21, -1, 25, 2), fill="#d6b04c")


@_register("flower_clock", (3, 3))
def _flower_clock(im, d, collision):
    d.ellipse((1, 4, 46, 47), fill="#3f7a4a", outline=OUTLINE)
    for i, c in enumerate(("#f4c24f", "#e0607a", "#f1e7ce", "#e98d3c", "#a38acb")):
        m = 3 + i * 4
        d.ellipse((1 + m, 4 + m, 46 - m, 47 - m), outline=c, width=2)
    d.ellipse((19, 21, 28, 30), fill="#6aa65e", outline=OUTLINE)
    d.line((23, 26, 23, 11), fill=OUTLINE, width=2)
    d.line((23, 26, 34, 31), fill=OUTLINE, width=2)
    import math
    for k in range(12):
        a = math.radians(k * 30)
        d.point((23 + round(19 * math.cos(a)), 26 + round(19 * math.sin(a))), fill="#fff6e4")
    d.rectangle((14, 0, 33, 5), fill=WOOD[0], outline=OUTLINE)
    d.line((16, 2, 31, 2), fill=CREAM)


@_register("topiary", (1, 1))
def _topiary(im, d, collision):
    d.rectangle((6, 11, 9, 15), fill="#c57c57", outline=OUTLINE)
    d.line((8, 8, 8, 11), fill=WOOD[1])
    d.ellipse((2, 0, 13, 10), fill="#3f8a4e", outline=OUTLINE)
    d.arc((4, 2, 11, 8), 180, 270, fill="#7fbf62")


@_register("topiary_elephant", (2, 2))
def _topiary_elephant(im, d, collision):
    g, dk, lt = "#4c9a52", "#2c6142", "#83c066"
    d.ellipse((4, 6, 25, 24), fill=g, outline=OUTLINE)
    d.ellipse((18, 3, 30, 15), fill=g, outline=OUTLINE)
    d.line((27, 13, 29, 23), fill=OUTLINE, width=4)
    d.line((27, 13, 29, 23), fill=g, width=2)
    d.ellipse((15, 6, 22, 14), fill=dk)
    for xx in (7, 13, 19):
        d.rectangle((xx, 22, xx + 3, 29), fill=g, outline=OUTLINE)
    d.arc((6, 8, 20, 18), 180, 290, fill=lt)
    d.point((25, 8), fill=OUTLINE)
    d.line((2, 30, 29, 30), fill=OUTLINE)


@_register("boat", (2, 1))
def _boat(im, d, collision):
    d.polygon(((1, 6), (30, 6), (26, 13), (5, 13)), fill=WOOD[1], outline=OUTLINE)
    d.line((3, 7, 28, 7), fill=WOOD[2])
    d.rectangle((8, 6, 23, 9), fill=WOOD[0])
    d.line((15, 6, 15, 9), fill=WOOD[1])
    d.line((4, 3, 12, 10), fill="#8a5a33", width=2)


@_register("swan_boat", (2, 1))
def _swan_boat(im, d, collision):
    d.polygon(((2, 8), (24, 8), (28, 12), (4, 13)), fill="#f6f2ea", outline=OUTLINE)
    d.ellipse((4, 4, 20, 11), fill="#f6f2ea", outline=OUTLINE)
    d.rectangle((7, 5, 17, 7), fill="#7fb8e0", outline=OUTLINE)
    d.line((24, 9, 26, 2), fill=OUTLINE, width=3)
    d.line((24, 9, 26, 2), fill="#f6f2ea", width=1)
    d.ellipse((24, 0, 29, 4), fill="#f6f2ea", outline=OUTLINE)
    d.point((30, 2), fill="#e98d3c")


@_register("icecream_cart", (1, 2))
def _icecream_cart(im, d, collision):
    collision[:] = [[False], [True]]
    d.line((8, 4, 8, 20), fill="#56606a")
    d.pieslice((0, 0, 15, 12), 180, 360, fill="#f4c24f", outline=OUTLINE)
    d.line((4, 6, 4, 2), fill="#e0607a")
    d.line((11, 6, 11, 2), fill="#e0607a")
    d.line((0, 6, 15, 6), fill=OUTLINE)
    _panel(d, (1, 18, 14, 27), "#f1ead8")
    d.rectangle((3, 20, 12, 22), fill="#7fb8e0")
    d.ellipse((5, 14, 9, 18), fill="#f2a6c0", outline=OUTLINE)
    for xx in (2, 10):
        d.ellipse((xx, 26, xx + 4, 30), fill="#33313a", outline=OUTLINE)


@_register("swing_set", (2, 2))
def _swing_set(im, d, collision):
    for xx in (2, 29):
        d.line((xx, 2, xx - 1, 30), fill="#d9534f", width=2)
    d.line((1, 2, 30, 2), fill="#d9534f", width=2)
    for xx in (9, 20):
        d.line((xx, 3, xx, 17), fill="#56606a")
        d.line((xx + 4, 3, xx + 4, 17), fill="#56606a")
        d.rectangle((xx - 1, 17, xx + 5, 19), fill="#f4c24f", outline=OUTLINE)
    d.line((0, 30, 31, 30), fill=OUTLINE)


@_register("slide", (2, 2))
def _slide(im, d, collision):
    d.line((4, 4, 4, 30), fill="#4f86b0", width=2)
    d.line((10, 4, 10, 30), fill="#4f86b0", width=2)
    for yy in range(8, 30, 5):
        d.line((4, yy, 10, yy), fill="#4f86b0")
    d.rectangle((3, 2, 12, 5), fill="#f4c24f", outline=OUTLINE)
    d.polygon(((11, 3), (15, 3), (31, 26), (31, 30), (27, 30)), fill="#e0607a", outline=OUTLINE)
    d.line((13, 4, 28, 26), fill="#f2a6c0")


@_register("seesaw", (2, 1))
def _seesaw(im, d, collision):
    d.polygon(((13, 15), (16, 8), (19, 15)), fill="#56606a", outline=OUTLINE)
    d.line((2, 12, 30, 5), fill=OUTLINE, width=3)
    d.line((2, 11, 30, 4), fill="#f4c24f")
    for xx, yy in ((4, 8), (27, 1)):
        d.line((xx, yy, xx, yy + 3), fill="#d9534f", width=2)


# ------------------------------------------------------------------------------------------------
# buildings
# ------------------------------------------------------------------------------------------------
def _register_building(kind, size, params=(), sized=None):
    def deco(fn):
        _BUILDING_SIZES[kind] = size
        _EXTRA_BUILDINGS[kind] = fn
        allowed = set(params)
        if sized:
            _SIZED_BUILDINGS[kind] = sized
            allowed |= {"w", "h", "door_x"}
        _BUILDING_PARAMS[kind] = allowed
        return fn
    return deco


@_register_building("old_house", (5, 3), params=("wall", "shutters"), sized=(4, 7, 3, 4))
def _old_house(im, door_col, wall="white", shutters="#3d7a5a"):
    """A Malleshwaram-style tiled house: Mangalore tiles, wooden veranda posts, red-oxide thinnai sit-outs."""
    d = ImageDraw.Draw(im)
    W, H = im.size
    wc = _color(wall)
    R = 16 if H <= 48 else 26
    _panel(d, (2, R - 2, W - 3, H - 6), wc)
    d.rectangle((3, R, W - 4, R + 4), fill=_shade(wc, -38))
    dx = door_col * 16
    for col in range(W // 16):
        if col == door_col:
            continue
        xx = col * 16 + 5
        if xx + 9 < W - 2 and xx > 2:
            d.rectangle((xx, R + 7, xx + 6, R + 15), fill="#3b3440", outline=OUTLINE)
            for k in (xx + 2, xx + 4):
                d.line((k, R + 8, k, R + 14), fill="#9aa0a6")
            d.rectangle((xx - 3, R + 7, xx - 1, R + 15), fill=shutters, outline=OUTLINE)
            d.rectangle((xx + 7, R + 7, xx + 9, R + 15), fill=shutters, outline=OUTLINE)
    if H > 48:
        for col in range(W // 16):
            xx = col * 16 + 5
            if 2 < xx and xx + 9 < W - 2:
                d.rectangle((xx, R - 13, xx + 6, R - 7), fill="#3b3440", outline=OUTLINE)
                d.line((xx + 3, R - 12, xx + 3, R - 8), fill="#9aa0a6")
    d.rectangle((3, H - 12, W - 4, H - 10), fill="#b5533c")
    for a, b in ((3, dx - 2), (dx + 17, W - 4)):
        if b - a > 5:
            _panel(d, (a, H - 12, b, H - 6), "#a8463b")
            d.line((a + 1, H - 11, b - 1, H - 11), fill="#c86a5d")
    _panel(d, (0, H - 6, W - 1, H - 1), "#b9b0a0")
    d.line((1, H - 5, W - 2, H - 5), fill="#d6cfc2")
    _tile_roof(im, (0, 0, W - 1, R + 4) if H <= 48 else (0, 0, W - 1, 14))
    if H > 48:
        _tile_roof(im, (0, R - 4, W - 1, R + 4))
    d.line((2, R + 4, W - 3, R + 4), fill=WOOD[1])
    posts = {3, W - 6}
    if 0 < door_col:
        posts.add(dx - 3)
    if door_col < W // 16 - 1:
        posts.add(dx + 17)
    for xx in posts:
        _panel(d, (xx, R + 5, xx + 2, H - 7), WOOD[1])
        d.line((xx - 1, R + 5, xx + 3, R + 5), fill=OUTLINE)
    return [(door_col, im.height // 16 - 1)], "wood"


@_register_building("apartment", (5, 5), params=("wall", "accent"), sized=(4, 7, 4, 6))
def _apartment(im, door_col, wall="#e8dcc0", accent="#c96b5a"):
    d = ImageDraw.Draw(im)
    W, H = im.size
    wc, ac = _color(wall), _color(accent)
    for xx in (5, W - 21):
        im.alpha_composite(prop("water_tank")[0], (xx, 0))
    d.line((W // 2 + 4, 1, W // 2 + 4, 7), fill=OUTLINE)
    d.ellipse((W // 2, 0, W // 2 + 7, 5), fill="#d6d3cc", outline=OUTLINE)
    _panel(d, (2, 8, W - 3, H - 2), wc)
    d.rectangle((1, 6, W - 2, 9), fill=STONE[2], outline=OUTLINE)
    floors = list(range(11, H - 22, 14))
    for i, fy in enumerate(floors):
        for col in range(W // 16):
            xx = col * 16
            _window(d, (xx + 4, fy, xx + 11, fy + 7), True)
            if (col + i) % 2 == 0:
                d.rectangle((xx + 2, fy + 6, xx + 13, fy + 10), fill=ac, outline=OUTLINE)
                for k in range(xx + 4, xx + 13, 3):
                    d.line((k, fy + 7, k, fy + 9), fill=_shade(ac, -35))
                if (col * 7 + i * 3) % 3 == 0:
                    d.line((xx + 3, fy + 2, xx + 12, fy + 2), fill=OUTLINE)
                    for k, c in ((xx + 4, "#e0607a"), (xx + 7, "#f4c24f"), (xx + 10, "#7fb8e0")):
                        d.rectangle((k, fy + 2, k + 1, fy + 5), fill=c)
                else:
                    d.ellipse((xx + 2, fy + 3, xx + 5, fy + 6), fill="#5fa65b", outline=OUTLINE)
            d.line((xx + 1, fy + 11, xx + 14, fy + 11), fill=_shade(wc, -30))
    gy = H - 18
    d.rectangle((3, gy, W - 4, H - 3), fill="#4a4550")
    for col in range(W // 16 + 1):
        xx = min(col * 16, W - 5)
        _panel(d, (xx, gy - 1, xx + 3, H - 3), wc)
    for col in range(W // 16):
        if col != door_col and col % 2 == 0:
            im.alpha_composite(prop("scooter_side", color=("#d9534f", "#4f86b0", "#f1ead8")[col % 3])[0], (col * 16 + 1, gy + 2))
    d.line((2, gy - 2, W - 3, gy - 2), fill=_shade(wc, -40))
    return [(door_col, im.height // 16 - 1)], "glass"


@_register_building("ranger_hut", (4, 3))
def _ranger_hut(im, door_col):
    d = ImageDraw.Draw(im)
    W, H = im.size
    _panel(d, (3, 16, W - 4, H - 3), WOOD[0])
    for yy in range(18, H - 4, 4):
        d.line((4, yy, W - 5, yy), fill=WOOD[1])
        d.line((4, yy + 1, W - 5, yy + 1), fill=WOOD[2])
    for xx in (8, W - 20):
        _window(d, (xx, 24, xx + 9, 33), True)
        d.rectangle((xx - 2, 24, xx - 1, 33), fill="#3f7a4a")
        d.rectangle((xx + 10, 24, xx + 11, 33), fill="#3f7a4a")
    _tile_roof(im, (0, 1, W - 1, 20))
    _panel(d, (14, 14, W - 15, 21), "#3f7a4a")
    _label(im, "RANGER", (15, 15, W - 16, 20), CREAM)
    d.rectangle((W - 12, H - 12, W - 3, H - 3), fill=WOOD[1], outline=OUTLINE)
    for yy in (H - 10, H - 7, H - 4):
        d.line((W - 11, yy, W - 4, yy), fill="#d9b27c")
    return [(door_col, 2)], "wood"


@_register_building("village_hut", (3, 3), params=("roof", "wall"), sized=(3, 5, 3, 3))
def _village_hut(im, door_col, roof="thatch", wall="#c9a46a"):
    d = ImageDraw.Draw(im)
    W, H = im.size
    wc = _color(wall)
    _panel(d, (3, 18, W - 4, H - 3), wc)
    d.rectangle((4, H - 9, W - 5, H - 4), fill="#a8463b")
    d.line((4, H - 10, W - 5, H - 10), fill="#f1e7ce")
    for col in range(W // 16):
        if col != door_col:
            xx = col * 16 + 5
            d.rectangle((xx, 25, xx + 5, 30), fill="#3b3440", outline=OUTLINE)
            d.line((xx + 2, 26, xx + 2, 29), fill=WOOD[1])
    if roof == "thatch":
        d.polygon(((0, 22), (8, 2), (W - 9, 2), (W - 1, 22)), fill="#c9a24e", outline=OUTLINE)
        for yy in range(5, 22, 3):
            d.line((3, yy, W - 4, yy), fill="#a8823a")
        for xx in range(3, W - 3, 4):
            d.line((xx, 20, xx + 1, 23), fill="#8a6a2e")
        d.line((9, 3, W - 10, 3), fill="#e6c472")
    else:
        _tile_roof(im, (0, 2, W - 1, 22))
    return [(door_col, 2)], "wood"


@_register_building("red_library", (7, 5))
def _red_library(im, door_col):
    """Cubbon Park's red Gothic library: terracotta walls, white trim, lancet windows, a corner turret."""
    d = ImageDraw.Draw(im)
    W, H = im.size
    red, trim = "#b8453a", "#f1e7ce"
    _panel(d, (6, 24, W - 7, H - 6), red)
    for xx in range(12, W - 14, 14):
        _arch(d, (xx, 34, xx + 7, 52), "#4f6f86", trim)
        d.line((xx + 3, 40, xx + 3, 52), fill=trim)
        _arch(d, (xx, 56, xx + 7, 70), "#4f6f86", trim)
    d.rectangle((6, 52, W - 7, 54), fill=trim)
    _panel(d, (2, 18, W - 3, 25), "#9c3a31")
    for xx in range(3, W - 3, 6):
        d.rectangle((xx, 15, xx + 3, 18), fill=trim, outline=OUTLINE)
    d.line((3, 21, W - 4, 21), fill=trim)
    # central porch with a pointed gable
    _panel(d, (40, 30, 71, H - 4), "#c5584b")
    d.polygon(((38, 32), (56, 12), (73, 32)), fill=red, outline=OUTLINE)
    d.polygon(((44, 30), (56, 18), (67, 30)), fill=trim)
    d.ellipse((52, 22, 59, 29), fill="#4f6f86", outline=OUTLINE)
    _arch(d, (48, 50, 63, H - 4), "#3b3440", trim)
    _columns(d, (42, 66), 36, H - 5, trim, 2)
    # corner turret with a slate cone
    for xx in (0, W - 18):
        _panel(d, (xx, 16, xx + 17, H - 4), "#a63d33")
        d.polygon(((xx - 1, 17), (xx + 8, 0), (xx + 18, 17)), fill="#5d5f6e", outline=OUTLINE)
        d.line((xx + 8, 2, xx + 3, 16), fill="#7d8090")
        _arch(d, (xx + 5, 26, xx + 11, 40), "#4f6f86", trim)
        _arch(d, (xx + 5, 50, xx + 11, 64), "#4f6f86", trim)
    _steps(d, (44, H - 6, 67, H - 1), "#c9bea8")
    return [], "none"


@_register_building("yali_gallery", (7, 3))
def _yali_gallery(im, door_col):
    """A ruined temple hall: carved back wall, a cracked roof slab and four rearing-yali pillars."""
    d = ImageDraw.Draw(im)
    W, H = im.size
    _panel(d, (2, 8, W - 3, H - 5), "#9d917b")
    d.rectangle((4, 12, W - 5, H - 8), fill="#4f4540")
    for xx in range(10, W - 10, 28):
        d.rectangle((xx + 6, 16, xx + 16, 32), fill="#6a5e55", outline="#3a322f")
        d.polygon(((xx + 8, 30), (xx + 11, 19), (xx + 14, 30)), fill="#8a7d6d")
        d.ellipse((xx + 9, 17, xx + 13, 21), fill="#8a7d6d")
    # roof slabs, the last one fallen in
    for xx in range(0, W - 30, 20):
        _panel(d, (xx, 2, xx + 20, 9), "#b8ac94")
        d.line((xx + 2, 3, xx + 18, 3), fill="#d6cbb4")
    d.polygon(((W - 30, 2), (W - 12, 6), (W - 14, 12), (W - 32, 9)), fill="#a69a82", outline=OUTLINE)
    d.line((W - 28, 4, W - 15, 7), fill="#d6cbb4")
    pillar, _ = prop("yali_pillar")
    for xx in (6, 34, 62, 90):
        if xx + 16 <= W:
            im.alpha_composite(pillar, (xx, H - 33))
    d.rectangle((0, H - 5, W - 1, H - 1), fill="#b9ad96", outline=OUTLINE)
    d.line((1, H - 4, W - 2, H - 4), fill="#d6cbb4")
    d.ellipse((W - 10, H - 9, W - 4, H - 5), fill="#8d9662")
    return [], "none"


@_register_building("glass_tower", (5, 6), params=("glass", "sign", "trim"), sized=(4, 8, 4, 7))
def _glass_tower(im, door_col, glass="#4f86a8", sign="TECH PARK", trim="#c9d2d4"):
    d = ImageDraw.Draw(im)
    W, H = im.size
    gc, tc = _color(glass), _color(trim)
    _panel(d, (2, 10, W - 3, H - 10), gc)
    for yy in range(14, H - 14, 8):
        d.line((3, yy, W - 4, yy), fill=_shade(gc, -30))
        d.line((3, yy + 1, W - 4, yy + 1), fill=_shade(gc, 18))
    for xx in range(10, W - 4, 10):
        d.line((xx, 11, xx, H - 11), fill=_shade(gc, -22))
    for k in range(0, W + H, 22):
        d.line((k, 11, k - 20, 31), fill=_shade(gc, 45))
        d.line((k + 3, 11, k - 17, 31), fill=_shade(gc, 25))
    d.polygon(((2, 11), (W // 3, 11), (2, H // 2)), fill=_shade(gc, 14))
    _panel(d, (W - 14, 6, W - 3, H - 10), tc)
    for yy in range(10, H - 12, 6):
        d.line((W - 12, yy, W - 6, yy), fill=_shade(tc, -25))
    _panel(d, (6, 1, W - 18, 10), "#3b3f55")
    _label(im, sign, (8, 3, W - 20, 8), CREAM)
    _panel(d, (0, H - 12, W - 1, H - 8), tc)
    d.rectangle((3, H - 8, W - 4, H - 2), fill=_shade(gc, -40))
    _steps(d, (door_col * 16 - 4, H - 3, door_col * 16 + 19, H - 1), STONE[0])
    return [(door_col, im.height // 16 - 1)], "glass"


# ------------------------------------------------------------------------------------------------
# interiors: things hung on the two-tile wall band, then furniture
# ------------------------------------------------------------------------------------------------
@_register("wall_window", (1, 1), params=("curtain",))
def _wall_window(im, d, collision, curtain="#d9534f"):
    _window(d, (2, 2, 13, 12), True)
    c = _color(curtain)
    d.polygon(((1, 1), (5, 1), (3, 13), (1, 13)), fill=c, outline=OUTLINE)
    d.polygon(((14, 1), (10, 1), (12, 13), (14, 13)), fill=c, outline=OUTLINE)
    d.line((0, 1, 15, 1), fill=WOOD[1], width=2)


@_register("calendar", (1, 1))
def _calendar(im, d, collision):
    d.line((8, 0, 8, 2), fill=OUTLINE)
    d.rectangle((3, 2, 12, 14), fill="#f6efe0", outline=OUTLINE)
    d.rectangle((4, 3, 11, 8), fill="#e98d3c")
    d.ellipse((6, 3, 9, 7), fill="#f4c24f")
    d.point((7, 5), fill="#d9534f")
    for yy in (10, 12):
        for xx in range(4, 12, 2):
            d.point((xx, yy), fill="#7c7768")


@_register("wall_clock", (1, 1))
def _wall_clock(im, d, collision):
    d.ellipse((2, 2, 13, 13), fill=CREAM, outline=OUTLINE)
    d.ellipse((3, 3, 12, 12), outline=WOOD[1])
    d.line((7, 7, 7, 4), fill=OUTLINE)
    d.line((7, 7, 10, 8), fill=OUTLINE)


@_register("photo_frame", (1, 1))
def _photo_frame(im, d, collision):
    # a garlanded portrait of a grandparent, as in every Bengaluru living room
    d.rectangle((3, 2, 12, 13), fill=WOOD[1], outline=OUTLINE)
    d.rectangle((5, 4, 10, 11), fill="#d9cdb5")
    d.ellipse((6, 5, 9, 8), fill="#8a7666")
    d.rectangle((6, 8, 9, 11), fill="#f1e7ce")
    d.arc((3, 6, 12, 15), 0, 180, fill="#f4a23c", width=2)


@_register("poster", (1, 1), params=("color",))
def _poster(im, d, collision, color="#4f86b0"):
    c = _color(color)
    d.rectangle((2, 1, 13, 14), fill=c, outline=OUTLINE)
    d.ellipse((5, 3, 10, 8), fill=CREAM)
    d.line((7, 8, 7, 11), fill=CREAM)
    d.line((4, 12, 11, 12), fill=_shade(c, 50))
    d.point((2, 1), fill="#9aa0a6")
    d.point((13, 1), fill="#9aa0a6")


@_register("menu_board", (2, 1))
def _menu_board(im, d, collision):
    _panel(d, (1, 0, 30, 15), "#2f4a3a")
    for i, (item, price) in enumerate((("IDLI", "30"), ("DOSA", "60"))):
        im.alpha_composite(text(item, _color(CREAM)), (3, 2 + i * 7))
        im.alpha_composite(text(price, _color("#f4c24f")), (21, 2 + i * 7))


@_register("blackboard", (2, 1))
def _blackboard(im, d, collision):
    _panel(d, (0, 0, 31, 14), WOOD[1])
    d.rectangle((2, 2, 29, 12), fill="#2f4a3a")
    im.alpha_composite(text("A+B=?", _color(CREAM)), (4, 3))
    d.line((24, 6, 28, 9), fill="#f4c24f")
    d.line((4, 10, 18, 10), fill="#a8c4b0")
    d.rectangle((10, 13, 15, 14), fill=CREAM)


@_register("whiteboard", (2, 1))
def _whiteboard(im, d, collision):
    _panel(d, (0, 0, 31, 14), "#c9d2d4")
    d.rectangle((2, 2, 29, 12), fill="#f8f8f2")
    d.line([(4, 10), (9, 6), (13, 8), (18, 4), (22, 5)], fill="#4f86b0")
    d.rectangle((24, 4, 28, 9), outline="#d9534f")
    d.line((4, 4, 12, 4), fill="#2f2b36")


@_register("tube_light", (1, 1))
def _tube_light(im, d, collision):
    d.rectangle((1, 5, 14, 8), fill="#d6d3cc", outline=OUTLINE)
    d.line((2, 6, 13, 6), fill="#ffffff")
    d.line((2, 9, 13, 9), fill=(255, 255, 230, 90))


@_register("ac_unit", (2, 1))
def _ac_unit(im, d, collision):
    d.rounded_rectangle((1, 2, 30, 11), radius=2, fill="#f2f2ec", outline=OUTLINE)
    d.line((3, 9, 28, 9), fill="#b9bcb8")
    d.point((26, 4), fill="#6fbf73")


@_register("wall_shelf", (1, 1))
def _wall_shelf(im, d, collision):
    d.rectangle((0, 10, 15, 12), fill=WOOD[0], outline=OUTLINE)
    _vessel(d, 1, 3, 6)
    d.rectangle((9, 4, 13, 10), fill="#cfe3e6", outline=OUTLINE)
    d.rectangle((10, 6, 12, 9), fill="#d9a35c")


@_register("mirror", (1, 1))
def _mirror(im, d, collision):
    d.ellipse((3, 1, 12, 14), fill=WOOD[1], outline=OUTLINE)
    d.ellipse((5, 3, 10, 12), fill="#bfe0e6")
    d.line((6, 5, 7, 4), fill="#ffffff")


@_register("map_poster", (2, 1))
def _map_poster(im, d, collision):
    _panel(d, (1, 0, 30, 14), "#f1ead8")
    d.polygon(((5, 3), (14, 2), (22, 4), (26, 9), (18, 12), (8, 11), (4, 7)), fill="#a7cf8a", outline="#6a8a5a")
    d.line([(8, 5), (14, 7), (20, 6), (24, 9)], fill="#8d4ab8")
    d.line([(12, 3), (13, 8), (15, 11)], fill="#49a879")
    for xx, yy in ((14, 7), (20, 6), (8, 5)):
        d.point((xx, yy), fill="#d9534f")


@_register("trophy_shelf", (2, 1))
def _trophy_shelf(im, d, collision):
    d.rectangle((0, 11, 31, 13), fill=WOOD[0], outline=OUTLINE)
    for xx, h in ((3, 8), (11, 10), (20, 7), (26, 9)):
        d.rectangle((xx + 1, 11 - 2, xx + 4, 11), fill="#b07f2a")
        d.polygon(((xx, 11 - h), (xx + 5, 11 - h), (xx + 4, 11 - h + 4), (xx + 1, 11 - h + 4)), fill="#f4c24f", outline=OUTLINE)


@_register("safety_poster", (1, 1))
def _safety_poster(im, d, collision):
    d.rectangle((2, 1, 13, 14), fill="#f2d14c", outline=OUTLINE)
    d.polygon(((7, 3), (11, 10), (4, 10)), fill="#2f2b36")
    d.line((7, 5, 7, 7), fill="#f2d14c")
    d.point((7, 9), fill="#f2d14c")
    d.line((3, 12, 12, 12), fill="#2f2b36")


@_register("banner", (1, 2), params=("color",))
def _banner(im, d, collision, color="#6aa65e"):
    c = _color(color)
    d.line((1, 1, 14, 1), fill=WOOD[1], width=2)
    d.polygon(((3, 2), (12, 2), (12, 26), (8, 22), (3, 26)), fill=c, outline=OUTLINE)
    d.line((5, 4, 5, 22), fill=_shade(c, 35))
    d.ellipse((5, 8, 10, 13), fill=CREAM, outline=OUTLINE)


@_register("fridge", (1, 2))
def _fridge(im, d, collision):
    _panel(d, (1, 1, 14, 30), "#d8dfe0")
    d.line((2, 11, 13, 11), fill="#9aa5a8")
    d.line((12, 4, 12, 8), fill="#6f7a7e")
    d.line((12, 14, 12, 20), fill="#6f7a7e")
    d.rectangle((4, 3, 7, 6), fill="#f4c24f")
    d.rectangle((5, 15, 8, 18), fill="#e0607a")


@_register("almirah", (1, 2))
def _almirah(im, d, collision):
    _panel(d, (1, 1, 14, 30), "#8e9aa6")
    d.line((7, 3, 7, 28), fill="#5f6b78")
    d.line((8, 3, 8, 28), fill="#b2bcc6")
    for xx in (5, 10):
        d.line((xx, 13, xx, 16), fill="#d6b04c")
    d.line((2, 2, 13, 2), fill="#c4ccd4")


@_register("oonjal", (2, 2))
def _oonjal(im, d, collision):
    # the wooden swing that hangs in the hall of every old house
    for xx in (3, 28):
        d.line((xx, 0, xx, 18), fill="#7c7768")
        for yy in range(1, 18, 3):
            d.point((xx, yy), fill="#b9bcb8")
    _panel(d, (0, 17, 31, 23), WOOD[0])
    d.line((2, 18, 29, 18), fill=WOOD[2])
    for xx in range(4, 28, 5):
        d.point((xx, 21), fill="#d6b04c")
    d.rectangle((6, 15, 12, 18), fill="#d9534f", outline=OUTLINE)
    d.line((0, 28, 31, 28), fill=(40, 30, 40, 80))


@_register("sink", (1, 1))
def _sink(im, d, collision):
    _panel(d, (1, 4, 14, 13), STEEL[0])
    d.ellipse((3, 5, 12, 11), fill=STEEL[1])
    d.line((8, 1, 8, 5), fill="#6f7a7e", width=2)
    d.line((8, 1, 11, 1), fill="#6f7a7e", width=2)


@_register("grinder", (1, 1))
def _grinder(im, d, collision):
    _panel(d, (2, 7, 13, 14), "#e8e2d4")
    d.ellipse((3, 2, 12, 9), fill=STEEL[0], outline=OUTLINE)
    d.ellipse((5, 3, 10, 7), fill="#f1ead8")
    d.line((7, 0, 7, 4), fill=OUTLINE, width=2)
    d.point((11, 11), fill="#d9534f")


@_register("gas_cylinder", (1, 1))
def _gas_cylinder(im, d, collision):
    d.rounded_rectangle((4, 4, 11, 15), radius=3, fill="#c8443a", outline=OUTLINE)
    d.rectangle((6, 1, 9, 4), fill="#9aa0a6", outline=OUTLINE)
    d.line((5, 6, 5, 13), fill="#e8766a")
    d.line((4, 10, 11, 10), fill="#8f2f2a")


@_register("water_filter", (1, 1))
def _water_filter(im, d, collision):
    _panel(d, (3, 1, 12, 13), "#e9eef2")
    d.rectangle((5, 3, 10, 7), fill="#7fb8e0")
    d.line((10, 10, 13, 10), fill="#4f86b0")
    d.point((13, 11), fill="#7fb8e0")
    d.rectangle((2, 13, 13, 15), fill="#9aa5a8", outline=OUTLINE)


@_register("shoe_rack", (1, 1))
def _shoe_rack(im, d, collision):
    _panel(d, (1, 4, 14, 15), WOOD[0])
    for yy, cs in ((6, ("#3d6ea8", "#c45b4f")), (11, ("#2f2b36", "#e9b945"))):
        d.line((2, yy + 3, 13, yy + 3), fill=WOOD[1])
        for i, c in enumerate(cs):
            d.rectangle((3 + i * 6, yy, 7 + i * 6, yy + 2), fill=c, outline=OUTLINE)


@_register("sack", (1, 1), params=("grain",))
def _sack(im, d, collision, grain="#f1e7ce"):
    d.polygon(((2, 15), (3, 5), (12, 5), (13, 15)), fill="#c9a865", outline=OUTLINE)
    d.ellipse((2, 2, 13, 8), fill="#b8954f", outline=OUTLINE)
    d.ellipse((4, 3, 11, 7), fill=_color(grain))
    d.line((5, 10, 10, 10), fill="#a8823a")
    d.line((5, 12, 9, 12), fill="#a8823a")


@_register("jar_shelf", (2, 1))
def _jar_shelf(im, d, collision):
    _panel(d, (0, 2, 31, 15), WOOD[0])
    d.rectangle((1, 3, 30, 13), fill=WOOD[1])
    for i, xx in enumerate(range(2, 30, 6)):
        c = ("#f4c24f", "#e0607a", "#c99a5e", "#7fbf62", "#f08a3c")[i % 5]
        d.rectangle((xx, 5, xx + 4, 12), fill="#dfeff0", outline=OUTLINE)
        d.rectangle((xx + 1, 8, xx + 3, 11), fill=c)
        d.rectangle((xx, 4, xx + 4, 5), fill="#d9534f")


@_register("weighing_scale", (1, 1))
def _weighing_scale(im, d, collision):
    d.line((8, 3, 8, 13), fill=OUTLINE, width=2)
    d.line((2, 4, 14, 4), fill="#b07f2a", width=2)
    for xx in (3, 13):
        d.line((xx, 5, xx, 9), fill="#7c7768")
        d.pieslice((xx - 3, 6, xx + 3, 12), 0, 180, fill="#d6b04c", outline=OUTLINE)
    d.rectangle((4, 13, 12, 15), fill=WOOD[1], outline=OUTLINE)


@_register("counter_wood", (2, 1))
def _counter_wood(im, d, collision):
    _panel(d, (0, 3, 31, 15), WOOD[0])
    d.rectangle((1, 3, 30, 5), fill=WOOD[2])
    for xx in (8, 16, 24):
        d.line((xx, 7, xx, 14), fill=WOOD[1])
    d.rectangle((3, 0, 8, 3), fill="#cfe3e6", outline=OUTLINE)
    d.rectangle((22, 1, 28, 3), fill="#5d6470", outline=OUTLINE)


@_register("steel_table", (1, 1))
def _steel_table(im, d, collision):
    d.line((8, 6, 8, 14), fill=STEEL[1], width=2)
    d.ellipse((4, 13, 12, 15), fill=STEEL[1], outline=OUTLINE)
    d.ellipse((0, 2, 15, 8), fill=STEEL[0], outline=OUTLINE)
    d.ellipse((2, 3, 13, 6), fill=STEEL[2])
    d.rectangle((4, 2, 6, 5), fill="#dfeff0", outline=OUTLINE)
    d.point((5, 3), fill="#c68a4c")
    d.ellipse((8, 2, 12, 5), fill=STEEL[1], outline=OUTLINE)
    d.point((10, 3), fill=CREAM)


@_register("kaapi_boiler", (1, 1))
def _kaapi_boiler(im, d, collision):
    _vessel(d, 2, 4, 12, True)
    d.line((12, 9, 15, 9), fill=OUTLINE)
    d.rectangle((3, 13, 12, 15), fill=WOOD[1], outline=OUTLINE)


@_register("specimen_tank", (1, 2))
def _specimen_tank(im, d, collision):
    _panel(d, (1, 24, 14, 31), STEEL[1])
    d.rectangle((2, 3, 13, 24), fill="#9fd8d0", outline=OUTLINE)
    d.line((3, 4, 3, 22), fill="#e4f6f0")
    d.line((8, 22, 8, 12), fill="#4b8263")
    d.ellipse((4, 9, 8, 13), fill="#71ae7b", outline=OUTLINE)
    d.ellipse((8, 7, 12, 11), fill="#a3ce7d", outline=OUTLINE)
    for yy in (6, 15, 19):
        d.point((10, yy), fill="#ffffff")
    _panel(d, (1, 0, 14, 4), STEEL[0])


@_register("potted_palm", (1, 2))
def _potted_palm(im, d, collision):
    collision[:] = [[False], [True]]
    d.polygon(((4, 23), (12, 23), (11, 31), (5, 31)), fill="#c57c57", outline=OUTLINE)
    _panel(d, (3, 22, 12, 24), "#dc9869")
    d.line((8, 22, 8, 10), fill=GRASS[3])
    for pts in (((8, 10), (1, 6), (0, 10)), ((8, 10), (15, 6), (15, 11)), ((8, 11), (3, 15), (2, 19)),
                ((8, 11), (13, 15), (14, 19)), ((8, 9), (6, 1), (10, 2))):
        d.polygon(pts, fill=GRASS[1], outline=OUTLINE)


@_register("server_rack", (1, 2))
def _server_rack(im, d, collision):
    _panel(d, (1, 1, 14, 30), "#3b3f4a")
    for yy in range(4, 28, 4):
        d.rectangle((3, yy, 12, yy + 2), fill="#2a2d36")
        d.point((4, yy + 1), fill="#6fbf73" if yy % 8 else "#f4c24f")
        d.point((6, yy + 1), fill="#6fbf73")
        d.line((8, yy + 1, 11, yy + 1), fill="#55596a")


@_register("bean_bag", (1, 1), params=("color",))
def _bean_bag(im, d, collision, color="#f08a3c"):
    c = _color(color)
    d.ellipse((1, 4, 14, 15), fill=_shade(c, -30), outline=OUTLINE)
    d.ellipse((2, 3, 13, 12), fill=c)
    d.arc((4, 5, 11, 10), 180, 300, fill=_shade(c, 45))


@_register("foosball", (2, 1))
def _foosball(im, d, collision):
    for xx in (3, 27):
        d.line((xx, 10, xx, 15), fill=OUTLINE, width=2)
    _panel(d, (0, 2, 31, 11), WOOD[1])
    d.rectangle((2, 3, 29, 10), fill="#5fa65b")
    for i, xx in enumerate(range(6, 28, 5)):
        d.line((xx, 1, xx, 12), fill="#9aa0a6")
        d.rectangle((xx - 1, 5, xx + 1, 7), fill="#d9534f" if i % 2 else "#4f86b0")
    d.point((16, 6), fill=CREAM)


@_register("coffee_machine", (1, 1))
def _coffee_machine(im, d, collision):
    _panel(d, (2, 0, 13, 13), "#3b3f4a")
    d.rectangle((4, 2, 11, 5), fill="#7fb8e0")
    d.rectangle((5, 8, 10, 12), fill="#2a2d36")
    d.rectangle((6, 10, 9, 12), fill=CREAM, outline=OUTLINE)
    d.rectangle((1, 13, 14, 15), fill="#9aa5a8", outline=OUTLINE)


@_register("water_cooler", (1, 1))
def _water_cooler(im, d, collision):
    _panel(d, (3, 6, 12, 15), "#e9eef2")
    d.rounded_rectangle((4, 0, 11, 7), radius=2, fill="#9fd0e8", outline=OUTLINE)
    d.line((6, 1, 6, 5), fill="#dff3f0")
    d.point((5, 10), fill="#4f86b0")
    d.point((10, 10), fill="#d9534f")


@_register("glass_partition_h", (1, 1))
def _glass_partition_h(im, d, collision):
    d.rectangle((0, 2, 15, 13), fill=(190, 228, 230, 150), outline="#8aa0a8")
    d.line((3, 3, 7, 12), fill=(255, 255, 255, 180))
    d.line((0, 13, 15, 13), fill="#5d6470", width=2)


@_register("glass_partition_v", (1, 1))
def _glass_partition_v(im, d, collision):
    d.rectangle((5, 0, 10, 15), fill=(190, 228, 230, 150), outline="#8aa0a8")
    d.line((7, 2, 8, 12), fill=(255, 255, 255, 180))


@_register("printer", (1, 1))
def _printer(im, d, collision):
    _panel(d, (1, 5, 14, 13), "#d8dfe0")
    d.rectangle((4, 2, 11, 6), fill="#f8f8f2", outline=OUTLINE)
    d.rectangle((3, 9, 12, 10), fill="#5d6470")
    d.point((12, 7), fill="#6fbf73")
    d.rectangle((2, 13, 13, 15), fill="#9aa5a8", outline=OUTLINE)


@_register("workstation", (2, 1))
def _workstation(im, d, collision):
    for xx in (2, 28):
        d.line((xx, 9, xx, 15), fill=OUTLINE, width=2)
    _panel(d, (0, 7, 31, 11), "#e9e3d6")
    for xx in (4, 18):
        _panel(d, (xx, 0, xx + 10, 7), "#3b3f4a")
        d.rectangle((xx + 2, 1, xx + 8, 5), fill="#7fb8e0")
        d.line((xx + 3, 2, xx + 5, 2), fill="#dff3f0")
    d.rectangle((12, 8, 17, 9), fill="#c9d2d4")
    d.ellipse((26, 7, 29, 10), fill="#f1e7ce", outline=OUTLINE)


@_register("bleachers", (3, 2))
def _bleachers(im, d, collision):
    for i, yy in enumerate(range(1, 30, 7)):
        _panel(d, (0, yy, 47, yy + 6), "#b9b6ad")
        for xx in range(2, 46, 4):
            d.rectangle((xx, yy + 1, xx + 2, yy + 3), fill=("#4f86b0", "#d9534f", "#f4c24f")[(xx // 4 + i) % 3])
        d.line((1, yy + 5, 46, yy + 5), fill="#8c887f")


@_register("practice_net", (2, 2))
def _practice_net(im, d, collision):
    for xx in (1, 30):
        d.line((xx, 0, xx, 30), fill="#56606a", width=2)
    d.line((1, 1, 30, 1), fill="#56606a", width=2)
    for xx in range(3, 30, 3):
        d.line((xx, 2, xx, 29), fill=(240, 240, 230, 120))
    for yy in range(4, 29, 3):
        d.line((2, yy, 29, yy), fill=(240, 240, 230, 120))
    im.alpha_composite(prop("cricket_stumps")[0], (8, 14))


@_register("scoreboard", (3, 2))
def _scoreboard(im, d, collision):
    _panel(d, (0, 0, 47, 26), "#2f3a33")
    im.alpha_composite(text("RUNS 186", _color("#f4c24f")), (4, 3))
    im.alpha_composite(text("WKTS 4", _color(CREAM)), (4, 11))
    im.alpha_composite(text("OVR 19.2", _color("#9fd0dc")), (4, 18))
    for xx in (8, 38):
        d.line((xx, 26, xx, 31), fill="#56606a", width=2)


@_register("throne", (2, 2))
def _throne(im, d, collision):
    _panel(d, (4, 2, 27, 26), "#b07f2a")
    d.rectangle((7, 5, 24, 18), fill="#8d3a5a")
    d.polygon(((6, 2), (16, -3), (26, 2)), fill="#d6b04c", outline=OUTLINE)
    _panel(d, (2, 16, 29, 26), "#c9932f")
    d.rectangle((6, 17, 25, 22), fill="#a84a6a")
    for xx in (3, 26):
        _panel(d, (xx, 12, xx + 3, 29), "#d6b04c")
    d.ellipse((13, 7, 18, 12), fill="#f4d481", outline=OUTLINE)


@_register("armor_stand", (1, 2))
def _armor_stand(im, d, collision):
    collision[:] = [[False], [True]]
    d.ellipse((5, 1, 10, 7), fill="#9aa5a8", outline=OUTLINE)
    d.rectangle((6, 4, 9, 5), fill="#2f2b36")
    _panel(d, (3, 7, 12, 18), "#b9c2c6")
    d.line((7, 8, 7, 17), fill="#8a959a")
    d.rectangle((4, 18, 11, 24), fill="#8d3a5a", outline=OUTLINE)
    d.line((13, 2, 13, 26), fill="#7c7768")
    d.polygon(((12, 1), (14, 1), (13, -2)), fill="#d6d3cc")
    d.rectangle((3, 25, 12, 30), fill=WOOD[1], outline=OUTLINE)


@_register("vase", (1, 1))
def _vase(im, d, collision):
    d.polygon(((5, 4), (10, 4), (13, 9), (10, 15), (5, 15), (2, 9)), fill="#4f86b0", outline=OUTLINE)
    d.line((4, 9, 11, 9), fill="#f1e7ce")
    d.line((5, 2, 10, 2), fill=OUTLINE)
    for xx, c in ((5, "#e0607a"), (8, "#f4c24f"), (11, "#f1e7ce")):
        d.point((xx, 1), fill=c)
        d.point((xx - 1, 1), fill=c)


@_register("showcase", (2, 1))
def _showcase(im, d, collision):
    _panel(d, (0, 0, 31, 15), WOOD[1])
    d.rectangle((2, 2, 29, 13), fill="#bfe0e6")
    d.line((16, 2, 16, 13), fill=WOOD[1])
    d.line((2, 8, 29, 8), fill=WOOD[0])
    for xx, c in ((4, "#f4c24f"), (9, "#e0607a"), (19, STEEL[0]), (24, STEEL[0])):
        d.rectangle((xx, 4, xx + 3, 7), fill=c, outline=OUTLINE)
    for xx in (5, 11, 20, 25):
        d.ellipse((xx, 9, xx + 3, 12), fill="#d6b04c", outline=OUTLINE)


@_register("stone_reader", (2, 2))
def _stone_reader(im, d, collision):
    _panel(d, (1, 4, 30, 30), STEEL[0])
    d.rectangle((3, 6, 14, 18), fill="#2f3a44", outline=OUTLINE)
    d.line([(4, 13), (6, 13), (7, 9), (9, 15), (11, 11), (13, 11)], fill="#c3eb9c")
    d.ellipse((17, 7, 28, 18), fill="#9fd8d0", outline=OUTLINE)
    d.polygon(((20, 15), (22, 10), (25, 11), (26, 15)), fill="#8d8378", outline=OUTLINE)
    d.point((22, 9), fill="#ffffff")
    for xx, c in ((5, "#e7ad65"), (9, "#a8d679"), (13, "#d9534f")):
        d.ellipse((xx, 21, xx + 2, 23), fill=c)
    d.rectangle((17, 21, 28, 26), fill="#5d6470", outline=OUTLINE)
    d.rectangle((3, 0, 28, 4), fill="#635c99", outline=OUTLINE)
    im.alpha_composite(text("STONE", _color(CREAM)), (6, 0))


@_register("rug_long", (3, 2), params=("color",), decal=True)
def _rug_long(im, d, collision, color="#4f6f9f"):
    _walkable(collision)
    c = _color(color)
    _panel(d, (1, 2, 46, 29), c)
    d.rectangle((4, 5, 43, 26), outline="#efc382")
    d.rectangle((7, 8, 40, 23), outline=_shade(c, 40))
    for cx in (14, 24, 34):
        d.polygon(((cx, 10), (cx + 5, 16), (cx, 22), (cx - 5, 16)), fill="#efc382")
        d.point((cx, 16), fill="#d9534f")
    for xx in range(3, 46, 3):
        d.line((xx, 0, xx, 1), fill=CREAM)
        d.line((xx, 30, xx, 31), fill=CREAM)


@_register("idli_counter", (3, 1))
def _idli_counter(im, d, collision):
    _prop_objects("darshini_counter", {}, im, d, collision)
    d.rectangle((40, 0, 46, 3), fill="#f1e7ce")


@_register("plant_big", (1, 1))
def _plant_big(im, d, collision):
    d.polygon(((3, 9), (12, 9), (11, 15), (4, 15)), fill="#b86a4a", outline=OUTLINE)
    _foliage(d, (0, 0, 15, 11), (GRASS[1], GRASS[3], GRASS[2]))


# ------------------------------------------------------------------------------------------------
# extra wall styles
# ------------------------------------------------------------------------------------------------
_WALL_EXTRA = {"tiled": "#e9eef0", "blue": "#9cc3d9", "green": "#a9d1a6", "office": "#e4e7ea",
               "stadium": "#c9c4b6", "site": "#7f95b0", "toxic": "#8fae6a", "water": "#7fb3cf",
               "fire": "#d98a5c", "temple": "#cdbf9f", "ranger": "#b98a5a", "pink": "#e9b8bd"}


def _interior_wall_extra(width_tiles, style):
    base = _WALL_EXTRA[style]
    im = _image(width_tiles * TILE, 32, base)
    d = ImageDraw.Draw(im)
    W = im.width
    if style == "tiled":
        for yy in range(4, 27, 5):
            d.line((0, yy, W - 1, yy), fill="#c9d2d6")
        for row, yy in enumerate(range(4, 27, 5)):
            for xx in range(2 if row % 2 else 0, W, 5):
                d.line((xx, yy, xx, yy + 4), fill="#c9d2d6")
        d.rectangle((0, 18, W - 1, 19), fill="#4f86b0")
    elif style in ("blue", "green", "pink"):
        d.rectangle((0, 18, W - 1, 26), fill=_shade(base, -22))
        d.line((0, 18, W - 1, 18), fill=_shade(base, 25))
        for xx in range(6, W, 32):
            d.line((xx, 6, xx + 4, 6), fill=_shade(base, 15))
    elif style == "office":
        d.rectangle((0, 20, W - 1, 26), fill="#b9c2c9")
        for xx in range(0, W, 16):
            d.line((xx, 3, xx, 26), fill="#cfd5da")
    elif style == "stadium":
        for xx in range(0, W, 32):
            col = ("#4f86b0", "#d9534f", "#5fa65b", "#f4c24f")[(xx // 32) % 4]
            _panel(d, (xx + 2, 14, xx + 29, 25), col)
            d.line((xx + 5, 18, xx + 24, 18), fill=CREAM)
            d.line((xx + 5, 21, xx + 18, 21), fill=_shade(col, 40))
        for xx in range(0, W, 4):
            d.line((xx, 4, xx, 11), fill="#b5b0a2")
    elif style == "site":
        for xx in range(0, W, 3):
            d.line((xx, 3, xx, 26), fill="#9fb3cc")
        d.rectangle((0, 22, W - 1, 26), fill="#f2d14c")
        for xx in range(-4, W, 6):
            d.line((xx, 26, xx + 4, 22), fill="#2f2b36")
    elif style in ("toxic", "water", "fire"):
        for xx in range(0, W, 16):
            _panel(d, (xx + 2, 6, xx + 13, 24), base, _shade(base, -30))
            if style == "toxic":
                d.ellipse((xx + 5, 10, xx + 10, 15), fill="#c9e36a")
                d.line((xx + 7, 15, xx + 7, 20), fill="#6f8a3a")
            elif style == "water":
                d.arc((xx + 4, 9, xx + 11, 16), 180, 360, fill="#e4f6f0")
                d.arc((xx + 4, 14, xx + 11, 21), 180, 360, fill="#e4f6f0")
            else:
                d.polygon(((xx + 5, 20), (xx + 7, 10), (xx + 9, 14), (xx + 11, 20)), fill="#ffd27a")
    elif style == "temple":
        for xx in range(0, W, 16):
            _panel(d, (xx + 1, 5, xx + 14, 24), base, "#9d917b")
            d.polygon(((xx + 4, 22), (xx + 7, 9), (xx + 10, 22)), fill="#b5a88a")
            d.ellipse((xx + 5, 7, xx + 9, 11), fill="#b5a88a")
    elif style == "ranger":
        for yy in range(3, 27, 4):
            d.line((0, yy, W - 1, yy), fill="#8f6a44")
            d.line((0, yy + 1, W - 1, yy + 1), fill="#d4a876")
    d.rectangle((0, 0, W - 1, 2), fill=_shade(base, -32))
    d.line((0, 3, W - 1, 3), fill=_shade(base, 25))
    d.rectangle((0, 27, W - 1, 31), fill=_shade(base, -40))
    d.line((0, 27, W - 1, 27), fill=_shade(base, 12))
    d.line((0, 31, W - 1, 31), fill=OUTLINE)
    return im


# ------------------------------------------------------------------------------------------------
# a few more landmarks and household bits
# ------------------------------------------------------------------------------------------------
@_register("ashoka_pillar", (1, 3))
def _ashoka_pillar(im, d, collision):
    # a polished stone column with a lion capital on a stepped plinth, as at the circle by Lalbagh's south gate
    collision[:] = [[False], [False], [True]]
    _panel(d, (1, 40, 14, 47), "#b9ad96")
    _panel(d, (3, 36, 12, 41), "#cbbfa7")
    _panel(d, (6, 9, 9, 37), "#d8cfbd")
    d.line((7, 10, 7, 36), fill="#efe8da")
    d.rectangle((5, 6, 10, 9), fill="#c9a24e", outline=OUTLINE)
    d.ellipse((4, 0, 11, 7), fill="#d6b04c", outline=OUTLINE)
    d.point((6, 2), fill="#f4d481")
    d.line((5, 5, 10, 5), fill="#a8823a")


@_register("tulasi_katte", (1, 1))
def _tulasi_katte(im, d, collision):
    _panel(d, (3, 8, 12, 15), "#e6dcc4")
    d.rectangle((4, 10, 11, 11), fill="#d9534f")
    d.point((7, 13), fill="#f4c24f")
    _foliage(d, (3, 0, 12, 9), ("#4c9a52", "#2c6142", "#83c066"))


@_register("clothes_line", (2, 1))
def _clothes_line(im, d, collision):
    for xx in (1, 30):
        d.line((xx, 2, xx, 15), fill=WOOD[1], width=2)
    d.line((1, 3, 30, 4), fill="#7c7768")
    for xx, c, h in ((4, "#d9534f", 8), (9, "#f4c24f", 6), (14, "#4f86b0", 9), (20, "#f1e7ce", 7), (25, "#a38acb", 6)):
        d.rectangle((xx, 4, xx + 3, 4 + h), fill=c, outline=OUTLINE)


@_register("water_tank_stand", (1, 2))
def _water_tank_stand(im, d, collision):
    collision[:] = [[False], [True]]
    for xx in (3, 12):
        d.line((xx, 12, xx, 30), fill="#56606a", width=2)
    d.line((3, 20, 12, 26), fill="#56606a")
    d.line((12, 20, 3, 26), fill="#56606a")
    tank, _ = prop("water_tank")
    im.alpha_composite(tank, (0, 0))


@_register("valve_wheel", (1, 1))
def _valve_wheel(im, d, collision):
    d.rectangle((0, 9, 15, 13), fill="#7d8a8f", outline=OUTLINE)
    d.line((0, 10, 15, 10), fill="#a9b6ba")
    d.rectangle((6, 6, 9, 10), fill="#5d6470", outline=OUTLINE)
    d.ellipse((2, 0, 13, 9), outline="#c8443a", width=2)
    d.line((7, 1, 7, 8), fill="#c8443a")
    d.line((3, 4, 12, 4), fill="#c8443a")
    d.ellipse((6, 3, 9, 6), fill="#e8766a", outline=OUTLINE)


@_register("hard_hats", (1, 1))
def _hard_hats(im, d, collision):
    d.line((1, 4, 14, 4), fill=WOOD[1], width=2)
    for xx, c in ((1, "#f2d14c"), (8, "#f08a3c")):
        d.pieslice((xx, 5, xx + 6, 13), 180, 360, fill=c, outline=OUTLINE)
        d.line((xx - 1, 9, xx + 7, 9), fill=_shade(c, -30))
        d.point((xx + 2, 6), fill=_shade(c, 50))


@_register("blueprint_table", (2, 1))
def _blueprint_table(im, d, collision):
    for xx in (3, 27):
        d.line((xx, 9, xx, 15), fill=OUTLINE, width=2)
    _panel(d, (0, 3, 31, 10), WOOD[0])
    d.rectangle((3, 2, 26, 9), fill="#3f6fb0", outline=OUTLINE)
    for xx in range(5, 25, 4):
        d.line((xx, 3, xx, 8), fill="#7fa8d8")
    d.line((4, 6, 25, 6), fill="#cfe3f6")
    d.rectangle((14, 4, 20, 7), outline="#f1e7ce")
    d.line((22, 1, 28, 4), fill="#d9534f", width=2)


@_register("elephant", (2, 2))
def _elephant(im, d, collision):
    grey, dk, lt = "#8f8a96", "#6a6572", "#b3aebb"
    for xx in (5, 11, 19, 24):
        d.rectangle((xx, 22, xx + 3, 30), fill=dk if xx in (11, 24) else grey, outline=OUTLINE)
    d.ellipse((3, 8, 27, 26), fill=grey, outline=OUTLINE)
    d.arc((5, 9, 24, 22), 190, 290, fill=lt)
    # caparison: a bright cloth with gold edging
    d.polygon(((8, 9), (21, 9), (22, 20), (7, 20)), fill="#c8443a", outline=OUTLINE)
    d.line((8, 18, 21, 18), fill="#f4c24f")
    for xx in (10, 14, 18):
        d.point((xx, 13), fill="#f4c24f")
    d.ellipse((22, 5, 31, 16), fill=grey, outline=OUTLINE)
    d.ellipse((19, 6, 25, 15), fill=dk, outline=OUTLINE)
    d.line((29, 14, 30, 25), fill=OUTLINE, width=3)
    d.line((29, 14, 30, 24), fill=grey, width=1)
    d.line((27, 15, 29, 18), fill=CREAM)
    d.point((27, 9), fill=OUTLINE)
    d.polygon(((24, 5), (28, 5), (27, 8)), fill="#f4c24f", outline=OUTLINE)
    d.line((2, 14, 1, 20), fill=OUTLINE)


if __name__ == "__main__":
    output=Path(__file__).resolve().parents[2]/"art-src/previews/tiles_preview.png"
    output.parent.mkdir(parents=True,exist_ok=True)
    atlas=preview()
    atlas=atlas.resize((atlas.width*3,atlas.height*3),Image.Resampling.NEAREST)
    atlas.save(output)
    print(f"Wrote {output} ({atlas.width}x{atlas.height})")
