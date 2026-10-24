import Phaser from '../lib/phaser.js';

/**
 * The canvas is always 1024 wide. It is 576 tall (16:9) except on touch screens held upright, where it grows towards a
 * square to fill the space above the pad (touch-controls.js picks the height, and changes it when the phone turns).
 * Scenes are laid out for 1024x576. Menu screens keep that layout at the top of a taller canvas, with their backgrounds
 * drawn down to FULL_HEIGHT, and the page repeats their messages in large type underneath. The overworld, its dialog,
 * the title screen and battles use the whole canvas, and scale their text and menus up by uiScale() once it is tall.
 */
export const GAME_WIDTH = 1024;
export const DESIGN_HEIGHT = 576;
/** The tallest the canvas gets (a square). */
export const FULL_HEIGHT = 1024;
/** From this height on, the full-canvas scenes lay themselves out for the whole canvas. */
const TALL_HEIGHT = 720;
const TALL_UI_SCALE = 1.35;

/**
 * Whether the canvas is tall: a touch screen held upright.
 * @param {Phaser.Scene} scene
 */
export function isTall(scene) {
  return scene.scale.height >= TALL_HEIGHT;
}

/**
 * How much bigger the full-canvas scenes draw their text and menus: 1 normally, more on a phone held upright, where
 * the 1024-pixel width is shown in about 400 CSS pixels and text would otherwise be tiny (tablets are wide enough).
 * @param {Phaser.Scene} scene
 * @returns {number}
 */
export function uiScale(scene) {
  return isTall(scene) && scene.scale.displaySize.width < 600 ? TALL_UI_SCALE : 1;
}

/**
 * Calls fn whenever the canvas changes size (a phone turned between upright and sideways), until the scene shuts down.
 * @param {Phaser.Scene} scene
 * @param {() => void} fn
 */
export function onResize(scene, fn) {
  const size = () => `${scene.scale.width}x${scene.scale.height}/${uiScale(scene)}`;
  let last = size();
  const handler = () => {
    const now = size();
    if (now !== last) {
      last = now;
      fn();
    }
  };
  scene.scale.on(Phaser.Scale.Events.RESIZE, handler);
  scene.events.once(Phaser.Scenes.Events.SHUTDOWN, () => scene.scale.off(Phaser.Scale.Events.RESIZE, handler));
}

/**
 * Renders a scene's text at `res` times its size, so text in containers scaled up by uiScale() stays crisp instead of
 * being stretched. Applies to the text already on screen and to any added later.
 * @param {Phaser.Scene & {textRes?: number}} scene
 * @param {number} res
 */
export function setTextResolution(scene, res) {
  if (scene.textRes === undefined) {
    scene.events.on(Phaser.Scenes.Events.ADDED_TO_SCENE, (/** @type {any} */ go) => {
      if (go.type === 'Text' && go.style.resolution !== scene.textRes) {
        go.setResolution(scene.textRes);
      }
    });
  }
  if (scene.textRes === res) {
    return;
  }
  scene.textRes = res;
  /** @param {any[]} list */
  const visit = (list) => list.forEach((go) => {
    if (go.type === 'Text' && go.style.resolution !== res) {
      go.setResolution(res);
    } else if (go.type === 'Container') {
      visit(go.list);
    }
  });
  visit(scene.children.list);
}
