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

# Default colors that cycle for any community
ALL_COLORS = [
    "\033[34m",    # blue
    "\033[35m",    # magenta
    "\033[33m",    # yellow
    "\033[32m",    # green
    "\033[36m",    # cyan
    "\033[31m",    # red
]

ALL_EMOJI_POOL = ["⛪", "🪶", "📖", "📰", "🎻", "🌾", "💰", "✍️", "🔨", "🎭", "👤", "🎪"]

# Brook Farm known characters (nice defaults)
BROOK_FARM_EMOJI = {
    "George Ripley":          "⛪",
    "Nathaniel Hawthorne":    "🪶",
    "Sophia Ripley":          "📖",
    "Charles Dana":           "📰",
    "John Sullivan Dwight":   "🎻",
}

BROOK_FARM_TAGLINES = {
    "George Ripley":        "Left the ministry to prove utopia is possible. Needs it to work more than anyone.",
    "Nathaniel Hawthorne":  "Joined not for ideology but to save money to marry. Watches more than he participates.",
    "Sophia Ripley":        "Runs the school — the commune's only real income. Missed two classes in six years.",
    "Charles Dana":         "22 years old, speaks ten languages, does whatever needs doing. The practical one.",
    "John Sullivan Dwight": "Escaped a failed ministry. Found music. Will stay as long as the concerts continue.",
}

def build_agent_info(events):
    """Auto-detect agents from persona_loaded events. Returns dicts for emoji, colors, icons, taglines."""
    agent_names = []
    agent_data = {}
    for e in events:
        if e["type"] == "persona_loaded":
            name = e["agent"]
            if name not in agent_data:
                agent_names.append(name)
                agent_data[name] = e.get("data", {})

    emoji = {}
    colors = {}
    icons = {}
    taglines = {}
    emoji_idx = 0

    for i, name in enumerate(agent_names):
        data = agent_data[name]
        # Use Brook Farm defaults if available, otherwise auto-assign
        emoji[name] = BROOK_FARM_EMOJI.get(name, ALL_EMOJI_POOL[emoji_idx % len(ALL_EMOJI_POOL)])
        if name not in BROOK_FARM_EMOJI:
            emoji_idx += 1
        colors[name] = ALL_COLORS[i % len(ALL_COLORS)]
        # Build initials from name
        parts = name.split()
        initials = "".join(p[0] for p in parts[:2]).upper() if parts else "??"
        role = data.get("role", "Member")
        # Shorten role for display
        short_role = role.split(",")[0].strip()[:10]
        icons[name] = (initials, short_role)
        taglines[name] = BROOK_FARM_TAGLINES.get(name, data.get("motivation", data.get("background", "")))

    return agent_names, emoji, colors, icons, taglines

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

def wrap_text(text, indent="     ", max_line=120):
    """Word-wrap text with indent prefix."""
    if len(indent + text) <= max_line:
        return indent + text
    lines = []
    words = text.split()
    line = indent
    for word in words:
        if len(line) + len(word) + 1 > max_line and line.strip():
            lines.append(line)
            line = indent + word
        else:
            line = line + (' ' if line != indent else '') + word
    if line.strip():
        lines.append(line)
    return '\n'.join(lines)


def render_round(round_num, date, env, actions, conversations, reflections,
                 key_moments, departures, historical_events, votes,
                 agents_present, satisfaction_map,
                 agent_emoji, agent_colors, agent_icons, community_name="Brook Farm", rich=True):
    cols = min(shutil.get_terminal_size((100, 40)).columns, 120)
    total_agents = len(agent_icons)

    clear()

    # ── Header ──
    season = env.get("season", "spring")
    season_icon = SEASON_ART.get(season, "")
    print(f"{BOLD}{'═' * cols}")
    title = f"  {community_name}  {season_icon}  Round {round_num}  •  {date}  •  {season.upper()}"
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
    print(f"  👥 Members {len(agents_present)}/{total_agents}")
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
            icon, role = agent_icons.get(agent, ("??", "Unknown"))
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
    if rich:
        print(f"\n  {'─'*40}")
        print(f"  🎭 Actions")
        print(f"  {'─'*40}")
    else:
        print(f"  {BOLD}— ACTIONS —{RESET}")
    for a in actions:
        agent = a["agent"]
        if agent not in agents_present:
            continue
        icon, role = agent_icons.get(agent, ("??", "Unknown"))
        ac = agent_colors.get(agent, "")
        chosen = a["data"].get("chosen_action", "")
        action_type = chosen.split()[0] if chosen else "?"
        action_detail = chosen[len(action_type):].strip().strip("<>")
        emoji = ACTION_EMOJI.get(action_type, "❓")
        mood = a["data"].get("mood", "")
        first = agent.split()[0]

        if rich:
            inner = a["data"].get("inner_thought", "").strip().strip('*')
            dialogue = a["data"].get("dialogue", "").strip().strip('"')
            if action_detail:
                action_detail_display = action_detail.title() if action_detail == action_detail.upper() else action_detail
                print(f"\n  {emoji} {ac}{BOLD}{first}{RESET} → {action_type.lower()} {action_detail_display}")
            else:
                print(f"\n  {emoji} {ac}{BOLD}{first}{RESET} → {action_type.lower()}")
            if inner:
                print(wrap_text(f"🧠 {inner}"))
            if dialogue and dialogue.lower() != "nothing":
                print(wrap_text(f'💬 "{dialogue}"'))
            print(f"  {'·'*30}")
        else:
            if action_detail:
                print(f"    {emoji} {ac}{BOLD}{icon}{RESET} {DIM}{role:8s}{RESET}  {truncate(action_detail, cols - 28)}")
            else:
                print(f"    {emoji} {ac}{BOLD}{icon}{RESET} {DIM}{role:8s}{RESET}  {action_type.lower()}")
    print()

    # ── Conversations ──
    if conversations:
        if rich:
            print(f"\n  {'─'*40}")
            print(f"  👥 Conversations")
            print(f"  {'─'*40}")
        else:
            print(f"  {BOLD}— OVERHEARD —{RESET}")
        # group by conversation
        seen_convos = {}
        for c in conversations:
            conv_id = c["data"].get("conversation_id", "")
            if conv_id not in seen_convos:
                seen_convos[conv_id] = []
            seen_convos[conv_id].append(c)

        shown = 0
        for conv_id, turns in seen_convos.items():
            if not rich and shown >= 2:
                break

            if rich:
                speakers = []
                for t in turns:
                    first = t["agent"].split()[0]
                    if first not in speakers:
                        speakers.append(first)
                print(f"\n  👥 {' & '.join(speakers)}")
                for t in turns:
                    speaker_first = t["agent"].split()[0]
                    says = t["data"].get("says", "...").strip().strip('"')
                    inner = t["data"].get("inner_thought", "").strip().strip('*')
                    tone = t["data"].get("tone", "")
                    tone_str = f" ({tone})" if tone else ""
                    print(f'\n     {speaker_first}{tone_str}:')
                    print(wrap_text(f'💬 "{says}"', indent="       "))
                    if inner:
                        print(wrap_text(f"🧠 {inner}", indent="       "))
                print(f"  {'·'*30}")
            else:
                agent = turns[0]["agent"]
                says = turns[0]["data"].get("says", "").strip().strip('"')
                inner = turns[0]["data"].get("inner_thought", "").strip().strip('*')
                icon, _ = agent_icons.get(agent, ("??", "Unknown"))
                ac = agent_colors.get(agent, "")

                for end in ['. ', '! ', '? ', '—', '...']:
                    idx = says.find(end)
                    if idx != -1 and idx > 40 and idx < 200:
                        says = says[:idx + len(end.rstrip())]
                        break
                else:
                    says = truncate(says, 180)

                inner_short = ""
                if inner:
                    for end in ['. ', '! ', '? ', '—']:
                        idx = inner.find(end)
                        if idx != -1 and idx > 30 and idx < 150:
                            inner_short = inner[:idx + len(end.rstrip())]
                            break
                    if not inner_short:
                        inner_short = truncate(inner, 130)

                print(f"    {ac}{icon}{RESET}: \"{says}\"")
                if inner_short:
                    print(f"        {DIM}🧠 {inner_short}{RESET}")

            shown += 1
        print()

    # ── Key moments + Reflections ──
    if rich:
        print(f"\n  {'─'*40}")
        print(f"  🪞 Reflections")
        print(f"  {'─'*40}")

        # Build key moments lookup
        km_by_agent = {}
        for km in key_moments:
            km_by_agent[km["agent"]] = km["data"]

        for r in reflections:
            agent = r["agent"]
            if agent not in agents_present:
                continue
            first = agent.split()[0]
            data = r.get("data", {})
            mood = data.get("mood", "neutral")
            sat = data.get("satisfaction", "?")
            summary = data.get("summary", "")
            km = km_by_agent.get(agent, {})
            km_desc = km.get("description", "")
            km_emotion = km.get("emotion", "")

            print(f"\n  {first} (sat {sat}) — {mood}")
            if summary:
                print(wrap_text(summary))
            if km_desc:
                emotion_str = f" [{km_emotion}]" if km_emotion else ""
                print(wrap_text(f"★ {km_desc}{emotion_str}"))
            print(f"  {'·'*30}")
    else:
        if key_moments:
            print(f"  {BOLD}— KEY MOMENTS —{RESET}")
            for km in key_moments[:2]:
                agent = km["agent"]
                icon, _ = agent_icons.get(agent, ("??", "Unknown"))
                ac = agent_colors.get(agent, "")
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
    for name in agent_icons:
        icon, _ = agent_icons.get(name, ("??", "Unknown"))
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
    interactive = True   # default: user controls pace
    rich = False          # default: clean output (replay is fast)
    auto = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--speed" and i + 1 < len(args):
            speed = float(args[i + 1])
            auto = True
            interactive = False
            i += 2
        elif args[i] == "--auto":
            auto = True
            interactive = False
            i += 1
        elif args[i] == "--clean":
            rich = False
            i += 1
        elif args[i] == "--rich":
            rich = True
            i += 1
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
        print("Usage: python replay.py [run_directory] [--rich] [--auto] [--speed SECONDS]")
        print("  Default: clean interactive (press Enter to advance)")
        print("  --rich:  full conversations, inner thoughts, reflections")
        print("  --auto:  auto-advance (use --speed to set pace)")
        sys.exit(1)

    print(f"Loading: {os.path.basename(run_dir)}")
    events = load_run(run_dir)
    rounds = get_rounds(events)

    # auto-detect agents from events
    agent_names, agent_emoji, agent_colors, agent_icons, agent_taglines = build_agent_info(events)

    # detect community name from sim_start event or default
    community_name = "Brook Farm"
    for e in events:
        if e["type"] == "sim_start":
            community_name = e.get("data", {}).get("experiment", community_name)
            break

    # init agents
    agents_present = set()
    satisfaction_map = {}
    for e in events:
        if e["type"] == "persona_loaded":
            agents_present.add(e["agent"])
            satisfaction_map[e["agent"]] = 70

    max_round = max(rounds.keys())
    print(f"  {len(events)} events • {max_round} rounds • {len(agents_present)} agents")
    mode = "rich" if rich else "clean"
    print(f"  Mode: {mode} • {'interactive' if interactive else f'auto ({speed}s/round)'}")

    print(f"\nPress Enter to start...")
    input()

    # ── Intro screen ──
    cols = min(shutil.get_terminal_size((100, 40)).columns, 120)
    clear()
    print()
    print(f"        🌳🌾🌳      🏠  🏫      🌳🌾🌳")
    print(f"          🌿    🐄    🌻  🌻    🐔    🌿")
    print()
    print(f"              🏡  {community_name.upper()}")
    print()
    print(f"  {'─' * (cols - 4)}")
    print(f"  {BOLD}👥 THE RESIDENTS{RESET}")
    print()

    for e in events:
        if e["type"] == "persona_loaded":
            name = e["agent"]
            data = e.get("data", {})
            icon, _ = agent_icons.get(name, ("??", "Unknown"))
            age = data.get("age", "?")
            ac = agent_colors.get(name, "")
            ae = agent_emoji.get(name, "👤")
            tagline = agent_taglines.get(name, "")

            print(f"    {ae} {ac}{BOLD}{icon}  {name}{RESET}, {age}")
            if tagline:
                print(f"        {DIM}{tagline[:100]}{RESET}")
            print()

    print(f"  {'─' * (cols - 4)}")
    print(f"  🎭 {DIM}{max_round} rounds • Every decision made by AI agents{RESET}")

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
                     rd["agents_present"], rd["satisfaction_map"],
                     agent_emoji, agent_colors, agent_icons, community_name, rich)

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
    all_agent_names = set(agent_icons.keys())
    departed = all_agent_names - final_agents
    total = len(all_agent_names)

    clear()
    print()
    print(f"        🌳  🍂      🏚️   🏚️       🍂  🌳")
    print(f"          🌿          🍂  🍂          🌿")
    print()
    print(f"              {RED}{BOLD}T H E   E N D{RESET}")
    print(f"              {DIM}{final_env.get('date', 'Unknown')} — {community_name} closes.{RESET}")
    print()
    print(f"  {'─' * (cols - 4)}")
    print(f"  {BOLD}👥 FINAL FATES{RESET}")
    print()

    for name in agent_names:
        icon, _ = agent_icons.get(name, ("??", "Unknown"))
        ac = agent_colors.get(name, "")
        ae = agent_emoji.get(name, "👤")
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
    print(f"  {DIM}Survived: {len(final_agents)}/{total}  •  Departed: {len(departed)}/{total}{RESET}")
    print()

if __name__ == "__main__":
    main()
