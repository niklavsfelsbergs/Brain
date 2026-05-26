# why.md — why we're building this

> The framing. Months from now, when context has faded, this is the file that reminds you what the project is *for*.

## What

A personal AI agent. Not a knowledge vault, not a single-purpose tool — a full agentic system with substrate, triggers, body, brain, gates, tools, and personality. Designed to serve whatever Niklavs brings: knowledge work, research, life logistics, reflection.

## Why a general-purpose substrate

Single-purpose tools are dead ends. The cost of building each new tool from scratch is what makes most personal-automation efforts fizzle. A general-purpose agent with a growing memory and a stable identity amortizes that cost — adding capabilities is incremental, not greenfield each time.

## The pilot

First concrete job-to-be-done: **morning shipping-data routing check.** Each morning the agent reviews shipping data and surfaces anything concerning. Architecture stays general-purpose, but the pilot makes Phase 1 falsifiable — gates, personality, and triggers stop being abstract and start having to ship a real outcome.

Source of shipping data, channel for delivering the morning report, and exact definition of "concerning" — all TBD. See [[plan]] §C.

## Why two brains

Process artifacts (this folder, `developer-braindead/`) and outcome artifacts (the main brain, `vault/`) are physically separated. The live agent never reads its own birth narrative. See [[D-001_two_brain_split]].

## Why we keep notes this carefully

Because the agent will outlive the active build phase, and future-Niklavs (and future-Claude) will need to understand *why* the architecture is the way it is — not just what it is. Without that, every revision risks re-litigating settled ground. The dev brain is the institutional memory.
