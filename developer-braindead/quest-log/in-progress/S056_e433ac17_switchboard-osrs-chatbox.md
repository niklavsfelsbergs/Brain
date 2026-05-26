# S056 — switchboard COMMS chatbox: OSRS reskin + readability

**Session:** braindead-e433ac17 · 2026-05-23 · dev-brain (entered via "lets develop gielinor")
**Status:** in-progress at close — code landed + `node --check` clean across 10 iterations; **awaiting live in-browser verify** (hard-refresh) and a **coordinated commit** (see Close).

## Close (session-end)

Ten iterations of switchboard chat work, all landed on disk, none committed. **Cascade (dev brain):** `switchboard/chat.js` (channel mutes, pills, flex columns, collapse, gap-rail, code-ref de-emphasis, mention-strip), `switchboard/styles.css` (OSRS bottom bar, pencil, font, layout — chat region only), `switchboard/switchboard.js` (pencil rename, sound-on-WAITING, pause-on-hover), `switchboard/index.html` (bottom bar markup, RS font link), new `switchboard/settings.js`, `developer-braindead/comms/_about.md` (gist authoring rule), this quest-log, `comms/active.md` (OPEN + ping + CLOSING). **Main-brain changes:** `gielinor/comms/_about.md` — the "lead with a human gist" authoring rule (player-side twin). **Commit: HELD** — the shared client files (`index.html`, `styles.css`, `switchboard.js`) are entangled with live siblings 3b367751/7c9033f4 ([[S060_brain_self_audit_and_plan_reconciliation|S060]] terminal/chat) + carry [[S057_switchboard_awaiting_crew_state|S057]]'s AWAITING-CREW hunks; a blanket commit would sweep their in-progress `server.py`/`terminal.js`/terminal-UI work. Deferred to a coordinated client-file commit (principal call). **No marker flip** — sibling Braindead 3b367751 is still live, so `active-mode.txt` stays `dev-brain`.

## Ask

Principal wants to keep iterating on the switchboard. Three concrete asks against the live board (screenshot):
1. The COMMS chatbox is "horrible" — make it a simple **oldschool RuneScape chatbox** (reference image: classic OSRS chat with bottom tab strip All/Game/Public/Private/Clan/Trade + red Report).
2. Add **settings buttons** in the same OSRS style — "what could we put there?"
3. Fix **rename**: it's supposed to rename the **agent name itself** so it's clearly visible (Zezima → anything), not tack on a faint side-label.

## Decisions (via AskUserQuestion)

- **Filter layout:** 6 **category channels** — All · Players · Sub-agents · Braindead · Guthix · Commits. (Players = Jebrim+Zezima+Wisp; Sub-agents = Dwarves+Gnomes+Penguins.) Per-actor granularity dropped in favour of the search box.
- **Settings toggles:** **Actions On/Off** (hide the Read/Edit/Glob/git tool-call stream — the biggest declutter) + **Sound on WAITING** (chime when a session flips to WAITING). Times/CRT not picked.

## What landed

Interaction model shift: channels are **multi-select visibility mutes** (OSRS Game/Public On/Off semantics), not the old single-select `data-filter`. You can watch Players + Braindead while muting Sub-agent noise.

- **`settings.js`** (NEW shared module, mirrors activity.js decoupling) — localStorage-backed booleans (`actions`, `sound`, per-channel) under one key `sb-settings`, plus a change bus. Both panels import it; neither imports the other.
- **`index.html`** — removed the top tab strip; search stays in the header (right-aligned). New `.chat-bar` bottom bar: `All` master + 5 channel buttons (`.cb-chan`, two-line name + On/Off `.cb-state`), then settings group (`Actions`, `Sound`) + red `Clear` (`.cb-report`, the Report slot). `styles.css?v=6` → `?v=7`.
- **`styles.css`** — replaced the whole `.log-tab*` / `[data-filter]` block with `.chat-bar` beveled-stone button styling (gradient stone, inset bevel, green `On` / red `Off` sub-labels, channel-name tints reusing `--*-dot` vars, `.off` dim, `.cb-all.active` gold, `.has-unread` flash). New `.log-scroll.mute-*` + `.hide-actions` CSS rules do the hiding (commit banners ride the Commits channel only via `:not([data-commit])` guards). Rename CSS: `.sb-label` → `.sb-name` (prominent) + `.sb-orig` (small "· Zezima" hint). `.jump-latest` bottom bumped to clear the bar.
- **`chat.js`** — dropped TAB_SPEAKERS/tab-badge machinery; added `CHANNELS` + `SPEAKER_CHANNEL` + `entryChannel()`; per-channel unread (`bumpChannelUnread` flashes a muted channel's button); `applyBar()`/`initChatBar()` wire mutes + toggles + All + Clear and reflect persisted settings on load. `SPEAKERS` set restored for `chatNdjsonSpeaker`.
- **`switchboard.js`** — `fillWho()` makes a custom name the **prominent** `.sb-name` (actor → small `.sb-orig` hint, sid8 trails). WAITING chime: WebAudio two-note ping, edge-triggered per sid8 in `chimeForWaiting()` (called from the poll), gated on `getSetting('sound')`, primed to skip first poll; audio context unlocked on first `pointerdown`.

## Verification

- `node --check` clean on all 7 modules.
- Grepped out dangling refs (fixed `TAB_SPEAKERS` in `chatNdjsonSpeaker`, dead `[data-filter]` time-rail rule).
- **Not yet visually verified** — JS modules are NOT cache-busted; principal must hard-refresh to pick up the new bar. CSS is at `?v=7`.

## Iteration 2 — readability + rename bug (same session)

Principal feedback on the first pass: (1) the top/hero row "can't be renamed, it bugs out"; (2) chat "unreadable" — timestamps don't align, inconsistent leading dots, ugly mixed fonts. Wants the actual OSRS chatbox font.

- **Rename bug — root cause:** the first `click` of a double-click fired `dispatchFocus` (live mode → vscode:// nav) which stole focus, so the rename input blurred instantly (its `blur` handler saved+closed) before you could type. Most visible on the hero row since that's the one reached for. **Fix** (`switchboard.js`): defer the single-click focus by 260ms via `clickTimer`; the `dblclick` handler `clearTimeout`s it. Shift-click copy stays immediate.
- **Font → RuneScape UF.** Loaded via CDNFonts (`https://fonts.cdnfonts.com/css/runescape-uf` — verified 200, serves `@font-face { font-family:'RuneScape UF'; src: …runescape_uf.woff }`). `.log-scroll` font-family → `'RuneScape UF', 'Trebuchet MS', Verdana, sans-serif`, weight normal, 19px, line-height 1.5, + RS-style 1px glyph drop-shadow. `.act-body` dropped its VT323 monospace override (no more font mixing) — whole chat is one font now.
- **Dots removed.** Deleted the 9 `.t::before { content:"● " }` speaker-bullet rules. Identity now carried by the color-tinted name alone.
- **Timestamp alignment.** Dropped brackets (`[14:32:05]` → `14:32:05`) in `chat.js`; `.t` is now `display:inline-block; width:70px; tabular-nums` so every speaker name starts at the same x regardless of digit widths or font.
- `styles.css?v=8` → `?v=9`.

`node --check` clean on both JS files. Still **not** visually verified in-browser — hard-refresh needed (JS modules uncached).

## Iteration 3 — rename still didn't open on the top row

Deferred-focus alone (iter 2) didn't fix it. Confirmed via the manifest that the top WAITING row (Zezima e5df54a2) *has* a sid8, so the handler was attached. **Real root cause:** the 1s age-ticker rebuilds every row's DOM; a double-click straddles a rebuild → 2nd click lands on a fresh element → no `dblclick` fires. **Fix** (`switchboard.js`): pause both the 1s ticker and the 2s poll-render while the pointer is over `sbList` (`hovering` flag + `renderPaused()`), so the DOM is stable during any interaction; resumes on mouseleave. Side benefit: rows no longer re-sort out from under the cursor. `requestRender` (post-rename) still bypasses the pause for an immediate refresh.

## Iteration 4 — scrap double-click, use a pencil button

Principal: double-click rename "operates" badly; wants an explicit button. Decided (AskUserQuestion): **pencil ✎ at the row's right edge, always visible, single-click.**
- `switchboard.js`: extracted `startRename(who, record)` (sets `editing` synchronously → render pauses before the rebuild can race it); removed the `who` dblclick handler + the `clickTimer` focus-defer (no longer needed); row click now focuses immediately again; added a `.sb-edit` `<button>` per row (stopPropagation so it doesn't also focus).
- `styles.css`: `.sb-row` grid `24px 1fr auto auto` → `…auto auto` (5th col); `.sb-intent` + `.sb-spark` grid-column `2/5`→`2/6`; new `.sb-edit` button block. All within the switchboard-row CSS region.
- Did **not** bump `styles.css?v=` (index.html is the live sibling's file) — hard-refresh picks up CSS anyway.

## Coordination state (parallel sessions — IMPORTANT for commit)

Three siblings touched switchboard files this session:
- **`213ea2ab` ([[S057_switchboard_awaiting_crew_state|S057]], closed)** added `waiting_for_subagents` / "AWAITING CREW". Its **render hunks are uncommitted in THIS working tree** and it pinged me to preserve them in the S056 commit: `switchboard.js` STATE_RANK (`waiting_for_subagents:2`, closing/idle/ended/unknown→3/4/5/6) + STATE_LABEL `'AWAITING CREW'`; `styles.css` `.sb-row[data-state="waiting_for_subagents"]` block + `@keyframes sbCrewPulse` + sparkline color. **Must NOT clobber; include in S056 commit.**
- **`e482340b` ([[S058_world_personality_in_voice_narration|S058]], closed)** longer in-voice messages — committed its own work (4af5279), avoided my files. Left optional follow-up: `.sb-intent` line-clamp 2→~4 (deferred).
- **`ac10ec71` (embedded PTY terminal, LIVE)** edits `index.html` + `styles.css` (terminal markup/styles). Overlap with me on `styles.css`. Mitigation: I touch **no** `index.html`; my `styles.css` edits are in the switchboard-row region only. Posted a heads-up to comms.

## Iteration 5 — chatbox legibility pass (10 improvements, all approved)

Principal: chatbox looks clunky, wants simple + easy on the eyes. Proposed 10, all approved. Landed in `chat.js` + `styles.css` (chat region only — ac10ec71 still live on the terminal region):
1. **Dropped per-line timestamps** — `logChatLine` no longer emits `.t`; the minute time-rail carries time. (They were all identical `15:23:31` on load = pure noise.)
2. **Hanging indent** — `.log-entry { padding-left:1.5em; text-indent:-1.5em }`; `.cont`/`.comms-body` reset. Multi-line posts read as one block.
3. **Collapse empty minutes** — `maybeTimeRail` drops a rail if the previous element is still a rail; `.time-rail:last-child` hides a trailing one.
4. **Kind pills** — `kindPill()` + `.kind-pill` (green OPEN / blue UPDATE / amber DONE / neutral ↪ dialog) replace inline `OPEN —`.
5. **Demoted sid8** — comms displayName is just the actor; `· sid8` moved to the row's hover title.
6. **Breathing room** — comms posts `margin-top:8px`, lines within a post stay tight.
7. **Calmer type** — line-height 1.5→1.58, softer ink (#2a1d12), lighter glyph shadow (0.16→0.10).
8. **Cleaner expand** — `▸`/`▾` marker forced to a symbol font (RS UF lacked the glyph → showed as `·`).
9. **Stream separation** — comms posts keep a 3px left rule (vs the action/intent `.cont` tinted rule).
10. **Content trim** — `cleanLine()` strips `Completed:`/`Shipped:` filler; dialog target strips `braindead-` (`→ @braindead-e433ac17` → `↪ e433ac17`).

`node --check` clean. No `styles.css?v=` bump (sibling owns index.html) — hard-refresh picks it up.

## Iteration 6 — wrap alignment + remove the left bars

Principal: disliked the wrap (still tucked under the username) and asked what the vertical bars were.
- **Bars** were the comms `border-left` stream-separator (iter-5 #9) — removed; separation now via pill + `margin-top` spacing only.
- **Wrap** redone as a flex two-column layout: `.log-entry { display:flex; align-items:baseline; gap:5px }`, `.user { flex:0 0 auto }`, `.body { flex:1 1 auto; min-width:0 }`. `logChatLine` wraps the body in `<span class="body">` (both header + cont branches). Replaced the iter-5 hanging-indent hack — wrapped body lines now align under the body text, not under the username, per-row regardless of name/pill width.

## Iteration 7 — narration walls + unreadable hex sid8

Principal flagged two bad parts: (a) long ownerless italic narration blocks at the top read as walls; (b) the `@braindead-<sid8>` / dialog-target hex is meaningless to a human.
- **Hex (b):** `cleanLine()` now strips `(?:→)?\s*@?[a-z]+-[0-9a-f]{8}` mention tokens from comms previews + expanded body lines; the dialog `↪` pill no longer renders the sid8 target (the pill alone signals the heads-up). So `UPDATE → @braindead-e433ac17 @braindead-ac10ec71 Hunks…` → `[UPDATE] Hunks…`.
- **Walls (a):** live intent/narrate ndjson lines clamped to `NDJSON_LINE_MAX=150` via `clip()` (the longer [[S058_world_personality_in_voice_narration|S058]] in-voice text isn't load-bearing in scrollback); `maybeTimeRail` resets `lastStreamSpeaker=null` after inserting a rail so a post-gap line re-shows its speaker name instead of rendering as an ownerless continuation.
- chat.js only; `node --check` clean. No styles bump.

## Iteration 8 — human-readable messages (authoring + display, "Both")

Principal: comms posts are unfollowable — dense agent-to-agent jargon (`.sb-row[data-state="alching"]`, `~L301`, `STATE_RANK`). Root cause: the board faithfully renders raw agent-to-agent coordination written for *another Claude* (needs file/line precision). Chose **Both** levers:
- **Authoring (durable, future messages):** added a "lead with a human gist; bury the machine detail" rule to both comms protocols — `developer-braindead/comms/_about.md` (strong version, with the bad/good example from this very handoff) and `gielinor/comms/_about.md` (lighter — players already conversational). Line 1 = plain prose a human can follow, no paths/symbols; exact refs go on line 2+. The dev channel serves two audiences (sibling Claude needs precision, principal needs to follow) — line 1 for the human, tail for the agent.
- **Display (immediate, existing messages):** `chat.js` `renderCommsText()` wraps backtick `` `code` `` spans + inline file/line refs (`foo.css`, `~L301`) in `.code-ref` (dimmed monospace) so the prose reads through the jargon. Applied to comms preview + body lines. CSS `.code-ref` added.
- chat.js `node --check` clean. Touches `gielinor/` (one doc) — first main-brain write of S056; live Jebrim/Zezima sessions won't collide on `comms/_about.md`.

## Iteration 9 — collapse the walls (clean 2-line clamp + chevron)

"Show all message" (iter 7) traded mid-word cut-offs for walls: the pre-discipline multi-paragraph comms posts dumped in full. Resolution — the stable middle:
- `renderCommsEntry` joins all body lines into one `.body` block; `.comms-collapsed .body` line-clamps to **2 lines**. After append it **measures** `scrollHeight > clientHeight` — only overflowing posts get a `⌄`/`⌃` toggle (whole-row click) + stay collapsed; short gist-first posts render full, no toggle. Replaces the separate-comms-body-divs approach.
- CSS `.comms-collapsed .body` (-webkit-line-clamp:2) + `.comms-toggle` chevron (Segoe UI Symbol, clear). Old `.comms-body` / `.comms-toggleable` rules now dead (left harmless).
- chat.js `node --check` clean. Display-only; no new doc/hook writes.
- Not addressed: long ndjson **intent** narration lines ([[S058_world_personality_in_voice_narration|S058]]) could still wall — not visible in the reported screenshot (all comms); revisit if they appear.

## Iteration 10 — time-rail is gap-driven, not per-minute

Principal: chatbox shouldn't "report every minute," only when a message comes. Rewrote `maybeTimeRail`: was per-minute-change; now gap-driven — tracks `lastMsgTs` (ms) and inserts a `HH:MM` rail only when a message arrives after `RAIL_GAP_MS` (3 min) of silence. Active chatter → zero rails; a lull → one marker on resume. Renamed `lastMinuteLabel`→`lastMsgTs` (decl + Clear handler). `node --check` clean; display-only.

## Open / next

- Live visual verify: bottom bar renders OSRS-style; channel mute toggles On/Off + flash on muted traffic; Actions toggle hides the action stream; Sound chimes on a real WAITING transition; rename replaces the prominent name.
- Possible follow-ups if principal wants more: relocate the CRT `▦` toggle into the bar; a "Times" toggle; per-actor fine-filter (currently search-only); decide whether rename should key by actor (global) vs sid8 (per-session — current).
- No commit yet (awaiting principal OK + live verify).
