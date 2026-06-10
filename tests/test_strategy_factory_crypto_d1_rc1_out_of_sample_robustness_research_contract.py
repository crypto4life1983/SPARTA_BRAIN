"""Tests for the Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Contract (READ-ONLY).

Every plan consumed here is a FAKE in-memory dict (or one derived under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no simulation,
no file write, no gate is unlocked. The contract is a spec only: it fixes evaluation windows
for the evidence-leading resume policy with parameters UNCHANGED, preserves
DO_NOT_PROMOTE_RESUME_POLICY_YET, and runs nothing."""

from __future__ import annotations

import ast
import datetime
import json

import sparta_commander.strategy_factory_crypto_d1_post_resume_policy_research_continuation_plan_contract as cp
import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract as rc1
import sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract as rr
import sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner as rs


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe, regimes=4, real_orders=0):
    regime_results = []
    for k in range(regimes):
        regime_results.append({
            "regime_id": f"regime_{k}", "window": "2021-01-01..2021-12-31",
            "evaluated": True,
            "metrics": {
                "total_return": mean_ret, "max_drawdown": worst_dd,
                "sharpe_ratio": mean_sharpe, "real_orders_placed": real_orders,
                "num_kill_events": 1, "num_resume_events": 1, "halted_at_end": False,
            },
        })
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "regime_results": regime_results,
        "aggregate": {
            "regimes_evaluated": regimes, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _sim_report(*, complete=True, rankings_leader="RP6_resume_after_volatility_cools",
                real_orders=0, override=None):
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rs._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rs.VERDICT_RERUNS_COMPLETE if complete else rs.VERDICT_BLOCKED_NOT_READY,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "symbols": ["BTC", "ETH", "SOL"],
        "policy_results": [
            _policy("RP1_wait_7d_trend_on", mean_ret=0.68, worst_dd=-0.61, mean_sharpe=0.09),
            _policy("RP6_resume_after_volatility_cools", mean_ret=1.55, worst_dd=-0.32,
                    mean_sharpe=0.57, real_orders=real_orders),
        ],
        "rankings": {
            "best_by_mean_return": rankings_leader,
            "best_by_worst_drawdown": rankings_leader,
            "best_by_mean_sharpe": rankings_leader,
        },
        "files_read": [], "files_written": [],
    })
    if override:
        rep.update(override)
    return rep


def _write_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(
        json.dumps(_sim_report()), encoding="utf-8"
    )


def _ready_plan(tmp_path):
    _write_report(tmp_path)
    return cp.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))


def _dates(window):
    a, b = window.split("..")
    return datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)


# --------------------------------------------------------------------------- #
# ready upstream plan -> READY spec, DO_NOT_PROMOTE preserved
# --------------------------------------------------------------------------- #
def test_record_ready_spec_preserves_do_not_promote(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_READY
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert s["approved_for_execution"] is False
    assert s["human_review_required"] is True
    assert s["selected_direction_id"] == "RC1_out_of_sample_robustness_of_leading_policy"
    assert s["next_required_action"] == "HUMAN_APPROVED_RC1_OUT_OF_SAMPLE_REPLAY"
    assert s["blockers"] == []


def test_spec_acknowledges_leader_as_evidence_only(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    assert s["evidence_leading_policy"]["policy_id"] == "RP6_resume_after_volatility_cools"
    assert s["leading_policy_parameters_changed"] is False
    assert "acknowledged_evidence_leading_policy:RP6_resume_after_volatility_cools" in s["risk_notes"]
    assert "acknowledged_as_evidence_only_not_promotion" in s["risk_notes"]
    assert "leading_policy_parameters_unchanged_no_optimization_no_search" in s["risk_notes"]
    assert "promotion_requires_separate_explicit_human_command" in s["risk_notes"]


def test_build_reads_local_report(tmp_path):
    _write_report(tmp_path)
    s = rc1.build_rc1_out_of_sample_robustness_spec(repo_root=str(tmp_path))
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_READY
    assert s["continuation_plan_verdict"] == cp.VERDICT_PLAN_READY
    assert s["resume_policy_sim_report_found"] is True


def test_build_blocks_when_no_local_report(tmp_path):
    s = rc1.build_rc1_out_of_sample_robustness_spec(repo_root=str(tmp_path))
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_BLOCKED
    assert "continuation_plan_not_ready" in s["blockers"]
    # the human decision is STILL preserved as DO_NOT_PROMOTE even when blocked
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_plan_blocks():
    s = rc1.record_rc1_out_of_sample_spec(None)
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_BLOCKED
    assert "continuation_plan_missing" in s["blockers"]
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_plan_with_overturned_decision_blocks(tmp_path):
    plan = _ready_plan(tmp_path)
    plan["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    s = rc1.record_rc1_out_of_sample_spec(plan)
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_BLOCKED
    assert "human_decision_not_do_not_promote" in s["blockers"]
    # the spec's own carried decision stays DO_NOT_PROMOTE regardless
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_plan_missing_rc1_direction_blocks(tmp_path):
    plan = _ready_plan(tmp_path)
    plan["research_continuation_directions"] = [
        d for d in plan["research_continuation_directions"]
        if d["direction_id"] != rc1.SELECTED_DIRECTION_ID
    ]
    s = rc1.record_rc1_out_of_sample_spec(plan)
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_BLOCKED
    assert "rc1_direction_not_in_continuation_plan" in s["blockers"]


def test_plan_invalid_blocks(tmp_path):
    plan = _ready_plan(tmp_path)
    plan["micro_live_gate_locked"] = False  # breaks Block 179's own validator
    s = rc1.record_rc1_out_of_sample_spec(plan)
    assert s["verdict"] == rc1.VERDICT_RC1_SPEC_BLOCKED
    assert "continuation_plan_invalid" in s["blockers"]


# --------------------------------------------------------------------------- #
# the spec unlocks nothing and runs nothing
# --------------------------------------------------------------------------- #
def test_spec_unlocks_nothing(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_simulation", "runs_backtest",
        "runs_optimization", "ran_parameter_search", "parameters_changed_based_on_results",
        "fetches_data", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "authorizes_paper_execution",
        "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
        "promotes_resume_policy", "unlocks_downstream_gate",
    ):
        assert s[key] is False, key


# --------------------------------------------------------------------------- #
# windows are fixed, honestly typed, and the held-out window is truly held out
# --------------------------------------------------------------------------- #
def test_windows_are_fixed_with_one_true_held_out():
    windows = rc1.out_of_sample_windows()
    assert len(windows) == 4
    ids = [w["window_id"] for w in windows]
    assert len(ids) == len(set(ids))
    held_out = [w for w in windows if w["window_type"] == rc1.WINDOW_TYPE_HELD_OUT]
    assert len(held_out) == 1
    for w in windows:
        assert w["window_type"] in (
            rc1.WINDOW_TYPE_HELD_OUT, rc1.WINDOW_TYPE_BOUNDARY_STRADDLING
        )


def test_held_out_window_does_not_overlap_evidence_windows():
    held_out = next(
        w for w in rc1.OUT_OF_SAMPLE_WINDOWS
        if w["window_type"] == rc1.WINDOW_TYPE_HELD_OUT
    )
    _, held_end = _dates(held_out["window"])
    from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
        REGIMES_TO_COVER,
    )
    earliest_evidence_start = min(_dates(r["window"])[0] for r in REGIMES_TO_COVER)
    # the held-out window ends strictly before any evidence regime begins
    assert held_end < earliest_evidence_start


def test_held_out_window_excludes_sol():
    held_out = next(
        w for w in rc1.OUT_OF_SAMPLE_WINDOWS
        if w["window_type"] == rc1.WINDOW_TYPE_HELD_OUT
    )
    assert held_out["symbols_expected"] == ["BTC", "ETH"]


def test_windows_accessor_returns_copies():
    a = rc1.out_of_sample_windows()
    a[0]["window_id"] = "tampered"
    b = rc1.out_of_sample_windows()
    assert b[0]["window_id"] != "tampered"


# --------------------------------------------------------------------------- #
# planned replays: one per window, inert, human-gated, parameters unchanged
# --------------------------------------------------------------------------- #
def test_planned_replays_cover_every_window_and_run_nothing():
    replays = rc1.planned_out_of_sample_replays()
    window_ids = {w["window_id"] for w in rc1.OUT_OF_SAMPLE_WINDOWS}
    assert {r["window_id"] for r in replays} == window_ids
    for r in replays:
        assert r["is_run"] is False
        assert r["requires_human_command"] is True
        assert r["policy_parameters_changed"] is False
        assert r["data_scope"] == "QA_PASSED_LOCAL_CSV_ONLY"
        assert r["authorization_required"] == rc1.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    assert rc1.validate_rc1_out_of_sample_robustness_spec(s)["valid"] is True


def test_validate_passes_on_blocked():
    s = rc1.record_rc1_out_of_sample_spec(None)
    assert rc1.validate_rc1_out_of_sample_robustness_spec(s)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    s["micro_live_gate_locked"] = False
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    s["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_replay_marked_run(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    s["planned_replays"][0]["is_run"] = True
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert any(e.startswith("replay_marked_run:") for e in v["errors"])


def test_validate_rejects_changed_parameters(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    s["planned_replays"][0]["policy_parameters_changed"] = True
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert any(e.startswith("replay_changes_parameters:") for e in v["errors"])


def test_validate_rejects_missing_held_out_window(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    for w in s["out_of_sample_windows"]:
        w["window_type"] = rc1.WINDOW_TYPE_BOUNDARY_STRADDLING
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert "no_truly_held_out_window" in v["errors"]


def test_validate_rejects_capability_true(tmp_path):
    s = rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    s["runs_simulation"] = True
    v = rc1.validate_rc1_out_of_sample_robustness_spec(s)
    assert v["valid"] is False
    assert any("capability_not_false:runs_simulation" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    md = rc1.render_rc1_out_of_sample_robustness_spec_markdown(
        rc1.record_rc1_out_of_sample_spec(_ready_plan(tmp_path))
    )
    assert md.startswith("# Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Spec")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md
    assert "OOS_W1_2020_early_held_out" in md


# --------------------------------------------------------------------------- #
# label / posture
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rc1.get_rc1_out_of_sample_robustness_contract_label() == rc1.RC1_LABEL
    assert "READ-ONLY" in rc1.RC1_LABEL
    assert rc1.RC1_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rc1.NEXT_REQUIRED_ACTION.upper(), banned


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rc1.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento", "dotenv", "smtplib"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
