import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { getItemByName } from '../game/game-data.js';
import { ListMenu, MessageBox, panel, readMenuInput, text, TEXT, HINTS } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { FULL_HEIGHT } from '../ui/screen.js';

/**
 * @typedef ShopSceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {string[]} items
 * @property {string} [greeting]
 */

export class ShopScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.SHOP_SCENE });
  }

  /** @param {ShopSceneData} data */
  init(data) {
    super.init();
    this.sceneData = data;
    this.stage = 'home';
    this.mode = 'BUY';
    this.quantity = 1;
    /** @type {import('../game/game-data.js').ItemData[]} */
    this.entries = [];
    /** @type {import('../game/game-data.js').ItemData | null} */
    this.selected = null;
    /** @type {ListMenu | null} */
    this.confirmMenu = null;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, FULL_HEIGHT, 0xe8bd79).setOrigin(0);
    const g = this.add.graphics();
    g.fillStyle(0xd9a65f, 1);
    for (let y = 0; y < FULL_HEIGHT; y += 32) {
      g.fillRect(0, y, 1024, 8);
    }
    text(this, 32, 20, 'NAMMA KIRANA', 'title');
    text(this, 34, 70, 'A little something for the journey.', 'small');
    panel(this, 748, 16, 260, 78);
    text(this, 770, 28, 'MONEY', 'small');
    this.moneyText = text(this, 984, 54, '', 'body').setOrigin(1, 0);

    this.homeMenu = new ListMenu(this, {
      x: 16, y: 108, width: 302, items: ['BUY', 'SELL', 'QUIT'], rowHeight: 52,
    });
    // Striped awning and jars give the little shop its own familiar corner.
    panel(this, 16, 314, 302, 106, { fill: 0xffebbb });
    const awning = this.add.graphics();
    awning.fillStyle(0x984951, 1);
    awning.fillRect(32, 326, 270, 18);
    for (let i = 0; i < 6; i += 1) {
      awning.fillStyle(i % 2 ? 0xfff4d6 : 0xc8545c, 1);
      awning.fillRoundedRect(32 + i * 45, 326, 45, 28, 6);
    }
    const jars = this.add.graphics();
    for (let i = 0; i < 4; i += 1) {
      jars.fillStyle([0x77a279, 0xc88f49, 0xb46f69, 0x8097b5][i], 1);
      jars.fillRoundedRect(40 + i * 42, 365, 28, 30, 5);
      jars.fillStyle(0x554666, 1);
      jars.fillRect(38 + i * 42, 360, 32, 7);
    }
    text(this, 226, 368, 'OPEN', 'small').setOrigin(0.5, 0);

    panel(this, 332, 108, 676, 312);
    this.list = new ListMenu(this, {
      x: 332, y: 108, width: 676, items: [], visibleRows: 6,
      withPanel: false,
      onChange: () => this.#updateDescription(),
    });
    this.emptyText = text(this, 368, 156, '', 'body').setWordWrapWidth(600).setLineSpacing(12);
    this.modal = this.add.container(0, 0).setDepth(20).setVisible(false);
    this.message = new MessageBox(this, { x: 0, y: 436, width: 1024, height: 140 });
    this.message.textObj.setStyle(TEXT.small).setLineSpacing(6);
    this.#showHome();
  }

  #showHome() {
    this.stage = 'home';
    this.selected = null;
    this.homeMenu.container.setAlpha(1);
    this.list.container.setVisible(false);
    this.modal.setVisible(false);
    this.emptyText.setVisible(true).setText('Welcome to your neighbourhood Kirana!\n\nBUY supplies or SELL spare items.');
    this.moneyText.setText(`₹${dataManager.money}`);
    this.message.setHints(HINTS.menu);
    this.message.setText(this.sceneData.greeting || 'Namaskara! What can I get you today?');
  }

  #showItems() {
    this.stage = 'items';
    this.selected = null;
    this.modal.setVisible(false);
    this.homeMenu.container.setAlpha(0.6);
    this.list.container.setVisible(true);
    this.message.setHints(HINTS.menu);
    if (this.mode === 'BUY') {
      this.entries = [...new Set(this.sceneData.items || [])]
        .map((name) => getItemByName(name))
        .filter((item) => Boolean(item));
    } else {
      this.entries = dataManager.getInventory(this)
        .filter((entry) => entry.item.category !== 'KEY')
        .map((entry) => entry.item);
    }
    const labels = this.entries.map((item) => item.name);
    const prices = this.entries.map((item) => `₹${this.#price(item)}`);
    labels.push('BACK');
    prices.push('');
    this.list.setItems(labels, prices);
    this.moneyText.setText(`₹${dataManager.money}`);
    this.emptyText.setVisible(this.entries.length === 0)
      .setText(this.mode === 'BUY' ? 'The shelves are empty today.' : 'You have no items to sell.');
    this.emptyText.setY(208);
    this.#updateDescription();
  }

  /** @param {import('../game/game-data.js').ItemData} item */
  #price(item) {
    return this.mode === 'SELL' ? Math.floor(item.price / 2) : item.price;
  }

  #updateDescription() {
    if (this.stage !== 'items') {
      return;
    }
    const item = this.entries[this.list.index];
    this.message.setText(item
      ? `${item.description}\nIn bag: ${dataManager.itemCount(item.id)}   •   ${this.mode === 'BUY' ? 'Buy' : 'Sell'} for ₹${this.#price(item)} each.`
      : 'Return to BUY / SELL / QUIT.');
  }

  #maxQuantity() {
    if (this.mode === 'SELL') {
      return dataManager.itemCount(this.selected.id);
    }
    const price = this.#price(this.selected);
    // Free items still use a finite batch; priced goods are bounded by the wallet.
    return price > 0 ? Math.max(1, Math.floor(dataManager.money / price)) : 99;
  }

  #showQuantity() {
    this.stage = 'quantity';
    this.list.container.setVisible(false);
    this.emptyText.setVisible(false);
    this.modal.removeAll(true);
    this.modal.setVisible(true);
    const price = this.#price(this.selected);
    this.modal.add([
      panel(this, 332, 108, 676, 312, { fill: 0xfff6dc }),
      text(this, 366, 130, this.mode === 'BUY' ? 'HOW MANY WOULD YOU LIKE?' : 'HOW MANY WILL YOU SELL?', 'small'),
      text(this, 366, 164, this.selected.name, 'body'),
      text(this, 972, 168, `₹${price} each`, 'small').setOrigin(1, 0),
      text(this, 366, 220, 'QUANTITY', 'small'),
      text(this, 366, 266, 'TOTAL', 'small'),
    ]);
    this.quantityText = text(this, 654, 210, '', 'title').setOrigin(1, 0);
    this.totalText = text(this, 654, 258, '', 'body').setOrigin(1, 0);
    this.modal.add([this.quantityText, this.totalText]);
    this.#refreshQuantity();
    this.message.setHints([{ key: '▲▼', label: '±1' }, { key: '◀ ▶', label: '±10' }, { btn: 'A', label: 'OK' }, { btn: 'B', label: 'Back' }]);
    this.message.setText(this.selected.description);
  }

  #refreshQuantity() {
    this.quantityText.setText(`×${this.quantity}`);
    this.totalText.setText(`₹${this.quantity * this.#price(this.selected)}`);
  }

  #showConfirmation() {
    this.stage = 'confirm';
    this.message.setHints(HINTS.menu);
    this.confirmMenu = new ListMenu(this, {
      x: 712, y: 278, width: 276, items: ['YES', 'NO'], rowHeight: 44, depth: 30,
    });
    this.message.setText(`${this.mode === 'BUY' ? 'Buy' : 'Sell'} ${this.quantity} × ${this.selected.name} for ₹${this.quantity * this.#price(this.selected)}?`);
  }

  async #trade() {
    const item = this.selected;
    const total = this.quantity * this.#price(item);
    let response;
    if (this.mode === 'BUY') {
      if (dataManager.money < total) {
        playSoundFx(this, AUDIO_KEYS.SFX_BUMP);
        await this.#notice("You don't have enough money for that.");
        return;
      }
      dataManager.addMoney(-total);
      dataManager.addItem(item.id, this.quantity);
      response = `Thank you! ${this.quantity} × ${item.name} went into your bag.`;
    } else {
      if (item.category === 'KEY' || !dataManager.removeItem(item.id, this.quantity)) {
        playSoundFx(this, AUDIO_KEYS.SFX_BUMP);
        await this.#notice('Those items are no longer available to sell.');
        return;
      }
      dataManager.addMoney(total);
      response = `Thank you! Sold ${this.quantity} × ${item.name} for ₹${total}.`;
    }
    this.moneyText.setText(`₹${dataManager.money}`);
    playSoundFx(this, AUDIO_KEYS.SFX_MONEY);
    await this.#notice(response);
  }

  /** @param {string} message */
  async #notice(message) {
    this.stage = 'message';
    await this.message.show(message, { wait: true });
    this.#showItems();
  }

  /** @param {number} time */
  update(time) {
    super.update(time);
    if (!this._controls) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.stage === 'message') {
      if (input === 'OK' || input === 'CANCEL') {
        this.message.handleConfirm(true);
      }
      return;
    }
    if (this.stage === 'confirm') {
      const result = this.confirmMenu.handleInput(input);
      if (!result) {
        return;
      }
      this.confirmMenu.destroy();
      this.confirmMenu = null;
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
      if (result.type === 'select' && result.index === 0) {
        this.#trade();
      } else {
        this.#showQuantity();
      }
      return;
    }
    if (this.stage === 'quantity') {
      if (input === 'CANCEL') {
        this.#showItems();
      } else if (input === 'OK') {
        playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
        this.#showConfirmation();
      } else {
        const change = { UP: 1, DOWN: -1, LEFT: -10, RIGHT: 10 }[input] ?? 0;
        this.quantity = Math.max(1, Math.min(this.#maxQuantity(), this.quantity + change));
        this.#refreshQuantity();
      }
      return;
    }
    const menu = this.stage === 'home' ? this.homeMenu : this.list;
    const result = menu.handleInput(input);
    if (!result) {
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    if (this.stage === 'home') {
      if (result.type === 'cancel' || result.index === 2) {
        this.scene.stop();
        this.scene.resume(this.sceneData.previousSceneName, {});
      } else {
        this.mode = result.index === 0 ? 'BUY' : 'SELL';
        this.list.setIndex(0);
        this.#showItems();
      }
    } else if (result.type === 'cancel' || result.index >= this.entries.length) {
      this.emptyText.setY(156);
      this.#showHome();
    } else {
      this.selected = this.entries[result.index];
      this.quantity = 1;
      this.#showQuantity();
    }
  }
}
