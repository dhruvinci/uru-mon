import Phaser from './lib/phaser.js';
import { SCENE_KEYS } from './scenes/scene-keys.js';
import { PreloadScene } from './scenes/preload-scene.js';
import { BattleScene } from './scenes/battle-scene.js';
import { WorldScene } from './scenes/world-scene.js';
import { TitleScene } from './scenes/title-scene.js';
import { OptionsScene } from './scenes/options-scene.js';
import { MonsterPartyScene } from './scenes/monster-party-scene.js';
import { MonsterDetailsScene } from './scenes/monster-details-scene.js';
import { InventoryScene } from './scenes/inventory-scene.js';
import { CutsceneScene } from './scenes/cutscene-scene.js';
import { DialogScene } from './scenes/dialog-scene.js';
import { IntroScene } from './scenes/intro-scene.js';
import { ShopScene } from './scenes/shop-scene.js';
import { StorageScene } from './scenes/storage-scene.js';
import { PustakaScene } from './scenes/pustaka-scene.js';
import { TrainerCardScene } from './scenes/trainer-card-scene.js';
import { MetroScene } from './scenes/metro-scene.js';
import { CreditsScene } from './scenes/credits-scene.js';
import { TestScene } from './scenes/test-scene.js';
import { setupTouchControls } from './input/touch-controls.js';
import { inputManager } from './input/input-manager.js';
import { dataManager } from './utils/data-manager.js';
import { gameData } from './game/game-data.js';
import { createMonster, fullyHeal } from './battle/engine/monster.js';

const game = new Phaser.Game({
  type: Phaser.AUTO,
  pixelArt: true,
  roundPixels: true,
  scale: {
    parent: 'game-container',
    width: 1024,
    height: 576,
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  backgroundColor: '#1c1430',
  // keyboard is handled by our own input manager
  input: { keyboard: false },
});

const scenes = [
  [SCENE_KEYS.PRELOAD_SCENE, PreloadScene],
  [SCENE_KEYS.TITLE_SCENE, TitleScene],
  [SCENE_KEYS.INTRO_SCENE, IntroScene],
  [SCENE_KEYS.WORLD_SCENE, WorldScene],
  [SCENE_KEYS.BATTLE_SCENE, BattleScene],
  [SCENE_KEYS.OPTIONS_SCENE, OptionsScene],
  [SCENE_KEYS.MONSTER_PARTY_SCENE, MonsterPartyScene],
  [SCENE_KEYS.MONSTER_DETAILS_SCENE, MonsterDetailsScene],
  [SCENE_KEYS.INVENTORY_SCENE, InventoryScene],
  [SCENE_KEYS.CUTSCENE_SCENE, CutsceneScene],
  [SCENE_KEYS.DIALOG_SCENE, DialogScene],
  [SCENE_KEYS.SHOP_SCENE, ShopScene],
  [SCENE_KEYS.STORAGE_SCENE, StorageScene],
  [SCENE_KEYS.PUSTAKA_SCENE, PustakaScene],
  [SCENE_KEYS.TRAINER_CARD_SCENE, TrainerCardScene],
  [SCENE_KEYS.METRO_SCENE, MetroScene],
  [SCENE_KEYS.CREDITS_SCENE, CreditsScene],
  [SCENE_KEYS.TEST_SCENE, TestScene],
];
scenes.forEach(([key, cls]) => game.scene.add(key, cls));
game.scene.start(SCENE_KEYS.PRELOAD_SCENE);

inputManager.onFullscreenToggle = () => {
  if (game.scale.isFullscreen) {
    game.scale.stopFullscreen();
  } else {
    game.scale.startFullscreen();
  }
};
setupTouchControls();

// handy for debugging and automated tests
window.__uruGame = game;
window.__uru = { game, dataManager, gameData, inputManager, createMonster, fullyHeal };
