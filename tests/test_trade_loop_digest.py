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
