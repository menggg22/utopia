# How the Simulation Works

This document explains the system architecture — how persona cards become autonomous agents, how memory shapes behavior over time, and why the design produces emergent historical parallels without being told what happened.

## The Core Loop

Each simulation round represents roughly two months of commune life. A 30-round run covers April 1841 to February 1845.

Every round has three phases:

```
ACT  →  Each agent observes the world and chooses one action
TALK →  2-3 conversation pairs interact; votes happen if rules were proposed
REFLECT → Each agent privately updates their memory, relationships, and concerns
```

This mirrors real commune life: you work, you talk to people, you go home and think about what happened. The separation matters — agents can say one thing in conversation and think another in reflection.

## Persona Cards

Each agent is built from historical research — biographies, letters, diaries, contemporary accounts. A persona card has six fields:

| Field | What it does |
|-------|-------------|
| **Background** | Who they were before Brook Farm. Sets baseline knowledge and class. |
| **Motivation** | Why they joined. Hawthorne wanted money to marry. Ripley wanted to prove God right. |
| **Personality** | How they behave under pressure. Sardonic, tireless, sensitive. |
| **Skills** | What they're good at. Determines which actions feel natural vs forced. |
| **Private goal** | Known only to the agent. Often contradicts the stated motivation. |

The critical design decision: **we never tell agents what historically happened.** Hawthorne's persona says he's a skeptic who wants to save money for marriage. It does not say he left after 18 months. If he leaves, it's because the simulation dynamics pushed him there.

The persona is injected as a system prompt on every LLM call. The agent doesn't "forget" who it is between rounds.

## Memory Architecture

Agents don't have perfect recall. They have structured memory with five components:

```
AgentMemory
├── key_moments[]      Permanent. "The phalanstery burned." Max 5 shown per prompt.
├── relationships{}    Per-person trust (1-10) + attitude. Updated every reflection.
├── concerns[]         Current worries. Replaced wholesale each reflection.
├── recent[]           Sliding window of last 15 events. Oldest dropped.
└── observations[]     Things noticed about others. Can spread as gossip.
```

**Key moments** are the agent's autobiography. Most days produce none — the prompt explicitly says "you should have at most 3-5 key moments across an entire year." When Hawthorne leaves, everyone who witnesses it records a key moment. These persist forever and shape all future decisions.

**Relationships** evolve through interaction. Trust starts at 5/10. Married couples (the Ripleys) start at 8. Each reflection, the agent re-evaluates trust and attitude toward everyone. A conversation that goes well raises trust. A perceived betrayal drops it. These numbers feed back into conversation pair selection — low-trust pairs generate "tension conversations."

**Concerns** are the agent's internal priority list. Replaced each reflection, not appended. If food is running low, concerns shift from "can I write here?" to "we might starve." This creates realistic attention — agents stop caring about intellectual life when survival is at stake.

**Observations** are what agents notice about each other: "Dana gave another speech about money but didn't farm." These can spread through gossip (50% chance per round per observation). When gossip reaches someone, it enters their gossip inbox and appears in their next action prompt as "what others have said about you."

## The Action Space

Each round, each agent picks one action:

| Action | Effect | Satisfaction |
|--------|--------|-------------|
| FARM | +8 food | -3 (miserable) |
| TEACH | +$10 school income | +5 (fulfilling) |
| BUILD | -$30, +building | +2 |
| TRADE | +$15 from visitors | +2 |
| ORGANIZE | +5 community morale | +5 |
| SPEAK | Address the community | 0 |
| WRITE | Personal creative work | +8 (most satisfying) |
| REST | Personal time | +2 |
| PROPOSE | Suggest rule, triggers vote | 0 |
| REPAIR | Fix deteriorating building, -$10 | +2 |
| LEAVE | Permanent departure | — |

Notice the tension: **farming is the most necessary action and the least rewarding.** Writing is the most satisfying and produces nothing for the community. This is the intellectual farming problem baked into the mechanics, and it mirrors exactly what happened at Brook Farm.

The LLM chooses freely. Nothing forces Hawthorne to farm or Sophia to teach. But Sophia's persona says she ran the school for six years, so she tends to teach. Hawthorne's says he couldn't write and his hands were covered in blisters — so he avoids farming and eventually leaves.

## Satisfaction and Departure

Each agent has a satisfaction score (0-100, starts at 70). It changes based on actions taken and reflection. Farming costs 3 points. Writing gains 8. A bad day's reflection can cost up to 10.

Satisfaction doesn't directly trigger departure. The agent decides to LEAVE through the same LLM decision process as every other action. But low satisfaction makes the agent more likely to choose it — a person at satisfaction 15 with concerns like "I cannot write here" and "this experiment is failing" will eventually pick LEAVE.

This produces realistic departure patterns. Hawthorne doesn't leave on a timer. He leaves when his persona, his memory of recent events, his deteriorating relationships, and his satisfaction all align to make leaving the obvious choice.

## Conversations

Each round, 2-3 pairs of agents talk. Pair selection follows priority:

1. **Proposal debates** — If someone proposed a rule, they talk to the most skeptical member (lowest trust toward them).
2. **Tension pairs** — The two agents with the lowest mutual trust. These are the arguments.
3. **Random weighted** — Remaining pair, weighted by trust. Married couples get a bonus. These are the friendships.

Each conversation is 4 turns (2 per agent). Every turn has three outputs:

```
SAYS: "George, I've been thinking about the finances..."  (public)
TONE: diplomatic                                           (public)
INNER_THOUGHT: "He won't listen. He never does."          (private)
```

The inner thought is invisible to the other agent but logged. It reveals when agents are being strategic versus authentic. Dana might say "I support the vision" while thinking "this place is going bankrupt."

After conversations, observations from them feed back into memory and can spread as gossip.

## Gossip

After each reflection phase, observations spread. Each observation has a 50% chance of reaching a random third party. The mechanism:

1. Agent A observes: "Hawthorne didn't farm again today."
2. Next round, 50% chance this reaches Agent C (but not Hawthorne).
3. Agent C now sees in their prompt: "Someone said about Hawthorne: 'didn't farm again today.'"
4. This influences C's next action and reflection.

Gossip creates social pressure without direct confrontation. In our runs, Hawthorne's refusal to farm becomes common knowledge through gossip before anyone confronts him about it.

## The Environment

The shared world has three resources:

- **Food** — Depletes by 5 per agent per round. FARM adds 8. If food hits 0, the community spends $20 buying emergency food (if they can afford it). Winter costs extra.
- **Money** — School generates $3-15/round (scales with morale — students leave when the community struggles). Operating costs: $10/round. Trading, teaching add more.
- **Morale** — Starts at 80. Drops when food is low, money is low, or people leave. Organizing events raises it. At 0, the community is in freefall.

The economy is deliberately tight. Five agents consuming 25 food/round need roughly 3 FARM actions per round to break even. In practice, agents farm 0.3-0.7 times per round. The deficit is structural.

## Historical Events

Scripted events fire at specific rounds, matching the real Brook Farm timeline:

| Round | Event |
|-------|-------|
| 8 | Boston visitors tour the community (+$20) |
| 12 | Albert Brisbane visits, argues for Fourierism |
| 15 | Phalanstery proposal ($7,000 building project) |
| 18 | New York Observer attacks the community's morals |
| 20 | Smallpox outbreak (morale -15) |
| 24 | Phalanstery fire (uninsured, -$200, morale -25) |

These are injected as environmental events. Agents react to them through their personas and current state. The Fourierist visit matters more when the community is already struggling — agents grasp at structural solutions.

## Building Decay

Buildings have health. Each round, 10% chance a healthy building starts deteriorating. After 3 rounds unrepaired, it's gone. Someone has to choose REPAIR (-$10) instead of doing something personally rewarding.

This creates another instance of the commons problem: everyone benefits from buildings, but repairing them costs individual satisfaction.

## Voting

When an agent proposes a rule, every active member votes (YES / NO / ABSTAIN) via an LLM call. The vote considers:
- The proposal's merits
- Their relationship with the proposer (trust matters)
- Their current concerns
- Their persona

Majority passes. Adopted rules appear in the environment summary but are not mechanically enforced — they're social contracts. Whether agents follow them depends on whether the rule aligns with their persona and incentives.

## What Makes This Produce Realistic Outcomes

The system doesn't simulate history. It simulates people in a situation and lets history emerge. Several design choices make this work:

**Persona-driven behavior over utility maximization.** Agents don't optimize for community survival. They act in character. Hawthorne writes because he's a writer, not because writing helps the commune.

**Asymmetric satisfaction.** The actions the community needs (farming) hurt the individual. The actions individuals want (writing, teaching) don't feed anyone. This is the actual structural problem of utopian communities.

**Memory creates path dependence.** A bad conversation in round 3 lowers trust, which makes future conversations tenser, which lowers trust further. Relationships spiral. Key moments anchor the narrative — once Hawthorne records "I cannot write here" as a key moment, it colors every subsequent decision.

**Gossip creates social dynamics without central coordination.** Nobody announces "Hawthorne isn't farming." But everyone knows, because observations spread probabilistically. Social pressure builds organically.

**Inner thoughts reveal the gap between public and private.** Agents maintain a public face while privately doubting. This is exactly how real communes operated — the meeting minutes look fine, but the diaries tell a different story.

## Configuration

Experiments are JSON configs:

```json
{
  "name": "no_hawthorne",
  "rounds": 30,
  "seed": 42,
  "agents": ["George Ripley", "Sophia Ripley", "Charles Dana", "John Sullivan Dwight"],
  "environment": {"food": 100, "money": 500, "morale": 80}
}
```

Remove an agent, double the food, change the seed. The same system produces different outcomes because the dynamics are emergent, not scripted. Remove Hawthorne and the community is happier. Remove Sophia and it goes bankrupt. Double the food and nothing changes — because the problem was never food.

## Technical Details

- **LLM**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`). Fast and cheap enough for 300+ calls per run.
- **Backends**: Claude Code CLI or Anthropic API directly.
- **Logging**: Append-only JSONL event stream. 15 event types. Single source of truth.
- **Derived outputs**: `derive.py` extracts narrative, character arcs, metrics, conversations, and votes from the event stream.
- **Comparison**: `compare.py` does cross-run analysis (departures, action distributions, satisfaction trajectories).
- **Runtime**: ~80 minutes for a 30-round run via CLI, ~20 minutes via API.
