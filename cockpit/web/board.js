// The fleet board (left column). One reactive view over the session model.

import { html } from "htm/preact";
import { useState, useRef } from "preact/hooks";
import { nameFor } from "./names.js";
import { reconcileSlots, slotFor } from "./slots.js";

// S139 taxonomy. The MAIN status is the primary chip (one of a small set); the
// rest are SUB-bubbles. ACTION NEEDED = blocked on a question list; the close
// ritual is two-phase (S141): WRAPPING UP = mid-wrap (closing started, not done),
// WRAPPED UP = finished + lingering; ALCHING/BANKSTANDING = rituals promoted to main.
const MAIN_LABEL = {
  busy: "BUSY",
  your_move: "YOUR MOVE",
  needs_you: "ACTION NEEDED",
  closing: "WRAPPING UP",
  done: "WRAPPED UP",
  alching: "ALCHING",
  bankstanding: "BANKSTANDING",
  ended: "ENDED",        // filtered off the board; here for completeness
  unknown: "…",
};

// SUB-bubbles ride below/beside the chip — small secondary annotations, never
// the primary status. Liveness (idle/stalled), demoted rituals, and the
// always-secondary rituals (consulting/drafts). Crew rides its own kind-letter
// row. (S139)
const SUB_LABEL = {
  idle: "idle",
  stalled: "stalled",
  closing: "wrapping up",
  alching: "alching",
  bankstanding: "bankstanding",
  consultation: "consulting",
  drafts: "drafts",
};

function fmtAge(s) {
  if (s < 60) return s + "s";
  if (s < 3600) return Math.floor(s / 60) + "m";
  return Math.floor(s / 3600) + "h";
}

function Row({ s, num, selected, onSelect, onRename }) {
  // The main status drives the chip + the row's colour class (S139). Fall back to
  // the semantic state for any row that predates the main/subs fields.
  const main = s.main || s.state;
  const subs = s.subs || s.tags || [];
  const cls =
    `row state-${main}` + (s.attention ? " attention" : "") +
    (s.stale ? " stale" : "") + (selected ? " selected" : "");
  // Custom label: cockpit-terminal renames live in localStorage (nameFor),
  // VSCode-session renames come off disk via the model (s.name). Either wins
  // over the bare actor name, and suppresses the ·N instance suffix. (S073)
  const label = nameFor(s.sid8) || s.name;
  // Double-click the name to rename from the board itself — a board operation,
  // so it works even while the session is mid-turn (the /rename hook can't, it's
  // gated to prompt submission). Enter/blur commits, Esc cancels; commit fires
  // exactly once via blur (Enter & Esc both just blur the input). (S077)
  const [editing, setEditing] = useState(false);
  const cancelRef = useRef(false);
  const onCommit = (e) => {
    const save = !cancelRef.current;
    cancelRef.current = false;
    setEditing(false);
    if (save) {
      const v = e.target.value.trim();
      if (v !== (label || "")) onRename(s.sid8, v);
    }
  };
  return html`
    <div class=${cls} onClick=${() => !editing && onSelect(s)}>
      <div class="row-head">
        ${/* The status dot doubles as the chat's recycling number (slots.js) —
              identity (the digit) and status (the disc colour + pulse) share the
              one mark. */ ""}
        <span class="dot">${num || ""}</span>
        <span
          class="actor"
          title="double-click to rename"
          onDblClick=${(e) => { e.stopPropagation(); setEditing(true); }}
        >
          ${editing
            ? html`<input
                class="rename-input"
                type="text"
                value=${label || ""}
                autofocus
                onClick=${(e) => e.stopPropagation()}
                onKeyDown=${(e) => {
                  if (e.key === "Enter") { e.preventDefault(); e.target.blur(); }
                  else if (e.key === "Escape") { e.preventDefault(); cancelRef.current = true; e.target.blur(); }
                }}
                onBlur=${onCommit}
              />`
            : html`${label || s.actor}${!label && s.instance > 1
                ? html`<span class="inst">·${s.instance}</span>`
                : ""}`}
        </span>
        ${s.host === "vscode" ? html`<span class="tag">vscode</span>` : ""}
        <span class="chip">${MAIN_LABEL[main] || (main || "").replace(/_/g, " ")}</span>
        ${subs.map(
          (t) => html`<span class=${"flavor flavor-" + t}>${SUB_LABEL[t] || t}</span>`
        )}
        ${/* The age chip shows time since last action (so the same-status sort —
              most-recently-active on top — is legible), with session lifetime in
              the hover title. Was age_sec (lifetime), which read 0s on fresh rows
              and gave nothing to sort by. (S134) */ ""}
        <span
          class="age"
          title=${fmtAge(s.age_sec) + " old · last active " + fmtAge(s.quiet_sec ?? s.age_sec) + " ago"}
        >${fmtAge(s.quiet_sec ?? s.age_sec)}</span>
      </div>
      ${/* Subheader: Claude Code's auto-title (same text VSCode shows) once it
            exists, else the first prompt until the title is generated. */ ""}
      ${(s.ai_title || s.first_prompt) &&
        html`<div class="prompt">${s.ai_title || s.first_prompt}</div>`}
      ${s.doing && html`<div class="doing">${s.doing}</div>`}
      ${s.subagents.length > 0 &&
      html`<div class="crew">
        crew
        ${s.subagents.map(
          (a) => html`<span class=${"sub sub-" + (a.kind || "unknown")} title=${a.kind}>${(a.kind || "?")[0].toUpperCase()}</span>`
        )}
      </div>`}
    </div>
  `;
}

export function Board({
  sessions, err, selectedSid8, onSelect, onNew, onRename, onHistory,
  soundOn, onToggleSound, feedOn, onToggleFeed,
  zoom, onZoomIn, onZoomOut, onZoomReset, onCollapseBoard, onToggleFocus, focused,
}) {
  // Reconcile the recycling chat numbers against the live set before rendering
  // rows, so dropped slots free up and new sessions claim the lowest free one.
  reconcileSlots(sessions);
  return html`
    <aside class="board-col">
      <header class="topbar">
        <h1>SWITCHBOARD</h1>
        <span class="topbar-right">
          <button
            class=${"icon-btn" + (soundOn ? " on" : "")}
            onClick=${onToggleSound}
            title="sound when a session needs you"
          >
            ${soundOn ? "🔔" : "🔕"}
          </button>
          <button
            class=${"icon-btn" + (feedOn ? " on" : "")}
            onClick=${onToggleFeed}
            title="toggle the activity feed (Ctrl+J)"
          >
            ▦
          </button>
          <button class="icon-btn" onClick=${onHistory} title="history — reopen a past chat (Ctrl+H)">↺</button>
          <button class="newbtn" onClick=${onNew} title="start a new conversation">+ new</button>
          <button class="icon-btn" onClick=${onCollapseBoard} title="collapse board (Ctrl+B)">‹</button>
        </span>
      </header>
      <div class="board">
        ${err && html`<div class="err">backend unreachable — ${err}</div>`}
        ${sessions.length === 0 && !err && html`<div class="empty">no live sessions</div>`}
        ${sessions.map(
          (s) =>
            html`<${Row}
              key=${s.sid8}
              s=${s}
              num=${slotFor(s.sid8)}
              selected=${s.sid8 === selectedSid8}
              onSelect=${onSelect}
              onRename=${onRename}
            />`
        )}
      </div>
      <footer class="board-foot">
        <span class="zoomctl">
          <button onClick=${onZoomOut} title="zoom out (Ctrl+-)">−</button>
          <button class="zval" onClick=${onZoomReset} title="reset zoom (Ctrl+0)">${Math.round(zoom * 100)}%</button>
          <button onClick=${onZoomIn} title="zoom in (Ctrl+=)">+</button>
        </span>
        <span class="spacer"></span>
        <button
          class=${"icon-btn" + (focused ? " on" : "")}
          onClick=${onToggleFocus}
          title="focus mode — hide side panels (Ctrl+\\)"
        >
          ⤢
        </button>
      </footer>
    </aside>
  `;
}
