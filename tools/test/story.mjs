// Runs individual story events in isolation and checks the flags they set.
import { launch, open, press, sleep, waitScene, state, walk, walkTo, enterWarp } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const part = process.argv[3];
const STRONG = '6:62,57:60,41:60,25:60,50:60,63:60';
const { browser, page, errors } = await launch();
const snap = (n) => page.screenshot({ path: `${shots}/st_${part}_${n}.png` });

async function playUntil(cond, ms = 240000) {
  const end = Date.now() + ms;
  let i = 0;
  while (Date.now() < end) {
    if (await cond()) return true;
    await page.evaluate(strongestMoveFirst).catch(() => {});
    await press(page, 'A', 50);
    await sleep(page, 130);
    i += 1;
    if (i === 40) await snap('mid');
  }
  return false;
}
// The driver only ever picks move 1, so keep the strongest move that still has PP there.
const strongestMoveFirst = () => {
  const { dataManager, gameData } = window.__uru;
  const power = (m) => (m.pp > 0 ? gameData.moves.find((x) => x.id === m.id)?.power || 0 : -1);
  dataManager.party.forEach((m) => m.moves.sort((a, b) => power(b) - power(a)));
};
const flags = async () => (await state(page)).flags;
const idle = () => page.evaluate(() => { const w = window.__uruGame.scene.getScene('WORLD_SCENE'); return window.__uruGame.scene.isActive('WORLD_SCENE') && w.player && !w.inputLocked && !w.player.isMoving; });
const go = async (q) => { await open(page, q); await waitScene(page, 'WORLD_SCENE'); await sleep(page, 900); };

try {
  if (part === 'cubbon') {
    await go(`?scene=test&map=cubbon_park&x=15&y=12&party=${STRONG}`);
    await walk(page, 'UP', 3);
    const ok = await playUntil(async () => (await state(page)).defeatedNpcs.includes('t_grunt1') && (await idle()));
    console.log('grunt1 beaten:', ok);
    await walk(page, 'RIGHT', 1); await walk(page, 'UP', 1);
    const ok2 = await playUntil(async () => (await flags()).includes('CUBBON_GRUNTS_DONE') && (await idle()), 120000);
    console.log('grunts done:', ok2, await flags());
  }
  if (part === 'rival2') {
    await go(`?scene=test&map=mg_road&warp=S0&party=${STRONG}&badges=GRASS`);
    await walk(page, 'UP', 1);
    const ok = await playUntil(async () => (await flags()).includes('RIVAL2_DONE') && (await idle()));
    console.log('rival2:', ok);
  }
  if (part === 'rival2lose') {
    // lose to Rohan with a weak team, then come back: the encounter must happen again
    await go(`?scene=test&map=mg_road&warp=S0&party=10:3&badges=GRASS`);
    await walk(page, 'UP', 1);
    const lost = await playUntil(async () => (await state(page)).player.location.area !== 'mg_road' && (await idle()));
    console.log('lost and blacked out:', lost, 'at', (await state(page)).player.location.area);
    await page.evaluate(() => window.__uru.dataManager.party.forEach((m) => window.__uru.fullyHeal(m)));
    await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').warpTo({ area: 'mg_road', warpId: 'S0' }));
    await sleep(page, 1500);
    await walk(page, 'UP', 1);
    const again = await playUntil(() => page.evaluate(() => window.__uruGame.scene.isActive('BATTLE_SCENE')), 30000);
    console.log('rematch started:', again, 'RIVAL2_DONE', (await flags()).includes('RIVAL2_DONE'));
  }
  if (part === 'rival3') {
    await go(`?scene=test&map=whitefield&warp=W0&party=${STRONG}`);
    const ok = await playUntil(async () => (await flags()).includes('RIVAL3_DONE') && (await idle()));
    console.log('rival3:', ok);
  }
  if (part === 'bellandur') {
    await go(`?scene=test&map=bellandur_site&x=6&y=4&party=${STRONG}`);
    await press(page, 'UP'); await sleep(page, 200); await press(page, 'A');
    const ok = await playUntil(async () => (await flags()).includes('BELLANDUR_ADMIN_DONE') && (await idle()));
    console.log('admin beaten:', ok);
    for (let i = 0; i < 6; i += 1) await walk(page, 'DOWN', 1);
    await sleep(page, 1200);
    console.log('area now', (await state(page)).player.location.area);
    const ok2 = await playUntil(async () => (await flags()).includes('BELLANDUR_DONE') && (await idle()), 90000);
    const st = await state(page);
    console.log('bellandur done:', ok2, 'metro card:', st.inventory.some((e) => e.itemId === 15));
  }
  if (part === 'rival4') {
    await go(`?scene=test&map=palace_road&x=19&y=14&party=${STRONG}&badges=GRASS,FIGHT,ELECTRIC,MIND,SPIRIT`);
    await walk(page, 'UP', 2);
    const ok = await playUntil(async () => (await flags()).includes('RIVAL4_DONE') && (await idle()), 480000);
    const dbg = await page.evaluate(() => ({ scenes: window.__uruGame.scene.getScenes(true).map((s) => s.scene.key), defeated: window.__uru.dataManager.state.defeatedNpcs, last: window.__uruGame.scene.getScene('WORLD_SCENE').lastBattleResult }));
    console.log('rival4:', ok, JSON.stringify(dbg));
    await snap('end');
  }
  if (part === 'nandi') {
    await go(`?scene=test&map=nandi_cave&x=14&y=5&party=${STRONG}`);
    // into Boss Bhaskar's line of sight (he stands at 8,2 looking down)
    await walkTo(page, 8, 4);
    const ok = await playUntil(async () => (await flags()).includes('NANDI_DONE') && (await idle()), 400000);
    console.log('boss beaten:', ok);
    console.log('out of the north exit:', await enterWarp(page, 'nandi_hills', 'north'));
    await sleep(page, 1500);
    let st = await state(page);
    console.log('area now', st.player.location.area, st.player.position.x / 64, st.player.position.y / 64);
    // the Udyanaga trigger covers x 27-33, y 2-5 at the summit
    await walkTo(page, 30, 4);
    const ok2 = await playUntil(async () => (await flags()).includes('UDYANAGA_DONE') && (await idle()), 240000);
    st = await state(page);
    console.log('udyanaga:', ok2, 'pos', st.player.position.x / 64, st.player.position.y / 64, 'flags', st.flags, 'caught', st.pustaka.caught.includes(64));
    await snap('end');
  }
  if (part === 'council') {
    const rooms = [['council_1', 'vs_nagaraj'], ['council_2', 'vs_basappa'], ['council_3', 'vs_kaveri'], ['council_4', 'vs_agni'], ['champion_room', 'vs_champion']];
    await go(`?scene=test&map=council_1&warp=door&party=${STRONG}&badges=GRASS,FIGHT,ELECTRIC,MIND,SPIRIT,SKY`);
    for (const [room, npcId] of rooms) {
      if (room !== 'council_1') {
        await page.evaluate((r) => window.__uruGame.scene.getScene('WORLD_SCENE').warpTo({ area: r, warpId: 'door' }), room);
        await sleep(page, 1500);
      }
      // heal up between chambers, like a player using items
      await page.evaluate(() => window.__uru.dataManager.party.forEach((m) => window.__uru.fullyHeal(m)));
      await page.evaluate(() => { const w = window.__uruGame.scene.getScene('WORLD_SCENE'); const n = w.npcs.find((x) => x.data.trainer); w.player.teleport(n.tilePosition.x, n.tilePosition.y + 64); w.player.face('UP'); });
      await sleep(page, 300);
      await press(page, 'A');
      const ok = await playUntil(async () => {
        await page.evaluate(strongestMoveFirst);
        const credits = await page.evaluate(() => window.__uruGame.scene.isActive('CREDITS_SCENE'));
        const s = await state(page);
        return credits || (s.defeatedNpcs.includes(npcId) && (await idle()));
      }, 400000);
      console.log(room, 'beaten:', ok);
    }
    await sleep(page, 3000);
    await snap('end');
    const st = await state(page);
    console.log('credits running:', await page.evaluate(() => window.__uruGame.scene.isActive('CREDITS_SCENE')), 'flags', st.flags, 'saved location', st.player.location.area);
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
