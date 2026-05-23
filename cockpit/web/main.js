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
import { isOwned, place, openOwned, openPeek, release } from "./fleet.js";
import { openTerm, Term, termForSid8, resumeTerm, ownedTermIds, liveTerms } from "./term.js";
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
  const [showFeed, setShowFeed] = useState(() => lsBool("cockpit-feed", true));
  const prevWaiting = useRef(new Set());
  const [, bumpNames] = useState(0);
  useEffect(() => subscribeNames(() => bumpNames((n) => n + 1)), []);

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
      .map((t) => ({
        sid8: t.sid8,
        session_id: t.sessionId,
        actor: t.label || "chat",
        instance: 1,
        state: "idle",
        age_sec: 0,
        idle_sec: 0,
        first_prompt: "",
        doing: "running in this cockpit",
        intent: "",
        attention: false,
        subagents: [],
        host: "cockpit",
        rank: 6,
      })),
  ];

  // ring once when a session newly needs you
  useEffect(() => {
    const now = new Set(sessions.filter((s) => s.attention).map((s) => s.sid8));
    if (soundOn) for (const id of now) if (!prevWaiting.current.has(id)) { beep(); break; }
    prevWaiting.current = now;
  }, [sessions, soundOn]);

  const toggleSound = () => setSoundOn((v) => { setLsBool("cockpit-sound", !v); return !v; });
  const toggleFeed = () => setShowFeed((v) => { setLsBool("cockpit-feed", !v); return !v; });

  const selectRow = (s) => {
    // a cockpit-launched terminal hosting this session wins; else headless/peek
    const t = termForSid8(s.sid8);
    const c = t || (isOwned(s.session_id) ? openOwned(s.session_id) : openPeek(s.session_id));
    c.label = s.actor + (s.instance > 1 ? "·" + s.instance : "");
    setSel(c);
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
      <${Board}
        sessions=${sessions}
        err=${err}
        selectedId=${sel && sel.id}
        onSelect=${selectRow}
        onNew=${() => setShowPlace(true)}
        soundOn=${soundOn}
        onToggleSound=${toggleSound}
        feedOn=${showFeed}
        onToggleFeed=${toggleFeed}
      />
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
      ${showFeed && html`<${FeedPanel} onJump=${jumpTo} />`}
      ${showPlace && html`<${PlaceModal} onPlace=${doPlace} onClose=${() => setShowPlace(false)} />`}
    </div>
  `;
}

render(html`<${App} />`, document.getElementById("app"));
