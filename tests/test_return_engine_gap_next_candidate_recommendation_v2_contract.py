"""Tests for the V2 return-engine-gap next-candidate recommendation.

Proves the record is PURE / RECOMMENDATION-ONLY: distils the recurring failure modes (incl.
selection-vs-null + 2021-artifact); recommends a PREFERRED RETURN-ENGINE family (crypto
volatility-risk-premium, delta-hedged short-vol) that is a return engine (not a dampener), has
no directional short-PRICE leg, targets the gap, and is materially distinct from the 26-family
rejected ledger AND from every forbidden direction (low-vol / illiquidity / funding-selection /
same-asset carry / directional / the funding diversifier); includes 2 backups (none forbidden);
flags the options/IV DATA-PHASE prerequisite and the short-vol TAIL risk; activates/promotes
nothing and changes no C22/C23/C24/funding-selection/ledger/lifecycle state; makes no
profitability/deployment claim; pins every capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.return_engine_gap_next_candidate_recommendation_v2_contract as rec
import sparta_commander.research_expansion_plan_v1_contract as rep

_R = rec.build_recommendation_v2()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_recommendation_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "RECOMMEND_NEXT_RETURN_ENGINE_CANDIDATE_V2_FOR_HUMAN_REVIEW"
    assert _R["supersedes"] == "RETURN_ENGINE_GAP_NEXT_CANDIDATE_RECOMMENDATION_V1"
    assert rec.validate_recommendation_v2(_R)["valid"] is True


def test_failure_modes():
    fm = {f["mode"] for f in _R["failure_modes"]}
    for must in ("overtrading_cost_drag", "non_stationary_2021_only_artifact",
                 "short_leg_bleed", "selection_timing_loses_to_always_on_null",
                 "directional_systems_fail_after_fees", "weak_forward_oos_durability"):
        assert must in fm, must


def test_preferred_is_distinct_return_engine():
    p = _R["preferred_candidate"]
    assert p["family"] == "crypto_volatility_risk_premium_delta_hedged_short_vol"
    assert p["family"] not in rep.REJECTED_FAMILIES_C1_TO_C21
    assert p["family"] not in _R["forbidden_directions"]
    assert p["is_return_engine"] is True
    assert p["is_dampener_only"] is False
    assert p["has_directional_short_price_leg"] is False
    assert p["targets_return_engine_gap"] is True
    # explicitly NOT any of the forbidden directions
    for forb in ("crypto_cross_sectional_low_volatility_anomaly_beta_neutral",
                 "crypto_cross_sectional_illiquidity_premium_beta_neutral",
                 "cross_sectional_crypto_funding_carry_market_neutral",
                 "always_on_broad_multi_asset_neutral_funding_carry"):
        assert forb in _R["forbidden_directions"] and p["family"] != forb


def test_preferred_avoids_each_failure_mode():
    a = _R["preferred_avoids_failure_modes"]
    for k in ("overtrading_cost_drag", "non_stationary_2021_only_artifact", "short_leg_bleed",
              "selection_loses_to_null", "benchmark_mismatch", "directional_fail_after_fees",
              "weak_forward_oos"):
        assert k in a and a[k], k


def test_data_phase_and_tail_risk_flagged():
    assert _R["next_best_step_is_data_phase"] is True
    assert "options" in _R["data_phase_needed"].lower()
    assert _R["is_data_gated"] is True
    mb = _R["main_blocker"].lower()
    assert "tail" in mb or "crash" in mb        # short-vol tail risk disclosed
    assert _R["next_required_action"].startswith(
        "HUMAN_APPROVED_ASSESS_AND_PREPARE_OPTIONS_IMPLIED_VOL_DATA_PHASE")


def test_two_backups_not_forbidden():
    assert len(_R["backups"]) == 2
    for b in _R["backups"]:
        assert b["family"] not in rep.REJECTED_FAMILIES_C1_TO_C21
        assert b["family"] not in _R["forbidden_directions"]
        assert b["idea"] and b["main_blocker"]


def test_preservation_no_activation():
    for k in ("activates_nothing", "promotes_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status"):
        assert _R[k] is True, k
    assert _R["is_profitability_claim"] is False and _R["is_deployment_claim"] is False


def test_capabilities_false_and_tamper_rejected():
    for flag in rec._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert rec.validate_recommendation_v2({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot flip preferred to a dampener, give it a directional short, or reactivate funding sel.
    assert rec.validate_recommendation_v2(
        {**_R, "preferred_candidate": {**_R["preferred_candidate"], "is_dampener_only": True}}
    )["valid"] is False
    assert rec.validate_recommendation_v2(
        {**_R, "preferred_candidate": {**_R["preferred_candidate"],
                                       "has_directional_short_price_leg": True}})["valid"] is False
    assert rec.validate_recommendation_v2(
        {**_R, "funding_selection_not_reactivated": False})["valid"] is False


def test_module_purity():
    src = Path(rec.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "urlopen", "requests.", "json.load", "read_text"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
