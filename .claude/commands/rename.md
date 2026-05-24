---
description: Relabel this session on the cockpit board (silent, no model turn)
argument-hint: <name>
---
<cockpit-rename>$ARGUMENTS</cockpit-rename>

(If you are reading this line, the `rename-intercept` UserPromptSubmit hook did not fire — normally it captures this command silently and blocks it before any model turn. Fallback: the user wants this session relabeled to "$ARGUMENTS" on the cockpit board. Write that name to `switchboard/state-names.json` at the brain root, keyed by this session's 8-char sid (first 8 chars of the session id), then confirm in one short line. Do nothing else.)
