# JARVIS Step 19 — UI Polish Plan Memo

- **Audited commit:** `496b0b8` (Refresh JARVIS docs index through Step 17)
- **Generated:** 2026-05-30
- **Type:** plan / memo only (no code, no panel, no UI change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Conclusion:** **PROCEED_TO_UI_POLISH**

This memo plans a future **Step 20** UI polish pass. It changes nothing now.
It identifies CSS/layout/label-only improvements that keep the console
strictly read-only and do not touch the API shape, data flow, panel set, or
capabilities.

---

## 1. Current UI inventory

**Layout.** A single `<section class="jarvis-root">` holds a sticky header
(`.jv-head`: title + live clock + `READ-ONLY` badge), a `.jv-core` orb/ring,
one `.jv-grid` containing every panel, and a `.jv-foot` disclaimer
("This console is a read-only mirror…").

**Grid behavior.** `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))`.
Standard panels take one column; `.jv-wide` panels span the full row
(`grid-column: 1 / -1`). It reflows from multi-column desktop to single-column
mobile. A `@media (prefers-reduced-motion: reduce)` block already disables
animations.

**Panels (22, DOM order):**

| # | id | Title | Wide | Tag |
| --- | --- | --- | --- | --- |
| 1 | `pSnapshot` | Commander's Snapshot | wide | — (jv-snap verdict styling) |
| 2 | `pCore` | System Core | | — |
| 3 | `pBrains` | AI Brains | | — |
| 4 | `pTrading` | Trading Bridge | | READ-ONLY |
| 5 | `pContent` | Content Engine | | — |
| 6 | `pMoney` | Money Engine | | — |
| 7 | `pMoving` | Moving Company | | — |
| 8 | `pMission` | Daily Mission | | — |
| 9 | `pSafety` | Safety Gates | | — (static fallback gates) |
| 10 | `pGit` | Git State | | — |
| 11 | `pOpSafety` | Operator Safety | | — |
| 12 | `pProject` | Project Files | | — |
| 13 | `pBrainMem` | Brain Memory | | — |
| 14 | `pNext` | Recommended Next Actions | | — |
| 15 | `pHealth` | Health Report | | — |
| 16 | `pRouteSmoke` | Route Smoke | | CACHED |
| 17 | `pHygiene` | File Hygiene | wide | CACHED |
| 18 | `pMissions` | Mission Board | wide | — |
| 19 | `pPromptLib` | Prompt Library | wide | DISPLAY ONLY |
| 20 | `pSystemMap` | System Map | wide | DISPLAY ONLY |
| 21 | `pTradingDetail` | Trading Research Detail | wide | — |
| 22 | `pCacheFreshness` | Cache Freshness | | DISPLAY ONLY |

**Implicit groups (today they are not visually separated):** Command
(`pSnapshot`); System (`pCore`, `pBrains`, `pGit`, `pProject`, `pBrainMem`);
Engines (`pTrading`, `pContent`, `pMoney`, `pMoving`); Mission/Next
(`pMission`, `pNext`); Safety (`pSafety`, `pOpSafety` — currently split by
`pGit`); Cached Reports (`pHealth`, `pRouteSmoke`, `pHygiene`,
`pCacheFreshness` — currently scattered); Operator Docs (`pMissions`,
`pPromptLib`, `pSystemMap`); Research (`pTradingDetail`).

---

## 2. Safe polish opportunities

1. **P1 — Visual grouping.** Add display-only section dividers/labels
   (Command / System / Engines / Safety / Cached Reports / Operator Docs /
   Research) so related panels read as groups. Markup + CSS only.
2. **P2 — Tag/legend consistency.** Unify the `READ-ONLY` / `CACHED` /
   `DISPLAY ONLY` tags into a consistent color-coded chip vocabulary with a
   one-line legend. Label/CSS only.
3. **P3 — Compact status badges.** Align the per-row LED + value badges
   (consistent width, monospace value, aligned label column) for faster
   state scanning.
4. **P4 — Clearer warning hierarchy.** Give real warnings a warn-tinted block
   with an icon, and de-emphasize conservative-by-design notes (commander
   yellow, `/money-spartan` 404) so genuine issues stand out.
5. **P5 — Snapshot readability.** Larger verdict chip, a compact one-line
   summary, and contributing signals (safety/health/route/cache/git) as
   aligned mini-badges instead of a text list.
6. **P6 — Reduce wall-of-text.** In the wide panels (File Hygiene, System Map,
   Trading Research Detail) cap long lists with a display-only
   truncation / "+N more" treatment and tighter spacing. Presentation only —
   no data is dropped from the API.
7. **P7 — Spacing & mobile.** Consistent panel padding and gap rhythm; tune
   min panel width so mobile single-column and desktop multi-column both
   breathe. Address the narrow Cache Freshness panel orphaned at the end of
   the wide-panel run, via CSS placement only.
8. **P8 — Reduced motion.** Extend the existing
   `@media (prefers-reduced-motion: reduce)` coverage to any new polish
   animations.

---

## 3. Explicit non-goals

- No `<button>`, `<form>`, `onclick`, or any interactive control.
- No POST routes, no `method="post"`, no refresh endpoint or refresh button.
- No script execution from the browser.
- No broker control, no paper/live trade controls, no order path.
- No file cleanup / stage / delete / move / write controls.
- No secrets or environment dumps.
- No new capability of any kind — polish is visual only.

---

## 4. Proposed Step 20 scope

**Allowed:**

- Edit `templates/jarvis.html` CSS (inline `<style>` scoped under
  `.jarvis-root`) for grouping, spacing, badges, warning hierarchy, snapshot.
- Edit `templates/jarvis.html` markup to add display-only group headers and to
  restructure existing rendered content for readability.
- Adjust the existing render JS **only** to reshape already-fetched data into
  clearer DOM (grouping, display truncation) — still a single GET fetch to
  `/api/jarvis/status`, no new requests.

**Not allowed:**

- No change to the `/api/jarvis/status` response shape or keys.
- No new scripts; no changes to `tools/jarvis_*.py`.
- No new route and no change to route behavior (GET-only, read-only).
- No change to data flow: still one GET fetch polled on a timer.

**API shape change:** none expected.

---

## 5. Risk controls

**Re-run before/after Step 20:**

```
python -m json.tool docs/jarvis_step_19_ui_polish_plan/report.json
python -m py_compile app.py
python -m py_compile tools/jarvis_health_report.py
python -m py_compile tools/jarvis_route_smoke_report.py
python -m py_compile tools/jarvis_file_hygiene_report.py
pytest tests/test_jarvis_route.py --rootdir=tests -q   # expect 108 passed
```

**Served-HTML safety scan (must all be absent):** `<button>`, `<form>`,
`onclick`, `method="post"`, any `/api/jarvis/refresh` or refresh-endpoint
reference.

**Endpoint guarantee:** no new endpoint; `/jarvis` stays GET-only HTML and
`/api/jarvis/status` stays GET-only JSON, every section fail-closed via
`_jarvis_safe`.

**Regression follow-up:** after Step 20 ships, re-run the live regression
smoke memo (JARVIS-LIVE-REGRESSION-SMOKE, recurring) to confirm all panels
still render and no execution affordance was introduced.

---

## 6. Non-blocking warnings

- Large untracked backlog keeps `commander_snapshot` **yellow** (conservative
  by design, not an error).
- `/money-spartan` may report a non-required **404** in the route smoke report.
- A corrupted `hydra ` directory can break bare pytest collection, so the
  scoped pytest command (`--rootdir=tests`) is used.

---

## 7. Recommended decision

**PROCEED_TO_UI_POLISH.** The console is functionally complete and strictly
read-only. A CSS/layout/label-only Step 20 can meaningfully improve grouping,
label consistency, warning hierarchy, and Commander's Snapshot readability
with no change to the API shape, data flow, panel set, or capabilities, and no
new execution, refresh, broker, trade, or file-mutation affordance.
