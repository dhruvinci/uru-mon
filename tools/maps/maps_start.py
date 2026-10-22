"""Basavanagudi: the player's home town, the lab, and Route 1 (South End Road)."""
from dsl import Canvas, Props, room, warp, npc, trainer, say, enc
from common import metro_staff
from expansion_scripts import bendakaalu, revival_machine

MAPS = []

# ---------------------------------------------------------------------------------------------
# Player's house
# ---------------------------------------------------------------------------------------------
c, walls = room(9, 8, "w", wall="blue")
c.set(8, 2, "S")
MAPS.append(dict(
    id="player_house_2f", name="Your Room", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="wood_floor",
    props=[("bed", 1, 2), ("desk", 4, 2), ("tv", 6, 2), ("bookshelf", 7, 5), ("rug", 3, 4), ("plant_pot", 1, 6),
           ("wall_window", 2, 0), ("poster", 4, 0, {"color": "#d9534f"}), ("poster", 5, 0, {"color": "#4f86b0"}),
           ("wall_clock", 7, 0), ("calendar", 0, 0), ("tube_light", 3, 0), ("chair", 4, 3), ("almirah", 0, 4),
           ("bean_bag", 5, 6, {"color": "#7fbf62"}), ("crate", 8, 3), ("slippers", 2, 5)],
    warps=[warp("stairs", 8, 2, "player_house_1f", "stairs", exit="LEFT", mode="step")],
    unblock=[(8, 2)],
    spawn=dict(x=3, y=4, dir="DOWN"),
    interactables=[
        dict(x=6, y=2, script=[say("A cricket match is on. India need 12 runs off the last over... You can't look away! ...But the Professor is waiting.")]),
        dict(x=4, y=2, script=[say("Your summer holiday homework. Untouched since April.")]),
        dict(x=5, y=2, script=[say("Your summer holiday homework. Untouched since April.")]),
        dict(x=7, y=6, script=[say("A shelf crammed with Urumon comics and an old cricket bat.")]),
    ],
))
c, walls = room(11, 8, "t", exit_x=4, wall="green")
c.set(10, 2, "S")
MAPS.append(dict(
    id="player_house_1f", name="Home", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="tile_floor",
    props=[("stove", 1, 2), ("shop_shelf", 2, 2), ("table", 1, 4), ("chair", 0, 4), ("chair", 3, 4), ("tv", 7, 2),
           ("sofa", 7, 4), ("pooja_shelf", 10, 6), ("plant_pot", 0, 6), ("fridge", 0, 2), ("wall_window", 2, 0),
           ("wall_shelf", 1, 1), ("calendar", 4, 0), ("photo_frame", 6, 0), ("wall_clock", 8, 0), ("tube_light", 5, 0),
           ("rug_long", 6, 5, {"color": "#b8453a"}), ("plant_big", 9, 6), ("shoe_rack", 5, 6), ("slippers", 3, 6),
           ("gas_cylinder", 3, 3), ("grinder", 0, 5), ("water_filter", 3, 1)],
    warps=[warp("stairs", 10, 2, "player_house_2f", "stairs", exit="LEFT", mode="step"),
           warp("door", 4, 7, "basavanagudi", "player_house", exit="UP", dir="DOWN")],
    npcs=[npc("amma", 4, 3, "amma", facing="RIGHT", script=[
        {"if": "GOT_STARTER", "then": [
            say("{PLAYER}! You look exhausted. Sit, sit. I made masala dosa.", speaker="Amma"),
            {"heal": True, "setRespawn": True},
            say("There! You and {STARTER} are full of energy again. Come home whenever you're tired.", speaker="Amma"),
        ], "else": [
            say("Good morning, sleepyhead! Professor Sharada stopped by.",
                "She wants you at her lab today - something about Urumon! Don't keep her waiting.", speaker="Amma"),
        ]},
    ])],
    triggers=[dict(id="mom_morning", x=9, y=2, w=1, h=1, unless="GOT_STARTER", script=[
        {"npcFace": {"id": "amma", "dir": "RIGHT"}},
        say("{PLAYER}! Finally awake? Professor Sharada came looking for you.",
            "Sudeep already ran to the lab an hour ago. Go on, it's just down the road!", speaker="Amma"),
    ])],
    respawnText=["{PLAYER}! You came home looking exhausted!",
                 "Amma fed your Urumon hot ragi mudde and they are full of energy again. \"Be careful out there, kanna.\""],
    interactables=[dict(x=7, y=2, script=[say("A news channel: 'Lakes across the city are foaming again. Experts are baffled.'")]),
                   dict(x=10, y=6, script=[say("A small brass lamp flickers in the pooja shelf.")])],
))

# ---------------------------------------------------------------------------------------------
# Sudeep's house
# ---------------------------------------------------------------------------------------------
c, walls = room(10, 8, "w", exit_x=4, wall="pink")
MAPS.append(dict(
    id="rival_house", name="Sudeep's House", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="wood_floor",
    props=[("bookshelf", 1, 2), ("tv", 4, 2), ("sofa", 3, 4), ("table", 6, 4), ("plant_pot", 8, 2), ("cricket_stumps", 8, 5),
           ("trophy_shelf", 5, 0), ("poster", 2, 0, {"color": "#d9534f"}), ("wall_clock", 8, 0), ("photo_frame", 7, 0),
           ("wall_window", 0, 0), ("rug", 3, 5), ("showcase", 6, 2), ("chair", 8, 4), ("bean_bag", 1, 5, {"color": "#4f86b0"}),
           ("shoe_rack", 2, 6), ("slippers", 5, 6), ("calendar", 3, 1)],
    warps=[warp("door", 4, 7, "basavanagudi", "rival_house", exit="UP", dir="DOWN")],
    npcs=[npc("rohan_mom", 6, 3, "rohan_mom", facing="DOWN", script=[
        {"if": "GOT_STARTER", "then": [
            {"if": "ROHAN_MOM_GIFT", "then": [
                say("Sudeep says he's going to be Champion. I said, first become champion of cleaning your room.", speaker="Aunty"),
            ], "else": [
                say("Oh {PLAYER}, you got an Urumon too! Sudeep left without even having breakfast.",
                    "Here, take these for the road. Make sure he eats something if you see him.", speaker="Aunty"),
                {"giveItem": "Filter Kaapi", "qty": 3},
                {"setFlag": "ROHAN_MOM_GIFT"},
            ]},
        ], "else": [
            say("Sudeep? He ran off to his grandmother's lab at six in the morning! Six! On a holiday!", speaker="Aunty"),
        ]},
    ])],
    interactables=[dict(x=8, y=5, script=[say("Cricket stumps, a taped tennis ball and a poster of the city cricket team.")])],
))

# ---------------------------------------------------------------------------------------------
# Professor Sharada's lab
# ---------------------------------------------------------------------------------------------
c, walls = room(13, 10, "l", exit_x=6, wall="lab")
LAB_INTRO = [
    {"cutscene": True},
    {"npcFace": {"id": "rohan_lab", "dir": "DOWN"}},
    say("{PLAYER}! Finally! I've been waiting FOREVER.", speaker="Sudeep"),
    {"playerWalk": ["UP", "UP", "UP"]},
    say("Good morning, {PLAYER}. Thank you for coming.",
        "As you know, the city has been... restless. Lakes foaming, trees vanishing overnight.",
        "The Urumon feel it before we do. I need young eyes out there, and Urumon partners to keep you safe.",
        "On that table are three Urumon. Each one is yours to raise. Go on, choose your partner.", speaker="Prof. Sharada"),
    say("Wait, Grandma! Why does {PLAYER} get to choose first?", speaker="Sudeep"),
    say("Because {PLAYER} was on time, Sudeep. You were late to your own birthday party.", speaker="Prof. Sharada"),
    {"starterChoice": True},
    {"setFlag": "GOT_STARTER"},
    say("Then I'll take {RIVAL_STARTER}! It's the best one anyway. Obviously.", speaker="Sudeep"),
    {"wait": 300},
    say("Sudeep received {RIVAL_STARTER}!"),
    say("Okay {PLAYER}, let's see whose Urumon is stronger! Best of one - no rematches!", speaker="Sudeep"),
    {"battle": {"trainer": "rival_lab", "canLose": True, "environment": "indoor"},
     "onWin": [say("What?! I picked the wrong one... no! I just need practice!", speaker="Sudeep")],
     "onLose": [say("Ha! Did you see that?! Sudeep, future Champion of Bengaluru!", speaker="Sudeep")]},
    {"heal": True},
    say("Splendid! Your partners already trust you.",
        "Take this too - the Uru-Pustaka. It records every Urumon you see and catch.", speaker="Prof. Sharada"),
    {"setFlag": "GOT_PUSTAKA"},
    {"sfx": "SFX_ITEM"},
    say("{PLAYER} received the Uru-Pustaka!"),
    say("And these steel Dabbas. Weaken a wild Urumon, then toss a Dabba to catch it.", speaker="Prof. Sharada"),
    {"giveItem": "Dabba", "qty": 5},
    say("There are six Arena Leaders across the city. Earn their badges, and the Namma Council at Vidhana Soudha will take you seriously.",
        "And keep your eyes open. Something is wrong with this city, and I mean to find out what.", speaker="Prof. Sharada"),
    say("Six badges? I'll get them first! Bye, Grandma! Bye, slowpoke!", speaker="Sudeep"),
    {"npcWalk": {"id": "rohan_lab", "steps": ["DOWN", "DOWN", "DOWN", "RIGHT", "RIGHT", "DOWN"], "ghost": True}},
    {"npcHide": "rohan_lab"},
    {"setFlag": "RIVAL1_DONE"},
    {"cutscene": False},
]
MAPS.append(dict(
    id="lab", name="Urumon Lab", music="MUSIC_LAB", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="lab_floor",
    props=[("lab_machine", 1, 2), ("lab_machine", 2, 2), ("bookshelf", 9, 2), ("bookshelf", 10, 2), ("bookshelf", 11, 2),
           ("desk", 5, 4), ("plant_pot", 0, 8), ("plant_pot", 12, 8), ("cloud_kiosk", 1, 6),
           ("whiteboard", 4, 0), ("map_poster", 7, 0), ("wall_clock", 10, 0), ("tube_light", 2, 0), ("tube_light", 12, 0),
           ("specimen_tank", 3, 2), ("specimen_tank", 12, 2), ("potted_palm", 0, 2), ("stone_reader", 11, 5),
           ("workstation", 9, 8), ("rug_long", 5, 6, {"color": "#4f6f9f"}), ("printer", 8, 4), ("server_rack", 0, 4)],
    warps=[warp("door", 6, 9, "basavanagudi", "lab", exit="UP", dir="DOWN")],
    npcs=[
        npc("prof", 6, 3, "professor", facing="DOWN", script=[
            {"if": "GOT_STARTER", "then": [
                {"if": {"badges": 6}, "then": [
                    say("Six badges! I knew it. The Namma Council at Vidhana Soudha is waiting for you.", speaker="Prof. Sharada"),
                ], "else": [
                    say("How is {STARTER} doing? Urumon grow strongest with partners who believe in them.",
                        "If your team is tired, a Darshini will feed them back to health. Every big neighbourhood has one.", speaker="Prof. Sharada"),
                ]},
            ]},
        ]),
        npc("rohan_lab", 4, 5, "rival", facing="UP", hideIf="RIVAL1_DONE",
            script=[say("Hurry up and pick, {PLAYER}!", speaker="Sudeep")]),
        npc("aide", 10, 6, "techie_f", facing="LEFT", script=[
            say("I'm Kavya, the Professor's assistant.",
                "Tip: Urumon types matter! FIRE burns GRASS, GRASS drinks up WATER, WATER puts out FIRE.",
                "Use the Namma Cloud terminal over there to store extra Urumon you catch.", speaker="Kavya"),
        ]),
    ],
    triggers=[dict(id="intro", x=6, y=8, w=1, h=1, unless="GOT_STARTER", script=LAB_INTRO)],
    interactables=[
        dict(x=1, y=6, script=[{"storage": True}]),
        dict(x=1, y=7, script=[{"storage": True}]),
        dict(x=5, y=4, script=[say("A table with research notes. 'Urumon migration patterns: lakes losing species every year.'")]),
        dict(x=6, y=4, script=[say("A table with research notes. 'Urumon migration patterns: lakes losing species every year.'")]),
        dict(x=9, y=2, script=[say("Dense books: 'Urumon of the Deccan Plateau', 'Lakes of Old Bengaluru', 'Advanced Kaapi Brewing'.")]),
        revival_machine(11, 6), revival_machine(12, 6),
    ],
))

# ---------------------------------------------------------------------------------------------
# Basavanagudi (home town)
# ---------------------------------------------------------------------------------------------
W, H = 42, 40
c = Canvas(W, H, ".")
pr = Props()
# a dense tree line round the town, with gaps for the three ways out
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
c.fill(20, 0, 2, 2, "=").fill(33, H - 2, 2, 2, ":")
# Bull Temple Road (north-south) and its footpaths
c.fill(20, 2, 2, 27, "=").fill(19, 2, 1, 27, "p").fill(22, 2, 1, 27, "p")
# DVG Road (east-west), which runs out west towards Mysuru Road
c.fill(0, 13, 40, 2, "=").fill(2, 12, 2, 1, "@").fill(2, 15, 2, 1, "@")
c.fill(4, 12, 36, 1, "p").fill(4, 15, 36, 1, "p").fill(20, 12, 2, 4, "=")
c.fill(19, 13, 1, 2, "z").fill(22, 13, 1, 2, "z")
# Gandhi Bazaar market street
c.fill(2, 26, 38, 1, "p").fill(2, 27, 38, 2, "=").fill(2, 29, 38, 1, "p").fill(20, 26, 2, 3, "=")
c.fill(19, 27, 1, 2, "z").fill(22, 27, 1, 2, "z")

# --- north-west: your walled yard; the neighbour's tiled house and the corner shops
c.fill(6, 8, 1, 2, "Q").fill(3, 8, 2, 2, ",").fill(2, 11, 17, 1, "d")
pr.box(2, 3, 11, 10, gates={(6, 10)})
pr.put("coconut_palm", 3, 4).put("coconut_palm", 10, 4).put("flower_bed", 9, 8).put("flower_bed", 10, 8, color="#f4c24f")
pr.put("scooter_side", 9, 9).put("rangoli", 6, 8).put("well", 3, 6).put("plant_pot", 4, 9)
c.fill(12, 7, 7, 4, "p").fill(15, 6, 1, 1, "Q")
pr.put("rangoli", 15, 6, color="#4f86b0").put("ashoka", 12, 4).put("ashoka", 18, 4)
pr.put("bunk_shop", 13, 7).put("tea_stall", 16, 7).put("trash_bin", 12, 8).put("bench_stone", 13, 9)
# --- north-east: an apartment block and Sudeep's yard
c.fill(23, 8, 7, 3, "_").fill(34, 8, 1, 2, "Q").fill(23, 11, 17, 1, "d")
pr.put("scooter_side", 24, 9).put("scooter_side", 25, 9, color="#4f86b0").put("scooter_side", 28, 9, color="#f1ead8")
pr.put("street_lamp", 23, 2).put("oil_stain", 27, 10).put("bus_stop", 23, 10)
pr.box(30, 3, 39, 10, gates={(34, 10)})
pr.put("jacaranda", 37, 4).put("car_side", 36, 8, color="#f1ead8").put("cricket_stumps", 31, 8).put("rangoli", 34, 8)
pr.put("petals", 36, 6).put("petals", 38, 7)
# verge along DVG Road: poles and wires, a lamp, a sleeping dog
for x in (8, 17, 26, 37):
    pr.put("electric_pole", x, 10)
pr.put("street_lamp", 13, 10).put("dog", 29, 11).put("manhole", 15, 12).put("pothole", 27, 13).put("puddle", 10, 14)
pr.put("bus_side", 24, 13).put("auto_rickshaw", 20, 17).put("cow", 20, 7).put("pothole", 21, 24).put("manhole", 20, 10)
pr.put("scooter_side", 36, 12, color="#6fbf73").put("wildflowers", 4, 2).put("wildflowers", 13, 2).put("bush", 8, 2)
pr.put("wildflowers", 27, 2).put("grass_tuft", 31, 2).put("bush", 35, 2).put("puddle", 16, 2)

# --- middle-west: Prof. Sharada's lab in its compound, and a pocket park
c.fill(7, 21, 7, 1, "Q").fill(15, 21, 4, 1, "Q").fill(3, 17, 2, 3, ",")
pr.box(2, 16, 14, 22, gates={(14, 21)})
pr.row("flower_bed", 3, 5, 21, color="#a38acb").put("lamp_post", 12, 17).put("hedge", 3, 20).put("hedge", 4, 20)
pr.put("bush", 12, 20).put("potted_palm", 11, 17)
pr.put("jacaranda", 15, 16).put("jacaranda", 17, 18).put("bench", 15, 19).put("petals", 16, 18).put("petals", 18, 20)
pr.put("petals", 15, 22).put("leaves", 17, 23)
# --- middle-east: the Bull Temple courtyard and the groundnut fair
c.fill(23, 16, 17, 8, "Q").fill(23, 24, 17, 2, "e")
pr.put("tree_katte", 24, 16).put("shrine", 38, 16).put("lamp_stand", 29, 19).put("lamp_stand", 37, 19)
pr.put("rangoli_big", 32, 21).put("cow", 26, 21).put("hoarding", 29, 22, text="GROUNDNUT FAIR", color="#e98d3c")
for x in (23, 26, 33, 36):
    pr.put("groundnut_stall", x, 24)
pr.put("flower_stall", 38, 25)
# --- the bazaar: vendors on the footpaths, traffic on the street
pr.put("flower_stall", 5, 29).put("coconut_cart", 9, 29).put("veg_cart", 13, 26).put("coconut_cart", 24, 29)
pr.put("auto_side", 36, 27).put("car_side", 9, 27, color="#d9534f").put("scooter_side", 16, 28)
pr.put("pothole", 26, 28).put("electric_pole", 18, 24).put("bush_tall", 18, 22)

# --- south-west: Bugle Rock with Kempegowda's watchtower, and the park lawns round it
c.fill(2, 30, 2, 8, ":").fill(2, 37, 15, 1, ":").fill(15, 30, 3, 7, '"').fill(4, 34, 3, 3, '"')
c.text(4, 30, """
   !!!!!!
  !!iiii!!
 !!iiiiii!!
!!iiiiiiii!
 !!iiiiii!!
  !!!SS!!!
   !!SS!!""")
pr.put("watchtower", 9, 30).put("tree", 16, 33).put("boulder", 13, 30).put("rock", 5, 31).put("rock", 14, 35)
pr.put("wildflowers", 6, 37).put("stump", 17, 37).put("bush", 4, 30)
# --- south-middle: a dusty lot where the kids play cricket
c.fill(18, 30, 5, 8, "e").fill(20, 31, 1, 4, "H")
pr.put("cricket_stumps", 20, 31).put("cricket_stumps", 20, 34).put("puddle", 22, 32).put("grass_tuft", 22, 34)
pr.put("garbage_pile", 22, 30).put("rain_tree", 18, 35).put("crate", 22, 36).put("auto_side", 21, 37)
# --- south-east: the metro station, the forest road south, a farmhouse under the metro line
c.fill(23, 30, 10, 8, "_").fill(33, 30, 2, 8, ":")
for x in range(32, 40):
    pr.put("metro_deck_h", x, 30)
    pr.put("deck_shadow", x, 32)
pr.put("metro_pillar", 36, 30)
pr.put("fence_h", 33, 35).put("fence_v", 32, 35).put("fence_v", 32, 37).put("fence_v", 35, 36).put("fence_v", 35, 37)
pr.put("barricade", 3, 13).put("coconut_palm", 38, 36).put("banana", 35, 31).put("haystack", 39, 31).put("hens", 36, 36)

MAPS.append(dict(
    id="basavanagudi", name="Basavanagudi", music="MUSIC_TOWN", environment="city", metroStation="basavanagudi",
    layout=c.layout(), props=pr,
    wires=[[(8, 10), (17, 10), (26, 10), (37, 10)]],
    buildings=[
        ("player_house", 4, 4, {"door": dict(id="player_house", to="player_house_1f", toId="door")}),
        ("old_house", 13, 3, {"w": 5}),
        ("apartment", 24, 3, {"w": 5, "h": 5, "wall": "#f1e2c4", "accent": "#5d9b6a"}),
        ("rival_house", 32, 4, {"door": dict(id="rival_house", to="rival_house", toId="door")}),
        ("lab", 5, 17, {"door": dict(id="lab", to="lab", toId="door")}),
        ("temple", 31, 16, {}),
        ("shop", 2, 23, {"w": 4, "sign": "FLOWERS", "awning": "yellow"}),
        ("shop", 6, 23, {"w": 4, "sign": "SILKS", "awning": "pink"}),
        ("shop", 10, 23, {"w": 4, "sign": "BAKERY", "awning": "#e98d3c"}),
        ("shop", 14, 23, {"w": 4, "sign": "DOSA CAMP", "awning": "green"}),
        ("metro_station", 24, 30, {}),
        ("village_hut", 35, 33, {"w": 4, "roof": "tile"}),
    ],
    exits=[dict(side="N", **{"from": 20, "to_": 21}, map="route1"),
           dict(side="S", **{"from": 33, "to_": 34}, map="bannerghatta"),
           dict(side="W", **{"from": 13, "to_": 14}, map="ramanagara")],
    warps=[warp("metro", 28, 35, None, exit="UP", mode="arrive")],
    signs=[
        dict(x=23, y=4, text="BASAVANAGUDI - Where the Big Bull keeps watch."),
        dict(x=4, y=30, text="BUGLE ROCK PARK. Please do not climb the rocks. (Urumon are allowed.) Use the steps - they're older than your grandfather's grandfather."),
        dict(x=13, y=19, text="Prof. Sharada's URUMON LAB - Visitors welcome. Mind the experiments."),
        dict(x=23, y=21, text="DODDA BASAVANA GUDI - the Big Bull Temple. Groundnut fair every November!"),
        dict(x=4, y=11, text="WEST: MYSURU ROAD. Ramanagara Rocks, 50 km. (Road closed for 'repairs'. Since forever.)"),
        dict(x=32, y=36, style="forest", text="SOUTH: BANNERGHATTA FOREST. Forest Department checkpost. Elephants have right of way."),
        dict(x=25, y=35, style="metro", text="NAMMA METRO - National College station. Mind the gap. Mind the auto drivers too."),
        dict(x=12, y=33, style="stone", text="KEMPEGOWDA'S TOWER. The founder of Bengaluru built four towers in 1537 to mark how far his city should ever grow. The city did not listen."),
    ],
    npcs=[
        npc("kid_bt", 20, 33, "kid1", movement="WANDER", script=[
            say("My appa says the Bull Temple is older than the whole city!")]),
        npc("ajji_bt", 25, 22, "ajji", facing="DOWN", script=[
            say("In my day there was a groundnut fair here every week. Now only once a year. Times change, kanda.")]),
        npc("guard_n", 19, 2, "area_boi", facing="RIGHT", hideIf="GOT_STARTER", script=[
            say("Macha, where are you going without an Urumon? The grass up there is full of wild ones.",
                "Go see Professor Sharada first. Then come, we'll see.", speaker="Area Boi")]),
        npc("man_bt", 15, 10, "man2", movement="LOOK", script=[
            say("They say there's a garden with a whole house made of glass up north in Lalbagh. Imagine the electricity bill!")]),
        bendakaalu(28, 25),
        metro_staff("metro_bg", 27, 34, "National College"),
        npc("bannerghatta_guard", 34, 35, "park_ranger", facing="UP", hideIf="GOT_STARTER", script=[
            say("Forest checkpost! Bannerghatta is wild country - elephants, leopards, and Urumon that bite.",
                "No partner Urumon, no entry. Come back when Professor Sharada has trusted you with one.", speaker="Forest Guard")]),
        npc("ramanagara_boi", 3, 14, "area_boi", facing="RIGHT", hideIf="CHAMPION_DONE", script=[
            say("Mysuru Road is closed, boss. The rocks out at Ramanagara are full of very old, very angry Urumon.",
                "Only the Champion of the Namma Council goes past this barricade. Rules of the area.", speaker="Area Boi")]),
        npc("priest_bt", 34, 21, "man4", facing="DOWN", script=[
            say("Long ago a bull kept eating the farmers' groundnuts. They prayed, and it turned to stone right here.",
                "Then the stone bull kept GROWING. So they hammered an iron peg into its head. True story. Mostly.")]),
        npc("tea_anna", 16, 9, "vendor", facing="DOWN", script=[
            say("One by two kaapi? Strong, extra sugar, served in a steel tumbler and davara.",
                "Pour it high so it gets frothy. If you don't spill some, you're not doing it right.")]),
        npc("techie_bt", 27, 9, "techie_m", movement="WANDER", wanderRadius=1, script=[
            say("I work from home, which is also my office, which is also my mother's living room. Very agile.")]),
        npc("kid2_bt", 19, 33, "kid2", facing="RIGHT", script=[
            say("Gully cricket rules: hit the neighbour's window and you're out. AND you pay. AND you run.")]),
        npc("tower_ajja", 7, 33, "ajja", facing="UP", script=[
            say("From up here, the old-timers say you could hear the bugle from the watchtower all the way to the fort.",
                "That's why it's called Bugle Rock. Now you hear mostly auto horns.")]),
        npc("auto_bt", 35, 28, "auto_driver", facing="RIGHT", script=[
            say("Meter? Meter is for tourists, saar. For you, special rate: one and a half. Swalpa adjust maadi.")]),
        npc("flower_akka", 6, 29, "woman4", facing="LEFT", script=[
            say("Mallige, kanakambara, sevanthige! Fresh this morning from the market. One mola for your hair?")]),
    ],
    triggers=[dict(id="no_starter", x=20, y=2, w=2, h=1, once=False, unless="GOT_STARTER", script=[
        {"exclaim": "guard_n"},
        say("Hey, wait! It's dangerous to go out without an Urumon!",
            "Professor Sharada's lab is just down the road, past the cross street."),
        {"playerWalk": ["DOWN"]},
    ])],
    interactables=[
        dict(x=4, y=25, script=[say("FLOWERS. Jasmine, roses and marigolds by the kilo. The florist weaves garlands faster than you can blink.")]),
        dict(x=8, y=25, script=[say("SILKS. A wall of silk sarees in every colour. Somebody's aunty is bargaining at championship level.")]),
        dict(x=12, y=25, script=[say("BAKERY. Fresh benne biscuits and honey cake! The baker waves you off: 'Urumon don't pay in rupees, no?'")]),
        dict(x=16, y=25, script=[say("DOSA CAMP. The queue goes out the door. A sign says: 'No parcel. Dosa must be eaten hot.'")]),
        dict(x=15, y=5, script=[say("A note on the door: 'Gone to Mysuru for a wedding. Please water the tulasi. - Shastri'")]),
    ],
    items=[dict(id="kaapi1", x=11, y=31, item="Filter Kaapi")],
))

# ---------------------------------------------------------------------------------------------
# Route 1 - South End Road
# ---------------------------------------------------------------------------------------------
W, H = 28, 46
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, 3, H, "@").fill(W - 3, 0, 3, H, "@").fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@")
c.fill(12, 0, 2, 5, ":").fill(15, H - 2, 2, 2, "=")
# Lalbagh's south boundary wall and gate
pr.row("compound_wall_h", 3, 10, 3).row("compound_wall_h", 15, 24, 3).put("gate_pillar", 11, 3).put("gate_pillar", 14, 3)
# South End Circle: a ring round the pillar island
c.fill(9, 5, 8, 7, "Q").fill(11, 7, 4, 3, ",")
pr.put("ashoka_pillar", 12, 6).put("flower_bed", 11, 8, color="#f4c24f").put("flower_bed", 13, 8, color="#e0607a")
pr.put("flower_bed", 14, 8, color="#a38acb").put("hedge", 11, 9).put("hedge", 14, 9).put("hedge", 12, 9).put("hedge", 13, 9)
pr.put("street_lamp", 9, 4).put("street_lamp", 16, 4)
# the duck pond east of the circle, a rocky copse west of it
c.fill(18, 5, 5, 4, "~").fill(19, 4, 3, 1, "~").fill(19, 9, 3, 1, "~")
pr.put("ducks", 19, 6).put("lily_pads", 21, 7).put("lotus", 20, 8).put("reeds", 18, 4).put("reeds", 23, 6).put("reeds", 22, 9)
pr.put("bench", 18, 11).put("rock", 8, 9).put("boulder", 5, 8).put("tree_dark", 3, 4).put("bush", 7, 5).put("mushrooms", 4, 10)
# the winding park path: circle -> west -> south -> east -> the road
c.fill(12, 12, 2, 2, ":").fill(6, 12, 8, 2, ":").fill(6, 12, 2, 10, ":").fill(6, 20, 11, 2, ":").fill(15, 20, 2, 6, ":")
c.blob(9, 14, 6, 6, '"', 1).blob(16, 12, 9, 8, '"', 2).fill(3, 14, 2, 6, '"')
pr.put("coconut_cart", 15, 12).put("jacaranda", 3, 11).put("tree_olive", 21, 11).put("bush", 8, 15)
pr.put("gulmohar", 18, 19).put("tree", 21, 19).put("petals_red", 17, 21).put("petals_red", 20, 22).put("bush_tall", 23, 21)
pr.put("rock", 13, 19).put("wildflowers", 10, 19).put("grass_tuft", 8, 18).put("stump", 4, 21)
c.text(3, 22, """
^^^^^^^^^^^^
""")
pr.put("bush", 14, 23).put("bush", 3, 23).put("wildflowers", 9, 24).put("tree", 5, 24).put("tree_dark", 9, 25)
# South End Road: old bungalows to the west, a meadow to the east
c.fill(15, 26, 2, 18, "=").fill(14, 26, 1, 18, "p").fill(17, 26, 1, 18, "p").fill(15, 22, 2, 4, ":")
c.fill(13, 26, 1, 18, "d").fill(3, 34, 11, 2, "e").fill(8, 31, 1, 2, "Q").fill(8, 40, 1, 2, "Q")
pr.box(4, 27, 12, 33, gates={(8, 33)}).box(4, 36, 12, 42, gates={(12, 40)})
pr.put("coconut_palm", 5, 28).put("tulasi_katte", 7, 31).put("clothes_line", 10, 31).put("banana", 5, 31)
pr.put("rangoli", 8, 31).put("scooter_side", 10, 41).put("coconut_palm", 5, 37).put("plant_pot", 5, 40).put("rangoli", 8, 40)
pr.put("well", 11, 37)
for y in (27, 32, 37):
    pr.put("electric_pole", 13, y)
pr.put("hens", 4, 35).put("puddle", 10, 34).put("cow", 6, 35)
c.blob(18, 28, 7, 11, '"', 3, only=".").fill(18, 39, 7, 1, "^").fill(18, 40, 7, 3, ".")
pr.put("bus_stop", 18, 26).put("rock", 22, 30).put("bush", 23, 35).put("street_lamp", 18, 32).put("street_lamp", 18, 37).put("tree", 22, 26).put("gulmohar", 20, 33)
pr.put("pothole", 15, 30).put("manhole", 16, 36).put("auto_side", 15, 41).put("milestone", 18, 30)
pr.put("rock", 24, 40).put("bush", 20, 41).put("wildflowers", 22, 42).put("tree_dark", 18, 41)

MAPS.append(dict(
    id="route1", name="Route 1 - South End Road", music="MUSIC_ROUTE", environment="grass",
    layout=c.layout(), props=pr, wires=[[(13, 27), (13, 32), (13, 37)]],
    buildings=[("old_house", 6, 28, {"w": 5, "wall": "#f2e6c8", "shutters": "#4f86b0"}),
               ("old_house", 6, 37, {"w": 5, "wall": "#e9c7c0"})],
    exits=[dict(side="S", **{"from": 15, "to_": 16}, map="basavanagudi"),
           dict(side="N", **{"from": 12, "to_": 13}, map="lalbagh")],
    signs=[dict(x=19, y=43, text="ROUTE 1 - SOUTH END ROAD. North: Lalbagh. South: Basavanagudi."),
           dict(x=17, y=23, text="Beware! Tall grass ahead. Wild Urumon love it."),
           dict(x=17, y=9, style="stone", text="SOUTH END CIRCLE. The pillar marks the old south gate of Lalbagh. Pigeons consider it theirs.")],
    npcs=[
        trainer("t_r1_kid", 14, 24, "schoolboy", "r1_kid", facing="LEFT", sight=3),
        trainer("t_r1_jogger", 5, 16, "jogger", "r1_jogger", facing="RIGHT", sight=4),
        trainer("t_r1_vendor", 14, 13, "vendor", "r1_vendor", facing="LEFT", sight=2),
        npc("r1_tip", 18, 40, "man1", facing="LEFT", script=[
            say("Wild Urumon hide in the tall grass. Weaken one, then throw a Dabba!",
                "The lower its HP, the easier it is to catch.")]),
        npc("r1_walker", 10, 6, "woman1", movement="WANDER", wanderRadius=1, script=[
            say("Seven rounds of the circle every morning. Doctor said walk more. He didn't say where.")]),
        npc("r1_ajja", 17, 7, "ajja", facing="RIGHT", script=[
            say("The ducks know me. I bring them puffed rice every day. My wife says they love me more than she does.")]),
        npc("r1_rangoli", 13, 41, "woman2", facing="LEFT", script=[
            say("I draw a fresh rangoli every morning, and every morning the dog walks right through it.",
                "We have an understanding.")]),
    ],
    items=[dict(id="dabba1", x=23, y=41, item="Dabba", qty=2), dict(id="kaapi1", x=4, y=7, item="Filter Kaapi"),
           dict(id="elaneer1", x=23, y=4, item="Elaneer")],
))

