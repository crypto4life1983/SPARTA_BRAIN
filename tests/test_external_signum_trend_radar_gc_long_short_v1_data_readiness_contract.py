"""Tests for the Candidate #22 real-candle DATA-READINESS review contract
(external_signum_trend_radar_gc_long_short_v1).

Verifies: research-only, readiness-review-only, executes nothing; chain-gated on the
frozen C22 detector dry-run (verdict + pinned commit cfad8ab7); HONESTLY concludes
DATA_NOT_READY (data_ready False, NO labels, NO artifacts, NOTHING SHA-pinned, NO
labels-review contract) because no surveyed frozen local dataset supplies the proprietary
Signum Trend-Radar gc-detector fields (gc.upper/gc.filter bands, breakoutDate, market_rank)
and they can be neither derived from OHLCV (would invent the indicator) nor fetched
(Signum/MCP/Hyperliquid hard-locked); preserves the frozen spec rules; declares the
required operator-staged dataset with provenance; advances nothing; downstream gates
locked; capability flags + scope locks; validator anti-tamper; module purity. The verdict
cannot be flipped to data-ready."""
from __future__ import annotations

import ast

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_data_readiness_contract as drd  # noqa: E501


_R = drd.build_c22_data_readiness()


# ---- core: research-only, readiness-only, validates ------------------------

def test_data_readiness_validates_and_not_ready():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_data_readiness_review_only"] is True
    assert _R["blockers"] == []
    assert _R["readiness_verdict"] == "DATA_NOT_READY"
    assert drd.validate_c22_data_readiness(_R)["valid"] is True


def test_identity():
    assert _R["candidate_id"] == "C22"
    assert _R["candidate_token"] == "C22_EXTERNAL_SIGNUM_TREND_RADAR_GC_LONG_SHORT_V1"


# ---- DATA_NOT_READY: no labels, no artifacts, nothing pinned ---------------

def test_no_labels_no_artifacts_no_pins():
    assert _R["data_ready"] is False
    assert _R["labels_produced"] is False
    assert _R["artifacts_produced"] == []
    assert _R["any_sha_pinned_artifacts"] is False
    assert _R["does_not_produce_labels_review_contract"] is True
    # the verdict cannot be flipped to ready
    for bad_kv in (("data_ready", True), ("labels_produced", True),
                   ("readiness_verdict", "FROZEN_AND_READY")):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert drd.validate_c22_data_readiness(bad)["valid"] is False, bad_kv[0]


# ---- chain-gated on the frozen detector dry-run ----------------------------

def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    assert _R["chain_gated_on_c22_detector_dry_run"] is True
    assert _R["detector_dry_run_commit"] == "cfad8ab7b4c5b9a2435658985950c6efc17497fe"
    bad = {**_R, "detector_dry_run_commit": "0" * 40}
    assert drd.validate_c22_data_readiness(bad)["valid"] is False
    bad2 = {**_R, "detector_dry_run_verdict": "X"}
    assert drd.validate_c22_data_readiness(bad2)["valid"] is False


# ---- survey honestly shows no suitable dataset -----------------------------

def test_survey_no_suitable_dataset():
    assert _R["any_local_dataset_supplies_trend_radar_gc_fields"] is False
    surveyed = _R["surveyed_local_datasets"]
    assert len(surveyed) >= 3
    for d in surveyed:
        assert d["supplies_trend_radar_gc_fields"] is False
        assert d["path"] and d["reason"]
    # tamper: claiming a surveyed dataset is suitable -> invalid
    bad_surv = [dict(d) for d in surveyed]
    bad_surv[0] = {**bad_surv[0], "supplies_trend_radar_gc_fields": True}
    bad = {**_R, "surveyed_local_datasets": bad_surv,
           "any_local_dataset_supplies_trend_radar_gc_fields": True}
    assert drd.validate_c22_data_readiness(bad)["valid"] is False


# ---- the not-ready reasons cover derive + fetch impossibility ---------------

def test_not_ready_reasons_and_no_invention():
    reasons = " || ".join(_R["data_not_ready_reasons"]).lower()
    assert "gc.trend" in reasons or "gc detector" in reasons or "gc' detector" in reasons
    assert "derive" in reasons          # cannot derive from OHLCV
    assert "invent" in reasons          # would invent rules
    assert "fetch" in reasons and ("signum" in reasons or "mcp" in reasons)
    assert _R["edits_no_rules"] is True
    assert _R["invents_no_indicator"] is True
    assert _R["preserves_frozen_c22_spec_rules"] is True
    assert _R["gc_bands_cannot_be_derived_from_ohlcv_without_inventing"] is True
    assert len(_R["data_not_ready_reasons"]) >= 4


# ---- required data fields + operator-staged dataset declared ---------------

def test_required_data_and_operator_dataset_declared():
    rdf = _R["required_data_fields"]
    pcd = " ".join(rdf["per_closed_daily_candle"])
    assert "gc.upper" in pcd and "gc.filter" in pcd and "gc.trend" in pcd
    assert rdf["minimum_line_items"] == 50
    req = _R["required_operator_staged_dataset"]
    assert req["sparta_fetches_nothing"] is True
    prov = " ".join(req["provenance_required"]).lower()
    assert "sha256" in prov and "retrieval_utc" in prov


# ---- no fetch / no connection posture --------------------------------------

def test_no_fetch_no_connection_posture():
    assert _R["uses_frozen_local_data_only"] is True
    assert _R["no_data_fetch"] is True
    assert _R["no_signum_connection"] is True
    assert _R["no_mcp"] is True
    assert _R["no_hyperliquid"] is True


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in drd._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert drd.validate_c22_data_readiness(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build_labels", "no_real_candle_detection", "no_replay",
                 "no_data_fetch", "no_edit_rules", "no_invent_indicator",
                 "no_signum_connection", "no_mcp", "no_hyperliquid", "no_send_trades",
                 "no_paper_trading", "no_live_trading", "no_commit", "no_push",
                 "no_claim_data_ready"):
        assert _R["scope_locks"][must] is True, must


# ---- advances nothing; downstream locked -----------------------------------

def test_advances_nothing_downstream_locked():
    nra = drd.get_c22_data_readiness_next_action()
    assert nra == _R["next_required_action"]
    assert "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in nra
    assert _R["advances_nothing"] is True
    for gate in ("labels_gate_locked_until_data_ready", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert drd.validate_c22_data_readiness(bad)["valid"] is False, gate


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(drd.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
