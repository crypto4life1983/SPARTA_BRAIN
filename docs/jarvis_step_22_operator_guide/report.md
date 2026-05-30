# JARVIS Step 22 — Operator Guide / Runbook

- **Generated:** 2026-05-30
- **Type:** documentation only (no code, no UI, no API change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This is the operator-facing runbook for the SPARTA JARVIS Command Center. It
explains what the page shows, how to read each panel and section, the
read-only safety posture, and what operators should and should not do. It adds
**no** capability, control, or API change.

---

## 1. Purpose and relation to Steps 20–21

- **Step 20** polished the UI (CSS/HTML/labels only): six section dividers, a
  posture legend, colour-coded tags, a more prominent Commander's Snapshot,
  Cache Freshness regrouped with the other cached reports, and roomier
  spacing. The API shape was unchanged.
- **Step 21** proved the polished UI is live and safe: all key panels render,
  the API shape is unchanged at 24 top-level keys, and there are no
  execution/refresh controls (conclusion **JARVIS_POST_POLISH_SMOKE_PASS**).
- **Step 22 (this guide)** documents how to *operate and interpret* that
  polished, validated surface. It touches no code, UI, or API.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass (`templates/jarvis.html` only). |
| Step 21 | `4f55aae` | Post-polish live smoke memo (validation only). |

---

## 3. What `/jarvis` is

A cinematic, **read-only** dashboard (a single HTML page) that renders the
aggregated SPARTA_BRAIN state. It performs one GET fetch to
`/api/jarvis/status` and re-polls on a 15-second timer. It has **no** buttons,
forms, `onclick` handlers, POST actions, or refresh endpoint. The browser
surface never mutates anything.

## 4. What `/api/jarvis/status` is

A GET-only JSON aggregate with **24 top-level keys**: 22 read-only sections
plus the two meta keys `online` and `read_only`. Every section is wrapped
fail-closed by `_jarvis_safe`, so if one section fails it returns an error dict
for *that* section but the endpoint still returns **HTTP 200**. The endpoint
reads state — it never executes scripts, runs probes, refreshes caches, or
controls a broker.

---

## 5. `read_only = true`

The JARVIS surface is in its guaranteed observe-only posture: no execution, no
refresh control, no broker/paper/live path, no file mutation from the web.
**`read_only` must always be true.**

## 6. `online = true`

The JARVIS aggregator responded and the page received its status payload. It
is a liveness signal for the dashboard itself — not a claim that every
downstream subsystem is green.

## 7. `commander_snapshot.overall_state = yellow`

**Yellow is conservative-by-design.** It most commonly reflects the large
untracked-file backlog and a dirty working tree. It means *"needs attention /
not fully green"* — it is **not** an error and **not** an approval to act. The
required safety checks (safety locked, health pass, route smoke pass, caches
fresh) can all be green while overall stays yellow purely because the working
tree is dirty/untracked. Green requires a clean posture.

## 8. `trading_detail` posture

| Field | Value | Meaning |
| --- | --- | --- |
| `read_only` | true | The trading surface is observe-only. |
| `paper_ready` | false | No paper-trading path is wired or armed. |
| `live_ready` | false | No live-trading path is wired or armed. |
| `broker_control` | false | JARVIS holds no broker control and exposes no order path. |

Research is candidate / visibility only.

---

## 9. The six UI sections

1. **Command Overview** — single-glance verdict (`pSnapshot`).
2. **Core Systems** — server, brains, repository, project artifacts, brain
   memory (`pCore`, `pBrains`, `pGit`, `pProject`, `pBrainMem`).
3. **Operations** — read-only engines plus the daily plan (`pTrading`,
   `pContent`, `pMoney`, `pMoving`, `pMission`, `pNext`).
4. **Safety & Reliability** — gates, operator posture, and the cached health /
   route smoke / cache freshness / file hygiene reports (`pSafety`,
   `pOpSafety`, `pHealth`, `pRouteSmoke`, `pCacheFreshness`, `pHygiene`).
5. **Research Visibility** — read-only trading research detail
   (`pTradingDetail`).
6. **Documentation & Maps** — tracked, display-only mission board, prompt
   library, and system map (`pMissions`, `pPromptLib`, `pSystemMap`).

**Posture legend** (shown at the top of the grid): `READ ONLY` (live status,
no writes), `CACHED` (offline report, read only), `DISPLAY ONLY` (tracked
docs, no execution), `MANUAL SCRIPT ONLY` (never run from the browser).

---

## 10. The 12 key panels

| Panel | Title | Reads | How to read it |
| --- | --- | --- | --- |
| `pSnapshot` | Commander's Snapshot | `commander_snapshot` | Top-level verdict + safety/health/route/trading/cache signals, counts, and warnings. Yellow = needs attention, not approval. |
| `pCore` | System Core | `system_core` | Server/brain state, server time, library counts. |
| `pBrains` | AI Brains | `ai_brains` | Per-brain state (Claude/Codex/Gemini/Ollama). Warn/idle is informational. |
| `pTrading` | Trading Bridge | `trading_bridge` | READ-ONLY / LOCKED posture, sealed lifecycle count, per-lifecycle verdicts. No order path. |
| `pHealth` | Health Report | `health_report` | CACHED compile/test health (py_compile, pytest). "No cached report" = manual tool not run. |
| `pRouteSmoke` | Route Smoke | `route_smoke_report` | CACHED GET-only route check; per-route status codes. `/money-spartan` 404 may be non-required. |
| `pHygiene` | File Hygiene | `file_hygiene_report` | CACHED git/untracked summary; watch the staged count. Cached reports stay gitignored. |
| `pMissions` | Mission Board | `mission_board` | DISPLAY-ONLY missions. "Safe next prompt" text is display only — nothing runs it. |
| `pPromptLib` | Prompt Library | `prompt_library` | DISPLAY-ONLY prompts; text is shown, never run, no copy-and-run affordance. |
| `pSystemMap` | System Map | `system_map` | DISPLAY-ONLY wiring: panels, manual-only scripts, tracked/ignored files, posture flags. |
| `pTradingDetail` | Trading Research Detail | `trading_detail` | READ-ONLY research: candidate status, posture flags, S26 state, latest report cards. No broker/paper/live. |
| `pCacheFreshness` | Cache Freshness | `cache_freshness` | DISPLAY-ONLY cache metadata (age vs threshold, gitignored, timestamps). Reads metadata only; never refreshes. Now grouped with Health & Route Smoke. |

> The grid also renders ten more read-only panels outside this "key 12":
> Content Engine, Money Engine, Moving Company, Daily Mission, Safety Gates,
> Git State, Operator Safety, Project Files, Brain Memory, and Recommended
> Next Actions.

---

## 11. Safety rules

- **JARVIS observes only** — it is a read-only mirror of state.
- **JARVIS does not execute** commands, scripts, prompts, or missions.
- **JARVIS does not refresh** through UI controls; there is no refresh button
  or endpoint. Data updates only via the page's own GET poll.
- **JARVIS does not control** broker, paper, or live trading, and exposes no
  order path.
- **Operators must treat yellow** as *"needs attention / not fully green"* —
  **not** as approval to act.
- Cached-report scripts (health / route smoke / file hygiene) are
  **manual-only** and are never run from the web.

---

## 12. Operator checklist for daily review

1. Open `http://127.0.0.1:8765/jarvis`; confirm it loads (status orb
   **ONLINE**, not SIGNAL LOST).
2. Confirm **Commander's Snapshot** renders; note overall state and read any
   warnings.
3. Confirm **Safety Gates**: Trading execution LOCKED, YouTube upload
   APPROVAL_REQUIRED, Live automation BLOCKED.
4. Confirm **Operator Safety** flags all locked/true (read-only, no execution
   control, no broker control, no secret display, no force git).
5. Confirm **Trading Research Detail**: read_only TRUE; paper_ready,
   live_ready, broker_control all FALSE.
6. Glance at **Cache Freshness**: overall fresh. Stale/missing only means a
   manual cached report is old or not generated — not a live failure.
7. Glance at **File Hygiene** staged count; non-zero is worth investigating
   before any commit work.
8. Optionally confirm `GET /api/jarvis/status` returns 200 with `online=true`,
   `read_only=true`, and 24 top-level keys.

---

## 13. Failure interpretation

| Symptom | Meaning | Action |
| --- | --- | --- |
| A panel is missing / stuck on loading text | The page didn't receive that section, or it returned a fail-closed error dict. Endpoint still 200. | Reload; if it persists, inspect `/api/jarvis/status` for that section's error. Do **not** add a UI control to "fix" it. |
| `/jarvis` or `/api/jarvis/status` non-200 | Server down or route broken. | Restart the server process **offline** (manual), then re-check. No restart/refresh control in the UI. |
| `online = false` | Aggregator liveness signal failed. | Treat as degraded; investigate server/aggregator offline. |
| `read_only = false` | **CRITICAL** — the read-only guarantee is broken; must never happen. | **Stop.** Serious safety regression — investigate immediately; do not trust the surface until read_only is true again. |
| `broker_control = true` | **CRITICAL** — a broker control path is reported; must never happen. | **Stop.** Serious safety regression — halt and investigate before further use. |
| `paper_ready` / `live_ready` unexpectedly true | **CRITICAL** — a paper/live trading path is reported armed; both must stay false. | **Stop.** Serious safety regression — halt and investigate before further use. |

---

## 14. Recommended next safe improvements (after Step 22)

- **JARVIS-CACHE-FRESHNESS-AGE-BADGES** — optional display-only age badges per
  cache row (no new controls).
- **JARVIS-DOCS-AUTO-CHECK-MEMO** — a read-only memo that re-verifies the docs
  index against the live API and tracked docs.
- **JARVIS-LIVE-REGRESSION-SMOKE (recurring)** — re-run the live regression /
  post-polish smoke memo after future JARVIS commits.
- **JARVIS-OPERATOR-GUIDE-LINK** — optionally surface a display-only
  link/footnote pointing operators to this runbook (no behavior).

---

**Conclusion:** documentation-only operator guide created. No code, UI, tool,
test, API, or trading surface was changed.
