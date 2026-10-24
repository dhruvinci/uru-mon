import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { getItemByName } from '../game/game-data.js';
import { ListMenu, MessageBox, panel, readMenuInput, text, HINTS } from '../ui/ui-kit.js';
import { playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';

/**
 * @typedef MetroSceneData
 * @type {object}
 * @property {string} previousSceneName
 * @property {string} [current]
 */

const STATIONS = [
  { id: 'basavanagudi', name: 'Basavanagudi', x: 120, y: 382 },
  { id: 'lalbagh', name: 'Lalbagh', x: 230, y: 322 },
  { id: 'mg_road', name: 'MG Road', x: 310, y: 262 },
  { id: 'whitefield', name: 'Whitefield', x: 450, y: 262 },
  { id: 'malleshwaram', name: 'Malleshwaram', x: 190, y: 202 },
  { id: 'palace_road', name: 'Palace Road', x: 310, y: 142 },
];

export class MetroScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.METRO_SCENE });
  }

  /** @param {MetroSceneData} data */
  init(data) {
    super.init();
    this.sceneData = { ...data };
    this.closed = false;
    this.stations = STATIONS.filter((station) => dataManager.state.metroStations.includes(station.id));
    const card = getItemByName('Metro Card');
    this.hasCard = Boolean(card && dataManager.itemCount(card.id) > 0);
  }

  create() {
    super.create();
    this.add.rectangle(0, 0, 1024, 576, 0x6d5795).setOrigin(0);
    const pattern = this.add.graphics().fillStyle(0x7f6aa8, 1);
    for (let x = 0; x < 1024; x += 48) {
      pattern.fillRect(x, 0, 12, 576);
    }
    text(this, 32, 24, 'NAMMA METRO', 'title').setColor('#ffffff');
    panel(this, 24, 100, 510, 350, { fill: 0xeee9fa });
    this.map = this.add.graphics();
    this.mapNumbers = this.stations.map((station, index) =>
      text(this, station.x, station.y, String(index + 1), 'small').setOrigin(0.5),
    );
    this.list = new ListMenu(this, {
      x: 552, y: 100, width: 448, visibleRows: 6, rowHeight: 50,
      items: this.stations.map((station, index) => `${index + 1}. ${station.name}`),
      onChange: () => this.#refresh(),
    });
    this.message = new MessageBox(this, { y: 470, height: 106 });
    this.message.setHints(this.hasCard ? [{ btn: 'A', label: 'Ride' }, { btn: 'B', label: 'Back' }] : HINTS.back);
    if (!this.hasCard) {
      this.message.setText('Please tap a Metro Card to ride.');
    }
    const currentIndex = this.stations.findIndex((station) => station.id === this.sceneData.current);
    this.list.setIndex(Math.max(0, currentIndex));
  }

  #refresh() {
    const selected = this.stations[this.list.index];
    const g = this.map;
    g.clear();
    g.lineStyle(14, 0x8d4ab8, 1);
    g.beginPath();
    g.moveTo(90, 400);
    g.lineTo(230, 322);
    g.lineTo(310, 262);
    g.lineTo(484, 262);
    g.strokePath();
    g.lineStyle(14, 0x49a879, 1);
    g.beginPath();
    g.moveTo(160, 202);
    g.lineTo(250, 202);
    g.lineTo(310, 262);
    g.lineTo(310, 124);
    g.strokePath();
    this.stations.forEach((station) => {
      g.fillStyle(station.id === this.sceneData.current ? 0xe9ad40 : 0x3a3058, 1);
      g.fillCircle(station.x, station.y, station === selected ? 24 : 19);
      g.fillStyle(station === selected ? 0xffffff : 0xe0d8f2, 1);
      g.fillCircle(station.x, station.y, station === selected ? 18 : 14);
    });
    if (!this.hasCard) {
      return;
    }
    this.message.setText(!selected ? 'No stations visited yet.' :
      selected.id === this.sceneData.current ? `${selected.name}: you are here.` : `Ride to ${selected.name}?`);
  }

  update(time) {
    super.update(time);
    if (!this._controls || this.closed) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (!this.hasCard) {
      if (input === 'OK' || input === 'CANCEL') {
        this.#close({});
      }
      return;
    }
    const oldIndex = this.list.index;
    const result = this.list.handleInput(input);
    if (oldIndex !== this.list.index) {
      playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    }
    if (result?.type === 'cancel') {
      this.#close({});
    } else if (result?.type === 'select') {
      const station = this.stations[result.index];
      if (station.id !== this.sceneData.current) {
        this.#close({ station: { area: station.id, warpId: 'metro' } });
      }
    }
  }

  /** @param {{station?: {area: string, warpId: string}}} result */
  #close(result) {
    if (this.closed) {
      return;
    }
    this.closed = true;
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    this.scene.stop();
    this.scene.resume(this.sceneData.previousSceneName, result);
  }
}
