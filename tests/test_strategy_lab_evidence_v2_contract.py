"""Acceptance tests for the strategy_lab.backtest.v2 evidence contract.

These tests verify the SHAPE of v2 records and the audit's read-time
checks. They never run a real backtest, never compute WFE, never
evaluate profitability, and never touch live trading. Synthetic
bar-return arrays are constructed in tmp_path scratch directories;
no file in strategy_lab/data/ is created or modified by any test.

The contract these tests pin down is documented at:
  C:\\SPARTA_RESEARCH_LAB\\robustness_audit_exp\\future_evidence_requirements.md
"""
from __future__ import annotations

import hashlib
import json
from math import isclose, prod
from pathlib import Path

import pytest

import strategy_lab.backtest_wrapper as backtest_module
import strategy_lab.evidence_pack as evidence_module
from strategy_lab.backtest_wrapper import (
    REQUIRED_V2_STR_FIELDS,
    SCHEMA_BACKTEST_V1,
    SCHEMA_BACKTEST_V2,
    BacktestConfig,
    BacktestResult,
    WindowMetric,
    make_v2_result,
    write_bar_returns_csv,
)
from strategy_lab.evidence_pack import _compute_wfe_audit_eligible

LAB_DATA_ROOT = Path(__file__).resolve().parents[1] / "strategy_lab" / "data"


def _synthetic_bar_returns(n: int) -> list[tuple[str, float]]:
    """Build a deterministic synthetic bar-return series of length n.

    Uses a small alternating +/- pattern so the cumulative product is
    well-defined and not pathological. No randomness; no live data.
    """
    rows: list[tuple[str, float]] = []
    base_day = 1  # 2024-07-01 + i days
    for i in range(n):
        ts = f"2024-07-{base_day + i:02d}T00:00:00Z"
        # Pattern: +0.01, -0.005, +0.012, -0.003, ... — bounded magnitudes
        if i % 4 == 0:
            r = 0.010
        elif i % 4 == 1:
            r = -0.005
        elif i % 4 == 2:
            r = 0.012
        else:
            r = -0.003
        rows.append((ts, r))
    return rows


def _build_v2_result(tmp_path: Path) -> BacktestResult:
    """Construct a v2-shaped BacktestResult into tmp_path/backtests/.

    Used by tests 1-9 below. All synthetic; no live trading.
    """
    cfg = BacktestConfig(
        candidate_id="cand_test_v2",
        symbol="BTCUSDT",
        timeframe="1D",
        start_date="2024-01-01",
        end_date="2024-12-31",
        fee_bps=8.0,
        slippage_bps=5.0,
        initial_capital=10000.0,
    )
    bar_returns = _synthetic_bar_returns(30)
    test_slice_returns = [r for _, r in bar_returns[20:]]
    cumulative_test_return = prod(1.0 + r for r in test_slice_returns) - 1.0
    train_slice_returns = [r for _, r in bar_returns[:20]]
    cumulative_train_return = prod(1.0 + r for r in train_slice_returns) - 1.0
    window = WindowMetric(
        train_start_utc="2024-07-01T00:00:00Z",
        train_end_utc="2024-07-20T23:59:59Z",
        test_start_utc="2024-07-21T00:00:00Z",
        test_end_utc="2024-07-30T23:59:59Z",
        train_bar_count=20,
        test_bar_count=10,
        train_sharpe=1.10,
        test_sharpe=0.50,
        train_return=cumulative_train_return,
        test_return=cumulative_test_return,
        train_maxdd=0.04,
        test_maxdd=0.02,
        trades_count_in_test=3,
    )
    bar_returns_dir = tmp_path / "backtests"
    bar_returns_dir.mkdir(parents=True, exist_ok=True)
    result = make_v2_result(
        cfg,
        run_id="run_20260514T150000Z",
        strategy_code_sha256="a" * 64,
        random_seed=42,
        exchange="binance",
        is_sample_start_utc="2024-01-01T00:00:00Z",
        is_sample_end_utc="2024-06-30T23:59:59Z",
        oos_start_utc="2024-07-01T00:00:00Z",
        oos_end_utc="2024-07-30T23:59:59Z",
        bar_returns=bar_returns,
        window_metrics=[window],
        bar_returns_dir=bar_returns_dir,
        trades_count=3,
        fees_paid=0.5,
        slippage_cost=0.3,
    )
    return result


# ---------------------------------------------------------------------------
# Tests 1-9: v2 shape verification
# ---------------------------------------------------------------------------


def test_v2_schema_version_present(tmp_path):
    result = _build_v2_result(tmp_path)
    assert result.schema_version == SCHEMA_BACKTEST_V2
    assert result.is_v2() is True


def test_required_identity_fields_present(tmp_path):
    result = _build_v2_result(tmp_path)
    assert result.run_id == "run_20260514T150000Z"
    assert len(result.strategy_code_sha256) == 64
    assert result.random_seed == 42
    assert result.generated_at  # auto-populated


def test_required_symbol_timeframe_window_fields_present(tmp_path):
    result = _build_v2_result(tmp_path)
    assert result.symbol == "BTCUSDT"
    assert result.exchange == "binance"
    assert result.bar_timeframe == "1D"
    assert result.timezone == "UTC"
    assert result.session == "24x7"
    assert result.is_sample_start_utc == "2024-01-01T00:00:00Z"
    assert result.is_sample_end_utc == "2024-06-30T23:59:59Z"
    assert result.oos_start_utc == "2024-07-01T00:00:00Z"
    assert result.oos_end_utc == "2024-07-30T23:59:59Z"
    assert result.oos_bar_count == 30


def test_oos_bar_returns_csv_written(tmp_path):
    result = _build_v2_result(tmp_path)
    csv_path = tmp_path / "backtests" / result.oos_bar_returns_path
    assert csv_path.exists()
    assert csv_path.stat().st_size > 0
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header == "timestamp_utc,bar_return"


def test_oos_bar_returns_sha256_matches(tmp_path):
    result = _build_v2_result(tmp_path)
    csv_path = tmp_path / "backtests" / result.oos_bar_returns_path
    on_disk_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert on_disk_sha == result.oos_bar_returns_sha256


def test_oos_bar_returns_csv_row_count_equals_oos_bar_count(tmp_path):
    result = _build_v2_result(tmp_path)
    csv_path = tmp_path / "backtests" / result.oos_bar_returns_path
    lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
    data_rows = lines[1:]  # skip header
    assert len(data_rows) == result.oos_bar_count


def test_window_metrics_test_return_matches_cumulative_bar_returns(tmp_path):
    """The audit's invariant: window.test_return ==
    prod(1 + bar_returns over test slice) - 1, within 1e-6 relative."""
    result = _build_v2_result(tmp_path)
    csv_path = tmp_path / "backtests" / result.oos_bar_returns_path
    lines = csv_path.read_text(encoding="utf-8").strip().splitlines()[1:]
    parsed = [(row.split(",")[0], float(row.split(",")[1])) for row in lines]
    window = result.window_metrics[0]
    test_start = window["test_start_utc"]
    test_end = window["test_end_utc"]
    test_slice = [r for ts, r in parsed if test_start <= ts <= test_end]
    computed = prod(1.0 + r for r in test_slice) - 1.0
    assert isclose(window["test_return"], computed, rel_tol=1e-6, abs_tol=1e-9)


def test_fee_rate_bps_propagated_from_config(tmp_path):
    result = _build_v2_result(tmp_path)
    assert result.fee_rate_bps == 8.0
    assert result.fee_model == "linear"


def test_slippage_rate_bps_propagated_from_config(tmp_path):
    result = _build_v2_result(tmp_path)
    assert result.slippage_rate_bps == 5.0
    assert result.slippage_model == "constant"


# ---------------------------------------------------------------------------
# Tests 10-12: evidence_pack flag + v1 immutability
# ---------------------------------------------------------------------------


def test_evidence_pack_wfe_audit_eligible_flag_set(tmp_path, monkeypatch):
    """When a v2 backtest record exists for a candidate, the
    _compute_wfe_audit_eligible read-side helper returns True."""
    backtests_root = tmp_path / "backtests"
    backtests_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(evidence_module, "BACKTESTS_ROOT", backtests_root)

    # Build a v2 result in a sibling tmp dir, then move its JSON envelope
    # into backtests_root so _latest_json can find it.
    result = _build_v2_result(tmp_path)
    envelope = {
        "schema_version": "strategy_lab.backtest_result.v1",
        "generated_at": "2026-05-14T15:00:00Z",
        "mode": "EXPERIMENTAL",
        "result": result.to_dict(),
    }
    json_path = (
        backtests_root / f"{result.candidate_id}__btc__1D__2024-07-01_to_2024-07-30__20260514T150000Z.json"
    )
    json_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")
    assert _compute_wfe_audit_eligible(result.candidate_id) is True


def test_v1_records_remain_unchanged_after_v2_upgrade():
    """The 'no backfill of v1 records' rule applies to the v1
    *backtest record files* (which hold the historical strategy
    evaluation data). It does NOT forbid the evidence-pack INDEX
    from being upserted with a newly-computed wfe_audit_eligible
    flag — that flag is a derived read-side capability the indexer
    re-evaluates on every pack write per the design proposal.

    What we lock down here: no existing v1 backtest record file
    under strategy_lab/data/**/backtests/ has been retroactively
    given any v2 schema field (which would be a true data backfill).
    The pack-index store at strategy_lab/data/**/evidence_packs/
    is allowed to be re-emitted (with or without wfe_audit_eligible)
    by the existing test suite's natural upsert flow.
    """
    pack_files = sorted(LAB_DATA_ROOT.rglob("evidence_packs/packs.json"))
    assert pack_files, "preconditions failed: no packs.json files on disk"
    for pf in pack_files:
        store = json.loads(pf.read_text(encoding="utf-8"))
        assert store.get("schema_version") == "strategy_lab.evidence_pack.v1", (
            f"{pf} schema_version drifted from v1"
        )

    # Scope to lifecycle-bucket backtests (e.g. data/complete/backtests/,
    # data/approve_robust/backtests/). The flat data/backtests/ folder is a
    # transient test-fixture stash that pytest run_backtest_stub writes into
    # on every run; it does not hold historical strategy evaluations and is
    # therefore out of scope for the no-backfill guarantee.
    bt_files = [
        bf for bf in sorted(LAB_DATA_ROOT.rglob("backtests/*.json"))
        if bf.parent.parent.name != "data"
    ]
    assert bt_files, "preconditions failed: no lifecycle-scoped backtest files on disk"
    v2_only_fields = (
        # If any of these appear in an existing v1 backtest record,
        # a wild backfill happened. None should be present.
        "oos_bar_returns_path",
        "oos_bar_returns_sha256",
        "window_metrics",
        "oos_bar_count",
        "is_sample_start_utc",
        "oos_start_utc",
        "fee_rate_bps",
        "slippage_rate_bps",
        "fee_model",
        "slippage_model",
        "run_id",
        "strategy_code_sha256",
        "starting_equity",
        "compounding_mode",
    )
    for bf in bt_files:
        try:
            payload = json.loads(bf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        result = payload.get("result") if isinstance(payload, dict) else None
        if not isinstance(result, dict):
            continue
        if str(result.get("schema_version") or "") == SCHEMA_BACKTEST_V2:
            # Genuine v2 record (written by a v2-aware producer). Not a backfill.
            continue
        for f in v2_only_fields:
            assert f not in result, (
                f"{bf}: v1 backtest record was backfilled with v2 field "
                f"{f!r} — this violates the no-backfill rule"
            )


def _candidate_latest_backtest_is_v2(backtests_root: Path, candidate_id: str) -> bool:
    """Return True iff the latest backtest record for ``candidate_id``
    in ``backtests_root`` carries ``schema_version == strategy_lab.backtest.v2``.

    Used by tests that need to classify existing records into v1 vs v2
    populations without depending on the pack index alone.
    """
    matches = sorted(
        backtests_root.glob(f"{candidate_id}__*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        return False
    try:
        payload = json.loads(matches[0].read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    result = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(result, dict):
        return False
    return str(result.get("schema_version") or "") == SCHEMA_BACKTEST_V2


def test_existing_v1_only_records_evaluate_as_not_eligible(monkeypatch, tmp_path):
    """Refined classifier-correctness test.

    For every candidate in every existing ``packs.json`` whose latest
    backtest is NOT v2-shape, ``_compute_wfe_audit_eligible`` must
    return ``False``. Candidates whose latest backtest IS v2-shape are
    excluded from this scan: their eligibility is True by design (the
    v2 contract is met) and is validated by the dedicated v2 contract
    tests above (``test_evidence_pack_wfe_audit_eligible_flag_set``,
    plus the round-trip integration test below).

    This preserves the original "no false-positive eligibility for v1"
    guarantee while allowing legitimate v2 candidates to coexist in
    the same pack store after pilot or bulk migration runs.
    """
    pack_files = sorted(LAB_DATA_ROOT.rglob("evidence_packs/packs.json"))
    assert pack_files, "preconditions failed: no packs.json files on disk"
    seen_any_v1 = False
    skipped_v2_count = 0
    for pf in pack_files:
        store = json.loads(pf.read_text(encoding="utf-8"))
        backtests_root = pf.parent.parent / "backtests"
        monkeypatch.setattr(evidence_module, "BACKTESTS_ROOT", backtests_root)
        for entry in store.get("packs", []):
            cid = str(entry.get("candidate_id") or "")
            if not cid:
                continue
            if _candidate_latest_backtest_is_v2(backtests_root, cid):
                skipped_v2_count += 1
                continue
            seen_any_v1 = True
            eligible = _compute_wfe_audit_eligible(cid)
            assert eligible is False, (
                f"v1 candidate {cid!r} in {pf} unexpectedly evaluates as "
                f"WFE-audit-eligible — the classifier may be over-permissive"
            )
    assert seen_any_v1, (
        "preconditions failed: no v1-only candidates found in any "
        "existing packs.json. If every candidate is now v2-eligible, "
        "this test no longer protects v1; investigate before continuing."
    )


def test_v2_pipeline_round_trip_via_legitimate_apis(tmp_path, monkeypatch):
    """End-to-end integration: create_candidate -> make_v2_result ->
    build_evidence_pack (eligibility True) -> delete_candidate ->
    registry empty.

    Uses fully isolated tmp_path with monkeypatched module globals so
    no production file is touched. Validates that the full v2 pipeline
    plus the new ``registry.delete_candidate`` API works as a single
    coherent contract.

    This is the integration test the α-3 pilot lessons identified as
    missing: previously the acceptance suite only exercised
    ``_compute_wfe_audit_eligible`` in isolation (test 10), never the
    full ``build_evidence_pack`` chain on a registry-backed candidate.
    """
    import strategy_lab.registry as reg_module
    import strategy_lab.evidence_pack as ep_module
    import strategy_lab.backtest_wrapper as bt_module

    cand_file = tmp_path / "candidates.json"
    bt_root = tmp_path / "backtests"
    bt_root.mkdir(parents=True, exist_ok=True)
    packs_root = tmp_path / "evidence_packs"
    packs_root.mkdir(parents=True, exist_ok=True)
    reports_root = tmp_path / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(reg_module, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(reg_module, "CANDIDATES_FILE", cand_file)
    monkeypatch.setattr(bt_module, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(bt_module, "BACKTESTS_ROOT", bt_root)
    monkeypatch.setattr(ep_module, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(ep_module, "BACKTESTS_ROOT", bt_root)
    monkeypatch.setattr(ep_module, "EVIDENCE_PACKS_ROOT", packs_root)
    monkeypatch.setattr(ep_module, "PACKS_FILE", packs_root / "packs.json")
    monkeypatch.setattr(ep_module, "REPORT_ROOT", reports_root)
    monkeypatch.setattr(ep_module, "REPORT_FILE", reports_root / "strategy_lab_phase_12_evidence_pack.md")
    # safety.APPROVED_OUTPUT_ROOTS includes data and reports under LAB_ROOT;
    # under monkeypatch we widen by patching is_approved_path to be permissive.
    import strategy_lab.safety as safety_module
    monkeypatch.setattr(safety_module, "is_approved_path", lambda p: True)

    CID = "v2_roundtrip_test_001"

    # Step 1 — register candidate via the legitimate API
    created = reg_module.create_candidate({
        "candidate_id": CID,
        "status": "IN_RESEARCH",
        "lifecycle_state": "IN_RESEARCH",
        "name": "round-trip integration test candidate",
    })
    assert created["candidate_id"] == CID
    assert reg_module.get_candidate(CID) is not None
    assert cand_file.exists()

    # Step 2 — build v2 evidence
    bar_returns = _synthetic_bar_returns(30)
    cfg = bt_module.BacktestConfig(
        candidate_id=CID,
        symbol="BTCUSDT",
        timeframe="1D",
        start_date="2024-01-01",
        end_date="2024-12-31",
        fee_bps=8.0,
        slippage_bps=5.0,
        initial_capital=10000.0,
    )
    train = bar_returns[:20]
    test = bar_returns[20:]
    train_return = 1.0
    for _, r in train:
        train_return *= 1.0 + r
    train_return -= 1.0
    test_return = 1.0
    for _, r in test:
        test_return *= 1.0 + r
    test_return -= 1.0
    window = bt_module.WindowMetric(
        train_start_utc="2024-07-01T00:00:00Z",
        train_end_utc="2024-07-20T23:59:59Z",
        test_start_utc="2024-07-21T00:00:00Z",
        test_end_utc="2024-07-30T23:59:59Z",
        train_bar_count=20,
        test_bar_count=10,
        train_sharpe=1.0,
        test_sharpe=0.5,
        train_return=train_return,
        test_return=test_return,
        train_maxdd=0.04,
        test_maxdd=0.02,
        trades_count_in_test=3,
    )
    result = bt_module.make_v2_result(
        cfg,
        run_id="rt_test_001",
        strategy_code_sha256="a" * 64,
        random_seed=42,
        exchange="binance",
        is_sample_start_utc="2024-01-01T00:00:00Z",
        is_sample_end_utc="2024-06-30T23:59:59Z",
        oos_start_utc="2024-07-01T00:00:00Z",
        oos_end_utc="2024-07-30T23:59:59Z",
        bar_returns=bar_returns,
        window_metrics=[window],
        bar_returns_dir=bt_root,
    )
    envelope = {
        "schema_version": "strategy_lab.backtest_result.v1",
        "generated_at": "2026-05-14T00:00:00+00:00",
        "mode": "EXPERIMENTAL",
        "config": cfg.to_dict(),
        "result": result.to_dict(),
    }
    json_path = bt_root / f"{CID}__btcusdt__1D__2024-01-01_to_2024-12-31__rt_test_001.json"
    json_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

    # Step 3 — indexer call sets the flag end-to-end
    pack = ep_module.build_evidence_pack(CID)
    assert pack["wfe_audit_eligible"] is True
    assert pack["candidate_id"] == CID
    assert ep_module._compute_wfe_audit_eligible(CID) is True

    # Step 4 — delete via the new API
    deleted = reg_module.delete_candidate(CID)
    assert deleted is not None
    assert deleted["candidate_id"] == CID
    assert reg_module.get_candidate(CID) is None
    assert len(reg_module.load_candidates()) == 0

    # Step 5 — after delete, the indexer's pre-condition fails as expected
    import pytest as _pytest
    with _pytest.raises(KeyError):
        ep_module.build_evidence_pack(CID)


# ---------------------------------------------------------------------------
# Bonus: v1 BacktestResult round-trip preserved (additive defaults)
# ---------------------------------------------------------------------------


def test_v1_backtest_result_default_construction_is_not_v2():
    """Constructing a BacktestResult with v1-only kwargs yields a
    record whose is_v2() == False and schema_version == v1."""
    r = BacktestResult(
        candidate_id="cand_x",
        symbol="BTCUSDT",
        total_return=1.0,
        sharpe=1.0,
        trades_count=10,
    )
    assert r.schema_version == SCHEMA_BACKTEST_V1
    assert r.is_v2() is False
    # Round-trip preserves both v1 fields and the v2 defaults.
    clone = BacktestResult.from_dict(r.to_dict())
    assert clone.schema_version == SCHEMA_BACKTEST_V1
    assert clone.is_v2() is False
    assert clone.candidate_id == "cand_x"


# ---------------------------------------------------------------------------
# Bonus: write_bar_returns_csv determinism
# ---------------------------------------------------------------------------


def test_write_bar_returns_csv_is_deterministic(tmp_path):
    rows = _synthetic_bar_returns(10)
    a = write_bar_returns_csv(tmp_path / "a.csv", rows)
    b = write_bar_returns_csv(tmp_path / "b.csv", rows)
    assert a == b
    assert (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()


# ---------------------------------------------------------------------------
# Bonus: required v2 string-field constant is well-formed
# ---------------------------------------------------------------------------


def test_required_v2_string_fields_constant_is_complete():
    """The REQUIRED_V2_STR_FIELDS constant must list every required
    string field the contract demands. Catches drift if a field is
    added to the dataclass without updating the eligibility check."""
    expected = {
        "run_id", "strategy_code_sha256", "exchange", "bar_timeframe",
        "is_sample_start_utc", "is_sample_end_utc",
        "oos_start_utc", "oos_end_utc",
        "oos_bar_returns_path", "oos_bar_returns_sha256",
        "compounding_mode", "fee_model", "slippage_model",
    }
    assert set(REQUIRED_V2_STR_FIELDS) == expected
