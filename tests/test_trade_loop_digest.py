from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import trade_loop_digest as dg  # noqa: E402


def _ledger(status="SHADOW"):
    return {"hypotheses": {"block_long_in_TREND_DOWN": {
        "status": status, "registered_as_of": "2026-09-11",
        "forward": {"n_signals": 3, "delta_R_mean": 0.4, "bootstrap_p_positive": None},
        "thresholds": {"min_forward_signals": 20, "min_p_positive": 0.9},
    }}}


def _scorecard():
    return [{"line": "nq_orb_paper", "status": "REJECTED", "sign": "NEGATIVE",
             "window": {"satisfied": True}, "reason": "own gate c3 failed"},
            {"line": "gc_ict_paper", "status": "BLOCKED", "sign": "NONE",
             "window": {"satisfied": False}, "reason": "tracker PAUSE"}]


def test_digest_has_all_sections_and_queue():
    md = dg.build_digest({"counts": {"closed": 42, "distinct_signals_closed": 31, "sum_R_dedup_best": 7.77,
                                     "expectancy_R": 0.34, "win_rate": 0.45}, "suggestions": [1, 2],
                          "sample_quality": {"overall_label": "OK"}},
                         _ledger(), {"n_signals": 31, "cells_tested": 15, "proposals": [], "cells": []},
                         _scorecard(), "2026-09-11")
    for h in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5."):
        assert h in md
    assert "OBSERVATION ONLY" in md
    assert "record closure of nq_orb_paper" in md
    assert "unblock or retire gc_ict_paper" in md
    assert "CONFIRMED rules awaiting the operator: **0**" in md
    assert dg.forbidden_words_found(md) == []


def test_confirmed_rule_enters_queue():
    md = dg.build_digest(None, _ledger("CONFIRMED"), None, None, "2026-09-11")
    assert "apply CONFIRMED rule `block_long_in_TREND_DOWN`" in md
    assert "learning report missing" in md and "scorecard missing" in md


def test_empty_inputs_do_not_crash():
    md = dg.build_digest(None, None, None, None, "2026-09-11")
    assert "none today" in md


def test_line_closed_on_record_leaves_the_queue():
    """Once the operator's closure is recorded, the line must stop being queued."""
    sc = [{"line": "nq_orb_paper", "status": "REJECTED", "sign": "NONE",
           "window": {"satisfied": True},
           "reason": "closed by recorded operator decision (CLOSURE_DECISION_2026-09-11.md)"},
          {"line": "other_line", "status": "REJECTED", "sign": "NEGATIVE",
           "window": {"satisfied": True}, "reason": "own gate failed"}]
    md = dg.build_digest(None, _ledger(), None, sc, "2026-09-12")
    assert "record closure of nq_orb_paper" not in md
    assert "record closure of other_line" in md


# ── evidence split (pre / post 2026-09-15 partial-bar fix) ──────────────────

def _learning_with_split(valid_closed=2, retired_closed=42):
    return {
        "counts": {"closed": valid_closed + retired_closed, "distinct_signals_closed": 33,
                   "sum_R_dedup_best": 5.74, "expectancy_R": 0.28, "win_rate": 0.432},
        "suggestions": [],
        "sample_quality": {"overall_label": "OK"},
        "evidence_split": {
            "cutoff": "2026-09-15",
            "cutoff_field": "open_date",
            "cutoff_reason": "partial-bar fix",
            "valid_forward": {"closed": valid_closed, "distinct_signals_closed": valid_closed,
                              "sum_R_raw": -2.034, "expectancy_R": -1.017, "win_rate": 0.0,
                              "outcome_WIN": 0, "outcome_TIMEOUT_positive": 0},
            "retired": {"closed": retired_closed, "distinct_signals_closed": 31,
                        "sum_R_raw": 14.359, "expectancy_R": 0.342, "win_rate": 0.452,
                        "outcome_WIN": 2, "outcome_TIMEOUT_positive": 17},
            "retired_share_of_closed": 0.955,
            "note": "headline counts cover ALL closed trades",
        },
    }


def test_digest_shows_valid_forward_and_retired_buckets():
    md = dg.build_digest(_learning_with_split(), _ledger(), None, _scorecard(), "2026-09-21")
    assert "valid forward evidence (opened on/after 2026-09-15)" in md
    assert "retired (opened before 2026-09-15" in md
    # both buckets' numbers are present, so the retired record cannot be
    # mistaken for the live one
    assert "-1.017" in md and "0.342" in md
    # the WIN vs profitable-TIMEOUT contrast that explains the retired edge
    assert "2 WIN vs 17 profitable TIMEOUT" in md


def test_digest_warns_when_valid_evidence_is_below_threshold():
    md = dg.build_digest(_learning_with_split(valid_closed=2), _ledger(), None,
                         _scorecard(), "2026-09-21")
    assert "NOT a track record of the system now running" in md
    assert f"< {dg.MIN_VALID_EVIDENCE}" in md


def test_digest_drops_the_warning_once_enough_valid_evidence_exists():
    md = dg.build_digest(_learning_with_split(valid_closed=dg.MIN_VALID_EVIDENCE),
                         _ledger(), None, _scorecard(), "2026-09-21")
    assert "valid forward evidence" in md
    assert "NOT a track record of the system now running" not in md


def test_digest_without_evidence_split_still_renders():
    """An older latest.json has no evidence_split key; the digest must not break."""
    learning = _learning_with_split()
    learning.pop("evidence_split")
    md = dg.build_digest(learning, _ledger(), None, _scorecard(), "2026-09-21")
    assert "## 1." in md and "valid forward evidence" not in md
    assert dg.forbidden_words_found(md) == []


def test_evidence_split_lines_are_empty_for_missing_input():
    assert dg._evidence_split_lines(None) == []
