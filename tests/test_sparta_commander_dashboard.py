from __future__ import annotations

import app as app_module
from fastapi.testclient import TestClient


def _install_profit_brain_reports(
    monkeypatch,
    profit_brain_report: dict,
    learning_report: dict,
    frozen_stack_context: dict | None = None,
    decision_gate_report: dict | None = None,
    data_quality_repair_report: dict | None = None,
    waiting_protocol_report: dict | None = None,
    alerts_report: dict | None = None,
    strategy_lab_report: dict | None = None,
) -> None:
    import sparta_commander.commander as commander

    monkeypatch.setattr(commander, "load_profit_brain_report", lambda: profit_brain_report)
    monkeypatch.setattr(commander, "load_profit_brain_learning_report", lambda: learning_report)
    monkeypatch.setattr(commander, "load_frozen_stack_read_only_context", lambda: frozen_stack_context or {})
    monkeypatch.setattr(
        commander,
        "load_strategy_lab_master_readiness_report",
        lambda: strategy_lab_report or {
            "schema": "sparta_commander.strategy_lab_master_readiness.v1",
            "generated_at": "2026-05-12T00:00:00+00:00",
            "read_only": True,
            "status": "INSUFFICIENT_DATA",
            "candidate_count": 0,
            "status_counts": {
                "REJECT": 0,
                "NEEDS_MORE_RESEARCH": 0,
                "PAPER_READY": 0,
                "WATCHLIST_READY": 0,
            },
            "latest_generated_at": None,
            "safety_status": "ISOLATED / READ_ONLY",
            "source_report": {"path": None, "exists": False},
            "candidates": [],
        },
    )
    monkeypatch.setattr(commander, "load_profit_brain_decision_gate", lambda: decision_gate_report or {})
    monkeypatch.setattr(commander, "load_profit_brain_data_quality_repair", lambda: data_quality_repair_report or {})
    monkeypatch.setattr(commander, "load_profit_brain_waiting_protocol", lambda: waiting_protocol_report or {})
    monkeypatch.setattr(commander, "load_profit_brain_alerts", lambda: alerts_report or {})
    monkeypatch.setattr(commander, "load_daily_profit_brain_snapshots", lambda limit=7: [])
    monkeypatch.setattr(commander, "summarize_daily_profit_brain_snapshots", lambda snapshots=None: {
        "status": "INSUFFICIENT_DATA",
        "count": 0,
        "recent": [],
        "regime_trend": [],
        "confidence_trend": [],
        "risk_level_trend": [],
        "strategy_changes": [],
        "recurring_risks": [],
    })


def test_dashboard_renders_profit_brain_panels(monkeypatch):
    _install_profit_brain_reports(
        monkeypatch,
        {
            "daily_profit_brief": {
                "current_regime": "COMPRESSION",
                "best_strategy_today": {"strategy": "G"},
                "worst_strategy_today": {"strategy": "D2"},
                "recommended_next_action": "watchlist",
                "confidence_score": 31,
                "data_quality_score": 51,
                "strategies_to_pause": ["D2"],
                "strategies_to_watch": ["F2"],
                "strategies_with_improving_edge": ["G"],
                "account_bot_health_summary": "1 running / 3 stopped bots",
            },
            "market_regime_compatibility": {"best_fit_strategy_type_now": "mean_reversion"},
            "risk_officer_report": {"risk_level": "MEDIUM", "warnings": ["Missing ETH heartbeat", "Insufficient history"], "open_trade_count": 5},
        },
        {
            "summary": {
                "status": "INSUFFICIENT_DATA",
                "most_reliable_regimes": [{"regime": "COMPRESSION", "entries": 3, "average_confidence": 61}],
                "most_reliable_strategies": [{"strategy": "G", "survival_score": 37.1}],
                "weakest_strategies": [{"strategy": "D2", "survival_score": 2.2}],
                "recurring_risk_patterns": ["Risk level repeatedly lands in MEDIUM."],
            },
            "learning_insights": {
                "confidence_drift": 0,
                "recommendation_accuracy": {
                    "strategy": {"accuracy_pct": None},
                    "regime": {"accuracy_pct": None},
                },
            },
            "regime_memory_database": {"entries_count": 0, "status": "INSUFFICIENT_DATA"},
            "confidence_calibration_layer": {"calibrated_confidence": 31},
        },
        {
            "market_regime": {
                "label": "COMPRESSED_DORMANT",
                "suppression_duration_days": 118,
                "cadence_trend": ["SUPPRESSED", "SUPPRESSED", "SUPPRESSED"],
            },
            "deployment_readiness": {
                "status": "RED",
                "confidence_score": 45.0,
                "drift_warning_count": 1,
                "why_not_ready_reasons": [
                    "min_30d_executed_trades failed: current=0, threshold=1.",
                    "min_60d_executed_trades failed: current=0, threshold=1.",
                ],
            },
            "validation_summary": {
                "global_verdict": "DRIFT_WARNING",
                "n_in_envelope": 3,
                "n_out_envelope": 3,
                "paper_days_elapsed": 390,
                "d4_reproducible": True,
                "frozen_stack_survives_operational_reality": True,
            },
            "evidence": {
                "executed_trades_30d": 0,
                "executed_trades_60d": 0,
                "executed_trades_90d": 0,
                "participation_ratio_90d": 0.0,
                "suppression_duration_days": 118,
                "drift_warning_count": 1,
            },
            "confidence_context": {
                "status": "READY",
                "base_confidence": 45.0,
                "adjusted_confidence": 30.0,
                "confidence_label": "LOW",
                "adjustments": [{"reason": "deployment_readiness_red", "delta": -8.0}],
                "note": "Read-only confidence context only; not used for trade execution or decision gating.",
            },
            "why_not_ready_reasons": [
                "min_30d_executed_trades failed: current=0, threshold=1.",
                "min_60d_executed_trades failed: current=0, threshold=1.",
            ],
        },
        {
            "gate_status": "YELLOW",
            "recommended_stance": "watch only / reduced confidence",
            "confidence_score": 31,
            "calibrated_confidence": 31,
            "data_quality_score": 51,
            "current_regime": "COMPRESSION",
            "market_fit_now": "mean_reversion",
            "risk_level": "MEDIUM",
            "top_3_reasons": [
                "Confidence is modest and the bot should stay watch-only.",
                "Risk is MEDIUM and the current regime is COMPRESSION.",
                "Active risk warnings remain: Missing heartbeat.",
            ],
            "strategies_allowed_to_watch": ["G", "F2"],
            "strategies_to_avoid": ["D2"],
            "risk_warnings": ["Missing heartbeat"],
            "snapshot_trend": {
                "status": "PARTIAL",
                "count": 2,
                "regime_trend": ["COMPRESSION", "EXTREME_COMPRESSION"],
                "confidence_trend": [29, 31],
                "risk_level_trend": ["MEDIUM", "MEDIUM"],
            },
        },
        {
            "current_data_quality_score": 51,
            "decision_gate_status": "RED",
            "top_missing_evidence": ["Missing bot heartbeat files", "Closed trade history is too short (4 < 20)."],
            "top_repair_actions": [
                {"priority": "HIGH", "recommended_action": "Restore heartbeat files and confirm bots report RUNNING state."},
                {"priority": "HIGH", "recommended_action": "Accumulate at least 20 closed trades before trusting statistics."},
            ],
            "confidence_blockers": ["Missing bot heartbeat files", "Closed trade history is too short"],
            "gate_blockers": ["Decision Gate remains RED"],
        },
        {
            "waiting_status": "RED",
            "current_gate_status": "RED",
            "why_gate_red": [
                "Closed-trade history is still below the 20-trade threshold.",
                "Open exposure is still concentrated in XRPUSDT (5/5).",
            ],
            "minimum_closed_trades_needed": 20,
            "current_closed_trades_count": 4,
            "current_concentration_risk": {
                "dominant_symbol": "XRPUSDT",
                "dominant_symbol_open_count": 5,
                "open_trade_count": 5,
                "concentration_ratio_pct": 100.0,
            },
            "data_quality_score": 51,
            "calibrated_confidence": 31,
            "closed_trades_progress_pct": 20.0,
            "data_quality_progress_pct": 72.9,
            "confidence_progress_pct": 68.9,
            "unlock_target": "20 closed trades, concentration under 60%, scheduler RUNNING, valid heartbeats, data quality > 70, calibrated confidence > 45",
            "what_sparta_needs_next": [
                "Wait for at least 20 closed trades.",
                "Reduce single-symbol exposure below 60% of open trades.",
            ],
            "what_should_not_be_done_yet": [
                "Do not raise allocation.",
                "Do not move the gate to GREEN.",
            ],
        },
        {
            "alert_state": "ACTIVE",
            "alert_badge": "2 UPDATES",
            "current_gate_status": "RED",
            "current_closed_trades_count": 4,
            "current_xrp_concentration_pct": 100.0,
            "current_data_quality_score": 51,
            "current_calibrated_confidence": 31,
            "alert_count": 2,
            "triggered_alerts": [
                {"message": "Closed trades reached the 20-trade unlock threshold."},
                {"message": "Data quality rose above the 70-point unlock threshold."},
            ],
            "unlock_targets": {
                "closed_trades": 20,
                "xrp_concentration_pct": 60,
                "data_quality_score": 70,
                "calibrated_confidence": 45,
            },
            "snapshot_trend": {"recent": [{"regime": "EXTREME_COMPRESSION", "calibrated_confidence": 31, "recommended_next_action": "watchlist"}]},
        },
    )
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "status-banner" in body
    assert "status-banner--orange" in body
    assert "status-yellow" in body
    assert "status-panel status-orange" in body
    assert "Blocked" in body
    assert "Caution" in body
    assert "Trading Profit Brain Decision Gate" in body
    assert "Profit Brain Data Quality" in body
    assert "What SPARTA Is Waiting For" in body
    assert "Profit Brain Alerts" in body
    assert "watch only / reduced confidence" in body
    assert "Trading Profit Brain" in body
    assert "Profit Brain Learning" in body
    assert "Frozen-Stack Regime Intelligence" in body
    assert "READ-ONLY — NO EXECUTION ENABLED" in body
    assert "SYSTEM STATUS: DEFENSIVE MODE" in body
    assert "COMPRESSION" in body
    assert "watchlist" in body
    assert "MEDIUM" in body
    assert "INSUFFICIENT_DATA" in body


def test_dashboard_missing_reports_fail_gracefully(monkeypatch):
    _install_profit_brain_reports(monkeypatch, {}, {}, None, {}, {}, {}, {})
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "status-banner--gray" in body
    assert "status-panel status-gray" in body
    assert "Unavailable" in body
    assert "Frozen-stack regime intelligence is not available yet." in body
    assert "Profit Brain Decision Gate report is not available yet." in body
    assert "Profit Brain Data Quality repair report is not available yet." in body
    assert "Trading Profit Brain report is not available yet." in body
    assert "Profit Brain Learning report is not available yet." in body
    assert "What SPARTA Is Waiting For report is not available yet." in body
    assert "Profit Brain Alerts report is not available yet." in body
    assert "READ-ONLY — NO EXECUTION ENABLED" in body


def test_dashboard_renders_critical_failure_status_classes(monkeypatch):
    _install_profit_brain_reports(
        monkeypatch,
        {},
        {},
        {
            "market_regime": {"label": "COMPRESSED_DORMANT", "suppression_duration_days": 118, "cadence_trend": ["SUPPRESSED", "SUPPRESSED", "SUPPRESSED"]},
            "deployment_readiness": {"status": "RED", "confidence_score": 45.0, "drift_warning_count": 1, "why_not_ready_reasons": ["min_30d_executed_trades failed: current=0, threshold=1."]},
            "validation_summary": {
                "global_verdict": "FAIL",
                "n_in_envelope": 0,
                "n_out_envelope": 3,
                "paper_days_elapsed": 390,
                "d4_reproducible": False,
                "frozen_stack_survives_operational_reality": False,
            },
            "evidence": {
                "executed_trades_30d": 0,
                "executed_trades_60d": 0,
                "executed_trades_90d": 0,
                "participation_ratio_90d": 0.0,
                "suppression_duration_days": 118,
                "drift_warning_count": 1,
            },
            "confidence_context": {
                "status": "READY",
                "base_confidence": 45.0,
                "adjusted_confidence": 30.0,
                "confidence_label": "LOW",
                "adjustments": [{"reason": "deployment_readiness_red", "delta": -8.0}],
                "note": "Read-only confidence context only; not used for trade execution or decision gating.",
            },
            "why_not_ready_reasons": ["validation failed"],
        },
        {
            "gate_status": "GREEN",
            "recommended_stance": "green / ready",
            "confidence_score": 82,
            "calibrated_confidence": 82,
            "data_quality_score": 88,
            "current_regime": "EXPANSION",
            "market_fit_now": "breakout",
            "risk_level": "LOW",
            "top_3_reasons": ["Confidence is high and the system is ready."],
            "strategies_allowed_to_watch": ["G"],
            "strategies_to_avoid": [],
            "risk_warnings": [],
            "snapshot_trend": {"status": "READY", "count": 2, "regime_trend": ["RECOVERING", "EXPANSION"], "confidence_trend": [78, 82], "risk_level_trend": ["LOW", "LOW"]},
        },
        {
            "current_data_quality_score": 88,
            "decision_gate_status": "GREEN",
            "top_missing_evidence": [],
            "top_repair_actions": [],
            "confidence_blockers": [],
            "gate_blockers": [],
        },
        {
            "waiting_status": "GREEN",
            "current_gate_status": "GREEN",
            "why_gate_red": [],
            "minimum_closed_trades_needed": 20,
            "current_closed_trades_count": 20,
            "current_concentration_risk": {"dominant_symbol": "BTCUSDT", "dominant_symbol_open_count": 1, "open_trade_count": 3, "concentration_ratio_pct": 33.3},
            "data_quality_score": 88,
            "calibrated_confidence": 82,
            "closed_trades_progress_pct": 100.0,
            "data_quality_progress_pct": 100.0,
            "confidence_progress_pct": 100.0,
            "unlock_target": "Ready",
            "what_sparta_needs_next": ["Keep monitoring only."],
            "what_should_not_be_done_yet": [],
        },
        {
            "alert_state": "GREEN",
            "alert_badge": "READY",
            "current_gate_status": "GREEN",
            "current_closed_trades_count": 20,
            "current_xrp_concentration_pct": 33.3,
            "current_data_quality_score": 88,
            "current_calibrated_confidence": 82,
            "alert_count": 0,
            "triggered_alerts": [],
            "unlock_targets": {"closed_trades": 20, "xrp_concentration_pct": 60, "data_quality_score": 70, "calibrated_confidence": 45},
            "snapshot_trend": {"recent": [{"regime": "EXPANSION", "calibrated_confidence": 82, "recommended_next_action": "keep active"}]},
        },
    )
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "status-banner--red" in body
    assert "status-panel status-red" in body
    assert "CRITICAL MODE" in body
    assert "Broken automation" in body
    assert "READ-ONLY — NO EXECUTION ENABLED" in body


def test_dashboard_renders_green_and_gray_status_classes(monkeypatch):
    _install_profit_brain_reports(
        monkeypatch,
        {
            "daily_profit_brief": {
                "current_regime": "EXPANSION",
                "best_strategy_today": {"strategy": "G"},
                "worst_strategy_today": {"strategy": "D2"},
                "recommended_next_action": "keep active",
                "confidence_score": 82,
                "data_quality_score": 88,
                "strategies_to_pause": [],
                "strategies_to_watch": ["G"],
                "strategies_with_improving_edge": ["G"],
                "account_bot_health_summary": "all systems healthy",
            },
            "market_regime_compatibility": {"best_fit_strategy_type_now": "breakout"},
            "risk_officer_report": {"risk_level": "LOW", "warnings": [], "open_trade_count": 0},
        },
        {
            "summary": {
                "status": "READY",
                "most_reliable_regimes": [{"regime": "EXPANSION", "entries": 7, "average_confidence": 82}],
                "most_reliable_strategies": [{"strategy": "G", "survival_score": 91.2}],
                "weakest_strategies": [{"strategy": "D2", "survival_score": 4.4}],
                "recurring_risk_patterns": [],
            },
            "learning_insights": {
                "confidence_drift": 4,
                "recommendation_accuracy": {
                    "strategy": {"accuracy_pct": 81},
                    "regime": {"accuracy_pct": 78},
                },
            },
            "regime_memory_database": {"entries_count": 7, "status": "READY"},
            "confidence_calibration_layer": {"calibrated_confidence": 82},
        },
        {
            "market_regime": {
                "label": "EXPANSION",
                "suppression_duration_days": 0,
                "cadence_trend": ["RECOVERING", "RECOVERING", "UP"],
            },
            "deployment_readiness": {
                "status": "GREEN",
                "confidence_score": 82,
                "drift_warning_count": 0,
                "why_not_ready_reasons": [],
            },
            "validation_summary": {
                "global_verdict": "PASS",
                "n_in_envelope": 6,
                "n_out_envelope": 0,
                "paper_days_elapsed": 390,
                "d4_reproducible": True,
                "frozen_stack_survives_operational_reality": True,
            },
            "evidence": {
                "executed_trades_30d": 2,
                "executed_trades_60d": 4,
                "executed_trades_90d": 6,
                "participation_ratio_90d": 0.34,
                "suppression_duration_days": 0,
                "drift_warning_count": 0,
            },
            "confidence_context": {
                "status": "READY",
                "base_confidence": 82.0,
                "adjusted_confidence": 82.0,
                "confidence_label": "HIGH",
                "adjustments": [],
                "note": "Read-only confidence context only; not used for trade execution or decision gating.",
            },
            "why_not_ready_reasons": [],
        },
        {
            "gate_status": "GREEN",
            "recommended_stance": "green / ready",
            "confidence_score": 82,
            "calibrated_confidence": 82,
            "data_quality_score": 88,
            "current_regime": "EXPANSION",
            "market_fit_now": "breakout",
            "risk_level": "LOW",
            "top_3_reasons": ["Confidence is high and the system is ready."],
            "strategies_allowed_to_watch": ["G"],
            "strategies_to_avoid": [],
            "risk_warnings": [],
            "snapshot_trend": {
                "status": "READY",
                "count": 2,
                "regime_trend": ["RECOVERING", "EXPANSION"],
                "confidence_trend": [78, 82],
                "risk_level_trend": ["LOW", "LOW"],
            },
        },
        {
            "current_data_quality_score": 88,
            "decision_gate_status": "GREEN",
            "top_missing_evidence": [],
            "top_repair_actions": [],
            "confidence_blockers": [],
            "gate_blockers": [],
        },
        {
            "waiting_status": "GREEN",
            "current_gate_status": "GREEN",
            "why_gate_red": [],
            "minimum_closed_trades_needed": 20,
            "current_closed_trades_count": 20,
            "current_concentration_risk": {
                "dominant_symbol": "BTCUSDT",
                "dominant_symbol_open_count": 1,
                "open_trade_count": 3,
                "concentration_ratio_pct": 33.3,
            },
            "data_quality_score": 88,
            "calibrated_confidence": 82,
            "closed_trades_progress_pct": 100.0,
            "data_quality_progress_pct": 100.0,
            "confidence_progress_pct": 100.0,
            "unlock_target": "Ready",
            "what_sparta_needs_next": ["Keep monitoring only."],
            "what_should_not_be_done_yet": [],
        },
        {
            "alert_state": "GREEN",
            "alert_badge": "READY",
            "current_gate_status": "GREEN",
            "current_closed_trades_count": 20,
            "current_xrp_concentration_pct": 33.3,
            "current_data_quality_score": 88,
            "current_calibrated_confidence": 82,
            "alert_count": 0,
            "triggered_alerts": [],
            "unlock_targets": {
                "closed_trades": 20,
                "xrp_concentration_pct": 60,
                "data_quality_score": 70,
                "calibrated_confidence": 45,
            },
            "snapshot_trend": {"recent": [{"regime": "EXPANSION", "calibrated_confidence": 82, "recommended_next_action": "keep active"}]},
        },
    )
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "status-banner--green" in body
    assert "status-panel status-green" in body
    assert "Good" in body
    assert "green / ready" in body
    assert "Deployment conditions acceptable." in body


def test_commander_profit_brain_refresh_endpoint_is_read_only(monkeypatch):
    import sparta_commander.daily_profit_brain_runner as runner

    monkeypatch.setattr(runner, "run_daily_profit_brain_refresh", lambda **kwargs: {
        "ok": True,
        "read_only": True,
        "reports": {
            "sparta_profit_brain": "C:/SPARTA_BRAIN/reports/sparta_profit_brain.json",
            "sparta_profit_brain_md": "C:/SPARTA_BRAIN/reports/sparta_profit_brain.md",
            "profit_brain_learning": "C:/SPARTA_BRAIN/reports/profit_brain_learning.json",
            "profit_brain_learning_md": "C:/SPARTA_BRAIN/reports/profit_brain_learning.md",
        },
        "snapshot_path": "C:/SPARTA_BRAIN/data/profit_brain_daily_snapshots.jsonl",
        "snapshot": {
            "regime": "COMPRESSION",
            "learning_status": "INSUFFICIENT_DATA",
            "recommended_next_action": "watchlist",
            "confidence_score": 31,
        },
    })

    client = TestClient(app_module.app)
    response = client.post("/api/commander/profit-brain/daily-refresh")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["reports"]["sparta_profit_brain"].endswith("sparta_profit_brain.json")
    assert payload["reports"]["profit_brain_learning"].endswith("profit_brain_learning.json")
    assert payload["summary"]["profit_brain_status"] == "refreshed"
    assert payload["summary"]["learning_status"] == "INSUFFICIENT_DATA"
    assert payload["summary"]["decision_gate_status"] == "INSUFFICIENT_DATA"

    route_paths = {route.path for route in app_module.app.routes if hasattr(route, "path")}
    assert "/api/commander/profit-brain/refresh" in route_paths
    assert "/api/commander/profit-brain/daily-refresh" in route_paths
    assert "/api/commander/profit-brain/execute" not in route_paths
    assert "/api/commander/profit-brain/decision-gate/execute" not in route_paths
    assert "/api/commander/profit-brain/data-quality/execute" not in route_paths
    assert "/api/commander/profit-brain/waiting-protocol/execute" not in route_paths
    assert "/api/commander/profit-brain/alerts/execute" not in route_paths
    assert "/api/commander/profit-brain-learning/execute" not in route_paths
