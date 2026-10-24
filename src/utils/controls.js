import { DIRECTION } from '../common/direction.js';
import { inputManager } from '../input/input-manager.js';

/**
 * Per-scene view of the shared input manager. Method names are kept from the original keyboard-only
 * version: "space" means the A button, "back"/"shift" means B and "enter" means START.
 * The Esc key counts as START or B, whichever the scene asks for first: the overworld checks START before anything
 * else, so Esc opens the menu there, and menus check B, so it backs out of them.
 */
export class Controls {
  /** @type {Phaser.Scene} */
  #scene;
  /** @type {boolean} */
  #lockPlayerInput;

  /**
   * @param {Phaser.Scene} scene
   */
  constructor(scene) {
    this.#scene = scene;
    this.#lockPlayerInput = false;
  }

  /** @type {boolean} */
  get isInputLocked() {
    return this.#lockPlayerInput;
  }

  /** @param {boolean} val */
  set lockInput(val) {
    this.#lockPlayerInput = val;
  }

  /** Must be called once per scene update before reading input. */
  update() {
    inputManager.beginFrame(this.#scene.game.loop.frame);
  }

  /** @param {'A'|'B'|'START'|'ESC'} button */
  #justPressed(button) {
    this.update();
    if (inputManager.justPressed(button)) {
      inputManager.consume(button);
      return true;
    }
    return false;
  }

  /** @returns {boolean} START (or Esc) */
  wasEnterKeyPressed() {
    return this.#justPressed('START') || this.#justPressed('ESC');
  }

  /** @returns {boolean} A */
  wasSpaceKeyPressed() {
    return this.#justPressed('A');
  }

  /** @returns {boolean} A */
  wasConfirmPressed() {
    return this.#justPressed('A');
  }

  /** @returns {boolean} B (or Esc) */
  wasBackKeyPressed() {
    return this.#justPressed('B') || this.#justPressed('ESC');
  }

  /** @returns {boolean} kept for compatibility; fullscreen is handled globally */
  wasFKeyPressed() {
    return false;
  }

  /** @returns {boolean} B held (run) */
  isShiftKeyDown() {
    return inputManager.isDown('B');
  }

  /** @returns {import('../common/direction.js').Direction} */
  getDirectionKeyJustPressed() {
    this.update();
    const d = inputManager.justPressedDirection();
    if (d !== 'NONE') {
      inputManager.consume(d);
    }
    return /** @type {import('../common/direction.js').Direction} */ (DIRECTION[d]);
  }

  /** @returns {import('../common/direction.js').Direction} */
  getDirectionKeyPressedDown() {
    this.update();
    let d = inputManager.heldDirection();
    if (d === 'NONE') {
      // a quick tap can press and release within one frame; still count it as one step
      d = inputManager.justPressedDirection();
    }
    return /** @type {import('../common/direction.js').Direction} */ (DIRECTION[d]);
  }
}
