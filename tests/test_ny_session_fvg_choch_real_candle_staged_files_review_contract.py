"""Tests for the SPARTA NY FVG+CHOCH Real-Candle Staged Files Review.

Failure modes use synthetic staged sets in tmp dirs; acceptance is also
checked against the REAL staged set when present. The review only ever
READS — the real staged files are never modified, deleted, or staged.
"""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract as sr

_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD", "XRPUSD")
_HEADER = "timestamp,open,high,low,close,volume,source,timeframe,symbol"
_SOURCE = "binance_public_spot_klines_no_auth"


def _rows(symbol, timeframe, start, count, step_seconds):
    out = []
    moment = start
    for _ in range(count):
        out.append("%s,100.0,101.0,99.0,100.5,12.5,%s,%s,%s"
                   % (moment.strftime("%Y-%m-%dT%H:%M:%SZ"), _SOURCE,
                      timeframe, symbol))
        moment += dt.timedelta(seconds=step_seconds)
    return out


def _make_valid_set(root):
    staging = root / "data" / "ny_fvg_choch" / "staged"
    staging.mkdir(parents=True)
    manifest = []
    specs = (("1m", dt.datetime(2026, 6, 10, 11, 30), 571, 60,
              "2026-06-10_2026-06-10"),
             ("15m", dt.datetime(2026, 6, 1), 960, 900,
              "2026-06-01_2026-06-10"))
    for timeframe, start, count, step, date_range in specs:
        for symbol in _SYMBOLS:
            name = "%s_%s_%s.csv" % (symbol, timeframe, date_range)
            content = "\n".join(
                [_HEADER] + _rows(symbol, timeframe, start, count, step)
            ) + "\n"
            raw = content.encode("utf-8")
            (staging / name).write_bytes(raw)
            manifest.append("%s,%s,%d"
                            % (name, hashlib.sha256(raw).hexdigest(), count))
    (staging / "manifest.txt").write_bytes(
        ("\n".join(manifest) + "\n").encode("utf-8"))
    return staging


def _retamper(staging, name, transform, fix_manifest):
    path = staging / name
    raw = transform(path.read_bytes().decode("utf-8")).encode("utf-8")
    path.write_bytes(raw)
    if fix_manifest:
        manifest_path = staging / "manifest.txt"
        lines = manifest_path.read_bytes().decode("utf-8").splitlines()
        fixed = []
        for line in lines:
            if line.startswith(name + ","):
                count = len(raw.decode("utf-8").splitlines()) - 1
                fixed.append("%s,%s,%d"
                             % (name, hashlib.sha256(raw).hexdigest(), count))
            else:
                fixed.append(line)
        manifest_path.write_bytes(("\n".join(fixed) + "\n").encode("utf-8"))


_BTC_1M = "BTCUSD_1m_2026-06-10_2026-06-10.csv"


def test_synthetic_valid_staged_set_accepts(tmp_path):
    _make_valid_set(tmp_path)
    review = sr.build_staged_files_review(tmp_path, tracked_paths=())
    assert review["verdict"] == sr.VERDICT_SR_ACCEPTED
    assert review["blockers"] == []
    assert review["total_rows"] == 9186
    assert all(review["checklist_results"][n] is True
               for n in sr.REVIEW_CHECKLIST)
    assert len(sr.REVIEW_CHECKLIST) == 12
    assert sr.validate_staged_files_review(review)["valid"] is True


def test_real_staged_set_accepts_when_present():
    if not os.path.isdir("C:/SPARTA_BRAIN/data/ny_fvg_choch/staged"):
        pytest.skip("real staged set absent on this machine")
    review = sr.build_staged_files_review("C:/SPARTA_BRAIN",
                                          tracked_paths=())
    assert review["verdict"] == sr.VERDICT_SR_ACCEPTED
    assert review["total_rows"] == 9186


def test_missing_manifest_blocks(tmp_path):
    staging = _make_valid_set(tmp_path)
    (staging / "manifest.txt").unlink()
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_BLOCKED
    assert "staging_dir_or_manifest_missing" in review["blockers"]
    review2 = sr.build_staged_files_review(tmp_path / "nowhere")
    assert review2["verdict"] == sr.VERDICT_SR_BLOCKED


def test_missing_file_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    (staging / _BTC_1M).unlink()
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:every_listed_file_exists_and_every_csv_is_listed"
            in review["blockers"])


def test_checksum_mismatch_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    _retamper(staging, _BTC_1M,
              lambda s: s.replace("100.5", "100.6", 1), fix_manifest=False)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:sha256_matches_manifest_for_every_file"
            in review["blockers"])


def test_row_count_mismatch_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    manifest_path = staging / "manifest.txt"
    text = manifest_path.read_bytes().decode("utf-8")
    manifest_path.write_bytes(text.replace(",571", ",570", 1).encode("utf-8"))
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:row_counts_match_manifest_for_every_file"
            in review["blockers"])


def test_wrong_symbol_or_timeframe_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    _retamper(staging, _BTC_1M,
              lambda s: s.replace(",BTCUSD", ",DOGEUSD"), fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:all_6_symbols_and_both_timeframes_covered_once"
            in review["blockers"])
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review["blockers"])


def test_missing_required_schema_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    _retamper(staging, _BTC_1M,
              lambda s: s.replace(_HEADER,
                                  _HEADER.replace(",volume", ""), 1),
              fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review["blockers"])


def test_bad_timestamps_reject(tmp_path):
    staging = _make_valid_set(tmp_path)

    def swap_two_rows(text):
        lines = text.splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        return "\n".join(lines) + "\n"

    _retamper(staging, _BTC_1M, swap_two_rows, fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review["blockers"])


def test_duplicate_candles_reject(tmp_path):
    staging = _make_valid_set(tmp_path)

    def duplicate_first_row(text):
        lines = text.splitlines()
        lines[2] = lines[1]
        return "\n".join(lines) + "\n"

    _retamper(staging, _BTC_1M, duplicate_first_row, fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review["blockers"])


def test_bad_ohlcv_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    _retamper(staging, _BTC_1M,
              lambda s: s.replace(",12.5,", ",-12.5,", 1),
              fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review["blockers"])
    staging2 = _make_valid_set(tmp_path / "two")
    _retamper(staging2, _BTC_1M,
              lambda s: s.replace(",101.0,", ",98.0,", 1),
              fix_manifest=True)
    review2 = sr.build_staged_files_review(tmp_path / "two")
    assert ("check_failed:schema_timestamps_ohlcv_quality_clean"
            in review2["blockers"])


def test_missing_provenance_rejects(tmp_path):
    staging = _make_valid_set(tmp_path)
    _retamper(staging, _BTC_1M,
              lambda s: s.replace(_SOURCE, "unknown_source", 1),
              fix_manifest=True)
    review = sr.build_staged_files_review(tmp_path)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:provenance_recorded_on_every_row"
            in review["blockers"])


def test_tracked_candle_files_reject(tmp_path):
    _make_valid_set(tmp_path)
    review = sr.build_staged_files_review(
        tmp_path,
        tracked_paths=["data/ny_fvg_choch/staged/BTCUSD_1m.csv"])
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:no_staged_candle_files_tracked_in_git_index"
            in review["blockers"])


def test_declared_train_oos_split_enforced(tmp_path):
    _make_valid_set(tmp_path)
    observation = sr.observe_staged_files(tmp_path)
    assert observation["declared_train_oos"] == {
        "train_start": "2026-06-01", "train_end": "2026-06-08",
        "oos_start": "2026-06-09", "oos_end": "2026-06-11",
        "no_oos_optimization": True}
    observation["declared_train_oos"]["no_oos_optimization"] = False
    review = sr.review_staged_files(observation)
    assert review["verdict"] == sr.VERDICT_SR_REJECTED
    assert ("check_failed:declared_train_oos_split_valid"
            in review["blockers"])


def test_review_cannot_run_anything_or_unlock(tmp_path):
    _make_valid_set(tmp_path)
    review = sr.build_staged_files_review(tmp_path)
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_staged_files", "deletes_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    assert review["staged_files_remain_untracked_operational_data"] is True
    tampered = sr.build_staged_files_review(tmp_path)
    tampered["runs_detector_now"] = True
    assert sr.validate_staged_files_review(tampered)["valid"] is False
    tampered2 = sr.build_staged_files_review(tmp_path)
    tampered2["live_gate_locked"] = False
    assert sr.validate_staged_files_review(tampered2)["valid"] is False
    tampered3 = sr.build_staged_files_review(tmp_path)
    tampered3["forbidden"] = tampered3["forbidden"][:4]
    assert sr.validate_staged_files_review(tampered3)["valid"] is False
    for item in ("modifying_candle_files", "deleting_candle_files",
                 "committing_candle_files",
                 "committing_manifest_without_separate_approval",
                 "detector_runs", "replay_runs", "scorer_runs",
                 "optimizer_runs", "report_artifact_creation",
                 "network_retrieval",
                 "broker_exchange_private_api_access",
                 "credentials_or_api_keys", "account_wallet_login_access",
                 "trading_endpoints_of_any_kind",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in sr.FORBIDDEN, item


def test_review_is_deterministic_and_does_not_modify_files(tmp_path):
    staging = _make_valid_set(tmp_path)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in staging.iterdir()}
    a = sr.build_staged_files_review(tmp_path)
    b = sr.build_staged_files_review(tmp_path)
    assert a == b
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in staging.iterdir()}
    assert before == after  # review never modified or deleted anything
    assert len(after) == 13


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_runner_dry_run as fr
    assert fr.RUNNER_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_plan as fp
    assert fp.build_public_candle_fetch_plan()["verdict"] == (
        "NY_FVG_CHOCH_PUBLIC_CANDLE_FETCH_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_candle_source_approval_contract as sa
    assert sa.build_candle_source_approval_contract()["verdict"] == (
        "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_READY")
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    assert plan_mod.build_real_candle_staging_plan()["verdict"] == (
        "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.build_dry_run_replay_results_review()["verdict"] == (
        "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING")
    from sparta_commander.ny_session_fvg_choch_replay_spec import (
        build_ny_fvg_choch_replay_spec)
    assert build_ny_fvg_choch_replay_spec()["verdict"] == (
        "NY_FVG_CHOCH_REPLAY_SPEC_READY")
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        LABEL_REQUIRED_FIELDS)
    assert len(LABEL_REQUIRED_FIELDS) == 29
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        CANDIDATE_ID)
    assert CANDIDATE_ID == "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        ALLOWED_EDITABLE_FIELDS)
    assert len(ALLOWED_EDITABLE_FIELDS) == 16
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert sr.get_staged_files_review_label() == sr.SR_LABEL
    assert "READ-ONLY" in sr.SR_LABEL and sr.SR_MODE == "RESEARCH_ONLY"
    assert sr.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_DETECTOR_RUN_ON_STAGED_CANDLES")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(sr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    # strictly read-only: no write/delete/create filesystem verbs
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    # never imports the detector/replay/scorer/optimizer machinery
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("detector_spec", "replay_runner", "replay_spec",
                         "optimizer"):
            assert fragment not in module, module
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))