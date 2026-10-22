/**
 * Turn-based battle resolution. The engine mutates the monster objects it is given and returns
 * a list of BattleEvents that the battle scene plays back (messages, HP changes, faints...).
 * No Phaser dependency.
 */
import { typeEffectiveness } from './type-chart.js';
import { displayName, getMaxHp, getMove, getSpecies, getStats } from './monster.js';

/**
 * @typedef {import('./monster.js').Monster} Monster
 * @typedef {'player'|'enemy'} Side
 */

/**
 * @typedef BattleEvent
 * @type {object}
 * @property {'MESSAGE'|'MOVE_USED'|'DAMAGE'|'HEAL'|'STATUS'|'STATUS_CURED'|'STAT_CHANGE'|'FAINT'|'SWITCH_IN'|'CATCH'|'RUN'|'MISS'} type
 * @property {Side} [side]
 * @property {string} [text]
 * @property {number} [moveId]
 * @property {number} [hp]
 * @property {number} [maxHp]
 * @property {number} [amount]
 * @property {number} [effectiveness]
 * @property {boolean} [crit]
 * @property {string | null} [status]
 * @property {number} [partyIndex]
 * @property {number} [shakes]
 * @property {boolean} [success]
 */

/**
 * @typedef BattleAction
 * @type {{kind: 'MOVE', slot: number} | {kind: 'SWITCH', index: number} | {kind: 'ITEM', item: object, targetIndex: number} | {kind: 'CATCH', item: object} | {kind: 'RUN'}}
 */

/**
 * @param {import('./monster.js').Monster} mon
 * @param {import('./monster.js').StatusCondition} status
 */
function statusImmune(mon, status) {
  return (
    (status === 'BRN' && hasType(mon, 'FIRE')) ||
    (status === 'PSN' && (hasType(mon, 'TOXIC') || hasType(mon, 'METAL'))) ||
    (status === 'PAR' && hasType(mon, 'ELECTRIC')) ||
    (status === 'FRZ' && hasType(mon, 'FROST'))
  );
}

export const STRUGGLE_MOVE = Object.freeze({
  id: 0,
  name: 'Struggle',
  type: 'NORMAL',
  category: 'PHYSICAL',
  power: 50,
  accuracy: 0,
  pp: 1,
  priority: 0,
  description: 'Used when out of PP.',
  effect: { kind: 'recoil', ratio: 0.25 },
});

const STAT_NAMES = { atk: 'ATK', def: 'DEF', spc: 'SPC', spd: 'SPD', acc: 'accuracy', eva: 'evasion' };
const STATUS_TEXT = {
  BRN: 'was burned',
  PSN: 'was poisoned',
  PAR: 'is paralyzed! It may be unable to move',
  SLP: 'fell asleep',
  FRZ: 'was frozen solid',
};

/** @param {number} stage */
export function stageMultiplier(stage) {
  return stage >= 0 ? (2 + stage) / 2 : 2 / (2 - stage);
}

/** @param {number} stage */
function accuracyStageMultiplier(stage) {
  return stage >= 0 ? (3 + stage) / 3 : 3 / (3 - stage);
}

function freshVolatile() {
  return { stages: { atk: 0, def: 0, spc: 0, spd: 0, acc: 0, eva: 0 }, flinch: false };
}

/**
 * @param {Monster} mon
 * @param {import('./type-chart.js').UruType} type
 */
function hasType(mon, type) {
  return getSpecies(mon.speciesId).types.includes(type);
}

export class Battle {
  /**
   * @param {object} config
   * @param {Monster[]} config.playerParty
   * @param {Monster[]} config.enemyParty
   * @param {boolean} [config.isTrainer=false]
   * @param {number} [config.aiLevel=0] 0 random, 1 trainer, 2 leader
   * @param {() => number} [config.rng]
   */
  constructor({ playerParty, enemyParty, isTrainer = false, aiLevel = 0, rng = Math.random }) {
    this.rng = rng;
    this.isTrainer = isTrainer;
    this.aiLevel = aiLevel;
    this.runAttempts = 0;
    this.sides = {
      player: { party: playerParty, active: Math.max(0, playerParty.findIndex((m) => m.hp > 0)), vol: freshVolatile() },
      enemy: { party: enemyParty, active: 0, vol: freshVolatile() },
    };
    /** uids of player monsters that have been out against the current enemy */
    this.participants = new Set([this.playerActive.uid]);
  }

  /** @type {Monster} */
  get playerActive() {
    return this.sides.player.party[this.sides.player.active];
  }

  /** @type {Monster} */
  get enemyActive() {
    return this.sides.enemy.party[this.sides.enemy.active];
  }

  /** @param {Side} side */
  active(side) {
    return this.sides[side].party[this.sides[side].active];
  }

  /** @param {Side} side */
  other(side) {
    return side === 'player' ? 'enemy' : 'player';
  }

  /** @param {Side} side */
  hasUsableMonsters(side) {
    return this.sides[side].party.some((m) => m.hp > 0);
  }

  /** @param {Side} side @returns {string} */
  label(side) {
    const name = displayName(this.active(side));
    if (side === 'enemy') {
      return this.isTrainer ? `Foe ${name}` : `Wild ${name}`;
    }
    return name;
  }

  /** @param {number} chancePercent */
  roll(chancePercent) {
    return this.rng() * 100 < chancePercent;
  }

  /**
   * Effective in-battle stat.
   * @param {Side} side
   * @param {'atk'|'def'|'spc'|'spd'} stat
   */
  effectiveStat(side, stat) {
    const mon = this.active(side);
    let value = getStats(mon)[stat] * stageMultiplier(this.sides[side].vol.stages[stat]);
    if (stat === 'spd' && mon.status === 'PAR') {
      value *= 0.5;
    }
    return Math.max(1, Math.floor(value));
  }

  // ------------------------------------------------------------------------------------------
  // AI
  // ------------------------------------------------------------------------------------------

  /** @returns {BattleAction} */
  chooseEnemyAction() {
    const mon = this.enemyActive;
    const usable = mon.moves.map((m, i) => ({ m, i })).filter(({ m }) => m.pp > 0);
    if (usable.length === 0) {
      return { kind: 'MOVE', slot: -1 };
    }
    if (this.aiLevel === 0) {
      return { kind: 'MOVE', slot: usable[Math.floor(this.rng() * usable.length)].i };
    }
    const scored = usable.map(({ m, i }) => ({ i, score: this.scoreMove('enemy', getMove(m.id)) }));
    scored.sort((a, b) => b.score - a.score);
    const smartChance = this.aiLevel >= 2 ? 0.9 : 0.65;
    if (this.rng() < smartChance) {
      return { kind: 'MOVE', slot: scored[0].i };
    }
    return { kind: 'MOVE', slot: scored[Math.floor(this.rng() * scored.length)].i };
  }

  /**
   * Rough desirability of a move for the AI.
   * @param {Side} side
   * @param {import('./monster.js').MoveData} move
   */
  scoreMove(side, move) {
    const user = this.active(side);
    const target = this.active(this.other(side));
    const effect = move.effect || {};
    if (move.category !== 'STATUS') {
      const eff = typeEffectiveness(move.type, getSpecies(target.speciesId).types);
      if (eff === 0) {
        return -1;
      }
      const stab = hasType(user, move.type) ? 1.5 : 1;
      const power = effect.kind === 'fixed' ? user.level * 1.2 : move.power * (effect.kind === 'multi' ? 3 : 1);
      const acc = move.accuracy === 0 ? 1 : move.accuracy / 100;
      const expected = power * eff * stab * acc;
      // finishing blows are worth extra
      const estimate = this.estimateDamage(side, move);
      return expected / 40 + (estimate >= target.hp ? 2 : 0);
    }
    switch (effect.kind) {
      case 'status':
        return target.status || statusImmune(target, effect.status) ? -1 : 1.2;
      case 'heal':
      case 'rest': {
        const ratio = user.hp / getMaxHp(user);
        return ratio < 0.4 ? 2.5 : ratio < 0.7 ? 0.6 : -1;
      }
      case 'stat': {
        const tgt = effect.target === 'self' ? side : this.other(side);
        const stages = this.sides[tgt].vol.stages;
        const room = Object.entries(effect.stats).some(([k, delta]) => {
          const v = stages[k.toLowerCase()];
          return delta > 0 ? v < 2 : v > -2;
        });
        return room ? 0.9 : -1;
      }
      default:
        return 0.5;
    }
  }

  /**
   * Average-roll damage estimate (no crit), used by the AI.
   * @param {Side} side
   * @param {import('./monster.js').MoveData} move
   */
  estimateDamage(side, move) {
    const target = this.active(this.other(side));
    const eff = typeEffectiveness(move.type, getSpecies(target.speciesId).types);
    return Math.floor(this.baseDamage(side, move, false) * eff * 0.92);
  }

  // ------------------------------------------------------------------------------------------
  // Turn resolution
  // ------------------------------------------------------------------------------------------

  /**
   * Resolves one full turn.
   * @param {BattleAction} playerAction
   * @param {BattleAction} [enemyAction]
   * @returns {{events: BattleEvent[], fled: boolean, caught: boolean}}
   */
  resolveTurn(playerAction, enemyAction) {
    /** @type {BattleEvent[]} */
    const events = [];
    const result = { events, fled: false, caught: false };
    const enemyAct = enemyAction || this.chooseEnemyAction();

    // non-move actions happen first
    if (playerAction.kind === 'RUN') {
      if (this.tryRun(events)) {
        result.fled = true;
        return result;
      }
    } else if (playerAction.kind === 'CATCH') {
      if (this.tryCatch(playerAction.item, events)) {
        result.caught = true;
        return result;
      }
    } else if (playerAction.kind === 'SWITCH') {
      this.switchIn('player', playerAction.index, events);
    } else if (playerAction.kind === 'ITEM') {
      const target = this.sides.player.party[playerAction.targetIndex];
      const outcome = applyItem(target, playerAction.item);
      events.push({ type: 'MESSAGE', text: `You used ${playerAction.item.name}.` });
      if (outcome.ok) {
        if (playerAction.targetIndex === this.sides.player.active) {
          events.push({ type: 'HEAL', side: 'player', hp: target.hp, maxHp: getMaxHp(target), amount: 0 });
          if (!target.status) {
            events.push({ type: 'STATUS_CURED', side: 'player', status: null });
          }
        }
      }
      events.push({ type: 'MESSAGE', text: outcome.message });
    }

    /** @type {{side: Side, move: import('./monster.js').MoveData, slot: number}[]} */
    const movers = [];
    if (playerAction.kind === 'MOVE') {
      movers.push({ side: 'player', ...this.moveForSlot('player', playerAction.slot) });
    }
    if (enemyAct.kind === 'MOVE') {
      movers.push({ side: 'enemy', ...this.moveForSlot('enemy', enemyAct.slot) });
    }
    movers.sort((a, b) => {
      if (a.move.priority !== b.move.priority) {
        return b.move.priority - a.move.priority;
      }
      const sa = this.effectiveStat(a.side, 'spd');
      const sb = this.effectiveStat(b.side, 'spd');
      if (sa !== sb) {
        return sb - sa;
      }
      return this.rng() < 0.5 ? -1 : 1;
    });

    movers.forEach((m, order) => {
      if (this.active(m.side).hp <= 0 || this.active(this.other(m.side)).hp <= 0) {
        return;
      }
      this.executeMove(m.side, m.move, m.slot, order === 0, events);
    });

    this.endOfTurn(events);
    return result;
  }

  /**
   * @param {Side} side
   * @param {number} slot
   */
  moveForSlot(side, slot) {
    const mon = this.active(side);
    const entry = mon.moves[slot];
    if (!entry || mon.moves.every((m) => m.pp <= 0)) {
      return { move: /** @type {any} */ (STRUGGLE_MOVE), slot: -1 };
    }
    return { move: getMove(entry.id), slot };
  }

  /**
   * @param {Side} side
   * @param {import('./monster.js').MoveData} move
   * @param {number} slot
   * @param {boolean} movedFirst
   * @param {BattleEvent[]} events
   */
  executeMove(side, move, slot, movedFirst, events) {
    const user = this.active(side);
    const foeSide = this.other(side);
    const foe = this.active(foeSide);
    const vol = this.sides[side].vol;

    // things that stop a monster from acting
    if (user.status === 'SLP') {
      user.sleepTurns -= 1;
      if (user.sleepTurns > 0) {
        events.push({ type: 'MESSAGE', text: `${this.label(side)} is fast asleep.` });
        return;
      }
      user.status = null;
      user.sleepTurns = 0;
      events.push({ type: 'STATUS_CURED', side, status: null });
      events.push({ type: 'MESSAGE', text: `${this.label(side)} woke up!` });
    }
    if (user.status === 'FRZ') {
      if (!this.roll(20)) {
        events.push({ type: 'MESSAGE', text: `${this.label(side)} is frozen solid!` });
        return;
      }
      user.status = null;
      events.push({ type: 'STATUS_CURED', side, status: null });
      events.push({ type: 'MESSAGE', text: `${this.label(side)} thawed out!` });
    }
    if (vol.flinch) {
      events.push({ type: 'MESSAGE', text: `${this.label(side)} flinched and couldn't move!` });
      return;
    }
    if (user.status === 'PAR' && this.roll(25)) {
      events.push({ type: 'MESSAGE', text: `${this.label(side)} is paralyzed! It can't move!` });
      return;
    }

    if (slot >= 0) {
      user.moves[slot].pp = Math.max(0, user.moves[slot].pp - 1);
    } else {
      events.push({ type: 'MESSAGE', text: `${this.label(side)} has no moves left!` });
    }
    events.push({ type: 'MOVE_USED', side, moveId: move.id, text: `${this.label(side)} used ${move.name}!` });

    const effect = move.effect || null;
    const targetsFoe = move.category !== 'STATUS' || (effect && (effect.kind === 'status' || (effect.kind === 'stat' && effect.target === 'foe')));

    if (targetsFoe && move.accuracy > 0) {
      const accStage = vol.stages.acc - this.sides[foeSide].vol.stages.eva;
      const hitChance = move.accuracy * accuracyStageMultiplier(Math.max(-6, Math.min(6, accStage)));
      if (!this.roll(hitChance)) {
        events.push({ type: 'MISS', side, text: `${this.label(side)}'s attack missed!` });
        return;
      }
    }

    if (move.category === 'STATUS') {
      this.applyStatusMove(side, move, events);
      return;
    }

    const foeTypes = getSpecies(foe.speciesId).types;
    // Struggle is typeless so a battle can never deadlock
    const eff = move.id === STRUGGLE_MOVE.id ? 1 : typeEffectiveness(move.type, foeTypes);
    if (eff === 0) {
      events.push({ type: 'MESSAGE', text: `It doesn't affect ${this.label(foeSide)}...` });
      return;
    }

    let hits = 1;
    if (effect && effect.kind === 'multi') {
      hits = effect.min + Math.floor(this.rng() * (effect.max - effect.min + 1));
    }
    let total = 0;
    let anyCrit = false;
    let landed = 0;
    for (let h = 0; h < hits && foe.hp > 0; h += 1) {
      let damage;
      let crit = false;
      if (effect && effect.kind === 'fixed') {
        damage = effect.damage === 'level' ? user.level : Number(effect.damage);
      } else {
        const critChance = effect && effect.kind === 'highCrit' ? 12.5 : 6.25;
        crit = this.roll(critChance);
        const stab = move.id !== STRUGGLE_MOVE.id && hasType(user, move.type) ? 1.5 : 1;
        const random = 0.85 + this.rng() * 0.15;
        damage = Math.floor(this.baseDamage(side, move, crit) * stab * eff * (crit ? 1.5 : 1) * random);
        damage = Math.max(1, damage);
      }
      damage = Math.min(damage, foe.hp);
      foe.hp -= damage;
      total += damage;
      anyCrit = anyCrit || crit;
      landed += 1;
      events.push({ type: 'DAMAGE', side: foeSide, amount: damage, hp: foe.hp, maxHp: getMaxHp(foe), effectiveness: eff, crit });
      if (crit) {
        events.push({ type: 'MESSAGE', text: 'A critical hit!' });
      }
    }
    // fire melts ice
    if (move.type === 'FIRE' && foe.status === 'FRZ' && foe.hp > 0) {
      foe.status = null;
      events.push({ type: 'STATUS_CURED', side: foeSide, status: null });
      events.push({ type: 'MESSAGE', text: `${this.label(foeSide)} thawed out!` });
    }
    if (hits > 1) {
      events.push({ type: 'MESSAGE', text: `Hit ${landed} time(s)!` });
    }
    if (!(effect && effect.kind === 'fixed')) {
      if (eff > 1) {
        events.push({ type: 'MESSAGE', text: "It's super effective!" });
      } else if (eff < 1) {
        events.push({ type: 'MESSAGE', text: "It's not very effective..." });
      }
    }

    if (effect) {
      if (effect.kind === 'drain' && total > 0) {
        this.healSide(side, Math.max(1, Math.floor(total * effect.ratio)), events, `${this.label(foeSide)} had its energy drained!`);
      }
      if (effect.kind === 'recoil' && total > 0) {
        const recoil = Math.max(1, Math.floor(total * effect.ratio));
        user.hp = Math.max(0, user.hp - recoil);
        events.push({ type: 'DAMAGE', side, amount: recoil, hp: user.hp, maxHp: getMaxHp(user), effectiveness: 1, crit: false });
        events.push({ type: 'MESSAGE', text: `${this.label(side)} is hit with recoil!` });
      }
    }

    if (foe.hp <= 0) {
      this.faint(foeSide, events);
    } else if (effect) {
      if (effect.kind === 'status' && this.roll(effect.chance)) {
        this.inflictStatus(foeSide, effect.status, events, false);
      }
      if (effect.kind === 'stat' && this.roll(effect.chance)) {
        this.changeStages(effect.target === 'self' ? side : foeSide, effect.stats, events, false);
      }
      if (effect.kind === 'flinch' && movedFirst && this.roll(effect.chance)) {
        this.sides[foeSide].vol.flinch = true;
      }
    }
    if (user.hp <= 0) {
      this.faint(side, events);
    }
  }

  /**
   * Damage before STAB, type, crit and random factors.
   * @param {Side} side
   * @param {import('./monster.js').MoveData} move
   * @param {boolean} crit
   */
  baseDamage(side, move, crit) {
    const user = this.active(side);
    const foeSide = this.other(side);
    const physical = move.category === 'PHYSICAL';
    const atkKey = physical ? 'atk' : 'spc';
    const defKey = physical ? 'def' : 'spc';
    let atkStage = this.sides[side].vol.stages[atkKey];
    let defStage = this.sides[foeSide].vol.stages[defKey];
    if (crit) {
      atkStage = Math.max(0, atkStage);
      defStage = Math.min(0, defStage);
    }
    let attack = getStats(user)[atkKey] * stageMultiplier(atkStage);
    const defense = Math.max(1, getStats(this.active(foeSide))[defKey] * stageMultiplier(defStage));
    if (physical && user.status === 'BRN') {
      attack *= 0.5;
    }
    const levelFactor = Math.floor((2 * user.level) / 5) + 2;
    return Math.floor(Math.floor((levelFactor * move.power * attack) / defense) / 50) + 2;
  }

  /**
   * @param {Side} side
   * @param {import('./monster.js').MoveData} move
   * @param {BattleEvent[]} events
   */
  applyStatusMove(side, move, events) {
    const effect = move.effect;
    const user = this.active(side);
    const foeSide = this.other(side);
    if (!effect) {
      events.push({ type: 'MESSAGE', text: 'But nothing happened!' });
      return;
    }
    switch (effect.kind) {
      case 'status':
        this.inflictStatus(foeSide, effect.status, events, true);
        return;
      case 'stat':
        this.changeStages(effect.target === 'self' ? side : foeSide, effect.stats, events, true);
        return;
      case 'heal': {
        const max = getMaxHp(user);
        if (user.hp >= max) {
          events.push({ type: 'MESSAGE', text: `${this.label(side)}'s HP is already full!` });
          return;
        }
        this.healSide(side, Math.floor(max * effect.ratio), events, `${this.label(side)} restored its HP.`);
        return;
      }
      case 'rest': {
        const max = getMaxHp(user);
        if (user.hp >= max) {
          events.push({ type: 'MESSAGE', text: 'But it failed!' });
          return;
        }
        user.status = 'SLP';
        user.sleepTurns = 3;
        events.push({ type: 'STATUS', side, status: 'SLP' });
        this.healSide(side, max, events, `${this.label(side)} took a long siesta and recovered!`);
        return;
      }
      case 'cure':
        user.status = null;
        events.push({ type: 'STATUS_CURED', side, status: null });
        events.push({ type: 'MESSAGE', text: `${this.label(side)} feels refreshed!` });
        return;
      default:
        events.push({ type: 'MESSAGE', text: 'But nothing happened!' });
    }
  }

  /**
   * @param {Side} side
   * @param {number} amount
   * @param {BattleEvent[]} events
   * @param {string} text
   */
  healSide(side, amount, events, text) {
    const mon = this.active(side);
    const max = getMaxHp(mon);
    const before = mon.hp;
    mon.hp = Math.min(max, mon.hp + amount);
    events.push({ type: 'HEAL', side, amount: mon.hp - before, hp: mon.hp, maxHp: max });
    events.push({ type: 'MESSAGE', text });
  }

  /**
   * @param {Side} side
   * @param {import('./monster.js').StatusCondition} status
   * @param {BattleEvent[]} events
   * @param {boolean} announceFailure
   */
  inflictStatus(side, status, events, announceFailure) {
    const mon = this.active(side);
    if (mon.status || statusImmune(mon, status) || mon.hp <= 0) {
      if (announceFailure) {
        events.push({ type: 'MESSAGE', text: 'But it failed!' });
      }
      return;
    }
    mon.status = status;
    if (status === 'SLP') {
      mon.sleepTurns = 2 + Math.floor(this.rng() * 3);
    }
    events.push({ type: 'STATUS', side, status });
    events.push({ type: 'MESSAGE', text: `${this.label(side)} ${STATUS_TEXT[status]}!` });
  }

  /**
   * @param {Side} side
   * @param {Object.<string, number>} stats keys are upper-case stat names (ATK, DEF, ...)
   * @param {BattleEvent[]} events
   * @param {boolean} announceLimit
   */
  changeStages(side, stats, events, announceLimit) {
    const stages = this.sides[side].vol.stages;
    Object.entries(stats).forEach(([key, delta]) => {
      const k = /** @type {'atk'|'def'|'spc'|'spd'|'acc'|'eva'} */ (key.toLowerCase());
      const next = Math.max(-6, Math.min(6, stages[k] + delta));
      if (next === stages[k]) {
        if (announceLimit) {
          events.push({ type: 'MESSAGE', text: `${this.label(side)}'s ${STAT_NAMES[k]} won't go ${delta > 0 ? 'higher' : 'lower'}!` });
        }
        return;
      }
      const applied = next - stages[k];
      stages[k] = next;
      const size = Math.abs(applied) >= 2 ? (applied > 0 ? 'sharply rose' : 'harshly fell') : applied > 0 ? 'rose' : 'fell';
      events.push({ type: 'STAT_CHANGE', side, amount: applied, text: `${this.label(side)}'s ${STAT_NAMES[k]} ${size}!` });
    });
  }

  /**
   * @param {Side} side
   * @param {BattleEvent[]} events
   */
  faint(side, events) {
    const mon = this.active(side);
    if (events.some((e) => e.type === 'FAINT' && e.side === side && e.partyIndex === this.sides[side].active)) {
      return;
    }
    mon.hp = 0;
    mon.status = null;
    mon.sleepTurns = 0;
    events.push({ type: 'FAINT', side, partyIndex: this.sides[side].active, text: `${this.label(side)} fainted!` });
  }

  /** @param {BattleEvent[]} events */
  endOfTurn(events) {
    /** @type {Side[]} */
    const order = ['player', 'enemy'];
    order.forEach((side) => {
      const mon = this.active(side);
      this.sides[side].vol.flinch = false;
      if (mon.hp <= 0 || (mon.status !== 'BRN' && mon.status !== 'PSN')) {
        return;
      }
      if (this.active(this.other(side)).hp <= 0 && !this.hasUsableMonsters(this.other(side))) {
        return;
      }
      const max = getMaxHp(mon);
      const dmg = Math.max(1, Math.floor(max / (mon.status === 'BRN' ? 16 : 8)));
      mon.hp = Math.max(0, mon.hp - dmg);
      events.push({ type: 'DAMAGE', side, amount: dmg, hp: mon.hp, maxHp: max, effectiveness: 1, crit: false });
      events.push({ type: 'MESSAGE', text: `${this.label(side)} is hurt by its ${mon.status === 'BRN' ? 'burn' : 'poison'}!` });
      if (mon.hp <= 0) {
        this.faint(side, events);
      }
    });
  }

  /**
   * @param {Side} side
   * @param {number} index
   * @param {BattleEvent[]} events
   */
  switchIn(side, index, events) {
    const s = this.sides[side];
    if (side === 'player' && s.party[s.active].hp > 0) {
      events.push({ type: 'MESSAGE', text: `Come back, ${displayName(s.party[s.active])}!` });
    }
    s.active = index;
    s.vol = freshVolatile();
    if (side === 'player') {
      this.participants.add(s.party[index].uid);
    } else {
      this.participants = new Set([this.playerActive.uid]);
    }
    events.push({
      type: 'SWITCH_IN',
      side,
      partyIndex: index,
      text: side === 'player' ? `Go, ${displayName(s.party[index])}!` : `Foe sent out ${displayName(s.party[index])}!`,
    });
  }

  /**
   * Called after the player's active monster fainted and they picked a replacement.
   * @param {number} index
   * @returns {BattleEvent[]}
   */
  replacePlayerMonster(index) {
    /** @type {BattleEvent[]} */
    const events = [];
    this.switchIn('player', index, events);
    return events;
  }

  /** @returns {number} index of the next healthy enemy monster, or -1 */
  nextEnemyIndex() {
    return this.sides.enemy.party.findIndex((m, i) => i !== this.sides.enemy.active && m.hp > 0);
  }

  /** @returns {BattleEvent[]} */
  sendNextEnemy() {
    /** @type {BattleEvent[]} */
    const events = [];
    const idx = this.nextEnemyIndex();
    if (idx >= 0) {
      this.switchIn('enemy', idx, events);
    }
    return events;
  }

  /**
   * @param {BattleEvent[]} events
   * @returns {boolean}
   */
  tryRun(events) {
    if (this.isTrainer) {
      events.push({ type: 'MESSAGE', text: "No! There's no running from a trainer battle!" });
      return false;
    }
    this.runAttempts += 1;
    const mine = this.effectiveStat('player', 'spd');
    const theirs = this.effectiveStat('enemy', 'spd');
    const odds = Math.floor((mine * 128) / Math.max(1, theirs)) + 30 * this.runAttempts;
    const success = mine >= theirs || this.rng() * 256 < odds;
    events.push({ type: 'RUN', success, text: success ? 'Got away safely!' : "Couldn't get away!" });
    return success;
  }

  /**
   * @param {{name: string, effect: {ball: number}}} item
   * @param {BattleEvent[]} events
   * @returns {boolean}
   */
  tryCatch(item, events) {
    const mon = this.enemyActive;
    const sp = getSpecies(mon.speciesId);
    events.push({ type: 'MESSAGE', text: `You threw a ${item.name}!` });
    const shakes = catchShakes(mon, sp.catchRate, item.effect.ball, this.rng);
    const success = shakes >= 4;
    const fails = ['Oh no! It broke free!', 'Aww! It appeared to be caught!', 'Argh! Almost had it!', 'Shoot! It was so close, too!'];
    events.push({
      type: 'CATCH',
      shakes: Math.min(3, shakes),
      success,
      text: success ? `Gotcha! ${sp.name} was caught!` : fails[Math.min(3, shakes)],
    });
    return success;
  }

  /**
   * Exp for every eligible player monster after the active enemy fainted.
   * Monsters that fought get full exp; the rest of the conscious party gets half.
   * @returns {{index: number, amount: number}[]}
   */
  expShares(baseAmount) {
    return this.sides.player.party
      .map((m, index) => ({ m, index }))
      .filter(({ m }) => m.hp > 0)
      .map(({ m, index }) => ({ index, amount: this.participants.has(m.uid) ? baseAmount : Math.max(1, Math.floor(baseAmount / 2)) }));
  }
}

/**
 * Number of successful shake checks (4 = caught).
 * @param {Monster} mon
 * @param {number} catchRate
 * @param {number} ball
 * @param {() => number} rng
 */
export function catchShakes(mon, catchRate, ball, rng = Math.random) {
  if (ball >= 255) {
    return 4;
  }
  const max = getMaxHp(mon);
  const statusBonus = mon.status === 'SLP' || mon.status === 'FRZ' ? 2 : mon.status ? 1.5 : 1;
  const a = Math.floor((((3 * max - 2 * mon.hp) * catchRate * ball) / (3 * max)) * statusBonus);
  if (a >= 255) {
    return 4;
  }
  const b = 1048560 / Math.sqrt(Math.sqrt(16711680 / Math.max(1, a)));
  let shakes = 0;
  while (shakes < 4 && rng() * 65536 < b) {
    shakes += 1;
  }
  return shakes;
}

/**
 * Applies a HEAL / STATUS / REVIVE / PP item to a monster (in or out of battle).
 * @param {Monster} mon
 * @param {{name: string, category: string, effect: any}} item
 * @returns {{ok: boolean, message: string}}
 */
export function applyItem(mon, item) {
  const name = displayName(mon);
  const max = getMaxHp(mon);
  const e = item.effect || {};
  switch (item.category) {
    case 'HEAL': {
      if (mon.hp <= 0) {
        return { ok: false, message: `${name} has fainted. It needs a revive.` };
      }
      // some food also cures status (e.cures, as for STATUS items)
      const cure = Boolean(e.cures && mon.status && (e.cures === 'all' || e.cures.includes(mon.status)));
      if (mon.hp >= max && !cure) {
        return { ok: false, message: `${name}'s HP is already full.` };
      }
      const before = mon.hp;
      mon.hp = e.hp === 'full' ? max : Math.min(max, mon.hp + e.hp);
      if (cure) {
        mon.status = null;
        mon.sleepTurns = 0;
      }
      const healed = mon.hp > before ? `${name} recovered ${mon.hp - before} HP` : '';
      return { ok: true, message: cure ? `${healed ? `${healed} and` : name} is feeling better!` : `${healed}.` };
    }
    case 'STATUS': {
      if (mon.hp <= 0 || !mon.status || (e.cures !== 'all' && !e.cures.includes(mon.status))) {
        return { ok: false, message: 'It had no effect.' };
      }
      mon.status = null;
      mon.sleepTurns = 0;
      return { ok: true, message: `${name} is feeling better!` };
    }
    case 'REVIVE': {
      if (mon.hp > 0) {
        return { ok: false, message: 'It had no effect.' };
      }
      mon.hp = Math.max(1, Math.floor(max * e.revive));
      return { ok: true, message: `${name} was revived!` };
    }
    case 'PP': {
      if (mon.moves.every((m) => m.pp >= getMove(m.id).pp)) {
        return { ok: false, message: 'It had no effect.' };
      }
      mon.moves.forEach((m) => {
        m.pp = Math.min(getMove(m.id).pp, m.pp + e.pp);
      });
      return { ok: true, message: `${name}'s PP was restored.` };
    }
    default:
      return { ok: false, message: "That can't be used now." };
  }
}
