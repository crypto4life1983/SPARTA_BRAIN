"""Tests for the SPARTA Arbitrage Factory V1 Scanner SPEC Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no scanner, no order logic, no file write, no gate is unlocked.
The contract specifies (and does not build) the future read-only scanner."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_factory_v1_research_readiness_contract as ar
import sparta_commander.arbitrage_scanner_spec_contract as sp


# --------------------------------------------------------------------------- #
# ready readiness -> READY spec, scanner not built
# --------------------------------------------------------------------------- #
def test_spec_ready_and_scanner_not_built():
    s = sp.build_arbitrage_scanner_spec()
    assert s["verdict"] == sp.VERDICT_SPEC_READY
    assert s["readiness_verdict"] == ar.VERDICT_READINESS_READY
    assert s["lane"] == "arbitrage_factory_v1"
    assert s["roadmap_seq"] == 1
    assert s["scanner_built_by_this_contract"] is False
    assert s["alerts_and_reports_only"] is True
    assert s["execution_capability_exists"] is False
    assert s["modifies_crypto_d1_lane"] is False
    assert s["blockers"] == []
    assert s["next_required_action"] == "HUMAN_APPROVED_ARBITRAGE_DATA_CONTRACT"


def test_io_spec_is_read_only_and_human_gated():
    io = sp.scanner_io_spec()
    assert io["inputs"]["access"] == "read_only"
    assert io["inputs"]["modified_by_scanner"] is False
    assert io["inputs"]["network_inputs_allowed"] is False
    assert io["inputs"]["credentialed_inputs_allowed"] is False
    assert io["outputs"]["writes_only_under"] == "reports/arbitrage_factory_v1/"
    assert set(io["outputs"]["verdict_states"]) == {"PASS", "WATCH", "FAIL"}
    assert io["outputs"]["existing_reports_modified"] is False
    assert io["run_model"]["per_run_human_approval_required"] is True
    assert io["run_model"]["scheduler_allowed"] is False
    assert io["run_model"]["background_loop_allowed"] is False
    assert io["run_model"]["dry_run_write_false_must_exist"] is True


def test_family_coverage_spans_all_six_families():
    cov = sp.family_coverage()
    assert [f["family_id"] for f in cov] == [
        "ARB_F1_spot_perp_funding_basis",
        "ARB_F2_cross_exchange_basis_monitoring",
        "ARB_F3_btc_eth_sol_pair_spread_alerts",
        "ARB_F4_fee_adjusted_net_edge_scanner",
        "ARB_F5_liquidity_spread_slippage_filters",
        "ARB_F6_pass_watch_fail_report_framework",
    ]
    for f in cov:
        assert f["planned_metrics"]


def test_refusal_conditions_default_to_blocked_writes_nothing():
    refusals = sp.refusal_conditions()
    assert len(refusals) >= 7
    joined = " ".join(refusals)
    assert "data_contract_not_yet_human_approved" in joined
    assert "fee_slippage_model_not_yet_human_approved" in joined
    assert "report_schema_not_yet_frozen" in joined
    assert "per_run_human_approval_absent" in joined
    assert "credentialed_or_authenticated_source" in joined
    assert "network_dependency" in joined
    assert "writes_nothing" in joined


def test_prohibitions_ban_orders_network_credentials_automation():
    prohibitions = sp.scanner_prohibitions()
    joined = " ".join(prohibitions)
    assert "no_network_connections" in joined
    assert "no_credentials" in joined
    assert "no_order_logic" in joined
    assert "no_scheduler" in joined
    assert "read_only" in joined
    assert "alerts_and_reports_are_the_only_outputs" in joined


def test_accessors_return_copies():
    io = sp.scanner_io_spec()
    io["run_model"]["scheduler_allowed"] = True
    assert sp.scanner_io_spec()["run_model"]["scheduler_allowed"] is False
    cov = sp.family_coverage()
    cov[0]["family_id"] = "tampered"
    assert sp.family_coverage()[0]["family_id"] != "tampered"


# --------------------------------------------------------------------------- #
# gating on the readiness contract
# --------------------------------------------------------------------------- #
def test_missing_readiness_blocks():
    s = sp.record_arbitrage_scanner_spec(None)
    assert s["verdict"] == sp.VERDICT_SPEC_BLOCKED
    assert "readiness_spec_missing" in s["blockers"]


def test_invalid_readiness_blocks():
    rs = ar.build_arbitrage_factory_v1_readiness()
    rs["execution_capability_exists"] = True  # breaks the readiness validator
    s = sp.record_arbitrage_scanner_spec(rs)
    assert s["verdict"] == sp.VERDICT_SPEC_BLOCKED
    assert "readiness_spec_invalid" in s["blockers"]


def test_non_alerts_only_lane_blocks():
    rs = ar.build_arbitrage_factory_v1_readiness()
    rs["alerts_and_reports_only"] = False
    s = sp.record_arbitrage_scanner_spec(rs)
    assert s["verdict"] == sp.VERDICT_SPEC_BLOCKED
    assert "lane_constitution_violated" in s["blockers"]


# --------------------------------------------------------------------------- #
# capability posture: nothing real, gates untouched
# --------------------------------------------------------------------------- #
def test_spec_runs_fetches_connects_nothing():
    s = sp.build_arbitrage_scanner_spec()
    for key in (
        "executes", "writes_files", "runs_scanner", "runs_simulation", "runs_backtest",
        "runs_optimization", "fetches_data", "calls_api", "connects_broker",
        "connects_exchange", "uses_real_money", "uses_network", "uses_credentials",
        "contains_order_logic", "authorizes_paper_execution", "authorizes_micro_live",
        "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    ):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True


def test_build_is_deterministic():
    assert sp.build_arbitrage_scanner_spec() == sp.build_arbitrage_scanner_spec()


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    ready = sp.build_arbitrage_scanner_spec()
    blocked = sp.record_arbitrage_scanner_spec(None)
    assert sp.validate_arbitrage_scanner_spec(ready)["valid"] is True
    assert sp.validate_arbitrage_scanner_spec(blocked)["valid"] is True


def test_validate_rejects_input_modification():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_io_spec"]["inputs"]["modified_by_scanner"] = True
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "spec_allows_input_modification" in v["errors"]


def test_validate_rejects_network_or_credentialed_inputs():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_io_spec"]["inputs"]["network_inputs_allowed"] = True
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "spec_allows_network_inputs" in v["errors"]
    s2 = sp.build_arbitrage_scanner_spec()
    s2["scanner_io_spec"]["inputs"]["credentialed_inputs_allowed"] = True
    v2 = sp.validate_arbitrage_scanner_spec(s2)
    assert v2["valid"] is False
    assert "spec_allows_credentialed_inputs" in v2["errors"]


def test_validate_rejects_dropped_per_run_approval_or_automation():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_io_spec"]["run_model"]["per_run_human_approval_required"] = False
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "per_run_approval_dropped" in v["errors"]
    s2 = sp.build_arbitrage_scanner_spec()
    s2["scanner_io_spec"]["run_model"]["scheduler_allowed"] = True
    v2 = sp.validate_arbitrage_scanner_spec(s2)
    assert v2["valid"] is False
    assert "scheduler_allowed" in v2["errors"]


def test_validate_rejects_bad_verdict_states():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_io_spec"]["outputs"]["verdict_states"] = ["BUY", "SELL"]
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "bad_verdict_states" in v["errors"]


def test_validate_rejects_built_scanner_claim():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_built_by_this_contract"] = True
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "scanner_claimed_built" in v["errors"]


def test_validate_rejects_missing_no_order_logic_rule():
    s = sp.build_arbitrage_scanner_spec()
    s["scanner_prohibitions"] = [p for p in s["scanner_prohibitions"]
                                  if "no_order_logic" not in p]
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert ("no_order_logic_rule_missing" in v["errors"]
            or "prohibitions_incomplete" in v["errors"])


def test_validate_rejects_crypto_d1_modification():
    s = sp.build_arbitrage_scanner_spec()
    s["modifies_crypto_d1_lane"] = True
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert "crypto_d1_lane_touched" in v["errors"]


def test_validate_rejects_unlocked_gate():
    s = sp.build_arbitrage_scanner_spec()
    s["micro_live_gate_locked"] = False
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    s = sp.build_arbitrage_scanner_spec()
    s["runs_scanner"] = True
    v = sp.validate_arbitrage_scanner_spec(s)
    assert v["valid"] is False
    assert any("capability_not_false:runs_scanner" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = sp.render_arbitrage_scanner_spec_markdown(sp.build_arbitrage_scanner_spec())
    assert md.startswith("# SPARTA Arbitrage Factory V1 Scanner SPEC")
    assert "BLOCKED writes nothing" in md
    assert "PASS, WATCH, FAIL" in md
    assert "execution: absent by construction" in md
    assert "LOCKED" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert sp.get_arbitrage_scanner_spec_label() == sp.SCANNER_SPEC_LABEL
    assert "READ-ONLY" in sp.SCANNER_SPEC_LABEL
    assert sp.SCANNER_SPEC_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sp.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(sp.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
