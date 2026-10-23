// Touch-only play on a phone-sized screen: tap to start, tap menus, tap to walk (through the HD-2D tilt), tap an NPC to
// talk, tap through a battle. Usage: node test/mobile.mjs <shots_dir> [portrait|landscape]
import { launch, open, sleep, waitScene, state } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const orient = process.argv[3] || 'landscape';
const [w, h] = orient === 'portrait' ? [390, 844] : [844, 390];
const { browser, page, errors } = await launch({ width: w, height: h, touch: true });

/** Game coordinates (1024x576) to a point on the page. */
async function toScreen(gx, gy) {
  const r = await page.evaluate(() => {
    const b = window.__uruGame.canvas.getBoundingClientRect();
    return { x: b.left, y: b.top, w: b.width, h: b.height };
  });
  return { x: r.x + (gx / 1024) * r.w, y: r.y + (gy / 576) * r.h };
}
const tapGame = async (gx, gy) => {
  const p = await toScreen(gx, gy);
  await page.touchscreen.tap(p.x, p.y);
  await sleep(page, 120);
};
/** Finds a spot on screen that the world maps to the given tile, by sampling. */
const screenForTile = (tx, ty) => page.evaluate(([x, y]) => {
  const wsc = window.__uruGame.scene.getScene('WORLD_SCENE');
  for (let gy = 20; gy < 560; gy += 8) {
    for (let gx = 20; gx < 1004; gx += 8) {
      const t = wsc.screenToTile(gx, gy);
      if (t.x === x && t.y === y) return { gx: gx + 4, gy: gy + 4 };
    }
  }
  return null;
}, [tx, ty]);
const playerTile = () => page.evaluate(() => {
  const p = window.__uruGame.scene.getScene('WORLD_SCENE').player.tilePosition;
  return { x: p.x / 64, y: p.y / 64 };
});

try {
  // title: tap to open the menu, tap QUICK BATTLE, then BACK
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 900);
  if (orient === 'portrait') {
    // phones held upright are asked to turn sideways first
    const asked = await page.isVisible('.rotate-overlay');
    await page.tap('.rotate-skip');
    await sleep(page, 200);
    console.log('portrait asks to turn sideways:', asked, '| dismissed:', !(await page.isVisible('.rotate-overlay')));
  }
  await tapGame(512, 300);
  await sleep(page, 400);
  const menu = await page.evaluate(() => {
    const t = window.__uruGame.scene.getScene('TITLE_SCENE');
    return t.menu ? { x: t.menu.container.x, y: t.menu.container.y, rh: t.menu.cfg.rowHeight, items: t.menuItems } : null;
  });
  console.log('title menu opened by a tap:', Boolean(menu));
  const qi = menu.items.indexOf('QUICK BATTLE');
  await tapGame(menu.x + 120, menu.y + 18 + qi * menu.rh + menu.rh / 2 - 4);
  await waitScene(page, 'QUICK_BATTLE_SCENE', 5000).catch(() => {});
  console.log('tapped into Quick Battle:', await page.evaluate(() => window.__uruGame.scene.isActive('QUICK_BATTLE_SCENE')));

  // world: tap to walk through the tilted HD-2D camera
  await open(page, '?scene=test&map=lalbagh&party=6:30&gfx=HD-2D&time=day&weather=clear');
  await waitScene(page, 'WORLD_SCENE');
  await sleep(page, 1200);
  const start = await playerTile();
  const target = await page.evaluate(([sx, sy]) => {
    const wsc = window.__uruGame.scene.getScene('WORLD_SCENE');
    const free = (x, y) => !(wsc.collisionLayer.getTileAt(x, y)?.index > 0) && !wsc.npcs.some((n) => n.tilePosition.x === x * 64 && n.tilePosition.y === y * 64);
    for (const [dx, dy] of [[3, 2], [-3, 2], [2, 3], [-2, 3], [4, 0], [-4, 0], [0, 3], [3, -1]]) {
      if (free(sx + dx, sy + dy)) return { x: sx + dx, y: sy + dy };
    }
    return null;
  }, [start.x, start.y]);
  const spot = await screenForTile(target.x, target.y);
  await tapGame(spot.gx, spot.gy);
  let at = start;
  for (let i = 0; i < 40 && (at.x !== target.x || at.y !== target.y); i += 1) {
    await sleep(page, 150);
    at = await playerTile();
  }
  console.log('tap-to-walk reached the tapped tile:', at.x === target.x && at.y === target.y, JSON.stringify(start), '->', JSON.stringify(at));
  await page.screenshot({ path: `${shots}/mob_${orient}_walk.png` });

  // tap an NPC: walk up and talk
  const npc = await page.evaluate(() => {
    const wsc = window.__uruGame.scene.getScene('WORLD_SCENE');
    const p = wsc.player.tilePosition;
    const list = wsc.npcs.filter((n) => n.sprite.visible && !n.data.trainer)
      .map((n) => ({ x: n.tilePosition.x / 64, y: n.tilePosition.y / 64, d: Math.abs(n.tilePosition.x - p.x) + Math.abs(n.tilePosition.y - p.y) }))
      .sort((a, b) => a.d - b.d);
    return list[0];
  });
  const npcSpot = await screenForTile(npc.x, npc.y);
  if (npcSpot) await tapGame(npcSpot.gx, npcSpot.gy);
  let talking = false;
  for (let i = 0; i < 60 && !talking; i += 1) {
    await sleep(page, 150);
    talking = await page.evaluate(() => window.__uruGame.scene.getScene('DIALOG_SCENE').busy);
  }
  const mirror = await page.evaluate(() => document.querySelector('.msg-mirror')?.textContent || '');
  console.log('tapping an NPC started a conversation:', talking, '| mirrored text:', JSON.stringify(mirror.slice(0, 50)));
  await page.screenshot({ path: `${shots}/mob_${orient}_talk.png` });
  for (let i = 0; i < 30 && talking; i += 1) {
    await tapGame(512, 500);
    await sleep(page, 250);
    talking = await page.evaluate(() => window.__uruGame.scene.getScene('DIALOG_SCENE').busy);
  }
  console.log('tapping closed the conversation:', !talking);

  // battle: tap messages, tap FIGHT, tap the first move
  await open(page, '?scene=test&battle=wild&species=13&level=5&party=6:40');
  await waitScene(page, 'BATTLE_SCENE');
  let hpBefore = null;
  let attacked = false;
  for (let i = 0; i < 80 && !attacked; i += 1) {
    const s = await page.evaluate(() => {
      const b = window.__uruGame.scene.getScene('BATTLE_SCENE');
      if (!b || !window.__uruGame.scene.isActive('BATTLE_SCENE')) return { over: true };
      return { waiting: b.messageBox.isWaiting, handler: Boolean(b.inputHandler), hp: b.battle.enemyActive.hp };
    });
    if (s.over) { attacked = true; break; }
    if (hpBefore === null) hpBefore = s.hp;
    if (s.hp < hpBefore) { attacked = true; break; }
    if (s.waiting) await tapGame(300, 500);
    else if (s.handler) { await tapGame(660, 462); await sleep(page, 300); await tapGame(140, 462); }
    await sleep(page, 250);
  }
  console.log('fought with taps only:', attacked);
  await page.screenshot({ path: `${shots}/mob_${orient}_battle.png` });
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
