"""Every trainer in the game. Species may be an id or "RIVAL:n" (stage n of Rohan's starter line).

Prize money = base x the highest level on the team.
"""

TRAINERS = {}

# portrait art per trainer class (art-src prompts live in tools/content/portraits_data.py)
CLASS_BASE = {
    "Schoolkid": 12, "College Student": 18, "Techie": 32, "Auto Driver": 24, "Cricketer": 26, "Gardener": 20,
    "Fisher": 18, "Jogger": 22, "Street Vendor": 20, "Wrestler": 28, "Dancer": 26, "Ajja": 30, "Ajji": 30,
    "Birdwatcher": 24, "Delivery Rider": 24, "Syndicate Grunt": 26, "Syndicate Admin": 50, "Syndicate Boss": 90,
    "Arena Leader": 110, "Council": 140, "Rival": 45, "Champion": 200,
}


def tr(id, name, title, portrait, team, intro, defeat, after=None, ai=1, sprite=None, **extra):
    base = CLASS_BASE.get(title, 25)
    prize = base * max(t[1] for t in team)
    TRAINERS[id] = dict(
        name=name, title=title, portrait=portrait, sprite=sprite or portrait,
        team=[dict(species=t[0], level=t[1], **({"moves": t[2]} if len(t) > 2 else {})) for t in team],
        prize=prize, aiLevel=ai, intro=intro if isinstance(intro, list) else [intro],
        defeat=defeat if isinstance(defeat, list) else [defeat],
        after=after if after is None or isinstance(after, list) else [after], **extra)


# ---------------------------------------------------------------------------------------------
# Rival: Rohan
# ---------------------------------------------------------------------------------------------
tr("rival_lab", "Rohan", "Rival", "rival", [("RIVAL:1", 5)],
   ["Wait, {PLAYER}! Let's see whose Urumon is stronger. Best of one - no rematches!"],
   ["What?! I picked the wrong one... no, I just need practice!"], canLose=True, music="MUSIC_RIVAL")
tr("rival_mg", "Rohan", "Rival", "rival", [(11, 14), (13, 13), ("RIVAL:1", 16)],
   ["{PLAYER}! Took you long enough to get through Cubbon Park.",
    "I've been training at the stadium nets every evening. Watch this!"],
   ["Arre! I was this close. I'm going to beat Gundappa first, just watch."],
   music="MUSIC_RIVAL", ai=1)
tr("rival_whitefield", "Rohan", "Rival", "rival", [(11, 24), (45, 23), (28, 23), ("RIVAL:2", 26)],
   ["Silk Board took me three hours. THREE HOURS, {PLAYER}.",
    "I'm in a terrible mood. Perfect for a battle!"],
   ["Fine, fine. You're good. Annoyingly good."], music="MUSIC_RIVAL", ai=1)
tr("rival_palace", "Rohan", "Rival", "rival", [(12, 36), (46, 35), (29, 35), (57, 35), ("RIVAL:3", 38)],
   ["The Syndicate is heading for Nandi Hills. Grandma's worried sick.",
    "Before we go after them, I need to know you're ready. Show me!"],
   ["...Yeah. You're ready. Let's stop them together. You go first - I'll cover the hill roads."],
   music="MUSIC_RIVAL", ai=2)
tr("champion", "Rohan", "Champion", "rival",
   [(12, 44), (57, 45), (41, 44), (50, 45), (46, 44), ("RIVAL:3", 48)],
   ["Hey, {PLAYER}. Surprised? I beat the Council an hour before you.",
    "Every route, every Arena - I was always one step ahead. Or one step behind.",
    "This is it. The Champion of Namma Bengaluru is decided right here. No holding back!"],
   ["...I lost. You really are the best, {PLAYER}.",
    "Grandma's going to be insufferable about this. Congratulations, Champion."],
   music="MUSIC_RIVAL", ai=2, environment="arena", isLeader=True)

# ---------------------------------------------------------------------------------------------
# Arena leaders
# ---------------------------------------------------------------------------------------------
tr("leader_hoovamma", "Hoovamma", "Arena Leader", "hoovamma", [(54, 9), (52, 10), (2, 12)],
   ["Ah, a young visitor in my Glass House! Mind the orchids, dear.",
    "Sixty years I have tended these gardens. Plants are patient, and patience wins battles.",
    "Show me what you have grown into!"],
   ["My, my. You bloom quickly. Take this - the GRASS Badge."],
   after=["Water your Urumon with kindness and they will grow tall.",
          "Keep the GRASS Badge shining, dear. The flower-show crowd will let you pass north now."],
   ai=1, isLeader=True, environment="arena", music="MUSIC_LEADER")
tr("leader_gundappa", "Gundappa", "Arena Leader", "gundappa", [(30, 17), (60, 17), (31, 19)],
   ["Thirty years ago I bowled the fastest spell this stadium ever saw.",
    "Now I coach. Rule one: no fear of the short ball.", "Pad up, kid. Let's play!"],
   ["Clean bowled! Superb line and length. The FIGHT Badge is yours."],
   after=["The traffic police at the east junction will let you through with that badge.",
          "Silk Board is... well. You'll see. Carry snacks."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_LEADER")
tr("leader_tanvi", "Tanvi", "Arena Leader", "tanvi", [(47, 22), (49, 22), (56, 23), (48, 25)],
   ["Welcome to my startup's demo day! Today's pitch: you, losing.",
    "We iterate fast here. Let's ship this battle!"],
   ["Okay, pivot... pivot... no, I'm out of runway. Here's the ELECTRIC Badge."],
   after=["Something weird is going on at Bellandur Lake. My sensors show the foam spiking.",
          "The security folks at the south gate will let a badge-holder through. Go check it out?"],
   ai=2, isLeader=True, environment="arena", music="MUSIC_LEADER")
tr("leader_vidya", "Vidya", "Arena Leader", "vidya", [(38, 29), (35, 29), (39, 31)],
   ["Sit down. Notebooks out. Today's lesson: type matchups.", "There will be a test. It starts now."],
   ["Full marks. I'm proud of you. Here is the MIND Badge."],
   after=["Revision is the secret. Revisit your weak matchups.",
          "The old palace to the east has a Leader who deals in spirits. Be brave."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_LEADER")
tr("leader_rukmini", "Rukmini", "Arena Leader", "rukmini", [(36, 32), (33, 33), (63, 34), (37, 36)],
   ["The palace was built for a king. Now it belongs to the spirits who stayed behind.",
    "They have been whispering about you... shall we see if they're right?"],
   ["The spirits are smiling. They accept you. Take the SPIRIT Badge."],
   after=["The spirits are restless tonight. They say the northern hills are in danger.",
          "Rohan rushed north on Palace Road. You should follow him."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_LEADER")
tr("leader_akash", "Akash", "Arena Leader", "akash", [(17, 40), (42, 41), (12, 41), (25, 43)],
   ["Up here the wind does whatever it wants. Sunrise, mist, monsoon - all in an hour.",
    "My team rides those winds. Can you keep your feet on the ground?"],
   ["Grounded! What a battle. You've earned the SKY Badge - your sixth!"],
   after=["Six badges! The guards at Vidhana Soudha will open the gates for you now.",
          "Take the Metro back to MG Road. The Namma Council is waiting."],
   ai=2, isLeader=True, environment="hill", music="MUSIC_LEADER")

# ---------------------------------------------------------------------------------------------
# Namma Council
# ---------------------------------------------------------------------------------------------
tr("council_nagaraj", "Nagaraj", "Council", "nagaraj", [(44, 44), (21, 44), (19, 45), (23, 46)],
   ["I am Nagaraj of the Namma Council. My Urumon were born where the city's waste goes.",
    "Poison is just what the city leaves behind. Can you survive it?"],
   ["You've cleared the fumes. Go on, the next councillor awaits."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_COUNCIL")
tr("council_basappa", "Basappa", "Council", "basappa", [(27, 45), (53, 45), (41, 46), (59, 47)],
   ["Ho ho! Basappa's the name. These rocks are older than the city itself.",
    "You'll need more than a shovel to move them!"],
   ["Hah! You dug right through us. Off you go!"],
   ai=2, isLeader=True, environment="arena", music="MUSIC_COUNCIL")
tr("council_kaveri", "Kaveri", "Council", "kaveri", [(46, 46), (23, 46), (9, 47), (25, 48)],
   ["Every lake in this city was once full and clear. I fight so they will be again.",
    "Let the water decide who is worthy."],
   ["The water flows your way. One councillor remains."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_COUNCIL")
tr("council_agni", "Agni", "Council", "agni", [(55, 47), (63, 48), (61, 48), (6, 49)],
   ["They call me Agni. I'm the last fire before the Champion.",
    "Let's turn the heat all the way up!"],
   ["Burned out... You're the real thing. The Champion is waiting beyond that door."],
   ai=2, isLeader=True, environment="arena", music="MUSIC_COUNCIL")

# ---------------------------------------------------------------------------------------------
# Concrete Syndicate
# ---------------------------------------------------------------------------------------------
tr("grunt_cubbon1", "Grunt", "Syndicate Grunt", "grunt_m", [(20, 10), (43, 11)],
   ["Oi! This park is going to be a parking lot. Move it, kid!"],
   ["Ugh. The boss won't like this."], after=["We were only cutting the dead trees! ...Mostly."], sprite="grunt_m")
tr("grunt_cubbon2", "Grunt", "Syndicate Grunt", "grunt_f", [(18, 11), (20, 12)],
   ["The Concrete Syndicate builds the future! Trees don't pay rent!"],
   ["Fine! We'll find another park. There's always another park."], sprite="grunt_f")
tr("grunt_bell1", "Grunt", "Syndicate Grunt", "grunt_m", [(22, 23), (20, 24)],
   ["The foam? Totally natural. Nothing to see here."], ["Okay, maybe it's not natural."], sprite="grunt_m")
tr("grunt_bell2", "Grunt", "Syndicate Grunt", "grunt_f", [(21, 24), (43, 23), (18, 24)],
   ["You're not allowed past the hoarding. Site is under construction!"], ["Our site! Our beautiful site..."],
   sprite="grunt_f")
tr("grunt_bell3", "Grunt", "Syndicate Grunt", "grunt_m", [(26, 24), (22, 25)],
   ["Admin Shetty is busy dumping - I mean, disposing of - very important stuff."], ["Shetty sir is going to fire me."],
   sprite="grunt_m")
tr("admin_shetty", "Shetty", "Syndicate Admin", "admin", [(22, 26), (21, 26), (53, 27)],
   ["Who let a child onto my site? Do you know how much this land is worth per square foot?",
    "This lake is just a very large, very wet plot. And I'm going to fill it."],
   ["Bah! Boss Bhaskar has bigger plans anyway. Up on the hills, the real project begins.",
    "Enjoy your stinky lake, kid."], ai=2, sprite="bhaskar")
tr("grunt_nandi1", "Grunt", "Syndicate Grunt", "grunt_m", [(21, 34), (59, 33)],
   ["Halt! The hill is closed for a private event. Very private."], ["The private event has been... postponed."],
   sprite="grunt_m")
tr("grunt_nandi2", "Grunt", "Syndicate Grunt", "grunt_f", [(19, 34), (44, 34), (20, 35)],
   ["We're going to put a resort on the summit. Infinity pool! Helipad!"], ["There goes my employee discount."],
   sprite="grunt_f")
tr("grunt_nandi3", "Grunt", "Syndicate Grunt", "grunt_m", [(27, 35), (62, 35)],
   ["The boss is waiting for sunrise. That's when the guardian shows itself."], ["Ow. Okay, you can go see the boss. Your funeral."],
   sprite="grunt_m")
tr("boss_bhaskar", "Bhaskar", "Syndicate Boss", "bhaskar", [(21, 38), (59, 38), (65, 41)],
   ["So you're the brat who keeps wrecking my projects.",
    "Do you know what this city needs? Flyovers. Malls. Towers. Concrete.",
    "And the guardian of this 'Garden City' keeps everything green and wet and SLOW.",
    "At sunrise I capture it, and Bengaluru finally becomes what it should be: mine.",
    "Concretor! Pour!"],
   ["My Concretor... cracked? By a child?",
    "Fine. FINE. Keep your trees and your lakes and your traffic.",
    "But the city will choose concrete in the end. It always does."],
   ai=2, isLeader=True, music="MUSIC_SYNDICATE", environment="cave")

# ---------------------------------------------------------------------------------------------
# Everyday trainers (route by route)
# ---------------------------------------------------------------------------------------------
tr("r1_kid", "Chinnu", "Schoolkid", "schoolboy", [(13, 4), (10, 4)],
   ["Summer holidays! No homework, only battles!"], ["Waaah! Okay, maybe I'll do my homework."])
tr("r1_jogger", "Priya", "Jogger", "jogger", [(10, 5), (28, 5)],
   ["I jog this road every morning before the traffic starts. Keep up!"], ["Phew... I need a coconut."])
tr("r1_vendor", "Manju", "Street Vendor", "vendor", [(52, 6)],
   ["Hot bajji! Hot bajji! ...And a battle, if you want."], ["Here, take a free bajji for the road. Wait, I ate it."])
tr("lb_gardener", "Ramesh", "Gardener", "gardener", [(54, 9), (52, 9)],
   ["The Glass House is no place for weeds like you!"], ["You're no weed. You're a whole tree."])
tr("lb_college", "Sneha", "College Student", "college_f", [(15, 8), (16, 10)],
   ["We're on a botany field trip. You're my field test!"], ["Note to self: study harder."])
tr("cp_bird", "Arvind", "Birdwatcher", "birdwatcher", [(10, 9), (34, 9), (11, 10)],
   ["Shh! I'm counting sparrows. Unless you'd like to battle, quietly."], ["Oh! A rare sighting: my own defeat."])
tr("cp_jogger", "Kavitha", "Jogger", "jogger", [(13, 10), (30, 11)],
   ["Ten laps of Cubbon Park before office. Battle you in between!"], ["Nine laps. Good enough."])
tr("cp_kid", "Tejas", "Schoolkid", "schoolboy", [(15, 8), (18, 9), (15, 9)],
   ["I caught this one near the bandstand!"], ["I'll catch a stronger one tomorrow."])
tr("cp_college", "Farhan", "College Student", "college_m", [(32, 11), (36, 10)],
   ["Bunking class to battle? Totally worth it."], ["Okay maybe not totally worth it."])
tr("st_cricketer1", "Vinay", "Cricketer", "cricketer", [(28, 15), (60, 16)],
   ["Coach Gundappa says I bowl like a sleepy cow. Let's see what you say!"], ["Wide ball. Wide everything."])
tr("st_cricketer2", "Shreya", "Cricketer", "cricketer", [(30, 16), (31, 17)],
   ["Nets session is on. You're the batter. I'm the fast bowler."], ["Six! Out of the stadium. Wow."])
tr("mg_techie", "Nikhil", "Techie", "techie_m", [(49, 14), (47, 15)],
   ["I have a standup in ten minutes. This'll be quick."], ["...I'm going to be late for standup."])
tr("mg_dancer", "Lakshmi", "Dancer", "dancer", [(60, 15), (34, 15)],
   ["My Urumon learned their steps at the Ranga Shankara workshop!"], ["Beautiful footwork. Yours, not mine."])
tr("sb_auto1", "Raju", "Auto Driver", "auto_driver", [(51, 18), (28, 17)],
   ["Whitefield? Meter plus fifty. Or battle me for a free ride!"], ["Okay okay, meter only. Final offer."])
tr("sb_auto2", "Shiva", "Auto Driver", "auto_driver", [(20, 17), (21, 18), (51, 19)],
   ["Signal is red for another forty minutes. Plenty of time!"], ["Oh, signal is green. Bye!"])
tr("sb_rider", "Imran", "Delivery Rider", "delivery_rider", [(47, 18), (11, 19)],
   ["Your order is arriving in ten minutes! ...After this battle."], ["Order delayed due to unexpected defeat."])
tr("sb_techie", "Divya", "Techie", "techie_f", [(49, 18), (56, 18)],
   ["I left the office at six. It is now nine. Battle me so I feel productive."], ["At least my code compiles."])
tr("sb_college", "Rahul", "College Student", "college_m", [(18, 18), (32, 19)],
   ["Engineering college in the morning, Silk Board all evening."], ["My CGPA and my battle record are similar."])
tr("wf_techie1", "Arjun", "Techie", "techie_m", [(49, 21), (47, 22)],
   ["Our Leader's demo day is legendary. Pass my code review first!"], ["LGTM. Looks good to... you."])
tr("wf_techie2", "Meghana", "Techie", "techie_f", [(56, 22), (49, 22)],
   ["Ping! You've got a battle invite. Accept?"], ["Merged and deployed. Right into the ground."])
tr("bl_fisher", "Bhoja", "Fisher", "fisher", [(24, 22), (24, 23), (22, 23)],
   ["The fish have all gone weird since the foam came."], ["Even my Meenu is ashamed of me."])
tr("sk_ajja", "Ramaiah", "Ajja", "ajja", [(29, 24), (34, 25)],
   ["In my day, Sankey Tank was clear enough to see your face in. Let's battle like old times!"],
   ["Ha! You remind me of my younger days. Here, have some peanuts."])
tr("sk_ajji", "Saroja", "Ajji", "ajji", [(38, 24), (36, 25)],
   ["Eat properly before you battle, child! You look thin."], ["Good, good. Now go eat something."])
tr("sk_bird", "Gautam", "Birdwatcher", "birdwatcher", [(42, 25), (35, 26)],
   ["The kites circle highest over Sankey Tank in the afternoon."], ["I need better binoculars. And Urumon."])
tr("ml_college", "Ananya", "College Student", "college_f", [(38, 27), (34, 28)],
   ["Vidya ma'am's tuition is the hardest in the city. Prove you're ready!"], ["I should revise chapter four again."])
tr("ml_kid", "Pavan", "Schoolkid", "schoolboy", [(39, 28)],
   ["I get top marks in class AND in battles!"], ["...I'm crying because of onions. Not because I lost."])
tr("pr_dancer", "Meera", "Dancer", "dancer", [(62, 31), (36, 31)],
   ["The palace corridors are a perfect stage. Watch!"], ["The spirits applauded you, not me."])
tr("pr_ajja", "Narasimha", "Ajja", "ajja", [(33, 32), (37, 32)],
   ["I've walked past this palace for seventy years and I still hear things at night."], ["Brr. You give me shivers too."])
tr("pr_cricketer", "Sachin", "Cricketer", "cricketer", [(31, 31), (61, 32), (29, 31)],
   ["Palace grounds has the best pitch for gully cricket. And battles!"], ["Run out! By a mile!"])
tr("hb_rider", "Faisal", "Delivery Rider", "delivery_rider", [(51, 33), (47, 34)],
   ["Delivering biryani to Nandi Hills. Don't ask."], ["Biryani's getting cold. Go, go!"])
tr("hb_wrestler", "Hanuma", "Wrestler", "wrestler", [(31, 34), (61, 35)],
   ["Morning kusti practice by the lake. You're my sparring partner!"], ["Pinned! I'm proud of you, small one."])
tr("hb_fisher", "Kiran", "Fisher", "fisher", [(25, 33), (46, 33)],
   ["Hebbal lake's still got some fight in it. Like me!"], ["Okay, okay, the fish win today. And you."])
tr("nh_bird", "Shalini", "Birdwatcher", "birdwatcher", [(12, 36), (35, 37)],
   ["You can see clouds BELOW you up here. Beautiful, isn't it?"], ["The view is still beautiful. I'm not."])
tr("nh_wrestler", "Bheema", "Wrestler", "wrestler", [(31, 38), (61, 37)],
   ["I climbed the 1,200 steps for training. Every morning!"], ["...I'm taking the bus down."])

TRAINER_TABLE = TRAINERS

# badge awards after beating each Arena Leader
for _tid, _badge in (("leader_hoovamma", "GRASS"), ("leader_gundappa", "FIGHT"), ("leader_tanvi", "ELECTRIC"),
                     ("leader_vidya", "MIND"), ("leader_rukmini", "SPIRIT"), ("leader_akash", "SKY")):
    TRAINERS[_tid]["onWin"] = [{"badge": _badge}]

# ---------------------------------------------------------------------------------------------
# Arena junior trainers (each Arena has its own)
# ---------------------------------------------------------------------------------------------
tr("ar_tuition1", "Rohit", "Schoolkid", "schoolboy", [(34, 27), (38, 28)],
   ["Ma'am says whoever loses today gets double homework!"], ["Double homework... again."])
tr("ar_tuition2", "Kavya", "College Student", "college_f", [(38, 28), (14, 27), (35, 29)],
   ["I've topped every test in this tuition. Battles are just another test."], ["I... got a question wrong?"])
tr("ar_palace1", "Leela", "Dancer", "dancer", [(36, 31), (62, 31)],
   ["The palace spirits dance with me at midnight. Care to join?"], ["The spirits stopped dancing. That's never happened."])
tr("ar_palace2", "Venkatesh", "Ajja", "ajja", [(33, 32), (40, 31), (37, 33)],
   ["I was a palace guard for forty years. I still do my rounds. Out of habit."], ["Old legs, young heart. Well fought!"])
tr("ar_pavilion1", "Varun", "Birdwatcher", "birdwatcher", [(11, 38), (34, 38), (42, 39)],
   ["I paraglide off this hill every weekend. My Urumon taught me how!"], ["Grounded. Literally."])
tr("ar_pavilion2", "Nandini", "Jogger", "jogger", [(17, 39), (12, 40)],
   ["Running up Nandi's steps every morning makes you strong. Like, really strong."], ["...Okay, I need to run more steps."])
tr("ar_glass1", "Shanthi", "Gardener", "gardener", [(52, 10), (54, 10)],
   ["Every plant in this Glass House has a name. This one is called 'Your Defeat'."], ["You're sprouting fast, young one."])
tr("ar_stadium1", "Prakash", "Cricketer", "cricketer", [(30, 15), (13, 16), (60, 16)],
   ["I've been twelfth man for six seasons. Today I play!"], ["Back to carrying drinks, I suppose."])
tr("ar_tech1", "Sahana", "Techie", "techie_f", [(49, 22), (47, 23)],
   ["Our Leader built her first startup in her hostel room. I built mine in a hackathon!"], ["Segfault. Core dumped. That was me."])
