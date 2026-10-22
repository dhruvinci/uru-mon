"""Move list for uru-mon.

Each move: id, name, type, category (PHYSICAL / SPECIAL / STATUS), power, accuracy (0 = never misses),
pp, priority, effect (or None), description. Effect kinds handled by src/battle/engine/battle-engine.js:
  status   {"status": BRN|PSN|PAR|SLP|FRZ, "chance": %}   (status moves use chance 100)
  stat     {"target": "self"|"foe", "stats": {...stages}, "chance": %}
  drain    {"ratio": 0.5}            heal user by ratio of damage dealt
  recoil   {"ratio": 0.25}           user takes ratio of damage dealt
  heal     {"ratio": 0.5}            heal user by ratio of max HP
  rest     {}                        full heal, fall asleep 2 turns
  highCrit {}                        crit chance 1/8
  fixed    {"damage": "level"|int}
  multi    {"min": 2, "max": 5}
  flinch   {"chance": %}
  cure     {}                        cure user's status
"""

M = []


def mv(id, name, type, cat, power, acc, pp, desc, effect=None, priority=0):
    M.append(dict(id=id, name=name, type=type, category=cat, power=power, accuracy=acc, pp=pp,
                  priority=priority, effect=effect, description=desc))


def st(status, chance=100):
    return dict(kind="status", status=status, chance=chance)


def stat(target, chance=100, **stages):
    return dict(kind="stat", target=target, stats=stages, chance=chance)


P, S_, X = "PHYSICAL", "SPECIAL", "STATUS"

# NORMAL
mv(1, "Bump", "NORMAL", P, 40, 100, 35, "A clumsy full-body bump.")
mv(2, "Scratch", "NORMAL", P, 40, 100, 35, "Rakes the foe with sharp claws.")
mv(3, "Honk", "NORMAL", X, 0, 100, 40, "A deafening horn blast that lowers the foe's ATK.", stat("foe", ATK=-1))
mv(4, "Tail Wag", "NORMAL", X, 0, 100, 30, "Cutely wags its tail. Lowers the foe's DEF.", stat("foe", DEF=-1))
mv(5, "Quick Dash", "NORMAL", P, 40, 100, 30, "Darts in before the foe can react. Usually goes first.", priority=1)
mv(6, "Headbutt", "NORMAL", P, 70, 100, 15, "A hard headbutt. May make the foe flinch.", dict(kind="flinch", chance=30))
mv(7, "Belly Flop", "NORMAL", P, 85, 100, 15, "Flops onto the foe. May paralyze.", st("PAR", 30))
mv(8, "Rush Hour", "NORMAL", P, 120, 100, 10, "A reckless charge like peak-hour traffic. The user takes recoil.", dict(kind="recoil", ratio=0.33))
mv(9, "Battle Cry", "NORMAL", X, 0, 0, 30, "Psyches itself up. Raises ATK.", stat("self", ATK=1))
mv(10, "Siesta", "NORMAL", X, 0, 0, 10, "A long afternoon nap. Fully heals, then sleeps for two turns.", dict(kind="rest"))
mv(11, "Meter Mele", "NORMAL", P, 80, 100, 15, "Charges one-and-a-half over the meter. High critical-hit ratio.", dict(kind="highCrit"))
mv(12, "Fury Swipes", "NORMAL", P, 18, 80, 15, "Scratches 2 to 5 times in a row.", dict(kind="multi", min=2, max=5))
mv(13, "Peanut Toss", "NORMAL", P, 15, 90, 20, "Throws peanuts 2 to 5 times.", dict(kind="multi", min=2, max=5))
mv(14, "Hard Stare", "NORMAL", X, 0, 100, 30, "An unblinking stare. Lowers the foe's SPD.", stat("foe", SPD=-1))

# FIRE
mv(20, "Ember", "FIRE", S_, 40, 100, 25, "A small flame. May burn.", st("BRN", 10))
mv(21, "Steam Jet", "FIRE", S_, 60, 100, 20, "A jet of scalding coffee steam. May burn.", st("BRN", 10))
mv(22, "Tandoor Fang", "FIRE", P, 65, 95, 15, "Bites with fangs hot as a tandoor. May burn.", st("BRN", 10))
mv(23, "Masala Blaze", "FIRE", S_, 90, 100, 15, "A spicy firestorm. May burn.", st("BRN", 10))
mv(24, "Kaapi Cannon", "FIRE", S_, 110, 85, 5, "Fires boiling decoction at full pressure.")
mv(25, "Lamp Glow", "FIRE", X, 0, 75, 15, "A hypnotic flame that burns the foe.", st("BRN"))
mv(26, "Filter Crash", "FIRE", P, 100, 100, 10, "A blazing charge in a steel helmet. The user takes recoil.", dict(kind="recoil", ratio=0.25))

# WATER
mv(30, "Squirt", "WATER", S_, 40, 100, 25, "Squirts water through a straw.")
mv(31, "Bubble Burst", "WATER", S_, 40, 100, 30, "Sprays bubbles. May lower SPD.", stat("foe", 10, SPD=-1))
mv(32, "Monsoon Shower", "WATER", S_, 65, 100, 20, "A sudden downpour.")
mv(33, "Shell Ram", "WATER", P, 75, 95, 15, "Rams with a hard, wet shell.")
mv(34, "Lake Surge", "WATER", S_, 90, 100, 15, "A huge wave from the lake.")
mv(35, "Kere Flood", "WATER", S_, 110, 80, 5, "Releases the whole lake at once.")
mv(36, "Coconut Sip", "WATER", X, 0, 0, 10, "Sips cool coconut water. Restores half max HP.", dict(kind="heal", ratio=0.5))
mv(37, "Withdraw", "WATER", X, 0, 0, 30, "Retreats into its shell. Raises DEF.", stat("self", DEF=1))

# GRASS
mv(40, "Creeper Lash", "GRASS", P, 45, 100, 25, "Whips the foe with a creeper vine.")
mv(41, "Petal Shower", "GRASS", S_, 60, 100, 20, "Showers the foe with sharp petals.")
mv(42, "Root Drain", "GRASS", S_, 60, 100, 15, "Drains energy through roots. Heals the user.", dict(kind="drain", ratio=0.5))
mv(43, "Mallige Scent", "GRASS", X, 0, 75, 15, "A heady jasmine scent that puts the foe to sleep.", st("SLP"))
mv(44, "Jacaranda Bloom", "GRASS", S_, 90, 100, 15, "A storm of purple blossoms.")
mv(45, "Thorn Charge", "GRASS", P, 85, 95, 15, "A charge with spiky skin. High critical-hit ratio.", dict(kind="highCrit"))
mv(46, "Sunbeam", "GRASS", S_, 120, 90, 5, "Focuses harsh afternoon sunlight into a beam.")
mv(47, "Pollen Puff", "GRASS", X, 0, 75, 30, "Scatters pollen that paralyzes the foe.", st("PAR"))
mv(48, "Garden City", "GRASS", S_, 130, 95, 5, "The guardian calls on every tree in the city. Heals the user a little.", dict(kind="drain", ratio=0.25))

# ELECTRIC
mv(50, "Spark", "ELECTRIC", P, 40, 100, 30, "An electric tackle. May paralyze.", st("PAR", 10))
mv(51, "Power Cut", "ELECTRIC", X, 0, 90, 20, "\"Current hogide!\" Paralyzes the foe.", st("PAR"))
mv(52, "Live Wire", "ELECTRIC", S_, 75, 100, 15, "Lashes with a live cable. May paralyze.", st("PAR", 10))
mv(53, "Thunderclap", "ELECTRIC", S_, 90, 100, 15, "A monsoon thunderbolt. May paralyze.", st("PAR", 10))
mv(54, "Overload", "ELECTRIC", S_, 110, 85, 5, "Overloads the grid in one huge discharge.")
mv(55, "Charge Up", "ELECTRIC", X, 0, 0, 20, "Stores power. Raises SPC.", stat("self", SPC=1))
mv(56, "Pantograph", "ELECTRIC", P, 80, 100, 15, "Strikes with crackling overhead wires.")

# EARTH
mv(60, "Mud Slap", "EARTH", S_, 20, 100, 10, "Hurls mud. Lowers the foe's accuracy.", stat("foe", ACC=-1))
mv(61, "Sand Toss", "EARTH", X, 0, 100, 15, "Throws sand in the foe's eyes. Lowers accuracy.", stat("foe", ACC=-1))
mv(62, "Pothole", "EARTH", P, 80, 100, 10, "Opens a pothole under the foe.")
mv(63, "Stampede", "EARTH", P, 75, 95, 15, "A heavy stampede. May make the foe flinch.", dict(kind="flinch", chance=20))
mv(64, "Earth Shake", "EARTH", P, 100, 100, 10, "Shakes the ground violently.")
mv(65, "Bath Time", "EARTH", X, 0, 0, 10, "Sprays dust and water over itself. Restores half max HP.", dict(kind="heal", ratio=0.5))

# ROCK
mv(70, "Pebble Throw", "ROCK", P, 40, 100, 25, "Flicks sharp pebbles.")
mv(71, "Rock Slide", "ROCK", P, 75, 90, 10, "Rolls rocks onto the foe. May make it flinch.", dict(kind="flinch", chance=30))
mv(72, "Boulder Crash", "ROCK", P, 100, 80, 5, "Drops a boulder on the foe.")
mv(73, "Granite Wall", "ROCK", X, 0, 0, 20, "Hardens like granite. Sharply raises DEF.", stat("self", DEF=2))
mv(74, "Concrete Pour", "ROCK", P, 95, 95, 10, "Buries the foe in wet concrete. Lowers its SPD.", stat("foe", SPD=-1))
mv(75, "Gem Shard", "ROCK", S_, 70, 100, 15, "Fires a glittering shard of gemstone.")

# SKY
mv(80, "Peck", "SKY", P, 35, 100, 35, "Jabs with a beak.")
mv(81, "Gust", "SKY", S_, 40, 100, 35, "Whips up a gust of wind.")
mv(82, "Wing Slice", "SKY", P, 60, 100, 25, "Slices with sharp wings.")
mv(83, "Kite Dive", "SKY", P, 90, 95, 15, "A screaming dive from high above. High critical-hit ratio.", dict(kind="highCrit"))
mv(84, "Feather Dance", "SKY", X, 0, 100, 15, "A dazzling dance. Sharply lowers the foe's ATK.", stat("foe", ATK=-2))
mv(85, "Monsoon Wind", "SKY", S_, 100, 85, 10, "A howling monsoon wind.")
mv(86, "Roost", "SKY", X, 0, 0, 10, "Lands to rest. Restores half max HP.", dict(kind="heal", ratio=0.5))

# BUG
mv(90, "Sting", "BUG", P, 35, 100, 35, "A jab with a stinger. May poison.", st("PSN", 20))
mv(91, "Silk Thread", "BUG", X, 0, 95, 40, "Wraps the foe in silk. Sharply lowers SPD.", stat("foe", SPD=-2))
mv(92, "Swarm", "BUG", P, 60, 100, 20, "A buzzing swarm attack.")
mv(93, "Leech Bite", "BUG", P, 60, 100, 15, "Sucks blood. Heals the user.", dict(kind="drain", ratio=0.5))
mv(94, "Wing Dust", "BUG", S_, 75, 100, 15, "Scatters shimmering wing scales. May lower SPC.", stat("foe", 20, SPC=-1))
mv(95, "Beetle Ram", "BUG", P, 100, 85, 10, "A ramming charge.")
mv(96, "Cocoon", "BUG", X, 0, 0, 20, "Wraps itself in silk. Sharply raises DEF.", stat("self", DEF=2))

# TOXIC
mv(100, "Toxic Jab", "TOXIC", P, 40, 100, 30, "A venomous jab. May poison.", st("PSN", 30))
mv(101, "Smog", "TOXIC", S_, 30, 70, 20, "Exhaust fumes. May poison.", st("PSN", 40))
mv(102, "Sludge", "TOXIC", S_, 65, 100, 20, "Hurls sludge. May poison.", st("PSN", 30))
mv(103, "Foam Flood", "TOXIC", S_, 90, 100, 10, "A wave of toxic foam. May poison.", st("PSN", 20))
mv(104, "Toxic Fumes", "TOXIC", X, 0, 90, 20, "Releases choking fumes that poison the foe.", st("PSN"))
mv(105, "Venom Fang", "TOXIC", P, 80, 100, 15, "A bite dripping venom. May poison.", st("PSN", 30))
mv(106, "Gunk Shot", "TOXIC", P, 120, 80, 5, "Hurls a mass of garbage-dump gunk. May poison.", st("PSN", 30))

# FIGHT
mv(110, "Kusti Chop", "FIGHT", P, 50, 100, 25, "A wrestler's chop.")
mv(111, "Leg Spin", "FIGHT", P, 60, 90, 20, "A spinning kick. May make the foe flinch.", dict(kind="flinch", chance=20))
mv(112, "Yorker", "FIGHT", P, 80, 95, 15, "Aims right at the toes. High critical-hit ratio.", dict(kind="highCrit"))
mv(113, "Bulk Up", "FIGHT", X, 0, 0, 20, "Flexes. Raises ATK and DEF.", stat("self", ATK=1, DEF=1))
mv(114, "Pailwan Slam", "FIGHT", P, 100, 85, 10, "Lifts and slams the foe into the mud.")
mv(115, "Tiger Stomp", "FIGHT", P, 90, 100, 10, "A stomping dance step. May make the foe flinch.", dict(kind="flinch", chance=20))
mv(116, "Counter Punch", "FIGHT", P, 40, 100, 30, "A fast jab that always goes first.", priority=1)

# MIND
mv(120, "Brain Wave", "MIND", S_, 50, 100, 25, "A wave of psychic power.")
mv(121, "Third Eye", "MIND", S_, 70, 100, 20, "A beam from a glowing third eye. May lower SPD.", stat("foe", 10, SPD=-1))
mv(122, "Mind Bomb", "MIND", S_, 90, 100, 10, "A massive psychic blast. May lower SPC.", stat("foe", 10, SPC=-1))
mv(123, "Dhyana", "MIND", X, 0, 0, 20, "Deep meditation. Sharply raises SPC.", stat("self", SPC=2))
mv(124, "Lullaby", "MIND", X, 0, 60, 20, "A soft lullaby that puts the foe to sleep.", st("SLP"))
mv(125, "Exam Pressure", "MIND", X, 0, 100, 20, "Overwhelms the foe with homework. Lowers SPC and SPD.", stat("foe", SPC=-1, SPD=-1))
mv(126, "Wish Jewel", "MIND", X, 0, 0, 10, "Makes a wish on its jewel. Restores half max HP.", dict(kind="heal", ratio=0.5))

# SPIRIT
mv(130, "Shadow Touch", "SPIRIT", P, 30, 100, 30, "A chilling touch. May paralyze.", st("PAR", 30))
mv(131, "Midnight Haunt", "SPIRIT", S_, 0, 100, 15, "Haunts the foe. Deals damage equal to the user's level.", dict(kind="fixed", damage="level"))
mv(132, "Spirit Orb", "SPIRIT", S_, 85, 100, 15, "Hurls a ball of spirit fire. May lower SPC.", stat("foe", 20, SPC=-1))
mv(133, "Ghostly Glare", "SPIRIT", X, 0, 100, 20, "A terrifying stare. Sharply lowers the foe's SPD.", stat("foe", SPD=-2))
mv(134, "Phantom Claw", "SPIRIT", P, 70, 100, 15, "Slashes from the shadows. High critical-hit ratio.", dict(kind="highCrit"))
mv(135, "Power-Cut Prowl", "SPIRIT", P, 80, 100, 10, "Strikes from the darkness of a power cut.")

# METAL
mv(140, "Metal Claw", "METAL", P, 50, 95, 35, "Rakes with steel claws. May raise ATK.", stat("self", 10, ATK=1))
mv(141, "Steel Plating", "METAL", X, 0, 0, 15, "Bolts on steel plates. Sharply raises DEF.", stat("self", DEF=2))
mv(142, "Tumbler Toss", "METAL", S_, 80, 100, 10, "Flings a spinning steel tumbler. May lower SPC.", stat("foe", 10, SPC=-1))
mv(143, "Rail Slam", "METAL", P, 100, 90, 10, "Slams down like a speeding train.")
mv(144, "Data Spike", "METAL", S_, 70, 100, 15, "Fires a spike of compressed data.")
mv(145, "Crane Swing", "METAL", P, 110, 85, 5, "Swings a crane arm with full force.")

# FROST
mv(150, "Chill Breeze", "FROST", S_, 40, 100, 25, "A cold gust like a December morning. May freeze.", st("FRZ", 10))
mv(151, "Hail Pellet", "FROST", P, 40, 100, 30, "Flicks a hailstone before the foe can react. Usually goes first.", priority=1)
mv(152, "Gola Blast", "FROST", S_, 55, 95, 15, "Sprays shaved ice. Lowers the foe's SPD.", stat("foe", SPD=-1))
mv(153, "Frost Bite", "FROST", P, 65, 95, 15, "Bites with icy fangs. May freeze.", st("FRZ", 10))
mv(154, "AC Blast", "FROST", S_, 90, 100, 10, "Air-conditioning at 16 degrees, full fan. May freeze.", st("FRZ", 10))
mv(155, "Glacier Crush", "FROST", P, 90, 95, 10, "Slams down a slab of ice.")
mv(156, "Hailstorm", "FROST", S_, 110, 70, 5, "Summons a sudden April hailstorm. May freeze.", st("FRZ", 10))
mv(157, "Fog Veil", "FROST", X, 0, 0, 15, "Hides in thick morning fog. Raises evasion.", stat("self", EVA=1))

# MYTH
mv(160, "Trunk Lash", "MYTH", P, 45, 100, 30, "Whips the foe with a carved stone trunk.")
mv(161, "Legend Breath", "MYTH", S_, 60, 100, 20, "Breathes the air of old legends. May paralyze.", st("PAR", 30))
mv(162, "Yali Claw", "MYTH", P, 80, 100, 15, "Strikes with the claws of a temple guardian.")
mv(163, "Torana Pulse", "MYTH", S_, 85, 100, 10, "A wave of power shaped like a temple archway.")
mv(164, "Epic Fury", "MYTH", P, 120, 100, 10, "A rampage straight out of an epic. The user takes recoil.", dict(kind="recoil", ratio=0.25))
mv(165, "Utsava Dance", "MYTH", X, 0, 0, 20, "A festival dance. Raises ATK and SPD.", stat("self", ATK=1, SPD=1))
mv(166, "Twin Talon", "MYTH", P, 55, 95, 10, "Both heads strike at once. Hits twice.", dict(kind="multi", min=2, max=2))

# ROGUE
mv(170, "Sly Swipe", "ROGUE", P, 40, 100, 25, "A quick swipe while the foe isn't looking.")
mv(171, "Sneak Bite", "ROGUE", P, 60, 100, 25, "Bites from a blind spot. May make the foe flinch.", dict(kind="flinch", chance=30))
mv(172, "Night Prowl", "ROGUE", P, 70, 100, 15, "Strikes from the dark. High critical-hit ratio.", dict(kind="highCrit"))
mv(173, "Dark Alley", "ROGUE", S_, 80, 100, 15, "Drags the foe into a pitch-dark lane. May make it flinch.", dict(kind="flinch", chance=20))
mv(174, "Gang Rush", "ROGUE", P, 85, 100, 15, "The whole gang piles in. May lower the foe's DEF.", stat("foe", 20, DEF=-1))
mv(175, "Midnight Raid", "ROGUE", P, 100, 85, 10, "A daring raid after midnight.")
mv(176, "Street Smarts", "ROGUE", X, 0, 0, 20, "Plots something clever. Sharply raises SPC.", stat("self", SPC=2))
mv(177, "Leg Pull", "ROGUE", X, 0, 100, 20, "Teases the foe mercilessly. Sharply lowers its DEF.", stat("foe", DEF=-2))

# CHARM
mv(180, "Sweet Breeze", "CHARM", S_, 40, 100, 25, "A breeze scented with jasmine.")
mv(181, "Coy Smile", "CHARM", X, 0, 100, 20, "A smile so sweet the foe forgets to fight. Sharply lowers its ATK.", stat("foe", ATK=-2))
mv(182, "Jasmine Kiss", "CHARM", S_, 50, 100, 10, "A fragrant kiss that drains HP.", dict(kind="drain", ratio=0.5))
mv(183, "Honey Drizzle", "CHARM", S_, 65, 100, 15, "Pours sticky honey. May lower the foe's SPD.", stat("foe", 30, SPD=-1))
mv(184, "Rangoli Burst", "CHARM", S_, 80, 100, 10, "Bursts into a cloud of bright rangoli colours.")
mv(185, "Festival Glow", "CHARM", S_, 95, 100, 10, "Shines like a street on festival night. May lower the foe's SPC.", stat("foe", 30, SPC=-1))
mv(186, "Bombe Dance", "CHARM", X, 0, 0, 20, "A graceful doll dance. Raises SPC and SPD.", stat("self", SPC=1, SPD=1))
mv(187, "Bean Blessing", "CHARM", S_, 100, 100, 5, "The blessing of the boiled bean. Drains HP.", dict(kind="drain", ratio=0.25))

# signatures and extras
mv(190, "Summer Scorch", "FIRE", S_, 100, 95, 5, "The full heat of an April noon. May burn.", st("BRN", 20))
mv(191, "Thunder Trumpet", "ELECTRIC", S_, 100, 95, 5, "Trumpets the first thunder of the monsoon. May paralyze.", st("PAR", 20))
mv(192, "Dawn Mist", "FROST", S_, 100, 95, 5, "Freezing mist that rolls in at sunrise. May freeze.", st("FRZ", 20))
mv(193, "Pillar Crash", "ROCK", P, 110, 90, 5, "Brings down a granite pillar. May make the foe flinch.", dict(kind="flinch", chance=20))
mv(194, "Makara Surge", "WATER", P, 95, 100, 10, "Bursts out of the temple tank with a great wave.")
mv(195, "Burning Foam", "FIRE", S_, 80, 100, 10, "Hurls blazing lake foam. May burn.", st("BRN", 30))
mv(196, "Red Light", "ELECTRIC", X, 0, 100, 20, "A red signal that never turns green. Sharply lowers the foe's SPD.", stat("foe", SPD=-2))
mv(197, "Fresh Steam", "NORMAL", X, 0, 0, 10, "Steams itself fresh. Restores half its max HP.", dict(kind="heal", ratio=0.5))
mv(198, "Ancestor Call", "SPIRIT", S_, 70, 100, 15, "Calls on the ancestors for help.")
mv(199, "Ghee Roast", "FIRE", P, 75, 100, 15, "A sizzling body slam with extra ghee. May burn.", st("BRN", 10))
mv(200, "Cracker String", "FIRE", P, 18, 90, 15, "A string of crackers pops 2 to 5 times.", dict(kind="multi", min=2, max=5))
mv(201, "Hot Press", "FIRE", P, 85, 100, 10, "Presses down with a red-hot iron. May burn.", st("BRN", 20))
mv(202, "Claw Pinch", "WATER", P, 70, 95, 15, "Pinches with a huge claw. High critical-hit ratio.", dict(kind="highCrit"))
mv(203, "Ram Charge", "FIGHT", P, 95, 100, 10, "A head-down charge. The user takes recoil.", dict(kind="recoil", ratio=0.25))
mv(204, "Ancient Glow", "ROCK", S_, 60, 100, 5, "Light from the dawn of time. May raise all the user's stats.",
   stat("self", 10, ATK=1, DEF=1, SPC=1, SPD=1))
mv(205, "Puddle Splash", "EARTH", S_, 55, 100, 20, "Splashes muddy pothole water. May lower accuracy.", stat("foe", 30, ACC=-1))

MOVES = M
MOVE_BY_NAME = {m["name"]: m for m in M}
