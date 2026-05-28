#!/usr/bin/env python3
"""verification/check.py -- golden-file verification harness (Khaan item 5).

Runs a registry of CODE-SHAPED checks over the brain's enforcement surfaces --
the things a refactor can silently break, where "it looks wired" is not the same
as "it fires." Answers "is the guarantee actually enforced?" with a command
instead of a manual audit every few weeks (the verify-enforcement-fires lesson,
made permanent).

Checks (this first cut):
  C1  banner-integrity   -- the failure-banner registry holds the 4 expected
                            ritual banners, and born-link-lint.py's BANNER
                            constant matches its registry block byte-for-byte
                            (so the .md canonical and the .py mirror can't drift).
  C2  born-link-golden   -- the born-link linter BLOCKS a malformed wikilink
                            (exit 1 + its banner) and PASSES a clean file (exit 0).
  C3  write-boundaries   -- each sub-agent write-boundary hook BLOCKS an
                            off-surface path (exit 2), ALLOWS an on-surface path
                            (exit 0), and stays INERT on an untyped
                            (general-purpose) spawn (exit 0) -- the S110 caveat.

Fixtures are inline (written to a tempdir at run time), NOT committed .md files
-- the born-link COMMIT hook lints every staged .md, so a committed
malformed-link fixture would block its own commit.

Deferred (brittle / low-value): markdown-structure checks (respawn step-order,
drafts-triage verdict table) break on benign rewording. The born-link WRAP path
(vs the BLOCK path covered here) needs a resolvable mini-vault fixture -- it is
exercised live by every commit (verified S118).

Ship-dormant (Khaan item 12): this harness is runnable standalone
(`python developer-braindead/verification/check.py`) but is deliberately NOT
auto-wired into the pre-commit hook. Promote it there when you want it as a gate.

Exit 0 if all checks pass; exit 1 (with the locked banner) if any fail.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # brain root
GIELINOR = ROOT / "gielinor"
DEVBRAIN = ROOT / "developer-braindead"
REGISTRY = GIELINOR / "spellbook" / "failure-banners.md"
BORN_LINK = DEVBRAIN / "bank" / "research" / "born-link-lint.py"
HOOKS = GIELINOR / ".claude" / "hooks"

# Locked failure receipt for the harness itself (dogfooding Khaan item 2). This
# one is construction tooling, not a ritual, so it lives here -- NOT in the
# gielinor registry (C1 asserts that registry holds exactly the 4 ritual banners).
BANNER = (
    "## VERIFICATION FAILED -- a brain guarantee is not holding\n"
    "One or more golden checks failed. A refactor may have silently broken an "
    "enforcement surface; fix the failing check(s) before trusting the guarantee."
)

EXPECTED_BANNER_HEADINGS = [
    "RESPAWN HALTED",
    "ALCHING HALTED",
    "DRAFTS-TRIAGE HALTED",
    "BORN-LINK LINT FAILED",
]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _registry_banners() -> list[str]:
    """The fenced banner blocks in the registry (the only ``` fences in it)."""
    text = REGISTRY.read_text(encoding="utf-8")
    return re.findall(r"```\n(## .*?)\n```", text, re.S)


# --- checks: each returns (name, ok: bool, detail: str) ---

def check_banner_integrity():
    name = "C1 banner-integrity"
    try:
        banners = _registry_banners()
        headings = [b.splitlines()[0] for b in banners]
        missing = [e for e in EXPECTED_BANNER_HEADINGS
                   if not any(e in h for h in headings)]
        if len(banners) != len(EXPECTED_BANNER_HEADINGS) or missing:
            return (name, False,
                    f"want {len(EXPECTED_BANNER_HEADINGS)} banners {EXPECTED_BANNER_HEADINGS}; "
                    f"got {len(banners)} headings={headings} missing={missing}")
        bll = _load(BORN_LINK, "bll_c1")
        born = next((b for b in banners if b.startswith("## BORN-LINK")), None)
        if born is None:
            return (name, False, "no BORN-LINK banner in registry")
        if born != bll.BANNER:
            return (name, False,
                    "born-link-lint.py BANNER has drifted from its registry block "
                    "(the .md canonical and .py mirror must match byte-for-byte)")
        return (name, True, "4 ritual banners present; born-link .py mirror matches registry")
    except Exception as e:
        return (name, False, f"exception: {e}")


def _run_lint(vault: Path, fname: str):
    return subprocess.run(
        [sys.executable, str(BORN_LINK), "--vault", str(vault), "--files", fname, "--check"],
        capture_output=True, text=True)


def check_born_link_golden():
    name = "C2 born-link-golden"
    try:
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td)
            (vault / "malformed.md").write_text(
                "See [[broken.md]] and [[../escape]].\n", encoding="utf-8")
            (vault / "clean.md").write_text(
                "A note linking [[D-004_stable_ids]] -- no malformed targets.\n",
                encoding="utf-8")
            r_bad = _run_lint(vault, "malformed.md")
            if r_bad.returncode != 1 or "BORN-LINK LINT FAILED" not in r_bad.stderr:
                return (name, False,
                        f"malformed fixture: want exit 1 + banner, got exit={r_bad.returncode}")
            r_ok = _run_lint(vault, "clean.md")
            if r_ok.returncode != 0:
                return (name, False,
                        f"clean fixture: want exit 0, got exit={r_ok.returncode} "
                        f"stderr={r_ok.stderr[:160]!r}")
        return (name, True, "malformed blocks (exit 1 + banner); clean passes (exit 0)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def _run_hook(hook: str, agent_type: str, file_path: Path, tool: str = "Write"):
    payload = {"agent_type": agent_type, "tool_name": tool,
               "tool_input": {"file_path": str(file_path)}}
    return subprocess.run([sys.executable, str(HOOKS / hook)],
                          input=json.dumps(payload), capture_output=True, text=True)


def check_write_boundaries():
    name = "C3 write-boundaries"
    J = GIELINOR / "players" / "jebrim"
    # (hook, role, an off-surface path -> block, an on-surface path -> allow)
    cases = [
        ("dwarf-write-boundary.py", "dwarf",
         J / "examine" / "drafts" / "x.md", J / "bank" / "notes" / "x.md"),
        ("gnome-write-boundary.py", "gnome",
         GIELINOR / "meta" / "x.md", J / "bank" / "drafts" / "notes" / "x.md"),
        ("penguin-write-boundary.py", "penguin",
         J / "bank" / "notes" / "x.md", J / "research" / "x.md"),
        ("shipping-agent-write-boundary.py", "shipping-agent",
         J / "bank" / "notes" / "x.md", J / "inventory" / "x.md"),
    ]
    try:
        fails = []
        for hook, role, blocked, allowed in cases:
            rb = _run_hook(hook, role, blocked)
            if rb.returncode != 2:
                fails.append(f"{role}: off-surface path got exit {rb.returncode} (want 2)")
            ra = _run_hook(hook, role, allowed)
            if ra.returncode != 0:
                fails.append(f"{role}: on-surface path got exit {ra.returncode} (want 0)")
            ri = _run_hook(hook, "general-purpose", blocked)
            if ri.returncode != 0:
                fails.append(f"{role}: hook fired on a general-purpose spawn "
                             f"(want inert exit 0, got {ri.returncode})")
        if fails:
            return (name, False, "; ".join(fails))
        return (name, True,
                "4 boundary hooks block off-surface (exit 2) + allow on-surface (exit 0) "
                "+ stay inert on untyped spawns")
    except Exception as e:
        return (name, False, f"exception: {e}")


CHECKS = [check_banner_integrity, check_born_link_golden, check_write_boundaries]


def main() -> int:
    results = [fn() for fn in CHECKS]
    width = max(len(r[0]) for r in results)
    for cname, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:<{width}}  {detail}")
    if all(ok for _, ok, _ in results):
        print(f"\n{len(results)}/{len(results)} checks passed.")
        return 0
    sys.stderr.write("\n" + BANNER + "\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
