# Utopia

Can we simulate historical utopian communities with AI agents modeled after real participants — and reproduce documented failure modes?

## The Experiment

Drop AI agents (each modeled after a real historical person) into a shared environment. Let them interact autonomously. Compare what emerges to what actually happened.

**Key insight**: If agents reproduce the same schisms, collapses, and power dynamics without being told what happened — those failure modes are structural, not uniquely human.

## First Target: Brook Farm (1841-1847)

Transcendentalist commune in Massachusetts. Founded by George Ripley, joined by Nathaniel Hawthorne (who later wrote a novel about it). Well-documented failure: intellectuals vs workers split, Fourierist conversion, phalanstery fire, financial collapse.

**5 agents** modeled from real biographies:
- **George Ripley** — Founder, visionary, carried the debt for 13 years after
- **Nathaniel Hawthorne** — Skeptic, writer, left after 18 months
- **Sophia Ripley** — Co-founder, ran the school (only reliable income)
- **Charles Dana** — 22-year-old pragmatist, spoke 10 languages
- **John Sullivan Dwight** — Music critic, cultural heart

## How It Works

Each simulation round has 3 phases:

1. **Act** — Each agent observes the environment and chooses an action (farm, teach, build, write, propose a rule, leave...)
2. **Talk** — 2-3 conversation pairs interact. Voting happens if rules are proposed. Agents argue, persuade, confide.
3. **Reflect** — Each agent privately updates their memory: what mattered today, how they feel about each person, what worries them.

Agents have **structured memory**: permanent key moments, evolving relationships (trust + attitude per person), running concerns, and observations about others that spread as gossip.

Historical events are injected at the right time: Brisbane's Fourierist visit, the phalanstery proposal, smallpox, the fire.

## First Result

30-round run (Apr 1841 — Feb 1845). 304 LLM calls, ~81 min.

| | Simulation | History |
|---|---|---|
| Hawthorne departs | Round 11 (Dec 1842) | Nov 1842 |
| Core failure mode | Intellectuals don't farm (22 FARM in 150 agent-rounds) | "Intellectual laborers" couldn't sustain farm work |
| School as lifeline | Sophia taught 20/30 rounds, only stable income | School was Brook Farm's primary revenue |
| Founder's burden | Ripley farmed most, satisfaction 0 for 17 rounds | Ripley spent 13 years repaying debts |

**Emergent pattern**: Dana gave ~15 speeches about the financial crisis while farming 3 times. The community talked about its problems more than it worked on them.

Full analysis: [`runs/run_20260401_235509/RUN_NOTES.md`](runs/run_20260401_235509/RUN_NOTES.md)

## Running Experiments

### Quick start (uses Claude Code CLI / Max subscription)

```bash
# Single run
python simulate_v1.py 30

# With experiment config
python simulate_v1.py --config experiments/baseline_seed0.json

# Batch run
python experiment.py experiments/baseline_seed0.json experiments/no_hawthorne.json

# All experiments
python experiment.py experiments/
```

### With Anthropic API

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python simulate_v1.py 30 --backend api
```

### After a run

```bash
# Derive narrative, character arcs, metrics, conversations, votes
python derive.py runs/<run_dir>/events.jsonl

# Compare multiple runs
python compare.py runs/baseline_* runs/no_hawthorne_*
```

## Experiments

9 experiment configs in `experiments/`:

| Config | What | Question |
|--------|------|----------|
| `baseline_seed[0-4].json` | 5 identical runs, different seeds | Is the failure mode reproducible? |
| `no_hawthorne.json` | Remove the skeptic | Does the community last longer? |
| `no_sophia.json` | Remove the school backbone | Does losing the only income source accelerate collapse? |
| `no_ripley.json` | Remove the founder | Does anyone else step up? |
| `double_food.json` | Start with 200 food | Does more time change the outcome? |

## Status

- [x] Historical research — 5 persona cards with real biographies ([BROOK-FARM-PERSONAS.md](BROOK-FARM-PERSONAS.md))
- [x] v1 simulation engine — 3-phase rounds, structured memory, conversations, voting, gossip ([simulate_v1.py](simulate_v1.py))
- [x] JSONL event stream — 15 event types, single source of truth ([LOGGING-SPEC.md](LOGGING-SPEC.md))
- [x] First complete run — reproduces Hawthorne departure and intellectual farming failure
- [x] Experiment infrastructure — config-driven runs, batch execution, cross-run comparison
- [ ] Reproducibility (5 baseline runs) — in progress
- [ ] Counterfactual experiments — in progress
- [ ] Visualization / documentary
- [ ] Second community (Oneida, New Harmony)

## Project Structure

```
simulate_v1.py      Main simulation engine (v1)
derive.py           Extract outputs from events.jsonl
experiment.py       Batch experiment runner
compare.py          Cross-run analysis tool
experiments/        Experiment config files (JSON)
runs/               Simulation output (events.jsonl + derived files)
simulate.py         v0 engine (reference, not used)
run_v0_local.py     v0 local test run (reference)
```

## Design Docs

| File | What |
|------|------|
| [DESIGN.md](DESIGN.md) | Original experiment design |
| [BROOK-FARM-PERSONAS.md](BROOK-FARM-PERSONAS.md) | Persona cards, timeline, economic model |
| [AGENT-DESIGN-V1.md](AGENT-DESIGN-V1.md) | v1 agent system design |
| [LOGGING-SPEC.md](LOGGING-SPEC.md) | JSONL event stream specification |
