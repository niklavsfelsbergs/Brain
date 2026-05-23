// focus.js — click-to-focus URL-scheme dispatch.
//
// The switchboard rows fire this when clicked. The claude-focus VS Code
// extension (niksis8.claude-focus) registers a URI handler at
// `vscode://niksis8.claude-focus/focus?sid8=...` which finds the matching
// terminal pane and brings it forward.

// Trigger the focus URI for a session. The brief flash on the row itself is
// the caller's job (switchboard.js handles its own row outline animation).
export function dispatchFocus(sid8) {
  if (!sid8) return;
  window.location.href = 'vscode://niksis8.claude-focus/focus?sid8=' + encodeURIComponent(sid8);
}

// Copy sid8 to the clipboard. Used for shift-click on switchboard rows when
// the operator wants the id text rather than the focus action.
export function copySid8(sid8) {
  if (!sid8 || !navigator.clipboard) return Promise.resolve(false);
  return navigator.clipboard.writeText(sid8).then(() => true).catch(() => false);
}
