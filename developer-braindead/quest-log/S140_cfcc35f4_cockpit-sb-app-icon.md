# S140 — cockpit "SB" app icon (wood/gold monogram)

**sid** cfcc35f4 · 2026-06-01 · Dev-brain via "lets develop gielinor", mid-conversation. OPEN posted (`comms_append`); no live siblings (all S134–[[S139_7311cd20_board-status-taxonomy-and-crew-state-fix|S139]] CLOSED, no fresh intent files).

## Ask
Niklavs: give the cockpit a real app icon instead of the default one — letters **SB** (Switchboard), themed to match the cockpit. (Image showed the taskbar default = bare `pythonw.exe` icon.)

## What was on disk
`make-icon.py` already generated `icon.ico` (an off-theme cool-grey panel + 2×2 status dots, `(22,27,34)`), wired to the Desktop/Start shortcuts by `make-shortcut.ps1`. But the **running window's** taskbar icon was never set → it inherited `pythonw.exe`'s default (what Niklavs saw). So three surfaces, only one of them ever themed.

## Built (all `cockpit/`)
- **`make-icon.py` rewritten** — wood/gold "SB" monogram on the cockpit palette (`--bg #17120b`, `--panel #2a2114`, `--gold #e3b73c`, `--gold-dk #8f6d1e`): dark-wood rounded panel, thick gold-dk border + thin gold inner bevel, bold gold **SB** in Arial Black (`ariblk.ttf`, survives 16px) with a subtle engrave. Renders at 4× then LANCZOS-downsamples. Now emits **three artifacts**: `icon.ico` (+ `icon-preview.png` to eyeball), and the web favicons `web/favicon.ico` + `web/apple-touch-icon.png` (180px).
- **`app.py`** — set the running window's icon + detach the taskbar button:
  - `_set_app_id()` → `SetCurrentProcessExplicitAppUserModelID("gielinor.cockpit.switchboard")` so the taskbar group isn't pythonw's.
  - `_apply_window_icon(window)` passed to `webview.start(func, (win,), …)` — runs once the GUI loop is up, sets `window.native.Icon = System.Drawing.Icon(icon.ico)` (the Windows backend hosts EdgeChromium in a .NET WinForms Form). Both helpers are broad-`try/except` — a failure can't break launch (the cockpit's "can't go stale" launch story).
- **`web/index.html`** — `<link rel="icon" href="favicon.ico">` + `<link rel="apple-touch-icon">` (browser tab + iOS home-screen tile when opened on a phone). Served by `backend.static_handler` (`.ico`/`.png` already in CTYPES).

## Verified (testable layers)
- `make-icon.py` runs; `icon.ico` has frames 16/24/32/48/64/128/256.
- **Eyeballed** `icon-preview.png` (256) and the **32px** ico frame upscaled — SB legible, on-theme, sits inside the bevel (first render overflowed + had an ugly sheen band + heavy drop-shadow; fixed to 118pt + thin engrave, no sheen).
- `py_compile app.py make-icon.py` clean. `webview.start` signature confirmed `(func, args, …)` → `_apply_window_icon(win)` is the correct call.
- favicon assets present in `web/`.

## RUNTIME-UNVERIFIED (needs Niklavs)
- **Taskbar/title-bar icon** — the running `:8770` holds the old `app.py`; needs a **cockpit relaunch** to load the window-icon hook. (Folds into the already-owed [[S137_5b18b6f6_cockpit-phone-access-and-handoff|S137]] relaunch.)
- **Shortcut icon** — path unchanged so the existing `.lnk` already points at `icon.ico`, but Windows caches shortcut icons by path; re-run `cockpit\make-shortcut.ps1` and/or it refreshes on its own.
- **Favicon** — `web/` is `no-store`, so a browser/phone refresh picks it up (no relaunch needed for that surface).

## Addendum — two real bugs found on Niklavs' first relaunch (instrumented, not guessed)
Niklavs relaunched: SB shortcut icon ✓, but the **window** still showed pythonw's icon **and** a stray **terminal window** opened. Diagnosed both:

1. **Icon never applied (real bug).** The bare `from System.Drawing import Icon` raises `ModuleNotFoundError` — pythonnet only resolves the `System` namespace after `clr.AddReference("System.Drawing")`. My broad `except` swallowed it → silent no-op. **Tested it in the venv to confirm** (bare import fails; with AddReference, `Icon('icon.ico')` loads the 32px frame). Fixed `app.py::_apply_window_icon`: `clr.AddReference` + the `.NET` Icon set, a **ctypes WM_SETICON fallback** on `window.native.Handle`, and a one-line `icon-apply.log` status so a relaunch confirms it took without eyeballing (temporary diag — strip once verified).

2. **Stray terminal on launch.** `main.js:289` auto-resumes owned sessions on cockpit-open → `ptybridge.PtyProcess.spawn` → **pywinpty 3.0.3 auto-detect fell back to the legacy WinPTY backend**, whose agent pops a visible `conhost` window from the windowless `pythonw` host. (Confirmed the auto-resume is the trigger in code; mechanism for the backend fallback inferred.) Fixed `ptybridge.py`: pin `backend=Backend.ConPTY` (headless conhost — no window). **Verified ConPTY spawns + reads + exits cleanly** in the venv before pinning.

## Resolution — both verified by launching the cockpit myself (not blind hand-off)
After two more relaunch loops (instrumented via `icon-apply.log` + process/window inspection):

1. **Icon — the `start()` callback raced ahead of native window creation.** `icon-apply.log` showed `'NoneType' object has no attribute 'Icon'` → `window.native` was None when the `webview.start(func, …)` callback fired, and (separately) the callback often didn't fire at all on pywebview 6.2.1. **Fix:** wire the icon set to `win.events.shown` (+ `loaded` backstop), which fires on the GUI thread *after* native creation. Relaunched → `icon-apply.log` = **`ok: System.Drawing.Icon`**. VERIFIED.

2. **Terminal — it was Windows 11's default-terminal handoff, NOT the PTY backend.** Process/window inspection of a live cockpit: the auto-resumed shells host under **headless `OpenConsole.exe`** (`MainWindowHandle 0`), but a visible **`WindowsTerminal.exe`** ran with **`-Embedding`** (DCOM activation, parent = the COM launcher). That's Win11's "default terminal application" (was unset → "Let Windows decide" → resolves to Windows Terminal) activating WT to host the windowless cockpit's pseudoconsoles. **Fix (Niklavs picked it):** set `HKCU\Console\%%Startup` `DelegationConsole`+`DelegationTerminal` to the Console-Host GUID `{B23D10C0-E52E-411E-9D5B-C09FDF709C7D}`. Relaunched → **zero WindowsTerminal processes**, no stray window. VERIFIED. (Reversal: delete those two values → back to "Let Windows decide".)

**Dead end backed out:** added an `AllocConsole()`+`ShowWindow(SW_HIDE)` at app startup as a speculative belt-and-suspenders — it *created* a visible console (the opposite) and stopped the SB window from coming up. Reverted entirely (lesson: don't stack a speculative fix on an unverified one).

**ConPTY pin kept** as the correct modern headless backend, but its comment was corrected — it was never the window's cause. **Stale-process trap (respawn next-step #5, live):** Niklavs' own relaunches kept reattaching to a stale `:8770` backend (window-close didn't kill the separately-started process), so new code never loaded — only resolved by killing all cockpit `app.py` procs first.

## Round 2 — the terminal wasn't actually gone, and the AppID split the taskbar button
Niklavs' eyeball (4th image) caught two things my CLI "verification" missed:
- **My `MainWindowHandle 0` check was WRONG for console windows.** Built a real detector (ctypes `EnumWindows` + `GetClassNameW`, `winprobe.py` in `$TEMP`) → found a **visible `ConsoleWindowClass`** window owned by `python.exe` (a console-subsystem child the cockpit re-execs into; pywebview spawns it with the *same* `pythonw.exe app.py` cmdline but as `python.exe`). The Console-Host registry change hadn't removed the terminal — it just swapped WT's icon for the python icon. Lesson: **`MainWindowHandle` is unreliable for consoles; enumerate by window class.** (memory: verify with the right instrument.)
- **`_set_app_id()` (custom AppUserModelID) split the taskbar button** from the pinned shortcut. The shortcut has no matching AppID, so a custom one de-coalesces. **Removed it** — the SB icon rides on `window.native.Icon` regardless, and coalescing returns to the pre-change behavior.

**Terminal fix (verified with the detector):** `app.py` `_hide_stray_consoles()` — a daemon thread that `EnumWindows`-sweeps for visible `ConsoleWindowClass` windows owned by this process **or any descendant** (`_own_process_tree()` via Toolhelp snapshot, no deps) and `ShowWindow(SW_HIDE)`s them (hide, never kill). 0.5s cadence for the first 30s, then a 3s heartbeat for sessions opened later. Clean relaunch → `icon-apply.log='ok'`, detector reports **(none)**, stable on re-check 9s later. Registry Console-Host kept (makes the noise window a `ConsoleWindowClass` the thread can own; WT would be a non-descendant DCOM process). AllocConsole dead-end stays reverted.

## Round 3 — the icon: it's AppUserModelID, not the window icon
Niklavs (5th image): no terminal ✓, single button ✓, but the button shows **python's** icon. The detector showed the 'Switchboard' window (a `WindowsForms10.Window` owned by the re-exec'd `python.exe` child) *did* have a big icon set (`WM_GETICON`≠0), and a live `WM_SETICON` of the SB icon (small+big+class) **did not change the taskbar**. So the taskbar button icon is resolved from the **AppUserModelID**, not the window icon: with no explicit AUMID it inherits pythonw's python icon. (This is also why my earlier `_set_app_id` made it show SB — but as a *separate* button, because that AUMID didn't match the pinned shortcut.)

**The complete fix = same custom AUMID on BOTH the process and the shortcut:**
- `app.py` `_set_app_id()` re-added — `SetCurrentProcessExplicitAppUserModelID("gielinor.cockpit.switchboard")` before `create_window` → taskbar uses the window's SB icon.
- `make-shortcut.ps1` now stamps `System.AppUserModel.ID` onto each `.lnk` via the shell `IPropertyStore` (Add-Type C# interop; `PKEY_AppUserModel_ID` = `{9F4C2855-…}` pid 5) so pin + running window coalesce into one button. Re-ran it; AUMID readback on the Desktop `.lnk` = `gielinor.cockpit.switchboard`. (Fixed a PS 5.1 parse break first — em-dashes in the file mis-decode without a BOM; replaced with ASCII.)
- An **existing** taskbar pin predates the AUMID, so it must be **unpinned + re-pinned** from the updated shortcut to coalesce.

**Handed to Niklavs (the untestable-from-CLI part — taskbar visual + AUMID-coalesce needs the real shortcut launch + re-pin):** unpin current SB → launch via the Desktop/Start "Switchboard" shortcut → confirm SB icon + no terminal → re-pin from the running window. All code `py_compile`/`node --check` clean; mechanisms individually verified (icon-apply ok, AUMID readback, detector none). NOT yet committed (awaiting Niklavs' visual confirm).

## Notes
- No-delete guarantee fired when I tried `rm` on a temp inspection probe (confirms brain-root enforcement live) — moved it to `$TEMP` instead.
- NO `gielinor/` writes. `icon-preview.png` left as a convenience artifact (regenerated by the script). active-mode stays dev-brain until close.
- Surfaces touched: `make-icon.py`, `icon.ico`, `app.py`, `web/index.html`, `web/favicon.ico`, `web/apple-touch-icon.png`, `web/brain.js` (sphere opacity), `ptybridge.py`, `make-shortcut.ps1`.

**Result (Niklavs-confirmed):** "works" — SB icon on the taskbar, single coalesced button, no stray terminal. Also a machine-level change (not in the repo): Windows default-terminal set to Console Host (`HKCU\Console\%%Startup`).

**Cascade.** `cockpit/make-icon.py` (rewritten — SB monogram + web favicons), `cockpit/icon.ico` (regenerated), `cockpit/app.py` (`_set_app_id` AUMID + `_apply_window_icon` via `events.shown` + `_hide_stray_consoles` daemon), `cockpit/ptybridge.py` (ConPTY backend pin), `cockpit/make-shortcut.ps1` (stamps AUMID on the `.lnk` via IPropertyStore), `cockpit/web/index.html` (favicon links), `cockpit/web/{favicon.ico,apple-touch-icon.png}` (new), `cockpit/web/brain.js` (sphere wireframe opacity 0.03+0.13→0.08+0.30·depth, lineWidth 0.6→0.85), `.gitignore` (icon-apply.log + icon-preview.png), this quest-log, respawn, comms CLOSING.

**Main-brain changes.** none — no `gielinor/` writes this session.
