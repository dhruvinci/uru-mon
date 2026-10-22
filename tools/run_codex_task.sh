#!/usr/bin/env bash
# Runs a Codex CLI task described by a markdown spec. Usage: tools/run_codex_task.sh docs/tasks/<name>.md
set -u
spec="$1"
name="$(basename "$spec" .md)"
cd "$(dirname "$0")/.."
codex exec -s workspace-write --ephemeral -C "$PWD" \
  "Read ${spec} and implement it completely and carefully. It is a self-contained task inside the uru-mon repo. \
Follow its rules exactly: only create/modify the files it names. Do not run git commands that change state (no commit, \
checkout, reset, stash). Do not install packages. You are not working with a human in the loop: make reasonable \
decisions yourself, do not ask questions, and do not stop to brainstorm or plan with the user. When finished, reply \
with a short summary of what you built and anything incomplete." < /dev/null > "art-src/logs/codex_${name}.log" 2>&1
echo "codex task ${name} exited with $?"
