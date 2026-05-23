// state.js — shared derivation helpers used by both panels.
//
// Pulled out of the legacy single-file index.html in S052. Kept tiny on purpose:
// these are pure functions plus two constants. The switchboard panel uses them
// to derive per-row state; the chat panel uses `formatWall` to stamp every line.

export const SB_IDLE_AFTER_SEC = 5 * 60;
export const SB_CLOSING_RX = /wrap(ping)?\s*up|clos(e|ing)\s*session|session\s*close/i;

// Seconds since the session's last hook event. `last_event_ts` is unix-seconds
// as written by status-sidecar.py.
export function sbAgeSec(record) {
  if (!record || !record.last_event_ts) return 0;
  return Math.max(0, (Date.now() / 1000) - record.last_event_ts);
}

// Derived state for a switchboard record. The raw `state` field (working /
// waiting_for_user / ended) is enriched with two derived states:
//   - idle:    waiting_for_user with no event for SB_IDLE_AFTER_SEC
//   - closing: working with intent text that looks like session-close prep
// The derivation is read-only; nothing on disk is mutated.
export function deriveSessionState(record) {
  if (record.state === 'ended') return 'ended';
  if (record.state === 'waiting_for_user' && sbAgeSec(record) > SB_IDLE_AFTER_SEC) return 'idle';
  if (record.state === 'working' && SB_CLOSING_RX.test(record.intent || '')) return 'closing';
  return record.state || 'unknown';
}

// HH:MM:SS in local time. Accepts ISO strings, Date, or unix-ms numbers.
// Lives here rather than in chat.js because both panels stamp times.
export function formatWall(input) {
  let d;
  if (input instanceof Date) d = input;
  else if (typeof input === 'number') d = new Date(input);
  else d = new Date(input);
  if (isNaN(d)) return '--:--:--';
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`;
}

// HH:MM for the chat time-rail (one divider per minute instead of a stamp on
// every line). Accepts the same inputs as formatWall.
export function formatMinute(input) {
  let d;
  if (input instanceof Date) d = input;
  else d = new Date(typeof input === 'number' ? input : input);
  if (isNaN(d)) return '';
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

// Strip the repo-root prefix (absolute or ~ form, either slash style) from a
// string so chat lines read as repo-relative. The hook (emit-event.py) now
// shortens at the source too; this is the client-side belt-and-braces pass and
// also cleans the historical lines already sitting in chat.ndjson.
export function shortenPaths(s) {
  let t = String(s == null ? '' : s).replace(/\\/g, '/');
  // brain-rooted (the common case) → repo-relative. Handles C:/…, /c/… and ~/.
  t = t.replace(/(?:[A-Za-z]:\/|\/[A-Za-z]\/|~\/)?(?:Users\/[^/\s]+\/)?Documents\/GitHub\/brain\/?/g, '');
  // any other GitHub repo → strip through GitHub/, keep the repo name + rest.
  t = t.replace(/(?:[A-Za-z]:\/|\/[A-Za-z]\/|~\/)?(?:Users\/[^/\s]+\/)?Documents\/GitHub\//g, '');
  return t.trim();
}

// Map a humanized action line (as composed by emit-event.py) to a verb glyph +
// color class + a cleaned body, plus an isCommit flag so the chat panel can
// promote commits to drop-banners. Pure; no DOM.
const ACTION_RULES = [
  { rx: /^Committing:?\s*(.*)/i,            glyph: '✦', cls: 'act-commit', commit: true },
  { rx: /^Reading\s+(.+)/i,                 glyph: '⌕', cls: 'act-read' },
  { rx: /^Searching(?:\s+for)?\s+(.+)/i,    glyph: '⌕', cls: 'act-read' },
  { rx: /^Looking for files\s*(.*)/i,       glyph: '≣', cls: 'act-glob' },
  { rx: /^Editing\s+(.+)/i,                 glyph: '✎', cls: 'act-edit' },
  { rx: /^Writing\s+(.+)/i,                 glyph: '✚', cls: 'act-write' },
  { rx: /^(?:Staging changes|Checking git status|Reviewing git history|Reviewing diff|Moving files|Pushing to remote)\b.*/i,
    glyph: '⎇', cls: 'act-git', full: true },
  { rx: /^Spawning\s+(.+)/i,                glyph: '☆', cls: 'act-spawn' },
  { rx: /^Starting local web server\b.*/i,  glyph: '❯', cls: 'act-run', full: true },
  { rx: /^Running:\s*([\s\S]+)/i,           glyph: '❯', cls: 'act-run' },
  { rx: /^Using\s+(.+)/i,                   glyph: '•', cls: 'act-misc' },
];

export function humanizeAction(text) {
  const raw = String(text == null ? '' : text).trim();
  for (const r of ACTION_RULES) {
    const m = r.rx.exec(raw);
    if (!m) continue;
    let body = (r.full ? raw : (m[1] != null ? m[1] : raw)).trim();
    if (r.cls === 'act-run') {
      // Collapse newlines and drop a leading `cd <path>` so historical lines
      // (pre-hook-fix) read clean too. New lines arrive already stripped.
      // Keep a bare `cd <path>` (nothing follows) — the dir change *is* the
      // action; stripping it to empty would fall back to the raw ugly string.
      body = body.replace(/\s*\r?\n\s*/g, ' ');
      const stripped = body.replace(/^cd\s+(?:"[^"]*"|'[^']*'|\S+)\s*(?:&&|;)?\s*/i, '').trim();
      if (stripped) body = stripped;
    }
    body = shortenPaths(body);
    if (r.commit && !body) body = 'changes';
    return { glyph: r.glyph, cls: r.cls, body: body || raw, isCommit: !!r.commit };
  }
  return { glyph: '•', cls: 'act-misc', body: shortenPaths(raw), isCommit: false };
}
