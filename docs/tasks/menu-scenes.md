# Task: six menu scenes for uru-mon

uru-mon is a GBA-style creature RPG in plain ES modules + Phaser 3.60 (no build step, no npm). Read `docs/DESIGN.md`,
then study these files closely and **follow their patterns exactly** (imports, BaseScene usage, input handling, UI kit):

- `src/ui/ui-kit.js` — `panel`, `text`, `ListMenu`, `MessageBox`, `Meter`, `typeBadge`, `readMenuInput`, `TEXT`, `COLORS`
- `src/scenes/inventory-scene.js` and `src/scenes/monster-party-scene.js` — reference implementations of menu scenes
- `src/utils/data-manager.js` — game state (`dataManager.state`, `party`, `boxes`, `money`, `addItem`, `removeItem`,
  `itemCount`, `addMoney`, `state.pustaka.{seen,caught}`, `state.player.{name,badges,money}`, `getPlayTimeSeconds()`,
  `state.metroStations`)
- `src/game/game-data.js` (`gameData.species`, `gameData.items`, `getItem`, `getItemByName`) and
  `src/battle/engine/monster.js` (`getSpecies`, `displayName`, `getMaxHp`, `getStats`)

## Conventions (must follow)
- Canvas is 1024×576. Font family `Pixelify` via the UI kit's `text()` helper and `TEXT` styles.
- Each scene `extends BaseScene`, calls `super.init()`/`super.create()`/`super.update(time)`, reads input once per frame
  with `readMenuInput(this._controls)` which returns `'UP'|'DOWN'|'LEFT'|'RIGHT'|'OK'|'CANCEL'|null`.
- Scenes are launched by a paused caller with `{previousSceneName, ...}`. To exit:
  `this.scene.stop(); this.scene.resume(this.sceneData.previousSceneName, resultData);`
- Creature textures are `getSpecies(id).assetKey` (64×64 native; draw them with `setScale(2..4)`); if
  `!this.textures.exists(key)` use `'__MISSING'`. Use `playSoundFx(this, AUDIO_KEYS.SFX_SELECT)` etc. from
  `src/utils/audio-utils.js` / `src/assets/asset-keys.js` for feedback (they no-op when audio is missing).
- Visual style: friendly GBA look, coloured patterned backgrounds like the party/bag scenes, rounded panels, no
  external images needed. Everything readable on a phone (text ≥ 22px).
- JSDoc types like the existing code. No new dependencies, no build tools.

## Scenes to create (one file each, class names and keys as listed — `src/main.js` already imports them)

1. `src/scenes/shop-scene.js` — `export class ShopScene`, key `SCENE_KEYS.SHOP_SCENE`. Data: `{previousSceneName,
   items: string[] (item names sold here), greeting?: string}`. Kirana-store UI: first choose BUY / SELL / QUIT.
   BUY: list of items with prices (`item.price`), money box top-right, description box at bottom, then a quantity picker
   (UP/DOWN ±1, LEFT/RIGHT ±10, shows total), confirm, check money, `dataManager.addMoney(-total)`,
   `dataManager.addItem(id, qty)`, thank-you line. SELL: list the player's non-KEY items with price/2 each, quantity
   picker up to owned count. Indian rupee sign `₹`.
2. `src/scenes/storage-scene.js` — `StorageScene`, key `STORAGE_SCENE`. "Namma Cloud" box storage. Options:
   WITHDRAW / DEPOSIT / MOVE OUT (release) / QUIT. Shows a grid or list of `dataManager.boxes` (with mini sprite, name,
   level) and the party. Rules: party must keep at least one non-fainted Urumon; party max 6
   (`dataManager.isPartyFull()`); confirm before release ("Bye-bye, X!"). Supports SUMMARY via launching
   `SCENE_KEYS.MONSTER_DETAILS_SCENE` with `{previousSceneName: SCENE_KEYS.STORAGE_SCENE, monsterIndex, list: 'box'|'party'}`
   and waiting for resume (see how monster-party-scene does it).
3. `src/scenes/pustaka-scene.js` — `PustakaScene`, key `PUSTAKA_SCENE`. The Uru-Pustaka (creature encyclopedia):
   scrolling list of all species by number (`No.001 Name`), unseen ones show `-----`; seen-but-not-caught show the name
   and a silhouette (sprite tinted black); caught show full sprite, types (`typeBadge`), and the dex text
   (`species.dex`). Header shows SEEN n / CAUGHT n. A = toggle detail panel, B = back.
4. `src/scenes/trainer-card-scene.js` — `TrainerCardScene`, key `TRAINER_CARD_SCENE`. Shows player name, money,
   Pustaka caught count, play time (h:mm), and the six badge slots (GRASS, FIGHT, ELECTRIC, MIND, SPIRIT, SKY — draw
   each badge as a coloured gem/emblem with Graphics; grey when not earned; earned ones are in `state.player.badges`).
   Draw the player's overworld sprite `CHAR_player_${state.player.gender}` frame 0 at scale 6 on the card. Any key closes.
5. `src/scenes/metro-scene.js` — `MetroScene`, key `METRO_SCENE`. Namma Metro fast travel. Data
   `{previousSceneName, current?: string}`. Stations list (id → area/warp):
   `basavanagudi→{area:'basavanagudi',warpId:'metro'}`, `lalbagh`, `mg_road`, `whitefield`, `malleshwaram`,
   `palace_road` (same shape: area = id, warpId 'metro'). Only show stations in `dataManager.state.metroStations`;
   if the player lacks the item named "Metro Card" (`dataManager.itemCount(getItemByName('Metro Card').id)`), show
   "Please tap a Metro Card to ride." and exit. Draw a stylised purple/green line map with station dots. Selecting the
   current station does nothing. Resume the caller with `{station: {area, warpId}}` or `{}`.
6. `src/scenes/credits-scene.js` — `CreditsScene`, key `CREDITS_SCENE` (started with `this.scene.start`, not launched).
   Scrolling credits on a night-sky gradient with twinkling stars: "uru-mon", "A Bengaluru adventure", the
   player's name as Champion, the party's sprites marching across the bottom, thanks to Namma Bengaluru, then
   "THE END". When finished (or START/A held), save via `dataManager.saveData()` and `this.scene.start(SCENE_KEYS.TITLE_SCENE)`.

## Rules
- Only create those six files. Do not modify any other file. Do not run git commands that change state.
- You can't run a browser; instead run `node --check <file>` on each file you write, and re-read the UI kit to make sure
  every function you call exists with that signature.
