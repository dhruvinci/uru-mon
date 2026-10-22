import { inputManager } from './input-manager.js';

/**
 * On-screen game pad for phones and tablets (D-pad, A, B, START), drawn as DOM elements over the page.
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
    <div class="dpad">
      <button data-btn="UP" class="dir up" aria-label="Up"></button>
      <button data-btn="LEFT" class="dir left" aria-label="Left"></button>
      <button data-btn="RIGHT" class="dir right" aria-label="Right"></button>
      <button data-btn="DOWN" class="dir down" aria-label="Down"></button>
      <div class="dpad-center"></div>
    </div>
    <button data-btn="START" class="start" aria-label="Start">START</button>
    <div class="ab">
      <button data-btn="B" class="b" aria-label="B">B</button>
      <button data-btn="A" class="a" aria-label="A">A</button>
    </div>`;
  document.body.appendChild(pad);

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
}
