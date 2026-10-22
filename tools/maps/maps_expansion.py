"""Side areas added in the expansion: Bannerghatta Forest (south of Basavanagudi, open once you have a partner),
Ramanagara Rocks (west along Mysuru Road, post-game) and Kokkare Bellur (the stork village beyond the rocks)."""
from dsl import Canvas, Props, npc, say
from expansion_scripts import bisilu

MAPS = []

# ---------------------------------------------------------------------------------------------
# Bannerghatta Forest
# ---------------------------------------------------------------------------------------------
W, H = 34, 46
c = Canvas(W, H, "@")
pr = Props()
# the trail in from Basavanagudi, past the forest checkpost and the ranger's hut
c.fill(15, 0, 2, 34, "L").fill(9, 3, 16, 7, ".").fill(15, 3, 2, 7, "L").fill(17, 6, 4, 1, "L")
# grass pockets either side of the trail
c.blob(2, 10, 13, 9, '"', 11, rough=0.35).fill(14, 13, 1, 2, ".").blob(18, 10, 14, 9, '"', 12, rough=0.35).fill(17, 14, 2, 1, ".")
c.fill(3, 11, 2, 2, ".").fill(29, 11, 2, 1, ".")
# the stream: stepping stones where the trail crosses
c.fill(2, 19, 30, 3, "~").blob(2, 17, 9, 4, "~", 5).blob(23, 20, 9, 5, "~", 6)
c.fill(8, 18, 7, 1, ".").fill(17, 18, 9, 1, ".").fill(2, 22, 13, 1, ".").fill(17, 22, 9, 1, ".").fill(15, 19, 2, 3, "+")
# south of the stream: a meadow, and a granite outcrop with a view over the canopy
c.blob(2, 23, 13, 11, '"', 13, rough=0.3).fill(14, 26, 1, 2, ".").fill(17, 23, 15, 11, ".")
c.text(19, 24, """
     !!!!
  !!!!ii!!!
 !!iiiiiii!!
 !iiiiiiiii!!
!!!iiiiii!!!
  !!!!SS!!!
     !SS!""")
c.blob(26, 31, 6, 3, '"', 4, only=".")
# the sacred grove at the end of the trail: an old banyan, snake stones, a forest pond
c.fill(5, 34, 24, 10, ".").blob(17, 37, 9, 6, "~", 2, rough=0.2).blob(5, 37, 9, 7, '"', 3, only=".")
pr.put("jeep_side", 10, 7).put("cone", 14, 3).put("cone", 17, 3).put("termite_mound", 23, 8).put("bamboo", 9, 3)
pr.put("log", 22, 5).put("mushrooms", 12, 5).put("leaves", 15, 8).put("leaves", 16, 12).put("leaves", 15, 27)
pr.put("bamboo", 6, 12).put("bamboo", 10, 15).put("termite_mound", 12, 12).put("rock", 4, 16)
pr.put("boulder", 25, 12).put("rock", 21, 16).put("thorn_bush", 28, 15).put("bamboo", 29, 12)
pr.put("log", 22, 20).put("reeds", 8, 18).put("reeds", 25, 18).put("reeds", 3, 22).put("lily_pads", 10, 20)
pr.put("termite_mound", 8, 26).put("termite_mound", 12, 30).put("log", 4, 28).put("mushrooms", 6, 31)
pr.put("eucalyptus", 17, 24).put("rock", 31, 27).put("boulder", 18, 31).put("bush_tall", 31, 23)
pr.put("banyan", 8, 34).put("naga_stones", 12, 35).put("shrine", 14, 34).put("lotus", 20, 39).put("ducks", 22, 40)
pr.put("reeds", 17, 38).put("mushrooms", 26, 36).put("stump", 27, 40).put("bamboo", 25, 42)

MAPS.append(dict(
    id="bannerghatta", name="Bannerghatta Forest", music="MUSIC_ROUTE", environment="grass",
    layout=c.layout(), props=pr, rockGround="forest_floor",
    forestKinds=["tree_dark", "tree", "mango", "tree_dark", "tree_olive"], forestFillers=["bush_tall", "ashoka"],
    buildings=[("ranger_hut", 18, 3, {})],
    exits=[dict(side="N", **{"from": 15, "to_": 16}, map="basavanagudi")],
    signs=[dict(x=13, y=2, style="forest", text="BANNERGHATTA FOREST - Elephant corridor. Walk, don't run. And definitely don't honk."),
           dict(x=14, y=17, style="forest", text="STREAM AHEAD. Stepping stones are slippery. So are the Urumon."),
           dict(x=23, y=30, style="stone", text="A view over the canopy. On a clear day you can see Bengaluru. On most days you see haze.")],
    npcs=[
        npc("bg_ranger", 20, 7, "park_ranger", facing="DOWN", script=[
            say("Welcome to Bannerghatta. Stay on the trail and you'll be fine.",
                "Leopards, sloth bears, elephants... and Urumon. Mostly Urumon. They're the ones who bite.", speaker="Ranger")]),
        npc("bg_birder", 21, 18, "birdwatcher", facing="DOWN", script=[
            say("Shh. A paradise flycatcher. White, with a tail as long as a ribbon.", "...And it's gone. Story of my life.")]),
        npc("bg_tourist", 17, 31, "man3", facing="LEFT", script=[
            say("I followed the arrows to the safari. Turns out the arrows were just sticks.",
                "Do you know the way back? Asking for a friend. The friend is me.")]),
        npc("bg_botanist", 20, 35, "college_f", facing="DOWN", script=[
            say("Wild jamun, sandalwood, bamboo, and a hundred plants with no English names.",
                "The villagers know them all. I just have a very expensive notebook.")]),
    ],
    interactables=[dict(x=20, y=5, script=[say("Locked. A note on the door: 'On patrol. Back by tiffin time. Do NOT feed the elephants. - Ranger Thimmaiah'")])],
    items=[dict(id="bg_dabba", x=27, y=27, item="Dabba", qty=3), dict(id="bg_neem", x=3, y=12, item="Neem Paste"),
           dict(id="bg_elaneer", x=27, y=42, item="Elaneer", qty=2), dict(id="bg_coil", x=30, y=11, item="Mosquito Coil", qty=2)],
))

# ---------------------------------------------------------------------------------------------
# Ramanagara Rocks
# ---------------------------------------------------------------------------------------------
W, H = 44, 34
c = Canvas(W, H, "y")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# old Mysuru Road, dusty and winding round a pile of boulders
c.fill(0, 15, 16, 2, ":").fill(14, 15, 2, 6, ":").fill(14, 19, 14, 2, ":").fill(26, 15, 2, 6, ":").fill(26, 15, 18, 2, ":")
# Ramadevara Betta: a granite dome with a walkable summit, steps cut into its east shoulder
c.text(12, 2, """
      !!!!!!!!!
    !!!!iiiii!!!!
  !!!iiiiiiiiiii!!!
 !!iiiiiiiiiiiiiii!!
!!iiiiiiiiiiiiiiiii!!
!!!iiiiiiiiiiiiiii!!!
 !!!iiiiiiiiiiiiiii!
  !!!!!iiiiiiii!!SS!
    !!!!!!!!!!!!!SS!
       !!!!!!!!!!SS!""")
c.fill(29, 12, 2, 3, ":")
# a pile of boulders the road has to go round
c.blob(16, 13, 10, 6, "!", 3, rough=0.2)
# wild grass in the scrub
c.blob(2, 2, 10, 11, "'", 1, only="y").blob(16, 22, 11, 9, "'", 2, only="y").blob(29, 26, 12, 6, "'", 4, only="y")
c.blob(30, 3, 6, 8, "'", 6, only="y")
# the ruined temple gallery of the Yali pillars, with its open courtyard
c.fill(5, 26, 9, 4, "Q").fill(13, 21, 2, 5, ":")
pr.put("broken_pillar", 5, 27).put("broken_pillar", 12, 29).put("fallen_slab", 6, 29).put("yali_pillar", 4, 23)
pr.put("yali_pillar", 15, 23).put("rubble", 7, 26).put("rubble", 11, 29).put("rubble", 5, 29).put("pebbles", 12, 26)
# the silk-cocoon trader's camp
pr.put("sack", 31, 25, grain="#f6f2ea").put("sack", 35, 25, grain="#f6f2ea").put("sack", 36, 25, grain="#f6f2ea")
pr.put("weighing_scale", 31, 26).put("hens", 36, 27)
# scrub
for name, x, y in (("thorn_bush", 3, 18), ("thorn_bush", 10, 20), ("thorn_bush", 38, 8), ("thorn_bush", 36, 19),
                   ("euphorbia", 5, 13), ("euphorbia", 39, 11), ("euphorbia", 33, 29), ("euphorbia", 2, 24),
                   ("rock", 12, 13), ("rock", 40, 22), ("rock", 2, 29), ("termite_mound", 7, 18), ("boulder", 36, 2),
                   ("boulder", 38, 12), ("boulder", 20, 30), ("boulder_big", 2, 20), ("boulder_big", 39, 3),
                   ("thorn_bush", 24, 11), ("rock", 9, 3), ("termite_mound", 34, 9), ("tree_olive", 33, 12),
                   ("thorn_bush", 6, 22), ("rock", 14, 9), ("thorn_bush", 29, 21), ("euphorbia", 24, 26), ("rock", 37, 28),
                   ("thorn_bush", 9, 31), ("pebbles", 20, 17), ("pebbles", 33, 17), ("thorn_bush", 41, 25), ("tree_olive", 3, 9)):
    pr.put(name, x, y)
pr.put("boulder_big", 17, 14).put("boulder_big", 22, 14)
# on the summit: the hottest rock in Karnataka, a tiny shrine, offerings
pr.put("boulder_big", 20, 4).put("shrine", 26, 4).put("rock", 16, 6).put("thorn_bush", 27, 7).put("pebbles", 23, 7)

MAPS.append(dict(
    id="ramanagara", name="Ramanagara Rocks", music="MUSIC_ROUTE", environment="hill",
    layout=c.layout(), props=pr, cliffGround="granite", rockGround="dry_grass",
    forestKinds=["tree_olive", "tree_olive", "tree", "tree_dark"], forestFillers=["euphorbia", "bush_tall"],
    buildings=[("yali_gallery", 6, 23, {}), ("village_hut", 32, 22, {"roof": "tile", "wall": "#d9b98a"})],
    exits=[dict(side="E", **{"from": 15, "to_": 16}, map="basavanagudi"),
           dict(side="W", **{"from": 15, "to_": 16}, map="kokkare_bellur")],
    signs=[dict(x=40, y=13, text="RAMANAGARA - Silk town of the south. These granite hills are older than the dinosaurs, and twice as grumpy."),
           dict(x=12, y=27, style="stone", text="THE YALI GALLERY. A temple hall older than anyone remembers. The stone lions are said to wake when the land needs them."),
           dict(x=18, y=8, style="stone", text="RAMADEVARA BETTA. The highest boulder bakes in the sun all year round. Villagers leave it buttermilk. It never says thank you.")],
    npcs=[
        npc("rm_climber", 31, 13, "jogger", facing="UP", script=[
            say("These rocks are two and a half billion years old. I'm climbing them in chappals.", "What could go wrong?")]),
        npc("rm_film", 8, 16, "man3", facing="UP", script=[
            say("They shot a famous bandit film on these very rocks, back in the seventies.",
                "Every boulder here thinks it's a movie star. That one over there won't stop posing.")]),
        npc("rm_silk", 34, 26, "woman2", facing="UP", script=[
            say("Silk cocoons, fresh from the farms! Ramanagara has the biggest cocoon market in the country.",
                "The silkworms do all the work. I just do the shouting.")]),
        npc("rm_vulture", 25, 6, "birdwatcher", facing="LEFT", script=[
            say("Long-billed vultures nest on these cliffs. One of the last places in the world they still do.",
                "Ugly? Maybe. But they keep the land clean. Respect the vulture.")]),
    ],
    interactables=[bisilu(21, 6)],
    items=[dict(id="rm_pak", x=4, y=4, item="Mysore Pak", qty=2), dict(id="rm_sdabba", x=28, y=5, item="Steel Dabba", qty=3),
           dict(id="rm_tiffin", x=40, y=30, item="Tiffin Carrier")],
))

# ---------------------------------------------------------------------------------------------
# Kokkare Bellur
# ---------------------------------------------------------------------------------------------
W, H = 38, 32
c = Canvas(W, H, ".")
pr = Props()
c.fill(0, 0, W, 2, "@").fill(0, H - 2, W, 2, "@").fill(0, 0, 2, H, "@").fill(W - 2, 0, 2, H, "@")
# red-earth village lanes: the road in from Ramanagara, and a lane through the village
c.fill(2, 15, 36, 2, "e").fill(18, 3, 2, 26, "e")
# paddy fields with walkable bunds
c.fill(3, 18, 14, 11, "I").fill(3, 23, 14, 1, ":").fill(9, 18, 2, 11, ":")
# the village pond: ghat steps on the north bank, a little jetty from the west bank
c.blob(22, 18, 12, 10, "~", 3, rough=0.15)
for x in range(25, 30):
    top = next(yy for yy in range(16, 28) if c.get(x, yy) == "~")
    c.set(x, top - 1, "D")
c.fill(21, 23, 5, 1, "b")
# a field of wild grass beyond the huts
c.blob(29, 2, 7, 11, '"', 5, only=".")
# nesting trees full of pelicans and painted storks
for x, y in ((3, 4), (8, 3), (24, 3), (33, 19), (20, 25)):
    pr.put("nest_tree", x, y)
# huts with storks on the roofs
for x, y in ((3, 9), (8, 10), (12, 5), (26, 8)):
    pr.put("roof_birds", x, y, _z=400)
pr.put("well", 14, 10).put("tulasi_katte", 12, 12).put("haystack", 6, 12).put("haystack", 15, 2).put("hens", 5, 13)
pr.put("cow", 13, 14).put("clothes_line", 9, 7).put("rangoli", 4, 12).put("rangoli", 10, 13).put("rangoli", 14, 8)
pr.put("tree_katte", 21, 10).put("shrine", 24, 11).put("buffalo", 31, 13).put("haystack", 34, 14).put("bench_stone", 22, 13)
pr.put("pelican", 21, 19).put("stork", 34, 24).put("pelican", 33, 26).put("stork", 22, 28).put("ducks", 27, 21)
pr.put("lotus", 30, 24).put("lily_pads", 24, 26).put("reeds", 21, 21).put("reeds", 34, 22).put("boat", 29, 19)
pr.put("hens", 17, 28).put("petals", 2, 27)

MAPS.append(dict(
    id="kokkare_bellur", name="Kokkare Bellur", music="MUSIC_TOWN", environment="lake",
    layout=c.layout(), props=pr, waterBank="dirt", forestKinds=["tree", "mango", "tree_dark", "tree_olive"],
    buildings=[("village_hut", 3, 9, {"roof": "thatch"}), ("village_hut", 8, 10, {"w": 4, "roof": "tile", "wall": "#e6cfa0"}),
               ("old_house", 12, 5, {"w": 5, "wall": "#efe3c8"}), ("village_hut", 26, 8, {"roof": "thatch", "wall": "#d9b98a"})],
    exits=[dict(side="E", **{"from": 15, "to_": 16}, map="ramanagara")],
    signs=[dict(x=34, y=17, text="KOKKARE BELLUR - Village of the storks. Please don't disturb the nests, or the grandmothers."),
           dict(x=21, y=17, style="board", text="NESTING SEASON: December to May. Pelicans and painted storks fish in this pond every day. Keep your Urumon calm.")],
    npcs=[
        npc("kb_ajji", 7, 14, "ajji", facing="DOWN", script=[
            say("The kokkare come every winter and nest on our roofs. We never chase them away.",
                "They bring luck, and their droppings make the best fertiliser in Karnataka. Both are true!")]),
        npc("kb_farmer", 9, 21, "man2", facing="DOWN", script=[
            say("Ragi on the high fields, paddy down here. The storks walk behind my plough and eat the frogs.",
                "Free pest control. The government should give them a salary.")]),
        npc("kb_kid", 20, 13, "kid1", movement="WANDER", wanderRadius=1, script=[
            say("I counted forty-two pelicans this morning! Then one sat on my head and I lost count.")]),
        npc("kb_volunteer", 24, 16, "college_f", facing="DOWN", script=[
            say("I'm counting nests for the bird survey. The village does most of the work, honestly.",
                "Nobody here has ever chased a stork off a roof. That's why they keep coming back.")]),
        npc("kb_fisher", 25, 23, "fisher", facing="RIGHT", script=[
            say("The pelicans and I fish the same pond. They're better at it. I've made my peace with that.")]),
    ],
    items=[dict(id="kb_elaneer", x=2, y=13, item="Elaneer", qty=2), dict(id="kb_mudde", x=34, y=11, item="Ragi Mudde")],
))
