import { launch, open, sleep, waitScene } from './harness.mjs';
const shots = process.argv[2];
for (const [w, h, tag] of [[390, 844, 'portrait'], [844, 390, 'landscape']]) {
  const { browser, page, errors } = await launch({ width: w, height: h, touch: true });
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 1200);
  await page.screenshot({ path: `${shots}/m_${tag}_title.png` });
  await open(page, '?scene=test&map=lalbagh&party=6:30');
  await waitScene(page, 'WORLD_SCENE');
  await sleep(page, 1500);
  await page.screenshot({ path: `${shots}/m_${tag}_world.png` });
  await open(page, '?scene=test&battle=trainer&trainer=leader_tanvi&party=6:60,3:60');
  await waitScene(page, 'BATTLE_SCENE');
  await sleep(page, 2500);
  await page.screenshot({ path: `${shots}/m_${tag}_battle.png` });
  console.log(tag, errors.length ? errors.join('\n') : 'no errors');
  await browser.close();
}
