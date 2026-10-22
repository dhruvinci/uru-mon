// Leader battle -> badge -> gate opens; Metro travel; blackout -> respawn.
import { launch, open, press, sleep, waitScene, state, mashUntilIdle, untilBattleMenu, walk } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const part = process.argv[3] || 'leader';
const { browser, page, errors } = await launch();
const snap = (n) => page.screenshot({ path: `${shots}/pr_${n}.png` });
try {
  if (part === 'leader') {
    await open(page, '?scene=test&map=glass_house&x=7&y=4&party=6:30');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 800);
    await press(page, 'UP'); await sleep(page, 200);
    await press(page, 'A');
    await sleep(page, 1500);
    await snap('1_leader_intro');
    let battles = 0;
    for (let i = 0; i < 600; i += 1) {
      const s = await page.evaluate(() => ({ b: window.__uruGame.scene.isActive('BATTLE_SCENE'), idle: (() => { const w = window.__uruGame.scene.getScene('WORLD_SCENE'); return window.__uruGame.scene.isActive('WORLD_SCENE') && !w.inputLocked; })() }));
      if (s.b) battles = 1;
      if (battles && s.idle) break;
      if (i === 60) await snap('2_leader_battle');
      await press(page, 'A', 50); await sleep(page, 140);
    }
    const st = await state(page);
    console.log('badges:', st.player.badges, 'defeated:', st.defeatedNpcs, 'money:', st.player.money);
    await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').warpTo({ area: 'lalbagh', warpId: 'glass_house' }));
    await sleep(page, 1500);
    const crowd = await page.evaluate(() => Boolean(window.__uruGame.scene.getScene('WORLD_SCENE').getNpc('crowd1')));
    console.log('lalbagh crowd still blocking:', crowd);
  }
  if (part === 'metro') {
    await open(page, '?scene=test&map=lalbagh&x=7&y=29');
    await waitScene(page, 'WORLD_SCENE');
    await page.evaluate(() => { const d = window.__uru.dataManager; d.addItem(15, 1); d.state.metroStations = ['lalbagh', 'mg_road', 'whitefield']; });
    await sleep(page, 800);
    await press(page, 'UP'); await sleep(page, 200); await press(page, 'A');
    for (let i = 0; i < 20; i += 1) {
      if (await page.evaluate(() => window.__uruGame.scene.isActive('METRO_SCENE'))) break;
      await press(page, 'A'); await sleep(page, 250);
    }
    await sleep(page, 500);
    await snap('3_metro');
    await press(page, 'DOWN'); await sleep(page, 200); await press(page, 'A');
    await sleep(page, 2000);
    const st = await state(page);
    console.log('after metro:', st.player.location.area, st.player.position.x / 64, st.player.position.y / 64);
    await snap('4_arrived');
  }
  if (part === 'blackout') {
    await open(page, '?scene=test&map=route1&x=12&y=30&party=13:2');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 800);
    await page.evaluate(() => {
      const u = window.__uru;
      u.dataManager.state.respawn = { area: 'player_house_1f', x: 192, y: 320, returnPoint: null };
      window.__uruGame.scene.getScene('WORLD_SCENE').startBattle({ wild: u.createMonster(25, 40), environment: 'grass' });
    });
    for (let i = 0; i < 300; i += 1) {
      const a = await page.evaluate(() => window.__uru.dataManager.state.player.location.area);
      const idle = await page.evaluate(() => { const w = window.__uruGame.scene.getScene('WORLD_SCENE'); return window.__uruGame.scene.isActive('WORLD_SCENE') && w.player && !w.inputLocked; });
      if (a === 'player_house_1f' && idle) break;
      await press(page, 'A', 50); await sleep(page, 150);
    }
    const st = await state(page);
    console.log('after blackout:', st.player.location.area, 'hp', st.monsters.inParty.map((m) => m.hp), 'money', st.player.money);
    await snap('5_after_blackout');
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
