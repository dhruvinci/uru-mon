import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { panel, readMenuInput, text } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { inputManager } from '../input/input-manager.js';

/**
 * @typedef TrainerCardSceneData
 * @type {object}
 * @property {string} previousSceneName
 */

const BADGES = [
  { type: 'GRASS', color: 0x58a858 },
  { type: 'FIGHT', color: 0xd86c50 },
  { type: 'ELECTRIC', color: 0xe8bb38 },
  { type: 'MIND', color: 0xdc70a0 },
  { type: 'SPIRIT', color: 0x8068bc },
  { type: 'SKY', color: 0x60b8d8 },
];

export class TrainerCardScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.TRAINER_CARD_SCENE });
  }

  /** @param {TrainerCardSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    this.keyPressed = false;
    this.closing = false;
  }

  create() {
    super.create();
    this.input.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => p.getDistance() < 24 && inputManager.tap('A'));
    this.add.rectangle(0, 0, 1024, 576, 0x7866a4).setOrigin(0);
    const pattern = this.add.graphics();
    pattern.fillStyle(0x8a78b6, 1);
    for (let y = 0; y < 576; y += 32) {
      for (let x = (y / 32) % 2 ? 0 : 32; x < 1024; x += 64) {
        pattern.fillRect(x, y, 32, 32);
      }
    }
    panel(this, 52, 28, 920, 496, { fill: 0xfff6df, inner: 0xd8b878 });
    text(this, 88, 52, 'TRAINER CARD', 'title');
    text(this, 936, 66, 'NAMMA BENGALURU', 'small').setOrigin(1, 0);
    const rule = this.add.graphics();
    rule.fillStyle(0xd8b878, 1);
    rule.fillRect(88, 110, 848, 4);
    rule.fillRect(88, 338, 848, 4);

    const player = dataManager.state.player;
    const rows = [
      ['NAME', player.name],
      ['MONEY', `₹${player.money}`],
      ['PUSTAKA', `${new Set(dataManager.state.pustaka.caught).size} caught`],
      ['PLAY TIME', this.#playTime()],
    ];
    rows.forEach(([label, value], i) => {
      text(this, 100, 134 + i * 48, label, 'small');
      const valueText = text(this, 320, 128 + i * 48, value, 'body');
      if (i === 3) {
        this.playTimeText = valueText;
      }
    });

    panel(this, 724, 128, 196, 194, { fill: 0xc8e0cc, inner: 0x89b89c });
    const key = `CHAR_player_${player.gender}`;
    // 16x32 overworld frame at 5x fits the 194-px-tall panel with a margin.
    this.add.image(822, 224, this.textures.exists(key) ? key : '__MISSING', 0).setScale(5);
    text(this, 100, 350, 'ARENA BADGES', 'small');
    BADGES.forEach((badge, i) => this.#drawBadge(159 + i * 141, 432, badge, player.badges.includes(badge.type)));
    text(this, 512, 542, 'Press any key or game button to close', 'small').setOrigin(0.5, 0);

    // Menu input covers touch controls; this listener also handles unmapped keyboard keys.
    this.onAnyKey = (event) => {
      if (!event.repeat) {
        this.keyPressed = true;
      }
    };
    // Phaser's keyboard plugin is disabled; the shared controls use window events too.
    window.addEventListener('keydown', this.onAnyKey);
    this.events.once('shutdown', () => {
      window.removeEventListener('keydown', this.onAnyKey);
    });
  }

  /** @returns {string} */
  #playTime() {
    const minutes = Math.floor(Math.max(0, dataManager.getPlayTimeSeconds()) / 60);
    return `${Math.floor(minutes / 60)}:${String(minutes % 60).padStart(2, '0')}`;
  }

  /**
   * @param {number} x
   * @param {number} y
   * @param {{type: string, color: number}} badge
   * @param {boolean} earned
   */
  #drawBadge(x, y, badge, earned) {
    const gem = this.add.graphics();
    gem.fillStyle(0x3a3058, 1);
    gem.fillPoints([
      { x, y: y - 36 }, { x: x + 34, y: y - 10 }, { x: x + 22, y: y + 24 },
      { x, y: y + 36 }, { x: x - 22, y: y + 24 }, { x: x - 34, y: y - 10 },
    ], true);
    gem.fillStyle(earned ? badge.color : 0xa6a4aa, 1);
    gem.fillPoints([
      { x, y: y - 29 }, { x: x + 27, y: y - 8 }, { x: x + 17, y: y + 19 },
      { x, y: y + 29 }, { x: x - 17, y: y + 19 }, { x: x - 27, y: y - 8 },
    ], true);
    gem.fillStyle(earned ? 0xffffff : 0xc5c3c8, earned ? 0.55 : 0.35);
    gem.fillTriangle(x, y - 24, x - 22, y - 7, x, y + 12);
    gem.lineStyle(2, 0x3a3058, 0.35);
    gem.lineBetween(x, y - 26, x, y + 25);
    text(this, x, 478, badge.type, 'small').setOrigin(0.5, 0);
  }

  /** @param {number} time */
  update(time) {
    super.update(time);
    if (!this._controls || this.closing) {
      return;
    }
    const input = readMenuInput(this._controls);
    const start = this._controls.wasEnterKeyPressed();
    this.playTimeText.setText(this.#playTime());
    if (!input && !start && !this.keyPressed) {
      return;
    }
    this.closing = true;
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    this.scene.stop();
    this.scene.resume(this.sceneData.previousSceneName, {});
  }
}
