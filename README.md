# Digital Brook Farm: Simulating Utopia with AI Agents

**[Watch the replay](https://menggg.me/utopia/replay.html)** — step through 30 rounds of AI agents trying to build utopia.

**[Read the blog post](https://menggg.me/blog/utopia.html)** — the full story of what happened and why.

What happens when you give AI agents the personas of real historical people, drop them into a shared world with scarce resources, and let them try to build utopia?

We built a simulation of **Brook Farm** (1841-1847), the most famous failed utopian commune in American history. Five AI agents, each carrying the biography, motivations, and private doubts of a real person who lived there. No one told them how the story ends.

**They figured it out themselves.** The skeptic proposed financial transparency rules. The artist organized concerts until guilt drove him to the fields. The teacher hit satisfaction 100 four times while the community died around her. The founder farmed until he broke.

---

## The Cast

Each agent gets a persona card built from historical research: who they were, why they joined, what they secretly wanted, and what skills they brought.

| Agent | Role | The Real Person |
|-------|------|-----------------|
| **George Ripley** | Founder, visionary | Former minister who staked everything on proving idealism works |
| **Nathaniel Hawthorne** | Trustee of Finance, writer | Joined for money, not ideology. Could not write. Hands full of blisters. |
| **Sophia Ripley** | Head of School | George's wife. Ran the only profitable operation. Missed two classes in six years. |
| **Charles Dana** | Editor, finance manager | 22, self-made, spoke ten languages. The "get things done" person. |
| **John Sullivan Dwight** | Music teacher | Failed minister turned music critic. Organized the evening gatherings. |

---

## How It Works

Each round has 3 phases:

1. **Act** — Each agent observes resources, relationships, gossip, and their own satisfaction. Chooses one action.
2. **Talk** — 2-3 conversation pairs selected by trust dynamics. Agents say one thing, think another.
3. **Reflect** — Private memory update: key moments, evolving trust, current concerns — and a community morale assessment.

Community morale = the average of all agents' private assessments. No formula decides how the community feels — the agents do.

The critical design decision: **agents are never told what historically happened.** Their persona says who they are, not what they did. If Hawthorne leaves, it's because the simulation dynamics pushed him there.

Full system architecture: [v1/DESIGN.md](v1/DESIGN.md). What changed in v3: [V3-DESIGN.md](V3-DESIGN.md)

---

## Run It Yourself

**Cost per 30-round run:** ~940K tokens (376 LLM calls).

By default, the simulation uses the **Claude CLI** (`claude` command) — no API key needed. Or use the Anthropic API for faster runs.

🍿 The live output reads like a novel unfolding in your terminal — full dialogue, inner monologues, key moments, trust shifting round by round. Grab coffee; each round takes a few minutes, and there's always something happening. Enjoy it!

Use `--clean` for compact output if you prefer just the headlines.

```bash
# Default: uses Claude CLI (no API key needed, ~80 min)
python simulate_v3.py 30

# Faster: use Anthropic API (~$0.40/run)
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python simulate_v3.py 30 --backend api

# Compact output (no inner thoughts, short conversations)
python simulate_v3.py 30 --clean
```

---

## Build Your Own Utopia 🏛️

If you would like to build your own utopia, we have build a little interactive wizard to help you customize Brook Farm or design a community from scratch:

```bash
python create_persona.py
```

**Start with Brook Farm** — you get 5 historical members, then customize:

- **Remove** someone — "What if Hawthorne never joined?" → instant counterfactual
- **Edit** someone's persona — change their motivation, personality, private goals
- **Add** someone new — pick from "what if?" presets or create from scratch:

| Extra Character | Role | The Question |
|----------------|------|-------------|
| **Thomas Reed** | Farmer | What if someone who actually liked farming joined? |
| **Silas Warren** | Merchant | What if someone competent with money showed up? |
| **Eliza Crane** | Journalist | What if a skeptic came to write an exposé? |

The wizard generates a JSON persona file. 
Or skip the wizard — copy [`personas/template.json`](personas/template.json) and edit the JSON to build your community directly.

**Run it and that's all** 

```bash
python simulate_v3.py 30 --personas personas/my_community.json
```

Then enjoy the live show from your terminal. All run logs are saved locally, so no worries, the history is well preserved after it finishes:

```bash
# Extract narrative, character arcs, metrics from any run log
python derive.py runs/<run_dir>/events.jsonl

# A replay tool help you navigate the whole thing from the log
python replay.py runs/<run_dir> -i
```

Now go and see if your community survives!

---

## What We Found

Five agents, modeled from real biographies:

| Agent | Role | What They Did |
|-------|------|---------------|
| **George Ripley** | Founder | Farmed 10 of 30 rounds. Satisfaction hit 0. Carried the community on guilt. |
| **Nathaniel Hawthorne** | Skeptic | Proposed financial transparency (R2, passed 5-0). Wrote his way back from despair. |
| **Sophia Ripley** | Teacher | Taught 9 rounds, wrote 9. Hit satisfaction 100 four separate times. Purpose-proof. |
| **Charles Dana** | Pragmatist | Wrote 9 times, gave 14 speeches about the financial crisis. The weight of knowledge. |
| **John Sullivan Dwight** | Artist | Organized 5 concerts (sat 100), then farmed out of guilt (sat 28). Hobbies are load-bearing. |

Community morale declined smoothly from 80% to 1% over 30 rounds — no cliff, no flatline. Each agent found their own trajectory:

| Agent | Satisfaction Shape | Why |
|-------|-------------------|-----|
| Hawthorne | U-curve (75 → 51 → 87) | Writing heals what truth-telling breaks |
| Dwight | Inverted U (80 → 100 → 31) | Concerts sustain, guilt destroys |
| Sophia | Plateau (78 → 100) | School is purpose-proof |
| Ripley | Steady decline (70 → 0) | Farming burden, unrewarded sacrifice |
| Dana | Decline with late recovery | Knowledge weighs, expression helps |

Deep dive: [V3-ANALYSIS.md](V3-ANALYSIS.md)

Counterfactual experiments (remove one person, double food, etc.) are running. Results will update here.

---

## Project Structure

```
simulate_v3.py           Simulation engine (rich live output by default)
create_persona.py        Interactive wizard — customize Brook Farm or build from scratch
replay.py                Replay past runs in your terminal (clean/rich, interactive)
derive.py                Extract narrative, character arcs, metrics from events.jsonl
compare.py               Cross-run analysis
experiment_v3.py         Batch experiment runner

personas/                Community persona files
  brook_farm.json        Default — the original 5 members
  brook_farm_with_farmer.json  "What if a real farmer joined?"
  template.json          Blank template with inline docs

experiments/             9 experiment configs (counterfactuals, seeds)
runs/                    Completed runs with full event logs

V3-DESIGN.md             System architecture and design decisions
V3-ANALYSIS.md           Findings from v3 runs
BROOK-FARM-PERSONAS.md   Historical research — persona cards, timeline, economic model
LICENSE                  CC BY-NC 4.0
```

### Earlier Versions

The simulation went through three iterations. Each fixed a real problem:

- **v1/** — The original experiment. Proved agents can reproduce historical dynamics — Hawthorne left on schedule, intellectuals refused to farm. But morale was formula-driven and hit 0 by round 10 in every run. Deep dive: [v1/ANALYSIS.md](v1/ANALYSIS.md)
- **v2/** — Added passion bonuses, softer economy, neutral prompts. 9 runs proved the failure is reproducible but the narrative varies wildly by seed — marriage dissolution, governance trauma, zombie communes. Deep dive: [v2/V2-ANALYSIS.md](v2/V2-ANALYSIS.md)
- **v3** (current) — Made morale agent-driven. Produced smooth decline curves, differentiated character arcs, and the richest narratives.

Each version's code, configs, runs, and analysis are preserved in their folders.

---

## What's Next

Beyond Brook Farm, there are dozens of documented utopian experiments: Oneida, New Harmony, the Shakers. Each failed differently. Each is a test case.

The code is open. You can write your own persona cards and run your own commune tonight. Maybe yours will survive.
