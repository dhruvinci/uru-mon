// Walks into a route trainer's line of sight; the trainer should approach and battle.
import { launch, open, press, sleep, waitScene, walk, state } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const { browser, page, errors } = await launch();
try {
  await open(page, '?scene=test&map=route1&x=10&y=24&party=4:12');
  await waitScene(page, 'WORLD_SCENE');
  await sleep(page, 1000);
  await walk(page, 'RIGHT', 1);
  await sleep(page, 600);
  await page.screenshot({ path: `${shots}/ts_1_spotted.png` });
  let sawBattle = false;
  for (let i = 0; i < 300; i += 1) {
    const s = await page.evaluate(() => ({ battle: window.__uruGame.scene.isActive('BATTLE_SCENE'), world: window.__uruGame.scene.isActive('WORLD_SCENE') }));
    if (s.battle) sawBattle = true;
    if (sawBattle && !s.battle && s.world) break;
    if (i === 30) await page.screenshot({ path: `${shots}/ts_2_battle.png` });
    await press(page, 'A', 50);
    await sleep(page, 120);
  }
  await sleep(page, 800);
  const st = await state(page);
  console.log('sawBattle', sawBattle, 'defeated', st.defeatedNpcs, 'money', st.player.money);
  await page.screenshot({ path: `${shots}/ts_3_after.png` });
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
