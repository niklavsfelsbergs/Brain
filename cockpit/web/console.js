// The session console (right column) — a pure view that subscribes to a
// SessionConn from fleet.js. It owns no connection; switching away leaves the
// session running. Renders streamed text / thinking / tool cards / dividers.

import { useEffect, useRef, useReducer, useState } from "preact/hooks";
import { html } from "htm/preact";
import { mdToHtml } from "./md.js";

function toolSummary(name, input) {
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
        <span class="tool-arg">${toolSummary(b.name, b.input)}</span>
      </div>
      ${b.result != null &&
      html`<details class="tool-result"><summary>result</summary><pre>${b.result}</pre></details>`}
    </div>`;
  return null;
}

function Turn({ turn }) {
  if (turn.role === "user")
    return html`<div class="t-user">
      <div
        class="bubble"
        dangerouslySetInnerHTML=${{ __html: mdToHtml(turn.blocks.map((b) => b.text).join("\n")) }}
      ></div>
    </div>`;
  if (turn.role === "divider")
    return html`<div class="t-divider">
      ${turn.cost != null ? html`<span>$${turn.cost.toFixed(4)}</span>` : ""}
      ${turn.ms != null ? html`<span>${(turn.ms / 1000).toFixed(1)}s</span>` : ""}
    </div>`;
  if (turn.role === "sys") return html`<div class="t-sys">${turn.text}</div>`;
  return html`<div class="t-asst">${turn.blocks.map((b, i) => html`<${Block} key=${i} b=${b} />`)}</div>`;
}

function Preview({ preview }) {
  return html`<div class="t-asst streaming">
    ${preview.thinking &&
    html`<details class="b-think" open><summary>thinking…</summary><div>${preview.thinking}</div></details>`}
    ${preview.text &&
    html`<div class="b-text" dangerouslySetInnerHTML=${{ __html: mdToHtml(preview.text) }}></div>`}
    <span class="cursor">▋</span>
  </div>`;
}

export function Console({ conn, title, onRelease, onAdopt }) {
  const [, force] = useReducer((x) => x + 1, 0);
  const rafRef = useRef(0);
  const turnsRef = useRef(null);
  const pinned = useRef(true); // stick to the bottom (newest) until the user scrolls up
  const [input, setInput] = useState("");

  useEffect(() => {
    const rerender = () => {
      if (!rafRef.current)
        rafRef.current = requestAnimationFrame(() => {
          rafRef.current = 0;
          force();
        });
    };
    const unsub = conn.subscribe(rerender);
    rerender();
    return unsub;
  }, [conn]);

  // Stick to the bottom (newest) until the user scrolls up. A single synchronous
  // scrollTop=scrollHeight on load races markdown/font/<details> layout — measured
  // too early it lands short of, or at the top of, the transcript, and a static
  // replayed history (no further renders) never corrects, so a row-jump leaves you
  // at the top. Instead: track the user's scroll to set/clear the pin, and on every
  // content render scroll to bottom on the NEXT frame, after layout has settled.
  useEffect(() => {
    const el = turnsRef.current;
    if (!el) return;
    const onScroll = () => {
      pinned.current = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [conn]);
  useEffect(() => {
    if (!pinned.current) return;
    const el = turnsRef.current;
    if (!el) return;
    const id = requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  });

  const model = conn.model;
  const send = () => {
    const text = input.trim();
    if (text && conn.sendInput(text)) setInput("");
  };

  return html`
    <div class="console">
      <div class="console-head">
        <span class="console-title">${title}</span>
        <span class="console-status">${model.status}</span>
        ${conn.drive && conn.id && onRelease
          ? html`<button class="release" title="terminate this session" onClick=${() => onRelease(conn.id)}>
              release
            </button>`
          : ""}
      </div>
      <div class="turns" ref=${turnsRef}>
        ${model.turns.map((t, i) => html`<${Turn} key=${i} turn=${t} />`)}
        ${(model.preview.text || model.preview.thinking) && html`<${Preview} preview=${model.preview} />`}
      </div>
      ${conn.drive
        ? html`<div class="composer">
            <textarea
              value=${input}
              onInput=${(e) => setInput(e.target.value)}
              onKeyDown=${(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder="message…"
            ></textarea>
            ${model.busy
              ? html`<button class="stop" onClick=${() => conn.interrupt()}>Stop</button>`
              : html`<button class="send" onClick=${send}>Send</button>`}
          </div>`
        : conn.host === "cockpit" && onAdopt
        ? html`<div class="composer readonly">
            <span>read-only — driven on another device</span>
            <button
              class="adopt"
              title="terminate it on the other device and resume it here"
              onClick=${() => onAdopt(conn)}
              style="margin-left:10px;padding:5px 12px;border:1px solid var(--gold-dk);border-radius:6px;background:transparent;color:var(--gold);cursor:pointer;font:inherit;"
            >drive here</button>
          </div>`
        : html`<div class="composer readonly">read-only — this session runs in VS Code</div>`}
    </div>
  `;
}
