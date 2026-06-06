"""Tests for the Crypto-D1 Next Research Protocol (Block 95).

The module is a PURE, stdlib-only, read-only *protocol specification* for the
next Crypto-D1 research lane, defined after the research-only dry-run governance
lane was closed/archived (Bundle 54). It defines WHAT a future research lane
would compare on paper (BTC/ETH/SOL spot daily; four candidate strategy
families) and proves it executes nothing and unlocks nothing real.

Coverage:
- pure stdlib import-root audit + forbidden-surface audit + no-filesystem audit
- mode RESEARCH_ONLY, read_only True, executes False, human_approval_required
- universe is BTC/ETH/SOL, spot only, daily (D1) only
- all four candidate strategy families present and research-only
- future data requirements DEFINED but not acquired/loaded/inspected
- future validation steps DEFINED but not executed
- pass/watch/fail rules exist
- next bundle/action is research-only (no execution token)
- safety posture + safety gates all False
- deterministic repeated calls; mutation-isolated copies
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (
    PROTOCOL_SCHEMA_VERSION,
    PROTOCOL_ID,
    PROTOCOL_NAME,
    PROTOCOL_MODE,
    RESEARCH_UNIVERSE,
    MARKET_TYPE,
    TIMEFRAME,
    NEXT_REQUIRED_ACTION,
    PROTOCOL_SAFETY_POSTURE,
    get_protocol,
    get_research_universe,
    get_candidate_strategy_families,
    get_required_future_data_spec,
    get_required_future_validation_steps,
    get_prohibited_actions,
    get_safety_gates,
    get_pass_watch_fail_rules,
    get_next_bundle_recommendation,
    get_safety_posture,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_next_research_protocol.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_EXPECTED_FAMILY_IDS = (
    "MOMENTUM_TREND_CONTINUATION",
    "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
    "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    "REGIME_FILTER_LAYER",
)


# --- 1: identity + mode -----------------------------------------------------

def test_protocol_identity_and_mode():
    assert PROTOCOL_ID == "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    assert PROTOCOL_NAME == "Crypto-D1 Strategy Candidate Protocol v1"
    assert PROTOCOL_MODE == "RESEARCH_ONLY"
    assert PROTOCOL_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_next_research_protocol.v1"
    )


def test_top_level_flags_are_read_only_no_execute():
    p = get_protocol()
    assert p["protocol_mode"] == "RESEARCH_ONLY"
    assert p["read_only"] is True
    assert p["executes"] is False
    assert p["human_approval_required"] is True


# --- 2: universe / market / timeframe ---------------------------------------

def test_universe_is_btc_eth_sol():
    assert tuple(RESEARCH_UNIVERSE) == ("BTC", "ETH", "SOL")
    universe = get_research_universe()
    assert universe == ["BTC", "ETH", "SOL"]
    assert get_protocol()["research_universe"] == ["BTC", "ETH", "SOL"]


def test_spot_only_and_daily_only():
    assert MARKET_TYPE == "SPOT"
    assert TIMEFRAME == "D1"
    p = get_protocol()
    assert p["market_type"] == "SPOT"
    assert p["timeframe"] == "D1"


# --- 3: candidate strategy families -----------------------------------------

def test_all_four_strategy_families_present():
    fams = get_candidate_strategy_families()
    ids = tuple(f["family_id"] for f in fams)
    assert ids == _EXPECTED_FAMILY_IDS
    assert len(fams) == 4


def test_each_family_is_research_only_and_well_formed():
    for f in get_candidate_strategy_families():
        assert f["research_only"] is True, f["family_id"]
        assert set(f.keys()) == {
            "family_id", "name", "concept",
            "definition_points", "possible_later_metrics", "research_only",
        }
        assert isinstance(f["name"], str) and f["name"]
        assert isinstance(f["concept"], str) and f["concept"]
        assert len(f["definition_points"]) >= 3
        assert len(f["possible_later_metrics"]) >= 2


def test_regime_layer_must_not_be_curve_fit():
    fams = {f["family_id"]: f for f in get_candidate_strategy_families()}
    regime = fams["REGIME_FILTER_LAYER"]
    joined = " ".join(regime["definition_points"]).lower()
    assert "curve fit" in joined
    assert "gate" in joined


# --- 4: future data requirements DEFINED but not executed -------------------

def test_future_data_spec_defined_not_acquired():
    spec = get_required_future_data_spec()
    assert tuple(spec["assets"]) == ("BTC", "ETH", "SOL")
    assert spec["market_type"] == "SPOT"
    assert spec["timeframe"] == "D1"
    assert spec["timezone"] == "UTC"
    # provenance requirements are declared...
    assert spec["source_provenance_required"] is True
    assert spec["checksums_required"] is True
    assert spec["freeze_manifest_required"] is True
    assert spec["fee_assumptions_required"] is True
    assert spec["slippage_assumptions_required"] is True
    # ...but nothing is fetched, keyed, accessed, acquired, loaded, inspected
    assert spec["live_fetch"] is False
    assert spec["uses_api_keys"] is False
    assert spec["exchange_account_access"] is False
    assert spec["acquired"] is False
    assert spec["inspected"] is False
    assert spec["loaded"] is False


def test_future_validation_steps_defined_not_executed():
    steps = get_required_future_validation_steps()
    step_ids = {s["step_id"] for s in steps}
    assert step_ids == {
        "FUTURE_DATA_QA",
        "FUTURE_BASELINE_TEST",
        "FUTURE_CANDIDATE_BACKTEST",
        "FUTURE_OOS_SPLIT",
        "FUTURE_ROBUSTNESS_CHECKS",
        "FUTURE_PASS_WATCH_FAIL_MEMO",
    }
    for s in steps:
        assert s["executed"] is False, s["step_id"]
        assert isinstance(s["description"], str) and s["description"]


# --- 5: pass / watch / fail rules -------------------------------------------

def test_pass_watch_fail_rules_exist():
    rules = get_pass_watch_fail_rules()
    assert set(rules.keys()) == {"PASS", "WATCH", "FAIL"}
    for bucket, criteria in rules.items():
        assert len(criteria) >= 3, bucket
        for c in criteria:
            assert isinstance(c, str) and c


def test_pass_requires_multiple_assets_and_oos():
    rules = get_pass_watch_fail_rules()
    joined = " ".join(rules["PASS"]).lower()
    assert "multiple assets" in joined
    assert "out-of-sample" in joined


# --- 6: prohibited actions + safety gates / posture all blocked -------------

def test_prohibited_actions_listed():
    prohibited = get_prohibited_actions()
    joined = " ".join(prohibited).lower()
    for needle in (
        "real data acquisition", "api calls", "backtest", "simulation",
        "order logic", "trade signal", "automation",
    ):
        assert needle in joined, needle


def test_safety_gates_all_false():
    gates = get_safety_gates()
    assert gates  # non-empty
    assert all(v is False for v in gates.values())


def test_safety_posture_all_false_except_mode_readonly_humangate():
    posture = get_safety_posture()
    assert posture["mode"] == "RESEARCH_ONLY"
    assert posture["read_only"] is True
    assert posture["human_approval_required"] is True
    for k, v in posture.items():
        if k in ("mode", "read_only", "human_approval_required"):
            continue
        assert v is False, f"posture flag {k} must be False"
    assert PROTOCOL_SAFETY_POSTURE["executes"] is False


# --- 7: next bundle / action is research-only -------------------------------

def test_next_bundle_recommendation_is_research_only():
    rec = get_next_bundle_recommendation()
    assert rec["bundle_number"] == 55
    assert rec["bundle_id"] == "BUNDLE_55"
    assert rec["name"] == "Crypto-D1 Strategy Candidate Protocol Contract"
    assert rec["mode"] == "RESEARCH_ONLY"
    assert rec["read_only"] is True
    assert rec["executes"] is False
    assert rec["next_required_action"] == NEXT_REQUIRED_ACTION


def test_next_required_action_has_no_execution_token():
    assert NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )
    assert NEXT_REQUIRED_ACTION.startswith("BUILD_")
    assert NEXT_REQUIRED_ACTION.endswith("_CONTRACT")
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION", "QA",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE", "ORDER", "SIGNAL"):
        assert banned not in NEXT_REQUIRED_ACTION, banned


# --- 8: full protocol shape -------------------------------------------------

def test_protocol_has_all_required_sections():
    p = get_protocol()
    assert set(p.keys()) == {
        "protocol_id", "protocol_name", "protocol_mode", "schema_version",
        "read_only", "executes", "human_approval_required",
        "research_universe", "market_type", "timeframe",
        "candidate_strategy_families", "required_future_data_spec",
        "required_future_validation_steps", "prohibited_actions",
        "safety_gates", "safety_posture", "pass_watch_fail_rules",
        "next_bundle_recommendation", "next_required_action", "rationale",
    }
    assert isinstance(p["rationale"], str) and p["rationale"]


# --- 9: determinism + mutation isolation ------------------------------------

def test_repeated_calls_are_identical():
    assert get_protocol() == get_protocol()
    assert get_candidate_strategy_families() == get_candidate_strategy_families()
    assert get_required_future_data_spec() == get_required_future_data_spec()
    assert get_pass_watch_fail_rules() == get_pass_watch_fail_rules()
    assert get_safety_gates() == get_safety_gates()


def test_returned_structures_are_mutation_isolated():
    p = get_protocol()
    p["protocol_mode"] = "TAMPERED"
    p["research_universe"].append("DOGE")
    p["candidate_strategy_families"][0]["research_only"] = False
    p["safety_gates"]["backtest"] = True
    p["required_future_data_spec"]["acquired"] = True
    fresh = get_protocol()
    assert fresh["protocol_mode"] == "RESEARCH_ONLY"
    assert fresh["research_universe"] == ["BTC", "ETH", "SOL"]
    assert fresh["candidate_strategy_families"][0]["research_only"] is True
    assert fresh["safety_gates"]["backtest"] is False
    assert fresh["required_future_data_spec"]["acquired"] is False
    # standalone getters are protected too
    get_safety_gates()["paper_or_live"] = True
    assert get_safety_gates()["paper_or_live"] is False


# --- 10: pure stdlib import-root audit --------------------------------------

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io", "ccxt", "freqtrade"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 11: forbidden-surface audit (no IO / network / exec / control) ---------

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
        "os.environ", "os.getenv", "getenv(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# --- 12: commander_2_safety allowlist ---------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_next_research_protocol.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_next_research_protocol.py"'
        in src
    )
