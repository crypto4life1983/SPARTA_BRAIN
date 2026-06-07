"""Tests for the Crypto-D1 Local Data Inventory Inspector (Block 140).

The inspector is a read-only, RESEARCH_ONLY local data lister. It LISTS files and
reads file *sizes* (metadata) under caller-supplied roots, infers symbol /
timeframe / date-range from file and folder NAMES only, and reports the inventory
in memory. It opens no file contents, reads no secret / .env, follows no symlink,
touches no network, and writes nothing. These tests use hermetic tmp_path
fixtures: inventory correctness, missing-pair derivation, name-only date-range
inference, secret / .env / skip-dir / symlink skipping, a before/after no-write
assertion, missing-folder tolerance, determinism, validation, render, AST purity
(stdlib os/re/typing only -- no open / network / subprocess / write attrs), and the
two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import os
import pathlib

import pytest

from sparta_commander.strategy_factory_crypto_d1_local_data_inventory_inspector import (  # noqa: E501
    DEFAULT_INSPECT_ROOTS,
    DEFAULT_REQUESTED_SYMBOLS,
    DEFAULT_REQUESTED_TIMEFRAMES,
    INSPECTOR_LABEL,
    INSPECTOR_MODE,
    INSPECTOR_SAFETY_FLAGS,
    INSPECTOR_SCHEMA_VERSION,
    INSPECTOR_STATUS,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    inspect_local_data_inventory,
    render_local_data_inventory_report_markdown,
    validate_local_data_inventory_report,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_local_data_inventory_inspector.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_local_data_inventory_inspector.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_local_data_inventory_inspector.py"
)

_INSPECT = inspect_local_data_inventory
_VALIDATE = validate_local_data_inventory_report
_RENDER = render_local_data_inventory_report_markdown


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def _build_tree(tmp_path):
    """A small fixture dataset tree with two roots, plus secret / non-data /
    skip-dir entries that MUST be skipped. Returns (root_a, root_b)."""
    root_a = tmp_path / "cache"
    (root_a / "BTCUSD").mkdir(parents=True)
    (root_a / "BTCUSD" / "BTCUSD_1d_2020-01-01_2024-12-31.csv").write_text(
        "x" * 10, encoding="utf-8"
    )

    root_b = tmp_path / "longhist"
    (root_b / "raw").mkdir(parents=True)
    (root_b / "raw" / "MGC_1d_2019-05-13_2025-12-31.csv").write_text(
        "y" * 20, encoding="utf-8"
    )
    (root_b / "raw" / "MNQ_1d_2019-05-13_2025-12-31.parquet").write_text(
        "z" * 30, encoding="utf-8"
    )
    (root_b / "raw" / "notes.md").write_text("readme", encoding="utf-8")
    # secret-named entries that must NEVER be listed / opened
    (root_b / ".env").write_text("DATABENTO_API_KEY=should-never-be-read", encoding="utf-8")
    (root_b / "databento_secret.txt").write_text("nope", encoding="utf-8")
    secret_dir = root_b / "local_secrets"
    secret_dir.mkdir()
    (secret_dir / "databento_api_key.txt").write_text("nope", encoding="utf-8")
    return root_a, root_b


def _inspect_tree(tmp_path, **overrides):
    root_a, root_b = _build_tree(tmp_path)
    payload = {
        "roots": [str(root_a), str(root_b)],
        "requested_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "requested_timeframes": ["1d"],
    }
    payload.update(overrides)
    return _INSPECT(payload), root_a, root_b


def _snapshot(base):
    snap = {}
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
                snap[p] = (st.st_size, st.st_mtime_ns)
            except OSError:
                snap[p] = None
    return snap


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert INSPECTOR_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_local_data_inventory_inspector.v1"
    )
    assert INSPECTOR_LABEL == "Block 140 - Crypto-D1 Local Data Inventory Inspector"
    assert INSPECTOR_STATUS == "READ_ONLY_LOCAL_DATA_INVENTORY"
    assert INSPECTOR_MODE == "RESEARCH_ONLY"


def test_default_roots_and_requested_constants():
    assert DEFAULT_INSPECT_ROOTS == (
        "data/databento_cache/",
        "data/databento_long_history/",
    )
    assert DEFAULT_REQUESTED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert DEFAULT_REQUESTED_TIMEFRAMES == ("1d",)


def test_safety_flags_true_facts_all_capability_false():
    flags = INSPECTOR_SAFETY_FLAGS
    posture_true = {"read_only", "research_only", "human_approval_required"}
    for key in posture_true:
        assert flags[key] is True, key
    for key, value in flags.items():
        if key in posture_true:
            continue
        assert value is False, key


def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Inventory correctness
# --------------------------------------------------------------------------- #
def test_folders_inspected_report_existence_and_counts(tmp_path):
    report, root_a, root_b = _inspect_tree(tmp_path)
    folders = report["folders_inspected"]
    assert len(folders) == 2
    for f in folders:
        assert f["exists"] is True
    by_root = {f["root"]: f for f in folders}
    assert by_root[str(root_a)]["file_count"] == 1
    assert by_root[str(root_b)]["file_count"] == 2


def test_only_data_files_are_listed(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    names = sorted(f["name"] for f in report["files_found"])
    assert names == [
        "BTCUSD_1d_2020-01-01_2024-12-31.csv",
        "MGC_1d_2019-05-13_2025-12-31.csv",
        "MNQ_1d_2019-05-13_2025-12-31.parquet",
    ]
    assert report["file_count"] == 3
    for f in report["files_found"]:
        assert f["size_bytes"] > 0


def test_symbol_timeframe_inference_from_names(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    assert report["discovered_pairs"] == ["BTCUSD@1d", "MGC@1d", "MNQ@1d"]


def test_date_ranges_inferred_from_names_only(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    ranges = report["date_ranges"]
    assert ranges["BTCUSD@1d"] == {"start": "2020-01-01", "end": "2024-12-31"}
    assert ranges["MGC@1d"] == {"start": "2019-05-13", "end": "2025-12-31"}
    assert ranges["MNQ@1d"] == {"start": "2019-05-13", "end": "2025-12-31"}


def test_missing_pairs_and_databento_flag(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    assert report["covered_pairs"] == ["BTCUSD@1d"]
    assert report["missing_pairs"] == ["ETHUSD@1d", "SOLUSD@1d"]
    assert report["databento_may_be_needed_later"] is True


def test_full_coverage_clears_databento_flag(tmp_path):
    # request only what's present -> nothing missing -> databento not needed.
    report, _a, _b = _inspect_tree(
        tmp_path, requested_symbols=["BTCUSD"], requested_timeframes=["1d"]
    )
    assert report["missing_pairs"] == []
    assert report["databento_may_be_needed_later"] is False


# --------------------------------------------------------------------------- #
# Secret / .env / skip-dir / symlink safety
# --------------------------------------------------------------------------- #
def test_secret_and_dotenv_entries_are_never_listed(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    listed = {f["name"] for f in report["files_found"]}
    assert ".env" not in listed
    assert "databento_secret.txt" not in listed
    assert "databento_api_key.txt" not in listed
    assert report["skipped_totals"]["secret"] >= 2
    assert report["no_secret_confirmation"]["secret_named_entries_skipped"] >= 2
    assert report["no_secret_confirmation"]["opened_no_file_contents"] is True
    assert report["no_secret_confirmation"]["inspected_no_dotenv"] is True


def test_non_data_files_are_skipped(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    listed = {f["name"] for f in report["files_found"]}
    assert "notes.md" not in listed
    total_non_data = sum(
        f["skipped"]["non_data"] for f in report["folders_inspected"]
    )
    assert total_non_data >= 1


def test_symlinks_are_skipped_not_followed(tmp_path):
    root_a, root_b = _build_tree(tmp_path)
    link = root_b / "raw" / "link_to_a"
    try:
        os.symlink(str(root_a), str(link))
    except (OSError, NotImplementedError, AttributeError):
        pytest.skip("symlink creation not permitted on this platform")
    report = _INSPECT({"roots": [str(root_b)]})
    total_symlinks = sum(
        f["skipped"]["symlinks"] for f in report["folders_inspected"]
    )
    assert total_symlinks >= 1
    # the symlinked-in BTCUSD file must NOT appear via the symlink path.
    assert all("link_to_a" not in f["rel_path"] for f in report["files_found"])


# --------------------------------------------------------------------------- #
# No-write guarantee (hermetic before/after)
# --------------------------------------------------------------------------- #
def test_inspection_writes_nothing(tmp_path):
    root_a, root_b = _build_tree(tmp_path)
    before = _snapshot(tmp_path)
    _INSPECT(
        {
            "roots": [str(root_a), str(root_b)],
            "requested_symbols": ["BTCUSD", "ETHUSD"],
            "requested_timeframes": ["1d"],
        }
    )
    after = _snapshot(tmp_path)
    assert before == after


# --------------------------------------------------------------------------- #
# Missing-folder tolerance / default roots
# --------------------------------------------------------------------------- #
def test_missing_folder_is_reported_not_raised(tmp_path):
    ghost = tmp_path / "nope_does_not_exist"
    report = _INSPECT(
        {
            "roots": [str(ghost)],
            "requested_symbols": ["BTCUSD"],
            "requested_timeframes": ["1d"],
        }
    )
    assert report["folders_inspected"][0]["exists"] is False
    assert report["folders_inspected"][0]["file_count"] == 0
    assert report["files_found"] == []
    assert report["missing_pairs"] == ["BTCUSD@1d"]
    assert report["databento_may_be_needed_later"] is True


def test_default_payload_uses_default_roots(tmp_path, monkeypatch):
    # Point the process at an empty cwd so default relative roots resolve to
    # non-existent folders -> no real disk is scanned, still no crash.
    monkeypatch.chdir(tmp_path)
    report = _INSPECT()
    roots = [f["root"] for f in report["folders_inspected"]]
    assert roots == list(DEFAULT_INSPECT_ROOTS)
    assert report["read_only"] is True
    assert _VALIDATE(report)["valid"] is True


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_inspection_is_deterministic(tmp_path):
    root_a, root_b = _build_tree(tmp_path)
    payload = {"roots": [str(root_a), str(root_b)]}
    assert _INSPECT(payload) == _INSPECT(payload)


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_report_validates(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    verdict = _VALIDATE(report)
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["flags_false"] is True
    assert verdict["posture_ok"] is True
    assert verdict["states_blocked_locked"] is True
    assert verdict["no_write_ok"] is True
    assert verdict["no_secret_ok"] is True
    assert verdict["safety_ok"] is True
    assert verdict["no_secret_file_listed"] is True
    assert verdict["db_flag_consistent"] is True


def test_validate_rejects_a_write_flag(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    report["writes_files"] = True
    verdict = _VALIDATE(report)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unblocked_state(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    report["real_data_qa_state"] = "UNLOCKED"
    verdict = _VALIDATE(report)
    assert verdict["valid"] is False
    assert verdict["states_blocked_locked"] is False


def test_validate_rejects_a_listed_secret_file(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    report["files_found"].append({"name": "databento_secret.csv", "rel_path": "x"})
    verdict = _VALIDATE(report)
    assert verdict["valid"] is False
    assert verdict["no_secret_file_listed"] is False


def test_validate_rejects_missing_required_field(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    del report["safety_flags"]
    verdict = _VALIDATE(report)
    assert verdict["valid"] is False
    assert "safety_flags" in verdict["missing_fields"]


def test_render_is_a_readonly_markdown_string(tmp_path):
    report, _a, _b = _inspect_tree(tmp_path)
    text = _RENDER(report)
    assert isinstance(text, str)
    assert text.startswith("# Crypto-D1 Local Data Inventory")
    assert "## 1. Folders Inspected" in text
    assert "## 3. Symbols / Timeframes Discovered" in text
    assert "## 4. Date Ranges Discovered" in text
    assert "## 5. Missing Pairs (requested but absent)" in text
    assert "## 7. No-Write Confirmation" in text
    assert "## 8. No-Secret Confirmation" in text
    assert "## 9. Safety Confirmation" in text
    # a secret value must never leak into the rendered brief.
    assert "should-never-be-read" not in text


# --------------------------------------------------------------------------- #
# AST purity: read-only os/re only, no content reads, no network, no writes
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORTS = {"__future__", "typing", "os", "re"}
_FORBIDDEN_CALL_NAMES = {"open", "eval", "exec", "compile", "__import__", "input"}
_FORBIDDEN_MODULE_TOKENS = {
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "http",
    "urllib",
    "ftplib",
    "importlib",
    "pandas",
    "numpy",
    "ccxt",
    "databento",
    "pickle",
    "sqlite3",
}
_FORBIDDEN_ATTRS = {
    "open",
    "write",
    "write_text",
    "write_bytes",
    "writelines",
    "mkdir",
    "makedirs",
    "rmtree",
    "rmdir",
    "removedirs",
    "unlink",
    "rename",
    "urlopen",
    "urlretrieve",
    "popen",
    "system",
    "fdopen",
    "symlink",
    "Popen",
    "connect",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_stdlib_os_re_typing_only():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in _FORBIDDEN_CALL_NAMES, node.func.id


def test_module_has_no_forbidden_module_tokens():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_module_has_no_write_or_network_attributes():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in _FORBIDDEN_ATTRS, node.attr


# --------------------------------------------------------------------------- #
# commander_2_safety allowlist (exactly two additive lines)
# --------------------------------------------------------------------------- #
def test_commander_safety_allowlist_includes_the_two_additive_entries():
    from sparta_commander.commander_2_safety import (
        COMMANDER_2_MODULES,
        COMMANDER_2_TESTS,
    )

    assert _MODULE_ALLOWLIST_LINE in COMMANDER_2_MODULES
    assert _TEST_ALLOWLIST_LINE in COMMANDER_2_TESTS
    assert COMMANDER_2_MODULES.count(_MODULE_ALLOWLIST_LINE) == 1
    assert COMMANDER_2_TESTS.count(_TEST_ALLOWLIST_LINE) == 1


def test_commander_safety_only_two_new_lines_for_this_module():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert src.count(_MODULE_ALLOWLIST_LINE) == 1
    assert src.count(_TEST_ALLOWLIST_LINE) == 1
