"""Candidate #22 -- FEE-HONEST REPLAY: FAIL-CLOSED PRECONDITION SHELL (RESEARCH ONLY).

This runner does NOT compute a fee-honest result. It enumerates, per required instrument of the
FROZEN 88-signal V2 cohort, the historical execution evidence the frozen B2/B3 hierarchy demands,
checks which admitted evidence exists on disk, checks every lifecycle-gate precondition, and
refuses to run unless ALL preconditions hold AND the exact advance token is supplied. It
follows the existing B2/B3 evidence categories and source tiers; it invents no instrument model,
assumes nothing about historical availability from present-day availability, and never fetches.

Evidence admission layout (from Phase B3, still not created unless a human authorizes acquisition):
  data/c22_short_instrument_evidence/manifests/<venue>__<asset>__evidence_manifest.json
Each manifest must carry: canonical_asset_identity, historical_execution_instrument, venue,
instrument_existence_on_required_dates, historical_shortability_mechanism (shorts),
historical_ohlc_coverage, fee_schedule, funding_or_borrow_requirement (shorts),
minimum_quantity_or_notional, tick_lot_constraints, liquidity_spread_evidence, each with a
source_tier (T1..T5; T5 never decisive) and sha256 sidecar references, plus an admission token.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_replay_cost_engine_contract as C  # noqa: E402
import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3  # noqa: E402
import sparta_commander.c22_short_instrument_evidence_request_contract as B2  # noqa: E402
import tools.c22_replay_dry_run_once as DR  # noqa: E402

ADVANCE_TOKEN = "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT=ADVANCE"
APPROVALS_DIR = REPO_ROOT / "reports" / "approvals"
EVIDENCE_ROOT = REPO_ROOT / B3.PROPOSED_EVIDENCE_ROOT
MANIFEST_DIR = EVIDENCE_ROOT / "manifests"
COST_BASE_CASE_DIR = REPO_ROOT / "reports" / "c22_gc_execution_cost_base_case"
DRY_RUN_REPORT = REPO_ROOT / "reports" / "c22_gc_replay_dry_run" / "c22_replay_dry_run_no_pnl.json"

COST_COMPONENTS = C.COST_COMPONENTS
RESULT_LEVELS = C.RESULT_LEVELS
SENSITIVITY_37BPS = C.SENSITIVITY_37BPS_STATUS
DECISIVE_MIN_TIER = B3.DECISIVE_MIN_TIER
SOURCE_TIERS = tuple(B3.SOURCE_HIERARCHY)

EVIDENCE_FIELDS_ALL = ("canonical_asset_identity", "historical_execution_instrument", "venue",
                       "instrument_existence_on_required_dates", "historical_ohlc_coverage", "fee_schedule",
                       "minimum_quantity_or_notional", "tick_lot_constraints", "liquidity_spread_evidence")
EVIDENCE_FIELDS_SHORT_ONLY = ("historical_shortability_mechanism", "funding_or_borrow_requirement")

GATE_TOKENS = {
    "replay_spec_accepted": "HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=ACCEPT",
    "forward_exit_contract_accepted": "HUMAN_DECISION_C22_FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE=ACCEPT",
    "execution_data_contract_accepted": "HUMAN_DECISION_C22_EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE=ACCEPT",
    "dry_run_accepted": "HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT=ACCEPT",
    "short_instrument_selected": "HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT",
    "cost_base_case_frozen": "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE=ACCEPT",
    "weekend_session_rule_ruled": "HUMAN_DECISION_C22_WEEKEND_SESSION_RULE",
    "basis_alignment_reviewed": "HUMAN_DECISION_C22_BASIS_ALIGNMENT_REVIEWED",
    "historical_evidence_admitted": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT=ADMIT",
}


def _approval_records() -> list:
    """Read-only scan of reports/approvals/*.json for exact token strings."""
    found = []
    if not APPROVALS_DIR.is_dir():
        return found
    for p in sorted(APPROVALS_DIR.glob("*.json")):
        try:
            found.append(p.read_text(encoding="utf-8"))
        except OSError:
            continue
    return found


def token_recorded(token: str, blobs=None) -> bool:
    blobs = _approval_records() if blobs is None else blobs
    return any(token in b for b in blobs)


def required_instruments() -> list:
    sigs, _ = DR.load_frozen_v2_signals()
    return DR.instrument_feasibility_requirements(sigs)["instruments"]


def _manifest_path(symbol: str) -> Path:
    ps = B2.parse_symbol(symbol)
    return MANIFEST_DIR / ("%s__%s__evidence_manifest.json" % (ps.get("venue"), ps.get("base") or symbol.replace(":", "_")))


def evaluate_instrument_evidence(inst: dict) -> dict:
    """Fail closed per instrument: every required field must be present with a decisive source
    tier (>= T3) in an admitted manifest; present-day availability is never accepted as proof."""
    needs_short = "SHORT" in inst["sides"]
    fields = list(EVIDENCE_FIELDS_ALL) + (list(EVIDENCE_FIELDS_SHORT_ONLY) if needs_short else [])
    path = _manifest_path(inst["symbol"])
    status = {"symbol": inst["symbol"], "sides": inst["sides"],
              "manifest": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path).replace("\\", "/"),
              "manifest_present": path.exists(), "fields": {}, "missing": [], "non_decisive_tier": [],
              "present_day_only_rejected": [], "satisfied": False}
    manifest = None
    if path.exists():
        try:
            manifest = json.loads(path.read_bytes().decode("utf-8"))
        except (OSError, ValueError):
            manifest = None
    for f in fields:
        ev = (manifest or {}).get(f)
        if not isinstance(ev, dict):
            status["fields"][f] = "MISSING"
            status["missing"].append(f)
            continue
        tier = ev.get("source_tier")
        if ev.get("evidence_basis") == "PRESENT_DAY_AVAILABILITY":
            status["fields"][f] = "REJECTED_PRESENT_DAY_ONLY"
            status["present_day_only_rejected"].append(f)
            continue
        if tier not in SOURCE_TIERS or SOURCE_TIERS.index(tier) > SOURCE_TIERS.index(DECISIVE_MIN_TIER):
            status["fields"][f] = "NON_DECISIVE_TIER:%s" % tier
            status["non_decisive_tier"].append(f)
            continue
        if not ev.get("sha256"):
            status["fields"][f] = "MISSING_SHA256"
            status["missing"].append(f)
            continue
        status["fields"][f] = "OK:%s" % tier
    status["satisfied"] = (manifest is not None and not status["missing"] and not status["non_decisive_tier"]
                           and not status["present_day_only_rejected"]
                           and manifest.get("admission_token") == GATE_TOKENS["historical_evidence_admitted"])
    return status


def check_preconditions() -> dict:
    blobs = _approval_records()
    p = {k: token_recorded(v, blobs) for k, v in GATE_TOKENS.items()}
    p["dry_run_report_present"] = DRY_RUN_REPORT.exists()
    p["cost_base_case_frozen"] = p["cost_base_case_frozen"] and COST_BASE_CASE_DIR.is_dir() and any(COST_BASE_CASE_DIR.glob("*.json"))
    p["evidence_layout_exists"] = MANIFEST_DIR.is_dir()
    inst = required_instruments()
    ev = [evaluate_instrument_evidence(i) for i in inst]
    p["instruments_required"] = len(inst)
    p["instruments_with_admitted_evidence"] = sum(1 for e in ev if e["satisfied"])
    p["all_required_instruments_evidenced"] = all(e["satisfied"] for e in ev) if ev else False
    p["short_instruments_required"] = sum(1 for i in inst if "SHORT" in i["sides"])
    p["short_instruments_evidenced"] = sum(1 for i, e in zip(inst, ev) if "SHORT" in i["sides"] and e["satisfied"])
    gates = ["replay_spec_accepted", "forward_exit_contract_accepted", "execution_data_contract_accepted",
             "dry_run_accepted", "dry_run_report_present", "short_instrument_selected", "cost_base_case_frozen",
             "weekend_session_rule_ruled", "basis_alignment_reviewed", "historical_evidence_admitted",
             "all_required_instruments_evidenced"]
    p["unsatisfied"] = [g for g in gates if not p[g]]
    p["all_satisfied"] = not p["unsatisfied"]
    p["instrument_evidence"] = ev
    p["fee_honest_replayable_trades_now"] = 0 if not p["all_satisfied"] else None
    p["sensitivity_37bps_status"] = SENSITIVITY_37BPS
    p["frozen_cost_base_case"] = C.frozen_base_case()
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--advance-token", default=os.environ.get("C22_REPLAY_ADVANCE_TOKEN"))
    a = ap.parse_args(argv)
    p = check_preconditions()
    summary = {"preconditions_all_satisfied": p["all_satisfied"], "unsatisfied": p["unsatisfied"],
               "instruments_required": p["instruments_required"],
               "instruments_with_admitted_evidence": p["instruments_with_admitted_evidence"],
               "short_instruments_required": p["short_instruments_required"],
               "short_instruments_evidenced": p["short_instruments_evidenced"],
               "fee_honest_replayable_trades_now": p["fee_honest_replayable_trades_now"],
               "cost_base_case": p["frozen_cost_base_case"]["status"],
               "sensitivity_37bps": p["sensitivity_37bps_status"],
               "advance_token_supplied": bool(a.advance_token), "advance_token_exact": a.advance_token == ADVANCE_TOKEN,
               "result": "REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED"}
    if p["all_satisfied"] and a.advance_token == ADVANCE_TOKEN:
        summary["result"] = "REPLAY_PRECONDITIONS_SATISFIED_BUT_PNL_BODY_NOT_IMPLEMENTED_IN_THIS_SHELL"
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
