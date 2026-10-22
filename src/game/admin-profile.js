import { dataManager } from '../utils/data-manager.js';
import { allSpecies, createMonster } from '../battle/engine/monster.js';
import { gameData } from './game-data.js';

/** Main-story flags: everything is open, but every legendary is still waiting to be met. */
const STORY_FLAGS = [
  'GOT_STARTER', 'GOT_PUSTAKA', 'RIVAL1_DONE', 'CUBBON_GRUNTS_DONE', 'RIVAL2_DONE', 'RIVAL3_DONE',
  'BELLANDUR_ADMIN_DONE', 'BELLANDUR_DONE', 'RIVAL4_DONE', 'NANDI_DONE', 'CHAMPION_DONE', 'GOT_GAALA',
];
const BADGES = ['GRASS', 'FIGHT', 'ELECTRIC', 'MIND', 'SPIRIT', 'SKY'];
const METRO = ['basavanagudi', 'lalbagh', 'mg_road', 'whitefield', 'malleshwaram', 'palace_road'];
const PARTY = [[6, 60], [3, 60], [9, 60], [145, 60], [146, 60], [64, 60]];

/** The admin profile shows on the title screen when running locally or with ?admin in the URL. */
export function adminAvailable() {
  const { hostname, search } = window.location;
  return /(^|[?&])admin\b/.test(search) || hostname === 'localhost' || hostname === '127.0.0.1';
}

/**
 * Switches to the admin save slot. A fresh admin profile has every Urumon (Namma Cloud holds all 150 at Lv 50),
 * every badge and key item, 99 of everything else, and WARP in the START menu to jump to any map.
 * An existing admin save is kept, so admin progress carries over between sessions.
 */
export function startAdminProfile() {
  dataManager.useProfile('admin');
  if (dataManager.hasSave()) {
    dataManager.loadData();
    dataManager.state.admin = true;
    return;
  }
  dataManager.startNewGame();
  const s = dataManager.state;
  s.admin = true;
  s.gameStarted = true;
  s.player.name = 'Admin';
  s.player.gender = 'boy';
  s.player.money = 999999;
  s.player.badges = [...BADGES];
  s.player.location = { area: 'player_house_1f', isInterior: true };
  s.player.position = { x: 3 * 64, y: 5 * 64 };
  s.flags = [...STORY_FLAGS];
  s.metroStations = [...METRO];
  s.vars = { starter: 4, starterName: 'Kaapup', rivalStarter: 7, rivalStarterName: 'Elanee' };
  s.inventory = gameData.items.map((item) => ({ itemId: item.id, quantity: item.category === 'KEY' ? 1 : 99 }));
  s.monsters.inParty = PARTY.map(([species, level]) => createMonster(species, level));
  s.monsters.boxes = allSpecies().map((sp) => createMonster(sp.id, 50));
  const ids = allSpecies().map((sp) => sp.id);
  s.pustaka = { seen: [...ids], caught: [...ids] };
}

/** Every map the admin can warp to, outdoor areas first. */
export function warpTargets() {
  const maps = [...(gameData.maps || [])];
  return maps.sort((a, b) => Number(a.interior) - Number(b.interior));
}
