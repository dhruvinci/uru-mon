import Phaser from '../lib/phaser.js';
import { Hd2dPipeline } from './hd2d-pipeline.js';
import { dataManager } from '../utils/data-manager.js';
import { TILE_SIZE } from '../config.js';

/**
 * Atmosphere for the overworld, by graphics setting:
 *   CLASSIC  - nothing (the original flat look)
 *   ENHANCED - time-of-day grade, weather and ambient particles, night lights, character shadows
 *   HD-2D    - all of that plus the tilted camera, depth of field and haze (see hd2d-pipeline.js)
 * Time of day follows the player's clock; `?time=dawn|day|dusk|night`, `?weather=rain|clear` and `?gfx=CLASSIC|ENHANCED|HD-2D`
 * override it for testing.
 */

const PHASES = {
  dawn: { grade: [1.0, 0.9, 0.86], haze: [1.0, 0.8, 0.75], saturation: 0.95, lights: 0.5 },
  day: { grade: [1.02, 1.0, 0.98], haze: [0.82, 0.9, 1.0], saturation: 1.06, lights: 0 },
  dusk: { grade: [1.06, 0.84, 0.72], haze: [1.0, 0.62, 0.45], saturation: 1.0, lights: 0.6 },
  night: { grade: [0.5, 0.57, 0.82], haze: [0.12, 0.14, 0.3], saturation: 0.75, lights: 1 },
};
const INDOOR = { grade: [1.03, 1.0, 0.95], haze: [1, 0.95, 0.85], saturation: 1.02, lights: 0 };

/** Ambient particles per map. */
const AMBIENT = {
  basavanagudi: { leaves: [0x6aa84f, 0xd9a441] },
  route1: { leaves: [0x6aa84f, 0x8bc34a] },
  lalbagh: { petals: [0xa07ad8, 0xc29ae8], fireflies: true },
  cubbon_park: { leaves: [0x5b9a45, 0xc9a13b], fireflies: true },
  palace_road: { petals: [0xe0533a, 0xf08a3c] },
  malleshwaram: { petals: [0xfdfaf0, 0xf3ead2] },
  bellandur: { bubbles: true },
  sankey_tank: { fireflies: true },
  hebbal: { fireflies: true },
  nandi_hills: { fog: true, fireflies: true },
  nandi_cave: { dust: true },
  bannerghatta: { leaves: [0x3f7f3a, 0x6aa84f], fireflies: true },
  ramanagara: { dust: true },
  kokkare_bellur: { petals: [0xffffff, 0xf2c9d8] },
};

/** @returns {'CLASSIC'|'ENHANCED'|'HD-2D'} */
export function graphicsSetting() {
  const forced = new URLSearchParams(window.location.search).get('gfx');
  if (forced && ['CLASSIC', 'ENHANCED', 'HD-2D'].includes(forced)) {
    return /** @type {any} */ (forced);
  }
  return dataManager.state.options.graphics || (window.matchMedia('(pointer: coarse)').matches ? 'ENHANCED' : 'HD-2D');
}

/** @returns {keyof PHASES} */
export function timeOfDay() {
  const forced = new URLSearchParams(window.location.search).get('time');
  if (forced && PHASES[forced]) {
    return /** @type {any} */ (forced);
  }
  const h = new Date().getHours();
  return h >= 5 && h < 7 ? 'dawn' : h >= 7 && h < 17 ? 'day' : h >= 17 && h < 19 ? 'dusk' : 'night';
}

/** Rain is likelier in the monsoon months (June to September). Decided once per map visit. */
function rollWeather(interior) {
  const forced = new URLSearchParams(window.location.search).get('weather');
  if (forced) {
    return forced;
  }
  if (interior) {
    return 'clear';
  }
  const month = new Date().getMonth();
  const chance = month >= 5 && month <= 8 ? 0.35 : 0.06;
  return Math.random() < chance ? 'rain' : 'clear';
}

/** Small textures drawn once and shared by every map. */
function ensureTextures(scene) {
  const make = (key, w, h, draw) => {
    if (scene.textures.exists(key)) {
      return;
    }
    const tex = scene.textures.createCanvas(key, w, h);
    draw(tex.getContext(), w, h);
    tex.refresh();
  };
  make('FX_SOFT', 64, 64, (ctx, w) => {
    const g = ctx.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    // fade colour as well as alpha, so additive glows don't light up the whole square
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.45, 'rgba(115,115,115,0.45)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, w);
  });
  make('FX_PETAL', 6, 5, (ctx) => {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(1, 0, 4, 1);
    ctx.fillRect(0, 1, 6, 3);
    ctx.fillRect(1, 4, 4, 1);
  });
  make('FX_RAIN', 2, 14, (ctx) => {
    ctx.fillStyle = 'rgba(200,220,255,0.75)';
    ctx.fillRect(0, 0, 2, 14);
  });
  make('FX_DOT', 4, 4, (ctx) => {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 4, 4);
  });
  make('FX_SHADOW', 40, 14, (ctx, w, h) => {
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.beginPath();
    ctx.ellipse(w / 2, h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
  });
}

export class WorldFx {
  /**
   * @param {Phaser.Scene & {uru: any, area: string, map: Phaser.Tilemaps.Tilemap}} scene
   */
  constructor(scene) {
    this.scene = scene;
    this.setting = graphicsSetting();
    this.objects = [];
    /** @type {{target: () => (Phaser.GameObjects.Sprite | undefined), shadow: Phaser.GameObjects.Image}[]} */
    this.shadows = [];
    if (this.setting === 'CLASSIC') {
      return;
    }
    ensureTextures(scene);
    const interior = Boolean(scene.uru.interior);
    this.phaseName = interior ? 'indoor' : timeOfDay();
    this.phase = interior ? INDOOR : PHASES[this.phaseName];
    this.weather = rollWeather(interior);
    this.#camera(interior);
    this.#ambient(interior);
    this.#lights(interior);
    this.#water();
  }

  /** @param {boolean} interior */
  #camera(interior) {
    const scene = this.scene;
    const renderer = /** @type {any} */ (scene.game.renderer);
    if (!renderer.pipelines) {
      return; // canvas renderer: no post effects
    }
    if (!renderer.pipelines.postPipelineClasses.has('UruHd2d')) {
      renderer.pipelines.addPostPipeline('UruHd2d', Hd2dPipeline);
    }
    const cam = scene.cameras.main;
    cam.setPostPipeline(Hd2dPipeline);
    const pipe = /** @type {Hd2dPipeline} */ (cam.getPostPipeline(Hd2dPipeline));
    if (!pipe) {
      return;
    }
    const p = pipe.params;
    const rain = this.weather === 'rain';
    const hd = this.setting === 'HD-2D';
    p.tilt = hd ? (interior ? 0.06 : 0.12) : 0;
    p.blur = hd ? (interior ? 0.7 : 1.3) : 0;
    p.hazeAmount = hd && !interior ? (rain ? 0.32 : 0.2) : 0;
    p.haze = this.phase.haze;
    p.grade = rain ? this.phase.grade.map((c, i) => c * [0.82, 0.86, 0.94][i]) : [...this.phase.grade];
    p.saturation = rain ? this.phase.saturation * 0.85 : this.phase.saturation;
    p.vignette = interior ? 0.32 : 0.24;
    this.pipe = pipe;
    if (p.tilt) {
      // frame the player a little below the middle of the screen, and keep them in the sharp band
      const want = 0.56;
      const srcY = pipe.sourceAt(0.5, want)[1];
      cam.setFollowOffset(0, (srcY - 0.5) * cam.height);
      p.focus = want;
    }
  }

  /** Emitters fixed to the screen so petals and rain fall the same way however the camera moves. */
  #ambient(interior) {
    const scene = this.scene;
    const { width, height } = scene.scale;
    const conf = interior ? {} : AMBIENT[scene.area] || {};
    const add = (emitter) => {
      emitter.setScrollFactor(0).setDepth(9000);
      this.objects.push(emitter);
      return emitter;
    };
    const night = this.phaseName === 'night' || this.phaseName === 'dusk';
    if (this.weather === 'rain') {
      add(scene.add.particles(0, -20, 'FX_RAIN', {
        x: { min: -100, max: width + 100 }, lifespan: 700, speedY: { min: 900, max: 1100 }, speedX: -160,
        rotate: 10, alpha: { start: 0.7, end: 0.3 }, quantity: 4, frequency: 16,
      }));
      this.storm = scene.time.addEvent({ delay: 9000 + Math.random() * 9000, loop: true, callback: () => {
        if (Math.random() < 0.5) {
          scene.cameras.main.flash(180, 220, 225, 255, true);
        }
      } });
    }
    if (conf.petals || conf.leaves) {
      const tints = conf.petals || conf.leaves;
      add(scene.add.particles(0, -10, 'FX_PETAL', {
        x: { min: 0, max: width + 200 }, lifespan: 9000, speedY: { min: 30, max: 60 }, speedX: { min: -50, max: -15 },
        rotate: { min: 0, max: 360 }, scale: { min: 1.6, max: 2.6 }, tint: tints, alpha: { start: 1, end: 0.7 },
        frequency: this.weather === 'rain' ? 900 : 380, quantity: 1,
      }));
    }
    if (conf.bubbles) {
      add(scene.add.particles(0, height + 10, 'FX_SOFT', {
        x: { min: 0, max: width }, lifespan: 6000, speedY: { min: -40, max: -15 }, speedX: { min: -8, max: 8 },
        scale: { min: 0.15, max: 0.45 }, alpha: { start: 0.55, end: 0 }, tint: 0xf4fff4, frequency: 260,
      }));
    }
    if (conf.fog) {
      add(scene.add.particles(0, 0, 'FX_SOFT', {
        x: { min: -200, max: width }, y: { min: 0, max: height }, lifespan: 14000, speedX: { min: 8, max: 22 },
        scale: { min: 4, max: 7 }, alpha: { start: 0, end: 0, ease: 'Sine.inOut' }, tint: 0xffffff, frequency: 900,
        emitCallback: (p) => scene.tweens.add({ targets: p, alpha: 0.22, duration: 5000, yoyo: true }),
      }));
    }
    if (conf.dust) {
      add(scene.add.particles(0, 0, 'FX_DOT', {
        x: { min: 0, max: width }, y: { min: 0, max: height }, lifespan: 5000, speedY: { min: -6, max: 6 },
        speedX: { min: -6, max: 6 }, scale: 0.5, alpha: { start: 0.45, end: 0 }, tint: 0xe8dcc0, frequency: 220,
      }));
    }
    if (conf.fireflies && night && this.weather !== 'rain') {
      add(scene.add.particles(0, 0, 'FX_SOFT', {
        x: { min: 0, max: width }, y: { min: height * 0.3, max: height }, lifespan: 4000, speed: { min: 4, max: 18 },
        scale: { start: 0.1, end: 0.16 }, alpha: { start: 0, end: 0 }, tint: 0xd8ff7a, blendMode: 'ADD', frequency: 300,
        emitCallback: (p) => scene.tweens.add({ targets: p, alpha: 0.9, duration: 900, yoyo: true, repeat: 1 }),
      }));
    }
  }

  /** At dusk and night, doorways and lamps glow and the player carries a soft light. */
  #lights(interior) {
    const strength = this.phase.lights;
    if (!strength || interior) {
      return;
    }
    const scene = this.scene;
    const glow = (x, y, scale, tint, alpha) => {
      const g = scene.add.image(x, y, 'FX_SOFT').setScale(scale).setTint(tint).setAlpha(alpha * strength)
        .setBlendMode(Phaser.BlendModes.ADD).setDepth(y + 1);
      this.objects.push(g);
      return g;
    };
    const edge = (w) => w.x <= 0 || w.y <= 0 || w.x >= scene.map.width - 1 || w.y >= scene.map.height - 1;
    (scene.uru.warps || []).filter((w) => !edge(w)).forEach((w) => {
      glow(w.x * TILE_SIZE + 32, w.y * TILE_SIZE + 40, 2.4, 0xffc070, 0.55);
    });
    (scene.uru.lights || []).forEach((l) => {
      glow(l.x * TILE_SIZE + 32, l.y * TILE_SIZE + 24, l.size || 3, l.tint ?? 0xffd890, 0.6);
    });
    this.playerLight = glow(0, 0, 4, 0xfff0c8, 0.3);
  }

  /** Twinkles on lakes. */
  #water() {
    const scene = this.scene;
    const cells = scene.uru.water || [];
    if (!cells.length) {
      return;
    }
    const W = scene.map.width;
    const zone = {
      getRandomPoint: (point) => {
        const idx = cells[Math.floor(Math.random() * cells.length)];
        point.x = (idx % W) * TILE_SIZE + Math.random() * TILE_SIZE;
        point.y = Math.floor(idx / W) * TILE_SIZE + Math.random() * TILE_SIZE;
        return point;
      },
    };
    const sparkle = scene.add.particles(0, 0, 'FX_DOT', {
      lifespan: 900, scale: { start: 0.9, end: 0 }, alpha: { start: 0.9, end: 0 }, tint: 0xffffff,
      blendMode: 'ADD', frequency: Math.max(30, 1600 / Math.sqrt(cells.length)), emitZone: { type: 'random', source: zone },
    }).setDepth(1);
    this.objects.push(sparkle);
  }

  /**
   * Gives a character a soft shadow at its feet.
   * @param {() => (Phaser.GameObjects.Sprite | undefined)} target
   */
  addShadow(target) {
    if (this.setting === 'CLASSIC') {
      return;
    }
    const shadow = this.scene.add.image(0, 0, 'FX_SHADOW').setAlpha(this.phaseName === 'night' ? 0.15 : 0.24);
    this.shadows.push({ target, shadow });
  }

  update() {
    for (const s of this.shadows) {
      const sprite = s.target();
      if (!sprite || !sprite.active) {
        s.shadow.setVisible(false);
        continue;
      }
      // characters are drawn from their tile's top-left corner; the feet sit near the tile's bottom edge
      const feetY = sprite.y + sprite.displayHeight * (1 - sprite.originY) - 4;
      s.shadow.setVisible(sprite.visible).setPosition(sprite.x + sprite.displayWidth * (0.5 - sprite.originX), feetY)
        .setDepth(sprite.depth - 0.5);
    }
    if (this.playerLight && this.scene.player) {
      // a pool of lantern light on the ground around the player's feet
      const p = this.scene.player.sprite;
      this.playerLight.setPosition(p.x + p.displayWidth / 2, p.y + p.displayHeight * (1 - p.originY) - 8).setDepth(p.depth - 1);
    }
  }

  destroy() {
    this.objects.forEach((o) => o.destroy());
    this.shadows.forEach((s) => s.shadow.destroy());
    this.storm?.remove();
    this.objects = [];
    this.shadows = [];
  }
}
