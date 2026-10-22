import Phaser from '../lib/phaser.js';

/**
 * High-resolution art for big creature and trainer pictures (battles, the starter showcase, the Pustaka).
 * assets/images/creatures_hd/NNN.webp and trainers_hd/<name>.webp are 4x the size of the pixel sprites and framed the
 * same way, so a sprite drawn at scale s swaps to its HD texture at scale s / 4 without moving. They are not in the
 * manifest: scenes load the few they need on demand and keep showing the pixel sprite until they arrive.
 */
export const HD_FACTOR = 4;
export const monHdKey = (id) => `MONHD_${String(id).padStart(3, '0')}`;
export const trainerHdKey = (name) => `TRAINERHD_${name}`;

/** @param {string} key */
function url(key) {
  return key.startsWith('MONHD_')
    ? `assets/images/creatures_hd/${key.slice('MONHD_'.length)}.webp`
    : `assets/images/trainers_hd/${key.slice('TRAINERHD_'.length)}.webp`;
}

/**
 * Loads HD textures that aren't loaded yet. Resolves when they are (missing files are skipped).
 * @param {Phaser.Scene} scene
 * @param {string[]} keys
 * @returns {Promise<void>}
 */
export function loadHd(scene, keys) {
  const todo = [...new Set(keys)].filter((k) => !scene.textures.exists(k));
  if (!todo.length) {
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    todo.forEach((k) => scene.load.image(k, url(k)));
    scene.load.once(Phaser.Loader.Events.COMPLETE, () => {
      // smooth sampling: the game is pixelArt, which would otherwise sample these with nearest-neighbour
      todo.filter((k) => scene.textures.exists(k)).forEach((k) => scene.textures.get(k).setFilter(Phaser.Textures.FilterMode.LINEAR));
      resolve();
    });
    scene.load.start();
  });
}

/**
 * The best texture available for a picture: the HD one if loaded, else the pixel sprite, with the matching scale.
 * @param {Phaser.Scene} scene
 * @param {string} lowKey
 * @param {string} hdKey
 * @param {number} lowScale the scale the pixel sprite is drawn at
 */
export function bestArt(scene, lowKey, hdKey, lowScale) {
  return scene.textures.exists(hdKey) ? { key: hdKey, scale: lowScale / HD_FACTOR } : { key: lowKey, scale: lowScale };
}

/**
 * Shows the HD version of an image as soon as it has loaded, keeping its on-screen size.
 * @param {Phaser.GameObjects.Image} image currently showing `lowKey`
 * @param {string} lowKey
 * @param {string} hdKey
 */
export function upgradeWhenLoaded(image, lowKey, hdKey) {
  loadHd(image.scene, [hdKey]).then(() => {
    if (image.active && image.texture.key === lowKey && image.scene.textures.exists(hdKey)) {
      image.setTexture(hdKey).setScale(image.scaleX / HD_FACTOR, image.scaleY / HD_FACTOR);
    }
  });
}
