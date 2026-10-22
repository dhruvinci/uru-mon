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
  Phaser 3.60 is vendored at `src/lib/vendor/phaser.min.js`.
- Dev shortcuts: `?scene=test&map=<id>[&x=&y=|&warp=<id>][&party=sp:lvl,...][&flags=A,B][&badges=GRASS,...]` and
  `?scene=test&battle=wild&species=10&level=5` / `&battle=trainer&trainer=<id>`. `?touch=1` forces the touch pad,
  `?debug` enables scene logging.
- Engine unit/fuzz tests: `node --test tools/test/engine.test.mjs`.
- Browser tests (Playwright, `cd tools && npm install` once) expect the dev server on port 8080:
  `node test/world-smoke.mjs <shots_dir> <map,map>`, `newgame.mjs`, `services.mjs`, `systems.mjs <dir> catch|evolve`,
  `progression.mjs <dir> leader|metro|blackout`, `story.mjs <dir> cubbon|rival2|rival3|bellandur|rival4|nandi|council`.
  `window.__uru` exposes `dataManager`, `gameData`, `createMonster` for tests.

## Generated files: edit the sources, not the outputs

| Output | Source | Rebuild |
|---|---|---|
| `assets/data/{species,moves,items,trainers}.json` | `tools/content/*_data.py` | `python3 tools/content/build_data.py` |
| `assets/maps/<id>/{bg.png,map.json}`, `assets/maps/index.json` | `tools/maps/maps_*.py` (+ `compiler.py`, `dsl.py`, `common.py`) | `python3 tools/maps/build_maps.py [--preview]` (also rebuilds the manifest) |
| `assets/manifest.json` | files present under `assets/` | `python3 tools/build_manifest.py` |
| `assets/images/{creatures,trainers,battle,ui}` | raw AI art in `art-src/raw/` (gitignored) | `python3 tools/art/process_art.py all` |
| `assets/images/characters/*.png` | `tools/art/characters.py` | `python3 tools/art/characters.py` |
| `assets/audio/**` | `tools/audio/synth.py` | `python3 tools/audio/synth.py` |

`build_maps.py` validates warps, NPC/item/spawn placement; treat its WARN lines as bugs.

## Architecture notes that aren't obvious from one file

- **Battles**: `src/battle/engine/` is pure logic (no Phaser). `Battle.resolveTurn()` mutates monsters and returns a list
  of events; `BattleScene` plays them back with async/await. Struggle is deliberately typeless so battles can't deadlock.
- **World flow**: battles and menu scenes run by pausing `WorldScene` and launching the other scene; the world resumes
  with data via `this.scene.resume(prev, data)` (`openSubScene` / `startBattle` return promises). Battle results arrive
  through `game.events` `'battle-finished'`.
- **Scripts**: map NPCs, triggers and interactables carry JSON command lists run by `src/world/script-runner.js`
  (command reference at the top of that file); conditions are evaluated by `WorldScene.checkCondition`.
- **Maps**: logical grid is 64 px (`TILE_SIZE`), art is 16 px shown ×4 with `pixelArt: true`. Building doors are
  *blocked* warp tiles triggered by bumping; `exits` on map edges generate paired warps (`N0`↔`S0`, ...).
  Shared interiors (Darshini, Kirana) exit to `@return`, set by the entering door's `setReturn`.
- **Characters**: `CHAR_*` sheets are 3 columns × 4 rows (down, up, left, right) of 16×24 frames; walk anims are built
  in `PreloadScene`. Trainer species `"RIVAL:n"` resolves to stage n of Rohan's starter line at runtime.
- **Council**: entering `council_1` resets the five Council trainers (`resetTrainers`), so losing restarts the run.
- **Input**: one global `inputManager` merges keyboard and the DOM touch pad; per-scene `Controls` just reads it.
  Keys typed into `<input>` elements are ignored by the game (used for name entry).

## Art generation (Codex)

`tools/art/gen_images.py <jobs.json> <out_dir>` and `tools/run_codex_task.sh docs/tasks/<spec>.md` drive the Codex
CLI using the user's ChatGPT login (`codex login status`). Codex must get `stdin` from `/dev/null` or it hangs.
Prompts for creatures and trainers come from `tools/content/species_data.py` and `portraits_data.py`; review results
for resemblance to existing franchise designs and regenerate when in doubt.
