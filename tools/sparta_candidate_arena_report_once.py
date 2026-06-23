"""SPARTA Candidate Arena report (READ-ONLY; REPORTING ONLY; ONE-SHOT).

Renders the pure `sparta_candidate_arena_v1_contract` normalized candidate table to the console.
It reads NO real data, fetches NOTHING, connects to NO exchange/broker, runs NO optimization,
promotes NOTHING, and advances NOTHING -- it only prints the frozen/known-state arena built by
the contract. Deterministic.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_candidate_arena_v1_contract as _arena  # noqa: E402


def main() -> int:
    rec = _arena.build_candidate_arena()
    assert _arena.validate_candidate_arena(rec)["valid"], "arena_failed_validation"
    print("=" * 100)
    print("SPARTA CANDIDATE ARENA v1 (READ-ONLY) -- as-of %s" % rec["as_of"])
    print("  normalized scores 0-5 (5=best on axis) | MISSING_EVIDENCE = not measured | N/A = "
          "axis n/a | promotes/ranks NOTHING")
    print("=" * 100)
    hdr = ("%-18s %-10s %-9s %-7s %-7s %-7s %-7s %-7s"
           % ("candidate", "status", "evid", "ret", "ddown", "bench", "cost", "corr"))
    print(hdr)
    print("-" * 100)
    for r in rec["rows"]:
        def s(x):
            return str(x)[:7] if x not in (_arena.MISSING, _arena.NA) else (
                "MISS" if x == _arena.MISSING else "N/A")
        print("%-18s %-10s %-9s %-7s %-7s %-7s %-7s %-7s" % (
            r["candidate_id"][:18], r["current_status"][:10],
            r["evidence_status"][:9], s(r["return_engine_score"]), s(r["drawdown_score"]),
            s(r["benchmark_score"]), s(r["cost_sensitivity_score"]),
            s(r["correlation_or_diversifier_score"])))
    print("-" * 100)
    print("BLOCKERS / NEXT SAFE ACTION:")
    for r in rec["rows"]:
        print("  [%s] %s" % (r["candidate_id"], r["blocker_reason"]))
        print("      -> %s" % r["next_safe_action"])
    print("-" * 100)
    print("ready_for_promotion: %s | ready_for_human_review: %s | missing_evidence_cells: %d"
          % (rec["anything_ready_for_promotion"], rec["anything_ready_for_human_review"],
             rec["missing_evidence_cells"]))
    for n in rec["review_notes"]:
        print("  note: %s" % n)
    print()
    print(json.dumps({"as_of": rec["as_of"], "row_count": rec["row_count"],
                      "c22_is_hold": rec["c22_is_hold"],
                      "c23_c24_blocked_by_broad_universe": rec["c23_c24_blocked_by_broad_universe"],
                      "vrp_phase1_promising_not_promoted": rec["vrp_phase1_promising_not_promoted"],
                      "vrp_phase2_not_backtest_evidence": rec["vrp_phase2_not_backtest_evidence"],
                      "anything_ready_for_promotion": rec["anything_ready_for_promotion"]},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
