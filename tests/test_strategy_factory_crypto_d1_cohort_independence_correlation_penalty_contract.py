"""Tests for the Crypto-D1 Cohort Independence / Correlation Penalty Contract
(Block 132).

The contract is a pure, stdlib-only, read-only paper contract. It groups a
static set of evidence records into cohorts and assigns each cohort exactly one
independence label (INDEPENDENT / CORRELATED / DUPLICATE / OPEN_OBSERVATION_ONLY
/ EXTERNAL_EVIDENCE_ONLY / INSUFFICIENT_SAMPLE) and authorizes nothing. These
tests assert the schema, the cohort/correlation model, determinism, source
isolation (no file writes / no forbidden imports), validation, render, and the
two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract import (  # noqa: E501
    COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS,
    COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS,
    COHORT_INDEPENDENCE_CORE_RULE,
    COHORT_INDEPENDENCE_CORRELATION_SIGNALS,
    COHORT_INDEPENDENCE_CURRENT_STAGE,
    COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS,
    COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS,
    COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS,
    COHORT_INDEPENDENCE_GATE_LOCK_FLAGS,
    COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS,
    COHORT_INDEPENDENCE_LABEL,
    COHORT_INDEPENDENCE_LABELS,
    COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT,
    COHORT_INDEPENDENCE_MODE,
    COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION,
    COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES,
    COHORT_INDEPENDENCE_OPEN_STATUS_TAGS,
    COHORT_INDEPENDENCE_SAFETY_POSTURE,
    COHORT_INDEPENDENCE_SCHEMA_VERSION,
    COHORT_INDEPENDENCE_STATUS,
    COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS,
    DEFAULT_SAMPLE_EVIDENCE,
    LABEL_CORRELATED,
    LABEL_DUPLICATE,
    LABEL_EXTERNAL_EVIDENCE_ONLY,
    LABEL_INDEPENDENT,
    LABEL_INSUFFICIENT_SAMPLE,
    LABEL_OPEN_OBSERVATION_ONLY,
    assess_cohort_independence,
    build_crypto_d1_cohort_independence_correlation_penalty_contract,
    render_crypto_d1_cohort_independence_correlation_penalty_contract_markdown,
    validate_crypto_d1_cohort_independence_correlation_penalty_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.py"
)

_BUILD = build_crypto_d1_cohort_independence_correlation_penalty_contract
_VALIDATE = validate_crypto_d1_cohort_independence_correlation_penalty_contract
_RENDER = render_crypto_d1_cohort_independence_correlation_penalty_contract_markdown


def _rec(rid, symbol=None, direction=None, status="closed", pnl=0.0, **extra):
    record = {"id": rid, "status": status, "pnl": pnl}
    if symbol is not None:
        record["symbol"] = symbol
    if direction is not None:
        record["direction"] = direction
    record.update(extra)
    return record


def _labels(result):
    return [c["independence_label"] for c in result["cohorts"]]


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert COHORT_INDEPENDENCE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.v1"
    )
    assert COHORT_INDEPENDENCE_LABEL == (
        "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert COHORT_INDEPENDENCE_STATUS == (
        "READ_ONLY_CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
    )
    assert COHORT_INDEPENDENCE_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in COHORT_INDEPENDENCE_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
    )
    assert COHORT_INDEPENDENCE_CURRENT_STAGE == (
        "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT_REQUIRED"
    )


def test_independence_labels_are_exactly_the_six_allowed():
    assert COHORT_INDEPENDENCE_LABELS == (
        LABEL_INDEPENDENT,
        LABEL_CORRELATED,
        LABEL_DUPLICATE,
        LABEL_OPEN_OBSERVATION_ONLY,
        LABEL_EXTERNAL_EVIDENCE_ONLY,
        LABEL_INSUFFICIENT_SAMPLE,
    )
    assert set(COHORT_INDEPENDENCE_LABELS) == {
        "INDEPENDENT",
        "CORRELATED",
        "DUPLICATE",
        "OPEN_OBSERVATION_ONLY",
        "EXTERNAL_EVIDENCE_ONLY",
        "INSUFFICIENT_SAMPLE",
    }


def test_correlation_signals_cover_the_required_dimensions():
    for signal in (
        "same_symbol_and_direction",
        "same_macro_event",
        "same_market_regime",
        "same_open_window_timing",
        "same_close_window_timing",
        "same_signal_family",
    ):
        assert signal in COHORT_INDEPENDENCE_CORRELATION_SIGNALS


def test_min_independent_booked_cohorts_threshold():
    assert (
        COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT
        == 3
    )


def test_source_and_status_tag_families():
    assert "trade" in COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS
    for tag in ("whale", "funding_rate", "btc_cycle", "daily_alpha"):
        assert tag in COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS
    assert "closed" in COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS
    assert "booked" in COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS
    assert "open" in COHORT_INDEPENDENCE_OPEN_STATUS_TAGS
    assert "unrealized" in COHORT_INDEPENDENCE_OPEN_STATUS_TAGS


def test_safety_posture_three_true_facts_all_else_false():
    posture = COHORT_INDEPENDENCE_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


def test_observation_only_lanes_include_open_pnl_and_external_sources():
    lanes = COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
    assert "open_unrealized_pnl" in lanes
    assert "daily_alpha_brief" in lanes
    assert "hyperliquid_whale_evidence" in lanes


# --------------------------------------------------------------------------- #
# Cohort / correlation model behavior (the user's example cases)
# --------------------------------------------------------------------------- #
def test_eth_same_macro_is_one_correlated_cohort_not_three_wins():
    eth = [
        _rec("E", "ETH", "short", "closed", 1.4, macro_event="eth_dump"),
        _rec("E2", "ETH", "short", "closed", 0.9, macro_event="eth_dump"),
        _rec("F2", "ETH", "short", "closed", 1.1, macro_event="eth_dump"),
    ]
    result = assess_cohort_independence(eth)
    assert result["cohort_count"] == 1
    assert result["correlated_cluster_count"] == 1
    assert _labels(result) == [LABEL_CORRELATED]
    assert result["positive_independent_booked_cohort_count"] == 0
    assert result["can_support_promote_to_review"] is False


def test_avax_same_symbol_same_direction_is_duplicate():
    avax = [
        _rec("a1", "AVAX", "short", "closed", 1.0),
        _rec("a2", "AVAX", "short", "closed", 0.5),
    ]
    result = assess_cohort_independence(avax)
    assert result["cohort_count"] == 1
    assert result["duplicate_count"] == 1
    assert _labels(result) == [LABEL_DUPLICATE]


def test_simultaneous_cross_symbol_shorts_are_correlated_macro_thesis():
    cluster = [
        _rec("s", "SOL", "short", "closed", 1.0, entry_window="2026-05-10",
             market_regime="crypto_down"),
        _rec("ar", "ARB", "short", "closed", 0.8, entry_window="2026-05-10",
             market_regime="crypto_down"),
        _rec("av", "AVAX", "short", "closed", 0.6, entry_window="2026-05-10",
             market_regime="crypto_down"),
    ]
    result = assess_cohort_independence(cluster)
    assert result["cohort_count"] == 1
    assert result["correlated_cluster_count"] == 1
    assert _labels(result) == [LABEL_CORRELATED]


def test_single_booked_positive_is_insufficient_sample():
    result = assess_cohort_independence(
        [_rec("ada", "ADA", "short", "closed", 1.2, setup_family="F")]
    )
    assert _labels(result) == [LABEL_INSUFFICIENT_SAMPLE]
    assert result["cohorts"][0]["independence_score"] == 0.5
    assert result["positive_independent_booked_cohort_count"] == 1
    assert result["can_support_promote_to_review"] is False


def test_single_booked_negative_is_not_positive_proof():
    result = assess_cohort_independence(
        [_rec("xrp", "XRP", "long", "closed", -0.7, setup_family="G")]
    )
    assert _labels(result) == [LABEL_INSUFFICIENT_SAMPLE]
    assert result["cohorts"][0]["independence_score"] == 0.1
    assert result["positive_independent_booked_cohort_count"] == 0


def test_open_unrealized_positions_are_observation_only():
    opens = [
        _rec("o1", "AVAX", "short", "open", 2.0),
        _rec("o2", "SOL", "short", "unrealized", 1.0),
        _rec("o3", "ARB", "short", "open", 0.5),
    ]
    result = assess_cohort_independence(opens)
    assert result["open_observation_count"] == 3
    assert result["booked_count"] == 0
    assert _labels(result) == [LABEL_OPEN_OBSERVATION_ONLY] * 3
    assert result["positive_independent_booked_cohort_count"] == 0
    assert result["can_support_promote_to_review"] is False


def test_external_evidence_is_never_an_independent_trade_cohort():
    ext = [
        _rec("w", "BTC", None, "closed", 5.0, source="whale"),
        _rec("f", "BTC", None, "closed", 0.0, source="funding_rate"),
        _rec("c", None, None, "closed", 0.0, source="btc_cycle"),
        _rec("da", None, None, "closed", 0.0, source="daily_alpha"),
    ]
    result = assess_cohort_independence(ext)
    assert result["external_evidence_count"] == 4
    assert result["booked_count"] == 0
    assert _labels(result) == [LABEL_EXTERNAL_EVIDENCE_ONLY] * 4
    assert result["can_support_promote_to_review"] is False


def test_three_truly_independent_positive_cohorts_can_support_review():
    promo = [
        _rec("i1", "BTC", "long", "closed", 1.0, macro_event="m1",
             setup_family="A", market_regime="r1", entry_window="w1"),
        _rec("i2", "ETH", "short", "closed", 1.0, macro_event="m2",
             setup_family="B", market_regime="r2", entry_window="w2"),
        _rec("i3", "SOL", "long", "closed", 1.0, macro_event="m3",
             setup_family="C", market_regime="r3", entry_window="w3"),
    ]
    result = assess_cohort_independence(promo)
    assert result["positive_independent_booked_cohort_count"] == 3
    assert _labels(result) == [LABEL_INDEPENDENT] * 3
    assert all(c["independence_score"] == 1.0 for c in result["cohorts"])
    assert result["can_support_promote_to_review"] is True


def test_two_independent_positive_cohorts_are_still_insufficient():
    promo = [
        _rec("i1", "BTC", "long", "closed", 1.0, macro_event="m1",
             setup_family="A"),
        _rec("i2", "ETH", "short", "closed", 1.0, macro_event="m2",
             setup_family="B"),
    ]
    result = assess_cohort_independence(promo)
    assert result["positive_independent_booked_cohort_count"] == 2
    assert _labels(result) == [LABEL_INSUFFICIENT_SAMPLE] * 2
    assert result["can_support_promote_to_review"] is False


def test_empty_payload_has_no_cohorts_and_supports_nothing():
    for payload in ([], {}, None):
        result = assess_cohort_independence(payload)
        assert result["cohort_count"] == 0
        assert result["can_support_promote_to_review"] is False


def test_default_sample_is_one_correlated_cohort():
    contract = _BUILD()
    assert contract["correlated_cluster_count"] == 1
    assert contract["cohort_count"] == 1
    assert contract["cohorts"][0]["independence_label"] == LABEL_CORRELATED
    assert contract["can_support_promote_to_review"] is False


# --------------------------------------------------------------------------- #
# Block / safety refusal
# --------------------------------------------------------------------------- #
def _three_independent():
    return [
        _rec("i1", "BTC", "long", "closed", 1.0, macro_event="m1",
             setup_family="A"),
        _rec("i2", "ETH", "short", "closed", 1.0, macro_event="m2",
             setup_family="B"),
        _rec("i3", "SOL", "long", "closed", 1.0, macro_event="m3",
             setup_family="C"),
    ]


def test_authorization_flag_forces_block_and_blocks_support():
    for flag in COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS:
        result = assess_cohort_independence(
            {"evidence": _three_independent(), flag: True}
        )
        assert result["block_reasons"], flag
        assert result["can_support_promote_to_review"] is False, flag


def test_gate_unlock_request_forces_block():
    for flag in COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS:
        result = assess_cohort_independence({"evidence": [], flag: True})
        assert result["block_reasons"], flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in COHORT_INDEPENDENCE_GATE_LOCK_FLAGS:
        result = assess_cohort_independence({"evidence": [], flag: False})
        assert result["block_reasons"], flag


def test_forbidden_promotion_request_forces_block():
    for flag in COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = assess_cohort_independence({"evidence": [], flag: True})
        assert result["block_reasons"], flag


def test_executable_signal_field_on_a_record_forces_block():
    for field in COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS:
        record = _rec("x", "ETH", "short", "closed", 1.0, macro_event="eth_dump")
        record[field] = "do something"
        result = assess_cohort_independence([record])
        assert result["block_reasons"], field
        assert result["can_support_promote_to_review"] is False, field


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    eth = [
        _rec("E", "ETH", "short", "closed", 1.4, macro_event="eth_dump"),
        _rec("E2", "ETH", "short", "closed", 0.9, macro_event="eth_dump"),
    ]
    assert assess_cohort_independence(eth) == assess_cohort_independence(eth)


def test_cohort_order_independent_of_input_order():
    a = _three_independent()
    b = list(reversed(a))
    ra = assess_cohort_independence(a)
    rb = assess_cohort_independence(b)
    assert ra["cohorts"] == rb["cohorts"]
    assert ra["positive_independent_booked_cohort_count"] == (
        rb["positive_independent_booked_cohort_count"]
    )


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = {
        "evidence": [
            _rec("E", "ETH", "short", "closed", 1.4, macro_event="eth_dump")
        ],
    }
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["penalty_reasons"].append("tampered")
    assert "tampered" not in c2["penalty_reasons"]
    assert DEFAULT_SAMPLE_EVIDENCE["evidence"][0]["id"] == "E"


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == ()
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["labels_ok"] is True
    assert verdict["signals_ok"] is True


def test_every_label_path_validates():
    payloads = [
        [],  # empty
        [_rec("ada", "ADA", "short", "closed", 1.2, setup_family="F")],
        [_rec("xrp", "XRP", "long", "closed", -0.7, setup_family="G")],
        [
            _rec("a1", "AVAX", "short", "closed", 1.0),
            _rec("a2", "AVAX", "short", "closed", 0.5),
        ],
        _three_independent(),
        [_rec("o1", "AVAX", "short", "open", 2.0)],
        [_rec("w", "BTC", None, "closed", 5.0, source="whale")],
        {"evidence": [], "authorizes_trading": True},  # block
    ]
    for payload in payloads:
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_contract():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = _BUILD()
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Cohort Independence / Correlation Penalty Contract"
    )
    assert "## Assessment Summary" in text
    assert "## Cohorts" in text
    assert "## No Execution Authorization" in text


def test_actionable_guidance_has_no_execution_verbs():
    contract = _BUILD()
    for field in (
        "assessment_summary_section",
        "cohort_section",
        "observation_only_section",
        "no_execution_authorization_section",
        "explanations",
    ):
        for line in contract[field]:
            tokens = set(
                "".join(c if c.isalpha() else " " for c in line.lower()).split()
            )
            for term in COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS:
                assert term not in tokens, (field, term, line)


def test_can_support_review_unlocks_no_gate():
    contract = _BUILD(_three_independent())
    assert contract["can_support_promote_to_review"] is True
    assert contract["promotes_beyond_review"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["assessment"]["authorizes_nothing"] is True


# --------------------------------------------------------------------------- #
# AST purity: stdlib-only, no I/O, no forbidden imports
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORTS = {"__future__", "typing"}
_FORBIDDEN_CALL_NAMES = {"open", "__import__", "eval", "exec", "compile", "input"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "http",
    "urllib",
    "importlib",
    "pandas",
    "numpy",
    "ccxt",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_stdlib_typing_only():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in _FORBIDDEN_CALL_NAMES, func.id


def test_module_has_no_forbidden_module_tokens():
    tree = _module_ast()
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD([_rec("E", "ETH", "short", "closed", 1.4, macro_event="eth_dump")])
    after = set(tmp_path.iterdir())
    assert before == after


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
