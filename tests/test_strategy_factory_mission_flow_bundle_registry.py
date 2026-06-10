"""Tests for the Strategy Factory Mission Flow Bundle Registry (Block 79).

The registry is a PURE, stdlib-only, read-only source of truth for completed
Strategy Factory bundle metadata. It lets the JARVIS Mission Flow feed follow
the pipeline from structured metadata instead of hardcoding each bundle inline.

Coverage:
- registry includes Bundles 42 through 54, all complete
- latest completed bundle is Bundle 54
- recognized research-only protocol (Block 95): Crypto-D1 Strategy Candidate
  Protocol v1 (RESEARCH_ONLY, read_only, no execute, BTC/ETH/SOL, spot, D1,
  four candidate families, unlocks nothing real, creates no new bundle)
- recognized research-only protocol contract (Block 97): Crypto-D1 Strategy
  Candidate Protocol Contract (RESEARCH_ONLY, read_only, no execute, validates
  the Block 95 protocol, preserves the four families, unlocks nothing real,
  creates no new bundle)
- current_stage / next_required_action match the post-protocol-contract state
- every registered bundle is RESEARCH_ONLY, read_only True, executes False
- no registered bundle authorizes real-world action or unlocks any real
  capability (data, QA, baseline, backtest, paper/live, broker/exchange,
  automation, runtime/registry/dashboard writes)
- schema constants are readable and stable
- deterministic repeated calls; mutation-isolated copies
- pure stdlib import-root audit + forbidden-surface audit
- no filesystem / network / subprocess / dynamic execution surface
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_mission_flow_bundle_registry import (
    REGISTRY_VERSION,
    REGISTRY_MODE,
    REGISTRY_SAFETY_POSTURE,
    CURRENT_STAGE,
    NEXT_REQUIRED_ACTION,
    LATEST_COMPLETED_PROTOCOL,
    LATEST_COMPLETED_PROTOCOL_CONTRACT,
    LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT,
    LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT,
    LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT,
    LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT,
    LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT,
    LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT,
    LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT,
    LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT,
    LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT,
    LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT,
    LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT,
    LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT,
    LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT,
    LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT,
    LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT,
    LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER,
    list_registered_bundles,
    list_completed_bundles,
    get_latest_completed_bundle,
    get_bundle_by_number,
    get_bundle_by_id,
    get_latest_completed_bundle_label,
    get_latest_completed_protocol,
    get_latest_completed_protocol_label,
    get_latest_completed_protocol_contract,
    get_latest_completed_protocol_contract_label,
    get_latest_completed_family_selection_contract,
    get_latest_completed_family_selection_contract_label,
    get_latest_completed_family_review_contract,
    get_latest_completed_family_review_contract_label,
    get_latest_completed_research_plan_contract,
    get_latest_completed_research_plan_contract_label,
    get_latest_completed_research_plan_review_contract,
    get_latest_completed_research_plan_review_contract_label,
    get_latest_completed_research_plan_approval_contract,
    get_latest_completed_research_plan_approval_contract_label,
    get_latest_completed_research_design_contract,
    get_latest_completed_research_design_contract_label,
    get_latest_completed_research_design_review_contract,
    get_latest_completed_research_design_review_contract_label,
    get_latest_completed_research_design_approval_contract,
    get_latest_completed_research_design_approval_contract_label,
    get_latest_completed_research_readiness_contract,
    get_latest_completed_research_readiness_contract_label,
    get_latest_completed_external_bot_evidence_intake_contract,
    get_latest_completed_external_bot_evidence_intake_contract_label,
    get_latest_completed_hyperliquid_whale_evidence_contract,
    get_latest_completed_hyperliquid_whale_evidence_contract_label,
    get_latest_completed_funding_rate_evidence_contract,
    get_latest_completed_funding_rate_evidence_contract_label,
    get_latest_completed_bitcoin_cycle_timing_evidence_contract,
    get_latest_completed_bitcoin_cycle_timing_evidence_contract_label,
    get_latest_completed_daily_alpha_brief_research_contract,
    get_latest_completed_daily_alpha_brief_research_contract_label,
    get_latest_completed_daily_alpha_brief_review_contract,
    get_latest_completed_daily_alpha_brief_review_contract_label,
    get_latest_completed_daily_alpha_brief_approval_contract,
    get_latest_completed_daily_alpha_brief_approval_contract_label,
    get_latest_completed_strategy_evidence_scoring_contract,
    get_latest_completed_strategy_evidence_scoring_contract_label,
    get_latest_completed_cohort_independence_contract,
    get_latest_completed_cohort_independence_contract_label,
    get_latest_completed_real_data_qa_boundary_decision_contract,
    get_latest_completed_real_data_qa_boundary_decision_contract_label,
    get_latest_completed_real_data_qa_human_approval_packet_contract,
    get_latest_completed_real_data_qa_human_approval_packet_contract_label,
    get_latest_completed_real_data_qa_readiness_checklist_contract,
    get_latest_completed_real_data_qa_readiness_checklist_contract_label,
    get_latest_completed_overnight_research_autopilot_controller,
    get_latest_completed_overnight_research_autopilot_controller_label,
    LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET,
    get_latest_completed_real_data_qa_human_approval_packet,
    get_latest_completed_real_data_qa_human_approval_packet_label,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION,
    get_latest_completed_real_data_qa_boundary_decision,
    get_latest_completed_real_data_qa_boundary_decision_label,
    LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION,
    get_latest_completed_pipeline_coverage_reconciliation,
    get_latest_completed_pipeline_coverage_reconciliation_label,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW,
    LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION,
    get_latest_completed_real_data_qa_boundary_readiness_review,
    get_latest_completed_real_data_qa_boundary_readiness_review_label,
    get_latest_completed_public_spot_source_evaluation,
    get_latest_completed_public_spot_source_evaluation_label,
    LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC,
    get_latest_completed_concrete_spot_provider_adapter_spec,
    get_latest_completed_concrete_spot_provider_adapter_spec_label,
    LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN,
    get_latest_completed_selected_spot_provider_fetch_runner_dry_run,
    get_latest_completed_selected_spot_provider_fetch_runner_dry_run_label,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET,
    get_latest_completed_real_data_qa_boundary_decision_packet,
    get_latest_completed_real_data_qa_boundary_decision_packet_label,
    LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT,
    get_latest_completed_real_data_qa_plan_only_contract,
    get_latest_completed_real_data_qa_plan_only_contract_label,
    LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION,
    get_latest_completed_real_data_qa_plan_approval_decision,
    get_latest_completed_real_data_qa_plan_approval_decision_label,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION,
    get_latest_completed_real_data_qa_boundary_final_decision,
    get_latest_completed_real_data_qa_boundary_final_decision_label,
    LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT,
    get_latest_completed_resume_policy_research_plan_contract_label,
    LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT,
    get_latest_completed_resume_policy_simulation_runner_contract_label,
    LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT,
    get_latest_completed_resume_policy_results_review_contract_label,
    get_current_stage,
    get_next_required_action,
    get_registry_safety_posture,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_mission_flow_bundle_registry.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_CAPABILITY_FLAGS = (
    "authorizes_real_world_action",
    "unlocks_data_acquisition",
    "unlocks_qa",
    "unlocks_baseline",
    "unlocks_backtest",
    "unlocks_simulation",
    "unlocks_paper_live",
    "unlocks_broker_exchange",
    "unlocks_automation",
    "unlocks_runtime_writes",
    "unlocks_registry_writes",
    "unlocks_dashboard_writes",
)


# --- 1: registry membership -------------------------------------------------

def test_registry_includes_bundles_42_through_54():
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_all_registered_bundles_complete():
    for b in list_registered_bundles():
        assert b["complete"] is True, b["bundle_id"]
    assert len(list_completed_bundles()) == 13


def test_bundle_record_has_stable_keys():
    expected = {
        "bundle_number", "bundle_id", "name", "module", "schema_constant",
        "schema_version", "stage", "complete", "mode", "read_only",
        "executes", "human_approval_required", "next_gate", "reason",
    } | set(_CAPABILITY_FLAGS)
    for b in list_registered_bundles():
        assert set(b.keys()) == expected, b["bundle_id"]


def test_bundle_ids_match_numbers():
    for b in list_registered_bundles():
        assert b["bundle_id"] == "BUNDLE_" + str(b["bundle_number"])


# --- 2: latest completed / lookups -----------------------------------------

def test_latest_completed_bundle_is_bundle_54():
    latest = get_latest_completed_bundle()
    assert latest["bundle_number"] == 54
    assert latest["bundle_id"] == "BUNDLE_54"
    assert latest["name"] == (
        "Crypto-D1 Research-Only Dry-Run Research Archive or Closure Contract"
    )


def test_latest_completed_bundle_label():
    assert get_latest_completed_bundle_label() == (
        "Bundle 54 - Crypto-D1 Research-Only Dry-Run Research Archive or "
        "Closure Contract"
    )


def test_get_bundle_by_number():
    assert get_bundle_by_number(42)["name"] == (
        "Crypto-D1 Acquire Decision Contract"
    )
    assert get_bundle_by_number(46)["bundle_id"] == "BUNDLE_46"
    assert get_bundle_by_number(999) is None


def test_get_bundle_by_id():
    assert get_bundle_by_id("BUNDLE_47")["bundle_number"] == 47
    assert get_bundle_by_id("BUNDLE_45")["name"] == (
        "Crypto-D1 Offline Acquisition Plan Contract"
    )
    assert get_bundle_by_id("BUNDLE_404") is None


# --- 3: stage / next action match post-protocol-definition state ------------

def test_current_stage_is_human_controlled_real_data_qa_boundary_decision():
    # After the research-only Resume-Policy chain (Blocks 175-177) is recognized
    # complete, the backbone advances to the human review of the resume-policy
    # simulation results -- NOT another build step. No stale
    # "..._APPROVAL_CONTRACT_REQUIRED" literal remains.
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert get_current_stage() == CURRENT_STAGE
    assert "HUMAN_REVIEW" in CURRENT_STAGE
    assert "RESUME_POLICY" in CURRENT_STAGE
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_REQUIRED"
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_REQUIRED"
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
    # A human review stage over research-only resume-policy results, not execution.
    # Execution verbs stay banned.
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "AUTOMATION", "ORDER"):
        assert banned not in CURRENT_STAGE, banned


def test_next_required_action_is_human_controlled_real_data_qa_boundary_decision():
    # After the research-only Resume-Policy chain (Blocks 175-177) is recognized
    # complete, the only next step is the human review of the resume-policy
    # simulation results -- a human judgment, NOT a BUILD step and NOT an
    # authorization. No stale "BUILD_..._APPROVAL_CONTRACT" literal remains.
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert get_next_required_action() == NEXT_REQUIRED_ACTION
    # it is explicitly NOT a build action
    assert not NEXT_REQUIRED_ACTION.startswith("BUILD_")
    assert "HUMAN_REVIEW" in NEXT_REQUIRED_ACTION
    assert "RESUME_POLICY" in NEXT_REQUIRED_ACTION
    assert NEXT_REQUIRED_ACTION != (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert NEXT_REQUIRED_ACTION != (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    # A human review action authorizes nothing real; execution verbs stay banned.
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in NEXT_REQUIRED_ACTION, banned


# --- 4: every bundle is research-only and unlocks nothing real --------------

def test_every_bundle_research_only_read_only_no_execute():
    for b in list_registered_bundles():
        assert b["mode"] == "RESEARCH_ONLY", b["bundle_id"]
        assert b["read_only"] is True, b["bundle_id"]
        assert b["executes"] is False, b["bundle_id"]
        assert b["human_approval_required"] is True, b["bundle_id"]


def test_no_bundle_authorizes_real_world_action():
    for b in list_registered_bundles():
        assert b["authorizes_real_world_action"] is False, b["bundle_id"]


def test_no_bundle_unlocks_any_real_capability():
    for b in list_registered_bundles():
        for flag in _CAPABILITY_FLAGS:
            assert b[flag] is False, (b["bundle_id"], flag)


def test_registry_safety_posture_blocks_everything():
    posture = get_registry_safety_posture()
    assert posture["mode"] == "RESEARCH_ONLY"
    assert posture["read_only"] is True
    assert posture["human_approval_required"] is True
    for k, v in posture.items():
        if k in ("mode", "read_only", "human_approval_required"):
            continue
        assert v is False, f"posture flag {k} must be False"


# --- 5: schema constants readable + stable ----------------------------------

def test_schema_versions_readable_and_stable():
    for b in list_registered_bundles():
        assert isinstance(b["schema_version"], str) and b["schema_version"]
        assert b["schema_constant"].endswith("SCHEMA_VERSION")
    boundary = get_bundle_by_number(47)
    assert boundary["schema_version"] == (
        "strategy_factory_crypto_d1_human_approved_offline_acquisition_"
        "execution_boundary_contract.v1"
    )
    next_step = get_bundle_by_number(48)
    assert next_step["schema_constant"] == "NEXT_STEP_SCHEMA_VERSION"
    assert next_step["schema_version"] == (
        "strategy_factory_crypto_d1_post_boundary_research_only_next_step_"
        "contract.v1"
    )
    preview = get_bundle_by_number(49)
    assert preview["schema_constant"] == "PREVIEW_SCHEMA_VERSION"
    assert preview["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_preview_contract.v1"
    )
    review = get_bundle_by_number(50)
    assert review["schema_constant"] == "REVIEW_SCHEMA_VERSION"
    assert review["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_review_contract.v1"
    )
    decision = get_bundle_by_number(51)
    assert decision["schema_constant"] == "DECISION_SCHEMA_VERSION"
    assert decision["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_decision_contract.v1"
    )
    decision_review = get_bundle_by_number(52)
    assert decision_review["schema_constant"] == "DECISION_REVIEW_SCHEMA_VERSION"
    assert decision_review["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_decision_review_"
        "contract.v1"
    )
    final_decision = get_bundle_by_number(53)
    assert final_decision["schema_constant"] == "FINAL_DECISION_SCHEMA_VERSION"
    assert final_decision["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_final_decision_"
        "contract.v1"
    )
    archive_or_closure = get_bundle_by_number(54)
    assert archive_or_closure["schema_constant"] == (
        "ARCHIVE_OR_CLOSURE_SCHEMA_VERSION"
    )
    assert archive_or_closure["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_research_archive_"
        "or_closure_contract.v1"
    )


def test_bundle_48_is_research_only_and_unlocks_nothing():
    b48 = get_bundle_by_number(48)
    assert b48 is not None
    assert b48["bundle_id"] == "BUNDLE_48"
    assert b48["mode"] == "RESEARCH_ONLY"
    assert b48["read_only"] is True
    assert b48["executes"] is False
    assert b48["human_approval_required"] is True
    assert b48["complete"] is True
    assert b48["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_post_boundary_"
        "research_only_next_step_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b48[flag] is False, flag


def test_bundle_49_is_research_only_and_unlocks_nothing():
    b49 = get_bundle_by_number(49)
    assert b49 is not None
    assert b49["bundle_id"] == "BUNDLE_49"
    assert b49["mode"] == "RESEARCH_ONLY"
    assert b49["read_only"] is True
    assert b49["executes"] is False
    assert b49["human_approval_required"] is True
    assert b49["complete"] is True
    assert b49["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_preview_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b49[flag] is False, flag


def test_bundle_50_is_research_only_and_unlocks_nothing():
    b50 = get_bundle_by_number(50)
    assert b50 is not None
    assert b50["bundle_id"] == "BUNDLE_50"
    assert b50["mode"] == "RESEARCH_ONLY"
    assert b50["read_only"] is True
    assert b50["executes"] is False
    assert b50["human_approval_required"] is True
    assert b50["complete"] is True
    assert b50["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_review_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b50[flag] is False, flag


def test_bundle_51_is_research_only_and_unlocks_nothing():
    b51 = get_bundle_by_number(51)
    assert b51 is not None
    assert b51["bundle_id"] == "BUNDLE_51"
    assert b51["mode"] == "RESEARCH_ONLY"
    assert b51["read_only"] is True
    assert b51["executes"] is False
    assert b51["human_approval_required"] is True
    assert b51["complete"] is True
    assert b51["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_decision_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b51[flag] is False, flag


def test_bundle_52_is_research_only_and_unlocks_nothing():
    b52 = get_bundle_by_number(52)
    assert b52 is not None
    assert b52["bundle_id"] == "BUNDLE_52"
    assert b52["mode"] == "RESEARCH_ONLY"
    assert b52["read_only"] is True
    assert b52["executes"] is False
    assert b52["human_approval_required"] is True
    assert b52["complete"] is True
    assert b52["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_decision_review_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b52[flag] is False, flag


def test_bundle_53_is_research_only_and_unlocks_nothing():
    b53 = get_bundle_by_number(53)
    assert b53 is not None
    assert b53["bundle_id"] == "BUNDLE_53"
    assert b53["mode"] == "RESEARCH_ONLY"
    assert b53["read_only"] is True
    assert b53["executes"] is False
    assert b53["human_approval_required"] is True
    assert b53["complete"] is True
    assert b53["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_final_decision_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b53[flag] is False, flag


def test_bundle_54_is_research_only_and_unlocks_nothing():
    b54 = get_bundle_by_number(54)
    assert b54 is not None
    assert b54["bundle_id"] == "BUNDLE_54"
    assert b54["mode"] == "RESEARCH_ONLY"
    assert b54["read_only"] is True
    assert b54["executes"] is False
    assert b54["human_approval_required"] is True
    assert b54["complete"] is True
    assert b54["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_research_archive_or_closure_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b54[flag] is False, flag


# --- 5b: recognized research-only protocol (Block 95) -----------------------

_EXPECTED_FAMILY_IDS = [
    "MOMENTUM_TREND_CONTINUATION",
    "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
    "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    "REGIME_FILTER_LAYER",
]


def test_latest_completed_protocol_label():
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert get_latest_completed_protocol_label() == LATEST_COMPLETED_PROTOCOL
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in LATEST_COMPLETED_PROTOCOL.upper(), banned


def test_registry_recognizes_strategy_candidate_protocol_v1():
    p = get_latest_completed_protocol()
    assert p["protocol_id"] == "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    assert p["protocol_name"] == "Crypto-D1 Strategy Candidate Protocol v1"
    assert p["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_next_research_protocol"
    )
    assert p["schema_constant"] == "PROTOCOL_SCHEMA_VERSION"
    assert p["schema_version"] == (
        "strategy_factory_crypto_d1_next_research_protocol.v1"
    )
    assert p["defined"] is True
    assert p["complete"] is True


def test_recognized_protocol_is_research_only_read_only_no_execute():
    p = get_latest_completed_protocol()
    assert p["mode"] == "RESEARCH_ONLY"
    assert p["read_only"] is True
    assert p["executes"] is False
    assert p["human_approval_required"] is True


def test_recognized_protocol_universe_is_btc_eth_sol_spot_d1():
    p = get_latest_completed_protocol()
    assert p["research_universe"] == ["BTC", "ETH", "SOL"]
    assert p["market_type"] == "SPOT"
    assert p["timeframe"] == "D1"


def test_recognized_protocol_has_four_candidate_families():
    p = get_latest_completed_protocol()
    assert p["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(p["candidate_family_ids"]) == 4
    assert p["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_protocol_authorizes_nothing_unlocks_nothing():
    p = get_latest_completed_protocol()
    for flag in _CAPABILITY_FLAGS:
        assert p[flag] is False, flag
    assert p["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )
    reason = p["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_protocol_does_not_change_latest_bundle():
    # Recognizing the protocol must NOT invent a new execution bundle; the
    # highest completed bundle is still Bundle 54.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_protocol_deterministic_and_mutation_isolated():
    assert get_latest_completed_protocol() == get_latest_completed_protocol()
    p = get_latest_completed_protocol()
    p["executes"] = True
    p["research_universe"].append("TAMPERED")
    p["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_protocol()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5c: recognized research-only protocol contract (Block 97) --------------

def test_latest_completed_protocol_contract_label():
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert (
        get_latest_completed_protocol_contract_label()
        == LATEST_COMPLETED_PROTOCOL_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in LATEST_COMPLETED_PROTOCOL_CONTRACT.upper(), banned


def test_registry_recognizes_strategy_candidate_protocol_contract():
    c = get_latest_completed_protocol_contract()
    assert c["protocol_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Strategy Candidate Protocol Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_protocol_contract"
    )
    assert c["schema_constant"] == "STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_protocol_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_protocol_contract_research_only_read_only_no_execute():
    c = get_latest_completed_protocol_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_protocol_contract_universe_is_btc_eth_sol_spot_d1():
    c = get_latest_completed_protocol_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_protocol_contract_preserves_four_candidate_families():
    c = get_latest_completed_protocol_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_protocol_contract_authorizes_nothing_unlocks_nothing():
    c = get_latest_completed_protocol_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_protocol_contract_does_not_change_latest_bundle():
    # Recognizing the contract must NOT invent a new execution bundle; the
    # highest completed bundle is still Bundle 54, and the latest protocol is
    # still Block 95.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_protocol_contract_deterministic_and_mutation_isolated():
    assert (
        get_latest_completed_protocol_contract()
        == get_latest_completed_protocol_contract()
    )
    c = get_latest_completed_protocol_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_protocol_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5d: recognized research-only family-selection contract (Block 99) ------

def test_latest_completed_family_selection_contract_label():
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert (
        get_latest_completed_family_selection_contract_label()
        == LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_family_selection_contract():
    c = get_latest_completed_family_selection_contract()
    assert c["family_selection_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_family_selection_"
        "contract"
    )
    assert c["schema_constant"] == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION"
    )
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_family_selection_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_family_selection_contract_research_only_no_execute():
    c = get_latest_completed_family_selection_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_family_selection_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_family_selection_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_family_selection_contract_preserves_four_families():
    c = get_latest_completed_family_selection_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_family_selection_contract_authorizes_nothing():
    c = get_latest_completed_family_selection_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_family_selection_contract_preserves_prior_truth():
    # Recognizing the family-selection contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / protocol / protocol
    # contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_family_selection_contract_deterministic_isolated():
    assert (
        get_latest_completed_family_selection_contract()
        == get_latest_completed_family_selection_contract()
    )
    c = get_latest_completed_family_selection_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_family_selection_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5e: recognized research-only family-review contract (Block 101) ---------

def test_latest_completed_family_review_contract_label():
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    assert (
        get_latest_completed_family_review_contract_label()
        == LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_family_review_contract():
    c = get_latest_completed_family_review_contract()
    assert c["family_review_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Family Review Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_family_review_"
        "contract"
    )
    assert c["schema_constant"] == (
        "STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION"
    )
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_family_review_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_family_review_contract_research_only_no_execute():
    c = get_latest_completed_family_review_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_family_review_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_family_review_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_family_review_contract_preserves_four_families():
    c = get_latest_completed_family_review_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_family_review_contract_authorizes_nothing():
    c = get_latest_completed_family_review_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_family_review_contract_preserves_prior_truth():
    # Recognizing the family-review contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / protocol / protocol
    # contract / family-selection contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_family_review_contract_deterministic_isolated():
    assert (
        get_latest_completed_family_review_contract()
        == get_latest_completed_family_review_contract()
    )
    c = get_latest_completed_family_review_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_family_review_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5f: recognized research-only research-plan contract (Block 103) ----------

def test_latest_completed_research_plan_contract_label():
    assert LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT == (
        "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    assert (
        get_latest_completed_research_plan_contract_label()
        == LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_plan_contract():
    c = get_latest_completed_research_plan_contract()
    assert c["research_plan_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_"
        "contract"
    )
    assert c["schema_constant"] == (
        "BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION"
    )
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_plan_contract_research_only_no_execute():
    c = get_latest_completed_research_plan_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_plan_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_plan_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_plan_contract_preserves_four_families():
    c = get_latest_completed_research_plan_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_plan_contract_authorizes_nothing():
    c = get_latest_completed_research_plan_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_plan_contract_preserves_prior_truth():
    # Recognizing the research-plan contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / protocol / protocol
    # contract / family-selection contract / family-review contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_family_review_contract_next_action_pinned_to_research_plan():
    # After Block 103, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 101 family-review record keeps its historical next step (build the
    # research-plan contract, now complete).
    c = get_latest_completed_family_review_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT"
    )


def test_recognized_research_plan_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_plan_contract()
        == get_latest_completed_research_plan_contract()
    )
    c = get_latest_completed_research_plan_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_plan_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5g: recognized research-only research-plan-review contract (Block 105) ---

def test_latest_completed_research_plan_review_contract_label():
    assert LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT == (
        "Block 105 - Crypto-D1 Strategy Candidate Research Plan Review Contract"
    )
    assert (
        get_latest_completed_research_plan_review_contract_label()
        == LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_plan_review_contract():
    c = get_latest_completed_research_plan_review_contract()
    assert c["research_plan_review_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Plan Review Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_review_"
        "contract"
    )
    assert c["schema_constant"] == "RESEARCH_PLAN_REVIEW_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_review_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_plan_review_contract_research_only_no_execute():
    c = get_latest_completed_research_plan_review_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_plan_review_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_plan_review_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_plan_review_contract_preserves_four_families():
    c = get_latest_completed_research_plan_review_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_plan_review_contract_authorizes_nothing():
    c = get_latest_completed_research_plan_review_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_plan_review_contract_preserves_prior_truth():
    # Recognizing the research-plan-review contract must NOT invent a new
    # execution bundle and must NOT disturb the latest bundle / protocol /
    # protocol contract / family-selection / family-review / research-plan.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT == (
        "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_plan_contract_next_action_pinned_to_review():
    # After Block 105, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 103 research-plan record keeps its historical next step (build the
    # research-plan review contract, now complete).
    c = get_latest_completed_research_plan_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
    )


def test_recognized_research_plan_review_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_plan_review_contract()
        == get_latest_completed_research_plan_review_contract()
    )
    c = get_latest_completed_research_plan_review_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_plan_review_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5h: recognized research-only research-plan-approval contract (Block 107) --

def test_latest_completed_research_plan_approval_contract_label():
    assert LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT == (
        "Block 107 - Crypto-D1 Strategy Candidate Research Plan Approval "
        "Contract"
    )
    assert (
        get_latest_completed_research_plan_approval_contract_label()
        == LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_plan_approval_contract():
    c = get_latest_completed_research_plan_approval_contract()
    assert c["research_plan_approval_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Plan Approval Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_"
        "approval_contract"
    )
    assert c["schema_constant"] == "RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_plan_approval_contract_research_only_no_execute():
    c = get_latest_completed_research_plan_approval_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_plan_approval_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_plan_approval_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_plan_approval_contract_preserves_four_families():
    c = get_latest_completed_research_plan_approval_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_plan_approval_contract_authorizes_nothing():
    c = get_latest_completed_research_plan_approval_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_plan_approval_contract_preserves_prior_truth():
    # Recognizing the research-plan-approval contract must NOT invent a new
    # execution bundle and must NOT disturb the latest bundle / protocol /
    # protocol contract / family-selection / family-review / research-plan /
    # research-plan-review.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT == (
        "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT == (
        "Block 105 - Crypto-D1 Strategy Candidate Research Plan Review Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_plan_review_contract_next_action_pinned_to_approval():
    # After Block 107, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 105 research-plan-review record keeps its historical next step (build the
    # research-plan approval contract, now complete).
    c = get_latest_completed_research_plan_review_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
    )


def test_recognized_research_plan_approval_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_plan_approval_contract()
        == get_latest_completed_research_plan_approval_contract()
    )
    c = get_latest_completed_research_plan_approval_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_plan_approval_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5i: recognized research-only research-design contract (Block 109) --------

def test_latest_completed_research_design_contract_label():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT == (
        "Block 109 - Crypto-D1 Strategy Candidate Research Design Contract"
    )
    assert (
        get_latest_completed_research_design_contract_label()
        == LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_design_contract():
    c = get_latest_completed_research_design_contract()
    assert c["research_design_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Design Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_design_"
        "contract"
    )
    assert c["schema_constant"] == "RESEARCH_DESIGN_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_design_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_design_contract_research_only_no_execute():
    c = get_latest_completed_research_design_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_design_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_design_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_design_contract_preserves_four_families():
    c = get_latest_completed_research_design_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_design_contract_authorizes_nothing():
    c = get_latest_completed_research_design_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_design_contract_preserves_prior_truth():
    # Recognizing the research-design contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / protocol / protocol
    # contract / family-selection / family-review / research-plan /
    # research-plan-review / research-plan-approval.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT == (
        "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT == (
        "Block 105 - Crypto-D1 Strategy Candidate Research Plan Review Contract"
    )
    assert LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT == (
        "Block 107 - Crypto-D1 Strategy Candidate Research Plan Approval "
        "Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_plan_approval_contract_next_action_pinned_to_design():
    # After Block 109, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 107 research-plan-approval record keeps its historical next step (build the
    # research-design contract, now complete).
    c = get_latest_completed_research_plan_approval_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
    )


def test_recognized_research_design_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_design_contract()
        == get_latest_completed_research_design_contract()
    )
    c = get_latest_completed_research_design_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_design_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5j: recognized research-only research-design-review contract (Block 111) -

def test_latest_completed_research_design_review_contract_label():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT == (
        "Block 111 - Crypto-D1 Strategy Candidate Research Design Review "
        "Contract"
    )
    assert (
        get_latest_completed_research_design_review_contract_label()
        == LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_design_review_contract():
    c = get_latest_completed_research_design_review_contract()
    assert c["research_design_review_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Design Review Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_design_"
        "review_contract"
    )
    assert c["schema_constant"] == "RESEARCH_DESIGN_REVIEW_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_design_review_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_design_review_contract_research_only_no_execute():
    c = get_latest_completed_research_design_review_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_design_review_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_design_review_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_design_review_contract_preserves_four_families():
    c = get_latest_completed_research_design_review_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_design_review_contract_authorizes_nothing():
    c = get_latest_completed_research_design_review_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_design_contract_next_action_pinned_to_review():
    # After Block 111, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 109 research-design record keeps its historical next step (build the
    # research-design-review contract, now complete).
    c = get_latest_completed_research_design_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT"
    )


def test_recognized_research_design_review_contract_preserves_prior_truth():
    # Recognizing the research-design-review contract must NOT invent a new
    # execution bundle and must NOT disturb the latest bundle / prior contracts.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT == (
        "Block 109 - Crypto-D1 Strategy Candidate Research Design Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_design_review_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_design_review_contract()
        == get_latest_completed_research_design_review_contract()
    )
    c = get_latest_completed_research_design_review_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_design_review_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5k: recognized research-only research-design-approval contract (Block 113)

def test_latest_completed_research_design_approval_contract_label():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT == (
        "Block 113 - Crypto-D1 Strategy Candidate Research Design Approval "
        "Contract"
    )
    assert (
        get_latest_completed_research_design_approval_contract_label()
        == LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_design_approval_contract():
    c = get_latest_completed_research_design_approval_contract()
    assert c["research_design_approval_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Design Approval Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_design_"
        "approval_contract"
    )
    assert c["schema_constant"] == "RESEARCH_DESIGN_APPROVAL_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_design_approval_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_design_approval_contract_research_only_no_execute():
    c = get_latest_completed_research_design_approval_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_design_approval_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_design_approval_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_design_approval_contract_preserves_four_families():
    c = get_latest_completed_research_design_approval_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_design_approval_contract_authorizes_nothing():
    c = get_latest_completed_research_design_approval_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_research_design_review_contract_next_action_pinned_to_approval():
    # After Block 113, the global NEXT_REQUIRED_ACTION advanced, but the Block
    # 111 research-design-review record keeps its historical next step (build the
    # research-design-approval contract, now complete).
    c = get_latest_completed_research_design_review_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT"
    )


def test_recognized_research_design_approval_contract_preserves_prior_truth():
    # Recognizing the research-design-approval contract must NOT invent a new
    # execution bundle and must NOT disturb the latest bundle / prior contracts.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT == (
        "Block 111 - Crypto-D1 Strategy Candidate Research Design Review "
        "Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_design_approval_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_design_approval_contract()
        == get_latest_completed_research_design_approval_contract()
    )
    c = get_latest_completed_research_design_approval_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_design_approval_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5l: recognized research-only research-readiness contract (Block 115) -----

def test_latest_completed_research_readiness_contract_label():
    assert LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT == (
        "Block 115 - Crypto-D1 Strategy Candidate Research Readiness Contract"
    )
    assert (
        get_latest_completed_research_readiness_contract_label()
        == LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in (
            LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_candidate_research_readiness_contract():
    c = get_latest_completed_research_readiness_contract()
    assert c["research_readiness_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Candidate Research Readiness Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_candidate_research_readiness_"
        "contract"
    )
    assert c["schema_constant"] == "RESEARCH_READINESS_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_candidate_research_readiness_"
        "contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )
    assert c["validates_protocol_name"] == (
        "Crypto-D1 Strategy Candidate Protocol v1"
    )


def test_recognized_research_readiness_contract_research_only_no_execute():
    c = get_latest_completed_research_readiness_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_research_readiness_contract_universe_btc_eth_sol_spot_d1():
    c = get_latest_completed_research_readiness_contract()
    assert c["research_universe"] == ["BTC", "ETH", "SOL"]
    assert c["market_type"] == "SPOT"
    assert c["timeframe"] == "D1"


def test_recognized_research_readiness_contract_preserves_four_families():
    c = get_latest_completed_research_readiness_contract()
    assert c["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(c["candidate_family_ids"]) == 4
    assert c["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_research_readiness_contract_authorizes_nothing():
    c = get_latest_completed_research_readiness_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # readiness now pins its historical next step: BUILD the research-only external
    # bot evidence intake contract (a paper step, since completed in Block 117).
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # readiness is paper readiness only and never opens real_data_qa
    assert "real_data_qa stays blocked" in reason


def test_recognized_research_design_approval_contract_next_action_pinned_to_readiness():
    # After Block 115, the global NEXT_REQUIRED_ACTION advanced to the await-human
    # boundary decision, but the Block 113 research-design-approval record keeps its
    # historical next step (build the research-readiness contract, now complete).
    c = get_latest_completed_research_design_approval_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT"
    )


def test_recognized_research_readiness_contract_preserves_prior_truth():
    # Recognizing the research-readiness contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / prior contracts.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT == (
        "Block 113 - Crypto-D1 Strategy Candidate Research Design Approval "
        "Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_readiness_contract_deterministic_isolated():
    assert (
        get_latest_completed_research_readiness_contract()
        == get_latest_completed_research_readiness_contract()
    )
    c = get_latest_completed_research_readiness_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_research_readiness_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5m: recognized research-only external-bot-evidence-intake (Block 117) ----

def test_latest_completed_external_bot_evidence_intake_contract_label():
    assert LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT == (
        "Block 117 - Crypto-D1 External Bot Evidence Intake Contract"
    )
    assert (
        get_latest_completed_external_bot_evidence_intake_contract_label()
        == LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT.upper()
        ), banned


def test_registry_recognizes_external_bot_evidence_intake_contract():
    c = get_latest_completed_external_bot_evidence_intake_contract()
    assert c["external_bot_evidence_intake_contract_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 External Bot Evidence Intake Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_external_bot_evidence_intake_contract"
    )
    assert c["schema_constant"] == "EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_external_bot_evidence_intake_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_external_bot_evidence_intake_contract_research_only():
    c = get_latest_completed_external_bot_evidence_intake_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_recognized_external_bot_evidence_intake_contract_authorizes_nothing():
    c = get_latest_completed_external_bot_evidence_intake_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the intake contract's own next step is to BUILD the next paper evidence
    # contract -- the global next required action.
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # evidence is never converted into permission; whale tracking is evidence only
    assert "never converted" in reason


def test_recognized_external_bot_evidence_intake_contract_preserves_prior_truth():
    # Recognizing the intake contract must NOT invent a new execution bundle and
    # must NOT disturb the latest bundle / prior readiness contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT == (
        "Block 115 - Crypto-D1 Strategy Candidate Research Readiness Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_external_bot_evidence_intake_contract_deterministic_isolated():
    assert (
        get_latest_completed_external_bot_evidence_intake_contract()
        == get_latest_completed_external_bot_evidence_intake_contract()
    )
    c = get_latest_completed_external_bot_evidence_intake_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_external_bot_evidence_intake_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5n: recognized research-only hyperliquid-whale-evidence (Block 119) -------

def test_latest_completed_hyperliquid_whale_evidence_contract_label():
    assert LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT == (
        "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
    assert (
        get_latest_completed_hyperliquid_whale_evidence_contract_label()
        == LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT.upper()
        ), banned


def test_registry_recognizes_hyperliquid_whale_evidence_contract():
    c = get_latest_completed_hyperliquid_whale_evidence_contract()
    assert c["hyperliquid_whale_evidence_contract_id"] == (
        "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Hyperliquid Whale Evidence Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract"
    )
    assert c["schema_constant"] == "WHALE_EVIDENCE_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_hyperliquid_whale_evidence_contract_research_only():
    c = get_latest_completed_hyperliquid_whale_evidence_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_hyperliquid_whale_evidence_contract_authorizes_nothing():
    c = get_latest_completed_hyperliquid_whale_evidence_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the whale contract's own next step is to BUILD the next paper evidence
    # contract -- the global next required action (funding-rate evidence).
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
    )
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # whale evidence is never converted into permission and needs confirmation
    assert "never converted" in reason
    assert "independent confirmation" in reason


def test_recognized_hyperliquid_whale_evidence_contract_preserves_prior_truth():
    # Recognizing the whale contract must NOT invent a new execution bundle and
    # must NOT disturb the latest bundle / prior intake contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT == (
        "Block 117 - Crypto-D1 External Bot Evidence Intake Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_hyperliquid_whale_evidence_contract_deterministic_isolated():
    assert (
        get_latest_completed_hyperliquid_whale_evidence_contract()
        == get_latest_completed_hyperliquid_whale_evidence_contract()
    )
    c = get_latest_completed_hyperliquid_whale_evidence_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_hyperliquid_whale_evidence_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5o: recognized research-only funding-rate-evidence (Block 121) ------------

def test_latest_completed_funding_rate_evidence_contract_label():
    assert LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT == (
        "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
    )
    assert (
        get_latest_completed_funding_rate_evidence_contract_label()
        == LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT.upper()
        ), banned


def test_registry_recognizes_funding_rate_evidence_contract():
    c = get_latest_completed_funding_rate_evidence_contract()
    assert c["funding_rate_evidence_contract_id"] == (
        "CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Funding Rate Evidence Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_funding_rate_evidence_contract"
    )
    assert c["schema_constant"] == "FUNDING_RATE_EVIDENCE_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_funding_rate_evidence_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_funding_rate_evidence_contract_research_only():
    c = get_latest_completed_funding_rate_evidence_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_funding_rate_evidence_contract_authorizes_nothing():
    c = get_latest_completed_funding_rate_evidence_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the funding-rate contract's own next step is now pinned to BUILD the
    # Bitcoin cycle timing evidence contract, which was inserted after it as a
    # macro timing filter before the global next required action (daily alpha
    # brief). The funding-rate record therefore no longer points at the global
    # next required action.
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # funding-rate evidence is never converted into permission and needs
    # independent confirmation
    assert "never converted" in reason
    assert "independent confirmation" in reason


def test_recognized_funding_rate_evidence_contract_preserves_prior_truth():
    # Recognizing the funding-rate contract must NOT invent a new execution
    # bundle and must NOT disturb the latest bundle / prior whale contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT == (
        "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_whale_contract_next_action_pinned_to_funding_rate():
    # After Block 121, the global NEXT_REQUIRED_ACTION advanced to the daily
    # alpha brief build, but the Block 119 whale record keeps its frozen
    # historical next step: BUILD the funding-rate evidence contract.
    c = get_latest_completed_hyperliquid_whale_evidence_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION


def test_recognized_funding_rate_evidence_contract_deterministic_isolated():
    assert (
        get_latest_completed_funding_rate_evidence_contract()
        == get_latest_completed_funding_rate_evidence_contract()
    )
    c = get_latest_completed_funding_rate_evidence_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_funding_rate_evidence_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5p: recognized research-only bitcoin-cycle-timing-evidence (Block 123) ----

def test_latest_completed_bitcoin_cycle_timing_evidence_contract_label():
    assert LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT == (
        "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )
    assert (
        get_latest_completed_bitcoin_cycle_timing_evidence_contract_label()
        == LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT.upper()
        ), banned


def test_registry_recognizes_bitcoin_cycle_timing_evidence_contract():
    c = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    assert c["bitcoin_cycle_timing_evidence_contract_id"] == (
        "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract"
    )
    assert c["schema_constant"] == (
        "BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION"
    )
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_bitcoin_cycle_timing_evidence_contract_research_only():
    c = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_bitcoin_cycle_timing_evidence_contract_authorizes_nothing():
    c = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the Bitcoin cycle timing record keeps its frozen historical next step:
    # BUILD the daily alpha brief research contract. After Block 126 registered
    # that contract complete, the global next action advanced past it, so the
    # pinned record no longer equals the global.
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # cycle-timing evidence is never converted into permission and needs
    # independent confirmation
    assert "never converted" in reason
    assert "independent confirmation" in reason
    # core rule is preserved on the record's reason
    assert "pay attention, not when to buy" in reason


def test_recognized_bitcoin_cycle_timing_evidence_contract_preserves_prior_truth():
    # Inserting the Bitcoin cycle timing contract must NOT invent a new
    # execution bundle and must NOT disturb the latest bundle / prior contracts.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT == (
        "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
    )
    assert LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT == (
        "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_global_stage_advances_after_daily_alpha_brief_registration():
    # Registering Block 129 (Block 130) DOES advance the global stage and next
    # required action past the daily alpha brief approval build, to the human-
    # controlled real-data QA boundary decision. No stale approval/review/
    # research-build literal remains.
    assert get_current_stage() == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert get_next_required_action() == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert get_current_stage() != (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_REQUIRED"
    )
    assert get_current_stage() != (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_REQUIRED"
    )
    assert get_current_stage() != (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
    )


def test_recognized_funding_rate_next_action_pinned_to_bitcoin_cycle_timing():
    # After Block 123 was inserted after the funding-rate contract, the
    # funding-rate record keeps a frozen pin to its real successor: BUILD the
    # Bitcoin cycle timing evidence contract -- NOT the global next action.
    c = get_latest_completed_funding_rate_evidence_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION


def test_recognized_bitcoin_cycle_timing_evidence_contract_deterministic_isolated():
    assert (
        get_latest_completed_bitcoin_cycle_timing_evidence_contract()
        == get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    )
    c = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5q: recognized research-only daily-alpha-brief-research (Block 125) -------

def test_latest_completed_daily_alpha_brief_research_contract_label():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )
    assert (
        get_latest_completed_daily_alpha_brief_research_contract_label()
        == LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT.upper()
        ), banned


def test_registry_recognizes_daily_alpha_brief_research_contract():
    c = get_latest_completed_daily_alpha_brief_research_contract()
    assert c["daily_alpha_brief_research_contract_id"] == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Daily Alpha Brief Research Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_daily_alpha_brief_research_contract"
    )
    assert c["schema_constant"] == "DAILY_ALPHA_BRIEF_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_daily_alpha_brief_research_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_daily_alpha_brief_research_contract_research_only():
    c = get_latest_completed_daily_alpha_brief_research_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_daily_alpha_brief_research_contract_authorizes_nothing():
    c = get_latest_completed_daily_alpha_brief_research_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # After Block 127 was registered (Block 128), the research record is no
    # longer the latest recognized contract: it keeps a frozen pin to its real
    # successor (BUILD the daily alpha brief review contract), which is NOT the
    # now-advanced global next action (BUILD the approval contract).
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # the brief is what-to-watch evidence, never a trade; highest stance is WATCH
    assert "what to watch and research, never what to trade" in reason
    assert "watch / research_only" in reason
    assert "never converts evidence into permission" in reason


def test_recognized_daily_alpha_brief_preserves_prior_truth():
    # Registering Block 125 must NOT invent a new execution bundle and must NOT
    # disturb the latest bundle or any prior recognized contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT == (
        "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )
    assert LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT == (
        "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
    )
    assert LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT == (
        "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_bitcoin_next_action_pinned_to_daily_alpha_brief_research():
    # After Block 125 was registered, the Block 123 bitcoin-cycle-timing record
    # keeps a frozen pin to its real successor: BUILD the daily alpha brief
    # research contract -- NOT the (now advanced) global next action.
    c = get_latest_completed_bitcoin_cycle_timing_evidence_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION


def test_recognized_daily_alpha_brief_research_contract_deterministic_isolated():
    assert (
        get_latest_completed_daily_alpha_brief_research_contract()
        == get_latest_completed_daily_alpha_brief_research_contract()
    )
    c = get_latest_completed_daily_alpha_brief_research_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_daily_alpha_brief_research_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5r: recognized research-only daily-alpha-brief-review (Block 127) ---------

def test_latest_completed_daily_alpha_brief_review_contract_label():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT == (
        "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
    )
    assert (
        get_latest_completed_daily_alpha_brief_review_contract_label()
        == LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT.upper()
        ), banned


def test_registry_recognizes_daily_alpha_brief_review_contract():
    c = get_latest_completed_daily_alpha_brief_review_contract()
    assert c["daily_alpha_brief_review_contract_id"] == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Daily Alpha Brief Review Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_daily_alpha_brief_review_contract"
    )
    assert c["schema_constant"] == "DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_daily_alpha_brief_review_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_daily_alpha_brief_review_contract_research_only():
    c = get_latest_completed_daily_alpha_brief_review_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_daily_alpha_brief_review_contract_authorizes_nothing():
    c = get_latest_completed_daily_alpha_brief_review_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # After Block 129 was registered (Block 130), the review record is no longer
    # the latest recognized contract: it keeps a frozen pin to its real
    # successor (BUILD the daily alpha brief approval contract), which is NOT the
    # now-advanced global next action (the human-controlled boundary decision).
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # the review escalates for approval, never a trade; highest verdict is READY
    assert "never what to trade" in reason
    assert "never converts evidence into permission" in reason


def test_recognized_daily_alpha_brief_review_preserves_prior_truth():
    # Registering Block 127 must NOT invent a new execution bundle and must NOT
    # disturb the latest bundle or any prior recognized contract, including the
    # Block 125 daily alpha brief research contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )
    assert LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT == (
        "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )
    assert LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT == (
        "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_research_next_action_pinned_to_daily_alpha_brief_review():
    # After Block 127 was registered, the Block 125 daily-alpha-brief-research
    # record keeps a frozen pin to its real successor: BUILD the daily alpha
    # brief review contract -- NOT the (now advanced) global next action.
    c = get_latest_completed_daily_alpha_brief_research_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION


def test_recognized_daily_alpha_brief_review_contract_deterministic_isolated():
    assert (
        get_latest_completed_daily_alpha_brief_review_contract()
        == get_latest_completed_daily_alpha_brief_review_contract()
    )
    c = get_latest_completed_daily_alpha_brief_review_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_daily_alpha_brief_review_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5a: recognized research-only daily-alpha-brief-approval (Block 129) -------

def test_latest_completed_daily_alpha_brief_approval_contract_label():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT == (
        "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
    )
    assert (
        get_latest_completed_daily_alpha_brief_approval_contract_label()
        == LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT.upper()
        ), banned


def test_registry_recognizes_daily_alpha_brief_approval_contract():
    c = get_latest_completed_daily_alpha_brief_approval_contract()
    assert c["daily_alpha_brief_approval_contract_id"] == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Daily Alpha Brief Approval Contract"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract"
    )
    assert c["schema_constant"] == "DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_daily_alpha_brief_approval_contract_research_only():
    c = get_latest_completed_daily_alpha_brief_approval_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_daily_alpha_brief_approval_contract_authorizes_nothing():
    c = get_latest_completed_daily_alpha_brief_approval_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the daily alpha brief approval contract is the latest recognized contract,
    # so its own next step IS the global next required action: the human-
    # controlled real-data QA boundary decision (NOT a build step).
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # an approval only files the reviewed brief as a research record, never trade
    assert "never as a trade" in reason
    assert "never converts evidence into permission" in reason


def test_recognized_daily_alpha_brief_approval_preserves_prior_truth():
    # Registering Block 129 must NOT invent a new execution bundle and must NOT
    # disturb the latest bundle or any prior recognized contract, including the
    # Block 127 daily alpha brief review contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT == (
        "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
    )
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )
    assert LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT == (
        "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_review_next_action_pinned_to_daily_alpha_brief_approval():
    # After Block 129 was registered, the Block 127 daily-alpha-brief-review
    # record keeps a frozen pin to its real successor: BUILD the daily alpha
    # brief approval contract -- NOT the (now advanced) global next action.
    c = get_latest_completed_daily_alpha_brief_review_contract()
    assert c["next_required_action"] == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert c["next_required_action"] != NEXT_REQUIRED_ACTION


def test_recognized_daily_alpha_brief_approval_contract_deterministic_isolated():
    assert (
        get_latest_completed_daily_alpha_brief_approval_contract()
        == get_latest_completed_daily_alpha_brief_approval_contract()
    )
    c = get_latest_completed_daily_alpha_brief_approval_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_daily_alpha_brief_approval_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


# --- 5z: recognized research-only cohort-independence (Block 132) -------------

def test_latest_completed_strategy_evidence_scoring_contract_label():
    assert LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT == (
        "Block 131 - Crypto-D1 Strategy Evidence Scoring Contract"
    )
    assert (
        get_latest_completed_strategy_evidence_scoring_contract_label()
        == LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT.upper()
        ), banned


def test_registry_recognizes_strategy_evidence_scoring_contract():
    c = get_latest_completed_strategy_evidence_scoring_contract()
    assert c["strategy_evidence_scoring_contract_id"] == (
        "CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Strategy Evidence Scoring Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_strategy_evidence_scoring_contract"
    )
    assert c["schema_constant"] == "STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_strategy_evidence_scoring_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_strategy_evidence_scoring_contract_research_only():
    c = get_latest_completed_strategy_evidence_scoring_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_strategy_evidence_scoring_contract_authorizes_nothing():
    c = get_latest_completed_strategy_evidence_scoring_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the evidence-scoring contract is a recognized contract, but registering it
    # is purely additive: its own next step IS the unchanged global next required
    # action -- the human-controlled real-data QA boundary decision (NOT a build
    # step).
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "never converts evidence into permission" in reason
    assert "purely additive latest-completed metadata" in reason


def test_recognized_strategy_evidence_scoring_preserves_prior_truth():
    # Registering Block 131 must NOT invent a new execution bundle, must NOT
    # advance the boundary stage, and must NOT disturb the latest bundle or any
    # prior recognized contract.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_strategy_evidence_scoring_contract_deterministic_isolated():
    assert (
        get_latest_completed_strategy_evidence_scoring_contract()
        == get_latest_completed_strategy_evidence_scoring_contract()
    )
    c = get_latest_completed_strategy_evidence_scoring_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_strategy_evidence_scoring_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_latest_completed_cohort_independence_contract_label():
    assert LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert (
        get_latest_completed_cohort_independence_contract_label()
        == LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT.upper()
        ), banned


def test_registry_recognizes_cohort_independence_contract():
    c = get_latest_completed_cohort_independence_contract()
    assert c["cohort_independence_contract_id"] == (
        "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract"
    )
    assert c["schema_constant"] == "COHORT_INDEPENDENCE_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_cohort_independence_contract_research_only():
    c = get_latest_completed_cohort_independence_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_cohort_independence_contract_authorizes_nothing():
    c = get_latest_completed_cohort_independence_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # the cohort-independence contract is the latest recognized contract, but
    # registering it is purely additive: its own next step IS the unchanged
    # global next required action -- the human-controlled real-data QA boundary
    # decision (NOT a build step).
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "never converts evidence into permission" in reason
    assert "purely additive latest-completed metadata" in reason


def test_recognized_cohort_independence_preserves_prior_truth():
    # Registering Block 132 must NOT invent a new execution bundle, must NOT
    # advance the boundary stage, and must NOT disturb the latest bundle or any
    # prior recognized contract (e.g. the Block 129 approval contract).
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT == (
        "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_cohort_independence_contract_deterministic_isolated():
    assert (
        get_latest_completed_cohort_independence_contract()
        == get_latest_completed_cohort_independence_contract()
    )
    c = get_latest_completed_cohort_independence_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_cohort_independence_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_latest_completed_real_data_qa_boundary_decision_contract_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT == (
        "Block 134 - Crypto-D1 Real Data QA Boundary Decision Contract"
    )
    assert (
        get_latest_completed_real_data_qa_boundary_decision_contract_label()
        == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT
    )
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT.upper()
        ), banned


def test_registry_recognizes_real_data_qa_boundary_decision_contract():
    c = get_latest_completed_real_data_qa_boundary_decision_contract()
    assert c["real_data_qa_boundary_decision_contract_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Real Data QA Boundary Decision Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract"
    )
    assert c["schema_constant"] == "RDQ_BOUNDARY_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_real_data_qa_boundary_decision_contract_research_only():
    c = get_latest_completed_real_data_qa_boundary_decision_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_boundary_decision_contract_authorizes_nothing():
    c = get_latest_completed_real_data_qa_boundary_decision_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    # registering Block 134 is purely additive: its own next step IS the unchanged
    # global next required action -- the human-controlled real-data QA boundary
    # decision (NOT a build step).
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "never converts evidence into permission" in reason
    assert "purely additive latest-completed metadata" in reason
    # recognizing the boundary-decision contract never unlocks real_data_qa
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_boundary_decision_preserves_prior_truth():
    # Registering Block 134 must NOT invent a new execution bundle, must NOT
    # advance the boundary stage, and must NOT disturb the latest bundle or any
    # prior recognized contract (e.g. the Block 132 cohort-independence contract).
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_real_data_qa_boundary_decision_contract_deterministic_isolated():
    assert (
        get_latest_completed_real_data_qa_boundary_decision_contract()
        == get_latest_completed_real_data_qa_boundary_decision_contract()
    )
    c = get_latest_completed_real_data_qa_boundary_decision_contract()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_real_data_qa_boundary_decision_contract()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_latest_completed_real_data_qa_human_approval_packet_contract_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT == (
        "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    assert (
        get_latest_completed_real_data_qa_human_approval_packet_contract_label()
        == LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT.upper()
        ), banned


def test_registry_recognizes_real_data_qa_human_approval_packet_contract():
    c = get_latest_completed_real_data_qa_human_approval_packet_contract()
    assert c["real_data_qa_human_approval_packet_contract_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract"
    )
    assert c["schema_constant"] == "RDQ_APPROVAL_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_real_data_qa_human_approval_packet_contract_research_only():
    c = get_latest_completed_real_data_qa_human_approval_packet_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_human_approval_packet_contract_authorizes_nothing():
    c = get_latest_completed_real_data_qa_human_approval_packet_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_latest_completed_real_data_qa_readiness_checklist_contract_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT == (
        "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    assert (
        get_latest_completed_real_data_qa_readiness_checklist_contract_label()
        == LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT.upper()
        ), banned


def test_registry_recognizes_real_data_qa_readiness_checklist_contract():
    c = get_latest_completed_real_data_qa_readiness_checklist_contract()
    assert c["real_data_qa_readiness_checklist_contract_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
    )
    assert c["name"] == (
        "Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract"
    )
    assert c["schema_constant"] == "RDQ_READINESS_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_real_data_qa_readiness_checklist_contract_research_only():
    c = get_latest_completed_real_data_qa_readiness_checklist_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_readiness_checklist_contract_authorizes_nothing():
    c = get_latest_completed_real_data_qa_readiness_checklist_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_block_136_contracts_deterministic_isolated():
    for getter in (
        get_latest_completed_real_data_qa_human_approval_packet_contract,
        get_latest_completed_real_data_qa_readiness_checklist_contract,
    ):
        assert getter() == getter()
        c = getter()
        c["executes"] = True
        c["research_universe"].append("TAMPERED")
        c["candidate_family_ids"].append("TAMPERED")
        fresh = getter()
        assert fresh["executes"] is False
        assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
        assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_block_136_registration_preserves_prior_truth():
    # Registering both Block 136 contracts must NOT advance the boundary stage,
    # must NOT disturb the latest bundle, and must NOT disturb the Block 134
    # boundary-decision contract recognition.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT == (
        "Block 134 - Crypto-D1 Real Data QA Boundary Decision Contract"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_latest_completed_overnight_research_autopilot_controller_label():
    assert LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert (
        get_latest_completed_overnight_research_autopilot_controller_label()
        == LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER.upper()
        ), banned


def test_registry_recognizes_overnight_research_autopilot_controller():
    c = get_latest_completed_overnight_research_autopilot_controller()
    assert c["overnight_research_autopilot_controller_id"] == (
        "SPARTA_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER"
    )
    assert c["name"] == "SPARTA Overnight Research Autopilot Controller"
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_overnight_research_autopilot_controller"
    )
    assert c["schema_constant"] == "CONTROLLER_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_overnight_research_autopilot_controller.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_overnight_research_autopilot_controller_research_only():
    c = get_latest_completed_overnight_research_autopilot_controller()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["per_run_push_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_overnight_research_autopilot_controller_authorizes_nothing():
    c = get_latest_completed_overnight_research_autopilot_controller()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_overnight_research_autopilot_controller_isolated():
    getter = get_latest_completed_overnight_research_autopilot_controller
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_block_152_registration_preserves_prior_truth():
    # Registering the Block 152 autopilot controller must NOT advance the
    # boundary stage, must NOT disturb the latest bundle, and must NOT disturb
    # the Block 136 readiness-checklist recognition.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT == (
        "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_latest_completed_real_data_qa_human_approval_packet_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    assert (
        get_latest_completed_real_data_qa_human_approval_packet_label()
        == LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET.upper()
        ), banned


def test_registry_recognizes_real_data_qa_human_approval_packet():
    c = get_latest_completed_real_data_qa_human_approval_packet()
    assert c["real_data_qa_human_approval_packet_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_HUMAN_APPROVAL_PACKET"
    )
    assert c["name"] == (
        "Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet"
    )
    assert c["schema_constant"] == "PACKET_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_real_data_qa_human_approval_packet_research_only():
    c = get_latest_completed_real_data_qa_human_approval_packet()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_human_approval_packet_authorizes_nothing():
    c = get_latest_completed_real_data_qa_human_approval_packet()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_human_approval_packet_isolated():
    getter = get_latest_completed_real_data_qa_human_approval_packet
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_block_155_registration_preserves_prior_truth():
    # Registering the Block 155 real-data-QA boundary-decision human approval
    # packet must NOT advance the boundary stage, must NOT disturb the latest
    # bundle, and must NOT disturb the Block 152 controller recognition.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_latest_completed_real_data_qa_boundary_decision_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION == (
        "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    assert (
        get_latest_completed_real_data_qa_boundary_decision_label()
        == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION.upper()
        ), banned


def test_registry_recognizes_real_data_qa_boundary_decision():
    c = get_latest_completed_real_data_qa_boundary_decision()
    assert c["real_data_qa_boundary_decision_id"] == (
        "CRYPTO_D1_HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    )
    assert c["name"] == (
        "Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision"
    )
    assert c["schema_constant"] == "DECISION_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision.v1"
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["validates_protocol_id"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_recognized_real_data_qa_boundary_decision_research_only():
    c = get_latest_completed_real_data_qa_boundary_decision()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_boundary_decision_authorizes_nothing():
    c = get_latest_completed_real_data_qa_boundary_decision()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_boundary_decision_isolated():
    getter = get_latest_completed_real_data_qa_boundary_decision
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    c["candidate_family_ids"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


def test_block_158_registration_preserves_prior_truth():
    # Registering the Block 158 human-controlled real-data-QA boundary-decision
    # layer must NOT advance the boundary stage, must NOT disturb the latest
    # bundle, must NOT disturb the Block 152 controller or Block 155 packet
    # recognition.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_latest_completed_pipeline_coverage_reconciliation_label():
    assert LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION == (
        "Block 161 - Crypto-D1 Pipeline Coverage Reconciliation"
    )
    assert (
        get_latest_completed_pipeline_coverage_reconciliation_label()
        == LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION.upper()
        ), banned


def test_registry_recognizes_pipeline_coverage_reconciliation():
    c = get_latest_completed_pipeline_coverage_reconciliation()
    assert c["pipeline_coverage_reconciliation_id"] == (
        "CRYPTO_D1_PIPELINE_COVERAGE_RECONCILIATION"
    )
    assert c["name"] == "Crypto-D1 Pipeline Coverage Reconciliation"
    assert c["label"] == LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION
    assert c["defined"] is True
    assert c["complete"] is True
    # 13 existing-but-parked downstream modules cataloged as coverage metadata.
    assert c["parked_module_count"] == 13
    assert len(c["parked_modules"]) == 13


def test_recognized_pipeline_coverage_reconciliation_research_only():
    c = get_latest_completed_pipeline_coverage_reconciliation()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_pipeline_coverage_modules_are_parked_not_active():
    # Every cataloged module must be EXISTS/TESTED/COMMITTED but PARKED and
    # NOT an active/executable stage -- coverage metadata, not an execution
    # permit.
    c = get_latest_completed_pipeline_coverage_reconciliation()
    assert c["parked_modules"], "expected a non-empty parked-module catalog"
    for m in c["parked_modules"]:
        assert m["exists"] is True, m["name"]
        assert m["tested"] is True, m["name"]
        assert m["committed"] is True, m["name"]
        assert m["registered_as_active_stage"] is False, m["name"]
        assert m["parked"] is True, m["name"]
        assert m["active"] is False, m["name"]
        assert m["executes"] is False, m["name"]
        assert m["status"] == "EXISTS_TESTED_COMMITTED_PARKED_NOT_ACTIVE", (
            m["name"]
        )


def test_recognized_pipeline_coverage_reconciliation_authorizes_nothing():
    c = get_latest_completed_pipeline_coverage_reconciliation()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_pipeline_coverage_reconciliation_isolated():
    getter = get_latest_completed_pipeline_coverage_reconciliation
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["parked_module_count"] = 999
    c["research_universe"].append("TAMPERED")
    c["parked_modules"][0]["active"] = True
    c["parked_modules"].append({"name": "TAMPERED"})
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["parked_module_count"] == 13
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert all(m["active"] is False for m in fresh["parked_modules"])
    assert len(fresh["parked_modules"]) == 13


def test_latest_completed_real_data_qa_boundary_readiness_review_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    assert (
        get_latest_completed_real_data_qa_boundary_readiness_review_label()
        == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW.upper()
        ), banned


def test_registry_recognizes_real_data_qa_boundary_readiness_review():
    c = get_latest_completed_real_data_qa_boundary_readiness_review()
    assert c["real_data_qa_boundary_readiness_review_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW"
    )
    assert c["name"] == "Crypto-D1 Real Data QA Boundary Readiness Review"
    assert c["label"] == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review"
    )


def test_recognized_real_data_qa_boundary_readiness_review_research_only():
    c = get_latest_completed_real_data_qa_boundary_readiness_review()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_boundary_readiness_review_authorizes_nothing():
    c = get_latest_completed_real_data_qa_boundary_readiness_review()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_boundary_readiness_review_isolated():
    getter = get_latest_completed_real_data_qa_boundary_readiness_review
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_real_data_qa_boundary_decision_packet_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET == (
        "Block 170 - Crypto-D1 Real Data QA Boundary Decision Packet"
    )
    assert (
        get_latest_completed_real_data_qa_boundary_decision_packet_label()
        == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET.upper()
        ), banned


def test_registry_recognizes_real_data_qa_boundary_decision_packet():
    c = get_latest_completed_real_data_qa_boundary_decision_packet()
    assert c["real_data_qa_boundary_decision_packet_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_PACKET"
    )
    assert c["name"] == "Crypto-D1 Real Data QA Boundary Decision Packet"
    assert c["label"] == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "PACKET_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet"
    )


def test_recognized_real_data_qa_boundary_decision_packet_research_only():
    c = get_latest_completed_real_data_qa_boundary_decision_packet()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_boundary_decision_packet_authorizes_nothing():
    c = get_latest_completed_real_data_qa_boundary_decision_packet()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_boundary_decision_packet_isolated():
    getter = get_latest_completed_real_data_qa_boundary_decision_packet
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_real_data_qa_plan_only_contract_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT == (
        "Block 171 - Crypto-D1 Real Data QA Plan-Only Contract"
    )
    assert (
        get_latest_completed_real_data_qa_plan_only_contract_label()
        == LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT.upper()
        ), banned


def test_registry_recognizes_real_data_qa_plan_only_contract():
    c = get_latest_completed_real_data_qa_plan_only_contract()
    assert c["real_data_qa_plan_only_contract_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_PLAN_ONLY_CONTRACT"
    )
    assert c["name"] == "Crypto-D1 Real Data QA Plan-Only Contract"
    assert c["label"] == LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "PLAN_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_plan_only_contract.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_plan_only_contract"
    )


def test_recognized_real_data_qa_plan_only_contract_research_only():
    c = get_latest_completed_real_data_qa_plan_only_contract()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_plan_only_contract_authorizes_nothing():
    c = get_latest_completed_real_data_qa_plan_only_contract()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_plan_only_contract_isolated():
    getter = get_latest_completed_real_data_qa_plan_only_contract
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_real_data_qa_plan_approval_decision_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION == (
        "Block 172 - Crypto-D1 Real Data QA Plan Approval Decision Contract"
    )
    assert (
        get_latest_completed_real_data_qa_plan_approval_decision_label()
        == LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION.upper()
        ), banned


def test_registry_recognizes_real_data_qa_plan_approval_decision():
    c = get_latest_completed_real_data_qa_plan_approval_decision()
    assert c["real_data_qa_plan_approval_decision_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_PLAN_APPROVAL_DECISION"
    )
    assert c["name"] == "Crypto-D1 Real Data QA Plan Approval Decision Contract"
    assert c["label"] == LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "DECISION_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract"
    )


def test_recognized_real_data_qa_plan_approval_decision_research_only():
    c = get_latest_completed_real_data_qa_plan_approval_decision()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_plan_approval_decision_authorizes_nothing():
    c = get_latest_completed_real_data_qa_plan_approval_decision()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_plan_approval_decision_isolated():
    getter = get_latest_completed_real_data_qa_plan_approval_decision
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_real_data_qa_boundary_final_decision_label():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION == (
        "Block 174 - Crypto-D1 Real Data QA Boundary Final Decision Contract"
    )
    assert (
        get_latest_completed_real_data_qa_boundary_final_decision_label()
        == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION.upper()
        ), banned


def test_registry_recognizes_real_data_qa_boundary_final_decision():
    c = get_latest_completed_real_data_qa_boundary_final_decision()
    assert c["real_data_qa_boundary_final_decision_id"] == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_FINAL_DECISION"
    )
    assert c["name"] == "Crypto-D1 Real Data QA Boundary Final Decision Contract"
    assert c["label"] == LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "DECISION_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_final_decision_contract.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_real_data_qa_boundary_final_decision_contract"
    )


def test_recognized_real_data_qa_boundary_final_decision_research_only():
    c = get_latest_completed_real_data_qa_boundary_final_decision()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_real_data_qa_boundary_final_decision_authorizes_nothing():
    c = get_latest_completed_real_data_qa_boundary_final_decision()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_real_data_qa_boundary_final_decision_isolated():
    getter = get_latest_completed_real_data_qa_boundary_final_decision
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_resume_policy_chain_labels():
    # Blocks 175-177: the research-only Resume-Policy chain recognized as additive
    # latest-completed evidence -- three separate labels for traceability. Each
    # label getter is the registry single source of truth and unlocks nothing.
    assert LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT == (
        "Block 175 - Crypto-D1 V2 Resume-Policy Research & Simulation Plan Contract"
    )
    assert (
        get_latest_completed_resume_policy_research_plan_contract_label()
        == LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT
    )
    assert LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT == (
        "Block 176 - Crypto-D1 V2 Resume-Policy Simulation Runner Contract"
    )
    assert (
        get_latest_completed_resume_policy_simulation_runner_contract_label()
        == LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT
    )
    assert LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT == (
        "Block 177 - Crypto-D1 V2 Resume-Policy Results Review / Decision Contract"
    )
    assert (
        get_latest_completed_resume_policy_results_review_contract_label()
        == LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT
    )
    # recognizing the chain names no execution capability
    for label in (
        LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT,
        LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT,
        LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT,
    ):
        for banned in ("PAPER", "LIVE", "BROKER", "EXCHANGE", "EXECUTION",
                       "ORDER", "UNLOCK", "PROMOTE"):
            assert banned not in label.upper(), banned


def test_latest_completed_public_spot_source_evaluation_label():
    assert LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION == (
        "Block 167 - Crypto-D1 Public Read-Only Spot Source Evaluation Contract"
    )
    assert (
        get_latest_completed_public_spot_source_evaluation_label()
        == LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION.upper()
        ), banned


def test_registry_recognizes_public_spot_source_evaluation():
    c = get_latest_completed_public_spot_source_evaluation()
    assert c["public_spot_source_evaluation_id"] == (
        "CRYPTO_D1_PUBLIC_READ_ONLY_SPOT_SOURCE_EVALUATION"
    )
    assert c["name"] == "Crypto-D1 Public Read-Only Spot Source Evaluation"
    assert c["label"] == LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "SOURCE_EVALUATION_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_public_read_only_spot_source_evaluation.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_public_read_only_spot_source_evaluation"
    )


def test_recognized_public_spot_source_evaluation_research_only():
    c = get_latest_completed_public_spot_source_evaluation()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_public_spot_source_evaluation_authorizes_nothing():
    c = get_latest_completed_public_spot_source_evaluation()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_public_spot_source_evaluation_isolated():
    getter = get_latest_completed_public_spot_source_evaluation
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_concrete_spot_provider_adapter_spec_label():
    assert LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC == (
        "Block 168 - Crypto-D1 Concrete Read-Only Spot Provider Adapter Spec"
    )
    assert (
        get_latest_completed_concrete_spot_provider_adapter_spec_label()
        == LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC.upper()
        ), banned


def test_registry_recognizes_concrete_spot_provider_adapter_spec():
    c = get_latest_completed_concrete_spot_provider_adapter_spec()
    assert c["concrete_spot_provider_adapter_spec_id"] == (
        "CRYPTO_D1_CONCRETE_READ_ONLY_SPOT_PROVIDER_ADAPTER_SPEC"
    )
    assert c["name"] == "Crypto-D1 Concrete Read-Only Spot Provider Adapter Spec"
    assert c["label"] == LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "ADAPTER_SPEC_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_concrete_read_only_spot_provider_adapter_spec.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_concrete_read_only_spot_provider_adapter_spec"
    )


def test_recognized_concrete_spot_provider_adapter_spec_research_only():
    c = get_latest_completed_concrete_spot_provider_adapter_spec()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_concrete_spot_provider_adapter_spec_authorizes_nothing():
    c = get_latest_completed_concrete_spot_provider_adapter_spec()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_concrete_spot_provider_adapter_spec_isolated():
    getter = get_latest_completed_concrete_spot_provider_adapter_spec
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_latest_completed_selected_spot_provider_fetch_runner_dry_run_label():
    assert LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN == (
        "Block 169 - Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry "
        "Run"
    )
    assert (
        get_latest_completed_selected_spot_provider_fetch_runner_dry_run_label()
        == LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN
    )
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION", "ORDER", "UNLOCK"):
        assert banned not in (
            LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN.upper()
        ), banned


def test_registry_recognizes_selected_spot_provider_fetch_runner_dry_run():
    c = get_latest_completed_selected_spot_provider_fetch_runner_dry_run()
    assert c["selected_spot_provider_fetch_runner_dry_run_id"] == (
        "CRYPTO_D1_SELECTED_READ_ONLY_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN"
    )
    assert c["name"] == (
        "Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run"
    )
    assert c["label"] == (
        LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN
    )
    assert c["defined"] is True
    assert c["complete"] is True
    assert c["schema_constant"] == "DRY_RUN_SCHEMA_VERSION"
    assert c["schema_version"] == (
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.v1"
    )
    assert c["module"] == (
        "sparta_commander."
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run"
    )


def test_recognized_selected_spot_provider_fetch_runner_dry_run_research_only():
    c = get_latest_completed_selected_spot_provider_fetch_runner_dry_run()
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    assert c["requires_independent_confirmation"] is True


def test_recognized_selected_spot_provider_fetch_runner_dry_run_authorizes_nothing():
    c = get_latest_completed_selected_spot_provider_fetch_runner_dry_run()
    for flag in _CAPABILITY_FLAGS:
        assert c[flag] is False, flag
    assert c["next_required_action"] == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    assert c["next_required_action"] == NEXT_REQUIRED_ACTION
    assert not c["next_required_action"].startswith("BUILD_")
    assert c["stage"] == CURRENT_STAGE
    assert c["next_gate"] == CURRENT_STAGE
    reason = c["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive latest-completed metadata" in reason
    assert "never an unlock of real_data_qa" in reason


def test_recognized_selected_spot_provider_fetch_runner_dry_run_isolated():
    getter = get_latest_completed_selected_spot_provider_fetch_runner_dry_run
    assert getter() == getter()
    c = getter()
    c["executes"] = True
    c["research_universe"].append("TAMPERED")
    fresh = getter()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]


def test_block_161_registration_preserves_prior_truth():
    # Registering the Block 161 pipeline coverage reconciliation layer must NOT
    # advance the boundary stage, must NOT disturb the latest bundle, and must
    # NOT disturb the Block 152/155/158 recognitions.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    assert LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION == (
        "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS_REQUIRED"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"
    )
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_registry_version_stable():
    assert REGISTRY_VERSION == "v1"
    assert REGISTRY_MODE == "RESEARCH_ONLY"


# --- 6: determinism + mutation isolation -----------------------------------

def test_repeated_calls_are_identical():
    assert list_registered_bundles() == list_registered_bundles()
    assert list_completed_bundles() == list_completed_bundles()
    assert get_latest_completed_bundle() == get_latest_completed_bundle()
    assert get_registry_safety_posture() == get_registry_safety_posture()


def test_returned_structures_are_mutation_isolated():
    a = list_registered_bundles()
    a[0]["complete"] = False
    a[0]["executes"] = True
    assert list_registered_bundles()[0]["complete"] is True
    assert list_registered_bundles()[0]["executes"] is False
    p = get_registry_safety_posture()
    p["unlocks_paper_live"] = True
    assert get_registry_safety_posture()["unlocks_paper_live"] is False
    latest = get_latest_completed_bundle()
    latest["name"] = "TAMPERED"
    assert get_latest_completed_bundle()["name"] != "TAMPERED"


# --- 7: pure stdlib import-root audit ---------------------------------------

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 8: forbidden-surface audit (no IO / network / exec / control) ----------

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# --- 9: commander_2_safety allowlist ---------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_mission_flow_bundle_registry.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_mission_flow_bundle_registry.py"' in src
    )
