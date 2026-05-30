# JARVIS Step 17 — Panel Consistency Audit Memo

- **Audited commit:** `34b09a5` (Add JARVIS Step 16 live regression smoke memo)
- **Generated:** 2026-05-30
- **Type:** audit / memo only (no code, no panel, no UI change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Conclusion:** **CONSISTENT** (runtime surface aligned; one labeled, non-blocking documentation-lag note)

---

## 1. Files inspected

- `app.py`
- `templates/jarvis.html`
- `tests/test_jarvis_route.py`
- `docs/jarvis_system_map.json`
- `docs/jarvis_mission_board.json`
- `docs/jarvis_prompt_library.json`
- `docs/jarvis_docs_index/report.json`
- `docs/jarvis_docs_index/report.md`
- `docs/jarvis_step_16_live_regression_smoke/report.json`
- `docs/jarvis_step_16_live_regression_smoke/report.md`

---

## 2. Validation commands and results

| Command | Result |
| --- | --- |
| `json.tool docs/jarvis_system_map.json` | JSON_OK |
| `json.tool docs/jarvis_mission_board.json` | JSON_OK |
| `json.tool docs/jarvis_prompt_library.json` | JSON_OK |
| `json.tool docs/jarvis_docs_index/report.json` | JSON_OK |
| `json.tool docs/jarvis_step_16_live_regression_smoke/report.json` | JSON_OK |
| `py_compile app.py` | PASS |
| `py_compile tools/jarvis_health_report.py` | PASS |
| `py_compile tools/jarvis_route_smoke_report.py` | PASS |
| `py_compile tools/jarvis_file_hygiene_report.py` | PASS |
| `pytest tests/test_jarvis_route.py --rootdir=tests -q` | **108 passed** |

---

## 3. API key count

- **Total top-level keys:** 24
- **Meta keys (not panels):** `online`, `read_only`
- **Section keys:** 22

Section keys: `commander_snapshot`, `system_core`, `ai_brains`,
`trading_bridge`, `content_engine`, `money_engine`, `moving_company`,
`daily_mission`, `safety_gates`, `git`, `safety`, `project`, `brain_memory`,
`recommended_next_actions`, `health_report`, `route_smoke_report`,
`file_hygiene_report`, `mission_board`, `prompt_library`, `system_map`,
`trading_detail`, `cache_freshness`.

---

## 4. System map panel count

- **Panels:** 22
- **Duplicate api_key values:** 0
- **api_key values not found in the live API:** none

All 22 `system_map` `api_key` values resolve to a live API section key. The two
remaining live keys (`online`, `read_only`) are meta keys, not panels. The
api_key ↔ API-section mapping is exact and unambiguous.

---

## 5. UI panel checklist (served `/jarvis` HTML)

| Panel | Expected id | Actual id | Present |
| --- | --- | --- | --- |
| Commander's Snapshot | `pSnapshot` | `pSnapshot` | ✅ |
| Health Report | `pHealth` | `pHealth` | ✅ |
| Route Smoke | `pRouteSmoke` | `pRouteSmoke` | ✅ |
| File Hygiene | `pHygiene` | `pHygiene` | ✅ |
| Cache Freshness | `pCacheFresh` | `pCacheFreshness` | ✅ (see note) |
| Mission Board | `pMissions` | `pMissions` | ✅ |
| Prompt Library | `pPromptLib` | `pPromptLib` | ✅ |
| System Map | `pSystemMap` | `pSystemMap` | ✅ |
| Trading Research Detail | `pTradingDetail` | `pTradingDetail` | ✅ |

**Note on Cache Freshness:** the Step 17 spec listed the id as `pCacheFresh`,
but the actual committed id (Step 15) is `pCacheFreshness`. This is a
naming-shorthand difference in the task spec, **not** codebase drift — the
API key (`cache_freshness`), the `system_map` `api_key` (`cache_freshness`), and
the UI element id (`pCacheFreshness`) are internally consistent.

---

## 6. Docs index consistency

- **File:** `docs/jarvis_docs_index/report.json`
- **audited_through_commit:** `da1f1ee` (Step 13)
- **api_sections listed:** 21 — does **not** include `cache_freshness`
- **Status:** STALE (non-blocking)

The docs index was generated at Step 14 and is explicitly scoped to commit
`da1f1ee`, so it predates the Step 15 `cache_freshness` section. Its
`api_sections` list (21) therefore lacks `cache_freshness`. Because the file
declares its own audit horizon, this is documentation lag rather than a
correctness defect. Refreshing it is the recommended Step 18.

---

## 7. Mission board / prompt library consistency

| Artifact | Count | Cache reference | Status |
| --- | --- | --- | --- |
| `docs/jarvis_mission_board.json` | 14 missions | `JARVIS-CACHE-FRESHNESS` present | CONSISTENT |
| `docs/jarvis_prompt_library.json` | 10 prompts | `JARVIS-CACHE-FRESHNESS` present | CONSISTENT |

Both the mission board and the prompt library carry a `JARVIS-CACHE-FRESHNESS`
entry, so the cache-freshness capability shipped in Step 15 is reflected in the
operator-facing tracked docs.

---

## 8. Findings

**CONSISTENT.** The live runtime surface — API sections, `system_map` `api_key`
fields, and rendered UI panel ids — is fully aligned with zero duplicate keys
and no dangling references. The mission board and prompt library both reference
the cache-freshness work.

The single drift is **documentation lag**: `docs/jarvis_docs_index` is scoped to
commit `da1f1ee` and does not yet list the `cache_freshness` section. This is
labeled and non-blocking.

---

## 9. Non-blocking warnings

- `docs/jarvis_docs_index/report.json` is scoped to `da1f1ee` and does not yet
  list `cache_freshness` (added in Step 15) — documentation lag only.
- The Step 17 spec wrote the cache panel id as `pCacheFresh`; the actual id is
  `pCacheFreshness` — naming shorthand, not drift.
- Large untracked backlog keeps `commander_snapshot` yellow (conservative by
  design).
- `/money-spartan` may report a non-required 404 in the route smoke report.
- A corrupted `hydra ` directory can break bare pytest collection, so the scoped
  pytest command (`--rootdir=tests`) is used.

---

## 10. Recommended Step 18

Refresh `docs/jarvis_docs_index` (`report.json` + `report.md`): add the
`cache_freshness` api section, add the `cache_freshness` `system_map` panel and
the Step 16/17 memos to the tracked-data file list, raise `api_sections` to 22,
and update `audited_through_commit` to the latest JARVIS commit.
