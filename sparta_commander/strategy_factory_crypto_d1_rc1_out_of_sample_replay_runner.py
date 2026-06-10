"""Crypto-D1 V2 RC1 Out-of-Sample REPLAY Runner (READ-ONLY, NO LIVE MONEY).

The human-authorized companion to the Block 180 RC1 out-of-sample robustness research
SPEC. It REPLAYS the single evidence-leading resume policy (RP6 on the committed
evidence), with its parameters strictly UNCHANGED, over the FIXED evaluation windows the
spec defined: one truly held-out 2020 window (BTC/ETH only -- SOL's local data starts
2020-08-11) plus honestly-typed boundary-straddle windows.

It exists to produce the out-of-sample robustness evidence RC1 asked for, WITHOUT
optimization, parameter search, or any change of parameters based on results: the policy is
read verbatim from the Block 175 research plan, the windows verbatim from the Block 180
spec, and neither is ever fitted or tuned here. The simulation engine is the SAME
``_simulate_regime`` used by the approved Block 176 runner -- nothing is reimplemented.

It RUNS NOTHING real: every fill is a model fill at the QA-passed daily close charged the
prep contract's fee + slippage; NO real order is placed; long-only; no leverage / shorting
/ margin. It connects to NO broker / exchange, uses NO network / credentials, and UNLOCKS
no gate: paper_trading_gate, micro_live_gate and the live gate all stay LOCKED. The human
decision DO_NOT_PROMOTE_RESUME_POLICY_YET is carried forward UNCHANGED.

It refuses to run (verdict BLOCKED_NOT_READY, writes nothing) unless the paper-prep gate is
READY for exactly V2 AND the Block 180 RC1 spec is READY. It reads ONLY
``data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv`` and writes ONLY simulated reports under
``reports/crypto_d1_rc1_out_of_sample_replay/``.

Public API:
  - RC1_REPLAY_SCHEMA_VERSION / RC1_REPLAY_LABEL / RC1_REPLAY_MODE
  - RC1_REPLAY_LOG_DIR / SELECTED_VARIANT_ID
  - VERDICT_REPLAYS_COMPLETE / VERDICT_BLOCKED_NOT_READY / NEXT_REQUIRED_ACTION
  - get_rc1_replay_label()
  - run_rc1_out_of_sample_replays(repo_root=".", *, write=True)
  - validate_rc1_out_of_sample_replay_report(report)
  - render_rc1_out_of_sample_replay_markdown(report)
"""

from __future__ import annotations

import json
import os
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
from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
    resume_policy_candidates,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract import (
    HUMAN_DECISION_PRESERVED,
    VERDICT_RC1_SPEC_READY,
    WINDOW_TYPE_HELD_OUT,
    build_rc1_out_of_sample_robustness_spec,
)

RC1_REPLAY_SCHEMA_VERSION = "strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner.v1"
RC1_REPLAY_LABEL = "Crypto-D1 V2 RC1 Out-of-Sample REPLAY Runner (READ-ONLY, NO LIVE MONEY)"
RC1_REPLAY_MODE = "RESEARCH_ONLY"

RC1_REPLAY_LOG_DIR = "reports/crypto_d1_rc1_out_of_sample_replay"

VERDICT_REPLAYS_COMPLETE = "RC1_OUT_OF_SAMPLE_REPLAYS_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_AUTHORIZATION = "HUMAN_APPROVED_RC1_OUT_OF_SAMPLE_REPLAY"

# After these replays the only thing a human could authorize is a REVIEW of the RC1
# out-of-sample evidence -- still no live money, still a separate locked gate.
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_RC1_OUT_OF_SAMPLE_RESULTS"

_VOL_LOOKBACK_DAYS = 30


def get_rc1_replay_label() -> str:
    """Human label for the recognized Crypto-D1 V2 RC1 out-of-sample replay runner."""
    return RC1_REPLAY_LABEL


def run_rc1_out_of_sample_replays(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Replay the evidence-leading resume policy (parameters UNCHANGED) over the FIXED
    Block 180 windows in SIMULATED mode.

    Refuses (verdict BLOCKED_NOT_READY, writes nothing) unless paper prep is READY and the
    Block 180 RC1 spec is READY. Reads only the staged CSVs; when ``write=True`` writes
    ONLY simulated reports under ``reports/crypto_d1_rc1_out_of_sample_replay/``. Runs NO
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

    spec = build_rc1_out_of_sample_robustness_spec(repo_root)
    if spec.get("verdict") != VERDICT_RC1_SPEC_READY:
        blockers.append("rc1_spec_not_ready")
        blockers.extend("spec:" + b for b in spec.get("blockers", []))
        return _blocked_report(blockers, config)

    leader_id = (spec.get("evidence_leading_policy") or {}).get("policy_id")
    policy = next(
        (p for p in resume_policy_candidates() if p.get("policy_id") == leader_id), None
    )
    if policy is None:
        blockers.append("leading_policy_not_in_registered_candidates:" + str(leader_id))
        return _blocked_report(blockers, config)

    windows = list(spec.get("out_of_sample_windows") or [])
    if not windows:
        return _blocked_report(["no_out_of_sample_windows_in_spec"], config)

    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    series_all: dict[str, dict[str, float]] = {}
    files_read: list[str] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        series_all[sym] = _read_close_series(path)
        files_read.append(path)

    sma_window, _min_sleeves = _v2_rule_params(config)

    window_results: list[dict[str, Any]] = []
    log_records: list[dict[str, Any]] = []
    for w in windows:
        symbols = [s for s in (w.get("symbols_expected") or []) if s in series_all]
        metrics: dict[str, Any] | None = None
        if len(symbols) >= 2:
            subset = {s: series_all[s] for s in symbols}
            common = set.intersection(*(set(subset[s].keys()) for s in symbols))
            common_dates = sorted(common)
            if len(common_dates) >= 2:
                closes_aligned = {
                    s: [subset[s][d] for d in common_dates] for s in symbols
                }
                market = _precompute_market(
                    closes_aligned, symbols, sma_window, _VOL_LOOKBACK_DAYS
                )
                metrics = _simulate_regime(
                    common_dates, subset, closes_aligned, symbols, market, config,
                    policy, w["window"],
                )
        entry = {
            "window_id": w.get("window_id"),
            "window": w.get("window"),
            "window_type": w.get("window_type"),
            "symbols": symbols,
            "evaluated": metrics is not None,
            "metrics": metrics,
        }
        window_results.append(entry)
        log_records.append({
            "policy_id": leader_id,
            "window_id": w.get("window_id"),
            "window": w.get("window"),
            "window_type": w.get("window_type"),
            "symbols": symbols,
            "evaluated": metrics is not None,
            "total_return": (metrics or {}).get("total_return"),
            "max_drawdown": (metrics or {}).get("max_drawdown"),
            "sharpe_ratio": (metrics or {}).get("sharpe_ratio"),
            "num_kill_events": (metrics or {}).get("num_kill_events"),
            "num_resume_events": (metrics or {}).get("num_resume_events"),
            "halted_at_end": (metrics or {}).get("halted_at_end"),
            "real_orders_placed": 0,
        })

    report = _base_report(config)
    report.update({
        "verdict": VERDICT_REPLAYS_COMPLETE,
        "blockers": [],
        "selected_variant_id": SELECTED_VARIANT_ID,
        "paper_prep_verdict": readiness.get("verdict"),
        "rc1_spec_verdict": spec.get("verdict"),
        "policy_id": leader_id,
        "policy_parameters_changed": False,
        "window_results": window_results,
        # Carried verbatim from the spec for human comparison; never recomputed here:
        "in_sample_reference": dict(
            (spec.get("evidence_leading_policy") or {}).get("aggregate") or {}
        ),
        "risk_notes": [
            "held_out_window_uses_btc_eth_only_sol_starts_2020_08_11",
            "held_out_window_sma_warmup_limits_exposure_no_pre_2020_history",
            "boundary_straddling_windows_are_window_robustness_not_strictly_out_of_sample",
            "results_are_research_evidence_only_promotion_requires_separate_human_command",
        ],
        "files_read": files_read,
    })

    files_written: list[str] = []
    if write:
        out_dir = os.path.join(repo_root, RC1_REPLAY_LOG_DIR)
        os.makedirs(out_dir, exist_ok=True)
        log_path = os.path.join(out_dir, "rc1_oos_replay_log.jsonl")
        with open(log_path, "w", encoding="utf-8") as fh:
            for rec in log_records:
                fh.write(json.dumps(rec) + "\n")
        files_written.append(log_path)
        rep_json = os.path.join(out_dir, "rc1_oos_replay_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(out_dir, "rc1_oos_replay_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_rc1_out_of_sample_replay_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _base_report(config: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the read-only / no-live-money safety posture. This
    run changes NO gate, tunes NO parameter, and preserves DO_NOT_PROMOTE."""
    return {
        "schema_version": RC1_REPLAY_SCHEMA_VERSION,
        "label": RC1_REPLAY_LABEL,
        "mode": RC1_REPLAY_MODE,
        "authorization": _AUTHORIZATION,
        "human_decision": HUMAN_DECISION_PRESERVED,
        "config": config,
        # Capability posture (simulation only, one fixed policy, fixed windows):
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
        "policy_id": None,
        "policy_parameters_changed": False,
        "window_results": [],
        "in_sample_reference": {},
        "risk_notes": [],
        "files_read": [],
        "files_written": [],
    })
    return report


def validate_rc1_out_of_sample_replay_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) an RC1 replay report's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_REPLAYS_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != RC1_REPLAY_SCHEMA_VERSION:
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
        results = r.get("window_results")
        if not isinstance(results, list) or not results:
            errors.append("no_window_results")
            results = []
        held_out_evaluated = False
        for wr in results:
            m = wr.get("metrics")
            if m and m.get("real_orders_placed") != 0:
                errors.append("real_orders_placed_nonzero:" + str(wr.get("window_id")))
            if wr.get("window_type") == WINDOW_TYPE_HELD_OUT and wr.get("evaluated"):
                held_out_evaluated = True
        if not held_out_evaluated:
            errors.append("held_out_window_not_evaluated")

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_rc1_out_of_sample_replay_markdown(report: Any) -> str:
    """Render an RC1 replay report as deterministic markdown. Pure."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC1 Out-of-Sample REPLAY (READ-ONLY, NO LIVE MONEY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    lines.append("- Selected variant: " + str(r.get("selected_variant_id", "")))
    lines.append("- Policy (parameters UNCHANGED): " + str(r.get("policy_id", "")))
    lines.append("- Human decision (preserved): " + str(r.get("human_decision", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    ref = r.get("in_sample_reference") or {}
    if ref:
        lines.append("- In-sample reference (carried, not recomputed): mean return "
                     + _pct(ref.get("mean_total_return"))
                     + ", worst maxDD " + _pct(ref.get("worst_max_drawdown"))
                     + ", mean Sharpe " + f"{float(ref.get('mean_sharpe_ratio', 0) or 0):.2f}")
    lines.append("")
    for wr in r.get("window_results") or []:
        m = wr.get("metrics") or {}
        lines.append("## " + str(wr.get("window_id")) + " (" + str(wr.get("window_type")) + ")")
        lines.append("- Window: " + str(wr.get("window")) + " | Symbols: "
                     + ", ".join(wr.get("symbols") or []))
        if wr.get("evaluated"):
            lines.append("- Return: " + _pct(m.get("total_return"))
                         + " | MaxDD: " + _pct(m.get("max_drawdown"))
                         + " | Sharpe: " + f"{float(m.get('sharpe_ratio', 0) or 0):.2f}"
                         + " | Kills: " + str(m.get("num_kill_events"))
                         + " | Resumes: " + str(m.get("num_resume_events")))
        else:
            lines.append("- NOT EVALUATED (insufficient data in window)")
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
    out = run_rc1_out_of_sample_replays(repo_root=".", write=False)
    print(render_rc1_out_of_sample_replay_markdown(out))
