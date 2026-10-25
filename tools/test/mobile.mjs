// Touch-only play on a phone-sized screen: tap to start, tap menus, tap to walk (through the HD-2D tilt), tap an NPC to
// talk, tap through a battle. Usage: node test/mobile.mjs <shots_dir> [portrait|landscape|iphone|turn]
//   portrait: held upright, where the game grows to a square and the overworld, dialog and battles draw big
//   iphone: sideways with an iPhone's notch margins and Safari's bars; the buttons must clear the game and the notch
//   turn: turns the phone mid-conversation, and mid-battle (a Quick Battle started upright, turned sideways in Safari)
import { launch, open, sleep, waitScene, press } from './harness.mjs';

const shots = process.argv[2] || '/tmp';
const orient = process.argv[3] || 'landscape';
const SIZES = {
  portrait: { width: 390, height: 844 },
  landscape: { width: 844, height: 390 },
  iphone: { width: 874, height: 296, insets: { l: 62, r: 62, b: 21 } }, // iPhone 17, Safari with its tab bar
  turn: { width: 402, height: 874, insets: { t: 62, b: 34, landscape: { l: 62, r: 62, b: 21 } } },
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
    // a Quick Battle started upright, with the moves open, then turned sideways in Safari (its tab bar showing): the
    // battle lays itself out again for the 16:9 game and covers it, then goes back to the tall layout when upright
    const battle = () => page.evaluate(() => {
      const g = window.__uruGame;
      const b = g.scene.getScene('BATTLE_SCENE');
      const box = b.messageBox.container;
      const menu = b.children.list.find((o) => o.type === 'Container' && o.depth === 55 && o.visible);
      const hidden = g.scene.getScenes(false).filter((s) => s !== b && s.sys.settings.status > 0 && !s.sys.settings.visible).map((s) => s.scene.key);
      return {
        size: [g.scale.width, g.scale.height], tall: b.L.tall, k: b.L.k, menu: b.menuMode,
        boxBottom: Math.round(box.y + b.messageBox.height * box.scaleY), menuAt: menu ? [Math.round(menu.y), menu.scaleX] : null,
        enemy: { y: Math.round(b.enemySprite.y), top: Math.round(b.enemySprite.getBounds().top), scale: b.enemySprite.scaleX },
        player: { y: Math.round(b.playerSprite.y), scale: b.playerSprite.scaleX },
        hud: Math.round(b.playerHud.container.y + 142 * b.playerHud.container.scaleY), field: b.L.field,
        hidden, cam: [b.cameras.main.width, b.cameras.main.height, b.cameras.main.zoom],
      };
    });
    const untilBattle = async (want) => {
      for (let i = 0; i < 40; i += 1) {
        const s = await page.evaluate(() => { const b = window.__uruGame.scene.getScene('BATTLE_SCENE'); return { menu: b.menuMode, waiting: b.messageBox.isWaiting }; });
        if (s.menu === want) return true;
        if (s.waiting) await press(page, 'A');
        await sleep(page, 300);
      }
      return false;
    };
    await open(page, '');
    await waitScene(page, 'TITLE_SCENE');
    await sleep(page, 800);
    await press(page, 'START');
    await sleep(page, 400);
    const items = await page.evaluate(() => window.__uruGame.scene.getScene('TITLE_SCENE').menuItems);
    for (let i = 0; i < items.indexOf('QUICK BATTLE'); i += 1) await press(page, 'DOWN');
    await press(page, 'A');
    await waitScene(page, 'QUICK_BATTLE_SCENE');
    await sleep(page, 1200);
    await press(page, 'A');
    await waitScene(page, 'BATTLE_SCENE');
    await untilBattle('main');
    // the teams are random: plenty of HP on both sides, so one turn can't knock anyone out and change what's on screen
    await page.evaluate(() => {
      window.__uruGame.scene.getScene('BATTLE_SCENE').battle.enemyActive.hp = 9999;
      window.__uru.dataManager.party.forEach((m) => { m.hp = 9999; });
    });
    await press(page, 'A'); // FIGHT
    await sleep(page, 400);
    const tallB = await battle();
    console.log('upright: the battle is tall, with the moves open:', tallB.tall && tallB.menu === 'moves' && tallB.boxBottom === 1024, JSON.stringify(tallB));
    await page.screenshot({ path: `${shots}/mob_turn_battle_up.png` });
    await page.setViewportSize({ width: 874, height: 296 });
    await sleep(page, 900);
    const sideB = await battle();
    const fits = sideB.size[1] === 576 && !sideB.tall && sideB.k === 1 && sideB.boxBottom === 576 && JSON.stringify(sideB.menuAt) === '[432,1]';
    console.log('sideways: the battle is laid out for 16:9, moves still open along the bottom:', fits && sideB.menu === 'moves', JSON.stringify(sideB));
    console.log('sideways: creatures and HUDs where a 16:9 battle has them:', sideB.enemy.y === 236 && sideB.player.y === 440 && sideB.hud <= sideB.field && sideB.enemy.scale < tallB.enemy.scale);
    console.log('sideways: the camera fills the game and nothing underneath shows:', JSON.stringify(sideB.cam) === '[1024,576,1]' && sideB.hidden.includes('QUICK_BATTLE_SCENE'));
    const { canvas, buttons } = await rects();
    const clash = buttons.filter((b) => overlaps(b, canvas)).map((b) => b.name);
    console.log('sideways: no button covers the game:', clash.length === 0, clash.join(' '));
    await page.screenshot({ path: `${shots}/mob_turn_battle.png` });
    // pick a move with a tap on the new layout, and play the turn out
    const moveAt = await toScreen(140, 462);
    await page.touchscreen.tap(moveAt.x, moveAt.y);
    await sleep(page, 300);
    const used = await page.evaluate(() => window.__uruGame.scene.getScene('BATTLE_SCENE').menuMode !== 'moves');
    console.log('sideways: tapping a move on the new layout uses it:', used);
    const again = await untilBattle('main');
    await page.evaluate(() => document.fullscreenElement && document.exitFullscreen()); // the tap went full screen, as on Android
    await sleep(page, 300);
    const settled = await battle();
    console.log('sideways: after the turn, everything is in place:', again && settled.enemy.y === 236 && settled.player.y === 440, JSON.stringify(settled));
    await page.setViewportSize({ width: 402, height: 874 });
    await sleep(page, 900);
    const upB = await battle();
    console.log('upright again: the battle is tall again, main menu redrawn:', upB.tall && upB.k > 1 && upB.menu === 'main' && upB.boxBottom === 1024 && upB.menuAt?.[0] === upB.field && upB.menuAt[1] === upB.k, JSON.stringify(upB));
    await page.screenshot({ path: `${shots}/mob_turn_battle_up2.png` });
    // the battle scene is reused: a second battle after a night one (which leaves a tinted backdrop behind) still runs
    await open(page, '?scene=test&battle=wild&species=10&level=5&party=6:30&time=night');
    await waitScene(page, 'BATTLE_SCENE');
    await untilBattle('main');
    const tinted = await page.evaluate(() => Boolean(window.__uruGame.scene.getScene('BATTLE_SCENE').nightTint));
    await page.evaluate(() => {
      const g = window.__uruGame;
      g.scene.stop('BATTLE_SCENE');
      g.scene.start('BATTLE_SCENE', { wild: window.__uru.createMonster(13, 5), environment: 'grass' });
    });
    await sleep(page, 500);
    console.log('a second battle after a night one starts:', tinted && await untilBattle('main'));
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
