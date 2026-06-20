"""Tests for the SPARTA Pipeline Audit v1 contract.

Proves the pipeline self-audit has real discriminating power before C21 fee-honest
replay: every audit category passes its known-GOOD fixture AND catches its known-BAD
injected fixture; the named known-truth scenarios behave exactly (winner passes, loser
fails, high-turnover fails after costs, low-turnover carry holds, exact fee bps, funding
applied to the correct side/time, lookahead trap caught, duplicate trap caught); the
C1-C20 failure-pattern summary is grounded in pinned lessons; the C21-specific hooks
hold; and the whole thing is read-only/research-only -- C21 unchanged, next gate still
the fee-honest replay decision, C20 rejected, C22 not started, no replay/paper/live
opened. Plus capability flags False, full scope locks, validator anti-tamper, and module
purity."""
from __future__ import annotations

import ast

import sparta_commander.sparta_pipeline_audit_v1_contract as a
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as lane


_R = a.build_pipeline_audit()


# ---- core: research-only, pure, validates ----------------------------------

def test_audit_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["audit_name"] == "SPARTA_PIPELINE_AUDIT_V1"
    assert _R["is_pure_audit_only"] is True
    assert _R["executes_nothing"] is True
    assert a.validate_pipeline_audit(_R)["valid"] is True


# ---- every category passes good + catches bad ------------------------------

def test_every_category_has_discriminating_power():
    cats = _R["category_results"]
    assert set(cats) == set(a.AUDIT_CATEGORIES)
    assert len(a.AUDIT_CATEGORIES) == 15
    for name, c in cats.items():
        assert c["correct_case_ok"] is True, "good case failed: %s" % name
        assert c["bad_case_caught"] is True, "bad case not caught: %s" % name
        assert c["pass"] is True, name
    assert _R["all_categories_pass"] is True


# ---- known-truth: winner passes, loser fails -------------------------------

def test_known_winner_passes_and_loser_fails():
    k = _R["known_truth_cases"]
    w = k["known_winner_passes"]
    assert w["net"] > 0 and w["passes"] is True
    loser = k["known_loser_fails"]
    assert loser["net"] <= 0 and loser["fails"] is True


# ---- known-truth: high-turnover fails after costs (C20 shape) --------------

def test_known_high_turnover_fails_after_costs():
    h = _R["known_truth_cases"]["known_high_turnover_fails_after_costs"]
    # gross is positive, but 704 round-trips x 74 bps drives net negative
    assert h["gross"] > 0
    assert h["cost"] == 704.0 * 74.0 / 10000.0
    assert h["net"] < 0
    assert h["fails_after_costs"] is True
    assert h["is_cost_driven"] is True


# ---- known-truth: low-turnover carry holds and avoids churn (C21 shape) ----

def test_known_low_turnover_carry_holds():
    c = _R["known_truth_cases"]["known_low_turnover_carry_holds"]
    assert c["turnover_ceiling"] == 6
    assert c["within_ceiling"] is True
    assert c["net"] > 0
    assert c["holds_and_avoids_churn"] is True


# ---- known-truth: exact fee bps deduction ----------------------------------

def test_known_fee_deducts_exact_bps():
    f = _R["known_truth_cases"]["known_fee_deducts_exact_bps"]
    # 100 round-trips x 37 bps = 0.37 fraction; net = 0.10 - 0.37 = -0.27
    assert abs(f["expected_cost"] - 0.37) < 1e-9
    assert abs(f["expected_net"] - (-0.27)) < 1e-9
    assert f["exact"] is True
    # direct check of the pure helper
    assert abs(a.expected_cost_fraction(100.0, 37.0) - 0.37) < 1e-9
    fee = a.audit_fee_deduction(0.10, 0.10, 100.0, 37.0)
    assert fee["ok"] is False and fee["missing_fee"] is True
    dbl = a.audit_fee_deduction(0.10, 0.10 - 0.74, 100.0, 37.0)
    assert dbl["ok"] is False and dbl["double_counted"] is True


# ---- known-truth: funding applied to correct side + time -------------------

def test_known_funding_correct_side_and_time():
    f = _R["known_truth_cases"]["known_funding_correct_side_and_time"]
    assert f["expected_pnl"] == 0.01 and f["correct"] is True
    # short-perp RECEIVES funding when the rate is positive (+); long-perp PAYS (-)
    assert a.expected_funding_pnl("short_perp", 0.01, 1.0) == 0.01
    assert a.expected_funding_pnl("long_perp", 0.01, 1.0) == -0.01
    # wrong side caught
    wrong = a.audit_funding_application("short_perp", 0.01, 1.0, -0.01, 5, 5)
    assert wrong["ok"] is False
    # future-bar funding (lookahead) caught
    future = a.audit_funding_application("short_perp", 0.01, 1.0, 0.01, 6, 5)
    assert future["ok"] is False and future["timing_ok"] is False


# ---- known-truth: lookahead + duplicate traps caught -----------------------

def test_known_lookahead_and_duplicate_traps_caught():
    la = _R["known_truth_cases"]["known_lookahead_trap_caught"]
    assert la["caught"] is True and 11 in la["offenders"]
    dup = _R["known_truth_cases"]["known_duplicate_trap_caught"]
    assert dup["caught"] is True and len(dup["duplicates"]) == 1
    # a clean (no-lookahead) decision is NOT flagged
    assert a.audit_lookahead(10, [8, 9, 10])["ok"] is True


# ---- direct bad-injection coverage for the remaining categories ------------

def test_direct_bad_injections_caught():
    assert a.audit_timestamp_alignment([1, 2, 3], [2, 3, 4])["ok"] is False
    assert a.audit_spot_perp_funding_alignment(
        [1, 2], [1, 2], [1, 3])["ok"] is False
    assert a.audit_trade_direction(
        {"spot": "long", "perp": "short"},
        {"spot": "long", "perp": "long"})["ok"] is False
    assert a.audit_position_sizing([0.5, 0.9], 1.4, 1.0)["ok"] is False
    assert a.audit_label_accept_reject(
        [{"truth_accept": True, "labeled_accept": False}])["ok"] is False
    assert a.audit_over_strict_rejection(
        [{"truth_accept": True, "labeled_accept": False}])["ok"] is False
    assert a.audit_benchmark_comparison(
        "net", "gross", "zero_baseline", "always_on_neutral_carry")["ok"] is False
    assert a.audit_no_hidden_optimization(
        {"p": 100.0}, {"p": 60.0})["ok"] is False
    # rescue of a rejected family is caught; the genuinely-new C21 family is allowed
    led = lane.REJECTED_FAMILIES_C1_TO_C20
    assert a.audit_no_rejected_family_rescue(
        "mechanically_neutral_spot_perp_basis_funding_carry", led)["ok"] is False
    assert a.audit_no_rejected_family_rescue(
        "low_turnover_same_asset_spot_perp_funding_carry", led)["ok"] is True


# ---- C1-C20 failure-pattern summary ----------------------------------------

def test_failure_ledger_audit_summary():
    fl = _R["failure_ledger_audit"]
    cands = fl["candidates_summarized"]
    assert cands == ["C%d" % n for n in range(10, 21)]   # C10..C20 pinned
    # classes present and reconciled
    cby = fl["count_by_failure_class"]
    assert sum(cby.values()) == len(cands)
    # the dominant repeated pattern is edge-driven (lost to B&H / OOS): C14/C15/C17/C18
    edge = set(fl["repeated_patterns"]["edge_driven_lost_to_buy_and_hold_or_oos"])
    assert {"C14", "C15", "C17", "C18"}.issubset(edge)
    # zero/low-setup + neutrality non-persistence: C13/C16/C19
    zls = set(fl["repeated_patterns"]["zero_or_low_setup_or_neutrality_non_persistence"])
    assert {"C13", "C16", "C19"}.issubset(zls)
    # cost-driven cluster includes C20 and is the part the fee audit verifies directly
    assert "C20" in fl["repeated_patterns"]["cost_or_turnover_driven"]
    assert "C20" in fl["cost_driven_cluster_verifiable_by_fee_audit"]
    # honesty: C1-C9 evidence is NOT pinned in the reused surfaces -> crosscheck flagged
    assert fl["early_candidates_c1_to_c9_evidence_pinned_in_reused_surfaces"] is False
    assert fl["early_candidates_crosscheck_recommended"] is True
    # every per-candidate entry carries a stage + class
    for e in fl["per_candidate"]:
        assert e["stage"] and e["failure_class"]


# ---- C21-specific audit hooks ----------------------------------------------

def test_c21_audit_hooks_hold_and_replay_not_started():
    h = _R["c21_audit_hooks"]
    assert h["candidate"] == "C21"
    assert len(h["detector_commit"]) == 40
    assert h["same_asset_spot_perp_alignment_required"] is True
    assert h["d1_funding_alignment_required"] is True
    assert h["no_beta_or_cointegration_hedge"] is True
    assert h["no_basis_z_or_drawdown_stop"] is True
    assert h["turnover_ceiling_round_trips_per_year_per_asset"] == 6
    assert h["turnover_ceiling_is_six"] is True
    assert h["always_on_carry_benchmark_required_for_replay"] is True
    assert h["replay_must_not_start_during_audit"] is True
    assert h["replay_started_during_audit"] is False


# ---- C21 unchanged + no replay/paper/live opened ---------------------------

def test_c21_unchanged_and_no_replay_paper_live():
    ls = lane.get_lane_status()
    # the audit was the pre-replay guardrail; C21 has since been rejected at replay
    assert _R["active_candidate"] is None
    assert ls["active_candidate"] is None
    assert _R["active_candidate_is_none"] is True
    assert _R["c21_now_rejected_at_replay"] is True
    assert _R["c21_rejection_was_edge_driven_not_artifact"] is True
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD")
    assert _R["next_is_c22_proposal_readiness"] is True
    assert _R["c20_remains_rejected"] is True
    assert _R["rejected_ledger_count"] == 26
    assert _R["c22_started"] is False
    assert _R["c21_replay_started"] is False
    # the audit itself opens NO execution permission
    for flag in ("runs_replay", "starts_c21_replay", "reruns_c21_labels",
                 "changes_c21_labels", "edits_c21_rules", "paper_trades",
                 "live_trades", "connects_broker", "places_orders", "rescues_c20",
                 "starts_c22", "fetches_data", "optimizes_parameters"):
        assert _R[flag] is False, flag


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in a._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert a.validate_pipeline_audit(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_replay", "no_start_c21_replay",
                 "no_rerun_c21_labels", "no_edit_c21_rules", "no_data_fetch",
                 "no_optimization", "no_rescue_c20", "no_start_c22",
                 "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- validator catches tampered audit results ------------------------------

def test_validator_catches_tampered_category_and_known_truth():
    # a category whose bad case is NOT caught must fail validation
    bad_cats = {k: dict(v) for k, v in _R["category_results"].items()}
    bad_cats["lookahead_leakage"] = {**bad_cats["lookahead_leakage"],
                                     "bad_case_caught": False}
    bad = {**_R, "category_results": bad_cats, "all_categories_pass": False}
    assert a.validate_pipeline_audit(bad)["valid"] is False
    # a tampered known-truth (loser marked as passing) must fail
    bad_k = {k: dict(v) for k, v in _R["known_truth_cases"].items()}
    bad_k["known_loser_fails"] = {**bad_k["known_loser_fails"], "fails": False}
    bad2 = {**_R, "known_truth_cases": bad_k}
    assert a.validate_pipeline_audit(bad2)["valid"] is False
    # flipping the next directive away from the C22 readiness must fail
    bad3 = {**_R, "next_required_action": "HUMAN_DECISION_C21_REPLAY_RUNNING",
            "next_is_c22_proposal_readiness": False}
    assert a.validate_pipeline_audit(bad3)["valid"] is False


# ---- morning-report summary -------------------------------------------------

def test_summarize_for_morning_report():
    summ = a.summarize_for_morning_report()
    assert summ["section"] == "sparta_pipeline_audit_v1"
    assert summ["pipeline_audit_available"] is True
    assert summ["research_only"] is True
    assert summ["all_categories_pass"] is True
    assert summ["active_candidate"] is None
    assert summ["active_candidate_is_none"] is True
    assert summ["c21_now_rejected_at_replay"] is True
    assert summ["next_is_c22_proposal_readiness"] is True
    assert summ["c20_remains_rejected"] is True
    assert summ["c22_started"] is False
    assert summ["c21_replay_started"] is False
    assert summ["executes_nothing"] is True


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(a.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
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
