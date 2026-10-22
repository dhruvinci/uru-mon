"""Proposal: growing the roster from 65 to 150 Urumon and bringing back the four missing types.

Nothing here is in the game yet. The review site (tools/review/) renders this file, with the type balance computed
from it, so the user can note on each family before anything is built. When building, each family turns into
species_data.py entries, art prompts, learnsets and encounter slots.

Stage tuple: (name, types, evolves at level or None, rough base-stat total).
Habitat: where it's found. "new:" marks an area that doesn't exist yet.
"""

# The four types the original 14 left out, renamed in the same spirit as SKY / TOXIC / MIND / SPIRIT.
NEW_TYPES = {
    "FROST": ("Ice", "Hailstorms, AC-chilled tech parks, Corner House ice cream, Nandi Hills winter fog. Brings back a freeze status."),
    "MYTH": ("Dragon", "Karnataka's temple beasts: Yali on the pillars, Makara on the arches, the two-headed Gandaberunda of the state emblem."),
    "ROGUE": ("Dark", "Night creatures and street smarts: stray-dog gangs, drain bandicoots, fruit bats, leopards on the city's edge."),
    "CHARM": ("Fairy", "Jasmine, rangoli, Dasara dolls, honey, ice cream: the sweet and pretty side of the city."),
}

# Existing Urumon whose concept already fits a new type.
RETYPES = {
    64: (["GRASS", "SKY"], ["GRASS", "MYTH"], "Udyanaga is already drawn as a garden dragon."),
    44: (["TOXIC"], ["TOXIC", "MYTH"], "Nagarahaavu is the cobra of naga-stone lore."),
    33: (["SPIRIT"], ["SPIRIT", "ROGUE"], "Kaalbekku is a black cat: the classic night prowler."),
    42: (["SKY", "MIND"], ["SKY", "CHARM"], "Navilu is a peacock; beauty over brains."),
    39: (["MIND", "ROCK"], ["MIND", "CHARM"], "Chintamani is a wish-granting jewel."),
    57: (["METAL", "ELECTRIC"], ["METAL", "MYTH"], "Metrovaha is drawn as a sleek metal dragon; also eases METAL's crowding."),
}

# Families. Each: key, role, concept, Bengaluru angle, habitat, stages.
FAMILIES = [
    # --- legendaries and mythicals ------------------------------------------------------------------------
    dict(key="gandaberunda", role="Legendary", concept="The two-headed eagle of Karnataka's state emblem, woken when you become Champion.",
         angle="Gandaberunda is on the state seal above Vidhana Soudha's doors.", habitat=["vidhana_soudha (post-game, on the dome)"],
         stages=[("Gandaberunda", ["SKY", "MYTH"], None, 580)]),
    dict(key="bisilu", role="Legendary (season trio)", concept="Summer: a sun-baked granite lion whose mane shimmers like heat haze.",
         angle="April on the Deccan plateau; the bare granite hills of Ramanagara.", habitat=["new: Ramanagara rocks (post-game)"],
         stages=[("Bisilu", ["FIRE", "EARTH"], None, 570)]),
    dict(key="mungaru", role="Legendary (season trio)", concept="Monsoon: a storm-cloud elephant that trumpets thunder.",
         angle="Mungaru male, the southwest monsoon; old poems call rain clouds elephants.", habitat=["hebbal (post-game, during a storm)"],
         stages=[("Mungaru", ["WATER", "ELECTRIC"], None, 570)]),
    dict(key="chali", role="Legendary (season trio)", concept="Winter: a great hornbill made of morning fog that is only seen at sunrise.",
         angle="December fog at Nandi Hills; the hornbills of the Western Ghats.", habitat=["nandi_hills (post-game, at sunrise point)"],
         stages=[("Chali", ["FROST", "MIND"], None, 570)]),
    dict(key="bendakaalu", role="Mythical (No. 150)", concept="A tiny glowing boiled bean, the spirit the city is named after.",
         angle="The legend of 'Benda Kaalu Ooru', the town of boiled beans that became Bengaluru.",
         habitat=["basavanagudi (event: the groundnut fair, after completing the Pustaka)"],
         stages=[("Bendakaalu", ["CHARM", "MIND"], None, 560)]),

    # --- pseudo-legendary and other MYTH --------------------------------------------------------------------
    dict(key="yali", role="Rare three-stage (pseudo-legendary)", concept="Temple-pillar guardian: lion body, elephant trunk, horse legs, carved from granite.",
         angle="Yali pillars line Vijayanagara-era temples across Karnataka.", habitat=["nandi_cave (deep, rare)", "new: Ramanagara rocks"],
         stages=[("Yalimari", ["ROCK", "MYTH"], 30, 300), ("Yalikamba", ["ROCK", "MYTH"], 50, 420), ("Mahayali", ["MYTH", "ROCK"], None, 520)]),
    dict(key="makara", role="Rare", concept="Crocodile-elephant-fish beast from temple archways, living in the old tanks.",
         angle="The Makara torana arch over temple doorways; Sankey and Hebbal were once temple tanks.", habitat=["sankey_tank (fishing, rare)", "hebbal (fishing, rare)"],
         stages=[("Makaramari", ["WATER", "MYTH"], 35, 300), ("Makara", ["WATER", "MYTH"], None, 470)]),

    # --- fossils --------------------------------------------------------------------------------------------
    dict(key="paachi", role="Fossil", concept="A living stromatolite: a mossy dome of ancient algae that photosynthesises.",
         angle="Lalbagh's rock is about 3,000 million years old, among the oldest on Earth.", habitat=["Old Moss Stone in nandi_cave, revived at the lab"],
         stages=[("Paachikallu", ["ROCK", "GRASS"], 40, 320), ("Paachibande", ["ROCK", "GRASS"], None, 470)]),
    dict(key="kalluhula", role="Fossil", concept="A trilobite-like stone bug that rolls into a ball.",
         angle="Same ancient Lalbagh rock; the other fossil choice.", habitat=["Old Shell Stone in nandi_cave, revived at the lab"],
         stages=[("Kalluhula", ["ROCK", "BUG"], 40, 320), ("Kalluveera", ["ROCK", "BUG"], None, 470)]),

    # --- early commons --------------------------------------------------------------------------------------
    dict(key="naayi", role="Early common, three-stage", concept="Street puppy that grows into the leader of a neighbourhood dog pack.",
         angle="Bengaluru's famous street dogs, fed by every darshini and guarded by every aunty.", habitat=["route1", "basavanagudi", "mg_road"],
         stages=[("Naayimari", ["NORMAL"], 18, 220), ("Beedinaayi", ["NORMAL", "ROGUE"], 36, 340), ("Kaavalnaayi", ["ROGUE", "FIGHT"], None, 450)]),
    dict(key="gedalu", role="Early common, three-stage", concept="Termite that builds ever-bigger mud mounds; the final one is a walking anthill.",
         angle="The red-earth termite mounds (huttu) of the city's empty plots, sacred in naga lore.", habitat=["route1", "cubbon_park"],
         stages=[("Gedalu", ["BUG", "EARTH"], 14, 190), ("Huttuhula", ["BUG", "EARTH"], 32, 320), ("Huttappa", ["EARTH", "BUG"], None, 440)]),
    dict(key="kadale", role="Early common", concept="A peanut in its shell that buries itself; evolves into a whole groundnut plant.",
         angle="Basavanagudi's Kadalekai Parishe, the groundnut fair right next to the home town.", habitat=["basavanagudi (grass by Bugle Rock)", "route1"],
         stages=[("Kadale", ["GRASS"], 20, 230), ("Kadalekaayi", ["GRASS", "EARTH"], None, 400)]),
    dict(key="idli", role="Early common", concept="A fluffy steamed rice cake; the evolution is a stack on an idli plate.",
         angle="Breakfast at every darshini.", habitat=["route1", "lalbagh"],
         stages=[("Idlimari", ["NORMAL"], 24, 230), ("Thatteidli", ["NORMAL", "CHARM"], None, 400)]),
    dict(key="halli", role="Early common", concept="A house gecko whose chirps are said to predict the future.",
         angle="Halli shastra: a lizard chirping or falling on you is read as an omen.", habitat=["route1", "lalbagh", "malleshwaram"],
         stages=[("Halli", ["NORMAL"], 24, 220), ("Hallishastri", ["NORMAL", "MIND"], None, 400)]),

    # --- city and urban ------------------------------------------------------------------------------------
    dict(key="gundi", role="Common", concept="A pothole that wanders the roads; the evolution swallows scooters.",
         angle="Bengaluru potholes, a civic institution. Gives an EARTH option before the ELECTRIC Arena.", habitat=["mg_road", "silk_board"],
         stages=[("Gundi", ["EARTH"], 30, 250), ("Mahagundi", ["EARTH", "ROGUE"], None, 420)]),
    dict(key="heggana", role="Common", concept="A drain bandicoot that grows into a sewer brute.",
         angle="The giant bandicoots of the city's storm drains.", habitat=["mg_road", "silk_board", "whitefield"],
         stages=[("Heggana", ["ROGUE"], 28, 250), ("Hegganasura", ["ROGUE", "TOXIC"], None, 420)]),
    dict(key="kasa", role="Common", concept="A walking heap of mixed garbage that the BBMP truck keeps missing.",
         angle="The city's garbage crisis and the dream of segregated waste.", habitat=["silk_board", "whitefield", "bellandur"],
         stages=[("Kasa", ["TOXIC"], 30, 240), ("Kasaraashi", ["TOXIC", "ROGUE"], None, 420)]),
    dict(key="thandi", role="Common", concept="A runaway AC unit that blasts freezing air; evolves into a rooftop chiller.",
         angle="Whitefield tech parks kept at 18°C while it's 34°C outside.", habitat=["whitefield", "tech_park area"],
         stages=[("Thandi", ["FROST", "ELECTRIC"], 30, 260), ("Thandasura", ["FROST", "ELECTRIC"], None, 430)]),
    dict(key="istri", role="Common", concept="The charcoal iron box of the street-corner ironing cart, glowing coals and all.",
         angle="The istri-wala's pushcart on every residential street.", habitat=["malleshwaram", "basavanagudi"],
         stages=[("Istri", ["FIRE", "METAL"], 30, 260), ("Istriraaja", ["FIRE", "METAL"], None, 430)]),
    dict(key="pataaki", role="Three-stage", concept="A firecracker that grows from a cracker strip to a sutli to a sky rocket.",
         angle="Deepavali nights. Also gives an early FIRE catch, which the game lacks today.", habitat=["mg_road", "malleshwaram"],
         stages=[("Pataaki", ["FIRE"], 16, 210), ("Sutli", ["FIRE"], 34, 330), ("Rocketaaki", ["FIRE", "SKY"], None, 450)]),
    dict(key="kulfi", role="Common", concept="A kulfi on a stick that becomes a towering gadbad sundae.",
         angle="Ice-cream carts, Corner House and the Gadbad sundae.", habitat=["mg_road", "lalbagh"],
         stages=[("Kulfimari", ["FROST", "CHARM"], 30, 250), ("Gadbadu", ["FROST", "CHARM"], None, 420)]),
    dict(key="dosa", role="Uncommon single", concept="A butter dosa that flies like a carpet and trails ghee sparks.",
         angle="Benne dose from Davangere; the dosa institutions around Lalbagh.", habitat=["lalbagh (rare)"],
         stages=[("Bennedose", ["FIRE", "SKY"], None, 420)]),

    # --- parks, lakes and gardens ----------------------------------------------------------------------------
    dict(key="jenu", role="Common", concept="A rock bee that grows into a queen with a honeycomb crown.",
         angle="The huge rock-bee hives hanging from Vidhana Soudha and the Cubbon Park trees.", habitat=["cubbon_park", "vidhana_soudha grounds"],
         stages=[("Jenuhula", ["BUG"], 22, 220), ("Jenuraani", ["BUG", "CHARM"], None, 420)]),
    dict(key="minchu", role="Common", concept="A firefly whose tail flashes in Morse; the evolution lights up a whole lake shore.",
         angle="Fireflies along the city's last dark lake edges.", habitat=["cubbon_park", "sankey_tank"],
         stages=[("Minchuhula", ["BUG", "ELECTRIC"], 24, 230), ("Minchurani", ["BUG", "ELECTRIC"], None, 410)]),
    dict(key="signalu", role="Common", concept="A traffic signal stuck on red; the evolution runs a whole junction.",
         angle="Silk Board junction, where signals last long enough to evolve.", habitat=["silk_board", "mg_road"],
         stages=[("Signalu", ["ELECTRIC"], 28, 240), ("Signalappa", ["ELECTRIC", "NORMAL"], None, 420)]),
    dict(key="mallige", role="Common", concept="A jasmine-bud sprite; the evolution wears a whole Mysore mallige garland.",
         angle="Malleshwaram's flower sellers and the GI-tagged Mysore mallige.", habitat=["malleshwaram", "lalbagh"],
         stages=[("Mallige", ["GRASS", "CHARM"], 28, 240), ("Mysoremallige", ["GRASS", "CHARM"], None, 420)]),
    dict(key="taavare", role="Common", concept="A lotus bud floating on a lily pad that opens into a great pink lotus.",
         angle="Lotuses in Lalbagh lake and the old temple tanks.", habitat=["lalbagh (lake)", "sankey_tank (fishing)"],
         stages=[("Taavaremari", ["WATER", "GRASS"], 26, 240), ("Taavare", ["WATER", "GRASS"], None, 420)]),
    dict(key="kokkare", role="Common", concept="A pelican chick that grows into a painted stork.",
         angle="Kokkare Bellur, the village near Bengaluru where pelicans and painted storks nest on rooftops.", habitat=["hebbal", "new: Kokkare Bellur"],
         stages=[("Kokkare", ["WATER", "SKY"], 30, 250), ("Bannadakokkare", ["WATER", "SKY"], None, 430)]),
    dict(key="edi", role="Common", concept="A lake crab that boxes with oversized claws.",
         angle="The freshwater crabs of Bengaluru's lakes.", habitat=["bellandur (fishing)", "sankey_tank (fishing)", "hebbal (fishing)"],
         stages=[("Edi", ["WATER", "FIGHT"], 28, 250), ("Ediyodha", ["WATER", "FIGHT"], None, 430)]),
    dict(key="benkinore", role="Common", concept="Lake foam that caught fire; the evolution is a burning toxic cloud on the water.",
         angle="The real day Bellandur Lake caught fire.", habitat=["bellandur"],
         stages=[("Benkinore", ["TOXIC", "FIRE"], 30, 250), ("Kerebenki", ["TOXIC", "FIRE"], None, 430)]),
    dict(key="baavali", role="Common", concept="A fruit bat that hangs upside down and steals mangoes.",
         angle="The flying-fox colony roosting in Cubbon Park's old trees.", habitat=["cubbon_park", "palace_road"],
         stages=[("Baavali", ["ROGUE", "SKY"], 26, 230), ("Baavalasura", ["ROGUE", "SKY"], None, 420)]),
    dict(key="kaage", role="Common", concept="A crow that carries messages to the ancestors.",
         angle="Crows are fed rice for the ancestors during Pitru Paksha.", habitat=["basavanagudi", "palace_road"],
         stages=[("Kaage", ["SKY", "SPIRIT"], 30, 240), ("Kaageraaja", ["SKY", "SPIRIT"], None, 420)]),

    # --- old city, culture and folklore ---------------------------------------------------------------------
    dict(key="hunase", role="Common", concept="A tamarind sapling with drooping pods; the grown tree is haunted.",
         angle="Village lore says ghosts live in tamarind trees.", habitat=["palace_road", "nandi_hills"],
         stages=[("Hunase", ["GRASS", "SPIRIT"], 32, 250), ("Hunasemohini", ["GRASS", "SPIRIT"], None, 430)]),
    dict(key="togalu", role="Common", concept="A leather shadow puppet that comes alive by lamplight.",
         angle="Togalu gombeyata, Karnataka's leather shadow-puppet theatre.", habitat=["palace_road", "malleshwaram"],
         stages=[("Togalu", ["SPIRIT"], 30, 250), ("Togalugombe", ["SPIRIT", "CHARM"], None, 430)]),
    dict(key="gombe", role="Common", concept="A lacquered wooden doll that becomes the royal couple of a Dasara doll display.",
         angle="Channapatna toys and the Dasara bombe habba doll steps.", habitat=["palace_road", "malleshwaram"],
         stages=[("Gombe", ["CHARM"], 30, 250), ("Pattadagombe", ["CHARM", "MIND"], None, 430)]),
    dict(key="chukki", role="Common", concept="A grid of rangoli dots that draws itself into patterns.",
         angle="Morning rangoli outside Malleshwaram homes.", habitat=["malleshwaram"],
         stages=[("Chukki", ["CHARM"], 28, 240), ("Rangavalli", ["CHARM"], None, 420)]),
    dict(key="gandha", role="Uncommon", concept="A sandalwood sapling whose fragrance calms anyone nearby.",
         angle="Karnataka's sandalwood (and 'Sandalwood', the nickname of Kannada cinema).", habitat=["palace_road", "nandi_hills"],
         stages=[("Gandhamari", ["GRASS"], 32, 250), ("Shrigandha", ["GRASS", "MIND"], None, 430)]),
    dict(key="midathe", role="Common", concept="A grasshopper that plays cricket with its hind legs as bats.",
         angle="Cricket, the insect and the sport; gully cricket in every lane.", habitat=["silk_board", "stadium surroundings", "palace_road"],
         stages=[("Midathe", ["BUG", "FIGHT"], 28, 240), ("Mahamidathe", ["BUG", "FIGHT"], None, 430)]),
    dict(key="mungusi", role="Common", concept="A mongoose that boxes snakes; the evolution is a scarred champion.",
         angle="Mongooses in the scrub around the city. Gives FIGHT early, for the FIGHT and ROGUE matchups.", habitat=["cubbon_park", "route1 (rare)"],
         stages=[("Mungusi", ["FIGHT"], 30, 250), ("Mungusiveera", ["FIGHT"], None, 430)]),
    dict(key="tagaru", role="Common", concept="A fighting ram with festival-painted horns.",
         angle="Tagaru kaalaga, the ram fights of village fairs on the city's outskirts.", habitat=["hebbal", "nandi_hills"],
         stages=[("Tagaru", ["FIGHT"], 32, 260), ("Kaadutagaru", ["FIGHT", "EARTH"], None, 440)]),

    # --- hills, forests and cold ----------------------------------------------------------------------------
    dict(key="aalikallu", role="Common", concept="A hailstone that grew a face during a summer storm.",
         angle="Bengaluru's sudden April hailstorms.", habitat=["nandi_hills", "hebbal (rare)"],
         stages=[("Aalikallu", ["FROST", "ROCK"], 34, 260), ("Aalibande", ["FROST", "ROCK"], None, 440)]),
    dict(key="manju", role="Uncommon", concept="A wisp of morning fog that hides travellers.",
         angle="Nandi Hills sunrise above the clouds.", habitat=["nandi_hills", "nandi_cave (entrance)"],
         stages=[("Manju", ["FROST", "SPIRIT"], 36, 260), ("Manjumaaye", ["FROST", "SPIRIT"], None, 440)]),
    dict(key="chirate", role="Uncommon", concept="A leopard cub that becomes a silent night hunter.",
         angle="Leopards still roam Bannerghatta and Turahalli at the city's edge.", habitat=["nandi_hills", "new: Bannerghatta forest"],
         stages=[("Chiratemari", ["ROGUE"], 32, 260), ("Chirate", ["ROGUE"], None, 440)]),
    dict(key="kaadupaapa", role="Rare single", concept="A slender loris with enormous night-time eyes.",
         angle="'Kaadu paapa' (forest baby), the endangered slender loris of the Bengaluru region.", habitat=["new: Bannerghatta forest", "nandi_hills (rare)"],
         stages=[("Kaadupaapa", ["ROGUE", "CHARM"], None, 420)]),
]

# Good ideas that didn't make the 85: swap any of these in with a note.
IDEA_BANK = [
    ("Karadi", "Sloth bear of Karadi Betta and Bannerghatta", "NORMAL/FIGHT"),
    ("Kona / Kambala", "Racing buffalo of the Kambala mud races", "WATER/EARTH"),
    ("Doddaala", "The 400-year-old Big Banyan Tree outside the city", "GRASS/MIND"),
    ("Udaa", "Monitor lizard of the outskirts", "EARTH"),
    ("Thumbi", "Dragonfly with stained-glass wings, over Sankey Tank", "BUG/SKY"),
    ("Doddabassu", "A double-decker city bus (they ran until the 2000s)", "NORMAL/METAL"),
    ("Tankeru", "Water tanker of the 'tanker mafia'", "WATER/ROGUE"),
    ("JCB-ppa", "The beloved yellow excavator", "EARTH/METAL"),
    ("Maavu", "Raw mango from the Lalbagh Mango Mela", "GRASS"),
    ("Gili", "The street fortune-teller's card-picking parrot", "SKY/MIND"),
    ("Paarivaala", "City pigeon", "NORMAL/SKY"),
    ("Chippuhandi", "Indian pangolin", "ROCK/NORMAL"),
    ("Mahseer", "Golden mahseer of the Kaveri", "WATER/FIGHT"),
    ("Dollu", "A drum-bodied creature from Dollu Kunitha", "NORMAL/FIGHT"),
    ("Buguri", "A Channapatna spinning top", "NORMAL/METAL"),
    ("Kempegopura", "A watchtower golem from Kempegowda's four towers", "ROCK/MIND"),
    ("Kabbu", "Sugarcane-juice crusher", "GRASS/METAL"),
    ("Panipuri", "VV Puram food street", "WATER/FIRE"),
]

# Things the expansion needs besides the creatures themselves.
FEATURES = [
    ("types", "Add FROST, MYTH, ROGUE and CHARM to the type chart (the standard 18-type matchups), badges and colours."),
    ("freeze", "Bring back a freeze status for FROST moves (thaws 20% a turn, or when hit by FIRE)."),
    ("moves", "About 35 new moves: 7-8 each for the new types, plus signatures for the legendaries and the Yali line."),
    ("fishing", "A fishing rod key item (Gaala) and water encounters at Lalbagh, Bellandur, Sankey and Hebbal lakes."),
    ("fossils", "Two old stones in Nandi Cave; Prof. Sharada revives them at the lab."),
    ("areas", "Up to three new areas: Bannerghatta forest, Ramanagara rocks, Kokkare Bellur (optional; the roster fits existing maps without them)."),
    ("postgame", "Post-game legendaries: Gandaberunda on the Vidhana Soudha dome, the season trio, Bendakaalu at the groundnut fair."),
    ("pustaka", "Renumber the Pustaka by region so legendaries come last and the mythical is No. 150 (save data keeps working)."),
    ("trainers", "Refresh trainer teams with the new species; give each Arena Leader one new-type Urumon."),
    ("names", "Rename the Route 1 vendor 'Manju' and the schoolkid 'Chinnu' (both clash with Urumon names)."),
]

# Arena -> types that beat it (for the availability check on the review page).
ARENAS = [
    ("Hoovamma (GRASS)", "GRASS", ["route1", "lalbagh", "basavanagudi"]),
    ("Gundappa (FIGHT)", "FIGHT", ["cubbon_park", "mg_road"]),
    ("Tanvi (ELECTRIC)", "ELECTRIC", ["silk_board", "whitefield"]),
    ("Vidya (MIND)", "MIND", ["bellandur", "sankey_tank", "malleshwaram"]),
    ("Rukmini (SPIRIT)", "SPIRIT", ["palace_road"]),
    ("Akash (SKY)", "SKY", ["hebbal", "nandi_hills", "nandi_cave"]),
]

# Matchups added by the four new types (the standard 18-type chart). Rows are attacking types.
CHART_ADDITIONS = {
    "FIRE": {"FROST": 2, "MYTH": 0.5}, "WATER": {"MYTH": 0.5}, "GRASS": {"MYTH": 0.5}, "ELECTRIC": {"MYTH": 0.5},
    "ROCK": {"FROST": 2}, "BUG": {"ROGUE": 2, "CHARM": 0.5}, "TOXIC": {"CHARM": 2},
    "FIGHT": {"FROST": 2, "ROGUE": 2, "CHARM": 0.5}, "MIND": {"ROGUE": 0}, "SPIRIT": {"ROGUE": 0.5},
    "METAL": {"FROST": 2, "CHARM": 2}, "EARTH": {}, "SKY": {}, "NORMAL": {},
    "FROST": {"GRASS": 2, "EARTH": 2, "SKY": 2, "MYTH": 2, "FIRE": 0.5, "WATER": 0.5, "FROST": 0.5, "METAL": 0.5},
    "MYTH": {"MYTH": 2, "METAL": 0.5, "CHARM": 0},
    "ROGUE": {"MIND": 2, "SPIRIT": 2, "FIGHT": 0.5, "ROGUE": 0.5, "CHARM": 0.5},
    "CHARM": {"FIGHT": 2, "MYTH": 2, "ROGUE": 2, "FIRE": 0.5, "TOXIC": 0.5, "METAL": 0.5},
}
