// Plays a wild battle by mashing FIGHT until it ends; reports errors and saves screenshots.
import { launch, open, press, sleep, waitScene } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const { browser, page, errors } = await launch();
try {
  await open(page, '?scene=test&battle=wild&species=10&level=4&party=4:9');
  await waitScene(page, 'BATTLE_SCENE');
  await sleep(page, 2500);
  await page.screenshot({ path: `${shots}/battle_1.png` });
  for (let i = 0; i < 120; i += 1) {
    const done = await page.evaluate(() => Boolean(window.__lastBattleResult));
    if (done) break;
    await press(page, 'A');
    await sleep(page, 150);
    if (i === 6) await page.screenshot({ path: `${shots}/battle_2.png` });
    if (i === 20) await page.screenshot({ path: `${shots}/battle_3.png` });
  }
  const result = await page.evaluate(() => window.__lastBattleResult);
  console.log('result:', JSON.stringify(result));
  await page.screenshot({ path: `${shots}/battle_end.png` });
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
