"""Tests for the Crypto-D1 V2 Paper-Trading Prep Contract (PREP ONLY, NO LIVE MONEY).
Every variant report consumed here is a FAKE in-memory JSON written under tmp_path; no
network, no credentials, no real data, no broker, no exchange, no paper run is started,
no gate is unlocked."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract as pp
import sparta_commander.strategy_factory_crypto_d1_variant_backtest_runner as vr


def _variant(vid, *, max_dd, sharpe=1.10, total_return=2.0, trading_days=2128,
             eligible, blockers=None, beats_floor=None):
    if beats_floor is None:
        beats_floor = max_dd >= -0.50
    return {
        "variant_id": vid,
        "description": vid,
        "controls": ["trend_filter"],
        "performance": {
            "max_drawdown": max_dd,
            "sharpe_ratio": sharpe,
            "total_return": total_return,
            "trading_days": trading_days,
            "cagr": 0.50,
        },
        "beats_drawdown_floor": beats_floor,
        "promotion_decision": "PROMOTE_TO_PAPER_PREP" if eligible else "DO_NOT_PROMOTE_TO_PAPER_YET",
        "eligible_for_paper_prep": eligible,
        "eligibility_blockers": list(blockers or []),
    }


def _report_v2_eligible():
    """Mirrors the real run: only V2 clears the floor and is paper-prep eligible."""
    return {
        "verdict": vr.VERDICT_VARIANTS_COMPLETE,
        "variant_count": 5,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V2_trend_plus_cash_regime", max_dd=-0.4816, sharpe=1.10,
                     total_return=11.5528, eligible=True),
            _variant("V3_voltarget_concentration_cap", max_dd=-0.8512, sharpe=0.99,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V4_monthly_rebalance_capped", max_dd=-0.8438, sharpe=1.04,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V5_full_risk_managed", max_dd=-0.5085, sharpe=1.07,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
        ],
        "eligible_for_paper_prep": ["V2_trend_plus_cash_regime"],
        "any_variant_eligible_for_paper_prep": True,
    }


def _report_none_eligible():
    return {
        "verdict": vr.VERDICT_VARIANTS_COMPLETE,
        "variant_count": 1,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
        ],
        "eligible_for_paper_prep": [],
        "any_variant_eligible_for_paper_prep": False,
    }


def _stage_report(tmp_path, report):
    rep_dir = tmp_path / "reports" / "crypto_d1_variant_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "variant_backtest_report.json").write_text(
        json.dumps(report), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# config pins V2 and its pre-registered rule parameters
# --------------------------------------------------------------------------- #
def test_config_pins_v2_and_its_parameters():
    c = pp.build_paper_prep_config()
    assert c["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert c["risk_limits"]["trend_filter_sma_days"] == 200
    assert c["risk_limits"]["min_sleeves_in_trend_to_invest"] == 2
    assert c["risk_limits"]["total_sleeves"] == 3
    # the pinned strategy parameters come from the V2 manifest
    assert isinstance(c["strategy_parameters"], dict) and c["strategy_parameters"]
    assert "trend_filter" in c["controls"]


def test_account_is_simulated_no_real_money():
    a = pp.paper_account_assumptions()
    assert a["account_type"] == "SIMULATED_PAPER"
    assert a["real_money"] is False
    assert a["broker_connected"] is False
    assert a["exchange_connected"] is False
    assert a["data_source"] == "QA_PASSED_LOCAL_CSV_ONLY"
    assert a["universe"] == ["BTC", "ETH", "SOL"]


def test_risk_limits_long_only_no_leverage():
    r = pp.risk_limits()
    assert r["long_only"] is True
    assert r["allow_leverage"] is False
    assert r["allow_shorting"] is False
    assert r["allow_margin"] is False
    assert r["max_weight_per_asset"] == 0.50


def test_kill_switch_flattens_and_needs_human():
    k = pp.kill_switch_rules()
    assert k["on_kill_action"] == "FLATTEN_TO_CASH_AND_HALT"
    assert k["auto_resume"] is False
    assert k["requires_human_to_resume"] is True
    assert k["manual_kill_enabled"] is True


def test_no_live_money_guardrails_all_true():
    g = pp.no_live_money_guardrails()
    for key in (
        "no_live_money", "no_real_account", "no_broker_connection",
        "no_exchange_connection", "no_network", "no_credentials",
        "no_real_order_execution", "simulated_orders_only",
        "requires_separate_human_command_to_run", "live_gate_locked",
        "micro_live_gate_locked",
    ):
        assert g[key] is True


def test_accessors_return_fresh_copies():
    a1 = pp.paper_account_assumptions()
    a1["universe"].append("DOGE")
    a1["account_type"] = "MUTATED"
    assert pp.paper_account_assumptions()["universe"] == ["BTC", "ETH", "SOL"]
    assert pp.paper_account_assumptions()["account_type"] == "SIMULATED_PAPER"
    log = pp.logging_requirements()
    log["required_log_fields"].append("x")
    assert "x" not in pp.logging_requirements()["required_log_fields"]


# --------------------------------------------------------------------------- #
# readiness: READY only when the review APPROVED paper prep for exactly V2
# --------------------------------------------------------------------------- #
def test_ready_when_v2_review_approved(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    assert d["verdict"] == pp.VERDICT_READY
    assert d["blockers"] == []
    assert d["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert d["review_paper_prep_decision"] == "APPROVE_PAPER_PREP_ONLY"
    assert d["next_required_action"] == pp.NEXT_REQUIRED_ACTION


def test_not_ready_when_no_eligible_variant(tmp_path):
    _stage_report(tmp_path, _report_none_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    assert d["verdict"] == pp.VERDICT_NOT_READY
    assert "variant_paper_prep_not_approved" in d["blockers"]


def test_not_ready_when_report_missing(tmp_path):
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    assert d["verdict"] == pp.VERDICT_NOT_READY
    assert d["blockers"]


# --------------------------------------------------------------------------- #
# readiness starts / connects / unlocks NOTHING
# --------------------------------------------------------------------------- #
def test_readiness_unlocks_nothing(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    assert d["starts_paper_trading"] is False
    assert d["connects_broker"] is False
    assert d["connects_exchange"] is False
    assert d["executes_orders"] is False
    assert d["uses_real_money"] is False
    assert d["uses_network"] is False
    assert d["uses_credentials"] is False
    assert d["runs_optimization"] is False
    assert d["runs_parameter_search"] is False
    assert d["authorizes_live_trading"] is False
    assert d["unlocks_downstream_gate"] is False
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_not_ready(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    ready = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    not_ready = pp.check_paper_prep_readiness(repo_root=str(tmp_path / "missing"))
    assert pp.validate_paper_prep_report(ready)["valid"] is True
    assert pp.validate_paper_prep_report(not_ready)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    d["micro_live_gate_locked"] = False
    v = pp.validate_paper_prep_report(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_real_money_capability(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    d["uses_real_money"] = True
    v = pp.validate_paper_prep_report(d)
    assert v["valid"] is False
    assert any("capability_not_false:uses_real_money" in e for e in v["errors"])


def test_validate_rejects_leverage_in_config(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    d["config"]["risk_limits"]["allow_leverage"] = True
    v = pp.validate_paper_prep_report(d)
    assert v["valid"] is False
    assert any("risk_limit_not_false:allow_leverage" in e for e in v["errors"])


def test_validate_rejects_guardrail_off(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    d = pp.check_paper_prep_readiness(repo_root=str(tmp_path))
    d["config"]["no_live_money_guardrails"]["no_live_money"] = False
    v = pp.validate_paper_prep_report(d)
    assert v["valid"] is False
    assert any("guardrail_not_true:no_live_money" in e for e in v["errors"])


def test_validate_rejects_non_dict():
    v = pp.validate_paper_prep_report(None)
    assert v["valid"] is False
    assert "report_not_a_dict" in v["errors"]


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _stage_report(tmp_path, _report_v2_eligible())
    md = pp.render_paper_prep_markdown(pp.check_paper_prep_readiness(repo_root=str(tmp_path)))
    assert md.startswith("# Crypto-D1 V2 Paper-Trading Prep")
    assert "NO LIVE MONEY" in md
    assert "V2_trend_plus_cash_regime" in md
    assert "LOCKED" in md


def test_label_is_prep_only():
    assert pp.get_paper_trading_prep_label() == pp.PAPER_PREP_LABEL
    assert "PREP ONLY" in pp.PAPER_PREP_LABEL


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(pp.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {
        "urllib",
        "requests",
        "socket",
        "http",
        "ftplib",
        "ccxt",
        "databento",
        "dotenv",
        "smtplib",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
