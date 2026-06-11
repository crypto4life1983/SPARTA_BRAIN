"""SPARTA Offline Strategy Factory - MISSION FLOW STATUS ADAPTER.

A PURE, stdlib-only *read-only display/status adapter* for the JARVIS Strategy
Factory "Mission Flow" panel. It derives a deterministic, plain-data snapshot of
where the Strategy Factory backbone currently stands -- which human workflow
stages and machine pipeline stages are complete, which is current, what the
single next required action is, and which downstream gates remain blocked or
locked. It is a *map of state*, not a controller.

It executes NOTHING. It does not run the Strategy Factory, does not acquire,
fetch, inspect, load, validate, transform, or compute on any data, does not run
QA, does not run a baseline, does not backtest, does not simulate, does not
touch any broker / exchange / order / trading / paper / live / distribution /
autopilot surface, triggers no automation, promotes/deploys nothing, records no
approval decision, writes no file, reads no file, lists no directory, opens no
network, spawns no subprocess, reads no environment, mints no id, records no
timestamp, and dynamically imports nothing.

The snapshot is derived from the known, committed contract/checkpoint state of
the Strategy Factory backbone as of Bundle 54 (Crypto-D1 research-only dry-run
research archive or closure contract complete, which closes the research-only
dry-run lane) plus the recognized Crypto-D1 Strategy Candidate Protocol v1
(defined on paper in Block 95) and the recognized Crypto-D1 Strategy Candidate
Protocol Contract (built on paper in Block 97). It requires no IO to produce the
default status. Reaching any
stage in this map unlocks nothing real: every downstream real-world capability
(real data, QA, baseline, backtest, paper, live, broker, exchange, automation,
runtime/registry/dashboard writes) stays blocked and human-gated. Bundle 54
only means the research-only dry-run research archive or closure *contract*
exists on paper; it authorizes nothing and executes nothing: no dry-run
execution, data acquisition, data fetch, data inspection, QA, baseline,
backtest, paper/live, broker/exchange, or automation is unlocked.

Public API:
  - MISSION_FLOW_VERSION
  - MISSION_FLOW_MODE
  - MISSION_FLOW_SAFETY_POSTURE
  - STATE_PASSED / STATE_COMPLETE / STATE_CURRENT / STATE_NEXT
  - STATE_BLOCKED / STATE_LOCKED / STATE_PARKED
  - CURRENT_STAGE
  - LATEST_COMPLETED_BUNDLE
  - LATEST_COMPLETED_PROTOCOL
  - LATEST_COMPLETED_PROTOCOL_CONTRACT
  - LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT
  - LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT
  - LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT
  - LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT
  - NEXT_REQUIRED_ACTION
  - human_workflow_lane()
  - machine_pipeline_lane()
  - blocked_gates()
  - safety_flags()
  - get_mission_flow_status()
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    SOURCE_CLASS_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
    SPEC_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
    PLAN_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
    GATE_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract import (  # noqa: E501
    BOUNDARY_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract import (  # noqa: E501
    NEXT_STEP_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
    PREVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_review_contract import (  # noqa: E501
    REVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_contract import (  # noqa: E501
    DECISION_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_review_contract import (  # noqa: E501
    DECISION_REVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract import (  # noqa: E501
    FINAL_DECISION_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract import (  # noqa: E501
    ARCHIVE_OR_CLOSURE_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (  # noqa: E501
    PROTOCOL_SCHEMA_VERSION as NEXT_RESEARCH_PROTOCOL_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_protocol_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION as STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_selection_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION as STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_review_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_contract import (  # noqa: E501
    BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_review_contract import (  # noqa: E501
    RESEARCH_PLAN_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_contract import (  # noqa: E501
    RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_contract import (  # noqa: E501
    RESEARCH_DESIGN_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_review_contract import (  # noqa: E501
    RESEARCH_DESIGN_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_approval_contract import (  # noqa: E501
    RESEARCH_DESIGN_APPROVAL_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_readiness_contract import (  # noqa: E501
    RESEARCH_READINESS_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_external_bot_evidence_intake_contract import (  # noqa: E501
    EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION as STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract import (  # noqa: E501
    WHALE_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_funding_rate_evidence_contract import (  # noqa: E501
    FUNDING_RATE_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract import (  # noqa: E501
    BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_research_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_review_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_approval_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_evidence_scoring_contract import (  # noqa: E501
    STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION as CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_ranking_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION as CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_external_human_trader_evidence_contract import (  # noqa: E501
    EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract import (  # noqa: E501
    COHORT_INDEPENDENCE_SCHEMA_VERSION as CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract import (  # noqa: E501
    RDQ_BOUNDARY_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract import (  # noqa: E501
    RDQ_APPROVAL_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract import (  # noqa: E501
    RDQ_READINESS_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_overnight_research_autopilot_controller import (  # noqa: E501
    CONTROLLER_SCHEMA_VERSION as CRYPTO_D1_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet import (  # noqa: E501
    PACKET_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision import (  # noqa: E501
    DECISION_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_pass_receipt import (  # noqa: E501
    get_qa_pass_receipt_label as _qa_pass_receipt_label,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_prep_contract import (  # noqa: E501
    get_baseline_backtest_prep_label as _baseline_prep_label,
)
from sparta_commander.strategy_factory_mission_flow_bundle_registry import (  # noqa: E501
    get_current_stage as _registry_current_stage,
    get_latest_completed_bundle_label as _registry_latest_bundle_label,
    get_latest_completed_protocol_label as _registry_latest_protocol_label,
    get_latest_completed_protocol_contract_label as _registry_latest_protocol_contract_label,  # noqa: E501
    get_latest_completed_family_selection_contract_label as _registry_latest_family_selection_contract_label,  # noqa: E501
    get_latest_completed_family_review_contract_label as _registry_latest_family_review_contract_label,  # noqa: E501
    get_latest_completed_research_plan_contract_label as _registry_latest_research_plan_contract_label,  # noqa: E501
    get_latest_completed_research_plan_review_contract_label as _registry_latest_research_plan_review_contract_label,  # noqa: E501
    get_latest_completed_research_plan_approval_contract_label as _registry_latest_research_plan_approval_contract_label,  # noqa: E501
    get_latest_completed_research_design_contract_label as _registry_latest_research_design_contract_label,  # noqa: E501
    get_latest_completed_research_design_review_contract_label as _registry_latest_research_design_review_contract_label,  # noqa: E501
    get_latest_completed_research_design_approval_contract_label as _registry_latest_research_design_approval_contract_label,  # noqa: E501
    get_latest_completed_research_readiness_contract_label as _registry_latest_research_readiness_contract_label,  # noqa: E501
    get_latest_completed_external_bot_evidence_intake_contract_label as _registry_latest_external_bot_evidence_intake_contract_label,  # noqa: E501
    get_latest_completed_hyperliquid_whale_evidence_contract_label as _registry_latest_hyperliquid_whale_evidence_contract_label,  # noqa: E501
    get_latest_completed_funding_rate_evidence_contract_label as _registry_latest_funding_rate_evidence_contract_label,  # noqa: E501
    get_latest_completed_bitcoin_cycle_timing_evidence_contract_label as _registry_latest_bitcoin_cycle_timing_evidence_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_research_contract_label as _registry_latest_daily_alpha_brief_research_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_review_contract_label as _registry_latest_daily_alpha_brief_review_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_approval_contract_label as _registry_latest_daily_alpha_brief_approval_contract_label,  # noqa: E501
    get_latest_completed_strategy_evidence_scoring_contract_label as _registry_latest_strategy_evidence_scoring_contract_label,  # noqa: E501
    get_latest_completed_strategy_candidate_ranking_contract_label as _registry_latest_strategy_candidate_ranking_contract_label,  # noqa: E501
    get_latest_completed_external_human_trader_evidence_contract_label as _registry_latest_external_human_trader_evidence_contract_label,  # noqa: E501
    get_latest_completed_cohort_independence_contract_label as _registry_latest_cohort_independence_contract_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_decision_contract_label as _registry_latest_real_data_qa_boundary_decision_contract_label,  # noqa: E501
    get_latest_completed_real_data_qa_human_approval_packet_contract_label as _registry_latest_real_data_qa_human_approval_packet_contract_label,  # noqa: E501
    get_latest_completed_real_data_qa_readiness_checklist_contract_label as _registry_latest_real_data_qa_readiness_checklist_contract_label,  # noqa: E501
    get_latest_completed_overnight_research_autopilot_controller_label as _registry_latest_overnight_research_autopilot_controller_label,  # noqa: E501
    get_latest_completed_real_data_qa_human_approval_packet_label as _registry_latest_real_data_qa_human_approval_packet_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_decision_label as _registry_latest_real_data_qa_boundary_decision_label,  # noqa: E501
    get_latest_completed_pipeline_coverage_reconciliation_label as _registry_latest_pipeline_coverage_reconciliation_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_readiness_review_label as _registry_latest_real_data_qa_boundary_readiness_review_label,  # noqa: E501
    get_latest_completed_public_spot_source_evaluation_label as _registry_latest_public_spot_source_evaluation_label,  # noqa: E501
    get_latest_completed_concrete_spot_provider_adapter_spec_label as _registry_latest_concrete_spot_provider_adapter_spec_label,  # noqa: E501
    get_latest_completed_selected_spot_provider_fetch_runner_dry_run_label as _registry_latest_selected_spot_provider_fetch_runner_dry_run_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_decision_packet_label as _registry_latest_real_data_qa_boundary_decision_packet_label,  # noqa: E501
    get_latest_completed_real_data_qa_plan_only_contract_label as _registry_latest_real_data_qa_plan_only_contract_label,  # noqa: E501
    get_latest_completed_real_data_qa_plan_approval_decision_label as _registry_latest_real_data_qa_plan_approval_decision_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_final_decision_label as _registry_latest_real_data_qa_boundary_final_decision_label,  # noqa: E501
    get_latest_completed_resume_policy_research_plan_contract_label as _registry_latest_resume_policy_research_plan_contract_label,  # noqa: E501
    get_latest_completed_resume_policy_simulation_runner_contract_label as _registry_latest_resume_policy_simulation_runner_contract_label,  # noqa: E501
    get_latest_completed_resume_policy_results_review_contract_label as _registry_latest_resume_policy_results_review_contract_label,  # noqa: E501
    get_latest_completed_resume_policy_human_review_decision_contract_label as _registry_latest_resume_policy_human_review_decision_contract_label,  # noqa: E501
    get_latest_completed_post_resume_policy_research_continuation_plan_contract_label as _registry_latest_post_resume_policy_research_continuation_plan_contract_label,  # noqa: E501
    get_latest_completed_rc1_out_of_sample_robustness_research_contract_label as _registry_latest_rc1_out_of_sample_robustness_research_contract_label,  # noqa: E501
    get_latest_completed_rc1_out_of_sample_replay_runner_contract_label as _registry_latest_rc1_out_of_sample_replay_runner_contract_label,  # noqa: E501
    get_latest_completed_rc1_out_of_sample_results_review_contract_label as _registry_latest_rc1_out_of_sample_results_review_contract_label,  # noqa: E501
    get_latest_completed_rc1_oos_human_evidence_decision_contract_label as _registry_latest_rc1_oos_human_evidence_decision_contract_label,  # noqa: E501
    get_latest_completed_rc2_cross_policy_stability_research_contract_label as _registry_latest_rc2_cross_policy_stability_research_contract_label,  # noqa: E501
    get_latest_completed_rc2_cross_policy_replay_runner_contract_label as _registry_latest_rc2_cross_policy_replay_runner_contract_label,  # noqa: E501
    get_latest_completed_rc2_cross_policy_results_review_contract_label as _registry_latest_rc2_cross_policy_results_review_contract_label,  # noqa: E501
    get_latest_completed_rc2_cross_policy_human_evidence_decision_contract_label as _registry_latest_rc2_cross_policy_human_evidence_decision_contract_label,  # noqa: E501
    get_latest_completed_rc3_failure_mode_characterization_research_contract_label as _registry_latest_rc3_failure_mode_characterization_research_contract_label,  # noqa: E501
    get_latest_completed_rc3_findings_human_decision_contract_label as _registry_latest_rc3_findings_human_decision_contract_label,  # noqa: E501
    get_latest_completed_fresh_evidence_validation_design_contract_label as _registry_latest_fresh_evidence_validation_design_contract_label,  # noqa: E501
    get_latest_completed_automation_roadmap_label as _registry_latest_automation_roadmap_label,  # noqa: E501
    get_latest_completed_arbitrage_lane_chain_label as _registry_latest_arbitrage_lane_chain_label,  # noqa: E501
    get_latest_completed_arbitrage_scanner_build_label as _registry_latest_arbitrage_scanner_build_label,  # noqa: E501
    get_next_required_action as _registry_next_required_action,
)

__all__ = [
    "MISSION_FLOW_VERSION",
    "MISSION_FLOW_MODE",
    "MISSION_FLOW_SAFETY_POSTURE",
    "STATE_PASSED",
    "STATE_COMPLETE",
    "STATE_CURRENT",
    "STATE_NEXT",
    "STATE_BLOCKED",
    "STATE_LOCKED",
    "STATE_PARKED",
    "CURRENT_STAGE",
    "LATEST_COMPLETED_BUNDLE",
    "LATEST_COMPLETED_PROTOCOL",
    "LATEST_COMPLETED_PROTOCOL_CONTRACT",
    "LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT",
    "LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT",
    "LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT",
    "LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_STRATEGY_CANDIDATE_RANKING_CONTRACT",
    "LATEST_COMPLETED_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT",
    "LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT",
    "LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT",
    "LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER",
    "LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION",
    "LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW",
    "LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION",
    "LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC",
    "LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET",
    "LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT",
    "LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION",
    "LATEST_COMPLETED_REAL_DATA_QA_PASS_RECEIPT",
    "LATEST_COMPLETED_BASELINE_BACKTEST_PREP_CONTRACT",
    "LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT",
    "LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT",
    "LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT",
    "LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT",
    "LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT",
    "LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT",
    "LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT",
    "LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT",
    "LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT",
    "LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT",
    "LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT",
    "LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT",
    "LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT",
    "LATEST_COMPLETED_AUTOMATION_ROADMAP",
    "LATEST_COMPLETED_ARBITRAGE_LANE_CHAIN",
    "LATEST_COMPLETED_ARBITRAGE_SCANNER_BUILD",
    "NEXT_REQUIRED_ACTION",
    "human_workflow_lane",
    "machine_pipeline_lane",
    "blocked_gates",
    "safety_flags",
    "get_mission_flow_status",
]

MISSION_FLOW_VERSION = "v1"
MISSION_FLOW_MODE = "RESEARCH_ONLY"

# Read-only safety posture: nothing here can execute or mutate anything.
MISSION_FLOW_SAFETY_POSTURE = {
    "mode": MISSION_FLOW_MODE,
    "read_only": True,
    "executes": False,
    "human_approval_required": True,
    "acquires_data": False,
    "inspects_data": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "touches_broker_or_exchange": False,
    "paper_or_live": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "refreshes_dashboard_snapshot": False,
}

# Per-stage status vocabulary (display-only labels).
STATE_PASSED = "PASSED"
STATE_COMPLETE = "COMPLETE"
STATE_CURRENT = "CURRENT"
STATE_NEXT = "NEXT"
STATE_BLOCKED = "BLOCKED"
STATE_LOCKED = "LOCKED"
STATE_PARKED = "PARKED"

# Derived from the read-only bundle registry (single source of truth) so the
# mission-flow feed follows the pipeline from structured metadata instead of a
# hardcoded bundle list. Values are equivalent to the prior hardcoded ones.
CURRENT_STAGE = _registry_current_stage()
LATEST_COMPLETED_BUNDLE = _registry_latest_bundle_label()
LATEST_COMPLETED_PROTOCOL = _registry_latest_protocol_label()
LATEST_COMPLETED_PROTOCOL_CONTRACT = _registry_latest_protocol_contract_label()
LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT = (
    _registry_latest_family_selection_contract_label()
)
LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT = (
    _registry_latest_family_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT = (
    _registry_latest_research_plan_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT = (
    _registry_latest_research_plan_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT = (
    _registry_latest_research_plan_approval_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT = (
    _registry_latest_research_design_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT = (
    _registry_latest_research_design_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT = (
    _registry_latest_research_design_approval_contract_label()
)
LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT = (
    _registry_latest_research_readiness_contract_label()
)
LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT = (
    _registry_latest_external_bot_evidence_intake_contract_label()
)
LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT = (
    _registry_latest_hyperliquid_whale_evidence_contract_label()
)
LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT = (
    _registry_latest_funding_rate_evidence_contract_label()
)
LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT = (
    _registry_latest_bitcoin_cycle_timing_evidence_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT = (
    _registry_latest_daily_alpha_brief_research_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT = (
    _registry_latest_daily_alpha_brief_review_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT = (
    _registry_latest_daily_alpha_brief_approval_contract_label()
)
LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT = (
    _registry_latest_strategy_evidence_scoring_contract_label()
)
LATEST_COMPLETED_STRATEGY_CANDIDATE_RANKING_CONTRACT = (
    _registry_latest_strategy_candidate_ranking_contract_label()
)
LATEST_COMPLETED_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT = (
    _registry_latest_external_human_trader_evidence_contract_label()
)
LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT = (
    _registry_latest_cohort_independence_contract_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT = (
    _registry_latest_real_data_qa_boundary_decision_contract_label()
)
LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT = (
    _registry_latest_real_data_qa_human_approval_packet_contract_label()
)
LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT = (
    _registry_latest_real_data_qa_readiness_checklist_contract_label()
)
LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER = (
    _registry_latest_overnight_research_autopilot_controller_label()
)
LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET = (
    _registry_latest_real_data_qa_human_approval_packet_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION = (
    _registry_latest_real_data_qa_boundary_decision_label()
)
LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION = (
    _registry_latest_pipeline_coverage_reconciliation_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW = (
    _registry_latest_real_data_qa_boundary_readiness_review_label()
)
LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION = (
    _registry_latest_public_spot_source_evaluation_label()
)
LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC = (
    _registry_latest_concrete_spot_provider_adapter_spec_label()
)
LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN = (
    _registry_latest_selected_spot_provider_fetch_runner_dry_run_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET = (
    _registry_latest_real_data_qa_boundary_decision_packet_label()
)
LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT = (
    _registry_latest_real_data_qa_plan_only_contract_label()
)
LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION = (
    _registry_latest_real_data_qa_plan_approval_decision_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION = (
    _registry_latest_real_data_qa_boundary_final_decision_label()
)
# Surfaces that the Manual CSV Real Data QA run produced PASS evidence. This is a
# read-only receipt: it records PASS but moves NO gate -- real_data_qa and
# baseline_backtest stay BLOCKED, and paper / micro-live stay LOCKED, until a
# separate explicit human baseline-prep policy decision.
LATEST_COMPLETED_REAL_DATA_QA_PASS_RECEIPT = _qa_pass_receipt_label()
LATEST_COMPLETED_BASELINE_BACKTEST_PREP_CONTRACT = _baseline_prep_label()
# Surfaces the completed research-only Crypto-D1 V2 Resume-Policy chain
# (research/simulation plan -> simulation runner -> results review) as additive
# latest-completed evidence. Each is read-only research: it moves NO gate --
# real_data_qa and baseline_backtest stay BLOCKED, paper / micro-live / live stay
# LOCKED -- and the only surfaced next step is the human review of the
# resume-policy simulation results.
LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT = (
    _registry_latest_resume_policy_research_plan_contract_label()
)
LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT = (
    _registry_latest_resume_policy_simulation_runner_contract_label()
)
LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT = (
    _registry_latest_resume_policy_results_review_contract_label()
)
# Block 178: the human review decision over the resume-policy results is now
# recorded as additive latest-completed evidence. The recorded human decision is
# DO_NOT_PROMOTE_RESUME_POLICY_YET; recognizing it moves NO gate -- real_data_qa
# and baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED -- and
# the surfaced next step is a research-only continuation, never execution.
LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT = (
    _registry_latest_resume_policy_human_review_decision_contract_label()
)
# Block 179: the post resume-policy research continuation plan is now recorded as
# additive latest-completed evidence. It is a fixed, human-gated, observation-only
# research plan that PRESERVES DO_NOT_PROMOTE_RESUME_POLICY_YET; recognizing it
# moves NO gate -- real_data_qa and baseline_backtest stay BLOCKED, paper /
# micro-live / live stay LOCKED -- and the surfaced next step is a human selecting
# a research-continuation direction, never execution.
LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT = (
    _registry_latest_post_resume_policy_research_continuation_plan_contract_label()
)
# Block 180: the RC1 out-of-sample robustness research spec is now recorded as
# additive latest-completed evidence. It fixes evaluation windows for the
# evidence-leading resume policy with parameters UNCHANGED and PRESERVES
# DO_NOT_PROMOTE_RESUME_POLICY_YET; recognizing it moves NO gate -- real_data_qa
# and baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED -- and
# the surfaced next step is only the human-gated choice to run a later
# research-only replay, never promotion and never execution.
LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT = (
    _registry_latest_rc1_out_of_sample_robustness_research_contract_label()
)
# Block 181: the RC1 out-of-sample replay RUNNER is now recorded as additive
# latest-completed evidence. It is the double-gated, dry-run-verified runner for
# the Block 180 spec; recognizing it runs nothing and does NOT advance the stage:
# the next step stays the human-approved research-only PERSISTED replay run --
# not promotion and not trading execution. DO_NOT_PROMOTE_RESUME_POLICY_YET
# stays preserved; real_data_qa and baseline_backtest stay BLOCKED, paper /
# micro-live / live stay LOCKED.
LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT = (
    _registry_latest_rc1_out_of_sample_replay_runner_contract_label()
)
# Block 182: the RC1 out-of-sample RESULTS REVIEW is now recorded as additive
# latest-completed evidence. It reviewed the persisted RC1 replay report:
# useful held-out evidence, but MATERIALLY DEGRADED versus in-sample, and its
# promotion decision is structurally DO_NOT_PROMOTE_RESUME_POLICY_YET. The
# surfaced next step is a HUMAN EVIDENCE DECISION only -- never promotion and
# never execution. Recognizing it moves NO gate: real_data_qa and
# baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT = (
    _registry_latest_rc1_out_of_sample_results_review_contract_label()
)
# Block 183: the human's RC1 OUT-OF-SAMPLE EVIDENCE DECISION is now recorded as
# additive latest-completed evidence. The human acknowledged the useful held-out
# survival AND the material degradation versus in-sample, kept
# DO_NOT_PROMOTE_RESUME_POLICY_YET, and selected the next research direction:
# RC2 cross-policy stability (re-rank the fixed candidate set over the SAME
# fixed out-of-sample windows, no fitting). The surfaced next step is the
# human-approved, research-only RC2 work -- never promotion and never
# execution. Recognizing it moves NO gate: real_data_qa and baseline_backtest
# stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT = (
    _registry_latest_rc1_oos_human_evidence_decision_contract_label()
)
# Block 184: the RC2 CROSS-POLICY STABILITY research spec is now recorded as
# additive latest-completed evidence. It fixes a pre-registered comparison of
# the six fixed candidates (RP1..RP6, parameters verbatim from Block 175, no
# fitting) over the SAME fixed out-of-sample windows RC1 used, and PRESERVES
# DO_NOT_PROMOTE_RESUME_POLICY_YET. The surfaced next step is only the
# human-approved, research-only replay over that fixed set -- never promotion
# and never trading execution. Recognizing it moves NO gate: real_data_qa and
# baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT = (
    _registry_latest_rc2_cross_policy_stability_research_contract_label()
)
# Block 185: the RC2 cross-policy replay RUNNER is now recorded as additive
# latest-completed evidence. It is the double-gated, dry-run-verified runner for
# the Block 184 spec; recognizing it runs nothing and does NOT advance the
# stage: the next step stays the human-approved research-only PERSISTED replay
# run over the fixed RP1..RP6 set -- not promotion and not trading execution.
# DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved; real_data_qa and
# baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT = (
    _registry_latest_rc2_cross_policy_replay_runner_contract_label()
)
# Block 186: the RC2 CROSS-POLICY RESULTS REVIEW is now recorded as additive
# latest-completed evidence. It reviewed the persisted RC2 replay report and
# recorded the LEADERSHIP FLIP: the RC1 leader leads ZERO out-of-sample ranking
# categories while other fixed candidates (RP4/RP5) lead every category -- as
# research evidence only, NOT selected successors. The review's promotion
# decision is structurally DO_NOT_PROMOTE_RESUME_POLICY_YET and the surfaced
# next step is a HUMAN EVIDENCE DECISION only -- never promotion and never
# execution. Recognizing it moves NO gate: real_data_qa and baseline_backtest
# stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT = (
    _registry_latest_rc2_cross_policy_results_review_contract_label()
)
# Block 187: the human's RC2 CROSS-POLICY EVIDENCE DECISION is now recorded as
# additive latest-completed evidence. The human acknowledged the RC1 leader's
# out-of-sample failure, kept the strongest candidates (RP4/RP5) as EVIDENCE
# ONLY -- NOT selected successors -- kept DO_NOT_PROMOTE_RESUME_POLICY_YET, and
# selected the next research direction: RC3 failure-mode characterization (a
# purely descriptive, human-approved, research-only study over already-
# persisted evidence). The surfaced next step is that human-approved RC3 work
# -- never promotion and never execution. Recognizing it moves NO gate:
# real_data_qa and baseline_backtest stay BLOCKED, paper / micro-live / live
# stay LOCKED.
LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT = (
    _registry_latest_rc2_cross_policy_human_evidence_decision_contract_label()
)
# Block 188: the RC3 FAILURE-MODE CHARACTERIZATION is now recorded as additive
# latest-completed evidence. Purely descriptive and recompute-free over the
# persisted RC1/RC2 reports, it found all four candidate failure modes
# SUPPORTED (volatility-cooldown overfit, regime sensitivity,
# delayed/over-filtered re-entry, ranking instability), explaining why the RC1
# leader failed out of sample. The strongest candidates (RP4/RP5) remain
# EVIDENCE ONLY -- NOT selected successors -- and
# DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. The surfaced next step is
# a HUMAN DECISION over the RC3 findings only -- never promotion and never
# execution. Recognizing it moves NO gate: real_data_qa and baseline_backtest
# stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT = (
    _registry_latest_rc3_failure_mode_characterization_research_contract_label()
)
# Block 189: the human's RC3 FINDINGS DECISION is now recorded as additive
# latest-completed evidence. The resume-policy research thread is CLOSED WITH
# LESSONS, fresh evidence is structurally required before any reconsideration,
# NO successors were selected (RP4/RP5 stay evidence only), and
# DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. The surfaced next step is
# simply awaiting a new, separate, explicit human research directive -- never
# promotion and never execution. Recognizing it moves NO gate: real_data_qa and
# baseline_backtest stay BLOCKED, paper / micro-live / live stay LOCKED.
LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT = (
    _registry_latest_rc3_findings_human_decision_contract_label()
)
# Block 190: the FRESH-EVIDENCE VALIDATION DESIGN is now recorded as additive
# latest-completed evidence. The evidence criteria are FROZEN before any
# qualifying data exists: post-2026-06-08 manually staged daily candles only,
# minimum 180-day window (365 preferred), frozen bars (return > 0, worst DD not
# worse than -35%, Sharpe >= 0.8, top-half stability vs all six fixed
# candidates), one look per window. Passing PROMOTES NOTHING -- it only
# qualifies a candidate for a separate future human reconsideration decision.
# DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved; the surfaced next step is
# simply WAITING for the fresh evidence to accrue. Recognizing it moves NO
# gate: real_data_qa and baseline_backtest stay BLOCKED, paper / micro-live /
# live stay LOCKED.
LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT = (
    _registry_latest_fresh_evidence_validation_design_contract_label()
)
# Links L1-L6: the completed Strategy Factory Automation Roadmap -- the
# read-only research paperwork/control chain (intake adapter, unsigned packet
# schema, batch approval, cycle scheduler SPEC only, report payloads only,
# dashboard/JARVIS display model only). Recognizing it moves NO gate: trading
# remains LOCKED, no scheduler/transport/UI wiring exists, and every future
# block (real wiring, manual-start transport, scheduler build, umbrella
# orchestrator) needs its own separate human approval.
LATEST_COMPLETED_AUTOMATION_ROADMAP = (
    _registry_latest_automation_roadmap_label()
)
# Seq 0-5: the completed Arbitrage Factory V1 lane contract chain (readiness,
# scanner spec, data contract, fee/slippage model, alert/report schema, lane
# review ACCEPTED). Registering it moves NO gate: the scanner build remains a
# separate, future, human-approved block, every future run needs its own
# per-run approval, and execution is absent from the lane by construction.
LATEST_COMPLETED_ARBITRAGE_LANE_CHAIN = (
    _registry_latest_arbitrage_lane_chain_label()
)
# The scanner BUILD is complete (dry scan FAIL/FAIL, research-only, nothing
# written); every RUN stays per-run human-approved and the first persisted
# report stays behind RUN_ARBITRAGE_SCAN_WITH_REPORT. Moves NO gate.
LATEST_COMPLETED_ARBITRAGE_SCANNER_BUILD = (
    _registry_latest_arbitrage_scanner_build_label()
)
NEXT_REQUIRED_ACTION = _registry_next_required_action()

# --- human workflow lane ---------------------------------------------------

_HUMAN_WORKFLOW: tuple[dict[str, str], ...] = (
    {
        "id": "idea_intake",
        "label": "Idea Intake",
        "state": STATE_PASSED,
        "reason": "Strategy ideas captured on paper in the research registry.",
    },
    {
        "id": "research_review",
        "label": "Research Review",
        "state": STATE_PASSED,
        "reason": "Research patterns reviewed; advisory-only, no execution.",
    },
    {
        "id": "candidate_creation",
        "label": "Candidate Creation",
        "state": STATE_PASSED,
        "reason": "Paper candidate strategies described in the registry.",
    },
    {
        "id": "backbone_build",
        "label": "Backbone Build",
        "state": STATE_COMPLETE,
        "reason": "Strategy Factory backbone (Bundles 11-54) complete on paper.",
    },
    {
        "id": "fake_lane",
        "label": "Fake Lane",
        "state": STATE_COMPLETE,
        "reason": "Fake-only dry-walk / report / closure lane complete; no real data used.",  # noqa: E501
    },
    {
        "id": "operator_review_before_real_strategy_intake",
        "label": "Operator Review Before Real Strategy Intake",
        "state": STATE_CURRENT,
        "reason": (
            "You are here. Bundles 42-54 contract chain is complete on paper, "
            "through the Crypto-D1 research-only dry-run research archive or "
            "closure contract, which closes the research-only dry-run lane. "
            "Block 95 DEFINED the next research-only protocol (Crypto-D1 "
            "Strategy Candidate Protocol v1, on paper), Block 97 BUILT the "
            "Strategy Candidate Protocol Contract that validates whether a "
            "proposed candidate plan follows it, Block 99 BUILT the "
            "Strategy Candidate Family Selection Contract that validates which "
            "of the four defined candidate strategy families a research-only "
            "selection packet scopes first, Block 101 BUILT the "
            "Strategy Candidate Family Review Contract that validates whether "
            "the selected/parked families are reasonable, Block 103 BUILT the "
            "Strategy Candidate Research Plan Contract that validates how the "
            "reviewed family selection would be researched before any real "
            "strategy research begins, Block 105 BUILT the Strategy Candidate "
            "Research Plan Review Contract that validates whether that research "
            "plan is reasonable, Block 107 BUILT the Strategy Candidate Research "
            "Plan Approval Contract that records the separate, later human "
            "approval the review READY gate requires, Block 109 BUILT the "
            "Strategy Candidate Research Design Contract that details how the "
            "approved research plan would be carried out before any real "
            "strategy research begins, Block 111 BUILT the Strategy Candidate "
            "Research Design Review Contract that reviews whether that research "
            "design is reasonable, Block 113 BUILT the Strategy Candidate "
            "Research Design Approval Contract that records the separate, later "
            "human approval the research-design-review READY gate requires, "
            "Block 115 BUILT the Strategy Candidate Research Readiness Contract "
            "that records, on paper, that the research-only paper chain is "
            "internally ready -- a final readiness paper gate before the still-"
            "blocked real_data_qa boundary -- Block 117 BUILT the "
            "External Bot Evidence Intake Contract that classifies external AI "
            "trading bot / tool / video ideas into research-only evidence buckets, "
            "Block 119 BUILT the Hyperliquid Whale Evidence Contract that "
            "classifies external Hyperliquid whale-tracking ideas into "
            "research-only evidence buckets, Block 121 BUILT the "
            "Funding Rate Evidence Contract that classifies external funding-rate "
            "scanner ideas into research-only evidence buckets, Block 123 BUILT "
            "the Bitcoin Cycle Timing Evidence Contract that converts the BTC "
            "364-day / 1064-day cycle idea into research-only timing evidence "
            "under the rule that cycle timing tells us when to pay attention, not "
            "when to buy, Block 125 BUILT the Daily Alpha Brief "
            "Research Contract that assembles a daily crypto alpha brief from "
            "already-approved static evidence inputs only (the external-bot, "
            "hyperliquid-whale, funding-rate, and bitcoin-cycle-timing evidence "
            "lanes), under the core rule that the brief tells us what to watch "
            "and research, never what to trade -- its highest stance is "
            "WATCH / RESEARCH_ONLY and it never produces a buy/sell/long/short/"
            "entry/exit/order instruction -- Block 127 BUILT the "
            "Daily Alpha Brief Review Contract that reviews whether an assembled "
            "brief is reasonable, still on paper, treating every input as "
            "external research evidence only; its highest verdict is READY for "
            "human approval and it never produces a trade instruction -- and "
            "Block 129 has now BUILT the Daily Alpha Brief Approval Contract that "
            "records, on paper, a human approval decision over a reviewed brief; "
            "its highest verdict is APPROVED, which only files the reviewed brief "
            "as a research record and never as a trade. With the research-only "
            "external-evidence sub-chain (research -> review -> approval) now "
            "complete, the only next step is the human-controlled real-data QA "
            "boundary decision -- a human judgment about whether to ever cross "
            "from research-only paper work into real-data QA. That boundary "
            "decision is not a build step and not an authorization: it fetches no "
            "data, runs no QA, baseline, or backtest, places no order, and writes "
            "no runtime artifact; real_data_qa stays BLOCKED unless a separate, "
            "future, human-approved boundary contract authorizes it. "
            "Nothing is authorized to run: real strategy intake remains paused for "
            "operator review."
        ),
    },
    {
        "id": "real_strategy_intake",
        "label": "Real Strategy Intake",
        "state": STATE_BLOCKED,
        "reason": "Blocked - not started. Requires explicit human approval; never automated.",  # noqa: E501
    },
)

# --- machine pipeline lane -------------------------------------------------

_MACHINE_PIPELINE: tuple[dict[str, str], ...] = (
    {
        "id": "strategy_factory_backbone",
        "label": "Strategy Factory Backbone",
        "state": STATE_COMPLETE,
        "reason": "Read-only contract backbone in place; executes nothing.",
    },
    {
        "id": "fake_dry_walk",
        "label": "Fake Dry Walk",
        "state": STATE_COMPLETE,
        "reason": "Deterministic fake walk produced on paper; no real data.",
    },
    {
        "id": "fake_report_renderer",
        "label": "Fake Report Renderer",
        "state": STATE_COMPLETE,
        "reason": "Fake report rendered from in-memory fixtures only.",
    },
    {
        "id": "fake_lane_closure",
        "label": "Fake Lane Closure",
        "state": STATE_COMPLETE,
        "reason": "Fake-only lane closed; no real-data capability unlocked.",
    },
    {
        "id": "crypto_d1_intake_reconciliation",
        "label": "Crypto-D1 Intake Reconciliation",
        "state": STATE_COMPLETE,
        "reason": "Bundle 41 reconciliation contract template complete on paper.",  # noqa: E501
    },
    {
        "id": "crypto_d1_acquire_decision_contract",
        "label": "Crypto-D1 Acquire Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 42 complete (" + ACQUIRE_SCHEMA_VERSION + "). Read-only "
            "acquire-decision template; acquires nothing, decides nothing."
        ),
    },
    {
        "id": "crypto_d1_source_class_contract",
        "label": "Crypto-D1 Source Class Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 43 complete (" + SOURCE_CLASS_SCHEMA_VERSION + "). "
            "Read-only source-class paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_source_specification_contract",
        "label": "Crypto-D1 Source Specification Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 44 complete (" + SPEC_SCHEMA_VERSION + "). Read-only "
            "source-specification paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_offline_acquisition_plan_contract",
        "label": "Crypto-D1 Offline Acquisition Plan Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 45 complete (" + PLAN_SCHEMA_VERSION + "). Read-only "
            "offline-acquisition-plan paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_pre_acquisition_human_gate_contract",
        "label": "Crypto-D1 Pre-Acquisition Human Approval Gate",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 46 complete (" + GATE_SCHEMA_VERSION + "). Read-only "
            "human-approval-gate paper contract only. It defines the gate but "
            "authorizes nothing: no data acquisition, QA, baseline, backtest, "
            "simulation, paper, broker, exchange, or automation is unlocked."
        ),
    },
    {
        "id": "crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
        "label": "Crypto-D1 Human-Approved Offline Acquisition Execution Boundary Contract",  # noqa: E501
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 47 complete (" + BOUNDARY_SCHEMA_VERSION + "). Read-only "
            "execution-boundary paper contract only. It authorizes nothing and "
            "executes nothing: no data acquisition, data fetch, data "
            "inspection, QA, baseline, backtest, simulation, paper, live, "
            "broker, exchange, or automation is unlocked."
        ),
    },
    {
        "id": "crypto_d1_post_boundary_research_only_next_step_contract",
        "label": "Crypto-D1 Post-Boundary Research-Only Next-Step Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 48 complete (" + NEXT_STEP_SCHEMA_VERSION + "). Read-only "
            "post-boundary next-step paper contract only. It only DECIDES which "
            "research-only, dry-run-preview-only contract is built next; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, QA, baseline, backtest, simulation, "
            "paper, live, broker, exchange, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_preview_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Preview Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 49 complete (" + PREVIEW_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run PREVIEW paper contract only. It only "
            "PREVIEWS, on paper, what a research-only dry run would look like; "
            "it authorizes nothing and executes nothing: no dry-run execution, "
            "no real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_review_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 50 complete (" + REVIEW_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run REVIEW paper contract only. It only REVIEWS, "
            "on paper, what a research-only dry-run preview produced; it "
            "authorizes nothing and executes nothing: no dry-run execution, no "
            "real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_decision_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 51 complete (" + DECISION_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run DECISION paper contract only. It only "
            "DECIDES, on paper, what a research-only dry-run review produced and "
            "which research-only dry-run-decision-review-only contract is built "
            "next; it authorizes nothing and executes nothing: no dry-run "
            "execution, no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_decision_review_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Decision Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 52 complete (" + DECISION_REVIEW_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run DECISION REVIEW paper contract "
            "only. It only REVIEWS, on paper, what a research-only dry-run "
            "decision produced and which research-only dry-run-final-decision-"
            "only contract is built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_final_decision_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Final Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 53 complete (" + FINAL_DECISION_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run FINAL DECISION paper contract "
            "only. It only FINALIZES, on paper, the research-only dry-run "
            "decision and which research-only research-archive-or-closure-only "
            "contract is built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_research_archive_or_closure_contract",  # noqa: E501
        "label": "Crypto-D1 Research-Only Dry-Run Research Archive or Closure Contract",  # noqa: E501
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 54 complete (" + ARCHIVE_OR_CLOSURE_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run RESEARCH ARCHIVE OR CLOSURE paper "
            "contract only. It only records, on paper, whether the research-"
            "only dry-run lane should be ARCHIVED or CLOSED, which closes the "
            "Crypto-D1 research-only dry-run lane; it authorizes nothing and "
            "executes nothing: no dry-run execution, no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_next_protocol_definition",
        "label": "Crypto-D1 Research-Only Next Protocol Definition",
        "state": STATE_COMPLETE,
        "reason": (
            "Protocol defined (" + NEXT_RESEARCH_PROTOCOL_SCHEMA_VERSION + "). "
            "The Crypto-D1 Strategy Candidate Protocol v1 is DEFINED on paper "
            "(BTC/ETH/SOL, spot, daily candles, four candidate strategy "
            "families); it authorizes nothing and executes nothing: no real "
            "data acquisition, data fetch, data inspection, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, market-data "
            "validation, paper/live, broker/exchange, automation, or runtime/"
            "registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_protocol_contract",
        "label": "Crypto-D1 Strategy Candidate Protocol Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 97 complete ("
            + STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Protocol Contract only. It only "
            "VALIDATES, on paper, whether a proposed candidate plan follows the "
            "Crypto-D1 Strategy Candidate Protocol v1; it authorizes nothing and "
            "executes nothing: no real data acquisition, data fetch, data "
            "inspection, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, market-data validation, paper, live, broker, "
            "exchange, automation, or runtime/registry/dashboard write is "
            "unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_family_selection_contract",
        "label": "Crypto-D1 Strategy Candidate Family Selection Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 99 complete ("
            + STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Family Selection Contract only. It "
            "only VALIDATES, on paper, which of the four defined candidate "
            "strategy families a research-only selection packet scopes first; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_family_review_contract",
        "label": "Crypto-D1 Strategy Candidate Family Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 101 complete ("
            + STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Family Review Contract only. It "
            "only REVIEWS, on paper, whether the candidate strategy families a "
            "research-only selection packet chose or parked are reasonable; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 103 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Research Plan Contract only. It only "
            "validates, on paper, how the reviewed family selection would be "
            "researched before any real strategy research begins; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_review_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 105 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Plan Review Contract "
            "only. It only reviews, on paper, whether the Block 103 research "
            "plan is reasonable before any real strategy research begins; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_approval_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Approval Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 107 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Plan Approval Contract "
            "only. It only records, on paper, the separate, later human approval "
            "the Block 105 research-plan review READY gate requires before any "
            "real strategy research begins; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_contract",
        "label": "Crypto-D1 Strategy Candidate Research Design Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 109 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Contract only. It "
            "only details, on paper, how the Block 107 approved research plan "
            "would be carried out before any real strategy research begins; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_review_contract",
        "label": "Crypto-D1 Strategy Candidate Research Design Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 111 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Review Contract "
            "only. It only records, on paper, a human review of whether the "
            "Block 109 research design is reasonable before any real strategy "
            "research begins; it authorizes nothing and executes nothing: no "
            "real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_approval_contract",
        "label": (
            "Crypto-D1 Strategy Candidate Research Design Approval Contract"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 113 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Approval Contract "
            "only. It only records, on paper, the separate, later human approval "
            "the Block 111 research-design-review READY gate requires before any "
            "real strategy research begins; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_readiness_contract",
        "label": "Crypto-D1 Strategy Candidate Research Readiness Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 115 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Readiness Contract only. "
            "It only records, on paper, that the research-only paper chain is "
            "internally ready -- a final readiness paper gate before the still-"
            "blocked real_data_qa boundary; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked. Readiness is paper "
            "readiness ONLY: real_data_qa stays BLOCKED."
        ),
    },
    {
        "id": "crypto_d1_external_bot_evidence_intake_contract",
        "label": "Crypto-D1 External Bot Evidence Intake Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 117 complete ("
            + STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION
            + "). Read-only External Bot Evidence Intake Contract only. It only "
            "classifies external AI trading bot / tool / video ideas into "
            "research-only evidence buckets (useful_for_research, "
            "risky_requires_validation, blocked_execution_feature, "
            "dashboard_or_brief_candidate, ignore_or_marketing_claim), marking "
            "every execution-capable idea blocked and every attractive-but-"
            "unverified claim risky, and never converting evidence into "
            "permission; it authorizes nothing and executes nothing: no real data "
            "acquisition, data fetch, data inspection, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, market-data "
            "validation, order placement, broker, exchange, Telegram trade "
            "command, TradingView execution webhook, portfolio account control, "
            "live deployment, cloud bot operation, paper, live, automation, or "
            "runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_hyperliquid_whale_evidence_contract",
        "label": "Crypto-D1 Hyperliquid Whale Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 119 complete ("
            + CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Hyperliquid Whale Evidence Contract only. It only "
            "classifies external Hyperliquid whale-tracking ideas into research-"
            "only evidence buckets (useful_for_research, risky_requires_validation, "
            "blocked_execution_feature, ignore_or_marketing_claim, "
            "needs_independent_confirmation), marking every execution-capable whale "
            "idea blocked, every unverified whale movement claim risky, requiring "
            "independent confirmation, and never converting whale evidence into "
            "permission; it authorizes nothing and executes nothing: no Hyperliquid "
            "API connection, wallet monitoring, account/portfolio access, exchange "
            "connection, real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, copy/follow whale execution, whale alert automation, "
            "Telegram trade command, paper, live, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_funding_rate_evidence_contract",
        "label": "Crypto-D1 Funding Rate Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 121 complete ("
            + CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Funding Rate Evidence Contract only. It only "
            "classifies external funding-rate scanner ideas into research-"
            "only evidence buckets (useful_for_research, risky_requires_validation, "
            "blocked_execution_feature, ignore_or_marketing_claim, "
            "needs_independent_confirmation), marking every execution-capable "
            "funding idea blocked, every unverified funding-rate claim risky, "
            "requiring independent confirmation, and never converting funding-rate "
            "evidence into permission or 'free money'; it authorizes nothing and "
            "executes nothing: no exchange API connection, futures/perps account "
            "access, position opening, hedging, carry-trade execution, arbitrage "
            "execution, live funding monitor, real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper, live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_bitcoin_cycle_timing_evidence_contract",
        "label": "Crypto-D1 Bitcoin Cycle Timing Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 123 complete ("
            + CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Bitcoin Cycle Timing Evidence Contract only -- a "
            "higher-level macro timing filter inserted before the Daily Alpha "
            "Brief contract. It only converts the BTC 364-day / 1064-day cycle "
            "idea into research-only timing evidence (an early/active/late/expired "
            "cycle-bottom watch zone and a caution/accumulation-watch/recovery-"
            "watch/no-signal evidence stance), under the core rule that cycle "
            "timing tells us when to pay attention, not when to buy; it requires "
            "independent confirmation and never converts timing evidence into "
            "permission or a buy instruction; it authorizes nothing and executes "
            "nothing: no BTC data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper, live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_research_contract",
        "label": "Crypto-D1 Daily Alpha Brief Research Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 125 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Research Contract only. It only "
            "assembles, on paper, a daily crypto alpha brief from already-"
            "approved static evidence inputs only (the external-bot, hyperliquid-"
            "whale, funding-rate, and bitcoin-cycle-timing evidence lanes) into a "
            "deterministic structured brief with an overall research decision and "
            "stance, under the core rule that the brief tells us what to watch and "
            "research, never what to trade. Its highest stance is WATCH / "
            "RESEARCH_ONLY and it never produces a buy/sell/long/short/entry/exit/"
            "order instruction; every input is treated as external research "
            "evidence only, always requires independent confirmation, and is never "
            "converted into permission. It authorizes nothing and executes "
            "nothing: no data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_review_contract",
        "label": "Crypto-D1 Daily Alpha Brief Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 127 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Review Contract only. It only "
            "reviews, on paper, whether an assembled daily crypto alpha brief is "
            "reasonable -- derived from already-approved static evidence inputs "
            "only (the external-bot, hyperliquid-whale, funding-rate, and bitcoin-"
            "cycle-timing evidence lanes) -- and emits a research verdict, under "
            "the core rule that the review tells us whether the brief is "
            "reasonable to escalate for human approval, never what to trade. Its "
            "highest verdict is READY and it never produces a buy/sell/long/short/"
            "entry/exit/order instruction; every input is treated as external "
            "research evidence only, always requires independent confirmation, and "
            "is never converted into permission. It authorizes nothing and "
            "executes nothing: no data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_approval_contract",
        "label": "Crypto-D1 Daily Alpha Brief Approval Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 129 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Approval Contract only. It only "
            "records, on paper, a human approval decision over a reviewed daily "
            "crypto alpha brief -- derived from already-approved static evidence "
            "inputs only (the external-bot, hyperliquid-whale, funding-rate, and "
            "bitcoin-cycle-timing evidence lanes) -- under the core rule that an "
            "approval only files the reviewed brief as a research record, never "
            "what to trade. Its highest verdict is APPROVED and it never produces "
            "a buy/sell/long/short/entry/exit/order instruction; every input is "
            "treated as external research evidence only, always requires "
            "independent confirmation, and is never converted into permission. It "
            "authorizes nothing and executes nothing: no data fetch, API call, "
            "dataset inspection, real data acquisition, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_evidence_scoring_contract",
        "label": "Crypto-D1 Strategy Evidence Scoring Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 131 complete ("
            + CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Evidence Scoring Contract only -- a "
            "research-only evidence/scoring support contract. It only assigns, on "
            "paper, a static evidence summary for a strategy candidate exactly one "
            "outcome (BLOCK > NEEDS_MORE_DATA > KEEP_WATCH > PROMOTE_TO_REVIEW), "
            "under the core rule that it scores evidence, never what to trade. Its "
            "highest outcome is PROMOTE_TO_REVIEW and it never produces a buy/sell/"
            "long/short/entry/exit/order instruction; every input is treated as "
            "static research evidence only, always requires independent "
            "confirmation, and is never converted into permission. It authorizes "
            "nothing and executes nothing: no data fetch, API call, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_ranking_contract",
        "label": "Crypto-D1 Strategy Candidate Ranking Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 162 complete ("
            + CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Ranking Contract only -- a "
            "research-only evidence/scoring support contract. It only ranks, on "
            "paper, a static set of already-scored strategy candidates into a "
            "review shortlist using only independent positive cohort counts and "
            "booked paper observations (BLOCK > NEEDS_MORE_CANDIDATES > NO_SHORTLIST "
            "> SHORTLIST_FOR_REVIEW), where only a PROMOTE_TO_REVIEW candidate with "
            "enough independent cohorts is shortlist-eligible, under the core rule "
            "that it ranks evidence, never what to trade. Its highest outcome is a "
            "research-support signal (SHORTLIST_FOR_REVIEW) and it never produces a "
            "buy/sell/long/short/entry/exit/order instruction; every input is "
            "treated as static research evidence only, always requires independent "
            "confirmation, and is never converted into permission. It authorizes "
            "nothing and executes nothing: no data fetch, API call, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_external_human_trader_evidence_contract",
        "label": "Crypto-D1 External Human Trader Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 163 complete ("
            + CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only External Human Trader Evidence Contract only -- a "
            "research-only evidence-intake support contract. It only classifies, on "
            "paper, a static external human-trader call/claim into exactly one lane "
            "(research_note / risky_unverified / hype_discard) and logs it as an "
            "observation only (BLOCK > NO_EVIDENCE > DISCARD_HYPE > "
            "LOG_AS_OBSERVATION), under the core rule that a human's call is "
            "research evidence only and never counts as proof. A logged observation "
            "never produces a buy/sell/long/short/entry/exit/order instruction; "
            "every input is treated as static research evidence only, always "
            "requires independent confirmation, and is never converted into "
            "permission. It authorizes nothing and executes nothing: no data fetch, "
            "API call, dataset inspection, real data acquisition, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked. Recognizing it is purely additive latest-"
            "completed metadata: it does not advance the stage past the human-"
            "controlled real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_cohort_independence_correlation_penalty_contract",
        "label": "Crypto-D1 Cohort Independence / Correlation Penalty Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 132 complete ("
            + CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Cohort Independence / Correlation Penalty Contract "
            "only -- a research-only evidence/scoring support contract. It only "
            "scores, on paper, whether a set of already-booked paper positions "
            "forms genuinely independent cohorts or merely correlated/duplicate "
            "ones (sharing symbol+direction, macro event, market regime, open/"
            "close timing window, or signal family) and reports whether the "
            "independent-booked-cohort sample can SUPPORT a promote-to-review "
            "judgment, under the core rule that it scores evidence independence, "
            "never what to trade. Its highest output is a research-support signal "
            "(can_support_promote_to_review) and it never produces a buy/sell/long/"
            "short/entry/exit/order instruction; every input is treated as static "
            "research evidence only, always requires independent confirmation, and "
            "is never converted into permission. It authorizes nothing and "
            "executes nothing: no data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_boundary_decision_contract",
        "label": "Crypto-D1 Real Data QA Boundary Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 134 complete ("
            + CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION
            + "). Read-only Real Data QA Boundary Decision Contract only -- the "
            "research-only paper contract that defines the structured human "
            "decision packet/gate reviewed BEFORE any Real Data QA may even be "
            "planned. It only assigns, on paper, a static evidence summary exactly "
            "one outcome (BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_DECISION) and "
            "assembles that packet for a human, under the core rule that it readies "
            "a human decision, never what to trade and never an unlock. Its highest "
            "outcome is READY_FOR_HUMAN_DECISION and it never produces a buy/sell/"
            "long/short/entry/exit/order instruction; every input is treated as "
            "static research evidence only, always requires independent "
            "confirmation, and is never converted into permission. It authorizes "
            "nothing and executes nothing: no data fetch, API call, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_human_approval_packet_contract",
        "label": "Crypto-D1 Real Data QA Human Approval Packet Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 136 (Phase A) complete ("
            + CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_SCHEMA_VERSION
            + "). Read-only Real Data QA Human Approval Packet Contract only -- the "
            "research-only paper contract that defines the structured eight-field "
            "human approval packet plus an exact approval phrase a person must "
            "complete BEFORE any Real Data QA may even be planned. It only assigns, "
            "on paper, a static packet exactly one outcome (BLOCK / INCOMPLETE / "
            "COMPLETE), under the core rule that COMPLETE only marks the packet "
            "ready for human review, never what to trade and never an unlock. It "
            "never produces a buy/sell/long/short/entry/exit/order instruction; "
            "every input is treated as static research evidence only, always "
            "requires independent confirmation, and is never converted into "
            "permission. It authorizes nothing and executes nothing: no data fetch, "
            "API call, dataset inspection, real data acquisition, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked. Recognizing it is purely additive latest-"
            "completed metadata: it does not advance the stage past the human-"
            "controlled real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_readiness_checklist_contract",
        "label": "Crypto-D1 Real Data QA Readiness Checklist Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 136 (Phase B) complete ("
            + CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_SCHEMA_VERSION
            + "). Read-only Real Data QA Readiness Checklist Contract only -- the "
            "research-only paper contract that defines the eight-item readiness "
            "checklist that must ALL pass BEFORE a human is even asked to approve "
            "Real Data QA. It only assigns, on paper, a static payload exactly one "
            "outcome (BLOCK / NOT_READY / READY), under the core rule that READY "
            "only means the checklist passed and this is ready for a separate human "
            "approval review, never what to trade and never an unlock. It never "
            "produces a buy/sell/long/short/entry/exit/order instruction; every "
            "input is treated as static research evidence only, always requires "
            "independent confirmation, and is never converted into permission. It "
            "authorizes nothing and executes nothing: no data fetch, API call, "
            "dataset inspection, real data acquisition, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked. Recognizing it is purely additive latest-"
            "completed metadata: it does not advance the stage past the human-"
            "controlled real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_overnight_research_autopilot_controller",
        "label": "SPARTA Overnight Research Autopilot Controller",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 152 complete ("
            + CRYPTO_D1_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_SCHEMA_VERSION
            + "). Read-only Overnight Research Autopilot Controller only -- the "
            "research-only PLANNING controller that, given a static caller-supplied "
            "status summary, reasons on paper over which safe research-only paper "
            "bundles to prepare next, the only paths each may touch, the scoped "
            "tests to run, and a commit/push policy that keeps every commit and "
            "every push gated behind explicit per-run human approval. It is a "
            "planner, not an actor: it never produces a buy/sell/long/short/entry/"
            "exit/order instruction; every input is treated as static research "
            "evidence only, always requires independent confirmation, and is never "
            "converted into permission. It authorizes nothing and executes nothing: "
            "no staging, commit, push, data fetch, API call, dataset inspection, "
            "real data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked. Recognizing it is purely additive latest-completed metadata: "
            "it does not advance the stage past the human-controlled real-data QA "
            "boundary and must not imply automatic execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_human_approval_packet",
        "label": (
            "Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 155 complete ("
            + CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_SCHEMA_VERSION
            + "). Read-only DECISION-BRIEFING packet only -- the single pure, "
            "research-only document a human operator reads at the parked real-data "
            "QA boundary before deciding whether to allow the FIRST controlled, "
            "read-only Real Data QA step. It states where the chain is parked, "
            "confirms the read-only provider/adapter/autopilot stack (Blocks 152/"
            "153/154) is shipped, registered, and reflected, names precisely what a "
            "separate future human approval would permit, and names precisely what "
            "stays forbidden. It is a briefing, not an actor: it authorizes nothing "
            "and executes nothing -- no staging, commit, push, data fetch, API "
            "call, dataset inspection, real data acquisition, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked. Recognizing it is purely additive latest-"
            "completed metadata: it does not advance the stage past the human-"
            "controlled real-data QA boundary and must not imply automatic "
            "execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_human_controlled_real_data_qa_boundary_decision_layer",
        "label": (
            "Crypto-D1 Human-Controlled Real Data QA Boundary Decision Layer"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 158 complete ("
            + CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_SCHEMA_VERSION
            + "). Read-only DECISION LAYER only -- the pure, research-only, human-"
            "driven gate at the parked real-data QA boundary. Absent human approval "
            "it returns HOLD_AWAIT; with the explicit approval token it permits ONLY "
            "the next read-only planning/packet step (never execution); on forbidden "
            "flags or mission-flow misalignment it returns BLOCK. It is a decision "
            "gate, not an actor: it authorizes nothing and executes nothing -- no "
            "staging, commit, push, data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked. The only "
            "thing a PERMIT outcome grants is the next read-only planning/packet "
            "step, never an unlock of real_data_qa. Recognizing it is purely "
            "additive latest-completed metadata: it does not advance the stage past "
            "the human-controlled real-data QA boundary and must not imply automatic "
            "execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_pipeline_coverage_reconciliation_layer",
        "label": "Crypto-D1 Pipeline Coverage Reconciliation",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 161 complete. Read-only COVERAGE METADATA only -- it records, on "
            "paper, that the downstream Crypto-D1 source/provider/fetch/Databento/"
            "inventory/data-QA modules found by the Bundle 160 inventory already "
            "exist, are tested, and are committed, yet stay PARKED behind the human-"
            "controlled real-data QA boundary. The gap was visibility, not "
            "authorship. It does NOT register those modules as active or executable "
            "stages and does NOT approve them for execution. It is a coverage map, "
            "not an actor: it authorizes nothing and executes nothing -- no staging, "
            "commit, push, data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, trade "
            "signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked. Listing a "
            "parked module here is never an unlock of real_data_qa. Recognizing it "
            "is purely additive latest-completed metadata: it does not advance the "
            "stage past the human-controlled real-data QA boundary and must not "
            "imply automatic execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_boundary_readiness_review",
        "label": "Crypto-D1 Real Data QA Boundary Readiness Review",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 166 complete. Read-only READINESS REVIEW only -- a pure, "
            "research-only paper review that reasons over a static caller-supplied "
            "summary of the parked boundary and returns one of exactly two verdicts "
            "(READY_FOR_HUMAN_BOUNDARY_DECISION when all ten boundary-readiness "
            "protections are in place and no unsafe flag is set, otherwise "
            "HOLD_NEEDS_MORE_PREP). It is a readiness verdict, not an actor: it "
            "authorizes nothing and executes nothing -- no staging, commit, push, "
            "data fetch, API call, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Even a READY verdict only "
            "means the prep is sound enough to put the decision in front of a human; "
            "it is never an unlock of real_data_qa and never a boundary crossing. "
            "Recognizing it is purely additive latest-completed metadata: it does "
            "not advance the stage past the human-controlled real-data QA boundary "
            "and must not imply automatic execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_public_spot_source_evaluation",
        "label": "Crypto-D1 Public Read-Only Spot Source Evaluation",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 167 complete. Read-only SOURCE EVALUATION only -- a pure, "
            "research-only paper contract that reasons over a static caller-supplied "
            "description of a candidate public read-only spot data source and returns "
            "one of exactly two verdicts (READY_FOR_HUMAN_SOURCE_REVIEW when all ten "
            "evaluation items pass and no unsafe flag is set, otherwise "
            "HOLD_NEEDS_MORE_PREP). It is a source-evaluation verdict, not an actor: "
            "it authorizes nothing and executes nothing -- no staging, commit, push, "
            "data fetch, API call, endpoint call, URL fetch, network open, credential "
            "read, dataset inspection, real data acquisition, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, Telegram "
            "trade command, paper/live, automation, or runtime/registry/dashboard "
            "write is unlocked. Even a READY verdict only means the paper description "
            "is sound enough for a human to review the source; it is never an unlock "
            "of real_data_qa and never a boundary crossing. Recognizing it is purely "
            "additive latest-completed metadata: it does not advance the stage past "
            "the human-controlled real-data QA boundary and must not imply automatic "
            "execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_concrete_spot_provider_adapter_spec",
        "label": "Crypto-D1 Concrete Read-Only Spot Provider Adapter Spec",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 168 complete. Read-only ADAPTER SPEC only -- a pure, "
            "research-only paper contract that reasons over a static caller-supplied "
            "specification of a future concrete read-only spot provider adapter "
            "(aligned with the Block 151 read-only spot adapter rules) and returns "
            "one of exactly two verdicts (READY_FOR_HUMAN_SPEC_REVIEW when all ten "
            "spec items pass and no unsafe flag is set, otherwise "
            "HOLD_NEEDS_MORE_PREP). It is a spec-review verdict, not an actor: it "
            "authorizes nothing and executes nothing -- no staging, commit, push, "
            "provider implementation, data fetch, API call, endpoint call, URL "
            "fetch, network open, credential read, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, trade "
            "signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked. Even a "
            "READY verdict only means the paper spec is sound enough for a human to "
            "review the design; it is never an unlock of real_data_qa and never a "
            "boundary crossing. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary and must not imply automatic execution or "
            "auto-push."
        ),
    },
    {
        "id": "crypto_d1_selected_spot_provider_fetch_runner_dry_run",
        "label": (
            "Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 169 complete. Read-only DRY RUN only -- a pure, research-only "
            "paper contract that reasons over a static caller-supplied description "
            "of a dry run of the selected read-only spot provider fetch runner, "
            "exercised only against an in-memory FAKE provider (aligned with the "
            "Block 151 read-only spot adapter rules), and returns one of exactly "
            "two verdicts (READY_FOR_HUMAN_DRY_RUN_REVIEW when all ten dry-run "
            "items pass and no unsafe flag is set, otherwise HOLD_NEEDS_MORE_PREP). "
            "It is a dry-run-review verdict, not an actor: it authorizes nothing "
            "and executes nothing -- no staging, commit, push, real provider "
            "injection, data fetch, API call, endpoint call, URL fetch, network "
            "open, credential read, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Even a READY verdict "
            "only means the paper dry run is sound enough for a human to review the "
            "exercise; it is never an unlock of real_data_qa and never a boundary "
            "crossing. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary and must not imply automatic execution or "
            "auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_boundary_decision_packet",
        "label": (
            "Crypto-D1 Real Data QA Boundary Decision Packet"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 170 complete. Read-only BOUNDARY DECISION PACKET only -- a pure, "
            "research-only contract that assembles, from static input, the "
            "human-facing decision packet for the parked real data QA boundary and "
            "offers four read-only decision options that are recommendations only. "
            "It is a decision packet, not an actor: it authorizes nothing and "
            "executes nothing -- no staging, commit, push, data fetch, API call, "
            "endpoint call, URL fetch, network open, credential read, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Even its highest option authorizes nothing beyond building "
            "another pure read-only research contract; it is never an unlock of "
            "real_data_qa, never an approval of real_data_qa execution, and never a "
            "boundary crossing. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary and must not imply automatic execution or "
            "auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_plan_only_contract",
        "label": (
            "Crypto-D1 Real Data QA Plan-Only Contract"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 171 complete. Read-only PLAN-ONLY contract only -- a pure, "
            "research-only contract that drafts, from static input, a plan (text and "
            "scope only) for a future real data QA step. It is a plan proposal, not "
            "an actor: it authorizes nothing and executes nothing -- no staging, "
            "commit, push, data fetch, API call, endpoint call, URL fetch, network "
            "open, credential read, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. The plan is text and "
            "scope only; it is never an unlock of real_data_qa, never an approval of "
            "real_data_qa execution, and never a boundary crossing. Recognizing it "
            "is purely additive latest-completed metadata: it does not advance the "
            "stage past the human-controlled real-data QA boundary and must not "
            "imply automatic execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_plan_approval_decision",
        "label": (
            "Crypto-D1 Real Data QA Plan Approval Decision Contract"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 172 complete. Read-only PLAN APPROVAL DECISION only -- a pure, "
            "research-only contract that reasons over a static caller-supplied "
            "requested decision and an optional Block 171 plan-only contract and "
            "records exactly one of four decisions (APPROVE_PLAN_ONLY, REJECT_PLAN, "
            "REQUEST_PLAN_REVISION, KEEP_BOUNDARY_BLOCKED) about the plan. It is a "
            "plan-approval verdict, not an actor: it authorizes nothing and "
            "executes nothing -- no staging, commit, push, data fetch, API call, "
            "endpoint call, URL fetch, network open, credential read, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Its single highest grant, APPROVE_PLAN_ONLY, approves "
            "only the plan's text and scope as a future candidate; it is never an "
            "unlock of real_data_qa, never an approval of real_data_qa execution, "
            "and never a boundary crossing. Recognizing it is purely additive "
            "latest-completed metadata: it does not advance the stage past the "
            "human-controlled real-data QA boundary and must not imply automatic "
            "execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_boundary_final_decision",
        "label": (
            "Crypto-D1 Real Data QA Boundary Final Decision Contract"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 174 complete. Read-only BOUNDARY FINAL DECISION only -- a pure, "
            "research-only contract that reasons over the static caller-supplied "
            "Block 170 packet, Block 171 plan, and Block 172 plan approval decision "
            "and records exactly one of four final decisions "
            "(AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT, "
            "REQUEST_MORE_RESEARCH, REJECT_REAL_DATA_QA_PATH_FOR_NOW, "
            "KEEP_REAL_DATA_QA_BLOCKED). It is a finalization verdict, not an actor: "
            "it authorizes nothing and executes nothing -- no staging, commit, push, "
            "data fetch, API call, endpoint call, URL fetch, network open, "
            "credential read, dataset inspection, real data acquisition, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, order "
            "placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Its single highest grant, "
            "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT, authorizes only the "
            "drafting of the next read-only preparation contract as a future "
            "candidate; it is never an unlock of real_data_qa, never an approval of "
            "real_data_qa execution, and never a boundary crossing. Recognizing it "
            "is purely additive latest-completed metadata: it does not advance the "
            "stage past the human-controlled real-data QA boundary and must not "
            "imply automatic execution or auto-push."
        ),
    },
    {
        "id": "crypto_d1_resume_policy_results_review",
        "label": "Crypto-D1 V2 Resume-Policy Results Review / Decision",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 177 read-only resume-policy results-review / "
            "decision contract recorded DO_NOT_PROMOTE_RESUME_POLICY_YET over the "
            "Block 176 simulation evidence. It acquired no data, ran no QA, "
            "baseline, backtest, or simulation, placed no order, automated "
            "nothing, and wrote no runtime/registry/dashboard artifact. It "
            "unlocked nothing: real_data_qa and baseline_backtest stay BLOCKED "
            "and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_resume_policy_human_review_recorded",
        "label": "Crypto-D1 V2 Resume-Policy Human Review Recorded / Research Continuation",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 178 read-only human review decision contract "
            "recorded a human's review of the resume-policy SIMULATION results "
            "(RP6 leads all categories) with the decision "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET. It acquired no data, ran no QA, "
            "baseline, backtest, or simulation, placed no order, automated "
            "nothing, and wrote no runtime/registry/dashboard artifact. It "
            "unlocked nothing: real_data_qa and baseline_backtest stay BLOCKED "
            "and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_post_resume_policy_research_continuation_direction_selection",
        "label": "Crypto-D1 V2 Post Resume-Policy Research Continuation Direction Selection",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the human selected the RC1 out-of-sample robustness "
            "direction from the Block 179 plan and the Block 180 read-only RC1 "
            "spec contract recorded it while preserving "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET. It acquired no data, ran no QA, "
            "baseline, backtest, simulation, or optimization, placed no order, "
            "automated nothing, and wrote no runtime/registry/dashboard "
            "artifact. It unlocked nothing: real_data_qa and baseline_backtest "
            "stay BLOCKED and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc1_out_of_sample_replay_approval",
        "label": "Crypto-D1 V2 RC1 Out-of-Sample Replay Approval",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the human approved the RC1 replay, the Block 181 "
            "runner persisted the simulated replay report over the fixed Block "
            "180 windows with the leading policy's parameters UNCHANGED, and "
            "the Block 182 read-only results review scored it. No real order "
            "was placed; DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It "
            "unlocked nothing: real_data_qa and baseline_backtest stay BLOCKED "
            "and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc1_out_of_sample_evidence_decision",
        "label": "Crypto-D1 V2 RC1 Out-of-Sample Evidence Decision",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 183 read-only human evidence decision "
            "contract recorded the human's judgment over the RC1 out-of-sample "
            "evidence: useful held-out survival acknowledged, material "
            "degradation versus in-sample acknowledged, decision kept at "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET, and the selected research "
            "direction is RC2 cross-policy stability. It unlocked nothing: "
            "real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc2_cross_policy_stability_research_approval",
        "label": "Crypto-D1 V2 RC2 Cross-Policy Stability Research Approval",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the human approved the RC2 direction and the Block 184 "
            "read-only RC2 cross-policy stability spec recorded the fixed, "
            "pre-registered comparison plan: RP1..RP6 verbatim from Block 175 "
            "(parameters UNCHANGED, no fitting) over the SAME fixed "
            "out-of-sample windows RC1 used, with the RC1 leader's status as "
            "the question, not the assumption. "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It unlocked "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc2_cross_policy_replay_approval",
        "label": "Crypto-D1 V2 RC2 Cross-Policy Replay Approval",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the human approved the RC2 replay, the Block 185 "
            "runner persisted the simulated cross-policy report over the fixed "
            "Block 184 windows with RP1..RP6 parameters UNCHANGED, and the "
            "Block 186 read-only results review scored it. No real order was "
            "placed; DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It "
            "unlocked nothing: real_data_qa and baseline_backtest stay BLOCKED "
            "and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc2_cross_policy_evidence_decision",
        "label": "Crypto-D1 V2 RC2 Cross-Policy Evidence Decision",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 187 read-only human evidence decision "
            "contract recorded the human's judgment over the RC2 cross-policy "
            "evidence: the RC1 leader's out-of-sample failure acknowledged, "
            "the strongest candidates (RP4/RP5) kept as evidence only -- NOT "
            "selected successors -- decision kept at "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET, and the selected research "
            "direction is RC3 failure-mode characterization. It unlocked "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc3_failure_mode_characterization_research_approval",
        "label": "Crypto-D1 V2 RC3 Failure-Mode Characterization Research Approval",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the human approved RC3 and the Block 188 read-only "
            "failure-mode characterization ran purely descriptively over the "
            "persisted RC1/RC2 evidence, with no recompute. It explained why "
            "the RC1 leader failed out of sample while simpler re-entry rules "
            "held up, kept RP4/RP5 as evidence only (NOT selected successors), "
            "and preserved DO_NOT_PROMOTE_RESUME_POLICY_YET. It unlocked "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_rc3_findings_decision",
        "label": "Crypto-D1 V2 RC3 Findings Decision",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 189 read-only human decision contract "
            "recorded the human's judgment over the RC3 findings: the "
            "resume-policy research thread is closed with lessons, fresh "
            "evidence is required before any reconsideration, no successors "
            "were selected (RP4/RP5 stay evidence only), and "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It unlocked "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_await_new_human_research_directive",
        "label": "Crypto-D1 V2 Awaiting New Human Research Directive",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the awaited human research directive arrived: the "
            "human directed the Block 190 fresh-evidence validation design, "
            "which froze the evidence criteria before any qualifying data "
            "exists. The resume-policy thread stays closed with lessons, no "
            "successors were selected, and "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It unlocked "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "crypto_d1_await_fresh_evidence_accrual",
        "label": "Crypto-D1 V2 Awaiting Fresh Evidence Accrual",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the Block 190 fresh-evidence wait is registered and "
            "continues in the background: the criteria are FROZEN before any "
            "qualifying data exists, post-2026-06-08 manually staged daily "
            "candles only (no fetch ever), minimum window 180 days, 365 "
            "preferred. Frozen pass bars (ALL must pass): return > 0, worst "
            "drawdown not worse than -35%, Sharpe >= 0.8, and top-half "
            "stability versus all six fixed candidates, with one look per "
            "window. Passing PROMOTES NOTHING: it only qualifies a candidate "
            "for a separate future human reconsideration decision, with "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET preserved. It unlocked nothing: "
            "real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "strategy_factory_roadmap_human_review",
        "label": "Strategy Factory Roadmap Human Review",
        "state": STATE_NEXT,
        "reason": (
            "Next required action: " + NEXT_REQUIRED_ACTION + ". The Strategy "
            "Factory Automation Roadmap links L1-L6 are COMPLETE as read-only "
            "designs, live on remote: L1 intake-to-orchestrator adapter (idea "
            "triage to an in-memory proposal), L2 unsigned lane-aware "
            "approval packet schema, L3 batch approval (one human signature "
            "per fully enumerated chain; deviation voids the batch), L4 "
            "research cycle scheduler SPEC only (no scheduler built), L5 "
            "result notification payloads only (nothing sent), and L6 "
            "dashboard/JARVIS sync display model only (no runtime UI edit). "
            "The automated research paperwork/control chain is complete; "
            "trading remains LOCKED. Future pending blocks, each needing its "
            "own separate human approval: (1) real dashboard/JARVIS wiring, "
            "(2) a manual-start notification transport, (3) the actual "
            "scheduler build under the L4 rules, and (4) an umbrella Strategy "
            "Research Orchestrator. Fresh-evidence accrual for Crypto-D1 "
            "continues in the background under the frozen Block 190 bars. "
            "This row is NOT a build step and NOT an authorization -- not "
            "promotion and not trading execution; it acquires no data, runs "
            "no dry run, QA, baseline, backtest, simulation, replay, scanner, "
            "or optimization, places no order, automates nothing, sends "
            "nothing, and writes no runtime/registry/dashboard artifact; "
            "DO_NOT_PROMOTE_RESUME_POLICY_YET stays preserved. It unlocks "
            "nothing: real_data_qa and baseline_backtest stay BLOCKED and the "
            "paper/micro-live/live gates stay LOCKED unless a separate, "
            "future, human-approved contract authorizes a crossing."
        ),
    },
    {
        "id": "arbitrage_factory_v1_lane_chain",
        "label": "Arbitrage Factory V1 Lane Contract Chain (Seq 0-5)",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the second research lane's full paper chain is built, "
            "reviewed, and ACCEPTED: seq 0 readiness (alerts/reports only, "
            "execution absent by construction, no exchange credentials ever), "
            "seq 1 scanner SPEC (frozen IO, refuse-by-default, per-run human "
            "approval), seq 2 data contract (operator-staged shapes; "
            "account/credential/position fields refused), seq 3 fee/slippage "
            "model (honest net edge; costs never default to zero; "
            "PASS/WATCH/FAIL readiness never a trade signal), seq 4 "
            "alert/report schema (verdicts must agree with the model; net "
            "edge must match the cost breakdown; mandatory disclaimer), and "
            "seq 5 lane review (all 12 coherence checks pass). It unlocked "
            "nothing: the scanner build stays BLOCKED as its own future "
            "human-approved block, real_data_qa and baseline_backtest stay "
            "BLOCKED, and the paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "arbitrage_factory_v1_scanner_build",
        "label": "Arbitrage Factory V1 Scanner Build",
        "state": STATE_COMPLETE,
        "reason": (
            "Complete - the scanner is built under the frozen seq-1 spec, "
            "gated on the seq 0-5 lane review, refuse-by-default. Its first "
            "dry scan (write=False) honestly produced FAIL/FAIL: today's "
            "micro-edges die under the full conservative cost stack, every "
            "alert is research-only with the mandatory disclaimer, and no "
            "report was written. It unlocked nothing: every run still needs "
            "its own per-run human approval, execution is absent from the "
            "lane by construction, and the paper/micro-live/live gates stay "
            "LOCKED."
        ),
    },
    {
        "id": "arbitrage_factory_v1_scanner_run",
        "label": "Arbitrage Factory V1 Scanner Run (Per-Run Approval)",
        "state": STATE_BLOCKED,
        "reason": (
            "Blocked - every scanner run requires its own per-run human "
            "approval; no scheduler exists and none may. This row is NOT a "
            "build step and NOT an authorization -- it acquires no data, "
            "runs no scan, places no order, automates nothing, and writes "
            "nothing. It unlocks nothing: the paper/micro-live/live gates "
            "stay LOCKED."
        ),
    },
    {
        "id": "arbitrage_factory_v1_persisted_report",
        "label": "Arbitrage Factory V1 First Persisted Report",
        "state": STATE_BLOCKED,
        "reason": (
            "Blocked - reports/arbitrage_factory_v1/ does not exist; the "
            "first persisted report pair stays behind an explicit "
            "RUN_ARBITRAGE_SCAN_WITH_REPORT approval (one report per "
            "approved run, exclusive-create, never overwritten, alerts "
            "only with the mandatory research-only disclaimer). Staged CSVs "
            "remain untracked operational data. It unlocks nothing: the "
            "paper/micro-live/live gates stay LOCKED."
        ),
    },
    {
        "id": "human_controlled_real_data_qa_boundary_decision",
        "label": "Human-Controlled Real Data QA Boundary Decision",
        "state": STATE_BLOCKED,
        "reason": (
            "Blocked - this is a separate, later human-controlled decision and "
            "is NOT the active next step while the resume-policy results review "
            "is pending. It is a human judgment about whether to ever cross from "
            "research-only paper work into real-data QA. It is NOT a build step "
            "and NOT an authorization -- it acquires no data, runs no dry run, QA, "
            "baseline, or backtest, places no order, automates nothing, and writes "
            "no runtime/registry/dashboard artifact. real_data_qa stays BLOCKED "
            "unless a separate, future, human-approved boundary contract "
            "authorizes it."
        ),
    },
    {
        "id": "real_data_qa",
        "label": "Real Data QA",
        "state": STATE_BLOCKED,
        "reason": "Blocked - no real data acquired; QA never run.",
    },
    {
        "id": "baseline_backtest",
        "label": "Baseline Backtest",
        "state": STATE_BLOCKED,
        "reason": "Blocked - depends on real data + passed QA; never run.",
    },
    {
        "id": "paper_trading_gate",
        "label": "Paper Trading Gate",
        "state": STATE_LOCKED,
        "reason": "Locked - human approval required; never automated.",
    },
    {
        "id": "micro_live_gate",
        "label": "Micro-Live Gate",
        "state": STATE_LOCKED,
        "reason": "Locked - never automated; explicit human action only.",
    },
)

# --- blocked / locked downstream gates -------------------------------------

_BLOCKED_GATES: tuple[dict[str, str], ...] = (
    {
        "id": "real_strategy_intake",
        "label": "Real Strategy Intake",
        "state": STATE_BLOCKED,
        "reason": "Not started; requires explicit human approval.",
    },
    {
        "id": "real_data_qa",
        "label": "Real Data QA",
        "state": STATE_BLOCKED,
        "reason": (
            "Manual CSV QA produced PASS evidence (BTC/ETH/SOL); gate stays "
            "BLOCKED pending a separate human baseline-prep policy decision."
        ),
    },
    {
        "id": "baseline_backtest",
        "label": "Baseline Backtest",
        "state": STATE_BLOCKED,
        "reason": "Depends on real data and a passed QA verdict; never run.",
    },
    {
        "id": "paper_trading_gate",
        "label": "Paper Trading Gate",
        "state": STATE_LOCKED,
        "reason": "Human approval required before any paper trading.",
    },
    {
        "id": "micro_live_gate",
        "label": "Micro-Live Gate",
        "state": STATE_LOCKED,
        "reason": "Never automated; explicit human action only.",
    },
)

# Real-world capabilities that no stage in this map unlocks.
_SAFETY_FLAGS: dict[str, bool] = {
    "real_data": False,
    "qa": False,
    "baseline": False,
    "backtest": False,
    "simulation": False,
    "paper": False,
    "live": False,
    "broker": False,
    "exchange": False,
    "automation": False,
    "runtime_writes": False,
    "registry_writes": False,
    "dashboard_writes": False,
}


def _clone(rows: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    """Return a fresh, mutation-safe copy of static lane rows."""
    return [dict(row) for row in rows]


def human_workflow_lane() -> list[dict[str, str]]:
    """The human workflow lane (display-only stage list)."""
    return _clone(_HUMAN_WORKFLOW)


def machine_pipeline_lane() -> list[dict[str, str]]:
    """The machine pipeline lane (display-only stage list)."""
    return _clone(_MACHINE_PIPELINE)


def blocked_gates() -> list[dict[str, str]]:
    """Downstream gates that remain blocked or locked (display-only)."""
    return _clone(_BLOCKED_GATES)


def safety_flags() -> dict[str, bool]:
    """Real-world capability flags; all False (nothing is unlocked)."""
    return dict(_SAFETY_FLAGS)


def get_mission_flow_status() -> dict[str, Any]:
    """Deterministic, read-only mission-flow snapshot (no IO required)."""
    return {
        "mission_flow_version": MISSION_FLOW_VERSION,
        "mode": MISSION_FLOW_MODE,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "current_stage": CURRENT_STAGE,
        "latest_completed_bundle": LATEST_COMPLETED_BUNDLE,
        "latest_completed_protocol": LATEST_COMPLETED_PROTOCOL,
        "latest_completed_protocol_contract": LATEST_COMPLETED_PROTOCOL_CONTRACT,
        "latest_completed_family_selection_contract": LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT,  # noqa: E501
        "latest_completed_family_review_contract": LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_contract": LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_review_contract": LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_approval_contract": LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_research_design_contract": LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT,  # noqa: E501
        "latest_completed_research_design_review_contract": LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_design_approval_contract": LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_research_readiness_contract": LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT,  # noqa: E501
        "latest_completed_external_bot_evidence_intake_contract": LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT,  # noqa: E501
        "latest_completed_hyperliquid_whale_evidence_contract": LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_funding_rate_evidence_contract": LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_bitcoin_cycle_timing_evidence_contract": LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_research_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_review_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_approval_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_strategy_evidence_scoring_contract": LATEST_COMPLETED_STRATEGY_EVIDENCE_SCORING_CONTRACT,  # noqa: E501
        "latest_completed_strategy_candidate_ranking_contract": LATEST_COMPLETED_STRATEGY_CANDIDATE_RANKING_CONTRACT,  # noqa: E501
        "latest_completed_external_human_trader_evidence_contract": LATEST_COMPLETED_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_cohort_independence_contract": LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT,  # noqa: E501
        "latest_completed_real_data_qa_boundary_decision_contract": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT,  # noqa: E501
        "latest_completed_real_data_qa_human_approval_packet_contract": LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT,  # noqa: E501
        "latest_completed_real_data_qa_readiness_checklist_contract": LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT,  # noqa: E501
        "latest_completed_overnight_research_autopilot_controller": LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER,  # noqa: E501
        "latest_completed_real_data_qa_human_approval_packet": LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET,  # noqa: E501
        "latest_completed_real_data_qa_boundary_decision": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION,  # noqa: E501
        "latest_completed_pipeline_coverage_reconciliation": LATEST_COMPLETED_PIPELINE_COVERAGE_RECONCILIATION,  # noqa: E501
        "latest_completed_real_data_qa_boundary_readiness_review": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW,  # noqa: E501
        "latest_completed_public_spot_source_evaluation": LATEST_COMPLETED_PUBLIC_SPOT_SOURCE_EVALUATION,  # noqa: E501
        "latest_completed_concrete_spot_provider_adapter_spec": LATEST_COMPLETED_CONCRETE_SPOT_PROVIDER_ADAPTER_SPEC,  # noqa: E501
        "latest_completed_selected_spot_provider_fetch_runner_dry_run": LATEST_COMPLETED_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN,  # noqa: E501
        "latest_completed_real_data_qa_boundary_decision_packet": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_PACKET,  # noqa: E501
        "latest_completed_real_data_qa_plan_only_contract": LATEST_COMPLETED_REAL_DATA_QA_PLAN_ONLY_CONTRACT,  # noqa: E501
        "latest_completed_real_data_qa_plan_approval_decision": LATEST_COMPLETED_REAL_DATA_QA_PLAN_APPROVAL_DECISION,  # noqa: E501
        "latest_completed_real_data_qa_boundary_final_decision": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_FINAL_DECISION,  # noqa: E501
        "latest_completed_real_data_qa_pass_receipt": LATEST_COMPLETED_REAL_DATA_QA_PASS_RECEIPT,  # noqa: E501
        "latest_completed_baseline_backtest_prep_contract": LATEST_COMPLETED_BASELINE_BACKTEST_PREP_CONTRACT,  # noqa: E501
        "latest_completed_resume_policy_research_plan_contract": LATEST_COMPLETED_RESUME_POLICY_RESEARCH_PLAN_CONTRACT,  # noqa: E501
        "latest_completed_resume_policy_simulation_runner_contract": LATEST_COMPLETED_RESUME_POLICY_SIMULATION_RUNNER_CONTRACT,  # noqa: E501
        "latest_completed_resume_policy_results_review_contract": LATEST_COMPLETED_RESUME_POLICY_RESULTS_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_resume_policy_human_review_decision_contract": LATEST_COMPLETED_RESUME_POLICY_HUMAN_REVIEW_DECISION_CONTRACT,  # noqa: E501
        "latest_completed_post_resume_policy_research_continuation_plan_contract": LATEST_COMPLETED_POST_RESUME_POLICY_RESEARCH_CONTINUATION_PLAN_CONTRACT,  # noqa: E501
        "latest_completed_rc1_out_of_sample_robustness_research_contract": LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_ROBUSTNESS_RESEARCH_CONTRACT,  # noqa: E501
        "latest_completed_rc1_out_of_sample_replay_runner_contract": LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_REPLAY_RUNNER_CONTRACT,  # noqa: E501
        "latest_completed_rc1_out_of_sample_results_review_contract": LATEST_COMPLETED_RC1_OUT_OF_SAMPLE_RESULTS_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_rc1_oos_human_evidence_decision_contract": LATEST_COMPLETED_RC1_OOS_HUMAN_EVIDENCE_DECISION_CONTRACT,  # noqa: E501
        "latest_completed_rc2_cross_policy_stability_research_contract": LATEST_COMPLETED_RC2_CROSS_POLICY_STABILITY_RESEARCH_CONTRACT,  # noqa: E501
        "latest_completed_rc2_cross_policy_replay_runner_contract": LATEST_COMPLETED_RC2_CROSS_POLICY_REPLAY_RUNNER_CONTRACT,  # noqa: E501
        "latest_completed_rc2_cross_policy_results_review_contract": LATEST_COMPLETED_RC2_CROSS_POLICY_RESULTS_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_rc2_cross_policy_human_evidence_decision_contract": LATEST_COMPLETED_RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_CONTRACT,  # noqa: E501
        "latest_completed_rc3_failure_mode_characterization_research_contract": LATEST_COMPLETED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH_CONTRACT,  # noqa: E501
        "latest_completed_rc3_findings_human_decision_contract": LATEST_COMPLETED_RC3_FINDINGS_HUMAN_DECISION_CONTRACT,  # noqa: E501
        "latest_completed_fresh_evidence_validation_design_contract": LATEST_COMPLETED_FRESH_EVIDENCE_VALIDATION_DESIGN_CONTRACT,  # noqa: E501
        "latest_completed_automation_roadmap": LATEST_COMPLETED_AUTOMATION_ROADMAP,  # noqa: E501
        "latest_completed_arbitrage_lane_chain": LATEST_COMPLETED_ARBITRAGE_LANE_CHAIN,  # noqa: E501
        "latest_completed_arbitrage_scanner_build": LATEST_COMPLETED_ARBITRAGE_SCANNER_BUILD,  # noqa: E501
        "next_required_action": NEXT_REQUIRED_ACTION,
        "safety_posture": dict(MISSION_FLOW_SAFETY_POSTURE),
        "human_workflow": human_workflow_lane(),
        "machine_pipeline": machine_pipeline_lane(),
        "blocked_gates": blocked_gates(),
        "safety": safety_flags(),
    }
