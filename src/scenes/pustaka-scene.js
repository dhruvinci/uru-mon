import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { gameData } from '../game/game-data.js';
import { getSpecies } from '../battle/engine/monster.js';
import { ListMenu, panel, readMenuInput, text, typeBadge, TEXT } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { monHdKey, upgradeWhenLoaded } from '../ui/hd-art.js';

/**
 * @typedef PustakaSceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {boolean} [browse] show every entry (from the title screen, before playing)
 */

export class PustakaScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.PUSTAKA_SCENE });
  }

  /** @param {PustakaSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    this.species = [...gameData.species].sort((a, b) => a.id - b.id);
    this.browse = Boolean(data.browse);
    const all = this.browse ? this.species.map((s) => s.id) : [];
    this.caught = new Set([...dataManager.state.pustaka.caught, ...all]);
    this.seen = new Set([...dataManager.state.pustaka.seen, ...this.caught]);
    this.showDetails = true;
    this.closing = false;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0x74aaa0).setOrigin(0);
    const pattern = this.add.graphics();
    pattern.fillStyle(0x85bbb0, 1);
    for (let y = 0; y < 576; y += 32) {
      pattern.fillRect(0, y, 1024, 8);
    }
    panel(this, 16, 14, 992, 76);
    text(this, 38, 28, 'Uru-Pustaka', 'title');
    const seenCount = this.species.filter((s) => this.seen.has(s.id)).length;
    const caughtCount = this.species.filter((s) => this.caught.has(s.id)).length;
    text(this, 978, 38, this.browse ? `ALL ${this.species.length} URUMON` : `SEEN ${seenCount} / CAUGHT ${caughtCount}`, 'body').setOrigin(1, 0);

    panel(this, 504, 104, 504, 416);
    this.entryName = text(this, 756, 116, '', 'body').setOrigin(0.5, 0);
    this.entryState = text(this, 756, 150, '', 'small').setOrigin(0.5, 0);
    this.portrait = this.add.image(600, 250, '__MISSING').setScale(2.1);
    this.unknown = text(this, 600, 250, '?', 'title').setOrigin(0.5);
    this.details = this.add.container(0, 0);
    this.detailHint = text(this, 756, 408, 'A: Show entry details', 'small').setOrigin(0.5, 0);
    this.list = new ListMenu(this, {
      x: 16,
      y: 104,
      width: 474,
      items: this.species.map((s) => `No.${String(s.id).padStart(3, '0')} ${this.seen.has(s.id) ? s.name : '-----'}`),
      visibleRows: 8,
      rowHeight: 46,
      style: 'small',
      onChange: () => this.#renderEntry(),
    });
    text(this, 36, 538, 'UP / DOWN: Browse', 'small');
    text(this, 988, 538, 'A: Toggle details    B: Back', 'small').setOrigin(1, 0);
    this.#renderEntry();
  }

  #renderEntry() {
    this.details.removeAll(true);
    this.details.setVisible(this.showDetails);
    this.detailHint.setVisible(!this.showDetails);
    const entry = this.species[this.list.index];
    if (!entry) {
      this.entryName.setText('No entries yet');
      this.entryState.setText('Explore Bengaluru to meet Urumon.');
      this.portrait.setVisible(false);
      this.unknown.setVisible(false);
      this.detailHint.setVisible(false);
      return;
    }
    const caught = this.caught.has(entry.id);
    const seen = this.seen.has(entry.id);
    this.entryName.setText(`No.${String(entry.id).padStart(3, '0')} ${seen ? entry.name : '-----'}`);
    this.entryState.setText(this.browse ? '' : caught ? 'CAUGHT' : seen ? 'SEEN' : 'NOT YET SEEN');
    this.portrait.setVisible(seen).clearTint();
    this.unknown.setVisible(!seen);
    if (seen) {
      const key = getSpecies(entry.id).assetKey;
      this.portrait.setTexture(this.textures.exists(key) ? key : '__MISSING').setScale(2.1);
      upgradeWhenLoaded(this.portrait, key, monHdKey(entry.id));
      if (!caught) {
        this.portrait.setTintFill(0x000000);
      }
    }
    const small = (x, y, str, width) => text(this, x, y, str, { ...TEXT.small, fontSize: '18px', wordWrap: { width }, lineSpacing: 2 });
    if (!caught) {
      this.details.add(small(700, 200, seen ? 'Catch this Urumon to record its types and story.' : 'An undiscovered Urumon. Keep exploring!', 290));
      return;
    }
    entry.types.forEach((type, i) => {
      this.details.add(typeBadge(this, 700 + i * 130, 180, type, 1.1));
    });
    const found = small(700, 214, `Found: ${(entry.habitat || []).slice(0, 3).join(', ') || 'unknown'}`, 290);
    this.details.add(found);
    const next = entry.evolution && gameData.species.find((s) => s.id === entry.evolution.speciesId);
    if (next) {
      this.details.add(small(700, found.y + found.height + 8, `Evolves into ${next.name} at Lv ${entry.evolution.level}`, 290));
    }
    const dex = small(526, 338, entry.dex, 460);
    this.details.add(dex);
    if (entry.ref) {
      this.details.add(small(526, dex.y + dex.height + 10, `In Bengaluru: ${entry.ref}`, 460).setColor('#4b3f7a'));
    }
  }

  /** @param {number} time */
  update(time) {
    super.update(time);
    if (!this._controls || this.closing) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    const previousIndex = this.list.index;
    const result = this.list.handleInput(input);
    if (result?.type === 'cancel') {
      this.closing = true;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.scene.stop();
      this.scene.resume(this.sceneData.previousSceneName, {});
      return;
    }
    if (result?.type === 'select') {
      this.showDetails = !this.showDetails;
      this.#renderEntry();
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    } else if (previousIndex !== this.list.index) {
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    }
  }
}
