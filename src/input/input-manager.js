/**
 * One input source for the whole game: keyboard plus the on-screen touch pad (see touch-controls.js).
 *
 * Buttons: UP DOWN LEFT RIGHT, A (confirm / talk), B (back / hold to run), START (menu).
 * Keyboard: arrows or WASD; A = Z, Space; B = X, Shift, Backspace; START = Enter, Esc.
 *
 * "Just pressed" is edge-triggered per frame: every scene calls `inputManager.beginFrame()` via Controls before
 * reading input, and a press is visible for exactly one game frame.
 */

/** @typedef {'UP'|'DOWN'|'LEFT'|'RIGHT'|'A'|'B'|'START'} Button */

const KEY_MAP = {
  ArrowUp: 'UP',
  KeyW: 'UP',
  ArrowDown: 'DOWN',
  KeyS: 'DOWN',
  ArrowLeft: 'LEFT',
  KeyA: 'LEFT',
  ArrowRight: 'RIGHT',
  KeyD: 'RIGHT',
  KeyZ: 'A',
  Space: 'A',
  KeyX: 'B',
  ShiftLeft: 'B',
  ShiftRight: 'B',
  Backspace: 'B',
  Enter: 'START',
  NumpadEnter: 'START',
  Escape: 'START',
};

/** @param {EventTarget | null} t */
function isTypingTarget(t) {
  return t instanceof HTMLInputElement || t instanceof HTMLTextAreaElement;
}

/** @type {Button[]} */
export const BUTTONS = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'B', 'START'];

class InputManager {
  constructor() {
    /** @type {Record<Button, number>} number of sources (keys / touches) currently holding each button */
    this.held = /** @type {any} */ (Object.fromEntries(BUTTONS.map((b) => [b, 0])));
    /** presses that arrived since the last frame */
    this.pending = new Set();
    /** presses visible during the current frame */
    this.pressedThisFrame = new Set();
    /** order in which directions were pressed so the latest held one wins */
    this.directionStack = [];
    this.lastFrame = -1;
    /** @type {Set<string>} keyboard codes currently down (to ignore auto-repeat) */
    this.downCodes = new Set();
    this.onFullscreenToggle = () => {};

    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', (e) => this.#onKeyDown(e));
      window.addEventListener('keyup', (e) => this.#onKeyUp(e));
      window.addEventListener('blur', () => this.releaseAll());
    }
  }

  /** @param {KeyboardEvent} e */
  #onKeyDown(e) {
    if (isTypingTarget(e.target)) {
      return;
    }
    if (e.code === 'KeyF') {
      if (!e.repeat) {
        this.onFullscreenToggle();
      }
      return;
    }
    const button = KEY_MAP[e.code];
    if (!button) {
      return;
    }
    e.preventDefault();
    if (this.downCodes.has(e.code)) {
      return;
    }
    this.downCodes.add(e.code);
    this.press(button);
  }

  /** @param {KeyboardEvent} e */
  #onKeyUp(e) {
    if (isTypingTarget(e.target) && !this.downCodes.has(e.code)) {
      return;
    }
    const button = KEY_MAP[e.code];
    if (!button || !this.downCodes.has(e.code)) {
      return;
    }
    this.downCodes.delete(e.code);
    this.release(button);
  }

  /** @param {Button} button */
  press(button) {
    this.held[button] += 1;
    this.pending.add(button);
    if (['UP', 'DOWN', 'LEFT', 'RIGHT'].includes(button)) {
      this.directionStack = this.directionStack.filter((d) => d !== button);
      this.directionStack.push(button);
    }
  }

  /** @param {Button} button */
  release(button) {
    this.held[button] = Math.max(0, this.held[button] - 1);
    if (this.held[button] === 0) {
      this.directionStack = this.directionStack.filter((d) => d !== button);
    }
  }

  releaseAll() {
    BUTTONS.forEach((b) => {
      this.held[b] = 0;
    });
    this.directionStack = [];
    this.downCodes.clear();
  }

  /**
   * Advances to a new frame. Safe to call from several scenes in the same frame.
   * @param {number} frame game.loop.frame
   */
  beginFrame(frame) {
    if (frame === this.lastFrame) {
      return;
    }
    this.lastFrame = frame;
    this.pressedThisFrame = this.pending;
    this.pending = new Set();
  }

  /** @param {Button} button */
  justPressed(button) {
    return this.pressedThisFrame.has(button);
  }

  /**
   * Marks a press as handled so another scene running in the same frame doesn't also act on it.
   * @param {Button} button
   */
  consume(button) {
    this.pressedThisFrame.delete(button);
  }

  /** @param {Button} button */
  isDown(button) {
    return this.held[button] > 0;
  }

  /** @returns {'UP'|'DOWN'|'LEFT'|'RIGHT'|'NONE'} most recently pressed direction still held */
  heldDirection() {
    return /** @type {any} */ (this.directionStack[this.directionStack.length - 1] || 'NONE');
  }

  /** @returns {'UP'|'DOWN'|'LEFT'|'RIGHT'|'NONE'} */
  justPressedDirection() {
    for (const d of ['UP', 'DOWN', 'LEFT', 'RIGHT']) {
      if (this.pressedThisFrame.has(d)) {
        return /** @type {any} */ (d);
      }
    }
    return 'NONE';
  }
}

export const inputManager = new InputManager();
