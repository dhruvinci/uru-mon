import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { dataManager } from '../utils/data-manager.js';
import { createMonster } from '../battle/engine/monster.js';
import { gameData } from '../game/game-data.js';
import { buildTrainerTeam } from '../world/trainers.js';

/**
 * Developer sandbox, opened with ?scene=test. Query params:
 *   map=<id>[&x=&y=]           jump straight into a map with a test party
 *   battle=wild&species=&level= start a wild battle
 *   battle=trainer&trainer=<id> start a trainer battle
 *   party=4:12,10:8            species:level list for the test party (default a strong mixed team)
 *   flags=A,B                   flags to set
 *   badges=GRASS,FIGHT          badges to grant
 */
export class TestScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.TEST_SCENE });
  }

  create() {
    super.create();
    const p = new URLSearchParams(window.location.search);
    dataManager.startNewGame();
    dataManager.state.player.name = p.get('name') || 'Tester';
    dataManager.state.player.gender = /** @type {any} */ (p.get('gender') || 'boy');
    const party = (p.get('party') || '6:30,25:28,48:27,44:26,53:27,33:28')
      .split(',')
      .map((s) => s.split(':').map(Number));
    party.forEach(([sp, lvl]) => dataManager.addMonster(createMonster(sp, lvl)));
    dataManager.state.vars.starter = 4;
    dataManager.state.vars.rivalStarter = 7;
    dataManager.state.vars.starterName = 'Kaapup';
    dataManager.state.vars.rivalStarterName = 'Elanee';
    dataManager.addItem(2, 20);
    dataManager.addItem(3, 10);
    dataManager.addItem(7, 3);
    (p.get('flags') || '').split(',').filter(Boolean).forEach((f) => dataManager.addFlag(f));
    (p.get('badges') || '').split(',').filter(Boolean).forEach((b) => dataManager.addBadge(b));
    dataManager.state.gameStarted = true;

    const battle = p.get('battle');
    if (battle) {
      this.scene.launch(SCENE_KEYS.DIALOG_SCENE);
      this.game.events.once('battle-finished', (result) => {
        window.__lastBattleResult = result;
        this.add.text(40, 40, `battle finished: ${JSON.stringify(result)}`, { fontSize: '24px', color: '#fff' });
      });
      if (battle === 'trainer') {
        const id = p.get('trainer') || Object.keys(gameData.trainers)[0];
        const t = gameData.trainers[id];
        this.scene.launch(SCENE_KEYS.BATTLE_SCENE, {
          trainer: { id, name: t.name, title: t.title, portrait: `TRAINER_${t.portrait}`, team: buildTrainerTeam(t), prize: t.prize, defeatText: t.defeat || [], aiLevel: t.aiLevel ?? 1, isLeader: t.isLeader },
          environment: p.get('env') || 'grass',
        });
      } else {
        this.scene.launch(SCENE_KEYS.BATTLE_SCENE, {
          wild: createMonster(Number(p.get('species') || 10), Number(p.get('level') || 5)),
          environment: p.get('env') || 'grass',
        });
      }
      return;
    }
    const map = p.get('map') || 'basavanagudi';
    let x = p.get('x');
    let y = p.get('y');
    let warpId = p.get('warp') || undefined;
    const uru = this.cache.tilemap.get(`MAP_${map}`)?.data?.uru || {};
    if (x === null && !warpId) {
      if (uru.spawn) {
        x = uru.spawn.x;
        y = uru.spawn.y;
      } else {
        warpId = (uru.warps || []).find((w) => w.mode !== 'step')?.id;
      }
    }
    dataManager.state.player.location = { area: map };
    this.scene.start(SCENE_KEYS.WORLD_SCENE, {
      area: map,
      position: x !== null && y !== null ? { x: Number(x) * 64, y: Number(y) * 64 } : undefined,
      warpId: x === null ? warpId : undefined,
    });
  }
}
