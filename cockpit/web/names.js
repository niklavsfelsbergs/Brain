// names.js — custom per-session display labels (S066). Set via `/rename <name>`
// typed in a terminal (intercepted in term.js) or anywhere else that calls
// setName. Keyed by sid8, persisted, with a change notifier so the board and
// console title update immediately rather than waiting for the next poll.

const KEY = "cockpit-names";

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}

let names = load();
const subs = new Set();

export function nameFor(sid8) {
  return (sid8 && names[sid8]) || "";
}

export function setName(sid8, name) {
  if (!sid8) return;
  if (name) names[sid8] = name;
  else delete names[sid8];
  try {
    localStorage.setItem(KEY, JSON.stringify(names));
  } catch {}
  for (const f of subs) f();
}

export function subscribeNames(fn) {
  subs.add(fn);
  return () => subs.delete(fn);
}
