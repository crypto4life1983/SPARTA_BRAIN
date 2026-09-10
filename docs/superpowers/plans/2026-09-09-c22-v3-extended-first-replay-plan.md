# C22 V3_EXTENDED Labels + First Deterministic Replay — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the V3_EXTENDED label artifact over the full Signum GC collection and a deterministic, no-PnL dry-run replay over the 81/82-window collection, reusing the existing V2 contract and Phase A/B1 contracts, so that the fee-honest replay can execute once its human-gated inputs exist.

**Architecture:** Three additive pieces. (1) A new V3 runner that calls the unchanged V2 range contract with frozen run profiles. (2) A new pure ledger module (`sparta_commander/c22_replay_ledger_contract.py`) implementing the already-specified execution rules (next-open fills from the following export, exits-before-entries, deterministic ordering, 100% NAV cap with deterministic rejection, spec exit rules, END_OF_TEST finalization). (3) A dry-run runner that feeds V2 entries plus the full exit path through the ledger and writes a report under `reports/c22_gc_replay_dry_run/`. The fee-honest runner (Task 6) is specified but stays blocked on human-gated data.

**Tech Stack:** Python 3.14 stdlib only (repo rule: no ccxt, no network in research tools), pytest. Venv `C:\SPARTA_BRAIN\.venv`.

**Spec:** `docs/superpowers/specs/2026-09-09-c22-v3-extended-first-replay-audit.md` (audit); binding upstream specs: `reports/c22_gc_replay_spec/c22_gc_replay_specification_phase_a.json` (sha `9bf10af3…`), `sparta_commander/c22_forward_exit_data_readiness_contract.py`, `sparta_commander/c22_execution_data_short_instrument_feasibility_contract.py`.

## Global Constraints

- NEVER modify: any file under `data/external_signum_trend_radar_gc*/`, the V2 artifact `detector_labels/c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json`, any existing `sparta_commander/c22_*.py` or `external_signum_trend_radar_gc_*.py` module, any existing `tools/c22_*.py`, or the strategy rules (label rules, exit rules, sizing 8/2/3/5, no max hold, 0.65 TP, 0.98 bear-high multiplier).
- Every new tool is READ-ONLY by default and writes only under `--execute-build` plus an exact token; never overwrites; atomic writes; no network; no git commit inside tools.
- Entry cutoff for the first replay = `2026-07-15` (spec `NO_NEW_ENTRY_AFTER`). V3 labels dated after the cutoff are `EXIT_ONLY` evidence, never entries.
- Fills reference the OPEN of the next executable candle, sourced only from the following day's export (`indicators.data[-1].ohlc.o` where `data[-1].date == decision_date`). No invented prices; missing next bar = fail-closed record.
- Sizing % NAV: `BEAR_SHORT=5.0`, `HEDGE_SHORT=3.0`, `LONG_ENTRY` breakout within 25 days `=8.0`, otherwise `=2.0`; gross cap `100.0`; rejection, never resize; one position per asset; no same-bar fill.
- Exits before entries on every session; ordering `decision_date_asc → market_rank_asc → symbol_asc`.
- END_OF_TEST: last admitted export date; open positions are counted, valued only in a separate truncation diagnostic with `exit_reason="end_of_data"`, excluded from decisive metrics, and force the decisive verdict to `BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA`.
- Tests run from `C:\SPARTA_BRAIN\tests` with `PYTHONPATH=C:\SPARTA_BRAIN` (root collection is broken by a stray `"hydra ` directory; do not delete it).
- Commit messages follow the repo pattern `Add C22 …`; one commit per task; no push.

---

## Task 0: Operator decisions and actions (no code)

These are human-only. Tasks 1–5 are implementable before they are resolved; Task 6 is not.

- [ ] **H1 – 2026-08-16 gap.** Operator-directed `get-trendradar-daily(detector="gc", assetClass="crypto", runDate="2026-08-16", includeIndicators=true)`, save the JSON to a clean folder, run `C22_GC_DROP_FOLDER=<folder> python tools\c22_signum_gc_download_pickup_once.py`. Precedent: decision log 2026-08-06. If Signum returns no run for that date, record `NO_SIGNUM_RUN_2026-08-16` and use the two-segment profile in Task 1.
- [ ] **H2 – Record the pending reviews:** Phase A REV1 accept/revise; B1, B2, B3 accept/revise. Without ACCEPT on Phase A the dry run is still buildable but its report must carry `SPEC_STATUS=REV1_NOT_YET_ACCEPTED`.
- [ ] **H3 – Weekend session rule** (`CALENDAR` vs `WEEKDAY`). The dry run reports both; the fee-honest run needs one pinned.
- [ ] **H4 – Short-instrument path:** authorize B3 stage 1–3 fetches, or accept a long-only decisive run (n=13), or accept shorts as non-decisive diagnostic only.
- [ ] **H5 – Cost base case:** supply T1/T2 fee schedules per venue + spread/slippage evidence; freeze via gate `C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW`.
- [ ] **H6 – Out-of-radar exit prices:** authorize an OHLC fetch for the affected symbols or accept fail-closed handling.
- [ ] **H7 – 2026-06-26 re-admission note** in `_quarantine/2026-06-26/` referencing the V2 pin (documentation only).

---

## Task 1: V3_EXTENDED label runner (reuses V2 contract unchanged)

**Files:**
- Create: `tools/c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once.py`
- Create: `tests/test_c22_signum_trend_radar_gc_v3_extended_runner_gate.py`

**Interfaces:**
- Consumes: `_v2.build_range_multi_window_manifest(window_inputs, *, start_date, end_date, expected_window_count, expected_rows_per_window, expected_total_rows)`, `_v2.validate_range_multi_window(record)`, `_v2.build_v2_aggregate_payload(record, agg_labels)`, `_v2.canonical_v2_artifact_bytes(payload)`, `_v2.v2_artifact_filename(start, end, count)`; `collect_v2_window_inputs(data_dir, expected_dates)` and `write_artifact(...)` from the V2 runner module `tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once` (imported, not copied).
- Produces: `RUN_PROFILES: dict[str, dict]`, `authorize_v3_write(execute_build: bool, token: str|None) -> dict`, `run_profile(name: str) -> tuple[dict, list]`, CLI `--profile`, `--execute-build`, `--build-token`.

- [ ] **Step 1: Write the failing gate tests**

```python
# tests/test_c22_signum_trend_radar_gc_v3_extended_runner_gate.py
import importlib, inspect
import pytest

runner = importlib.import_module(
    "tools.c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once")
TOKEN = "HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY"


def test_profiles_are_frozen_and_arithmetically_consistent():
    assert set(runner.RUN_PROFILES) == {
        "V3_EXTENDED_82W", "V3_EXTENDED_SEG_A_57W", "V3_EXTENDED_SEG_B_24W"}
    p = runner.RUN_PROFILES["V3_EXTENDED_82W"]
    assert (p["start"], p["end"], p["windows"], p["rows"], p["total"]) == (
        "2026-06-20", "2026-09-09", 82, 50, 4100)
    a = runner.RUN_PROFILES["V3_EXTENDED_SEG_A_57W"]
    assert (a["start"], a["end"], a["windows"], a["total"]) == ("2026-06-20", "2026-08-15", 57, 2850)
    b = runner.RUN_PROFILES["V3_EXTENDED_SEG_B_24W"]
    assert (b["start"], b["end"], b["windows"], b["total"]) == ("2026-08-17", "2026-09-09", 24, 1200)
    for q in runner.RUN_PROFILES.values():
        assert q["windows"] * q["rows"] == q["total"]


def test_gate_refuses_without_option_or_token():
    assert runner.authorize_v3_write(False, None)["authorized"] is False
    assert runner.authorize_v3_write(True, None)["reason"] == "missing_v3_build_token"
    assert runner.authorize_v3_write(False, TOKEN)["authorized"] is False
    assert runner.authorize_v3_write(True, "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")["reason"] == "wrong_v3_build_token"


def test_gate_option_plus_exact_token_authorized():
    assert runner.authorize_v3_write(True, TOKEN)["authorized"] is True


def test_gate_signature_cannot_consult_execution_flags():
    assert list(inspect.signature(runner.authorize_v3_write).parameters) == ["execute_build", "token"]


def test_artifact_name_keeps_v2_basename_and_cannot_collide_with_26w():
    name = runner.artifact_name_for("V3_EXTENDED_82W")
    assert name == "c22_gc_real_candle_entry_labels_multiwindow_v2_82w_2026-06-20_2026-09-09.json"
    assert name != "c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json"


def test_dry_run_profile_reports_without_writing(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "OUT_DIR", tmp_path)
    record, labels = runner.run_profile("V3_EXTENDED_SEG_B_24W")
    assert record["expected_window_count"] == 24
    assert record["verdict"] in (
        "C22_V2_RANGE_MULTI_WINDOW_LABEL_MANIFEST_READY_BUILD_GATED",
        "C22_V2_RANGE_MULTI_WINDOW_LABEL_MANIFEST_BLOCKED")
    assert list(tmp_path.iterdir()) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `C:\SPARTA_BRAIN\tests`): `set PYTHONPATH=C:\SPARTA_BRAIN && ..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --rootdir=. test_c22_signum_trend_radar_gc_v3_extended_runner_gate.py`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write the runner**

```python
"""Candidate #22 -- Signum Trend Radar GC V3_EXTENDED MULTI-WINDOW REAL-CANDLE LABELS RUNNER
(READ-ONLY DRY-RUN by default; FAILS CLOSED on build; RESEARCH ONLY; ADDITIVE to V2).

Reuses the UNCHANGED V2 range contract with explicitly frozen V3 run profiles. Labels after
2026-07-15 are EXIT_ONLY evidence under the accepted replay spec (NO_NEW_ENTRY_AFTER) and are
never replay entries. Writing requires BOTH --execute-build AND the exact token
HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY (via --build-token or C22_V3_BUILD_TOKEN).
Never overwrites; never mutates frozen sources; never fetches; never replays; never commits.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E402,E501
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as _v2run  # noqa: E402

DATA_DIR = _v2run.DATA_DIR
OUT_DIR = _v2run.OUT_DIR
V3_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY"
ENTRY_CUTOFF = "2026-07-15"   # spec NO_NEW_ENTRY_AFTER; later windows are EXIT_ONLY evidence

RUN_PROFILES = {
    "V3_EXTENDED_82W":       {"start": "2026-06-20", "end": "2026-09-09", "windows": 82, "rows": 50, "total": 4100},
    "V3_EXTENDED_SEG_A_57W": {"start": "2026-06-20", "end": "2026-08-15", "windows": 57, "rows": 50, "total": 2850},
    "V3_EXTENDED_SEG_B_24W": {"start": "2026-08-17", "end": "2026-09-09", "windows": 24, "rows": 50, "total": 1200},
}


def authorize_v3_write(execute_build, token):
    if not execute_build:
        return {"authorized": False, "reason": "execute_build_not_requested"}
    if not token:
        return {"authorized": False, "reason": "missing_v3_build_token"}
    if token != V3_BUILD_TOKEN:
        return {"authorized": False, "reason": "wrong_v3_build_token"}
    return {"authorized": True, "reason": "option_plus_exact_v3_token"}


def artifact_name_for(profile):
    p = RUN_PROFILES[profile]
    return _v2.v2_artifact_filename(p["start"], p["end"], p["windows"])


def run_profile(profile):
    p = RUN_PROFILES[profile]
    expected = _v2._v1._daterange(p["start"], p["end"])
    inputs = _v2run.collect_v2_window_inputs(DATA_DIR, expected)
    record, labels = _v2.build_range_multi_window_manifest(
        inputs, start_date=p["start"], end_date=p["end"], expected_window_count=p["windows"],
        expected_rows_per_window=p["rows"], expected_total_rows=p["total"])
    record["v3_profile"] = profile
    record["entry_cutoff_for_replay"] = ENTRY_CUTOFF
    record["exit_only_windows"] = [d for d in record.get("window_dates", []) if d > ENTRY_CUTOFF]
    return record, labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="V3_EXTENDED_82W", choices=sorted(RUN_PROFILES))
    ap.add_argument("--execute-build", action="store_true")
    ap.add_argument("--build-token", default=os.environ.get("C22_V3_BUILD_TOKEN"))
    a = ap.parse_args()
    record, labels = run_profile(a.profile)
    validation = _v2.validate_range_multi_window(record)
    gate = authorize_v3_write(a.execute_build, a.build_token)
    written = None
    if gate["authorized"] and _v2run.manifest_write_eligible(record, validation):
        payload = _v2.build_v2_aggregate_payload(record, labels)
        written = _v2run.write_artifact(OUT_DIR / artifact_name_for(a.profile),
                                        _v2.canonical_v2_artifact_bytes(payload))
    print(json.dumps({"profile": a.profile, "verdict": record.get("verdict"),
                      "valid": validation["valid"], "failures": validation["failures"][:10],
                      "windows": record.get("window_count"), "gate": gate,
                      "written": str(written) if written else None}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Note for the implementer: confirm the exact names `record["window_dates"]`, `record["window_count"]`, `record["verdict"]`, `_v2run.manifest_write_eligible`, `_v2run.write_artifact` against `tools/c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once.py:94-113` and the V2 contract before use; adapt the key names only, never the contract.

- [ ] **Step 4: Run tests to verify they pass**

Same command as Step 2. Expected: 6 passed. The dry-run test must leave `tmp_path` empty.

- [ ] **Step 5: Dry-run all three profiles and record the verdicts**

Run: `..\.venv\Scripts\python.exe tools\c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once.py --profile V3_EXTENDED_SEG_A_57W` (and `SEG_B_24W`, `82W`).
Expected today: SEG_A and SEG_B `valid: true`; `82W` `valid: false` with `dates_not_exactly_expected_contiguous_range` until H1 is done.

- [ ] **Step 6: Commit**

```bash
git add tools/c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once.py tests/test_c22_signum_trend_radar_gc_v3_extended_runner_gate.py
git commit -m "Add C22 V3_EXTENDED label runner over the V2 range contract"
```

---

## Task 2: V3 evidence integrity report (byte-identical rebuild check)

**Files:**
- Create: `tools/c22_signum_gc_v3_label_evidence_integrity_report_once.py`
- Create: `tests/test_c22_signum_gc_v3_label_evidence_integrity_report.py`

**Interfaces:**
- Consumes: `provenance_accounting(...)`, `render_markdown(...)`, `canonical_report_bytes(...)` from `tools.c22_signum_gc_v2_label_evidence_integrity_report_once` (import the pure helpers; re-implement only `run_report` with V3 profile constants — do not edit the V2 report tool); `RUN_PROFILES`, `run_profile`, `artifact_name_for` from Task 1.
- Produces: `run_v3_report(profile: str) -> dict` with keys `artifact_sha256_on_disk`, `artifact_sha256_rebuilt`, `byte_identical_rebuild`, `label_counts`, `exit_only_window_count`, `provenance`; CLI `--profile`, `--execute-write` writes `reports/c22_gc_label_pipeline_v3_evidence/<profile>.json|.md`.

- [ ] **Step 1: Write the failing test**

```python
import importlib, hashlib
rep = importlib.import_module("tools.c22_signum_gc_v3_label_evidence_integrity_report_once")
runner = importlib.import_module(
    "tools.c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once")


def test_rebuild_matches_when_artifact_present(tmp_path, monkeypatch):
    # build SEG_B into tmp via the runner's write path, then verify the report rebuilds it byte-identically
    monkeypatch.setattr(runner, "OUT_DIR", tmp_path)
    monkeypatch.setattr(rep, "ARTIFACT_DIR", tmp_path)
    record, labels = runner.run_profile("V3_EXTENDED_SEG_B_24W")
    payload = runner._v2.build_v2_aggregate_payload(record, labels)
    blob = runner._v2.canonical_v2_artifact_bytes(payload)
    (tmp_path / runner.artifact_name_for("V3_EXTENDED_SEG_B_24W")).write_bytes(blob)
    r = rep.run_v3_report("V3_EXTENDED_SEG_B_24W")
    assert r["byte_identical_rebuild"] is True
    assert r["artifact_sha256_on_disk"] == hashlib.sha256(blob).hexdigest()
    assert r["exit_only_window_count"] == 24
    assert r["label_counts"]["NONE"] + r["label_counts"]["LONG_ENTRY"] + \
        r["label_counts"]["BEAR_SHORT"] + r["label_counts"]["HEDGE_SHORT"] + r["label_counts"]["SKIP"] == 1200


def test_report_is_read_only_without_execute_write(tmp_path, monkeypatch):
    monkeypatch.setattr(rep, "REPORT_DIR", tmp_path)
    rep.main_with_args(["--profile", "V3_EXTENDED_SEG_B_24W"])
    assert list(tmp_path.iterdir()) == []
```

- [ ] **Step 2: Run to verify it fails** — `ModuleNotFoundError`.
- [ ] **Step 3: Implement** `run_v3_report(profile)`: locate `ARTIFACT_DIR / artifact_name_for(profile)`; if absent return `{"status": "ARTIFACT_ABSENT", "byte_identical_rebuild": False, ...}`; else sha the file, call `runner.run_profile(profile)` → `build_v2_aggregate_payload` → `canonical_v2_artifact_bytes`, sha the rebuild, compare; count labels; `exit_only_window_count = len(record["exit_only_windows"])`; provenance via the imported `provenance_accounting`. `main_with_args(argv)` parses `--profile`, `--execute-write`; writes only with the flag using `_write_atomic` copied from `tools/c22_forward_and_execution_data_readiness_report_once.py:224`.
- [ ] **Step 4: Run tests** — expected 2 passed.
- [ ] **Step 5: Commit** — `git commit -m "Add C22 V3_EXTENDED label evidence integrity report"`.

---

## Task 3: Replay ledger contract — sessions and next-open fills

**Files:**
- Create: `sparta_commander/c22_replay_ledger_contract.py`
- Create: `tests/test_c22_replay_ledger_sessions.py`

**Interfaces:**
- Consumes: export files via `sparta_commander.c22_signum_gc_data_collection_tracker_contract.EXPORT_GLOB` / `DATA_DIR`; `_date_from_filename`.
- Produces:
  - `load_session_index(data_dir: Path) -> dict[str, dict[str, dict]]` — `{run_date: {symbol: row}}`, legacy undated file mapped to its content runDate.
  - `latest_candle(row: dict) -> dict` — `{"date","o","h","l","c","upper","filter","trend"}`.
  - `next_export_date(index, date: str, session_rule: str) -> str|None` — `CALENDAR`: the next present export strictly after `date`; `WEEKDAY`: the next present export whose weekday < 5.
  - `next_executable_open(index, decision_date: str, symbol: str, session_rule: str) -> dict` — `{"status": "OK"|"NO_EXECUTABLE_NEXT_BAR"|"NO_NEXT_SESSION"|"CANDLE_DATE_MISMATCH", "fill_date": str|None, "price": float|None, "source_export": str|None}`.
  - Constants: `SESSION_RULES = ("CALENDAR", "WEEKDAY")`, `STATUS_OK = "OK"`, `STATUS_NO_NEXT_BAR = "NO_EXECUTABLE_NEXT_BAR"`, `STATUS_NO_NEXT_SESSION = "NO_NEXT_SESSION"`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_c22_replay_ledger_sessions.py
import json
from pathlib import Path
import pytest
import sparta_commander.c22_replay_ledger_contract as L


def _row(symbol, dates_ohlc, rank=1):
    data = [{"date": d, "ohlc": {"o": o, "h": o * 1.01, "l": o * 0.99, "c": c}, "volume": 1,
             "gc": {"upper": 10.0, "filter": 9.0, "lower": 8.0, "trend": "Green"}} for d, o, c in dates_ohlc]
    return {"symbol": symbol, "runDate": None, "marketRank": rank, "marketCap": 1.0,
            "indicators": {"data": data, "cmcRefPriceUsd": c}}


def _write_export(dir_, run_date, rows):
    for r in rows:
        r["runDate"] = run_date
    (dir_ / f"gc_crypto_trendradar_daily_{run_date.replace('-', '')}.json").write_text(
        json.dumps({"limited": False, "total": len(rows), "results": rows}), encoding="utf-8")


@pytest.fixture
def idx_dir(tmp_path):
    # D=07-10 (Fri) candle 07-09 ; D+1=07-11 (Sat) candle 07-10 ; D+2=07-13 (Mon) candle 07-12 ; 07-12 missing
    _write_export(tmp_path, "2026-07-10", [_row("BINANCE:AAAUSDT", [("2026-07-08", 1.0, 1.1), ("2026-07-09", 1.1, 1.2)])])
    _write_export(tmp_path, "2026-07-11", [_row("BINANCE:AAAUSDT", [("2026-07-09", 1.1, 1.2), ("2026-07-10", 1.25, 1.3)])])
    _write_export(tmp_path, "2026-07-13", [_row("BINANCE:BBBUSDT", [("2026-07-11", 5.0, 5.1), ("2026-07-12", 5.2, 5.3)])])
    return tmp_path


def test_load_index_maps_run_dates_and_symbols(idx_dir):
    idx = L.load_session_index(idx_dir)
    assert sorted(idx) == ["2026-07-10", "2026-07-11", "2026-07-13"]
    assert "BINANCE:AAAUSDT" in idx["2026-07-10"]


def test_latest_candle_is_last_element(idx_dir):
    idx = L.load_session_index(idx_dir)
    c = L.latest_candle(idx["2026-07-10"]["BINANCE:AAAUSDT"])
    assert (c["date"], c["o"], c["c"], c["upper"], c["filter"], c["trend"]) == ("2026-07-09", 1.1, 1.2, 10.0, 9.0, "Green")


def test_next_open_calendar_rule_uses_following_export(idx_dir):
    idx = L.load_session_index(idx_dir)
    r = L.next_executable_open(idx, "2026-07-10", "BINANCE:AAAUSDT", "CALENDAR")
    assert r == {"status": "OK", "fill_date": "2026-07-10", "price": 1.25, "source_export": "2026-07-11"}


def test_next_open_weekday_rule_skips_saturday_export(idx_dir):
    idx = L.load_session_index(idx_dir)
    r = L.next_executable_open(idx, "2026-07-10", "BINANCE:AAAUSDT", "WEEKDAY")
    # next weekday export is 07-13 whose latest candle is 07-12, not 07-10 -> mismatch, never invent
    assert r["status"] == "CANDLE_DATE_MISMATCH" and r["price"] is None


def test_next_open_symbol_dropped_from_top50_is_fail_closed(idx_dir):
    idx = L.load_session_index(idx_dir)
    r = L.next_executable_open(idx, "2026-07-11", "BINANCE:AAAUSDT", "CALENDAR")
    assert r["status"] == "NO_EXECUTABLE_NEXT_BAR" and r["price"] is None


def test_next_open_after_last_export_is_no_next_session(idx_dir):
    idx = L.load_session_index(idx_dir)
    r = L.next_executable_open(idx, "2026-07-13", "BINANCE:BBBUSDT", "CALENDAR")
    assert r["status"] == "NO_NEXT_SESSION"


def test_session_rule_validated(idx_dir):
    idx = L.load_session_index(idx_dir)
    with pytest.raises(ValueError):
        L.next_executable_open(idx, "2026-07-10", "BINANCE:AAAUSDT", "MONTHLY")
```

- [ ] **Step 2: Run to verify failure** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

```python
"""Candidate #22 -- REPLAY LEDGER CONTRACT (PURE; DETERMINISTIC; RESEARCH ONLY; NO PnL BY DEFAULT).
Implements the execution rules already frozen in the Phase A replay spec and the B1 execution-data
contract: next-executable-OPEN fills sourced ONLY from the following export's latest closed candle,
exits-before-entries, deterministic ordering, 100% NAV gross cap with deterministic rejection, the
frozen exit rules, and END_OF_TEST finalization. Reads nothing but local exports; fetches nothing;
invents no price; never mutates inputs.
"""
from __future__ import annotations

import json
from datetime import date as _date, timedelta as _td
from pathlib import Path
from typing import Any

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk

SESSION_RULES = ("CALENDAR", "WEEKDAY")
STATUS_OK = "OK"
STATUS_NO_NEXT_BAR = "NO_EXECUTABLE_NEXT_BAR"
STATUS_NO_NEXT_SESSION = "NO_NEXT_SESSION"
STATUS_CANDLE_MISMATCH = "CANDLE_DATE_MISMATCH"


def load_session_index(data_dir: Path) -> dict:
    index: dict = {}
    for p in sorted(Path(data_dir).glob(_trk.EXPORT_GLOB)):
        if not p.is_file():
            continue
        parsed = json.loads(p.read_bytes().decode("utf-8"))
        rows = parsed.get("results") or []
        run_date = _trk._date_from_filename(p.name) or (rows[0].get("runDate") if rows else None)
        if not run_date or run_date in index:
            continue                       # legacy undated file only fills a date not already present
        index[run_date] = {r["symbol"]: r for r in rows}
    return index


def latest_candle(row: dict) -> dict:
    d = row["indicators"]["data"][-1]
    return {"date": d["date"], "o": d["ohlc"]["o"], "h": d["ohlc"]["h"], "l": d["ohlc"]["l"],
            "c": d["ohlc"]["c"], "upper": d["gc"]["upper"], "filter": d["gc"]["filter"],
            "trend": d["gc"]["trend"]}


def next_export_date(index: dict, date: str, session_rule: str):
    if session_rule not in SESSION_RULES:
        raise ValueError("unknown session_rule:%s" % session_rule)
    for d in sorted(index):
        if d <= date:
            continue
        if session_rule == "WEEKDAY" and _date.fromisoformat(d).weekday() >= 5:
            continue
        return d
    return None


def next_executable_open(index: dict, decision_date: str, symbol: str, session_rule: str) -> dict:
    nxt = next_export_date(index, decision_date, session_rule)
    out = {"status": STATUS_NO_NEXT_SESSION, "fill_date": None, "price": None, "source_export": None}
    if nxt is None:
        return out
    row = index[nxt].get(symbol)
    if row is None:
        out["status"] = STATUS_NO_NEXT_BAR
        out["source_export"] = nxt
        return out
    c = latest_candle(row)
    if c["date"] != decision_date:          # next executable candle must be the one dated exactly D
        out.update({"status": STATUS_CANDLE_MISMATCH, "source_export": nxt})
        return out
    return {"status": STATUS_OK, "fill_date": c["date"], "price": c["o"], "source_export": nxt}
```

Implementer note: keep the function free of any fallback that would search later exports for a price; a mismatch is a fail-closed record, never a substitution.

- [ ] **Step 4: Run tests** — expected 7 passed.
- [ ] **Step 5: Commit** — `git commit -m "Add C22 replay ledger session index and next-open fill lookup"`.

---

## Task 4: Replay ledger contract — sizing, ordering, exits, cap, END_OF_TEST

**Files:**
- Modify: `sparta_commander/c22_replay_ledger_contract.py` (append)
- Create: `tests/test_c22_replay_ledger_rules.py`

**Interfaces:**
- Produces:
  - Constants `SIZING_PCT_NAV = {"LONG_ENTRY_BREAKOUT_25D": 8.0, "LONG_ENTRY": 2.0, "HEDGE_SHORT": 3.0, "BEAR_SHORT": 5.0}`, `MAX_GROSS_PCT_NAV = 100.0`, `SHORT_TP_MULT = 0.65`, `BREAKOUT_WINDOW_DAYS = 25`, `END_OF_TEST_REASON = "end_of_data"`, `BLOCKED_INSUFFICIENT_FORWARD = "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"`.
  - `sizing_pct(signal: str, breakout_within_25d: bool) -> float`
  - `breakout_within_window(row: dict, decision_date: str) -> bool` — `row.get("breakoutDate")` parsed as ISO date, True iff `0 <= decision − breakoutDate <= 25` days.
  - `entry_sort_key(label: dict) -> tuple` — `(decision_date, market_rank, symbol)`.
  - `evaluate_exit(position: dict, candle: dict|None) -> str|None` — returns `"OUT_OF_RADAR"` if `candle is None`; long: `"LONG_BELOW_UPPER"` if `c < upper`; short: `"SHORT_STOP_ABOVE_FILTER"` if `c > filter`, else `"SHORT_TP_0_65"` if `c <= 0.65*entry_price`; else `None`.
  - `new_state() -> dict` — `{"committed_pct": 0.0, "open": {}, "closed": [], "rejected": [], "fail_closed": [], "pending_entries": [], "pending_exits": []}`.
  - `process_session(state, session_date, entry_labels: list[dict], index, session_rule) -> dict` — (1) settle pending fills for this session (exits first, then entries) using `next_executable_open` results computed at decision time; (2) evaluate exits for every open position on this session's candle and queue them; (3) queue new entries in `entry_sort_key` order, rejecting `ONE_POSITION_PER_ASSET` duplicates and `NAV_CAP_EXCEEDED` when `committed_pct + size > 100.0`; capacity freed by exits queued in step 2 is available to entries in the same session's settlement, which happens on the next session (spec: exits before entries at settlement).
  - `finalize(state, last_session: str, index) -> dict` — `{"end_of_test_date", "open_trade_count", "truncation_diagnostic": [{symbol, side, entry_price, mark_close, mark_date, exit_reason: "end_of_data"}], "decisive_status": "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"|"ALL_POSITIONS_CLOSED_NATURALLY"}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_c22_replay_ledger_rules.py
import sparta_commander.c22_replay_ledger_contract as L


def test_sizing_matches_frozen_spec():
    assert L.sizing_pct("BEAR_SHORT", False) == 5.0
    assert L.sizing_pct("HEDGE_SHORT", False) == 3.0
    assert L.sizing_pct("LONG_ENTRY", True) == 8.0
    assert L.sizing_pct("LONG_ENTRY", False) == 2.0


def test_breakout_window_is_inclusive_25_days():
    assert L.breakout_within_window({"breakoutDate": "2026-06-20"}, "2026-07-15") is True
    assert L.breakout_within_window({"breakoutDate": "2026-06-19"}, "2026-07-15") is False
    assert L.breakout_within_window({"breakoutDate": None}, "2026-07-15") is False
    assert L.breakout_within_window({"breakoutDate": "2026-07-16"}, "2026-07-15") is False


def test_entry_sort_key_is_date_rank_symbol():
    labels = [{"decision_date": "2026-07-01", "market_rank": 5, "symbol": "B"},
              {"decision_date": "2026-07-01", "market_rank": 5, "symbol": "A"},
              {"decision_date": "2026-06-30", "market_rank": 9, "symbol": "Z"}]
    assert [x["symbol"] for x in sorted(labels, key=L.entry_sort_key)] == ["Z", "A", "B"]


def test_exit_rules():
    long_pos = {"side": "LONG", "entry_price": 10.0}
    short_pos = {"side": "SHORT", "entry_price": 10.0}
    assert L.evaluate_exit(long_pos, None) == "OUT_OF_RADAR"
    assert L.evaluate_exit(long_pos, {"c": 9.9, "upper": 10.0, "filter": 9.0}) == "LONG_BELOW_UPPER"
    assert L.evaluate_exit(long_pos, {"c": 10.0, "upper": 10.0, "filter": 9.0}) is None
    assert L.evaluate_exit(short_pos, {"c": 9.1, "upper": 10.0, "filter": 9.0}) == "SHORT_STOP_ABOVE_FILTER"
    assert L.evaluate_exit(short_pos, {"c": 6.5, "upper": 10.0, "filter": 9.0}) == "SHORT_TP_0_65"
    assert L.evaluate_exit(short_pos, {"c": 8.0, "upper": 10.0, "filter": 9.0}) is None


def _index_two_days(price_open=2.0):
    row = lambda sym, rank: {"symbol": sym, "marketRank": rank, "breakoutDate": None, "indicators": {"data": [
        {"date": "2026-07-01", "ohlc": {"o": price_open, "h": 2.1, "l": 1.9, "c": 2.05}, "gc": {"upper": 1.0, "filter": 0.9, "trend": "Green"}}]}}
    return {"2026-07-01": {"S1": row("S1", 1), "S2": row("S2", 2)},
            "2026-07-02": {"S1": row("S1", 1), "S2": row("S2", 2)}}


def test_nav_cap_rejects_deterministically_never_resizes():
    idx = _index_two_days()
    st = L.new_state()
    st["committed_pct"] = 96.0
    labels = [{"decision_date": "2026-07-01", "symbol": "S1", "market_rank": 1, "signal": "BEAR_SHORT"},
              {"decision_date": "2026-07-01", "symbol": "S2", "market_rank": 2, "signal": "HEDGE_SHORT"}]
    st = L.process_session(st, "2026-07-01", labels, idx, "CALENDAR")
    rejected = [r for r in st["rejected"] if r["reason"] == "NAV_CAP_EXCEEDED"]
    assert [r["symbol"] for r in rejected] == ["S1"]          # 96 + 5 > 100 -> rejected, not resized
    assert [p["symbol"] for p in st["pending_entries"]] == ["S2"]   # 96 + 3 <= 100 -> queued at 3.0
    assert st["pending_entries"][0]["size_pct"] == 3.0


def test_one_position_per_asset():
    idx = _index_two_days()
    st = L.new_state()
    st["open"]["S1"] = {"symbol": "S1", "side": "SHORT", "entry_price": 2.0, "size_pct": 5.0}
    st = L.process_session(st, "2026-07-01", [{"decision_date": "2026-07-01", "symbol": "S1", "market_rank": 1, "signal": "BEAR_SHORT"}], idx, "CALENDAR")
    assert st["rejected"][0]["reason"] == "ONE_POSITION_PER_ASSET"


def test_finalize_blocks_when_positions_open_and_reports_truncation_diagnostic():
    idx = _index_two_days()
    st = L.new_state()
    st["open"]["S1"] = {"symbol": "S1", "side": "SHORT", "entry_price": 2.5, "size_pct": 5.0}
    out = L.finalize(st, "2026-07-02", idx)
    assert out["open_trade_count"] == 1
    assert out["decisive_status"] == "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
    d = out["truncation_diagnostic"][0]
    assert (d["exit_reason"], d["mark_close"], d["mark_date"]) == ("end_of_data", 2.05, "2026-07-01")


def test_finalize_clean_when_nothing_open():
    out = L.finalize(L.new_state(), "2026-07-02", _index_two_days())
    assert out["open_trade_count"] == 0 and out["decisive_status"] == "ALL_POSITIONS_CLOSED_NATURALLY"
```

- [ ] **Step 2: Run to verify failure** — `AttributeError` on the new names.

- [ ] **Step 3: Implement (append to the module)**

```python
SIZING_PCT_NAV = {"LONG_ENTRY_BREAKOUT_25D": 8.0, "LONG_ENTRY": 2.0, "HEDGE_SHORT": 3.0, "BEAR_SHORT": 5.0}
MAX_GROSS_PCT_NAV = 100.0
SHORT_TP_MULT = 0.65
BREAKOUT_WINDOW_DAYS = 25
END_OF_TEST_REASON = "end_of_data"
BLOCKED_INSUFFICIENT_FORWARD = "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
CLOSED_NATURALLY = "ALL_POSITIONS_CLOSED_NATURALLY"
SIDE_OF = {"LONG_ENTRY": "LONG", "HEDGE_SHORT": "SHORT", "BEAR_SHORT": "SHORT"}


def sizing_pct(signal: str, breakout_within_25d: bool) -> float:
    if signal == "LONG_ENTRY":
        return SIZING_PCT_NAV["LONG_ENTRY_BREAKOUT_25D" if breakout_within_25d else "LONG_ENTRY"]
    return SIZING_PCT_NAV[signal]


def breakout_within_window(row: dict, decision_date: str) -> bool:
    bd = row.get("breakoutDate")
    if not bd:
        return False
    delta = (_date.fromisoformat(decision_date) - _date.fromisoformat(str(bd)[:10])).days
    return 0 <= delta <= BREAKOUT_WINDOW_DAYS


def entry_sort_key(label: dict) -> tuple:
    return (label["decision_date"], int(label["market_rank"]), label["symbol"])


def evaluate_exit(position: dict, candle):
    if candle is None:
        return "OUT_OF_RADAR"
    if position["side"] == "LONG":
        return "LONG_BELOW_UPPER" if candle["c"] < candle["upper"] else None
    if candle["c"] > candle["filter"]:
        return "SHORT_STOP_ABOVE_FILTER"
    if candle["c"] <= SHORT_TP_MULT * position["entry_price"]:
        return "SHORT_TP_0_65"
    return None


def new_state() -> dict:
    return {"committed_pct": 0.0, "open": {}, "closed": [], "rejected": [], "fail_closed": [],
            "pending_entries": [], "pending_exits": []}


def _settle(state: dict, session_date: str) -> None:
    # exits first (free NAV), then entries -- both were priced at decision time from the NEXT export
    still = []
    for ex in state["pending_exits"]:
        if ex["fill"]["fill_date"] < session_date:
            pos = state["open"].pop(ex["symbol"], None)
            if pos is not None:
                state["committed_pct"] -= pos["size_pct"]
                state["closed"].append({**pos, "exit_reason": ex["reason"], "exit_date": ex["fill"]["fill_date"],
                                        "exit_price": ex["fill"]["price"], "exit_source_export": ex["fill"]["source_export"]})
        else:
            still.append(ex)
    state["pending_exits"] = still
    still = []
    for en in state["pending_entries"]:
        if en["fill"]["fill_date"] < session_date:
            state["open"][en["symbol"]] = {"symbol": en["symbol"], "side": en["side"], "signal": en["signal"],
                                           "decision_date": en["decision_date"], "entry_date": en["fill"]["fill_date"],
                                           "entry_price": en["fill"]["price"], "size_pct": en["size_pct"],
                                           "entry_source_export": en["fill"]["source_export"]}
        else:
            still.append(en)
    state["pending_entries"] = still


def process_session(state: dict, session_date: str, entry_labels: list, index: dict, session_rule: str) -> dict:
    _settle(state, session_date)
    snapshot = index.get(session_date, {})
    # 1. exits for open positions, evaluated on this session's latest closed candle
    for sym in sorted(state["open"]):
        row = snapshot.get(sym)
        reason = evaluate_exit(state["open"][sym], latest_candle(row) if row else None)
        if reason is None or any(e["symbol"] == sym for e in state["pending_exits"]):
            continue
        fill = next_executable_open(index, session_date, sym, session_rule)
        if fill["status"] != STATUS_OK:
            state["fail_closed"].append({"symbol": sym, "kind": "EXIT", "reason": reason, "decision_date": session_date, **fill})
            continue
        state["pending_exits"].append({"symbol": sym, "reason": reason, "decision_date": session_date, "fill": fill})
    # 2. entries in deterministic order; capacity check against committed + queued
    queued = sum(e["size_pct"] for e in state["pending_entries"])
    for lab in sorted(entry_labels, key=entry_sort_key):
        sym = lab["symbol"]
        if sym in state["open"] or any(e["symbol"] == sym for e in state["pending_entries"]):
            state["rejected"].append({**lab, "reason": "ONE_POSITION_PER_ASSET"})
            continue
        row = snapshot.get(sym, {})
        size = sizing_pct(lab["signal"], breakout_within_window(row, session_date))
        if state["committed_pct"] + queued + size > MAX_GROSS_PCT_NAV + 1e-9:
            state["rejected"].append({**lab, "size_pct": size, "reason": "NAV_CAP_EXCEEDED"})
            continue
        fill = next_executable_open(index, session_date, sym, session_rule)
        if fill["status"] != STATUS_OK:
            state["fail_closed"].append({**lab, "kind": "ENTRY", **fill})
            continue
        state["pending_entries"].append({**lab, "side": SIDE_OF[lab["signal"]], "size_pct": size, "fill": fill})
        queued += size
    return state


def finalize(state: dict, last_session: str, index: dict) -> dict:
    # Fills that would settle after the last export cannot exist (next_executable_open already
    # returned NO_NEXT_SESSION), but any leftover pending is recorded fail-closed, never settled.
    for kind in ("pending_entries", "pending_exits"):
        for item in state[kind]:
            state["fail_closed"].append({**item, "kind": kind.upper(), "status": STATUS_NO_NEXT_SESSION})
        state[kind] = []
    diag = []
    for sym in sorted(state["open"]):
        pos = state["open"][sym]
        row = index.get(last_session, {}).get(sym)
        c = latest_candle(row) if row else None
        diag.append({"symbol": sym, "side": pos["side"], "entry_price": pos["entry_price"],
                     "mark_close": c["c"] if c else None, "mark_date": c["date"] if c else None,
                     "exit_reason": END_OF_TEST_REASON})
    return {"end_of_test_date": last_session, "open_trade_count": len(state["open"]),
            "truncation_diagnostic": diag,
            "decisive_status": BLOCKED_INSUFFICIENT_FORWARD if state["open"] else CLOSED_NATURALLY}
```

Implementer note: in `_settle`, `fill_date < session_date` means the fill candle (dated `decision_date`) closed before this session's export; adjust to `<=` only if the dry run proves an off-by-one against the spec's "no same-bar fill" rule, and document it in the commit.

- [ ] **Step 4: Run tests** — expected 9 passed (Task 3 + Task 4 files: 16 total).
- [ ] **Step 5: Commit** — `git commit -m "Add C22 replay ledger rules: sizing, ordering, exits, NAV cap, END_OF_TEST"`.

---

## Task 5: No-PnL deterministic dry-run runner over the 81/82-window collection

**Files:**
- Create: `tools/c22_replay_dry_run_once.py`
- Create: `tests/test_c22_replay_dry_run_gate.py`
- Output (only with token): `reports/c22_gc_replay_dry_run/c22_replay_dry_run_<session_rule>.json|.md`

**Interfaces:**
- Consumes: V2 artifact path `data/external_signum_trend_radar_gc/detector_labels/c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json` (sha pinned `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`, assert before read); `L.load_session_index`, `L.process_session`, `L.finalize`; `c22_forward_exit_data_readiness_contract.expected_export_sessions`, `readiness_from_coverage`, `initial_exit_data_range`, `extension_range`; `_write_atomic` pattern from `tools/c22_forward_and_execution_data_readiness_report_once.py:224`.
- Produces: `build_dry_run(session_rule: str) -> dict` with keys `spec_status`, `entry_cutoff`, `entries_considered` (88), `trades` (closed list), `open_trade_count`, `truncation_diagnostic`, `rejected`, `fail_closed`, `no_executable_next_bar_count`, `shorts_fail_closed_policy: "SHORT_INSTRUMENT_UNRESOLVED_DIAGNOSTIC_ONLY"`, `weekend_entry_count`, `forward_coverage` (from B1 functions through the last export), `extension_index_reached`, `decisive_status`, `sha256_inputs`; token `HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL`.

- [ ] **Step 1: Write the failing gate tests**

```python
import importlib, inspect
dr = importlib.import_module("tools.c22_replay_dry_run_once")
TOKEN = "HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL"


def test_gate_requires_option_and_exact_token():
    assert dr.authorize_write(False, None)["authorized"] is False
    assert dr.authorize_write(True, "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT")["authorized"] is False
    assert dr.authorize_write(True, TOKEN)["authorized"] is True
    assert list(inspect.signature(dr.authorize_write).parameters) == ["execute_build", "token"]


def test_dry_run_is_pnl_free_and_entry_cutoff_bound():
    r = dr.build_dry_run("CALENDAR")
    assert r["entry_cutoff"] == "2026-07-15"
    assert r["entries_considered"] == 88
    assert all(t["decision_date"] <= "2026-07-15" for t in r["trades"])
    for t in r["trades"]:
        assert "pnl" not in t and "net" not in t and "gross" not in t
    assert r["decisive_status"] in ("BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA", "ALL_POSITIONS_CLOSED_NATURALLY")
    assert r["shorts_fail_closed_policy"] == "SHORT_INSTRUMENT_UNRESOLVED_DIAGNOSTIC_ONLY"


def test_both_session_rules_are_reported_and_deterministic():
    a1, a2 = dr.build_dry_run("CALENDAR"), dr.build_dry_run("CALENDAR")
    b = dr.build_dry_run("WEEKDAY")
    assert dr.canonical_bytes(a1) == dr.canonical_bytes(a2)
    assert a1["weekend_entry_count"] == b["weekend_entry_count"]   # same labels, different fills
```

- [ ] **Step 2: Run to verify failure** — `ModuleNotFoundError`.
- [ ] **Step 3: Implement** `build_dry_run(session_rule)`: assert V2 sha; load labels where `signal in ("LONG_ENTRY","HEDGE_SHORT","BEAR_SHORT")` and `source_date <= 2026-07-15` (88 rows; map `source_date → decision_date`, `market_rank_raw → market_rank`); `index = L.load_session_index(DATA_DIR)`; iterate `for d in sorted(index)`: `L.process_session(state, d, [labels on d], index, session_rule)`; `final = L.finalize(state, max(index), index)`; `weekend_entry_count = sum(weekday(decision_date) >= 5)`; forward coverage via `expected_export_sessions("2026-07-16", max(index))` + `readiness_from_coverage`; `extension_index_reached` by iterating `extension_range(n)` until it contains `max(index)`; `spec_status = "REV1_NOT_YET_ACCEPTED"` unless a `reports/approvals/` record with `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=ACCEPT` exists; `canonical_bytes` = `json.dumps(sort_keys=True, separators=(",",":")).encode()`; `render_markdown` lists counts and the first 20 trades; `main()` with `--session-rule`, `--execute-build`, `--build-token`; writes both JSON and MD atomically only when authorized; never overwrites (suffix `_<UTC timestamp>` if a file exists).
- [ ] **Step 4: Run tests** — expected 3 passed; then run the tool read-only for both rules and paste the two summaries into the commit message body.
- [ ] **Step 5: Commit** — `git commit -m "Add C22 no-PnL deterministic replay dry run over the collected exit path"`.

---

## Task 6: Fee-honest replay runner — preconditions checker only (blocked on H4/H5/H6)

**Files:**
- Create: `tools/c22_fee_honest_replay_once.py`
- Create: `tests/test_c22_fee_honest_replay_preconditions.py`

**Interfaces:**
- Consumes: `c22_execution_data_short_instrument_feasibility_contract.COST_COMPONENTS`, `COST_RESULT_LEVELS`, `THIRTY_SEVEN_BPS_STATUS`; ledger from Tasks 3–4; `_metrics`/`_max_drawdown` copied from `tools/c21_fee_honest_replay_once.py:141-168`; random null pattern from `tools/c14_fee_honest_replay_once.py:212-260` (seed constant `RANDOM_MASTER_SEED = 20260909`); B&H from `tools/c18_h4_fee_honest_replay_once.py:187-193`; EW passive from `tools/c17_fee_honest_replay_once.py:189-204`.
- Produces: `check_preconditions() -> dict` with one boolean per gate and `all_satisfied`; `main()` exits 0 printing the checklist and `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED` unless all are true AND token `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT=ADVANCE` is supplied. The PnL body is implemented in a later plan once H5 freezes the base case; this task ships only the fail-closed shell.

- [ ] **Step 1: Write the failing test**

```python
import importlib
fr = importlib.import_module("tools.c22_fee_honest_replay_once")


def test_preconditions_enumerate_every_blocker_and_fail_closed_today():
    p = fr.check_preconditions()
    assert set(p) >= {"replay_spec_accepted", "forward_exit_contract_accepted", "execution_data_contract_accepted",
                      "dry_run_accepted", "short_instrument_selected", "cost_base_case_frozen",
                      "out_of_radar_price_source_admitted", "basis_alignment_reviewed", "all_satisfied"}
    assert p["all_satisfied"] is False


def test_cost_components_are_the_contract_ones():
    import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as X
    assert fr.COST_COMPONENTS == X.COST_COMPONENTS and fr.RESULT_LEVELS == X.COST_RESULT_LEVELS
    assert fr.SENSITIVITY_37BPS == X.THIRTY_SEVEN_BPS_STATUS == "SENSITIVITY_CASE_NOT_BASE_CASE"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** `check_preconditions()`: each flag derived from the presence of a specific approval record (`reports/approvals/*.json` containing the exact token string) or data artifact (`data/c22_short_instrument_evidence/manifests/`, `reports/c22_gc_execution_cost_base_case/*.json`); `main()` prints the checklist and refuses to run otherwise.
- [ ] **Step 4: Run tests** — 2 passed.
- [ ] **Step 5: Commit** — `git commit -m "Add C22 fee-honest replay precondition shell (fail-closed)"`.

---

## Self-review

- **Spec coverage:** M1 → Task 0/H1 + Task 1 profiles; M2 → Global constraint + Task 5 cutoff test; M3 → session_rule parameter, both reported; M4 → `NO_EXECUTABLE_NEXT_BAR` fail-closed records (Task 3/5); M5 → shorts diagnostic policy + Task 6 gate; M6 → Task 6 uses contract components, no base case invented; M7 → `finalize` + END_OF_TEST constraint; M8 → Task 6 `basis_alignment_reviewed`; M9 → `spec_status` field.
- **Placeholder scan:** none; Task 6 explicitly ships only the shell and says why.
- **Type consistency:** `next_executable_open` returns `{status, fill_date, price, source_export}` everywhere; `process_session(state, session_date, entry_labels, index, session_rule)` matches Tasks 4 and 5; token names are unique per task and none reuse an existing lifecycle token.
