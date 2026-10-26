# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**uru-mon**: a GBA-style creature-collecting RPG set in Bengaluru, deployed as a static website. It began as a fork of
`devshareacademy/monster-tamer` (MIT; the `upstream` remote), but the engine, data model, UI and all content have
been rewritten. Game design lives in `docs/DESIGN.md`.

Everything must stay original IP: no Nintendo names or terms (Pokémon, Poké-anything, species or move names), no
look-alike designs, no "Pokémon style" or artist-name prompts for generated art. Mechanics may mirror the genre.

## Running and testing

- No build step. Serve the repo root (`python3 -m http.server 8080`) and open `http://127.0.0.1:8080`.
  Phaser 3.60 is vendored at `src/lib/vendor/phaser.min.js`. Since nothing bundles `src/`, an npm import
  (`import x from 'some-package'`) breaks the whole game in the browser; vendor a file or use a `<script>` tag instead.
  Vercel Web Analytics is loaded that way, by a snippet in `index.html`. Vercel's bot once merged the npm version and
  took the live site down. The game is one page, so `trackPage()` (`src/utils/analytics.js`) reports sections as
  virtual pages (`/menu`, each title menu choice, `/world`, `/battle`, `/quick-battle/fight`), once per visit: the
  Hobby plan has 50,000 events a month and custom events need Pro.
- Dev shortcuts: `?scene=test&map=<id>[&x=&y=|&warp=<id>][&party=sp:lvl,...][&flags=A,B][&badges=GRASS,...]` and
  `?scene=test&battle=wild&species=10&level=5` / `&battle=trainer&trainer=<id>`. `?touch=1` forces the touch pad,
  `?debug` enables scene logging.
- Engine unit/fuzz tests: `node --test tools/test/engine.test.mjs`.
- Browser tests (Playwright, `cd tools && npm install` once) expect the dev server on port 8080:
  `node test/world-smoke.mjs <shots_dir> <map,map>`, `newgame.mjs`, `services.mjs`, `systems.mjs <dir> catch|evolve`,
  `progression.mjs <dir> leader|metro|blackout`, `story.mjs <dir> cubbon|rival2|rival2lose|rival3|bellandur|rival4|nandi|council`.
  `frontdoor.mjs <dir> [pustaka|map|starter|admin|fishing]` covers the title-screen extras, the starter showcase,
  the admin profile and fishing; `expansion.mjs <dir> [gaala|fossil|legends|gates]` the expansion's story pieces.
  `tools/test/run-all.sh [dir]` runs every browser test in sequence and prints PASS/FAIL. Tests walk with the BFS
  `walkTo` / `enterWarp` helpers in harness.mjs, which survive map layout changes; prefer them to timed `walk()`.
  `window.__uru` exposes `dataManager`, `gameData`, `createMonster` for tests.

## Review site and the user's notes

**Local only**: `tools/review/` is gitignored (the public repo must not carry the user's notes or the franchise
comparison table), so it exists only on the user's machine. `python3 tools/review/server.py` serves
http://127.0.0.1:8090: every Pokémon -> uru-mon change as before/after cards with a note box on each. **The user's notes in `tools/review/notes.json` are change requests**; every save is also
appended to `notes-log.jsonl`. Reply to each note in `tools/review/responses.json`
({id: {status, reply}}; the page shows it under the note) when you act on it. The "after" side is read live from the game data; the Pokémon counterparts ("before")
and the Pokémon-term flags live in `tools/review/analogs.py` (and `plan_analogs.py` for the expansion families), so add
entries there when adding species, moves, items or maps. Never move these back into tracked files. `node test/review-smoke.mjs <dir>` checks the site (it adds and removes one note, leaving two log lines).

## Generated files: edit the sources, not the outputs

| Output | Source | Rebuild |
|---|---|---|
| `assets/data/{species,moves,items,trainers}.json` | `tools/content/*_data.py` | `python3 tools/content/build_data.py` |
| `assets/maps/<id>/{bg.png,map.json}`, `assets/maps/index.json` | `tools/maps/maps_*.py` (+ `compiler.py`, `dsl.py`, `common.py`) | `python3 tools/maps/build_maps.py [--preview]` (also rebuilds the manifest) |
| `assets/manifest.json` | files present under `assets/` | `python3 tools/build_manifest.py` |
| `assets/images/{creatures,trainers,battle,ui}` | raw AI art in `art-src/raw/` (gitignored) | `python3 tools/art/process_art.py all` |
| `assets/images/{creatures,trainers}_hd/*.webp` (4x, smooth; loaded on demand via `src/ui/hd-art.js`) | same raw art | `python3 tools/art/process_art.py hd` |
| `assets/images/characters/*.png` | `tools/art/characters.py` | `python3 tools/art/characters.py` |
| `assets/audio/**` | `tools/audio/synth.py` | `python3 tools/audio/synth.py` |
| `assets/images/ui/title_bg.png` | `tools/art/title_art.py` | `python3 tools/art/title_art.py` |
| `favicon.ico`, `assets/icons/*` (incl. `share.png`, the 1200x630 link preview named in index.html's og:image), `docs/brand/profile*.png` (the logo: the title scene recomposed square) | `tools/art/brand.py` (reuses `title_art.py`'s pieces; 16 px favicon hand-pixelled in the script) | `python3 tools/art/brand.py` |

`build_maps.py` validates warps, NPC/item/spawn placement; `python3 tools/maps/reachability.py` then flood-fills every map
to prove all warps, NPCs, items and signs are reachable. Treat any WARN or problem line as a bug.

## Architecture notes that aren't obvious from one file

- **Battles**: `src/battle/engine/` is pure logic (no Phaser). `Battle.resolveTurn()` mutates monsters and returns a list
  of events; `BattleScene` plays them back with async/await. Struggle is deliberately typeless so battles can't deadlock.
- **World flow**: battles and menu scenes run by pausing `WorldScene` and launching the other scene; the world resumes
  with data via `this.scene.resume(prev, data)` (`openSubScene` / `startBattle` return promises). Battle results arrive
  through `game.events` `'battle-finished'`.
- **Scripts**: map NPCs, triggers and interactables carry JSON command lists run by `src/world/script-runner.js`
  (command reference at the top of that file); conditions are evaluated by `WorldScene.checkCondition`.
  Triggers are one-time by default and are marked viewed *before* they run, so a trigger whose battle can be lost
  must use `once=False` plus an `unless` flag set at the end of its script (see the rival triggers).
- **Maps**: logical grid is 64 px (`TILE_SIZE`), art is 16 px shown ×4 with `pixelArt: true`. Building doors are
  *blocked* warp tiles triggered by bumping; `exits` on map edges generate paired warps (`N0`↔`S0`, ...).
  Shared interiors (Darshini, Kirana) exit to `@return`, set by the entering door's `setReturn`.
- **Characters**: `CHAR_*` sheets are 3 columns × 4 rows (down, up, left, right) of 16×32 frames; walk anims are built
  in `PreloadScene`. Trainer species `"RIVAL:n"` resolves to stage n of Sudeep's starter line at runtime.
- **Admin profile**: on localhost (or with `?admin`) the title menu shows ADMIN MODE, a separate save slot
  (`URU_MON_SAVE_V1_ADMIN`) with all 150 Urumon, every badge and item, and WARP in the START menu (src/game/admin-profile.js).
- **Visual effects** (`src/fx/`): `WorldFx` adds time-of-day grading (from the player's clock), weather, ambient particles
  per map, night lights and character shadows; `Hd2dPipeline` is a one-pass post shader for the tilted HD-2D camera,
  depth of field, haze and vignette. GRAPHICS option: HD-2D / ENHANCED / CLASSIC. Test overrides:
  `?time=dawn|day|dusk|night&weather=rain|clear&gfx=CLASSIC|ENHANCED|HD-2D`; `node test/fx-shots.mjs <dir> map:time:weather:gfx`.
- **Fishing**: maps with a "fish" encounter table record their water tiles (`uru.water`); pressing A while facing water with
  the Gaala rod starts a fishing encounter.
- **Council**: entering `council_1` resets the five Council trainers (`resetTrainers`), so losing restarts the run.
- **Input**: one global `inputManager` merges keyboard and the DOM touch pad; per-scene `Controls` just reads it.
  Keys: Enter/Z/Space = A, X/Shift/Backspace = B, and Esc is its own `ESC` button that `Controls` counts as START when
  a scene asks for START first (only the overworld does, so Esc opens the menu there) and as B everywhere else. Tests
  press START as Escape (harness.mjs). Button prompts: `ControlHints` in ui-kit shows "[Enter] Select  [Esc] Back" on
  keyboards and the pad's red A/B on touch screens, and clicking a prompt presses its button. `MessageBox.setHints`
  puts a row in the box's bottom-right corner (it shows "Next" while waiting, and hides itself if a long message
  reaches it). Screens without a box put the row in a header or in a dark pill in the bottom-right corner. Every
  screen that takes input should have one. The overworld's own prompts (Talk / Menu / Run) are keyboard-only and go
  away once the player has used both (`uru-learned-keys` in localStorage).
  Touch is first-class: `inputManager.tap(button)` injects a zero-length press, and taps on the game reuse it (ListMenu
  rows select, MessageBox / battle / dialog taps act as A, party cards, battle grids, options rows). The world scene
  walks to tapped tiles with a BFS path follower (`screenToTile` looks through the HD-2D tilt) and interacts with tapped
  NPCs, signs, items, water and doors. `src/input/touch-controls.js` sizes the game and lays out the pad, reading the
  safe-area insets through `--safe-*` CSS variables (tests override them): landscape = 16:9 at full height with
  A/B/MENU in columns beside it, clear of the notch, D-pad optional; portrait = the pad below and the game above it,
  grown towards a square (`game.scale.setGameSize(1024, H)`, H up to 1024, changed live when the phone turns).
  Keys typed into `<input>` elements are ignored by the game (used for name entry). A tap shorter than a frame still
  counts as one step.
- **Tall canvas** (`src/ui/screen.js`): every scene is designed for 1024x576. Menu screens keep that layout at the top
  of a taller canvas (draw backgrounds to `FULL_HEIGHT`), and the page repeats their MessageBox text in large type
  under it (`uru:message` / `uru:speaker` window events; a box's message is withdrawn when its scene pauses or closes).
  The overworld (camera zoomed to keep tiles about 38 CSS px), its DialogScene, the title, intro, battles and credits
  use the whole canvas when `isTall()`, draw their UI `uiScale()` times bigger on phones (containers scaled up, with
  `setTextResolution` so text stays sharp), dock message boxes with `MessageBox.dock`, and don't announce to the page.
  They re-lay themselves out through `onResize`, battles included (`BattleScene.#relayout`: open menus redraw through
  `this.redraw`, and anything caught mid-animation is put in place once the battle next waits for the player). A battle
  hides the scenes under it while it runs (they would show through the vignette's translucent edges).
  main.js patches Phaser 3.60 so camera effects' render targets resize with the game. On Android the first tap
  requests fullscreen; iPhones can't, so the ⛶ button (and a one-time tip) explains Add to Home Screen.
  HD-2D outdoors uses camera zoom 0.75, or 1 on phones (`PHONE` in `world-fx.js`), times the tall zoom.
  `node test/mobile.mjs <dir> portrait|landscape|iphone|turn` plays with taps only (`iphone`: notch insets and
  Safari's bars; `turn`: rotates mid-conversation, and mid-Quick-Battle into Safari's sideways size). The user plays
  on an iPhone in Safari, both ways up: check every screen change in both orientations and after turning.
- **Audio**: only SFX and the title theme load before the title screen; `PreloadScene` stays alive to stream the rest
  and starts a requested track when it arrives. Missing audio keys are silently ignored.
  The manifest lists MP3 before Ogg (Safari's Ogg support varies). For iPhones, `setGlobalSoundSettings` sets
  `navigator.audioSession.type` to `playback` (sound plays with the ring/silent switch on; `ambient` when Sound is OFF),
  and `keepAudioAwake` resumes the AudioContext on later taps after iOS suspends it (calls, app switches).
- **Browser tests drive real key presses**, so their walking is timing-based: run them one at a time (parallel
  headless browsers on a busy CPU cause missed steps).

## Art generation (Codex)

`tools/art/gen_images.py <jobs.json> <out_dir>` and `tools/run_codex_task.sh docs/tasks/<spec>.md` drive the Codex
CLI using the user's ChatGPT login (`codex login status`). Codex must get `stdin` from `/dev/null` or it hangs.
Prompts for creatures and trainers come from `tools/content/species_data.py` and `portraits_data.py`; review results
for resemblance to existing franchise designs and regenerate when in doubt.
