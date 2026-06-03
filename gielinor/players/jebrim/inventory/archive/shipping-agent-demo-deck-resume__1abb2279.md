# Resume — Shipping-agent demo deck (S076)

**Status:** in-progress (deliverable built + rendered; open decisions remain)
**Quest:** `quest-log/in-progress/S076_1abb2279_shipping-agent-demo-deck.md`

## Where we are
11-slide Marp deck for the shipping-agent DEMO is built, styled in the brain-docs theme (dark parchment + gold), and rendered to `.html` + `.pptx` (+ per-slide PNGs). Tuned for business stakeholders. All artifacts live in `Documents/GitHub/shipping-agent/demo/` — **uncommitted, untracked** in that (separate) repo. No pending external actions.

## Slide order (11)
1 title · 2 old way (BI ticket pain) · 3 new way (conversation) · 4 what you can ask · 5 🔴 LIVE DEMO (backdrop — prompts not yet locked) · 6 it thinks before it answers · 7 how it was "trained" (taught, not trained) · 8 why you can trust the number · 9 honest about limits · 10 get it running (4-step flow) · 11 paste-this message (FINAL — contains ship_mart_ro password).

## Next concrete step — three principal decisions (all optional polish; quest blocks on these)
1. **Password redaction?** Slide 11 + `.html`/`.pptx`/`.011.png` show the `ship_mart_ro` password verbatim. Internal-acceptable per bank note, but if the deck travels by email → redact that one line on the slide, distribute full message separately. *Principal call.*
2. **Lock the live-demo prompts** on slide 5 (currently a 3-item backdrop) — pick the actual questions to run live.
3. **Commit/push the deck** to picanova/shipping-agent? Separate repo, push principal-gated; if yes, `git commit -- demo/<pathspec>` only (shared-index hazard), and decide whether the credential should be in version control at all.

## Files / paths to read first
- `Documents/GitHub/shipping-agent/demo/shipping-agent-demo.md` — the deck source (edit + re-render)
- Render cmd: `CHROME_PATH="…/chrome.exe" npx -y @marp-team/marp-cli@latest shipping-agent-demo.md --pptx --html --images png --allow-local-files`
- `gielinor/players/jebrim/bank/notes/projects/shipping-agent-onboarding-message.md` — source of the slide-11 message (+ credential note)
- `gielinor/players/jebrim/keepsake/current.md` — shipping-mart routing context
