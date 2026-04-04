#!/usr/bin/env python3
"""
Utopia Replay — ASCII animated playback of commune simulation runs.

Usage: python replay.py [run_directory] [--speed SECONDS]
"""

import json
import sys
import os
import time
import shutil

# ── Characters ──────────────────────────────────────────────────────

AGENT_EMOJI = {
    "George Ripley":          "⛪",
    "Nathaniel Hawthorne":    "🪶",
    "Sophia Ripley":          "📖",
    "Charles Dana":           "📰",
    "John Sullivan Dwight":   "🎻",
}

AGENT_COLORS = {
    "George Ripley":          "\033[34m",    # blue
    "Nathaniel Hawthorne":    "\033[35m",    # magenta
    "Sophia Ripley":          "\033[33m",    # yellow
    "Charles Dana":           "\033[32m",    # green
    "John Sullivan Dwight":   "\033[36m",    # cyan
}

AGENT_ICONS = {
    "George Ripley":          ("GR", "Founder"),
    "Nathaniel Hawthorne":    ("NH", "Writer"),
    "Sophia Ripley":          ("SR", "Teacher"),
    "Charles Dana":           ("CD", "Editor"),
    "John Sullivan Dwight":   ("JD", "Musician"),
}

ACTION_EMOJI = {
    "FARM":         "🌾",
    "TEACH":        "📚",
    "WRITE":        "✍️ ",
    "SPEAK":        "🗣️ ",
    "ORGANIZE":     "🎵",
    "TRADE":        "💰",
    "BUILD":        "🔨",
    "REPAIR":       "🔧",
    "REST":         "💤",
    "LEAVE":        "🚪",
    "PROPOSE_RULE": "📜",
    "RULE":         "📜",
    "VOTE":         "🗳️ ",
}

SEASON_ART = {
    "spring": "🌱",
    "summer": "☀️ ",
    "fall":   "🍂",
    "winter": "❄️ ",
}

# ── Rendering ───────────────────────────────────────────────────────

def clear():
    print("\033[2J\033[H", end="")

def bar(value, max_val, width=20, fill="█", empty="░"):
    if max_val == 0:
        filled = 0
    else:
        filled = int((value / max_val) * width)
    filled = max(0, min(filled, width))
    return fill * filled + empty * (width - filled)

def morale_color(m):
    if m >= 60: return "\033[32m"   # green
    if m >= 30: return "\033[33m"   # yellow
    return "\033[31m"               # red

def sat_color(s):
    if isinstance(s, (int, float)):
        if s >= 60: return "\033[32m"
        if s >= 30: return "\033[33m"
        return "\033[31m"
    return ""

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"

def truncate(s, max_len):
    if len(s) > max_len:
        return s[:max_len-3] + "..."
    return s

def render_round(round_num, date, env, actions, conversations, reflections,
                 key_moments, departures, historical_events, votes,
                 agents_present, satisfaction_map):
    cols = min(shutil.get_terminal_size((100, 40)).columns, 120)

    clear()

    # ── Header ──
    season = env.get("season", "spring")
    season_icon = SEASON_ART.get(season, "")
    print(f"{BOLD}{'═' * cols}")
    title = f"  BROOK FARM  {season_icon}  Round {round_num}  •  {date}  •  {season.upper()}"
    print(title)
    print(f"{'═' * cols}{RESET}")
    print()

    # ── Resources ──
    food = env.get("food", 0)
    money = env.get("money", 0)
    morale = env.get("morale", 0)
    mc = morale_color(morale)

    print(f"  🍞 Food    {bar(food, 200, 25)}  {food}")
    print(f"  💵 Money   {bar(money, 500, 25)}  ${money}")
    print(f"  {mc}♥  Morale  {bar(morale, 100, 25)}  {morale}%{RESET}")
    print(f"  👥 Members {len(agents_present)}/5")
    print()

    # ── Historical events ──
    if historical_events:
        for he in historical_events[:2]:
            print(f"  {YELLOW}📜 {truncate(he, cols - 8)}{RESET}")
        print()

    # ── Departures (show before actions — dramatic) ──
    if departures:
        for d in departures:
            agent = d["agent"]
            icon, role = AGENT_ICONS.get(agent, ("??", "Unknown"))
            sat = d["data"].get("final_satisfaction", "?")
            concerns = d["data"].get("final_concerns", [])
            farewell = concerns[0] if concerns else ""
            print(f"  {RED}{'━' * (cols - 4)}")
            print(f"  🚪 {BOLD}{agent} DEPARTS{RESET}{RED}  (satisfaction: {sat}){RESET}")
            if farewell:
                # wrap farewell
                print(f"  {DIM}\"{truncate(farewell, cols - 8)}\"{RESET}")
            print(f"  {RED}{'━' * (cols - 4)}{RESET}")
        print()

    # ── Actions ──
    print(f"  {BOLD}— ACTIONS —{RESET}")
    for a in actions:
        agent = a["agent"]
        if agent not in agents_present:
            continue
        icon, role = AGENT_ICONS.get(agent, ("??", "Unknown"))
        ac = AGENT_COLORS.get(agent, "")
        chosen = a["data"].get("chosen_action", "")
        action_type = chosen.split()[0] if chosen else "?"
        action_detail = chosen[len(action_type):].strip().strip("<>")
        # don't fall back to reasoning — it's too long
        emoji = ACTION_EMOJI.get(action_type, "❓")
        if action_detail:
            print(f"    {emoji} {ac}{BOLD}{icon}{RESET} {DIM}{role:8s}{RESET}  {truncate(action_detail, cols - 28)}")
        else:
            print(f"    {emoji} {ac}{BOLD}{icon}{RESET} {DIM}{role:8s}{RESET}  {action_type.lower()}")
    print()

    # ── Conversations (best 2 exchanges with inner thoughts) ──
    if conversations:
        print(f"  {BOLD}— OVERHEARD —{RESET}")
        # group by conversation, show first exchange from each (2 convos max)
        seen_convos = set()
        shown = 0
        for c in conversations:
            if shown >= 2:
                break
            conv_id = c["data"].get("conversation_id", "")
            if conv_id in seen_convos:
                continue
            seen_convos.add(conv_id)

            agent = c["agent"]
            says = c["data"].get("says", "").strip().strip('"')
            inner = c["data"].get("inner_thought", "").strip().strip('*')
            icon, _ = AGENT_ICONS.get(agent, ("??", "Unknown"))
            ac = AGENT_COLORS.get(agent, "")

            # extract first sentence only
            for end in ['. ', '! ', '? ', '—', '...']:
                idx = says.find(end)
                if idx != -1 and idx < 120:
                    says = says[:idx + len(end.rstrip())]
                    break
            else:
                says = truncate(says, 100)

            inner_short = ""
            if inner:
                for end in ['. ', '! ', '? ', '—']:
                    idx = inner.find(end)
                    if idx != -1 and idx < 100:
                        inner_short = inner[:idx + len(end.rstrip())]
                        break
                if not inner_short:
                    inner_short = truncate(inner, 80)

            print(f"    {ac}{icon}{RESET}: \"{says}\"")
            if inner_short:
                print(f"        {DIM}💭 {inner_short}{RESET}")
            shown += 1
        print()

    # ── Key moments ──
    if key_moments:
        print(f"  {BOLD}— KEY MOMENTS —{RESET}")
        for km in key_moments[:2]:
            agent = km["agent"]
            icon, _ = AGENT_ICONS.get(agent, ("??", "Unknown"))
            ac = AGENT_COLORS.get(agent, "")
            desc = km["data"].get("description", "")
            emotion = km["data"].get("emotion", "")
            print(f"    {MAGENTA}★ {ac}{icon}{RESET}: {truncate(desc, cols - 14)}")
            if emotion:
                print(f"        {DIM}Feeling: {emotion}{RESET}")
        print()

    # ── Votes ──
    if votes:
        for v in votes:
            proposal = v.get("data", {}).get("proposal", "")
            result = v.get("data", {}).get("result", "")
            print(f"  {YELLOW}🗳️  VOTE: {truncate(proposal, cols - 15)}{RESET}")
            print(f"      Result: {result}")
        print()

    # ── Agent status strip ──
    print(f"  {'─' * (cols - 4)}")
    parts = []
    for name in ["George Ripley", "Nathaniel Hawthorne", "Sophia Ripley",
                  "Charles Dana", "John Sullivan Dwight"]:
        icon, _ = AGENT_ICONS.get(name, ("??", "Unknown"))
        if name not in agents_present:
            parts.append(f"{DIM}{icon}:gone{RESET}")
        else:
            sat = satisfaction_map.get(name, "?")
            sc = sat_color(sat)
            parts.append(f"{sc}{icon}:{sat}{RESET}")
    print(f"  {' │ '.join(parts)}")


# ── Main ────────────────────────────────────────────────────────────

def load_run(run_dir):
    events = []
    with open(os.path.join(run_dir, "events.jsonl")) as f:
        for line in f:
            events.append(json.loads(line))
    return events

def get_rounds(events):
    rounds = {}
    for e in events:
        r = e.get("round", 0)
        if r not in rounds:
            rounds[r] = []
        rounds[r].append(e)
    return rounds

def find_default_run():
    runs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
    if not os.path.exists(runs_dir):
        return None
    # prefer v2 baseline runs
    candidates = sorted(os.listdir(runs_dir))
    v2 = [d for d in candidates if d.startswith("v2_baseline")]
    if v2:
        return os.path.join(runs_dir, v2[-1])
    if candidates:
        return os.path.join(runs_dir, candidates[-1])
    return None

def main():
    # parse args
    run_dir = None
    speed = 3.0
    interactive = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--speed" and i + 1 < len(args):
            speed = float(args[i + 1])
            i += 2
        elif args[i] == "--interactive" or args[i] == "-i":
            interactive = True
            i += 1
        elif not args[i].startswith("--"):
            run_dir = args[i]
            i += 1
        else:
            i += 1

    if not run_dir:
        run_dir = find_default_run()
    if not run_dir or not os.path.exists(run_dir):
        print("Usage: python replay.py [run_directory] [--speed SECONDS] [-i]")
        print("  -i / --interactive: press Enter to advance each round")
        sys.exit(1)

    print(f"Loading: {os.path.basename(run_dir)}")
    events = load_run(run_dir)
    rounds = get_rounds(events)

    # init agents
    agents_present = set()
    satisfaction_map = {}
    for e in events:
        if e["type"] == "persona_loaded":
            agents_present.add(e["agent"])
            satisfaction_map[e["agent"]] = 70

    max_round = max(rounds.keys())
    print(f"  {len(events)} events • {max_round} rounds • {len(agents_present)} agents")

    if interactive:
        print(f"\nPress Enter to advance, 'b' to go back, 'q' to quit...")
    else:
        print(f"\nSpeed: {speed}s/round • Press Enter to start, Ctrl+C to quit...")
    input()

    # ── Intro screen ──
    cols = min(shutil.get_terminal_size((100, 40)).columns, 120)
    clear()
    print()
    print(f"        🌳🌾🌳      🏠  🏫      🌳🌾🌳")
    print(f"          🌿    🐄    🌻  🌻    🐔    🌿")
    print()
    print(f"              🏡  B R O O K   F A R M")
    print(f"              {DIM}West Roxbury, Massachusetts — 1841{RESET}")
    print()
    print(f"  {YELLOW}\"A light over this country and this age.\"{RESET}")
    print(f"  {DIM}— George Ripley, in a letter to Ralph Waldo Emerson{RESET}")
    print()
    print(f"  A transcendentalist commune founded on a radical idea:")
    print(f"  that intellectual life and manual labor can coexist,")
    print(f"  that a community of thinkers can also feed itself.")
    print()
    print(f"  {RED}It lasted six years. Today we rebuild it with AI agents to see how it falls apart.{RESET}")
    print()
    print(f"  {'─' * (cols - 4)}")
    print(f"  {BOLD}👥 THE RESIDENTS{RESET}")
    print()

    # curated one-liners (persona data uses 2nd person which reads weird)
    AGENT_TAGLINES = {
        "George Ripley":        "Left the ministry to prove utopia is possible. Needs it to work more than anyone.",
        "Nathaniel Hawthorne":  "Joined not for ideology but to save money to marry. Watches more than he participates.",
        "Sophia Ripley":        "Runs the school — the commune's only real income. Missed two classes in six years.",
        "Charles Dana":         "22 years old, speaks ten languages, does whatever needs doing. The practical one.",
        "John Sullivan Dwight": "Escaped a failed ministry. Found music. Will stay as long as the concerts continue.",
    }

    for e in events:
        if e["type"] == "persona_loaded":
            name = e["agent"]
            data = e.get("data", {})
            icon, _ = AGENT_ICONS.get(name, ("??", "Unknown"))
            age = data.get("age", "?")
            ac = AGENT_COLORS.get(name, "")
            ae = AGENT_EMOJI.get(name, "👤")
            tagline = AGENT_TAGLINES.get(name, "")

            print(f"    {ae} {ac}{BOLD}{icon}  {name}{RESET}, {age}")
            print(f"        {DIM}{tagline}{RESET}")
            print()

    print(f"  {'─' * (cols - 4)}")
    print(f"  🎭 {DIM}30 rounds • 6 years • Every decision made by AI agents")
    print(f"     who don't know what happened to the real Brook Farm.{RESET}")

    try:
        if interactive:
            input(f"\n  {DIM}[Enter] begin{RESET} ")
        else:
            time.sleep(speed * 2)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

    # precompute per-round data (enables going back)
    round_data = []
    snap_agents = set()
    snap_sat = {}
    for e in events:
        if e["type"] == "persona_loaded":
            snap_agents.add(e["agent"])
            snap_sat[e["agent"]] = 70

    for r in range(1, max_round + 1):
        round_events = rounds.get(r, [])

        env = {}
        actions = []
        conversations = []
        reflections = []
        key_moments = []
        departures = []
        historical_events = []
        votes = []

        for e in round_events:
            t = e["type"]
            if t == "env_state":
                env = e.get("data", {})
            elif t == "action":
                actions.append(e)
            elif t == "utterance":
                conversations.append(e)
            elif t == "reflection":
                reflections.append(e)
                agent = e["agent"]
                sat = e.get("data", {}).get("satisfaction", None)
                if sat is not None:
                    snap_sat[agent] = sat
            elif t == "key_moment":
                key_moments.append(e)
            elif t == "agent_departed":
                departures.append(e)
                snap_agents.discard(e["agent"])
            elif t == "historical_event":
                desc = e.get("data", {}).get("description", "")
                if not desc:
                    desc = str(e.get("data", ""))
                historical_events.append(desc)
            elif t == "vote_result":
                votes.append(e)

        round_data.append({
            "round": r,
            "env": env,
            "actions": actions,
            "conversations": conversations,
            "reflections": reflections,
            "key_moments": key_moments,
            "departures": departures,
            "historical_events": historical_events,
            "votes": votes,
            "agents_present": set(snap_agents),
            "satisfaction_map": dict(snap_sat),
        })

    # playback loop with back support
    idx = 0
    while idx < len(round_data):
        rd = round_data[idx]
        render_round(rd["round"], rd["env"].get("date", f"Round {rd['round']}"),
                     rd["env"], rd["actions"], rd["conversations"],
                     rd["reflections"], rd["key_moments"], rd["departures"],
                     rd["historical_events"], rd["votes"],
                     rd["agents_present"], rd["satisfaction_map"])

        try:
            if idx < len(round_data) - 1:
                if interactive:
                    resp = input(f"\n  {DIM}[Enter] next  [b] back  [q] quit{RESET} ").strip().lower()
                    if resp == 'q':
                        break
                    elif resp == 'b':
                        if idx > 0:
                            idx -= 1
                        continue
                    else:
                        idx += 1
                else:
                    time.sleep(speed)
                    idx += 1
            else:
                idx += 1
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}  Stopped at round {rd['round']}.{RESET}")
            sys.exit(0)

    # finale
    final = round_data[-1] if round_data else {}
    final_agents = final.get("agents_present", set())
    final_sat = final.get("satisfaction_map", {})
    final_env = final.get("env", {})
    departed = set(AGENT_ICONS.keys()) - final_agents

    clear()
    print()
    print(f"        🌳  🍂      🏚️   🏚️       🍂  🌳")
    print(f"          🌿          🍂  🍂          🌿")
    print()
    print(f"              {RED}{BOLD}T H E   E N D{RESET}")
    print(f"              {DIM}{final_env.get('date', 'Unknown')} — Brook Farm closes.{RESET}")
    print()
    print(f"  {'─' * (cols - 4)}")
    print(f"  {BOLD}👥 FINAL FATES{RESET}")
    print()

    for name in ["George Ripley", "Nathaniel Hawthorne", "Sophia Ripley",
                  "Charles Dana", "John Sullivan Dwight"]:
        icon, _ = AGENT_ICONS.get(name, ("??", "Unknown"))
        ac = AGENT_COLORS.get(name, "")
        ae = AGENT_EMOJI.get(name, "👤")
        sat = final_sat.get(name, "?")
        sc = sat_color(sat)

        if name in departed:
            farewell = ""
            dep_round = "?"
            dep_date = ""
            for rd in round_data:
                for d in rd["departures"]:
                    if d["agent"] == name:
                        dep_round = d["data"].get("round", "?")
                        dep_date = d["data"].get("date", "")
                        concerns = d["data"].get("final_concerns", [])
                        farewell = concerns[0] if concerns else ""
            status_line = f"{RED}Departed round {dep_round} ({dep_date}){RESET}"
        else:
            farewell = ""
            status_line = f"{DIM}Remained to the end{RESET}"

        print(f"    {ae} {ac}{BOLD}{icon}  {name}{RESET}")
        print(f"        {sc}Satisfaction: {sat}{RESET}  •  {status_line}")
        if farewell:
            short = farewell
            for end in ['. ', '! ', '? ', '—']:
                idx = farewell.find(end)
                if idx != -1 and idx < 120:
                    short = farewell[:idx + len(end.rstrip())]
                    break
            else:
                short = truncate(farewell, 100)
            print(f"        {DIM}\"{short}\"{RESET}")
        print()

    print(f"  {'─' * (cols - 4)}")
    food = final_env.get("food", "?")
    money = final_env.get("money", "?")
    morale = final_env.get("morale", "?")
    print(f"  {DIM}Final state: 🍞 {food} food  💵 ${money}  ♥ {morale}% morale{RESET}")
    print(f"  {DIM}Survived: {len(final_agents)}/5  •  Departed: {len(departed)}/5{RESET}")
    print()

if __name__ == "__main__":
    main()
