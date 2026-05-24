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
import { openTerm, Term, termForSid8, resumeTerm, ownedTermIds, liveTerms, applyTermZoom, fitTerms } from "./term.js";
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

let _ac;
function beep() {
  try {
    _ac = _ac || new (window.AudioContext || window.webkitAudioContext)();
    if (_ac.state === "suspended") _ac.resume();
    const o = _ac.createOscillator();
    const g = _ac.createGain();
    o.connect(g);
    g.connect(_ac.destination);
    o.type = "sine";
    o.frequency.value = 660;
    const t = _ac.currentTime;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.16, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
    o.start(t);
    o.stop(t + 0.36);
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

function PlaceModal({ onPlace, onClose }) {
  const [actor, setActor] = useState(null); // null = plain chat, no player address
  const [prompt, setPrompt] = useState("");
  const submit = () => {
    const p = prompt.trim();
    if (p) onPlace(actor, actor ? actor.addr + p : p);
  };
  return html`
    <div class="modal-backdrop" onClick=${onClose}>
      <div class="modal" onClick=${(e) => e.stopPropagation()}>
        <div class="modal-title">place a session</div>
        <div class="actor-pick">
          ${ACTORS.map(
            (a) =>
              html`<button
                class=${"actor-opt" + (actor && a.key === actor.key ? " on" : "")}
                onClick=${() => setActor(actor && a.key === actor.key ? null : a)}
              >
                ${a.label}
              </button>`
          )}
        </div>
        <textarea
          class="place-prompt"
          value=${prompt}
          onInput=${(e) => setPrompt(e.target.value)}
          placeholder=${(actor ? "first message to " + actor.label : "message — plain chat, no player") + "…"}
          onKeyDown=${(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        ></textarea>
        <div class="modal-preview">${actor ? actor.addr : ""}<span class="dim">${
          prompt || (actor ? "…" : "plain chat — no player selected")
        }</span></div>
        <div class="modal-actions">
          <button class="ghost" onClick=${onClose}>cancel</button>
          <button class="primary" onClick=${submit}>place</button>
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
  const [soundOn, setSoundOn] = useState(() => lsBool("cockpit-sound", true));
  const [feedOpen, setFeedOpen] = useState(() => lsBool("cockpit-feed", true));
  const [boardOpen, setBoardOpen] = useState(() => lsBool("cockpit-board", true));
  const [zoom, setZoom] = useState(loadZoom);
  const prevWaiting = useRef(new Set());
  const [, bumpNames] = useState(0);
  useEffect(() => subscribeNames(() => bumpNames((n) => n + 1)), []);

  // refs so the once-bound keyboard handler reads fresh collapse state
  const boardRef = useRef(boardOpen); boardRef.current = boardOpen;
  const feedRef = useRef(feedOpen); feedRef.current = feedOpen;
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

  const toggleFocus = () => {
    const anyOpen = boardRef.current || feedRef.current;
    setBoardOpen(!anyOpen);
    setFeedOpen(!anyOpen);
  };

  // Ctrl/Cmd + scroll = zoom; Ctrl/Cmd + = / - / 0 = zoom; Ctrl+B / Ctrl+J / Ctrl+\
  // = layout. Capture phase + stopPropagation so these never reach xterm (which
  // would otherwise scroll, or send ^B/^J to the PTY) or trigger WebView2 page zoom.
  useEffect(() => {
    const onWheel = (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      e.stopPropagation();
      setZoom((z) => clampZoom(z + (e.deltaY < 0 ? ZSTEP : -ZSTEP)));
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

  // Merge the hook manifest with the cockpit's own live terminals, so a session
  // the cockpit is running (e.g. a just-resumed, still-idle one) shows on the
  // board before it fires its first hook event. Manifest wins on dupes (richer).
  const manifest = data.sessions || [];
  const known = new Set(manifest.map((s) => s.sid8));
  const sessions = [
    ...manifest,
    ...liveTerms()
      .filter((t) => t.sid8 && !known.has(t.sid8))
      .map((t) => {
        // real state from the feed: recent activity → working; needs_you → waiting;
        // a close checkpoint or silence → idle. No feed entry yet → idle.
        const fs = feedState[t.sid8];
        let state = "idle";
        if (fs) {
          const age = Date.now() / 1000 - fs.ts;
          if (fs.kind === "needs_you") state = "waiting_for_user";
          else if (fs.kind === "done") state = "idle";
          else if (age < 120) state = "working";
        }
        return {
          sid8: t.sid8,
          session_id: t.sessionId,
          actor: t.label || "chat",
          instance: 1,
          state,
          age_sec: 0,
          idle_sec: fs ? Math.max(0, Math.floor(Date.now() / 1000 - fs.ts)) : 0,
          first_prompt: "",
          doing: fs && fs.text ? fs.text : "running in this cockpit",
          intent: "",
          attention: state === "waiting_for_user",
          subagents: [],
          host: "cockpit",
          rank: 6,
        };
      }),
  ];

  // ring once when a session newly needs you
  useEffect(() => {
    const now = new Set(sessions.filter((s) => s.attention).map((s) => s.sid8));
    if (soundOn) for (const id of now) if (!prevWaiting.current.has(id)) { beep(); break; }
    prevWaiting.current = now;
  }, [sessions, soundOn]);

  const toggleSound = () => setSoundOn((v) => { setLsBool("cockpit-sound", !v); return !v; });
  const toggleFeed = () => setFeedOpen((v) => !v);
  const zoomIn = () => setZoom((z) => clampZoom(z + ZSTEP));
  const zoomOut = () => setZoom((z) => clampZoom(z - ZSTEP));
  const zoomReset = () => setZoom(ZDEF);

  const selectRow = (s) => {
    // VSCode-hosted sessions: focus their terminal pane in VSCode (S073). The
    // claude-focus extension matches sid8 → claude_pid_chain → the pane and
    // show()s it. Still falls through to a read-only peek so the cockpit keeps
    // a selection + transcript view.
    if (s.host === "vscode") {
      fetch("/api/open-vscode?sid8=" + encodeURIComponent(s.sid8)).catch(() => {});
    }
    // a cockpit-launched terminal hosting this session wins; else a read-only peek
    const t = termForSid8(s.sid8);
    const c = t || openPeek(s.session_id);
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
  const doPlace = (actor, seed) => {
    const c = openTerm(seed); // S066 B: real interactive claude in a PTY (on-subscription)
    c.label = actor ? actor.label : "chat";
    setSel(c);
    setShowPlace(false);
  };
  const doRelease = (id) => {
    release(id);
    if (sel && sel.id === id) setSel(null);
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

  return html`
    <div class="app-grid">
      ${boardOpen
        ? html`<${Board}
              sessions=${sessions}
              err=${err}
              selectedId=${sel && sel.id}
              onSelect=${selectRow}
              onNew=${() => setShowPlace(true)}
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
          ? html`<div class="term-col" style="display:flex;flex-direction:column;height:100%;">
              <div class="console-head">
                <span class="console-title">${title}</span>
                <span class="console-status">terminal · on subscription</span>
                <button class="release" title="end this session" onClick=${() => {
                  sel.close();
                  setSel(null);
                }}>release</button>
              </div>
              <div style="flex:1;min-height:0;"><${Term} key=${sel.cid} conn=${sel} /></div>
            </div>`
          : html`<${Console} key=${sel.cid} conn=${sel} title=${title} onRelease=${doRelease} />`}
      </div>
      ${feedOpen
        ? html`<${Resizer} side="feed" onResized=${refit} />
            <${FeedPanel} onJump=${jumpTo} onCollapse=${() => setFeedOpen(false)} />`
        : html`<div class="rail rail-right" onClick=${() => setFeedOpen(true)} title="show feed (Ctrl+J)">
            <button title="show feed (Ctrl+J)" onClick=${(e) => { e.stopPropagation(); setFeedOpen(true); }}>‹</button>
          </div>`}
      ${showPlace && html`<${PlaceModal} onPlace=${doPlace} onClose=${() => setShowPlace(false)} />`}
    </div>
  `;
}

render(html`<${App} />`, document.getElementById("app"));
