"""Builds assets/data/{species,moves,items}.json from the Python content tables, with validation.

Run: python3 tools/content/build_data.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from species_data import SPECIES  # noqa: E402
from moves_data import MOVES, MOVE_BY_NAME  # noqa: E402
from learnsets_data import LINES, EXTRA  # noqa: E402
from items_data import ITEMS  # noqa: E402
from trainers_data import TRAINERS  # noqa: E402

TYPES = {"NORMAL", "FIRE", "WATER", "GRASS", "ELECTRIC", "EARTH", "ROCK", "SKY", "BUG", "TOXIC", "FIGHT", "MIND",
         "SPIRIT", "METAL"}


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def main():
    by_id = {s["id"]: s for s in SPECIES}
    if len(by_id) != len(SPECIES):
        fail("duplicate species id")
    move_ids = {m["id"] for m in MOVES}
    if len(move_ids) != len(MOVES):
        fail("duplicate move id")
    for m in MOVES:
        if m["type"] not in TYPES:
            fail(f"bad type on move {m['name']}")

    learn = {}
    for line, entries in LINES.items():
        for sid in line:
            learn.setdefault(sid, []).extend(entries)
    for sid, entries in EXTRA.items():
        learn.setdefault(sid, []).extend(entries)

    species_out = []
    for s in SPECIES:
        for t in s["types"]:
            if t not in TYPES:
                fail(f"bad type {t} on {s['name']}")
        if s["evolution"] and s["evolution"][1] not in by_id:
            fail(f"bad evolution target on {s['name']}")
        entries = learn.get(s["id"])
        if not entries:
            fail(f"no learnset for {s['name']}")
        seen = set()
        learnset = []
        for lvl, name in sorted(entries, key=lambda e: e[0]):
            if name not in MOVE_BY_NAME:
                fail(f"unknown move {name!r} in learnset of {s['name']}")
            mid = MOVE_BY_NAME[name]["id"]
            if mid in seen:
                continue
            seen.add(mid)
            learnset.append({"level": lvl, "moveId": mid})
        species_out.append({
            "id": s["id"],
            "name": s["name"],
            "types": s["types"],
            "baseStats": s["base"],
            "catchRate": s["catchRate"],
            "baseExp": s["baseExp"],
            "evolution": {"level": s["evolution"][0], "speciesId": s["evolution"][1]} if s["evolution"] else None,
            "learnset": learnset,
            "dex": s["dex"],
            "assetKey": f"MON_{s['id']:03d}",
        })

    moves_out = []
    for m in MOVES:
        out = {k: m[k] for k in ("id", "name", "type", "category", "power", "accuracy", "pp", "priority", "description")}
        out["effect"] = m["effect"]
        moves_out.append(out)

    for tid, t in TRAINERS.items():
        for mon in t["team"]:
            sp = mon["species"]
            if isinstance(sp, int) and sp not in by_id:
                fail(f"trainer {tid}: unknown species {sp}")
            if isinstance(sp, str) and not (sp.startswith(("RIVAL:", "PLAYER:")) and sp[-1] in "123"):
                fail(f"trainer {tid}: bad species ref {sp}")
            for mv in mon.get("moves", []):
                if mv not in MOVE_BY_NAME:
                    fail(f"trainer {tid}: unknown move {mv}")

    data_dir = os.path.join(ROOT, "assets", "data")
    for name, payload in (("species", species_out), ("moves", moves_out), ("items", ITEMS), ("trainers", TRAINERS)):
        with open(os.path.join(data_dir, f"{name}.json"), "w") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    print(f"wrote {len(species_out)} species, {len(moves_out)} moves, {len(ITEMS)} items, {len(TRAINERS)} trainers")

    unused = move_ids - {e["moveId"] for s in species_out for e in s["learnset"]}
    if unused:
        print("note: moves not in any learnset:", sorted(m["name"] for m in MOVES if m["id"] in unused))


if __name__ == "__main__":
    main()
