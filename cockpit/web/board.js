// The fleet board (left column). One reactive view over the session model.

import { html } from "htm/preact";

const STATE_LABEL = {
  working: "WORKING",
  waiting_for_user: "WAITING ON YOU",
  waiting_for_subagents: "AWAITING CREW",
  alching: "ALCHING",
  closing: "CLOSING",
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

function Row({ s, selected, onSelect }) {
  const cls =
    `row state-${s.state}` + (s.attention ? " attention" : "") + (selected ? " selected" : "");
  return html`
    <div class=${cls} onClick=${() => onSelect(s)}>
      <div class="row-head">
        <span class="dot"></span>
        <span class="actor">
          ${s.actor}${s.instance > 1 ? html`<span class="inst">·${s.instance}</span>` : ""}
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

export function Board({ sessions, err, selectedId, onSelect, onNew, soundOn, onToggleSound, feedOn, onToggleFeed }) {
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
            title="toggle the activity feed"
          >
            ▦
          </button>
          <button class="newbtn" onClick=${onNew} title="start a new conversation">+ new</button>
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
            />`
        )}
      </div>
    </aside>
  `;
}
