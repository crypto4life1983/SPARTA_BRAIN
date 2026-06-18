"""Tests for the SPARTA Research Expansion Plan v1 PURE PLANNER contract.

Verifies: the plan is research-only, pure-planner-only, and executes nothing;
the 6-stage gate sequence is preserved unchanged with the real-data gates kept
human-gated; the C14 lesson is operationalized (durability weighted ABOVE
timing) so a durable idea outranks a timing-only idea; anti-loop refuses
rejected families / not-materially-different / parameter-only tweaks; the full
C1-C14 (19) rejected ledger + lessons are carried as learning data; the
portfolio objective is DECLARED not computed; overnight batching is planner-only
(builds/commits/pushes nothing); every capability flag + scope lock; validator
anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.research_expansion_plan_v1_contract as rep


_R = rep.build_research_expansion_plan(".", [])


# ---- core: research-only, pure planner, validates --------------------------

def test_plan_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_planner_only"] is True
    assert rep.validate_research_expansion_plan(_R)["valid"] is True


def test_gate_sequence_preserved_unchanged():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["gate_sequence_preserved_unchanged"] is True
    for stage in ("real_candle_labels_review", "fee_honest_replay_review"):
        assert stage in _R["real_data_stages"]
    bad = dict(_R)
    bad["gate_sequence"] = ["candidate_spec", "family_proposal"]
    assert rep.validate_research_expansion_plan(bad)["valid"] is False


# ---- C14 lesson operationalized: durability above timing -------------------

def test_durability_weighted_above_timing():
    pw = _R["priority_weights"]
    assert pw["durability_proxy"] > pw["timing_signal_proxy"]
    assert _R["durability_weighted_above_timing"] is True
    assert _R["c14_lesson"]
    assert "buy-and-hold" in _R["c14_lesson"].lower()
    assert "forward-oos" in _R["c14_lesson"].lower()
    bad = dict(_R)
    bad["priority_weights"] = {"durability_proxy": 0.1, "timing_signal_proxy": 0.9}
    assert rep.validate_research_expansion_plan(bad)["valid"] is False


def test_durable_idea_outranks_timing_only_idea():
    # idea A: a C14-style timing-only signal (beats random, weak durability).
    timing_only = {
        "family": "new_timing_only_axis", "distinct_edge_axis": True,
        "materially_different_from_all_rejected": True,
        "durability_proxy": 0.1, "timing_signal_proxy": 0.95,
        "portfolio_fit": {"expected_low_correlation": True,
                          "capital_efficiency_proxy": 0.5,
                          "regime_breadth_proxy": 0.5},
    }
    # idea B: durable axis (expected to beat B&H + forward-OOS), modest timing.
    durable = {
        "family": "new_durable_axis", "distinct_edge_axis": True,
        "materially_different_from_all_rejected": True,
        "durability_proxy": 0.9, "timing_signal_proxy": 0.3,
        "portfolio_fit": {"expected_low_correlation": True,
                          "capital_efficiency_proxy": 0.5,
                          "regime_breadth_proxy": 0.5},
    }
    sa = rep.score_candidate_idea(timing_only)
    sb = rep.score_candidate_idea(durable)
    assert sa["buildable"] and sb["buildable"]
    assert sb["priority_score"] > sa["priority_score"]
    ranked = rep.rank_candidate_ideas([timing_only, durable])
    assert ranked[0]["family"] == "new_durable_axis"


# ---- anti-loop -------------------------------------------------------------

def test_anti_loop_refuses_rejected_family():
    for fam in ("cointegration_pairs_market_neutral",      # C16
                "slow_vol_targeted_time_series_momentum",  # C15
                "conviction_bar_follow_through", "lead_lag_propagation_continuation",
                "intraweek_calendar_seasonality_drift"):
        s = rep.score_candidate_idea({
            "family": fam, "distinct_edge_axis": True,
            "materially_different_from_all_rejected": True,
            "durability_proxy": 0.9})
        assert s["buildable"] is False
        assert s["reason"] == "family_in_rejected_ledger_C1_to_C16"


def test_anti_loop_requires_material_difference():
    s = rep.score_candidate_idea({
        "family": "brand_new", "distinct_edge_axis": True,
        "materially_different_from_all_rejected": False,
        "durability_proxy": 0.9})
    assert s["buildable"] is False
    assert s["reason"] == "not_materially_different_from_all_rejected"


def test_anti_loop_penalizes_param_only():
    s = rep.score_candidate_idea({
        "family": "brand_new_v2", "distinct_edge_axis": True,
        "materially_different_from_all_rejected": True,
        "is_param_only_modification": True, "durability_proxy": 0.9})
    assert s["buildable"] is False
    assert s["reason"] == "parameter_only_modification_not_buildable"


def test_anti_loop_requires_distinct_edge_axis():
    s = rep.score_candidate_idea({
        "family": "brand_new_v3",
        "materially_different_from_all_rejected": True,
        "distinct_edge_axis": False, "durability_proxy": 0.9})
    assert s["buildable"] is False
    assert s["reason"] == "no_distinct_edge_axis"


# ---- rejected ledger + lessons (learning data) -----------------------------

def test_rejected_ledger_has_19_families_including_c14():
    # the FROZEN historical C1-C14 ledger (referenced by the pushed C15 chain)
    led = _R["rejected_families_c1_to_c14"]
    assert len(led) == 19
    for fam in ("intraweek_calendar_seasonality_drift",
                "cross_asset_dispersion_reversion",
                "failed_breakdown_reclaim_reversal",
                "lead_lag_propagation_continuation",
                "conviction_bar_follow_through"):
        assert fam in led
    assert "single_bar_conviction_continuation" in _R["rejected_family_lessons"]


def test_current_rejected_ledger_is_22_including_c17():
    # the CURRENT canonical ledger used for forward anti-loop now includes C17
    cur = _R["rejected_families_current"]
    assert len(cur) == 22
    assert _R["rejected_families_count"] == 22
    assert "risk_adjusted_portfolio_construction_vol_targeted_allocation" in cur
    assert "cointegration_pairs_market_neutral" in cur
    assert "slow_vol_targeted_time_series_momentum" in cur
    assert "conviction_bar_follow_through" in cur
    assert ("risk_adjusted_portfolio_construction_vol_targeted_allocation"
            in _R["rejected_family_lessons"])
    # C15, C16 and C17 are all refused by the scorer's default anti-loop
    for fam in ("slow_vol_targeted_time_series_momentum",
                "cointegration_pairs_market_neutral",
                "risk_adjusted_portfolio_construction_vol_targeted_allocation"):
        s = rep.score_candidate_idea({
            "family": fam, "distinct_edge_axis": True,
            "materially_different_from_all_rejected": True, "durability_proxy": 0.9})
        assert s["buildable"] is False


# ---- portfolio objective: declared, not computed ---------------------------

def test_portfolio_objective_declared_not_computed():
    po = _R["portfolio_objective"]
    assert po["computed_in_this_contract"] is False
    assert po["prefer_low_correlation_to_existing_research"] is True
    for dim in ("trade_time_overlap", "regime_profile", "symbol_exposure",
                "holding_time_bars", "return_stream_correlation"):
        assert dim in po["tracked_dimensions"]
    bad = dict(_R)
    bad["portfolio_objective"] = dict(po, computed_in_this_contract=True)
    assert rep.validate_research_expansion_plan(bad)["valid"] is False


def test_portfolio_fit_blends_declared_proxies_only():
    hi = rep.portfolio_fit_score({"expected_low_correlation": True,
                                  "capital_efficiency_proxy": 1.0,
                                  "regime_breadth_proxy": 1.0})
    lo = rep.portfolio_fit_score({"expected_low_correlation": False,
                                  "capital_efficiency_proxy": 0.0,
                                  "regime_breadth_proxy": 0.0})
    assert hi == 1.0 and lo == 0.0


# ---- overnight batching: planner-only --------------------------------------

def test_overnight_batch_plan_builds_nothing():
    ideas = [
        {"family": "axis_a", "distinct_edge_axis": True,
         "materially_different_from_all_rejected": True,
         "durability_proxy": 0.9, "timing_signal_proxy": 0.4,
         "portfolio_fit": {"expected_low_correlation": True,
                           "capital_efficiency_proxy": 0.8,
                           "regime_breadth_proxy": 0.8}},
        {"family": "axis_b", "distinct_edge_axis": True,
         "materially_different_from_all_rejected": True,
         "durability_proxy": 0.4, "timing_signal_proxy": 0.9,
         "portfolio_fit": {"expected_low_correlation": True,
                           "capital_efficiency_proxy": 0.3,
                           "regime_breadth_proxy": 0.3}},
        {"family": "conviction_bar_follow_through",  # rejected -> skipped
         "distinct_edge_axis": True,
         "materially_different_from_all_rejected": True,
         "durability_proxy": 0.9},
    ]
    plan = rep.overnight_batch_plan(ideas, build_top_k=1)
    assert plan["generated_count"] == 3
    assert plan["buildable_count"] == 2
    assert plan["builds_anything_automatically"] is False
    assert plan["auto_commits"] is False and plan["auto_pushes"] is False
    assert plan["fetches_data"] is False
    assert plan["requires_human_approval_to_build_each_gate"] is True
    assert len(plan["selected_to_build"]) == 1
    assert plan["selected_to_build"][0]["family"] == "axis_a"
    assert plan["morning_report_summary"]["executes_nothing"] is True
    assert "conviction_bar_follow_through" in [
        s["family"] for s in plan["skipped_or_rejected"]]


def test_overnight_batch_top_k_clamped():
    plan = rep.overnight_batch_plan([], build_top_k=99)
    assert plan["build_top_k"] <= rep.OVERNIGHT_BATCHING["max_build_top_k"]
    assert plan["selected_to_build"] == []


# ---- capability flags + scope locks ----------------------------------------

def test_all_capability_flags_false_and_tamper_rejected():
    for flag in rep._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = dict(_R)
        bad[flag] = True
        assert rep.validate_research_expansion_plan(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_execute", "no_labels", "no_replay",
                 "no_data_fetch", "no_commit", "no_push", "no_paper_trading",
                 "no_live_trading", "no_broker", "no_gate_skip",
                 "no_rejected_family_repropose", "no_param_only_buildable"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_execution_token():
    label = rep.get_research_expansion_plan_label()
    assert "RESEARCH ONLY" in label
    assert "BUILDS NOTHING" in label
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = _R["next_required_action"]
    assert nra == "HUMAN_DECISION_ADOPT_RESEARCH_EXPANSION_PLAN_OR_AMEND"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rep.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
