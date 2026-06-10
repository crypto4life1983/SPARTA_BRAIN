"""Crypto-D1 V2 RC2 Cross-Policy REPLAY Runner (READ-ONLY, NO LIVE MONEY).

The human-authorized companion to the Block 184 RC2 cross-policy stability SPEC. It
REPLAYS ALL SIX fixed resume-policy candidates (RP1..RP6, parameters strictly UNCHANGED,
read verbatim from the Block 184 spec which carries them verbatim from the Block 175
research plan) over the SAME four FIXED out-of-sample windows RC1 used, to answer ONE
pre-registered question: does the RC1 evidence leader still lead versus the other fixed
candidates across the same out-of-sample windows?

It exists to produce the RC2 cross-policy stability evidence, WITHOUT optimization,
parameter search, or any change of parameters based on results: the policies, windows,
and ranking categories are all fixed BEFORE this run by Blocks 175/180/184 and are never
fitted or tuned here. The simulation engine is the SAME ``_simulate_regime`` used by the
approved Block 176 and Block 181 runners -- nothing is reimplemented. Ranking is pure
reporting; nothing is selected, promoted, or changed based on it.

It RUNS NOTHING real: every fill is a model fill at the QA-passed daily close charged the
prep contract's fee + slippage; NO real order is placed; long-only; no leverage / shorting
/ margin. It connects to NO broker / exchange, uses NO network / credentials, and UNLOCKS
no gate: paper_trading_gate, micro_live_gate and the live gate all stay LOCKED. The human
decision DO_NOT_PROMOTE_RESUME_POLICY_YET is carried forward UNCHANGED.

It refuses to run (verdict BLOCKED_NOT_READY, writes nothing) unless the paper-prep gate
is READY for exactly V2 AND the Block 184 RC2 spec is READY. It reads ONLY
``data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv`` and writes ONLY simulated reports under
``reports/crypto_d1_rc2_cross_policy_replay/``.

Public API:
  - RC2_REPLAY_SCHEMA_VERSION / RC2_REPLAY_LABEL / RC2_REPLAY_MODE
  - RC2_REPLAY_LOG_DIR / SELECTED_VARIANT_ID
  - VERDICT_REPLAYS_COMPLETE / VERDICT_BLOCKED_NOT_READY / NEXT_REQUIRED_ACTION
  - get_rc2_replay_label()
  - run_rc2_cross_policy_replays(repo_root=".", *, write=True)
  - validate_rc2_cross_policy_replay_report(report)
  - render_rc2_cross_policy_replay_markdown(report)
"""

from __future__ import annotations

import json
import os
import statistics
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_APPROVED_INPUT_DIR,
    QA_REQUIRED_SYMBOLS,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner import (
    _read_close_series,
)
from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
    VERDICT_READY,
    build_paper_prep_config,
    check_paper_prep_readiness,
)
from sparta_commander.strategy_factory_crypto_d1_paper_trading_run_simulated import (
    _v2_rule_params,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner import (
    _precompute_market,
    _simulate_regime,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract import (
    WINDOW_TYPE_HELD_OUT,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_stability_research_contract import (
    HUMAN_DECISION_PRESERVED,
    RANKING_CATEGORIES,
    VERDICT_RC2_SPEC_READY,
    build_rc2_cross_policy_stability_spec,
)

RC2_REPLAY_SCHEMA_VERSION = "strategy_factory_crypto_d1_rc2_cross_policy_replay_runner.v1"
RC2_REPLAY_LABEL = "Crypto-D1 V2 RC2 Cross-Policy REPLAY Runner (READ-ONLY, NO LIVE MONEY)"
RC2_REPLAY_MODE = "RESEARCH_ONLY"

RC2_REPLAY_LOG_DIR = "reports/crypto_d1_rc2_cross_policy_replay"

VERDICT_REPLAYS_COMPLETE = "RC2_CROSS_POLICY_REPLAYS_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_AUTHORIZATION = "HUMAN_APPROVED_RC2_CROSS_POLICY_REPLAY"

# After these replays the only thing a human could authorize is a REVIEW of the RC2
# cross-policy evidence -- still no live money, still a separate locked gate.
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_RC2_CROSS_POLICY_RESULTS"

_VOL_LOOKBACK_DAYS = 30


def get_rc2_replay_label() -> str:
    """Human label for the recognized Crypto-D1 V2 RC2 cross-policy replay runner."""
    return RC2_REPLAY_LABEL


def _aggregate_windows(window_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate one policy's per-window metrics. Reporting only -- never feeds back into
    parameters. Pure."""
    rets = [w["metrics"]["total_return"] for w in window_results if w.get("metrics")]
    dds = [w["metrics"]["max_drawdown"] for w in window_results if w.get("metrics")]
    shp = [w["metrics"]["sharpe_ratio"] for w in window_results if w.get("metrics")]
    return {
        "windows_evaluated": len(rets),
        "mean_total_return": statistics.fmean(rets) if rets else 0.0,
        "min_total_return": min(rets) if rets else 0.0,
        "worst_max_drawdown": min(dds) if dds else 0.0,
        "mean_sharpe_ratio": statistics.fmean(shp) if shp else 0.0,
    }


def _rank_policies(policy_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify the best policy by mean return, by worst-case drawdown (least bad), and by
    mean Sharpe across the fixed windows. Pure reporting -- NO parameter is changed and NO
    policy is promoted based on this."""
    if not policy_results:
        return {}
    by_return = max(policy_results, key=lambda p: p["aggregate"]["mean_total_return"])
    by_drawdown = max(policy_results, key=lambda p: p["aggregate"]["worst_max_drawdown"])
    by_sharpe = max(policy_results, key=lambda p: p["aggregate"]["mean_sharpe_ratio"])
    return {
        "best_by_mean_return": by_return["policy_id"],
        "best_by_worst_drawdown": by_drawdown["policy_id"],
        "best_by_mean_sharpe": by_sharpe["policy_id"],
    }


def _leader_stability(rankings: dict[str, Any], rc1_leader: Any) -> dict[str, Any]:
    """Answer the pre-registered RC2 question descriptively: which ranking categories does
    the RC1 leader still lead out of sample? Pure reporting only."""
    cats_led = [
        c for c, key in (
            ("mean_total_return", "best_by_mean_return"),
            ("worst_max_drawdown", "best_by_worst_drawdown"),
            ("mean_sharpe_ratio", "best_by_mean_sharpe"),
        )
        if rankings.get(key) == rc1_leader
    ]
    return {
        "rc1_leader_policy_id": rc1_leader,
        "categories_led_by_rc1_leader": cats_led,
        "rc1_leader_leads_all_categories": len(cats_led) == len(RANKING_CATEGORIES),
        "rc1_leader_leads_any_category": bool(cats_led),
    }


def run_rc2_cross_policy_replays(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Replay ALL fixed candidate policies (parameters UNCHANGED) over the FIXED Block 184
    windows in SIMULATED mode.

    Refuses (verdict BLOCKED_NOT_READY, writes nothing) unless paper prep is READY and the
    Block 184 RC2 spec is READY. Reads only the staged CSVs; when ``write=True`` writes
    ONLY simulated reports under ``reports/crypto_d1_rc2_cross_policy_replay/``. Runs NO
    optimization / parameter search, places NO real order, connects to NO broker/exchange,
    uses NO network/credentials, and UNLOCKS no gate."""
    readiness = check_paper_prep_readiness(repo_root)
    config = build_paper_prep_config()

    blockers: list[str] = []
    if readiness.get("verdict") != VERDICT_READY:
        blockers.append("paper_prep_not_ready")
        blockers.extend("prep:" + b for b in readiness.get("blockers", []))
    if blockers:
        return _blocked_report(blockers, config)

    spec = build_rc2_cross_policy_stability_spec(repo_root)
    if spec.get("verdict") != VERDICT_RC2_SPEC_READY:
        blockers.append("rc2_spec_not_ready")
        blockers.extend("spec:" + b for b in spec.get("blockers", []))
        return _blocked_report(blockers, config)

    policies = list(spec.get("candidate_policies") or [])
    windows = list(spec.get("evaluation_windows") or [])
    rc1_leader = spec.get("rc1_leader_policy_id")
    if not policies:
        return _blocked_report(["no_candidate_policies_in_spec"], config)
    if not windows:
        return _blocked_report(["no_evaluation_windows_in_spec"], config)

    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    series_all: dict[str, dict[str, float]] = {}
    files_read: list[str] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        series_all[sym] = _read_close_series(path)
        files_read.append(path)

    sma_window, _min_sleeves = _v2_rule_params(config)

    # Precompute per-window market state ONCE; reuse across all six policies.
    window_ctx: list[dict[str, Any]] = []
    for w in windows:
        symbols = [s for s in (w.get("symbols_expected") or []) if s in series_all]
        ctx: dict[str, Any] = {"window": w, "symbols": symbols, "ready": False}
        if len(symbols) >= 2:
            subset = {s: series_all[s] for s in symbols}
            common = set.intersection(*(set(subset[s].keys()) for s in symbols))
            common_dates = sorted(common)
            if len(common_dates) >= 2:
                closes_aligned = {
                    s: [subset[s][d] for d in common_dates] for s in symbols
                }
                ctx.update({
                    "ready": True,
                    "subset": subset,
                    "common_dates": common_dates,
                    "closes_aligned": closes_aligned,
                    "market": _precompute_market(
                        closes_aligned, symbols, sma_window, _VOL_LOOKBACK_DAYS
                    ),
                })
        window_ctx.append(ctx)

    policy_results: list[dict[str, Any]] = []
    log_records: list[dict[str, Any]] = []
    for policy in policies:
        window_results: list[dict[str, Any]] = []
        for ctx in window_ctx:
            w = ctx["window"]
            metrics: dict[str, Any] | None = None
            if ctx["ready"]:
                metrics = _simulate_regime(
                    ctx["common_dates"], ctx["subset"], ctx["closes_aligned"],
                    ctx["symbols"], ctx["market"], config, policy, w["window"],
                )
            entry = {
                "window_id": w.get("window_id"),
                "window": w.get("window"),
                "window_type": w.get("window_type"),
                "symbols": ctx["symbols"],
                "evaluated": metrics is not None,
                "metrics": metrics,
            }
            window_results.append(entry)
            log_records.append({
                "policy_id": policy.get("policy_id"),
                "window_id": w.get("window_id"),
                "window": w.get("window"),
                "window_type": w.get("window_type"),
                "evaluated": metrics is not None,
                "total_return": (metrics or {}).get("total_return"),
                "max_drawdown": (metrics or {}).get("max_drawdown"),
                "sharpe_ratio": (metrics or {}).get("sharpe_ratio"),
                "num_kill_events": (metrics or {}).get("num_kill_events"),
                "num_resume_events": (metrics or {}).get("num_resume_events"),
                "halted_at_end": (metrics or {}).get("halted_at_end"),
                "real_orders_placed": 0,
            })
        policy_results.append({
            "policy_id": policy.get("policy_id"),
            "description": policy.get("description"),
            "reentry_exposure": policy.get("reentry_exposure"),
            "window_results": window_results,
            "aggregate": _aggregate_windows(window_results),
        })

    rankings = _rank_policies(policy_results)

    report = _base_report(config)
    report.update({
        "verdict": VERDICT_REPLAYS_COMPLETE,
        "blockers": [],
        "selected_variant_id": SELECTED_VARIANT_ID,
        "paper_prep_verdict": readiness.get("verdict"),
        "rc2_spec_verdict": spec.get("verdict"),
        "policy_parameters_changed": False,
        "policy_results": policy_results,
        "rankings": rankings,
        "leader_stability": _leader_stability(rankings, rc1_leader),
        "risk_notes": [
            "policies_verbatim_from_block_175_no_fitting",
            "windows_verbatim_from_block_180_same_as_rc1",
            "rankings_are_pure_reporting_nothing_promoted_or_changed",
            "results_are_research_evidence_only_promotion_requires_separate_human_command",
        ],
        "files_read": files_read,
    })

    files_written: list[str] = []
    if write:
        out_dir = os.path.join(repo_root, RC2_REPLAY_LOG_DIR)
        os.makedirs(out_dir, exist_ok=True)
        log_path = os.path.join(out_dir, "rc2_cross_policy_replay_log.jsonl")
        with open(log_path, "w", encoding="utf-8") as fh:
            for rec in log_records:
                fh.write(json.dumps(rec) + "\n")
        files_written.append(log_path)
        rep_json = os.path.join(out_dir, "rc2_cross_policy_replay_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(out_dir, "rc2_cross_policy_replay_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_rc2_cross_policy_replay_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _base_report(config: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the read-only / no-live-money safety posture. This
    run changes NO gate, tunes NO parameter, and preserves DO_NOT_PROMOTE."""
    return {
        "schema_version": RC2_REPLAY_SCHEMA_VERSION,
        "label": RC2_REPLAY_LABEL,
        "mode": RC2_REPLAY_MODE,
        "authorization": _AUTHORIZATION,
        "human_decision": HUMAN_DECISION_PRESERVED,
        "config": config,
        # Capability posture (simulation only, fixed policies, fixed windows):
        "uses_real_money": False,
        "connects_broker": False,
        "connects_exchange": False,
        "executes_real_orders": False,
        "simulated_orders_only": True,
        "uses_network": False,
        "uses_credentials": False,
        "ran_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
        "used_lookahead": False,
        "used_leverage": False,
        "used_shorting": False,
        "used_margin": False,
        "uses_only_qa_passed_inputs": True,
        "manual_csv_only": True,
        "promotes_resume_policy": False,
        # Gate posture (UNCHANGED by this run):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "unlocks_downstream_gate": False,
        "authorizes_live_trading": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def _blocked_report(blockers: list[str], config: dict[str, Any]) -> dict[str, Any]:
    """A refusal report: a required gate or input was not READY, so no replay occurred and
    nothing was written."""
    report = _base_report(config)
    report.update({
        "verdict": VERDICT_BLOCKED_NOT_READY,
        "blockers": list(blockers),
        "selected_variant_id": SELECTED_VARIANT_ID,
        "policy_parameters_changed": False,
        "policy_results": [],
        "rankings": {},
        "leader_stability": {},
        "risk_notes": [],
        "files_read": [],
        "files_written": [],
    })
    return report


def validate_rc2_cross_policy_replay_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) an RC2 replay report's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_REPLAYS_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != RC2_REPLAY_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if r.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")
    if r.get("human_decision") != HUMAN_DECISION_PRESERVED:
        errors.append("human_decision_not_do_not_promote")
    if r.get("policy_parameters_changed") is not False:
        errors.append("policy_parameters_changed")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "uses_real_money", "connects_broker", "connects_exchange", "executes_real_orders",
        "uses_network", "uses_credentials", "ran_optimization", "ran_parameter_search",
        "parameters_changed_based_on_results", "used_lookahead", "used_leverage",
        "used_shorting", "used_margin", "unlocks_downstream_gate", "authorizes_live_trading",
        "promotes_resume_policy",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("simulated_orders_only") is not True:
        errors.append("simulated_orders_only_not_true")

    if r.get("verdict") == VERDICT_REPLAYS_COMPLETE:
        results = r.get("policy_results")
        if not isinstance(results, list) or not results:
            errors.append("no_policy_results")
            results = []
        if results and len(results) < 2:
            errors.append("fewer_than_two_policies_compared")
        for p in results:
            held_out_evaluated = False
            for wr in p.get("window_results") or []:
                m = wr.get("metrics")
                if m and m.get("real_orders_placed") != 0:
                    errors.append(
                        "real_orders_placed_nonzero:" + str(p.get("policy_id"))
                    )
                if wr.get("window_type") == WINDOW_TYPE_HELD_OUT and wr.get("evaluated"):
                    held_out_evaluated = True
            if not held_out_evaluated:
                errors.append("held_out_window_not_evaluated:" + str(p.get("policy_id")))
        rankings = r.get("rankings") or {}
        valid_ids = {p.get("policy_id") for p in results}
        for key in ("best_by_mean_return", "best_by_worst_drawdown", "best_by_mean_sharpe"):
            if rankings.get(key) not in valid_ids:
                errors.append("ranking_missing_or_unknown:" + key)

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_rc2_cross_policy_replay_markdown(report: Any) -> str:
    """Render an RC2 replay report as deterministic markdown. Pure."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC2 Cross-Policy REPLAY (READ-ONLY, NO LIVE MONEY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    lines.append("- Selected variant: " + str(r.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(r.get("human_decision", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    rk = r.get("rankings") or {}
    if rk:
        lines.append("- Best by mean return: " + str(rk.get("best_by_mean_return")))
        lines.append("- Best by worst drawdown: " + str(rk.get("best_by_worst_drawdown")))
        lines.append("- Best by mean Sharpe: " + str(rk.get("best_by_mean_sharpe")))
    ls = r.get("leader_stability") or {}
    if ls:
        lines.append("- RC1 leader: " + str(ls.get("rc1_leader_policy_id"))
                     + " | leads categories: "
                     + (", ".join(ls.get("categories_led_by_rc1_leader") or []) or "(none)")
                     + " | leads all: " + str(ls.get("rc1_leader_leads_all_categories")))
    lines.append("")
    for p in r.get("policy_results") or []:
        agg = p.get("aggregate") or {}
        lines.append("## " + str(p.get("policy_id")) + " (" + str(p.get("reentry_exposure")) + ")")
        lines.append("- Mean return: " + _pct(agg.get("mean_total_return"))
                     + " | Worst drawdown: " + _pct(agg.get("worst_max_drawdown"))
                     + " | Mean Sharpe: " + f"{float(agg.get('mean_sharpe_ratio', 0) or 0):.2f}")
        for wr in p.get("window_results") or []:
            m = wr.get("metrics") or {}
            if wr.get("evaluated"):
                lines.append("  - " + str(wr.get("window_id")) + ": return "
                             + _pct(m.get("total_return"))
                             + ", maxDD " + _pct(m.get("max_drawdown"))
                             + ", Sharpe " + f"{float(m.get('sharpe_ratio', 0) or 0):.2f}"
                             + ", kills " + str(m.get("num_kill_events"))
                             + ", resumes " + str(m.get("num_resume_events")))
            else:
                lines.append("  - " + str(wr.get("window_id")) + ": NOT EVALUATED")
    lines.append("")
    lines.append("## Risk notes")
    for note in r.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- uses_real_money: False | executes_real_orders: False | ran_optimization: False")
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_rc2_cross_policy_replays(repo_root=".", write=False)
    print(render_rc2_cross_policy_replay_markdown(out))
