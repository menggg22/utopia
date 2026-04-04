# Double Food Run

**Config**: 5 agents, 30 rounds, seed 42, food=200 (double standard)
**Question**: Does more starting food change the outcome, or do intellectuals still refuse to farm?

## Final State

| Metric | Value |
|--------|-------|
| Food | 10 (emergency purchases, same as baseline) |
| Money | $394 (highest of any 5-agent run) |
| Morale | 0% (since round 15) |
| Departed | Hawthorne (R19) |
| Survived | Ripley, Sophia, Dana, Dwight |

## Answer: More food delays the crisis but doesn't prevent it

Double food bought 4 extra rounds of stability (food hit emergency at R10 vs R6 in baseline). Morale hit 0 at R15 vs R10. But the end state is the same — food at emergency level, morale at 0, community in decline.

**Hawthorne still leaves** — R19 instead of R11 (original) or R28 (no_sophia). More food gives him 8 extra rounds, but the fundamental dynamic is unchanged.

## Timeline Comparison

| Phase | Standard | Double Food |
|-------|----------|-------------|
| Food crisis begins | R6 | R10 |
| Morale hits 0 | R10 | R15 |
| Hawthorne departs | R11* | R19 |
| Emergency food purchases | R6-30 | R12-30 |

*Original run (seed 42); baseline seed 0 Hawthorne stayed.

## Character Arcs

**George Ripley** — The extra breathing room made him **more optimistic early** (satisfaction peaked at 73 in R7, vs 65 start in baseline). But the crash is just as severe: 0 by R25 and stays there. Farmed 8 times, gave 16 speeches. Same pattern, just delayed.

**Nathaniel Hawthorne** — **The golden period effect.** Satisfaction soared to 100 by R6 (with food abundant and morale high). He wrote 5 times, taught 4 times — in his element. But as food declined, so did he. Left at R19 with satisfaction 70. The extra food gave him a taste of what Brook Farm could be, making the decline harder to accept.

**Sophia Ripley** — The **best Sophia** of any 5-agent run. Taught 19/30 rounds, wrote 9 times. Satisfaction stayed 73-100 the entire run. More food meant less crisis, which meant she could focus on teaching and personal writing. The school thrived.

**Charles Dana** — **Trader Dana** again (12 trades, matching no_hawthorne). With less crisis pressure early, Dana defaulted to his practical instincts. Satisfaction held at 40 (vs 0 baseline).

**John Sullivan Dwight** — Happiest Dwight (91 final). Organized 10 events, taught 8 times. The extra resources let the cultural heart flourish. Same as no_hawthorne: less pressure → more joy.

## Key Moments

16 key moments (0.5/round). The turning points cluster around R9-R19 — the period when the extra food runs out and reality hits. The community's "fall from grace" is more dramatic because they had further to fall.

Notable: **Dwight's confession** (R15) — "the hands that betray the musician" — the moment the cultural heart admits the community is failing. In baseline, this happens earlier (~R8). More food buys more illusion.

## Key Observations

1. **Food is necessary but not sufficient** — doubling food delays every crisis milestone by 4-5 rounds but doesn't prevent any of them. The structural problem (intellectuals don't farm) eventually overwhelms any stockpile.

2. **Hawthorne's departure is delayed, not prevented** — R19 vs R11 (original). 8 more rounds of food didn't change his fundamental relationship to the community. He still left for the same reasons.

3. **The golden period creates worse heartbreak** — agents experienced genuine happiness (Hawthorne at 100, Dwight at 100) during rounds 4-9, making the decline emotionally harder. The key moments in this run are more anguished.

4. **Money is highest** — $394. More food → less emergency spending → more money survives. But money alone can't save the community — they need food production, not reserves.

5. **No behavioral change** — agents don't farm more with double food. They farm the same amount (Ripley 8, Dwight 3, Dana 2, Hawthorne 2). More food doesn't teach intellectuals to farm — it just postpones the consequence of not farming.
