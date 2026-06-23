"""Tests for the BTC-only Deribit per-strike forward-collector SPEC v1.

Verifies: BTC-only; no private/auth endpoints; no collector implementation/run authorized; no
replay/backtest/paper/live authorized; v2 requires bid/ask + greeks; v2 does not overwrite
duplicate snapshots; data paths stay under the gitignored local-only data root; all future
actions require explicit human gates; and v1 retirement is NOT authorized by this spec."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.btc_per_strike_collector_spec_v1_contract as spec

_S = spec.build_spec()


def test_builds_and_validates():
    assert _S["mode"] == "RESEARCH_ONLY"
    assert _S["is_spec_only"] is True
    assert _S["blockers"] == []
    assert _S["verdict"] == "BTC_PER_STRIKE_COLLECTOR_SPEC_FROZEN_DESIGN_ONLY"
    assert spec.validate_spec(_S)["valid"] is True


def test_btc_only():
    assert _S["currency"] == "BTC"
    assert spec.CURRENCY == "BTC"


def test_no_private_or_auth_endpoints():
    for e in _S["allowed_public_endpoints"]:
        assert e.startswith("https://www.deribit.com/api/v2/public/")
        assert "/private/" not in e
    assert _S["uses_only_public_endpoints"] is True
    for frag in ("/private/", "account", "order", "apikey", "signature"):
        assert frag in _S["forbidden_endpoint_fragments"]


def test_no_collector_implementation_or_run_authorized():
    for flag in ("implements_collector", "runs_collector", "schedules_collector",
                 "changes_scheduled_task", "makes_external_api_call", "fetches_data",
                 "writes_data"):
        assert _S[flag] is False
    assert _S["implements_no_collector"] is True and _S["runs_nothing"] is True


def test_no_replay_backtest_paper_live_authorized():
    for flag in ("runs_replay", "runs_backtest", "optimizes_parameters", "paper_trading",
                 "live_trading", "sells_options", "authorizes_naked_short_vol"):
        assert _S[flag] is False
    assert _S["naked_short_vol_forbidden"] is True


def test_v2_requires_bid_ask_and_greeks():
    assert _S["v2_requires_bid_ask"] is True
    assert _S["v2_requires_greeks"] is True
    for fld in ("bid", "ask", "delta", "gamma", "vega", "theta"):
        assert fld in _S["required_v2_fields"]
    rel = _S["v1_relationship"]
    assert rel["v1_lacks_bid_ask"] is True and rel["v1_lacks_greeks"] is True
    assert rel["v2_is_strict_superset"] is True


def test_v2_no_overwrite_duplicate_snapshot():
    st = _S["storage"]
    assert st["immutable_one_snapshot_per_utc_date"] is True
    assert st["duplicate_snapshot_behavior"] == "NO_OVERWRITE__REPORT_DUPLICATE_SNAPSHOT"


def test_data_paths_gitignored_local_only():
    st = _S["storage"]
    assert st["data_root"] == "data/deribit_options_chain_universe/"
    assert st["v2_snapshots_dir"].startswith("data/deribit_options_chain_universe/snapshots_v2")
    assert st["data_is_gitignored_local_only"] is True
    assert st["no_data_file_tracked_by_git"] is True
    assert st["manifest_required"] is True and st["quality_report_required"] is True


def test_all_future_actions_human_gated():
    steps = {g["step"]: g for g in _S["human_gates"]}
    for req in ("build_collector", "run_or_schedule_collector", "retire_v1_00_20_task",
                "paid_historical_data", "phase2_replay_backtest", "paper_trading",
                "live_trading"):
        assert req in steps, req
        assert steps[req]["authorized_now"] is False
    assert _S["all_future_actions_human_gated"] is True
    assert _S["next_required_action"].startswith(
        "HUMAN_APPROVED_BUILD_BTC_DERIBIT_PER_STRIKE_FORWARD_COLLECTOR")


def test_v1_retirement_not_authorized_by_this_spec():
    assert _S["v1_retirement_authorized_by_this_spec"] is False
    assert _S["retires_v1_task"] is False
    assert _S["changes_no_scheduled_task"] is True
    rel = _S["v1_relationship"]
    assert rel["v2_supersedes_v1_only_after_separate_human_approval"] is True


def test_phase1_grounding_pinned():
    g = _S["phase1_grounding"]
    assert _S["phase1_evidence_commit"] == "6daac546f95f7f78022823e7616b70febcaa1953"
    assert g["btc_avg_spread_30d"] == 8.8 and g["btc_hit_rate_30d"] == 0.727
    assert g["btc_ex_2021_avg"] == 7.2 and g["btc_2024_2026_avg"] == 5.4
    assert g["combined_avg_spread_30d"] == 6.8 and g["combined_hit_rate_30d"] == 0.688
    assert g["btc_worst_day_spread"] == -45.2 and g["eth_worst_day_spread"] == -111.6
    assert g["eth_positive_but_fading"] is True
    assert g["yen_carry_2024_08_near_break_even"] is True


def test_capabilities_false_and_tamper_rejected():
    for flag in spec._CAPABILITY_FLAGS_FALSE:
        assert _S[flag] is False, flag
        assert spec.validate_spec({**_S, flag: True})["valid"] is False
    for k, v in _S["scope_locks"].items():
        assert v is True, k
    # cannot authorize a gate now, allow a private endpoint, or claim tradability
    bad_gate = [{**g, "authorized_now": True} if g["step"] == "phase2_replay_backtest" else g
                for g in _S["human_gates"]]
    assert spec.validate_spec({**_S, "human_gates": bad_gate})["valid"] is False
    assert spec.validate_spec(
        {**_S, "allowed_public_endpoints": ["https://www.deribit.com/api/v2/private/buy"]}
    )["valid"] is False
    assert spec.validate_spec({**_S, "is_tradability_claim": True})["valid"] is False


def test_module_purity():
    src = Path(spec.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "urlopen", "urllib", "requests.", "json.load", "read_text"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
