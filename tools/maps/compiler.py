"""Map compiler: turns compact Python map definitions into game assets.

For each map it writes assets/maps/<id>/bg.png (16 px tiles, shown x4 in game), an optional fg.png, and map.json —
a Tiled-format map with a "Collision" layer, "Encounter-<zone>" layers and an "uru" block holding warps, NPCs, signs,
items, triggers and encounter tables for the WorldScene.

Layout characters (ground):
  .  grass          ,  grass with flowers     "  tall grass (encounters)    :  dirt path
  =  road           -  road line (horizontal) |  road line (vertical)        z  zebra crossing
  _  pavers         s  sand                   ~  water (blocked)             m  mud
  w  wood floor     t  tile floor             c  carpet                      l  lab floor
  o  stone floor    v  cave floor (encounters in caves)                      b  bridge (horizontal)
  B  bridge (vert)  #  rock/cliff (blocked)   X  void (blocked, black)       %  invisible wall over grass
Single-tile props:
  h hedge  u bush  r rock  q flower bed  f fence  F fence (vertical)  k compound wall  K compound wall (vertical)
  g open gate (walkable)  n trash bin
Multi-tile anchors (top-left of the stamp; the cells it covers can be anything):
  T tree 2x2   J jacaranda 2x2   G gulmohar 2x2   P coconut palm 1x2   R rain tree 3x3   Y banyan 3x3   O boulder 2x2
"""
import json
import os
import sys

from PIL import Image

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
}
BLOCKED_GROUND = {"~", "#", "X", "%"}
SINGLE_PROPS = {"h": "hedge", "u": "bush", "r": "rock", "q": "flower_bed", "f": "fence_h", "F": "fence_v",
                "k": "compound_wall_h", "K": "compound_wall_v", "g": "gate", "n": "trash_bin"}
STAMPS = {"T": "tree", "J": "jacaranda", "G": "gulmohar", "P": "coconut_palm", "R": "rain_tree", "Y": "banyan",
          "O": "boulder"}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
EXIT_DIR = {"N": "DOWN", "S": "UP", "E": "LEFT", "W": "RIGHT"}


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
        self.draw_ops = []   # (sort_y, x_px, y_px, image, layer)
        self.warps = list(d.get("warps", []))
        self.base_ground = d.get("ground", "grass")

    # ---------------------------------------------------------------------------------------
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

    def place(self, img, grid, tx, ty, layer="bg", sort_bias=0):
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        for gy in range(rows):
            for gx in range(cols):
                if grid[gy][gx]:
                    self.block_rect(tx + gx, ty + gy, 1, 1)
        bottom = (ty + max(rows, img.height // T)) * T
        self.draw_ops.append((bottom + sort_bias, tx * T, ty * T + (rows * T - img.height if img.height > rows * T else 0), img, layer))

    # ---------------------------------------------------------------------------------------
    def build(self):
        bg = Image.new("RGBA", (self.w * T, self.h * T), (28, 20, 48, 255))
        fg = Image.new("RGBA", (self.w * T, self.h * T), (0, 0, 0, 0))
        water = lambda x, y: self.ch(x, y) == "~"  # noqa: E731

        # ground
        for y in range(self.h):
            for x in range(self.w):
                c = self.ch(x, y)
                if c == "X":
                    self.blocked[y][x] = True
                    continue
                if c == "~":
                    tile = tiles.water(water(x, y - 1), water(x + 1, y), water(x, y + 1), water(x - 1, y),
                                       water(x + 1, y - 1), water(x - 1, y - 1), water(x + 1, y + 1), water(x - 1, y + 1), x, y)
                    self.blocked[y][x] = True
                    self.water.add((x, y))
                elif c == "#":
                    tile = rock_wall(x, y, self.ch(x, y + 1) != "#", self.ch(x, y - 1) != "#",
                                     self.ch(x - 1, y) != "#", self.ch(x + 1, y) != "#",
                                     earthy=self.d.get("cliffGround") == "dirt")
                    self.blocked[y][x] = True
                else:
                    tile = tiles.ground(self.ground_name(x, y), x, y)
                    if c == "%":
                        self.blocked[y][x] = True
                bg.alpha_composite(tile, (x * T, y * T))
                if c == '"':
                    self.encounter.setdefault(self.d.get("grassZone", "grass"), set()).add((x, y))
                if c == "v" and self.d.get("caveEncounters"):
                    self.encounter.setdefault("cave", set()).add((x, y))

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

        # listed props
        for p in self.d.get("props", []):
            name, x, y = p[0], p[1], p[2]
            params = p[3] if len(p) > 3 else {}
            img, grid = tiles.prop(name, **params)
            if params.get("_walkable"):
                grid = [[False] * len(grid[0]) for _ in grid]
            self.place(img, grid, x, y, sort_bias=-1 if name in ("rug",) else 0)

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
            if not s.get("noPost"):
                img, _ = tiles.prop("signpost")
                self.place(img, [[True]], s["x"], s["y"])
            else:
                self.blocked[s["y"]][s["x"]] = True
        for c in self.d.get("counters", []):
            self.blocked[c[1]][c[0]] = True

        # draw props/buildings bottom-to-top so lower things overlap higher ones
        for _, px, py, img, layer in sorted(self.draw_ops, key=lambda o: o[0]):
            (fg if layer == "fg" else bg).alpha_composite(img, (px, py))

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
            "water": sorted(y * self.w + x for x, y in self.water) if "fish" in d.get("encounters", {}) else [],
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
