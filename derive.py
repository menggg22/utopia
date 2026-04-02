"""
Derive outputs from events.jsonl — the single source of truth.

Usage:
    python derive.py runs/run_XXX/events.jsonl        # all outputs
    python derive.py runs/run_XXX/events.jsonl narrative
    python derive.py runs/run_XXX/events.jsonl characters
    python derive.py runs/run_XXX/events.jsonl metrics
    python derive.py runs/run_XXX/events.jsonl conversations
    python derive.py runs/run_XXX/events.jsonl votes
    python derive.py runs/run_XXX/events.jsonl summary
"""

import sys
import os
import json
import csv


def load_events(path: str) -> list:
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def derive_narrative(events: list, out_path: str):
    """Generate human-readable narrative markdown."""
    with open(out_path, "w") as f:
        # Header
        sim_start = next((e for e in events if e["type"] == "sim_start"), None)
        sim_end = next((e for e in events if e["type"] == "sim_end"), None)

        f.write("# Brook Farm — Simulation Narrative\n\n")
        if sim_start:
            d = sim_start["data"]
            f.write(f"**Model**: {d.get('model', '?')}\n")
            f.write(f"**Agents**: {', '.join(d.get('agents', []))}\n")
        if sim_end:
            d = sim_end["data"]
            fs = d.get("final_state", {})
            f.write(f"**Rounds**: {d.get('rounds_completed', '?')}\n")
            f.write(f"**Final**: Food={fs.get('food', '?')}, Money=${fs.get('money', '?')}, Morale={fs.get('morale', '?')}%\n")
            f.write(f"**Departed**: {', '.join(d.get('departed', [])) or 'None'}\n")
            f.write(f"**Survived**: {', '.join(d.get('survived', [])) or 'None'}\n")
        f.write("\n---\n\n")

        # Group by round
        rounds = {}
        for e in events:
            r = e.get("round", 0)
            if r not in rounds:
                rounds[r] = []
            rounds[r].append(e)

        for round_num in sorted(rounds.keys()):
            if round_num == 0:
                continue
            round_events = rounds[round_num]

            # Get date from first event
            date = round_events[0].get("date", "?")
            env_state = next((e for e in round_events if e["type"] == "env_state"), None)

            f.write(f"## {date} (Round {round_num})\n\n")
            if env_state:
                d = env_state["data"]
                f.write(f"*{d.get('season', '?').capitalize()}. Food: {d.get('food', '?')}, Money: ${d.get('money', '?')}, Morale: {d.get('morale', '?')}%*\n\n")

            # Historical events
            for e in round_events:
                if e["type"] == "historical_event":
                    f.write(f"> **EVENT**: {e['data'].get('description', '')}\n\n")

            # Actions
            actions = [e for e in round_events if e["type"] == "action"]
            if actions:
                for e in actions:
                    d = e["data"]
                    f.write(f"### {e['agent']}\n\n")
                    f.write(f"**{d.get('chosen_action', '?')}**\n\n")
                    f.write(f"*Reasoning*: {d.get('reasoning', '')}\n\n")
                    f.write(f"*Inner thought*: {d.get('inner_thought', '')}\n\n")
                    if d.get("observation"):
                        f.write(f"*Observes*: {d['observation']}\n\n")
                    dialogue = d.get("dialogue", "nothing")
                    if dialogue and dialogue.lower() != "nothing":
                        f.write(f'*Says aloud*: "{dialogue}"\n\n')
                    f.write(f"*Mood*: {d.get('mood', '?')} | *Satisfaction*: {d.get('satisfaction_after', '?')}/100\n\n")

            # Conversations
            utterances = [e for e in round_events if e["type"] == "utterance"]
            if utterances:
                f.write("### Conversations\n\n")
                # Group by conversation_id
                convs = {}
                for e in utterances:
                    cid = e["data"].get("conversation_id", "?")
                    if cid not in convs:
                        convs[cid] = []
                    convs[cid].append(e)
                for cid, turns in convs.items():
                    f.write(f"**{cid}**\n\n")
                    for t in turns:
                        d = t["data"]
                        f.write(f'> **{t["agent"]}** ({d.get("tone", "?")}): "{d.get("says", "...")}"\n')
                        f.write(f'> *thinks: {d.get("inner_thought", "")}*\n\n')

            # Votes
            vote_results = [e for e in round_events if e["type"] == "vote_result"]
            for e in vote_results:
                d = e["data"]
                t = d.get("tally", {})
                f.write(f"### Vote: {d.get('proposal', '?')}\n\n")
                f.write(f"**{d.get('result', '?')}** ({t.get('YES', 0)} YES, {t.get('NO', 0)} NO)\n\n")
                for name, vote in d.get("votes", {}).items():
                    f.write(f"- {name}: {vote}\n")
                f.write("\n")

            # Reflections
            reflections = [e for e in round_events if e["type"] == "reflection"]
            if reflections:
                f.write("### End of Day\n\n")
                for e in reflections:
                    d = e["data"]
                    f.write(f"**{e['agent']}** (mood: {d.get('mood', '?')}, satisfaction: {d.get('satisfaction', '?')}/100)\n")
                    f.write(f"> {d.get('summary', '')}\n\n")

            # Departures
            departures = [e for e in round_events if e["type"] == "agent_departed"]
            for e in departures:
                d = e["data"]
                f.write(f"### *** {e['agent']} DEPARTS ***\n\n")
                if d.get("parting_words"):
                    f.write(f'> "{d["parting_words"]}"\n\n')
                if d.get("inner_thought"):
                    f.write(f'*Inner thought: {d["inner_thought"]}*\n\n')

            f.write("---\n\n")


def derive_characters(events: list, out_path: str):
    """Extract per-character arc data."""
    characters = {}

    for e in events:
        if e["type"] == "action":
            name = e["agent"]
            if name not in characters:
                characters[name] = []
            d = e["data"]
            characters[name].append({
                "round": e["round"],
                "date": e.get("date"),
                "action": d.get("chosen_action"),
                "mood": d.get("mood"),
                "satisfaction": d.get("satisfaction_after"),
                "inner_thought": d.get("inner_thought"),
                "observation": d.get("observation"),
            })

        if e["type"] == "reflection":
            name = e["agent"]
            if name in characters and characters[name]:
                last = characters[name][-1]
                if last["round"] == e["round"]:
                    d = e["data"]
                    last["reflect_mood"] = d.get("mood")
                    last["reflect_satisfaction"] = d.get("satisfaction")
                    last["concerns"] = d.get("concerns_updated")
                    last["relationships"] = d.get("relationships_updated")

        if e["type"] == "agent_departed":
            name = e["agent"]
            if name not in characters:
                characters[name] = []
            characters[name].append({
                "round": e["round"],
                "date": e.get("date"),
                "action": "LEAVE",
                "departed": True,
                **e["data"],
            })

    with open(out_path, "w") as f:
        json.dump(characters, f, indent=2)


def derive_metrics(events: list, out_path: str):
    """Extract environment time series as CSV."""
    rows = []
    for e in events:
        if e["type"] == "env_state":
            d = e["data"]
            rows.append({
                "round": e["round"],
                "date": d.get("date", ""),
                "food": d.get("food", ""),
                "money": d.get("money", ""),
                "morale": d.get("morale", ""),
                "members": d.get("members_present", ""),
                "season": d.get("season", ""),
            })

    if rows:
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)


def derive_conversations(events: list, out_path: str):
    """Extract all conversations."""
    conversations = {}

    for e in events:
        if e["type"] == "conversation_start":
            cid = e["data"].get("conversation_id", f"r{e['round']}_unknown")
            conversations[cid] = {
                "round": e["round"],
                "date": e.get("date"),
                "participants": e["data"].get("participants", []),
                "context": e["data"].get("context", ""),
                "exchanges": [],
            }
        elif e["type"] == "utterance":
            cid = e["data"].get("conversation_id", "")
            if cid in conversations:
                conversations[cid]["exchanges"].append({
                    "speaker": e["agent"],
                    "turn": e["data"].get("turn"),
                    "says": e["data"].get("says", ""),
                    "tone": e["data"].get("tone", ""),
                    "inner_thought": e["data"].get("inner_thought", ""),
                })
        elif e["type"] == "conversation_end":
            cid = e["data"].get("conversation_id", "")
            if cid in conversations:
                conversations[cid]["turns"] = e["data"].get("turns", 0)

    with open(out_path, "w") as f:
        json.dump(list(conversations.values()), f, indent=2)


def derive_votes(events: list, out_path: str):
    """Extract all votes."""
    votes = []
    current_vote = None

    for e in events:
        if e["type"] == "vote_start":
            current_vote = {
                "round": e["round"],
                "date": e.get("date"),
                "proposal": e["data"].get("proposal", ""),
                "proposed_by": e["data"].get("proposed_by", ""),
                "votes": {},
            }
        elif e["type"] == "vote_cast" and current_vote:
            current_vote["votes"][e["agent"]] = {
                "vote": e["data"].get("vote", "ABSTAIN"),
                "reasoning": e["data"].get("reasoning", ""),
            }
        elif e["type"] == "vote_result":
            if current_vote:
                current_vote["result"] = e["data"].get("result", "")
                current_vote["tally"] = e["data"].get("tally", {})
                votes.append(current_vote)
                current_vote = None

    with open(out_path, "w") as f:
        json.dump(votes, f, indent=2)


def derive_summary(events: list, out_path: str):
    """Generate quick summary text."""
    sim_start = next((e for e in events if e["type"] == "sim_start"), None)
    sim_end = next((e for e in events if e["type"] == "sim_end"), None)

    with open(out_path, "w") as f:
        f.write("Brook Farm Simulation — Summary\n")
        f.write("=" * 40 + "\n\n")

        if sim_start:
            d = sim_start["data"]
            f.write(f"Model: {d.get('model', '?')}\n")
            f.write(f"Agents: {', '.join(d.get('agents', []))}\n")

        if sim_end:
            d = sim_end["data"]
            fs = d.get("final_state", {})
            f.write(f"Rounds: {d.get('rounds_completed', '?')}\n")
            f.write(f"Final: Food={fs.get('food', '?')}, Money=${fs.get('money', '?')}, Morale={fs.get('morale', '?')}%\n")
            f.write(f"Departed: {', '.join(d.get('departed', [])) or 'None'}\n")
            f.write(f"Survived: {', '.join(d.get('survived', [])) or 'None'}\n")
            f.write(f"Total events: {d.get('total_events', '?')}\n")
            f.write(f"LLM calls: {d.get('total_llm_calls', '?')}\n")
            f.write(f"Wall time: {d.get('wall_time_seconds', '?')}s\n")

        f.write("\n")

        # Action counts per agent
        action_counts = {}
        for e in events:
            if e["type"] == "action":
                name = e["agent"]
                action = e["data"].get("chosen_action", "?")
                if name not in action_counts:
                    action_counts[name] = {}
                action_counts[name][action] = action_counts[name].get(action, 0) + 1

        if action_counts:
            f.write("Action counts per agent:\n")
            for name, counts in sorted(action_counts.items()):
                f.write(f"  {name}:\n")
                for action, count in sorted(counts.items(), key=lambda x: -x[1]):
                    f.write(f"    {action}: {count}\n")

        # Key moments
        key_moments = [e for e in events if e["type"] == "key_moment"]
        if key_moments:
            f.write("\nKey moments:\n")
            for e in key_moments:
                f.write(f"  Round {e['round']} ({e.get('date', '?')}): {e['agent']} — {e['data'].get('description', '')} [{e['data'].get('emotion', '')}]\n")

        # Departures
        departures = [e for e in events if e["type"] == "agent_departed"]
        if departures:
            f.write("\nDepartures:\n")
            for e in departures:
                d = e["data"]
                f.write(f"  {e['agent']} — Round {e['round']} ({e.get('date', '?')}), satisfaction: {d.get('final_satisfaction', '?')}\n")
                if d.get("parting_words"):
                    f.write(f'    "{d["parting_words"]}"\n')


def derive_all(events_path: str):
    """Derive all outputs from events.jsonl."""
    run_dir = os.path.dirname(events_path)
    events = load_events(events_path)

    print(f"Loaded {len(events)} events from {events_path}")

    derive_narrative(events, os.path.join(run_dir, "narrative.md"))
    print("  -> narrative.md")

    derive_characters(events, os.path.join(run_dir, "characters.json"))
    print("  -> characters.json")

    derive_metrics(events, os.path.join(run_dir, "metrics.csv"))
    print("  -> metrics.csv")

    derive_conversations(events, os.path.join(run_dir, "conversations.json"))
    print("  -> conversations.json")

    derive_votes(events, os.path.join(run_dir, "votes.json"))
    print("  -> votes.json")

    derive_summary(events, os.path.join(run_dir, "summary.txt"))
    print("  -> summary.txt")

    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python derive.py <events.jsonl> [type]")
        print("Types: narrative, characters, metrics, conversations, votes, summary, all (default)")
        sys.exit(1)

    events_path = sys.argv[1]
    derive_type = sys.argv[2] if len(sys.argv) > 2 else "all"

    if not os.path.exists(events_path):
        print(f"Error: {events_path} not found")
        sys.exit(1)

    events = load_events(events_path)
    run_dir = os.path.dirname(events_path)

    if derive_type == "all":
        derive_all(events_path)
    elif derive_type == "narrative":
        derive_narrative(events, os.path.join(run_dir, "narrative.md"))
    elif derive_type == "characters":
        derive_characters(events, os.path.join(run_dir, "characters.json"))
    elif derive_type == "metrics":
        derive_metrics(events, os.path.join(run_dir, "metrics.csv"))
    elif derive_type == "conversations":
        derive_conversations(events, os.path.join(run_dir, "conversations.json"))
    elif derive_type == "votes":
        derive_votes(events, os.path.join(run_dir, "votes.json"))
    elif derive_type == "summary":
        derive_summary(events, os.path.join(run_dir, "summary.txt"))
    else:
        print(f"Unknown type: {derive_type}")
        sys.exit(1)
