"""Tests for the Candidate #18 data-readiness / fetch-approval contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, data-readiness-only, executes nothing; chain-gated on the
frozen C18 detector dry-run; HONESTLY records that NO frozen local H4 BTCUSD OHLC
exists (labels cannot proceed); acknowledges the existing safe daily fetch convention
but that it is interval-locked to 1d and NOT reusable for H4; declares the safety
requirements + human approval token a future public, no-credential, deterministic,
SHA-frozen H4 fetch must satisfy; performs NO fetch / NO network / NO credentials / NO
XAUUSD; stops before any network; keeps downstream gates locked; capability flags +
scope locks; validator anti-tamper; module purity (incl. no network imports)."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_data_readiness_contract as dr18  # noqa: E501


_R = dr18.build_c18_data_readiness(".", [])


def test_readiness_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_data_readiness_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_DATA_READINESS_FROZEN_FOR_HUMAN_REVIEW"
    assert dr18.validate_c18_data_readiness(_R)["valid"] is True


def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_verdict"] == (
        "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    assert _R["detector_dry_run_valid"] is True
    bad = {**_R, "detector_dry_run_verdict": "C18_DETECTOR_DRY_RUN_BLOCKED"}
    assert dr18.validate_c18_data_readiness(bad)["valid"] is False


# ---- HONEST discovery: no H4 data; labels cannot proceed -------------------

def test_no_h4_data_labels_cannot_proceed():
    assert _R["frozen_local_h4_btcusd_exists"] is False
    assert _R["labels_can_proceed_now"] is False
    md = _R["missing_data"]
    assert md["symbol"] == "BTCUSD"
    assert md["timeframe"] == "H4"
    assert "open" in md["columns"] and "close" in md["columns"]
    # the local crypto data that WAS found is daily (wrong timeframe)
    assert any("DAILY" in v for v in _R["local_crypto_data_found"].values())
    # tamper: cannot claim data exists / labels can proceed
    bad = {**_R, "frozen_local_h4_btcusd_exists": True}
    assert dr18.validate_c18_data_readiness(bad)["valid"] is False
    bad2 = {**_R, "labels_can_proceed_now": True}
    assert dr18.validate_c18_data_readiness(bad2)["valid"] is False


# ---- existing convention is daily-only, NOT reusable for H4 -----------------

def test_existing_convention_is_daily_only():
    conv = _R["existing_safe_fetch_convention"]
    assert conv["public_market_data_only"] is True
    assert conv["no_api_key"] is True
    assert conv["interval_locked_to"] == "1d"
    assert conv["covers_h4"] is False
    assert conv["reusable_for_h4_as_is"] is False
    assert _R["approved_h4_fetch_convention_exists"] is False
    assert _R["reuses_existing_convention_for_h4"] is False
    # tamper: cannot claim the daily convention covers H4
    bad = {**_R, "existing_safe_fetch_convention": {**conv, "covers_h4": True}}
    assert dr18.validate_c18_data_readiness(bad)["valid"] is False
    bad2 = {**_R, "reuses_existing_convention_for_h4": True}
    assert dr18.validate_c18_data_readiness(bad2)["valid"] is False


# ---- proposed safe fetch: declared, NOT executed ---------------------------

def test_proposed_fetch_safe_and_not_executed():
    reqs = " || ".join(_R["proposed_fetch_safety_requirements"]).lower()
    assert "public market data only" in reqs
    assert "no api key" in reqs and "no credentials" in reqs
    assert "no signed" in reqs
    assert "interval restricted to 4h" in reqs
    assert "sha-frozen" in reqs
    assert "no xauusd" in reqs
    assert _R["proposed_fetch_approval_token"] == (
        "APPROVE_C18_H4_BTCUSD_PUBLIC_READONLY_FETCH")
    assert _R["no_fetch_performed_here"] is True
    assert _R["no_network_call_here"] is True
    assert _R["no_credentials_used"] is True
    assert _R["stops_before_any_network_fetch"] is True
    assert _R["fetch_requires_explicit_human_approval"] is True
    assert _R["fetches_data"] is False
    assert _R["uses_network"] is False
    assert _R["approves_fetch_itself"] is False
    bad = {**_R, "no_fetch_performed_here": False}
    assert dr18.validate_c18_data_readiness(bad)["valid"] is False


def test_xauusd_out_of_scope():
    assert _R["xauusd_in_scope"] is False
    assert _R["uses_xauusd"] is False


def test_next_action_is_fetch_approval():
    nra = dr18.get_c18_data_readiness_next_action()
    assert nra == _R["next_required_action"]
    assert nra == (
        "HUMAN_DECISION_APPROVE_C18_H4_BTCUSD_PUBLIC_READONLY_FETCH_OR_REJECT")
    for banned in ("PAPER", "LIVE", "BROKER", "ORDER", "REPLAY", "PNL"):
        assert banned not in nra.upper(), banned


def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert dr18.validate_c18_data_readiness(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in dr18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert dr18.validate_c18_data_readiness(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_network", "no_fetch", "no_credentials",
                 "no_api_call", "no_broker", "no_xauusd", "no_labels", "no_replay",
                 "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                 "no_self_fetch_approval"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_claim():
    label = dr18.get_c18_data_readiness_label()
    assert "RESEARCH ONLY" in label
    assert "FETCHES NOTHING" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())


# ---- module purity (incl. NO network imports) ------------------------------

def test_module_purity_no_io_no_network_no_main():
    src = open(dr18.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "urlopen", "requests.get"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas",
              "binance"}
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
