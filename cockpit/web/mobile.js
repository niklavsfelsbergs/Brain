/* Mobile / phone layout controller for the cockpit.
 *
 * Self-contained — no Preact, no imports. It manipulates the DOM that main.js
 * renders (by class name) and toggles body classes that mobile.css keys on, so
 * it never touches main.js or styles.css (live-sibling surfaces). Loaded after
 * main.js, so #app is already populated when this runs.
 *
 * Below the 760px breakpoint it adds `body.m-mobile`, injects a fixed bottom tab
 * bar (Board / Session / Feed), and shows one full-screen panel at a time via a
 * `body.m-tab-*` class. When a session is selected it lands you on the Session
 * tab, opens at the latest messages, and — for a drivable PTY session — prefers
 * the TRANSCRIPT view (clean text, and the always-present compose bar drives it).
 * Read-only peeks (VS Code / ended sessions) have no composer by design. Desktop
 * never crosses the breakpoint, so none of this activates there. (S-mobile)
 */
const MQ = window.matchMedia("(max-width: 760px)");
const TABS = [
  ["board", "board"],
  ["console", "session"],
  ["feed", "feed"],
];

let bar = null;
let activeTab = "console";
let lastTitle = null; // guards the per-session "on select" actions

function clickIfPresent(sel) {
  const el = document.querySelector(sel);
  if (el) el.click();
}

function setTab(t) {
  activeTab = t;
  const b = document.body;
  b.classList.remove("m-tab-board", "m-tab-console", "m-tab-feed");
  b.classList.add("m-tab-" + t);
  if (bar) for (const btn of bar.children) btn.classList.toggle("on", btn.dataset.tab === t);
  // Board/feed collapse to a thin rail when "closed"; clicking the rail re-mounts
  // the full panel so the tab has something to show.
  if (t === "board") clickIfPresent(".rail-left");
  if (t === "feed") clickIfPresent(".rail-right");
}

function buildBar() {
  if (bar) return;
  bar = document.createElement("div");
  bar.className = "m-tabbar";
  for (const [tab, label] of TABS) {
    const btn = document.createElement("button");
    btn.dataset.tab = tab;
    btn.textContent = label;
    btn.addEventListener("click", () => setTab(tab));
    bar.appendChild(btn);
  }
  document.body.appendChild(bar);
}

// Jump the session view to the latest messages. The console-side autoscroll only
// pins-to-bottom when already near the bottom, so a freshly-opened session sits at
// the top until you scroll — wrong on a phone. History streams in async, so retry.
function scrollSessionToBottom() {
  const col = document.querySelector(".console-col");
  if (!col) return;
  const scrollers = col.querySelectorAll(".turns, .transcript-view, .transcript-view > *");
  scrollers.forEach((el) => {
    if (el.scrollHeight > el.clientHeight) el.scrollTop = el.scrollHeight;
  });
}

// Fires when the shown session changes (console title differs). Lands on the
// Session tab, prefers transcript for drivable sessions, and scrolls to newest.
function onSessionChange() {
  const titleEl = document.querySelector(".console-col .console-title");
  const title = titleEl ? titleEl.textContent : null;
  if (!title || title === lastTitle) return;
  lastTitle = title;
  if (activeTab !== "console") setTab("console");
  // Drivable PTY session: switch to transcript (clean text + compose bar). The
  // toggle exists only for term sessions; peeks have no toggle (read-only).
  const tabs = document.querySelectorAll(".console-col .tv-toggle .tv-tab");
  if (tabs.length === 2 && !tabs[1].classList.contains("on")) tabs[1].click(); // [1] = transcript
  [50, 300, 900].forEach((d) => setTimeout(scrollSessionToBottom, d));
}

function enable() {
  document.body.classList.add("m-mobile");
  buildBar();
  // Make sure all three panels are mounted so any tab can show its content.
  clickIfPresent(".rail-left");
  clickIfPresent(".rail-right");
  setTab(activeTab);
  onSessionChange();
}

function disable() {
  document.body.classList.remove("m-mobile", "m-tab-board", "m-tab-console", "m-tab-feed");
  if (bar) {
    bar.remove();
    bar = null;
  }
}

function apply() {
  if (MQ.matches) enable();
  else disable();
}

// Preact re-renders on every state change; react to a changed session selection.
// Cheap + guarded by the title check, so firing often is fine.
const root = document.getElementById("app");
if (root) {
  const obs = new MutationObserver(() => {
    if (MQ.matches) onSessionChange();
  });
  obs.observe(root, { childList: true, subtree: true });
}

// React to rotate / resize crossing the breakpoint.
if (MQ.addEventListener) MQ.addEventListener("change", apply);
else if (MQ.addListener) MQ.addListener(apply); // older WebKit

// iOS soft-keyboard handling. The session panel is position:fixed, so when the
// compose box is focused the keyboard slides up and COVERS it (the panel is
// positioned against the layout viewport, which the keyboard doesn't shrink) —
// the "can't write" trap. Track the keyboard height via the VisualViewport API
// and expose it as --kb + a body.m-kb flag; mobile.css lifts the session panel
// above the keyboard (and hides the tab bar) while it's open.
const vv = window.visualViewport;
function onViewport() {
  if (!vv) return;
  const kb = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
  document.body.style.setProperty("--kb", kb + "px");
  document.body.classList.toggle("m-kb", MQ.matches && kb > 80);
}
if (vv) {
  vv.addEventListener("resize", onViewport);
  vv.addEventListener("scroll", onViewport);
}

apply();
