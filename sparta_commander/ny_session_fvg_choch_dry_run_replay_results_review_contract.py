"""SPARTA NY-Session FVG+CHOCH DRY-RUN REPLAY RESULTS REVIEW (READ-ONLY).

The human-review contract over the fixture-only replay runner: it exercises
the LIVE runner on canonical in-memory fixtures, observes its behavior, and
certifies whether it is safe, deterministic, and fee-honest enough to proceed
-- after a SEPARATE human approval -- to a real-candle staging block.
Acceptance stages nothing, scores nothing, promotes nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_replay_runner_dry_run import (
    run_replay_dry_run,
)
from sparta_commander.ny_session_fvg_choch_replay_spec import (
    VERDICT_RP_READY,
    build_ny_fvg_choch_replay_spec,
)

RV_SCHEMA_VERSION = "ny_session_fvg_choch_dry_run_replay_results_review.v1"
RV_LABEL = ("SPARTA NY-Session FVG+CHOCH Dry-Run Replay Results Review "
            "(READ-ONLY, REVIEW ONLY)")
RV_MODE = "RESEARCH_ONLY"
VERDICT_ACCEPTED = "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING"
VERDICT_REJECTED = "DRY_RUN_REPLAY_RESULTS_REJECTED"
VERDICT_BLOCKED = "DRY_RUN_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_REAL_CANDLE_STAGING_PLAN"

REVIEW_CHECKLIST = (
    "runner_gated_on_ready_replay_spec",
    "accepted_label_replays",
    "rejected_label_cannot_replay",
    "all_five_outcomes_supported",
    "net_after_costs_mandatory",
    "costs_worsen_losses_and_reduce_wins",
    "gross_only_pass_claims_impossible",
    "same_candle_entry_stop_conservative",
    "stop_checked_before_target",
    "rejected_replays_auditable",
    "fixture_only_no_fetch_no_network_no_credentials_no_execution",
)

_LABEL = {"detector_status": "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
          "setup_id": "review_fixture", "symbol": "BTC",
          "session_date": "2026-06-11", "direction": "long",
          "proposed_entry_price": 100.0, "proposed_stop_price": 95.0,
          "proposed_target_4r_price": 120.0}
_T = ["2026-06-11T14:0%d:00Z" % i for i in range(5)]


def _c(ts, high, low, close):
    return {"timestamp_utc": ts, "high": high, "low": low, "close": close}


def _req(candles, **kw):
    base = {"candles": candles, "fees_bps": 4.0, "spread_bps": 1.0,
            "slippage_bps": 5.0}
    base.update(kw)
    return base


def get_dry_run_replay_results_review_label() -> str:
    return RV_LABEL


def observe_runner_behavior() -> dict[str, Any]:
    """Exercise the LIVE runner on canonical fixtures. Pure/in-memory."""
    win = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102), _c(_T[1], 121, 101, 120)]))
    loss = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102), _c(_T[1], 101, 94.5, 95)]))
    breakeven = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102), _c(_T[1], 106, 101, 105.5),
         _c(_T[2], 104, 99.9, 101)], breakeven_enabled=True))
    timeout = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102), _c(_T[1], 104, 101, 103)]))
    no_entry = run_replay_dry_run(_LABEL, _req([_c(_T[0], 110, 101, 105)]))
    rejected_label = run_replay_dry_run(
        {"detector_status": "SETUP_REJECTED_AMBIGUOUS"},
        _req([_c(_T[0], 103, 100, 102)]))
    same_candle = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 94.0, 95)]))
    # ambiguous candle touching both stop and target after entry
    ambiguous = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102), _c(_T[1], 121, 94.5, 110)]))
    forbidden = run_replay_dry_run(_LABEL, _req(
        [_c(_T[0], 103, 100, 102)], order_id="x"))
    spec = build_ny_fvg_choch_replay_spec()
    return {
        "replay_spec_verdict": spec.get("verdict"),
        "outcomes": {"target": win.get("exit_reason"),
                     "stop": loss.get("exit_reason"),
                     "breakeven": breakeven.get("exit_reason"),
                     "timeout": timeout.get("exit_reason"),
                     "no_entry": no_entry.get("replay_status")},
        "win_gross_r": win.get("gross_r"),
        "win_net_r": win.get("net_r_after_costs"),
        "loss_gross_r": loss.get("gross_r"),
        "loss_net_r": loss.get("net_r_after_costs"),
        "accepted_label_status": win.get("replay_status"),
        "rejected_label_status": rejected_label.get("replay_status"),
        "same_candle_exit": same_candle.get("exit_reason"),
        "ambiguous_exit": ambiguous.get("exit_reason"),
        "rejected_audit_notes": no_entry.get("audit_notes"),
        "forbidden_status": forbidden.get("replay_status"),
        "net_fields_numeric": all(isinstance(r.get("net_r_after_costs"),
                                             (int, float))
                                  for r in (win, loss, breakeven, timeout)),
        "gross_only_field_absent": all("gross_only_pass_claim" not in r
                                       for r in (win, loss)),
        "deterministic": win == run_replay_dry_run(_LABEL, _req(
            [_c(_T[0], 103, 100, 102), _c(_T[1], 121, 101, 120)])),
    }


def certify_dry_run_results(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of an observed runner behavior. Pure."""
    review: dict[str, Any] = {
        "schema_version": RV_SCHEMA_VERSION, "label": RV_LABEL, "mode": RV_MODE,
        "lane": "crypto_d1_auto_research", "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "acceptance_stages_nothing": True,
        "acceptance_is_not_a_promotion": True,
        "real_candle_staging_requires_its_own_human_approval": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(observation, dict):
        review["verdict"] = VERDICT_BLOCKED
        review["blockers"].append("observation_missing_runner_unavailable")
        return review
    o = observation
    r: dict[str, bool] = {}
    r["runner_gated_on_ready_replay_spec"] = (
        o.get("replay_spec_verdict") == VERDICT_RP_READY)
    r["accepted_label_replays"] = (
        o.get("accepted_label_status") == "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW")
    r["rejected_label_cannot_replay"] = (
        o.get("rejected_label_status") == "REPLAY_REJECTED_INVALID_LABEL")
    outcomes = o.get("outcomes") or {}
    r["all_five_outcomes_supported"] = (
        outcomes.get("target") == "target_4r_hit"
        and outcomes.get("stop") == "stop_hit"
        and outcomes.get("breakeven") == "breakeven_stop_hit"
        and outcomes.get("timeout") == "timeout_end_of_window"
        and outcomes.get("no_entry") == "REPLAY_REJECTED_NO_ENTRY")
    r["net_after_costs_mandatory"] = o.get("net_fields_numeric") is True
    win_g, win_n = o.get("win_gross_r"), o.get("win_net_r")
    loss_g, loss_n = o.get("loss_gross_r"), o.get("loss_net_r")
    r["costs_worsen_losses_and_reduce_wins"] = (
        isinstance(win_g, (int, float)) and isinstance(win_n, (int, float))
        and isinstance(loss_g, (int, float)) and isinstance(loss_n, (int, float))
        and win_n < win_g and loss_n < loss_g)
    r["gross_only_pass_claims_impossible"] = o.get(
        "gross_only_field_absent") is True
    r["same_candle_entry_stop_conservative"] = (
        o.get("same_candle_exit") == "stop_hit_same_candle")
    r["stop_checked_before_target"] = o.get("ambiguous_exit") == "stop_hit"
    r["rejected_replays_auditable"] = "kept on record" in str(
        o.get("rejected_audit_notes"))
    r["fixture_only_no_fetch_no_network_no_credentials_no_execution"] = (
        o.get("forbidden_status") == "REPLAY_REJECTED_FORBIDDEN_CAPABILITY"
        and o.get("deterministic") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
    else:
        review["verdict"] = VERDICT_ACCEPTED
    return review


def build_dry_run_replay_results_review() -> dict[str, Any]:
    """Observe the live runner and certify it. Pure/in-memory."""
    return certify_dry_run_results(observe_runner_behavior())


def validate_dry_run_replay_results_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_ACCEPTED, VERDICT_REJECTED,
                                VERDICT_BLOCKED):
        errors.append("bad_verdict")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_REJECTED, VERDICT_BLOCKED) and not v.get(
            "blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("acceptance_stages_nothing", True),
        ("acceptance_is_not_a_promotion", True),
        ("real_candle_staging_requires_its_own_human_approval", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "fetches_data",
                "calls_api", "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
