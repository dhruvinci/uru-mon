"""MG Road (Arena 2, FIGHT), Silk Board (Route 3), Whitefield (Arena 3, ELECTRIC) and Bellandur Lake."""
from dsl import Canvas, Props, room, warp, npc, trainer, say, enc
from common import metro_staff

MAPS = []

# ---------------------------------------------------------------------------------------------
# MG Road
# ---------------------------------------------------------------------------------------------
W, H = 48, 36
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@").fill(0, H - 2, W, 2, "@")
# Cubbon Road (north) and Brigade Road (south) cross MG Road
c.fill(20, 0, 2, 16, "=").fill(19, 2, 1, 14, "p").fill(22, 2, 1, 14, "p")
c.fill(20, 20, 2, 16, "=").fill(19, 20, 1, 14, "p").fill(22, 20, 1, 14, "p")
# MG Road: four lanes, the boulevard under the metro to the north, a footpath to the south
c.fill(0, 16, W, 4, "=").fill(2, 18, 44, 1, "-").fill(2, 13, 44, 3, "p").fill(2, 13, 44, 1, "_")
c.fill(2, 20, 44, 2, "p").fill(19, 16, 1, 4, "z").fill(22, 16, 1, 4, "z").fill(20, 13, 2, 3, "=")
# north-west: Chinnaswamy Stadium and its plaza
c.fill(2, 9, 17, 4, "Q").fill(2, 2, 17, 2, ".")
pr.put("floodlight", 2, 3).put("floodlight", 16, 3).put("bunk_shop", 3, 9).put("icecream_cart", 15, 9)
pr.put("street_lamp", 5, 9).put("street_lamp", 13, 9).put("trash_bin", 7, 9)
# north-east: the metro station on the boulevard, a little garden with wild grass, an office block
c.blob(37, 2, 9, 8, '"', 2, only=".").fill(23, 9, 23, 4, "_").fill(23, 2, 4, 7, ".")
pr.put("jacaranda", 23, 2).put("jacaranda", 23, 6).put("bench", 40, 10).put("tree", 44, 8).put("rock", 40, 6)
pr.put("street_lamp", 27, 8).put("coconut_cart", 24, 9).put("scooter_side", 37, 10).put("scooter_side", 38, 10, color="#4f86b0")
# the Purple Line over the boulevard
for x in range(2, 46):
    if not 28 <= x <= 35:
        pr.put("metro_deck_h", x, 11).put("deck_shadow", x, 13)
for x in (5, 11, 17, 25, 39, 44):
    pr.put("metro_pillar", x, 11)
# traffic on MG Road (a jam, naturally)
pr.put("bus_side", 5, 16, color="#c8443a").put("auto_side", 11, 17).put("car_side", 14, 16, color="#f1ead8")
pr.put("car_side", 26, 18, color="#4f86b0").put("auto_side", 31, 19).put("scooter_side", 29, 18).put("bus_side", 36, 18)
pr.put("car_side", 9, 19, color="#e98d3c").put("auto_side", 42, 16).put("barricade", 1, 18).put("barricade", 1, 19)
pr.put("barricade", 46, 18).put("barricade", 46, 19).put("cone", 45, 17).put("cone", 2, 17).put("manhole", 33, 17)
# south: Church Street's cafes and bookshops, and the lanes behind
c.fill(2, 25, 44, 2, "_").fill(2, 30, 44, 2, "e").fill(2, 32, 17, 2, ".").fill(23, 32, 23, 2, '"')
for x in (3, 9, 15, 33, 41):
    pr.put("street_lamp", x, 20)
pr.put("flower_stall", 8, 26).put("bench", 12, 26).put("scooter_side", 26, 26).put("scooter_side", 27, 26, color="#6fbf73")
pr.put("scooter_side", 38, 26, color="#f1ead8").put("trash_bin", 31, 26).put("dog", 44, 26)
pr.put("garbage_pile", 2, 30).put("puddle", 10, 31).put("pothole", 30, 30).put("crate", 45, 30).put("auto_side", 15, 30)
pr.put("tree", 3, 32).put("bench", 9, 32).put("tree_dark", 15, 32).put("tree", 43, 32).put("rock", 30, 33)

MAPS.append(dict(
    id="mg_road", name="MG Road", music="MUSIC_CITY", environment="city", metroStation="mg_road",
    layout=c.layout(), props=pr,
    buildings=[
        ("stadium", 6, 4, {"door": dict(id="stadium", to="stadium", toId="door")}),
        ("metro_station", 28, 10, {}),
        ("glass_tower", 30, 2, {"w": 4, "h": 5, "glass": "#5c7fa3", "sign": "OFFICES"}),
        ("shop", 2, 22, {"w": 5, "sign": "BRIGADE", "awning": "red"}),
        ("shop", 7, 22, {"w": 4, "sign": "BOOKS", "awning": "green"}),
        ("shop", 11, 22, {"w": 4, "sign": "CAFE", "awning": "#e98d3c"}),
        ("shop", 15, 22, {"w": 4, "sign": "MUSIC", "awning": "purple"}),
        ("darshini", 23, 22, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 27, 22, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("shop", 31, 22, {"w": 5, "sign": "JEWELLERS", "awning": "yellow"}),
        ("shop", 36, 22, {"w": 5, "sign": "PUB", "awning": "#4f86b0"}),
        ("shop", 41, 22, {"w": 5, "sign": "SAREES", "awning": "pink"}),
        ("old_house", 2, 27, {"w": 5}),
        ("old_house", 9, 27, {"w": 5, "wall": "#e9c7c0"}),
        ("shop", 24, 27, {"w": 4, "sign": "TAILOR", "awning": "sky blue"}),
        ("shop", 28, 27, {"w": 4, "sign": "XEROX", "awning": "#d9534f"}),
        ("old_house", 33, 27, {"w": 6, "wall": "#f2d98c"}),
        ("old_house", 40, 27, {"w": 6, "wall": "#cfe0e6", "shutters": "#c96b5a"}),
    ],
    exits=[dict(side="S", **{"from": 20, "to_": 21}, map="cubbon_park"),
           dict(side="N", **{"from": 20, "to_": 21}, map="sankey_tank"),
           dict(side="E", **{"from": 16, "to_": 17}, map="silk_board"),
           dict(side="W", **{"from": 16, "to_": 17}, map="vidhana_soudha")],
    warps=[warp("metro", 32, 15, None, exit="UP", mode="arrive")],
    signs=[dict(x=18, y=21, text="MAHATMA GANDHI ROAD - Shopping, chai, and the best people-watching in the city."),
           dict(x=14, y=9, text="CHINNASWAMY STADIUM - Arena of Leader Gundappa. No outside food. (Bajji allowed.)"),
           dict(x=2, y=21, text="WEST: VIDHANA SOUDHA. Entry for Namma Council challengers with SIX badges only."),
           dict(x=2, y=25, style="board", text="CHURCH STREET - Books, filter coffee and live music. Mind the buskers."),
           dict(x=36, y=14, style="metro", text="NAMMA METRO - MG Road station. Purple Line.")],
    npcs=[
        metro_staff("metro_mg", 31, 14, "MG Road"),
        npc("cop_east", 46, 16, "traffic_cop", facing="LEFT", hideIf={"badge": "FIGHT"}, script=[
            say("Road closed! Silk Board junction is jammed solid.",
                "Only people with an Arena badge from the stadium get through. Rules are rules.", speaker="Traffic Police")]),
        npc("cop_east2", 46, 17, "traffic_cop", facing="LEFT", hideIf={"badge": "FIGHT"}, script=[
            say("Have you tried Chinnaswamy Stadium? Coach Gundappa's badge opens a lot of doors around here.", speaker="Traffic Police")]),
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
        npc("mg_vendor", 25, 14, "vendor", facing="DOWN", script=[
            say("Hot corn! Masala corn! ...You look like a Masala Dosa person, though.")]),
        npc("mg_old", 16, 21, "ajji", movement="LOOK", script=[
            say("MG Road used to have a tree canopy so thick you didn't need an umbrella. Now we have a metro.",
                "Both are nice, I suppose.")]),
        npc("mg_techie", 36, 21, "techie_f", movement="WANDER", wanderRadius=1, script=[
            say("Whitefield's Arena Leader runs a startup. Her demo days are legendary.",
                "Getting there means crossing Silk Board, though. Pack lunch. And dinner.")]),
        npc("rohan_mg", 21, 31, "rival", facing="DOWN", showIf={"not": "RIVAL2_DONE"}, sight=0, script=[]),
        npc("mg_fan", 9, 10, "cricketer", facing="UP", script=[
            say("Sixteen hours in the queue for a ticket. The match got rained out after one ball.",
                "Best day of my life. I saw the ball.")]),
        npc("mg_busker", 16, 26, "college_m", facing="DOWN", script=[
            say("I only know one song. But I play it with a LOT of feeling.")]),
        npc("mg_bookworm", 34, 26, "college_f", facing="UP", script=[
            say("Church Street on a Sunday: buy a book, drink a coffee, forget to read the book. Perfect.")]),
    ],
    triggers=[dict(id="rival2", once=False, x=20, y=33, w=2, h=1, unless="RIVAL2_DONE", script=[
        {"exclaim": "rohan_mg"},
        {"npcToPlayer": "rohan_mg"},
        {"battle": {"trainer": "rival_mg", "id": "rohan_mg"}},
        say("I'm going to the stadium nets. See you in the history books, {PLAYER}!", speaker="Sudeep"),
        {"npcWalk": {"id": "rohan_mg", "steps": ["UP", "UP", "UP", "UP", "UP", "UP"], "ghost": True}},
        {"npcHide": "rohan_mg"},
        {"setFlag": "RIVAL2_DONE"},
    ])],
    items=[dict(id="pak1", x=38, y=31, item="Mysore Pak"), dict(id="sdabba1", x=2, y=9, item="Steel Dabba", qty=2)],
))

# ---------------------------------------------------------------------------------------------
# Chinnaswamy Stadium (Arena 2, FIGHT)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 16, "E", exit_x=7, wall="stadium")
c.fill(6, 4, 3, 8, "H").fill(0, 13, 15, 2, ".")
MAPS.append(dict(
    id="stadium", name="Chinnaswamy Stadium", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="turf",
    props=[("cricket_stumps", 7, 4), ("cricket_stumps", 7, 11), ("bleachers", 0, 2), ("bleachers", 12, 2), ("bench", 1, 13),
           ("bench", 12, 13), ("scoreboard", 0, 0), ("scoreboard", 12, 0), ("banner", 5, 0, {"color": "#d9534f"}),
           ("banner", 9, 0, {"color": "#d9534f"}), ("practice_net", 0, 6), ("practice_net", 13, 9), ("crate", 14, 5),
           ("water_cooler", 0, 10), ("tube_light", 7, 0), ("plant_pot", 0, 14), ("plant_pot", 14, 14)],
    warps=[warp("door", 7, 15, "mg_road", "stadium", exit="UP", dir="DOWN")],
    npcs=[
        trainer("st_leader", 7, 2, "gundappa", "leader_gundappa", sight=0),
        trainer("st_t1", 3, 9, "cricketer", "st_cricketer1", facing="RIGHT", sight=4),
        trainer("st_t2", 11, 6, "cricketer", "st_cricketer2", facing="LEFT", sight=4),
        trainer("st_t3", 3, 12, "cricketer", "ar_stadium1", facing="RIGHT", sight=3),
        npc("st_guide", 9, 14, "arena_guide", facing="LEFT", script=[
            say("Coach Gundappa uses FIGHT Urumon. Tough as nails!",
                "SKY and MIND moves knock them for six. NORMAL and ROCK types struggle against them.")]),
    ],
    unblock=[],
))

# ---------------------------------------------------------------------------------------------
# Route 3 - Silk Board Junction
# ---------------------------------------------------------------------------------------------
W, H = 56, 28
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# Outer Ring Road (east-west, seven lanes of patience) and Hosur Road (north-south, closed for metro work)
c.fill(0, 12, 2, 2, "=").fill(W - 2, 15, 2, 2, "=")
c.fill(2, 11, W - 4, 7, "=").fill(2, 14, W - 4, 1, "-").fill(2, 10, W - 4, 1, "p").fill(2, 18, W - 4, 1, "p")
c.fill(26, 2, 6, 24, "=").fill(28, 2, 1, 8, "|").fill(28, 19, 1, 7, "|").fill(25, 2, 1, 8, "p").fill(32, 2, 1, 8, "p")
c.fill(25, 19, 1, 7, "p").fill(32, 19, 1, 7, "p").fill(25, 11, 1, 7, "z").fill(32, 11, 1, 7, "z")
# the double-decker flyover: metro on top, road below, pillars along the north kerb
for x in range(2, W - 2):
    pr.put("double_deck_h", x, 7).put("deck_shadow", x, 10)
for x in (5, 12, 19, 36, 43, 50):
    pr.put("double_pillar", x, 7)
# gridlock
for name, x, y, kw in (("bus_side", 3, 15, {}), ("car_side", 8, 12, {"color": "#f1ead8"}), ("auto_side", 11, 12, {}),
                       ("car_side", 14, 13, {"color": "#d9534f"}), ("scooter_side", 17, 12, {}), ("auto_side", 19, 16, {}),
                       ("car_side", 8, 16, {"color": "#4f86b0"}), ("scooter_side", 13, 16, {"color": "#6fbf73"}),
                       ("bus_side", 15, 15, {"color": "#c8443a"}), ("car_side", 21, 13, {"color": "#e98d3c"}),
                       ("auto_side", 34, 12, {}), ("car_side", 37, 13, {"color": "#f1ead8"}), ("bus_side", 40, 11, {}),
                       ("scooter_side", 45, 12, {"color": "#4f86b0"}), ("car_side", 47, 13, {"color": "#a38acb"}),
                       ("auto_side", 35, 16, {}), ("car_side", 39, 16, {"color": "#d9534f"}), ("scooter_side", 42, 17, {}),
                       ("bus_side", 46, 15, {"color": "#5f9e6f"}), ("auto_side", 29, 13, {}), ("car_side", 26, 15, {}),
                       ("scooter_side", 30, 17, {"color": "#f1ead8"}), ("auto_rickshaw", 27, 5, {}), ("car", 29, 21, {"color": "red"})):
    pr.put(name, x, y, **kw)
pr.put("pothole", 23, 12).put("pothole", 9, 14).put("puddle", 33, 15).put("manhole", 44, 14).put("oil_stain", 24, 16)
pr.put("traffic_light", 24, 19).put("traffic_light", 33, 20)
# Hosur Road closed both ends
pr.row("barricade", 26, 31, 3).row("cone", 26, 31, 24).put("road_arrow", 29, 23)
# north-west: the BMTC bus stand and its tea stalls
c.fill(2, 2, 22, 5, "_").fill(14, 2, 10, 2, '"')
pr.put("bus_stop", 3, 2).put("bus_side", 7, 4).put("bus_side", 12, 4, color="#c8443a").put("tea_stall", 17, 4)
pr.put("bunk_shop", 20, 4).put("hoarding", 2, 5, text="IT CORRIDOR", color="#4f86b0").put("trash_bin", 23, 6).put("garbage_pile", 16, 6)
# north-east: the metro works yard
c.fill(33, 2, 21, 5, "j")
pr.row("site_fence_h", 33, 52, 6).put("crane", 34, 1).put("pipe_stack", 40, 2).put("sand_heap", 43, 4).put("cement_bags", 46, 3)
pr.put("concrete_mixer", 48, 2).put("brick_stack", 51, 5).put("brick_stack", 51, 4).put("dumper", 38, 3).put("lantern", 52, 2)
# south-west: the Central Silk Board office that gave the junction its name
c.fill(2, 19, 22, 7, ".").blob(13, 19, 11, 7, '"', 2, only=".")
pr.put("street_lamp", 10, 19).put("tree", 8, 23).put("rock", 18, 24).put("bush", 22, 19)
# south-east: wasteland, a wild-grass meadow and the hawkers who sell you things through car windows
c.fill(33, 19, 21, 7, ".").blob(35, 19, 18, 7, '"', 5, only=".")
pr.put("coconut_cart", 33, 19).put("garbage_pile", 52, 19).put("tree_olive", 49, 23).put("rock", 40, 24).put("stump", 45, 21)
pr.put("street_lamp", 39, 19).put("street_lamp", 47, 19)

MAPS.append(dict(
    id="silk_board", name="Route 3 - Silk Board Junction", music="MUSIC_ROUTE", environment="city",
    layout=c.layout(), props=pr,
    buildings=[("glass_tower", 3, 20, {"w": 5, "h": 5, "glass": "#7a9a8a", "sign": "SILK BOARD", "trim": "#d6cfc2"})],
    exits=[dict(side="W", **{"from": 12, "to_": 13}, map="mg_road"),
           dict(side="E", **{"from": 15, "to_": 16}, map="whitefield")],
    signs=[dict(x=2, y=18, text="SILK BOARD JUNCTION. Estimated waiting time: yes."),
           dict(x=53, y=19, text="WHITEFIELD 18 km. (Approx. 1 to 4 hours.)"),
           dict(x=9, y=21, text="CENTRAL SILK BOARD. Silkworms were here first. Then the traffic came.")],
    npcs=[
        trainer("t_sb_auto1", 12, 20, "auto_driver", "sb_auto1", facing="UP", sight=2),
        trainer("t_sb_auto2", 33, 13, "auto_driver", "sb_auto2", facing="RIGHT", sight=2),
        trainer("t_sb_rider", 24, 16, "delivery_rider", "sb_rider", facing="RIGHT", sight=4),
        trainer("t_sb_techie", 44, 20, "techie_f", "sb_techie", facing="UP", sight=3),
        trainer("t_sb_college", 16, 21, "college_m", "sb_college", facing="UP", sight=4),
        npc("sb_stuck", 10, 13, "man4", facing="UP", script=[
            say("I've been stuck at this signal so long, my Urumon evolved. Twice.")]),
        npc("sb_cop", 28, 14, "traffic_cop", facing="DOWN", script=[
            say("Keep moving! ...I mean, keep standing still. Everyone is standing still.", speaker="Traffic Police")]),
        npc("sb_hawker", 23, 14, "vendor", facing="LEFT", script=[
            say("Car sun-shades! Phone chargers! Peanuts! A map of Bengaluru! ...Okay, the map is from 1994.")]),
        npc("sb_conductor", 6, 3, "man3", facing="DOWN", script=[
            say("500D to Hebbal! Come, come, there's space inside! ...There's always space inside. Just breathe in.")]),
        npc("sb_engineer", 41, 5, "officer", facing="DOWN", script=[
            say("Metro work. Two more months. ...I've been saying 'two more months' for three years now.")]),
    ],
    items=[dict(id="dosa1", x=52, y=24, item="Masala Dosa", qty=2), dict(id="coil1", x=2, y=19, item="Mosquito Coil", qty=2),
           dict(id="sdabba1", x=52, y=3, item="Steel Dabba")],
))

# ---------------------------------------------------------------------------------------------
# Whitefield
# ---------------------------------------------------------------------------------------------
W, H = 46, 36
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# ITPL Main Road with the metro running above its north footpath
c.fill(0, 14, 2, 1, "p").fill(0, 15, 2, 1, "=").fill(2, 11, 42, 2, "d").fill(2, 13, 42, 2, "p")
c.fill(2, 15, 42, 4, "=").fill(2, 17, 42, 1, "-").fill(2, 19, 42, 2, "p")
c.fill(17, 15, 1, 4, "z").fill(20, 15, 1, 4, "z")
# the road south to Bellandur, squeezed between walls of trees at the checkpoint
c.fill(18, 19, 2, 17, "=").fill(17, 21, 1, 11, "p").fill(20, 21, 1, 11, "p")
c.fill(16, 32, 2, 2, "@").fill(20, 32, 2, 2, "@")
for x in range(2, 44):
    if not 4 <= x <= 11:
        pr.put("metro_deck_h", x, 11).put("deck_shadow", x, 13)
for x in (14, 21, 28, 35, 41):
    pr.put("metro_pillar", x, 11)
# the tech park campus behind its wall, entered past a security booth and a boom barrier
c.fill(13, 8, 31, 2, "Q").fill(27, 2, 2, 6, ",").fill(4, 10, 8, 3, "_")
pr.row("compound_wall_h", 13, 21, 10).row("compound_wall_h", 26, 43, 10)
pr.put("security_booth", 22, 9).put("boom_barrier", 23, 10)
for x in (19, 28, 35, 43):
    pr.put("coconut_palm", x, 8)
pr.put("fountain", 27, 5).put("bench", 30, 9).put("bean_bag", 36, 9, color="#e0607a").put("bean_bag", 37, 9, color="#4f86b0")
pr.put("flower_bed", 14, 9).put("flower_bed", 15, 9, color="#f4c24f").put("lamp_post", 26, 7).put("trash_bin", 41, 9)
# west of the campus: an old Whitefield cottage from the days of mango orchards
pr.put("mango", 2, 2).put("mango", 10, 7).put("banana", 2, 7).put("well", 11, 2).put("hens", 5, 8).put("rangoli", 6, 6)
# traffic: office shuttles, cabs, one lost auto
pr.put("bus_side", 5, 16, color="#f1ead8").put("car_side", 12, 18, color="#2f2b36").put("car_side", 14, 15, color="#f1ead8")
pr.put("auto_side", 24, 16).put("car_side", 27, 18, color="#a38acb").put("bus_side", 33, 17, color="#5f9e6f")
pr.put("scooter_side", 38, 15).put("car_side", 40, 16, color="#d9534f").put("manhole", 30, 16).put("pothole", 9, 15)
for x in (6, 13, 24, 31, 38):
    pr.put("street_lamp", x, 19)
# south-west: a darshini, a kirana and a cafe on a lane, apartments behind, their parking lot
c.fill(2, 24, 15, 2, "_").fill(2, 31, 14, 3, "_")
pr.put("scooter_side", 7, 25).put("scooter_side", 8, 25, color="#4f86b0").put("trash_bin", 16, 24).put("plant_pot", 2, 24)
pr.put("tree", 14, 27).put("tree_dark", 14, 29).put("car_side", 3, 32, color="#f1ead8").put("car_side", 7, 32, color="#4f86b0")
pr.put("scooter_side", 11, 32).put("scooter_side", 12, 32, color="#e98d3c").put("oil_stain", 9, 33)
# south-east: the mall, a bus stop, and a vacant plot gone wild
c.blob(22, 25, 22, 9, '"', 3, only=".")
pr.put("bus_stop", 22, 21).put("icecream_cart", 38, 22).put("tree", 41, 25).put("rock", 30, 29).put("stump", 25, 31)
pr.put("hoarding", 39, 30, text="PLOTS FOR SALE", color="#d9534f")

MAPS.append(dict(
    id="whitefield", name="Whitefield", music="MUSIC_CITY", environment="city", metroStation="whitefield",
    layout=c.layout(), props=pr,
    buildings=[
        ("tech_tower", 21, 2, {"door": dict(id="tech_park", to="tech_park", toId="door")}),
        ("glass_tower", 14, 2, {"w": 5, "h": 6, "sign": "INFOTECH"}),
        ("glass_tower", 29, 2, {"w": 5, "h": 6, "glass": "#4f9a96", "sign": "CLOUDWORKS"}),
        ("glass_tower", 37, 2, {"w": 6, "h": 6, "glass": "#6b7fa8", "sign": "DATA HUB"}),
        ("old_house", 4, 3, {"w": 5, "wall": "#f2e6c8", "shutters": "#3d7a5a"}),
        ("metro_station", 4, 10, {}),
        ("darshini", 3, 21, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 8, 21, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("shop", 12, 21, {"w": 4, "sign": "CAFE", "awning": "#2f2b36"}),
        ("apartment", 3, 26, {"w": 5, "h": 5, "wall": "#dfe6ea", "accent": "#4f86b0"}),
        ("apartment", 9, 26, {"w": 5, "h": 5, "wall": "#f1e2c4", "accent": "#c96b5a"}),
        ("glass_tower", 30, 21, {"w": 7, "h": 4, "glass": "#c9a24e", "sign": "MALL", "trim": "#e6dcc4"}),
    ],
    exits=[dict(side="W", **{"from": 14, "to_": 15}, map="silk_board"),
           dict(side="S", **{"from": 18, "to_": 19}, map="bellandur")],
    warps=[warp("metro", 8, 15, None, exit="UP", mode="arrive")],
    signs=[dict(x=26, y=14, text="WHITEFIELD TECH PARK - Arena of Leader Tanvi. Visitors must sign an NDA. (Not really.)"),
           dict(x=21, y=21, text="SOUTH: Bellandur Lake. Do not touch the foam."),
           dict(x=12, y=14, style="metro", text="NAMMA METRO - Whitefield station. End of the Purple Line. End of the world, some say.")],
    npcs=[
        metro_staff("metro_wf", 7, 14, "Whitefield"),
        npc("wf_guard", 18, 33, "area_boi", facing="UP", hideIf={"badge": "ELECTRIC"}, script=[
            say("Road to Bellandur is closed, bro. Full chemical smell, foam everywhere. Even our bikes got foamed.",
                "Only a badge-holding trainer can go in. Seen Tanvi at the tech park?", speaker="Area Boi")]),
        npc("wf_guard2", 19, 33, "area_boi2", facing="UP", hideIf={"badge": "ELECTRIC"}, script=[
            say("Don't argue, guru. Even the delivery boys are turning back.", speaker="Area Boi")]),
        npc("wf_techie", 30, 14, "techie_m", movement="WANDER", wanderRadius=1, script=[
            say("I commute two hours each way. I have optimised my podcast list to perfection.")]),
        npc("wf_coffee", 13, 24, "college_f", facing="LEFT", script=[
            say("Whitefield has eleven coffee places and zero parking spots.")]),
        npc("rohan_wf", 3, 15, "rival", facing="RIGHT", showIf={"not": "RIVAL3_DONE"}, script=[]),
        npc("wf_security", 23, 9, "officer", facing="DOWN", script=[
            say("Visitor pass? ID card? Laptop declaration? ...Arena challenger? Fine, fine, go in.", speaker="Security")]),
        npc("wf_founder", 33, 9, "techie_f", facing="DOWN", script=[
            say("Our startup is like a darshini, but with an app. And no food. We're 'pre-revenue'.")]),
        npc("wf_ajji", 7, 7, "ajji", facing="DOWN", script=[
            say("When I was a girl, all of Whitefield was mango orchards and little cottages.",
                "Now they call it 'Phase Two'. I still have my mango trees. Phase One.")]),
    ],
    triggers=[dict(id="rival3", once=False, x=1, y=14, w=1, h=2, unless="RIVAL3_DONE", script=[
        {"exclaim": "rohan_wf"},
        {"npcToPlayer": "rohan_wf"},
        {"battle": {"trainer": "rival_whitefield", "id": "rohan_wf"}},
        say("Tanvi's Arena is in the big tower. Her Urumon zap like a short circuit. Good luck - not that you need it.", speaker="Sudeep"),
        {"npcWalk": {"id": "rohan_wf", "steps": ["RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"], "ghost": True}},
        {"npcHide": "rohan_wf"},
        {"setFlag": "RIVAL3_DONE"},
    ])],
    items=[dict(id="chakli1", x=36, y=28, item="Chakli"), dict(id="bath1", x=3, y=10, item="Bisi Bele Bath")],
))

# ---------------------------------------------------------------------------------------------
# Tech Park (Arena 3, ELECTRIC)
# ---------------------------------------------------------------------------------------------
c, walls = room(15, 15, "Z", exit_x=7, wall="office")
c.fill(6, 3, 3, 11, "l")
MAPS.append(dict(
    id="tech_park", name="Tech Park Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="office_carpet",
    props=[("server_rack", 1, 4), ("server_rack", 2, 4), ("server_rack", 3, 4), ("server_rack", 11, 4), ("server_rack", 12, 4),
           ("server_rack", 13, 4), ("workstation", 1, 9), ("workstation", 4, 9), ("workstation", 9, 9), ("workstation", 12, 9),
           ("plant_pot", 0, 13), ("plant_pot", 14, 13), ("sofa", 6, 6), ("whiteboard", 2, 0), ("whiteboard", 11, 0),
           ("poster", 5, 0, {"color": "#f4c24f"}), ("poster", 9, 0, {"color": "#7fb8e0"}), ("tube_light", 7, 0),
           ("glass_partition_h", 1, 10), ("glass_partition_h", 2, 10), ("glass_partition_h", 12, 10), ("glass_partition_h", 13, 10),
           ("coffee_machine", 14, 2), ("water_cooler", 0, 2), ("foosball", 11, 12), ("bean_bag", 13, 7, {"color": "#e0607a"}),
           ("bean_bag", 1, 7, {"color": "#6fbf73"}), ("printer", 0, 6), ("potted_palm", 14, 5)],
    warps=[warp("door", 7, 14, "whitefield", "tech_park", exit="UP", dir="DOWN")],
    npcs=[
        trainer("tp_leader", 7, 2, "tanvi", "leader_tanvi", sight=0),
        trainer("tp_t1", 3, 11, "techie_m", "wf_techie1", facing="RIGHT", sight=4),
        trainer("tp_t2", 11, 7, "techie_f", "wf_techie2", facing="LEFT", sight=4),
        trainer("tp_t3", 4, 7, "techie_f", "ar_tech1", facing="RIGHT", sight=2),
        npc("tp_guide", 9, 13, "arena_guide", facing="LEFT", script=[
            say("Tanvi's team is pure ELECTRIC. EARTH moves short-circuit them completely!",
                "And ELECTRIC moves do nothing to EARTH types. Just saying.")]),
    ],
))

# ---------------------------------------------------------------------------------------------
# Bellandur Lake
# ---------------------------------------------------------------------------------------------
W, H = 40, 38
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
c.fill(18, 0, 2, 11, ":").fill(3, 11, 34, 2, ":").fill(3, 13, 34, 1, ":")
# the lake: grey-green water, foam drifting from the sludge pipe, a shore path all round
c.fill(3, 13, 2, 20, ":").fill(35, 13, 2, 20, ":").fill(3, 31, 34, 2, ":")
c.blob(5, 15, 30, 16, "~", 4, rough=0.15)
c.blob(7, 15, 12, 7, "U", 1, only="~").blob(24, 22, 9, 6, "U", 2, only="~").blob(12, 24, 6, 5, "U", 3, only="~")
c.fill(20, 25, 1, 6, "B").fill(19, 24, 3, 1, "b")
# the Syndicate's yard and site office
c.fill(2, 2, 15, 9, "j")
pr.put("crane", 3, 2).put("dumper", 14, 2).put("pipe_stack", 15, 7).put("cement_bags", 16, 5).put("lantern", 7, 9)
for x, y in ((3, 8), (4, 8), (3, 9), (5, 9)):
    pr.put("drum_barrel", x, y, color="#6f8a3a")
pr.put("pipe_outlet", 12, 14).put("foam_bank", 11, 14).put("foam_bank", 13, 14).put("drum_barrel", 14, 14, color="#6f8a3a")
# lake-view apartments, and residents who have had enough
c.fill(21, 8, 17, 3, "_")
pr.put("hoarding", 21, 8, text="SAVE OUR LAKE", color="#4f86b0").put("scooter_side", 26, 9).put("car_side", 32, 9, color="#f1ead8")
pr.put("street_lamp", 25, 8).put("street_lamp", 35, 8)
# the shore: reeds, rubbish, tired eucalyptus
for x, y in ((6, 14), (33, 14), (4, 28), (35, 27), (27, 14), (9, 30)):
    pr.put("reeds", x, y)
pr.put("garbage_pile", 16, 14).put("garbage_pile", 36, 20).put("eucalyptus", 37, 14).put("eucalyptus", 37, 24)
pr.put("eucalyptus", 2, 16).put("eucalyptus", 2, 26).put("foam_bank", 30, 31).put("foam_bank", 8, 31)
# south: wild grass and the old fishing jetty
c.blob(3, 33, 34, 3, '"', 6, rough=0.5).fill(3, 35, 34, 1, '"')
pr.put("puddle", 9, 12).put("pothole", 27, 11).put("grass_tuft", 3, 20).put("grass_tuft", 36, 17).put("leaves", 13, 32)
pr.put("puddle", 30, 32).put("grass_tuft", 18, 31).put("rubble", 5, 11).put("garbage_pile", 34, 12)
pr.put("boat", 22, 27).put("tree_dark", 35, 33).put("rock", 10, 34).put("stump", 28, 34)

MAPS.append(dict(
    id="bellandur", name="Bellandur Lake", music="MUSIC_SYNDICATE", environment="lake",
    layout=c.layout(), props=pr, waterStyle="murky", forestKinds=["tree_olive", "tree", "tree_dark"],
    buildings=[("syndicate_hq", 8, 4, {"door": dict(id="site", to="bellandur_site", toId="door")}),
               ("apartment", 22, 2, {"w": 5, "h": 6, "wall": "#e8dcc0", "accent": "#c96b5a"}),
               ("apartment", 28, 2, {"w": 5, "h": 6, "wall": "#dfe6ea", "accent": "#4f86b0"}),
               ("apartment", 34, 2, {"w": 4, "h": 6, "wall": "#f1e2c4", "accent": "#5d9b6a"})],
    exits=[dict(side="N", **{"from": 18, "to_": 19}, map="whitefield")],
    signs=[dict(x=20, y=10, text="BELLANDUR LAKE. Once the city's largest lake. Now the city's largest bubble bath."),
           dict(x=15, y=10, text="CONCRETE SYNDICATE - SITE OFFICE. Keep out. We are building the future (of parking).")],
    npcs=[
        trainer("t_bl_grunt1", 15, 9, "grunt_m", "grunt_bell1", facing="RIGHT", sight=3),
        trainer("t_bl_grunt2", 26, 13, "grunt_f", "grunt_bell2", facing="LEFT", sight=4),
        trainer("t_bl_grunt3", 4, 24, "grunt_m", "grunt_bell3", facing="UP", sight=4),
        trainer("t_bl_fisher", 16, 31, "fisher", "bl_fisher", facing="UP", sight=3),
        npc("bl_officer", 21, 12, "rowdy", facing="DOWN", showIf="BELLANDUR_ADMIN_DONE", hideIf="BELLANDUR_DONE", script=[]),
        npc("bl_resident", 30, 10, "woman4", facing="DOWN", script=[
            {"if": "BELLANDUR_DONE", "then": [
                say("The pipes are shut and the foam is settling! I could cry. I might cry.")],
             "else": [say("My flat overlooks the lake. Every morning the foam is a little higher.",
                          "Last week a foam monster rose out of it and floated past my balcony. I'm not joking!")]}]),
        npc("bl_activist", 24, 10, "college_f", facing="DOWN", script=[
            say("We've written to the city four hundred times. The fish have written too. Well, the ones that are left.")]),
        npc("bl_birder", 36, 29, "birdwatcher", facing="LEFT", script=[
            say("Purple herons still nest in the reeds, foam and all. Stubborn birds. I like them.")]),
    ],
    triggers=[dict(id="metro_reward", x=8, y=8, w=6, h=3, requires="BELLANDUR_ADMIN_DONE", unless="BELLANDUR_DONE", script=[
        {"npcToPlayer": "bl_officer"},
        say("Oi! You're the kid who shut down the foam factory? I'm Rangappa. Everyone calls me Rowdy Rangappa.",
            "This lake is MY area. Thirty years I've swum here. Those Syndicate fellows thought they could dump in it?",
            "You did what I couldn't, and without breaking a single head. Respect, chikka. Take this.", speaker="Rowdy Rangappa"),
        {"giveItem": "Metro Card"},
        say("A Metro Card. Tap it at any Namma Metro station. My nephew works at the Metro office - don't ask questions.",
            "And that barricade north of MG Road? Consider it gone. Nobody blocks a friend of Rangappa.",
            "That Admin kept muttering about 'the hills' and 'sunrise'. If they go to Nandi, you go too. Give them one from me.",
            speaker="Rowdy Rangappa"),
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
    items=[dict(id="elaneer1", x=3, y=14, item="Elaneer", qty=2), dict(id="tiffin1", x=32, y=34, item="Tiffin Carrier")],
))

c, walls = room(13, 11, "t", exit_x=6, wall="site")
MAPS.append(dict(
    id="bellandur_site", name="Syndicate Site Office", music="MUSIC_SYNDICATE", interior=True, environment="indoor",
    layout=c.layout(), walls=walls, ground="tile_floor",
    props=[("desk", 2, 3), ("desk", 9, 3), ("crate", 1, 7), ("crate", 2, 7), ("crate", 11, 7), ("crate", 10, 8),
           ("bookshelf", 5, 2), ("bookshelf", 7, 2), ("valve_wheel", 3, 1), ("hard_hats", 10, 1), ("map_poster", 4, 0),
           ("safety_poster", 8, 0), ("safety_poster", 1, 0), ("tube_light", 6, 0),
           ("blueprint_table", 2, 5), ("drum_barrel", 11, 5, {"color": "#6f8a3a"}), ("drum_barrel", 12, 5, {"color": "#6f8a3a"}),
           ("cement_bags", 1, 8), ("water_cooler", 12, 2), ("cone", 9, 8), ("hard_hats", 12, 8)],
    warps=[warp("door", 6, 10, "bellandur", "site", exit="UP", dir="DOWN")],
    npcs=[
        trainer("bs_admin", 6, 3, "bhaskar", "admin_shetty", sight=0, hideIf="BELLANDUR_ADMIN_DONE",
                onDefeat=[{"npcWalk": {"id": "self", "steps": ["RIGHT", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN"], "ghost": True}},
                          {"npcHide": "self"}, {"setFlag": "BELLANDUR_ADMIN_DONE"},
                          say("Shetty fled! The valve on the wall reads: SLUDGE PIPE - SHUT.")]),
        npc("bs_valve_note", 1, 2, "grunt_f", facing="DOWN", hideIf="BELLANDUR_ADMIN_DONE", script=[
            say("Shh! Admin Shetty's busy. Something about pumping 'extra-special detergent' into the lake.")]),
    ],
    interactables=[dict(x=3, y=1, script=[say("A big red valve marked SLUDGE PIPE. A note taped to it: 'DO NOT CLOSE. - Mgmt.'")]),
                   dict(x=2, y=5, script=[say("Blueprints: 'BELLANDUR LAKE PARKING COMPLEX - PHASE 1'. The lake is coloured grey.")]),
                   dict(x=3, y=5, script=[say("Blueprints: 'BELLANDUR LAKE PARKING COMPLEX - PHASE 1'. The lake is coloured grey.")])],
))

