import { SOUND_OPTIONS } from '../common/options.js';
import { dataManager } from './data-manager.js';

/** Key of the music track that should be playing (kept even while sound is off, so turning it on resumes it). */
let currentMusicKey = null;

/**
 * Plays a looping music track, replacing whatever music is playing. Missing tracks are ignored.
 * @param {Phaser.Scene} scene
 * @param {string} audioKey
 * @param {{restart?: boolean}} [opts]
 */
export function playBackgroundMusic(scene, audioKey, opts = {}) {
  if (!audioKey) {
    return;
  }
  const sm = scene.sound;
  if (currentMusicKey === audioKey && !opts.restart) {
    const playing = sm.getAll(audioKey).some((s) => s.isPlaying);
    if (playing || dataManager.state.options.sound !== SOUND_OPTIONS.ON) {
      return;
    }
  }
  currentMusicKey = audioKey;
  sm.getAllPlaying().forEach((s) => {
    if (/** @type {any} */ (s).__isMusic) {
      s.stop();
    }
  });
  if (dataManager.state.options.sound !== SOUND_OPTIONS.ON || !scene.cache.audio.exists(audioKey)) {
    // not downloaded yet: the preload scene starts it when it arrives
    return;
  }
  const music = sm.add(audioKey, { loop: true, volume: 0.55 });
  /** @type {any} */ (music).__isMusic = true;
  music.once('stop', () => music.destroy());
  music.play();
}

/** @param {Phaser.Scene} scene */
export function stopMusic(scene) {
  currentMusicKey = null;
  scene.sound.getAllPlaying().forEach((s) => {
    if (/** @type {any} */ (s).__isMusic) {
      s.stop();
    }
  });
}

/** @returns {string | null} */
export function currentMusic() {
  return currentMusicKey;
}

/**
 * Plays a one-shot sound effect if it exists.
 * @param {Phaser.Scene} scene
 * @param {string} audioKey
 * @param {number} [volume=0.8]
 */
export function playSoundFx(scene, audioKey, volume = 0.8) {
  if (dataManager.state.options.sound !== SOUND_OPTIONS.ON || !audioKey || !scene.cache.audio.exists(audioKey)) {
    return;
  }
  scene.sound.play(audioKey, { volume });
}

/** @param {Phaser.Scene} scene */
export function setGlobalSoundSettings(scene) {
  scene.sound.setVolume(dataManager.state.options.volume * 0.25);
  scene.sound.setMute(dataManager.state.options.sound === SOUND_OPTIONS.OFF);
}
