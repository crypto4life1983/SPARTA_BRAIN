"""Tests for the Crypto-D1 Databento Read-Only Fetch Runner (Block 143).

The runner is the module a future, explicitly human-approved run would use to
perform the READ-ONLY Databento historical market-data fetch defined and guarded
by the Block 142 contract. In THIS block the runner is built and tested ONLY; no
real fetch is performed.

Two structural safety properties are exercised here:

  1. DEPENDENCY-INJECTED PROVIDER. The runner never constructs a live Databento
     client; it only calls an injected `provider_client`. With no client, it
     cannot fetch -- it has no network capability of its own. These tests inject a
     FAKE provider that returns synthetic OHLCV bars and records its calls.

  2. INJECTED WRITER. The runner never opens a file; it only hands an approved
     RELATIVE path + text to an injected `writer.persist` sink. With no writer, it
     writes nothing -- it has no filesystem-write capability of its own. These
     tests inject a tmp_path-backed `_TmpWriter`, so every write lands in a
     throwaway temp dir -- never the real repo. (The actual `open()` lives in the
     test sink, not in the scanned runner module.)

These tests assert: schema / constants; mission-flow truth sync against the live
status module; blocked-by-default (no human-run approval); out-of-scope and
forbidden-flag refusals; blocked-no-provider and blocked-no-writer guards; the
happy-path fake fetch (files + manifest + gap report written ONLY under the
injected writer's base); a skipped symbol when the fake returns no data; that
performing the fetch unlocks no gate; that a secret value is never carried;
determinism / isolation; post-run validation (incl. tamper rejections); render;
AST purity (only json / typing / sparta_commander roots, no os / network /
credential modules, no os.environ / os.getenv access, NO open / write_* call in
the module); a no-real-repo-write proof; and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_runner import (  # noqa: E501
    DEFAULT_RUN_INPUT,
    RUNNER_CORE_RULE,
    RUNNER_LABEL,
    RUNNER_MODE,
    RUNNER_SCHEMA_VERSION,
    RUNNER_STATUS,
    STATUS_BLOCKED_DISABLED,
    STATUS_BLOCKED_NO_PROVIDER,
    STATUS_BLOCKED_NO_WRITER,
    STATUS_COMPLETED,
    STATUS_REFUSED_OUT_OF_SCOPE,
    STATUS_REFUSED_UNSAFE,
    render_fetch_run_summary_markdown,
    run_databento_read_only_fetch,
    validate_fetch_run_summary,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_DESTINATION,
    FETCH_APPROVED_PROVIDER,
    FETCH_APPROVED_REPORT_DIR,
    FETCH_APPROVED_SYMBOLS,
    FETCH_HUMAN_RUN_APPROVAL_FLAG,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_databento_read_only_fetch_runner.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_databento_read_only_fetch_runner.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_databento_read_only_fetch_runner.py"
)

_RUN = run_databento_read_only_fetch
_VALIDATE = validate_fetch_run_summary
_RENDER = render_fetch_run_summary_markdown


# --------------------------------------------------------------------------- #
# Fakes (the ONLY way the runner can fetch / write in tests)
# --------------------------------------------------------------------------- #
class _FakeProvider:
    """A fake Databento historical client. Returns synthetic daily OHLCV bars and
    records every call. Constructs no network, reads no credential. A symbol named
    in `empty_for` yields an empty list (simulating "no data for symbol")."""

    def __init__(self, empty_for=()):
        self.calls = []
        self.empty_for = set(empty_for)

    def fetch_historical_daily_bars(self, symbol, timeframe):
        self.calls.append((symbol, timeframe))
        if symbol in self.empty_for:
            return []
        return [
            {
                "date": "2024-01-0" + str(i),
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100 + i,
                "volume": 10 * i,
            }
            for i in range(1, 4)
        ]


class _TmpWriter:
    """A tmp_path-backed writer sink. Resolves the runner's approved relative path
    under `base`, creates parent dirs, and writes the text. Records every call.
    The runner module never opens a file -- this test sink does."""

    def __init__(self, base):
        self.base = pathlib.Path(base)
        self.calls = []

    def persist(self, rel_path, text):
        self.calls.append(rel_path)
        target = self.base / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def _base(tmp_path):
    """A clean repo-root stand-in *inside* tmp_path. The conftest creates an
    `_iso_reports` dir at the tmp_path root, so we write under a subdir to keep
    the runner's footprint isolated and assertable."""
    b = tmp_path / "repo"
    b.mkdir()
    return b


def _safe_input(**overrides):
    payload = {
        "mode": "RESEARCH_ONLY",
        "read_only": True,
        "executes": False,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "requested_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "requested_timeframes": ["1d"],
        "requested_provider": FETCH_APPROVED_PROVIDER,
        "requested_destination": FETCH_APPROVED_DESTINATION,
        "requested_report_dir": FETCH_APPROVED_REPORT_DIR,
        "databento_config_declared": False,
    }
    payload.update(overrides)
    return payload


def _approved_input(**overrides):
    payload = _safe_input(**{FETCH_HUMAN_RUN_APPROVAL_FLAG: True})
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert RUNNER_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_databento_read_only_fetch_runner.v1"
    )
    assert RUNNER_LABEL == (
        "Block 143 - Crypto-D1 Databento Read-Only Fetch Runner"
    )
    assert RUNNER_STATUS == "READ_ONLY_DATABENTO_FETCH_RUNNER"
    assert RUNNER_MODE == "RESEARCH_ONLY"
    assert "disabled by default" in RUNNER_CORE_RULE.lower()
    assert "blocked" in RUNNER_CORE_RULE.lower()


def test_default_run_input_has_no_human_approval():
    assert FETCH_HUMAN_RUN_APPROVAL_FLAG not in DEFAULT_RUN_INPUT


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Blocked by default (disabled): no human-run approval
# --------------------------------------------------------------------------- #
def test_blocked_by_default_no_human_approval(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(_safe_input(), provider_client=fake, writer=writer)
    assert summary["run_status"] == STATUS_BLOCKED_DISABLED
    assert summary["performs_data_fetch"] is False
    assert summary["provider_call_count"] == 0
    assert summary["fetched_symbols"] == []
    assert summary["wrote_files"] == []
    assert fake.calls == []
    assert writer.calls == []
    assert "no_explicit_human_run_approval" in summary["blocked_reasons"]
    assert set(base.iterdir()) == set()


def test_default_payload_none_is_blocked(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(None, provider_client=fake, writer=writer)
    assert summary["run_status"] == STATUS_BLOCKED_DISABLED
    assert fake.calls == []
    assert writer.calls == []
    assert set(base.iterdir()) == set()


# --------------------------------------------------------------------------- #
# Scope refusals (approved human-run, but out-of-scope request)
# --------------------------------------------------------------------------- #
def test_out_of_scope_symbol_refused(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(requested_symbols=["DOGEUSD"]),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_OUT_OF_SCOPE
    assert summary["performs_data_fetch"] is False
    assert fake.calls == []
    assert writer.calls == []
    assert "symbols_out_of_scope" in summary["blocked_reasons"]
    assert set(base.iterdir()) == set()


def test_out_of_scope_timeframe_refused(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(requested_timeframes=["1h"]),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_OUT_OF_SCOPE
    assert fake.calls == []
    assert "timeframe_out_of_scope" in summary["blocked_reasons"]


def test_out_of_scope_destination_refused(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(requested_destination="data/elsewhere/"),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_OUT_OF_SCOPE
    assert fake.calls == []
    assert "destination_out_of_scope" in summary["blocked_reasons"]
    assert set(base.iterdir()) == set()


def test_non_databento_provider_refused(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(requested_provider="binance_exchange_api"),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_OUT_OF_SCOPE
    assert fake.calls == []
    assert "provider_not_databento_historical" in summary["blocked_reasons"]


# --------------------------------------------------------------------------- #
# Forbidden-flag refusals
# --------------------------------------------------------------------------- #
def test_authorization_flag_refused_unsafe(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(authorizes_trading=True),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_UNSAFE
    assert summary["performs_data_fetch"] is False
    assert fake.calls == []
    assert writer.calls == []
    assert any(r.startswith("forbidden_flag:") for r in summary["blocked_reasons"])
    assert set(base.iterdir()) == set()


def test_gate_unlock_request_refused_unsafe(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(unlock_real_data_qa=True),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_UNSAFE
    assert fake.calls == []


def test_off_boundary_mission_flow_refused_unsafe(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(mission_flow_current_stage="SOMETHING_ELSE"),
        provider_client=fake,
        writer=writer,
    )
    assert summary["run_status"] == STATUS_REFUSED_UNSAFE
    assert fake.calls == []
    assert "mission_flow_off_boundary" in summary["blocked_reasons"]


# --------------------------------------------------------------------------- #
# Permitted but missing client / writer -> cannot act
# --------------------------------------------------------------------------- #
def test_blocked_no_provider_client(tmp_path):
    base = _base(tmp_path)
    writer = _TmpWriter(base)
    summary = _RUN(_approved_input(), provider_client=None, writer=writer)
    assert summary["run_status"] == STATUS_BLOCKED_NO_PROVIDER
    assert summary["performs_data_fetch"] is False
    assert summary["provider_call_count"] == 0
    assert summary["wrote_files"] == []
    assert writer.calls == []
    assert "no_provider_client_injected" in summary["blocked_reasons"]
    assert set(base.iterdir()) == set()


def test_blocked_no_writer():
    fake = _FakeProvider()
    summary = _RUN(_approved_input(), provider_client=fake, writer=None)
    assert summary["run_status"] == STATUS_BLOCKED_NO_WRITER
    assert summary["performs_data_fetch"] is False
    assert fake.calls == []
    assert summary["wrote_files"] == []
    assert "no_writer_injected" in summary["blocked_reasons"]


# --------------------------------------------------------------------------- #
# Happy path: fake fetch via the injected writer only
# --------------------------------------------------------------------------- #
def test_happy_path_fake_fetch_writes_only_under_base(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(_approved_input(), provider_client=fake, writer=writer)

    assert summary["run_status"] == STATUS_COMPLETED
    assert summary["performs_data_fetch"] is True
    assert summary["attempted_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert summary["fetched_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert summary["skipped_symbols"] == []
    assert summary["provider_call_count"] == 3
    assert fake.calls == [
        ("BTCUSD", "1d"),
        ("ETHUSD", "1d"),
        ("SOLUSD", "1d"),
    ]

    # data files written under base/data/databento_cache/crypto_d1/
    dest = base / "data" / "databento_cache" / "crypto_d1"
    assert (dest / "BTCUSD_1d.json").exists()
    assert (dest / "ETHUSD_1d.json").exists()
    assert (dest / "SOLUSD_1d.json").exists()

    # manifest + gap report under base/reports/research_os/data_qa/
    report = base / "reports" / "research_os" / "data_qa"
    assert (report / "crypto_d1_databento_manifest.json").exists()
    assert (report / "crypto_d1_databento_gap_report.md").exists()

    # every wrote_files entry is a relative path under base (no abs / no ..)
    for rel in summary["wrote_files"]:
        assert not rel.startswith("..")
        assert not pathlib.PurePath(rel).is_absolute()

    # performing the fetch unlocks NO gate
    assert summary["real_data_qa_state"] == "BLOCKED"
    assert summary["baseline_backtest_state"] == "BLOCKED"
    assert summary["paper_live_state"] == "LOCKED"
    assert summary["real_data_qa_blocked"] is True
    assert summary["unlocks_real_data_qa"] is False

    assert _VALIDATE(summary)["valid"] is True


def test_happy_path_writes_nothing_outside_two_approved_trees(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    _RUN(_approved_input(), provider_client=fake, writer=writer)
    top = {p.name for p in base.iterdir()}
    assert top == {"data", "reports"}


def test_manifest_records_pair_rowcount_daterange(tmp_path):
    import json

    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    _RUN(_approved_input(), provider_client=fake, writer=writer)
    manifest_path = (
        base / "reports" / "research_os" / "data_qa"
        / "crypto_d1_databento_manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["fetched_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    entries = {e["pair"]: e for e in manifest["entries"]}
    assert entries["BTCUSD@1d"]["row_count"] == 3
    assert entries["BTCUSD@1d"]["date_min"] == "2024-01-01"
    assert entries["BTCUSD@1d"]["date_max"] == "2024-01-03"
    assert manifest["real_data_qa_state"] == "BLOCKED"


# --------------------------------------------------------------------------- #
# Skipped symbol when the fake returns no data
# --------------------------------------------------------------------------- #
def test_symbol_with_no_data_is_skipped(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider(empty_for=["SOLUSD"])
    writer = _TmpWriter(base)
    summary = _RUN(_approved_input(), provider_client=fake, writer=writer)

    assert summary["run_status"] == STATUS_COMPLETED
    assert summary["fetched_symbols"] == ["BTCUSD", "ETHUSD"]
    assert summary["skipped_symbols"] == ["SOLUSD"]
    # provider was still CALLED for all three (call count == attempted)
    assert summary["provider_call_count"] == 3
    dest = base / "data" / "databento_cache" / "crypto_d1"
    assert not (dest / "SOLUSD_1d.json").exists()
    gap = (
        base / "reports" / "research_os" / "data_qa"
        / "crypto_d1_databento_gap_report.md"
    ).read_text(encoding="utf-8")
    assert "SOLUSD@1d: NO DATA (skipped)" in gap
    assert _VALIDATE(summary)["valid"] is True


# --------------------------------------------------------------------------- #
# Secret never carried
# --------------------------------------------------------------------------- #
def test_secret_value_in_input_is_never_carried_into_summary(tmp_path):
    base = _base(tmp_path)
    fake = _FakeProvider()
    writer = _TmpWriter(base)
    summary = _RUN(
        _approved_input(databento_api_key="SHOULD-NEVER-APPEAR"),
        provider_client=fake,
        writer=writer,
    )
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(summary)
    assert _VALIDATE(summary)["no_secret_value_fields"] is True


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_two_runs_into_separate_dirs_are_equivalent(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    s1 = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(a))
    s2 = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(b))
    assert s1 == s2


def test_run_does_not_mutate_caller_payload(tmp_path):
    import copy

    base = _base(tmp_path)
    payload = _approved_input()
    snapshot = copy.deepcopy(payload)
    _RUN(payload, provider_client=_FakeProvider(), writer=_TmpWriter(base))
    assert payload == snapshot


# --------------------------------------------------------------------------- #
# Post-run validation / render
# --------------------------------------------------------------------------- #
def test_blocked_summary_validates():
    summary = _RUN(_safe_input(), provider_client=None, writer=None)
    assert _VALIDATE(summary)["valid"] is True


def test_validate_rejects_tampered_executes(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["executes"] = True
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["real_data_qa_blocked"] = False
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_unlocked_state(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["real_data_qa_state"] = "OPEN"
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["states_blocked_locked"] is False


def test_validate_rejects_secret_value(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["databento_api_key"] = "leaked-value"
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


def test_validate_rejects_absolute_wrote_path(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["wrote_files"] = ["/etc/passwd"]
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["writes_under_base"] is False


def test_validate_rejects_windows_absolute_wrote_path(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["wrote_files"] = ["C:/Windows/system32/hosts"]
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["writes_under_base"] is False


def test_validate_rejects_inconsistent_counts(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    summary["fetched_symbols"] = ["BTCUSD"]  # drop two -> counts no longer add up
    verdict = _VALIDATE(summary)
    assert verdict["valid"] is False
    assert verdict["counts_consistent"] is False


def test_render_is_a_readonly_markdown_string(tmp_path):
    base = _base(tmp_path)
    summary = _RUN(_approved_input(), provider_client=_FakeProvider(), writer=_TmpWriter(base))
    text = _RENDER(summary)
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Databento Read-Only Fetch Run Summary"
    )
    assert "## Attempted Symbols" in text
    assert "## Fetched Symbols" in text
    assert "## Wrote Files" in text
    assert "## Safety Confirmations" in text


# --------------------------------------------------------------------------- #
# AST purity: json / typing / sparta_commander roots only; no os / network /
# credential modules; no os.environ / os.getenv access; no open / write_* call
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "json", "sparta_commander"}
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
    "databento",
    "dotenv",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
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
    # guard against os.environ / os.getenv / os.environb attribute access.
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv", "environb"}, node.attr


def test_module_has_no_eval_exec_import_dunder():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "input"}


def test_module_has_no_filesystem_write_capability_of_its_own():
    # The runner must own NO filesystem-write capability: it never calls open,
    # write_text, write_bytes, or write_json. All persistence is delegated to the
    # injected writer.persist sink. This is asserted both lexically (so the safety
    # verifier's `filesystem_write` pattern cannot match) and via the AST.
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
# No real repo write proof: every NON-completed path writes nothing / no provider
# --------------------------------------------------------------------------- #
def test_blocked_and_refused_paths_write_nothing(tmp_path):
    for payload in (
        _safe_input(),
        _approved_input(requested_symbols=["DOGEUSD"]),
        _approved_input(authorizes_trading=True),
    ):
        sub = tmp_path / "x"
        sub.mkdir()
        client = _FakeProvider()
        writer = _TmpWriter(sub)
        summary = _RUN(payload, provider_client=client, writer=writer)
        assert summary["run_status"] != STATUS_COMPLETED
        assert client.calls == []
        assert writer.calls == []
        assert set(sub.iterdir()) == set()
        sub.rmdir()


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
