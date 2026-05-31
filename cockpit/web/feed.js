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

// BRAIN ↔ FEED vertical split (S136). The brain dock's height lives in the
// --brain-h CSS var (styles.css; persisted to localStorage); this gutter
// rewrites it on drag. Mirrors the horizontal Resizer in main.js — the feed-col
// is zoomed, so the rendered offset is divided by --zoom to get the layout-px
// height the dock's CSS `height` expects.
const BRAIN_MIN = 130, BRAIN_MAX = 820, BRAIN_DEF = 300;
const clampBrain = (px) => Math.max(BRAIN_MIN, Math.min(BRAIN_MAX, px));
const cssNum = (name, fb) =>
  parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name)) || fb;
function setBrainH(px) {
  document.documentElement.style.setProperty("--brain-h", px + "px");
}
function beginBrainDrag(e) {
  e.preventDefault();
  const dock = e.currentTarget.previousElementSibling; // .brain-dock
  if (!dock) return;
  const z = cssNum("--zoom", 1);
  const top = dock.getBoundingClientRect().top;
  const move = (ev) => setBrainH(clampBrain((ev.clientY - top) / z));
  const up = () => {
    window.removeEventListener("pointermove", move);
    window.removeEventListener("pointerup", up);
    document.body.classList.remove("brain-resizing");
    try { localStorage.setItem("cockpit-brain-h", String(clampBrain(cssNum("--brain-h", BRAIN_DEF)))); } catch {}
  };
  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", up);
  document.body.classList.add("brain-resizing");
}
function resetBrainH() {
  setBrainH(BRAIN_DEF);
  try { localStorage.setItem("cockpit-brain-h", String(BRAIN_DEF)); } catch {}
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
  // The four view toggles live behind a "filters ▾" menu now (S136) — the four
  // native checkboxes crowded the narrow header and were off-theme. Open state +
  // an outside-click close below.
  const [filtersOpen, setFiltersOpen] = useState(false);
  const filtersRef = useRef(null);
  const elRef = useRef(null);
  const innerRef = useRef(null);
  // Stick to the bottom until the user scrolls up. Starts true so the first
  // load lands at the newest item. (S132)
  const pinned = useRef(true);
  const brainRef = useRef(null);
  const [, bump] = useState(0);
  useEffect(() => subscribeNames(() => bump((n) => n + 1)), []); // re-render on rename
  // close the filters menu on any click outside it
  useEffect(() => {
    if (!filtersOpen) return;
    function onDoc(e) {
      if (filtersRef.current && !filtersRef.current.contains(e.target)) setFiltersOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [filtersOpen]);
  // the brain graph — a square docked at the top of the feed column. Mounted
  // imperatively (vanilla canvas) into a stable ref'd div, once; torn down on
  // unmount (feed collapse). The div carries no Preact children, so the 2s feed
  // re-render never disturbs the canvas underneath it.
  useEffect(() => (brainRef.current ? mountBrain(brainRef.current) : undefined), []);
  // restore the persisted brain/feed split on mount (S136)
  useEffect(() => {
    const v = parseFloat(localStorage.getItem("cockpit-brain-h"));
    if (v) setBrainH(clampBrain(v));
  }, []);

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

  // The render-effect above snaps once, synchronously after commit — but the
  // content's final height isn't always settled then (a tall comms block, a late
  // font swap, or wrapped prose reflows a frame later), so the snap occasionally
  // lands short and the feed "doesn't stick." A ResizeObserver on the inner
  // content re-snaps whenever the real content height changes, regardless of
  // render timing — the robust catch for that race. Only when pinned, so it
  // never yanks the view while you're scrolled up reading. (S136)
  useEffect(() => {
    const el = elRef.current, inner = innerRef.current;
    if (!el || !inner || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => {
      if (pinned.current) el.scrollTop = el.scrollHeight;
    });
    ro.observe(inner);
    return () => ro.disconnect();
  }, []);

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
      <div
        class="brain-gutter"
        onPointerDown=${beginBrainDrag}
        onDblClick=${resetBrainH}
        title="drag to resize brain / feed · double-click to reset"
      ></div>
      <div class="feed-head">
        <span>FEED</span>
        <span class="feed-head-right">
          <div class="feed-filters" ref=${filtersRef}>
            <button
              class=${"icon-btn feed-filters-btn" + (filtersOpen ? " on" : "")}
              title="feed filters"
              onClick=${() => setFiltersOpen((v) => !v)}
            >filters ▾</button>
            ${filtersOpen &&
            html`<div class="feed-filters-menu">
              <label class="feed-filter-row">
                <input type="checkbox" checked=${showActions} onChange=${(e) => {
                  setShowActions(e.target.checked);
                  try {
                    localStorage.setItem("cockpit-feed-actions", e.target.checked ? "1" : "0");
                  } catch {}
                }} />
                actions
              </label>
              <label class="feed-filter-row">
                <input type="checkbox" checked=${showSay} onChange=${(e) => {
                  setShowSay(e.target.checked);
                  try {
                    localStorage.setItem("cockpit-feed-say", e.target.checked ? "1" : "0");
                  } catch {}
                }} />
                prose
              </label>
              <label class="feed-filter-row" title="show the model's reasoning blocks (verbose)">
                <input type="checkbox" checked=${showThink} onChange=${(e) => {
                  setShowThink(e.target.checked);
                  try {
                    localStorage.setItem("cockpit-feed-think", e.target.checked ? "1" : "0");
                  } catch {}
                }} />
                thinking
              </label>
              <label class="feed-filter-row" title="only the board-selected session (vs the whole fleet)">
                <input type="checkbox" checked=${thisSession} onChange=${(e) => {
                  setThisSession(e.target.checked);
                  try {
                    localStorage.setItem("cockpit-feed-thissession", e.target.checked ? "1" : "0");
                  } catch {}
                }} />
                this session
              </label>
            </div>`}
          </div>
          ${onCollapse &&
          html`<button class="icon-btn" title="collapse feed (Ctrl+J)" onClick=${onCollapse}>›</button>`}
        </span>
      </div>
      <div class="feed-items" ref=${elRef} onScroll=${onFeedScroll}>
        <div class="feed-items-inner" ref=${innerRef}>
          ${shown.length === 0 && html`<div class="feed-empty">quiet</div>`}
          ${shown.map((i, idx) => html`<${FeedItem} key=${idx} i=${i} onJump=${onJump} />`)}
        </div>
      </div>
    </aside>
  `;
}
