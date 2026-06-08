// Minimal, safe markdown → HTML. Escapes first, then a small block + inline subset.

import { linkifyPaths } from "./links.js";

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Link hardening (S085). esc() above neutralizes <>& but NOT quotes or URL
// schemes, so a raw `[t](url)` could inject an attribute (url contains a ")
// or run script (url is `javascript:`/`data:`). safeUrl drops any explicit
// scheme that isn't http(s)/mailto (relative/anchor links pass through); the
// surviving href is then quote-escaped before it lands in the attribute.
function safeUrl(u) {
  const t = (u || "").trim();
  const m = /^([a-z][a-z0-9+.-]*):/i.exec(t);
  if (m) {
    const scheme = m[1].toLowerCase();
    if (scheme !== "http" && scheme !== "https" && scheme !== "mailto") return "";
  }
  return t;
}

// GFM table support. A table is a `|`-bearing header row immediately followed
// by a separator row of dash-cells (`| --- | :--: |`), then body rows. SEP_RE
// matches the separator (optional outer pipes, optional alignment colons); the
// bare-`---` hr case never reaches here because a table requires the |-header
// directly above the separator.
const SEP_RE = /^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$/;

function splitRow(ln) {
  let s = ln.trim();
  if (s.startsWith("|")) s = s.slice(1);
  if (s.endsWith("|")) s = s.slice(0, -1);
  return s.split("|").map((c) => c.trim());
}

function inline(s) {
  return s
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, txt, url) => {
      const safe = safeUrl(url);
      // Unsafe scheme → render the link text only, no anchor.
      return safe
        ? `<a href="${safe.replace(/"/g, "&quot;")}" target="_blank" rel="noopener noreferrer">${txt}</a>`
        : txt;
    });
}

export function mdToHtml(text) {
  const lines = esc(text || "").split("\n");
  const out = [];
  let inCode = false;
  let codeBuf = [];
  let listBuf = null; // { type: "ul" | "ol", items: [] }
  // A blank line BETWEEN list items makes a "loose" list — still ONE list, not a
  // fresh one per item. Flushing on every blank (the old behavior) split a
  // blank-separated ordered list into N single-item <ol>s, each restarting at 1
  // (the "all items show 1." bug). So defer the flush across a blank: a same-type
  // item that follows continues the list; any other content closes it.
  let pendingBlank = false;
  const flushList = () => {
    if (listBuf) {
      const { type, items } = listBuf;
      out.push(`<${type}>` + items.map((li) => `<li>${inline(li)}</li>`).join("") + `</${type}>`);
      listBuf = null;
    }
    pendingBlank = false;
  };
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    if (/^```/.test(ln)) {
      if (inCode) {
        out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
        codeBuf = [];
        inCode = false;
      } else {
        flushList();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(ln);
      continue;
    }
    const h = ln.match(/^(#{1,3})\s+(.*)$/);
    if (h) {
      flushList();
      out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`);
      continue;
    }
    // GFM table: |-bearing header row + a separator row on the next line.
    if (ln.includes("|") && i + 1 < lines.length && SEP_RE.test(lines[i + 1])) {
      flushList();
      const headers = splitRow(ln);
      const aligns = splitRow(lines[i + 1]).map((c) => {
        const l = c.startsWith(":");
        const r = c.endsWith(":");
        return l && r ? "center" : r ? "right" : l ? "left" : "";
      });
      const alignAttr = (idx) => (aligns[idx] ? ` style="text-align:${aligns[idx]}"` : "");
      i += 1; // consume the separator row
      const rows = [];
      while (i + 1 < lines.length && lines[i + 1].trim() !== "" && lines[i + 1].includes("|")) {
        rows.push(splitRow(lines[i + 1]));
        i += 1;
      }
      const thead =
        "<thead><tr>" +
        headers.map((hd, idx) => `<th${alignAttr(idx)}>${inline(hd)}</th>`).join("") +
        "</tr></thead>";
      const tbody =
        "<tbody>" +
        rows
          .map(
            (r) =>
              "<tr>" +
              headers.map((_, idx) => `<td${alignAttr(idx)}>${inline(r[idx] || "")}</td>`).join("") +
              "</tr>",
          )
          .join("") +
        "</tbody>";
      out.push(`<table>${thead}${tbody}</table>`);
      continue;
    }
    const ul = ln.match(/^\s*[-*]\s+(.*)$/);
    const ol = ln.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ul || ol) {
      const type = ul ? "ul" : "ol";
      if (!listBuf || listBuf.type !== type) {
        flushList();
        listBuf = { type, items: [] };
      }
      pendingBlank = false; // a same-type item after a blank → keep ONE list, don't restart
      listBuf.items.push((ul || ol)[1]);
      continue;
    }
    if (/^\s*---+\s*$/.test(ln)) {
      flushList();
      out.push("<hr>");
      continue;
    }
    const q = ln.match(/^>\s?(.*)$/);
    if (q) {
      flushList();
      out.push(`<blockquote>${inline(q[1])}</blockquote>`);
      continue;
    }
    if (ln.trim() === "") {
      // Don't end an open list on a single blank — defer. A following same-type
      // item continues it (loose list); any other block flushes via flushList().
      if (listBuf) pendingBlank = true;
      else flushList();
      continue;
    }
    flushList();
    out.push(`<p>${inline(ln)}</p>`);
  }
  if (inCode) out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
  flushList();
  // Final pass: make file-path tokens clickable (S160). Runs on the assembled,
  // already-escaped HTML and skips text inside existing tags/anchors, so it never
  // double-links a markdown link or breaks the markup.
  return linkifyPaths(out.join(""));
}
