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

/** Presses a game button by sending a key. A=z, B=x, START=Enter. */
export async function press(page, button, holdMs = 60) {
  const key = { A: 'z', B: 'x', START: 'Enter', UP: 'ArrowUp', DOWN: 'ArrowDown', LEFT: 'ArrowLeft', RIGHT: 'ArrowRight' }[button] || button;
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
