# S076 — Shipping-agent demo deck

**Player:** Jebrim · **Session:** 1abb2279 · **Opened:** 2026-05-26
**Artifact repo:** out-of-tree `Documents/GitHub/shipping-agent/demo/` (NOT the brain repo)

## Ask
Principal: "Lets make a slide deck for the shipping agent DEMO. What do you suggest we put in there? I know that the final slide should be how to set it up." (Demo likely today/imminent — a prior session 006248ef opened "presenting the shipping agent tomorrow" on 05-25.)

## Subject = the NL agent, not the AWS dashboard
"Shipping agent" = `picanova/shipping-agent` — the standalone plain-English talk-to-your-data harness over the gold `shipping_mart` (Redshift, `ship_mart_ro` read-only). Distinct from S073's bi-analytics Next.js costs-monitoring dashboard on AWS.

## Decisions (principal-picked via AskUserQuestion)
- **Audience = Business stakeholders** (non-technical). → lighter on the 3 answer modes + setup mechanics, heavier on value / live demo / trust. Plain English throughout, no internal vocab.
- **Format = Marp markdown** → exports to HTML + PPTX.

## Outline shipped (9 slides)
Title → problem (old way) → new way (conversation) → what you can ask → 🔴 LIVE DEMO (centerpiece) → it thinks before it answers (modes, de-jargoned) → why you can trust the number (read-only / one source / confirms scope / states assumptions) → honest about limits (coverage holes, freshness stamp) → **setup closer** (5-min: locate folder, cp .env.example→.env, ask BI for ship_mart_ro creds, pip install, smoke-test SELECT 1, open AI session, ask) → "Ask away" closer.

## Artifacts produced (uncommitted)
- `shipping-agent/demo/shipping-agent-demo.md` (Marp source, ~3.9KB)
- `shipping-agent/demo/shipping-agent-demo.html` (self-contained, 96KB) — present from browser
- `shipping-agent/demo/shipping-agent-demo.pptx` (1.4MB, image-per-slide — presentable, NOT text-editable in PowerPoint; re-render from .md to change content)
- Rendered via `npx @marp-team/marp-cli` (Chrome present for PPTX). marp-cli not installed globally — used npx.

## State / open
- Deck drafted + rendered. **HELD uncommitted** — principal not yet asked to commit; new `demo/` folder is untracked in picanova/shipping-agent. If committing: `git commit -- demo/<pathspec>` only (shared-index hazard from 006248ef), and push is principal-gated.
- Awaiting principal review of content/design. Likely tweaks: real example numbers on slide 4 backdrop, brand/logo, trimming to ~7 slides if they want it tighter.
- Per-slide design is gaia theme + TCG-green accent; demo slide inverted (dark green / gold).

## Styling pass (turn 2, principal: "can we give some styling")
- Rebuilt theme from `theme: default` + full custom CSS block (was gaia). Branded palette: TCG green `#0b5d4e` / `#12876f`, gold `#f0b429`/`#ffd36b`, off-white paper. Top accent gradient bar on every slide, gold-underlined H2s, custom gold ▸ bullets, green ol markers, footer ("Shipping Data Agent · internal demo") + page numbers. Lead slides = green radial-gradient full-bleed; demo slide = dark-green gradient, gold heading.
- VERIFIED visually: rendered `--images png` (10 slides) and eyeballed title / content / demo — styling landed correctly. Re-rendered HTML (178KB) + PPTX (3.2MB).
- 10 per-slide PNGs left in demo/ as render previews (uncommitted, removable).

## Theme borrow (turn 3, principal: "borrow the theme from brain docs")
- Source: `brain/docs/build-html.py` `<style>` block (the brain-docs.html theme). Lifted the full palette verbatim: bg `#11130f`, panel `#181b14`, ink `#e6e3d6`, gold `#d6b24a`/`#8c7530`, link `#cdb86a`, accent (teal) `#3f7a6a`, warn `#caa24a`, code-bg `#0e100b`, strong `#f1eedd`, line `#2c3024`. Body font = docs' system stack; code = SFMono/Consolas gold-on-dark with line border.
- Mapped doc elements → slide elements: h1/h2 gold + thin `--line` underline (docs h2 rule); blockquote teal-left-border + teal bg tint (docs); code chips dark+bordered (docs). Lead slides = panel→bg radial, subtitle uppercase letter-spaced gold-link (docs nav `.brand`). Demo slide = teal-tinted radial, gold heading, warn-gold markers.
- VERIFIED visually (PNG render of slides 1/3/5/9): theme matches docs register. Re-rendered HTML (186KB) + PPTX (2.6MB). Deck is now DARK (was light off-white).

## Setup slide → real onboarding flow (turn 4)
- Principal: drop the manual cp/.env/pip steps; show the actual flow = GitHub account → download Claude Code → open folder → paste the prepared message and let it self-install.
- MISS surfaced: I grepped only the shipping-agent repo for the "prepared message" — it actually lives in MY bank: `bank/notes/projects/shipping-agent-onboarding-message.md` (built 2026-05-25 for this presentation). Lesson logged below.
- Restructured setup into 2 slides: (9) "Get it running" — 4-step flow (GitHub access via BI / `claude.ai/code` / open empty folder / paste next slide); (10) "Paste this into Claude Code" — the message verbatim in a docs-style mono code block (new `section.msg` class, 15px wrap-pre, fits one slide). Message slide is now the FINAL slide (dropped the "Ask away" closer per "final slide = setup"). Deck now 10 slides.
- **CREDENTIAL EXPOSURE NOTE:** the pasted message embeds the `ship_mart_ro` password (`ShpMart_Ro!...`). Per the bank note this is internal-acceptable (read-only, gold-only, SELECT blast radius). It is now visible in 4 demo artifacts: `.md`, `.html`, `.pptx`, and `shipping-agent-demo.010.png`. Flagged to principal: offered to redact the password line on the slide + distribute full message separately if the deck travels by email. Awaiting any call; left verbatim per the explicit "show the message I prepared" instruction.
- Repo clone URL is inside the message (`github.com/picanova/shipping-agent.git`) — no separate repo callout needed.

## "How it was trained" slide (turn 5)
- Principal: add a light technical slide on how the agent was trained. Framed HONESTLY (it's not a trained ML model — Claude + a written handbook): title `How it was "trained"`, blockquote reframe "it wasn't trained on a pile of data — it was taught the rules," 3 ingredients (rulebook / map of the data / query recipes), business takeaway (no ML project, improves by editing text). Avoids the deck getting caught out by a technical attendee — protects the trust theme.
- Inserted as slide 7, after "It thinks before it answers", before "Why you can trust the number" (groups the how-it-works beats, then the trust beats). Deck now 11 slides. Re-rendered all 3 outputs.
