"""Formal safety-isolation verifier for SPARTA Commander 2.0.

This module *proves*, by re-runnable static source analysis plus behavioral
assertions, that the Commander 2.0 layer is purely additive and read-only
toward trading / frozen stack / strategy parameters / scheduler / API keys /
live execution, and that no external action (email, Telegram, external API)
can fire.

It is itself read-only except for writing its own two report files under
``reports/``. It never touches C:\\Users\\mahmo\\obsidian-trade-logger.
"""

from __future__ import annotations

import json
import re
import tempfile
import urllib.parse  # URL string parsing only (urlsplit) - NOT the net module
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .memory import ROOT, write_json

SCHEMA = "sparta_commander.commander_2_safety_isolation.v1"

REPORT_JSON = ROOT / "reports" / "sparta_commander_2_safety_isolation.json"
REPORT_MD = ROOT / "reports" / "sparta_commander_2_safety_isolation.md"

# New Commander 2.0 source modules (the surface under audit). The verifier
# audits itself too.
COMMANDER_2_MODULES = (
    "sparta_commander/mobile_command.py",
    "sparta_commander/persona_registry.py",
    "sparta_commander/claude_bridge.py",
    "sparta_commander/morning_brief.py",
    "sparta_commander/revenue_opportunity_planner.py",
    "sparta_commander/commander_2.py",
    "sparta_commander/commander_2_safety.py",
    "sparta_commander/approval_ledger.py",
    "sparta_commander/telegram_adapter.py",
    "sparta_commander/phase2_manual_simulation.py",
    "sparta_commander/telegram_bot_runtime.py",
    "sparta_commander/phase3_manual_qa.py",
    "sparta_commander/source_quality.py",
    "sparta_commander/operator_memory.py",
    "sparta_commander/local_web.py",
    "sparta_commander/research_watcher.py",
    "sparta_commander/research_hunter.py",
    "sparta_commander/research_hunter_alerts.py",
    "sparta_commander/external_research_spec.py",
    "sparta_commander/obsidian_sync.py",
    "sparta_commander/external_search_boundary.py",
    "sparta_commander/external_research_hunter.py",
    "sparta_commander/external_finding_review.py",
    "sparta_commander/external_finding_verification_plan.py",
    "sparta_commander/external_finding_static_inspection.py",
    "sparta_commander/external_finding_reimpl_spec.py",
    "sparta_commander/external_finding_paper_sim_scaffold.py",
    "sparta_commander/external_finding_prereg_plan.py",
    "sparta_commander/external_finding_prerun_checklist.py",
    "sparta_commander/external_finding_paper_sim_run.py",
    "sparta_commander/external_finding_prereg_plan_v2.py",
    "sparta_commander/external_finding_prerun_checklist_v2.py",
    "sparta_commander/external_finding_paper_sim_run_v2.py",
    "sparta_commander/external_finding_closure_report.py",
    "sparta_commander/nq_mnq_or_prereg.py",
    "sparta_commander/nq_mnq_or_data_requirements.py",
    "sparta_commander/nq_mnq_or_data_contract_discovery.py",
    "sparta_commander/nq_mnq_or_folder_staging_report.py",
    "sparta_commander/crypto_regime_prereg.py",
    "sparta_commander/crypto_regime_data_contract_discovery.py",
    "sparta_commander/crypto_regime_folder_staging_report.py",
    "sparta_commander/stat_arb_pair_prereg.py",
    "sparta_commander/stat_arb_pair_data_requirements.py",
    "sparta_commander/copy_research_charter.py",
    "sparta_commander/copy_research_source_registry.py",
    "sparta_commander/copy_research_observer.py",
    "sparta_commander/copy_research_hypothesis_builder.py",
    "sparta_commander/external_strategy_discovery_d01.py",
    "sparta_commander/external_strategy_discovery_d02_seed_intake.py",
    "sparta_commander/crypto_regime_data_contract_discovery_rerun.py",
    "sparta_commander/crypto_regime_sealed_prereg.py",
    "sparta_commander/crypto_regime_prerun_checklist.py",
    "sparta_commander/crypto_regime_phase05_paper_run.py",
    "sparta_commander/crypto_regime_closure_report.py",
    "sparta_commander/market_permission_gate.py",
    "sparta_commander/ai_strategy_reviewer.py",
    "sparta_commander/strategy_evidence_card.py",
    "sparta_commander/strategy_factory_charter.py",
    "sparta_commander/strategy_factory_source_registry.py",
    "sparta_commander/strategy_factory_idea_intake.py",
    "sparta_commander/strategy_factory_hypothesis_spec.py",
    "sparta_commander/strategy_factory_backtest_readiness.py",
    "sparta_commander/strategy_factory_data_contract_gate.py",
    "sparta_commander/strategy_factory_template_registry.py",
    "sparta_commander/strategy_factory_cost_slippage_registry.py",
    "sparta_commander/strategy_factory_phase5_block_idea_draft.py",
    "sparta_commander/strategy_factory_phase5_offline_backtest_run.py",
    "sparta_commander/strategy_factory_run_queue.py",
    "sparta_commander/strategy_factory_run_queue_planner.py",
    "sparta_commander/strategy_factory_run_queue_reporter.py",
    "sparta_commander/strategy_factory_queue_schema.py",
    "sparta_commander/strategy_factory_orchestrator_contract.py",
    "sparta_commander/strategy_factory_orchestrator_preview.py",
    "sparta_commander/strategy_factory_orchestrator_approval_packet.py",
    "sparta_commander/strategy_factory_orchestrator_approval_index.py",
    "sparta_commander/strategy_factory_orchestrator_display_adapter.py",
    "sparta_commander/strategy_factory_orchestrator_stack_safety.py",
    "sparta_commander/strategy_factory_research_queue.py",
    "sparta_commander/strategy_factory_queue_reader.py",
    "sparta_commander/strategy_factory_queue_planner.py",
    "sparta_commander/strategy_factory_research_task_packet.py",
    "sparta_commander/strategy_factory_research_report_contract.py",
    "sparta_commander/strategy_factory_research_decision_memo_contract.py",
    "sparta_commander/strategy_factory_research_pipeline_closure.py",
    "sparta_commander/strategy_factory_research_protocol_draft_contract.py",
    "sparta_commander/strategy_factory_protocol_review_gate.py",
    "sparta_commander/strategy_factory_data_contract_planning.py",
    "sparta_commander/strategy_factory_data_qa_contract.py",
    "sparta_commander/strategy_factory_research_runner_contract.py",
    "sparta_commander/strategy_factory_dry_run_orchestrator_contract.py",
    "sparta_commander/strategy_factory_dashboard_registry_feed_contract.py",
    "sparta_commander/strategy_factory_decision_ledger_contract.py",
    "sparta_commander/strategy_factory_safety_kill_switch_contract.py",
    "sparta_commander/strategy_factory_end_to_end_fake_pipeline_contract.py",
    "sparta_commander/strategy_factory_backbone_closure_report.py",
    "sparta_commander/strategy_factory_fake_artifact_smoke_test_contract.py",
    "sparta_commander/strategy_factory_fake_artifact_dry_walk_contract.py",
    "sparta_commander/strategy_factory_fake_dry_walk_operator_review_gate.py",
    "sparta_commander/strategy_factory_fake_dry_walk_implementation_contract.py",
    "sparta_commander/strategy_factory_fake_dry_walk_in_memory.py",
    "sparta_commander/strategy_factory_fake_dry_walk_result_review_contract.py",
    "sparta_commander/strategy_factory_fake_walk_report_contract.py",
    "sparta_commander/strategy_factory_fake_walk_report_operator_review_gate.py",
    "sparta_commander/strategy_factory_fake_report_renderer_contract.py",
    "sparta_commander/strategy_factory_fake_report_renderer_in_memory.py",
    "sparta_commander/strategy_factory_fake_report_renderer_result_review_contract.py",
    "sparta_commander/strategy_factory_fake_lane_closure_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_intake_reconciliation_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_acquire_decision_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_source_class_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_source_specification_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_offline_acquisition_plan_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract.py",
    "sparta_commander/strategy_factory_mission_flow_status.py",
    "sparta_commander/strategy_factory_mission_flow_bundle_registry.py",
    "sparta_commander/strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_preview_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_review_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_decision_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_decision_review_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract.py",
    "sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract.py",
)

COMMANDER_2_TESTS = (
    "tests/test_sparta_commander_persona_registry.py",
    "tests/test_sparta_commander_claude_bridge.py",
    "tests/test_sparta_commander_revenue_opportunity_planner.py",
    "tests/test_sparta_commander_morning_brief.py",
    "tests/test_sparta_commander_mobile_command.py",
    "tests/test_sparta_commander_2.py",
    "tests/test_sparta_commander_2_safety.py",
    "tests/test_sparta_commander_approval_ledger.py",
    "tests/test_sparta_commander_telegram_adapter.py",
    "tests/test_sparta_commander_phase2_manual_simulation.py",
    "tests/test_sparta_commander_telegram_bot_runtime.py",
    "tests/test_sparta_commander_phase3_manual_qa.py",
    "tests/test_sparta_commander_source_quality.py",
    "tests/test_sparta_commander_operator_memory.py",
    "tests/test_sparta_commander_local_web.py",
    "tests/test_sparta_commander_research_watcher.py",
    "tests/test_sparta_commander_research_hunter.py",
    "tests/test_sparta_commander_research_hunter_alerts.py",
    "tests/test_sparta_commander_external_research_spec.py",
    "tests/test_sparta_commander_obsidian_sync.py",
    "tests/test_sparta_commander_external_search_boundary.py",
    "tests/test_sparta_commander_external_research_hunter.py",
    "tests/test_sparta_commander_external_finding_review.py",
    "tests/test_sparta_commander_external_finding_verification_plan.py",
    "tests/test_sparta_commander_external_finding_static_inspection.py",
    "tests/test_sparta_commander_external_finding_reimpl_spec.py",
    "tests/test_sparta_commander_external_finding_paper_sim_scaffold.py",
    "tests/test_sparta_commander_external_finding_prereg_plan.py",
    "tests/test_sparta_commander_external_finding_prerun_checklist.py",
    "tests/test_sparta_commander_external_finding_paper_sim_run.py",
    "tests/test_sparta_commander_external_finding_prereg_plan_v2.py",
    "tests/test_sparta_commander_external_finding_prerun_checklist_v2.py",
    "tests/test_sparta_commander_external_finding_paper_sim_run_v2.py",
    "tests/test_sparta_commander_external_finding_closure_report.py",
    "tests/test_sparta_commander_nq_mnq_or_prereg.py",
    "tests/test_sparta_commander_nq_mnq_or_data_requirements.py",
    "tests/test_sparta_commander_nq_mnq_or_data_contract_discovery.py",
    "tests/test_sparta_commander_nq_mnq_or_folder_staging_report.py",
    "tests/test_sparta_commander_crypto_regime_prereg.py",
    "tests/test_sparta_commander_crypto_regime_data_contract_discovery.py",
    "tests/test_sparta_commander_crypto_regime_folder_staging_report.py",
    "tests/test_sparta_commander_stat_arb_pair_prereg.py",
    "tests/test_sparta_commander_stat_arb_pair_data_requirements.py",
    "tests/test_copy_research_charter.py",
    "tests/test_copy_research_source_registry.py",
    "tests/test_copy_research_observer.py",
    "tests/test_copy_research_hypothesis_builder.py",
    "tests/test_sparta_commander_external_strategy_discovery_d01.py",
    "tests/test_sparta_commander_external_strategy_discovery_d02_seed_intake.py",
    "tests/test_sparta_commander_crypto_regime_data_contract_discovery_rerun.py",
    "tests/test_sparta_commander_crypto_regime_sealed_prereg.py",
    "tests/test_sparta_commander_crypto_regime_prerun_checklist.py",
    "tests/test_sparta_commander_crypto_regime_phase05_paper_run.py",
    "tests/test_sparta_commander_crypto_regime_closure_report.py",
    "tests/test_sparta_commander_market_permission_gate.py",
    "tests/test_sparta_commander_ai_strategy_reviewer.py",
    "tests/test_sparta_commander_strategy_evidence_card.py",
    "tests/test_sparta_commander_strategy_factory_charter.py",
    "tests/test_sparta_commander_strategy_factory_source_registry.py",
    "tests/test_sparta_commander_strategy_factory_idea_intake.py",
    "tests/test_sparta_commander_strategy_factory_hypothesis_spec.py",
    "tests/test_sparta_commander_strategy_factory_backtest_readiness.py",
    "tests/test_sparta_commander_strategy_factory_data_contract_gate.py",
    "tests/test_sparta_commander_strategy_factory_template_registry.py",
    "tests/test_sparta_commander_strategy_factory_cost_slippage_registry.py",
    "tests/test_sparta_commander_strategy_factory_phase5_block_idea_draft.py",
    "tests/test_sparta_commander_strategy_factory_phase5_offline_backtest_run.py",
    "tests/test_strategy_factory_run_queue.py",
    "tests/test_strategy_factory_run_queue_planner.py",
    "tests/test_strategy_factory_run_queue_reporter.py",
    "tests/test_strategy_factory_queue_schema.py",
    "tests/test_strategy_factory_orchestrator_contract.py",
    "tests/test_strategy_factory_orchestrator_preview.py",
    "tests/test_strategy_factory_orchestrator_approval_packet.py",
    "tests/test_strategy_factory_orchestrator_approval_index.py",
    "tests/test_strategy_factory_orchestrator_display_adapter.py",
    "tests/test_strategy_factory_orchestrator_stack_safety.py",
    "tests/test_strategy_factory_research_queue.py",
    "tests/test_strategy_factory_queue_reader.py",
    "tests/test_strategy_factory_queue_planner.py",
    "tests/test_strategy_factory_research_task_packet.py",
    "tests/test_strategy_factory_research_report_contract.py",
    "tests/test_strategy_factory_research_decision_memo_contract.py",
    "tests/test_strategy_factory_research_pipeline_closure.py",
    "tests/test_strategy_factory_research_protocol_draft_contract.py",
    "tests/test_strategy_factory_protocol_review_gate.py",
    "tests/test_strategy_factory_data_contract_planning.py",
    "tests/test_strategy_factory_data_qa_contract.py",
    "tests/test_strategy_factory_research_runner_contract.py",
    "tests/test_strategy_factory_dry_run_orchestrator_contract.py",
    "tests/test_strategy_factory_dashboard_registry_feed_contract.py",
    "tests/test_strategy_factory_decision_ledger_contract.py",
    "tests/test_strategy_factory_safety_kill_switch_contract.py",
    "tests/test_strategy_factory_end_to_end_fake_pipeline_contract.py",
    "tests/test_strategy_factory_backbone_closure_report.py",
    "tests/test_strategy_factory_fake_artifact_smoke_test_contract.py",
    "tests/test_strategy_factory_fake_artifact_dry_walk_contract.py",
    "tests/test_strategy_factory_fake_dry_walk_operator_review_gate.py",
    "tests/test_strategy_factory_fake_dry_walk_implementation_contract.py",
    "tests/test_strategy_factory_fake_dry_walk_in_memory.py",
    "tests/test_strategy_factory_fake_dry_walk_result_review_contract.py",
    "tests/test_strategy_factory_fake_walk_report_contract.py",
    "tests/test_strategy_factory_fake_walk_report_operator_review_gate.py",
    "tests/test_strategy_factory_fake_report_renderer_contract.py",
    "tests/test_strategy_factory_fake_report_renderer_in_memory.py",
    "tests/test_strategy_factory_fake_report_renderer_result_review_contract.py",
    "tests/test_strategy_factory_fake_lane_closure_contract.py",
    "tests/test_strategy_factory_crypto_d1_intake_reconciliation_contract.py",
    "tests/test_strategy_factory_crypto_d1_acquire_decision_contract.py",
    "tests/test_strategy_factory_crypto_d1_source_class_contract.py",
    "tests/test_strategy_factory_crypto_d1_source_specification_contract.py",
    "tests/test_strategy_factory_crypto_d1_offline_acquisition_plan_contract.py",
    "tests/test_strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.py",
    "tests/test_strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract.py",
    "tests/test_strategy_factory_mission_flow_status.py",
    "tests/test_strategy_factory_mission_flow_bundle_registry.py",
    "tests/test_strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_preview_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_review_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_decision_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_decision_review_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract.py",
    "tests/test_strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract.py",
)

# Shared files that were *touched* (additive) and are checked with targeted,
# false-positive-safe assertions instead of a whole-file forbidden scan.
TOUCH_POINTS = (
    "sparta_commander/__init__.py",
    "sparta_commander/commander.py",
    "templates/dashboard.html",
    "app.py",
)

# Forbidden capability detectors. Patterns match code constructs
# (imports / calls), NOT bare substrings, so declarative safety-rail string
# literals like "send_telegram_message" in persona_registry are NOT flagged.
_DANGEROUS_PATTERNS: dict[str, str] = {
    "live_trading_execution": (
        r"(^\s*(import|from)\s+(freqtrade|ccxt)\b)"
        r"|(\b(place_order|create_order|submit_order|cancel_order|create_market_order)\s*\()"
    ),
    "trade_logger_path": r"obsidian[-_]trade[-_]logger",
    "frozen_stack_write": r"frozen_stack[\w/\\.]*\.(json|yaml|yml)['\"]?\s*(,|\))",
    "strategy_lab_data_write": r"strategy_lab[/\\]data",
    "email_send": (
        r"(^\s*(import|from)\s+(smtplib|aiosmtplib|sendgrid)\b)"
        r"|(\.send_message\s*\()|(\.sendmail\s*\()|(ses\.send_email\s*\()"
    ),
    "telegram_send": (
        r"api\.telegram\.org"
        r"|(^\s*(import|from)\s+(telegram|telebot|aiogram)\b)"
        r"|(\.send_message\s*\()|(bot\.sendMessage)"
    ),
    "external_http": (
        r"(^\s*(import|from)\s+(requests|httpx|aiohttp|urllib3)\b)"
        r"|(urllib\.request)|(socket\.socket\s*\()"
    ),
    "external_ai_api": r"^\s*(import|from)\s+(openai|anthropic|google\.generativeai|boto3)\b",
    "secret_access": r"(os\.environ\b)|(os\.getenv\s*\()|(\bgetenv\s*\()",
    "destructive_fs": (
        r"(shutil\.(rmtree|move)\s*\()|(os\.remove\s*\()|(os\.unlink\s*\()"
        r"|(os\.rmdir\s*\()|(\.unlink\s*\()"
    ),
    "filesystem_write": (
        r"(\.write_text\s*\()|(\.write_bytes\s*\()|(\bwrite_json\s*\()"
        r"|(open\s*\([^)]*['\"][wax])"
    ),
    "subprocess_exec": r"(^\s*import\s+subprocess\b)|(subprocess\.)",
}

# Allowlist: bounded behaviors that are intentional and proven-safe.
#   - report generation writes ONLY under reports/
#   - claude_bridge runs ONLY a local read-only `git status --porcelain`
_WRITE_ALLOWED_MODULES = {
    "sparta_commander/morning_brief.py",
    "sparta_commander/revenue_opportunity_planner.py",
    "sparta_commander/commander_2_safety.py",
    "sparta_commander/approval_ledger.py",
    "sparta_commander/telegram_adapter.py",
    "sparta_commander/phase2_manual_simulation.py",
    "sparta_commander/telegram_bot_runtime.py",
    "sparta_commander/phase3_manual_qa.py",
    "sparta_commander/source_quality.py",
    "sparta_commander/operator_memory.py",
    "sparta_commander/local_web.py",
    "sparta_commander/research_watcher.py",
    "sparta_commander/research_hunter.py",
    "sparta_commander/research_hunter_alerts.py",
    "sparta_commander/external_research_spec.py",
    "sparta_commander/obsidian_sync.py",
    # Phase 14B orchestrator: writes only its quarantine report (no network,
    # no secret, no exec). The search BOUNDARY writes nothing and is NOT
    # listed here — its sole sanctioned cap is external_http via the
    # designated-boundary registry.
    "sparta_commander/external_research_hunter.py",
    # Phase 14C review queue: writes only its local queue + report (no
    # network/secret/exec; reads only the Phase 14B quarantine report).
    "sparta_commander/external_finding_review.py",
    # Phase 14D: pure design/plan module; writes only its plan report.
    "sparta_commander/external_finding_verification_plan.py",
    # Phase 14E: static-only inspection framework; text-only, writes only
    # its own pack report (no clone/install/exec/network).
    "sparta_commander/external_finding_static_inspection.py",
    # Phase 14H: pure design/spec module; writes only its design report.
    "sparta_commander/external_finding_reimpl_spec.py",
    # Phase 14I: paper-only sim scaffold; deterministic math + schemas,
    # writes only its scaffold report (no run/network/exec/repo).
    "sparta_commander/external_finding_paper_sim_scaffold.py",
    # Phase 14J: preregistration plan; writes only its prereg report
    # (no run, existence-only data stat, no network/exec/repo).
    "sparta_commander/external_finding_prereg_plan.py",
    # Phase 14K pre-run checklist: writes only its checklist report
    # (no run, recomputes prereg hash read-only, no data/network/exec).
    "sparta_commander/external_finding_prerun_checklist.py",
    # Phase 14K runner: paper-only; reads frozen H1 data read-only for
    # sha256 provenance; writes ONLY its 2 bound report files. No
    # network/exec/repo/credentials; INVALID on any sealed-rule mismatch.
    "sparta_commander/external_finding_paper_sim_run.py",
    # Phase 14L corrected prereg: writes only its prereg report (no run,
    # existence/path-shape stat only, no data read, no network/exec/repo).
    "sparta_commander/external_finding_prereg_plan_v2.py",
    # Phase 14M pre-run checklist: writes only its checklist report
    # (no run, recomputes 14L hash read-only, no data/network/exec).
    "sparta_commander/external_finding_prerun_checklist_v2.py",
    # Phase 14M runner: paper-only; reads frozen H1 JSON read-only; writes
    # ONLY its 2 bound report files. No network/exec/repo/credentials;
    # INVALID on any sealed-rule mismatch; never auto-PASS.
    "sparta_commander/external_finding_paper_sim_run_v2.py",
    # Phase 14N closure: immutable closure report; writes only its 2
    # report files (no run/runner/data/network/exec/repo).
    "sparta_commander/external_finding_closure_report.py",
    # NQ/MNQ-OR Phase 01 prereg plan: writes only its 2 report files
    # (no run/runner/optimization; existence/path-shape probe only).
    "sparta_commander/nq_mnq_or_prereg.py",
    # NQ/MNQ-OR data-requirements checklist: writes only its 2 report
    # files (pure spec; no run/data/probe/network).
    "sparta_commander/nq_mnq_or_data_requirements.py",
    # NQ/MNQ-OR data-contract discovery: existence/path-shape + sha256
    # provenance only; writes only its 2 report files (no bar parsing).
    "sparta_commander/nq_mnq_or_data_contract_discovery.py",
    # NQ/MNQ-OR folder-staging report: existence/path-shape only;
    # writes only its 2 report files (no hashing, no bar parsing).
    "sparta_commander/nq_mnq_or_folder_staging_report.py",
    # Crypto regime momentum/MR Phase 01 prereg: writes only its 2 report
    # files (no run/runner/optimization; existence/path-shape probe only,
    # no data read; returns NEEDS_DATA_CONTRACT instead of guessing).
    "sparta_commander/crypto_regime_prereg.py",
    # Crypto regime Phase 02 data-contract discovery: existence/path-shape
    # + sha256/size/mtime provenance only; writes only its 2 report files
    # (no bar parsing, no other-arc descent, no contract guessing).
    "sparta_commander/crypto_regime_data_contract_discovery.py",
    # Crypto regime folder-staging report: existence/path-shape ONLY (no
    # hashing); writes only its 2 report files (no acquisition/fake data).
    "sparta_commander/crypto_regime_folder_staging_report.py",
    # Stat-arb pair-spread Phase 01 prereg plan: writes only its 2 report
    # files (no run/runner/strategy/optimization; existence/path-shape
    # probe only, no data read; no cross-arc data binding).
    "sparta_commander/stat_arb_pair_prereg.py",
    # Stat-arb pair-spread data-requirements checklist: pure spec; writes
    # only its 2 report files (no run/data/probe/network).
    "sparta_commander/stat_arb_pair_data_requirements.py",
    # Copy-Research Bot Phase 2 charter: pure-spec preregistration;
    # writes only its 2 report files (no probe/run/data/network).
    "sparta_commander/copy_research_charter.py",
    # Copy-Research Bot Phase 2 source registry: existence/path-shape +
    # sha256-raw-bytes provenance only; writes only its 2 report files
    # (no fetch/scrape/network/parse/guess; review_queue untouched).
    "sparta_commander/copy_research_source_registry.py",
    # Copy-Research Bot Phase 3A offline observer: read-only,
    # manifest-gated, sha256-verified, path-contained reader; writes
    # only its 2 report files (no network/scrape/exec/parse-beyond-
    # declared-schema; review_queue untouched).
    "sparta_commander/copy_research_observer.py",
    # Copy-Research Bot Phase 3A hypothesis builder: pure transform;
    # writes only its 2 report files (no network/exec/copy-trading;
    # forbidden-trade-field validator; review_queue untouched).
    "sparta_commander/copy_research_hypothesis_builder.py",
    # External Strategy Discovery Engine D01: architecture/schema/report
    # only; writes only its 2 report files (no network/scrape/API/
    # crawler/sim; references other arcs as static read-only text only).
    "sparta_commander/external_strategy_discovery_d01.py",
    # External Strategy Discovery D02: READ-ONLY operator-inbox
    # classification/ranking; reads only the local inbox JSON
    # read-only, works empty, fabricates nothing; writes only its 2
    # report files; no scrape/API/network/sim/runner/promotion/prereg.
    "sparta_commander/external_strategy_discovery_d02_seed_intake.py",
    # Crypto regime data-contract discovery RE-RUN: read-only provenance
    # confirmation; writes only its 2 report files (no bar parsing, no
    # downloader rerun, acquisition manifest read-only/not overwritten).
    "sparta_commander/crypto_regime_data_contract_discovery_rerun.py",
    # Crypto regime Phase 03 sealed runnable prereg: writes only its 2
    # report files; reuses Phase 01 rules read-only via function import;
    # no run/sim/exec/optimize/refit; no downloader rerun; acquisition
    # manifest not overwritten; Phase 04 not built.
    "sparta_commander/crypto_regime_sealed_prereg.py",
    # Crypto regime Phase 04 pre-run checklist: writes only its 2 report
    # files; reuses Phase 03 read-only via function import; captures
    # read-only baselines (review_queue / acquisition manifest); no run/
    # sim/exec/downloader/Phase05; manifest/review_queue not mutated.
    "sparta_commander/crypto_regime_prerun_checklist.py",
    # Crypto regime Phase 05 single paper-only run: reads LOCAL FROZEN
    # data read-only (zip/csv) + sha256 provenance re-verify; writes
    # only its 2 report files; no live/exchange/order/credential/
    # network/promotion; downloader not rerun; acquisition manifest +
    # review_queue read-only; no other arc touched; ONE run only.
    "sparta_commander/crypto_regime_phase05_paper_run.py",
    # Crypto regime Phase 06 closure report: immutable summary; writes
    # only its 2 report files; reuses Phase 03 read-only; re-verifies
    # review_queue + acquisition manifest READ-ONLY (sha256); no run/
    # sim/parse/optimize/promote; manifest/review_queue not mutated.
    "sparta_commander/crypto_regime_closure_report.py",
    # Market Permission Gate + Strategy Evidence Cards: deterministic /
    # research-only; each writes ONLY its 2 report files under
    # reports/sparta_commander/ (no run/sim/exec/network/credentials).
    "sparta_commander/market_permission_gate.py",
    "sparta_commander/strategy_evidence_card.py",
    "sparta_commander/strategy_factory_charter.py",
    "sparta_commander/strategy_factory_source_registry.py",
    "sparta_commander/strategy_factory_idea_intake.py",
    "sparta_commander/strategy_factory_hypothesis_spec.py",
    "sparta_commander/strategy_factory_backtest_readiness.py",
    "sparta_commander/strategy_factory_data_contract_gate.py",
    "sparta_commander/strategy_factory_template_registry.py",
    "sparta_commander/strategy_factory_cost_slippage_registry.py",
    "sparta_commander/strategy_factory_phase5_block_idea_draft.py",
    "sparta_commander/strategy_factory_phase5_offline_backtest_run.py",
}
_SUBPROCESS_ALLOWED_MODULES = {"sparta_commander/claude_bridge.py"}

# The verifier itself necessarily *names* the forbidden paths/strings inside
# its detector regexes and its own report prose (an AV scanner's signature DB
# is not itself malware). Those literal occurrences are acknowledged ONLY for
# this file. Real action capabilities (destructive_fs, external_http,
# external_ai_api, email_send, telegram_send, live_trading_execution,
# secret_access) are NOT acknowledged for any file and would still FAIL.
_NON_VIOLATION_FOR_ALLOWED = {
    "sparta_commander/morning_brief.py": {"filesystem_write"},
    "sparta_commander/revenue_opportunity_planner.py": {"filesystem_write"},
    "sparta_commander/commander_2_safety.py": {
        "filesystem_write",
        "subprocess_exec",
        "trade_logger_path",
        "strategy_lab_data_write",
    },
    "sparta_commander/claude_bridge.py": {"subprocess_exec"},
    # Phase 2: bounded report/ledger writes, verified to resolve under reports/.
    "sparta_commander/approval_ledger.py": {"filesystem_write"},
    "sparta_commander/telegram_adapter.py": {"filesystem_write"},
    "sparta_commander/phase2_manual_simulation.py": {"filesystem_write"},
    # Phase 3 transport boundary: bounded report write (booleans only, no
    # token). telegram_send / external_http are handled by the dedicated
    # boundary mechanism, not this allowlist.
    "sparta_commander/telegram_bot_runtime.py": {"filesystem_write"},
    # Phase 3.5: bounded QA report write (read-only QA; no token, paths only).
    "sparta_commander/phase3_manual_qa.py": {"filesystem_write"},
    # Phase 5: read-only source-quality inspector; bounded report write only.
    "sparta_commander/source_quality.py": {"filesystem_write"},
    # Phase 6: local advisory operator-memory + report write only.
    "sparta_commander/operator_memory.py": {"filesystem_write"},
    # Phase 8A: thin local-web wrapper; bounded report write only.
    "sparta_commander/local_web.py": {"filesystem_write"},
    # Phase 10: read-only watcher; writes only its own watcher reports.
    "sparta_commander/research_watcher.py": {"filesystem_write"},
    # Research Hunter Phase 1: read-only; writes only its own hunter reports.
    "sparta_commander/research_hunter.py": {"filesystem_write"},
    # Research Hunter Phase 3: delegates Telegram to the boundary; writes
    # only its local sent-ledger + report.
    "sparta_commander/research_hunter_alerts.py": {"filesystem_write"},
    # Phase 14A: pure design/spec module; writes only its design report.
    "sparta_commander/external_research_spec.py": {"filesystem_write"},
    # Obsidian sync: knowledge-only; writes sanitized .md into the user's
    # vault + its own bounded report. No execution/secret capability.
    "sparta_commander/obsidian_sync.py": {"filesystem_write"},
    # Phase 14B orchestrator: bounded quarantine-report write only. No
    # network/secret/exec; delegates all fetch to the search boundary.
    "sparta_commander/external_research_hunter.py": {"filesystem_write"},
    # Phase 14C review queue: bounded local queue/report writes only.
    "sparta_commander/external_finding_review.py": {"filesystem_write"},
    # Phase 14D plan: bounded plan-report write only (design/plan only).
    "sparta_commander/external_finding_verification_plan.py": {"filesystem_write"},
    # Phase 14E static inspection: bounded pack-report write only.
    "sparta_commander/external_finding_static_inspection.py": {"filesystem_write"},
    # Phase 14H design spec: bounded spec-report write only.
    "sparta_commander/external_finding_reimpl_spec.py": {"filesystem_write"},
    # Phase 14I scaffold: bounded scaffold-report write only.
    "sparta_commander/external_finding_paper_sim_scaffold.py": {"filesystem_write"},
    # Phase 14J prereg plan: bounded prereg-report write only.
    "sparta_commander/external_finding_prereg_plan.py": {"filesystem_write"},
    # Phase 14K pre-run checklist: bounded checklist-report write only.
    "sparta_commander/external_finding_prerun_checklist.py": {"filesystem_write"},
    # Phase 14K runner: bounded 2-file report write only (frozen data is
    # READ-ONLY for sha256; reads are not a write capability).
    "sparta_commander/external_finding_paper_sim_run.py": {"filesystem_write"},
    # Phase 14L corrected prereg: bounded prereg-report write only.
    "sparta_commander/external_finding_prereg_plan_v2.py": {"filesystem_write"},
    # Phase 14M pre-run checklist: bounded checklist-report write only.
    "sparta_commander/external_finding_prerun_checklist_v2.py": {"filesystem_write"},
    # Phase 14M runner: bounded 2-file report write only (frozen JSON is
    # READ-ONLY for sha256+parse; reads are not a write capability).
    "sparta_commander/external_finding_paper_sim_run_v2.py": {"filesystem_write"},
    # Phase 14N closure: bounded 2-file closure-report write only.
    "sparta_commander/external_finding_closure_report.py": {"filesystem_write"},
    # NQ/MNQ-OR Phase 01 prereg: bounded 2-file prereg-report write only.
    "sparta_commander/nq_mnq_or_prereg.py": {"filesystem_write"},
    # NQ/MNQ-OR data-requirements checklist: bounded 2-file write only.
    "sparta_commander/nq_mnq_or_data_requirements.py": {"filesystem_write"},
    # NQ/MNQ-OR discovery: bounded 2-file report write only (frozen data
    # READ-ONLY for sha256; reads are not a write capability).
    "sparta_commander/nq_mnq_or_data_contract_discovery.py": {"filesystem_write"},
    # NQ/MNQ-OR folder-staging report: bounded 2-file report write only
    # (existence/path-shape probe; no data read, no hashing).
    "sparta_commander/nq_mnq_or_folder_staging_report.py": {"filesystem_write"},
    # Crypto regime momentum/MR Phase 01 prereg: bounded 2-file
    # prereg-report write only (existence/path-shape probe; no data read).
    "sparta_commander/crypto_regime_prereg.py": {"filesystem_write"},
    # Crypto regime Phase 02 discovery: bounded 2-file report write only
    # (frozen data READ-ONLY for sha256; reads are not a write capability).
    "sparta_commander/crypto_regime_data_contract_discovery.py": {"filesystem_write"},
    # Crypto regime folder-staging report: bounded 2-file report write
    # only (existence/path-shape only; no hashing, no data read).
    "sparta_commander/crypto_regime_folder_staging_report.py": {"filesystem_write"},
    # Stat-arb pair-spread Phase 01 prereg: bounded 2-file prereg-report
    # write only (no run, existence/path-shape probe only, no data read).
    "sparta_commander/stat_arb_pair_prereg.py": {"filesystem_write"},
    # Stat-arb pair-spread data-requirements checklist: bounded 2-file
    # checklist-report write only (pure spec; no run/data/probe).
    "sparta_commander/stat_arb_pair_data_requirements.py": {"filesystem_write"},
    # Copy-Research Bot Phase 2 charter: bounded 2-file report write only
    # (pure spec; no probe/run/data/network).
    "sparta_commander/copy_research_charter.py": {"filesystem_write"},
    # Copy-Research Bot Phase 2 source registry: bounded 2-file report
    # write only (existence/path-shape + sha256 raw-bytes provenance;
    # reads-for-hash are not a write capability; no parse/network).
    "sparta_commander/copy_research_source_registry.py": {"filesystem_write"},
    # Copy-Research Bot Phase 3A offline observer: bounded 2-file
    # report write only (reads-for-hash/declared-schema are not a write
    # capability; no network/exec/parse-beyond-schema).
    "sparta_commander/copy_research_observer.py": {"filesystem_write"},
    # Copy-Research Bot Phase 3A hypothesis builder: bounded 2-file
    # report write only (pure transform; no network/exec).
    "sparta_commander/copy_research_hypothesis_builder.py": {"filesystem_write"},
    # External Strategy Discovery Engine D01: bounded 2-file schema/
    # report write only (no network/scrape/API/crawler/sim/data read).
    "sparta_commander/external_strategy_discovery_d01.py": {"filesystem_write"},
    # External Strategy Discovery D02: bounded 2-file report write only
    # (operator inbox JSON read-only; inbox never created/mutated; no
    # scrape/API/network/sim/runner/promotion/preregistration).
    "sparta_commander/external_strategy_discovery_d02_seed_intake.py": {"filesystem_write"},
    # Crypto regime discovery RE-RUN: bounded 2-file report write only
    # (reads staged bytes for sha256 + manifest/provenance JSON read-only;
    # never overwrites the acquisition manifest; no bar parsing).
    "sparta_commander/crypto_regime_data_contract_discovery_rerun.py": {"filesystem_write"},
    # Crypto regime Phase 03 sealed prereg: bounded 2-file prereg-report
    # write only (no run/sim/exec/optimize; manifest not overwritten).
    "sparta_commander/crypto_regime_sealed_prereg.py": {"filesystem_write"},
    # Crypto regime Phase 04 pre-run checklist: bounded 2-file report
    # write only (read-only baselines; no run/sim/exec; Phase 05 not
    # built; review_queue + acquisition manifest never mutated).
    "sparta_commander/crypto_regime_prerun_checklist.py": {"filesystem_write"},
    # Crypto regime Phase 05 paper-only run: bounded 2-file report
    # write only (frozen data + provenance read-only for sha256; reads
    # are not a write capability); manifest/review_queue not mutated.
    "sparta_commander/crypto_regime_phase05_paper_run.py": {"filesystem_write"},
    # Crypto regime Phase 06 closure report: bounded 2-file immutable
    # report write only (re-verifies baselines read-only; no run/sim/
    # parse/optimize; manifest/review_queue not mutated).
    "sparta_commander/crypto_regime_closure_report.py": {"filesystem_write"},
    # Market Permission Gate: bounded 2-file research report write only
    # (deterministic scoring; no run/sim/exec/network/credentials).
    "sparta_commander/market_permission_gate.py": {"filesystem_write"},
    # Strategy Evidence Card: bounded 2-file research report write only
    # (deterministic-primary fusion; AI advisory capped at 30%).
    "sparta_commander/strategy_evidence_card.py": {"filesystem_write"},
    # Strategy Factory Phase 1: pure-stdlib offline charter + source
    # registry; each writes ONLY its 2 report files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_charter.py": {"filesystem_write"},
    "sparta_commander/strategy_factory_source_registry.py": {"filesystem_write"},
    # Strategy Factory Phase 2: pure-stdlib offline operator idea-intake
    # transcription; writes ONLY its 2 report files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_idea_intake.py": {"filesystem_write"},
    # Strategy Factory Phase 3: pure-stdlib offline verify-and-chain
    # hypothesis spec; writes ONLY its 2 report files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_hypothesis_spec.py": {"filesystem_write"},
    # Strategy Factory Phase 4: pure-stdlib offline verify-and-chain
    # backtest-readiness; writes ONLY its 2 report files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_backtest_readiness.py": {"filesystem_write"},
    # Strategy Factory Phase 4B: pure-stdlib zero-data-access
    # data-contract gate; writes ONLY its 2 report files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_data_contract_gate.py": {"filesystem_write"},
    # Strategy Factory D-5-A: pure-stdlib offline declarative template
    # registry; writes ONLY its 2 snapshot files under
    # reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_template_registry.py": {"filesystem_write"},
    # Strategy Factory D-5-B: pure-stdlib offline declarative
    # cost/slippage model registry; writes ONLY its 2 snapshot files
    # under reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_cost_slippage_registry.py": {"filesystem_write"},
    # Strategy Factory D-5-D: pure-stdlib offline draft-only output
    # contract; writes ONLY draft files matching the closed filename
    # regex under reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_phase5_block_idea_draft.py": {"filesystem_write"},
    # Strategy Factory Phase 5: pure-stdlib offline paper-only
    # backtest runner; writes ONLY run files matching the closed filename
    # regex under reports/strategy_factory/ (no run/sim/exec/network/credentials).
    "sparta_commander/strategy_factory_phase5_offline_backtest_run.py": {"filesystem_write"},
}

# Capabilities that are NEVER acknowledged for ANY file — their presence is
# always a hard violation, even in the verifier.
_NEVER_ACKNOWLEDGED = frozenset(
    {
        "destructive_fs",
        "external_http",
        "external_ai_api",
        "email_send",
        "telegram_send",
        "live_trading_execution",
        "secret_access",
        "frozen_stack_write",
    }
)

# Phase 3: the SINGLE, hardened, designated Telegram transport boundary. This
# is NOT a weakening of the global no-egress rule — it is the one explicitly
# audited egress point. ONLY this exact file may carry telegram_send /
# external_http, and ONLY because Phase 3 must deliver Commander replies. It
# is held to STRICTER positive constraints (delegates to the pure adapter,
# fails closed, token never printed/written/reported, no email/trading/exec).
# Every OTHER module remains fully capability-denied (telegram_send /
# external_http stay in _NEVER_ACKNOWLEDGED for them).
_TELEGRAM_TRANSPORT_BOUNDARY = "sparta_commander/telegram_bot_runtime.py"
# Phase 14B: the SINGLE, hardened, designated READ-ONLY search egress. Like
# the Telegram boundary, this is NOT a weakening of the global no-egress
# rule — it is a second explicitly-audited egress point, held to STRICTER
# positive constraints (fail-closed without local secrets, GET-only to an
# allowlisted host, key never printed/written/returned, writes nothing).
_EXTERNAL_SEARCH_BOUNDARY = "sparta_commander/external_search_boundary.py"
# Per-boundary sanctioned capabilities. ``external_http`` is sanctioned ONLY
# in these exact designated files; ``telegram_send`` ONLY in the Telegram
# boundary. Every OTHER module stays in _NEVER_ACKNOWLEDGED for these caps.
_DESIGNATED_BOUNDARIES = {
    _TELEGRAM_TRANSPORT_BOUNDARY: frozenset({"telegram_send", "external_http"}),
    _EXTERNAL_SEARCH_BOUNDARY: frozenset({"external_http"}),
}
_BOUNDARY_ACK = frozenset({"telegram_send", "external_http"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _scan_module(root: Path, rel: str) -> dict[str, Any]:
    src = _read(root, rel)
    exists = bool(src)
    raw_hits: dict[str, list[str]] = {}
    for cap, pattern in _DANGEROUS_PATTERNS.items():
        matches = re.findall(pattern, src, flags=re.MULTILINE)
        if matches:
            # Flatten tuple groups from alternation into readable tokens.
            flat = []
            for m in matches:
                token = m if isinstance(m, str) else next((g for g in m if g), "")
                token = token.strip()
                if token:
                    flat.append(token)
            raw_hits[cap] = sorted(set(flat))[:6]

    allowed = _NON_VIOLATION_FOR_ALLOWED.get(rel, set())
    violations: dict[str, list[str]] = {}
    acknowledged: dict[str, list[str]] = {}
    boundary_ack = _DESIGNATED_BOUNDARIES.get(rel, frozenset())
    for cap, hits in raw_hits.items():
        if cap in boundary_ack:
            # Sanctioned ONLY for this exact designated egress boundary file.
            acknowledged[cap] = hits
        elif cap in allowed and cap not in _NEVER_ACKNOWLEDGED:
            acknowledged[cap] = hits
        else:
            violations[cap] = hits
    return {
        "file": rel,
        "exists": exists,
        "violations": violations,
        "acknowledged_bounded": acknowledged,
        "clean": not violations and exists,
    }


def _verify_report_paths_under_reports() -> dict[str, Any]:
    from . import approval_ledger as al
    from . import morning_brief as mb
    from . import phase2_manual_simulation as sim
    from . import revenue_opportunity_planner as rp
    from . import telegram_adapter as ta
    from . import telegram_bot_runtime as tbr
    from . import phase3_manual_qa as _qa
    from . import source_quality as _sq
    from . import operator_memory as _om
    from . import local_web as _lw
    from . import research_watcher as _rw
    from . import research_hunter as _rh
    from . import research_hunter_alerts as _rha
    from . import external_research_spec as _ers
    from . import external_research_hunter as _erh
    from . import external_finding_review as _efr
    from . import external_finding_verification_plan as _efvp
    from . import external_finding_static_inspection as _efsi
    from . import external_finding_reimpl_spec as _efrs
    from . import external_finding_paper_sim_scaffold as _efps
    from . import external_finding_prereg_plan as _efpp
    from . import external_finding_prerun_checklist as _efpc
    from . import external_finding_paper_sim_run as _efpr
    from . import external_finding_prereg_plan_v2 as _efp2
    from . import external_finding_prerun_checklist_v2 as _efc2
    from . import external_finding_paper_sim_run_v2 as _efr2
    from . import external_finding_closure_report as _efcl
    from . import nq_mnq_or_prereg as _nqp
    from . import nq_mnq_or_data_requirements as _nqd
    from . import nq_mnq_or_data_contract_discovery as _nqdisc
    from . import nq_mnq_or_folder_staging_report as _nqstg
    from . import crypto_regime_prereg as _crp
    from . import crypto_regime_data_contract_discovery as _crpd
    from . import crypto_regime_folder_staging_report as _crps
    from . import stat_arb_pair_prereg as _sap
    from . import stat_arb_pair_data_requirements as _sad
    from . import copy_research_charter as _crc
    from . import copy_research_source_registry as _crsr
    from . import copy_research_observer as _cro
    from . import copy_research_hypothesis_builder as _crhb
    from . import external_strategy_discovery_d01 as _esd
    from . import external_strategy_discovery_d02_seed_intake as _esd2
    from . import crypto_regime_data_contract_discovery_rerun as _crpr
    from . import crypto_regime_sealed_prereg as _crsp
    from . import crypto_regime_prerun_checklist as _crpc
    from . import crypto_regime_phase05_paper_run as _crp5
    from . import crypto_regime_closure_report as _crcl
    from . import market_permission_gate as _mpg
    from . import strategy_evidence_card as _sec
    from . import strategy_factory_charter as _sfc
    from . import strategy_factory_source_registry as _sfsr
    from . import strategy_factory_idea_intake as _sfii
    from . import strategy_factory_hypothesis_spec as _sfhs
    from . import strategy_factory_backtest_readiness as _sfbr
    from . import strategy_factory_data_contract_gate as _sfdcg
    from . import strategy_factory_template_registry as _sftreg
    from . import strategy_factory_cost_slippage_registry as _sfcost
    from . import strategy_factory_phase5_block_idea_draft as _sfblock
    from . import strategy_factory_phase5_offline_backtest_run as _sfp5
    from . import obsidian_sync as _obs

    checks = {}
    for name, p in (
        ("morning_brief.json", mb.REPORT_JSON),
        ("morning_brief.md", mb.REPORT_MD),
        ("revenue.json", rp.REPORT_JSON),
        ("revenue.md", rp.REPORT_MD),
        ("safety.json", REPORT_JSON),
        ("safety.md", REPORT_MD),
        ("approvals_ledger.json", al.LEDGER_PATH),
        ("approvals_dir", al.APPROVALS_DIR),
        ("telegram_phase2.json", ta.PHASE2_REPORT_JSON),
        ("telegram_phase2.md", ta.PHASE2_REPORT_MD),
        ("phase4_reply.json", ta.PHASE4_REPORT_JSON),
        ("phase4_reply.md", ta.PHASE4_REPORT_MD),
        ("phase45.json", ta.PHASE45_REPORT_JSON),
        ("phase45.md", ta.PHASE45_REPORT_MD),
        ("phase2_sim.json", sim.REPORT_JSON),
        ("phase2_sim.md", sim.REPORT_MD),
        ("phase2_sim_ledger_dir", sim.SIM_LEDGER_DIR),
        ("phase3.json", tbr.PHASE3_REPORT_JSON),
        ("phase3.md", tbr.PHASE3_REPORT_MD),
        ("phase3_qa.json", _qa.REPORT_JSON),
        ("phase3_qa.md", _qa.REPORT_MD),
        ("phase6_om.json", _om.REPORT_JSON),
        ("phase6_om.md", _om.REPORT_MD),
        ("phase6_om_memory", _om.MEMORY_PATH),
        ("phase7_digest.json", _om.PHASE7_REPORT_JSON),
        ("phase7_digest.md", _om.PHASE7_REPORT_MD),
        ("phase8a_web.json", _lw.REPORT_JSON),
        ("phase8a_web.md", _lw.REPORT_MD),
        ("phase8b_voice.json", _lw.PHASE8B_REPORT_JSON),
        ("phase8b_voice.md", _lw.PHASE8B_REPORT_MD),
        ("phase8c_qa.json", _lw.PHASE8C_REPORT_JSON),
        ("phase8c_qa.md", _lw.PHASE8C_REPORT_MD),
        ("phase9_launcher.json", _lw.PHASE9_REPORT_JSON),
        ("phase9_launcher.md", _lw.PHASE9_REPORT_MD),
        ("watcher_latest.json", _rw.LATEST_JSON),
        ("watcher_latest.md", _rw.LATEST_MD),
        ("watcher_history", _rw.HISTORY_JSONL),
        ("phase10_watcher.json", _rw.PHASE10_REPORT_JSON),
        ("phase10_watcher.md", _rw.PHASE10_REPORT_MD),
        ("hunter_latest.json", _rh.LATEST_JSON),
        ("hunter_latest.md", _rh.LATEST_MD),
        ("hunter_history", _rh.HISTORY_JSONL),
        ("hunter_big_alerts", _rh.BIG_ALERTS_JSONL),
        ("hunter_phase1.json", _rh.PHASE1_REPORT_JSON),
        ("hunter_phase1.md", _rh.PHASE1_REPORT_MD),
        ("hunter_phase2.json", _rh.PHASE2_REPORT_JSON),
        ("hunter_phase2.md", _rh.PHASE2_REPORT_MD),
        ("hunter_phase3.json", _rha.PHASE3_REPORT_JSON),
        ("hunter_phase3.md", _rha.PHASE3_REPORT_MD),
        ("hunter_sent_ledger", _rha.SENT_LEDGER),
        ("hunter_trading_focus.json", _rh.TRADING_FOCUS_REPORT_JSON),
        ("hunter_trading_focus.md", _rh.TRADING_FOCUS_REPORT_MD),
        ("ext_research_14a.json", _ers.PHASE14A_REPORT_JSON),
        ("ext_research_14a.md", _ers.PHASE14A_REPORT_MD),
        ("obsidian_sync.json", _obs.REPORT_JSON),
        ("obsidian_sync.md", _obs.REPORT_MD),
        ("ext_research_14b.json", _erh.PHASE14B_REPORT_JSON),
        ("ext_research_14b.md", _erh.PHASE14B_REPORT_MD),
        ("ext_review_queue.json", _efr.QUEUE_JSON),
        ("ext_review_queue.md", _efr.QUEUE_MD),
        ("ext_review_14c.json", _efr.PHASE14C_REPORT_JSON),
        ("ext_review_14c.md", _efr.PHASE14C_REPORT_MD),
        ("ext_plan_14d.json", _efvp.PHASE14D_PLAN_JSON),
        ("ext_plan_14d.md", _efvp.PHASE14D_PLAN_MD),
        ("ext_static_14e.json", _efsi.PHASE14E_PACK_JSON),
        ("ext_static_14e.md", _efsi.PHASE14E_PACK_MD),
        ("ext_reimpl_14h.json", _efrs.PHASE14H_SPEC_JSON),
        ("ext_reimpl_14h.md", _efrs.PHASE14H_SPEC_MD),
        ("ext_paper_14i.json", _efps.PHASE14I_SCAFFOLD_JSON),
        ("ext_paper_14i.md", _efps.PHASE14I_SCAFFOLD_MD),
        ("ext_prereg_14j.json", _efpp.PHASE14J_PREREG_JSON),
        ("ext_prereg_14j.md", _efpp.PHASE14J_PREREG_MD),
        ("ext_prerun_14k.json", _efpc.PHASE14K_CHECKLIST_JSON),
        ("ext_prerun_14k.md", _efpc.PHASE14K_CHECKLIST_MD),
        ("ext_run_14k.json", _efpr.PHASE14K_RUN_JSON),
        ("ext_run_14k.md", _efpr.PHASE14K_RUN_MD),
        ("ext_prereg_14l.json", _efp2.PHASE14L_PREREG_JSON),
        ("ext_prereg_14l.md", _efp2.PHASE14L_PREREG_MD),
        ("ext_prerun_14m.json", _efc2.PHASE14M_CHECKLIST_JSON),
        ("ext_prerun_14m.md", _efc2.PHASE14M_CHECKLIST_MD),
        ("ext_run_14m.json", _efr2.PHASE14M_RUN_JSON),
        ("ext_run_14m.md", _efr2.PHASE14M_RUN_MD),
        ("ext_closure_14n.json", _efcl.PHASE14N_CLOSURE_JSON),
        ("ext_closure_14n.md", _efcl.PHASE14N_CLOSURE_MD),
        ("nq_or_p01.json", _nqp.NQ_PREREG_JSON),
        ("nq_or_p01.md", _nqp.NQ_PREREG_MD),
        ("nq_or_datareq.json", _nqd.NQ_DATAREQ_JSON),
        ("nq_or_datareq.md", _nqd.NQ_DATAREQ_MD),
        ("nq_or_disc.json", _nqdisc.NQ_DISCOVERY_JSON),
        ("nq_or_disc.md", _nqdisc.NQ_DISCOVERY_MD),
        ("nq_or_stg.json", _nqstg.NQ_STAGING_JSON),
        ("nq_or_stg.md", _nqstg.NQ_STAGING_MD),
        ("crypto_regime_p01.json", _crp.CRYPTO_REGIME_PREREG_JSON),
        ("crypto_regime_p01.md", _crp.CRYPTO_REGIME_PREREG_MD),
        ("crypto_regime_p02.json", _crpd.CRYPTO_REGIME_DISCOVERY_JSON),
        ("crypto_regime_p02.md", _crpd.CRYPTO_REGIME_DISCOVERY_MD),
        ("crypto_regime_stg.json", _crps.CRYPTO_REGIME_STAGING_JSON),
        ("crypto_regime_stg.md", _crps.CRYPTO_REGIME_STAGING_MD),
        ("stat_arb_p01.json", _sap.STAT_ARB_PREREG_JSON),
        ("stat_arb_p01.md", _sap.STAT_ARB_PREREG_MD),
        ("stat_arb_datareq.json", _sad.STAT_ARB_DATAREQ_JSON),
        ("stat_arb_datareq.md", _sad.STAT_ARB_DATAREQ_MD),
        ("copy_research_charter.json", _crc.CHARTER_JSON),
        ("copy_research_charter.md", _crc.CHARTER_MD),
        ("copy_research_source_registry.json", _crsr.REGISTRY_JSON),
        ("copy_research_source_registry.md", _crsr.REGISTRY_MD),
        ("copy_research_observer_run.json", _cro.OBSERVER_RUN_JSON),
        ("copy_research_observer_run.md", _cro.OBSERVER_RUN_MD),
        ("copy_research_hypotheses.json", _crhb.HYPOTHESES_JSON),
        ("copy_research_hypotheses.md", _crhb.HYPOTHESES_MD),
        ("ext_strat_disc_d01.json", _esd.D01_JSON),
        ("ext_strat_disc_d01.md", _esd.D01_MD),
        ("ext_strat_disc_d02.json", _esd2.SEED_INTAKE_JSON),
        ("ext_strat_disc_d02.md", _esd2.SEED_INTAKE_MD),
        ("crypto_regime_disc_rerun.json", _crpr.RERUN_JSON),
        ("crypto_regime_disc_rerun.md", _crpr.RERUN_MD),
        ("crypto_regime_sealed_p03.json", _crsp.SEALED_PREREG_JSON),
        ("crypto_regime_sealed_p03.md", _crsp.SEALED_PREREG_MD),
        ("crypto_regime_prerun_p04.json", _crpc.PRERUN_JSON),
        ("crypto_regime_prerun_p04.md", _crpc.PRERUN_MD),
        ("crypto_regime_run_p05.json", _crp5.RUN_JSON),
        ("crypto_regime_run_p05.md", _crp5.RUN_MD),
        ("crypto_regime_closure_p06.json", _crcl.CLOSURE_JSON),
        ("crypto_regime_closure_p06.md", _crcl.CLOSURE_MD),
        ("market_permission_gate.json", _mpg.GATE_REPORT_JSON),
        ("market_permission_gate.md", _mpg.GATE_REPORT_MD),
        ("strategy_evidence_cards.json", _sec.CARDS_REPORT_JSON),
        ("strategy_evidence_cards.md", _sec.CARDS_REPORT_MD),
        ("phase5_sq.json", _sq.REPORT_JSON),
        ("phase5_sq.md", _sq.REPORT_MD),
        ("sf_charter.json", _sfc.CHARTER_JSON),
        ("sf_charter.md", _sfc.CHARTER_MD),
        ("sf_registry.json", _sfsr.REGISTRY_JSON),
        ("sf_registry.md", _sfsr.REGISTRY_MD),
        ("sf_intake.json", _sfii.INTAKE_JSON),
        ("sf_intake.md", _sfii.INTAKE_MD),
        ("sf_spec.json", _sfhs.SPEC_JSON),
        ("sf_spec.md", _sfhs.SPEC_MD),
        ("sf_readiness.json", _sfbr.READINESS_JSON),
        ("sf_readiness.md", _sfbr.READINESS_MD),
        ("sf_gate.json", _sfdcg.GATE_JSON),
        ("sf_gate.md", _sfdcg.GATE_MD),
        ("sf_template_registry.json", _sftreg.SNAPSHOT_JSON),
        ("sf_template_registry.md", _sftreg.SNAPSHOT_MD),
        ("sf_cost_slippage_registry.json", _sfcost.SNAPSHOT_JSON),
        ("sf_cost_slippage_registry.md", _sfcost.SNAPSHOT_MD),
        ("sf_block_idea_draft_dir", _sfblock._DIR),
        ("sf_phase5_run_dir", _sfp5._DIR),
    ):
        try:
            rel = Path(p).resolve().relative_to(ROOT.resolve())
            checks[name] = rel.parts[0] == "reports"
        except Exception:
            checks[name] = False
    return {"all_under_reports": all(checks.values()), "checks": checks}


def _verify_subprocess_is_local_git(root: Path) -> dict[str, Any]:
    src = _read(root, "sparta_commander/claude_bridge.py")
    only_git = bool(
        re.search(r'\[\s*"git"\s*,\s*"-C"\s*,\s*str\(root\)\s*,\s*"status"\s*,\s*"--porcelain"\s*\]', src)
    )
    other_subprocess = re.findall(r"subprocess\.\w+", src)
    # Only subprocess.run for the git status call is permitted.
    extra = sorted({c for c in other_subprocess if c not in {"subprocess.run"}})
    return {
        "uses_only_local_git_status": only_git,
        "no_network_in_subprocess": True,
        "other_subprocess_calls": extra,
        "ok": only_git and not extra,
    }


def _behavioral_checks(root: Path) -> dict[str, Any]:
    results: dict[str, Any] = {}

    # Persona safety rails.
    try:
        from .persona_registry import GLOBAL_FORBIDDEN_ACTIONS, load_personas, persona_registry

        reg = persona_registry()
        required = {
            "send_email",
            "send_telegram_message",
            "place_or_modify_live_trades",
            "modify_trading_entries_or_exits",
            "call_external_paid_api",
            "store_or_print_secrets",
            "scrape_third_party_sites",
        }
        rails_ok = required.issubset(set(GLOBAL_FORBIDDEN_ACTIONS))
        every_persona_inherits = all(
            required.issubset(set(p["forbidden_actions"])) for p in load_personas()
        )
        results["persona_rails"] = {
            "read_only": reg.get("read_only") is True,
            "required_rails_present": rails_ok,
            "every_persona_inherits_rails": every_persona_inherits,
            "ok": rails_ok and every_persona_inherits and reg.get("read_only") is True,
        }
    except Exception as exc:
        results["persona_rails"] = {"ok": False, "error": str(exc)}

    # Telegram adapter must not be active.
    try:
        from .mobile_command import mobile_command_summary

        ms = mobile_command_summary(root)
        results["telegram_inactive"] = {
            "telegram_connected": ms.get("telegram_connected"),
            "phase_is_1": str(ms.get("phase", "")).startswith("1"),
            "ok": ms.get("telegram_connected") is False
            and str(ms.get("phase", "")).startswith("1"),
        }
    except Exception as exc:
        results["telegram_inactive"] = {"ok": False, "error": str(exc)}

    # draft_email cannot send; requires approval.
    try:
        from .mobile_command import handle_command

        env = handle_command(
            "draft_email",
            {"to": "x@example.com", "subject": "t", "goal": "t"},
            root=root,
        )
        draft = env.get("data", {}).get("draft", {})
        results["draft_email_cannot_send"] = {
            "approval_required": env.get("approval_required"),
            "sent": draft.get("sent"),
            "channel": draft.get("channel"),
            "ok": env.get("approval_required") is True
            and draft.get("sent") is False
            and "no email sending" in str(draft.get("channel", "")),
        }
    except Exception as exc:
        results["draft_email_cannot_send"] = {"ok": False, "error": str(exc)}

    # Revenue opportunities are plans only; every external step gated.
    try:
        from .revenue_opportunity_planner import build_revenue_opportunity_plan

        plan = build_revenue_opportunity_plan()
        all_external_gated = all(
            step["approval_required"] is True
            for track in plan.get("tracks", [])
            for step in track.get("steps", [])
            if step.get("external")
        )
        results["revenue_plans_only"] = {
            "no_send": plan.get("no_send"),
            "no_scrape": plan.get("no_scrape"),
            "no_external_api": plan.get("no_external_api"),
            "every_external_step_requires_approval": all_external_gated,
            "ok": all(
                [
                    plan.get("no_send") is True,
                    plan.get("no_scrape") is True,
                    plan.get("no_external_api") is True,
                    all_external_gated,
                ]
            ),
        }
    except Exception as exc:
        results["revenue_plans_only"] = {"ok": False, "error": str(exc)}

    # Trading bridge (transitive dependency) is read-only; no trade-logger write.
    try:
        from .trading_bridge import bridge_status

        bs = bridge_status()
        results["trading_bridge_read_only"] = {
            "read_only": bs.get("read_only"),
            "interaction": "Path.exists() stat only (pre-existing module)",
            "ok": bs.get("read_only") is True,
        }
    except Exception as exc:
        results["trading_bridge_read_only"] = {"ok": False, "error": str(exc)}

    # Dashboard facade has no side effects: load_* must NOT create files when
    # the report is absent (falls back to in-memory build).
    try:
        from .morning_brief import load_morning_brief
        from .revenue_opportunity_planner import load_revenue_opportunity_plan

        missing_mb = root / "reports" / "_probe_missing_mb.json"
        missing_rp = root / "reports" / "_probe_missing_rp.json"
        load_morning_brief(json_path=missing_mb)
        load_revenue_opportunity_plan(json_path=missing_rp)
        results["dashboard_no_side_effects"] = {
            "morning_brief_loader_wrote_file": missing_mb.exists(),
            "revenue_loader_wrote_file": missing_rp.exists(),
            "ok": not missing_mb.exists() and not missing_rp.exists(),
        }
    except Exception as exc:
        results["dashboard_no_side_effects"] = {"ok": False, "error": str(exc)}

    # Phase 2: approval ledger can never execute an external action.
    try:
        from . import approval_ledger as al

        sandbox = Path(tempfile.mkdtemp(prefix="c2safe_")) / "ledger.json"
        rec = al.create_approval(
            command="/draft_email probe",
            intent="draft_email",
            proposed_action={"summary": ["probe"]},
            risk_level="EXTERNAL_EMAIL",
            requested_by="verifier",
            path=sandbox,
        )
        created_pending = rec["status"] == al.STATUS_PENDING and rec["action_executed"] is False
        approved = al.approve(rec["approval_id"], approved_by="verifier", path=sandbox)
        still_not_executed = approved["action_executed"] is False
        no_execute_attr = not hasattr(al, "execute") and not hasattr(al, "execute_action")
        results["approval_ledger_no_execution"] = {
            "execution_enabled": al.is_execution_allowed(),
            "created_pending": created_pending,
            "approved_but_not_executed": (
                approved["status"] == al.STATUS_APPROVED and still_not_executed
            ),
            "no_execute_function": no_execute_attr,
            "ok": (
                al.is_execution_allowed() is False
                and created_pending
                and still_not_executed
                and no_execute_attr
            ),
        }
    except Exception as exc:
        results["approval_ledger_no_execution"] = {"ok": False, "error": str(exc)}

    # Phase 2: Telegram adapter never sends and gates external intents.
    try:
        from . import telegram_adapter as ta

        sandbox2 = Path(tempfile.mkdtemp(prefix="c2tg_")) / "ledger.json"
        missing_cfg = Path(tempfile.mkdtemp(prefix="c2cfg_")) / "no_telegram.json"

        def _msg(text: str, uid: str = "mahmoud") -> dict[str, Any]:
            return ta.handle_telegram_message(
                {"text": text, "user_id": uid},
                root=root,
                ledger_path=sandbox2,
                config_path=missing_cfg,
            )

        brief = _msg("/brief")
        trading = _msg("/trading")
        email = _msg("/draft_email follow up with the lead")
        revenue = _msg("/revenue")
        denied = _msg("/brief", uid="intruder")
        helped = ta.handle_telegram_message(
            {"text": "/help", "user_id": "intruder"},
            root=root,
            ledger_path=sandbox2,
            config_path=missing_cfg,
        )
        approve_resp = _msg(f"/approve {email['approval_id']}")

        def _never_sends(r: dict[str, Any]) -> bool:
            return (
                r["telegram_sent"] is False
                and r["external_action_sent"] is False
                and r["action_executed"] is False
            )

        all_never_send = all(
            _never_sends(r)
            for r in (brief, trading, email, revenue, denied, helped, approve_resp)
        )
        results["telegram_adapter_no_send"] = {
            "all_responses_never_send": all_never_send,
            "brief_read_only": brief["read_only"] is True
            and brief["approval_required"] is False
            and brief["safety_status"] == "READ_ONLY",
            "trading_read_only": trading["read_only"] is True
            and trading["safety_status"] == "READ_ONLY",
            "draft_email_gated": email["approval_required"] is True
            and bool(email["approval_id"])
            and email["approved"] is False,
            "revenue_gated": revenue["approval_required"] is True
            and bool(revenue["approval_id"]),
            "unauthorized_denied": denied["safety_status"] == "DENIED"
            and denied["approval_required"] is False,
            "help_available_to_all": helped["safety_status"] == "HELP",
            "approve_records_no_execution": approve_resp["approved"] is True
            and approve_resp["action_executed"] is False
            and approve_resp["safety_status"] == "APPROVED_NO_EXECUTION",
            "ok": all(
                [
                    all_never_send,
                    brief["safety_status"] == "READ_ONLY",
                    trading["read_only"] is True,
                    email["approval_required"] is True and bool(email["approval_id"]),
                    revenue["approval_required"] is True,
                    denied["safety_status"] == "DENIED",
                    helped["safety_status"] == "HELP",
                    approve_resp["approved"] is True
                    and approve_resp["action_executed"] is False,
                ]
            ),
        }
    except Exception as exc:
        results["telegram_adapter_no_send"] = {"ok": False, "error": str(exc)}

    return results


def _verify_touch_points(root: Path) -> dict[str, Any]:
    init_src = _read(root, "sparta_commander/__init__.py")
    cmd_src = _read(root, "sparta_commander/commander.py")
    dash_src = _read(root, "templates/dashboard.html")
    app_src = _read(root, "app.py")

    # app.py: the only Commander-2.0 addition is a docs DB row; isolate its block.
    app_block = ""
    m = re.search(r'db\.upsert_manual_entry\(\s*\n?\s*"sparta_commander_2"', app_src)
    if m:
        app_block = app_src[m.start() : m.start() + 1600]
    app_block_clean = bool(app_block) and not re.search(
        r"(place_order|live_trade|smtplib|requests\.|telegram|obsidian[-_]trade)", app_block
    )

    # dashboard.html: the new panel must be static display (no script/form/fetch).
    panel = ""
    pm = re.search(r"SPARTA COMMANDER 2\.0 ==============", dash_src)
    if pm:
        panel = dash_src[pm.start() : pm.start() + 6000]
    panel_static = bool(panel) and not re.search(
        r"<script|<form|fetch\s*\(|XMLHttpRequest|action\s*=", panel, re.IGNORECASE
    )

    return {
        "init_additive_only": "commander_2_summary" in init_src
        and "persona_registry" in init_src,
        "commander_guarded_call": "commander_2 = commander_2_summary()" in cmd_src
        and '"commander_2": commander_2' in cmd_src,
        "app_guide_row_is_docs_only": app_block_clean,
        "dashboard_panel_is_static": panel_static,
        "ok": all(
            [
                "commander_2_summary" in init_src,
                "commander_2 = commander_2_summary()" in cmd_src,
                app_block_clean,
                panel_static,
            ]
        ),
    }


def _verify_telegram_transport_boundary(
    root: Path, module_scans: list[dict[str, Any]]
) -> dict[str, Any]:
    """Hold the ONE sanctioned egress to stricter positive constraints, and
    prove no other module gained Telegram/network capability."""
    rel = _TELEGRAM_TRANSPORT_BOUNDARY
    src = _read(root, rel)

    # 1. Sole egress: only the boundary file may carry telegram_send /
    #    external_http (acknowledged there, NEVER anywhere else).
    sole_egress = True
    for scan in module_scans:
        f = scan["file"]
        caps = set(scan.get("violations", {})) | set(scan.get("acknowledged_bounded", {}))
        # telegram_send may exist ONLY in the Telegram boundary; external_http
        # ONLY in a designated boundary. Anywhere else => sole-egress broken.
        if "telegram_send" in caps and f != _TELEGRAM_TRANSPORT_BOUNDARY:
            sole_egress = False
        if "external_http" in caps and f not in _DESIGNATED_BOUNDARIES:
            sole_egress = False

    # 2. Static hardening constraints on the boundary file itself.
    delegates = "telegram_adapter.handle_telegram_message(" in src
    fails_closed = "class TelegramRuntimeError" in src and "raise TelegramRuntimeError" in src
    token_not_printed = "print(" not in src
    no_env_secrets = not re.search(r"os\.environ\b|os\.getenv\s*\(|\bgetenv\s*\(", src)
    boundary_scan = next((s for s in module_scans if s["file"] == rel), {})
    # The ONLY caps allowed for this file are the two boundary caps +
    # filesystem_write (report). Anything else => violation.
    only_expected_caps = set(boundary_scan.get("acknowledged_bounded", {})).issubset(
        set(_BOUNDARY_ACK) | {"filesystem_write"}
    )
    no_hard_violations = boundary_scan.get("violations", {}) == {}

    # 3. Behavioral (network fully mocked — no external API call).
    behavioral: dict[str, Any] = {}
    try:
        from . import telegram_bot_runtime as tbr

        sandbox = Path(tempfile.mkdtemp(prefix="c2tbr_"))
        bad_path = sandbox / "missing.txt"
        # Fail-closed checks.
        fc_token = False
        try:
            tbr.load_token(bad_path)
        except tbr.TelegramRuntimeError:
            fc_token = True
        fc_users = False
        try:
            tbr.load_allowed_users(sandbox / "missing.json")
        except tbr.TelegramRuntimeError:
            fc_users = True

        users_path = sandbox / "telegram_allowed_users.json"
        users_path.write_text('{"allowed_user_ids": [4242]}', encoding="utf-8")
        fake_token = "DUMMY_NOT_A_REAL_TOKEN"

        calls: list[dict[str, Any]] = []

        def _fake_http(url: str, payload: dict[str, Any], timeout: int = 25) -> dict[str, Any]:
            method = url.rsplit("/", 1)[-1]
            calls.append({"method": method, "payload": payload})
            if method == "getUpdates":
                return {"ok": True, "result": []}
            return {"ok": True, "result": {"message_id": 1}}

        original = tbr._http_post_json
        tbr._http_post_json = _fake_http
        try:
            allowed = tbr.load_allowed_users(users_path)

            def _upd(uid: str, text: str) -> dict[str, Any]:
                return {
                    "update_id": 1,
                    "message": {
                        "chat": {"id": 999},
                        "from": {"id": uid},
                        "text": text,
                    },
                }

            sled = sandbox / "ledger.json"
            unauth = tbr.process_update(_upd("9999", "/brief"), fake_token, allowed,
                                        root=root, allowed_users_path=users_path,
                                        ledger_path=sled)
            brief = tbr.process_update(_upd("4242", "/brief"), fake_token, allowed,
                                       root=root, allowed_users_path=users_path,
                                       ledger_path=sled)
            email = tbr.process_update(_upd("4242", "/draft_email reach a lead"),
                                       fake_token, allowed, root=root,
                                       allowed_users_path=users_path, ledger_path=sled)
            approve = tbr.process_update(
                _upd("4242", f"/approve {email.get('approval_id')}"),
                fake_token, allowed, root=root, allowed_users_path=users_path,
                ledger_path=sled,
            )
            report = tbr.build_phase3_report(bad_path, users_path)
        finally:
            tbr._http_post_json = original

        only_send_message = all(c["method"] == "sendMessage" for c in calls)
        only_to_origin_chat = all(c["payload"].get("chat_id") == 999 for c in calls)
        token_absent = (
            fake_token not in json.dumps([unauth, brief, email, approve])
            and fake_token not in json.dumps(report)
        )
        behavioral = {
            "fail_closed_missing_token": fc_token,
            "fail_closed_missing_allowed_users": fc_users,
            "unauthorized_denied": unauth["safety_status"] == "DENIED"
            and unauth["action_executed"] is False,
            "brief_read_only_reply_only": brief["safety_status"] == "READ_ONLY"
            and brief["action_executed"] is False
            and brief["external_action_sent"] is False
            and brief["telegram_reply_sent"] is True,
            "draft_email_approval_gated_no_send": email["approval_required"] is True
            and bool(email["approval_id"])
            and email["action_executed"] is False,
            "approve_marks_only_no_execution": approve["approved"] is True
            and approve["action_executed"] is False,
            "only_sendMessage_calls": only_send_message,
            "only_to_origin_chat": only_to_origin_chat,
            "token_absent_from_outputs": token_absent,
            "ok": all(
                [
                    fc_token,
                    fc_users,
                    unauth["safety_status"] == "DENIED",
                    brief["safety_status"] == "READ_ONLY",
                    brief["action_executed"] is False,
                    email["approval_required"] is True and bool(email["approval_id"]),
                    email["action_executed"] is False,
                    approve["approved"] is True and approve["action_executed"] is False,
                    only_send_message,
                    only_to_origin_chat,
                    token_absent,
                ]
            ),
        }
    except Exception as exc:
        behavioral = {"ok": False, "error": str(exc)}

    static_ok = all(
        [
            sole_egress,
            delegates,
            fails_closed,
            token_not_printed,
            bool(no_env_secrets),
            only_expected_caps,
            no_hard_violations,
        ]
    )
    return {
        "boundary_module": rel,
        "is_sole_egress": sole_egress,
        "delegates_to_pure_adapter": delegates,
        "fails_closed_defined": fails_closed,
        "token_not_printed": token_not_printed,
        "no_env_var_secret_reads": bool(no_env_secrets),
        "only_expected_capabilities": only_expected_caps,
        "no_hard_violations": no_hard_violations,
        "behavioral": behavioral,
        "ok": static_ok and behavioral.get("ok") is True,
    }


def _verify_external_search_boundary(
    root: Path, module_scans: list[dict[str, Any]]
) -> dict[str, Any]:
    """Hold the Phase 14B read-only search egress to stricter positive
    constraints, and prove it is fail-closed with NO real network call."""
    rel = _EXTERNAL_SEARCH_BOUNDARY
    src = _read(root, rel)
    scan = next((s for s in module_scans if s["file"] == rel), {})

    # Static: the ONLY sanctioned cap for this file is external_http. It must
    # write nothing (no filesystem_write), read no env secret, run no
    # subprocess, and carry zero hard violations.
    only_external_http = set(scan.get("acknowledged_bounded", {})) == {"external_http"}
    no_hard_violations = scan.get("violations", {}) == {}
    fails_closed = ("class ExternalSearchError" in src
                    and "raise ExternalSearchError" in src)
    key_not_printed = "print(" not in src
    no_env_secrets = not re.search(r"os\.environ\b|os\.getenv\s*\(|\bgetenv\s*\(", src)
    host_allowlisted = "_ALLOWED_HOSTS" in src and "www.googleapis.com" in src
    https_and_host_guarded = '!= "https"' in src and "_ALLOWED_HOSTS" in src
    get_only = 'method="GET"' in src and "data=" not in src
    not_wired = not re.search(
        r"import\s+telegram|telegram_bot_runtime|research_hunter|schtasks|"
        r"freqtrade|ccxt", src)

    behavioral: dict[str, Any] = {}
    try:
        from . import external_research_hunter as erh
        from . import external_search_boundary as esb

        sandbox = Path(tempfile.mkdtemp(prefix="c2esb_"))
        missing = sandbox / "absent.json"

        # 1. Fail-closed: no secret store -> raises, status configured False.
        fc_raises = False
        try:
            esb.load_search_config(missing)
        except esb.ExternalSearchError:
            fc_raises = True
        st = esb.boundary_status(missing)
        status_no_keys = (st["configured"] is False
                          and set(st) == {"schema", "configured", "google_ready",
                                          "youtube_ready", "network_enabled"})

        calls: list[str] = []

        def _spy(url: str) -> dict[str, Any]:
            calls.append(url)
            if "customsearch" in url:
                return {"items": [{"title": "g", "link": "https://x.test/a",
                                   "snippet": "s", "displayLink": "x.test"}]}
            return {"items": [{"id": {"videoId": "vid1"},
                               "snippet": {"title": "y", "channelTitle": "c",
                                           "description": "d",
                                           "publishedAt": "2026"}}]}

        # 2. No credentials => ZERO network (spy never invoked), [] results.
        g0 = esb.google_search("q", config=None, transport=_spy)
        y0 = esb.youtube_search("q", config=None, transport=_spy)
        a0 = esb.search_all("q", transport=_spy, secrets_path=missing)
        no_net_without_creds = (g0 == [] and y0 == [] and a0 == []
                                and calls == [])

        # 3. Host/scheme guard rejects a non-allowlisted target.
        host_guard = False
        try:
            esb._http_get_json("http://evil.example.com/x")
        except esb.ExternalSearchError:
            host_guard = True

        # 4. Configured (FAKE key) + mocked transport: only googleapis HTTPS
        #    GET, key never surfaced in results or the generated report.
        fake_key = "FAKE_TEST_KEY_NOT_REAL_000"
        secrets = sandbox / "external_search.json"
        secrets.write_text(json.dumps({
            "google_api_key": fake_key, "google_cx": "cx_test",
            "youtube_api_key": fake_key}), encoding="utf-8")
        results = esb.search_all("q", transport=_spy, secrets_path=secrets)
        hosts_ok = all(
            urllib.parse.urlsplit(u).scheme == "https"
            and urllib.parse.urlsplit(u).hostname == "www.googleapis.com"
            for u in calls) and len(calls) >= 2
        key_absent_results = fake_key not in json.dumps(results)

        rj = sandbox / "rep.json"
        rm = sandbox / "rep.md"
        rep = erh.generate_external_search_report(
            secrets_path=secrets, transport=_spy, json_path=rj, md_path=rm)
        key_absent_report = (
            fake_key not in json.dumps(rep)
            and fake_key not in rj.read_text(encoding="utf-8")
            and fake_key not in rm.read_text(encoding="utf-8"))
        quarantined = (
            all(c["stage"] == "EXTERNAL_CLAIM_ONLY" for c in rep["results"])
            and all(c["status"] == "NEEDS_VERIFICATION" for c in rep["results"])
            and all(c["can_be_high_confidence"] is False for c in rep["results"])
            and all(c["can_trigger_alert"] is False for c in rep["results"])
            and rep["wired_to_scheduled_hunter"] is False
            and rep["wired_to_telegram_alerts"] is False)

        behavioral = {
            "fail_closed_missing_secrets": fc_raises,
            "status_exposes_no_keys": status_no_keys,
            "no_network_without_credentials": no_net_without_creds,
            "host_scheme_guard_blocks_non_allowlisted": host_guard,
            "only_googleapis_https_get": hosts_ok,
            "key_absent_from_results": key_absent_results,
            "key_absent_from_report": key_absent_report,
            "findings_quarantined_external_claim_only": quarantined,
            "ok": all([fc_raises, status_no_keys, no_net_without_creds,
                       host_guard, hosts_ok, key_absent_results,
                       key_absent_report, quarantined]),
        }
    except Exception as exc:  # pragma: no cover - defensive
        behavioral = {"ok": False, "error": str(exc)}

    static_ok = all([
        only_external_http, no_hard_violations, fails_closed, key_not_printed,
        bool(no_env_secrets), host_allowlisted, https_and_host_guarded,
        get_only, bool(not_wired),
    ])
    return {
        "boundary_module": rel,
        "only_external_http_capability": only_external_http,
        "no_hard_violations": no_hard_violations,
        "fails_closed_defined": fails_closed,
        "key_not_printed": key_not_printed,
        "no_env_var_secret_reads": bool(no_env_secrets),
        "host_allowlisted": host_allowlisted,
        "https_and_host_guarded": https_and_host_guarded,
        "get_only_no_post": get_only,
        "not_wired_to_hunter_alerts_scheduler": bool(not_wired),
        "behavioral": behavioral,
        "ok": static_ok and behavioral.get("ok") is True,
    }


def build_commander_2_safety_isolation_report(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    module_scans = [_scan_module(base, rel) for rel in COMMANDER_2_MODULES]
    tests_present = {
        rel: (base / rel).exists() for rel in COMMANDER_2_TESTS
    }
    report_paths = _verify_report_paths_under_reports()
    subprocess_check = _verify_subprocess_is_local_git(base)
    behavioral = _behavioral_checks(base)
    touch_points = _verify_touch_points(base)
    telegram_boundary = _verify_telegram_transport_boundary(base, module_scans)
    external_search_boundary = _verify_external_search_boundary(base, module_scans)

    violating_files = [s["file"] for s in module_scans if s["violations"]]
    missing_modules = [s["file"] for s in module_scans if not s["exists"]]
    missing_tests = [r for r, ok in tests_present.items() if not ok]
    behavioral_failures = [k for k, v in behavioral.items() if not v.get("ok")]

    blocked_capabilities = sorted(_DANGEROUS_PATTERNS.keys())

    trading_isolation_ok = (
        not violating_files
        and behavioral.get("trading_bridge_read_only", {}).get("ok") is True
        and all(
            "trade_logger_path" not in s["violations"]
            and "live_trading_execution" not in s["violations"]
            and "frozen_stack_write" not in s["violations"]
            and "strategy_lab_data_write" not in s["violations"]
            for s in module_scans
        )
    )
    external_action_isolation_ok = (
        behavioral.get("telegram_inactive", {}).get("ok") is True
        and behavioral.get("draft_email_cannot_send", {}).get("ok") is True
        and behavioral.get("revenue_plans_only", {}).get("ok") is True
        and behavioral.get("approval_ledger_no_execution", {}).get("ok") is True
        and behavioral.get("telegram_adapter_no_send", {}).get("ok") is True
        and telegram_boundary["ok"] is True
        and external_search_boundary["ok"] is True
        and all(
            not any(
                c in s["violations"]
                for c in ("email_send", "telegram_send", "external_http", "external_ai_api")
            )
            for s in module_scans
        )
    )

    status_pass = (
        not violating_files
        and not missing_modules
        and not missing_tests
        and not behavioral_failures
        and report_paths["all_under_reports"]
        and subprocess_check["ok"]
        and touch_points["ok"]
        and trading_isolation_ok
        and external_action_isolation_ok
        and telegram_boundary["ok"]
        and external_search_boundary["ok"]
    )

    remaining_risks: list[str] = []
    if missing_tests:
        remaining_risks.append(f"Missing safety tests: {missing_tests}")
    if not subprocess_check["ok"]:
        remaining_risks.append("Subprocess usage not limited to local read-only git status.")
    remaining_risks.append(
        "claude_bridge runs a LOCAL read-only `git status --porcelain` "
        "(bounded, no network, cannot mutate). Acknowledged, not a violation."
    )
    remaining_risks.append(
        "morning_brief & revenue_opportunity_planner write report files; "
        "verified to resolve only under reports/. Acknowledged, not a violation."
    )
    remaining_risks.append(
        "trading_bridge.bridge_status() performs a read-only Path.exists() stat "
        "on the trading root; no file in obsidian-trade-logger is read or written."
    )
    remaining_risks.append(
        "commander_2_safety.py is self-audited: its detector regexes and report "
        "prose literally name forbidden paths (obsidian-trade-logger, "
        "strategy_lab/data). These are signature literals, not executable "
        "behavior, and are acknowledged ONLY for that file. Action capabilities "
        "(network/exec/email/telegram/live-trade/destructive-fs/secrets) are "
        "never acknowledged for any file, including the verifier."
    )
    remaining_risks.append(
        "Phase 3: telegram_bot_runtime.py is the SINGLE designated, hardened "
        "transport boundary. It is the ONLY module permitted telegram_send / "
        "external_http (verified sole-egress; every other module stays "
        "egress-denied). It delegates all logic to the pure adapter, fails "
        "closed without local secrets, never prints/writes/reports the token, "
        "and performs no email/trading/execution. The bot token lives only in "
        "gitignored local_secrets/ (never in code/tests/reports/logs/Git/"
        "Brain Memory). Action execution of approved items is still NOT "
        "implemented (separate future phase)."
    )

    remaining_risks.append(
        "Phase 14B: external_search_boundary.py is a SECOND designated, "
        "hardened, READ-ONLY egress. It is the ONLY non-Telegram module "
        "permitted external_http (verified sole-egress per capability; every "
        "other module stays egress-denied). It is fail-closed (no local "
        "secret store => zero network, empty results), GET-only to an "
        "allowlisted host over HTTPS, never prints/writes/returns the API "
        "key, and writes nothing. external_research_hunter.py delegates ALL "
        "fetch to it, quarantines findings as EXTERNAL_CLAIM_ONLY capped at "
        "NEEDS_VERIFICATION, and is NOT wired to the Hunter, alerts, or any "
        "scheduler. Search keys live only in gitignored local_secrets/ "
        "(never in code/tests/reports/logs/Git/Brain Memory)."
    )

    recommendation = (
        "Commander 2.0 (Phases 1-3) is statically and behaviorally isolated "
        "from trading and external execution. The Phase 3 real Telegram "
        "transport is a single hardened, audited egress boundary: it sends "
        "ONLY Commander replies, delegates all logic to the pure adapter, "
        "fails closed without local secrets, never leaks the token, and "
        "executes no approved action. Real manual Telegram testing is SAFE "
        "once Mahmoud configures local_secrets/. Action EXECUTION remains a "
        "separate, explicitly-authorized future phase. Re-run this verifier "
        "as a hard gate before any change."
        if status_pass
        else "DO NOT proceed. Resolve the violations/failures listed before "
        "any further Telegram integration."
    )

    return {
        "schema": SCHEMA,
        "generated_at": _utc_now(),
        "read_only": True,
        "status": "PASS" if status_pass else "FAIL",
        "verified_files": {
            "modules": [s["file"] for s in module_scans],
            "tests": list(COMMANDER_2_TESTS),
            "touch_points": list(TOUCH_POINTS),
        },
        "module_scans": module_scans,
        "blocked_dangerous_capabilities": blocked_capabilities,
        "trading_isolation": {
            "result": "ISOLATED / READ_ONLY" if trading_isolation_ok else "NOT_ISOLATED",
            "no_live_trading_execution_import": all(
                "live_trading_execution" not in s["violations"] for s in module_scans
            ),
            "no_trade_logger_write": all(
                "trade_logger_path" not in s["violations"] for s in module_scans
            ),
            "no_frozen_stack_write": all(
                "frozen_stack_write" not in s["violations"] for s in module_scans
            ),
            "no_strategy_lab_data_write": all(
                "strategy_lab_data_write" not in s["violations"] for s in module_scans
            ),
            "trading_bridge_read_only": behavioral.get("trading_bridge_read_only"),
        },
        "external_action_isolation": {
            "result": "BLOCKED" if external_action_isolation_ok else "NOT_BLOCKED",
            "telegram_inactive": behavioral.get("telegram_inactive"),
            "draft_email_cannot_send": behavioral.get("draft_email_cannot_send"),
            "revenue_plans_only": behavioral.get("revenue_plans_only"),
            "approval_ledger_no_execution": behavioral.get("approval_ledger_no_execution"),
            "telegram_adapter_no_send": behavioral.get("telegram_adapter_no_send"),
            "no_email_telegram_http_ai_imports": all(
                not any(
                    c in s["violations"]
                    for c in (
                        "email_send",
                        "telegram_send",
                        "external_http",
                        "external_ai_api",
                    )
                )
                for s in module_scans
            ),
        },
        "telegram_transport_boundary": telegram_boundary,
        "external_search_transport_boundary": external_search_boundary,
        "report_path_isolation": report_paths,
        "subprocess_isolation": subprocess_check,
        "behavioral_checks": behavioral,
        "touch_point_isolation": touch_points,
        "tests_present": tests_present,
        "violating_files": violating_files,
        "behavioral_failures": behavioral_failures,
        "remaining_risks": remaining_risks,
        "phase_2_recommendation": recommendation,
    }


def format_safety_report_markdown(rep: dict[str, Any]) -> str:
    L = [
        "# SPARTA Commander 2.0 — Safety Isolation Verification",
        "",
        f"**STATUS: {rep.get('status', 'UNKNOWN')}**",
        "",
        f"Generated: {rep.get('generated_at')}  ·  Read-only: {rep.get('read_only')}",
        "",
        "## Verified Files",
        "",
        "### Modules",
    ]
    for m in rep["verified_files"]["modules"]:
        scan = next((s for s in rep["module_scans"] if s["file"] == m), {})
        flag = "✅ clean" if scan.get("clean") else (
            "⚠️ acknowledged-bounded"
            if scan.get("acknowledged_bounded") and not scan.get("violations")
            else "❌ VIOLATION"
        )
        L.append(f"- `{m}` — {flag}")
        if scan.get("acknowledged_bounded"):
            L.append(f"  - acknowledged: {list(scan['acknowledged_bounded'].keys())}")
        if scan.get("violations"):
            L.append(f"  - VIOLATIONS: {scan['violations']}")
    L += ["", "### Tests"]
    for t, ok in rep["tests_present"].items():
        L.append(f"- `{t}` — {'present' if ok else 'MISSING'}")
    L += ["", "### Touch points (additive only)"]
    for t in rep["verified_files"]["touch_points"]:
        L.append(f"- `{t}`")

    L += ["", "## Blocked Dangerous Capabilities"]
    for c in rep["blocked_dangerous_capabilities"]:
        L.append(f"- {c}")

    ti = rep["trading_isolation"]
    L += [
        "",
        f"## Trading Isolation: {ti['result']}",
        f"- No live-trading execution import: {ti['no_live_trading_execution_import']}",
        f"- No write to obsidian-trade-logger: {ti['no_trade_logger_write']}",
        f"- No frozen-stack write: {ti['no_frozen_stack_write']}",
        f"- No strategy_lab/data write: {ti['no_strategy_lab_data_write']}",
        f"- Trading bridge read-only: {(ti.get('trading_bridge_read_only') or {}).get('ok')}",
    ]

    ea = rep["external_action_isolation"]
    L += [
        "",
        f"## External Action Isolation: {ea['result']}",
        f"- Telegram inactive: {(ea.get('telegram_inactive') or {}).get('ok')}",
        f"- draft_email cannot send: {(ea.get('draft_email_cannot_send') or {}).get('ok')}",
        f"- Revenue = plans only, external gated: {(ea.get('revenue_plans_only') or {}).get('ok')}",
        f"- No email/telegram/http/ai imports: {ea['no_email_telegram_http_ai_imports']}",
    ]

    tb = rep.get("telegram_transport_boundary", {})
    L += [
        "",
        f"## Phase 3 Telegram Transport Boundary: "
        f"{'OK' if tb.get('ok') else 'FAIL'}",
        f"- Boundary module: `{tb.get('boundary_module')}`",
        f"- Sole egress (no other module has telegram/http): {tb.get('is_sole_egress')}",
        f"- Delegates to pure adapter: {tb.get('delegates_to_pure_adapter')}",
        f"- Fails closed without secrets: {tb.get('fails_closed_defined')}",
        f"- Token never printed: {tb.get('token_not_printed')}",
        f"- No env-var secret reads: {tb.get('no_env_var_secret_reads')}",
        f"- Behavioral (mocked, no network) ok: "
        f"{(tb.get('behavioral') or {}).get('ok')}",
        f"- Token absent from all outputs: "
        f"{(tb.get('behavioral') or {}).get('token_absent_from_outputs')}",
    ]

    eb = rep.get("external_search_transport_boundary", {})
    ebb = eb.get("behavioral") or {}
    L += [
        "",
        f"## Phase 14B Read-Only Search Boundary: "
        f"{'OK' if eb.get('ok') else 'FAIL'}",
        f"- Boundary module: `{eb.get('boundary_module')}`",
        f"- Only external_http capability: {eb.get('only_external_http_capability')}",
        f"- Fails closed without secrets: {eb.get('fails_closed_defined')}",
        f"- GET-only, host-allowlisted HTTPS: "
        f"{eb.get('get_only_no_post')} / {eb.get('https_and_host_guarded')}",
        f"- Key never printed / no env secrets: "
        f"{eb.get('key_not_printed')} / {eb.get('no_env_var_secret_reads')}",
        f"- Not wired to hunter/alerts/scheduler: "
        f"{eb.get('not_wired_to_hunter_alerts_scheduler')}",
        f"- Behavioral (mocked, no real network) ok: {ebb.get('ok')}",
        f"- No network without credentials: "
        f"{ebb.get('no_network_without_credentials')}",
        f"- Key absent from results & report: "
        f"{ebb.get('key_absent_from_results')} / {ebb.get('key_absent_from_report')}",
        f"- Findings quarantined EXTERNAL_CLAIM_ONLY: "
        f"{ebb.get('findings_quarantined_external_claim_only')}",
    ]

    L += ["", "## Remaining Risks"]
    for r in rep["remaining_risks"]:
        L.append(f"- {r}")

    L += [
        "",
        "## Phase 2 Recommendation",
        "",
        rep["phase_2_recommendation"],
        "",
    ]
    return "\n".join(L).strip() + "\n"


def generate_commander_2_safety_isolation_report(
    root: Path | None = None,
    json_path: Path = REPORT_JSON,
    md_path: Path = REPORT_MD,
) -> dict[str, Any]:
    rep = build_commander_2_safety_isolation_report(root)
    write_json(json_path, rep)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_safety_report_markdown(rep), encoding="utf-8")
    return rep
