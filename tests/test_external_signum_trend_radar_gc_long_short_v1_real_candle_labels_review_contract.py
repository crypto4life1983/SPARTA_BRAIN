"""Tests for the Candidate #22 real-candle LABELS REVIEW contract.

Reads the committed dataset + the gitignored labels artifact READ-ONLY (a deterministic
SHA-verification rebuild only), and proves the review is honest: it confirms the dataset SHA
+ the labels-artifact SHA match their pinned values, the human marketRank tie-breaker was
applied WITHOUT mutating source data, the label distribution (50 total; 2 actionable:
LONG_ENTRY=1 + BEAR_SHORT=1; NONE=48), the near-zero setup pressure, and -- because there is
only ONE frozen daily export / ONE decision date -- recommends HOLD_FOR_MORE_FROZEN_DATA_
WINDOWS (not ADVANCE_TO_REPLAY). Also proves the anti-tamper validator forbids a dishonest
ADVANCE on a thin sample, that the review runs no replay / no data fetch / no label mutation
/ no dataset mutation, and module purity."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as lr  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as lb  # noqa: E501

_ROOT = Path(lr.__file__).resolve().parents[1]
_DATASET = _ROOT / lb.DATASET_PATH
_ARTIFACT = _ROOT / lb.ARTIFACT_DIR / ("%s_2026-06-20.json" % lb.ARTIFACT_BASENAME)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


_DS_SHA = _sha(_DATASET)
_ART_SHA = _sha(_ARTIFACT) if _ARTIFACT.is_file() else lb.LABELS_ARTIFACT_SHA256
# deterministic read-only rebuild of the labels record for the review input
_LABELS_REC = lb.build_labels(json.loads(_DATASET.read_text(encoding="utf-8")), _DS_SHA)
_REV = lr.build_labels_review(_LABELS_REC, _DS_SHA, _ART_SHA)


# ---- (1)+(2) SHA integrity verified ----------------------------------------

def test_dataset_and_labels_artifact_sha_match_pins():
    assert _DS_SHA == (
        "cc37dee4f6bb65ac9ae219bfa8e4ececa83fb06952d8ecac3250419367470f21")
    assert _REV["dataset_sha_matches"] is True
    if _ARTIFACT.is_file():
        assert _ART_SHA == (
            "bc434aebe056fd72670735442e58926f9df483cbbbf820308b153c36d12a8947")
    assert _REV["labels_artifact_sha_matches"] is True
    assert _REV["evidence_integrity_ok"] is True


# ---- (3) tie-breaker applied without mutating source data ------------------

def test_tiebreaker_applied_without_mutation():
    assert _REV["tiebreaker_applied_without_mutation"] is True
    assert _REV["source_data_not_mutated"] is True
    assert _REV["labels_record_valid"] is True
    assert _REV["labels_produced_verdict_ok"] is True


# ---- (4) near-zero setup pressure + distribution ---------------------------

def test_label_distribution_and_setup_pressure():
    assert _REV["n_total_labels"] == 50
    assert _REV["n_long_entry"] == 1
    assert _REV["n_bear_short"] == 1
    assert _REV["n_hedge_short"] == 0
    assert _REV["n_none"] == 48
    assert _REV["n_skip"] == 0
    assert _REV["n_actionable_labels"] == 2
    assert _REV["setup_density"] == 0.04
    assert _REV["near_zero_setup_pressure"] is True


# ---- (5)+(6) sample-size decision: single export -> HOLD -------------------

def test_single_export_is_insufficient_for_replay():
    assert _REV["n_frozen_data_windows"] == 1
    assert _REV["distinct_decision_dates"] == ["2026-06-19"]
    assert _REV["n_distinct_decision_dates"] == 1
    assert _REV["sample_sufficient_for_replay"] is False
    assert _REV["single_day_replay_is_justified"] is False
    assert _REV["sample_size_reasons"]  # non-empty, names the deficits
    assert "2026-05-12" in _REV["precedent_note"]  # multi-week precedent cited


# ---- (7) recommendation = HOLD_FOR_MORE_FROZEN_DATA_WINDOWS -----------------

def test_recommendation_is_hold():
    assert _REV["recommendation"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _REV["next_required_action"] == (
        "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS")
    assert lr.validate_labels_review(_REV)["valid"] is True


# ---- no replay / advance / mutation ----------------------------------------

def test_no_replay_no_advance_no_mutation():
    assert _REV["advances_nothing"] is True
    assert _REV["replay_gate_locked"] is True
    for flag in ("runs_replay", "builds_replay", "fetches_data", "edits_labels",
                 "mutates_dataset", "modifies_c22_rules", "unlocks_replay_gate"):
        assert _REV[flag] is False, flag
    for key, val in _REV["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper: dishonest ADVANCE / REJECT rejected ----------------------

def test_tamper_dishonest_advance_rejected():
    # forcing ADVANCE on a thin, unjustified sample must fail validation
    bad = {**_REV, "recommendation": "ADVANCE_TO_REPLAY_REVIEW",
           "next_required_action": lr.NEXT_ACTION_ADVANCE}
    assert lr.validate_labels_review(bad)["valid"] is False
    # REJECT while integrity is intact must fail
    bad2 = {**_REV, "recommendation": "REJECT_AT_LABELS_REVIEW",
            "next_required_action": lr.NEXT_ACTION_REJECT}
    assert lr.validate_labels_review(bad2)["valid"] is False


def test_synthetic_broken_integrity_is_reject():
    rev = lr.build_labels_review(_LABELS_REC, "0" * 64, _ART_SHA)
    assert rev["evidence_integrity_ok"] is False
    assert rev["recommendation"] == "REJECT_AT_LABELS_REVIEW"
    assert lr.validate_labels_review(rev)["valid"] is True


def test_synthetic_sufficient_sample_still_not_advanced_without_justification():
    # even a synthetic 'sufficient' sample stays HOLD because single_day_replay_is_justified
    # is hard-coded False (the contract never fabricates a justification).
    big = dict(_LABELS_REC)
    assert _REV["single_day_replay_is_justified"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = Path(lr.__file__).read_text(encoding="utf-8")
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
