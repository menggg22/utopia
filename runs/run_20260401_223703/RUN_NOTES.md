# v1 Run #1 — Notes

**Status**: Interrupted at round 17 of 30 (bugs found, not worth continuing)
**Backend**: CLI (claude-haiku-4-5-20251001 via Claude Code)
**Duration**: ~50 min for 17 rounds

## Results

| Metric | Value |
|--------|-------|
| Rounds completed | 17/30 (interrupted) |
| Food | 0 (starving since round 5) |
| Money | $770 (climbing the entire run) |
| Morale | 0% (since round 8) |
| Departed | Hawthorne (round 13) |

## What Worked

- **3-phase loop executes correctly** — act, talk, reflect all run, events logged to JSONL
- **Conversations are rich** — real dialogue with tone and inner thoughts
- **Hawthorne left** (round 13, ~mid 1843) — historically plausible
- **Relationship updates parse** — all 72 reflections have relationship data
- **Gossip spreads** — 311 gossip events across 17 rounds
- **Voting works** — 2 votes in round 2 (one passed, one failed)
- **Action diversity** — agents chose from SPEAK, TEACH, FARM, REPAIR, ORGANIZE, WRITE, PROPOSE, TRADE, LEAVE

## Bugs Found (fixed after this run)

### 1. Satisfaction always 100
The LLM set satisfaction directly (0-100) and defaulted to 100 almost every round. Occasional dips (Ripley: 25, Hawthorne: 28, 42) but instant recovery.
**Fix**: Changed to SATISFACTION_CHANGE (-10 to +10 delta per round). LLM can't jump to 100.

### 2. Food goes negative
Food hit -5 because winter drain applied after the zero clamp.
**Fix**: Moved winter drain before the clamp. All clamps at the end.

### 3. Money never stops climbing
With morale at 0% and food at 0 for 12 rounds, money still grew because school income ($15/round) + teaching actions ($10) flowed regardless.
**Fix**: School income now scales with morale (50%+ = $15, 25-49% = $8, <25% = $3). Starvation forces emergency food purchases ($20).

### 4. Key moments every round
76 key moments in 17 rounds = 4.5/round. Every agent flagged a key moment almost every round.
**Fix**: Prompt now says "Most days are NOT key moments. Write 'none' unless something extraordinary happened."

### 5. SPEAK action overused
29 SPEAK actions (38% of all actions). Agents prefer speechifying over working.
**Not yet fixed** — may self-correct with better satisfaction mechanics (speaking doesn't improve food/money).

## Other Observations

- **Too few farmers** — only 14 FARM actions in 17 rounds. Community starved by round 5.
- **Dwight farmed more than expected** (6 times!) — historically inaccurate, he was the least practical member
- **Dana barely farmed** (2 times) — historically he was a reliable worker
- **Sophia taught 11/16 rounds** — historically accurate, she was the school backbone
