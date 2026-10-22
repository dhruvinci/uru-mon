/**
 * Monster (Urumon) instances: creation, stats, experience, learning moves and evolution.
 * Pure logic with no Phaser dependency, so it runs in Node tests too.
 */

/**
 * @typedef BaseStats
 * @type {{hp: number, atk: number, def: number, spc: number, spd: number}}
 */

/**
 * @typedef Species
 * @type {object}
 * @property {number} id
 * @property {string} name
 * @property {import('./type-chart.js').UruType[]} types
 * @property {BaseStats} baseStats
 * @property {number} catchRate
 * @property {number} baseExp
 * @property {{level: number, speciesId: number} | null} evolution
 * @property {{level: number, moveId: number}[]} learnset
 * @property {string} dex
 * @property {string} assetKey
 */

/**
 * @typedef MoveData
 * @type {object}
 * @property {number} id
 * @property {string} name
 * @property {import('./type-chart.js').UruType} type
 * @property {'PHYSICAL'|'SPECIAL'|'STATUS'} category
 * @property {number} power
 * @property {number} accuracy 0 means the move never misses
 * @property {number} pp
 * @property {number} priority
 * @property {string} description
 * @property {object | null} effect
 */

/**
 * @typedef MonsterMove
 * @type {{id: number, pp: number}}
 */

/**
 * @typedef {'BRN'|'PSN'|'PAR'|'SLP'} StatusCondition
 */

/**
 * @typedef Monster
 * @type {object}
 * @property {string} uid
 * @property {number} speciesId
 * @property {string | null} nickname
 * @property {number} level
 * @property {number} exp
 * @property {BaseStats} sparks individual values, 0-15 per stat
 * @property {number} hp current HP
 * @property {MonsterMove[]} moves
 * @property {StatusCondition | null} status
 * @property {number} sleepTurns
 */

export const MAX_LEVEL = 100;
export const MAX_MOVES = 4;
/** Gentler-than-classic levelling for a browser game. */
export const EXP_MULTIPLIER = 1.25;
export const STAT_KEYS = /** @type {const} */ (['hp', 'atk', 'def', 'spc', 'spd']);

/** @type {{species: Map<number, Species>, moves: Map<number, MoveData>}} */
const registry = { species: new Map(), moves: new Map() };

/**
 * @param {Species[]} species
 * @param {MoveData[]} moves
 */
export function setGameData(species, moves) {
  registry.species = new Map(species.map((s) => [s.id, s]));
  registry.moves = new Map(moves.map((m) => [m.id, m]));
}

/** @param {number} id @returns {Species} */
export function getSpecies(id) {
  const s = registry.species.get(id);
  if (!s) {
    throw new Error(`unknown species ${id}`);
  }
  return s;
}

/** @param {number} id @returns {MoveData} */
export function getMove(id) {
  const m = registry.moves.get(id);
  if (!m) {
    throw new Error(`unknown move ${id}`);
  }
  return m;
}

/** @returns {Species[]} */
export function allSpecies() {
  return [...registry.species.values()];
}

/** @param {() => number} rng */
export function generateUid(rng = Math.random) {
  return 'xxxxxxxx-xxxx-4xxx'.replace(/x/g, () => Math.floor(rng() * 16).toString(16));
}

/** @param {Monster} mon @returns {string} */
export function displayName(mon) {
  return mon.nickname || getSpecies(mon.speciesId).name;
}

/** @param {number} level @returns {number} total exp needed to reach this level */
export function expForLevel(level) {
  const l = Math.min(level, MAX_LEVEL);
  return l <= 1 ? 0 : l ** 3;
}

/**
 * @param {Monster} mon
 * @returns {BaseStats}
 */
export function getStats(mon) {
  const sp = getSpecies(mon.speciesId);
  const L = mon.level;
  /** @type {BaseStats} */
  const out = { hp: 0, atk: 0, def: 0, spc: 0, spd: 0 };
  STAT_KEYS.forEach((k) => {
    const core = Math.floor((2 * (sp.baseStats[k] + mon.sparks[k]) * L) / 100);
    out[k] = k === 'hp' ? core + L + 10 : core + 5;
  });
  return out;
}

/** @param {Monster} mon @returns {number} */
export function getMaxHp(mon) {
  return getStats(mon).hp;
}

/**
 * The (up to 4) most recent moves a species knows at a level, the classic way wild/trainer
 * monsters get their moves.
 * @param {number} speciesId
 * @param {number} level
 * @returns {number[]}
 */
export function defaultMoveIds(speciesId, level) {
  const known = [];
  getSpecies(speciesId).learnset.forEach((e) => {
    if (e.level <= level && !known.includes(e.moveId)) {
      known.push(e.moveId);
    }
  });
  return known.slice(-MAX_MOVES);
}

/**
 * @param {number} speciesId
 * @param {number} level
 * @param {{rng?: () => number, moveIds?: number[], nickname?: string | null}} [opts]
 * @returns {Monster}
 */
export function createMonster(speciesId, level, opts = {}) {
  const rng = opts.rng || Math.random;
  getSpecies(speciesId);
  /** @type {BaseStats} */
  const sparks = { hp: 0, atk: 0, def: 0, spc: 0, spd: 0 };
  STAT_KEYS.forEach((k) => {
    sparks[k] = Math.floor(rng() * 16);
  });
  const moveIds = opts.moveIds && opts.moveIds.length > 0 ? opts.moveIds : defaultMoveIds(speciesId, level);
  /** @type {Monster} */
  const mon = {
    uid: generateUid(rng),
    speciesId,
    nickname: opts.nickname ?? null,
    level,
    exp: expForLevel(level),
    sparks,
    hp: 1,
    moves: moveIds.slice(0, MAX_MOVES).map((id) => ({ id, pp: getMove(id).pp })),
    status: null,
    sleepTurns: 0,
  };
  mon.hp = getMaxHp(mon);
  return mon;
}

/**
 * Fully restores HP, PP and status, as at a Darshini.
 * @param {Monster} mon
 */
export function fullyHeal(mon) {
  mon.hp = getMaxHp(mon);
  mon.status = null;
  mon.sleepTurns = 0;
  mon.moves.forEach((m) => {
    m.pp = getMove(m.id).pp;
  });
}

/**
 * Exp a defeated monster gives.
 * @param {Monster} defeated
 * @param {boolean} isTrainerBattle
 * @returns {number}
 */
export function expYield(defeated, isTrainerBattle) {
  const base = Math.floor((getSpecies(defeated.speciesId).baseExp * defeated.level) / 7);
  return Math.max(1, Math.floor(base * EXP_MULTIPLIER * (isTrainerBattle ? 1.5 : 1)));
}

/**
 * @typedef LevelUpResult
 * @type {object}
 * @property {number} fromLevel
 * @property {number} toLevel
 * @property {BaseStats} before
 * @property {BaseStats} after
 * @property {number[]} learned move ids learned automatically (had a free slot)
 * @property {number[]} pendingMoves move ids that need the player to choose a move to forget
 */

/**
 * Adds exp and applies level ups. HP rises by the same amount max HP rises.
 * @param {Monster} mon
 * @param {number} amount
 * @returns {LevelUpResult}
 */
export function gainExp(mon, amount) {
  const before = getStats(mon);
  const fromLevel = mon.level;
  /** @type {number[]} */
  const learned = [];
  /** @type {number[]} */
  const pendingMoves = [];
  if (mon.level >= MAX_LEVEL) {
    return { fromLevel, toLevel: mon.level, before, after: before, learned, pendingMoves };
  }
  mon.exp += amount;
  while (mon.level < MAX_LEVEL && mon.exp >= expForLevel(mon.level + 1)) {
    mon.level += 1;
    movesLearnedAtLevel(mon.speciesId, mon.level).forEach((moveId) => {
      if (mon.moves.some((m) => m.id === moveId)) {
        return;
      }
      if (mon.moves.length < MAX_MOVES) {
        mon.moves.push({ id: moveId, pp: getMove(moveId).pp });
        learned.push(moveId);
      } else {
        pendingMoves.push(moveId);
      }
    });
  }
  if (mon.level >= MAX_LEVEL) {
    mon.exp = Math.min(mon.exp, expForLevel(MAX_LEVEL));
  }
  const after = getStats(mon);
  if (mon.hp > 0) {
    mon.hp = Math.min(after.hp, mon.hp + (after.hp - before.hp));
  }
  return { fromLevel, toLevel: mon.level, before, after, learned, pendingMoves };
}

/**
 * @param {number} speciesId
 * @param {number} level
 * @returns {number[]}
 */
export function movesLearnedAtLevel(speciesId, level) {
  return getSpecies(speciesId)
    .learnset.filter((e) => e.level === level)
    .map((e) => e.moveId);
}

/**
 * Replaces the move in a slot (or appends when slot is -1 and there's room).
 * @param {Monster} mon
 * @param {number} moveId
 * @param {number} slot
 */
export function teachMove(mon, moveId, slot) {
  const entry = { id: moveId, pp: getMove(moveId).pp };
  if (slot < 0 || slot >= mon.moves.length) {
    if (mon.moves.length < MAX_MOVES) {
      mon.moves.push(entry);
    }
    return;
  }
  mon.moves[slot] = entry;
}

/**
 * @param {Monster} mon
 * @returns {number | null} species id it is ready to evolve into
 */
export function pendingEvolution(mon) {
  const evo = getSpecies(mon.speciesId).evolution;
  if (evo && mon.level >= evo.level) {
    return evo.speciesId;
  }
  return null;
}

/**
 * Evolves in place, keeping HP damage proportionate and learning the new form's moves for this level.
 * @param {Monster} mon
 * @param {number} intoSpeciesId
 * @returns {{learned: number[], pendingMoves: number[]}}
 */
export function evolve(mon, intoSpeciesId) {
  const oldMax = getMaxHp(mon);
  const missing = oldMax - mon.hp;
  mon.speciesId = intoSpeciesId;
  mon.hp = Math.max(mon.hp > 0 ? 1 : 0, getMaxHp(mon) - missing);
  /** @type {number[]} */
  const learned = [];
  /** @type {number[]} */
  const pendingMoves = [];
  movesLearnedAtLevel(intoSpeciesId, mon.level).forEach((moveId) => {
    if (mon.moves.some((m) => m.id === moveId)) {
      return;
    }
    if (mon.moves.length < MAX_MOVES) {
      mon.moves.push({ id: moveId, pp: getMove(moveId).pp });
      learned.push(moveId);
    } else {
      pendingMoves.push(moveId);
    }
  });
  return { learned, pendingMoves };
}
