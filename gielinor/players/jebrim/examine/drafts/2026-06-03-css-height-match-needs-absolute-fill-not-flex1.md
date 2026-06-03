# Matching a scroll-panel's height to a sibling needs the absolute-fill trick, not flex-1 alone

**Observation ([[S149_ebe0a532_scm-transit-times-rework|S149]], ebe0a532).** Asked to make the SCM corridors table fill the
blank space and match the height of the right-hand chart stack, my first move was
`h-full flex flex-col` on the card + `flex-1 overflow-y-auto` on the scroll area.
That did **not** bound the height: under CSS grid `align-items: stretch`, the row
height = the *tallest* item's content, and the un-capped table was now the tallest —
so it grew very long with no scrollbar. Niklavs caught it ("now has no scroll bar at
all, it's very long").

**The fix that worked.** Make the left grid cell a positioning context
(`lg:relative`) and the card `lg:absolute lg:inset-0`. Absolutely-positioned content
has zero intrinsic height, so the *sibling* (the distribution/outcome stack) drives
the row height; the card then fills the cell and its `flex-1` scroll area finally has
a bounded parent → it scrolls and matches the sibling.

**Lesson.** "Make panel A the same height as sibling B via flex" only works if B
drives the row. If A has the larger content, A drives the row and flex-1 can't bound
it — A must be taken out of the height calculation (absolute fill inside a relative
cell). Check *which sibling drives the row* before reaching for flex-1.

Anchor: the table-height correction turn this session. Frontend/CSS technique;
player-scope (not a working-style lesson → not promoted to cross-conv memory).
