// Shared Playwright helpers for driving uru-mon in headless Chromium.
import { chromium } from 'playwright';

export const BASE = process.env.URU_URL || 'http://127.0.0.1:8080/index.html';

/**
 * @param {{width?: number, height?: number, touch?: boolean}} [opts]
 */
export async function launch(opts = {}) {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const context = await browser.newContext({
    viewport: { width: opts.width || 1024, height: opts.height || 576 },
    hasTouch: Boolean(opts.touch),
    isMobile: Boolean(opts.touch),
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}\n${e.stack || ''}`));
  page.on('console', (m) => {
    if (m.type() === 'error') {
      errors.push(`console: ${m.text()}`);
    }
  });
  return { browser, page, errors };
}

/** @param {import('playwright').Page} page @param {string} query */
export async function open(page, query = '') {
  await page.goto(`${BASE}${query}`);
  await page.waitForFunction(() => window.__uru && window.__uru.gameData.species.length > 0, null, { timeout: 30000 });
}

/** Waits until a scene is active. */
export async function waitScene(page, key, timeout = 20000) {
  await page.waitForFunction((k) => window.__uruGame.scene.isActive(k), key, { timeout });
}

/** @returns {Promise<string[]>} active scene keys */
export async function activeScenes(page) {
  return page.evaluate(() => window.__uruGame.scene.getScenes(true).map((s) => s.scene.key));
}

/** Presses a game button by sending a key. A=z, B=x, START=Escape (START in the overworld, B elsewhere). */
export async function press(page, button, holdMs = 60) {
  const key = { A: 'z', B: 'x', START: 'Escape', UP: 'ArrowUp', DOWN: 'ArrowDown', LEFT: 'ArrowLeft', RIGHT: 'ArrowRight' }[button] || button;
  await page.keyboard.down(key);
  await page.waitForTimeout(holdMs);
  await page.keyboard.up(key);
  await page.waitForTimeout(40);
}

/** Holds a direction for roughly `tiles` steps. */
export async function walk(page, dir, tiles = 1) {
  await press(page, dir, 240 * tiles + 20);
  await page.waitForTimeout(260);
}

export async function sleep(page, ms) {
  await page.waitForTimeout(ms);
}

export async function state(page) {
  return page.evaluate(() => JSON.parse(JSON.stringify(window.__uru.dataManager.state)));
}

/** True when the overworld is active and accepting player input. */
export async function worldIdle(page) {
  return page.evaluate(() => {
    const w = window.__uruGame.scene.getScene('WORLD_SCENE');
    return Boolean(w && window.__uruGame.scene.isActive('WORLD_SCENE') && !w.inputLocked && w.player && !w.player.isMoving);
  });
}

/** Presses A until the world is idle again (dialog finished), or until timeout. */
export async function mashUntilIdle(page, ms = 30000) {
  const end = Date.now() + ms;
  await page.waitForTimeout(250);
  while (Date.now() < end) {
    if (await worldIdle(page)) {
      return true;
    }
    await press(page, 'A', 50);
    await page.waitForTimeout(140);
  }
  return false;
}

/** Presses A through battle messages until the player is choosing an action (or the battle ended). */
export async function untilBattleMenu(page, ms = 60000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const s = await page.evaluate(() => {
      const b = window.__uruGame.scene.getScene('BATTLE_SCENE');
      const active = window.__uruGame.scene.isActive('BATTLE_SCENE');
      return { active, menu: active && b.inputHandler !== null && !b.messageBox.isWaiting };
    });
    if (!s.active) return 'ended';
    if (s.menu) return 'menu';
    await press(page, 'A', 50);
    await page.waitForTimeout(150);
  }
  return 'timeout';
}

/** The player's current tile. */
export async function playerTile(page) {
  return page.evaluate(() => {
    const p = window.__uruGame.scene.getScene('WORLD_SCENE').player.sprite;
    return { x: Math.round(p.x / 64), y: Math.round(p.y / 64) };
  });
}

/**
 * Walks to a tile by breadth-first search over the collision layer (NPCs count as walls), one key press per step,
 * checking each arrival. Robust to layout changes, unlike timed walks. Returns true when it got there.
 * @param {import('playwright').Page} page
 * @param {number} tx
 * @param {number} ty
 */
export async function walkTo(page, tx, ty, maxSteps = 400) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const path = await page.evaluate(([gx, gy]) => {
      const w = window.__uruGame.scene.getScene('WORLD_SCENE');
      const W = w.map.width;
      const H = w.map.height;
      const blocked = new Set();
      for (let y = 0; y < H; y += 1) {
        for (let x = 0; x < W; x += 1) {
          if (w.collisionLayer.getTileAt(x, y)?.index > 0) blocked.add(y * W + x);
        }
      }
      w.npcs.forEach((n) => {
        if (n.sprite?.visible) blocked.add(Math.round(n.tilePosition.y / 64) * W + Math.round(n.tilePosition.x / 64));
      });
      const p = w.player.sprite;
      const start = Math.round(p.y / 64) * W + Math.round(p.x / 64);
      const goal = gy * W + gx;
      const prev = new Map([[start, -1]]);
      const queue = [start];
      const dirs = [[0, -1, 'UP'], [0, 1, 'DOWN'], [-1, 0, 'LEFT'], [1, 0, 'RIGHT']];
      while (queue.length) {
        const cur = queue.shift();
        if (cur === goal) break;
        const cx = cur % W;
        const cy = Math.floor(cur / W);
        for (const [dx, dy] of dirs) {
          const nx = cx + dx;
          const ny = cy + dy;
          const ni = ny * W + nx;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H || prev.has(ni) || (blocked.has(ni) && ni !== goal)) continue;
          prev.set(ni, cur);
          queue.push(ni);
        }
      }
      if (!prev.has(goal)) return null;
      const steps = [];
      for (let cur = goal; prev.get(cur) !== -1; cur = prev.get(cur)) {
        const from = prev.get(cur);
        const d = cur - from;
        steps.unshift(d === 1 ? 'RIGHT' : d === -1 ? 'LEFT' : d === W ? 'DOWN' : 'UP');
      }
      return steps;
    }, [tx, ty]);
    if (!path) return false;
    let ok = true;
    for (const dir of path.slice(0, maxSteps)) {
      // stop as soon as the world stops taking input (a battle, cutscene or dialog started)
      const free = await page.evaluate(() => {
        const w = window.__uruGame.scene.getScene('WORLD_SCENE');
        return window.__uruGame.scene.isActive('WORLD_SCENE') && !w.inputLocked;
      });
      if (!free) return false;
      const before = await playerTile(page);
      await press(page, dir, 60);
      const t0 = Date.now();
      let moved = false;
      while (Date.now() - t0 < 1500) {
        await page.waitForTimeout(40);
        const now = await playerTile(page);
        const idle = await page.evaluate(() => !window.__uruGame.scene.getScene('WORLD_SCENE').player.isMoving);
        if ((now.x !== before.x || now.y !== before.y) && idle) { moved = true; break; }
      }
      if (!moved) { ok = false; break; } // something got in the way (an NPC walked in, a trainer spotted us)
    }
    const at = await playerTile(page);
    if (ok && at.x === tx && at.y === ty) return true;
    const free = await page.evaluate(() => window.__uruGame.scene.isActive('WORLD_SCENE')
      && !window.__uruGame.scene.getScene('WORLD_SCENE').inputLocked);
    if (!free) return false;
    await page.waitForTimeout(400);
  }
  const at = await playerTile(page);
  return at.x === tx && at.y === ty;
}

/** Walks up to a warp door (to the tile on its exit side) and bumps into it. `warpId` picks one of several exits. */
export async function enterWarp(page, toArea, warpId) {
  const warp = await page.evaluate(([area, id]) => {
    const w = window.__uruGame.scene.getScene('WORLD_SCENE');
    return (w.uru.warps || []).find((x) => x.to === area && (!id || x.id === id));
  }, [toArea, warpId]);
  if (!warp) return false;
  const step = { UP: [0, -1], DOWN: [0, 1], LEFT: [-1, 0], RIGHT: [1, 0] }[warp.exit || 'DOWN'];
  const ok = await walkTo(page, warp.x + step[0], warp.y + step[1]);
  if (!ok) return false;
  const into = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT' }[warp.exit || 'DOWN'];
  await press(page, into, 120);
  await page.waitForTimeout(1200);
  return page.evaluate((area) => window.__uruGame.scene.getScene('WORLD_SCENE').area === area, toArea);
}
