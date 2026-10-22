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
sp(33, "Kaalbekku", ["SPIRIT"], (65, 70, 60, 85, 115), 90, 158, None,
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
sp(39, "Chintamani", ["MIND", "ROCK"], (70, 50, 80, 120, 80), 45, 220, None,
   "A wish-granting jewel in old tales. It only listens to wishes made for others.",
   "a radiant floating guardian made of large faceted pink and violet gems, a glowing jewel in its forehead, a crystal halo")
sp(40, "Aanemari", ["EARTH"], (70, 70, 60, 40, 30), 120, 66, (30, 41),
   "It loves bath time in the river and sprays water at everyone nearby.",
   "a baby elephant with grey wrinkly skin, a tiny trunk raised happily, a decorative colorful cloth on its forehead")
sp(41, "Ambaari", ["EARTH", "METAL"], (110, 110, 110, 65, 45), 45, 228, None,
   "It leads the grand autumn procession carrying a golden howdah. The crowds go silent as it passes.",
   "a giant majestic elephant carrying an ornate golden howdah on its back, decorated with jewels and a patterned caparison, tusks with gold rings")
sp(42, "Navilu", ["SKY", "MIND"], (75, 80, 70, 95, 100), 45, 210, None,
   "It dances only when the first monsoon clouds roll in. Seeing it is said to bring rain.",
   "a dazzling peacock with an enormous fanned tail of iridescent blue-green eye feathers, a jeweled crest, elegant")
sp(43, "Haavu", ["TOXIC"], (35, 60, 44, 40, 55), 255, 58, (22, 44),
   "It hides in termite mounds and rock walls. It means no harm if left alone.",
   "a small striped snake with a flared hood, yellow and black bands, flicking tongue")
sp(44, "Nagarahaavu", ["TOXIC"], (60, 95, 69, 65, 80), 90, 157, None,
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
sp(57, "Metrovaha", ["METAL", "ELECTRIC"], (85, 110, 100, 85, 100), 45, 245, None,
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
sp(64, "Udyanaga", ["GRASS", "SKY"], (106, 110, 100, 130, 104), 3, 306, None,
   "Guardian of the Garden City. When the city forgets its trees and lakes, it sleeps atop the northern hills.",
   "a majestic long eastern-style dragon made of lush garden foliage, purple jacaranda and red gulmohar blossoms along its mane, leafy wings, golden eyes, legendary aura")
sp(65, "Concretor", ["ROCK", "METAL"], (100, 120, 120, 60, 50), 3, 250, None,
   "Built by the Concrete Syndicate from cement mixers and cranes. Wherever it walks, grass stops growing.",
   "a hulking construction mech creature made of grey concrete and yellow steel, a cement-mixer drum body, a crane arm, a hard-hat head, menacing")

SPECIES = S
