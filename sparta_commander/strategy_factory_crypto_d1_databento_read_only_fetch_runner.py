"""Crypto-D1 Databento Read-Only Fetch Runner (Block 143).

The RUNNER that a future, explicitly human-approved run would use to perform the
READ-ONLY Databento historical market-data fetch defined and guarded by Block 142.
In THIS block the runner is built and tested ONLY; no real fetch is performed.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

Two structural safety properties make the runner incapable of an accidental real
call or an accidental real-repo write:

  1. DEPENDENCY-INJECTED PROVIDER. The runner NEVER constructs a live Databento
     client. It only calls a `provider_client` that the caller injects. With no
     client injected, the runner cannot fetch -- it has no network capability of
     its own. In tests a FAKE client is injected; a real client would be injected
     only by a future, human-approved run.

  2. INJECTED WRITER REQUIRED. The runner has NO filesystem-write capability of
     its own: it never calls `open`, `write_text`, `write_bytes`, or `write_json`.
     It only hands an approved RELATIVE path + text to an injected `writer.persist`
     sink, which resolves the path under its OWN base dir and performs the write.
     In tests the writer is a tmp_path-backed sink; a future real run would inject
     a repo-root sink. With no writer injected, the runner refuses to write.

Permission is reused verbatim from the Block 142 contract: fetch is DISABLED by
default and permitted only when `human_run_approved=True` is supplied, the request
stays inside the approved scope (BTCUSD / ETHUSD / SOLUSD @ 1d, Databento
historical read-only provider, destination data/databento_cache/crypto_d1/, report
dir reports/research_os/data_qa/), and no forbidden authorization / unlock / gate
flag is set.

The runner NEVER reads or prints a credential, NEVER reads or prints a .env file,
NEVER logs a secret, NEVER touches an exchange / broker / account / trading
endpoint, NEVER places an order, NEVER runs QA / baseline / backtest / simulation,
NEVER writes a runtime / dashboard output, and NEVER unlocks a gate. Performing the
fetch (even the future real one) does NOT unlock Real Data QA: real_data_qa stays
BLOCKED, baseline stays BLOCKED, paper / micro-live stay LOCKED.

Provider interface a future real adapter (or the test fake) must implement:
    provider_client.fetch_historical_daily_bars(symbol: str, timeframe: str)
        -> list[dict]    # daily OHLCV bars; empty list means "no data for symbol"

Writer (sink) interface a future real adapter (or the test fake) must implement:
    writer.persist(rel_path: str, text: str) -> None
        # resolves rel_path under the writer's OWN base dir, creates parent dirs,
        # and writes text. The runner never opens a file itself.

Public API:
  - RUNNER_SCHEMA_VERSION / RUNNER_LABEL / RUNNER_STATUS / RUNNER_MODE
  - RUNNER_CORE_RULE / DEFAULT_RUN_INPUT
  - run_databento_read_only_fetch(payload=None, *, provider_client=None, writer=None)
  - validate_fetch_run_summary(summary)
  - render_fetch_run_summary_markdown(summary)
"""

from __future__ import annotations

import json
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_DESTINATION,
    FETCH_APPROVED_PROVIDER,
    FETCH_APPROVED_REPORT_DIR,
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    FETCH_GAP_REPORT_PATH,
    FETCH_HUMAN_RUN_APPROVAL_FLAG,
    FETCH_MANIFEST_REPORT_PATH,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    assess_databento_read_only_fetch_execution,
    build_crypto_d1_databento_read_only_fetch_execution_contract,
    validate_crypto_d1_databento_read_only_fetch_execution_contract,
)

RUNNER_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_databento_read_only_fetch_runner.v1"
)
RUNNER_LABEL = "Block 143 - Crypto-D1 Databento Read-Only Fetch Runner"
RUNNER_STATUS = "READ_ONLY_DATABENTO_FETCH_RUNNER"
RUNNER_MODE = "RESEARCH_ONLY"

RUNNER_CORE_RULE = (
    "Fetch is disabled by default. The runner performs a READ-ONLY Databento "
    "historical fetch only with explicit human_run_approved=True, an injected "
    "provider client, and an injected writer sink, and only within the approved "
    "scope. The runner constructs no live client, opens no file, and reads no "
    "credential / .env. Performing the fetch NEVER unlocks Real Data QA: "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, paper / micro-live stay "
    "LOCKED."
)

# Status labels for a run summary.
STATUS_BLOCKED_DISABLED = "BLOCKED_DISABLED_BY_DEFAULT"
STATUS_REFUSED_UNSAFE = "REFUSED_UNSAFE"
STATUS_REFUSED_OUT_OF_SCOPE = "REFUSED_OUT_OF_SCOPE"
STATUS_BLOCKED_NO_PROVIDER = "BLOCKED_NO_PROVIDER_CLIENT"
STATUS_BLOCKED_NO_WRITER = "BLOCKED_NO_WRITER"
STATUS_COMPLETED = "COMPLETED"

# A deterministic static input. Deliberately NO human_run_approved flag, so the
# default run is blocked (disabled by default).
DEFAULT_RUN_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 Databento read-only fetch run input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "requested_symbols": list(FETCH_APPROVED_SYMBOLS),
    "requested_timeframes": list(FETCH_APPROVED_TIMEFRAMES),
    "requested_provider": FETCH_APPROVED_PROVIDER,
    "requested_destination": FETCH_APPROVED_DESTINATION,
    "requested_report_dir": FETCH_APPROVED_REPORT_DIR,
    "databento_config_declared": False,
    # NOTE: no "human_run_approved" -> fetch stays disabled by default.
}

_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _join_rel(prefix: str, name: str) -> str:
    """Join an approved relative directory and a file name into a clean POSIX
    relative path. Pure string work; touches no filesystem."""
    p = str(prefix).replace("\\", "/").rstrip("/")
    return (p + "/" + name) if p else name


def _is_abs_like(p: str) -> bool:
    """Pure (no-os) test for an absolute-looking path: POSIX root, UNC / backslash
    root, or a Windows drive letter. Used to reject any out-of-base wrote_files
    entry without importing os."""
    if not p:
        return False
    if p.startswith("/") or p.startswith("\\"):
        return True
    return len(p) >= 2 and p[1] == ":"


def _date_range(bars: list[dict[str, Any]]) -> tuple[str, str]:
    dates = [str(b.get("date")) for b in bars if isinstance(b, dict) and b.get("date")]
    if not dates:
        return ("", "")
    dates.sort()
    return (dates[0], dates[-1])


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty string
    value. A secret VALUE is always a string; booleans (e.g. the confirmation
    flag `no_secret_logged=True`) and counts are flags, never secrets."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            looks_secret = any(tok in key_l for tok in _SECRET_VALUE_TOKENS)
            if looks_secret and isinstance(value, str) and value.strip():
                return True
            if _has_secret_value(value):
                return True
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _has_secret_value(item):
                return True
    return False


def _blank_summary(
    status: str,
    blocked_reasons: list[str],
    *,
    human_run_approved: bool,
    safe: bool,
    fetch_permitted: bool,
    destination: str,
    report_path: str,
    pre_run_contract_valid: bool,
) -> dict[str, Any]:
    return _summary(
        status=status,
        attempted=[],
        fetched=[],
        skipped=[],
        destination=destination,
        report_path=report_path,
        provider_call_count=0,
        wrote_files=[],
        blocked_reasons=blocked_reasons,
        performs_data_fetch=False,
        human_run_approved=human_run_approved,
        safe=safe,
        fetch_permitted=fetch_permitted,
        pre_run_contract_valid=pre_run_contract_valid,
        writes_under_base=True,
    )


def _summary(
    *,
    status: str,
    attempted: list[str],
    fetched: list[str],
    skipped: list[str],
    destination: str,
    report_path: str,
    provider_call_count: int,
    wrote_files: list[str],
    blocked_reasons: list[str],
    performs_data_fetch: bool,
    human_run_approved: bool,
    safe: bool,
    fetch_permitted: bool,
    pre_run_contract_valid: bool,
    writes_under_base: bool,
) -> dict[str, Any]:
    return {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "label": RUNNER_LABEL,
        "status_label": RUNNER_STATUS,
        "mode": RUNNER_MODE,
        "core_rule": RUNNER_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "run_status": status,
        # --- required run summary fields ---
        "attempted_symbols": list(attempted),
        "fetched_symbols": list(fetched),
        "skipped_symbols": list(skipped),
        "destination": destination,
        "report_path": report_path,
        "provider_call_count": provider_call_count,
        "wrote_files": list(wrote_files),
        "blocked_reasons": list(blocked_reasons),
        "safety_confirmations": {
            "runner_constructs_no_live_client": True,
            "no_network_in_runner": True,
            "no_credential_read": True,
            "no_dotenv_read": True,
            "no_secret_logged": True,
            "writes_only_under_base_dir": writes_under_base,
            "no_trading_or_order_action": True,
            "gates_remain_locked": True,
        },
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        # --- posture / flags ---
        "human_run_approved": human_run_approved,
        "safe": safe,
        "fetch_permitted_for_future_runner": fetch_permitted,
        "performs_data_fetch": performs_data_fetch,
        "pre_run_contract_valid": pre_run_contract_valid,
        "read_only": True,
        "research_only": True,
        "executes": False,
        "calls_databento_directly": False,
        "uses_network_directly": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "authorizes_trading": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_order_placement": False,
        "authorizes_account_control": False,
        "authorizes_portfolio_control": False,
        "authorizes_strategy_promotion": False,
        "authorizes_automation_trading": False,
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }


# --------------------------------------------------------------------------- #
# the runner
# --------------------------------------------------------------------------- #
def run_databento_read_only_fetch(
    payload: Any = None,
    *,
    provider_client: Any = None,
    writer: Any = None,
) -> dict[str, Any]:
    """Run (or refuse) the read-only Databento Crypto-D1 fetch.

    Returns a deterministic run-summary dict. Performs a fetch ONLY when the
    Block 142 contract permits it (human_run_approved + approved scope + safe),
    AND a provider_client is injected, AND a writer sink is injected. The runner
    constructs no live client and makes no network call of its own; it only calls
    the injected client. The runner opens no file of its own; it only hands an
    approved relative path + text to the injected `writer.persist`. With no client
    it fetches nothing; with no writer it writes nothing. The fetch unlocks no
    gate."""
    data = dict(DEFAULT_RUN_INPUT) if payload is None else _as_payload(payload)

    a = assess_databento_read_only_fetch_execution(data)
    destination = a["requested_destination"]
    report_path = a["requested_report_dir"]

    # Validate the guarding contract BEFORE any run (pre-run validation).
    pre_contract = build_crypto_d1_databento_read_only_fetch_execution_contract(data)
    pre_run_contract_valid = validate_crypto_d1_databento_read_only_fetch_execution_contract(
        pre_contract
    )["valid"]

    blocked_reasons: list[str] = []
    if not a["human_run_approved"]:
        blocked_reasons.append("no_explicit_human_run_approval")
    if not a["mission_flow_aligned"]:
        blocked_reasons.append("mission_flow_off_boundary")
    for hit in a["forbidden_flag_hits"]:
        blocked_reasons.append("forbidden_flag:" + hit)
    if not a["symbols_approved"]:
        blocked_reasons.append("symbols_out_of_scope")
    if not a["timeframes_approved"]:
        blocked_reasons.append("timeframe_out_of_scope")
    if not a["provider_approved"]:
        blocked_reasons.append("provider_not_databento_historical")
    if not a["destination_approved"]:
        blocked_reasons.append("destination_out_of_scope")
    if not a["report_path_approved"]:
        blocked_reasons.append("report_path_out_of_scope")

    permitted = a["fetch_permitted_for_future_runner"]

    # Pick a status for the refusal cases, in priority order.
    if not a["human_run_approved"]:
        refuse_status = STATUS_BLOCKED_DISABLED
    elif not a["safe"]:
        refuse_status = STATUS_REFUSED_UNSAFE
    elif not a["scope_approved"]:
        refuse_status = STATUS_REFUSED_OUT_OF_SCOPE
    else:
        refuse_status = STATUS_COMPLETED  # provisional; refined below

    if not permitted:
        return _blank_summary(
            refuse_status,
            blocked_reasons,
            human_run_approved=a["human_run_approved"],
            safe=a["safe"],
            fetch_permitted=permitted,
            destination=destination,
            report_path=report_path,
            pre_run_contract_valid=pre_run_contract_valid,
        )

    # Permitted by the contract -- but the runner still cannot act without an
    # injected client and an injected writer. These guarantee no accidental live
    # call and no accidental real-repo write: the runner has neither network nor
    # filesystem-write capability of its own.
    if provider_client is None:
        blocked_reasons.append("no_provider_client_injected")
        return _blank_summary(
            STATUS_BLOCKED_NO_PROVIDER,
            blocked_reasons,
            human_run_approved=a["human_run_approved"],
            safe=a["safe"],
            fetch_permitted=permitted,
            destination=destination,
            report_path=report_path,
            pre_run_contract_valid=pre_run_contract_valid,
        )
    if writer is None:
        blocked_reasons.append("no_writer_injected")
        return _blank_summary(
            STATUS_BLOCKED_NO_WRITER,
            blocked_reasons,
            human_run_approved=a["human_run_approved"],
            safe=a["safe"],
            fetch_permitted=permitted,
            destination=destination,
            report_path=report_path,
            pre_run_contract_valid=pre_run_contract_valid,
        )

    # --- perform the read-only fetch via the injected client only ---
    # The runner builds approved RELATIVE paths + text and hands them to the
    # injected writer.persist sink; it opens no file itself.
    timeframe = a["requested_timeframes"][0]
    attempted = list(a["requested_symbols"])
    fetched: list[str] = []
    skipped: list[str] = []
    wrote_files: list[str] = []
    provider_call_count = 0
    fetched_bars: dict[str, list[dict[str, Any]]] = {}

    for symbol in attempted:
        bars = provider_client.fetch_historical_daily_bars(symbol, timeframe)
        provider_call_count += 1
        if not bars:
            skipped.append(symbol)
            continue
        bars = list(bars)
        fetched_bars[symbol] = bars
        rel = _join_rel(destination, symbol + "_" + timeframe + ".json")
        writer.persist(
            rel,
            json.dumps(
                {"symbol": symbol, "timeframe": timeframe, "bars": bars},
                ensure_ascii=False,
                indent=2,
            ),
        )
        fetched.append(symbol)
        wrote_files.append(rel)

    # --- write manifest + gap report under the approved report dir ---
    manifest_entries = []
    for symbol in fetched:
        bars = fetched_bars[symbol]
        lo, hi = _date_range(bars)
        manifest_entries.append(
            {
                "pair": symbol + "@" + timeframe,
                "row_count": len(bars),
                "date_min": lo,
                "date_max": hi,
            }
        )
    manifest = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "provider": FETCH_APPROVED_PROVIDER,
        "destination": destination,
        "attempted_symbols": attempted,
        "fetched_symbols": fetched,
        "skipped_symbols": skipped,
        "entries": manifest_entries,
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
    }
    writer.persist(
        FETCH_MANIFEST_REPORT_PATH,
        json.dumps(manifest, ensure_ascii=False, indent=2),
    )
    wrote_files.append(FETCH_MANIFEST_REPORT_PATH)

    gap_lines = ["# Crypto-D1 Databento Gap Report", ""]
    for symbol in attempted:
        if symbol in fetched:
            lo, hi = _date_range(fetched_bars[symbol])
            gap_lines.append(
                "- "
                + symbol
                + "@"
                + timeframe
                + ": "
                + str(len(fetched_bars[symbol]))
                + " rows ["
                + lo
                + ".."
                + hi
                + "]"
            )
        else:
            gap_lines.append(
                "- " + symbol + "@" + timeframe + ": NO DATA (skipped)"
            )
    writer.persist(FETCH_GAP_REPORT_PATH, "\n".join(gap_lines) + "\n")
    wrote_files.append(FETCH_GAP_REPORT_PATH)

    writes_under_base = all(
        not p.startswith("..") and not p.startswith("/") for p in wrote_files
    )

    return _summary(
        status=STATUS_COMPLETED,
        attempted=attempted,
        fetched=fetched,
        skipped=skipped,
        destination=destination,
        report_path=report_path,
        provider_call_count=provider_call_count,
        wrote_files=wrote_files,
        blocked_reasons=blocked_reasons,
        performs_data_fetch=True,
        human_run_approved=a["human_run_approved"],
        safe=a["safe"],
        fetch_permitted=permitted,
        pre_run_contract_valid=pre_run_contract_valid,
        writes_under_base=writes_under_base,
    )


# --------------------------------------------------------------------------- #
# post-run validation
# --------------------------------------------------------------------------- #
_REQUIRED_SUMMARY_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status_label",
    "mode",
    "run_status",
    "attempted_symbols",
    "fetched_symbols",
    "skipped_symbols",
    "destination",
    "report_path",
    "provider_call_count",
    "wrote_files",
    "blocked_reasons",
    "safety_confirmations",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "calls_databento_directly",
    "uses_network_directly",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_fetch_run_summary(summary: Any) -> dict[str, Any]:
    """Validate (read-only) a run summary -- the AFTER-run check. Returns a verdict
    dict of boolean checks plus an overall `valid`."""
    s = summary if isinstance(summary, dict) else {}
    missing_fields = [f for f in _REQUIRED_SUMMARY_FIELDS if f not in s]

    schema_ok = s.get("schema_version") == RUNNER_SCHEMA_VERSION
    label_ok = s.get("label") == RUNNER_LABEL
    status_label_ok = s.get("status_label") == RUNNER_STATUS
    read_only = s.get("read_only") is True
    flags_false = all(s.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = s.get("authorizes_nothing") is True
    gates_locked = all(s.get(g) is True for g in _ALL_GATE_LOCKS)
    states_blocked_locked = (
        s.get("real_data_qa_state") == "BLOCKED"
        and s.get("baseline_backtest_state") == "BLOCKED"
        and s.get("paper_live_state") == "LOCKED"
    )

    conf = s.get("safety_confirmations")
    safety_confirmations_ok = isinstance(conf, dict) and all(
        conf.get(k) is True
        for k in (
            "runner_constructs_no_live_client",
            "no_network_in_runner",
            "no_credential_read",
            "no_dotenv_read",
            "no_secret_logged",
            "writes_only_under_base_dir",
            "no_trading_or_order_action",
            "gates_remain_locked",
        )
    )

    wrote = s.get("wrote_files") or []
    wrote_is_list = isinstance(wrote, list)
    writes_under_base = wrote_is_list and all(
        isinstance(p, str) and not p.startswith("..") and not _is_abs_like(p)
        for p in wrote
    )

    attempted = s.get("attempted_symbols") or []
    fetched = s.get("fetched_symbols") or []
    skipped = s.get("skipped_symbols") or []
    fetched_in_scope = all(sym in FETCH_APPROVED_SYMBOLS for sym in fetched)
    counts_consistent = isinstance(attempted, list) and (
        set(fetched) | set(skipped) == set(attempted)
        if attempted
        else (not fetched and not skipped)
    )

    completed = s.get("run_status") == STATUS_COMPLETED
    blocked_consistency = (
        completed
        or (
            s.get("performs_data_fetch") is False
            and s.get("provider_call_count") == 0
            and not wrote
        )
    )
    completed_consistency = (
        (not completed)
        or (
            s.get("performs_data_fetch") is True
            and s.get("provider_call_count") == len(attempted)
        )
    )

    no_secret_value_fields = not _has_secret_value(s)

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_label_ok": status_label_ok,
        "read_only": read_only,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "states_blocked_locked": states_blocked_locked,
        "safety_confirmations_ok": safety_confirmations_ok,
        "writes_under_base": writes_under_base,
        "fetched_in_scope": fetched_in_scope,
        "counts_consistent": counts_consistent,
        "blocked_consistency": blocked_consistency,
        "completed_consistency": completed_consistency,
        "no_secret_value_fields": no_secret_value_fields,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
    return verdict


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def render_fetch_run_summary_markdown(summary: Any) -> str:
    """Render a run summary as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    s = summary if isinstance(summary, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Databento Read-Only Fetch Run Summary")
    lines.append("")
    lines.append("- Label: " + str(s.get("label", "")))
    lines.append("- Run status: " + str(s.get("run_status", "")))
    lines.append("- Human-run approved: " + str(s.get("human_run_approved", False)))
    lines.append(
        "- Performs data fetch: " + str(s.get("performs_data_fetch", False))
    )
    lines.append("- Destination: " + str(s.get("destination", "")))
    lines.append("- Report path: " + str(s.get("report_path", "")))
    lines.append(
        "- Provider call count: " + str(s.get("provider_call_count", 0))
    )
    lines.append("- real_data_qa state: " + str(s.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(s.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(s.get("paper_live_state", "")))
    lines.append("")
    lines.append("## Attempted Symbols")
    for sym in s.get("attempted_symbols", []) or ["(none)"]:
        lines.append("- " + str(sym))
    lines.append("")
    lines.append("## Fetched Symbols")
    for sym in s.get("fetched_symbols", []) or ["(none)"]:
        lines.append("- " + str(sym))
    lines.append("")
    lines.append("## Skipped Symbols")
    for sym in s.get("skipped_symbols", []) or ["(none)"]:
        lines.append("- " + str(sym))
    lines.append("")
    lines.append("## Wrote Files")
    for path in s.get("wrote_files", []) or ["(none)"]:
        lines.append("- " + str(path))
    lines.append("")
    lines.append("## Blocked Reasons")
    for reason in s.get("blocked_reasons", []) or ["(none)"]:
        lines.append("- " + str(reason))
    lines.append("")
    lines.append("## Safety Confirmations")
    for key, value in (s.get("safety_confirmations") or {}).items():
        lines.append("- " + str(key) + ": " + str(value))
    return "\n".join(lines)
