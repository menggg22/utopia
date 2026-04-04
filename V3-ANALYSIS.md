# V3 Analysis: When Agents Tell You How They Feel

One run. 30 rounds. 376 LLM calls. The only change from v2: morale is no longer a formula. Each agent reports how they feel about the community's direction, and morale = the average.

That one change produced the most interesting run we've seen.

## The Morale Curve

```
R1: 80  R5: 62  R10: 38  R15: 19  R20: 6  R25: 2  R30: 1
```

No cliff. No flatline. A smooth, 30-round decline from 80% to 1% — the shape of a community learning to live with its own failure.

In v1, morale hit 0 by round 10 and stayed there for 20 rounds. In v2, it hit 0 by round 14 and stayed there for 16 rounds. In v3, it never hits 0. The agents always report at least 1% — a sliver of something. Not hope, exactly. More like: we are still here.

### Agents Mostly Agree

The individual morale scores cluster tightly each round — typically within 5-10 points of each other. The agents are reading the same environment and reaching similar conclusions. This is what collective sentiment looks like: not identical, but convergent.

The exception is Sophia. In round 19, everyone reports 4-5 except Sophia at 12. In round 23, everyone reports 1-2, Sophia reports 8. She consistently rates the community higher than anyone else — the school gives her a reason to believe even when everything else is failing.

### No Recovery, But No Trap Either

The decline is roughly -5/round in the early game, slowing to -2 as it approaches zero. This is realistic: decline accelerates when things feel salvageable ("we could fix this if we just farmed more"), then flattens into resignation ("this is who we are now").

The key difference from v1/v2: there's no formula preventing recovery. If agents had a genuinely good round — a successful concert, a harvest, an honest conversation that cleared the air — morale *could* go up. It just didn't happen to, in this run. That's a finding, not a bug.

---

## The Hawthorne Reversal: Skeptic Becomes Reformer

In v1 and v2, Hawthorne's first instinct was withdrawal — retreat to writing, avoid the fields, leave when the contradiction became unbearable.

In v3, his second action (R2) is **proposing a financial transparency rule**: daily record-keeping, monthly accounting reviews by all trustees. It passes 5-0 — the only unanimous vote in the run.

His inner thought: *"This place will collapse if no one insists on order. Ripley dreams of brotherhood while the ledgers bleed confusion."*

This is new. The skeptic isn't withdrawing — he's building institutions. The golden period gave him enough stability to act constructively before the crisis forced retreat. He saw a solvable problem (chaotic finances) and proposed a structural fix — something v1 Hawthorne never did because by round 2 he was already in survival mode.

### The U-Shaped Arc

Hawthorne's satisfaction tells a story no previous version produced:

```
R1-R5:   75 → 93   (teaching, proposing rules, writing — engagement)
R6-R17:  86 → 53   (truth-telling erodes him — 8 speeches about financial reality)
R18-R30: 53 → 87   (writing heals what truth-telling broke)
```

The middle section is the cost of being the honest one. R9: *"My hands have bled for six months in service of a dream I never truly held."* R13: *"I have not written a word in months that was not a ledger entry."*

Then R20 — he picks up his pen again. Satisfaction jumps from 51 to 60. By R26 it's 87: *"I am aware, as I reach for my pen, that I am stealing time."*

He finds equilibrium: be the financial conscience, write when the weight gets too heavy, accept the contradiction. And he stays — all 30 rounds, satisfaction 83 at the end. No departure. No dramatic exit. Just a man who found a way to coexist with failure.

V1/v2 couldn't produce this because morale's cliff forced binary outcomes: leave or suffer at 0%. V3's gradual decline gave Hawthorne room to bend without breaking.

---

## Dwight: The Collapse of the Artist

Dwight's arc is the inverse of Hawthorne's — and the most painful in the run.

```
R1-R8:   80 → 100  (concerts, teaching — six rounds of pure joy)
R9-R13:  92 → 78   (starts speaking about "the gulf between philosophy and hunger")
R14-R21: 71 → 36   (farms out of guilt — "I cannot play Beethoven while the community starves")
R22-R30: 34 → 31   (stabilizes low — writing provides small relief)
```

The first 8 rounds are Dwight at his best. He organizes 4 concerts, teaches, hits satisfaction 100 three times. His inner thought at R3: *"I know what this looks like: the impractical musician fiddling while the ledgers burn. But they are wrong if they think beauty is expendable."*

Then the turn. R9: *"I came here to escape the ministry because I could not bear to speak in a voice that was not mine. Now I am doing it again."* He starts giving speeches about the crisis — the artist becoming another voice in the speech spiral.

R14 is the break: *"I am a coward, and I have known it for days."* He farms. Then farms again. Each time his satisfaction drops 6-8 points. By R21: *"I will pretend to be useful while he carries the weight of everything I cannot."*

His passion is ORGANIZE (+5 bonus), but guilt drives him to FARM (-3 base). The system is working exactly as designed — the passion bonus sustains him when he follows his nature, and guilt destroys him when he doesn't. The tragedy is that he *chooses* guilt.

**But he doesn't leave.** In v1 he departed R21. In v2 seed 3 he departed R27. In v3 he stays all 30 rounds at satisfaction 31. The gradual morale decline (instead of a 0% cliff) gave him no single moment dramatic enough to trigger departure. There's no clean break point — just slow erosion.

---

## Sophia: Purpose-Proof

Sophia is the control subject. Her satisfaction barely dips:

```
R1-R8:   78 → 100
R9-R18:  91 → 83   (brief dip — speaks about restructuring, farms once)
R19-R30: 87 → 100  (recovers through writing and teaching)
```

She hits satisfaction 100 four separate times across the run. No other agent does this. Her inner thoughts explain why:

- R6 (sat 100): *"I am using the children's tuition to buy time for a community that may not survive the spring. This is not idealism. This is arithmetic."*
- R21 (sat 94): *"I have spent eight years building proof that women can lead serious institutions."*
- R24 (sat 100): *"I am teaching because I have no other certainty left... because those young women deserve better than my doubt."*
- R27 (sat 93): Her speech "On the cost of idealism to women" — she names the gendered burden explicitly.

She sees everything collapsing. She's not naive. But the school gives her purpose that's **independent of the community's fate**. Whether Brook Farm succeeds or fails, the school matters. The students matter. That's enough.

Her morale votes are consistently the highest — the community's optimist, not because she believes in the vision, but because she has work that works.

---

## Ripley: The Founder's Burden (Unchanged)

Ripley farms 10 of 30 rounds. Gives ~15 speeches. Proposes one rule (R13). Satisfaction ends at... we don't have the exact number, but his morale votes tell the story: starting at 75 and declining steadily to 1.

Some things don't change across versions. The founder sacrifices himself in every simulation. His passion bonus is for ORGANIZE and SPEAK, but he farms because nobody else will. The system creates a man who destroys himself for a community that doesn't structurally need his destruction.

R22 inner thought: *"...asking aloud whether philosophy becomes mere narcissism, I felt the ground beneath my certainty finally give way."*

---

## Dana: The Weight of Knowledge

Dana wrote 9 times (tied with Sophia for most) and gave ~14 speeches about financial reality. His arc is familiar from v2: he sees the numbers early, carries the knowledge alone, eventually shares it. The difference in v3 is that the gradual morale decline means the knowledge doesn't crash the community — it just accumulates weight.

R6 key moment: *"Hawthorne's conversation at dusk. The gap between his spoken words and his actual conviction became visible to both of us."* This is Dana noticing that the skeptic-reformer is also performing.

---

## The Three Shapes

The most important finding in v3 is that agent-driven morale lets each agent find their own satisfaction trajectory — and those trajectories are driven by *who they are*, not by the environment's arithmetic.

| Agent | Satisfaction Shape | Driver |
|-------|-------------------|--------|
| **Hawthorne** | U-curve (75 → 51 → 87) | Writing heals what truth-telling breaks |
| **Dwight** | Inverted U (80 → 100 → 31) | Concerts sustain, guilt destroys |
| **Sophia** | Plateau (78 → 100, barely dips) | School is purpose-proof |
| **Ripley** | Steady decline (70 → ~0) | Farming burden, unrewarded sacrifice |
| **Dana** | Gradual decline with late writing recovery | Knowledge weighs, expression helps |

V1/v2 couldn't produce these shapes because formula morale flattened everyone. When the environment says "morale is 0," every agent's reflection is colored by that number. When the environment says "morale is 19," agents can differentiate — Sophia sees the school working, Dwight sees his concerts mattering less, Hawthorne sees the accounts clearly.

---

## Governance: Institutions Before Crisis

Two rules were proposed and voted on:

**R2: Hawthorne's financial transparency rule.** Daily record-keeping, monthly reviews. Passes 5-0. This is round *two* — the community builds institutional infrastructure before crisis forces it. In v1, agents never proposed rules. In v2, proposals came from desperation (R4-R5). In v3, the golden period gives the skeptic time to build rather than flee.

**R13: Ripley's rule.** (Unspecified in the data — likely governance-related.) Passes 4-0-1, with Hawthorne abstaining. By R13 the community is at morale 23% — proposals now come from declining hope, not rising ambition. The contrast with R2 is telling.

---

## Nobody Left

All five agents survive 30 rounds. But this isn't the v2 seed 0 "zombie commune" where everyone stays at morale 0 out of obligation. The v3 community at morale 1% has agents with satisfaction ranging from 31 (Dwight) to 100 (Sophia). They're not trapped — they've each found their own accommodation with failure.

Hawthorne writes. Sophia teaches. Dwight suffers. Ripley farms. Dana speaks. Each is living in the same dying community, experiencing it through their own persona, finding their own level.

This is arguably the most realistic outcome we've produced. Historical Brook Farm didn't end with a dramatic departure (though Hawthorne did leave). It ended with the fire, the debts, and a slow dispersal. People didn't storm out — they gradually accepted that the experiment was over while still showing up every day.

---

## What V3 Proved

The morale formula was the last wall between the simulation and genuine emergence. Remove it, and you get:

1. **A realistic decline curve** — gradual, not cliff-then-flatline
2. **Individual differentiation** — each agent finds their own satisfaction trajectory
3. **New behaviors** — the skeptic becomes a reformer, the artist collapses from guilt, the teacher is purpose-proof
4. **No forced outcomes** — nobody is trapped at 0%, nobody is artificially sustained

The single change (formula → agent-driven morale) produced the richest narrative, the most varied character arcs, and the most realistic community dynamics of any version.

Next: run more seeds to test whether these patterns are reproducible, or whether this was v3's lucky accident.
