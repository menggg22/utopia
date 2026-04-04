# V3 Design: Agent-Driven Morale

This document describes the v3 simulation changes. For the full system architecture (round structure, personas, memory, gossip, economics), see [v1/DESIGN.md](v1/DESIGN.md). For v2 changes (passion bonuses, softer economy, speech fatigue), see [v2/V2-DESIGN.md](v2/V2-DESIGN.md).

## What Changed Across Versions

**V1 problem:** Morale was formula-only. Only ORGANIZE (+5) raised it. Food crises drained -10 to -20/round. Morale hit 0 by round 10 and never recovered.

**V2 fix attempt:** Added morale boosts to positive actions (FARM +2, TEACH +2, etc.) and softened food economy. Morale collapse delayed to round ~14 but still flatlined at 0 for 11-19 rounds in every run.

**V2 diagnosis:** The morale boosts were fighting a -10 penalty that fires every round food < 20. The math always loses. More fundamentally: morale is not a resource like food or money. It's a collective feeling. Hardcoding "+2 morale for farming" is a mechanical fiction — real morale comes from how people *feel* about what's happening, not from an action lookup table.

## V3 Principle: Formula vs Agent-Driven

Every mechanic in the simulation is either:
- **Formula-driven** — deterministic, physical, arithmetic (food consumption, money, building decay)
- **Agent-driven** — emergent from LLM reasoning about persona, memory, and context (action choice, departure, conversations)

The rule: **if a real person would need to think/feel to produce this value, it should be agent-driven. If it's physics or accounting, it should be formula.**

| Mechanic | Type | Rationale |
|----------|------|-----------|
| Food consumption | Formula | Physics — people eat |
| Food production | Formula | Physics — farming yields crops |
| Money flow | Formula | Accounting — school income, operating costs |
| Building decay | Formula | Physics — buildings deteriorate |
| Historical events | Formula | Timeline is fixed |
| Action choice | Agent | Requires judgment, persona, context |
| Departure | Agent | Deeply personal decision |
| Satisfaction | Hybrid | Base deltas are physical (farming hurts), reflection adjusts |
| Conversations | Agent | Content is persona-driven |
| Voting | Agent | Requires judgment |
| **Morale** | **Agent (v3)** | How the community *feels* is a collective judgment, not arithmetic |

## The V3 Morale Mechanic

### Remove
- All hardcoded morale changes from `resolve_action()` (no more +2 for FARM, +2 for TEACH, +5 for ORGANIZE, etc.)
- All hardcoded morale penalties from `tick()` (no more -10 for food < 20, -20 for food = 0, -5 for money < 50)
- Morale changes from historical events (smallpox -15, fire -25) — agents will feel these through context

### Add
During the REFLECT phase, each agent answers one additional question:

```
COMMUNITY_MORALE: <How do you feel about the community's direction right now?
A number from 0 to 100. Consider: Are people doing meaningful work? Is there
enough food? Are relationships healthy? Is the vision alive? Be honest —
this is your private assessment, not a public performance.>
```

Community morale = **average of all active agents' COMMUNITY_MORALE scores.**

### Why This Works

- **Morale can recover.** If agents have a good day (successful concert, honest conversation, food comes in), they'll report higher confidence. No formula prevents this.
- **Morale can crash.** If agents feel hopeless, they'll report 0. No formula props it up artificially.
- **Morale reflects reality.** Each agent weighs the situation differently based on their persona. Sophia might feel good because the school is working; Hawthorne might feel bad because he can't write. The average captures genuine collective sentiment.
- **No tuning needed.** We don't need to balance +2 vs -10. The LLM reads the environment and decides.

### What Morale Still Affects

Morale remains an environment variable that agents can see. It affects:
- **School income** — still scales with morale (students leave when community struggles). This is realistic: parents pull kids from struggling communes.
- **Agent context** — agents see "Community Morale: X%" in their prompts, which influences their decisions.
- **No mechanical termination** — morale 0 no longer triggers a crisis message. The agents see the number and react.

### School Income at Morale 0

One issue: if morale is agent-driven and agents report 0, school income drops to $3/round. This creates a feedback loop: low morale → less income → more financial crisis → lower morale.

This is actually realistic — Brook Farm's school enrollment did drop as the community declined. But we should watch for it becoming a mechanical trap despite being agent-driven. If the feedback loop is too tight, we can decouple school income from morale (make it depend on how many agents TEACH instead).

## What V3 Keeps From V2

All other v2 changes remain:
1. **Per-agent passion bonuses** — satisfaction bonuses for persona-aligned actions
2. **Neutral reflection prompt** — no "most days should be -5 to +3" bias
3. **Speech fatigue** — trust erosion after 3+ consecutive speeches
4. **Softer food economy** — 4 food/agent/round instead of 5
5. **Event-catalyzed proposals** — ideological events prompt structural thinking
6. **v2_ run directory prefix** and version tagging

The only change is: morale goes from formula-driven to agent-driven.

## Validation

### What success looks like
- Morale should vary across runs — some runs stay at 20-40%, others crash to 0
- Morale should oscillate within a run — good days and bad days, not monotonic decline
- Morale should correlate with what's actually happening (food crisis → lower morale, successful event → higher morale) without being mechanically linked

### What failure looks like
- All runs still flatline at 0 → agents are too pessimistic, prompt needs adjustment
- Morale stays at 80+ despite crises → agents are too optimistic, prompt needs adjustment
- Morale is random noise → agents aren't reading the environment properly

### Test plan
Run 3 baseline seeds (0, 1, 2) and compare morale trajectories to v2. If morale shows variance and oscillation, the mechanic works.
