"""Tests for the SPARTA Arbitrage Factory V1 Read-Only Data Acquisition Plan.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. The plan fetches nothing; humans acquire public data by hand."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_read_only_data_acquisition_plan_contract as aq
import sparta_commander.arbitrage_staged_data_csv_template_guide_contract as tg


def _entry(**overrides):
    entry = {
        "kind": "funding_rates",
        "method": "manual_export_from_venue_public_page",
        "source_description": "binance public funding-rate history page, "
                              "read by hand, no login",
        "uses_auth": False,
    }
    entry.update(overrides)
    return entry


# --------------------------------------------------------------------------- #
# ready template guide -> READY plan
# --------------------------------------------------------------------------- #
def test_plan_ready_on_real_chain():
    p = aq.build_data_acquisition_plan()
    assert p["verdict"] == aq.VERDICT_ACQ_PLAN_READY
    assert p["blockers"] == []
    assert p["template_guide_verdict"] == tg.VERDICT_TEMPLATE_GUIDE_READY
    assert p["lane"] == "arbitrage_factory_v1"
    assert p["next_required_action"] == (
        "HUMAN_REVIEW_OF_SOURCE_WHITELIST_PROPOSAL")


def test_kind_fields_align_with_seq2_data_contract():
    for kind, fields in aq.MISSING_KIND_FIELDS.items():
        assert fields == dc.STAGED_DATASET_SPECS[kind]["required_columns"], kind
    assert set(aq.MISSING_KIND_FIELDS) == set(dc.STAGED_DATASET_SPECS)


def test_future_endpoint_is_not_allowed_now():
    assert aq.ALLOWED_METHODS["future_no_auth_public_endpoint"][
        "allowed_now"] is False
    allowed_now = [m for m, spec in aq.ALLOWED_METHODS.items()
                   if spec["allowed_now"]]
    assert sorted(allowed_now) == [
        "manual_export_from_venue_public_page",
        "public_csv_download_no_auth",
        "public_webpage_snapshot_manual",
    ]


def test_forbidden_methods_cover_the_core_bans():
    joined = " ".join(aq.FORBIDDEN_METHODS)
    assert "authenticated_or_keyed_api" in joined
    assert "account_statements" in joined
    assert "wallet_order_fill_or_position" in joined
    assert "private_keys" in joined
    assert "paid_private_feeds" in joined
    assert "software_touches_a_network_without_its_own_approval" in joined


def test_whitelist_is_proposed_never_approved():
    assert len(aq.SOURCE_WHITELIST_PROPOSAL) == 5
    for s in aq.SOURCE_WHITELIST_PROPOSAL:
        assert s["status"] == "PROPOSED_FOR_HUMAN_REVIEW"
        assert s["kind"] in dc.STAGED_DATASET_SPECS


def test_rules_cover_transformation_freshness_provenance():
    t = " ".join(aq.TRANSFORMATION_RULES)
    assert "exact_template_headers" in t
    assert "utc_iso8601" in t
    assert "allowed_labels_only" in t
    assert "staging_manifest_pre_check" in t
    f = " ".join(aq.FRESHNESS_RULES)
    assert "7_days" in f and "30_days" in f
    assert "stale_acknowledgement" in f
    pv = " ".join(aq.PROVENANCE_RULES)
    assert "source_label" in pv
    assert "no_login_no_key_no_account" in pv
    assert "never_inside_the_csv_rows" in pv


def test_build_is_deterministic():
    assert aq.build_data_acquisition_plan() == aq.build_data_acquisition_plan()


# --------------------------------------------------------------------------- #
# plan entries: accepted
# --------------------------------------------------------------------------- #
def test_manual_public_entry_accepted():
    r = aq.evaluate_acquisition_plan_entry(_entry())
    assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_ACCEPTED
    assert r["errors"] == []


def test_all_allowed_now_methods_accepted_for_each_kind():
    for kind in aq.MISSING_KIND_FIELDS:
        for method, spec in aq.ALLOWED_METHODS.items():
            if not spec["allowed_now"]:
                continue
            r = aq.evaluate_acquisition_plan_entry(_entry(
                kind=kind, method=method,
                source_description="public venue page, read by hand"))
            assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_ACCEPTED, (kind, method)


# --------------------------------------------------------------------------- #
# plan entries: refused
# --------------------------------------------------------------------------- #
def test_future_endpoint_entry_refused_for_now():
    r = aq.evaluate_acquisition_plan_entry(_entry(
        method="future_no_auth_public_endpoint"))
    assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED
    assert any("method_not_allowed_yet" in e for e in r["errors"])


def test_authenticated_entry_refused():
    r = aq.evaluate_acquisition_plan_entry(_entry(uses_auth=True))
    assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED
    assert "entry_declares_authentication_refused_outright" in r["errors"]


def test_credential_account_trading_sources_refused():
    for bad in ("export via my api_key from binance",
                "download my account statement",
                "wallet balance history export",
                "order_id fill export from the exchange",
                "open position snapshot",
                "private feed from a paid signal group",
                "scrape the page behind my login"):
        r = aq.evaluate_acquisition_plan_entry(_entry(source_description=bad))
        assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED, bad
        assert any("forbidden_source_token" in e for e in r["errors"])


def test_unknown_method_kind_or_missing_source_refused():
    r = aq.evaluate_acquisition_plan_entry(_entry(method="scheduled_scraper"))
    assert r["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED
    r2 = aq.evaluate_acquisition_plan_entry(_entry(kind="live_positions"))
    assert r2["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED
    r3 = aq.evaluate_acquisition_plan_entry(_entry(source_description="  "))
    assert r3["verdict"] == aq.VERDICT_PLAN_ENTRY_REFUSED
    assert aq.evaluate_acquisition_plan_entry(None)["verdict"] == (
        aq.VERDICT_PLAN_ENTRY_REFUSED)


# --------------------------------------------------------------------------- #
# gating on the template guide
# --------------------------------------------------------------------------- #
def test_missing_template_guide_blocks():
    p = aq.record_data_acquisition_plan(None)
    assert p["verdict"] == aq.VERDICT_ACQ_PLAN_BLOCKED
    assert "template_guide_missing" in p["blockers"]


def test_invalid_template_guide_blocks():
    guide = tg.build_csv_template_guide()
    guide["writes_files"] = True
    p = aq.record_data_acquisition_plan(guide)
    assert p["verdict"] == aq.VERDICT_ACQ_PLAN_BLOCKED
    assert "template_guide_invalid" in p["blockers"]


def test_blocked_template_guide_blocks():
    blocked = tg.record_csv_template_guide(None)
    p = aq.record_data_acquisition_plan(blocked)
    assert p["verdict"] == aq.VERDICT_ACQ_PLAN_BLOCKED
    assert "template_guide_not_ready" in p["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_plan_is_inert_on_all_paths():
    plans = [
        aq.build_data_acquisition_plan(),
        aq.record_data_acquisition_plan(None),
    ]
    for p in plans:
        assert p["plan_fetches_nothing"] is True
        assert p["whitelist_is_a_proposal_not_an_approval"] is True
        assert p["data_describes_markets_never_accounts"] is True
        assert p["no_software_touches_a_network_under_this_plan"] is True
        assert p["scanner_remains_blocked"] is True
        assert p["human_review_required"] is True
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
            assert p[key] is False, key
        assert p["paper_trading_gate_locked"] is True
        assert p["micro_live_gate_locked"] is True
        assert p["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert aq.validate_data_acquisition_plan(
        aq.build_data_acquisition_plan())["valid"] is True
    assert aq.validate_data_acquisition_plan(
        aq.record_data_acquisition_plan(None))["valid"] is True


def test_validate_rejects_enabled_future_endpoint():
    p = aq.build_data_acquisition_plan()
    p["allowed_methods"]["future_no_auth_public_endpoint"]["allowed_now"] = True
    v = aq.validate_data_acquisition_plan(p)
    assert v["valid"] is False
    assert "future_endpoint_enabled_without_its_own_contract" in v["errors"]


def test_validate_rejects_weakened_bans_or_approved_whitelist():
    p = aq.build_data_acquisition_plan()
    p["forbidden_methods"] = p["forbidden_methods"][:2]
    v = aq.validate_data_acquisition_plan(p)
    assert v["valid"] is False
    assert "forbidden_methods_weakened" in v["errors"]
    p2 = aq.build_data_acquisition_plan()
    p2["source_whitelist_proposal"][0]["status"] = "APPROVED"
    v2 = aq.validate_data_acquisition_plan(p2)
    assert v2["valid"] is False
    assert "whitelist_entry_claims_approval" in v2["errors"]


def test_validate_rejects_fetch_or_network_claims():
    p = aq.build_data_acquisition_plan()
    p["plan_fetches_nothing"] = False
    v = aq.validate_data_acquisition_plan(p)
    assert v["valid"] is False
    assert "plan_claims_to_fetch" in v["errors"]
    p2 = aq.build_data_acquisition_plan()
    p2["no_software_touches_a_network_under_this_plan"] = False
    v2 = aq.validate_data_acquisition_plan(p2)
    assert v2["valid"] is False
    assert "network_allowed" in v2["errors"]


def test_validate_rejects_diverged_fields_or_rules():
    p = aq.build_data_acquisition_plan()
    p["missing_kind_fields"]["funding_rates"] = ["timestamp_utc"]
    v = aq.validate_data_acquisition_plan(p)
    assert v["valid"] is False
    assert "kind_fields_diverge_from_data_contract" in v["errors"]
    p2 = aq.build_data_acquisition_plan()
    p2["provenance_rules"] = p2["provenance_rules"][:1]
    v2 = aq.validate_data_acquisition_plan(p2)
    assert v2["valid"] is False
    assert "provenance_rules_tampered" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    p = aq.build_data_acquisition_plan()
    p["micro_live_gate_locked"] = False
    v = aq.validate_data_acquisition_plan(p)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    p2 = aq.build_data_acquisition_plan()
    p2["fetches_data"] = True
    v2 = aq.validate_data_acquisition_plan(p2)
    assert v2["valid"] is False
    assert any("capability_not_false:fetches_data" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = aq.render_data_acquisition_plan_markdown(
        aq.build_data_acquisition_plan())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Read-Only Data Acquisition Plan")
    assert "FETCHES NOTHING" in md
    assert "PROPOSAL, not an approval" in md
    assert "NOT YET (own contract)" in md
    assert "LOCKED" in md
    md2 = aq.render_data_acquisition_plan_markdown(
        aq.record_data_acquisition_plan(None))
    assert "BLOCKED defines nothing usable" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_plan_label():
    assert aq.get_data_acquisition_plan_label() == aq.ACQ_LABEL
    assert "READ-ONLY" in aq.ACQ_LABEL
    assert "FETCHES NOTHING" in aq.ACQ_LABEL
    assert aq.ACQ_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in aq.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_filesystem_or_credential_modules():
    with open(aq.__file__, "r", encoding="utf-8") as fh:
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
