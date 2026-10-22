# uru-mon — Game Design

A GBA-style creature-collecting RPG set in **Bengaluru**. Creatures are called **Urumon** ("ūru" is Kannada for town/home; Bengal-*uru*). Everything (names, art, music, text) is original; mechanics deliberately mirror the classic genre.

## Pillars
- Feels like a GBA-era monster RPG: 16 px tiles scaled ×4, grid movement, turn-based battles, 6-creature party, gyms ("Arenas"), badges, a league.
- Unmistakably Bengaluru: filter coffee, darshinis, autos, potholes, power cuts, lakes and foam, jacaranda season, tech parks, metro, cricket, Kannada words.
- Plays in a browser on desktop **and phones** (touch D-pad + A/B/START overlay).

## Vocabulary (genre term → ours)
| Genre | uru-mon |
|---|---|
| capture ball | **Dabba** (steel tiffin box) |
| healing center | **Darshini** (standing-only South Indian eatery; the owner heals your team with idli) |
| mart | **Kirana** store |
| encyclopedia | **Uru-Pustaka** (pustaka = book) |
| PC storage | **Namma Cloud** box |
| gym / leader | **Arena** / Arena Leader |
| villain team | **Concrete Syndicate** (hard hats, hi-vis vests) — want to pave lakes and parks |
| league | **Namma Council** at Vidhana Soudha |
| currency | ₹ |

## Battle rules (see `src/battle/engine/`)
- 14 types: NORMAL FIRE WATER GRASS ELECTRIC EARTH ROCK SKY BUG TOXIC FIGHT MIND SPIRIT METAL (chart in `type-chart.js`).
- 5 stats: HP, ATK, DEF, SPC (special atk+def), SPD. Base stats per species; each individual has a 0–15 "spark" per stat.
  - `HP = floor((2·(B+s)·L)/100) + L + 10`, others `floor((2·(B+s)·L)/100) + 5`.
- Moves: type, category (PHYSICAL uses ATK/DEF, SPECIAL uses SPC/SPC, STATUS), power, accuracy, PP, priority, optional effect.
- Damage: `floor(floor(floor(2L/5+2)·P·A/D)/50)+2` × STAB 1.5 × type × crit 1.5 (1/16; high-crit moves 1/8) × random 0.85–1.0. Burn halves physical damage.
- Status: BRN (1/16 HP per turn), PSN (1/8), PAR (speed ×½, 25% full-para), SLP (1–3 turns).
- Stat stages −6…+6 for ATK DEF SPC SPD ACC EVA.
- Turn order: priority, then speed (paralysis applied), ties random.
- AI: wild = random usable move; trainers = weighted by expected damage; leaders/council = best move most of the time, status moves when sensible.
- EXP: `floor(baseExp·L/7)` (×1.5 trainer). Active creature full, rest of conscious party half. Growth curve `L³`.
- Level-up: learn moves from learnset (prompt to forget if 4 known), evolve after battle at evolution level.
- Catch: `a = (3M − 2H)·rate·ball / 3M · status(SLP 2, other 1.5)`; 4 shake checks.
- Blackout: warp to last Darshini, lose half ₹.

## Region (outdoor maps, south → north)
1. **Basavanagudi** — home town. Player's house, rival Sudeep's house, Prof. Sharada's **Urumon Lab**, Bugle Rock.
2. **Route 1 · South End Road** — first grass.
3. **Lalbagh** — Glass House **Arena 1 (GRASS)**, Leader **Hoovamma**. Darshini, Kirana.
4. **Cubbon Park** — wooded maze; Syndicate grunts cutting trees.
5. **MG Road** — city hub, Metro station, **Arena 2 (FIGHT)** in Chinnaswamy Stadium, Leader **Gundappa**. Vidhana Soudha gate (needs 6 badges).
6. **Route 3 · Silk Board** — the infamous traffic junction; autos everywhere.
7. **Whitefield** — tech parks, **Arena 3 (ELECTRIC)**, Leader **Tanvi** (startup founder).
8. **Bellandur Lake** — foaming lake; Syndicate dumping sludge (story event, gives Metro Card).
9. **Route 5 · Sankey Tank** — lake path from MG Road north.
10. **Malleshwaram** — old neighbourhood, **Arena 4 (MIND)**, Leader **Vidya** (tutor).
11. **Palace Road** — Bangalore Palace, **Arena 5 (SPIRIT)**, Leader **Rukmini**.
12. **Route 7 · Hebbal** — flyover and lake toward the hills.
13. **Nandi Hills** — climb + cave; Syndicate HQ climax vs **Boss Bhaskar**; legendary **Udyanaga** at the summit; **Arena 6 (SKY)**, Leader **Akash**.
14. **Vidhana Soudha** — Namma Council: Nagaraj (TOXIC), Basappa (ROCK), Kaveri (WATER), Agni (FIRE), then Champion **Sudeep**.

## Story beats
1. Amma wakes you; Prof. Sharada's lab; choose starter (Jakkafawn / Kaapup / Elanee); Sudeep takes the one strong against yours; first battle.
2. Route 1 → Lalbagh badge. Grunts in Cubbon Park chopping trees — first Syndicate battle.
3. MG Road badge → Silk Board → Whitefield badge.
4. Bellandur: stop the sludge dumping; grateful BBMP officer gives **Metro Card** (fast travel between visited Metro stations).
5. Malleshwaram badge → Palace badge. Sudeep tells you the Syndicate is heading to Nandi Hills.
6. Nandi Hills: fight through the cave, defeat Boss Bhaskar; Udyanaga appears (catchable); Arena 6 at the summit.
7. Vidhana Soudha: Council ×4 → Champion Sudeep → credits.

## Art pipeline
- World tiles & characters: authored as code (`tools/art/`), 16 px, rendered to PNG; displayed ×4 with `pixelArt: true`.
- Maps: `tools/maps/` compile a text layout + object list → `assets/maps/<id>/{bg,fg}.png` + Tiled-format JSON (collision, encounters, objects).
- Creatures, trainer portraits, battle backgrounds, title art: generated with Codex image gen, then cleaned (`tools/art/pixelize.py`: crop, downscale, palette-quantize, transparent background).
- Audio: synthesized chiptune (`tools/audio/`).
