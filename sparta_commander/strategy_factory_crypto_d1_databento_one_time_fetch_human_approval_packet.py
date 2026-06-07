"""Crypto-D1 Databento One-Time Read-Only Fetch -- Human-Run Approval Packet (Block 144).

A PURE, stdlib-only, *read-only* PACKET / SPEC layer. It is the single document a
human operator reads and signs off before authorizing ONE controlled, read-only
Databento historical fetch of the three missing Crypto-D1 daily pairs (BTCUSD@1d,
ETHUSD@1d, SOLUSD@1d). It states the EXACT operator command / payload shape, the
pre- and post-run safety checks, the allowed outputs, and the hard stops the
Block 143 runner would honour. It is the human-facing approval form for that run.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS packet executes NOTHING. It does NOT call Databento, open a network, fetch or
download data, inspect or read any credential, read a .env file, print / store /
log any secret, read or write any data file, write a manifest / gap report, run QA,
run a backtest, open a file, spawn a subprocess, read an environment variable, mint
an id, or record a timestamp. It only assembles a static, deterministic approval
document and emits it for human review.

WHAT THE PACKET DESCRIBES (and nothing it does):
  - The exact `human_run_approved=True` run payload an operator would hand to the
    Block 143 runner, plus the shape of the operator command (which injected
    provider client and writer sink must be supplied from OUTSIDE the runner).
  - The approved scope: BTCUSD / ETHUSD / SOLUSD, 1d only, Databento historical
    read-only provider, destination data/databento_cache/crypto_d1/, report dir
    reports/research_os/data_qa/.
  - Credential handling: existing environment / config may be used by a future
    real provider client only if no secret value is ever printed, logged, or
    written; no .env content is ever printed; no credential is stored in any
    output file.
  - Expected outputs: data files only under the approved destination; manifest /
    gap report only under the approved report path.
  - The hard stops that abort the run before any provider call.

CORE RULE: assembling or reviewing this packet authorizes nothing and crosses no
real-world boundary. real_data_qa stays BLOCKED, baseline stays BLOCKED, and
paper / micro-live stay LOCKED. Granting the run approval this packet describes is
a SEPARATE human action; even then the run only acquires read-only market data and
unlocks no gate.

Public API:
  - PACKET_SCHEMA_VERSION / PACKET_LABEL / PACKET_STATUS / PACKET_MODE / PACKET_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - PACKET_APPROVED_SYMBOLS / PACKET_APPROVED_TIMEFRAMES / PACKET_APPROVED_PAIRS
  - PACKET_APPROVED_PROVIDER / PACKET_APPROVED_DESTINATION / PACKET_APPROVED_REPORT_DIR
  - PACKET_REQUIRED_RUN_FLAG / PACKET_PROVIDER_BOUNDARY_RULES
  - PACKET_CREDENTIAL_HANDLING_RULES / PACKET_EXPECTED_OUTPUTS / PACKET_HARD_STOPS
  - PACKET_SAFETY_POSTURE / DEFAULT_PACKET_INPUT
  - build_approved_run_payload()
  - build_one_time_fetch_human_approval_packet(payload=None)
  - validate_one_time_fetch_human_approval_packet(packet)
  - render_one_time_fetch_human_approval_packet_markdown(packet)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_DESTINATION,
    FETCH_APPROVED_PAIRS,
    FETCH_APPROVED_PROVIDER,
    FETCH_APPROVED_REPORT_DIR,
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    FETCH_GAP_REPORT_PATH,
    FETCH_HUMAN_RUN_APPROVAL_FLAG,
    FETCH_MANIFEST_REPORT_PATH,
    FETCH_PROVIDER_DETAIL,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_runner import (  # noqa: E501
    DEFAULT_RUN_INPUT,
)

PACKET_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet.v1"
)
PACKET_LABEL = (
    "Block 144 - Crypto-D1 Databento One-Time Fetch Human-Run Approval Packet"
)
PACKET_STATUS = "HUMAN_APPROVAL_PACKET_ONLY"
PACKET_MODE = "RESEARCH_ONLY"

PACKET_CORE_RULE = (
    "This packet is the human-facing approval form for ONE controlled, read-only "
    "Databento historical fetch of the missing Crypto-D1 daily pairs. Assembling "
    "or reviewing it authorizes nothing and crosses no real-world boundary: no "
    "Databento call is made, no network is opened, no data is fetched, no "
    "credential is inspected, no .env is read, and no secret is shown. Granting "
    "the run approval it describes is a SEPARATE human action; even then "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live "
    "stay LOCKED."
)

# Approved scope (single source of truth: re-exported from the Block 142 contract).
PACKET_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
PACKET_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES
PACKET_APPROVED_PAIRS: tuple[str, ...] = FETCH_APPROVED_PAIRS
PACKET_APPROVED_PROVIDER = FETCH_APPROVED_PROVIDER
PACKET_PROVIDER_DETAIL = FETCH_PROVIDER_DETAIL
PACKET_APPROVED_DESTINATION = FETCH_APPROVED_DESTINATION
PACKET_APPROVED_REPORT_DIR = FETCH_APPROVED_REPORT_DIR
PACKET_MANIFEST_REPORT_PATH = FETCH_MANIFEST_REPORT_PATH
PACKET_GAP_REPORT_PATH = FETCH_GAP_REPORT_PATH

# 6. The single run flag that must be present and True for the runner to act.
PACKET_REQUIRED_RUN_FLAG = FETCH_HUMAN_RUN_APPROVAL_FLAG  # "human_run_approved"

# 7. Provider boundary rules: a live client is constructed OUTSIDE the runner and
# injected; the runner never builds a hidden client.
PACKET_PROVIDER_BOUNDARY_RULES: tuple[str, ...] = (
    "If a live Databento client is needed, it is constructed OUTSIDE the runner "
    "and passed in as the `provider_client` argument.",
    "The runner constructs no hidden client and has no network capability of its "
    "own; with no client injected it fetches nothing.",
    "The live client may call only the Databento historical market-data endpoint "
    "(read-only daily bars). No exchange / broker / account / trading endpoint.",
    "A writer sink is likewise constructed OUTSIDE the runner and passed in as the "
    "`writer` argument; the runner opens no file of its own.",
)

# 8. Credential handling rules.
PACKET_CREDENTIAL_HANDLING_RULES: tuple[str, ...] = (
    "A future real provider client may use existing environment / config "
    "credentials only -- never new or hard-coded ones.",
    "No secret value is ever printed.",
    "No .env file content is ever printed.",
    "No credential value is ever logged.",
    "No credential value is ever stored in any output file (data, manifest, gap "
    "report, or packet).",
    "If any real secret value would be printed, logged, or written -> hard stop.",
)

# 9. Expected outputs of the approved run (written by the injected writer only).
PACKET_EXPECTED_OUTPUTS: tuple[str, ...] = (
    "Data files for fetched pairs only under data/databento_cache/crypto_d1/.",
    "A manifest only under reports/research_os/data_qa/ recording pair, row "
    "count, and date range.",
    "A gap report only under reports/research_os/data_qa/ recording any missing "
    "pairs or date ranges.",
    "No file anywhere else; no runtime or dashboard output; no credential in any "
    "output.",
)

# 10. Hard stops: if ANY would be true, the runner aborts before any provider call.
PACKET_HARD_STOPS: tuple[str, ...] = (
    "Wrong symbol (anything outside BTCUSD / ETHUSD / SOLUSD) -> hard stop.",
    "Wrong timeframe (anything other than 1d) -> hard stop.",
    "Wrong provider (anything other than Databento historical read-only) -> hard "
    "stop.",
    "Destination outside data/databento_cache/crypto_d1/ -> hard stop.",
    "Report path outside reports/research_os/data_qa/ -> hard stop.",
    "Missing human_run_approved (disabled by default) -> hard stop.",
    "Any exchange / broker / account endpoint would be touched -> hard stop.",
    "Any order / trade / paper / live / account / portfolio flag is set -> hard "
    "stop.",
    "Any credential / secret would be exposed (printed, logged, or written) -> "
    "hard stop.",
    "Any gate unlock (real_data_qa / baseline / paper / micro-live) -> hard stop.",
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe. Mirrors
# the Block 142 contract's authorization-flag family.
PACKET_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "run_qa_now",
    "run_baseline_now",
    "run_backtest_now",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
PACKET_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability / execution
# flag is False.
PACKET_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_packet_only": True,
    "human_approval_required": True,
    "fetch_disabled_by_default": True,
    "executes": False,
    "performs_data_fetch": False,
    "calls_databento": False,
    "uses_network": False,
    "fetches_data": False,
    "downloads_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_manifest": False,
    "writes_reports": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
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
    "authorizes_qa_baseline": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no human_run_approved.
DEFAULT_PACKET_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 Databento one-time fetch approval packet input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _tokenize(text: str) -> list[str]:
    token: list[str] = []
    out: list[str] = []
    for ch in str(text).lower():
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            if token:
                out.append("".join(token))
                token = []
    if token:
        out.append("".join(token))
    return out


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
    """True if any dict key looks like a secret AND carries a non-empty string
    value. A secret VALUE is always a string; booleans (e.g. *_exposed=False) and
    counts are flags, never secrets."""
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


# --------------------------------------------------------------------------- #
# the approved run payload (exact operator command shape)
# --------------------------------------------------------------------------- #
def build_approved_run_payload() -> dict[str, Any]:
    """Build (fresh each call) the EXACT payload an operator hands to the Block 143
    runner to authorize the one-time fetch: the runner's own static input plus the
    single `human_run_approved=True` flag. No secret is included."""
    payload = {
        key: (list(value) if isinstance(value, list) else value)
        for key, value in DEFAULT_RUN_INPUT.items()
    }
    payload[PACKET_REQUIRED_RUN_FLAG] = True
    return payload


def _operator_command_shape() -> dict[str, Any]:
    return {
        "callable": "run_databento_read_only_fetch",
        "module": (
            "sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_runner"
        ),
        "positional_payload": build_approved_run_payload(),
        "keyword_arguments": {
            "provider_client": (
                "a live Databento historical client, constructed OUTSIDE the runner "
                "and injected; never built inside the runner"
            ),
            "writer": (
                "a repo-root writer sink, constructed OUTSIDE the runner and "
                "injected; the runner opens no file itself"
            ),
        },
        "required_run_flag": PACKET_REQUIRED_RUN_FLAG,
        "required_run_flag_value": True,
        "this_packet_invokes_it": False,
    }


# --------------------------------------------------------------------------- #
# packet build
# --------------------------------------------------------------------------- #
def build_one_time_fetch_human_approval_packet(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the human-run approval packet. Every capability /
    execution flag is False and every gate lock is True regardless of input. The
    packet invokes nothing."""
    data = dict(DEFAULT_PACKET_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [f for f in PACKET_FORBIDDEN_FLAGS if _is_truthy(data.get(f))]
    safe = mission_flow_aligned and not forbidden_flag_hits

    spec = {
        # 1-2. approved symbols / timeframe
        "approved_symbols": list(PACKET_APPROVED_SYMBOLS),
        "approved_timeframes": list(PACKET_APPROVED_TIMEFRAMES),
        "approved_pairs": list(PACKET_APPROVED_PAIRS),
        # 3. approved provider
        "approved_provider": PACKET_APPROVED_PROVIDER,
        "provider_detail": PACKET_PROVIDER_DETAIL,
        # 4. approved destination
        "approved_destination": PACKET_APPROVED_DESTINATION,
        # 5. approved report path
        "approved_report_dir": PACKET_APPROVED_REPORT_DIR,
        "manifest_report_path": PACKET_MANIFEST_REPORT_PATH,
        "gap_report_path": PACKET_GAP_REPORT_PATH,
        # 6. required run flag + exact operator command / payload shape
        "required_run_flag": PACKET_REQUIRED_RUN_FLAG,
        "required_run_flag_value": True,
        "approved_run_payload": build_approved_run_payload(),
        "operator_command_shape": _operator_command_shape(),
        # 7. provider / writer boundary rules
        "provider_boundary_rules": list(PACKET_PROVIDER_BOUNDARY_RULES),
        # 8. credential handling rules
        "credential_handling_rules": list(PACKET_CREDENTIAL_HANDLING_RULES),
        "databento_secret_exposed": False,
        # 9. expected outputs
        "expected_outputs": list(PACKET_EXPECTED_OUTPUTS),
        # 10. hard stops
        "hard_stops": list(PACKET_HARD_STOPS),
        # no-unlock confirmation
        "no_unlock_confirmation": {
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    packet: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "label": PACKET_LABEL,
        "status": PACKET_STATUS,
        "mode": PACKET_MODE,
        "core_rule": PACKET_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "approval_packet": spec,
        "packet_summary": (
            "Human-run approval packet for ONE controlled, read-only Databento "
            "historical fetch of the missing Crypto-D1 daily pairs (BTCUSD@1d, "
            "ETHUSD@1d, SOLUSD@1d) into data/databento_cache/crypto_d1/ with a "
            "manifest / gap report under reports/research_os/data_qa/. THIS packet "
            "performs no fetch, calls no Databento, opens no network, and unlocks "
            "nothing."
        ),
        "operator_next_step": (
            "A human reviews this packet and, as a SEPARATE action, decides whether "
            "to grant the one-time run by handing the approved payload (with "
            "human_run_approved=True) plus an externally constructed provider "
            "client and writer sink to the Block 143 runner. Reviewing this packet "
            "acquires no data and unlocks no gate."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only approval packet.",
            "A human separately constructs the live Databento provider client and "
            "the repo-root writer sink OUTSIDE the runner.",
            "A human separately invokes the Block 143 runner with the approved "
            "payload; the run only acquires read-only market data and unlocks no "
            "gate.",
        ],
        "requires_explicit_human_run_approval": True,
        "this_packet_invokes_runner": False,
        "safety_posture": dict(PACKET_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "human_approval_required": True,
        "read_only": True,
        "research_only": True,
        "fetch_disabled_by_default": True,
        "executes": False,
        "performs_data_fetch": False,
        "calls_databento": False,
        "uses_network": False,
        "fetches_data": False,
        "downloads_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_manifest": False,
        "writes_reports": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
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
    return packet


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_PACKET_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "approval_packet",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_SPEC_KEYS: tuple[str, ...] = (
    "approved_symbols",
    "approved_timeframes",
    "approved_provider",
    "approved_destination",
    "approved_report_dir",
    "required_run_flag",
    "approved_run_payload",
    "operator_command_shape",
    "provider_boundary_rules",
    "credential_handling_rules",
    "expected_outputs",
    "hard_stops",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "calls_databento",
    "uses_network",
    "fetches_data",
    "downloads_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_manifest",
    "writes_reports",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
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


def validate_one_time_fetch_human_approval_packet(packet: Any) -> dict[str, Any]:
    """Validate (read-only) a built approval packet. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = packet if isinstance(packet, dict) else {}
    missing_fields = [f for f in _REQUIRED_PACKET_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == PACKET_SCHEMA_VERSION
    label_ok = c.get("label") == PACKET_LABEL
    status_ok = c.get("status") == PACKET_STATUS
    mode_ok = c.get("mode") == PACKET_MODE
    core_rule_ok = c.get("core_rule") == PACKET_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    performs_fetch_false = c.get("performs_data_fetch") is False
    human_required = c.get("human_approval_required") is True
    human_run_required = c.get("requires_explicit_human_run_approval") is True
    fetch_disabled_default = c.get("fetch_disabled_by_default") is True
    invokes_runner_false = c.get("this_packet_invokes_runner") is False
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == PACKET_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )

    spec = c.get("approval_packet")
    spec_is_dict = isinstance(spec, dict)
    spec_keys_ok = spec_is_dict and all(k in spec for k in _REQUIRED_SPEC_KEYS)

    symbols_ok = spec_is_dict and spec.get("approved_symbols") == list(
        PACKET_APPROVED_SYMBOLS
    )
    timeframes_ok = spec_is_dict and spec.get("approved_timeframes") == list(
        PACKET_APPROVED_TIMEFRAMES
    )
    provider_ok = spec_is_dict and spec.get("approved_provider") == (
        PACKET_APPROVED_PROVIDER
    )
    destination_ok = spec_is_dict and spec.get("approved_destination") == (
        PACKET_APPROVED_DESTINATION
    )
    report_dir_ok = spec_is_dict and spec.get("approved_report_dir") == (
        PACKET_APPROVED_REPORT_DIR
    )
    run_flag_ok = spec_is_dict and spec.get("required_run_flag") == (
        PACKET_REQUIRED_RUN_FLAG
    )

    # the approved run payload must carry the run flag = True and stay in scope.
    arp = spec.get("approved_run_payload") if spec_is_dict else None
    approved_payload_ok = isinstance(arp, dict) and (
        arp.get(PACKET_REQUIRED_RUN_FLAG) is True
        and arp.get("requested_symbols") == list(PACKET_APPROVED_SYMBOLS)
        and arp.get("requested_timeframes") == list(PACKET_APPROVED_TIMEFRAMES)
        and arp.get("requested_provider") == PACKET_APPROVED_PROVIDER
        and arp.get("requested_destination") == PACKET_APPROVED_DESTINATION
        and arp.get("requested_report_dir") == PACKET_APPROVED_REPORT_DIR
    )

    # operator command shape: names the runner callable, requires an injected
    # provider client + writer, and does not invoke anything itself.
    ocs = spec.get("operator_command_shape") if spec_is_dict else None
    command_shape_ok = isinstance(ocs, dict) and (
        ocs.get("callable") == "run_databento_read_only_fetch"
        and ocs.get("required_run_flag") == PACKET_REQUIRED_RUN_FLAG
        and ocs.get("required_run_flag_value") is True
        and ocs.get("this_packet_invokes_it") is False
        and isinstance(ocs.get("keyword_arguments"), dict)
        and "provider_client" in ocs["keyword_arguments"]
        and "writer" in ocs["keyword_arguments"]
    )

    boundary_rules_ok = spec_is_dict and bool(spec.get("provider_boundary_rules"))
    credential_rules_ok = spec_is_dict and bool(
        spec.get("credential_handling_rules")
    )
    credential_safe = spec_is_dict and spec.get("databento_secret_exposed") is False
    expected_outputs_ok = spec_is_dict and bool(spec.get("expected_outputs"))
    hard_stops_ok = spec_is_dict and len(spec.get("hard_stops") or ()) >= 10

    nuc = spec.get("no_unlock_confirmation") if spec_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    # authored narrative must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "packet_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(PACKET_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "performs_fetch_false": performs_fetch_false,
        "human_required": human_required,
        "human_run_required": human_run_required,
        "fetch_disabled_default": fetch_disabled_default,
        "invokes_runner_false": invokes_runner_false,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "spec_keys_ok": spec_keys_ok,
        "symbols_ok": symbols_ok,
        "timeframes_ok": timeframes_ok,
        "provider_ok": provider_ok,
        "destination_ok": destination_ok,
        "report_dir_ok": report_dir_ok,
        "run_flag_ok": run_flag_ok,
        "approved_payload_ok": approved_payload_ok,
        "command_shape_ok": command_shape_ok,
        "boundary_rules_ok": boundary_rules_ok,
        "credential_rules_ok": credential_rules_ok,
        "credential_safe": credential_safe,
        "expected_outputs_ok": expected_outputs_ok,
        "hard_stops_ok": hard_stops_ok,
        "no_unlock_ok": no_unlock_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "no_trade_language": no_trade_language,
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


def render_one_time_fetch_human_approval_packet_markdown(packet: Any) -> str:
    """Render a built approval packet as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = packet if isinstance(packet, dict) else {}
    spec = c.get("approval_packet") or {}
    ocs = spec.get("operator_command_shape") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Databento One-Time Fetch Human-Run Approval Packet")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- This packet invokes runner: "
        + str(c.get("this_packet_invokes_runner", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "1. Approved Symbols", list(spec.get("approved_symbols") or []))
    _emit(
        lines,
        "2. Approved Timeframe",
        list(spec.get("approved_timeframes") or []),
    )
    _emit(
        lines,
        "3. Approved Provider",
        [str(spec.get("approved_provider", "")), str(spec.get("provider_detail", ""))],
    )
    _emit(
        lines,
        "4. Approved Destination",
        [str(spec.get("approved_destination", ""))],
    )
    _emit(
        lines,
        "5. Approved Report Path",
        [
            "report dir: " + str(spec.get("approved_report_dir", "")),
            "manifest: " + str(spec.get("manifest_report_path", "")),
            "gap report: " + str(spec.get("gap_report_path", "")),
        ],
    )
    _emit(
        lines,
        "6. Required Run Flag + Operator Command Shape",
        [
            "required_run_flag: " + str(spec.get("required_run_flag", "")),
            "required_run_flag_value: " + str(spec.get("required_run_flag_value", "")),
            "callable: " + str(ocs.get("callable", "")),
            "module: " + str(ocs.get("module", "")),
            "this_packet_invokes_it: " + str(ocs.get("this_packet_invokes_it", False)),
        ],
    )
    _emit(
        lines,
        "7. Provider / Writer Boundary Rules",
        list(spec.get("provider_boundary_rules") or []),
    )
    _emit(
        lines,
        "8. Credential Handling Rules",
        list(spec.get("credential_handling_rules") or []),
    )
    _emit(lines, "9. Expected Outputs", list(spec.get("expected_outputs") or []))
    _emit(lines, "10. Hard Stops", list(spec.get("hard_stops") or []))
    _emit(
        lines,
        "No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
