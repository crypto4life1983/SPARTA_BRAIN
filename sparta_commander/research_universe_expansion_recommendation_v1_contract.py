"""SPARTA Research-Universe Expansion Recommendation v1
(PURE, READ-ONLY, RESEARCH ONLY).

A research-only recommendation, built BEFORE any decision to open C20, for expanding
the research universe / data sources beyond the current BTC/ETH/SOL D1 spot-only lane.
It is motivated by the meta-study finding that C1-C19 failures split into two roots:
long-biased candidates lose to buy-and-hold risk-adjusted, and market-neutral
candidates fail OOS neutrality -- so another BTC/ETH/SOL D1-only candidate is likely to
repeat the same failure.

It EVALUATES seven possible future data/universe expansions and, for each, reports the
edge it could test, why it is structurally different from C1-C19, the required data
fields, likely public data-source possibilities, safety risks, whether a network fetch
would be needed, whether credentials would be needed, and whether it can stay
research-only. It then recommends a first data-expansion target.

It does NOTHING beyond describing options: it does NOT assign C20, opens no candidate,
fetches NO data, adds NO XAUUSD / new instrument, creates NO detector/labels/replay,
runs NO optimization/tuning, and touches NO paper/live/broker/order/trading surface.
Any actual data fetch is a SEPARATE hard human gate and is NOT taken here. Every
capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

RUE_VERSION = "v1"
RUE_MODE = "RESEARCH_ONLY"
RUE_LANE = "crypto_d1_auto_research"

# the two failure roots from the meta-study (what an expansion must structurally fix)
FAILURE_ROOTS = {
    "root_a_lose_to_buy_and_hold_risk_adjusted": (
        "long-biased families reduce to crypto beta and lose to holding risk-adjusted "
        "(C14, C15, C17, C18) -- needs a NON-BETA / orthogonal return source"),
    "root_b_oos_neutrality_fails": (
        "market-neutral families fail because estimated cross-asset neutrality does "
        "not persist out of sample (C16, C19) -- needs a MECHANICALLY neutral "
        "construction, not an estimated one"),
}

# the recommended first target + the explicit token required before ANY fetch
RECOMMENDED_FIRST_TARGET = "perp_basis_spot_perp_spread"
NEXT_HUMAN_TOKEN_BEFORE_ANY_FETCH = (
    "HUMAN_APPROVED_FETCH_PUBLIC_PERP_SPOT_BASIS_AND_FUNDING_DATA_RESEARCH_ONLY")
NEXT_REQUIRED_ACTION = (
    "AWAIT_HUMAN_DECISION_ON_DATA_EXPANSION_TARGET__NO_C20_ASSIGNED__NO_FETCH_TAKEN")

# --- the seven evaluated expansion options ----------------------------------
EXPANSION_OPTIONS = (
    {
        "key": "crypto_funding_rate_data",
        "name": "Crypto perpetual funding-rate data",
        "edge_it_could_test": (
            "funding-carry (harvest persistently positive funding), funding-extreme "
            "mean reversion, and funding as a positioning/regime signal -- a NON-PRICE "
            "return source orthogonal to spot direction"),
        "structurally_different_from_c1_c19": (
            "funding is a DERIVATIVES-market information source, not a spot-OHLCV "
            "directional or estimated-neutral construction; it is new INFORMATION, not "
            "a re-parameterization of price -- directly targets failure root A"),
        "required_data_fields": ("timestamp", "symbol", "funding_rate",
                                 "funding_interval", "mark_price"),
        "likely_public_data_sources": (
            "Binance/Bybit/OKX PUBLIC funding-rate history REST endpoints "
            "(unauthenticated market data)"),
        "safety_risks": ("low: public REST, no account; main risk is cross-exchange "
                         "alignment + survivorship of delisted perps"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_a_lose_to_buy_and_hold_risk_adjusted",
        "feasibility": "high",
    },
    {
        "key": "perp_basis_spot_perp_spread",
        "name": "Perpetual basis / spot-perp spread",
        "edge_it_could_test": (
            "basis carry (long spot / short perp of the SAME asset to harvest the "
            "funding/basis), basis mean-reversion, and basis as a leverage/positioning "
            "regime signal"),
        "structurally_different_from_c1_c19": (
            "a spread between two instruments on the SAME underlying is MECHANICALLY "
            "dollar- and beta-neutral by construction -- its neutrality CANNOT 'fail "
            "OOS' the way C16/C19's ESTIMATED cross-asset beta did -- AND its return is "
            "carry, not spot direction; it targets BOTH failure roots at once"),
        "required_data_fields": ("timestamp", "symbol", "spot_close", "perp_close",
                                 "perp_mark", "funding_rate"),
        "likely_public_data_sources": (
            "Binance PUBLIC spot klines + PUBLIC USDT-perp klines/mark + PUBLIC "
            "funding history (all unauthenticated)"),
        "safety_risks": ("low: public klines; main risk is treating the carry as "
                         "risk-free (it is not -- basis can gap) and ignoring perp "
                         "liquidation/borrow frictions in the replay cost model"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_b_oos_neutrality_fails",
        "feasibility": "high",
    },
    {
        "key": "cross_exchange_spread_or_basis",
        "name": "Cross-exchange spread / basis",
        "edge_it_could_test": (
            "cross-exchange price dislocations and lead-lag between venues"),
        "structurally_different_from_c1_c19": (
            "an inter-venue spread -- different from any single-venue C1-C19 family -- "
            "but it is execution/latency-sensitive and the apparent edge is usually "
            "illusory after fees, borrow, and transfer frictions"),
        "required_data_fields": ("timestamp", "symbol", "exchange", "close"),
        "likely_public_data_sources": (
            "multiple exchanges' PUBLIC klines (Binance / Coinbase / Kraken)"),
        "safety_risks": ("medium: multi-source timestamp alignment, latency illusions, "
                         "and edges that vanish under realistic cross-venue costs"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_b_oos_neutrality_fails",
        "feasibility": "medium",
    },
    {
        "key": "options_implied_volatility",
        "name": "Options / implied-volatility (variance risk premium)",
        "edge_it_could_test": (
            "variance risk premium (implied vs realized vol), vol-carry, and skew "
            "signals -- a documented NON-BETA return source"),
        "structurally_different_from_c1_c19": (
            "a volatility-premium edge is orthogonal to both spot direction AND "
            "cross-asset neutrality -- a genuinely new return driver vs every C1-C19 "
            "price/structure family"),
        "required_data_fields": ("timestamp", "symbol", "atm_implied_vol",
                                 "realized_vol", "expiry", "skew"),
        "likely_public_data_sources": (
            "Deribit PUBLIC market data (option summary / IV); realized vol derived "
            "from the existing cached spot"),
        "safety_risks": ("medium: option data is sparser and harder to clean; "
                         "modelling complexity; easy to over-fit a small surface"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_a_lose_to_buy_and_hold_risk_adjusted",
        "feasibility": "medium",
    },
    {
        "key": "broader_crypto_universe",
        "name": "Broader crypto universe beyond BTC/ETH/SOL",
        "edge_it_could_test": (
            "cross-sectional momentum / relative value over a larger liquid universe "
            "(e.g. top 20-50), giving more breadth for a market-neutral construction"),
        "structurally_different_from_c1_c19": (
            "more breadth could make a neutral residual MORE STABLE and the sample "
            "LARGER (directly answering C19's 41-entry / ~44%-neutral problem) -- BUT "
            "it is the SAME mechanism class as C11/C16/C19, so it risks repeating the "
            "estimated-neutrality failure; only a partial differentiation"),
        "required_data_fields": ("timestamp", "symbol", "open", "high", "low",
                                 "close", "volume"),
        "likely_public_data_sources": "Binance PUBLIC D1 klines for N symbols",
        "safety_risks": ("low data risk, but HIGH repeat-failure risk: it is the same "
                         "estimated-neutrality mechanism that already failed twice"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_b_oos_neutrality_fails",
        "feasibility": "high_data_but_low_novelty",
    },
    {
        "key": "higher_frequency_ohlcv",
        "name": "Higher-frequency OHLCV (only if it solves a specific root)",
        "edge_it_could_test": (
            "intraday microstructure / mean-reversion -- ONLY justified if a specific "
            "rejected root needs more samples (e.g. neutrality estimation)"),
        "structurally_different_from_c1_c19": (
            "NOT really -- it is a higher frequency of the SAME price signal; C18 (H4) "
            "already failed at higher frequency, and more frequency adds cost/noise. "
            "Recommend AGAINST unless tied to a specific, named failure root"),
        "required_data_fields": ("timestamp", "symbol", "open", "high", "low",
                                 "close", "volume"),
        "likely_public_data_sources": "Binance PUBLIC intraday klines",
        "safety_risks": ("medium: turnover/cost sensitivity is high and intraday noise "
                         "invites over-fitting; low structural novelty"),
        "network_fetch_needed": True,
        "credentials_needed": False,
        "can_stay_research_only": True,
        "addresses_failure_root": "none_clearly",
        "feasibility": "low_novelty",
    },
    {
        "key": "non_crypto_instruments_separate_lane",
        "name": "Non-crypto instruments (SEPARATE lane, explicit approval only)",
        "edge_it_could_test": (
            "cross-asset diversification / macro signals (equities, rates, FX, gold) "
            "with different return drivers"),
        "structurally_different_from_c1_c19": (
            "genuinely different return drivers, BUT this is OUTSIDE the crypto-D1 "
            "lane: it is a SEPARATE research lane that needs its own explicit approval "
            "(XAUUSD and any new instrument class remain deferred)"),
        "required_data_fields": ("timestamp", "symbol", "open", "high", "low",
                                 "close", "volume"),
        "likely_public_data_sources": (
            "yfinance proxies / Databento (some already cached) -- but a SEPARATE lane"),
        "safety_risks": ("medium: scope creep, lane confusion, and some sources "
                         "(Databento) may need credentials -- must be a separate, "
                         "explicitly-approved lane"),
        "network_fetch_needed": True,
        "credentials_needed": True,
        "can_stay_research_only": True,
        "addresses_failure_root": "root_a_lose_to_buy_and_hold_risk_adjusted",
        "feasibility": "separate_lane_explicit_approval_required",
    },
)

_REQUIRED_OPTION_KEYS = (
    "key", "name", "edge_it_could_test", "structurally_different_from_c1_c19",
    "required_data_fields", "likely_public_data_sources", "safety_risks",
    "network_fetch_needed", "credentials_needed", "can_stay_research_only",
    "addresses_failure_root", "feasibility",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "assigns_c20", "opens_candidate", "creates_candidate",
    "creates_family_proposal", "fetches_data", "fetches_funding", "fetches_basis",
    "fetches_options", "adds_xauusd", "adds_new_instrument_class", "runs_detector",
    "runs_labels", "runs_replay", "computes_pnl", "optimizes_parameters",
    "tunes_parameters", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def get_universe_expansion_label() -> str:
    return (
        "Research-universe expansion recommendation v1 (READ-ONLY, RESEARCH ONLY). "
        "Evaluates 7 data/universe expansions beyond BTC/ETH/SOL D1 spot. Recommended "
        "first target: perpetual basis / spot-perp spread + funding -- MECHANICALLY "
        "neutral (fixes the OOS-neutrality root) and a carry source (fixes the "
        "buy-and-hold root), from PUBLIC unauthenticated data. Does NOT assign C20, "
        "opens no candidate, fetches no data, adds no XAUUSD/new instrument, runs no "
        "detector/labels/replay/optimization. Any fetch is a SEPARATE explicit human "
        "gate, not taken here. NOT a profitability claim.")


def get_universe_expansion_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def _recommended() -> dict[str, Any]:
    for o in EXPANSION_OPTIONS:
        if o["key"] == RECOMMENDED_FIRST_TARGET:
            return dict(o)
    return {}


def build_universe_expansion_recommendation() -> dict[str, Any]:
    """Assemble the frozen research-universe expansion recommendation. Pure; no I/O;
    assigns no C20; opens no candidate; fetches nothing."""
    options = [dict(o) for o in EXPANSION_OPTIONS]
    rec = _recommended()
    record: dict[str, Any] = {
        "version": RUE_VERSION, "mode": RUE_MODE, "lane": RUE_LANE,
        "is_recommendation_only": True,
        "label": get_universe_expansion_label(),
        # hard guarantees
        "assigns_c20": False, "c20_assigned": False, "candidate_id": None,
        "opens_candidate": False, "creates_family_proposal": False,
        "fetches_data": False, "any_fetch_taken_here": False,
        "adds_xauusd_or_new_instrument": False,
        "creates_detector_labels_or_replay": False,
        "optimizes_or_tunes": False,
        # motivation (the two failure roots an expansion must fix)
        "failure_roots": dict(FAILURE_ROOTS),
        "current_universe": "BTC/ETH/SOL D1 spot only (cached, SHA-pinned)",
        # the seven evaluated options
        "expansion_options": options,
        "option_count": len(options),
        # the recommendation
        "recommended_first_target": RECOMMENDED_FIRST_TARGET,
        "recommended_option": rec,
        "why_recommended": (
            "The perpetual basis / spot-perp spread is the only evaluated option that "
            "structurally targets BOTH failure roots: it is MECHANICALLY market-neutral "
            "(long spot / short perp of the same asset, so neutrality cannot fail out "
            "of sample as C16/C19's estimated cross-asset beta did), and its return is "
            "CARRY (funding/basis), a non-beta source that does not have to beat "
            "buy-and-hold. It is sourceable from PUBLIC, unauthenticated Binance spot + "
            "perp + funding data -- no credentials -- and can stay research-only. "
            "Funding-rate data is its companion signal. Broader-universe and "
            "higher-frequency repeat existing mechanisms; non-crypto is a separate "
            "lane."),
        "companion_signal": "crypto_funding_rate_data",
        "recommendation_is_advisory_human_decides": True,
        # the data-fetch hard gate (not taken here)
        "fetch_requires_separate_explicit_human_token": True,
        "next_human_token_before_any_fetch": NEXT_HUMAN_TOKEN_BEFORE_ANY_FETCH,
        "recommended_target_uses_public_data_no_credentials": (
            rec.get("credentials_needed") is False),
        "human_review_required": True,
        "current_loop_stage": "pre_c20_data_universe_expansion_recommendation",
        "next_required_action": NEXT_REQUIRED_ACTION,
        "requires_human_approval_before_c20": True,
        "opening_c20_requires_explicit_open_candidate_token": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_assign_c20": True,
        "no_open_candidate": True, "no_create_candidate": True,
        "no_family_proposal": True, "no_data_fetch": True, "no_funding_fetch": True,
        "no_basis_fetch": True, "no_options_fetch": True, "no_xauusd": True,
        "no_new_instrument_class": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_pnl": True, "no_optimization": True, "no_tuning": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_universe_expansion_recommendation(
        record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the recommendation is research-only,
    recommendation-only, assigns NO C20 / opens no candidate / fetches no data / adds
    no new instrument, evaluates all seven options each with the full required field
    set, names a recommended first target that is one of the options, records that any
    fetch needs a separate explicit human token (not taken here), keeps the C20 human
    gate, and pins every capability flag False with the scope locks."""
    failures: list = []
    if record.get("mode") != RUE_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_recommendation_only") is not True:
        failures.append("not_recommendation_only")

    # hard guarantees
    for k in ("assigns_c20", "c20_assigned", "opens_candidate",
              "creates_family_proposal", "fetches_data", "any_fetch_taken_here",
              "adds_xauusd_or_new_instrument", "creates_detector_labels_or_replay",
              "optimizes_or_tunes"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)
    if record.get("candidate_id") is not None:
        failures.append("candidate_id_must_be_none")

    # the two failure roots are carried
    fr = record.get("failure_roots") or {}
    for k in ("root_a_lose_to_buy_and_hold_risk_adjusted",
              "root_b_oos_neutrality_fails"):
        if not fr.get(k):
            failures.append("failure_root_missing_%s" % k)

    # all seven options present, each with the full field set
    opts = record.get("expansion_options") or []
    if len(opts) != 7:
        failures.append("expected_seven_options")
    keys = {o.get("key") for o in opts}
    for must in ("crypto_funding_rate_data", "perp_basis_spot_perp_spread",
                 "cross_exchange_spread_or_basis", "options_implied_volatility",
                 "broader_crypto_universe", "higher_frequency_ohlcv",
                 "non_crypto_instruments_separate_lane"):
        if must not in keys:
            failures.append("option_missing_%s" % must)
    for o in opts:
        for f in _REQUIRED_OPTION_KEYS:
            if f not in o or o.get(f) in (None, ""):
                failures.append("option_%s_missing_field_%s" % (o.get("key"), f))
        if not isinstance(o.get("network_fetch_needed"), bool):
            failures.append("option_%s_fetch_flag_not_bool" % o.get("key"))
        if not isinstance(o.get("credentials_needed"), bool):
            failures.append("option_%s_creds_flag_not_bool" % o.get("key"))
        if o.get("can_stay_research_only") is not True:
            failures.append("option_%s_not_research_only" % o.get("key"))

    # the recommendation
    if record.get("recommended_first_target") not in keys:
        failures.append("recommended_target_not_in_options")
    if record.get("recommended_first_target") != RECOMMENDED_FIRST_TARGET:
        failures.append("recommended_target_tampered")
    if record.get("recommendation_is_advisory_human_decides") is not True:
        failures.append("recommendation_not_advisory")
    if not record.get("why_recommended"):
        failures.append("why_recommended_missing")
    # the recommended target must be public-data / no-credentials
    if record.get("recommended_target_uses_public_data_no_credentials") is not True:
        failures.append("recommended_target_needs_credentials")

    # fetch hard gate (not taken here) + C20 gate
    if record.get("fetch_requires_separate_explicit_human_token") is not True:
        failures.append("fetch_gate_missing")
    if record.get("next_human_token_before_any_fetch") != (
            NEXT_HUMAN_TOKEN_BEFORE_ANY_FETCH):
        failures.append("fetch_token_tampered")
    if record.get("requires_human_approval_before_c20") is not True:
        failures.append("c20_gate_missing")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_assign_c20", "no_open_candidate", "no_data_fetch",
                "no_funding_fetch", "no_basis_fetch", "no_xauusd",
                "no_new_instrument_class", "no_detector", "no_labels", "no_replay",
                "no_optimization", "no_credentials", "no_commit", "no_push",
                "no_paper_trading", "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
