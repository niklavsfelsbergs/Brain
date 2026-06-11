// Cockpit shell — fleet board (left) + session console (right) + place modal.
// Phase 3: place (actor picker → composed address), re-task (click an owned
// idle/wrapped row → resume + type), release (terminate). Connections live in
// fleet.js, so sessions keep running when you switch away.

import { render } from "preact";
import { useState, useEffect, useRef } from "preact/hooks";
import { html } from "htm/preact";
import { Board } from "./board.js";
import { Console } from "./console.js";
import { FeedPanel } from "./feed.js";
import { openPeek, release } from "./fleet.js";
import { openTerm, Term, TermComposer, termForSid8, termInterrupted, termLastOutput, resumeTerm, handoffAndResume, ownedTermIds, liveTerms, applyTermZoom, fitTerms, reconnectTermsAfterWake } from "./term.js";
import { TranscriptView } from "./transcript.js";
import { nameFor, subscribeNames } from "./names.js";

// Actor → the address the cockpit writes as the first message. The actor
// implies the brain: Braindead enters the dev brain via the start phrase;
// everyone else routes in gielinor by address.
const ACTORS = [
  { key: "jebrim", label: "Jebrim", addr: "Hey Jebrim, " },
  { key: "zezima", label: "Zezima", addr: "Hey Zezima, " },
  { key: "guthix", label: "Guthix", addr: "Hey Guthix, " },
  { key: "unscoped", label: "unscoped", addr: "Hey unscoped, " },
  { key: "braindead", label: "Braindead · dev", addr: "Lets develop gielinor. " },
];

// D-029: two distinct pings. NEEDS YOU (mid-turn block) is urgent; YOUR MOVE
// (turn parked) is gentle. Both ride one shared oscillator helper.
let _ac;
function _tone(freq, startOffset, dur, peak) {
  _ac = _ac || new (window.AudioContext || window.webkitAudioContext)();
  if (_ac.state === "suspended") _ac.resume();
  const o = _ac.createOscillator();
  const g = _ac.createGain();
  o.connect(g);
  g.connect(_ac.destination);
  o.type = "sine";
  o.frequency.value = freq;
  const t = _ac.currentTime + startOffset;
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(peak, t + 0.01);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.start(t);
  o.stop(t + dur + 0.02);
}
// NEEDS YOU — urgent: two quick ascending notes.
function pingHot() {
  try {
    _tone(784, 0, 0.18, 0.18);
    _tone(1047, 0.16, 0.22, 0.18);
  } catch {}
}
// YOUR MOVE — gentle: a single soft low note.
function pingSoft() {
  try {
    _tone(523, 0, 0.4, 0.1);
  } catch {}
}
function lsBool(key, def) {
  const v = localStorage.getItem(key);
  return v === null ? def : v === "1";
}
function setLsBool(key, val) {
  try {
    localStorage.setItem(key, val ? "1" : "0");
  } catch {}
}

// ---- view knobs: UI zoom + side-pillar widths, all persisted ----
const ZMIN = 0.6, ZMAX = 2.2, ZSTEP = 0.1, ZDEF = 1.35;
const BOARD_DEF = 372, FEED_DEF = 340, PANE_MIN = 220, PANE_MAX = 760;
const ROOT = document.documentElement;
const setVar = (name, val) => ROOT.style.setProperty(name, val);
const cssZoom = () => parseFloat(getComputedStyle(ROOT).getPropertyValue("--zoom")) || ZDEF;
const clampZoom = (z) => Math.min(ZMAX, Math.max(ZMIN, Math.round(z * 100) / 100));
const clampPane = (px) => Math.min(PANE_MAX, Math.max(PANE_MIN, Math.round(px)));
function loadZoom() {
  const v = parseFloat(localStorage.getItem("cockpit-zoom"));
  return v >= ZMIN && v <= ZMAX ? v : ZDEF;
}
function loadPane(key, def) {
  const v = parseFloat(localStorage.getItem(key));
  return v >= PANE_MIN && v <= PANE_MAX ? v : def;
}

// A draggable divider between two pillars. `side` 'board' grows --board-w from the
// grid's left edge; 'feed' grows --feed-w from its right edge. clientX and the grid
// rect are both viewport px (the grid is sized to fill the viewport under `zoom`),
// so the rendered offset is divided by --zoom to get the layout-px width the CSS
// `width` property expects. Widths live in CSS vars + localStorage, not React state
// — no re-render needed mid-drag. onResized refits terminals once the layout settles.
function Resizer({ side, onResized }) {
  const isBoard = side === "board";
  const varName = isBoard ? "--board-w" : "--feed-w";
  const lsKey = isBoard ? "cockpit-board-w" : "cockpit-feed-w";
  const begin = (e) => {
    e.preventDefault();
    const grid = e.currentTarget.closest(".app-grid");
    if (!grid) return;
    const rect = grid.getBoundingClientRect();
    const z = cssZoom();
    const move = (ev) => {
      const px = isBoard ? (ev.clientX - rect.left) / z : (rect.right - ev.clientX) / z;
      setVar(varName, clampPane(px) + "px");
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      document.body.classList.remove("resizing");
      const cur = clampPane(parseFloat(getComputedStyle(ROOT).getPropertyValue(varName)));
      try { localStorage.setItem(lsKey, String(cur)); } catch {}
      onResized && onResized();
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    document.body.classList.add("resizing");
  };
  const reset = () => {
    const def = isBoard ? BOARD_DEF : FEED_DEF;
    setVar(varName, def + "px");
    try { localStorage.setItem(lsKey, String(def)); } catch {}
    onResized && onResized();
  };
  return html`<div
    class="gutter"
    onPointerDown=${begin}
    onDblClick=${reset}
    title="drag to resize · double-click to reset"
  ></div>`;
}

// Pick a name (optional), then click an actor to open it. No message box: the
// click places the session immediately and the actor's address ("Hey Jebrim, ")
// is prewritten into the PTY prompt — unsubmitted — so you just keep typing.
function PlaceModal({ onPlace, onClose }) {
  const [sessName, setSessName] = useState("");
  const place = (actor) => onPlace(actor, actor ? actor.addr : "", sessName.trim());
  return html`
    <div class="modal-backdrop" onClick=${onClose}>
      <div class="modal" onClick=${(e) => e.stopPropagation()}>
        <div class="modal-title">place a session</div>
        <label class="place-name">
          <span class="place-name-tag">name <span class="dim">· optional</span></span>
          <input
            type="text"
            value=${sessName}
            onInput=${(e) => setSessName(e.target.value)}
            placeholder="name this session…"
            autofocus
          />
        </label>
        <div class="place-hint">pick who to open — the address is prewritten in the terminal, you just continue typing.</div>
        <div class="actor-pick">
          ${ACTORS.map(
            (a) =>
              html`<button class="actor-opt" title=${"opens with: " + a.addr} onClick=${() => place(a)}>
                <span class="actor-label">${a.label}</span>
                <span class="actor-addr">${a.addr.trim()}</span>
              </button>`
          )}
          <button class="actor-opt plain" title="plain chat — no address prewritten" onClick=${() => place(null)}>
            <span class="actor-label">plain chat</span>
            <span class="actor-addr">no actor</span>
          </button>
        </div>
        <div class="modal-actions">
          <button class="ghost" onClick=${onClose}>cancel</button>
        </div>
      </div>
    </div>
  `;
}

function fmtAgo(ts) {
  if (!ts) return "";
  const s = Math.max(0, Math.floor(Date.now() / 1000 - ts));
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.floor(s / 60) + "m ago";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  return Math.floor(s / 86400) + "d ago";
}

// The restore list (S###). Every session on disk (~/.claude/projects), newest
// first, minus the ones already live on the board — reopening one resumes the
// conversation interactively (claude --resume). Sibling of PlaceModal: "+ new"
// places a fresh chat, this reopens a past one.
function HistoryModal({ liveSids, onReopen, onClose }) {
  const [items, setItems] = useState(null); // null = loading
  const [q, setQ] = useState("");
  useEffect(() => {
    let alive = true;
    fetch("/api/history")
      .then((r) => r.json())
      .then((j) => { if (alive) setItems(j.sessions || []); })
      .catch(() => { if (alive) setItems([]); });
    return () => { alive = false; };
  }, []);
  const ql = q.trim().toLowerCase();
  const rows = (items || [])
    .filter((s) => !liveSids.has(s.sid8)) // already on the board → not "history"
    .filter((s) => !ql || `${s.name} ${s.title} ${s.first_prompt}`.toLowerCase().includes(ql));
  return html`
    <div class="modal-backdrop" onClick=${onClose}>
      <div class="modal modal-history" onClick=${(e) => e.stopPropagation()}>
        <div class="modal-title">history — reopen a past chat</div>
        <input
          class="hist-filter"
          type="text"
          value=${q}
          autofocus
          placeholder="filter by name, title, or first message…"
          onInput=${(e) => setQ(e.target.value)}
        />
        <div class="hist-list">
          ${items === null
            ? html`<div class="hist-empty">loading…</div>`
            : rows.length === 0
            ? html`<div class="hist-empty">${ql ? "no match" : "no past sessions"}</div>`
            : rows.map(
                (s) => html`<button
                  class="hist-row"
                  key=${s.session_id}
                  title=${"resume " + s.sid8}
                  onClick=${() => onReopen(s)}
                >
                  <div class="hist-row-head">
                    <span class="hist-name">${s.name || s.title || s.sid8}</span>
                    <span class="hist-ago">${fmtAgo(s.last_active)}</span>
                  </div>
                  <div class="hist-sub">${(s.name && s.title) ? s.title : s.first_prompt}</div>
                </button>`
              )}
        </div>
        <div class="modal-actions">
          <button class="ghost" onClick=${onClose}>close</button>
        </div>
      </div>
    </div>
  `;
}

function App() {
  const [data, setData] = useState({ sessions: [] });
  const [err, setErr] = useState(null);
  const [sel, setSel] = useState(null);
  const [showPlace, setShowPlace] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [soundOn, setSoundOn] = useState(() => lsBool("cockpit-sound", true));
  const [feedOpen, setFeedOpen] = useState(() => lsBool("cockpit-feed", true));
  const [boardOpen, setBoardOpen] = useState(() => lsBool("cockpit-board", true));
  const [zoom, setZoom] = useState(loadZoom);
  // Driven-session view: the raw PTY terminal, or the clean-text transcript
  // (read/copy skin over the same session — S091). One global default, persisted.
  const [termView, setTermView] = useState(() =>
    localStorage.getItem("cockpit-term-view") === "transcript" ? "transcript" : "terminal",
  );
  const prevWaiting = useRef(new Map());   // sid8 -> last state, for ping transitions
  const [, bumpNames] = useState(0);
  useEffect(() => subscribeNames(() => bumpNames((n) => n + 1)), []);

  // refs so the once-bound keyboard handler reads fresh collapse state
  const boardRef = useRef(boardOpen); boardRef.current = boardOpen;
  const feedRef = useRef(feedOpen); feedRef.current = feedOpen;
  // refs for keyboard session-nav (Ctrl+↑/↓, Ctrl+1–9). The key handler binds
  // once on mount, so it reads the live fleet + selection + selectRow off refs
  // rather than the stale mount-time closures. Assigned each render below.
  const sessionsRef = useRef([]);
  const selSid8Ref = useRef(null);
  const selectRowRef = useRef(null);
  const refit = () => requestAnimationFrame(fitTerms);

  // apply persisted pillar widths once on mount (zoom is applied by its own effect)
  useEffect(() => {
    setVar("--board-w", loadPane("cockpit-board-w", BOARD_DEF) + "px");
    setVar("--feed-w", loadPane("cockpit-feed-w", FEED_DEF) + "px");
  }, []);

  // zoom → CSS var + persist + rescale terminal fonts
  useEffect(() => {
    setVar("--zoom", String(zoom));
    try { localStorage.setItem("cockpit-zoom", String(zoom)); } catch {}
    applyTermZoom();
  }, [zoom]);

  // persist collapse state; refit terminals when the console column resizes
  useEffect(() => { setLsBool("cockpit-board", boardOpen); }, [boardOpen]);
  useEffect(() => { setLsBool("cockpit-feed", feedOpen); }, [feedOpen]);
  useEffect(() => { const id = requestAnimationFrame(fitTerms); return () => cancelAnimationFrame(id); }, [boardOpen, feedOpen]);
  // persist the terminal/transcript choice; refit on return to the terminal — it
  // was display:none under the transcript, so its row count drifted while hidden.
  useEffect(() => {
    try { localStorage.setItem("cockpit-term-view", termView); } catch {}
    if (termView === "terminal") { const id = requestAnimationFrame(fitTerms); return () => cancelAnimationFrame(id); }
    return undefined;
  }, [termView]);

  const toggleFocus = () => {
    const anyOpen = boardRef.current || feedRef.current;
    setBoardOpen(!anyOpen);
    setFeedOpen(!anyOpen);
  };

  // Ctrl/Cmd + scroll = zoom; Ctrl/Cmd + = / - / 0 = zoom; Ctrl+B / Ctrl+J / Ctrl+\
  // = layout; Ctrl+↑/↓ = move the board selection (wraps); Ctrl+1–9 = jump to the
  // Nth session; Ctrl+Shift+` = new conversation. Capture phase + stopPropagation
  // so these never reach xterm (which would otherwise scroll, or send control bytes
  // to the PTY) or trigger WebView2 page zoom.
  useEffect(() => {
    const onWheel = (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      e.stopPropagation();
      setZoom((z) => clampZoom(z + (e.deltaY < 0 ? ZSTEP : -ZSTEP)));
    };
    // session-nav helpers read the live fleet/selection off refs (handler is
    // bound once). Keyboard selection never yanks VSCode forward (focusVscode:false).
    const navBy = (delta) => {
      const list = sessionsRef.current || [];
      const pick = selectRowRef.current;
      if (!list.length || !pick) return;
      let i = list.findIndex((s) => s.sid8 === selSid8Ref.current);
      if (i < 0) i = delta > 0 ? -1 : 0; // nothing selected → ↓ first, ↑ last
      pick(list[(i + delta + list.length) % list.length], { focusVscode: false });
    };
    const navTo = (n) => {
      const list = sessionsRef.current || [];
      const pick = selectRowRef.current;
      if (pick && n >= 1 && n <= list.length) pick(list[n - 1], { focusVscode: false });
    };
    const onKey = (e) => {
      if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
      const k = e.key;
      const hit = () => { e.preventDefault(); e.stopPropagation(); };
      if (k === "=" || k === "+") { hit(); setZoom((z) => clampZoom(z + ZSTEP)); }
      else if (k === "-" || k === "_") { hit(); setZoom((z) => clampZoom(z - ZSTEP)); }
      else if (k === "0") { hit(); setZoom(ZDEF); }
      else if (k === "b" || k === "B") { hit(); setBoardOpen((v) => !v); }
      else if (k === "j" || k === "J") { hit(); setFeedOpen((v) => !v); }
      else if (k === "\\") { hit(); toggleFocus(); }
      else if (k === "ArrowUp") { hit(); navBy(-1); }
      else if (k === "ArrowDown") { hit(); navBy(1); }
      // e.code is layout/shift-proof: Ctrl+Shift+1 reports key "!" but code "Digit1".
      else if (/^Digit[1-9]$/.test(e.code)) { hit(); navTo(Number(e.code.slice(5))); }
      else if (e.shiftKey && e.code === "Backquote") { hit(); setShowPlace(true); }
      else if (k === "h" || k === "H") { hit(); setShowHistory((v) => !v); }
    };
    window.addEventListener("wheel", onWheel, { passive: false, capture: true });
    window.addEventListener("keydown", onKey, true);
    return () => {
      window.removeEventListener("wheel", onWheel, { capture: true });
      window.removeEventListener("keydown", onKey, true);
    };
  }, []);
  // latest feed event per session — lets the board merge give cockpit-own
  // (unmanifested) terminals a real state instead of a hardcoded "idle".
  const [feedState, setFeedState] = useState({});

  // On cockpit open, resume owned terminals from disk (claude --resume) so
  // sessions survive a close/reopen or reload. They relaunch live and reappear
  // on the board; click a row to view. `release` is how you stop one returning.
  useEffect(() => {
    for (const uuid of ownedTermIds()) resumeTerm(uuid);
  }, []);

  // Resume cockpit terminals after the laptop wakes from sleep (S160/S161). On
  // sleep the PTY WebSockets drop and ptybridge terminates each claude (its
  // WS-close finally → proc.terminate), so terminals come back dead — you "can't
  // type in them" — and the resume-on-open effect above only runs at page LOAD,
  // never on wake. JS timers don't fire while the machine is suspended, so a large
  // gap between ticks is a reliable wake signal. On a detected wake we reconnect
  // the terminals that are IN MEMORY (reconnectTermsAfterWake — scoped to the live
  // map = what was actually open), NOT a page reload. The reload (S160's first cut)
  // wiped memory and let resume-on-open rebuild from the whole owned history, which
  // resurrected old/closed sessions as fresh "0s / YOUR MOVE" rows (S161 fix). In-
  // place reconnect resumes each open conversation (claude --resume) on its
  // existing pane; old owned sessions stay gone until a genuine reopen.
  useEffect(() => {
    const GAP_MS = 60000; // a >60s gap between ticks ≈ a sleep, not a timer hiccup
    const TICK_MS = 10000;
    let last = Date.now();
    const id = setInterval(() => {
      const now = Date.now();
      const gap = now - last;
      last = now;
      if (gap > GAP_MS) reconnectTermsAfterWake();
    }, TICK_MS);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let alive = true;
    async function poll() {
      try {
        const r = await fetch("/api/feed");
        const j = await r.json();
        if (!alive) return;
        const m = {};
        for (const it of j.items || [])
          if (it.sid8 && it.ts && (!m[it.sid8] || it.ts > m[it.sid8].ts))
            m[it.sid8] = { kind: it.kind, ts: it.ts, text: it.text || "" };
        setFeedState(m);
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
    let alive = true;
    async function poll() {
      try {
        const r = await fetch("/api/sessions");
        const j = await r.json();
        if (alive) {
          setData(j);
          setErr(null);
        }
      } catch (e) {
        if (alive) setErr(String(e));
      }
    }
    poll();
    const id = setInterval(poll, 2000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  // PTY-output liveness override (S188) for cockpit-driven rows. The cockpit owns
  // the terminal byte stream, so for its own sessions it has ground truth the
  // hook/heartbeat model lacks: claude emits output while it works and goes quiet at
  // the prompt. Recompute the STALLED/IDLE *liveness subs* from output recency
  // instead of the backend's frozen heartbeat. Fixes: a streaming turn never reads
  // STALLED (bug 3 — heartbeat freezes between tool completions); a parked turn's
  // IDLE clock counts from the LAST OUTPUT = the response ending (bug 2 — was
  // measured from a mid-turn event, so a long final answer went idle instantly).
  // No-op for sessions the cockpit doesn't drive (termLastOutput→0 → backend wins).
  // Touches only liveness (subs/stale/rank); the ball-state main chip is unchanged.
  const ptyLiveness = (s) => {
    const out = termLastOutput(s.sid8);
    if (!out) return s;
    const since = Math.floor((Date.now() - out) / 1000);
    const subs = (s.subs || []).filter((x) => x !== "idle" && x !== "stalled");
    if (s.state === "busy" && since > 900) subs.push("stalled"); // genuinely silent 15m+
    let idle = false;
    if (s.state === "your_move" && since > 300) { subs.push("idle"); idle = true; }
    let rank = s.rank;
    if (s.state === "your_move") rank = idle ? 7 : 1;
    else if (s.state === "busy") rank = 4;
    // Mirror the backend's attention rule (needs_you/your_move and not idle) against
    // the PTY-corrected idle, so an un-idled fresh-response row pulses + counts again.
    const attention = (s.main === "needs_you" || s.main === "your_move") && !idle;
    return { ...s, subs, tags: subs, stale: idle, quiet_sec: since,
             last_action_ts: Math.floor(out / 1000), attention, rank };
  };
  // Merge the hook manifest with the cockpit's own live terminals, so a session
  // the cockpit is running (e.g. a just-resumed, still-idle one) shows on the
  // board before it fires its first hook event. Manifest wins on dupes (richer).
  // The cockpit saw an Esc-cancel in this session's own terminal, but no hook
  // fires on interrupt so the manifest is stuck at busy. Clear it to idle at once
  // (the 90s backend decay is the backstop for non-cockpit/VSCode sessions).
  const manifest = (data.sessions || []).map((s) =>
    s.state === "busy" && termInterrupted(s.sid8)
      ? { ...s, state: "idle", attention: false, rank: 7 }
      : ptyLiveness(s),
  );
  const known = new Set(manifest.map((s) => s.sid8));
  const sessions = [
    ...manifest,
    ...liveTerms()
      .filter((t) => t.sid8 && !known.has(t.sid8))
      .map((t) => {
        // real state from the feed (D-029 tokens): needs_you → NEEDS YOU;
        // recent activity → busy; a close checkpoint or silence → idle.
        // No feed entry yet → idle.
        const fs = feedState[t.sid8];
        // Elapsed since this cockpit opened/resumed the terminal — the clock to
        // use when the session hasn't fired a feed event yet (a freshly-resumed,
        // still-idle one), so its age ticks up instead of freezing at "0s".
        const sinceOpen = t.openedAt
          ? Math.max(0, Math.floor((Date.now() - t.openedAt) / 1000))
          : 0;
        let state = "idle";
        if (fs) {
          const age = Date.now() / 1000 - fs.ts;
          if (fs.kind === "needs_you") state = "needs_you";
          else if (fs.kind === "done") state = "idle";
          else if (age < 120) state = "busy";
        }
        // An interrupt (Esc / Ctrl+C) cancels the turn with no hook to clear busy
        // — mirror the manifest override above so a cockpit-own row drops out of
        // BUSY too instead of staying stuck at it. (S164)
        const interrupted = termInterrupted(t.sid8);
        if (interrupted && state === "busy") state = "idle";
        // last action = the freshest feed event for this terminal (fs.ts). With no
        // feed event yet, anchor recency to when it opened here (not 0) so the age
        // chip shows a real "active Ns ago" instead of a frozen 0s and the row
        // doesn't tie at the top with everything else at ts 0. (S134 + jump-up fix)
        const quiet = fs ? Math.max(0, Math.floor(Date.now() / 1000 - fs.ts)) : sinceOpen;
        // A RESUMED session is parked-idle until the USER actually interacts with
        // it. Gate on userActive, NOT feed presence (S179): `claude --resume` fires
        // startup hook events that make the feed look active right after a restart,
        // which would otherwise flip a session that was IDLE at cockpit-close back
        // to YOUR MOVE / busy. Force idle here so resume-startup noise can't un-idle
        // it; it then sinks to rank 7 (below live work, dimmed) until the user drives
        // it. A fresh placement (isResume false) keeps its visible top slot. (Was
        // gated on `!fs`, which the resume's own startup events defeated — S164.)
        const resumedIdle = t.isResume && !t.userActive;
        if (resumedIdle) state = "idle";
        // S139 taxonomy: derive the main chip + sub-bubbles for this cockpit-own
        // row, matching the backend. needs_you → ACTION NEEDED; recent → BUSY; a
        // quiet/parked terminal → YOUR MOVE, with an `idle` sub once it's resumed-
        // idle or has sat past the 5-min window. (These transient rows join the
        // manifest on their first hook and get the backend's full treatment.)
        let main, subs = [];
        if (state === "needs_you") main = "needs_you";
        else if (state === "busy") main = "busy";
        else { main = "your_move"; if (resumedIdle || interrupted || quiet > 300) subs.push("idle"); }
        const cockpitIdle = subs.includes("idle");
        return {
          sid8: t.sid8,
          session_id: t.sessionId,
          actor: t.label || "chat",
          instance: 1,
          state,
          main,
          subs,
          tags: subs,
          age_sec: quiet,
          idle_sec: quiet,
          quiet_sec: quiet,
          last_action_ts: fs ? fs.ts : (t.openedAt ? Math.floor(t.openedAt / 1000) : 0),
          first_prompt: "",
          doing: fs && fs.text ? fs.text : "running in this cockpit",
          intent: "",
          attention: main === "needs_you",
          subagents: [],
          host: "cockpit",
          stale: cockpitIdle,
          rank: state === "needs_you" ? 0 : state === "busy" ? 4 : (cockpitIdle ? 7 : 1),
        };
      }),
  ];
  // Re-sort the MERGED list (manifest rows are pre-sorted by the backend, but the
  // cockpit-own rows are appended after — without this they'd pin to the bottom
  // regardless of state/activity). One axis, matching the backend: attention rank
  // first, then most-recently-active on top (last_action_ts desc), age as the
  // stable tiebreaker. (S134)
  sessions.sort(
    (a, b) =>
      (a.rank ?? 99) - (b.rank ?? 99) ||
      (b.last_action_ts || 0) - (a.last_action_ts || 0) ||
      (a.age_sec || 0) - (b.age_sec || 0),
  );

  // D-029: two distinct pings, fired on a session's *transition* into an
  // attention state. needs_you (hot) takes priority over your_move (soft) when
  // both land in the same poll, so a fleet update is one sound, not a chord.
  useEffect(() => {
    let hot = false;
    let soft = false;
    const cur = new Map();
    for (const s of sessions) {
      cur.set(s.sid8, s.state);
      if (s.state !== prevWaiting.current.get(s.sid8)) {
        if (s.state === "needs_you") hot = true;
        else if (s.state === "your_move") soft = true;
      }
    }
    if (soundOn) {
      if (hot) pingHot();
      else if (soft) pingSoft();
    }
    prevWaiting.current = cur;
  }, [sessions, soundOn]);

  // Re-pin the live terminal when the view flips back to it. A row selected while
  // the transcript view was up mounted display:none (0-height frame), so its
  // <Term> open pin loop bailed (fitNow guards a 0-box) and never fit/pinned;
  // without this, flipping to terminal leaves the prompt below the fold until a
  // keystroke (S095 term-fit-diag: opens logged frameH=0, recovery only on
  // keydown). reshow() waits out the show, then fits + pins across several frames.
  useEffect(() => {
    if (termView === "terminal" && sel && sel.kind === "term" && typeof sel.reshow === "function") {
      sel.reshow();
    }
  }, [termView, sel]);

  const toggleSound = () => setSoundOn((v) => { setLsBool("cockpit-sound", !v); return !v; });
  const toggleFeed = () => setFeedOpen((v) => !v);
  const zoomIn = () => setZoom((z) => clampZoom(z + ZSTEP));
  const zoomOut = () => setZoom((z) => clampZoom(z - ZSTEP));
  const zoomReset = () => setZoom(ZDEF);

  const selectRow = (s, { focusVscode = true } = {}) => {
    // VSCode-hosted sessions: focus their terminal pane in VSCode (S073). The
    // claude-focus extension matches sid8 → claude_pid_chain → the pane and
    // show()s it. Still falls through to a read-only peek so the cockpit keeps
    // a selection + transcript view. Skipped on keyboard-nav (focusVscode:false)
    // so arrowing across a vscode row doesn't repeatedly steal window focus.
    if (focusVscode && s.host === "vscode") {
      fetch("/api/open-vscode?sid8=" + encodeURIComponent(s.sid8)).catch(() => {});
    }
    // a cockpit-launched terminal hosting this session wins; else a read-only peek
    const t = termForSid8(s.sid8);
    const c = t || openPeek(s.session_id);
    if (!t) {
      // Carry host + the full session uuid onto the peek so the console can offer
      // a handoff ("drive here") for a cockpit session driven on another client.
      c.host = s.host;
      c.sessionId = s.session_id;
    }
    const label = nameFor(s.sid8) || s.name; // match the board's rename (S073)
    c.label = label || s.actor + (s.instance > 1 ? "·" + s.instance : "");
    setSel(c);
  };
  // Rename from the board (double-click a row name). Writes the same disk store
  // the /rename hook uses (POST /api/rename); optimistically patch the local
  // model so the new label shows immediately rather than on the next 2s poll.
  // Empty name clears the rename back to the bare actor label.
  const renameSession = (sid8, name) => {
    setData((d) => ({
      ...d,
      sessions: (d.sessions || []).map((s) => (s.sid8 === sid8 ? { ...s, name } : s)),
    }));
    fetch("/api/rename", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ sid8, name }),
    }).catch(() => {});
  };
  const doPlace = (actor, seed, name) => {
    // submit:false — the address (seed) is prewritten into the prompt unsubmitted,
    // so the user continues typing rather than firing a bare "Hey Jebrim,".
    const c = openTerm(seed, { submit: false }); // S066 B: real interactive claude in a PTY (on-subscription)
    c.label = name || (actor ? actor.label : "chat");
    c.placedName = name || ""; // a user-chosen name becomes the board row name once the sid8 lands
    setSel(c);
    setShowPlace(false);
  };
  // Reopen a past chat from history: if a cockpit terminal already hosts it just
  // select that; otherwise claude --resume into a fresh driven terminal (the same
  // path owned-resume uses, so it re-owns + survives the next cockpit reopen). It
  // reappears on the board as a live row and claims the lowest-free slot number.
  const doReopen = (s) => {
    const c = termForSid8(s.sid8) || resumeTerm(s.session_id);
    c.label = s.name || s.title || "chat";
    setSel(c);
    setShowHistory(false);
  };
  const doRelease = (id) => {
    release(id);
    if (sel && sel.id === id) setSel(null);
  };
  // Adopt a cockpit session driven on another client: terminate its PTY there,
  // then resume the conversation here in a fresh driven terminal. Safe by
  // construction (kill-then-resume — one claude per transcript); handoffAndResume
  // returns null if no live cockpit PTY drove it, so we never double-write.
  const doAdopt = async (conn) => {
    const c = await handoffAndResume(conn.sessionId || conn.id);
    if (c) {
      c.label = conn.label;
      setSel(c);
    }
  };
  const jumpTo = (sid8) => {
    const s = sessions.find((x) => x.sid8 === sid8);
    if (s) selectRow(s);
    else {
      const c = openPeek(sid8); // ended/off-board: /history accepts a sid8
      c.label = sid8;
      setSel(c);
    }
  };

  const title = sel
    ? nameFor(sel.id) || sel.label || (sel.id ? sel.id.slice(0, 8) : "new conversation")
    : "";

  // The open session's sid8, robust across both connection kinds: a PTY term's
  // .id is already the sid8; a peek's .id is the full session_id. slice(0,8) of
  // either yields the sid8 the board rows carry. (Fixes the never-matching
  // s.session_id === sel.id compare that left PTY rows unhighlighted.)
  const selSid8 = sel && sel.id ? sel.id.slice(0, 8) : null;
  // keep the once-bound key handler's refs current
  sessionsRef.current = sessions;
  selSid8Ref.current = selSid8;
  selectRowRef.current = selectRow;

  return html`
    <div class="app-grid">
      ${boardOpen
        ? html`<${Board}
              sessions=${sessions}
              err=${err}
              selectedSid8=${selSid8}
              onSelect=${selectRow}
              onNew=${() => setShowPlace(true)}
              onHistory=${() => setShowHistory(true)}
              onRename=${renameSession}
              soundOn=${soundOn}
              onToggleSound=${toggleSound}
              feedOn=${feedOpen}
              onToggleFeed=${toggleFeed}
              zoom=${zoom}
              onZoomIn=${zoomIn}
              onZoomOut=${zoomOut}
              onZoomReset=${zoomReset}
              onCollapseBoard=${() => setBoardOpen(false)}
              onToggleFocus=${toggleFocus}
              focused=${!boardOpen && !feedOpen}
            />
            <${Resizer} side="board" onResized=${refit} />`
        : html`<div class="rail rail-left" onClick=${() => setBoardOpen(true)} title="show board (Ctrl+B)">
            <button title="show board (Ctrl+B)" onClick=${(e) => { e.stopPropagation(); setBoardOpen(true); }}>›</button>
            <button title="new conversation" onClick=${(e) => { e.stopPropagation(); setShowPlace(true); }}>+</button>
          </div>`}
      <div class="console-col">
        ${!sel
          ? html`<div class="console-empty">select a session, or place a new one</div>`
          : sel.kind === "term"
          ? html`<div class=${"term-col" + (termView === "transcript" ? " reading" : "")} style="display:flex;flex-direction:column;height:100%;">
              <div class="console-head">
                <span class="console-title">${title}</span>
                ${/* subtitle dropped (S134) — the terminal/transcript toggle to the
                      right already says which mode this is; "· on subscription" was
                      redundant chrome. */ ""}
                <div class="console-head-right">
                  <div class="tv-toggle">
                    <button
                      class=${"tv-tab" + (termView === "terminal" ? " on" : "")}
                      onClick=${() => setTermView("terminal")}
                      title="drive the live PTY (interactive)"
                    >terminal</button>
                    <button
                      class=${"tv-tab" + (termView === "transcript" ? " on" : "")}
                      onClick=${() => setTermView("transcript")}
                      title="clean, copyable text of this same session"
                    >transcript</button>
                  </div>
                  <button class="release" title="end this session" onClick=${() => {
                    sel.close();
                    setSel(null);
                  }}>release</button>
                </div>
              </div>
              ${/* Term stays mounted across the toggle (hidden, not unmounted) so
                    the PTY/WebSocket never drops; the transcript view mounts over
                    it and reads the same session via /history. (S091) */ ""}
              <div style=${"flex:1;min-height:0;" + (termView === "transcript" ? "display:none;" : "")}>
                <${Term} key=${sel.cid} conn=${sel} />
              </div>
              ${termView === "transcript" &&
              html`<${TranscriptView} key=${sel.cid + "-tv"} conn=${sel} live=${true} />`}
              <${TermComposer} key=${sel.cid + "-c"} conn=${sel} />
            </div>`
          : html`<${Console} key=${sel.cid} conn=${sel} title=${title} onRelease=${doRelease} onAdopt=${doAdopt} />`}
      </div>
      ${feedOpen
        ? html`<${Resizer} side="feed" onResized=${refit} />
            <${FeedPanel} onJump=${jumpTo} onCollapse=${() => setFeedOpen(false)} selSid8=${selSid8} />`
        : html`<div class="rail rail-right" onClick=${() => setFeedOpen(true)} title="show feed (Ctrl+J)">
            <button title="show feed (Ctrl+J)" onClick=${(e) => { e.stopPropagation(); setFeedOpen(true); }}>‹</button>
          </div>`}
      ${showPlace && html`<${PlaceModal} onPlace=${doPlace} onClose=${() => setShowPlace(false)} />`}
      ${showHistory && html`<${HistoryModal}
          liveSids=${new Set(sessions.map((x) => x.sid8))}
          onReopen=${doReopen}
          onClose=${() => setShowHistory(false)}
        />`}
    </div>
  `;
}

render(html`<${App} />`, document.getElementById("app"));
