"""SPARTA Offline Strategy Factory - CRYPTO-D1 COHORT INDEPENDENCE / CORRELATION.

A PURE, stdlib-only *read-only paper contract* that decides, for a small,
caller-provided set of static trading-evidence and external-evidence records,
whether the records are INDEPENDENT, CORRELATED, DUPLICATE, observation-only, or
too small a sample to judge. It groups correlated records into cohorts and
returns a deterministic, structured result: one independence label per cohort,
the penalty reasons, the independence score, and aggregate counts -- so a human
can decide, on paper, whether a strategy candidate has truly independent proof
or merely one correlated move counted many times.

CORE RULE: one correlated move is ONE event, not many independent wins. Trades
that share a macro event, a market regime, a timing window, a signal family, or
the same symbol and trade direction collapse into a single cohort and a single
penalised event. Open / unrealized positions are observation-only and create no
independent cohort. External-research evidence (other bots, whale tracking,
funding rates, BTC cycle timing, the daily alpha brief) creates no independent
trade cohort. Only closed / booked trades can supply positive independent proof,
and at least three TRULY INDEPENDENT positive booked cohorts are required before
downstream scoring may even consider a research review. This contract can ONLY
support a research review; it unlocks no QA, no baseline, no backtest, no
paper/live, no broker/exchange, no automation, and no promotion beyond review.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / account / API surface, trade any paper and any live, promote
any strategy beyond a research review, unlock any downstream gate (real_data_qa,
baseline_backtest, paper_trading_gate, micro_live_gate stay blocked / locked),
trigger any automation, write any runtime / registry / ledger / dashboard /
report state, spawn any child process, read any environment, record any
wall-clock time, mint any random id, or dynamically import anything. It ONLY
inspects the static records the caller passes in, using pure dict / string /
number arithmetic.

Independence labels (one per cohort):
  - INDEPENDENT            -> a single booked positive cohort that shares no
                             correlation signal with any other booked cohort,
                             AND at least three such cohorts exist overall.
  - CORRELATED             -> two or more booked records linked by a shared
                             macro event, market regime, timing window, or
                             signal family: one event, not many wins.
  - DUPLICATE              -> two or more booked records repeating the same
                             symbol and the same trade direction with no shared
                             macro event: duplicated exposure, not new proof.
  - OPEN_OBSERVATION_ONLY  -> an open / unrealized position: observation only,
                             zero independent proof weight.
  - EXTERNAL_EVIDENCE_ONLY -> external-research evidence: never trade proof.
  - INSUFFICIENT_SAMPLE    -> a lone booked cohort (positive but too small a
                             sample to be independent, or with no positive edge).

Public API:
  - COHORT_INDEPENDENCE_SCHEMA_VERSION
  - COHORT_INDEPENDENCE_LABEL
  - COHORT_INDEPENDENCE_STATUS
  - COHORT_INDEPENDENCE_MODE
  - COHORT_INDEPENDENCE_CORE_RULE
  - COHORT_INDEPENDENCE_SAFETY_POSTURE
  - COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
  - COHORT_INDEPENDENCE_LABELS
  - LABEL_INDEPENDENT / LABEL_CORRELATED / LABEL_DUPLICATE /
    LABEL_OPEN_OBSERVATION_ONLY / LABEL_EXTERNAL_EVIDENCE_ONLY /
    LABEL_INSUFFICIENT_SAMPLE
  - COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT
  - COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS
  - COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS
  - COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS
  - COHORT_INDEPENDENCE_OPEN_STATUS_TAGS
  - COHORT_INDEPENDENCE_CORRELATION_SIGNALS
  - COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS
  - COHORT_INDEPENDENCE_GATE_LOCK_FLAGS
  - COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS
  - COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS
  - COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS
  - COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION
  - COHORT_INDEPENDENCE_CURRENT_STAGE
  - DEFAULT_SAMPLE_EVIDENCE
  - assess_cohort_independence(payload)
  - build_crypto_d1_cohort_independence_correlation_penalty_contract(payload=None)
  - validate_crypto_d1_cohort_independence_correlation_penalty_contract(contract)
  - render_crypto_d1_cohort_independence_correlation_penalty_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "COHORT_INDEPENDENCE_SCHEMA_VERSION",
    "COHORT_INDEPENDENCE_LABEL",
    "COHORT_INDEPENDENCE_STATUS",
    "COHORT_INDEPENDENCE_MODE",
    "COHORT_INDEPENDENCE_CORE_RULE",
    "COHORT_INDEPENDENCE_SAFETY_POSTURE",
    "COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES",
    "COHORT_INDEPENDENCE_LABELS",
    "LABEL_INDEPENDENT",
    "LABEL_CORRELATED",
    "LABEL_DUPLICATE",
    "LABEL_OPEN_OBSERVATION_ONLY",
    "LABEL_EXTERNAL_EVIDENCE_ONLY",
    "LABEL_INSUFFICIENT_SAMPLE",
    "COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT",
    "COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS",
    "COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS",
    "COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS",
    "COHORT_INDEPENDENCE_OPEN_STATUS_TAGS",
    "COHORT_INDEPENDENCE_CORRELATION_SIGNALS",
    "COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS",
    "COHORT_INDEPENDENCE_GATE_LOCK_FLAGS",
    "COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS",
    "COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS",
    "COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS",
    "COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS",
    "COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION",
    "COHORT_INDEPENDENCE_CURRENT_STAGE",
    "DEFAULT_SAMPLE_EVIDENCE",
    "assess_cohort_independence",
    "build_crypto_d1_cohort_independence_correlation_penalty_contract",
    "validate_crypto_d1_cohort_independence_correlation_penalty_contract",
    "render_crypto_d1_cohort_independence_correlation_penalty_contract_markdown",
]

COHORT_INDEPENDENCE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract.v1"
)
COHORT_INDEPENDENCE_LABEL = (
    "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
)
COHORT_INDEPENDENCE_STATUS = (
    "READ_ONLY_CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
)
COHORT_INDEPENDENCE_MODE = "RESEARCH_ONLY"

COHORT_INDEPENDENCE_CORE_RULE = (
    "One correlated move is one event, not many independent wins; trades that "
    "share a macro event, market regime, timing window, signal family, or the "
    "same symbol and trade direction collapse into a single penalised cohort, "
    "and only several truly independent positive booked cohorts can support a "
    "research review -- which authorizes nothing."
)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later block; importing the registry would also
# risk a circular import).
COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
)
COHORT_INDEPENDENCE_CURRENT_STAGE = (
    "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT_REQUIRED"
)

# A research review may only be considered once at least this many TRULY
# INDEPENDENT positive booked cohorts exist. One correlated cluster repeated, or
# a single small cohort, is never enough.
COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT = 3

# Evidence lanes that remain observation-only at every outcome. The assessment
# reads about them; it never wires any of them to a fetch, a QA run, a backtest,
# a trade, a broker/exchange, an order, or any automation.
COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief",
    "open_unrealized_pnl",
)

# Independence labels (one assigned per cohort).
LABEL_INDEPENDENT = "INDEPENDENT"
LABEL_CORRELATED = "CORRELATED"
LABEL_DUPLICATE = "DUPLICATE"
LABEL_OPEN_OBSERVATION_ONLY = "OPEN_OBSERVATION_ONLY"
LABEL_EXTERNAL_EVIDENCE_ONLY = "EXTERNAL_EVIDENCE_ONLY"
LABEL_INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"

COHORT_INDEPENDENCE_LABELS: tuple[str, ...] = (
    LABEL_INDEPENDENT,
    LABEL_CORRELATED,
    LABEL_DUPLICATE,
    LABEL_OPEN_OBSERVATION_ONLY,
    LABEL_EXTERNAL_EVIDENCE_ONLY,
    LABEL_INSUFFICIENT_SAMPLE,
)
_LABEL_SET: frozenset[str] = frozenset(COHORT_INDEPENDENCE_LABELS)

# Deterministic independence score per label. Only a truly INDEPENDENT booked
# positive cohort earns full weight; everything correlated, duplicated, open, or
# external earns little or none.
_LABEL_SCORE: dict[str, float] = {
    LABEL_INDEPENDENT: 1.0,
    LABEL_CORRELATED: 0.2,
    LABEL_DUPLICATE: 0.0,
    LABEL_OPEN_OBSERVATION_ONLY: 0.0,
    LABEL_EXTERNAL_EVIDENCE_ONLY: 0.0,
    LABEL_INSUFFICIENT_SAMPLE: 0.1,
}
# A lone booked POSITIVE cohort (promising but too small a sample) scores a touch
# higher than a lone non-positive one, but still well below INDEPENDENT.
_INSUFFICIENT_SAMPLE_POSITIVE_SCORE = 0.5

# Source tags treated as first-party trade evidence (booked or open). An empty /
# missing source defaults to trade evidence.
COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS: tuple[str, ...] = (
    "trade",
    "booked_trade",
    "closed_trade",
    "open_trade",
    "position",
)

# Source tags treated as external research context. These NEVER count as an
# independent trade cohort.
COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS: tuple[str, ...] = (
    "external_bot",
    "hyperliquid_whale",
    "whale",
    "funding_rate",
    "bitcoin_cycle_timing",
    "btc_cycle",
    "daily_alpha_brief",
    "daily_alpha",
)

# Record statuses treated as BOOKED (closed / realized) -> can supply proof.
COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS: tuple[str, ...] = (
    "closed",
    "booked",
    "realized",
    "settled",
)

# Record statuses treated as OPEN (unrealized) -> observation only, no cohort.
COHORT_INDEPENDENCE_OPEN_STATUS_TAGS: tuple[str, ...] = (
    "open",
    "unrealized",
    "live",
    "running",
    "floating",
)

# The correlation signals that collapse booked records into one cohort. Any
# shared signal makes the records one event, not many independent wins.
COHORT_INDEPENDENCE_CORRELATION_SIGNALS: tuple[str, ...] = (
    "same_symbol_and_direction",
    "same_macro_event",
    "same_market_regime",
    "same_open_window_timing",
    "same_close_window_timing",
    "same_signal_family",
)

_TRADE_SOURCE_SET: frozenset[str] = frozenset(
    COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS
)
_EXTERNAL_SOURCE_SET: frozenset[str] = frozenset(
    COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS
)
_BOOKED_STATUS_SET: frozenset[str] = frozenset(
    COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS
)
_OPEN_STATUS_SET: frozenset[str] = frozenset(
    COHORT_INDEPENDENCE_OPEN_STATUS_TAGS
)

# Top-level (or per-record) authorization flags that, if truthy, force a block.
COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the payload tried to unlock a gate -> block.
COHORT_INDEPENDENCE_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a block.
COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the assessment to mean execution / live promotion. Any truthy
# value forces a block: an independence label can only support a research review.
COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
)

# Fields whose presence (non-empty) on a record signals an executable order /
# signal instruction rather than historical evidence -> block.
COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the assessment's own generated guidance must never
# contain as whole words.
COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Read-only safety posture. The three True flags are *posture* facts (this is a
# read-only, research-only contract that requires human approval); every
# capability / authorization / unlock flag is False.
COHORT_INDEPENDENCE_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "executes": False,
    "human_approval_required": True,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}


# A deterministic, illustrative paper sample: three booked ETH records that all
# share one macro move and the same direction. They are PROMISING but
# CORRELATED -- one independent event, not three independent wins. Nothing here
# is real data; static example only.
DEFAULT_SAMPLE_EVIDENCE: dict[str, Any] = {
    "label": "Crypto-D1 cohort independence evidence (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "evidence": [
        {
            "id": "E",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.4,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "E2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 0.9,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "F2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.1,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
    ],
}


def _as_text(value: Any) -> str:
    """Coerce any value to a stripped string; non-str/None -> ''."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _truthy(value: Any) -> bool:
    """Conservative truthiness for caller-supplied flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "on", "allow")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _isolated(value: Any) -> Any:
    """Return an isolated copy so the contract never shares mutable references
    with caller input."""
    if isinstance(value, dict):
        return {k: _isolated(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_isolated(v) for v in value]
    return value


def _word_tokens(text: str) -> set[str]:
    """Lowercased alphabetic whole-word tokens of a string."""
    tokens: set[str] = set()
    word: list[str] = []
    for ch in text.lower():
        if ch.isalpha():
            word.append(ch)
        else:
            if word:
                tokens.add("".join(word))
                word = []
    if word:
        tokens.add("".join(word))
    return tokens


def _non_empty(value: Any) -> bool:
    """True when a caller field is present and carries real content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _as_number(value: Any) -> float:
    """Coerce a caller PnL value to a float; non-numeric -> 0.0. Bools are 0.0."""
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return 0.0
    return 0.0


def _record_id(record: dict[str, Any], index: int) -> str:
    rid = _as_text(record.get("id"))
    return rid if rid else "#" + str(index)


def _record_source(record: dict[str, Any]) -> str:
    """The normalized source tag; empty / unknown source defaults to trade."""
    src = _as_text(record.get("source")).lower()
    if not src:
        src = _as_text(record.get("source_type")).lower()
    if src in _EXTERNAL_SOURCE_SET:
        return src
    return src if src in _TRADE_SOURCE_SET else "trade"


def _record_status(record: dict[str, Any]) -> str:
    status = _as_text(record.get("status")).lower()
    if not status:
        status = _as_text(record.get("pnl_status")).lower()
    return status


def _record_symbol(record: dict[str, Any]) -> str:
    return _as_text(record.get("symbol")).lower()


def _record_direction(record: dict[str, Any]) -> str:
    return _as_text(record.get("direction")).lower()


def _record_macro(record: dict[str, Any]) -> str:
    return _as_text(record.get("macro_event")).lower()


def _record_regime(record: dict[str, Any]) -> str:
    return _as_text(record.get("market_regime")).lower()


def _record_open_window(record: dict[str, Any]) -> str:
    """The trade-open timing key (entry window / entry date)."""
    win = _as_text(record.get("entry_window")).lower()
    if win:
        return win
    return _as_text(record.get("entry_date")).lower()


def _record_close_window(record: dict[str, Any]) -> str:
    """The trade-close timing key (close window / exit date)."""
    win = _as_text(record.get("close_window")).lower()
    if win:
        return win
    return _as_text(record.get("exit_date")).lower()


def _record_signal_family(record: dict[str, Any]) -> str:
    """The signal / setup family key (setup_family, then strategy_label)."""
    fam = _as_text(record.get("setup_family")).lower()
    if fam:
        return fam
    return _as_text(record.get("strategy_label")).lower()


def _symdir_key(record: dict[str, Any]) -> str:
    """Same symbol + same trade direction = duplicated exposure key."""
    sym = _record_symbol(record)
    if not sym:
        return ""
    return sym + "|" + _record_direction(record)


def _safety_block_findings(
    controls: dict[str, Any], records: list[dict[str, Any]]
) -> list[str]:
    """Reasons the whole payload is unsafe and must be refused. Pure."""
    reasons: list[str] = []
    for flag in COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("authorization flag requested: " + flag)
    for flag in COHORT_INDEPENDENCE_GATE_LOCK_FLAGS:
        if flag in controls and controls.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("gate unlock request: " + flag)
    for flag in COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("forbidden promotion/execution request: " + flag)
    for index, record in enumerate(records):
        rid = _record_id(record, index)
        for field in COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS:
            if field in record and _non_empty(record.get(field)):
                reasons.append(
                    "record " + rid + " carries executable field: " + field
                )
        for flag in COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
            if _truthy(record.get(flag)):
                reasons.append(
                    "record "
                    + rid
                    + " requests forbidden promotion/execution: "
                    + flag
                )
        for flag in COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS:
            if _truthy(record.get(flag)):
                reasons.append(
                    "record " + rid + " requests authorization: " + flag
                )
    return reasons


# Human-readable label for each correlation signal id. References signal TYPES
# only (never a raw symbol or trade direction), so the guidance never emits an
# execution verb.
_SIGNAL_HUMAN: dict[str, str] = {
    "same_symbol_and_direction": "same symbol and trade direction",
    "same_macro_event": "shared macro event",
    "same_market_regime": "shared market regime",
    "same_open_window_timing": "shared open-window timing",
    "same_close_window_timing": "shared close-window timing",
    "same_signal_family": "shared signal family",
}


class _UnionFind:
    """Tiny deterministic union-find over booked-record indices."""

    def __init__(self, size: int) -> None:
        self._parent = list(range(size))

    def find(self, x: int) -> int:
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            # Lower index becomes the root for determinism.
            if ra < rb:
                self._parent[rb] = ra
            else:
                self._parent[ra] = rb


def _shared_signal_ids(members: list[dict[str, Any]]) -> list[str]:
    """The correlation signal ids actually shared by >=2 members of a cohort."""
    if len(members) < 2:
        return []
    shared: list[str] = []
    key_fns = (
        ("same_symbol_and_direction", _symdir_key),
        ("same_macro_event", _record_macro),
        ("same_market_regime", _record_regime),
        ("same_open_window_timing", _record_open_window),
        ("same_close_window_timing", _record_close_window),
        ("same_signal_family", _record_signal_family),
    )
    for signal_id, fn in key_fns:
        counts: dict[str, int] = {}
        for record in members:
            value = fn(record)
            if value:
                counts[value] = counts.get(value, 0) + 1
        if any(c >= 2 for c in counts.values()):
            shared.append(signal_id)
    return shared


def assess_cohort_independence(payload: Any) -> dict[str, Any]:
    """Return a deterministic, research-only cohort independence assessment for a
    static evidence payload.

    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed / missing inputs never raise. ``payload`` may be a list of evidence
    records, or a dict carrying an ``evidence`` list plus optional control flags.
    Each cohort receives one of INDEPENDENT / CORRELATED / DUPLICATE /
    OPEN_OBSERVATION_ONLY / EXTERNAL_EVIDENCE_ONLY / INSUFFICIENT_SAMPLE. The
    result can only support a human research review; it unlocks no gate and
    authorizes nothing."""
    if isinstance(payload, dict):
        controls = payload
        raw_evidence = payload.get("evidence")
    elif isinstance(payload, (list, tuple)):
        controls = {}
        raw_evidence = payload
    else:
        controls = {}
        raw_evidence = None

    if isinstance(raw_evidence, (list, tuple)):
        records = [r for r in raw_evidence if isinstance(r, dict)]
    else:
        records = []

    block_reasons = _safety_block_findings(controls, records)

    # Partition records by source then status. External-research evidence can
    # never be an independent trade cohort; open/unrealized trades are
    # observation-only; only booked trades enter correlation analysis.
    trade_records: list[dict[str, Any]] = []
    external_records: list[tuple[int, dict[str, Any]]] = []
    for index, record in enumerate(records):
        if _record_source(record) in _EXTERNAL_SOURCE_SET:
            external_records.append((index, record))
        else:
            trade_records.append(record)

    booked: list[dict[str, Any]] = []
    booked_index: list[int] = []
    open_records: list[tuple[int, dict[str, Any]]] = []
    for record in trade_records:
        idx = records.index(record)
        if _record_status(record) in _BOOKED_STATUS_SET:
            booked.append(record)
            booked_index.append(idx)
        else:
            open_records.append((idx, record))

    # Union-find: collapse booked records that share any correlation signal.
    uf = _UnionFind(len(booked))
    key_fns = (
        _symdir_key,
        _record_macro,
        _record_regime,
        _record_open_window,
        _record_close_window,
        _record_signal_family,
    )
    for fn in key_fns:
        buckets: dict[str, list[int]] = {}
        for i, record in enumerate(booked):
            value = fn(record)
            if value:
                buckets.setdefault(value, []).append(i)
        for grouped in buckets.values():
            first = grouped[0]
            for other in grouped[1:]:
                uf.union(first, other)

    components: dict[int, list[int]] = {}
    for i in range(len(booked)):
        components.setdefault(uf.find(i), []).append(i)

    # First pass over booked components: which are lone positive booked cohorts?
    # Those are the candidates for true independence.
    component_list: list[tuple[tuple[str, ...], list[int]]] = []
    for member_indices in components.values():
        ids = tuple(
            sorted(
                _record_id(booked[i], booked_index[i]) for i in member_indices
            )
        )
        component_list.append((ids, member_indices))
    component_list.sort(key=lambda pair: pair[0])

    positive_independent_count = 0
    for _ids, member_indices in component_list:
        if len(member_indices) == 1:
            net = _as_number(booked[member_indices[0]].get("pnl"))
            if net > 0:
                positive_independent_count += 1

    min_independent = (
        COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT
    )
    independent_unlocked = positive_independent_count >= min_independent

    cohorts: list[dict[str, Any]] = []
    correlated_cluster_count = 0
    duplicate_count = 0

    # Booked cohorts.
    for ids, member_indices in component_list:
        members = [booked[i] for i in member_indices]
        net = sum(_as_number(m.get("pnl")) for m in members)
        size = len(members)
        cohort_id = "cohort:" + "|".join(ids)
        penalty_reasons: list[str] = []
        if size >= 2:
            shared_ids = _shared_signal_ids(members)
            shared_human = [_SIGNAL_HUMAN[s] for s in shared_ids]
            symdir_values = {
                (_record_symbol(m), _record_direction(m)) for m in members
            }
            same_symdir_only = (
                len(symdir_values) == 1
                and "same_macro_event" not in shared_ids
            )
            if "same_macro_event" in shared_ids:
                label = LABEL_CORRELATED
                correlated_cluster_count += 1
                penalty_reasons.append(
                    "correlated cluster of "
                    + str(size)
                    + " booked records sharing: "
                    + ", ".join(shared_human)
                    + "; counts as one event, not "
                    + str(size)
                    + " independent wins."
                )
            elif same_symdir_only:
                label = LABEL_DUPLICATE
                duplicate_count += 1
                penalty_reasons.append(
                    "duplicate exposure: "
                    + str(size)
                    + " booked records repeat the same symbol and trade "
                    "direction; counts as one event, not "
                    + str(size)
                    + " independent wins."
                )
            else:
                label = LABEL_CORRELATED
                correlated_cluster_count += 1
                penalty_reasons.append(
                    "correlated cluster of "
                    + str(size)
                    + " booked records sharing: "
                    + (", ".join(shared_human) or "a common timing/regime")
                    + "; counts as one event, not "
                    + str(size)
                    + " independent wins."
                )
        else:
            if net > 0 and independent_unlocked:
                label = LABEL_INDEPENDENT
            elif net > 0:
                label = LABEL_INSUFFICIENT_SAMPLE
                penalty_reasons.append(
                    "single booked positive cohort: a sample too small for "
                    "independence confidence ("
                    + str(positive_independent_count)
                    + " of "
                    + str(min_independent)
                    + " required independent positive booked cohorts)."
                )
            else:
                label = LABEL_INSUFFICIENT_SAMPLE
                penalty_reasons.append(
                    "single booked cohort with no positive edge: not positive "
                    "independent proof."
                )
        if net > 0:
            net_sign = "positive"
        elif net < 0:
            net_sign = "negative"
        else:
            net_sign = "flat"
        if label == LABEL_INDEPENDENT:
            score = _LABEL_SCORE[LABEL_INDEPENDENT]
        elif label == LABEL_INSUFFICIENT_SAMPLE and net > 0:
            score = _INSUFFICIENT_SAMPLE_POSITIVE_SCORE
        else:
            score = _LABEL_SCORE[label]
        cohorts.append(
            {
                "cohort_id": cohort_id,
                "source_class": "booked",
                "size": size,
                "member_ids": list(ids),
                "independence_label": label,
                "independence_score": score,
                "net_pnl_sign": net_sign,
                "penalty_reasons": penalty_reasons,
            }
        )

    # Open / unrealized cohorts (observation-only, never independent proof).
    open_cohorts: list[dict[str, Any]] = []
    for idx, record in open_records:
        rid = _record_id(record, idx)
        open_cohorts.append(
            {
                "cohort_id": "cohort:" + rid,
                "source_class": "open",
                "size": 1,
                "member_ids": [rid],
                "independence_label": LABEL_OPEN_OBSERVATION_ONLY,
                "independence_score": _LABEL_SCORE[LABEL_OPEN_OBSERVATION_ONLY],
                "net_pnl_sign": "unrealized",
                "penalty_reasons": [
                    "open/unrealized position: observation only; contributes "
                    "zero independent proof weight and creates no cohort."
                ],
            }
        )
    open_cohorts.sort(key=lambda c: c["cohort_id"])
    cohorts.extend(open_cohorts)

    # External-research cohorts (never an independent trade cohort).
    external_cohorts: list[dict[str, Any]] = []
    for idx, record in external_records:
        rid = _record_id(record, idx)
        src = _record_source(record)
        external_cohorts.append(
            {
                "cohort_id": "cohort:" + rid,
                "source_class": "external",
                "size": 1,
                "member_ids": [rid],
                "independence_label": LABEL_EXTERNAL_EVIDENCE_ONLY,
                "independence_score": (
                    _LABEL_SCORE[LABEL_EXTERNAL_EVIDENCE_ONLY]
                ),
                "net_pnl_sign": "not_applicable",
                "penalty_reasons": [
                    "external-research evidence ("
                    + src
                    + "): never an independent trade cohort and never trade "
                    "proof."
                ],
            }
        )
    external_cohorts.sort(key=lambda c: c["cohort_id"])
    cohorts.extend(external_cohorts)

    open_observation_count = len(open_records)
    external_evidence_count = len(external_records)
    can_support_promote_to_review = independent_unlocked and not block_reasons

    penalty_reasons_all: list[str] = []
    for cohort in cohorts:
        penalty_reasons_all.extend(cohort["penalty_reasons"])

    explanations = _independence_explanations(
        record_count=len(records),
        booked_count=len(booked),
        open_count=open_observation_count,
        external_count=external_evidence_count,
        correlated_cluster_count=correlated_cluster_count,
        duplicate_count=duplicate_count,
        positive_independent_count=positive_independent_count,
        min_independent=min_independent,
        block_reasons=block_reasons,
        can_support=can_support_promote_to_review,
    )

    return {
        "mode": COHORT_INDEPENDENCE_MODE,
        "evidence_present": len(records) > 0,
        "record_count": len(records),
        "trade_record_count": len(trade_records),
        "booked_count": len(booked),
        "open_count": open_observation_count,
        "external_record_count": external_evidence_count,
        "cohorts": cohorts,
        "cohort_count": len(cohorts),
        "positive_independent_booked_cohort_count": positive_independent_count,
        "correlated_cluster_count": correlated_cluster_count,
        "duplicate_count": duplicate_count,
        "open_observation_count": open_observation_count,
        "external_evidence_count": external_evidence_count,
        "min_independent_booked_cohorts_for_promote_support": min_independent,
        "block_reasons": block_reasons,
        "penalty_reasons": penalty_reasons_all,
        "explanations": explanations,
        "can_support_promote_to_review": can_support_promote_to_review,
        "promotes_beyond_review": False,
        "assesses_research_only": True,
        "authorizes_nothing": True,
    }


def _independence_explanations(
    record_count: int,
    booked_count: int,
    open_count: int,
    external_count: int,
    correlated_cluster_count: int,
    duplicate_count: int,
    positive_independent_count: int,
    min_independent: int,
    block_reasons: list[str],
    can_support: bool,
) -> list[str]:
    """Plain-language rationale referencing counts only (never a raw symbol or
    trade direction), so the guidance never emits an execution verb."""
    lines = [
        "Assessed "
        + str(record_count)
        + " record(s): "
        + str(booked_count)
        + " booked, "
        + str(open_count)
        + " open/unrealized, "
        + str(external_count)
        + " external-research.",
        "Independent positive booked cohorts: "
        + str(positive_independent_count)
        + " of "
        + str(min_independent)
        + " required before a research review may even be considered.",
        "Correlated clusters: "
        + str(correlated_cluster_count)
        + "; duplicate clusters: "
        + str(duplicate_count)
        + " (each counts as one event, not many independent wins).",
    ]
    if block_reasons:
        lines.append(
            "Refused: the payload requested an authorization, a gate unlock, a "
            "forbidden promotion, or carried an executable field; the "
            "assessment authorizes nothing."
        )
    elif can_support:
        lines.append(
            "Enough truly independent positive booked cohorts exist that a "
            "human may REVIEW the evidence. This unlocks no QA, no baseline, no "
            "backtest, no paper, no live, no broker/exchange, and no automation."
        )
    else:
        lines.append(
            "Not enough truly independent positive booked cohorts exist; this "
            "cannot support a research review yet. More INDEPENDENT booked "
            "evidence is needed."
        )
    return lines


def _assessment_summary_section(assessment: dict[str, Any]) -> list[str]:
    return [
        "Cohort independence assessment ("
        + assessment["mode"]
        + ", research review support only).",
        "Records assessed: "
        + str(assessment["record_count"])
        + " ("
        + str(assessment["booked_count"])
        + " booked, "
        + str(assessment["open_count"])
        + " open/unrealized, "
        + str(assessment["external_record_count"])
        + " external-research).",
        "Cohorts found: "
        + str(assessment["cohort_count"])
        + " (correlated clusters: "
        + str(assessment["correlated_cluster_count"])
        + ", duplicate clusters: "
        + str(assessment["duplicate_count"])
        + ", open: "
        + str(assessment["open_observation_count"])
        + ", external: "
        + str(assessment["external_evidence_count"])
        + ").",
        "Independent positive booked cohorts: "
        + str(assessment["positive_independent_booked_cohort_count"])
        + " of "
        + str(
            assessment["min_independent_booked_cohorts_for_promote_support"]
        )
        + " required.",
        "Can support a research review: "
        + str(assessment["can_support_promote_to_review"])
        + " (this still authorizes nothing).",
    ]


def _assessment_findings_section(assessment: dict[str, Any]) -> list[str]:
    if assessment["block_reasons"]:
        lines = ["Payload is unsafe and is refused:"]
        lines.extend("- " + reason for reason in assessment["block_reasons"])
        lines.append(
            "Refusal authorizes nothing and unlocks no gate; the unsafe payload "
            "must be rebuilt as static research-only evidence."
        )
        return lines
    lines = list(assessment["explanations"])
    if assessment["penalty_reasons"]:
        lines.append("Penalties applied:")
        lines.extend(
            "- " + reason for reason in assessment["penalty_reasons"]
        )
    return lines


def _cohort_section(assessment: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for cohort in assessment["cohorts"]:
        lines.append(
            cohort["cohort_id"]
            + " -> "
            + cohort["independence_label"]
            + " (score "
            + str(cohort["independence_score"])
            + ", "
            + str(cohort["size"])
            + " record(s), net "
            + cohort["net_pnl_sign"]
            + ")."
        )
    if not lines:
        lines.append("(no cohorts: no records were supplied)")
    return lines


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This assessment authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The most this assessment can do is support a human research review, which "
    "only invites a human to read the evidence and never produces an execution "
    "instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this independence assessment, "
    "independently confirm every cohort and penalty, and treat any "
    "can-support-review outcome as an invitation to review evidence on paper "
    "only. The single permitted next step is to register or assemble the next "
    "research-only contract. No execution of any kind is authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 cohort independence / correlation penalty contract "
    "template and is execution-free.",
    "It inspects an already-produced static set of evidence records, groups "
    "correlated records into cohorts, and reports one independence label per "
    "cohort; it runs nothing, fetches nothing, and connects nowhere.",
    "Core rule: one correlated move is one event, not many independent wins; "
    "shared macro event, market regime, timing window, signal family, or the "
    "same symbol and trade direction collapse records into one cohort.",
    "Open/unrealized positions are observation-only and create no independent "
    "cohort; external bot/whale/funding/BTC-cycle/daily-alpha evidence is never "
    "an independent trade cohort.",
    "Only closed/booked trades can supply positive independent proof, and at "
    "least three truly independent positive booked cohorts are required before "
    "a research review may even be considered.",
    "A can-support-review outcome never unlocks real-data QA, baseline, "
    "backtest, paper, live, broker/exchange, or automation.",
    "Every finding is attention-only and needs independent confirmation; the "
    "assessment never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured independence assessment before "
    "any further research-only contract is built.",
    "A human reviewer must confirm a can-support-review outcome is treated only "
    "as an invitation to review evidence and is never wired to a data fetch, an "
    "API call, a dataset, a QA run, a backtest, a paper/live trade, a broker or "
    "exchange, an order, or any automation.",
    "A human reviewer must independently confirm every cohort and penalty "
    "before it is trusted.",
    "A human reviewer must confirm the next step is only to register or build "
    "the next research-only contract, still on paper.",
    "No execution, data fetch, API call, dataset inspection, data acquisition, "
    "QA, backtest, paper/live, broker/exchange, automation, promotion, or "
    "downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "independence_next_required_action",
    "independence_current_stage",
    "observation_only_evidence_lanes",
    "independence_labels",
    "correlation_signals",
    "min_independent_booked_cohorts_for_promote_support",
    "trade_source_tags",
    "external_research_source_tags",
    "booked_status_tags",
    "open_status_tags",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_promotion_request_flags",
    "executable_signal_fields",
    "forbidden_trade_terms",
    "evidence",
    "assessment",
    "cohorts",
    "cohort_count",
    "record_count",
    "booked_count",
    "open_count",
    "external_record_count",
    "positive_independent_booked_cohort_count",
    "correlated_cluster_count",
    "duplicate_count",
    "open_observation_count",
    "external_evidence_count",
    "can_support_promote_to_review",
    "block_reasons",
    "penalty_reasons",
    "explanations",
    "assessment_summary_section",
    "assessment_findings_section",
    "cohort_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "operator_next_step",
    "safety_posture",
    "operator_notes",
    "human_operator_required_next_steps",
    "requires_independent_confirmation",
    "human_approval_required",
    "read_only",
    "executes",
    "research_only",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "promotes_beyond_review",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the posture (callers cannot taint the global)."""
    return dict(COHORT_INDEPENDENCE_SAFETY_POSTURE)


def build_crypto_d1_cohort_independence_correlation_penalty_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build the read-only cohort independence / correlation penalty contract.
    Pure; no I/O, no data fetch, no mutation of inputs, no clock read, no random
    id. When no payload is given, the static DEFAULT_SAMPLE_EVIDENCE is assessed.
    A fresh dict (with fresh lists/dicts) is returned every call. The contract
    never promotes a strategy beyond a research review and authorizes nothing."""
    if payload is None:
        source = _isolated(DEFAULT_SAMPLE_EVIDENCE)
    elif isinstance(payload, (dict, list, tuple)):
        source = _isolated(payload)
    else:
        source = payload

    assessment = assess_cohort_independence(source)

    contract: dict[str, Any] = {
        "schema_version": COHORT_INDEPENDENCE_SCHEMA_VERSION,
        "label": COHORT_INDEPENDENCE_LABEL,
        "status": COHORT_INDEPENDENCE_STATUS,
        "stage": "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT_ONLY",
        "mode": COHORT_INDEPENDENCE_MODE,
        "core_rule": COHORT_INDEPENDENCE_CORE_RULE,
        "independence_next_required_action": (
            COHORT_INDEPENDENCE_NEXT_REQUIRED_ACTION
        ),
        "independence_current_stage": COHORT_INDEPENDENCE_CURRENT_STAGE,
        "observation_only_evidence_lanes": (
            COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "independence_labels": COHORT_INDEPENDENCE_LABELS,
        "correlation_signals": COHORT_INDEPENDENCE_CORRELATION_SIGNALS,
        "min_independent_booked_cohorts_for_promote_support": (
            COHORT_INDEPENDENCE_MIN_INDEPENDENT_BOOKED_COHORTS_FOR_PROMOTE_SUPPORT
        ),
        "trade_source_tags": COHORT_INDEPENDENCE_TRADE_SOURCE_TAGS,
        "external_research_source_tags": (
            COHORT_INDEPENDENCE_EXTERNAL_RESEARCH_SOURCE_TAGS
        ),
        "booked_status_tags": COHORT_INDEPENDENCE_BOOKED_STATUS_TAGS,
        "open_status_tags": COHORT_INDEPENDENCE_OPEN_STATUS_TAGS,
        "authorization_flags": COHORT_INDEPENDENCE_AUTHORIZATION_FLAGS,
        "gate_lock_flags": COHORT_INDEPENDENCE_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            COHORT_INDEPENDENCE_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": (
            COHORT_INDEPENDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": (
            COHORT_INDEPENDENCE_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": (
            COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS
        ),
        "evidence": _isolated(source)
        if isinstance(source, (dict, list))
        else {},
        "assessment": assessment,
        "cohorts": list(assessment["cohorts"]),
        "cohort_count": assessment["cohort_count"],
        "record_count": assessment["record_count"],
        "booked_count": assessment["booked_count"],
        "open_count": assessment["open_count"],
        "external_record_count": assessment["external_record_count"],
        "positive_independent_booked_cohort_count": (
            assessment["positive_independent_booked_cohort_count"]
        ),
        "correlated_cluster_count": assessment["correlated_cluster_count"],
        "duplicate_count": assessment["duplicate_count"],
        "open_observation_count": assessment["open_observation_count"],
        "external_evidence_count": assessment["external_evidence_count"],
        "can_support_promote_to_review": (
            assessment["can_support_promote_to_review"]
        ),
        "block_reasons": list(assessment["block_reasons"]),
        "penalty_reasons": list(assessment["penalty_reasons"]),
        "explanations": list(assessment["explanations"]),
        "assessment_summary_section": _assessment_summary_section(assessment),
        "assessment_findings_section": _assessment_findings_section(
            assessment
        ),
        "cohort_section": _cohort_section(assessment),
        "observation_only_section": _observation_only_section(),
        "no_execution_authorization_section": list(
            _NO_EXECUTION_AUTHORIZATION_SECTION
        ),
        "operator_next_step": _OPERATOR_NEXT_STEP,
        "safety_posture": _safety_posture(),
        "operator_notes": list(_OPERATOR_NOTES),
        "human_operator_required_next_steps": list(
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "requires_independent_confirmation": True,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "research_only": True,
        "authorizes_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_backtest": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_automation": False,
        "authorizes_real_world_action": False,
        "unlocks_downstream_gate": False,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "promotes_beyond_review": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# Top-level posture flags that must all be exactly False for a valid contract.
_REQUIRED_FALSE_FLAGS: tuple[str, ...] = (
    "executes",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "promotes_beyond_review",
)

# The generated-guidance fields whose text is the assessment's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``evidence``, ``cohorts``, ``penalty_reasons`` and ``block_reasons`` may embed
# caller-supplied field names and are excluded from this check.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "operator_next_step",
    "assessment_summary_section",
    "assessment_findings_section",
    "cohort_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "explanations",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in COHORT_INDEPENDENCE_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the assessment's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    A block findings section can legitimately quote an offending input field
    name while explaining the refusal, so that section is skipped when the
    payload was refused."""
    blocked = bool(contract.get("block_reasons"))
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "assessment_findings_section" and blocked:
            continue
        value = contract.get(field)
        if isinstance(value, str):
            if _contains_forbidden_term(value):
                return False
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str) and _contains_forbidden_term(item):
                    return False
    return True


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == COHORT_INDEPENDENCE_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == COHORT_INDEPENDENCE_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT_ONLY"
    )
    core_rule_ok = safe.get("core_rule") == COHORT_INDEPENDENCE_CORE_RULE
    human_required = safe.get("human_approval_required") is True
    confirmation_required = (
        safe.get("requires_independent_confirmation") is True
    )
    flags_false = all(
        safe.get(flag) is False for flag in _REQUIRED_FALSE_FLAGS
    )
    gates_locked = (
        safe.get("real_data_qa_blocked") is True
        and safe.get("baseline_backtest_blocked") is True
        and safe.get("paper_trading_gate_locked") is True
        and safe.get("micro_live_gate_locked") is True
    )

    posture = safe.get("safety_posture")
    posture_ok = (
        isinstance(posture, dict)
        and posture == COHORT_INDEPENDENCE_SAFETY_POSTURE
    )

    labels_ok = (
        tuple(safe.get("independence_labels") or ())
        == COHORT_INDEPENDENCE_LABELS
    )
    signals_ok = (
        tuple(safe.get("correlation_signals") or ())
        == COHORT_INDEPENDENCE_CORRELATION_SIGNALS
    )
    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == COHORT_INDEPENDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
    )

    cohorts = safe.get("cohorts")
    cohorts_ok = isinstance(cohorts, list) and all(
        isinstance(c, dict)
        and c.get("independence_label") in _LABEL_SET
        and isinstance(c.get("cohort_id"), str)
        for c in cohorts
    )

    assessment = safe.get("assessment")
    assessment_ok = (
        isinstance(assessment, dict)
        and assessment.get("authorizes_nothing") is True
        and assessment.get("assesses_research_only") is True
        and assessment.get("promotes_beyond_review") is False
    )

    support_flag = safe.get("can_support_promote_to_review")
    support_is_bool = support_flag is True or support_flag is False

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "assessment_summary_section",
            "assessment_findings_section",
            "cohort_section",
            "observation_only_section",
            "no_execution_authorization_section",
            "operator_notes",
            "human_operator_required_next_steps",
        )
    )
    operator_next_step_ok = bool(_as_text(safe.get("operator_next_step")))

    valid = (
        not missing
        and schema_ok
        and label_ok
        and read_only
        and research_only
        and stage_ok
        and core_rule_ok
        and human_required
        and confirmation_required
        and flags_false
        and gates_locked
        and posture_ok
        and labels_ok
        and signals_ok
        and lanes_ok
        and cohorts_ok
        and assessment_ok
        and support_is_bool
        and no_trade_language
        and sections_ok
        and operator_next_step_ok
    )

    return {
        "valid": bool(valid),
        "missing_fields": missing,
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "flags_false": flags_false,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "labels_ok": labels_ok,
        "signals_ok": signals_ok,
        "lanes_ok": lanes_ok,
        "cohorts_ok": cohorts_ok,
        "assessment_ok": assessment_ok,
        "support_is_bool": support_is_bool,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_cohort_independence_correlation_penalty_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_cohort_independence_correlation_penalty_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Cohort Independence / Correlation Penalty Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Records assessed: " + str(safe.get("record_count")))
    lines.append("- Booked: " + str(safe.get("booked_count")))
    lines.append("- Open/unrealized: " + str(safe.get("open_count")))
    lines.append("- External-research: " + str(safe.get("external_record_count")))
    lines.append(
        "- Independent positive booked cohorts: "
        + str(safe.get("positive_independent_booked_cohort_count"))
    )
    lines.append(
        "- Correlated clusters: " + str(safe.get("correlated_cluster_count"))
    )
    lines.append("- Duplicate clusters: " + str(safe.get("duplicate_count")))
    lines.append(
        "- Can support research review: "
        + str(safe.get("can_support_promote_to_review"))
    )
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
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
        "- micro_live_gate locked: " + str(safe.get("micro_live_gate_locked"))
    )

    def _emit(title: str, key: str) -> None:
        lines.append("")
        lines.append("## " + title)
        section = safe.get(key)
        if isinstance(section, (list, tuple)) and section:
            for item in section:
                lines.append("- " + _as_text(item))
        else:
            lines.append("- (none)")

    _emit("Assessment Summary", "assessment_summary_section")
    _emit("Assessment Findings", "assessment_findings_section")
    _emit("Cohorts", "cohort_section")
    _emit("Penalties", "penalty_reasons")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)
