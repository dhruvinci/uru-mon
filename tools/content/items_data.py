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
it(14, "Strong Kaapi", "STATUS", 100, "Extra-strong decoction. Wakes up a sleeping Urumon and cures paralysis.", cures=["SLP", "PAR"])
it(15, "Metro Card", "KEY", 0, "A smart card for Namma Metro. Ride between any stations you have visited.")
it(16, "Arena Badge Case", "KEY", 0, "Holds your Arena Badges.")

ITEMS = I
