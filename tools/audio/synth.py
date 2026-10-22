"""uru-mon soundtrack & SFX: a tiny GBA-style synthesizer with original compositions.

Voices: band-limited pulse waves (PolyBLEP), triangle bass, a Karplus-Strong pluck (veena-ish), a soft flute,
and drums including tabla-like 'dha/dhin/na/ta' strokes. Songs are written in a compact note language:

    "C5:1 D5:.5 E5:.5 G5:2 r:1 A5>C6:1"   name+octave, ':' duration in beats, 'r' rest, 'X>Y' slide (gamaka)

Run: python3 tools/audio/synth.py   (writes assets/audio/{music,sfx}/*.ogg + .mp3)
"""
import os
import subprocess
import sys

import numpy as np

SR = 32000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "audio")
NOTE_INDEX = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
              "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
rng = np.random.default_rng(7)


def midi(name):
    n = name[:-1]
    octave = int(name[-1])
    return 12 * (octave + 1) + NOTE_INDEX[n]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------------------------------------
# oscillators
# ------------------------------------------------------------------------------------------------
def _polyblep(t, dt):
    """PolyBLEP residual for a naive step at phase 0 (t and dt are arrays)."""
    out = np.zeros_like(t)
    a = t < dt
    x = t[a] / dt[a]
    out[a] = x + x - x * x - 1
    b = t > 1 - dt
    x = (t[b] - 1) / dt[b]
    out[b] = x * x + x + x + 1
    return out


def pulse(freqs, duty=0.5):
    """Band-limited pulse wave for a per-sample frequency array."""
    dt = np.clip(freqs / SR, 1e-6, 0.45)
    phase = np.cumsum(dt) % 1.0
    sq = np.where(phase < duty, 1.0, -1.0)
    sq += _polyblep(phase, dt)
    sq -= _polyblep((phase - duty) % 1.0, dt)
    return sq * 0.5


def triangle(freqs):
    phase = np.cumsum(freqs / SR) % 1.0
    return (2 * np.abs(2 * phase - 1) - 1) * 0.7


def sine(freqs):
    return np.sin(2 * np.pi * np.cumsum(freqs / SR))


def pluck(freq, n, bright=0.6):
    """Karplus-Strong string (vectorised per period) with a little buzz for a veena/sitar colour."""
    period = max(2, int(SR / freq))
    blocks = n // period + 2
    y = np.zeros(blocks * period)
    y[:period] = rng.uniform(-1, 1, period) * bright
    decay = 0.996
    for k in range(1, blocks):
        prev = y[(k - 1) * period:k * period]
        y[k * period:(k + 1) * period] = decay * 0.5 * (prev + np.roll(prev, -1))
    out = y[:n]
    buzz = np.clip(out * 3, -1, 1) * 0.15
    return (out + buzz) * 0.8


def envelope(n, a=0.005, d=0.08, s=0.7, r=0.05):
    env = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    env[:na] = np.linspace(0, 1, na, endpoint=False) if na else env[:na]
    nd = min(nd, max(0, n - na))
    if nd:
        env[na:na + nd] = np.linspace(1, s, nd, endpoint=False)
    nr = min(nr, n)
    if nr:
        env[n - nr:] *= np.linspace(1, 0, nr)
    return env


# ------------------------------------------------------------------------------------------------
# note language
# ------------------------------------------------------------------------------------------------
def parse(line):
    """-> list of (start_beat, dur_beats, midi_from | None, midi_to | None)"""
    events = []
    t = 0.0
    for tok in line.split():
        if ":" in tok:
            name, dur = tok.split(":")
            dur = float(dur)
        else:
            name, dur = tok, 1.0
        if name == "r":
            events.append((t, dur, None, None))
        elif ">" in name:
            a, b = name.split(">")
            events.append((t, dur, midi(a), midi(b)))
        else:
            m = midi(name)
            events.append((t, dur, m, m))
        t += dur
    return events, t


def render_voice(line, bpm, voice, vol=0.3, transpose=0, total_beats=None):
    events, beats = parse(line)
    beats = total_beats or beats
    spb = 60.0 / bpm
    n_total = int(beats * spb * SR) + SR * 2
    out = np.zeros(n_total)
    for start, dur, m0, m1 in events:
        if m0 is None:
            continue
        m0 += transpose
        m1 += transpose
        i0 = int(start * spb * SR)
        n = int(dur * spb * SR)
        if n <= 0:
            continue
        if voice == "pluck":
            ring = n + int(0.25 * SR)
            sig = pluck(hz(m0), ring)
            if m1 != m0:  # approximate a gamaka by resampling the pluck
                ratio = np.linspace(1, 2 ** ((m1 - m0) / 12), ring)
                idx = np.clip(np.cumsum(ratio), 0, ring - 1).astype(int)
                sig = sig[idx]
            sig *= envelope(ring, 0.002, 0.05, 0.9, 0.08)
            n = ring
        else:
            glide = np.ones(n) * m0
            if m1 != m0:
                k = min(n, int(0.12 * SR))
                glide[:k] = np.linspace(m0, m1, k)
                glide[k:] = m1
            vib_depth = 0.15 if dur * spb > 0.35 and voice in ("flute", "lead", "lead12") else 0.0
            vib = vib_depth * np.sin(2 * np.pi * 5.5 * np.arange(n) / SR) * np.clip(np.arange(n) / (0.2 * SR), 0, 1)
            freqs = hz(glide + vib)
            if voice == "lead":
                sig = pulse(freqs, 0.25) * envelope(n, 0.004, 0.1, 0.75, 0.04)
            elif voice == "lead12":
                sig = pulse(freqs, 0.125) * envelope(n, 0.004, 0.1, 0.7, 0.04)
            elif voice == "square":
                sig = pulse(freqs, 0.5) * envelope(n, 0.004, 0.08, 0.65, 0.04)
            elif voice == "arp":
                sig = pulse(freqs, 0.125) * envelope(n, 0.002, 0.06, 0.25, 0.02)
            elif voice == "bass":
                sig = triangle(freqs) * envelope(n, 0.003, 0.05, 0.85, 0.03)
            elif voice == "flute":
                sig = (sine(freqs) * 0.8 + triangle(freqs * 2) * 0.12) * envelope(n, 0.04, 0.1, 0.8, 0.08)
            elif voice == "pad":
                sig = (pulse(freqs, 0.5) * 0.3 + sine(freqs) * 0.6) * envelope(n, 0.12, 0.2, 0.7, 0.15)
            else:
                raise ValueError(voice)
        end = min(n_total, i0 + len(sig))
        out[i0:end] += sig[: end - i0] * vol
    return out[: int(beats * spb * SR) + SR * 2], int(beats * spb * SR)


# ------------------------------------------------------------------------------------------------
# drums
# ------------------------------------------------------------------------------------------------
def _noise(n):
    return rng.uniform(-1, 1, n)


def drum(kind):
    if kind == "K":  # kick
        n = int(0.18 * SR)
        f = np.linspace(140, 45, n)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.arange(n) / (0.06 * SR)) * 0.9
    if kind == "S":  # snare
        n = int(0.16 * SR)
        nz = _noise(n)
        nz = np.diff(np.concatenate([[0], nz]))
        return (nz * 0.5 + np.sin(2 * np.pi * 190 * np.arange(n) / SR) * 0.3) * np.exp(-np.arange(n) / (0.04 * SR))
    if kind == "H":  # hat
        n = int(0.05 * SR)
        nz = np.diff(np.concatenate([[0], _noise(n)]))
        return nz * np.exp(-np.arange(n) / (0.012 * SR)) * 0.35
    if kind == "O":  # open hat
        n = int(0.2 * SR)
        nz = np.diff(np.concatenate([[0], _noise(n)]))
        return nz * np.exp(-np.arange(n) / (0.07 * SR)) * 0.25
    if kind == "D":  # tabla bayan 'dhin/ge': low pitch that bends up
        n = int(0.32 * SR)
        f = np.linspace(85, 130, n)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.arange(n) / (0.11 * SR)) * 0.8
    if kind == "N":  # tabla dayan 'na': bright ringing ping
        n = int(0.22 * SR)
        t = np.arange(n) / SR
        sig = np.sin(2 * np.pi * 980 * t) * 0.6 + np.sin(2 * np.pi * 1960 * t) * 0.2
        return (sig + _noise(n) * 0.15 * np.exp(-t / 0.004)) * np.exp(-t / 0.07) * 0.5
    if kind == "T":  # tabla 'ta/te': short dry tap
        n = int(0.06 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 620 * t) * 0.5 + _noise(n) * 0.3) * np.exp(-t / 0.012) * 0.6
    if kind == "C":  # crash
        n = int(0.9 * SR)
        nz = np.diff(np.concatenate([[0], _noise(n)]))
        return nz * np.exp(-np.arange(n) / (0.3 * SR)) * 0.25
    raise ValueError(kind)


DRUM_CACHE = {}


def drum_steps(pat):
    """'K.H(SH)...' -> ['K', '.', 'H', 'SH', ...]; parentheses stack hits on one step."""
    steps, i = [], 0
    while i < len(pat):
        if pat[i] == "(":
            j = pat.index(")", i)
            steps.append(pat[i + 1:j])
            i = j + 1
        else:
            steps.append(pat[i])
            i += 1
    return steps


def render_drums(patterns, bpm, bars, vol=0.5):
    """patterns: list of 16-step strings per bar (cycled); '.' rest; several chars may be stacked with '+'."""
    spb = 60.0 / bpm
    step = spb / 4
    n_total = int(bars * 4 * spb * SR) + SR
    out = np.zeros(n_total)
    for bar in range(bars):
        steps = drum_steps(patterns[bar % len(patterns)])
        for i, s in enumerate(steps[:16]):
            if s == ".":
                continue
            for k in s:
                if k not in DRUM_CACHE:
                    DRUM_CACHE[k] = drum(k)
                d = DRUM_CACHE[k]
                i0 = int((bar * 16 + i) * step * SR)
                e = min(n_total, i0 + len(d))
                out[i0:e] += d[: e - i0] * vol
    return out


# ------------------------------------------------------------------------------------------------
# harmony helpers
# ------------------------------------------------------------------------------------------------
CHORDS = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11],
          "sus": [0, 5, 7], "dim": [0, 3, 6], "add9": [0, 4, 7, 14], "5": [0, 7, 12]}


def chord_notes(sym, octave):
    root, qual = sym, ""
    for q in sorted(CHORDS, key=len, reverse=True):
        if q and sym.endswith(q) and sym[: -len(q)] in NOTE_INDEX:
            root, qual = sym[: -len(q)], q
            break
    base = midi(f"{root}{octave}")
    return [base + i for i in CHORDS[qual]]


def name_of(m):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[m % 12]}{m // 12 - 1}"


def bass_line(chords, style="root", octave=2):
    toks = []
    for sym in chords:
        c = chord_notes(sym, octave)
        r, f = c[0], c[2] if len(c) > 2 else c[0] + 7
        if style == "root":
            toks += [f"{name_of(r)}:1"] * 4
        elif style == "pump":
            toks += [f"{name_of(r)}:.5", f"{name_of(r + 12)}:.5"] * 4
        elif style == "fifth":
            toks += [f"{name_of(r)}:1", f"{name_of(f)}:1", f"{name_of(r)}:1", f"{name_of(f)}:1"]
        elif style == "drive":
            toks += [f"{name_of(r)}:.5"] * 8
        elif style == "walk":
            third = c[1]
            toks += [f"{name_of(r)}:1", f"{name_of(third)}:1", f"{name_of(f)}:1", f"{name_of(f + 2)}:1"]
        elif style == "long":
            toks += [f"{name_of(r)}:4"]
        elif style == "half":
            toks += [f"{name_of(r)}:2", f"{name_of(f)}:2"]
    return " ".join(toks)


def arp_line(chords, octave=4, pattern=(0, 1, 2, 1), step=0.5):
    toks = []
    per_bar = int(4 / step)
    for sym in chords:
        c = chord_notes(sym, octave)
        for i in range(per_bar):
            toks.append(f"{name_of(c[pattern[i % len(pattern)] % len(c)])}:{step}")
    return " ".join(toks)


def pad_line(chords, octave=4):
    voices = [[], [], []]
    for sym in chords:
        c = chord_notes(sym, octave)
        for v in range(3):
            voices[v].append(f"{name_of(c[v % len(c)])}:4")
    return [" ".join(v) for v in voices]


# ------------------------------------------------------------------------------------------------
# mixing & output
# ------------------------------------------------------------------------------------------------
def mix_song(bpm, bars, parts, drums=None, drum_vol=0.45, loop=True, echo=0.18):
    """parts: list of (line, voice, vol, transpose). Returns a float32 stereo array."""
    spb = 60.0 / bpm
    body = int(bars * 4 * spb * SR)
    tail = SR * 2
    left = np.zeros(body + tail)
    right = np.zeros(body + tail)
    pans = {"lead": -0.15, "lead12": 0.2, "square": 0.0, "arp": 0.35, "bass": 0.0, "flute": -0.1, "pluck": 0.25, "pad": 0.0}
    for line, voice, vol, tr in parts:
        sig, _ = render_voice(line, bpm, voice, vol, tr, total_beats=bars * 4)
        sig = sig[: body + tail]
        sig = np.pad(sig, (0, max(0, body + tail - len(sig))))
        p = pans.get(voice, 0)
        left += sig * (1 - p)
        right += sig * (1 + p)
    if drums:
        d = render_drums(drums, bpm, bars, drum_vol)
        d = np.pad(d, (0, max(0, body + tail - len(d))))[: body + tail]
        left += d
        right += d
    if echo:
        delay = int(spb * 0.75 * SR)
        for ch in (left, right):
            ech = np.zeros_like(ch)
            ech[delay:] = ch[:-delay] * echo
            ch += ech
    stereo = np.stack([left, right], axis=1)
    if loop:
        # wrap the release tail into the start so the loop point is seamless
        out = stereo[:body].copy()
        out[:tail] += stereo[body:body + tail]
        stereo = out
    else:
        stereo = stereo[: body + tail]
    return normalize(stereo)


def normalize(x, peak=0.89):
    x = x - np.mean(x, axis=0)
    rms = np.sqrt(np.mean(x ** 2))
    target_rms = 0.16
    if rms > 0:
        x = x * (target_rms / rms)
    m = np.max(np.abs(x))
    if m > peak:
        x = np.tanh(x / m * 1.2) / np.tanh(1.2) * peak
    return x.astype(np.float32)


def write(path_noext, data):
    os.makedirs(os.path.dirname(path_noext), exist_ok=True)
    raw = path_noext + ".f32"
    data.astype(np.float32).tofile(raw)
    ch = 1 if data.ndim == 1 else data.shape[1]
    for ext, codec in (("ogg", ["-c:a", "libvorbis", "-q:a", "4"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "112k"])):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", raw,
                        *codec, f"{path_noext}.{ext}"], check=True)
    os.remove(raw)


# ------------------------------------------------------------------------------------------------
# compositions
# ------------------------------------------------------------------------------------------------
TABLA_TEENTAL = ["D...N.T.D.N.T.N.", "D.N.N.T.D...N.T."]
DRIVE = ["K.H.S.H.K.H.S.H.", "K.H.S.H.K.K.S.HH"]


def main_motif():
    # Mohanam (C D E G A) - the game's main theme
    a = ("E5:1 G5:.5 A5:.5 C6:1.5 A5:.5 G5:1 E5:.5 D5:.5 E5:2 r:1 "
         "G5:.5 A5:.5 C6:1 D6:.5 C6:.5 A5:1 G5:1 A5:2 r:2 ")
    b = ("C6:1 D6:.5 E6:.5 D6:1 C6:.5 A5:.5 G5:1.5 A5:.5 G5:.5 E5:.5 D5:1 E5:3 r:1 "
         "D5:.5 E5:.5 G5:1 A5:.5 G5:.5 E5:1 D5:.5 C5:.5 D5>E5:1 C5:3 r:1 ")
    return a, b


def song_title():
    a, b = main_motif()
    chords = ["C", "G", "Am", "F", "C", "G", "F", "G", "Am", "F", "C", "G", "F", "G", "C", "C"]
    lead = a + b + a.replace("r:2", "r:1 G5:1") + b
    return mix_song(100, 16, [(lead, "lead", 0.32, 0), (lead, "pluck", 0.18, -12), (bass_line(chords, "half"), "bass", 0.5, 0),
                              (arp_line(chords, 4, (0, 1, 2, 3), 0.25), "arp", 0.12, 0)] + [(p, "pad", 0.06, 0) for p in pad_line(chords)],
                    drums=["K.......S.......", "K...K...S...O..."], drum_vol=0.35)


def song_route():
    a, b = main_motif()
    chords = ["G", "D", "Em", "C", "G", "D", "C", "D"] * 2
    lead = a + b
    return mix_song(126, 16, [(lead, "lead", 0.3, -5), (bass_line(chords, "pump"), "bass", 0.5, 0),
                              (arp_line(chords, 4, (0, 2, 1, 2), 0.5), "arp", 0.14, 0)],
                    drums=TABLA_TEENTAL + ["K...S...K.K.S..."], drum_vol=0.4)


def song_town():
    # Kalyani flavour (raised 4th) in F, bouncy
    lead = ("F5:.5 G5:.5 A5:1 B5:.5 C6:.5 A5:1 G5:.5 F5:.5 G5:2 "
            "A5:.5 B5:.5 C6:1 D6:.5 C6:.5 B5:1 A5:.5 G5:.5 A5:2 "
            "C6:1 B5:.5 A5:.5 G5:1 E5:.5 F5:.5 G5:1 A5:.5 G5:.5 F5:2 "
            "E5:.5 F5:.5 G5:1 A5:.5 B5:.5 C6:1 A5:1 F5:3 r:1 ")
    chords = ["F", "C", "Dm", "Bb", "F", "C", "Bb", "C"]
    return mix_song(112, 8, [(lead, "lead", 0.3, 0), (lead, "pluck", 0.12, 12), (bass_line(chords, "fifth"), "bass", 0.5, 0),
                             (arp_line(chords, 4, (0, 1, 2, 1), 0.5), "arp", 0.13, 0)], drums=TABLA_TEENTAL, drum_vol=0.4)


def song_home():
    lead = ("E5:1.5 D5:.5 C5:1 G4:1 A4:1.5 C5:.5 D5:2 E5:1.5 G5:.5 E5:1 D5:1 C5:3 r:1 "
            "A4:1 C5:1 D5:1 E5:1 G5:1.5 E5:.5 D5:2 C5:1 D5:.5 E5:.5 D5:1 A4:1 C5:4 ")
    chords = ["C", "Am", "F", "G", "C", "Am", "F", "C"]
    return mix_song(84, 8, [(lead, "flute", 0.32, 0), (bass_line(chords, "half"), "bass", 0.45, 0),
                            (arp_line(chords, 4, (0, 1, 2, 1), 0.5), "pluck", 0.1, 0)], drums=["D.......N.......", "D.......N...T..."], drum_vol=0.25)


def song_city():
    lead = ("C5:.5 C5:.5 r:.5 Eb5:.5 r:.5 F5:.5 G5:1 Bb5:.5 G5:.5 F5:.5 Eb5:.5 F5:2 "
            "C5:.5 C5:.5 r:.5 Eb5:.5 r:.5 F5:.5 G5:1 C6:.5 Bb5:.5 G5:.5 F5:.5 G5:2 "
            "Bb5:1 G5:.5 F5:.5 Eb5:1 F5:.5 G5:.5 F5:1 Eb5:.5 C5:.5 Eb5:2 "
            "F5:.5 G5:.5 Bb5:.5 C6:.5 Bb5:.5 G5:.5 F5:.5 Eb5:.5 C5:3 r:1 ")
    chords = ["Cm7", "Fm", "Cm7", "Gm", "Ab", "Bb", "Fm", "G"]
    return mix_song(128, 8, [(lead, "square", 0.28, 0), (bass_line(chords, "drive"), "bass", 0.5, 0),
                             (arp_line(chords, 4, (0, 2, 3, 2), 0.25), "arp", 0.1, 0)], drums=DRIVE, drum_vol=0.42)


def song_park():
    lead = ("G5:.25 A5:.25 G5:.5 E5:1 D5:.5 E5:.5 G5:1 A5:.25 C6:.25 A5:.5 G5:1 E5:1 D5:1 "
            "E5:.5 G5:.5 A5:1 G5:.25 A5:.25 G5:.5 E5:1 D5:.5 C5:.5 D5:3 r:1 ")
    chords = ["C", "Am", "F", "G"] * 2
    return mix_song(104, 8, [(lead + lead.replace("D5:3 r:1", "C5:3 r:1"), "lead12", 0.26, 0), (bass_line(chords, "half"), "bass", 0.42, 0),
                             (arp_line(chords, 5, (0, 1, 2, 1), 0.5), "pluck", 0.1, 0)], drums=["T...N...T...N.T.", "T...N...D...N..."], drum_vol=0.3)


def song_cave():
    lead = ("E4:2 r:1 G4:.5 F4:.5 E4:3 r:1 B3:2 r:1 C4:.5 D4:.5 E4:4 "
            "G4:2 r:1 A4:.5 G4:.5 F4:3 r:1 E4:2 D4:1 C4:1 B3:4 ")
    chords = ["Em", "Em", "C", "B", "Em", "Am", "C", "B"]
    return mix_song(72, 8, [(lead, "flute", 0.3, 0), (bass_line(chords, "long", 2), "bass", 0.45, 0)] +
                    [(p, "pad", 0.05, -12) for p in pad_line(chords)], drums=["D...............", "........N......."], drum_vol=0.3, echo=0.35)


def song_lab():
    lead = ("C5:.5 E5:.5 G5:.5 C6:.5 B5:.5 G5:.5 E5:1 D5:.5 F5:.5 A5:.5 D6:.5 C6:.5 A5:.5 F5:1 "
            "E5:.5 G5:.5 C6:.5 E6:.5 D6:.5 B5:.5 G5:1 F5:.5 E5:.5 D5:.5 B4:.5 C5:2 ")
    chords = ["C", "Dm", "C", "G"] * 2
    return mix_song(116, 8, [(lead * 2, "lead12", 0.26, 0), (bass_line(chords, "walk"), "bass", 0.45, 0),
                             (arp_line(chords, 4, (0, 1, 2, 1), 0.25), "arp", 0.1, 0)], drums=["K...T...K.T.T...", "K...T...K...T.T."], drum_vol=0.35)


def song_darshini():
    lead = ("G4:.5 C5:.5 E5:1 D5:.5 C5:.5 D5:1 E5:.5 G5:.5 A5:1 G5:2 "
            "E5:.5 D5:.5 C5:1 A4:.5 G4:.5 A4:1 C5:.5 D5:.5 C5:3 r:1 ")
    chords = ["C", "F", "G", "C"]
    return mix_song(96, 4, [(lead, "pluck", 0.32, 0), (lead, "flute", 0.12, 12), (bass_line(chords, "half"), "bass", 0.42, 0)],
                    drums=TABLA_TEENTAL, drum_vol=0.35)


def song_arena():
    lead = ("A4:1 C5:1 D5:1 E5:1 F5:2 E5:1 D5:1 E5:3 r:1 C5:1 B4:1 "
            "A4:1 C5:1 D5:1 E5:1 G5:2 F5:1 E5:1 D5:3 r:1 E5:2 ")
    chords = ["Am", "F", "Am", "E", "Am", "F", "Dm", "E"]
    return mix_song(122, 8, [(lead, "square", 0.26, 0), (bass_line(chords, "drive"), "bass", 0.5, 0),
                             (arp_line(chords, 4, (0, 1, 2, 1), 0.25), "arp", 0.1, 0)],
                    drums=["K...K...K...S...", "K.K.K...K...S.SS"], drum_vol=0.42)


def song_syndicate():
    # Mayamalavagowla-ish: C Db E F G Ab B
    lead = ("C5:.5 Db5:.5 E5:1 r:.5 F5:.5 E5:.5 Db5:.5 C5:2 r:1 G4:1 "
            "Ab4:.5 B4:.5 C5:1 Db5:.5 C5:.5 B4:.5 Ab4:.5 G4:3 r:1 ")
    chords = ["C5", "Db", "C5", "G", "Ab", "G", "C5", "G"]
    return mix_song(110, 8, [(lead * 2, "lead", 0.28, 0), (bass_line(chords, "drive"), "bass", 0.52, 0),
                             (arp_line(chords, 3, (0, 1, 0, 2), 0.25), "arp", 0.12, 12)],
                    drums=["K..HK..HS..HK..H", "K..HK.KHS..HK.SH"], drum_vol=0.45)


def battle_lead_a():
    return ("E5:.5 E5:.5 G5:.5 A5:.5 B5:1 A5:.5 G5:.5 E5:.5 D5:.5 E5:1 B4:1 "
            "D5:.5 E5:.5 G5:.5 A5:.5 B5:.5 D6:.5 B5:1 A5:2 G5:1 A5:1 "
            "B5:1 A5:.5 G5:.5 E5:1 D5:.5 E5:.5 G5:1 E5:.5 D5:.5 B4:2 "
            "C5:.5 D5:.5 E5:.5 G5:.5 A5:1 G5:.5 E5:.5 D5>E5:4 ")


def song_wild():
    chords = ["Em", "C", "D", "Em", "Em", "C", "D", "B7"] * 2
    lead = battle_lead_a()
    lead2 = lead.replace("D5>E5:4", "B5:4")
    return mix_song(150, 16, [(lead + lead2, "lead", 0.3, 0), (bass_line(chords, "drive"), "bass", 0.52, 0),
                              (arp_line(chords, 4, (0, 1, 2, 1), 0.25), "arp", 0.11, 0)],
                    drums=["K.HKS.H.K.HKS.HH", "K.HKS.H.KKH.(SO).T."], drum_vol=0.45)


def song_trainer():
    chords = ["Am", "Am", "F", "G", "Am", "Am", "F", "E7"] * 2
    lead = battle_lead_a()
    return mix_song(146, 16, [(lead + lead, "square", 0.28, -7), (bass_line(chords, "drive"), "bass", 0.52, 0),
                              (arp_line(chords, 4, (0, 2, 1, 2), 0.25), "arp", 0.11, 0)],
                    drums=["K.H.S.HKK.H.S.H.", "K.HKS.H.K.HKS.TT"], drum_vol=0.45)


def song_leader():
    lead = ("D5:1 F5:.5 G5:.5 A5:1 C6:1 Bb5:.5 A5:.5 G5:.5 F5:.5 G5:2 "
            "A5:1 G5:.5 F5:.5 E5:1 C5:1 D5:.5 E5:.5 F5:.5 G5:.5 A5:2 "
            "D6:1 C6:.5 Bb5:.5 A5:1 F5:1 G5:.5 A5:.5 Bb5:.5 C6:.5 D6:2 "
            "C6:.5 Bb5:.5 A5:.5 G5:.5 F5:1 E5:1 D5:4 ")
    chords = ["Dm", "F", "C", "Gm", "Dm", "Bb", "C", "A7"] * 2
    return mix_song(152, 16, [(lead * 2, "lead", 0.28, 0), (lead * 2, "pluck", 0.1, -12), (bass_line(chords, "drive"), "bass", 0.52, 0),
                              (arp_line(chords, 4, (0, 1, 2, 3), 0.25), "arp", 0.1, 0)],
                    drums=["K.HKS.HKK.HKS.HH", "K.HKS.HKK.K.(SC).SS"], drum_vol=0.47)


def song_rival():
    lead = ("G5:.5 G5:.5 A5:.5 B5:.5 D6:1 B5:.5 A5:.5 G5:1 E5:1 D5:2 "
            "E5:.5 G5:.5 A5:1 B5:.5 A5:.5 G5:1 E5:.5 D5:.5 E5:3 r:1 ")
    chords = ["G", "Em", "C", "D"] * 2
    return mix_song(140, 8, [(lead * 2, "lead12", 0.3, 0), (bass_line(chords, "pump"), "bass", 0.5, 0),
                             (arp_line(chords, 4, (0, 1, 2, 1), 0.25), "arp", 0.1, 0)], drums=DRIVE, drum_vol=0.45)


def song_legend():
    lead = ("E5:2 B5:2 A5:1 G5:1 F#5:2 E5:3 D5:1 E5:4 "
            "G5:2 A5:2 B5:1 D6:1 C6:2 B5:3 A5:1 B5:4 ")
    chords = ["Em", "C", "Am", "B", "Em", "C", "D", "B"]
    return mix_song(90, 8, [(lead, "flute", 0.3, 0), (lead, "pluck", 0.12, -12), (bass_line(chords, "long"), "bass", 0.5, 0)] +
                    [(p, "pad", 0.07, 0) for p in pad_line(chords, 4)], drums=["D.......D...N...", "D...D...D...N.N."], drum_vol=0.4, echo=0.3)


def song_victory():
    fanfare = "C5:.5 E5:.5 G5:.5 C6:1.5 G5:.5 A5:.5 B5:.5 C6:3 r:2 "
    loop = ("E5:1 D5:.5 C5:.5 D5:1 G4:1 C5:1 E5:1 D5:2 E5:1 G5:.5 E5:.5 D5:1 C5:1 D5:1 E5:.5 D5:.5 C5:2 ")
    chords = ["C", "F", "C", "G", "C", "Am", "F", "G", "C", "F"]
    return mix_song(128, 10, [(fanfare + loop + loop.replace("C5:2", "C5:1 r:1"), "lead", 0.3, 0),
                              (bass_line(chords, "pump"), "bass", 0.48, 0), (arp_line(chords, 4, (0, 1, 2, 1), 0.5), "arp", 0.12, 0)],
                    drums=["K...S...K...S...", "K...S...K.K.S..."], drum_vol=0.38)


def song_evolution():
    lead = " ".join(f"{n}:.25" for n in ["C5", "E5", "G5", "C6", "D5", "F5", "A5", "D6", "E5", "G5", "B5", "E6", "F5", "A5", "C6", "F6"] * 4)
    chords = ["C", "Dm", "Em", "F"] * 2
    return mix_song(100, 8, [(lead, "arp", 0.22, 0), (bass_line(chords, "long"), "bass", 0.45, 0)] +
                    [(p, "pad", 0.08, 0) for p in pad_line(chords)], drums=["N.......N.......", "N...N...N...N..."], drum_vol=0.2, echo=0.3)


def song_council():
    lead = ("B4:.5 D5:.5 F#5:.5 G5:.5 F#5:1 E5:1 D5:.5 E5:.5 F#5:.5 A5:.5 G5:1 F#5:1 "
            "E5:.5 G5:.5 B5:.5 C6:.5 B5:1 A5:1 G5:.5 F#5:.5 E5:.5 D5:.5 F#5:2 "
            "B5:1 A5:.5 G5:.5 F#5:1 D5:1 E5:.5 F#5:.5 G5:.5 A5:.5 B5:2 "
            "C6:.5 B5:.5 A5:.5 G5:.5 F#5:1 E5:.5 D5:.5 B4:4 ")
    chords = ["Bm", "G", "D", "A", "Em", "G", "F#7", "Bm"] * 2
    return mix_song(156, 16, [(lead * 2, "square", 0.28, 0), (lead * 2, "lead12", 0.1, 12), (bass_line(chords, "drive"), "bass", 0.54, 0),
                              (arp_line(chords, 4, (0, 1, 2, 1), 0.25), "arp", 0.1, 0)],
                    drums=["K.HKS.HKK.HKS.HK", "K.HKS.HKK.H(KC).SSS"], drum_vol=0.48)


def song_credits():
    a, b = main_motif()
    chords = ["F", "C", "Dm", "Bb", "F", "C", "Bb", "C"] * 3
    lead = (a + b) * 1 + a
    return mix_song(104, 24, [(lead, "flute", 0.3, 5), (lead, "pluck", 0.14, -7), (bass_line(chords, "half"), "bass", 0.45, 0),
                              (arp_line(chords, 4, (0, 1, 2, 1), 0.5), "arp", 0.1, 0)],
                    drums=TABLA_TEENTAL, drum_vol=0.35, loop=False)


SONGS = {
    "title": song_title, "home": song_home, "town": song_town, "city": song_city, "route": song_route, "park": song_park,
    "cave": song_cave, "lab": song_lab, "darshini": song_darshini, "arena": song_arena, "syndicate": song_syndicate,
    "rival": song_rival, "wild": song_wild, "trainer": song_trainer, "leader": song_leader, "legend": song_legend,
    "victory": song_victory, "evolution": song_evolution, "council": song_council, "credits": song_credits,
}


# ------------------------------------------------------------------------------------------------
# sound effects
# ------------------------------------------------------------------------------------------------
def sfx_tone(freqs_hz, dur, voice="square", duty=0.5, decay=None, vol=0.5):
    n = int(dur * SR)
    f = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(freqs_hz)), freqs_hz)
    sig = pulse(f, duty) if voice == "square" else triangle(f) if voice == "tri" else sine(f)
    env = np.exp(-np.arange(n) / (decay * SR)) if decay else envelope(n, 0.002, 0.02, 0.8, 0.02)
    return sig * env * vol


def seq(*parts, gap=0.0):
    out = []
    for p in parts:
        out.append(p)
        if gap:
            out.append(np.zeros(int(gap * SR)))
    return np.concatenate(out)


def arpeggio(notes, step, voice="square", duty=0.25, vol=0.45, last=0.3):
    return np.concatenate([sfx_tone([hz(midi(n))] * 2, last if i == len(notes) - 1 else step, voice, duty, vol=vol)
                           for i, n in enumerate(notes)])


def noise_burst(dur, vol=0.4, decay=0.05, hp=True):
    n = int(dur * SR)
    nz = rng.uniform(-1, 1, n)
    if hp:
        nz = np.diff(np.concatenate([[0], nz]))
    return nz * np.exp(-np.arange(n) / (decay * SR)) * vol


def make_sfx():
    s = {}
    s["select"] = sfx_tone([1320, 1320], 0.05, duty=0.25, vol=0.35)
    s["bump"] = sfx_tone([110, 80], 0.09, "tri", vol=0.6)
    s["door"] = seq(noise_burst(0.12, 0.25, 0.04), sfx_tone([220, 180], 0.12, "tri", vol=0.35))
    s["hit"] = seq(noise_burst(0.12, 0.6, 0.05), sfx_tone([180, 90], 0.1, "square", vol=0.3))
    s["hit_super"] = seq(noise_burst(0.2, 0.8, 0.08), sfx_tone([260, 60], 0.2, "square", vol=0.45))
    s["hit_weak"] = seq(noise_burst(0.06, 0.4, 0.02), sfx_tone([400, 300], 0.06, "square", duty=0.125, vol=0.2))
    s["faint"] = sfx_tone(np.linspace(600, 80, 50), 0.8, "square", duty=0.25, vol=0.4)
    s["throw"] = seq(noise_burst(0.25, 0.3, 0.12), sfx_tone([300, 900], 0.15, "sine", vol=0.3))
    s["shake"] = seq(noise_burst(0.05, 0.4, 0.015), np.zeros(int(0.05 * SR)), noise_burst(0.05, 0.4, 0.015))
    s["catch"] = arpeggio(["C6", "E6", "G6", "C7"], 0.08, duty=0.25, last=0.4)
    s["run"] = seq(*[noise_burst(0.04, 0.3, 0.01) for _ in range(5)], gap=0.04)
    s["level_up"] = arpeggio(["C5", "E5", "G5", "C6", "E6", "G6"], 0.06, duty=0.125, last=0.35)
    s["heal"] = seq(arpeggio(["G5", "C6", "E6"], 0.18, voice="sine", vol=0.4, last=0.25), arpeggio(["D6", "G6"], 0.18, "sine", vol=0.4, last=0.9))
    s["send_out"] = seq(sfx_tone([200, 900], 0.1, "sine", vol=0.4), arpeggio(["E6", "B6"], 0.05, duty=0.125, vol=0.25, last=0.15))
    s["grass"] = noise_burst(0.12, 0.25, 0.03)
    s["item"] = arpeggio(["G5", "B5", "D6", "G6"], 0.07, duty=0.25, last=0.35)
    s["save"] = arpeggio(["E6", "A6"], 0.1, voice="sine", vol=0.4, last=0.4)
    s["exclaim"] = arpeggio(["A6", "A6"], 0.06, duty=0.25, vol=0.4, last=0.08)
    s["badge"] = seq(arpeggio(["C5", "E5", "G5", "C6"], 0.12, duty=0.25, last=0.2), arpeggio(["D6", "E6", "G6", "C7"], 0.12, duty=0.25, last=0.9))
    s["money"] = seq(sfx_tone([1976, 1976], 0.06, duty=0.25, vol=0.35), sfx_tone([2637, 2637], 0.25, duty=0.25, decay=0.08, vol=0.35))
    return s


def main():
    only = set(sys.argv[1:])
    rows = []
    for name, fn in SONGS.items():
        if only and name not in only:
            continue
        data = fn()
        write(os.path.join(OUT, "music", name), data)
        seam = float(np.max(np.abs(data[0] - data[-1])))
        rows.append((f"music/{name}", len(data) / SR, float(np.max(np.abs(data))), float(np.sqrt(np.mean(data ** 2))), seam))
    for name, data in make_sfx().items():
        if only and name not in only:
            continue
        data = data / max(1e-6, np.max(np.abs(data))) * 0.8
        data = np.concatenate([np.zeros(int(0.005 * SR)), data, np.zeros(int(0.02 * SR))]).astype(np.float32)
        write(os.path.join(OUT, "sfx", name), data)
        rows.append((f"sfx/{name}", len(data) / SR, float(np.max(np.abs(data))), float(np.sqrt(np.mean(data ** 2))), 0.0))
    print(f"{'file':22s} {'secs':>6s} {'peak':>6s} {'rms':>6s} {'seam':>6s}")
    for r in rows:
        print(f"{r[0]:22s} {r[1]:6.1f} {r[2]:6.2f} {r[3]:6.3f} {r[4]:6.3f}")


if __name__ == "__main__":
    main()
