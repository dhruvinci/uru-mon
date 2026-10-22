"""Items. category: CAPTURE | HEAL | STATUS | REVIVE | PP | REPEL | KEY. price 0 = can't be bought or sold."""

I = []


def it(id, name, category, price, description, **effect):
    I.append(dict(id=id, name=name, category=category, price=price, description=description, effect=effect))


it(1, "Filter Kaapi", "HEAL", 100, "Strong South Indian coffee. Restores 20 HP.", hp=20)
it(2, "Dabba", "CAPTURE", 200, "A steel tiffin box. Throw it at a weakened wild Urumon to catch it.", ball=1)
it(3, "Masala Dosa", "HEAL", 300, "Crisp and golden. Restores 60 HP.", hp=60)
it(4, "Bisi Bele Bath", "HEAL", 700, "Hot lentil rice with ghee. Restores 120 HP.", hp=120)
it(5, "Ragi Mudde", "HEAL", 1500, "A dense millet ball. Fully restores HP.", hp="full")
it(6, "Elaneer", "STATUS", 250, "Fresh tender coconut water. Cures any status problem.", cures="all")
it(7, "Mysore Pak", "REVIVE", 1500, "A rich sweet. Revives a fainted Urumon with half its HP.", revive=0.5)
it(8, "Chakli", "PP", 800, "A crunchy spiral snack. Restores 10 PP to every move.", pp=10)
it(9, "Steel Dabba", "CAPTURE", 600, "A sturdier two-tier tiffin. Better catch rate than a Dabba.", ball=1.5)
it(10, "Tiffin Carrier", "CAPTURE", 1200, "A four-tier carrier. Much better catch rate.", ball=2)
it(11, "Ajji's Dabba", "CAPTURE", 0, "Grandma's brass tiffin. Nothing has ever escaped it.", ball=255)
it(12, "Mosquito Coil", "REPEL", 350, "Its smoke keeps weak wild Urumon away for 100 steps.", steps=100)
it(13, "Neem Paste", "STATUS", 100, "Bitter but effective. Cures poison and burns.", cures=["PSN", "BRN"])
it(14, "Strong Kaapi", "STATUS", 100, "Extra-strong hot decoction. Wakes a sleeping Urumon, thaws a frozen one and cures paralysis.", cures=["SLP", "PAR", "FRZ"])
it(15, "Metro Card", "KEY", 0, "A smart card for Namma Metro. Ride between any stations you have visited.")
it(16, "Arena Badge Case", "KEY", 0, "Holds your Arena Badges.")
it(17, "Gaala", "KEY", 0, "A bamboo fishing rod. Face the water and press A to cast a line.")
it(18, "Old Moss Stone", "KEY", 0, "A layered green stone from deep in Nandi Cave. Prof. Sharada might know what's inside.")
it(19, "Old Shell Stone", "KEY", 0, "A stone with a curled-up bug-like shape in it. Prof. Sharada might know what's inside.")
it(20, "Ellu Bella", "HEAL", 2500, "Sesame, jaggery and coconut. Fully restores HP and cures any status problem.", hp="full", cures="all")
it(21, "Benne", "PP", 1800, "A lump of fresh butter. Fully restores the PP of every move.", pp=99)

ITEMS = I
