# Agent Society Experiment — Design Doc

**Date**: April 1, 2026
**Status**: Design phase
**Vibe**: Fun experiment, not a product

---

## Core Idea

Create a simulated society of AI agents modeled after **real historical people** who participated in utopian communities. Each agent gets a system prompt derived from that person's actual biography, values, goals, and personality. Drop them in a shared environment and let them interact autonomously for N rounds. Compare what emerges to what actually happened.

**The twist**: We don't invent personalities. We research real people, real motivations, real tensions. The simulation becomes a **retrodiction** — can it reproduce documented historical outcomes without being told what happened?

---

## Why This Is More Than a Toy

1. **Ground truth exists**: Historical communes have documented outcomes — who left, what split, why it collapsed, what survived. We can compare.
2. **Structural vs human**: If agents reproduce the same failure modes, it suggests those failures are structural (resource dynamics, information asymmetry, coordination costs) not uniquely human (emotions, irrationality).
3. **Controlled experiments on history**: We can't rerun Brook Farm. But we can rerun simulated Brook Farm 100 times, change one variable, and see what happens.
4. **Novel angle**: Most multi-agent papers simulate generic agents. Nobody is grounding agents in real historical people and comparing to documented outcomes.

---

## Historical Candidates

### Tier 1 — Best documented, clear failure modes

**Brook Farm (1841-1847, Massachusetts)**
- Transcendentalist commune, 60-120 members
- Founded by George Ripley (Unitarian minister, intellectual)
- Members included: Nathaniel Hawthorne (writer, skeptic), Charles Dana (journalist), John Dwight (music critic), Sophia Ripley (women's rights)
- Key tension: intellectuals vs workers, Fourierism conversion split
- Failure mode: fire destroyed phalanstery + financial collapse + intellectual drift
- **Why good**: Well-documented individual perspectives. Hawthorne literally wrote a novel about it (The Blithedale Romance).

**Oneida Community (1848-1881, New York)**
- 300 members at peak, lasted 33 years (longest successful US commune)
- Founded by John Humphrey Noyes (charismatic theologian)
- Complex marriage, mutual criticism, stirpiculture
- Key tension: founder dependency, generational change, sexual politics
- Failure mode: Noyes fled (statutory rape charges), community voted to dissolve
- **Why good**: Extreme Big Man problem. What happens when the founder agent is removed?

**Kibbutz movement (1910s-present, Israel)**
- Collective agriculture, communal child-rearing, no private property
- Thousands of participants, hundreds of communities
- Key tension: idealism vs pragmatism, generational drift, privatization pressure
- **Why good**: Actually survived (in modified form). Can model the drift from pure communism to privatization.

### Tier 2 — Interesting but less documented

- **New Harmony (1825-1827)** — Robert Owen's experiment. Failed in 2 years. Too many freeloaders.
- **Auroville (1968-present, India)** — Still running. Chronic governance issues.
- **Twin Oaks (1967-present, Virginia)** — Behaviorist commune (Walden Two). Still running.

### Tier 3 — Modern/digital

- **Early Wikipedia governance** — emergence of rules, admins, revert wars
- **Open source projects** — BDFL model, meritocracy claims, fork dynamics
- **DAO experiments** — TheDAO hack, governance token concentration

---

## Agent Design

### Per-Agent Setup

Each agent gets a **persona card** built from historical research:

```
AGENT: {name}
COMMUNITY: {which experiment}
YEAR: {time period}

BACKGROUND:
{2-3 sentences: who they were before joining}

MOTIVATION:
{Why they joined — idealism, escape, curiosity, social pressure?}

VALUES:
{What they care about most — equality, freedom, intellectual life, practical work, spiritual growth?}

PERSONALITY:
{Disposition — cooperative, skeptical, charismatic, withdrawn, pragmatic?}

PRIVATE GOAL:
{What they actually want — may differ from stated motivation}

KNOWLEDGE:
{What they know — farming, writing, theology, business, nothing useful?}

HISTORICAL NOTE (hidden from agent, used for evaluation):
{What actually happened to this person — did they leave? lead? sabotage? thrive?}
```

### How to Build Persona Cards

1. **Web search** the person's biography, letters, diaries, contemporary accounts
2. Extract motivations, personality, conflicts, relationships
3. Synthesize into system prompt
4. Store "historical note" separately for post-hoc comparison

**Key principle**: Don't tell the agent what happened. Let it decide. Compare afterward.

---

## Environment Design

### Shared State

```python
environment = {
    "day": 0,
    "resources": {
        "food": 100,        # depletes if not farmed
        "money": 500,       # shared treasury
        "shelter": 5,       # housing units
        "morale": 70,       # collective mood (0-100)
    },
    "buildings": [],         # things the community has built
    "rules": [],             # norms/rules the community has adopted
    "bulletin_board": [],    # public messages (last N visible)
    "private_messages": {},  # agent -> agent (optional)
    "history": [],           # log of all actions
}
```

### Action Space

Each round, each agent can take ONE action:

| Action | Effect | Cost |
|--------|--------|------|
| `farm` | +10 food | boring, reduces personal morale |
| `build <thing>` | adds to buildings | -20 money, requires 2+ agents cooperating |
| `propose <rule>` | adds rule to voting queue | free, but others must vote |
| `vote <yes/no> on <rule>` | if majority yes, rule adopted | free |
| `speak <message>` | posts to bulletin board | free |
| `private_message <agent> <message>` | DM another agent | free |
| `trade <resource> with <agent>` | bilateral exchange | both must agree |
| `rest` | +5 personal morale | no community contribution |
| `leave` | agent exits the simulation | irreversible |
| `challenge <agent>` | public criticism (Oneida-style) | -10 morale for target |

### Resource Dynamics

- Food depletes by `N_agents * 2` per round (everyone eats)
- If food hits 0: everyone loses 20 morale per round
- If morale hits 0: agent has 50% chance of leaving
- Money depletes from building projects
- New money from... what? (This is where the economic model matters)

### Communication

- **Bulletin board**: All agents see last 10 messages
- **Private messages**: Only recipient sees them (enables conspiracy, alliance)
- **Rules**: Once adopted, the environment enforces them (e.g., "everyone must farm 2 days per week" → agents who don't get flagged)

---

## Simulation Loop

```
for day in range(N_DAYS):
    # 1. Update environment (resource depletion, rule enforcement)
    environment.tick()

    # 2. Each agent observes
    for agent in agents:
        observation = environment.get_observation(agent)
        # observation includes: resources, bulletin board,
        # private messages, current rules, who's here

    # 3. Each agent decides (LLM call)
    actions = []
    for agent in agents:
        action = agent.decide(observation)
        actions.append(action)

    # 4. Resolve actions (handle conflicts, cooperation)
    environment.resolve(actions)

    # 5. Update agent memories
    for agent in agents:
        agent.update_memory(what_happened_this_round)

    # 6. Log everything
    logger.log(day, actions, environment.state)
```

### Agent Decision (LLM call)

```python
def decide(self, observation):
    prompt = f"""
    {self.persona_card}

    CURRENT SITUATION:
    {observation}

    YOUR MEMORY OF RECENT EVENTS:
    {self.memory[-10:]}

    What do you do today? Choose ONE action and explain your reasoning briefly.

    Available actions: farm, build, propose, vote, speak,
    private_message, trade, rest, leave, challenge

    Respond in format:
    ACTION: <action with parameters>
    REASONING: <1-2 sentences, in character>
    INNER_THOUGHT: <what you really think but won't say publicly>
    """
    return llm_call(prompt)
```

**INNER_THOUGHT is key** — it reveals when agents are being strategic vs authentic. Mirrors how real commune members had private doubts while publicly cooperating.

---

## Evaluation Framework

### Quantitative

- **Survival**: How many rounds before collapse (or does it survive)?
- **Population**: How many agents leave vs stay?
- **Resource trajectory**: Does the economy grow, stabilize, or deplete?
- **Rule count**: How many rules get adopted? (Bureaucracy signal)
- **Gini coefficient**: If resources become unequal despite communal intent

### Qualitative (compare to history)

- **Did the same factions form?** (Brook Farm: intellectuals vs workers)
- **Did the same person leave first?** (Hawthorne left Brook Farm early)
- **Did the same failure mode appear?** (Oneida: founder dependency)
- **Did unexpected dynamics emerge?** (Something history didn't record)

### Retrodiction Score

For each historical community:
1. List 5-10 documented outcomes (who left, what split, what rules emerged)
2. Run simulation 10 times
3. Score: how many outcomes does the simulation reproduce?
4. A score of 3-4/10 would be genuinely interesting. 7+/10 would be remarkable.

---

## Implementation Plan

### Phase 0: Pick one community (tonight)
- **Brook Farm** is the best starting point — 5-8 key members, well-documented, clear failure, Hawthorne's novel provides insider perspective
- Research the 5 key members, build persona cards

### Phase 1: Minimal loop (v0)
- Python script, simple environment, 5 agents, 50 rounds
- Use Claude API (or local model) for agent decisions
- Text log output
- **Goal**: Does anything interesting happen at all?

### Phase 2: Compare to history
- Add evaluation framework
- Run 10 times, aggregate
- Write up: "What the simulation got right/wrong about Brook Farm"

### Phase 3: Controlled experiments
- Remove one agent (the founder) at round 25 — does it collapse?
- Double the resources — does utopia work when there's abundance?
- Add an adversarial agent (infiltrator, freeloader) — how resilient?
- Scale from 5 to 15 agents — does Dunbar-like breakdown appear?

### Phase 4: Cross-community
- Run Oneida with same framework — different failure mode?
- Run a modern one (open source project governance)
- Compare: are there universal failure patterns across all communities?

---

## Open Design Questions

1. **LLM choice**: Claude API (expensive but good reasoning) vs local model (cheap, many runs, weaker reasoning)? For v0, Claude API is fine. For 100-run statistical analysis, need something cheaper.

2. **Memory design**: How much history does each agent remember? Full transcript = expensive + context window issues. Summary memory = lossy but scalable. Sliding window of last N events + key memories?

3. **Simultaneous vs sequential**: Do all agents act simultaneously (prisoner's dilemma style) or take turns (conversation style)? Real communities are simultaneous — but sequential is easier to implement and reason about.

4. **Rule enforcement**: When agents adopt rules, who enforces them? The environment (automatic)? Other agents (social pressure)? Nobody (honor system)? This choice dramatically changes dynamics.

5. **Economic model**: Where does new money come from? Selling farm produce to "outside world"? Fixed income? This determines whether the game is zero-sum (competition) or positive-sum (cooperation can grow the pie).

6. **Death/birth**: Should agents die (get removed after N rounds)? Should new agents join? Generational change was key to kibbutz drift and Oneida collapse.

7. **Hawthorne's novel**: Should we use The Blithedale Romance as additional source for persona cards? It's fictionalized but written by a participant. Rich psychological detail but possibly unfair to real people.

---

## What Would Make This Worth Writing About

If the experiment shows ANY of these, it's a genuine contribution:

1. **Same failure mode, different cause**: The simulation produces a schism, but for a different reason than history records — suggesting the recorded reason was surface-level and the structural dynamics would have produced a schism anyway.

2. **Counterfactual insight**: "If Hawthorne had stayed, Brook Farm would have lasted 2 more years" — because removing the skeptic removed the reality-check function.

3. **Universal pattern**: Running 3 different communities produces the same failure at roughly the same round — suggesting a structural inevitability regardless of ideology or personnel.

4. **The rule that saves it**: In 100 runs, the communities that survive all independently invent the same rule (e.g., mandatory rotation of labor, or a term-limited leader). That would be genuinely prescriptive.

---

## Fun Factor Checklist

- [x] Grounded in real history (not arbitrary)
- [x] Each run is different (emergent, not scripted)
- [x] Can be built incrementally (v0 tonight, iterate forever)
- [x] Connects to the anthropology thread (but doesn't need to "go anywhere")
- [x] Produces artifacts worth reading (simulation logs are stories)
- [x] Can be shared (blog post, demo, or just a fun conversation piece)
- [ ] No deadlines, no KPIs — pure exploration
