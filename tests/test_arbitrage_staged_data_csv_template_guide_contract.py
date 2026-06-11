"""Tests for the SPARTA Arbitrage Factory V1 Staged-Data CSV Template Guide.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. Templates are text only; the operator places files by hand."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_staged_data_csv_template_guide_contract as tg
import sparta_commander.arbitrage_staged_data_preparation_rules_contract as pr


# --------------------------------------------------------------------------- #
# ready prep rules -> READY guide
# --------------------------------------------------------------------------- #
def test_guide_ready_on_real_chain():
    g = tg.build_csv_template_guide()
    assert g["verdict"] == tg.VERDICT_TEMPLATE_GUIDE_READY
    assert g["blockers"] == []
    assert g["prep_rules_verdict"] == pr.VERDICT_PREP_RULES_READY
    assert g["staging_folder"] == "data/arbitrage_factory_v1/staged/"
    assert g["next_required_action"] == "HUMAN_PLACES_STAGED_DATA_MANUALLY"


def test_templates_cover_all_five_kinds():
    g = tg.build_csv_template_guide()
    assert set(g["csv_templates"]) == set(dc.STAGED_DATASET_SPECS)


def test_template_headers_match_seq2_required_columns_exactly():
    for kind, spec in dc.STAGED_DATASET_SPECS.items():
        template = tg.CSV_TEMPLATES[kind]
        assert template["header"] == ",".join(spec["required_columns"]), kind


def test_template_filename_examples_pass_the_prep_rules_validator():
    for kind, template in tg.CSV_TEMPLATES.items():
        check = pr.validate_staged_file_name(template["filename_example"])
        assert check["acceptable"] is True, kind
        assert check["kind"] == kind


def test_template_sample_rows_match_header_field_counts():
    for kind, template in tg.CSV_TEMPLATES.items():
        columns = len(template["header"].split(","))
        assert template["sample_rows"], kind
        for row in template["sample_rows"]:
            assert len(row.split(",")) == columns, (kind, row)


def test_template_sample_rows_use_allowed_labels_and_utc_timestamps():
    for kind, template in tg.CSV_TEMPLATES.items():
        for row in template["sample_rows"]:
            fields = row.split(",")
            if kind != "fee_schedule":
                assert fields[0].endswith("Z"), (kind, row)
                assert fields[1] in dc.ALLOWED_SYMBOLS, (kind, row)
                assert fields[2] in dc.ALLOWED_VENUE_LABELS, (kind, row)
            else:
                assert fields[0] in dc.ALLOWED_VENUE_LABELS, (kind, row)
                assert fields[1] in dc.ALLOWED_SYMBOLS, (kind, row)


def test_templates_contain_no_forbidden_tokens():
    for kind, template in tg.CSV_TEMPLATES.items():
        joined = (template["header"] + " " + " ".join(template["sample_rows"])
                  + " " + template["notes"]).lower()
        for token in dc.FORBIDDEN_FIELD_TOKENS:
            assert token not in joined, (kind, token)


def test_a_filled_template_passes_the_manifest_validator():
    # the guide and the prep rules agree end to end
    entries = []
    for kind, template in tg.CSV_TEMPLATES.items():
        entry = {
            "filename": template["filename_example"],
            "kind": kind,
            "columns": template["header"].split(","),
        }
        if kind != "fee_schedule":
            first = template["sample_rows"][0].split(",")[0]
            last = template["sample_rows"][-1].split(",")[0]
            entry["first_timestamp_utc"] = first
            entry["last_timestamp_utc"] = last
        entries.append(entry)
    manifest = {"prepared_as_of_utc": "2026-06-10T00:00:00Z",
                "entries": entries}
    result = pr.validate_staging_manifest(manifest)
    assert result["verdict"] == pr.VERDICT_MANIFEST_ACCEPTED
    assert result["manifest_complete_for_all_kinds"] is True


def test_build_is_deterministic():
    assert tg.build_csv_template_guide() == tg.build_csv_template_guide()


# --------------------------------------------------------------------------- #
# get_csv_template accessor
# --------------------------------------------------------------------------- #
def test_get_csv_template_returns_copy_with_placement_info():
    t = tg.get_csv_template("funding_rates")
    assert t["available"] is True
    assert t["kind"] == "funding_rates"
    assert t["place_under"] == "data/arbitrage_factory_v1/staged/"
    assert t["template_is_text_only_nothing_is_written"] is True
    t["header"] = "tampered"
    assert tg.get_csv_template("funding_rates")["header"] != "tampered"


def test_get_csv_template_unknown_kind_errors():
    t = tg.get_csv_template("live_positions")
    assert t["available"] is False
    assert any("unknown_dataset_kind" in e for e in t["errors"])


# --------------------------------------------------------------------------- #
# placement checklist
# --------------------------------------------------------------------------- #
def test_placement_checklist_covers_the_core_steps():
    joined = " ".join(tg.PLACEMENT_CHECKLIST)
    assert "by_hand" in joined
    assert "copy_the_template_header_exactly" in joined
    assert "manually_exported_market_data" in joined
    assert "allowed_symbol_and_venue_labels" in joined
    assert "utc_iso8601" in joined
    assert "never_include_account_credential_balance_order_or_position" in joined
    assert "staging_manifest_validator" in joined
    assert "acknowledge_stale_data_explicitly" in joined
    assert "scanner_stays_blocked" in joined


# --------------------------------------------------------------------------- #
# gating on the prep rules
# --------------------------------------------------------------------------- #
def test_missing_prep_rules_blocks():
    g = tg.record_csv_template_guide(None)
    assert g["verdict"] == tg.VERDICT_TEMPLATE_GUIDE_BLOCKED
    assert "prep_rules_missing" in g["blockers"]


def test_invalid_prep_rules_blocks():
    rules = pr.build_staged_data_preparation_rules()
    rules["fetches_data"] = True
    g = tg.record_csv_template_guide(rules)
    assert g["verdict"] == tg.VERDICT_TEMPLATE_GUIDE_BLOCKED
    assert "prep_rules_invalid" in g["blockers"]


def test_blocked_prep_rules_blocks():
    blocked = pr.record_staged_data_preparation_rules(None)
    g = tg.record_csv_template_guide(blocked)
    assert g["verdict"] == tg.VERDICT_TEMPLATE_GUIDE_BLOCKED
    assert "prep_rules_not_ready" in g["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_guide_is_inert_on_all_paths():
    guides = [
        tg.build_csv_template_guide(),
        tg.record_csv_template_guide(None),
    ]
    for g in guides:
        assert g["templates_are_text_only_nothing_is_written"] is True
        assert g["sample_values_are_illustrative_placeholders_only"] is True
        assert g["operator_fills_templates_from_manually_exported_data"] is True
        assert g["scanner_remains_blocked"] is True
        assert g["guide_reads_no_files"] is True
        assert g["human_review_required"] is True
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
            assert g[key] is False, key
        assert g["paper_trading_gate_locked"] is True
        assert g["micro_live_gate_locked"] is True
        assert g["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert tg.validate_csv_template_guide(
        tg.build_csv_template_guide())["valid"] is True
    assert tg.validate_csv_template_guide(
        tg.record_csv_template_guide(None))["valid"] is True


def test_validate_rejects_diverged_header():
    g = tg.build_csv_template_guide()
    g["csv_templates"]["funding_rates"]["header"] = "timestamp_utc,symbol"
    v = tg.validate_csv_template_guide(g)
    assert v["valid"] is False
    assert "template_header_diverges:funding_rates" in v["errors"]


def test_validate_rejects_bad_filename_example_or_row_shape():
    g = tg.build_csv_template_guide()
    g["csv_templates"]["fee_schedule"]["filename_example"] = "fees_ftx.csv"
    v = tg.validate_csv_template_guide(g)
    assert v["valid"] is False
    assert "template_filename_example_invalid:fee_schedule" in v["errors"]
    g2 = tg.build_csv_template_guide()
    g2["csv_templates"]["liquidity_depth"]["sample_rows"] = (
        "2026-06-08T00:00:00Z,BTC,coinbase,250000.00",)
    v2 = tg.validate_csv_template_guide(g2)
    assert v2["valid"] is False
    assert "template_sample_row_field_count:liquidity_depth" in v2["errors"]


def test_validate_rejects_added_kind_or_tampered_checklist():
    g = tg.build_csv_template_guide()
    g["csv_templates"]["live_positions"] = {
        "filename_example": "positions.csv", "header": "x",
        "sample_rows": ("1",), "notes": "n"}
    v = tg.validate_csv_template_guide(g)
    assert v["valid"] is False
    assert "templates_missing_or_kind_set_tampered" in v["errors"]
    g2 = tg.build_csv_template_guide()
    g2["placement_checklist"] = g2["placement_checklist"][:3]
    v2 = tg.validate_csv_template_guide(g2)
    assert v2["valid"] is False
    assert "placement_checklist_tampered" in v2["errors"]


def test_validate_rejects_write_claims_or_scanner_unblock():
    g = tg.build_csv_template_guide()
    g["templates_are_text_only_nothing_is_written"] = False
    v = tg.validate_csv_template_guide(g)
    assert v["valid"] is False
    assert "templates_claim_to_write" in v["errors"]
    g2 = tg.build_csv_template_guide()
    g2["scanner_remains_blocked"] = False
    v2 = tg.validate_csv_template_guide(g2)
    assert v2["valid"] is False
    assert "scanner_block_dropped" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    g = tg.build_csv_template_guide()
    g["micro_live_gate_locked"] = False
    v = tg.validate_csv_template_guide(g)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    g2 = tg.build_csv_template_guide()
    g2["writes_files"] = True
    v2 = tg.validate_csv_template_guide(g2)
    assert v2["valid"] is False
    assert any("capability_not_false:writes_files" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = tg.render_csv_template_guide_markdown(tg.build_csv_template_guide())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Staged-Data CSV Template Guide")
    assert "Place files by hand under: data/arbitrage_factory_v1/staged/" in md
    assert "scanner remains BLOCKED" in md
    assert "```csv" in md
    assert "funding_BTC_binance.csv" in md
    assert "Placement checklist" in md
    assert "LOCKED" in md
    md2 = tg.render_csv_template_guide_markdown(tg.record_csv_template_guide(None))
    assert "BLOCKED provides no templates" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_templates_label():
    assert tg.get_csv_template_guide_label() == tg.GUIDE_LABEL
    assert "READ-ONLY" in tg.GUIDE_LABEL
    assert "TEMPLATES ONLY" in tg.GUIDE_LABEL
    assert tg.GUIDE_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in tg.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_filesystem_or_credential_modules():
    with open(tg.__file__, "r", encoding="utf-8") as fh:
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
