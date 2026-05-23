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
