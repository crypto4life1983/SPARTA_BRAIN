"""Tests for the Candidate #22 real-candle ENTRY-SIGNAL LABELS contract + runner.

Reads the SHA-pinned staged GC dataset READ-ONLY and proves the labels produced after the
human marketRank tie-breaker: 50 deterministic per-asset entry-signal labels in tie-broken
order (LONG_ENTRY / HEDGE_SHORT / BEAR_SHORT / NONE), counts LONG_ENTRY=1 (DEXE),
BEAR_SHORT=1 (QNT, the tie-broken rank-60 asset), NONE=48; BTC present + in downtrend; the
bear high-multiple single-sourced from the frozen detector; the dataset NOT mutated and NO
rank invented; the canonical artifact byte-stable + its SHA256 pinned in the contract and
matching the on-disk gitignored artifact; the blocked branch on an invalid dataset; the
anti-tamper validator; and module purity (no file/network I/O in the contract)."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as lb  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as dr  # noqa: E501
import tools.c22_signum_trend_radar_gc_real_candle_labels_once as runner

_ROOT = Path(lb.__file__).resolve().parents[1]
_DATASET = _ROOT / lb.DATASET_PATH


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


_DS_SHA = _sha(_DATASET)
_PARSED = json.loads(_DATASET.read_text(encoding="utf-8"))
_REC = lb.build_labels(_PARSED, _DS_SHA)
_BY_SYMBOL = {lab["symbol"]: lab for lab in _REC["labels"]}


# ---- labels produced, chain-gated on a valid dataset validation ------------

def test_labels_produced_and_valid():
    assert _REC["verdict"] == lb.VERDICT_LABELS_PRODUCED
    assert _REC["dataset_validation_verdict"] == (
        "C22_DATASET_VALID_VIA_MARKET_RANK_TIEBREAKER_PROCEED_TO_LABELS")
    assert _REC["chain_gated_on_validation"] is True
    assert _REC["labels_produced"] == 50
    assert len(_REC["labels"]) == 50
    assert lb.validate_labels(_REC)["valid"] is True


# ---- counts + the actionable per-asset signals -----------------------------

def test_label_counts_and_actionable_signals():
    assert _REC["label_counts"] == {
        "LONG_ENTRY": 1, "HEDGE_SHORT": 0, "BEAR_SHORT": 1, "NONE": 48, "SKIP": 0}
    assert sum(_REC["label_counts"].values()) == 50
    assert _BY_SYMBOL["BINANCE:DEXEUSDT"]["signal"] == "LONG_ENTRY"
    assert _BY_SYMBOL["BINANCE:QNTUSDT"]["signal"] == "BEAR_SHORT"
    assert _BY_SYMBOL["BINANCE:BTCUSDT"]["signal"] == "NONE"
    # BTC regime drove the bear short
    assert _REC["btc_present"] is True
    assert _REC["btc_downtrend"] is True


# ---- ordering is the human tie-breaker (QNT before POL); raw rank preserved -

def test_tiebroken_order_and_raw_rank_preserved():
    order = _REC["tie_broken_order_symbols"]
    assert len(order) == 50 and len(set(order)) == 50
    assert order.index("BINANCE:QNTUSDT") < order.index("BINANCE:POLUSDT")
    assert [lab["order_index"] for lab in _REC["labels"]] == list(range(50))
    # the tie-broken asset is flagged + its RAW provider rank (60) is preserved verbatim
    qnt = _BY_SYMBOL["BINANCE:QNTUSDT"]
    pol = _BY_SYMBOL["BINANCE:POLUSDT"]
    assert qnt["market_rank_raw"] == 60 and pol["market_rank_raw"] == 60
    assert qnt["tie_broken"] is True and pol["tie_broken"] is True
    assert _REC["dataset_mutated"] is False
    assert _REC["repaired_market_rank"] is False
    assert _REC["invented_ranks"] is False
    assert _REC["raw_market_rank_preserved"] is True


# ---- bear multiple single-sourced from the frozen detector -----------------

def test_bear_multiple_single_sourced():
    assert _REC["bear_high_multiple_single_sourced"] == dr.BEAR_HIGH_MULT == 0.98


# ---- determinism + artifact SHA pinned + matches on-disk gitignored file ----

def test_artifact_determinism_and_sha_pin():
    rec2 = lb.build_labels(_PARSED, _DS_SHA)
    assert rec2["labels_payload"] == _REC["labels_payload"]  # byte-stable payload
    blob = runner.canonical_labels_bytes(_REC["labels_payload"])
    assert hashlib.sha256(blob).hexdigest() == lb.LABELS_ARTIFACT_SHA256
    # the on-disk gitignored artifact matches the pin
    art = _ROOT / lb.ARTIFACT_DIR / (
        "%s_2026-06-20.json" % lb.ARTIFACT_BASENAME)
    if art.is_file():
        assert _sha(art) == lb.LABELS_ARTIFACT_SHA256


def test_artifact_path_is_gitignored_location():
    assert _REC["artifact_dir"] == "data/external_signum_trend_radar_gc/detector_labels"
    assert _REC["artifact_gitignored"] is True


# ---- blocked branch on an invalid dataset (sha mismatch) -------------------

def test_blocked_when_dataset_invalid():
    rec = lb.build_labels(_PARSED, "0" * 64)
    assert rec["verdict"] == lb.VERDICT_LABELS_BLOCKED
    assert rec["labels_produced"] == 0
    assert rec["labels"] == []
    assert rec["blockers"]
    assert lb.validate_labels(rec)["valid"] is True


# ---- anti-tamper: cannot fake mutation / invented rank / extra labels -------

def test_tamper_rejected():
    assert lb.validate_labels({**_REC, "dataset_mutated": True})["valid"] is False
    assert lb.validate_labels({**_REC, "invented_ranks": True})["valid"] is False
    assert lb.validate_labels(
        {**_REC, "labels_artifact_sha256_pinned": "x"})["valid"] is False
    # a tampered count that no longer sums to 50
    bad_counts = dict(_REC["label_counts"]); bad_counts["NONE"] = 0
    assert lb.validate_labels({**_REC, "label_counts": bad_counts})["valid"] is False


# ---- downstream gates locked + advances nothing ----------------------------

def test_downstream_locked_and_capability_flags():
    for g in ("replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        assert _REC[g] is True, g
    assert _REC["advances_nothing"] is True
    assert _REC["next_required_action"] == (
        "HUMAN_DECISION_C22_REVIEW_REAL_CANDLE_LABELS_OR_REJECT")
    for flag in lb._CAPABILITY_FLAGS_FALSE:
        assert _REC[flag] is False, flag
    for key, val in _REC["scope_locks"].items():
        assert val is True, key


# ---- module purity (the pure labels contract) ------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = Path(lb.__file__).read_text(encoding="utf-8")
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
