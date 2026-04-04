"""Generate figures for v2 analysis."""
import csv
import json
import os
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("pip install matplotlib numpy")
    sys.exit(1)

FIGS_DIR = "figures/v2"
os.makedirs(FIGS_DIR, exist_ok=True)

# --- Run directories ---
V1_RUNS = {
    "v1_original": "runs/run_20260401_235509",
    "v1_baseline": "runs/baseline_20260402_085324",
}

V2_RUNS = {
    "v2_s0": "runs/v2_baseline_20260402_230405",
    "v2_s1": "runs/v2_baseline_20260403_004934",
    "v2_s2": "runs/v2_baseline_20260403_021642",
    "v2_s3": "runs/v2_baseline_20260403_040227",
    "v2_s4": "runs/v2_baseline_20260403_055621",
    "v2_double": "runs/v2_double_food_20260403_072904",
    "v2_no_haw": "runs/v2_no_hawthorne_20260403_085921",
    "v2_no_rip": "runs/v2_no_ripley_20260403_102321",
    "v2_no_sop": "runs/v2_no_sophia_20260403_113949",
}

PALETTE = {
    "v1_original": "#2d2d2d",
    "v1_baseline": "#888888",
    "v2_s0": "#D94032",
    "v2_s1": "#E8634A",
    "v2_s2": "#F08C6E",
    "v2_s3": "#F4A68C",
    "v2_s4": "#F8C0AA",
    "v2_double": "#2D5BDA",
    "v2_no_haw": "#4CAF50",
    "v2_no_rip": "#FF9800",
    "v2_no_sop": "#9C27B0",
}

LABELS = {
    "v1_original": "v1 Original (s42)",
    "v1_baseline": "v1 Baseline (s0)",
    "v2_s0": "v2 Seed 0",
    "v2_s1": "v2 Seed 1",
    "v2_s2": "v2 Seed 2",
    "v2_s3": "v2 Seed 3",
    "v2_s4": "v2 Seed 4",
    "v2_double": "v2 Double Food",
    "v2_no_haw": "v2 No Hawthorne",
    "v2_no_rip": "v2 No Ripley",
    "v2_no_sop": "v2 No Sophia",
}


def load_metrics(run_dir):
    path = os.path.join(run_dir, "metrics.csv")
    rounds, food, money, morale = [], [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rounds.append(int(row["round"]))
            food.append(int(row["food"]))
            money.append(int(row["money"]))
            morale.append(int(row["morale"]))
    return rounds, food, money, morale


def load_actions_from_events(run_dir):
    """Parse action counts per agent from events.jsonl."""
    path = os.path.join(run_dir, "events.jsonl")
    agent_actions = {}
    with open(path) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get("type") == "action" and ev.get("agent"):
                agent = ev["agent"]
                raw = ev.get("data", {}).get("chosen_action", "REST")
                act = raw.split()[0].upper() if raw.strip() else "REST"
                if agent not in agent_actions:
                    agent_actions[agent] = {}
                agent_actions[agent][act] = agent_actions[agent].get(act, 0) + 1
    return agent_actions


def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2, linewidth=0.5)


# --- Figure 1: v1 vs v2 morale trajectories ---
def fig_morale_v1_v2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    # Left: v1 runs
    for name, run_dir in V1_RUNS.items():
        r, f, m, morale = load_metrics(run_dir)
        ax1.plot(r, morale, '-', color=PALETTE[name], label=LABELS[name], linewidth=2)
    ax1.set_title("v1: Morale Collapse", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Community Morale (%)")
    ax1.set_ylim(-5, 105)
    ax1.axhline(y=0, color='red', linewidth=0.5, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=9)
    style_ax(ax1)

    # Right: v2 baseline seeds
    for name in ["v2_s0", "v2_s1", "v2_s2", "v2_s3", "v2_s4"]:
        r, f, m, morale = load_metrics(V2_RUNS[name])
        ax2.plot(r, morale, '-', color=PALETTE[name], label=LABELS[name], linewidth=1.5, alpha=0.8)
    ax2.set_title("v2: Golden Period, Same Endpoint", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Round")
    ax2.set_ylim(-5, 105)
    ax2.axhline(y=0, color='red', linewidth=0.5, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9)
    style_ax(ax2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "morale_v1_v2.png"), dpi=150)
    plt.close()
    print("  morale_v1_v2.png")


# --- Figure 2: v2 counterfactuals morale ---
def fig_morale_counterfactuals():
    fig, ax = plt.subplots(figsize=(10, 5))

    for name in ["v2_s0", "v2_double", "v2_no_haw", "v2_no_rip", "v2_no_sop"]:
        r, f, m, morale = load_metrics(V2_RUNS[name])
        lw = 2.5 if name in ("v2_s0", "v2_no_rip") else 1.5
        ax.plot(r, morale, '-', color=PALETTE[name], label=LABELS[name], linewidth=lw)

    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Community Morale (%)", fontsize=12)
    ax.set_title("Counterfactuals: Who Matters Most?", fontsize=14, fontweight='bold')
    ax.set_ylim(-5, 105)
    ax.axhline(y=0, color='red', linewidth=0.5, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    style_ax(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "morale_counterfactuals.png"), dpi=150)
    plt.close()
    print("  morale_counterfactuals.png")


# --- Figure 3: Food trajectories v1 vs v2 ---
def fig_food_v1_v2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for name, run_dir in V1_RUNS.items():
        r, food, m, morale = load_metrics(run_dir)
        ax1.plot(r, food, '-', color=PALETTE[name], label=LABELS[name], linewidth=2)
    ax1.set_title("v1: Food Crashes to Zero", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Food")
    ax1.axhline(y=0, color='red', linewidth=0.5, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=9)
    style_ax(ax1)

    for name in ["v2_s0", "v2_s1", "v2_s2", "v2_s3", "v2_s4"]:
        r, food, m, morale = load_metrics(V2_RUNS[name])
        ax2.plot(r, food, '-', color=PALETTE[name], label=LABELS[name], linewidth=1.5, alpha=0.8)
    ax2.set_title("v2: Food Never Hits Zero", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Round")
    ax2.axhline(y=0, color='red', linewidth=0.5, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9)
    style_ax(ax2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "food_v1_v2.png"), dpi=150)
    plt.close()
    print("  food_v1_v2.png")


# --- Figure 4: Action distribution comparison ---
def fig_actions_comparison():
    # Aggregate actions across v2 baselines
    action_totals = {}
    for name in ["v2_s0", "v2_s1", "v2_s2", "v2_s3", "v2_s4"]:
        agent_acts = load_actions_from_events(V2_RUNS[name])
        for agent, acts in agent_acts.items():
            for act, count in acts.items():
                action_totals[act] = action_totals.get(act, 0) + count

    # Also get v1
    v1_totals = {}
    for name in V1_RUNS:
        agent_acts = load_actions_from_events(V1_RUNS[name])
        for agent, acts in agent_acts.items():
            for act, count in acts.items():
                v1_totals[act] = v1_totals.get(act, 0) + count

    # Normalize to per-run averages
    categories = ["SPEAK", "TEACH", "FARM", "WRITE", "TRADE", "ORGANIZE", "REPAIR", "REST"]
    v1_vals = [v1_totals.get(c, 0) / 2 for c in categories]  # 2 v1 runs
    v2_vals = [action_totals.get(c, 0) / 5 for c in categories]  # 5 v2 baselines

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width/2, v1_vals, width, label='v1 (avg)', color='#2d2d2d', alpha=0.7)
    bars2 = ax.bar(x + width/2, v2_vals, width, label='v2 (avg)', color='#D94032', alpha=0.7)

    ax.set_ylabel("Actions per Run (avg)", fontsize=12)
    ax.set_title("What Changed: v1 vs v2 Action Distribution", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.legend(fontsize=11)
    style_ax(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "actions_v1_v2.png"), dpi=150)
    plt.close()
    print("  actions_v1_v2.png")


# --- Figure 5: Departure timing ---
def fig_departures():
    departures = {
        "v1 Original (s42)": [("Hawthorne", 11), ("Dwight", 21)],
        "v2 Seed 1": [("Hawthorne", 9)],
        "v2 Seed 3": [("Dwight", 27)],
        "v2 Seed 4": [("Hawthorne", 7)],
        "v2 Double Food": [("Hawthorne", 10)],
        "v2 No Ripley": [("Hawthorne", 18), ("Sophia", 25)],
    }

    agent_colors = {
        "Hawthorne": "#2D5BDA",
        "Dwight": "#F2C12E",
        "Sophia": "#D94032",
    }

    fig, ax = plt.subplots(figsize=(10, 4))
    y_labels = list(departures.keys())

    for i, (run, deps) in enumerate(departures.items()):
        for name, rnd in deps:
            ax.scatter(rnd, i, s=120, color=agent_colors[name], zorder=5, edgecolors='white', linewidth=1)
            ax.annotate(name.split()[0], (rnd, i), textcoords="offset points",
                       xytext=(8, 0), fontsize=8, va='center')

    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=10)
    ax.set_xlabel("Round", fontsize=12)
    ax.set_title("When People Leave", fontsize=14, fontweight='bold')
    ax.set_xlim(0, 32)
    ax.axvline(x=11, color='#2d2d2d', linewidth=0.5, alpha=0.3, linestyle='--')
    ax.text(11.5, 5.3, "v1 Hawthorne\ndeparts", fontsize=8, color='#888', va='top')
    style_ax(ax)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "departures.png"), dpi=150)
    plt.close()
    print("  departures.png")


# --- Figure 6: Satisfaction heatmap ---
def fig_satisfaction():
    agents = ["George Ripley", "Nathaniel Hawthorne", "Sophia Ripley", "Charles Dana", "John Sullivan Dwight"]
    short = ["Ripley", "Hawthorne", "Sophia", "Dana", "Dwight"]
    runs = ["v2_s0", "v2_s1", "v2_s2", "v2_s3", "v2_s4", "v2_double", "v2_no_haw", "v2_no_rip", "v2_no_sop"]
    run_labels = ["s0", "s1", "s2", "s3", "s4", "2x food", "-Haw", "-Rip", "-Soph"]

    # Parse final satisfaction from characters.json
    matrix = []
    for name in runs:
        path = os.path.join(V2_RUNS[name], "characters.json")
        row = []
        with open(path) as f:
            chars = json.load(f)
        for agent in agents:
            if agent in chars and chars[agent]:
                last = chars[agent][-1]
                row.append(last.get("reflect_satisfaction", last.get("satisfaction", -1)))
            else:
                row.append(-1)  # agent not in run
        matrix.append(row)

    matrix = np.array(matrix, dtype=float)
    matrix[matrix < 0] = np.nan

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(matrix.T, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    ax.set_xticks(range(len(run_labels)))
    ax.set_xticklabels(run_labels, fontsize=10)
    ax.set_yticks(range(len(short)))
    ax.set_yticklabels(short, fontsize=10)
    ax.set_title("Final Satisfaction by Agent and Run", fontsize=14, fontweight='bold')

    # Add text annotations
    for i in range(len(run_labels)):
        for j in range(len(short)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = 'white' if val < 30 or val > 80 else 'black'
                ax.text(i, j, f"{int(val)}", ha='center', va='center', fontsize=9, color=color, fontweight='bold')
            else:
                ax.text(i, j, "—", ha='center', va='center', fontsize=9, color='#ccc')

    plt.colorbar(im, ax=ax, label='Satisfaction (0-100)', shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "satisfaction.png"), dpi=150)
    plt.close()
    print("  satisfaction.png")


if __name__ == "__main__":
    print("Generating v2 figures...")
    fig_morale_v1_v2()
    fig_morale_counterfactuals()
    fig_food_v1_v2()
    fig_actions_comparison()
    fig_departures()
    fig_satisfaction()
    print(f"Done. Figures in {FIGS_DIR}/")
