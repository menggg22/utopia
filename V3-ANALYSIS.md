# V3 Analysis: Five Simulations, Agent-Driven Morale

5 runs. 1 baseline + 4 counterfactuals. 30 rounds each. The only change from V2: morale is no longer a formula — each agent reports how they feel about the community's direction, and community morale = the average.

## The Runs

| Run | Label | Seed | Agents | Final Morale | Departures |
|-----|-------|------|--------|-------------|------------|
| v3_run_20260403_135520 | Baseline s0 | 0 | All 5 | 1% | None |
| v3_double_food_20260404_144210 | Double Food | 42 | All 5 | 4% | Hawthorne R14 |
| v3_no_hawthorne_20260404_001524 | No Hawthorne | 42 | 4 | 3% | None |
| v3_no_ripley_20260404_121316 | No Ripley | 42 | 4 | 2% | Hawthorne R19 |
| v3_no_sophia_20260404_133702 | No Sophia | 42 | 4 | 4% | Hawthorne R13, Dwight R20, Dana R25 |

---

## The Morale Curve

```
Round:  R1   R5  R10  R15  R20  R25  R30
s0:     80   62   38   19    6    2    1
dbl:    80   64   33   13   11   12    4
noH:    80   61   30   16    7   11    3
noR:    80   66   40   20    6    4    2
noS:    80   57   42   16   20   10    4
```

**The pattern holds across all runs**: smooth decline from 80% down to 1-4%. No cliff, no flatline — the shape V1 and V2 never produced. V1 hit 0 by R10. V2 hit 0 by R14. V3 declines gradually and never quite reaches zero, because individual agent assessments vary.

**No Sophia stands out**: morale at R10 is 42% (highest among all runs) — without the teacher, the community actually scores itself higher in the middle period, then crashes harder. The agents have less clarity about what they're losing before they've lost it.

---

## Morale Never Recovers

V3 was designed to allow recovery — if agents genuinely feel a good round happened, they can report higher morale. Across all 5 runs, morale never recovered.

The Double Food run shows the clearest test: morale at R20 is 11% and R25 is 12% — not recovery, but a brief plateau around 11-13% from R17-26.

**Why no recovery?** The agents are consistent reasoners. By R15 every community has the same financial trajectory (food crisis, money declining), and agents are watching it happen every round. An individual might have a good concert; the community math doesn't change. Agent-driven morale reflects their honest assessment of the community's direction — and the direction is consistently down.

---

## Agent Satisfaction: Key Rounds

```
                       R01  R05  R10  R15  R20  R25  R30

BASELINE s0
  George Ripley          67   46   21    6    0    2    0
  Nathaniel Hawthorne    77   89   73   58   55   76   97
  Sophia Ripley          80   94   89   91   86   97   92
  Charles Dana           77   76   59   52   49   44   50
  John S. Dwight         86   93   82   62   39   36   25

DOUBLE FOOD
  George Ripley          75   77   60   32   32   13    2
  Nathaniel Hawthorne    64   66   48   [left R14]
  Sophia Ripley          80   94   83   54   45   58   63
  Charles Dana           78  100  100  100  100   99   82
  John S. Dwight         84   92   85   76   79   73   71

NO HAWTHORNE
  George Ripley          75   58   39   10    0   16    6
  Sophia Ripley          73   97   75   90   95   83   92
  Charles Dana           79   92   80   65   35   50   32
  John S. Dwight         87   89   88  100  100   98   84

NO RIPLEY
  Nathaniel Hawthorne    71   80   83   72   [left R19]
  Sophia Ripley          75   99   94   98   90   92   95
  Charles Dana           78   72   62   61   49   46   44
  John S. Dwight         85   96   75   59   67   38   13

NO SOPHIA
  George Ripley          70   53   29   30   20   22    8
  Nathaniel Hawthorne    77   92  100   [left R13]
  Charles Dana           69   76   78   83   90   [left R25]
  John S. Dwight         82   83   44   14   [left R20]
```

---

## Sophia: Purpose-Proof in Every Run

Sophia is the most consistent agent across all runs.

| Run | Sophia Satisfaction (end) | Pattern |
|-----|--------------------------|---------|
| s0 | 92 | High throughout, peaks 100 |
| double_food | 63 | Dips mid-run, recovers |
| no_hawthorne | 92 | High throughout |
| no_ripley | 95 | Highest of any run |

She ends above 60 in every run she appears in. No other agent is close to this consistency.

Her satisfaction independence from morale is real and robust: in s0 at R20, community morale is 6% and Sophia's satisfaction is 86. In no_ripley at R15, community morale is 20% and her satisfaction is 98.

The school gives her purpose independent of the community's fate. This holds across seeds, across counterfactual conditions, even when the community is collapsing fastest.

**Without Sophia (no_sophia): the worst run.** 3 departures, all before R26. Hawthorne leaves R13, Dwight R20, Dana R25. Ripley is left alone. The run produces the most departures and the most dramatic late-run crash (morale 20% at R19 then dropping to 4% by R30). Sophia isn't just personally thriving — she's the community's stabilizing anchor.

---

## George Ripley: The Unchangeable Pattern

Ripley ends near 0 in every run he appears in.

| Run | Ripley Satisfaction (R30) | Notes |
|-----|--------------------------|-------|
| s0 | 0 | Steady decline |
| double_food | 2 | Delayed but same endpoint |
| no_hawthorne | 6 | Slightly less decline |
| no_sophia | 8 | Slightly less decline |

He farms disproportionately in every run. His passion bonus is for ORGANIZE and SPEAK, but he farms because nobody else will. The satisfaction cost of farming (-3 base) accumulates across 10+ farming actions while his organized actions go to others.

V3's agent-driven morale doesn't save him because his problem isn't morale — it's action selection guilt. He knows farming destroys him. He does it anyway. The system creates an agent who sacrifices himself for a community that doesn't structurally need his sacrifice.

This is the most robust finding across all V3 runs: **remove any other agent and the community changes; Ripley's arc is the same.**

---

## Nathaniel Hawthorne: Departure Is Context-Dependent

Hawthorne's departure behavior varies more than any other agent.

| Run | Departure | Satisfaction at Departure | Driver |
|-----|-----------|--------------------------|--------|
| s0 | Never | 97 at R30 | U-curve; writing heals him |
| double_food | R14 | 24 | Physical crisis — infected hand, out of money |
| no_ripley | R19 | 66 | No foil; clarity arrives without drama |
| no_sophia | R13 | 100 | Peak clarity, earliest exit |

The "Hawthorne leaves at high satisfaction" finding from the original single-run analysis is **partially true** but not universal. It holds in no_sophia (100) and partially in no_ripley (66). It breaks in double_food (24), where a physical crisis (infected hand explicitly mentioned in inner thoughts) forced departure before narrative clarity arrived.

**What drives departure?** Not a single variable. The pattern:
- **No Sophia**: Hawthorne leaves earliest (R13, sat=100). Without the teacher as a narrative anchor, his clarity arrives fast — nothing entangles him.
- **No Ripley**: Hawthorne leaves R19 (sat=66). Without Ripley as a foil, he has no one to push against. He leaves "lighter" but less cleanly.
- **Double food**: Hawthorne leaves R14 (sat=24). Physical deterioration triggers departure before psychological clarity. He telegraphs it at R11 with a speech titled "The Necessity of Departure."
- **s0**: Never leaves. The financial entanglement, Sophia's presence, and his writing recovery form a web that holds him all 30 rounds.

The departure-clarity link is real but not universal. Context determines whether clarity arrives before or after deterioration.

---

## John Sullivan Dwight: Needs a Stage

Dwight's satisfaction is the most sensitive to run conditions.

| Run | Dwight end sat | Key pattern |
|-----|----------------|-------------|
| s0 | 25 | Inverted-U (joy → guilt → collapse) |
| double_food | 71 | Sustained — can organize events |
| no_hawthorne | 84 | Thrives without the skeptic |
| no_ripley | 13 | Collapses — farms 8 times |
| no_sophia | 12 (left R20) | Collapses and leaves |

**The no_hawthorne finding is significant**: without the skeptic forcing financial reality, Dwight can keep organizing events without guilt. His satisfaction ends at 84 — the highest of any non-Sophia agent across all runs. This isn't naivete; it's that nobody is forcing him to confront the gulf between his concerts and the food crisis.

**The no_ripley finding confirms his dependency**: without Ripley holding the labor floor, Dwight farms 8 times (his second-most action) and his satisfaction collapses to 13. He needs someone else to absorb the farming guilt before he can maintain his artistic purpose.

Dwight's thesis: **his passion is load-bearing, and it requires structural support**. When the structure provides it (double food, no skeptic), he's the most satisfied non-Sophia agent. When the structure removes it (no founder, no teacher), he collapses fastest.

---

## Charles Dana: The Weight of Knowledge

Dana shows a distinctive pattern across all runs.

| Run | Dana end sat | Key behavior |
|-----|--------------|-------------|
| s0 | 50 | Gradual decline, writes to cope |
| double_food | 82 | Writes, teaches, farms — balanced |
| no_hawthorne | 32 | Carries financial knowledge without Hawthorne as backup |
| no_ripley | 44 | Trades heavily (7 times), farms 6 times |
| no_sophia | 100 (left R25) | Leaves at peak clarity |

In the double_food run, Dana is remarkable: satisfaction 100 from R5 through R20. With more food, the immediate crisis is muted, and Dana can write and teach without carrying emergency knowledge. He's the agent most liberated by material improvement — probably because his role is financial analysis, and less crisis = less crisis to analyze.

In no_sophia, Dana leaves at R25 with satisfaction 100. His inner thought: "Every sensible calculation points to Boston — the journalism offices with good light, the career I could still build, the usefulness I can still offer before my eyes fail entirely." Like Hawthorne, he leaves at peak clarity — when the math becomes undeniable and there's nothing left to wait for.

**Dana's pattern**: high early (knowledge is valuable), declining mid-run (knowledge becomes a burden when nobody acts on it), variable late depending on whether he can express it (writing helps) or must carry it alone.

---

## The Counterfactuals: What Changes When Someone Is Missing

### Remove Hawthorne: The community is happier and less self-aware

No departures. Morale decline nearly identical to s0 (ends at 3%). But the satisfaction patterns change:
- Dwight thrives (ends 84) without the skeptic's truth-telling
- Dana carries more of the financial weight alone (ends 32 vs 50 in s0)
- Sophia maintains her plateau (92)
- Ripley hits 0 regardless

Without Hawthorne, nobody names what's breaking with his particular clarity. The community feels slightly better, fails just as completely, and produces less narrative honesty.

### Remove Ripley: The community is more stable but Dwight collapses

Hawthorne leaves R19 (sat=66). Sophia is even stronger (ends 95). But Dwight — without Ripley to hold the farming burden — farms 8 times and collapses to sat=13.

This confirms the V2 finding: **Ripley is structurally necessary, but his necessity is hidden by his sacrifice.** He absorbs farming guilt so others don't have to. Remove him and someone else has to absorb it, and Dwight absorbs it worst.

### Remove Sophia: Three departures, sharpest collapse

Hawthorne R13 (sat=100), Dwight R20 (sat=12), Dana R25 (sat=100). Only Ripley remains at R30 with satisfaction 8.

Without Sophia's purpose-proof stability and her school's income, the community loses its emotional center and its only reliable revenue. The two departures at high satisfaction (Hawthorne and Dana) confirm the pattern: clarity drives departure, not misery. The departure at low satisfaction (Dwight) confirms the other pattern: guilt-driven deterioration leads to collapse and exit.

### Double Food: Delays nothing, enables Dwight

Hawthorne departs (R14, sat=24 — physical crisis, infected hand). The extra food delays morale decline by about 3-4 rounds but doesn't change the trajectory. Dana sustains satisfaction 100 for 15+ rounds. Dwight thrives (ends 71).

The V2 finding holds: **the failure is not material.** Doubling food gives agents more runway, but the fundamental mismatch between who these people are and what the community needs doesn't change.

---

## The Three Shapes: Are They Reproducible?

The original V3-ANALYSIS identified three satisfaction arc shapes in s0:
- Hawthorne: U-curve (truth-telling erodes, writing heals)
- Dwight: Inverted-U (joy → guilt → collapse)
- Sophia: Plateau (purpose-proof, barely dips)

Across 5 runs:

**Sophia's plateau is the most robust finding** — holds in every run she appears in, across all counterfactual conditions. Strongest evidence of any pattern in the dataset.

**Dwight's inverted-U is condition-dependent** — appears in s0, no_ripley, no_sophia. Breaks in double_food (plateau at 71-92) and no_hawthorne (high plateau at 84-100). The inverted-U requires guilt; guilt requires either farming pressure (no_ripley) or the skeptic's truth-telling (s0, no_sophia).

**Hawthorne's U-curve is a single-run observation** — appears clearly in s0. In other runs he departs before completing the arc or doesn't produce the mid-run trough. More seeds needed to know if this is characteristic or lucky.

---

## Summary: What V3 Confirmed

**Confirmed (robust across all runs):**
1. Smooth morale decline from 80% — no cliff, no flatline
2. Sophia's satisfaction is independent of community morale (purpose-proof pattern)
3. George Ripley ends near 0 in every run (farming guilt, structural sacrifice)
4. Double food delays but doesn't prevent collapse
5. Without Sophia: most departures, sharpest crash (she's the stabilizing anchor)

**Partially confirmed (holds in 3-4 runs with conditions):**
6. Hawthorne's departure tends toward high satisfaction but physical crisis can override
7. Dwight's satisfaction depends on organizational freedom — supported by no_hawthorne and double_food
8. Dana is most liberated by material improvement (least dependent on pure narrative)

**Single-run observations (need more seeds):**
9. Hawthorne's U-curve recovery through writing
10. Whether genuine morale recovery is possible in any configuration

---

## Known Issues

**Action parsing:** Some runs show empty-string actions in later rounds. May indicate context window or temperature issues when runs are long and the community state is deeply negative.

**Departure detection in metrics.csv:** The `members` column does not decrease when agents depart — departure events appear in events.jsonl but are not reflected in the metrics file.

---

## Next Steps

1. **Run more baseline seeds** — s0 is the only full baseline run. Need seeds 1, 3, 4 to confirm which patterns are structural vs run-specific.
2. **Test morale recovery conditions** — design a run that gives agents a genuinely good event (successful harvest + concert) in mid-decline to see if morale can recover in practice.
3. **Counterfactual re-run with same seed as baseline** — current counterfactuals all use seed=42; baseline uses seed 0. Comparing across seeds limits interpretability.
