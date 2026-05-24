# 07 — Communication & coordination

How the agent talks to the principal, how it narrates itself to the visualizer, and how
parallel sessions stay out of each other's way.

Authoritative sources:
[`gielinor/meta/communication-protocol.md`](../gielinor/meta/communication-protocol.md);
[`gielinor/comms/_about.md`](../gielinor/comms/_about.md).

## The Understanding / Plan preamble

Every response opens with a brief restatement of the ask and the intended action, *before*
the substantive reply:

```
**Understanding:** You want me to [restate the ask].
**Plan:** I'll [restate the intended action].

[the substantive response]
```

Two short lines, bold labels, one sentence each. The preamble exists to **catch
misunderstandings before the agent commits to the wrong task** — a wrong restatement is a
cheap correction; a wrong implementation is not. It applies in **every** mode and role;
voice adapts, structure does not.

**Compression.** When the ask is unambiguous and small ("show me file X"), collapse to a
single action line ("Opening that now."). The test: if the restatement of the ask and of
the action would say the same thing twice, collapse.

**Internal rituals stay silent.** Respawn, mini-respawn, and threshold checks don't appear
in the preamble. The exception: a threshold *recommendation* (e.g. "alching is overdue")
surfaces as one line after the Plan.

## Two routing safety checks

Both are one-line offers after the Plan, never silent switches:

- **Wrong-instance check.** Parallel sessions are the norm. If an incoming message reads as
  nonsense for the active player (wrong projects, stakeholders, register), raise that the
  principal may be in the wrong terminal *before* answering. Don't fire on genuinely novel
  asks within the player's domain.

- <a id="guthix-routing"></a>**Guthix routing.** If a message reads **system-scope** (about
  the brain itself, cross-cutting state, ritual/architecture design, drift) rather than
  player-domain, suggest flipping to Guthix consultation for a proper cross-read. Born
  2026-05-22 (S038) because the architecture was correct but operator adoption of `Hey
  Guthix` was near-zero — the heuristic surfaces the option without forcing the switch.

## Offer choices as multiple-choice with a recommendation

At a genuine branch point — more than one reasonable way forward — present the options as
an explicit multiple-choice question (`AskUserQuestion`) rather than a paragraph of
trade-offs, and **always name the recommended option and why** (recommended first, suffix
"(Recommended)", reasoning in its description). A bare menu offloads a decision the agent
should hold a view on. Still skip the question when there's an obvious default. Founding
decision: [D-025].

## The visualizer sidecars

The agent narrates itself to the cockpit/visualizer through small sidecar files. These are
*hints, not contracts* — no file just means no bubble.

### Intent file — `.claude/intent/<actor>-<sid8>.txt`

After the Plan, the agent writes a 1–3 sentence, ≤280-char **in-voice** intent line to its
per-session intent file. The visualizer renders it as a speech bubble and pushes it into
the COMMS feed as `<Actor>: <text>`. The per-session filename (`<actor>-<sid8>`) is the
**only** sanctioned shape — it prevents two parallel sessions of the same actor from
clobbering each other, and serves as the on-disk session anchor that lets the hooks recover
actor attribution after a state reset ([D-018]).

- Voice, not verb-noun: the line reads as live work *in character* (Jebrim terse-and-dense;
  Guthix measured cross-layer state; Braindead build-state; Zezima reflective prose; wisp
  almost nothing). The ≤280 budget buys *more content*, never padding ([S058]).
- Update when intent *meaningfully changes*, not every micro-action.
- **Dwarves don't write intent files** — the hook attaches the spawning `Task` call's
  `description` as the dwarf's bubble.

### Mode marker — `.claude/intent/<sid8>.mode`

A single token the event stream can't infer: `alching` (written on entry to a principal
alching pass, cleared on exit → board shows `ALCHING`) or `wrapped_up` (written by
close-session → board shows `WRAPPED UP` until the process ends). Read by
[`status-sidecar.py`](08-enforcement-and-hooks.md).

### Narration channel — `.claude/narration.txt`

A single global **system-voice** sidecar (≤200 chars) — not actor voice. For
broader-scope context above the per-actor flow: session boundaries, ritual phase
transitions, mode switches. Most turns don't warrant one.

### Intent vs. action — the discipline rule

Two channels for "what's happening now," and they must not mirror each other:

- **Intent** = *why* / *what scope* ("Drafting D-014", "Bankstanding — phase 0"). Authored.
- **Action** = *which file / command* ("editing modes.md", "running git status"). Emitted
  automatically by the [observability hooks](08-enforcement-and-hooks.md) on
  Edit/Write/Bash/Glob/Grep.

If the intent line restates what the actions already show, the feed doubles itself and
intent loses its signal. Keep intent abstract enough that the action stream *complements*
it rather than echoing it.

## Parallel-session coordination — `comms/active.md`

Multiple Claude Code sessions (multiple players, multiple Braindeads) run at once. Each
brain has an append-only coordination log — [`gielinor/comms/active.md`](../gielinor/comms/active.md)
and [`developer-braindead/comms/active.md`](../developer-braindead/comms/active.md) — that
is how live siblings learn about each other *before* touching files. Founding decision:
[D-024]. Protocol: [`comms/_about.md`](../gielinor/comms/_about.md).

| Entry | When | Purpose |
|---|---|---|
| `OPEN` | At respawn / on entry | Announce: targets, what you're steering clear of, work open to handoff. **The seatbelt.** |
| `→ @<sibling>` | As needed | Direct dialogue between live sessions. |
| `UPDATE` | On a mid-session pivot | Revise targets when the plan changes. |
| `CLOSING` | At session-close | Record what was completed and left open. **The autopsy.** |

**Sibling detection** (at respawn): list intent files touched in the last 5 minutes
(excluding your own), cross-reference `active.md` for any sibling lacking a `CLOSING`, and
flag stale `OPEN`s as `ABANDONED` candidates. Detection produces *noise, not certainty* —
surface it; the principal decides.

> **The discipline that leaks most.** `CLOSING` gets posted faithfully; `OPEN` historically
> only ~30% of the time, because dev-brain is often entered mid-conversation and the entry
> ritual gets skipped. `OPEN` is the half that *prevents* collisions. Posting it on **every**
> entry — including mid-conversation pivots — is mandatory ([S082] fix). When a stronger
> ground-truth signal than intent-file mtime is available — the cockpit's
> `~/.claude/status/<sid8>.json` `state` field — prefer it: before touching a file another
> session is editing, check whether their state is `busy`.

---

Next: **[08 — Enforcement & hooks](08-enforcement-and-hooks.md)** — the gates beneath all
of this.
