// The title-screen extras and the starter showcase: Pustaka browse, Bengaluru map, admin profile, starter choice.
// Usage: node test/frontdoor.mjs <shots_dir> [pustaka|map|admin|starter|quick|fishing]   (default: all)
import { launch, open, press, sleep, waitScene, state } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const only = process.argv[3];
const { browser, page, errors } = await launch();
const snap = (n) => page.screenshot({ path: `${shots}/fd_${n}.png` });
const active = () => page.evaluate(() => window.__uruGame.scene.getScenes(true).map((s) => s.scene.key));
const want = (part) => !only || only === part;

/** Opens the title menu and moves the cursor to an entry. */
async function titleMenu(entry) {
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 800);
  await press(page, 'START');
  await sleep(page, 400);
  const items = await page.evaluate(() => window.__uruGame.scene.getScene('TITLE_SCENE').menuItems);
  const idx = items.indexOf(entry);
  if (idx < 0) throw new Error(`no ${entry} in ${items}`);
  for (let i = 0; i < idx; i += 1) await press(page, 'DOWN');
  await sleep(page, 200);
  return items;
}

try {
  if (want('pustaka')) {
    const items = await titleMenu('URU-PUSTAKA');
    console.log('title menu:', items.join(' | '));
    await press(page, 'A');
    await waitScene(page, 'PUSTAKA_SCENE');
    await sleep(page, 500);
    await snap('pustaka_1');
    for (let i = 0; i < 70; i += 1) await press(page, 'DOWN', 30);
    await sleep(page, 400);
    await snap('pustaka_71');
    await press(page, 'B');
    await sleep(page, 400);
    console.log('pustaka closed, scenes:', (await active()).join(','));
  }
  if (want('map')) {
    await titleMenu('BENGALURU MAP');
    await press(page, 'A');
    await waitScene(page, 'REGION_MAP_SCENE');
    await sleep(page, 1200);
    await snap('map_1');
    for (let i = 0; i < 2; i += 1) await press(page, 'DOWN');
    await sleep(page, 1200);
    await snap('map_3');
    await press(page, 'B');
    await sleep(page, 300);
  }
  if (want('starter')) {
    await open(page, '?scene=test&map=lab&x=6&y=6&flags=');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 900);
    // don't await: the script only finishes after the choice is made
    await page.evaluate(() => { window.__uruGame.scene.getScene('WORLD_SCENE').runScript([{ starterChoice: true }]); });
    await waitScene(page, 'STARTER_SCENE');
    await sleep(page, 900);
    await snap('starter_mid');
    await press(page, 'RIGHT');
    await sleep(page, 600);
    await snap('starter_right');
    await press(page, 'A');
    await sleep(page, 300);
    await press(page, 'A');
    await sleep(page, 1200);
    for (let i = 0; i < 6; i += 1) { await press(page, 'A'); await sleep(page, 200); }
    const st = await state(page);
    console.log('starter chosen:', st.monsters.inParty.map((m) => m.speciesId), 'rival', st.vars.rivalStarter);
  }
  if (want('admin')) {
    await titleMenu('ADMIN MODE');
    await press(page, 'A');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 1500);
    const st = await state(page);
    console.log('admin:', st.admin, 'party', st.monsters.inParty.map((m) => `${m.speciesId}@${m.level}`).join(','), 'boxes', st.monsters.boxes.length,
      'badges', st.player.badges.length, 'caught', st.pustaka.caught.length);
    const mainSave = await page.evaluate(() => localStorage.getItem('URU_MON_SAVE_V1') !== null);
    // START menu -> WARP -> pick Lalbagh
    await press(page, 'START');
    await sleep(page, 400);
    await snap('admin_menu');
    const opts = await page.evaluate(() => {
      const ui = window.__uruGame.scene.getScene('WORLD_SCENE').ui;
      return ui && ui.menu ? ui.menu.items : null;
    });
    console.log('start menu:', opts);
    for (let i = 0; i < 6; i += 1) await press(page, 'DOWN');
    await press(page, 'A');
    await sleep(page, 400);
    await snap('admin_warp_list');
    await press(page, 'DOWN'); await press(page, 'DOWN');
    await press(page, 'A');
    await sleep(page, 2000);
    const after = await state(page);
    const area = await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').area);
    console.log('warped to:', area, 'saved location', after.player.location.area);
    await snap('admin_warped');
    console.log('main save untouched by admin:', !mainSave || 'main save existed before');
  }
  if (want('quick')) {
    await titleMenu('QUICK BATTLE');
    await press(page, 'A');
    await waitScene(page, 'QUICK_BATTLE_SCENE');
    await sleep(page, 1500);
    await snap('quick_matchup');
    const teams = await page.evaluate(() => { const q = window.__uruGame.scene.getScene('QUICK_BATTLE_SCENE'); return { mine: q.mine, theirs: q.theirs, opp: q.opponent.name }; });
    console.log('quick battle teams:', JSON.stringify(teams));
    await press(page, 'A');
    await waitScene(page, 'BATTLE_SCENE');
    const levels = await page.evaluate(() => { const b = window.__uruGame.scene.getScene('BATTLE_SCENE'); return [b.battle.playerActive.level, b.battle.enemyActive.level]; });
    let stage = '';
    for (let i = 0; i < 700 && stage !== 'result'; i += 1) {
      await press(page, 'A', 40);
      await sleep(page, 120);
      stage = await page.evaluate(() => window.__uruGame.scene.getScene('QUICK_BATTLE_SCENE').stage);
    }
    await snap('quick_result');
    console.log('quick battle finished:', stage === 'result', 'levels', levels.join('/'));
    // back to the title: the real state comes back and nothing was saved
    await sleep(page, 800);
    await press(page, 'DOWN'); await press(page, 'DOWN'); await press(page, 'A');
    await waitScene(page, 'TITLE_SCENE');
    const after = await page.evaluate(() => ({ party: window.__uru.dataManager.party.length, saved: localStorage.getItem('URU_MON_SAVE_V1') }));
    console.log('state restored after quick battle:', after.party === 0, 'saved anything:', Boolean(after.saved));
  }
  if (want('fishing')) {
    await open(page, '?scene=test&map=lalbagh&party=6:30');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 900);
    // put the player on a shore tile facing water
    const spot = await page.evaluate(() => {
      const w = window.__uruGame.scene.getScene('WORLD_SCENE');
      const W = w.map.width;
      const blocked = (x, y) => w.collisionLayer.getTileAt(x, y)?.index > 0;
      for (const idx of w.water) {
        const x = idx % W; const y = Math.floor(idx / W);
        for (const [dx, dy, dir] of [[0, 1, 'UP'], [0, -1, 'DOWN'], [1, 0, 'LEFT'], [-1, 0, 'RIGHT']]) {
          if (!blocked(x + dx, y + dy) && !w.water.has((y + dy) * W + x + dx)) return { x: x + dx, y: y + dy, dir };
        }
      }
      return null;
    });
    console.log('shore spot:', spot);
    await page.evaluate((s) => {
      const w = window.__uruGame.scene.getScene('WORLD_SCENE');
      window.__uru.dataManager.addItem(window.__uru.gameData.items.find((i) => i.name === 'Gaala').id, 1);
      w.player.teleport(s.x * 64, s.y * 64);
      w.player.face(s.dir);
    }, spot);
    await sleep(page, 300);
    let battled = false;
    for (let i = 0; i < 6 && !battled; i += 1) {
      await press(page, 'A');
      for (let k = 0; k < 12; k += 1) {
        await sleep(page, 250);
        if (await page.evaluate(() => window.__uruGame.scene.isActive('BATTLE_SCENE'))) { battled = true; break; }
        await press(page, 'A', 40);
      }
    }
    await sleep(page, 1500);
    await snap('fishing_battle');
    const enemy = await page.evaluate(() => window.__uruGame.scene.getScene('BATTLE_SCENE')?.battle?.enemyActive?.speciesId);
    console.log('fishing battle:', battled, 'species', enemy);
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
