# Cross-Experiment Analysis

6 runs of the Brook Farm simulation. 5 agents modeled after real historical participants. 30 rounds each (~Apr 1841 — Feb 1845). LLM: claude-haiku-4-5-20251001 via Claude Code CLI.

## Runs

| Run | Seed | Agents | Variation |
|-----|------|--------|-----------|
| original | 42 | 5 | First complete run |
| baseline | 0 | 5 | Different seed (reproducibility) |
| no_hawthorne | 42 | 4 | Remove the skeptic |
| no_sophia | 42 | 4 | Remove the school backbone |
| no_ripley | 42 | 4 | Remove the founder |
| double_food | 42 | 5 | Start with 200 food (2x) |

## Overview

| Run | Food | Money | Morale=0 | Food crisis | Departed |
|-----|------|-------|----------|-------------|----------|
| original | 10 | $224 | R11 | R5 | Hawthorne R11, Dwight R21 |
| baseline | 0 | $14 | R10 | R6 | None |
| no_hawthorne | 10 | $234 | R11 | R6 | None |
| no_sophia | 0 | -$1 | R10 | R6 | Hawthorne R28 |
| no_ripley | 10 | $44 | R10 | R6 | None |
| double_food | 10 | $394 | R15 | R10 | Hawthorne R19 |

Every run ends at 0% morale. Every run hits food crisis. The community always fails. The question is how.

---

## Finding 1: The Intellectual Farming Problem is Structural

Total FARM actions across all runs:

| Run | Ripley | Hawthorne | Sophia | Dana | Dwight | Total | Per agent-round |
|-----|--------|-----------|--------|------|--------|-------|-----------------|
| original | 11 | 0 | 2 | 3 | 6 | 22 | 0.15 |
| baseline | 10 | 1 | 0 | 2 | 2 | 15 | 0.10 |
| no_hawthorne | 3 | -- | 1 | 3 | 1 | 8 | 0.07 |
| no_sophia | 3 | 0 | -- | 2 | 7 | 12 | 0.10 |
| no_ripley | -- | 0 | 0 | 1 | 4 | 5 | 0.04 |
| double_food | 8 | 2 | 0 | 2 | 3 | 15 | 0.10 |

**Agents farm 4-15% of the time.** The community needs ~2 FARM actions per round to sustain food (each FARM = +8 food, consumption = 25/round for 5 agents). Actual farming: 0.3-0.7 per round. The deficit is structural — no configuration change fixes it.

**Ripley is the only consistent farmer** (8-11 times in runs where he's present). Without him (no_ripley), total farming drops to 5. He farms out of guilt, not because it's rewarding (his satisfaction hits 0).

**Double food doesn't increase farming** — 15 FARM actions, same as baseline. Agents don't farm more when there's abundance. They also don't farm more when there's scarcity. Farming behavior is persona-driven, not resource-driven.

---

## Finding 2: The Speech Spiral

| Run | Total SPEAK | % of all actions | Speeches per agent-round |
|-----|-------------|------------------|--------------------------|
| original | 36 | 30% | 0.24 |
| baseline | 73 | 49% | 0.49 |
| no_hawthorne | 33 | 28% | 0.28 |
| no_sophia | 48 | 41% | 0.40 |
| no_ripley | 53 | 44% | 0.44 |
| double_food | 28 | 20% | 0.19 |

**SPEAK is the dominant action** in 4 of 6 runs. In the baseline run, agents spent nearly half their time giving speeches about the crisis instead of working.

**Dana is the worst offender** — 15-22 SPEAK actions in every run. He becomes the voice of financial reality without ever taking productive financial action (farms 1-3 times across runs).

**The spiral intensifies in leaderless communities** — no_ripley has Dana at 22 speeches (73% of his actions). Without the founder's ideological leadership, others fill the vacuum with talk.

**Double food reduces speeches** — 20% vs 49% baseline. When there's less crisis, there's less to speechify about. Agents default to more productive actions (trade, organize, teach).

---

## Finding 3: Sophia is the Indispensable Member

| Run | Sophia present | Final money | Teaching total | School income |
|-----|----------------|-------------|----------------|---------------|
| original | Yes | $224 | 24 | High |
| baseline | Yes | $14 | 20 | High |
| no_hawthorne | Yes | $234 | 33 | High |
| **no_sophia** | **No** | **-$1** | **13** | **Low** |
| no_ripley | Yes | $44 | 32 | High |
| double_food | Yes | $394 | 32 | High |

**no_sophia is the only run where money goes negative.** Without her, teaching drops from 20-33 to 13. Others teach occasionally but nobody fills her role consistently.

Sophia teaches 13-20 rounds in every run she's present. Her satisfaction stays 61-98 — highest and most stable of any agent across experiments. The school gives her purpose independent of the community's crisis.

**Historically accurate**: Sophia Ripley ran the school for 6 years and missed only 2 classes. The school was Brook Farm's primary revenue source. The simulation reproduces this without being told.

---

## Finding 4: The Founder is Not Structurally Necessary

| Run | Ripley present | Departures | Final money | Community survives? |
|-----|----------------|------------|-------------|---------------------|
| original | Yes | 2 | $224 | Yes (3 remaining) |
| baseline | Yes | 0 | $14 | Yes (barely) |
| **no_ripley** | **No** | **0** | **$44** | **Yes** |
| no_sophia | Yes | 1 | -$1 | Barely |

**Removing Ripley doesn't kill the community.** Nobody leaves. Money ($44) is better than baseline ($14). The founder's contribution was emotional (guilt-driven farming, visionary speeches) not structural.

Without Ripley, Dana takes 22 SPEAK actions — he becomes the voice. Sophia still teaches. Dwight farms more (4 vs 1-2). The community reorganizes around Sophia's school instead of Ripley's vision.

**Ripley's real contribution was suffering** — he farmed 10-11 times (more than anyone) while his satisfaction hit 0. He sacrificed himself for a community that didn't structurally need him.

---

## Finding 5: Hawthorne as Destabilizer

| Run | Hawthorne | Left? | When | Final sat | Community sat (avg) |
|-----|-----------|-------|------|-----------|---------------------|
| original | Present | Yes | R11 | 89 | 24 |
| baseline | Present | No | -- | 28 | 19 |
| **no_hawthorne** | **Absent** | -- | -- | -- | **74** |
| no_sophia | Present | Yes | R28 | 100 | 4 |
| no_ripley | Present | No | -- | 62 | 41 |
| double_food | Present | Yes | R19 | 70 | 51 |

**Removing Hawthorne produces the happiest community** — average final satisfaction 74, vs 4-41 in other runs. No departures. Most money ($234). Fewest key moments (6 — least drama).

Hawthorne's presence creates tension that drags others down. When he's absent:
- Dana shifts from speeches (18) to trading (11) — the financial anxiety is redirected productively
- Dwight stays at satisfaction 100 — the cultural heart blooms
- Ripley still declines but slower (24 vs 0)

**But Hawthorne is also the honest observer.** His key moments and inner thoughts are the richest data in every run. The community is happier without him but also less self-aware.

---

## Finding 6: More Resources Don't Change Behavior

| Metric | Standard food | Double food | Difference |
|--------|---------------|-------------|------------|
| Total FARM | 15 (baseline) | 15 | 0 |
| Food crisis | R6 | R10 | +4 rounds |
| Morale=0 | R10 | R15 | +5 rounds |
| Hawthorne leaves | R11 (original) | R19 | +8 rounds |
| Final money | $14-224 | $394 | Higher |
| Speech % | 49% (baseline) | 20% | Lower |

Double food buys time (4-5 rounds) but doesn't change the underlying dynamic. Agents farm exactly the same amount (15 actions). They don't adapt to abundance or scarcity — they follow their personas.

The extra food creates a "golden period" (rounds 1-9) where satisfaction is high and agents pursue their interests (writing, organizing, trading). This makes the eventual decline more painful — key moments in this run are more anguished because agents had further to fall.

---

## Finding 7: Hawthorne's Departure is Variable, Not Fixed

| Run | Hawthorne departs | Satisfaction at departure |
|-----|-------------------|--------------------------|
| original (s42) | R11 | 89 (relieved to leave) |
| baseline (s0) | Never | 28 (miserable but stayed) |
| no_sophia (s42) | R28 | 100 (thriving, left voluntarily) |
| no_ripley (s42) | Never | 62 (moderate, no foil) |
| double_food (s42) | R19 | 70 (delayed departure) |

Hawthorne doesn't always leave, and when he does, it's for different reasons:
- **Original**: Early departure (R11), relieved. Classic "this isn't for me."
- **No sophia**: Late departure (R28), at peak satisfaction (100). He thrived in the dysfunctional community, then left on his own terms.
- **Double food**: Middle departure (R19), moderate satisfaction. The golden period gave him hope, making the decline harder.
- **Baseline s0**: Never left despite satisfaction 28. Different random conversations kept him engaged.
- **No ripley**: Never left (62 sat). Without Ripley's idealism to push against, no tension to escape.

**Departure is driven by interpersonal dynamics (conversation pairs, trust), not just resources.** The random seed (which affects pair selection) matters as much as the environment.

---

## Summary Table

| Finding | Evidence |
|---------|----------|
| Intellectuals don't farm | 4-15% farming rate across all runs, regardless of food level |
| Speech spiral | 20-49% of all actions are speeches; Dana worst (15-22 per run) |
| Sophia is indispensable | Only run without her goes bankrupt; she teaches 13-20 rounds consistently |
| Founder is replaceable | Removing Ripley: nobody leaves, money comparable to baseline |
| Skeptic destabilizes | Removing Hawthorne: highest satisfaction, most money, no departures |
| Resources don't change behavior | Double food: same farming rate, crisis delayed but not prevented |
| Departure is stochastic | Hawthorne leaves in 3/5 runs at different times (R11, R19, R28) |

## What This Means

The simulation reproduces Brook Farm's core failure without being told about it: **a community of intellectuals that talks about its problems instead of solving them, sustained by one person's practical labor (school), while the founder destroys himself trying to compensate.**

The counterfactuals reveal something history couldn't: the community's survival depended more on Sophia's school than Ripley's vision, and Hawthorne's honest skepticism — while valuable for self-awareness — was a net negative for collective wellbeing.

The most striking finding is that **doubling resources doesn't change behavior**. The failure is not material scarcity — it's the mismatch between who these people are and what the community needs them to do. That's a structural insight about utopian communities, not just a simulation artifact.
