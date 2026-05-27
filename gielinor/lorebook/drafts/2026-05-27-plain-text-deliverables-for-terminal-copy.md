# Present copyable deliverables as plain text, not code blocks

**Type:** operating rule (communication). Drafted 2026-05-27 (Jebrim player session, sid 201f195c). Pending confirmation — proposed D-027.

**What changed.** When producing text the principal will copy out of the terminal and paste somewhere else (email, Slack, a ticket, a doc), present it as **plain prose** — never inside a fenced code block or a markdown blockquote. Code formatting stays reserved for things that genuinely *are* code: shell commands, file paths, config snippets, literal code.

**Why.** In a terminal, the clean way to copy text is to select it directly and copy — that yields **plain text** that pastes as normal text anywhere. Markdown decoration fights that:

- A **fenced code block** renders monospace, and copying it (via the copy button or selection) carries code styling into the target — e.g. Outlook showed the pasted email-draft in monospace. "The block is not clean."
- A **blockquote** prefixes every line with `>`; selecting it drags the `>` markers into the clipboard, and the nested `-` bullets render as `> -` instead of clean bullets.

Plain prose has neither problem. The principal selects the relevant span and gets exactly the characters, no styling.

**What triggered it.** Direct user workflow feedback, this session. Niklavs was pasting an IT-ticket draft into an Outlook compose window; the code-block version pasted as monospace ("the block is not clean. It should copy as normal text not a code block"). He then generalized it: *"I want to be able to copy all kinds of convos we have not just stuff I specifically ask for to be copyable."* — i.e. the agent should never wrap copyable content in markdown that resists a clean paste, so *any* part of the conversation copies cleanly the same way.

**Mechanism (so the agent can remind the principal how to grab text).** Windows Terminal captures the mouse while Claude Code's TUI runs, so a plain click-drag may not select. **Hold Shift while click-dragging**, then Ctrl+C — this bypasses the app's mouse capture, uses Windows Terminal's own selection, and produces clean plain text. Works on any message, not just deliverables.

**The distinction to hold.** Prose deliverables (emails, messages, tickets, notes the principal will send) → plain text. Literal code, commands, paths, config → code formatting is still correct and wanted (monospace is a feature there). The rule is about prose-to-paste, not about banning code fences.

**What it affects.** Added directly to `meta/communication-protocol.md` this session under explicit principal authorization ("Lets update relevant docs to communicate this way going forward") — section *Copyable deliverables — plain text, not code blocks*. Applies to every actor and mode (players, Guthix, Braindead, unscoped). Related working-preference: [[D-025_offer-multiple-choice-with-recommendation|D-025]] (also a comms rule born from direct workflow feedback) and the *lead with send-ready surface* discipline in [[2026-05-26-lead-with-send-ready-artifact]].
