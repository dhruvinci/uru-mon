"""Lalbagh (Arena 1, GRASS), the shared Darshini and Kirana interiors, and Cubbon Park."""
from dsl import Canvas, room, warp, npc, trainer, say, enc
from common import darshini, kirana, metro_staff

MAPS = [darshini(), kirana()]

# ---------------------------------------------------------------------------------------------
# Lalbagh
# ---------------------------------------------------------------------------------------------
W, H = 38, 32
c = Canvas(W, H, ".")
c.tree_border("J", gaps={"N": [(17, 18)], "S": [(17, 18)]})
c.fill(17, 0, 2, 32, "_")              # central promenade, north to south
c.fill(3, 14, 32, 2, "_")              # east-west promenade
c.fill(18, 9, 1, 5, ":")               # glass house approach
c.fill(8, 20, 1, 1, ":")               # darshini path
c.fill(13, 20, 1, 2, ":")              # kirana path
c.fill(3, 21, 14, 2, "_")              # shop street
# flower beds around the Glass House
for x in list(range(12, 15)) + list(range(22, 25)):
    for y in (5, 7, 9, 11):
        c.set(x, y, "q")
# Lalbagh lake (east)
c.fill(24, 18, 10, 7, "~")
c.fill(25, 17, 8, 1, "~")
c.fill(25, 25, 8, 1, "~")
c.fill(22, 26, 12, 3, '"')             # meadow by the lake
# Lalbagh Rock (west)
c.set(3, 3, "O").set(6, 4, "O").set(4, 6, "O").set(8, 3, "r").set(9, 6, "r").set(3, 9, "r")
c.set(28, 3, "G").set(31, 6, "G").set(26, 9, "J").set(31, 10, "J")
c.text(9, 25, """
,,,,
,,,,""")
MAPS.append(dict(
    id="lalbagh", name="Lalbagh", music="MUSIC_TOWN", environment="park", metroStation="lalbagh",
    layout=c.layout(),
    buildings=[
        ("glass_house", 15, 4, {"door": dict(id="glass_house", to="glass_house", toId="door")}),
        ("darshini", 6, 17, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 11, 17, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("metro_station", 3, 24, {}),
    ],
    exits=[dict(side="S", **{"from": 17, "to_": 18}, map="route1"),
           dict(side="N", **{"from": 17, "to_": 18}, map="cubbon_park")],
    warps=[warp("metro", 8, 29, None, exit="UP", mode="arrive")],
    signs=[
        dict(x=16, y=12, text="LALBAGH BOTANICAL GARDEN - Home of the Glass House Arena. Leader: Hoovamma."),
        dict(x=10, y=13, text="LALBAGH ROCK - Over 3,000 million years old. Older than every Urumon. Probably."),
        dict(x=23, y=16, text="Please do not feed the lake Urumon. They have very specific diets."),
    ],
    npcs=[
        metro_staff("metro_lb", 7, 28, "Lalbagh"),
        npc("crowd1", 17, 2, "woman3", facing="DOWN", hideIf={"badge": "GRASS"}, script=[
            say("The flower show crowd is HUGE today. Nobody's getting through until the show's over!",
                "...Unless you're an Arena champion, I suppose. They always get waved through.")]),
        npc("crowd2", 18, 2, "man3", facing="DOWN", hideIf={"badge": "GRASS"}, script=[
            say("I've been standing in this queue since morning to see the giant flower clock.")]),
        npc("lb_old", 21, 16, "ajja", facing="LEFT", script=[
            say("The jacarandas bloom purple every spring. The whole city turns into a painting.",
                "Some say a great guardian Urumon sleeps beneath the oldest tree in the city.")]),
        npc("lb_jog", 10, 15, "jogger", movement="WANDER", script=[
            say("Morning walkers own this garden before seven. After that it's the photographers.")]),
        npc("lb_kid", 27, 27, "kid2", movement="WANDER", script=[
            say("I saw a Gulmo in the grass by the lake! It ran off when I sneezed.")]),
    ],
    items=[dict(id="dosa1", x=34, y=4, item="Masala Dosa"), dict(id="coil1", x=3, y=28, item="Mosquito Coil")],
    encounters={"grass": enc(0.12, (54, 5, 7, 25), (52, 5, 7, 20), (15, 4, 6, 20), (10, 5, 7, 20), (22, 5, 6, 15))},
))

# ---------------------------------------------------------------------------------------------
# Glass House (Arena 1, GRASS)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 16, "o", exit_x=7, wall="lab")
c.fill(2, 4, 3, 2, "q").fill(10, 4, 3, 2, "q")
c.fill(1, 8, 5, 1, "h").fill(9, 8, 5, 1, "h")
c.fill(3, 11, 4, 1, "h").fill(8, 11, 4, 1, "h")
MAPS.append(dict(
    id="glass_house", name="Glass House Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="stone_floor",
    props=[("plant_pot", 1, 2), ("plant_pot", 13, 2), ("fountain", 6, 5), ("plant_pot", 0, 14), ("plant_pot", 14, 14)],
    warps=[warp("door", 7, 15, "lalbagh", "glass_house", exit="UP", dir="DOWN")],
    npcs=[
        trainer("gh_leader", 7, 3, "hoovamma", "leader_hoovamma", sight=0),
        trainer("gh_t1", 2, 9, "gardener", "lb_gardener", facing="RIGHT", sight=4),
        trainer("gh_t2", 12, 12, "college_f", "lb_college", facing="LEFT", sight=4),
        npc("gh_guide", 9, 14, "man1", facing="LEFT", script=[
            say("Hey, future champ! Hoovamma loves GRASS Urumon.",
                "FIRE and SKY moves wilt them fast. BUG works too. Good luck!")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Cubbon Park
# ---------------------------------------------------------------------------------------------
W, H = 32, 48
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(17, 18)], "N": [(15, 16)]})
# winding trail: south entrance -> west loop -> centre -> east -> north exit
c.fill(17, 38, 2, 10, ":")
c.fill(5, 38, 14, 2, ":")
c.fill(5, 26, 2, 14, ":")
c.fill(5, 26, 22, 2, ":")
c.fill(25, 14, 2, 14, ":")
c.fill(15, 14, 12, 2, ":")
c.fill(15, 0, 2, 16, ":")
# tree blocks forming the maze
c.trees(8, 30, 8, 6)
c.trees(20, 30, 8, 8)
c.trees(2, 18, 8, 6)
c.trees(12, 18, 10, 6)
c.trees(2, 4, 10, 8)
c.trees(19, 4, 10, 8)
# grass patches
c.fill(9, 40, 6, 4, '"')
c.fill(21, 40, 6, 4, '"')
c.fill(8, 28, 12, 2, '"')
c.fill(27, 18, 3, 8, '"')
c.fill(3, 13, 10, 3, '"')
# bandstand clearing
c.fill(12, 8, 6, 4, "_")
MAPS.append(dict(
    id="cubbon_park", name="Cubbon Park", music="MUSIC_PARK", environment="park",
    layout=c.layout(),
    exits=[dict(side="S", **{"from": 17, "to_": 18}, map="lalbagh"),
           dict(side="N", **{"from": 15, "to_": 16}, map="mg_road")],
    signs=[dict(x=19, y=45, text="CUBBON PARK - 300 acres of green in the heart of the city. Please keep it that way."),
           dict(x=18, y=10, text="THE BANDSTAND - Free concerts every Sunday morning. Urumon choir rehearsals on Tuesdays.")],
    props=[("bench", 12, 10), ("bench", 17, 10), ("statue", 13, 8), ("lamp_post", 11, 12), ("lamp_post", 18, 12)],
    npcs=[
        trainer("t_cp_bird", 7, 33, "birdwatcher", "cp_bird", facing="DOWN", sight=4),
        trainer("t_cp_kid", 24, 28, "schoolboy", "cp_kid", facing="LEFT", sight=4),
        trainer("t_cp_jogger", 26, 22, "jogger", "cp_jogger", facing="DOWN", sight=3),
        trainer("t_cp_college", 20, 16, "college_m", "cp_college", facing="LEFT", sight=4),
        trainer("t_grunt1", 15, 6, "grunt_m", "grunt_cubbon1", facing="DOWN", sight=3,
                hideIf={"defeated": "t_grunt1"},
                onDefeat=[{"npcWalk": {"id": "self", "steps": ["UP", "UP", "UP", "UP"], "ghost": True}}, {"npcHide": "self"}]),
        trainer("t_grunt2", 16, 6, "grunt_f", "grunt_cubbon2", facing="DOWN", sight=3,
                hideIf={"defeated": "t_grunt2"},
                onDefeat=[say("Retreat! Tell the Admin the park is guarded by a kid with a Dabba!"),
                          {"npcWalk": {"id": "self", "steps": ["UP", "UP", "UP", "UP"], "ghost": True}}, {"npcHide": "self"},
                          {"setFlag": "CUBBON_GRUNTS_DONE"}]),
        npc("cp_ranger", 13, 13, "officer", facing="RIGHT", script=[
            {"if": {"defeated": "t_grunt2"}, "then": [
                say("You chased off those Concrete Syndicate goons? Wonderful!",
                    "They had permits to 'trim' three trees. They brought a crane. A CRANE.", speaker="Park Ranger"),
            ], "else": [
                say("Some people in hard hats walked in with chainsaws this morning. Said they were 'developers'.",
                    "I'm just a park ranger... could you check on them, up by the north gate?", speaker="Park Ranger"),
            ]}]),
    ],
    items=[dict(id="dabba1", x=3, y=42, item="Dabba", qty=3), dict(id="kaapi1", x=28, y=16, item="Filter Kaapi", qty=2),
           dict(id="neem1", x=4, y=13, item="Neem Paste"), dict(id="pak1", x=27, y=3, item="Mysore Pak")],
    encounters={"grass": enc(0.13, (15, 6, 9, 22), (18, 6, 9, 14), (13, 6, 9, 14), (52, 7, 9, 10), (10, 6, 8, 10),
                             (32, 7, 9, 10), (34, 7, 9, 10), (16, 8, 10, 6), (36, 8, 9, 4))},
))
