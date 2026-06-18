"""Tests that the overnight autopilot run-record next human gate is ALIGNED to the
post-C16 automation-readiness directive, with no residual drift to
HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY.

Read-only: imports the runner module (no main() execution at import) and inspects
its source. No detector/labels/replay/PnL/data fetch; no trading code."""
from __future__ import annotations

from pathlib import Path

import tools.overnight_autopilot_run_once as runner

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_SRC = (_REPO_ROOT / "tools" / "overnight_autopilot_run_once.py").read_text(
    encoding="utf-8")


def test_run_record_gate_constant_is_automation_readiness():
    assert runner.NEXT_HUMAN_GATE == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"


def test_run_record_uses_the_constant_not_the_old_gate():
    # the run record assigns next_human_gate from the constant
    assert '"next_human_gate": NEXT_HUMAN_GATE,' in RUNNER_SRC
    # the old next-candidate gate string is no longer the run-record's value
    assert '"next_human_gate": "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"' \
        not in RUNNER_SRC


def test_seed_brief_direction_aligned_to_automation_readiness():
    # the seed-brief draft direction now points at automation readiness, not a
    # "next candidate family" gate.
    assert "AUTOMATION READINESS" in RUNNER_SRC
    assert "NEXT_HUMAN_GATE + \".\"" in RUNNER_SRC
    # no leftover hardcoded next-candidate gate anywhere in the runner
    assert "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY" not in RUNNER_SRC


def test_runner_remains_research_only_no_trading_reach():
    for tok in ("import ccxt", "from ccxt", "place_order", "create_order",
                "paper_trade", "live_trade", "broker", "api.telegram.org"):
        assert tok not in RUNNER_SRC, tok
    # the run record still asserts no commit / no push / no claims
    assert '"no_commit_no_push": True' in RUNNER_SRC
    assert '"claims_made": "none"' in RUNNER_SRC
