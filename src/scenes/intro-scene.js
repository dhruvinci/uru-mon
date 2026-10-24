import { SCENE_KEYS } from './scene-keys.js';
import { BaseScene } from './base-scene.js';
import { dataManager } from '../utils/data-manager.js';
import { playBackgroundMusic, playSoundFx } from '../utils/audio-utils.js';
import { AUDIO_KEYS } from '../assets/asset-keys.js';
import { ListMenu, MessageBox, readMenuInput, tween, wait, HINTS } from '../ui/ui-kit.js';

const NAME_SUGGESTIONS = { boy: ['Kiran', 'Arjun', 'Vikram', 'Sameer'], girl: ['Ananya', 'Diya', 'Meera', 'Kavya'] };

/**
 * New-game intro: Professor Sharada's welcome, boy/girl choice, name entry and meeting the rival.
 */
export class IntroScene extends BaseScene {
  constructor() {
    super({ key: SCENE_KEYS.INTRO_SCENE });
  }

  create() {
    super.create();
    dataManager.startNewGame();
    const g = this.add.graphics();
    g.fillGradientStyle(0x2a2050, 0x2a2050, 0x6a4a90, 0x6a4a90, 1);
    g.fillRect(0, 0, 1024, 576);
    this.platform = this.add.ellipse(512, 410, 360, 70, 0x000000, 0.25);
    this.portrait = this.add.image(512, 410, 'TRAINER_professor').setOrigin(0.5, 1).setScale(4).setAlpha(0);
    this.box = new MessageBox(this, { height: 144 });
    this.box.setVisible(false);
    /** @type {null | ((input: string) => void)} */
    this.inputHandler = null;
    playBackgroundMusic(this, AUDIO_KEYS.MUSIC_LAB);
    this.#run();
  }

  update(time) {
    super.update(time);
    if (!this._controls || this.typing) {
      return;
    }
    const input = readMenuInput(this._controls);
    if (!input) {
      return;
    }
    if (this.box.isWaiting && (input === 'OK' || input === 'CANCEL')) {
      this.box.handleConfirm(true);
      return;
    }
    this.inputHandler?.(input);
  }

  /** @param {string} s */
  #fmt(s) {
    return s.replaceAll('{PLAYER}', dataManager.state.player.name);
  }

  /** @param {string[]} lines */
  async #say(...lines) {
    for (const l of lines) {
      await this.box.show(this.#fmt(l));
    }
  }

  /** @param {string[]} items @returns {Promise<number>} */
  #choose(items) {
    return new Promise((resolve) => {
      const menu = new ListMenu(this, { x: 1024 - 262, y: 432 - (items.length * 46 + 36) - 8, width: 250, items, cancelable: false });
      this.box.setHints(HINTS.select);
      this.inputHandler = (input) => {
        const r = menu.handleInput(/** @type {any} */ (input));
        if (r && r.type === 'select') {
          this.inputHandler = null;
          this.box.setHints([]);
          menu.destroy();
          resolve(r.index);
        }
      };
    });
  }

  /** @param {string} key */
  async #showPortrait(key) {
    await tween(this, { targets: this.portrait, alpha: 0, duration: 200 });
    this.portrait.setTexture(this.textures.exists(key) ? key : '__MISSING');
    await tween(this, { targets: this.portrait, alpha: 1, duration: 300 });
  }

  async #run() {
    await wait(this, 400);
    await tween(this, { targets: this.portrait, alpha: 1, duration: 700 });
    await this.#say(
      'Namaskara! Welcome to the world of Urumon!',
      "I'm Sharada. Everyone in Basavanagudi calls me Professor Sharada - I study Urumon at the little lab near Bugle Rock."
    );
    const mon = this.add.image(700, 300, 'MON_004').setOrigin(0.5, 1).setScale(3).setAlpha(0);
    await tween(this, { targets: this.portrait, x: 360, duration: 400 });
    playSoundFx(this, AUDIO_KEYS.SFX_SEND_OUT);
    await tween(this, { targets: mon, alpha: 1, y: 330, duration: 400, ease: 'Back.out' });
    await this.#say(
      'This city is full of creatures we call Urumon.',
      'They nest in our lakes and parks, hide in tech parks and temple towers... this little one even lives in a coffee tumbler!',
      'People and Urumon have shared Bengaluru for as long as anyone can remember. Some battle side by side. Some just share a cup of filter kaapi.',
      'But lately the city is changing fast. Lakes are foaming, trees are vanishing... and the Urumon are worried.',
      'Now, tell me a little about yourself.'
    );
    await tween(this, { targets: mon, alpha: 0, duration: 300 });
    mon.destroy();
    await tween(this, { targets: this.portrait, x: 512, duration: 300 });

    let gender = 'boy';
    for (;;) {
      this.box.setText('Are you a boy or a girl?');
      const idx = await this.#choose(['BOY', 'GIRL']);
      gender = idx === 0 ? 'boy' : 'girl';
      await this.#showPortrait(`TRAINER_player_${gender}`);
      this.box.setText(`So you're a ${gender}?`);
      if ((await this.#choose(['YES', 'NO'])) === 0) {
        break;
      }
    }
    dataManager.state.player.gender = /** @type {'boy'|'girl'} */ (gender);

    await this.#say("And what's your name?");
    const name = await this.#askName(gender);
    dataManager.state.player.name = name;
    await this.#say(`${name}! What a lovely name.`);

    await this.#showPortrait('TRAINER_rival');
    await this.#say(
      'This is my grandson, Sudeep.',
      "You two have been best friends - and fiercest rivals - since you first fought over a cricket bat in kindergarten.",
      "He's been pestering me all week about getting his first Urumon. I suppose you both deserve one."
    );
    await this.#showPortrait(`TRAINER_player_${gender}`);
    await this.#say(
      '{PLAYER}, your very own Urumon story is about to begin!',
      'A city of jacaranda avenues, crowded junctions, hidden lakes and old hills is waiting for you.',
      "Come and see me at the lab when you're ready. Let's go!"
    );
    await tween(this, { targets: this.portrait, scale: 0.5, alpha: 0, duration: 900, ease: 'Quad.in' });
    this.cameras.main.fadeOut(600, 0, 0, 0);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      dataManager.state.gameStarted = false;
      this.scene.start(SCENE_KEYS.WORLD_SCENE, { area: 'player_house_2f' });
    });
  }

  /**
   * Name entry with a real text field (so phones get their keyboard) plus quick suggestions.
   * @param {string} gender
   * @returns {Promise<string>}
   */
  #askName(gender) {
    return new Promise((resolve) => {
      this.typing = true;
      const wrap = document.createElement('div');
      wrap.style.cssText =
        'position:fixed;left:50%;top:38%;transform:translate(-50%,-50%);z-index:50;background:#fbfaf6;border:6px solid #3a3058;' +
        'border-radius:16px;padding:18px 22px;font-family:Pixelify,monospace;color:#2d2a3a;box-shadow:0 8px 30px #0008;width:min(86vw,440px)';
      const suggestions = NAME_SUGGESTIONS[gender];
      wrap.innerHTML = `
        <div style="font-size:22px;margin-bottom:10px">Your name</div>
        <input maxlength="10" value="${suggestions[0]}" style="font:inherit;font-size:28px;width:100%;box-sizing:border-box;padding:8px 10px;border:3px solid #9b8fd0;border-radius:10px;outline:none" />
        <div class="sugs" style="display:flex;flex-wrap:wrap;gap:8px;margin:12px 0"></div>
        <button class="ok" style="font:inherit;font-size:24px;width:100%;padding:10px;border:none;border-radius:10px;background:#c4404a;color:#fff">OK</button>`;
      document.body.appendChild(wrap);
      const input = /** @type {HTMLInputElement} */ (wrap.querySelector('input'));
      const sugs = wrap.querySelector('.sugs');
      suggestions.forEach((s) => {
        const b = document.createElement('button');
        b.textContent = s;
        b.style.cssText = 'font:inherit;font-size:20px;padding:6px 12px;border:2px solid #9b8fd0;border-radius:8px;background:#efeafd';
        b.onclick = () => {
          input.value = s;
          input.focus();
        };
        sugs.appendChild(b);
      });
      const done = () => {
        const v = input.value.replace(/[^\p{L}\p{N} .'-]/gu, '').trim().slice(0, 10) || suggestions[0];
        wrap.remove();
        this.typing = false;
        resolve(v);
      };
      /** @type {HTMLButtonElement} */ (wrap.querySelector('button.ok')).onclick = done;
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          done();
        }
      });
      setTimeout(() => {
        input.focus();
        input.select();
      }, 50);
    });
  }
}
