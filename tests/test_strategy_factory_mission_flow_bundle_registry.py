"""Tests for the Strategy Factory Mission Flow Bundle Registry (Block 79).

The registry is a PURE, stdlib-only, read-only source of truth for completed
Strategy Factory bundle metadata. It lets the JARVIS Mission Flow feed follow
the pipeline from structured metadata instead of hardcoding each bundle inline.

Coverage:
- registry includes Bundles 42 through 54, all complete
- latest completed bundle is Bundle 54
- recognized research-only protocol (Block 95): Crypto-D1 Strategy Candidate
  Protocol v1 (RESEARCH_ONLY, read_only, no execute, BTC/ETH/SOL, spot, D1,
  four candidate families, unlocks nothing real, creates no new bundle)
- current_stage / next_required_action match the post-protocol-definition state
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
    LATEST_COMPLETED_PROTOCOL,
    list_registered_bundles,
    list_completed_bundles,
    get_latest_completed_bundle,
    get_bundle_by_number,
    get_bundle_by_id,
    get_latest_completed_bundle_label,
    get_latest_completed_protocol,
    get_latest_completed_protocol_label,
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

def test_registry_includes_bundles_42_through_54():
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_all_registered_bundles_complete():
    for b in list_registered_bundles():
        assert b["complete"] is True, b["bundle_id"]
    assert len(list_completed_bundles()) == 13


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

def test_latest_completed_bundle_is_bundle_54():
    latest = get_latest_completed_bundle()
    assert latest["bundle_number"] == 54
    assert latest["bundle_id"] == "BUNDLE_54"
    assert latest["name"] == (
        "Crypto-D1 Research-Only Dry-Run Research Archive or Closure Contract"
    )


def test_latest_completed_bundle_label():
    assert get_latest_completed_bundle_label() == (
        "Bundle 54 - Crypto-D1 Research-Only Dry-Run Research Archive or "
        "Closure Contract"
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


# --- 3: stage / next action match post-protocol-definition state ------------

def test_current_stage_is_post_protocol_definition():
    assert CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINED_NEXT_CONTRACT_REQUIRED"
    )
    assert get_current_stage() == CURRENT_STAGE
    assert "STRATEGY_CANDIDATE_PROTOCOL" in CURRENT_STAGE
    assert "DEFINED" in CURRENT_STAGE
    assert "CONTRACT_REQUIRED" in CURRENT_STAGE
    # a safe post-protocol-definition research-only stage, not real execution
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION", "QA",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "AUTOMATION"):
        assert banned not in CURRENT_STAGE, banned


def test_next_required_action_is_build_candidate_protocol_contract():
    assert NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )
    assert get_next_required_action() == NEXT_REQUIRED_ACTION
    assert NEXT_REQUIRED_ACTION.startswith("BUILD_")
    assert "PROTOCOL_CONTRACT" in NEXT_REQUIRED_ACTION
    # it names building a research-only paper contract, not real execution
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
    next_step = get_bundle_by_number(48)
    assert next_step["schema_constant"] == "NEXT_STEP_SCHEMA_VERSION"
    assert next_step["schema_version"] == (
        "strategy_factory_crypto_d1_post_boundary_research_only_next_step_"
        "contract.v1"
    )
    preview = get_bundle_by_number(49)
    assert preview["schema_constant"] == "PREVIEW_SCHEMA_VERSION"
    assert preview["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_preview_contract.v1"
    )
    review = get_bundle_by_number(50)
    assert review["schema_constant"] == "REVIEW_SCHEMA_VERSION"
    assert review["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_review_contract.v1"
    )
    decision = get_bundle_by_number(51)
    assert decision["schema_constant"] == "DECISION_SCHEMA_VERSION"
    assert decision["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_decision_contract.v1"
    )
    decision_review = get_bundle_by_number(52)
    assert decision_review["schema_constant"] == "DECISION_REVIEW_SCHEMA_VERSION"
    assert decision_review["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_decision_review_"
        "contract.v1"
    )
    final_decision = get_bundle_by_number(53)
    assert final_decision["schema_constant"] == "FINAL_DECISION_SCHEMA_VERSION"
    assert final_decision["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_final_decision_"
        "contract.v1"
    )
    archive_or_closure = get_bundle_by_number(54)
    assert archive_or_closure["schema_constant"] == (
        "ARCHIVE_OR_CLOSURE_SCHEMA_VERSION"
    )
    assert archive_or_closure["schema_version"] == (
        "strategy_factory_crypto_d1_research_only_dry_run_research_archive_"
        "or_closure_contract.v1"
    )


def test_bundle_48_is_research_only_and_unlocks_nothing():
    b48 = get_bundle_by_number(48)
    assert b48 is not None
    assert b48["bundle_id"] == "BUNDLE_48"
    assert b48["mode"] == "RESEARCH_ONLY"
    assert b48["read_only"] is True
    assert b48["executes"] is False
    assert b48["human_approval_required"] is True
    assert b48["complete"] is True
    assert b48["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_post_boundary_"
        "research_only_next_step_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b48[flag] is False, flag


def test_bundle_49_is_research_only_and_unlocks_nothing():
    b49 = get_bundle_by_number(49)
    assert b49 is not None
    assert b49["bundle_id"] == "BUNDLE_49"
    assert b49["mode"] == "RESEARCH_ONLY"
    assert b49["read_only"] is True
    assert b49["executes"] is False
    assert b49["human_approval_required"] is True
    assert b49["complete"] is True
    assert b49["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_preview_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b49[flag] is False, flag


def test_bundle_50_is_research_only_and_unlocks_nothing():
    b50 = get_bundle_by_number(50)
    assert b50 is not None
    assert b50["bundle_id"] == "BUNDLE_50"
    assert b50["mode"] == "RESEARCH_ONLY"
    assert b50["read_only"] is True
    assert b50["executes"] is False
    assert b50["human_approval_required"] is True
    assert b50["complete"] is True
    assert b50["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_review_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b50[flag] is False, flag


def test_bundle_51_is_research_only_and_unlocks_nothing():
    b51 = get_bundle_by_number(51)
    assert b51 is not None
    assert b51["bundle_id"] == "BUNDLE_51"
    assert b51["mode"] == "RESEARCH_ONLY"
    assert b51["read_only"] is True
    assert b51["executes"] is False
    assert b51["human_approval_required"] is True
    assert b51["complete"] is True
    assert b51["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_decision_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b51[flag] is False, flag


def test_bundle_52_is_research_only_and_unlocks_nothing():
    b52 = get_bundle_by_number(52)
    assert b52 is not None
    assert b52["bundle_id"] == "BUNDLE_52"
    assert b52["mode"] == "RESEARCH_ONLY"
    assert b52["read_only"] is True
    assert b52["executes"] is False
    assert b52["human_approval_required"] is True
    assert b52["complete"] is True
    assert b52["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_decision_review_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b52[flag] is False, flag


def test_bundle_53_is_research_only_and_unlocks_nothing():
    b53 = get_bundle_by_number(53)
    assert b53 is not None
    assert b53["bundle_id"] == "BUNDLE_53"
    assert b53["mode"] == "RESEARCH_ONLY"
    assert b53["read_only"] is True
    assert b53["executes"] is False
    assert b53["human_approval_required"] is True
    assert b53["complete"] is True
    assert b53["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_final_decision_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b53[flag] is False, flag


def test_bundle_54_is_research_only_and_unlocks_nothing():
    b54 = get_bundle_by_number(54)
    assert b54 is not None
    assert b54["bundle_id"] == "BUNDLE_54"
    assert b54["mode"] == "RESEARCH_ONLY"
    assert b54["read_only"] is True
    assert b54["executes"] is False
    assert b54["human_approval_required"] is True
    assert b54["complete"] is True
    assert b54["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_research_only_"
        "dry_run_research_archive_or_closure_contract"
    )
    for flag in _CAPABILITY_FLAGS:
        assert b54[flag] is False, flag


# --- 5b: recognized research-only protocol (Block 95) -----------------------

_EXPECTED_FAMILY_IDS = [
    "MOMENTUM_TREND_CONTINUATION",
    "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
    "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    "REGIME_FILTER_LAYER",
]


def test_latest_completed_protocol_label():
    assert LATEST_COMPLETED_PROTOCOL == (
        "Block 95 - Crypto-D1 Strategy Candidate Protocol v1"
    )
    assert get_latest_completed_protocol_label() == LATEST_COMPLETED_PROTOCOL
    # the label does not name a trading-execution stage
    for banned in ("BACKTEST", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "EXECUTION"):
        assert banned not in LATEST_COMPLETED_PROTOCOL.upper(), banned


def test_registry_recognizes_strategy_candidate_protocol_v1():
    p = get_latest_completed_protocol()
    assert p["protocol_id"] == "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    assert p["protocol_name"] == "Crypto-D1 Strategy Candidate Protocol v1"
    assert p["module"] == (
        "sparta_commander.strategy_factory_crypto_d1_next_research_protocol"
    )
    assert p["schema_constant"] == "PROTOCOL_SCHEMA_VERSION"
    assert p["schema_version"] == (
        "strategy_factory_crypto_d1_next_research_protocol.v1"
    )
    assert p["defined"] is True
    assert p["complete"] is True


def test_recognized_protocol_is_research_only_read_only_no_execute():
    p = get_latest_completed_protocol()
    assert p["mode"] == "RESEARCH_ONLY"
    assert p["read_only"] is True
    assert p["executes"] is False
    assert p["human_approval_required"] is True


def test_recognized_protocol_universe_is_btc_eth_sol_spot_d1():
    p = get_latest_completed_protocol()
    assert p["research_universe"] == ["BTC", "ETH", "SOL"]
    assert p["market_type"] == "SPOT"
    assert p["timeframe"] == "D1"


def test_recognized_protocol_has_four_candidate_families():
    p = get_latest_completed_protocol()
    assert p["candidate_family_ids"] == _EXPECTED_FAMILY_IDS
    assert len(p["candidate_family_ids"]) == 4
    assert p["candidate_family_names"] == [
        "Momentum / Trend Continuation",
        "Breakout / Donchian / Volatility Expansion",
        "Pullback / Mean Reversion After Strong Trend",
        "Regime Filter Layer",
    ]


def test_recognized_protocol_authorizes_nothing_unlocks_nothing():
    p = get_latest_completed_protocol()
    for flag in _CAPABILITY_FLAGS:
        assert p[flag] is False, flag
    assert p["next_required_action"] == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )
    reason = p["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_recognized_protocol_does_not_change_latest_bundle():
    # Recognizing the protocol must NOT invent a new execution bundle; the
    # highest completed bundle is still Bundle 54.
    assert get_latest_completed_bundle()["bundle_number"] == 54
    nums = sorted(b["bundle_number"] for b in list_registered_bundles())
    assert nums == [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]


def test_recognized_protocol_deterministic_and_mutation_isolated():
    assert get_latest_completed_protocol() == get_latest_completed_protocol()
    p = get_latest_completed_protocol()
    p["executes"] = True
    p["research_universe"].append("TAMPERED")
    p["candidate_family_ids"].append("TAMPERED")
    fresh = get_latest_completed_protocol()
    assert fresh["executes"] is False
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_family_ids"] == _EXPECTED_FAMILY_IDS


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
