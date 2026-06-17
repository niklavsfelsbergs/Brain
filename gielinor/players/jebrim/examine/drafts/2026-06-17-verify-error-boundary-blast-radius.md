---
observation: Verify a framework error-boundary's blast radius before claiming isolation
type: self-observation
anchor: [[S255_bde53943_scm-clientside-crash-diagnosis|S255]] (sid8 bde53943) — SCM client-side crash fix
---

This session I told Niklavs the error-boundary fix would "contain the throw to one panel; the rest of the dashboard keeps working," then had to correct myself a turn later: a Next.js App-Router **`error.tsx` replaces the whole route segment** — it does NOT give per-component isolation. Keeping the *other* tabs alive required a separate React `ErrorBoundary` class wrapping each tab's `<Suspense>`; `error.tsx`/`global-error.tsx` are only the outer net.

**Pattern:** I described the *desired* behavior (panel isolation) and attached it to the *first mechanism that came to mind* (route boundary) without checking that mechanism's actual scope. The reflex to fix: when claiming an error boundary / guard "isolates X," state *which* unit it isolates to and confirm the mechanism's real granularity — route-segment vs component-tree — before promising the blast radius. A boundary's scope is the whole thing it wraps, not the thing you wish it wrapped.

Sibling of the pinned *verify-the-thing-don't-trust-the-wiring* reflex, applied to framework semantics. Caught it myself before it shipped, but it reached the principal first.
