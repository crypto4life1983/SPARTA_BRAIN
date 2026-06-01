"""SPARTA Crypto-D1 Protocol Memo — validator (research-only, stdlib).

Validates `reports/crypto_d1_protocol_v1/protocol.json` against the required
schema and the hard safety contract:
  * research_only is True
  * seven execution / fetch / connection / backtest / dataset-processing flags
    are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      backtest_enabled
      dataset_processing_enabled
  * target_assets include BTC, ETH, SOL
  * allowed_market_type == 'spot'; perp_futures + dated_futures + options +
    leveraged_tokens are explicitly listed in forbidden_market_types
  * timeframe.primary == '1d'; intraday is explicitly out of scope
  * session_model declares 24/7 crypto + UTC + missing-day policy
  * candidate_strategy_families include the 7 declared families with
    mean_reversion marked WATCH_only (not primary)
  * data_requirements cover OHLCV / timezone / 24/7 / missing-day / provenance
    / symbol mapping / fees / slippage / stablecoin / freeze / no-lookahead
  * validation_phases include P0..P8
  * pass_watch_fail_rules + kill_conditions + required_future_artifacts +
    safety_boundaries are non-empty
  * no profitability / live-readiness / backtest-authorize claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_protocol_check.py validate
  python tools/crypto_d1_protocol_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR_REL = "reports/crypto_d1_protocol_v1"
PROTO_JSON = "protocol.json"
PROTO_MD = "protocol.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "protocol_id",
    "title",
    "version",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_enabled",
    "dataset_processing_enabled",
    "lane",
    "target_assets",
    "allowed_market_type",
    "forbidden_market_types",
    "timeframe",
    "session_model",
    "candidate_strategy_families",
    "data_requirements",
    "fee_slippage_requirements",
    "risk_assumptions",
    "validation_phases",
    "pass_watch_fail_rules",
    "kill_conditions",
    "required_future_artifacts",
    "safety_boundaries",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_enabled",
    "dataset_processing_enabled",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_STRATEGY_FAMILY_IDS = (
    "daily_trend_following",
    "donchian_channel_breakout",
    "moving_average_trend_filter",
    "volatility_regime_gate",
    "momentum_continuation",
    "risk_on_risk_off_filter",
    "mean_reversion",
)

REQUIRED_VALIDATION_PHASES = (
    "P0_protocol",
    "P1_data_contract",
    "P2_dataset_manifest_freeze",
    "P3_baseline_strategy_impl",
    "P4_is_oos_split",
    "P5_walk_forward_or_rolling",
    "P6_robustness_sensitivity",
    "P7_paper_signal_simulation",
    "P8_live_trading",
)

REQUIRED_DATA_REQ_KEYS = (
    "ohlcv_daily_required",
    "timezone_normalization",
    "session_handling",
    "missing_day_rules",
    "exchange_or_source_provenance",
    "symbol_mapping",
    "fee_assumptions_required",
    "slippage_assumptions_required",
    "stablecoin_quote_currency_handling",
    "data_freeze_requirement",
    "no_lookahead_requirement",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "kill_conditions",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown.
DISTINCTION_PHRASES = (
    "Crypto trend ideas are not profitable until tested",
    "A good historical chart does not imply future returns",
    "No backtest is authorized by this protocol alone",
    "24/7",
)

# Forbidden capability claims.
FORBIDDEN_PHRASES = (
    "guaranteed profit",
    "risk-free profit",
    "guaranteed alpha",
    "live-ready",
    "production-ready",
    "live trading enabled",
    "this is profitable",
    "we have an edge",
    "place the order",
    "place an order",
    "connect to exchange",
    "fetch live data",
)


def _load(repo_root: Path):
    p = repo_root / PROTO_DIR_REL / PROTO_JSON
    if not p.exists():
        return None, f"missing: {p.as_posix()}"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid JSON ({type(exc).__name__}): {p.as_posix()}"


def validate(repo_root: Path = REPO_ROOT):
    errors: list = []
    data, err = _load(repo_root)
    if err:
        return False, [err]
    if not isinstance(data, dict):
        return False, ["protocol.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Lane.
    if data.get("lane") != "crypto_d1_protocol":
        errors.append(f"lane must be 'crypto_d1_protocol' (got {data.get('lane')!r})")

    # Target assets must include BTC, ETH, SOL.
    tas = data.get("target_assets")
    if not isinstance(tas, list) or not tas:
        errors.append("target_assets must be a non-empty list")
    else:
        canonical_set = {a.get("symbol_canonical") for a in tas if isinstance(a, dict)}
        for asset in REQUIRED_TARGET_ASSETS:
            if asset not in canonical_set:
                errors.append(f"target_assets missing required canonical symbol: {asset}")

    # allowed_market_type == 'spot'.
    if data.get("allowed_market_type") != "spot":
        errors.append(f"allowed_market_type must be 'spot' (got {data.get('allowed_market_type')!r})")

    # forbidden_market_types: must mention perp_futures.
    fmt = data.get("forbidden_market_types")
    if not isinstance(fmt, list) or not fmt:
        errors.append("forbidden_market_types must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in fmt).lower()
        for needle in ("perp", "dated_futures", "options", "leveraged"):
            if needle not in joined:
                errors.append(f"forbidden_market_types missing needle: {needle!r}")

    # Timeframe.
    tf = data.get("timeframe")
    if not isinstance(tf, dict):
        errors.append("timeframe must be a dict")
    else:
        if tf.get("primary") != "1d":
            errors.append(f"timeframe.primary must be '1d' (got {tf.get('primary')!r})")
        if tf.get("intraday_explicitly_out_of_scope") is not True:
            errors.append("timeframe.intraday_explicitly_out_of_scope must be True")

    # Session model.
    sm = data.get("session_model")
    if not isinstance(sm, dict):
        errors.append("session_model must be a dict")
    else:
        cal = sm.get("market_calendar") or ""
        if "24/7" not in cal:
            errors.append("session_model.market_calendar must mention '24/7'")
        if sm.get("weekday_only_filters_forbidden") is not True:
            errors.append("session_model.weekday_only_filters_forbidden must be True")
        if sm.get("missing_day_policy_documented_in_data_contract") is not True:
            errors.append("session_model.missing_day_policy_documented_in_data_contract must be True")
        if not isinstance(sm.get("timezone_normalization"), str) or "UTC" not in sm.get("timezone_normalization"):
            errors.append("session_model.timezone_normalization must mention UTC")

    # Strategy families: 7 families, mean_reversion marked WATCH_only.
    sf = data.get("candidate_strategy_families")
    if not isinstance(sf, list):
        errors.append("candidate_strategy_families must be a list")
        sf = []
    sf_ids = {f.get("id") for f in sf if isinstance(f, dict)}
    for fid in REQUIRED_STRATEGY_FAMILY_IDS:
        if fid not in sf_ids:
            errors.append(f"candidate_strategy_families missing id: {fid}")
    mr = next((f for f in sf if isinstance(f, dict) and f.get("id") == "mean_reversion"), None)
    if mr is not None and mr.get("status") != "WATCH_only":
        errors.append(f"mean_reversion status must be 'WATCH_only' (got {mr.get('status')!r})")

    # Data requirements: all required keys present.
    dr = data.get("data_requirements")
    if not isinstance(dr, dict):
        errors.append("data_requirements must be a dict")
    else:
        for k in REQUIRED_DATA_REQ_KEYS:
            if k not in dr:
                errors.append(f"data_requirements missing key: {k}")
        if dr.get("ohlcv_daily_required") is not True:
            errors.append("data_requirements.ohlcv_daily_required must be True")
        if "UTC" not in str(dr.get("timezone_normalization", "")):
            errors.append("data_requirements.timezone_normalization must mention UTC")
        if "24/7" not in str(dr.get("session_handling", "")):
            errors.append("data_requirements.session_handling must mention '24/7'")

    # Validation phases: all P0..P8 markers present.
    vp = data.get("validation_phases")
    if not isinstance(vp, list) or not vp:
        errors.append("validation_phases must be a non-empty list")
    else:
        phase_ids = {p.get("phase") for p in vp if isinstance(p, dict)}
        for required in REQUIRED_VALIDATION_PHASES:
            if required not in phase_ids:
                errors.append(f"validation_phases missing phase: {required}")

    # pass_watch_fail_rules: PASS/WATCH/FAIL keys.
    pwf = data.get("pass_watch_fail_rules")
    if isinstance(pwf, dict):
        for k in ("PASS", "WATCH", "FAIL"):
            if k not in pwf:
                errors.append(f"pass_watch_fail_rules missing key: {k}")
    elif isinstance(pwf, list):
        joined = " ".join(str(x) for x in pwf)
        for k in ("PASS", "WATCH", "FAIL"):
            if k not in joined:
                errors.append(f"pass_watch_fail_rules missing marker: {k}")
    else:
        errors.append("pass_watch_fail_rules must be a dict or list")

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # safety_boundaries must mention research-only / no broker / no live / no order.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / PROTO_DIR_REL / PROTO_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"protocol.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"protocol.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"protocol.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"protocol_id:        {data.get('protocol_id')}")
    print(f"title:              {data.get('title')}")
    print(f"version:            {data.get('version')}")
    print(f"research_only:      {data.get('research_only')}")
    print(f"lane:               {data.get('lane')}")
    print(f"allowed_market_type:{data.get('allowed_market_type')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    tas = data.get("target_assets") or []
    print(f"target_assets ({len(tas)}):")
    for a in tas:
        if isinstance(a, dict):
            print(f"  - {a.get('symbol_canonical')}  {a.get('label')}")
    sf = data.get("candidate_strategy_families") or []
    print(f"candidate_strategy_families ({len(sf)}):")
    for f in sf:
        if isinstance(f, dict):
            print(f"  - {str(f.get('id', '?')):>30}  status={f.get('status')}")
    vp = data.get("validation_phases") or []
    print(f"validation_phases ({len(vp)}):")
    for p in vp:
        if isinstance(p, dict):
            print(f"  - {p.get('phase')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Protocol Memo validator (research-only)",
    )
    parser.add_argument("command", choices=("validate", "show"))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if args.command == "validate":
        ok, errs = validate(root)
        if ok:
            print("validate: OK")
            return 0
        print("validate: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 2
    if args.command == "show":
        return show(root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
