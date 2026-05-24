// The fleet board (left column). One reactive view over the session model.

import { html } from "htm/preact";
import { useState, useRef } from "preact/hooks";
import { nameFor } from "./names.js";

const STATE_LABEL = {
  working: "WORKING",
  waiting_for_answers: "Waiting for answers…",
  waiting_for_user: "WAITING ON YOU",
  waiting_for_subagents: "AWAITING CREW",
  alching: "ALCHING",
  wrapped_up: "WRAPPED UP",
  idle: "IDLE",
  ended: "ENDED",
  unknown: "…",
};

function fmtAge(s) {
  if (s < 60) return s + "s";
  if (s < 3600) return Math.floor(s / 60) + "m";
  return Math.floor(s / 3600) + "h";
}

function Row({ s, selected, onSelect, onRename }) {
  const cls =
    `row state-${s.state}` + (s.attention ? " attention" : "") + (selected ? " selected" : "");
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
        <span class="dot"></span>
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
        <span class="chip">${STATE_LABEL[s.state] || s.state}</span>
        <span class="age">${fmtAge(s.age_sec)}</span>
      </div>
      ${s.first_prompt && html`<div class="prompt">${s.first_prompt}</div>`}
      ${s.doing && html`<div class="doing">${s.doing}</div>`}
      ${s.subagents.length > 0 &&
      html`<div class="crew">
        crew
        ${s.subagents.map(
          (a) => html`<span class="sub" title=${a.kind}>${a.kind[0].toUpperCase()}</span>`
        )}
      </div>`}
    </div>
  `;
}

export function Board({
  sessions, err, selectedId, onSelect, onNew, onRename,
  soundOn, onToggleSound, feedOn, onToggleFeed,
  zoom, onZoomIn, onZoomOut, onZoomReset, onCollapseBoard, onToggleFocus, focused,
}) {
  const waiting = sessions.filter((s) => s.attention).length;
  return html`
    <aside class="board-col">
      <header class="topbar">
        <h1>SWITCHBOARD</h1>
        <span class="count">
          ${sessions.length} live${waiting
            ? html` · <b class="warn">${waiting} need you</b>`
            : ""}
        </span>
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
              selected=${s.session_id === selectedId}
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
