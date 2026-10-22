// Darshini healing, Kirana shopping and the START menu screens.
import { launch, open, press, sleep, waitScene, walk, state, activeScenes, mashUntilIdle } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const { browser, page, errors } = await launch();
const snap = (n) => page.screenshot({ path: `${shots}/sv_${n}.png` });
const area = async () => (await state(page)).player.location.area;
try {
  await open(page, '?scene=test&map=lalbagh&x=8&y=20');
  await waitScene(page, 'WORLD_SCENE');
  await sleep(page, 800);
  await page.evaluate(() => window.__uru.dataManager.party.forEach((m) => { m.hp = 1; m.status = 'PSN'; }));
  await walk(page, 'UP', 1);
  await sleep(page, 800);
  console.log('entered:', await area());
  await walk(page, 'UP', 3);
  await press(page, 'A');
  await sleep(page, 900);
  await snap('1_owner');
  console.log('idle after owner:', await mashUntilIdle(page));
  let st = await state(page);
  console.log('healed:', st.monsters.inParty.every((m) => m.status === null && m.hp > 1), 'respawn:', st.respawn.area, 'return:', JSON.stringify(st.respawn.returnPoint));
  await walk(page, 'DOWN', 4);
  await sleep(page, 900);
  console.log('back out:', await area(), (await state(page)).player.position);
  await walk(page, 'RIGHT', 5);
  await walk(page, 'UP', 1);
  await sleep(page, 900);
  console.log('entered:', await area());
  await walk(page, 'LEFT', 2);
  await walk(page, 'UP', 1);
  const before = await state(page);
  await press(page, 'A');
  await sleep(page, 600);
  for (let i = 0; i < 5; i += 1) { await press(page, 'A'); await sleep(page, 250); }
  await snap('2_shop');
  console.log('scenes in shop:', await activeScenes(page));
  for (let i = 0; i < 6; i += 1) { await press(page, 'A'); await sleep(page, 250); }
  await snap('3_bought');
  for (let i = 0; i < 6; i += 1) { await press(page, 'B'); await sleep(page, 250); }
  const after = await state(page);
  const dabbas = (s) => s.inventory.find((e) => e.itemId === 2)?.quantity ?? 0;
  console.log('money', before.player.money, '->', after.player.money, 'dabbas', dabbas(before), '->', dabbas(after));
  await sleep(page, 400);
  await press(page, 'START');
  await sleep(page, 500);
  await snap('4_start_menu');
  await press(page, 'DOWN'); await press(page, 'A');
  await sleep(page, 800);
  await snap('5_party');
  await press(page, 'A'); await sleep(page, 300); await press(page, 'A'); await sleep(page, 700);
  await snap('6_summary');
  await press(page, 'RIGHT'); await sleep(page, 300); await snap('7_summary_stats');
  await press(page, 'RIGHT'); await sleep(page, 300); await snap('8_summary_moves');
  await press(page, 'B'); await sleep(page, 400); await press(page, 'B'); await sleep(page, 600);
  await press(page, 'DOWN'); await press(page, 'A'); await sleep(page, 800);
  await snap('9_bag');
  await press(page, 'B'); await sleep(page, 500);
  await press(page, 'UP'); await press(page, 'UP'); await press(page, 'A'); await sleep(page, 800);
  await snap('10_pustaka');
  await press(page, 'B'); await sleep(page, 500);
  console.log('scenes at end:', await activeScenes(page));
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
