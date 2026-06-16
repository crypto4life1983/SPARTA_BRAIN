"""Tests for the Candidate #10 real-candle labels review / evidence-
freeze contract (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the 9-record ledger + the full C10 chain
through the pushed dry-run review + V5 + V4 + V3 + V2 + REC + AP;
SHA-256 pins of the untracked detector-labels and detector-summary
artifacts and of the canonical BTCUSD 1d source; frozen counts (156
attempts, 156 accepted pre, 156 accepted post, 0 rejected, 0
anti-cluster drops); identity checks; status breakdown
{accepted_for_replay_review: 156}; sample-size adequacy SATISFIED
(156 >= 100) without consuming the edit token; anti-cluster gap = 5
without consuming the edit token; every accepted record Friday / ISO
weekday 5 / bucket 5; the old coverage blocker stays separate, stale,
unchanged and is NOT used as evidence; downstream replay / relabel /
paper / live gates remain locked; the two JSON artifacts remain
untracked; AST/purity green for the contract.

Optimization: a single shared module-level `_R` record built once at
import time. Tampering tests use deepcopy + targeted mutation and
validate without rebuilding."""

from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_dry_run_review_contract as c10r
import sparta_commander.intraweek_calendar_seasonality_drift_v1_real_candle_labels_review_contract as c10l
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


# ---- one-time memoization of the pure build-gate chain --------------------
# build_c10_labels_review() chain-gates on a DEEP forest of shared, pure,
# deterministic build_* contract gates: the C10 sub-gates (family proposal /
# spec review / detector spec / dry-run review) PLUS the shared V5 -> V4 -> V3
# rejected-family blacklists, the C9/C8/C7 dry-run-review chains, Overnight
# Autopilot V2, Recommendation V1, the Autopilot Loop, and the proposal
# drafter. None of these gates is memoized in production, so the forest is
# re-evaluated EXPONENTIALLY (each gate re-runs its predecessors in full):
# measured in isolation, V3 ~0.08s, V4 ~4.18s (~52x V3), V5 does not finish --
# and C10 sits one layer ABOVE V5. The per-call _recompute_live_dry_run leaves
# are NOT the cost (each ~0.00s); the cost is the sheer NUMBER of repeated
# build_* node evaluations.
#
# Fix (test-local, deterministic): for the SINGLE _R construction below, wrap
# every zero-argument build_* gate (and the cheap _recompute leaves) across all
# loaded sparta_commander modules in a once-per-original, deepcopy-returning
# cache, so each unique gate is computed EXACTLY ONCE -> the exponential tree
# collapses to linear. Every monkeypatch is restored in the finally. No
# assertion or chain-gate meaning is weakened: the gates are pure and
# deterministic, so computing each once yields the IDENTICAL _R; every caller
# still receives an independent deep copy (no shared-mutation risk). Production
# code is untouched. Argument-taking builds (e.g. build_c10_labels_review
# itself) are never cached -- the wrapper passes those straight through.
def _install_pure_gate_memoization():
    cache: dict = {}      # id(original) -> computed result (deep-copied out)
    wrappers: dict = {}   # id(original) -> shared wrapper installed everywhere
    restore: list = []    # (module, attr, original) for exact teardown

    def _make(orig):
        def _wrapped(*args, **kwargs):
            if args or kwargs:          # arg-taking builds: never cached
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

    # Pass 1: one shared wrapper per unique original gate function.
    for modname, mod in list(sys.modules.items()):
        if mod is None or not modname.startswith("sparta_commander"):
            continue
        for orig in list(vars(mod).values()):
            if _is_target(orig) and id(orig) not in wrappers:
                wrappers[id(orig)] = _make(orig)
    # Pass 2: rebind EVERY attribute pointing at a target (defeats by-value
    # `from X import build_Y` imports -- each call site hits the wrapper).
    for modname, mod in list(sys.modules.items()):
        if mod is None or not modname.startswith("sparta_commander"):
            continue
        for attr, val in list(vars(mod).items()):
            if inspect.isfunction(val) and id(val) in wrappers:
                restore.append((mod, attr, val))
                setattr(mod, attr, wrappers[id(val)])
    return restore


_memo_restore = _install_pure_gate_memoization()
try:
    # Build the chain-gated record ONCE at module import time.
    _R = c10l.build_c10_labels_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_chain_gates_all_certify():
    assert _R["verdict"] == c10l.VERDICT_C10L_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert c10l.validate_c10_labels_review(_R)["valid"] is True


def test_full_chain_certifies():
    # A FROZEN verdict with no blockers/failures is ONLY reachable when
    # EVERY upstream chain gate certified: the 9-record rejection ledger,
    # the C10 family proposal, the C10 spec review, the C10 detector spec,
    # the pushed C10 dry-run review, the V5/V4/V3 blacklists, Overnight
    # Autopilot V2, Recommendation V1 and Autopilot Loop V1. Any broken
    # gate short-circuits build_c10_labels_review to a BLOCKED/REJECTED
    # verdict carrying a named blocker. We therefore assert on the already-
    # built `_R` instead of re-running the whole chain, which would re-pay
    # the multi-hour C10 + C9 dry-run recomputes for no extra coverage.
    assert _R["verdict"] == c10l.VERDICT_C10L_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert _R["ledger_all_rejected_kept_on_record"] is True
    assert len(_R["ledger_status_nine_records"]) == 9
    assert all(s == "REJECTED_KEPT_ON_RECORD"
               for s in _R["ledger_status_nine_records"])
    assert c10l.validate_c10_labels_review(_R)["valid"] is True


def test_nine_record_ledger_intact():
    assert _R["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert _R["ledger_all_rejected_kept_on_record"] is True


# ---- SHA pins frozen ------------------------------------------------------

def test_artifact_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == (
        "8276e9a6ee9bd9b89ff28a41f5c160973934bcc03ad8c5371095e62f"
        "b8f9c47d")
    assert _R["expected_summary_sha256"] == (
        "d23d0c34363d4e0cde3413d40266046c8fc4dbcd16a084afbefccfa93"
        "3a2c8ee")
    assert _R["head_at_detection"] == (
        "225c655f8afe28663b2cca4dbbb9252106092e17")
    assert _R["runner_path_tracked"] == (
        "tools/c10_real_candle_detection_once.py")
    assert _R["labels_path"] == (
        "data/intraweek_calendar_seasonality_c10/detector_labels/"
        "c10_detector_labels_2023-01-01_2025-12-31.json")
    assert _R["summary_path"] == (
        "data/intraweek_calendar_seasonality_c10/detector_labels/"
        "c10_detector_summary_2023-01-01_2025-12-31.json")
    for field in ("expected_labels_sha256",
                  "expected_summary_sha256", "head_at_detection"):
        bad = copy.deepcopy(_R)
        bad[field] = "0" * 64
        assert c10l.validate_c10_labels_review(
            bad)["valid"] is False, field


def test_canonical_source_pin_frozen():
    assert _R["expected_source_path"] == (
        "data/crypto_d1_spot/raw/BTC_1d.csv")
    assert _R["expected_source_sha256"] == (
        "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28b"
        "bb89b88")
    assert _R["expected_source_first_date"] == "2019-01-01"
    assert _R["expected_source_last_date"] == "2026-06-08"
    assert _R["expected_source_row_count"] == 2716
    for field in ("expected_source_sha256",
                  "expected_source_first_date",
                  "expected_source_last_date"):
        bad = copy.deepcopy(_R)
        bad[field] = "tampered"
        assert c10l.validate_c10_labels_review(
            bad)["valid"] is False, field
    bad_rc = copy.deepcopy(_R)
    bad_rc["expected_source_row_count"] = 0
    assert c10l.validate_c10_labels_review(bad_rc)["valid"] is False


# ---- old coverage blocker stays separate and stale ------------------------

def test_old_coverage_blocker_separate_and_stale():
    assert _R["blocker_path"] == (
        "data/intraweek_calendar_seasonality_c10/coverage_blocker/"
        "c10_real_candle_coverage_blocker.json")
    assert _R["expected_blocker_sha256"] == (
        "9e66f0f227e7cbd67710d8ae98288fb96303e2a81afe11a4b5eb4aafe"
        "d66c7d6")
    # blocker is a different path from both labels and summary
    assert _R["blocker_path"] != _R["labels_path"]
    assert _R["blocker_path"] != _R["summary_path"]
    bad = copy.deepcopy(_R)
    bad["expected_blocker_sha256"] = "0" * 64
    assert c10l.validate_c10_labels_review(bad)["valid"] is False


# ---- frozen counts --------------------------------------------------------

def test_frozen_windows_and_counts():
    assert _R["expected_in_sample_window"] == [
        "2019-01-01", "2022-12-31"]
    assert _R["expected_out_of_sample_window"] == [
        "2023-01-01", "2025-12-31"]
    assert _R["expected_sample_tag"] == "2023-01-01_2025-12-31"
    assert _R["expected_favorable_weekday_bucket"] == 5
    assert _R["expected_total_attempts"] == 156
    assert _R["expected_accepted_pre_anti_cluster"] == 156
    assert _R["expected_accepted_post_anti_cluster"] == 156
    assert _R["expected_rejected_by_scanner"] == 0
    assert _R["expected_dropped_by_anti_cluster"] == 0
    for field, bad_v in (("expected_total_attempts", 0),
                         ("expected_total_attempts", 1000),
                         ("expected_accepted_pre_anti_cluster", 0),
                         ("expected_accepted_post_anti_cluster", 0),
                         ("expected_rejected_by_scanner", 7),
                         ("expected_dropped_by_anti_cluster", 5),
                         ("expected_favorable_weekday_bucket", 3)):
        bad = copy.deepcopy(_R)
        bad[field] = bad_v
        assert c10l.validate_c10_labels_review(
            bad)["valid"] is False, (field, bad_v)


def test_identity_checks_consistent():
    identity = _R["expected_identity_checks"]
    assert identity[
        "accepted_pre_plus_rejected_equals_attempts"] is True
    assert identity[
        "accepted_post_plus_dropped_equals_accepted_pre"] is True
    assert (_R["expected_accepted_pre_anti_cluster"]
            + _R["expected_rejected_by_scanner"]
            == _R["expected_total_attempts"])
    assert (_R["expected_accepted_post_anti_cluster"]
            + _R["expected_dropped_by_anti_cluster"]
            == _R["expected_accepted_pre_anti_cluster"])


def test_status_breakdown_frozen():
    breakdown = _R["expected_status_breakdown"]
    assert breakdown["accepted_for_replay_review"] == 156
    # No other statuses present (no geometry-floor rejects, no
    # no-evaluation-bar, no clustered drops on this OOS window)
    assert set(breakdown.keys()) == {"accepted_for_replay_review"}
    assert sum(breakdown.values()) == 156
    bad = copy.deepcopy(_R)
    bad["expected_status_breakdown"] = {}
    assert c10l.validate_c10_labels_review(bad)["valid"] is False


# ---- sample-size adequacy SATISFIED --------------------------------------

def test_sample_size_adequacy_satisfied_not_structural_failure():
    sa = _R["expected_sample_size_adequacy"]
    assert sa["accepted_count"] == 156
    assert sa["minimum_required_at_labels_review_gate"] == 100
    assert sa["below_minimum_at_dry_run"] is False
    assert sa["enforced_at_labels_review_gate_only"] is True
    assert sa["does_not_consume_edit_token"] is True
    assert _R["expected_sample_size_satisfied"] is True
    assert _R["expected_sample_size_structural_failure"] is False
    assert 156 >= 100  # explicit arithmetic verification
    # tampering on the satisfied / structural-failure flags invalidates
    bad = copy.deepcopy(_R)
    bad["expected_sample_size_satisfied"] = False
    assert c10l.validate_c10_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["expected_sample_size_structural_failure"] = True
    assert c10l.validate_c10_labels_review(bad2)["valid"] is False


def test_anti_cluster_proposal_locked_and_not_edit_token():
    anti = _R["expected_anti_cluster_facts"]
    assert anti["anti_cluster_min_bar_gap"] == 5
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["accepted_before_anti_cluster"] == 156
    assert anti["accepted_after_anti_cluster"] == 156
    assert anti["dropped_by_anti_cluster"] == 0
    bad = copy.deepcopy(_R)
    bad["expected_anti_cluster_facts"] = {}
    assert c10l.validate_c10_labels_review(bad)["valid"] is False


def test_per_weekday_in_sample_means_frozen():
    means = _R["expected_per_weekday_in_sample_mean_bps"]
    # Friday (weekday 5) is the unique in-sample winner clearing 81 bps
    assert means["5"] == 83.896091
    assert means["5"] > 81.0
    # every other weekday's in-sample mean is below Friday's
    for wd in ("1", "2", "3", "4", "6", "7"):
        assert means[wd] < means["5"], wd
    bad = copy.deepcopy(_R)
    bad["expected_per_weekday_in_sample_mean_bps"] = {}
    assert c10l.validate_c10_labels_review(bad)["valid"] is False


def test_claim_locks_present_including_proposal_locks():
    locks = _R["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_edit_token_applied_by_this_gate",
            "no_rejection_decision_made_by_this_gate",
            "no_promotion_decision_made_by_this_gate",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked",
            "old_coverage_blocker_remains_separate_and_stale"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c10l.validate_c10_labels_review(bad)["valid"] is False


# ---- scope locks + summary self-claims ------------------------------------

def test_expected_scope_locks_all_true():
    locks = _R["expected_scope_locks"]
    for key in ("no_replay", "no_relabel", "no_pnl", "no_fetch",
                "no_network", "no_api", "no_credentials",
                "no_broker", "no_exchange", "no_wallet",
                "no_scheduler", "no_paper_trading",
                "no_micro_live", "no_live_trading",
                "no_edit_token_consumed",
                "no_downstream_gates_unlocked",
                "frozen_regime_inputs_source_not_used",
                "c10_contract_not_weakened_for_missing_2019"):
        assert locks[key] is True, key


def test_expected_summary_self_claims():
    claims = _R["expected_summary_self_claims"]
    assert claims["candidate_id"] == (
        "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1")
    assert claims["candidate_family"] == (
        "intraweek_calendar_seasonality_drift")
    assert claims["symbol"] == "BTCUSD"
    assert claims["timeframe"] == "1d"
    assert claims["direction"] == "long_only"
    assert claims["sample_tag"] == "2023-01-01_2025-12-31"
    assert claims["favorable_weekday_bucket"] == 5
    assert claims["attempts"] == 156
    assert claims["accepted_pre_anti_cluster"] == 156
    assert claims["accepted_post_anti_cluster"] == 156
    assert claims["anti_cluster_dropped_count"] == 0
    assert claims["anti_cluster_min_bar_gap"] == 5
    assert claims["minimum_labels_review_threshold"] == 100
    assert claims["source_sha256_before"] == (
        "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28b"
        "bb89b88")
    assert claims["source_sha256_after"] == (
        claims["source_sha256_before"])
    assert claims["source_row_count"] == 2716
    assert claims["anti_cluster_does_not_consume_edit_token"] is True
    assert claims["source_unchanged_during_detection"] is True


# ---- frozen detection facts ----------------------------------------------

def test_frozen_detection_facts_complete():
    findings = _R["frozen_detection_facts"]
    joined = " || ".join(findings)
    assert "single-symbol btcusd 1d" in joined
    assert "locally promoted canonical btcusd 1d spot source" in joined
    assert "2019-01-01..2026-06-08, 2716 rows" in joined
    assert ("the missing-2019 in-sample coverage blocker is now "
            "cleared and remains a SEPARATE, STALE artifact") in joined
    assert "weekday 5 (friday) is the unique" in joined
    assert ("scan ran over the OUT-OF-SAMPLE window "
            "2023-01-01..2025-12-31 only") in joined
    assert "156 calendar-only friday trigger attempts" in joined
    assert ("156 accepted before anti-cluster; 156 accepted after "
            "anti-cluster") in joined
    assert "0 rejected by the scanner" in joined
    assert "0 dropped by the 5-bar anti-cluster" in joined
    assert "156 + 0 = 156 (accepted-pre + rejected = attempts)" in joined
    assert ("156 + 0 = 156 (accepted-post + drops = accepted-pre)"
            in joined)
    assert "SAMPLE-SIZE ADEQUACY SATISFIED: 156 accepted-post >= 100" \
        in joined
    assert ("anti-cluster gap remains proposal-level locked at 5 bars "
            "and does NOT consume") in joined
    assert ("sample-size adequacy threshold remains proposal-level "
            "locked at 100 accepted setups") in joined
    assert "no replay; no pnl; no relabel; no edit token applied" \
        in joined


# ---- labels-review-only safety / capability flags ------------------------

def test_labels_review_only_with_all_downstream_locked():
    assert _R["is_labels_review_only"] is True
    assert _R["current_loop_stage"] == "detector_and_label_review"
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "promotion_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        assert _R[key] is False, key
    # exhaustive tampering check on capability flags
    for key in ("runs_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_replay", "runs_replay_now", "runs_relabel",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_canonical_source",
                "modifies_detector_labels_artifacts",
                "modifies_coverage_blocker",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability",
                "executes", "writes_files"):
        assert _R[key] is False, key
        bad = copy.deepcopy(_R)
        bad[key] = True
        assert c10l.validate_c10_labels_review(
            bad)["valid"] is False, key


def test_label_next_required_action_and_label_text():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C10_REPLAY_EVALUATION_OR_REJECT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c10l.NEXT_REQUIRED_ACTION.upper(), banned
    assert c10l.get_candidate_10_labels_review_label() == (
        c10l.C10L_LABEL)
    assert c10l.C10L_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NOT A RESCUE",
                   "NOT A PROFITABILITY CLAIM",
                   "SAMPLE-SIZE ADEQUACY SATISFIED",
                   "156 ACCEPTED POST ANTI-CLUSTER"):
        assert phrase in c10l.C10L_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c10l.C10L_LABEL.upper(), (
            banned_phrase)


def test_artifacts_remain_untracked_runner_and_blocker_tracked():
    tracked = _tracked_paths()
    # the two JSON artifacts must stay untracked
    for path in (c10l.LABELS_PATH, c10l.SUMMARY_PATH):
        assert path not in tracked, path
    # the runner and the coverage blocker are intentionally tracked
    assert c10l.RUNNER_PATH in tracked
    assert c10l.BLOCKER_PATH in tracked
    # no detector_labels artifact may be tracked
    for tracked_path in tracked:
        assert not tracked_path.startswith(
            "data/intraweek_calendar_seasonality_c10/"
            "detector_labels/"), tracked_path
    assert _R["failures"] == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c10l.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "os", "io", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "statistics",
                   "random"}
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
