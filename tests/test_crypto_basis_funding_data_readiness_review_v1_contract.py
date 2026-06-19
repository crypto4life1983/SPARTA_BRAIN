"""Tests for the Crypto basis/funding data-readiness review v1 contract.

Verifies: research-only, data-readiness-review-only, executes nothing; assigns NO C20,
opens no candidate, builds no detector/labels/replay, runs no optimization, fetches
nothing more; pins all nine PUBLIC spot/perp/funding files (64-char SHAs + row counts +
date ranges) + the manifest SHA + the common basis window; confirms monotonic timestamps
+ valid columns + public-no-credentials + gitignored-not-committed; declares the data
frozen and ready; preserves the C20 human gate; capability flags + scope locks; validator
anti-tamper; module purity. The fetched data artifacts themselves are NOT read here
(pure contract pins their SHAs) and are NOT committed."""
from __future__ import annotations

import ast

import sparta_commander.crypto_basis_funding_data_readiness_review_v1_contract as dr


_R = dr.build_data_readiness_review()


def test_review_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_data_readiness_review_only"] is True
    assert dr.validate_data_readiness_review(_R)["valid"] is True


def test_no_c20_no_candidate_no_detector_no_optimize_no_fetch():
    assert _R["assigns_c20"] is False
    assert _R["c20_assigned"] is False
    assert _R["candidate_id"] is None
    assert _R["opens_candidate"] is False
    assert _R["creates_family_proposal"] is False
    assert _R["builds_detector_labels_or_replay"] is False
    assert _R["optimizes_or_tunes"] is False
    assert _R["fetched_more_data_here"] is False


def test_nine_files_sha_rows_dates_pinned():
    files = _R["files"]
    assert len(files) == 9
    assert _R["file_count"] == 9
    for key in ("BTCUSDT_spot", "BTCUSDT_perp", "BTCUSDT_funding",
                "ETHUSDT_spot", "ETHUSDT_perp", "ETHUSDT_funding",
                "SOLUSDT_spot", "SOLUSDT_perp", "SOLUSDT_funding"):
        f = files[key]
        assert len(f["sha256"]) == 64, key
        assert f["rows"] > 0, key
        assert f["first"] and f["last"], key
        assert f["path"].startswith("data/crypto_basis_funding_research/")
    # spot-check a couple of pinned values
    assert files["BTCUSDT_spot"]["rows"] == 2350
    assert files["SOLUSDT_perp"]["rows"] == 2094
    assert files["BTCUSDT_funding"]["rows"] == 7050
    assert _R["total_rows"] == sum(f["rows"] for f in files.values())
    assert len(_R["manifest_sha256"]) == 64


def test_date_ranges_and_common_window():
    files = _R["files"]
    assert files["BTCUSDT_spot"]["first"] == "2020-01-02"
    assert files["SOLUSDT_perp"]["first"] == "2020-09-14"
    assert files["SOLUSDT_spot"]["first"] == "2020-08-11"
    for f in files.values():
        assert f["last"] == "2026-06-08"
    # the common spot+perp+funding window is gated by SOL perp start
    assert _R["common_basis_window"] == ["2020-09-14", "2026-06-08"]
    assert _R["fetch_window"] == ["2020-01-01", "2026-06-08"]


def test_columns_monotonic_public_and_gitignored():
    assert _R["klines_columns"] == ["date", "open", "high", "low", "close", "volume"]
    assert _R["funding_columns"] == ["datetime", "funding_time_ms", "symbol",
                                     "funding_rate", "mark_price"]
    assert _R["all_timestamps_monotonic"] is True
    assert _R["all_columns_valid"] is True
    assert _R["public_data_only_no_credentials"] is True
    assert _R["artifacts_gitignored_not_committed"] is True


def test_readiness_verdict_and_human_gate():
    assert _R["readiness_verdict"] == (
        "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY")
    assert _R["ready_for_future_basis_funding_research"] is True
    assert _R["supports_recommended_first_target"] == "perp_basis_spot_perp_spread"
    assert _R["requires_human_approval_before_c20"] is True
    assert _R["opening_c20_requires_explicit_open_candidate_token"] is True
    nra = dr.get_data_readiness_next_action()
    assert nra == _R["next_required_action"]
    assert "NO_C20_ASSIGNED" in nra


def test_sha_and_count_tamper_rejected():
    files = {k: dict(v) for k, v in _R["files"].items()}
    files["BTCUSDT_spot"]["sha256"] = "0" * 64
    bad = {**_R, "files": files}
    assert dr.validate_data_readiness_review(bad)["valid"] is False
    files2 = {k: dict(v) for k, v in _R["files"].items()}
    files2["SOLUSDT_perp"]["rows"] = 99999
    bad2 = {**_R, "files": files2}
    assert dr.validate_data_readiness_review(bad2)["valid"] is False


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in dr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert dr.validate_data_readiness_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_assign_c20", "no_open_candidate", "no_fetch",
                 "no_detector", "no_labels", "no_replay", "no_optimization",
                 "no_data_commit", "no_credentials", "no_network", "no_xauusd",
                 "no_commit", "no_push", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(dr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "requests"):
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
