/**
 * Runs map scripts: arrays of small JSON commands authored in tools/maps/*.py.
 *
 *   {say: "text" | ["a", "b"], speaker?: "Name"}       dialog, waits for A after each line
 *   {ask: "question?", yes: [...], no: [...]}           yes/no branch
 *   {choice: "prompt", options: [{label, do: [...]}]}  multi-choice branch
 *   {if: <condition>, then: [...], else: [...]}         see WorldScene.checkCondition
 *   {setFlag: "X"} {clearFlag: "X"} {setVar: {k: v}}
 *   {giveItem: "Name" | id, qty?}  {takeItem: "Name", qty?}  {giveMoney: n} {takeMoney: n}
 *   {giveMonster: {species, level, nickname?}}
 *   {heal: true, setRespawn?: true}
 *   {battle: {trainer: "id"} | {wild: {species, level}, environment?, music?, canLose?}, onWin?: [...], onLose?: [...]}
 *   {npcFace: {id, dir}} {npcWalk: {id, steps: ["UP", ...], ghost?}} {npcToPlayer: "id"} {npcHide: "id"}
 *   {npcShow: {def}} {exclaim: "id" | "player"}
 *   {playerWalk: ["UP", ...]} {playerFace: "UP"}
 *   {warp: {area, warpId?, x?, y?, dir?}}
 *   {music: "MUSIC_X"} {sfx: "SFX_X"} {wait: ms} {fade: "out"|"in"} {cutscene: true|false}
 *   {badge: "NAME", text?} {shop: [item names], greeting?} {storage: true} {metro: true} {pustaka: true}
 *   {starterChoice: true} {save: true} {credits: true} {setRespawn: true} {end: true}
 *   {resetTrainers: ["npc id", ...]} {setLocation: {area, x, y, dir?}}
 *   {money: true} (show money box)  {hideMoney: true}
 */
import { DIRECTION } from '../common/direction.js';
import { TILE_SIZE } from '../config.js';
import { SCENE_KEYS } from '../scenes/scene-keys.js';
import { dataManager } from '../utils/data-manager.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { createMonster, fullyHeal, getSpecies } from '../battle/engine/monster.js';
import { getItem, getItemByName } from '../game/game-data.js';
import { buildTrainerTeam } from './trainers.js';
import { gameData } from '../game/game-data.js';

class EndScript extends Error {}

const OPPOSITE = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT' };

export class ScriptRunner {
  /** @param {import('../scenes/world-scene.js').WorldScene} world */
  constructor(world) {
    this.world = world;
  }

  get ui() {
    return this.world.ui;
  }

  /**
   * @param {any[]} script
   * @param {{npc?: import('./characters/npc.js').NPC}} ctx
   */
  async run(script, ctx = {}) {
    try {
      await this.#block(script, ctx);
    } catch (e) {
      if (!(e instanceof EndScript)) {
        throw e;
      }
    } finally {
      this.ui.hideMoney();
      this.ui.close();
    }
  }

  /** @param {any[]} cmds @param {any} ctx */
  async #block(cmds, ctx) {
    if (!cmds) {
      return;
    }
    const list = Array.isArray(cmds) ? cmds : [cmds];
    for (const cmd of list) {
      await this.#exec(cmd, ctx);
    }
  }

  /** @param {string | number} ref */
  #item(ref) {
    return typeof ref === 'number' ? getItem(ref) : getItemByName(ref);
  }

  /** @param {string} id */
  #npc(id, ctx) {
    if (id === 'self' || id === undefined) {
      return ctx.npc;
    }
    return this.world.getNpc(id);
  }

  /** @param {any} c @param {any} ctx */
  async #exec(c, ctx) {
    const w = this.world;
    if (typeof c === 'string') {
      await this.ui.say(c, { keepOpen: false });
      return;
    }
    if (c.say !== undefined) {
      await this.ui.say(c.say, { speaker: c.speaker });
      return;
    }
    if (c.ask !== undefined) {
      const yes = await this.ui.ask(c.ask, { speaker: c.speaker });
      await this.#block(yes ? c.yes : c.no, ctx);
      return;
    }
    if (c.choice !== undefined) {
      const idx = await this.ui.choose(c.options.map((o) => o.label), { prompt: c.choice, cancelValue: c.options.length - 1 });
      this.ui.close();
      await this.#block(c.options[idx]?.do, ctx);
      return;
    }
    if (c.if !== undefined) {
      await this.#block(w.checkCondition(c.if) ? c.then : c.else, ctx);
      return;
    }
    if (c.setFlag) {
      dataManager.addFlag(c.setFlag);
      return;
    }
    if (c.clearFlag) {
      dataManager.removeFlag(c.clearFlag);
      return;
    }
    if (c.setVar) {
      Object.assign(dataManager.state.vars, c.setVar);
      return;
    }
    if (c.giveItem !== undefined) {
      const item = this.#item(c.giveItem);
      const qty = c.qty ?? 1;
      dataManager.addItem(item.id, qty);
      playSoundFx(w, AUDIO_KEYS.SFX_ITEM);
      if (!c.silent) {
        await this.ui.say(`${dataManager.state.player.name} received ${qty > 1 ? `${qty}x ` : ''}${item.name}!`);
      }
      return;
    }
    if (c.takeItem !== undefined) {
      const item = this.#item(c.takeItem);
      dataManager.removeItem(item.id, c.qty ?? 1);
      return;
    }
    if (c.giveMoney !== undefined) {
      dataManager.addMoney(c.giveMoney);
      playSoundFx(w, AUDIO_KEYS.SFX_MONEY);
      await this.ui.say(`${dataManager.state.player.name} received ₹${c.giveMoney}!`);
      return;
    }
    if (c.takeMoney !== undefined) {
      dataManager.addMoney(-c.takeMoney);
      return;
    }
    if (c.giveMonster) {
      const m = createMonster(c.giveMonster.species, c.giveMonster.level, { nickname: c.giveMonster.nickname });
      const where = dataManager.addMonster(m);
      playSoundFx(w, AUDIO_KEYS.SFX_LEVEL_UP);
      await this.ui.say(`${dataManager.state.player.name} received ${getSpecies(m.speciesId).name}!`);
      if (where === 'box') {
        await this.ui.say(`Your party is full, so it was sent to the Namma Cloud.`);
      }
      return;
    }
    if (c.heal) {
      dataManager.party.forEach((m) => fullyHeal(m));
      playSoundFx(w, AUDIO_KEYS.SFX_HEAL);
      await this.#fade(250, 450);
      if (c.setRespawn) {
        w.setRespawnHere();
      }
      return;
    }
    if (c.setRespawn) {
      w.setRespawnHere();
      return;
    }
    if (c.battle) {
      await this.#battle(c, ctx);
      return;
    }
    if (c.npcFace) {
      this.#npc(c.npcFace.id, ctx)?.face(c.npcFace.dir === 'player' ? OPPOSITE[w.player.direction] : c.npcFace.dir);
      return;
    }
    if (c.npcWalk) {
      const npc = this.#npc(c.npcWalk.id, ctx);
      if (npc) {
        await npc.walk(c.npcWalk.steps, Boolean(c.npcWalk.ghost));
      }
      return;
    }
    if (c.npcToPlayer) {
      await this.#npcToPlayer(this.#npc(c.npcToPlayer, ctx));
      return;
    }
    if (c.npcHide) {
      w.removeNpc(c.npcHide === 'self' ? ctx.npc.id : c.npcHide);
      return;
    }
    if (c.npcShow) {
      if (!w.getNpc(c.npcShow.id)) {
        w.spawnNpc(c.npcShow);
      }
      return;
    }
    if (c.exclaim) {
      playSoundFx(w, AUDIO_KEYS.SFX_EXCLAIM);
      await w.exclaim(c.exclaim === 'player' ? w.player : this.#npc(c.exclaim, ctx));
      return;
    }
    if (c.playerWalk) {
      for (const dir of c.playerWalk) {
        await this.#playerStep(dir);
      }
      return;
    }
    if (c.playerFace) {
      w.player.face(c.playerFace === 'npc' && ctx.npc ? this.#dirTowards(w.player.tilePosition, ctx.npc.tilePosition) : c.playerFace);
      return;
    }
    if (c.warp) {
      const d = c.warp;
      await w.warpTo({
        area: d.area,
        warpId: d.warpId,
        position: d.x !== undefined ? { x: d.x * TILE_SIZE, y: d.y * TILE_SIZE } : undefined,
        direction: d.dir,
      });
      throw new EndScript();
    }
    if (c.music) {
      playBackgroundMusic(w, AUDIO_KEYS[c.music] || c.music);
      return;
    }
    if (c.sfx) {
      playSoundFx(w, AUDIO_KEYS[c.sfx] || c.sfx);
      return;
    }
    if (c.wait) {
      await new Promise((r) => w.time.delayedCall(c.wait, r));
      return;
    }
    if (c.fade) {
      await this.#fade(c.fade === 'out' ? 300 : 0, c.fade === 'in' ? 300 : 0, c.fade);
      return;
    }
    if (c.cutscene !== undefined) {
      const cs = /** @type {any} */ (w.scene.get(SCENE_KEYS.CUTSCENE_SCENE));
      if (cs?.startCutScene) {
        await (c.cutscene ? cs.startCutScene() : cs.endCutScene());
      }
      return;
    }
    if (c.badge) {
      dataManager.addBadge(c.badge);
      playSoundFx(w, AUDIO_KEYS.SFX_BADGE);
      await this.ui.say(c.text || `${dataManager.state.player.name} received the ${c.badge} Badge!`);
      return;
    }
    if (c.shop) {
      await w.openSubScene(SCENE_KEYS.SHOP_SCENE, { items: c.shop, greeting: c.greeting });
      return;
    }
    if (c.storage) {
      await w.openSubScene(SCENE_KEYS.STORAGE_SCENE, {});
      return;
    }
    if (c.pustaka) {
      await w.openSubScene(SCENE_KEYS.PUSTAKA_SCENE, {});
      return;
    }
    if (c.metro) {
      const result = await w.openSubScene(SCENE_KEYS.METRO_SCENE, { current: w.uru.metroStation });
      if (result && result.station && result.station.area !== w.area) {
        await w.warpTo({ area: result.station.area, warpId: result.station.warpId });
        throw new EndScript();
      }
      return;
    }
    if (c.starterChoice) {
      await this.#starterChoice(c, ctx);
      return;
    }
    if (c.save) {
      dataManager.saveData();
      return;
    }
    if (c.money) {
      this.ui.showMoney();
      return;
    }
    if (c.hideMoney) {
      this.ui.hideMoney();
      return;
    }
    if (c.credits) {
      w.scene.stop(SCENE_KEYS.DIALOG_SCENE);
      w.scene.start(SCENE_KEYS.CREDITS_SCENE);
      throw new EndScript();
    }
    if (c.resetTrainers) {
      const ids = new Set(c.resetTrainers.map(String));
      dataManager.state.defeatedNpcs = dataManager.state.defeatedNpcs.filter((id) => !ids.has(id));
      return;
    }
    if (c.setLocation) {
      const l = c.setLocation;
      dataManager.state.player.location = { area: l.area };
      dataManager.state.player.position = { x: l.x * TILE_SIZE, y: l.y * TILE_SIZE };
      dataManager.state.player.direction = l.dir || 'DOWN';
      return;
    }
    if (c.end) {
      throw new EndScript();
    }
    console.warn('[ScriptRunner] unknown command', c);
  }

  /**
   * @param {number} outMs
   * @param {number} inMs
   * @param {'out'|'in'|'both'} [mode='both']
   */
  #fade(outMs, inMs, mode = 'both') {
    const cam = this.world.cameras.main;
    return new Promise((resolve) => {
      const doIn = () => {
        if (mode === 'out') {
          resolve();
          return;
        }
        cam.fadeIn(inMs || 1, 0, 0, 0);
        this.world.time.delayedCall(inMs || 1, resolve);
      };
      if (mode === 'in') {
        doIn();
        return;
      }
      cam.fadeOut(outMs || 1, 0, 0, 0);
      this.world.time.delayedCall((outMs || 1) + 120, doIn);
    });
  }

  /**
   * @param {{x: number, y: number}} from
   * @param {{x: number, y: number}} to
   */
  #dirTowards(from, to) {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    if (Math.abs(dx) > Math.abs(dy)) {
      return dx > 0 ? DIRECTION.RIGHT : DIRECTION.LEFT;
    }
    return dy > 0 ? DIRECTION.DOWN : DIRECTION.UP;
  }

  /** @param {string} dir */
  #playerStep(dir) {
    const p = this.world.player;
    return new Promise((resolve) => {
      const prev = p._spriteGridMovementFinishedCallback;
      p._spriteGridMovementFinishedCallback = () => {
        p._spriteGridMovementFinishedCallback = prev;
        resolve();
      };
      p.moveCharacter(/** @type {any} */ (dir));
      if (!p.isMoving) {
        p._spriteGridMovementFinishedCallback = prev;
        resolve();
      }
    });
  }

  /** @param {import('./characters/npc.js').NPC | undefined} npc */
  async #npcToPlayer(npc) {
    if (!npc) {
      return;
    }
    const p = this.world.player.tilePosition;
    for (let guard = 0; guard < 30; guard += 1) {
      const n = npc.tilePosition;
      const dx = (p.x - n.x) / TILE_SIZE;
      const dy = (p.y - n.y) / TILE_SIZE;
      if (Math.abs(dx) + Math.abs(dy) <= 1) {
        break;
      }
      const dir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'RIGHT' : 'LEFT') : dy > 0 ? 'DOWN' : 'UP';
      const before = { ...n };
      await npc.walk([/** @type {any} */ (dir)]);
      const after = npc.tilePosition;
      if (after.x === before.x && after.y === before.y) {
        // blocked; try the other axis once
        const alt = Math.abs(dx) > Math.abs(dy) ? (dy > 0 ? 'DOWN' : 'UP') : dx > 0 ? 'RIGHT' : 'LEFT';
        await npc.walk([/** @type {any} */ (alt)]);
        const again = npc.tilePosition;
        if (again.x === before.x && again.y === before.y) {
          break;
        }
      }
    }
    const n = npc.tilePosition;
    npc.face(/** @type {any} */ (this.#dirTowards(n, p)));
    this.world.player.face(/** @type {any} */ (this.#dirTowards(p, n)));
  }

  /** @param {any} c @param {any} ctx */
  async #battle(c, ctx) {
    const b = c.battle;
    const w = this.world;
    let data;
    if (b.trainer) {
      const t = gameData.trainers[b.trainer];
      data = {
        trainer: {
          id: b.id || b.trainer,
          name: t.name,
          title: t.title,
          portrait: `TRAINER_${t.portrait}`,
          sprite: t.sprite,
          team: buildTrainerTeam(t),
          prize: t.prize ?? 0,
          defeatText: t.defeat || [],
          aiLevel: t.aiLevel ?? 1,
          isLeader: Boolean(t.isLeader),
        },
        environment: b.environment || t.environment || w.uru.environment,
        canLose: Boolean(b.canLose ?? t.canLose),
        music: b.music ? AUDIO_KEYS[b.music] || b.music : t.music ? AUDIO_KEYS[t.music] || t.music : undefined,
      };
    } else {
      data = {
        wild: createMonster(b.wild.species, b.wild.level),
        environment: b.environment || w.uru.environment,
        music: b.music ? AUDIO_KEYS[b.music] || b.music : undefined,
        canLose: Boolean(b.canLose),
      };
    }
    const result = await w.startBattle(data);
    if (result.outcome === 'lose' && !result.canLose) {
      throw new EndScript();
    }
    if (b.trainer && (result.outcome === 'win' || result.canLose)) {
      dataManager.addDefeatedNpc(b.id || b.trainer);
    }
    if (result.outcome === 'win' || result.outcome === 'caught') {
      await this.#block(c.onWin, ctx);
    } else {
      await this.#block(c.onLose, ctx);
    }
  }

  /**
   * Shows the three starters and lets the player pick one. Sets vars starter / rivalStarter.
   * @param {any} c
   */
  async #starterChoice(c) {
    const options = c.options || [1, 4, 7];
    const counters = { 1: 4, 4: 7, 7: 1 }; // the rival picks the one strong against yours
    for (;;) {
      const labels = options.map((id) => `${getSpecies(id).name} (${getSpecies(id).types[0]})`);
      const idx = await this.ui.choose(labels, { prompt: 'Which Urumon will you choose as your partner?', cancelValue: -1, width: 380 });
      if (idx < 0) {
        continue;
      }
      const sp = getSpecies(options[idx]);
      const info = {
        1: `${sp.name}, the jacaranda fawn. A GRASS type that grows into a mystic stag.`,
        4: `${sp.name}, the filter-coffee pup. A FIRE type with a steel tumbler on its head.`,
        7: `${sp.name}, the tender-coconut turtle. A WATER type that becomes a living island.`,
      }[sp.id];
      await this.ui.say(info || sp.dex);
      const yes = await this.ui.ask(`So, you want ${sp.name}?`);
      if (!yes) {
        continue;
      }
      const mon = createMonster(sp.id, 5);
      dataManager.addMonster(mon);
      const rival = counters[sp.id] ?? options[(idx + 1) % options.length];
      dataManager.state.vars.starter = sp.id;
      dataManager.state.vars.starterName = sp.name;
      dataManager.state.vars.rivalStarter = rival;
      dataManager.state.vars.rivalStarterName = getSpecies(rival).name;
      playSoundFx(this.world, AUDIO_KEYS.SFX_LEVEL_UP);
      await this.ui.say(`${dataManager.state.player.name} received ${sp.name}!`);
      return;
    }
  }
}
