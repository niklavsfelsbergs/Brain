// transcript.js — the clean-text transcript panel (S091). A driven PTY session
// (term.js) renders as a real terminal, and copying out of it is horrible:
// xterm is a fixed-width character grid, so long lines are hard-wrapped at the
// column width and TUI chrome is baked into the cells — select-and-copy gives
// you the chopped, mangled form. This panel renders the SAME session's on-disk
// transcript (/history, parsed from the .jsonl — no ANSI, no wrapping) as clean
// DOM, and its copy buttons hand the RAW source text to the clipboard. The PTY
// stays the engine underneath (subscription, interactive); this is purely a
// read/copy skin over it. The toggle lives in main.js, which keeps <Term/>
// mounted (hidden) so flipping views never drops the live session.
//
// S093 readability pass (principal: "not very well designed"): it was a flat
// document — no turn boundaries, raw tool dumps crowding out the conversation,
// hierarchy inverted. Now: tool calls collapse by default (#1), turns carry a
// speaker header + divider (#2), prose caps at a readable measure (#3, CSS),
// the redundant hint is gone (#5), code/tool styling is unified + an optional
// line-number strip (#6), and an A−/A+ font control (#7).

import { useEffect, useRef, useState } from "preact/hooks";
import { html } from "htm/preact";
import { mdToHtml } from "./md.js";

// Clipboard write through the backend bridge — the WebView2-safe path term.js
// already uses for Ctrl+C (navigator.clipboard.writeText is permission-gated in
// the webview; the server is on 127.0.0.1 so its clipboard IS the user's). The
// navigator path is the fallback for a plain browser pointed at a remote server.
// Best-effort: returns true/false, never throws into the click handler.
export async function copyText(text) {
  if (!text) return false;
  try {
    const r = await fetch("/api/clipboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (r.ok && (await r.json()).ok) return true;
  } catch {}
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {}
  return false;
}

// True while the user has a live (non-collapsed) text selection anchored inside
// `el`. Used to make the 2s poll yield: don't re-render content out from under a
// drag-select. anchorNode can be a text node, so climb to its element to test.
function _selectionInside(el) {
  if (!el) return false;
  const sel = window.getSelection && window.getSelection();
  if (!sel || sel.isCollapsed || !sel.rangeCount) return false;
  let n = sel.anchorNode;
  if (n && n.nodeType === 3) n = n.parentNode;
  return !!(n && el.contains(n));
}

// Read renders file content as `cat -n` — a right-aligned line number + a tab
// per line. Handy on screen, noise in a paste. When the strip toggle is on, drop
// that prefix (both the on-screen <pre> and what the copy buttons grab).
// Conservative: only the `<spaces><digits><tab>` shape Read uses, so bash output
// and grep's `n:line` form pass through untouched.
function stripNums(text, on) {
  if (text == null) return "";
  const s = String(text);
  return on ? s.replace(/^[ \t]*\d+\t/gm, "") : s;
}

// Font-size control (#7): one persisted scale multiplied into the scoped CSS
// font sizes via the --tv-scale custom property on the panel root.
const SMIN = 0.8, SMAX = 1.7, SSTEP = 0.1;
const clampScale = (s) => Math.min(SMAX, Math.max(SMIN, Math.round(s * 100) / 100));
function loadScale() {
  const v = parseFloat(localStorage.getItem("cockpit-tv-font"));
  return v >= SMIN && v <= SMAX ? v : 1;
}

// Copy control. Icon-only by default (#3) — the per-tool and per-turn copies
// repeat enough that a text label on each was visual noise; the glyph stays out
// of the way and reveals on row-hover (CSS). `showText` keeps a labelled button
// for the single "copy all" in the bar, where one prominent control is fine.
// The clipboard glyph briefly swaps to a check/cross for feedback either way.
function CopyBtn({ get, label = "copy", showText = false }) {
  const [done, setDone] = useState(0); // 0 idle · 1 ok · -1 fail
  const onClick = async (e) => {
    e.stopPropagation();
    const ok = await copyText(get());
    setDone(ok ? 1 : -1);
    setTimeout(() => setDone(0), 1200);
  };
  const glyph = done === 1 ? "✓" : done === -1 ? "✕" : "⧉";
  const cls = "copy-btn " + (showText ? "has-text" : "icon-only") + (done ? " done" : "");
  return html`<button class=${cls} onClick=${onClick} title=${label} aria-label=${label}>
    <span class="copy-ic">${glyph}</span>${showText && html`<span class="copy-lbl">${done === 1 ? "copied" : label}</span>`}
  </button>`;
}

function toolSummary(input) {
  if (!input || typeof input !== "object") return "";
  if (input.command) return String(input.command).split("\n")[0].slice(0, 90);
  if (input.file_path) return tail(input.file_path);
  if (input.path) return tail(input.path);
  if (input.pattern) return String(input.pattern).slice(0, 90);
  if (input.query) return String(input.query).slice(0, 90);
  const k = Object.keys(input)[0];
  return k ? `${k}: ${String(input[k]).slice(0, 70)}` : "";
}
function tail(p) {
  return String(p).split(/[\\/]/).slice(-2).join("/");
}

// Flatten a turn to plain, copyable text — raw source, no markup. This is what
// the copy buttons grab; the DOM render is only for reading. `strip` honours the
// line-number toggle so a copied turn matches what's on screen.
function turnText(turn, strip) {
  if (turn.role === "user") return (turn.blocks || []).map((b) => b.text || "").join("\n");
  const parts = [];
  for (const b of turn.blocks || []) {
    if (b.t === "text") parts.push(b.text || "");
    else if (b.t === "thinking") parts.push("[thinking]\n" + (b.text || ""));
    else if (b.t === "tool") {
      parts.push(`[${b.name} ${toolSummary(b.input)}]`.trim());
      if (b.result != null) parts.push(stripNums(b.result, strip));
    }
  }
  return parts.filter(Boolean).join("\n");
}
function allText(turns, strip) {
  return (turns || [])
    .map((t) => (t.role === "user" ? "You:\n" : "") + turnText(t, strip))
    .filter((s) => s.trim())
    .join("\n\n———\n\n");
}

// A tool call. Collapsed by default (#1) — the head row alone (name + arg + line
// count + copy) so file reads and git dumps don't bury the conversation. Click
// the head to expand the output; errors open themselves so failures aren't
// hidden. Copy works without expanding.
function ToolBlock({ b, strip }) {
  const hasResult = b.result != null;
  const [open, setOpen] = useState(!!b.isError);
  const lineN = hasResult ? String(b.result).split("\n").length : 0;
  return html`<div class=${"b-tool" + (b.isError ? " err" : "") + (open ? " open" : "")}>
    <div
      class=${"tool-head" + (hasResult ? " clickable" : "")}
      onClick=${hasResult ? () => setOpen((o) => !o) : undefined}
    >
      ${hasResult && html`<span class="tool-chev">${open ? "▾" : "▸"}</span>`}
      <span class="tool-name">${b.name}</span>
      <span class="tool-arg">${toolSummary(b.input)}</span>
      ${hasResult && !open && html`<span class="tool-meta">${lineN} line${lineN === 1 ? "" : "s"}</span>`}
      ${hasResult && html`<${CopyBtn} get=${() => stripNums(b.result, strip)} label="copy output" />`}
    </div>
    ${open && hasResult && html`<pre class="tv-result">${stripNums(b.result, strip)}</pre>`}
  </div>`;
}

function Block({ b, strip }) {
  if (b.t === "text")
    return html`<div class="b-text" dangerouslySetInnerHTML=${{ __html: mdToHtml(b.text) }}></div>`;
  if (b.t === "thinking")
    return html`<details class="b-think">
      <summary>thinking</summary>
      <div dangerouslySetInnerHTML=${{ __html: mdToHtml(b.text) }}></div>
    </details>`;
  if (b.t === "tool") return html`<${ToolBlock} b=${b} strip=${strip} />`;
  return null;
}

// One turn, with a speaker header so the back-and-forth is legible (#2). Both
// sides get a speech bubble (principal ask): the user a compact right-aligned
// bubble, the agent a WIDE left-aligned one — the modern LLM-chat asymmetry
// (assistant content is rich/long so it gets the width; the user stays small).
// The agent's label sits above its bubble; the bubble's squared top-left corner
// reads as the tail pointing up to that label (mirrors the user bubble's
// squared bottom-right). Prose + tool rows all nest inside the bubble.
function Turn({ turn, strip, who }) {
  if (turn.role === "user")
    return html`<div class="t-user tv-turn-u">
      <div class="tv-speaker u">You</div>
      <div
        class="bubble"
        dangerouslySetInnerHTML=${{ __html: mdToHtml((turn.blocks || []).map((b) => b.text).join("\n")) }}
      ></div>
    </div>`;
  return html`<div class="t-asst tv-turn">
    <div class="tv-turn-head">
      <span class="tv-speaker">${who}</span>
      <${CopyBtn} get=${() => turnText(turn, strip)} label="copy turn" />
    </div>
    <div class="asst-bubble">
      ${(turn.blocks || []).map((b, i) => html`<${Block} key=${i} b=${b} strip=${strip} />`)}
    </div>
  </div>`;
}

// `conn` is the live TermConn being driven; `live` is true while this view is the
// one on screen, so the 2s transcript poll only runs when it's actually visible.
export function TranscriptView({ conn, live }) {
  const [turns, setTurns] = useState([]);
  const [status, setStatus] = useState("");
  const [scale, setScale] = useState(loadScale);
  const [strip, setStrip] = useState(() => localStorage.getItem("cockpit-tv-strip") === "1");
  const scroller = useRef(null);
  const pinned = useRef(true);
  const sigRef = useRef("");
  const who = conn.label || "Claude";

  // persist the two view knobs
  useEffect(() => { try { localStorage.setItem("cockpit-tv-font", String(scale)); } catch {} }, [scale]);
  useEffect(() => { try { localStorage.setItem("cockpit-tv-strip", strip ? "1" : "0"); } catch {} }, [strip]);
  const bumpScale = (d) => setScale((s) => clampScale(s + d * SSTEP));

  useEffect(() => {
    if (!live) return undefined;
    let alive = true;
    async function poll() {
      const sid = conn.id; // sid8, announced by the PTY bridge on connect
      if (!sid) {
        setStatus("waiting for the session to start…");
        return;
      }
      try {
        const r = await fetch(`/history?session=${encodeURIComponent(sid)}&full=1`);
        const j = await r.json();
        if (!alive) return;
        const t = j.turns || [];
        // Re-render only when the transcript actually grew — a blind 2s setState
        // would fight the scroll pin and re-collapse any <details> the user opened.
        // Signature = turn count + the tail block's text length (cheap, catches
        // both a new turn and streamed growth of the last one).
        const last = t[t.length - 1];
        const lastB = last && last.blocks && last.blocks[last.blocks.length - 1];
        const sig = t.length + ":" + (lastB ? (lastB.text || lastB.result || "").length : 0);
        // Don't replace the DOM while the user is mid-selection inside this panel
        // — re-rendering the (growing) last turn wipes an active highlight before
        // they can copy it, which reads as "I can't select text." Hold the update
        // until the selection is released; the next poll catches up. THE point of
        // this view is hand-selectable text, so the poll yields to it.
        if (sig !== sigRef.current && !_selectionInside(scroller.current)) {
          sigRef.current = sig;
          setTurns(t);
        }
        setStatus(t.length ? "" : "no transcript on disk yet — send a message");
      } catch {
        if (alive) setStatus("transcript unavailable");
      }
    }
    poll();
    const id = setInterval(poll, 2000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [conn, live]);

  // Stick to the bottom (newest) unless the user scrolled up — same pin approach
  // as console.js, so a live-growing transcript follows without yanking a reader.
  useEffect(() => {
    const el = scroller.current;
    if (!el) return undefined;
    const onScroll = () => {
      pinned.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => {
    if (!pinned.current) return undefined;
    const el = scroller.current;
    if (!el) return undefined;
    const id = requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [turns]);

  return html`
    <div class="transcript-view" style=${"--tv-scale:" + scale}>
      <div class="tv-bar">
        <div class="tv-font" title="text size">
          <button class="tv-fbtn" onClick=${() => bumpScale(-1)} title="smaller">A−</button>
          <button class="tv-fbtn" onClick=${() => bumpScale(1)} title="larger">A+</button>
        </div>
        <label class="tv-strip" title="drop Read's line numbers from the view and from copies">
          <input type="checkbox" checked=${strip} onChange=${(e) => setStrip(e.target.checked)} />
          strip line #s
        </label>
        <${CopyBtn} get=${() => allText(turns, strip)} label="copy all" showText=${true} />
      </div>
      <div class="turns tv-turns" ref=${scroller}>
        ${status && html`<div class="t-sys">${status}</div>`}
        ${turns.map((t, i) => html`<${Turn} key=${i} turn=${t} strip=${strip} who=${who} />`)}
      </div>
    </div>
  `;
}
