# S093 — cockpit transcript readability pass + terminal fit-while-hidden fix

**Session:** braindead-f3239bdc · 2026-05-25 · dev-brain via "lets develop gielinor" (mid-conversation; OPEN posted; no live Braindead siblings — S092 just CLOSING'd).

**One line:** The S092 clean-text transcript landed but read poorly; three principal-driven rounds turned it from a flat document into an actual reading surface, and a fourth round fixed a terminal-collapse bug the toggle exposed. All in `cockpit/web/`. Doc-free, no hooks, no backend.

## The arc

Principal showed the live transcript ("not very well designed") and asked for suggestions, picking from a menu each round.

**Round 1 — structure (`transcript.js` + `styles.css`).** It rendered a conversation as a flat document — every block equal weight, raw tool dumps (full file reads) crowding out the prose, hierarchy inverted. Landed:
- **#1 Collapse tool calls** — tools are now a one-line head (chevron · name · arg · *N lines* · copy-output), collapsed by default, expand on click; errors auto-open. `ToolBlock` component with per-block `open` state. Copy works collapsed. The biggest single win — the prior render kept the result `<pre>` always-open (a regression vs the peek console's `<details>`).
- **#2 Turn boundaries + speaker** — each turn carries a speaker header (actor name / `You`) + a hairline divider (`.tv-turns > * + *`); user turns became a right-aligned column. The empty `tv-turn-bar` strip is gone (copy-turn rides the speaker row).
- **#3 Reading width** — prose capped (later 66ch); code/tool blocks stay wide.
- **#5 De-dupe** — dropped the redundant `tv-hint` sentence; header's "transcript · clean copy" stays. Bar repurposed for controls.
- **#6 Strip + unify** — `strip line #s` toggle drops Read's `cat -n` prefix (`^[ \t]*\d+\t`) from view + copies, conservative so bash/grep pass through; tool-output sized to match code blocks. Persisted.
- **#7 Font size** — `A−`/`A+` drive `--tv-scale` on the panel root; scoped sizes are `calc(base * var(--tv-scale))`. Persisted (0.8–1.7).

**Round 2 — readability ("hard on the eyes", `styles.css` + `md.js`).** The structure was right; the surface was wearing the cockpit's OSRS chrome, which fights reading. Root finds: `.term-col` carries the feTurbulence **paper grain** *under* the body text; warm monochrome (cream on grained brown + orange vignette); ~20 boxed gold inline-code chips per turn; Trebuchet/RuneScape UI font for long-form; flat headings; and **`md.js` never parsed ordered lists** (`1.`/`2.` fell through to spaced `<p>`). Landed (all scoped to `.transcript-view` except the md.js fix):
- Grain off + calmer flatter bg `#1c1813`; inline code → faint `rgba(...,0.08)` wash + dimmer ink; gold heading hierarchy (1.3/1.15/1.02em + top margin); Segoe UI reading font (code stays mono); 66ch measure + em-based rhythm.
- **`md.js` ordered lists** — `listBuf` now carries `{type, items}`; matches `^\s*\d+[.)]\s+`, flushes on type switch, emits `<ol>`/`<ul>`. Shared fix → peek view benefits too. Functionally tested via node import.

**Round 3 — terminal collapse-to-2-cols (`term.js`).** Principal: the terminal sometimes renders ~3 chars wide, "especially when switching between transcript and terminal." Root cause: the `ResizeObserver` on the term container (term.js:217) fires when `<Term>` goes `display:none` under the transcript (container → 0×0); `fitNow()` ran `FitAddon.fit()` on the zero box, flooring `cols` to xterm's 2-col minimum and resizing the PTY to match (Claude then redraws its whole TUI 2 chars wide). Fix: guard **both** the RO callback (skip scheduling when `!clientWidth || !clientHeight`) and `fitNow()` (bail when `clientWidth < 2 || clientHeight < 2`). While hidden they no-op; the RO re-fires with a real box on re-show. Also covers a zoom change made while the transcript is showing (`applyTermZoom` calls `fitNow` on all live terms). Live screen recovers fully on the first real resize; only already-scrolled history stays wrapped.

## Verification

- `node --check` green: transcript.js, main.js, term.js, md.js.
- `md.js` ordered-list parse tested by import: `1.\n2.\n3.` → `<ol>`; mixed ul→ol flushes correctly.
- CSS has no checker — eyeballed; all reading-polish rules scoped to `.transcript-view` so board/feed/peek chrome is untouched.

## Left open (EYES-ONLY, post-relaunch — running window holds stale code)

1. **Transcript reads easy:** flat calm bg (no texture behind text), inline code is a quiet wash not bright chips, `##` headings show gold breaks, numbered lists render as tight lists, prose wraps at a comfortable measure, `A−`/`A+` scales all of it and survives reopen, `strip line #s` cleans a Read block + its copy. Selection still sticks while the session works.
2. **Terminal fit:** flip terminal⇄transcript several times + zoom while on transcript, then back to terminal → stays full-width every time (no 2-col collapse). Peek Console (VS Code rows) unchanged.
3. **Open aesthetic calls if round 2 isn't enough:** could go serif for the reading font instead of Segoe UI; could tune the `#1c1813` bg further.

## Commit

Scoped: `cockpit/web/{transcript.js, styles.css, md.js, term.js}` + this quest-log + respawn.md + comms CLOSING. NOT `cockpit/_probe_ask.py` (sibling's throwaway). No push.
