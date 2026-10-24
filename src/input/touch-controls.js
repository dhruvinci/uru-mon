import { inputManager } from './input-manager.js';
import { DESIGN_HEIGHT, FULL_HEIGHT, GAME_WIDTH } from '../ui/screen.js';

/**
 * On-screen controls for phones and tablets. The game itself is touch-first (tap to walk, tap menus and dialog), so
 * the pad is a backup plus the buttons taps can't replace (B to go back, START for the menu):
 *   - portrait: the game sits on top at full width and grows towards a square to fill the space above a full pad
 *     (see ui/screen.js for how scenes use the extra height);
 *   - landscape: the game is 16:9 and fills the height; A/B/START live in the side margins, clear of the notch, so
 *     nothing covers the game, and the D-pad is optional (the ✥ button shows it, remembered per device).
 * Shown automatically on touch-first devices; `?touch=1` forces it on and `?touch=0` off.
 * @param {Phaser.Game} game
 */
export function setupTouchControls(game) {
  const params = new URLSearchParams(window.location.search);
  const forced = params.get('touch');
  const isTouch = window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
  if (forced === '0' || (!isTouch && forced !== '1')) {
    return;
  }
  document.body.classList.add('has-touch-controls');

  const pad = document.createElement('div');
  pad.className = 'touch-pad';
  pad.innerHTML = `
    <div class="pad-hint">Tap the map to walk · tap menus to choose</div>
    <div class="dpad">
      <button data-btn="UP" class="dir up" aria-label="Up"></button>
      <button data-btn="LEFT" class="dir left" aria-label="Left"></button>
      <button data-btn="RIGHT" class="dir right" aria-label="Right"></button>
      <button data-btn="DOWN" class="dir down" aria-label="Down"></button>
      <div class="dpad-center"></div>
    </div>
    <div class="ab">
      <button data-btn="A" class="a" aria-label="A">A</button>
      <button data-btn="B" class="b" aria-label="B">B</button>
    </div>
    <div class="sys">
      <button data-btn="START" class="start" aria-label="Menu">MENU</button>
      <button data-tool="dpad" class="tool" aria-label="Show or hide the D-pad">✥</button>
      <button data-tool="fullscreen" class="tool" aria-label="Fullscreen">⛶</button>
    </div>`;
  document.body.appendChild(pad);

  // portrait: menu screens keep their 16:9 layout at the top of the game, and their messages are repeated in large
  // type underneath (the overworld and battles show big text themselves there, so their messages aren't announced)
  const hint = /** @type {HTMLElement} */ (pad.querySelector('.pad-hint'));
  const mirror = document.createElement('div');
  mirror.className = 'msg-mirror';
  pad.appendChild(mirror);
  mirror.addEventListener('pointerup', () => inputManager.tap('A'));
  const who = document.createElement('div');
  who.className = 'who';
  const said = document.createElement('div');
  mirror.append(who, said);
  window.addEventListener('uru:speaker', (e) => {
    who.textContent = /** @type {CustomEvent} */ (e).detail;
  });
  window.addEventListener('uru:message', (e) => {
    const message = /** @type {CustomEvent} */ (e).detail;
    said.textContent = message;
    if (!message) {
      who.textContent = '';
    }
    mirror.classList.toggle('on', Boolean(message));
    hint.classList.toggle('hidden', Boolean(message));
  });

  // the D-pad choice in landscape is remembered
  const remember = (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* storage unavailable: fine, it just won't be remembered */
    }
  };
  try {
    if (localStorage.getItem('uru-dpad') === 'on') {
      document.body.classList.add('show-dpad');
    }
  } catch {
    /* ignore */
  }

  // iPhones can't put a web page in full screen; the ⛶ button explains Add to Home Screen instead
  const ios = /iPhone|iPod/.test(navigator.userAgent);
  const installed = window.matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches
    || /** @type {any} */ (navigator).standalone;
  const canFullscreen = document.fullscreenEnabled || Boolean(document.documentElement.webkitRequestFullscreen);
  const tip = document.createElement('div');
  tip.className = 'fs-tip';
  tip.innerHTML = `<b>Play full screen</b>Safari keeps its bars on web pages. Tap Safari's <b>Share</b> button, then
    <b>Add to Home Screen</b>, and open uru-mon from your home screen: it fills the whole screen like an app.
    <span class="fs-tip-close">Got it</span>`;
  document.body.appendChild(tip);
  tip.addEventListener('pointerup', () => tip.classList.remove('on'));
  if (installed || (!canFullscreen && !ios)) {
    pad.querySelector('[data-tool="fullscreen"]')?.remove();
  }
  if (ios && !installed && !canFullscreen) {
    // shown once per device, the first time the game is played in Safari, for a few seconds
    let seen = 'yes';
    try {
      seen = localStorage.getItem('uru-fs-tip') || '';
      localStorage.setItem('uru-fs-tip', 'yes');
    } catch {
      /* ignore */
    }
    if (!seen) {
      window.addEventListener('pointerup', () => {
        setTimeout(() => tip.classList.add('on'), 400);
        setTimeout(() => tip.classList.remove('on'), 12000);
      }, { once: true });
    }
  }

  /** @type {Map<number, string>} pointerId -> button currently held by that pointer */
  const active = new Map();

  /** @param {PointerEvent} e */
  const buttonAt = (e) => {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    const btn = el && el.closest('[data-btn]');
    return btn ? btn.getAttribute('data-btn') : null;
  };

  const setHeld = (pointerId, button) => {
    const prev = active.get(pointerId);
    if (prev === button) {
      return;
    }
    if (prev) {
      inputManager.release(/** @type {any} */ (prev));
      pad.querySelector(`[data-btn="${prev}"]`)?.classList.remove('held');
    }
    if (button) {
      inputManager.press(/** @type {any} */ (button));
      pad.querySelector(`[data-btn="${button}"]`)?.classList.add('held');
      active.set(pointerId, button);
      if (navigator.vibrate) {
        navigator.vibrate(8);
      }
    } else {
      active.delete(pointerId);
    }
  };

  pad.addEventListener('pointerdown', (e) => {
    const tool = /** @type {HTMLElement} */ (e.target).closest?.('[data-tool]');
    if (tool) {
      e.preventDefault();
      const which = tool.getAttribute('data-tool');
      if (which === 'dpad') {
        const on = document.body.classList.toggle('show-dpad');
        remember('uru-dpad', on ? 'on' : 'off');
      } else if (which === 'fullscreen') {
        const el = document.documentElement;
        if (!canFullscreen) {
          tip.classList.toggle('on');
        } else if (document.fullscreenElement) {
          document.exitFullscreen?.();
        } else {
          (el.requestFullscreen || el.webkitRequestFullscreen)?.call(el, { navigationUI: 'hide' })?.catch?.(() => {});
        }
      }
      return;
    }
    if (!(/** @type {HTMLElement} */ (e.target).closest?.('[data-btn]'))) {
      return; // empty pad space: let the tap through to nothing
    }
    e.preventDefault();
    pad.setPointerCapture?.(e.pointerId);
    setHeld(e.pointerId, buttonAt(e));
  });
  pad.addEventListener('pointermove', (e) => {
    if (!active.has(e.pointerId)) {
      return;
    }
    // let a thumb slide across the D-pad between directions
    const next = buttonAt(e);
    const prev = active.get(e.pointerId);
    const isDir = (b) => ['UP', 'DOWN', 'LEFT', 'RIGHT'].includes(b);
    if (next && isDir(next) && isDir(prev)) {
      setHeld(e.pointerId, next);
    }
  });
  const end = (e) => setHeld(e.pointerId, null);
  pad.addEventListener('pointerup', end);
  pad.addEventListener('pointercancel', end);
  pad.addEventListener('contextmenu', (e) => e.preventDefault());

  // Android: the first tap goes full screen, hiding the browser bars (iPhones can't; see the tip above)
  let triedFullscreen = false;
  window.addEventListener('pointerup', () => {
    if (triedFullscreen || installed || document.fullscreenElement || !document.fullscreenEnabled) {
      return;
    }
    triedFullscreen = true;
    document.documentElement.requestFullscreen({ navigationUI: 'hide' }).catch(() => {});
  });

  // The safe-area insets (notch, rounded corners, home bar), read through CSS variables that index.html sets to env().
  const probe = document.createElement('div');
  probe.style.cssText = 'position:fixed;visibility:hidden;pointer-events:none;'
    + 'padding:var(--safe-t) var(--safe-r) var(--safe-b) var(--safe-l)';
  document.body.appendChild(probe);
  const insets = () => {
    const s = getComputedStyle(probe);
    return { t: parseFloat(s.paddingTop) || 0, r: parseFloat(s.paddingRight) || 0, b: parseFloat(s.paddingBottom) || 0, l: parseFloat(s.paddingLeft) || 0 };
  };

  const container = /** @type {HTMLElement} */ (document.getElementById('game-container'));
  const body = document.body;
  const px = (name, value) => body.style.setProperty(name, `${Math.round(value)}px`);
  /** Sizes the game for the screen and places everything around it. */
  const layout = () => {
    if (document.activeElement?.tagName === 'INPUT') {
      return; // an on-screen keyboard is up (name entry): keep the game as it is until it closes
    }
    const w = window.innerWidth;
    const h = window.innerHeight;
    const s = insets();
    let rect;
    let gameHeight = DESIGN_HEIGHT;
    if (w > h) {
      // sideways: 16:9 at full height, with a column of buttons in each margin, clear of the notch. When the margins
      // are too narrow for that (shorter phones, tablets), shrink the game until they fit, by up to a fifth; past that,
      // overlay the buttons on the game's corners.
      const side = Math.max(s.l, s.r);
      const column = 84;
      const full = Math.min(w, (h * 16) / 9);
      const squeezed = w - 2 * (side + column);
      let width = full;
      let roomy = (w - full) / 2 - side >= column;
      if (!roomy && squeezed >= full * 0.8) {
        width = squeezed;
        roomy = true;
      }
      const height = (width * 9) / 16;
      rect = { left: (w - width) / 2, top: (h - height) / 2, width, height };
      const colW = (w - width) / 2 - side - 12;
      px('--col-w', colW);
      px('--btn', Math.max(52, Math.min(colW - 4, 78)));
      body.classList.toggle('roomy', roomy);
      body.classList.add('mirror-off');
    } else {
      // upright: as tall as the room above the pad allows, up to a square
      body.classList.remove('roomy');
      const padTop = Math.min(...['.dpad', '.ab'].map((sel) => /** @type {HTMLElement} */ (pad.querySelector(sel)).getBoundingClientRect().top));
      const width = w - s.l - s.r;
      const room = padTop - 12 - s.t;
      const wanted = Math.max((width * DESIGN_HEIGHT) / GAME_WIDTH, Math.min(width, room));
      gameHeight = Math.max(DESIGN_HEIGHT, Math.min(FULL_HEIGHT, Math.round((GAME_WIDTH * wanted) / width / 2) * 2));
      const height = (width * gameHeight) / GAME_WIDTH;
      rect = { left: s.l, top: s.t, width, height };
      // menu screens' messages, repeated large under their 16:9 layout (over the rest of the game) down to the pad
      const mirrorTop = s.t + (width * DESIGN_HEIGHT) / GAME_WIDTH + 10;
      px('--mirror-top', mirrorTop);
      px('--mirror-max', padTop - 10 - mirrorTop);
      body.classList.toggle('mirror-off', padTop - 10 - mirrorTop < 72);
      // the hint goes in the gap between the game and the pad, if there is one
      const gap = padTop - (rect.top + height);
      px('--hint-top', rect.top + height + Math.max(6, (gap - 48) / 2));
      body.classList.toggle('hint-off', gap < 48);
    }
    Object.assign(container.style, {
      left: `${rect.left}px`, top: `${rect.top}px`, width: `${rect.width}px`, height: `${rect.height}px`, right: 'auto', bottom: 'auto',
    });
    px('--game-l', rect.left);
    px('--game-w', rect.width);
    if (!ready) {
      return; // the renderer boots at 1024x576; laid out again once the game is ready
    }
    game.scale.getParentBounds(); // so the resize sees the new container size straight away
    if (game.scale.height !== gameHeight) {
      game.scale.setGameSize(GAME_WIDTH, gameHeight);
    } else {
      game.scale.refresh();
    }
  };
  let ready = false;
  layout();
  game.events.once('ready', () => {
    ready = true;
    layout();
  });
  window.addEventListener('resize', layout);
  window.visualViewport?.addEventListener('resize', layout);
  window.addEventListener('orientationchange', () => setTimeout(layout, 250));
  // the pad's size depends on the fonts and CSS, so measure again once everything has loaded
  window.addEventListener('load', layout);
  document.addEventListener('focusout', () => setTimeout(layout, 300));
}
