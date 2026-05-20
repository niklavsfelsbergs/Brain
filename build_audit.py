"""Generate gielinor-audit.html — single self-contained audit tool for gielinor/.

Walks gielinor/, reads every file, attaches hand-authored purpose + drift annotations,
emits a single .html file at brain root with no external dependencies.

Run:
    python build_audit.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent
GIELINOR = BRAIN_ROOT / "gielinor"
OUTPUT = BRAIN_ROOT / "gielinor-audit.html"


# ---------------------------------------------------------------------------
# Hand-authored metadata. Keys are paths relative to gielinor/ using forward slashes.
#
# purpose: one-sentence role-of-file (NOT a paraphrase of contents).
# drift:   True iff the builder made a non-obvious judgment call Niklavs should
#          double-check. Per the audit spec, candidates include every _about.md,
#          D-001 and D-002, all persona.md and player _about.md, the four hooks,
#          all CLAUDE.md, and the rituals.
# reason:  one-line description of the specific judgment call (only if drift).
# ---------------------------------------------------------------------------

META: dict[str, dict] = {
    # Body
    "CLAUDE.md": {
        "purpose": "Session entry point: the file Claude Code reads first; binds the master rulebook and points to the rituals.",
        "drift": True,
        "reason": "Builder authored the framing prose, the layer index, and the four-guarantees enumeration. Updated in S004: cross-player dwarf invocation section strengthened to enumerate trigger phrases ('ask {name} to ...', etc.); layer index updated to describe lorebook as the self-improvement log (not the build log). Verify the new lorebook framing in the layer index and the expanded dwarf-trigger list.",
    },
    "CLAUDE.local.md": {
        "purpose": "Local-only body file (gitignored); holds machine-specific or personal-secret additions to master CLAUDE.md.",
        "drift": False,
    },
    ".mcp.json": {
        "purpose": "MCP server registry for this project; empty in Phase 1 (no servers wired).",
        "drift": False,
    },
    "ticks.md": {
        "purpose": "Scheduling slot — dormant Phase 1; will hold recurring-job definitions when Phase 2 picks a substrate (Routines vs VPS).",
        "drift": True,
        "reason": "Builder authored the Phase 2 substrate framing (Routines vs VPS) and a proposed YAML format. Both are forward-looking guesses, not requirements — confirm the substrate framing matches your actual Phase 2 thinking before content accumulates against it.",
    },

    # .claude/
    ".claude/settings.json": {
        "purpose": "Wires the four hook scripts to PreToolUse matchers (Edit/Write/NotebookEdit/MultiEdit, Bash/PowerShell, Agent/Task) — the file that makes the architectural guarantees real.",
        "drift": True,
        "reason": "Security boundary. Matcher patterns and command strings are load-bearing. Verify the PowerShell matcher is right (Claude Code may not emit a 'PowerShell' tool name on your machine — check the actual tool name), and that ${CLAUDE_PROJECT_DIR} resolves correctly when sessions are opened in player subfolders.",
    },
    ".claude/hooks/block-confirmed-writes.py": {
        "purpose": "Hook #1 — fires PreToolUse on edits; blocks (exit 2) any write to a path containing a 'confirmed' segment under gielinor/.",
        "drift": True,
        "reason": "Security boundary. The 'confirmed' segment match is case-folded over Path.parts — confirm that's the right scope (it will block writes to any future folder named 'confirmed', not just identity layers). is_in_brain() uses BRAIN_ROOT = the parent of .claude/hooks/.parent.parent — that resolves to gielinor/, so the hook only fires for paths under gielinor/ and is a no-op elsewhere. Double-check that's what you want.",
    },
    ".claude/hooks/block-deletes.py": {
        "purpose": "Hook #2 — fires PreToolUse on Bash/PowerShell; pattern-matches the command string for delete verbs and blocks broadly.",
        "drift": True,
        "reason": "Security boundary. Pattern-match-on-command-string is blunt — it will block legitimate deletes anywhere on disk while a Claude Code session is running in gielinor/, not only deletes targeting the brain. Confirm that's the right trade-off; the alternative (parse the path argument) is harder to do safely. Also verify the regex set covers your shells (rm, Remove-Item, del, erase, unlink, rmdir, ri/rd PS aliases, .unlink(), shutil.rmtree).",
    },
    ".claude/hooks/dwarf-write-boundary.py": {
        "purpose": "Hook #3 — fires PreToolUse on edits when CLAUDE_BRAIN_DWARF=1; restricts a sub-agent's write surface to bank/notes, quest-log/{in-progress,completed}, inventory, and lorebook/patch-notes.md.",
        "drift": True,
        "reason": "Security boundary and environmental assumption. Requires CLAUDE_BRAIN_DWARF=1 to be set on the spawned sub-agent — confirm Claude Code's Agent tool actually propagates env vars to sub-agent hook calls, and that you have a way (or a discipline) to set it when spawning a dwarf. If env propagation doesn't work, the dwarf boundary is silently inert.",
    },
    ".claude/hooks/block-sub-dwarf-spawn.py": {
        "purpose": "Hook #4 — fires PreToolUse on Agent/Task when CLAUDE_BRAIN_DWARF=1; blocks any further sub-agent spawn from inside a dwarf.",
        "drift": True,
        "reason": "Security boundary and environmental assumption (same env-var concern as hook #3). Also: matcher 'Agent|Task' assumes Claude Code's spawn tool surfaces as one of those names — verify against your version (the tool list at the top of this audit session lists 'Agent', so 'Task' is belt-and-braces).",
    },

    # meta/
    "meta/_about.md": {
        "purpose": "Layer card for meta/ — names the lifetime asymmetry (meta rewrites in place, lorebook only grows) and points at the rulebook files.",
        "drift": True,
        "reason": "_about.md files are framing documents; the builder chose the metaphor (current-rulebook-vs-history) and the boundary between meta/ and lorebook/. Verify that boundary is exactly what you want — the audit's most likely correction site.",
    },
    "meta/write-rules.md": {
        "purpose": "The per-layer write discipline table — what auto-writes, what's draft-then-approve, what's user-only — and which lines are hook-enforced vs guidance.",
        "drift": True,
        "reason": "Authored content. Every row in the table is a judgment call. Updated in S004: lorebook collapsed to a single row with the identity-layer pattern (drafts/confirmed/archive/rejected) since the layer was redefined as a self-improvement log. Verify the new lorebook row matches the redefinition.",
    },
    "meta/modes.md": {
        "purpose": "Documents the two orthogonal axes of agent behavior — session mode (player/unscoped/bankstanding) and role (principal/dwarf) — with the dwarf write boundary and cross-player invocation rules.",
        "drift": True,
        "reason": "Substantially rewritten in S004 to add the three-session-modes axis (player/unscoped/bankstanding) at the top, orthogonal to principal/dwarf. The dwarf write surface was also updated — lorebook/patch-notes.md removed from the allow-list (since patch-notes.md no longer exists), with explicit note that lorebook is principal-only. Confirm the three-session-modes framing matches your intent; particularly that bankstanding is its own mode (not a player-mode or unscoped-mode variant).",
    },
    "meta/archive-discipline.md": {
        "purpose": "The never-delete rule — explains why archive/ exists, what archive/ vs rejected/ mean, and how moves preserve relative paths.",
        "drift": True,
        "reason": "Authored content. The three reasons (recoverability, pattern memory, trust) and the archive/rejected distinction are the builder's framing — verify both. The 'append timestamp on collision' rule is a specific operational choice that may need different handling.",
    },
    "meta/drafts-mechanics.md": {
        "purpose": "The drafts → confirmed → archive/rejected flow, including the observation rule (drafts must be observation-backed, not aspirational).",
        "drift": True,
        "reason": "Authored content. The observation rule and the 'bad/good' example are interpretive — confirm that's the gate you want on identity-layer writes. The '/drafts' command is deferred to real use; check whether you want the agent surfacing drafts at session start (the builder said no — only on /drafts, bankstanding, or when blocking an action).",
    },
    "meta/death-and-spawn.md": {
        "purpose": "Crash recovery + reset behavior — defines which layers persist across reset, the reconciliation prompt, and the deferred 'ascension' migration.",
        "drift": True,
        "reason": "Authored content. The persist-across-reset table is the load-bearing part — every row is a judgment call (which layers are durable, which are volatile). Especially check the 'principal's choice' rows for quest-log/in-progress/ and the body files.",
    },

    # spellbook/ global
    "spellbook/_about.md": {
        "purpose": "Layer card for global spellbook/ — distinguishes rituals (principal-owned procedures) from skills (cross-player capabilities).",
        "drift": True,
        "reason": "_about framing. The 'rituals are user-only by discipline, not hook-enforced' choice is one to verify — the builder flagged a Phase 2 hook for this would be reasonable but didn't add it.",
    },
    "spellbook/rituals/respawn.md": {
        "purpose": "Canonical session-start procedure — the load order the agent follows on respawn and the mini-respawn on mid-session player switch.",
        "drift": True,
        "reason": "Load order is canonical and must be exactly right. Updated in S004: step 6 removed (the old 'read lorebook/assumptions.md' step is gone since assumptions.md was moved out), so the per-player scope is now step 6 (was 7). Reconciliation prompt section was tightened — three explicit options including 'reconcile the pending action externally first' (verifying side-effects on the outside world before resuming), and an explicit 'do not auto-resume' rule. Verify the new reconciliation flow.",
    },
    "spellbook/rituals/bankstanding.md": {
        "purpose": "Canonical bankstanding-mode procedure — the cross-cutting reorganization ritual where the agent operates as the system tending its own brain, not as a character.",
        "drift": True,
        "reason": "Rewritten in S004. Two big changes: (1) bankstanding now framed as a distinct session mode with explicit cross-cutting reach (reads every layer across all players). (2) New step 3 added — cross-player synthesis, where patterns confirmed in multiple per-player layers get proposed for graduation to the global layer. Old steps 7-8 (update assumptions, append to patch-notes) removed since those files no longer exist; replaced with 'if anything in this round changed how the agent operates, log it in lorebook/drafts/.' Verify the 8-step sequence and the explicit mode-framing in the opening sections.",
    },

    # examine/
    "examine/_about.md": {
        "purpose": "Layer card for global examine/ — agent-system self-model layer; defines what goes here vs per-player examine/ vs niksis8/.",
        "drift": True,
        "reason": "_about framing. Boundary between global examine/ (system patterns) and per-player examine/ (character patterns) is interpretive — verify it matches your model of where self-observations land.",
    },
    "examine/confirmed/current.md": {
        "purpose": "Identity-layer read target — the rolling, in-force agent-system self-model loaded at respawn (step 4).",
        "drift": False,
    },

    # niksis8/
    "niksis8/_about.md": {
        "purpose": "Layer card for global niksis8/ — user-model layer; defines what universal Niklavs facts go here vs per-player niksis8_character/.",
        "drift": True,
        "reason": "_about framing. The seed ('My name is Niklavs.') and the 'don't front-load facts the agent should be earning' principle are interpretive choices — confirm both, especially the discipline against pre-loading bio facts.",
    },
    "niksis8/confirmed/current.md": {
        "purpose": "Identity-layer read target — the universal-facts-about-Niklavs file loaded at respawn (step 5). Seeded with one line.",
        "drift": False,
    },

    # keepsake/
    "keepsake/_about.md": {
        "purpose": "Layer card for global keepsake/ — always-surface-pins layer; defines the pinning vs proposing flow and the ~2k size budget.",
        "drift": True,
        "reason": "_about framing. 'Small handful, not a long list' is a discipline choice — confirm the size budget (~2k) and the proposals-vs-current.md flow are what you want.",
    },
    "keepsake/current.md": {
        "purpose": "Identity-layer read target — global pins loaded at respawn (step 3, before identity layers).",
        "drift": False,
    },

    # lorebook/
    "lorebook/_about.md": {
        "purpose": "Layer card for global lorebook/ — the agent's self-improvement log; defines what counts as a self-improvement entry, the entry format, and the boundary against construction history (which lives in the dev brain).",
        "drift": True,
        "reason": "Rewritten in S004. The lorebook was redefined from 'build log with decisions/assumptions/patch-notes' to 'self-improvement log only.' Verify the new framing ('decided by the agent, about itself, during bankstanding or reflection') matches your intent. Verify the entry shape (what changed / why / what triggered it / what was affected / supersedes-by) is right. The 'append-only' rule and the rejected-drafts-are-data section are deliberate choices to verify.",
    },

    # players/ system
    "players/_about.md": {
        "purpose": "System card for players/ — defines the player-template, the global-vs-per-player layer split, the initial roster (Zezima, Jebrim), the address-based invocation rule, and the cross-player dwarf flow.",
        "drift": True,
        "reason": "_about framing AND a system-level operational document. Updated in S004: 'How to invoke a player' section rewritten to match the address-based model (was previously describing a preemptive prompt). The cross-player dwarf section was strengthened to enumerate trigger phrases ('ask {name} to ...', 'have {name} ...', etc.). Verify both sections match how you actually want invocation to work.",
    },
    "players/inbox/_about.md": {
        "purpose": "System card for the unscoped-writes holding pen — defines when to write here, the bankstanding triage flow, and the ~4-week age limit.",
        "drift": True,
        "reason": "_about framing. The 'default bias: write to active player and let bankstanding re-route' rule and the ~4-week age limit are discipline choices — confirm both.",
    },

    # Jebrim
    "players/jebrim/_about.md": {
        "purpose": "Character card for Jebrim — names domain (work / focused analytical execution), source repos, and the bank-grows-from-real-use discipline.",
        "drift": True,
        "reason": "Character framing is interpretive. The 'Jebrim as the Agility-grinder register' metaphor, the work-vs-Zezima split, and the explicit naming of source repos (bi-analytics-main/NFE/, bi-etl/) are the builder's choices. Confirm those repo paths are still accurate and that the work-vs-personal split matches how you actually delegate.",
    },
    "players/jebrim/persona.md": {
        "purpose": "Jebrim's voice spec — register, length, voice cues, what he avoids.",
        "drift": True,
        "reason": "Character framing is interpretive. The 'analytical, terse, outcome-oriented' register and the specific voice cues (name deliverable first, smallest unblocking question, cite source paths) shape how the agent will sound when scoped to Jebrim. The persona disclaimer ('Develops through use. Don't front-load voice details that haven't been earned.') is itself a judgment call — verify that's the discipline you want.",
    },
    "players/jebrim/CLAUDE.md": {
        "purpose": "Per-player session entry for Jebrim — imports _about.md and persona.md, restates in-scope/out-of-scope and register.",
        "drift": True,
        "reason": "Tone choices. The 'suggest invoking Zezima as a player switch or as a dwarf' instruction for out-of-scope tasks is a routing decision worth verifying. Also: the file restates content already in _about.md/persona.md (which it then imports) — confirm that restatement is intentional, not accidental duplication.",
    },
    "players/jebrim/bank/_about.md": {
        "purpose": "Layer card for Jebrim's semantic memory — defines bank-grows-from-real-repos, source-path discipline, and the contradiction-handling rule.",
        "drift": True,
        "reason": "_about framing. The 'every note links back to source path' discipline and the explicit naming of bi-analytics-main/NFE/ and bi-etl/ as source repos are interpretive. Confirm both.",
    },
    "players/jebrim/examine/_about.md": {
        "purpose": "Layer card for Jebrim's per-character self-knowledge — distinguishes from gielinor/examine/ (system-level).",
        "drift": True,
        "reason": "_about framing — same boundary call as the global examine/_about.md, applied per-player.",
    },
    "players/jebrim/examine/confirmed/current.md": {
        "purpose": "Identity-layer read target — loaded at respawn when Jebrim is active (step 7e).",
        "drift": False,
    },
    "players/jebrim/inventory/_about.md": {
        "purpose": "Layer card for Jebrim's working memory — volatile, session-scoped; defines the promote-to-bank-or-drop discipline.",
        "drift": True,
        "reason": "_about framing. The 'if it crosses two sessions, promote to bank' threshold is a discipline call.",
    },
    "players/jebrim/keepsake/_about.md": {
        "purpose": "Layer card for Jebrim's player-scoped pins — items that always surface when Jebrim is active.",
        "drift": True,
        "reason": "_about framing — applies the global-keepsake principle (small, intentional) per-player.",
    },
    "players/jebrim/keepsake/current.md": {
        "purpose": "Identity-layer read target — Jebrim's pins, loaded at respawn when Jebrim is active (step 7d).",
        "drift": False,
    },
    "players/jebrim/niksis8_character/_about.md": {
        "purpose": "Layer card for Jebrim's per-character model of Niklavs — what Jebrim knows about Niklavs through the work lens.",
        "drift": True,
        "reason": "_about framing. The 'work-register view of Niklavs' framing is interpretive — confirm it's the right slicing of user-model knowledge.",
    },
    "players/jebrim/niksis8_character/confirmed/current.md": {
        "purpose": "Identity-layer read target — loaded at respawn when Jebrim is active (step 7f).",
        "drift": False,
    },
    "players/jebrim/quest-log/_about.md": {
        "purpose": "Layer card for Jebrim's episodic memory — defines the every-turn-append discipline and the pending/completed/failed action markers.",
        "drift": True,
        "reason": "_about framing AND load-bearing operational rules. The 'every turn' append rule and the pending-marker discipline are the crash-recovery substrate (see meta/death-and-spawn.md). Confirm the discipline is right.",
    },
    "players/jebrim/spellbook/_about.md": {
        "purpose": "Layer card for Jebrim's procedural memory — distinguishes skills (procedures) from rituals (rare, character-specific).",
        "drift": True,
        "reason": "_about framing. The 'don't write speculative skills; propose them after the procedure has happened a few times' discipline is a judgment call worth verifying.",
    },

    # Zezima
    "players/zezima/_about.md": {
        "purpose": "Character card for Zezima — names domain (personal life / reading / reflection) and the slow-synthesis register.",
        "drift": True,
        "reason": "Character framing is interpretive. The 'Zezima as the legendary-player register' metaphor (patience, depth, long horizons) and the personal-vs-work split are the builder's choices.",
    },
    "players/zezima/persona.md": {
        "purpose": "Zezima's voice spec — register, length, voice cues, what he avoids.",
        "drift": True,
        "reason": "Character framing is interpretive. The 'reflective, unhurried, comfortable with not-knowing' register and the cues (paragraphs over bullets, name ambivalence, don't perform productivity) shape how the agent will sound when scoped to Zezima.",
    },
    "players/zezima/CLAUDE.md": {
        "purpose": "Per-player session entry for Zezima — imports _about.md and persona.md, restates in-scope/out-of-scope and register.",
        "drift": True,
        "reason": "Tone choices and routing. The 'suggest invoking Jebrim as a player switch or as a dwarf' instruction for work-flavored tasks is the symmetric routing decision worth verifying.",
    },
    "players/zezima/bank/_about.md": {
        "purpose": "Layer card for Zezima's semantic memory — defines what knowledge accumulates (reading notes, cross-source synthesis, reflection-derived patterns).",
        "drift": True,
        "reason": "_about framing. The 'no pre-imposed taxonomy in notes/' choice is a structure decision — confirm you want notes/ free-form vs subdivided.",
    },
    "players/zezima/examine/_about.md": {
        "purpose": "Layer card for Zezima's per-character self-knowledge — distinguishes from gielinor/examine/ (system-level).",
        "drift": True,
        "reason": "_about framing — same boundary call as the global examine/_about.md, applied per-player.",
    },
    "players/zezima/examine/confirmed/current.md": {
        "purpose": "Identity-layer read target — loaded at respawn when Zezima is active (step 7e).",
        "drift": False,
    },
    "players/zezima/inventory/_about.md": {
        "purpose": "Layer card for Zezima's working memory — volatile, session-scoped; defines the don't-let-accumulate discipline.",
        "drift": True,
        "reason": "_about framing. The 'if you don't look at it each turn, it doesn't belong here' rule is a working-memory discipline call.",
    },
    "players/zezima/keepsake/_about.md": {
        "purpose": "Layer card for Zezima's player-scoped pins — items that always surface when Zezima is active.",
        "drift": True,
        "reason": "_about framing — applies the global-keepsake principle (small, intentional) per-player.",
    },
    "players/zezima/keepsake/current.md": {
        "purpose": "Identity-layer read target — Zezima's pins, loaded at respawn when Zezima is active (step 7d).",
        "drift": False,
    },
    "players/zezima/niksis8_character/_about.md": {
        "purpose": "Layer card for Zezima's per-character model of Niklavs — what Zezima knows about Niklavs through the reflective lens.",
        "drift": True,
        "reason": "_about framing. The 'reflective-register view of Niklavs' framing is interpretive — confirm it's the right slicing of user-model knowledge.",
    },
    "players/zezima/niksis8_character/confirmed/current.md": {
        "purpose": "Identity-layer read target — loaded at respawn when Zezima is active (step 7f).",
        "drift": False,
    },
    "players/zezima/quest-log/_about.md": {
        "purpose": "Layer card for Zezima's episodic memory — defines the every-turn-append discipline and the pending/completed/failed action markers.",
        "drift": True,
        "reason": "_about framing AND load-bearing operational rules — same crash-recovery substrate as Jebrim's quest-log. Confirm the discipline is right; mirror-content with Jebrim's version is intentional.",
    },
    "players/zezima/spellbook/_about.md": {
        "purpose": "Layer card for Zezima's procedural memory — distinguishes skills (procedures) from rituals (rare, character-specific).",
        "drift": True,
        "reason": "_about framing — mirrors Jebrim's spellbook/_about.md. Confirm the 'don't write speculative skills' discipline.",
    },
}


# ---------------------------------------------------------------------------
# Ordered groups of load-bearing files for the linear "File Contents" section.
# Per the iteration spec: skip empty folders' contents, include every load-bearing
# file verbatim in this order.
# ---------------------------------------------------------------------------

CONTENT_GROUPS: list[tuple[str, list[str]]] = [
    ("Body — gielinor root", [
        "CLAUDE.md",
        "CLAUDE.local.md",
        "ticks.md",
        ".mcp.json",
    ]),
    ("Hooks — .claude/", [
        ".claude/settings.json",
        ".claude/hooks/block-confirmed-writes.py",
        ".claude/hooks/block-deletes.py",
        ".claude/hooks/dwarf-write-boundary.py",
        ".claude/hooks/block-sub-dwarf-spawn.py",
    ]),
    ("Meta — current rulebook", [
        "meta/_about.md",
        "meta/write-rules.md",
        "meta/modes.md",
        "meta/drafts-mechanics.md",
        "meta/archive-discipline.md",
        "meta/death-and-spawn.md",
    ]),
    ("Global layer — examine/", [
        "examine/_about.md",
        "examine/confirmed/current.md",
    ]),
    ("Global layer — niksis8/", [
        "niksis8/_about.md",
        "niksis8/confirmed/current.md",
    ]),
    ("Global layer — keepsake/", [
        "keepsake/_about.md",
        "keepsake/current.md",
    ]),
    ("Global layer — lorebook/", [
        "lorebook/_about.md",
    ]),
    ("Global layer — spellbook/ + rituals", [
        "spellbook/_about.md",
        "spellbook/rituals/respawn.md",
        "spellbook/rituals/bankstanding.md",
    ]),
    ("Players — system", [
        "players/_about.md",
        "players/inbox/_about.md",
    ]),
    ("Player — jebrim", [
        "players/jebrim/CLAUDE.md",
        "players/jebrim/_about.md",
        "players/jebrim/persona.md",
        "players/jebrim/bank/_about.md",
        "players/jebrim/quest-log/_about.md",
        "players/jebrim/spellbook/_about.md",
        "players/jebrim/inventory/_about.md",
        "players/jebrim/examine/_about.md",
        "players/jebrim/examine/confirmed/current.md",
        "players/jebrim/niksis8_character/_about.md",
        "players/jebrim/niksis8_character/confirmed/current.md",
        "players/jebrim/keepsake/_about.md",
        "players/jebrim/keepsake/current.md",
    ]),
    ("Player — zezima", [
        "players/zezima/CLAUDE.md",
        "players/zezima/_about.md",
        "players/zezima/persona.md",
        "players/zezima/bank/_about.md",
        "players/zezima/quest-log/_about.md",
        "players/zezima/spellbook/_about.md",
        "players/zezima/inventory/_about.md",
        "players/zezima/examine/_about.md",
        "players/zezima/examine/confirmed/current.md",
        "players/zezima/niksis8_character/_about.md",
        "players/zezima/niksis8_character/confirmed/current.md",
        "players/zezima/keepsake/_about.md",
        "players/zezima/keepsake/current.md",
    ]),
]


# ---------------------------------------------------------------------------
# Walk gielinor/ and build the catalogue.
# ---------------------------------------------------------------------------

def is_gitkeep(p: Path) -> bool:
    return p.name == ".gitkeep"


def walk_gielinor() -> tuple[dict[str, dict], dict[str, list[str]]]:
    """Return (files, dir_children).

    files: { relpath: { content, purpose, drift, reason, ext } }
    dir_children: { dir_relpath_or_empty_string: [child_name, ...] (subdirs first, then files, alpha) }
    """
    files: dict[str, dict] = {}
    dirs: dict[str, set[str]] = {}

    for path in GIELINOR.rglob("*"):
        rel = path.relative_to(GIELINOR).as_posix()
        parent = path.parent.relative_to(GIELINOR).as_posix()
        if parent == ".":
            parent = ""
        dirs.setdefault(parent, set()).add(path.name)
        if path.is_dir():
            dirs.setdefault(rel, set())
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_bytes().decode("utf-8", errors="replace")
        meta = META.get(rel, {})
        # Files that aren't in META get a generic purpose
        if not meta:
            if is_gitkeep(path):
                meta = {
                    "purpose": "Empty directory marker — keeps the empty scaffolding folder in git so structure survives clones.",
                    "drift": False,
                }
            else:
                meta = {
                    "purpose": "(unannotated — file was created during scaffolding but isn't in the audit's annotation set; review manually)",
                    "drift": False,
                }
        files[rel] = {
            "content": content,
            "purpose": meta["purpose"],
            "drift": bool(meta.get("drift")),
            "reason": meta.get("reason", ""),
            "ext": path.suffix.lower(),
            "name": path.name,
        }

    # Sort children: directories first (alpha), then files (alpha)
    dir_children: dict[str, list[str]] = {}
    for d, names in dirs.items():
        children = []
        d_path = GIELINOR / d if d else GIELINOR
        subdirs = sorted([n for n in names if (d_path / n).is_dir()])
        subfiles = sorted([n for n in names if (d_path / n).is_file()])
        children = subdirs + subfiles
        dir_children[d] = children

    return files, dir_children


# ---------------------------------------------------------------------------
# HTML assembly.
# ---------------------------------------------------------------------------

CSS = r"""
:root {
  --bg: #0e1116;
  --bg-elev: #161b22;
  --bg-hover: #1f262e;
  --border: #2a313b;
  --fg: #c9d1d9;
  --fg-dim: #8b949e;
  --fg-mute: #6e7681;
  --accent: #79b8ff;
  --accent-2: #f0883e;
  --drift: #d29922;
  --drift-bg: #2d2208;
  --green: #56d364;
  --red: #f85149;
  --code-bg: #0a0d12;
  --kw: #ff7b72;
  --str: #a5d6a7;
  --com: #6e7681;
  --num: #ffa657;
  --punct: #c9d1d9;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--fg); }
body {
  font-family: ui-monospace, "JetBrains Mono", "Fira Code", Consolas, "Cascadia Mono", monospace;
  font-size: 13px;
  line-height: 1.45;
}
.app { display: flex; height: 100vh; }
.sidebar {
  width: 360px;
  min-width: 240px;
  max-width: 600px;
  background: var(--bg-elev);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  overflow-x: auto;
  padding: 12px 0;
  flex-shrink: 0;
  position: relative;
}
.sidebar-resize {
  position: absolute;
  top: 0; right: -3px;
  width: 6px; height: 100%;
  cursor: col-resize;
  background: transparent;
  z-index: 5;
}
.sidebar-resize:hover { background: var(--accent); opacity: 0.4; }

.brand {
  padding: 0 14px 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.brand h1 {
  font-size: 12px;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--fg-dim);
  font-weight: 600;
}
.brand .sub {
  font-size: 11px;
  color: var(--fg-mute);
  margin-top: 2px;
}

.tree { padding: 4px 0; }
.tree .row {
  padding: 2px 8px 2px 0;
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tree .row:hover { background: var(--bg-hover); }
.tree .row.active { background: var(--bg-hover); color: var(--accent); }
.tree .row .caret { width: 12px; display: inline-block; color: var(--fg-mute); text-align: center; }
.tree .row .name { flex: 1; overflow: hidden; text-overflow: ellipsis; }
.tree .row .badge {
  background: var(--drift);
  color: var(--bg);
  padding: 0 4px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  margin-left: 4px;
}
.tree .dir > .name { color: var(--fg); font-weight: 600; }
.tree .file > .name { color: var(--fg-dim); }
.tree .file.has-drift > .name { color: var(--drift); }
.tree .children { display: none; }
.tree .row.open + .children { display: block; }

.main {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px 80px;
  min-width: 0;
}
.path-bar {
  font-size: 11px;
  color: var(--fg-mute);
  margin-bottom: 8px;
  word-break: break-all;
}
.path-bar code { background: var(--bg-elev); padding: 2px 5px; border-radius: 3px; }
.file-head {
  border-bottom: 1px solid var(--border);
  padding-bottom: 14px;
  margin-bottom: 18px;
}
.file-head h1 {
  font-size: 18px;
  margin: 0 0 6px 0;
  font-weight: 700;
  color: var(--fg);
}
.purpose {
  background: var(--bg-elev);
  border-left: 3px solid var(--accent);
  padding: 10px 12px;
  margin: 8px 0;
  font-size: 13px;
  color: var(--fg);
}
.purpose .label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--accent);
  display: block;
  margin-bottom: 4px;
  font-weight: 700;
}
.drift {
  background: var(--drift-bg);
  border-left: 3px solid var(--drift);
  padding: 10px 12px;
  margin: 8px 0;
  font-size: 13px;
}
.drift .label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--drift);
  display: block;
  margin-bottom: 4px;
  font-weight: 700;
}
.section-head {
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--fg-mute);
  font-size: 10px;
  margin: 24px 0 8px;
  font-weight: 700;
}

/* Markdown rendering */
.md h1, .md h2, .md h3, .md h4 {
  font-family: ui-monospace, Consolas, monospace;
  color: var(--fg);
  margin: 16px 0 8px;
  font-weight: 700;
}
.md h1 { font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
.md h2 { font-size: 15px; }
.md h3 { font-size: 13px; color: var(--accent); }
.md h4 { font-size: 13px; color: var(--fg-dim); }
.md p { margin: 6px 0; }
.md ul, .md ol { margin: 6px 0; padding-left: 22px; }
.md li { margin: 2px 0; }
.md blockquote {
  border-left: 3px solid var(--fg-mute);
  margin: 8px 0;
  padding: 4px 12px;
  color: var(--fg-dim);
  background: var(--bg-elev);
}
.md code {
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  color: var(--accent-2);
}
.md pre {
  background: var(--code-bg);
  padding: 10px 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  border: 1px solid var(--border);
}
.md pre code { background: transparent; padding: 0; color: var(--fg); }
.md table { border-collapse: collapse; margin: 8px 0; }
.md th, .md td {
  border: 1px solid var(--border);
  padding: 4px 8px;
  text-align: left;
  font-size: 12px;
}
.md th { background: var(--bg-elev); color: var(--fg); }
.md a { color: var(--accent); text-decoration: none; }
.md a:hover { text-decoration: underline; }
.md hr { border: 0; border-top: 1px solid var(--border); margin: 12px 0; }
.md strong { color: var(--fg); }
.md em { color: var(--fg-dim); font-style: italic; }
.xref { color: var(--accent-2); cursor: pointer; }
.xref:hover { text-decoration: underline; }
.xref.unresolved { color: var(--fg-mute); cursor: help; }

/* Raw view */
.raw-toggle {
  display: inline-block;
  font-size: 10px;
  color: var(--fg-mute);
  text-transform: uppercase;
  letter-spacing: 1.2px;
  cursor: pointer;
  padding: 2px 6px;
  border: 1px solid var(--border);
  border-radius: 3px;
  margin-left: 8px;
}
.raw-toggle:hover { color: var(--accent); border-color: var(--accent); }
.raw-toggle.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
pre.raw {
  background: var(--code-bg);
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid var(--border);
  overflow-x: auto;
  font-size: 12px;
  white-space: pre;
  margin: 8px 0;
}

/* Landing */
.landing h1 { font-size: 22px; margin: 0 0 6px 0; }
.landing .lede { color: var(--fg-dim); margin-bottom: 18px; max-width: 720px; }
.diagram {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 18px;
  margin: 12px 0;
  overflow-x: auto;
}
.diagram pre {
  margin: 0;
  font-size: 12px;
  color: var(--fg);
  white-space: pre;
}
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin: 12px 0;
}
.card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px;
}
.card .num {
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
}
.card .label {
  font-size: 10px;
  color: var(--fg-mute);
  text-transform: uppercase;
  letter-spacing: 1.4px;
}
.start-list { margin: 8px 0 0 0; padding: 0; list-style: none; }
.start-list li {
  padding: 8px 10px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 3px;
  margin: 6px 0;
}
.start-list .ord {
  display: inline-block;
  background: var(--accent);
  color: var(--bg);
  width: 18px;
  height: 18px;
  text-align: center;
  border-radius: 3px;
  font-weight: 700;
  font-size: 11px;
  line-height: 18px;
  margin-right: 8px;
}
.start-list a { color: var(--accent); }
.start-list .why { color: var(--fg-mute); font-size: 11px; margin-top: 4px; }

.kbd {
  font-family: inherit;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-bottom-width: 2px;
  border-radius: 3px;
  padding: 1px 5px;
  font-size: 11px;
  color: var(--fg-dim);
}

/* Linear "File Contents" section */
.contents-section-head {
  font-size: 20px;
  margin: 8px 0 4px;
  color: var(--fg);
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
}
.contents-toc {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0 24px;
}
.contents-toc-head {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--fg-mute);
  margin-bottom: 8px;
  font-weight: 700;
}
.contents-toc ul {
  margin: 0; padding: 0; list-style: none;
  column-count: 2;
  column-gap: 24px;
}
.contents-toc li {
  padding: 3px 0;
  font-size: 12px;
  break-inside: avoid;
}
.contents-toc a { color: var(--accent); text-decoration: none; }
.contents-toc a:hover { text-decoration: underline; }
.contents-toc-count {
  display: inline-block;
  color: var(--fg-mute);
  margin-left: 4px;
  font-size: 11px;
}
.contents-group-head {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--accent);
  margin: 32px 0 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
  font-weight: 700;
}
.contents-file {
  margin: 16px 0 24px;
  padding: 0;
}
.contents-file h3 {
  font-size: 13px;
  font-weight: 700;
  color: var(--fg);
  margin: 0 0 6px;
  background: var(--bg-elev);
  padding: 6px 10px;
  border-radius: 3px;
  border-left: 3px solid var(--accent);
  word-break: break-all;
}
.contents-file.missing h3 { border-left-color: var(--red); }
.contents-missing {
  color: var(--red);
  padding: 6px 10px;
  font-size: 12px;
}
.contents-badge {
  background: var(--drift);
  color: var(--bg);
  padding: 0 5px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  margin-left: 8px;
  vertical-align: middle;
}
.contents-purpose {
  font-size: 12px;
  color: var(--fg-dim);
  margin: 4px 0 6px;
  padding: 0 4px;
}
.contents-purpose .label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--accent);
  font-weight: 700;
  margin-right: 6px;
}
.contents-drift { margin: 4px 0 8px; font-size: 12px; }
.contents-raw {
  margin: 4px 0 0;
  max-height: 600px;
  overflow: auto;
}
.home-btn {
  display: block;
  margin: 0 14px 8px;
  padding: 5px 8px;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--fg);
  font-size: 11px;
  cursor: pointer;
  text-align: center;
  font-family: inherit;
  width: calc(100% - 28px);
}
.home-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--fg-mute); }
"""

JS = r"""
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const DATA = window.__GIELINOR__;
let currentPath = null;
let rawMode = false;

// ---- Tree ----
function buildTree(dir, container, depth) {
  const children = DATA.dirs[dir] || [];
  for (const name of children) {
    const childPath = dir ? `${dir}/${name}` : name;
    const isDir = DATA.dirs[childPath] !== undefined;
    if (isDir) {
      const row = document.createElement('div');
      row.className = 'row dir';
      row.dataset.dir = childPath;
      row.style.paddingLeft = (8 + depth * 12) + 'px';
      row.innerHTML = `<span class="caret">▸</span><span class="name">${escapeHtml(name)}/</span>`;
      row.addEventListener('click', (e) => {
        e.stopPropagation();
        row.classList.toggle('open');
        const caret = row.querySelector('.caret');
        caret.textContent = row.classList.contains('open') ? '▾' : '▸';
      });
      container.appendChild(row);
      const wrap = document.createElement('div');
      wrap.className = 'children';
      container.appendChild(wrap);
      buildTree(childPath, wrap, depth + 1);
    } else {
      const meta = DATA.files[childPath];
      const row = document.createElement('div');
      row.className = 'row file' + (meta.drift ? ' has-drift' : '');
      row.dataset.path = childPath;
      row.style.paddingLeft = (8 + depth * 12 + 14) + 'px';
      const badge = meta.drift ? '<span class="badge">DRIFT</span>' : '';
      row.innerHTML = `<span class="name">${escapeHtml(name)}</span>${badge}`;
      row.addEventListener('click', (e) => {
        e.stopPropagation();
        openFile(childPath);
      });
      container.appendChild(row);
    }
  }
}

function expandToPath(path) {
  const parts = path.split('/');
  let cur = '';
  for (let i = 0; i < parts.length - 1; i++) {
    cur = cur ? `${cur}/${parts[i]}` : parts[i];
    const row = $(`.tree .row.dir[data-dir="${cssEscape(cur)}"]`);
    if (row && !row.classList.contains('open')) {
      row.classList.add('open');
      const caret = row.querySelector('.caret');
      if (caret) caret.textContent = '▾';
    }
  }
}

function cssEscape(s) { return s.replace(/"/g, '\\"'); }

// ---- File view ----
function openFile(path) {
  currentPath = path;
  rawMode = false;
  $$('.tree .row.active').forEach(r => r.classList.remove('active'));
  const row = $(`.tree .row.file[data-path="${cssEscape(path)}"]`);
  if (row) {
    row.classList.add('active');
    row.scrollIntoView({ block: 'nearest' });
  }
  expandToPath(path);
  renderFile(path);
}

function renderFile(path) {
  const meta = DATA.files[path];
  if (!meta) {
    renderLanding();
    return;
  }
  const drift = meta.drift ? `
    <div class="drift">
      <span class="label">⚑ Drift flag</span>
      <div>${escapeHtml(meta.reason)}</div>
    </div>` : '';

  const ext = meta.ext;
  let contentHtml;
  if (rawMode || ext === '.json' || ext === '.py') {
    contentHtml = renderCode(meta.content, ext);
  } else if (ext === '.md') {
    contentHtml = `<div class="md">${renderMarkdown(meta.content)}</div>`;
  } else {
    contentHtml = renderCode(meta.content, ext);
  }

  const toggle = (ext === '.md')
    ? `<span class="raw-toggle ${rawMode ? 'active' : ''}" id="raw-toggle">${rawMode ? 'rendered' : 'raw'}</span>`
    : '';

  const main = $('#main');
  main.innerHTML = `
    <div class="path-bar"><code>gielinor/${escapeHtml(path)}</code></div>
    <div class="file-head">
      <h1>${escapeHtml(meta.name)}${toggle}</h1>
    </div>
    <div class="purpose">
      <span class="label">Purpose</span>
      <div>${escapeHtml(meta.purpose)}</div>
    </div>
    ${drift}
    <div class="section-head">File contents</div>
    ${contentHtml}
  `;
  if (ext === '.md') {
    const t = $('#raw-toggle');
    if (t) t.addEventListener('click', () => { rawMode = !rawMode; renderFile(path); });
  }
  // Wire xref clicks
  $$('.xref').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const target = a.dataset.target;
      if (target && DATA.files[target]) {
        openFile(target);
      }
    });
  });
  main.scrollTop = 0;
}

// ---- Markdown rendering (lightweight) ----
function renderMarkdown(src) {
  // Pull out fenced code blocks first, replace with placeholders.
  const blocks = [];
  src = src.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => {
    const i = blocks.length;
    blocks.push({ lang, code });
    return `\x00CODE${i}\x00`;
  });

  // Tables (very simple).
  src = src.replace(/((?:^\|.+\|\s*$\n?)+)/gm, (m) => {
    const lines = m.trim().split('\n').map(l => l.trim());
    if (lines.length < 2) return m;
    const sep = lines[1];
    if (!/^\|[\s\-:|]+\|$/.test(sep)) return m;
    const header = lines[0].slice(1, -1).split('|').map(c => c.trim());
    const rows = lines.slice(2).map(l => l.slice(1, -1).split('|').map(c => c.trim()));
    let html = '<table><thead><tr>' + header.map(h => `<th>${inlineMd(h)}</th>`).join('') + '</tr></thead><tbody>';
    rows.forEach(r => {
      html += '<tr>' + r.map(c => `<td>${inlineMd(c)}</td>`).join('') + '</tr>';
    });
    html += '</tbody></table>';
    return html;
  });

  // Split into block-level units by blank lines (preserving table HTML).
  const lines = src.split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // Headings
    const hm = /^(#{1,6})\s+(.*)$/.exec(line);
    if (hm) {
      const lvl = hm[1].length;
      out.push(`<h${lvl}>${inlineMd(hm[2])}</h${lvl}>`);
      i++;
      continue;
    }
    // HR
    if (/^---+\s*$/.test(line) || /^\*\*\*\s*$/.test(line)) {
      out.push('<hr>');
      i++;
      continue;
    }
    // Already-HTML (e.g. tables we replaced)
    if (/^\s*<(table|thead|tbody|tr|h\d|p|ul|ol|li|hr|blockquote|pre)/i.test(line)) {
      out.push(line);
      i++;
      continue;
    }
    // Blockquote
    if (/^>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        buf.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      out.push(`<blockquote>${renderMarkdown(buf.join('\n'))}</blockquote>`);
      continue;
    }
    // Lists
    if (/^\s*[-*]\s+/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        buf.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i++;
        // continuation lines (indented)
        while (i < lines.length && /^\s{2,}\S/.test(lines[i])) {
          buf[buf.length - 1] += ' ' + lines[i].trim();
          i++;
        }
      }
      out.push('<ul>' + buf.map(li => `<li>${inlineMd(li)}</li>`).join('') + '</ul>');
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        buf.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i])) {
          buf[buf.length - 1] += ' ' + lines[i].trim();
          i++;
        }
      }
      out.push('<ol>' + buf.map(li => `<li>${inlineMd(li)}</li>`).join('') + '</ol>');
      continue;
    }
    // Frontmatter delimiter (---) is HR above; YAML lines as paragraphs
    // Blank
    if (/^\s*$/.test(line)) { i++; continue; }
    // Paragraph
    const buf = [line];
    i++;
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,6})\s/.test(lines[i]) && !/^>\s?/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i]) && !/^\s*<(table|thead|tbody|tr|h\d|p|ul|ol|li|hr|blockquote|pre)/i.test(lines[i])) {
      buf.push(lines[i]);
      i++;
    }
    out.push(`<p>${inlineMd(buf.join(' '))}</p>`);
  }

  let html = out.join('\n');
  // Restore code blocks with syntax highlighting if lang known
  html = html.replace(/\x00CODE(\d+)\x00/g, (m, idx) => {
    const blk = blocks[parseInt(idx, 10)];
    const code = highlightCode(blk.code, blk.lang ? '.' + blk.lang : '');
    return `<pre><code>${code}</code></pre>`;
  });
  return html;
}

function inlineMd(s) {
  // Escape first, then re-introduce known tokens.
  s = escapeHtml(s);
  // Inline code `x`
  s = s.replace(/`([^`]+)`/g, (m, c) => `<code>${c}</code>`);
  // Wiki-links [[X]] (may include dashes, slashes, digits)
  s = s.replace(/\[\[([^\]]+)\]\]/g, (m, target) => {
    return resolveXref(target, target);
  });
  // Links [text](url)
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, text, url) => {
    if (/^https?:/.test(url)) {
      return `<a href="${url}" target="_blank" rel="noopener">${text}</a>`;
    }
    return resolveXref(url, text);
  });
  // Bold **x**
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italics *x* (but not **)
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  // Path references like `gielinor/...` or `meta/...` — best-effort linkify when not already in code/anchor
  return s;
}

function resolveXref(target, text) {
  // Target can be: D-NNN, S-NNN, plan, path like meta/foo.md, .claude/hooks/xxx.py
  // Try to resolve to a file in DATA.files.
  let resolved = null;

  // Strip @ prefix used by Claude Code imports.
  let t = target.replace(/^@/, '');

  // Direct file match
  if (DATA.files[t]) {
    resolved = t;
  } else if (DATA.files[t + '.md']) {
    resolved = t + '.md';
  } else {
    // D-NNN slug match against lorebook/decisions/
    const dMatch = /^D-(\d+)/.exec(t);
    if (dMatch) {
      const key = Object.keys(DATA.files).find(k => k.startsWith(`lorebook/decisions/D-${dMatch[1]}_`));
      if (key) resolved = key;
    }
  }

  if (resolved) {
    return `<a class="xref" data-target="${escapeHtml(resolved)}" href="#${escapeHtml(resolved)}">${escapeHtml(text)}</a>`;
  }
  return `<a class="xref unresolved" title="not in gielinor/ (likely a dev-brain reference)">${escapeHtml(text)}</a>`;
}

function highlightCode(code, ext) {
  if (ext === '.py') return highlightPython(code);
  if (ext === '.json') return highlightJson(code);
  return escapeHtml(code);
}

function highlightPython(code) {
  // tokenize: comments, strings, keywords, numbers, rest
  const KW = new Set(['False','None','True','and','as','assert','async','await','break','class','continue','def','del','elif','else','except','finally','for','from','global','if','import','in','is','lambda','nonlocal','not','or','pass','raise','return','try','while','with','yield','self']);
  let out = '';
  let i = 0;
  while (i < code.length) {
    const c = code[i];
    // comment
    if (c === '#') {
      let j = code.indexOf('\n', i);
      if (j === -1) j = code.length;
      out += `<span style="color:var(--com)">${escapeHtml(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    // triple string
    const TDQ = '"' + '""';
    const TSQ = "'" + "''";
    if (code.startsWith(TDQ, i) || code.startsWith(TSQ, i)) {
      const q = code.substr(i, 3);
      const j = code.indexOf(q, i + 3);
      const end = j === -1 ? code.length : j + 3;
      out += `<span style="color:var(--str)">${escapeHtml(code.slice(i, end))}</span>`;
      i = end;
      continue;
    }
    // string
    if (c === '"' || c === "'") {
      const q = c;
      let j = i + 1;
      while (j < code.length && code[j] !== q) {
        if (code[j] === '\\') j++;
        j++;
      }
      j = Math.min(j + 1, code.length);
      out += `<span style="color:var(--str)">${escapeHtml(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    // identifier / keyword
    if (/[A-Za-z_]/.test(c)) {
      let j = i;
      while (j < code.length && /[A-Za-z0-9_]/.test(code[j])) j++;
      const word = code.slice(i, j);
      if (KW.has(word)) out += `<span style="color:var(--kw)">${escapeHtml(word)}</span>`;
      else out += escapeHtml(word);
      i = j;
      continue;
    }
    // number
    if (/[0-9]/.test(c)) {
      let j = i;
      while (j < code.length && /[0-9.]/.test(code[j])) j++;
      out += `<span style="color:var(--num)">${escapeHtml(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    out += escapeHtml(c);
    i++;
  }
  return out;
}

function highlightJson(code) {
  // Quick pass.
  let out = escapeHtml(code);
  out = out.replace(/(&quot;[^&]*?&quot;)(\s*:)?/g, (m, str, colon) => {
    const color = colon ? 'var(--accent)' : 'var(--str)';
    return `<span style="color:${color}">${str}</span>${colon || ''}`;
  });
  out = out.replace(/\b(true|false|null)\b/g, '<span style="color:var(--kw)">$1</span>');
  out = out.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span style="color:var(--num)">$1</span>');
  return out;
}

function renderCode(code, ext) {
  return `<pre class="raw">${highlightCode(code, ext)}</pre>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// ---- Landing ----
function renderLanding() {
  currentPath = null;
  $$('.tree .row.active').forEach(r => r.classList.remove('active'));
  const fileCount = Object.keys(DATA.files).length;
  const dirCount = Object.keys(DATA.dirs).length;
  const driftCount = Object.values(DATA.files).filter(f => f.drift).length;

  const diagram = `\
gielinor/                                    ← the brain root
│
├─ CLAUDE.md, CLAUDE.local.md, .mcp.json, ticks.md  ← BODY (loads first)
├─ .claude/hooks/*.py + settings.json               ← HOOKS (four guarantees)
│
├─ meta/                  ← RULEBOOK (imported into CLAUDE.md each session)
│   write-rules · modes · archive-discipline · drafts-mechanics · death-and-spawn
│
├─ examine/   ← agent's self-model (global)
├─ niksis8/   ← model of Niklavs (global)
├─ keepsake/  ← always-surface pins (global)
├─ lorebook/  ← decisions + assumptions + patch-notes (the build log)
│
├─ spellbook/rituals/     ← respawn · bankstanding (canonical procedures)
│
└─ players/               ← CHARACTERS (Zezima, Jebrim) — each with the full template:
       bank · quest-log · spellbook · inventory  (per-player only)
       examine · niksis8_character · keepsake    (also per-player)
       _about · persona · CLAUDE.md
`;

  const startHere = [
    { path: '.claude/hooks/block-confirmed-writes.py', why: 'Hook #1 — security boundary; verify the path-match scope.' },
    { path: '.claude/hooks/block-deletes.py', why: 'Hook #2 — broad delete pattern matching; verify the trade-off.' },
    { path: '.claude/hooks/dwarf-write-boundary.py', why: 'Hook #3 — depends on env-var propagation; verify it actually fires.' },
    { path: '.claude/hooks/block-sub-dwarf-spawn.py', why: 'Hook #4 — same env-var concern; matcher patterns.' },
    { path: '.claude/settings.json', why: 'Wires the hooks. Matcher patterns are load-bearing.' },
    { path: 'meta/write-rules.md', why: 'Per-layer write discipline table — every row is a judgment call.' },
    { path: 'meta/modes.md', why: 'Principal vs dwarf split + cross-player invocation.' },
    { path: 'meta/archive-discipline.md', why: 'Never-delete rule + archive/rejected distinction.' },
    { path: 'meta/drafts-mechanics.md', why: 'Drafts → confirmed flow + observation rule.' },
    { path: 'meta/death-and-spawn.md', why: 'Crash recovery + reset table.' },
    { path: 'spellbook/rituals/respawn.md', why: 'Canonical load order — must be exactly right (S004 removed old step 6 + refined reconciliation).' },
    { path: 'spellbook/rituals/bankstanding.md', why: 'Cross-cutting reorganization — its own session mode (S004 rewrite).' },
    { path: 'lorebook/_about.md', why: 'Self-improvement log — redefined in S004; verify the new framing.' },
    { path: 'CLAUDE.md', why: 'Master body — voice, four-guarantees, address-based player invocation.' },
    { path: 'players/_about.md', why: 'Roster + invocation; rewritten in S004 to match address-based rule.' },
    { path: 'players/jebrim/persona.md', why: 'Jebrim voice spec.' },
    { path: 'players/jebrim/_about.md', why: 'Jebrim character framing + source repos.' },
    { path: 'players/zezima/persona.md', why: 'Zezima voice spec.' },
    { path: 'players/zezima/_about.md', why: 'Zezima character framing.' },
  ];

  $('#main').innerHTML = `
    <div class="landing">
      <h1>gielinor/ audit</h1>
      <div class="lede">
        Single-file audit of the gielinor/ scaffold landed in [[S003]] on 2026-05-20.
        Walk the tree on the left. Files flagged <span class="kbd" style="color:var(--drift)">DRIFT</span> are where the builder made a non-obvious judgment call worth verifying. Everything else is structurally inert (empty placeholders, .gitkeep markers).
      </div>

      <div class="cards">
        <div class="card"><div class="num">${fileCount}</div><div class="label">files</div></div>
        <div class="card"><div class="num">${dirCount}</div><div class="label">directories</div></div>
        <div class="card"><div class="num" style="color:var(--drift)">${driftCount}</div><div class="label">drift flags</div></div>
      </div>

      <div class="section-head">Architecture</div>
      <div class="diagram"><pre>${escapeHtml(diagram)}</pre></div>

      <div class="section-head">Start auditing here</div>
      <ol class="start-list">
        ${startHere.map((s, idx) => {
          const meta = DATA.files[s.path];
          if (!meta) return '';
          return `<li><span class="ord">${idx+1}</span><a class="xref" data-target="${s.path}" href="#${s.path}">${escapeHtml(s.path)}</a>${meta.drift ? ' <span class="badge" style="background:var(--drift);color:var(--bg);padding:0 4px;border-radius:3px;font-size:10px;font-weight:700">DRIFT</span>' : ''}<div class="why">${escapeHtml(s.why)}</div></li>`;
        }).join('')}
      </ol>

      <div class="section-head">Audit discipline</div>
      <div class="md">
        <ul>
          <li>The <strong>Purpose</strong> line on every file describes its <em>role in the architecture</em> — not a summary of contents. If the purpose doesn't match what you see in the inlined contents, that's a structural drift worth flagging.</li>
          <li>The <strong>Drift flag</strong> is honest about where the builder extended your sketches or authored content from scratch. Where you see one, check whether the call was made the way you'd have made it.</li>
          <li>Wiki-links (<code>[[D-001]]</code>) and path references resolve in-page; unresolved links are likely dev-brain references (out of this audit's scope).</li>
        </ul>
      </div>

      ${renderContentsSection()}
    </div>
  `;
  $$('.xref').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const target = a.dataset.target;
      if (target && DATA.files[target]) openFile(target);
    });
  });
}

// ---- Linear "File Contents" section (verbatim contents, in spec order) ----
function renderContentsSection() {
  const groups = DATA.groups || [];
  // Build TOC
  let toc = '<div class="contents-toc"><div class="contents-toc-head">Jump to</div><ul>';
  for (const [label, paths] of groups) {
    const slug = slugify(label);
    toc += `<li><a href="#group-${slug}">${escapeHtml(label)}</a> <span class="contents-toc-count">${paths.length}</span></li>`;
  }
  toc += '</ul></div>';

  // Build sections
  let body = '';
  for (const [label, paths] of groups) {
    const slug = slugify(label);
    body += `<h2 class="contents-group-head" id="group-${slug}">${escapeHtml(label)}</h2>`;
    for (const path of paths) {
      const meta = DATA.files[path];
      if (!meta) {
        body += `<div class="contents-file missing"><h3>gielinor/${escapeHtml(path)}</h3><div class="contents-missing">⚠ file not present in scaffold</div></div>`;
        continue;
      }
      const badge = meta.drift ? '<span class="badge contents-badge">DRIFT</span>' : '';
      const driftBlock = meta.drift ? `<div class="drift contents-drift"><span class="label">⚑ Drift flag</span><div>${escapeHtml(meta.reason)}</div></div>` : '';
      const anchorId = 'content-' + slugify(path);
      body += `
        <div class="contents-file" id="${anchorId}">
          <h3>gielinor/${escapeHtml(path)}${badge}</h3>
          <div class="contents-purpose"><span class="label">Purpose</span> ${escapeHtml(meta.purpose)}</div>
          ${driftBlock}
          <pre class="raw contents-raw"><code>${highlightCode(meta.content, meta.ext)}</code></pre>
        </div>
      `;
    }
  }

  return `
    <hr style="border:0;border-top:1px solid var(--border);margin:32px 0 16px;">
    <h1 class="contents-section-head">File Contents — verbatim</h1>
    <div class="lede">Literal contents of every load-bearing file, in review order. Markdown is shown raw (not rendered) so what you see is exactly what the agent reads. Empty scaffolding folders are omitted.</div>
    ${toc}
    ${body}
  `;
}

function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

// ---- Sidebar resize ----
function wireResize() {
  const sidebar = $('.sidebar');
  const handle = $('.sidebar-resize');
  let dragging = false;
  handle.addEventListener('mousedown', (e) => { dragging = true; e.preventDefault(); });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const w = Math.max(240, Math.min(600, e.clientX));
    sidebar.style.width = w + 'px';
  });
  window.addEventListener('mouseup', () => { dragging = false; });
}

// ---- Boot ----
function boot() {
  buildTree('', $('.tree'), 0);
  wireResize();
  $('#home-btn').addEventListener('click', () => renderLanding());
  renderLanding();
  // Hash deep-link
  if (location.hash) {
    const path = decodeURIComponent(location.hash.slice(1));
    if (DATA.files[path]) openFile(path);
  }
}

document.addEventListener('DOMContentLoaded', boot);
"""


def build_html(files: dict, dirs: dict) -> str:
    # Serialize file contents + dir tree as JSON.
    payload = {
        "files": files,
        "dirs": {k: list(v) for k, v in dirs.items()},
        "groups": [[label, paths] for label, paths in CONTENT_GROUPS],
    }
    json_blob = json.dumps(payload, ensure_ascii=False)
    # Escape closing script tag if it appears in any file content.
    json_blob = json_blob.replace("</script", "<\\/script")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>gielinor — audit</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <h1>gielinor / audit</h1>
      <div class="sub">Phase 1 scaffold · 2026-05-20</div>
    </div>
    <button class="home-btn" id="home-btn">↩ overview + all contents</button>
    <div class="tree"></div>
    <div class="sidebar-resize"></div>
  </aside>
  <main id="main" class="main"></main>
</div>
<script id="payload" type="application/json">{json_blob}</script>
<script>
  window.__GIELINOR__ = JSON.parse(document.getElementById('payload').textContent);
</script>
<script>
{JS}
</script>
</body>
</html>
"""


def main() -> None:
    files, dirs = walk_gielinor()
    html_text = build_html(files, dirs)
    OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"  files: {len(files)}")
    print(f"  dirs:  {len(dirs)}")
    drift = sum(1 for f in files.values() if f["drift"])
    print(f"  drift: {drift}")
    # Sanity: any unannotated files?
    unannotated = [p for p, f in files.items() if "unannotated" in f["purpose"] and not p.endswith(".gitkeep")]
    if unannotated:
        print(f"\n  WARNING: {len(unannotated)} non-.gitkeep files have no annotation:")
        for p in unannotated:
            print(f"    - {p}")


if __name__ == "__main__":
    main()
