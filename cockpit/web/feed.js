// The activity feed (right column) — the cross-fleet "watch what's happening"
// stream. Lifecycle checkpoints + comms merged; raw actions off by default.
// Click an item to jump to its session.

import { useState, useEffect, useRef } from "preact/hooks";
import { html } from "htm/preact";
import { nameFor, subscribeNames } from "./names.js";
import { mountBrain } from "./brain.js";

const KIND_LABEL = {
  picked_up: "PICKED UP",
  intent: "PROGRESS",
  needs_you: "NEEDS YOU",
  done: "DONE",
  action: "",
  say: "", // the agent's visible prose (transcript text blocks); reads clean, no chip
  think: "THINKING", // S132: the model's reasoning blocks; opt-in, dim
  comms: "COMMS",
};

function fmtClock(ts) {
  return new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function FeedItem({ i, onJump }) {
  const label = i.kind === "comms" ? i.subkind || "COMMS" : KIND_LABEL[i.kind] || "";
  const who = i.kind === "picked_up" ? "NIKLAVS" : nameFor(i.sid8) || i.actor || "—";
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

export function FeedPanel({ onJump, onCollapse, selSid8 }) {
  const [items, setItems] = useState([]);
  // Actions ON by default — with them off a working session looks dead (only
  // sparse lifecycle checkpoints show). Choice persists. (S066)
  const [showActions, setShowActions] = useState(() => {
    const v = localStorage.getItem("cockpit-feed-actions");
    return v === null ? true : v === "1";
  });
  // Prose ON by default — it's the agent's running commentary (kind:"say"), the
  // thing the principal wanted in the feed (S073). Toggle persists. (S073)
  const [showSay, setShowSay] = useState(() => {
    const v = localStorage.getItem("cockpit-feed-say");
    return v === null ? true : v === "1";
  });
  // Thinking OFF by default — the model's reasoning blocks (kind:"think") are
  // voluminous with interleaved thinking; opt-in only. Persisted. (S132)
  const [showThink, setShowThink] = useState(() => {
    return localStorage.getItem("cockpit-feed-think") === "1";
  });
  // "this session" OFF by default — the feed stays cross-fleet as before; flip
  // it to stop a busy sibling (e.g. bankstanding) from burying the session
  // you're watching. Keyed to the board-selected session. Persisted. (S132)
  const [thisSession, setThisSession] = useState(() => {
    return localStorage.getItem("cockpit-feed-thissession") === "1";
  });
  const elRef = useRef(null);
  // Stick to the bottom until the user scrolls up. Starts true so the first
  // load lands at the newest item. (S132)
  const pinned = useRef(true);
  const brainRef = useRef(null);
  const [, bump] = useState(0);
  useEffect(() => subscribeNames(() => bump((n) => n + 1)), []); // re-render on rename
  // the brain graph — a square docked at the top of the feed column. Mounted
  // imperatively (vanilla canvas) into a stable ref'd div, once; torn down on
  // unmount (feed collapse). The div carries no Preact children, so the 2s feed
  // re-render never disturbs the canvas underneath it.
  useEffect(() => (brainRef.current ? mountBrain(brainRef.current) : undefined), []);

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

  // Re-pin/unpin from the user's OWN scroll, measured before any new content
  // lands. The old post-append distance check unpinned whenever a single new
  // item was taller than the threshold — and prose blocks routinely are — so
  // autoscroll kept disengaging. Capturing intent at scroll time fixes that:
  // scroll up → unpin; return to the bottom → re-pin. Our own programmatic
  // scroll-to-bottom fires this too and harmlessly re-confirms pinned. (S132)
  function onFeedScroll(e) {
    const el = e.currentTarget;
    pinned.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
  }

  // After every render (new items, filter change, rename bump): if pinned,
  // snap to the newest. Unconditional when pinned — no height threshold to trip.
  useEffect(() => {
    const el = elRef.current;
    if (el && pinned.current) el.scrollTop = el.scrollHeight;
  });

  const shown = items.filter(
    (i) =>
      (showActions || i.kind !== "action") &&
      (showSay || i.kind !== "say") &&
      (showThink || i.kind !== "think") &&
      // per-session filter: keep comms (sid8 may be absent) and items for the
      // selected session only. No selection → fall back to cross-fleet.
      (!thisSession || !selSid8 || i.kind === "comms" || i.sid8 === selSid8)
  );
  return html`
    <aside class="feed-col">
      <div class="brain-dock" ref=${brainRef}></div>
      <div class="feed-head">
        <span>FEED</span>
        <span class="feed-head-right">
          <label class="feed-toggle">
            <input type="checkbox" checked=${showActions} onChange=${(e) => {
              setShowActions(e.target.checked);
              try {
                localStorage.setItem("cockpit-feed-actions", e.target.checked ? "1" : "0");
              } catch {}
            }} />
            actions
          </label>
          <label class="feed-toggle">
            <input type="checkbox" checked=${showSay} onChange=${(e) => {
              setShowSay(e.target.checked);
              try {
                localStorage.setItem("cockpit-feed-say", e.target.checked ? "1" : "0");
              } catch {}
            }} />
            prose
          </label>
          <label class="feed-toggle" title="show the model's reasoning blocks (verbose)">
            <input type="checkbox" checked=${showThink} onChange=${(e) => {
              setShowThink(e.target.checked);
              try {
                localStorage.setItem("cockpit-feed-think", e.target.checked ? "1" : "0");
              } catch {}
            }} />
            thinking
          </label>
          <label class="feed-toggle" title="only the board-selected session (vs the whole fleet)">
            <input type="checkbox" checked=${thisSession} onChange=${(e) => {
              setThisSession(e.target.checked);
              try {
                localStorage.setItem("cockpit-feed-thissession", e.target.checked ? "1" : "0");
              } catch {}
            }} />
            this session
          </label>
          ${onCollapse &&
          html`<button class="icon-btn" title="collapse feed (Ctrl+J)" onClick=${onCollapse}>›</button>`}
        </span>
      </div>
      <div class="feed-items" ref=${elRef} onScroll=${onFeedScroll}>
        ${shown.length === 0 && html`<div class="feed-empty">quiet</div>`}
        ${shown.map((i, idx) => html`<${FeedItem} key=${idx} i=${i} onJump=${onJump} />`)}
      </div>
    </aside>
  `;
}
