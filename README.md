# Utopia

Can we simulate historical utopian communities with AI agents modeled after real participants — and reproduce documented failure modes?

## The Experiment

Drop AI agents (each modeled after a real historical person) into a shared environment. Let them interact autonomously. Compare what emerges to what actually happened.

**Key insight**: If agents reproduce the same schisms, collapses, and power dynamics without being told what happened — those failure modes are structural, not uniquely human.

## First Target: Brook Farm (1841-1847)

Transcendentalist commune in Massachusetts. Founded by George Ripley, joined by Nathaniel Hawthorne (who later wrote a novel about it). Well-documented failure: intellectuals vs workers split, Fourierist conversion, phalanstery fire, financial collapse.

**6 agents** modeled from real biographies:
- **George Ripley** — Founder, visionary, carried the debt for 13 years after
- **Nathaniel Hawthorne** — Skeptic, writer, left after 18 months ("my soul is not utterly buried under a dung-heap")
- **Sophia Ripley** — Co-founder, ran the school (only reliable income), later called it all "childish, empty, & sad"
- **Charles Dana** — 22-year-old pragmatist, spoke 10 languages, later became Assistant Secretary of War
- **John Sullivan Dwight** — Music critic, cultural heart, organized the evening gatherings
- **Isaac Hecker** — Spiritual seeker, left during Fourier conversion, founded the Paulist Fathers

## How It Works

Each simulation round has 3 phases:

1. **Act** — Each agent observes the environment and chooses an action (farm, teach, build, write, propose a rule, leave...)
2. **Talk** — 2-3 conversation pairs interact. Voting happens if rules are proposed. Agents argue, persuade, confide.
3. **Reflect** — Each agent privately updates their memory: what mattered today, how they feel about each person, what worries them.

Agents have **structured memory**: permanent key moments, evolving relationships (trust + attitude per person), running concerns, and observations about others that spread as gossip.

Historical events are injected at the right time: Brisbane's Fourierist visit, the phalanstery proposal, smallpox, the fire.

## Logging

Single JSONL event stream (`events.jsonl`) captures everything — actions, inner thoughts, conversations, votes, relationship changes, gossip, resource levels. All other views (narrative, charts, character arcs) derive from this one file.

15 event types. Flush every write. Survives crashes. Ready for documentary reconstruction.

## Status

- [x] Experiment design ([DESIGN.md](DESIGN.md))
- [x] Historical research — 6 persona cards with real biographies, quotes, outcomes ([BROOK-FARM-PERSONAS.md](BROOK-FARM-PERSONAS.md))
- [x] v0 simulation engine ([simulate.py](simulate.py))
- [x] v1 agent design — structured memory, conversations, voting, gossip ([AGENT-DESIGN-V1.md](AGENT-DESIGN-V1.md))
- [x] Logging specification — JSONL event stream ([LOGGING-SPEC.md](LOGGING-SPEC.md))
- [x] v0 test run — 10 rounds, Hawthorne departs round 10 ([run summary](#v0-test-run))
- [x] v1 implementation ([simulate_v1.py](simulate_v1.py), [derive.py](derive.py))
- [x] First complete run — 30 rounds, reproduces key failure modes ([run summary](#v1-first-complete-run))
- [ ] Controlled experiments (remove founder, add scarcity, scale up)
- [ ] Visualization / documentary

## What Would Make This Worth Sharing

1. **Same failure mode, different cause** — simulation produces a schism for a structural reason history didn't record
2. **Counterfactual insight** — "if Hawthorne had stayed, the community lasts 2 more years"
3. **Universal pattern** — running 3 different communities produces the same failure at the same point
4. **The rule that saves it** — in 100 runs, surviving communities independently invent the same rule

## v0 Test Run

10 rounds (Apr 1841 — Oct 1842), claude-opus-4-6 (via Claude Code), pre-generated agent responses grounded in historical personas.

**Result**: Hawthorne departed round 10 (Oct 1842) — matches real history (~18 months). 4 members survived. Food hit 0, morale crashed to 15%.

| Metric | Final |
|--------|-------|
| Food | 0 |
| Money | $750 |
| Morale | 15% |
| Departed | Nathaniel Hawthorne |
| Survived | Ripley, Sophia, Dana, Dwight |

**Lessons for v1**:
- Satisfaction model too simple (monotonic +5/+8 per action, caps at 100) — needs decay, social factors, unmet-goal pressure
- Money too generous (two teachers + base school income outpaces costs) — needs rebalancing
- No conversations, voting, or reflection — the core v1 additions
- Food drain harsh (5/agent/round) with only 1-2 farmers — farming yield or consumption needs tuning

Output: `runs/v0_local_20260401_220537/` (config.json, full_log.json, characters.json, metrics.json, narrative.md, summary.txt)

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python simulate.py
```

Output lands in `runs/<timestamp>/`.

## v1 First Complete Run

30 rounds (Apr 1841 — Feb 1845), claude-haiku-4-5-20251001 via Claude Code CLI. 304 LLM calls, 1401 events, ~81 min.

**Result**: Community limps to round 30 with 3 survivors. Morale 0% for 20 straight rounds.

| Metric | Final |
|--------|-------|
| Food | 10 (emergency purchases) |
| Money | $241 (down from $500) |
| Morale | 0% (since round 11) |
| Departed | Hawthorne (R11), Dwight (R21) |
| Survived | Ripley, Sophia, Dana |

**Key findings**:

1. **Hawthorne's departure timing matches history** — Left round 11 (Dec 1842). Real Hawthorne left Nov 1842. The simulation reproduced this without being told when he left.

2. **Intellectuals don't farm** — Only 22 FARM actions in 150 agent-rounds. Ripley did half of all farming. Food collapsed by round 5. This IS Brook Farm's documented failure mode, reproduced structurally.

3. **The speech spiral** — Dana gave ~15 speeches about the financial crisis while farming only 3 times. The community talked about its problems more than it worked on them.

4. **Sophia as load-bearer** — Taught 20/30 rounds, satisfaction stayed high. The school was the only functional institution — matching history.

5. **Ripley's sacrifice** — Farmed the most, satisfaction hit 0 by round 13, stayed 17 more rounds at 0. Matches the real Ripley who spent 13 years repaying Brook Farm's debts.

Full analysis: [`runs/run_20260401_235509/RUN_NOTES.md`](runs/run_20260401_235509/RUN_NOTES.md)

## Docs

| File | What |
|------|------|
| [DESIGN.md](DESIGN.md) | Original experiment design — candidates, environment, evaluation |
| [BROOK-FARM-PERSONAS.md](BROOK-FARM-PERSONAS.md) | 6 persona cards, timeline, economic model, Blithedale mappings |
| [AGENT-DESIGN-V1.md](AGENT-DESIGN-V1.md) | v1 agent system — 3-phase rounds, structured memory, conversations |
| [LOGGING-SPEC.md](LOGGING-SPEC.md) | JSONL event stream specification — 15 event types |
