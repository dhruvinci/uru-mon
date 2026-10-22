# uru-mon

A GBA-style creature-collecting adventure across **Bengaluru**, playable in the browser on desktop and phones.

Catch Urumon in steel tiffin **Dabbas**, heal them with idli at the neighbourhood **Darshini**, battle six Arena
Leaders from Lalbagh's Glass House to the summit of Nandi Hills, stop the **Concrete Syndicate** from paving over the
city's lakes and parks, and take on the **Namma Council** at Vidhana Soudha.

- 150 original Urumon across 18 types (including FROST, MYTH, ROGUE and CHARM), 151 moves, 21 items, fishing and fossils
- 36 maps: Basavanagudi, Lalbagh, Cubbon Park, MG Road, Silk Board, Whitefield, Bellandur Lake, Sankey Tank,
  Malleshwaram, Palace Road, Hebbal, Nandi Hills, Vidhana Soudha, and Bannerghatta, Ramanagara and Kokkare Bellur
- 6 Arena Leaders, a 4-member Council and Champion Sudeep, a villain team, and six legendaries (five after the Council)
- HD-2D look: tilted camera, depth of field, time of day from your clock, monsoon rain, lamps at night (GRAPHICS option)
- Browse every Urumon (Uru-Pustaka) and every place (Bengaluru map) from the title screen before you play
- Touch controls on phones, keyboard on desktop; save anytime from the menu (stored in your browser)

## Controls

| | Keyboard | Touch |
|---|---|---|
| Move | Arrow keys / WASD | D-pad |
| A (talk, confirm) | Z or Space | A |
| B (back, hold to run) | X or Shift | B |
| Menu | Enter | START |
| Fullscreen | F | — |

## Run it locally

There is no build step. Serve the folder over HTTP and open it:

```
python3 -m http.server 8080
# then visit http://localhost:8080
```

Handy dev URL: `?scene=test&map=lalbagh` jumps straight into a map with a test team
(see `src/scenes/test-scene.js` for all options).

## Deploy

It's a static site: upload the repository root (everything except `art-src/` and `tools/`) to GitHub Pages,
Cloudflare Pages, Netlify or any static host.

## How it's made

| Part | Where | Notes |
|---|---|---|
| Engine | `src/` | Phaser 3.60 (vendored), plain ES modules. Battle rules live in `src/battle/engine/` and are unit-tested in Node. |
| Game data | `tools/content/*.py` → `assets/data/*.json` | `python3 tools/content/build_data.py` |
| Maps | `tools/maps/*.py` → `assets/maps/` | Maps are written in Python, compiled to PNG layers plus Tiled-format JSON: `python3 tools/maps/build_maps.py --preview` |
| World art | `tools/art/tiles.py`, `tools/art/characters.py`, `tools/art/icons.py` | 16 px pixel art generated from code |
| Creature, trainer and backdrop art | `tools/art/gen_images.py` + `tools/art/process_art.py` | AI-generated, then pixelized and palette-reduced |
| Music & SFX | `tools/audio/synth.py` | Original chiptune, synthesized in code |
| Tests | `tools/test/` | `node --test tools/test/engine.test.mjs`; browser smoke tests use Playwright (`cd tools && npm install`) |

See `docs/DESIGN.md` for the full game design.

## Credits

- Built on the MIT-licensed [monster-tamer](https://github.com/devshareacademy/monster-tamer) Phaser tutorial by
  Dev Share Academy (see `LICENSE`).
- [Phaser](https://phaser.io) game framework (MIT).
- [Pixelify Sans](https://github.com/eifetx/Pixelify-Sans) font (SIL Open Font License 1.1, `assets/fonts/pixelify/OFL.txt`).
- All creatures, characters, places, music and story are original to uru-mon. uru-mon is a fan-made homage to the
  monster-collecting genre and is not affiliated with any game company.
