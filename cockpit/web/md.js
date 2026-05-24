// Minimal, safe markdown → HTML. Escapes first, then a small block + inline subset.

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
  let listBuf = null;
  const flushList = () => {
    if (listBuf) {
      out.push("<ul>" + listBuf.map((li) => `<li>${inline(li)}</li>`).join("") + "</ul>");
      listBuf = null;
    }
  };
  for (const ln of lines) {
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
    const li = ln.match(/^\s*[-*]\s+(.*)$/);
    if (li) {
      (listBuf = listBuf || []).push(li[1]);
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
      flushList();
      continue;
    }
    flushList();
    out.push(`<p>${inline(ln)}</p>`);
  }
  if (inCode) out.push(`<pre><code>${codeBuf.join("\n")}</code></pre>`);
  flushList();
  return out.join("");
}
