import { WORLD_KEYS } from '../assets/asset-keys.js';

/**
 * A dabba lying on the ground that the player can pick up.
 */
export class Item {
  /**
   * @param {object} config
   * @param {Phaser.Scene} config.scene
   * @param {{x: number, y: number}} config.position tile top-left in world pixels
   * @param {number} config.itemId
   * @param {string} config.id unique pickup id
   * @param {number} [config.quantity]
   */
  constructor(config) {
    this.id = config.id;
    this.itemId = config.itemId;
    this.quantity = config.quantity ?? 1;
    const scene = config.scene;
    this.gameObject = scene.textures.exists(WORLD_KEYS.ITEM_BALL)
      ? scene.add.image(config.position.x, config.position.y, WORLD_KEYS.ITEM_BALL).setOrigin(0).setScale(4)
      : scene.add.circle(config.position.x + 32, config.position.y + 32, 18, 0xe04040).setStrokeStyle(4, 0x2a2230);
    this.gameObject.setDepth(config.position.y);
    this.position = { ...config.position };
  }
}
