/**
 * Static game content loaded once at boot (species, moves, items, map manifest).
 */
import { setGameData } from '../battle/engine/monster.js';

/**
 * @typedef ItemData
 * @type {object}
 * @property {number} id
 * @property {string} name
 * @property {'CAPTURE'|'HEAL'|'STATUS'|'REVIVE'|'PP'|'REPEL'|'KEY'} category
 * @property {number} price
 * @property {string} description
 * @property {any} effect
 */

/**
 * @typedef MapManifestEntry
 * @type {object}
 * @property {string} id
 * @property {string} name
 * @property {number} width tiles
 * @property {number} height tiles
 * @property {boolean} interior
 */

export const gameData = {
  /** @type {import('../battle/engine/monster.js').Species[]} */
  species: [],
  /** @type {import('../battle/engine/monster.js').MoveData[]} */
  moves: [],
  /** @type {ItemData[]} */
  items: [],
  /** @type {MapManifestEntry[]} */
  maps: [],
  /** @type {Record<string, any>} */
  trainers: {},
};

/**
 * @param {{species: any[], moves: any[], items: ItemData[], maps: MapManifestEntry[], trainers?: Record<string, any>}} data
 */
export function initGameData(data) {
  gameData.species = data.species;
  gameData.moves = data.moves;
  gameData.items = data.items;
  gameData.maps = data.maps;
  gameData.trainers = data.trainers || {};
  setGameData(data.species, data.moves);
}

/** @param {number} id @returns {ItemData | undefined} */
export function getItem(id) {
  return gameData.items.find((i) => i.id === id);
}

/** @param {string} name @returns {ItemData | undefined} */
export function getItemByName(name) {
  return gameData.items.find((i) => i.name === name);
}

/** @param {string} id @returns {MapManifestEntry | undefined} */
export function getMapInfo(id) {
  return gameData.maps.find((m) => m.id === id);
}
