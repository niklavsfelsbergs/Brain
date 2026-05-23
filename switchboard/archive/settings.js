// settings.js — shared, localStorage-backed UI toggles + a tiny change bus.
//
// The COMMS bottom bar (chat.js) owns the toggle buttons, but some toggles
// drive the switchboard panel (e.g. sound-on-WAITING). Rather than have the
// two panels import each other, they both lean on this module — same decoupling
// pattern as activity.js. Keys are plain booleans:
//
//   actions    — show the Read/Edit/Glob/git tool-call stream in chat
//   sound      — chime when a session flips to WAITING
//   players / subagents / braindead / guthix / commits
//              — per-channel chat visibility (true = shown)
//
// State persists in localStorage under one key so a browser remembers the
// operator's preferences across reloads.

const KEY = 'sb-settings';
const DEFAULTS = {
  actions: true,
  sound: false,
  players: true,
  subagents: true,
  braindead: true,
  guthix: true,
  commits: true,
};

let cache = null;
const listeners = new Set();

function load() {
  if (cache) return cache;
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (_) { /* corrupt → defaults */ }
  cache = { ...DEFAULTS, ...stored };
  return cache;
}

export function getSetting(key) {
  return load()[key];
}

export function setSetting(key, value) {
  const s = load();
  s[key] = value;
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (_) { /* private mode */ }
  for (const fn of listeners) { try { fn(key, value); } catch (_) {} }
}

// Subscribe to changes. Returns an unsubscribe function.
export function onSettingChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
