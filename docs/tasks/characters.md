# Task: procedural overworld character sprites

Create `tools/art/characters.py` (Python 3, Pillow + numpy only; do not install anything) that procedurally generates
GBA-era (think 2004 handheld monster RPGs) overworld character spritesheets for **uru-mon**, a game set in Bengaluru, India.
Read `docs/DESIGN.md` for context.

## Format
- Frame: **16×24 px**, native resolution (no upscaling in the output files). Transparent background (RGBA).
- Sheet: 3 columns × 4 rows → **48×96 px** PNG. Rows (top→bottom): DOWN, UP, LEFT, RIGHT. Columns: STAND, STEP_A, STEP_B.
  The game plays walking as STEP_A, STAND, STEP_B, STAND. RIGHT must be the exact horizontal mirror of LEFT.
- Feet touch the bottom of the frame (rows 22–23). Chibi proportions: big head (~rows 1–11), short body and legs.
- 1 px dark outline (use `#2a2230`, never pure black) around the whole silhouette; 2–3 tone shading per material;
  eyes visible facing down/left/right; back of head on UP.
- Walk frames: legs alternate, arms swing opposite, 1 px body bob on step frames. STAND frames must line up exactly so
  idle doesn't jitter.

## How to author
Hand-author the base body as ASCII pixel grids **inside the file** (per direction and frame) using role letters
(outline, skin, skin-shade, hair, hair-shade, eye, top, top-shade, bottom, bottom-shade, shoe, accent...). Then build
variants by recolouring roles and applying overlay grids for hair styles, headwear and long garments. Don't draw bodies
with ellipse/rectangle primitives — they read as blobs at this size.

## Parameters
- skin tone: at least 5 Indian skin tones from light wheatish to deep brown
- hair: short, side-part, curly, ponytail, long braid, bun, bald, grey-short (elderly); any colour
- headwear: none, cricket cap (colour), construction hard hat (yellow), bike helmet (colour), white police-style cap
- top: t-shirt, collared shirt, kurta (long, to the knees), saree (draped over one shoulder, full-length), lab coat (white,
  long), school uniform (white shirt + tie), hi-vis vest over shirt (orange with a reflective stripe), sports jersey,
  hoodie, suit jacket
- bottom: pants, shorts, jeans, lungi/dhoti (white wrap with coloured border), skirt
- extras: glasses, backpack, moustache, walking stick, apron, binoculars

## Presets (`CHARACTERS` dict, ~45 entries)
Story: `player_boy`, `player_girl`, `rival` (Rohan: blue cricket jersey, cap), `professor` (Prof. Sharada: woman, white
lab coat over a saree, glasses, bun), `amma` (player's mother, saree), `rohan_mom`.
Arena leaders: `hoovamma` (elderly woman gardener, green saree, grey bun), `gundappa` (burly ex-fast-bowler coach,
tracksuit, moustache), `tanvi` (young startup founder, hoodie, glasses), `vidya` (tutor, kurta, braid, glasses),
`rukmini` (elegant woman, purple saree, long hair), `akash` (young man, aviator-style jacket).
Council: `nagaraj` (snake charmer vibe, black kurta), `basappa` (big farmer, white dhoti, moustache), `kaveri` (woman,
blue saree), `agni` (fiery young man, red kurta). Villains: `bhaskar` (boss: business suit + yellow hard hat), `grunt_m`,
`grunt_f` (hi-vis vests, hard hats).
Trainer classes & townsfolk: `schoolboy`, `schoolgirl`, `college_m`, `college_f`, `techie_m`, `techie_f` (lanyard/backpack),
`auto_driver` (khaki shirt), `cricketer`, `gardener`, `fisher` (lungi), `jogger`, `vendor` (apron), `wrestler`
(bare-chested, red shorts), `dancer` (classical dance costume), `ajja` (grandpa: white kurta + dhoti, grey, stick),
`ajji` (grandma: saree, grey bun), `birdwatcher` (hat, binoculars), `delivery_rider` (orange jacket, helmet),
`traffic_cop` (khaki, white cap), `darshini_owner` (white shirt, apron, moustache), `shopkeeper`, `metro_staff`
(purple uniform), `officer` (civic official, white shirt), and generic `man1`–`man4`, `woman1`–`woman4`, `kid1`, `kid2`
with varied colours.

## CLI
`python3 tools/art/characters.py` writes `assets/images/characters/<name>.png` for every preset, and a preview contact
sheet `art-src/previews/characters_preview.png` (every sheet scaled ×4, labelled, on a light grass-green background).

## Rules
- Quality bar: clean, readable silhouettes like official GBA sprites; symmetric where appropriate; no stray pixels.
- Only create `tools/art/characters.py` and its outputs. Do not modify any other file. Do not install packages.
- When done, run it, open the preview yourself and fix anything that looks wrong before finishing.
