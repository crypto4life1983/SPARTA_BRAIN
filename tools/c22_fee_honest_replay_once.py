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
COST_BASE_CASE_FIELDS = ("fee_schedule", "minimum_quantity_or_notional", "tick_lot_constraints", "liquidity_spread_evidence")
PREREG_DIR = REPO_ROOT / "reports" / "c22_gc_governance"
DECISIVE_INPUTS_DIR = EVIDENCE_ROOT / "decisive_inputs"
RESULTS_DIR = REPO_ROOT / "reports" / "c22_gc_fee_honest_replay"

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


GOVERNANCE_EXCLUSIONS = {
    # asset -> (excluded sides, recorded basis). Terminal exclusions from SEALED artifacts: these
    # signals can never trade, so requiring admitted execution evidence for them is incoherent.
    # They are still reported, never silently dropped, and the gate keeps failing closed for
    # every instrument the decisive cohort CAN trade.
    "BYBIT:TELUSDT": ({"SHORT"}, "Stage One FAIL_WRONG_INSTRUMENT_TYPE: no Bybit linear perpetual exists and spot margin is 'none'; elimination preserved"),
    "COINBASE:MORPHOUSD": ({"SHORT"}, "Stage Two governance closure: EXCLUDED_VENUE_POLICY under HOME_VENUE_ONLY (short needs Coinbase International, a substituted platform)"),
}


def required_instruments() -> list:
    """Instruments the decisive cohort can actually trade. Governance-excluded sides are dropped
    from the requirement and returned separately so nothing disappears silently."""
    sigs, _ = DR.load_frozen_v2_signals()
    allq = DR.instrument_feasibility_requirements(sigs)["instruments"]
    out = []
    for i in allq:
        ex = GOVERNANCE_EXCLUSIONS.get(i["symbol"])
        if not ex:
            out.append(i)
            continue
        keep = [s for s in i["sides"] if s not in ex[0]]
        if keep:
            out.append(dict(i, sides=keep))
    return out


def excluded_instruments() -> list:
    sigs, _ = DR.load_frozen_v2_signals()
    allq = DR.instrument_feasibility_requirements(sigs)["instruments"]
    out = []
    for i in allq:
        ex = GOVERNANCE_EXCLUSIONS.get(i["symbol"])
        if ex:
            out.append({"symbol": i["symbol"], "excluded_sides": sorted(ex[0]), "basis": ex[1],
                        "remaining_sides": [s for s in i["sides"] if s not in ex[0]]})
    return out


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
    cost_gate_recorded = token_recorded(GATE_TOKENS["cost_base_case_frozen"])
    for f in fields:
        ev = (manifest or {}).get(f)
        if not isinstance(ev, dict):
            status["fields"][f] = "MISSING"
            status["missing"].append(f)
            continue
        tier = ev.get("source_tier")
        if ev.get("evidence_basis") == "FROZEN_COST_BASE_CASE" and f in COST_BASE_CASE_FIELDS:
            # B1 assigns fee / constraint / spread base-case values to the human-frozen cost gate, never to B3 evidence
            if cost_gate_recorded and (manifest or {}).get("cost_base_case_token") == GATE_TOKENS["cost_base_case_frozen"]:
                status["fields"][f] = "OK:FROZEN_COST_BASE_CASE"
            else:
                status["fields"][f] = "COST_BASE_CASE_NOT_FROZEN"
                status["missing"].append(f)
            continue
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
    p["cost_base_case_frozen"] = p["cost_base_case_frozen"] and bool(sorted(PREREG_DIR.glob("c22_decisive_replay_preregistration_*.json")))
    p["evidence_layout_exists"] = MANIFEST_DIR.is_dir()
    inst = required_instruments()
    ev = [evaluate_instrument_evidence(i) for i in inst]
    p["instruments_required"] = len(inst)
    p["instruments_with_admitted_evidence"] = sum(1 for e in ev if e["satisfied"])
    p["all_required_instruments_evidenced"] = all(e["satisfied"] for e in ev) if ev else False
    p["short_instruments_required"] = sum(1 for i in inst if "SHORT" in i["sides"])
    p["short_instruments_evidenced"] = sum(1 for i, e in zip(inst, ev) if "SHORT" in i["sides"] and e["satisfied"])
    p["governance_excluded_instruments"] = excluded_instruments()
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


def latest_prereg() -> tuple:
    files = sorted(PREREG_DIR.glob("c22_decisive_replay_preregistration_*.json"))
    if not files:
        raise RuntimeError("no_preregistration")
    p = files[-1]
    raw = p.read_bytes()
    side = p.with_suffix(".json.sha256")
    if side.exists() and side.read_text().strip() != hashlib.sha256(raw).hexdigest():
        raise RuntimeError("preregistration_sha_mismatch")
    pre = json.loads(raw.decode("utf-8"))
    ip = DECISIVE_INPUTS_DIR / ("c22_decisive_inputs_%s.json" % pre["run_id"])
    inputs = json.loads(ip.read_bytes().decode("utf-8"))
    if inputs["prereg_sha256"] != pre["prereg_sha256"]:
        raise RuntimeError("decisive_inputs_do_not_match_preregistration")
    return pre, inputs, str(p.relative_to(REPO_ROOT)).replace("\\", "/"), hashlib.sha256(raw).hexdigest()


def load_stage3_short_ohlc(pre: dict) -> dict:
    """{asset: {date: row}} from the Stage Three canonical OHLC files for the short instruments."""
    import tools.c22_b3_stage3_historical_ohlc_once as S3
    out = {}
    for key, c in pre["cost_base_case"]["constraints"].items():
        if not key.startswith("SHORT|"):
            continue
        asset = key.split("|", 1)[1]
        base = asset.split(":")[1]
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        files = sorted((S3.OHLC_DIR / base).glob("%s__%s__historical_ohlc__*.json" % (c["venue"], base)))
        if not files:
            continue
        payload = json.loads(files[-1].read_bytes().decode("utf-8"))
        out[asset] = {r["date"]: r for r in payload["rows"]}
    return out


def run_fee_honest_replay(pre: dict, inputs: dict, prereg_path: str, prereg_file_sha: str) -> dict:
    import sparta_commander.c22_fee_honest_replay_engine_contract as FE
    import sparta_commander.c22_replay_lifecycle_engine_contract as E
    signals, v2_sha = DR.load_frozen_v2_signals()
    index = E.load_session_index(DR.DATA_DIR)
    short_ohlc = load_stage3_short_ohlc(pre)
    nav = pre["decisions"]["nav_usd"]["value"]
    dec_profile, sens_profile = pre["decisions"]["session_profile_decisive"], pre["decisions"]["session_profile_sensitivity"]
    base_hooks = FE.build_execution(pre, inputs, short_ohlc, use_venue_prices=True)
    decisive = FE.run_variant(index, signals, dec_profile, base_hooks, nav, "DECISIVE_V2_EXACT_VENUE_PRICES_FROZEN_BASE_CASE", "DECISIVE")
    export_basis = FE.run_variant(index, signals, dec_profile, FE.build_execution(pre, inputs, short_ohlc, use_venue_prices=False), nav, "SENSITIVITY_EXPORT_PRICE_BASIS", "SENSITIVITY")
    sens = [export_basis,
            FE.run_variant(index, signals, sens_profile, base_hooks, nav, "SENSITIVITY_CRYPTO_CALENDAR_PROFILE", "SENSITIVITY"),
            FE.run_variant(index, signals, dec_profile, base_hooks, 100_000.0, "SENSITIVITY_NAV_100K", "SENSITIVITY"),
            FE.run_variant(index, signals, dec_profile, FE.build_execution(pre, inputs, short_ohlc, True, fee_override_bps=13.5, slippage_override_bps=5.0), nav, "SENSITIVITY_37BPS_ROUND_TRIP_CONVENTION", "SENSITIVITY"),
            FE.run_variant(index, signals, dec_profile, FE.build_execution(pre, inputs, short_ohlc, True, spot_fee_override_bps=10.0), nav, "SENSITIVITY_SPOT_LOW_OBSERVED_FEE_10BPS", "SENSITIVITY")]
    sessions = E.expected_sessions(min(index), max(index), dec_profile)
    btc = FE.btc_buy_and_hold(index, [s for s in sessions if s in index], pre, nav)
    executed = FE.executed_trades_for_matching(decisive)
    nb = pre["benchmarks"]["matched_random_entry_null"]
    null = FE.matched_random_null(index, executed, pre, nav, nb["seed"], nb["resamples"], dec_profile)
    g = FE.gates(decisive, null, btc, export_basis)
    strip = lambda v: {k: x for k, x in v.items() if k not in ("records", "nav_series")}
    return {"report": "c22_fee_honest_replay_results", "engine_version": FE.ENGINE_VERSION,
            "preregistration": {"path": prereg_path, "file_sha256": prereg_file_sha, "prereg_sha256": pre["prereg_sha256"]},
            "v2_artifact_sha256": v2_sha, "signals_in": len(signals), "data_boundary": max(index), "starting_nav_usd": nav,
            "decisive": strip(decisive), "decisive_nav_series": decisive["nav_series"],
            "decisive_records": [{k: v for k, v in r.items() if k not in ("entry_fill", "exit_fill")} for r in decisive["records"]],
            "sensitivities": [strip(v) for v in sens],
            "benchmarks": {"btc_buy_and_hold": btc, "zero_return_flat": {"total_return": 0.0}, "signal_off_control": {"trades": 0, "total_return": 0.0}, "matched_random_entry_null": null},
            "gates": g, "power_warning": pre["rejection_gates"]["power_warning"], "assumption_register": pre["assumption_register"],
            "decisive_conclusion": g["verdict"], "strategy_rules_modified": False, "v2_modified": False, "one_run_only": True}


def _write_results(res: dict) -> dict:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = RESULTS_DIR / ("c22_fee_honest_replay_results_%s.json" % run_id)
    if p.exists():
        raise RuntimeError("refuse_overwrite")
    blob = json.dumps(dict(res, run_id=run_id), indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    p.write_bytes(blob)
    p.with_suffix(".json.sha256").write_text(hashlib.sha256(blob).hexdigest() + "\n", encoding="utf-8")
    return {"results_json": str(p.relative_to(REPO_ROOT)).replace("\\", "/"), "results_sha256": hashlib.sha256(blob).hexdigest(), "run_id": run_id}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--advance-token", default=os.environ.get("C22_REPLAY_ADVANCE_TOKEN"))
    ap.add_argument("--execute-replay", action="store_true")
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
