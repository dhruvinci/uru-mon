import Phaser from '../lib/phaser.js';

/**
 * One-pass "HD-2D" post effect for the overworld camera:
 * - perspective tilt: the screen shows a trapezoid of the camera's view (wide at the top, narrow at the bottom) through a
 *   homography, so the far edge recedes and the near edge looms, as if the camera were tilted over the map;
 * - depth of field: a small blur that grows away from the focus band around the player;
 * - haze toward the far edge, a vignette, and a colour grade (used for time of day and weather).
 * With tilt 0 and blur 0 it is just the grade + vignette, which the ENHANCED graphics setting uses.
 */
const FRAG = `
#define SHADER_NAME URU_HD2D_FS
precision mediump float;
uniform sampler2D uMainSampler;
uniform vec2 uResolution;
uniform vec3 uH0;
uniform vec3 uH1;
uniform vec3 uH2;
uniform float uBlur;
uniform float uFocus;
uniform vec3 uHaze;
uniform float uHazeAmount;
uniform vec3 uGrade;
uniform float uSaturation;
uniform float uVignette;
varying vec2 outTexCoord;

vec2 warp(vec2 uv) {
  vec3 q = vec3(uv, 1.0);
  vec3 p = vec3(dot(uH0, q), dot(uH1, q), dot(uH2, q));
  return p.xy / p.z;
}

vec4 sampleTop(vec2 src) {
  // the texture is stored bottom-up
  return texture2D(uMainSampler, vec2(src.x, 1.0 - src.y));
}

void main() {
  vec2 uv = vec2(outTexCoord.x, 1.0 - outTexCoord.y);
  vec2 src = warp(uv);
  vec4 col = sampleTop(src);
  float dist = abs(uv.y - uFocus);
  float r = uBlur * smoothstep(0.12, 0.55, dist);
  if (r > 0.0) {
    vec2 px = r / uResolution;
    col = col * 0.36
      + (sampleTop(src + vec2(px.x, 0.0)) + sampleTop(src - vec2(px.x, 0.0))
      + sampleTop(src + vec2(0.0, px.y)) + sampleTop(src - vec2(0.0, px.y))) * 0.11
      + (sampleTop(src + px) + sampleTop(src - px)
      + sampleTop(src + vec2(px.x, -px.y)) + sampleTop(src + vec2(-px.x, px.y))) * 0.05;
  }
  float far = clamp(1.0 - uv.y, 0.0, 1.0);
  col.rgb = mix(col.rgb, uHaze, uHazeAmount * far * far);
  float grey = dot(col.rgb, vec3(0.299, 0.587, 0.114));
  col.rgb = mix(vec3(grey), col.rgb, uSaturation) * uGrade;
  vec2 c = uv - 0.5;
  col.rgb *= 1.0 - uVignette * smoothstep(0.35, 0.85, length(c * vec2(1.25, 1.0)));
  gl_FragColor = vec4(col.rgb, 1.0);
}
`;

/**
 * Homography taking the unit square (u, v) to the quad tl, tr, br, bl (Heckbert's square-to-quad).
 * @returns {number[][]} rows of a 3x3 matrix
 */
function squareToQuad(tl, tr, br, bl) {
  const dx1 = tr[0] - br[0];
  const dx2 = bl[0] - br[0];
  const dx3 = tl[0] - tr[0] + br[0] - bl[0];
  const dy1 = tr[1] - br[1];
  const dy2 = bl[1] - br[1];
  const dy3 = tl[1] - tr[1] + br[1] - bl[1];
  const den = dx1 * dy2 - dx2 * dy1;
  const g = (dx3 * dy2 - dx2 * dy3) / den;
  const h = (dx1 * dy3 - dx3 * dy1) / den;
  return [
    [tr[0] - tl[0] + g * tr[0], bl[0] - tl[0] + h * bl[0], tl[0]],
    [tr[1] - tl[1] + g * tr[1], bl[1] - tl[1] + h * bl[1], tl[1]],
    [g, h, 1],
  ];
}

export class Hd2dPipeline extends Phaser.Renderer.WebGL.Pipelines.PostFXPipeline {
  /** @param {Phaser.Game} game */
  constructor(game) {
    super({ game, name: 'UruHd2d', fragShader: FRAG });
    this.params = {
      tilt: 0, // 0 = flat; 0.2 = the bottom edge shows 60% of the width
      blur: 0,
      focus: 0.62,
      haze: [0.85, 0.9, 1.0],
      hazeAmount: 0,
      grade: [1, 1, 1],
      saturation: 1,
      vignette: 0.25,
    };
  }

  /** The homography for the current tilt. */
  matrix() {
    const inset = Math.max(0, Math.min(0.3, this.params.tilt));
    return squareToQuad([0, 0], [1, 0], [1 - inset, 1], [inset, 1]);
  }

  /**
   * Where on the camera's own view (0-1, top-left origin) the screen point (u, v) samples from.
   * @returns {number[]}
   */
  sourceAt(u, v) {
    const H = this.matrix();
    const w = H[2][0] * u + H[2][1] * v + H[2][2];
    return [(H[0][0] * u + H[0][1] * v + H[0][2]) / w, (H[1][0] * u + H[1][1] * v + H[1][2]) / w];
  }

  onPreRender() {
    const p = this.params;
    const H = this.matrix();
    this.set3f('uH0', H[0][0], H[0][1], H[0][2]);
    this.set3f('uH1', H[1][0], H[1][1], H[1][2]);
    this.set3f('uH2', H[2][0], H[2][1], H[2][2]);
    this.set2f('uResolution', this.renderer.width, this.renderer.height);
    this.set1f('uBlur', p.blur);
    this.set1f('uFocus', p.focus);
    this.set3f('uHaze', p.haze[0], p.haze[1], p.haze[2]);
    this.set1f('uHazeAmount', p.hazeAmount);
    this.set3f('uGrade', p.grade[0], p.grade[1], p.grade[2]);
    this.set1f('uSaturation', p.saturation);
    this.set1f('uVignette', p.vignette);
  }
}
