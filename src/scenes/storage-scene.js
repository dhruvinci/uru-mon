import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { displayName, getSpecies } from '../battle/engine/monster.js';
import { ListMenu, MessageBox, panel, readMenuInput, text, HINTS } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { FULL_HEIGHT } from '../ui/screen.js';

/**
 * @typedef StorageSceneData
 * @type {object}
 * @property {string} previousSceneName
 */

const OPTIONS = ['WITHDRAW', 'DEPOSIT', 'MOVE OUT', 'QUIT'];
const VISIBLE_ROWS = 2;

export class StorageScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.STORAGE_SCENE });
  }

  /** @param {StorageSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    this.mode = 'WITHDRAW';
    this.phase = 'options';
    /** @type {'party'|'box'} */
    this.source = 'box';
    this.indices = { party: 0, box: 0 };
    this.tops = { party: 0, box: 0 };
    this.optionIndex = 0;
    this.busy = false;
    /** @type {ListMenu | null} */
    this.menu = null;
    this.menuItems = [];
    /** @type {{source: 'party'|'box', mon: import('../battle/engine/monster.js').Monster} | null} */
    this.selected = null;
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, FULL_HEIGHT, 0x78b8c8).setOrigin(0);
    const pattern = this.add.graphics();
    pattern.fillStyle(0x91cad5, 1);
    for (let y = 0; y < FULL_HEIGHT; y += 40) {
      for (let x = (y / 40) % 2 ? 20 : 0; x < 1024; x += 80) {
        pattern.fillRoundedRect(x, y, 48, 16, 8);
      }
    }
    panel(this, 12, 12, 1000, 62);
    text(this, 34, 20, 'Namma Cloud', 'title');
    this.modeText = text(this, 980, 30, '', 'small').setOrigin(1, 0);
    this.cardsRoot = this.add.container(0, 0);
    this.message = new MessageBox(this, { y: 462, height: 114 });
    this.message.textObj.setFontSize(22);
    this.#showOptions();
  }

  /** @param {'party'|'box'} source */
  #list(source) {
    return source === 'party' ? dataManager.party : dataManager.boxes;
  }

  #render() {
    this.cardsRoot.removeAll(true);
    this.modeText.setText(this.phase === 'options' ? 'Your Urumon, close to home.' : this.mode);
    for (const source of /** @type {const} */ (['party', 'box'])) {
      const list = this.#list(source);
      const x = source === 'party' ? 12 : 518;
      const active = this.phase !== 'options' && this.source === source;
      this.indices[source] = Math.min(this.indices[source], Math.max(0, list.length - 1));
      this.tops[source] = Math.max(0, Math.min(this.tops[source], Math.max(0, list.length - VISIBLE_ROWS)));
      if (this.indices[source] < this.tops[source]) {
        this.tops[source] = this.indices[source];
      } else if (this.indices[source] >= this.tops[source] + VISIBLE_ROWS) {
        this.tops[source] = this.indices[source] - VISIBLE_ROWS + 1;
      }
      const add = (o) => this.cardsRoot.add(o);
      add(panel(this, x, 84, 494, 368, { fill: active ? 0xeaf8f5 : 0xe3edf1, border: active ? 0xc67b35 : 0x3a3058 }));
      add(text(this, x + 22, 96, source === 'party' ? `PARTY  ${list.length}/6` : `CLOUD BOX  ${list.length}`, 'body'));
      if (!list.length) {
        add(text(this, x + 247, 250, source === 'box' ? 'The cloud is empty.' : 'No Urumon here.', 'small').setOrigin(0.5));
      }
      for (let row = 0; row < VISIBLE_ROWS; row += 1) {
        const index = this.tops[source] + row;
        const mon = list[index];
        if (!mon) {
          continue;
        }
        const y = 138 + row * 138;
        const highlighted = active && index === this.indices[source];
        add(panel(this, x + 12, y, 470, 134, {
          fill: highlighted ? 0xfff3cc : 0xfbfaf6,
          border: highlighted ? 0xc67b35 : 0x9b8fd0,
        }));
        const key = getSpecies(mon.speciesId).assetKey;
        add(this.add.image(x + 82, y + 67, this.textures.exists(key) ? key : '__MISSING').setScale(2));
        const name = displayName(mon);
        add(text(this, x + 154, y + 16, name.length > 21 ? `${name.slice(0, 20)}…` : name, 'small'));
        add(text(this, x + 154, y + 53, `Lv${mon.level}`, 'body'));
        add(text(this, x + 154, y + 94, mon.hp > 0 ? `HP ${mon.hp}${mon.status ? `  ${mon.status}` : ''}` : 'FAINTED', 'small'));
      }
      const first = list.length ? this.tops[source] + 1 : 0;
      const last = Math.min(this.tops[source] + VISIBLE_ROWS, list.length);
      const above = this.tops[source] > 0 ? '▲ ' : '';
      const below = last < list.length ? ' ▼' : '';
      add(text(this, x + 247, 422, `${above}${first}–${last} / ${list.length}${below}`, 'small').setOrigin(0.5, 0));
    }
  }

  #defaultMessage() {
    this.message.setHints([{ key: '▲▼', label: 'Choose' }, { key: '◀ ▶', label: 'Party / Box' }, { btn: 'A', label: 'Actions' }, { btn: 'B', label: 'Menu' }]);
    this.message.setText(this.mode === 'WITHDRAW' ? 'Pick an Urumon to bring home.' : this.mode === 'DEPOSIT' ? 'Pick an Urumon to rest in the cloud.' : 'Pick an Urumon.');
  }

  /** @param {string[]} items @param {number} [x=690] */
  #openMenu(items, x = 690) {
    this.menu?.destroy();
    this.menuItems = items;
    this.menu = new ListMenu(this, {
      x, y: 450 - (items.length * 46 + 36), width: 310, items, depth: 30,
    });
    this.message.setHints(HINTS.menu);
  }

  #showOptions() {
    this.phase = 'options';
    this.selected = null;
    this.#render();
    this.#openMenu(OPTIONS, 357);
    this.menu.setIndex(this.optionIndex);
    this.message.setText('Welcome! Withdraw, deposit, or say goodbye to an Urumon.');
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
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    if (this.phase === 'notice') {
      if (input === 'OK' || input === 'CANCEL') {
        this.phase = 'browse';
        this.#defaultMessage();
      }
      return;
    }
    if (this.menu) {
      const result = this.menu.handleInput(input);
      if (!result) {
        return;
      }
      const choice = result.type === 'select' ? this.menuItems[result.index] : 'CANCEL';
      if (this.phase === 'options') {
        this.optionIndex = this.menu.index;
      }
      this.menu.destroy();
      this.menu = null;
      this.#choose(choice);
      return;
    }
    if (input === 'CANCEL') {
      this.#showOptions();
      return;
    }
    if (input === 'LEFT' || input === 'RIGHT') {
      this.source = input === 'LEFT' ? 'party' : 'box';
    } else if (input === 'UP' || input === 'DOWN') {
      const n = this.#list(this.source).length;
      if (n) {
        this.indices[this.source] = (this.indices[this.source] + (input === 'UP' ? n - 1 : 1)) % n;
      }
    } else if (input === 'OK') {
      this.#selectMonster();
      return;
    }
    this.#render();
  }

  /** @param {string} choice */
  #choose(choice) {
    if (this.phase === 'options') {
      if (choice === 'QUIT' || choice === 'CANCEL') {
        this.scene.stop();
        this.scene.resume(this.sceneData.previousSceneName, {});
        return;
      }
      this.mode = choice;
      this.source = choice === 'DEPOSIT' ? 'party' : 'box';
      this.phase = 'browse';
      this.#render();
      this.#defaultMessage();
      return;
    }
    const confirming = this.phase === 'confirm';
    this.phase = 'browse';
    this.#defaultMessage();
    if (choice === 'CANCEL' || choice === 'KEEP') {
      this.selected = null;
      return;
    }
    const selection = this.selected;
    if (!selection || !this.#list(selection.source).includes(selection.mon)) {
      this.selected = null;
      this.#render();
      return;
    }
    if (choice === 'SUMMARY') {
      this.busy = true;
      this.scene.launch(SCENE_KEYS.MONSTER_DETAILS_SCENE, {
        previousSceneName: SCENE_KEYS.STORAGE_SCENE,
        monsterIndex: this.#list(selection.source).indexOf(selection.mon),
        list: selection.source,
      });
      this.scene.pause();
      return;
    }
    if (choice === 'MOVE OUT' && !confirming) {
      if (!this.#canRemove(selection)) {
        return;
      }
      this.phase = 'confirm';
      this.#openMenu(['KEEP', 'RELEASE']);
      this.message.setText(`Release ${displayName(selection.mon)} forever? This cannot be undone.`);
      return;
    }
    if (choice === 'WITHDRAW') {
      if (dataManager.isPartyFull()) {
        this.#notice('Your party is full! Deposit an Urumon first.', true);
        return;
      }
      dataManager.party.push(selection.mon);
    } else if (choice === 'DEPOSIT') {
      if (!this.#canRemove(selection)) {
        return;
      }
      dataManager.boxes.push(selection.mon);
    } else if (!(choice === 'RELEASE' && confirming && this.#canRemove(selection))) {
      return;
    }
    const source = this.#list(selection.source);
    source.splice(source.indexOf(selection.mon), 1);
    const name = displayName(selection.mon);
    this.selected = null;
    this.#render();
    this.#notice(choice === 'RELEASE' ? `Bye-bye, ${name}!` : choice === 'WITHDRAW' ? `${name} joined your party!` : `${name} is resting in Namma Cloud.`);
  }

  #selectMonster() {
    const mon = this.#list(this.source)[this.indices[this.source]];
    if (!mon) {
      this.#notice(this.source === 'box' ? 'The cloud is empty. Deposit an Urumon to fill it.' : 'There are no Urumon in your party.', true);
      return;
    }
    this.selected = { source: this.source, mon };
    const canAct = this.mode === 'MOVE OUT' || (this.mode === 'WITHDRAW' && this.source === 'box') || (this.mode === 'DEPOSIT' && this.source === 'party');
    this.phase = 'actions';
    this.#openMenu(canAct ? [this.mode, 'SUMMARY', 'CANCEL'] : ['SUMMARY', 'CANCEL']);
    this.message.setText(`Do what with ${displayName(mon)}?`);
  }

  /** @param {{source: 'party'|'box', mon: import('../battle/engine/monster.js').Monster}} selection */
  #canRemove(selection) {
    if (selection.source === 'party' && !dataManager.party.some((mon) => mon !== selection.mon && mon.hp > 0)) {
      this.#notice('Keep at least one non-fainted Urumon in your party!', true);
      return false;
    }
    return true;
  }

  /** @param {string} message @param {boolean} [error=false] */
  #notice(message, error = false) {
    this.phase = 'notice';
    this.message.setHints([{ btn: 'A', label: 'OK' }]);
    this.message.setText(message);
    playSoundFx(this, error ? AUDIO_KEYS.SFX_BUMP : AUDIO_KEYS.SFX_SELECT);
  }

  /** @param {Phaser.Scenes.Systems} sys @param {object} [data] */
  handleSceneResume(sys, data) {
    super.handleSceneResume(sys, data);
    if (this.busy) {
      this.busy = false;
      this.selected = null;
      this.phase = 'browse';
      this.#render();
      this.#defaultMessage();
    }
  }
}
