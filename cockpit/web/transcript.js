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

function CopyBtn({ get, label = "copy" }) {
  const [done, setDone] = useState("");
  const onClick = async (e) => {
    e.stopPropagation();
    const ok = await copyText(get());
    setDone(ok ? "copied ✓" : "failed");
    setTimeout(() => setDone(""), 1200);
  };
  return html`<button class="copy-btn" onClick=${onClick} title="copy clean text">${done || label}</button>`;
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
// the copy buttons grab; the DOM render is only for reading.
function turnText(turn) {
  if (turn.role === "user") return (turn.blocks || []).map((b) => b.text || "").join("\n");
  const parts = [];
  for (const b of turn.blocks || []) {
    if (b.t === "text") parts.push(b.text || "");
    else if (b.t === "thinking") parts.push("[thinking]\n" + (b.text || ""));
    else if (b.t === "tool") {
      parts.push(`[${b.name} ${toolSummary(b.input)}]`.trim());
      if (b.result != null) parts.push(b.result);
    }
  }
  return parts.filter(Boolean).join("\n");
}
function allText(turns) {
  return (turns || [])
    .map((t) => (t.role === "user" ? "You:\n" : "") + turnText(t))
    .filter((s) => s.trim())
    .join("\n\n———\n\n");
}

function Block({ b }) {
  if (b.t === "text")
    return html`<div class="b-text" dangerouslySetInnerHTML=${{ __html: mdToHtml(b.text) }}></div>`;
  if (b.t === "thinking")
    return html`<details class="b-think">
      <summary>thinking</summary>
      <div dangerouslySetInnerHTML=${{ __html: mdToHtml(b.text) }}></div>
    </details>`;
  if (b.t === "tool")
    return html`<div class=${"b-tool" + (b.isError ? " err" : "")}>
      <div class="tool-head">
        <span class="tool-name">${b.name}</span>
        <span class="tool-arg">${toolSummary(b.input)}</span>
        ${b.result != null && html`<${CopyBtn} get=${() => b.result || ""} label="copy output" />`}
      </div>
      ${b.result != null && html`<pre class="tv-result">${b.result}</pre>`}
    </div>`;
  return null;
}

function Turn({ turn }) {
  if (turn.role === "user")
    return html`<div class="t-user">
      <div
        class="bubble"
        dangerouslySetInnerHTML=${{ __html: mdToHtml((turn.blocks || []).map((b) => b.text).join("\n")) }}
      ></div>
    </div>`;
  return html`<div class="t-asst tv-turn">
    <div class="tv-turn-bar"><${CopyBtn} get=${() => turnText(turn)} label="copy turn" /></div>
    ${(turn.blocks || []).map((b, i) => html`<${Block} key=${i} b=${b} />`)}
  </div>`;
}

// `conn` is the live TermConn being driven; `live` is true while this view is the
// one on screen, so the 2s transcript poll only runs when it's actually visible.
export function TranscriptView({ conn, live }) {
  const [turns, setTurns] = useState([]);
  const [status, setStatus] = useState("");
  const scroller = useRef(null);
  const pinned = useRef(true);
  const sigRef = useRef("");

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
    <div class="transcript-view">
      <div class="tv-bar">
        <span class="tv-hint">clean text — select &amp; copy freely, no terminal wrapping</span>
        <${CopyBtn} get=${() => allText(turns)} label="copy all" />
      </div>
      <div class="turns tv-turns" ref=${scroller}>
        ${status && html`<div class="t-sys">${status}</div>`}
        ${turns.map((t, i) => html`<${Turn} key=${i} turn=${t} />`)}
      </div>
    </div>
  `;
}
