import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { ControlHints, HINTS, ListMenu, MessageBox, isTouchUI, panel, readMenuInput, text } from '../ui/ui-kit.js';
import { dataManager } from '../utils/data-manager.js';
import { inputManager } from '../input/input-manager.js';
import { GAME_WIDTH, isTall, onResize, setTextResolution, uiScale } from '../ui/screen.js';

/** Overworld prompts for keyboard players, shown until they've talked to someone and opened the menu once. */
const WORLD_HINTS = [{ btn: 'A', label: 'Talk' }, { btn: 'START', label: 'Menu' }, { key: 'Shift', label: 'Run', kb: true }];
const LEARNED_KEY = 'uru-learned-keys';

/**
 * Overlay used by the world for dialog, yes/no questions and choice lists. It owns its own fixed camera so
 * the world camera's scroll never affects it. All methods are promise based.
 * On a tall canvas (a phone held upright) everything is drawn uiScale() times bigger, since the 1024-wide game is shown
 * on the phone's narrow side, and the message box grows to fit long messages.
 */
export class DialogScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.DIALOG_SCENE });
  }

  create() {
    super.create();
    this.k = 1;
    this.message = '';
    this.box = new MessageBox(this, { height: 144, depth: 10 });
    this.box.setVisible(false);
    this.speaker = this.add.container(24, 432 - 44).setDepth(11).setVisible(false);
    this.speakerBg = this.add.graphics();
    this.speakerText = text(this, 20, 8, '', 'lightSmall');
    this.speaker.add([this.speakerBg, this.speakerText]);
    /** @type {null | ((input: string) => void)} */
    this.inputHandler = null;
    this.moneyBox = null;
    this.busyCount = 0;
    // tap anywhere to advance a message; menus sit above this and take their own taps
    this.tapZone = this.add.zone(0, 0, GAME_WIDTH, this.scale.height).setOrigin(0).setDepth(9).setInteractive();
    this.tapZone.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => {
      if (this.busy && p.getDistance() < 24) {
        inputManager.tap('A');
      }
    });
    // prompts in the bottom-right corner when no message box is up: menus opened over the world, and WORLD_HINTS
    this.corner = new ControlHints(this, 1004, 546, { backing: true, depth: 30 });
    /** @type {import('../ui/ui-kit.js').Hint[] | null} */
    this.menuHints = null;
    /** @type {null | (() => void)} puts the open choice menu in place */
    this.placeMenu = null;
    try {
      this.learnedKeys = new Set(JSON.parse(localStorage.getItem(LEARNED_KEY) || '[]'));
    } catch {
      this.learnedKeys = new Set();
    }
    this.#layout();
    onResize(this, () => this.#layout());
  }

  /** Sizes and places everything for the canvas: normal size, or uiScale() times bigger on a tall one. */
  #layout() {
    const k = uiScale(this);
    this.k = k;
    setTextResolution(this, k);
    const H = this.scale.height;
    this.box.setAnnounces(!isTall(this)); // big enough to read on its own
    this.#fitBox(this.message);
    this.box.hints.refresh();
    this.corner.refresh();
    this.corner.container.setScale(k).setPosition(GAME_WIDTH - 20 * k, H - 30 * k);
    this.speaker.setScale(k);
    this.tapZone.setSize(GAME_WIDTH, H);
    this.moneyBox?.setScale(k).setPosition(GAME_WIDTH - 250 * k, 12 * k);
    this.placeMenu?.();
  }

  /**
   * Makes the box tall enough for a message (two lines normally; at least three, and more for long messages, on a
   * tall canvas) and keeps it on the bottom edge, with the speaker's name on top.
   * @param {string} message
   */
  #fitBox(message) {
    this.box.dock(message, this.k, isTall(this));
    this.speaker.setPosition(24 * this.k, this.box.container.y - 44 * this.k);
  }

  /** The top of the message box, on screen. */
  get boxTop() {
    return this.box.container.y;
  }

  /**
   * Shows one message in the box, sized for it.
   * @param {string} message
   * @param {{wait?: boolean, pause?: number}} [opts]
   */
  #show(message, opts) {
    this.message = message;
    this.#fitBox(message);
    return this.box.show(message, opts);
  }

  /**
   * The world tells us when the player has used one of WORLD_HINTS' buttons.
   * @param {'talk' | 'menu'} what
   */
  learned(what) {
    if (this.learnedKeys.has(what)) {
      return;
    }
    this.learnedKeys.add(what);
    try {
      localStorage.setItem(LEARNED_KEY, JSON.stringify([...this.learnedKeys]));
    } catch {
      /* storage unavailable: the prompts just come back next visit */
    }
  }

  #updateCorner() {
    const world = /** @type {any} */ (this.scene.get(SCENE_KEYS.WORLD_SCENE));
    const worldIdle = !this.busy && this.scene.isActive(SCENE_KEYS.WORLD_SCENE) && world?.player && !world.inputLocked;
    const showWorld = worldIdle && !isTouchUI() && this.learnedKeys.size < 2;
    this.corner.set(this.menuHints ?? (showWorld ? WORLD_HINTS : []));
  }

  /** True while any dialog UI is on screen. */
  get busy() {
    return this.busyCount > 0;
  }

  // kept for older call sites
  get isVisible() {
    return this.busy;
  }

  update(time) {
    super.update(time);
    // only catch taps while dialog is up, so the world underneath gets them otherwise
    this.tapZone.input.enabled = this.busy;
    this.#updateCorner();
    if (!this._controls || !this.busy) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.box.isWaiting && (input === 'OK' || input === 'CANCEL')) {
      this.box.handleConfirm(true);
      return;
    }
    this.inputHandler?.(input);
  }

  /**
   * @param {string} s
   * @returns {string}
   */
  format(s) {
    const st = dataManager.state;
    return s
      .replaceAll('{PLAYER}', st.player.name)
      .replaceAll('{RIVAL}', 'Sudeep')
      .replaceAll('{STARTER}', st.vars.starterName || 'your partner')
      .replaceAll('{RIVAL_STARTER}', st.vars.rivalStarterName || 'his partner')
      .replaceAll('{MONEY}', `₹${dataManager.money}`);
  }

  /**
   * Shows one or more lines, waiting for A after each.
   * @param {string | string[]} lines
   * @param {{speaker?: string, keepOpen?: boolean}} [opts]
   */
  async say(lines, opts = {}) {
    const list = Array.isArray(lines) ? lines : [lines];
    this.busyCount += 1;
    this.#setSpeaker(opts.speaker);
    for (const line of list) {
      await this.#show(this.format(line), { wait: true });
    }
    this.busyCount -= 1;
    if (!opts.keepOpen && !this.busy) {
      this.close();
    }
  }

  /** @param {string} [name] */
  #setSpeaker(name) {
    // the phone layout shows the speaker with its large copy of the message (when it makes one)
    window.dispatchEvent(new CustomEvent('uru:speaker', { detail: (this.box.announces && name) || '' }));
    if (!name) {
      this.speaker.setVisible(false);
      return;
    }
    this.speakerText.setText(name);
    this.speakerBg.clear();
    this.speakerBg.fillStyle(0x3a3058, 1);
    this.speakerBg.fillRoundedRect(0, 0, this.speakerText.width + 40, 40, 10);
    this.speaker.setVisible(true);
  }

  close() {
    this.box.setVisible(false);
    this.speaker.setVisible(false);
  }

  /**
   * Asks a question and resolves true for YES.
   * @param {string} question
   * @param {{speaker?: string}} [opts]
   * @returns {Promise<boolean>}
   */
  async ask(question, opts = {}) {
    this.busyCount += 1;
    this.#setSpeaker(opts.speaker);
    await this.#show(this.format(question), { wait: false, pause: 0 });
    const idx = await this.choose(['YES', 'NO'], { cancelValue: 1 });
    this.busyCount -= 1;
    if (!this.busy) {
      this.close();
    }
    return idx === 0;
  }

  /**
   * Shows a list menu at the right, above the message box (or in the top-right corner with `top`). Resolves the
   * index, or cancelValue (default -1) on B.
   * @param {string[]} items
   * @param {{cancelValue?: number, rightLabels?: string[], width?: number, prompt?: string, top?: boolean, visibleRows?: number}} [opts]
   * @returns {Promise<number>}
   */
  async choose(items, opts = {}) {
    this.busyCount += 1;
    if (opts.prompt) {
      await this.#show(this.format(opts.prompt), { wait: false, pause: 0 });
    }
    const width = opts.width ?? Math.max(220, ...items.map((s) => s.length * 17 + 100));
    const visibleRows = Math.min(items.length, opts.visibleRows ?? 6);
    const menu = new ListMenu(this, { x: 0, y: 0, width, items, visibleRows, rightLabels: opts.rightLabels, depth: 20 });
    this.placeMenu = () => {
      const k = this.k;
      menu.container.setScale(k);
      const y = opts.top ? 12 * k : this.boxTop - menu.height * k - 8 * k;
      menu.container.setPosition(GAME_WIDTH - (width + 12) * k, y);
    };
    this.placeMenu();
    // with a question in the message box, the prompts go in the box; a menu on its own gets them in the corner
    if (this.box.container.visible) {
      this.box.setHints(HINTS.menu);
    } else {
      this.menuHints = HINTS.menu;
    }
    const result = await new Promise((resolve) => {
      this.inputHandler = (input) => {
        const r = menu.handleInput(/** @type {any} */ (input));
        if (!r) {
          return;
        }
        this.inputHandler = null;
        resolve(r.type === 'select' ? r.index : opts.cancelValue ?? -1);
      };
    });
    menu.destroy();
    this.placeMenu = null;
    this.box.setHints([]);
    this.menuHints = null;
    this.busyCount -= 1;
    return /** @type {number} */ (result);
  }

  /** Shows (or refreshes) the money window in the top-right corner. */
  showMoney() {
    this.hideMoney();
    const k = this.k;
    const c = this.add.container(GAME_WIDTH - 250 * k, 12 * k).setDepth(15).setScale(k);
    c.add(panel(this, 0, 0, 238, 70));
    c.add(text(this, 28, 18, `₹${dataManager.money}`, 'body'));
    this.moneyBox = c;
  }

  hideMoney() {
    this.moneyBox?.destroy();
    this.moneyBox = null;
  }

  // ---- compatibility with the original API -----------------------------------------------------

  /** @param {string[]} messages */
  showDialogModal(messages) {
    this.say(messages);
  }

  hideDialogModal() {
    this.close();
  }
}
