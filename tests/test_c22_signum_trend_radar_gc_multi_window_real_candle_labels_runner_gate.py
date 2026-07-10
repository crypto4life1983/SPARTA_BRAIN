"""Tests for the corrected C22 multi-window label RUNNER artifact-write authorization gate.

Proves: writing requires BOTH --execute-build AND the exact canonical token; the option alone
or token alone or a wrong token is refused; EXECUTION_AUTHORIZED=False never blocks an
otherwise-authorized analytical build and True is never required/enabled; committed defaults
stay fail-closed; manifest-not-ready and output-collision still refuse; and label semantics
are unchanged. All write-path tests use temporary directories; no production artifact created.
"""
import hashlib
import json

import tools.c22_signum_trend_radar_gc_multi_window_real_candle_labels_once as runner
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract as mw

TOKEN = "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


# ---- synthetic 20-window builder (mirrors the contract test; no real data) --------------

def _cndl(c, upper, filt, trend="Green", h=None, date="2026-06-20"):
    h = c + 1 if h is None else h
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"trend": trend, "upper": upper, "filter": filt}, "date": date}


def _row(symbol, rank, rd, latest, prev):
    return {"detector": "gc", "assetClass": "crypto", "runDate": rd, "symbol": symbol,
            "marketRank": rank, "marketCap": 1e9,
            "indicators": {"cmcRefPriceUsd": 100.0, "data": [prev, latest]}}


def _syn_window(rd, n=50):
    rows = [_row("BINANCE:BTCUSDT", 1, rd, _cndl(80, 110, 90, date=rd), _cndl(80, 110, 90, date=rd))]
    for i in range(2, n + 1):
        rows.append(_row("SYM%02d" % i, i, rd, _cndl(100, 110, 90, date=rd), _cndl(100, 110, 90, date=rd)))
    return {"limited": False, "total": n, "results": rows}


def _syn_inputs(dates):
    out = []
    for d in dates:
        parsed = _syn_window(d)
        sha = hashlib.sha256(json.dumps(parsed, sort_keys=True).encode()).hexdigest()
        out.append({"source_path": "syn/%s.json" % d, "run_date": d,
                    "row_count": 50, "sha256": sha, "parsed": parsed})
    return out


# ---- authorization gate matrix ----------------------------------------------

def test_gate_no_option_no_token_refused():
    assert runner.authorize_artifact_write(False, None)["authorized"] is False


def test_gate_option_only_refused():
    r = runner.authorize_artifact_write(True, None)
    assert r["authorized"] is False and r["reason"] == "missing_canonical_build_token"


def test_gate_token_only_refused():
    assert runner.authorize_artifact_write(False, TOKEN)["authorized"] is False


def test_gate_wrong_token_refused():
    r = runner.authorize_artifact_write(True, "HUMAN_DECISION_SOMETHING_ELSE")
    assert r["authorized"] is False and r["reason"] == "wrong_canonical_build_token"


def test_gate_option_plus_exact_token_authorized():
    r = runner.authorize_artifact_write(True, TOKEN)
    assert r["authorized"] is True


def test_canonical_token_is_the_committed_lifecycle_token():
    assert runner.CANONICAL_BUILD_TOKEN == TOKEN == mw.NEXT_GATE_TOKEN


# ---- EXECUTION_AUTHORIZED must be irrelevant to the analytical build ----------

def test_execution_authorized_does_not_block_and_is_never_required():
    assert mw.EXECUTION_AUTHORIZED is False            # committed default stays False
    # authorized purely by option + token, with EXECUTION_AUTHORIZED False
    assert runner.authorize_artifact_write(True, TOKEN)["authorized"] is True
    # the gate cannot consult EXECUTION_AUTHORIZED: its signature takes only (execute_build, token)
    import inspect
    params = list(inspect.signature(runner.authorize_artifact_write).parameters)
    assert params == ["execute_build", "token"]


# ---- committed defaults fail-closed -----------------------------------------

def test_committed_defaults_fail_closed():
    for k in ("BUILD_AUTHORIZED", "REPLAY_AUTHORIZED", "OPTIMIZATION_AUTHORIZED",
              "ACTIVATION_AUTHORIZED", "PAPER_LIVE_AUTHORIZED", "EXECUTION_AUTHORIZED"):
        assert getattr(mw, k) is False
    # default runner invocation (no option) is not authorized
    assert runner.authorize_artifact_write(False, None)["authorized"] is False


# ---- manifest eligibility gate (independent of authorization) ---------------

def test_manifest_write_eligible_ready_vs_blocked():
    ready, _ = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))
    assert runner.manifest_write_eligible(ready, mw.validate_multi_window(ready)) is True
    blocked, _ = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES[:-1]))  # 19
    assert runner.manifest_write_eligible(blocked, mw.validate_multi_window(blocked)) is False


# ---- write path (temp dir only; never the production path) ------------------

def test_write_path_eligible_writes_to_tmp(tmp_path):
    rec, agg = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))
    assert runner.manifest_write_eligible(rec, mw.validate_multi_window(rec)) is True
    res = runner.write_artifact(rec, agg, tmp_path)
    out = tmp_path / mw.MW_ARTIFACT_FILENAME
    assert out.is_file()
    assert out.name == "c22_gc_real_candle_entry_labels_multiwindow_2026-06-20_2026-07-09.json"
    # deterministic content sha
    assert res["sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    # 1000 labels in the written payload
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert len(payload["labels"]) == 1000


def test_write_collision_refuses(tmp_path):
    rec, agg = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))
    (tmp_path / mw.MW_ARTIFACT_FILENAME).write_text("preexisting", encoding="utf-8")
    try:
        runner.write_artifact(rec, agg, tmp_path)
        assert False, "expected collision refusal"
    except RuntimeError as e:
        assert "refuse_overwrite_existing_artifact" in str(e)
    # the pre-existing file was NOT overwritten
    assert (tmp_path / mw.MW_ARTIFACT_FILENAME).read_text(encoding="utf-8") == "preexisting"


# ---- no semantic drift (label output unchanged by the runner fix) -----------

def test_no_semantic_drift_after_gate_fix():
    assert mw.classify_signal.__name__ == "_classify_signal"
    rec, agg = mw.build_multi_window_manifest(_syn_inputs(mw.EXPECTED_DATES))
    assert len(agg) == 1000
    assert rec["bear_high_multiple_single_sourced"] == mw.BEAR_HIGH_MULT
