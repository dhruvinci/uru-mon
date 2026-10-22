# Task: bug review (read-only)

Review uru-mon's core gameplay code for real bugs: softlocks (the player gets stuck with no way to continue),
crashes, incorrect battle maths, state that isn't saved/restored correctly, promise flows that never resolve, input
that leaks between scenes, and edge cases (party full, out of PP, all fainted, catching the last Urumon in a trainer
battle, evolving mid-battle, learning a move with 4 known, blackout during a scripted battle, warping during dialog).

Files, in priority order:
`src/scenes/battle-scene.js`, `src/battle/engine/battle-engine.js`, `src/battle/engine/monster.js`,
`src/scenes/world-scene.js`, `src/world/script-runner.js`, `src/world/characters/{character,player,npc}.js`,
`src/scenes/{monster-party-scene,inventory-scene,dialog-scene}.js`, `src/utils/data-manager.js`,
`src/input/input-manager.js`, `src/utils/controls.js`. Read `CLAUDE.md` and `docs/DESIGN.md` first for context.

Rules:
- Do NOT modify any file except creating `art-src/logs/review.md`.
- In that file list each finding as: severity (high/medium/low), file:line, what goes wrong, a concrete scenario that
  triggers it, and a suggested fix. Only include issues you are confident are real after reading the code paths
  involved; skip style nits. If you can verify an engine issue with a quick `node` script against
  `src/battle/engine/*`, do so and say so.
