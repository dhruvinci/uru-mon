import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { displayName, getMaxHp, getSpecies } from '../battle/engine/monster.js';
import { ListMenu, Meter, readMenuInput, statusBadge, text, MessageBox } from '../ui/ui-kit.js';
import { applyItem } from '../battle/engine/battle-engine.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';

/**
 * @typedef MonsterPartySceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {'world'|'battle'|'battle-forced'|'use-item'} [mode='world']
 * @property {number} [activeIndex] active battler (battle modes)
 * @property {import('../game/game-data.js').ItemData} [item] item being used (use-item mode, from the world bag)
 */

const CARD_W = 494;
const CARD_H = 142;

export class MonsterPartyScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.MONSTER_PARTY_SCENE });
  }

  /** @param {MonsterPartySceneData} data */
  init(data) {
    super.init();
    this.sceneData = { mode: 'world', ...data };
    this.index = 0;
    this.swapFrom = -1;
    /** @type {ListMenu | null} */
    this.submenu = null;
    this.busy = false;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0x6a5aa8).setOrigin(0);
    const g = this.add.graphics();
    g.fillStyle(0x7d6dbc, 1);
    for (let y = 0; y < 576; y += 32) {
      for (let x = (y / 32) % 2 ? 0 : 32; x < 1024; x += 64) {
        g.fillRect(x, y, 32, 32);
      }
    }
    this.cards = [];
    for (let i = 0; i < 6; i += 1) {
      this.cards.push(this.#createCard(i));
    }
    this.message = new MessageBox(this, { x: 0, y: 470, width: 1024, height: 106 });
    this.#renderAll();
    this.#setDefaultMessage();
  }

  #setDefaultMessage() {
    const m = this.sceneData.mode;
    const msg =
      m === 'battle-forced'
        ? 'Choose an Urumon to send out.'
        : m === 'use-item'
          ? `Use ${this.sceneData.item?.name} on which Urumon?`
          : this.swapFrom >= 0
            ? 'Move to where?'
            : 'Choose an Urumon.';
    this.message.setText(msg);
  }

  /** @param {number} i */
  #createCard(i) {
    const x = 12 + (i % 2) * (CARD_W + 12);
    const y = 12 + Math.floor(i / 2) * (CARD_H + 10);
    const c = this.add.container(x, y);
    const bg = this.add.graphics();
    const icon = this.add.image(78, CARD_H / 2 + 6, '__MISSING').setOrigin(0.5).setScale(1.6);
    const name = text(this, 150, 18, '', 'body');
    const lvl = text(this, CARD_W - 24, 20, '', 'small').setOrigin(1, 0);
    const hpLabel = text(this, 150, 66, 'HP', { fontFamily: 'Pixelify', fontSize: '18px', color: '#e0703a', fontStyle: 'bold' });
    const meter = new Meter(this, 186, 68, CARD_W - 214, 16, 'hp');
    const hpText = text(this, CARD_W - 24, 92, '', 'small').setOrigin(1, 0);
    const status = statusBadge(this, 150, 98);
    c.add([bg, icon, name, lvl, hpLabel, meter.container, hpText, status.container]);
    return { c, bg, icon, name, lvl, meter, hpText, status, x, y };
  }

  #renderAll() {
    const party = dataManager.party;
    this.cards.forEach((card, i) => {
      const mon = party[i];
      card.bg.clear();
      const selected = i === this.index;
      const swapping = i === this.swapFrom;
      const fill = !mon ? 0x564a8c : mon.hp <= 0 ? 0xd8a0a0 : selected ? 0xfff6d8 : 0xf4f0ff;
      card.bg.fillStyle(selected ? 0xf0a040 : swapping ? 0x58c0f0 : 0x3a3058, 1);
      card.bg.fillRoundedRect(0, 0, CARD_W, CARD_H, 16);
      card.bg.fillStyle(fill, 1);
      card.bg.fillRoundedRect(6, 6, CARD_W - 12, CARD_H - 12, 12);
      const visible = Boolean(mon);
      [card.icon, card.name, card.lvl, card.meter.container, card.hpText].forEach((o) => o.setVisible(visible));
      card.c.list[4].setVisible(visible);
      if (!mon) {
        card.status.set(null);
        return;
      }
      const key = getSpecies(mon.speciesId).assetKey;
      card.icon.setTexture(this.textures.exists(key) ? key : '__MISSING');
      card.name.setText(displayName(mon));
      card.lvl.setText(`Lv${mon.level}`);
      const max = getMaxHp(mon);
      card.meter.set(mon.hp / max);
      card.hpText.setText(`${mon.hp}/${max}`);
      card.status.set(mon.hp <= 0 ? 'FNT' : mon.status);
      if (this.sceneData.mode !== 'world' && i === this.sceneData.activeIndex) {
        card.name.setText(`${displayName(mon)} ★`);
      }
    });
    // little bob on the selected icon
    this.tweens.killTweensOf(this.cards.map((c) => c.icon));
    this.cards.forEach((c) => c.icon.setY(CARD_H / 2 + 6));
    const sel = this.cards[this.index];
    if (dataManager.party[this.index]) {
      this.tweens.add({ targets: sel.icon, y: CARD_H / 2 - 2, duration: 220, yoyo: true, repeat: -1 });
    }
  }

  update(time) {
    super.update(time);
    if (!this._controls || this.busy) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.message.isWaiting) {
      if (input === 'OK' || input === 'CANCEL') {
        this.message.handleConfirm(true);
      }
      return;
    }
    if (this.submenu) {
      const r = this.submenu.handleInput(input);
      if (r) {
        const choice = r.type === 'select' ? this.submenuItems[r.index] : 'CANCEL';
        this.submenu.destroy();
        this.submenu = null;
        this.#onSubmenu(choice);
      }
      return;
    }
    const n = dataManager.party.length;
    if (input === 'LEFT' || input === 'RIGHT') {
      const next = this.index ^ 1;
      if (next < n) {
        this.index = next;
      }
    } else if (input === 'UP') {
      this.index = this.index - 2 >= 0 ? this.index - 2 : this.index;
    } else if (input === 'DOWN') {
      this.index = this.index + 2 < n ? this.index + 2 : this.index;
    } else if (input === 'OK') {
      this.#onSelect();
      return;
    } else if (input === 'CANCEL') {
      if (this.swapFrom >= 0) {
        this.swapFrom = -1;
        this.#setDefaultMessage();
      } else if (this.sceneData.mode !== 'battle-forced') {
        this.#close({});
        return;
      }
    }
    this.#renderAll();
  }

  #onSelect() {
    const mon = dataManager.party[this.index];
    if (!mon) {
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    const mode = this.sceneData.mode;
    if (this.swapFrom >= 0) {
      const party = dataManager.party;
      [party[this.swapFrom], party[this.index]] = [party[this.index], party[this.swapFrom]];
      this.swapFrom = -1;
      this.#setDefaultMessage();
      this.#renderAll();
      return;
    }
    if (mode === 'use-item') {
      this.#useItemOn(mon);
      return;
    }
    if (mode === 'battle-forced') {
      if (mon.hp <= 0) {
        this.#flash(`${displayName(mon)} has no energy left to battle!`);
        return;
      }
      this.#close({ selectedIndex: this.index });
      return;
    }
    const items = mode === 'battle' ? ['SHIFT', 'SUMMARY', 'CANCEL'] : ['SUMMARY', 'SWITCH', 'CANCEL'];
    this.submenuItems = items;
    this.submenu = new ListMenu(this, { x: 1024 - 260, y: 470 - (items.length * 46 + 36) - 6, width: 250, items, depth: 20 });
    this.message.setText(`Do what with ${displayName(mon)}?`);
  }

  /** @param {string} choice */
  #onSubmenu(choice) {
    const mon = dataManager.party[this.index];
    this.#setDefaultMessage();
    if (choice === 'SUMMARY') {
      this.busy = true;
      this.events.once('resume', () => {
        this.busy = false;
        this.#renderAll();
      });
      this.scene.launch(SCENE_KEYS.MONSTER_DETAILS_SCENE, {
        previousSceneName: SCENE_KEYS.MONSTER_PARTY_SCENE,
        monsterIndex: this.index,
        list: 'party',
      });
      this.scene.pause();
      return;
    }
    if (choice === 'SWITCH') {
      this.swapFrom = this.index;
      this.#setDefaultMessage();
      this.#renderAll();
      return;
    }
    if (choice === 'SHIFT') {
      if (this.index === this.sceneData.activeIndex) {
        this.#flash(`${displayName(mon)} is already in battle!`);
        return;
      }
      if (mon.hp <= 0) {
        this.#flash(`${displayName(mon)} has no energy left to battle!`);
        return;
      }
      this.#close({ selectedIndex: this.index });
    }
  }

  /** @param {import('../battle/engine/monster.js').Monster} mon */
  async #useItemOn(mon) {
    const item = this.sceneData.item;
    // in battle the battle engine applies the item, here we only validate it would work
    const probe = JSON.parse(JSON.stringify(mon));
    const result = applyItem(probe, item);
    if (!result.ok) {
      await this.#flash(result.message);
      return;
    }
    if (this.sceneData.previousSceneName === SCENE_KEYS.BATTLE_SCENE || this.sceneData.returnTargetOnly) {
      this.#close({ selectedIndex: this.index });
      return;
    }
    applyItem(mon, item);
    dataManager.removeItem(item.id, 1);
    playSoundFx(this, AUDIO_KEYS.SFX_HEAL);
    this.#renderAll();
    await this.#flash(result.message);
    this.#close({ itemUsed: true });
  }

  /** @param {string} msg */
  async #flash(msg) {
    await this.message.show(msg, { wait: true });
    this.#setDefaultMessage();
  }

  /** @param {object} data */
  #close(data) {
    this.scene.stop();
    this.scene.resume(this.sceneData.previousSceneName, data);
  }
}

