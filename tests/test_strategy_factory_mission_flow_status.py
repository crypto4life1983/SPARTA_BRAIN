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
    LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT,
    CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT,
    CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT,
    CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT,
    CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT,
    CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT,
    CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT,
    CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION,
    LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER,
    CRYPTO_D1_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_SCHEMA_VERSION,
    LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET,
    CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_SCHEMA_VERSION,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION,
    CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_SCHEMA_VERSION,
    LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW,
    LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION,
    LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC,
    LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET,
    LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT,
    LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION,
    LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION,
    LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT,
    LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT,
    LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT,
    LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT,
    LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT,
    LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT,
    LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT,
    LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT,
    LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT,
    LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT,
    LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT,
    LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT,
    LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT,
    LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT,
    LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT,
    LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT,
    LATEST_COMPLETED_AUTOMATION_ROADMAP,
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
        "latest_completed_bitcoin_cycle_timing_evidence_contract",
        "latest_completed_daily_alpha_brief_research_contract",
        "latest_completed_daily_alpha_brief_review_contract",
        "latest_completed_daily_alpha_brief_approval_contract",
        "latest_completed_strategy_evidence_scoring_contract",
        "latest_completed_strategy_candidate_ranking_contract",
        "latest_completed_external_human_trader_evidence_contract",
        "latest_completed_cohort_independence_contract",
        "latest_completed_real_data_qa_boundary_decision_contract",
        "latest_completed_real_data_qa_human_approval_packet_contract",
        "latest_completed_real_data_qa_readiness_checklist_contract",
        "latest_completed_overnight_research_autopilot_controller",
        "latest_completed_real_data_qa_human_approval_packet",
        "latest_completed_real_data_qa_boundary_decision",
        "latest_completed_pipeline_coverage_reconciliation",
        "latest_completed_real_data_qa_boundary_readiness_review",
        "latest_completed_public_spot_source_evaluation",
        "latest_completed_concrete_spot_provider_adapter_spec",
        "latest_completed_selected_spot_provider_fetch_runner_dry_run",
        "latest_completed_real_data_qa_boundary_decision_packet",
        "latest_completed_real_data_qa_plan_only_contract",
        "latest_completed_real_data_qa_plan_approval_decision",
        "latest_completed_real_data_qa_boundary_final_decision",
        "latest_completed_real_data_qa_pass_receipt",
        "latest_completed_baseline_backtest_prep_contract",
        "latest_completed_resume_policy_research_plan_contract",
        "latest_completed_resume_policy_simulation_runner_contract",
        "latest_completed_resume_policy_results_review_contract",
        "latest_completed_resume_policy_human_review_decision_contract",
        "latest_completed_post_resume_policy_research_continuation_plan_contract",
        "latest_completed_rc1_out_of_sample_robustness_research_contract",
        "latest_completed_rc1_out_of_sample_replay_runner_contract",
        "latest_completed_rc1_out_of_sample_results_review_contract",
        "latest_completed_rc1_oos_human_evidence_decision_contract",
        "latest_completed_rc2_cross_policy_stability_research_contract",
        "latest_completed_rc2_cross_policy_replay_runner_contract",
        "latest_completed_rc2_cross_policy_results_review_contract",
        "latest_completed_rc2_cross_policy_human_evidence_decision_contract",
        "latest_completed_rc3_failure_mode_characterization_research_contract",
        "latest_completed_rc3_findings_human_decision_contract",
        "latest_completed_fresh_evidence_validation_design_contract",
        "latest_completed_automation_roadmap",
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


def test_resume_policy_chain_recognized_as_latest_completed_evidence():
    # The research-only Resume-Policy chain (Blocks 175-177) is surfaced as
    # additive latest-completed evidence -- three separate fields for traceability.
    # Recognizing it unlocks nothing: gates stay BLOCKED/LOCKED.
    assert LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT == (
        "Block 175 - Crypto-D1 V2 Resume-Policy Research & Simulation Plan Contract"
    )
    assert LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT == (
        "Block 176 - Crypto-D1 V2 Resume-Policy Simulation Runner Contract"
    )
    assert LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT == (
        "Block 177 - Crypto-D1 V2 Resume-Policy Results Review / Decision Contract"
    )
    assert LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT == (
        "Block 178 - Crypto-D1 V2 Resume-Policy Human Review Decision Contract"
    )
    assert LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT == (
        "Block 179 - Crypto-D1 V2 Post Resume-Policy Research Continuation Plan Contract"
    )
    assert LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT == (
        "Block 180 - Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Contract"
    )
    assert LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT == (
        "Block 181 - Crypto-D1 V2 RC1 Out-of-Sample Replay Runner Contract"
    )
    assert LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT == (
        "Block 182 - Crypto-D1 V2 RC1 Out-of-Sample Results Review Contract"
    )
    assert LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT == (
        "Block 183 - Crypto-D1 V2 RC1 Out-of-Sample Human Evidence Decision Contract"
    )
    assert LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT == (
        "Block 184 - Crypto-D1 V2 RC2 Cross-Policy Stability Research Contract"
    )
    assert LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT == (
        "Block 185 - Crypto-D1 V2 RC2 Cross-Policy Replay Runner Contract"
    )
    assert LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT == (
        "Block 186 - Crypto-D1 V2 RC2 Cross-Policy Results Review Contract"
    )
    assert LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT == (
        "Block 187 - Crypto-D1 V2 RC2 Cross-Policy Human Evidence Decision Contract"
    )
    assert LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT == (
        "Block 188 - Crypto-D1 V2 RC3 Failure-Mode Characterization Research Contract"
    )
    assert LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT == (
        "Block 189 - Crypto-D1 V2 RC3 Findings Human Decision Contract"
    )
    assert LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT == (
        "Block 190 - Crypto-D1 V2 Fresh-Evidence Validation Design Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_resume_policy_research_plan_contract"] == (
        LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT
    )
    assert s["latest_completed_resume_policy_simulation_runner_contract"] == (
        LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT
    )
    assert s["latest_completed_resume_policy_results_review_contract"] == (
        LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT
    )
    assert s["latest_completed_resume_policy_human_review_decision_contract"] == (
        LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT
    )
    assert s["latest_completed_post_resume_policy_research_continuation_plan_contract"] == (
        LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT
    )
    assert s["latest_completed_rc1_out_of_sample_robustness_research_contract"] == (
        LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT
    )
    assert s["latest_completed_rc1_out_of_sample_replay_runner_contract"] == (
        LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT
    )
    assert s["latest_completed_rc1_out_of_sample_results_review_contract"] == (
        LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT
    )
    assert s["latest_completed_rc1_oos_human_evidence_decision_contract"] == (
        LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT
    )
    assert s["latest_completed_rc2_cross_policy_stability_research_contract"] == (
        LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT
    )
    assert s["latest_completed_rc2_cross_policy_replay_runner_contract"] == (
        LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT
    )
    assert s["latest_completed_rc2_cross_policy_results_review_contract"] == (
        LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT
    )
    assert s["latest_completed_rc2_cross_policy_human_evidence_decision_contract"] == (
        LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT
    )
    assert s["latest_completed_rc3_failure_mode_characterization_research_contract"] == (
        LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT
    )
    assert s["latest_completed_rc3_findings_human_decision_contract"] == (
        LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT
    )
    assert s["latest_completed_fresh_evidence_validation_design_contract"] == (
        LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT
    )
    # recognizing the chain unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


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


def test_next_required_action_is_human_controlled_real_data_qa_boundary_decision():
    # After the research-only Resume-Policy chain (Blocks 175-177) is recognized
    # complete, the only next step is the human review of the resume-policy
    # simulation results -- a human judgment, NOT a BUILD step and NOT an
    # authorization. No stale "BUILD_..._APPROVAL_CONTRACT" literal remains.
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert not NEXT_REQUIRED_ACTION.startswith("BUILD_")
    # an idle wait state for future evidence, not an execution / authorization
    assert "COMPLETED" in NEXT_REQUIRED_ACTION
    assert "ROADMAP" in NEXT_REQUIRED_ACTION
    assert NEXT_REQUIRED_ACTION != (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert NEXT_REQUIRED_ACTION != (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    # A boundary decision authorizes nothing real. "QA" is intentionally allowed:
    # it names the still-blocked real_data_qa gate, not an action that runs QA.
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "ORDER", "TRACK"):
        assert banned not in NEXT_REQUIRED_ACTION, banned
    s = get_mission_flow_status()
    assert s["next_required_action"] == NEXT_REQUIRED_ACTION
    # the boundary decision still unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the resume-policy results review and human review record are now complete
    assert pipe["crypto_d1_resume_policy_results_review"]["state"] == STATE_COMPLETE
    assert (
        pipe["crypto_d1_resume_policy_human_review_recorded"]["state"] == STATE_COMPLETE
    )
    # the research-continuation direction selection is now complete
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete
    assert (
        pipe["crypto_d1_rc1_out_of_sample_replay_approval"]["state"] == STATE_COMPLETE
    )
    # the RC1 out-of-sample evidence decision is now complete
    assert (
        pipe["crypto_d1_rc1_out_of_sample_evidence_decision"]["state"] == STATE_COMPLETE
    )
    # the RC2 cross-policy stability research approval is now complete
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background (COMPLETE)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    # the roadmap human review is the active STATE_NEXT step
    nxt = pipe["strategy_factory_roadmap_human_review"]
    assert nxt["state"] == STATE_NEXT
    assert NEXT_REQUIRED_ACTION in nxt["reason"]
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED


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


def test_bitcoin_cycle_timing_evidence_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_bitcoin_cycle_timing_evidence_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 123" in row["reason"]
    assert CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # core rule: cycle timing is attention-only evidence, never a buy instruction
    assert "pay attention, not when to buy" in reason
    assert "independent confirmation" in reason
    assert "never converts timing evidence into permission" in reason


def test_daily_alpha_brief_research_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_daily_alpha_brief_research_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 125" in row["reason"]
    assert CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # the brief is what-to-watch evidence, never a trade; highest stance is WATCH
    assert "what to watch and research, never what to trade" in reason
    assert "watch / research_only" in reason


def test_daily_alpha_brief_review_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_daily_alpha_brief_review_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 127" in row["reason"]
    assert CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # the review escalates for approval, never a trade; highest verdict is READY
    assert "never what to trade" in reason


def test_daily_alpha_brief_approval_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_daily_alpha_brief_approval_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 129" in row["reason"]
    assert CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # an approval only files the reviewed brief as a research record, never trade
    assert "never what to trade" in reason


def test_strategy_evidence_scoring_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_strategy_evidence_scoring_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 131" in row["reason"]
    assert CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # a research-only evidence/scoring support contract; it scores, never trades
    assert "never what to trade" in reason
    # recognizing it is purely additive -- it does not advance the boundary stage
    assert "purely additive latest-completed metadata" in reason


def test_cohort_independence_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_cohort_independence_correlation_penalty_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 132" in row["reason"]
    assert CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # a research-only evidence/scoring support contract; it scores, never trades
    assert "never what to trade" in reason
    # recognizing it is purely additive -- it does not advance the boundary stage
    assert "purely additive latest-completed metadata" in reason


def test_real_data_qa_boundary_decision_contract_now_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_real_data_qa_boundary_decision_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Block 134" in row["reason"]
    assert CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION in (
        row["reason"]
    )
    reason = row["reason"].lower()
    assert "executes nothing" in reason
    # the contract readies a human decision; it never trades and never unlocks
    assert "never what to trade and never an unlock" in reason
    # recognizing it is purely additive -- it does not advance the boundary stage
    assert "purely additive latest-completed metadata" in reason
    # the resume-policy results review is now complete; the human-reviewed
    # research continuation is the STATE_NEXT human step; the QA boundary
    # decision remains its own separate BLOCKED step
    assert pipe["crypto_d1_resume_policy_results_review"]["state"] == STATE_COMPLETE
    assert (
        pipe["crypto_d1_resume_policy_human_review_recorded"]["state"] == STATE_COMPLETE
    )
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    nxt = pipe["human_controlled_real_data_qa_boundary_decision"]
    assert nxt["state"] == STATE_BLOCKED
    # recognizing the contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())


def test_roadmap_human_review_is_next_and_qa_boundary_is_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the full RC1, RC2, and RC3 characterization chains are now complete
    assert (
        pipe["crypto_d1_resume_policy_results_review"]["state"] == STATE_COMPLETE
    )
    assert (
        pipe["crypto_d1_resume_policy_human_review_recorded"]["state"] == STATE_COMPLETE
    )
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    assert (
        pipe["crypto_d1_rc1_out_of_sample_replay_approval"]["state"] == STATE_COMPLETE
    )
    assert (
        pipe["crypto_d1_rc1_out_of_sample_evidence_decision"]["state"] == STATE_COMPLETE
    )
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    assert (
        pipe["crypto_d1_rc2_cross_policy_replay_approval"]["state"] == STATE_COMPLETE
    )
    assert (
        pipe["crypto_d1_rc2_cross_policy_evidence_decision"]["state"] == STATE_COMPLETE
    )
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    assert (
        pipe["crypto_d1_rc3_findings_decision"]["state"] == STATE_COMPLETE
    )
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background (COMPLETE)
    bg = pipe["crypto_d1_await_fresh_evidence_accrual"]
    assert bg["state"] == STATE_COMPLETE
    bg_reason = bg["reason"].lower()
    # the frozen wait terms are preserved on the completed row
    assert "continues in the background" in bg_reason
    assert "post-2026-06-08" in bg_reason
    assert "manually staged" in bg_reason
    assert "180 days" in bg_reason
    assert "365" in bg_reason
    assert "return > 0" in bg_reason
    assert "-35%" in bg_reason
    assert "sharpe >= 0.8" in bg_reason
    assert "top-half stability" in bg_reason
    assert "promotes nothing" in bg_reason
    assert "do_not_promote_resume_policy_yet" in bg_reason
    # the roadmap human review is the active next step
    nxt = pipe["strategy_factory_roadmap_human_review"]
    assert nxt["state"] == STATE_NEXT
    assert NEXT_REQUIRED_ACTION in nxt["reason"]
    nxt_reason = nxt["reason"].lower()
    # it is NOT a build step and NOT an authorization, and unlocks nothing
    assert "not a build step" in nxt_reason
    assert "not an authorization" in nxt_reason
    assert "unlocks nothing" in nxt_reason
    # all six roadmap links are surfaced as complete read-only designs
    assert "links l1-l6 are complete" in nxt_reason
    assert "intake-to-orchestrator adapter" in nxt_reason
    assert "unsigned lane-aware" in nxt_reason
    assert "one human signature" in nxt_reason
    assert "no scheduler built" in nxt_reason
    assert "nothing sent" in nxt_reason
    assert "no runtime ui edit" in nxt_reason
    # the control chain is complete but trading remains locked
    assert "paperwork/control chain is complete" in nxt_reason
    assert "trading remains locked" in nxt_reason
    # the four future blocks each need their own separate human approval
    assert "own separate human approval" in nxt_reason
    assert "dashboard/jarvis wiring" in nxt_reason
    assert "manual-start notification transport" in nxt_reason
    assert "scheduler build under the l4 rules" in nxt_reason
    assert "umbrella strategy research orchestrator" in nxt_reason
    # the crypto-d1 fresh-evidence wait continues in the background
    assert "continues in the background under the frozen block 190 bars" in nxt_reason
    # never promotion or execution
    assert "not promotion" in nxt_reason
    assert "not trading execution" in nxt_reason
    # the DO_NOT_PROMOTE decision is preserved, never overturned by the roadmap
    assert "do_not_promote_resume_policy_yet" in nxt_reason
    # the QA boundary decision is now a separate, later, BLOCKED step
    row = pipe["human_controlled_real_data_qa_boundary_decision"]
    assert row["state"] == STATE_BLOCKED
    reason = row["reason"].lower()
    # its safety body is preserved verbatim
    assert "not a build step" in reason
    assert "not an authorization" in reason
    assert "boundary" in reason
    # downstream real_data_qa gate stays blocked
    assert "real_data_qa stays" in reason


def test_latest_completed_automation_roadmap_is_links_l1_l6():
    assert LATEST_COMPLETED_AUTOMATION_ROADMAP == (
        "Links L1-L6 - Strategy Factory Automation Roadmap Complete "
        "(Design Only)"
    )
    # design-only label: never a promotion and never an unlock
    assert "Design Only" in LATEST_COMPLETED_AUTOMATION_ROADMAP
    for banned in ("PROMOTE", "UNLOCK"):
        assert banned not in LATEST_COMPLETED_AUTOMATION_ROADMAP.upper(), banned
    s = get_mission_flow_status()
    assert s["latest_completed_automation_roadmap"] == (
        LATEST_COMPLETED_AUTOMATION_ROADMAP
    )
    # recognizing the completed roadmap unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the roadmap human review is the active next step; gates stay shut
    assert pipe["strategy_factory_roadmap_human_review"]["state"] == STATE_NEXT
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


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


def test_latest_completed_bitcoin_cycle_timing_evidence_contract_is_block_123():
    assert LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT == (
        "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_bitcoin_cycle_timing_evidence_contract"] == (
        LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT
    )
    # the recognized bitcoin-cycle-timing-evidence contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # after Block 130, the global stage has advanced past the daily alpha brief
    # approval build to the human-controlled real-data QA boundary decision.
    assert s["current_stage"] == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert s["next_required_action"] == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )


def test_latest_completed_daily_alpha_brief_research_contract_is_block_125():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_daily_alpha_brief_research_contract"] == (
        LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT
    )
    # the recognized daily-alpha-brief-research contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False


def test_latest_completed_daily_alpha_brief_review_contract_is_block_127():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT == (
        "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_daily_alpha_brief_review_contract"] == (
        LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT
    )
    # the recognized daily-alpha-brief-review contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # the Block 125 research contract completion is preserved alongside it
    assert s["latest_completed_daily_alpha_brief_research_contract"] == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )


def test_latest_completed_daily_alpha_brief_approval_contract_is_block_129():
    assert LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT == (
        "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_daily_alpha_brief_approval_contract"] == (
        LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT
    )
    # the recognized daily-alpha-brief-approval contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # the Block 127 review contract completion is preserved alongside it
    assert s["latest_completed_daily_alpha_brief_review_contract"] == (
        "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
    )


def test_latest_completed_strategy_evidence_scoring_contract_is_block_131():
    assert LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT == (
        "Block 131 - Crypto-D1 Strategy Evidence Scoring Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_strategy_evidence_scoring_contract"] == (
        LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT
    )
    # the recognized evidence-scoring contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # registering Block 131 does not advance the boundary stage or next action
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the Block 132 cohort contract completion is preserved alongside it
    assert s["latest_completed_cohort_independence_contract"] == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )


def test_latest_completed_cohort_independence_contract_is_block_132():
    assert LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_cohort_independence_contract"] == (
        LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT
    )
    # the recognized cohort-independence contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # registering Block 132 does not advance the boundary stage or next action
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the Block 129 approval contract completion is preserved alongside it
    assert s["latest_completed_daily_alpha_brief_approval_contract"] == (
        "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
    )


def test_latest_completed_real_data_qa_boundary_decision_contract_is_block_134():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT == (
        "Block 134 - Crypto-D1 Real Data QA Boundary Decision Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_boundary_decision_contract"] == (
        LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT
    )
    # the recognized boundary-decision contract unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    # registering Block 134 does not advance the boundary stage or next action
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the Block 132 cohort contract completion is preserved alongside it
    assert s["latest_completed_cohort_independence_contract"] == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )


def test_latest_completed_real_data_qa_human_approval_packet_contract_is_block_136():
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT == (
        "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_human_approval_packet_contract"] == (
        LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe[
        "crypto_d1_real_data_qa_human_approval_packet_contract"
    ]["state"] == STATE_COMPLETE
    # recognizing Phase A unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the Block 134 boundary-decision contract completion is preserved alongside it
    assert s["latest_completed_real_data_qa_boundary_decision_contract"] == (
        "Block 134 - Crypto-D1 Real Data QA Boundary Decision Contract"
    )


def test_latest_completed_real_data_qa_readiness_checklist_contract_is_block_136():
    assert LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT == (
        "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_readiness_checklist_contract"] == (
        LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe[
        "crypto_d1_real_data_qa_readiness_checklist_contract"
    ]["state"] == STATE_COMPLETE
    # recognizing Phase B unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the Phase A approval-packet contract completion is preserved alongside it
    assert s["latest_completed_real_data_qa_human_approval_packet_contract"] == (
        "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
    )


def test_latest_completed_overnight_research_autopilot_controller_is_block_152():
    assert LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_overnight_research_autopilot_controller"] == (
        LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe[
        "crypto_d1_overnight_research_autopilot_controller"
    ]["state"] == STATE_COMPLETE
    # recognizing Block 152 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # the Block 136 readiness checklist completion is preserved alongside it
    assert s["latest_completed_real_data_qa_readiness_checklist_contract"] == (
        "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
    )


def test_latest_completed_real_data_qa_human_approval_packet_is_block_155():
    assert LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_human_approval_packet"] == (
        LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe[
        "crypto_d1_real_data_qa_human_approval_packet"
    ]["state"] == STATE_COMPLETE
    assert CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_SCHEMA_VERSION in (
        pipe["crypto_d1_real_data_qa_human_approval_packet"]["reason"]
    )
    # recognizing Block 155 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # the Block 152 controller completion is preserved alongside it
    assert s["latest_completed_overnight_research_autopilot_controller"] == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )


def test_latest_completed_real_data_qa_boundary_decision_is_block_158():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION == (
        "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_boundary_decision"] == (
        LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 158 decision-layer module is recognized as COMPLETE
    assert pipe[
        "crypto_d1_human_controlled_real_data_qa_boundary_decision_layer"
    ]["state"] == STATE_COMPLETE
    assert CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_SCHEMA_VERSION in (
        pipe[
            "crypto_d1_human_controlled_real_data_qa_boundary_decision_layer"
        ]["reason"]
    )
    # recognizing Block 158 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 152 controller and Block 155 packet completions are preserved
    assert s["latest_completed_overnight_research_autopilot_controller"] == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert s["latest_completed_real_data_qa_human_approval_packet"] == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_pipeline_coverage_reconciliation_is_block_161():
    assert LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION == (
        "Block 161 - Crypto-D1 Pipeline Coverage Reconciliation"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_pipeline_coverage_reconciliation"] == (
        LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 161 coverage-reconciliation layer is recognized as COMPLETE
    node = pipe["crypto_d1_pipeline_coverage_reconciliation_layer"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "coverage metadata" in reason
    assert "parked" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 161 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the coverage layer is NOT registered as an active step ahead of the
    # boundary -- the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 152/155/158 completions are preserved
    assert s["latest_completed_overnight_research_autopilot_controller"] == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert s["latest_completed_real_data_qa_human_approval_packet"] == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval "
        "Packet"
    )
    assert s["latest_completed_real_data_qa_boundary_decision"] == (
        "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_real_data_qa_boundary_readiness_review_is_block_166():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_boundary_readiness_review"] == (
        LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 166 boundary-readiness review is recognized as COMPLETE
    node = pipe["crypto_d1_real_data_qa_boundary_readiness_review"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "readiness review" in reason
    assert "ready_for_human_boundary_decision" in reason
    assert "hold_needs_more_prep" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 166 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the review is NOT registered as an active step ahead of the boundary --
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 161 completion is preserved
    assert s["latest_completed_pipeline_coverage_reconciliation"] == (
        "Block 161 - Crypto-D1 Pipeline Coverage Reconciliation"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_real_data_qa_boundary_decision_packet_is_block_170():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET == (
        "Block 170 - Crypto-D1 Real Data QA Boundary Decision Packet"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_boundary_decision_packet"] == (
        LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 170 boundary decision packet is recognized as COMPLETE
    node = pipe["crypto_d1_real_data_qa_boundary_decision_packet"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "boundary decision packet" in reason
    assert "recommendations only" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 170 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 166 completion is preserved
    assert s["latest_completed_real_data_qa_boundary_readiness_review"] == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_real_data_qa_plan_only_contract_is_block_171():
    assert LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT == (
        "Block 171 - Crypto-D1 Real Data QA Plan-Only Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_plan_only_contract"] == (
        LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 171 plan-only contract is recognized as COMPLETE
    node = pipe["crypto_d1_real_data_qa_plan_only_contract"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "plan-only contract" in reason
    assert "text and scope only" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 171 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 170 completion is preserved alongside Block 171
    assert s["latest_completed_real_data_qa_boundary_decision_packet"] == (
        "Block 170 - Crypto-D1 Real Data QA Boundary Decision Packet"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_real_data_qa_plan_approval_decision_is_block_172():
    assert LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION == (
        "Block 172 - Crypto-D1 Real Data QA Plan Approval Decision Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_plan_approval_decision"] == (
        LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 172 plan approval decision is recognized as COMPLETE
    node = pipe["crypto_d1_real_data_qa_plan_approval_decision"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "plan approval decision" in reason
    assert "approve_plan_only" in reason
    assert "request_plan_revision" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 172 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the approval decision is NOT registered as an active step ahead of the
    # boundary -- the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 166 completion is preserved
    assert s["latest_completed_real_data_qa_boundary_readiness_review"] == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_real_data_qa_boundary_final_decision_is_block_174():
    assert LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION == (
        "Block 174 - Crypto-D1 Real Data QA Boundary Final Decision Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_real_data_qa_boundary_final_decision"] == (
        LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 174 boundary final decision is recognized as COMPLETE
    node = pipe["crypto_d1_real_data_qa_boundary_final_decision"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "boundary final decision" in reason
    assert "authorize_next_read_only_real_data_qa_prep_contract" in reason
    assert "request_more_research" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 174 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the final decision is NOT registered as an active step ahead of the
    # boundary -- the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 172 completion is preserved
    assert s["latest_completed_real_data_qa_plan_approval_decision"] == (
        "Block 172 - Crypto-D1 Real Data QA Plan Approval Decision Contract"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_public_spot_source_evaluation_is_block_167():
    assert LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION == (
        "Block 167 - Crypto-D1 Public Read-Only Spot Source Evaluation Contract"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_public_spot_source_evaluation"] == (
        LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 167 source evaluation is recognized as COMPLETE
    node = pipe["crypto_d1_public_spot_source_evaluation"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "source evaluation" in reason
    assert "ready_for_human_source_review" in reason
    assert "hold_needs_more_prep" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 167 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the source evaluation is NOT registered as an active step ahead of the
    # boundary -- the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 166 completion is preserved
    assert s["latest_completed_real_data_qa_boundary_readiness_review"] == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_concrete_spot_provider_adapter_spec_is_block_168():
    assert LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC == (
        "Block 168 - Crypto-D1 Concrete Read-Only Spot Provider Adapter Spec"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_concrete_spot_provider_adapter_spec"] == (
        LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 168 adapter spec is recognized as COMPLETE
    node = pipe["crypto_d1_concrete_spot_provider_adapter_spec"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "adapter spec" in reason
    assert "ready_for_human_spec_review" in reason
    assert "hold_needs_more_prep" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 168 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the adapter spec is NOT registered as an active step ahead of the boundary --
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 167 completion is preserved
    assert s["latest_completed_public_spot_source_evaluation"] == (
        "Block 167 - Crypto-D1 Public Read-Only Spot Source Evaluation Contract"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_latest_completed_selected_spot_provider_fetch_runner_dry_run_is_block_169():
    assert LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN == (
        "Block 169 - Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry "
        "Run"
    )
    s = get_mission_flow_status()
    assert s["latest_completed_selected_spot_provider_fetch_runner_dry_run"] == (
        LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN
    )
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    # the Block 169 dry run is recognized as COMPLETE
    node = pipe["crypto_d1_selected_spot_provider_fetch_runner_dry_run"]
    assert node["state"] == STATE_COMPLETE
    reason = node["reason"].lower()
    assert "dry run" in reason
    assert "ready_for_human_dry_run_review" in reason
    assert "hold_needs_more_prep" in reason
    assert "never an unlock of real_data_qa" in reason
    # recognizing Block 169 unlocks nothing real and does not advance the boundary
    assert all(v is False for v in safety_flags().values())
    assert s["executes"] is False
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert NEXT_REQUIRED_ACTION == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    # the dry run is NOT registered as an active step ahead of the boundary --
    # the resume-policy results review is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_results_review"
    ]["state"] == STATE_COMPLETE
    # the human review record is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_resume_policy_human_review_recorded"
    ]["state"] == STATE_COMPLETE
    # the research-continuation direction selection is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_post_resume_policy_research_continuation_direction_selection"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC1 out-of-sample evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc1_out_of_sample_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy stability research approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_stability_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy replay approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_replay_approval"
    ]["state"] == STATE_COMPLETE
    # the RC2 cross-policy evidence decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc2_cross_policy_evidence_decision"
    ]["state"] == STATE_COMPLETE
    # the RC3 failure-mode characterization approval is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_failure_mode_characterization_research_approval"
    ]["state"] == STATE_COMPLETE
    # the RC3 findings decision is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_rc3_findings_decision"
    ]["state"] == STATE_COMPLETE
    # awaiting a new human research directive is now complete (STATE_COMPLETE)
    assert pipe[
        "crypto_d1_await_new_human_research_directive"
    ]["state"] == STATE_COMPLETE
    # awaiting fresh evidence accrual continues in the background
    # (STATE_COMPLETE); the roadmap human review is the active step (STATE_NEXT)
    assert pipe[
        "crypto_d1_await_fresh_evidence_accrual"
    ]["state"] == STATE_COMPLETE
    assert pipe[
        "strategy_factory_roadmap_human_review"
    ]["state"] == STATE_NEXT
    # the QA boundary decision remains its own separate BLOCKED step
    assert pipe[
        "human_controlled_real_data_qa_boundary_decision"
    ]["state"] == STATE_BLOCKED
    # Block 168 completion is preserved
    assert s["latest_completed_concrete_spot_provider_adapter_spec"] == (
        "Block 168 - Crypto-D1 Concrete Read-Only Spot Provider Adapter Spec"
    )
    # downstream gates stay blocked/locked
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    assert pipe["paper_trading_gate"]["state"] == STATE_LOCKED
    assert pipe["micro_live_gate"]["state"] == STATE_LOCKED


def test_current_stage_is_human_controlled_real_data_qa_boundary_decision():
    assert CURRENT_STAGE == (
        "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
    )
    assert "COMPLETED" in CURRENT_STAGE
    assert "ROADMAP" in CURRENT_STAGE
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_REQUIRED"
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_REQUIRED"
    assert CURRENT_STAGE != "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
    # A human review stage over research-only resume-policy results, not execution.
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
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
