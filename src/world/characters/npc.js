import Phaser from '../../lib/phaser.js';
import { Character } from './character.js';
import { DIRECTION } from '../../common/direction.js';
import { IDLE_FRAMES } from './player.js';

/**
 * @typedef {keyof typeof NPC_MOVEMENT_PATTERN} NpcMovementPattern
 */

/** @enum {NpcMovementPattern} */
export const NPC_MOVEMENT_PATTERN = Object.freeze({
  IDLE: 'IDLE',
  LOOK: 'LOOK',
  WANDER: 'WANDER',
  CLOCKWISE: 'CLOCKWISE',
  SET_PATH: 'SET_PATH',
});

/**
 * @typedef NPCPath
 * @type {Object.<number, import('../../types/typedef.js').Coordinate>}
 */

/**
 * @typedef NPCConfigProps
 * @type {object}
 * @property {string} assetKey CHAR_* spritesheet
 * @property {NPCPath} [npcPath]
 * @property {NpcMovementPattern} movementPattern
 * @property {string} id
 * @property {any} [data] the map's NPC definition (script, trainer, ...)
 */

/**
 * @typedef {Omit<import('./character').CharacterConfig, 'idleFrameConfig'> & NPCConfigProps} NPCConfig
 */

const DIRS = [DIRECTION.UP, DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT];
const OPPOSITE = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT', NONE: 'NONE' };

export class NPC extends Character {
  #talkingToPlayer = false;
  /** @type {NPCPath} */
  #npcPath;
  #currentPathIndex = 0;
  /** @type {NpcMovementPattern} */
  #movementPattern;
  #lastMovementTime;
  #assetKey;
  #id;
  #home;
  /** @type {any} */
  data;
  frozen = false;

  /**
   * @param {NPCConfig} config
   */
  constructor(config) {
    super({
      ...config,
      origin: { x: 0, y: 1 / 3 },
      idleFrameConfig: IDLE_FRAMES,
    });
    this.#npcPath = config.npcPath || { 0: { ...config.position } };
    this.#movementPattern = config.movementPattern;
    this.#lastMovementTime = Phaser.Math.Between(1500, 4000);
    this.#assetKey = config.assetKey;
    this.#id = config.id;
    this.#home = { ...config.position };
    this.data = config.data || {};
  }

  /** @type {string} */
  get id() {
    return this.#id;
  }

  get isTalkingToPlayer() {
    return this.#talkingToPlayer;
  }

  set isTalkingToPlayer(val) {
    this.#talkingToPlayer = val;
  }

  get npcPath() {
    return this.#npcPath;
  }

  set npcPath(val) {
    this.#npcPath = val;
    this.#currentPathIndex = 0;
  }

  /** @param {NpcMovementPattern} val */
  set npcMovementPattern(val) {
    this.#movementPattern = val;
  }

  set finishedMovementCallback(val) {
    this._spriteGridMovementFinishedCallback = val;
  }

  resetMovementTime() {
    this.#lastMovementTime = 0;
  }

  /**
   * Turn to look at the player, given the direction the player is facing.
   * @param {import('../../common/direction.js').Direction} playerDirection
   */
  facePlayer(playerDirection) {
    this.face(/** @type {any} */ (OPPOSITE[playerDirection]));
  }

  /**
   * Walks a list of steps; resolves when finished.
   * @param {import('../../common/direction.js').Direction[]} steps
   * @param {boolean} [ignoreCollisions=false]
   * @returns {Promise<void>}
   */
  walk(steps, ignoreCollisions = false) {
    return new Promise((resolve) => {
      const queue = [...steps];
      const prevPattern = this.#movementPattern;
      this.#movementPattern = NPC_MOVEMENT_PATTERN.IDLE;
      const next = () => {
        if (queue.length === 0) {
          this._spriteGridMovementFinishedCallback = undefined;
          this.#movementPattern = prevPattern === NPC_MOVEMENT_PATTERN.SET_PATH ? NPC_MOVEMENT_PATTERN.IDLE : prevPattern;
          this.#home = { ...this._targetPosition };
          this.update(0);
          resolve();
          return;
        }
        const dir = queue.shift();
        this._spriteGridMovementFinishedCallback = next;
        if (ignoreCollisions) {
          const saved = this._collisionLayer;
          const savedChars = this._otherCharactersToCheckForCollisionsWith;
          this._collisionLayer = undefined;
          this._otherCharactersToCheckForCollisionsWith = [];
          this.moveCharacter(dir);
          this._collisionLayer = saved;
          this._otherCharactersToCheckForCollisionsWith = savedChars;
        } else {
          this.moveCharacter(dir);
        }
        if (!this._isMoving) {
          // blocked: give up on this step
          this.face(dir);
          this._scene.time.delayedCall(10, next);
        }
      };
      next();
    });
  }

  /** @param {DOMHighResTimeStamp} time */
  update(time) {
    if (this._isMoving) {
      return;
    }
    super.update(time);
    if (this.#talkingToPlayer || this.frozen) {
      return;
    }
    if (this.#lastMovementTime > time) {
      return;
    }
    switch (this.#movementPattern) {
      case NPC_MOVEMENT_PATTERN.LOOK:
        this.face(DIRS[Phaser.Math.Between(0, 3)]);
        this.#lastMovementTime = time + Phaser.Math.Between(1500, 4000);
        return;
      case NPC_MOVEMENT_PATTERN.WANDER: {
        const dir = DIRS[Phaser.Math.Between(0, 3)];
        const d = { UP: [0, -1], DOWN: [0, 1], LEFT: [-1, 0], RIGHT: [1, 0] }[dir];
        const nx = this._targetPosition.x + d[0] * 64;
        const ny = this._targetPosition.y + d[1] * 64;
        const radius = (this.data.wanderRadius ?? 2) * 64;
        if (Math.abs(nx - this.#home.x) <= radius && Math.abs(ny - this.#home.y) <= radius) {
          this.moveCharacter(dir);
        } else {
          this.face(dir);
        }
        this.#lastMovementTime = time + Phaser.Math.Between(1800, 4200);
        return;
      }
      case NPC_MOVEMENT_PATTERN.CLOCKWISE: {
        const keys = Object.keys(this.#npcPath).map(Number).sort((a, b) => a - b);
        if (keys.length < 2) {
          return;
        }
        const target = this.#npcPath[keys[(this.#currentPathIndex + 1) % keys.length]];
        const cur = this._targetPosition;
        let dir = DIRECTION.NONE;
        if (target.x > cur.x) dir = DIRECTION.RIGHT;
        else if (target.x < cur.x) dir = DIRECTION.LEFT;
        else if (target.y > cur.y) dir = DIRECTION.DOWN;
        else if (target.y < cur.y) dir = DIRECTION.UP;
        if (dir === DIRECTION.NONE) {
          this.#currentPathIndex = (this.#currentPathIndex + 1) % keys.length;
          return;
        }
        this.moveCharacter(dir);
        this.#lastMovementTime = time + 500;
        return;
      }
      default:
    }
  }

  /**
   * @param {import('../../common/direction.js').Direction} direction
   */
  moveCharacter(direction) {
    super.moveCharacter(direction);
    if (!this._isMoving) {
      return;
    }
    const key = `${this.#assetKey}_${this._direction}`;
    if (!this._phaserGameObject.anims.isPlaying || this._phaserGameObject.anims.currentAnim?.key !== key) {
      this._phaserGameObject.play(key);
    }
  }
}
