"""Tests for the Candidate #22 real-candle DATASET VALIDATION contract.

Reads the single locally-staged Signum Trend Radar GC detector dataset READ-ONLY, pins its
SHA256, and proves the outcome AFTER the human duplicate-marketRank resolution: the dataset
is structurally complete (50 gc rows, indicators.data latest+previous candles with
gc.trend/upper/filter, cmcRefPriceUsd, numeric marketRank) and although marketRank is NOT
unique (value 60 duplicated), the human deterministic tie-breaker (marketRank asc, marketCap
desc, symbol asc) yields a strict total entry ordering -- so the verdict is
DATASET_VALID_VIA_MARKET_RANK_TIEBREAKER and it may proceed to labels. The dataset is NOT
mutated and NO marketRank value is invented. Also proves the synthetic unique-VALID,
ENTRIES_INVALID (no total order), and DATASET_INVALID branches, the anti-tamper validator,
and module purity (no file/network I/O in the contract)."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as dv  # noqa: E501

_ROOT = Path(dv.__file__).resolve().parents[1]
_DATASET = _ROOT / dv.DATASET_PATH


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


_SHA = _file_sha256(_DATASET)
_PARSED = json.loads(_DATASET.read_text(encoding="utf-8"))
_FACTS = dv.extract_dataset_facts(_PARSED)
_REC = dv.build_dataset_validation(_FACTS, _SHA)


# ---- the staged file is the pinned artifact --------------------------------

def test_dataset_exists_and_sha_matches_pin():
    assert _DATASET.is_file()
    assert _SHA == dv.DATASET_SHA256
    assert _REC["sha256_matches_pin"] is True


# ---- required fields all present (structurally complete) -------------------

def test_required_fields_present():
    assert _FACTS["row_count"] == 50
    assert _FACTS["all_detector_gc"] is True
    assert _FACTS["rows_missing_indicators_data"] == 0
    assert _FACTS["latest_and_previous_candles_present"] is True
    assert _FACTS["gc_trend_upper_filter_present"] is True
    assert _FACTS["cmc_ref_price_usd_present"] is True
    assert _FACTS["market_rank_present_numeric"] is True
    assert _REC["structurally_complete"] is True
    assert _REC["required_field_checks"]["row_count_50"] is True


# ---- marketRank is NOT unique (value 60 duplicated) ------------------------

def test_market_rank_not_unique():
    assert _FACTS["market_rank_unique"] is False
    assert _FACTS["distinct_market_rank_count"] == 49
    assert _FACTS["duplicate_market_ranks"] == [60]
    assert _REC["market_rank_unique"] is False
    assert _REC["duplicate_market_ranks"] == [60]


# ---- resolved verdict: VALID_VIA_TIEBREAKER, no mutation, no invented rank --

def test_verdict_valid_via_tiebreaker_no_mutation():
    assert _REC["verdict"] == dv.VERDICT_VALID_VIA_TIEBREAKER
    assert _REC["proceed_to_labels"] is True
    assert _REC["had_market_rank_ties"] is True
    assert _REC["tiebreaker_applied"] is True
    assert _REC["tiebreaker_yields_total_order"] is True
    assert _REC["market_rank_tiebreaker"] == [
        "market_rank_asc", "market_cap_desc", "symbol_asc"]
    # dataset NOT mutated; NO rank invented or repaired
    assert _REC["repaired_market_rank"] is False
    assert _REC["invented_ranks"] is False
    assert _REC["mutated_dataset"] is False
    assert _REC["repairs_market_rank"] is False
    # validation still builds no labels itself
    assert _REC["labels_produced"] == 0
    assert _REC["next_required_action"] == (
        "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    assert dv.validate_dataset_validation(_REC)["valid"] is True


def test_tiebreaker_orders_qnt_before_pol():
    order = _REC["tie_broken_order_symbols"]
    assert len(order) == 50
    assert len(set(order)) == 50  # strict total order
    assert order.index("BINANCE:QNTUSDT") < order.index("BINANCE:POLUSDT")


# ---- chain provenance: gated on frozen spec + frozen detector --------------

def test_chain_gated_on_frozen_spec_and_detector():
    assert _REC["spec_verdict"] == "C22_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert _REC["spec_commit"] == dv.SPEC_COMMIT
    assert _REC["detector_verdict"] == "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert _REC["chain_gated"] is True


# ---- downstream gates locked + advances nothing ----------------------------

def test_downstream_locked_and_advances_nothing():
    for g in ("labels_gate_locked", "replay_gate_locked",
              "paper_trading_gate_locked", "live_gate_locked"):
        assert _REC[g] is True, g
    assert _REC["advances_nothing"] is True
    for flag in dv._CAPABILITY_FLAGS_FALSE:
        assert _REC[flag] is False, flag
    for key, val in _REC["scope_locks"].items():
        assert val is True, key


# ---- synthetic branches: VALID (unique) + DATASET_INVALID ------------------

def test_synthetic_unique_rank_is_valid_proceed():
    facts = {
        "row_count": 50, "all_detector_gc": True,
        "rows_missing_indicators_data": 0,
        "latest_and_previous_candles_present": True,
        "gc_trend_upper_filter_present": True,
        "cmc_ref_price_usd_present": True, "market_rank_present_numeric": True,
        "distinct_market_rank_count": 50, "market_rank_unique": True,
        "duplicate_market_ranks": []}
    rec = dv.build_dataset_validation(facts, dv.DATASET_SHA256)
    assert rec["verdict"] == dv.VERDICT_VALID
    assert rec["proceed_to_labels"] is True
    assert rec["next_required_action"] == (
        "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    assert dv.validate_dataset_validation(rec)["valid"] is True


def test_synthetic_structurally_incomplete_is_dataset_invalid():
    facts = dict(_FACTS)
    facts["row_count"] = 49  # wrong row count
    facts["latest_and_previous_candles_present"] = False
    rec = dv.build_dataset_validation(facts, _SHA)
    assert rec["verdict"] == dv.VERDICT_DATASET_INVALID
    assert rec["proceed_to_labels"] is False
    assert rec["structurally_complete"] is False
    assert dv.validate_dataset_validation(rec)["valid"] is True


def test_sha_mismatch_is_dataset_invalid():
    rec = dv.build_dataset_validation(_FACTS, "0" * 64)
    assert rec["sha256_matches_pin"] is False
    assert rec["verdict"] == dv.VERDICT_DATASET_INVALID


def test_synthetic_no_total_order_is_entries_invalid():
    # structurally complete + numeric ranks but the tie-breaker cannot totally order
    # (e.g. duplicate symbols) -> ENTRIES_INVALID, no proceed, human gate required.
    facts = {
        "row_count": 50, "all_detector_gc": True,
        "rows_missing_indicators_data": 0,
        "latest_and_previous_candles_present": True,
        "gc_trend_upper_filter_present": True,
        "cmc_ref_price_usd_present": True, "market_rank_present_numeric": True,
        "distinct_market_rank_count": 49, "market_rank_unique": False,
        "duplicate_market_ranks": [60], "had_market_rank_ties": True,
        "tie_broken_order_symbols": ["S"] * 50, "distinct_symbols": 49,
        "tiebreaker_total_order": False}
    rec = dv.build_dataset_validation(facts, dv.DATASET_SHA256)
    assert rec["verdict"] == dv.VERDICT_ENTRIES_INVALID
    assert rec["proceed_to_labels"] is False
    assert rec["requires_human_rank_disambiguation_gate"] is True
    assert rec["next_required_action"] == (
        "HUMAN_DECISION_C22_RESOLVE_DUPLICATE_MARKET_RANK_OR_REJECT")
    assert dv.validate_dataset_validation(rec)["valid"] is True


# ---- anti-tamper: cannot fake VALID or claim a repair ----------------------

def test_tamper_valid_with_nonunique_rank_rejected():
    bad = {**_REC, "verdict": dv.VERDICT_VALID, "proceed_to_labels": True,
           "next_required_action": dv.NEXT_ACTION_VALID}
    assert dv.validate_dataset_validation(bad)["valid"] is False


def test_tamper_claimed_repair_rejected():
    bad = {**_REC, "repaired_market_rank": True}
    assert dv.validate_dataset_validation(bad)["valid"] is False
    bad2 = {**_REC, "labels_produced": 5}
    assert dv.validate_dataset_validation(bad2)["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = Path(dv.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "json.load", "read_text", "read_bytes"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas"}
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
