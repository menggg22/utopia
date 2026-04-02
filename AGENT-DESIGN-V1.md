# Agent System Design v1

## Round Structure

Each round now has **3 phases**, not just 1:

```
PHASE 1: OBSERVE + ACT (morning)
  - Each agent sees the environment state
  - Each agent picks an action (farm, teach, build, write, etc.)
  - Actions resolve, environment updates

PHASE 2: INTERACT (afternoon/evening)
  - 2-3 conversation pairs selected (random, or tension-based)
  - Each pair has a short back-and-forth (2-3 exchanges)
  - Conversations produce: public dialogue, private impressions, relationship updates
  - If anyone PROPOSED a rule in Phase 1, a VOTE happens here

PHASE 3: REFLECT (night)
  - Each agent privately updates their memory
  - Key moments get flagged (auto-detected from emotional intensity)
  - Relationship attitudes update based on the day
  - Concerns list updates
  - This is one LLM call per agent — "what do you think about today?"
```

## Memory System

```python
@dataclass
class AgentMemory:
    # Permanent — never trimmed
    key_moments: list[dict]    # {"day": 5, "event": "...", "emotion": "..."}

    # Relationships — updated each round
    relationships: dict[str, dict]  # {
    #   "George Ripley": {
    #     "attitude": "respectful but worried",  # free text, updated by agent
    #     "trust": 7,          # 1-10
    #     "last_interaction": "Day 5: he asked me to farm more"
    #   }
    # }

    # Running concerns — things on their mind
    concerns: list[str]        # ["money is running out", "I can't write here"]

    # Recent events — sliding window
    recent: list[str]          # last 15 events

    # Gossip / observations about others (shareable)
    observations: list[dict]   # {"about": "Hawthorne", "observation": "hasn't farmed in 3 days", "day": 7}
```

### How memory feeds into decisions

The OBSERVE+ACT prompt includes:
- Environment state (resources, season, events)
- Recent events (last 10)
- Current concerns (all)
- Relationship summary (all attitudes, 1 line each)
- Other agents' recent observations ABOUT this agent (gossip they'd hear)

The REFLECT prompt includes:
- What happened today (actions, conversations)
- Current key moments, concerns, relationships
- Ask: "What stays with you? What worries you? How do you feel about each person now?"

## Conversation System

### Pair Selection

Each round, select 2-3 conversation pairs:

```python
def select_pairs(agents, env):
    pairs = []

    # 1. If there's a pending proposal, the proposer talks to the most skeptical member
    # 2. If tension exists (low trust between two agents), they interact
    # 3. Otherwise, random pair weighted by existing relationship strength
    # 4. Married couples (George + Sophia) have higher interaction probability

    return pairs  # [(agent_a, agent_b, context), ...]
```

### Conversation Flow

Each pair gets 2-3 exchanges:

```
Turn 1: Agent A speaks (sees context + relationship memory)
Turn 2: Agent B responds (sees A's words + own relationship memory)
Turn 3: Agent A responds (optional — only if the conversation has tension)
```

Each response includes:
- SAYS: what they say aloud
- TONE: warm, tense, diplomatic, frustrated, playful
- INNER_THOUGHT: what they really think during this exchange

After conversation, both agents get:
- The full exchange added to recent memory
- A relationship update prompt: "How do you feel about [other] after this conversation?"

### Voting

When a PROPOSE action happens:
1. The proposal is announced
2. In Phase 2, instead of random pairs, ALL agents discuss the proposal
3. Each agent votes: YES / NO / ABSTAIN with reasoning
4. Majority wins
5. The vote and reasoning are logged (rich data for documentary)

## Action Space (expanded)

Phase 1 actions:
```
FARM          — work fields (+food, -satisfaction)
TEACH         — run school (+money, +satisfaction for educators)
BUILD <what>  — construction (-money, +building)
WRITE         — personal writing (+satisfaction, 0 community)
ORGANIZE <what> — cultural event (+morale)
PROPOSE <rule>  — triggers vote in Phase 2
TRADE         — sell goods to visitors (+money, requires effort)
REPAIR        — fix buildings/tools (prevents decay)
REST          — personal time
LEAVE         — depart permanently
```

New additions:
- **TRADE**: Sell handmade goods or host paying visitors
- **REPAIR**: Prevent building decay (buildings deteriorate without maintenance)

## Observation Sharing (Gossip)

Each agent generates observations about others during REFLECT:
```
"I noticed Hawthorne wasn't in the fields again today."
"Dana seems to be the only one who truly understands our finances."
"Sophia looked exhausted — she hasn't rested in weeks."
```

These observations are:
1. Stored in the observing agent's memory
2. **Shared probabilistically** — 50% chance another random agent "hears" it next round
3. The observed agent never sees observations about themselves directly
4. Creates emergent gossip dynamics

## LLM Calls Per Round

| Phase | Calls | Purpose |
|-------|-------|---------|
| Phase 1: Act | 5 | One per agent: choose action |
| Phase 2: Talk | 4-6 | 2-3 pairs × 2 exchanges each |
| Phase 2: Vote | 5 (if proposal) | One per agent: vote + reasoning |
| Phase 3: Reflect | 5 | One per agent: update memory |

**Total per round**: ~14-16 calls (no vote) or ~19-21 (with vote)
**30 rounds**: ~450-630 calls
**Cost with Haiku**: ~$0.50-0.80 per run (still very cheap)

## Data Output Additions

### characters.json additions
```json
{
  "George Ripley": [
    {
      "round": 5,
      "action": "TEACH",
      "mood": "anxious",
      "satisfaction": 62,
      "concerns": ["money running low", "Hawthorne not farming"],
      "relationships": {
        "Nathaniel Hawthorne": {"trust": 5, "attitude": "worried about his commitment"},
        "Sophia Ripley": {"trust": 9, "attitude": "grateful for her steadiness"},
        "Charles Dana": {"trust": 8, "attitude": "impressed by his energy"},
        "John Sullivan Dwight": {"trust": 6, "attitude": "wish he'd farm more"}
      },
      "key_moment_added": null,
      "observation_made": "Hawthorne was writing by the window again instead of working"
    }
  ]
}
```

### conversations.json (new)
```json
[
  {
    "round": 5,
    "date": "Jan 1842",
    "participants": ["George Ripley", "Nathaniel Hawthorne"],
    "context": "Ripley concerned about Hawthorne's farming contribution",
    "exchanges": [
      {
        "speaker": "George Ripley",
        "says": "Nathaniel, we need every hand in the fields this week...",
        "tone": "diplomatic",
        "inner_thought": "I hate asking him. He looks miserable out there."
      },
      {
        "speaker": "Nathaniel Hawthorne",
        "says": "I understand, George. I shall do my part tomorrow.",
        "tone": "resigned",
        "inner_thought": "My hands are already ruined. How much longer can I endure this?"
      }
    ],
    "relationship_updates": {
      "George Ripley -> Nathaniel Hawthorne": "He agreed but I saw no conviction in his eyes.",
      "Nathaniel Hawthorne -> George Ripley": "He means well but doesn't understand what this costs me."
    }
  }
]
```

### votes.json (new, if any proposals)
```json
[
  {
    "round": 15,
    "proposal": "Build the Phalanstery for $7,000",
    "proposed_by": "George Ripley",
    "votes": {
      "George Ripley": {"vote": "YES", "reasoning": "This is our future..."},
      "Nathaniel Hawthorne": {"vote": "NO", "reasoning": "We cannot afford this..."},
      "Sophia Ripley": {"vote": "YES", "reasoning": "If it brings more students..."},
      "Charles Dana": {"vote": "YES", "reasoning": "Ambitious but needed..."},
      "John Sullivan Dwight": {"vote": "YES", "reasoning": "Imagine the concert hall!"}
    },
    "result": "PASSED (4-1)",
    "aftermath": "Hawthorne was visibly displeased. Construction begins."
  }
]
```

## Implementation Order

1. Refactor AgentMemory (structured memory)
2. Update Phase 1 (act) to use structured memory in prompt
3. Add Phase 2 (conversation pairs + voting)
4. Add Phase 3 (reflect + memory update)
5. Add observation sharing (gossip)
6. Update logging (conversations.json, votes.json, richer characters.json)
7. Test with 5 rounds
8. Full 30-round run
