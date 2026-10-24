import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { displayName, expForLevel, getMaxHp, getMove, getSpecies, getStats, MAX_LEVEL } from '../battle/engine/monster.js';
import { Meter, panel, readMenuInput, statusBadge, text, typeBadge, ControlHints } from '../ui/ui-kit.js';
import { inputManager } from '../input/input-manager.js';
import { FULL_HEIGHT } from '../ui/screen.js';

/**
 * @typedef MonsterDetailsSceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {number} monsterIndex
 * @property {'party'|'box'} [list='party']
 */

const PAGES = ['INFO', 'STATS', 'MOVES'];

export class MonsterDetailsScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.MONSTER_DETAILS_SCENE });
  }

  /** @param {MonsterDetailsSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { list: 'party', ...data };
    this.index = data.monsterIndex ?? 0;
    this.page = 0;
    this.moveIndex = 0;
  }

  get list() {
    return this.sceneData.list === 'box' ? dataManager.boxes : dataManager.party;
  }

  create() {
    super.create();
    this.input.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => p.getDistance() < 24 && inputManager.tap('RIGHT'));
    this.root = this.add.container(0, 0);
    this.#render();
  }

  #render() {
    this.root.removeAll(true);
    const mon = this.list[this.index];
    if (!mon) {
      return;
    }
    const sp = getSpecies(mon.speciesId);
    const add = (o) => {
      this.root.add(o);
      return o;
    };
    add(this.add.rectangle(0, 0, 1024, FULL_HEIGHT, 0x6a5aa8).setOrigin(0));
    // header tabs
    PAGES.forEach((p, i) => {
      const x = 470 + i * 182;
      const g = this.add.graphics();
      g.fillStyle(i === this.page ? 0xfbfaf6 : 0x4d4180, 1);
      g.fillRoundedRect(x, 14, 172, 52, 12);
      add(g);
      add(text(this, x + 86, 26, p, i === this.page ? 'body' : 'light').setOrigin(0.5, 0));
    });
    add(new ControlHints(this, 470, 88, { align: 'left', dark: true })
      .set([{ key: '◀ ▶', label: 'Page' }, { key: '▲▼', label: 'Urumon' }, { btn: 'B', label: 'Back' }]).container);

    // left: portrait card
    add(panel(this, 14, 14, 440, 548, { radius: 16 }));
    add(text(this, 44, 36, `No.${String(sp.id).padStart(3, '0')}`, 'small'));
    add(text(this, 44, 66, displayName(mon), 'title'));
    add(text(this, 420, 74, `Lv${mon.level}`, 'body').setOrigin(1, 0));
    const key = sp.assetKey;
    add(this.add.image(234, 400, this.textures.exists(key) ? key : '__MISSING').setOrigin(0.5, 1).setScale(4.5));
    sp.types.forEach((t, i) => add(typeBadge(this, 44 + i * 116, 418, t)));
    const st = statusBadge(this, 300, 422);
    st.set(mon.hp <= 0 ? 'FNT' : mon.status);
    add(st.container);
    const max = getMaxHp(mon);
    add(text(this, 44, 466, 'HP', { fontFamily: 'Pixelify', fontSize: '20px', color: '#e0703a', fontStyle: 'bold' }));
    const m = new Meter(this, 86, 470, 230, 18, 'hp');
    m.set(mon.hp / max);
    add(m.container);
    add(text(this, 420, 462, `${mon.hp}/${max}`, 'body').setOrigin(1, 0));
    const lo = expForLevel(mon.level);
    const hi = expForLevel(mon.level + 1);
    add(text(this, 44, 510, 'EXP', { fontFamily: 'Pixelify', fontSize: '18px', color: '#3a7ad8', fontStyle: 'bold' }));
    const e = new Meter(this, 96, 514, 320, 12, 'exp');
    e.set(mon.level >= MAX_LEVEL ? 1 : (mon.exp - lo) / (hi - lo));
    add(e.container);

    // right: page body
    add(panel(this, 466, 112, 544, 450, { radius: 16 }));
    const x0 = 498;
    if (PAGES[this.page] === 'INFO') {
      const rows = [
        ['SPECIES', sp.name],
        ['TYPE', sp.types.join(' / ')],
        ['EXP', `${mon.exp}`],
        ['TO NEXT LV', mon.level >= MAX_LEVEL ? '-' : `${hi - mon.exp}`],
      ];
      if (sp.evolution) {
        rows.push(['EVOLVES', `at Lv${sp.evolution.level}`]);
      }
      rows.forEach(([k, v], i) => {
        add(text(this, x0, 140 + i * 48, k, { fontFamily: 'Pixelify', fontSize: '24px', color: '#7a7390' }));
        add(text(this, x0 + 210, 138 + i * 48, v, 'body'));
      });
      add(text(this, x0, 140 + rows.length * 48 + 16, sp.dex, 'small').setWordWrapWidth(480).setLineSpacing(6));
    } else if (PAGES[this.page] === 'STATS') {
      const s = getStats(mon);
      const rows = [
        ['HP', `${mon.hp}/${s.hp}`],
        ['ATTACK', s.atk],
        ['DEFENSE', s.def],
        ['SPECIAL', s.spc],
        ['SPEED', s.spd],
      ];
      rows.forEach(([k, v], i) => {
        add(text(this, x0, 150 + i * 62, k, 'body'));
        add(text(this, x0 + 470, 150 + i * 62, String(v), 'body').setOrigin(1, 0));
        const bar = this.add.graphics();
        const base = sp.baseStats[['hp', 'atk', 'def', 'spc', 'spd'][i]];
        bar.fillStyle(0xe6e0f4, 1);
        bar.fillRoundedRect(x0, 188 + i * 62, 470, 8, 4);
        bar.fillStyle(0x8a70d8, 1);
        bar.fillRoundedRect(x0, 188 + i * 62, Math.min(470, (base / 130) * 470), 8, 4);
        add(bar);
      });
      add(text(this, x0, 470, 'Bars show this species\' base stats.', 'small'));
    } else {
      mon.moves.forEach((mv, i) => {
        const data = getMove(mv.id);
        const y = 136 + i * 62;
        if (i === this.moveIndex) {
          const g = this.add.graphics();
          g.fillStyle(0xfff0c8, 1);
          g.fillRoundedRect(x0 - 12, y - 6, 500, 56, 10);
          add(g);
        }
        add(typeBadge(this, x0, y + 6, data.type, 0.9));
        add(text(this, x0 + 112, y + 4, data.name, 'body'));
        add(text(this, x0 + 476, y + 8, `PP ${mv.pp}/${data.pp}`, 'small').setOrigin(1, 0));
      });
      const sel = mon.moves[this.moveIndex];
      if (sel) {
        const d = getMove(sel.id);
        add(text(this, x0, 392, `${d.category}   POW ${d.power || '-'}   ACC ${d.accuracy || '-'}`, 'small'));
        add(text(this, x0, 428, d.description, 'small').setWordWrapWidth(480).setLineSpacing(6));
      }
    }
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
    const n = this.list.length;
    if (input === 'CANCEL' || (input === 'OK' && PAGES[this.page] !== 'MOVES')) {
      this.scene.stop();
      this.scene.resume(this.sceneData.previousSceneName, {});
      return;
    }
    if (input === 'LEFT') {
      this.page = (this.page + PAGES.length - 1) % PAGES.length;
    } else if (input === 'RIGHT') {
      this.page = (this.page + 1) % PAGES.length;
    } else if (input === 'UP' || input === 'DOWN') {
      if (PAGES[this.page] === 'MOVES') {
        const count = this.list[this.index].moves.length;
        this.moveIndex = (this.moveIndex + (input === 'UP' ? count - 1 : 1)) % count;
      } else if (n > 1) {
        this.index = (this.index + (input === 'UP' ? n - 1 : 1)) % n;
        this.moveIndex = 0;
      }
    }
    this.#render();
  }
}
