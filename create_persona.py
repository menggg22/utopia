#!/usr/bin/env python3
"""
Interactive wizard to create a community persona file.

Usage: python create_persona.py
"""

import json
import os
import sys


def ask(prompt, default=None, required=True):
    """Ask a question, return the answer."""
    suffix = f" [{default}]" if default else ""
    while True:
        answer = input(f"  {prompt}{suffix}: ").strip()
        if not answer and default:
            return default
        if not answer and required:
            print("    (required)")
            continue
        return answer


def ask_int(prompt, default=None):
    while True:
        val = ask(prompt, default=str(default) if default else None)
        try:
            return int(val)
        except ValueError:
            print("    (enter a number)")


def ask_list(prompt, default=None):
    """Ask for comma-separated items."""
    raw = ask(prompt, default=", ".join(default) if default else None)
    return [s.strip() for s in raw.split(",") if s.strip()]


def ask_yn(prompt, default="y"):
    val = ask(prompt, default=default, required=False)
    return val.lower() in ("y", "yes", "")


def ask_passions(available_actions):
    """Ask which actions sustain this person."""
    print(f"\n  Available actions: {', '.join(available_actions)}")
    print("  Which actions sustain them? (give bonus satisfaction)")
    passions = {}
    while True:
        action = ask("Action name (or 'done')", required=False)
        if not action or action.lower() == "done":
            break
        action = action.upper()
        if action not in available_actions:
            print(f"    (not in available actions — add it anyway? y/n)")
            if not ask_yn("Add anyway?", "n"):
                continue
        bonus = ask_int("Bonus satisfaction (1-5)", default=3)
        passions[action] = max(1, min(5, bonus))
    return passions


def create_agent(num, available_actions):
    """Walk through creating one agent."""
    print(f"\n{'─'*50}")
    print(f"  MEMBER #{num}")
    print(f"{'─'*50}")

    name = ask("Full name")
    role = ask("Role in the community", default="Member")
    age = ask_int("Age", default=30)

    print("\n  Tell me about them (1-3 sentences each):")
    background = ask("Background (who are they?)")
    motivation = ask("Why did they join?")
    personality = ask("Personality (how do they act under pressure?)")
    skills = ask_list("Skills (comma-separated)", default=["general"])
    private_goal = ask("Private goal (what do they secretly want?)")

    passions = ask_passions(available_actions)

    return name, {
        "role": role,
        "age": age,
        "background": background,
        "motivation": motivation,
        "personality": personality,
        "skills": skills,
        "private_goal": private_goal,
        "passions": passions,
    }


def create_actions():
    """Ask if they want custom actions or the defaults."""
    defaults = {
        "FARM":     {"food": 8, "satisfaction": -3, "prompt": "Work the fields (+food, physically exhausting)"},
        "TEACH":    {"money": 10, "satisfaction": 5, "prompt": "Run school classes (+money, intellectually fulfilling)"},
        "BUILD":    {"money": -30, "satisfaction": 2, "prompt": "Construction (-$30, +building)", "arg": "<what>"},
        "PROPOSE":  {"prompt": "Suggest a rule — ALL members will vote on it", "arg": "<rule>"},
        "SPEAK":    {"prompt": "Address the community", "arg": "<topic>"},
        "ORGANIZE": {"satisfaction": 5, "prompt": "Plan a cultural/social event", "arg": "<event>"},
        "TRADE":    {"money": 15, "satisfaction": 2, "prompt": "Sell goods to visitors (+money)"},
        "REPAIR":   {"money": -10, "satisfaction": 2, "prompt": "Fix a deteriorating building (-$10)", "arg": "<building>"},
        "REST":     {"satisfaction": 2, "prompt": "Personal time"},
        "WRITE":    {"satisfaction": 8, "prompt": "Work on personal writing/art"},
        "LEAVE":    {"prompt": "Permanently depart the community (irreversible)"},
    }

    print("\n  The default actions are:")
    for name, a in defaults.items():
        print(f"    {name}: {a['prompt']}")

    if ask_yn("\n  Use these defaults? (y=keep, n=customize)", "y"):
        return defaults

    print("\n  Let's build your action list.")
    print("  PROPOSE, SPEAK, REST, and LEAVE are always included.\n")

    actions = {
        "PROPOSE": defaults["PROPOSE"],
        "SPEAK":   defaults["SPEAK"],
        "REST":    defaults["REST"],
        "LEAVE":   defaults["LEAVE"],
    }

    while True:
        name = ask("Action name (e.g. FARM, CODE, PAINT) or 'done'", required=False)
        if not name or name.lower() == "done":
            break
        name = name.upper()
        prompt_text = ask("What does it do? (shown to agents)")
        food = ask_int("Food effect (0 for none)", default=0)
        money = ask_int("Money effect (0 for none)", default=0)
        sat = ask_int("Satisfaction effect (-10 to +10)", default=0)
        has_arg = ask_yn("Does it take an argument? (e.g. BUILD <what>)", "n")

        action = {"prompt": prompt_text}
        if food: action["food"] = food
        if money: action["money"] = money
        if sat: action["satisfaction"] = sat
        if has_arg:
            arg = ask("Argument placeholder (e.g. <what>)", default="<detail>")
            action["arg"] = arg

        actions[name] = action
        print(f"    Added: {name}")

    return actions


RELATIONSHIP_PRESETS = {
    "Brook Farm (1841)": [
        {"pair": ["George Ripley", "Sophia Ripley"], "type": "married", "initial_trust": 8},
    ],
}


def create_relationships(agent_names, community_name=None):
    """Ask about special relationships."""
    relationships = []
    presets = RELATIONSHIP_PRESETS.get(community_name, [])

    # Filter presets to only include members actually in the community
    valid_presets = [r for r in presets if r["pair"][0] in agent_names and r["pair"][1] in agent_names]

    if valid_presets:
        print("\n  Suggested relationships:")
        for i, r in enumerate(valid_presets):
            print(f"    [{i+1}] {r['pair'][0]} ↔ {r['pair'][1]}: {r['type']} (trust {r['initial_trust']}/10)")
        print(f"    [A] Add all")
        print(f"    [N] Skip")
        print()

        rel_choice = ask("Pick (e.g. '1,2' or 'A' or 'N')", default="A")
        if rel_choice.upper() == "A":
            relationships = list(valid_presets)
            for r in relationships:
                print(f"    Added: {r['pair'][0]} ↔ {r['pair'][1]}")
        elif rel_choice.upper() != "N":
            for key in rel_choice.split(","):
                idx = int(key.strip()) - 1
                if 0 <= idx < len(valid_presets):
                    relationships.append(valid_presets[idx])
                    r = valid_presets[idx]
                    print(f"    Added: {r['pair'][0]} ↔ {r['pair'][1]}")

    print(f"\n  Add custom relationships?")
    print(f"  Members: {', '.join(agent_names)}")
    print(f"  (trust: 1=hostile, 5=neutral, 8=close, 10=unconditional)")
    while True:
        if not ask_yn("  Add a relationship?", "n"):
            break
        a = ask("Person 1")
        if a not in agent_names:
            # fuzzy match
            matches = [n for n in agent_names if a.lower() in n.lower()]
            if matches:
                a = matches[0]
                print(f"    → matched: {a}")
            else:
                print(f"    (not found, skipping)")
                continue
        b = ask("Person 2")
        if b not in agent_names:
            matches = [n for n in agent_names if b.lower() in n.lower()]
            if matches:
                b = matches[0]
                print(f"    → matched: {b}")
            else:
                print(f"    (not found, skipping)")
                continue
        rel_type = ask("Relationship (e.g. married, rivals, mentor-student, ex-friends)", default="close")
        trust = ask_int("Starting trust (1-10)", default=7)
        relationships.append({"pair": [a, b], "type": rel_type, "initial_trust": trust})

    return relationships


def main():
    PRESETS = {
        "1": {
            "name": "Brook Farm (1841)",
            "desc": "The original — transcendentalist commune in Massachusetts",
            "setting": "Brook Farm, a utopian community in West Roxbury, Massachusetts, in the 1840s.",
        },
        "2": {
            "name": "Custom",
            "desc": "Design your own utopian community from scratch",
            "setting": None,
        },
    }

    print()
    print("=" * 50)
    print("  UTOPIA LAB — Community Creator")
    print("=" * 50)
    print()
    print("  Choose a starting point, or design from scratch:")
    print()
    for key, preset in PRESETS.items():
        print(f"  [{key}] {preset['name']}")
        print(f"      {preset['desc']}")
    print()

    choice = ask("Pick a number (1-2)", default="1")
    preset = PRESETS.get(choice, PRESETS["2"])

    if preset["setting"]:
        name = preset["name"]
        description = preset["desc"]
        setting = preset["setting"]
        print(f"\n  Starting with: {name}")
        print(f"  Setting: {setting}")
        if ask_yn("  Customize the name/setting?", "n"):
            name = ask("Community name", default=name)
            description = ask("One-line description", default=description)
            setting = ask("Setting", default=setting)
    else:
        print("\n  Let's design your community from scratch.\n")
        name = ask("Community name", default="My Community")
        description = ask("One-line description")
        setting = ask("Setting (where and when?)")

    # Environment
    print("\n  Starting resources:")
    food = ask_int("Food (default 100)", default=100)
    money = ask_int("Money (default 500)", default=500)
    morale = ask_int("Morale % (default 80)", default=80)

    # Actions
    actions = create_actions()
    available_actions = list(actions.keys())

    # Historical members by community type
    MEMBER_PRESETS = {
        "Brook Farm (1841)": {
            "1": ("George Ripley", {
                "role": "Founder and Leader", "age": 38,
                "background": "Former Unitarian minister. Left the ministry to build a community that balances intellectual life with manual labor. Married to Sophia.",
                "motivation": "Needs this to succeed to justify leaving the ministry. Sees himself as responsible for everyone.",
                "personality": "Idealistic, persuasive, visionary. Struggles with practical matters. Takes on too much guilt.",
                "skills": ["theology", "philosophy", "teaching", "fundraising"],
                "private_goal": "Prove that transcendentalist ideals work in practice.",
                "passions": {"ORGANIZE": 3, "SPEAK": 3},
            }),
            "2": ("Nathaniel Hawthorne", {
                "role": "Trustee of Finance, Writer", "age": 37,
                "background": "Published author. Joined hoping to save money to marry, not for ideology.",
                "motivation": "Save money for marriage. Doesn't believe in the community's ideals.",
                "personality": "Sardonic, observant, private. Cannot write here. Hands covered in blisters.",
                "skills": ["writing", "observation", "financial management"],
                "private_goal": "Save enough money to marry. Will leave if the farm doesn't help.",
                "passions": {"WRITE": 3},
            }),
            "3": ("Sophia Ripley", {
                "role": "Head of School", "age": 38,
                "background": "Highly educated. Married to George. Runs the school — the only reliable income.",
                "motivation": "Committed to women's education. The school is her domain.",
                "personality": "Dedicated, tireless, principled. The practical backbone.",
                "skills": ["teaching", "languages", "school administration"],
                "private_goal": "Build a school that proves women can lead serious institutions.",
                "passions": {"TEACH": 3},
            }),
            "4": ("Charles Dana", {
                "role": "Editor, Finance Manager", "age": 22,
                "background": "Self-made. Speaks ten languages. Arrived with no money and enormous energy.",
                "motivation": "Part idealism, part opportunity. Platform for journalism.",
                "personality": "Energetic, competent, pragmatic. The 'get things done' person.",
                "skills": ["journalism", "editing", "financial management"],
                "private_goal": "Learn everything possible. Brook Farm is a launching pad.",
                "passions": {"TRADE": 3, "WRITE": 3},
            }),
            "5": ("John Sullivan Dwight", {
                "role": "Music Teacher", "age": 28,
                "background": "Failed minister turned music critic. Passion is Beethoven.",
                "motivation": "Escape from ministry. Found his element as the cultural heart.",
                "personality": "Sensitive, cultured, devoted to beauty. Not practical.",
                "skills": ["music", "Latin", "cultural events", "teaching"],
                "private_goal": "Create a life where music is central. The farming bores him.",
                "passions": {"ORGANIZE": 5},
            }),
        },
    }

    # "What if?" extra characters — fictional but historically plausible
    EXTRA_MEMBERS = {
        "Brook Farm (1841)": {
            "F": ("Thomas Reed", {
                "role": "Farmer", "age": 34,
                "background": "Third-generation farmer from Concord. No college education. Joined because his wife died last winter and he needed community. Knows soil, weather, livestock, carpentry. Has never read Emerson.",
                "motivation": "Lonely and grieving. The community offers companionship. Doesn't care about transcendentalism — cares whether the potatoes are in the ground by May.",
                "personality": "Quiet, practical, patient. Finds the intellectuals baffling but not unkind. Wakes before dawn out of habit, not virtue.",
                "skills": ["farming", "carpentry", "animal husbandry", "weather reading"],
                "private_goal": "Find a reason to keep living after his wife's death. The community is not what he expected — too much talk, not enough work — but the people are kind.",
                "passions": {"FARM": 5, "REPAIR": 3},
            }),
            "J": ("Eliza Crane", {
                "role": "Journalist", "age": 29,
                "background": "Reporter for the Boston Daily Advertiser. Editor sent her to write a three-part exposé on 'the transcendentalist folly.' Educated, sharp, privately envious of people who believe in something.",
                "motivation": "Get the story. File three devastating pieces and earn a promotion. She did not come here to be convinced.",
                "personality": "Witty, perceptive, guarded. Asks questions that sound friendly but aren't. Takes notes on everything. Laughs at idealism until it starts working.",
                "skills": ["writing", "investigation", "interviewing", "shorthand"],
                "private_goal": "Write the story that makes her career. But if the commune actually works... that's a better story than failure.",
                "passions": {"WRITE": 5},
            }),
            "M": ("Silas Warren", {
                "role": "Merchant", "age": 42,
                "background": "Boston dry goods merchant. Moderate success, no debts. Visited Brook Farm out of curiosity and saw an opportunity — cheap goods from the farm, city customers willing to pay premium for 'utopian' products.",
                "motivation": "Part curiosity, part business instinct. Thinks the transcendentalists are terrible with money. Believes he can make the commune profitable if they'd listen.",
                "personality": "Shrewd, sociable, impatient with philosophy. Counts everything. Generous with practical advice, dismissive of abstract ideals.",
                "skills": ["trade", "negotiation", "accounting", "supply chains"],
                "private_goal": "Prove that idealism and profit aren't enemies. Secretly wants to be respected by the intellectuals, not just tolerated as 'the money man'.",
                "passions": {"TRADE": 5, "ORGANIZE": 2},
            }),
        },
    }

    # Members
    print(f"\n{'='*50}")
    print("  COMMUNITY MEMBERS")
    print(f"{'='*50}")

    agents = {}
    member_presets = MEMBER_PRESETS.get(name, {})
    extra_presets = EXTRA_MEMBERS.get(name, {})

    if member_presets:
        print(f"\n  Historical members of {name}:")
        for key, (pname, pdata) in member_presets.items():
            print(f"    [{key}] {pname} — {pdata['role']}")
        print(f"\n    [A] Add all historical members")
        print(f"    [C] Skip — create from scratch")
        print()

        member_choice = ask("Pick members (e.g. '1,2,3' or 'A' or 'C')", default="A")

        if member_choice.upper() == "A":
            for key, (pname, pdata) in member_presets.items():
                agents[pname] = dict(pdata)
                print(f"    Added: {pname} ({pdata['role']})")
        elif member_choice.upper() != "C":
            for key in member_choice.split(","):
                key = key.strip()
                if key in member_presets:
                    pname, pdata = member_presets[key]
                    agents[pname] = dict(pdata)
                    print(f"    Added: {pname} ({pdata['role']})")

        # Customize existing members
        if agents:
            print(f"\n  {len(agents)} members added.")
            print(f"\n  Want to customize the composition?")
            print(f"    [R] Remove a member (counterfactual: 'what without Hawthorne?')")
            print(f"    [E] Edit a member's persona")
            print(f"    [+] Add a new member")
            print(f"    [D] Done — keep as is")
            print()

            while True:
                action = ask("Action (R/E/+/D)", default="D")

                if action.upper() == "D":
                    break

                elif action.upper() == "R":
                    print(f"    Current members: {', '.join(agents.keys())}")
                    to_remove = ask("Remove who?", required=False)
                    if not to_remove:
                        continue
                    # fuzzy match
                    matches = [n for n in agents if to_remove.lower() in n.lower()]
                    if matches:
                        removed = matches[0]
                        del agents[removed]
                        print(f"    Removed: {removed} ({len(agents)} remaining)")
                    else:
                        print(f"    (not found)")

                elif action.upper() == "E":
                    print(f"    Current members: {', '.join(agents.keys())}")
                    to_edit = ask("Edit who?", required=False)
                    if not to_edit:
                        continue
                    matches = [n for n in agents if to_edit.lower() in n.lower()]
                    if not matches:
                        print(f"    (not found)")
                        continue
                    edit_name = matches[0]
                    agent = agents[edit_name]
                    print(f"\n    Editing {edit_name}:")
                    print(f"    Current role: {agent['role']}")
                    print(f"    Current background: {agent['background']}")
                    print(f"    Current motivation: {agent['motivation']}")
                    print(f"    Current personality: {agent['personality']}")
                    print(f"    Current private goal: {agent['private_goal']}")
                    print(f"\n    Press Enter to keep current value, or type new value:")
                    new_role = ask("Role", default=agent["role"])
                    new_bg = ask("Background", default=agent["background"])
                    new_mot = ask("Motivation", default=agent["motivation"])
                    new_pers = ask("Personality", default=agent["personality"])
                    new_goal = ask("Private goal", default=agent["private_goal"])
                    agent["role"] = new_role
                    agent["background"] = new_bg
                    agent["motivation"] = new_mot
                    agent["personality"] = new_pers
                    agent["private_goal"] = new_goal
                    print(f"    Updated: {edit_name}")

                elif action == "+":
                    if extra_presets:
                        print(f"\n    'What if?' characters (fictional but historically plausible):")
                        for key, (pname, pdata) in extra_presets.items():
                            if pname not in agents:
                                print(f"      [{key}] {pname} — {pdata['role']}")
                        print(f"      [N] Create new from scratch")
                        print()
                        add_choice = ask("Pick", default="N")

                        if add_choice.upper() in extra_presets and extra_presets[add_choice.upper()][0] not in agents:
                            pname, pdata = extra_presets[add_choice.upper()]
                            agents[pname] = dict(pdata)
                            print(f"    Added: {pname} ({pdata['role']})")
                            continue

                    agent_name, agent_data = create_agent(len(agents) + 1, available_actions)
                    agents[agent_name] = agent_data

    if not agents:
        print(f"\n  Let's create your community members.")
        print(f"  You need at least 2. Most interesting with 4-6.")
        num = 1
        while True:
            agent_name, agent_data = create_agent(num, available_actions)
            agents[agent_name] = agent_data
            num += 1
            if num > 2:
                if not ask_yn(f"\n  Add another member? ({len(agents)} so far)", "y"):
                    break
            else:
                print(f"\n  (need at least 2 members)")

    # Relationships
    relationships = create_relationships(list(agents.keys()), community_name=name)

    # Build the output
    output = {
        "name": name,
        "description": description,
        "setting": setting,
        "environment": {
            "food": food,
            "money": money,
            "morale": morale,
        },
        "actions": actions,
        "relationships": relationships,
        "agents": agents,
    }

    # Save
    default_filename = name.lower().replace(" ", "_") + ".json"
    filename = ask(f"\n  Save as", default=f"personas/{default_filename}")

    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  Saved to {filename}")
    print(f"\n  Run it:")
    print(f"    python simulate_v3.py 30 --personas {filename}")
    print()


if __name__ == "__main__":
    main()
