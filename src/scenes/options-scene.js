import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { dataManager } from '../utils/data-manager.js';
import { panel, readMenuInput, text, cursor, MessageBox } from '../ui/ui-kit.js';
import { setGlobalSoundSettings, playBackgroundMusic, currentMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { graphicsSetting } from '../fx/world-fx.js';

const ROWS = [
  { key: 'textSpeed', label: 'TEXT SPEED', values: ['SLOW', 'MID', 'FAST'], help: 'How fast dialog text appears.' },
  { key: 'battleSceneAnimations', label: 'BATTLE ANIMS', values: ['ON', 'OFF'], help: 'Turn off to make battles quicker.' },
  { key: 'sound', label: 'SOUND', values: ['ON', 'OFF'], help: 'Music and sound effects.' },
  { key: 'volume', label: 'VOLUME', values: [0, 1, 2, 3, 4], help: 'Master volume.' },
  {
    key: 'graphics', label: 'GRAPHICS', values: ['HD-2D', 'ENHANCED', 'CLASSIC'],
    help: 'HD-2D: tilted camera, depth of field, light and weather. ENHANCED: light and weather only. CLASSIC: the original flat look. Applies on the next map.',
  },
  { key: 'close', label: 'CLOSE', values: [], help: 'Save options and go back.' },
];

export class OptionsScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.OPTIONS_SCENE });
  }

  /** @param {{previousSceneName: string}} data */
  init(data) {
    super.init();
    this.sceneData = data || { previousSceneName: SCENE_KEYS.TITLE_SCENE };
    this.index = 0;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0x2a2050, 0.92).setOrigin(0);
    panel(this, 112, 40, 800, 380);
    text(this, 512, 62, 'OPTIONS', 'title').setOrigin(0.5, 0);
    this.valueTexts = ROWS.map((row, i) => {
      text(this, 200, 130 + i * 54, row.label, 'body');
      return text(this, 820, 130 + i * 54, '', 'body').setOrigin(1, 0);
    });
    this.cur = cursor(this);
    this.help = new MessageBox(this, { y: 432, height: 144 });
    this.#render();
  }

  #render() {
    const o = dataManager.state.options;
    ROWS.forEach((row, i) => {
      if (row.key === 'close') {
        this.valueTexts[i].setText('');
        return;
      }
      const v = row.key === 'graphics' ? graphicsSetting() : o[row.key];
      this.valueTexts[i].setText(`◀ ${v} ▶`).setColor(i === this.index ? '#c4404a' : '#2d2a3a');
    });
    this.cur.setPosition(170, 140 + this.index * 54);
    this.help.setText(ROWS[this.index].help);
  }

  update(time) {
    super.update(time);
    if (!this._controls) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    const row = ROWS[this.index];
    if (input === 'UP' || input === 'DOWN') {
      this.index = (this.index + (input === 'UP' ? ROWS.length - 1 : 1)) % ROWS.length;
    } else if ((input === 'LEFT' || input === 'RIGHT') && row.values.length) {
      const o = dataManager.state.options;
      const i = row.values.indexOf(row.key === 'graphics' ? graphicsSetting() : o[row.key]);
      const next = row.values[(i + (input === 'LEFT' ? row.values.length - 1 : 1)) % row.values.length];
      o[row.key] = next;
      if (row.key === 'sound' || row.key === 'volume') {
        setGlobalSoundSettings(this);
        if (row.key === 'sound' && next === 'ON' && currentMusic()) {
          playBackgroundMusic(this, currentMusic(), { restart: true });
        }
        playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      }
    } else if (input === 'CANCEL' || (input === 'OK' && row.key === 'close')) {
      dataManager.saveOptions();
      this.scene.stop();
      this.scene.resume(this.sceneData.previousSceneName, {});
      return;
    }
    this.#render();
  }
}
