"""Basavanagudi: the player's home town, the lab, and Route 1 (South End Road)."""
from dsl import Canvas, room, warp, npc, trainer, say, enc

MAPS = []

# ---------------------------------------------------------------------------------------------
# Player's house
# ---------------------------------------------------------------------------------------------
c, walls = room(9, 8, "w")
c.set(8, 2, "S")
MAPS.append(dict(
    id="player_house_2f", name="Your Room", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="wood_floor",
    props=[("bed", 1, 2), ("desk", 4, 2), ("tv", 6, 2), ("bookshelf", 7, 6), ("rug", 3, 4), ("plant_pot", 1, 6)],
    warps=[warp("stairs", 8, 2, "player_house_1f", "stairs", exit="LEFT", mode="step")],
    unblock=[(8, 2)],
    spawn=dict(x=3, y=4, dir="DOWN"),
    interactables=[
        dict(x=6, y=2, script=[say("A cricket match is on. India need 12 runs off the last over... You can't look away! ...But the Professor is waiting.")]),
        dict(x=4, y=2, script=[say("Your summer holiday homework. Untouched since April.")]),
        dict(x=5, y=2, script=[say("Your summer holiday homework. Untouched since April.")]),
        dict(x=7, y=6, script=[say("A shelf crammed with Urumon comics and an old cricket bat.")]),
        dict(x=7, y=7, script=[say("A shelf crammed with Urumon comics and an old cricket bat.")]),
    ],
))
c, walls = room(11, 8, "t", exit_x=4)
c.set(10, 2, "S")
MAPS.append(dict(
    id="player_house_1f", name="Home", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="tile_floor",
    props=[("stove", 1, 2), ("shop_shelf", 2, 2), ("table", 1, 4), ("chair", 0, 4), ("chair", 3, 4), ("tv", 7, 2),
           ("sofa", 7, 4), ("pooja_shelf", 10, 6), ("plant_pot", 0, 6)],
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
            "Rohan already ran to the lab an hour ago. Go on, it's just down the road!", speaker="Amma"),
    ])],
    respawnText=["{PLAYER}! You came home looking exhausted!",
                 "Amma fed your Urumon hot ragi mudde and they are full of energy again. \"Be careful out there, kanna.\""],
    interactables=[dict(x=7, y=2, script=[say("A news channel: 'Lakes across the city are foaming again. Experts are baffled.'")]),
                   dict(x=10, y=6, script=[say("A small brass lamp flickers in the pooja shelf.")])],
))

# ---------------------------------------------------------------------------------------------
# Rohan's house
# ---------------------------------------------------------------------------------------------
c, walls = room(10, 8, "w", exit_x=4)
MAPS.append(dict(
    id="rival_house", name="Rohan's House", music="MUSIC_HOME", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="wood_floor",
    props=[("bookshelf", 1, 2), ("tv", 4, 2), ("sofa", 3, 4), ("table", 6, 4), ("plant_pot", 8, 2), ("cricket_stumps", 8, 5)],
    warps=[warp("door", 4, 7, "basavanagudi", "rival_house", exit="UP", dir="DOWN")],
    npcs=[npc("rohan_mom", 6, 3, "rohan_mom", facing="DOWN", script=[
        {"if": "GOT_STARTER", "then": [
            {"if": "ROHAN_MOM_GIFT", "then": [
                say("Rohan says he's going to be Champion. I said, first become champion of cleaning your room.", speaker="Aunty"),
            ], "else": [
                say("Oh {PLAYER}, you got an Urumon too! Rohan left without even having breakfast.",
                    "Here, take these for the road. Make sure he eats something if you see him.", speaker="Aunty"),
                {"giveItem": "Filter Kaapi", "qty": 3},
                {"setFlag": "ROHAN_MOM_GIFT"},
            ]},
        ], "else": [
            say("Rohan? He ran off to his grandmother's lab at six in the morning! Six! On a holiday!", speaker="Aunty"),
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
    say("{PLAYER}! Finally! I've been waiting FOREVER.", speaker="Rohan"),
    {"playerWalk": ["UP", "UP", "UP"]},
    say("Good morning, {PLAYER}. Thank you for coming.",
        "As you know, the city has been... restless. Lakes foaming, trees vanishing overnight.",
        "The Urumon feel it before we do. I need young eyes out there, and Urumon partners to keep you safe.",
        "On that table are three Urumon. Each one is yours to raise. Go on, choose your partner.", speaker="Prof. Sharada"),
    say("Wait, Grandma! Why does {PLAYER} get to choose first?", speaker="Rohan"),
    say("Because {PLAYER} was on time, Rohan. You were late to your own birthday party.", speaker="Prof. Sharada"),
    {"starterChoice": True},
    {"setFlag": "GOT_STARTER"},
    say("Then I'll take {RIVAL_STARTER}! It's the best one anyway. Obviously.", speaker="Rohan"),
    {"wait": 300},
    say("Rohan received {RIVAL_STARTER}!"),
    say("Okay {PLAYER}, let's see whose Urumon is stronger! Best of one - no rematches!", speaker="Rohan"),
    {"battle": {"trainer": "rival_lab", "canLose": True, "environment": "indoor"},
     "onWin": [say("What?! I picked the wrong one... no! I just need practice!", speaker="Rohan")],
     "onLose": [say("Ha! Did you see that?! Rohan, future Champion of Bengaluru!", speaker="Rohan")]},
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
    say("Six badges? I'll get them first! Bye, Grandma! Bye, slowpoke!", speaker="Rohan"),
    {"npcWalk": {"id": "rohan_lab", "steps": ["DOWN", "DOWN", "DOWN", "RIGHT", "RIGHT", "DOWN"], "ghost": True}},
    {"npcHide": "rohan_lab"},
    {"setFlag": "RIVAL1_DONE"},
    {"cutscene": False},
]
MAPS.append(dict(
    id="lab", name="Urumon Lab", music="MUSIC_LAB", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="lab_floor",
    props=[("lab_machine", 1, 2), ("lab_machine", 2, 2), ("bookshelf", 9, 2), ("bookshelf", 10, 2), ("bookshelf", 11, 2),
           ("desk", 5, 4), ("plant_pot", 0, 8), ("plant_pot", 12, 8), ("cloud_kiosk", 1, 6)],
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
            script=[say("Hurry up and pick, {PLAYER}!", speaker="Rohan")]),
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
    ],
))

# ---------------------------------------------------------------------------------------------
# Basavanagudi (home town)
# ---------------------------------------------------------------------------------------------
W, H = 32, 26
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"N": [(15, 16)]})
c.fill(15, 0, 2, 21, "_")          # main road, north exit down to the lower street
c.fill(3, 9, 26, 2, "_")           # cross street
c.fill(3, 19, 26, 2, "_")          # lower street
c.fill(6, 8, 1, 1, ":")            # player's front path (door at x=6)
c.fill(22, 8, 1, 1, ":")           # Rohan's front path
c.fill(11, 17, 1, 2, ":")          # lab front path
c.fill(23, 17, 1, 2, ":")          # temple front path
for x, y in [(9, 5), (10, 5), (18, 5), (19, 5), (13, 12), (14, 12), (19, 12), (20, 12), (8, 22), (9, 22), (27, 22)]:
    c.set(x, y, "q")
for x, y in [(3, 5), (26, 5), (27, 5), (12, 22), (13, 22), (20, 22), (21, 22)]:
    c.set(x, y, "u")
c.set(11, 2, "J").set(26, 12, "J").set(4, 12, "G")
# Bugle Rock park in the south-west corner
c.set(2, 21, "O").set(5, 22, "r").set(6, 21, "O").set(3, 23, "r")
c.text(17, 21, """
,,,,
,,,,""")
MAPS.append(dict(
    id="basavanagudi", name="Basavanagudi", music="MUSIC_TOWN", environment="city",
    layout=c.layout(),
    buildings=[
        ("player_house", 4, 4, {"door": dict(id="player_house", to="player_house_1f", toId="door")}),
        ("rival_house", 20, 4, {"door": dict(id="rival_house", to="rival_house", toId="door")}),
        ("lab", 8, 13, {"door": dict(id="lab", to="lab", toId="door")}),
        ("temple", 21, 12, {}),
    ],
    exits=[dict(side="N", **{"from": 15, "to_": 16}, map="route1")],
    signs=[
        dict(x=17, y=7, text="BASAVANAGUDI - Where the Big Bull keeps watch."),
        dict(x=8, y=21, text="BUGLE ROCK PARK. Please do not climb the rocks. (Urumon are allowed.)"),
        dict(x=12, y=17, text="Prof. Sharada's URUMON LAB - Visitors welcome. Mind the experiments."),
        dict(x=24, y=17, text="DODDA BASAVANA GUDI - the Big Bull Temple. Groundnut fair every November!"),
    ],
    npcs=[
        npc("kid_bt", 10, 23, "kid1", movement="WANDER", script=[
            say("My appa says the Bull Temple is older than the whole city!")]),
        npc("ajji_bt", 26, 17, "ajji", facing="LEFT", script=[
            say("In my day there was a groundnut fair here every week. Now only once a year. Times change, kanda.")]),
        npc("guard_n", 14, 2, "officer", facing="DOWN", hideIf="GOT_STARTER", script=[
            say("The tall grass up the road is full of wild Urumon.",
                "Go and see Professor Sharada before you wander off, okay?")]),
        npc("man_bt", 24, 9, "man2", movement="LOOK", script=[
            say("They say there's a garden with a whole house made of glass up north in Lalbagh. Imagine the electricity bill!")]),
    ],
    triggers=[dict(id="no_starter", x=15, y=2, w=2, h=1, once=False, unless="GOT_STARTER", script=[
        {"exclaim": "guard_n"},
        say("Hey, wait! It's dangerous to go out without an Urumon!",
            "Professor Sharada's lab is just down the road, past the cross street."),
        {"playerWalk": ["DOWN"]},
    ])],
    items=[dict(id="kaapi1", x=4, y=21, item="Filter Kaapi")],
))

# ---------------------------------------------------------------------------------------------
# Route 1 - South End Road
# ---------------------------------------------------------------------------------------------
W, H = 22, 44
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"N": [(10, 11)], "S": [(15, 16)]})
c.fill(10, 0, 2, 12, ":")
c.fill(10, 11, 7, 2, ":")
c.fill(15, 11, 2, 33, ":")
c.fill(4, 22, 12, 2, ":")
c.fill(4, 22, 2, 14, ":")
c.fill(4, 34, 12, 2, ":")
# tall grass patches
c.fill(3, 4, 6, 6, '"')
c.fill(12, 15, 3, 6, '"')
c.fill(7, 26, 7, 6, '"')
c.fill(17, 26, 3, 8, '"')
c.fill(2, 37, 4, 4, '"')
# trees inside
c.trees(12, 2, 4, 4)
c.trees(2, 14, 6, 4)
c.trees(17, 14, 2, 8)
c.set(9, 38, "J").set(12, 39, "J")
c.text(6, 18, """
,,,
,,,""")
MAPS.append(dict(
    id="route1", name="Route 1 - South End Road", music="MUSIC_ROUTE", environment="grass",
    layout=c.layout(),
    exits=[dict(side="S", **{"from": 15, "to_": 16}, map="basavanagudi"),
           dict(side="N", **{"from": 10, "to_": 11}, map="lalbagh")],
    signs=[dict(x=17, y=40, text="ROUTE 1 - SOUTH END ROAD. North: Lalbagh. South: Basavanagudi."),
           dict(x=8, y=11, text="Beware! Tall grass ahead. Wild Urumon love it.")],
    npcs=[
        trainer("t_r1_kid", 14, 24, "schoolboy", "r1_kid", facing="LEFT", sight=3),
        trainer("t_r1_jogger", 6, 30, "jogger", "r1_jogger", facing="RIGHT", sight=4),
        trainer("t_r1_vendor", 12, 9, "vendor", "r1_vendor", facing="DOWN", sight=2),
        npc("r1_tip", 17, 38, "man1", facing="LEFT", script=[
            say("Wild Urumon hide in the tall grass. Weaken one, then throw a Dabba!",
                "The lower its HP, the easier it is to catch.")]),
    ],
    items=[dict(id="dabba1", x=19, y=34, item="Dabba", qty=2), dict(id="kaapi1", x=3, y=13, item="Filter Kaapi"),
           dict(id="elaneer1", x=17, y=3, item="Elaneer")],
    encounters={"grass": enc(0.12, (10, 2, 4, 35), (13, 2, 4, 30), (28, 3, 5, 15), (32, 3, 4, 12), (20, 3, 4, 8))},
))
