// Touch-only play on a phone-sized screen: tap to start, tap menus, tap to walk (through the HD-2D tilt), tap an NPC to
// talk, tap through a battle. Usage: node test/mobile.mjs <shots_dir> [portrait|landscape|iphone|turn]
//   portrait: held upright, where the game grows to a square and the overworld, dialog and battles draw big
//   iphone: sideways with an iPhone's notch margins and Safari's bars; the buttons must clear the game and the notch
//   turn: turns the phone mid-conversation and mid-battle
import { launch, open, sleep, waitScene, press } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const orient = process.argv[3] || 'landscape';
const SIZES = {
  portrait: { width: 390, height: 844 },
  landscape: { width: 844, height: 390 },
  iphone: { width: 874, height: 296, insets: { l: 62, r: 62, b: 21 } }, // iPhone 17, Safari with its tab bar
  turn: { width: 402, height: 874, insets: { t: 62, b: 34 } },
};
const { browser, page, errors } = await launch({ ...SIZES[orient], touch: true });

/** Game coordinates (1024 wide, 576 or more tall) to a point on the page. */
async function toScreen(gx, gy) {
  const r = await page.evaluate(() => {
    const b = window.__uruGame.canvas.getBoundingClientRect();
    return { x: b.left, y: b.top, w: b.width, h: b.height, gw: window.__uruGame.scale.width, gh: window.__uruGame.scale.height };
  });
  return { x: r.x + (gx / r.gw) * r.w, y: r.y + (gy / r.gh) * r.h };
}
const tapGame = async (gx, gy) => {
  const p = await toScreen(gx, gy);
  await page.touchscreen.tap(p.x, p.y);
  await sleep(page, 120);
};
/** Finds a spot on screen that the world maps to the given tile, by sampling. */
const screenForTile = (tx, ty) => page.evaluate(([x, y]) => {
  const wsc = window.__uruGame.scene.getScene('WORLD_SCENE');
  for (let gy = 20; gy < wsc.scale.height - 16; gy += 8) {
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
const gameSize = () => page.evaluate(() => [window.__uruGame.scale.width, window.__uruGame.scale.height]);
/** The page rectangles of the canvas and the pad's buttons. */
const rects = () => page.evaluate(() => {
  const r = (el) => { const b = el.getBoundingClientRect(); return { l: b.left, t: b.top, r: b.right, b: b.bottom }; };
  return {
    canvas: r(window.__uruGame.canvas),
    buttons: [...document.querySelectorAll('.touch-pad button')].filter((b) => b.offsetParent).map((b) => ({ name: b.textContent || b.dataset.btn, ...r(b) })),
  };
});
const overlaps = (a, b) => a.l < b.r - 1 && b.l < a.r - 1 && a.t < b.b - 1 && b.t < a.b - 1;

if (orient === 'iphone') {
  try {
    await open(page, '?scene=test&map=basavanagudi&party=6:30&time=day&weather=clear');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 1200);
    const { canvas, buttons } = await rects();
    const clash = buttons.filter((b) => overlaps(b, canvas)).map((b) => b.name);
    const notch = buttons.filter((b) => b.l < 62 || b.r > 874 - 62).map((b) => b.name);
    console.log('game fills the height:', Math.round(canvas.b - canvas.t) >= 290, JSON.stringify(canvas));
    console.log('no button covers the game:', clash.length === 0, clash.join(' '));
    console.log('no button under the notch or the rounded corners:', notch.length === 0, notch.join(' '));
    await page.screenshot({ path: `${shots}/mob_iphone.png` });
  } finally {
    console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
    await browser.close();
  }
  process.exit(0);
}

if (orient === 'turn') {
  try {
    const dialog = () => page.evaluate(() => {
      const d = window.__uruGame.scene.getScene('DIALOG_SCENE');
      const box = d.box.container;
      return { k: d.k, top: box.y, bottom: box.y + d.box.height * box.scaleY, visible: box.visible };
    });
    await open(page, '?scene=test&map=basavanagudi&party=6:30&time=day&weather=clear');
    await waitScene(page, 'WORLD_SCENE');
    await sleep(page, 1200);
    await page.evaluate(() => {
      window.__uruGame.scene.getScene('WORLD_SCENE').runScript([{ say: ['Turn the phone while I talk, and this box should stay along the bottom of the game.'], speaker: 'Ajji' }]);
    });
    await sleep(page, 1500);
    const up = await dialog();
    console.log('upright: square game, big dialog on the bottom edge:', JSON.stringify(await gameSize()) === '[1024,1024]' && up.k > 1 && Math.round(up.bottom) === 1024, JSON.stringify(up));
    await page.setViewportSize({ width: 874, height: 402 });
    await sleep(page, 800);
    const side = await dialog();
    console.log('sideways: 16:9 game, normal dialog on the bottom edge:', JSON.stringify(await gameSize()) === '[1024,576]' && side.k === 1 && Math.round(side.bottom) === 576 && side.visible, JSON.stringify(side));
    const zoom = await page.evaluate(() => window.__uruGame.scene.getScene('WORLD_SCENE').cameras.main.zoom);
    console.log('sideways: overworld back to its normal zoom:', zoom === 1);
    await page.screenshot({ path: `${shots}/mob_turn_side.png` });
    await page.setViewportSize({ width: 402, height: 874 });
    await sleep(page, 800);
    const back = await dialog();
    console.log('upright again:', back.k > 1 && Math.round(back.bottom) === 1024, JSON.stringify(back));
    await press(page, 'A');
    await sleep(page, 400);
    await press(page, 'A');
    // a battle started upright carries on, shrunk to fit, when the phone turns, and still takes taps
    await open(page, '?scene=test&battle=wild&species=10&level=5&party=6:30');
    await waitScene(page, 'BATTLE_SCENE');
    await sleep(page, 2500);
    await page.setViewportSize({ width: 874, height: 402 });
    await sleep(page, 800);
    for (let i = 0; i < 20; i += 1) {
      const s = await page.evaluate(() => { const b = window.__uruGame.scene.getScene('BATTLE_SCENE'); return { menu: b.menuMode, waiting: b.messageBox.isWaiting }; });
      if (s.menu === 'main') break;
      if (s.waiting) {
        const c = (await rects()).canvas;
        await page.touchscreen.tap((c.l + c.r) / 2, c.b - 30);
      }
      await sleep(page, 300);
    }
    const menu = await page.evaluate(() => window.__uruGame.scene.getScene('BATTLE_SCENE').menuMode);
    console.log('battle turned sideways mid-fight still answers taps:', menu === 'main');
    await page.screenshot({ path: `${shots}/mob_turn_battle.png` });
  } finally {
    console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
    await browser.close();
  }
  process.exit(0);
}

try {
  // title: tap to open the menu, tap QUICK BATTLE, then BACK
  await open(page, '');
  await waitScene(page, 'TITLE_SCENE');
  await sleep(page, 900);
  if (orient === 'portrait') {
    const [, gh] = await gameSize();
    const { canvas, buttons } = await rects();
    const clash = buttons.filter((b) => overlaps(b, canvas)).map((b) => b.name);
    console.log('upright, the game is square:', gh === 1024 && Math.round(canvas.r - canvas.l) === Math.round(canvas.b - canvas.t), JSON.stringify(canvas));
    console.log('upright, the pad is below the game:', clash.length === 0, clash.join(' '));
  }
  await tapGame(512, 300);
  await sleep(page, 400);
  const menu = await page.evaluate(() => {
    const t = window.__uruGame.scene.getScene('TITLE_SCENE');
    const c = t.menu?.container;
    return c ? { x: c.x, y: c.y, k: c.scaleX, rh: t.menu.cfg.rowHeight, items: t.menuItems } : null;
  });
  console.log('title menu opened by a tap:', Boolean(menu));
  const qi = menu.items.indexOf('QUICK BATTLE');
  await tapGame(menu.x + 120 * menu.k, menu.y + (18 + qi * menu.rh + menu.rh / 2 - 4) * menu.k);
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
  const mirror = await page.evaluate(() => (document.querySelector('.msg-mirror.on') ? document.querySelector('.msg-mirror').textContent : ''));
  console.log('tapping an NPC started a conversation:', talking, '| mirrored text:', JSON.stringify(mirror.slice(0, 50)));
  if (orient === 'portrait') {
    const k = await page.evaluate(() => window.__uruGame.scene.getScene('DIALOG_SCENE').k);
    console.log('upright, the conversation is big in the game and not repeated below:', k > 1 && !mirror);
  }
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
    else if (s.handler) {
      // FIGHT, then the first move: where they are depends on the layout (a tall one has bigger menus)
      const L = await page.evaluate(() => window.__uruGame.scene.getScene('BATTLE_SCENE').L);
      const k = L.k;
      const fight = L.tall ? [1024 - 400 * k + 96 * k, L.field + 60 * k] : [660, 462];
      const move = L.tall ? [100 * k, L.field + 38 * k] : [140, 462];
      await tapGame(...fight);
      await sleep(page, 300);
      await tapGame(...move);
    }
    await sleep(page, 250);
  }
  console.log('fought with taps only:', attacked);
  await page.screenshot({ path: `${shots}/mob_${orient}_battle.png` });
} finally {
  console.log(errors.length ? `ERRORS:\n${errors.join('\n')}` : 'no errors');
  await browser.close();
}
