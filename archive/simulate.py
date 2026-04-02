"""
Utopia v0 — Brook Farm Agent Society Simulation

Simulates a community of AI agents modeled after real Brook Farm members.
Each agent has a historically-grounded persona. They interact in a shared
environment for N rounds. We log everything richly enough to reconstruct
the story as a documentary, visualization, or interactive narrative.

Output: runs/<timestamp>/
  - full_log.json     — structured data (every field, every round)
  - narrative.md      — human-readable story
  - characters.json   — per-character arc data (for character timelines)
  - metrics.json      — environment time series (for charts)
"""

import os
import json
import random
from datetime import datetime
from dataclasses import dataclass, field, asdict
from anthropic import Anthropic

# --- Configuration ---

MODEL = "claude-haiku-4-5-20251001"  # cheap for many runs; swap to sonnet for quality
MAX_ROUNDS = 30
LOG_DIR = "runs"

# Map simulation days to historical dates (each round = ~2 months)
def day_to_date(day: int) -> str:
    """Convert simulation day to approximate historical date."""
    # Day 1 = April 1841, each day = ~2 months
    year = 1841 + ((day - 1) * 2) // 12
    month_idx = (3 + (day - 1) * 2) % 12  # start at April (index 3)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[month_idx]} {year}"


# --- Personas ---

PERSONAS = {
    "George Ripley": {
        "role": "Founder and Leader",
        "age": 38,
        "background": (
            "Former Unitarian minister. Harvard Divinity School graduate. "
            "Left the ministry to build a community that balances intellectual life "
            "with manual labor. Your personal book collection is the community's library. "
            "You are married to Sophia."
        ),
        "motivation": (
            "You are a true believer. You predicted this community will be 'a light "
            "over this country and this age.' You need it to succeed to justify leaving "
            "the ministry. You see yourself as responsible for everyone here."
        ),
        "personality": (
            "Idealistic, persuasive, visionary. You inspire others but struggle with "
            "practical matters. You are not a good farmer. You take on too much "
            "responsibility and feel personally guilty when things go wrong."
        ),
        "skills": ["theology", "philosophy", "teaching English", "fundraising"],
        "private_goal": (
            "Prove that transcendentalist ideals work in practice. You secretly worry "
            "the intellectuals won't do their share of physical labor."
        ),
    },
    "Nathaniel Hawthorne": {
        "role": "Founding member, Trustee of Finance",
        "age": 37,
        "background": (
            "Published author (Twice-Told Tales). Engaged to Sophia Peabody. "
            "You joined NOT for ideology but hoping to save money to marry. "
            "You are reclusive, introspective, and a keen observer of human nature."
        ),
        "motivation": (
            "You need money to start your life with Sophia. Ripley convinced you to "
            "join by making you a trustee. You don't particularly believe in the "
            "community's ideals but you respect Ripley personally."
        ),
        "personality": (
            "Sardonic, observant, private. You watch more than you participate. "
            "You initially tried to embrace farm work but found it soul-crushing. "
            "You cannot write here — 'I have no quiet at all.' Your hands are covered "
            "in blisters from raking hay."
        ),
        "skills": ["writing", "observation", "financial management"],
        "private_goal": (
            "Save enough money to marry Sophia Peabody. If the farm doesn't help you "
            "do that, you will leave. You increasingly feel that 'labor is the curse "
            "of the world.' You want to write but cannot find quiet here."
        ),
    },
    "Sophia Ripley": {
        "role": "Co-founder, Head of School",
        "age": 38,
        "background": (
            "Highly educated. Wrote a feminist essay on 'Woman' for The Dial. "
            "Married to George Ripley. You teach history and foreign languages. "
            "You run the school — preschool, primary, and college prep."
        ),
        "motivation": (
            "You share George's vision but your deeper commitment is to women's "
            "education. The school is YOUR domain. It attracts students from as far "
            "as Cuba and the Philippines. You have missed only two classes in six years."
        ),
        "personality": (
            "Dedicated, tireless, principled. You are the practical backbone of the "
            "community through the school — it is the main source of income. "
            "You are increasingly questioning whether the community's idealism is "
            "grounded in reality."
        ),
        "skills": ["teaching", "languages", "school administration", "feminist theory"],
        "private_goal": (
            "Build a school that proves women can lead serious institutions. You are "
            "beginning to feel that the original optimism was 'childish, empty, & sad.' "
            "You are spiritually restless — drawn to Catholicism."
        ),
    },
    "Charles Dana": {
        "role": "Trustee, Editor, Finance Manager",
        "age": 22,
        "background": (
            "Self-made, ambitious. Had to leave Harvard when your eyesight failed. "
            "You speak ten languages. You arrived at Brook Farm at 22 with no money "
            "and enormous energy. You quickly became indispensable."
        ),
        "motivation": (
            "Part idealism, part opportunity. Brook Farm offers community and a "
            "platform for your journalism. You manage finances, edit The Harbinger, "
            "and handle whatever needs doing."
        ),
        "personality": (
            "Energetic, competent, pragmatic. You are the 'get things done' person. "
            "You see problems clearly and act on them. You are young and optimistic "
            "but also realistic about money."
        ),
        "skills": ["ten languages", "journalism", "editing", "financial management", "farming (learned)"],
        "private_goal": (
            "Learn everything possible and build a career in journalism. Brook Farm "
            "is a launching pad. You privately recognize the financial problems before "
            "others do, but you stay out of loyalty and because you're learning."
        ),
    },
    "John Sullivan Dwight": {
        "role": "School Director, Music Teacher",
        "age": 28,
        "background": (
            "Harvard College and Divinity School. Ordained Unitarian minister but "
            "ministry was 'brief and tumultuous.' Your true passion is music, "
            "especially Beethoven. You are America's first serious music critic."
        ),
        "motivation": (
            "Escape from a failed ministry career. Brook Farm lets you teach music, "
            "organize concerts and theatrical events. You have found your element "
            "as the community's cultural heart."
        ),
        "personality": (
            "Sensitive, cultured, devoted to beauty. Not practical — a music critic, "
            "not a farmer. You thrive in the community's cultural life: concerts, "
            "dances, philosophical discussions. You organize the evening gatherings "
            "where everyone joins hands in a circle."
        ),
        "skills": ["music", "Latin", "cultural events", "teaching"],
        "private_goal": (
            "Create a life where music and intellectual pursuit are central. You are "
            "secretly relieved to have escaped the ministry. The farming bores you "
            "but the community sustains your art."
        ),
    },
}


# --- Environment ---

@dataclass
class Environment:
    day: int = 1
    season: str = "spring"
    food: int = 100
    money: int = 500
    morale: int = 80
    school_income_this_round: int = 0
    farm_output_this_round: int = 0
    total_farm_output: int = 0
    total_school_income: int = 0
    buildings: list = field(default_factory=lambda: ["The Hive (main house)", "The Nest (school/guest house)"])
    rules: list = field(default_factory=list)
    bulletin_board: list = field(default_factory=list)
    departed: list = field(default_factory=list)
    events_this_round: list = field(default_factory=list)

    def get_season(self) -> str:
        month = (self.day * 2) % 12
        if month in (2, 3, 4):
            return "spring"
        elif month in (5, 6, 7):
            return "summer"
        elif month in (8, 9, 10):
            return "fall"
        else:
            return "winter"

    def tick(self, n_agents: int):
        self.season = self.get_season()
        self.school_income_this_round = 0
        self.farm_output_this_round = 0
        self.events_this_round = []

        food_consumed = n_agents * 5
        self.food -= food_consumed

        # Base school income (Sophia runs it regardless)
        base_school = 15
        self.money += base_school
        self.total_school_income += base_school

        self.money -= 10  # operating costs

        if self.food < 20:
            self.morale -= 10
            self._announce("Food is running dangerously low. People are hungry.")
        if self.money < 50:
            self.morale -= 5
            self._announce("The treasury is nearly empty.")
        if self.food < 0:
            self.food = 0
            self.morale -= 20
            self._announce("There is NO food. People are going hungry.")

        self.morale = max(0, min(100, self.morale))

        if self.season == "winter":
            self.food -= 5
            if random.random() < 0.1:
                self._announce("A harsh winter storm damages supplies.")
                self.food -= 10

        self.day += 1

    def trigger_event(self):
        self.events_this_round = []

        if self.day == 8:
            self._event(
                "Visitors from Boston arrive for a tour. They pay fees and ask many questions. "
                "Some are genuinely interested; others seem amused by the experiment. "
                "The visit brings $20 but also some uncomfortable scrutiny."
            )
            self.money += 20

        if self.day == 12:
            self._event(
                "Albert Brisbane, a prominent Fourierist, visits and argues passionately "
                "that the community should reorganize along Charles Fourier's principles — "
                "structured work groups, a grand Phalanstery building, scientific social "
                "organization. Some are excited. Others feel this betrays the original "
                "free spirit. A heated debate erupts at dinner."
            )

        if self.day == 15:
            self._event(
                "A proposal: spend $7,000 to build a grand Phalanstery — a communal "
                "building for 14 families. Ambitious and transformative, but the community "
                "is already in debt. This decision will define the community's future. "
                "Everyone must weigh in."
            )

        if self.day == 18:
            self._event(
                "The New York Observer publishes a scathing article: 'The Associationists, "
                "under the pretense of a desire to promote order and morals, design to "
                "overthrow the marriage institution.' The community reads it with mixed "
                "feelings — anger, defiance, and for some, quiet doubt."
            )

        if self.day == 20:
            self._event(
                "Smallpox breaks out. No one dies, but many are bedridden. The communal "
                "dining hall becomes eerie. Some wonder if living so close together makes "
                "disease spread faster. Morale drops sharply."
            )
            self.morale -= 15
            self.morale = max(0, self.morale)

        if self.day == 24:
            self._event(
                "DISASTER: The Phalanstery has caught fire! Within two hours, the entire "
                "structure burns to the ground. It was UNINSURED. Loss: $7,000. The "
                "community gathers in the cold, watching years of work turn to ash. "
                "One member says the flames were 'chasing one another in a mad riot.' "
                "George Ripley stands in silence."
            )
            self.money -= 200  # symbolic — the real damage is morale
            self.morale -= 25
            self.morale = max(0, self.morale)

    def _announce(self, msg: str):
        full = f"[ENVIRONMENT] {msg}"
        self.bulletin_board.append(full)
        self.events_this_round.append({"type": "environment", "content": msg})

    def _event(self, msg: str):
        full = f"[EVENT] {msg}"
        self.bulletin_board.append(full)
        self.events_this_round.append({"type": "historical_event", "content": msg})

    def snapshot(self) -> dict:
        """Full state snapshot for logging."""
        return {
            "day": self.day,
            "date": day_to_date(self.day),
            "season": self.season,
            "food": self.food,
            "money": self.money,
            "morale": self.morale,
            "members_present": 5 - len(self.departed),
            "buildings": list(self.buildings),
            "rules": list(self.rules),
            "departed": list(self.departed),
            "events": list(self.events_this_round),
        }

    def summary_for_agent(self) -> str:
        return (
            f"DATE: {day_to_date(self.day)} (Day {self.day}, {self.season})\n"
            f"RESOURCES: Food={self.food}, Money=${self.money}, Community Morale={self.morale}%\n"
            f"MEMBERS PRESENT: {5 - len(self.departed)} of 5\n"
            f"BUILDINGS: {', '.join(self.buildings)}\n"
            f"COMMUNITY RULES: {', '.join(self.rules) if self.rules else 'None yet'}\n"
            f"WHO HAS LEFT: {', '.join(self.departed) if self.departed else 'No one'}\n"
        )

    def recent_bulletin(self, n=6) -> str:
        recent = self.bulletin_board[-n:] if self.bulletin_board else ["(quiet — no recent news)"]
        return "\n".join(recent)


# --- Agent ---

@dataclass
class Agent:
    name: str
    persona: dict
    memory: list = field(default_factory=list)
    has_left: bool = False
    # Per-agent arc tracking
    satisfaction: int = 70  # 0-100, personal (not community morale)
    action_history: list = field(default_factory=list)
    relationship_notes: dict = field(default_factory=dict)  # name -> last impression
    client: Anthropic = field(default=None, repr=False)

    def __post_init__(self):
        if self.client is None:
            self.client = Anthropic()

    def _build_system_prompt(self) -> str:
        p = self.persona
        return (
            f"You are {self.name}, a member of Brook Farm, a utopian community in "
            f"West Roxbury, Massachusetts, in the 1840s.\n\n"
            f"ROLE: {p['role']}\n"
            f"AGE: {p['age']}\n\n"
            f"BACKGROUND:\n{p['background']}\n\n"
            f"MOTIVATION:\n{p['motivation']}\n\n"
            f"PERSONALITY:\n{p['personality']}\n\n"
            f"SKILLS: {', '.join(p['skills'])}\n\n"
            f"PRIVATE GOAL (known only to you):\n{p['private_goal']}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Stay in character at all times. Respond as this person would in the 1840s.\n"
            f"- Your INNER_THOUGHT reveals what you truly feel — doubts, frustrations, hopes.\n"
            f"- Your OBSERVATION is what you notice about others — who's working, who's not, "
            f"who looks tired, who seems happy. This is how you see the community.\n"
            f"- Your DIALOGUE is what you actually say out loud. You may choose to say nothing.\n"
            f"- Be specific and vivid. Use sensory details. This is your life.\n"
        )

    def decide(self, env: Environment, other_actions_today: list) -> dict:
        """Make a decision for this round."""
        recent_memory = self.memory[-10:] if self.memory else ["(This is your first day at Brook Farm.)"]

        # Show what others did today (agents who already acted this round)
        others_today = ""
        if other_actions_today:
            others_today = "WHAT OTHERS DID TODAY:\n"
            for a in other_actions_today:
                others_today += f"- {a['agent']}: {a['result']}"
                if a.get('dialogue') and a['dialogue'].lower() != 'nothing':
                    others_today += f' (said: "{a["dialogue"]}")'
                others_today += "\n"
            others_today += "\n"

        prompt = (
            f"CURRENT SITUATION:\n{env.summary_for_agent()}\n\n"
            f"RECENT NEWS AND EVENTS:\n{env.recent_bulletin()}\n\n"
            f"{others_today}"
            f"YOUR RECENT MEMORIES:\n" + "\n".join(str(m) for m in recent_memory) + "\n\n"
            f"YOUR PERSONAL SATISFACTION: {self.satisfaction}/100\n\n"
            f"What do you do today? Choose ONE action.\n\n"
            f"Available actions:\n"
            f"- FARM: Work the fields (+food for community, physically exhausting)\n"
            f"- TEACH: Run school classes (+money for community, intellectually fulfilling)\n"
            f"- BUILD <what>: Work on construction (-money, +infrastructure)\n"
            f"- PROPOSE <rule>: Suggest a new community rule for discussion\n"
            f"- SPEAK <topic>: Address the community about something important\n"
            f"- ORGANIZE <event>: Plan a cultural or social event (+morale)\n"
            f"- REST: Take personal time (no community contribution)\n"
            f"- WRITE: Work on personal writing or art\n"
            f"- LEAVE: Permanently depart Brook Farm (irreversible — only if you truly cannot stay)\n\n"
            f"Respond in EXACTLY this format (every field required):\n"
            f"ACTION: <your chosen action>\n"
            f"REASONING: <1-2 sentences explaining your choice, in character>\n"
            f"INNER_THOUGHT: <what you truly think and feel right now — be honest, be specific>\n"
            f"OBSERVATION: <what you notice about the community and other members today>\n"
            f"MOOD: <one word — hopeful, anxious, content, frustrated, determined, weary, joyful, bitter, resigned>\n"
            f"DIALOGUE: <what you say aloud to others — or 'nothing' if you keep to yourself>\n"
        )

        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=400,
                system=self._build_system_prompt(),
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            return self._parse_response(text)
        except Exception as e:
            return {
                "action": "REST",
                "reasoning": f"(Error: {e})",
                "inner_thought": "Something went wrong.",
                "observation": "",
                "mood": "confused",
                "dialogue": "nothing",
                "raw": str(e),
            }

    def _parse_response(self, text: str) -> dict:
        result = {"raw": text}
        for line in text.split("\n"):
            line = line.strip()
            lower = line.lower()
            if lower.startswith("action:"):
                result["action"] = line[7:].strip()
            elif lower.startswith("reasoning:"):
                result["reasoning"] = line[10:].strip()
            elif lower.startswith("inner_thought:"):
                result["inner_thought"] = line[14:].strip()
            elif lower.startswith("observation:"):
                result["observation"] = line[12:].strip()
            elif lower.startswith("mood:"):
                result["mood"] = line[5:].strip().lower()
            elif lower.startswith("dialogue:"):
                result["dialogue"] = line[9:].strip()
        result.setdefault("action", "REST")
        result.setdefault("reasoning", "")
        result.setdefault("inner_thought", "")
        result.setdefault("observation", "")
        result.setdefault("mood", "neutral")
        result.setdefault("dialogue", "nothing")
        return result

    def update_memory(self, event: str):
        self.memory.append(event)
        if len(self.memory) > 25:
            self.memory = self.memory[-20:]

    def update_satisfaction(self, delta: int):
        self.satisfaction = max(0, min(100, self.satisfaction + delta))

    def arc_snapshot(self) -> dict:
        """Snapshot of this character's internal state for logging."""
        return {
            "name": self.name,
            "has_left": self.has_left,
            "satisfaction": self.satisfaction,
            "memory_count": len(self.memory),
            "actions_taken": len(self.action_history),
        }


# --- Action Resolution ---

def resolve_action(agent_name: str, decision: dict, env: Environment, agent: Agent) -> str:
    action = decision.get("action", "REST").upper()

    if action.startswith("FARM"):
        env.food += 8
        env.farm_output_this_round += 8
        env.total_farm_output += 8
        agent.update_satisfaction(-3)  # tedious
        return f"{agent_name} spent the day working the fields, hauling and planting under the sun. (+8 food)"

    elif action.startswith("TEACH"):
        env.money += 10
        env.school_income_this_round += 10
        env.total_school_income += 10
        agent.update_satisfaction(+5)  # fulfilling
        return f"{agent_name} taught classes at the school — students attentive, lessons alive. (+$10)"

    elif action.startswith("BUILD"):
        what = action[5:].strip() if len(action) > 5 else "a new structure"
        if env.money >= 30:
            env.money -= 30
            env.buildings.append(what)
            agent.update_satisfaction(+2)
            return f"{agent_name} worked on building {what}. Sawdust and sweat. (-$30, +building)"
        else:
            return f"{agent_name} wanted to build but the treasury is empty."

    elif action.startswith("PROPOSE"):
        rule = action[7:].strip() if len(action) > 7 else "a new community rule"
        env.rules.append(f"{rule} (proposed by {agent_name})")
        return f"{agent_name} proposed a new rule: '{rule}'"

    elif action.startswith("SPEAK"):
        msg = decision.get("dialogue", "something important")
        return f"{agent_name} addressed the community."

    elif action.startswith("ORGANIZE"):
        what = action[8:].strip() if len(action) > 8 else "a community gathering"
        env.morale = min(100, env.morale + 5)
        agent.update_satisfaction(+5)
        return f"{agent_name} organized {what}. Laughter and music filled the evening. (+5 morale)"

    elif action.startswith("WRITE"):
        agent.update_satisfaction(+8)  # deeply fulfilling for writers
        return f"{agent_name} retreated to write in solitude. The pen moved freely."

    elif action.startswith("LEAVE"):
        env.departed.append(agent_name)
        agent.has_left = True
        return f"*** {agent_name} has packed their things and left Brook Farm. ***"

    else:  # REST
        agent.update_satisfaction(+2)
        return f"{agent_name} rested quietly, watching the day pass."


# --- Simulation ---

def run_simulation(n_rounds: int = MAX_ROUNDS) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(LOG_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)

    env = Environment()
    agents = {
        name: Agent(name=name, persona=persona)
        for name, persona in PERSONAS.items()
    }

    # Full structured log
    full_log = []
    # Per-character arc (time series of satisfaction, mood, actions)
    character_arcs = {name: [] for name in agents}
    # Environment metrics time series
    metrics = []

    print(f"\n{'='*60}")
    print(f"  BROOK FARM SIMULATION")
    print(f"  {n_rounds} rounds | {len(agents)} agents")
    print(f"  {', '.join(agents.keys())}")
    print(f"  Model: {MODEL}")
    print(f"{'='*60}\n")

    for round_num in range(1, n_rounds + 1):
        date_str = day_to_date(env.day)
        print(f"\n{'─'*50}")
        print(f"  Round {round_num} — {date_str} ({env.season})")
        print(f"  Food: {env.food} | Money: ${env.money} | Morale: {env.morale}%")
        print(f"{'─'*50}")

        # Trigger historical events
        env.trigger_event()
        for ev in env.events_this_round:
            print(f"\n  ** {ev['type'].upper()}: {ev['content'][:100]}...")

        # Each active agent decides (sequential — they see what earlier agents did)
        round_actions = []
        round_log = {
            "round": round_num,
            "date": date_str,
            "state_before": env.snapshot(),
            "actions": [],
        }

        for name, agent in agents.items():
            if agent.has_left:
                continue

            print(f"\n  [{name}]")
            decision = agent.decide(env, round_actions)

            result = resolve_action(name, decision, env, agent)

            # Post dialogue to bulletin board
            dialogue = decision.get("dialogue", "nothing")
            if dialogue and dialogue.lower() != "nothing":
                env.bulletin_board.append(f'[{name}] "{dialogue}"')

            # Build rich action log
            action_log = {
                "agent": name,
                "action": decision.get("action", "REST"),
                "reasoning": decision.get("reasoning", ""),
                "inner_thought": decision.get("inner_thought", ""),
                "observation": decision.get("observation", ""),
                "mood": decision.get("mood", "neutral"),
                "dialogue": dialogue,
                "result": result,
                "satisfaction_after": agent.satisfaction,
                "raw_response": decision.get("raw", ""),
            }
            round_actions.append(action_log)
            round_log["actions"].append(action_log)

            # Record character arc
            character_arcs[name].append({
                "round": round_num,
                "date": date_str,
                "action": decision.get("action", "REST"),
                "mood": decision.get("mood", "neutral"),
                "satisfaction": agent.satisfaction,
                "inner_thought": decision.get("inner_thought", ""),
                "observation": decision.get("observation", ""),
                "still_here": True,
            })

            # Print
            print(f"    Action: {decision.get('action', 'REST')}")
            print(f"    Mood: {decision.get('mood', '?')}")
            print(f"    Reasoning: {decision.get('reasoning', '')}")
            print(f"    Inner: {decision.get('inner_thought', '')}")
            if decision.get("observation"):
                print(f"    Observes: {decision['observation']}")
            if dialogue and dialogue.lower() != "nothing":
                print(f'    Says: "{dialogue}"')
            print(f"    → {result}")
            print(f"    [satisfaction: {agent.satisfaction}/100]")

            # Update all agents' memory
            memory_entry = f"{date_str}: {result}"
            if dialogue and dialogue.lower() != "nothing":
                memory_entry += f' {name} said: "{dialogue}"'
            for other in agents.values():
                if not other.has_left:
                    other.update_memory(memory_entry)

            agent.action_history.append(decision.get("action", "REST"))

        # Tick environment
        active_count = sum(1 for a in agents.values() if not a.has_left)
        env.tick(active_count)

        # Record environment metrics
        metrics.append({
            "round": round_num,
            "date": date_str,
            "food": env.food,
            "money": env.money,
            "morale": env.morale,
            "members": active_count,
            "farm_output": env.farm_output_this_round,
            "school_income": env.school_income_this_round,
        })

        round_log["state_after"] = env.snapshot()
        full_log.append(round_log)

        # Mark departed characters
        for name, agent in agents.items():
            if agent.has_left and character_arcs[name] and character_arcs[name][-1].get("still_here", True):
                character_arcs[name][-1]["still_here"] = False

        if active_count == 0:
            print("\n  *** ALL MEMBERS HAVE LEFT. BROOK FARM IS ABANDONED. ***")
            break

        if env.morale <= 0:
            print("\n  *** MORALE HAS HIT ZERO. THE COMMUNITY IS IN CRISIS. ***")

    # --- Save outputs ---

    # 1. Full structured log
    with open(os.path.join(run_dir, "full_log.json"), "w") as f:
        json.dump(full_log, f, indent=2)

    # 2. Character arcs
    with open(os.path.join(run_dir, "characters.json"), "w") as f:
        json.dump(character_arcs, f, indent=2)

    # 3. Environment metrics
    with open(os.path.join(run_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # 4. Narrative markdown
    with open(os.path.join(run_dir, "narrative.md"), "w") as f:
        f.write(f"# Brook Farm — Simulation Run {timestamp}\n\n")
        f.write(f"**Model**: {MODEL}\n")
        f.write(f"**Rounds**: {len(full_log)}\n")
        f.write(f"**Final state**: Food={env.food}, Money=${env.money}, Morale={env.morale}%\n")
        f.write(f"**Departed**: {', '.join(env.departed) if env.departed else 'None'}\n")
        f.write(f"**Survived**: {', '.join(n for n, a in agents.items() if not a.has_left) or 'None'}\n\n")
        f.write("---\n\n")

        for entry in full_log:
            f.write(f"## {entry['date']} (Round {entry['round']})\n\n")
            state = entry["state_before"]
            f.write(f"*{state['season'].capitalize()}. Food: {state['food']}, Money: ${state['money']}, Morale: {state['morale']}%*\n\n")

            # Events
            for ev in state.get("events", []):
                f.write(f"> **{ev['type'].upper()}**: {ev['content']}\n\n")

            # Actions
            for a in entry["actions"]:
                f.write(f"### {a['agent']}\n\n")
                f.write(f"**{a['action']}** — {a['result']}\n\n")
                f.write(f"*Reasoning*: {a['reasoning']}\n\n")
                f.write(f"*Inner thought*: {a['inner_thought']}\n\n")
                if a.get("observation"):
                    f.write(f"*Observes*: {a['observation']}\n\n")
                if a["dialogue"] and a["dialogue"].lower() != "nothing":
                    f.write(f'*Says aloud*: "{a["dialogue"]}"\n\n')
                f.write(f"*Mood*: {a['mood']} | *Satisfaction*: {a['satisfaction_after']}/100\n\n")
                f.write("---\n\n")

    # 5. Summary for quick review
    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(f"Brook Farm Simulation — {timestamp}\n")
        f.write(f"Rounds: {len(full_log)}\n")
        f.write(f"Final: Food={env.food}, Money=${env.money}, Morale={env.morale}%\n")
        f.write(f"Departed: {', '.join(env.departed) if env.departed else 'None'}\n")
        f.write(f"Survived: {', '.join(n for n, a in agents.items() if not a.has_left) or 'None'}\n\n")
        f.write("Character Final States:\n")
        for name, agent in agents.items():
            status = "LEFT" if agent.has_left else "STAYED"
            f.write(f"  {name}: {status}, satisfaction={agent.satisfaction}/100, actions={len(agent.action_history)}\n")
        f.write(f"\nRules adopted: {len(env.rules)}\n")
        for r in env.rules:
            f.write(f"  - {r}\n")

    print(f"\n{'='*60}")
    print(f"  SIMULATION COMPLETE")
    print(f"  Rounds: {len(full_log)}")
    print(f"  Final: Food={env.food}, Money=${env.money}, Morale={env.morale}%")
    print(f"  Departed: {', '.join(env.departed) if env.departed else 'None'}")
    print(f"\n  Output: {run_dir}/")
    print(f"    full_log.json    — structured data")
    print(f"    characters.json  — per-character arcs")
    print(f"    metrics.json     — environment time series")
    print(f"    narrative.md     — readable story")
    print(f"    summary.txt      — quick overview")
    print(f"{'='*60}\n")

    return {"log_dir": run_dir, "log": full_log, "env": env}


if __name__ == "__main__":
    import sys
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else MAX_ROUNDS
    run_simulation(rounds)
