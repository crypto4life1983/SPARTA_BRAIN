"""Tests for the return-engine-gap next-candidate recommendation.

Proves the record is PURE / RECOMMENDATION-ONLY: distils the recurring C1-C25 failure modes;
recommends a PREFERRED family (cross-sectional funding carry) that is market-neutral with NO
directional short leg, targets the return-engine gap, is materially distinct from the 26-family
rejected ledger and from C22-C25, and avoids each known failure mode; includes 2 backups;
discloses the data-gated blocker; activates/promotes nothing and changes no C22/C23/C24/ledger/
lifecycle state; makes no profitability claim; and pins every capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.return_engine_gap_next_candidate_recommendation_v1_contract as rec
import sparta_commander.research_expansion_plan_v1_contract as rep

_R = rec.build_recommendation()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_recommendation_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "RECOMMEND_NEXT_RETURN_ENGINE_CANDIDATE_FOR_HUMAN_REVIEW"
    assert rec.validate_recommendation(_R)["valid"] is True


def test_failure_modes_distilled():
    names = {f["mode"] for f in _R["failure_modes"]}
    for must in ("overtrading_cost_drag", "short_leg_bleed",
                 "benchmark_mismatch_loses_to_buy_and_hold_risk_adjusted",
                 "non_stationary_single_regime_2021_artifact",
                 "neutral_systems_lose_via_bad_directional_short_leg"):
        assert must in names, must


def test_preferred_distinct_and_neutral():
    p = _R["preferred_candidate"]
    assert p["family"] == "cross_sectional_crypto_funding_carry_market_neutral"
    assert p["family"] not in rep.REJECTED_FAMILIES_C1_TO_C21
    assert p["is_market_neutral"] is True
    assert p["has_directional_short_leg"] is False
    assert p["targets_return_engine_gap"] is True
    assert _R["preferred_distinct_from_c22_c25"] is True
    # distinct from the two SAME-ASSET carry families that were rejected
    assert "mechanically_neutral_spot_perp_basis_funding_carry" in rep.REJECTED_FAMILIES_C1_TO_C21
    assert "low_turnover_same_asset_spot_perp_funding_carry" in rep.REJECTED_FAMILIES_C1_TO_C21
    assert p["family"] not in (
        "mechanically_neutral_spot_perp_basis_funding_carry",
        "low_turnover_same_asset_spot_perp_funding_carry")


def test_preferred_avoids_each_failure_mode():
    a = _R["preferred_avoids_failure_modes"]
    for k in ("overtrading_cost_drag", "short_leg_bleed", "benchmark_mismatch",
              "non_stationary_2021_artifact", "weak_durability",
              "directional_fail_after_fees", "neutral_bad_short_leg"):
        assert k in a and a[k], k


def test_two_backups_not_in_ledger():
    assert len(_R["backups"]) == 2
    for b in _R["backups"]:
        assert b["family"] not in rep.REJECTED_FAMILIES_C1_TO_C21
        assert b["idea"] and b["main_blocker"]


def test_data_gated_blocker_disclosed():
    assert _R["is_data_gated"] is True
    assert "funding" in _R["main_blocker"].lower()
    assert _R["data_fetch_gate_locked"] is True


def test_preservation_and_no_activation():
    for k in ("activates_nothing", "promotes_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "does_not_modify_official_ledger",
              "does_not_modify_lifecycle", "does_not_modify_lane_status"):
        assert _R[k] is True, k
    assert _R["is_profitability_claim"] is False
    assert _R["next_required_action"].startswith("HUMAN_DECISION_OPEN_CROSS_SECTIONAL_FUNDING")


def test_capabilities_false_and_tamper_rejected():
    for flag in rec._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert rec.validate_recommendation({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot flip preferred to having a directional short leg, nor activate anything
    bad_pref = {**_R["preferred_candidate"], "has_directional_short_leg": True}
    assert rec.validate_recommendation({**_R, "preferred_candidate": bad_pref})["valid"] is False
    assert rec.validate_recommendation({**_R, "c22_unchanged": False})["valid"] is False


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
