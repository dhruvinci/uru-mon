// Takes the screenshots used in README.md. Usage: node test/readme-shots.mjs [out_dir]   (default docs/screenshots)
import { launch, open, press, sleep, waitScene } from './harness.mjs';

const out = process.argv[2] || new URL('../../docs/screenshots', import.meta.url).pathname;
const shot = async (page, name) => {
  await page.screenshot({ path: `${out}/${name}.jpg`, type: 'jpeg', quality: 88 });
  console.log(`${out}/${name}.jpg`);
};

/** Opens the title menu and moves the cursor to an entry. */
async function titleMenu(page, entry) {
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 900);
  await press(page, 'START');
  await sleep(page, 400);
  const items = await page.evaluate(() => window.__uruGame.scene.getScene('TITLE_SCENE').menuItems);
  for (let i = 0; i < items.indexOf(entry); i += 1) await press(page, 'DOWN');
  await sleep(page, 300);
}

/** Presses through battle messages until the action menu is up. */
async function toBattleMenu(page) {
  await waitScene(page, 'BATTLE_SCENE');
  for (let i = 0; i < 60; i += 1) {
    const s = await page.evaluate(() => {
      const b = window.__uruGame.scene.getScene('BATTLE_SCENE');
      return { menu: b.menuMode, waiting: b.messageBox?.isWaiting };
    });
    if (s.menu === 'main') break;
    if (s.waiting) await press(page, 'A');
    await sleep(page, 200);
  }
  await sleep(page, 1500); // HD art streams in
}

const { browser, page, errors } = await launch();
try {
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 1500);
  await shot(page, 'title');

  const worlds = [
    ['world_lalbagh', '?scene=test&map=lalbagh&time=day&weather=clear&gfx=HD-2D'],
    ['world_mg_road_night', '?scene=test&map=mg_road&time=night&weather=clear&gfx=HD-2D'],
    ['world_basavanagudi_rain', '?scene=test&map=basavanagudi&time=dusk&weather=rain&gfx=HD-2D'],
    ['world_cubbon_dusk', '?scene=test&map=cubbon_park&time=dusk&weather=clear&gfx=HD-2D'],
    ['world_darshini', '?scene=test&map=darshini&time=day&weather=clear&gfx=HD-2D'],
  ];
  for (const [name, q] of worlds) {
    await open(page, q);
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 2500);
    await shot(page, name);
  }

  await open(page, '?scene=test&battle=trainer&trainer=leader_hoovamma&party=5:16');
  await toBattleMenu(page);
  await shot(page, 'battle_leader');
  await open(page, '?scene=test&battle=wild&species=146&level=60&party=9:60');
  await toBattleMenu(page);
  await shot(page, 'battle_legendary');

  await open(page, '?scene=test&map=lab&x=6&y=6&flags=');
  await waitScene(page, 'WORLD_SCENE');
  await sleep(page, 900);
  await page.evaluate(() => { window.__uruGame.scene.getScene('WORLD_SCENE').runScript([{ starterChoice: true }]); });
  await waitScene(page, 'STARTER_SCENE');
  await sleep(page, 1500);
  await shot(page, 'starters');

  await titleMenu(page, 'URU-PUSTAKA');
  await press(page, 'A');
  await waitScene(page, 'PUSTAKA_SCENE');
  for (let i = 0; i < 5; i += 1) await press(page, 'DOWN', 30);
  await sleep(page, 1500);
  await shot(page, 'pustaka');

  await titleMenu(page, 'BENGALURU MAP');
  await press(page, 'A');
  await waitScene(page, 'REGION_MAP_SCENE');
  await press(page, 'DOWN');
  await sleep(page, 1500);
  await shot(page, 'region_map');

  await titleMenu(page, 'QUICK BATTLE');
  await press(page, 'A');
  await waitScene(page, 'QUICK_BATTLE_SCENE');
  await sleep(page, 2000);
  await shot(page, 'quick_battle');
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}

// phone, portrait: the game on top, the pad and large dialogue text below
const phone = await launch({ width: 390, height: 844, touch: true });
try {
  await open(phone.page, '?scene=test&map=basavanagudi&time=day&weather=clear&gfx=HD-2D');
  await waitScene(phone.page, 'WORLD_SCENE');
  await phone.page.tap('.rotate-skip'); // "Play upright anyway"
  await sleep(phone.page, 1500);
  await phone.page.evaluate(() => {
    const w = window.__uruGame.scene.getScene('WORLD_SCENE');
    w.runScript([{ say: ['Namaskara! Tap anywhere on the map to walk there, or tap someone to talk to them.'], speaker: 'Ajji' }]);
  });
  await sleep(phone.page, 1500);
  await phone.page.screenshot({ path: `${out}/mobile_portrait.jpg`, type: 'jpeg', quality: 88 });
  console.log(`${out}/mobile_portrait.jpg`);
} finally {
  console.log(phone.errors.length ? `ERRORS:\n${phone.errors.join('\n')}` : 'no errors');
  await phone.browser.close();
}
