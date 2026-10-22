import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { Player } from '../world/characters/player.js';
import { NPC, NPC_MOVEMENT_PATTERN } from '../world/characters/npc.js';
import { Item } from '../world/item.js';
import { DIRECTION } from '../common/direction.js';
import { TILE_SIZE } from '../config.js';
import { dataManager } from '../utils/data-manager.js';
import { playBackgroundMusic, playSoundFx, currentMusic } from '../utils/audio-utils.js';
import { AUDIO_KEYS, UI_KEYS, WORLD_KEYS } from '../assets/asset-keys.js';
import { getTargetPositionFromGameObjectPositionAndDirection } from '../utils/grid-utils.js';
import { createMonster, displayName, fullyHeal } from '../battle/engine/monster.js';
import { gameData, getItem, getItemByName } from '../game/game-data.js';
import { ScriptRunner } from '../world/script-runner.js';
import { buildTrainerTeam } from '../world/trainers.js';
import { warpTargets } from '../game/admin-profile.js';

/**
 * Picks a weighted slot from an encounter table.
 * @param {{slots: {species: number, min: number, max: number, weight: number}[]}} table
 */
function rollEncounter(table) {
  const total = table.slots.reduce((sum, e) => sum + e.weight, 0);
  let r = Math.random() * total;
  const slot = table.slots.find((e) => (r -= e.weight) < 0) || table.slots[0];
  return { species: slot.species, level: slot.min + Math.floor(Math.random() * (slot.max - slot.min + 1)) };
}

/**
 * @typedef WorldSceneData
 * @type {object}
 * @property {string} [area] map id to load (defaults to the saved location)
 * @property {string} [warpId] arrive at this warp in the new map
 * @property {{x: number, y: number}} [position] tile-pixel position to place the player
 * @property {import('../common/direction.js').Direction} [direction]
 * @property {boolean} [isPlayerKnockedOut]
 * @property {boolean} [fadeIn=true]
 */

const STEP = { UP: [0, -1], DOWN: [0, 1], LEFT: [-1, 0], RIGHT: [1, 0] };
const OPPOSITE = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT' };

export class WorldScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.WORLD_SCENE });
  }

  /** @param {WorldSceneData} data */
  init(data) {
    super.init();
    this.sceneData = data || {};
    this.area = this.sceneData.area || dataManager.state.player.location.area;
    this.scriptDepth = 0;
    // bumped on every (re)start so work started before a restart can't unbalance scriptDepth
    this.generation = (this.generation || 0) + 1;
    this.transitioning = false;
    this.menuOpen = false;
    /** @type {NPC[]} */
    this.npcs = [];
    /** @type {Item[]} */
    this.items = [];
    this.stepsSinceEncounter = 0;
  }

  // ------------------------------------------------------------------------------------------
  // setup
  // ------------------------------------------------------------------------------------------

  create() {
    super.create();
    const key = `MAP_${this.area}`;
    if (!this.cache.tilemap.exists(key)) {
      console.error(`[WorldScene] unknown map ${this.area}`);
      this.area = 'basavanagudi';
    }
    this.mapKey = `MAP_${this.area}`;
    this.map = this.make.tilemap({ key: this.mapKey });
    /** @type {any} */
    this.uru = this.cache.tilemap.get(this.mapKey).data.uru || {};
    this.water = new Set(this.uru.water || []);
    this.mapW = this.map.width * TILE_SIZE;
    this.mapH = this.map.height * TILE_SIZE;

    this.add.image(0, 0, `${this.mapKey}_BG`).setOrigin(0).setScale(4).setDepth(-10);
    if (this.textures.exists(`${this.mapKey}_FG`)) {
      this.add.image(0, 0, `${this.mapKey}_FG`).setOrigin(0).setScale(4).setDepth(1e6);
    }

    const collisionTiles = this.map.addTilesetImage('collision', WORLD_KEYS.COLLISION);
    this.collisionLayer = this.map.createLayer('Collision', collisionTiles, 0, 0).setVisible(false);
    this.#createEncounterLayers();

    this.ui = /** @type {import('./dialog-scene.js').DialogScene} */ (this.scene.get(SCENE_KEYS.DIALOG_SCENE));
    if (!this.scene.isActive(SCENE_KEYS.DIALOG_SCENE)) {
      this.scene.launch(SCENE_KEYS.DIALOG_SCENE);
    }
    this.scene.launch(SCENE_KEYS.CUTSCENE_SCENE);

    this.#placePlayer();
    this.#createItems();
    this.#createNpcs();
    this.grassOverlay = this.textures.exists(WORLD_KEYS.TALL_GRASS)
      ? this.add.image(0, 0, WORLD_KEYS.TALL_GRASS).setOrigin(0).setScale(4).setVisible(false)
      : null;
    this.#setupCamera();

    dataManager.state.player.location = { area: this.area };
    dataManager.state.gameStarted = true;
    this.scripts = new ScriptRunner(this);

    const music = this.uru.music ? AUDIO_KEYS[this.uru.music] || this.uru.music : null;
    if (music) {
      playBackgroundMusic(this, music);
    }

    if (this.uru.metroStation && !dataManager.state.metroStations.includes(this.uru.metroStation)) {
      dataManager.state.metroStations.push(this.uru.metroStation);
    }

    this.cameras.main.fadeIn(this.sceneData.fadeIn === false ? 0 : 350, 0, 0, 0);
    this.time.delayedCall(10, () => this.#afterArrive());
  }

  async #afterArrive() {
    if (this.sceneData.isPlayerKnockedOut) {
      dataManager.party.forEach((m) => fullyHeal(m));
      await this.ui.say(this.uru.respawnText || ['Your Urumon were fed fresh idli and are full of energy again.', 'Take care out there!']);
    }
    if (this.uru.onEnter) {
      await this.runScript(this.uru.onEnter);
    }
    this.#checkTriggers();
  }

  #createEncounterLayers() {
    /** @type {Phaser.Tilemaps.TilemapLayer[]} */
    this.encounterLayers = [];
    const names = this.map.getTileLayerNames().filter((n) => n.startsWith('Encounter'));
    if (names.length === 0) {
      return;
    }
    const tiles = this.map.addTilesetImage('encounter', WORLD_KEYS.ENCOUNTER);
    names.forEach((n) => {
      const layer = this.map.createLayer(n, tiles, 0, 0).setVisible(false);
      this.encounterLayers.push(layer);
    });
  }

  #placePlayer() {
    const st = dataManager.state.player;
    let pos = this.sceneData.position || st.position;
    let dir = this.sceneData.direction || st.direction || DIRECTION.DOWN;
    if (this.sceneData.warpId) {
      const warp = (this.uru.warps || []).find((w) => w.id === this.sceneData.warpId);
      if (warp) {
        const exit = warp.exit || 'DOWN';
        pos = { x: (warp.x + STEP[exit][0]) * TILE_SIZE, y: (warp.y + STEP[exit][1]) * TILE_SIZE };
        dir = /** @type {any} */ (exit);
      }
    } else if (this.sceneData.adminWarp) {
      // land on the map's spawn point, or just inside its first warp
      const warp = (this.uru.warps || []).find((w) => w.mode !== 'arrive') || (this.uru.warps || [])[0];
      if (this.uru.spawn) {
        pos = { x: this.uru.spawn.x * TILE_SIZE, y: this.uru.spawn.y * TILE_SIZE };
      } else if (warp) {
        const exit = warp.exit || 'DOWN';
        pos = { x: (warp.x + STEP[exit][0]) * TILE_SIZE, y: (warp.y + STEP[exit][1]) * TILE_SIZE };
        dir = /** @type {any} */ (exit);
      }
    } else if (!this.sceneData.position && !dataManager.state.gameStarted && this.uru.spawn) {
      pos = { x: this.uru.spawn.x * TILE_SIZE, y: this.uru.spawn.y * TILE_SIZE };
      dir = this.uru.spawn.dir || DIRECTION.DOWN;
    }
    st.position = { ...pos };
    st.direction = dir;
    const gender = dataManager.state.player.gender;
    this.player = new Player({
      scene: this,
      assetKey: `CHAR_player_${gender}`,
      position: pos,
      direction: dir,
      collisionLayer: this.collisionLayer,
      spriteGridMovementStartedCallback: (p) => this.#onStepStart(p),
      spriteGridMovementFinishedCallback: () => this.#onStepEnd(),
      spriteChangedDirectionCallback: () => {
        dataManager.state.player.direction = this.player.direction;
      },
      bumpCallback: (target) => this.#onBump(target),
    });
  }

  #setupCamera() {
    const cam = this.cameras.main;
    const vw = this.scale.width;
    const vh = this.scale.height;
    const bx = this.mapW < vw ? (this.mapW - vw) / 2 : 0;
    const by = this.mapH < vh ? (this.mapH - vh) / 2 : 0;
    cam.setBounds(bx, by, Math.max(this.mapW, vw), Math.max(this.mapH, vh));
    cam.startFollow(this.player.sprite, true, 1, 1, -32, -32);
    cam.setRoundPixels(true);
  }

  // ------------------------------------------------------------------------------------------
  // map objects
  // ------------------------------------------------------------------------------------------

  /** @param {any} cond @returns {boolean} */
  checkCondition(cond) {
    if (cond === undefined || cond === null) {
      return true;
    }
    if (typeof cond === 'string') {
      return dataManager.hasFlag(cond);
    }
    if (Array.isArray(cond)) {
      return cond.every((c) => this.checkCondition(c));
    }
    if (cond.not !== undefined) {
      return !this.checkCondition(cond.not);
    }
    if (cond.any) {
      return cond.any.some((c) => this.checkCondition(c));
    }
    if (cond.flag) {
      return dataManager.hasFlag(cond.flag);
    }
    if (cond.badges !== undefined) {
      return dataManager.state.player.badges.length >= cond.badges;
    }
    if (cond.badge) {
      return dataManager.state.player.badges.includes(cond.badge);
    }
    if (cond.defeated) {
      return dataManager.isNpcDefeated(cond.defeated);
    }
    if (cond.hasItem) {
      const item = typeof cond.hasItem === 'number' ? getItem(cond.hasItem) : getItemByName(cond.hasItem);
      return Boolean(item) && dataManager.itemCount(item.id) > 0;
    }
    if (cond.partySize !== undefined) {
      return dataManager.party.length >= cond.partySize;
    }
    if (cond.var) {
      return dataManager.state.vars[cond.var] === cond.equals;
    }
    if (cond.gender) {
      return dataManager.state.player.gender === cond.gender;
    }
    if (cond.won !== undefined) {
      return (this.lastBattleResult?.outcome === 'win') === cond.won;
    }
    if (cond.caught) {
      return dataManager.state.pustaka.caught.includes(cond.caught);
    }
    if (cond.money !== undefined) {
      return dataManager.money >= cond.money;
    }
    return true;
  }

  /** @param {any} def */
  isNpcVisible(def) {
    if (def.showIf !== undefined && !this.checkCondition(def.showIf)) {
      return false;
    }
    if (def.hideIf !== undefined && this.checkCondition(def.hideIf)) {
      return false;
    }
    return true;
  }

  #createNpcs() {
    (this.uru.npcs || []).forEach((def) => {
      if (this.isNpcVisible(def)) {
        this.spawnNpc(def);
      }
    });
    this.#refreshCollisionLists();
  }

  /**
   * @param {any} def map NPC definition
   * @returns {NPC}
   */
  spawnNpc(def) {
    const position = { x: def.x * TILE_SIZE, y: def.y * TILE_SIZE };
    const sprite = `CHAR_${def.sprite || 'man1'}`;
    const npc = new NPC({
      scene: this,
      assetKey: this.textures.exists(sprite) ? sprite : 'CHAR_man1',
      position,
      direction: def.facing || DIRECTION.DOWN,
      collisionLayer: this.collisionLayer,
      movementPattern: def.movement || (def.trainer ? NPC_MOVEMENT_PATTERN.IDLE : NPC_MOVEMENT_PATTERN.IDLE),
      npcPath: def.path ? Object.fromEntries(def.path.map((p, i) => [i, { x: p[0] * TILE_SIZE, y: p[1] * TILE_SIZE }])) : undefined,
      id: def.id,
      data: def,
    });
    this.npcs.push(npc);
    this.#refreshCollisionLists();
    return npc;
  }

  /** @param {string} id */
  removeNpc(id) {
    const idx = this.npcs.findIndex((n) => n.id === id);
    if (idx >= 0) {
      this.npcs[idx].sprite.destroy();
      this.npcs.splice(idx, 1);
    }
    this.#refreshCollisionLists();
  }

  /** @param {string} id */
  getNpc(id) {
    return this.npcs.find((n) => n.id === id);
  }

  #refreshCollisionLists() {
    if (!this.player) {
      return;
    }
    this.player.setCharactersToCheckForCollisionsWith(this.npcs);
    this.player.setObjectsToCheckForCollisionsWith(this.items);
    this.npcs.forEach((n) => {
      n.setCharactersToCheckForCollisionsWith([this.player, ...this.npcs.filter((o) => o !== n)]);
      n.setObjectsToCheckForCollisionsWith(this.items);
    });
  }

  #createItems() {
    const picked = new Set(dataManager.state.itemsPickedUp);
    (this.uru.items || []).forEach((def) => {
      const id = `${this.area}:${def.id}`;
      if (picked.has(id)) {
        return;
      }
      const item = typeof def.item === 'number' ? getItem(def.item) : getItemByName(def.item);
      if (!item) {
        return;
      }
      this.items.push(new Item({ scene: this, position: { x: def.x * TILE_SIZE, y: def.y * TILE_SIZE }, itemId: item.id, id, quantity: def.qty }));
    });
  }

  // ------------------------------------------------------------------------------------------
  // update loop
  // ------------------------------------------------------------------------------------------

  get inputLocked() {
    return this.scriptDepth > 0 || this.transitioning || this.menuOpen || this.ui.busy || this._controls.isInputLocked;
  }

  update(time) {
    super.update(time);
    if (!this._controls || !this.player) {
      return;
    }
    this._controls.update();
    if (!this.inputLocked) {
      if (this._controls.wasEnterKeyPressed() && !this.player.isMoving) {
        this.#openStartMenu();
      } else if (this._controls.wasConfirmPressed() && !this.player.isMoving) {
        this.#interact();
      } else {
        const dir = this._controls.getDirectionKeyPressedDown();
        if (dir !== DIRECTION.NONE) {
          this.player.moveCharacter(dir, this._controls.isShiftKeyDown());
        }
      }
    }
    this.player.update(time);
    this.npcs.forEach((n) => n.update(time));
  }

  // ------------------------------------------------------------------------------------------
  // movement events
  // ------------------------------------------------------------------------------------------

  /** @param {{x: number, y: number}} target */
  #onStepStart(target) {
    if (this.grassOverlay) {
      this.grassOverlay.setVisible(false);
    }
    this.pendingGrass = this.#encounterLayerAt(target.x, target.y);
    if (this.pendingGrass && this.pendingGrass.tileType === 'GRASS') {
      playSoundFx(this, AUDIO_KEYS.SFX_GRASS, 0.4);
    }
  }

  async #onStepEnd() {
    const p = this.player.sprite;
    dataManager.state.player.position = { x: p.x, y: p.y };
    if (this.grassOverlay && this.pendingGrass && this.pendingGrass.tileType === 'GRASS') {
      this.grassOverlay.setPosition(p.x, p.y).setDepth(p.y + 2).setVisible(true);
    }
    if (this.scriptDepth > 0 || this.transitioning) {
      return;
    }
    // step-on warps (stairs, cave mouths without doors)
    const tx = Math.round(p.x / TILE_SIZE);
    const ty = Math.round(p.y / TILE_SIZE);
    const stepWarp = (this.uru.warps || []).find((w) => w.mode === 'step' && w.x === tx && w.y === ty);
    if (stepWarp) {
      this.#useWarp(stepWarp);
      return;
    }
    if (dataManager.state.repelSteps > 0) {
      dataManager.state.repelSteps -= 1;
      if (dataManager.state.repelSteps === 0) {
        await this.ui.say('The Mosquito Coil burned out.');
      }
    }
    if (this.#checkTriggers()) {
      return;
    }
    if (await this.#checkTrainerSight()) {
      return;
    }
    this.#maybeWildEncounter();
  }

  /**
   * @param {number} x
   * @param {number} y
   * @returns {{area: string, tileType: string} | null}
   */
  #encounterLayerAt(x, y) {
    for (const layer of this.encounterLayers) {
      const tile = layer.getTileAtWorldXY(x + 1, y + 1, true);
      if (tile && tile.index !== -1) {
        const props = layer.layer.properties || [];
        const get = (k) => props.find((pp) => pp.name === k)?.value;
        return { area: String(get('area')), tileType: get('tileType') || 'GRASS' };
      }
    }
    return null;
  }

  #maybeWildEncounter() {
    const p = this.player.sprite;
    const zone = this.#encounterLayerAt(p.x, p.y);
    if (!zone || dataManager.party.every((m) => m.hp <= 0)) {
      return;
    }
    const table = this.uru.encounters?.[zone.area];
    if (!table || table.slots.length === 0) {
      return;
    }
    this.stepsSinceEncounter += 1;
    const rate = table.rate ?? 0.12;
    if (this.stepsSinceEncounter < 3 || Math.random() >= rate) {
      return;
    }
    const { species, level } = rollEncounter(table);
    const lead = dataManager.party.find((m) => m.hp > 0);
    if (dataManager.state.repelSteps > 0 && lead && level < lead.level) {
      return;
    }
    this.stepsSinceEncounter = 0;
    const wild = createMonster(species, level);
    this.startBattle({ wild, environment: this.uru.environment || 'grass' });
  }

  /** @returns {boolean} whether a trigger started */
  #checkTriggers() {
    const p = this.player.sprite;
    const tx = Math.round(p.x / TILE_SIZE);
    const ty = Math.round(p.y / TILE_SIZE);
    for (const t of this.uru.triggers || []) {
      const inside = tx >= t.x && ty >= t.y && tx < t.x + (t.w || 1) && ty < t.y + (t.h || 1);
      if (!inside) {
        continue;
      }
      const viewedKey = `${this.area}:${t.id}`;
      if (t.once !== false && dataManager.state.viewedEvents.includes(viewedKey)) {
        continue;
      }
      if (!this.checkCondition(t.requires) || (t.unless !== undefined && this.checkCondition(t.unless))) {
        continue;
      }
      if (t.once !== false) {
        dataManager.viewedEvent(viewedKey);
      }
      this.runScript(t.script);
      return true;
    }
    return false;
  }

  /** @returns {Promise<boolean>} */
  async #checkTrainerSight() {
    const p = this.player.tilePosition;
    for (const npc of this.npcs) {
      const def = npc.data;
      if (!def.trainer || dataManager.isNpcDefeated(def.id) || def.sight === 0) {
        continue;
      }
      const range = def.sight ?? 4;
      const [dx, dy] = STEP[npc.direction] || [0, 0];
      const n = npc.tilePosition;
      for (let i = 1; i <= range; i += 1) {
        const x = n.x + dx * TILE_SIZE * i;
        const y = n.y + dy * TILE_SIZE * i;
        if (x === p.x && y === p.y) {
          await this.#trainerSpotsPlayer(npc, i - 1);
          return true;
        }
        if (this.#blocked(x, y)) {
          break;
        }
      }
    }
    return false;
  }

  /** @param {number} x @param {number} y */
  #blocked(x, y) {
    const tile = this.collisionLayer.getTileAtWorldXY(x + 1, y + 1, true);
    if (tile && tile.index !== -1) {
      return true;
    }
    return this.npcs.some((n) => n.tilePosition.x === x && n.tilePosition.y === y);
  }

  /**
   * @param {NPC} npc
   * @param {number} distance tiles between them
   */
  async #trainerSpotsPlayer(npc, distance) {
    const release = this.lockForScript();
    try {
      playSoundFx(this, AUDIO_KEYS.SFX_EXCLAIM);
      await this.exclaim(npc);
      const steps = Array(Math.max(0, distance)).fill(npc.direction);
      if (steps.length) {
        await npc.walk(steps);
      }
      this.player.face(/** @type {any} */ (OPPOSITE[npc.direction]));
      await this.trainerBattle(npc);
    } finally {
      release();
    }
  }

  /**
   * Full trainer flow for an NPC: intro, battle, and aftermath.
   * @param {NPC} npc
   */
  async trainerBattle(npc) {
    const def = npc.data;
    const trainer = gameData.trainers[def.trainer];
    if (!trainer) {
      console.warn('[WorldScene] unknown trainer', def.trainer);
      return;
    }
    npc.isTalkingToPlayer = true;
    if (trainer.music) {
      playBackgroundMusic(this, AUDIO_KEYS[trainer.music] || trainer.music);
    }
    await this.ui.say(trainer.intro || ['Let\'s battle!'], { speaker: trainer.name });
    const result = await this.startBattle({
      trainer: {
        id: def.id,
        name: trainer.name,
        title: trainer.title,
        portrait: `TRAINER_${trainer.portrait || def.sprite}`,
        sprite: def.sprite || trainer.sprite,
        team: buildTrainerTeam(trainer),
        prize: trainer.prize ?? 0,
        defeatText: trainer.defeat || [],
        aiLevel: trainer.aiLevel ?? 1,
        isLeader: Boolean(trainer.isLeader),
      },
      environment: trainer.environment || this.uru.environment || 'grass',
      canLose: Boolean(trainer.canLose),
      music: trainer.music ? AUDIO_KEYS[trainer.music] || trainer.music : undefined,
    });
    npc.isTalkingToPlayer = false;
    if (result.outcome === 'win' || (result.outcome === 'lose' && trainer.canLose)) {
      dataManager.addDefeatedNpc(def.id);
      if (trainer.onWin && result.outcome === 'win') {
        await this.runScript(trainer.onWin, npc);
      }
      if (trainer.onDone) {
        await this.runScript(trainer.onDone, npc);
      }
      if (def.onDefeat) {
        await this.runScript(def.onDefeat, npc);
      }
    }
  }

  // ------------------------------------------------------------------------------------------
  // interaction
  // ------------------------------------------------------------------------------------------

  /** @param {{x: number, y: number}} target */
  #onBump(target) {
    const tx = Math.round(target.x / TILE_SIZE);
    const ty = Math.round(target.y / TILE_SIZE);
    const warp = (this.uru.warps || []).find((w) => (w.mode || 'bump') === 'bump' && w.x === tx && w.y === ty);
    if (warp && !this.inputLocked) {
      if (warp.dir && warp.dir !== this.player.direction) {
        return;
      }
      this.#useWarp(warp);
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_BUMP, 0.25);
  }

  async #interact() {
    const p = this.player.sprite;
    const target = getTargetPositionFromGameObjectPositionAndDirection({ x: p.x, y: p.y }, this.player.direction);
    const tx = Math.round(target.x / TILE_SIZE);
    const ty = Math.round(target.y / TILE_SIZE);

    const npc = this.npcs.find((n) => n.tilePosition.x === target.x && n.tilePosition.y === target.y);
    if (npc) {
      await this.#talkTo(npc);
      return;
    }
    // talk across counters
    if ((this.uru.counters || []).some((c) => c[0] === tx && c[1] === ty)) {
      const [dx, dy] = STEP[this.player.direction];
      const beyond = { x: target.x + dx * TILE_SIZE, y: target.y + dy * TILE_SIZE };
      const clerk = this.npcs.find((n) => n.tilePosition.x === beyond.x && n.tilePosition.y === beyond.y);
      if (clerk) {
        await this.#talkTo(clerk);
        return;
      }
    }
    const sign = (this.uru.signs || []).find((s) => s.x === tx && s.y === ty);
    if (sign) {
      const release = this.lockForScript();
      await this.ui.say(sign.text);
      release();
      return;
    }
    const itemIdx = this.items.findIndex((i) => i.position.x === target.x && i.position.y === target.y);
    if (itemIdx >= 0) {
      const it = this.items[itemIdx];
      const data = getItem(it.itemId);
      it.gameObject.destroy();
      this.items.splice(itemIdx, 1);
      this.#refreshCollisionLists();
      dataManager.addItemPickedUp(it.id);
      dataManager.addItem(it.itemId, it.quantity);
      playSoundFx(this, AUDIO_KEYS.SFX_ITEM);
      const release = this.lockForScript();
      await this.ui.say(`${dataManager.state.player.name} found ${it.quantity > 1 ? `${it.quantity}x ` : 'a '}${data.name}!`);
      release();
      return;
    }
    const thing = (this.uru.interactables || []).find((s) => s.x === tx && s.y === ty);
    if (thing && this.checkCondition(thing.requires)) {
      await this.runScript(thing.script);
      return;
    }
    if (this.water.has(ty * this.map.width + tx) && this.uru.encounters?.fish) {
      await this.#fish();
    }
  }

  /** Casts the Gaala rod into the water the player is facing. */
  async #fish() {
    const rod = getItemByName('Gaala');
    if (!rod || dataManager.itemCount(rod.id) === 0 || dataManager.party.every((m) => m.hp <= 0)) {
      return;
    }
    const release = this.lockForScript();
    let bite = false;
    try {
      await this.ui.say(`${dataManager.state.player.name} cast the Gaala...`);
      await new Promise((resolve) => {
        this.time.delayedCall(500 + Math.random() * 1000, resolve);
      });
      bite = Math.random() < 0.7;
      if (bite) {
        playSoundFx(this, AUDIO_KEYS.SFX_EXCLAIM);
      }
      await this.ui.say(bite ? 'Oh! A bite!' : 'Not even a nibble...');
    } finally {
      release();
    }
    if (bite) {
      const { species, level } = rollEncounter(this.uru.encounters.fish);
      await this.startBattle({ wild: createMonster(species, level), environment: 'lake' });
    }
  }

  /** @param {NPC} npc */
  async #talkTo(npc) {
    const def = npc.data;
    if (!def.noTurn) {
      npc.facePlayer(this.player.direction);
    }
    if (def.trainer && !dataManager.isNpcDefeated(def.id)) {
      const release = this.lockForScript();
      try {
        await this.trainerBattle(npc);
      } finally {
        release();
      }
      return;
    }
    npc.isTalkingToPlayer = true;
    if (def.trainer && dataManager.isNpcDefeated(def.id)) {
      const trainer = gameData.trainers[def.trainer];
      const after = def.after || trainer?.after || trainer?.defeat;
      if (after) {
        await this.runScript(Array.isArray(after) && typeof after[0] === 'string' ? [{ say: after, speaker: trainer?.name }] : after, npc);
        npc.isTalkingToPlayer = false;
        return;
      }
    }
    await this.runScript(def.script || [{ say: '...' }], npc);
    npc.isTalkingToPlayer = false;
  }

  /**
   * Shows the "!" bubble over an NPC (or the player).
   * @param {NPC | Player} who
   */
  async exclaim(who) {
    const s = who.sprite;
    const bubble = this.textures.exists(UI_KEYS.EXCLAIM)
      ? this.add.image(s.x + 32, s.y - 40, UI_KEYS.EXCLAIM).setScale(4)
      : this.add.text(s.x + 22, s.y - 74, '!', { fontFamily: 'Pixelify', fontSize: '48px', color: '#c4404a', fontStyle: 'bold' });
    bubble.setDepth(1e6 + 1);
    await new Promise((r) => this.tweens.add({ targets: bubble, y: '-=12', duration: 160, yoyo: true, onComplete: r }));
    await new Promise((r) => this.time.delayedCall(450, r));
    bubble.destroy();
  }

  // ------------------------------------------------------------------------------------------
  // scripts, battles, warps
  // ------------------------------------------------------------------------------------------

  /** Locks player input until the returned release function is called (safe across scene restarts). */
  lockForScript() {
    const gen = this.generation;
    this.scriptDepth += 1;
    let released = false;
    return () => {
      if (!released && gen === this.generation) {
        this.scriptDepth = Math.max(0, this.scriptDepth - 1);
      }
      released = true;
    };
  }

  /**
   * @param {any[]} script
   * @param {NPC} [npc]
   */
  async runScript(script, npc) {
    if (!script) {
      return;
    }
    const release = this.lockForScript();
    try {
      await this.scripts.run(script, { npc });
    } catch (e) {
      console.error('[WorldScene] script error', e, script);
    } finally {
      release();
    }
  }

  /**
   * Pauses the world, runs a battle and resolves with its result once the world resumes.
   * @param {import('./battle-scene.js').BattleSceneData} data
   * @returns {Promise<import('./battle-scene.js').BattleResult>}
   */
  startBattle(data) {
    const release = this.lockForScript();
    this.ui.close();
    const musicBefore = currentMusic();
    return new Promise((resolve) => {
      this.game.events.once('battle-finished', (result) => {
        this.lastBattleResult = result;
        this.scene.resume();
        this.scene.resume(SCENE_KEYS.DIALOG_SCENE);
        release();
        if (result.outcome === 'lose' && !result.canLose) {
          this.#blackout();
          resolve(result);
          return;
        }
        if (musicBefore) {
          playBackgroundMusic(this, musicBefore, { restart: true });
        }
        this.cameras.main.fadeIn(400, 0, 0, 0);
        resolve(result);
      });
      this.#battleTransition().then(() => {
        this.scene.pause(SCENE_KEYS.DIALOG_SCENE);
        this.scene.launch(SCENE_KEYS.BATTLE_SCENE, data);
        this.scene.pause();
      });
    });
  }

  #battleTransition() {
    const cam = this.cameras.main;
    return new Promise((resolve) => {
      let flashes = 0;
      const flash = () => {
        cam.flash(120, 255, 255, 255);
        flashes += 1;
        if (flashes < 3) {
          this.time.delayedCall(160, flash);
          return;
        }
        cam.fadeOut(350, 0, 0, 0);
        cam.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => resolve());
      };
      flash();
    });
  }

  #blackout() {
    const r = dataManager.state.respawn;
    dataManager.state.returnPoint = r.returnPoint || null;
    dataManager.party.forEach((m) => fullyHeal(m));
    this.transitioning = true;
    this.scene.restart({ area: r.area, position: { x: r.x, y: r.y }, direction: DIRECTION.UP, isPlayerKnockedOut: true });
  }

  /** @param {any} warp */
  #useWarp(warp) {
    if (warp.requires && !this.checkCondition(warp.requires)) {
      if (warp.lockedText) {
        this.runScript([{ say: warp.lockedText }]);
      }
      return;
    }
    let to = warp.to;
    let toId = warp.toId;
    if (to === '@return') {
      const rp = dataManager.state.returnPoint;
      to = rp?.area || 'basavanagudi';
      toId = rp?.warpId;
    }
    if (warp.setReturn) {
      dataManager.state.returnPoint = { area: this.area, warpId: warp.id };
    }
    playSoundFx(this, AUDIO_KEYS.SFX_DOOR, 0.6);
    this.warpTo({ area: to, warpId: toId });
  }

  /**
   * @param {WorldSceneData} data
   * @returns {Promise<void>}
   */
  warpTo(data) {
    this.transitioning = true;
    return new Promise((resolve) => {
      this.cameras.main.fadeOut(260, 0, 0, 0);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        resolve();
        this.scene.restart(data);
      });
    });
  }

  // ------------------------------------------------------------------------------------------
  // start menu
  // ------------------------------------------------------------------------------------------

  async #openStartMenu() {
    this.menuOpen = true;
    try {
      for (;;) {
        const hasDex = dataManager.hasFlag('GOT_PUSTAKA');
        const options = [
          ...(hasDex ? ['PUSTAKA'] : []),
          ...(dataManager.party.length ? ['URUMON'] : []),
          'BAG',
          dataManager.state.player.name.toUpperCase(),
          'SAVE',
          'OPTIONS',
          ...(dataManager.state.admin ? ['WARP'] : []),
          'EXIT',
        ];
        this.lastMenuIndex = this.lastMenuIndex || 0;
        const idx = await this.ui.choose(options, { x: 1024 - 300, y: 12, width: 288, visibleRows: 7 });
        if (idx < 0) {
          return;
        }
        const choice = options[idx];
        if (choice === 'EXIT') {
          return;
        }
        if (choice === 'WARP') {
          const targets = warpTargets();
          const pick = await this.ui.choose(targets.map((m) => m.name), { x: 1024 - 420, y: 12, width: 408, visibleRows: 8 });
          if (pick >= 0) {
            this.ui.close();
            this.menuOpen = false;
            await this.warpTo({ area: targets[pick].id, adminWarp: true });
            return;
          }
          continue;
        }
        if (choice === 'SAVE') {
          const yes = await this.ui.ask('Save your progress?');
          if (yes) {
            if (dataManager.saveData()) {
              playSoundFx(this, AUDIO_KEYS.SFX_SAVE);
              await this.ui.say(`${dataManager.state.player.name} saved the game.`);
            } else {
              await this.ui.say("The save didn't go through. Your browser may be blocking or out of storage.");
            }
          } else {
            this.ui.close();
          }
          continue;
        }
        const map = {
          PUSTAKA: [SCENE_KEYS.PUSTAKA_SCENE, {}],
          URUMON: [SCENE_KEYS.MONSTER_PARTY_SCENE, { mode: 'world' }],
          BAG: [SCENE_KEYS.INVENTORY_SCENE, { mode: 'world' }],
          OPTIONS: [SCENE_KEYS.OPTIONS_SCENE, {}],
        };
        const target = map[choice] || [SCENE_KEYS.TRAINER_CARD_SCENE, {}];
        await this.openSubScene(target[0], target[1]);
      }
    } finally {
      this.ui.close();
      this.menuOpen = false;
    }
  }

  /**
   * Launches a menu scene over the world and waits until it resumes us.
   * @param {string} key
   * @param {object} data
   * @returns {Promise<any>}
   */
  openSubScene(key, data) {
    return new Promise((resolve) => {
      this.events.once(Phaser.Scenes.Events.RESUME, (sys, resumeData) => {
        this.scene.resume(SCENE_KEYS.DIALOG_SCENE);
        resolve(resumeData);
      });
      this.scene.pause(SCENE_KEYS.DIALOG_SCENE);
      this.scene.launch(key, { ...data, previousSceneName: SCENE_KEYS.WORLD_SCENE });
      this.scene.pause();
    });
  }

  /** Records the current spot as where the player wakes up after blacking out. */
  setRespawnHere() {
    const p = this.player.sprite;
    dataManager.state.respawn = { area: this.area, x: p.x, y: p.y, returnPoint: dataManager.state.returnPoint };
  }

  /** @returns {string} */
  leadName() {
    const lead = dataManager.party[0];
    return lead ? displayName(lead) : '';
  }
}

