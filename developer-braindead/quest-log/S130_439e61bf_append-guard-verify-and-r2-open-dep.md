# S130 — append-guard live-verify + §R.2 open-dep marker (sid 439e61bf)

**Date.** 2026-05-30. Dev-brain via "lets develop gielinor", mid-conversation; OPEN posted (no live siblings — [[S128_b64229ad_comms-append-lock|S128]] b64229ad CLOSED, [[S129_e291b8fc_cockpit_polish_3d_brain|S129]] e291b8fc committed). Fresh session, picked up the two [[S128_b64229ad_comms-append-lock|S128]] hand-offs.

## What was asked

Pick a direction from the [[S128_b64229ad_comms-append-lock|S128]] hand-off. Principal chose (multiple-choice): **live-verify the append-guard hook + scope §R.2 delta-first**. Then, on the scope: **build the convention now**; then **apply** the user-only close-session edits and **wrap up**.

## What happened

### 1. Append-guard hook — LIVE-VERIFIED (clears the [[S128_b64229ad_comms-append-lock|S128]] debt)

[[S128_b64229ad_comms-append-lock|S128]] shipped `gielinor/.claude/hooks/comms-append-guard.py` but left it **load-unverified** — a new hook does not load mid-session, so [[S128_b64229ad_comms-append-lock|S128]] never watched it fire. This fresh session was exactly the condition needed.

- **Live block confirmed:** a raw `Edit` on `developer-braindead/comms/active.md` was intercepted by the hook with exit 2 and the correct stderr (the actual Edit tool, not a synthetic probe). The guard loads and bites from a cold start.
- **All branches green** (synthetic payloads via Bash): no-env → exit 2; `COMMS_ROTATE=1` → exit 0 (escape works); non-comms path (`_about.md`) → exit 0; gielinor `active.md` → exit 2 (both vaults guarded).
- Cosmetic note (not fixed): the hook's stderr em-dash mangles in the Windows console (`directly �`) — display only, the block is unaffected. Optional polish for a future pass.

### 2. §R.2 — scoped delta-first, then built

Per the respawn's emphatic **DELTA-FIRST not build-first** steer, diffed Jebrim's proposed "graduation = clerk-not-nanny" shape (plan.md §R.2) against the landed [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] in `gielinor/spellbook/rituals/close-session.md` L119–128.

**Finding: 4 of 5 of Jebrim's elements already live in [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]]** — fix-the-discriminator ("no open dep" not "closed"), auto-file-unambiguous-silently, veto-only-the-ambiguous, never-hard-block. [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] (godly proposal, 2026-05-29) independently arrived at almost exactly Jebrim's shape.

**The one genuine delta:** Jebrim's "put the cheap half on the player." Today "no named open dependency" is a **soft agent judgment** (the agent infers it from the quest body); there is no defined, player-writable open-dep field. The sharp example is *this* session: work done, but two open deps live (ritual one-liners awaiting sign-off; §R.3 → bankstanding) — `Next concrete step: none` ≠ `no open dependency`.

Grounding confirmed: `close_check.py` has player arms but **no graduation/open-dep arm** ([[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] is ritual-prose only); the resume file already carries the [[S118_e0a88f49_khaan-item-6-freshness-header|S118]] **freshness header** (`quest`/`sid8`/`ts`, read-not-enforced) — the natural slot for the marker.

**Built (the minimal convention, not a graduation engine):**

- **`open_dep` field added** to both players' `inventory/_about.md` freshness-header convention — `open_dep: none | <text>`, player-declared, read-not-enforced, one line. (Agent-writable `_about` doc.)
- **`close-session.md` updated** (user-only ritual; applied on explicit principal go-ahead, [[D-017_user-only-with-explicit-permission|D-017]]): step-3 header block + write-instruction now carry `open_dep`; step-4 classify reads the field first, infers from the body only as a legacy fallback. Backward-compatible — absent field → today's behavior.
- close_check arm: **deferred** (optional, thin guard — the classification judgment can't be mechanized per the [[S121_03861733_ritual-analytics-item-11|S121]] constraint; only the marker axis is now a read field).

**Cascade.** None. The change is additive convention + ritual prose; no per-carrier/status tables, no downstream docs depend on it. `inventory/_about.md` (both players) and `close-session.md` are mutually consistent (same field name, same semantics).

**Main-brain changes.**

- `gielinor/players/jebrim/inventory/_about.md` — `open_dep` freshness-header field + bullet.
- `gielinor/players/zezima/inventory/_about.md` — same.
- `gielinor/spellbook/rituals/close-session.md` — step-3 header + write-instruction, step-4 classify (user-only, principal-authorized).

## Open

- **§R.3 — render the cut, not the keystrokes** — still deferred; a gielinor `meta/communication-protocol.md` change = a Guthix **godly proposal at next bankstanding**, not a Braindead edit.
- **2 gielinor ritual one-liners from [[S128_b64229ad_comms-append-lock|S128]]** (respawn 6.g + close-session CLOSING `comms_append` pointers) — still await principal sign-off.
- read_comms `--last-conversation` dual-opener + ffmpeg-clean concat (optional tool polish).
- append-guard stderr em-dash console-mangle (cosmetic).

active-mode → unscoped at close.
