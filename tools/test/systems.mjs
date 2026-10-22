// Catching, evolution and blackout.
import { launch, open, press, sleep, waitScene, state, untilBattleMenu } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const part = process.argv[3] || 'catch';
const { browser, page, errors } = await launch();
const snap = (n) => page.screenshot({ path: `${shots}/sys_${n}.png` });
try {
  if (part === 'catch') {
  // --- catch a weak wild Gubbi with a Dabba via the real menus
  await open(page, '?scene=test&battle=wild&species=10&level=2&party=4:20');
  await waitScene(page, 'BATTLE_SCENE');
  console.log('menu:', await untilBattleMenu(page));
  await press(page, 'RIGHT'); await press(page, 'A');          // BAG
  await waitScene(page, 'INVENTORY_SCENE');
  await sleep(page, 400);
  await press(page, 'RIGHT');                                   // DABBAS pocket
  await sleep(page, 300);
  await snap('1_bag_dabbas');
  await press(page, 'A'); await sleep(page, 300); await press(page, 'A');   // select Dabba, USE
  for (let i = 0; i < 80; i += 1) {
    const r = await page.evaluate(() => window.__lastBattleResult);
    if (r) break;
    if (i === 6) await snap('2_throw');
    await press(page, 'A', 50); await sleep(page, 200);
  }
  const st = await state(page);
  console.log('catch result:', JSON.stringify(await page.evaluate(() => window.__lastBattleResult)), 'party:', st.monsters.inParty.map((m) => m.speciesId), 'caught:', st.pustaka.caught);

  }
  if (part === 'evolve') {
  // --- evolution: Kaapup L15 just short of 16, beat a wild
  await open(page, '?scene=test&battle=wild&species=24&level=10&party=4:15');
  await waitScene(page, 'BATTLE_SCENE');
  await page.evaluate(() => { const m = window.__uru.dataManager.party[0]; m.exp = 16 ** 3 - 5; });
  let evolved = false;
  if ((await untilBattleMenu(page)) === 'menu') {
    await press(page, 'A'); await sleep(page, 200);           // FIGHT
    await press(page, 'RIGHT'); await press(page, 'DOWN');    // slot 3 (Steam Jet)
    await press(page, 'A');
  }
  for (let i = 0; i < 400; i += 1) {
    const r = await page.evaluate(() => window.__lastBattleResult);
    if (r) break;
    const sp = await page.evaluate(() => window.__uru.dataManager.party[0].speciesId);
    if (sp === 5 && !evolved) { evolved = true; await snap('3_evolved'); }
    if (i === 40) await snap('3_evolving');
    await press(page, 'A', 50); await sleep(page, 160);
  }
  const st = await state(page);
  console.log('battle result', JSON.stringify(await page.evaluate(() => window.__lastBattleResult)), 'exp', st.monsters.inParty[0].exp);
  console.log('evolution: species now', st.monsters.inParty[0].speciesId, 'level', st.monsters.inParty[0].level, 'moves', st.monsters.inParty[0].moves.map((m) => m.id));
  }

} catch (e) {
  console.log('note:', e.message.split('\n')[0]);
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
