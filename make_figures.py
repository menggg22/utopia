"""Generate figures for README from run data."""
import csv
import json
import os
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("pip install matplotlib")
    sys.exit(1)

RUNS_DIR = "runs"
FIGS_DIR = "figures"
os.makedirs(FIGS_DIR, exist_ok=True)

# Color palette
COLORS = {
    "original": "#2d2d2d",
    "baseline": "#888888",
    "no_hawthorne": "#4CAF50",
    "no_sophia": "#F44336",
    "no_ripley": "#FF9800",
    "double_food": "#2196F3",
}

LABELS = {
    "original": "Original",
    "baseline": "Baseline (seed 0)",
    "no_hawthorne": "No Hawthorne",
    "no_sophia": "No Sophia",
    "no_ripley": "No Ripley",
    "double_food": "Double Food",
}

RUN_DIRS = {
    "original": "run_20260401_235509",
    "baseline": "baseline_20260402_085324",
    "no_hawthorne": "no_hawthorne_20260402_103514",
    "no_sophia": "no_sophia_20260402_115345",
    "no_ripley": "no_ripley_20260402_131839",
    "double_food": "double_food_20260402_144239",
}


def load_metrics(run_name):
    path = os.path.join(RUNS_DIR, RUN_DIRS[run_name], "metrics.csv")
    rounds, food, money, morale = [], [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rounds.append(int(row["round"]))
            food.append(int(row["food"]))
            money.append(int(row["money"]))
            morale.append(int(row["morale"]))
    return rounds, food, money, morale


def load_characters(run_name):
    path = os.path.join(RUNS_DIR, RUN_DIRS[run_name], "characters.json")
    with open(path) as f:
        return json.load(f)


def load_summary(run_name):
    path = os.path.join(RUNS_DIR, RUN_DIRS[run_name], "summary.txt")
    with open(path) as f:
        return f.read()


def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)


# --- Figure 1: Morale across all runs ---
def fig_morale():
    fig, ax = plt.subplots(figsize=(10, 5))
    for name in ["original", "baseline", "no_hawthorne", "no_sophia", "no_ripley", "double_food"]:
        rounds, food, money, morale = load_metrics(name)
        style = "-" if name in ("original", "no_hawthorne", "no_sophia") else "--"
        lw = 2.5 if name in ("original", "no_hawthorne", "no_sophia") else 1.5
        ax.plot(rounds, morale, style, color=COLORS[name], label=LABELS[name], linewidth=lw)

    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Community Morale (%)", fontsize=12)
    ax.set_title("Every Community Fails — The Question Is How Fast", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_ylim(-5, 105)
    ax.axhline(y=0, color='red', linewidth=0.5, alpha=0.5)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "morale.png"), dpi=150)
    plt.close()
    print("  morale.png")


# --- Figure 2: What agents actually do (action distribution) ---
def fig_actions():
    # Parse action counts from summaries
    action_data = {}
    for name in ["original", "baseline", "no_hawthorne", "no_sophia", "double_food"]:
        summary = load_summary(name)
        actions = {}
        in_actions = False
        for line in summary.split("\n"):
            if "Action counts:" in line or "action counts:" in line.lower():
                in_actions = True
                continue
            if in_actions and ":" in line and line.strip():
                parts = line.strip().split(":")
                if len(parts) == 2:
                    act = parts[0].strip().upper()
                    try:
                        count = int(parts[1].strip())
                        actions[act] = count
                    except ValueError:
                        pass
            elif in_actions and not line.strip():
                in_actions = False
        action_data[name] = actions

    # If summaries don't have action counts, fall back to events.jsonl
    if not action_data.get("original"):
        print("  (parsing events.jsonl for action counts)")
        for name in ["original", "baseline", "no_hawthorne", "no_sophia", "double_food"]:
            path = os.path.join(RUNS_DIR, RUN_DIRS[name], "events.jsonl")
            actions = {}
            with open(path) as f:
                for line in f:
                    ev = json.loads(line)
                    if ev.get("type") == "action":
                        raw = ev.get("data", {}).get("chosen_action", "REST")
                        act = raw.split()[0].upper() if raw.strip() else "REST"
                        actions[act] = actions.get(act, 0) + 1
            action_data[name] = actions

    # Build stacked bar chart for original run
    acts = action_data.get("original", {})
    if not acts:
        print("  skipping actions chart (no data)")
        return

    # Sort by count
    sorted_acts = sorted(acts.items(), key=lambda x: -x[1])
    labels = [a[0].capitalize() for a in sorted_acts]
    values = [a[1] for a in sorted_acts]

    # Color by category
    act_colors = {
        "SPEAK": "#FF6B6B",
        "TEACH": "#4ECDC4",
        "FARM": "#45B7D1",
        "ORGANIZE": "#96CEB4",
        "TRADE": "#FFEAA7",
        "WRITE": "#DDA0DD",
        "BUILD": "#F4A460",
        "REST": "#C0C0C0",
        "PROPOSE": "#FFB347",
        "REPAIR": "#87CEEB",
        "LEAVE": "#2d2d2d",
    }
    colors = [act_colors.get(a[0], "#AAAAAA") for a in sorted_acts]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], edgecolor='white', linewidth=0.5)
    ax.set_xlabel("Total Actions (30 rounds, 5 agents)", fontsize=11)
    ax.set_title("What They Did Instead of Farming", fontsize=14, fontweight='bold')
    style_ax(ax)

    # Add count labels
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "actions.png"), dpi=150)
    plt.close()
    print("  actions.png")


# --- Figure 3: The counterfactual comparison ---
def fig_counterfactual():
    data = {
        "Original": {"money": 224, "satisfaction": 24, "departures": 2},
        "No Hawthorne": {"money": 234, "satisfaction": 74, "departures": 0},
        "No Sophia": {"money": -1, "satisfaction": 4, "departures": 1},
        "No Ripley": {"money": 44, "satisfaction": 41, "departures": 0},
        "Double Food": {"money": 394, "satisfaction": 51, "departures": 1},
    }

    names = list(data.keys())
    sats = [data[n]["satisfaction"] for n in names]
    colors_bar = ["#2d2d2d", "#4CAF50", "#F44336", "#FF9800", "#2196F3"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, sats, color=colors_bar, edgecolor='white', linewidth=0.5, width=0.6)
    ax.set_ylabel("Average Final Satisfaction", fontsize=12)
    ax.set_title("Remove the Skeptic, Keep the Teacher", fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    style_ax(ax)

    # Add value labels
    for bar, val in zip(bars, sats):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(val), ha='center', fontsize=12, fontweight='bold')

    # Annotate
    ax.annotate('Happiest\ncommunity', xy=(1, 74), xytext=(1, 90),
                ha='center', fontsize=9, color='#4CAF50',
                arrowprops=dict(arrowstyle='->', color='#4CAF50'))
    ax.annotate('Only run that\ngoes bankrupt', xy=(2, 4), xytext=(2.8, 25),
                ha='center', fontsize=9, color='#F44336',
                arrowprops=dict(arrowstyle='->', color='#F44336'))

    plt.xticks(rotation=15)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "counterfactual.png"), dpi=150)
    plt.close()
    print("  counterfactual.png")


if __name__ == "__main__":
    print("Generating figures...")
    fig_morale()
    fig_actions()
    fig_counterfactual()
    print("Done. Figures in figures/")
