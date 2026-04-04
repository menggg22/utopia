# V2 Design: From Experiment to Study

V1 was an experiment — "can agents reproduce historical dynamics?" The answer was yes, with caveats. V2 is a study — we fix the known mechanical issues, establish rigorous methodology, and use the simulation to answer questions history cannot.

## The Cardinal Rule

**Never tune the simulation to match a specific historical outcome.**

Every change must be justified by one of:
1. **Structural realism** — real communities work this way (e.g., good events lift morale)
2. **Mechanical fairness** — the system shouldn't have traps that no real community would have (e.g., morale stuck at 0 forever)
3. **Experimental validity** — the system should produce variance, not a single attractor (e.g., every run ending at 0% morale is a sign of a broken mechanic, not a finding)

If a change would make Dwight stay longer, that's fine — as long as the change is justified independently of Dwight. If the only reason for the change is "Dwight should stay longer," it's overfitting.

**How to check:** Before making a change, ask: "Would I make this change if I had no idea what happened at Brook Farm?" If yes, it's structural. If no, it's tuning.

---

## V1 Issues

### Mechanical Problems

**1. Morale is a one-way trap.**
Morale starts at 80 and only goes up from ORGANIZE (+5). Food crises drain -10 to -20 per round. Once food hits 0 (usually round 5-6), morale drops ~15/round and recovers at most +5. The math guarantees collapse. Every run in v1 ended at 0% morale — that's not a finding, it's an arithmetic inevitability.

*Why this is a mechanical problem, not a feature:* Real communities have good days even during decline. A harvest comes in, a concert goes well, a visitor brings encouragement. Brook Farm had five good years before the final collapse. Our simulation has five good *rounds*.

**2. Satisfaction spirals downward.**
The reflection prompt says "Most days should be -5 to +3." This biases the LLM toward negative deltas. Combined with FARM costing -3 satisfaction per action, a farming agent loses ~5-8 satisfaction per round. From 70, that's 0 in ~10 rounds. No recovery path exists except avoiding farming — which is the core community need.

*Why this matters:* Real people find meaning even in hard work. Ripley farmed because he believed in the mission. That belief should sustain satisfaction somewhat, even when farming is miserable. V1 Ripley hits 0 satisfaction and keeps farming out of what looks like masochism.

**3. SPEAK has no cost.**
SPEAK gives 0 satisfaction and takes no resources. It's the "do nothing" action that looks productive. In 4 of 6 runs, it was the most common action. Dana gave 15-22 speeches per run. The speech spiral is partially emergent (agents genuinely prefer talking over farming) but also partially mechanical (there's no downside to speaking).

*Why this matters:* In real communities, speeches take time away from other work. People who only talk eventually lose social capital. V1 has no mechanism for this — Dana can speechify forever with no consequences.

**4. No passion anchoring.**
All agents get the same satisfaction from the same actions. WRITE is +8 for everyone. TEACH is +5 for everyone. But Dwight's music was his reason for being there, and Sophia's teaching was hers. In v1, the LLM infers preferences from personas, but the satisfaction mechanics don't reinforce them. When morale hits 0, the LLM overwhelms persona preferences with crisis reasoning.

*Why this matters:* Dwight stayed at Brook Farm until 1847 despite years of decline, because the musical community was irreplaceable. V1 Dwight left in 1844 because the flat satisfaction system couldn't represent "this one thing makes everything else bearable."

**5. No morale recovery from positive actions.**
TEACH, WRITE, TRADE, and successful events don't improve community morale. Only ORGANIZE does. But ORGANIZE is abstract — it doesn't represent specific positive events like a concert, a good school term, or a successful trade. The system has no way to model "things are bad but today was good."

**6. Historical events are fire-and-forget.**
The Brisbane visit (round 12) appears as a bulletin item. Agents see it, react in reflection, and move on. There's no mechanism for it to catalyze structural proposals. In reality, Brisbane's visit triggered months of debate and eventually the Fourier conversion. V1 agents are too caught up in immediate survival to think systemically.

### Environment Problems

**7. The food economy is impossibly tight.**
5 agents consume 25 food/round. FARM produces 8. The community needs 3+ FARM actions per round just to break even. Actual farming: 0.3-0.7 per round. Food hits 0 by round 5-6 in every run. The deficit is so severe that it dominates all other dynamics.

*This may actually be realistic* — Brook Farm did have chronic food problems. But the severity in v1 means food crisis starts before agents have had any time to establish relationships, test their beliefs, or experience the community's positive side. The "golden period" of Brook Farm (1841-1843) doesn't exist in v1.

**8. All runs converge to the same endpoint.**
Every run ends at 0% morale. Every run hits food crisis by round 6. The community always fails in the same way. The variance is in departure timing and conversation content, not in outcomes. A good simulation should produce both failure and near-success — otherwise we can't distinguish between "this community was doomed" and "this simulation is broken."

### What V1 Got Right

These should be preserved:
- **Persona-driven decisions** via LLM, not utility functions
- **Asymmetric satisfaction** — farming hurts, writing helps, community needs clash with individual wants
- **Structured memory** — key moments, relationships, concerns, observations
- **Inner thoughts** in conversations — the public/private gap
- **Gossip mechanics** — social pressure without central coordination
- **No historical scripting** — agents don't know what happened

---

## V2 Changes

### Change 1: Morale responds to positive actions

Actions that benefit the community should lift morale slightly:

| Action | Morale effect |
|--------|--------------|
| FARM | +2 (visible effort) |
| TEACH | +2 (school functioning) |
| ORGANIZE | +5 (direct morale action) |
| BUILD/REPAIR | +1 (visible improvement) |
| TRADE | +1 (community engaging with outside) |

Negative events still apply. The goal: morale can stabilize at low levels (10-30%) instead of being trapped at 0. A community where 2-3 people are doing useful work should feel bad but not dead.

**Validation:** Does this produce runs where morale oscillates rather than flatlines? If yes, the mechanic is working. If morale still flatlines, the penalties are too harsh. If morale recovers to 80+, the boosts are too generous.

### Change 2: Per-agent passion bonuses

Each persona card gets a `passions` field — 1-2 actions that give bonus satisfaction for that specific agent.

| Agent | Passions | Bonus |
|-------|----------|-------|
| Dwight | ORGANIZE (concerts) | +5 extra |
| Sophia | TEACH | +3 extra |
| Hawthorne | WRITE | +3 extra |
| Ripley | ORGANIZE, SPEAK | +3 extra |
| Dana | TRADE, WRITE | +3 extra |

**Why this is structural, not tuning:** Every person has activities that sustain them disproportionately. A musician who can play music is happier than a musician who cannot, even if everything else is the same. This is a general human property, not a Brook Farm fix.

**Validation:** Passions should make departure timing more variable, not more historically accurate. If Dwight stays exactly until 1847, we overfit. If Dwight sometimes stays late and sometimes leaves early, the mechanic is adding realistic variance.

### Change 3: Rebalance the reflection prompt

Remove "Most days should be -5 to +3." Replace with neutral framing:

> "How much did your satisfaction change today? A number from -10 to +10. Negative if discouraging, positive if genuinely good. 0 if ordinary."

Let the LLM decide the distribution based on what actually happened, not a hardcoded pessimism bias.

### Change 4: Speech fatigue

Track consecutive SPEAK actions per agent. After 3+ consecutive speeches without a productive action, other agents' trust toward the speaker decreases by 1. The LLM is told in the environment summary: "[Agent] has spoken about the crisis for [N] consecutive rounds without taking other action."

This creates natural social pressure against pure speechifying without mechanically preventing it.

### Change 5: Soften the food economy

Options (test which produces the most realistic dynamics):
- **A)** Reduce consumption from 5 to 4 per agent per round
- **B)** Increase FARM yield from 8 to 10
- **C)** Start with more food (150 instead of 100)

Goal: food crisis should hit around round 10-12, not round 5. This gives agents a "golden period" to establish relationships and beliefs before survival pressures dominate.

### Change 6: Event-catalyzed proposals

When a major historical event fires (Brisbane visit, phalanstery proposal), add to the next round's action prompt:

> "In light of [event], you may also consider proposing structural changes to how the community is organized."

This doesn't force proposals — it makes them salient. The LLM still decides freely.

---

## Research Questions

V1 answered: "Can agents reproduce historical dynamics?" (Yes, roughly.)

V2 should answer:

### Q1: Is the failure mode reproducible?
Run 5 baseline seeds with identical configuration. Do they all fail? Do they fail the same way? What varies — timing, departure order, conversation content, or outcome?

### Q2: What is the minimum viable community?
Systematically vary community size (3, 5, 7, 10 agents). At what size does farming become sustainable? Does adding generic "farmer" agents (no intellectual ambitions) change the outcome?

### Q3: Do passions change departure dynamics?
Compare v1 (flat satisfaction) vs v2 (passion bonuses) across the same seeds. Does passion anchoring produce more variance in departure timing? Does it change who leaves first?

### Q4: Is the speech spiral a model artifact or a structural phenomenon?
Compare runs with and without speech fatigue. If the spiral disappears with fatigue, it was mechanical. If agents find other ways to avoid farming (REST, WRITE), the avoidance is structural and the speech was just the vehicle.

### Q5: What makes a community survive?
Run a sweep: vary food abundance, number of "practical" agents, presence/absence of a skeptic, passion strength. Map the parameter space. Is there any configuration where the community survives 30 rounds with positive morale?

### Q6: Does the founder matter?
V1 found Ripley is structurally replaceable. Does this hold in v2 with morale recovery? Does the founder matter more when the community can actually recover from crises?

### Q7: Beyond Brook Farm
Apply the same framework to a different utopian community (Oneida, New Harmony, or a Shaker village). Different personas, different economic structure, different failure modes. Does the simulation reproduce the different failure?

---

## Experimental Protocol

### Baseline requirements
- Every comparison requires at least 3 seeds per configuration
- Report mean and variance, not single-run anecdotes
- Changes are tested one at a time against the v1 baseline before combining

### What counts as a result
- A finding is a pattern that holds across 3+ seeds
- A single-run observation is an anecdote, not a finding
- If a result depends on the seed, report the variance — that's the real finding

### What counts as overfitting
- Any change motivated by "agent X should do Y" where Y matches history
- Any parameter chosen because it produces a historically accurate outcome
- Any post-hoc explanation that only works for one run

### Reporting
- Every run produces: events.jsonl, narrative.md, metrics.csv, conversations.json, votes.json
- Cross-run analysis via compare.py
- Figures regenerated per batch, not cherry-picked from best runs
