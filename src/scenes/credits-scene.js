import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { getSpecies } from '../battle/engine/monster.js';
import { inputManager } from '../input/input-manager.js';
import { readMenuInput, text, TEXT, ControlHints } from '../ui/ui-kit.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';

const SCROLL_SPEED = 34;
const END_OFFSET = 1000;
const END_POSITION = 230;
const END_PAUSE = 4500;
const SKIP_HOLD = 750;

export class CreditsScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.CREDITS_SCENE });
  }

  init() {
    super.init();
    this.finished = false;
    this.elapsed = 0;
    this.skipHeld = 0;
    this.lastTime = null;
  }

  create() {
    super.create();
    this.input.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => p.getDistance() < 24 && inputManager.tap('A'));
    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_CREDITS);
    // Narrow solid bands work in both Phaser's Canvas and WebGL renderers.
    const sky = this.add.graphics();
    for (let y = 0; y < 576; y += 4) {
      const ratio = y / 576;
      const red = Math.round(15 + ratio * 51);
      const green = Math.round(20 + ratio * 25);
      const blue = Math.round(48 + ratio * 54);
      sky.fillStyle((red << 16) | (green << 8) | blue, 1);
      sky.fillRect(0, y, 1024, 4);
    }
    this.stars = Array.from({ length: 64 }, (_, index) => {
      const x = (index * 167 + 43) % 1024;
      const y = (index * 97 + 21) % 414;
      return this.add.rectangle(x, y, index % 5 === 0 ? 4 : 2, index % 5 === 0 ? 4 : 2, 0xf8edcf);
    });
    this.roll = this.add.container(512, 576);
    const lines = [
      { y: 0, label: 'uru-mon', size: 60 },
      { y: 90, label: 'A Bengaluru adventure', size: 34 },
      { y: 260, label: 'CHAMPION', size: 30 },
      { y: 320, label: dataManager.state.player.name, size: 46 },
      { y: 500, label: 'With thanks to', size: 30 },
      { y: 560, label: 'Namma Bengaluru', size: 42 },
      { y: 640, label: 'And every Urumon by your side.', size: 28 },
      { y: END_OFFSET, label: 'THE END', size: 56 },
    ];
    lines.forEach((line) => {
      this.roll.add(text(this, 0, line.y, line.label, {
        ...TEXT.light, fontSize: `${line.size}px`, align: 'center', wordWrap: { width: 920 },
      }).setOrigin(0.5, 0));
    });
    // The parade stays in its own strip while the credits pass above it.
    this.add.rectangle(0, 416, 1024, 160, 0x231f3e).setOrigin(0);
    this.add.rectangle(0, 524, 1024, 52, 0x17172f).setOrigin(0);
    this.add.rectangle(0, 524, 1024, 4, 0x7e799e).setOrigin(0);
    this.marchers = dataManager.party.map((mon, index) => {
      const key = getSpecies(mon.speciesId).assetKey;
      return this.add.image(80 + index * 164, 524, this.textures.exists(key) ? key : '__MISSING')
        .setOrigin(0.5, 1).setScale(2);
    });
    new ControlHints(this, 512, 552, { align: 'center', dark: true }).set([{ btn: 'A', label: 'Hold to save and return' }]);
  }

  update(time) {
    super.update(time);
    if (!this._controls || this.finished) {
      return;
    }
    readMenuInput(this._controls);
    const delta = this.lastTime === null ? 0 : Math.max(0, time - this.lastTime);
    this.lastTime = time;
    this.elapsed += delta;
    this.skipHeld = inputManager.isDown('START') || inputManager.isDown('A') ? this.skipHeld + delta : 0;
    const scrollDuration = (576 + END_OFFSET - END_POSITION) / SCROLL_SPEED * 1000;
    this.roll.y = Math.max(END_POSITION - END_OFFSET, 576 - this.elapsed / 1000 * SCROLL_SPEED);
    this.stars.forEach((star, index) => star.setAlpha(0.35 + 0.65 * (1 + Math.sin(this.elapsed / 650 + index * 1.7)) / 2));
    this.marchers.forEach((sprite, index) => {
      sprite.x = ((160 + index * 164 + this.elapsed * 0.038) % 1184) - 80;
      sprite.y = 524 - Math.abs(Math.sin(this.elapsed / 170 + index)) * 8;
    });
    if (this.skipHeld >= SKIP_HOLD || this.elapsed >= scrollDuration + END_PAUSE) {
      this.#finish();
    }
  }

  #finish() {
    if (this.finished) {
      return;
    }
    this.finished = true;
    inputManager.consume('START');
    inputManager.consume('A');
    playSoundFx(this, AUDIO_KEYS.SFX_SAVE);
    dataManager.saveData();
    this.scene.start(SCENE_KEYS.TITLE_SCENE);
  }
}
