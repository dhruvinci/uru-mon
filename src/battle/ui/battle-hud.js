/**
 * HP boxes for the two sides of a battle.
 */
import { FONT, Meter, panel, statusBadge, text } from '../../ui/ui-kit.js';
import { displayName, expForLevel, getMaxHp, MAX_LEVEL } from '../engine/monster.js';

export class BattleHud {
  /**
   * @param {Phaser.Scene} scene
   * @param {'player'|'enemy'} side
   * @param {{x: number, y: number}} home where the box sits once it has slid in
   * @param {number} [scale=1]
   */
  constructor(scene, side, home, scale = 1) {
    this.scene = scene;
    this.side = side;
    const isPlayer = side === 'player';
    const w = isPlayer ? 452 : 430;
    const h = isPlayer ? 142 : 104;
    this.boxWidth = w;
    this.width = w * scale;
    this.home = home;
    this.container = scene.add.container(home.x, home.y).setDepth(20).setScale(scale);
    this.container.add(panel(scene, 0, 0, w, h, { radius: 14 }));
    this.nameText = text(scene, 26, 16, '', 'body');
    this.levelText = text(scene, w - 26, 18, '', { fontFamily: FONT, fontSize: '26px', color: '#2d2a3a' }).setOrigin(1, 0);
    const hpLabel = text(scene, 26, 62, 'HP', { fontFamily: FONT, fontSize: '20px', color: '#e0703a', fontStyle: 'bold' });
    this.hpMeter = new Meter(scene, 66, 64, w - 96, 18, 'hp');
    this.status = statusBadge(scene, w - 92, 92 - (isPlayer ? 0 : 22));
    this.container.add([this.nameText, this.levelText, hpLabel, this.hpMeter.container, this.status.container]);
    if (isPlayer) {
      this.hpText = text(scene, w - 30, 84, '', { fontFamily: FONT, fontSize: '24px', color: '#2d2a3a' }).setOrigin(1, 0);
      this.status.container.setPosition(26, 86);
      this.expMeter = new Meter(scene, 84, 118, w - 112, 10, 'exp');
      const expLabel = text(scene, 26, 113, 'EXP', { fontFamily: FONT, fontSize: '16px', color: '#3a7ad8', fontStyle: 'bold' });
      this.container.add([this.hpText, expLabel, this.expMeter.container]);
    }
    this.container.setVisible(false);
  }

  /** @param {import('../engine/monster.js').Monster} mon */
  bind(mon) {
    this.mon = mon;
    this.nameText.setText(displayName(mon));
    this.levelText.setText(`Lv${mon.level}`);
    const max = getMaxHp(mon);
    this.hpMeter.set(mon.hp / max);
    this.status.set(mon.hp <= 0 ? 'FNT' : mon.status);
    if (this.hpText) {
      this.hpText.setText(`${mon.hp}/${max}`);
    }
    this.setExp(mon);
  }

  /** @param {import('../engine/monster.js').Monster} mon */
  expRatio(mon) {
    if (mon.level >= MAX_LEVEL) {
      return 1;
    }
    const lo = expForLevel(mon.level);
    const hi = expForLevel(mon.level + 1);
    return Math.max(0, Math.min(1, (mon.exp - lo) / (hi - lo)));
  }

  /** @param {import('../engine/monster.js').Monster} mon */
  setExp(mon) {
    this.expMeter?.set(this.expRatio(mon));
  }

  /**
   * @param {number} hp
   * @param {number} maxHp
   * @returns {Promise<void>}
   */
  animateHp(hp, maxHp) {
    return this.hpMeter.animateTo(hp / maxHp, undefined, (ratio) => {
      if (this.hpText) {
        this.hpText.setText(`${Math.round(ratio * maxHp)}/${maxHp}`);
      }
    });
  }

  /** @param {string | null} status */
  setStatus(status) {
    this.status.set(status);
  }

  /**
   * Moves the box to a new home, drawn at a new size (the phone turned).
   * @param {{x: number, y: number}} home
   * @param {number} scale
   */
  place(home, scale) {
    this.home = home;
    this.width = this.boxWidth * scale;
    this.container.setPosition(home.x, home.y).setScale(scale);
  }

  /** Slides the box in from off-screen. */
  slideIn() {
    this.container.setVisible(true);
    const fromX = this.side === 'player' ? 1100 : -this.width - 50;
    this.container.setX(fromX);
    return new Promise((resolve) => {
      this.scene.tweens.add({ targets: this.container, x: this.home.x, duration: 450, ease: 'Cubic.out', onComplete: resolve });
    });
  }

  hide() {
    this.container.setVisible(false);
  }
}
