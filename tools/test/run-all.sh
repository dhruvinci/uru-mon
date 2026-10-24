#!/usr/bin/env bash
# Runs every browser test one after another (they drive real key presses, so never in parallel) and prints a summary.
# Needs the dev server on :8080. Usage: tools/test/run-all.sh [shots_dir]
set -u
cd "$(dirname "$0")/.."
SHOTS="${1:-/tmp/uru-shots}"
mkdir -p "$SHOTS"
MAPS=$(python3 -c "import json;print(','.join(m['id'] for m in json.load(open('../assets/maps/index.json'))))")
TESTS=(
  "world-smoke.mjs $SHOTS $MAPS"
  "battle-smoke.mjs $SHOTS"
  "newgame.mjs $SHOTS"
  "trainer-sight.mjs $SHOTS"
  "services.mjs $SHOTS"
  "systems.mjs $SHOTS catch"
  "systems.mjs $SHOTS evolve"
  "progression.mjs $SHOTS leader"
  "progression.mjs $SHOTS metro"
  "progression.mjs $SHOTS blackout"
  "frontdoor.mjs $SHOTS"
  "expansion.mjs $SHOTS"
  "mobile.mjs $SHOTS landscape"
  "mobile.mjs $SHOTS portrait"
  "mobile.mjs $SHOTS iphone"
  "mobile.mjs $SHOTS turn"
  "story.mjs $SHOTS cubbon"
  "story.mjs $SHOTS rival2"
  "story.mjs $SHOTS rival2lose"
  "story.mjs $SHOTS rival3"
  "story.mjs $SHOTS bellandur"
  "story.mjs $SHOTS rival4"
  "story.mjs $SHOTS nandi"
  "story.mjs $SHOTS council"
)
fail=0
for t in "${TESTS[@]}"; do
  out=$(timeout 1500 node test/$t 2>&1 | grep -v "GL Driver")
  # a test passes when it reports no page errors and none of its checks printed "false"
  # ("still blocking: false" is the one check where false is the good answer)
  if echo "$out" | grep -q "^no errors" && ! echo "$out" | grep -v "still blocking" | grep -qE ": false|ERRORS"; then
    echo "PASS  $t" | cut -c1-90
  else
    echo "FAIL  $t" | cut -c1-90
    echo "$out" | tail -8 | sed 's/^/      /'
    fail=$((fail + 1))
  fi
done
echo "$fail failing"
exit $fail
