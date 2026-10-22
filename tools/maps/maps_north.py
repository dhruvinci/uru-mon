"""Sankey Tank, Malleshwaram (Arena 4, MIND), Palace Road (Arena 5, SPIRIT), Hebbal and Nandi Hills (Arena 6, SKY)."""
from dsl import Canvas, Props, room, warp, npc, trainer, say, enc
from common import metro_staff
from expansion_scripts import mungaru, chali, moss_stone, shell_stone

MAPS = []

# ---------------------------------------------------------------------------------------------
# Route 5 - Sankey Tank
# ---------------------------------------------------------------------------------------------
W, H = 32, 46
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 3, H, "@").fill(W - 3, 0, 3, H, "@")
c.fill(12, 0, 2, 10, ":").fill(12, 36, 2, 10, ":")
# the walking track round the tank
c.fill(7, 10, 22, 2, ":").fill(7, 10, 2, 26, ":").fill(27, 10, 2, 26, ":").fill(7, 34, 22, 2, ":")
# the tank: stone embankments, ghat steps on the south bund, a boating jetty on the east side
c.fill(10, 13, 16, 19, "~").fill(11, 12, 14, 1, "~").fill(11, 32, 14, 1, "~")
c.fill(13, 33, 10, 1, "D").fill(23, 18, 4, 1, "b").fill(23, 17, 1, 3, "b")
# meadows
c.blob(3, 12, 4, 22, '"', 2, rough=0.4).blob(15, 3, 11, 6, '"', 3).blob(15, 37, 12, 6, '"', 4).blob(3, 37, 8, 6, '"', 5)
pr.put("rain_tree", 3, 12).put("rain_tree", 3, 20).put("rain_tree", 3, 28).put("rain_tree", 26, 2).put("jacaranda", 3, 2)
pr.put("mantapa", 4, 5).put("bench", 9, 8).put("lamp_post", 6, 9).put("lamp_post", 25, 8).put("lamp_post", 9, 36)
pr.put("lamp_post", 26, 36).put("bench", 16, 36).put("bench", 19, 8)
pr.put("swan_boat", 18, 15).put("swan_boat", 14, 26).put("ducks", 21, 23).put("ducks", 12, 17).put("lotus", 22, 29)
pr.put("lily_pads", 11, 28).put("lotus", 19, 13).put("reeds", 9, 12).put("reeds", 26, 31).put("boat", 24, 20)
pr.put("petals", 4, 4).put("leaves", 8, 33).put("leaves", 27, 9).put("wildflowers", 11, 41).put("rock", 22, 40)
pr.put("tree", 27, 40).put("tree_dark", 3, 40)

MAPS.append(dict(
    id="sankey_tank", name="Route 5 - Sankey Tank", music="MUSIC_ROUTE", environment="lake",
    layout=c.layout(), props=pr, waterBank="stone", forestKinds=["tree", "jacaranda", "tree_dark", "tree"],
    exits=[dict(side="S", **{"from": 12, "to_": 13}, map="mg_road"),
           dict(side="N", **{"from": 12, "to_": 13}, map="malleshwaram")],
    signs=[dict(x=14, y=40, text="SANKEY TANK - Built in 1882 to bring water to the city. Ducks: welcome. Foam: not welcome."),
           dict(x=11, y=8, text="NORTH: Malleshwaram. Famous for jasmine, silk sarees and the strictest tuition teacher in town."),
           dict(x=24, y=33, style="stone", text="Built by Colonel Sankey in 1882 to water the cantonment. Now waters the ducks.")],
    npcs=[
        trainer("t_sk_ajja", 6, 28, "ajja", "sk_ajja", facing="RIGHT", sight=3),
        trainer("t_sk_ajji", 6, 16, "ajji", "sk_ajji", facing="RIGHT", sight=3),
        trainer("t_sk_bird", 14, 6, "birdwatcher", "sk_bird", facing="LEFT", sight=4),
        npc("sk_walker", 20, 38, "woman1", movement="WANDER", script=[
            say("Every evening I walk three rounds of the tank. The Kappe here sing louder than the temple bells.")]),
        npc("sk_boatman", 28, 18, "man2", facing="LEFT", script=[
            say("Boating is closed today. The ducks are on strike. They want more puffed rice.")]),
        npc("sk_yoga", 17, 34, "woman3", facing="UP", script=[
            say("Sunrise yoga on the ghat steps. Breathe in... breathe out... ignore the man shouting into his phone.")]),
        npc("sk_swimmer", 22, 10, "man1", facing="DOWN", script=[
            say("There's a swimming pool just past the tank. Real water. No ducks. Very disappointing.")]),
    ],
    items=[dict(id="bath1", x=24, y=39, item="Bisi Bele Bath"), dict(id="elaneer1", x=4, y=10, item="Elaneer"),
           dict(id="tdabba1", x=24, y=4, item="Steel Dabba", qty=3)],
))

# ---------------------------------------------------------------------------------------------
# Malleshwaram
# ---------------------------------------------------------------------------------------------
W, H = 44, 36
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# Margosa Road (east-west, out to Palace Road) and Sampige Road (south to Sankey Tank)
c.fill(2, 14, 42, 2, "=").fill(2, 13, 38, 1, "p").fill(2, 16, 38, 1, "p").fill(40, 13, 4, 1, "@").fill(40, 16, 4, 1, "@")
c.fill(18, 16, 2, 20, "=").fill(17, 17, 1, 17, "p").fill(20, 17, 1, 17, "p").fill(17, 14, 1, 2, "z").fill(20, 14, 1, 2, "z")
# north-west: the stepped temple tank (kalyani) beside the old temple and its courtyard
c.fill(3, 3, 9, 9, "D").fill(5, 5, 5, 5, "~").fill(12, 3, 8, 10, "Q")
pr.put("lotus", 6, 6).put("lily_pads", 8, 8).put("coconut_palm", 12, 3).put("tree_katte", 12, 8).put("rangoli_big", 15, 8)
pr.put("lamp_stand", 18, 9).put("flower_stall", 18, 12).put("shrine", 19, 3)
# north-east: an old tiled house, and Vidya's tuition house in its walled yard
c.fill(24, 7, 1, 6, "Q").fill(34, 8, 1, 4, "Q")
pr.put("coconut_palm", 21, 8).put("banana", 26, 8).put("rangoli", 24, 7).put("clothes_line", 21, 11).put("scooter_side", 26, 11)
pr.box(29, 3, 38, 12, gates={(34, 12)})
pr.put("coconut_palm", 30, 4).put("coconut_palm", 37, 4).put("tulasi_katte", 32, 9).put("rangoli", 34, 8)
pr.put("flower_bed", 30, 10).put("flower_bed", 31, 10, color="#f4c24f").put("flower_bed", 37, 10).put("bench_stone", 35, 10)
pr.put("dog", 41, 8).put("garbage_pile", 39, 11).put("leaves", 40, 6)
# poles along Margosa Road
for x in (3, 11, 22, 28):
    pr.put("electric_pole", x, 12)
pr.put("auto_side", 6, 14).put("car_side", 26, 15, color="#f1ead8").put("scooter_side", 33, 14).put("pothole", 13, 15)
pr.put("cow", 36, 15).put("manhole", 23, 14)
# south-west: the metro station, the darshini and shops of 8th Cross, the market lane, old houses
c.fill(2, 21, 15, 2, "_").fill(3, 17, 8, 4, "_").fill(2, 27, 15, 2, "p").fill(2, 32, 15, 2, "e")
pr.put("scooter_side", 12, 21).put("scooter_side", 13, 21, color="#4f86b0").put("coconut_cart", 14, 22).put("trash_bin", 2, 22)
pr.put("flower_stall", 7, 27).put("flower_stall", 8, 27).put("veg_cart", 11, 28).put("flower_stall", 15, 28)
pr.put("rangoli", 5, 32).put("rangoli", 12, 32, color="#7fb8e0").put("tulasi_katte", 8, 32).put("cow", 14, 33)
# south-east: the flower shop, lanes of old houses, a playground gone to grass
c.fill(21, 20, 11, 2, "e").fill(21, 25, 21, 2, "e").fill(21, 32, 6, 2, "e")
c.blob(32, 17, 10, 8, '"', 6, only=".").blob(28, 27, 14, 7, '"', 7, only=".")
pr.put("swing_set", 33, 17).put("slide", 37, 21).put("tree", 39, 17).put("rock", 34, 23).put("jacaranda", 28, 27)
pr.put("petals", 30, 29).put("tree_dark", 39, 30).put("coconut_palm", 21, 27).put("plant_pot", 27, 22)

MAPS.append(dict(
    id="malleshwaram", name="Malleshwaram", music="MUSIC_TOWN", environment="city", metroStation="malleshwaram",
    layout=c.layout(), props=pr, wires=[[(3, 12), (11, 12), (22, 12), (28, 12)]],
    forestKinds=["tree", "mango", "tree_dark", "jacaranda"],
    buildings=[
        ("tutor_house", 31, 4, {"door": dict(id="tutor_house", to="tutor_house", toId="door")}),
        ("temple", 13, 3, {}),
        ("old_house", 21, 3, {"w": 6, "h": 4, "wall": "#f2e6c8"}),
        ("metro_station", 3, 17, {}),
        ("darshini", 3, 24, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 7, 24, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("shop", 11, 24, {"w": 4, "sign": "SILKS", "awning": "pink"}),
        ("old_house", 3, 29, {"w": 5, "wall": "#e9c7c0", "shutters": "#4f86b0"}),
        ("old_house", 10, 29, {"w": 5, "wall": "#cfe0e6"}),
        ("shop", 21, 17, {"w": 4, "sign": "FLOWERS", "awning": "yellow"}),
        ("old_house", 26, 17, {"w": 5, "wall": "#f2d98c"}),
        ("old_house", 21, 22, {"w": 5, "wall": "#e6dcc4", "shutters": "#c96b5a"}),
        ("old_house", 27, 22, {"w": 5, "wall": "#d6e6cf"}),
        ("apartment", 22, 27, {"w": 5, "h": 5, "wall": "#f1e2c4", "accent": "#a38acb"}),
    ],
    exits=[dict(side="S", **{"from": 18, "to_": 19}, map="sankey_tank"),
           dict(side="E", **{"from": 14, "to_": 15}, map="palace_road")],
    warps=[warp("metro", 8, 22, None, exit="UP", mode="arrive")],
    signs=[dict(x=20, y=11, text="8TH CROSS, MALLESHWARAM - Jasmine, silks, filter coffee. Arena of Leader Vidya: Room 2, upstairs. (It's the whole house.)"),
           dict(x=12, y=12, text="KADU MALLESHWARA TEMPLE - Old as the hills. Quiet, please."),
           dict(x=33, y=11, style="board", text="VIDYA'S TUITION CENTRE. Classes 1 to 10. MIND-type coaching. No chappals inside."),
           dict(x=11, y=22, style="metro", text="NAMMA METRO - Sampige Road station. Green Line.")],
    npcs=[
        metro_staff("metro_ml", 7, 21, "Malleshwaram"),
        npc("ml_guard", 40, 14, "area_boi", facing="LEFT", hideIf={"badge": "MIND"}, script=[
            say("Boss, road closed. Film shooting is going on. Only Arena champions get through, that's the rule.",
                "Vidya ma'am's tuition house is right here. Pass her test first, then come.", speaker="Area Boi")]),
        npc("ml_guard2", 40, 15, "area_boi2", facing="LEFT", hideIf={"badge": "MIND"}, script=[
            say("Which film? Can't tell, guru. ...Okay fine, it's a ghost movie. Don't tell anyone, scene aagutte.",
                speaker="Area Boi")]),
        npc("ml_flower", 22, 20, "woman4", facing="UP", script=[
            say("Mallige! Fresh mallige! A string of jasmine for your hair? For your Urumon's hair?")]),
        npc("ml_student", 21, 16, "schoolgirl", movement="WANDER", wanderRadius=1, script=[
            say("Vidya ma'am gives surprise tests. On Sundays. During festivals.")]),
        trainer("t_ml_college", 31, 20, "college_f", "ml_college", facing="LEFT", sight=4),
        trainer("t_ml_kid", 26, 25, "schoolboy", "ml_kid", facing="UP", sight=3),
        npc("ml_priest", 16, 10, "man4", facing="DOWN", script=[
            say("Water flows into this kalyani from a stone Nandi's mouth, and nobody knows where it starts.",
                "It was buried for centuries. Someone dug it up in 1997. The Nandi didn't seem surprised.")]),
        npc("ml_coffee", 4, 27, "ajja", facing="RIGHT", script=[
            say("Fifty years I've had my morning dosa at this darshini. Same table. Well. Same spot. There are no tables.")]),
        npc("ml_tutor_kid", 33, 13, "schoolboy", facing="UP", script=[
            say("Tuition starts at 6 AM. I've been here since 5:45. Fear is a great alarm clock.")]),
    ],
    items=[dict(id="chakli1", x=36, y=28, item="Chakli"), dict(id="mudde1", x=40, y=3, item="Ragi Mudde")],
))

c, walls = room(13, 13, "x", exit_x=6, wall="blue")
MAPS.append(dict(
    id="tutor_house", name="Vidya's Tuition House", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="red_oxide",
    props=[("desk", 1, 4), ("desk", 4, 4), ("desk", 8, 4), ("desk", 10, 4), ("desk", 1, 7), ("desk", 4, 7), ("desk", 8, 7),
           ("desk", 10, 7), ("bookshelf", 0, 2), ("bookshelf", 12, 2), ("plant_pot", 0, 11),
           ("blackboard", 5, 0), ("wall_clock", 9, 0), ("calendar", 2, 0), ("photo_frame", 3, 1), ("photo_frame", 10, 1),
           ("poster", 11, 0, {"color": "#a38acb"}), ("tube_light", 8, 0),
           ("chair", 2, 5), ("chair", 5, 5), ("chair", 9, 5), ("chair", 11, 5), ("chair", 2, 8), ("chair", 5, 8),
           ("chair", 9, 8), ("chair", 11, 8), ("slippers", 5, 11), ("slippers", 7, 11), ("oonjal", 1, 9),
           ("pooja_shelf", 12, 4), ("plant_pot", 12, 11)],
    warps=[warp("door", 6, 12, "malleshwaram", "tutor_house", exit="UP", dir="DOWN")],
    npcs=[
        trainer("th_leader", 6, 2, "vidya", "leader_vidya", sight=0),
        trainer("th_t1", 3, 6, "schoolboy", "ar_tuition1", facing="RIGHT", sight=3),
        trainer("th_t2", 9, 9, "college_f", "ar_tuition2", facing="LEFT", sight=3),
        npc("th_guide", 8, 11, "schoolboy", facing="LEFT", script=[
            say("Psst! Vidya ma'am's Urumon are MIND types.",
                "BUG and SPIRIT moves are super effective against them. And FIGHT moves barely tickle them.")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Palace Road
# ---------------------------------------------------------------------------------------------
W, H = 44, 36
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# the avenue north to Hebbal, and Palace Road
c.fill(19, 0, 2, 14, "Q").fill(0, 14, 42, 2, "=").fill(0, 14, 42, 1, "-").fill(2, 13, 40, 1, "p").fill(2, 16, 40, 1, "p")
c.fill(19, 13, 2, 1, "Q")
pr.put("hedge", 18, 2).put("hedge", 21, 2).put("rain_tree", 16, 3).put("rain_tree", 21, 3).put("rain_tree", 16, 8)
pr.put("rain_tree", 21, 8).put("street_lamp", 18, 11).put("street_lamp", 23, 11).put("petals", 23, 7).put("leaves", 18, 6)
# north-west: the long lawns, gone wild
c.blob(3, 3, 11, 9, '"', 1, only=".")
pr.put("banyan", 3, 2).put("rock", 12, 4).put("tree", 13, 9).put("bush", 6, 11).put("stump", 9, 12)
# north-east: the palace grounds where the concerts happen
c.fill(25, 3, 9, 7, "e").blob(34, 6, 8, 7, '"', 2, only=".").fill(33, 9, 8, 4, "_")
pr.put("bandstand", 28, 3).put("tea_stall", 25, 6).put("icecream_cart", 33, 7).put("bench", 26, 9).put("bench", 31, 9)
pr.put("hoarding", 36, 2, text="EXPO TODAY", color="#a38acb").put("trash_bin", 24, 9).put("garbage_pile", 34, 4)
# traffic on Palace Road
pr.put("auto_side", 6, 15).put("car_side", 11, 14, color="#f1ead8").put("scooter_side", 28, 15).put("car_side", 34, 14, color="#2f2b36")
pr.put("pothole", 15, 15).put("manhole", 37, 15)
# the palace in its walled grounds: a long drive, a forecourt, the royal elephants
pr.box(6, 17, 36, 33, gates={(12, 17), (13, 17)})
c.fill(12, 18, 2, 9, "Q").fill(10, 26, 21, 6, "Q").fill(26, 18, 10, 7, "e")
c.blob(7, 18, 5, 15, '"', 3, only=".").blob(27, 27, 9, 6, '"', 4, only=".")
pr.put("fountain", 19, 28).put("statue", 17, 26).put("statue", 23, 26).put("lamp_post", 14, 26).put("lamp_post", 26, 26)
pr.row("flower_bed", 15, 18, 30, color="#e0607a").row("flower_bed", 22, 25, 30, color="#a38acb").put("topiary", 11, 29)
pr.put("topiary", 29, 26).put("car_side", 26, 30, color="#f1ead8").put("coconut_palm", 14, 19).put("coconut_palm", 25, 19)
pr.put("elephant", 27, 19).put("elephant", 32, 21).put("haystack", 34, 18).put("haystack", 30, 18).put("rubble", 28, 23)
# outside the walls: an avenue of trees on either side
pr.put("tree_dark", 2, 18).put("tree", 2, 23).put("tree_olive", 2, 28).put("tree", 38, 18).put("tree_dark", 38, 23)
pr.put("tree", 38, 30).put("wildflowers", 4, 31).put("leaves", 40, 27)

RIVAL4_SCRIPT = [
    {"exclaim": "rohan_pr"},
    {"npcToPlayer": "rohan_pr"},
    {"battle": {"trainer": "rival_palace", "id": "rohan_pr"}},
    say("Grandma called. Something big is happening at Nandi Hills at sunrise.",
        "The Syndicate's boss is going after the Garden City's guardian - Udyanaga.",
        "Go through Hebbal and climb the hill. The only way to the summit is through the old cave. Hurry!", speaker="Sudeep"),
    {"npcWalk": {"id": "rohan_pr", "steps": ["UP", "UP", "UP", "UP", "UP", "UP", "UP", "UP"], "ghost": True}},
    {"npcHide": "rohan_pr"},
    {"setFlag": "RIVAL4_DONE"},
]
MAPS.append(dict(
    id="palace_road", name="Palace Road", music="MUSIC_ROUTE", environment="park", metroStation="palace_road",
    layout=c.layout(), props=pr,
    buildings=[("palace", 16, 20, {"door": dict(id="palace", to="palace", toId="door")}),
               ("metro_station", 33, 9, {})],
    warps=[warp("metro", 37, 14, None, exit="UP", mode="arrive")],
    exits=[dict(side="W", **{"from": 14, "to_": 15}, map="malleshwaram"),
           dict(side="N", **{"from": 19, "to_": 20}, map="hebbal")],
    signs=[dict(x=17, y=13, text="BANGALORE PALACE - Built to look like a castle in England. Now home to a spirited Arena. Literally."),
           dict(x=22, y=2, text="NORTH: Hebbal and the road to Nandi Hills.")],
    npcs=[
        trainer("t_pr_cricketer", 15, 11, "cricketer", "pr_cricketer", facing="RIGHT", sight=4),
        trainer("t_pr_dancer", 24, 6, "dancer", "pr_dancer", facing="LEFT", sight=4),
        npc("pr_mahout", 30, 23, "man2", facing="LEFT", script=[
            say("I look after the palace elephants. Aanemari love a bath in the afternoon.",
                "In the old days they carried golden howdahs in the autumn procession.")]),
        npc("pr_guard", 19, 2, "area_boi", facing="DOWN", hideIf={"badge": "SPIRIT"}, script=[
            say("No going north, macha. The palace ghosts are full active these days. Even our gang won't ride past at night.",
                "Win at the palace Arena and calm them down. Then we'll move our bikes.", speaker="Area Boi")]),
        npc("pr_guard2", 20, 2, "area_boi2", facing="DOWN", hideIf={"badge": "SPIRIT"}, script=[
            say("Last night someone laughed in the palace corridor. Nobody was there.",
                "I'm not scared, okay? I'm just... standing here. Guarding.", speaker="Area Boi")]),
        npc("rohan_pr", 21, 7, "rival", facing="DOWN", showIf={"badge": "SPIRIT"}, hideIf="RIVAL4_DONE", script=[]),
        metro_staff("metro_pr", 36, 13, "Palace Road"),
        npc("pr_gatekeeper", 14, 18, "officer", facing="DOWN", script=[
            say("Welcome to the palace grounds. Photography allowed. Ghost photography, extra charge.", speaker="Gatekeeper")]),
        npc("pr_concert", 30, 8, "college_m", facing="UP", script=[
            say("Last week a rock band played here. This week, a carnatic concert. Next week, a wedding expo.",
                "Same stage. Very confused acoustics.")]),
    ],
    triggers=[dict(id="rival4", once=False, x=19, y=9, w=2, h=4, requires={"badge": "SPIRIT"}, unless="RIVAL4_DONE",
                   script=RIVAL4_SCRIPT),
              # the lawns let you walk round the avenue, so Sudeep also waits at the north gate
              dict(id="rival4_gate", once=False, x=19, y=3, w=2, h=1, requires={"badge": "SPIRIT"}, unless="RIVAL4_DONE",
                   script=RIVAL4_SCRIPT)],
    items=[dict(id="pak1", x=7, y=5, item="Mysore Pak", qty=2), dict(id="tiffin1", x=39, y=27, item="Tiffin Carrier")],
))

c, walls = room(17, 15, "o", exit_x=8, wall="palace")
c.fill(2, 4, 1, 8, "c").fill(14, 4, 1, 8, "c").fill(7, 3, 3, 11, "c")
MAPS.append(dict(
    id="palace", name="Bangalore Palace Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="stone_floor",
    props=[("statue", 4, 3), ("statue", 12, 3), ("statue", 4, 9), ("statue", 12, 9), ("pooja_shelf", 1, 2),
           ("pooja_shelf", 15, 2), ("plant_pot", 0, 13), ("plant_pot", 16, 13), ("sofa", 1, 6), ("sofa", 14, 6),
           ("throne", 8, 0), ("photo_frame", 3, 0), ("photo_frame", 13, 0), ("banner", 5, 0, {"color": "#a38acb"}),
           ("banner", 11, 0, {"color": "#a38acb"}), ("armor_stand", 0, 3), ("armor_stand", 16, 3), ("lamp_stand", 0, 9),
           ("lamp_stand", 16, 9), ("vase", 3, 12), ("vase", 13, 12), ("vase", 6, 2),
           ("mist", 2, 10), ("mist", 12, 4), ("wall_clock", 1, 0), ("photo_frame", 15, 1)],
    warps=[warp("door", 8, 14, "palace_road", "palace", exit="UP", dir="DOWN")],
    npcs=[
        trainer("pa_leader", 8, 2, "rukmini", "leader_rukmini", sight=0),
        trainer("pa_t1", 6, 10, "dancer", "ar_palace1", facing="RIGHT", sight=3),
        trainer("pa_t2", 10, 6, "ajja", "ar_palace2", facing="LEFT", sight=3),
        npc("pa_guide", 10, 13, "arena_guide", facing="LEFT", script=[
            say("Rukmini commands SPIRIT Urumon. NORMAL and FIGHT moves pass right through them!",
                "Use SPIRIT moves of your own. Or a very brave heart.")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Route 7 - Hebbal
# ---------------------------------------------------------------------------------------------
W, H = 36, 48
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# the highway: north towards the airport and Nandi Hills, bending south-east towards the palace
c.fill(12, 0, 2, 2, "=").fill(12, 2, 4, 25, "=").fill(11, 2, 1, 25, "p").fill(16, 2, 1, 24, "p")
c.fill(12, 26, 10, 4, "=").fill(18, 30, 4, 18, "=").fill(17, 30, 1, 16, "p").fill(22, 26, 1, 20, "p")
c.fill(11, 27, 1, 4, "p").fill(12, 30, 5, 1, "p").fill(19, 46, 2, 2, "=")
# Hebbal lake: pelicans and painted storks nest on the island trees
c.blob(2, 4, 9, 27, "~", 3, rough=0.12).fill(10, 6, 1, 20, "~").blob(4, 10, 4, 4, ".", 1, rough=0.0)
c.fill(7, 22, 4, 1, "b")
pr.put("nest_tree", 4, 9).put("pelican", 6, 13).put("stork", 5, 13).put("lily_pads", 3, 26).put("lotus", 7, 18)
pr.put("ducks", 5, 6).put("reeds", 10, 4).put("reeds", 10, 27).put("lotus", 3, 20).put("boat", 4, 24)
# the flyover strides over everything
for x in range(2, 34):
    pr.put("flyover_deck_h", x, 16)
    if x > 10:
        pr.put("deck_shadow", x, 18)
for x in (8, 19, 26, 31):
    pr.put("flyover_pillar", x, 16)
# north-east: a wild meadow, the bus stop and a tea stall for drivers heading north
c.blob(18, 3, 15, 11, '"', 2, only=".")
pr.put("bus_stop", 17, 2).put("tea_stall", 18, 10).put("coconut_cart", 20, 13).put("tree", 31, 2).put("rock", 27, 6)
pr.put("street_lamp", 17, 6).put("milestone", 17, 14).put("eucalyptus", 32, 9)
# traffic
pr.put("bus_side", 12, 5, color="#c8443a").put("car_side", 14, 11, color="#f1ead8").put("auto_side", 12, 20)
pr.put("car_side", 15, 27, color="#4f86b0").put("scooter_side", 19, 28).put("car_side", 18, 35, color="#2f2b36")
pr.put("auto_side", 20, 40).put("pothole", 13, 23).put("manhole", 20, 33)
# east of the bend: apartments with a lake view (and a flyover view)
c.fill(23, 19, 11, 6, ".")
pr.put("tree_dark", 32, 21).put("garbage_pile", 23, 24).put("dog", 30, 24).put("coconut_palm", 30, 19)
pr.put("scooter_side", 24, 24).put("scooter_side", 25, 24, color="#4f86b0").put("wildflowers", 31, 23).put("electric_pole", 29, 22)
# south-west: tall grass and the old garadi mane wrestling pit
c.blob(2, 31, 14, 13, '"', 4, only=".").fill(11, 33, 5, 4, "e")
pr.put("stump", 2, 32).put("tree", 7, 41).put("bench_stone", 11, 37).put("rock", 15, 40).put("tree_olive", 2, 41)
# south-east: the auto stand and the way back to the palace
c.fill(23, 30, 11, 14, ".").blob(26, 32, 8, 10, '"', 5, only=".")
pr.put("auto_side", 23, 31).put("auto_side", 23, 33).put("auto_side", 23, 35).put("bus_stop", 24, 41).put("tree", 31, 30)
pr.put("street_lamp", 23, 37).put("rock", 30, 43).put("tea_stall", 27, 29).put("wildflowers", 32, 42).put("tree_olive", 32, 36)

MAPS.append(dict(
    id="hebbal", name="Route 7 - Hebbal", music="MUSIC_ROUTE", environment="lake",
    layout=c.layout(), props=pr,
    buildings=[("apartment", 24, 19, {"w": 5, "h": 5, "wall": "#dfe6ea", "accent": "#5d9b6a"})],
    exits=[dict(side="S", **{"from": 19, "to_": 20}, map="palace_road"),
           dict(side="N", **{"from": 12, "to_": 13}, map="nandi_hills")],
    signs=[dict(x=23, y=44, text="HEBBAL FLYOVER - The gateway to the north. Nandi Hills: 50 km."),
           dict(x=11, y=31, text="HEBBAL LAKE - Pelicans, painted storks, and occasionally a very confused Meenaga.")],
    npcs=[
        trainer("t_hb_rider", 22, 27, "delivery_rider", "hb_rider", facing="LEFT", sight=4),
        trainer("t_hb_wrestler", 13, 33, "wrestler", "hb_wrestler", facing="DOWN", sight=3),
        trainer("t_hb_fisher", 11, 21, "fisher", "hb_fisher", facing="LEFT", sight=2),
        npc("hb_walker", 17, 4, "man3", facing="DOWN", script=[
            say("I saw trucks with hard-hat people heading up to Nandi Hills before dawn.", "Hope they're just tourists...")]),
        npc("hb_birder", 11, 12, "birdwatcher", facing="LEFT", script=[
            say("Spot-billed pelicans! Painted storks! They fly all the way from Kokkare Bellur to fish here.",
                "The storks nest on village rooftops out there. The villagers think they bring good luck.")]),
        npc("hb_autodriver", 24, 34, "auto_driver", facing="LEFT", script=[
            say("Airport? Two thousand. Nandi Hills? Three thousand. Palace? ...Walk, saar. It's right there.")]),
    ],
    interactables=[mungaru(6, 22)],
    items=[dict(id="mudde1", x=3, y=38, item="Ragi Mudde"), dict(id="dosa1", x=23, y=5, item="Masala Dosa", qty=3)],
))

# ---------------------------------------------------------------------------------------------
# Nandi Hills (lower slope + summit, linked only through the cave)
# ---------------------------------------------------------------------------------------------
W, H = 36, 48
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# ---- the summit ----
# Tipu's Drop: a granite edge with nothing beyond it but the plains and the morning mist
c.fill(34, 2, 2, 14, "#").fill(28, 2, 6, 4, "Q")
# stone paths: the pavilion plaza, down to the old walk along the summit, round to the viewpoint
c.fill(13, 7, 8, 2, "Q").fill(16, 9, 2, 6, "Q").fill(4, 15, 23, 2, "Q").fill(26, 4, 2, 13, "Q").fill(4, 15, 2, 5, "Q")
# the summit's outer fort wall above the cliffs, and older battlements to the west
c.fill(9, 20, 25, 1, "W").fill(2, 13, 11, 1, "W")
c.fill(2, 2, 7, 4, "@").blob(2, 6, 10, 7, '"', 1, only=".").blob(19, 9, 7, 5, '"', 2, only=".").blob(28, 6, 6, 8, '"', 3, only=".")
# the way down into the cave: a hole in the rock
c.fill(3, 19, 5, 3, "#").set(5, 19, "Q").set(5, 20, "S")
# the cliff band splitting the hill
c.fill(0, 22, W, 3, "#")
pr.put("binoculars", 31, 6).put("binoculars", 29, 6).put("mist", 31, 6).put("mist", 27, 9)
for y in range(2, 6):
    pr.put("railing_v", 34, y)
pr.put("lamp_post", 13, 7).put("lamp_post", 20, 7).put("shrine", 24, 6).put("lamp_stand", 22, 7).put("monkey", 21, 6)
pr.put("boulder", 30, 11).put("rock", 33, 8).put("eucalyptus", 10, 2).put("eucalyptus", 12, 2).put("eucalyptus", 22, 2)
pr.put("eucalyptus", 24, 2).put("eucalyptus", 9, 17).put("eucalyptus", 15, 17).put("eucalyptus", 29, 17).put("rock", 21, 18)
pr.put("mist", 18, 17).put("monkey", 12, 20).put("monkey", 25, 20).put("bench_stone", 22, 14)
pr.put("wildflowers", 9, 15).put("wildflowers", 30, 15).put("rock", 31, 18).put("boulder", 31, 16)
pr.put("wildflowers", 14, 11).put("grass_tuft", 23, 16).put("grass_tuft", 7, 18).put("bench_stone", 13, 12)
# ---- the lower slope ----
# the hairpin hill road up from Hebbal, through the old fort gate, to the mouth of the cave
c.fill(12, 38, 2, 10, "=").fill(12, 38, 14, 2, "=").fill(24, 30, 2, 10, "=").fill(8, 30, 18, 2, "=").fill(8, 27, 2, 5, "=")
c.fill(2, 43, 9, 1, "W").fill(14, 43, 20, 1, "W")
c.blob(2, 32, 9, 9, '"', 4, only=".").blob(15, 32, 8, 5, '"', 5, only=".").blob(27, 26, 7, 15, '"', 6, only=".")
c.blob(14, 44, 20, 2, '"', 7, only=".")
pr.put("fort_arch", 11, 41).put("monkey", 5, 43).put("monkey", 20, 43).put("monkey", 29, 43)
pr.put("boulder_big", 2, 26).put("boulder", 18, 26).put("rock", 14, 28).put("rock", 30, 37).put("boulder", 31, 31)
pr.put("eucalyptus", 6, 27).put("eucalyptus", 11, 33).put("eucalyptus", 22, 33).put("eucalyptus", 27, 41)
pr.put("eucalyptus", 2, 44).put("eucalyptus", 9, 44).put("milestone", 14, 40)

MAPS.append(dict(
    id="nandi_hills", name="Nandi Hills", music="MUSIC_CAVE", environment="hill", cliffGround="granite",
    layout=c.layout(), props=pr, forestKinds=["tree_olive", "tree", "tree_dark"], forestFillers=["eucalyptus", "ashoka"],
    buildings=[("cave_entrance", 7, 25, {"door": dict(id="cave_s", to="nandi_cave", toId="south")}),
               ("hill_pavilion", 14, 3, {"door": dict(id="pavilion", to="hill_pavilion", toId="door")})],
    exits=[dict(side="S", **{"from": 12, "to_": 13}, map="hebbal")],
    warps=[warp("cave_n", 5, 20, "nandi_cave", "north", exit="UP", mode="step")],
    signs=[dict(x=14, y=44, text="NANDI HILLS - 1,478 m. Sunrise point at the summit. Please carry your own water."),
           dict(x=30, y=7, text="TIPU'S DROP - A sheer cliff with a view over the whole Deccan plateau."),
           dict(x=10, y=28, text="OLD CAVE - The only path to the summit since the landslide. Bring a torch."),
           dict(x=12, y=14, style="stone", text="THE OLD FORT. These walls kept armies out for three hundred years. Monkeys: not so much.")],
    npcs=[
        trainer("t_nh_bird", 16, 36, "birdwatcher", "nh_bird", facing="DOWN", sight=4),
        trainer("t_nh_wrestler", 25, 29, "wrestler", "nh_wrestler", facing="DOWN", sight=3),
        npc("nh_monkey_man", 6, 40, "man4", facing="RIGHT", script=[
            say("A Mangaa stole my sunglasses. Then it came back for my sandwich. Then my dignity.")]),
        npc("nh_prof", 18, 14, "professor", facing="DOWN", showIf="NANDI_DONE", hideIf="UDYANAGA_SEEN", script=[
            say("{PLAYER}! You did it! Bhaskar's crew is scattering down the hill.",
                "Look - the mist at Tipu's Drop is glowing. The guardian is waking up.",
                "Go to the viewpoint. Udyanaga only shows itself to those who protect the city.", speaker="Prof. Sharada")]),
        npc("nh_sunrise", 32, 3, "college_f", facing="RIGHT", script=[
            say("I drove up at 4 AM for the sunrise. It's 6:30. All I can see is fog.", "...Best morning of my life, honestly.")]),
        npc("nh_vendor", 23, 9, "vendor", facing="DOWN", script=[
            say("Hot corn, roasted peanuts, chai! Keep your snacks hidden, the monkeys have no manners.")]),
    ],
    triggers=[dict(id="udyanaga", x=27, y=2, w=7, h=4, once=False, requires="NANDI_DONE", unless="UDYANAGA_DONE", script=[
        {"setFlag": "UDYANAGA_SEEN"},
        {"cutscene": True},
        say("The morning mist pours over the cliff... and something enormous rises out of it."),
        say("Petals of purple and red swirl in the wind. A dragon made of an entire garden looks straight at you."),
        {"cutscene": False},
        {"battle": {"wild": {"species": 64, "level": 45}, "music": "MUSIC_LEGEND", "environment": "hill"},
         "onWin": [{"setFlag": "UDYANAGA_DONE"},
                   {"if": {"caught": 64}, "then": [say("The guardian of the Garden City has chosen to travel with you.")],
                    "else": [say("Udyanaga let out a gentle roar and vanished into the mist. The city's trees seem a little greener.")]}],
         "onLose": []},
    ])],
    interactables=[chali(34, 4)],
    items=[dict(id="mudde1", x=33, y=41, item="Ragi Mudde"), dict(id="pak1", x=4, y=8, item="Mysore Pak", qty=2),
           dict(id="tiffin1", x=33, y=12, item="Tiffin Carrier", qty=2)],
))

W, H = 30, 26
c = Canvas(W, H, "#")
c.fill(14, 21, 2, 4, "v")          # south entry
c.fill(4, 19, 22, 3, "v")
c.fill(4, 10, 3, 10, "v")
c.fill(4, 9, 14, 3, "v")
c.fill(16, 12, 3, 8, "v")
c.fill(19, 15, 7, 3, "v")
c.fill(23, 3, 3, 13, "v")
c.fill(8, 3, 16, 3, "v")
c.fill(8, 1, 1, 3, "v")            # north exit corridor, one tile wide
c.fill(9, 13, 5, 4, "v")
c.fill(11, 12, 1, 1, "v")          # doorway into the inner chamber
# side pockets: a mossy hollow off the west passage, a dripping grotto with a pool off the east one
c.fill(1, 13, 3, 3, "v").fill(26, 5, 3, 3, "v").fill(26, 8, 3, 3, "~").fill(19, 19, 4, 1, "v").fill(20, 22, 4, 2, "v")
c.fill(2, 20, 2, 2, "v").fill(21, 6, 2, 1, "v").fill(12, 6, 3, 1, "v")
pr = Props()
pr.put("stalagmite", 4, 21).put("stalagmite", 25, 21).put("stalagmite", 6, 10).put("stalagmite", 17, 9)
pr.put("stalagmite", 25, 15).put("stalagmite", 9, 16).put("stalagmite", 1, 15).put("stalagmite", 28, 5)
pr.put("cave_rock", 18, 18).put("cave_rock", 22, 23).put("cave_rock", 13, 13).put("cave_rock", 2, 21)
pr.put("puddle", 6, 20).put("puddle", 24, 12).put("rubble", 15, 20).put("rubble", 20, 4).put("mushrooms", 2, 14)
pr.put("mushrooms", 27, 6).put("rubble", 12, 6).put("puddle", 10, 10)
# the Syndicate's digging gear near the way out
pr.put("crate", 11, 4).put("crate", 12, 4).put("crate", 20, 19).put("lantern", 9, 3).put("lantern", 20, 3)
pr.put("lantern", 15, 19).put("drum_barrel", 14, 3, color="#6f8a3a").put("pipe_stack", 17, 3).put("cement_bags", 19, 5)
# carvings on the old walls
pr.put("carving", 7, 4).put("carving", 22, 2, motif="elephant").put("carving", 10, 12, motif="naga").put("carving", 3, 18)
MAPS.append(dict(
    id="nandi_cave", name="Nandi Cave", music="MUSIC_CAVE", environment="cave", interior=True,
    layout=c.layout(), props=pr, ground="cave_floor", caveEncounters=True, cliffGround="cave_floor",
    waterBank="cave", waterStyle="dark",
    warps=[warp("south", 14, 25, "nandi_hills", "cave_s", exit="UP", dir="DOWN"),
           warp("north", 8, 0, "nandi_hills", "cave_n", exit="DOWN", dir="UP")],
    npcs=[
        trainer("t_nc_grunt1", 10, 19, "grunt_m", "grunt_nandi1", facing="RIGHT", sight=4),
        trainer("t_nc_grunt2", 5, 13, "grunt_f", "grunt_nandi2", facing="DOWN", sight=4),
        trainer("t_nc_grunt3", 24, 9, "grunt_m", "grunt_nandi3", facing="DOWN", sight=4),
        trainer("t_nc_boss", 8, 2, "bhaskar", "boss_bhaskar", facing="DOWN", sight=2, hideIf="NANDI_DONE",
                onDefeat=[say("Pack up the cranes! We're leaving! This city isn't worth it!", speaker="Bhaskar"),
                          {"npcWalk": {"id": "self", "steps": ["UP", "UP"], "ghost": True}}, {"npcHide": "self"},
                          {"setFlag": "NANDI_DONE"},
                          say("The Syndicate's equipment rumbles away down the far side of the hill. The path to the summit is clear!")]),
    ],
    interactables=[
        dict(x=7, y=4, script=[say("An old carving of a seated Nandi, worn smooth by centuries of bats and pilgrims.")]),
        dict(x=22, y=2, script=[say("A carved elephant with a garland. Someone has added a moustache in chalk. Recently.")]),
        dict(x=10, y=12, script=[say("A coiled naga carved over the doorway. Its eyes seem to follow your torch.")]),
        dict(x=3, y=18, script=[say("Faded marks: a sun, a lake, and a long-tailed creature. The rock here feels warm.")]),
    ],
    items=[dict(id="elaneer1", x=13, y=15, item="Elaneer", qty=2), dict(id="bath1", x=25, y=4, item="Bisi Bele Bath", qty=2),
           moss_stone(1, 13), shell_stone(28, 7)],
))

c, walls = room(13, 13, "i", exit_x=6, wall="temple")
c.fill(5, 3, 3, 9, "Q")
MAPS.append(dict(
    id="hill_pavilion", name="Hill Pavilion Arena", music="MUSIC_ARENA", interior=True, environment="hill",
    layout=c.layout(), walls=walls, ground="rock_floor",
    props=[("statue", 2, 3), ("statue", 10, 3), ("plant_pot", 0, 11), ("plant_pot", 12, 11), ("rock", 3, 8), ("rock", 9, 8),
           ("pillar", 0, 4), ("pillar", 12, 4), ("pillar", 0, 7), ("pillar", 12, 7), ("banner", 3, 0, {"color": "#7fb8e0"}),
           ("banner", 9, 0, {"color": "#7fb8e0"}), ("banner", 6, 0, {"color": "#f1e7ce"}), ("mist", 1, 9), ("mist", 8, 5),
           ("bush_tall", 12, 9), ("wildflowers", 2, 10), ("wildflowers", 10, 11),
           ("binoculars", 1, 2), ("binoculars", 11, 2)],
    warps=[warp("door", 6, 12, "nandi_hills", "pavilion", exit="UP", dir="DOWN")],
    npcs=[
        trainer("hp_leader", 6, 2, "akash", "leader_akash", sight=0),
        trainer("hp_t1", 2, 6, "birdwatcher", "ar_pavilion1", facing="RIGHT", sight=3),
        trainer("hp_t2", 10, 9, "jogger", "ar_pavilion2", facing="LEFT", sight=3),
        npc("hp_guide", 8, 11, "arena_guide", facing="LEFT", script=[
            say("Akash flies SKY Urumon. ELECTRIC and ROCK moves will bring them down to earth!")]),
    ],
))
