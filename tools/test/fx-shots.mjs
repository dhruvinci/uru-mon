// Screenshots maps under different graphics settings, times of day and weather.
// Usage: node test/fx-shots.mjs <shots_dir> <map[:time[:weather[:gfx]]]> ...   e.g. lalbagh:night:clear:HD-2D
import { launch, open, sleep, waitScene } from './harness.mjs';

const [shots, ...specs] = process.argv.slice(2);
const { browser, page, errors } = await launch();
try {
  for (const spec of specs) {
    const [map, time = 'day', weather = 'clear', gfx = 'HD-2D'] = spec.split(':');
    await open(page, `?scene=test&map=${map}&party=6:30&time=${time}&weather=${weather}&gfx=${gfx}`);
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 2500);
    const file = `${shots}/fx_${map}_${time}_${weather}_${gfx}.png`;
    await page.screenshot({ path: file });
    console.log(file);
  }
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
