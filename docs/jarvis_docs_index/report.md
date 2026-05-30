# JARVIS Docs Index / Command Center Manual

- **Generated:** 2026-05-30
- **Audited through commit:** `c94da5c` (Step 17)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

---

## 1. Overview

The SPARTA JARVIS Command Center is a cinematic, **read-only** dashboard that
aggregates the state of the SPARTA_BRAIN system (server, AI brains, trading
research, content/money/moving engines, git, safety posture, cached reports,
and operator docs) into one screen.

**Read-only posture:** confirmed. The browser surface never mutates anything.

**Allowed:**
- Read and display aggregated status from `/api/jarvis/status` (GET only).
- Display cached reports written offline by manual tools.
- Display tracked documentation JSON (mission board, prompt library, system map).
- Poll the status endpoint on a timer for a live read-only view.

**Not allowed:**
- Execute commands or scripts from the browser.
- Clean, stage, delete, move, or write any file from the web.
- Run tests or probes from the web route.
- Execute any prompt or mission text.
- Control a broker, place paper/live trades, or expose any order path.
- Upload, deploy, push, or fire automation.
- Dump secrets or environment values.

---

## 2. Commit timeline (base → Step 13)

| Hash | Purpose |
| --- | --- |
| `7c9cad2` | Add SPARTA JARVIS command center (base) |
| `6632b9b` | Add JARVIS command center release note |
| `38cf4fa` | Step 02 operator intelligence panel |
| `5ae2f84` | Step 03 cached health report panel |
| `0f4523c` | Step 04 read-only mission board panel |
| `f4ba60d` | Step 05 trading detail panel |
| `df14112` | Step 06 cached route smoke panel |
| `49f3f4e` | Step 07 read-only prompt library panel |
| `bdcca5a` | Step 08 read-only file hygiene panel |
| `0640d25` | Step 09 commander's snapshot summary |
| `4e21cc4` | Step 10 read-only system map panel |
| `78a50cc` | Step 11 read-only hardening audit memo |
| `9a97848` | Step 12 system map api_key reconciliation |
| `da1f1ee` | Step 13 refresh mission board and prompt library |
| `efa8298` | Step 14 docs index / command center manual |
| `8eea703` | Step 15 read-only cache freshness panel |
| `34b09a5` | Step 16 live regression smoke memo |
| `c94da5c` | Step 17 panel consistency audit memo |

---

## 3. Main code files

| Path | Purpose |
| --- | --- |
| `app.py` | FastAPI app. Holds the `_jarvis_*` read-only helpers, the `GET /api/jarvis/status` aggregate endpoint, and the `GET /jarvis` page route. |
| `templates/jarvis.html` | Cinematic read-only dashboard template. Single GET fetch to `/api/jarvis/status`; no buttons, forms, onclick, or POST. |
| `tests/test_jarvis_route.py` | JARVIS route + reader test suite (98 tests). Run scoped with `--rootdir=tests`. |

---

## 4. Tracked data / doc files

| Path | Purpose |
| --- | --- |
| `docs/JARVIS_COMMAND_CENTER_RELEASE_NOTE.md` | Original release note for the command center. |
| `docs/jarvis_mission_board.json` | Display-only operator mission board (14 missions). |
| `docs/jarvis_prompt_library.json` | Display-only operator prompt library (10 read-only prompts). |
| `docs/jarvis_system_map.json` | Display-only wiring map: 21 panels (each with `api_key`), 3 scripts, tracked/ignored file lists. |
| `docs/jarvis_step_11_hardening_audit/report.json` | Step 11 hardening audit memo (machine-readable). |
| `docs/jarvis_step_11_hardening_audit/report.md` | Step 11 hardening audit memo (human-readable). Conclusion: JARVIS_HARDENING_PASS. |
| `docs/jarvis_docs_index/report.json` | This docs index (machine-readable). |
| `docs/jarvis_docs_index/report.md` | This docs index / command center manual (human-readable). |
| `docs/jarvis_step_16_live_regression_smoke/report.json` | Step 16 live regression smoke memo (machine-readable). |
| `docs/jarvis_step_16_live_regression_smoke/report.md` | Step 16 live regression smoke memo (human-readable). Conclusion: JARVIS_LIVE_REGRESSION_PASS. |
| `docs/jarvis_step_17_panel_consistency_audit/report.json` | Step 17 panel consistency audit memo (machine-readable). |
| `docs/jarvis_step_17_panel_consistency_audit/report.md` | Step 17 panel consistency audit memo (human-readable). Conclusion: CONSISTENT. |

---

## 5. Manual-only scripts

These run **offline only** and write cached JSON the web route reads. The web
app never runs them.

| Path | Writes | Purpose |
| --- | --- | --- |
| `tools/jarvis_health_report.py` | `storage/jarvis/health_report.json` | Offline compile/test health report. Manual only; never run from the web. |
| `tools/jarvis_route_smoke_report.py` | `storage/jarvis/route_smoke_report.json` | Offline GET-only route smoke report. Manual only; never run from the web. |
| `tools/jarvis_file_hygiene_report.py` | `storage/jarvis/file_hygiene_report.json` | Offline git/untracked hygiene summary. Manual only; never run from the web. |

---

## 6. Ignored runtime cache files

These are gitignored; they are produced by the manual scripts and only **read**
by the dashboard.

- `storage/jarvis/health_report.json`
- `storage/jarvis/route_smoke_report.json`
- `storage/jarvis/file_hygiene_report.json`

---

## 7. Current API sections

`/api/jarvis/status` returns these 22 sections (plus the meta keys `online` and
`read_only`, for 24 top-level keys total):

- `commander_snapshot`
- `system_core`
- `ai_brains`
- `trading_bridge`
- `content_engine`
- `money_engine`
- `moving_company`
- `daily_mission`
- `safety_gates`
- `git`
- `safety`
- `project`
- `brain_memory`
- `recommended_next_actions`
- `health_report`
- `mission_board`
- `trading_detail`
- `route_smoke_report`
- `prompt_library`
- `file_hygiene_report`
- `system_map`
- `cache_freshness`

The `cache_freshness` section (added Step 15) renders in the UI panel with id
`pCacheFreshness`. It reports whether the known `storage/jarvis/*.json` caches
are fresh, stale, missing, or invalid by reading only their metadata
(existence, modified time, `generated_at`) — it never runs the generator
scripts and never refreshes a cache.

Every section is wrapped fail-closed by `_jarvis_safe`, so one failing section
never crashes the endpoint (it still returns 200 with an error dict for that
section).

---

## 8. Safety rules

- No browser execution.
- No broker control.
- No paper or live trading controls.
- No file cleanup, stage, or delete controls.
- No POST routes or actions.
- No secrets or environment dumps.
- Cached-report scripts are manual only.
- The web route reads only; every section is fail-closed via `_jarvis_safe`.

---

## 9. Current known warnings

- `commander_snapshot` may show **yellow** due to the large untracked-file
  backlog and a dirty working tree (conservative by design, not an error).
- `/money-spartan` may report a non-required **404** in the route smoke report.
- A corrupted `hydra ` directory can break bare pytest collection, so always use
  the scoped JARVIS pytest command (`--rootdir=tests`).
- This docs index is now refreshed through **Step 17** (commit `c94da5c`): it
  lists the `cache_freshness` section and the Step 16 / 17 memos.

---

## 10. How to validate JARVIS

```
python -m py_compile app.py
python -m py_compile tools/jarvis_health_report.py
python -m py_compile tools/jarvis_route_smoke_report.py
python -m py_compile tools/jarvis_file_hygiene_report.py
python tools/jarvis_health_report.py
python tools/jarvis_route_smoke_report.py
python tools/jarvis_file_hygiene_report.py
pytest tests/test_jarvis_route.py --rootdir=tests -q
```

---

## 11. Recommended next steps

**Completed since the last index revision:**

- **JARVIS-CACHE-FRESHNESS** — shipped Step 15 (commit `8eea703`).
- **JARVIS-LIVE-REGRESSION-SMOKE** — memo Step 16 (commit `34b09a5`); conclusion
  JARVIS_LIVE_REGRESSION_PASS.
- **JARVIS-PANEL-CONSISTENCY** — memo Step 17 (commit `c94da5c`); conclusion
  CONSISTENT.

**Recommended next:**

- **JARVIS-UI-POLISH** — cosmetic layout, spacing, and label improvements only;
  no new buttons, forms, POST routes, or capabilities.
- **JARVIS-CACHE-FRESHNESS-AGE-BADGES** — optional display-only age badges on
  each cache row (no new controls).
- **JARVIS-DOCS-AUTO-CHECK-MEMO** — a read-only memo that re-verifies the docs
  index against the live API and tracked docs.
- **JARVIS-LIVE-REGRESSION-SMOKE (recurring)** — re-run the live regression
  memo after future JARVIS commits.
