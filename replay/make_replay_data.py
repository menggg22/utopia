"""
Generate replay_data.json from run directories.

Usage:
    python make_replay_data.py runs/v3_*              # specific runs
    python make_replay_data.py runs/                   # all runs in directory
"""

import json
import os
import sys
import glob


def load_events(run_dir):
    """Load events from a run's events.jsonl."""
    events_path = os.path.join(run_dir, "events.jsonl")
    if not os.path.exists(events_path):
        return None
    events = []
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if line:
                ev = json.loads(line)
                # Strip bulky fields to keep data size reasonable
                if ev.get("data", {}).get("raw_llm_response"):
                    del ev["data"]["raw_llm_response"]
                events.append(ev)
    return events


def find_run_dirs(paths):
    """Find all valid run directories from paths (files, dirs, globs)."""
    dirs = []
    for path in paths:
        if os.path.isdir(path):
            # Check if this IS a run dir (has events.jsonl)
            if os.path.exists(os.path.join(path, "events.jsonl")):
                dirs.append(path)
            else:
                # It's a parent dir — find run dirs inside
                for entry in sorted(os.listdir(path)):
                    sub = os.path.join(path, entry)
                    if os.path.isdir(sub) and os.path.exists(os.path.join(sub, "events.jsonl")):
                        dirs.append(sub)
        else:
            # Try glob
            for match in sorted(glob.glob(path)):
                if os.path.isdir(match) and os.path.exists(os.path.join(match, "events.jsonl")):
                    dirs.append(match)
    return dirs


NICE_NAMES = {
    "baseline": "Brook Farm",
    "run": "Brook Farm",
    "no_hawthorne": "No Nathaniel",
    "no_sophia": "No Sophia",
    "no_ripley": "No George",
    "double_food": "Double Food",
}

NICE_DESCS = {
    "baseline": "All 5 members. Will the community survive?",
    "run": "All 5 members. The original experiment.",
    "no_hawthorne": "Remove the skeptic. Does the commune thrive without his doubt?",
    "no_sophia": "Remove the backbone. What holds idealists together when the practical one is gone?",
    "no_ripley": "Remove the founder. Can vision be replaced?",
    "double_food": "Start with 200 food. Does abundance save them?",
}


def run_label(run_dir):
    """Extract a human-readable label from run directory name."""
    name = os.path.basename(run_dir)
    config_path = os.path.join(run_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        # v3 config uses "name"/"seed"; v1/v2 config uses directory name prefix
        dir_prefix = name.split("_20")[0]  # e.g. "run" from "run_20260401_235509"
        exp_name = config.get("name", dir_prefix)
        seed = config.get("seed", config.get("random_seed", "?"))
        nice = NICE_NAMES.get(exp_name, exp_name)
        # Only add seed qualifier if there are multiple baselines
        if exp_name in ("baseline", "run"):
            return f"{nice} #{seed}"
        return nice
    return name


SUMMARIES = {
    "run_0": "Nobody left. All five stayed to the end — and the commune still died. George believed the hardest and broke first. Hawthorne and Sophia found something worth staying for. The skeptic and the teacher outlasted the founder. The commune became a shell. Its dreamer disappeared inside it.",

    "run_42": "Hawthorne walked out with his eyes open. Not in despair — in clarity. By then George had already hollowed out. The three who stayed made it to the end with money in the bank and nothing left to say to each other.",

    "no_hawthorne": "Without the skeptic, no one told the truth. The commune held together quietly — no confrontations, no reckonings. George still broke. The silence felt comfortable. It was also lethal.",

    "no_ripley": "Sophia became the leader no one asked for. The school ran. The money held. But John, who needed a believer to follow, had no one. Hawthorne left when there was no longer anyone worth arguing with. Competence kept the lights on. It couldn't replace the dream.",

    "no_sophia": "Remove the practical one and watch the honest ones emerge. Hawthorne found his purpose. Dana found his voice. Both left not in despair but in clarity — having said everything they needed to say. The commune starved. The skeptic left happy.",

    "double_food": "More food. Same people. Same ending.",
}

def run_summary(run_dir, exp_name, seed):
    """Get narrative summary for a run."""
    key = None
    if exp_name in ("baseline", "run"):
        key = f"run_{seed}"
    else:
        key = exp_name
    return SUMMARIES.get(key, "")

SEED_UNIVERSE = {
    0:  "Universe #0 — the original timeline.",
    2:  "Universe #2 — a quieter spring, a different fate.",
    42: "Universe #42 — what if history rolled a different seed?",
}

def run_desc(run_dir):
    """Get a description for the run."""
    config_path = os.path.join(run_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        dir_prefix = os.path.basename(run_dir).split("_20")[0]
        exp_name = config.get("name", dir_prefix)
        seed = config.get("seed", config.get("random_seed", None))
        # For baselines, make it fun with parallel universe flavor
        if exp_name in ("baseline", "run") and seed is not None:
            universe = SEED_UNIVERSE.get(seed, f"Universe #{seed} — a road not taken.")
            return universe
        return NICE_DESCS.get(exp_name, "")
    return ""


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_replay_data.py <run_dir or parent_dir> [...]")
        sys.exit(1)

    run_dirs = find_run_dirs(sys.argv[1:])
    if not run_dirs:
        print("No valid run directories found.")
        sys.exit(1)

    print(f"Loading {len(run_dirs)} run(s)...")
    all_runs = {}
    meta = {}
    for run_dir in run_dirs:
        label = run_label(run_dir)
        events = load_events(run_dir)
        if events:
            all_runs[label] = events
            desc = run_desc(run_dir)
            lk = label.lower()
            tag = "counterfactual" if ("no " in lk or "double" in lk) else "baseline"
            # Extract exp_name and seed for summary lookup
            config_path = os.path.join(run_dir, "config.json")
            exp_name, seed = None, None
            if os.path.exists(config_path):
                with open(config_path) as cf:
                    cfg = json.load(cf)
                dir_prefix = os.path.basename(run_dir).split("_20")[0]
                exp_name = cfg.get("name", dir_prefix)
                seed = cfg.get("seed", cfg.get("random_seed", None))
            summary = run_summary(run_dir, exp_name, seed)
            meta[label] = {"name": label, "desc": desc, "tag": tag, "summary": summary}
            print(f"  {label}: {len(events)} events")

    output = {"meta": meta, "runs": all_runs}
    out_path = os.path.join(os.path.dirname(__file__), "replay_data.json")
    with open(out_path, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nWrote {out_path} ({size_mb:.1f} MB, {len(all_runs)} runs)")


if __name__ == "__main__":
    main()
