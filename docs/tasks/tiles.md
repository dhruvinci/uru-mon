# Task: procedural world tileset, props and buildings

Create `tools/art/tiles.py` (Python 3, Pillow + numpy only; do not install anything): a library that renders GBA-era
(2004 handheld monster RPG) **16×16 px** world graphics for **uru-mon**, a creature-collecting RPG set in Bengaluru, India.
Read `docs/DESIGN.md` for context. A separate map compiler (written by someone else) will import this module, so the
**API below is a contract** — keep names and signatures exactly.

## Look
- Bright, warm, readable GBA palette; 2–4 tones per material; dark outlines (`#2a2230`, never pure black) on props and
  buildings but not on ground tiles. Light comes from the top-left.
- Bengaluru flavour: red Mangalore-tile pitched roofs; flat concrete roofs with a parapet and a black plastic water tank;
  pastel painted walls (pink, yellow, sky blue, mint, white); window grills; compound walls with small iron gates;
  interlocking grey/red paver footpaths; tar roads with white dashed lines; jacaranda (purple), gulmohar (red-orange),
  rain trees and coconut palms; yellow-and-black auto-rickshaws; steel-vessel darshini counters.
- Hand-author key textures and props as ASCII pixel grids inside the file where it helps quality. Tiles must tile
  seamlessly (grass, road, water, floors).

## API (all images are RGBA PIL Images)
```python
TILE = 16

def ground(name: str, x: int, y: int) -> Image   # one 16x16 ground tile; x,y are map coords, used to pick variants deterministically
GROUND_NAMES: list[str]
# must include: "grass", "grass_flowers", "tall_grass", "dirt", "road", "road_line_h", "road_line_v", "zebra",
# "pavers", "sand", "wood_floor", "tile_floor", "carpet", "cave_floor", "mud", "bridge_h", "bridge_v",
# "stone_floor" (palace/temple), "lab_floor", "mat" (exit door mat), "stairs"

def water(n: bool, e: bool, s: bool, w: bool, ne: bool, nw: bool, se: bool, sw: bool, x: int, y: int) -> Image
# a water tile; each flag says whether that neighbour is ALSO water. Where a neighbour is not water, draw a grass/stone shore edge.

def tall_grass_overlay() -> Image   # 16x16; the top part of tall grass drawn over the player's legs while standing in it

def prop(name: str, **params) -> tuple[Image, list[list[bool]]]
# multi-tile prop. Image size is a multiple of 16; the second value is a collision grid (rows of tiles, True = blocked).
PROP_NAMES: list[str]
# must include (default size in tiles):
#  "tree" 2x2 (generic green), "jacaranda" 2x2, "gulmohar" 2x2, "rain_tree" 3x3, "banyan" 3x3 (with aerial roots),
#  "coconut_palm" 1x2 (collision on the bottom tile only), "bush" 1x1, "hedge" 1x1, "flower_bed" 1x1 (param color),
#  "rock" 1x1, "boulder" 2x2 (granite), "lamp_post" 1x2 (collision bottom), "bench" 2x1, "signpost" 1x1,
#  "trash_bin" 1x1, "water_tank" 1x1, "fence_h" 1x1, "fence_v" 1x1, "compound_wall_h" 1x1, "compound_wall_v" 1x1,
#  "gate" 1x1 (open iron gate, NOT blocked), "auto_rickshaw" 2x2, "car" 2x2 (param color), "scooter" 1x1,
#  "bus_stop" 3x2, "cow" 2x1, "statue" 1x2, "fountain" 2x2, "cricket_stumps" 1x1,
#  interior: "table" 2x1, "chair" 1x1, "bed" 1x2, "tv" 1x1, "bookshelf" 1x2 (collision both), "plant_pot" 1x1,
#  "darshini_counter" 3x1 (steel vessels, idli stand), "shop_shelf" 2x1, "cloud_kiosk" 1x2 (a PC-like terminal labelled
#  CLOUD), "stove" 1x1, "rug" 2x2 (not blocked), "desk" 2x1, "lab_machine" 1x2, "sofa" 2x1, "pooja_shelf" 1x1 (lamp)
#  cave: "cave_rock" 1x1, "stalagmite" 1x1, "crate" 1x1

def interior_wall(width_tiles: int, style: str = "plain") -> Image
# the top wall band of a room: width_tiles x 2 tiles (32 px tall); styles: "plain", "wood", "lab", "palace", "shop", "cave"

def building(kind: str, **params) -> tuple[Image, list[list[bool]], list[tuple[int, int]]]
# returns (image, collision grid, door tile positions relative to the building's top-left).
# Doors are blocked tiles (the game triggers a warp when the player bumps a door).
# kinds and params:
#  "house": w (tiles, 3..7), h (tiles, 3..5), wall (colour name or hex), roof ("tile" | "flat"), door_x (tile col)
#  "shop": w (3..6), sign (short uppercase text), awning (colour)          -- rolling shutter + painted signboard
#  "darshini": 4x3 healing eatery, white walls, green/red signboard "DARSHINI", steaming vessel
#  "kirana": 4x3 provision store, blue awning, signboard "KIRANA"
#  "lab": 6x4 modern research building, glass + concrete, sign "URUMON LAB"
#  "glass_house": 7x5 Victorian glasshouse/greenhouse with a central dome (Lalbagh arena)
#  "stadium": 8x5 cricket stadium wall with floodlight towers and a gate (MG Road arena)
#  "tech_tower": 6x6 glass office tower with logo panel (Whitefield arena)
#  "tutor_house": 6x4 old-style house with a veranda, pillars, tiled roof (Malleshwaram arena)
#  "palace": 9x6 Tudor-style palace with turrets and battlements (Palace Road arena)
#  "hill_pavilion": 6x4 old stone hill pavilion with arches (Nandi Hills arena)
#  "metro_station": 8x4 elevated station, concrete pillars, purple stripe, stairs entrance, sign "METRO"
#  "vidhana_soudha": 13x8 grand neo-Dravidian government building: pale stone, central dome, colonnade, wide steps
#  "temple": 5x5 small stone temple with a stepped tower (gopura) and a big bull statue silhouette at the front
#  "syndicate_hq": 6x4 grey concrete site office with yellow/black hazard stripes and sign "CONCRETE SYNDICATE"
#  "cave_entrance": 3x2 dark cave mouth in rock
#  "player_house" / "rival_house": 5x4 two-storey homes (different colours)

def text(s: str, color=(255,255,255,255)) -> Image   # tiny 3x5 (or 4x6) pixel font for signboards, A-Z 0-9 and a few symbols

def preview() -> Image  # a sample scene using everything, for review
```

## CLI
`python3 tools/art/tiles.py` writes `art-src/previews/tiles_preview.png`: every ground tile, water edge cases, props and
buildings laid out on a grid with labels, scaled ×3, plus a small sample town scene. Open it yourself and fix anything
that looks off (seams, muddy colours, broken outlines) before finishing.

## Rules
- Only create `tools/art/tiles.py` and its preview. Do not modify any other file. Do not install packages.
- Deterministic output (seed any randomness from the x,y arguments).
