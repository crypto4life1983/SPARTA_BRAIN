"""Tests for the Strategy Factory commit guard. Offline, no network, no git.

This file lives under tests/ which the safety-guard source scanner excludes, so
it may contain the sensitive vendor/credential tokens used as fixtures.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import commit_guard  # noqa: E402


# --- allowed (factory documentation lane) ----------------------------------

def test_report_paths_are_allowed():
    paths = [
        "trading_research/agentic_factory/reports/strategy_factory_v1_hygiene_bundle_h1_h2/report.md",
        "trading_research/agentic_factory/reports/strategy_factory_v1_hygiene_bundle_h1_h2/report.json",
    ]
    res = commit_guard.check_paths(paths)
    assert res["ok"] is True
    assert res["blocked"] == []
    assert len(res["allowed"]) == 2


def test_guard_own_files_are_allowed():
    # The guard must approve its own tooling (tools/ is not a strategy path).
    paths = [
        "trading_research/agentic_factory/tools/commit_guard.py",
        "trading_research/agentic_factory/tools/commit_guard_rules.json",
        "trading_research/agentic_factory/tests/test_commit_guard.py",
    ]
    res = commit_guard.check_paths(paths)
    assert res["ok"] is True
    assert res["blocked"] == []


# --- hard-blocked categories ------------------------------------------------

def test_jarvis_files_blocked():
    for p in ["app.py", "templates/jarvis.html", "tests/test_jarvis_route.py",
              "docs/jarvis_checkpoint_bundle_b/report.json", "templates/base.html"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["category"] == "jarvis"


def test_data_files_blocked():
    for p in ["trading_research/agentic_factory/data_offline/nq_c0_ohlcv_1d_2013.csv",
              "data/asset_registry.json",
              "trading_research/agentic_factory/data_crypto/spot_binance_usdt_1d_2020_2025/BTCUSDT_1d_2020_2025.csv",
              "data/databento_cache/foo.parquet"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["category"] == "data_file"


def test_runtime_snapshot_blocked():
    # Paths chosen to uniquely exercise the runtime_snapshot category (not under
    # data/ and not jarvis, which would otherwise match first).
    for p in ["trading_research/agentic_factory/reports/live_snapshot_20260530.json",
              "engine_state_snapshot.json",
              "sparta_status.json"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["category"] == "runtime_snapshot"


def test_profit_brain_and_media_runtime_files_blocked():
    # These live under data/, so they read as data_file (also hard-blocked) —
    # the security contract is "blocked", regardless of which hard bucket wins.
    for p in ["data/profit_brain_daily_snapshots.jsonl",
              "data/media_os_pipeline_status.json"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["severity"] == "hard"


def test_broker_live_paper_credential_blocked():
    for p in ["paper_trading/engine.py",
              "broker/bybit_adapter.py",
              "local_secrets/keys.json",
              "config/.env",
              "wallet/binance_api_key.txt",
              "sparta_commander/research_orchestrator/safe_executor.py"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["category"] == "broker_live_paper"


# --- overridable category (strategy mutation) -------------------------------

def test_strategy_files_blocked_by_default():
    for p in ["trading_research/agentic_factory/engine/donchian_daily.py",
              "trading_research/agentic_factory/config/factory_config.yaml",
              "trading_research/agentic_factory/strategies/nq_orb/nq_orb_spec.md",
              "trading_research/agentic_factory/loop/factory_loop.py"]:
        res = commit_guard.check_paths([p])
        assert res["ok"] is False, p
        assert res["blocked"][0]["category"] == "strategy_mutation"


def test_strategy_files_allowed_with_override():
    p = "trading_research/agentic_factory/engine/s30_overnight_drift.py"
    res = commit_guard.check_paths([p], allow_strategy=True)
    assert res["ok"] is True
    assert res["blocked"] == []
    assert res["overridden"][0]["category"] == "strategy_mutation"


def test_override_does_not_relax_hard_categories():
    # Even with allow_strategy, broker / data / jarvis stay blocked.
    paths = ["broker/live_exec.py",
             "trading_research/agentic_factory/data_offline/nq_c0_ohlcv_1d_2013.csv",
             "app.py"]
    res = commit_guard.check_paths(paths, allow_strategy=True)
    assert res["ok"] is False
    assert {b["category"] for b in res["blocked"]} == {"broker_live_paper", "data_file", "jarvis"}


# --- mixed sets, ordering, normalization, edges -----------------------------

def test_mixed_set_blocks_when_any_forbidden():
    paths = [
        "trading_research/agentic_factory/reports/x/report.md",   # allowed
        "app.py",                                                 # blocked
    ]
    res = commit_guard.check_paths(paths)
    assert res["ok"] is False
    assert len(res["allowed"]) == 1
    assert len(res["blocked"]) == 1


def test_backslash_paths_are_normalized():
    p = r"trading_research\agentic_factory\data_offline\nq_c0_ohlcv_1d_2013.csv"
    res = commit_guard.check_paths([p])
    assert res["ok"] is False
    assert res["blocked"][0]["category"] == "data_file"


def test_empty_set_passes():
    res = commit_guard.check_paths([])
    assert res["ok"] is True
    assert res["checked"] == 0


def test_classify_path_returns_none_for_allowed():
    assert commit_guard.classify_path(
        "trading_research/agentic_factory/reports/x/report.json") is None


def test_broker_severity_is_hard():
    hit = commit_guard.classify_path("broker/adapter.py")
    assert hit is not None
    assert hit["severity"] == "hard"


def test_main_returns_nonzero_on_blocked(capsys):
    rc = commit_guard.main(["app.py"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "BLOCKED" in out


def test_main_returns_zero_on_clean(capsys):
    rc = commit_guard.main([
        "trading_research/agentic_factory/reports/x/report.md",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "PASS" in out
