"""Tests for the SPARTA Arbitrage Factory V1 Alert/Report Schema Contract.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. Alerts are research only, never trade signals; verdicts must agree with
the seq-3 model and net edges must match their cost breakdowns."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_alert_report_schema_contract as rs
import sparta_commander.arbitrage_fee_slippage_model_contract as fm


def _alert(**overrides):
    record = {
        "alert_id": "alert_btc_basis_0001",
        "timestamp_utc": "2026-06-10T00:00:00Z",
        "family_id": "ARB_F1_spot_perp_funding_basis",
        "symbol": "BTC",
        "venues": ["binance", "bybit"],
        "gross_edge_bps": 30.0,
        "taker_fee_bps": 5.0,
        "spread_cost_bps": 2.0,
        "slippage_bps": 1.5,
        "funding_adjustment_bps": 1.0,
        "withdrawal_amortization_bps": 0.5,
        "net_edge_bps": 15.0,
        "verdict": "PASS",
        "data_staleness_days": 1,
        "evidence_label": "[evidence: staged funding/basis csv 2026-06]",
        "summary": "fee-adjusted basis carry observed across venues",
        "alert_is_research_only_not_a_trade_signal": True,
        "human_action_needed": True,
        "disclaimer": rs.MANDATORY_DISCLAIMER,
    }
    record.update(overrides)
    return record


# --------------------------------------------------------------------------- #
# ready model -> READY schema
# --------------------------------------------------------------------------- #
def test_schema_ready_on_real_chain():
    s = rs.build_arbitrage_alert_report_schema()
    assert s["verdict"] == rs.VERDICT_REPORT_SCHEMA_READY
    assert s["blockers"] == []
    assert s["fee_slippage_model_verdict"] == fm.VERDICT_MODEL_READY
    assert s["lane"] == "arbitrage_factory_v1"
    assert s["roadmap_seq"] == 4
    assert s["next_required_action"] == "HUMAN_APPROVED_LANE_REVIEW_CONTRACT"


def test_schema_surface_is_frozen():
    s = rs.build_arbitrage_alert_report_schema()
    assert tuple(s["alert_verdict_states"]) == ("PASS", "WATCH", "FAIL")
    assert s["reports_root"] == "reports/arbitrage_factory_v1/"
    assert "alert_id" in s["alert_required_fields"]
    assert "disclaimer" in s["alert_required_fields"]
    for cost in rs.ALERT_COST_FIELDS:
        assert cost in s["alert_required_fields"]
    rules = " ".join(s["report_file_rules"])
    assert "append_only" in rules
    assert "one_report_per_human_approved_run" in rules
    assert "blocked_or_refused_runs_write_nothing" in rules


def test_build_is_deterministic():
    assert (rs.build_arbitrage_alert_report_schema()
            == rs.build_arbitrage_alert_report_schema())


# --------------------------------------------------------------------------- #
# alert records: a valid alert is accepted
# --------------------------------------------------------------------------- #
def test_valid_pass_alert_accepted():
    v = rs.validate_alert_record(_alert())
    assert v["acceptable"] is True
    assert v["errors"] == []


def test_valid_watch_and_fail_alerts_accepted():
    # gross 20 -> net 5.0 => WATCH per the seq-3 thresholds
    watch = _alert(gross_edge_bps=20.0, net_edge_bps=5.0, verdict="WATCH")
    assert rs.validate_alert_record(watch)["acceptable"] is True
    # gross 10 -> net -5.0 => FAIL
    fail = _alert(gross_edge_bps=10.0, net_edge_bps=-5.0, verdict="FAIL")
    assert rs.validate_alert_record(fail)["acceptable"] is True


# --------------------------------------------------------------------------- #
# honesty checks: verdict and net edge cannot lie
# --------------------------------------------------------------------------- #
def test_verdict_must_agree_with_seq3_model():
    # net edge of -5.0 is FAIL per the model; calling it PASS is refused
    lying = _alert(gross_edge_bps=10.0, net_edge_bps=-5.0, verdict="PASS")
    v = rs.validate_alert_record(lying)
    assert v["acceptable"] is False
    assert "verdict_disagrees_with_seq3_model_classification" in v["errors"]


def test_net_edge_must_match_cost_breakdown():
    # quietly dropping a cost from the arithmetic is refused
    padded = _alert(net_edge_bps=20.0)  # true net is 15.0
    v = rs.validate_alert_record(padded)
    assert v["acceptable"] is False
    assert "net_edge_does_not_match_cost_breakdown" in v["errors"]


def test_verdict_agreement_uses_model_threshold():
    # exactly at the PASS bar
    at_bar = _alert(gross_edge_bps=25.0, net_edge_bps=10.0, verdict="PASS")
    assert rs.validate_alert_record(at_bar)["acceptable"] is True
    just_below = _alert(gross_edge_bps=24.9, net_edge_bps=9.9, verdict="PASS")
    v = rs.validate_alert_record(just_below)
    assert v["acceptable"] is False


# --------------------------------------------------------------------------- #
# refusals: unsafe content, fields, labels, flags
# --------------------------------------------------------------------------- #
def test_trade_instruction_language_refused():
    for bad in ("strong edge, buy now", "go long the basis",
                "place order on the spread", "enter position immediately"):
        v = rs.validate_alert_record(_alert(summary=bad))
        assert v["acceptable"] is False, bad
        assert any("forbidden_alert_content" in e for e in v["errors"])


def test_credential_account_position_fields_refused():
    for bad_key in ("api_key", "account_balance", "order_id", "open_position",
                    "leverage"):
        v = rs.validate_alert_record(_alert(**{bad_key: "x"}))
        assert v["acceptable"] is False, bad_key
        assert any("forbidden_alert_field" in e for e in v["errors"])


def test_unknown_symbol_or_venue_refused():
    v = rs.validate_alert_record(_alert(symbol="DOGE"))
    assert v["acceptable"] is False
    assert "symbol_not_in_allowed_labels" in v["errors"]
    v2 = rs.validate_alert_record(_alert(venues=["binance", "my_private_venue"]))
    assert v2["acceptable"] is False
    assert "venues_not_in_allowed_labels" in v2["errors"]
    v3 = rs.validate_alert_record(_alert(venues=[]))
    assert v3["acceptable"] is False


def test_dropped_flags_or_disclaimer_refused():
    v = rs.validate_alert_record(
        _alert(alert_is_research_only_not_a_trade_signal=False))
    assert v["acceptable"] is False
    assert "research_only_flag_dropped" in v["errors"]
    v2 = rs.validate_alert_record(_alert(human_action_needed=False))
    assert v2["acceptable"] is False
    assert "human_action_flag_dropped" in v2["errors"]
    v3 = rs.validate_alert_record(_alert(disclaimer="trust me"))
    assert v3["acceptable"] is False
    assert "disclaimer_missing_or_altered" in v3["errors"]


def test_missing_fields_and_bad_numbers_refused():
    incomplete = _alert()
    del incomplete["slippage_bps"]
    v = rs.validate_alert_record(incomplete)
    assert v["acceptable"] is False
    assert "missing_required_field:slippage_bps" in v["errors"]
    v2 = rs.validate_alert_record(_alert(net_edge_bps="fifteen"))
    assert v2["acceptable"] is False
    assert "non_numeric:net_edge_bps" in v2["errors"]
    v3 = rs.validate_alert_record(_alert(data_staleness_days=-1))
    assert v3["acceptable"] is False
    assert "staleness_missing_or_negative" in v3["errors"]
    assert rs.validate_alert_record(None)["acceptable"] is False


def test_bad_verdict_state_refused():
    v = rs.validate_alert_record(_alert(verdict="BUY"))
    assert v["acceptable"] is False
    assert "verdict_outside_closed_set" in v["errors"]


# --------------------------------------------------------------------------- #
# gating on the seq-3 model
# --------------------------------------------------------------------------- #
def test_missing_model_blocks():
    s = rs.record_arbitrage_alert_report_schema(None)
    assert s["verdict"] == rs.VERDICT_REPORT_SCHEMA_BLOCKED
    assert "fee_slippage_model_missing" in s["blockers"]


def test_invalid_model_blocks():
    model = fm.build_arbitrage_fee_slippage_model()
    model["contains_order_logic"] = True
    s = rs.record_arbitrage_alert_report_schema(model)
    assert s["verdict"] == rs.VERDICT_REPORT_SCHEMA_BLOCKED
    assert "fee_slippage_model_invalid" in s["blockers"]


def test_blocked_model_blocks():
    blocked = fm.record_arbitrage_fee_slippage_model(None)
    s = rs.record_arbitrage_alert_report_schema(blocked)
    assert s["verdict"] == rs.VERDICT_REPORT_SCHEMA_BLOCKED
    assert "fee_slippage_model_not_ready" in s["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_schema_is_inert_on_all_paths():
    schemas = [
        rs.build_arbitrage_alert_report_schema(),
        rs.record_arbitrage_alert_report_schema(None),
    ]
    for s in schemas:
        assert s["alerts_are_research_only_never_trade_signals"] is True
        assert s["verdicts_must_agree_with_seq3_model"] is True
        assert s["net_edge_must_match_cost_breakdown"] is True
        assert s["schema_writes_no_reports"] is True
        assert s["output_is_schema_readiness_only"] is True
        assert s["human_review_required"] is True
        for key in (
            "executes", "writes_files", "writes_reports", "sends_notifications",
            "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "starts_daemon",
            "starts_background_worker", "runs_loop", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert s[key] is False, key
        assert s["paper_trading_gate_locked"] is True
        assert s["micro_live_gate_locked"] is True
        assert s["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation of the schema contract itself
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert rs.validate_arbitrage_alert_report_schema(
        rs.build_arbitrage_alert_report_schema())["valid"] is True
    assert rs.validate_arbitrage_alert_report_schema(
        rs.record_arbitrage_alert_report_schema(None))["valid"] is True


def test_validate_rejects_tampered_states_or_fields():
    s = rs.build_arbitrage_alert_report_schema()
    s["alert_verdict_states"] = ["PASS", "WATCH", "FAIL", "BUY"]
    v = rs.validate_arbitrage_alert_report_schema(s)
    assert v["valid"] is False
    assert "verdict_states_tampered" in v["errors"]
    s2 = rs.build_arbitrage_alert_report_schema()
    s2["alert_required_fields"] = [
        f for f in s2["alert_required_fields"] if f != "disclaimer"]
    v2 = rs.validate_arbitrage_alert_report_schema(s2)
    assert v2["valid"] is False
    assert "required_fields_tampered" in v2["errors"]


def test_validate_rejects_moved_reports_root_or_weakened_content():
    s = rs.build_arbitrage_alert_report_schema()
    s["reports_root"] = "C:/anywhere/"
    v = rs.validate_arbitrage_alert_report_schema(s)
    assert v["valid"] is False
    assert "reports_root_moved" in v["errors"]
    s2 = rs.build_arbitrage_alert_report_schema()
    s2["forbidden_alert_content"] = [
        t for t in s2["forbidden_alert_content"] if t != "buy now"]
    v2 = rs.validate_arbitrage_alert_report_schema(s2)
    assert v2["valid"] is False
    assert "forbidden_content_weakened" in v2["errors"]


def test_validate_rejects_dropped_honesty_or_disclaimer():
    s = rs.build_arbitrage_alert_report_schema()
    s["verdicts_must_agree_with_seq3_model"] = False
    v = rs.validate_arbitrage_alert_report_schema(s)
    assert v["valid"] is False
    assert "model_agreement_dropped" in v["errors"]
    s2 = rs.build_arbitrage_alert_report_schema()
    s2["mandatory_disclaimer"] = "research-ish"
    v2 = rs.validate_arbitrage_alert_report_schema(s2)
    assert v2["valid"] is False
    assert "disclaimer_tampered" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    s = rs.build_arbitrage_alert_report_schema()
    s["live_gate_locked"] = False
    v = rs.validate_arbitrage_alert_report_schema(s)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    s2 = rs.build_arbitrage_alert_report_schema()
    s2["writes_reports"] = True
    v2 = rs.validate_arbitrage_alert_report_schema(s2)
    assert v2["valid"] is False
    assert any("capability_not_false:writes_reports" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = rs.render_arbitrage_alert_report_schema_markdown(
        rs.build_arbitrage_alert_report_schema())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Alert/Report Schema (SCHEMA ONLY)")
    assert "NEVER trade signals" in md
    assert rs.MANDATORY_DISCLAIMER in md
    assert "LOCKED" in md
    md2 = rs.render_arbitrage_alert_report_schema_markdown(
        rs.record_arbitrage_alert_report_schema(None))
    assert "BLOCKED defines nothing usable" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_schema_label():
    assert rs.get_arbitrage_alert_report_schema_label() == rs.REPORT_SCHEMA_LABEL
    assert "READ-ONLY" in rs.REPORT_SCHEMA_LABEL
    assert "SCHEMA ONLY" in rs.REPORT_SCHEMA_LABEL
    assert rs.REPORT_SCHEMA_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rs.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(rs.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
