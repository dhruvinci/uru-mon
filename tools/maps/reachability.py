"""Static reachability check for every compiled map.

From each map's entry points (warps, spawn), flood-fill walkable tiles. Every warp, NPC, item, sign and
interactable must touch a reachable tile. NPCs that disappear later (hideIf / showIf) don't count as walls;
everyone else does. Run after build_maps.py: python3 tools/maps/reachability.py
"""
import json
import os
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check(map_id):
    data = json.load(open(os.path.join(ROOT, "assets", "maps", map_id, "map.json")))
    w, h = data["width"], data["height"]
    coll = next(l for l in data["layers"] if l["name"] == "Collision")["data"]
    uru = data["uru"]
    blocked = {(i % w, i // w) for i, v in enumerate(coll) if v}
    for n in uru["npcs"]:
        if "hideIf" not in n and "showIf" not in n:
            blocked.add((n["x"], n["y"]))
    for it in uru["items"]:
        blocked.add((it["x"], it["y"]))

    starts = []
    step = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
    for wp in uru["warps"]:
        dx, dy = step.get(wp.get("exit", "DOWN"), (0, 1))
        if wp.get("mode") == "step":
            starts.append((wp["x"] + dx, wp["y"] + dy))
        else:
            starts.append((wp["x"] + dx, wp["y"] + dy))
    if uru.get("spawn"):
        starts.append((uru["spawn"]["x"], uru["spawn"]["y"]))
    seen = set()
    q = deque(s for s in starts if 0 <= s[0] < w and 0 <= s[1] < h and s not in blocked)
    seen.update(q)
    while q:
        x, y = q.popleft()
        for dx, dy in step.values():
            nb = (x + dx, y + dy)
            if 0 <= nb[0] < w and 0 <= nb[1] < h and nb not in blocked and nb not in seen:
                seen.add(nb)
                q.append(nb)

    def touches(x, y):
        return any((x + dx, y + dy) in seen for dx, dy in step.values()) or (x, y) in seen

    problems = []
    for s in starts:
        if s not in seen:
            problems.append(f"entry tile {s} is blocked")
    for wp in uru["warps"]:
        if wp.get("mode") == "arrive":
            continue
        if not touches(wp["x"], wp["y"]):
            problems.append(f"warp {wp['id']} at ({wp['x']},{wp['y']}) unreachable")
    for n in uru["npcs"]:
        if not touches(n["x"], n["y"]):
            problems.append(f"npc {n['id']} at ({n['x']},{n['y']}) unreachable")
    for it in uru["items"]:
        if not touches(it["x"], it["y"]):
            problems.append(f"item {it['id']} at ({it['x']},{it['y']}) unreachable")
    for s in uru["signs"]:
        if not touches(s["x"], s["y"]):
            problems.append(f"sign at ({s['x']},{s['y']}) unreachable")
    for t in uru.get("interactables", []):
        if not touches(t["x"], t["y"]):
            problems.append(f"interactable at ({t['x']},{t['y']}) unreachable")
    # entries should all be in one connected region (maps split on purpose are listed in SPLIT_OK)
    comp = {}
    for s0 in starts:
        if s0 in comp or s0 in blocked or not (0 <= s0[0] < w and 0 <= s0[1] < h):
            continue
        cid = len(set(comp.values()))
        q2 = deque([s0])
        comp[s0] = cid
        while q2:
            x, y = q2.popleft()
            for dx, dy in step.values():
                nb = (x + dx, y + dy)
                if 0 <= nb[0] < w and 0 <= nb[1] < h and nb not in blocked and nb not in comp:
                    comp[nb] = cid
                    q2.append(nb)
    regions = {comp[s0] for s0 in starts if s0 in comp}
    if len(regions) > 1 and map_id not in SPLIT_OK:
        problems.append(f"entries fall into {len(regions)} disconnected regions")
    return problems, len(seen)


SPLIT_OK = {"nandi_hills"}  # lower slope and summit are joined only through the cave


def main():
    index = json.load(open(os.path.join(ROOT, "assets", "maps", "index.json")))
    total = 0
    for m in index:
        problems, n = check(m["id"])
        for p in problems:
            print(f"{m['id']}: {p}")
        total += len(problems)
    print(f"{len(index)} maps checked, {total} problems")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
