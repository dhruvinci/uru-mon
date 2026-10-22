/**
 * Procedural move animations so every move has visual feedback without per-move spritesheets.
 * Physical moves lunge, special moves fire a projectile, status moves pulse an aura. Colours follow the move type.
 */
import { TYPE_COLORS } from '../engine/type-chart.js';
import { tween, wait } from '../../ui/ui-kit.js';

/**
 * @param {Phaser.Scene} scene
 * @param {number} x
 * @param {number} y
 * @param {number} color
 * @param {number} [count=10]
 * @param {number} [spread=90]
 */
function burst(scene, x, y, color, count = 10, spread = 90) {
  const pieces = [];
  for (let i = 0; i < count; i += 1) {
    const size = 10 + Math.floor(Math.random() * 3) * 4;
    const r = scene.add.rectangle(x, y, size, size, i % 3 === 0 ? 0xffffff : color).setDepth(30);
    pieces.push(r);
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.4;
    const dist = spread * (0.6 + Math.random() * 0.6);
    scene.tweens.add({
      targets: r,
      x: x + Math.cos(angle) * dist,
      y: y + Math.sin(angle) * dist,
      alpha: 0,
      angle: 90,
      duration: 380 + Math.random() * 200,
      ease: 'Quad.out',
      onComplete: () => r.destroy(),
    });
  }
  return wait(scene, 420);
}

/**
 * @param {Phaser.Scene} scene
 * @param {Phaser.GameObjects.Image} target
 */
export async function shakeAndBlink(scene, target) {
  const x = target.x;
  await tween(scene, { targets: target, x: x + 14, duration: 50, yoyo: true, repeat: 2 });
  target.setX(x);
  await tween(scene, { targets: target, alpha: 0.15, duration: 70, yoyo: true, repeat: 2 });
  target.setAlpha(1);
}

/**
 * @param {Phaser.Scene} scene
 * @param {object} p
 * @param {Phaser.GameObjects.Image} p.attacker
 * @param {Phaser.GameObjects.Image} p.target
 * @param {import('../engine/monster.js').MoveData} p.move
 * @param {'player'|'enemy'} p.side attacker side
 * @param {boolean} [p.skip]
 * @returns {Promise<void>}
 */
export async function playMoveFx(scene, { attacker, target, move, side, skip }) {
  if (skip) {
    return;
  }
  const color = TYPE_COLORS[move.type] ?? 0xffffff;
  const targetCenter = { x: target.x, y: target.y - target.displayHeight * 0.45 };
  const dir = side === 'player' ? 1 : -1;

  if (move.category === 'PHYSICAL') {
    const homeX = attacker.x;
    const homeY = attacker.y;
    await tween(scene, { targets: attacker, x: homeX + dir * 70, y: homeY - dir * 26, duration: 120, ease: 'Quad.in' });
    const flash = scene.add.circle(targetCenter.x, targetCenter.y, 70, color, 0.55).setDepth(30);
    scene.tweens.add({ targets: flash, scale: 1.8, alpha: 0, duration: 260, onComplete: () => flash.destroy() });
    burst(scene, targetCenter.x, targetCenter.y, color, 8, 80);
    await tween(scene, { targets: attacker, x: homeX, y: homeY, duration: 180, ease: 'Quad.out' });
    return;
  }

  if (move.category === 'SPECIAL') {
    const start = { x: attacker.x + dir * 60, y: attacker.y - attacker.displayHeight * 0.5 };
    const orbs = [];
    for (let i = 0; i < 3; i += 1) {
      const orb = scene.add.circle(start.x, start.y, 18 - i * 4, i === 0 ? 0xffffff : color, 1).setDepth(30);
      orb.setStrokeStyle(4, color);
      orbs.push(orb);
      scene.tweens.add({
        targets: orb,
        x: targetCenter.x,
        y: targetCenter.y,
        delay: i * 70,
        duration: 340,
        ease: 'Sine.in',
        onComplete: () => orb.destroy(),
      });
    }
    await wait(scene, 360 + 140);
    await burst(scene, targetCenter.x, targetCenter.y, color, 14, 110);
    return;
  }

  // status moves: aura on whoever the effect lands on
  const effect = /** @type {any} */ (move.effect) || {};
  const onSelf = effect.kind === 'heal' || effect.kind === 'rest' || effect.kind === 'cure' || (effect.kind === 'stat' && effect.target === 'self');
  const who = onSelf ? attacker : target;
  const cx = who.x;
  const cy = who.y - who.displayHeight * 0.45;
  for (let i = 0; i < 3; i += 1) {
    const ring = scene.add.circle(cx, cy, 30, color, 0).setStrokeStyle(8, color, 0.9).setDepth(30);
    scene.tweens.add({ targets: ring, scale: 3.2, alpha: 0, delay: i * 140, duration: 520, onComplete: () => ring.destroy() });
  }
  await wait(scene, 700);
}

/**
 * Up/down arrows for stat stage changes.
 * @param {Phaser.Scene} scene
 * @param {Phaser.GameObjects.Image} who
 * @param {number} amount
 */
export async function statChangeFx(scene, who, amount) {
  const up = amount > 0;
  const color = up ? 0xf07860 : 0x6090f0;
  const cx = who.x;
  const top = who.y - who.displayHeight;
  const arrows = [];
  for (let i = 0; i < 5; i += 1) {
    const x = cx - 100 + i * 50;
    const y = up ? who.y - 20 : top + 20;
    const tri = up
      ? scene.add.triangle(x, y, 0, 24, 24, 24, 12, 0, color)
      : scene.add.triangle(x, y, 0, 0, 24, 0, 12, 24, color);
    tri.setDepth(30).setAlpha(0.9);
    arrows.push(tri);
    scene.tweens.add({
      targets: tri,
      y: up ? y - 150 : y + 150,
      alpha: 0,
      delay: i * 60,
      duration: 600,
      onComplete: () => tri.destroy(),
    });
  }
  who.setTint(color);
  await wait(scene, 750);
  who.clearTint();
}

/**
 * Coloured flash on a status being inflicted.
 * @param {Phaser.Scene} scene
 * @param {Phaser.GameObjects.Image} who
 * @param {string} status
 */
export async function statusFx(scene, who, status) {
  const colors = { BRN: 0xf06030, PSN: 0xb050c0, PAR: 0xf0d020, SLP: 0x9090b0 };
  const c = colors[status] ?? 0xffffff;
  for (let i = 0; i < 2; i += 1) {
    who.setTint(c);
    await wait(scene, 120);
    who.clearTint();
    await wait(scene, 100);
  }
  await burst(scene, who.x, who.y - who.displayHeight * 0.45, c, 8, 70);
}
