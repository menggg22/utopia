# Baseline Run (seed 0)

**Config**: 5 agents, 30 rounds, seed 0, standard resources
**Duration**: ~80 min, 304 LLM calls, 1401+ events

## Final State

| Metric | Value |
|--------|-------|
| Food | 0 (hit 0 on final round) |
| Money | $14 (nearly bankrupt) |
| Morale | 0% (since round 10) |
| Departed | None |
| Survived | All 5 |

## What Happened

Nobody left — but everyone was miserable. The community ground on for 30 rounds at 0% morale with declining resources. This is the "zombie commune" outcome: nobody has the will to leave, but nobody is thriving either.

**Food collapsed by round 6** (down to 7). Emergency food purchases kept it at 10 for 24 rounds, then money ran out too. Final round: food 0, money $16.

**Morale hit 0% at round 10** and never recovered. 20 straight rounds of zero morale.

## Character Arcs

**George Ripley** — Farmed 10/30 rounds (the most), gave 15 speeches. Satisfaction: 65 → 0 by round 12. The founder destroyed himself trying to save the community, same pattern as the original run. Proposed 2 rules (both failed).

**Nathaniel Hawthorne** — Surprisingly, he **stayed**. Unlike the original run (seed 42) where he left at R11. Satisfaction declined slowly (77 → 28) but never hit the threshold for departure. Gave 15 speeches and wrote 7 times. More engaged than in seed 42, perhaps because the random conversation pairs gave him different dynamics.

**Sophia Ripley** — Taught 13/30 rounds, most stable satisfaction (76 → 61). Still the school backbone but gave 11 speeches (more than original run). Her satisfaction held above 60 even at the end.

**Charles Dana** — Gave 18 speeches (most of any agent), farmed only 2 times. The speech spiral at its worst. Satisfaction: 77 → 0 by round 17.

**John Sullivan Dwight** — Gave 14 speeches, wrote 8 times, farmed only 2 times. Satisfaction declined steadily (79 → 7). More miserable than in no_hawthorne run.

## Votes

Two proposals, both failed:
- R2: "All members shall work the fields a minimum of 4 hours" — **FAILED** (2 YES, 3 NO). The intellectuals voted against mandatory labor.
- R5: (unclear rule) — **FAILED** (0 YES, 0 NO, 5 ABSTAIN). Complete apathy.

## Key Observations

1. **Hawthorne staying is the surprise** — with a different seed, the skeptic endured. His satisfaction was 28 at the end (not happy, but not desperate enough to leave). This suggests departure is influenced by conversation dynamics, not just persona.

2. **The farming vote is remarkable** — Ripley proposed mandatory farming in R2 and it was voted down 2-3. The community democratically rejected the one rule that might have saved it. This mirrors Brook Farm's real resistance to structured labor.

3. **Speech spiral is even worse** — 77 SPEAK actions across all agents (51% of all actions). The community spent more than half its time talking about problems.

4. **Money runs out** — unlike the original run where money stabilized around $240, this run hit $14 by the end. The difference: lower school income from 0% morale for longer.
