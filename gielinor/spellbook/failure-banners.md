# failure-banners — locked failure receipts for rituals

Every ritual that can fail mid-step has **one byte-locked failure banner**. On any step failure, the agent emits that ritual's banner **verbatim** and **halts the ritual** — it does not narrate the failure softly and carry on, and it never silently falls back to a stale or partial artifact.

Borrowed from the Kha'an brain's `_alert.py` convention (see the dev-brain Khaan benchmark, plan §P / item 2). The point is a *consistent, recognizable shape* of failure: the principal learns to read these banners at a glance, so a failed load or a half-finished promotion is caught the moment it happens instead of being discovered later as a silent-wrong-answer.

## The doctrine — no silent fallback

When a ritual step cannot complete as written (a required file won't read, a `git mv` fails, a subprocess errors, an invariant doesn't hold):

1. **Emit the ritual's banner verbatim** — copy the exact block from the registry below. Do not paraphrase it; the byte-for-byte sameness is what makes it recognizable.
2. **State the specific failure** in one line under the banner — which step, which file, what error.
3. **Halt the ritual.** Do not proceed to the next step. Do not substitute a stale artifact (yesterday's resume file, a partial draft list, a cached count) for the one that failed to produce.
4. **Surface to the principal** and wait. The principal decides: retry, skip the step deliberately, or abandon the ritual.

A halt is **stop-and-surface**, not a session brick. There is no gate-binary to get stuck behind here — the banner is a *receipt*, not a lock. (The brain's one true positive *gate*, the `require-open-on-entry.py` hook, is a different mechanism that fails open by design; failure banners do not need that escape because halting a ritual never blocks the next tool call.)

## The registry — one banner per ritual

Each banner is the canonical, byte-locked string. Emit exactly this.

### respawn (`spellbook/rituals/respawn.md`)

```
## RESPAWN HALTED -- I am operating without my full memory
A load step failed. I have NOT loaded my full identity/state this session and will not act as if I have. Tell me how to proceed.
```

### alching (`spellbook/rituals/alching.md`)

```
## ALCHING HALTED -- a transmutation did not complete
A promotion or move failed mid-ritual. The knowledge layer is in a partial state; I have NOT updated last-alched and will not pretend the pass finished. Tell me how to proceed.
```

### drafts-triage (`spellbook/rituals/drafts-triage.md`)

```
## DRAFTS-TRIAGE HALTED -- a verdict did not land
A draft move failed. Some verdicts may be applied and some not; I will not report the triage as clean. Tell me how to proceed.
```

### born-link lint (`developer-braindead/bank/research/born-link-lint.py`)

```
## BORN-LINK LINT FAILED -- the graph is not safe to commit
A malformed wikilink or a failed migrate pass means the commit was blocked rather than silently mangled. Fix the listed link(s) and re-commit.
```

This banner is a real script's output, not agent discipline: `born-link-lint.py` carries it as a Python constant (`BANNER`) and prints it verbatim on its block / migrate-failure paths. The Python constant is the **mirror**; this registry entry is the **canonical**. They must match byte-for-byte — item 5's golden-file verification (plan §P.3) asserts the equality so the two copies can't drift.

## How a ritual references this

Each agent-performed ritual carries a one-line **Failure handling** pointer near the top:

> **Failure handling.** On any step failure, emit this ritual's locked banner from `spellbook/failure-banners.md` verbatim and halt — never silently fall back to a stale or partial artifact.

The banner text lives here (one canonical place); the ritual only points. Adding a new ritual = add its banner here + the one-line pointer there.

## Related

- `spellbook/rituals/respawn.md`, `alching.md`, `drafts-triage.md` — the ritual procedures that point here.
- `developer-braindead/bank/research/born-link-lint.py` — the one banner wired into real code.
- `meta/communication-protocol.md` — the Understanding/Plan surface; a halt-and-surface is a louder sibling of the threshold-recommendation exception.
