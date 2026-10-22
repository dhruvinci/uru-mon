"""Species roster for uru-mon: the single source for game data and creature art prompts.

Fields: id, name, types, base stats (hp, atk, def, spc, spd), catch rate, base exp,
evolution (level, into id) or None, Uru-Pustaka entry, and the visual description used
for art generation.
"""

S = []


def sp(id, name, types, stats, catch, exp, evo, dex, look):
    S.append(dict(id=id, name=name, types=types, base=dict(zip(("hp", "atk", "def", "spc", "spd"), stats)),
                  catchRate=catch, baseExp=exp, evolution=evo, dex=dex, look=look))


# --- starters -----------------------------------------------------------------------------
sp(1, "Jakkafawn", ["GRASS"], (45, 49, 49, 60, 50), 45, 64, (16, 2),
   "Born each March when the jacaranda trees bloom. It naps under purple canopies on quiet streets.",
   "a small fawn with lavender-purple fur dotted with white spots shaped like tiny jacaranda flowers, a sprig of purple jacaranda blossoms sprouting between its little nubby antlers, big curious eyes, leaf-green hooves")
sp(2, "Jakkadeer", ["GRASS"], (60, 62, 63, 78, 65), 45, 142, (36, 3),
   "Its antlers flower year-round. Petals it sheds are said to cool the hottest summer pavements.",
   "a slender young deer with a lavender-purple coat, branching antlers covered in purple jacaranda blossoms, a mane of green feathery leaves along its neck, confident stance")
sp(3, "Jakkaranda", ["GRASS", "MIND"], (80, 82, 83, 100, 85), 45, 236, None,
   "When it walks the avenues at dawn, every jacaranda it passes bursts into bloom.",
   "a majestic stag whose huge antlers are a full canopy of purple jacaranda blossoms like a tree in bloom, glowing violet eyes, purple petals floating around its legs, regal and mystical")
sp(4, "Kaapup", ["FIRE"], (42, 56, 43, 55, 62), 45, 65, (16, 5),
   "The steel tumbler on its head is always warm. It follows the smell of fresh decoction for miles.",
   "a chubby brown puppy wearing a small shiny stainless-steel filter-coffee tumbler as a helmet, curly wisps of coffee steam rising from the tumbler, cream-colored belly like milk froth, a little flame-tipped tail")
sp(5, "Brewolf", ["FIRE"], (58, 72, 58, 70, 80), 45, 142, (36, 6),
   "It pours scalding steam from its shoulders. Darshini owners leave out a cup for it at closing time.",
   "a lean young wolf with dark coffee-brown fur and cream frothy chest fur, stainless steel tumbler-shaped armor pieces on its forelegs, steam and small flames curling off its shoulders, fierce amber eyes")
sp(6, "Kaapiraja", ["FIRE", "METAL"], (78, 98, 78, 90, 96), 45, 240, None,
   "Its steel crown is shaped like a coffee filter. Its roar smells of chicory and burnt sugar.",
   "a large powerful wolf king with deep coffee-brown fur, polished stainless steel armor shaped like a coffee filter and a davara bowl forming a crown and chest plate, a mane of roaring flames and steam, golden eyes")
sp(7, "Elanee", ["WATER"], (46, 48, 62, 52, 44), 45, 63, (16, 8),
   "Its shell is a tender coconut. It sips lake water through its straw and sprays it at bullies.",
   "a tiny round-bodied turtle with soft coral-pink skin and cream freckles, big friendly eyes, a rounded snout, no plants on its head, whose shell is a bright green tender coconut with the top sliced open and a striped paper straw sticking out like a snorkel, water droplets around it")
sp(8, "Kobbari", ["WATER"], (60, 63, 80, 65, 58), 45, 142, (36, 9),
   "Its husky shell has become tough and fibrous. It guards the steps of old temple tanks.",
   "a sturdy young turtle with deep coral-pink skin with cream wave-shaped stripes, a shell made of a hairy brown husked coconut with fibrous tufts, water splashing around its feet, determined look")
sp(9, "Kerekurma", ["WATER", "EARTH"], (82, 85, 102, 85, 72), 45, 239, None,
   "Old stories say the city's lakes were dug by its footsteps. A small island grows on its back.",
   "a giant old lake turtle with weathered coral-pink and stone-grey skin, its huge shell is an old stone lake embankment with carved temple-tank steps and a small shrine bell, waterfalls pouring off the shell edges into the water, wise old eyes")

# --- early birds & critters ---------------------------------------------------------------
sp(10, "Gubbi", ["NORMAL", "SKY"], (40, 45, 40, 35, 56), 255, 50, (18, 11),
   "Once seen on every balcony. It chirps loudest when someone puts out rice on a steel plate.",
   "a round fluffy house sparrow chick, brown and grey feathers, a black bib, tiny beak, puffed up and cheerful")
sp(11, "Haddu", ["NORMAL", "SKY"], (60, 65, 55, 50, 75), 120, 122, (36, 12),
   "It circles over the city on warm air rising from the roads, then dives to snatch snacks from hands.",
   "a sleek brown kite bird with a forked tail, sharp hooked yellow beak, wings spread mid-glide, keen eyes")
sp(12, "Hadduraja", ["NORMAL", "SKY"], (80, 90, 75, 70, 101), 45, 216, None,
   "Its chestnut wings span a whole street. It nests on the tallest temple tower in town.",
   "a large brahminy kite raptor with rich chestnut-brown wings, a clean white head and chest, a sharp yellow hooked beak, realistic bird proportions, no flames and no crest, talons outstretched, majestic gliding pose")
sp(13, "Alilu", ["NORMAL"], (30, 56, 35, 25, 72), 255, 51, (20, 14),
   "The three stripes on its back are said to be a blessing for helping build a bridge long ago.",
   "a small Indian palm squirrel with three white stripes on its grey-brown back, bushy tail, holding a peanut, alert and cheeky")
sp(14, "Alilord", ["NORMAL"], (55, 81, 60, 50, 97), 127, 145, None,
   "It rules its tree like a tiny king and defends it with a shield made from a peanut shell.",
   "a bigger confident squirrel standing upright like a little warrior, three glowing white stripes on its back, a huge fluffy tail, a peanut-shell shield")
sp(15, "Reshmite", ["BUG"], (45, 30, 35, 20, 45), 255, 39, (7, 16),
   "It eats only mulberry leaves. The thread it spins is softer than any machine-made silk.",
   "a small pale cream silkworm caterpillar with a soft segmented body, tiny silk threads trailing from its mouth, sitting on a mulberry leaf")
sp(16, "Koshoon", ["BUG"], (50, 20, 55, 25, 30), 120, 72, (10, 17),
   "It wraps itself in golden silk and dreams. Weavers wait patiently for it to wake.",
   "a shiny golden-yellow silk cocoon with two sleepy eyes peeking out, wrapped in shimmering silk threads")
sp(17, "Reshmoth", ["BUG", "SKY"], (70, 45, 50, 85, 70), 45, 160, None,
   "Its wings are patterned like a wedding saree. Its scales shimmer gold in lamplight.",
   "an elegant silk moth with large wings patterned like a rich silk saree, deep magenta with gold zari borders, feathery antennae, graceful")
sp(18, "Sollu", ["BUG", "TOXIC"], (40, 50, 30, 35, 60), 255, 52, (22, 19),
   "Swarms rise from still lake water at dusk. Its whine near your ear is impossible to ignore.",
   "a small annoying mosquito with a long needle nose, striped black and white legs, buzzing translucent wings, mischievous grin")
sp(19, "Sollasura", ["BUG", "TOXIC"], (65, 85, 50, 60, 90), 90, 159, None,
   "A tyrant of the monsoon. One bite and you'll scratch for a week.",
   "a big menacing mosquito demon with a dragonfly-like body, glowing red eyes, a needle proboscis, toxic green droplets, striped legs, small demon horns")
sp(20, "Hoge", ["TOXIC"], (40, 45, 65, 60, 35), 190, 68, (30, 21),
   "It is born from the exhaust of a thousand idling engines at red lights.",
   "a floating grey puff of exhaust smoke with angry little eyes and a coughing mouth, tiny swirling soot particles")
sp(21, "Smogasura", ["TOXIC"], (70, 70, 95, 90, 60), 60, 172, None,
   "It hangs over the worst junctions at rush hour. Its rumble sounds like a thousand horns.",
   "a large looming smog monster made of dark grey and sickly yellow exhaust clouds, tire-like rings around its body, a tailpipe mouth, menacing red eyes")
sp(22, "Norepuff", ["WATER", "TOXIC"], (50, 35, 45, 60, 45), 190, 66, (32, 23),
   "A clump of lake foam that came alive. Do not try to wash your hands in it.",
   "a small bubbly blob of white foam with cute eyes, soap bubbles and lake water, a slightly greenish tint")
sp(23, "Noreyaksha", ["WATER", "TOXIC"], (85, 65, 75, 100, 70), 60, 175, None,
   "It rises out of polluted lakes as a wall of foam. It only calms when the water is clean again.",
   "a towering foam spirit made of churning white toxic lake foam with a green glow, foam arms, a mask-like face, bubbles floating upward")
sp(24, "Meenu", ["WATER"], (20, 10, 55, 20, 80), 255, 20, (20, 25),
   "It can do almost nothing except flop. Lake anglers throw it back out of pity.",
   "a small clumsy grey-green lake tilapia fish with a lily pad stuck on its head like a hat, droopy whiskers, a worried face, flopping awkwardly on its side")
sp(25, "Meenaga", ["WATER", "SKY"], (95, 125, 79, 80, 81), 45, 214, None,
   "No one believes a Meenu becomes this until they see it rise roaring from the lake.",
   "a long graceful serpentine water naga with emerald-green and gold scales, a wide lotus-petal crest behind its head, long flowing fins like silk banners, coiled elegantly above rippling water, calm but powerful expression")
sp(26, "Bandekal", ["ROCK", "EARTH"], (40, 80, 100, 30, 20), 255, 60, (25, 27),
   "It sits so still on hillsides that people paint signs on it.",
   "a grumpy grey granite boulder creature with mossy patches, stubby rock arms and small legs, cracks forming its face")
sp(27, "Bandeyodha", ["ROCK", "EARTH"], (80, 110, 130, 55, 45), 45, 177, None,
   "Some say the old rocky hills around the city are sleeping Bandeyodha.",
   "a massive granite warrior made of stacked boulders like an ancient rocky hill, glowing orange cracks, huge stone fists")
sp(28, "Karu", ["NORMAL"], (55, 55, 45, 30, 45), 190, 58, (24, 29),
   "It wanders into traffic and simply stands there. Somehow every vehicle goes around it.",
   "a small cream-white calf with tiny nubs for horns, a bell on a red string around its neck, big gentle eyes")
sp(29, "Hori", ["NORMAL", "EARTH"], (85, 100, 80, 50, 85), 75, 172, None,
   "At harvest festivals its horns are painted bright colors. Its charge can topple a bus.",
   "a powerful white bull with huge curved horns painted in bright festival colors with tassels, a muscular hump, stamping its hoof")
sp(30, "Mangaa", ["FIGHT"], (40, 80, 35, 35, 70), 190, 61, (28, 31),
   "It ambushes tourists on hilltops and steals bananas, sunglasses and phones.",
   "a cheeky bonnet macaque monkey with a tuft of hair on its head like a cap, holding a stolen banana, ready to fight")
sp(31, "Kapikusti", ["FIGHT"], (65, 105, 60, 60, 95), 75, 159, None,
   "It trains in mud pits at dawn and challenges any wrestler who dares enter.",
   "a burly wrestler monkey wearing a red wrestling loincloth belt, muscular arms, mud on its fur, confident wrestling stance")
sp(32, "Bekku", ["NORMAL"], (40, 45, 35, 40, 90), 255, 58, (28, 33),
   "Every street has one. It knows exactly which house gives out milk.",
   "a scruffy street cat with tabby orange and white fur, one bent ear, curious green eyes, sitting")
sp(33, "Kaalbekku", ["SPIRIT", "ROGUE"], (65, 70, 60, 85, 115), 90, 158, None,
   "If it crosses your path, people wait a moment before walking on. It finds this very funny.",
   "a sleek black ghostly cat with glowing yellow eyes, a wispy smoky tail splitting into two, floating shadow paws")
sp(34, "Goobe", ["SKY", "MIND"], (60, 30, 30, 50, 50), 255, 52, (20, 35),
   "It stares at you all night from the banyan tree. Nobody knows what it is thinking.",
   "a small round brown owl with huge orange eyes and ear tufts, perched, looking wise and sleepy")
sp(35, "Goobeguru", ["SKY", "MIND"], (100, 50, 50, 86, 70), 90, 155, None,
   "It tutors students in exam season. It is strict but never wrong.",
   "a large scholarly owl wearing round spectacles, a scroll in its talons, glowing mystical symbols around it, broad patterned wings")
sp(36, "Neralu", ["SPIRIT"], (30, 35, 30, 80, 70), 190, 62, (25, 37),
   "During power cuts it slips out of the shadows and plays with candle flames.",
   "a small floating shadow wisp with two white eyes and a wavy tail, half-transparent dark purple")
sp(37, "Neraluga", ["SPIRIT"], (60, 65, 60, 120, 100), 45, 225, None,
   "It haunts the old palace corridors. Portraits' eyes seem to follow you when it is near.",
   "a large serpent-like shadow spirit made of dark purple smoke, glowing white eyes, long shadowy claws, eerie")
sp(38, "Chintu", ["MIND"], (35, 20, 35, 90, 70), 190, 62, (26, 39),
   "It floats near people deep in thought, nibbling on stray ideas.",
   "a small floating crystal creature with a pale pink gem body, a glowing third eye, tiny hands")
sp(39, "Chintamani", ["MIND", "CHARM"], (70, 50, 80, 120, 80), 45, 220, None,
   "A wish-granting jewel in old tales. It only listens to wishes made for others.",
   "a radiant floating guardian made of large faceted pink and violet gems, a glowing jewel in its forehead, a crystal halo")
sp(40, "Aanemari", ["EARTH"], (70, 70, 60, 40, 30), 120, 66, (30, 41),
   "It loves bath time in the river and sprays water at everyone nearby.",
   "a baby elephant with grey wrinkly skin, a tiny trunk raised happily, a decorative colorful cloth on its forehead")
sp(41, "Ambaari", ["EARTH", "METAL"], (110, 110, 110, 65, 45), 45, 228, None,
   "It leads the grand autumn procession carrying a golden howdah. The crowds go silent as it passes.",
   "a giant majestic elephant carrying an ornate golden howdah on its back, decorated with jewels and a patterned caparison, tusks with gold rings")
sp(42, "Navilu", ["SKY", "CHARM"], (75, 80, 70, 95, 100), 45, 210, None,
   "It dances only when the first monsoon clouds roll in. Seeing it is said to bring rain.",
   "a dazzling peacock with an enormous fanned tail of iridescent blue-green eye feathers, a jeweled crest, elegant")
sp(43, "Haavu", ["TOXIC"], (35, 60, 44, 40, 55), 255, 58, (22, 44),
   "It hides in termite mounds and rock walls. It means no harm if left alone.",
   "a small striped snake with a flared hood, yellow and black bands, flicking tongue")
sp(44, "Nagarahaavu", ["TOXIC", "MYTH"], (60, 95, 69, 65, 80), 90, 157, None,
   "When it raises its great hood, even the boldest Mangaa backs away.",
   "a huge king cobra with a massive spread hood with a distinctive marking, glistening black and gold scales, dripping venom")
sp(45, "Kappe", ["WATER"], (40, 50, 40, 40, 90), 255, 60, (25, 46),
   "Its croaking chorus after the first rain keeps whole neighbourhoods awake.",
   "a small round green frog with a bulging throat sac, big eyes, sitting in a puddle")
sp(46, "Malekappe", ["WATER", "ELECTRIC"], (75, 75, 70, 85, 95), 75, 165, None,
   "It summons a raincloud and rides the thunder. Flash floods follow its song.",
   "a large frog wearing a small rain cloud on its head, lightning bolt markings on its blue-green skin, crackling with electricity, rain falling")
sp(47, "Volti", ["ELECTRIC"], (35, 30, 35, 65, 75), 190, 62, (26, 48),
   "When it gets excited the whole street's lights flicker. Then the power goes out.",
   "a small round electric spark creature shaped like a light bulb with a coiled filament tail, yellow glow, mischievous")
sp(48, "Currentaa", ["ELECTRIC"], (60, 60, 60, 95, 110), 75, 168, None,
   "\"Current hogide!\" is the cry when it feeds on a transformer. It is always gone before the linemen arrive.",
   "a lanky electric creature made of tangled power-line cables and a transformer box body, crackling sparks, lightbulb eyes that flicker")
sp(49, "Chiplet", ["ELECTRIC", "METAL"], (30, 35, 65, 75, 45), 190, 65, (30, 50),
   "It lives inside office laptops and gets cranky after midnight deploys.",
   "a tiny square computer-chip creature with metallic pin legs, green circuit-board patterns, a blinking LED eye")
sp(50, "Siliconda", ["ELECTRIC", "METAL"], (65, 70, 95, 110, 80), 45, 210, None,
   "It coils through the server rooms of tech parks. Its hiss sounds like a cooling fan.",
   "a long snake made of linked server-rack segments and glowing data cables, neon blue circuitry, a sleek metallic head")
sp(51, "Autorikshasa", ["NORMAL", "METAL"], (70, 100, 70, 60, 115), 75, 180, None,
   "It never goes where you ask. It always asks for one-and-a-half over the meter.",
   "a creature that is half auto-rickshaw half demon, a yellow and black three-wheeled body, headlight eyes, a horn nose, a fare meter on its side, small horns, a big grin")
sp(52, "Halasu", ["GRASS"], (55, 50, 75, 40, 25), 190, 62, (28, 53),
   "Its spiky skin hides a sweet smell. Squirrels follow it everywhere.",
   "a small round jackfruit creature with spiky green bumpy skin, two leaf sprouts on top, stubby legs")
sp(53, "Halasuru", ["GRASS", "ROCK"], (90, 95, 120, 60, 40), 60, 180, None,
   "So heavy that it leaves potholes. The city has stopped trying to fix them.",
   "a huge armored jackfruit tank creature with thick spiky rocky green hide, tree-trunk legs, a leafy crown")
sp(54, "Gulmo", ["GRASS"], (40, 40, 40, 65, 55), 190, 64, (30, 55),
   "It blooms bright red in the hottest week of summer.",
   "a small sprite made of a cluster of bright red-orange gulmohar flowers with feathery green leaves as arms")
sp(55, "Gulmohara", ["GRASS", "FIRE"], (75, 80, 70, 100, 85), 60, 182, None,
   "Its flowers look like flames, and in May they really are.",
   "a tree spirit with a canopy of blazing red-orange gulmohar flowers that look like flames, a wooden body, petals drifting like embers")
sp(56, "Railu", ["METAL", "ELECTRIC"], (45, 60, 60, 45, 60), 120, 70, (34, 57),
   "It runs back and forth along the same track all day and never gets bored.",
   "a small metallic caterpillar-like train creature with three cylindrical segments, purple and green stripes, headlight eyes")
sp(57, "Metrovaha", ["METAL", "MYTH"], (85, 110, 100, 85, 100), 45, 245, None,
   "It carries thousands across the city every day and is never on time, except when you are late.",
   "a long sleek metal dragon shaped like a modern metro train with purple livery, pantograph horns crackling with electricity, glowing windows along its body")
sp(58, "Chinnu", ["ROCK", "METAL"], (30, 55, 85, 30, 40), 190, 64, (30, 59),
   "It sparkles in old mine shafts east of the city. Prospectors once followed it for luck.",
   "a small gold nugget creature with sparkling facets, tiny pickaxe-shaped arms, shiny")
sp(59, "Chinnasura", ["ROCK", "METAL"], (75, 110, 130, 60, 45), 45, 190, None,
   "Its body is veined with gold. It guards abandoned mines and hates trespassers.",
   "a hulking golem made of rock veined with gold, glowing gold eyes, mine-cart wheel shoulders")
sp(60, "Hulimari", ["FIGHT"], (45, 70, 40, 35, 65), 120, 64, (30, 61),
   "It pounces at drumbeats and dances until it tires out.",
   "a small tiger cub with its face painted in yellow and black stripes like a folk dancer, playful pounce pose")
sp(61, "Hulivesha", ["FIGHT"], (80, 120, 70, 55, 90), 45, 195, None,
   "It leads the tiger dance at festivals. Its stomp shakes the whole street.",
   "a muscular tiger warrior in a fierce dance pose, bold painted stripes, ankle bells, a flowing red sash")
sp(62, "Hanate", ["FIRE", "SPIRIT"], (40, 30, 45, 70, 50), 120, 66, (32, 63),
   "A lamp that was never blown out. It lights the way for lost children.",
   "a small clay oil-lamp spirit with a single flickering flame as its head, gentle glowing eyes")
sp(63, "Jyotiyaksha", ["FIRE", "SPIRIT"], (65, 50, 70, 120, 90), 45, 205, None,
   "On festival nights it gathers every lamp in the city into a single robe of light.",
   "a tall elegant spirit made of countless floating lamp flames forming a robed figure, golden light, a ghostly flowing body")

# --- legendary & boss ---------------------------------------------------------------------
sp(64, "Udyanaga", ["GRASS", "MYTH"], (106, 110, 100, 130, 104), 3, 306, None,
   "Guardian of the Garden City. When the city forgets its trees and lakes, it sleeps atop the northern hills.",
   "a majestic long eastern-style dragon made of lush garden foliage, purple jacaranda and red gulmohar blossoms along its mane, leafy wings, golden eyes, legendary aura")
sp(65, "Concretor", ["ROCK", "METAL"], (100, 120, 120, 60, 50), 3, 250, None,
   "Built by the Concrete Syndicate from cement mixers and cranes. Wherever it walks, grass stops growing.",
   "a hulking construction mech creature made of grey concrete and yellow steel, a cement-mixer drum body, a crane arm, a hard-hat head, menacing")


# =============================================================================================
# Expansion to 150 (tools/content/roster_plan.py). Stats come from a total and a shape so the
# power curve stays consistent; catch rate and EXP follow the stage.
# =============================================================================================
SHAPES = {  # hp, atk, def, spc, spd weights
    "bal": (1, 1, 1, 1, 1), "phys": (1, 1.35, 1, 0.7, 0.95), "tank": (1.15, 0.9, 1.45, 0.8, 0.7),
    "spec": (0.9, 0.7, 0.9, 1.45, 1.05), "fast": (0.85, 1.1, 0.8, 1.0, 1.35), "bulky": (1.45, 1.1, 1.1, 0.8, 0.55),
    "glass": (0.8, 1.25, 0.7, 1.15, 1.3), "fastspec": (0.85, 0.75, 0.8, 1.3, 1.3),
}


def st(total, shape):
    w = SHAPES[shape]
    raw = [total * x / sum(w) for x in w]
    out = [max(10, round(v)) for v in raw]
    out[0] += total - sum(out)
    return tuple(out)


def nsp(id, name, types, total, shape, stage, evo, dex, look):
    """New-species shorthand: stage is 'base', 'mid', 'final', 'single', 'rare' or 'legend'."""
    catch = {"base": 200, "mid": 100, "final": 45, "single": 75, "rare": 25, "legend": 3}[stage]
    exp = round(total * {"base": 0.25, "mid": 0.42, "final": 0.55, "single": 0.5, "rare": 0.3, "legend": 0.6}[stage])
    sp(id, name, types, st(total, shape), catch, exp, evo, dex, look)


# --- early routes ----------------------------------------------------------------------------
nsp(66, "Naayimari", ["NORMAL"], 220, "fast", "base", (18, 67),
    "Every street has one. It follows whoever last fed it biscuits, which is everyone.",
    "a scruffy little street puppy with a tan coat, one floppy ear and one upright ear, a white chest patch, a torn red string collar, wagging tail, big hopeful eyes")
nsp(67, "Beedinaayi", ["NORMAL", "ROGUE"], 340, "fast", "mid", (36, 68),
    "It knows every shortcut in the neighbourhood and barks only at strangers on motorbikes.",
    "a lean street dog with a brindle tan-and-black coat, a nicked ear, a sly confident grin, a faded blue bandana around its neck, mid-trot")
nsp(68, "Kaavalnaayi", ["ROGUE", "FIGHT"], 450, "phys", "final", None,
    "The leader of the night pack. Shopkeepers sleep well when it patrols their lane.",
    "a big muscular guard dog with a dark brindle coat and a pale scar over one eye, a spiked leather collar, broad chest, standing tall and protective, glowing amber eyes")
nsp(69, "Gedalu", ["BUG", "EARTH"], 190, "tank", "base", (14, 70),
    "It chews dry wood and spits out red mud. Empty plots fill with its tiny towers overnight.",
    "a tiny pale cream termite with a big round reddish-brown head and small mandibles, carrying a lump of red earth, cute and determined")
nsp(70, "Huttuhula", ["BUG", "EARTH"], 320, "tank", "mid", (32, 71),
    "It lives inside a mound of hardened red clay and wears part of it as armour.",
    "a stocky termite soldier creature wearing a helmet-like shell of hardened red-clay mound with small chimney holes, strong mandibles, six sturdy legs")
nsp(71, "Huttappa", ["EARTH", "BUG"], 440, "tank", "final", None,
    "A walking termite mound as tall as a house. Its chimneys hum when it is about to charge.",
    "a huge walking termite mound creature of tall red clay spires and chimneys, termite mandibles at its base, small glowing eyes in the mud, earthy and ancient")
nsp(72, "Kadale", ["GRASS"], 230, "bal", "base", (20, 73),
    "It buries itself in sandy soil and pops up when someone shells peanuts nearby.",
    "a small round peanut-in-the-shell creature with a beige ridged shell body, two little leaf sprouts on top, stubby legs, a shy smile")
nsp(73, "Kadalekaayi", ["GRASS", "EARTH"], 400, "tank", "final", None,
    "At the groundnut fair it is guest of honour. Its roots grow pods it shares with kids.",
    "a bushy groundnut plant creature with a body of green clover-like leaves and small yellow flowers on top, long roots for legs hung with peanut pods, kind eyes")
nsp(74, "Idlimari", ["NORMAL"], 230, "bulky", "base", (24, 75),
    "Soft and warm, it bounces when happy. Darshini cooks swear it once escaped the steamer.",
    "a small round fluffy white steamed rice cake creature, soft spongy texture with tiny holes, rosy cheeks, a little dab of green chutney like a beret, bouncy")
nsp(75, "Thatteidli", ["NORMAL", "CHARM"], 400, "bulky", "final", None,
    "A stack of idlis on a steel plate. Wherever it rests, people feel like it's breakfast time.",
    "a stack of three plump white rice-cake creatures on a shining round steel plate, the top one with a happy face and a coconut-chutney crown, steam curling up like ribbons")
nsp(76, "Halli", ["NORMAL"], 220, "fast", "base", (24, 77),
    "It clings to the wall above the tube light. Grandmothers listen when it chirps.",
    "a small pale tan house gecko with big round black eyes, sticky toe pads, a stubby striped tail, clinging to a wall, curious expression")
nsp(77, "Hallishastri", ["NORMAL", "MIND"], 400, "spec", "final", None,
    "It reads the future in the chirps of other lizards and is right just often enough.",
    "a larger wise gecko with sandy scales covered in faint glowing star-chart markings, a tiny pair of round spectacles, holding a palm-leaf scroll with its tail, mystical")
nsp(78, "Kulfimari", ["FROST", "CHARM"], 250, "spec", "base", (30, 79),
    "It lives in the clay pot of the kulfi cart and only comes out on the hottest afternoons.",
    "a small clay matka pot with a frosty creamy saffron-and-pistachio kulfi creature peeking out of the top, tiny arms, crushed pistachios on its head, frosty sparkles")
nsp(79, "Gadbadu", ["FROST", "CHARM"], 420, "spec", "final", None,
    "A towering sundae of every flavour. Children follow it in parades all summer.",
    "a tall layered sundae creature in a fluted glass body, layers of pink, white and brown ice cream, jelly cubes and nuts, a cherry on its head, two wafer arms, cheerful and grand")
nsp(80, "Bennedose", ["FIRE", "SKY"], 420, "fastspec", "single", None,
    "A golden butter dosa that flies like a carpet and leaves a trail of ghee sparks.",
    "a crispy golden folded dosa crepe creature flying like a magic carpet, butter melting on top, edges curling like wings, a cheeky face, small sparks of fire trailing behind")
nsp(81, "Taavaremari", ["WATER", "GRASS"], 240, "spec", "base", (26, 82),
    "A lotus bud riding a lily pad. It drifts to the warmest corner of the lake to bloom.",
    "a small closed pink lotus bud creature sitting on a round green lily pad, little eyes peeking between the petals, water droplets, calm")
nsp(82, "Taavare", ["WATER", "GRASS"], 420, "spec", "final", None,
    "When it opens its petals at dawn, the whole lake goes still to watch.",
    "a graceful creature with a body of a fully open pink lotus flower, a serene face at the centre, broad lily-pad arms, standing on the water with ripples around it")
nsp(83, "Istri", ["FIRE", "METAL"], 260, "tank", "base", (30, 84),
    "A heavy charcoal iron box. It presses any cloth flat, whether you want it to or not.",
    "a heavy old black charcoal clothes-iron box creature with a wooden handle like a crest, glowing orange coals visible through vent holes, steam puffs, stubby legs")
nsp(84, "Istriraaja", ["FIRE", "METAL"], 430, "tank", "final", None,
    "It rules the ironing cart at the street corner, coals blazing, every shirt perfectly pressed.",
    "a big armoured creature whose body is a large ornate brass-and-iron charcoal iron with flames inside, a folded-cloth cape, strong arms, proud stance, a small rooster crest of fire")

# --- Cubbon Park and MG Road -----------------------------------------------------------------
nsp(85, "Jenuhula", ["BUG"], 220, "fast", "base", (22, 86),
    "Rock bees build hives the size of doors under the ledges of the Assembly building.",
    "a fuzzy round rock bee with golden and dark brown stripes, clear wings, tiny stinger, carrying a drop of honey, busy and cheerful")
nsp(86, "Jenuraani", ["BUG", "CHARM"], 420, "spec", "final", None,
    "The queen of a hive of thousands. Her honey is said to cure sore throats and bad moods.",
    "a regal queen bee creature with a golden body, a crown made of hexagon honeycomb dripping honey, long elegant wings, a skirt of honeycomb cells, calm commanding look")
nsp(87, "Minchuhula", ["BUG", "ELECTRIC"], 230, "fastspec", "base", (24, 88),
    "Its tail blinks in patterns. Researchers think it is gossiping with other fireflies.",
    "a small firefly beetle with a dark green shell and a big glowing yellow-green tail lantern, tiny antennae, little sparks around it, night glow")
nsp(88, "Minchurani", ["BUG", "ELECTRIC"], 410, "fastspec", "final", None,
    "On dark nights hundreds gather around it and the lake shore lights up like a festival.",
    "an elegant large firefly creature with long translucent wings, a lantern-shaped glowing abdomen crackling with electricity, a halo of tiny floating lights, graceful")
nsp(89, "Mungusi", ["FIGHT"], 250, "fast", "base", (30, 90),
    "Quick and fearless. It boxes snakes for practice and usually wins.",
    "a small grey-brown mongoose with a bushy tail, standing upright on its hind legs in a boxing stance, little fists raised, bright fearless eyes")
nsp(90, "Mungusiveera", ["FIGHT"], 430, "fast", "final", None,
    "A scarred champion. The cobras of the scrubland give it a very wide berth.",
    "a muscular mongoose warrior standing upright, grey fur with a pale scar over its snout, a red cloth band tied around its head and wrists, fierce stance, bushy tail")
nsp(91, "Baavali", ["ROGUE", "SKY"], 230, "fast", "base", (26, 92),
    "It hangs upside down in the park's old trees all day and raids mango trees all night.",
    "a small fruit bat with a fox-like face, russet-orange fur collar, leathery brown wings wrapped around itself, hanging upside down, holding a stolen mango")
nsp(92, "Baavalasura", ["ROGUE", "SKY"], 420, "glass", "final", None,
    "Its wings blot out the street lamps. Gardeners blame it for every missing fruit.",
    "a large flying fox bat with wide dark leathery wings spread, a russet mane, sharp grin, glowing red eyes, swooping pose at dusk")
nsp(93, "Pataaki", ["FIRE"], 210, "glass", "base", (16, 94),
    "A strip of tiny crackers. It giggles, sparks and pops when anyone steps on it.",
    "a small red paper firecracker strip creature, a row of tiny crackers forming its body, a lit sparking fuse tail, mischievous grin, little sparks")
nsp(94, "Sutli", ["FIRE"], 330, "glass", "mid", (34, 95),
    "Wrapped tight in jute string. Its bang can be heard three neighbourhoods away.",
    "a round chubby firecracker bomb creature wrapped tightly in brown jute string, a short sparking fuse on its head, angry eyebrows, ready to burst")
nsp(95, "Rocketaaki", ["FIRE", "SKY"], 450, "glass", "final", None,
    "It launches into the night sky and bursts into colours before landing gracefully again.",
    "a sleek sky-rocket firework creature with a long body of red and gold paper, a pointed nose cone, a bamboo stick tail blasting colourful flames and sparks, soaring upward")
nsp(96, "Gundi", ["EARTH"], 250, "tank", "base", (30, 97),
    "A pothole that wanders. It fills with rainwater and waits for someone's scooter.",
    "a round pothole creature: a hole in grey asphalt with broken edges for a mouth, muddy rainwater inside, two cheeky eyes above it, little cracked-asphalt legs")
nsp(97, "Mahagundi", ["EARTH", "ROGUE"], 420, "bulky", "final", None,
    "So deep it has its own echo. Road crews fill it every year, and every year it comes back.",
    "a huge menacing crater creature of broken asphalt slabs and muddy water, jagged edges like teeth, orange traffic cones stuck in it like horns, sly smile")
nsp(98, "Heggana", ["ROGUE"], 250, "fast", "base", (28, 99),
    "A bandicoot of the storm drains. It is bigger than a cat and braver than a dog.",
    "a large bandicoot rat with coarse dark grey fur, a long scaly tail, whiskers, a cheeky snarl, standing on a drain grate")
nsp(99, "Hegganasura", ["ROGUE", "TOXIC"], 420, "phys", "final", None,
    "The king of the drains. It comes up when it rains and drags away anything left outside.",
    "a hulking sewer-rat brute with matted dark fur dripping green sludge, a long whip-like tail, big yellow teeth, wearing a broken drain cover like a shield")
nsp(100, "Signalu", ["ELECTRIC"], 240, "spec", "base", (28, 101),
    "A traffic signal that wandered off. It turns red whenever you are in a hurry.",
    "a small traffic-signal creature with a black box body and three round lights for a face (red lit up), a pole for a leg, little arms, stubborn expression")
nsp(101, "Signalappa", ["ELECTRIC", "NORMAL"], 420, "spec", "final", None,
    "It runs an entire junction. Its red light lasts long enough for drivers to finish a phone call.",
    "a tall traffic-signal tower creature with four signal heads glowing red, amber and green, a countdown timer chest display, zebra-crossing striped base, arms directing traffic")

# --- Silk Board, Whitefield and Bellandur ----------------------------------------------------
nsp(102, "Kasa", ["TOXIC"], 240, "bulky", "base", (30, 103),
    "A heap of unsorted rubbish that walks. It grows every time someone skips segregation day.",
    "a small walking pile of mixed rubbish: crumpled plastic bags, a coconut shell, a paper cup, a banana peel on top like hair, two eyes in the middle, smelly green fumes")
nsp(103, "Kasaraashi", ["TOXIC", "ROGUE"], 420, "bulky", "final", None,
    "It hides in empty plots and grabs passing garbage trucks to make itself bigger.",
    "a huge garbage-mountain creature of black plastic bags, old tyres and broken buckets, flies buzzing, toxic green ooze, glaring eyes and long trash-bag arms")
nsp(104, "Thandi", ["FROST", "ELECTRIC"], 260, "spec", "base", (30, 105),
    "A runaway air conditioner. It blasts cold air at anyone who complains about the heat.",
    "a boxy white window air-conditioner creature with louvred vents for a mouth blowing icy wind, a little remote-control companion antenna, frost crystals, grumpy face")
nsp(105, "Thandasura", ["FROST", "ELECTRIC"], 430, "spec", "final", None,
    "It lives on tech-park rooftops and keeps whole buildings at 18 degrees.",
    "a large rooftop chiller-unit creature with spinning fan heads, coiled copper pipes like arms, frost and icicles, electric sparks, glowing blue control panel eyes")
nsp(106, "Midathe", ["BUG", "FIGHT"], 240, "phys", "base", (28, 107),
    "A grasshopper that plays gully cricket. It uses its hind legs as bats and never gets out.",
    "a green grasshopper standing upright holding its long hind leg like a cricket bat, a tiny cap, wide grin, a red cricket ball nearby")
nsp(107, "Mahamidathe", ["BUG", "FIGHT"], 430, "phys", "final", None,
    "Its sixes clear the stadium roof. Opposing bowlers bring it gifts before matches.",
    "a tall athletic green grasshopper warrior in white cricket pads and gloves, a helmet-like head shell, swinging a cricket bat made from its own leg, powerful pose")
nsp(108, "Benkinore", ["TOXIC", "FIRE"], 250, "spec", "base", (30, 109),
    "Lake foam that caught fire one day and never went out.",
    "a blob of white toxic lake foam with small orange flames dancing on top, bubbles, green chemical tint, a sad smoky face")
nsp(109, "Kerebenki", ["TOXIC", "FIRE"], 430, "spec", "final", None,
    "A burning cloud that rises off polluted water. Its smoke spells out warnings to the city.",
    "a towering cloud of burning white foam with flames and dark smoke billowing, glowing toxic green core, ghostly arms of smoke, angry eyes, rising off the water")
nsp(110, "Edi", ["WATER", "FIGHT"], 250, "phys", "base", (28, 111),
    "A lake crab with one big claw. It shadow-boxes the reeds at dawn.",
    "a small freshwater crab with a mottled brown-purple shell, one oversized boxing-glove-shaped claw, sideways boxing stance, bubbles")
nsp(111, "Ediyodha", ["WATER", "FIGHT"], 430, "tank", "final", None,
    "It guards the lake steps with two huge claws and has never lost a pinching match.",
    "a big armoured crab warrior with a deep purple-blue shell like a breastplate, two huge powerful claws, wrapped claw tape, standing on its hind legs ready to brawl")

# --- Malleshwaram and Palace Road ------------------------------------------------------------
nsp(112, "Mallige", ["GRASS", "CHARM"], 240, "spec", "base", (28, 113),
    "A jasmine bud with a sweet scent. Flower sellers string it into garlands without noticing.",
    "a tiny white jasmine flower bud sprite with soft petals as a hood, a green leaf skirt, sweet face, a faint sparkle of fragrance")
nsp(113, "Mysoremallige", ["GRASS", "CHARM"], 420, "spec", "final", None,
    "It wears a garland of a thousand blooms. Its scent can calm a traffic jam.",
    "a graceful flower dancer creature wearing long strings of white jasmine garlands, a body of jasmine petals and green leaves, flowing movement, scent sparkles")
nsp(114, "Chukki", ["CHARM"], 240, "spec", "base", (28, 115),
    "A grid of white dots that rearranges itself into patterns on doorsteps before sunrise.",
    "a small floating creature made of a neat grid of white rice-flour dots connected by curving lines, a little face in the middle, sparkling")
nsp(115, "Rangavalli", ["CHARM"], 420, "spec", "final", None,
    "A full rangoli come to life. Every festival it chooses new colours.",
    "a large floating circular rangoli pattern creature with bright pink, yellow and green powder petals in a mandala, a serene face at the centre, powder sparkles drifting")
nsp(116, "Gombe", ["CHARM"], 250, "bal", "base", (30, 117),
    "A lacquered wooden toy that rolls on its own. It sulks if put away after the festival.",
    "a small round lacquered wooden toy doll, glossy red and yellow stripes, a painted smiling face, rolling on tiny wheels, toy-like and cute")
nsp(117, "Pattadagombe", ["CHARM", "MIND"], 430, "spec", "final", None,
    "The royal doll couple from the top step of the festival display. It remembers every family it has visited.",
    "a regal pair of carved wooden dolls joined as one creature, a king and queen in painted crowns and silk robes, lacquered shine, serene painted faces, standing on a decorated step")
nsp(118, "Togalu", ["SPIRIT"], 250, "glass", "base", (30, 119),
    "A leather puppet that moves when the lamp is lit. It acts out old stories on any wall.",
    "a flat translucent leather shadow-puppet creature with intricate punched patterns, colourful dyed panels, jointed arms on thin sticks, glowing from behind like a lamp")
nsp(119, "Togalugombe", ["SPIRIT", "CHARM"], 430, "spec", "final", None,
    "Its shadow can be a king, a tiger or a storm. It never shows its true shape.",
    "a large ornate leather shadow-puppet spirit with a crown and jointed limbs, glowing amber light shining through its patterns, its shadow cast as a dramatic figure behind it")
nsp(120, "Kaage", ["SKY", "SPIRIT"], 240, "fast", "base", (30, 121),
    "Families leave rice out for it on remembrance days. It carries the offering to the ancestors.",
    "a sleek grey-necked house crow with glossy black wings, clever eyes, carrying a small ball of rice in its beak, a faint ghostly glow around its feathers")
nsp(121, "Kaageraaja", ["SKY", "SPIRIT"], 420, "fastspec", "final", None,
    "The crow king who walks between this world and the next with messages for the living.",
    "a large majestic crow with deep black feathers shimmering purple, a ghostly silver neck ruff, wispy spirit-flame tail feathers, piercing silver eyes, a small crown of feathers")
nsp(122, "Hunase", ["GRASS", "SPIRIT"], 250, "bulky", "base", (32, 123),
    "A tamarind sapling hung with sour pods. Children dare each other to pick them at night.",
    "a small tamarind sapling creature with feathery green leaves, hanging curved brown tamarind pods, a gnarled trunk body with spooky hollow eyes")
nsp(123, "Hunasemohini", ["GRASS", "SPIRIT"], 430, "spec", "final", None,
    "Village tales say a spirit lives in every old tamarind tree. This is the spirit.",
    "a tall haunting tamarind tree spirit with a twisted dark trunk, long drooping branches like hair, hanging pods, pale ghostly glow from within, a calm eerie face in the bark")
nsp(124, "Gandhamari", ["GRASS"], 250, "spec", "base", (32, 125),
    "A sandalwood sapling. Its fragrance makes nearby creatures sleepy and kind.",
    "a small sandalwood sapling creature with a smooth pale-brown wooden body, glossy green leaves, a sleepy content face, wisps of fragrant smoke")
nsp(125, "Shrigandha", ["GRASS", "MIND"], 430, "spec", "final", None,
    "Its heartwood is so fragrant that a single branch scents a whole palace for a year.",
    "a serene tall sandalwood tree spirit with a golden-brown heartwood body carved with fine patterns, glossy leaves, sitting in meditation, fragrant golden mist around it")

# --- Hebbal and Nandi Hills ------------------------------------------------------------------
nsp(126, "Kokkare", ["WATER", "SKY"], 250, "bal", "base", (30, 127),
    "A pelican chick from the nesting village. Its pouch is always full of tiny fish.",
    "a fluffy grey spot-billed pelican chick with a big pinkish pouch beak, small wings, a fish tail peeking from its pouch, standing in shallow water")
nsp(127, "Bannadakokkare", ["WATER", "SKY"], 430, "bal", "final", None,
    "A painted stork with rose-pink wings. Villagers count its return each winter as good luck.",
    "a tall elegant painted stork with a long yellow beak, white body, rose-pink tinted wing feathers, black and white barred wings spread, a bare orange face, standing in a lake")
nsp(128, "Tagaru", ["FIGHT"], 260, "phys", "base", (32, 129),
    "A young ram that headbutts everything. Its horns are painted for the fair.",
    "a stocky young ram with thick curled horns painted with festival colours, woolly cream fleece, a bell on a red string, stamping its hoof, ready to charge")
nsp(129, "Kaadutagaru", ["FIGHT", "EARTH"], 440, "phys", "final", None,
    "A fighting ram of the hills. When it charges, the ground cracks under its hooves.",
    "a powerful wild ram with massive spiralled horns, a shaggy dark fleece, rocky armour plates on its shoulders, dust cloud around its hooves, fierce glowing eyes")
nsp(130, "Aalikallu", ["FROST", "ROCK"], 260, "tank", "base", (34, 131),
    "A hailstone that grew a face during a summer storm. It is surprised every time it doesn't melt.",
    "a round chunky hailstone creature with a frosty layered ice-and-stone body, small icy spikes, surprised round eyes, little rocky feet, cold mist")
nsp(131, "Aalibande", ["FROST", "ROCK"], 440, "tank", "final", None,
    "A boulder of ice and granite. It rolls down the hills during freak hailstorms.",
    "a huge boulder creature of grey granite fused with blue glacial ice, jagged ice spikes on its back, frosty breath, heavy fists, rolling stance")
nsp(132, "Manju", ["FROST", "SPIRIT"], 260, "fastspec", "base", (36, 133),
    "A wisp of morning fog. Travellers on the hill road lose their way when it giggles.",
    "a small floating wisp of white morning fog with a soft round face, trailing mist wisps, faint icy sparkles, playful ghostly")
nsp(133, "Manjumaaye", ["FROST", "SPIRIT"], 440, "fastspec", "final", None,
    "It wraps the whole hill in fog at sunrise and reveals the view only to those it likes.",
    "a tall elegant fog-spirit creature in a flowing gown made of mist and frost, pale blue glowing eyes, icy crystal jewellery, half-transparent, drifting above clouds")
nsp(134, "Chiratemari", ["ROGUE"], 260, "fast", "base", (32, 135),
    "A leopard cub that hides in rocky scrub. It practises stalking on lizards.",
    "a small leopard cub with golden fur covered in black rosette spots, big bright eyes, a crouching playful stalking pose, long tail")
nsp(135, "Chirate", ["ROGUE"], 440, "glass", "final", None,
    "It slips through the forest edge at night without a sound. Only its eyes give it away.",
    "a sleek adult leopard with dark golden fur and bold black rosettes, a long tail, crouched on a rock at night, glowing green eyes, shadowy aura")
nsp(136, "Kaadupaapa", ["ROGUE", "CHARM"], 420, "fastspec", "single", None,
    "The 'forest baby'. It moves so slowly that few have seen it, but its huge eyes see everything.",
    "a slender loris with soft grey-brown fur, enormous round shining eyes with dark eye patches, long thin limbs gripping a branch, gentle and mysterious, night glow")

# --- rare, fossils and the Yali line ---------------------------------------------------------
nsp(137, "Makaramari", ["WATER", "MYTH"], 300, "bal", "rare", (35, 138),
    "A young temple-arch beast hiding in the old tanks. Fishermen think it is a crocodile with a trunk.",
    "a small mythical makara creature: a crocodile body with a short curling elephant trunk, fish fins and a curled fish tail, turquoise and gold scales, playful")
nsp(138, "Makara", ["WATER", "MYTH"], 470, "phys", "final", None,
    "The beast carved over temple doors. When it surfaces, the tank's water rises to the top step.",
    "a large majestic mythical makara beast: a crocodile jaw and body, a long curling elephant trunk, flowing fish fins and a peacock-like spiral tail, turquoise and gold scales, ornate temple-carving details")
nsp(139, "Paachikallu", ["ROCK", "GRASS"], 320, "tank", "rare", (40, 140),
    "Revived from three-billion-year-old rock. It is the oldest kind of life ever found in the city.",
    "a small domed stone creature made of layered ancient stromatolite rock, a fuzzy green algae mat on top, tiny stubby legs, slow ancient eyes")
nsp(140, "Paachibande", ["ROCK", "GRASS"], 470, "tank", "final", None,
    "Its layered body is a record of the planet's first sunrises.",
    "a large ancient creature shaped like a stack of layered stromatolite stone domes, covered in green and teal algae mats glowing in sunlight, crystal veins, moss beard")
nsp(141, "Kalluhula", ["ROCK", "BUG"], 320, "tank", "rare", (40, 142),
    "Revived from a fossil in the cave. It rolls into a stone ball when startled.",
    "a small trilobite-like ancient bug with a segmented grey-brown stone shell, many tiny legs, curious compound eyes, partly curled up")
nsp(142, "Kalluveera", ["ROCK", "BUG"], 470, "phys", "final", None,
    "An ancient armoured hunter. Its shell is harder than the granite it was found in.",
    "a large armoured ancient arthropod warrior with a segmented granite-like shell, long spiked tail, blade-like forelimbs, fossil patterns on its armour, standing upright")
nsp(143, "Yalimari", ["ROCK", "MYTH"], 300, "phys", "rare", (30, 144),
    "A temple-pillar cub that shook itself loose from the stone. It still has chisel marks on its paws.",
    "a small mythical yali cub carved from grey granite: a lion cub body, a tiny elephant trunk, curled mane, horse-like hooves, chisel marks, glowing amber eyes")
nsp(144, "Yalikamba", ["ROCK", "MYTH"], 420, "phys", "mid", (50, 145),
    "It guards a ruined mandapa and rears up on its hind legs like the carvings it came from.",
    "a rearing mythical yali beast carved from stone, a lion body with a curled elephant trunk and tusks, a heavy mane, standing on hind legs, carved pillar fragments on its back")
nsp(145, "Mahayali", ["MYTH", "ROCK"], 520, "phys", "final", None,
    "The great guardian of every temple gate. Legends say a whole hall of pillars came alive to form it.",
    "a huge majestic mythical yali guardian: lion body of polished granite and gold, a long curling elephant trunk with tusks, a flaming mane, horse hooves, ornate temple carvings across its body, powerful heroic pose")

# --- legendaries and the mythical No. 150 ----------------------------------------------------
nsp(146, "Gandaberunda", ["SKY", "MYTH"], 580, "bal", "legend", None,
    "The two-headed eagle of the old kingdom's seal. It wakes only when the land needs a protector.",
    "a colossal mythical two-headed eagle with two crowned heads facing opposite ways, golden and crimson feathers, huge spread wings, each head holding a curled trunk-like beak ornament, regal and fierce, legendary aura")
nsp(147, "Bisilu", ["FIRE", "EARTH"], 570, "phys", "legend", None,
    "The spirit of summer. In April it lies on the granite hills and the rocks glow with heat.",
    "a powerful legendary lion made of sun-baked orange granite, a mane of shimmering heat-haze flames, cracked-earth patterns across its body, molten golden eyes, standing on a rocky outcrop")
nsp(148, "Mungaru", ["WATER", "ELECTRIC"], 570, "bulky", "legend", None,
    "The spirit of the monsoon. Its trumpet is the first thunder of June.",
    "a giant legendary elephant made of dark storm clouds, lightning crackling along its tusks, rain pouring from its ears, a glowing blue rain-drop crest, trumpeting")
nsp(149, "Chali", ["FROST", "MIND"], 570, "fastspec", "legend", None,
    "The spirit of winter mornings. It is seen only at sunrise, gliding over the sea of clouds.",
    "a graceful legendary great hornbill made of pale morning fog and frost, a huge ivory casque on its beak, long white and silver tail feathers trailing mist, calm wise blue eyes, gliding above clouds")
nsp(150, "Bendakaalu", ["CHARM", "MIND"], 560, "bal", "legend", None,
    "The boiled bean of the old legend, said to have fed a lost king. The city is named after it.",
    "a tiny glowing cream-coloured boiled bean spirit with a sprout on its head, a soft golden halo, wide wondering eyes, floating gently with sparkles, mythical and humble")

SPECIES = S
