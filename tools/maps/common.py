"""Shared scripts and interiors used by many towns."""
from dsl import room, warp, npc, say


def shop_list():
    """Kirana stock grows with the number of badges."""
    tiers = [
        (0, ["Dabba", "Filter Kaapi", "Neem Paste", "Strong Kaapi", "Mosquito Coil"]),
        (1, ["Masala Dosa", "Elaneer"]),
        (2, ["Steel Dabba"]),
        (3, ["Bisi Bele Bath", "Mysore Pak"]),
        (4, ["Tiffin Carrier", "Chakli"]),
        (5, ["Ragi Mudde"]),
    ]
    branches = None
    for need in range(5, -1, -1):
        items = [i for n, lst in tiers if n <= need for i in lst]
        cmd = {"shop": items, "greeting": "Namaskara! What can I get you?"}
        if branches is None:
            branches = [cmd]
        else:
            branches = [{"if": {"badges": need + 1}, "then": branches, "else": [cmd]}]
    return branches


DARSHINI_OWNER = [
    say("Namaskara! Welcome to the Darshini.", "Shall I feed your Urumon some hot idli and chutney? On the house!", speaker="Owner"),
    {"ask": "Rest your Urumon?", "yes": [
        say("Two plates idli-vada, extra chutney! Coming right up!", speaker="Owner"),
        {"heal": True, "setRespawn": True},
        say("There! Fresh as a morning filter kaapi. Come again, okay?", speaker="Owner"),
    ], "no": [say("Okay, okay. The tava is always hot if you change your mind.", speaker="Owner")]},
]


def darshini():
    c, walls = room(11, 9, "t", exit_x=5)
    return dict(
        id="darshini", name="Darshini", music="MUSIC_DARSHINI", interior=True, environment="indoor",
        layout=c.layout(), walls=walls, ground="tile_floor",
        props=[("darshini_counter", 4, 3), ("table", 1, 5), ("table", 8, 5), ("cloud_kiosk", 9, 2), ("plant_pot", 0, 7),
               ("pooja_shelf", 1, 2)],
        counters=[[4, 3], [5, 3], [6, 3]],
        warps=[warp("exit", 5, 8, "@return", exit="UP", dir="DOWN")],
        npcs=[
            npc("owner", 5, 2, "darshini_owner", facing="DOWN", script=DARSHINI_OWNER, noTurn=False),
            npc("cust1", 2, 6, "techie_m", facing="UP", script=[
                say("I come here every morning before office. Best kaapi in the city. Don't tell my mother.")]),
            npc("cust2", 8, 7, "ajja", facing="LEFT", script=[
                say("Standing and eating is good for digestion. That's why darshinis have no chairs. Ha!")]),
        ],
        interactables=[dict(x=9, y=2, script=[{"storage": True}]), dict(x=9, y=3, script=[{"storage": True}])],
        respawnText=["The darshini owner nursed your Urumon back to health with hot idli.",
                     "\"They were completely exhausted! Be careful out there, okay?\""],
    )


def kirana():
    c, walls = room(10, 8, "t", exit_x=4, wall="shop")
    return dict(
        id="kirana", name="Kirana Store", music="MUSIC_DARSHINI", interior=True, environment="indoor",
        layout=c.layout(), walls=walls, ground="tile_floor",
        props=[("shop_shelf", 0, 2), ("shop_shelf", 6, 2), ("shop_shelf", 8, 2), ("shop_shelf", 6, 5), ("shop_shelf", 8, 5),
               ("darshini_counter", 1, 4), ("plant_pot", 9, 7)],
        counters=[[1, 4], [2, 4], [3, 4]],
        warps=[warp("exit", 4, 7, "@return", exit="UP", dir="DOWN")],
        npcs=[
            npc("clerk", 2, 3, "shopkeeper", facing="DOWN", script=shop_list()),
            npc("shopper", 7, 4, "woman2", facing="UP", movement="LOOK", script=[
                say("Dabbas are buy ten, get ten... no wait, that was the onions.")]),
        ],
    )


def metro_staff(id, x, y, station_name):
    return npc(id, x, y, "metro_staff", facing="DOWN", script=[
        say(f"Welcome to Namma Metro, {station_name} station.", speaker="Metro Staff"),
        {"if": {"hasItem": "Metro Card"}, "then": [{"metro": True}],
         "else": [say("Sorry, you need a Metro Card to ride. They're given out by the city office... for good citizens.",
                      speaker="Metro Staff")]},
    ])
