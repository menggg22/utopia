# Logging Specification — Utopia v1

## Principle

**One event stream. Everything derives from it.**

A single append-only JSONL file (`events.jsonl`) captures every event in the simulation. All other outputs (narrative, character arcs, charts, documentary) are **views** computed from this stream.

```
events.jsonl  ← single source of truth
    ├── narrative.md       (derived: human-readable story)
    ├── characters.json    (derived: per-character arc)
    ├── metrics.csv        (derived: environment time series)
    ├── conversations.json (derived: all dialogues)
    └── summary.txt        (derived: quick overview)
```

The event stream is **append-only** and **never modified** during a run. Derivation happens after the simulation completes (or can be streamed live).

---

## Event Format

Every line in `events.jsonl` is a JSON object with these required fields:

```json
{
  "seq": 142,                    // global sequence number (monotonic)
  "round": 5,                   // simulation round (1-indexed)
  "phase": "act",               // "setup" | "act" | "talk" | "vote" | "reflect" | "env" | "meta"
  "type": "action",             // event type (see catalog below)
  "ts": "2026-04-01T23:15:42",  // wall clock time (when this event was created)
  "date": "Jan 1842",           // in-simulation historical date
  "agent": "Nathaniel Hawthorne", // who (null for environment/meta events)
  "data": { ... }               // event-specific payload
}
```

---

## Event Catalog

### Phase: `setup` (once, at simulation start)

**`sim_start`** — Simulation begins
```json
{
  "type": "sim_start",
  "data": {
    "model": "claude-haiku-4-5-20251001",
    "max_rounds": 30,
    "n_agents": 5,
    "agents": ["George Ripley", "Nathaniel Hawthorne", ...],
    "initial_state": { "food": 100, "money": 500, "morale": 80 }
  }
}
```

**`persona_loaded`** — Agent persona initialized (one per agent)
```json
{
  "type": "persona_loaded",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "role": "Founding member, Trustee of Finance",
    "age": 37,
    "background": "...",
    "motivation": "...",
    "personality": "...",
    "skills": ["writing", "observation", "financial management"],
    "private_goal": "..."
  }
}
```

---

### Phase: `env` (environment changes)

**`env_state`** — Full environment snapshot (start of each round)
```json
{
  "type": "env_state",
  "data": {
    "food": 85, "money": 420, "morale": 72,
    "season": "summer",
    "members_present": 5,
    "buildings": ["The Hive", "The Nest"],
    "rules": [],
    "departed": [],
    "bulletin_board_size": 12
  }
}
```

**`env_tick`** — Environment resource changes (end of each round)
```json
{
  "type": "env_tick",
  "data": {
    "food_consumed": 25, "food_produced": 16, "food_net": -9,
    "money_earned": 25, "money_spent": 10, "money_net": 15,
    "morale_change": -5,
    "season_change": null
  }
}
```

**`historical_event`** — Scripted historical events
```json
{
  "type": "historical_event",
  "data": {
    "title": "Fourier Conversion Pressure",
    "description": "Albert Brisbane visits and argues for Fourierist reorganization...",
    "effects": { "morale": 0, "money": 0 }
  }
}
```

**`random_event`** — Stochastic events (weather, visitors, disease)
```json
{
  "type": "random_event",
  "data": {
    "title": "Winter Storm",
    "description": "A harsh storm damages supplies.",
    "effects": { "food": -10 }
  }
}
```

---

### Phase: `act` (agent actions)

**`action`** — An agent takes their daily action
```json
{
  "type": "action",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "chosen_action": "WRITE",
    "reasoning": "I must put pen to paper. The stories in my head will rot if I don't.",
    "inner_thought": "Another day I've avoided the fields. Ripley will notice. But I cannot bear it — my hands, my spirit, all of it rebels against the plow.",
    "observation": "George looked haggard at breakfast. Dana was already in the fields by dawn — that young man never stops. Dwight was humming Beethoven, oblivious as always.",
    "mood": "restless",
    "dialogue": "nothing",
    "effects": { "food": 0, "money": 0, "satisfaction_delta": 8 },
    "satisfaction_after": 78,
    "raw_llm_response": "ACTION: WRITE\nREASONING: ..."
  }
}
```

**`action_effect`** — The resolved consequence (separate from decision)
```json
{
  "type": "action_effect",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "description": "Nathaniel Hawthorne retreated to write in solitude. The pen moved freely.",
    "resource_changes": { "satisfaction": 8 }
  }
}
```

---

### Phase: `talk` (conversations)

**`conversation_start`** — A conversation pair is selected
```json
{
  "type": "conversation_start",
  "data": {
    "participants": ["George Ripley", "Nathaniel Hawthorne"],
    "context": "Ripley concerned about Hawthorne's farming contribution",
    "selection_reason": "tension (trust 5/10, Hawthorne hasn't farmed in 3 rounds)"
  }
}
```

**`utterance`** — One line of dialogue in a conversation
```json
{
  "type": "utterance",
  "agent": "George Ripley",
  "data": {
    "conversation_id": "r5_ripley_hawthorne",
    "turn": 1,
    "says": "Nathaniel, I wonder if you might join us in the fields tomorrow. We are short-handed and the hay won't wait.",
    "tone": "diplomatic",
    "inner_thought": "I hate asking him. He looks miserable out there. But others are watching — if he doesn't work, why should they?",
    "body_language": "Places a hand on Hawthorne's shoulder, voice gentle but firm."
  }
}
```

**`conversation_end`** — Conversation concludes with relationship updates
```json
{
  "type": "conversation_end",
  "data": {
    "conversation_id": "r5_ripley_hawthorne",
    "turns": 3,
    "relationship_updates": [
      {
        "from": "George Ripley",
        "to": "Nathaniel Hawthorne",
        "trust_change": -1,
        "new_attitude": "He agreed but I saw no conviction in his eyes. I fear he will leave us.",
        "trust_after": 4
      },
      {
        "from": "Nathaniel Hawthorne",
        "to": "George Ripley",
        "trust_change": 0,
        "new_attitude": "He means well. But he cannot understand what this place costs a man who lives by his pen.",
        "trust_after": 6
      }
    ]
  }
}
```

---

### Phase: `vote` (when proposals are made)

**`vote_start`** — A proposal goes to vote
```json
{
  "type": "vote_start",
  "data": {
    "proposal": "Build the Phalanstery — a grand communal building for $7,000",
    "proposed_by": "George Ripley",
    "context": "The community has $420 in the treasury. This would require massive debt."
  }
}
```

**`vote_cast`** — Individual vote
```json
{
  "type": "vote_cast",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "vote": "NO",
    "reasoning": "We are already in debt. This is vanity disguised as vision.",
    "inner_thought": "Ripley has lost his sense of proportion. This building will be our tomb.",
    "dialogue": "I cannot in good conscience support spending money we do not have on a building we do not need."
  }
}
```

**`vote_result`** — Final tally
```json
{
  "type": "vote_result",
  "data": {
    "proposal": "Build the Phalanstery",
    "result": "PASSED",
    "tally": { "YES": 4, "NO": 1, "ABSTAIN": 0 },
    "votes": {
      "George Ripley": "YES",
      "Nathaniel Hawthorne": "NO",
      "Sophia Ripley": "YES",
      "Charles Dana": "YES",
      "John Sullivan Dwight": "YES"
    }
  }
}
```

---

### Phase: `reflect` (nightly reflection)

**`reflection`** — Agent's end-of-day private reflection
```json
{
  "type": "reflection",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "summary": "A wasted day, in truth. I wrote little and farmed nothing...",
    "mood": "melancholy",
    "satisfaction": 65,
    "concerns_updated": [
      "I am not saving money here — I am spending my health.",
      "Sophia Peabody waits for me. Every day here is a day stolen from our life together."
    ],
    "key_moment": null,
    "relationships_updated": {
      "George Ripley": { "trust": 6, "attitude": "I respect the man but pity his dream." },
      "Charles Dana": { "trust": 7, "attitude": "The most capable among us. He will go far." },
      "John Sullivan Dwight": { "trust": 5, "attitude": "A pleasant companion, useless in the fields." },
      "Sophia Ripley": { "trust": 7, "attitude": "The school is the only thing that works here. Her doing." }
    },
    "observations_shared": [
      { "about": "George Ripley", "observation": "looked exhausted and worried at supper" }
    ],
    "raw_llm_response": "..."
  }
}
```

**`key_moment`** — A moment flagged as permanently memorable
```json
{
  "type": "key_moment",
  "agent": "George Ripley",
  "data": {
    "description": "Watched the Phalanstery burn. Everything we built, gone in two hours.",
    "emotion": "devastation",
    "trigger": "historical_event:phalanstery_fire"
  }
}
```

**`gossip_spread`** — An observation gets shared to another agent
```json
{
  "type": "gossip_spread",
  "data": {
    "origin": "Charles Dana",
    "hearer": "Sophia Ripley",
    "about": "Nathaniel Hawthorne",
    "observation": "hasn't farmed in three rounds",
    "original_round": 4
  }
}
```

---

### Phase: `meta` (simulation-level events)

**`agent_departed`** — Someone leaves
```json
{
  "type": "agent_departed",
  "agent": "Nathaniel Hawthorne",
  "data": {
    "round": 8,
    "date": "Oct 1842",
    "final_satisfaction": 35,
    "final_relationships": { ... },
    "final_concerns": [ ... ],
    "parting_words": "I shall remember this place, George, though not as you would wish.",
    "inner_thought": "Thank God. My soul is not utterly buried under a dung-heap."
  }
}
```

**`sim_end`** — Simulation complete
```json
{
  "type": "sim_end",
  "data": {
    "rounds_completed": 30,
    "final_state": { "food": 12, "money": -200, "morale": 15 },
    "departed": ["Nathaniel Hawthorne"],
    "survived": ["George Ripley", "Sophia Ripley", "Charles Dana", "John Sullivan Dwight"],
    "total_events": 892,
    "total_llm_calls": 510,
    "total_tokens": 180000,
    "wall_time_seconds": 340
  }
}
```

---

## File Structure

```
runs/
  run_20260401_231542/
    events.jsonl          ← THE source of truth (append-only during run)
    narrative.md          ← derived after run
    characters.json       ← derived: per-character arcs
    metrics.csv           ← derived: food,money,morale per round
    conversations.json    ← derived: all dialogues extracted
    votes.json            ← derived: all votes extracted
    summary.txt           ← derived: quick overview
    config.json           ← run configuration (model, rounds, seed)
```

## Derivation Scripts (future)

```bash
# Generate narrative from events
python derive.py narrative runs/run_XXX/events.jsonl > runs/run_XXX/narrative.md

# Extract character arcs
python derive.py characters runs/run_XXX/events.jsonl > runs/run_XXX/characters.json

# Extract metrics for charting
python derive.py metrics runs/run_XXX/events.jsonl > runs/run_XXX/metrics.csv

# Extract all conversations
python derive.py conversations runs/run_XXX/events.jsonl > runs/run_XXX/conversations.json

# Full derivation (all outputs)
python derive.py all runs/run_XXX/events.jsonl
```

---

## Logger Implementation

```python
class EventLogger:
    def __init__(self, path: str):
        self.path = path
        self.seq = 0
        self.f = open(path, 'a')

    def log(self, round: int, phase: str, type: str, agent: str = None, data: dict = None):
        self.seq += 1
        event = {
            "seq": self.seq,
            "round": round,
            "phase": phase,
            "type": type,
            "ts": datetime.now().isoformat(),
            "date": day_to_date(round),
            "agent": agent,
            "data": data or {},
        }
        self.f.write(json.dumps(event) + "\n")
        self.f.flush()  # write immediately — survive crashes

    def close(self):
        self.f.close()
```

Key design decisions:
- **JSONL not JSON** — append-only, survives crashes, streamable
- **flush every write** — if the sim crashes at round 20, you still have 1-19
- **seq numbers** — total ordering even if timestamps collide
- **agent is nullable** — environment and meta events have no agent

---

## What This Enables for Documentary

With this event stream, a visualization tool can:

1. **Timeline view**: Scrub through rounds, see all events in order
2. **Character focus**: Filter events by agent, see their full arc
3. **Relationship graph**: Animate trust levels over time, show who talked to whom
4. **Resource charts**: Plot food/money/morale over time with event annotations
5. **Conversation reader**: Read dialogues with inner thoughts revealed (or hidden)
6. **Key moments**: Highlight the turning points flagged by agents themselves
7. **Gossip network**: Visualize how observations spread through the community
8. **Counterfactual**: Compare multiple runs — same personas, different outcomes
9. **Historical comparison**: Overlay real Brook Farm timeline on simulation timeline

All from one file. No cross-referencing needed.
