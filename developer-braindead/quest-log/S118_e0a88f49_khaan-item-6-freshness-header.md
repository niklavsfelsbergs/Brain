# S118 — Khaan item 6: resume freshness header (context-hash freshness, gielinor port)

**Session.** sid e0a88f49. Dev-brain via "lets develop gielinor", mid-conversation. OPEN posted; no live Braindead siblings ([[S112_c7986694_cockpit-terminal-scroll-up-lock|S112]]–[[S117_fa446492_close-check-player-ritual|S117]] all CLOSED; only stale intent files).

**Ask.** "lets continue with khaan." Per the respawn ★ NEXT + the [[S117_fa446492_close-check-player-ritual|S117]] close, the agreed next cheap carry was **item 6 — context-hash freshness**, teed up to be scoped fresh in a new session.

## The judgment call (decided WITH the principal, multiple-choice)

Item 6 carried the same brittleness trap that **held item G** ([[S116_caa72357_khaan-item-g-judgment-call|S116]]). Khaan stamps every active artifact with `context_hash = sha256(prompt)[:16]` and rejects on mismatch. Ported *literally* onto gielinor resume files this false-trips every turn — the prompt changes each turn, so the stamp reads "stale" immediately → alert fatigue, exactly what the failure-banners work (items 2/5) exists to prevent. Meanwhile gielinor resume files already carry most of the freshness signal informally (`# RESUME — … — S120 cont. (2ae1248b)` title, a date in prose, `sid8` in the filename).

Offered three options; principal chose **Cheap non-brittle header** (hash-free):

- **A (chosen):** small machine-readable header (`quest` / `sid8` / `ts`) on `inventory/<slug>-resume__<sid8>.md`; respawn reconciliation **surfaces** age + quest-mismatch as a *note*, never hard-blocks.
- B: literal `sha256(prompt)` port — advised against (the false-trip trap).
- C: HOLD like item G — defensible (title+filename+prose already carry signal) but the principal opted to build.

The chosen preview was hash-free, which I honored: the explicit `quest`/`sid8`/`ts` fields **are** the identity check, so a `context_hash` would be redundant *and* reopen the false-trip surface. This delivers item 6's *intent* (a staleness check on resume state) with a better-fit, legible mechanism — the same adaptation move as item 5 (take Khaan's mechanism, fit our substrate).

## Built

1. **Convention doc (canonical spec)** — new `## Freshness header` section in both `gielinor/players/{jebrim,zezima}/inventory/_about.md`: the three fields, the explicit "fields ARE the identity check / no cryptographic hash / read-not-enforced" rationale, and the write→read→verify pointers. *(Freely writable — inventory layer doc.)*
2. **Write side** — `gielinor/spellbook/rituals/close-session.md` step 3 now opens the resume file with the header + a migration note (existing headerless resumes get the header on next close, this step overwrites each pass — mirrors the [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] sid8-suffix migration). Plus a 5th bullet in step 10's gate list. *(User-only ritual — principal explicitly authorized.)*
3. **Read side** — `gielinor/spellbook/rituals/respawn.md` reconciliation prompt step 2 gains a bullet: read the header, surface `ts` age + any `quest`/`sid8` mismatch as a *note, not a block* ("N days old / tagged for quest X — stale?"); absence is fine (legacy). Pointer added in step 6.i. *(User-only ritual — authorized.)*
4. **Enforcement** — `developer-braindead/verification/close_check.py` gains a 5th `run_player` arm `check_freshness_header_player`: asserts the header on **this session's own** resume files. Parse-lenient (substring scan of top 15 lines, not strict YAML → no benign-format false-trip) and bounded to the current sid8 (legacy/other-session resumes never inspected). Docstring updated.

## Verified (BOTH ways)

- Temp-tree: STAMPED resume → PASS; UNSTAMPED → FAIL with the specific missing keys.
- Vacuous: dev sid8 e0a88f49 (no gielinor in-progress quest) → PASS ("no resume header required").
- Integrated `--ritual player` on historical `2ae1248b` → the new "resume freshness header" row appears and correctly FAILs (those live-Jebrim resumes predate the convention — *correct*, not a bug; read-only, left untouched).
- Dev path (`run_dev`) structurally unchanged (still 5 checks; FAILs only because this dev session isn't closed yet). `py_compile` clean.

## Decisions

- **Hash-free by design.** The `quest`/`sid8`/`ts` triple is the identity check; a content-hash is both redundant with those fields and the source of the item-G false-trip. (Logged in `plan.md` §P.7.)
- **Surface, don't block.** A freshness mismatch is a reconciliation *note*; the principal decides resume / abandon / reconcile. Matches the brain's HITL-brakes posture.
- **Enforce the stamp, bounded.** The close_check arm is a real FAIL-able check (enforcement-fires culture), but scoped to the current sid8 so it can't false-trip on the legacy corpus.

**Cascade.** No further doc cascade needed — the convention is documented at its canonical home (`inventory/_about.md`) and both rituals + the gate reference it; `plan.md` §P.7 records the close-out.

**Main-brain changes.** `gielinor/players/{jebrim,zezima}/inventory/_about.md` (convention), `gielinor/spellbook/rituals/close-session.md` (step 3 header + step 10 bullet — user-only, authorized), `gielinor/spellbook/rituals/respawn.md` (reconciliation surfacing — user-only, authorized).

## Open / left for next

- `meta/write-rules.md` "enforced by hook" line via a godly proposal at the next `Hey Guthix, bankstand` (meta user-only, [[D-032_godly_proposal_flow_and_code_bearing_seam|D-032]]) — the remaining cheap carry.
- Item 4 (5-lens decision scaffold, Low/Low, optional) is the only other near-term Khaan item; everything else is later-phase.
- Untouched: all jebrim/zezima player WIP (incl. the live `2ae1248b` EU-tender resumes the gate's header arm flagged), cockpit/*, .claude/hooks/, switchboard/*.log, state.ndjson.
