"""Tests for the Strategy Factory Mission Flow status adapter (Block 71).

The adapter is a PURE, stdlib-only, read-only display/status feed for the JARVIS
"Mission Flow" panel. It maps where the Strategy Factory backbone stands as of
Bundle 54 (Crypto-D1 research-only dry-run research archive or closure contract
complete, which closes the research-only dry-run lane) and proves it executes
nothing and unlocks nothing real.

Coverage:
- stable output schema (keys + types)
- mode RESEARCH_ONLY, read_only True, executes False, human_approval_required True
- Bundles 42-54 recognized complete; the next research-only protocol (Crypto-D1
  Strategy Candidate Protocol v1, Block 95) is recognized DEFINED/COMPLETE; the
  Crypto-D1 Strategy Candidate Protocol Contract (Block 97) is recognized
  COMPLETE; and the next stage is a research-only planning step (BUILD the
  candidate-family-selection contract, not real execution)
- Real Data QA blocked, Baseline Backtest blocked
- Paper Trading Gate locked, Micro-Live Gate locked + never automated
- no stage unlocks real data / QA / baseline / backtest / paper / live /
  broker / exchange / automation / runtime writes / registry writes /
  dashboard writes
- deterministic repeated calls; mutation-isolated copies
- no IO required for default status (stdlib import-root + forbidden-surface audit)
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_mission_flow_status import (
    MISSION_FLOW_VERSION,
    MISSION_FLOW_MODE,
    MISSION_FLOW_SAFETY_POSTURE,
    STATE_PASSED,
    STATE_COMPLETE,
    STATE_CURRENT,
    STATE_NEXT,
    STATE_BLOCKED,
    STATE_LOCKED,
    CURRENT_STAGE,
    LATEST_COMPLETED_BUNDLE,
    LATEST_COMPLETED_PROTOCOL,
    LATEST_COMPLETED_PROTOCOL_CONTRACT,
    LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT,
    STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT,
    STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT,
    CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT,
    CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION,
    NEXT_REQUIRED_ACTION,
    human_workflow_lane,
    machine_pipeline_lane,
    blocked_gates,
    safety_flags,
    get_mission_flow_status,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_mission_flow_status.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)


# --- 1: stable top-level schema --------------------------------------------

def test_status_schema_is_stable():
    s = get_mission_flow_status()
    assert set(s.keys()) == {
        "mission_flow_version",
        "mode",
        "read_only",
        "executes",
        "human_approval_required",
        "current_stage",
        "latest_completed_bundle",
        "latest_completed_protocol",
        "latest_completed_protocol_contract",
        "latest_completed_family_selection_contract",
        "latest_completed_family_review_contract",
        "latest_completed_research_plan_contract",
        "latest_completed_research_plan_review_contract",
        "latest_completed_research_plan_approval_contract",
        "latest_completed_research_design_contract",
        "latest_completed_research_design_review_contract",
        "latest_completed_research_design_approval_contract",
        "latest_completed_research_readiness_contract",
        "latest_completed_external_bot_evidence_intake_contract",
        "latest_completed_hyperliquid_whale_evidence_contract",
        "latest_completed_funding_rate_evidence_contract",
        "next_required_action",
        "safety_posture",
        "human_workflow",
        "machine_pipeline",
        "blocked_gates",
        "safety",
    }
    assert s["mission_flow_version"] == MISSION_FLOW_VERSION == "v1"
    assert isinstance(s["human_workflow"], list)
    assert isinstance(s["machine_pipeline"], list)
    assert isinstance(s["blocked_gates"], list)
    assert isinstance(s["safety"], dict)
    assert isinstance(s["safety_posture"], dict)


def test_lane_rows_have_stable_keys():
    for lane in (human_workflow_lane(), machine_pipeline_lane(), blocked_gates()):
        assert lane, "lane must not be empty"
        for row in lane:
            assert set(row.keys()) == {"id", "label", "state", "reason"}
            for v in row.values():
                assert isinstance(v, str) and v


# --- 2: posture -------------------------------------------------------------

def test_mode_and_posture_flags():
    s = get_mission_flow_status()
    assert s["mode"] == MISSION_FLOW_MODE == "RESEARCH_ONLY"
    assert s["read_only"] is True
    assert s["executes"] is False
    assert s["human_approval_required"] is True


def test_safety_posture_all_false_except_gates():
    assert MISSION_FLOW_SAFETY_POSTURE["mode"] == "RESEARCH_ONLY"
    assert MISSION_FLOW_SAFETY_POSTURE["read_only"] is True
    assert MISSION_FLOW_SAFETY_POSTURE["human_approval_required"] is True
    for k, v in MISSION_FLOW_SAFETY_POSTURE.items():
        if k in ("mode", "read_only", "human_approval_required"):
            continue
        assert v is False, f"posture flag {k} must be False"


def test_safety_flags_all_false():
    flags = safety_flags()
    assert set(flags.keys()) == {
        "real_data", "qa", "baseline", "backtest", "simulation",
        "paper", "live", "broker", "exchange", "automation",
        "runtime_writes", "registry_writes", "dashboard_writes",
    }
    assert all(v is False for v in flags.values())


# --- 3: Bundles 42-54 complete; next = research-only next-protocol definition

def test_bundles_42_through_54_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    for stage_id in (
        "crypto_d1_acquire_decision_contract",          # Bundle 42
        "crypto_d1_source_class_contract",              # Bundle 43
        "crypto_d1_source_specification_contract",      # Bundle 44
        "crypto_d1_offline_acquisition_plan_contract",  # Bundle 45
        "crypto_d1_pre_acquisition_human_gate_contract",  # Bundle 46
        "crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # Bundle 47  # noqa: E501
        "crypto_d1_post_boundary_research_only_next_step_contract",  # Bundle 48
        "crypto_d1_research_only_dry_run_preview_contract",  # Bundle 49
        "crypto_d1_research_only_dry_run_review_contract",  # Bundle 50
        "crypto_d1_research_only_dry_run_decision_contract",  # Bundle 51
        "crypto_d1_research_only_dry_run_decision_review_contract",  # Bundle 52
        "crypto_d1_research_only_dry_run_final_decision_contract",  # Bundle 53
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract",  # Bundle 54  # noqa: E501
    ):
        assert pipe[stage_id]["state"] == STATE_COMPLETE, stage_id


def test_bundle45_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_offline_acquisition_plan_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 45" in row["reason"]


def test_bundle46_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_pre_acquisition_human_gate_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 46" in row["reason"]


def test_bundle47_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_human_approved_offline_acquisition_execution_boundary_contract"]  # noqa: E501
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 47" in row["reason"]


def test_bundle47_authorizes_nothing_executes_nothing():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    reason = pipe["crypto_d1_human_approved_offline_acquisition_execution_boundary_contract"]["reason"].lower()  # noqa: E501
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # the boundary contract existing does not flip any real capability on
    assert all(v is False for v in safety_flags().values())
    assert get_mission_flow_status()["executes"] is False


def test_bundle48_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_post_boundary_research_only_next_step_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 48" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle49_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_preview_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 49" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle50_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 50" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle51_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_decision_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 51" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle52_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_decision_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 52" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle53_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_final_decision_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 53" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle54_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe[
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract"
    ]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 54" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_latest_completed_bundle_is_bundle54():
    assert "Bundle 54" in LATEST_COMPLETED_BUNDLE
    assert "Research Archive or Closure" in LATEST_COMPLETED_BUNDLE
    assert "Contract" in LATEST_COMPLETED_BUNDLE
    assert get_mission_flow_status()["latest_completed_bundle"] == LATEST_COMPLETED_BUNDLE


def test_next_required_action_is_build_daily_alpha_brief_research_contract():
    assert NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )
    # the readiness paper chain continues into the research-only external-evidence
    # sub-chain; the only next step is to BUILD another paper research contract --
    # it never authorizes real work and treats daily-alpha-brief signals as evidence.
    assert NEXT_REQUIRED_ACTION.startswith("BUILD_")
    assert "DAILY_ALPHA_BRIEF" in NEXT_REQUIRED_ACTION
    assert "CONTRACT" in NEXT_REQUIRED_ACTION
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "ORDER", "TRACK"):
        assert banned not in NEXT_REQUIRED_ACTION, banned
    s = get_mission_flow_status()
    assert s["next_required_action"] == NEXT_REQUIRED_ACTION
    # the next research-contract build still unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    nxt = pipe["crypto_d1_daily_alpha_brief_research_contract"]
    assert nxt["state"] == STATE_NEXT


def test_next_protocol_definition_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_next_protocol_definition"]
    assert row["state"] == STATE_COMPLETE
    reason = row["reason"].lower()
    assert "protocol defined" in reason
    assert "btc/eth/sol" in reason
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_protocol_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_protocol_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 97" in row["reason"]
    reason = row["reason"].lower()
    assert "validates" in reason
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_family_selection_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_family_selection_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 99" in row["reason"]
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "validates" in reason
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_family_review_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_family_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 101" in row["reason"]
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "reviews" in reason
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_research_plan_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_plan_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 103" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "validates" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_research_plan_review_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_plan_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 105" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "reviews" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_research_plan_approval_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_plan_approval_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 107" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "records" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_research_design_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_design_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 109" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "details" in reason
    assert "executes nothing" in reason


def test_strategy_candidate_research_design_review_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_design_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 111" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason


def test_strategy_candidate_research_design_approval_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_design_approval_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 113" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason


def test_strategy_candidate_research_readiness_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_candidate_research_readiness_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 115" in row["reason"]
    assert STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # readiness is paper readiness only and never opens real_data_qa
    assert "real_data_qa stays blocked" in reason


def test_external_bot_evidence_intake_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_external_bot_evidence_intake_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 117" in row["reason"]
    assert STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # every execution-capable idea is blocked; evidence is never permission
    assert "blocked_execution_feature" in reason
    assert "never converting evidence into" in reason


def test_hyperliquid_whale_evidence_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_hyperliquid_whale_evidence_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 119" in row["reason"]
    assert CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # every execution-capable whale idea is blocked; evidence is never permission
    assert "blocked_execution_feature" in reason
    assert "needs_independent_confirmation" in reason
    assert "never converting whale evidence into" in reason


def test_funding_rate_evidence_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_funding_rate_evidence_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 121" in row["reason"]
    assert CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # every execution-capable funding idea is blocked; evidence is never permission
    assert "blocked_execution_feature" in reason
    assert "needs_independent_confirmation" in reason
    assert "never converting funding-rate" in reason


def test_daily_alpha_brief_research_contract_is_next():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_daily_alpha_brief_research_contract"]
    assert row["state"] == STATE_NEXT
    assert NEXT_REQUIRED_ACTION in row["reason"]
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # daily-alpha-brief signals are treated as external research evidence only
    assert "evidence only" in reason
    assert "real_data_qa stays" in reason


def test_human_controlled_real_data_qa_boundary_decision_now_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["human_controlled_real_data_qa_boundary_decision"]
    assert row["state"] == STATE_BLOCKED
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # the external-evidence sub-chain now precedes this boundary, which stays
    # blocked; real_data_qa stays blocked
    assert "boundary" in reason
    assert "real_data_qa stays" in reason


def test_latest_completed_protocol_contract_is_block_97():
    assert LATEST_COMPLETED_PROTOCOL_CONTRACT == (
        "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_protocol_contract"] == (
        LATEST_COMPLETED_PROTOCOL_CONTRACT
    )
    # the recognized protocol contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_protocol_is_strategy_candidate_v1():
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_protocol"] == LATEST_COMPLETED_PROTOCOL
    # the recognized protocol unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_family_selection_contract_is_block_99():
    assert LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT == (
        "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_family_selection_contract"] == (
        LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT
    )
    # the recognized family-selection contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_family_review_contract_is_block_101():
    assert LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT == (
        "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_family_review_contract"] == (
        LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT
    )
    # the recognized family-review contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_plan_contract_is_block_103():
    assert LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT == (
        "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_plan_contract"] == (
        LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT
    )
    # the recognized research-plan contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_plan_review_contract_is_block_105():
    assert LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT == (
        "Block 105 - Crypto-D1 Strategy Candidate Research Plan Review Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_plan_review_contract"] == (
        LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT
    )
    # the recognized research-plan-review contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_plan_approval_contract_is_block_107():
    assert LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT == (
        "Block 107 - Crypto-D1 Strategy Candidate Research Plan Approval "
        "Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_plan_approval_contract"] == (
        LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT
    )
    # the recognized research-plan-approval contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_design_contract_is_block_109():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT == (
        "Block 109 - Crypto-D1 Strategy Candidate Research Design Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_design_contract"] == (
        LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT
    )
    # the recognized research-design contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_design_review_contract_is_block_111():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT == (
        "Block 111 - Crypto-D1 Strategy Candidate Research Design Review "
        "Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_design_review_contract"] == (
        LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT
    )
    # the recognized research-design-review contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_design_approval_contract_is_block_113():
    assert LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT == (
        "Block 113 - Crypto-D1 Strategy Candidate Research Design Approval "
        "Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_design_approval_contract"] == (
        LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT
    )
    # the recognized research-design-approval contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_research_readiness_contract_is_block_115():
    assert LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT == (
        "Block 115 - Crypto-D1 Strategy Candidate Research Readiness Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_research_readiness_contract"] == (
        LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT
    )
    # the recognized research-readiness contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_external_bot_evidence_intake_contract_is_block_117():
    assert LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT == (
        "Block 117 - Crypto-D1 External Bot Evidence Intake Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_external_bot_evidence_intake_contract"] == (
        LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT
    )
    # the recognized external-bot-evidence-intake contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_hyperliquid_whale_evidence_contract_is_block_119():
    assert LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT == (
        "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_hyperliquid_whale_evidence_contract"] == (
        LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT
    )
    # the recognized hyperliquid-whale-evidence contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_funding_rate_evidence_contract_is_block_121():
    assert LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT == (
        "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_funding_rate_evidence_contract"] == (
        LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT
    )
    # the recognized funding-rate-evidence contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_current_stage_is_funding_rate_evidence_complete():
    assert CURRENT_STAGE == "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
    assert "DAILY_ALPHA_BRIEF" in CURRENT_STAGE
    assert "CONTRACT_REQUIRED" in CURRENT_STAGE
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION", "QA",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "AUTOMATION", "ORDER"):
        assert banned not in CURRENT_STAGE, banned
    assert get_mission_flow_status()["current_stage"] == CURRENT_STAGE
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["operator_review_before_real_strategy_intake"]["state"] == STATE_CURRENT


def test_backbone_and_fake_lane_complete():
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["backbone_build"]["state"] == STATE_COMPLETE
    assert human["fake_lane"]["state"] == STATE_COMPLETE
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["fake_lane_closure"]["state"] == STATE_COMPLETE
    assert pipe["crypto_d1_intake_reconciliation"]["state"] == STATE_COMPLETE


# --- 4: downstream gates blocked / locked ----------------------------------

def test_real_data_qa_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["real_data_qa"]["state"] == STATE_BLOCKED


def test_baseline_backtest_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["baseline_backtest"]["state"] == STATE_BLOCKED


def test_paper_trading_gate_locked():
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["paper_trading_gate"]["state"] == STATE_LOCKED
    assert "human approval" in gates["paper_trading_gate"]["reason"].lower()


def test_micro_live_gate_locked_never_automated():
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["micro_live_gate"]["state"] == STATE_LOCKED
    assert "never automated" in gates["micro_live_gate"]["reason"].lower()


def test_real_strategy_intake_blocked():
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["real_strategy_intake"]["state"] == STATE_BLOCKED


# --- 5: no stage unlocks anything real -------------------------------------

def test_no_stage_state_is_an_execution_signal():
    allowed_states = {
        STATE_PASSED, STATE_COMPLETE, STATE_CURRENT,
        STATE_NEXT, STATE_BLOCKED, STATE_LOCKED,
    }
    s = get_mission_flow_status()
    for lane in (s["human_workflow"], s["machine_pipeline"], s["blocked_gates"]):
        for row in lane:
            assert row["state"] in allowed_states, row["state"]


def test_no_real_capability_marked_unlocked():
    # Every real-world capability flag must stay False regardless of how the
    # snapshot is read; reaching any mapped stage unlocks nothing real.
    assert all(v is False for v in safety_flags().values())
    assert get_mission_flow_status()["executes"] is False


# --- 6: determinism + mutation isolation -----------------------------------

def test_repeated_calls_are_identical():
    assert get_mission_flow_status() == get_mission_flow_status()
    assert human_workflow_lane() == human_workflow_lane()
    assert machine_pipeline_lane() == machine_pipeline_lane()
    assert blocked_gates() == blocked_gates()
    assert safety_flags() == safety_flags()


def test_returned_structures_are_mutation_isolated():
    a = get_mission_flow_status()
    a["mode"] = "TAMPERED"
    a["human_workflow"][0]["state"] = "TAMPERED"
    a["safety"]["live"] = True
    b = get_mission_flow_status()
    assert b["mode"] == "RESEARCH_ONLY"
    assert b["human_workflow"][0]["state"] != "TAMPERED"
    assert b["safety"]["live"] is False
    # module-level posture constant is also protected
    safety_flags()["broker"] = True
    assert safety_flags()["broker"] is False


# --- 7: pure stdlib import-root audit --------------------------------------

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


# --- 8: forbidden-surface audit (no IO / network / exec / control) ---------

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
    assert '"sparta_commander/strategy_factory_mission_flow_status.py"' in src
    assert '"tests/test_strategy_factory_mission_flow_status.py"' in src
