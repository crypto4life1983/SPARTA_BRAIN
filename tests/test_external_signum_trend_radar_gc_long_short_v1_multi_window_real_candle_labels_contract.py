"""Tests for the C22 MULTI-WINDOW real-candle labels contract (spec + impl only).

All fixtures are in-memory synthetic windows -- no real frozen dataset is read, no artifact is
written, no build is executed. Proves: 20 contiguous windows / 50 per window / 1000 aggregate,
per-window SHA + date binding, manifest + rebuild determinism, source-SHA sensitivity,
missing/duplicate/schema-invalid failures, no cross-window state leakage, NO semantic drift
from the single-window frozen core, canonical date-range artifact naming, and that every
authorization/capability/lifecycle lock stays closed.
"""
import hashlib
import json

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract as mw
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as lb
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as dv
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as dr


def _cndl(c, upper, filt, trend="Green", h=None, date="2026-06-20"):
    h = c + 1 if h is None else h
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"trend": trend, "upper": upper, "filter": filt}, "date": date}


def _row(symbol, rank, run_date, latest, prev, cap=1_000_000_000.0):
    return {"detector": "gc", "assetClass": "crypto", "runDate": run_date,
            "symbol": symbol, "marketRank": rank, "marketCap": cap,
            "currentStatus": "CLOSED", "trendTo": latest["gc"]["trend"],
            "indicators": {"cmcRefPriceUsd": 100.0, "data": [prev, latest]}}


def _syn_window(run_date, n=50):
    """A structurally-valid 50-row GC window: unique ranks/symbols, BTC in downtrend, all
    NONE signals by default."""
    rows = []
    # BTC row: latest close below filter -> btc_downtrend True (context), NONE itself.
    rows.append(_row("BINANCE:BTCUSDT", 1, run_date,
                     _cndl(80, 110, 90, "Green", date=run_date),
                     _cndl(80, 110, 90, "Green", date=run_date)))
    for i in range(2, n + 1):
        rows.append(_row("SYM%02d" % i, i, run_date,
                         _cndl(100, 110, 90, "Green", date=run_date),
                         _cndl(100, 110, 90, "Green", date=run_date)))
    return {"limited": False, "total": n, "results": rows}


def _syn_inputs(dates):
    inputs = []
    for d in dates:
        parsed = _syn_window(d)
        sha = hashlib.sha256(json.dumps(parsed, sort_keys=True).encode()).hexdigest()
        inputs.append({"source_path": "syn/%s.json" % d, "run_date": d,
                       "row_count": len(parsed["results"]), "sha256": sha, "parsed": parsed})
    return inputs


# ---- happy path -------------------------------------------------------------

def test_manifest_ready_20_windows_1000_labels():
    rec, agg = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))
    assert rec["verdict"] == mw.VERDICT_MANIFEST_READY
    assert not rec["blockers"]
    assert mw.validate_multi_window(rec)["valid"] is True
    assert len(rec["per_window"]) == 20
    assert all(p["row_count"] == 50 and p["structurally_valid"] for p in rec["per_window"])
    assert rec["aggregate_labels_built"] == 1000
    assert len(agg) == 1000
    assert [p["run_date"] for p in rec["per_window"]] == list(mw.EXPECTED_DATES)


def test_source_sha_and_date_binding():
    inputs = _syn_inputs(mw.EXPECTED_DATES)
    rec, agg = mw.build_multi_window_manifest(inputs)
    by_date = {i["run_date"]: i["sha256"] for i in inputs}
    for lab in agg:
        assert lab["source_sha256"] == by_date[lab["source_date"]]
    # every window contributes exactly 50 labels
    from collections import Counter
    c = Counter(lab["source_date"] for lab in agg)
    assert set(c) == set(mw.EXPECTED_DATES) and all(v == 50 for v in c.values())


def test_manifest_and_rebuild_determinism():
    inputs = _syn_inputs(mw.EXPECTED_DATES)
    r1, a1 = mw.build_multi_window_manifest(inputs)
    r2, a2 = mw.build_multi_window_manifest(inputs)
    assert r1["aggregate_manifest_sha256"] == r2["aggregate_manifest_sha256"]
    b1 = mw.canonical_payload_bytes(mw.build_aggregate_payload(r1, a1))
    b2 = mw.canonical_payload_bytes(mw.build_aggregate_payload(r2, a2))
    assert b1 == b2   # byte-identical rebuild


def test_modified_source_sha_changes_manifest():
    inputs = _syn_inputs(mw.EXPECTED_DATES)
    base = mw.build_multi_window_manifest(inputs)[0]["aggregate_manifest_sha256"]
    inputs[5]["sha256"] = "deadbeef" * 8   # a modified source SHA
    changed = mw.build_multi_window_manifest(inputs)[0]["aggregate_manifest_sha256"]
    assert base != changed


# ---- fail-closed cases ------------------------------------------------------

def test_missing_window_fails_closed():
    rec, _ = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES[:-1]))  # 19
    assert rec["verdict"] == mw.VERDICT_MANIFEST_BLOCKED
    assert any("20_windows" in b or "not_exactly_expected" in b for b in rec["blockers"])
    # anti-tamper: a BLOCKED record may not be forged into a READY verdict
    forged = dict(rec)
    forged["verdict"] = mw.VERDICT_MANIFEST_READY
    assert mw.validate_multi_window(forged)["valid"] is False


def test_duplicate_date_fails_closed():
    inputs = _syn_inputs(mw.EXPECTED_DATES[:-1])
    dup = dict(inputs[0])
    inputs.append(dup)   # 20 entries but a duplicate date + a missing date
    rec, _ = mw.build_multi_window_manifest(inputs)
    assert rec["verdict"] == mw.VERDICT_MANIFEST_BLOCKED
    assert any("duplicate" in b or "not_exactly_expected" in b for b in rec["blockers"])


def test_schema_invalid_window_fails_closed():
    inputs = _syn_inputs(mw.EXPECTED_DATES)
    inputs[3]["parsed"]["results"] = inputs[3]["parsed"]["results"][:49]  # 49 rows
    inputs[3]["row_count"] = 49
    rec, _ = mw.build_multi_window_manifest(inputs)
    assert rec["verdict"] == mw.VERDICT_MANIFEST_BLOCKED
    assert any("invalid_window" in b for b in rec["blockers"])


def test_mixed_date_window_fails_closed():
    inputs = _syn_inputs(mw.EXPECTED_DATES)
    inputs[7]["parsed"]["results"][0]["runDate"] = "2099-01-01"  # content date != window date
    rec, _ = mw.build_multi_window_manifest(inputs)
    assert rec["verdict"] == mw.VERDICT_MANIFEST_BLOCKED


# ---- no cross-window state leakage -----------------------------------------

def test_no_cross_window_state_leakage():
    wA = _syn_window("2026-06-20")
    wB = _syn_window("2026-06-21")
    a1 = mw.label_window(wA, "shaA", "2026-06-20")
    b1 = mw.label_window(wB, "shaB", "2026-06-21")
    # reverse order of calls -> identical per-window output (no shared state)
    b2 = mw.label_window(wB, "shaB", "2026-06-21")
    a2 = mw.label_window(wA, "shaA", "2026-06-20")
    assert a1 == a2 and b1 == b2
    assert all(l["source_date"] == "2026-06-20" for l in a1["labels"])
    assert all(l["source_date"] == "2026-06-21" for l in b1["labels"])


# ---- NO semantic drift: identity-reuse of the frozen core -------------------

def test_no_semantic_drift_identity():
    assert mw.classify_signal is lb._classify_signal
    assert mw.extract_label_rows is lb.extract_label_rows
    assert mw.apply_market_rank_tiebreaker is dv.apply_market_rank_tiebreaker
    assert mw.extract_dataset_facts is dv.extract_dataset_facts
    assert mw.BEAR_HIGH_MULT == lb.BEAR_HIGH_MULT == dr.BEAR_HIGH_MULT
    assert (mw.SIGNAL_LONG, mw.SIGNAL_HEDGE, mw.SIGNAL_BEAR, mw.SIGNAL_NONE, mw.SIGNAL_SKIP) \
        == (lb.SIGNAL_LONG, lb.SIGNAL_HEDGE, lb.SIGNAL_BEAR, lb.SIGNAL_NONE, lb.SIGNAL_SKIP)
    assert mw.MARKET_RANK_TIEBREAKER == tuple(dv.MARKET_RANK_TIEBREAKER)


def test_frozen_predicates_trigger_each_signal():
    rd = "2026-06-20"
    # BTC downtrend context row + one row per target signal
    rows = [
        _row("BINANCE:BTCUSDT", 1, rd, _cndl(80, 110, 90, "Green", date=rd),
             _cndl(80, 110, 90, "Green", date=rd)),
        # LONG: c>upper and prev c<=prev upper
        _row("LONGSYM", 2, rd, _cndl(115, 110, 90, "Green", date=rd),
             _cndl(108, 110, 90, "Green", date=rd)),
        # HEDGE: Red, c<filter, prev c>=prev filter
        _row("HEDGESYM", 3, rd, _cndl(85, 110, 90, "Red", h=86, date=rd),
             _cndl(95, 110, 90, "Red", date=rd)),
        # BEAR: btc downtrend, Red, high>=0.98*filter, c<filter, prev c<prev filter (not hedge)
        _row("BEARSYM", 4, rd, _cndl(89, 110, 100, "Red", h=99, date=rd),
             _cndl(90, 110, 100, "Red", date=rd)),
        # NONE
        _row("NONESYM", 5, rd, _cndl(100, 110, 90, "Green", date=rd),
             _cndl(100, 110, 90, "Green", date=rd)),
    ]
    parsed = {"limited": False, "total": 5, "results": rows}
    out = mw.label_window(parsed, "sha", rd)
    sig = {l["symbol"]: l["signal"] for l in out["labels"]}
    assert out["btc_downtrend"] is True
    assert sig["LONGSYM"] == lb.SIGNAL_LONG
    assert sig["HEDGESYM"] == lb.SIGNAL_HEDGE
    assert sig["BEARSYM"] == lb.SIGNAL_BEAR
    assert sig["NONESYM"] == lb.SIGNAL_NONE


# ---- canonical naming + collision prevention --------------------------------

def test_artifact_naming_date_range_no_today_no_collision():
    assert mw.WINDOW_START in mw.MW_ARTIFACT_FILENAME
    assert mw.WINDOW_END in mw.MW_ARTIFACT_FILENAME
    assert mw.MW_ARTIFACT_FILENAME != mw.SINGLE_WINDOW_ARTIFACT_FILENAME
    assert "multiwindow" in mw.MW_ARTIFACT_FILENAME


# ---- authorization / capability / lifecycle locks ---------------------------

def test_authorization_and_capability_locks_closed():
    rec = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))[0]
    for k in ("build_authorized", "replay_authorized", "optimization_authorized",
              "activation_authorized", "paper_live_authorized", "execution_authorized"):
        assert rec[k] is False
        assert getattr(mw, k.upper()) is False
    for flag in mw._CAPABILITY_FLAGS_FALSE:
        assert rec[flag] is False, flag
    assert rec["replay_gate_locked"] and rec["live_gate_locked"]
    assert rec["advances_nothing"] is True


def test_reuses_canonical_lifecycle_token_not_a_new_one():
    # governs execution via the EXISTING canonical C22 label-build token; no parallel token
    assert mw.NEXT_GATE_TOKEN == dv.NEXT_ACTION_VALID
    assert mw.NEXT_GATE_TOKEN == "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    assert mw.NEXT_ACTION_AFTER_LABELS == lb.NEXT_ACTION_AFTER_LABELS


def test_single_window_contract_pins_unchanged():
    # remediation must not have touched the single-window source-of-truth pins
    assert lb.DATASET_SHA256 == "cc37dee4f6bb65ac9ae219bfa8e4ececa83fb06952d8ecac3250419367470f21"
    assert lb.LABELS_ARTIFACT_SHA256 == "bc434aebe056fd72670735442e58926f9df483cbbbf820308b153c36d12a8947"
    assert lb.ARTIFACT_BASENAME == "c22_gc_real_candle_entry_labels"
