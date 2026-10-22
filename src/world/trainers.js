import { createMonster, getMaxHp, getMove } from '../battle/engine/monster.js';
import { dataManager } from '../utils/data-manager.js';

/**
 * Resolves a species reference in trainer data. "RIVAL:n" means stage n (1-3) of the rival's starter line,
 * "PLAYER:n" the same for the player's starter line (used for mirror matches).
 * @param {number | string} ref
 * @returns {number}
 */
export function resolveSpecies(ref) {
  if (typeof ref === 'number') {
    return ref;
  }
  const [who, stage] = ref.split(':');
  const base = who === 'RIVAL' ? dataManager.state.vars.rivalStarter ?? 4 : dataManager.state.vars.starter ?? 1;
  return Number(base) + Number(stage) - 1;
}

/**
 * Builds fresh monsters for a trainer from its data entry.
 * @param {{team: {species: number | string, level: number, moves?: string[]}[]}} trainer
 * @returns {import('../battle/engine/monster.js').Monster[]}
 */
export function buildTrainerTeam(trainer) {
  return trainer.team.map((t) => {
    const mon = createMonster(resolveSpecies(t.species), t.level, {
      moveIds: t.moves ? t.moves.map((m) => (typeof m === 'number' ? m : moveIdByName(m))).filter(Boolean) : undefined,
    });
    // trainer monsters have decent individual values
    Object.keys(mon.sparks).forEach((k) => {
      mon.sparks[k] = Math.max(mon.sparks[k], 8);
    });
    mon.hp = getMaxHp(mon);
    return mon;
  });
}

/** @type {Map<string, number> | null} */
let byName = null;

/** @param {string} name */
function moveIdByName(name) {
  if (!byName) {
    byName = new Map();
    for (let id = 0; id < 400; id += 1) {
      try {
        byName.set(getMove(id).name, id);
      } catch {
        /* gap in ids */
      }
    }
  }
  return byName.get(name);
}
