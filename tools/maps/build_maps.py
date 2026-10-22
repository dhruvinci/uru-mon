"""Compiles every map module, validates connections, writes assets/maps/index.json and the manifest.

Run: python3 tools/maps/build_maps.py [--preview]
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))

from compiler import MapBuild, validate  # noqa: E402
import tiles  # noqa: E402

MODULES = ["maps_start", "maps_south", "maps_central", "maps_north", "maps_council"]


def main():
    defs = []
    for name in MODULES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name == name:
                continue
            raise
        defs.extend(mod.MAPS)
    ids = [d["id"] for d in defs]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        print("duplicate map ids:", dupes)
        sys.exit(1)

    built = [MapBuild(d).build() for d in defs]
    problems = validate(built)
    for p in problems:
        print("WARN", p)

    index = [{"id": b.id, "name": b.d.get("name", b.id), "width": b.w, "height": b.h, "interior": b.d.get("interior", False)}
             for b in built]
    with open(os.path.join(ROOT, "assets", "maps", "index.json"), "w") as fh:
        json.dump(index, fh, indent=1)

    world_dir = os.path.join(ROOT, "assets", "images", "world")
    os.makedirs(world_dir, exist_ok=True)
    tiles.tall_grass_overlay().save(os.path.join(world_dir, "tall_grass.png"))

    print(f"built {len(built)} maps")
    if "--preview" in sys.argv:
        from PIL import Image
        prev = os.path.join(ROOT, "art-src", "previews", "maps")
        os.makedirs(prev, exist_ok=True)
        for b in built:
            img = Image.open(os.path.join(ROOT, "assets", "maps", b.id, "bg.png")).convert("RGBA")
            # mark NPCs, warps and blocked tiles for review
            from PIL import ImageDraw
            d = ImageDraw.Draw(img)
            for w in b.warps:
                d.rectangle([w["x"] * 16, w["y"] * 16, w["x"] * 16 + 15, w["y"] * 16 + 15], outline=(0, 120, 255, 255))
            for n in b.d.get("npcs", []):
                d.ellipse([n["x"] * 16 + 3, n["y"] * 16 + 3, n["x"] * 16 + 12, n["y"] * 16 + 12], fill=(255, 40, 160, 255))
            for it in b.d.get("items", []):
                d.rectangle([it["x"] * 16 + 5, it["y"] * 16 + 5, it["x"] * 16 + 10, it["y"] * 16 + 10], fill=(255, 220, 0, 255))
            img.save(os.path.join(prev, f"{b.id}.png"))
    os.system(f"{sys.executable} -I {os.path.join(ROOT, 'tools', 'build_manifest.py')}")
    if problems:
        sys.exit(2)


if __name__ == "__main__":
    main()
