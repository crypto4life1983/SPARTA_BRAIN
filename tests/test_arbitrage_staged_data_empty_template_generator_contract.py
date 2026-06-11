"""Tests for the SPARTA Arbitrage Factory V1 Empty Template Generator Contract.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. The contract PLANS header-only files and creates nothing."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_staged_data_csv_template_guide_contract as tg
import sparta_commander.arbitrage_staged_data_empty_template_generator_contract as eg


# --------------------------------------------------------------------------- #
# ready template guide -> READY generator contract
# --------------------------------------------------------------------------- #
def test_generator_ready_on_real_chain():
    c = eg.build_empty_template_generator()
    assert c["verdict"] == eg.VERDICT_GENERATOR_READY
    assert c["blockers"] == []
    assert c["template_guide_verdict"] == tg.VERDICT_TEMPLATE_GUIDE_READY
    assert c["staging_folder"] == "data/arbitrage_factory_v1/staged/"
    assert c["next_required_action"] == (
        "HUMAN_APPROVED_EMPTY_TEMPLATE_FILE_CREATION")


def test_headers_align_with_template_guide():
    c = eg.build_empty_template_generator()
    for kind, template in tg.CSV_TEMPLATES.items():
        assert c["headers_by_kind"][kind] == template["header"], kind


def test_generation_rules_cover_the_core_set():
    joined = " ".join(eg.GENERATION_RULES)
    assert "exactly_one_line_the_template_header" in joined
    assert "no_sample_rows_no_market_values" in joined
    assert "data_arbitrage_factory_v1_staged" in joined
    assert "filename_validator" in joined
    assert "never_overwritten_without_a_separate_approval" in joined
    assert "human_fills_rows_by_hand" in joined
    assert "plans_only_actual_creation_needs_its_own_approval" in joined


def test_build_is_deterministic():
    assert eg.build_empty_template_generator() == eg.build_empty_template_generator()


# --------------------------------------------------------------------------- #
# generation plans: accepted
# --------------------------------------------------------------------------- #
def test_valid_plan_accepted_header_only():
    plan = eg.plan_empty_template_generation(
        ["funding_BTC_binance.csv", "fees_kraken.csv"])
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_ACCEPTED
    assert plan["errors"] == []
    assert plan["plan_creates_no_files"] is True
    assert plan["execution_requires_separate_human_approval"] is True
    assert len(plan["planned_files"]) == 2
    for f in plan["planned_files"]:
        assert f["content_is_header_only"] is True
        assert f["action"] == "CREATE_HEADER_ONLY_PLACEHOLDER"
        assert f["destination"].startswith("data/arbitrage_factory_v1/staged/")
        assert "\n" not in f["content"]  # exactly one line
        assert f["content"] == tg.CSV_TEMPLATES[f["kind"]]["header"]


def test_plan_for_all_five_kinds_accepted():
    names = ["funding_BTC_binance.csv", "basis_ETH_bybit.csv",
             "quotes_SOL_okx.csv", "fees_kraken.csv", "depth_BTC_coinbase.csv"]
    plan = eg.plan_empty_template_generation(names)
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_ACCEPTED
    assert sorted(f["kind"] for f in plan["planned_files"]) == sorted(
        tg.CSV_TEMPLATES)


def test_plan_is_deterministic():
    names = ["funding_BTC_binance.csv"]
    assert eg.plan_empty_template_generation(names) == (
        eg.plan_empty_template_generation(names))


# --------------------------------------------------------------------------- #
# generation plans: refused
# --------------------------------------------------------------------------- #
def test_overwrite_refused():
    plan = eg.plan_empty_template_generation(
        ["funding_BTC_binance.csv"],
        existing_filenames=["funding_BTC_binance.csv"])
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED
    assert any("file_already_exists_overwrite_needs_separate_approval" in e
               for e in plan["refused_files"]["funding_BTC_binance.csv"])
    assert plan["planned_files"] == []


def test_path_traversal_and_subdirs_refused():
    for bad in ("../funding_BTC_binance.csv", "sub/funding_BTC_binance.csv",
                "..\\\\funding_BTC_binance.csv"):
        plan = eg.plan_empty_template_generation([bad])
        assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED, bad


def test_market_data_filled_request_refused():
    plan = eg.plan_empty_template_generation([
        {"filename": "funding_BTC_binance.csv",
         "rows": ["2026-06-10T00:00:00Z,BTC,binance,0.0001,67000"]}])
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED
    assert any("request_carries_content_only_bare_filenames_allowed" in e
               for e in plan["refused_files"]["funding_BTC_binance.csv"])


def test_bad_labels_and_duplicates_refused():
    plan = eg.plan_empty_template_generation(["funding_DOGE_binance.csv"])
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED
    plan2 = eg.plan_empty_template_generation(
        ["fees_kraken.csv", "fees_kraken.csv"])
    assert plan2["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED
    assert any("duplicate_request" in e
               for e in plan2["refused_files"]["fees_kraken.csv"])
    plan3 = eg.plan_empty_template_generation([])
    assert plan3["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED


def test_one_bad_request_refuses_whole_plan():
    plan = eg.plan_empty_template_generation(
        ["fees_kraken.csv", "positions_BTC_binance.csv"])
    assert plan["verdict"] == eg.VERDICT_GENERATION_PLAN_REFUSED
    assert plan["planned_files"] == []


# --------------------------------------------------------------------------- #
# gating on the template guide
# --------------------------------------------------------------------------- #
def test_missing_or_blocked_template_guide_blocks():
    c = eg.record_empty_template_generator(None)
    assert c["verdict"] == eg.VERDICT_GENERATOR_BLOCKED
    assert "template_guide_missing" in c["blockers"]
    blocked = tg.record_csv_template_guide(None)
    c2 = eg.record_empty_template_generator(blocked)
    assert c2["verdict"] == eg.VERDICT_GENERATOR_BLOCKED
    assert "template_guide_not_ready" in c2["blockers"]


def test_invalid_template_guide_blocks():
    guide = tg.build_csv_template_guide()
    guide["writes_files"] = True
    c = eg.record_empty_template_generator(guide)
    assert c["verdict"] == eg.VERDICT_GENERATOR_BLOCKED
    assert "template_guide_invalid" in c["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_contract_is_inert_on_all_paths():
    contracts = [
        eg.build_empty_template_generator(),
        eg.record_empty_template_generator(None),
    ]
    for c in contracts:
        assert c["plan_creates_no_files"] is True
        assert c["generated_files_would_be_header_only"] is True
        assert c["no_market_values_ever_generated"] is True
        assert c["overwrite_requires_separate_approval"] is True
        assert c["scanner_remains_blocked"] is True
        assert c["human_review_required"] is True
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
            assert c[key] is False, key
        assert c["paper_trading_gate_locked"] is True
        assert c["micro_live_gate_locked"] is True
        assert c["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert eg.validate_empty_template_generator(
        eg.build_empty_template_generator())["valid"] is True
    assert eg.validate_empty_template_generator(
        eg.record_empty_template_generator(None))["valid"] is True


def test_validate_rejects_diverged_headers_or_moved_folder():
    c = eg.build_empty_template_generator()
    c["headers_by_kind"]["funding_rates"] = "timestamp_utc,symbol"
    v = eg.validate_empty_template_generator(c)
    assert v["valid"] is False
    assert "headers_diverge_from_template_guide" in v["errors"]
    c2 = eg.build_empty_template_generator()
    c2["staging_folder"] = "C:/anywhere/"
    v2 = eg.validate_empty_template_generator(c2)
    assert v2["valid"] is False
    assert "staging_folder_moved" in v2["errors"]


def test_validate_rejects_dropped_rules():
    for flag, err in (
        ("plan_creates_no_files", "plan_claims_to_create_files"),
        ("generated_files_would_be_header_only", "header_only_rule_dropped"),
        ("no_market_values_ever_generated", "market_values_allowed"),
        ("overwrite_requires_separate_approval", "overwrite_allowed"),
        ("scanner_remains_blocked", "scanner_block_dropped"),
    ):
        c = eg.build_empty_template_generator()
        c[flag] = False
        v = eg.validate_empty_template_generator(c)
        assert v["valid"] is False, flag
        assert err in v["errors"], flag


def test_validate_rejects_unlocked_gate_or_capability():
    c = eg.build_empty_template_generator()
    c["micro_live_gate_locked"] = False
    v = eg.validate_empty_template_generator(c)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    c2 = eg.build_empty_template_generator()
    c2["writes_files"] = True
    v2 = eg.validate_empty_template_generator(c2)
    assert v2["valid"] is False
    assert any("capability_not_false:writes_files" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = eg.render_empty_template_generator_markdown(
        eg.build_empty_template_generator())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Empty Template Generator (PLAN ONLY)")
    assert "PLANS only" in md
    assert "header-only" in md
    assert "scanner remains BLOCKED" in md
    assert "LOCKED" in md
    md2 = eg.render_empty_template_generator_markdown(
        eg.record_empty_template_generator(None))
    assert "BLOCKED plans nothing" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_plan_label():
    assert eg.get_empty_template_generator_label() == eg.GEN_LABEL
    assert "READ-ONLY" in eg.GEN_LABEL
    assert "CREATES NO FILE" in eg.GEN_LABEL
    assert eg.GEN_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in eg.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_filesystem_or_credential_modules():
    with open(eg.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas",
              "pathlib", "os", "io"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
