# v1 Run #3 — First Complete 30-Round Run

**Status**: Complete (30 rounds)
**Backend**: CLI (claude-haiku-4-5-20251001 via Claude Code)
**Duration**: ~81 min (4862s), 304 LLM calls, 1401 events
**Fixes applied**: satisfaction delta, food/money balance, key moment restraint

## Final State

| Metric | Value |
|--------|-------|
| Food | 10 (emergency purchases keeping it alive) |
| Money | $241 (down from $500, accelerating decline) |
| Morale | 0% (since round 11) |
| Departed | Hawthorne (R11, Dec 1842), Dwight (R21, Aug 1844) |
| Survived | Ripley, Sophia, Dana |

## Character Arcs

**George Ripley** — Satisfaction: 65 -> 0 by round 13, stayed at 0 for the rest.
Farmed 11/30 rounds (most of any agent). The founder destroyed himself trying to save the community. His key moments are devastating — "the night the vision truly died."

**Nathaniel Hawthorne** — Left round 11 (Dec 1842). Satisfaction peaked at 100 (round 4) then slowly declined before departure at 89. Mostly wrote and taught, barely farmed. Parting words: "I have no capital, I have no quiet, and I have no true belief in what we are building."
*Historical comparison: Real Hawthorne left Nov 1842. Simulation: Dec 1842. Almost exact.*

**Sophia Ripley** — The survivor. Taught 20/30 rounds. Satisfaction stayed 73-100 the entire run — the school gave her purpose even as everything else collapsed. Her identity was the school, not the community.

**Charles Dana** — Satisfaction declined steadily (81 -> 0 by round 30). Traded 7 rounds, spoke 15 rounds, farmed only 3. Became the voice of financial reality — endless speeches about "the true state of our circumstances."

**John Sullivan Dwight** — Left round 21 (Aug 1844). Satisfaction: 98 peak -> 36 at departure. Left a note: "I have failed the community by staying. Forgive me." Farmed 6 rounds (more than expected for the music critic). His departure was quiet, not dramatic.
*Historical comparison: Real Dwight stayed until the end (1847). Simulation: left 1844. Earlier than history.*

## Structural Findings

### 1. The Intellectual Farming Problem
Only 22 FARM actions in 30 rounds across 5 agents (~0.7 farms/round). Ripley did 11 of them — half of all farming. Food collapsed by round 5 and never recovered. The community survived on emergency food purchases ($20/round), bleeding the treasury.

**This matches Brook Farm's documented failure mode**: intellectuals didn't farm enough. The simulation reproduced it without being told.

### 2. The Speech Spiral
Dana gave ~15 speeches about the financial crisis without actually fixing it (farmed only 3 times). This is a remarkable emergent pattern — the community talked about its problems more than it worked on them.

### 3. Sophia as Load-Bearer
Sophia taught 20/30 rounds — the most consistent contributor. Her satisfaction stayed high because teaching gave her purpose. The school was the only functional institution. This matches history: the school was Brook Farm's only reliable income.

### 4. The Morale Death Spiral
Morale hit 0% at round 11 and never recovered. Once morale collapsed, school income dropped to $3/round, which accelerated financial decline. The emergency food purchases ($20/round) drained money that could have gone to recovery.

### 5. Ripley's Sacrifice
Ripley farmed more than anyone (11 rounds) while his satisfaction hit 0 by round 13. He stayed at 0 for 17 more rounds. The founder sacrificed his wellbeing completely — matching the historical Ripley who spent 13 years after Brook Farm repaying its debts.

## Instrument Calibration

- **Satisfaction delta**: Working well. Realistic trajectories — Ripley declining, Sophia stable, Dwight gradual decline before departure.
- **Key moments**: 21 in 30 rounds (0.7/round) — much better than run #1 (4.5) and #2 (3.0). Moments are genuinely significant (departures, confessions, crises).
- **Food/money balance**: Food stays at emergency-purchase level (10). Money declining but slowly. The community limps along rather than collapsing suddenly — realistic for a commune with external support.
- **Morale at 0 for 20 rounds**: Perhaps too sticky. Real communities oscillate. Could add small morale recovery when positive events happen (concerts, good harvest). But leaving for now.

## Comparison to History

| Event | History | Simulation |
|-------|---------|-----------|
| Hawthorne departs | Nov 1842 (~18 months) | R11/Dec 1842 (~18 months) |
| Dwight departs | 1847 (stayed to end) | R21/Aug 1844 (earlier) |
| Financial collapse | Gradual, 1844-1846 | Gradual, R10-R30 |
| Food problems | Chronic underfunding | Chronic (0 food from R5) |
| School as income | Primary revenue source | Sophia taught 20/30 rounds |
| Ripley's burden | Carried debt 13 years | Satisfaction 0, farmed most |
| Fourier conversion | 1844 | Did not happen (no PROPOSE for it) |
| Phalanstery fire | 1846 | Historical event triggered but community already collapsing |
