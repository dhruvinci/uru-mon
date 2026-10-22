import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { ListMenu, MessageBox, panel, readMenuInput, text } from '../ui/ui-kit.js';
import { dataManager } from '../utils/data-manager.js';

/**
 * Overlay used by the world for dialog, yes/no questions and choice lists. It owns its own fixed camera so
 * the world camera's scroll never affects it. All methods are promise based.
 */
export class DialogScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.DIALOG_SCENE });
  }

  create() {
    super.create();
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
      .replaceAll('{RIVAL}', 'Rohan')
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
      await this.box.show(this.format(line), { wait: true });
    }
    this.busyCount -= 1;
    if (!opts.keepOpen && !this.busy) {
      this.close();
    }
  }

  /** @param {string} [name] */
  #setSpeaker(name) {
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
    await this.box.show(this.format(question), { wait: false, pause: 0 });
    const idx = await this.choose(['YES', 'NO'], { cancelValue: 1 });
    this.busyCount -= 1;
    if (!this.busy) {
      this.close();
    }
    return idx === 0;
  }

  /**
   * Shows a list menu above the message box. Resolves the index, or cancelValue (default -1) on B.
   * @param {string[]} items
   * @param {{cancelValue?: number, rightLabels?: string[], width?: number, prompt?: string, x?: number, y?: number, visibleRows?: number}} [opts]
   * @returns {Promise<number>}
   */
  async choose(items, opts = {}) {
    this.busyCount += 1;
    if (opts.prompt) {
      await this.box.show(this.format(opts.prompt), { wait: false, pause: 0 });
    }
    const width = opts.width ?? Math.max(220, ...items.map((s) => s.length * 17 + 100));
    const visibleRows = Math.min(items.length, opts.visibleRows ?? 6);
    const menu = new ListMenu(this, {
      x: opts.x ?? 1024 - width - 12,
      y: opts.y ?? 432 - (visibleRows * 46 + 36) - 8,
      width,
      items,
      visibleRows,
      rightLabels: opts.rightLabels,
      depth: 20,
    });
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
    this.busyCount -= 1;
    return /** @type {number} */ (result);
  }

  /** Shows (or refreshes) the money window in the top-right corner. */
  showMoney() {
    this.hideMoney();
    const c = this.add.container(1024 - 250, 12).setDepth(15);
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
