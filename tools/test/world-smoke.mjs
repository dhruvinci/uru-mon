// Loads maps through the test scene, walks a little, screenshots, reports errors.
import { launch, open, press, sleep, waitScene, walk } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const maps = (process.argv[3] || 'basavanagudi').split(',');
const { browser, page, errors } = await launch();
try {
  for (const m of maps) {
    await open(page, `?scene=test&map=${m}`);
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 1200);
    await page.screenshot({ path: `${shots}/world_${m}.png` });
    await walk(page, 'DOWN', 2);
    await walk(page, 'RIGHT', 2);
    await sleep(page, 400);
    const pos = await page.evaluate(() => window.__uru.dataManager.state.player.position);
    console.log(m, 'ok, player at', pos.x / 64, pos.y / 64);
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
