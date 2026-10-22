"""Scripted pieces for the 150 expansion, written once and placed by the map modules at whatever coordinates fit.

Each function takes coordinates and returns an npc / interactable / item / trigger dict. Flags used:
GOT_GAALA, CHAMPION_DONE, GANDA_DONE, BISILU_DONE, MUNGARU_DONE, CHALI_DONE, BENDA_DONE.
"""
from dsl import npc, say


# --- fishing --------------------------------------------------------------------------------------------------
def gaala_ajja(x, y, facing="DOWN"):
    """Old fisherman by the Lalbagh lake who gives the Gaala rod once. Stand him on the shore."""
    return npc("gaala_ajja", x, y, "ajja", facing=facing, script=[
        {"if": "GOT_GAALA", "then": [
            say("Face the water and press A to cast. Be patient. The lake gives to those who wait.",
                "Bigger lakes up north hide bigger Urumon. Some say even something from the temple carvings.",
                speaker="Fisherman Ajja")],
         "else": [
            say("Sixty years I've fished this lake. Back then the water was so clear you could count the pebbles.",
                "You look like you have patience, kanda. Here - my spare rod.", speaker="Fisherman Ajja"),
            {"giveItem": "Gaala"},
            {"setFlag": "GOT_GAALA"},
            say("Stand at the edge, face the water and press A. Every lake has its own Urumon.", speaker="Fisherman Ajja")]}])


# --- fossils --------------------------------------------------------------------------------------------------
def moss_stone(x, y):
    return dict(id="old_moss_stone", x=x, y=y, item="Old Moss Stone")


def shell_stone(x, y):
    return dict(id="old_shell_stone", x=x, y=y, item="Old Shell Stone")


def revival_machine(x, y):
    """Interactable in the lab: turns an old stone into a level-20 fossil Urumon."""
    def revive(item, species, name):
        return {"if": {"hasItem": item}, "then": [
            say(f"Prof. Sharada slides the {item} into the machine. It whirs, glows... and hums for a long time."),
            {"takeItem": item},
            {"giveMonster": {"species": species, "level": 20}},
            say(f"Three billion years later, {name} is alive again!")]}
    return dict(x=x, y=y, script=[
        {"if": {"any": [{"hasItem": "Old Moss Stone"}, {"hasItem": "Old Shell Stone"}]}, "then": [
            revive("Old Moss Stone", 139, "Paachikallu"),
            revive("Old Shell Stone", 141, "Kalluhula")],
         "else": [say("THE STONE READER. Prof. Sharada's machine for reading life out of ancient rock.",
                      "Lalbagh's rock is 3,000 million years old. Who knows what's sleeping in the cave rocks up north?")]}])


# --- post-game legendaries ------------------------------------------------------------------------------------
def _legend(flag, species, level, env, intro, caught_line, gone_line):
    return [
        {"cutscene": True},
        *[say(line) for line in intro],
        {"cutscene": False},
        {"battle": {"wild": {"species": species, "level": level}, "music": "MUSIC_LEGEND", "environment": env},
         "onWin": [{"setFlag": flag},
                   {"if": {"caught": species}, "then": [say(caught_line)], "else": [say(gone_line)]}],
         "onLose": []},
    ]


def gandaberunda(x, y):
    """Vidhana Soudha, after becoming Champion: stand-on trigger in front of the dome stairs (or a spot on the roof)."""
    return dict(id="gandaberunda", once=False, x=x, y=y, w=2, h=1, requires="CHAMPION_DONE", unless="GANDA_DONE",
                script=_legend("GANDA_DONE", 146, 60, "city",
                               ["The great seal above the doors begins to glow.",
                                "Two crowned heads turn towards you. The emblem of the old kingdom spreads its wings!"],
                               "Gandaberunda bows both heads. It will protect the land at your side.",
                               "Gandaberunda soars over the dome and fades into the seal."))


def bisilu(x, y):
    """Ramanagara rocks, on the highest boulder: interactable."""
    return dict(x=x, y=y, requires={"not": "BISILU_DONE"},
                script=_legend("BISILU_DONE", 147, 58, "hill",
                               ["The granite is too hot to touch. The air shimmers like a mirage...",
                                "A lion of sun-baked stone opens its molten eyes!"],
                               "The spirit of summer settles warmly into its Dabba.",
                               "Bisilu shakes its blazing mane and melts into the heat haze."))


def mungaru(x, y):
    """Hebbal lake shore after becoming Champion: interactable facing the water."""
    return dict(x=x, y=y, requires=["CHAMPION_DONE", {"not": "MUNGARU_DONE"}],
                script=_legend("MUNGARU_DONE", 148, 58, "lake",
                               ["Dark clouds pile up over the lake out of a clear sky. The first drop falls...",
                                "Thunder answers like a trumpet. A storm-cloud elephant wades out of the rain!"],
                               "The monsoon itself has joined your team. Better carry an umbrella.",
                               "Mungaru trumpets once more and the storm rolls away east."))


def chali(x, y):
    """Nandi Hills sunrise point after becoming Champion: interactable at the cliff edge."""
    return dict(x=x, y=y, requires=["CHAMPION_DONE", {"not": "CHALI_DONE"}],
                script=_legend("CHALI_DONE", 149, 58, "hill",
                               ["The sun rises over a sea of clouds. The fog below begins to take a shape...",
                                "A great hornbill made of morning mist glides up to the cliff!"],
                               "Chali folds its misty wings. Mornings will never be quite so cold again.",
                               "Chali circles once and dissolves into the sunrise."))


def bendakaalu(x, y):
    """Basavanagudi: an ajji at a groundnut-fair stall. After all four post-game legends she tells the old story."""
    return npc("benda_ajji", x, y, "ajji", facing="DOWN", script=[
        {"if": "BENDA_DONE", "then": [
            say("Have some boiled beans, kanda. Every city starts with someone being kind to a stranger.", speaker="Bean Ajji")],
         "else": [{"if": ["GANDA_DONE", "BISILU_DONE", "MUNGARU_DONE", "CHALI_DONE"], "then": [
             say("You've met the great spirits of this land? Then you should hear the oldest story of all.",
                 "A king once got lost hunting in the forest here. Hungry and tired, he met an old woman.",
                 "She had nothing but a pot of boiled beans - benda kaalu - and she gave him all of it.",
                 "He named the place Benda-Kaalu-Ooru. Bengaluru.", speaker="Bean Ajji"),
             say("...Oh! One of the beans in the pot is glowing!"),
             {"battle": {"wild": {"species": 150, "level": 50}, "music": "MUSIC_LEGEND", "environment": "city"},
              "onWin": [{"setFlag": "BENDA_DONE"},
                        {"if": {"caught": 150}, "then": [say("The little bean that named a city is travelling with you now.")],
                         "else": [say("The glowing bean hops back into the pot and goes quiet. Some stories stay where they began.")]}],
              "onLose": []}],
             "else": [say("Groundnuts! Hot boiled beans! Best at the fair, kanda.",
                          "My grandmother's grandmother sold beans on this very street. Come back when you've seen more of the land - I'll tell you a story.",
                          speaker="Bean Ajji")]}]}])
