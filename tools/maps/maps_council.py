"""Vidhana Soudha and the Namma Council: four councillors, then the Champion."""
from dsl import Canvas, room, warp, npc, trainer, say

MAPS = []

COUNCIL_IDS = ["vs_nagaraj", "vs_basappa", "vs_kaveri", "vs_agni", "vs_champion"]

# ---------------------------------------------------------------------------------------------
# Vidhana Soudha grounds
# ---------------------------------------------------------------------------------------------
W, H = 36, 30
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"E": [(16, 17)]})
c.fill(0, 16, 36, 2, "_")
c.fill(16, 12, 4, 6, "_")
c.fill(3, 19, 30, 8, ",")
c.fill(15, 19, 6, 8, "_")
for x in range(4, 33, 4):
    c.set(x, 13, "q").set(x, 14, "q")
MAPS.append(dict(
    id="vidhana_soudha", name="Vidhana Soudha", music="MUSIC_CITY", environment="city",
    layout=c.layout(),
    buildings=[("vidhana_soudha", 11, 3, {"door": dict(id="council", to="council_1", toId="door")}),
               ("darshini", 27, 21, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)})],
    props=[("fountain", 8, 22), ("fountain", 26, 18), ("lamp_post", 14, 20), ("lamp_post", 21, 20)],
    exits=[dict(side="E", **{"from": 16, "to_": 17}, map="mg_road")],
    signs=[dict(x=20, y=12, text="VIDHANA SOUDHA - Seat of the Namma Council. 'Government's work is God's work.'")],
    npcs=[
        npc("vs_guard", 15, 12, "officer", facing="DOWN", script=[
            say("Beyond these doors wait the four councillors of the Namma Council, and the Champion.",
                "Once you go in, there's no walking out until you win - or lose.", speaker="Guard")]),
        npc("vs_prof", 23, 17, "professor", facing="LEFT", script=[
            {"if": "CHAMPION_DONE", "then": [
                say("Champion {PLAYER}! The lakes are clearing, the trees are growing back. And it started with you.",
                    "Go anywhere. Catch everything. The city is yours to explore.", speaker="Prof. Sharada")],
             "else": [
                say("{PLAYER}! Six badges! Sudeep is already inside, you know. He left about an hour ago.",
                    "Rest at the Darshini first. The Council doesn't hold back.", speaker="Prof. Sharada")]}]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Council rooms
# ---------------------------------------------------------------------------------------------
ROOMS = [
    ("council_1", "Nagaraj's Chamber", "c", "plain", "vs_nagaraj", "nagaraj", "council_nagaraj"),
    ("council_2", "Basappa's Chamber", "o", "cave", "vs_basappa", "basappa", "council_basappa"),
    ("council_3", "Kaveri's Chamber", "t", "lab", "vs_kaveri", "kaveri", "council_kaveri"),
    ("council_4", "Agni's Chamber", "c", "palace", "vs_agni", "agni", "council_agni"),
]
for i, (mid, name, floor, wall, npc_id, sprite, tid) in enumerate(ROOMS):
    c, walls = room(13, 12, floor, exit_x=6, wall=wall)
    nxt = ROOMS[i + 1][0] if i + 1 < len(ROOMS) else "champion_room"
    warps = [warp("next", 6, 1, nxt, "door", exit="DOWN", dir="UP",
                  requires={"defeated": npc_id}, lockedText="The door is sealed. Defeat the councillor first.")]
    if i == 0:
        warps.append(warp("door", 6, 11, "vidhana_soudha", "council", exit="UP", dir="DOWN"))
    else:
        warps.append(warp("door", 6, 11, None, exit="UP", mode="arrive"))
    on_enter = [{"resetTrainers": COUNCIL_IDS}] if i == 0 else None
    MAPS.append(dict(
        id=mid, name=name, music="MUSIC_COUNCIL", interior=True, environment="arena",
        layout=c.layout(), walls=walls, ground={"c": "carpet", "o": "stone_floor", "t": "tile_floor"}[floor],
        props=[("statue", 2, 3), ("statue", 10, 3), ("plant_pot", 0, 10), ("plant_pot", 12, 10)],
        warps=warps,
        npcs=[trainer(npc_id, 6, 3, sprite, tid, sight=0)],
        onEnter=on_enter,
        block=[(6, 11)] if i > 0 else [],
    ))

c, walls = room(15, 14, "c", exit_x=7, wall="palace")
MAPS.append(dict(
    id="champion_room", name="Champion's Hall", music="MUSIC_COUNCIL", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="carpet",
    props=[("statue", 2, 3), ("statue", 12, 3), ("statue", 2, 9), ("statue", 12, 9), ("pooja_shelf", 7, 2)],
    warps=[warp("door", 7, 13, None, exit="UP", mode="arrive")],
    block=[(7, 13)],
    npcs=[trainer("vs_champion", 7, 4, "rival", "champion", sight=0,
                  onDefeat=[
                      {"setFlag": "CHAMPION_DONE"},
                      {"npcShow": dict(id="hall_prof", x=6, y=11, sprite="professor", facing="UP", movement="IDLE")},
                      {"npcWalk": {"id": "hall_prof", "steps": ["UP", "UP", "UP", "UP", "UP"]}},
                      say("{PLAYER}! Sudeep! I watched the whole thing from the gallery.",
                          "{PLAYER}, you are the new Champion of the Namma Council.",
                          "You didn't just win battles. You stopped the Syndicate, cleaned up Bellandur, and woke the guardian of the Garden City.",
                          "Sudeep, you were magnificent too. Your grandfather would be proud of both of you.", speaker="Prof. Sharada"),
                      say("Yeah, yeah. Next year I'm taking that title back, {PLAYER}. Just you wait.", speaker="Sudeep"),
                      say("Come. Let's record your team in the Hall of Fame.", speaker="Prof. Sharada"),
                      {"heal": True},
                      {"setLocation": {"area": "player_house_1f", "x": 3, "y": 5, "dir": "UP"}},
                      {"credits": True},
                  ])],
))
