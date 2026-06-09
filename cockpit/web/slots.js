// slots.js — recycling per-chat numbers. Each live session on the board gets
// the lowest free positive integer as a memory anchor ("chat 3 is my UPS dig").
// A number frees the moment its session leaves the board, and the next new
// session reclaims the lowest unused slot — so the pool stays dense and small.
//
// In-memory only (no localStorage): the numbers are ephemeral tags for the
// current cockpit run, not durable IDs. On a reload the map starts empty and
// is rebuilt oldest-first (oldest live chat = 1) so the board comes back
// deterministically ordered rather than scrambled or carrying dead sids.

let slots = {}; // sid8 -> number, for sessions currently on the board

function lowestFree() {
  const used = new Set(Object.values(slots));
  let n = 1;
  while (used.has(n)) n++;
  return n;
}

// Reconcile the slot map against the live session set. Call once per render
// (before reading slotFor): frees numbers held by dropped sessions, then hands
// the lowest free slot to each still-unnumbered session, oldest-first so a
// fresh map rebuilds deterministically by age.
export function reconcileSlots(sessions) {
  const live = new Set(sessions.map((s) => s.sid8));
  for (const sid8 of Object.keys(slots)) {
    if (!live.has(sid8)) delete slots[sid8];
  }
  const unnumbered = sessions
    .filter((s) => slots[s.sid8] == null)
    .sort((a, b) => (b.age_sec ?? 0) - (a.age_sec ?? 0)); // largest age = oldest first
  for (const s of unnumbered) {
    slots[s.sid8] = lowestFree();
  }
  return slots;
}

export function slotFor(sid8) {
  return (sid8 && slots[sid8]) || null;
}
