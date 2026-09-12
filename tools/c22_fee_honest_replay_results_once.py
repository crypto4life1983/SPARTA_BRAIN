"""Candidate #22 -- FEE-HONEST REPLAY RESULTS (research computation over sealed inputs; ONE RUN).

Thin driver: re-checks every precondition through the fail-closed shell
(tools/c22_fee_honest_replay_once.py), requires the recorded advance decision, and then computes
the decisive research replay plus labelled sensitivities and benchmarks from the SEALED
pre-registration. Writes one sealed results file per invocation (never overwrites). Places no
orders, touches no exchange account, changes no strategy rule, modifies no frozen artifact.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.c22_fee_honest_replay_once as FH  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compute", action="store_true", help="compute the research results (otherwise only the precondition check is printed)")
    a = ap.parse_args(argv)
    p = FH.check_preconditions()
    advance_recorded = FH.token_recorded(FH.ADVANCE_TOKEN)
    out = {"preconditions_all_satisfied": p["all_satisfied"], "unsatisfied": p["unsatisfied"],
           "instruments_with_admitted_evidence": p["instruments_with_admitted_evidence"], "instruments_required": p["instruments_required"],
           "advance_decision_recorded": advance_recorded, "computed": False}
    if p["all_satisfied"] and advance_recorded and a.compute:
        pre, inputs, ppath, psha = FH.latest_prereg()
        res = FH.run_fee_honest_replay(pre, inputs, ppath, psha)
        w = FH._write_results(res)
        out.update({"computed": True, "decisive_conclusion": res["decisive_conclusion"], "decisive_lifecycle_counts": res["decisive"]["lifecycle_counts"],
                    "decisive_metrics": res["decisive"]["metrics"], "decisive_totals": res["decisive"]["attribution"]["totals"],
                    "open_at_end_of_data": res["decisive"]["open_at_end_of_data"], "gates": res["gates"], **w})
    elif not a.compute:
        out["note"] = "precondition check only; pass --compute to produce the sealed research results"
    print(json.dumps(out, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
