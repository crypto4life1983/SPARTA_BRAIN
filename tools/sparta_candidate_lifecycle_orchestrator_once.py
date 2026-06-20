"""SPARTA candidate-lifecycle ORCHESTRATOR runner (READ-ONLY; SUGGESTION-ONLY; ONE-SHOT).

Reads the live C22 collection window count READ-ONLY (committed tracker listing) and prints
the current candidate/lane gate + the single SUGGESTED next human token. C22 is treated as
the ACTIVE collection lane (c22_concluded=False) -- the orchestrator never decides that C22
has concluded and never advances it.

It advances NO candidate, opens NO C23, runs NO labels/replay, auto-executes NO token,
modifies NO repo, changes NO scheduled task, makes NO network call, connects to NO
Signum/MCP, and does NO commit/push.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_candidate_lifecycle_orchestrator_contract as _lo  # noqa: E402,E501
import tools.sparta_current_state_once as _cs  # noqa: E402


def build_lifecycle_finding() -> dict:
    """READ-ONLY: gather the live C22 window count and compute the lifecycle gate. C22 is
    active (not concluded); nothing is advanced."""
    collected, _latest, _days = _cs.gather_c22_collection()
    finding = _lo.build_lifecycle(collected_windows=collected, c22_concluded=False)
    assert _lo.validate_lifecycle(finding)["valid"], "lifecycle_failed_validation"
    return finding


def main() -> int:
    f = build_lifecycle_finding()
    st = f["lifecycle_state"]
    print(json.dumps({
        "current_gate": f["current_gate"],
        "c22_gate": f["c22_gate"],
        "c23_gate": f["c23_gate"],
        "suggested_human_token": f["suggested_human_token"],
        "c22_progress": st["c22_progress"],
        "c22_state": st["c22_state"],
        "c21_closed_rejected": st["c21_closed_rejected"],
        "c23_on_deck": st["c23_on_deck"],
        "advances_any_candidate": f["advances_any_candidate"],
        "opens_c23_as_active": f["opens_c23_as_active"],
        "auto_executes_any_token": f["auto_executes_any_token"],
        "modifies_repo": f["modifies_repo"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
