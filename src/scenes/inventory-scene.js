import Phaser from '../lib/phaser.js';
import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { ListMenu, MessageBox, panel, readMenuInput, text, HINTS } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';

/**
 * @typedef InventorySceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {'world'|'battle'} [mode='world']
 * @property {boolean} [isTrainerBattle]
 */

const POCKETS = [
  { name: 'ITEMS', categories: ['HEAL', 'STATUS', 'REVIVE', 'PP', 'REPEL'] },
  { name: 'DABBAS', categories: ['CAPTURE'] },
  { name: 'KEY ITEMS', categories: ['KEY'] },
];

export class InventoryScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.INVENTORY_SCENE });
  }

  /** @param {InventorySceneData} data */
  init(data) {
    super.init();
    this.sceneData = { mode: 'world', ...data };
    this.pocket = this.lastPocket ?? 0;
    /** @type {ListMenu | null} */
    this.actionMenu = null;
    this.busy = false;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0xe8c070).setOrigin(0);
    const g = this.add.graphics();
    g.fillStyle(0xd8a850, 1);
    for (let y = 0; y < 576; y += 24) {
      g.fillRect(0, y, 1024, 8);
    }
    // the bag: a cloth jhola
    const bag = this.add.graphics();
    bag.fillStyle(0x3a3058, 1);
    bag.fillRoundedRect(70, 130, 240, 200, 28);
    bag.fillStyle(0xc0505a, 1);
    bag.fillRoundedRect(78, 138, 224, 184, 24);
    bag.fillStyle(0xe8d070, 1);
    for (let i = 0; i < 4; i += 1) {
      bag.fillRect(90, 166 + i * 38, 200, 8);
    }
    bag.lineStyle(10, 0x3a3058, 1);
    bag.strokeEllipse(190, 130, 170, 110);
    this.pocketTitle = text(this, 190, 342, '', 'title').setOrigin(0.5, 0);
    this.pocketHint = text(this, 190, 388, '◀  pocket  ▶', 'small').setOrigin(0.5, 0);
    this.money = text(this, 40, 40, '', 'body');

    this.list = new ListMenu(this, {
      x: 380,
      y: 20,
      width: 630,
      items: [],
      visibleRows: 8,
      onChange: () => this.#updateDescription(),
    });
    this.desc = new MessageBox(this, { x: 0, y: 432, width: 1024, height: 144 });
    this.desc.setHints(HINTS.menu);
    this.#refresh();
  }

  #entries() {
    const cats = POCKETS[this.pocket].categories;
    return dataManager.getInventory(this).filter((e) => cats.includes(e.item.category));
  }

  #refresh() {
    this.entries = this.#entries();
    const labels = this.entries.map((e) => e.item.name);
    const qty = this.entries.map((e) => (e.item.category === 'KEY' ? '' : `x${e.quantity}`));
    labels.push('CLOSE BAG');
    qty.push('');
    this.list.setItems(labels, qty);
    this.pocketTitle.setText(POCKETS[this.pocket].name);
    this.money.setText(`₹${dataManager.money}`);
    this.#updateDescription();
  }

  #updateDescription() {
    const e = this.entries?.[this.list.index];
    this.desc.setText(e ? e.item.description : 'Close the bag.');
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
    if (this.desc.isWaiting) {
      if (input === 'OK' || input === 'CANCEL') {
        this.desc.handleConfirm(true);
      }
      return;
    }
    if (this.actionMenu) {
      const r = this.actionMenu.handleInput(input);
      if (r) {
        const choice = r.type === 'select' ? this.actionItems[r.index] : 'CANCEL';
        this.actionMenu.destroy();
        this.actionMenu = null;
        this.#onAction(choice);
      }
      return;
    }
    if (input === 'LEFT' || input === 'RIGHT') {
      this.pocket = (this.pocket + (input === 'LEFT' ? POCKETS.length - 1 : 1)) % POCKETS.length;
      this.lastPocket = this.pocket;
      this.list.setIndex(0);
      this.#refresh();
      return;
    }
    const r = this.list.handleInput(input);
    if (!r) {
      return;
    }
    if (r.type === 'cancel' || r.index >= this.entries.length) {
      this.#close({});
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    const entry = this.entries[r.index];
    this.selected = entry.item;
    const canUse = this.#canUseHere(entry.item);
    this.actionItems = canUse ? ['USE', 'CANCEL'] : ['CANCEL'];
    this.actionMenu = new ListMenu(this, { x: 1024 - 250, y: 432 - (this.actionItems.length * 46 + 36) - 4, width: 240, items: this.actionItems, depth: 30 });
    this.desc.setText(`${entry.item.name} is selected.`);
  }

  /** @param {import('../game/game-data.js').ItemData} item */
  #canUseHere(item) {
    if (this.sceneData.mode === 'battle') {
      return ['HEAL', 'STATUS', 'REVIVE', 'PP', 'CAPTURE'].includes(item.category);
    }
    return ['HEAL', 'STATUS', 'REVIVE', 'PP', 'REPEL', 'KEY'].includes(item.category);
  }

  /** @param {string} choice */
  async #onAction(choice) {
    const item = this.selected;
    if (choice !== 'USE' || !item) {
      this.#updateDescription();
      return;
    }
    if (this.sceneData.mode === 'battle') {
      if (item.category === 'CAPTURE') {
        this.#close({ item });
        return;
      }
      const target = await this.#pickTarget(item, true);
      if (target === undefined) {
        this.#refresh();
        return;
      }
      this.#close({ item, targetIndex: target });
      return;
    }
    // world use
    if (item.category === 'REPEL') {
      dataManager.removeItem(item.id, 1);
      dataManager.state.repelSteps = item.effect.steps;
      playSoundFx(this, AUDIO_KEYS.SFX_ITEM);
      await this.desc.show('You lit a Mosquito Coil. Weak wild Urumon will stay away for a while.');
      this.#refresh();
      return;
    }
    if (item.category === 'KEY') {
      await this.desc.show(item.name === 'Metro Card' ? 'Tap it at any Metro station to ride the train.' : "This isn't the time to use that.");
      this.#updateDescription();
      return;
    }
    if (dataManager.party.length === 0) {
      await this.desc.show('You have no Urumon to use that on.');
      this.#updateDescription();
      return;
    }
    await this.#pickTarget(item, false);
    this.#refresh();
  }

  /**
   * Opens the party to choose a target.
   * @param {import('../game/game-data.js').ItemData} item
   * @param {boolean} returnTargetOnly true in battle (the battle engine applies the item)
   * @returns {Promise<number | undefined>}
   */
  #pickTarget(item, returnTargetOnly) {
    return new Promise((resolve) => {
      this.busy = true;
      this.events.once(Phaser.Scenes.Events.RESUME, (sys, data) => {
        this.busy = false;
        resolve(data && data.selectedIndex !== undefined ? data.selectedIndex : undefined);
      });
      this.scene.launch(SCENE_KEYS.MONSTER_PARTY_SCENE, {
        previousSceneName: SCENE_KEYS.INVENTORY_SCENE,
        mode: 'use-item',
        item,
        returnTargetOnly,
      });
      this.scene.pause();
    });
  }

  /** @param {object} data */
  #close(data) {
    this.scene.stop();
    this.scene.resume(this.sceneData.previousSceneName, data);
  }
}
