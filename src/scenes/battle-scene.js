import Phaser from '../lib/phaser.js';
import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { Battle } from '../battle/engine/battle-engine.js';
import {
  displayName,
  expYield,
  gainExp,
  getMaxHp,
  getMove,
  getSpecies,
  pendingEvolution,
  evolve,
  generateUid,
} from '../battle/engine/monster.js';
import { BattleHud } from '../battle/ui/battle-hud.js';
import { playMoveFx, shakeAndBlink, statChangeFx, statusFx } from '../battle/ui/move-fx.js';
import { MessageBox, ListMenu, panel, text, typeBadge, readMenuInput, wait, tween, cursor, ControlHints, HINTS } from '../ui/ui-kit.js';
import { promptLearnMove } from '../ui/learn-move.js';
import { dataManager } from '../utils/data-manager.js';
import { inputManager } from '../input/input-manager.js';
import { graphicsSetting, timeOfDay } from '../fx/world-fx.js';
import { bestArt, loadHd, monHdKey, trainerHdKey, HD_FACTOR } from '../ui/hd-art.js';
import { BATTLE_SCENE_OPTIONS, BATTLE_STYLE_OPTIONS } from '../common/options.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS, UI_KEYS } from '../assets/asset-keys.js';
import { FULL_HEIGHT, GAME_WIDTH, isTall, onResize, setTextResolution, uiScale } from '../ui/screen.js';

/**
 * @typedef TrainerBattleInfo
 * @type {object}
 * @property {string} id
 * @property {string} name
 * @property {string} [title] trainer class shown before the name
 * @property {string} portrait texture key
 * @property {string} [sprite] overworld CHAR_ preset, used when the portrait is missing
 * @property {import('../battle/engine/monster.js').Monster[]} team
 * @property {number} prize
 * @property {string[]} defeatText
 * @property {number} [aiLevel]
 * @property {boolean} [isLeader]
 */

/**
 * @typedef BattleSceneData
 * @type {object}
 * @property {import('../battle/engine/monster.js').Monster} [wild]
 * @property {TrainerBattleInfo} [trainer]
 * @property {string} [environment]
 * @property {boolean} [canLose] story battles where losing doesn't black you out
 * @property {string} [music]
 * @property {boolean} [quick] Quick Battle from the title screen: no EXP (prize 0 and canLose are set by the caller)
 */

/**
 * @typedef BattleResult
 * @type {object}
 * @property {'win'|'lose'|'fled'|'caught'} outcome
 * @property {string} [trainerId]
 * @property {boolean} [canLose]
 */

const MAIN_OPTIONS = ['FIGHT', 'BAG', 'PARTY', 'RUN'];
/** Where trainers wait before sliding in, and go after. */
const OFF_RIGHT = 1350;

/**
 * @typedef {{x: number, y: number}} Point
 * @typedef BattleLayout
 * @type {object}
 * @property {boolean} tall laid out for a tall canvas
 * @property {number} k how much bigger the HUDs, menus and text are drawn
 * @property {number} height of the whole layout
 * @property {number} field height of the battlefield; the message box and menus fill the rest
 * @property {number} uiHeight height of the message box and menus, before scaling by k
 * @property {number} sprite scale of the creature art
 * @property {number} bgScale scale of the backdrop art
 * @property {Point} enemy where the creatures and the trainer stand (their feet)
 * @property {Point} player
 * @property {Point} trainer
 * @property {Point} enemyHud
 * @property {Point} playerHud
 * @property {Point} evolve
 */

/**
 * The 1024x576 battle, or on a tall canvas (a phone held upright) a taller field with bigger creatures, and the
 * HUDs, menus and text drawn k times bigger.
 * @param {Phaser.Scene} scene
 * @returns {BattleLayout}
 */
function battleLayout(scene) {
  const k = uiScale(scene);
  if (!isTall(scene)) {
    return {
      tall: false, k, height: 576, field: 432, uiHeight: 144, sprite: 4, bgScale: 4,
      enemy: { x: 760, y: 236 }, player: { x: 250, y: 440 }, trainer: { x: 760, y: 318 },
      enemyHud: { x: 28, y: 26 }, playerHud: { x: 548, y: 276 }, evolve: { x: 512, y: 330 },
    };
  }
  const height = scene.scale.height;
  const uiHeight = 200;
  const field = Math.round(height - uiHeight * k);
  // bigger creatures when there's room; the enemy stands low enough for its 64-pixel art to fit under the top edge
  const sprite = field >= 640 ? 5 : 4;
  const enemyY = Math.max(Math.round(field * 0.53), 64 * sprite + 24);
  return {
    tall: true, k, height, field, uiHeight, sprite, bgScale: Math.max(4, Math.ceil(field / 108)),
    enemy: { x: 760, y: enemyY }, player: { x: 240, y: field - 8 }, trainer: { x: 760, y: enemyY + 100 },
    enemyHud: { x: 20, y: 20 }, playerHud: { x: Math.round(GAME_WIDTH - 452 * k - 16), y: Math.round(field - 142 * k - 24) },
    evolve: { x: 512, y: Math.round(field * 0.78) },
  };
}

export class BattleScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.BATTLE_SCENE });
  }

  /** @param {BattleSceneData} data */
  init(data) {
    super.init();
    /** @type {BattleSceneData} */
    this.data_ = data;
    this.skipAnim = dataManager.state.options.battleSceneAnimations === BATTLE_SCENE_OPTIONS.OFF;
    /** @type {null | ((input: string) => void)} */
    this.inputHandler = null;
    this.levelledUp = new Set();
    this.finished = false;
  }

  create() {
    super.create();
    const L = battleLayout(this);
    this.L = L;
    setTextResolution(this, L.k);
    this.#fitCamera();
    onResize(this, () => this.#fitCamera());
    const d = this.data_;
    const party = dataManager.party;
    this.isTrainer = Boolean(d.trainer);
    const enemyParty = this.isTrainer ? d.trainer.team : [d.wild];
    this.battle = new Battle({
      playerParty: party,
      enemyParty,
      isTrainer: this.isTrainer,
      aiLevel: this.isTrainer ? d.trainer.aiLevel ?? 1 : 0,
    });

    this.#createBackground(d.environment || 'grass');
    this.#atmosphere(d.environment || 'grass');
    this.enemySprite = this.add.image(L.enemy.x, L.enemy.y, getSpecies(this.battle.enemyActive.speciesId).assetKey).setOrigin(0.5, 1).setScale(L.sprite).setDepth(10);
    this.playerSprite = this.add.image(L.player.x, L.player.y, getSpecies(this.battle.playerActive.speciesId).assetKey).setOrigin(0.5, 1).setScale(L.sprite).setFlipX(true).setDepth(11);
    this.enemySprite.setVisible(false);
    this.playerSprite.setVisible(false);
    if (this.isTrainer) {
      const hasPortrait = this.textures.exists(d.trainer.portrait);
      const fallback = `CHAR_${d.trainer.sprite || 'man1'}`;
      this.trainerSprite = hasPortrait
        ? this.add.image(L.trainer.x, L.trainer.y, d.trainer.portrait).setOrigin(0.5, 1).setScale(L.sprite)
        : this.add.image(L.trainer.x, L.trainer.y, fallback, 0).setOrigin(0.5, 1).setScale((9 * L.sprite) / 4); // 16x32 -> portrait height
      this.trainerSprite.setDepth(10).setVisible(false);
    }
    // sharper art: fetch the HD pictures for everyone in this battle (and what the party could evolve into)
    const ids = [...party, ...this.battle.sides.enemy.party].map((m) => m.speciesId);
    party.forEach((m) => getSpecies(m.speciesId).evolution && ids.push(getSpecies(m.speciesId).evolution.speciesId));
    const hdKeys = ids.map(monHdKey);
    if (this.isTrainer && d.trainer.portrait?.startsWith('TRAINER_')) {
      hdKeys.push(trainerHdKey(d.trainer.portrait.slice('TRAINER_'.length)));
    }
    loadHd(this, hdKeys).then(() => this.#upgradeArt());

    this.enemyHud = new BattleHud(this, 'enemy', L.enemyHud, L.k);
    this.playerHud = new BattleHud(this, 'player', L.playerHud, L.k);
    this.messageBox = new MessageBox(this, { y: L.field, width: GAME_WIDTH / L.k, height: L.uiHeight });
    this.messageBox.container.setScale(L.k);
    this.messageBox.setAnnounces(!L.tall); // big enough to read on its own
    this.tapZone = this.add.zone(0, 0, GAME_WIDTH, L.height).setOrigin(0).setDepth(55).setInteractive();
    this.tapZone.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => {
      if (this.messageBox.isWaiting && p.getDistance() < 24) {
        inputManager.tap('A');
      }
    });
    this.messageBox.setText('');
    this.#createPartyIndicators();

    const music = d.music || (this.isTrainer ? (d.trainer.isLeader ? AUDIO_KEYS.MUSIC_LEADER : AUDIO_KEYS.MUSIC_TRAINER) : AUDIO_KEYS.MUSIC_WILD);
    playBackgroundMusic(this, music);

    this.#run().catch((err) => {
      console.error('[BattleScene] battle flow crashed', err);
      this.#finish({ outcome: 'fled' });
    });
  }

  /**
   * Fits the layout to the canvas. They match, except when the phone turns mid-battle: the battle then carries on in the
   * layout it started with, shrunk to fit or at the top.
   */
  #fitCamera() {
    const cam = this.cameras.main;
    const H = this.scale.height;
    const zoom = Math.min(1, H / this.L.height);
    const width = GAME_WIDTH * zoom;
    cam.setViewport((GAME_WIDTH - width) / 2, 0, width, H).setZoom(zoom);
    cam.centerOn(GAME_WIDTH / 2, zoom < 1 ? this.L.height / 2 : H / 2);
  }

  update(time) {
    super.update(time);
    if (this.tapZone) {
      // tapping anywhere advances a waiting message; menus sit above and take their own taps
      this.tapZone.input.enabled = this.messageBox.isWaiting;
    }
    if (!this._controls) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.messageBox.isWaiting && (input === 'OK' || input === 'CANCEL')) {
      this.messageBox.handleConfirm(true);
      return;
    }
    if (this.inputHandler) {
      this.inputHandler(input);
    }
  }

  // ------------------------------------------------------------------------------------------
  // scenery
  // ------------------------------------------------------------------------------------------

  /** @param {string} env */
  #createBackground(env) {
    const L = this.L;
    const key = `BATTLE_BG_${env.toUpperCase()}`;
    if (this.textures.exists(key)) {
      // a tall field shows the middle of the scene, bigger
      this.add.image(GAME_WIDTH / 2, 0, key).setOrigin(0.5, 0).setScale(L.bgScale);
    } else {
      const g = this.add.graphics();
      g.fillGradientStyle(0xa8d8f0, 0xa8d8f0, 0xe8f4d8, 0xe8f4d8, 1);
      g.fillRect(0, 0, GAME_WIDTH, L.field);
    }
    const g = this.add.graphics().setDepth(5);
    // platforms the creatures stand on
    const f = L.sprite / 4;
    g.fillStyle(0x000000, 0.18);
    g.fillEllipse(L.enemy.x, L.enemy.y - 8 * f, 330 * f, 70 * f);
    g.fillEllipse(L.player.x, L.player.y - 8 * f, 390 * f, 80 * f);
  }

  #createPartyIndicators() {
    const { k, playerHud, enemyHud } = this.L;
    /** @param {import('../battle/engine/monster.js').Monster[]} team @param {number} x @param {number} y @param {number} dir */
    const make = (team, x, y, dir) => {
      const c = this.add.container(x, y).setDepth(21);
      for (let i = 0; i < 6; i += 1) {
        const m = team[i];
        const key = UI_KEYS.DABBA;
        const icon = this.textures.exists(key)
          ? this.add.image(dir * i * 36, 0, key).setScale(2)
          : this.add.circle(dir * i * 36, 0, 12, 0xd0d0d8).setStrokeStyle(3, 0x3a3058);
        icon.setAlpha(!m ? 0.15 : m.hp > 0 ? 1 : 0.4);
        c.add(icon);
      }
      c.setVisible(false).setScale(k);
      return c;
    };
    // above the player's HUD, and under the trainer's
    this.playerBalls = make(dataManager.party, GAME_WIDTH - 44 * k, playerHud.y - 14 * k, -1);
    this.enemyBalls = this.isTrainer ? make(this.data_.trainer.team, enemyHud.x + 24 * k, enemyHud.y + 124 * k, 1) : null;
  }

  #refreshPartyIndicators() {
    /** @param {Phaser.GameObjects.Container | null} c @param {import('../battle/engine/monster.js').Monster[]} team */
    const upd = (c, team) => {
      if (!c) {
        return;
      }
      c.list.forEach((icon, i) => {
        const m = team[i];
        /** @type {any} */ (icon).setAlpha(!m ? 0.15 : m.hp > 0 ? 1 : 0.4);
      });
    };
    upd(this.playerBalls, dataManager.party);
    upd(this.enemyBalls, this.isTrainer ? this.data_.trainer.team : []);
  }

  // ------------------------------------------------------------------------------------------
  // dialog helpers
  // ------------------------------------------------------------------------------------------

  /** @param {string} msg */
  say(msg) {
    return this.messageBox.show(msg, { wait: true });
  }

  /** @param {string} msg */
  note(msg) {
    return this.messageBox.show(msg, { wait: false, pause: this.skipAnim ? 250 : 550 });
  }

  /**
   * Shows a small choice list over the bottom-right corner.
   * @param {string[]} items
   * @param {{cancelable?: boolean, title?: string}} [opts]
   * @returns {Promise<number>}
   */
  choose(items, opts = {}) {
    return new Promise((resolve) => {
      const { k, field } = this.L;
      const width = Math.max(220, ...items.map((s) => s.length * 17 + 90));
      const menu = new ListMenu(this, { x: 0, y: 0, width, items, cancelable: opts.cancelable ?? true, depth: 80 });
      menu.container.setScale(k).setPosition(GAME_WIDTH - (width + 12) * k, field - (menu.height + 8) * k);
      if (opts.title) {
        this.messageBox.setText(opts.title);
      }
      this.messageBox.setHints(opts.cancelable ?? true ? HINTS.menu : HINTS.select);
      this.inputHandler = (input) => {
        const r = menu.handleInput(/** @type {any} */ (input));
        if (!r) {
          return;
        }
        this.inputHandler = null;
        this.messageBox.setHints([]);
        menu.destroy();
        resolve(r.type === 'select' ? r.index : -1);
      };
    });
  }

  // ------------------------------------------------------------------------------------------
  // main flow
  // ------------------------------------------------------------------------------------------

  async #run() {
    await this.#intro();
    for (;;) {
      const action = await this.#chooseAction();
      if (!action) {
        continue;
      }
      const { events, fled, caught } = this.battle.resolveTurn(action);
      await this.#playEvents(events);
      if (fled) {
        playSoundFx(this, AUDIO_KEYS.SFX_RUN);
        return this.#finish({ outcome: 'fled' });
      }
      if (caught) {
        await this.#onCaught();
        return this.#finish({ outcome: 'caught' });
      }
      const done = await this.#afterTurn();
      if (done) {
        return;
      }
    }
  }

  async #intro() {
    const d = this.data_;
    const enemy = this.battle.enemyActive;
    dataManager.markSeen(enemy.speciesId);
    await this.#fadeInFromBlack();
    if (this.isTrainer) {
      this.trainerSprite.setVisible(true).setX(OFF_RIGHT);
      await tween(this, { targets: this.trainerSprite, x: this.L.trainer.x, duration: this.skipAnim ? 1 : 600, ease: 'Cubic.out' });
      this.enemyBalls?.setVisible(true);
      const who = d.trainer.title ? `${d.trainer.title} ${d.trainer.name}` : d.trainer.name;
      await this.say(`${who} wants to battle!`);
      await tween(this, { targets: this.trainerSprite, x: OFF_RIGHT, duration: this.skipAnim ? 1 : 450, ease: 'Cubic.in' });
      this.trainerSprite.setVisible(false);
      await this.#sendOut('enemy', `${d.trainer.name} sent out ${displayName(enemy)}!`);
    } else {
      this.enemySprite.setVisible(true).setX(OFF_RIGHT);
      await tween(this, { targets: this.enemySprite, x: this.L.enemy.x, duration: this.skipAnim ? 1 : 700, ease: 'Cubic.out' });
      this.enemyHud.bind(enemy);
      await this.enemyHud.slideIn();
      await this.say(`A wild ${displayName(enemy)} appeared!`);
    }
    await this.#sendOut('player', `Go! ${displayName(this.battle.playerActive)}!`);
  }

  #fadeInFromBlack() {
    if (this.skipAnim) {
      return Promise.resolve();
    }
    const cover = this.add.rectangle(0, 0, GAME_WIDTH, FULL_HEIGHT, 0x000000).setOrigin(0).setDepth(100);
    return tween(this, { targets: cover, alpha: 0, duration: 450 }).then(() => cover.destroy());
  }

  /**
   * @param {'player'|'enemy'} side
   * @param {string} message
   */
  async #sendOut(side, message) {
    const mon = this.battle.active(side);
    const sprite = side === 'player' ? this.playerSprite : this.enemySprite;
    const hud = side === 'player' ? this.playerHud : this.enemyHud;
    const home = side === 'player' ? this.L.player : this.L.enemy;
    dataManager.markSeen(mon.speciesId);
    const art = this.#monArt(mon.speciesId);
    sprite.setTexture(art.key).setPosition(home.x, home.y).setVisible(true).setAlpha(1);
    const scale = art.scale;
    if (side === 'player') {
      this.playerBalls.setVisible(true);
    }
    this.messageBox.setText(message);
    playSoundFx(this, AUDIO_KEYS.SFX_SEND_OUT);
    if (!this.skipAnim) {
      sprite.setScale(0.2).setTintFill(0xffffff);
      await tween(this, { targets: sprite, scale, duration: 320, ease: 'Back.out' });
      sprite.clearTint();
    } else {
      sprite.setScale(scale);
    }
    hud.bind(mon);
    await hud.slideIn();
    await wait(this, 350);
  }

  /** @returns {Promise<import('../battle/engine/battle-engine.js').BattleAction | null>} */
  async #chooseAction() {
    const mon = this.battle.playerActive;
    for (;;) {
      this.messageBox.setText(`What will ${displayName(mon)} do?`);
      const choice = await this.#mainMenu();
      if (choice === 'FIGHT') {
        if (mon.moves.every((m) => m.pp <= 0)) {
          await this.say(`${displayName(mon)} has no moves left!`);
          return { kind: 'MOVE', slot: -1 };
        }
        const slot = await this.#moveMenu();
        if (slot >= 0) {
          return { kind: 'MOVE', slot };
        }
        continue;
      }
      if (choice === 'BAG') {
        const result = await this.#openSub(SCENE_KEYS.INVENTORY_SCENE, {
          previousSceneName: SCENE_KEYS.BATTLE_SCENE,
          mode: 'battle',
          isTrainerBattle: this.isTrainer,
        });
        if (!result || !result.item) {
          continue;
        }
        if (result.item.category === 'CAPTURE') {
          if (this.isTrainer) {
            await this.say("You can't catch another trainer's Urumon!");
            continue;
          }
          dataManager.removeItem(result.item.id, 1);
          return { kind: 'CATCH', item: result.item };
        }
        dataManager.removeItem(result.item.id, 1);
        return { kind: 'ITEM', item: result.item, targetIndex: result.targetIndex ?? this.battle.sides.player.active };
      }
      if (choice === 'PARTY') {
        const result = await this.#openSub(SCENE_KEYS.MONSTER_PARTY_SCENE, {
          previousSceneName: SCENE_KEYS.BATTLE_SCENE,
          mode: 'battle',
          activeIndex: this.battle.sides.player.active,
        });
        if (result && result.selectedIndex !== undefined && result.selectedIndex !== this.battle.sides.player.active) {
          return { kind: 'SWITCH', index: result.selectedIndex };
        }
        continue;
      }
      if (choice === 'RUN') {
        if (this.isTrainer) {
          await this.say("No! There's no running from a trainer battle!");
          continue;
        }
        return { kind: 'RUN' };
      }
    }
  }

  /**
   * Tappable areas inside a menu container: cells are [x, y, w, h] in the container's coordinates.
   * @param {Phaser.GameObjects.Container} container
   * @param {number[][]} cells
   * @param {(index: number) => void} onTap
   */
  #tapCells(container, cells, onTap) {
    cells.forEach(([x, y, w, h], i) => {
      const zone = this.add.zone(x, y, w, h).setOrigin(0).setInteractive();
      zone.on('pointerup', (/** @type {Phaser.Input.Pointer} */ p) => {
        if (p.getDistance() < 24 && container.visible) {
          onTap(i);
        }
      });
      container.add(zone);
    });
  }

  /** @returns {Promise<string>} */
  #mainMenu() {
    return new Promise((resolve) => {
      const { k, field, uiHeight } = this.L;
      // on a tall canvas the menu is taller too, with bigger cells to tap
      const { tall } = this.L;
      const w = tall ? 400 : 420;
      const left = GAME_WIDTH / k - w; // in the message box's units
      const c = this.add.container(GAME_WIDTH - w * k, field).setDepth(55).setScale(k);
      // B here just moves the cursor to RUN, so only A gets a prompt: in the message box, left of this menu, where
      // the question wraps too
      this.messageBox.setHints(HINTS.select, left - 24).setTextWidth(left - 58);
      c.once('destroy', () => {
        this.menuMode = null;
        this.messageBox.setHints([]).setTextWidth();
      });
      c.add(panel(this, 0, 0, w, uiHeight, { radius: 12 }));
      const [x1, x2] = tall ? [56, 226] : [60, 236];
      const [y1, y2] = tall ? [46, 118] : [30, 82];
      const pos = [
        [x1, y1],
        [x2, y1],
        [x1, y2],
        [x2, y2],
      ];
      MAIN_OPTIONS.forEach((label, i) => c.add(text(this, pos[i][0], pos[i][1], label, 'body')));
      const cur = cursor(this);
      c.add(cur);
      let idx = this.lastMainIndex ?? 0;
      this.menuMode = 'main';
      this.menuCursor = () => idx;
      const place = () => cur.setPosition(pos[idx][0] - 30, pos[idx][1] + 8);
      place();
      const cellH = tall ? 68 : 52;
      this.#tapCells(c, pos.map(([x, y]) => [x - 40, y - (cellH - 20) / 2, 170, cellH]), (i) => {
        idx = i;
        place();
        inputManager.tap('A');
      });
      this.inputHandler = (input) => {
        if (input === 'LEFT' || input === 'RIGHT') {
          idx ^= 1;
        } else if (input === 'UP' || input === 'DOWN') {
          idx ^= 2;
        } else if (input === 'OK') {
          this.inputHandler = null;
          this.lastMainIndex = idx;
          c.destroy();
          playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
          resolve(MAIN_OPTIONS[idx]);
          return;
        } else if (input === 'CANCEL') {
          idx = 3;
        }
        place();
      };
    });
  }

  /** @returns {Promise<number>} slot or -1 */
  #moveMenu() {
    const mon = this.battle.playerActive;
    return new Promise((resolve) => {
      const { k, field, uiHeight } = this.L;
      const c = this.add.container(0, field).setDepth(55).setScale(k);
      c.once('destroy', () => { this.menuMode = null; });
      // the moves on the left with PP and type beside them; on a tall canvas, too narrow for that, PP and type go in a
      // strip underneath
      const { tall } = this.L;
      const W = GAME_WIDTH / k;
      const info = tall ? [0, 128, W, uiHeight - 128] : [660, 0, 364, 144];
      c.add(panel(this, 0, 0, tall ? W : 660, tall ? 128 : 144, { radius: 12 }));
      c.add(panel(this, info[0], info[1], info[2], info[3], { radius: 12 }));
      const [x1, x2] = tall ? [56, 396] : [60, 350];
      const [y1, y2] = tall ? [24, 76] : [30, 82];
      const pos = [
        [x1, y1],
        [x2, y1],
        [x1, y2],
        [x2, y2],
      ];
      for (let i = 0; i < 4; i += 1) {
        const m = mon.moves[i];
        c.add(text(this, pos[i][0], pos[i][1], m ? getMove(m.id).name : '-', 'body').setAlpha(m && m.pp <= 0 ? 0.5 : 1));
      }
      const ppText = tall ? text(this, 34, info[1] + 20, '', 'body') : text(this, 690, 22, '', 'body');
      const typeLabel = tall ? text(this, 236, info[1] + 26, 'TYPE/', 'small') : text(this, 690, 70, 'TYPE/', 'small');
      const badgeAt = tall ? [312, info[1] + 22] : [790, 68];
      c.add([ppText, typeLabel]);
      /** @type {Phaser.GameObjects.Container | null} */
      let badge = null;
      const cur = cursor(this);
      c.add(cur);
      let idx = Math.min(this.lastMoveIndex ?? 0, mon.moves.length - 1);
      this.menuMode = 'moves';
      this.menuCursor = () => idx;
      const place = () => {
        cur.setPosition(pos[idx][0] - 30, pos[idx][1] + 8);
        const m = mon.moves[idx];
        const data = getMove(m.id);
        ppText.setText(`PP  ${m.pp}/${data.pp}`).setColor(m.pp === 0 ? '#c4404a' : m.pp <= data.pp / 4 ? '#d08020' : '#2d2a3a');
        badge?.destroy();
        badge = typeBadge(this, badgeAt[0], badgeAt[1], data.type);
        c.add(badge);
      };
      place();
      this.#tapCells(c, pos.map(([x, y]) => [x - 40, y - 16, x2 - x1, 52]), (i) => {
        if (i < mon.moves.length) {
          idx = i;
          place();
          inputManager.tap('A');
        }
      });
      // the info panel doubles as a back button on touch screens
      this.#tapCells(c, [info], () => inputManager.tap('B'));
      const hintAt = tall ? [W - 28, info[1] + info[3] / 2] : [996, 116];
      c.add(new ControlHints(this, hintAt[0], hintAt[1]).set([{ btn: 'A', label: 'Use' }, { btn: 'B', label: 'Back' }]).container);
      this.inputHandler = (input) => {
        const n = mon.moves.length;
        let next = idx;
        if (input === 'LEFT' || input === 'RIGHT') {
          next = idx ^ 1;
        } else if (input === 'UP' || input === 'DOWN') {
          next = idx ^ 2;
        } else if (input === 'OK') {
          if (mon.moves[idx].pp <= 0) {
            this.inputHandler = null;
            c.setVisible(false);
            this.say("There's no PP left for this move!").then(() => {
              c.setVisible(true);
              this.inputHandler = handler;
            });
            return;
          }
          this.inputHandler = null;
          this.lastMoveIndex = idx;
          c.destroy();
          playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
          resolve(idx);
          return;
        } else if (input === 'CANCEL') {
          this.inputHandler = null;
          c.destroy();
          resolve(-1);
          return;
        }
        if (next < n) {
          idx = next;
          place();
        }
      };
      const handler = this.inputHandler;
    });
  }

  /**
   * Launches a menu scene over this one and resolves with whatever it passes back on resume.
   * @param {string} key
   * @param {object} data
   * @returns {Promise<any>}
   */
  #openSub(key, data) {
    return new Promise((resolve) => {
      this.events.once(Phaser.Scenes.Events.RESUME, (sys, resumeData) => resolve(resumeData));
      this.scene.launch(key, data);
      this.scene.pause();
    });
  }

  // ------------------------------------------------------------------------------------------
  // event playback
  // ------------------------------------------------------------------------------------------

  /** @param {import('../battle/engine/battle-engine.js').BattleEvent[]} events */
  async #playEvents(events) {
    for (const e of events) {
      const sprite = e.side === 'player' ? this.playerSprite : this.enemySprite;
      const hud = e.side === 'player' ? this.playerHud : this.enemyHud;
      switch (e.type) {
        case 'MESSAGE':
        case 'MISS':
          await this.note(e.text);
          break;
        case 'MOVE_USED': {
          this.messageBox.setText(e.text);
          await wait(this, this.skipAnim ? 200 : 400);
          const move = e.moveId === 0 ? { type: 'NORMAL', category: 'PHYSICAL', effect: null } : getMove(e.moveId);
          const attacker = e.side === 'player' ? this.playerSprite : this.enemySprite;
          const target = e.side === 'player' ? this.enemySprite : this.playerSprite;
          await playMoveFx(this, { attacker, target, move: /** @type {any} */ (move), side: e.side, skip: this.skipAnim });
          break;
        }
        case 'DAMAGE':
          playSoundFx(this, e.effectiveness > 1 ? AUDIO_KEYS.SFX_HIT_SUPER : e.effectiveness < 1 ? AUDIO_KEYS.SFX_HIT_WEAK : AUDIO_KEYS.SFX_HIT);
          if (!this.skipAnim) {
            await shakeAndBlink(this, sprite);
          }
          await hud.animateHp(e.hp, e.maxHp);
          break;
        case 'HEAL':
          playSoundFx(this, AUDIO_KEYS.SFX_HEAL);
          await hud.animateHp(e.hp, e.maxHp);
          break;
        case 'STATUS':
          hud.setStatus(e.status);
          if (!this.skipAnim) {
            await statusFx(this, sprite, e.status);
          }
          break;
        case 'STATUS_CURED':
          hud.setStatus(null);
          break;
        case 'STAT_CHANGE':
          if (!this.skipAnim) {
            await statChangeFx(this, sprite, e.amount);
          }
          await this.note(e.text);
          break;
        case 'FAINT':
          playSoundFx(this, AUDIO_KEYS.SFX_FAINT);
          hud.setStatus('FNT');
          await tween(this, { targets: sprite, y: sprite.y + 120, alpha: 0, duration: this.skipAnim ? 1 : 600, ease: 'Quad.in' });
          sprite.setVisible(false);
          hud.hide();
          this.#refreshPartyIndicators();
          await this.say(e.text);
          break;
        case 'SWITCH_IN':
          if (e.side === 'player') {
            await tween(this, { targets: this.playerSprite, x: -200, duration: this.skipAnim ? 1 : 300 });
            this.playerHud.hide();
            await this.#sendOut('player', e.text);
          } else {
            await this.#sendOut('enemy', e.text);
          }
          break;
        case 'CATCH':
          await this.#playCatch(e.shakes, e.success);
          await this.say(e.text);
          break;
        case 'RUN':
          await this.say(e.text);
          break;
        default:
          break;
      }
    }
    this.#refreshPartyIndicators();
  }

  /**
   * @param {number} shakes
   * @param {boolean} success
   */
  async #playCatch(shakes, success) {
    playSoundFx(this, AUDIO_KEYS.SFX_THROW);
    const key = UI_KEYS.DABBA;
    const { player, enemy, sprite } = this.L;
    const f = sprite / 4;
    const from = { x: player.x, y: player.y - 160 * f };
    const dabba = this.textures.exists(key)
      ? this.add.image(from.x, from.y, key).setScale(sprite).setDepth(40)
      : this.add.circle(from.x, from.y, 22 * f, 0xd8d8e0).setStrokeStyle(4, 0x3a3058).setDepth(40);
    const target = { x: enemy.x, y: enemy.y - 90 * f };
    await new Promise((resolve) => {
      this.tweens.addCounter({
        from: 0,
        to: 1,
        duration: this.skipAnim ? 1 : 650,
        onUpdate: (tw) => {
          const t = tw.getValue();
          dabba.setPosition(from.x + (target.x - from.x) * t, from.y + (target.y - from.y) * t - Math.sin(Math.PI * t) * 220 * f);
          dabba.setAngle(t * 720);
        },
        onComplete: resolve,
      });
    });
    dabba.setAngle(0);
    this.enemySprite.setTintFill(0xffffff);
    await tween(this, { targets: this.enemySprite, scale: 0.1, alpha: 0, duration: this.skipAnim ? 1 : 350 });
    await tween(this, { targets: dabba, y: enemy.y - 20 * f, duration: this.skipAnim ? 1 : 300, ease: 'Bounce.out' });
    for (let i = 0; i < shakes; i += 1) {
      await wait(this, 350);
      playSoundFx(this, AUDIO_KEYS.SFX_SHAKE);
      await tween(this, { targets: dabba, angle: 18, duration: this.skipAnim ? 1 : 110, yoyo: true, repeat: 1 });
    }
    await wait(this, 300);
    if (success) {
      playSoundFx(this, AUDIO_KEYS.SFX_CATCH);
      dabba.setTint?.(0xb0b0b0);
      for (let i = 0; i < 6; i += 1) {
        const star = this.add.star(dabba.x, dabba.y - 10, 5, 6, 14, 0xfff0a0).setDepth(41);
        this.tweens.add({ targets: star, x: dabba.x + Math.cos(i) * 90, y: dabba.y - 60 - Math.sin(i) * 40, alpha: 0, duration: 600, onComplete: () => star.destroy() });
      }
      await wait(this, 500);
      this.caughtDabba = dabba;
      return;
    }
    dabba.destroy();
    this.enemySprite.clearTint().setAlpha(1);
    await tween(this, { targets: this.enemySprite, scale: this.#scaleFor(this.enemySprite.texture.key), duration: this.skipAnim ? 1 : 250, ease: 'Back.out' });
  }

  // ------------------------------------------------------------------------------------------
  // outcomes
  // ------------------------------------------------------------------------------------------

  /** @returns {Promise<boolean>} true when the battle is over */
  async #afterTurn() {
    const enemy = this.battle.enemyActive;
    if (enemy.hp <= 0) {
      await this.#awardExp(enemy);
      if (this.isTrainer && this.battle.nextEnemyIndex() >= 0) {
        const next = this.data_.trainer.team[this.battle.nextEnemyIndex()];
        await this.say(`${this.data_.trainer.name} is about to send in ${displayName(next)}.`);
        await this.#offerShift();
        await this.#playEvents(this.battle.sendNextEnemy());
      } else if (this.battle.hasUsableMonsters('player')) {
        await this.#onWin();
        return true;
      }
      // both sides went down together (recoil, Struggle): fall through to the loss below
    }
    if (this.battle.playerActive.hp <= 0) {
      if (!this.battle.hasUsableMonsters('player')) {
        await this.#onLose();
        return true;
      }
      const idx = await this.#forceSwitch();
      await this.#playEvents(this.battle.replacePlayerMonster(idx));
    }
    return false;
  }

  /** SHIFT battle style: before a trainer's next Urumon comes out, the player may switch for free. */
  async #offerShift() {
    const side = this.battle.sides.player;
    const canSwitch = side.party.some((m, i) => i !== side.active && m.hp > 0);
    if (dataManager.state.options.battleStyle === BATTLE_STYLE_OPTIONS.SET || this.battle.playerActive.hp <= 0 || !canSwitch) {
      return;
    }
    const answer = await this.choose(['YES', 'NO'], { title: `Will ${dataManager.state.player.name} change Urumon?` });
    if (answer !== 0) {
      return;
    }
    const result = await this.#openSub(SCENE_KEYS.MONSTER_PARTY_SCENE, {
      previousSceneName: SCENE_KEYS.BATTLE_SCENE,
      mode: 'battle',
      activeIndex: side.active,
    });
    if (result && result.selectedIndex !== undefined && result.selectedIndex !== side.active) {
      await this.#playEvents(this.battle.replacePlayerMonster(result.selectedIndex));
    }
  }

  /** @returns {Promise<number>} */
  async #forceSwitch() {
    for (;;) {
      const result = await this.#openSub(SCENE_KEYS.MONSTER_PARTY_SCENE, {
        previousSceneName: SCENE_KEYS.BATTLE_SCENE,
        mode: 'battle-forced',
        activeIndex: this.battle.sides.player.active,
      });
      if (result && result.selectedIndex !== undefined && dataManager.party[result.selectedIndex]?.hp > 0) {
        return result.selectedIndex;
      }
    }
  }

  /** @param {import('../battle/engine/monster.js').Monster} enemy */
  async #awardExp(enemy) {
    if (this.data_.quick) {
      return;
    }
    const base = expYield(enemy, this.isTrainer);
    const shares = this.battle.expShares(base);
    const ctx = { say: (m) => this.say(m), choose: (items, opts) => this.choose(items, opts) };
    for (const { index, amount } of shares) {
      const mon = dataManager.party[index];
      const isActive = index === this.battle.sides.player.active;
      await this.say(`${displayName(mon)} gained ${amount} EXP. Points!`);
      const result = gainExp(mon, amount);
      if (isActive) {
        if (result.toLevel > result.fromLevel) {
          await this.playerHud.expMeter.animateTo(1, 500);
          this.playerHud.expMeter.set(0);
        }
        await this.playerHud.expMeter.animateTo(this.playerHud.expRatio(mon), 500);
      }
      if (result.toLevel > result.fromLevel) {
        this.levelledUp.add(mon.uid);
        playSoundFx(this, AUDIO_KEYS.SFX_LEVEL_UP);
        if (isActive) {
          this.playerHud.bind(mon);
        }
        await this.say(`${displayName(mon)} grew to Lv. ${mon.level}!`);
        const a = result.before;
        const b = result.after;
        await this.say(`HP +${b.hp - a.hp}  ATK +${b.atk - a.atk}  DEF +${b.def - a.def}  SPC +${b.spc - a.spc}  SPD +${b.spd - a.spd}`);
        for (const moveId of result.learned) {
          await this.say(`${displayName(mon)} learned ${getMove(moveId).name}!`);
        }
        for (const moveId of result.pendingMoves) {
          await promptLearnMove(ctx, mon, moveId);
        }
      }
    }
  }

  async #onWin() {
    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_VICTORY);
    if (this.isTrainer) {
      const t = this.data_.trainer;
      this.trainerSprite.setVisible(true).setX(OFF_RIGHT).setAlpha(1);
      await tween(this, { targets: this.trainerSprite, x: this.L.trainer.x, duration: this.skipAnim ? 1 : 500, ease: 'Cubic.out' });
      await this.say(`You defeated ${t.title ? `${t.title} ${t.name}` : t.name}!`);
      for (const line of t.defeatText || []) {
        await this.say(line);
      }
      if (t.prize > 0) {
        dataManager.addMoney(t.prize);
        await this.say(`${dataManager.state.player.name} got ₹${t.prize} for winning!`);
      }
    }
    await this.#evolutions();
    this.#finish({ outcome: 'win', trainerId: this.data_.trainer?.id });
  }

  async #onLose() {
    const name = dataManager.state.player.name;
    if (this.data_.canLose) {
      await this.say(`${name}'s team has no Urumon left that can fight...`);
      this.#finish({ outcome: 'lose', trainerId: this.data_.trainer?.id, canLose: true });
      return;
    }
    await this.say(`${name} is out of usable Urumon!`);
    const lost = Math.floor(dataManager.money / 2);
    if (lost > 0) {
      dataManager.addMoney(-lost);
      await this.say(`${name} panicked and dropped ₹${lost}...`);
    }
    await this.say(`... ... ${name} blacked out!`);
    this.#finish({ outcome: 'lose', trainerId: this.data_.trainer?.id });
  }

  async #onCaught() {
    const caughtMon = this.battle.enemyActive;
    const sp = getSpecies(caughtMon.speciesId);
    const firstTime = !dataManager.state.pustaka.caught.includes(sp.id);
    caughtMon.uid = generateUid();
    caughtMon.status = caughtMon.status || null;
    const where = dataManager.addMonster(caughtMon);
    if (firstTime) {
      await this.say(`${sp.name}'s data was added to the Uru-Pustaka.`);
    }
    if (where === 'box') {
      await this.say(`Your party is full, so ${sp.name} was sent to the Namma Cloud.`);
    }
    await this.#evolutions();
  }

  /** Evolve any party member that levelled up this battle and reached its evolution level. */
  async #evolutions() {
    for (const mon of dataManager.party) {
      if (!this.levelledUp.has(mon.uid) || mon.hp <= 0) {
        continue;
      }
      const into = pendingEvolution(mon);
      if (into === null) {
        continue;
      }
      await this.#evolveSequence(mon, into);
    }
  }

  /**
   * @param {import('../battle/engine/monster.js').Monster} mon
   * @param {number} into
   */
  async #evolveSequence(mon, into) {
    const oldName = displayName(mon);
    const { field, evolve: at } = this.L;
    const cover = this.add.rectangle(0, 0, GAME_WIDTH, field, 0x1c1430).setOrigin(0).setDepth(70);
    const from = this.#monArt(mon.speciesId);
    const to = this.#monArt(into);
    const sprite = this.add.image(at.x, at.y, from.key).setOrigin(0.5, 1).setScale(from.scale).setDepth(71);
    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_EVOLUTION);
    await this.say(`What? ${oldName} is evolving!`);
    let cancelled = false;
    this.inputHandler = (input) => {
      if (input === 'CANCEL') {
        cancelled = true;
      }
    };
    for (let i = 0; i < 10 && !cancelled; i += 1) {
      const dur = Math.max(70, 260 - i * 22);
      const stage = i % 2 ? to : from;
      sprite.setTexture(stage.key).setScale(stage.scale).setTintFill(0xffffff);
      await tween(this, { targets: sprite, scaleX: stage.scale * 0.85, duration: dur, yoyo: true });
    }
    this.inputHandler = null;
    if (cancelled) {
      sprite.setTexture(from.key).clearTint().setScale(from.scale);
      await this.say(`Huh? ${oldName} stopped evolving!`);
    } else {
      const flash = this.add.rectangle(0, 0, GAME_WIDTH, field, 0xffffff).setOrigin(0).setDepth(72);
      await tween(this, { targets: flash, alpha: 0, duration: 600 });
      flash.destroy();
      sprite.setTexture(to.key).clearTint().setScale(to.scale);
      const learnedNow = evolve(mon, into);
      dataManager.markCaught(into);
      playSoundFx(this, AUDIO_KEYS.SFX_LEVEL_UP);
      await this.say(`Congratulations! Your ${oldName} evolved into ${getSpecies(into).name}!`);
      const ctx = { say: (m) => this.say(m), choose: (items, opts) => this.choose(items, opts) };
      for (const moveId of learnedNow.learned) {
        await this.say(`${displayName(mon)} learned ${getMove(moveId).name}!`);
      }
      for (const moveId of learnedNow.pendingMoves) {
        await promptLearnMove(ctx, mon, moveId);
      }
    }
    sprite.destroy();
    cover.destroy();
  }

  /**
   * Matches the overworld's graphics setting: a soft vignette, and a cooler, dimmer grade for outdoor battles at night.
   * @param {string} environment
   */
  #atmosphere(environment) {
    const cam = /** @type {any} */ (this.cameras.main);
    if (graphicsSetting() === 'CLASSIC' || !cam.postFX) {
      return;
    }
    cam.postFX.addVignette(0.5, 0.5, 0.95, 0.22);
    const indoor = ['indoor', 'arena', 'cave'].includes(environment);
    const phase = timeOfDay();
    if (!indoor && phase !== 'day') {
      // tint only the backdrop (depth 0); the creatures and the UI stay true to colour
      const night = phase === 'night';
      this.add.rectangle(0, 0, GAME_WIDTH, this.L.field, night ? 0x5868b8 : 0xf0a070, night ? 0.55 : 0.28).setOrigin(0).setDepth(1)
        .setBlendMode(Phaser.BlendModes.MULTIPLY);
    }
  }

  /** The sharpest picture available for a species, and the scale that makes it battle-sized. */
  #monArt(speciesId) {
    return bestArt(this, getSpecies(speciesId).assetKey, monHdKey(speciesId), this.L.sprite);
  }

  /** @param {string} key */
  #scaleFor(key) {
    return key.startsWith('MONHD_') ? this.L.sprite / HD_FACTOR : this.L.sprite;
  }

  /** Swaps the pixel sprites on screen for HD ones once they've loaded, keeping their size. */
  #upgradeArt() {
    if (!this.scene.isActive()) {
      return;
    }
    let retry = false;
    [[this.enemySprite, 'enemy'], [this.playerSprite, 'player']].forEach(([sprite, side]) => {
      const id = this.battle.active(side).speciesId;
      if (this.tweens.isTweening(sprite)) {
        retry = true; // a running scale tween would finish at the pixel sprite's scale; swap afterwards
        return;
      }
      if (sprite.texture.key === getSpecies(id).assetKey && this.textures.exists(monHdKey(id))) {
        sprite.setTexture(monHdKey(id)).setScale(sprite.scaleX / HD_FACTOR, sprite.scaleY / HD_FACTOR);
      }
    });
    const portrait = this.data_.trainer?.portrait;
    if (this.trainerSprite && portrait && this.trainerSprite.texture.key === portrait) {
      const hd = trainerHdKey(portrait.slice('TRAINER_'.length));
      if (this.textures.exists(hd)) {
        this.trainerSprite.setTexture(hd).setScale(this.trainerSprite.scaleX / HD_FACTOR);
      }
    }
    if (retry) {
      this.time.delayedCall(400, () => this.#upgradeArt());
    }
  }

  /** @param {BattleResult} result */
  #finish(result) {
    if (this.finished) {
      return;
    }
    this.finished = true;
    // statuses persist but battle-only state does not; fainted monsters stay fainted
    dataManager.party.forEach((m) => {
      if (m.hp > getMaxHp(m)) {
        m.hp = getMaxHp(m);
      }
    });
    this.inputHandler = null;
    this.cameras.main.fadeOut(this.skipAnim ? 100 : 500, 0, 0, 0);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.game.events.emit('battle-finished', result);
      this.scene.stop();
    });
  }
}
