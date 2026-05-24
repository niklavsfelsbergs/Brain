# Proposal: mark bankstanding step 3 (cross-player synthesis) dormant until N≥2

**Drafted:** 2026-05-23 (B-004 closure, guthix-dfcbc740)
**LANDED:** 2026-05-24 (B-006) — dormancy gate applied to `bankstanding.md` step 3 after a 5th consecutive N=1 no-op.

## 1. Observation

Bankstanding step 3 — cross-player synthesis — has produced **no work for four consecutive rounds**:

- B-002 (2026-05-23 00:32 CLOSING) — synthesis read, no-op.
- B-003 (2026-05-23 ~01:00 CLOSING) — "N=1-populated still no-op on cross-player synthesis (third consecutive — flagged as candidate godly proposal next round)."
- B-004 pre-walk (guthix-ba467555) — "still N=1 effective (Zezima pre-operational) — third consecutive no-op, godly-proposal candidate carried from B-003."
- B-004 closure (this round) — re-verified: Jebrim is the sole operational player (14 `examine/confirmed` + 4 `niksis8_character/confirmed`); Zezima's confirmed `current.md` files are empty placeholders.

The step asks the agent to find patterns recurring **across** players and graduate them to the global layer. That is structurally impossible with one operational player — there is no "across" to read. The no-op is not a finding; it is a fixed consequence of the current roster, and it will recur every round until a second player accrues confirmed content.

## 2. Proposed change

Add a short dormancy gate to the top of step 3 in `gielinor/spellbook/rituals/bankstanding.md`. Diff-shaped:

```
### 3. Cross-player synthesis — promote recurring patterns to the global layer

+ **Dormancy gate.** This step requires ≥2 players carrying confirmed content in
+ `examine/` or `niksis8_character/`. If only one player is operational (others
+ pre-operational / placeholder), the step is structurally dormant — there is no
+ cross-player recurrence to detect. Note "step 3 dormant (N=1)" in the trace and
+ move on; do not re-deliberate. Re-activate when a second player has confirmed
+ entries.

  Read across what's been confirmed in each player's `examine/` and
  `niksis8_character/`. Look for patterns that recur across players:
  ...
```

## 3. Reasoning

- **Stops wasted deliberation.** Four rounds have each re-derived the same conclusion. The gate turns a recurring judgment call into a one-line check.
- **Preserves the signal for when it matters.** The step isn't removed — it reactivates automatically once Zezima (or any second player) carries confirmed content. Nothing is lost.
- **Honest about state.** "Dormant (N=1)" is a more accurate trace line than "synthesis: no-op," which reads like the agent looked and found nothing rather than that the lookup was structurally void.

Cost to land: one small edit to a user-only ritual file. No migration, no backfill.

## 4. Scope of impact

- Touches only `gielinor/spellbook/rituals/bankstanding.md`, step 3.
- Affects only the bankstanding ritual's behavior. No other actor, layer, or hook.
- No data migration. Existing traces stay as-is.

## 5. Alternatives considered

- **Defer again (carry to next round).** Rejected — that's what B-002/B-003 did; deferral is the problem this proposal fixes.
- **Remove step 3 entirely.** Rejected — it becomes correct and valuable the moment a second player is operational; deleting it would lose the integrative mechanism.
- **Auto-detect and silently skip in the agent's head, no ritual text change.** Rejected — the dormancy is worth documenting so a future operator (or a fresh respawn) doesn't read four "no-op" traces and wonder if synthesis is broken.

## 6. Risk if landed wrong

Minimal. Worst case: the gate is phrased such that a future operator skips step 3 even after a second player is operational. Mitigated by the explicit "re-activate when a second player has confirmed entries" clause and the N≥2 phrasing. If the gate ever causes a missed synthesis, the cost is one deferred graduation — surfaced again the next round.
