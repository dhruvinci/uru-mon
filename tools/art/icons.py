"""Small hand-pixelled UI and world icons (16 px), written to assets/images/ui and assets/images/world.

Run: python3 tools/art/icons.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAL = {
    ".": (0, 0, 0, 0),
    "o": (42, 34, 48, 255),      # outline
    "s": (214, 220, 230, 255),   # steel
    "S": (166, 174, 190, 255),   # steel shade
    "h": (248, 250, 255, 255),   # highlight
    "d": (120, 126, 146, 255),   # dark steel
    "r": (200, 64, 74, 255),     # red band / exclaim
    "R": (150, 40, 56, 255),
    "w": (255, 255, 255, 255),
    "y": (240, 196, 80, 255),
    "Y": (200, 150, 50, 255),
    "f": (232, 168, 70, 255),    # food peeking out
}

# A two-tier steel tiffin dabba with a clip handle
DABBA = """
................
......oooo......
.....o.dd.o.....
....oooooooo....
...ohhssssssSo..
...osssssssSSo..
...oooooooooo...
...orrrrrrrRo...
...oooooooooo...
...ohsssssssSo..
...ossssssSSSo..
...osssssssSSo..
...oSSSSSSSSdo..
....oooooooo....
................
................
"""

DABBA_OPEN = """
................
...oooooooooo...
...ohhssssssSo..
...oooooooooo...
................
...ooooooooo....
...offyffyffo...
...oyffffyffo...
...oooooooooo...
...ohsssssssSo..
...ossssssSSSo..
...osssssssSSo..
...oSSSSSSSSdo..
....oooooooo....
................
................
"""

EXCLAIM = """
....oooooooo....
...owwwwwwwwo...
..owwwwrrwwwwo..
..owwwwrrwwwwo..
..owwwwrrwwwwo..
..owwwwrrwwwwo..
..owwwwrrwwwwo..
..owwwwwwwwwwo..
..owwwwrrwwwwo..
...owwwwwwwwo...
....ooowwooo....
.......owo......
........o.......
................
................
................
"""


def grid_image(art):
    rows = [r for r in art.strip("\n").split("\n")]
    h = len(rows)
    w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            img.putpixel((x, y), PAL.get(ch, (255, 0, 255, 255)))
    return img


def main():
    ui = os.path.join(ROOT, "assets", "images", "ui")
    world = os.path.join(ROOT, "assets", "images", "world")
    os.makedirs(ui, exist_ok=True)
    os.makedirs(world, exist_ok=True)
    grid_image(DABBA).save(os.path.join(ui, "dabba.png"))
    grid_image(DABBA_OPEN).save(os.path.join(ui, "dabba_open.png"))
    grid_image(EXCLAIM).save(os.path.join(ui, "exclaim.png"))
    # dabba lying on the ground as a pickup
    grid_image(DABBA).save(os.path.join(world, "item_ball.png"))
    # invisible logic tiles for the Tiled layers (tinted for debugging only)
    Image.new("RGBA", (64, 64), (255, 0, 0, 90)).save(os.path.join(world, "collision.png"))
    Image.new("RGBA", (64, 64), (0, 255, 0, 90)).save(os.path.join(world, "encounter.png"))
    print("icons written")


if __name__ == "__main__":
    main()
