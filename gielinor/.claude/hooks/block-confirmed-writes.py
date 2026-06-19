#!/usr/bin/env python3
# Architectural guarantee #1: writes to confirmed/ paths are user-only.
# Fires PreToolUse on Edit/Write/NotebookEdit/MultiEdit. Reads JSON payload
# from stdin; exits 2 to block, 0 to allow.

import json
import sys
from pathlib import Path

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event, classify_path
except Exception:
    def log_event(*a, **k): pass
    def classify_path(p): return ""

# Braindead full-access grant (2026-06-02, principal-authorized): the dev-brain
# construction crew may write confirmed/ paths directly (full rulebook + identity
# authorship is his role). The gate stays for every other actor. Resolve via the
# hardened helper; bypass logged for audit. See write-rules.md.
_HOOK_DIR = Path(__file__).resolve().parent
if str(_HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOK_DIR))
try:
    from _actor import resolve_actor
except Exception:
    def resolve_actor(sid8, brain_root=None): return ""

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent

# Intent sidecars scatter across two dirs (brain-root + gielinor), freshest by
# mtime wins -- same convention _actor.py / status-sidecar.py use.
_INTENT_DIRS = (BRAIN_ROOT / ".claude" / "intent",
                BRAIN_ROOT / "gielinor" / ".claude" / "intent")


def read_mode(sid8: str) -> str:
    """Current ritual mode from the `<sid8>.mode` sidecar (freshest across both
    intent dirs). '' when unset."""
    if not sid8:
        return ""
    best, best_mt = "", -1.0
    for d in _INTENT_DIRS:
        f = d / f"{sid8}.mode"
        try:
            mt = f.stat().st_mtime
            val = f.read_text(encoding="utf-8").strip().lower()
        except OSError:
            continue
        if val and mt > best_mt:
            best, best_mt = val, mt
    return best


def floor_unlocked(sid8: str) -> bool:
    """True iff a non-empty `<sid8>.floor-unlock` marker exists -- the principal's
    explicit, session-scoped grant for Guthix to write confirmed/ during
    bankstanding/alching (D-036). The marker IS the permission record; absent it,
    the floor holds. Deletes are NOT covered (block-deletes.py stays braindead-only)."""
    if not sid8:
        return False
    for d in _INTENT_DIRS:
        try:
            if (d / f"{sid8}.floor-unlock").read_text(encoding="utf-8").strip():
                return True
        except OSError:
            continue
    return False


def is_in_brain(p: Path) -> bool:
    try:
        p.resolve().relative_to(BRAIN_ROOT)
        return True
    except ValueError:
        return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-confirmed-writes: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    if not is_in_brain(p):
        sys.exit(0)

    sid8 = (payload.get("session_id") or "")[:8]
    actor = resolve_actor(sid8)
    if actor == "braindead":
        log_event("block-confirmed", "bypass-braindead", sid8=sid8, detail=str(p))
        sys.exit(0)  # construction crew: unrestricted (principal-authorized)

    parts_lower = [part.lower() for part in p.parts]
    if "confirmed" in parts_lower:
        # D-036: Guthix floor-unlock. Three independent AND-gates -- the principal's
        # explicit, session-scoped grant for closing drafts to confirmed/ during a
        # bankstanding (or its Phase-0 alching). Drop any one and the floor holds.
        # Deletes are NOT covered (block-deletes.py stays braindead-only).
        if (actor == "guthix"
                and read_mode(sid8) in ("bankstanding", "alching")
                and floor_unlocked(sid8)):
            log_event("block-confirmed", "bypass-guthix-authorized", sid8=sid8, detail=str(p))
            sys.exit(0)
        log_event("block-confirmed", "block", sid8=(payload.get("session_id") or "")[:8], path_class="confirmed", detail=str(p))
        print(
            f"BLOCKED: writes to confirmed/ paths are user-only.\n"
            f"  Path: {p}\n"
            f"  Propose this change as a draft instead "
            f"(see meta/drafts-mechanics.md).",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
