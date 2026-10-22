#!/usr/bin/env python3
"""Original, hand-pixelled Bengaluru overworld characters (16 x 32 frames).

Run ``python3 tools/art/characters.py`` from any directory. It writes one PNG
per preset to assets/images/characters/ and a labelled contact sheet to
art-src/previews/characters_preview.png. Pillow and numpy are the only
third-party dependencies; no source images, fonts or random seeds are used.

Sheets are native RGBA, 48 x 128: rows DOWN / UP / LEFT / RIGHT, columns
STAND / STEP_A / STEP_B (the engine plays A, STAND, B, STAND). RIGHT is the
mirror of LEFT, taken after compositing. Step frames lower everything above
the hips by one pixel (the walk bob) while the feet keep the bottom row.

Proportions follow GBA overworld sprites: a big head (14 x 14 px, eyes at
rows 10-11) on a 16 px body, feet on the bottom row. Builds: regular, broad
(heavy-set) and kid (three pixels shorter).

How a frame is built (all art is ASCII pixel grids, never drawing primitives):

1. A *body* grid for the build, direction and pose. Every pose is drawn
   whole: planted and lifted feet, the arm swing and the walk bob. Limbs use
   semantic roles that each outfit resolves at the end: z/Z upper arm,
   1/2 elbow, x/X forearm (so a style picks short, rolled or long sleeves),
   J/K shin and 3/4 ankle (shorts, socks).
2. Garment, accessory, hair and hat *layers*, painted in z order. A layer is
   directional art with an anchor (head / torso / waist / ground / hand), an
   optional role mask (it may only repaint those roles; '.' lets it grow the
   silhouette) and optional per-pose frames. '-' erases a pixel. Underlays
   (long hair, bags behind the body) paint only empty pixels. Carried items
   follow the hand found in each body pose.
3. The arms are stamped again over skirts, coat tails and wraps, then the
   bald head with its face, then hair, hats and glasses.
4. Semantic roles become materials and one dark outline is enforced.

Material roles (base / shadow / light):
  skin s k l   hair h H j   top t T u   bottom b B v   shoes f F g
  accent a A c   outer q Q r   hat p P i   extra 5 6 7   white w W
  gold y Y   metal n N   wood d D   red R   leaf G   eyes/ink e
  mouth m   outline O

Public API: Character(...), render_frame(character, direction, pose),
render_sheet(character) and the CHARACTERS presets. Colours accept Pillow
colour names or #rrggbb; hair also takes a HAIR_COLORS name.

Review art with ``--dev NAME[,NAME...] [--scale N] [--out PATH]`` (presets, or
style samplers such as hair_bun / top_saree / bottom_veshti; ``all`` draws
every preset), and ``--check`` to validate without writing.
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
import colorsys
import math

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont


FRAME_W, FRAME_H = 16, 32
SHEET_SIZE = (FRAME_W * 3, FRAME_H * 4)
DIRECTIONS = ("down", "up", "left", "right")
POSES = ("stand", "step_a", "step_b")
OUTLINE = "#2a2230"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets/images/characters"
PREVIEW_PATH = ROOT / "art-src/previews/characters_preview.png"

VALID_ROLES = set(".-O" "skl" "hHj" "tTu" "bBv" "fFg" "aAc" "qQr" "pPi" "567"
                  "wW" "yY" "nN" "dD" "RG" "em" "zZ12xXJK34")

def grid(text):
    """Parse and strictly check an ASCII grid; indentation is not artwork."""
    rows = tuple(line.strip() for line in text.strip().splitlines())
    if not rows or len({len(row) for row in rows}) != 1:
        raise ValueError(f"Ragged pixel grid: {rows!r}")
    unknown = set("".join(rows)) - VALID_ROLES
    if unknown:
        raise ValueError(f"Unknown pixel roles: {unknown}")
    return np.array([list(row) for row in rows], dtype="<U1")


def patch(x, y, text):
    return (x, y, grid(text))


def stamp(canvas, art, dy=0, mask=None, clip=False):
    """Composite one patch. ``mask`` lists the roles it may repaint.

    Patches must fit the frame unless ``clip`` is set (carried items).
    """
    x, y, pixels = art
    y += dy
    h, w = pixels.shape
    if x < 0 or y < 0 or x + w > FRAME_W or y + h > FRAME_H:
        if not clip:
            raise ValueError(f"Patch outside frame: {(x, y, w, h)}")
        x0, y0 = max(0, -x), max(0, -y)
        x1, y1 = min(w, FRAME_W - x), min(h, FRAME_H - y)
        if x0 >= x1 or y0 >= y1:
            return
        stamp(canvas, (x + x0, y + y0, pixels[y0:y1, x0:x1]), 0, mask)
        return
    region = canvas[y:y + h, x:x + w]
    paint = pixels != "."
    if mask is not None:
        paint &= np.isin(region, list(mask))
    region[paint] = np.where(pixels[paint] == "-", ".", pixels[paint])


def outline(canvas):
    """Keep exactly one ink pixel at the outer silhouette after layering."""
    solid = canvas != "."
    padded = np.pad(solid, 1)
    interior = (padded[:-2, 1:-1] & padded[2:, 1:-1]
                & padded[1:-1, :-2] & padded[1:-1, 2:])
    canvas[solid & ~interior] = "O"


# ---------------------------------------------------------------------------
# Bodies. Every pose is drawn whole: the planted foot, the lifted foot, the
# arm swing and the one-pixel bob are authored, not computed. Light comes from
# the upper left. Rows 0-15 belong to the head, which is stamped afterwards.
# ---------------------------------------------------------------------------

BODIES = {
    "regular": {
        "down": (patch(0, 16, """
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTxXO..
            ..OxXuttttTxXO..
            ..OskuttttTskO..
            ..OskbbbbbBskO..
            ..OOObbbbbBOOO..
            ....ObbbbbBO....
            ....ObbOObBO....
            ....ObbOObBO....
            ....OJKOOJKO....
            ....O34OO34O....
            ...OgfFOOgfFO...
            ...OOOOOOOOOO...
        """), patch(0, 16, """
            ................
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OskuttttTxXO..
            ..OskuttttTxXO..
            ..OOOuttttTskO..
            ....ObbbbbBskO..
            ....ObbbbbBOOO..
            ....ObbOObBO....
            ....ObbOOJKO....
            ....OJKOOgfFO...
            ....O34OOOOOO...
            ...OgfFO........
            ...OOOOO........
        """), patch(0, 16, """
            ................
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTskO..
            ..OxXuttttTskO..
            ..OskuttttTOOO..
            ..OskbbbbbBO....
            ..OOObbbbbBO....
            ....ObbOObBO....
            ....OJKOObBO....
            ...OgfFOOJKO....
            ...OOOOOO34O....
            ........OgfFO...
            ........OOOOO...
        """)),
        "up": (patch(0, 16, """
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTxXO..
            ..OxXuttttTxXO..
            ..OskuttttTskO..
            ..OskbbbbbBskO..
            ..OOObbbbbBOOO..
            ....ObbbbbBO....
            ....ObbOObBO....
            ....ObbOObBO....
            ....OJKOOJKO....
            ....O34OO34O....
            ...OFfFOOFfFO...
            ...OOOOOOOOOO...
        """), patch(0, 16, """
            ................
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OskuttttTxXO..
            ..OskuttttTxXO..
            ..OOOuttttTskO..
            ....ObbbbbBskO..
            ....ObbbbbBOOO..
            ....ObbOObBO....
            ....ObbOOJKO....
            ....OJKOOFfFO...
            ....O34OOOOOO...
            ...OFfFO........
            ...OOOOO........
        """), patch(0, 16, """
            ................
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..OzZuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTskO..
            ..OxXuttttTskO..
            ..OskuttttTOOO..
            ..OskbbbbbBO....
            ..OOObbbbbBO....
            ....ObbOObBO....
            ....OJKOObBO....
            ...OFfFOOJKO....
            ...OOOOOO34O....
            ........OFfFO...
            ........OOOOO...
        """)),
        "left": (patch(0, 16, """
            ....OtkkkktO....
            ...OuttzZttTO...
            ...OuttzZOtTO...
            ...Outt12OtTO...
            ...OuttxXOtTO...
            ...OuttxXOtTO...
            ...OuttskOtTO...
            ...ObbbskObBO...
            ...ObbbOOObBO...
            ...ObbbbbbbBO...
            ....ObbbbbBO....
            ....ObbbbbBO....
            .....OJJJKO.....
            .....O3334O.....
            ...OgffffFO.....
            ...OOOOOOOO.....
        """), patch(0, 16, """
            ................
            ....OtkkkktO....
            ...OuttzZttTO...
            ...OutttzZtTO...
            ...OutttO12TO...
            ...OuttttOxXO...
            ...OuttttOOxXO..
            ...ObbbbbbOskO..
            ...ObbbbbbOskO..
            ...ObbbbbbBOO...
            ..ObbbbOBBBBO...
            ..ObbbO.OBBBO...
            .OJJJO...OKKO...
            .O33O....OKK4O..
            OgffFO....OFFO..
            OOOOOO....OOOO..
        """), patch(0, 16, """
            ................
            ....OtkkkktO....
            ...OuttzZttTO...
            ...OutzZOttTO...
            ...Ou12OuttTO...
            ...OxXOuuttTO...
            ..OxXOuuuttTO...
            .OskObbbbbbBO...
            .OskObbbbbbBO...
            ..OOObbbbbbBO...
            ...OBBBOObbbbO..
            ..OBBBO..ObbbO..
            .OKKKO....OJJO..
            .OKK4O....OJJ3O.
            OFFFO......OgfFO
            OOOOO......OOOOO
        """)),
    },
    # Heavy-set adults: shoulders as wide as the head, 3-px legs, a belly.
    "broad": {
        "down": (patch(0, 16, """
            .OOOuttkkttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OxXuttttttTxXO.
            .OxXuttttttTxXO.
            .OskuttttttTskO.
            .OskbbbbbbbBskO.
            .OOObbbbbbbBOOO.
            ...ObbbbbbbBO...
            ...ObbbOObbBO...
            ...ObbbOObbBO...
            ...OJJKOOJJKO...
            ...O334OO334O...
            ..OgffFOOgffFO..
            ..OOOOOOOOOOOO..
        """), patch(0, 16, """
            ................
            .OOOuttkkttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OskuttttttTxXO.
            .OskuttttttTxXO.
            .OOOuttttttTskO.
            ...ObbbbbbbBskO.
            ...ObbbbbbbBOOO.
            ...ObbbOObbBO...
            ...ObbbOOJJKO...
            ...OJJKOOgffFO..
            ...O334OOOOOOO..
            ..OgffFO........
            ..OOOOOO........
        """), patch(0, 16, """
            ................
            .OOOuttkkttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OxXuttttttTskO.
            .OxXuttttttTskO.
            .OskuttttttTOOO.
            .OskbbbbbbbBO...
            .OOObbbbbbbBO...
            ...ObbbOObbBO...
            ...OJJKOObbBO...
            ..OgffFOOJJKO...
            ..OOOOOOO334O...
            ........OgffFO..
            ........OOOOOO..
        """)),
        "up": (patch(0, 16, """
            .OOOuttttttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OxXuttttttTxXO.
            .OxXuttttttTxXO.
            .OskuttttttTskO.
            .OskbbbbbbbBskO.
            .OOObbbbbbbBOOO.
            ...ObbbbbbbBO...
            ...ObbbOObbBO...
            ...ObbbOObbBO...
            ...OJJKOOJJKO...
            ...O334OO334O...
            ..OFffFOOFffFO..
            ..OOOOOOOOOOOO..
        """), patch(0, 16, """
            ................
            .OOOuttttttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OskuttttttTxXO.
            .OskuttttttTxXO.
            .OOOuttttttTskO.
            ...ObbbbbbbBskO.
            ...ObbbbbbbBOOO.
            ...ObbbOObbBO...
            ...ObbbOOJJKO...
            ...OJJKOOFffFO..
            ...O334OOOOOOO..
            ..OFffFO........
            ..OOOOOO........
        """), patch(0, 16, """
            ................
            .OOOuttttttTOOO.
            .OzzuttttttTzZO.
            .OzZuttttttTzZO.
            .O12uttttttT12O.
            .OxXuttttttTskO.
            .OxXuttttttTskO.
            .OskuttttttTOOO.
            .OskbbbbbbbBO...
            .OOObbbbbbbBO...
            ...ObbbOObbBO...
            ...OJJKOObbBO...
            ..OFffFOOJJKO...
            ..OOOOOOO334O...
            ........OFffFO..
            ........OOOOOO..
        """)),
        "left": (patch(0, 16, """
            ....OtkkkktO....
            ..OOuttzZttTO...
            ..OuttzzZOtTO...
            .Ouuttt12OtTO...
            .OuttttxXOtTO...
            .OuttttxXOtTO...
            .OuttttskOtTO...
            ..ObbbbskObBO...
            ..ObbbbOOObBO...
            ..ObbbbbbbbBO...
            ...ObbbbbbBO....
            ...ObbbbbbBO....
            ....OJJJJKO.....
            ....O33334O.....
            ..OgfffffFO.....
            ..OOOOOOOOO.....
        """), patch(0, 16, """
            ................
            ....OtkkkktO....
            ..OOuttzZttTO...
            ..OuttttzZtTO...
            .OuutttO12TO....
            .OuuttttOxXO....
            .OuuttttOOxXO...
            ..ObbbbbbOskO...
            ..ObbbbbbOskO...
            ..ObbbbbbbOO....
            .ObbbbbOBBBBO...
            .ObbbbO.OBBBO...
            OJJJJO...OKKKO..
            O333O....OKKK4O.
            OgffFO....OFFFO.
            OOOOOO....OOOOO.
        """), patch(0, 16, """
            ................
            ....OtkkkktO....
            ..OOuttzZttTO...
            ..OutzZOttttTO..
            .Ou12OuuttttTO..
            .OxXOuuuttttTO..
            OxXOuuuuttttTO..
            OskObbbbbbbBO...
            OskObbbbbbbBO...
            .OOObbbbbbbBO...
            ..OBBBBOObbbbO..
            ..OBBBO..ObbbO..
            .OKKKKO...OJJJO.
            .OKKK4O...OJJ3O.
            OFFFFO.....OgfFO
            OOOOOO.....OOOOO
        """)),
    },
    # Children: the same head, a body three pixels shorter.
    "kid": {
        "down": (patch(0, 19, """
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTxXO..
            ..OskuttttTskO..
            ..OskbbbbbBskO..
            ..OOObbbbbBOOO..
            ....ObbOObBO....
            ....OJKOOJKO....
            ....OJKOOJKO....
            ....O34OO34O....
            ...OgfFOOgfFO...
            ...OOOOOOOOOO...
        """), patch(0, 19, """
            ................
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..OskuttttT12O..
            ..OskuttttTxXO..
            ..OOOuttttTskO..
            ....ObbbbbBskO..
            ....ObbOObBOOO..
            ....OJKOOJKO....
            ....OJKOOgfFO...
            ....O34OOOOOO...
            ...OgfFO........
            ...OOOOO........
        """), patch(0, 19, """
            ................
            ..OOuttkkttTOO..
            ..OzzuttttTzZO..
            ..O12uttttTskO..
            ..OxXuttttTskO..
            ..OskuttttTOOO..
            ..OskbbbbbBO....
            ..OOObbOObBO....
            ....OJKOOJKO....
            ...OgfFOOJKO....
            ...OOOOOO34O....
            ........OgfFO...
            ........OOOOO...
        """)),
        "up": (patch(0, 19, """
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..O12uttttT12O..
            ..OxXuttttTxXO..
            ..OskuttttTskO..
            ..OskbbbbbBskO..
            ..OOObbbbbBOOO..
            ....ObbOObBO....
            ....OJKOOJKO....
            ....OJKOOJKO....
            ....O34OO34O....
            ...OFfFOOFfFO...
            ...OOOOOOOOOO...
        """), patch(0, 19, """
            ................
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..OskuttttT12O..
            ..OskuttttTxXO..
            ..OOOuttttTskO..
            ....ObbbbbBskO..
            ....ObbOObBOOO..
            ....OJKOOJKO....
            ....OJKOOFfFO...
            ....O34OOOOOO...
            ...OFfFO........
            ...OOOOO........
        """), patch(0, 19, """
            ................
            ..OOuttttttTOO..
            ..OzzuttttTzZO..
            ..O12uttttTskO..
            ..OxXuttttTskO..
            ..OskuttttTOOO..
            ..OskbbbbbBO....
            ..OOObbOObBO....
            ....OJKOOJKO....
            ...OFfFOOJKO....
            ...OOOOOO34O....
            ........OFfFO...
            ........OOOOO...
        """)),
        "left": (patch(0, 19, """
            ....OtkkkktO....
            ...OuttzZttTO...
            ...Outt12OtTO...
            ...OuttxXOtTO...
            ...OuttskOtTO...
            ...ObbbskObBO...
            ...ObbbOOObBO...
            ....ObbbbbBO....
            .....OJJJKO.....
            .....OJJJKO.....
            .....O3334O.....
            ...OgffffFO.....
            ...OOOOOOOO.....
        """), patch(0, 19, """
            ................
            ....OtkkkktO....
            ...OuttzZttTO...
            ...OutttO12TO...
            ...OuttttOxXO...
            ...ObbbbbOOskO..
            ...ObbbbbbOskO..
            ..ObbbbOBBOOO...
            ..ObbbO.OBBBO...
            .OJJJO...OKKO...
            .O33O....OKK4O..
            OgffFO....OFFO..
            OOOOOO....OOOO..
        """), patch(0, 19, """
            ................
            ....OtkkkktO....
            ...OuttzZttTO...
            ...Ou12OuttTO...
            ..OxXOuuttTTO...
            .OskObbbbbbBO...
            .OskObbbbbbBO...
            ..OOOBBOObbbO...
            ..OBBBO..ObbbO..
            .OKKKO....OJJO..
            .OKK4O....OJJ3O.
            OFFFO......OgfFO
            OOOOO......OOOOO
        """)),
    },
}

# Bald heads with faces, at the regular head position (rows 2-15). Eyes are
# 1 x 2, the nose a single shadow pixel, the mouth two deep-shadow pixels.
HEADS = {
    "down": patch(0, 2, """
        .....OOOOOO.....
        ...OOllllssOO...
        ..OllllssssssO..
        .OlllsssssssskO.
        .OllssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlswessssewskO.
        OklssessssesskkO
        OkllsssskssslkkO
        ..OlsssmmssskO..
        ...OlsssssskO...
        ....OOOOOOOO....
    """),
    "up": patch(0, 2, """
        .....OOOOOO.....
        ...OOllllssOO...
        ..OllllssssssO..
        .OlllsssssssskO.
        .OllssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        ..OlsssssssskO..
        ...OlsssssskO...
        ....OOOOOOOO....
    """),
    "left": patch(0, 2, """
        .....OOOOOO.....
        ...OOllllssOO...
        ..OllllssssssO..
        .OlllsssssssskO.
        .OllssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OlsssssssssskO.
        .OsewsssssssskO.
        .OsessssssssskO.
        OssssssssssskO..
        .OmsssssssskO...
        ..OOsssssskO....
        ....OOkkkkO.....
    """),
}


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

# How far each anchor sits from its regular-build position.
BUILDS = {
    "regular": {"head": 0, "torso": 0, "waist": 0, "ground": 0},
    "broad": {"head": 0, "torso": 0, "waist": 0, "ground": 0},
    "kid": {"head": 3, "torso": 3, "waist": 1, "ground": 0},
}

# Role groups for masks.
TORSO = "tTu"
ARMS = "zZ12xX"
HANDS = "sk"
LEGS = "bBvJK34"
SHOES = "fFg"
EMPTY = "."

# Paint order (lower first). The head is stamped at Z_HEAD.
Z_LEGWEAR, Z_TOP, Z_OUTER, Z_ARMS, Z_STRAP, Z_HEAD = 10, 20, 30, 39, 40, 50
Z_FACE, Z_HAIR, Z_HAT, Z_GLASSES, Z_HELD = 60, 70, 80, 90, 100


@dataclass(frozen=True)
class Layer:
    """Directional art: {direction: patch | (stand, step_a, step_b)}.

    Single patches follow the walk bob unless anchored to the ground. Pose
    tuples are authored in place, bob included. ``mask`` restricts which
    roles may be repainted ('.' lets the layer grow the silhouette);
    ``under`` paints only empty pixels, i.e. behind everything else.
    """
    art: tuple
    z: int = Z_TOP
    anchor: str = "torso"
    mask: str | None = None
    under: bool = False


def L(z, anchor="torso", mask=None, under=False, **art):
    """Shorthand: L(Z_TOP, down=patch(...), up=..., left=...)."""
    return Layer(art=tuple(art.items()), z=z, anchor=anchor, mask=mask, under=under)


def poses(stand, step_a, step_b):
    return (stand, step_a, step_b)


def apply_layer(canvas, layer, build, direction, pose):
    art = dict(layer.art).get(direction)
    if art is None:
        return
    if art[0] == "hand":
        _, side, dx, dy, pixels = art
        hx, hy = hand_point(build, direction, pose, side)
        stamp(canvas, (hx + dx, hy + dy, pixels), 0, layer.mask, clip=True)
        return
    if isinstance(art[0], tuple):
        art = art[POSES.index(pose)]
        dy = 0
    else:
        dy = int(pose != "stand" and layer.anchor != "ground")
    dy += BUILDS[build][layer.anchor]
    stamp(canvas, art, dy, EMPTY if layer.under else layer.mask)


# ---------------------------------------------------------------------------
# Hair. Front art covers the bald crown; '.' keeps the face. Long styles add
# an underlay that hangs behind the shoulders.
# ---------------------------------------------------------------------------

def hair(front, back=None):
    layers = [Layer(art=tuple(front.items()), z=Z_HAIR, anchor="head")]
    if back:
        layers.append(Layer(art=tuple(back.items()), z=Z_HAIR, anchor="head",
                            under=True))
    return tuple(layers)


HAIR = {
    "bald": (
        Layer(art=(
            ("down", patch(3, 3, """
                .ll..
                lll..
                l....
            """)),
            ("up", patch(3, 3, """
                .ll..
                lll..
                l....
            """)),
            ("left", patch(4, 3, """
                .lll.
                lll..
                l....
            """)),
        ), z=Z_HAIR, anchor="head"),
    ),
    # A ring of hair above the ears and round the back; the crown is bare.
    "balding": hair({
        "down": patch(0, 3, """
            ...ll...........
            ..lll...........
            ..l.............
            ................
            .Oh..........hO.
            OhjH........HjhO
            OhhH........HhhO
            OhH..........HhO
        """),
        "up": patch(0, 3, """
            ...ll...........
            ..lll...........
            ..l.............
            ................
            .Oh..........hO.
            OhjHH......HHjhO
            OhjhhHHHHHHhhHhO
            OhhhhhhhhhhhHHHO
            .OhhhhhhhhhhHHO.
            .OsHhhhhhhhHHkO.
            ...OHHHHHHHHO...
        """),
        "left": patch(0, 3, """
            ...lll..........
            ..lll...........
            ..l.............
            ............HhO.
            ..........HhhhHO
            .........HhjhHHO
            ........HhhhHHHO
            .......HsshHHHO.
            .......HskHHHO..
            ........OHHHO...
        """),
    }),
    "short": hair({
        "down": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhhjjhhhhhhhHO.
            .OhjhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhHkkkkkHHhHHO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhhjjhhhhhhhHO.
            .OhjhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhHHHO.
            .OhhhhhhhhhHHHO.
            .OsHhhhhhhhHHkO.
            ...OHHHHHHHHO...
        """),
        "left": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhhjjhhhhhhhHO.
            .OhjhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OHhhhhhhhhhHHO.
            .OkkHhhhhhhHHHO.
            ......HsshHHHO..
            ......HskHHHO...
            .......OHHHO....
        """),
    }),
    # Close crop: the skull shape shows through.
    "buzz": hair({
        "down": patch(0, 1, """
            ................
            ....OOOOOOOO....
            ...OhhjjhhhhO...
            ..OhjjhhhhhhHO..
            .OhjhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OHkkkkkkkkkkHO.
            .OH..........HO.
        """),
        "up": patch(0, 1, """
            ................
            ....OOOOOOOO....
            ...OhhjjhhhhO...
            ..OhjjhhhhhhHO..
            .OhjhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhHHHO.
            .OsHhhhhhhhHHkO.
            ...OHHHHHHHHO...
        """),
        "left": patch(0, 1, """
            ................
            ....OOOOOOOO....
            ...OhhjjhhhhO...
            ..OhjjhhhhhhHO..
            .OhjhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OkkkHhhhhhhHHO.
            .O....HhhhhhHHO.
            .......HsshHHHO.
            .......HskHHHO..
            ........OHHHO...
        """),
    }),
    "spiky": hair({
        "down": patch(0, 0, """
            ......O...O.....
            ....OOhO.OhOO...
            ...OhhjhOhjhhO..
            ..OhjjhhhjjhhhO.
            .OhjjhhhjjhhhhHO
            OhjjhhhhhhhhhhHO
            OhhhhhhhhhhhhhHO
            OhhhhhhhhhhhhHHO
            OhHhkkhHkkhhkHHO
            .Oh.........hHO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ......O...O.....
            ....OOhO.OhOO...
            ...OhhjhOhjhhO..
            ..OhjjhhhjjhhhO.
            .OhjjhhhjjhhhhHO
            OhjjhhhhhhhhhhHO
            OhhhhhhhhhhhhhHO
            OhhhhhhhhhhhhHHO
            OhhhhhhhhhhhhHHO
            OhhhhhhhhhhhHHHO
            .OhhhhhhhhhhHHO.
            .OsHhHhhHhHhHkO.
            ...OHOHHOHHOO...
            ....O.OO.OO.....
        """),
        "left": patch(0, 0, """
            .......O..O.....
            .....OOhOOhOO...
            ...OOhjhhjhhhO..
            ..OhhjjhhjjhhhO.
            .OhjjhhhhhhhhhHO
            OhjhhhhhhhhhhhHO
            OhhhhhhhhhhhhhHO
            OhHhhhhhhhhhhHHO
            OOkHkHhhhhhhHHHO
            .O..k.HhhhhhHHHO
            .......HsshHHHHO
            .......HskHHHHO.
            ........OHHHHO..
            ........OHOHO...
        """),
    }),
    # Sudeep: a tall spiky quiff over tight sides, gold aviators pushed up
    # onto it (dark lenses with a glint).
    "quiff": hair({
        "down": patch(0, 0, """
            ...O.OO.O.O.....
            ..OhOjhOjOhO....
            ..OhjjhjjhhhOO..
            .OhyyyhhhhyyyHO.
            .OyneeyyyyneeyO.
            .OyeeeyhhyeeeyO.
            .OhYeYhhhhYeYHO.
            .OhhhhhhhhhhHHO.
            .OhHhhHhhHhhHHO.
            .OHkHkkkkkHkHHO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ...O.OO.O.O.....
            ..OhOjhOjOhO....
            ..OhjjhjjhhhOO..
            .OhjjhhhhhhhhHO.
            .yhjhhhhhhhhhHy.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhHHHO.
            .OHhhhhhhhhHHHO.
            .OsHhHhhHhHhHkO.
            ...OHOHHOHHO....
        """),
        "left": patch(0, 0, """
            .O.OO.O.........
            OhOjhOjOO.......
            OhjjhjhhhOOO....
            OyyyyhhhhhhhOO..
            OneeyyyyyyhhhHO.
            OeeeyhhhhhhhhHO.
            .OeYhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            OhHhhhhhhhhhHHO.
            .OkHkHhhhhhHHHO.
            ......HsshHHHO..
            ......HskHHHO...
            .......OHHHO....
        """),
    }),
    # Combed back with a side parting and a sheen.
    "slick": hair({
        "down": patch(0, 1, """
            .....OOOOOO.....
            ...OOjjjHhhOO...
            ..OhjjjHhhhhhO..
            .OhjjjHhhhhhhHO.
            .OhjjHhhhhhhhHO.
            OhhjHhhhhhhhhHHO
            OhhHkkhhhhhhHHHO
            OhHk..kkkhhhHHHO
            .OH.......kHHHO.
            .OH..........HO.
        """),
        "up": patch(0, 1, """
            .....OOOOOO.....
            ...OOjjjhhhOO...
            ..OhjjjhhhhhhO..
            .OhjjjhhhhhhhHO.
            .OhjjhhhhhhhhHO.
            OhhjhhhhhhhhhHHO
            OhhjhhhhhhhhhHHO
            OhhhhhhhhhhhHHHO
            OhhhhhhhhhhhHHHO
            .OhhhhhhhhhhHHO.
            .OsHhhhhhhhHHkO.
            ...OHHHHHHHHO...
        """),
        "left": patch(0, 1, """
            .....OOOOOO.....
            ...OOjjjjhhOO...
            ..OhjjjjhhhhhO..
            .OhhhhjjjhhhhHO.
            .OkkhhhhjjhhhHO.
            O..kkhhhhhhhhHHO
            O....khhhhhhHHHO
            O.....HhhhhhHHHO
            .O.....HhhhhHHHO
            .......HsshHHHO.
            .......HskHHHO..
            ........OHHHO...
        """),
    }),
    # Tousled, with strands across the forehead.
    "messy": hair({
        "down": patch(0, 0, """
            ................
            ....OO.OOOO.....
            ...OhhOhjjhOO...
            ..OhjjhhjjhhhO..
            .OhjjhhhhhhhhHO.
            OhjhhhhhjhhhhHHO
            OhhhhhhhhhhhhhHO
            OhhhhhhhhhhhhHHO
            OhHhhHkhhhHhhHHO
            OHhkHkkhHkkHkHHO
            .Oh..k...k...hO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ................
            ....OO.OOOO.....
            ...OhhOhjjhOO...
            ..OhjjhhjjhhhO..
            .OhjjhhhhhhhhHO.
            OhjhhhhhjhhhhHHO
            OhhhhhhhhhhhhhHO
            OhhhhhhhhhhhhHHO
            OhhhhhhhhhhhhHHO
            OhhhhhhhhhhhHHHO
            .OhhhhhhhhhhHHO.
            .OsHhhHhhHhHHkO.
            ..OOHHOHHHOHOO..
            ....OO.OOO.O....
        """),
        "left": patch(0, 0, """
            ................
            ....OO.OOOO.....
            ...OhhOhjjhOO...
            ..OhjjhhjjhhhO..
            .OhjjhhhhhhhhHO.
            OhjhhhhhjhhhhHHO
            OhhhhhhhhhhhhhHO
            OhHhhhhhhhhhhHHO
            OkHkhHhhhhhhHHHO
            .O.k..HhhhhhHHHO
            .......HsshHHHHO
            .......HskHHHHO.
            ........OHHHHO..
            ........OOHOO...
        """),
    }),
    "curly": hair({
        "down": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OHhHhHhHhHhHhHHO
            OhjkHjkHjkHjhHHO
            .OHk........HHO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OHhHhHhHhHhHhHHO
            OhjhhjhhjhhjhHHO
            OhHhhHhhHhhHhHHO
            .OhjhhjhhjhhHHO.
            .OsHhHhHhHhHHkO.
            ..OOHOHHOHHOOO..
            ....O.OO.OO.....
        """),
        "left": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OkHhHhHhHhHhHHHO
            OkHkhjhhjhhjhHHO
            .O.k..HhhHhhHHHO
            .......HsshjHHHO
            .......HskHhHHO.
            ........OHHHHO..
            ........OOHOO...
        """),
    }),
    # Big curls that fall past the jaw (Tanvi, college students). Each curl
    # is a lit pixel over a shadowed one, staggered row by row.
    "curly-long": hair({
        "down": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OHhHhHhHhHhHhHHO
            OhjkHjkHjkHjhHHO
            OjHk........HjHO
            OhH..........HhO
            OjhH........HjHO
            OhHO........OHhO
            .OO..........OO.
        """),
        "up": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OHhHhHhHhHhHhHHO
            OhjhhjhhjhhjhHHO
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OHhHhHhHhHhHhHHO
            OhjhhjhhjhhjhHHO
            .OHhHHhHHhHHHHO.
            .OHHOHHOHHOHHO..
            ..OO.OO.OO.OO...
        """),
        "left": patch(0, 0, """
            ................
            ....OO.OO.OO....
            ...OjhOjhOjhO...
            ..OhhHhhHhhHhO..
            .OjhhjhhjhhjhHO.
            OhHhhHhhHhhHhHHO
            OhjhhjhhjhhjhHHO
            OkHhHhHhHhHhHHHO
            OkHkhjhhjhhjhHHO
            .O.k..HhhHhhHHHO
            ......HssjhhjHHO
            ......OHskHhHhHO
            .......OHhjhhjHO
            ........OHhHHHO.
            .........OHHHO..
            ..........OOO...
        """),
    }, {
        "down": patch(0, 13, """
            OhO..........OhO
            OHjO........OjHO
            .OO..........OO.
        """),
    }),
    # Centre parting pulled back (buns, braids, long hair share it).
    "parted": hair({
        "down": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhjHHjhOO...
            ..OhjjhHHhjjhO..
            .OhjjhhHHhhjjhO.
            .OjhhhhHHhhhhjO.
            .OhhhhHkkHhhhhO.
            .OhhhHk..kHhhhO.
            .OhhHk....kHhhO.
            .OhH........HhO.
            .OH..........HO.
            .OH..........HO.
        """),
        "up": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhhjjhhhhhhhHO.
            .OhjhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhHHHO.
            .OhhhhhhhhhHHHO.
            .OsHhhhhhhhHHkO.
            ...OHHHHHHHHO...
        """),
        "left": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhjjjhhOO...
            ..OhhjjjhhhhhO..
            .OhjjhhhhhhhhHO.
            .OjhhhhhhhhhhHO.
            .OkhhhhhhhhhhHO.
            .O.kkhhhhhhhHHO.
            .O...kHhhhhhHHO.
            .O....HhhhhHHHO.
            ......HsshHHHO..
            ......HskHHHO...
            .......OHHHO....
        """),
    }),
    # Bangs and long side locks (girls).
    "fringe": hair({
        "down": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhjjhhhhhhhhHO.
            .OjhhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhHhhHhhHhHHO.
            OhHkhHkkHkhHkHHO
            OhH..........HhO
            OhH..........HhO
            OhH..........HhO
            .OO..........OO.
        """),
        "up": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhhjjhhhhhhhHO.
            .OhjhhhhhhhhhHO.
            .OhhhhhhhhhhhHO.
            .OhhhhhhhhhhHHO.
            .OhhhhhhhhhhHHO.
            OhhhhhhhhhhHHHHO
            OhhhhhhhhhhHHHHO
            OhHhhhhhhhhHHHHO
            OhHOHHHHHHHHOHHO
            .OO.OOOOOOOO.OO.
        """),
        "left": patch(0, 0, """
            ................
            .....OOOOOO.....
            ...OOhhjjhhOO...
            ..OhhjjjjhhhhO..
            .OhjjhhhhhhhhHO.
            OhjhhhhhhhhhhHHO
            OhhhhhhhhhhhhhHO
            OhhhhhhhhhhhhHHO
            OhHhHhhhhhhhHHHO
            OHkHkHhhhhhhHHHO
            .O....HhhhhhHHHO
            ......HsshhHHHO.
            ......HskhHHHO..
            .......OHHHHO...
        """),
    }),
}

# Styles built on the centre parting, plus what hangs off the back.
HAIR["bun"] = HAIR["parted"] + (
    Layer(art=(
        ("down", patch(11, 3, """
            .OOO.
            OjjhO
            OjhhO
            OhhHO
            .OOO.
        """)),
        ("up", patch(4, 9, """
            ..OOOO..
            .OjjhhO.
            OjjhhhHO
            OjhhhHHO
            OhhhHHHO
            .OHHHHO.
            ..OOOO..
        """)),
        ("left", patch(11, 6, """
            .OOO.
            OjjhO
            OjhhO
            OhhHO
            OhHHO
            .OOO.
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
)
HAIR["topknot"] = HAIR["parted"] + (
    Layer(art=(
        ("down", patch(4, 0, """
            ..OOOO..
            .OjjhhO.
            .OjhhHO.
            ..OHHO..
        """)),
        ("up", patch(4, 0, """
            ..OOOO..
            .OjjhhO.
            .OhhhHO.
            ..OHHO..
        """)),
        ("left", patch(5, 0, """
            ..OOOO..
            .OjjhhO.
            .OjhhHO.
            ..OHHO..
        """)),
    ), z=Z_HAIR + 1, anchor="head", mask=".hHjO"),
)
HAIR["ponytail"] = HAIR["fringe"] + (
    Layer(art=(
        ("up", patch(5, 1, """
            ..OO..
            .OaaO.
            OhjjhO
            OhjjHO
            OhjhHO
            OhjhHO
            OhjhHO
            OhhhHO
            .OjhHO
            .OjhHO
            .OhhHO
            .OhHHO
            ..OhHO
            ..OHHO
            ...OO.
        """)),
        ("left", patch(10, 1, """
            ..OO..
            .OaaO.
            OhjhHO
            OhjjhO
            .OjjhO
            .OhjHO
            ..OjhO
            ..OhHO
            ..OhjO
            ..OhHO
            ...OHO
            ....O.
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
    # From the front the tail flicks out behind the crown.
    Layer(art=(("down", patch(11, 0, """
            ..OOO
            .OaaO
            OhjhO
            OhjHO
            .OhHO
            ..OHO
            ...OO
        """)),), z=Z_HAIR, anchor="head", under=True),
)
HAIR["braid"] = HAIR["parted"] + (
    Layer(art=(
        ("up", patch(6, 11, """
            OhhO
            OjHO
            OHjO
            OjHO
            OHjO
            OjHO
            OHjO
            OjHO
            OaaO
            OhhO
            .OO.
        """)),
        ("left", patch(11, 10, """
            OhhO
            OjHO
            OHjO
            OjHO
            OHjO
            OjHO
            OHjO
            OaaO
            OhhO
            .OO.
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
)
HAIR["side braid"] = HAIR["parted"] + (
    Layer(art=(
        ("down", patch(11, 11, """
            .OO.
            OhjO
            OjHO
            OHjO
            OjHO
            OHjO
            OjHO
            OHjO
            OaaO
            OhhO
            .OO.
        """)),
        ("left", patch(11, 10, """
            OhhO
            OjHO
            OHjO
            OjHO
            OHjO
            OjHO
            OHjO
            OaaO
            OhhO
            .OO.
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
)
HAIR["pigtails"] = HAIR["parted"] + (
    Layer(art=(
        ("down", patch(0, 10, """
            OaO..........OaO
            OaO..........OaO
            OjO..........OjO
            OHhO........OhHO
            OjHO........OHjO
            OHhO........OhHO
            OjHO........OHjO
            OaaO........OaaO
            OhhO........OhhO
            .OO..........OO.
        """)),
        ("up", patch(1, 10, """
            OaaO......OaaO
            OjHO......OHjO
            OHjO......OjHO
            OjHO......OHjO
            OHjO......OjHO
            OjHO......OHjO
            OaaO......OaaO
            OhhO......OhhO
            .OO........OO.
        """)),
        ("left", patch(9, 10, """
            OaaO
            OjHO
            OHjO
            OjHO
            OHjO
            OaaO
            OhhO
            .OO.
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
)
HAIR["long"] = HAIR["parted"] + (
    Layer(art=(
        ("down", patch(0, 9, """
            OhH..........HhO
            OjH..........HhO
            OhH..........HjO
            OhHO........OHhO
            OjHO........OHhO
            OhHO........OHjO
        """)),
        ("up", patch(1, 9, """
            OhjhhhhhjhhhHO
            OhjhhhhhjhhHHO
            OhjhhhhhjhhHHO
            OhjhhhhhhhhHHO
            OhhhhhhhhjhHHO
            OhhjhhhhhjHHHO
            OhhjhhhhhhHHHO
            OHhhhhhhhhHHHO
            .OHhHhOHhHHHO.
            ..OO.O.OO.OO..
        """)),
        ("left", patch(8, 8, """
            .OhhhhhO
            .HsshhHO
            .HskhjHO
            ..OhhjHO
            ..OhhhHO
            ..OhjhHO
            ..OhjhHO
            ..OhhHHO
            ...OHHO.
            ....OO..
        """)),
    ), z=Z_HAIR + 1, anchor="head"),
    Layer(art=(("down", patch(0, 15, """
            OhHO........OHhO
            OhHO........OHhO
            OHHO........OHHO
            .OO..........OO.
        """)),), z=Z_HAIR, anchor="head", under=True),
)

HAIR["bob"] = hair({
    "down": patch(0, 0, """
        ................
        .....OOOOOO.....
        ...OOhhjjhhOO...
        ..OhhjjjjhhhhO..
        .OhjjhhhhhhhhHO.
        OhjhhhhhhhhhhHHO
        OhhhhhhhhhhhhhHO
        OhhhhhhhhhhhhHHO
        OhhHHHHHHHHhhHHO
        OhHkkkkkkkkkHHHO
        OhH..........HHO
        OjH..........HhO
        OhHO........OHHO
        .OO..........OO.
    """),
    "up": patch(0, 0, """
        ................
        .....OOOOOO.....
        ...OOhhjjhhOO...
        ..OhhjjjjhhhhO..
        .OhhjjhhhhhhhHO.
        OhhjhhhhhhhhhHHO
        OhhhhhhhhhhhhhHO
        OhhhhhhhhhhhhHHO
        OhhhhhhhhhhhhHHO
        OhhhhhhhhhhhHHHO
        OhhhhhhhhhhhHHHO
        OjhhhhhhhhhhHhHO
        OhHHHHHHHHHHHHHO
        .OOOOOOOOOOOOOO.
    """),
    "left": patch(0, 0, """
        ................
        .....OOOOOO.....
        ...OOhhjjhhOO...
        ..OhhjjjjhhhhO..
        .OhjjhhhhhhhhHO.
        OhjhhhhhhhhhhHHO
        OhhhhhhhhhhhhhHO
        OhHHHhhhhhhhhHHO
        OkkkHHhhhhhhHHHO
        .O...HhhhhhhHHHO
        .....HhhhhhhHhHO
        .....OHhhhhHHjHO
        .....OHHHHHHHHHO
        ......OOOOOOOOO.
    """),
})


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

# Explicit ramps keep warmth in every skin tone. Order: base, shadow, light.
SKIN_TONES = {
    "wheat": ("#dca875", "#b87851", "#f0c694"),
    "honey": ("#c68b58", "#9d603f", "#e0aa71"),
    "copper": ("#ad7149", "#815039", "#cf9460"),
    "brown": ("#8e573c", "#673d30", "#b57b50"),
    "deep": ("#6c4234", "#4f302c", "#945f43"),
    "umber": ("#7d4b32", "#57342b", "#a26a45"),
}
FIXED = {
    "white": ("#f1ece0", "#c5bfc0", "#ffffff"),
    "gold": ("#e6b84a", "#a8742e", "#fbe08a"),
    "metal": ("#b8c4c6", "#7d8790", "#e8eef0"),
    "wood": ("#9a6c43", "#6c4632", "#bf8d5c"),
    "red": ("#d23b3b", "#9c2836", "#f06a5a"),
    "leaf": ("#4f9a4a", "#356b3e", "#7cc067"),
}


def rgb(color):
    value = ImageColor.getrgb(color)
    if len(value) != 3:
        raise ValueError(f"Colours must be RGB, without alpha: {color!r}")
    return value


def ramp(color):
    """Base, shadow, light: shadows cool toward violet, lights warm and lift.

    A tuple of three colours is taken as an explicit ramp.
    """
    if isinstance(color, tuple):
        return tuple(rgb(c) for c in color)
    r, g, b = (c / 255 for c in rgb(color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    def shift(hue, target, amount):
        delta = ((target - hue + .5) % 1) - .5
        return (hue + delta * amount) % 1

    def to255(hls):
        return tuple(int(round(min(1, max(0, c)) * 255))
                     for c in colorsys.hls_to_rgb(*hls))

    shadow = to255((shift(h, .72, .12 if s > .08 else 0), l * .70, min(1, s * 1.05)))
    light = to255((shift(h, .14, .08 if s > .08 else 0), l + (1 - l) * .30, s * .95))
    base = tuple(max(14, c) for c in to255((h, l, s)))
    return base, shadow, light


# Hair needs bright cool highlights to read against the dark outline.
HAIR_COLORS = {
    "black": ("#3e3548", "#28212f", "#74688c"),
    "dark brown": ("#4a3530", "#30221f", "#7e5c4c"),
    "brown": ("#6e4a32", "#4a3024", "#a2744c"),
    "grey": ("#9c9a98", "#6c6a70", "#cbc8c2"),
    "salt": ("#6e6a72", "#48444e", "#a6a2a8"),
    "white": ("#dcd8d0", "#9c98a6", "#faf7f0"),
}

MATERIAL_ROLES = {
    "skin": "skl", "hair": "hHj", "top": "tTu", "bottom": "bBv",
    "shoes": "fFg", "accent": "aAc", "outer": "qQr", "hat": "pPi",
    "extra": "567", "white": "wW", "gold": "yY", "metal": "nN", "wood": "dD",
    "red": "R", "leaf": "G",
}


# ---------------------------------------------------------------------------
# Garment styles
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Top:
    sleeves: str = "short"      # none | short | rolled | elbow | long
    sleeve: str = "top"         # material the sleeves are made of
    layers: tuple = ()


@dataclass(frozen=True)
class Bottom:
    legs: str = "long"          # long | shorts
    layers: tuple = ()


NOT_HANDS = ".OtTubBvJK34fFgzZ12xX"

# Ankle-length wraps (saree, veshti, long skirt): authored per pose and
# anchored to the ground so the hem hangs still while the feet alternate.
# 't' is the garment (mapped to the right material by each style), 'a' the
# border; pleats are drawn in shadow.
WRAP_DOWN = poses(patch(3, 23, """
    ..uttttT..
    .OuttTtTTO
    .OuttTtTTO
    OuuttTttTO
    OuttTtTtTO
    OutttTttTO
    OaaaaaaaAO
    OOgfOOgfOO
    .OOOOOOOO.
"""), patch(3, 24, """
    ..uttttT..
    .OuttTtTTO
    OuuttTtTTO
    OutttTttTO
    OuttTtTtTO
    OaaaaaaaAO
    OOgfOOOOOO
    .OOOO.....
"""), patch(3, 24, """
    ..uttttT..
    .OuttTtTTO
    OuuttTtTTO
    OutttTttTO
    OuttTtTtTO
    OaaaaaaaAO
    OOOOOOgfOO
    .....OOOO.
"""))
WRAP_UP = poses(patch(3, 23, """
    ..uttttT..
    .OuttttTTO
    .OuttttTTO
    OuuttttTTO
    OutttttTTO
    OutttttTTO
    OaaaaaaaAO
    OOFfOOFfOO
    .OOOOOOOO.
"""), patch(3, 24, """
    ..uttttT..
    .OuttttTTO
    OuuttttTTO
    OutttttTTO
    OutttttTTO
    OaaaaaaaAO
    OOFfOOOOOO
    .OOOO.....
"""), patch(3, 24, """
    ..uttttT..
    .OuttttTTO
    OuuttttTTO
    OutttttTTO
    OutttttTTO
    OaaaaaaaAO
    OOOOOOFfOO
    .....OOOO.
"""))
WRAP_LEFT = poses(patch(2, 23, """
    .OuuuttttTO.
    .OuuuttttTO.
    .OuttTtttTO.
    .OuttTtttTO.
    OuuttTttttTO
    OuttTttttTTO
    OaaaaaaaaaAO
    OgffffFOOOOO
    OOOOOOOO....
"""), patch(1, 24, """
    ..OuuuttttTO.
    ..OuuuttttTO.
    .OuuttTtttTO.
    .OuttTttttTO.
    OuuttTttttTTO
    OaaaaaaaaaaAO
    OgffFOOOOOOOO
    OOOOOO.......
"""), patch(1, 24, """
    ..OuuuttttTO.
    ..OuuuttttTO.
    ..OuuttTtttTO
    .OuuttTttttTO
    .OuttTttttTTO
    .OaaaaaaaaaAO
    OFFfOOOOOOOOO
    OOOOO........
"""))

# Knee-length wraps (skirt, folded veshti, lungi, kurta and coat hems) hang
# from the waist and bob with the body.
KNEE_DOWN = patch(3, 23, """
    ..uttttT..
    .OuttttTTO
    .OuttttTTO
    OuuttttTTO
    OutttttTTO
    OOOOOOOOOO
""")
KNEE_LEFT = patch(2, 23, """
    .OuuuttttTO.
    .OuuuttttTO.
    .OuttttttTO.
    OuuttttttTO.
    OutttttttTTO
    OOOOOOOOOOOO
""")


def wrap(material, border="a", mask=NOT_HANDS, z=Z_LEGWEAR):
    """Recolour the wrap templates: 't' -> material ramp, 'a' -> border."""
    base = MATERIAL_ROLES[material]
    trim = MATERIAL_ROLES.get(border, border)
    table = {"t": base[0], "T": base[1], "u": base[2] if len(base) > 2 else base[0],
             "a": trim[0], "A": trim[1] if len(trim) > 1 else trim[0]}

    def recolor(art):
        if isinstance(art[0], tuple):
            return tuple(recolor(a) for a in art)
        x, y, pixels = art
        out = pixels.copy()
        for role, target in table.items():
            out[pixels == role] = target
        return (x, y, out)

    art = {"down": WRAP_DOWN, "up": WRAP_UP, "left": WRAP_LEFT}
    return Layer(art=tuple((d, recolor(a)) for d, a in art.items()), z=z,
                 anchor="ground", mask=mask)


def knee(material, border=None, z=Z_LEGWEAR, anchor="waist"):
    """A knee-length hem; ``border`` recolours its lowest cloth row."""
    base = MATERIAL_ROLES[material]
    table = {"t": base[0], "T": base[1], "u": base[2] if len(base) > 2 else base[0]}

    def recolor(art, hem_row):
        x, y, pixels = art
        out = pixels.copy()
        for role, target in table.items():
            out[pixels == role] = target
        if border:
            trim = MATERIAL_ROLES.get(border, border)
            row = out[hem_row]
            row[np.isin(row, list(base))] = trim[0]
        return (x, y, out)

    return Layer(art=(("down", recolor(KNEE_DOWN, 4)), ("up", recolor(KNEE_DOWN, 4)),
                      ("left", recolor(KNEE_LEFT, 4))),
                 z=z, anchor=anchor, mask=NOT_HANDS)


TOPS = {
    "tee": Top("short"),
    "tank": Top("none", layers=(
        L(Z_TOP, mask="tTu", down=patch(5, 16, """
            s....s
            .s..s.
        """), up=patch(5, 16, """
            s....s
        """)),
    )),
    "bare": Top("none", layers=(
        L(Z_TOP, mask="tTu", down=patch(5, 17, """
            uu..uu
            uuTTuu
            .TTTT.
            ..uu..
            .uTTu.
            ..TT..
        """), up=patch(5, 17, """
            uT..Tu
            .uTTu.
            ..TT..
            ..TT..
        """), left=patch(4, 17, """
            uu
            uT
            T.
        """)),
    )),
    "shirt": Top("long", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            uukkuu
            .TkkT.
            ..TT..
            ...T..
            ...T..
            ...T..
        """), up=patch(5, 16, """
            uuuuuu
            TTTTTT
        """), left=patch(4, 16, """
            .u....u
            uT.....
            T......
        """)),
    )),
    "jersey": Top("short", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            aakkaa
            .akka.
            ..aa..
        """), up=patch(5, 16, """
            aaaaaa
            .wwww.
            ....w.
            ...w..
            ...w..
        """), left=patch(4, 16, """
            .a....a
            a......
        """)),
    )),
    "hoodie": Top("long", layers=(
        L(Z_TOP, mask="tTuk", down=patch(4, 16, """
            uuukkuuT
            .Tw..wT.
            ..w..w..
            ........
            ........
            .TTTTTT.
            .T....T.
        """), up=patch(4, 16, """
            .uuuuuuT
            .TuuuuTT
            ..TTTT..
        """), left=patch(4, 16, """
            .uu...uT
            .......T
            .......T
            .....TTT
        """)),
    )),
    "kurta": Top("long", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            ..kk..
            ..aA..
            ..aA..
            ..aA..
        """), up=patch(5, 16, """
            uuuuuu
        """), left=patch(4, 16, """
            .aa
            a..
            a..
        """)),
        knee("top", z=Z_TOP + 1),
    )),
    "lab coat": Top("long", sleeve="outer", layers=(
        L(Z_OUTER, mask="tTuk", down=patch(5, 16, """
            rq..qr
            qQttQq
            qQttQq
            qqttqQ
            qqttqQ
            qqttqQ
            qqttqQ
        """), up=patch(4, 16, """
            rqqqqqqQ
            .qqqqqQ.
            .qqqqqQ.
            .qqqqqQ.
            .qqqQqQ.
            .qqqQqQ.
            .qqqQqQ.
        """), left=patch(4, 16, """
            .rqqqqqq
            tqqqqqqQ
            tqqqqqqQ
            tqqqqqqQ
            tqqqqqqQ
            tqqqqqqQ
            tqqqqqqQ
        """)),
        L(Z_OUTER, anchor="waist", mask=NOT_HANDS, down=patch(3, 23, """
            ..qq..qQ..
            .Oqq..qQO.
            OqqqO.OqQO
            OqqqO.OqQO
            OqqqO.OqQO
            OOOO..OOOO
        """), up=patch(3, 23, """
            ..qqqqQ...
            .OqqqqqQO.
            OqqqqQqqQO
            OqqqqQqqQO
            OqqqqOqqQO
            OOOOOOOOOO
        """), left=patch(2, 23, """
            .Oqqq..OqQO.
            .Oqqq...qQO.
            .OqqqqqqqQO.
            OqqqqqqqqQO.
            OqqqqqqqqQQO
            OOOOOOOOOOOO
        """)),
    )),
    "suit": Top("long", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            uwkkwu
            twaawT
            tTaATT
            ttaATT
            tTaTtT
            tttTtT
            tttTtT
        """), up=patch(5, 16, """
            wwwwww
            ......
            ...T..
        """), left=patch(4, 16, """
            .w....w
            wa.....
            Ta.....
            T......
        """)),
    )),
    "jacket": Top("long", layers=(
        L(Z_OUTER, mask="tTuk", down=patch(4, 16, """
            rqqkkqqQ
            .rqwwqQ.
            ..TwwT..
            ...ww...
            ...ww...
            ...ww...
            ..TwwT..
        """), up=patch(4, 16, """
            rqqqqqqQ
            .TTTTTT.
        """), left=patch(4, 16, """
            .rqqqqq
            rqQ....
            w......
            w......
            w......
            w......
            w......
        """)),
    )),
    "overshirt": Top("rolled", sleeve="outer", layers=(
        L(Z_OUTER, mask="tTuk", down=patch(5, 16, """
            rq..qQ
            qr..rQ
            qT..TQ
            q....Q
            q....Q
            q....Q
            q....Q
        """), up=patch(4, 16, """
            rrqqqqqQ
            .qqqqqQ.
            .qqqqqQ.
            .qqqqqQ.
            .qqqqqQ.
            .qqqqqQ.
            .qqqqqQ.
        """), left=patch(4, 16, """
            .rr....
            trqqqqq
            tqqqqqQ
            tqqqqqQ
            tqqqqqQ
            tqqqqqQ
            tqqqqqQ
        """)),
    )),
    "tracksuit": Top("long", layers=(
        L(Z_TOP, mask="tTuk", down=patch(4, 16, """
            wwwkkwwW
            .wwwwwW.
            .uttTttT
            ...T....
            ...T....
            ...T....
            ...T....
        """), up=patch(4, 16, """
            wwwwwwwW
            .wwwwwW.
            .uttttT.
        """), left=patch(4, 16, """
            .wwwwww
            Twwwwww
            T......
            T......
        """)),
        L(Z_TOP, mask="zZ12xX", down=patch(3, 17, """
            w........w
            w........w
            w........w
            w........w
            w........w
            w........w
        """), up=patch(3, 17, """
            w........w
            w........w
            w........w
            w........w
            w........w
            w........w
        """)),
    )),
    "hi-vis": Top("short", sleeve="outer", layers=(
        L(Z_OUTER, mask="tTu", down=patch(5, 16, """
            .n..n.
            .n..n.
            .n..n.
            nnnnnn
            ......
            nnnnnn
        """), up=patch(5, 16, """
            .n..n.
            ..nn..
            ..nn..
            nnnnnn
            ......
            nnnnnn
        """), left=patch(4, 16, """
            .nnn....
            ........
            ........
            nnnnnnnn
            ........
            nnnnnnnn
        """)),
    )),
    "school": Top("short", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            uukkuu
            .TaaT.
            ..aa..
            ..aA..
            ..aA..
            ...A..
        """), up=patch(5, 16, """
            uuuuuu
            TTTTTT
        """), left=patch(4, 16, """
            .u....u
            ua.....
            Ta.....
            .a.....
        """)),
    )),
    "pinafore": Top("short", layers=(
        L(Z_OUTER, mask="tTu", down=patch(5, 16, """
            .b..b.
            .b..b.
            .b..b.
            bbbbbB
            bbbbbB
            bvbbbB
            bbbbbB
        """), up=patch(5, 16, """
            .b..b.
            ..bb..
            ..bb..
            bbbbbB
            bbbbbB
            bbbbbB
            bbbbbB
        """), left=patch(4, 16, """
            ..b....
            ..b....
            bbb....
            bbbbbbb
            bbbbbbB
            bbbbbbB
            bbbbbbB
        """)),
    )),
    "printed": Top("short", layers=(
        L(Z_TOP, mask="tTuk", down=patch(5, 16, """
            uukkuu
            a.kk.5
            ..a..a
            5..5..
            .a..a.
            ..5..5
            a..a..
        """), up=patch(5, 16, """
            uuuuuu
            a..5..
            ..a..a
            5..5..
            .a..a.
            ..5..5
            a..a..
        """), left=patch(4, 16, """
            .u....u
            a..5..a
            ..a...5
            5....a.
            .a.5...
            ...a..5
            a5.....
        """)),
        L(Z_TOP, mask="zZ", down=patch(3, 17, """
            a........5
            .5......a.
        """), up=patch(3, 17, """
            a........5
            .5......a.
        """), left=patch(6, 17, """
            .a.
            5..
        """)),
    )),
    "dance": Top("short", layers=(
        L(Z_TOP, mask="tTuk", down=patch(4, 16, """
            yy.kk.yy
            .yykkyy.
            ..yyyy..
            ...yy...
            ........
            ..aaaa..
            .yyyyyy.
        """), up=patch(5, 16, """
            yyyyyy
            ......
            ......
            ......
            ......
            ......
            yyyyyy
        """), left=patch(4, 16, """
            .y...yy
            yy.....
            y......
            .......
            .......
            .......
            yyyyyyy
        """)),
    )),
    "saree": Top("short", sleeve="outer", layers=(
        L(Z_TOP, mask="tTu", down=patch(5, 16, """
            ...aau
            ..aauu
            .aauuT
            aauutT
            auuttT
            uuuttT
            uutttT
        """), up=patch(4, 16, """
            uaa.....
            uuaa....
            Tuuaa...
            .Tuuaa..
            .TTuuaa.
            ..TTuuaa
            ..TTTuua
        """), left=patch(4, 16, """
            .aaaau.
            aauuuu.
            auu....
            uu.....
            u......
            u......
            u......
        """)),
    )),
}

BOTTOMS = {
    "pants": Bottom("long"),
    "shorts": Bottom("shorts"),
    "cargo": Bottom("long", layers=(
        L(Z_LEGWEAR, anchor="waist", mask="bB", down=patch(5, 26, """
            B....B
            B....B
        """), up=patch(5, 26, """
            B....B
            B....B
        """), left=patch(6, 25, """
            BB
            BB
        """)),
    )),
    "track": Bottom("long", layers=(
        L(Z_LEGWEAR, anchor="waist", mask="bBJK34", down=patch(5, 24, """
            w....w
            w....w
            w....w
            w....w
            w....w
            w....w
        """), up=patch(5, 24, """
            w....w
            w....w
            w....w
            w....w
            w....w
            w....w
        """)),
    )),
    "skirt": Bottom("shorts", layers=(knee("bottom"),)),
    "pinafore": Bottom("shorts", layers=(knee("bottom"),)),
    "long skirt": Bottom("long", layers=(wrap("bottom", border="bottom"),)),
    "veshti": Bottom("long", layers=(wrap("bottom", border="accent"),)),
    "veshti-folded": Bottom("shorts", layers=(knee("bottom", border="bottom"),)),
    "lungi": Bottom("shorts", layers=(
        knee("bottom"),
        L(Z_LEGWEAR + 1, mask="bBv", anchor="waist", down=patch(4, 23, """
            ..a..a..
            aaaaaaaa
            ..a..a..
            ..a..a..
        """), up=patch(4, 23, """
            ..a..a..
            aaaaaaaa
            ..a..a..
            ..a..a..
        """), left=patch(3, 23, """
            ..a..a..
            aaaaaaaa
            ..a..a..
            ..a..a..
        """)),
    )),
    "saree": Bottom("long", layers=(wrap("top", border="accent"),)),
    "dance": Bottom("long", layers=(
        L(Z_LEGWEAR, anchor="waist", mask=NOT_HANDS, down=patch(5, 23, """
            yyyyyy
            .OaaO.
            .OacO.
            OaacaO
            OacaaO
            OOOOOO
        """), up=patch(5, 23, """
            yyyyyy
        """), left=patch(2, 24, """
            ..OaaO.
            .OacaO.
            OaacaO.
            OOOOOO.
        """)),
    )),
}


# ---------------------------------------------------------------------------
# Headwear and faces
# ---------------------------------------------------------------------------

def hat(**art):
    return (Layer(art=tuple(art.items()), z=Z_HAT, anchor="head"),)


HATS = {
    "none": (),
    # Baseball / cricket cap, peak forward.
    "cap": hat(down=patch(0, 1, """
        .....OOOOOO.....
        ...OOpiipppOO...
        ..OpiiippppppO..
        .OpiipppppppPPO.
        .OpipppppppppPO.
        .OpppppppppPPPO.
        OPPPPPPPPPPPPPPO
        OiiiiiiiiiiiiiPO
        .OPPPPPPPPPPPPO.
    """), up=patch(0, 1, """
        .....OOOOOO.....
        ...OOppiipPOO...
        ..OpiiippppPPO..
        .OpiipppppppPPO.
        .OppppppppppPPO.
        .OppppppppppPPO.
        OPPPPPOOOPPPPPPO
        OPPPPOhhhOPPPPPO
    """), left=patch(0, 1, """
        .....OOOOOO.....
        ...OOpiippPOO...
        ..OpiiippppPPO..
        .OpiipppppppPPO.
        .OppppppppppPPO.
        .OppppppppppPPO.
        OOPPPPPPPPPPPPPO
        iiiiPO..........
        PPPPO...........
    """)),
    "hard hat": hat(down=patch(0, 1, """
        .....OOOOOO.....
        ...OOiipPppOO...
        ..OiiipPpppppO..
        .OiippPPpppppPO.
        .OippppPpppppPO.
        .OppppPPppppPPO.
        OiiiiiiiiiiiiiPO
        OPPPPPPPPPPPPPPO
    """), up=patch(0, 1, """
        .....OOOOOO.....
        ...OOiipPppOO...
        ..OiiipPpppppO..
        .OiippPPpppppPO.
        .OippppPpppppPO.
        .OppppPPppppPPO.
        OiiiiiiiiiiiiiPO
        OPPPPPPPPPPPPPPO
    """), left=patch(0, 1, """
        .....OOOOOO.....
        ...OOiiipppOO...
        ..OiiipPPpppPO..
        .OiippppPPppPPO.
        .OippppppPPpPPO.
        .OppppppppPPPPO.
        OiiiiiiiiiiiiiPO
        OPPPPPPPPPPPPPPO
    """)),
    # Open-face motorbike helmet with a raised dark visor.
    "helmet": hat(down=patch(0, 1, """
        .....OOOOOO.....
        ...OOiipppPOO...
        ..OiippppppPPO..
        .OiipppppppppPO.
        OiippppppppppPPO
        OippppppppppPPPO
        OppppppppppppPPO
        OennnneeeeeeeeeO
        OpP..........PpO
        OpP..........PpO
        OPPO........OPPO
        .OO..........OO.
    """), up=patch(0, 1, """
        .....OOOOOO.....
        ...OOiipppPOO...
        ..OiippppppPPO..
        .OiipppppppppPO.
        OiippppppppppPPO
        OippppppppppPPPO
        OppppppppppppPPO
        OpppppppppppPPPO
        OpppppppppppPPPO
        OPpppppppppPPPPO
        OPPPPPPPPPPPPPPO
        .OOOOOOOOOOOOOO.
    """), left=patch(0, 1, """
        .....OOOOOO.....
        ...OOiipppPOO...
        ..OiippppppPPO..
        .OiipppppppppPO.
        OiippppppppppPPO
        OippppppppppPPPO
        OppppppppppppPPO
        OennneppppppPPPO
        .O....OpppppPPPO
        ......OpPppPPPPO
        ......OPPPPPPPO.
        .......OOOOOOO..
    """)),
    # Peaked uniform cap.
    # Peaked uniform cap; the visor shades the brow and hides the fringe.
    "police cap": hat(down=patch(0, 1, """
        ..OOOOOOOOOOOO..
        .OiiiiiiiiiiiPO.
        .OpppppppppppPO.
        ..OPPPPyyPPPPO..
        ..OPPPPPPPPPPO..
        ..OPPPPPPPPPPO..
        .OeeeeeeeeeeeeO.
        ..OennnnnnnneO..
        ..HkkkkkkkkkkH..
    """), up=patch(0, 1, """
        ..OOOOOOOOOOOO..
        .OiiiiiiiiiiiPO.
        .OpppppppppppPO.
        ..OPPPPPPPPPPO..
        ..OPPPPPPPPPPO..
        ..OPPPPPPPPPPO..
        ..OOOOOOOOOOOO..
    """), left=patch(0, 1, """
        ...OOOOOOOOOOO..
        ..OiiiiiiiiiiPO.
        ..OppppppppppPO.
        ...OyPPPPPPPPO..
        ...OPPPPPPPPPO..
        ...OPPPPPPPPPO..
        OeeneeOOOOOOOO..
        .OOOOOkk........
    """)),
    # Wide-brimmed bush / ranger hat.
    "wide brim": hat(down=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OiipppppPO...
        ...OipppppPPO...
        ..OaaaaaaaaaAO..
        OOiiiiiiiiiiiiOO
        OiiiiiiiiiiiiiPO
        .OPPPPPPPPPPPPO.
    """), up=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OiipppppPO...
        ...OipppppPPO...
        ..OaaaaaaaaaAO..
        OOiiiiiiiiiiiiOO
        OPPPPPPPPPPPPPPO
        .OOOOOOOOOOOOOO.
    """), left=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OiipppppPO...
        ...OipppppPPO...
        ..OaaaaaaaaaAO..
        OOiiiiiiiiiiiiOO
        OPPPPPPPPPPPPPPO
        .OOO.......OOOO.
    """)),
    "straw hat": hat(down=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OipiPipiPO...
        ...OPiPiPiPPO...
        ..OaaaaaaaaaAO..
        OOiPiPiPiPiPiPOO
        OiPiPiPiPiPiPiPO
        .OPPPPPPPPPPPPO.
    """), up=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OipiPipiPO...
        ...OPiPiPiPPO...
        ..OaaaaaaaaaAO..
        OOiPiPiPiPiPiPOO
        OPPPPPPPPPPPPPPO
        .OOOOOOOOOOOOOO.
    """), left=patch(0, 1, """
        ................
        ....OOOOOOOO....
        ...OipiPipiPO...
        ...OPiPiPiPPO...
        ..OaaaaaaaaaAO..
        OOiPiPiPiPiPiPOO
        OPPPPPPPPPPPPPPO
        .OOO.......OOOO.
    """)),
    # A cloth wound round the head (gardener's towel).
    "head towel": hat(down=patch(0, 1, """
        ................
        ....OOOOOOO.....
        ..OOiiiPiiiOO...
        .OiiiiPiiiiiPO..
        .OiiiPPiiiiPPO..
        OiPPPiiiPPPPiPO.
        OiiiiiPPiiiiiPPO
        OPPPPPPPPPPPPPPO
        .OO..........OO.
    """), up=patch(0, 1, """
        ................
        ....OOOOOOO.....
        ..OOiiiPiiiOO...
        .OiiiiPiiiiiPO..
        .OiiiPPiiiiPPO..
        OiPPPiiiPPPPiPO.
        OiiiiiPPiiiiiPPO
        OPPPPPiiPPPPPPPO
        ......OiiO......
        ......OPPO......
        .......OO.......
    """), left=patch(0, 1, """
        ................
        ....OOOOOOO.....
        ..OOiiiPiiiOO...
        .OiiiiPiiiiiPO..
        .OiiiPPiiiiPPO..
        OiPPPiiiPPPPiPOO
        OiiiiiPPiiiiiPiO
        OPPPPPPPPPPPPPPO
        ............OO..
    """)),
    # Area-boi bandana: a band across the brow, knot behind.
    "bandana": hat(down=patch(0, 4, """
        .OOOOOOOOOOOOOO.
        OpipppippppippPO
        OPPPPPPPPPPPPPPO
        .OO..........OO.
    """), up=patch(0, 4, """
        .OOOOOOOOOOOOOO.
        OpipppippppippPO
        OPPPPPPiiPPPPPPO
        ......OpPO......
        ......OpPO......
        .......OO.......
    """), left=patch(0, 4, """
        .OOOOOOOOOOOOOO.
        OpipppippppippPO
        OPPPPPPPPPPPPPiO
        ............OpPO
        .............OPO
        ..............O.
    """)),
    "headband": hat(down=patch(1, 6, """
        OiiiiiiiiiiiiO
        OPPPPPPPPPPPPO
    """), up=patch(1, 6, """
        OiiiiiiiiiiiiO
        OPPPPPPPPPPPPO
    """), left=patch(1, 6, """
        OiiiiiiiiiiiiO
        OPPPPPPPPPPPPO
    """)),
}

# Jasmine strands are worn with buns: white buds round the knot.
JASMINE = (Layer(art=(
    ("down", patch(11, 7, """
        .wWw.
    """)),
    ("up", patch(4, 13, """
        w......w
        .wWwwWw.
    """)),
    ("left", patch(10, 10, """
        w.....
        .wWw..
    """)),
), z=Z_HAT, anchor="head", mask=".hHjO"),)


def face(z=Z_FACE, mask="skl", **art):
    return (Layer(art=tuple(art.items()), z=z, anchor="head", mask=mask),)


FACE = {
    "brows": face(z=Z_HAIR + 5, down=patch(4, 9, """
        HH....HH
    """), left=patch(2, 9, """
        HH
    """)),
    "lashes": face(z=Z_HAIR + 5, down=patch(4, 9, """
        e......e
    """), left=patch(3, 9, """
        e
    """)),
    "moustache": face(z=Z_HAIR + 5, down=patch(5, 13, """
        HhhhhH
    """), left=patch(1, 13, """
        Hh
    """)),
    "big moustache": face(z=Z_HAIR + 5, down=patch(4, 12, """
        .Hh..hH.
        HhhhhhhH
        H......H
    """), left=patch(1, 12, """
        .hH
        HhH
        H..
    """)),
    "beard": face(z=Z_HAIR + 5, down=patch(2, 12, """
        H..........H
        hH.hhhhhh.Hh
        .hHhhmmhhHh.
        ..OhhhhhhO..
    """), left=patch(1, 12, """
        ....HH
        Hhhhhh
        .hhhh.
        ..OO..
    """), mask="sklmO"),
    "smirk": face(z=Z_HAIR + 5, mask="sklm", down=patch(7, 12, """
        ..m
        mm.
    """), left=patch(2, 12, """
        m
    """)),
    "stubble": face(z=Z_HAIR + 5, down=patch(3, 13, """
        .k.k..k.k.
        ..k.kk.k..
    """), left=patch(2, 13, """
        .k.k
        k.k.
    """)),
    "bindi": face(z=Z_HAIR + 5, down=patch(7, 9, """
        R
    """)),
    "sindoor": face(z=Z_HAIR + 6, mask="hHjk", down=patch(7, 2, """
        R
        R
        R
    """)),
    "earrings": face(z=Z_HAIR + 6, mask=".skl", down=patch(1, 13, """
        y............y
    """), left=patch(8, 12, """
        y
    """)),
    "wrinkles": face(down=patch(3, 12, """
        k........k
    """), left=patch(5, 12, """
        k
    """)),
    "glasses": face(z=Z_GLASSES, mask="sklhHjkemw", down=patch(4, 10, """
        eneeeene
        e.e..e.e
    """), left=patch(1, 10, """
        eneeeee
        e.e....
    """)),
    "shades": face(z=Z_GLASSES, mask="sklhHjkemw", down=patch(3, 10, """
        eneeeeenee
        eeee..eeee
    """), left=patch(1, 10, """
        eneeeee
        eee....
    """)),
}


# ---------------------------------------------------------------------------
# Accessories and carried items
# ---------------------------------------------------------------------------

def hand_point(build, direction, pose, side):
    """Bottom-centre pixel of a hand in a body pose ('L', 'R' or 'near')."""
    x0, y0, body = BODIES[build][direction][POSES.index(pose)]
    top = BUILDS[build]["torso"] + 17 + int(pose != "stand") - y0
    hands = np.isin(body, list(HANDS))
    hands[:max(0, top)] = False
    ys, xs = np.nonzero(hands)
    xs, ys = xs + x0, ys + y0
    pick = {"L": xs < 8, "R": xs >= 8}.get(side, np.ones(len(xs), bool))
    return int(np.floor(xs[pick].mean())), int(ys[pick].max())


def held(z=Z_HELD, mask=None, **art):
    """Items carried in a hand: {direction: (side, dx, dy, grid text)}.

    The grid's top-left lands at the hand point plus (dx, dy), so the item
    follows the arm swing; pixels that fall outside the frame are dropped.
    """
    frames = tuple((d, ("hand", side, dx, dy, grid(text)))
                   for d, (side, dx, dy, text) in art.items())
    return (Layer(art=frames, z=z, anchor="hand", mask=mask),)


def worn(z=Z_STRAP, mask=None, anchor="torso", under=False, **art):
    return (Layer(art=tuple(art.items()), z=z, anchor=anchor, mask=mask,
                  under=under),)


EXTRAS = {
    "backpack": worn(mask="tTuk", down=patch(4, 16, """
        .q....q.
        .q....q.
        .Q....Q.
        .q....q.
        ..q..q..
    """), left=patch(7, 16, """
        qq
        .q
    """)) + worn(z=Z_STRAP, mask=NOT_HANDS + "sk", up=patch(4, 16, """
        .OOOOOO.
        OqqrqqQO
        OqqqqqQO
        OQQQQQQO
        OqrqqqQO
        OqqqqqQO
        OQQQQQQO
        .OOOOOO.
    """)) + worn(under=True, left=patch(12, 15, """
        .OO.
        OOqO
        OqqO
        OqrO
        OqqO
        OQqO
        OqqO
        OQQO
        .OO.
    """)),
    "crossbody": worn(mask="tTuk", down=patch(5, 16, """
        a.....
        .a....
        ..a...
        ...a..
        ....a.
        .....a
    """), up=patch(5, 16, """
        .....a
        ....a.
        ...a..
        ..a...
        .a....
        a.....
    """), left=patch(5, 16, """
        aa.
        ..a
        ..a
    """)) + worn(z=Z_STRAP + 1, mask=None, down=patch(9, 21, """
        .OOOO
        OAaaO
        OaaaO
        OAAAO
        .OOO.
    """), up=patch(2, 21, """
        OOOO.
        OaaAO
        OaaaO
        OAAAO
        .OOO.
    """), left=patch(9, 21, """
        OOOO
        OaaO
        OaAO
        OOOO
    """)),
    "lanyard": worn(mask="tTuk", down=patch(6, 16, """
        a..a
        a..a
        .aa.
        .aa.
        .ww.
        .wW.
    """), up=patch(6, 16, """
        aaaa
    """), left=patch(4, 16, """
        .aa
        a..
        w..
        w..
        W..
    """)),
    "chain": worn(mask="tTuk", down=patch(5, 16, """
        y....y
        .y..y.
        ..yy..
    """), up=patch(5, 16, """
        yyyyyy
    """), left=patch(4, 16, """
        .yyy
        y...
        y...
    """)),
    "thick chain": worn(mask="tTuk", down=patch(5, 16, """
        yy..yy
        .yyyy.
        ..YY..
        ..yy..
    """), up=patch(5, 16, """
        yyyyyy
    """), left=patch(4, 16, """
        .yyy
        yy..
        yY..
    """)),
    "bracelet": worn(mask="xX", down=patch(3, 21, """
        yY........
    """), up=patch(3, 21, """
        ........yY
    """), left=patch(0, 21, """
        yyyyyyyyyyyyyyyy
    """)),
    "watch": worn(mask="xX", down=patch(3, 21, """
        ........eN
    """), up=patch(3, 21, """
        eN........
    """), left=patch(0, 21, """
        eeeeeeeeeeeeeeee
    """)),
    "whistle": worn(mask="tTuk", down=patch(6, 16, """
        e..e
        .e.e
        ..e.
        ..nn
        ..NN
    """), up=patch(6, 16, """
        eeee
    """), left=patch(4, 16, """
        .ee
        e..
        nn.
    """)),
    "towel": worn(mask=None, down=patch(9, 15, """
        .OOOO.
        OrqqqO
        OqQqQO
        .OqQqO
        .OqQqO
        .OqqQO
        .OrqqO
        ..OOO.
    """), up=patch(1, 15, """
        .OOOO.
        OqqqrO
        OQqQqO
        OqQqO.
        OqQqO.
        OQqqO.
        OqqrO.
        .OOO..
    """), left=patch(3, 15, """
        .OOOOOOOO.
        OrqqqqqqqO
        OqQ.....qO
        OqQ.....qO
        OqQ.......
        .OO.......
    """)),
    "shawl": worn(z=Z_OUTER + 1, mask=NOT_HANDS, down=patch(2, 15, """
        .OOOO..OOOO.
        OqrqqO.OqQqO
        OqqQqO.OqQqO
        .OqQqO.OqQO.
        .OqQO..OqQO.
        .OqQO..OqQO.
        .OqQO..OqQO.
        .OqQO..OqQO.
        .OqqO..OqqO.
        .OOOO..OOOO.
    """), up=patch(2, 15, """
        .OOOOOOOOOO.
        OqqqqqqqqqQO
        OqqqqqqqqQQO
        OqqqqqqqqQQO
        OqqqqqqqqQQO
        OqqqqqqqQQQO
        .OqqqqqqQQO.
        ..OOOOOOOO..
    """), left=patch(3, 15, """
        .OOOOOOOO.
        OqqqqqqqqO
        OqQ....OqO
        OqQ....OqO
        OqQ....OQO
        OqQ.....O.
        OqqO......
        .OO.......
    """)),
    "binoculars": worn(mask=None, down=patch(5, 16, """
        e....e
        .e..e.
        .OOOO.
        OnOOnO
        OeeeeO
        .OOOO.
    """), left=patch(3, 18, """
        OOO
        nOe
        OOO
    """)),
    "apron": worn(z=Z_OUTER, mask=NOT_HANDS, down=patch(4, 16, """
        ..w..w..
        ..wwww..
        ..wwwW..
        ..wwwW..
        ..wwwW..
        .awwwwa.
        .wwwwwW.
        .wwwwwW.
        OwwwwwWO
        OwwwwwWO
        OwwwwwWO
        OOOOOOOO
    """), up=patch(4, 16, """
        ..w..w..
        ...ww...
        ........
        ........
        ........
        ...aa...
        ..a..a..
    """), left=patch(2, 16, """
        ..w...
        ..ww..
        ..wW..
        ..wW..
        ..wW..
        ..aaaa
        .wwW..
        .wwW..
        OwwwO.
        OwwwO.
        OwwWO.
        OOOOO.
    """)),
    "belt": worn(mask="bBv", anchor="waist", down=patch(5, 23, """
        eeyyee
    """), up=patch(5, 23, """
        eeeeee
    """), left=patch(3, 23, """
        yeeeeeeee
    """)),
    "wallet chain": worn(mask="bBv", anchor="waist", down=patch(8, 23, """
        n..
        .n.
        ..n
    """), up=patch(8, 23, """
        n..
        .nn
    """), left=patch(5, 23, """
        n...n
        .n.n.
        ..n..
    """)),
    "badge": worn(mask="tTu", down=patch(9, 18, """
        y
    """), left=patch(5, 18, """
        y
    """)),
    "pockets": worn(mask="tTu", down=patch(5, 18, """
        TT..TT
        uT..uT
    """), left=patch(4, 18, """
        TT
    """)),
    "star": worn(mask="tTu", down=patch(6, 18, """
        .R.
        RRR
        R.R
    """)),
    "delivery box": worn(under=True, down=patch(0, 11, """
        OOOOOOOOOOOOOOOO
        OaaaaaaaaaaaaaAO
        OaaaaaaaaaaaaaAO
        OccccccccccccccO
        OaaaaaaaaaaaaaAO
        OaAO........OaAO
        OaAO........OaAO
        OaAO........OaAO
        OaAO........OaAO
        OAAO........OAAO
        OOOO........OOOO
    """), left=patch(8, 10, """
        OOOOOOOO
        OaaaaaaO
        OaaaaaAO
        OccccccO
        OaaaaaAO
        OaaaaaAO
        OaaaaaAO
        OaaaaaAO
        OaaaaaAO
        OaaaaaAO
        OAAAAAAO
        OAAAAAAO
        OOOOOOOO
    """)) + worn(z=Z_HAIR + 10, up=patch(1, 11, """
        OOOOOOOOOOOOOO
        OaaaaaaaaaaaAO
        OaaaaaaaaaaaAO
        OccccccccccccO
        OaaawwwwwwaaAO
        OaaaaaaaaaaaAO
        OaaaaaaaaaaaAO
        OaaaaaaaaaaaAO
        OaaaaaaaaaaaAO
        OAAAAAAAAAAAAO
        OOOOOOOOOOOOOO
    """)),
    # --- held in a hand -----------------------------------------------------
    "clipboard": held(down=("R", -1, -5, """
        .OnO.
        OdwwO
        OdwWO
        OdwwO
        OdWwO
        .OOO.
    """), left=("near", -1, -5, """
        OnO
        OwO
        OwO
        OwO
        OWO
        OOO
    """)),
    "folder": held(down=("L", -1, -5, """
        OOOO.
        OaawO
        OaawO
        OaawO
        OAAwO
        OOOO.
    """), left=("near", -1, -5, """
        OOO
        OaO
        OaO
        OaO
        OAO
        OOO
    """)),
    "book": held(down=("L", -1, -5, """
        OOOO.
        O556O
        O556O
        O556O
        O666O
        OOOO.
    """), left=("near", -1, -5, """
        OOO
        O5O
        O5O
        O5O
        O6O
        OOO
    """)),
    "phone": held(down=("R", -1, -3, """
        OOO
        OnO
        OeO
        OOO
    """), left=("near", -1, -3, """
        OO
        nO
        eO
        OO
    """)),
    "cup": held(down=("R", -1, -3, """
        OOO
        OwO
        OWO
        OOO
    """), left=("near", -1, -3, """
        OOO
        OwO
        OWO
        OOO
    """)),
    "watering can": held(down=("R", -3, -1, """
        OO..OO.
        OyO.OyO
        .OyOyyO
        ..OyyYO
        ..OYYYO
        ...OOO.
    """), left=("near", -6, -1, """
        OO..OO.
        OyO.OyO
        .OyOyyO
        ..OyyYO
        ..OYYYO
        ...OOO.
    """)),
    "coffee": held(down=("R", -2, -3, """
        .OOO.
        .OnO.
        OnnNO
        .OOO.
    """), left=("near", -2, -3, """
        .OOO.
        .OnO.
        OnnNO
        .OOO.
    """)),
    "handbag": held(down=("L", -1, 0, """
        .OO.
        OaaO
        OaAO
        OAAO
        .OO.
    """), left=("near", -1, 0, """
        .OO.
        OaaO
        OaAO
        OAAO
        .OO.
    """)),
    "shears": held(down=("R", 0, 0, """
        On
        On
        On
        .O
    """), left=("near", -1, 0, """
        On
        On
        On
        .O
    """)),
    "fishing rod": held(z=Z_HELD, down=("R", 1, -21, """
        .w.
        .d.
        .d.
        .D.
        .d.
        .d.
        .D.
        .d.
        .d.
        .D.
        .d.
        .d.
        .D.
        .d.
        .d.
        .D.
        .d.
        .d.
        .D.
        .d.
        OdO
        OOO
    """), left=("near", 1, -19, """
        w..
        Od.
        .dO
        .dO
        .DO
        .dO
        .dO
        .DO
        .dO
        .dO
        .DO
        .dO
        .dO
        .DO
        .dO
        .dO
        .DO
        .dO
        OdO
        OOO
    """)),
    "staff": held(z=Z_STRAP + 1, down=("L", 0, -18, """
        .OO.
        OddO
        ODdO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .OOO
    """), up=("R", -1, -18, """
        .OO.
        OddO
        ODdO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .OOO
    """), left=("near", -1, -18, """
        .OO.
        OddO
        ODdO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OdO
        .OOO
    """)),
    "cane": held(down=("L", -1, -1, """
        OOO.
        OddO
        OdOO
        OdO.
        ODO.
        OdO.
        OdO.
        ODO.
        OdO.
        OOO.
    """), up=("R", 0, -1, """
        .OOO
        OddO
        OOdO
        .OdO
        .ODO
        .OdO
        .OdO
        .ODO
        .OdO
        .OOO
    """), left=("near", -2, -1, """
        .OOO
        OddO
        OdOO
        OdO.
        ODO.
        OdO.
        OdO.
        ODO.
        OdO.
        OOO.
    """)),
    "tray": held(down=("R", -3, -3, """
        .OaG5aO.
        OnnnnnnO
        .ONNNNO.
    """), left=("near", -5, -3, """
        .OaG5aO.
        OnnnnnnO
        .ONNNNO.
    """)),
    # A cricket bat carried blade-down beside the leg.
    "bat": held(down=("R", 0, 0, """
        .OO.
        .OeO
        OddO
        OdDO
        OdDO
        OdDO
        OdDO
        .OO.
    """), up=("L", -2, 0, """
        .OO.
        OeO.
        OddO
        ODdO
        ODdO
        ODdO
        ODdO
        .OO.
    """), left=("near", -1, 0, """
        .OO.
        .OeO
        OddO
        OdDO
        OdDO
        OdDO
        OdDO
        .OO.
    """)),
    "neck towel": worn(mask="tTuk", down=patch(4, 16, """
        qqrqqrqq
        .q....q.
        .Q....Q.
        .q....q.
    """), up=patch(4, 16, """
        qqrqqrqq
    """), left=patch(4, 16, """
        .qqrqqq
        q......
        Q......
    """)),
    "logo": worn(mask="tTu", down=patch(6, 18, """
        ..ww
        .ww.
        ww..
    """), left=patch(4, 18, """
        w
        w
    """)),
    "top flowers": (Layer(art=(
        ("down", patch(4, 3, """
            .w5..5w.
        """)),
        ("up", patch(4, 3, """
            .w5..5w.
        """)),
        ("left", patch(5, 3, """
            .w5..5w.
        """)),
    ), z=Z_HAT, anchor="head", mask=".hHjO"),),

}
EXTRAS["jasmine"] = JASMINE
# Jasmine strung with orange kanakambara (the extra colour).
EXTRAS["flowers"] = tuple(
    Layer(art=tuple((d, (x, y, np.where(np.isin(px, ["W"]), "5", px)))
                    for d, (x, y, px) in layer.art),
          z=layer.z, anchor=layer.anchor, mask=layer.mask)
    for layer in JASMINE)


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Character:
    skin: str = "honey"
    build: str = "regular"
    hair: str = "short"
    hair_color: str = "black"
    face: tuple = ()
    headwear: str = "none"
    hat_color: str = "#3974ac"
    top: str = "tee"
    top_color: str = "#398d86"
    sleeves: str | None = None          # overrides the top style's sleeves
    sleeve: str | None = None           # overrides the sleeve material
    outer_color: str = "#f1ece0"
    bottom: str = "pants"
    bottom_color: str = "#46566e"
    shoes: str = "#745449"
    feet: str = "shoes"                 # shoes | sandals | barefoot
    socks: bool = False
    accent: str = "#e5b956"
    extra_color: str = "#c94a4a"
    extras: tuple = ()
    custom: tuple = ()                  # bespoke Layer objects

    def __post_init__(self):
        checks = {"skin": SKIN_TONES, "build": BODIES, "hair": HAIR,
                  "headwear": HATS, "top": TOPS, "bottom": BOTTOMS}
        for key, allowed in checks.items():
            if getattr(self, key) not in allowed:
                raise ValueError(f"Unknown {key}: {getattr(self, key)!r}")
        unknown = set(self.face) - set(FACE)
        if unknown:
            raise ValueError(f"Unknown face features: {unknown}")
        unknown = set(self.extras) - set(EXTRAS)
        if unknown:
            raise ValueError(f"Unknown extras: {unknown}")
        if self.sleeves not in (None, "none", "short", "rolled", "elbow", "long"):
            raise ValueError(f"Unknown sleeves: {self.sleeves!r}")
        if self.feet not in ("shoes", "sandals", "barefoot"):
            raise ValueError(f"Unknown feet: {self.feet!r}")
        for value in (HAIR_COLORS.get(self.hair_color, self.hair_color),
                      self.hat_color, self.top_color, self.outer_color,
                      self.bottom_color, self.shoes, self.accent, self.extra_color):
            ramp(value)

    def layers(self):
        found = list(HAIR[self.hair]) + list(HATS[self.headwear])
        found += TOPS[self.top].layers + BOTTOMS[self.bottom].layers
        for name in self.face:
            found += FACE[name]
        for name in self.extras:
            found += EXTRAS[name]
        found += self.custom
        return sorted(found, key=lambda layer: layer.z)


def palette(character):
    ink = (*rgb(OUTLINE), 255)
    p = {".": (0, 0, 0, 0), "O": ink, "e": ink}
    bottom = character.top_color if character.bottom == "saree" else character.bottom_color
    colors = {"hair": HAIR_COLORS.get(character.hair_color, character.hair_color),
              "top": character.top_color,
              "bottom": bottom, "shoes": character.shoes,
              "accent": character.accent, "outer": character.outer_color,
              "hat": character.hat_color, "extra": character.extra_color}
    for material, roles in MATERIAL_ROLES.items():
        if material == "skin":
            tones = tuple(rgb(c) for c in SKIN_TONES[character.skin])
        elif material in FIXED:
            tones = tuple(rgb(c) for c in FIXED[material])
        else:
            tones = ramp(colors[material])
        for role, tone in zip(roles, tones):
            p[role] = (*tone, 255)
    shadow = np.array(p["k"][:3])
    p["m"] = (*np.rint(shadow * .62 + np.array(rgb(OUTLINE)) * .38).astype(int), 255)
    if character.top == "bare":
        for top_role, skin_role in zip("tTu", "skl"):
            p[top_role] = p[skin_role]
    if character.feet == "sandals":
        p["f"], p["g"] = p["s"], p["l"]
    elif character.feet == "barefoot":
        p["f"], p["F"], p["g"] = p["s"], p["k"], p["l"]
    return p


def semantic_map(character):
    """Limb roles -> material roles for this outfit."""
    top = TOPS[character.top]
    sleeves = character.sleeves or top.sleeves
    cloth = MATERIAL_ROLES[character.sleeve or top.sleeve]
    if len(cloth) == 2:
        cloth = cloth + cloth[0]
    skin = "skl"
    cuff = cloth[2] + cloth[0]
    upper, elbow, fore = {
        "none": (skin, skin, skin),
        "short": (cloth, skin, skin),
        "rolled": (cloth, cuff, skin),
        "elbow": (cloth, cloth, skin),
        "long": (cloth, cloth, cloth),
    }[sleeves]
    legs = BOTTOMS[character.bottom].legs
    shin = "bB" if legs == "long" else "sk"
    ankle = "wW" if character.socks else shin
    return {"z": upper[0], "Z": upper[1], "1": elbow[0], "2": elbow[1],
            "x": fore[0], "X": fore[1], "J": shin[0], "K": shin[1],
            "3": ankle[0], "4": ankle[1]}


def arm_patch(build, direction, pose):
    """The arms and hands of a body pose, with the ink that bounds them.

    They are stamped again after garments, so a swinging arm or a hand at
    the hip stays in front of skirts, coat tails and wraps.
    """
    x, y, body = BODIES[build][direction][POSES.index(pose)]
    top = BUILDS[build]["torso"] + 17 + int(pose != "stand") - y
    core = np.isin(body, list(ARMS + HANDS))
    core[:max(0, top)] = False
    padded = np.pad(core, 1)
    near = (padded[:-2, 1:-1] | padded[2:, 1:-1]
            | padded[1:-1, :-2] | padded[1:-1, 2:])
    keep = core | (near & (body == "O"))
    return (x, y, np.where(keep, body, "."))


def render_roles(character, direction, pose):
    if direction not in DIRECTIONS or pose not in POSES:
        raise ValueError(f"Unknown direction/pose: {direction!r}/{pose!r}")
    if direction == "right":
        return render_roles(character, "left", pose)[:, ::-1].copy()
    build = character.build
    canvas = np.full((FRAME_H, FRAME_W), ".", dtype="<U1")
    stamp(canvas, BODIES[build][direction][POSES.index(pose)])
    head_dy = BUILDS[build]["head"] + int(pose != "stand")
    steps = [(Z_ARMS, lambda: stamp(canvas, arm_patch(build, direction, pose))),
             (Z_HEAD, lambda: stamp(canvas, HEADS[direction], head_dy))]
    for layer in character.layers():
        while steps and layer.z >= steps[0][0]:
            steps.pop(0)[1]()
        apply_layer(canvas, layer, build, direction, pose)
    for _, step in steps:
        step()
    for role, target in semantic_map(character).items():
        canvas[canvas == role] = target
    outline(canvas)
    return canvas


def render_frame(character, direction="down", pose="stand"):
    """Return a fresh 16 x 32 RGBA image; no filesystem side effects."""
    roles = render_roles(character, direction, pose)
    p = palette(character)
    rgba = np.zeros((FRAME_H, FRAME_W, 4), dtype=np.uint8)
    for role in np.unique(roles):
        rgba[roles == role] = p[role]
    return Image.fromarray(rgba)


def render_sheet(character):
    """Render the fixed 3-column / 4-row engine contract at native size."""
    sheet = Image.new("RGBA", SHEET_SIZE)
    for row, direction in enumerate(DIRECTIONS):
        for col, pose in enumerate(POSES):
            sheet.paste(render_frame(character, direction, pose),
                        (col * FRAME_W, row * FRAME_H))
    return sheet


C = Character

# Story, Arena Leaders, Council, villains, then townsfolk. Every name is an
# engine sprite key (CHAR_<name>); colours follow the trainer portraits.
CHARACTERS = {
    # --- story -------------------------------------------------------------
    "player_boy": C(skin="honey", hair="spiky", top="tee", top_color="#d8443a",
                    bottom="shorts", bottom_color="#2e4a7c", shoes="#eeeadc",
                    outer_color="#a8683a", extras=("backpack",)),
    "player_girl": C(skin="copper", hair="ponytail", face=("lashes",), top="tee",
                     top_color="#2aa79c", bottom="pants", bottom_color="#2c2a3a",
                     shoes="#3cbcae", accent="#e0505a"),
    # Sudeep: tall quiff with gold aviators, open denim shirt, white tee
    # with a red star, black jeans with a wallet chain, white sneakers.
    "rival": C(skin="honey", hair="quiff", face=("brows", "smirk"), top="overshirt",
               top_color="#f3efe4", outer_color="#5d9ee0", bottom="pants",
               bottom_color="#2b2933", shoes="#f6f4ec",
               extras=("star", "wallet chain")),
    "professor": C(skin="brown", hair="bun", hair_color="grey",
                   face=("glasses", "bindi", "wrinkles"), top="lab coat",
                   top_color="#b3283c", outer_color="#f4f1e8", bottom="saree",
                   accent="#e2b64e", shoes="#6e4a3a", feet="sandals"),
    "amma": C(skin="honey", hair="bun", face=("lashes", "bindi", "earrings", "sindoor"),
              top="saree", top_color="#c04a74", outer_color="#8e2f58",
              bottom="saree", accent="#eec060", shoes="#7a4a3a", feet="sandals",
              extras=("jasmine",)),
    "rohan_mom": C(skin="wheat", hair="braid", face=("lashes", "bindi", "earrings"),
                   top="saree", top_color="#e09040", outer_color="#2f7a72",
                   bottom="saree", accent="#2f8a80", shoes="#7a4a3a", feet="sandals"),
    "techie_f": C(skin="umber", hair="ponytail", face=("lashes", "earrings"),
                  top="kurta", top_color="#efebe0", accent="#3f78c0",
                  bottom="pants", bottom_color="#3b5d92", shoes="#efece4",
                  extras=("lanyard", "folder")),
    # Runs the darshini: a towel on the shoulder and a steel tumbler of
    # filter coffee.
    "darshini_owner": C(skin="umber", build="broad", hair="slick",
                        face=("big moustache", "brows"), top="shirt",
                        top_color="#9cc8e8", sleeves="short", bottom="veshti",
                        bottom_color="#f4f0e6", accent="#3f9a5a",
                        outer_color="#d8443a", shoes="#6a4a32", feet="sandals",
                        extras=("towel", "pockets", "coffee")),
    "shopkeeper": C(skin="brown", hair="balding", hair_color="salt",
                    face=("glasses", "moustache"), top="shirt", top_color="#a98cc0",
                    sleeves="short", bottom="pants", bottom_color="#5a6274",
                    shoes="#3e3a40", extras=("pockets", "belt")),
    "metro_staff": C(skin="honey", hair="bun", face=("lashes", "earrings"),
                     top="suit", top_color="#7a46a8", accent="#f0c040",
                     bottom="pants", bottom_color="#3a3448", shoes="#2e2a34",
                     extras=("lanyard",)),
    "officer": C(skin="copper", hair="short", face=("moustache", "brows"),
                 headwear="police cap", hat_color="#b9a06a", top="shirt",
                 top_color="#bfa66e", sleeves="short", bottom="pants",
                 bottom_color="#a88f5c", shoes="#2e2a30",
                 extras=("belt", "badge", "pockets")),
    "traffic_cop": C(skin="brown", hair="short", face=("moustache",),
                     headwear="police cap", hat_color="#f0ede4", top="shirt",
                     top_color="#f0ece2", sleeves="short", bottom="pants",
                     bottom_color="#b39b66", shoes="#2e2a30",
                     extras=("belt", "badge", "whistle")),
    # --- Arena Leaders ------------------------------------------------------
    "hoovamma": C(skin="deep", hair="topknot", hair_color="grey",
                  face=("bindi", "earrings", "wrinkles"), top="saree",
                  top_color="#3f9a4a", outer_color="#2c6e3a", bottom="saree",
                  accent="#a6d86a", shoes="#6a4a3a", feet="sandals",
                  extra_color="#f08a2a", extras=("top flowers", "watering can")),
    "gundappa": C(skin="brown", build="broad", hair="short",
                  face=("big moustache", "brows"), top="tracksuit",
                  top_color="#2f5fc0", bottom="track", bottom_color="#2f5fc0",
                  shoes="#f2f0ea", extras=("whistle",)),
    "tanvi": C(skin="honey", hair="curly-long", face=("glasses", "lashes"),
               top="hoodie", top_color="#6c46b8", bottom="pants",
               bottom_color="#3f63a0", shoes="#a68ae0", extras=("phone",)),
    "vidya": C(skin="copper", hair="side braid", hair_color="dark brown",
               face=("lashes", "bindi", "earrings"), top="kurta", top_color="#ecb92e",
               accent="#c0702a", bottom="pants", bottom_color="#efe6cf",
               shoes="#9a5a32", feet="sandals", extra_color="#8a2f3a",
               extras=("book",)),
    "rukmini": C(skin="umber", hair="long", face=("lashes", "bindi", "earrings"),
                 top="saree", top_color="#6a3290", outer_color="#4a2066",
                 bottom="saree", accent="#e2b03e", shoes="#5a3a30", feet="sandals"),
    "akash": C(skin="wheat", hair="messy", hair_color="brown", face=("brows",),
               top="jacket", top_color="#8a5634", outer_color="#eadcc0",
               bottom="cargo", bottom_color="#6c7048", shoes="#5a3a28"),
    # --- Council ------------------------------------------------------------
    "nagaraj": C(skin="deep", hair="short", face=("brows", "stubble"),
                 top="kurta", top_color="#34323e", accent="#5aa05a",
                 outer_color="#2f7a46", bottom="pants", bottom_color="#ddd5c2",
                 shoes="#4a3a32", extras=("shawl", "staff")),
    "basappa": C(skin="umber", build="broad", hair="short",
                 face=("big moustache", "brows"), top="shirt", top_color="#f2eee2",
                 sleeves="rolled", bottom="veshti", bottom_color="#f2eee2",
                 accent="#d9a93e", outer_color="#2f8a52", shoes="#6a4a32",
                 feet="sandals", extras=("towel",)),
    "kaveri": C(skin="brown", hair="long", face=("lashes", "bindi", "earrings"),
                top="saree", top_color="#4f94d8", outer_color="#2f6aa8",
                bottom="saree", accent="#d8ecf6", shoes="#5a4a40", feet="sandals"),
    "agni": C(skin="copper", hair="spiky", face=("brows",), top="kurta",
              top_color="#c83a2c", accent="#efb446", bottom="pants",
              bottom_color="#ece4d0", shoes="#5a3428", extras=("chain",)),
    # --- villains -----------------------------------------------------------
    "bhaskar": C(skin="wheat", hair="slick", hair_color="salt",
                 face=("brows", "stubble"), top="suit", top_color="#6a6e82",
                 accent="#a8343c", bottom="pants", bottom_color="#5e6276",
                 shoes="#2a2630", extras=("watch",)),
    "grunt_m": C(skin="brown", hair="buzz", hair_color="grey", face=("beard",),
                 headwear="hard hat", hat_color="#f2b632", top="hi-vis",
                 top_color="#ee7a2a", outer_color="#6a6e78", bottom="cargo",
                 bottom_color="#3e424c", shoes="#4a3a30"),
    "grunt_f": C(skin="copper", hair="ponytail", face=("lashes",),
                 headwear="hard hat", hat_color="#f2b632", top="hi-vis",
                 top_color="#ee7a2a", outer_color="#6a6e78", bottom="cargo",
                 bottom_color="#4a4c3a", shoes="#4a3a30", accent="#c03a4a"),
    # --- trainers and townsfolk with roles ----------------------------------
    "schoolboy": C(skin="honey", build="kid", hair="short", top="school",
                   top_color="#f4f2ea", accent="#c83a3a", bottom="shorts",
                   bottom_color="#2e3f6e", shoes="#2a2630", socks=True,
                   outer_color="#2e4a8a", extras=("backpack",)),
    "schoolgirl": C(skin="deep", build="kid", hair="pigtails", face=("lashes",),
                    top="pinafore", top_color="#f4f2ea", bottom="pinafore",
                    bottom_color="#2f5fb8", accent="#4f8ae0", shoes="#2a2630",
                    socks=True),
    "college_m": C(skin="copper", hair="messy", top="tee", top_color="#3a3a4a",
                   bottom="pants", bottom_color="#4f75aa", shoes="#efece4",
                   outer_color="#2e2e38", extras=("backpack", "watch", "logo")),
    "college_f": C(skin="wheat", hair="curly-long", hair_color="dark brown",
                   face=("lashes", "earrings"), top="overshirt", top_color="#d8665a",
                   outer_color="#eadcc4", bottom="pants", bottom_color="#5a80b8",
                   shoes="#efece4", accent="#8a5a3a", extras=("crossbody",)),
    "techie_m": C(skin="honey", hair="slick", face=("glasses",), top="shirt",
                  top_color="#5f86c4", sleeves="rolled", bottom="pants",
                  bottom_color="#c9b48a", shoes="#5a4034", accent="#d84a4a",
                  outer_color="#4a4e5e", extras=("lanyard", "backpack", "cup")),
    "auto_driver": C(skin="brown", hair="short", face=("moustache", "brows"),
                     top="shirt", top_color="#b8a46a", sleeves="short",
                     bottom="pants", bottom_color="#a8935e", shoes="#4a3a30",
                     outer_color="#e8e2d4", feet="sandals",
                     extras=("pockets", "neck towel")),
    "cricketer": C(skin="deep", hair="short", headwear="cap", hat_color="#cc3a3a",
                   top="jersey", top_color="#f2efe6", accent="#cc3a3a",
                   bottom="pants", bottom_color="#ece8de", shoes="#f4f2ec",
                   extras=("bat",)),
    "gardener": C(skin="copper", hair="short", hair_color="salt",
                  face=("moustache",), headwear="head towel", hat_color="#efeae0",
                  top="tank", top_color="#f2eee4", bottom="lungi",
                  bottom_color="#4a78b8", accent="#c6d8ee", shoes="#6a4a32",
                  feet="sandals", extras=("shears",)),
    "fisher": C(skin="deep", hair="short", face=("stubble",), headwear="straw hat",
                hat_color="#d8b868", top="overshirt", top_color="#efe9dc",
                outer_color="#e07a5a", bottom="lungi", bottom_color="#3f6ab0",
                accent="#9cc0e8", shoes="#6a4a32", feet="barefoot",
                extras=("fishing rod",)),
    "jogger": C(skin="honey", hair="curly-long", face=("lashes",),
                headwear="headband", hat_color="#e04848", top="tank",
                top_color="#e04848", bottom="shorts", bottom_color="#2c2a36",
                shoes="#ee80a0", extras=("watch",)),
    "vendor": C(skin="umber", hair="short", face=("moustache", "brows"),
                top="shirt", top_color="#c9443a", sleeves="rolled",
                bottom="pants", bottom_color="#3a3842", shoes="#3a302c",
                extra_color="#e08a3a", extras=("apron", "tray")),
    "wrestler": C(skin="brown", build="broad", hair="bald",
                  face=("big moustache", "brows"), top="bare", bottom="shorts",
                  bottom_color="#c8343a", shoes="#8e573c", feet="barefoot"),
    "dancer": C(skin="copper", hair="topknot", face=("lashes", "bindi", "earrings"),
                top="dance", top_color="#2f8a4e", bottom="dance",
                bottom_color="#2f8a4e", accent="#ee8a2a", shoes="#ad7149",
                feet="barefoot", extras=("jasmine",)),
    "ajja": C(skin="umber", hair="balding", hair_color="white",
              face=("big moustache", "glasses", "wrinkles"), top="kurta",
              top_color="#f2eee4", accent="#d8c8a0", bottom="veshti",
              bottom_color="#f2eee4", outer_color="#f6f2e8", shoes="#6a4a32",
              feet="sandals", extras=("towel", "cane")),
    "ajji": C(skin="honey", hair="bun", hair_color="grey",
              face=("glasses", "bindi", "wrinkles"), top="saree",
              top_color="#8c2a40", outer_color="#5e1e2c", bottom="saree",
              accent="#e0c070", shoes="#6a4a32", feet="sandals",
              extras=("handbag",)),
    "birdwatcher": C(skin="wheat", hair="buzz", hair_color="grey",
                     headwear="wide brim", hat_color="#8e9064", accent="#6a6c48",
                     outer_color="#6a6c48",
                     top="shirt", top_color="#cdbb86", sleeves="rolled",
                     bottom="cargo", bottom_color="#7a6a4a", shoes="#5a4632",
                     extras=("binoculars", "backpack", "pockets")),
    "delivery_rider": C(skin="brown", hair="short", headwear="helmet",
                        hat_color="#f49030", top="hoodie", top_color="#d2562a",
                        bottom="pants", bottom_color="#34425e", shoes="#3a3a42",
                        accent="#f6982e", extras=("delivery box",)),
    # --- new faces ----------------------------------------------------------
    # Area bois: one lanky in a bandana and neon print, one stocky with a
    # moustache and a loud floral shirt. Both: chain, shades, slick hair.
    "area_boi": C(skin="copper", hair="slick", face=("shades",),
                  headwear="bandana", hat_color="#e03a5a", top="printed",
                  top_color="#3ad6a0", accent="#f6e04a", extra_color="#e03a8a",
                  bottom="pants", bottom_color="#2e4a7a", shoes="#f2f0ea",
                  extras=("chain",)),
    "area_boi2": C(skin="brown", build="broad", hair="slick",
                   face=("shades", "moustache"), top="printed",
                   top_color="#f08a2a", accent="#f6e8c0", extra_color="#d83a3a",
                   bottom="pants", bottom_color="#3a3a4a", shoes="#a86a3a",
                   extras=("chain", "bracelet")),
    # A local don with a heart of gold.
    "rowdy": C(skin="brown", build="broad", hair="slick",
               face=("big moustache", "shades"), top="shirt", top_color="#f6f3ea",
               sleeves="rolled", bottom="veshti-folded", bottom_color="#f6f3ea",
               accent="#d9a93e", shoes="#5a3a2a", feet="sandals",
               extras=("thick chain", "bracelet")),
    "park_ranger": C(skin="copper", hair="short", face=("brows",),
                     headwear="wide brim", hat_color="#5a7a46", accent="#3e5a32",
                     top="shirt", top_color="#4f7244", sleeves="rolled",
                     bottom="cargo", bottom_color="#3e5a36", shoes="#4a3a2a",
                     extras=("binoculars", "badge", "belt", "pockets")),
    "arena_guide": C(skin="honey", hair="short", face=("brows",), headwear="cap",
                     hat_color="#e05a2a", top="tracksuit", top_color="#e05a2a",
                     bottom="track", bottom_color="#2e3448", shoes="#f2f0ea",
                     extras=("whistle", "clipboard")),
    # --- townsfolk ----------------------------------------------------------
    "man1": C(skin="wheat", hair="slick", top="shirt", top_color="#b8604e",
              sleeves="rolled", bottom="pants", bottom_color="#5a6070",
              shoes="#4a3a34", extras=("watch",)),
    "man2": C(skin="deep", hair="curly", face=("stubble",), top="tee",
              top_color="#4f9e8a", bottom="pants", bottom_color="#46699a",
              shoes="#f0eee6"),
    "man3": C(skin="brown", hair="bald", face=("moustache", "brows"), top="kurta",
              top_color="#c8a650", accent="#8a6a2a", bottom="pants",
              bottom_color="#ebe3cf", shoes="#6a4a32", feet="sandals"),
    "man4": C(skin="honey", hair="buzz", hair_color="grey", face=("glasses",),
              top="shirt", top_color="#7393bc", sleeves="short", bottom="pants",
              bottom_color="#6e5e4a", shoes="#3e3430", extras=("belt", "pockets")),
    "woman1": C(skin="copper", hair="braid", face=("lashes", "bindi"),
                top="saree", top_color="#cc8a3a", outer_color="#2f6e5a",
                bottom="saree", accent="#3f8a6a", shoes="#6a4a32", feet="sandals"),
    "woman2": C(skin="deep", hair="bun", face=("lashes", "earrings"), top="kurta",
                top_color="#d0607a", accent="#f0c060", bottom="pants",
                bottom_color="#6a4a7a", shoes="#6a4a40", feet="sandals",
                extra_color="#f08a2a", extras=("flowers",)),
    "woman3": C(skin="wheat", hair="long", hair_color="dark brown",
                face=("lashes",), top="shirt", top_color="#6ea8a2",
                sleeves="elbow", bottom="long skirt", bottom_color="#a8648c",
                shoes="#6a4a40"),
    "woman4": C(skin="umber", hair="bob", face=("lashes",), top="hoodie",
                top_color="#9cac64", bottom="pants", bottom_color="#3f5f86",
                shoes="#f0eee6", extras=("crossbody",), accent="#7a4a3a"),
    "kid1": C(skin="honey", build="kid", hair="curly", top="tee",
              top_color="#ecb83a", bottom="shorts", bottom_color="#5a76a8",
              shoes="#e64a4a"),
    "kid2": C(skin="brown", build="kid", hair="ponytail", face=("lashes",),
              top="tee", top_color="#b07ab8", bottom="skirt",
              bottom_color="#3f9e94", shoes="#f0eee6", accent="#f0c040"),
}

# Style samplers for art review only (dev_preview); never written as sheets.
DEV_CHARACTERS = {
    **{f"hair_{name}": C(hair=name, top_color="#7a9a6a") for name in HAIR},
    **{f"top_{name}": C(top=name, top_color="#c96a4a", outer_color="#e9e4d6",
                        accent="#e2b64e", extra_color="#4fa3c9",
                        bottom_color="#3f5f8a") for name in TOPS},
    **{f"bottom_{name}": C(bottom=name, bottom_color="#3f5f8a", accent="#e2b64e")
       for name in BOTTOMS},
}


def validate_sheet(name, sheet):
    """Engine contract, grounded feet, one connected figure, ink outline."""
    if sheet.mode != "RGBA" or sheet.size != SHEET_SIZE:
        raise ValueError(f"{name}: expected {SHEET_SIZE} RGBA sheet")
    pixels = np.array(sheet)
    if not set(np.unique(pixels[:, :, 3])).issubset({0, 255}):
        raise ValueError(f"{name}: soft alpha is not native pixel art")
    opaque = pixels[:, :, 3] == 255
    if np.any(opaque & np.all(pixels[:, :, :3] == 0, axis=2)):
        raise ValueError(f"{name}: pure black pixel")
    ink = (*rgb(OUTLINE), 255)
    frames = {}
    for row, direction in enumerate(DIRECTIONS):
        for col, pose in enumerate(POSES):
            frame = pixels[row * FRAME_H:(row + 1) * FRAME_H,
                           col * FRAME_W:(col + 1) * FRAME_W]
            frames[direction, pose] = frame
            solid = frame[:, :, 3] == 255
            if not solid[FRAME_H - 1].any():
                raise ValueError(f"{name}/{direction}/{pose}: feet not grounded")
            start = tuple(np.argwhere(solid)[0])
            seen, todo = {start}, [start]
            while todo:
                y, x = todo.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        point = (y + dy, x + dx)
                        if (0 <= point[0] < FRAME_H and 0 <= point[1] < FRAME_W
                                and solid[point] and point not in seen):
                            seen.add(point)
                            todo.append(point)
            if len(seen) != int(solid.sum()):
                raise ValueError(f"{name}/{direction}/{pose}: stray pixels")
            padded = np.pad(solid, 1)
            inside = (padded[:-2, 1:-1] & padded[2:, 1:-1]
                      & padded[1:-1, :-2] & padded[1:-1, 2:])
            if not np.all(frame[solid & ~inside] == ink):
                raise ValueError(f"{name}/{direction}/{pose}: broken outline")
        stand, step_a, step_b = (frames[direction, pose] for pose in POSES)
        if (np.array_equal(stand, step_a) or np.array_equal(stand, step_b)
                or np.array_equal(step_a, step_b)):
            raise ValueError(f"{name}/{direction}: repeated walking pose")
    for pose in POSES:
        if not np.array_equal(frames["left", pose][:, ::-1], frames["right", pose]):
            raise ValueError(f"{name}: RIGHT is not the mirror of LEFT")


def validate_options():
    """Every advertised style, on every build, renders a valid sheet."""
    for build in BODIES:
        for direction in ("down", "up", "left"):
            for pose, art in zip(POSES, BODIES[build][direction]):
                x, y, pixels = art
                if x != 0 or y + pixels.shape[0] != FRAME_H:
                    raise ValueError(f"{build}/{direction}/{pose}: body must reach the ground")
        samples = [Character(build=build, hair=name) for name in HAIR]
        samples += [Character(build=build, headwear=name) for name in HATS]
        samples += [Character(build=build, top=name) for name in TOPS]
        samples += [Character(build=build, bottom=name) for name in BOTTOMS]
        samples += [Character(build=build, face=(name,)) for name in FACE]
        samples += [Character(build=build, extras=(name,)) for name in EXTRAS]
        for character in samples:
            validate_sheet(f"{build} sample", render_sheet(character))


def create_preview(sheets):
    """Every sheet at 3x with its name; rows D / U / L / R, columns S / A / B."""
    columns, scale = 8, 3
    cell_w, cell_h = SHEET_SIZE[0] * scale + 30, SHEET_SIZE[1] * scale + 44
    rows = math.ceil(len(sheets) / columns)
    preview = Image.new("RGB", (columns * cell_w + 24, rows * cell_h + 96), "#d8e6c0")
    draw = ImageDraw.Draw(preview)
    title_font = ImageFont.load_default(size=23)
    name_font = ImageFont.load_default(size=14)
    small_font = ImageFont.load_default(size=11)
    draw.text((24, 15), "URU-MON  /  BENGALURU OVERWORLD CAST", font=title_font, fill=OUTLINE)
    draw.text((24, 47), f"{len(sheets)} original characters  |  native 16 x 32 px frames"
              f"  |  preview {scale}x nearest-neighbour", font=name_font, fill="#4c604f")
    draw.text((24, 67), "Rows: DOWN / UP / LEFT / RIGHT     Columns: STAND / STEP A / STEP B"
              "     Walk: A, STAND, B, STAND", font=small_font, fill="#4c604f")
    for index, (name, sheet) in enumerate(sheets.items()):
        x = 24 + (index % columns) * cell_w
        y = 96 + (index // columns) * cell_h
        draw.text((x + 14, y), name, font=name_font, fill=OUTLINE)
        big = sheet.resize((sheet.width * scale, sheet.height * scale),
                           Image.Resampling.NEAREST)
        preview.paste(big, (x + 14, y + 20), big)
        for row, label in enumerate("DULR"):
            draw.text((x, y + 20 + FRAME_H * scale * row + 40), label,
                      font=small_font, fill="#607254")
    return preview


def dev_preview(names, scale, path):
    """Large labelled sheets for art review: every frame of each preset."""
    known = {**CHARACTERS, **DEV_CHARACTERS}
    sheets = [(name, render_sheet(known[name])) for name in names]
    cell_w = SHEET_SIZE[0] * scale + 24
    cell_h = SHEET_SIZE[1] * scale + 30
    cols = min(len(sheets), max(1, 1800 // cell_w))
    rows = math.ceil(len(sheets) / cols)
    out = Image.new("RGB", (cols * cell_w + 12, rows * cell_h + 12), "#c9dcb4")
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default(size=18)
    for i, (name, sheet) in enumerate(sheets):
        x, y = 12 + (i % cols) * cell_w, 6 + (i // cols) * cell_h
        draw.text((x, y), name, font=font, fill=OUTLINE)
        big = sheet.resize((sheet.width * scale, sheet.height * scale),
                           Image.Resampling.NEAREST)
        out.paste(big, (x, y + 24), big)
    out.save(path)
    print(f"dev preview: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="validate all presets and options without writing files")
    parser.add_argument("--dev", metavar="NAMES",
                        help="comma-separated presets (or style samplers) to draw large")
    parser.add_argument("--scale", type=int, default=6, help="scale for --dev")
    parser.add_argument("--out", default=str(ROOT / "art-src/previews/characters_dev.png"),
                        help="output path for --dev")
    args = parser.parse_args()
    if args.dev:
        names = list(CHARACTERS) if args.dev == "all" else args.dev.split(",")
        dev_preview(names, args.scale, args.out)
        return
    validate_options()
    sheets = {name: render_sheet(character) for name, character in CHARACTERS.items()}
    for name, sheet in sheets.items():
        validate_sheet(name, sheet)
    if args.check:
        print(f"Validated {len(sheets)} characters, {len(sheets) * 12} frames, and every option.")
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    for name, sheet in sheets.items():
        sheet.save(OUTPUT_DIR / f"{name}.png", optimize=True)
    create_preview(sheets).save(PREVIEW_PATH, optimize=True)
    print(f"Wrote {len(sheets)} character sheets to {OUTPUT_DIR}")
    print(f"Preview: {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
