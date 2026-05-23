// activity.js — shared per-session event-cadence store.
//
// The chat panel is the only thing that reads chat.ndjson, so it's the natural
// place to learn "how often is session X firing events." It records each event
// here (keyed by sid8); the switchboard panel reads it back to draw a per-row
// sparkline. Decoupled on purpose — neither panel imports the other, they only
// share this tiny ring-buffer module.
//
// Memory is bounded: each session keeps only timestamps within WINDOW_SEC.

const WINDOW_SEC = 240;          // 4-minute rolling window
const MAX_PER_SESSION = 400;     // hard cap so a runaway session can't grow unbounded

const store = new Map();         // sid8 -> [tsSec, ...] ascending

// Accepts unix-ms or unix-sec; normalizes to seconds.
function toSec(ts) {
  if (typeof ts !== 'number' || !isFinite(ts)) return Date.now() / 1000;
  return ts > 1e12 ? ts / 1000 : ts;
}

export function recordEvent(sid8, ts) {
  if (!sid8) return;
  const t = toSec(ts);
  let arr = store.get(sid8);
  if (!arr) { arr = []; store.set(sid8, arr); }
  arr.push(t);
  const cutoff = (Date.now() / 1000) - WINDOW_SEC;
  while (arr.length && arr[0] < cutoff) arr.shift();
  if (arr.length > MAX_PER_SESSION) arr.splice(0, arr.length - MAX_PER_SESSION);
}

// Bucketize the rolling window into `buckets` slots, oldest→newest (left→right).
// Returns an array of event counts per slot.
export function activityBuckets(sid8, buckets = 16) {
  const out = new Array(buckets).fill(0);
  const arr = store.get(sid8);
  if (!arr || !arr.length) return out;
  const now = Date.now() / 1000;
  const span = WINDOW_SEC / buckets;
  for (const t of arr) {
    const ageIdx = Math.floor((now - t) / span);   // 0 = most recent slot
    if (ageIdx < 0 || ageIdx >= buckets) continue;
    out[buckets - 1 - ageIdx] += 1;
  }
  return out;
}
