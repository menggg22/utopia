"""
Experiment runner (v3) — run one or many v3 simulation configs sequentially.

Usage:
    python experiment_v3.py experiments/v3/baseline_seed0.json           # run one
    python experiment_v3.py experiments/v3/baseline_seed*.json           # run several
    python experiment_v3.py experiments/v3/                              # run all in dir
"""

import sys
import os
import json
import glob
import time
from simulate_v3 import run_simulation
from derive import derive_all


def load_configs(path: str) -> list:
    """Load config(s) from a file or directory."""
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "*.json")))
    elif os.path.isfile(path):
        files = [path]
    else:
        # Try glob pattern
        files = sorted(glob.glob(path))

    configs = []
    for f in files:
        with open(f) as fh:
            config = json.load(fh)
            config["_config_file"] = f
            configs.append(config)
    return configs


def run_experiment(configs: list):
    """Run all configs sequentially, derive outputs, print summary."""
    results = []
    total_start = time.time()

    print(f"\n{'='*60}")
    print(f"  EXPERIMENT BATCH — {len(configs)} run(s)")
    for i, c in enumerate(configs):
        print(f"  {i+1}. {c.get('name', '?')} (seed={c.get('seed', '?')}) — {c.get('_config_file', '?')}")
    print(f"{'='*60}\n")

    for i, config in enumerate(configs):
        print(f"\n{'#'*60}")
        print(f"  Run {i+1}/{len(configs)}: {config.get('name', '?')} (seed={config.get('seed', '?')})")
        print(f"{'#'*60}")

        result = run_simulation(config)
        run_dir = result["run_dir"]

        # Derive outputs
        events_path = os.path.join(run_dir, "events.jsonl")
        if os.path.exists(events_path):
            print(f"\n  Deriving outputs...")
            derive_all(events_path)

        results.append({
            "config": config.get("name", "?"),
            "seed": config.get("seed", "?"),
            "run_dir": run_dir,
            **result,
        })

    total_time = time.time() - total_start

    # Print summary table
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT COMPLETE — {len(results)} run(s) in {total_time:.0f}s")
    print(f"{'='*60}")
    print(f"\n  {'Name':<20} {'Seed':<6} {'Events':<8} {'LLM':<6} {'Dir'}")
    print(f"  {'-'*20} {'-'*5} {'-'*7} {'-'*5} {'-'*30}")
    for r in results:
        print(f"  {r['config']:<20} {r['seed']:<6} {r['events']:<8} {r['llm_calls']:<6} {r['run_dir']}")

    # Save batch summary
    summary_path = os.path.join("runs", f"batch_{int(time.time())}.json")
    with open(summary_path, "w") as f:
        json.dump({
            "total_time_seconds": round(total_time, 1),
            "runs": results,
        }, f, indent=2)
    print(f"\n  Batch summary: {summary_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run v3 experiment batch")
    parser.add_argument("paths", nargs="+", help="Config files or directories")
    parser.add_argument("--backend", choices=["cli", "api"], default="cli",
                        help="LLM backend: 'cli' (claude CLI) or 'api' (Anthropic API)")
    args = parser.parse_args()

    configs = []
    for path in args.paths:
        configs.extend(load_configs(path))

    if not configs:
        print("No config files found.")
        sys.exit(1)

    # Inject backend into each config
    for c in configs:
        c.setdefault("backend", args.backend)

    run_experiment(configs)
