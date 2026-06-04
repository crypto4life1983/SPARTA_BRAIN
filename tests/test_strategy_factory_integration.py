"""Tests for the read-only Strategy Factory v1 Integration Bundle (dry-run).

Pure stdlib + pytest, synthetic fixtures only. Asserts:
  * the bundle assembles the full chain and runs/executes nothing;
  * verdict ceiling stays WATCH; the memo verdict is only ever WATCH / FAIL /
    INSUFFICIENT_EVIDENCE (never PASS / ACTIVE / STRONG), and even all-green
    synthetic evidence caps at WATCH;
  * N stays fixed at 20 and the {18,20,22} neighborhood stays sensitivity-not-
    optimization with the winner never re-selected;
  * the registry output is a PROPOSAL (proposal_only / not applied) and the
    dashboard output is a PREVIEW (preview_only / not applied);
  * the human-facing free text carries no forbidden trading terms;
  * safety flags stay pinned false; deterministic JSON is byte-stable;
  * imports are allowlisted (no subprocess/socket/urllib/requests/ccxt) and no
    execution call surfaces exist;
  * the opt-in writer is confined to the single build folder;
  * the read-only CLI returns 0 and runs no backtest.
"""
from __future__ import annotations

import ast
import io
import json
import sys
import tokenize
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import strategy_factory_integration as sfi  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "strategy_factory_integration.py"


# ---------------------------------------------------------------------------
# Minimal crafted validation_report for direct _derive_decision unit tests.
# (Never touches real data; exercises the verdict logic in isolation.)
# ---------------------------------------------------------------------------
def _fake_report(*, meets_family=True, per_asset_clear=True, all_positive=True,
                 insufficient=False, has_trades=True):
    per_asset = {}
    if has_trades:
        per_asset = {"BTC": {"clears_per_asset_floor": per_asset_clear},
                     "ETH": {"clears_per_asset_floor": per_asset_clear}}
    return {
        "insufficient_history_notes": {"BTC": "short"} if insufficient else {},
        "validation_sections": {
            "3_per_asset_consistency": {"all_positive": all_positive},
            "4_trade_count_and_turnover": {
                "meets_family_floor": meets_family, "per_asset": per_asset},
            "5_fee_slippage_stress": {"BTC": {
                "baseline_total_return": 0.1,
                "stress_levels": {"150": {"survives_positive": True}}}},
            "6_outlier_sensitivity": {"BTC": {"edge_outlier_dependent": False}},
            "7_regime_sensitivity": {"BTC": {"confined_to_single_regime": False}},
            "9_small_parameter_neighborhood_sensitivity": {"BTC": {
                "is_sensitivity_not_optimization": True,
                "winner_reselected": False}},
        },
    }


@pytest.fixture(scope="module")
def bundle():
    return sfi.build_integration_bundle(_REPO_ROOT)


# ---------------------------------------------------------------------------
# Identity / chain
# ---------------------------------------------------------------------------
def test_show_plan_identity():
    plan = sfi.show_plan()
    assert plan["config_name"] == "strategy_factory_integration_v1"
    assert plan["layer"] == "strategy_factory_integration_v1"
    assert plan["verdict_ceiling"] == "WATCH"
    assert plan["primary_lookback"] == 20
    assert plan["build_only"] is True
    assert plan["executes_backtest"] is False
    assert len(plan["chain"]) == 9
    assert plan["outputs"] == [
        "report.json", "report.md", "decision_memo.md",
        "registry_update_proposal.json", "dashboard_feed_preview.json"]


def test_bundle_assembles_full_chain(bundle):
    for key in ("chain", "queue_summary", "orchestrator_summary",
                "safety_summary", "registry_summary", "validation_report",
                "decision_memo", "registry_update_proposal",
                "dashboard_feed_preview", "next_action"):
        assert key in bundle, f"missing chain section: {key}"
    assert bundle["chain"][0] == "queue"
    assert bundle["chain"][-1] == "next_action"


def test_bundle_executes_nothing(bundle):
    assert bundle["executes_backtest"] is False
    assert bundle["executes_anything"] is False
    assert bundle["dry_run"] is True
    assert bundle["read_only"] is True
    assert bundle["reads_frozen_dataset"] is False
    assert bundle["uses_synthetic_data_only"] is True


# ---------------------------------------------------------------------------
# Verdict ceiling
# ---------------------------------------------------------------------------
def test_verdict_ceiling_and_allowed_verdict(bundle):
    assert bundle["verdict_ceiling"] == "WATCH"
    v = bundle["decision_memo"]["verdict"]
    assert v in sfi.ALLOWED_MEMO_VERDICTS
    assert v not in sfi.FORBIDDEN_VERDICTS


def test_all_green_synthetic_caps_at_watch():
    verdict, evidence, checks = sfi._derive_decision(_fake_report())
    assert verdict == "WATCH"
    assert verdict not in sfi.FORBIDDEN_VERDICTS
    assert evidence == "MIXED"


def test_missing_floor_is_fail():
    verdict, _, _ = sfi._derive_decision(_fake_report(meets_family=False))
    assert verdict == "FAIL"


def test_no_trades_is_insufficient():
    verdict, _, _ = sfi._derive_decision(_fake_report(has_trades=False))
    assert verdict == "INSUFFICIENT_EVIDENCE"
    verdict2, _, _ = sfi._derive_decision(_fake_report(insufficient=True))
    assert verdict2 == "INSUFFICIENT_EVIDENCE"


def test_memo_verdict_never_forbidden():
    for kwargs in ({}, {"meets_family": False}, {"per_asset_clear": False},
                   {"has_trades": False}, {"insufficient": True}):
        verdict, _, _ = sfi._derive_decision(_fake_report(**kwargs))
        assert verdict in sfi.ALLOWED_MEMO_VERDICTS
        assert verdict not in sfi.FORBIDDEN_VERDICTS


# ---------------------------------------------------------------------------
# N fixed at 20 / neighborhood sensitivity preserved
# ---------------------------------------------------------------------------
def test_n_fixed_at_20(bundle):
    assert sfi.PRIMARY_LOOKBACK == 20
    assert bundle["primary_lookback"] == 20
    cand = bundle["registry_update_proposal"]["proposed_candidate"]
    assert cand["primary_lookback"] == 20


def test_neighborhood_sensitivity_preserved(bundle):
    cand = bundle["registry_update_proposal"]["proposed_candidate"]
    assert cand["neighborhood_is_sensitivity_not_optimization"] is True
    assert cand["winner_reselected"] is False
    sec9 = bundle["validation_report"]["validation_sections"][
        "9_small_parameter_neighborhood_sensitivity"]
    for asset_view in sec9.values():
        assert asset_view["is_sensitivity_not_optimization"] is True
        assert asset_view["winner_reselected"] is False


# ---------------------------------------------------------------------------
# Proposal / preview are non-applied
# ---------------------------------------------------------------------------
def test_registry_output_is_proposal_only(bundle):
    p = bundle["registry_update_proposal"]
    assert p["proposal_only"] is True
    assert p["applied"] is False
    assert p["registry_mutation_performed"] is False
    assert p["human_approval_required_to_apply"] is True
    assert p["proposed_candidate"]["status"] not in sfi.FORBIDDEN_VERDICTS


def test_dashboard_output_is_preview_only(bundle):
    d = bundle["dashboard_feed_preview"]
    assert d["preview_only"] is True
    assert d["applied_to_dashboard"] is False
    assert d["dashboard_write_performed"] is False
    assert set(d["entry"]) <= set(sfi._DASHBOARD_ENTRY_FIELDS)


# ---------------------------------------------------------------------------
# Human-text screen / safety flags / determinism
# ---------------------------------------------------------------------------
def test_human_text_carries_no_forbidden_terms(bundle):
    assert bundle["forbidden_term_scan_on_human_text"] == []


def test_safety_flags_pinned_false(bundle):
    flags = bundle["safety_flags"]
    assert flags["research_only"] is True
    for key in ("paper_live_authorized", "broker_path_enabled",
                "exchange_path_enabled", "order_path_enabled",
                "fetch_live_data_enabled", "dataset_mutation_allowed",
                "queue_mutation_allowed", "registry_mutation_allowed",
                "dashboard_mutation_allowed", "active_strong_promoted",
                "bundle_23_started", "execution_authorized"):
        assert flags[key] is False, f"{key} must be False"


def test_json_is_byte_stable():
    a = sfi.to_stable_json(sfi.build_integration_bundle(_REPO_ROOT))
    b = sfi.to_stable_json(sfi.build_integration_bundle(_REPO_ROOT))
    assert a == b
    assert a.endswith("\n")
    assert json.loads(a) == json.loads(b)


# ---------------------------------------------------------------------------
# Adapter seam
# ---------------------------------------------------------------------------
def test_adapter_handles_dict_and_list():
    runner_out = sfi.synthetic_runner_output(n=60)
    per_asset = sfi.adapt_runner_output_to_per_asset(runner_out)
    assert isinstance(per_asset, list)
    assert {x["asset"] for x in per_asset} == {"BTC", "ETH", "SOL"}
    for x in per_asset:
        assert x["bars"] and isinstance(x["bars"], list)
    # A list passes through unchanged.
    same = sfi.adapt_runner_output_to_per_asset(per_asset)
    assert same is per_asset


# ---------------------------------------------------------------------------
# Import allowlist / no execution surfaces
# ---------------------------------------------------------------------------
def _code_names_and_strings(src):
    names, strings = set(), []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.NAME:
            names.add(tok.string)
        elif tok.type == tokenize.STRING:
            strings.append(tok.string)
    return names, strings


def test_no_execution_or_network_identifiers():
    src = TOOL_FILE.read_text(encoding="utf-8")
    names, strings = _code_names_and_strings(src)
    for bad in ("subprocess", "socket", "urllib", "requests", "ccxt", "Popen",
                "system", "popen"):
        assert bad not in names, f"forbidden code identifier: {bad!r}"
    joined = "".join(strings).lower()
    for bad in ("http://", "https://", "binance.com", "private_key",
                "api_secret", "place_order"):
        assert bad not in joined, f"forbidden string literal: {bad!r}"


def test_module_imports_allowlist_only():
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    allowed = {
        "argparse", "json", "sys", "pathlib", "datetime", "__future__",
        "crypto_d1_backtest_runner", "crypto_d1_deeper_validation",
        "strategy_factory_queue", "strategy_factory_orchestrator",
        "strategy_factory_safety", "strategy_report_registry",
    }
    assert imported <= allowed, f"unexpected imports: {imported - allowed}"
    for bad in ("subprocess", "socket", "urllib", "requests", "http", "ccxt"):
        assert bad not in imported, f"unexpected import: {bad}"


def test_no_execution_call_surfaces():
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden_attrs = {"Popen", "run", "call", "system", "popen", "urlopen",
                       "connect", "request", "place_order", "create_order"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in forbidden_attrs:
                root = f.value
                root_name = root.id if isinstance(root, ast.Name) else None
                assert root_name not in ("os", "subprocess", "socket", "urllib"), (
                    f"forbidden call surface: {root_name}.{f.attr}")


# ---------------------------------------------------------------------------
# Confined writer + read-only CLI
# ---------------------------------------------------------------------------
def test_write_bundle_confined_to_build_folder(tmp_path, bundle):
    written = sfi.write_bundle(tmp_path, bundle)
    rel = "reports/strategy_factory_integration_v1_build"
    assert written == [
        f"{rel}/report.json", f"{rel}/report.md", f"{rel}/decision_memo.md",
        f"{rel}/registry_update_proposal.json",
        f"{rel}/dashboard_feed_preview.json"]
    all_files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert len(all_files) == 5
    build_dir = tmp_path / "reports" / "strategy_factory_integration_v1_build"
    for p in all_files:
        assert build_dir in p.parents


def test_cli_main_returns_zero_runs_no_backtest(capsys):
    rc = sfi.main(["--base", str(_REPO_ROOT)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["executes_backtest"] is False
    assert payload["dry_run"] is True
    assert payload["verdict_ceiling"] == "WATCH"
