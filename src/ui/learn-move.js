/**
 * The classic "wants to learn a move but already knows four" conversation, shared by battle and evolution.
 */
import { displayName, getMove, MAX_MOVES, teachMove } from '../battle/engine/monster.js';

/**
 * @typedef PromptContext
 * @type {object}
 * @property {(message: string) => Promise<void>} say
 * @property {(items: string[], opts?: {cancelable?: boolean, title?: string}) => Promise<number>} choose resolves the chosen index, or -1 if cancelled
 */

/**
 * @param {PromptContext} ctx
 * @param {import('../battle/engine/monster.js').Monster} mon
 * @param {number} moveId
 * @returns {Promise<boolean>} whether the move was learned
 */
export async function promptLearnMove(ctx, mon, moveId) {
  const name = displayName(mon);
  const move = getMove(moveId);
  if (mon.moves.some((m) => m.id === moveId)) {
    return false;
  }
  if (mon.moves.length < MAX_MOVES) {
    teachMove(mon, moveId, -1);
    await ctx.say(`${name} learned ${move.name}!`);
    return true;
  }
  for (;;) {
    await ctx.say(`${name} wants to learn ${move.name}.`);
    await ctx.say(`But ${name} already knows ${MAX_MOVES} moves. Forget one to make room for ${move.name}?`);
    const yes = await ctx.choose(['YES', 'NO'], { cancelable: true });
    if (yes === 0) {
      const options = mon.moves.map((m) => getMove(m.id).name);
      const slot = await ctx.choose(options, { cancelable: true, title: 'Forget which move?' });
      if (slot >= 0) {
        const old = getMove(mon.moves[slot].id).name;
        teachMove(mon, moveId, slot);
        await ctx.say(`1, 2 and... Poof! ${name} forgot ${old}.`);
        await ctx.say(`And... ${name} learned ${move.name}!`);
        return true;
      }
    }
    await ctx.say(`Stop trying to teach ${move.name}?`);
    const stop = await ctx.choose(['YES', 'NO'], { cancelable: false });
    if (stop === 0) {
      await ctx.say(`${name} did not learn ${move.name}.`);
      return false;
    }
  }
}
