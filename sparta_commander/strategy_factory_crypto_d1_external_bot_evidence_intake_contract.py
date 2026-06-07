"""SPARTA Offline Strategy Factory - CRYPTO-D1 EXTERNAL BOT EVIDENCE INTAKE
CONTRACT.

A PURE, stdlib-only *read-only paper contract* that converts external AI trading
bot / video / tool *claims* into structured SPARTA research evidence. It takes a
list of free-text claims (e.g. "Hyperliquid whale tracking", "TradingView
execution webhook", "daily alpha brief") and returns a deterministic
classification of each into one of five observation-only evidence buckets:

  - useful_for_research          (a legitimate research artifact, still requires
                                  independent validation)
  - risky_requires_validation    (attractive but unverified; never "free money")
  - blocked_execution_feature    (execution-capable; blocked, never authorized)
  - dashboard_or_brief_candidate (read-only display / summary candidate only;
                                  no account control, no trade command)
  - ignore_or_marketing_claim    (hype / marketing / guaranteed-profit noise)

This contract authorizes NOTHING real. It does not acquire, fetch, inspect,
load, validate, transform, or compute on any market data, runs no QA, baseline,
backtest, or simulation, produces no trade signal, reaches no broker / exchange
/ order / account / API surface, places no order, sends no Telegram trade
command, fires no TradingView execution webhook, trades no paper and no live,
promotes no strategy, unlocks no downstream gate, triggers no automation, writes
no runtime / registry / ledger / dashboard / report state, opens no network,
spawns no child process, writes no file, reads no file, lists no directory,
records no timestamp, mints no random id, reads no environment, and dynamically
imports nothing. It NEVER modifies the external bot's own repository or
dashboard files.

Hard classification stances (every one preserves SPARTA safety gates):
  - Hyperliquid whale tracking is external evidence only -- never execution
    permission.
  - Funding-rate scanning is risky evidence only -- not "free money".
  - Telegram is a read-only command/status interface only -- no trade commands;
    a trade-command variant is a blocked execution feature.
  - TradingView webhooks are future signal-ingestion / logging only -- no
    execution webhook; an execution webhook is a blocked execution feature.
  - Daily alpha brief is a read-only summary only.
  - Portfolio dashboard is a read-only display candidate only -- no account
    control; an account-control variant is a blocked execution feature.
  - Pine Script generation / debugging is a research artifact only -- no live
    strategy deployment; a live-deployment variant is a blocked execution
    feature.
  - Cloud bot operation is blocked unless it is only offline / read-only
    research packaging.
  - Support/resistance chart analysis is useful for research only and requires
    independent validation.

Converting external evidence into structured SPARTA evidence NEVER converts it
into permission for QA, backtest, paper, live, broker/exchange, automation, or
promotion. Every execution-capable idea is marked blocked_execution_feature and
every attractive-but-unverified claim is marked risky_requires_validation.

Public API:
  - EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION
  - DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL
  - EXTERNAL_BOT_EVIDENCE_INTAKE_STATUS
  - EXTERNAL_BOT_EVIDENCE_INTAKE_MODE
  - EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE
  - EVIDENCE_CLASSIFICATION_BUCKETS
  - BUCKET_USEFUL_FOR_RESEARCH
  - BUCKET_RISKY_REQUIRES_VALIDATION
  - BUCKET_BLOCKED_EXECUTION_FEATURE
  - BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE
  - BUCKET_IGNORE_OR_MARKETING_CLAIM
  - CANONICAL_FEATURE_CLASSIFICATIONS
  - EXECUTION_CAPABILITY_MARKERS
  - MARKETING_CLAIM_MARKERS
  - DASHBOARD_OR_BRIEF_MARKERS
  - RESEARCH_ARTIFACT_MARKERS
  - EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION
  - EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE
  - EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - classify_external_bot_evidence_claim(claim)
  - build_crypto_d1_external_bot_evidence_intake_contract(claims=None)
  - validate_crypto_d1_external_bot_evidence_intake_contract(contract)
  - render_crypto_d1_external_bot_evidence_intake_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION",
    "DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_STATUS",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_MODE",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE",
    "EVIDENCE_CLASSIFICATION_BUCKETS",
    "BUCKET_USEFUL_FOR_RESEARCH",
    "BUCKET_RISKY_REQUIRES_VALIDATION",
    "BUCKET_BLOCKED_EXECUTION_FEATURE",
    "BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE",
    "BUCKET_IGNORE_OR_MARKETING_CLAIM",
    "CANONICAL_FEATURE_CLASSIFICATIONS",
    "EXECUTION_CAPABILITY_MARKERS",
    "MARKETING_CLAIM_MARKERS",
    "DASHBOARD_OR_BRIEF_MARKERS",
    "RESEARCH_ARTIFACT_MARKERS",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE",
    "EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "classify_external_bot_evidence_claim",
    "build_crypto_d1_external_bot_evidence_intake_contract",
    "validate_crypto_d1_external_bot_evidence_intake_contract",
    "render_crypto_d1_external_bot_evidence_intake_contract_markdown",
]

EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_external_bot_evidence_intake_contract.v1"
)
DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL = (
    "Strategy Factory Crypto-D1 External Bot Evidence Intake Contract"
)
EXTERNAL_BOT_EVIDENCE_INTAKE_STATUS = (
    "READ_ONLY_CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
)
EXTERNAL_BOT_EVIDENCE_INTAKE_MODE = "RESEARCH_ONLY"

# The five observation-only evidence buckets. Order is stable and is the
# canonical enumeration the contract and its validator compare against.
BUCKET_USEFUL_FOR_RESEARCH = "useful_for_research"
BUCKET_RISKY_REQUIRES_VALIDATION = "risky_requires_validation"
BUCKET_BLOCKED_EXECUTION_FEATURE = "blocked_execution_feature"
BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE = "dashboard_or_brief_candidate"
BUCKET_IGNORE_OR_MARKETING_CLAIM = "ignore_or_marketing_claim"

EVIDENCE_CLASSIFICATION_BUCKETS: tuple[str, ...] = (
    BUCKET_USEFUL_FOR_RESEARCH,
    BUCKET_RISKY_REQUIRES_VALIDATION,
    BUCKET_BLOCKED_EXECUTION_FEATURE,
    BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
    BUCKET_IGNORE_OR_MARKETING_CLAIM,
)
_BUCKET_SET: frozenset[str] = frozenset(EVIDENCE_CLASSIFICATION_BUCKETS)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is a separate, later block; importing the registry would also
# risk a circular import).
EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
)
EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_REQUIRED"
)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract classifies claims on paper and unlocks nothing.
EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE: dict[str, bool] = {
    "acquires_data": False,
    "fetches_data": False,
    "inspects_market_data": False,
    "loads_dataset": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "generates_trade_signal": False,
    "paper_or_live": False,
    "order_logic": False,
    "places_order": False,
    "connects_exchange_or_broker": False,
    "account_access": False,
    "uses_api_keys": False,
    "sends_telegram_trade_command": False,
    "fires_tradingview_execution_webhook": False,
    "controls_portfolio_account": False,
    "deploys_live_strategy": False,
    "operates_cloud_bot": False,
    "selects_live_strategy": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
    "modifies_external_bot": False,
    "promotes_strategy": False,
    "unlocks_downstream_gate": False,
}

# Capability flags a caller-supplied claim record must NOT request. Any truthy
# value forces the claim's classification to blocked_execution_feature and is
# recorded as a forbidden-flag reason. These are descriptive paper guards, not
# runtime switches.
EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_execution",
    "executes",
    "allow_order_placement",
    "places_order",
    "allow_broker_exchange",
    "connects_exchange_or_broker",
    "allow_account_control",
    "controls_portfolio_account",
    "allow_telegram_trade_command",
    "sends_telegram_trade_command",
    "allow_tradingview_execution_webhook",
    "fires_tradingview_execution_webhook",
    "allow_live_deployment",
    "deploys_live_strategy",
    "allow_cloud_bot_operation",
    "operates_cloud_bot",
    "allow_paper_live",
    "paper_or_live",
    "allow_automation",
    "triggers_automation",
    "allow_strategy_promotion",
    "promotes_strategy",
    "allow_downstream_gate_unlock",
    "unlocks_downstream_gate",
)
_FORBIDDEN_FLAG_SET: frozenset[str] = frozenset(
    EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
)

# Real-world capabilities that remain blocked regardless of classification.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_data_acquisition",
    "data_fetch",
    "data_inspection",
    "qa_run",
    "baseline_run",
    "backtest_run",
    "simulation_run",
    "trade_signal_production",
    "order_placement",
    "broker_or_exchange_connection",
    "account_access",
    "api_key_use",
    "telegram_trade_command",
    "tradingview_execution_webhook",
    "portfolio_account_control",
    "live_strategy_deployment",
    "cloud_bot_operation",
    "paper_or_live_trading",
    "strategy_promotion",
    "automation_trigger",
    "downstream_gate_unlock",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
    "external_bot_modification",
)

# Substrings that mark an execution-capable idea. Presence of ANY (after the
# canonical-feature lookup) forces blocked_execution_feature -- safety wins over
# every other bucket.
EXECUTION_CAPABILITY_MARKERS: tuple[str, ...] = (
    "execute",
    "execution",
    "place order",
    "place_order",
    "order placement",
    "auto-trade",
    "auto trade",
    "autotrade",
    "auto-buy",
    "auto-sell",
    "live trade",
    "live trading",
    "place a trade",
    "send order",
    "submit order",
    "broker api",
    "broker_api",
    "exchange api",
    "exchange_api",
    "order webhook",
    "execution webhook",
    "trade command",
    "trade webhook",
    "account control",
    "control account",
    "withdraw",
    "deposit funds",
    "live deployment",
    "deploy live",
    "go live",
    "cloud bot operation",
    "run the bot live",
)

# Substrings that mark hype / marketing / guaranteed-profit noise.
MARKETING_CLAIM_MARKERS: tuple[str, ...] = (
    "guaranteed",
    "guarantee",
    "free money",
    "risk-free",
    "risk free",
    "can't lose",
    "cant lose",
    "no risk",
    "100x",
    "1000x",
    "get rich",
    "to the moon",
    "passive income guaranteed",
    "never lose",
    "instant profit",
    "easy money",
    "sure thing",
)

# Substrings that mark a read-only display / summary / brief candidate.
DASHBOARD_OR_BRIEF_MARKERS: tuple[str, ...] = (
    "dashboard",
    "display",
    "read-only view",
    "read only view",
    "status interface",
    "status panel",
    "summary",
    "daily brief",
    "alpha brief",
    "report view",
    "overview panel",
    "portfolio view",
)

# Substrings that mark a legitimate research artifact (still needs independent
# validation).
RESEARCH_ARTIFACT_MARKERS: tuple[str, ...] = (
    "support/resistance",
    "support resistance",
    "support and resistance",
    "chart analysis",
    "indicator study",
    "pine script generation",
    "pine script debugging",
    "backtest research",
    "pattern study",
    "research artifact",
    "historical study",
    "offline research",
)

# Canonical, explicit per-feature classifications. Keys are normalized feature
# ids; each record names the bucket, the human reason, and whether the feature
# is execution-capable. The build/classify path checks these FIRST so the nine
# named stances from the source idea are honored verbatim.
CANONICAL_FEATURE_CLASSIFICATIONS: dict[str, dict[str, Any]] = {
    "hyperliquid_whale_tracking": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "Hyperliquid whale tracking is external evidence only and never "
            "execution permission."
        ),
    },
    "funding_rate_scanning": {
        "bucket": BUCKET_RISKY_REQUIRES_VALIDATION,
        "execution_capable": False,
        "reason": (
            "Funding-rate scanning is risky evidence only and never 'free "
            "money'; it requires independent validation."
        ),
    },
    "telegram_command_status_interface": {
        "bucket": BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
        "execution_capable": False,
        "reason": (
            "Telegram is a read-only command/status interface only; no trade "
            "commands are permitted."
        ),
    },
    "telegram_trade_command": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "A Telegram trade command is an execution feature and stays "
            "blocked."
        ),
    },
    "tradingview_signal_ingestion_logging": {
        "bucket": BUCKET_RISKY_REQUIRES_VALIDATION,
        "execution_capable": False,
        "reason": (
            "TradingView webhooks are future signal-ingestion / logging only "
            "and require independent validation."
        ),
    },
    "tradingview_execution_webhook": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "A TradingView execution webhook is an execution feature and stays "
            "blocked."
        ),
    },
    "daily_alpha_brief": {
        "bucket": BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
        "execution_capable": False,
        "reason": "Daily alpha brief is a read-only summary only.",
    },
    "portfolio_dashboard": {
        "bucket": BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
        "execution_capable": False,
        "reason": (
            "Portfolio dashboard is a read-only display candidate only; no "
            "account control is permitted."
        ),
    },
    "portfolio_account_control": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Portfolio account control is an execution feature and stays "
            "blocked."
        ),
    },
    "pine_script_generation_debugging": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "Pine Script generation / debugging is a research artifact only; "
            "no live strategy deployment is permitted."
        ),
    },
    "pine_script_live_deployment": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Pine Script live strategy deployment is an execution feature and "
            "stays blocked."
        ),
    },
    "cloud_bot_operation": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Cloud bot operation stays blocked unless it is only offline / "
            "read-only research packaging."
        ),
    },
    "cloud_bot_offline_readonly_research_packaging": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "Offline / read-only research packaging of a cloud bot is a "
            "research artifact only."
        ),
    },
    "support_resistance_chart_analysis": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "Support/resistance chart analysis is useful for research only and "
            "requires independent validation."
        ),
    },
}

# Aliases mapping a normalized free-text claim to a canonical feature id. Each
# alias is matched as a substring of the normalized claim.
_FEATURE_ALIASES: tuple[tuple[str, str], ...] = (
    ("hyperliquid whale", "hyperliquid_whale_tracking"),
    ("whale tracking", "hyperliquid_whale_tracking"),
    ("whale tracker", "hyperliquid_whale_tracking"),
    ("funding rate", "funding_rate_scanning"),
    ("funding-rate", "funding_rate_scanning"),
    ("telegram trade command", "telegram_trade_command"),
    ("telegram trading command", "telegram_trade_command"),
    ("telegram command", "telegram_command_status_interface"),
    ("telegram status", "telegram_command_status_interface"),
    ("telegram assistant", "telegram_command_status_interface"),
    ("telegram bot", "telegram_command_status_interface"),
    ("tradingview execution webhook", "tradingview_execution_webhook"),
    ("tradingview order webhook", "tradingview_execution_webhook"),
    ("execution webhook", "tradingview_execution_webhook"),
    ("tradingview webhook", "tradingview_signal_ingestion_logging"),
    ("tradingview signal", "tradingview_signal_ingestion_logging"),
    ("signal ingestion", "tradingview_signal_ingestion_logging"),
    ("daily alpha brief", "daily_alpha_brief"),
    ("alpha brief", "daily_alpha_brief"),
    ("portfolio account control", "portfolio_account_control"),
    ("account control", "portfolio_account_control"),
    ("portfolio dashboard", "portfolio_dashboard"),
    ("pine script live deployment", "pine_script_live_deployment"),
    ("deploy pine script", "pine_script_live_deployment"),
    ("live pine script", "pine_script_live_deployment"),
    ("pine script", "pine_script_generation_debugging"),
    ("cloud bot offline", "cloud_bot_offline_readonly_research_packaging"),
    ("offline research packaging", "cloud_bot_offline_readonly_research_packaging"),
    ("cloud bot operation", "cloud_bot_operation"),
    ("cloud bot", "cloud_bot_operation"),
    ("support/resistance", "support_resistance_chart_analysis"),
    ("support resistance", "support_resistance_chart_analysis"),
    ("support and resistance", "support_resistance_chart_analysis"),
    ("chart analysis", "support_resistance_chart_analysis"),
)


def _as_text(value: Any) -> str:
    """Coerce any value to a stripped string; non-str/None -> ''."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize(value: Any) -> str:
    """Lowercase, whitespace-collapsed form used for substring matching."""
    text = _as_text(value).lower()
    return " ".join(text.split())


def _truthy(value: Any) -> bool:
    """Conservative truthiness for caller-supplied allow flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "on", "allow")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _claim_text_and_flags(claim: Any) -> tuple[str, str, dict[str, Any]]:
    """Return (raw_text, normalized_text, flags) for a claim that may be a plain
    string or a dict carrying a text field plus optional allow-flags."""
    if isinstance(claim, dict):
        raw = _as_text(
            claim.get("claim")
            or claim.get("text")
            or claim.get("feature")
            or claim.get("name")
        )
        flags = {k: v for k, v in claim.items() if isinstance(k, str)}
        return raw, _normalize(raw), flags
    raw = _as_text(claim)
    return raw, _normalize(raw), {}


def _requested_forbidden_flags(flags: dict[str, Any]) -> tuple[str, ...]:
    """Forbidden allow-flags the claim record requested as truthy."""
    return tuple(
        f
        for f in EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
        if f in flags and _truthy(flags.get(f))
    )


def _match_canonical_feature(normalized: str) -> str | None:
    """Return the canonical feature id for a normalized claim, or None."""
    if not normalized:
        return None
    # Direct id match first (e.g. a caller passing the exact feature id).
    if normalized in CANONICAL_FEATURE_CLASSIFICATIONS:
        return normalized
    underscored = normalized.replace(" ", "_").replace("-", "_")
    if underscored in CANONICAL_FEATURE_CLASSIFICATIONS:
        return underscored
    # Alias substring match (order is most-specific-first).
    for alias, feature_id in _FEATURE_ALIASES:
        if alias in normalized:
            return feature_id
    return None


def _heuristic_bucket(normalized: str) -> tuple[str, str]:
    """Classify a free-text claim with no canonical match. Execution markers win
    first (safety), then marketing, then dashboard/brief, then research artifact,
    then the conservative attractive-but-unverified default."""
    if any(m in normalized for m in EXECUTION_CAPABILITY_MARKERS):
        return (
            BUCKET_BLOCKED_EXECUTION_FEATURE,
            "Execution-capable claim; blocked and never authorized.",
        )
    if any(m in normalized for m in MARKETING_CLAIM_MARKERS):
        return (
            BUCKET_IGNORE_OR_MARKETING_CLAIM,
            "Marketing / guaranteed-profit hype; ignored as evidence.",
        )
    if any(m in normalized for m in DASHBOARD_OR_BRIEF_MARKERS):
        return (
            BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
            "Read-only display / summary candidate only; no account control.",
        )
    if any(m in normalized for m in RESEARCH_ARTIFACT_MARKERS):
        return (
            BUCKET_USEFUL_FOR_RESEARCH,
            "Research artifact; useful for research, requires validation.",
        )
    return (
        BUCKET_RISKY_REQUIRES_VALIDATION,
        "Attractive but unverified claim; requires independent validation.",
    )


def classify_external_bot_evidence_claim(claim: Any) -> dict[str, Any]:
    """Return a deterministic classification for one external bot/video/tool
    claim. Pure; no I/O, no mutation, no timestamp, no random id. Unknown or
    malformed inputs never raise. A requested forbidden allow-flag, or any
    execution marker, forces blocked_execution_feature (safety wins)."""
    raw, normalized, flags = _claim_text_and_flags(claim)

    if not normalized:
        return {
            "claim": raw,
            "bucket": BUCKET_RISKY_REQUIRES_VALIDATION,
            "execution_capable": False,
            "matched_feature": None,
            "requested_forbidden_flags": (),
            "authorizes_nothing": True,
            "reason": "Empty claim; defaulted to risky_requires_validation.",
        }

    forbidden = _requested_forbidden_flags(flags)
    feature_id = _match_canonical_feature(normalized)

    if feature_id is not None:
        spec = CANONICAL_FEATURE_CLASSIFICATIONS[feature_id]
        bucket = spec["bucket"]
        reason = spec["reason"]
        execution_capable = bool(spec["execution_capable"])
    else:
        bucket, reason = _heuristic_bucket(normalized)
        execution_capable = bucket == BUCKET_BLOCKED_EXECUTION_FEATURE

    # Safety override: any requested forbidden flag, or any execution marker in
    # the text, forces the blocked bucket regardless of the canonical/heuristic
    # result -- evidence intake never lets an execution-capable idea pass.
    if forbidden or any(m in normalized for m in EXECUTION_CAPABILITY_MARKERS):
        bucket = BUCKET_BLOCKED_EXECUTION_FEATURE
        execution_capable = True
        if forbidden:
            reason = (
                "Claim requested a forbidden execution allow-flag; forced to "
                "blocked_execution_feature."
            )

    return {
        "claim": raw,
        "bucket": bucket,
        "execution_capable": execution_capable,
        "matched_feature": feature_id,
        "requested_forbidden_flags": forbidden,
        "authorizes_nothing": True,
        "reason": reason,
    }


# The source-idea claim set: the nine features described in the external AI
# trading bot / video walkthrough. Used as the default intake when no claim
# list is supplied.
DEFAULT_SOURCE_IDEA_CLAIMS: tuple[str, ...] = (
    "Support/resistance chart analysis",
    "Pine Script generation and debugging",
    "TradingView webhooks",
    "Telegram command assistant",
    "Portfolio dashboard",
    "Funding-rate scanner",
    "Hyperliquid whale tracking",
    "Daily alpha brief",
    "Cloud bot operation",
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 external bot evidence intake contract template and is "
    "execution-free.",
    "It classifies external AI trading bot / video / tool claims into "
    "observation-only research-evidence buckets; it runs nothing and touches "
    "no external bot.",
    "Every execution-capable idea is classified blocked_execution_feature and "
    "is never authorized.",
    "Every attractive but unverified claim is classified "
    "risky_requires_validation and never treated as 'free money'.",
    "Hyperliquid whale tracking stays external evidence only -- never "
    "execution permission.",
    "Telegram stays a read-only command/status interface only; no trade "
    "commands.",
    "TradingView webhooks stay future signal-ingestion / logging only; no "
    "execution webhook.",
    "Daily alpha brief and portfolio dashboard stay read-only summary / "
    "display candidates only; no account control.",
    "Pine Script generation / debugging stays a research artifact only; no "
    "live strategy deployment.",
    "Cloud bot operation stays blocked unless it is only offline / read-only "
    "research packaging.",
    "Classifying external evidence never converts it into permission for QA, "
    "backtest, paper, live, broker/exchange, automation, or promotion.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured evidence classifications before "
    "any further research-only contract is built.",
    "A human reviewer must confirm every blocked_execution_feature stays "
    "blocked and is never wired to a broker, exchange, order, Telegram trade "
    "command, TradingView execution webhook, or account control.",
    "A human reviewer must confirm every risky_requires_validation claim is "
    "independently validated before it is trusted as evidence.",
    "A human reviewer must confirm the next step is only to BUILD the next "
    "research-only evidence contract (Hyperliquid whale evidence), still on "
    "paper.",
    "No execution, data acquisition, QA, backtest, paper/live, broker/"
    "exchange, automation, promotion, or downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "external_bot_evidence_intake_next_required_action",
    "external_bot_evidence_intake_current_stage",
    "evidence_classification_buckets",
    "canonical_feature_classifications",
    "execution_capability_markers",
    "marketing_claim_markers",
    "dashboard_or_brief_markers",
    "research_artifact_markers",
    "forbidden_allow_flags",
    "remaining_real_world_capabilities_blocked",
    "submitted_claims",
    "classified_claims",
    "classification_counts",
    "blocked_execution_feature_count",
    "safety_posture",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE)


def build_crypto_d1_external_bot_evidence_intake_contract(
    claims: Any = None,
) -> dict[str, Any]:
    """Build the read-only external-bot-evidence-intake contract. Pure; no I/O,
    no mutation of inputs, no timestamp, no random id. When no claims are given,
    the nine source-idea features are classified. A fresh dict (with fresh
    lists) is returned every call for mutation isolation."""
    if claims is None:
        source = list(DEFAULT_SOURCE_IDEA_CLAIMS)
    elif isinstance(claims, (list, tuple)):
        source = list(claims)
    else:
        source = [claims]

    classified = [classify_external_bot_evidence_claim(c) for c in source]

    counts: dict[str, int] = {b: 0 for b in EVIDENCE_CLASSIFICATION_BUCKETS}
    for item in classified:
        bucket = item.get("bucket")
        if bucket in counts:
            counts[bucket] += 1

    submitted = [_as_text(item.get("claim")) for item in classified]

    contract: dict[str, Any] = {
        "schema_version": EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION,
        "label": DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL,
        "status": EXTERNAL_BOT_EVIDENCE_INTAKE_STATUS,
        "stage": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_"
            "CONTRACT_ONLY"
        ),
        "mode": EXTERNAL_BOT_EVIDENCE_INTAKE_MODE,
        "external_bot_evidence_intake_next_required_action": (
            EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION
        ),
        "external_bot_evidence_intake_current_stage": (
            EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE
        ),
        "evidence_classification_buckets": EVIDENCE_CLASSIFICATION_BUCKETS,
        "canonical_feature_classifications": {
            k: dict(v) for k, v in CANONICAL_FEATURE_CLASSIFICATIONS.items()
        },
        "execution_capability_markers": EXECUTION_CAPABILITY_MARKERS,
        "marketing_claim_markers": MARKETING_CLAIM_MARKERS,
        "dashboard_or_brief_markers": DASHBOARD_OR_BRIEF_MARKERS,
        "research_artifact_markers": RESEARCH_ARTIFACT_MARKERS,
        "forbidden_allow_flags": (
            EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
        ),
        "remaining_real_world_capabilities_blocked": (
            REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "submitted_claims": submitted,
        "classified_claims": [dict(item) for item in classified],
        "classification_counts": counts,
        "blocked_execution_feature_count": counts[
            BUCKET_BLOCKED_EXECUTION_FEATURE
        ],
        "safety_posture": _safety_posture(),
        "operator_notes": list(_OPERATOR_NOTES),
        "human_operator_required_next_steps": list(
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "authorizes_real_world_action": False,
        "unlocks_downstream_gate": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == (
            "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_"
            "CONTRACT_ONLY"
        )
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    authorizes_false = safe.get("authorizes_real_world_action") is False
    unlocks_false = safe.get("unlocks_downstream_gate") is False
    gates_locked = (
        safe.get("real_data_qa_blocked") is True
        and safe.get("baseline_backtest_blocked") is True
        and safe.get("paper_trading_gate_locked") is True
        and safe.get("micro_live_gate_locked") is True
    )

    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    buckets_ok = (
        tuple(safe.get("evidence_classification_buckets") or ())
        == EVIDENCE_CLASSIFICATION_BUCKETS
    )
    forbidden_ok = (
        tuple(safe.get("forbidden_allow_flags") or ())
        == EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
    )
    remaining_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )

    classified = safe.get("classified_claims")
    classified_ok = isinstance(classified, list) and all(
        isinstance(item, dict)
        and item.get("bucket") in _BUCKET_SET
        and item.get("authorizes_nothing") is True
        for item in classified
    )
    # Every execution-capable classified claim must sit in the blocked bucket.
    execution_safe = isinstance(classified, list) and all(
        (item.get("bucket") == BUCKET_BLOCKED_EXECUTION_FEATURE)
        for item in classified
        if isinstance(item, dict) and item.get("execution_capable") is True
    )

    counts = safe.get("classification_counts")
    counts_ok = isinstance(counts, dict) and set(counts.keys()) == _BUCKET_SET

    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    valid = (
        not missing
        and schema_ok
        and read_only
        and research_only
        and stage_ok
        and human_required
        and executes_false
        and authorizes_false
        and unlocks_false
        and gates_locked
        and safety_all_false
        and buckets_ok
        and forbidden_ok
        and remaining_ok
        and classified_ok
        and execution_safe
        and counts_ok
        and notes_ok
        and next_steps_ok
    )

    return {
        "valid": bool(valid),
        "missing_fields": missing,
        "schema_ok": schema_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "human_required": human_required,
        "executes_false": executes_false,
        "authorizes_false": authorizes_false,
        "unlocks_false": unlocks_false,
        "gates_locked": gates_locked,
        "safety_all_false": safety_all_false,
        "buckets_ok": buckets_ok,
        "forbidden_ok": forbidden_ok,
        "remaining_ok": remaining_ok,
        "classified_ok": classified_ok,
        "execution_safe": execution_safe,
        "counts_ok": counts_ok,
        "notes_ok": notes_ok,
        "next_steps_ok": next_steps_ok,
    }


def validate_crypto_d1_external_bot_evidence_intake_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_external_bot_evidence_intake_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 External Bot Evidence Intake Contract")
    lines.append("")
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
    lines.append(
        "- Authorizes real-world action: "
        + str(safe.get("authorizes_real_world_action"))
    )
    lines.append(
        "- real_data_qa blocked: " + str(safe.get("real_data_qa_blocked"))
    )
    lines.append(
        "- baseline_backtest blocked: "
        + str(safe.get("baseline_backtest_blocked"))
    )
    lines.append(
        "- paper_trading_gate locked: "
        + str(safe.get("paper_trading_gate_locked"))
    )
    lines.append(
        "- micro_live_gate locked: "
        + str(safe.get("micro_live_gate_locked"))
    )
    lines.append("")
    lines.append("## Classified Claims")
    for item in safe.get("classified_claims") or ():
        if not isinstance(item, dict):
            continue
        lines.append(
            "- "
            + _as_text(item.get("claim"))
            + " -> "
            + _as_text(item.get("bucket"))
            + " ("
            + _as_text(item.get("reason"))
            + ")"
        )
    lines.append("")
    lines.append("## Classification Counts")
    counts = safe.get("classification_counts")
    if isinstance(counts, dict):
        for bucket in EVIDENCE_CLASSIFICATION_BUCKETS:
            lines.append("- " + bucket + ": " + str(counts.get(bucket, 0)))
    return "\n".join(lines)
