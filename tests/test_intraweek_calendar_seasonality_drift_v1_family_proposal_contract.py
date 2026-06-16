"""Tests for the Candidate #10 family proposal contract
(INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the NINE-record ledger (C1-C9) + V5 + V4 + V3
+ V2 + Recommendation V1 + Autopilot Loop V1 + the pushed Overnight
Autopilot Next-Candidate Proposal Drafter; V5 blacklist clearance;
single-symbol BTCUSD 1d long-only; single deterministic calendar
weekday trigger (the C9 single-trigger lesson); explicit edge argument
beyond pattern geometry (the C8 lesson); joint/intersection-trigger
sample-size pre-justification field (the C9 lesson); proposal-level
anti-cluster + sample-size adequacy + explicit-edge-argument +
joint-trigger-pre-justification policies all locked and NOT the edit
token; 27/81 bps fee + floor; human review required at every gate;
the embedded flat draft certifies against the pushed drafter's
validate_c10_proposal_draft; all downstream capability flags False;
AST/purity green."""

from __future__ import annotations

import ast
import copy
import inspect
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract as c10p
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_autopilot_next_candidate_proposal_drafter_contract as drafter
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4
import sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract as bl5

# Build the deep-chain Candidate #10 record ONCE; every test reuses a
# deep copy. The build is computationally expensive (it rebuilds the
# full upstream chain incl. the drafter), so rebuilding per assertion
# is prohibitively slow. Tampering tests mutate an independent deep
# copy and call the (fast, pure) validator, which exercises the same
# safety coverage without another chain rebuild.
# The shared build_* contract gates (C10 sub-gates + the V5/V4/V3 rejected-
# family blacklists, the C9/C8/C7 dry-run-review chains, Overnight Autopilot
# V2, Recommendation V1, the Autopilot Loop, and the proposal drafter) are NOT
# memoized in production, so the chain is re-evaluated EXPONENTIALLY (each gate
# re-runs its predecessors in full). For the SINGLE record build below we wrap
# every zero-argument build_* gate (and the _recompute_live_dry_run leaves)
# across all loaded sparta_commander modules in a once-per-original, deepcopy-
# returning cache, so each unique gate is computed EXACTLY ONCE -> the tree
# collapses to linear. All monkeypatches are restored in the finally. Gates are
# pure + deterministic, so the built record is IDENTICAL and every caller still
# gets an independent deep copy; production code is untouched; arg-taking
# builds pass straight through, never cached.
def _install_pure_gate_memoization():
    cache: dict = {}
    wrappers: dict = {}
    restore: list = []

    def _make(orig):
        def _wrapped(*args, **kwargs):
            if args or kwargs:
                return orig(*args, **kwargs)
            oid = id(orig)
            if oid not in cache:
                cache[oid] = orig()
            return copy.deepcopy(cache[oid])
        return _wrapped

    def _is_target(fn) -> bool:
        return inspect.isfunction(fn) and (
            fn.__name__.startswith("build_")
            or fn.__name__ == "_recompute_live_dry_run")

    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _orig in list(vars(_mod).values()):
            if _is_target(_orig) and id(_orig) not in wrappers:
                wrappers[id(_orig)] = _make(_orig)
    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _attr, _val in list(vars(_mod).items()):
            if inspect.isfunction(_val) and id(_val) in wrappers:
                restore.append((_mod, _attr, _val))
                setattr(_mod, _attr, wrappers[id(_val)])
    return restore


_memo_restore = _install_pure_gate_memoization()
try:
    _R = c10p.build_candidate_10_family_proposal()
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


def _record():
    return copy.deepcopy(_R)


# ---- chain gate + ready verdict -------------------------------------------

def test_proposal_ready_and_chain_gates_all_certify():
    # The shared build already chain-gated every upstream contract;
    # its embedded verdict fields are the live results of those builds,
    # so asserting on them covers upstream certification without
    # rebuilding each (deep) contract again.
    record = _record()
    assert record["v5_blacklist_verdict"] == bl5.VERDICT_BL5_READY
    assert record["v4_blacklist_verdict"] == bl4.VERDICT_BL4_READY
    assert record["v3_blacklist_verdict"] == bl3.VERDICT_BL3_READY
    assert record["v2_verdict"] == oap2.VERDICT_OAP2_READY
    assert record["recommendation_verdict"] == rec.VERDICT_CR_READY
    assert record["autopilot_loop_verdict"] == ap.VERDICT_AP_READY
    assert record["drafter_verdict"] == drafter.VERDICT_DRAFTER_READY
    assert record["verdict"] == c10p.VERDICT_C10P_READY
    assert record["blockers"] == []
    assert c10p.validate_candidate_10_family_proposal(
        record)["valid"] is True


def test_nine_record_ledger_intact():
    record = _record()
    assert record["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    # One real rebuild with a single ledger entry broken proves the
    # nine-record gate blocks (the build's gate uses all(... ==
    # REJECTED_KEPT_ON_RECORD), so any single broken entry trips it).
    # Restoration is witnessed by the shared READY record _R, so no
    # second deep rebuild is needed.
    mod = c10p
    original = mod.C1_STATUS
    try:
        mod.C1_STATUS = "APPROVED_FOR_TRADING"
        record = mod.build_candidate_10_family_proposal()
        assert record["verdict"] == c10p.VERDICT_C10P_BLOCKED
        assert "nine_record_ledger_broken" in record["blockers"]
        assert record["ledger_all_rejected_kept_on_record"] is False
    finally:
        mod.C1_STATUS = original
    assert _R["verdict"] == c10p.VERDICT_C10P_READY


# ---- V5 blacklist clearance ----------------------------------------------

def test_v5_blacklist_clearance_and_upstream_certification():
    record = _record()
    assert record["v5_blacklist_clearance"] is True
    assert record["v5_blacklist_verdict"] == bl5.VERDICT_BL5_READY
    assert record["v4_blacklist_verdict"] == bl4.VERDICT_BL4_READY
    assert record["v3_blacklist_verdict"] == bl3.VERDICT_BL3_READY
    assert record["v2_verdict"] == oap2.VERDICT_OAP2_READY
    assert record["recommendation_verdict"] == rec.VERDICT_CR_READY
    assert record["autopilot_loop_verdict"] == ap.VERDICT_AP_READY
    assert record["drafter_verdict"] == drafter.VERDICT_DRAFTER_READY


def test_family_name_not_in_any_rejected_tuple():
    record = _record()
    family = record["candidate_family"]
    assert family == "intraweek_calendar_seasonality_drift"
    assert family not in bl5.REJECTED_FAMILY_LOGIC_BLACKLIST_V5
    assert family not in bl4.REJECTED_FAMILY_LOGIC_BLACKLIST_V4
    assert family not in bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3
    assert family not in oap2.REJECTED_FAMILY_LOGIC_BLACKLIST
    assert family not in ap.REJECTED_FAMILIES
    assert family not in rec.ALL_REJECTED_FAMILIES


# ---- universe / timeframe / direction / sample window --------------------

def test_universe_timeframe_direction_sample_window_locked():
    record = _record()
    assert record["symbols"] == ["BTCUSD"]
    assert record["timeframe"] == "1d"
    assert record["direction"] == "long_only"
    assert record["sample_window_proposal"] == "2019-01-01_2025-12-31"
    for field, value in (("symbols", ["BTCUSD", "ETHUSD"]),
                         ("symbols", []),
                         ("timeframe", "1h"),
                         ("timeframe", "15m"),
                         ("direction", "long_or_short"),
                         ("direction", "short_only"),
                         ("sample_window_proposal", "2025-01-01")):
        tampered = _record()
        tampered[field] = value
        assert c10p.validate_candidate_10_family_proposal(
            tampered)["valid"] is False, (field, value)


# ---- explicit edge argument beyond pattern geometry (V5-required) -------

def test_explicit_edge_argument_beyond_pattern_geometry_present():
    record = _record()
    edge = record["explicit_edge_argument_beyond_pattern_geometry"]
    assert len(edge) > 1000
    assert "CALENDAR RISK PREMIUM" in edge
    assert "ORTHOGONAL TO C1-C9" in edge
    assert "27 BPS + 81 BPS" in edge or "27 bps" in edge.lower()
    assert "SINGLE-TRIGGER" in edge
    assert "FALSIFIABILITY" in edge
    for token in ("calendar", "weekday", "liquidity", "flow",
                  "orthogonal"):
        assert token in edge.lower(), token
    tampered = _record()
    tampered["explicit_edge_argument_beyond_pattern_geometry"] = (
        "just a chart pattern")
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


def test_explicit_edge_argument_policy_locked_and_not_edit_token():
    policy = _record()["explicit_edge_argument_policy"]
    assert policy["built_in_at_proposal_time"] is True
    assert policy["v5_required_field"] is True
    assert policy["argument_is_a_calendar_risk_premium_not_visual"] is True
    assert policy[
        "argument_is_orthogonal_to_all_price_and_volume_conditions"
    ] is True
    assert policy["is_not_the_single_allowed_c10_edit"] is True
    tampered = _record()
    tampered["explicit_edge_argument_policy"][
        "is_not_the_single_allowed_c10_edit"] = False
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


def test_edge_source_hypothesis_frozen():
    record = _record()
    eh = record["edge_source_hypothesis"]
    assert "weekly flow cycle" in eh.lower()
    assert "calendar" in eh.lower()
    assert "exogenous time" in eh.lower()
    assert "27 bps" in eh.lower() and "81 bps" in eh.lower()


# ---- joint/intersection-trigger sample-size pre-justification (C9) ------

def test_joint_trigger_pre_justification_field_present():
    record = _record()
    pj = record[
        "joint_or_intersection_trigger_sample_size_pre_justification"]
    assert "NOT APPLICABLE BY DESIGN" in pj
    assert "SINGLE" in pj
    assert "no intersection" in pj.lower()
    assert "hundreds" in pj.lower()
    tampered = _record()
    tampered[
        "joint_or_intersection_trigger_sample_size_pre_justification"
    ] = "n/a"
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


def test_joint_trigger_pre_justification_policy_locked_not_edit_token():
    policy = _record()["joint_trigger_pre_justification_policy"]
    assert policy["design_is_single_deterministic_trigger"] is True
    assert policy["no_intersection_of_trigger_conditions"] is True
    assert policy["intersection_sparsity_failure_cannot_occur"] is True
    assert policy["is_not_the_single_allowed_c10_edit"] is True
    tampered = _record()
    tampered["joint_trigger_pre_justification_policy"][
        "is_not_the_single_allowed_c10_edit"] = False
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


# ---- material differences from all 9 rejected families ------------------

def test_material_differences_from_each_rejected_family():
    record = _record()
    diff = record["difference_from_rejected_families"]
    for label in ("ny_session_fvg_choch_v3",
                  "crypto_intraday_breakout_pullback_structure_v2",
                  "btc_sol_long_trend_continuation_v1",
                  "sol_btc_long_1h_swing_structure",
                  "eth_sol_relative_strength_pullback_continuation_v1",
                  "multi_symbol_relative_strength_rotation_filter",
                  "volatility_compression_expansion",
                  "liquidity_sweep_mean_reversion",
                  "low_volume_downside_capitulation_mean_reversion"):
        assert label in diff, label
    assert "calendar" in diff.lower()
    assert "exogenous calendar risk premium" in diff.lower()


def test_differentiation_dict_addresses_all_nine_v5_labels():
    record = _record()
    d = record["differentiation_from_each_rejected_family"]
    assert set(d.keys()) == set(bl5.REJECTED_FAMILY_LOGIC_BLACKLIST_V5)
    for label, text in d.items():
        assert isinstance(text, str) and text.strip(), label


def test_explicit_non_reuse_of_rejected_family_logic_covers_c1_c9():
    nonreuse = _record()[
        "explicit_non_reuse_of_rejected_family_logic"]
    assert "no C1-C9 setup_ids" in nonreuse
    assert "ny-session" in nonreuse.lower()
    assert "range-breakout" in nonreuse.lower()
    assert "trend-continuation" in nonreuse.lower()
    assert "swing-pivot" in nonreuse.lower()
    assert "relative-strength" in nonreuse.lower()
    assert "rotation filter" in nonreuse.lower()
    assert "atr contraction" in nonreuse.lower()
    assert "sweep-below-prior-low" in nonreuse.lower()
    assert "volume condition" in nonreuse.lower()


# ---- locked fee / floor / anti-cluster / sample-size / human-review -----

def test_fee_and_floor_locked_27_and_81_bps():
    fee = _record()["fee_aware_geometry_policy"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 26, 28, 50, 100):
        tampered = _record()
        tampered["fee_aware_geometry_policy"]["fee_model_round_trip"
                                              "_bps"] = value
        assert c10p.validate_candidate_10_family_proposal(
            tampered)["valid"] is False, value
    for value in (0, 27, 80, 82, 162):
        tampered = _record()
        tampered["fee_aware_geometry_policy"][
            "minimum_gross_target_distance_floor_bps"] = value
        assert c10p.validate_candidate_10_family_proposal(
            tampered)["valid"] is False, value


def test_anti_cluster_policy_proposal_locked_not_edit_token():
    policy = _record()["anti_cluster_policy"]
    assert policy["built_in_at_label_emission_time"] is True
    assert policy[
        "scope"] == "per_symbol_one_fire_per_iso_week_plus_minimum_bar_gap"
    assert policy["calendar_is_the_primary_anti_cluster_constraint"] is True
    assert policy["is_not_the_single_allowed_c10_edit"] is True
    assert policy["applies_before_replay_time_non_overlap"] is True
    assert policy["replay_time_non_overlap_unchanged"] is True
    tampered = _record()
    tampered["anti_cluster_policy"][
        "is_not_the_single_allowed_c10_edit"] = False
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


def test_sample_size_adequacy_policy_proposal_locked_not_edit_token():
    policy = _record()["sample_size_adequacy_policy"]
    assert policy["built_in_at_proposal_time"] is True
    assert policy["applies_at_labels_review_gate"] is True
    assert policy[
        "below_threshold_triggers_structural_rejection_without_edit"
        "_token"] is True
    assert policy[
        "sample_is_abundant_by_construction_a_bucket_recurs_every_iso"
        "_week"] is True
    assert policy["is_not_the_single_allowed_c10_edit"] is True
    tampered = _record()
    tampered["sample_size_adequacy_policy"][
        "is_not_the_single_allowed_c10_edit"] = False
    assert c10p.validate_candidate_10_family_proposal(
        tampered)["valid"] is False


def test_edit_allowance_one_token_must_target_different_parameter():
    record = _record()
    edit = record["edit_allowance_policy"]
    assert "ONE pre-committed edit" in edit
    assert "REJECTED_KEPT_ON_RECORD" in edit
    assert "anti-cluster policy" in edit
    assert "sample-size adequacy" in edit
    assert "explicit-edge-argument field" in edit
    assert "joint-trigger" in edit
    assert "different structural parameter" in edit


def test_human_review_required_at_every_gate():
    record = _record()
    assert record["human_review_required"] is True
    assert record["human_review_required_at_every_gate"] is True
    assert record["plan_is_not_a_promotion"] is True
    assert record["no_promotion_no_paper_no_live"] is True
    for key in ("human_review_required",
                "human_review_required_at_every_gate",
                "plan_is_not_a_promotion",
                "no_promotion_no_paper_no_live"):
        tampered = _record()
        tampered[key] = False
        assert c10p.validate_candidate_10_family_proposal(
            tampered)["valid"] is False, key


# ---- single deterministic calendar trigger / exit -----------------------

def test_trigger_family_is_single_deterministic_calendar():
    trigger = _record()["trigger_family"]
    assert trigger["name"] == "intraweek_calendar_weekday_bucket_event"
    assert "iso weekday" in trigger["definition"].lower()
    assert "NO price-pattern" in trigger["definition"]
    assert trigger["is_a_single_deterministic_calendar_trigger"] is True
    assert trigger["uses_no_price_pattern_condition"] is True
    assert trigger["uses_no_volume_condition"] is True
    assert trigger["uses_no_statistical_excursion_condition"] is True
    assert trigger["is_not_a_cross_symbol_rs_filter"] is True
    assert trigger["is_not_a_session_anchored_structure_trigger"] is True
    assert trigger["is_not_a_breakout_pullback_trigger"] is True
    assert trigger["is_not_a_trend_ma_filter"] is True
    assert trigger["is_not_a_swing_pivot_trigger"] is True
    assert trigger["is_not_an_atr_contraction_expansion_trigger"] is True
    assert trigger["is_not_a_relative_strength_rotation_trigger"] is True
    assert trigger["is_not_a_sweep_reclaim_trigger"] is True
    assert trigger["is_not_a_volume_conditioned_excursion_trigger"] is True
    assert trigger["uses_completed_daily_bars_only"] is True
    assert trigger["no_future_bars"] is True
    assert trigger["no_same_bar_lookahead"] is True
    assert trigger["no_intrabar_entry"] is True


def test_exit_family_fixed_horizon_with_structural_stop():
    exit_f = _record()["exit_family"]
    assert "fixed-horizon" in exit_f["rule"]
    assert exit_f["never_tightened_after_entry"] is True
    assert exit_f["stop_must_be_below_entry"] is True
    assert exit_f["invalid_if_stop_distance_not_positive"] is True


def test_target_variants_2r_3r_4r():
    targets = _record()["target_policy"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    assert targets["no_new_variants_after_label_freeze"] is True


# ---- embedded flat draft certifies against the pushed drafter -----------

def test_embedded_draft_certifies_against_pushed_drafter():
    record = _record()
    draft = record["c10_draft"]
    assert isinstance(draft, dict)
    dv = drafter.validate_c10_proposal_draft(draft)
    assert dv["valid"] is True, dv["errors"]
    standalone = drafter.validate_c10_proposal_draft(c10p.get_c10_draft())
    assert standalone["valid"] is True, standalone["errors"]


def test_draft_has_all_eighteen_v5_required_fields_filled():
    draft = c10p.get_c10_draft()
    for field in bl5.C10_PROPOSAL_REQUIREMENTS["required_fields"]:
        assert field in draft, field
        assert draft[field] not in (None, "", drafter.PLACEHOLDER_HUMAN_FILL)
    assert draft["fee_assumption_round_trip_bps"] == 27
    assert draft["minimum_gross_target_distance_floor_bps"] == 81
    assert draft["human_review_required_at_every_gate"] is True
    assert draft["no_promotion_no_paper_no_live"] is True


def test_draft_next_human_gate_has_no_banned_tokens():
    draft = c10p.get_c10_draft()
    gate = draft["next_human_gate"].upper()
    for banned in drafter.BANNED_TOKENS_IN_NEXT_HUMAN_GATE:
        assert banned not in gate, banned


# ---- proposal-only safety / capability flags ----------------------------

def test_proposal_only_with_all_downstream_locked():
    record = _record()
    assert record["is_proposal_only"] is True
    assert record["is_a_rescue_attempt"] is False
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("runs_spec_review_now", "runs_detector",
                "runs_real_candle_detection",
                "runs_real_detection_now", "runs_dry_run",
                "labels_now", "runs_replay", "runs_replay_now",
                "runs_relabel", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "uses_external_data_source",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c10p.validate_candidate_10_family_proposal(
            tampered)["valid"] is False, key


def test_label_and_next_required_action():
    record = _record()
    assert record["candidate_family"] == (
        "intraweek_calendar_seasonality_drift")
    assert record["candidate_id"] == (
        "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1")
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_10_SPEC_REVIEW")
    assert record["next_loop_stage"] == "candidate_spec"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c10p.NEXT_REQUIRED_ACTION.upper(), banned
    assert c10p.get_candidate_10_proposal_label() == c10p.C10P_LABEL
    assert c10p.C10P_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "PROPOSAL GATE ONLY",
                   "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY",
                   "SINGLE-TRIGGER", "NOT A RESCUE", "NOT A CLAIM"):
        assert phrase in c10p.C10P_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c10p.C10P_LABEL.upper(), (
            banned_phrase)


# ---- safety claims + seeds never rescue ----------------------------------

def test_safety_and_no_claim_complete():
    safety = _record()["safety_and_no_claim"]
    joined = " || ".join(safety)
    for required in ("no trading", "no paper trading",
                     "no live trading",
                     "no wallet, account, api, or order capability",
                     "no auto-push, no auto-commit",
                     "no scheduler activation",
                     "no profitability claim and no winner wording",
                     "every stage requires evidence freeze and "
                     "explicit human gates"):
        assert required in joined, required


def test_seeds_are_inspiration_never_rescue():
    record = _record()
    assert record["seeds_are_never_rescue_paths"] is True
    seeds = " || ".join(record["seed_usage"])
    assert "c6_clustering_lesson_is_inspiration" in seeds
    assert "c7_sample_size_adequacy_lesson_is_inspiration" in seeds
    assert "c8_explicit_edge_argument_lesson_is_inspiration" in seeds
    assert "c9_intersection_sparsity_lesson_is_inspiration" in seeds
    assert ("the_calendar_weekday_index_is_a_new_exogenous_input_that"
            "_c1_through_c9_did_not_consume") in seeds
    assert ("no_c1_c9_setup_ids_replay_rows_labels_edited_labels_or"
            "_replay_results_may_be_reused") in seeds


def test_rationale_paragraph_mentions_c1_c9_and_calendar():
    rationale = _record()["rationale_paragraph"]
    assert "c1-c9" in rationale.lower() or "C1-C9" in rationale
    assert "calendar weekday index" in rationale.lower()
    assert "exogenous" in rationale.lower()
    assert "single-trigger" in rationale.lower()
    assert "fee-honest" in rationale.lower() or (
        "fee-aware" in rationale.lower())


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c10p.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
