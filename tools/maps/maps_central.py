"""MG Road (Arena 2, FIGHT), Silk Board (Route 3), Whitefield (Arena 3, ELECTRIC) and Bellandur Lake."""
from dsl import Canvas, room, warp, npc, trainer, say, enc
from common import metro_staff

MAPS = []

# ---------------------------------------------------------------------------------------------
# MG Road
# ---------------------------------------------------------------------------------------------
W, H = 44, 34
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(20, 21)], "N": [(20, 21)], "E": [(16, 17)], "W": [(16, 17)]})
c.fill(20, 0, 2, 34, "=")                      # Brigade Road / Cubbon Road spine
c.fill(0, 16, 44, 2, "=")                      # MG Road
c.fill(20, 0, 1, 34, "|")
c.fill(0, 16, 44, 1, "-")
c.fill(18, 0, 2, 34, "_").fill(22, 0, 2, 34, "_")
c.fill(0, 14, 44, 2, "_").fill(0, 18, 44, 2, "_")
c.fill(18, 14, 6, 6, "=")
c.fill(18, 16, 6, 1, "z").fill(20, 14, 2, 6, "z")
# north-west: stadium grounds
c.fill(4, 3, 12, 9, "_")
# north-east: metro plaza
c.fill(26, 3, 12, 8, "_")
# south: shops
c.fill(3, 21, 15, 7, "_")
c.fill(26, 21, 15, 7, "_")
# small garden with wild grass in the south-east corner
c.fill(32, 28, 8, 3, '"')
c.set(12, 29, "G").set(4, 28, "G").set(27, 29, "J")
MAPS.append(dict(
    id="mg_road", name="MG Road", music="MUSIC_CITY", environment="city", metroStation="mg_road",
    layout=c.layout(),
    buildings=[
        ("stadium", 6, 4, {"door": dict(id="stadium", to="stadium", toId="door")}),
        ("metro_station", 28, 3, {}),
        ("darshini", 4, 22, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 10, 22, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("shop", 28, 22, {"w": 4, "sign": "BRIGADE", "awning": "red"}),
        ("shop", 34, 22, {"w": 4, "sign": "BOOKS", "awning": "green"}),
    ],
    exits=[dict(side="S", **{"from": 20, "to_": 21}, map="cubbon_park"),
           dict(side="N", **{"from": 20, "to_": 21}, map="sankey_tank"),
           dict(side="E", **{"from": 16, "to_": 17}, map="silk_board"),
           dict(side="W", **{"from": 16, "to_": 17}, map="vidhana_soudha")],
    warps=[warp("metro", 33, 8, None, exit="UP", mode="arrive")],
    signs=[dict(x=17, y=12, text="MAHATMA GANDHI ROAD - Shopping, chai, and the best people-watching in the city."),
           dict(x=13, y=10, text="CUBBON CRICKET STADIUM - Arena of Leader Gundappa. No outside food. (Bajji allowed.)"),
           dict(x=3, y=13, text="WEST: VIDHANA SOUDHA. Entry for Namma Council challengers with SIX badges only.")],
    npcs=[
        metro_staff("metro_mg", 32, 7, "MG Road"),
        npc("cop_east", 42, 16, "traffic_cop", facing="LEFT", hideIf={"badge": "FIGHT"}, script=[
            say("Road closed! Silk Board junction is jammed solid.",
                "Only people with an Arena badge from the stadium get through. Rules are rules.", speaker="Traffic Police")]),
        npc("cop_east2", 42, 17, "traffic_cop", facing="LEFT", hideIf={"badge": "FIGHT"}, script=[
            say("Have you tried the stadium? Coach Gundappa's badge opens a lot of doors around here.", speaker="Traffic Police")]),
        npc("guard_w1", 1, 16, "officer", facing="RIGHT", hideIf={"badges": 6}, script=[
            say("Vidhana Soudha is the seat of the Namma Council.",
                "Only trainers with all six Arena badges may enter.", speaker="Guard")]),
        npc("guard_w2", 1, 17, "officer", facing="RIGHT", hideIf={"badges": 6}, script=[
            say("Six badges. Not five. Not five and a half. Six.", speaker="Guard")]),
        npc("barricade1", 20, 1, "traffic_cop", facing="DOWN", hideIf="BELLANDUR_DONE", script=[
            say("Road north is closed for a VIP convoy. Has been for... three weeks now.",
                "Maybe if you did something heroic, the city would open it for you.", speaker="Traffic Police")]),
        npc("barricade2", 21, 1, "traffic_cop", facing="DOWN", hideIf="BELLANDUR_DONE", script=[
            say("Barricades. Barricades everywhere.", speaker="Traffic Police")]),
        npc("mg_vendor", 25, 13, "vendor", facing="DOWN", script=[
            say("Hot corn! Masala corn! ...You look like a Masala Dosa person, though.")]),
        npc("mg_old", 15, 20, "ajji", movement="LOOK", script=[
            say("MG Road used to have a tree canopy so thick you didn't need an umbrella. Now we have a metro.",
                "Both are nice, I suppose.")]),
        npc("mg_techie", 36, 20, "techie_f", movement="WANDER", script=[
            say("Whitefield's Arena Leader runs a startup. Her demo days are legendary.",
                "Getting there means crossing Silk Board, though. Pack lunch. And dinner.")]),
        npc("rohan_mg", 21, 29, "rival", facing="DOWN", showIf={"not": "RIVAL2_DONE"}, sight=0, script=[]),
    ],
    triggers=[dict(id="rival2", x=20, y=31, w=2, h=1, unless="RIVAL2_DONE", script=[
        {"exclaim": "rohan_mg"},
        {"npcToPlayer": "rohan_mg"},
        {"battle": {"trainer": "rival_mg", "id": "rohan_mg"}},
        say("I'm going to the stadium nets. See you in the history books, {PLAYER}!", speaker="Rohan"),
        {"npcWalk": {"id": "rohan_mg", "steps": ["UP", "UP", "UP", "UP", "UP", "UP"], "ghost": True}},
        {"npcHide": "rohan_mg"},
        {"setFlag": "RIVAL2_DONE"},
    ])],
    items=[dict(id="pak1", x=38, y=30, item="Mysore Pak"), dict(id="sdabba1", x=5, y=12, item="Steel Dabba", qty=2)],
    encounters={"grass": enc(0.12, (32, 11, 14, 30), (20, 11, 14, 20), (47, 12, 14, 20), (56, 12, 14, 10), (13, 12, 14, 20))},
))

# ---------------------------------------------------------------------------------------------
# Cubbon Cricket Stadium (Arena 2, FIGHT)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 16, ".", exit_x=7, wall="wood")
c.fill(6, 4, 3, 8, ":")
MAPS.append(dict(
    id="stadium", name="Cubbon Cricket Stadium", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="grass",
    props=[("cricket_stumps", 7, 4), ("cricket_stumps", 7, 11), ("bench", 1, 3), ("bench", 12, 3), ("bench", 1, 13),
           ("bench", 12, 13)],
    warps=[warp("door", 7, 15, "mg_road", "stadium", exit="UP", dir="DOWN")],
    npcs=[
        trainer("st_leader", 7, 2, "gundappa", "leader_gundappa", sight=0),
        trainer("st_t1", 3, 9, "cricketer", "st_cricketer1", facing="RIGHT", sight=4),
        trainer("st_t2", 11, 6, "cricketer", "st_cricketer2", facing="LEFT", sight=4),
        trainer("st_t3", 3, 12, "cricketer", "ar_stadium1", facing="RIGHT", sight=3),
        npc("st_guide", 9, 14, "man1", facing="LEFT", script=[
            say("Coach Gundappa uses FIGHT Urumon. Tough as nails!",
                "SKY and MIND moves knock them for six. NORMAL and ROCK types struggle against them.")]),
    ],
    unblock=[],
))

# ---------------------------------------------------------------------------------------------
# Route 3 - Silk Board Junction
# ---------------------------------------------------------------------------------------------
W, H = 52, 24
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"W": [(10, 11)], "E": [(10, 11)]})
c.fill(0, 9, 52, 4, "=")
c.fill(0, 10, 52, 1, "-")
c.fill(22, 0, 6, 24, "=")
c.fill(24, 0, 1, 24, "|")
c.fill(22, 8, 6, 6, "z")
c.fill(0, 7, 52, 2, "_").fill(0, 13, 52, 2, "_")
c.fill(20, 0, 2, 24, "_").fill(28, 0, 2, 24, "_")
# medians of tall grass and dusty verges
c.fill(4, 3, 14, 3, '"')
c.fill(32, 3, 16, 3, '"')
c.fill(4, 17, 14, 4, '"')
c.fill(32, 17, 16, 4, '"')
MAPS.append(dict(
    id="silk_board", name="Route 3 - Silk Board Junction", music="MUSIC_ROUTE", environment="city",
    layout=c.layout(),
    props=[("auto_rickshaw", 6, 9), ("car", 10, 11, {"color": "white"}), ("auto_rickshaw", 14, 9), ("car", 17, 11, {"color": "red"}),
           ("auto_rickshaw", 31, 11), ("car", 34, 9, {"color": "blue"}), ("auto_rickshaw", 38, 11), ("car", 42, 9, {"color": "white"}),
           ("auto_rickshaw", 22, 3), ("car", 26, 18, {"color": "red"}), ("auto_rickshaw", 25, 5), ("scooter", 9, 13),
           ("scooter", 30, 8), ("bus_stop", 44, 14), ("lamp_post", 19, 6), ("lamp_post", 30, 15)],
    exits=[dict(side="W", **{"from": 10, "to_": 11}, map="mg_road"),
           dict(side="E", **{"from": 10, "to_": 11}, map="whitefield")],
    signs=[dict(x=3, y=7, text="SILK BOARD JUNCTION. Estimated waiting time: yes."),
           dict(x=46, y=13, text="WHITEFIELD 18 km. (Approx. 1 to 4 hours.)")],
    npcs=[
        trainer("t_sb_auto1", 12, 7, "auto_driver", "sb_auto1", facing="DOWN", sight=2),
        trainer("t_sb_auto2", 33, 13, "auto_driver", "sb_auto2", facing="UP", sight=2),
        trainer("t_sb_rider", 27, 16, "delivery_rider", "sb_rider", facing="LEFT", sight=4),
        trainer("t_sb_techie", 40, 7, "techie_f", "sb_techie", facing="DOWN", sight=3),
        trainer("t_sb_college", 19, 20, "college_m", "sb_college", facing="RIGHT", sight=4),
        npc("sb_stuck", 8, 13, "man4", facing="UP", script=[
            say("I've been stuck at this signal so long, my Urumon evolved. Twice.")]),
        npc("sb_cop", 25, 14, "traffic_cop", facing="DOWN", script=[
            say("Keep moving! ...I mean, keep standing still. Everyone is standing still.", speaker="Traffic Police")]),
    ],
    items=[dict(id="dosa1", x=46, y=19, item="Masala Dosa", qty=2), dict(id="coil1", x=5, y=19, item="Mosquito Coil", qty=2),
           dict(id="sdabba1", x=47, y=4, item="Steel Dabba")],
    encounters={"grass": enc(0.13, (20, 14, 18, 22), (32, 14, 17, 14), (28, 14, 17, 12), (11, 15, 18, 14), (47, 15, 18, 14),
                             (18, 14, 17, 12), (51, 17, 17, 3), (56, 15, 17, 9))},
))

# ---------------------------------------------------------------------------------------------
# Whitefield
# ---------------------------------------------------------------------------------------------
W, H = 40, 32
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"W": [(14, 15)], "S": [(18, 19)]})
c.fill(0, 14, 40, 2, "=").fill(0, 14, 40, 1, "-")
c.fill(18, 14, 2, 18, "=").fill(18, 14, 1, 18, "|")
c.fill(0, 12, 40, 2, "_").fill(0, 16, 40, 2, "_")
c.fill(16, 16, 2, 16, "_").fill(20, 16, 2, 16, "_")
c.fill(3, 3, 34, 8, "_")
c.fill(3, 19, 12, 9, "_")
c.fill(24, 20, 12, 3, '"')
c.fill(24, 26, 12, 3, '"')
MAPS.append(dict(
    id="whitefield", name="Whitefield", music="MUSIC_CITY", environment="city", metroStation="whitefield",
    layout=c.layout(),
    buildings=[
        ("tech_tower", 15, 3, {"door": dict(id="tech_park", to="tech_park", toId="door")}),
        ("tech_tower", 4, 3, {}),
        ("tech_tower", 26, 3, {}),
        ("darshini", 4, 20, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 10, 20, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("metro_station", 5, 24, {}),
    ],
    exits=[dict(side="W", **{"from": 14, "to_": 15}, map="silk_board"),
           dict(side="S", **{"from": 18, "to_": 19}, map="bellandur")],
    warps=[warp("metro", 10, 29, None, exit="UP", mode="arrive")],
    signs=[dict(x=14, y=11, text="WHITEFIELD TECH PARK - Arena of Leader Tanvi. Visitors must sign an NDA. (Not really.)"),
           dict(x=22, y=18, text="SOUTH: Bellandur Lake. Do not touch the foam.")],
    npcs=[
        metro_staff("metro_wf", 9, 28, "Whitefield"),
        npc("wf_guard", 18, 30, "officer", facing="UP", hideIf={"badge": "ELECTRIC"}, script=[
            say("The road to Bellandur Lake is closed. Strange chemical smell, foam everywhere.",
                "Only a badge-holding trainer could go in safely. Have you seen Tanvi at the tech park?", speaker="Security")]),
        npc("wf_guard2", 19, 30, "officer", facing="UP", hideIf={"badge": "ELECTRIC"}, script=[
            say("Sorry, closed. Please don't make me fill out an incident report.", speaker="Security")]),
        npc("wf_techie", 30, 13, "techie_m", movement="WANDER", script=[
            say("I commute two hours each way. I have optimised my podcast list to perfection.")]),
        npc("wf_coffee", 13, 24, "college_f", facing="LEFT", script=[
            say("Whitefield has eleven coffee places and zero parking spots.")]),
        npc("rohan_wf", 3, 15, "rival", facing="RIGHT", showIf={"not": "RIVAL3_DONE"}, script=[]),
    ],
    triggers=[dict(id="rival3", x=1, y=14, w=1, h=2, unless="RIVAL3_DONE", script=[
        {"exclaim": "rohan_wf"},
        {"npcToPlayer": "rohan_wf"},
        {"battle": {"trainer": "rival_whitefield", "id": "rohan_wf"}},
        say("Tanvi's Arena is in the big tower. Her Urumon zap like a short circuit. Good luck - not that you need it.", speaker="Rohan"),
        {"npcWalk": {"id": "rohan_wf", "steps": ["RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"], "ghost": True}},
        {"npcHide": "rohan_wf"},
        {"setFlag": "RIVAL3_DONE"},
    ])],
    items=[dict(id="chakli1", x=36, y=28, item="Chakli"), dict(id="bath1", x=3, y=10, item="Bisi Bele Bath")],
    encounters={"grass": enc(0.12, (49, 17, 21, 30), (47, 17, 21, 25), (56, 18, 20, 15), (32, 17, 20, 15), (28, 18, 20, 15))},
))

# ---------------------------------------------------------------------------------------------
# Tech Park (Arena 3, ELECTRIC)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 15, "l", exit_x=7, wall="lab")
MAPS.append(dict(
    id="tech_park", name="Tech Park Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="lab_floor",
    props=[("lab_machine", 1, 4), ("lab_machine", 2, 4), ("lab_machine", 3, 4), ("lab_machine", 11, 4), ("lab_machine", 12, 4),
           ("lab_machine", 13, 4), ("desk", 1, 9), ("desk", 4, 9), ("desk", 9, 9), ("desk", 12, 9), ("plant_pot", 0, 13),
           ("plant_pot", 14, 13), ("sofa", 6, 6)],
    warps=[warp("door", 7, 14, "whitefield", "tech_park", exit="UP", dir="DOWN")],
    npcs=[
        trainer("tp_leader", 7, 2, "tanvi", "leader_tanvi", sight=0),
        trainer("tp_t1", 3, 11, "techie_m", "wf_techie1", facing="RIGHT", sight=4),
        trainer("tp_t2", 11, 7, "techie_f", "wf_techie2", facing="LEFT", sight=4),
        trainer("tp_t3", 4, 7, "techie_f", "ar_tech1", facing="RIGHT", sight=2),
        npc("tp_guide", 9, 13, "man1", facing="LEFT", script=[
            say("Tanvi's team is pure ELECTRIC. EARTH moves short-circuit them completely!",
                "And ELECTRIC moves do nothing to EARTH types. Just saying.")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Bellandur Lake
# ---------------------------------------------------------------------------------------------
W, H = 38, 36
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"N": [(18, 19)]})
c.fill(18, 0, 2, 12, ":")
c.fill(4, 11, 30, 2, ":")
c.fill(4, 11, 2, 20, ":")
c.fill(4, 29, 12, 2, ":")
c.fill(8, 15, 26, 13, "~")
c.fill(7, 17, 1, 9, "~").fill(34, 17, 1, 9, "~")
c.fill(9, 28, 24, 1, "~")
c.fill(22, 3, 12, 6, '"')
c.fill(8, 31, 24, 3, '"')
c.fill(2, 15, 2, 12, '"')
MAPS.append(dict(
    id="bellandur", name="Bellandur Lake", music="MUSIC_SYNDICATE", environment="lake",
    layout=c.layout(),
    buildings=[("syndicate_hq", 8, 4, {"door": dict(id="site", to="bellandur_site", toId="door")})],
    exits=[dict(side="N", **{"from": 18, "to_": 19}, map="whitefield")],
    signs=[dict(x=20, y=10, text="BELLANDUR LAKE. Once the city's largest lake. Now the city's largest bubble bath."),
           dict(x=14, y=10, text="CONCRETE SYNDICATE - SITE OFFICE. Keep out. We are building the future (of parking).")],
    npcs=[
        trainer("t_bl_grunt1", 15, 9, "grunt_m", "grunt_bell1", facing="RIGHT", sight=3),
        trainer("t_bl_grunt2", 26, 13, "grunt_f", "grunt_bell2", facing="LEFT", sight=4),
        trainer("t_bl_grunt3", 6, 22, "grunt_m", "grunt_bell3", facing="UP", sight=4),
        trainer("t_bl_fisher", 16, 30, "fisher", "bl_fisher", facing="UP", sight=3),
        npc("bl_officer", 21, 12, "officer", facing="DOWN", showIf="BELLANDUR_ADMIN_DONE", hideIf="BELLANDUR_DONE", script=[]),
        npc("bl_resident", 30, 10, "woman4", facing="DOWN", script=[
            {"if": "BELLANDUR_DONE", "then": [
                say("The pipes are shut and the foam is settling! I could cry. I might cry.")],
             "else": [say("My flat overlooks the lake. Every morning the foam is a little higher.",
                          "Last week a foam monster rose out of it and floated past my balcony. I'm not joking!")]}]),
    ],
    triggers=[dict(id="metro_reward", x=8, y=8, w=6, h=3, requires="BELLANDUR_ADMIN_DONE", unless="BELLANDUR_DONE", script=[
        {"npcToPlayer": "bl_officer"},
        say("Are you the trainer who stopped the dumping? I'm Inspector Gowda from the city office.",
            "We've been trying to catch the Syndicate for months. Every time we came, the site was 'closed for lunch'.",
            "On behalf of the city - thank you. Please take this.", speaker="Inspector Gowda"),
        {"giveItem": "Metro Card"},
        say("A Metro Card! Tap it at any Namma Metro station to ride between stations you've visited.",
            "Oh, and I'll have the barricade on the road north of MG Road removed. You've earned free passage.",
            "That Admin said something about 'the hills' and 'sunrise'... I don't like the sound of that.", speaker="Inspector Gowda"),
        {"setFlag": "BELLANDUR_DONE"},
        {"npcWalk": {"id": "bl_officer", "steps": ["UP", "UP", "UP", "UP"], "ghost": True}},
        {"npcHide": "bl_officer"},
    ])],
    interactables=[dict(x=21, y=15, requires={"not": "FOAM_SPIRIT_DONE"}, script=[
        say("The foam is churning... something huge is rising out of it!"),
        {"battle": {"wild": {"species": 23, "level": 26}, "music": "MUSIC_LEGEND"},
         "onWin": [{"setFlag": "FOAM_SPIRIT_DONE"}], "onLose": []},
        {"setFlag": "FOAM_SPIRIT_DONE"},
    ])],
    items=[dict(id="elaneer1", x=3, y=13, item="Elaneer", qty=2), dict(id="tiffin1", x=32, y=33, item="Tiffin Carrier")],
    encounters={"grass": enc(0.13, (22, 19, 23, 30), (18, 19, 23, 20), (45, 19, 22, 15), (24, 19, 23, 15), (43, 19, 22, 10),
                             (20, 20, 23, 10))},
))

c, walls = room(13, 11, "t", exit_x=6, wall="plain")
MAPS.append(dict(
    id="bellandur_site", name="Syndicate Site Office", music="MUSIC_SYNDICATE", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="tile_floor",
    props=[("desk", 2, 3), ("desk", 9, 3), ("crate", 1, 7), ("crate", 2, 7), ("crate", 11, 7), ("crate", 10, 8),
           ("bookshelf", 5, 2), ("bookshelf", 7, 2)],
    warps=[warp("door", 6, 10, "bellandur", "site", exit="UP", dir="DOWN")],
    npcs=[
        trainer("bs_admin", 6, 3, "bhaskar", "admin_shetty", sight=0, hideIf="BELLANDUR_ADMIN_DONE",
                onDefeat=[{"npcWalk": {"id": "self", "steps": ["RIGHT", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN"], "ghost": True}},
                          {"npcHide": "self"}, {"setFlag": "BELLANDUR_ADMIN_DONE"},
                          say("Shetty fled! The valve on the wall reads: SLUDGE PIPE - SHUT.")]),
        npc("bs_valve_note", 1, 2, "grunt_f", facing="DOWN", hideIf="BELLANDUR_ADMIN_DONE", script=[
            say("Shh! Admin Shetty's busy. Something about pumping 'extra-special detergent' into the lake.")]),
    ],
))
