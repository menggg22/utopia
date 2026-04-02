"""
Compare results across multiple simulation runs.

Usage:
    python compare.py runs/baseline_*           # compare all baseline runs
    python compare.py runs/baseline_* runs/no_hawthorne_*  # cross-experiment
    python compare.py runs/                     # all runs in directory
"""

import sys
import os
import json
import glob
from collections import Counter


def load_run(run_dir: str) -> dict:
    """Load events and config from a run directory."""
    events_path = os.path.join(run_dir, "events.jsonl")
    config_path = os.path.join(run_dir, "config.json")

    events = []
    if os.path.exists(events_path):
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)

    return {"dir": run_dir, "config": config, "events": events}


def analyze_run(run: dict) -> dict:
    """Extract key metrics from a run."""
    events = run["events"]
    config = run["config"]

    if not events:
        return {"name": config.get("name", "?"), "error": "no events"}

    # Basic info
    sim_end = next((e for e in events if e["type"] == "sim_end"), None)
    final_state = sim_end["data"]["final_state"] if sim_end else {}

    # Departures
    departures = []
    for e in events:
        if e["type"] == "agent_departed":
            departures.append({"agent": e["agent"], "round": e["round"], "date": e.get("date", "?")})

    # Action counts per agent
    action_counts = {}
    for e in events:
        if e["type"] == "action":
            name = e["agent"]
            raw = e["data"].get("chosen_action", "?") or "?"
            action = raw.split()[0].upper() if raw else "?"
            if name not in action_counts:
                action_counts[name] = Counter()
            action_counts[name][action] += 1

    # Satisfaction trajectories (from reflections)
    satisfaction = {}
    for e in events:
        if e["type"] == "reflection":
            name = e["agent"]
            if name not in satisfaction:
                satisfaction[name] = []
            satisfaction[name].append(e["data"].get("satisfaction", "?"))

    # Morale trajectory
    morale = []
    for e in events:
        if e["type"] == "env_state":
            morale.append(e["data"].get("morale", "?"))

    # Food trajectory
    food = []
    for e in events:
        if e["type"] == "env_state":
            food.append(e["data"].get("food", "?"))

    # Key moments
    key_moments = []
    for e in events:
        if e["type"] == "key_moment":
            key_moments.append({
                "agent": e["agent"], "round": e["round"],
                "description": e["data"].get("description", ""),
                "emotion": e["data"].get("emotion", ""),
            })

    # Votes
    votes = []
    for e in events:
        if e["type"] == "vote_result":
            votes.append({
                "round": e["round"],
                "proposal": e["data"].get("proposal", ""),
                "result": e["data"].get("result", ""),
            })

    rounds_completed = sim_end["data"].get("rounds_completed", 0) if sim_end else 0

    return {
        "name": config.get("name", "?"),
        "seed": config.get("seed", "?"),
        "dir": run["dir"],
        "rounds": rounds_completed,
        "agents": config.get("agents", []),
        "final_food": final_state.get("food", "?"),
        "final_money": final_state.get("money", "?"),
        "final_morale": final_state.get("morale", "?"),
        "departures": departures,
        "action_counts": action_counts,
        "satisfaction": satisfaction,
        "morale_trajectory": morale,
        "food_trajectory": food,
        "key_moments": key_moments,
        "votes": votes,
        "total_events": sim_end["data"].get("total_events", 0) if sim_end else 0,
        "llm_calls": sim_end["data"].get("total_llm_calls", 0) if sim_end else 0,
        "wall_time": sim_end["data"].get("wall_time_seconds", 0) if sim_end else 0,
    }


def print_comparison(analyses: list):
    """Print a comparison table across runs."""

    print(f"\n{'='*70}")
    print(f"  COMPARISON — {len(analyses)} runs")
    print(f"{'='*70}")

    # Overview table
    print(f"\n  {'Name':<16} {'Seed':<6} {'Rnds':<5} {'Food':<5} {'$':<6} {'Mor%':<5} {'Departed'}")
    print(f"  {'-'*16} {'-'*5} {'-'*4} {'-'*4} {'-'*5} {'-'*4} {'-'*30}")
    for a in analyses:
        departed_str = ", ".join(f"{d['agent'].split()[-1]} R{d['round']}" for d in a["departures"]) or "None"
        print(f"  {a['name']:<16} {a['seed']:<6} {a['rounds']:<5} {a['final_food']:<5} {a['final_money']:<6} {a['final_morale']:<5} {departed_str}")

    # Departure analysis
    print(f"\n  --- Departures ---")
    all_agents = set()
    for a in analyses:
        for d in a["departures"]:
            all_agents.add(d["agent"])

    if all_agents:
        for agent in sorted(all_agents):
            rounds = []
            for a in analyses:
                dep = next((d for d in a["departures"] if d["agent"] == agent), None)
                if dep:
                    rounds.append(f"R{dep['round']} ({a['name']} s{a['seed']})")
                else:
                    rounds.append(f"stayed ({a['name']} s{a['seed']})")
            print(f"  {agent}:")
            for r in rounds:
                print(f"    {r}")
    else:
        print("  No departures in any run.")

    # Action distribution comparison
    print(f"\n  --- Action Distribution (top actions per agent) ---")
    all_agent_names = set()
    for a in analyses:
        all_agent_names.update(a["action_counts"].keys())

    for agent in sorted(all_agent_names):
        print(f"\n  {agent}:")
        for a in analyses:
            counts = a["action_counts"].get(agent, Counter())
            top = counts.most_common(4)
            top_str = ", ".join(f"{act}:{n}" for act, n in top)
            print(f"    {a['name']} s{a['seed']}: {top_str}")

    # Satisfaction final values
    print(f"\n  --- Final Satisfaction ---")
    for agent in sorted(all_agent_names):
        vals = []
        for a in analyses:
            traj = a["satisfaction"].get(agent, [])
            final = traj[-1] if traj else "?"
            vals.append(f"{final} ({a['name']} s{a['seed']})")
        print(f"  {agent}: {', '.join(vals)}")

    # Food collapse timing
    print(f"\n  --- Food First Hits Zero ---")
    for a in analyses:
        first_zero = None
        for i, f in enumerate(a["food_trajectory"]):
            if isinstance(f, int) and f <= 0:
                first_zero = i + 1
                break
        if first_zero:
            print(f"  {a['name']} s{a['seed']}: Round {first_zero}")
        else:
            print(f"  {a['name']} s{a['seed']}: Never")

    # Key moment counts
    print(f"\n  --- Key Moments ---")
    for a in analyses:
        n = len(a["key_moments"])
        print(f"  {a['name']} s{a['seed']}: {n} moments in {a['rounds']} rounds ({n/max(a['rounds'],1):.1f}/round)")

    print(f"\n{'='*70}\n")


def save_comparison(analyses: list, out_path: str):
    """Save comparison as markdown."""
    with open(out_path, "w") as f:
        f.write("# Run Comparison\n\n")

        f.write("## Overview\n\n")
        f.write(f"| Name | Seed | Rounds | Food | Money | Morale | Departed |\n")
        f.write(f"|------|------|--------|------|-------|--------|----------|\n")
        for a in analyses:
            departed_str = ", ".join(f"{d['agent'].split()[-1]} R{d['round']}" for d in a["departures"]) or "None"
            f.write(f"| {a['name']} | {a['seed']} | {a['rounds']} | {a['final_food']} | ${a['final_money']} | {a['final_morale']}% | {departed_str} |\n")

        f.write("\n## Departures\n\n")
        all_agents = set()
        for a in analyses:
            for d in a["departures"]:
                all_agents.add(d["agent"])
        for agent in sorted(all_agents):
            f.write(f"**{agent}**:\n")
            for a in analyses:
                dep = next((d for d in a["departures"] if d["agent"] == agent), None)
                if dep:
                    f.write(f"- {a['name']} (seed {a['seed']}): Left round {dep['round']} ({dep['date']})\n")
                else:
                    f.write(f"- {a['name']} (seed {a['seed']}): Stayed\n")
            f.write("\n")

        f.write("## Final Satisfaction\n\n")
        all_agent_names = set()
        for a in analyses:
            all_agent_names.update(a["satisfaction"].keys())
        for agent in sorted(all_agent_names):
            vals = []
            for a in analyses:
                traj = a["satisfaction"].get(agent, [])
                final = traj[-1] if traj else "?"
                vals.append(f"{final} ({a['name']} s{a['seed']})")
            f.write(f"- **{agent}**: {', '.join(vals)}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compare.py <run_dir> [run_dir2 ...] [--save comparison.md]")
        sys.exit(1)

    save_path = None
    args = []
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--save" and i + 2 < len(sys.argv):
            save_path = sys.argv[i + 2]
        elif sys.argv[i] != "--save":  # skip the value after --save
            args.append(arg)

    # Collect run directories
    run_dirs = []
    for arg in args:
        if os.path.isdir(arg) and os.path.exists(os.path.join(arg, "events.jsonl")):
            run_dirs.append(arg)
        elif os.path.isdir(arg):
            # Directory of runs
            for d in sorted(os.listdir(arg)):
                full = os.path.join(arg, d)
                if os.path.isdir(full) and os.path.exists(os.path.join(full, "events.jsonl")):
                    run_dirs.append(full)
        else:
            # Try glob
            for d in sorted(glob.glob(arg)):
                if os.path.isdir(d) and os.path.exists(os.path.join(d, "events.jsonl")):
                    run_dirs.append(d)

    if not run_dirs:
        print("No valid run directories found.")
        sys.exit(1)

    print(f"Loading {len(run_dirs)} run(s)...")
    runs = [load_run(d) for d in run_dirs]
    analyses = [analyze_run(r) for r in runs]

    # Filter out runs with no events
    analyses = [a for a in analyses if "error" not in a]

    print_comparison(analyses)

    if save_path:
        save_comparison(analyses, save_path)
        print(f"Saved to {save_path}")
