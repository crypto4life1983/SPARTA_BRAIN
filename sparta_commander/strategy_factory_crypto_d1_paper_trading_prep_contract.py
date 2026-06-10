"""Crypto-D1 V2 Paper-Trading Prep Contract (PREP ONLY, NO LIVE MONEY).

A PURE, stdlib-only, read-only module that PREPARES (but never starts) a SIMULATED
paper-trading harness for the single selected variant
``V2_trend_plus_cash_regime`` -- the only variant the variant-backtest review
APPROVED for paper prep (clears the -50% drawdown floor: max drawdown -48.16%,
Sharpe 1.10).

It pins V2's exact pre-registered rule parameters (200-day trend filter; cash regime
requiring >= 2 of 3 sleeves in trend) and assembles a fully-specified PAPER config:
  - simulated paper account assumptions (no real money, no broker, no exchange);
  - risk limits (long-only, no leverage / shorting / margin, exposure & per-asset caps);
  - kill-switch rules (drawdown kill, daily-loss halt, data-staleness halt, manual kill);
  - logging / reporting requirements;
  - hard no-live-money guardrails.

It STARTS NOTHING: no paper run, no broker/exchange connection, no order execution,
no real account, no optimization, no parameter search, no network, no credentials.
It writes nothing to disk. It UNLOCKS no gate: paper_trading_gate and micro_live_gate
(and the live gate) stay LOCKED. An ACTUAL simulated paper run requires a SEPARATE
explicit human command.

Public API:
  - PAPER_PREP_SCHEMA_VERSION / PAPER_PREP_LABEL / PAPER_PREP_MODE
  - SELECTED_VARIANT_ID / VERDICT_READY / VERDICT_NOT_READY
  - PAPER_ACCOUNT / RISK_LIMITS / KILL_SWITCH / LOGGING / NO_LIVE_MONEY_GUARDRAILS
  - NEXT_REQUIRED_ACTION
  - get_paper_trading_prep_label()
  - paper_account_assumptions() / risk_limits() / kill_switch_rules()
  - logging_requirements() / no_live_money_guardrails()
  - build_paper_prep_config()
  - check_paper_prep_readiness(repo_root)
  - validate_paper_prep_report(report)
  - render_paper_prep_markdown(report)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_REQUIRED_SYMBOLS,
)
from sparta_commander.strategy_factory_crypto_d1_variant_backtest_prep_contract import (
    build_variant_manifests,
)
from sparta_commander.strategy_factory_crypto_d1_variant_backtest_review_contract import (
    APPROVE_PAPER_PREP_ONLY,
    build_variant_review_decision,
)

PAPER_PREP_SCHEMA_VERSION = "strategy_factory_crypto_d1_paper_trading_prep_contract.v1"
PAPER_PREP_LABEL = "Crypto-D1 V2 Paper-Trading Prep Contract (PREP ONLY, NO LIVE MONEY)"
PAPER_PREP_MODE = "RESEARCH_ONLY"

SELECTED_VARIANT_ID = "V2_trend_plus_cash_regime"

VERDICT_READY = "READY"
VERDICT_NOT_READY = "NOT_READY"

NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PAPER_TRADING_RUN_SIMULATED_NO_LIVE_MONEY"

# Where a FUTURE simulated paper runner would write its logs. Declared only -- this
# prep contract creates nothing.
PAPER_LOG_DIR = "reports/crypto_d1_paper_prep"

# Simulated account assumptions. There is NO real money and NO venue connection: every
# fill is a model fill against the next QA-passed daily close, with assumed costs.
PAPER_ACCOUNT: dict[str, Any] = {
    "account_type": "SIMULATED_PAPER",
    "real_money": False,
    "broker_connected": False,
    "exchange_connected": False,
    "starting_equity": 10000.0,
    "quote_currency": "USDT",
    "universe": list(QA_REQUIRED_SYMBOLS),
    "data_source": "QA_PASSED_LOCAL_CSV_ONLY",
    "fill_model": "SIMULATED_NEXT_DAILY_CLOSE",
    "assumed_fee_rate": 0.001,
    "assumed_slippage_rate": 0.0005,
    "rebalance_frequency": "DAILY_SIGNAL_EVAL",
}

# Hard risk limits for the simulated paper harness. V2 is long-only with a cash regime;
# a single sleeve can reach 0.5 (two-sleeve invested state), hence the 0.50 per-asset
# cap. No leverage / shorting / margin -- ever.
RISK_LIMITS: dict[str, Any] = {
    "long_only": True,
    "allow_leverage": False,
    "allow_shorting": False,
    "allow_margin": False,
    "max_gross_exposure": 1.0,
    "max_weight_per_asset": 0.50,
    "trend_filter_sma_days": 200,
    "min_sleeves_in_trend_to_invest": 2,
    "total_sleeves": 3,
    "daily_loss_limit": -0.10,
    "hard_drawdown_kill": -0.50,
}

# Kill-switch rules. On ANY trigger the harness flattens to cash and halts; nothing
# auto-resumes without a human.
KILL_SWITCH: dict[str, Any] = {
    "drawdown_kill_threshold": -0.50,
    "daily_loss_halt_threshold": -0.10,
    "data_staleness_halt_hours": 48,
    "error_halt": True,
    "manual_kill_enabled": True,
    "on_kill_action": "FLATTEN_TO_CASH_AND_HALT",
    "auto_resume": False,
    "requires_human_to_resume": True,
}

# Logging / reporting requirements a future paper runner must satisfy.
LOGGING: dict[str, Any] = {
    "log_dir": PAPER_LOG_DIR,
    "log_format": "jsonl",
    "log_each_evaluation": True,
    "required_log_fields": [
        "timestamp",
        "date",
        "in_trend_by_symbol",
        "sleeves_in_trend",
        "target_weights",
        "simulated_fills",
        "equity",
        "cash",
        "drawdown",
        "kill_switch_state",
        "notes",
    ],
    "daily_report": True,
    "report_fields": [
        "equity_curve",
        "daily_return",
        "max_drawdown",
        "positions",
        "simulated_trades",
        "kill_switch_events",
    ],
    "writes_real_orders": False,
}

# Non-negotiable no-live-money guardrails. Every one of these MUST hold for the paper
# harness; the prep contract itself also honors them.
NO_LIVE_MONEY_GUARDRAILS: dict[str, Any] = {
    "no_live_money": True,
    "no_real_account": True,
    "no_broker_connection": True,
    "no_exchange_connection": True,
    "no_network": True,
    "no_credentials": True,
    "no_real_order_execution": True,
    "simulated_orders_only": True,
    "requires_separate_human_command_to_run": True,
    "live_gate_locked": True,
    "micro_live_gate_locked": True,
}


def get_paper_trading_prep_label() -> str:
    """Human label for the recognized Crypto-D1 V2 paper-trading prep contract."""
    return PAPER_PREP_LABEL


def paper_account_assumptions() -> dict[str, Any]:
    """Return a fresh copy of the simulated paper account assumptions. Pure."""
    return dict(PAPER_ACCOUNT, universe=list(PAPER_ACCOUNT["universe"]))


def risk_limits() -> dict[str, Any]:
    """Return a fresh copy of the paper risk limits. Pure."""
    return dict(RISK_LIMITS)


def kill_switch_rules() -> dict[str, Any]:
    """Return a fresh copy of the kill-switch rules. Pure."""
    return dict(KILL_SWITCH)


def logging_requirements() -> dict[str, Any]:
    """Return a fresh copy of the logging / reporting requirements. Pure."""
    return dict(
        LOGGING,
        required_log_fields=list(LOGGING["required_log_fields"]),
        report_fields=list(LOGGING["report_fields"]),
    )


def no_live_money_guardrails() -> dict[str, Any]:
    """Return a fresh copy of the no-live-money guardrails. Pure."""
    return dict(NO_LIVE_MONEY_GUARDRAILS)


def _selected_variant_manifest() -> dict[str, Any] | None:
    """The fully-specified manifest for the selected V2 variant (or None). Pure."""
    for m in build_variant_manifests():
        if m.get("variant_id") == SELECTED_VARIANT_ID:
            return m
    return None


def build_paper_prep_config() -> dict[str, Any]:
    """Assemble the fully-specified PAPER prep config for V2: its pinned strategy rule
    parameters plus account / risk / kill-switch / logging / guardrail blocks. Pure;
    reads nothing from disk; starts nothing."""
    manifest = _selected_variant_manifest()
    fixed = (manifest or {}).get("fixed_parameters") or {}
    return {
        "selected_variant_id": SELECTED_VARIANT_ID,
        "description": (manifest or {}).get("description"),
        "controls": list((manifest or {}).get("controls") or []),
        "strategy_parameters": fixed,
        "paper_account": paper_account_assumptions(),
        "risk_limits": risk_limits(),
        "kill_switch": kill_switch_rules(),
        "logging": logging_requirements(),
        "no_live_money_guardrails": no_live_money_guardrails(),
    }


def check_paper_prep_readiness(repo_root: str = ".") -> dict[str, Any]:
    """Decide whether V2 paper-trading is PREPARED (not started). READY requires the
    variant-backtest review to have APPROVED paper prep for exactly V2. Reads only the
    variant review (one local report); writes nothing; starts no paper run; connects
    nothing; unlocks no gate."""
    review = build_variant_review_decision(repo_root)
    config = build_paper_prep_config()

    blockers: list[str] = []
    if review.get("paper_prep_decision") != APPROVE_PAPER_PREP_ONLY:
        blockers.append("variant_paper_prep_not_approved")
    if review.get("selected_variant_id") != SELECTED_VARIANT_ID:
        blockers.append("selected_variant_mismatch")
    if _selected_variant_manifest() is None:
        blockers.append("selected_variant_manifest_missing")

    verdict = VERDICT_READY if not blockers else VERDICT_NOT_READY
    return {
        "schema_version": PAPER_PREP_SCHEMA_VERSION,
        "label": PAPER_PREP_LABEL,
        "mode": PAPER_PREP_MODE,
        "verdict": verdict,
        "blockers": blockers,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "review_paper_prep_decision": review.get("paper_prep_decision"),
        "review_selected_variant_id": review.get("selected_variant_id"),
        "config": config,
        # Capability posture (this prep starts / connects / authorizes nothing):
        "starts_paper_trading": False,
        "connects_broker": False,
        "connects_exchange": False,
        "executes_orders": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "runs_optimization": False,
        "runs_parameter_search": False,
        "authorizes_live_trading": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this prep):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_paper_prep_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a paper-prep report's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_READY, VERDICT_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != PAPER_PREP_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if r.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    config = r.get("config")
    if not isinstance(config, dict):
        errors.append("config_missing")
    else:
        guardrails = config.get("no_live_money_guardrails")
        if not isinstance(guardrails, dict):
            errors.append("guardrails_missing")
        else:
            for key in ("no_live_money", "no_real_account", "no_broker_connection",
                        "no_exchange_connection", "no_real_order_execution",
                        "simulated_orders_only", "requires_separate_human_command_to_run"):
                if guardrails.get(key) is not True:
                    errors.append("guardrail_not_true:" + key)
        limits = config.get("risk_limits")
        if not isinstance(limits, dict):
            errors.append("risk_limits_missing")
        else:
            for key in ("allow_leverage", "allow_shorting", "allow_margin"):
                if limits.get(key) is not False:
                    errors.append("risk_limit_not_false:" + key)
            if limits.get("long_only") is not True:
                errors.append("not_long_only")

    must_be_locked = (
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
        "live_gate_locked",
    )
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "starts_paper_trading",
        "connects_broker",
        "connects_exchange",
        "executes_orders",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "runs_optimization",
        "runs_parameter_search",
        "authorizes_live_trading",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_paper_prep_markdown(report: Any) -> str:
    """Render a paper-prep report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    config = r.get("config") or {}
    acct = config.get("paper_account") or {}
    limits = config.get("risk_limits") or {}
    kill = config.get("kill_switch") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Paper-Trading Prep (PREP ONLY, NO LIVE MONEY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Selected variant: " + str(r.get("selected_variant_id", "")))
    lines.append("- Review paper-prep decision: " + str(r.get("review_paper_prep_decision", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    lines.append("## Paper account (SIMULATED)")
    lines.append("- Account type: " + str(acct.get("account_type")))
    lines.append("- Real money: " + str(acct.get("real_money")))
    lines.append("- Starting equity: " + str(acct.get("starting_equity")) + " " + str(acct.get("quote_currency")))
    lines.append("- Universe: " + ", ".join(acct.get("universe") or []))
    lines.append("- Fill model: " + str(acct.get("fill_model")))
    lines.append("")
    lines.append("## Risk limits")
    lines.append("- Long only: " + str(limits.get("long_only"))
                 + " | leverage: " + str(limits.get("allow_leverage"))
                 + " | shorting: " + str(limits.get("allow_shorting")))
    lines.append("- Max per-asset weight: " + _pct(limits.get("max_weight_per_asset"))
                 + " | max gross: " + _pct(limits.get("max_gross_exposure")))
    lines.append("- Trend filter SMA days: " + str(limits.get("trend_filter_sma_days"))
                 + " | min sleeves in trend: " + str(limits.get("min_sleeves_in_trend_to_invest")))
    lines.append("- Daily loss limit: " + _pct(limits.get("daily_loss_limit"))
                 + " | hard drawdown kill: " + _pct(limits.get("hard_drawdown_kill")))
    lines.append("")
    lines.append("## Kill switch")
    lines.append("- On kill: " + str(kill.get("on_kill_action"))
                 + " | auto resume: " + str(kill.get("auto_resume")))
    lines.append("- Drawdown kill: " + _pct(kill.get("drawdown_kill_threshold"))
                 + " | daily-loss halt: " + _pct(kill.get("daily_loss_halt_threshold")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- starts_paper_trading: False (separate human command required)")
    return "\n".join(lines)
