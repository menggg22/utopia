# v1 Run #2 — Notes

**Status**: Interrupted at round 6 of 30 (checking balance fixes)
**Backend**: CLI (claude-haiku-4-5-20251001 via Claude Code)
**Changes from Run #1**: satisfaction delta, food clamp, school income scaling, key moment discouragement

## Results (6 rounds)

| Metric | Trajectory |
|--------|-----------|
| Food | 100 -> 75 -> 50 -> 25 -> 16 -> 7 (heading to 0) |
| Money | $500 -> $595 (still climbing) |
| Morale | 80 -> 85 -> 85 -> 85 -> 75 -> 65 (starting to drop) |
| Departures | None yet |

## What Improved

- **Satisfaction is realistic** — Ripley declining (65 -> 43), tracking his growing anxiety. Hawthorne rising (77 -> 100), comfortable writing/teaching. No more stuck-at-100.
- **No empty utterances** — all conversations have real dialogue
- **Morale dropping with food crisis** — 85 -> 65 as food runs low

## Remaining Issues

### Key moments still too frequent
15 in 5 rounds (3.0/round). Better than run #1 (4.5/round) but should be ~0.5/round. Prompt discouragement not strong enough.

### Sophia writes instead of teaches (4/5 rounds)
Surprising — her persona emphasizes teaching dedication ("missed only two classes in six years"). But this is a FINDING, not a bug. The LLM-Sophia is making her own choices. We should not force historical behavior.

### Hawthorne teaches instead of writes (4/5 rounds)  
Also surprising — his persona emphasizes writing and inability to find quiet. Another finding.

### Food crisis approaching
Only 4 FARM actions in 6 rounds. Community heading for starvation. Agents may or may not adapt — that's the experiment.

## Methodology Insight

**Tuning philosophy established this run:**
- FIX: mechanics (food physics, money flow, satisfaction instrument)
- FIX: prompt clarity (agents need info to make rational decisions)  
- FIX: LLM artifacts (positivity bias, over-dramatizing)
- DO NOT FIX: agent behavioral choices (farming, teaching, writing)

If agents collectively under-farm and starve, that's a structural finding about communities of intellectuals — exactly what Brook Farm experienced. The simulation should create realistic pressures; agents decide how to respond.
