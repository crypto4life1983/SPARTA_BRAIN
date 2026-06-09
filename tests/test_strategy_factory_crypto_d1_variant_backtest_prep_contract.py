"""Tests for the Crypto-D1 Risk-Controlled Variant Backtest Prep Contract (PREP
ONLY). All inputs are FAKE local CSVs under tmp_path; no network, no credentials,
no real data, and no variant backtest is ever run."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_crypto_d1_variant_backtest_prep_contract as vp
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_CANON = ",".join(qa.QA_REQUIRED_FIELDS)
_SRC = "binance_usdt_spot_frozen_regime_inputs"


def _rows() -> str:
    return "\n".join(
        [
            _CANON,
            "2024-01-01,100,110,90,105,1000," + _SRC + ",spot",
            "2024-01-02,105,115,100,108,1200," + _SRC + ",spot",
            "2024-01-03,108,120,107,118,1300," + _SRC + ",spot",
        ]
    )


def _stage_and_qa(tmp_path) -> None:
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sym in ("BTC", "ETH", "SOL"):
        (raw / (sym + "_1d.csv")).write_text(_rows(), encoding="utf-8")
    rep = qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    assert rep["verdict"] == qa.VERDICT_PASS


# --------------------------------------------------------------------------- #
# manifests
# --------------------------------------------------------------------------- #
def test_five_variants_all_fully_specified():
    manifests = vp.build_variant_manifests()
    ids = [m["variant_id"] for m in manifests]
    assert ids == [
        "V1_trend_filter",
        "V2_trend_plus_cash_regime",
        "V3_voltarget_concentration_cap",
        "V4_monthly_rebalance_capped",
        "V5_full_risk_managed",
    ]
    assert all(m["fully_specified"] for m in manifests)
    assert all(m["unresolved_controls"] == [] for m in manifests)


def test_v1_pins_trend_filter_window():
    m = next(m for m in vp.build_variant_manifests() if m["variant_id"] == "V1_trend_filter")
    assert m["fixed_parameters"]["trend_filter"]["sma_window_days"] == 200
    assert m["symbols"] == list(qa.QA_REQUIRED_SYMBOLS)


def test_v3_pins_concentration_cap():
    m = next(m for m in vp.build_variant_manifests()
             if m["variant_id"] == "V3_voltarget_concentration_cap")
    assert m["fixed_parameters"]["sol_concentration_cap"]["max_weight_per_asset"] == 0.33
    assert m["fixed_parameters"]["volatility_cap"]["gross_exposure_cap"] == 1.0


def test_v5_resolves_all_six_controls():
    m = next(m for m in vp.build_variant_manifests() if m["variant_id"] == "V5_full_risk_managed")
    assert set(m["fixed_parameters"].keys()) == set(vp.CONTROL_PARAMETERS.keys())


def test_constraints_forbid_optimization_and_leverage():
    c = vp.build_variant_manifests()[0]["constraints"]
    assert c["optimization"] is False and c["parameter_search"] is False
    assert c["walk_forward"] is False and c["lookahead_allowed"] is False
    assert c["allow_shorting"] is False and c["allow_leverage"] is False
    assert c["long_only"] is True


# --------------------------------------------------------------------------- #
# readiness
# --------------------------------------------------------------------------- #
def test_ready_when_inputs_staged(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    assert r["verdict"] == vp.VERDICT_READY
    assert r["blockers"] == []
    assert r["baseline_inputs_ready"] is True
    assert r["variant_count"] == 5
    assert r["next_required_action"] == "HUMAN_APPROVED_RISK_CONTROLLED_VARIANT_BACKTEST_RUN"


def test_not_ready_when_inputs_missing(tmp_path):
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    assert r["verdict"] == vp.VERDICT_NOT_READY
    assert "baseline_inputs_not_ready" in r["blockers"]


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_prep_unlocks_nothing(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    assert r["executes"] is False
    assert r["runs_variant_backtest"] is False
    assert r["runs_optimization"] is False
    assert r["runs_parameter_search"] is False
    assert r["runs_walk_forward"] is False
    assert r["authorizes_variant_run"] is False
    assert r["authorizes_paper_trading"] is False
    assert r["unlocks_downstream_gate"] is False
    assert r["baseline_backtest_blocked"] is True
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True


def test_validate_passes(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    v = vp.validate_variant_prep_report(r)
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    r["paper_trading_gate_locked"] = False
    v = vp.validate_variant_prep_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_optimization_constraint(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    r["variant_constraints"]["optimization"] = True
    v = vp.validate_variant_prep_report(r)
    assert v["valid"] is False
    assert any("constraint_not_false:optimization" in e for e in v["errors"])


def test_render_markdown_is_string(tmp_path):
    _stage_and_qa(tmp_path)
    r = vp.check_variant_prep_readiness(repo_root=str(tmp_path))
    md = vp.render_variant_prep_markdown(r)
    assert md.startswith("# Crypto-D1 Risk-Controlled Variant Backtest Prep (PREP ONLY)")
    assert "LOCKED" in md and "V5_full_risk_managed" in md


def test_module_imports_no_network_or_credential_modules():
    with open(vp.__file__, "r", encoding="utf-8") as fh:
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
