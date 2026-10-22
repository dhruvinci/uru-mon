import { DIRECTION } from '../../common/direction.js';
import { Character } from './character.js';
import { getTargetPositionFromGameObjectPositionAndDirection } from '../../utils/grid-utils.js';

/** Standard idle frames for CHAR_* sheets (row * 3). */
export const IDLE_FRAMES = Object.freeze({ DOWN: 0, UP: 3, LEFT: 6, RIGHT: 9, NONE: 0 });

/**
 * @typedef PlayerConfigProps
 * @type {object}
 * @property {string} assetKey CHAR_* spritesheet
 * @property {Phaser.Tilemaps.TilemapLayer} collisionLayer
 * @property {(target: {x: number, y: number}) => void} [bumpCallback] called when the player walks into something blocking
 */

/**
 * @typedef {Omit<import('./character').CharacterConfig, 'idleFrameConfig'> & PlayerConfigProps} PlayerConfig
 */

export class Player extends Character {
  /** @type {(target: {x: number, y: number}) => void} */
  #bumpCallback;
  /** @type {string} */
  #assetKey;
  #lastBump = 0;

  /**
   * @param {PlayerConfig} config
   */
  constructor(config) {
    super({
      ...config,
      // 16x32 frames: the bottom 16 px stand on the tile, the head overhangs the tile above.
      origin: { x: 0, y: 1 / 2 },
      idleFrameConfig: IDLE_FRAMES,
    });
    this.#assetKey = config.assetKey;
    this.#bumpCallback = config.bumpCallback;
  }

  /**
   * @param {import('../../common/direction.js').Direction} direction
   * @param {boolean} [isRunning=false]
   */
  moveCharacter(direction, isRunning = false) {
    if (this._isMoving || direction === DIRECTION.NONE) {
      return;
    }
    super.moveCharacter(direction, isRunning);

    const key = `${this.#assetKey}_${this._direction}`;
    if (this._isMoving) {
      if (!this._phaserGameObject.anims.isPlaying || this._phaserGameObject.anims.currentAnim?.key !== key) {
        this._phaserGameObject.play(key);
      }
      this._phaserGameObject.anims.timeScale = this._isRunning ? 1.8 : 1;
      return;
    }

    // blocked: face the way we tried to go and report what we bumped into
    this._phaserGameObject.anims.stop();
    this._phaserGameObject.setFrame(IDLE_FRAMES[this._direction]);
    const target = getTargetPositionFromGameObjectPositionAndDirection(
      { x: this._phaserGameObject.x, y: this._phaserGameObject.y },
      this._direction
    );
    const now = this._scene.time.now;
    if (now - this.#lastBump > 120) {
      this.#lastBump = now;
      this.#bumpCallback?.(target);
    }
  }

  /** @param {string} assetKey */
  setAppearance(assetKey) {
    this.#assetKey = assetKey;
    this._phaserGameObject.setTexture(assetKey, IDLE_FRAMES[this._direction]);
  }
}
