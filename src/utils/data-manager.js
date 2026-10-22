import Phaser from '../lib/phaser.js';
import { DIRECTION } from '../common/direction.js';
import { TEXT_SPEED } from '../config.js';
import { TEXT_SPEED_OPTIONS, BATTLE_SCENE_OPTIONS, BATTLE_STYLE_OPTIONS, SOUND_OPTIONS } from '../common/options.js';
import { exhaustiveGuard } from './guard.js';
import { getItem } from '../game/game-data.js';

/** One save slot per profile; the admin profile never touches the player's own save. */
const SAVE_KEYS = { main: 'URU_MON_SAVE_V1', admin: 'URU_MON_SAVE_V1_ADMIN' };
export const PARTY_SIZE = 6;
export const STARTING_AREA = 'player_house_2f';

/**
 * @typedef PlayerLocation
 * @type {object}
 * @property {string} area
 * @property {boolean} [isInterior]
 */

/**
 * @typedef GlobalState
 * @type {object}
 * @property {object} player
 * @property {string} player.name
 * @property {'boy'|'girl'} player.gender
 * @property {{x: number, y: number}} player.position
 * @property {import('../common/direction.js').Direction} player.direction
 * @property {PlayerLocation} player.location
 * @property {number} player.money
 * @property {string[]} player.badges
 * @property {number} player.playTimeSeconds
 * @property {object} options
 * @property {boolean} gameStarted
 * @property {{inParty: import('../battle/engine/monster.js').Monster[], boxes: import('../battle/engine/monster.js').Monster[]}} monsters
 * @property {{itemId: number, quantity: number}[]} inventory
 * @property {string[]} itemsPickedUp
 * @property {string[]} viewedEvents
 * @property {string[]} flags
 * @property {string[]} defeatedNpcs
 * @property {{seen: number[], caught: number[]}} pustaka
 * @property {{area: string, x: number, y: number}} respawn
 * @property {{area: string, entranceId: string} | null} returnPoint
 * @property {string[]} metroStations
 * @property {number} repelSteps
 * @property {Record<string, any>} vars
 */

/** @returns {GlobalState} */
function initialState() {
  return {
    player: {
      name: 'Kiran',
      gender: 'boy',
      position: { x: 0, y: 0 },
      direction: DIRECTION.DOWN,
      location: { area: STARTING_AREA, isInterior: true },
      money: 3000,
      badges: [],
      playTimeSeconds: 0,
    },
    options: {
      textSpeed: TEXT_SPEED_OPTIONS.MID,
      battleSceneAnimations: BATTLE_SCENE_OPTIONS.ON,
      battleStyle: BATTLE_STYLE_OPTIONS.SHIFT,
      sound: SOUND_OPTIONS.ON,
      volume: 3,
      menuColor: 0,
    },
    gameStarted: false,
    monsters: { inParty: [], boxes: [] },
    inventory: [{ itemId: 1, quantity: 3 }],
    itemsPickedUp: [],
    viewedEvents: [],
    flags: [],
    defeatedNpcs: [],
    pustaka: { seen: [], caught: [] },
    respawn: { area: 'player_house_1f', x: 3 * 64, y: 5 * 64 },
    returnPoint: null,
    metroStations: [],
    repelSteps: 0,
    vars: {},
  };
}

export const DATA_MANAGER_STORE_KEYS = Object.freeze({
  PLAYER_POSITION: 'PLAYER_POSITION',
  PLAYER_DIRECTION: 'PLAYER_DIRECTION',
  PLAYER_LOCATION: 'PLAYER_LOCATION',
  OPTIONS_TEXT_SPEED: 'OPTIONS_TEXT_SPEED',
  OPTIONS_BATTLE_SCENE_ANIMATIONS: 'OPTIONS_BATTLE_SCENE_ANIMATIONS',
  OPTIONS_BATTLE_STYLE: 'OPTIONS_BATTLE_STYLE',
  OPTIONS_SOUND: 'OPTIONS_SOUND',
  OPTIONS_VOLUME: 'OPTIONS_VOLUME',
  OPTIONS_MENU_COLOR: 'OPTIONS_MENU_COLOR',
  GAME_STARTED: 'GAME_STARTED',
  MONSTERS_IN_PARTY: 'MONSTERS_IN_PARTY',
  INVENTORY: 'INVENTORY',
  ITEMS_PICKED_UP: 'ITEMS_PICKED_UP',
  VIEWED_EVENTS: 'VIEWED_EVENTS',
  FLAGS: 'FLAGS',
  DEFEATED_NPCS: 'DEFEATED_NPCS',
});

/** key -> [getter, setter] over the state object */
const KEY_PATHS = {
  PLAYER_POSITION: ['player', 'position'],
  PLAYER_DIRECTION: ['player', 'direction'],
  PLAYER_LOCATION: ['player', 'location'],
  OPTIONS_TEXT_SPEED: ['options', 'textSpeed'],
  OPTIONS_BATTLE_SCENE_ANIMATIONS: ['options', 'battleSceneAnimations'],
  OPTIONS_BATTLE_STYLE: ['options', 'battleStyle'],
  OPTIONS_SOUND: ['options', 'sound'],
  OPTIONS_VOLUME: ['options', 'volume'],
  OPTIONS_MENU_COLOR: ['options', 'menuColor'],
  GAME_STARTED: ['gameStarted'],
  MONSTERS_IN_PARTY: ['monsters', 'inParty'],
  INVENTORY: ['inventory'],
  ITEMS_PICKED_UP: ['itemsPickedUp'],
  VIEWED_EVENTS: ['viewedEvents'],
  FLAGS: ['flags'],
  DEFEATED_NPCS: ['defeatedNpcs'],
};

/** Minimal key/value facade kept for the scenes written against the original store API. */
class StateStore {
  /** @param {DataManager} dm */
  constructor(dm) {
    this.dm = dm;
  }

  /** @param {string} key */
  get(key) {
    const path = KEY_PATHS[key];
    if (!path) {
      return undefined;
    }
    return path.reduce((obj, k) => (obj ? obj[k] : undefined), /** @type {any} */ (this.dm.state));
  }

  /** @param {string} key @param {any} value */
  set(key, value) {
    const path = KEY_PATHS[key];
    if (!path) {
      return;
    }
    let obj = /** @type {any} */ (this.dm.state);
    for (let i = 0; i < path.length - 1; i += 1) {
      obj = obj[path[i]];
    }
    obj[path[path.length - 1]] = value;
  }
}

class DataManager extends Phaser.Events.EventEmitter {
  constructor() {
    super();
    /** @type {GlobalState} */
    this.state = initialState();
    this.store = new StateStore(this);
    this.sessionStart = Date.now();
    /** @type {'main'|'admin'} */
    this.profile = 'main';
  }

  get storageKey() {
    return SAVE_KEYS[this.profile];
  }

  /** @param {'main'|'admin'} profile */
  useProfile(profile) {
    this.profile = profile;
  }

  /** @returns {boolean} whether a save exists */
  hasSave() {
    try {
      return localStorage.getItem(this.storageKey) !== null;
    } catch {
      return false;
    }
  }

  loadData() {
    let raw = null;
    try {
      raw = localStorage.getItem(this.storageKey);
    } catch {
      console.warn('[DataManager] localStorage unavailable; progress will not persist.');
      return;
    }
    if (raw === null) {
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      const base = initialState();
      this.state = {
        ...base,
        ...parsed,
        player: { ...base.player, ...parsed.player },
        options: { ...base.options, ...parsed.options },
        monsters: { ...base.monsters, ...parsed.monsters },
        pustaka: { ...base.pustaka, ...parsed.pustaka },
      };
      this.sessionStart = Date.now();
    } catch (error) {
      console.warn('[DataManager] could not parse saved data', error);
    }
  }

  /** @returns {boolean} whether the save reached storage */
  saveData() {
    this.#accumulatePlayTime();
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.state));
      return true;
    } catch (error) {
      console.warn('[DataManager] could not save', error);
      return false;
    }
  }

  /** Persists options only (used from the title screen before a game exists). */
  saveOptions() {
    if (this.hasSave()) {
      try {
        const parsed = JSON.parse(localStorage.getItem(this.storageKey) || '{}');
        parsed.options = this.state.options;
        localStorage.setItem(this.storageKey, JSON.stringify(parsed));
      } catch {
        /* ignore */
      }
    }
  }

  #accumulatePlayTime() {
    const now = Date.now();
    this.state.player.playTimeSeconds += Math.floor((now - this.sessionStart) / 1000);
    this.sessionStart = now;
  }

  /** @returns {number} */
  getPlayTimeSeconds() {
    return this.state.player.playTimeSeconds + Math.floor((Date.now() - this.sessionStart) / 1000);
  }

  startNewGame() {
    const options = { ...this.state.options };
    this.state = initialState();
    this.state.options = options;
    this.sessionStart = Date.now();
  }

  /** @returns {number} */
  getAnimatedTextSpeed() {
    const chosen = this.state.options.textSpeed;
    switch (chosen) {
      case TEXT_SPEED_OPTIONS.FAST:
        return TEXT_SPEED.FAST;
      case TEXT_SPEED_OPTIONS.MID:
        return TEXT_SPEED.MEDIUM;
      case TEXT_SPEED_OPTIONS.SLOW:
        return TEXT_SPEED.SLOW;
      default:
        exhaustiveGuard(chosen);
        return TEXT_SPEED.MEDIUM;
    }
  }

  // ---- party & storage ----------------------------------------------------------------------

  /** @returns {import('../battle/engine/monster.js').Monster[]} */
  get party() {
    return this.state.monsters.inParty;
  }

  /** @returns {import('../battle/engine/monster.js').Monster[]} */
  get boxes() {
    return this.state.monsters.boxes;
  }

  isPartyFull() {
    return this.party.length >= PARTY_SIZE;
  }

  /**
   * Adds a caught/received monster to the party, or to Namma Cloud storage if the party is full.
   * @param {import('../battle/engine/monster.js').Monster} mon
   * @returns {'party'|'box'}
   */
  addMonster(mon) {
    this.markCaught(mon.speciesId);
    if (!this.isPartyFull()) {
      this.party.push(mon);
      return 'party';
    }
    this.boxes.push(mon);
    return 'box';
  }

  /** @param {number} speciesId */
  markSeen(speciesId) {
    if (!this.state.pustaka.seen.includes(speciesId)) {
      this.state.pustaka.seen.push(speciesId);
    }
  }

  /** @param {number} speciesId */
  markCaught(speciesId) {
    this.markSeen(speciesId);
    if (!this.state.pustaka.caught.includes(speciesId)) {
      this.state.pustaka.caught.push(speciesId);
    }
  }

  // ---- inventory ----------------------------------------------------------------------------

  /**
   * @param {Phaser.Scene} [scene] unused, kept for older callers
   * @returns {{item: import('../game/game-data.js').ItemData, quantity: number}[]}
   */
  // eslint-disable-next-line no-unused-vars
  getInventory(scene) {
    return this.state.inventory
      .filter((e) => e.quantity > 0)
      .map((e) => ({ item: getItem(e.itemId), quantity: e.quantity }))
      .filter((e) => e.item);
  }

  /** @param {number} itemId */
  itemCount(itemId) {
    return this.state.inventory.find((e) => e.itemId === itemId)?.quantity ?? 0;
  }

  /**
   * @param {{id: number} | number} item
   * @param {number} quantity
   */
  addItem(item, quantity) {
    const id = typeof item === 'number' ? item : item.id;
    const existing = this.state.inventory.find((e) => e.itemId === id);
    if (existing) {
      existing.quantity += quantity;
    } else {
      this.state.inventory.push({ itemId: id, quantity });
    }
  }

  /**
   * @param {number} itemId
   * @param {number} [quantity=1]
   * @returns {boolean}
   */
  removeItem(itemId, quantity = 1) {
    const existing = this.state.inventory.find((e) => e.itemId === itemId);
    if (!existing || existing.quantity < quantity) {
      return false;
    }
    existing.quantity -= quantity;
    if (existing.quantity <= 0) {
      this.state.inventory = this.state.inventory.filter((e) => e.itemId !== itemId);
    }
    return true;
  }

  /** @param {string} id */
  addItemPickedUp(id) {
    if (!this.state.itemsPickedUp.includes(String(id))) {
      this.state.itemsPickedUp.push(String(id));
    }
  }

  // ---- money & progress ---------------------------------------------------------------------

  get money() {
    return this.state.player.money;
  }

  /** @param {number} delta */
  addMoney(delta) {
    this.state.player.money = Math.max(0, Math.min(999999, this.state.player.money + delta));
  }

  /** @param {string} badge */
  addBadge(badge) {
    if (!this.state.player.badges.includes(badge)) {
      this.state.player.badges.push(badge);
    }
  }

  /** @param {string | number} eventId */
  viewedEvent(eventId) {
    if (!this.state.viewedEvents.includes(String(eventId))) {
      this.state.viewedEvents.push(String(eventId));
    }
  }

  /** @returns {Set<string>} */
  getFlags() {
    return new Set(this.state.flags);
  }

  /** @param {string} flag */
  hasFlag(flag) {
    return this.state.flags.includes(flag);
  }

  /** @param {string} flag */
  addFlag(flag) {
    if (!this.state.flags.includes(flag)) {
      this.state.flags.push(flag);
    }
  }

  /** @param {string} flag */
  removeFlag(flag) {
    this.state.flags = this.state.flags.filter((f) => f !== flag);
  }

  /** @param {string | number} npcId */
  addDefeatedNpc(npcId) {
    if (!this.state.defeatedNpcs.includes(String(npcId))) {
      this.state.defeatedNpcs.push(String(npcId));
    }
  }

  /** @returns {Set<string>} */
  getDefeatedNpcs() {
    return new Set(this.state.defeatedNpcs);
  }

  /** @param {string | number} npcId */
  isNpcDefeated(npcId) {
    return this.state.defeatedNpcs.includes(String(npcId));
  }
}

export const dataManager = new DataManager();
