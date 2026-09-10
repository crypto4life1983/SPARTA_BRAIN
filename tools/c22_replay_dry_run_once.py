"""Candidate #22 -- NO-P&L DETERMINISTIC REPLAY DRY RUN (RESEARCH ONLY; READ-ONLY by default).

Runs the FROZEN V2 cohort (exactly the 88 actionable V2 signals, SHA-pinned) through the pure
ledger + lifecycle engine over the admitted Signum export collection, with P&L DISABLED, under
BOTH session profiles (V2_CONTRACT_EXACT and CRYPTO_CALENDAR_SENSITIVITY), and reports every
lifecycle outcome, the full 88-signal reconciliation, the weekend-profile differences, the exact
external execution evidence still missing, and the END-OF-DATA state. Computes no performance
number. Selects no profile. Issues no token.

Writing the report requires --execute-build plus the exact token
HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL (or env C22_DRY_RUN_TOKEN). Never overwrites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import date as _date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_replay_lifecycle_engine_contract as E  # noqa: E402
import sparta_commander.c22_replay_cost_engine_contract as C  # noqa: E402
import sparta_commander.c22_forward_exit_data_readiness_contract as FED  # noqa: E402
import sparta_commander.c22_short_instrument_evidence_request_contract as B2  # noqa: E402
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as _v2run  # noqa: E402

DATA_DIR = REPO_ROOT / _trk.DATA_DIR
V2_ARTIFACT = _v2run.OUT_DIR / _v2run._v2.v2_artifact_filename(_v2run.RUN_START, _v2run.RUN_END, _v2run.RUN_EXPECTED_WINDOWS)
V2_FROZEN_SHA256 = "b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8"
V2_FROZEN_ACTIONABLE = 88
ENTRY_CUTOFF = _v2run.RUN_END                                  # 2026-07-15
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_replay_dry_run"
REPORT_BASENAME = "c22_replay_dry_run_no_pnl"
BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL"
ACTIONABLE = ("LONG_ENTRY", "BEAR_SHORT", "HEDGE_SHORT")
SPEC_STATUS = "PHASE_A_REV1_SECOND_REVIEW_NOT_RECORDED"       # no ACCEPT token exists on disk
STARTING_NAV = 100_000.0                                        # unitless research NAV; P&L disabled


def authorize_write(execute_build, token):
    if not execute_build:
        return {"authorized": False, "reason": "execute_build_not_requested"}
    if not token:
        return {"authorized": False, "reason": "missing_dry_run_token"}
    if token != BUILD_TOKEN:
        return {"authorized": False, "reason": "wrong_dry_run_token"}
    return {"authorized": True, "reason": "option_plus_exact_dry_run_token"}


def load_frozen_v2_signals(path: Path = V2_ARTIFACT) -> tuple:
    """SHA-pin BEFORE read; returns (signals, sha256). Fails closed on any drift."""
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != V2_FROZEN_SHA256:
        raise RuntimeError("v2_artifact_sha_mismatch:%s" % sha)
    art = json.loads(raw.decode("utf-8"))
    sigs = [{"symbol": l["symbol"], "decision_date": l["source_date"], "signal": l["signal"],
             "market_rank": l["market_rank_raw"], "source_sha256": l["source_sha256"]}
            for l in art["labels"] if l["signal"] in ACTIONABLE]
    if len(sigs) != V2_FROZEN_ACTIONABLE:
        raise RuntimeError("v2_actionable_count_%d_ne_88" % len(sigs))
    if any(s["decision_date"] > ENTRY_CUTOFF for s in sigs):
        raise RuntimeError("v2_signal_after_entry_cutoff")
    return sigs, sha


def reconciliation(run: dict, signals: list) -> dict:
    recs = run["records"]
    ids_in = [E.signal_id(s) for s in signals]
    ids_out = [r["signal_id"] for r in recs]
    counts = run["lifecycle_counts"]
    return {
        "source_signals": len(ids_in), "records": len(ids_out),
        "every_signal_has_exactly_one_record": sorted(ids_in) == sorted(ids_out) and len(set(ids_out)) == len(ids_out),
        "lifecycle_counts": counts, "lifecycle_total": sum(counts.values()),
        "no_silent_drops": sum(counts.values()) == len(ids_in) and run["reconciles_to_input"],
        "accepted_entry_candidates": [r["signal_id"] for r in recs if r["entry_date"]],
        "rejected_candidates": [{"signal_id": r["signal_id"], "reason": r["reject_reason"]} for r in recs if r["lifecycle_status"] in ("REJECTED", "INSTRUMENT_UNVERIFIED")],
        "unresolved_entries": [{"signal_id": r["signal_id"], "status": r["lifecycle_status"], "fill": r["entry_fill"]} for r in recs if r["lifecycle_status"] in ("PENDING_ENTRY", "DATA_GAP", "MISSING_EXECUTION_PRICE")],
        "positions_reaching_exit_condition": [{"signal_id": r["signal_id"], "on": r["exit_condition_date"], "reason": r["exit_reason"], "filled": r["exit_date"] is not None} for r in recs if r["exit_condition_date"]],
        "positions_requiring_external_ohlc": [{"signal_id": r["signal_id"], "why": (r["exit_fill"] or r["entry_fill"] or {}).get("status"), "exit_reason": r["exit_reason"]} for r in recs if r["requires_external_ohlc"]],
        "positions_crossing_missing_data_dates": [{"signal_id": r["signal_id"], "dates": r["crossed_data_gap_dates"]} for r in recs if r["crossed_data_gap_dates"]],
        "positions_open_at_end_of_data": [{"signal_id": r["signal_id"], "entry_date": r["entry_date"], "exit_condition_met": r["exit_condition_date"], "mark_to_market": r["mark_to_market"]} for r in recs if r["lifecycle_status"] == "OPEN_AT_END_OF_DATA"],
        "instrument_unverified_records": sum(1 for r in recs if r["instrument_status"] == "UNVERIFIED"),
        "weekend_decision_dates": sum(1 for r in recs if _date.fromisoformat(r["decision_date"]).weekday() >= 5),
    }


def instrument_feasibility_requirements(signals: list) -> dict:
    """Per required instrument (from the frozen cohort), the evidence fields still missing.
    Follows the B2/B3 hierarchy; invents no instrument model."""
    req = {}
    for s in signals:
        sym = s["symbol"]
        r = req.setdefault(sym, {"symbol": sym, "parsed": B2.parse_symbol(sym), "mapping_risk": B2.mapping_risk_class(sym),
                                 "sides": set(), "signals": 0, "first": s["decision_date"], "last": s["decision_date"]})
        r["sides"].add("SHORT" if s["signal"] in B2.SHORT_SIGNALS else "LONG")
        r["signals"] += 1
        r["first"], r["last"] = min(r["first"], s["decision_date"]), max(r["last"], s["decision_date"])
    out = []
    for sym in sorted(req):
        r = req[sym]
        needs_short = "SHORT" in r["sides"]
        out.append({
            "symbol": sym, "venue": r["parsed"].get("venue"), "base": r["parsed"].get("base"),
            "mapping_risk": r["mapping_risk"], "sides": sorted(r["sides"]), "signals": r["signals"],
            "required_from": r["first"], "required_through": "until_natural_exit_or_end_of_data",
            "evidence_required": {
                "canonical_asset_identity": "MISSING", "historical_execution_instrument": "MISSING",
                "venue": r["parsed"].get("venue") or "MISSING", "instrument_existence_on_required_dates": "MISSING",
                "historical_shortability_mechanism": ("MISSING" if needs_short else "N/A_LONG_ONLY"),
                "historical_ohlc_coverage": "MISSING", "fee_schedule": "MISSING",
                "funding_or_borrow_requirement": ("MISSING" if needs_short else "N/A_LONG_ONLY"),
                "minimum_quantity_or_notional": "MISSING", "tick_lot_constraints": "MISSING",
                "liquidity_spread_evidence": "MISSING",
            },
            "local_partial_funding": (sym in B2.PARTIAL_FUNDING_BINANCE),
            "fail_closed": True,
        })
    return {"instruments": out, "count": len(out),
            "short_instruments": sum(1 for x in out if "SHORT" in x["sides"]),
            "long_instruments": sum(1 for x in out if "LONG" in x["sides"]),
            "perp_required_evidence_fields": list(B2.PERP_REQUIRED_EVIDENCE),
            "margin_required_evidence_fields": list(B2.MARGIN_REQUIRED_EVIDENCE),
            "acquisition_status": B2.ACQUISITION_STATUS}


def forward_coverage(index: dict) -> dict:
    last = max(index)
    exp = FED.expected_export_sessions(FED.FIRST_EXIT_ONLY_DATE, last)
    cov = FED.readiness_from_coverage(exp, set(index) & set(exp))
    n, rng = 0, FED.initial_exit_data_range()
    while rng["end"] < last:
        n += 1
        rng = FED.extension_range(n)
    return {"first_exit_only_date": FED.FIRST_EXIT_ONLY_DATE, "last_admitted_export": last,
            "expected_weekday_sessions": len(exp), "missing_sessions": cov["missing_sessions"],
            "readiness": cov["readiness"], "extension_index_reached": n, "extension_range": rng}


def build_dry_run() -> dict:
    signals, v2_sha = load_frozen_v2_signals()
    index = E.load_session_index(DATA_DIR)
    runs, recon = {}, {}
    for prof in E.PROFILES:
        runs[prof] = E.run_lifecycle(index, signals, prof, instrument_registry={}, cost_model=C.ZERO_COST_MODEL,
                                     starting_nav=STARTING_NAV, pnl_enabled=False, enforce_instrument_verification=False)
        recon[prof] = reconciliation(runs[prof], signals)
    diff = E.diff_profiles(runs[E.PROFILE_V2_CONTRACT_EXACT], runs[E.PROFILE_CRYPTO_CALENDAR])
    feas = instrument_feasibility_requirements(signals)
    missing_external = {
        "short_instrument_evidence_for": sorted({s["symbol"] for s in signals if s["signal"] in B2.SHORT_SIGNALS}),
        "long_execution_venue_evidence_for": sorted({s["symbol"] for s in signals if s["signal"] == "LONG_ENTRY"}),
        "external_ohlc_for_out_of_radar_or_missing_price": {p: recon[p]["positions_requiring_external_ohlc"] for p in E.PROFILES},
        "cost_base_case": C.frozen_base_case(),
        "basis_alignment_status": B2.BASIS_STATUS,
        "local_funding_coverage_end": B2.PARTIAL_FUNDING_LOCAL_END,
        "local_borrow_status": B2.BORROW_LOCAL_STATUS_ALL,
    }
    return {
        "report": REPORT_BASENAME, "mode": "RESEARCH_ONLY_NO_PNL_DRY_RUN", "engine_version": E.ENGINE_VERSION,
        "fill_convention": E.FILL_CONVENTION, "spec_status": SPEC_STATUS, "entry_cutoff": ENTRY_CUTOFF,
        "v2_artifact_sha256": v2_sha, "v2_actionable_signals": len(signals), "starting_nav_unitless": STARTING_NAV,
        "cost_model": C.ZERO_COST_MODEL["model_id"], "performance_computed": False,
        "data_boundary_last_admitted_export": max(index), "admitted_exports": len(index),
        "forward_coverage_frozen_b1_rule": forward_coverage(index),
        "profiles": {p: {"role": E.PROFILE_ROLE[p], "sessions_expected": runs[p]["sessions_expected"],
                         "data_gap_sessions": runs[p]["data_gap_sessions"], "lifecycle_counts": runs[p]["lifecycle_counts"],
                         "ledger_snapshot": runs[p]["ledger_snapshot"], "ledger_validation": runs[p]["ledger_validation"],
                         "performance_conclusion": runs[p]["performance_conclusion"], "reconciliation": recon[p],
                         "records": runs[p]["records"]} for p in E.PROFILES},
        "weekend_profile_differences": diff,
        "instrument_feasibility_requirements": feas,
        "missing_external_evidence": missing_external,
        "fee_honest_replayable_now": 0,
        "fee_honest_blocked_reason": "NO_INSTRUMENT_EVIDENCE_ADMITTED_AND_NO_FROZEN_COST_BASE_CASE",
        "decisive_replay_can_run": False,
        "token_issued": False, "replay_authorized": False, "profile_selected": None, "human_review_required": True,
    }


def canonical_bytes(r: dict) -> bytes:
    return json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"


def render_markdown(r: dict) -> str:
    L = ["# C22 Replay Dry Run — NO P&L (frozen V2 cohort, both session profiles)", "",
         "Research only. Performance not computed. No profile selected. Issues no token.", "",
         "- V2 artifact sha256: `%s` · actionable signals: %d · entry cutoff %s" % (r["v2_artifact_sha256"], r["v2_actionable_signals"], r["entry_cutoff"]),
         "- Fill convention: %s" % r["fill_convention"],
         "- Data boundary (last admitted export): %s · admitted exports: %d" % (r["data_boundary_last_admitted_export"], r["admitted_exports"]),
         "- Forward coverage (frozen B1 weekday rule): %s · missing: %s · extension #%d" % (
             r["forward_coverage_frozen_b1_rule"]["readiness"], r["forward_coverage_frozen_b1_rule"]["missing_sessions"] or "none",
             r["forward_coverage_frozen_b1_rule"]["extension_index_reached"]),
         "- Spec status: %s" % r["spec_status"], ""]
    for p, pr in r["profiles"].items():
        rc = pr["reconciliation"]
        L += ["## Profile %s (%s)" % (p, pr["role"]), "",
              "- Sessions: %d · data-gap sessions: %s" % (pr["sessions_expected"], pr["data_gap_sessions"] or "none"),
              "- Lifecycle counts: %s" % json.dumps(pr["lifecycle_counts"], sort_keys=True),
              "- Reconciliation: %d signals -> %d records · one record each: %s · no silent drops: %s" % (
                  rc["source_signals"], rc["records"], rc["every_signal_has_exactly_one_record"], rc["no_silent_drops"]),
              "- Accepted entries: %d · rejected: %d · unresolved entries: %d · exit condition reached: %d" % (
                  len(rc["accepted_entry_candidates"]), len(rc["rejected_candidates"]), len(rc["unresolved_entries"]), len(rc["positions_reaching_exit_condition"])),
              "- Requiring external OHLC: %d · crossing missing-data dates: %d · open at end of data: %d" % (
                  len(rc["positions_requiring_external_ohlc"]), len(rc["positions_crossing_missing_data_dates"]), len(rc["positions_open_at_end_of_data"])),
              "- Instrument UNVERIFIED records: %d of %d · weekend decision dates: %d" % (rc["instrument_unverified_records"], rc["source_signals"], rc["weekend_decision_dates"]),
              "- Ledger (P&L disabled): %s · valid: %s" % (json.dumps({k: pr["ledger_snapshot"][k] for k in ("nav", "cash", "realized_pnl", "gross_exposure_pct_nav", "open_positions", "closed_positions", "rejected_orders")}, sort_keys=True), pr["ledger_validation"]["valid"]),
              "- Performance conclusion: %s" % pr["performance_conclusion"], "",
              "| signal_id | size% | status | entry | exit cond | reason | exit | instr | notes |", "|---|---|---|---|---|---|---|---|---|"]
        for x in pr["records"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                x["signal_id"], x["size_pct_nav"], x["lifecycle_status"], x["entry_date"] or "", x["exit_condition_date"] or "",
                x["exit_reason"] or x["reject_reason"] or "", x["exit_date"] or "", x["instrument_status"], "; ".join(x["notes"])[:80]))
        L.append("")
    d = r["weekend_profile_differences"]
    L += ["## Weekend-profile differences (V2_CONTRACT_EXACT vs CRYPTO_CALENDAR_SENSITIVITY)", "",
          "- Signals with any difference: %d of %d · by field: %s" % (d["signals_with_any_difference"], d["signals_compared"], json.dumps(d["differences_by_field"], sort_keys=True)), "",
          "| signal_id | field | V2_CONTRACT_EXACT | CRYPTO_CALENDAR |", "|---|---|---|---|"]
    for x in d["differences"]:
        L.append("| %s | %s | %s | %s |" % (x["signal_id"], x["field"], x["a"], x["b"]))
    f = r["instrument_feasibility_requirements"]
    L += ["", "## Instrument feasibility requirements (fail-closed; %d instruments, %d short, %d long)" % (f["count"], f["short_instruments"], f["long_instruments"]), "",
          "| symbol | risk | sides | signals | from | missing evidence |", "|---|---|---|---|---|---|"]
    for x in f["instruments"]:
        miss = [k for k, v in x["evidence_required"].items() if v == "MISSING"]
        L.append("| %s | %s | %s | %d | %s | %d fields |" % (x["symbol"], x["mapping_risk"], "/".join(x["sides"]), x["signals"], x["required_from"], len(miss)))
    m = r["missing_external_evidence"]
    L += ["", "## Exact external evidence still missing", "",
          "- Short-instrument evidence (B2/B3 hierarchy) for %d assets: %s" % (len(m["short_instrument_evidence_for"]), ", ".join(m["short_instrument_evidence_for"])),
          "- Long execution-venue evidence for %d assets: %s" % (len(m["long_execution_venue_evidence_for"]), ", ".join(m["long_execution_venue_evidence_for"])),
          "- External OHLC for out-of-radar / missing-price fills: %s" % json.dumps({p: len(v) for p, v in m["external_ohlc_for_out_of_radar_or_missing_price"].items()}),
          "- Cost base case: %s" % m["cost_base_case"]["status"],
          "- Basis alignment: %s · local funding ends %s · borrow: %s" % (m["basis_alignment_status"], m["local_funding_coverage_end"], m["local_borrow_status"]),
          "", "## Verdict", "",
          "- Fee-honest replayable now: **%d** · blocked reason: %s" % (r["fee_honest_replayable_now"], r["fee_honest_blocked_reason"]),
          "- Decisive replay can run: **%s**" % r["decisive_replay_can_run"], ""]
    return "\n".join(L) + "\n"


def _write_atomic(path: Path, blob: bytes) -> None:
    if path.exists():
        raise RuntimeError("refuse_overwrite:%s" % path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute-build", action="store_true")
    ap.add_argument("--build-token", default=os.environ.get("C22_DRY_RUN_TOKEN"))
    a = ap.parse_args(argv)
    r = build_dry_run()
    auth = authorize_write(a.execute_build, a.build_token)
    out = {"mode": "BUILD" if auth["authorized"] else "DRY_RUN_STDOUT_ONLY", "authorization": auth,
           "lifecycle_counts": {p: r["profiles"][p]["lifecycle_counts"] for p in r["profiles"]},
           "reconciles": {p: r["profiles"][p]["reconciliation"]["no_silent_drops"] for p in r["profiles"]},
           "weekend_differences": r["weekend_profile_differences"]["signals_with_any_difference"],
           "fee_honest_replayable_now": r["fee_honest_replayable_now"], "decisive_replay_can_run": r["decisive_replay_can_run"],
           "written": False}
    if auth["authorized"]:
        jp, mp = REPORT_DIR / (REPORT_BASENAME + ".json"), REPORT_DIR / (REPORT_BASENAME + ".md")
        _write_atomic(jp, canonical_bytes(r))
        _write_atomic(mp, render_markdown(r).encode("utf-8"))
        out.update({"written": True, "report_json": str(jp.relative_to(REPO_ROOT) if jp.is_relative_to(REPO_ROOT) else jp).replace("\\", "/"),
                    "report_sha256": hashlib.sha256(canonical_bytes(r)).hexdigest()})
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
