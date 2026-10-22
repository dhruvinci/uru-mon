import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { getSpecies } from '../battle/engine/monster.js';
import { ListMenu, panel, readMenuInput, text, typeBadge, TEXT } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { bestArt, monHdKey, HD_FACTOR } from '../ui/hd-art.js';
import Phaser from '../lib/phaser.js';

/**
 * @typedef StarterSceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {number[]} [options] species ids to choose from
 */

const BLURBS = {
  1: 'The jacaranda fawn. It grows into a mystic stag whose antlers bloom all year round.',
  4: 'The filter-coffee pup. It grows into a steel-crowned wolf king of the darshinis.',
  7: 'The tender-coconut turtle. It grows into a giant whose shell is a whole temple tank.',
};
const GLOW = { GRASS: 0x7ac74c, FIRE: 0xee8130, WATER: 0x6390f0 };
const SLOTS = [212, 512, 812];

/** Prof. Sharada's table: the three starters side by side, with the chosen one's whole evolution line. */
export class StarterScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.STARTER_SCENE });
  }

  /** @param {StarterSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    this.options = data.options || [1, 4, 7];
    this.index = 1;
    /** @type {ListMenu | null} */
    this.confirm = null;
    this.done = false;
  }

  /** The HD pictures of all three lines, so the first look at them is sharp. */
  preload() {
    const ids = [];
    this.options.forEach((id) => {
      for (let sp = getSpecies(id); sp; sp = sp.evolution ? getSpecies(sp.evolution.speciesId) : null) {
        ids.push(sp.id);
      }
    });
    ids.map(monHdKey).filter((k) => !this.textures.exists(k))
      .forEach((k) => this.load.image(k, `assets/images/creatures_hd/${k.slice('MONHD_'.length)}.webp`));
  }

  /** @param {number} speciesId @param {number} lowScale */
  #art(speciesId, lowScale) {
    const key = monHdKey(speciesId);
    if (this.textures.exists(key)) {
      this.textures.get(key).setFilter(Phaser.Textures.FilterMode.LINEAR);
    }
    return bestArt(this, getSpecies(speciesId).assetKey, key, lowScale);
  }

  create() {
    super.create();
    this.bg = this.add.rectangle(0, 0, 1024, 576, 0x221a3a).setOrigin(0);
    this.glow = this.add.graphics();
    text(this, 512, 18, "Prof. Sharada's Urumon", 'title').setOrigin(0.5, 0).setColor('#fff4d6');
    text(this, 512, 70, 'Choose your partner', 'lightSmall').setOrigin(0.5, 0).setAlpha(0.85);

    if (!this.textures.exists('STARTER_SPARK')) {
      const g = this.make.graphics({ x: 0, y: 0 }, false);
      g.fillStyle(0xffffff, 1).fillCircle(4, 4, 4);
      g.generateTexture('STARTER_SPARK', 8, 8);
      g.destroy();
    }
    this.cards = this.options.map((id, i) => {
      const sp = getSpecies(id);
      const x = SLOTS[i];
      const table = this.add.ellipse(x, 300, 210, 46, 0x000000, 0.35);
      const art = this.#art(id, 2.4);
      const img = this.add.image(x, 290, art.key).setOrigin(0.5, 1).setScale(art.scale);
      const name = text(this, x, 306, sp.name, 'body').setOrigin(0.5, 0).setColor('#fff4d6');
      // scale factor relative to the 64 px pixel sprite: 1, or 1/4 for the HD picture
      const unit = art.key.startsWith('MONHD_') ? 1 / HD_FACTOR : 1;
      return { id, sp, x, table, img, name, unit };
    });
    this.sparks = this.add.particles(0, 0, 'STARTER_SPARK', {
      lifespan: 900, speed: { min: 20, max: 70 }, scale: { start: 0.8, end: 0 }, alpha: { start: 0.9, end: 0 },
      frequency: 90, emitting: true,
    });

    panel(this, 24, 360, 976, 204);
    this.typeHolder = this.add.container(0, 0);
    this.blurb = text(this, 48, 378, '', { ...TEXT.small, wordWrap: { width: 470 }, lineSpacing: 4 });
    text(this, 756, 374, 'Grows into', 'small').setOrigin(0.5, 0);
    this.line = this.add.container(0, 0);
    this.hint = text(this, 512, 540, 'LEFT / RIGHT: Look    A: Choose', 'small').setOrigin(0.5, 0);
    this.#select(this.index, true);
  }

  /** @param {number} index @param {boolean} [instant] */
  #select(index, instant = false) {
    this.index = index;
    const current = this.cards[index];
    const type = current.sp.types[0];
    this.glow.clear();
    this.glow.fillStyle(GLOW[type] ?? 0xffffff, 0.22).fillEllipse(current.x, 220, 330, 300);
    this.glow.fillStyle(GLOW[type] ?? 0xffffff, 0.12).fillEllipse(current.x, 220, 470, 420);
    this.cards.forEach((card, i) => {
      const on = i === index;
      this.tweens.killTweensOf(card.img);
      card.img.setY(290);
      this.tweens.add({ targets: card.img, scale: (on ? 3.1 : 2.2) * card.unit, duration: instant ? 1 : 220, ease: 'Back.out' });
      card.img.setAlpha(on ? 1 : 0.55);
      card.name.setAlpha(on ? 1 : 0.6);
      if (on) {
        this.tweens.add({ targets: card.img, y: 280, duration: 520, yoyo: true, repeat: -1, ease: 'Sine.inOut', delay: 220 });
      }
    });
    this.sparks.setPosition(current.x, 200);
    this.sparks.particleTint = GLOW[type] ?? 0xffffff;

    this.typeHolder.removeAll(true);
    this.typeHolder.add(typeBadge(this, 48, 500, type, 1));
    this.typeHolder.add(text(this, 170, 502, `${current.sp.name}`, 'body'));
    this.blurb.setText(BLURBS[current.id] || current.sp.dex);

    // the whole evolution line
    this.line.removeAll(true);
    const chain = [current.sp];
    while (chain[chain.length - 1].evolution) {
      chain.push(getSpecies(chain[chain.length - 1].evolution.speciesId));
    }
    const stages = chain.slice(1);
    stages.forEach((sp, i) => {
      const x = 660 + i * 190;
      const art = this.#art(sp.id, 1.5);
      this.line.add(this.add.image(x, 486, art.key).setOrigin(0.5, 1).setScale(art.scale));
      this.line.add(text(this, x, 490, sp.name, { ...TEXT.small, fontSize: '18px' }).setOrigin(0.5, 0));
      if (i > 0) {
        this.line.add(text(this, x - 95, 440, '→', 'body').setOrigin(0.5));
      }
    });
  }

  /** @param {number} time */
  update(time) {
    super.update(time);
    if (!this._controls || this.done) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.confirm) {
      const r = this.confirm.handleInput(input);
      if (!r) {
        return;
      }
      this.confirm.destroy();
      this.confirm = null;
      this.prompt.destroy();
      this.hint.setVisible(true);
      if (r.type === 'select' && r.index === 0) {
        this.done = true;
        playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
        this.cameras.main.flash(300, 255, 255, 255);
        this.time.delayedCall(350, () => {
          this.scene.stop();
          this.scene.resume(this.sceneData.previousSceneName, { species: this.options[this.index] });
        });
      }
      return;
    }
    if (input === 'LEFT' || input === 'RIGHT') {
      const next = (this.index + (input === 'RIGHT' ? 1 : -1) + this.options.length) % this.options.length;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.#select(next);
      return;
    }
    if (input === 'OK') {
      const sp = this.cards[this.index].sp;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.hint.setVisible(false);
      this.prompt = text(this, 512, 536, `Choose ${sp.name}, the ${sp.types[0]} type?`, 'small').setOrigin(0.5, 0);
      this.confirm = new ListMenu(this, { x: 1000 - 180, y: 380, width: 160, items: ['YES', 'NO'], depth: 20 });
    }
  }
}
