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
................
................
...l......l.....
.l.gl...l.gl....
..lgsg...lgsg...
..ggss...ggss...
...ss.....ss....
................
.......l........
..l..l.gl...l...
l.gl..lgsg.l.gl.
.lgsg.ggss..lgsg
.ggss..ss...ggss
..ss........ss..
................
................
"""


def tall_grass_overlay() -> Image.Image:
    """Foreground blade tips at the player's feet, with a transparent upper half."""
    im = _image()
    _pixels(im, _BLADES, {"g": GRASS[1], "s": GRASS[3], "l": GRASS[2]})
    ImageDraw.Draw(im).rectangle((0, 0, 15, 7), fill=(0, 0, 0, 0))
    return im


def ground(name: str, x: int, y: int) -> Image.Image:
    """Opaque terrain. Texture motifs meet across tile edges without dark borders."""
    if name not in GROUND_NAMES:
        raise ValueError(f"Unknown ground {name!r}; choose from {GROUND_NAMES}")
    seed = _seed(x, y)
    if name in ("grass", "grass_flowers", "tall_grass"):
        im = _image(color=GRASS[0])
        motif = _GRASS if name != "tall_grass" else _BLADES
        _pixels(im, motif, {"g": GRASS[1], "s": GRASS[3] if name == "tall_grass" else GRASS[1], "l": GRASS[2]})
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
          se: bool, sw: bool, x: int, y: int) -> Image.Image:
    """Eight-neighbour shoreline: cardinal banks and concave diagonal corners.

    Flags describe water, not land. Cardinal banks take priority; a missing
    diagonal adds an inset only when both incident cardinal neighbours exist.
    """
    im = _image(color=WATER[0])
    d = ImageDraw.Draw(im)
    for px, py in ((2, 4), (10, 12)):
        d.line((px, py, px + 3, py), fill=WATER[2])
        d.point((px + 4, py - 1), fill=WATER[2])
        d.line((px + 1, py + 2, px + 4, py + 2), fill=WATER[1])
    # Shore material is consistent around every edge. The grass is the same
    # base as ground('grass'); the sandy lip provides separation without ink.
    bank = (GRASS[0], GRASS[0], "#d9c991", WATER[1])
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
                        c = GRASS[0] if distance <= 1 else "#d9c991" if distance <= 4 else WATER[1]
                        d.point((15 - xx if right else xx, 15 - yy if bottom else yy), fill=c)
        elif not a and not b:
            # Fill the outside square where two banks meet, removing pinholes.
            xx, yy = (12 if right else 0), (12 if bottom else 0)
            d.rectangle((xx, yy, xx + 3, yy + 3), fill=GRASS[0])
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
    palettes = {"tree": ("#64ac59", "#39794e", "#99cc70"),
                "jacaranda": ("#a589d2", "#705caa", "#d3b7ef"),
                "gulmohar": ("#e9784f", "#ae4c44", "#ffb56b"),
                "rain_tree": ("#58996a", "#376b53", "#8dc583"),
                "banyan": ("#70a35e", "#446e4c", "#afd180")}
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
    allowed = {"color"} if name in ("flower_bed", "car") else set()
    if set(params) - allowed:
        raise ValueError(f"Unsupported parameters for {name}: {sorted(set(params) - allowed)}")
    tw, th = _PROP_SIZES[name]
    im = _image(tw * TILE, th * TILE)
    d = ImageDraw.Draw(im)
    collision = [[True for _ in range(tw)] for _ in range(th)]
    if name in ("tree", "jacaranda", "gulmohar", "rain_tree", "banyan"):
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
    allowed = {"w","h","wall","roof","door_x"} if kind=="house" else {"w","sign","awning"} if kind=="shop" else set()
    if set(params)-allowed:
        raise ValueError(f"Unsupported parameters for {kind}: {sorted(set(params)-allowed)}")
    tw,th=_BUILDING_SIZES[kind]
    if kind=="house":
        tw=_integer(params.get("w",tw),"w",3,7)
        th=_integer(params.get("h",th),"h",3,5)
    elif kind=="shop":
        tw=_integer(params.get("w",tw),"w",3,6)
    door_col=_integer(params.get("door_x",tw//2),"door_x",0,tw-1)
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
    else:
        doors,style=_landmark(kind,im)
    for col,row in doors:
        # The cave mouth already fills its trigger tile. A second little arch
        # would look like a stone door placed inside the natural opening.
        if kind != "cave_entrance":
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
        _label(im,"URU CRICKET",(40,22,87,29))
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
    sheet=_image(width,1900,"#eee4cf")
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
    y0+=6*82+4
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


if __name__ == "__main__":
    output=Path(__file__).resolve().parents[2]/"art-src/previews/tiles_preview.png"
    output.parent.mkdir(parents=True,exist_ok=True)
    atlas=preview()
    atlas=atlas.resize((atlas.width*3,atlas.height*3),Image.Resampling.NEAREST)
    atlas.save(output)
    print(f"Wrote {output} ({atlas.width}x{atlas.height})")
