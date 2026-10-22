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
from refs_data import REFS, SPECIAL_HABITAT  # noqa: E402
import roster_plan  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tools", "maps"))
from encounters import ENCOUNTERS  # noqa: E402


def references():
    """species id -> the Bengaluru reference of its family."""
    by_name = {s["name"]: s["id"] for s in SPECIES}
    refs = {}
    for f in roster_plan.FAMILIES:
        for stage in f["stages"]:
            refs[by_name[stage[0]]] = f["angle"]
    parent = {s["evolution"][1]: s["id"] for s in SPECIES if s["evolution"]}
    for s in SPECIES:
        root = s["id"]
        while root in parent:
            root = parent[root]
        if root in REFS:
            refs[s["id"]] = REFS[root]
    return refs


def habitats():
    """species id -> where to find it: wild areas, special events, or evolving."""
    try:
        names = {m["id"]: m["name"] for m in json.load(open(os.path.join(ROOT, "assets", "maps", "index.json")))}
    except FileNotFoundError:
        names = {}
    kinds = {"grass": "", "cave": "", "fish": " (fishing)"}
    found = {}
    for map_id, zones in ENCOUNTERS.items():
        for zone, table in zones.items():
            for slot in table["slots"]:
                where = names.get(map_id, map_id) + kinds.get(zone, "")
                if where not in found.setdefault(slot["species"], []):
                    found[slot["species"]].append(where)
    by_id = {s["id"]: s for s in SPECIES}
    parent = {s["evolution"][1]: s["id"] for s in SPECIES if s["evolution"]}
    out = {}
    for s in SPECIES:
        sid = s["id"]
        spots = list(found.get(sid, []))
        if sid in SPECIAL_HABITAT:
            spots.insert(0, SPECIAL_HABITAT[sid])
        if not spots and sid in parent:
            p = by_id[parent[sid]]
            spots.append(f"Evolve {p['name']} (Lv {p['evolution'][0]})")
        out[sid] = spots
    return out

TYPES = {"NORMAL", "FIRE", "WATER", "GRASS", "ELECTRIC", "EARTH", "ROCK", "SKY", "BUG", "TOXIC", "FIGHT", "MIND",
         "SPIRIT", "METAL", "FROST", "MYTH", "ROGUE", "CHARM"}


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

    refs = references()
    habitat = habitats()
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
            "ref": refs.get(s["id"], ""),
            "habitat": habitat.get(s["id"], []),
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
