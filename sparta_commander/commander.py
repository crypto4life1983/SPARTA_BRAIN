"""Facade for the SPARTA Commander orchestration layer."""

from __future__ import annotations

from typing import Any

from .action_planner import load_action_plans, summarize_action_plans
from .daily_summary import load_daily_summary
from .failure_classifier import classify_many
from .health import check_health
from .memory import latest_workflows, record_workflow
from .notification_channels import load_notification_config
from .profit_brain_decision_gate import load_profit_brain_decision_gate
from .profit_brain_alerts import load_profit_brain_alerts
from .profit_brain_data_quality_repair import load_profit_brain_data_quality_repair
from .profit_brain_waiting_protocol import load_profit_brain_waiting_protocol
from .reports import build_report, generate_daily_report
from .frozen_stack_regime_intelligence import load_frozen_stack_read_only_context
from .strategy_lab_readiness import load_strategy_lab_master_readiness_report
from .profit_brain import load_profit_brain_report
from .profit_brain_learning import load_profit_brain_learning_report
from .daily_profit_brain_runner import load_daily_profit_brain_snapshots, summarize_daily_profit_brain_snapshots
from .router import recommend_brain
from .safe_executor import executor_status
from .skill_suggestions import load_skill_suggestions
from .task_queue import add_task, get_next_task, list_tasks
from .trading_reports import build_trading_bridge_report
from .watcher import read_heartbeat
from .workflow_learning import load_workflow_scores


def health_status() -> dict[str, Any]:
    return check_health()


def route_task(task_text: str = "", category: str = "") -> dict[str, str]:
    return recommend_brain(task_text, category)


def generate_report() -> dict[str, Any]:
    return generate_daily_report()


def dashboard_summary() -> dict[str, Any]:
    """Read current commander state for dashboard display without mutating pipelines."""
    health = check_health()
    latest = latest_workflows(1)
    pending = list_tasks("pending")
    next_task = get_next_task()
    next_action = "No pending commander task."
    recommended_brain = "Commander"
    if next_task:
        next_action = str(next_task.get("title", "Untitled task"))
        recommended_brain = str(next_task.get("assigned_brain") or "Commander")
    elif health.get("warnings"):
        next_action = str(health["warnings"][0])

    report = build_report()
    watcher = read_heartbeat()
    workflow_scores = load_workflow_scores()
    skill_suggestions = load_skill_suggestions()
    daily_summary = load_daily_summary()
    notification_config = load_notification_config()
    failure_classifications = classify_many([{"title": "Health warning", "message": warning} for warning in health.get("warnings", [])])
    action_plans = load_action_plans()
    action_plan_summary = summarize_action_plans(action_plans)
    top_action_plans = [plan for plan in action_plans if plan.get("status") in {"proposed", "blocked"}][:3]
    safe_executor_status = executor_status()
    trading_report = build_trading_bridge_report()
    profit_brain = load_profit_brain_report()
    profit_brain_learning = load_profit_brain_learning_report()
    profit_brain_decision_gate = load_profit_brain_decision_gate()
    profit_brain_data_quality_repair = load_profit_brain_data_quality_repair()
    profit_brain_waiting_protocol = load_profit_brain_waiting_protocol()
    profit_brain_alerts = load_profit_brain_alerts()
    frozen_stack_read_only_context = load_frozen_stack_read_only_context()
    strategy_lab_master_readiness = load_strategy_lab_master_readiness_report()
    profit_brain_daily_snapshots = load_daily_profit_brain_snapshots(limit=7)
    profit_brain_daily_snapshot_summary = summarize_daily_profit_brain_snapshots(profit_brain_daily_snapshots)
    return {
        "overall_status": report.get("overall_status", "unknown"),
        "pending_tasks_count": len(pending),
        "latest_workflow_memory": latest[0] if latest else None,
        "health_warnings": health.get("warnings", []),
        "recommended_next_action": next_action,
        "recommended_brain_for_next_task": recommended_brain,
        "health": health,
        "watcher": watcher,
        "failure_classifications": failure_classifications,
        "workflow_reliability_top5": workflow_scores[:5],
        "skill_suggestions_count": len(skill_suggestions),
        "notification_config": notification_config,
        "daily_summary": daily_summary,
        "top_recommended_actions": (report.get("recommended_next_actions") or [])[:3],
        "action_plan_summary": action_plan_summary,
        "top_action_plans": top_action_plans,
        "safe_executor": safe_executor_status,
        "trading_bridge": trading_report,
        "profit_brain": profit_brain,
        "profit_brain_learning": profit_brain_learning,
        "profit_brain_decision_gate": profit_brain_decision_gate,
        "profit_brain_data_quality_repair": profit_brain_data_quality_repair,
        "profit_brain_waiting_protocol": profit_brain_waiting_protocol,
        "profit_brain_alerts": profit_brain_alerts,
        "frozen_stack_read_only_context": frozen_stack_read_only_context,
        "strategy_lab_master_readiness": strategy_lab_master_readiness,
        "profit_brain_daily_snapshots": profit_brain_daily_snapshots,
        "profit_brain_daily_snapshot_summary": profit_brain_daily_snapshot_summary,
    }
