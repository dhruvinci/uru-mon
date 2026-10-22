// Plays the opening: title -> intro -> home -> lab -> starter -> rival battle. Screenshots each checkpoint.
import { launch, open, press, sleep, waitScene, walk, state, activeScenes } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const { browser, page, errors } = await launch();
let shot = 0;
const snap = async (name) => page.screenshot({ path: `${shots}/ng_${String(++shot).padStart(2, '0')}_${name}.png` });

/** Mash A until cond() is true or timeout. */
async function mashUntil(cond, ms = 30000, every = 140) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    if (await cond()) return true;
    await press(page, 'A', 50);
    await sleep(page, every);
  }
  return false;
}
const worldIdle = () => page.evaluate(() => {
  const w = window.__uruGame.scene.getScene('WORLD_SCENE');
  return w && window.__uruGame.scene.isActive('WORLD_SCENE') && !w.inputLocked && !w.player?.isMoving;
});
const area = () => page.evaluate(() => window.__uru.dataManager.state.player.location.area);
const tile = () => page.evaluate(() => { const p = window.__uru.dataManager.state.player.position; return [p.x / 64, p.y / 64]; });

try {
  await page.goto('http://127.0.0.1:8080/index.html');
  await page.evaluate(() => localStorage.clear());
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 1200);
  await snap('title');
  await press(page, 'START');
  await sleep(page, 400);
  await snap('title_menu');
  await press(page, 'A');
  await waitScene(page, 'INTRO_SCENE');
  await mashUntil(() => page.evaluate(() => Boolean(document.querySelector('input'))), 60000, 200);
  await snap('name_entry');
  await page.fill('input', 'Ravi');
  await page.click('button.ok');
  await mashUntil(() => page.evaluate(() => window.__uruGame.scene.isActive('WORLD_SCENE')), 60000, 200);
  await sleep(page, 800);
  await snap('bedroom');
  console.log('in world:', await area(), await tile());
  // bedroom -> stairs
  await walk(page, 'RIGHT', 4); await walk(page, 'UP', 2); await walk(page, 'RIGHT', 1);
  await sleep(page, 900);
  console.log('after stairs:', await area(), await tile());
  await snap('downstairs');
  await mashUntil(worldIdle, 15000);
  await walk(page, 'DOWN', 3); await walk(page, 'LEFT', 5); await walk(page, 'DOWN', 2);
  await sleep(page, 900);
  console.log('outside:', await area(), await tile());
  await snap('outside');
  // to the lab
  await walk(page, 'DOWN', 1); await walk(page, 'RIGHT', 9); await walk(page, 'DOWN', 10); await walk(page, 'LEFT', 4);
  await walk(page, 'UP', 3);
  await sleep(page, 900);
  console.log('lab?', await area(), await tile());
  await snap('lab_enter');
  // cutscene + starter + rival battle: mash A until back in an idle world with a starter
  const ok = await mashUntil(async () => {
    const st = await state(page);
    return st.flags.includes('RIVAL1_DONE') && (await worldIdle());
  }, 240000, 160);
  await snap('after_lab');
  const st = await state(page);
  console.log('lab done:', ok, 'party', st.monsters.inParty.map((m) => `${m.speciesId}@${m.level}`), 'flags', st.flags, 'inv', JSON.stringify(st.inventory));
  console.log('scenes', await activeScenes(page));
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
