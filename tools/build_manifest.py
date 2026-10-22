"""Scans assets/ and writes assets/manifest.json, which the preload scene uses to load everything.

Run: python3 tools/build_manifest.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")


def rel(*parts):
    return "/".join(("assets",) + parts)


def files(*parts, ext=".png"):
    d = os.path.join(A, *parts)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(ext))


def main():
    images, sheets, maps, audio = [], [], [], []

    for f in files("images", "creatures"):
        images.append({"key": f"MON_{f[:3]}", "url": rel("images", "creatures", f)})
    for f in files("images", "characters"):
        sheets.append({"key": f"CHAR_{f[:-4]}", "url": rel("images", "characters", f), "frameWidth": 16, "frameHeight": 24})
    for f in files("images", "trainers"):
        images.append({"key": f"TRAINER_{f[:-4]}", "url": rel("images", "trainers", f)})
    for f in files("images", "battle"):
        images.append({"key": f"BATTLE_BG_{f[:-4].upper()}", "url": rel("images", "battle", f)})

    ui_keys = {"dabba": "UI_DABBA", "dabba_open": "UI_DABBA_OPEN", "exclaim": "UI_EXCLAIM", "title_bg": "UI_TITLE_BG",
               "title_logo": "UI_TITLE_LOGO", "region_map": "UI_REGION_MAP"}
    for f in files("images", "ui"):
        key = ui_keys.get(f[:-4], f"UI_{f[:-4].upper()}")
        images.append({"key": key, "url": rel("images", "ui", f)})
    world_keys = {"collision": "WORLD_COLLISION", "encounter": "WORLD_ENCOUNTER", "tall_grass": "WORLD_TALL_GRASS",
                  "item_ball": "WORLD_ITEM_BALL"}
    for f in files("images", "world"):
        images.append({"key": world_keys.get(f[:-4], f"WORLD_{f[:-4].upper()}"), "url": rel("images", "world", f)})

    index_path = os.path.join(A, "maps", "index.json")
    if os.path.exists(index_path):
        for m in json.load(open(index_path)):
            mid = m["id"]
            entry = {"key": f"MAP_{mid}", "url": rel("maps", mid, "map.json"), "bg": rel("maps", mid, "bg.png")}
            if os.path.exists(os.path.join(A, "maps", mid, "fg.png")):
                entry["fg"] = rel("maps", mid, "fg.png")
            maps.append(entry)

    for kind in ("music", "sfx"):
        d = os.path.join(A, "audio", kind)
        if not os.path.isdir(d):
            continue
        names = sorted({f.rsplit(".", 1)[0] for f in os.listdir(d) if f.endswith((".ogg", ".mp3", ".m4a"))})
        for n in names:
            urls = [rel("audio", kind, f"{n}.{e}") for e in ("ogg", "m4a", "mp3") if os.path.exists(os.path.join(d, f"{n}.{e}"))]
            audio.append({"key": f"{kind.upper()}_{n.upper()}", "urls": urls})

    out = {"images": images, "spritesheets": sheets, "maps": maps, "audio": audio}
    with open(os.path.join(A, "manifest.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"manifest: {len(images)} images, {len(sheets)} sheets, {len(maps)} maps, {len(audio)} audio")


if __name__ == "__main__":
    main()
