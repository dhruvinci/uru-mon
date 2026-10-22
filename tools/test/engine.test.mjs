// Unit + fuzz tests for the battle engine. Run: node --test tools/test/
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

import {
  setGameData,
  createMonster,
  getStats,
  getMaxHp,
  gainExp,
  expForLevel,
  pendingEvolution,
  evolve,
  allSpecies,
  getSpecies,
  fullyHeal,
} from '../../src/battle/engine/monster.js';
import { Battle, catchShakes, applyItem } from '../../src/battle/engine/battle-engine.js';
import { typeEffectiveness } from '../../src/battle/engine/type-chart.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const load = (f) => JSON.parse(readFileSync(path.join(root, 'assets/data', f), 'utf8'));
const species = load('species.json');
const moves = load('moves.json');
const items = load('items.json');
setGameData(species, moves);

function seeded(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

test('type chart basics', () => {
  assert.equal(typeEffectiveness('FIRE', ['GRASS']), 2);
  assert.equal(typeEffectiveness('WATER', ['FIRE', 'EARTH']), 4);
  assert.equal(typeEffectiveness('ELECTRIC', ['EARTH']), 0);
  assert.equal(typeEffectiveness('NORMAL', ['SPIRIT']), 0);
  assert.equal(typeEffectiveness('GRASS', ['FIRE', 'METAL']), 0.25);
});

test('stats and creation', () => {
  const rng = seeded(1);
  const m = createMonster(4, 5, { rng });
  const stats = getStats(m);
  assert.ok(stats.hp >= 19 && stats.hp <= 22, `hp ${stats.hp}`);
  assert.equal(m.hp, stats.hp);
  assert.ok(m.moves.length >= 1 && m.moves.length <= 4);
  const lvl50 = createMonster(6, 50, { rng });
  assert.ok(getMaxHp(lvl50) > 140);
  assert.equal(lvl50.moves.length, 4);
});

test('exp, level up, move learning and evolution', () => {
  const m = createMonster(4, 5, { rng: seeded(2) });
  const res = gainExp(m, expForLevel(16) - m.exp);
  assert.equal(m.level, 16);
  assert.ok(res.after.hp > res.before.hp);
  assert.equal(pendingEvolution(m), 5);
  evolve(m, 5);
  assert.equal(getSpecies(m.speciesId).name, 'Brewolf');
  assert.ok(m.hp <= getMaxHp(m));
  // learning when full
  const full = createMonster(1, 30, { rng: seeded(3) });
  assert.equal(full.moves.length, 4);
  const r2 = gainExp(full, expForLevel(32) - full.exp);
  assert.ok(r2.pendingMoves.length >= 1, 'should have a pending move at 32');
});

test('catch odds behave', () => {
  const rng = seeded(4);
  const weak = createMonster(10, 5, { rng });
  weak.hp = 1;
  let caught = 0;
  for (let i = 0; i < 1000; i += 1) {
    if (catchShakes(weak, 255, 1, rng) >= 4) caught += 1;
  }
  assert.ok(caught > 900, `common low-hp catch ${caught}`);
  const legend = createMonster(64, 50, { rng });
  let lc = 0;
  for (let i = 0; i < 1000; i += 1) {
    if (catchShakes(legend, 3, 1, rng) >= 4) lc += 1;
  }
  assert.ok(lc < 50, `legendary full hp catch ${lc}`);
  assert.equal(catchShakes(legend, 3, 255, rng), 4);
});

test('items', () => {
  const m = createMonster(7, 10, { rng: seeded(5) });
  const dosa = items.find((i) => i.name === 'Masala Dosa');
  assert.equal(applyItem(m, dosa).ok, false);
  m.hp = 1;
  assert.equal(applyItem(m, dosa).ok, true);
  m.hp = 0;
  assert.equal(applyItem(m, dosa).ok, false);
  const pak = items.find((i) => i.name === 'Mysore Pak');
  assert.equal(applyItem(m, pak).ok, true);
  assert.ok(m.hp > 0);
});

test('fuzz: thousands of random battles finish without errors', () => {
  const rng = seeded(42);
  const ids = allSpecies().map((s) => s.id);
  const pick = () => ids[Math.floor(rng() * ids.length)];
  let turnsTotal = 0;
  for (let b = 0; b < 2000; b += 1) {
    const lvl = 2 + Math.floor(rng() * 60);
    const playerParty = Array.from({ length: 1 + Math.floor(rng() * 6) }, () => createMonster(pick(), lvl, { rng }));
    const enemyParty = Array.from({ length: 1 + Math.floor(rng() * 6) }, () => createMonster(pick(), lvl, { rng }));
    const battle = new Battle({ playerParty, enemyParty, isTrainer: true, aiLevel: b % 3, rng });
    let turns = 0;
    while (battle.hasUsableMonsters('player') && battle.hasUsableMonsters('enemy') && turns < 500) {
      turns += 1;
      const mon = battle.playerActive;
      const slot = Math.floor(rng() * mon.moves.length);
      const { events } = battle.resolveTurn({ kind: 'MOVE', slot });
      for (const e of events) {
        assert.ok(e.type, 'event type');
        if (e.hp !== undefined) assert.ok(e.hp >= 0 && e.hp <= e.maxHp, `hp out of range ${JSON.stringify(e)}`);
      }
      if (battle.enemyActive.hp <= 0 && battle.nextEnemyIndex() >= 0) battle.sendNextEnemy();
      if (battle.playerActive.hp <= 0) {
        const next = battle.sides.player.party.findIndex((m) => m.hp > 0);
        if (next >= 0) battle.replacePlayerMonster(next);
      }
    }
    assert.ok(turns < 500, `battle ${b} did not finish (lvl ${lvl})`);
    turnsTotal += turns;
  }
  console.log(`avg turns per battle: ${(turnsTotal / 2000).toFixed(1)}`);
});

test('level 5 starter vs level 3 wild: reasonable damage', () => {
  const rng = seeded(7);
  const starter = createMonster(4, 5, { rng });
  const wild = createMonster(10, 3, { rng });
  fullyHeal(wild);
  const battle = new Battle({ playerParty: [starter], enemyParty: [wild], rng });
  const before = wild.hp;
  battle.resolveTurn({ kind: 'MOVE', slot: 0 }, { kind: 'MOVE', slot: 1 });
  const dealt = before - wild.hp;
  assert.ok(dealt >= 3 && dealt <= before, `dealt ${dealt} of ${before}`);
});
