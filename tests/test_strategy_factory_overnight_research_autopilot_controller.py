"""Tests for the SPARTA Overnight Research Autopilot Controller (Block 152).

This module is a PURE, stdlib-only, *read-only* RESEARCH_ONLY_AUTOPILOT planning
controller. It reasons -- on paper only -- over a static caller-supplied status summary
and emits a BOUNDED plan: which safe research-only paper bundles to prepare next, which
paths each may touch, which it may not, which scoped tests to run, and a commit / push
POLICY that keeps every commit and every push gated behind explicit per-run human
approval. It stages nothing, commits nothing, pushes nothing, fetches nothing, calls no
provider / API / network, reads no credential / .env, runs no QA / backtest, touches no
broker / exchange / account, writes no runtime / dashboard output, and unlocks no gate.

These tests assert: schema / constants; mission-flow truth sync against the live status
module; the bounded bundle queue and decision categories; that the default plan is a
safe bounded RUN with commit / push human-gated; that any authorization / gate-unlock /
boundary-crossing flag forces a HOLD with no automated step; that a zero / negative
budget falls back to HOLD; that every capability flag is False and every gate stays
locked; commit / push policy strings; that allowed paths never fall under a forbidden
path; that the generated guidance carries no execution / trade verbs; determinism /
caller isolation; validation tamper rejections; render; AST purity (only __future__ /
typing / sparta_commander roots, no os / json / csv / network / credential modules, no
os.environ access, NO open / write_* call); and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_overnight_research_autopilot_controller import (  # noqa: E501
    COMMIT_POLICY,
    CONTROLLER_BOUNDARY_CROSSING_FLAGS,
    CONTROLLER_CORE_RULE,
    CONTROLLER_FORBIDDEN_PATHS,
    CONTROLLER_FORBIDDEN_TRADE_TERMS,
    CONTROLLER_HARD_STOP_RULES,
    CONTROLLER_LABEL,
    CONTROLLER_MODE,
    CONTROLLER_SAFETY_FLAGS,
    CONTROLLER_SCHEMA_VERSION,
    CONTROLLER_STATUS,
    DECISION_CATEGORIES,
    DECISION_HOLD,
    DECISION_RUN,
    DEFAULT_AUTOPILOT_BUNDLE_QUEUE,
    DEFAULT_MAX_SAFE_BUNDLES,
    MAX_SAFE_BUNDLES_CEILING,
    PUSH_POLICY,
    allowed_paths_for_bundle,
    assess_overnight_research_autopilot,
    build_overnight_research_autopilot_plan,
    render_overnight_research_autopilot_plan_markdown,
    scoped_tests_for_bundle,
    validate_overnight_research_autopilot_plan,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_overnight_research_autopilot_controller.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_overnight_research_autopilot_controller.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_overnight_research_autopilot_controller.py"
)

_ASSESS = assess_overnight_research_autopilot
_BUILD = build_overnight_research_autopilot_plan
_VALIDATE = validate_overnight_research_autopilot_plan
_RENDER = render_overnight_research_autopilot_plan_markdown


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert CONTROLLER_SCHEMA_VERSION == (
        "strategy_factory_overnight_research_autopilot_controller.v1"
    )
    assert CONTROLLER_LABEL == (
        "Block 152 - SPARTA Overnight Research Autopilot Controller"
    )
    assert CONTROLLER_STATUS == "READ_ONLY_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER"
    assert CONTROLLER_MODE == "RESEARCH_ONLY_AUTOPILOT"


def test_core_rule_states_no_boundary_and_no_auto_push():
    low = CONTROLLER_CORE_RULE.lower()
    assert "never crosses a real-world boundary" in low
    assert "never auto-pushes" in low
    assert "blocked" in low
    assert "locked" in low
    assert "per-run human approval" in low


def test_decision_categories():
    assert DECISION_HOLD == "HOLD"
    assert DECISION_RUN == "RUN_BOUNDED_RESEARCH_AUTOPILOT"
    assert DECISION_CATEGORIES == (DECISION_HOLD, DECISION_RUN)


def test_commit_and_push_policies_are_human_gated():
    assert "NO_AUTO_COMMIT" in COMMIT_POLICY
    assert "REQUIRES_EXPLICIT_HUMAN_APPROVAL" in COMMIT_POLICY
    assert PUSH_POLICY == "NO_AUTO_PUSH_REQUIRES_EXPLICIT_PER_RUN_HUMAN_APPROVAL"


def test_bundle_budget_constants():
    assert MAX_SAFE_BUNDLES_CEILING == 8
    assert DEFAULT_MAX_SAFE_BUNDLES == 5
    assert 0 < DEFAULT_MAX_SAFE_BUNDLES <= MAX_SAFE_BUNDLES_CEILING


def test_default_bundle_queue_is_research_only_and_crosses_no_boundary():
    assert len(DEFAULT_AUTOPILOT_BUNDLE_QUEUE) >= 1
    for c in DEFAULT_AUTOPILOT_BUNDLE_QUEUE:
        assert c["research_only"] is True
        assert c["crosses_real_data_qa_boundary"] is False
        assert c.get("slug")
        assert c.get("kind")


def test_hard_stop_rules_forbid_staging_commit_push():
    blob = " ".join(CONTROLLER_HARD_STOP_RULES).lower()
    assert "never stage files (git add)." in [r.lower() for r in CONTROLLER_HARD_STOP_RULES]
    assert "never commit." in [r.lower() for r in CONTROLLER_HARD_STOP_RULES]
    assert "never push." in [r.lower() for r in CONTROLLER_HARD_STOP_RULES]
    assert "decisions.md" in blob and "lessons.md" in blob


def test_forbidden_trade_terms():
    for term in ("buy", "sell", "long", "short", "entry", "exit", "order"):
        assert term in CONTROLLER_FORBIDDEN_TRADE_TERMS


def test_forbidden_paths_include_data_secrets_and_app():
    for p in (
        "data/",
        "reports/",
        "runtime/",
        "local_secrets/",
        ".env",
        "app.py",
        "brain_memory/projects/trading_bot/decisions.md",
        "brain_memory/projects/trading_bot/lessons.md",
    ):
        assert p in CONTROLLER_FORBIDDEN_PATHS


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


def test_default_plan_carries_live_mission_flow_truth():
    plan = _BUILD()
    assert plan["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert plan["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# allowed_paths / scoped_tests helpers
# --------------------------------------------------------------------------- #
def test_allowed_paths_for_bundle_only_module_test_and_allowlist():
    paths = allowed_paths_for_bundle("research_contract", "some_demo_slug")
    assert any(p.startswith("sparta_commander/") and p.endswith(".py") for p in paths)
    assert any(p.startswith("tests/test_") for p in paths)
    assert any("commander_2_safety.py" in p for p in paths)
    for p in paths:
        for forbidden in CONTROLLER_FORBIDDEN_PATHS:
            assert not p.startswith(forbidden)


def test_scoped_tests_for_bundle_includes_safety_test():
    tests = scoped_tests_for_bundle("research_contract", "some_demo_slug")
    assert "tests/test_sparta_commander_2_safety.py" in tests
    assert any(t.startswith("tests/test_strategy_factory_") for t in tests)


# --------------------------------------------------------------------------- #
# Assessment: safe default RUN
# --------------------------------------------------------------------------- #
def test_assess_default_is_bounded_run():
    a = _ASSESS({})
    assert a["decision_category"] == DECISION_RUN
    assert a["automation_allowed"] is True
    assert a["unsafe_flag_hits"] == []
    assert 0 < a["max_safe_bundles"] <= MAX_SAFE_BUNDLES_CEILING
    assert isinstance(a["next_safe_bundle"], dict)
    assert a["real_data_qa_state"] == "BLOCKED"
    assert a["baseline_backtest_state"] == "BLOCKED"
    assert a["paper_live_state"] == "LOCKED"


def test_assess_respects_requested_budget_and_ceiling():
    assert _ASSESS({"requested_max_bundles": 1})["max_safe_bundles"] == 1
    assert (
        _ASSESS({"requested_max_bundles": 999})["max_safe_bundles"]
        <= MAX_SAFE_BUNDLES_CEILING
    )


def test_assess_zero_budget_falls_back_to_hold():
    a = _ASSESS({"requested_max_bundles": 0})
    assert a["decision_category"] == DECISION_HOLD
    assert a["automation_allowed"] is False
    assert a["max_safe_bundles"] == 0
    assert a["next_safe_bundle"] is None


def test_assess_negative_budget_falls_back_to_hold():
    a = _ASSESS({"requested_max_bundles": -3})
    assert a["decision_category"] == DECISION_HOLD
    assert a["max_safe_bundles"] == 0


def test_assess_boolean_budget_is_ignored_uses_default():
    a = _ASSESS({"requested_max_bundles": True})
    assert a["decision_category"] == DECISION_RUN
    assert a["max_safe_bundles"] > 0


# --------------------------------------------------------------------------- #
# Assessment: unsafe inputs force HOLD
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_hold():
    a = _ASSESS({"authorizes_auto_push": True})
    assert a["decision_category"] == DECISION_HOLD
    assert a["automation_allowed"] is False
    assert "authorizes_auto_push" in a["unsafe_flag_hits"]
    assert a["next_safe_bundle"] is None
    assert a["max_safe_bundles"] == 0


def test_auto_commit_authorization_forces_hold():
    a = _ASSESS({"authorizes_auto_commit": True})
    assert a["decision_category"] == DECISION_HOLD
    assert "authorizes_auto_commit" in a["unsafe_flag_hits"]


def test_gate_unlock_request_forces_hold():
    a = _ASSESS({"unlock_real_data_qa": True})
    assert a["decision_category"] == DECISION_HOLD
    assert "unlock_real_data_qa" in a["unsafe_flag_hits"]


def test_boundary_crossing_flag_forces_hold():
    for flag in ("fetch_data_now", "auto_push_now", "stage_files_now", "run_qa_now"):
        a = _ASSESS({flag: True})
        assert a["decision_category"] == DECISION_HOLD, flag
        assert flag in a["unsafe_flag_hits"], flag


def test_flipped_gate_lock_forces_hold():
    a = _ASSESS({"real_data_qa_blocked": False})
    assert a["decision_category"] == DECISION_HOLD
    assert "unlocked:real_data_qa_blocked" in a["unsafe_flag_hits"]


# --------------------------------------------------------------------------- #
# Build: default plan is safe, bounded, human-gated
# --------------------------------------------------------------------------- #
def test_default_plan_builds_and_validates():
    plan = _BUILD()
    assert plan["status"] == CONTROLLER_STATUS
    assert plan["decision_category"] == DECISION_RUN
    assert plan["automation_allowed"] is True
    assert plan["max_safe_bundles"] > 0
    assert isinstance(plan["next_safe_bundle"], dict)
    assert plan["allowed_paths"]
    assert plan["scoped_tests"]
    assert plan["commit_policy"] == COMMIT_POLICY
    assert plan["push_policy"] == PUSH_POLICY
    assert plan["human_approval_required"] is True
    assert plan["per_run_push_approval_required"] is True
    assert _VALIDATE(plan)["valid"] is True


def test_plan_capability_flags_all_false_and_gates_locked():
    plan = _BUILD()
    for flag in (
        "executes",
        "runs_git",
        "stages_files",
        "auto_commits",
        "auto_pushes",
        "fetches_data",
        "calls_provider",
        "uses_network",
        "reads_credentials",
        "reads_dotenv",
        "exposes_secret",
        "runs_qa",
        "runs_backtest",
        "calls_broker_exchange",
        "places_orders",
        "triggers_paper_trading",
        "triggers_live_trading",
        "writes_runtime_outputs",
        "writes_dashboard_outputs",
        "modifies_decisions_or_lessons",
        "authorizes_auto_commit",
        "authorizes_auto_push",
        "unlocks_real_data_qa",
        "crosses_boundary",
    ):
        assert plan[flag] is False, flag
    assert plan["authorizes_nothing"] is True
    assert plan["safety_flags_all_false"] is True
    assert plan["real_data_qa_blocked"] is True
    assert plan["baseline_backtest_blocked"] is True
    assert plan["paper_trading_gate_locked"] is True
    assert plan["micro_live_gate_locked"] is True


def test_every_planned_bundle_keeps_commit_and_push_human_gated():
    plan = _BUILD()
    assert plan["planned_bundles"]
    for b in plan["planned_bundles"]:
        assert b["commit_policy"] == COMMIT_POLICY
        assert b["push_policy"] == PUSH_POLICY
        assert b["requires_human_commit_approval"] is True
        assert b["requires_human_push_approval"] is True
        assert b["crosses_real_data_qa_boundary"] is False


def test_plan_allowed_paths_never_under_a_forbidden_path():
    plan = _BUILD()
    for p in plan["allowed_paths"]:
        for forbidden in plan["forbidden_paths"]:
            assert not str(p).startswith(forbidden), (p, forbidden)


def test_unsafe_input_builds_a_hold_plan():
    plan = _BUILD({"authorizes_auto_push": True})
    assert plan["decision_category"] == DECISION_HOLD
    assert plan["automation_allowed"] is False
    assert plan["max_safe_bundles"] == 0
    assert plan["next_safe_bundle"] is None
    assert plan["allowed_paths"] == []
    assert plan["scoped_tests"] == []
    assert plan["planned_bundles"] == []
    # still safe and locked
    assert plan["real_data_qa_blocked"] is True
    assert _VALIDATE(plan)["valid"] is True


# --------------------------------------------------------------------------- #
# Secret never carried
# --------------------------------------------------------------------------- #
def test_secret_value_in_input_is_never_rendered():
    plan = _BUILD({"api_key": "SHOULD-NEVER-APPEAR"})
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(plan)


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_two_builds_are_equivalent():
    assert _BUILD() == _BUILD()


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = {"requested_max_bundles": 2}
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


# --------------------------------------------------------------------------- #
# Validation tamper rejections
# --------------------------------------------------------------------------- #
def test_validate_rejects_tampered_executes():
    plan = _BUILD()
    plan["executes"] = True
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["flags_false"] is False


def test_validate_rejects_auto_push_flag_true():
    plan = _BUILD()
    plan["auto_pushes"] = True
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    plan = _BUILD()
    plan["real_data_qa_blocked"] = False
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["gates_locked"] is False


def test_validate_rejects_unlocked_state():
    plan = _BUILD()
    plan["real_data_qa_state"] = "OPEN"
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["states_blocked_locked"] is False


def test_validate_rejects_tampered_commit_policy():
    plan = _BUILD()
    plan["commit_policy"] = "AUTO_COMMIT_NOW"
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["commit_policy_ok"] is False


def test_validate_rejects_tampered_push_policy():
    plan = _BUILD()
    plan["push_policy"] = "AUTO_PUSH_NOW"
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["push_policy_ok"] is False


def test_validate_rejects_planned_bundle_without_human_push_approval():
    plan = _BUILD()
    plan["planned_bundles"][0]["requires_human_push_approval"] = False
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["planned_ok"] is False


def test_validate_rejects_authorizes_nothing_flipped():
    plan = _BUILD()
    plan["authorizes_nothing"] = False
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["authorizes_nothing"] is False


def test_validate_rejects_run_without_next_bundle():
    plan = _BUILD()
    plan["next_safe_bundle"] = None
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["run_shape_ok"] is False


def test_validate_rejects_trade_language_in_guidance():
    plan = _BUILD()
    plan["reason"] = "place an order to buy now"
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert v["no_trade_language"] is False


def test_validate_rejects_missing_field():
    plan = _BUILD()
    del plan["commit_policy"]
    v = _VALIDATE(plan)
    assert v["valid"] is False
    assert "commit_policy" in v["missing_fields"]


def test_default_plan_carries_no_trade_language():
    assert _VALIDATE(_BUILD())["no_trade_language"] is True


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith("# SPARTA Overnight Research Autopilot Controller")
    assert "## Next Safe Bundle" in text
    assert "## Bundle Queue" in text
    assert "## Planned Bundles" in text
    assert "## Allowed Paths (next bundle)" in text
    assert "## Forbidden Paths" in text
    assert "## Scoped Tests (next bundle)" in text
    assert "## Hard Stop Rules" in text
    assert "## Final Operator Report" in text
    assert PUSH_POLICY in text


def test_render_never_leaks_a_secret():
    text = _RENDER(_BUILD({"access_token": "TOP-SECRET-VALUE"}))
    assert "TOP-SECRET-VALUE" not in text


# --------------------------------------------------------------------------- #
# Safety flags table
# --------------------------------------------------------------------------- #
def test_controller_safety_flags_posture_true_capabilities_false():
    assert CONTROLLER_SAFETY_FLAGS["read_only"] is True
    assert CONTROLLER_SAFETY_FLAGS["research_only"] is True
    assert CONTROLLER_SAFETY_FLAGS["human_approval_required"] is True
    assert CONTROLLER_SAFETY_FLAGS["per_run_push_approval_required"] is True
    for name, value in CONTROLLER_SAFETY_FLAGS.items():
        if name in {
            "read_only",
            "research_only",
            "human_approval_required",
            "per_run_push_approval_required",
        }:
            continue
        assert value is False, name


# --------------------------------------------------------------------------- #
# AST purity: __future__ / typing / sparta_commander roots only; no os / json /
# csv / network / credential modules; no os.environ access; no open / write_* call
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "sparta_commander"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
    "json",
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
    "databento",
    "dotenv",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
    "csv",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_within_allowed_roots():
    tree = _module_ast()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORT_ROOTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORT_ROOTS, node.module


def test_module_imports_no_os_network_or_credential_modules():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS), (
        imported_roots & _FORBIDDEN_MODULE_TOKENS
    )


def test_module_never_reads_environment():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv", "environb"}, node.attr


def test_module_has_no_eval_exec_import_dunder():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "input"}


def test_module_has_no_filesystem_write_capability_of_its_own():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "open(" not in src
    assert ".write_text(" not in src
    assert ".write_bytes(" not in src
    assert "write_json(" not in src
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id != "open"
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"write_text", "write_bytes", "write_json"}


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
