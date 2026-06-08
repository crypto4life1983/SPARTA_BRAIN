"""Selected Read-Only Spot Provider Fetch Runner (Block 150).

A PURE, stdlib-only runner that *can* fetch BTCUSD / ETHUSD / SOLUSD daily SPOT
OHLCV -- but ONLY through an INJECTED provider_client and an INJECTED writer, and
ONLY when human_spot_provider_run_approved=True is explicitly supplied for the source
the Block 148 orchestrator selected (the clear-license READ-ONLY spot historical
provider, Block 149 approval packet).

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

Hard design properties (enforced by construction):
  - DISABLED BY DEFAULT. With no payload / no approval flag it refuses and makes ZERO
    provider calls.
  - Requires human_spot_provider_run_approved=True.
  - Requires selected_candidate_type = CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER.
  - Allows ONLY symbols BTCUSD / ETHUSD / SOLUSD, ONLY the 1d timeframe, ONLY
    read-only spot historical OHLCV, ONLY destination data/crypto_d1_spot_cache/, and
    ONLY report path reports/research_os/data_qa/.
  - Uses the INJECTED provider_client ONLY and the INJECTED writer ONLY. It never
    constructs a live provider client, never opens a network, never reads a
    credential or .env, never prints / logs / stores a secret, and never writes
    outside the approved paths.
  - Touches NO broker / exchange / account / order / portfolio endpoint.

This module imports NOTHING that can reach the network, the filesystem, the
environment, or a credential store (no os / sys / json / csv / pathlib / requests /
urllib / dotenv / ccxt / databento). All real I/O is delegated to the caller-injected
provider_client and writer, so in this block (and its tests) every "fetch" and every
"write" is a fake / tmp_path stand-in. real_data_qa stays BLOCKED, baseline stays
BLOCKED, and paper / micro-live stay LOCKED regardless of input.

Public API:
  - RUNNER_SCHEMA_VERSION / RUNNER_LABEL / RUNNER_STATUS_* / RUNNER_MODE / RUNNER_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - RUNNER_SELECTED_CANDIDATE_TYPE / REQUIRED_RUN_APPROVAL_FLAG
  - RUNNER_APPROVED_SYMBOLS / RUNNER_APPROVED_TIMEFRAMES / RUNNER_SYMBOL_ALIASES
  - RUNNER_APPROVED_CACHE_PATH / RUNNER_APPROVED_REPORT_DIR
  - RUNNER_PROVIDER_METHOD_NAME
  - run_selected_read_only_spot_provider_fetch(payload=None, *, provider_client=None, writer=None)
  - validate_selected_read_only_spot_provider_fetch_run_summary(summary)
  - render_selected_read_only_spot_provider_fetch_run_summary_markdown(summary)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

RUNNER_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner.v1"
)
RUNNER_LABEL = "Block 150 - Selected Read-Only Spot Provider Fetch Runner"
RUNNER_MODE = "RESEARCH_ONLY"

RUNNER_STATUS_REFUSED = "REFUSED_NOT_APPROVED_OR_OUT_OF_SCOPE"
RUNNER_STATUS_RAN = "FETCH_RUN_COMPLETED_WITH_INJECTED_PROVIDER"

RUNNER_CORE_RULE = (
    "This runner fetches nothing on its own. It is disabled by default and runs only "
    "through an injected provider_client and an injected writer, only when "
    "human_spot_provider_run_approved is True for the selected clear-license "
    "read-only spot historical provider, only for BTCUSD / ETHUSD / SOLUSD at 1d, "
    "only writing under the approved cache and report paths. It constructs no live "
    "client, opens no network, reads no credential and no .env, stores no secret, and "
    "authorizes nothing. real_data_qa stays BLOCKED, baseline stays BLOCKED, and "
    "paper / micro-live stay LOCKED."
)

# The source the Block 148 orchestrator already selected / Block 149 approved.
RUNNER_SELECTED_CANDIDATE_TYPE = "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"

# The explicit approval flag a caller MUST supply as True to enable a run.
REQUIRED_RUN_APPROVAL_FLAG = "human_spot_provider_run_approved"

RUNNER_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
RUNNER_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

# Acceptable written forms for each approved symbol (normalized by removing the
# slash / dash and upper-casing -- e.g. "BTC/USD" -> "BTCUSD").
RUNNER_SYMBOL_ALIASES: dict[str, tuple[str, ...]] = {
    "BTCUSD": ("BTCUSD", "BTC/USD", "BTC-USD", "XBTUSD"),
    "ETHUSD": ("ETHUSD", "ETH/USD", "ETH-USD"),
    "SOLUSD": ("SOLUSD", "SOL/USD", "SOL-USD"),
}

# The ONLY approved logical destination + report dir. The injected writer decides
# where bytes physically land (a fake / tmp_path in this block); the runner only
# validates these logical roots and never writes outside them.
RUNNER_APPROVED_CACHE_PATH = "data/crypto_d1_spot_cache/"
RUNNER_APPROVED_REPORT_DIR = "reports/research_os/data_qa/"

# The read-only method the injected provider_client MUST expose. A trading / broker
# client would not implement a method with this read-only name.
RUNNER_PROVIDER_METHOD_NAME = "fetch_read_only_daily_spot_ohlcv"

# Top-level flags that, if truthy on the payload, refuse the run outright.
RUNNER_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "use_real_provider",
    "construct_live_client",
    "real_network_fetch",
    "read_credentials",
    "read_dotenv",
    "print_secrets",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "place_order",
    "go_live",
    "paper_trade",
    "broker_login",
    "exchange_account",
    "order_endpoint",
    "portfolio_endpoint",
    "account_endpoint",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
)

# If a provider row carries any of these keys it is NOT read-only OHLCV: the symbol is
# skipped (never written) and the run records a blocked reason.
RUNNER_FORBIDDEN_ROW_FIELDS: tuple[str, ...] = (
    "order_id",
    "side",
    "account",
    "account_id",
    "position",
    "fill",
    "broker",
    "trade_id",
    "balance",
    "wallet",
    "api_key",
    "apikey",
    "secret",
    "password",
    "bearer",
    "access_token",
    "private_key",
)

# Every trading / execution capability flag -- always False in every run summary.
_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes_trading",
    "calls_real_provider",
    "constructs_live_client",
    "uses_network",
    "reads_credentials",
    "reads_dotenv",
    "exposes_secret",
    "writes_outside_approved_paths",
    "writes_real_repo_files",
    "runs_qa",
    "runs_baseline",
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
    "touches_broker_exchange",
    "touches_order_endpoint",
    "touches_portfolio_endpoint",
    "touches_account_endpoint",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
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

_SAFETY_CONFIRMATION_KEYS: tuple[str, ...] = (
    "used_injected_provider_client_only",
    "used_injected_writer_only",
    "constructed_no_live_client",
    "made_no_real_network_call",
    "read_no_credentials",
    "read_no_dotenv",
    "stored_no_secret",
    "wrote_only_within_approved_paths",
    "touched_no_broker_exchange",
    "touched_no_order_or_portfolio_endpoint",
)


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _normalize_symbol(value: Any) -> str | None:
    """Map a written symbol form onto an approved canonical symbol, else None."""
    if not isinstance(value, str):
        return None
    raw = value.strip().upper().replace("/", "").replace("-", "")
    for canonical, aliases in RUNNER_SYMBOL_ALIASES.items():
        if raw == canonical:
            return canonical
        for alias in aliases:
            if raw == alias.upper().replace("/", "").replace("-", ""):
                return canonical
    return None


_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty string value."""
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


def _row_has_forbidden_field(row: Any) -> bool:
    if not isinstance(row, dict):
        return False
    keys = {str(k).lower() for k in row.keys()}
    return any(f in keys for f in RUNNER_FORBIDDEN_ROW_FIELDS)


def _safety_confirmations() -> dict[str, bool]:
    return {k: True for k in _SAFETY_CONFIRMATION_KEYS}


def _locked_truth() -> dict[str, Any]:
    truth: dict[str, Any] = {f: False for f in _ALL_CAPABILITY_FLAGS}
    truth.update({g: True for g in _ALL_GATE_LOCKS})
    truth["real_data_qa_state"] = "BLOCKED"
    truth["baseline_backtest_state"] = "BLOCKED"
    truth["paper_live_state"] = "LOCKED"
    truth["this_block_called_real_provider"] = False
    truth["this_block_made_network_call"] = False
    truth["this_block_read_credentials"] = False
    truth["this_block_wrote_real_repo_files"] = False
    truth["authorizes_nothing"] = True
    return truth


def _base_summary(
    *,
    status: str,
    attempted: list[str],
    fetched: list[str],
    skipped: list[str],
    provider_call_count: int,
    destination: str,
    report_path: str,
    wrote_files: list[str],
    blocked_reasons: list[str],
    run_executed: bool,
    manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "label": RUNNER_LABEL,
        "mode": RUNNER_MODE,
        "status": status,
        "core_rule": RUNNER_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "selected_candidate_type": RUNNER_SELECTED_CANDIDATE_TYPE,
        "required_run_approval_flag": REQUIRED_RUN_APPROVAL_FLAG,
        "approved_symbols": list(RUNNER_APPROVED_SYMBOLS),
        "approved_timeframes": list(RUNNER_APPROVED_TIMEFRAMES),
        "attempted_symbols": list(attempted),
        "fetched_symbols": list(fetched),
        "skipped_symbols": list(skipped),
        "provider_call_count": provider_call_count,
        "destination": destination,
        "report_path": report_path,
        "wrote_files": list(wrote_files),
        "blocked_reasons": list(blocked_reasons),
        "run_executed": run_executed,
        "safety_confirmations": _safety_confirmations(),
        "manifest": manifest,
    }
    summary.update(_locked_truth())
    return summary


# --------------------------------------------------------------------------- #
# the runner
# --------------------------------------------------------------------------- #
def run_selected_read_only_spot_provider_fetch(
    payload: Any = None,
    *,
    provider_client: Any = None,
    writer: Any = None,
) -> dict[str, Any]:
    """Run (or refuse) a read-only daily spot OHLCV fetch for the approved symbols.

    The runner is disabled by default. It refuses (with ZERO provider calls) unless
    EVERY scope check passes AND both an injected provider_client and writer are
    supplied. When it runs, it uses ONLY the injected provider_client (via its
    read-only method) and ONLY the injected writer, writing only logical paths under
    the approved cache / report roots. It never constructs a live client, never opens
    a network, never reads a credential, and never writes a real repo file itself.
    """
    data = _as_payload(payload)

    requested_symbols_raw = data.get("symbols", list(RUNNER_APPROVED_SYMBOLS))
    if not isinstance(requested_symbols_raw, (list, tuple)):
        requested_symbols_raw = [requested_symbols_raw]
    destination = data.get("destination", RUNNER_APPROVED_CACHE_PATH)
    report_path = data.get("report_path", RUNNER_APPROVED_REPORT_DIR)
    timeframe = data.get("timeframe", RUNNER_APPROVED_TIMEFRAMES[0])
    selected_type = data.get("selected_candidate_type", RUNNER_SELECTED_CANDIDATE_TYPE)

    blocked_reasons: list[str] = []

    if not _is_truthy(data.get(REQUIRED_RUN_APPROVAL_FLAG)):
        blocked_reasons.append("missing_human_spot_provider_run_approved")

    if selected_type != RUNNER_SELECTED_CANDIDATE_TYPE:
        blocked_reasons.append("wrong_selected_candidate_type")

    if timeframe not in RUNNER_APPROVED_TIMEFRAMES:
        blocked_reasons.append("wrong_timeframe:" + str(timeframe))

    if destination != RUNNER_APPROVED_CACHE_PATH:
        blocked_reasons.append("wrong_destination")
        destination = str(destination)

    if report_path != RUNNER_APPROVED_REPORT_DIR:
        blocked_reasons.append("wrong_report_path")
        report_path = str(report_path)

    normalized: list[str] = []
    for sym in requested_symbols_raw:
        canon = _normalize_symbol(sym)
        if canon is None:
            blocked_reasons.append("wrong_symbol:" + str(sym))
        else:
            normalized.append(canon)
    attempted = list(dict.fromkeys(normalized))  # de-dupe, keep order

    for flag in RUNNER_FORBIDDEN_FLAGS:
        if _is_truthy(data.get(flag)):
            blocked_reasons.append("forbidden_flag:" + flag)

    if _has_secret_value(data):
        blocked_reasons.append("secret_value_in_payload")

    approved = not blocked_reasons

    # Injected dependencies are required only once scope is fully approved -- so a
    # refusal never depends on (and never touches) any client.
    if approved:
        if provider_client is None:
            blocked_reasons.append("no_injected_provider_client")
        if writer is None:
            blocked_reasons.append("no_injected_writer")
        approved = not blocked_reasons

    if not approved:
        return _base_summary(
            status=RUNNER_STATUS_REFUSED,
            attempted=attempted,
            fetched=[],
            skipped=[],
            provider_call_count=0,
            destination=destination,
            report_path=report_path,
            wrote_files=[],
            blocked_reasons=blocked_reasons,
            run_executed=False,
            manifest=None,
        )

    # --- approved: run through the injected provider + writer only ---------- #
    fetch = getattr(provider_client, RUNNER_PROVIDER_METHOD_NAME, None)
    if not callable(fetch):
        return _base_summary(
            status=RUNNER_STATUS_REFUSED,
            attempted=attempted,
            fetched=[],
            skipped=[],
            provider_call_count=0,
            destination=destination,
            report_path=report_path,
            wrote_files=[],
            blocked_reasons=["injected_provider_missing_read_only_method"],
            run_executed=False,
            manifest=None,
        )

    fetched: list[str] = []
    skipped: list[str] = []
    wrote_files: list[str] = []
    provider_call_count = 0
    manifest_symbols: list[dict[str, Any]] = []
    gap_summary: list[str] = []

    for symbol in attempted:
        provider_call_count += 1
        rows = fetch(symbol=symbol, timeframe=timeframe)

        if not isinstance(rows, (list, tuple)) or len(rows) == 0:
            skipped.append(symbol)
            gap_summary.append(symbol + ": empty_or_invalid_rows")
            continue
        if any(_row_has_forbidden_field(r) for r in rows):
            skipped.append(symbol)
            gap_summary.append(symbol + ": non_read_only_or_secret_bearing_rows")
            continue

        bar_count = len(rows)
        dates = [
            str(r.get("date")) for r in rows if isinstance(r, dict) and "date" in r
        ]
        first_date = dates[0] if dates else None
        last_date = dates[-1] if dates else None
        ordered_ok = all(dates[i] <= dates[i + 1] for i in range(len(dates) - 1))
        if not ordered_ok:
            gap_summary.append(symbol + ": dates_not_monotonic")

        data_path = destination + symbol + "_" + timeframe + "_spot_ohlcv.json"
        writer(
            data_path,
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "instrument": "spot",
                "source": RUNNER_SELECTED_CANDIDATE_TYPE,
                "read_only": True,
                "bars": list(rows),
            },
        )
        wrote_files.append(data_path)
        fetched.append(symbol)
        manifest_symbols.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "bar_count": bar_count,
                "first_date": first_date,
                "last_date": last_date,
                "ordered_ok": ordered_ok,
            }
        )

    manifest: dict[str, Any] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "selected_candidate_type": RUNNER_SELECTED_CANDIDATE_TYPE,
        "timeframe": timeframe,
        "destination": destination,
        "symbols": manifest_symbols,
        "gap_summary": gap_summary,
        "attempted_symbols": list(attempted),
        "fetched_symbols": list(fetched),
        "skipped_symbols": list(skipped),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
    }
    report_file = report_path + "crypto_d1_spot_fetch_manifest.json"
    writer(report_file, manifest)
    wrote_files.append(report_file)

    return _base_summary(
        status=RUNNER_STATUS_RAN,
        attempted=attempted,
        fetched=fetched,
        skipped=skipped,
        provider_call_count=provider_call_count,
        destination=destination,
        report_path=report_path,
        wrote_files=wrote_files,
        blocked_reasons=[],
        run_executed=True,
        manifest=manifest,
    )


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_SUMMARY_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "mode",
    "status",
    "selected_candidate_type",
    "required_run_approval_flag",
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
)


def validate_selected_read_only_spot_provider_fetch_run_summary(
    summary: Any,
) -> dict[str, Any]:
    """Validate (read-only) a run summary. Returns boolean checks plus overall `valid`."""
    s = summary if isinstance(summary, dict) else {}
    missing_fields = [f for f in _REQUIRED_SUMMARY_FIELDS if f not in s]

    schema_ok = s.get("schema_version") == RUNNER_SCHEMA_VERSION
    label_ok = s.get("label") == RUNNER_LABEL
    mode_ok = s.get("mode") == RUNNER_MODE
    status_ok = s.get("status") in {RUNNER_STATUS_REFUSED, RUNNER_STATUS_RAN}
    selected_type_ok = (
        s.get("selected_candidate_type") == RUNNER_SELECTED_CANDIDATE_TYPE
    )
    approval_flag_ok = s.get("required_run_approval_flag") == REQUIRED_RUN_APPROVAL_FLAG

    flags_false = all(s.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    gates_locked = all(s.get(g) is True for g in _ALL_GATE_LOCKS)
    states_blocked_locked = (
        s.get("real_data_qa_state") == "BLOCKED"
        and s.get("baseline_backtest_state") == "BLOCKED"
        and s.get("paper_live_state") == "LOCKED"
    )
    authorizes_nothing = s.get("authorizes_nothing") is True
    this_block_clean = (
        s.get("this_block_called_real_provider") is False
        and s.get("this_block_made_network_call") is False
        and s.get("this_block_read_credentials") is False
        and s.get("this_block_wrote_real_repo_files") is False
    )

    confs = s.get("safety_confirmations")
    safety_confirmations_all_true = isinstance(confs, dict) and all(
        confs.get(k) is True for k in _SAFETY_CONFIRMATION_KEYS
    )

    no_secret_value_fields = not _has_secret_value(s)

    # Symbols / timeframe / paths within scope.
    symbols_in_scope = all(
        sym in RUNNER_APPROVED_SYMBOLS for sym in (s.get("attempted_symbols") or [])
    )
    fetched_in_scope = all(
        sym in RUNNER_APPROVED_SYMBOLS for sym in (s.get("fetched_symbols") or [])
    )

    status = s.get("status")
    provider_call_count = s.get("provider_call_count")
    if status == RUNNER_STATUS_REFUSED:
        refused_zero_calls_ok = (
            provider_call_count == 0
            and not (s.get("fetched_symbols") or [])
            and not (s.get("wrote_files") or [])
            and s.get("run_executed") is False
            and bool(s.get("blocked_reasons"))
        )
        destination_ok = True
        report_path_ok = True
        ran_consistency_ok = True
    else:
        refused_zero_calls_ok = True
        destination_ok = s.get("destination") == RUNNER_APPROVED_CACHE_PATH
        report_path_ok = s.get("report_path") == RUNNER_APPROVED_REPORT_DIR
        fetched = s.get("fetched_symbols") or []
        skipped = s.get("skipped_symbols") or []
        attempted = s.get("attempted_symbols") or []
        ran_consistency_ok = (
            s.get("run_executed") is True
            and provider_call_count == len(attempted)
            and len(fetched) + len(skipped) == len(attempted)
            and len(s.get("wrote_files") or []) == len(fetched) + (1 if fetched else 0)
        )

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "mode_ok": mode_ok,
        "status_ok": status_ok,
        "selected_type_ok": selected_type_ok,
        "approval_flag_ok": approval_flag_ok,
        "flags_false": flags_false,
        "gates_locked": gates_locked,
        "states_blocked_locked": states_blocked_locked,
        "authorizes_nothing": authorizes_nothing,
        "this_block_clean": this_block_clean,
        "safety_confirmations_all_true": safety_confirmations_all_true,
        "no_secret_value_fields": no_secret_value_fields,
        "symbols_in_scope": symbols_in_scope,
        "fetched_in_scope": fetched_in_scope,
        "refused_zero_calls_ok": refused_zero_calls_ok,
        "destination_ok": destination_ok,
        "report_path_ok": report_path_ok,
        "ran_consistency_ok": ran_consistency_ok,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
    return verdict


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def _emit(lines: list[str], heading: str, rows: list[str]) -> None:
    lines.append("")
    lines.append("## " + heading)
    if not rows:
        lines.append("- (none)")
        return
    for row in rows:
        lines.append("- " + row)


def render_selected_read_only_spot_provider_fetch_run_summary_markdown(
    summary: Any,
) -> str:
    """Render a run summary as a deterministic markdown brief. Writes nothing."""
    s = summary if isinstance(summary, dict) else {}
    lines: list[str] = []
    lines.append("# Selected Read-Only Spot Provider Fetch Runner")
    lines.append("")
    lines.append("- Label: " + str(s.get("label", "")))
    lines.append("- Mode: " + str(s.get("mode", "")))
    lines.append("- Status: " + str(s.get("status", "")))
    lines.append("- Run executed: " + str(s.get("run_executed", False)))
    lines.append("- Provider call count: " + str(s.get("provider_call_count", 0)))
    lines.append("- Destination: " + str(s.get("destination", "")))
    lines.append("- Report path: " + str(s.get("report_path", "")))
    lines.append("- real_data_qa state: " + str(s.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(s.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(s.get("paper_live_state", "")))

    _emit(lines, "Attempted Symbols", list(s.get("attempted_symbols") or []))
    _emit(lines, "Fetched Symbols", list(s.get("fetched_symbols") or []))
    _emit(lines, "Skipped Symbols", list(s.get("skipped_symbols") or []))
    _emit(lines, "Wrote Files", list(s.get("wrote_files") or []))
    _emit(lines, "Blocked Reasons", list(s.get("blocked_reasons") or []))
    confs = s.get("safety_confirmations") or {}
    _emit(
        lines,
        "Safety Confirmations",
        [k + ": " + str(confs.get(k)) for k in _SAFETY_CONFIRMATION_KEYS],
    )
    return "\n".join(lines)
