"""Tests for the Selected Read-Only Spot Provider Fetch Runner (Block 150).

The runner can fetch BTCUSD / ETHUSD / SOLUSD daily SPOT OHLCV, but ONLY through an
INJECTED provider_client and an INJECTED writer, and ONLY when
human_spot_provider_run_approved=True for the selected clear-license read-only spot
historical provider. It is disabled by default, constructs no live client, opens no
network, reads no credential / .env, stores no secret, and writes outside no approved
path. No real provider is ever called in these tests -- every fetch is a fake and
every write lands in tmp_path.

These tests assert: schema / constants; mission-flow truth sync; disabled-by-default
and every refusal path (missing approval, wrong symbol / timeframe / provider type /
destination / report path, trading / account / order / portfolio flags, missing
injected deps) each yielding ZERO provider calls; the approved run against a fake
provider + tmp_path writer (simulating BTCUSD@1d, ETHUSD@1d, SOLUSD@1d, writing only
tmp_path-approved equivalents, producing a manifest / gap summary, keeping gates
blocked / locked); read-only enforcement (trading-field-bearing rows skipped); the
required run-summary fields; that a secret value is never carried; determinism;
validation tamper rejections; render; AST purity (only __future__ / typing /
sparta_commander roots, no os / json / csv / network / credential modules, no
os.environ access, NO open / write_* call of its own); and the two additive
commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from sparta_commander.strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner import (  # noqa: E501
    REQUIRED_RUN_APPROVAL_FLAG,
    RUNNER_APPROVED_CACHE_PATH,
    RUNNER_APPROVED_REPORT_DIR,
    RUNNER_APPROVED_SYMBOLS,
    RUNNER_APPROVED_TIMEFRAMES,
    RUNNER_CORE_RULE,
    RUNNER_LABEL,
    RUNNER_MODE,
    RUNNER_PROVIDER_METHOD_NAME,
    RUNNER_SCHEMA_VERSION,
    RUNNER_SELECTED_CANDIDATE_TYPE,
    RUNNER_STATUS_RAN,
    RUNNER_STATUS_REFUSED,
    RUNNER_SYMBOL_ALIASES,
    render_selected_read_only_spot_provider_fetch_run_summary_markdown,
    run_selected_read_only_spot_provider_fetch,
    validate_selected_read_only_spot_provider_fetch_run_summary,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner.py"
)

_RUN = run_selected_read_only_spot_provider_fetch
_VALIDATE = validate_selected_read_only_spot_provider_fetch_run_summary
_RENDER = render_selected_read_only_spot_provider_fetch_run_summary_markdown


# --------------------------------------------------------------------------- #
# Fakes: NO real network / provider / filesystem.
# --------------------------------------------------------------------------- #
class FakeProvider:
    """In-memory read-only OHLCV source. Counts its own calls. No network."""

    def __init__(self, rows_by_symbol=None, extra_field_symbols=None):
        self._rows = rows_by_symbol or {}
        self._extra = set(extra_field_symbols or [])
        self.calls = []

    def _default_rows(self, symbol):
        return [
            {
                "date": "2024-01-01",
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
                "volume": 100.0,
            },
            {
                "date": "2024-01-02",
                "open": 1.5,
                "high": 2.5,
                "low": 1.0,
                "close": 2.0,
                "volume": 120.0,
            },
        ]

    def fetch_read_only_daily_spot_ohlcv(self, symbol, timeframe):
        self.calls.append((symbol, timeframe))
        if symbol in self._rows:
            return self._rows[symbol]
        rows = self._default_rows(symbol)
        if symbol in self._extra:
            rows = [dict(r, order_id="X-1", side="buy") for r in rows]
        return rows


class TmpWriter:
    """Routes approved logical paths into tmp_path. Records writes. No real repo write."""

    def __init__(self, tmp_root: pathlib.Path):
        self.root = tmp_root
        self.writes = {}

    def __call__(self, logical_path, content):
        self.writes[logical_path] = content
        target = self.root / logical_path  # tmp_path-approved equivalent
        target.parent.mkdir(parents=True, exist_ok=True)
        # store a small marker; we assert structure, not serialization format
        target.write_text("written", encoding="utf-8")
        return logical_path


def _approved_payload(**overrides):
    base = {
        REQUIRED_RUN_APPROVAL_FLAG: True,
        "selected_candidate_type": RUNNER_SELECTED_CANDIDATE_TYPE,
        "symbols": list(RUNNER_APPROVED_SYMBOLS),
        "timeframe": "1d",
        "destination": RUNNER_APPROVED_CACHE_PATH,
        "report_path": RUNNER_APPROVED_REPORT_DIR,
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert RUNNER_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner.v1"
    )
    assert RUNNER_LABEL == (
        "Block 150 - Selected Read-Only Spot Provider Fetch Runner"
    )
    assert RUNNER_MODE == "RESEARCH_ONLY"
    assert "disabled by default" in RUNNER_CORE_RULE.lower()
    assert "blocked" in RUNNER_CORE_RULE.lower()
    assert "human_spot_provider_run_approved" in RUNNER_CORE_RULE.lower()


def test_selected_type_and_approval_flag():
    assert RUNNER_SELECTED_CANDIDATE_TYPE == (
        "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"
    )
    assert REQUIRED_RUN_APPROVAL_FLAG == "human_spot_provider_run_approved"
    assert RUNNER_PROVIDER_METHOD_NAME == "fetch_read_only_daily_spot_ohlcv"


def test_approved_symbols_timeframe_and_paths():
    assert RUNNER_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert RUNNER_APPROVED_TIMEFRAMES == ("1d",)
    assert RUNNER_APPROVED_CACHE_PATH == "data/crypto_d1_spot_cache/"
    assert RUNNER_APPROVED_REPORT_DIR == "reports/research_os/data_qa/"


def test_symbol_aliases_include_slash_and_dash_forms():
    assert "BTC/USD" in RUNNER_SYMBOL_ALIASES["BTCUSD"]
    assert "ETH-USD" in RUNNER_SYMBOL_ALIASES["ETHUSD"]
    assert "SOL/USD" in RUNNER_SYMBOL_ALIASES["SOLUSD"]


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Disabled by default + refusal paths (ZERO provider calls)
# --------------------------------------------------------------------------- #
def test_disabled_by_default_no_args_refuses_zero_calls():
    out = _RUN()
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["run_executed"] is False
    assert out["provider_call_count"] == 0
    assert out["wrote_files"] == []
    assert "missing_human_spot_provider_run_approved" in out["blocked_reasons"]
    assert _VALIDATE(out)["valid"] is True


def test_missing_approval_refuses_and_never_calls_provider():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(**{REQUIRED_RUN_APPROVAL_FLAG: False}),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "missing_human_spot_provider_run_approved" in out["blocked_reasons"]


def test_wrong_symbol_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(symbols=["BTCUSD", "DOGEUSD"]),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert any(r.startswith("wrong_symbol:") for r in out["blocked_reasons"])


def test_wrong_timeframe_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(timeframe="1h"),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert any(r.startswith("wrong_timeframe:") for r in out["blocked_reasons"])


def test_wrong_provider_type_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(selected_candidate_type="TRADING_API"),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "wrong_selected_candidate_type" in out["blocked_reasons"]


def test_wrong_destination_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(destination="data/somewhere_else/"),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "wrong_destination" in out["blocked_reasons"]


def test_wrong_report_path_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(report_path="reports/elsewhere/"),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "wrong_report_path" in out["blocked_reasons"]


@pytest.mark.parametrize(
    "flag",
    [
        "authorizes_trading",
        "place_order",
        "account_endpoint",
        "portfolio_endpoint",
        "order_endpoint",
        "use_real_provider",
        "construct_live_client",
        "read_credentials",
        "read_dotenv",
        "unlock_real_data_qa",
    ],
)
def test_forbidden_flag_refuses_zero_calls(flag):
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(**{flag: True}),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "forbidden_flag:" + flag in out["blocked_reasons"]


def test_missing_injected_provider_refuses_zero_calls():
    out = _RUN(_approved_payload(), provider_client=None, writer=lambda p, c: p)
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert "no_injected_provider_client" in out["blocked_reasons"]


def test_missing_injected_writer_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(_approved_payload(), provider_client=prov, writer=None)
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "no_injected_writer" in out["blocked_reasons"]


def test_secret_in_payload_refuses_zero_calls():
    prov = FakeProvider()
    out = _RUN(
        _approved_payload(api_key="SHOULD-NEVER-APPEAR"),
        provider_client=prov,
        writer=lambda p, c: p,
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert prov.calls == []
    assert "secret_value_in_payload" in out["blocked_reasons"]
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(out)


# --------------------------------------------------------------------------- #
# Approved run against fake provider + tmp_path writer
# --------------------------------------------------------------------------- #
def test_approved_run_with_fake_provider_and_tmp_writer(tmp_path):
    prov = FakeProvider()
    writer = TmpWriter(tmp_path)
    out = _RUN(_approved_payload(), provider_client=prov, writer=writer)

    assert out["status"] == RUNNER_STATUS_RAN
    assert out["run_executed"] is True
    assert out["attempted_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert out["fetched_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert out["skipped_symbols"] == []
    assert out["provider_call_count"] == 3
    assert prov.calls == [
        ("BTCUSD", "1d"),
        ("ETHUSD", "1d"),
        ("SOLUSD", "1d"),
    ]
    assert out["destination"] == RUNNER_APPROVED_CACHE_PATH
    assert out["report_path"] == RUNNER_APPROVED_REPORT_DIR
    # 3 data files + 1 manifest
    assert len(out["wrote_files"]) == 4
    assert out["blocked_reasons"] == []
    # gates stay blocked / locked
    assert out["real_data_qa_state"] == "BLOCKED"
    assert out["baseline_backtest_state"] == "BLOCKED"
    assert out["paper_live_state"] == "LOCKED"
    assert _VALIDATE(out)["valid"] is True


def test_approved_run_writes_only_under_approved_paths(tmp_path):
    prov = FakeProvider()
    writer = TmpWriter(tmp_path)
    out = _RUN(_approved_payload(), provider_client=prov, writer=writer)

    for path in out["wrote_files"]:
        assert path.startswith(RUNNER_APPROVED_CACHE_PATH) or path.startswith(
            RUNNER_APPROVED_REPORT_DIR
        )
    # everything physically landed inside tmp_path (no real repo write)
    for logical in writer.writes:
        assert (tmp_path / logical).exists()
    # manifest written under the approved report dir
    manifest_paths = [
        p for p in out["wrote_files"] if p.startswith(RUNNER_APPROVED_REPORT_DIR)
    ]
    assert len(manifest_paths) == 1


def test_manifest_and_gap_summary_present_in_tmp_only(tmp_path):
    prov = FakeProvider()
    writer = TmpWriter(tmp_path)
    out = _RUN(_approved_payload(), provider_client=prov, writer=writer)

    manifest = out["manifest"]
    assert manifest is not None
    assert manifest["timeframe"] == "1d"
    assert manifest["destination"] == RUNNER_APPROVED_CACHE_PATH
    assert [s["symbol"] for s in manifest["symbols"]] == [
        "BTCUSD",
        "ETHUSD",
        "SOLUSD",
    ]
    assert all(s["bar_count"] == 2 for s in manifest["symbols"])
    assert manifest["gap_summary"] == []
    assert manifest["real_data_qa_state"] == "BLOCKED"


def test_symbol_alias_forms_normalize_and_run(tmp_path):
    prov = FakeProvider()
    writer = TmpWriter(tmp_path)
    out = _RUN(
        _approved_payload(symbols=["BTC/USD", "ETH-USD", "SOL/USD"]),
        provider_client=prov,
        writer=writer,
    )
    assert out["status"] == RUNNER_STATUS_RAN
    assert out["fetched_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]


def test_trading_field_bearing_rows_are_skipped_read_only_enforced(tmp_path):
    prov = FakeProvider(extra_field_symbols=["ETHUSD"])
    writer = TmpWriter(tmp_path)
    out = _RUN(_approved_payload(), provider_client=prov, writer=writer)

    assert out["status"] == RUNNER_STATUS_RAN
    assert "ETHUSD" in out["skipped_symbols"]
    assert "ETHUSD" not in out["fetched_symbols"]
    assert out["provider_call_count"] == 3  # called, then skipped on read-only guard
    assert any("ETHUSD" in g for g in out["manifest"]["gap_summary"])
    assert _VALIDATE(out)["valid"] is True


def test_empty_rows_symbol_is_skipped(tmp_path):
    prov = FakeProvider(rows_by_symbol={"SOLUSD": []})
    writer = TmpWriter(tmp_path)
    out = _RUN(_approved_payload(), provider_client=prov, writer=writer)
    assert "SOLUSD" in out["skipped_symbols"]
    assert "SOLUSD" not in out["fetched_symbols"]
    assert _VALIDATE(out)["valid"] is True


def test_provider_missing_read_only_method_refuses(tmp_path):
    class TradingClient:
        def place_order(self, *a, **k):  # not a read-only method
            return "nope"

    out = _RUN(
        _approved_payload(),
        provider_client=TradingClient(),
        writer=TmpWriter(tmp_path),
    )
    assert out["status"] == RUNNER_STATUS_REFUSED
    assert out["provider_call_count"] == 0
    assert "injected_provider_missing_read_only_method" in out["blocked_reasons"]


# --------------------------------------------------------------------------- #
# Run summary required fields
# --------------------------------------------------------------------------- #
def test_run_summary_has_all_required_fields(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    for key in (
        "attempted_symbols",
        "fetched_symbols",
        "skipped_symbols",
        "provider_call_count",
        "destination",
        "report_path",
        "wrote_files",
        "blocked_reasons",
        "safety_confirmations",
        "real_data_qa_state",
        "baseline_backtest_state",
        "paper_live_state",
    ):
        assert key in out


def test_capability_flags_all_false_and_gates_locked(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    assert out["this_block_called_real_provider"] is False
    assert out["this_block_made_network_call"] is False
    assert out["this_block_read_credentials"] is False
    assert out["this_block_wrote_real_repo_files"] is False
    assert out["authorizes_nothing"] is True
    assert out["real_data_qa_blocked"] is True
    assert out["baseline_backtest_blocked"] is True
    assert out["paper_trading_gate_locked"] is True
    assert out["micro_live_gate_locked"] is True
    assert out["calls_real_provider"] is False
    assert out["uses_network"] is False
    assert out["writes_real_repo_files"] is False


def test_safety_confirmations_all_true(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    assert all(out["safety_confirmations"].values())


# --------------------------------------------------------------------------- #
# Secret never carried / determinism
# --------------------------------------------------------------------------- #
def test_secret_value_never_carried_into_summary():
    out = _RUN(_approved_payload(secret="leak"))
    assert _VALIDATE(out)["no_secret_value_fields"] is True
    assert "leak" not in _RENDER(out)


def test_two_refused_runs_are_equivalent():
    assert _RUN() == _RUN()


def test_run_does_not_mutate_caller_payload():
    import copy

    payload = _approved_payload()
    snapshot = copy.deepcopy(payload)
    _RUN(payload, provider_client=FakeProvider(), writer=lambda p, c: p)
    assert payload == snapshot


# --------------------------------------------------------------------------- #
# Validation tamper rejections
# --------------------------------------------------------------------------- #
def test_validate_rejects_unlocked_gate(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    out["real_data_qa_blocked"] = False
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_unlocked_state(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    out["real_data_qa_state"] = "OPEN"
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["states_blocked_locked"] is False


def test_validate_rejects_real_provider_flag(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    out["calls_real_provider"] = True
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_refused_summary_with_nonzero_calls():
    out = _RUN()  # refused
    out["provider_call_count"] = 3
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["refused_zero_calls_ok"] is False


def test_validate_rejects_out_of_scope_symbol(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    out["fetched_symbols"] = ["DOGEUSD"]
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["fetched_in_scope"] is False


def test_validate_rejects_secret_value(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    out["api_key"] = "leaked-value"
    verdict = _VALIDATE(out)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string(tmp_path):
    out = _RUN(
        _approved_payload(), provider_client=FakeProvider(), writer=TmpWriter(tmp_path)
    )
    text = _RENDER(out)
    assert isinstance(text, str)
    assert text.startswith("# Selected Read-Only Spot Provider Fetch Runner")
    assert "## Attempted Symbols" in text
    assert "## Fetched Symbols" in text
    assert "## Wrote Files" in text
    assert "## Safety Confirmations" in text
    assert "data/crypto_d1_spot_cache/" in text


def test_render_refused_run():
    text = _RENDER(_RUN())
    assert "Status: " + RUNNER_STATUS_REFUSED in text
    assert "## Blocked Reasons" in text


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
    # The runner owns NO filesystem-write capability: it never calls open, write_text,
    # write_bytes, or write_json. All writes go through the injected writer. Asserted
    # both lexically (so the safety verifier's `filesystem_write` pattern cannot match)
    # and via the AST.
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
