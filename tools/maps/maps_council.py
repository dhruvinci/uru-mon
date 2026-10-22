"""Vidhana Soudha and the Namma Council: four councillors, then the Champion."""
from dsl import Canvas, Props, room, warp, npc, trainer, say
from expansion_scripts import gandaberunda

MAPS = []

COUNCIL_IDS = ["vs_nagaraj", "vs_basappa", "vs_kaveri", "vs_agni", "vs_champion"]

# ---------------------------------------------------------------------------------------------
# Vidhana Soudha grounds
# ---------------------------------------------------------------------------------------------
W, H = 40, 32
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# Ambedkar Veedhi runs east to MG Road; a polished granite approach climbs to the doors
c.fill(2, 16, 38, 2, "=").fill(2, 15, 36, 1, "p").fill(2, 18, 36, 1, "p").fill(17, 11, 5, 4, "C").fill(17, 15, 5, 1, "C")
# formal lawns either side of the approach
c.fill(2, 2, 11, 13, ",").fill(26, 2, 12, 13, ",").fill(3, 3, 9, 11, ".").fill(27, 3, 10, 11, ".")
c.fill(13, 11, 4, 4, ".").fill(22, 11, 4, 4, ".")
pr.put("fountain", 6, 5).put("fountain", 31, 5).put("jacaranda", 10, 3).put("jacaranda", 3, 3).put("jacaranda", 27, 3).put("jacaranda", 34, 3).put("bench", 5, 7).put("bench", 30, 7)
for x in range(4, 11, 2):
    pr.put("flower_bed", x, 9, color="#f4c24f").put("flower_bed", x, 12, color="#e0607a")
for x in range(28, 36, 2):
    pr.put("flower_bed", x, 9, color="#f4c24f").put("flower_bed", x, 12, color="#e0607a")
pr.put("lamp_post", 16, 12).put("lamp_post", 22, 12).put("topiary", 14, 13).put("topiary", 24, 13)
pr.put("security_booth", 13, 11).put("hedge", 3, 14).put("hedge", 11, 14).put("hedge", 27, 14).put("hedge", 36, 14)
# the avenue: an official car, a police jeep, barricades
pr.put("car_side", 7, 16, color="#f1ead8").put("jeep_side", 28, 17).put("barricade", 34, 16).put("barricade", 35, 17)
pr.put("street_lamp", 4, 18).put("street_lamp", 12, 18).put("street_lamp", 27, 18).put("street_lamp", 35, 18)
# across the road: the red High Court, a garden with a statue, the darshini
c.fill(18, 19, 3, 11, "Q").fill(14, 19, 11, 2, "Q").fill(5, 26, 7, 3, "_")
pr.put("statue", 19, 21).put("fountain", 15, 24).put("fountain", 22, 24).put("bench", 14, 27).put("bench", 23, 27)
pr.put("rain_tree", 26, 25).put("jacaranda", 2, 25).put("tree", 13, 21).put("flower_bed", 16, 21).put("flower_bed", 22, 21)
pr.put("lamp_post", 17, 22).put("lamp_post", 21, 22).put("tree_dark", 34, 25).put("petals", 3, 28).put("bench", 35, 28)

MAPS.append(dict(
    id="vidhana_soudha", name="Vidhana Soudha", music="MUSIC_CITY", environment="city",
    layout=c.layout(), props=pr,
    buildings=[("vidhana_soudha", 13, 3, {"door": dict(id="council", to="council_1", toId="door")}),
               ("red_library", 5, 21, {}),
               ("darshini", 30, 21, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)})],
    exits=[dict(side="E", **{"from": 16, "to_": 17}, map="mg_road")],
    signs=[dict(x=22, y=14, text="VIDHANA SOUDHA - Seat of the Namma Council. 'Government's work is God's work.'"),
           dict(x=12, y=26, style="stone", text="ATTARA KACHERI - The old red court of eighteen offices. Still arguing, after all these years.")],
    npcs=[
        npc("vs_guard", 16, 11, "officer", facing="DOWN", script=[
            say("Beyond these doors wait the four councillors of the Namma Council, and the Champion.",
                "Once you go in, there's no walking out until you win - or lose.", speaker="Guard")]),
        npc("vs_prof", 24, 18, "professor", facing="LEFT", script=[
            {"if": "CHAMPION_DONE", "then": [
                say("Champion {PLAYER}! The lakes are clearing, the trees are growing back. And it started with you.",
                    "Go anywhere. Catch everything. The city is yours to explore.", speaker="Prof. Sharada")],
             "else": [
                say("{PLAYER}! Six badges! Sudeep is already inside, you know. He left about an hour ago.",
                    "Rest at the Darshini first. The Council doesn't hold back.", speaker="Prof. Sharada")]}]),
        npc("vs_tourist", 23, 12, "college_m", facing="UP", script=[
            say("Every evening they light up the whole building. I've taken four hundred photos. They're all the same photo.")]),
        npc("vs_guard2", 21, 11, "officer", facing="DOWN", script=[
            say("Those two-headed birds carved over the doors? The Gandaberunda. Old royal emblem.",
                "Some nights I could swear one of the heads turns to look at me.", speaker="Guard")]),
        npc("vs_lawyer", 9, 27, "man3", facing="UP", script=[
            say("My case has been in that court for twenty-two years. Next hearing: next month. It's always next month.")]),
    ],
    # every tile you step out onto from the Council doors
    triggers=[gandaberunda(18, 11), gandaberunda(20, 11)],
))

# ---------------------------------------------------------------------------------------------
# Council rooms
# ---------------------------------------------------------------------------------------------
ROOMS = [
    ("council_1", "Nagaraj's Chamber", "c", "toxic", "vs_nagaraj", "nagaraj", "council_nagaraj"),
    ("council_2", "Basappa's Chamber", "i", "cave", "vs_basappa", "basappa", "council_basappa"),
    ("council_3", "Kaveri's Chamber", "V", "water", "vs_kaveri", "kaveri", "council_kaveri"),
    ("council_4", "Agni's Chamber", "c", "fire", "vs_agni", "agni", "council_agni"),
]
THEME_PROPS = {
    "council_1": [("drum_barrel", 1, 5, {"color": "#6f8a3a"}), ("drum_barrel", 11, 5, {"color": "#6f8a3a"}),
                  ("drum_barrel", 1, 6, {"color": "#8fae6a"}), ("drum_barrel", 11, 7, {"color": "#6f8a3a"}),
                  ("safety_poster", 3, 0), ("safety_poster", 9, 0), ("valve_wheel", 1, 1), ("valve_wheel", 11, 1),
                  ("oil_stain", 3, 8), ("oil_stain", 9, 6), ("mushrooms", 2, 9), ("mushrooms", 10, 9)],
    "council_2": [("boulder", 0, 5), ("boulder", 11, 5), ("rock", 3, 7), ("rock", 9, 8), ("stalagmite", 1, 8),
                  ("stalagmite", 11, 8), ("carving", 3, 1), ("carving", 9, 1, {"motif": "elephant"}), ("rubble", 4, 9),
                  ("pebbles", 8, 6), ("cave_rock", 2, 9)],
    "council_3": [("lotus", 2, 6), ("lotus", 10, 7), ("ducks", 1, 8), ("lily_pads", 11, 5), ("plant_big", 4, 9),
                  ("plant_big", 8, 9), ("banner", 3, 0, {"color": "#7fb8e0"}), ("banner", 9, 0, {"color": "#7fb8e0"})],
    "council_4": [("brazier", 1, 5), ("brazier", 11, 5), ("brazier", 1, 8), ("brazier", 11, 8), ("lamp_stand", 3, 2),
                  ("lamp_stand", 9, 2), ("banner", 5, 0, {"color": "#d9534f"}), ("banner", 7, 0, {"color": "#d9534f"}),
                  ("rug_long", 5, 7, {"color": "#a63d33"})],
}
for i, (mid, name, floor, wall, npc_id, sprite, tid) in enumerate(ROOMS):
    c, walls = room(13, 12, floor, exit_x=6, wall=wall)
    if mid == "council_3":
        c.fill(1, 5, 3, 4, "~").fill(9, 5, 3, 4, "~")
    if mid == "council_4":
        c.fill(5, 4, 3, 7, "x")
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
        layout=c.layout(), walls=walls,
        ground={"c": "carpet", "i": "rock_floor", "V": "mosaic"}[floor],
        waterBank="stone",
        props=[("statue", 2, 3), ("statue", 10, 3), ("plant_pot", 0, 10), ("plant_pot", 12, 10)] + THEME_PROPS[mid],
        warps=warps,
        npcs=[trainer(npc_id, 6, 3, sprite, tid, sight=0)],
        onEnter=on_enter,
        block=[(6, 11)] if i > 0 else [],
    ))

c, walls = room(15, 14, "c", exit_x=7, wall="palace")
c.fill(0, 2, 3, 11, "A").fill(12, 2, 3, 11, "A")
MAPS.append(dict(
    id="champion_room", name="Champion's Hall", music="MUSIC_COUNCIL", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="carpet",
    props=[("statue", 2, 3), ("statue", 12, 3), ("statue", 2, 9), ("statue", 12, 9), ("pooja_shelf", 7, 2),
           ("banner", 3, 0, {"color": "#d6b04c"}), ("banner", 11, 0, {"color": "#d6b04c"}), ("trophy_shelf", 6, 0),
           ("photo_frame", 1, 0), ("photo_frame", 13, 0), ("lamp_stand", 0, 5), ("lamp_stand", 14, 5),
           ("lamp_stand", 0, 10), ("lamp_stand", 14, 10), ("vase", 4, 2), ("vase", 10, 2), ("armor_stand", 1, 6),
           ("armor_stand", 13, 6)],
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
