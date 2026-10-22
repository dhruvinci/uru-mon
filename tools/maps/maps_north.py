"""Sankey Tank, Malleshwaram (Arena 4, MIND), Palace Road (Arena 5, SPIRIT), Hebbal and Nandi Hills (Arena 6, SKY)."""
from dsl import Canvas, room, warp, npc, trainer, say, enc
from common import metro_staff

MAPS = []

# ---------------------------------------------------------------------------------------------
# Route 5 - Sankey Tank
# ---------------------------------------------------------------------------------------------
W, H = 28, 44
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(12, 13)], "N": [(12, 13)]})
c.fill(12, 34, 2, 10, ":")
c.fill(4, 34, 10, 2, ":")
c.fill(4, 8, 2, 28, ":")
c.fill(4, 8, 10, 2, ":")
c.fill(12, 0, 2, 10, ":")
c.fill(10, 14, 14, 16, "~")
c.fill(11, 13, 12, 1, "~").fill(11, 30, 12, 1, "~")
c.fill(7, 12, 3, 20, '"')
c.fill(15, 36, 10, 4, '"')
c.fill(16, 3, 9, 5, '"')
c.set(24, 12, "J").set(24, 22, "J").set(2, 38, "G")
MAPS.append(dict(
    id="sankey_tank", name="Route 5 - Sankey Tank", music="MUSIC_ROUTE", environment="lake",
    layout=c.layout(),
    exits=[dict(side="S", **{"from": 12, "to_": 13}, map="mg_road"),
           dict(side="N", **{"from": 12, "to_": 13}, map="malleshwaram")],
    props=[("bench", 6, 20), ("bench", 6, 26), ("lamp_post", 3, 18)],
    signs=[dict(x=14, y=40, text="SANKEY TANK - Built in 1882 to bring water to the city. Ducks: welcome. Foam: not welcome."),
           dict(x=10, y=6, text="NORTH: Malleshwaram. Famous for jasmine, silk sarees and the strictest tuition teacher in town.")],
    npcs=[
        trainer("t_sk_ajja", 5, 30, "ajja", "sk_ajja", facing="UP", sight=3),
        trainer("t_sk_ajji", 4, 16, "ajji", "sk_ajji", facing="DOWN", sight=3),
        trainer("t_sk_bird", 13, 4, "birdwatcher", "sk_bird", facing="DOWN", sight=4),
        npc("sk_walker", 20, 37, "woman1", movement="WANDER", script=[
            say("Every evening I walk three rounds of the tank. The Kappe here sing louder than the temple bells.")]),
    ],
    items=[dict(id="bath1", x=24, y=38, item="Bisi Bele Bath"), dict(id="elaneer1", x=8, y=11, item="Elaneer"),
           dict(id="tdabba1", x=24, y=4, item="Steel Dabba", qty=3)],
))

# ---------------------------------------------------------------------------------------------
# Malleshwaram
# ---------------------------------------------------------------------------------------------
W, H = 40, 32
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(18, 19)], "E": [(14, 15)]})
c.fill(18, 0, 2, 32, "_")
c.fill(0, 14, 40, 2, "_")
c.fill(3, 3, 14, 9, "_")
c.fill(22, 3, 15, 9, "_")
c.fill(3, 18, 14, 10, "_")
c.fill(22, 18, 15, 3, "_")
c.fill(24, 23, 12, 5, '"')
for x in (4, 7, 10, 13):
    c.set(x, 13, "q")
c.set(23, 21, "J").set(34, 21, "J")
MAPS.append(dict(
    id="malleshwaram", name="Malleshwaram", music="MUSIC_TOWN", environment="city", metroStation="malleshwaram",
    layout=c.layout(),
    buildings=[
        ("tutor_house", 24, 4, {"door": dict(id="tutor_house", to="tutor_house", toId="door")}),
        ("temple", 4, 3, {}),
        ("shop", 10, 4, {"w": 4, "sign": "SILKS", "awning": "pink"}),
        ("shop", 32, 8, {"w": 4, "sign": "FLOWERS", "awning": "yellow"}),
        ("darshini", 4, 19, {"door": dict(id="darshini", to="darshini", toId="exit", setReturn=True)}),
        ("kirana", 10, 19, {"door": dict(id="kirana", to="kirana", toId="exit", setReturn=True)}),
        ("metro_station", 4, 23, {}),
    ],
    exits=[dict(side="S", **{"from": 18, "to_": 19}, map="sankey_tank"),
           dict(side="E", **{"from": 14, "to_": 15}, map="palace_road")],
    warps=[warp("metro", 9, 29, None, exit="UP", mode="arrive")],
    signs=[dict(x=20, y=11, text="8TH CROSS, MALLESHWARAM - Jasmine, silks, filter coffee. Arena of Leader Vidya: Room 2, upstairs. (It's the whole house.)"),
           dict(x=3, y=12, text="KADU MALLESHWARA TEMPLE - Old as the hills. Quiet, please.")],
    npcs=[
        metro_staff("metro_ml", 8, 28, "Malleshwaram"),
        npc("ml_guard", 38, 14, "area_boi", facing="LEFT", hideIf={"badge": "MIND"}, script=[
            say("Boss, road closed. Film shooting is going on. Only Arena champions get through, that's the rule.",
                "Vidya ma'am's tuition house is right here. Pass her test first, then come.", speaker="Area Boi")]),
        npc("ml_guard2", 38, 15, "area_boi2", facing="LEFT", hideIf={"badge": "MIND"}, script=[
            say("Which film? Can't tell, guru. ...Okay fine, it's a ghost movie. Don't tell anyone, scene aagutte.",
                speaker="Area Boi")]),
        npc("ml_flower", 33, 13, "woman4", facing="DOWN", script=[
            say("Mallige! Fresh mallige! A string of jasmine for your hair? For your Urumon's hair?")]),
        npc("ml_student", 21, 17, "schoolgirl", movement="WANDER", script=[
            say("Vidya ma'am gives surprise tests. On Sundays. During festivals.")]),
        trainer("t_ml_college", 30, 17, "college_f", "ml_college", facing="LEFT", sight=4),
        trainer("t_ml_kid", 26, 22, "schoolboy", "ml_kid", facing="UP", sight=3),
    ],
    items=[dict(id="chakli1", x=36, y=27, item="Chakli"), dict(id="mudde1", x=37, y=4, item="Ragi Mudde")],
))

c, walls = room(13, 13, "w", exit_x=6, wall="wood")
MAPS.append(dict(
    id="tutor_house", name="Vidya's Tuition House", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="wood_floor",
    props=[("desk", 1, 4), ("desk", 4, 4), ("desk", 8, 4), ("desk", 10, 4), ("desk", 1, 7), ("desk", 4, 7), ("desk", 8, 7),
           ("desk", 10, 7), ("bookshelf", 0, 2), ("bookshelf", 12, 2), ("plant_pot", 0, 11)],
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
W, H = 42, 36
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"W": [(14, 15)], "N": [(19, 20)]})
c.fill(0, 14, 42, 2, "=").fill(0, 14, 42, 1, "-")
c.fill(19, 0, 2, 16, "_")
c.fill(14, 16, 14, 10, "_")
c.fill(4, 20, 8, 8, '"')
c.fill(30, 20, 8, 8, '"')
c.fill(4, 3, 10, 8, '"')
c.fill(28, 3, 10, 8, '"')
c.set(4, 30, "Y").set(36, 30, "Y").set(14, 29, "R").set(24, 29, "R")
MAPS.append(dict(
    id="palace_road", name="Palace Road", music="MUSIC_ROUTE", environment="park",
    layout=c.layout(),
    buildings=[("palace", 16, 17, {"door": dict(id="palace", to="palace", toId="door")})],
    exits=[dict(side="W", **{"from": 14, "to_": 15}, map="malleshwaram"),
           dict(side="N", **{"from": 19, "to_": 20}, map="hebbal")],
    signs=[dict(x=17, y=13, text="BANGALORE PALACE - Built to look like a castle in England. Now home to a spirited Arena. Literally."),
           dict(x=22, y=2, text="NORTH: Hebbal and the road to Nandi Hills.")],
    npcs=[
        trainer("t_pr_cricketer", 8, 12, "cricketer", "pr_cricketer", facing="RIGHT", sight=4),
        trainer("t_pr_dancer", 33, 12, "dancer", "pr_dancer", facing="LEFT", sight=4),
        npc("pr_mahout", 36, 17, "man2", facing="LEFT", script=[
            say("I look after the palace elephants. Aanemari love a bath in the afternoon.",
                "In the old days they carried golden howdahs in the autumn procession.")]),
        npc("pr_guard", 19, 2, "area_boi", facing="DOWN", hideIf={"badge": "SPIRIT"}, script=[
            say("No going north, macha. The palace ghosts are full active these days. Even our gang won't ride past at night.",
                "Win at the palace Arena and calm them down. Then we'll move our bikes.", speaker="Area Boi")]),
        npc("pr_guard2", 20, 2, "area_boi2", facing="DOWN", hideIf={"badge": "SPIRIT"}, script=[
            say("Last night someone laughed in the palace corridor. Nobody was there.",
                "I'm not scared, okay? I'm just... standing here. Guarding.", speaker="Area Boi")]),
        npc("rohan_pr", 21, 7, "rival", facing="DOWN", showIf={"badge": "SPIRIT"}, hideIf="RIVAL4_DONE", script=[]),
    ],
    triggers=[dict(id="rival4", once=False, x=19, y=9, w=2, h=4, requires={"badge": "SPIRIT"}, unless="RIVAL4_DONE", script=[
        {"exclaim": "rohan_pr"},
        {"npcToPlayer": "rohan_pr"},
        {"battle": {"trainer": "rival_palace", "id": "rohan_pr"}},
        say("Grandma called. Something big is happening at Nandi Hills at sunrise.",
            "The Syndicate's boss is going after the Garden City's guardian - Udyanaga.",
            "Go through Hebbal and climb the hill. The only way to the summit is through the old cave. Hurry!", speaker="Sudeep"),
        {"npcWalk": {"id": "rohan_pr", "steps": ["UP", "UP", "UP", "UP", "UP", "UP", "UP", "UP"], "ghost": True}},
        {"npcHide": "rohan_pr"},
        {"setFlag": "RIVAL4_DONE"},
    ])],
    items=[dict(id="pak1", x=5, y=4, item="Mysore Pak", qty=2), dict(id="tiffin1", x=37, y=26, item="Tiffin Carrier")],
))

c, walls = room(17, 15, "o", exit_x=8, wall="palace")
c.fill(2, 4, 1, 8, "c").fill(14, 4, 1, 8, "c").fill(7, 3, 3, 11, "c")
MAPS.append(dict(
    id="palace", name="Bangalore Palace Arena", music="MUSIC_ARENA", interior=True, environment="arena",
    layout=c.layout(), walls=walls, ground="stone_floor",
    props=[("statue", 4, 3), ("statue", 12, 3), ("statue", 4, 9), ("statue", 12, 9), ("pooja_shelf", 1, 2),
           ("pooja_shelf", 15, 2), ("plant_pot", 0, 13), ("plant_pot", 16, 13), ("sofa", 1, 6), ("sofa", 14, 6)],
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
W, H = 28, 46
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(19, 20)], "N": [(12, 13)]})
c.fill(19, 30, 2, 16, "=").fill(19, 30, 1, 16, "|")
c.fill(12, 28, 9, 3, "=")
c.fill(12, 0, 2, 31, "=").fill(12, 0, 1, 31, "|")
c.fill(2, 8, 8, 16, "~")
c.fill(3, 7, 6, 1, "~").fill(3, 24, 6, 1, "~")
c.fill(15, 4, 9, 10, '"')
c.fill(15, 18, 9, 8, '"')
c.fill(2, 32, 14, 8, '"')
MAPS.append(dict(
    id="hebbal", name="Route 7 - Hebbal", music="MUSIC_ROUTE", environment="lake",
    layout=c.layout(),
    props=[("lamp_post", 11, 10), ("lamp_post", 11, 20), ("lamp_post", 14, 15), ("bus_stop", 21, 36)],
    exits=[dict(side="S", **{"from": 19, "to_": 20}, map="palace_road"),
           dict(side="N", **{"from": 12, "to_": 13}, map="nandi_hills")],
    signs=[dict(x=21, y=42, text="HEBBAL FLYOVER - The gateway to the north. Nandi Hills: 50 km."),
           dict(x=10, y=26, text="HEBBAL LAKE - Pelicans, painted storks, and occasionally a very confused Meenaga.")],
    npcs=[
        trainer("t_hb_rider", 21, 26, "delivery_rider", "hb_rider", facing="LEFT", sight=4),
        trainer("t_hb_wrestler", 14, 34, "wrestler", "hb_wrestler", facing="DOWN", sight=3),
        trainer("t_hb_fisher", 10, 13, "fisher", "hb_fisher", facing="RIGHT", sight=2),
        npc("hb_walker", 17, 2, "man3", facing="DOWN", script=[
            say("I saw trucks with hard-hat people heading up to Nandi Hills before dawn.", "Hope they're just tourists...")]),
    ],
    items=[dict(id="mudde1", x=3, y=38, item="Ragi Mudde"), dict(id="dosa1", x=23, y=5, item="Masala Dosa", qty=3)],
))

# ---------------------------------------------------------------------------------------------
# Nandi Hills (lower slope + summit, linked only through the cave)
# ---------------------------------------------------------------------------------------------
W, H = 36, 48
c = Canvas(W, H, ".")
c.tree_border("T", gaps={"S": [(12, 13)]})
c.fill(0, 22, 36, 3, "#")                  # cliff band splitting the hill
c.fill(12, 38, 2, 10, ":")
c.fill(12, 38, 14, 2, ":")
c.fill(24, 30, 2, 10, ":")
c.fill(8, 30, 18, 2, ":")
c.fill(8, 26, 2, 6, ":")
c.fill(3, 33, 8, 4, '"').fill(16, 33, 7, 4, '"').fill(27, 33, 6, 6, '"').fill(3, 41, 8, 4, '"')
c.set(28, 41, "O").set(31, 27, "O").set(15, 41, "r").set(20, 27, "r").set(3, 27, "O")
# summit
c.fill(5, 17, 2, 4, ":")
c.fill(5, 15, 24, 2, ":")
c.fill(16, 8, 2, 8, ":")
c.fill(26, 4, 2, 12, ":")
c.fill(3, 4, 8, 8, '"').fill(20, 10, 6, 4, '"')
c.fill(29, 2, 5, 3, "_")                  # Tipu's Drop viewpoint
c.set(31, 9, "O").set(2, 15, "O")
c.set(5, 20, "S")                         # stairs down into the cave
MAPS.append(dict(
    id="nandi_hills", name="Nandi Hills", music="MUSIC_CAVE", environment="hill", cliffGround="dirt",
    layout=c.layout(),
    buildings=[("cave_entrance", 7, 25, {"door": dict(id="cave_s", to="nandi_cave", toId="south")}),
               ("hill_pavilion", 14, 3, {"door": dict(id="pavilion", to="hill_pavilion", toId="door")})],
    exits=[dict(side="S", **{"from": 12, "to_": 13}, map="hebbal")],
    warps=[warp("cave_n", 5, 20, "nandi_cave", "north", exit="UP", mode="step")],
    signs=[dict(x=14, y=44, text="NANDI HILLS - 1,478 m. Sunrise point at the summit. Please carry your own water."),
           dict(x=30, y=6, text="TIPU'S DROP - A sheer cliff with a view over the whole Deccan plateau."),
           dict(x=11, y=29, text="OLD CAVE - The only path to the summit since the landslide. Bring a torch.")],
    npcs=[
        trainer("t_nh_bird", 20, 36, "birdwatcher", "nh_bird", facing="LEFT", sight=4),
        trainer("t_nh_wrestler", 25, 29, "wrestler", "nh_wrestler", facing="DOWN", sight=3),
        npc("nh_monkey_man", 6, 40, "man4", facing="RIGHT", script=[
            say("A Mangaa stole my sunglasses. Then it came back for my sandwich. Then my dignity.")]),
        npc("nh_prof", 18, 14, "professor", facing="DOWN", showIf="NANDI_DONE", hideIf="UDYANAGA_SEEN", script=[
            say("{PLAYER}! You did it! Bhaskar's crew is scattering down the hill.",
                "Look - the mist at Tipu's Drop is glowing. The guardian is waking up.",
                "Go to the viewpoint. Udyanaga only shows itself to those who protect the city.", speaker="Prof. Sharada")]),
    ],
    triggers=[dict(id="udyanaga", x=29, y=2, w=5, h=3, once=False, requires="NANDI_DONE", unless="UDYANAGA_DONE", script=[
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
    items=[dict(id="mudde1", x=33, y=44, item="Ragi Mudde"), dict(id="pak1", x=4, y=8, item="Mysore Pak", qty=2),
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
MAPS.append(dict(
    id="nandi_cave", name="Nandi Cave", music="MUSIC_CAVE", environment="cave", interior=True,
    layout=c.layout(), ground="cave_floor", caveEncounters=True, cliffGround="cave_floor",
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
    props=[("crate", 11, 4), ("crate", 12, 4), ("stalagmite", 5, 10), ("stalagmite", 25, 16), ("crate", 20, 19)],
    items=[dict(id="elaneer1", x=13, y=15, item="Elaneer", qty=2), dict(id="bath1", x=25, y=4, item="Bisi Bele Bath", qty=2)],
))

c, walls = room(13, 13, "o", exit_x=6, wall="cave")
MAPS.append(dict(
    id="hill_pavilion", name="Hill Pavilion Arena", music="MUSIC_ARENA", interior=True, environment="hill",
    layout=c.layout(), walls=walls, ground="stone_floor",
    props=[("statue", 2, 3), ("statue", 10, 3), ("plant_pot", 0, 11), ("plant_pot", 12, 11), ("rock", 3, 8), ("rock", 9, 8)],
    warps=[warp("door", 6, 12, "nandi_hills", "pavilion", exit="UP", dir="DOWN")],
    npcs=[
        trainer("hp_leader", 6, 2, "akash", "leader_akash", sight=0),
        trainer("hp_t1", 2, 6, "birdwatcher", "ar_pavilion1", facing="RIGHT", sight=3),
        trainer("hp_t2", 10, 9, "jogger", "ar_pavilion2", facing="LEFT", sight=3),
        npc("hp_guide", 8, 11, "arena_guide", facing="LEFT", script=[
            say("Akash flies SKY Urumon. ELECTRIC and ROCK moves will bring them down to earth!")]),
    ],
))
