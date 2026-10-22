import Phaser from '../lib/phaser.js';
import { BaseScene } from './base-scene.js';
import { SCENE_KEYS } from './scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { gameData } from '../game/game-data.js';
import { allSpecies, createMonster, getSpecies } from '../battle/engine/monster.js';
import { ListMenu, panel, readMenuInput, text, typeBadge, TEXT } from '../ui/ui-kit.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { bestArt, loadHd, monHdKey, trainerHdKey } from '../ui/hd-art.js';

const LEVEL = 60;
const TEAM = 3;
/** Legendaries, the mythical and the Syndicate's machine sit out: Quick Battle is meant to be fair. */
const BANNED = new Set([64, 65, 146, 147, 148, 149, 150]);
const ARENAS = ['arena', 'park', 'city', 'grass', 'lake', 'hill'];
const MUSIC = [AUDIO_KEYS.MUSIC_TRAINER, AUDIO_KEYS.MUSIC_LEADER, AUDIO_KEYS.MUSIC_RIVAL];

const pick = (list) => list[Math.floor(Math.random() * list.length)];

/**
 * Quick Battle from the title screen: three random fully-evolved Urumon at Lv 60 each, against a random trainer.
 * Runs on a throwaway game state (nothing is saved, no EXP or money) and restores the real one on the way out.
 */
export class QuickBattleScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.QUICK_BATTLE_SCENE });
  }

  init() {
    super.init();
    this.realState = dataManager.state;
    this.playerName = this.#savedName();
    this.stage = 'matchup';
    /** @type {ListMenu | null} */
    this.menu = null;
    this.#roll();
  }

  /** The name from the player's save, so battle text reads naturally. */
  #savedName() {
    try {
      const raw = localStorage.getItem(dataManager.storageKey);
      return (raw && JSON.parse(raw)?.player?.name) || 'You';
    } catch {
      return 'You';
    }
  }

  /** Picks both teams and the opponent. */
  #roll() {
    const pool = allSpecies().filter((s) => !s.evolution && !BANNED.has(s.id)).map((s) => s.id);
    const draw = () => {
      const ids = [];
      while (ids.length < TEAM) {
        const id = pick(pool);
        if (!ids.includes(id)) {
          ids.push(id);
        }
      }
      return ids;
    };
    this.mine = draw();
    this.theirs = draw();
    const trainers = Object.entries(gameData.trainers || {}).filter(([, t]) => t.portrait && t.name !== 'Grunt');
    const [id, t] = pick(trainers);
    this.opponent = { id, ...t };
    this.environment = pick(ARENAS);
    this.music = pick(MUSIC);
  }

  create() {
    super.create();
    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_ARENA);
    this.#drawMatchup();
  }

  #drawMatchup() {
    this.children.removeAll(true);
    this.menu = null;
    const { width } = this.scale;
    this.add.rectangle(0, 0, width, 576, 0x1d1736).setOrigin(0);
    this.add.rectangle(0, 0, width / 2, 576, 0x2b3f7a, 0.45).setOrigin(0);
    this.add.rectangle(width / 2, 0, width / 2, 576, 0x7a2b3f, 0.45).setOrigin(0);
    text(this, width / 2, 14, 'QUICK BATTLE', 'title').setOrigin(0.5, 0).setColor('#fff4d6');
    text(this, width / 2, 66, `Lv ${LEVEL}  ·  3 vs 3`, 'lightSmall').setOrigin(0.5, 0);
    text(this, width / 2, 238, 'VS', 'title').setOrigin(0.5).setColor('#ffd35a');

    // your three
    text(this, 40, 100, this.playerName.toUpperCase(), 'body').setColor('#cfe0ff');
    this.mine.forEach((id, i) => this.#monCard(40, 124 + i * 94, id, false));

    // the opponent and their three
    const t = this.opponent;
    const portraitKey = `TRAINER_${t.portrait}`;
    const portrait = bestArt(this, portraitKey, trainerHdKey(t.portrait), 2.2);
    const pImg = this.add.image(width - 110, 430, portrait.key).setOrigin(0.5, 1).setScale(portrait.scale);
    text(this, width - 40, 100, `${t.title ? `${t.title} ` : ''}${t.name}`.toUpperCase(), 'body').setOrigin(1, 0).setColor('#ffd0d8');
    this.theirs.forEach((id, i) => this.#monCard(width - 470, 124 + i * 94, id, true));

    // HD pictures arrive a moment later
    loadHd(this, [...this.mine, ...this.theirs].map(monHdKey).concat(trainerHdKey(t.portrait))).then(() => {
      if (this.stage === 'matchup' && this.scene.isActive()) {
        this.#refreshArt(pImg, portraitKey, trainerHdKey(t.portrait), 2.2);
      }
    });

    this.menu = new ListMenu(this, { x: width / 2 - 150, y: 414, width: 300, rowHeight: 38, items: ['BATTLE!', 'SHUFFLE', 'BACK'], depth: 10 });
    this.stage = 'matchup';
  }

  /** A row with the Urumon's picture, name and types. */
  #monCard(x, y, id, flip) {
    const sp = getSpecies(id);
    panel(this, x, y, 330, 92, { fill: 0xf4efe2 });
    const art = bestArt(this, sp.assetKey, monHdKey(id), 1.25);
    const img = this.add.image(x + 52, y + 88, art.key).setOrigin(0.5, 1).setScale(art.scale).setFlipX(!flip);
    img.setData('art', [sp.assetKey, monHdKey(id), 1.25]);
    text(this, x + 108, y + 14, sp.name, 'body');
    sp.types.forEach((type, i) => typeBadge(this, x + 108 + i * 108, y + 54, type, 0.95));
  }

  /** Swaps freshly loaded HD pictures in. */
  #refreshArt(portrait, low, hd, scale) {
    if (this.textures.exists(hd)) {
      this.textures.get(hd).setFilter(Phaser.Textures.FilterMode.LINEAR);
      portrait.setTexture(hd).setScale(scale / 4);
    }
    this.children.list.forEach((o) => {
      const art = o.getData?.('art');
      if (art && this.textures.exists(art[1])) {
        this.textures.get(art[1]).setFilter(Phaser.Textures.FilterMode.LINEAR);
        o.setTexture(art[1]).setScale(art[2] / 4);
      }
    });
  }

  /** Starts the battle on a throwaway state; the real save is untouched. */
  #fight() {
    this.stage = 'battle';
    dataManager.startNewGame();
    const s = dataManager.state;
    s.player.name = this.playerName;
    s.monsters.inParty = this.mine.map((id) => createMonster(id, LEVEL));
    const t = this.opponent;
    this.game.events.once('battle-finished', (result) => this.#afterBattle(result));
    this.scene.launch(SCENE_KEYS.BATTLE_SCENE, {
      trainer: {
        id: `quick_${t.id}`,
        name: t.name,
        title: t.title,
        portrait: `TRAINER_${t.portrait}`,
        sprite: t.sprite,
        team: this.theirs.map((id) => createMonster(id, LEVEL)),
        prize: 0,
        defeatText: t.defeat || [],
        aiLevel: 2,
        isLeader: true,
      },
      environment: this.environment,
      canLose: true,
      music: this.music,
      quick: true,
    });
    this.scene.pause();
  }

  /** @param {{outcome: string}} result */
  #afterBattle(result) {
    this.scene.resume();
    this.stage = 'result';
    this.children.removeAll(true);
    const { width } = this.scale;
    const won = result.outcome === 'win';
    playBackgroundMusic(this, won ? AUDIO_KEYS.MUSIC_VICTORY : AUDIO_KEYS.MUSIC_ARENA);
    this.add.rectangle(0, 0, width, 576, won ? 0x24402f : 0x40242f).setOrigin(0);
    text(this, width / 2, 120, won ? 'YOU WIN!' : 'YOU LOST', 'title').setOrigin(0.5).setColor(won ? '#ffe680' : '#ffb0b8')
      .setScale(1.6);
    const t = this.opponent;
    text(this, width / 2, 200, won ? `You beat ${t.name}.` : `${t.name} took this one.`, 'lightSmall').setOrigin(0.5);
    this.menu = new ListMenu(this, { x: width / 2 - 170, y: 280, width: 340, items: ['REMATCH', 'NEW BATTLE', 'TITLE SCREEN'], depth: 10 });
  }

  #leave() {
    dataManager.state = this.realState;
    this.scene.start(SCENE_KEYS.TITLE_SCENE);
  }

  /** @param {number} time */
  update(time) {
    super.update(time);
    if (!this._controls || !this.menu || this.stage === 'battle') {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    const r = this.menu.handleInput(input);
    if (!r) {
      return;
    }
    playSoundFx(this, AUDIO_KEYS.SFX_SELECT);
    if (r.type === 'cancel') {
      if (this.stage === 'matchup') {
        this.#leave();
      }
      return;
    }
    const choice = this.menu.items[r.index];
    if (choice === 'BATTLE!' || choice === 'REMATCH') {
      this.menu.destroy();
      this.menu = null;
      this.#fight();
    } else if (choice === 'SHUFFLE' || choice === 'NEW BATTLE') {
      this.#roll();
      this.#drawMatchup();
    } else {
      this.#leave();
    }
  }
}
