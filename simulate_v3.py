"""
Utopia v3 — Brook Farm Agent Society Simulation

Based on v2. Three-phase rounds (Act / Talk / Reflect), structured agent
memory, conversations, voting, gossip, and JSONL event logging.

Output: runs/<timestamp>/events.jsonl (single source of truth)
Derived outputs via derive.py.

=== V3 CHANGE FROM V2 ===

AGENT-DRIVEN MORALE (the only change from v2)

   v1: Morale was formula-only. Only ORGANIZE (+5) raised it. Penalties of
       -10 to -20 per round for food/money crises. Hit 0 by round 10, stuck.
   v2: Added morale boosts to actions (FARM +2, TEACH +2, ORGANIZE +5, etc).
       Delayed collapse to round ~14 but still flatlined at 0 for 11-19 rounds.
   v3: Morale is no longer formula-driven. Instead, each agent reports a
       COMMUNITY_MORALE score (0-100) during reflection. Community morale =
       average of all agents' scores. No hardcoded boosts or penalties.

   Why: Morale is not a resource like food or money. It's a collective feeling.
   Real morale comes from how people *feel*, not from action lookup tables.
   Letting agents assess morale means it can recover from good events, crash
   from bad ones, and reflect genuine collective sentiment — not arithmetic.

   What was removed:
   - All morale +N from resolve_action() (FARM, TEACH, ORGANIZE, etc.)
   - All morale -N from tick() (food crisis, money crisis)
   - All morale -N from historical events (smallpox, fire)

   What was kept:
   - Morale still affects school income (students leave when community struggles)
   - Agents still see "Community Morale: X%" in their prompts

=== V2 CHANGES KEPT FROM V1 ===

1. PER-AGENT PASSION BONUSES — persona-specific satisfaction boosts
2. NEUTRAL REFLECTION PROMPT — no pessimism bias
3. SPEECH FATIGUE — trust erosion after 3+ consecutive speeches
4. SOFTER FOOD ECONOMY — 4 food/agent/round instead of 5
5. EVENT-CATALYZED PROPOSALS — ideological events prompt structural thinking
"""

import os
import sys
import json
import random
import time
import subprocess
from datetime import datetime
from dataclasses import dataclass, field

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


# --- Configuration ---

MODEL = "claude-haiku-4-5-20251001"
BACKEND = "cli"  # "cli" (uses claude CLI / Max sub) or "api" (uses Anthropic API)
MAX_ROUNDS = 30
LOG_DIR = "runs"
CONVERSATION_PAIRS_PER_ROUND = 2
ACTION_DEFS = None  # set by run_simulation from persona file or DEFAULT_ACTIONS
MAX_GOSSIP_IN_PROMPT = 5


def day_to_date(day: int) -> str:
    """Convert simulation day to approximate historical date."""
    year = 1841 + ((day - 1) * 2) // 12
    month_idx = (3 + (day - 1) * 2) % 12
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[month_idx]} {year}"


# --- Personas ---

# Default personas — loaded from JSON if --personas is specified
DEFAULT_PERSONAS_FILE = os.path.join(os.path.dirname(__file__), "personas", "brook_farm.json")

def load_personas(path=None):
    """Load personas from a JSON file. Returns (agents_dict, setting, relationships, environment, actions)."""
    path = path or DEFAULT_PERSONAS_FILE
    with open(path) as f:
        data = json.load(f)
    agents = data.get("agents", data)  # support both {agents: {...}} and flat dict
    setting = data.get("setting", "Brook Farm, a utopian community in West Roxbury, Massachusetts, in the 1840s.")
    relationships = data.get("relationships", [])
    environment = data.get("environment", {})
    actions = data.get("actions", None)  # None = use hardcoded defaults
    return agents, setting, relationships, environment, actions


# Default actions (used when persona file doesn't define them)
DEFAULT_ACTIONS = {
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
        "passions": {"ORGANIZE": 3, "SPEAK": 3},  # v2: leading and rallying the community
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
        "passions": {"WRITE": 3},  # v2: writing is his sustaining activity
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
        "passions": {"TEACH": 3},  # v2: the school is her domain
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
        "passions": {"TRADE": 3, "WRITE": 3},  # v2: journalism and practical commerce
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
        "passions": {"ORGANIZE": 5},  # v2: music/concerts are his reason for being here
    },
}


# --- Event Logger ---

class EventLogger:
    def __init__(self, path: str):
        self.path = path
        self.seq = 0
        self.f = open(path, "a")

    def log(self, round_num: int, phase: str, event_type: str,
            agent: str = None, data: dict = None) -> dict:
        self.seq += 1
        event = {
            "seq": self.seq,
            "round": round_num,
            "phase": phase,
            "type": event_type,
            "ts": datetime.now().isoformat(),
            "date": day_to_date(round_num) if round_num > 0 else None,
            "agent": agent,
            "data": data or {},
        }
        self.f.write(json.dumps(event) + "\n")
        self.f.flush()
        return event

    def close(self):
        self.f.close()


# --- Agent Memory ---

@dataclass
class AgentMemory:
    key_moments: list = field(default_factory=list)
    relationships: dict = field(default_factory=dict)
    concerns: list = field(default_factory=list)
    recent: list = field(default_factory=list)
    observations: list = field(default_factory=list)
    gossip_inbox: list = field(default_factory=list)  # gossip heard about others

    def add_recent(self, event: str):
        self.recent.append(event)
        if len(self.recent) > 15:
            self.recent = self.recent[-15:]

    def add_key_moment(self, day: int, event: str, emotion: str):
        self.key_moments.append({"day": day, "event": event, "emotion": emotion})

    def update_relationship(self, name: str, attitude: str = None,
                            trust: int = None, last_interaction: str = None):
        if name not in self.relationships:
            self.relationships[name] = {"attitude": "neutral", "trust": 5, "last_interaction": ""}
        rel = self.relationships[name]
        if attitude is not None:
            rel["attitude"] = attitude
        if trust is not None:
            rel["trust"] = max(1, min(10, trust))
        if last_interaction is not None:
            rel["last_interaction"] = last_interaction

    def add_observation(self, about: str, observation: str, day: int):
        self.observations.append({"about": about, "observation": observation, "day": day})

    def set_concerns(self, concerns: list):
        self.concerns = concerns[:10]  # cap at 10

    def relationship_summary(self) -> str:
        if not self.relationships:
            return "(no relationships yet)"
        lines = []
        for name, rel in self.relationships.items():
            lines.append(f"- {name}: trust {rel['trust']}/10, {rel['attitude']}")
        return "\n".join(lines)

    def concerns_summary(self) -> str:
        if not self.concerns:
            return "(no particular concerns)"
        return "\n".join(f"- {c}" for c in self.concerns)

    def key_moments_summary(self) -> str:
        if not self.key_moments:
            return "(none yet)"
        lines = []
        for km in self.key_moments[-5:]:  # show last 5
            lines.append(f"- Day {km['day']}: {km['event']} ({km['emotion']})")
        return "\n".join(lines)

    def recent_summary(self, n: int = 10) -> str:
        items = self.recent[-n:] if self.recent else ["(This is your first day at Brook Farm.)"]
        return "\n".join(str(m) for m in items)

    def gossip_about_me_summary(self, my_name: str) -> str:
        """Return gossip this agent has heard about themselves (from gossip_inbox)."""
        relevant = [g for g in self.gossip_inbox if g.get("about") != my_name]
        relevant = relevant[-MAX_GOSSIP_IN_PROMPT:]
        if not relevant:
            return "(nothing)"
        lines = []
        for g in relevant:
            lines.append(f'- Someone said about {g["about"]}: "{g["observation"]}"')
        return "\n".join(lines)

    def snapshot(self) -> dict:
        return {
            "key_moments": list(self.key_moments),
            "relationships": dict(self.relationships),
            "concerns": list(self.concerns),
            "recent_count": len(self.recent),
            "observations_count": len(self.observations),
            "gossip_inbox_count": len(self.gossip_inbox),
        }


# --- Environment ---

@dataclass
class Environment:
    n_initial_agents: int = 5
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
    building_health: dict = field(default_factory=lambda: {"The Hive (main house)": -1, "The Nest (school/guest house)": -1})
    rules: list = field(default_factory=list)
    bulletin_board: list = field(default_factory=list)
    departed: list = field(default_factory=list)
    events_this_round: list = field(default_factory=list)
    pending_proposals: list = field(default_factory=list)
    event_catalyst: str = None  # v2: ideological event that should prompt structural thinking

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

    def tick(self, n_agents: int) -> dict:
        """End-of-round environment update. Returns deltas for logging."""
        self.season = self.get_season()
        old_food, old_money, old_morale = self.food, self.money, self.morale

        self.school_income_this_round = 0
        self.farm_output_this_round = 0
        self.events_this_round = []
        self.pending_proposals = []

        # Food consumption (v2: reduced from 5 to 4 per agent)
        food_consumed = n_agents * 4
        self.food -= food_consumed

        # Winter extra food drain
        if self.season == "winter":
            self.food -= 5
            if random.random() < 0.1:
                self._announce("A harsh winter storm damages supplies.")
                self.food -= 10

        # School income scales with morale — students leave when community struggles
        if self.morale >= 50:
            base_school = 15
        elif self.morale >= 25:
            base_school = 8
            self._announce("Some students have withdrawn. School income is falling.")
        else:
            base_school = 3
            self._announce("Most students have left. The school barely functions.")
        self.money += base_school
        self.total_school_income += base_school
        self.money -= 10  # operating costs

        # v3: Resource crisis announcements (no morale penalties — morale is agent-driven)
        if self.food < 20 and self.food > 0:
            self._announce("Food is running dangerously low. People are hungry.")
        if self.food <= 0:
            self.food = 0
            self._announce("There is NO food. People are going hungry.")
            # Starvation: community must spend money to buy food
            if self.money >= 20:
                self.money -= 20
                self.food += 10  # emergency purchase
                self._announce("Emergency: $20 spent buying food from neighbors. This cannot continue.")
            else:
                self._announce("CRISIS: No food and no money to buy any. Members are falling ill.")
        if self.money < 50:
            self._announce("The treasury is nearly empty.")

        # Clamp
        self.food = max(0, self.food)
        self.morale = max(0, min(100, self.morale))

        self.day += 1

        return {
            "food_consumed": food_consumed,
            "food_produced": self.farm_output_this_round,
            "food_net": self.food - old_food,
            "money_earned": self.school_income_this_round + base_school,
            "money_spent": 10,
            "money_net": self.money - old_money,
            "morale_change": self.morale - old_morale,
            "season_change": self.season if self.season != self.get_season() else None,
        }

    def apply_building_decay(self):
        """10% chance per healthy building to need repair. 3 rounds unrepaired = removed."""
        to_remove = []
        for building in list(self.building_health.keys()):
            health = self.building_health[building]
            if health == -1:  # healthy
                if random.random() < 0.10:
                    self.building_health[building] = 0
                    self._announce(f"{building} is showing signs of wear and needs repair.")
            elif health >= 2:  # 3 rounds unrepaired
                to_remove.append(building)
                self._announce(f"{building} has deteriorated beyond repair and is no longer usable.")
            else:
                self.building_health[building] += 1

        for building in to_remove:
            if building in self.buildings:
                self.buildings.remove(building)
            del self.building_health[building]

    def repair_building(self, building: str) -> bool:
        """Repair a building. Returns True if successful."""
        # Find best match
        target = None
        for b in self.building_health:
            if building.lower() in b.lower() or b.lower() in building.lower():
                target = b
                break
        if target is None:
            # try first building needing repair
            for b, h in self.building_health.items():
                if h >= 0:
                    target = b
                    break
        if target is not None and self.building_health.get(target, -1) >= 0:
            if self.money >= 10:
                self.money -= 10
                self.building_health[target] = -1
                return True
        return False

    def trigger_event(self):
        self.events_this_round = []
        if self.day == 8:
            self._event(
                "Visitors from Boston arrive for a tour. They pay fees and ask many questions. "
                "Some are genuinely interested; others seem amused by the experiment.",
                {"money": 20}
            )
            self.money += 20
        if self.day == 12:
            self._event(
                "Albert Brisbane, a prominent Fourierist, visits and argues passionately "
                "that the community should reorganize along Charles Fourier's principles — "
                "structured work groups, a grand Phalanstery building, scientific social organization.",
                {}
            )
            # v2: catalyze structural proposals
            self.event_catalyst = (
                "Albert Brisbane's visit has raised the question: should the community "
                "reorganize along Fourierist principles? You may consider proposing "
                "structural changes to how the community is organized."
            )
        if self.day == 15:
            self._event(
                "A proposal: spend $7,000 to build a grand Phalanstery — a communal "
                "building for 14 families. Ambitious and transformative, but the community is already in debt.",
                {}
            )
            # v2: catalyze structural proposals
            self.event_catalyst = (
                "The Phalanstery proposal forces a question: should the community make "
                "a bold investment, or is the current path unsustainable? You may consider "
                "proposing changes to the community's direction."
            )
        if self.day == 18:
            self._event(
                "The New York Observer publishes a scathing article attacking the community's morals.",
                {}
            )
        if self.day == 20:
            self._event(
                "Smallpox breaks out. No one dies, but many are bedridden.",
                {}
            )
        if self.day == 24:
            self._event(
                "DISASTER: The Phalanstery has caught fire! Within two hours, the entire "
                "structure burns to the ground. It was UNINSURED. Loss: $7,000.",
                {"money": -200}
            )
            self.money -= 200

    def _announce(self, msg: str):
        self.bulletin_board.append(f"[ENVIRONMENT] {msg}")
        self.events_this_round.append({"type": "random_event", "title": msg[:60], "description": msg, "effects": {}})

    def _event(self, msg: str, effects: dict):
        self.bulletin_board.append(f"[EVENT] {msg}")
        self.events_this_round.append({"type": "historical_event", "title": msg[:60], "description": msg, "effects": effects})

    def snapshot(self) -> dict:
        return {
            "day": self.day,
            "date": day_to_date(self.day),
            "season": self.season,
            "food": self.food,
            "money": self.money,
            "morale": self.morale,
            "members_present": self.n_initial_agents - len(self.departed),
            "buildings": list(self.buildings),
            "building_health": dict(self.building_health),
            "rules": list(self.rules),
            "departed": list(self.departed),
        }

    def summary_for_agent(self) -> str:
        building_status = []
        for b in self.buildings:
            h = self.building_health.get(b, -1)
            status = "good" if h == -1 else f"NEEDS REPAIR ({h + 1} rounds)"
            building_status.append(f"  {b} [{status}]")

        return (
            f"DATE: {day_to_date(self.day)} (Day {self.day}, {self.season})\n"
            f"RESOURCES: Food={self.food}, Money=${self.money}, Community Morale={self.morale}%\n"
            f"MEMBERS PRESENT: {self.n_initial_agents - len(self.departed)} of 5\n"
            f"BUILDINGS:\n" + "\n".join(building_status) + "\n"
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
    memory: AgentMemory = field(default_factory=AgentMemory)
    has_left: bool = False
    satisfaction: int = 70
    action_history: list = field(default_factory=list)
    consecutive_speeches: int = 0  # v2: track speech fatigue
    community_setting: str = "Brook Farm, a utopian community in West Roxbury, Massachusetts, in the 1840s."
    client: object = field(default=None, repr=False)  # Anthropic client (api mode only)

    def __post_init__(self):
        # Initialize relationships with all other agents (default trust 5)
        for other_name in PERSONAS:
            if other_name != self.name:
                self.memory.update_relationship(other_name, attitude="new acquaintance", trust=5)

    def _system_prompt(self) -> str:
        p = self.persona
        return (
            f"You are {self.name}, a member of {self.community_setting}\n\n"
            f"ROLE: {p['role']}\n"
            f"AGE: {p['age']}\n\n"
            f"BACKGROUND:\n{p['background']}\n\n"
            f"MOTIVATION:\n{p['motivation']}\n\n"
            f"PERSONALITY:\n{p['personality']}\n\n"
            f"SKILLS: {', '.join(p['skills'])}\n\n"
            f"PRIVATE GOAL (known only to you):\n{p['private_goal']}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Stay in character at all times. Respond as this person would in the 1840s.\n"
            f"- Be specific and vivid. Use sensory details. This is your life.\n"
            f"- Your inner thoughts reveal what you truly feel — doubts, frustrations, hopes.\n"
        )

    def _llm_call(self, user_prompt: str, max_tokens: int = 500) -> str:
        system = self._system_prompt()
        if BACKEND == "cli":
            return self._llm_call_cli(system, user_prompt, max_tokens)
        else:
            return self._llm_call_api(system, user_prompt, max_tokens)

    def _llm_call_cli(self, system: str, user_prompt: str, max_tokens: int) -> str:
        """Use claude CLI (works with Max subscription)."""
        full_prompt = f"{system}\n---\n\n{user_prompt}"
        try:
            result = subprocess.run(
                ["claude", "-p", full_prompt, "--output-format", "text",
                 "--max-turns", "1", "--model", MODEL],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                text = result.stdout.strip()
                if not text:
                    return "(CLI error: empty response)"
                return text
            else:
                return f"(CLI error: {result.stderr.strip()[:200]})"
        except subprocess.TimeoutExpired:
            return "(CLI timeout)"
        except Exception as e:
            return f"(CLI error: {e})"

    def _llm_call_api(self, system: str, user_prompt: str, max_tokens: int) -> str:
        """Use Anthropic API directly."""
        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"(API error: {e})"

    def _parse_kv(self, text: str, keys: list) -> dict:
        """Parse KEY: value lines from LLM response."""
        result = {"raw_llm_response": text}
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            for key in keys:
                prefix = key.upper() + ":"
                if line.upper().startswith(prefix):
                    result[key.lower()] = line[len(prefix):].strip()
                    break
        # Defaults
        for key in keys:
            result.setdefault(key.lower(), "")
        return result

    def decide_action(self, env: "Environment", gossip_about_me: list) -> dict:
        """Phase 1: Choose an action for the day."""
        gossip_text = "(nothing)"
        if gossip_about_me:
            gossip_items = gossip_about_me[-MAX_GOSSIP_IN_PROMPT:]
            gossip_text = "\n".join(
                f'- Someone said about you: "{g["observation"]}"' for g in gossip_items
            )

        prompt = (
            f"CURRENT SITUATION:\n{env.summary_for_agent()}\n\n"
            f"RECENT NEWS AND EVENTS:\n{env.recent_bulletin()}\n\n"
            f"YOUR RECENT MEMORIES:\n{self.memory.recent_summary()}\n\n"
            f"YOUR CURRENT CONCERNS:\n{self.memory.concerns_summary()}\n\n"
            f"YOUR RELATIONSHIPS:\n{self.memory.relationship_summary()}\n\n"
            f"WHAT OTHERS HAVE SAID ABOUT YOU (gossip you've overheard):\n{gossip_text}\n\n"
            f"YOUR KEY MEMORIES:\n{self.memory.key_moments_summary()}\n\n"
            f"YOUR PERSONAL SATISFACTION: {self.satisfaction}/100\n\n"
            f"What do you do today? Choose ONE action.\n\n"
            + (f"** RECENT EVENT: {env.event_catalyst} **\n\n" if env.event_catalyst else "")
            + f"Available actions:\n"
            + "".join(
                f"- {name}{(' ' + a.get('arg', '')) if a.get('arg') else ''}: {a['prompt']}\n"
                for name, a in (ACTION_DEFS or DEFAULT_ACTIONS).items()
            )
            + "\n"
            f"Respond in EXACTLY this format:\n"
            f"ACTION: <your chosen action>\n"
            f"REASONING: <1-2 sentences, in character>\n"
            f"INNER_THOUGHT: <what you truly think and feel — be honest>\n"
            f"OBSERVATION: <what you notice about others today>\n"
            f"MOOD: <one word>\n"
            f"DIALOGUE: <what you say aloud, or 'nothing'>\n"
        )

        text = self._llm_call(prompt, max_tokens=400)
        result = self._parse_kv(text, ["action", "reasoning", "inner_thought", "observation", "mood", "dialogue"])
        result.setdefault("action", "REST")
        if not result.get("mood"):
            result["mood"] = "neutral"
        if not result.get("dialogue"):
            result["dialogue"] = "nothing"
        return result

    def speak_in_conversation(self, partner_name: str, context: str,
                               history: list, is_initiator: bool) -> dict:
        """Phase 2: One turn of conversation."""
        rel = self.memory.relationships.get(partner_name, {"attitude": "unknown", "trust": 5, "last_interaction": ""})

        history_text = ""
        if history:
            history_text = "CONVERSATION SO FAR:\n"
            for turn in history:
                history_text += f'  {turn["speaker"]}: "{turn["says"]}" (tone: {turn["tone"]})\n'
            history_text += "\n"

        role = "You are starting this conversation." if is_initiator and not history else "Respond to what was said."

        prompt = (
            f"You are having a conversation with {partner_name}.\n\n"
            f"CONTEXT: {context}\n\n"
            f"YOUR RELATIONSHIP WITH {partner_name}:\n"
            f"- Attitude: {rel['attitude']}\n"
            f"- Trust: {rel['trust']}/10\n"
            f"- Last interaction: {rel['last_interaction'] or '(none yet)'}\n\n"
            f"YOUR CURRENT CONCERNS:\n{self.memory.concerns_summary()}\n\n"
            f"{history_text}"
            f"{role}\n\n"
            f"Respond in EXACTLY this format:\n"
            f"SAYS: <what you say aloud — be specific and natural>\n"
            f"TONE: <warm, tense, diplomatic, frustrated, playful, resigned, earnest, sardonic>\n"
            f"INNER_THOUGHT: <what you truly think during this exchange>\n"
        )

        text = self._llm_call(prompt, max_tokens=250)
        result = self._parse_kv(text, ["says", "tone", "inner_thought"])
        result.setdefault("says", "...")
        result.setdefault("tone", "neutral")
        return result

    def vote_on_proposal(self, proposal: str, proposed_by: str, env: "Environment") -> dict:
        """Phase 2b: Vote on a proposal."""
        rel = self.memory.relationships.get(proposed_by, {"attitude": "unknown", "trust": 5})

        prompt = (
            f"A PROPOSAL has been made for the community to vote on.\n\n"
            f'PROPOSAL: "{proposal}"\n'
            f"PROPOSED BY: {proposed_by}\n\n"
            f"CURRENT STATE:\n{env.summary_for_agent()}\n\n"
            f"YOUR CONCERNS:\n{self.memory.concerns_summary()}\n\n"
            f"YOUR RELATIONSHIP WITH {proposed_by}:\n"
            f"- Attitude: {rel['attitude']}\n"
            f"- Trust: {rel['trust']}/10\n\n"
            f"You must vote. Consider the proposal on its merits and how it affects you.\n\n"
            f"Respond in EXACTLY this format:\n"
            f"VOTE: <YES / NO / ABSTAIN>\n"
            f"REASONING: <1-2 sentences, in character>\n"
            f"INNER_THOUGHT: <what you truly think about this proposal>\n"
            f"DIALOGUE: <what you say aloud about your vote, or 'nothing'>\n"
        )

        text = self._llm_call(prompt, max_tokens=200)
        result = self._parse_kv(text, ["vote", "reasoning", "inner_thought", "dialogue"])
        # Normalize vote
        vote_raw = result.get("vote", "ABSTAIN").upper().strip()
        if "YES" in vote_raw:
            result["vote"] = "YES"
        elif "NO" in vote_raw:
            result["vote"] = "NO"
        else:
            result["vote"] = "ABSTAIN"
        return result

    def reflect(self, today_summary: str, env: "Environment",
                active_agents: list) -> dict:
        """Phase 3: End-of-day reflection. Updates memory."""
        rel_prompts = ""
        for other in active_agents:
            if other != self.name:
                rel = self.memory.relationships.get(other, {"trust": 5, "attitude": "unknown"})
                rel_prompts += (
                    f"RELATIONSHIP_{other.replace(' ', '_')}: "
                    f"<trust 1-10> | <your current attitude in one sentence>\n"
                )

        prompt = (
            f"The day is ending. Reflect privately on what happened today.\n\n"
            f"TODAY'S EVENTS:\n{today_summary}\n\n"
            f"YOUR KEY MEMORIES:\n{self.memory.key_moments_summary()}\n\n"
            f"YOUR CURRENT CONCERNS:\n{self.memory.concerns_summary()}\n\n"
            f"YOUR CURRENT RELATIONSHIPS:\n{self.memory.relationship_summary()}\n\n"
            f"YOUR SATISFACTION: {self.satisfaction}/100\n\n"
            f"Reflect on this day. Be honest with yourself.\n\n"
            f"Respond in EXACTLY this format:\n\n"
            f"SUMMARY: <2-3 sentences — what stays with you from today?>\n\n"
            f"MOOD: <one word>\n\n"
            f"SATISFACTION_CHANGE: <how much your satisfaction changed today: a number from -10 to +10. "
            f"Negative if the day was discouraging or frustrating. "
            f"Positive if something genuinely good happened. 0 if an ordinary day. "
            f"Your current satisfaction is {self.satisfaction}/100.>\n\n"
            f"KEY_MOMENT: <Will you remember this specific day years from now? A death, a departure, "
            f"a betrayal, a fire, a vote that changed everything — THAT is a key moment. "
            f"Ordinary days of work, conversation, and worry are NOT key moments. "
            f"You should have at most 3-5 key moments across an entire year. "
            f"Write 'none' for most days.>\n"
            f"KEY_EMOTION: <If key moment, one emotion word. If none, write 'none'>\n\n"
            f"COMMUNITY_MORALE: <How do you feel about the community's direction right now? "
            f"A number from 0 to 100. Consider: Are people doing meaningful work? Is there "
            f"enough food? Are relationships healthy? Is the vision alive? Be honest — "
            f"this is your private assessment, not a public performance. "
            f"Current community morale is {env.morale}%.>\n\n"
            f"CONCERNS:\n<List your current worries, one per line with '- ' prefix. Replace old list.>\n\n"
            f"{rel_prompts}\n"
            f"OBSERVATION: <Something you noticed about ONE other person today. Format: ABOUT: <name> | <what you noticed>>\n"
        )

        text = self._llm_call(prompt, max_tokens=600)
        result = {"raw_llm_response": text}

        # Parse structured fields
        lines = text.split("\n")
        concerns = []
        in_concerns = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_concerns:
                    in_concerns = False
                continue

            upper = stripped.upper()

            if upper.startswith("SUMMARY:"):
                result["summary"] = stripped[8:].strip()
                in_concerns = False
            elif upper.startswith("MOOD:"):
                result["mood"] = stripped[5:].strip().lower()
                in_concerns = False
            elif upper.startswith("SATISFACTION_CHANGE:") or upper.startswith("SATISFACTION CHANGE:"):
                try:
                    prefix_len = 19 if "CHANGE:" in upper else 20
                    val = stripped[prefix_len:].strip()
                    # Extract number (may have +/- sign)
                    num_str = ""
                    for c in val:
                        if c in "-+0123456789":
                            num_str += c
                        elif num_str:
                            break
                    delta = int(num_str) if num_str else 0
                    delta = max(-10, min(10, delta))  # clamp to [-10, +10]
                    result["satisfaction_change"] = delta
                except (ValueError, IndexError):
                    result["satisfaction_change"] = 0
                in_concerns = False
            elif upper.startswith("SATISFACTION:"):
                # Fallback if LLM ignores the _CHANGE format
                try:
                    val = stripped[13:].strip()
                    raw = int("".join(c for c in val if c.isdigit())[:3])
                    # Convert absolute to delta, clamped
                    delta = raw - self.satisfaction
                    delta = max(-10, min(10, delta))
                    result["satisfaction_change"] = delta
                except (ValueError, IndexError):
                    result["satisfaction_change"] = 0
                in_concerns = False
            elif upper.startswith("KEY_MOMENT:"):
                val = stripped[11:].strip()
                result["key_moment"] = None if val.lower() == "none" else val
                in_concerns = False
            elif upper.startswith("KEY_EMOTION:"):
                val = stripped[12:].strip()
                result["key_emotion"] = None if val.lower() == "none" else val
                in_concerns = False
            elif upper.startswith("COMMUNITY_MORALE:") or upper.startswith("COMMUNITY MORALE:"):
                # v3: parse agent's community morale assessment
                try:
                    prefix_len = 17 if "MORALE:" in upper[10:] else 18
                    val = stripped[prefix_len:].strip()
                    num_str = ""
                    for c in val:
                        if c in "0123456789":
                            num_str += c
                        elif num_str:
                            break
                    cm = int(num_str) if num_str else 50
                    cm = max(0, min(100, cm))
                    result["community_morale"] = cm
                except (ValueError, IndexError):
                    result["community_morale"] = 50
                in_concerns = False
            elif upper.startswith("CONCERNS:"):
                in_concerns = True
                # Check if content follows on same line
                rest = stripped[9:].strip()
                if rest and rest.startswith("- "):
                    concerns.append(rest[2:].strip())
            elif in_concerns and stripped.startswith("- "):
                concerns.append(stripped[2:].strip())
            elif upper.startswith("RELATIONSHIP_"):
                # Parse RELATIONSHIP_George_Ripley: 7 | attitude text
                parts = stripped.split(":", 1)
                if len(parts) == 2:
                    name_part = parts[0][13:].replace("_", " ").strip()
                    val_part = parts[1].strip()
                    pipe_parts = val_part.split("|", 1)
                    if len(pipe_parts) == 2:
                        try:
                            trust = int("".join(c for c in pipe_parts[0] if c.isdigit())[:2])
                        except (ValueError, IndexError):
                            trust = 5
                        attitude = pipe_parts[1].strip()
                        # Match to actual agent name
                        matched_name = None
                        for agent_name in PERSONAS:
                            if agent_name.replace(" ", "_").lower() == name_part.replace(" ", "_").lower():
                                matched_name = agent_name
                                break
                            # Partial match
                            if name_part.lower() in agent_name.lower() or agent_name.lower() in name_part.lower():
                                matched_name = agent_name
                                break
                        if matched_name:
                            result.setdefault("relationships", {})[matched_name] = {
                                "trust": trust, "attitude": attitude
                            }
                in_concerns = False
            elif upper.startswith("OBSERVATION:"):
                obs_text = stripped[12:].strip()
                if "ABOUT:" in obs_text.upper():
                    obs_parts = obs_text.split("|", 1)
                    about_part = obs_parts[0].replace("ABOUT:", "").replace("about:", "").strip()
                    obs_detail = obs_parts[1].strip() if len(obs_parts) > 1 else obs_text
                    # Match name
                    matched = None
                    for agent_name in PERSONAS:
                        if about_part.lower() in agent_name.lower() or agent_name.lower() in about_part.lower():
                            matched = agent_name
                            break
                    result["observation"] = {"about": matched or about_part, "detail": obs_detail}
                else:
                    result["observation"] = {"about": "unknown", "detail": obs_text}
                in_concerns = False

        result.setdefault("summary", "")
        result.setdefault("mood", "neutral")
        result.setdefault("satisfaction_change", 0)
        result.setdefault("key_moment", None)
        result.setdefault("key_emotion", None)
        result.setdefault("community_morale", 50)  # v3: default if not parsed
        result.setdefault("relationships", {})
        result.setdefault("observation", None)
        result["concerns"] = concerns if concerns else self.memory.concerns

        return result


# --- Action Resolution ---

def _apply_passion_bonus(agent: Agent, action_type: str, base_sat: int) -> int:
    """v2: Apply per-agent passion bonus to satisfaction delta."""
    passions = agent.persona.get("passions", {})
    bonus = passions.get(action_type, 0)
    return base_sat + bonus


def resolve_action(agent_name: str, decision: dict, env: Environment, agent: Agent) -> dict:
    """Resolve an action and return {description, effects}.
    v3.1: reads action effects from ACTION_DEFS (data-driven)."""
    action = decision.get("action", "REST").upper()
    action_type = action.split()[0] if action else "REST"
    arg = action[len(action_type):].strip().strip("<>") if len(action) > len(action_type) else ""
    effects = {}
    defs = ACTION_DEFS or DEFAULT_ACTIONS

    # v2: track speech fatigue
    if action_type == "SPEAK":
        agent.consecutive_speeches += 1
    else:
        agent.consecutive_speeches = 0

    # Special-case actions (structural side effects beyond resources)
    if action_type == "LEAVE":
        env.departed.append(agent_name)
        agent.has_left = True
        return {"description": f"*** {agent_name} has departed the community. ***", "effects": {"departed": True}}

    if action_type == "PROPOSE":
        rule = arg or "a new community rule"
        env.pending_proposals.append({"proposal": rule, "proposed_by": agent_name})
        return {"description": f"{agent_name} proposed: '{rule}' — a vote will be held.", "effects": {}}

    if action_type == "BUILD":
        what = arg or "a new structure"
        cost = abs(defs.get("BUILD", {}).get("money", -30))
        if env.money >= cost:
            env.money -= cost
            env.buildings.append(what)
            env.building_health[what] = -1
            base_sat = defs.get("BUILD", {}).get("satisfaction", 2)
            sat_delta = _apply_passion_bonus(agent, "BUILD", base_sat)
            agent.satisfaction = min(100, agent.satisfaction + sat_delta)
            return {"description": f"{agent_name} worked on building {what}. (-${cost})", "effects": {"money": -cost, "satisfaction": sat_delta}}
        else:
            return {"description": f"{agent_name} wanted to build but the treasury is empty.", "effects": {}}

    if action_type == "REPAIR":
        building = arg or ""
        if env.repair_building(building):
            base_sat = defs.get("REPAIR", {}).get("satisfaction", 2)
            sat_delta = _apply_passion_bonus(agent, "REPAIR", base_sat)
            agent.satisfaction = min(100, agent.satisfaction + sat_delta)
            cost = abs(defs.get("REPAIR", {}).get("money", -10))
            return {"description": f"{agent_name} repaired a building. (-${cost})", "effects": {"money": -cost, "satisfaction": sat_delta}}
        else:
            return {"description": f"{agent_name} wanted to repair but nothing needs fixing (or no money).", "effects": {}}

    # Generic data-driven resolution
    action_def = defs.get(action_type, defs.get("REST", {"satisfaction": 2, "prompt": "Personal time"}))
    base_sat = action_def.get("satisfaction", 0)
    sat_delta = _apply_passion_bonus(agent, action_type, base_sat)

    # Apply resource effects
    food_delta = action_def.get("food", 0)
    money_delta = action_def.get("money", 0)

    if food_delta:
        env.food += food_delta
        env.farm_output_this_round += max(0, food_delta)
        env.total_farm_output += max(0, food_delta)
    if money_delta > 0:
        env.money += money_delta
        if action_type == "TEACH":
            env.school_income_this_round += money_delta
            env.total_school_income += money_delta
    elif money_delta < 0:
        env.money += money_delta  # negative

    if sat_delta:
        agent.satisfaction = max(0, min(100, agent.satisfaction + sat_delta))

    effects = {}
    if food_delta: effects["food"] = food_delta
    if money_delta: effects["money"] = money_delta
    if sat_delta: effects["satisfaction"] = sat_delta

    # Build description
    desc_parts = [f"{agent_name} — {action_def.get('prompt', action_type)}"]
    if arg:
        arg_display = arg.title() if arg == arg.upper() else arg
        desc_parts[0] = f"{agent_name} — {action_def.get('prompt', action_type)}: {arg_display}"
    effect_notes = []
    if food_delta: effect_notes.append(f"{'+' if food_delta > 0 else ''}{food_delta} food")
    if money_delta: effect_notes.append(f"{'+'if money_delta > 0 else ''}${money_delta}")
    if effect_notes:
        desc_parts.append(f"({', '.join(effect_notes)})")
    desc = " ".join(desc_parts)

    # Speech fatigue
    if action_type == "SPEAK" and agent.consecutive_speeches >= 3:
        effects["speech_fatigue"] = agent.consecutive_speeches
        desc += f" (spoken {agent.consecutive_speeches} rounds in a row)"

    return {"description": desc, "effects": effects}


# --- Conversation Pair Selection ---

def select_conversation_pairs(agents: dict, env: Environment,
                               proposals: list) -> list:
    """Select 2-3 conversation pairs for this round."""
    active = [name for name, a in agents.items() if not a.has_left]
    if len(active) < 2:
        return []

    pairs = []
    used = set()

    # 1. If proposals, proposer talks to most skeptical member
    for prop in proposals:
        proposer = prop["proposed_by"]
        if proposer not in active:
            continue
        # Find agent with lowest trust toward proposer
        lowest_trust = 11
        skeptic = None
        for name in active:
            if name == proposer or name in used:
                continue
            trust = agents[name].memory.relationships.get(proposer, {}).get("trust", 5)
            if trust < lowest_trust:
                lowest_trust = trust
                skeptic = name
        if skeptic:
            pairs.append((proposer, skeptic, f"{proposer} proposed '{prop['proposal']}' and needs support"))
            used.add(proposer)
            used.add(skeptic)

    # 2. Tension pair — lowest mutual trust
    if len(pairs) < CONVERSATION_PAIRS_PER_ROUND:
        lowest_trust = 11
        tension_pair = None
        for i, a in enumerate(active):
            if a in used:
                continue
            for b in active[i+1:]:
                if b in used:
                    continue
                trust_ab = agents[a].memory.relationships.get(b, {}).get("trust", 5)
                trust_ba = agents[b].memory.relationships.get(a, {}).get("trust", 5)
                avg = (trust_ab + trust_ba) / 2
                if avg < lowest_trust:
                    lowest_trust = avg
                    tension_pair = (a, b)
        if tension_pair and lowest_trust < 6:
            a, b = tension_pair
            pairs.append((a, b, f"Tension between {a} and {b} (trust: {lowest_trust:.0f}/10)"))
            used.add(a)
            used.add(b)

    # 3. Random weighted pair (married couple bonus)
    if len(pairs) < CONVERSATION_PAIRS_PER_ROUND:
        available = [n for n in active if n not in used]
        if len(available) >= 2:
            # Weight by relationship + married bonus
            candidates = []
            for i, a in enumerate(available):
                for b in available[i+1:]:
                    weight = 1.0
                    trust_ab = agents[a].memory.relationships.get(b, {}).get("trust", 5)
                    weight += trust_ab / 10
                    if {a, b} == {"George Ripley", "Sophia Ripley"}:
                        weight += 3.0
                    candidates.append((a, b, weight))
            if candidates:
                weights = [c[2] for c in candidates]
                total = sum(weights)
                r = random.random() * total
                cumulative = 0
                for a, b, w in candidates:
                    cumulative += w
                    if r <= cumulative:
                        context = "Evening encounter"
                        if {a, b} == {"George Ripley", "Sophia Ripley"}:
                            context = "Private conversation between spouses"
                        pairs.append((a, b, context))
                        break

    return pairs


# --- Gossip Spread ---

def spread_gossip(agents: dict, current_round: int, logger: EventLogger):
    """Spread observations between agents. 50% chance per observation."""
    active = [name for name, a in agents.items() if not a.has_left]

    for name in active:
        agent = agents[name]
        for obs in agent.memory.observations:
            if random.random() < 0.5:
                # Pick random hearer (not observer, not observed)
                candidates = [n for n in active if n != name and n != obs["about"]]
                if candidates:
                    hearer = random.choice(candidates)
                    agents[hearer].memory.gossip_inbox.append({
                        "about": obs["about"],
                        "observation": obs["observation"],
                        "from": name,
                        "day": obs["day"],
                    })
                    logger.log(current_round, "reflect", "gossip_spread", data={
                        "origin": name,
                        "hearer": hearer,
                        "about": obs["about"],
                        "observation": obs["observation"],
                        "original_round": obs["day"],
                    })


# --- Main Simulation ---

def run_simulation(config: dict = None):
    """Run a simulation from a config dict.

    Config keys (all optional, with defaults):
        name: str           — experiment name (default: "run")
        rounds: int         — number of rounds (default: 30)
        seed: int           — random seed (default: 42)
        model: str          — LLM model (default: MODULE-level MODEL)
        backend: str        — "cli" or "api" (default: MODULE-level BACKEND)
        agents: list[str]   — subset of persona keys (default: all)
        personas: str       — path to personas JSON file (default: brook_farm.json)
        environment: dict   — override food, money, morale (default: standard)
    """
    if config is None:
        config = {}

    global MODEL, BACKEND, PERSONAS

    # v3.1: load personas from JSON file
    personas_file = config.get("personas", None)
    if personas_file:
        PERSONAS, community_setting, persona_relationships, persona_env, custom_actions = load_personas(personas_file)
    else:
        community_setting = "Brook Farm, a utopian community in West Roxbury, Massachusetts, in the 1840s."
        persona_relationships = [{"pair": ["George Ripley", "Sophia Ripley"], "type": "married", "initial_trust": 8}]
        persona_env = {}
        custom_actions = None

    # v3.1: action definitions — custom or default (module global for Agent access)
    global ACTION_DEFS
    ACTION_DEFS = custom_actions or DEFAULT_ACTIONS

    exp_name = config.get("name", "run")
    n_rounds = config.get("rounds", MAX_ROUNDS)
    seed = config.get("seed", 42)
    model = config.get("model", MODEL)
    backend = config.get("backend", BACKEND)
    agent_names = config.get("agents", list(PERSONAS.keys()))
    # Environment: persona file sets defaults, experiment config overrides
    env_overrides = {**persona_env, **config.get("environment", {})}

    # Set globals for this run (used by Agent._llm_call)
    MODEL = model
    BACKEND = backend

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(LOG_DIR, f"v3_{exp_name}_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)

    start_time = time.time()
    logger = EventLogger(os.path.join(run_dir, "events.jsonl"))

    # Environment with optional overrides
    env = Environment(n_initial_agents=len(agent_names))
    if "food" in env_overrides:
        env.food = env_overrides["food"]
    if "money" in env_overrides:
        env.money = env_overrides["money"]
    if "morale" in env_overrides:
        env.morale = env_overrides["morale"]

    random.seed(seed)

    # Initialize agents (filtered by config)
    shared_client = None
    if backend == "api":
        if Anthropic is None:
            print("Error: anthropic package not installed. Use --backend cli or pip install anthropic")
            sys.exit(1)
        shared_client = Anthropic()

    selected_personas = {k: v for k, v in PERSONAS.items() if k in agent_names}
    agents = {}
    for name, persona in selected_personas.items():
        agent = Agent(name=name, persona=persona, client=shared_client,
                      community_setting=community_setting)
        agents[name] = agent

    # v3.1: Apply custom relationships from persona file
    for rel in persona_relationships:
        pair = rel.get("pair", [])
        if len(pair) == 2 and pair[0] in agents and pair[1] in agents:
            trust = rel.get("initial_trust", 8)
            agents[pair[0]].memory.update_relationship(pair[1], trust=trust)
            agents[pair[1]].memory.update_relationship(pair[0], trust=trust)

    # Save config — everything needed to reproduce this exact run
    git_hash = ""
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        pass

    full_config = {
        "version": "v3",
        "name": exp_name,
        "model": model,
        "backend": backend,
        "rounds": n_rounds,
        "seed": seed,
        "agents": list(selected_personas.keys()),
        "environment": {"food": env.food, "money": env.money, "morale": env.morale},
        "timestamp": timestamp,
        "run_dir": run_dir,
        "git_hash": git_hash,
        "config_source": config.get("_config_file", None),
        "notes": config.get("notes", None),
    }
    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump(full_config, f, indent=2)

    # --- Setup events ---
    logger.log(0, "setup", "sim_start", data={
        "version": "v3",
        "experiment": exp_name,
        "model": model,
        "max_rounds": n_rounds,
        "n_agents": len(selected_personas),
        "agents": list(selected_personas.keys()),
        "initial_state": {"food": env.food, "money": env.money, "morale": env.morale},
    })
    for name, persona in selected_personas.items():
        logger.log(0, "setup", "persona_loaded", agent=name, data=persona)

    total_llm_calls = 0
    rich = not config.get("clean", False)
    WRAP = 120  # max line width for rich output

    # --- Pretty output helpers ---
    def wrap_text(text, indent="     ", max_line=None):
        """Word-wrap text with indent prefix."""
        if max_line is None:
            max_line = WRAP
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

    def bar(value, max_val=100, width=20):
        filled = int(value / max_val * width) if max_val > 0 else 0
        filled = max(0, min(width, filled))
        return "█" * filled + "░" * (width - filled)

    MOOD_EMOJI = {
        "hopeful": "😊", "optimistic": "😊", "content": "😌", "happy": "😄",
        "anxious": "😰", "worried": "😟", "concerned": "😟",
        "frustrated": "😤", "angry": "😠", "bitter": "😒",
        "sad": "😢", "melancholy": "😢", "resigned": "😔", "despairing": "😞",
        "determined": "💪", "resolute": "💪",
        "guilty": "😣", "conflicted": "😣",
        "neutral": "😐", "tired": "😫", "exhausted": "😫",
    }
    ACTION_EMOJI = {
        "FARM": "🌾", "TEACH": "📚", "BUILD": "🔨", "REPAIR": "🔧",
        "TRADE": "💰", "WRITE": "✍️", "SPEAK": "🎤", "ORGANIZE": "🎵",
        "REST": "💤", "PROPOSE": "📜", "LEAVE": "🚪",
    }

    def get_mood_emoji(mood):
        mood_lower = (mood or "neutral").lower()
        for key, emoji in MOOD_EMOJI.items():
            if key in mood_lower:
                return emoji
        return "😐"

    print(f"\n  🏛️  UTOPIA SIMULATION")
    print(f"  {'─'*50}")
    print(f"  {exp_name}")
    print(f"  {n_rounds} rounds · {len(agents)} agents · seed {seed}")
    print(f"  Model: {model} ({backend})")
    print(f"  Output: {run_dir}/")
    print(f"  {'─'*50}\n")

    for round_num in range(1, n_rounds + 1):
        date_str = day_to_date(env.day)
        active = {n: a for n, a in agents.items() if not a.has_left}

        print(f"\n  {'═'*60}")
        print(f"  Round {round_num}/{n_rounds} — {date_str} ({env.season})")
        print(f"  🌾 Food   {bar(env.food, 200)} {env.food}")
        print(f"  💰 Money  {bar(env.money, 1000)} ${env.money}")
        print(f"  ❤️  Morale {bar(env.morale)} {env.morale}%")
        print(f"  👥 {', '.join(active.keys())}")
        print(f"  {'═'*60}")

        # --- Environment events ---
        env.trigger_event()
        logger.log(round_num, "env", "env_state", data=env.snapshot())
        for ev in env.events_this_round:
            logger.log(round_num, "env", ev["type"], data=ev)
            print(f"\n  ⚡ {ev['type'].upper()}: {ev['description'][:80]}")

        # ========================
        # PHASE 1: ACT
        # ========================
        print(f"\n  {'─'*40}")
        print(f"  🎭 Actions")
        print(f"  {'─'*40}")
        round_action_summaries = []

        for name, agent in active.items():
            # Collect gossip about this agent from other agents' observations
            gossip = []
            for other_name, other_agent in active.items():
                if other_name == name:
                    continue
                for obs in other_agent.memory.observations:
                    if obs["about"] == name:
                        gossip.append(obs)

            decision = agent.decide_action(env, gossip)
            total_llm_calls += 1

            result = resolve_action(name, decision, env, agent)

            # Log
            logger.log(round_num, "act", "action", agent=name, data={
                "chosen_action": decision.get("action", "REST"),
                "reasoning": decision.get("reasoning", ""),
                "inner_thought": decision.get("inner_thought", ""),
                "observation": decision.get("observation", ""),
                "mood": decision.get("mood", "neutral"),
                "dialogue": decision.get("dialogue", "nothing"),
                "effects": result["effects"],
                "satisfaction_after": agent.satisfaction,
            })
            logger.log(round_num, "act", "action_effect", agent=name, data={
                "description": result["description"],
                "resource_changes": result["effects"],
            })

            # Handle departure
            if agent.has_left:
                logger.log(round_num, "meta", "agent_departed", agent=name, data={
                    "round": round_num,
                    "date": date_str,
                    "final_satisfaction": agent.satisfaction,
                    "final_concerns": list(agent.memory.concerns),
                    "final_relationships": dict(agent.memory.relationships),
                    "parting_words": decision.get("dialogue", ""),
                    "inner_thought": decision.get("inner_thought", ""),
                })
                print(f"  🚪 {name} DEPARTS")

            # Bulletin board
            dialogue = decision.get("dialogue", "nothing")
            if dialogue and dialogue.lower() != "nothing":
                env.bulletin_board.append(f'[{name}] "{dialogue}"')

            # Update all agents' recent memory
            for other in agents.values():
                if not other.has_left:
                    other.memory.add_recent(f"{date_str}: {result['description']}")

            agent.action_history.append(decision.get("action", "REST"))
            round_action_summaries.append(f"{name}: {result['description']}")

            # Print
            action_raw = decision.get('action', 'REST') or 'REST'
            action_base = action_raw.split()[0].upper()
            mood = decision.get('mood', 'neutral')
            emoji = ACTION_EMOJI.get(action_base, '·')
            mood_e = get_mood_emoji(mood)
            first = name.split()[0]

            if rich:
                inner = decision.get('inner_thought', '').strip().strip('*')
                dialogue = decision.get('dialogue', '').strip().strip('"')
                desc = result['description']
                # Strip agent name from description — already shown in header
                short_desc = desc.split(' — ', 1)[-1] if ' — ' in desc else desc
                print(f"\n  {emoji} {first} → {action_raw.lower()} {mood_e}")
                print(wrap_text(short_desc))
                if inner:
                    print(wrap_text(f"🧠 {inner}"))
                if dialogue and dialogue.lower() != "nothing":
                    print(wrap_text(f'💬 "{dialogue}"'))
                print(f"  {'·'*30}")
            else:
                print(f"  {emoji} {first} → {action_raw.lower()} {mood_e}")

        # Refresh active list (someone may have left)
        active = {n: a for n, a in agents.items() if not a.has_left}
        if not active:
            print("\n  💀 ALL MEMBERS HAVE LEFT")
            break

        # ========================
        # PHASE 2: TALK
        # ========================
        print(f"\n  {'─'*40}")
        print(f"  👥 Conversations")
        print(f"  {'─'*40}")
        pairs = select_conversation_pairs(agents, env, env.pending_proposals)
        all_conversations = []

        for agent_a_name, agent_b_name, context in pairs:
            if agents[agent_a_name].has_left or agents[agent_b_name].has_left:
                continue

            conv_id = f"r{round_num}_{agent_a_name.split()[-1].lower()}_{agent_b_name.split()[-1].lower()}"
            logger.log(round_num, "talk", "conversation_start", data={
                "conversation_id": conv_id,
                "participants": [agent_a_name, agent_b_name],
                "context": context,
            })

            history = []

            # Turn 1: A speaks
            turn1 = agents[agent_a_name].speak_in_conversation(agent_b_name, context, history, True)
            total_llm_calls += 1
            turn1["speaker"] = agent_a_name
            history.append(turn1)
            logger.log(round_num, "talk", "utterance", agent=agent_a_name, data={
                "conversation_id": conv_id, "turn": 1,
                "says": turn1.get("says", ""), "tone": turn1.get("tone", ""),
                "inner_thought": turn1.get("inner_thought", ""),
            })

            # Turn 2: B responds
            turn2 = agents[agent_b_name].speak_in_conversation(agent_a_name, context, history, False)
            total_llm_calls += 1
            turn2["speaker"] = agent_b_name
            history.append(turn2)
            logger.log(round_num, "talk", "utterance", agent=agent_b_name, data={
                "conversation_id": conv_id, "turn": 2,
                "says": turn2.get("says", ""), "tone": turn2.get("tone", ""),
                "inner_thought": turn2.get("inner_thought", ""),
            })

            # Turn 3: only if tension (low trust)
            trust_ab = agents[agent_a_name].memory.relationships.get(agent_b_name, {}).get("trust", 5)
            trust_ba = agents[agent_b_name].memory.relationships.get(agent_a_name, {}).get("trust", 5)
            if min(trust_ab, trust_ba) < 5:
                turn3 = agents[agent_a_name].speak_in_conversation(agent_b_name, context, history, True)
                total_llm_calls += 1
                turn3["speaker"] = agent_a_name
                history.append(turn3)
                logger.log(round_num, "talk", "utterance", agent=agent_a_name, data={
                    "conversation_id": conv_id, "turn": 3,
                    "says": turn3.get("says", ""), "tone": turn3.get("tone", ""),
                    "inner_thought": turn3.get("inner_thought", ""),
                })

            # Add conversation to both agents' memory
            exchange_lines = [f'{t["speaker"]}: "{t.get("says", "...")}"' for t in history]
            exchange_text = f"{date_str} conversation between {agent_a_name} and {agent_b_name}: " + " / ".join(exchange_lines)
            agents[agent_a_name].memory.add_recent(exchange_text)
            agents[agent_b_name].memory.add_recent(exchange_text)

            logger.log(round_num, "talk", "conversation_end", data={
                "conversation_id": conv_id,
                "turns": len(history),
            })

            all_conversations.append({
                "participants": [agent_a_name, agent_b_name],
                "context": context,
                "exchanges": history,
            })

            first_name_a = agent_a_name.split()[0]
            first_name_b = agent_b_name.split()[0]
            print(f"\n  👥 {first_name_a} & {first_name_b}")
            for t in history:
                speaker_first = t["speaker"].split()[0]
                says = t.get("says", "...").strip().strip('"')
                if rich:
                    inner = t.get("inner_thought", "").strip().strip('*')
                    tone = t.get("tone", "")
                    tone_str = f" ({tone})" if tone else ""
                    print(f'\n     {speaker_first}{tone_str}:')
                    print(wrap_text(f'💬 "{says}"', indent="       "))
                    if inner:
                        print(wrap_text(f"🧠 {inner}", indent="       "))
                else:
                    # Clean: first sentence only
                    dot = says.find(". ")
                    if dot > 40:
                        says = says[:dot+1]
                    elif len(says) > 80:
                        says = says[:77] + "..."
                    print(f'     {speaker_first}: "{says}"')

            if rich:
                print(f"  {'·'*30}")

        # ========================
        # PHASE 2b: VOTE
        # ========================
        all_votes = []
        for proposal in env.pending_proposals:
            print(f"\n  📜 VOTE: {proposal['proposal'][:60]}")
            logger.log(round_num, "vote", "vote_start", data={
                "proposal": proposal["proposal"],
                "proposed_by": proposal["proposed_by"],
                "context": f"Treasury: ${env.money}, Morale: {env.morale}%",
            })

            votes = {}
            for name, agent in active.items():
                vote_result = agent.vote_on_proposal(proposal["proposal"], proposal["proposed_by"], env)
                total_llm_calls += 1
                votes[name] = vote_result
                logger.log(round_num, "vote", "vote_cast", agent=name, data={
                    "vote": vote_result["vote"],
                    "reasoning": vote_result.get("reasoning", ""),
                    "inner_thought": vote_result.get("inner_thought", ""),
                    "dialogue": vote_result.get("dialogue", "nothing"),
                })
                vote_icon = "✅" if vote_result['vote'] == "YES" else "❌"
                print(f"     {vote_icon} {name}: {vote_result.get('reasoning', '')[:60]}")

            yes_count = sum(1 for v in votes.values() if v["vote"] == "YES")
            no_count = sum(1 for v in votes.values() if v["vote"] == "NO")
            passed = yes_count > no_count

            if passed:
                env.rules.append(f"{proposal['proposal']} (proposed by {proposal['proposed_by']})")

            result_str = "PASSED" if passed else "FAILED"
            logger.log(round_num, "vote", "vote_result", data={
                "proposal": proposal["proposal"],
                "result": result_str,
                "tally": {"YES": yes_count, "NO": no_count, "ABSTAIN": len(votes) - yes_count - no_count},
                "votes": {n: v["vote"] for n, v in votes.items()},
            })

            vote_memory = f"{date_str}: Vote on '{proposal['proposal']}' — {result_str} ({yes_count}-{no_count})"
            for agent in active.values():
                agent.memory.add_recent(vote_memory)

            all_votes.append({"proposal": proposal, "votes": votes, "result": result_str})
            result_icon = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {result_icon} ({yes_count} yes, {no_count} no)")

        # ========================
        # PHASE 3: REFLECT
        # ========================
        print(f"\n  {'─'*40}")
        print(f"  🪞 Reflections")
        print(f"  {'─'*40}")

        # Build today's summary
        today_parts = []
        for s in round_action_summaries:
            today_parts.append(s)
        for conv in all_conversations:
            conv_lines = [f'{e["speaker"]}: "{e.get("says", "...")}"' for e in conv["exchanges"]]
            today_parts.append(f"Conversation ({conv['context']}): " + " / ".join(conv_lines))
        for v in all_votes:
            today_parts.append(f"Vote on '{v['proposal']['proposal']}' — {v['result']}")
        today_summary = "\n".join(today_parts)

        active_names = list(active.keys())
        morale_scores = []  # v3: collect community morale assessments
        for name, agent in active.items():
            reflection = agent.reflect(today_summary, env, active_names)
            total_llm_calls += 1

            # v3: collect community morale score
            morale_scores.append(reflection.get("community_morale", 50))

            # Update memory from reflection
            agent.memory.set_concerns(reflection.get("concerns", agent.memory.concerns))

            for rel_name, rel_data in reflection.get("relationships", {}).items():
                agent.memory.update_relationship(
                    rel_name,
                    attitude=rel_data.get("attitude"),
                    trust=rel_data.get("trust"),
                    last_interaction=date_str,
                )

            if reflection.get("key_moment"):
                agent.memory.add_key_moment(
                    round_num,
                    reflection["key_moment"],
                    reflection.get("key_emotion", "mixed"),
                )
                logger.log(round_num, "reflect", "key_moment", agent=name, data={
                    "description": reflection["key_moment"],
                    "emotion": reflection.get("key_emotion", "mixed"),
                })

            if reflection.get("observation"):
                obs = reflection["observation"]
                agent.memory.add_observation(obs["about"], obs["detail"], round_num)

            # Update satisfaction
            sat_delta = reflection.get("satisfaction_change", 0)
            agent.satisfaction = max(0, min(100, agent.satisfaction + sat_delta))

            logger.log(round_num, "reflect", "reflection", agent=name, data={
                "summary": reflection.get("summary", ""),
                "mood": reflection.get("mood", "neutral"),
                "satisfaction": agent.satisfaction,
                "concerns_updated": list(agent.memory.concerns),
                "key_moment": reflection.get("key_moment"),
                "relationships_updated": {
                    rn: {"trust": rd["trust"], "attitude": rd.get("attitude", "")}
                    for rn, rd in agent.memory.relationships.items()
                },
                "observation": reflection.get("observation"),
                "community_morale": reflection.get("community_morale", 50),  # v3
            })

            mood = reflection.get('mood', 'neutral')
            mood_e = get_mood_emoji(mood)
            first = name.split()[0]

            if rich:
                summary = reflection.get('summary', '')
                key_moment = reflection.get('key_moment', '')
                key_emotion = reflection.get('key_emotion', '')
                sat_delta = reflection.get('satisfaction_change', 0)
                sat_str = f"sat {agent.satisfaction}"
                if sat_delta > 0:
                    sat_str += f" (+{sat_delta})"
                elif sat_delta < 0:
                    sat_str += f" ({sat_delta})"

                print(f"\n  {mood_e} {first} ({sat_str}) — {mood}")
                if summary:
                    print(wrap_text(summary))
                if key_moment:
                    emotion_str = f" [{key_emotion}]" if key_emotion else ""
                    print(wrap_text(f"★ {key_moment}{emotion_str}"))
                print(f"  {'·'*30}")
            else:
                print(f"  {mood_e} {first} (sat {agent.satisfaction}) — {mood}")

        # --- v3: Update community morale from agents' assessments ---
        if morale_scores:
            old_morale = env.morale
            env.morale = round(sum(morale_scores) / len(morale_scores))
            env.morale = max(0, min(100, env.morale))
            logger.log(round_num, "reflect", "morale_update", data={
                "individual_scores": dict(zip(active_names, morale_scores)),
                "new_morale": env.morale,
                "old_morale": old_morale,
            })
            direction = "📈" if env.morale > old_morale else "📉" if env.morale < old_morale else "➡️"
            print(f"\n  {direction} Community morale: {old_morale}% → {env.morale}%")

        # --- Gossip spread ---
        spread_gossip(agents, round_num, logger)

        # --- v2: Speech fatigue — erode trust toward chronic speechifiers ---
        for name, agent in active.items():
            if agent.consecutive_speeches >= 3:
                for other_name, other_agent in active.items():
                    if other_name != name:
                        rel = other_agent.memory.relationships.get(name, {})
                        old_trust = rel.get("trust", 5)
                        if old_trust > 1:
                            other_agent.memory.update_relationship(name, trust=old_trust - 1)
                logger.log(round_num, "reflect", "speech_fatigue", agent=name, data={
                    "consecutive_speeches": agent.consecutive_speeches,
                })
                print(f"  ⚠️  {name} has been speechifying for {agent.consecutive_speeches} rounds straight")

        # --- v2: Clear event catalyst after one round ---
        env.event_catalyst = None

        # --- Environment tick ---
        env.apply_building_decay()
        tick_deltas = env.tick(len(active))
        logger.log(round_num, "env", "env_tick", data=tick_deltas)

        # Check termination
        active = {n: a for n, a in agents.items() if not a.has_left}
        if not active:
            print("\n  💀 ALL MEMBERS HAVE LEFT")
            break
        if env.morale <= 10:
            print(f"\n  🔥 COMMUNITY MORALE CRITICAL: {env.morale}%")

    # --- Sim end ---
    wall_time = time.time() - start_time
    logger.log(round_num, "meta", "sim_end", data={
        "rounds_completed": round_num,
        "final_state": env.snapshot(),
        "departed": list(env.departed),
        "survived": [n for n, a in agents.items() if not a.has_left],
        "total_events": logger.seq,
        "total_llm_calls": total_llm_calls,
        "wall_time_seconds": round(wall_time, 1),
    })
    logger.close()

    departed_str = ', '.join(env.departed) if env.departed else 'None'
    survived = [n for n, a in agents.items() if not a.has_left]
    survived_str = ', '.join(survived) if survived else 'None'

    print(f"\n  {'═'*52}")
    print(f"  🏛️  SIMULATION COMPLETE")
    print(f"  {'─'*52}")
    print(f"  Rounds: {round_num} · LLM calls: {total_llm_calls} · {wall_time:.0f}s")
    print(f"  🌾 Food: {env.food}  💰 Money: ${env.money}  ❤️ Morale: {env.morale}%")
    print(f"  👥 Survived: {survived_str}")
    print(f"  🚪 Departed: {departed_str}")
    print(f"  {'─'*52}")
    print(f"  📁 {run_dir}/events.jsonl ({logger.seq} events)")
    print(f"  ▶  python replay.py {run_dir} -i")
    print(f"  📊 python derive.py {run_dir}/events.jsonl")
    print(f"  {'═'*52}\n")

    return {"run_dir": run_dir, "events": logger.seq, "llm_calls": total_llm_calls}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brook Farm v3 simulation")
    parser.add_argument("rounds", nargs="?", type=int, default=MAX_ROUNDS, help="Number of rounds")
    parser.add_argument("--config", type=str, help="Path to experiment config JSON")
    parser.add_argument("--backend", choices=["cli", "api"], default=BACKEND,
                        help="LLM backend: 'cli' (claude CLI / Max sub) or 'api' (Anthropic API key)")
    parser.add_argument("--model", default=MODEL, help="Model to use")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--personas", type=str, help="Path to personas JSON file (default: personas/brook_farm.json)")
    parser.add_argument("--clean", action="store_true", help="Clean compact output (default: rich detailed output)")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        # CLI args override config file
        if args.backend != BACKEND:
            config["backend"] = args.backend
        if args.model != MODEL:
            config["model"] = args.model
        if args.personas:
            config["personas"] = args.personas
        config["clean"] = args.clean
    else:
        config = {
            "name": "run",
            "rounds": args.rounds,
            "seed": args.seed,
            "model": args.model,
            "backend": args.backend,
        }
        if args.personas:
            config["personas"] = args.personas
        config["clean"] = args.clean

    run_simulation(config)
