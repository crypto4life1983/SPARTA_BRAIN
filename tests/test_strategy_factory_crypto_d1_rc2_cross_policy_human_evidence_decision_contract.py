"""Tests for the Crypto-D1 V2 RC2 Cross-Policy HUMAN EVIDENCE Decision Contract
(READ-ONLY).

Every decision consumed here is a FAKE in-memory dict (or one derived under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract records a human's decision
over RC2 cross-policy evidence as research only, never selects a successor policy, and
never promotes anything to execution."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract as hd
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract as rv

_WINDOW_IDS = [
    ("OOS_W1_2020_early_held_out", "held_out_early_history"),
    ("OOS_W2_2021H2_2022H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W3_2022H2_2023H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W4_2024H2_2025H1_straddle", "boundary_straddling_robustness"),
]


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe):
    window_results = []
    for wid, wtype in _WINDOW_IDS:
        window_results.append({
            "window_id": wid, "window": "2020-01-01..2020-08-10", "window_type": wtype,
            "symbols": ["BTC", "ETH"], "evaluated": True,
            "metrics": {
                "total_return": mean_ret, "max_drawdown": worst_dd,
                "sharpe_ratio": mean_sharpe, "real_orders_placed": 0,
                "num_kill_events": 0, "num_resume_events": 0, "halted_at_end": False,
            },
        })
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "window_results": window_results,
        "aggregate": {
            "windows_evaluated": 4, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _replay_report(*, complete=True):
    """A fake Block 185 report mirroring the committed real evidence (RP6 flipped)."""
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rp._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rp.VERDICT_REPLAYS_COMPLETE if complete else rp.VERDICT_BLOCKED_NOT_READY,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "policy_parameters_changed": False,
        "policy_results": [
            _policy("RP1_wait_7d_trend_on", mean_ret=0.4089, worst_dd=-0.4141, mean_sharpe=1.43),
            _policy("RP2_wait_14d_trend_on", mean_ret=0.3404, worst_dd=-0.4141, mean_sharpe=1.36),
            _policy("RP3_wait_30d_trend_on", mean_ret=0.3002, worst_dd=-0.4147, mean_sharpe=1.31),
            _policy("RP4_breadth_2of3_above_sma200", mean_ret=0.4206, worst_dd=-0.4141, mean_sharpe=1.43),
            _policy("RP5_half_then_full_on_confirmation", mean_ret=0.4187, worst_dd=-0.4140, mean_sharpe=1.44),
            _policy("RP6_resume_after_volatility_cools", mean_ret=0.2767, worst_dd=-0.4535, mean_sharpe=1.28),
        ],
        "rankings": {
            "best_by_mean_return": "RP4_breadth_2of3_above_sma200",
            "best_by_worst_drawdown": "RP5_half_then_full_on_confirmation",
            "best_by_mean_sharpe": "RP5_half_then_full_on_confirmation",
        },
        "leader_stability": {
            "rc1_leader_policy_id": "RP6_resume_after_volatility_cools",
            "categories_led_by_rc1_leader": [],
            "rc1_leader_leads_all_categories": False,
            "rc1_leader_leads_any_category": False,
        },
        "risk_notes": [], "files_read": [], "files_written": [],
    })
    return rep


def _review_decision(**kwargs):
    """A valid Block 186 reviewer decision derived from a fake replay report."""
    d = rv.review_rc2_cross_policy_results(_replay_report(**kwargs))
    d["rc2_replay_report_found"] = True
    d["rc2_replay_report_path"] = (
        "reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json"
    )
    return d


# --------------------------------------------------------------------------- #
# the real outcome -> RECORDED, DO NOT PROMOTE, RC3 direction, acknowledgments
# --------------------------------------------------------------------------- #
def test_records_decision_do_not_promote_with_rc3_direction():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["selected_research_direction"] == (
        "CONTINUE_RESEARCH_VIA_RC3_FAILURE_MODE_CHARACTERIZATION"
    )
    assert d["next_required_action"] == (
        "HUMAN_APPROVED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH"
    )
    assert d["blockers"] == []


def test_decision_acknowledges_flip_and_strongest_evidence():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    notes = d["risk_notes"]
    assert "acknowledged_rc2_reviewed_fixed_candidates_over_same_oos_windows" in notes
    assert (
        "acknowledged_rc1_leader_failed_oos_leadership:RP6_resume_after_volatility_cools"
        in notes
    )
    assert "acknowledged_rc1_leader_led_zero_categories" in notes
    assert "acknowledged_strongest_oos_evidence:RP4_breadth_2of3_above_sma200" in notes
    assert "acknowledged_strongest_oos_evidence:RP5_half_then_full_on_confirmation" in notes
    assert "strongest_policies_are_evidence_only_not_selected_successors" in notes
    assert "selecting_a_successor_from_the_same_windows_risks_repeating_overfit" in notes
    assert "promotion_requires_separate_explicit_human_command" in notes
    # the reviewer's own notes are carried forward
    assert any(n.startswith("review_note:") for n in notes)


def test_decision_never_selects_successors():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    assert d["successors_selected"] is False
    assert sorted(d["strongest_evidence_policies"]) == [
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
    ]


def test_decision_records_reason_and_rc3_question():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    assert "RC3" in d["decision_reason"]
    assert "failure modes" in d["rc3_research_question"]


# --------------------------------------------------------------------------- #
# direction handling
# --------------------------------------------------------------------------- #
def test_each_allowed_direction_is_accepted():
    for direction in hd.ALLOWED_DIRECTIONS:
        d = hd.record_rc2_cross_policy_human_evidence_decision(
            _review_decision(), selected_direction=direction
        )
        assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
        assert d["selected_research_direction"] == direction


def test_invalid_direction_blocks():
    d = hd.record_rc2_cross_policy_human_evidence_decision(
        _review_decision(), selected_direction="PROMOTE_RP5_NOW"
    )
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert any(b.startswith("invalid_selected_direction:") for b in d["blockers"])
    assert d["selected_research_direction"] is None
    # even a bad request keeps the decision DO_NOT_PROMOTE and selects nothing
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["successors_selected"] is False


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_review_decision_blocks():
    d = hd.record_rc2_cross_policy_human_evidence_decision(None)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc2_results_review_decision_missing" in d["blockers"]
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_incomplete_review_blocks():
    rd = _review_decision(complete=False)
    d = hd.record_rc2_cross_policy_human_evidence_decision(rd)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc2_results_review_not_complete" in d["blockers"]


def test_report_not_found_blocks():
    rd = _review_decision()
    rd["rc2_replay_report_found"] = False
    d = hd.record_rc2_cross_policy_human_evidence_decision(rd)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc2_replay_report_missing" in d["blockers"]


def test_invalid_review_decision_blocks():
    rd = _review_decision()
    rd["micro_live_gate_locked"] = False  # breaks Block 186's own validator
    d = hd.record_rc2_cross_policy_human_evidence_decision(rd)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc2_results_review_decision_invalid" in d["blockers"]


def test_review_with_promote_decision_blocks():
    rd = _review_decision()
    rd["promotion_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    d = hd.record_rc2_cross_policy_human_evidence_decision(rd)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "review_promotion_decision_not_do_not_promote" in d["blockers"]


# --------------------------------------------------------------------------- #
# the decision unlocks nothing
# --------------------------------------------------------------------------- #
def test_decision_unlocks_nothing():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_replay", "runs_simulation", "runs_backtest",
        "runs_optimization", "ran_parameter_search", "parameters_changed_based_on_results",
        "fetches_data", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "authorizes_paper_execution",
        "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
        "promotes_resume_policy", "unlocks_downstream_gate",
    ):
        assert d[key] is False, key


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rc2_cross_policy_replay_report.json").write_text(
        json.dumps(_replay_report()), encoding="utf-8"
    )
    d = hd.build_rc2_cross_policy_human_evidence_decision(repo_root=str(tmp_path))
    assert d["rc2_replay_report_found"] is True
    assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
    assert d["results_review_verdict"] == rv.VERDICT_RC2_REVIEW_COMPLETE


def test_build_handles_missing_local_report(tmp_path):
    d = hd.build_rc2_cross_policy_human_evidence_decision(repo_root=str(tmp_path))
    assert d["rc2_replay_report_found"] is False
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_recorded():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    assert hd.validate_rc2_cross_policy_human_evidence_decision(d)["valid"] is True


def test_validate_passes_on_blocked():
    d = hd.record_rc2_cross_policy_human_evidence_decision(None)
    assert hd.validate_rc2_cross_policy_human_evidence_decision(d)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["micro_live_gate_locked"] = False
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_selected_successor():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["successors_selected"] = True
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("successor_policy_marked_selected" in e for e in v["errors"])


def test_validate_rejects_marked_approved():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["approved_for_execution"] = True
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("decision_marked_approved" in e for e in v["errors"])


def test_validate_rejects_recorded_without_direction():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["selected_research_direction"] = None
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("recorded_without_valid_direction" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    d["runs_replay"] = True
    v = hd.validate_rc2_cross_policy_human_evidence_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = hd.render_rc2_cross_policy_human_evidence_decision_markdown(
        hd.record_rc2_cross_policy_human_evidence_decision(_review_decision())
    )
    assert md.startswith("# Crypto-D1 V2 RC2 Cross-Policy Human Evidence Decision")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "CONTINUE_RESEARCH_VIA_RC3_FAILURE_MODE_CHARACTERIZATION" in md
    assert "Successors selected: False" in md
    assert "NOT selected successors" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert (
        hd.get_rc2_cross_policy_human_evidence_decision_label() == hd.HUMAN_EVIDENCE_LABEL
    )
    assert "READ-ONLY" in hd.HUMAN_EVIDENCE_LABEL
    assert hd.HUMAN_EVIDENCE_MODE == "RESEARCH_ONLY"
    assert hd.allowed_directions() == hd.ALLOWED_DIRECTIONS


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in hd.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_or_credential_modules():
    with open(hd.__file__, "r", encoding="utf-8") as fh:
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
