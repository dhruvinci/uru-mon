import { inputManager } from './input-manager.js';

/**
 * On-screen controls for phones and tablets. The game itself is touch-first (tap to walk, tap menus and dialog), so
 * the pad is a backup plus the buttons taps can't replace (B to go back, START for the menu):
 *   - portrait: the game sits on top at full width; a full pad sits under your thumbs.
 *   - landscape: the game fills the height; A/B/START live in the side margins so nothing covers the game, and the
 *     D-pad is optional (the ✥ button shows it, remembered per device).
 * Shown automatically on touch-first devices; `?touch=1` forces it on and `?touch=0` off.
 */
export function setupTouchControls() {
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
    <div class="pad-hint">Tap the map to walk · tap menus to choose<br><span class="rotate">↻ Turn your phone sideways for a bigger screen</span></div>
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

  // portrait: repeat the message on screen in large type in the space under the game
  const hint = /** @type {HTMLElement} */ (pad.querySelector('.pad-hint'));
  const defaultHint = hint.innerHTML;
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
    hint.innerHTML = message ? '' : defaultHint;
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
  if (!document.fullscreenEnabled && !document.documentElement.webkitRequestFullscreen) {
    pad.querySelector('[data-tool="fullscreen"]')?.remove(); // iOS Safari: use Add to Home Screen instead
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
        if (document.fullscreenElement) {
          document.exitFullscreen?.();
        } else {
          (el.requestFullscreen || el.webkitRequestFullscreen)?.call(el, { navigationUI: 'hide' })?.catch?.(() => {});
          screen.orientation?.lock?.('landscape').catch(() => {});
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

  // phones held upright: the 16:9 game is a thin strip, so ask for landscape (with a way to carry on anyway)
  const ios = /iPhone|iPod/.test(navigator.userAgent);
  const installed = window.matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches
    || /** @type {any} */ (navigator).standalone;
  const rotate = document.createElement('div');
  rotate.className = 'rotate-overlay';
  rotate.innerHTML = `
    <div class="phone-icon"></div>
    <div class="rotate-title">Turn your phone sideways</div>
    <div class="rotate-sub">uru-mon plays like a handheld console: the screen is much bigger held sideways.</div>
    ${ios && !installed ? '<div class="rotate-tip">Tip: tap Share, then <b>Add to Home Screen</b>, to play full screen without the browser bars.</div>' : ''}
    <button class="rotate-skip">Play upright anyway</button>`;
  document.body.appendChild(rotate);
  try {
    if (sessionStorage.getItem('uru-upright') === 'ok') {
      document.body.classList.add('upright-ok');
    }
  } catch {
    /* ignore */
  }
  rotate.querySelector('.rotate-skip')?.addEventListener('click', () => {
    document.body.classList.add('upright-ok');
    try {
      sessionStorage.setItem('uru-upright', 'ok');
    } catch {
      /* ignore */
    }
  });

  // Android: the first tap in landscape goes full screen, hiding the browser bars (iPhones can't; see the tip above)
  let triedFullscreen = false;
  window.addEventListener('pointerup', () => {
    if (triedFullscreen || installed || document.fullscreenElement || !document.fullscreenEnabled
      || window.innerWidth < window.innerHeight) {
      return;
    }
    triedFullscreen = true;
    document.documentElement.requestFullscreen({ navigationUI: 'hide' })
      .then(() => /** @type {any} */ (screen.orientation)?.lock?.('landscape'))
      .catch(() => {});
  });

  // landscape layout depends on how much room the 16:9 game leaves at the sides
  const layout = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const gutter = Math.max(0, (w - (h * 16) / 9) / 2);
    document.body.style.setProperty('--gutter', `${gutter}px`);
    document.body.classList.toggle('roomy', w > h && gutter >= 72);
  };
  layout();
  window.addEventListener('resize', layout);
  window.addEventListener('orientationchange', () => setTimeout(layout, 200));
}
