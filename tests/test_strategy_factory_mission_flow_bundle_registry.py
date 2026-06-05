"""Tests for the Strategy Factory Mission Flow Bundle Registry (Block 79).

The registry is a PURE, stdlib-only, read-only source of truth for completed
Strategy Factory bundle metadata. It lets the JARVIS Mission Flow feed follow
the pipeline from structured metadata instead of hardcoding each bundle inline.

Coverage:
- registry includes Bundles 42 through 47, all complete
- latest completed bundle is Bundle 47
- current_stage / next_required_action match the post-Bundle-47 state
- every registered bundle is RESEARCH_ONLY, read_only True, executes False
- no registered bundle authorizes real-world action or unlocks any real
  capability (data, QA, baseline, backtest, paper/live, broker/exchange,
  automation, runtime/registry/dashboard writes)
- schema constants are readable and stable
- deterministic repeated calls; mutation-isolated copies
- pure stdlib import-root audit + forbidden-surface audit
- no filesystem / network / subprocess / dynamic execution surface
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_mission_flow_bundle_registry import (
    REGISTRY_VERSION,
    REGISTRY_MODE,
    REGISTRY_SAFETY_POSTURE,
    CURRENT_STAGE,
    NEXT_REQUIRED_ACTION,
    list_registered_bundles,
    list_completed_bundles,
    get_latest_completed_bundle,
    get_bundle_by_number,
    get_bundle_by_id,
    get_latest_completed_bundle_label,
    get_current_stage,
    get_next_required_action,
    get_registry_safety_posture,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_mission_flow_bundle_registry.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_CAPABILITY_FLAGS = (
    "authorizes_real_world_action",
    "unlocks_data_acquisition",
    "unlocks_qa",
    "unlocks_baseline",
    "unlocks_backtest",
    "unlocks_simulation",
    "unlocks_paper_live",
    "unlocks_broker_exchange",
    "unlocks_automation",
    "unlocks_runtime_writes",
    "unlocks_registry_writes",
    "unlocks_dashboard_writes",
)


# --- 1: registry membership -------------------------------------------------

def test_registry_includes_bundles_42_through_47():
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47]


def test_all_registered_bundles_complete():
    for b in list_registered_bundles():
        assert b["complete"] is True, b["bundle_id"]
    assert len(list_completed_bundles()) == 6


def test_bundle_record_has_stable_keys():
    expected = {
        "bundle_number", "bundle_id", "name", "module", "schema_constant",
        "schema_version", "stage", "complete", "mode", "read_only",
        "executes", "human_approval_required", "next_gate", "reason",
    } | set(_CAPABILITY_FLAGS)
    for b in list_registered_bundles():
        assert set(b.keys()) == expected, b["bundle_id"]


def test_bundle_ids_match_numbers():
    for b in list_registered_bundles():
        assert b["bundle_id"] == "BUNDLE_" + str(b["bundle_number"])


# --- 2: latest completed / lookups -----------------------------------------

def test_latest_completed_bundle_is_bundle_47():
    latest = get_latest_completed_bundle()
    assert latest["bundle_number"] == 47
    assert latest["bundle_id"] == "BUNDLE_47"
    assert latest["name"] == (
        "Crypto-D1 Human-Approved Offline Acquisition Execution Boundary "
        "Contract"
    )


def test_latest_completed_bundle_label():
    assert get_latest_completed_bundle_label() == (
        "Bundle 47 - Crypto-D1 Human-Approved Offline Acquisition Execution "
        "Boundary Contract"
    )


def test_get_bundle_by_number():
    assert get_bundle_by_number(42)["name"] == (
        "Crypto-D1 Acquire Decision Contract"
    )
    assert get_bundle_by_number(46)["bundle_id"] == "BUNDLE_46"
    assert get_bundle_by_number(999) is None


def test_get_bundle_by_id():
    assert get_bundle_by_id("BUNDLE_47")["bundle_number"] == 47
    assert get_bundle_by_id("BUNDLE_45")["name"] == (
        "Crypto-D1 Offline Acquisition Plan Contract"
    )
    assert get_bundle_by_id("BUNDLE_404") is None


# --- 3: stage / next action match post-Bundle-47 state ----------------------

def test_current_stage_is_post_bundle47():
    assert CURRENT_STAGE == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_"
        "STILL_BLOCKED_NEXT_CONTRACT_REQUIRED"
    )
    assert get_current_stage() == CURRENT_STAGE
    assert "STILL_BLOCKED" in CURRENT_STAGE


def test_next_required_action_is_research_only_post_boundary_contract():
    assert NEXT_REQUIRED_ACTION == (
        "DEFINE_NEXT_RESEARCH_ONLY_CRYPTO_D1_POST_BOUNDARY_CONTRACT"
    )
    assert get_next_required_action() == NEXT_REQUIRED_ACTION
    assert "RESEARCH_ONLY" in NEXT_REQUIRED_ACTION
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION", "QA",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE"):
        assert banned not in NEXT_REQUIRED_ACTION, banned


# --- 4: every bundle is research-only and unlocks nothing real --------------

def test_every_bundle_research_only_read_only_no_execute():
    for b in list_registered_bundles():
        assert b["mode"] == "RESEARCH_ONLY", b["bundle_id"]
        assert b["read_only"] is True, b["bundle_id"]
        assert b["executes"] is False, b["bundle_id"]
        assert b["human_approval_required"] is True, b["bundle_id"]


def test_no_bundle_authorizes_real_world_action():
    for b in list_registered_bundles():
        assert b["authorizes_real_world_action"] is False, b["bundle_id"]


def test_no_bundle_unlocks_any_real_capability():
    for b in list_registered_bundles():
        for flag in _CAPABILITY_FLAGS:
            assert b[flag] is False, (b["bundle_id"], flag)


def test_registry_safety_posture_blocks_everything():
    posture = get_registry_safety_posture()
    assert posture["mode"] == "RESEARCH_ONLY"
    assert posture["read_only"] is True
    assert posture["human_approval_required"] is True
    for k, v in posture.items():
        if k in ("mode", "read_only", "human_approval_required"):
            continue
        assert v is False, f"posture flag {k} must be False"


# --- 5: schema constants readable + stable ----------------------------------

def test_schema_versions_readable_and_stable():
    for b in list_registered_bundles():
        assert isinstance(b["schema_version"], str) and b["schema_version"]
        assert b["schema_constant"].endswith("SCHEMA_VERSION")
    boundary = get_bundle_by_number(47)
    assert boundary["schema_version"] == (
        "strategy_factory_crypto_d1_human_approved_offline_acquisition_"
        "execution_boundary_contract.v1"
    )


def test_registry_version_stable():
    assert REGISTRY_VERSION == "v1"
    assert REGISTRY_MODE == "RESEARCH_ONLY"


# --- 6: determinism + mutation isolation -----------------------------------

def test_repeated_calls_are_identical():
    assert list_registered_bundles() == list_registered_bundles()
    assert list_completed_bundles() == list_completed_bundles()
    assert get_latest_completed_bundle() == get_latest_completed_bundle()
    assert get_registry_safety_posture() == get_registry_safety_posture()


def test_returned_structures_are_mutation_isolated():
    a = list_registered_bundles()
    a[0]["complete"] = False
    a[0]["executes"] = True
    assert list_registered_bundles()[0]["complete"] is True
    assert list_registered_bundles()[0]["executes"] is False
    p = get_registry_safety_posture()
    p["unlocks_paper_live"] = True
    assert get_registry_safety_posture()["unlocks_paper_live"] is False
    latest = get_latest_completed_bundle()
    latest["name"] = "TAMPERED"
    assert get_latest_completed_bundle()["name"] != "TAMPERED"


# --- 7: pure stdlib import-root audit ---------------------------------------

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 8: forbidden-surface audit (no IO / network / exec / control) ----------

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# --- 9: commander_2_safety allowlist ---------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_mission_flow_bundle_registry.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_mission_flow_bundle_registry.py"' in src
    )
