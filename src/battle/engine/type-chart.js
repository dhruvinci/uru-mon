/** @typedef {'NORMAL'|'FIRE'|'WATER'|'GRASS'|'ELECTRIC'|'EARTH'|'ROCK'|'SKY'|'BUG'|'TOXIC'|'FIGHT'|'MIND'|'SPIRIT'|'METAL'} UruType */

export const TYPES = Object.freeze([
  'NORMAL',
  'FIRE',
  'WATER',
  'GRASS',
  'ELECTRIC',
  'EARTH',
  'ROCK',
  'SKY',
  'BUG',
  'TOXIC',
  'FIGHT',
  'MIND',
  'SPIRIT',
  'METAL',
]);

/** Display colours for type badges. */
export const TYPE_COLORS = Object.freeze({
  NORMAL: 0xa8a77a,
  FIRE: 0xee8130,
  WATER: 0x6390f0,
  GRASS: 0x7ac74c,
  ELECTRIC: 0xf7d02c,
  EARTH: 0xe2bf65,
  ROCK: 0xb6a136,
  SKY: 0xa98ff3,
  BUG: 0xa6b91a,
  TOXIC: 0xa33ea1,
  FIGHT: 0xc22e28,
  MIND: 0xf95587,
  SPIRIT: 0x735797,
  METAL: 0xb7b7ce,
});

/** attacker type -> { defender type: multiplier } (unlisted = 1) */
const CHART = {
  NORMAL: { ROCK: 0.5, METAL: 0.5, SPIRIT: 0 },
  FIRE: { GRASS: 2, BUG: 2, METAL: 2, FIRE: 0.5, WATER: 0.5, ROCK: 0.5 },
  WATER: { FIRE: 2, EARTH: 2, ROCK: 2, WATER: 0.5, GRASS: 0.5 },
  GRASS: { WATER: 2, EARTH: 2, ROCK: 2, FIRE: 0.5, GRASS: 0.5, TOXIC: 0.5, SKY: 0.5, BUG: 0.5, METAL: 0.5 },
  ELECTRIC: { WATER: 2, SKY: 2, ELECTRIC: 0.5, GRASS: 0.5, EARTH: 0 },
  EARTH: { FIRE: 2, ELECTRIC: 2, TOXIC: 2, ROCK: 2, METAL: 2, GRASS: 0.5, BUG: 0.5, SKY: 0 },
  ROCK: { FIRE: 2, SKY: 2, BUG: 2, FIGHT: 0.5, EARTH: 0.5, METAL: 0.5 },
  SKY: { GRASS: 2, FIGHT: 2, BUG: 2, ELECTRIC: 0.5, ROCK: 0.5, METAL: 0.5 },
  BUG: { GRASS: 2, MIND: 2, FIRE: 0.5, FIGHT: 0.5, SKY: 0.5, SPIRIT: 0.5, METAL: 0.5, TOXIC: 0.5 },
  TOXIC: { GRASS: 2, TOXIC: 0.5, EARTH: 0.5, ROCK: 0.5, SPIRIT: 0.5, METAL: 0 },
  FIGHT: { NORMAL: 2, ROCK: 2, METAL: 2, TOXIC: 0.5, SKY: 0.5, BUG: 0.5, MIND: 0.5, SPIRIT: 0 },
  MIND: { FIGHT: 2, TOXIC: 2, MIND: 0.5, METAL: 0.5 },
  SPIRIT: { MIND: 2, SPIRIT: 2, NORMAL: 0 },
  METAL: { ROCK: 2, FIRE: 0.5, WATER: 0.5, ELECTRIC: 0.5, METAL: 0.5 },
};

/**
 * @param {UruType} attackType
 * @param {UruType[]} defenderTypes
 * @returns {number}
 */
export function typeEffectiveness(attackType, defenderTypes) {
  const row = CHART[attackType] || {};
  return defenderTypes.reduce((mult, t) => mult * (row[t] ?? 1), 1);
}
