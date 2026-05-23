// The activity feed (right column) — the cross-fleet "watch what's happening"
// stream. Lifecycle checkpoints + comms merged; raw actions off by default.
// Click an item to jump to its session.

import { useState, useEffect, useRef } from "preact/hooks";
import { html } from "htm/preact";

const KIND_LABEL = {
  picked_up: "PICKED UP",
  intent: "PROGRESS",
  needs_you: "NEEDS YOU",
  done: "DONE",
  action: "",
  comms: "COMMS",
};

function fmtClock(ts) {
  return new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function FeedItem({ i, onJump }) {
  const label = i.kind === "comms" ? i.subkind || "COMMS" : KIND_LABEL[i.kind] || "";
  const who = i.kind === "picked_up" ? "NIKLAVS" : i.actor || "—";
  return html`
    <div class=${"feed-item k-" + i.kind} onClick=${() => i.sid8 && onJump && onJump(i.sid8)}>
      <div class="fi-head">
        <span class="fi-actor">${who}</span>
        ${label && html`<span class="fi-kind">${label}</span>`}
        <span class="fi-time">${i.ts ? fmtClock(i.ts) : ""}</span>
      </div>
      <div class="fi-text">${i.text}</div>
    </div>
  `;
}

export function FeedPanel({ onJump }) {
  const [items, setItems] = useState([]);
  const [showActions, setShowActions] = useState(false);
  const elRef = useRef(null);
  const pinned = useRef(false);

  useEffect(() => {
    let alive = true;
    async function poll() {
      try {
        const r = await fetch("/api/feed");
        const j = await r.json();
        if (alive) setItems(j.items || []);
      } catch {}
    }
    poll();
    const id = setInterval(poll, 2000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;
    if (!pinned.current) {
      if (el.scrollHeight > el.clientHeight) {
        el.scrollTop = el.scrollHeight;
        pinned.current = true;
      }
      return;
    }
    if (el.scrollHeight - el.scrollTop - el.clientHeight < 160) el.scrollTop = el.scrollHeight;
  });

  const shown = items.filter((i) => showActions || i.kind !== "action");
  return html`
    <aside class="feed-col">
      <div class="feed-head">
        <span>FEED</span>
        <label class="feed-toggle">
          <input type="checkbox" checked=${showActions} onChange=${(e) => setShowActions(e.target.checked)} />
          actions
        </label>
      </div>
      <div class="feed-items" ref=${elRef}>
        ${shown.length === 0 && html`<div class="feed-empty">quiet</div>`}
        ${shown.map((i, idx) => html`<${FeedItem} key=${idx} i=${i} onJump=${onJump} />`)}
      </div>
    </aside>
  `;
}
