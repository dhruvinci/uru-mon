# Task: original chiptune soundtrack and sound effects

uru-mon is a GBA-style creature RPG set in Bengaluru (read `docs/DESIGN.md`). Build a small synthesizer and compose an
**original** soundtrack and SFX set entirely in code. No samples, no downloaded audio, nothing derived from existing
songs or games.

## Deliverable
`tools/audio/synth.py` (Python 3 + numpy only; use the `ffmpeg` binary for encoding) that renders every file below to
`assets/audio/music/<name>.ogg` + `.mp3` and `assets/audio/sfx/<name>.ogg` + `.mp3`
(Vorbis ~q4 and MP3 ~128k, 44.1 kHz; music may be mono or stereo; SFX mono). Running
`python3 tools/audio/synth.py` regenerates everything deterministically.

## Sound engine
- GBA-like channels: two pulse/square voices (duty 12.5/25/50%), a triangle or soft wave bass, a noise channel for
  drums, plus an optional soft "sitar-ish" plucked voice (Karplus-Strong or a decaying bright saw) for local colour.
- Simple ADSR envelopes, vibrato on long notes, light stereo spread/echo is fine. Avoid harsh aliasing (band-limit
  or oversample + lowpass). Normalise to about -14 LUFS / peaks under -1 dBFS. No clicks at note boundaries.
- Author songs in a compact text/tracker notation inside the file (e.g. per-channel note strings, patterns, BPM).

## Music (each must loop seamlessly: render the loop body so end flows into start; 30–90 s each)
Musical flavour: catchy GBA-RPG melodies with South Indian colour — use ragas/scales like Mohanam (major pentatonic),
Kalyani (Lydian), Shankarabharanam (major), Mayamalavagowla (S R1 G3 M1 P D1 N3), Hindolam; gamaka-like slides and
trills on lead notes; occasional Rupaka (3/4) or Khanda (5) feel; tabla-like drum patterns on the noise channel.

| file | mood |
|---|---|
| title | grand, hopeful opening theme; the game's main motif |
| home | gentle, warm morning at home |
| town | cheerful neighbourhood stroll (Basavanagudi/Lalbagh) |
| city | busy, bright, horn-like stabs, bustling (MG Road) |
| route | adventurous walking theme, main motif variation |
| park | leafy, light, birdsong-like trills |
| cave | mysterious, sparse, echoey |
| lab | curious, bubbly, scientific |
| darshini | short cosy loop, homely (used for healing places and shops) |
| arena | tense build-up inside a gym |
| syndicate | sneaky villain theme, minor, mechanical |
| rival | cocky upbeat theme for Rohan |
| wild | fast wild-battle theme (the one players hear most — make it great) |
| trainer | trainer battle, driving |
| leader | Arena Leader battle, epic |
| legend | legendary encounter, majestic and eerie |
| victory | short victory fanfare then a loopable cool-down (~20 s) |
| evolution | shimmering, rising |
| council | Namma Council / final battles, intense |
| credits | warm, celebratory reprise of the main motif (60–90 s, may not loop) |

## SFX (short, punchy, 0.05–1.2 s)
select, bump, door, hit, hit_super (bigger), hit_weak (thin), faint (falling pitch), throw (whoosh), shake (rattle),
catch (bright jingle), run (scurry), level_up (rising arpeggio), heal (soothing 2-second jingle), send_out (pop + sparkle),
grass (soft rustle), item (pickup jingle), save (confirm chime), exclaim (alert "!" blip), badge (triumphant jingle ~2 s),
money (coin clink)

## Rules
- Only create `tools/audio/synth.py` and the files in `assets/audio/`. Do not modify anything else. Do not install packages.
- After rendering, analyse your own output (peak/RMS per file, durations, check loops have no discontinuity at the
  seam) and print a summary table. Fix anything clipping or silent.
