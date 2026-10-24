import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { dataManager } from '../utils/data-manager.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS, UI_KEYS } from '../assets/asset-keys.js';
import { ControlHints, FONT, HINTS, ListMenu, isTouchUI, readMenuInput, text } from '../ui/ui-kit.js';
import { allSpecies } from '../battle/engine/monster.js';
import { adminAvailable, startAdminProfile } from '../game/admin-profile.js';
import { inputManager } from '../input/input-manager.js';
import { DESIGN_HEIGHT, FULL_HEIGHT, GAME_WIDTH, isTall, onResize, setTextResolution, uiScale } from '../ui/screen.js';

export class TitleScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.TITLE_SCENE });
  }

  init() {
    super.init();
    this.stage = 'press';
    /** @type {ListMenu | null} */
    this.menu = null;
  }

  create() {
    super.create();
    if (this.textures.exists(UI_KEYS.TITLE_BG)) {
      this.bg = this.add.image(0, 0, UI_KEYS.TITLE_BG);
    } else {
      this.bgFallback = this.add.graphics();
    }
    this.add.rectangle(0, 0, GAME_WIDTH, FULL_HEIGHT, 0x120a26, 0.25).setOrigin(0);

    // a parade of creatures along the bottom
    const legends = new Set([64, 65, 146, 147, 148, 149, 150]);
    const species = allSpecies().filter((s) => !legends.has(s.id) && this.textures.exists(s.assetKey));
    this.parade = this.add.container(0, 0);
    for (let i = 0; i < 9 && species.length; i += 1) {
      const sp = species[(i * 7 + 3) % species.length];
      const img = this.add.image(-200 - i * 190, -18, sp.assetKey).setOrigin(0.5, 1).setScale(2.2);
      this.parade.add(img);
      this.tweens.add({ targets: img, y: -30, duration: 260, yoyo: true, repeat: -1, delay: i * 90 });
    }

    // the title block, laid out for 1024x576 and scaled up on a tall canvas
    const width = GAME_WIDTH;
    this.content = this.add.container(0, 0);
    if (this.textures.exists(UI_KEYS.TITLE_LOGO)) {
      const logo = this.add.image(width / 2, 150, UI_KEYS.TITLE_LOGO).setOrigin(0.5);
      logo.setScale(Math.min(700 / logo.width, 220 / logo.height));
      this.logo = logo;
    } else {
      this.logo = this.add
        .text(width / 2, 140, 'uru-mon', { fontFamily: FONT, fontSize: '128px', color: '#fff4d6', fontStyle: 'bold' })
        .setOrigin(0.5)
        .setStroke('#3a1f5c', 18)
        .setShadow(8, 8, '#00000066', 0, true, true);
    }
    this.tweens.add({ targets: this.logo, y: '+=8', duration: 1600, yoyo: true, repeat: -1, ease: 'Sine.inOut' });
    this.subtitle = text(this, width / 2, 238, 'A  BENGALURU  ADVENTURE', { fontFamily: FONT, fontSize: '30px', color: '#ffe9a8', fontStyle: 'bold' })
      .setOrigin(0.5)
      .setStroke('#3a1f5c', 8);

    const touch = isTouchUI();
    this.press = this.add
      .text(width / 2, 318, touch ? 'TAP TO START' : 'PRESS ENTER', { fontFamily: FONT, fontSize: '36px', color: '#ffffff', fontStyle: 'bold' })
      .setOrigin(0.5)
      .setStroke('#3a1f5c', 8);
    this.tweens.add({ targets: this.press, alpha: 0.2, duration: 600, yoyo: true, repeat: -1 });
    // the keyboard at a glance (touch screens have the pad, whose buttons the menus' prompts point to)
    this.hint = new ControlHints(this, width / 2, 380, { align: 'center', backing: true }).set(touch ? [] : [
      { key: 'Arrows', label: 'Move' }, { btn: 'A', label: 'Select / Talk' }, { btn: 'B', label: 'Back / Menu' }, { key: 'F', label: 'Fullscreen' },
    ]);
    this.content.add([this.logo, this.subtitle, this.press, this.hint.container]);
    this.menuHints = new ControlHints(this, 0, 0, { backing: true, depth: 20 }).set(HINTS.menu).setVisible(false);
    this.version = this.add.text(0, 10, 'v1.0', { fontFamily: FONT, fontSize: '16px', color: '#fff4d6' }).setOrigin(1, 0).setAlpha(0.6);
    this.#layout();
    onResize(this, () => this.#layout());

    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_TITLE);
    this.cameras.main.fadeIn(600, 0, 0, 0);
    // tap anywhere to start (menu rows take their own taps)
    this.input.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => {
      if (this.stage === 'press' && p.getDistance() < 24) {
        inputManager.tap('A');
      }
    });
  }

  /** Fits the screen to the canvas: on a tall one (a phone held upright) the title, menu and prompts are bigger. */
  #layout() {
    const W = GAME_WIDTH;
    const H = this.scale.height;
    const k = uiScale(this);
    setTextResolution(this, k);
    if (this.bg) {
      this.bg.setPosition(W / 2, H / 2).setScale(Math.max(W / this.bg.width, H / this.bg.height));
    } else {
      this.bgFallback.clear().fillGradientStyle(0x2b1d5a, 0x2b1d5a, 0xe87a5a, 0xf2b46a, 1).fillRect(0, 0, W, H);
    }
    this.parade.setY(H).setScale(k);
    this.content.setScale(k).setPosition((W / 2) * (1 - k), isTall(this) ? (H - DESIGN_HEIGHT * k) * 0.4 : 0);
    this.hint.refresh();
    this.menuHints.refresh();
    this.menuHints.container.setScale(k).setPosition(W - 20 * k, H - 30 * k);
    this.version.setScale(k).setX(W - 12);
    this.#placeMenu();
  }

  #placeMenu() {
    if (!this.menu) {
      return;
    }
    const k = this.content.scaleX;
    const y = Math.min(this.content.y + 290 * k, this.scale.height - (this.menu.height + 10) * k);
    this.menu.container.setScale(k).setPosition(GAME_WIDTH / 2 - 190 * k, y);
  }

  update(time) {
    super.update(time);
    if (this.parade) {
      this.parade.x += 1.2;
      if (this.parade.x > this.scale.width + 1900 * this.parade.scaleX) {
        this.parade.x = 0;
      }
    }
    if (!this._controls) {
      return;
    }
    const input = readMenuInput(this._controls);
    // any button starts: A, B or MENU
    const start = this.stage === 'press' && (input === 'OK' || input === 'CANCEL' || this._controls.wasEnterKeyPressed());
    if (start) {
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      this.#showMenu();
      return;
    }
    if (this.stage !== 'menu' || !input || !this.menu) {
      return;
    }
    const r = this.menu.handleInput(input);
    if (!r) {
      return;
    }
    if (r.type === 'cancel') {
      this.menu.destroy();
      this.menu = null;
      this.stage = 'press';
      this.press.setVisible(true);
      this.subtitle.setVisible(true);
      this.hint.setVisible(true);
      this.menuHints.setVisible(false);
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    this.#choose(this.menuItems[r.index]);
  }

  #showMenu() {
    this.stage = 'menu';
    this.press.setVisible(false);
    dataManager.useProfile('main');
    this.menuItems = [
      ...(dataManager.hasSave() ? ['CONTINUE'] : []),
      'NEW GAME',
      'QUICK BATTLE',
      'URU-PUSTAKA',
      'BENGALURU MAP',
      'OPTIONS',
      ...(adminAvailable() ? ['ADMIN MODE'] : []),
    ];
    const rowHeight = 42;
    const height = this.menuItems.length * rowHeight + 36;
    this.subtitle.setVisible(height < 300);
    this.hint.setVisible(false);
    this.menuHints.setVisible(true);
    this.menu = new ListMenu(this, { x: 0, y: 0, width: 380, items: this.menuItems, rowHeight, depth: 10 });
    this.#placeMenu();
  }

  /** @param {string} choice */
  #choose(choice) {
    const browse = {
      OPTIONS: [SCENE_KEYS.OPTIONS_SCENE, {}],
      'URU-PUSTAKA': [SCENE_KEYS.PUSTAKA_SCENE, { browse: true }],
      'BENGALURU MAP': [SCENE_KEYS.REGION_MAP_SCENE, {}],
    }[choice];
    if (browse) {
      this.stage = 'sub';
      this.events.once('resume', () => {
        this.stage = 'menu';
      });
      this.scene.launch(browse[0], { ...browse[1], previousSceneName: SCENE_KEYS.TITLE_SCENE });
      this.scene.pause();
      return;
    }
    this.stage = 'leaving';
    this.cameras.main.fadeOut(500, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      if (choice === 'CONTINUE') {
        dataManager.loadData();
        this.scene.start(SCENE_KEYS.WORLD_SCENE);
        return;
      }
      if (choice === 'QUICK BATTLE') {
        this.scene.start(SCENE_KEYS.QUICK_BATTLE_SCENE);
        return;
      }
      if (choice === 'ADMIN MODE') {
        startAdminProfile();
        this.scene.start(SCENE_KEYS.WORLD_SCENE);
        return;
      }
      this.scene.start(SCENE_KEYS.INTRO_SCENE);
    });
  }
}
