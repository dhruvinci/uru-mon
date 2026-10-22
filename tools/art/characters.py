#!/usr/bin/env python3
"""Original, hand-pixelled Bengaluru overworld characters.

Run ``python3 tools/art/characters.py`` from any directory. Only the 52 character
PNGs and art-src/previews/characters_preview.png are written. Pillow and numpy
are the only third-party dependencies. No source images, fonts or random seeds
are needed.

Sheets are native RGBA, 48 x 96: DOWN / UP / LEFT / RIGHT, each with STAND /
STEP_A / STEP_B. Play columns 1, 0, 2, 0. RIGHT is mirrored *after* compositing,
including asymmetric clothing and accessories. Both steps lower the head and
torso by one pixel, while independently drawn legs retain the ground baseline.

Authoring: O outline; s/k/l skin/shadow/light; h/H/j hair/shadow/light;
e eyes; m mouth; t/T/u top/shadow/light; b/B/v bottom/shadow/light;
f/F/g shoes/shadow/light; a/A/c accent/shadow/light; w/W white/shadow;
q/Q coat/shadow; r reflective tape; d/D wood/shadow; n metal.
Dots are transparent in bodies and leave pixels untouched in overlay grids.
Overlay '-' explicitly erases a pixel. All artwork is ASCII, never geometric
drawing primitives. ImageDraw is used only for contact-sheet text.

Public API: Character(...), render_frame(character, direction, pose), and
render_sheet(character). Colours accept Pillow colour names or #rrggbb. Skin
is a key in SKIN_TONES; hair_color is independent of the hairstyle (grey-short
defaults to grey). Long garments and accessories have separate directional
overlays; lab coats can be worn over a saree via under_top='saree'.
"""

from dataclasses import dataclass, replace
from pathlib import Path
import argparse
import math

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont


FRAME_SIZE = (16, 24)
SHEET_SIZE = (48, 96)
DIRECTIONS = ("down", "up", "left", "right")
POSES = ("stand", "step_a", "step_b")
OUTLINE = "#2a2230"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "assets/images/characters"
PREVIEW_PATH = ROOT / "art-src/previews/characters_preview.png"

# Explicit ramps preserve warmth in every skin tone, including the shadows.
# Order: base, shadow, light.
SKIN_TONES = {
    "wheat": ("#dca875", "#b87851", "#f0c694"),
    "honey": ("#c68b58", "#9d603f", "#e0aa71"),
    "copper": ("#ad7149", "#815039", "#cf9460"),
    "brown": ("#8e573c", "#673d30", "#b57b50"),
    "deep": ("#6c4234", "#4f302c", "#945f43"),
    "umber": ("#7d4b32", "#57342b", "#a26a45"),
}
HAIR_STYLES = ("short", "side-part", "curly", "ponytail", "long braid",
               "bun", "bald", "grey-short")
HEADWEAR = ("none", "cricket cap", "hard hat", "bike helmet", "police cap")
TOPS = ("t-shirt", "collared shirt", "kurta", "saree", "lab coat",
        "school uniform", "hi-vis vest", "sports jersey", "hoodie",
        "suit jacket", "aviator jacket", "tracksuit", "bare", "dance costume")
BOTTOMS = ("pants", "shorts", "jeans", "lungi/dhoti", "skirt")
EXTRAS = ("glasses", "backpack", "moustache", "walking stick", "apron",
          "binoculars", "lanyard", "bindi", "earrings")


def grid(text):
    """Parse and strictly check an ASCII grid; indentation is not artwork."""
    rows = tuple(line.strip() for line in text.strip().splitlines())
    if not rows or len({len(row) for row in rows}) != 1:
        raise ValueError(f"Ragged pixel grid: {rows!r}")
    valid = set(".OsklheHjmtTubBvfFgaAcwWqQr dDn-".replace(" ", ""))
    unknown = set("".join(rows)) - valid
    if unknown:
        raise ValueError(f"Unknown pixel roles: {unknown}")
    return np.array([list(row) for row in rows], dtype="<U1")


# Every pose is drawn independently: the planted foot, passing foot, sleeve,
# hand and leg break are authored, rather than moving a rigid sprite around.
# The bald base is deliberately neutral; hair silhouettes are layered later.
BASE_BODIES = {
    "down": tuple(map(grid, (
        """
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssesssseskO..
        ..OssesssseskO..
        ...OssssksskO...
        ....OssmmkkO....
        .....OkkkkO.....
        .....OssskO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OtttttttTTTO..
        ..OsktttttTksO..
        ...OOtttttTOO...
        ....ObbbBBBO....
        ....ObbOObBO....
        ....ObbOObBO....
        ...OggfOOfgFO...
        ...OOOO..OOOO...
        """,
        """
        ................
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssesssseskO..
        ..OssesssseskO..
        ...OssssksskO...
        ....OssmmkkO....
        .....OkkkkO.....
        .....OssskO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OssOttttTTTO..
        ..OskOttttTksO..
        ...OOtttttTkO...
        ....ObbOOBBO....
        ....ObbOOfFO....
        ...OggfO.OOO....
        ...OOOO.........
        """,
        """
        ................
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssesssseskO..
        ..OssesssseskO..
        ...OssssksskO...
        ....OssmmkkO....
        .....OkkkkO.....
        .....OssskO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OutttttTOssO..
        ..OskttttTOskO..
        ...OktttttTOO...
        ....ObbOOBBO....
        ....OgfOObBO....
        ....OOO.OfgFO...
        .........OOOO...
        """,
    ))),
    "up": tuple(map(grid, (
        """
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssssssssskO..
        ..OssssssssskO..
        ...OssssssskO...
        ....OsssskkO....
        .....OkkkkO.....
        .....OkkksO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OtttttttTTTO..
        ..OsktttttTksO..
        ...OOtttttTOO...
        ....ObbbBBBO....
        ....ObbOObBO....
        ....ObbOObBO....
        ...OgfFOOfgFO...
        ...OOOO..OOOO...
        """,
        """
        ................
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssssssssskO..
        ..OssssssssskO..
        ...OssssssskO...
        ....OsssskkO....
        .....OkkkkO.....
        .....OkkksO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OutttttTOssO..
        ..OskttttTOskO..
        ...OktttttTOO...
        ....ObbOOBBO....
        ....OgfOObBO....
        ....OOO.OfgFO...
        .........OOOO...
        """,
        """
        ................
        ................
        .....OOOOOO.....
        ...OOllllssOO...
        ...OllllssssO...
        ..OllllssssskO..
        ..OlllsssssskO..
        ..OlsssssssskO..
        ..OssssssssskO..
        ..OssssssssskO..
        ...OssssssskO...
        ....OsssskkO....
        .....OkkkkO.....
        .....OkkksO.....
        ....OuttttTO....
        ...OutttttTTO...
        ..OuttttttTTTO..
        ..OssOttttTTTO..
        ..OskOttttTksO..
        ...OOtttttTkO...
        ....ObbOOBBO....
        ....ObbOOfFO....
        ...OggfO.OOO....
        ...OOOO.........
        """,
    ))),
    "left": tuple(map(grid, (
        """
        ................
        ......OOOOO.....
        ....OOlllssOO...
        ...OllllssssO...
        ...OlllssssskO..
        ..OllllssssskO..
        ..OslssssssskO..
        ..OessssssskkO..
        .OseessksskkkO..
        ..OsssskskkkO...
        ...OssmkkkkO....
        ....OOkkkOO.....
        .....OsskO......
        ....OutttTO.....
        ....OutttTTO....
        ....OttttTTO....
        ....OtttTTTO....
        ....OtsskTTO....
        ....OOkkOTTO....
        .....ObbBBO.....
        .....ObOBBO.....
        .....ObOBBO.....
        ....OgfOfFO.....
        ....OOOOOOO.....
        """,
        """
        ................
        ................
        ......OOOOO.....
        ....OOlllssOO...
        ...OllllssssO...
        ...OlllssssskO..
        ..OllllssssskO..
        ..OslssssssskO..
        ..OessssssskkO..
        .OseessksskkkO..
        ..OsssskskkkO...
        ...OssmkkkkO....
        ....OOkkkOO.....
        .....OsskO......
        ....OutttTO.....
        ....OutttTTO....
        ....OuttTTTTO...
        ....OtttTOssO...
        ...OktttTOskO...
        ...OkttttTOO....
        ....ObbBOBBO....
        ...ObbBO.OfFO...
        ..OggfO..OOOO...
        ..OOOO..........
        """,
        """
        ................
        ................
        ......OOOOO.....
        ....OOlllssOO...
        ...OllllssssO...
        ...OlllssssskO..
        ..OllllssssskO..
        ..OslssssssskO..
        ..OessssssskkO..
        .OseessksskkkO..
        ..OsssskskkkO...
        ...OssmkkkkO....
        ....OOkkkOO.....
        .....OsskO......
        ....OutttTO.....
        ....OutttTTO....
        ...OuutttTTO....
        ...OssOttTTO....
        ...OskOttTTkO...
        ....OOtttTTkO...
        ....ObbBOBBO....
        ...OfFO..ObBO...
        ...OOO...OfgFO..
        .........OOOOO..
        """,
    ))),
}


def patch(x, y, text):
    return (x, y, grid(text))


# Hair caps, drawn on the bald head. Tufts and partings change the silhouette;
# the rear view fills the cranium instead of repeating the face.
HAIR = {
    "short": {
        "down": patch(2, 1, """
            ...OOOOOO...
            .OOjjhhhhOO.
            .OhjjhhhhHO.
            OhhhhHhhhHHO
            OhHHHssHHHHO
            OhO......OHO
            .O........O.
        """),
        "up": patch(2, 1, """
            ...OOOOOO...
            .OOjjhhhhOO.
            .OhjjhhhhHO.
            OhjjhhhhhHHO
            OhhhhhhhhHHO
            OhhhhhhhhHHO
            OhhhhhhhHHHO
            OhHhhhHHHHHO
            .OHHHHHHHHO.
            ..OHHHHHHO..
            ...OOOOOO...
        """),
        "left": patch(3, 1, """
            ...OOOOO...
            .OOjjhhhOO.
            OhjjhhhhHO.
            OhhhhhhhHHO
            OhHHhhhhHHO
            .OssOHhhHHO
            ....OhhhHHO
            .....OHHHHO
            ......OHHO.
            .......OO..
        """),
    },
    "side-part": {
        "down": patch(2, 1, """
            ...OOOOOO...
            .OOjjjHhhOO.
            .OhjjjHhhHO.
            OhjjhhHhhHHO
            OhhhHHshHHHO
            OhHHssssOHHO
            .Os......sO.
        """),
        "up": patch(2, 1, """
            ...OOOOOO...
            .OOjjjHhhOO.
            .OhjjjHhhHO.
            OhjjjhHhhHHO
            OhjjhhhhhHHO
            OhhhhhhhhHHO
            OhhhhhhhhHHO
            OhHhhhhHHHHO
            .OHHHHHHHHO.
            ..OHHHHHHO..
            ...OOOOOO...
        """),
        "left": patch(3, 1, """
            ...OOOOO...
            .OOjjhhhOO.
            OhjjjhhhHO.
            OhjjhhhhHHO
            OhhhHhhhHHO
            .HHsOHhhHHO
            ....OhhhHHO
            .....OHHHHO
            ......OHHO.
            .......OO..
        """),
    },
    "curly": {
        "down": patch(1, 0, """
            .....OOOO.....
            ...OOjhhHOO...
            ..OhjHhjHhHO..
            .OhjHhjHhhhHO.
            OhhHhjHhjHhHHO
            OHHhHHhHhHhHHO
            .OHssHssHssHO.
            ..O........O..
        """),
        "up": patch(1, 0, """
            .....OOOO.....
            ...OOjhhHOO...
            ..OhjHhjHhHO..
            .OhjHhjHhhhHO.
            OhhHhjHhjHhHHO
            OHjHhjHhjHhHHO
            .OhHhjHhjHhHO.
            .OHhjHhjHhHHO.
            ..OhHhHHhHHO..
            ..OHHhHHHHHO..
            ...OHHHHHHO...
            ....OOOOOO....
        """),
        "left": patch(2, 0, """
            .....OOOO....
            ...OOjhhHOO..
            ..OhjHhjHhHO.
            .OhjHhjHhhhHO
            OhhHhjHhjHhHO
            OHhHHhHhjHHHO
            .OHssOHhhHHO.
            .....OhHHHHO.
            ......OHHHHO.
            .......OHHO..
            ........OO...
        """),
    },
    "bald": {},
}

# Long styles share a swept crown but each has its own rear/side silhouette.
# These additions are stamped after clothing, so the braid rests over a kurta.
HAIR_TAILS = {
    "ponytail": {
        "down": patch(11, 7, """
            .OO.
            OhHO
            OhHO
            OhHO
            OHHO
            .OHO
            ..O.
        """),
        "up": patch(6, 8, """
            .OOO.
            OacaO
            OhhHO
            OhhHO
            OhhHO
            OhHHO
            .OHHO
            ..OO.
        """),
        "left": patch(11, 6, """
            .OO.
            OacO
            OhHO
            OhHO
            OhHO
            OHHO
            OHHO
            .OO.
        """),
    },
    "long braid": {
        "down": patch(10, 9, """
            .OO.
            OhHO
            OhHO
            OHhO
            OhHO
            OHhO
            OaaO
            .OO.
        """),
        "up": patch(6, 9, """
            .OO.
            OhHO
            OHhO
            OhHO
            OHhO
            OhHO
            OHhO
            OaaO
            .OO.
        """),
        "left": patch(10, 9, """
            .OO.
            OhHO
            OhHO
            OHhO
            OhHO
            OHhO
            OaaO
            .OO.
        """),
    },
    "bun": {
        "down": patch(10, 1, """
            .OO.
            OhHO
            OjHO
            .OO.
        """),
        "up": patch(9, 5, """
            .OOO.
            OhjhO
            OhhHO
            OHHHO
            .OOO.
        """),
        "left": patch(11, 5, """
            .OO.
            OhHO
            OjHO
            OHHO
            .OO.
        """),
    },
    # 'long' is an additional style for Rukmini, beyond the required eight.
    "long": {
        "down": patch(2, 8, """
            OhO......OHO
            OhO......OHO
            OhHO....OHHO
            OhHO....OHHO
            OhHO....OHHO
            OHHO....OHHO
            .OO......OO.
        """),
        "up": patch(3, 8, """
            OhhhhhhhHO
            OhhhhhhhHO
            OhjhhhhhHO
            OhjhhhhhHO
            OhhhhhhhHO
            OHHhhHHHHO
            .OOOOOOOO.
        """),
        "left": patch(8, 8, """
            OhhhHO
            OhhhHO
            OhhhHO
            OhhhHO
            OhhhHO
            OHhHHO
            .OOOO.
        """),
    },
}


HATS = {
    "cricket cap": {
        "down": patch(2, 0, """
            ....OOOO....
            ..OOuccTOO..
            .OuuccctTTO.
            OutttwttTTTO
            OtttttttTTTO
            OOOOOOOOOOOO
            .OaaacaaaAO.
            ..OOOOOOOO..
        """),
        "up": patch(2, 0, """
            ....OOOO....
            ..OOuccTOO..
            .OuuccctTTO.
            OuttttttTTTO
            OtttttttTTTO
            OtttOOOtTTTO
            .OaaWWWaaAO.
            ..OOOOOOOO..
        """),
        "left": patch(0, 0, """
            .......OOOO...
            .....OOuccTOO.
            ....OuuccctTTO
            ...OuttttttTTO
            ...OtttttttTTO
            .OOOOOOOOOOOTO
            OaaacaaaAAOOOO
            .OOOOOOOOO....
        """),
    },
    "hard hat": {
        "down": patch(1, 0, """
            .....OOOO.....
            ...OOuccTOO...
            ..OuuucccTTO..
            ..OuttcttTTO..
            .OutttcttTTTO.
            OuuuuuuuuuuTTO
            .OOOOOOOOOOOO.
        """),
        "up": patch(1, 0, """
            .....OOOO.....
            ...OOuccTOO...
            ..OuuucccTTO..
            ..OuttcttTTO..
            .OutttcttTTTO.
            OuuuuuuuuuuTTO
            .OOOOOOOOOOOO.
        """),
        "left": patch(1, 0, """
            .....OOOO.....
            ...OOuccTOO...
            ..OuuccctTTO..
            ..OutctttTTO..
            .OuttctttTTTO.
            OuuuuuuuuuuTTO
            .OOOOOOOOOOOO.
        """),
    },
    "bike helmet": {
        "down": patch(2, 0, """
            ....OOOO....
            ..OOuuutOO..
            .OuuwwttTTO.
            OutwwtttTTTO
            OtwwttttTTTO
            OOOOOOOOOOOO
            OtO......OTO
            OtO......OTO
            OtO......OTO
            .TO......TO.
        """),
        "up": patch(2, 0, """
            ....OOOO....
            ..OOuuutOO..
            .OuuwwttTTO.
            OutwwtttTTTO
            OtwwttttTTTO
            OttwwtttTTTO
            OttwwtttTTTO
            OttwwtttTTTO
            .OtttttTTTO.
            ..OOOOOOOO..
        """),
        "left": patch(2, 0, """
            .....OOOO...
            ...OOuutTOO.
            ..OuwwttTTO.
            .OuwwtttTTTO
            .OtwwtttTTTO
            OOOOOtttTTTO
            .....OttTTTO
            .....OttTTTO
            ......OtTTO.
            ......OOOO..
        """),
    },
    "police cap": {
        "down": patch(2, 0, """
            ...OOOOOO...
            .OOwwwwwWOO.
            OwwwwwwwwwWO
            OwwwwaawwwWO
            .OwwwaawwWO.
            .OOOOOOOOOO.
            ..OfggffFO..
            ...OOOOOO...
        """),
        "up": patch(2, 0, """
            ...OOOOOO...
            .OOwwwwwWOO.
            OwwwwwwwwwWO
            OwwwwwwwwwWO
            .OwwwwwwwWO.
            .OOOOOOOOOO.
            ..OFFFFFWO..
            ...OOOOOO...
        """),
        "left": patch(0, 0, """
            ......OOOOOO..
            ....OOwwwwwWOO
            ...OwwwwwwwwWO
            ...OwwwwwwwwWO
            ...OawwwwwwWWO
            ..OOOOOOOOOOOO
            .OfggfffFO....
            ..OOOOOOO.....
        """),
    },
}


@dataclass(frozen=True)
class Character:
    skin: str = "honey"
    hair: str = "short"
    hair_color: str | None = None
    headwear: str = "none"
    hat_color: str = "#3974ac"
    top: str = "t-shirt"
    top_color: str = "#398d86"
    bottom: str = "pants"
    bottom_color: str = "#46566e"
    shoes: str = "#745449"
    accent: str = "#e5b956"
    extras: tuple[str, ...] = ()
    under_top: str | None = None
    under_color: str = "#a75481"
    build: str = "regular"

    def __post_init__(self):
        choices = {
            "skin": SKIN_TONES,
            "hair": (*HAIR_STYLES, "long"),
            "headwear": HEADWEAR,
            "top": TOPS,
            "bottom": BOTTOMS,
            "build": ("regular", "broad"),
            "under_top": (None, "saree"),
        }
        for key, allowed in choices.items():
            if getattr(self, key) not in allowed:
                raise ValueError(f"Unknown {key}: {getattr(self, key)!r}")
        if set(self.extras) - set(EXTRAS):
            raise ValueError(f"Unknown extras: {set(self.extras) - set(EXTRAS)}")
        for value in (self.hair_color, self.hat_color, self.top_color,
                      self.bottom_color, self.shoes, self.accent, self.under_color):
            if value is not None:
                ImageColor.getrgb(value)


def ramp(color):
    """A small, warm-shadow / cool-light ramp; no pure-black palette entries."""
    rgb = np.array(ImageColor.getrgb(color), dtype=float)
    if rgb.shape != (3,):
        raise ValueError("Material colours must be RGB, without alpha")
    shadow = np.rint(rgb * .69 + np.array((42, 34, 48)) * .31).astype(int)
    light = np.rint(rgb * .72 + np.array((255, 244, 217)) * .28).astype(int)
    # A requested black material still uses a coloured near-black ink.
    base = tuple(max(12, int(c)) for c in rgb)
    return base, tuple(shadow), tuple(light)


def palette(character):
    p = {".": (0, 0, 0, 0), "O": (*ImageColor.getrgb(OUTLINE), 255),
         "e": (*ImageColor.getrgb(OUTLINE), 255)}
    hair_color = character.hair_color or (
        "#a9aba6" if character.hair == "grey-short" else "#3d3032")
    top_color = character.top_color
    if character.top in ("lab coat", "school uniform"):
        top_color = "#eee9d9"
    for roles, color in (("hHj", hair_color), ("tTu", top_color),
                         ("bBv", character.bottom_color), ("fFg", character.shoes),
                         ("aAc", character.accent), ("wWn", "#eee9d9"),
                         ("qQr", "#f4f0e3"), ("dDm", "#9a6c43")):
        for role, rgb in zip(roles, ramp(color)):
            p[role] = (*rgb, 255)
    for role, color in zip("skl", SKIN_TONES[character.skin]):
        p[role] = (*ImageColor.getrgb(color), 255)
    p["m"] = p["k"]
    p["r"] = (240, 239, 181, 255)
    p["n"] = (154, 181, 180, 255)
    if character.top == "bare":
        for top_role, skin_role in zip("tTu", "skl"):
            p[top_role] = p[skin_role]
    return p


def stamp(canvas, overlay, bob=0, mapping=None):
    """Composite roles with explicit clipping checks, not silent truncation."""
    x, y, pixels = overlay
    y += bob
    h, w = pixels.shape
    if x < 0 or y < 0 or x + w > 16 or y + h > 24:
        raise ValueError(f"Overlay outside frame: {(x, y, w, h)}")
    for py, px in np.argwhere(pixels != "."):
        role = pixels[py, px]
        canvas[y + py, x + px] = "." if role == "-" else (
            mapping.get(role, role) if mapping else role)


# Garments sit within the shoulder/hand contours. Hems have their own outline
# and stop above the planted shoe. Fronts, backs and profiles are separate art.
GARMENTS = {
    "kurta": {
        "down": patch(4, 13, """
            OuttttTO
            OttwttTO
            OttattTO
            OttattTO
            OtttttTO
            OtttttTO
            OttttTTO
            OaaaaAAO
        """),
        "up": patch(4, 13, """
            OuttttTO
            OtttttTO
            OtttttTO
            OtttttTO
            OtttttTO
            OtttttTO
            OttttTTO
            OaaaaAAO
        """),
        "left": patch(5, 13, """
            utttTO
            tttTTO
            tttTTO
            tttTTO
            tttTTO
            tttTTO
            tttTTO
            aaaaAO
        """),
    },
    "saree": {
        "down": patch(4, 13, """
            OuttaTTO
            OttaaTTO
            OtaaTTTO
            OaaTTTTO
            OatttTTO
            OttttTTO
            OuttTTTO
            OuttTTTO
            OaaaaAAO
        """),
        "up": patch(4, 13, """
            OuttaTTO
            OttaaTTO
            OtaaTTTO
            OaaTTTTO
            OatttTTO
            OttttTTO
            OuttTTTO
            OuttTTTO
            OaaaaAAO
        """),
        "left": patch(4, 13, """
            OuttaTO
            OttaTTO
            OtaTTTO
            OatTTTO
            OttTTTO
            OutTTTO
            OutTTTO
            OutTTTO
            OaaaaAO
        """),
    },
    "lab coat": {
        "down": patch(4, 13, """
            OqwssqQO
            OqqwwqQO
            OqqtTqQO
            OqqtTqQO
            OQqtTqQO
            OqqtTqQO
            OqqtTqQO
            OQQtTQQO
        """),
        "up": patch(4, 13, """
            OqqqqqQO
            OqqqqqQO
            OqqqqqQO
            OqqqqqQO
            OQQQQQQO
            OqqqqqQO
            OqqqQqQO
            OQQQQQQO
        """),
        "left": patch(4, 13, """
            OqqqqQO
            OqqqqQO
            OqqqqQO
            OqqqqQO
            OqQqqQO
            OqqqqQO
            OqqqqQO
            OQQQQQO
        """),
    },
    "skirt": {
        "down": patch(4, 18, """
            ObbbbBBO
            ObvbbBBO
            ObvbBBBO
            OBBBBBBO
        """),
        "up": patch(4, 18, """
            ObbbbBBO
            ObvbbBBO
            ObvbBBBO
            OBBBBBBO
        """),
        "left": patch(4, 18, """
            ObbbBBO
            ObvbBBO
            ObvbBBO
            OBBBBBO
        """),
    },
    "lungi/dhoti": {
        "down": patch(4, 18, """
            OwwwwwWO
            OwwwWwWO
            OwwWwwWO
            OaaaaAAO
        """),
        "up": patch(4, 18, """
            OwwwwwWO
            OwwWwwWO
            OwwWwwWO
            OaaaaAAO
        """),
        "left": patch(4, 18, """
            OwwwwWO
            OwwWwWO
            OwwWwWO
            OaaaaAO
        """),
    },
}


TOP_DETAILS = {
    "collared shirt": {
        "down": patch(5, 13, """
            wtsstW
            twtwWT
            ttatTT
            ttatwT
            ttatTT
        """),
        "up": patch(5, 13, """
            uwwwWT
            ttttTT
        """),
        "left": patch(4, 13, """
            .uwT..
            .twTT.
            .ttTT.
            .ttwT.
        """),
    },
    "school uniform": {
        "down": patch(5, 13, """
            wsssWW
            wwawWW
            wwawWW
            wwawWW
            wwAwWW
            aaaaaA
        """),
        "up": patch(5, 13, """
            wwwwWW
            wwwwWW
            wwwwWW
            wwwwWW
            wwwwWW
            aaaaaA
        """),
        "left": patch(4, 13, """
            .wwWW.
            .awWW.
            .awWW.
            .wwWW.
            .wwWW.
            .aaaA.
        """),
    },
    "hi-vis vest": {
        "down": patch(4, 13, """
            OtwwwTTO
            OtrwTrTO
            OtrwTrTO
            OrrrrrrO
            OttwTTTO
            OrrrrrrO
        """),
        "up": patch(4, 13, """
            OttttTTO
            OtrtTrTO
            OtrtTrTO
            OrrrrrrO
            OtttTTTO
            OrrrrrrO
        """),
        "left": patch(4, 13, """
            OtttTTO
            OttrTTO
            OttrTTO
            OrrrrrO
            OtttTTO
            OrrrrrO
        """),
    },
    "sports jersey": {
        "down": patch(5, 13, """
            awsswa
            uawwaT
            utwwtT
            uttwtT
            utwwtT
        """),
        "up": patch(5, 13, """
            aaaaaA
            uttttT
            utwwtT
            uttwtT
            uttwtT
        """),
        "left": patch(4, 13, """
            .aatt.
            .utta.
            .utTa.
            .utTT.
        """),
    },
    "hoodie": {
        "down": patch(4, 12, """
            .OtssTO.
            OutwwTTO
            OttwTwTO
            OttttTTO
            OttttTTO
            OtTTTTTO
            OttttTTO
        """),
        "up": patch(4, 12, """
            .OOOOOO.
            OuttttTO
            OutttTTO
            .OTTTTO.
            ..OOOO..
        """),
        "left": patch(5, 12, """
            .OOO..
            OttTO.
            OttTTO
            .OTTO.
            ..OO..
        """),
    },
    "suit jacket": {
        "down": patch(5, 13, """
            wwswWT
            TwwWTT
            tTaTTT
            ttattT
            ttattT
            ttTttT
        """),
        "up": patch(5, 13, """
            uTTTTT
            uttttT
            uttttT
            uttttT
            uttTtT
        """),
        "left": patch(5, 13, """
            wttTT
            TwtTT
            tTtTT
            tttTT
            tttTT
        """),
    },
    "aviator jacket": {
        "down": patch(5, 13, """
            wwssWW
            twtwWT
            ttatTT
            TwatWT
            ttatTT
            aaaaaA
        """),
        "up": patch(5, 13, """
            wwwwWW
            uttttT
            uttttT
            uttttT
            uttttT
            aaaaaA
        """),
        "left": patch(5, 13, """
            wwwwW
            uttTT
            uttTT
            uTtTT
            uttTT
            aaaaA
        """),
    },
    "tracksuit": {
        "down": patch(5, 13, """
            wtsstW
            wttwtW
            wttwtW
            wttwtW
            wttwtW
            wttwtW
        """),
        "up": patch(5, 13, """
            wttttW
            wttttW
            wttttW
            wttttW
            wttttW
            wttttW
        """),
        "left": patch(5, 13, """
            uwttW
            uwttW
            uwttW
            uwttW
            uwttW
            uwttW
        """),
    },
    "dance costume": {
        "down": patch(4, 13, """
            OatssTaO
            OtaaaTTO
            OttatTTO
            OaaaaaaO
            OttatTTO
            OttaaTTO
            OtaaaaTO
            OatatTaO
            OaaaaaaO
        """),
        "up": patch(4, 13, """
            OatssTaO
            OttatTTO
            OttatTTO
            OaaaaaaO
            OttatTTO
            OttaaTTO
            OtaaaaTO
            OatatTaO
            OaaaaaaO
        """),
        "left": patch(4, 13, """
            OatsTaO
            OtaaTTO
            OttTTTO
            OaaaaaO
            OttTTTO
            OtaTTTO
            OtaaTTO
            OataaTO
            OaaaaaO
        """),
    },
}


# Accessories are intentionally small but still directional: two lenses on
# the front, one on the profile, no lenses on the back of the head.
ACCESSORIES = {
    "glasses": {
        "down": patch(4, 7, """
            nnn..nnn.
            neOnOneOn
            .nn..nn..
        """),
        "up": patch(2, 8, """
            OO........OO
        """),
        "left": patch(1, 7, """
            .nnn......
            nseOnnnnn.
            .nnn......
        """),
    },
    "moustache": {
        "down": patch(5, 9, """
            .h..h.
            hHHHHh
        """),
        "left": patch(3, 10, """
            hHHh
        """),
    },
    "bindi": {"down": patch(7, 6, "a")},
    "earrings": {
        "down": patch(2, 9, "a..........a"),
        "left": patch(8, 9, "a"),
    },
    "backpack": {
        "down": patch(4, 13, """
            .a....a.
            .a....a.
            .A....A.
            .A....A.
        """),
        "up": patch(4, 13, """
            .OOOOOO.
            OcaaaaAO
            OcaWWaAO
            OcaaaaAO
            OaAAAAAO
            OacaaaAO
            .OOOOOO.
        """),
        "left": patch(10, 13, """
            .OO.
            OcAO
            OcAO
            OaAO
            OaAO
            OAAO
            .OO.
        """),
    },
    "apron": {
        "down": patch(5, 14, """
            .w..w.
            .wwWW.
            wwwWWW
            wwwWWW
            wwWWWW
            wwwWWW
            WWWWWW
        """),
        "up": patch(4, 17, """
            wwwwwWWW
            ..WwW...
            ..w.w...
        """),
        "left": patch(4, 14, """
            .w....
            .w....
            ww....
            wwwWWW
            ww....
            ww....
            WW....
        """),
    },
    "binoculars": {
        "down": patch(5, 13, """
            O....O
            .O..O.
            .O..O.
            OOOOOO
            OnOOnO
            OOOOOO
        """),
        "up": patch(5, 13, """
            .OOOO.
            O....O
        """),
        "left": patch(4, 13, """
            .O..
            .O..
            O...
            OO..
            OnO.
            OOO.
        """),
    },
    "lanyard": {
        "down": patch(6, 13, """
            a..a
            a..a
            .aa.
            .ww.
            .wa.
        """),
        "up": patch(6, 13, "aaaa"),
        "left": patch(5, 13, """
            a..
            a..
            a..
            ww.
            wa.
        """),
    },
}

# The stick stays grounded (no bob). Its handle meets the swinging hand.
STICKS = {
    "down": patch(12, 17, """
        OOO.
        OdDO
        .OdO
        .OdO
        .OdO
        .OdO
        .OOO
    """),
    "up": patch(0, 17, """
        .OOO
        OdDO
        OdO.
        OdO.
        OdO.
        OdO.
        OOO.
    """),
    "left": patch(1, 17, """
        .OOOO
        OdDDO
        OdO..
        OdO..
        OdO..
        OdO..
        OOO..
    """),
}


def apply_clothes(canvas, character, direction, pose):
    bob = int(pose != "stand")
    if character.build == "broad":
        # Replace the torso, including its old edge, so widening cannot leave
        # a second outline inside the shoulders. Hand poses retain opposition.
        if direction != "left":
            wide = grid("""
                ..OutttttttTTO..
                .OuttttttttTTTO.
                .OtttttttttTTTO.
                .OskttttttTTksO.
                ..OOttttttTTOO..
            """) if pose == "stand" else grid("""
                ..OutttttttTTO..
                .OuttttttttTTTO.
                .OssOttttttTTTO.
                .OskOtttttTTksO.
                ..OOttttttTTkO..
            """)
            if (direction == "down" and pose == "step_b"
                    or direction == "up" and pose == "step_a"):
                wide = wide[:, ::-1].copy()
            canvas[14 + bob:19 + bob] = wide
        else:
            # Extra chest width is authored separately from the near arm.
            stamp(canvas, patch(3, 14, """
                OutttTTTO.
                OutttTTTTO
                OttttTTTTO
                OttttTTTTO
                .OtttTTTTO
            """), bob)
    if character.bottom == "shorts":
        # Knees follow the independently drawn legs, including profile strides.
        lower = canvas[20:22]
        lower[lower == "b"] = "s"
        lower[lower == "B"] = "k"
    elif character.bottom in GARMENTS:
        stamp(canvas, GARMENTS[character.bottom][direction], bob)

    if character.top == "hi-vis vest":
        for before, after in zip("tTu", "wWw"):
            canvas[canvas == before] = after

    if character.under_top == "saree":
        # A separate colour ramp keeps Sharada's saree visible under her coat.
        stamp(canvas, GARMENTS["saree"][direction], bob,
              {"t": "i", "T": "I", "u": "z"})
    if character.top in GARMENTS:
        mapping = {"t": "i", "T": "I"} if character.under_top else None
        stamp(canvas, GARMENTS[character.top][direction], bob, mapping)
    if character.top in TOP_DETAILS:
        stamp(canvas, TOP_DETAILS[character.top][direction], bob)


def apply_near_arm(canvas, character, direction, pose):
    # The near arm is in front of both garments and torso accessories. A bag
    # or apron must not erase the hand as it swings across the body.
    if direction == "left":
        sleeves = {
            "stand": patch(5, 15, """
                uttO
                ttTO
                sskO
                OkkO
            """),
            "step_b": patch(3, 16, """
                OuuO
                OssO
                OskO
                .OO.
            """),
            "step_a": patch(8, 16, """
                OTTTO
                .OssO
                .OskO
                ..OO.
            """),
        }
        sleeve_map = {"t": "q", "T": "Q", "u": "q"} if character.top == "lab coat" else None
        if character.top == "hi-vis vest":
            sleeve_map = {"t": "w", "T": "W", "u": "w"}
        # Poses already include their own vertical placement, unlike garments.
        stamp(canvas, sleeves[pose], mapping=sleeve_map)


def outline(canvas):
    """Keep exactly one ink pixel at the outer silhouette after layering.

    This does not grow or smooth the hand-drawn art. It restores only the
    existing edge pixels, so overlays cannot leak a coloured outside edge.
    """
    solid = canvas != "."
    padded = np.pad(solid, 1)
    interior = (padded[:-2, 1:-1] & padded[2:, 1:-1]
                & padded[1:-1, :-2] & padded[1:-1, 2:])
    canvas[solid & ~interior] = "O"


def render_roles(character, direction, pose):
    if direction not in DIRECTIONS or pose not in POSES:
        raise ValueError(f"Unknown direction/pose: {direction!r}/{pose!r}")
    if direction == "right":
        return render_roles(character, "left", pose)[:, ::-1].copy()
    canvas = BASE_BODIES[direction][POSES.index(pose)].copy()
    bob = int(pose != "stand")
    apply_clothes(canvas, character, direction, pose)
    for extra in character.extras:
        if extra in ("backpack", "apron", "binoculars", "lanyard"):
            overlay = ACCESSORIES[extra].get(direction)
            if overlay:
                stamp(canvas, overlay, bob)
    if "walking stick" in character.extras:
        stamp(canvas, STICKS[direction])
    apply_near_arm(canvas, character, direction, pose)

    style = character.hair
    crown = "short" if style == "grey-short" else (
        "side-part" if style in HAIR_TAILS else style)
    if direction in HAIR[crown]:
        stamp(canvas, HAIR[crown][direction], bob)
    if style in HAIR_TAILS:
        stamp(canvas, HAIR_TAILS[style][direction], bob)
    if character.headwear != "none":
        stamp(canvas, HATS[character.headwear][direction], bob,
              {"t": "C", "T": "V", "u": "L", "c": "L"})
    for extra in character.extras:
        if extra in ("glasses", "moustache", "bindi", "earrings"):
            overlay = ACCESSORIES[extra].get(direction)
            if overlay:
                stamp(canvas, overlay, bob)
    outline(canvas)
    return canvas


def render_frame(character, direction="down", pose="stand"):
    """Return a fresh 16 x 24 RGBA image; no filesystem side effects."""
    roles = render_roles(character, direction, pose)
    p = palette(character)
    hat_color = "#e8ba3b" if character.headwear == "hard hat" else character.hat_color
    for role, color in zip("CVL", ramp(hat_color)):
        p[role] = (*color, 255)
    for role, color in zip("iIz", ramp(character.under_color)):
        p[role] = (*color, 255)
    rgba = np.zeros((24, 16, 4), dtype=np.uint8)
    for role in np.unique(roles):
        rgba[roles == role] = p[role]
    return Image.fromarray(rgba)


def render_sheet(character):
    """Render the fixed 3-column / 4-row engine contract at native size."""
    sheet = Image.new("RGBA", SHEET_SIZE)
    for row, direction in enumerate(DIRECTIONS):
        for col, pose in enumerate(POSES):
            sheet.paste(render_frame(character, direction, pose), (col * 16, row * 24))
    return sheet


# The task's explicit roster contains 52 names (rather than its approximate
# '~45'). Keep all of them, in story / leaders / council / townsfolk order.
CHARACTERS = {
    "player_boy": Character(skin="honey", hair="short", top="t-shirt",
        top_color="#cc5b48", bottom="shorts", bottom_color="#3d657e",
        accent="#dfb551", extras=("backpack",), shoes="#e4d4ae"),
    "player_girl": Character(skin="copper", hair="ponytail", top="t-shirt",
        top_color="#36a6a3", bottom="shorts", bottom_color="#635183",
        accent="#ecb35e", extras=("backpack",), shoes="#e7d3b3"),
    "rival": Character(skin="wheat", hair="side-part", headwear="cricket cap",
        hat_color="#326bb0", top="sports jersey", top_color="#326bb0",
        bottom_color="#e0dfcd", accent="#e2b34f", shoes="#e9dfc2"),
    "professor": Character(skin="brown", hair="bun", hair_color="#554344",
        top="lab coat", under_top="saree", under_color="#398e8e",
        accent="#e4bc64", extras=("glasses", "bindi")),
    "amma": Character(skin="honey", hair="bun", top="saree",
        top_color="#b94c6d", accent="#e4bb62", extras=("bindi", "earrings")),
    "rohan_mom": Character(skin="wheat", hair="long braid", top="saree",
        top_color="#dc9146", accent="#367f78", extras=("bindi",)),
    "hoovamma": Character(skin="deep", hair="bun", hair_color="#b6b5ab",
        top="saree", top_color="#52844e", accent="#e5bc69",
        extras=("bindi", "earrings")),
    "gundappa": Character(skin="brown", hair="short", top="tracksuit",
        top_color="#346879", bottom_color="#346879", accent="#dbac55",
        extras=("moustache",), build="broad", shoes="#d7d5c5"),
    "tanvi": Character(skin="honey", hair="ponytail", top="hoodie",
        top_color="#8464a5", bottom="jeans", bottom_color="#3c617f",
        accent="#dc7954", extras=("glasses",), shoes="#d7d8cb"),
    "vidya": Character(skin="copper", hair="long braid", top="kurta",
        top_color="#d69a4c", bottom_color="#317e7a", accent="#8a496e",
        extras=("glasses", "bindi")),
    "rukmini": Character(skin="umber", hair="long", top="saree",
        top_color="#86539c", accent="#e6bd69", extras=("bindi", "earrings")),
    "akash": Character(skin="wheat", hair="side-part", top="aviator jacket",
        top_color="#997249", bottom="jeans", bottom_color="#426b88",
        accent="#e6c494", shoes="#554651"),
    "nagaraj": Character(skin="deep", hair="long", top="kurta",
        top_color="#403e4d", bottom_color="#77634b", accent="#9bb65b",
        extras=("moustache",)),
    "basappa": Character(skin="umber", hair="curly", top="collared shirt",
        top_color="#c6a875", bottom="lungi/dhoti", accent="#538354",
        extras=("moustache",), build="broad", shoes="#80593c"),
    "kaveri": Character(skin="brown", hair="long braid", top="saree",
        top_color="#3e80b4", accent="#9ed2c2", extras=("bindi", "earrings")),
    "agni": Character(skin="copper", hair="curly", hair_color="#754038",
        top="kurta", top_color="#ce4f3e", bottom_color="#dcc895",
        accent="#efb446"),
    "bhaskar": Character(skin="wheat", hair="side-part", headwear="hard hat",
        top="suit jacket", top_color="#505168", bottom_color="#505168",
        accent="#ad4845", shoes="#49414a"),
    "grunt_m": Character(skin="brown", hair="short", headwear="hard hat",
        top="hi-vis vest", top_color="#e98432", bottom_color="#59616b",
        accent="#d2bf74", shoes="#6f5942"),
    "grunt_f": Character(skin="copper", hair="ponytail", headwear="hard hat",
        top="hi-vis vest", top_color="#e98432", bottom_color="#59616b",
        accent="#935071", shoes="#6f5942"),
    "schoolboy": Character(skin="honey", hair="short", top="school uniform",
        bottom="shorts", bottom_color="#547089", accent="#3f6290",
        extras=("backpack",), shoes="#4c444d"),
    "schoolgirl": Character(skin="deep", hair="long braid", top="school uniform",
        bottom="skirt", bottom_color="#547089", accent="#3f6290",
        extras=("backpack",), shoes="#4c444d"),
    "college_m": Character(skin="copper", hair="curly", top="collared shirt",
        top_color="#c28854", bottom="jeans", bottom_color="#466e92",
        accent="#62916e", extras=("backpack",)),
    "college_f": Character(skin="wheat", hair="ponytail", top="kurta",
        top_color="#5ba391", bottom="jeans", bottom_color="#4b6489",
        accent="#c85b72", extras=("backpack",)),
    "techie_m": Character(skin="honey", hair="side-part", top="collared shirt",
        top_color="#6c9cac", bottom="jeans", bottom_color="#455e7e",
        accent="#9c5fa0", extras=("backpack", "lanyard", "glasses")),
    "techie_f": Character(skin="umber", hair="bun", top="collared shirt",
        top_color="#c47a89", bottom="pants", bottom_color="#4d576e",
        accent="#507dac", extras=("backpack", "lanyard")),
    "auto_driver": Character(skin="brown", hair="short", top="collared shirt",
        top_color="#b39a66", bottom_color="#9e865c", accent="#657550",
        extras=("moustache",)),
    "cricketer": Character(skin="deep", hair="short", headwear="cricket cap",
        hat_color="#3e886e", top="sports jersey", top_color="#eee6ce",
        bottom_color="#d8d9c7", accent="#3e886e", shoes="#e6dac1"),
    "gardener": Character(skin="copper", hair="curly", top="collared shirt",
        top_color="#6c9861", bottom="shorts", bottom_color="#977c54",
        accent="#ddbb68"),
    "fisher": Character(skin="deep", hair="short", top="t-shirt",
        top_color="#639caa", bottom="lungi/dhoti", accent="#326a9a",
        extras=("moustache",), shoes="#8f6543"),
    "jogger": Character(skin="honey", hair="ponytail", top="sports jersey",
        top_color="#d37691", bottom="shorts", bottom_color="#575d7b",
        accent="#d9d99c", shoes="#e8dec5"),
    "vendor": Character(skin="umber", hair="side-part", top="collared shirt",
        top_color="#c28751", bottom_color="#6d6572", extras=("apron",)),
    "wrestler": Character(skin="brown", hair="short", top="bare",
        bottom="shorts", bottom_color="#bb4844", accent="#e3ba71",
        extras=("moustache",), shoes="#8e573c", build="broad"),
    "dancer": Character(skin="copper", hair="bun", top="dance costume",
        top_color="#b34459", bottom="skirt", bottom_color="#368575",
        accent="#e4b956", extras=("bindi", "earrings"), shoes="#ad7149"),
    "ajja": Character(skin="umber", hair="grey-short", top="kurta",
        top_color="#e6e0cb", bottom="lungi/dhoti", accent="#a17c55",
        extras=("glasses", "moustache", "walking stick"), shoes="#805b42"),
    "ajji": Character(skin="honey", hair="bun", hair_color="#b6b5ab",
        top="saree", top_color="#a17799", accent="#e0c687",
        extras=("glasses", "bindi")),
    "birdwatcher": Character(skin="wheat", hair="grey-short",
        headwear="cricket cap", hat_color="#8b9767", top="collared shirt",
        top_color="#d1bd83", bottom="shorts", bottom_color="#71875e",
        accent="#879868", extras=("binoculars", "backpack")),
    "delivery_rider": Character(skin="brown", hair="short", headwear="bike helmet",
        hat_color="#ce6840", top="aviator jacket", top_color="#e2853b",
        bottom="jeans", bottom_color="#41637c", accent="#eab363",
        extras=("backpack",)),
    "traffic_cop": Character(skin="copper", hair="short", headwear="police cap",
        top="collared shirt", top_color="#bda675", bottom_color="#9c875f",
        accent="#dfb04d", extras=("moustache",), shoes="#594a46"),
    "darshini_owner": Character(skin="umber", hair="side-part", top="collared shirt",
        top_color="#e6e0cd", bottom_color="#807362", accent="#c1a672",
        extras=("apron", "moustache")),
    "shopkeeper": Character(skin="brown", hair="bald", top="collared shirt",
        top_color="#b294b7", bottom_color="#5c6475", accent="#d6b76e",
        extras=("glasses", "moustache")),
    "metro_staff": Character(skin="honey", hair="bun", top="collared shirt",
        top_color="#9067a7", bottom_color="#57516c", accent="#d8a95e",
        extras=("lanyard",)),
    "officer": Character(skin="copper", hair="side-part", top="collared shirt",
        top_color="#e7e4d5", bottom_color="#666451", accent="#648b6c",
        extras=("glasses",)),
    "man1": Character(skin="wheat", hair="side-part", top="collared shirt",
        top_color="#b56858", bottom_color="#6d7380", accent="#b7c284"),
    "man2": Character(skin="deep", hair="curly", top="t-shirt",
        top_color="#55998a", bottom="jeans", bottom_color="#506d8b"),
    "man3": Character(skin="brown", hair="bald", top="kurta",
        top_color="#b29f65", bottom_color="#e0d4b7", accent="#6c7753",
        extras=("moustache",)),
    "man4": Character(skin="honey", hair="grey-short", top="collared shirt",
        top_color="#738eaf", bottom_color="#716453", extras=("glasses",)),
    "woman1": Character(skin="copper", hair="long braid", top="saree",
        top_color="#c17e43", accent="#5a8e72", extras=("bindi",)),
    "woman2": Character(skin="deep", hair="bun", top="kurta",
        top_color="#c96379", bottom_color="#745375", accent="#dfbc68"),
    "woman3": Character(skin="wheat", hair="long", top="collared shirt",
        top_color="#7da6a3", bottom="skirt", bottom_color="#ab7090",
        accent="#deb461"),
    "woman4": Character(skin="umber", hair="ponytail", top="hoodie",
        top_color="#9caa6c", bottom="jeans", bottom_color="#496783",
        accent="#c78a55"),
    "kid1": Character(skin="honey", hair="curly", top="t-shirt",
        top_color="#e5b755", bottom="shorts", bottom_color="#647b9e",
        shoes="#e5d0a5"),
    "kid2": Character(skin="brown", hair="ponytail", top="t-shirt",
        top_color="#ab79ad", bottom="shorts", bottom_color="#59a098",
        accent="#e6ba6b", shoes="#e3cca8"),
}


def validate_sheet(name, sheet):
    """Check the engine contract plus disconnected pixels and outline leaks."""
    if sheet.mode != "RGBA" or sheet.size != SHEET_SIZE:
        raise ValueError(f"{name}: expected 48x96 RGBA sheet")
    pixels = np.array(sheet)
    if not set(np.unique(pixels[:, :, 3])).issubset({0, 255}):
        raise ValueError(f"{name}: soft alpha is not native pixel art")
    opaque = pixels[:, :, 3] == 255
    if np.any(opaque & np.all(pixels[:, :, :3] == 0, axis=2)):
        raise ValueError(f"{name}: pure black pixel")
    ink = (*ImageColor.getrgb(OUTLINE), 255)
    for row, direction in enumerate(DIRECTIONS):
        for col, pose in enumerate(POSES):
            frame = pixels[row * 24:(row + 1) * 24, col * 16:(col + 1) * 16]
            solid = frame[:, :, 3] == 255
            if not solid[22].any() or not solid[23].any():
                raise ValueError(f"{name}/{direction}/{pose}: feet not grounded")
            start = tuple(np.argwhere(solid)[0])
            seen, todo = {start}, [start]
            while todo:
                y, x = todo.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        point = (y + dy, x + dx)
                        if (0 <= point[0] < 24 and 0 <= point[1] < 16
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
        frames = [pixels[row * 24:(row + 1) * 24, col * 16:(col + 1) * 16]
                  for col in range(3)]
        if any(np.array_equal(frames[a], frames[b])
               for a, b in ((0, 1), (0, 2), (1, 2))):
            raise ValueError(f"{name}/{direction}: repeated walking pose")
        if any(not np.array_equal(frames[0][:12], step[1:13]) for step in frames[1:]):
            raise ValueError(f"{name}/{direction}: head bob must be exactly 1px")
    for col in range(3):
        left = pixels[48:72, col * 16:(col + 1) * 16]
        right = pixels[72:96, col * 16:(col + 1) * 16]
        if not np.array_equal(left[:, ::-1], right):
            raise ValueError(f"{name}: RIGHT is not the exact mirror of LEFT")


def create_preview(sheets):
    """Every complete sheet at exactly 4x, with names and frame/row labels."""
    columns, cell_w, cell_h = 6, 228, 432
    rows = math.ceil(len(sheets) / columns)
    preview = Image.new("RGB", (columns * cell_w + 24, rows * cell_h + 100),
                        "#d8e6c0")
    draw = ImageDraw.Draw(preview)
    title_font = ImageFont.load_default(size=23)
    name_font = ImageFont.load_default(size=14)
    small_font = ImageFont.load_default(size=11)
    draw.text((24, 15), "URU-MON  /  BENGALURU OVERWORLD CAST", font=title_font,
              fill=OUTLINE)
    draw.text((24, 47),
              f"{len(sheets)} original characters  |  native 16 x 24 px  |  preview 4x nearest-neighbour",
              font=name_font, fill="#4c604f")
    draw.text((24, 67), "Rows: DOWN / UP / LEFT / RIGHT     Columns: STAND / STEP A / STEP B     Walk: A, STAND, B, STAND",
              font=small_font, fill="#4c604f")
    for index, (name, sheet) in enumerate(sheets.items()):
        x, y = 24 + (index % columns) * cell_w, 100 + (index // columns) * cell_h
        draw.text((x + 16, y), name, font=name_font, fill=OUTLINE)
        for col, label in enumerate(("STAND", "A", "B")):
            draw.text((x + 18 + col * 64, y + 19), label, font=small_font,
                      fill="#607254")
        big = sheet.resize((192, 384), Image.Resampling.NEAREST)
        preview.paste(big, (x + 16, y + 36), big)
        for row, label in enumerate(("D", "U", "L", "R")):
            draw.text((x, y + 78 + row * 96), label, font=small_font,
                      fill="#607254")
    return preview


def validate_options():
    """Exercise every advertised option, including options not in the cast."""
    for direction, poses in BASE_BODIES.items():
        if len(poses) != 3 or any(pose.shape != (24, 16) for pose in poses):
            raise ValueError(f"Invalid base grid dimensions for {direction}")
    base = Character()
    choices = {"skin": SKIN_TONES, "hair": (*HAIR_STYLES, "long"),
               "headwear": HEADWEAR, "top": TOPS, "bottom": BOTTOMS,
               "extras": ((extra,) for extra in EXTRAS),
               "hair_color": ("#478dca", "#af466e", "black"),
               "build": ("regular", "broad")}
    for key, values in choices.items():
        for value in values:
            character = replace(base, **{key: value})
            validate_sheet(f"option {key}={value}", render_sheet(character))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate all presets and options without writing files")
    args = parser.parse_args()
    validate_options()
    sheets = {name: render_sheet(character) for name, character in CHARACTERS.items()}
    for name, sheet in sheets.items():
        validate_sheet(name, sheet)
    if args.check:
        print(f"Validated {len(sheets)} characters, {len(sheets) * 12} frames, and every option.")
        return
    preview = create_preview(sheets)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    for name, sheet in sheets.items():
        sheet.save(OUTPUT_DIR / f"{name}.png", optimize=True)
    preview.save(PREVIEW_PATH, optimize=True)
    print(f"Wrote {len(sheets)} character sheets to {OUTPUT_DIR}")
    print(f"Preview: {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
