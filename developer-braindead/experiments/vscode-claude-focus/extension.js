// claude-focus — focuses the VS Code terminal pane belonging to a Claude
// Code session whose switchboard row was clicked.
//
// Triggered by `vscode://niksis8.claude-focus/focus?sid8=<sid8>` URIs fired
// from the switchboard sidebar (developer-braindead/experiments/visualizer/
// index.html). VS Code routes the URI to whichever window owns the URI
// handler — the extension can only focus terminals in *its own* window.
//
// Flow:
//   1. Parse sid8 from the URI query.
//   2. Read ~/.claude/status/<sid8>.json for `claude_pid_chain`
//      (recorded by status-sidecar.py at hook fire time).
//   3. Iterate vscode.window.terminals; resolve each terminal's processId.
//   4. The first terminal whose processId appears anywhere in the chain
//      wins. show() it and we're done.
//   5. No match → status-bar message. Probably the URI landed in the wrong
//      VS Code window or the chain is stale.

const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const os = require('os');

function activate(context) {
  const handler = {
    async handleUri(uri) {
      if (uri.path !== '/focus') {
        vscode.window.setStatusBarMessage(
          `claude-focus: unknown path '${uri.path}'`, 4000);
        return;
      }
      const params = new URLSearchParams(uri.query);
      const sid8 = (params.get('sid8') || '').trim().toLowerCase();
      if (!/^[0-9a-f]{8}$/.test(sid8)) {
        vscode.window.setStatusBarMessage(
          `claude-focus: invalid sid8 '${sid8}'`, 4000);
        return;
      }

      const statusFile = path.join(
        os.homedir(), '.claude', 'status', `${sid8}.json`);
      let chain;
      try {
        const raw = fs.readFileSync(statusFile, 'utf8');
        const status = JSON.parse(raw);
        chain = Array.isArray(status.claude_pid_chain)
          ? status.claude_pid_chain : [];
      } catch (e) {
        vscode.window.setStatusBarMessage(
          `claude-focus: can't read status for ${sid8}`, 4000);
        return;
      }
      if (!chain.length) {
        vscode.window.setStatusBarMessage(
          `claude-focus: no pid chain for ${sid8} (send a message in that session to refresh)`,
          5000);
        return;
      }

      const chainPids = new Set(
        chain.map(n => Number(n.pid)).filter(n => Number.isFinite(n) && n > 0));

      // terminal.processId is a Promise<number | undefined>; await each.
      // Walk in current order so newer terminals (likely the click target)
      // win ties.
      for (const t of vscode.window.terminals) {
        let pid;
        try { pid = await t.processId; } catch { continue; }
        if (!pid) continue;
        if (chainPids.has(pid)) {
          // show(preserveFocus=false) gives the terminal focus.
          t.show(false);
          vscode.window.setStatusBarMessage(
            `claude-focus: focused ${t.name || `terminal pid ${pid}`} for ${sid8}`,
            3000);
          return;
        }
      }

      vscode.window.setStatusBarMessage(
        `claude-focus: no terminal in this window matches sid8 ${sid8} (wrong window?)`,
        5000);
    }
  };

  context.subscriptions.push(vscode.window.registerUriHandler(handler));
}

function deactivate() {}

module.exports = { activate, deactivate };
