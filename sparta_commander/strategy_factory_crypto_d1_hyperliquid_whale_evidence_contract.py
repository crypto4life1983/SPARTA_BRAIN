"""SPARTA Offline Strategy Factory - CRYPTO-D1 HYPERLIQUID WHALE EVIDENCE
CONTRACT.

A PURE, stdlib-only *read-only paper contract* that interprets Hyperliquid
whale-tracking *ideas / claims / signals* as external research evidence ONLY. It
takes a list of free-text whale-tracking claim descriptions (e.g. "Hyperliquid
whale tracking", "copy profitable whale wallets", "large whale movement alert")
and returns a deterministic classification of each into one of five
observation-only evidence buckets:

  - useful_for_research            (a legitimate research observation; still
                                    requires independent validation)
  - risky_requires_validation      (unverified whale-movement claim; never
                                    trusted until independently confirmed)
  - blocked_execution_feature      (execution-capable / live-access; blocked,
                                    never authorized)
  - ignore_or_marketing_claim      ("smart money certainty" / "guaranteed whale
                                    signal" hype noise)
  - needs_independent_confirmation (a confirmed-but-non-actionable observation
                                    that must be independently re-confirmed
                                    before any later research protocol uses it)

This contract authorizes NOTHING real. It does NOT connect to the Hyperliquid
API, monitor any wallet, access any account or portfolio, connect to any
exchange, place any order, run any live whale-alert automation, run any "copy
whale" / "follow whale" execution logic, acquire/fetch/inspect/load any market
or on-chain data, run any QA, baseline, backtest, or simulation, produce any
trade signal, reach any broker / exchange / order / account / API surface, trade
any paper and any live, promote any strategy, unlock any downstream gate,
trigger any automation, write any runtime / registry / ledger / dashboard /
report state, open any network, spawn any child process, write any file, read
any file, list any directory, record any timestamp, mint any random id, read any
environment, or dynamically import anything.

Hard classification stances (every one preserves SPARTA safety gates):
  - Hyperliquid whale tracking is external evidence only -- never execution
    permission.
  - Whale evidence cannot unlock real_data_qa, baseline_backtest, paper trading,
    live trading, broker/exchange, automation, or promotion.
  - Whale evidence must require independent confirmation before it can be used
    in any later research protocol.
  - Large position / whale-movement claims are risky_requires_validation unless
    independently confirmed.
  - "Smart money certainty" / "guaranteed whale signal" claims are
    ignore_or_marketing_claim; "copy profitable wallets" and any execution
    language are blocked_execution_feature.
  - Any Hyperliquid API connection, wallet monitoring, account/portfolio access,
    exchange connection, order placement, live whale-alert automation, or
    copy/follow-whale execution logic is a blocked execution feature.

Converting whale evidence into structured SPARTA evidence NEVER converts it into
permission for QA, backtest, paper, live, broker/exchange, automation, or
promotion. Every execution-capable whale idea is marked
blocked_execution_feature and every unverified whale-movement claim is marked
risky_requires_validation.

Public API:
  - WHALE_EVIDENCE_SCHEMA_VERSION
  - DEFAULT_WHALE_EVIDENCE_LABEL
  - WHALE_EVIDENCE_STATUS
  - WHALE_EVIDENCE_MODE
  - WHALE_EVIDENCE_SAFETY_POSTURE
  - WHALE_EVIDENCE_CLASSIFICATION_BUCKETS
  - BUCKET_USEFUL_FOR_RESEARCH
  - BUCKET_RISKY_REQUIRES_VALIDATION
  - BUCKET_BLOCKED_EXECUTION_FEATURE
  - BUCKET_IGNORE_OR_MARKETING_CLAIM
  - BUCKET_NEEDS_INDEPENDENT_CONFIRMATION
  - WHALE_CANONICAL_FEATURE_CLASSIFICATIONS
  - WHALE_EXECUTION_CAPABILITY_MARKERS
  - WHALE_MARKETING_CLAIM_MARKERS
  - WHALE_INDEPENDENT_CONFIRMATION_MARKERS
  - WHALE_RESEARCH_ARTIFACT_MARKERS
  - WHALE_EVIDENCE_NEXT_REQUIRED_ACTION
  - WHALE_EVIDENCE_CURRENT_STAGE
  - WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
  - WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - classify_whale_evidence_claim(claim)
  - build_crypto_d1_hyperliquid_whale_evidence_contract(claims=None)
  - validate_crypto_d1_hyperliquid_whale_evidence_contract(contract)
  - render_crypto_d1_hyperliquid_whale_evidence_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "WHALE_EVIDENCE_SCHEMA_VERSION",
    "DEFAULT_WHALE_EVIDENCE_LABEL",
    "WHALE_EVIDENCE_STATUS",
    "WHALE_EVIDENCE_MODE",
    "WHALE_EVIDENCE_SAFETY_POSTURE",
    "WHALE_EVIDENCE_CLASSIFICATION_BUCKETS",
    "BUCKET_USEFUL_FOR_RESEARCH",
    "BUCKET_RISKY_REQUIRES_VALIDATION",
    "BUCKET_BLOCKED_EXECUTION_FEATURE",
    "BUCKET_IGNORE_OR_MARKETING_CLAIM",
    "BUCKET_NEEDS_INDEPENDENT_CONFIRMATION",
    "WHALE_CANONICAL_FEATURE_CLASSIFICATIONS",
    "WHALE_EXECUTION_CAPABILITY_MARKERS",
    "WHALE_MARKETING_CLAIM_MARKERS",
    "WHALE_INDEPENDENT_CONFIRMATION_MARKERS",
    "WHALE_RESEARCH_ARTIFACT_MARKERS",
    "WHALE_EVIDENCE_NEXT_REQUIRED_ACTION",
    "WHALE_EVIDENCE_CURRENT_STAGE",
    "WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS",
    "WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "classify_whale_evidence_claim",
    "build_crypto_d1_hyperliquid_whale_evidence_contract",
    "validate_crypto_d1_hyperliquid_whale_evidence_contract",
    "render_crypto_d1_hyperliquid_whale_evidence_contract_markdown",
]

WHALE_EVIDENCE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract.v1"
)
DEFAULT_WHALE_EVIDENCE_LABEL = (
    "Strategy Factory Crypto-D1 Hyperliquid Whale Evidence Contract"
)
WHALE_EVIDENCE_STATUS = (
    "READ_ONLY_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
)
WHALE_EVIDENCE_MODE = "RESEARCH_ONLY"

# The five observation-only evidence buckets. Order is stable and is the
# canonical enumeration the contract and its validator compare against.
BUCKET_USEFUL_FOR_RESEARCH = "useful_for_research"
BUCKET_RISKY_REQUIRES_VALIDATION = "risky_requires_validation"
BUCKET_BLOCKED_EXECUTION_FEATURE = "blocked_execution_feature"
BUCKET_IGNORE_OR_MARKETING_CLAIM = "ignore_or_marketing_claim"
BUCKET_NEEDS_INDEPENDENT_CONFIRMATION = "needs_independent_confirmation"

WHALE_EVIDENCE_CLASSIFICATION_BUCKETS: tuple[str, ...] = (
    BUCKET_USEFUL_FOR_RESEARCH,
    BUCKET_RISKY_REQUIRES_VALIDATION,
    BUCKET_BLOCKED_EXECUTION_FEATURE,
    BUCKET_IGNORE_OR_MARKETING_CLAIM,
    BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
)
_BUCKET_SET: frozenset[str] = frozenset(WHALE_EVIDENCE_CLASSIFICATION_BUCKETS)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is a separate, later block; importing the registry would also
# risk a circular import).
WHALE_EVIDENCE_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
)
WHALE_EVIDENCE_CURRENT_STAGE = (
    "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_REQUIRED"
)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract classifies whale-tracking claims on paper and unlocks nothing.
WHALE_EVIDENCE_SAFETY_POSTURE: dict[str, bool] = {
    "connects_hyperliquid_api": False,
    "monitors_wallet": False,
    "accesses_account_or_portfolio": False,
    "connects_exchange": False,
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
    "uses_api_keys": False,
    "copies_or_follows_whale": False,
    "runs_whale_alert_automation": False,
    "sends_telegram_trade_command": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
    "promotes_strategy": False,
    "unlocks_downstream_gate": False,
}

# Capability flags a caller-supplied claim record must NOT request. Any truthy
# value forces the claim's classification to blocked_execution_feature and is
# recorded as a forbidden-flag reason. These are descriptive paper guards, not
# runtime switches.
WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_execution",
    "executes",
    "allow_hyperliquid_api",
    "connects_hyperliquid_api",
    "allow_wallet_monitoring",
    "monitors_wallet",
    "allow_account_access",
    "accesses_account_or_portfolio",
    "allow_exchange_connection",
    "connects_exchange",
    "allow_order_placement",
    "places_order",
    "allow_copy_whale",
    "copies_or_follows_whale",
    "allow_whale_alert_automation",
    "runs_whale_alert_automation",
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
    WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
)

# Real-world capabilities that remain blocked regardless of classification.
WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "hyperliquid_api_connection",
    "wallet_monitoring",
    "account_or_portfolio_access",
    "exchange_connection",
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
    "api_key_use",
    "copy_or_follow_whale_execution",
    "whale_alert_automation",
    "telegram_trade_command",
    "paper_or_live_trading",
    "strategy_promotion",
    "automation_trigger",
    "downstream_gate_unlock",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
)

# Substrings that mark an execution-capable / live-access whale idea. Presence of
# ANY (after the canonical-feature lookup) forces blocked_execution_feature --
# safety wins over every other bucket.
WHALE_EXECUTION_CAPABILITY_MARKERS: tuple[str, ...] = (
    "execute",
    "execution",
    "place order",
    "place_order",
    "order placement",
    "auto-trade",
    "auto trade",
    "autotrade",
    "live trade",
    "live trading",
    "send order",
    "submit order",
    "broker api",
    "exchange api",
    "order webhook",
    "execution webhook",
    "trade command",
    "withdraw",
    "deposit funds",
    "copy whale",
    "copy-whale",
    "copy wallet",
    "copy profitable",
    "copy trade",
    "copy-trade",
    "follow whale",
    "mirror whale",
    "wallet monitoring",
    "monitor wallet",
    "wallet monitor",
    "live monitor",
    "hyperliquid api",
    "whale api",
    "connect to hyperliquid",
    "connect hyperliquid",
    "whale alert automation",
    "alert automation",
    "auto whale",
    "auto-alert",
    "exchange connection",
    "connect exchange",
    "account access",
    "portfolio access",
    "account control",
)

# Substrings that mark hype / "smart money certainty" / guaranteed-profit noise.
WHALE_MARKETING_CLAIM_MARKERS: tuple[str, ...] = (
    "smart money certainty",
    "smart money guaranteed",
    "guaranteed whale",
    "guaranteed signal",
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
    "never lose",
    "instant profit",
    "easy money",
    "sure thing",
    "certain profit",
)

# Substrings that mark a confirmed-but-non-actionable whale observation that must
# be independently re-confirmed before any later research protocol uses it.
WHALE_INDEPENDENT_CONFIRMATION_MARKERS: tuple[str, ...] = (
    "whale position",
    "position observation",
    "observed position",
    "position snapshot",
    "wallet holdings",
    "whale holdings",
    "confirmed observation",
    "holdings snapshot",
)

# Substrings that mark a legitimate offline research artifact (still needs
# independent validation).
WHALE_RESEARCH_ARTIFACT_MARKERS: tuple[str, ...] = (
    "offline historical",
    "historical whale",
    "historical study",
    "offline research",
    "research artifact",
    "whale evidence study",
    "evidence study",
    "pattern study",
    "offline study",
)

# Canonical, explicit per-feature classifications. Keys are normalized feature
# ids; each record names the bucket, the human reason, and whether the feature
# is execution-capable. The build/classify path checks these FIRST so the named
# whale stances are honored verbatim.
WHALE_CANONICAL_FEATURE_CLASSIFICATIONS: dict[str, dict[str, Any]] = {
    "hyperliquid_whale_tracking": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "Hyperliquid whale tracking is external evidence only and never "
            "execution permission; it still requires independent validation."
        ),
    },
    "whale_position_observation": {
        "bucket": BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
        "execution_capable": False,
        "reason": (
            "A confirmed-but-non-actionable whale observation must be "
            "independently re-confirmed before any later research protocol "
            "uses it."
        ),
    },
    "large_whale_movement_claim": {
        "bucket": BUCKET_RISKY_REQUIRES_VALIDATION,
        "execution_capable": False,
        "reason": (
            "A large position / whale-movement claim is risky_requires_"
            "validation unless independently confirmed; never trusted as-is."
        ),
    },
    "whale_evidence_offline_study": {
        "bucket": BUCKET_USEFUL_FOR_RESEARCH,
        "execution_capable": False,
        "reason": (
            "An offline / historical whale evidence study is a research "
            "artifact only and requires independent validation."
        ),
    },
    "wallet_monitoring": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Live wallet monitoring is a real-world access capability and "
            "stays blocked."
        ),
    },
    "hyperliquid_api_connection": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "A Hyperliquid API connection is a real-world access capability "
            "and stays blocked."
        ),
    },
    "copy_whale_execution": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "'Copy whale' / 'follow whale' execution logic is an execution "
            "feature and stays blocked."
        ),
    },
    "copy_profitable_wallets": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "'Copy profitable wallets' carries execution language and stays "
            "blocked as an execution feature."
        ),
    },
    "whale_alert_automation": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Live whale-alert automation is an automation/execution feature "
            "and stays blocked."
        ),
    },
    "account_portfolio_access": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "Account / portfolio access is a real-world access capability and "
            "stays blocked."
        ),
    },
    "exchange_connection": {
        "bucket": BUCKET_BLOCKED_EXECUTION_FEATURE,
        "execution_capable": True,
        "reason": (
            "An exchange connection is a real-world access capability and "
            "stays blocked."
        ),
    },
    "smart_money_certainty_claim": {
        "bucket": BUCKET_IGNORE_OR_MARKETING_CLAIM,
        "execution_capable": False,
        "reason": (
            "'Smart money certainty' is marketing hype and is ignored as "
            "evidence."
        ),
    },
    "guaranteed_whale_signal": {
        "bucket": BUCKET_IGNORE_OR_MARKETING_CLAIM,
        "execution_capable": False,
        "reason": (
            "A 'guaranteed whale signal' is marketing hype and is ignored as "
            "evidence."
        ),
    },
}

# Aliases mapping a normalized free-text claim to a canonical feature id. Each
# alias is matched as a substring of the normalized claim (most-specific-first).
_FEATURE_ALIASES: tuple[tuple[str, str], ...] = (
    ("hyperliquid api", "hyperliquid_api_connection"),
    ("whale api", "hyperliquid_api_connection"),
    ("connect to hyperliquid", "hyperliquid_api_connection"),
    ("connect hyperliquid", "hyperliquid_api_connection"),
    ("wallet monitoring", "wallet_monitoring"),
    ("monitor wallet", "wallet_monitoring"),
    ("wallet monitor", "wallet_monitoring"),
    ("copy profitable wallet", "copy_profitable_wallets"),
    ("copy profitable", "copy_profitable_wallets"),
    ("copy whale", "copy_whale_execution"),
    ("follow whale", "copy_whale_execution"),
    ("mirror whale", "copy_whale_execution"),
    ("whale alert automation", "whale_alert_automation"),
    ("alert automation", "whale_alert_automation"),
    ("auto whale", "whale_alert_automation"),
    ("smart money certainty", "smart_money_certainty_claim"),
    ("smart money guaranteed", "smart_money_certainty_claim"),
    ("smart money", "smart_money_certainty_claim"),
    ("guaranteed whale signal", "guaranteed_whale_signal"),
    ("guaranteed whale", "guaranteed_whale_signal"),
    ("whale position observation", "whale_position_observation"),
    ("whale position", "whale_position_observation"),
    ("position observation", "whale_position_observation"),
    ("whale holdings", "whale_position_observation"),
    ("large whale movement", "large_whale_movement_claim"),
    ("whale movement", "large_whale_movement_claim"),
    ("large position", "large_whale_movement_claim"),
    ("offline historical whale", "whale_evidence_offline_study"),
    ("historical whale", "whale_evidence_offline_study"),
    ("offline research packaging", "whale_evidence_offline_study"),
    ("whale evidence study", "whale_evidence_offline_study"),
    ("account access", "account_portfolio_access"),
    ("portfolio access", "account_portfolio_access"),
    ("account control", "account_portfolio_access"),
    ("exchange connection", "exchange_connection"),
    ("connect exchange", "exchange_connection"),
    ("hyperliquid whale", "hyperliquid_whale_tracking"),
    ("whale tracking", "hyperliquid_whale_tracking"),
    ("whale tracker", "hyperliquid_whale_tracking"),
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
        for f in WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
        if f in flags and _truthy(flags.get(f))
    )


def _match_canonical_feature(normalized: str) -> str | None:
    """Return the canonical feature id for a normalized claim, or None."""
    if not normalized:
        return None
    # Direct id match first (e.g. a caller passing the exact feature id).
    if normalized in WHALE_CANONICAL_FEATURE_CLASSIFICATIONS:
        return normalized
    underscored = normalized.replace(" ", "_").replace("-", "_")
    if underscored in WHALE_CANONICAL_FEATURE_CLASSIFICATIONS:
        return underscored
    # Alias substring match (order is most-specific-first).
    for alias, feature_id in _FEATURE_ALIASES:
        if alias in normalized:
            return feature_id
    return None


def _heuristic_bucket(normalized: str) -> tuple[str, str]:
    """Classify a free-text whale claim with no canonical match. Execution
    markers win first (safety), then marketing, then research artifact, then
    independent-confirmation, then the conservative risky default."""
    if any(m in normalized for m in WHALE_EXECUTION_CAPABILITY_MARKERS):
        return (
            BUCKET_BLOCKED_EXECUTION_FEATURE,
            "Execution-capable / live-access whale claim; blocked and never "
            "authorized.",
        )
    if any(m in normalized for m in WHALE_MARKETING_CLAIM_MARKERS):
        return (
            BUCKET_IGNORE_OR_MARKETING_CLAIM,
            "Marketing / 'smart money certainty' hype; ignored as evidence.",
        )
    if any(m in normalized for m in WHALE_RESEARCH_ARTIFACT_MARKERS):
        return (
            BUCKET_USEFUL_FOR_RESEARCH,
            "Offline whale research artifact; useful for research, requires "
            "validation.",
        )
    if any(m in normalized for m in WHALE_INDEPENDENT_CONFIRMATION_MARKERS):
        return (
            BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
            "Whale observation; needs independent confirmation before any "
            "later research protocol uses it.",
        )
    return (
        BUCKET_RISKY_REQUIRES_VALIDATION,
        "Unverified whale-movement claim; requires independent validation.",
    )


def classify_whale_evidence_claim(claim: Any) -> dict[str, Any]:
    """Return a deterministic classification for one Hyperliquid whale-tracking
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
        spec = WHALE_CANONICAL_FEATURE_CLASSIFICATIONS[feature_id]
        bucket = spec["bucket"]
        reason = spec["reason"]
        execution_capable = bool(spec["execution_capable"])
    else:
        bucket, reason = _heuristic_bucket(normalized)
        execution_capable = bucket == BUCKET_BLOCKED_EXECUTION_FEATURE

    # Safety override: any requested forbidden flag, or any execution marker in
    # the text, forces the blocked bucket regardless of the canonical/heuristic
    # result -- whale evidence never lets an execution-capable idea pass.
    if forbidden or any(
        m in normalized for m in WHALE_EXECUTION_CAPABILITY_MARKERS
    ):
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


# The source-idea whale claim set: the named whale-tracking stances from the
# Bundle 61 evidence chain. Used as the default intake when no claim list is
# supplied.
DEFAULT_SOURCE_IDEA_CLAIMS: tuple[str, ...] = (
    "Hyperliquid whale tracking",
    "Whale position observation",
    "Large whale movement alert",
    "Copy profitable whale wallets",
    "Guaranteed whale signal",
    "Hyperliquid API wallet monitoring",
    "Smart money certainty",
    "Offline historical whale evidence study",
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 Hyperliquid whale evidence contract template and is "
    "execution-free.",
    "It classifies Hyperliquid whale-tracking claims into observation-only "
    "research-evidence buckets; it runs nothing and connects nowhere.",
    "Hyperliquid whale tracking stays external evidence only -- never "
    "execution permission.",
    "No Hyperliquid API connection, wallet monitoring, account/portfolio "
    "access, exchange connection, or order placement is performed.",
    "No 'copy whale' / 'follow whale' execution logic and no live whale-alert "
    "automation is performed.",
    "Every execution-capable whale idea is classified "
    "blocked_execution_feature and is never authorized.",
    "Every unverified whale-movement claim is classified "
    "risky_requires_validation and never trusted as-is.",
    "'Smart money certainty' / 'guaranteed whale signal' claims are "
    "ignore_or_marketing_claim.",
    "Confirmed-but-non-actionable whale observations are "
    "needs_independent_confirmation and must be independently re-confirmed.",
    "Whale evidence cannot unlock real_data_qa, baseline_backtest, paper "
    "trading, live trading, broker/exchange, automation, or promotion.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured whale-evidence classifications "
    "before any further research-only contract is built.",
    "A human reviewer must confirm every blocked_execution_feature stays "
    "blocked and is never wired to the Hyperliquid API, a wallet monitor, an "
    "account, an exchange, an order, or copy/follow-whale logic.",
    "A human reviewer must independently confirm every "
    "needs_independent_confirmation and risky_requires_validation whale claim "
    "before it is trusted as evidence.",
    "A human reviewer must confirm the next step is only to BUILD the next "
    "research-only evidence contract (Funding Rate evidence), still on paper.",
    "No execution, Hyperliquid API access, wallet monitoring, data "
    "acquisition, QA, backtest, paper/live, broker/exchange, automation, "
    "promotion, or downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "whale_evidence_next_required_action",
    "whale_evidence_current_stage",
    "evidence_classification_buckets",
    "canonical_feature_classifications",
    "execution_capability_markers",
    "marketing_claim_markers",
    "independent_confirmation_markers",
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
    "requires_independent_confirmation",
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
    return dict(WHALE_EVIDENCE_SAFETY_POSTURE)


def build_crypto_d1_hyperliquid_whale_evidence_contract(
    claims: Any = None,
) -> dict[str, Any]:
    """Build the read-only Hyperliquid-whale-evidence contract. Pure; no I/O,
    no mutation of inputs, no timestamp, no random id. When no claims are given,
    the named source-idea whale features are classified. A fresh dict (with
    fresh lists) is returned every call for mutation isolation."""
    if claims is None:
        source = list(DEFAULT_SOURCE_IDEA_CLAIMS)
    elif isinstance(claims, (list, tuple)):
        source = list(claims)
    else:
        source = [claims]

    classified = [classify_whale_evidence_claim(c) for c in source]

    counts: dict[str, int] = {b: 0 for b in WHALE_EVIDENCE_CLASSIFICATION_BUCKETS}
    for item in classified:
        bucket = item.get("bucket")
        if bucket in counts:
            counts[bucket] += 1

    submitted = [_as_text(item.get("claim")) for item in classified]

    contract: dict[str, Any] = {
        "schema_version": WHALE_EVIDENCE_SCHEMA_VERSION,
        "label": DEFAULT_WHALE_EVIDENCE_LABEL,
        "status": WHALE_EVIDENCE_STATUS,
        "stage": "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_ONLY",
        "mode": WHALE_EVIDENCE_MODE,
        "whale_evidence_next_required_action": (
            WHALE_EVIDENCE_NEXT_REQUIRED_ACTION
        ),
        "whale_evidence_current_stage": WHALE_EVIDENCE_CURRENT_STAGE,
        "evidence_classification_buckets": WHALE_EVIDENCE_CLASSIFICATION_BUCKETS,
        "canonical_feature_classifications": {
            k: dict(v)
            for k, v in WHALE_CANONICAL_FEATURE_CLASSIFICATIONS.items()
        },
        "execution_capability_markers": WHALE_EXECUTION_CAPABILITY_MARKERS,
        "marketing_claim_markers": WHALE_MARKETING_CLAIM_MARKERS,
        "independent_confirmation_markers": (
            WHALE_INDEPENDENT_CONFIRMATION_MARKERS
        ),
        "research_artifact_markers": WHALE_RESEARCH_ARTIFACT_MARKERS,
        "forbidden_allow_flags": WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS,
        "remaining_real_world_capabilities_blocked": (
            WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
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
        "requires_independent_confirmation": True,
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
        safe.get("schema_version") == WHALE_EVIDENCE_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_ONLY"
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    authorizes_false = safe.get("authorizes_real_world_action") is False
    unlocks_false = safe.get("unlocks_downstream_gate") is False
    confirmation_required = (
        safe.get("requires_independent_confirmation") is True
    )
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
        == WHALE_EVIDENCE_CLASSIFICATION_BUCKETS
    )
    forbidden_ok = (
        tuple(safe.get("forbidden_allow_flags") or ())
        == WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
    )
    remaining_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
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
        and confirmation_required
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
        "confirmation_required": confirmation_required,
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


def validate_crypto_d1_hyperliquid_whale_evidence_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_hyperliquid_whale_evidence_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Hyperliquid Whale Evidence Contract")
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
        "- Requires independent confirmation: "
        + str(safe.get("requires_independent_confirmation"))
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
        for bucket in WHALE_EVIDENCE_CLASSIFICATION_BUCKETS:
            lines.append("- " + bucket + ": " + str(counts.get(bucket, 0)))
    return "\n".join(lines)
