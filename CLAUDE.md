# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**uru-mon** is a browser-based creature-collector RPG set in a region modeled on Bangalore's neighborhoods. It's a fork of `devshareacademy/monster-tamer` (MIT), and the `upstream` remote points at that repo. The goal is a public website, so all content must be original:
- no Nintendo names or terms (Pokémon, Poké-anything, species or move names)
- no look-alike designs
- no "Pokémon style" or artist-name prompts when generating art

Mechanics (types, stats, catching, gyms) may closely mirror the genre.

## Running

There's no build step or package manager. Phaser 3.60 is loaded from a CDN in `index.html`, and `src/lib/phaser.js` just re-exports `window.Phaser`. Serve the repo root over HTTP; `file://` won't work:

```
python3 -m http.server 8080 --bind 127.0.0.1
```

`deploy/bundle.sh` is upstream's packaging script. It downloads upstream's *old* asset zip, so don't use it for this project.

## Assets: what's ours vs. borrowed

- `assets/images/` and `assets/audio/` are gitignored. They come from upstream's release zip (`all-game-assets-v2.zip`) and are third-party art under mixed licenses (see the README credits). Treat them as placeholders: they must be replaced, or each license checked, before any public deploy, and they must never be committed. Their sizes and keys are the contract new art has to meet.
- The zip is missing `monster-tamer/monsters/ignivolt.png`. Monster species 3 appears in wild-encounter areas 1 and 2, so those battles show a missing texture until it's replaced.

## How content is wired

- All content is JSON in `assets/data/`, loaded in `src/scenes/preload-scene.js`. Every image or spritesheet needs a key in `src/assets/asset-keys.js` and a load call there.
- In `monsters.json`, `id` identifies one monster instance (a specific level and stats), while `monsterId` is the species. `encounters.json` maps an encounter-area id to `[[monsterId, weight], ...]`.
- World maps are **pre-rendered PNG layers** (`*_level_background.png` and `*_level_foreground.png`). The Tiled JSON (`main_1.json`, `building_*.json`, `forest_1.json`) only supplies collision, encounter zones and object layers such as NPCs, signs and events. Changing how a map looks means re-exporting the images, not editing tiles in JSON.
- `TILE_SIZE` is 64 and the canvas is 1024×576, both set in `src/config.js` and `src/main.js`. Social-link assets only load when `SHOW_SOCIAL_LINKS` is true.
