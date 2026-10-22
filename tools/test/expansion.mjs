// Story pieces added by the 150 expansion: the Gaala rod, fossil revival, post-game legendaries and the new areas' gates.
// Usage: node test/expansion.mjs <shots_dir> [gaala|fossil|legends|gates]   (default: all)
import { launch, open, press, sleep, waitScene, state, walkTo, enterWarp } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const only = process.argv[3];
const want = (p) => !only || only === p;
const { browser, page, errors } = await launch();
const go = async (q) => { await open(page, q); await waitScene(page, 'WORLD_SCENE'); await sleep(page, 1000); };
const battleSpecies = () => page.evaluate(() => {
  const b = window.__uruGame.scene.getScene('BATTLE_SCENE');
  return window.__uruGame.scene.isActive('BATTLE_SCENE') ? b.battle?.enemyActive?.speciesId : null;
});
/** Faces a tile next to the player and presses A until `cond` holds (or time runs out). */
async function talkUntil(dir, cond, ms = 20000) {
  await press(page, dir, 60);
  await sleep(page, 200);
  const end = Date.now() + ms;
  while (Date.now() < end) {
    await press(page, 'A', 50);
    await sleep(page, 180);
    if (await cond()) return true;
  }
  return false;
}
/** Walks to a reachable tile next to (x, y); returns the direction to face from it (or null). */
async function stepNextTo(x, y) {
  const spots = await page.evaluate(([tx, ty]) => {
    const w = window.__uruGame.scene.getScene('WORLD_SCENE');
    const free = (a, b) => !(w.collisionLayer.getTileAt(a, b)?.index > 0) && !w.water.has(b * w.map.width + a);
    return [[0, 1, 'UP'], [-1, 0, 'RIGHT'], [1, 0, 'LEFT'], [0, -1, 'DOWN']]
      .filter(([dx, dy]) => free(tx + dx, ty + dy)).map(([dx, dy, dir]) => ({ x: tx + dx, y: ty + dy, dir }));
  }, [x, y]);
  for (const spot of spots) {
    if (await walkTo(page, spot.x, spot.y)) return spot.dir;
  }
  return null;
}

try {
  if (want('gaala')) {
    await go('?scene=test&map=lalbagh&party=6:30');
    const ajja = await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').npcs.find((n) => n.data.id === 'gaala_ajja')?.tilePosition);
    const dir = await stepNextTo(ajja.x / 64, ajja.y / 64);
    console.log('to the fisherman:', Boolean(dir));
    const got = await talkUntil(dir, async () => (await state(page)).flags.includes('GOT_GAALA'));
    console.log('got the Gaala:', got);
  }
  if (want('fossil')) {
    await go('?scene=test&map=lab&party=6:30&flags=GOT_STARTER');
    await page.evaluate(() => {
      const id = window.__uru.gameData.items.find((i) => i.name === 'Old Moss Stone').id;
      window.__uru.dataManager.addItem(id, 1);
    });
    const machine = await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').uru.interactables.find((i) => JSON.stringify(i.script).includes('Old Moss Stone')));
    const dir = await stepNextTo(machine.x, machine.y);
    console.log('to the stone reader:', Boolean(dir));
    const ok = await talkUntil(dir, async () => {
      const st = await state(page);
      return [...st.monsters.inParty, ...st.monsters.boxes].some((m) => m.speciesId === 139);
    });
    console.log('fossil revived:', ok);
  }
  if (want('legends')) {
    // the Nandi summit only connects to the lower slope through the cave, so start up there
    const legends = [['hebbal', 148, 'interactable', ''], ['nandi_hills', 149, 'interactable', '&x=33&y=3'],
      ['vidhana_soudha', 146, 'trigger', ''], ['ramanagara', 147, 'interactable', '']];
    for (const [map, species, kind, at] of legends) {
      await go(`?scene=test&map=${map}${at}&party=6:70&flags=CHAMPION_DONE,NANDI_DONE,UDYANAGA_DONE`);
      const target = await page.evaluate(([sp, k]) => {
        const u = window.__uruGame.scene.getScene('WORLD_SCENE').uru;
        const list = k === 'trigger' ? u.triggers : u.interactables;
        return list.find((t) => JSON.stringify(t.script).includes(`"species":${sp}`));
      }, [species, kind]);
      let ok;
      if (kind === 'trigger') {
        await walkTo(page, target.x, target.y);
        ok = await talkUntil('UP', async () => (await battleSpecies()) === species, 15000);
      } else {
        const dir = await stepNextTo(target.x, target.y);
        ok = Boolean(dir) && await talkUntil(dir, async () => (await battleSpecies()) === species, 15000);
      }
      console.log(`legend ${species} at ${map}:`, ok);
    }
  }
  if (want('legends')) {
    // the bean ajji tells the old story once the four other legends have been met
    await go('?scene=test&map=basavanagudi&party=6:70&flags=CHAMPION_DONE,GANDA_DONE,BISILU_DONE,MUNGARU_DONE,CHALI_DONE');
    const ajji = await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').npcs.find((n) => n.data.id === 'benda_ajji')?.tilePosition);
    const dir = await stepNextTo(ajji.x / 64, ajji.y / 64);
    const ok = Boolean(dir) && await talkUntil(dir, async () => (await battleSpecies()) === 150, 30000);
    console.log('legend 150 at basavanagudi:', ok);
  }
  if (want('gates')) {
    await go('?scene=test&map=basavanagudi&party=6:30&flags=GOT_STARTER');
    console.log('into Bannerghatta after getting a starter:', await enterWarp(page, 'bannerghatta'));
    await go('?scene=test&map=basavanagudi&party=6:30&flags=GOT_STARTER');
    const blocked = !(await enterWarp(page, 'ramanagara'));
    console.log('Ramanagara blocked before the Council:', blocked);
    await go('?scene=test&map=basavanagudi&party=6:30&flags=GOT_STARTER,CHAMPION_DONE');
    console.log('into Ramanagara after becoming Champion:', await enterWarp(page, 'ramanagara'));
    console.log('on to Kokkare Bellur:', await enterWarp(page, 'kokkare_bellur'));
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
