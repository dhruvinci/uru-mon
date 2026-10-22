"""Lalbagh (Arena 1, GRASS), the shared Darshini and Kirana interiors, and Cubbon Park."""
from dsl import Canvas, Props, room, warp, npc, trainer, say, enc
from expansion_scripts import gaala_ajja
from common import darshini, kirana, metro_staff

MAPS = [darshini(), kirana()]

# ---------------------------------------------------------------------------------------------
# Lalbagh
# ---------------------------------------------------------------------------------------------
W, H = 44, 40
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 3, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 3, H, "@").fill(W - 3, 0, 3, H, "@")
c.fill(21, 0, 2, 5, "Q").fill(21, H - 2, 2, 2, "Q")
# the Glass House plaza: symmetric beds, fountains, topiary
c.fill(14, 5, 15, 11, "Q").fill(20, 16, 4, 22, "Q").fill(3, 20, 38, 2, "Q")
for x, col in ((15, "#e0607a"), (16, "#f4c24f"), (27, "#a38acb"), (28, "#e98d3c")):
    pr.col("flower_bed", x, 6, 12, color=col)
pr.put("fountain", 16, 13).put("fountain", 26, 13).put("topiary", 18, 6).put("topiary", 25, 6)
pr.put("street_lamp", 19, 13).put("street_lamp", 24, 13)
# north-west lawns: the floral clock, topiary elephants, the bandstand
c.fill(4, 4, 9, 2, ",").fill(3, 9, 2, 6, '"')
pr.put("flower_clock", 8, 6).put("topiary_elephant", 4, 6).put("topiary_elephant", 11, 10).put("bandstand", 5, 11)
pr.put("jacaranda", 3, 3).put("jacaranda", 12, 3).put("bench", 9, 10).put("rain_tree", 9, 13)
pr.put("petals", 13, 6).put("petals", 4, 16).put("bush", 13, 13).put("wildflowers", 4, 15).put("bush", 3, 17)
# north-east: Lalbagh Rock with one of Kempegowda's towers
c.text(30, 3, """
  !!!!!!!
 !!!iiii!!
!!iiiiiiii!
!!iiiiiiii!
 !!iiiiii!!
  !!!SS!!!
   !!SS!!""")
c.blob(29, 11, 12, 9, '"', 4, only=".")
pr.put("watchtower", 34, 3).put("boulder", 28, 3).put("boulder", 38, 10).put("rock", 30, 11).put("rock", 40, 10)
pr.put("rock", 33, 12).put("tree_olive", 37, 14).put("jacaranda", 29, 16).put("bush", 35, 17)
# west: the shop row facing the promenade, the metro below it, a bamboo grove
c.fill(3, 28, 17, 3, "_").fill(3, 24, 8, 4, "_").fill(12, 22, 2, 6, ":")
pr.put("icecream_cart", 19, 17).put("bench", 14, 23).put("street_lamp", 3, 18).put("trash_bin", 10, 19)
pr.put("bamboo", 15, 32).put("bamboo", 17, 34).put("bamboo", 11, 34).put("bush", 3, 33).put("tree_dark", 3, 22)
c.blob(13, 31, 7, 7, '"', 5, only=".")
pr.put("coconut_cart", 14, 29).put("scooter_side", 3, 31).put("scooter_side", 12, 30, color="#4f86b0")
pr.put("tree", 16, 23).put("wildflowers", 18, 25).put("rock", 19, 27)
pr.put("banyan", 4, 32).put("jacaranda", 8, 31).put("bench", 7, 35).put("wildflowers", 10, 36).put("petals", 9, 33)
# south-east: Lalbagh Lake with a jetty, ghat steps, swan boats
c.blob(24, 22, 17, 15, ":", 6).blob(26, 24, 14, 12, "~", 7)
for x in range(27, 31):
    top = next(yy for yy in range(20, 34) if c.get(x, yy) == "~")
    c.set(x, top - 1, "D")
c.fill(32, 23, 1, 6, "B").fill(31, 29, 3, 1, "b")
pr.put("swan_boat", 35, 27).put("swan_boat", 28, 31).put("lotus", 37, 31).put("lotus", 29, 27).put("ducks", 35, 32)
pr.put("lily_pads", 27, 34).put("reeds", 25, 28).put("reeds", 39, 25).put("reeds", 38, 35).put("lily_pads", 37, 28)
c.blob(36, 35, 6, 3, '"', 8, only=".").blob(24, 35, 5, 3, '"', 9, only=".")
pr.put("rain_tree", 37, 21).put("tree", 24, 36).put("bench", 34, 22).put("street_lamp", 24, 22)

MAPS.append(dict(
    id="lalbagh", name="Lalbagh", music="MUSIC_TOWN", environment="park", metroStation="lalbagh",
    layout=c.layout(), props=pr, forestKinds=["tree", "jacaranda", "tree_dark", "tree", "gulmohar", "tree_olive"],
    buildings=[
        ("glass_house", 18, 8, {"door": dict(id="glass_house", to="glass_house", toId="door")}),
        ("darshini", 6, 17, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 11, 17, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("shop", 15, 17, {"w": 4, "sign": "BONSAI", "awning": "green"}),
        ("metro_station", 3, 24, {}),
    ],
    exits=[dict(side="S", **{"from": 21, "to_": 22}, map="route1"),
           dict(side="N", **{"from": 21, "to_": 22}, map="cubbon_park")],
    warps=[warp("metro", 8, 29, None, exit="UP", mode="arrive")],
    signs=[
        dict(x=24, y=15, text="LALBAGH BOTANICAL GARDEN - Home of the Glass House Arena. Leader: Hoovamma."),
        dict(x=31, y=10, text="LALBAGH ROCK - Over 3,000 million years old. Older than every Urumon. Probably."),
        dict(x=25, y=22, text="Please do not feed the lake Urumon. They have very specific diets."),
        dict(x=12, y=9, style="board", text="THE FLORAL CLOCK. Keeps perfect time, except when the gardeners are watering it."),
        dict(x=11, y=27, style="metro", text="NAMMA METRO - Lalbagh station. Green Line."),
    ],
    npcs=[
        metro_staff("metro_lb", 7, 28, "Lalbagh"),
        npc("crowd1", 21, 3, "woman3", facing="DOWN", hideIf={"badge": "GRASS"}, script=[
            say("The flower show crowd is HUGE today. Nobody's getting through until the show's over!",
                "...Unless you're an Arena champion, I suppose. They always get waved through.")]),
        npc("crowd2", 22, 3, "man3", facing="DOWN", hideIf={"badge": "GRASS"}, script=[
            say("I've been standing in this queue since morning to see the giant flower clock.")]),
        npc("lb_old", 24, 19, "ajja", facing="LEFT", script=[
            say("The jacarandas bloom purple every spring. The whole city turns into a painting.",
                "Some say a great guardian Urumon sleeps beneath the oldest tree in the city.")]),
        npc("lb_jog", 26, 36, "jogger", movement="WANDER", script=[
            say("Morning walkers own this garden before seven. After that it's the photographers.")]),
        npc("lb_kid", 38, 36, "kid2", movement="WANDER", wanderRadius=1, script=[
            say("I saw a Gulmo in the grass by the lake! It ran off when I sneezed.")]),
        gaala_ajja(32, 29, facing="DOWN"),
        npc("lb_gardener", 17, 7, "gardener", facing="LEFT", script=[
            say("Two hundred and forty flower beds, and Hoovamma knows if one petal is out of place.",
                "Don't step on the marigolds. They bite. ...No, they don't. But Hoovamma does.")]),
        npc("lb_photo", 10, 9, "college_m", facing="UP", script=[
            say("I'm doing a time-lapse of the floral clock. Twelve hours of footage. Very exciting. Very... slow.")]),
        npc("lb_icecream", 19, 19, "vendor", facing="DOWN", script=[
            say("Ice cream! Kulfi! Mango, pista, and 'chikoo surprise'. The surprise is that it's chikoo.")]),
        npc("lb_lover", 36, 23, "woman1", facing="DOWN", script=[
            say("We had our first date on this bench. He brought me a bonsai. It's still alive. He's on thin ice.")]),
    ],
    items=[dict(id="dosa1", x=38, y=7, item="Masala Dosa"), dict(id="coil1", x=19, y=36, item="Mosquito Coil")],
))

# ---------------------------------------------------------------------------------------------
# Glass House (Arena 1, GRASS)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 16, "o", exit_x=7, wall="lab")
c.fill(2, 4, 3, 2, "q").fill(10, 4, 3, 2, "q")
c.fill(1, 8, 5, 1, "h").fill(9, 8, 5, 1, "h")
c.fill(3, 11, 4, 1, "h").fill(8, 11, 4, 1, "h")
c.fill(6, 7, 3, 8, "Q").fill(1, 12, 5, 3, ".").fill(9, 12, 5, 3, ".").fill(1, 9, 5, 2, ",").fill(9, 9, 5, 2, ",")
MAPS.append(dict(
    id="glass_house", name="Glass House Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="stone_floor",
    props=[("potted_palm", 1, 2), ("potted_palm", 13, 2), ("fountain", 6, 5), ("plant_pot", 0, 14), ("plant_pot", 14, 14),
           ("banner", 3, 0, {"color": "#6aa65e"}), ("banner", 11, 0, {"color": "#6aa65e"}), ("banner", 7, 0, {"color": "#e0607a"}),
           ("banana", 0, 4), ("banana", 14, 4), ("bamboo", 0, 6), ("plant_big", 5, 2), ("plant_big", 9, 2),
           ("bush", 1, 13), ("bush", 13, 13), ("wildflowers", 2, 14), ("wildflowers", 11, 12), ("topiary", 5, 13),
           ("topiary", 9, 13), ("lily_pads", 6, 6), ("flower_bed", 13, 6, {"color": "#a38acb"}), ("flower_bed", 13, 7, {"color": "#f4c24f"})],
    warps=[warp("door", 7, 15, "lalbagh", "glass_house", exit="UP", dir="DOWN")],
    npcs=[
        trainer("gh_leader", 7, 3, "hoovamma", "leader_hoovamma", sight=0),
        trainer("gh_t1", 2, 9, "gardener", "lb_gardener", facing="RIGHT", sight=4),
        trainer("gh_t2", 12, 12, "college_f", "lb_college", facing="LEFT", sight=4),
        trainer("gh_t3", 12, 6, "gardener", "ar_glass1", facing="LEFT", sight=2),
        npc("gh_guide", 9, 14, "arena_guide", facing="LEFT", script=[
            say("Hey, future champ! Hoovamma loves GRASS Urumon.",
                "FIRE and SKY moves wilt them fast. BUG works too. Good luck!")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Cubbon Park
# ---------------------------------------------------------------------------------------------
W, H = 36, 50
c = Canvas(W, H, "@")
pr = Props()
# the trail through the old woods: south gate -> west loop -> centre -> east -> north gate
c.fill(15, 0, 2, 15, ":").fill(15, 13, 14, 2, ":").fill(27, 13, 2, 13, ":").fill(5, 24, 24, 2, ":")
c.fill(5, 24, 2, 16, ":").fill(5, 38, 14, 2, ":").fill(17, 38, 2, 12, ":")
# clearings
c.fill(6, 5, 8, 8, ".").fill(7, 6, 6, 6, "Q")                 # bandstand
c.fill(13, 8, 2, 5, ".").fill(17, 8, 2, 5, ".")                # verges of the north trail
c.fill(19, 2, 10, 10, ".").fill(23, 8, 3, 4, "Q")             # library lawn
c.fill(7, 16, 7, 8, '"').fill(6, 15, 9, 1, "d")                # west hollow
c.fill(19, 15, 3, 2, ".").fill(19, 17, 8, 7, '"')              # centre hollow
c.fill(29, 13, 4, 12, '"')                                     # east strip
c.fill(7, 27, 10, 10, ".").fill(11, 26, 3, 1, ".").fill(11, 27, 6, 2, '"').fill(11, 29, 6, 8, ",")
c.fill(20, 26, 2, 1, ".").fill(19, 27, 14, 11, ".").fill(20, 30, 4, 4, "Q")
c.blob(25, 29, 8, 8, "~", 3)
c.fill(19, 40, 1, 6, ".").fill(20, 40, 13, 6, '"')
c.fill(7, 40, 10, 6, "s")
# --- north-west: the bandstand clearing
pr.put("bandstand", 8, 7).put("bench", 7, 11).put("bench", 11, 11).put("lamp_post", 7, 6).put("lamp_post", 12, 6)
pr.put("leaves", 6, 12).put("leaves", 13, 6)
# --- the Syndicate's 'tree trimming' at the north gate
pr.put("crane", 19, 2).put("stump", 14, 9).put("stump", 17, 9).put("log", 17, 8)
pr.put("site_fence_h", 13, 8).put("cone", 13, 11).put("cone", 18, 11).put("barricade", 14, 11)
pr.put("rubble", 15, 4).put("leaves", 16, 3).put("leaves", 18, 10).put("stump", 20, 8)
# --- north-east: the red library in its lawn
pr.put("statue", 24, 9).put("flower_bed", 22, 10).put("flower_bed", 26, 10, color="#f4c24f").put("jacaranda", 19, 9)
pr.put("street_lamp", 22, 8).put("street_lamp", 26, 8).put("bench", 27, 2).put("petals", 21, 11).put("petals", 20, 10)
# --- the middle woods: big old trees in grassy hollows
pr.put("rain_tree", 9, 18).put("rain_tree", 22, 19).put("rock", 12, 22).put("mushrooms", 7, 23).put("stump", 31, 19)
# --- the west loop: bamboo grove and a wildflower meadow
pr.put("bamboo", 8, 27).put("bamboo", 8, 32).put("bamboo", 8, 34).put("bench", 13, 33).put("tree_dark", 15, 35)
pr.put("wildflowers", 12, 31).put("tree", 15, 30)
# --- east: the lotus pond and the statue plaza
pr.put("lotus", 27, 32).put("lotus", 29, 34).put("lily_pads", 26, 35).put("ducks", 28, 31).put("reeds", 24, 32)
pr.put("statue", 21, 30).put("bench", 20, 34).put("lamp_post", 23, 30).put("tree", 30, 27).put("bush", 19, 27)
pr.put("tree", 29, 41).put("rock", 24, 42).put("bush", 31, 44)
# --- south-west: the children's park
pr.put("swing_set", 7, 40).put("slide", 10, 40).put("seesaw", 7, 43).put("bench", 12, 44).put("icecream_cart", 14, 40)
pr.put("hopscotch", 10, 43)

MAPS.append(dict(
    id="cubbon_park", name="Cubbon Park", music="MUSIC_PARK", environment="park",
    layout=c.layout(), props=pr, forestKinds=["tree", "tree_dark", "tree", "mango", "tree_olive"],
    buildings=[("red_library", 21, 3, {})],
    exits=[dict(side="S", **{"from": 17, "to_": 18}, map="lalbagh"),
           dict(side="N", **{"from": 15, "to_": 16}, map="mg_road")],
    signs=[dict(x=19, y=44, text="CUBBON PARK - 300 acres of green in the heart of the city. Please keep it that way."),
           dict(x=12, y=9, text="THE BANDSTAND - Free concerts every Sunday morning. Urumon choir rehearsals on Tuesdays."),
           dict(x=20, y=8, text="STATE CENTRAL LIBRARY - Quiet, please. (The squirrels never listen.)"),
           dict(x=14, y=8, style="board", text="CONCRETE SYNDICATE - 'TREE TRIMMING' IN PROGRESS. Permit No. 0000001. (Totally genuine.)")],
    npcs=[
        trainer("t_cp_bird", 8, 30, "birdwatcher", "cp_bird", facing="LEFT", sight=4),
        trainer("t_cp_kid", 12, 27, "schoolboy", "cp_kid", facing="UP", sight=4),
        trainer("t_cp_jogger", 25, 20, "jogger", "cp_jogger", facing="RIGHT", sight=3),
        trainer("t_cp_college", 20, 16, "college_m", "cp_college", facing="UP", sight=4),
        trainer("t_grunt1", 15, 6, "grunt_m", "grunt_cubbon1", facing="DOWN", sight=3,
                hideIf={"defeated": "t_grunt1"},
                onDefeat=[{"npcWalk": {"id": "self", "steps": ["UP", "UP", "UP", "UP"], "ghost": True}}, {"npcHide": "self"}]),
        trainer("t_grunt2", 16, 6, "grunt_f", "grunt_cubbon2", facing="DOWN", sight=3,
                hideIf={"defeated": "t_grunt2"},
                onDefeat=[say("Retreat! Tell the Admin the park is guarded by a kid with a Dabba!"),
                          {"npcWalk": {"id": "self", "steps": ["UP", "UP", "UP", "UP"], "ghost": True}}, {"npcHide": "self"},
                          {"setFlag": "CUBBON_GRUNTS_DONE"}]),
        npc("cp_ranger", 17, 12, "park_ranger", facing="LEFT", script=[
            {"if": {"defeated": "t_grunt2"}, "then": [
                say("You chased off those Concrete Syndicate goons? Wonderful!",
                    "They had permits to 'trim' three trees. They brought a crane. A CRANE.", speaker="Park Ranger"),
            ], "else": [
                say("Some people in hard hats walked in with chainsaws this morning. Said they were 'developers'.",
                    "I'm just a park ranger... could you check on them, up by the north gate?", speaker="Park Ranger"),
            ]}]),
        npc("cp_bandsman", 9, 11, "ajja", facing="UP", script=[
            say("The police band plays here every Sunday. Same five songs since 1978. I know all the words.",
                "There are no words. I know them anyway.")]),
        npc("cp_reader", 25, 11, "college_f", facing="UP", script=[
            say("The library has a book on every Urumon ever recorded. Except the ones from the old cave up north.",
                "Nobody's been in there for years. Well. Nobody nice.")]),
        npc("cp_kid_play", 12, 42, "kid1", movement="WANDER", wanderRadius=1, script=[
            say("I went down the slide forty times. FORTY. Amma says one more and we go home. I'm never going home.")]),
        npc("cp_yoga", 22, 36, "woman1", facing="UP", script=[
            say("Laughter yoga. HA. HA. HA. HA.", "...It works. My Urumon thinks I've gone mad, but it works.")]),
    ],
    items=[dict(id="dabba1", x=16, y=45, item="Dabba", qty=3), dict(id="kaapi1", x=31, y=15, item="Filter Kaapi", qty=2),
           dict(id="neem1", x=7, y=16, item="Neem Paste"), dict(id="pak1", x=28, y=3, item="Mysore Pak")],
))

