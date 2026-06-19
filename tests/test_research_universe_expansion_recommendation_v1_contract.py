"""Tests for the Research-Universe Expansion Recommendation v1 contract.

Verifies: research-only, recommendation-only, executes nothing; assigns NO C20, opens
no candidate, fetches no data, adds no XAUUSD/new instrument, creates no
detector/labels/replay, runs no optimization; carries the two failure roots; evaluates
all seven expansion options each with the full required field set (edge / structural
difference / data fields / public sources / safety risks / fetch / credentials /
research-only); recommends the perp-basis first target (public, no credentials);
records that any fetch needs a separate explicit human token (not taken here) and keeps
the C20 human gate; capability flags + scope locks; validator anti-tamper; module
purity."""
from __future__ import annotations

import ast

import sparta_commander.research_universe_expansion_recommendation_v1_contract as rue


_R = rue.build_universe_expansion_recommendation()


def test_recommendation_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_recommendation_only"] is True
    assert rue.validate_universe_expansion_recommendation(_R)["valid"] is True


def test_no_c20_no_fetch_no_new_instrument():
    assert _R["assigns_c20"] is False
    assert _R["c20_assigned"] is False
    assert _R["candidate_id"] is None
    assert _R["opens_candidate"] is False
    assert _R["fetches_data"] is False
    assert _R["any_fetch_taken_here"] is False
    assert _R["adds_xauusd_or_new_instrument"] is False
    assert _R["creates_detector_labels_or_replay"] is False
    assert _R["optimizes_or_tunes"] is False


def test_two_failure_roots_carried():
    fr = _R["failure_roots"]
    assert "risk-adjusted" in fr["root_a_lose_to_buy_and_hold_risk_adjusted"].lower()
    assert "beta" in fr["root_a_lose_to_buy_and_hold_risk_adjusted"].lower()
    assert "out of sample" in fr["root_b_oos_neutrality_fails"].lower()


def test_seven_options_each_fully_specified():
    opts = _R["expansion_options"]
    assert len(opts) == 7
    keys = {o["key"] for o in opts}
    for must in ("crypto_funding_rate_data", "perp_basis_spot_perp_spread",
                 "cross_exchange_spread_or_basis", "options_implied_volatility",
                 "broader_crypto_universe", "higher_frequency_ohlcv",
                 "non_crypto_instruments_separate_lane"):
        assert must in keys, must
    for o in opts:
        for f in ("edge_it_could_test", "structurally_different_from_c1_c19",
                  "required_data_fields", "likely_public_data_sources",
                  "safety_risks", "addresses_failure_root", "feasibility"):
            assert o.get(f), (o["key"], f)
        assert isinstance(o["network_fetch_needed"], bool)
        assert isinstance(o["credentials_needed"], bool)
        assert o["can_stay_research_only"] is True
        # every crypto option requires a network fetch (none use cached data alone)
        assert o["network_fetch_needed"] is True, o["key"]


def test_recommended_first_target_is_perp_basis_public_no_creds():
    assert _R["recommended_first_target"] == "perp_basis_spot_perp_spread"
    rec = _R["recommended_option"]
    assert rec["key"] == "perp_basis_spot_perp_spread"
    assert rec["credentials_needed"] is False
    assert rec["can_stay_research_only"] is True
    assert rec["addresses_failure_root"] == "root_b_oos_neutrality_fails"
    assert _R["recommended_target_uses_public_data_no_credentials"] is True
    assert _R["companion_signal"] == "crypto_funding_rate_data"
    assert _R["recommendation_is_advisory_human_decides"] is True
    assert "MECHANICALLY" in _R["why_recommended"]


def test_higher_frequency_and_non_crypto_flagged_honestly():
    opts = {o["key"]: o for o in _R["expansion_options"]}
    assert opts["higher_frequency_ohlcv"]["addresses_failure_root"] == "none_clearly"
    nc = opts["non_crypto_instruments_separate_lane"]
    assert nc["credentials_needed"] is True
    assert "separate" in nc["structurally_different_from_c1_c19"].lower()


def test_fetch_is_a_separate_human_gate_not_taken():
    assert _R["fetch_requires_separate_explicit_human_token"] is True
    assert _R["next_human_token_before_any_fetch"] == (
        "HUMAN_APPROVED_FETCH_PUBLIC_PERP_SPOT_BASIS_AND_FUNDING_DATA_RESEARCH_ONLY")
    nra = rue.get_universe_expansion_next_action()
    assert nra == _R["next_required_action"]
    assert "NO_FETCH_TAKEN" in nra
    assert "NO_C20_ASSIGNED" in nra


def test_c20_human_gate_preserved():
    assert _R["requires_human_approval_before_c20"] is True
    assert _R["opening_c20_requires_explicit_open_candidate_token"] is True


def test_recommended_target_tamper_rejected():
    bad = {**_R, "recommended_first_target": "broader_crypto_universe"}
    # mismatch with the pinned RECOMMENDED_FIRST_TARGET -> invalid
    assert rue.validate_universe_expansion_recommendation(bad)["valid"] is False


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rue._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rue.validate_universe_expansion_recommendation(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_assign_c20", "no_open_candidate", "no_data_fetch",
                 "no_funding_fetch", "no_basis_fetch", "no_xauusd",
                 "no_new_instrument_class", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_credentials", "no_commit", "no_push",
                 "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rue.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "requests",
                 "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
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
