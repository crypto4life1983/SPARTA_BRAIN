"""SPARTA Crypto-D1 Data Contract -- validator (research-only, stdlib).

Validates `reports/crypto_d1_data_contract_v1/data_contract.json` against the
required schema and the hard safety contract:
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
  * lane == 'crypto_d1_protocol'
  * target_assets include BTC, ETH, SOL
  * allowed_market_type == 'spot'; perp_futures + dated_futures + options +
    leveraged in forbidden_market_types
  * timeframe.primary == '1d'; intraday is explicitly out of scope
  * required_columns include the 9 OHLCV+provenance columns
  * timestamp_requirements / ohlcv_requirements / session_requirements /
    missing_data_rules / duplicate_data_rules / fee_slippage_requirements are
    populated with the documented keys
  * pass_watch_fail_rules + safety_boundaries are non-empty
  * no profitability / live-readiness / backtest-authorize claim in either
    file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_data_contract_check.py validate
  python tools/crypto_d1_data_contract_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_DIR_REL = "reports/crypto_d1_data_contract_v1"
CONTRACT_JSON = "data_contract.json"
CONTRACT_MD = "data_contract.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "data_contract_id",
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
    "timeframe",
    "allowed_market_type",
    "forbidden_market_types",
    "required_columns",
    "optional_columns",
    "timestamp_requirements",
    "ohlcv_requirements",
    "volume_requirements",
    "timezone_requirements",
    "session_requirements",
    "symbol_mapping_requirements",
    "source_provenance_requirements",
    "missing_data_rules",
    "duplicate_data_rules",
    "data_quality_rules",
    "normalization_rules",
    "fee_slippage_requirements",
    "future_allowed_data_sources",
    "forbidden_data_sources_or_methods",
    "minimum_viable_dataset",
    "required_future_artifacts",
    "pass_watch_fail_rules",
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

REQUIRED_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "source",
    "quote_currency",
)

REQUIRED_TIMESTAMP_KEYS = (
    "primary_clock",
    "daily_bar_boundary",
    "session_handling",
    "missing_day_detection",
    "duplicate_timestamp_rejection",
    "daylight_saving_handling",
    "partial_day_bar_handling",
    "source_timestamp_vs_ingestion_timestamp",
)

REQUIRED_OHLCV_KEYS = (
    "high_rule",
    "low_rule",
    "open_close_positive",
    "high_positive",
    "low_positive",
    "volume_non_negative",
    "missing_close_invalid",
    "missing_timestamp_invalid",
    "duplicate_row_invalid",
    "zero_volume_rules",
    "extreme_gap_outlier_flag",
)

REQUIRED_FEE_SLIPPAGE_KEYS = (
    "spot_taker_fee_required",
    "spot_maker_fee_recorded_if_used",
    "fee_tier_assumption",
    "slippage_assumption",
    "spread_assumption_when_quote_data_absent",
    "stablecoin_quote_currency_assumption",
    "cost_sensitivity_checks_required_before_pass",
    "no_profitability_claim_if_fees_ignored",
)

REQUIRED_MISSING_DATA_KEYS = (
    "no_silent_forward_fill",
    "missing_day_flagged_in_manifest",
    "missing_close_invalid",
    "missing_timestamp_invalid",
)

REQUIRED_DUPLICATE_DATA_KEYS = (
    "duplicate_symbol_timestamp_rejected",
    "duplicate_row_rejected",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "required_columns",
    "future_allowed_data_sources",
    "forbidden_data_sources_or_methods",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "Crypto trend ideas are not profitable until tested",
    "A good historical chart does not imply future returns",
    "No backtest is authorized by this contract alone",
    "Clean OHLCV data does not imply profit",
    "24/7",
)

# Forbidden capability claims. Negative-framed safety language must remain
# expressible, so phrases that only ever appear in negative framings are not
# listed here.
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
    p = repo_root / CONTRACT_DIR_REL / CONTRACT_JSON
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
        return False, ["data_contract.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    if data.get("lane") != "crypto_d1_protocol":
        errors.append(f"lane must be 'crypto_d1_protocol' (got {data.get('lane')!r})")

    tas = data.get("target_assets")
    if not isinstance(tas, list) or not tas:
        errors.append("target_assets must be a non-empty list")
    else:
        canonical_set = {a.get("symbol_canonical") for a in tas if isinstance(a, dict)}
        for asset in REQUIRED_TARGET_ASSETS:
            if asset not in canonical_set:
                errors.append(f"target_assets missing required canonical symbol: {asset}")

    if data.get("allowed_market_type") != "spot":
        errors.append(f"allowed_market_type must be 'spot' (got {data.get('allowed_market_type')!r})")

    fmt = data.get("forbidden_market_types")
    if not isinstance(fmt, list) or not fmt:
        errors.append("forbidden_market_types must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in fmt).lower()
        for needle in ("perp", "dated_futures", "options", "leveraged"):
            if needle not in joined:
                errors.append(f"forbidden_market_types missing needle: {needle!r}")

    tf = data.get("timeframe")
    if not isinstance(tf, dict):
        errors.append("timeframe must be a dict")
    else:
        if tf.get("primary") != "1d":
            errors.append(f"timeframe.primary must be '1d' (got {tf.get('primary')!r})")
        if tf.get("intraday_explicitly_out_of_scope") is not True:
            errors.append("timeframe.intraday_explicitly_out_of_scope must be True")

    rc = data.get("required_columns")
    if not isinstance(rc, list) or not rc:
        errors.append("required_columns must be a non-empty list")
    else:
        rc_set = {str(c).strip().lower() for c in rc}
        for col in REQUIRED_COLUMNS:
            if col not in rc_set:
                errors.append(f"required_columns missing required column: {col}")

    oc = data.get("optional_columns")
    if not isinstance(oc, list):
        errors.append("optional_columns must be a list (may be empty)")

    ts = data.get("timestamp_requirements")
    if not isinstance(ts, dict):
        errors.append("timestamp_requirements must be a dict")
    else:
        for k in REQUIRED_TIMESTAMP_KEYS:
            if k not in ts:
                errors.append(f"timestamp_requirements missing key: {k}")
        if "UTC" not in str(ts.get("primary_clock", "")):
            errors.append("timestamp_requirements.primary_clock must be 'UTC'")
        if "24/7" not in str(ts.get("session_handling", "")):
            errors.append("timestamp_requirements.session_handling must mention '24/7'")

    oh = data.get("ohlcv_requirements")
    if not isinstance(oh, dict):
        errors.append("ohlcv_requirements must be a dict")
    else:
        for k in REQUIRED_OHLCV_KEYS:
            if k not in oh:
                errors.append(f"ohlcv_requirements missing key: {k}")
        if oh.get("volume_non_negative") is not True:
            errors.append("ohlcv_requirements.volume_non_negative must be True")
        if oh.get("missing_close_invalid") is not True:
            errors.append("ohlcv_requirements.missing_close_invalid must be True")
        if oh.get("duplicate_row_invalid") is not True:
            errors.append("ohlcv_requirements.duplicate_row_invalid must be True")
        if "max(open" not in str(oh.get("high_rule", "")):
            errors.append("ohlcv_requirements.high_rule must encode 'high >= max(open, close, low)'")
        if "min(open" not in str(oh.get("low_rule", "")):
            errors.append("ohlcv_requirements.low_rule must encode 'low <= min(open, close, high)'")

    sr = data.get("session_requirements")
    if not isinstance(sr, dict):
        errors.append("session_requirements must be a dict")
    else:
        if "24/7" not in str(sr.get("calendar", "")):
            errors.append("session_requirements.calendar must mention '24/7'")
        if sr.get("weekday_only_filters_forbidden") is not True:
            errors.append("session_requirements.weekday_only_filters_forbidden must be True")

    tz = data.get("timezone_requirements")
    if not isinstance(tz, dict):
        errors.append("timezone_requirements must be a dict")
    else:
        if "UTC" not in str(tz.get("storage_timezone", "")):
            errors.append("timezone_requirements.storage_timezone must be 'UTC'")
        if tz.get("iso8601_required") is not True:
            errors.append("timezone_requirements.iso8601_required must be True")

    md_rules = data.get("missing_data_rules")
    if not isinstance(md_rules, dict):
        errors.append("missing_data_rules must be a dict")
    else:
        for k in REQUIRED_MISSING_DATA_KEYS:
            if k not in md_rules:
                errors.append(f"missing_data_rules missing key: {k}")
        if md_rules.get("no_silent_forward_fill") is not True:
            errors.append("missing_data_rules.no_silent_forward_fill must be True")

    dup_rules = data.get("duplicate_data_rules")
    if not isinstance(dup_rules, dict):
        errors.append("duplicate_data_rules must be a dict")
    else:
        for k in REQUIRED_DUPLICATE_DATA_KEYS:
            if k not in dup_rules:
                errors.append(f"duplicate_data_rules missing key: {k}")
        if dup_rules.get("duplicate_symbol_timestamp_rejected") is not True:
            errors.append("duplicate_data_rules.duplicate_symbol_timestamp_rejected must be True")

    fs = data.get("fee_slippage_requirements")
    if not isinstance(fs, dict):
        errors.append("fee_slippage_requirements must be a dict")
    else:
        for k in REQUIRED_FEE_SLIPPAGE_KEYS:
            if k not in fs:
                errors.append(f"fee_slippage_requirements missing key: {k}")

    mvd = data.get("minimum_viable_dataset")
    if not isinstance(mvd, dict):
        errors.append("minimum_viable_dataset must be a dict")
    else:
        for k in ("frozen_sha256_required", "manifest_required",
                  "contract_version_pinned", "qa_report_required_before_use",
                  "is_window_sealed_before_run", "oos_window_sealed_before_run"):
            if mvd.get(k) is not True:
                errors.append(f"minimum_viable_dataset.{k} must be True")
        ar = mvd.get("assets_required") or []
        if not isinstance(ar, list) or "BTC" not in ar:
            errors.append("minimum_viable_dataset.assets_required must include 'BTC'")

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

    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    mpath = repo_root / CONTRACT_DIR_REL / CONTRACT_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"data_contract.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"data_contract.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"data_contract.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"data_contract_id:    {data.get('data_contract_id')}")
    print(f"title:               {data.get('title')}")
    print(f"version:             {data.get('version')}")
    print(f"research_only:       {data.get('research_only')}")
    print(f"lane:                {data.get('lane')}")
    print(f"allowed_market_type: {data.get('allowed_market_type')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    tas = data.get("target_assets") or []
    print(f"target_assets ({len(tas)}):")
    for a in tas:
        if isinstance(a, dict):
            print(f"  - {a.get('symbol_canonical')}  {a.get('label')}  required={a.get('required')}")
    rc = data.get("required_columns") or []
    print(f"required_columns ({len(rc)}):  {', '.join(str(c) for c in rc)}")
    oc = data.get("optional_columns") or []
    print(f"optional_columns ({len(oc)}):  {', '.join(str(c) for c in oc)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Data Contract validator (research-only)",
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
