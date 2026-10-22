import Phaser from '../lib/phaser.js';
import { DATA_ASSET_KEYS } from '../assets/asset-keys.js';
import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { dataManager } from '../utils/data-manager.js';
import { setGlobalSoundSettings } from '../utils/audio-utils.js';
import { initGameData } from '../game/game-data.js';
import { FONT } from '../ui/ui-kit.js';

const DIRS = ['DOWN', 'UP', 'LEFT', 'RIGHT'];

export class PreloadScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.PRELOAD_SCENE });
  }

  preload() {
    super.preload();
    this.load.json(DATA_ASSET_KEYS.MANIFEST, 'assets/manifest.json');
    this.load.json(DATA_ASSET_KEYS.SPECIES, 'assets/data/species.json');
    this.load.json(DATA_ASSET_KEYS.MOVES, 'assets/data/moves.json');
    this.load.json(DATA_ASSET_KEYS.ITEMS, 'assets/data/items.json');
    this.load.json(DATA_ASSET_KEYS.MAPS, 'assets/maps/index.json');
    this.load.json(DATA_ASSET_KEYS.TRAINERS, 'assets/data/trainers.json');
  }

  create() {
    super.create();
    document.getElementById('boot')?.remove();
    const { width, height } = this.scale;
    const label = this.add.text(width / 2, height / 2 - 40, 'Loading Bengaluru...', { fontFamily: 'monospace', fontSize: '28px', color: '#cbb8ff' }).setOrigin(0.5);
    const barBg = this.add.rectangle(width / 2, height / 2 + 10, 520, 26, 0x3a3058).setOrigin(0.5);
    const bar = this.add.rectangle(width / 2 - 256, height / 2 + 10, 0, 18, 0xc4a8ff).setOrigin(0, 0.5);
    this.load.on('progress', (p) => bar.setSize(512 * p, 18));

    const manifest = this.cache.json.get(DATA_ASSET_KEYS.MANIFEST) || {};
    (manifest.images || []).forEach((a) => this.load.image(a.key, a.url));
    (manifest.spritesheets || []).forEach((a) => this.load.spritesheet(a.key, a.url, { frameWidth: a.frameWidth, frameHeight: a.frameHeight }));
    (manifest.maps || []).forEach((m) => {
      this.load.tilemapTiledJSON(m.key, m.url);
      this.load.image(`${m.key}_BG`, m.bg);
      if (m.fg) {
        this.load.image(`${m.key}_FG`, m.fg);
      }
    });
    (manifest.audio || []).forEach((a) => this.load.audio(a.key, a.urls));

    this.load.once('complete', async () => {
      try {
        await Promise.race([document.fonts.load(`30px ${FONT}`), new Promise((r) => setTimeout(r, 2500))]);
      } catch {
        /* fall back to default font */
      }
      initGameData({
        species: this.cache.json.get(DATA_ASSET_KEYS.SPECIES),
        moves: this.cache.json.get(DATA_ASSET_KEYS.MOVES),
        items: this.cache.json.get(DATA_ASSET_KEYS.ITEMS),
        maps: this.cache.json.get(DATA_ASSET_KEYS.MAPS) || [],
        trainers: this.cache.json.get(DATA_ASSET_KEYS.TRAINERS) || {},
      });
      this.#createCharacterAnimations(manifest);
      dataManager.loadData();
      setGlobalSoundSettings(this);
      label.destroy();
      barBg.destroy();
      bar.destroy();
      const params = new URLSearchParams(window.location.search);
      if (params.get('scene') === 'test') {
        this.scene.start(SCENE_KEYS.TEST_SCENE);
        return;
      }
      this.scene.start(SCENE_KEYS.TITLE_SCENE);
    });
    this.load.start();
  }

  /**
   * Every CHAR_* sheet is 3 columns (stand, step A, step B) x 4 rows (down, up, left, right).
   * Walk animations play step A, stand, step B, stand; frames[1] is the idle frame Character expects.
   * @param {any} manifest
   */
  #createCharacterAnimations(manifest) {
    (manifest.spritesheets || [])
      .filter((s) => s.key.startsWith('CHAR_'))
      .forEach((s) => {
        DIRS.forEach((dir, row) => {
          const base = row * 3;
          this.anims.create({
            key: `${s.key}_${dir}`,
            frames: this.anims.generateFrameNumbers(s.key, { frames: [base + 1, base, base + 2, base] }),
            frameRate: 8,
            repeat: -1,
          });
        });
      });
  }
}

export { Phaser };
