"""Map compiler: turns compact Python map definitions into game assets.

For each map it writes assets/maps/<id>/bg.png (16 px tiles, shown x4 in game), an optional fg.png (drawn over the
characters: tree crowns, flyover and metro decks, overhead wires) and map.json - a Tiled-format map with a "Collision"
layer, "Encounter-<zone>" layers and an "uru" block holding warps, NPCs, signs, items, triggers and encounter tables.

Layout characters (ground):
  .  grass          ,  grass with flowers     "  tall grass (encounters)    :  dirt path
  =  road           -  road line (horizontal) |  road line (vertical)        z  zebra crossing
  _  pavers         s  sand                   ~  water (blocked)             m  mud
  w  wood floor     t  tile floor             c  carpet                      l  lab floor
  o  stone floor    v  cave floor (encounters in caves)                      b  bridge (horizontal)
  B  bridge (vert)  #  rock/cliff (blocked)   X  void (blocked, black)       %  invisible wall over grass
  p  footpath slabs d  dark grass             y  dry grass / scrub           e  red earth (laterite)
  i  granite sheet  j  gravel                 x  red oxide floor             A  checker floor
  C  polished granite floor                   D  ghat steps (to water)       L  forest floor (leaf litter)
  Q  flagstones     E  striped turf           H  cricket pitch clay          V  mosaic floor
  Z  office carpet  '  dry tall grass (encounters)   M  door mat     S  stairs
Blocked autotiles:
  U  foamy water    +  stepping stones in water (walkable)                   @  dense forest (auto-filled trees)
  !  granite boulder mass                     ^  grassy ledge / terrace      W  fort wall (crenellated)
  I  paddy field
Single-tile props:
  h hedge  u bush  r rock  q flower bed  f fence  F fence (vertical)  k compound wall  K compound wall (vertical)
  g open gate (walkable)  n trash bin
Multi-tile anchors (top-left of the stamp; the cells it covers can be anything; they block every covered tile):
  T tree 2x2   J jacaranda 2x2   G gulmohar 2x2   P coconut palm 1x2   R rain tree 3x3   Y banyan 3x3   O boulder 2x2

Map definition keys beyond the obvious ones:
  objects / legend   a second ASCII layer the size of the layout; legend maps a character to a prop name or
                     (name, params). Multi-tile props anchor at their top-left character. Characters missing from
                     the legend are ignored by the compiler (use them as position markers, see dsl.marks).
  props              [(name, x, y[, params])]. Params starting with "_" are compiler options:
                     _fg (whole prop drawn over characters, walkable), _walk (no collision), _block (all blocked),
                     _z (draw-order bias).
  wires              [[(x, y), ...], ...] pole positions (anchor of an electric_pole); sagging cables drawn in fg.
  forestKinds        tree kinds used to fill "@" (default tree/tree_dark mix).
  waterStyle         "clear" | "murky" | "lotus"; waterBank "grass" | "stone" | "sand".
  cliffGround        "dirt" | "cave_floor" | "granite" picks the "#" rock style. rockGround: ground under rounded rock.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))

import tiles  # noqa: E402

T = 16
GROUND = {
    ".": "grass", ",": "grass_flowers", '"': "tall_grass", ":": "dirt", "=": "road", "-": "road_line_h",
    "|": "road_line_v", "z": "zebra", "_": "pavers", "s": "sand", "m": "mud", "w": "wood_floor", "t": "tile_floor",
    "c": "carpet", "l": "lab_floor", "o": "stone_floor", "v": "cave_floor", "b": "bridge_h", "B": "bridge_v",
    "M": "mat", "S": "stairs",
    "p": "footpath", "d": "grass_dark", "y": "dry_grass", "e": "red_earth", "i": "rock_floor", "j": "gravel",
    "x": "red_oxide", "A": "checker", "C": "granite_floor", "D": "ghat", "L": "forest_floor", "Q": "flagstone",
    "E": "turf", "H": "pitch", "V": "mosaic", "Z": "office_carpet", "'": "tall_grass_dry",
}
WATER_CH = {"~", "U", "+"}
SOLID_CH = {"#", "!", "^", "W"}
# props that glow at dusk and night: name -> (glow size, tint)
LIGHT_PROPS = {"street_lamp": (3.2, 0xffd890), "lamp_post": (2.8, 0xffe0a0), "lamp_stand": (2.2, 0xffd080),
               "brazier": (3, 0xff9a50), "tea_stall": (2.4, 0xffc070), "bunk_shop": (2.4, 0xffd090),
               "signal": (1.4, 0xff5040)}
BLOCKED_GROUND = {"~", "U", "#", "X", "%", "@", "!", "^", "W", "I"}
SINGLE_PROPS = {"h": "hedge", "u": "bush", "r": "rock", "q": "flower_bed", "f": "fence_h", "F": "fence_v",
                "k": "compound_wall_h", "K": "compound_wall_v", "g": "gate", "n": "trash_bin"}
STAMPS = {"T": "tree", "J": "jacaranda", "G": "gulmohar", "P": "coconut_palm", "R": "rain_tree", "Y": "banyan",
          "O": "boulder"}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
EXIT_DIR = {"N": "DOWN", "S": "UP", "E": "LEFT", "W": "RIGHT"}
SIGN_STYLES = {"post": "signpost", "board": "notice_board", "stone": "stone_tablet", "metro": "metro_sign",
               "forest": "forest_sign", "milestone": "milestone"}
DECAL_BIAS = -100000


def _hash(x, y, salt=0):
    v = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    v = (v ^ (v >> 13)) * 0x5bd1e995 & 0xFFFFFFFF
    return v ^ (v >> 15)


class MapBuild:
    def __init__(self, d):
        self.d = d
        self.id = d["id"]
        rows = [r for r in d["layout"].strip("\n").split("\n")]
        rows = [r.rstrip() for r in rows]
        width = max(len(r) for r in rows)
        self.rows = [r.ljust(width, ".") for r in rows]
        self.w = width
        self.h = len(self.rows)
        self.blocked = [[False] * self.w for _ in range(self.h)]
        self.encounter = {}  # zone -> set((x,y))
        self.water = set()   # (x,y) of water tiles, for fishing
        self.lights = []     # lamps and fires that glow at night (src/fx/world-fx.js)
        self.draw_ops = []   # (sort_y, x_px, y_px, image, layer)
        self.warps = list(d.get("warps", []))
        self.base_ground = d.get("ground", "grass")
        self.props = list(d.get("props", []))
        self._parse_objects()

    # ---------------------------------------------------------------------------------------
    def _parse_objects(self):
        text = self.d.get("objects")
        if not text:
            return
        legend = self.d.get("legend", {})
        rows = text.strip("\n").split("\n")
        if len(rows) != self.h:
            raise ValueError(f"{self.id}: objects layer has {len(rows)} rows, layout has {self.h}")
        for y, row in enumerate(rows):
            if len(row.rstrip()) > self.w:
                raise ValueError(f"{self.id}: objects row {y} is wider than the layout")
            for x, ch in enumerate(row):
                if ch in legend:
                    entry = legend[ch]
                    if isinstance(entry, str):
                        self.props.append((entry, x, y))
                    else:
                        self.props.append((entry[0], x, y, dict(entry[1]) if len(entry) > 1 else {}))

    def ch(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.rows[y][x]
        return "X"

    def ground_name(self, x, y):
        c = self.ch(x, y)
        if c in GROUND:
            return GROUND[c]
        if c in STAMPS or c in SINGLE_PROPS:
            return self.d.get("stampGround", self.base_ground)
        return self.base_ground

    def block_rect(self, x, y, w, h):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.blocked[yy][xx] = True

    def place(self, img, grid, tx, ty, layer="bg", sort_bias=0, fg_mask=None, block=True):
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if block:
            for gy in range(rows):
                for gx in range(cols):
                    if grid[gy][gx]:
                        self.block_rect(tx + gx, ty + gy, 1, 1)
        bottom = (ty + max(rows, img.height // T)) * T
        oy = ty * T + (rows * T - img.height if img.height > rows * T else 0)
        if fg_mask and any(any(r) for r in fg_mask) and img.height == rows * T:
            # split the sprite: overhanging cells go over the characters, the rest stays on the ground layer
            low = img.copy()
            high = Image.new("RGBA", img.size, (0, 0, 0, 0))
            for gy in range(rows):
                for gx in range(cols):
                    if fg_mask[gy][gx]:
                        box = (gx * T, gy * T, gx * T + T, gy * T + T)
                        high.paste(img.crop(box), box[:2])
                        low.paste(Image.new("RGBA", (T, T), (0, 0, 0, 0)), box[:2])
            self.draw_ops.append((bottom + sort_bias, tx * T, oy, low, layer))
            self.draw_ops.append((bottom + sort_bias, tx * T, oy, high, "fg"))
        else:
            self.draw_ops.append((bottom + sort_bias, tx * T, oy, img, layer))

    # ---------------------------------------------------------------------------------------
    def _solid_tile(self, c, x, y):
        # a granite mass treats its own walkable top ("i") and steps cut into it ("S") as part of the rock
        tops = {"i", "S"} if c in "!#" else set()
        same = lambda xx, yy: self.ch(xx, yy) == c or self.ch(xx, yy) in tops or (c == "#" and self.ch(xx, yy) == "X")  # noqa: E731
        nb = dict(n=same(x, y - 1), s=same(x, y + 1), w=same(x - 1, y), e=same(x + 1, y),
                  nw=same(x - 1, y - 1), ne=same(x + 1, y - 1), sw=same(x - 1, y + 1), se=same(x + 1, y + 1))
        if tops:
            nb["inner"] = tuple(k for k, (dx, dy) in (("n", (0, -1)), ("s", (0, 1)), ("w", (-1, 0)), ("e", (1, 0)))
                                if self.ch(x + dx, y + dy) in tops)
            nb["deep"] = self.ch(x, y + 1) == c and not same(x, y + 2)
        if c == "#":
            style = self.d.get("cliffGround")
            if style == "granite":
                return tiles.solid("granite", x, y, **nb)
            if style == "cave_floor":
                return tiles.solid("cave_wall", x, y, **nb)
            return rock_wall(x, y, not nb["s"], not nb["n"], not nb["w"], not nb["e"], earthy=style == "dirt")
        if c != "!":
            nb.pop("inner", None)
            nb.pop("deep", None)
        return tiles.solid({"!": "granite", "^": "ledge", "W": "fort_wall"}[c], x, y, **nb)

    def build(self):
        bg = Image.new("RGBA", (self.w * T, self.h * T), (28, 20, 48, 255))
        fg = Image.new("RGBA", (self.w * T, self.h * T), (0, 0, 0, 0))
        water = lambda x, y: self.ch(x, y) in WATER_CH  # noqa: E731
        wstyle = self.d.get("waterStyle", "clear")
        wbank = self.d.get("waterBank", "grass")
        under_rock = self.d.get("rockGround", self.base_ground)

        # ground
        for y in range(self.h):
            for x in range(self.w):
                c = self.ch(x, y)
                if c == "X":
                    self.blocked[y][x] = True
                    continue
                if c in WATER_CH:
                    tile = tiles.water(water(x, y - 1), water(x + 1, y), water(x, y + 1), water(x - 1, y),
                                       water(x + 1, y - 1), water(x - 1, y - 1), water(x + 1, y + 1), water(x - 1, y + 1),
                                       x, y, style=wstyle, bank=wbank)
                    if c == "U":
                        tile.alpha_composite(tiles.water_overlay("foam", x, y))
                    if c == "+":
                        tile.alpha_composite(tiles.water_overlay("stones", x, y))
                    else:
                        self.blocked[y][x] = True
                        self.water.add((x, y))
                elif c in SOLID_CH:
                    tile = tiles.ground(under_rock, x, y)
                    tile.alpha_composite(self._solid_tile(c, x, y))
                    self.blocked[y][x] = True
                elif c == "@":
                    tile = tiles.ground("canopy", x, y)
                    self.blocked[y][x] = True
                elif c == "I":
                    tile = tiles.ground("paddy", x, y)
                    self.blocked[y][x] = True
                else:
                    tile = tiles.ground(self.ground_name(x, y), x, y)
                    if c == "%":
                        self.blocked[y][x] = True
                bg.alpha_composite(tile, (x * T, y * T))
                if c in ('"', "'"):
                    self.encounter.setdefault(self.d.get("grassZone", "grass"), set()).add((x, y))
                if c == "v" and self.d.get("caveEncounters"):
                    self.encounter.setdefault("cave", set()).add((x, y))

        self._forest()

        # single-tile props and stamp anchors in the layout
        for y in range(self.h):
            for x in range(self.w):
                c = self.ch(x, y)
                if c in SINGLE_PROPS:
                    img, grid = tiles.prop(SINGLE_PROPS[c])
                    self.place(img, grid, x, y)
                elif c in STAMPS:
                    img, grid = tiles.prop(STAMPS[c])
                    # trees, palms and boulders block every tile they cover
                    grid = [[True] * len(grid[0]) for _ in grid]
                    self.place(img, grid, x, y)

        # listed props (and the objects layer)
        for p in self.props:
            name, x, y = p[0], p[1], p[2]
            if name in LIGHT_PROPS:
                size, tint = LIGHT_PROPS[name]
                self.lights.append({"x": x, "y": y, "size": size, "tint": tint})
            params = dict(p[3]) if len(p) > 3 else {}
            opts = {k: params.pop(k) for k in list(params) if k.startswith("_")}
            img, grid = tiles.prop(name, **params)
            if opts.get("_walk"):
                grid = [[False] * len(grid[0]) for _ in grid]
            if opts.get("_block"):
                grid = [[True] * len(grid[0]) for _ in grid]
            bias = opts.get("_z", 0)
            if name in tiles.DECALS:
                bias += DECAL_BIAS
            if opts.get("_fg"):
                self.place(img, [[False] * len(grid[0]) for _ in grid], x, y, layer="fg", sort_bias=bias)
                continue
            self.place(img, grid, x, y, sort_bias=bias, fg_mask=tiles.prop_fg_mask(name, grid))

        # interior wall bands
        for wb in self.d.get("walls", []):
            x, y, width = wb[0], wb[1], wb[2]
            style = wb[3] if len(wb) > 3 else "plain"
            img = tiles.interior_wall(width, style)
            bg.alpha_composite(img, (x * T, y * T))
            self.block_rect(x, y, width, 2)

        # buildings
        for b in self.d.get("buildings", []):
            kind, x, y = b[0], b[1], b[2]
            params = dict(b[3]) if len(b) > 3 else {}
            door = params.pop("door", None)
            img, grid, doors = tiles.building(kind, **params)
            self.place(img, grid, x, y)
            if door and doors:
                for i, (dx, dy) in enumerate(doors):
                    warp = dict(door)
                    warp.setdefault("id", kind)
                    if i > 0:
                        warp["id"] = f"{warp['id']}__{i}"
                    warp.update(x=x + dx, y=y + dy)
                    warp.setdefault("exit", "DOWN")
                    warp.setdefault("dir", "UP")
                    self.warps.append(warp)

        # exits along map edges
        for e in self.d.get("exits", []):
            side, a, b_ = e["side"], e["from"], e["to_"]
            for i, t in enumerate(range(a, b_ + 1)):
                if side == "N":
                    x, y = t, 0
                elif side == "S":
                    x, y = t, self.h - 1
                elif side == "W":
                    x, y = 0, t
                else:
                    x, y = self.w - 1, t
                self.blocked[y][x] = True
                self.warps.append(dict(id=f"{side}{i}", x=x, y=y, to=e["map"], toId=f"{OPP[side]}{i}",
                                       exit=EXIT_DIR[side], dir={"N": "UP", "S": "DOWN", "E": "RIGHT", "W": "LEFT"}[side]))

        # explicit blocked / unblocked tiles
        for (x, y) in self.d.get("block", []):
            self.blocked[y][x] = True
        for (x, y) in self.d.get("unblock", []):
            self.blocked[y][x] = False
        for wp in self.warps:
            if wp.get("mode", "bump") == "bump":
                self.blocked[wp["y"]][wp["x"]] = True
        for s in self.d.get("signs", []):
            style = "none" if s.get("noPost") else s.get("style", "post")
            if style != "none":
                img, _ = tiles.prop(SIGN_STYLES[style])
                self.place(img, [[True]], s["x"], s["y"])
            else:
                self.blocked[s["y"]][s["x"]] = True
        for c in self.d.get("counters", []):
            self.blocked[c[1]][c[0]] = True

        # draw props/buildings bottom-to-top so lower things overlap higher ones
        for _, px, py, img, layer in sorted(self.draw_ops, key=lambda o: o[0]):
            if px < 0 or py < 0:
                img = img.crop((max(0, -px), max(0, -py), img.width, img.height))
                px, py = max(0, px), max(0, py)
            (fg if layer == "fg" else bg).alpha_composite(img, (px, py))
        self._wires(fg)

        out_dir = os.path.join(ROOT, "assets", "maps", self.id)
        os.makedirs(out_dir, exist_ok=True)
        bg.save(os.path.join(out_dir, "bg.png"), optimize=True)
        fg_path = os.path.join(out_dir, "fg.png")
        if fg.getbbox():
            fg.save(fg_path, optimize=True)
        elif os.path.exists(fg_path):
            os.remove(fg_path)
        with open(os.path.join(out_dir, "map.json"), "w") as fh:
            json.dump(self.tiled_json(), fh, separators=(",", ":"))
        return self

    # ---------------------------------------------------------------------------------------
    def _forest(self):
        """Fills "@" regions with overlapping, staggered trees; slim trees and bushes plug the edge gaps."""
        cells = {(x, y) for y in range(self.h) for x in range(self.w) if self.ch(x, y) == "@"}
        if not cells:
            return
        # beyond the map edge counts as forest, so border trees can hang half off the map and stagger
        outside = lambda x, y: not (0 <= x < self.w and 0 <= y < self.h)  # noqa: E731
        near = lambda x, y: any((x + dx, y + dy) in cells for dx in (-1, 0, 1) for dy in (-1, 0, 1))  # noqa: E731
        is_forest = lambda x, y: (x, y) in cells or (outside(x, y) and near(x, y))  # noqa: E731
        kinds = self.d.get("forestKinds", ["tree", "tree", "tree_dark", "tree", "tree_olive"])
        fillers = self.d.get("forestFillers", ["ashoka", "ashoka", "bush_tall"])
        covered = set()
        for y in range(-1, self.h):
            for x in range(-1, self.w):
                if (x + y) % 2:
                    continue
                foot = [(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1)]
                if all(is_forest(*p) for p in foot) and any(p in cells for p in foot):
                    kind = kinds[_hash(x, y) % len(kinds)]
                    img, grid = tiles.prop(kind)
                    self.draw_ops.append(((y + 2) * T, x * T, y * T, img, "bg"))
                    covered.update(p for p in foot if p in cells)
        for y in range(self.h):
            for x in range(self.w):
                if (x, y) in cells and (x, y) not in covered:
                    if (x, y + 1) in cells and (x, y + 1) not in covered:
                        img, _ = tiles.prop(fillers[_hash(x, y, 3) % len(fillers)])
                        self.place(img, [[True], [True]], x, y)
                        covered.update({(x, y), (x, y + 1)})
                    else:
                        img, _ = tiles.prop("bush")
                        self.place(img, [[True]], x, y)
                        covered.add((x, y))

    def _wires(self, fg):
        """Sagging overhead cables between consecutive electric poles (anchored at the pole's top tile)."""
        d = ImageDraw.Draw(fg)
        for line in self.d.get("wires", []):
            for (x0, y0), (x1, y1) in zip(line, line[1:]):
                for k, (ox, oy, col) in enumerate(((3, 4, (42, 34, 48, 255)), (12, 4, (42, 34, 48, 255)),
                                                    (7, 7, (70, 62, 74, 255)))):
                    ax, ay = x0 * T + ox, y0 * T + oy
                    bx, by = x1 * T + ox, y1 * T + oy
                    dist = max(abs(bx - ax), abs(by - ay))
                    sag = 3 + dist // 14 + k
                    steps = max(2, dist)
                    pts = []
                    for i in range(steps + 1):
                        t = i / steps
                        pts.append((round(ax + (bx - ax) * t), round(ay + (by - ay) * t + sag * 4 * t * (1 - t))))
                    d.line(pts, fill=col)
                # a tangle of loose cable near the first pole
                if (x0 + y0) % 3 == 0:
                    cx, cy = x0 * T + 8, y0 * T + 9
                    d.arc((cx - 4, cy - 1, cx + 5, cy + 6), 10, 300, fill=(42, 34, 48, 255))

    # ---------------------------------------------------------------------------------------
    def tiled_json(self):
        d = self.d
        collision = [1 if self.blocked[y][x] else 0 for y in range(self.h) for x in range(self.w)]
        layers = [{"id": 1, "name": "Collision", "type": "tilelayer", "width": self.w, "height": self.h, "x": 0, "y": 0,
                   "opacity": 1, "visible": True, "data": collision}]
        lid = 2
        tile_type = {"cave": "CAVE"}
        for zone, cells in sorted(self.encounter.items()):
            data = [2 if (x, y) in cells else 0 for y in range(self.h) for x in range(self.w)]
            layers.append({"id": lid, "name": f"Encounter-{zone}", "type": "tilelayer", "width": self.w, "height": self.h,
                           "x": 0, "y": 0, "opacity": 1, "visible": True, "data": data,
                           "properties": [{"name": "area", "type": "string", "value": zone},
                                          {"name": "tileType", "type": "string", "value": tile_type.get(zone, "GRASS")}]})
            lid += 1
        uru = {
            "id": self.id, "name": d.get("name", self.id), "music": d.get("music"),
            "environment": d.get("environment", "grass"), "interior": d.get("interior", False),
            "warps": self.warps, "npcs": d.get("npcs", []), "signs": d.get("signs", []), "items": d.get("items", []),
            "triggers": d.get("triggers", []), "counters": d.get("counters", []),
            "interactables": d.get("interactables", []), "encounters": d.get("encounters", {}),
            "water": sorted(y * self.w + x for x, y in self.water),
            "lights": self.lights,
            "onEnter": d.get("onEnter"), "spawn": d.get("spawn"), "metroStation": d.get("metroStation"),
            "respawnText": d.get("respawnText"),
        }
        return {
            "compressionlevel": -1, "height": self.h, "width": self.w, "infinite": False, "orientation": "orthogonal",
            "renderorder": "right-down", "tiledversion": "1.10.2", "tileheight": 64, "tilewidth": 64, "type": "map",
            "version": "1.10", "nextlayerid": lid, "nextobjectid": 1, "layers": layers,
            "tilesets": [
                {"firstgid": 1, "name": "collision", "tilewidth": 64, "tileheight": 64, "tilecount": 1, "columns": 1,
                 "image": "collision.png", "imagewidth": 64, "imageheight": 64, "margin": 0, "spacing": 0},
                {"firstgid": 2, "name": "encounter", "tilewidth": 64, "tileheight": 64, "tilecount": 1, "columns": 1,
                 "image": "encounter.png", "imagewidth": 64, "imageheight": 64, "margin": 0, "spacing": 0},
            ],
            "uru": uru,
        }


def validate(maps):
    """Cross-map checks: warp targets exist and point at real warp ids; NPC/sign/item tiles are in bounds."""
    by_id = {m.id: m for m in maps}
    problems = []
    for m in maps:
        for w in m.warps:
            to = w.get("to")
            if to in (None, "@return"):
                continue
            if to not in by_id:
                problems.append(f"{m.id}: warp {w.get('id')} -> unknown map {to}")
                continue
            if w.get("toId") and not any(t.get("id") == w["toId"] for t in by_id[to].warps):
                problems.append(f"{m.id}: warp {w.get('id')} -> {to} has no warp id {w['toId']}")
        ids_w = [w.get("id") for w in m.warps]
        if len(ids_w) != len(set(ids_w)):
            problems.append(f"{m.id}: duplicate warp ids {sorted({i for i in ids_w if ids_w.count(i) > 1})}")
        for w in m.warps:
            if w.get("mode", "bump") == "bump" or w.get("mode") == "arrive":
                dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[w.get("exit", "DOWN")]
                ex, ey = w["x"] + dx, w["y"] + dy
                if not (0 <= ex < m.w and 0 <= ey < m.h) or m.blocked[ey][ex]:
                    problems.append(f"{m.id}: warp {w.get('id')} exits onto a blocked tile ({ex},{ey})")
        for n in m.d.get("npcs", []):
            if not (0 <= n["x"] < m.w and 0 <= n["y"] < m.h):
                problems.append(f"{m.id}: npc {n['id']} out of bounds")
            elif m.blocked[n["y"]][n["x"]] and not n.get("onBlocked"):
                problems.append(f"{m.id}: npc {n['id']} stands on a blocked tile ({n['x']},{n['y']})")
        ids = [n["id"] for n in m.d.get("npcs", [])]
        if len(ids) != len(set(ids)):
            problems.append(f"{m.id}: duplicate npc ids")
        for it in m.d.get("items", []):
            if m.blocked[it["y"]][it["x"]]:
                problems.append(f"{m.id}: item {it['id']} on a blocked tile")
        sp = m.d.get("spawn")
        if sp and m.blocked[sp["y"]][sp["x"]]:
            problems.append(f"{m.id}: spawn on blocked tile")
        for t in m.d.get("triggers", []):
            for yy in range(t["y"], t["y"] + t.get("h", 1)):
                for xx in range(t["x"], t["x"] + t.get("w", 1)):
                    if m.blocked[yy][xx]:
                        problems.append(f"{m.id}: trigger {t['id']} covers a blocked tile ({xx},{yy})")
        if "fish" in m.d.get("encounters", {}):
            shore = {(x, y) for (wx, wy) in m.water for x, y in ((wx + 1, wy), (wx - 1, wy), (wx, wy + 1), (wx, wy - 1))
                     if 0 <= x < m.w and 0 <= y < m.h and not m.blocked[y][x]}
            if len(shore) < 4:
                problems.append(f"{m.id}: only {len(shore)} walkable tiles next to fishing water")
        if "grass" in m.d.get("encounters", {}) and not m.encounter.get(m.d.get("grassZone", "grass")):
            problems.append(f"{m.id}: has a grass encounter table but no tall grass")
    return problems


def rock_wall(x, y, open_below, open_above, open_left, open_right, earthy=False):
    """A solid 16px rock tile: speckled stone with a lit top lip and a shadowed cliff face above open floor."""
    import random
    rnd = random.Random(x * 7919 + y * 104729)
    if earthy:
        base, mid, dark, light, edge = (150, 120, 92), (128, 100, 76), (92, 70, 54), (182, 152, 118), (66, 50, 40)
    else:
        base, mid, dark, light, edge = (104, 98, 112), (88, 82, 96), (62, 56, 70), (140, 134, 150), (40, 34, 48)
    img = Image.new("RGBA", (16, 16), base + (255,))
    px = img.load()
    for yy in range(16):
        for xx in range(16):
            r = rnd.random()
            if r < 0.18:
                px[xx, yy] = mid + (255,)
            elif r < 0.24:
                px[xx, yy] = dark + (255,)
            elif r < 0.28:
                px[xx, yy] = light + (255,)
    # cracks
    for _ in range(2):
        cx, cy = rnd.randrange(2, 14), rnd.randrange(2, 12)
        for k in range(rnd.randrange(2, 5)):
            if 0 <= cx < 16 and 0 <= cy < 16:
                px[cx, cy] = dark + (255,)
            cx += rnd.choice((-1, 0, 1))
            cy += 1
    if open_above:
        for xx in range(16):
            px[xx, 0] = edge + (255,)
            px[xx, 1] = light + (255,)
            px[xx, 2] = light + (255,) if rnd.random() < 0.6 else base + (255,)
    if open_below:
        # vertical cliff face: darker banded strata at the bottom of the wall
        for yy in range(9, 16):
            for xx in range(16):
                shade = dark if (yy + (xx // 4)) % 3 == 0 else mid
                px[xx, yy] = shade + (255,)
        for xx in range(16):
            px[xx, 15] = edge + (255,)
    if open_left:
        for yy in range(16):
            px[0, yy] = edge + (255,)
    if open_right:
        for yy in range(16):
            px[15, yy] = edge + (255,)
    return img
