"""Tests for the per-strike options paid-data import contract.

Proves the contract is PURE / IMPORT-SPEC-ONLY: it buys/fetches/downloads NOTHING; defines the
required per-strike fields (incl. greeks delta/gamma/vega/theta + IV), an approved human-procured
vendor list, a gitignored inbox, and BTC scope; its validator accepts only a BTC, approved-vendor,
all-required-fields, in-range, human-procured manifest and rejects tampered/SPARTA-fetched ones;
and it runs no backtest / activates nothing. No network, no I/O."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.per_strike_options_paid_data_import_contract as imp


def _ok_manifest(**ov):
    base = {
        "source": "tardis.dev",
        "currency": "BTC",
        "fields_present": list(imp.REQUIRED_FIELDS) + ["bid", "ask"],
        "row_count": 5_000_000,
        "date_coverage": {"first": "2021-03-24", "last": "2026-06-21"},
        "procured_externally_by_human": True,
        "fetched_or_bought_inside_sparta": False,
    }
    base.update(ov)
    return base


def test_spec_builds_buys_and_fetches_nothing():
    s = imp.build_paid_import_spec()
    assert s["mode"] == "RESEARCH_ONLY"
    assert s["is_import_spec_only"] is True
    assert s["buys_nothing"] is True and s["fetches_nothing"] is True and s["downloads_nothing"] is True
    assert s["currency"] == "BTC"
    assert s["inbox_is_gitignored"] is True
    for g in ("delta", "gamma", "vega", "theta", "implied_vol"):
        assert g in s["required_fields"]
    for k, v in s["scope_locks"].items():
        assert v is True, k


def test_validator_accepts_clean_human_procured_manifest():
    r = imp.validate_paid_dataset_manifest(_ok_manifest())
    assert r["valid"] is True and r["failures"] == []
    assert r["required_fields_ok"] is True


def test_validator_rejects_bad_manifests():
    assert imp.validate_paid_dataset_manifest(_ok_manifest(currency="ETH"))["valid"] is False
    assert imp.validate_paid_dataset_manifest(_ok_manifest(source="random_blog"))["valid"] is False
    assert imp.validate_paid_dataset_manifest(
        _ok_manifest(fields_present=["instrument_name", "strike"]))["valid"] is False  # missing greeks
    assert imp.validate_paid_dataset_manifest(_ok_manifest(row_count=0))["valid"] is False
    # must be human-procured, NOT fetched/bought inside SPARTA
    assert imp.validate_paid_dataset_manifest(
        _ok_manifest(procured_externally_by_human=False))["valid"] is False
    assert imp.validate_paid_dataset_manifest(
        _ok_manifest(fetched_or_bought_inside_sparta=True))["valid"] is False
    # coverage entirely outside target
    assert imp.validate_paid_dataset_manifest(
        _ok_manifest(date_coverage={"first": "2018-01-01", "last": "2018-06-01"}))["valid"] is False


def test_march_2020_coverage_flag():
    r = imp.validate_paid_dataset_manifest(
        _ok_manifest(date_coverage={"first": "2020-01-01", "last": "2026-06-21"}))
    assert r["valid"] is True and r["covers_march_2020"] is True
    r2 = imp.validate_paid_dataset_manifest(_ok_manifest())  # starts 2021-03 -> no March-2020
    assert r2["covers_march_2020"] is False


def test_module_purity():
    src = Path(imp.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    # strip the docstring (prose like "separately purchased / downloads nothing" is descriptive)
    doc = ast.get_docstring(ast.parse(src)) or ""
    code = src.replace(doc, "")
    # actionable I/O / network verbs must be ABSENT (no fetch/buy/download capability)
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "urlopen", "urllib.request", "requests.get", "json.load",
                 "read_text", "urlretrieve"):
        assert verb not in code, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
