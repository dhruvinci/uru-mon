import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { gameData, getMapInfo } from '../game/game-data.js';
import { REGION, REGION_ROADS } from '../game/region.js';
import { panel, readMenuInput, text, TEXT, ControlHints } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';

/**
 * @typedef RegionMapSceneData
 * @type {object}
 * @property {string} previousSceneName
 */

const KIND_COLORS = {
  home: 0xe8584a, town: 0xf2a33a, route: 0xd8c690, park: 0x58a858, lake: 0x4a8fd8, hill: 0x9a7a5a,
  landmark: 0xb47ad8, wild: 0x3f7f4a,
};

/** A browsable map of every place in the game, with the real Bengaluru place behind each one. */
export class RegionMapScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.REGION_MAP_SCENE });
  }

  /** @param {RegionMapSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    // only places that exist as maps (the expansion areas may not be built yet)
    this.places = REGION.filter((p) => getMapInfo(p.id));
    this.index = 0;
    this.closing = false;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0x3d6b5c).setOrigin(0);
    text(this, 32, 20, 'BENGALURU', 'title').setColor('#fff4d6');
    new ControlHints(this, 994, 46, { backing: true }).set([{ key: '▲▼', label: 'Places' }, { btn: 'B', label: 'Back' }]);

    // the stylised map
    panel(this, 16, 80, 512, 488, { fill: 0xe9dfc2 });
    const g = this.add.graphics();
    g.fillStyle(0xcfdcaa, 1).fillRoundedRect(28, 92, 488, 464, 10);
    g.fillStyle(0xb9cf8f, 1).fillEllipse(270, 130, 150, 90).fillEllipse(300, 548, 170, 40).fillEllipse(80, 500, 120, 90);
    g.fillStyle(0x9fc6e6, 1).fillEllipse(445, 432, 70, 34).fillEllipse(180, 246, 36, 20).fillEllipse(296, 196, 44, 22)
      .fillEllipse(270, 430, 22, 14).fillEllipse(52, 452, 30, 18);
    g.fillStyle(0x88b36e, 1).fillCircle(262, 418, 16).fillCircle(300, 352, 18);
    const at = (id) => REGION.find((p) => p.id === id);
    g.lineStyle(5, 0xf6efd6, 1);
    REGION_ROADS.forEach(([a, b]) => {
      const pa = at(a);
      const pb = at(b);
      if (pa && pb && getMapInfo(a) && getMapInfo(b)) {
        g.lineBetween(pa.x, pa.y, pb.x, pb.y);
      }
    });
    this.nodes = this.places.map((p) => {
      const node = this.add.circle(p.x, p.y, p.kind === 'route' ? 6 : 9, KIND_COLORS[p.kind]).setStrokeStyle(3, 0x2d2a3a);
      return node;
    });
    // tap a place on the map to read about it
    this.add.zone(28, 92, 488, 464).setOrigin(0).setInteractive().on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => {
      if (p.getDistance() > 24) {
        return;
      }
      let best = -1;
      let bestD = 40 * 40;
      this.places.forEach((pl, i) => {
        const d = (pl.x - p.x) ** 2 + (pl.y - p.y) ** 2;
        if (d < bestD) {
          bestD = d;
          best = i;
        }
      });
      if (best >= 0 && best !== this.index) {
        this.index = best;
        playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
        this.#show();
      }
    });
    this.marker = this.add.circle(0, 0, 16).setStrokeStyle(4, 0xffffff);
    this.tweens.add({ targets: this.marker, scale: 1.25, duration: 500, yoyo: true, repeat: -1 });
    this.label = text(this, 0, 0, '', 'small').setOrigin(0.5, 1).setBackgroundColor('#2d2a3add').setColor('#ffffff').setPadding(6, 2);

    // details
    panel(this, 540, 80, 468, 488);
    this.title = text(this, 562, 94, '', 'body');
    this.kind = text(this, 986, 100, '', 'small').setOrigin(1, 0);
    this.previewFrame = this.add.rectangle(562, 136, 424, 184, 0x2d2a3a).setOrigin(0);
    this.preview = this.add.image(774, 228, '__MISSING').setVisible(false);
    this.loading = text(this, 774, 228, 'Loading map...', 'lightSmall').setOrigin(0.5);
    this.blurb = text(this, 562, 332, '', { ...TEXT.small, fontSize: '20px', wordWrap: { width: 424 }, lineSpacing: 3 });
    this.extra = text(this, 562, 450, '', { ...TEXT.small, fontSize: '18px', wordWrap: { width: 424 }, lineSpacing: 2 }).setColor('#4b3f7a');
    this.#show();
  }

  #show() {
    const place = this.places[this.index];
    if (!place) {
      return;
    }
    this.marker.setPosition(place.x, place.y);
    this.label.setText(place.name).setPosition(place.x, place.y - 16);
    this.title.setText(place.name);
    this.kind.setText(place.kind === 'home' ? 'HOME TOWN' : place.kind.toUpperCase());
    this.blurb.setText(place.blurb);
    const name = getMapInfo(place.id)?.name || place.name;
    const here = gameData.species.filter((s) => (s.habitat || []).some((h) => h.startsWith(name))).map((s) => s.name);
    const lines = [];
    if (place.arena) {
      lines.push(`Arena: ${place.arena}`);
    }
    if (here.length) {
      lines.push(`Urumon here: ${here.slice(0, 6).join(', ')}${here.length > 6 ? ` and ${here.length - 6} more` : ''}`);
    }
    this.extra.setText(lines.join('\n'));
    this.extra.setY(this.blurb.y + this.blurb.height + 12);
    this.#loadPreview(place.id);
  }

  /** @param {string} id */
  #loadPreview(id) {
    const key = `REGION_PREVIEW_${id}`;
    const apply = () => {
      if (this.places[this.index]?.id !== id || !this.textures.exists(key)) {
        return;
      }
      const tex = this.textures.get(key).getSourceImage();
      const scale = Math.min(424 / tex.width, 184 / tex.height);
      this.preview.setTexture(key).setScale(scale).setVisible(true);
      this.loading.setVisible(false);
    };
    if (this.textures.exists(key)) {
      apply();
      return;
    }
    this.preview.setVisible(false);
    this.loading.setVisible(true);
    this.load.image(key, `assets/maps/${id}/bg.png`);
    this.load.once('complete', apply);
    this.load.start();
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
    if (input === 'CANCEL') {
      this.closing = true;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.scene.stop();
      this.scene.resume(this.sceneData.previousSceneName, {});
      return;
    }
    const step = input === 'DOWN' || input === 'RIGHT' ? 1 : input === 'UP' || input === 'LEFT' ? -1 : 0;
    if (step) {
      this.index = (this.index + step + this.places.length) % this.places.length;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.#show();
    }
  }
}
