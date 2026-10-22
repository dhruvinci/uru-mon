"""Batch image generation through Codex CLI's built-in image tool (uses the local ChatGPT login).

Usage: python3 tools/art/gen_images.py <jobs.json> <out_dir> [--batch 4] [--parallel 3]

jobs.json is a list of {"file": "name.png", "prompt": "..."}. Existing files are skipped,
so the script can be re-run to retry failures.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

INSTRUCTIONS = (
    "Use your image generation tool to create the images listed below: exactly one separate image per item, "
    "each saved as a PNG to the exact filename given, in the current directory. Do not create, modify or delete "
    "any other files. Do not ask questions. Do not write code to draw the images; use the image generation tool. "
    "When done, reply with only the list of saved filenames.\n\n"
)


def run_batch(batch, out_dir, log_dir, idx):
    prompt = INSTRUCTIONS + "\n\n".join(f"### {j['file']}\n{j['prompt']}" for j in batch)
    log = os.path.join(log_dir, f"batch_{idx:03d}_{int(time.time())}.log")
    with open(log, "w") as fh:
        try:
            subprocess.run(
                ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-C", out_dir, "-s", "workspace-write", prompt],
                stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, timeout=900, check=False,
            )
        except subprocess.TimeoutExpired:
            fh.write("\nTIMEOUT\n")
    done = [j["file"] for j in batch if os.path.exists(os.path.join(out_dir, j["file"]))]
    print(f"batch {idx}: {len(done)}/{len(batch)} saved -> {', '.join(done)}", flush=True)
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("out_dir")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=3)
    args = ap.parse_args()

    jobs = json.load(open(args.jobs))
    out_dir = os.path.abspath(args.out_dir)
    log_dir = os.path.join(out_dir, "_logs")
    os.makedirs(log_dir, exist_ok=True)

    for rnd in range(args.rounds):
        todo = [j for j in jobs if not os.path.exists(os.path.join(out_dir, j["file"]))]
        if not todo:
            break
        print(f"round {rnd + 1}: {len(todo)} images to generate", flush=True)
        batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            list(pool.map(lambda p: run_batch(p[1], out_dir, log_dir, p[0]), enumerate(batches)))

    missing = [j["file"] for j in jobs if not os.path.exists(os.path.join(out_dir, j["file"]))]
    print(f"finished; missing: {missing}", flush=True)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
