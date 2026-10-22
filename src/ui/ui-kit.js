/**
 * Shared GBA-style UI building blocks: panels, text, list menus, HP/EXP bars, type & status badges,
 * and a message box with typewriter text. All positions are in game pixels (1024x576 canvas).
 */
import Phaser from '../lib/phaser.js';
import { TYPE_COLORS } from '../battle/engine/type-chart.js';
import { dataManager } from '../utils/data-manager.js';

export const FONT = 'Pixelify';

export const COLORS = Object.freeze({
  panelFill: 0xfbfaf6,
  panelBorder: 0x3a3058,
  panelInner: 0x9b8fd0,
  darkFill: 0x2b2440,
  text: '#2d2a3a',
  textShadow: '#d6d0e6',
  textLight: '#f6f2ff',
  textLightShadow: '#4a3f6b',
  textMuted: '#7a7390',
  accent: '#c4404a',
  hpGreen: 0x58d058,
  hpYellow: 0xf0c020,
  hpRed: 0xe84838,
  exp: 0x48a0f8,
  barBg: 0x4a4458,
});

/** @type {Record<string, Phaser.Types.GameObjects.Text.TextStyle>} */
export const TEXT = Object.freeze({
  body: { fontFamily: FONT, fontSize: '30px', color: COLORS.text },
  small: { fontFamily: FONT, fontSize: '22px', color: COLORS.text },
  tiny: { fontFamily: FONT, fontSize: '18px', color: COLORS.text },
  title: { fontFamily: FONT, fontSize: '40px', color: COLORS.text, fontStyle: 'bold' },
  light: { fontFamily: FONT, fontSize: '30px', color: COLORS.textLight },
  lightSmall: { fontFamily: FONT, fontSize: '22px', color: COLORS.textLight },
});

/**
 * @param {Phaser.Scene} scene
 * @param {number} x
 * @param {number} y
 * @param {string} str
 * @param {keyof typeof TEXT | Phaser.Types.GameObjects.Text.TextStyle} [style='body']
 * @returns {Phaser.GameObjects.Text}
 */
export function text(scene, x, y, str, style = 'body') {
  const s = typeof style === 'string' ? TEXT[style] : style;
  const t = scene.add.text(x, y, str, s);
  const light = typeof style === 'string' && style.startsWith('light');
  t.setShadow(2, 2, light ? COLORS.textLightShadow : COLORS.textShadow, 0, false, true);
  return t;
}

/**
 * Rounded GBA window.
 * @param {Phaser.Scene} scene
 * @param {number} x
 * @param {number} y
 * @param {number} w
 * @param {number} h
 * @param {{fill?: number, border?: number, inner?: number, radius?: number}} [opts]
 * @returns {Phaser.GameObjects.Graphics}
 */
export function panel(scene, x, y, w, h, opts = {}) {
  const g = scene.add.graphics();
  drawPanel(g, x, y, w, h, opts);
  return g;
}

/**
 * @param {Phaser.GameObjects.Graphics} g
 * @param {number} x
 * @param {number} y
 * @param {number} w
 * @param {number} h
 * @param {{fill?: number, border?: number, inner?: number, radius?: number}} [opts]
 */
export function drawPanel(g, x, y, w, h, opts = {}) {
  const r = opts.radius ?? 10;
  g.fillStyle(opts.border ?? COLORS.panelBorder, 1);
  g.fillRoundedRect(x, y, w, h, r);
  g.fillStyle(opts.inner ?? COLORS.panelInner, 1);
  g.fillRoundedRect(x + 4, y + 4, w - 8, h - 8, Math.max(2, r - 3));
  g.fillStyle(opts.fill ?? COLORS.panelFill, 1);
  g.fillRoundedRect(x + 8, y + 8, w - 16, h - 16, Math.max(2, r - 5));
}

/**
 * Small right-pointing triangle cursor.
 * @param {Phaser.Scene} scene
 * @returns {Phaser.GameObjects.Triangle}
 */
export function cursor(scene) {
  return scene.add.triangle(0, 0, 0, 0, 0, 18, 13, 9, 0x2d2a3a).setOrigin(0, 0);
}

/**
 * @param {Phaser.Scene} scene
 * @param {number} x
 * @param {number} y
 * @param {string} type
 * @param {number} [scale=1]
 * @returns {Phaser.GameObjects.Container}
 */
export function typeBadge(scene, x, y, type, scale = 1) {
  const w = 104 * scale;
  const h = 30 * scale;
  const g = scene.add.graphics();
  g.fillStyle(0x2d2a3a, 1);
  g.fillRoundedRect(0, 0, w, h, 8 * scale);
  g.fillStyle(TYPE_COLORS[type] ?? 0x999999, 1);
  g.fillRoundedRect(2, 2, w - 4, h - 4, 7 * scale);
  const t = scene.add
    .text(w / 2, h / 2, type, { fontFamily: FONT, fontSize: `${Math.round(18 * scale)}px`, color: '#ffffff', fontStyle: 'bold' })
    .setOrigin(0.5)
    .setShadow(1, 1, '#00000088', 0, false, true);
  return scene.add.container(x, y, [g, t]);
}

const STATUS_COLORS = { BRN: 0xe86030, PSN: 0xa040a0, PAR: 0xd8b818, SLP: 0x8888a0, FRZ: 0x58b8d8, FNT: 0x703838 };

/**
 * @param {Phaser.Scene} scene
 * @param {number} x
 * @param {number} y
 * @returns {{container: Phaser.GameObjects.Container, set: (status: string | null) => void}}
 */
export function statusBadge(scene, x, y) {
  const g = scene.add.graphics();
  const t = scene.add
    .text(26, 12, '', { fontFamily: FONT, fontSize: '18px', color: '#ffffff', fontStyle: 'bold' })
    .setOrigin(0.5);
  const container = scene.add.container(x, y, [g, t]);
  const set = (status) => {
    g.clear();
    t.setText(status || '');
    container.setVisible(Boolean(status));
    if (status) {
      g.fillStyle(STATUS_COLORS[status] ?? 0x666666, 1);
      g.fillRoundedRect(0, 0, 52, 24, 6);
    }
  };
  set(null);
  return { container, set };
}

/** A horizontal meter (HP or EXP) that animates between values. */
export class Meter {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x
   * @param {number} y
   * @param {number} width
   * @param {number} height
   * @param {'hp'|'exp'} kind
   */
  constructor(scene, x, y, width, height, kind) {
    this.scene = scene;
    this.width = width;
    this.height = height;
    this.kind = kind;
    this.value = 1;
    this.g = scene.add.graphics();
    this.container = scene.add.container(x, y, [this.g]);
    this.#draw();
  }

  #color() {
    if (this.kind === 'exp') {
      return COLORS.exp;
    }
    if (this.value > 0.5) {
      return COLORS.hpGreen;
    }
    if (this.value > 0.2) {
      return COLORS.hpYellow;
    }
    return COLORS.hpRed;
  }

  #draw() {
    const g = this.g;
    g.clear();
    g.fillStyle(0x2d2a3a, 1);
    g.fillRoundedRect(0, 0, this.width, this.height, this.height / 2);
    g.fillStyle(COLORS.barBg, 1);
    g.fillRoundedRect(2, 2, this.width - 4, this.height - 4, (this.height - 4) / 2);
    const fill = Math.max(0, Math.min(1, this.value)) * (this.width - 4);
    if (fill > 0) {
      g.fillStyle(this.#color(), 1);
      g.fillRoundedRect(2, 2, Math.max(fill, this.height - 4), this.height - 4, (this.height - 4) / 2);
      g.fillStyle(0xffffff, 0.35);
      g.fillRect(6, 3, Math.max(0, fill - 8), Math.max(1, Math.floor((this.height - 4) / 3)));
    }
  }

  /** @param {number} ratio */
  set(ratio) {
    this.value = ratio;
    this.#draw();
  }

  /**
   * @param {number} ratio
   * @param {number} [duration]
   * @param {(ratio: number) => void} [onUpdate]
   * @returns {Promise<void>}
   */
  animateTo(ratio, duration, onUpdate) {
    const from = this.value;
    const d = duration ?? Math.min(1200, 200 + Math.abs(ratio - from) * 1400);
    if (d <= 0 || from === ratio) {
      this.set(ratio);
      onUpdate?.(ratio);
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      this.scene.tweens.addCounter({
        from: 0,
        to: 1,
        duration: d,
        onUpdate: (tw) => {
          const v = from + (ratio - from) * tw.getValue();
          this.set(v);
          onUpdate?.(v);
        },
        onComplete: () => {
          this.set(ratio);
          onUpdate?.(ratio);
          resolve();
        },
      });
    });
  }
}

/**
 * Vertical list menu with a cursor, optional scrolling and disabled rows.
 * Feed it input with handleInput(); it returns {type:'select', index} or {type:'cancel'} when done.
 */
export class ListMenu {
  /**
   * @param {Phaser.Scene} scene
   * @param {object} cfg
   * @param {number} cfg.x
   * @param {number} cfg.y
   * @param {number} cfg.width
   * @param {string[]} cfg.items
   * @param {number} [cfg.visibleRows]
   * @param {number} [cfg.rowHeight=46]
   * @param {boolean} [cfg.cancelable=true]
   * @param {boolean} [cfg.withPanel=true]
   * @param {number[]} [cfg.disabled]
   * @param {(index: number) => void} [cfg.onChange]
   * @param {string[]} [cfg.rightLabels] right-aligned text per row (e.g. quantities, prices)
   * @param {keyof typeof TEXT} [cfg.style='body']
   * @param {number} [cfg.depth]
   */
  constructor(scene, cfg) {
    this.scene = scene;
    this.cfg = { rowHeight: 46, cancelable: true, withPanel: true, style: 'body', ...cfg };
    this.items = cfg.items;
    this.index = 0;
    this.top = 0;
    this.visibleRows = cfg.visibleRows ?? cfg.items.length;
    this.disabled = new Set(cfg.disabled || []);
    const h = this.visibleRows * this.cfg.rowHeight + 36;
    this.height = h;
    this.container = scene.add.container(cfg.x, cfg.y);
    if (cfg.depth !== undefined) {
      this.container.setDepth(cfg.depth);
    }
    if (this.cfg.withPanel) {
      this.container.add(panel(scene, 0, 0, cfg.width, h));
    }
    /** @type {Phaser.GameObjects.Text[]} */
    this.rows = [];
    /** @type {Phaser.GameObjects.Text[]} */
    this.rightRows = [];
    for (let i = 0; i < this.visibleRows; i += 1) {
      const t = text(scene, 46, 18 + i * this.cfg.rowHeight, '', this.cfg.style);
      const r = text(scene, cfg.width - 28, 18 + i * this.cfg.rowHeight, '', this.cfg.style).setOrigin(1, 0);
      this.rows.push(t);
      this.rightRows.push(r);
      this.container.add([t, r]);
    }
    this.cursor = cursor(scene);
    this.upArrow = scene.add.triangle(cfg.width / 2, 6, 0, 10, 16, 10, 8, 0, 0x3a3058).setVisible(false);
    this.downArrow = scene.add.triangle(cfg.width / 2, h - 16, 0, 0, 16, 0, 8, 10, 0x3a3058).setVisible(false);
    this.container.add([this.cursor, this.upArrow, this.downArrow]);
    this.#render();
  }

  /** @param {string[]} items @param {string[]} [rightLabels] */
  setItems(items, rightLabels) {
    this.items = items;
    if (rightLabels) {
      this.cfg.rightLabels = rightLabels;
    }
    this.index = Math.min(this.index, Math.max(0, items.length - 1));
    this.top = Math.min(this.top, Math.max(0, items.length - this.visibleRows));
    this.#render();
  }

  /** @param {number} i */
  setIndex(i) {
    this.index = Math.max(0, Math.min(this.items.length - 1, i));
    this.#scrollToIndex();
    this.#render();
    this.cfg.onChange?.(this.index);
  }

  #scrollToIndex() {
    if (this.index < this.top) {
      this.top = this.index;
    } else if (this.index >= this.top + this.visibleRows) {
      this.top = this.index - this.visibleRows + 1;
    }
  }

  #render() {
    for (let i = 0; i < this.visibleRows; i += 1) {
      const idx = this.top + i;
      const label = this.items[idx] ?? '';
      this.rows[i].setText(label).setAlpha(this.disabled.has(idx) ? 0.45 : 1);
      this.rightRows[i].setText(this.cfg.rightLabels?.[idx] ?? '');
    }
    const visible = this.index - this.top;
    this.cursor.setPosition(20, 18 + visible * this.cfg.rowHeight + (this.cfg.rowHeight - 18) / 2 - 4);
    this.cursor.setVisible(this.items.length > 0);
    this.upArrow.setVisible(this.top > 0);
    this.downArrow.setVisible(this.top + this.visibleRows < this.items.length);
  }

  /**
   * @param {import('../common/direction.js').Direction | 'OK' | 'CANCEL'} input
   * @returns {{type: 'select', index: number} | {type: 'cancel'} | null}
   */
  handleInput(input) {
    if (input === 'UP' && this.items.length > 0) {
      this.setIndex(this.index === 0 ? this.items.length - 1 : this.index - 1);
    } else if (input === 'DOWN' && this.items.length > 0) {
      this.setIndex(this.index === this.items.length - 1 ? 0 : this.index + 1);
    } else if (input === 'OK' && this.items.length > 0 && !this.disabled.has(this.index)) {
      return { type: 'select', index: this.index };
    } else if (input === 'CANCEL' && this.cfg.cancelable) {
      return { type: 'cancel' };
    }
    return null;
  }

  destroy() {
    this.container.destroy();
  }
}

/**
 * Reads one frame of menu input from a scene's Controls.
 * @param {import('../utils/controls.js').Controls} controls
 * @returns {import('../common/direction.js').Direction | 'OK' | 'CANCEL' | null}
 */
export function readMenuInput(controls) {
  if (controls.wasConfirmPressed()) {
    return 'OK';
  }
  if (controls.wasBackKeyPressed()) {
    return 'CANCEL';
  }
  const d = controls.getDirectionKeyJustPressed();
  return d === 'NONE' ? null : d;
}

/**
 * Typewriter message box anchored to the bottom of the screen.
 */
export class MessageBox {
  /**
   * @param {Phaser.Scene} scene
   * @param {{x?: number, y?: number, width?: number, height?: number, depth?: number}} [cfg]
   */
  constructor(scene, cfg = {}) {
    this.scene = scene;
    const width = cfg.width ?? scene.scale.width;
    const height = cfg.height ?? 144;
    const x = cfg.x ?? 0;
    const y = cfg.y ?? scene.scale.height - height;
    this.container = scene.add.container(x, y).setDepth(cfg.depth ?? 50);
    this.container.add(panel(scene, 0, 0, width, height, { radius: 12 }));
    this.textObj = text(scene, 34, 26, '', 'body').setWordWrapWidth(width - 90).setLineSpacing(10);
    this.arrow = scene.add.triangle(width - 44, height - 34, 0, 0, 18, 0, 9, 11, 0xc4404a).setVisible(false);
    this.container.add([this.textObj, this.arrow]);
    this.arrowTween = scene.tweens.add({ targets: this.arrow, y: '+=6', duration: 350, yoyo: true, repeat: -1 });
    /** @type {null | (() => void)} */
    this.waitResolve = null;
    this.typing = null;
  }

  setVisible(v) {
    this.container.setVisible(v);
    return this;
  }

  /**
   * Types out text. If wait is true, resolves after the player presses A; otherwise resolves when typed
   * (plus a short pause).
   * @param {string} message
   * @param {{wait?: boolean, pause?: number}} [opts]
   * @returns {Promise<void>}
   */
  show(message, opts = {}) {
    const wait = opts.wait ?? true;
    this.container.setVisible(true);
    this.arrow.setVisible(false);
    return new Promise((resolve) => {
      const delay = dataManager.getAnimatedTextSpeed();
      let i = 0;
      this.textObj.setText('');
      const finishTyping = () => {
        this.typing?.remove();
        this.typing = null;
        this.textObj.setText(message);
        if (wait) {
          this.arrow.setVisible(true);
          this.waitResolve = () => {
            this.arrow.setVisible(false);
            resolve();
          };
        } else {
          this.scene.time.delayedCall(opts.pause ?? 450, resolve);
        }
      };
      this.skipTyping = finishTyping;
      if (delay <= 0 || message.length === 0) {
        finishTyping();
        return;
      }
      this.typing = this.scene.time.addEvent({
        delay,
        repeat: message.length - 1,
        callback: () => {
          i += 1;
          this.textObj.setText(message.slice(0, i));
          if (i >= message.length) {
            finishTyping();
          }
        },
      });
    });
  }

  /** Sets text instantly without waiting. */
  setText(message) {
    this.typing?.remove();
    this.typing = null;
    this.container.setVisible(true);
    this.arrow.setVisible(false);
    this.textObj.setText(message);
  }

  /**
   * Call with true when A (or B) was pressed this frame.
   * @param {boolean} pressed
   * @returns {boolean} whether the press was used
   */
  handleConfirm(pressed) {
    if (!pressed) {
      return false;
    }
    if (this.typing) {
      this.skipTyping?.();
      return true;
    }
    if (this.waitResolve) {
      const r = this.waitResolve;
      this.waitResolve = null;
      r();
      return true;
    }
    return false;
  }

  get isWaiting() {
    return Boolean(this.waitResolve || this.typing);
  }
}

/**
 * @param {Phaser.Scene} scene
 * @param {number} ms
 */
export function wait(scene, ms) {
  return new Promise((resolve) => scene.time.delayedCall(ms, resolve));
}

/**
 * @param {Phaser.Scene} scene
 * @param {Phaser.Types.Tweens.TweenBuilderConfig} config
 * @returns {Promise<void>}
 */
export function tween(scene, config) {
  return new Promise((resolve) => {
    scene.tweens.add({ ...config, onComplete: () => resolve() });
  });
}

export { Phaser };
