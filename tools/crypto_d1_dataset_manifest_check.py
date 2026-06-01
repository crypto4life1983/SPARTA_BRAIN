"""SPARTA Crypto-D1 Dataset Manifest -- validator (research-only, stdlib).

Validates `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.json`
against the required schema and the hard safety contract:
  * research_only is True
  * seven execution / fetch / connection / backtest / dataset-processing
    flags are False:
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
  * manifest_schema.required_fields contains all 35 future manifest fields
  * qa_status_model contains DRAFT/FROZEN/QA_PASS/QA_WARN/QA_FAIL/RETIRED/BLOCKED
  * allowed_file_formats mentions CSV, Parquet, JSON manifest, Markdown report
  * forbidden_inputs is a non-empty list
  * freeze rules require UTC daily bars + forbid weekday-only calendars
  * pass_watch_fail_rules + safety_boundaries are non-empty
  * no profitability / live-readiness / backtest-authorize claim in either
    file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_dataset_manifest_check.py validate
  python tools/crypto_d1_dataset_manifest_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR_REL = "reports/crypto_d1_dataset_manifest_v1"
MANIFEST_JSON = "dataset_manifest.json"
MANIFEST_MD = "dataset_manifest.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "dataset_manifest_id",
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
    "manifest_schema",
    "dataset_identity_fields",
    "source_fields",
    "symbol_fields",
    "time_range_fields",
    "timestamp_fields",
    "OHLCV_fields",
    "fee_slippage_fields",
    "provenance_fields",
    "normalization_fields",
    "data_quality_fields",
    "freeze_fields",
    "validation_fields",
    "qa_status_model",
    "allowed_file_formats",
    "forbidden_inputs",
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

REQUIRED_FUTURE_MANIFEST_FIELDS = (
    "dataset_id",
    "dataset_version",
    "created_at",
    "created_by",
    "research_lane",
    "market_type",
    "assets",
    "symbols",
    "quote_currency",
    "timeframe",
    "time_start",
    "time_end",
    "timezone",
    "bar_boundary",
    "data_frequency",
    "source_type",
    "source_name",
    "source_location",
    "data_contract_version",
    "protocol_version",
    "checksum_policy",
    "row_count_expected",
    "row_count_actual",
    "missing_day_policy",
    "duplicate_policy",
    "partial_day_policy",
    "zero_volume_policy",
    "outlier_policy",
    "normalization_policy",
    "fee_slippage_assumption_reference",
    "freeze_status",
    "QA_status",
    "allowed_use",
    "forbidden_use",
    "notes",
)

REQUIRED_QA_STATUSES = (
    "DRAFT",
    "FROZEN",
    "QA_PASS",
    "QA_WARN",
    "QA_FAIL",
    "RETIRED",
    "BLOCKED",
)

REQUIRED_ALLOWED_FILE_FORMAT_NEEDLES = (
    "CSV",
    "Parquet",
    "JSON manifest",
    "Markdown report",
)

REQUIRED_FREEZE_KEYS = (
    "no_mutable_data_in_backtest",
    "manifest_required",
    "manifest_passes_validation_required",
    "data_contract_version_referenced",
    "protocol_version_referenced",
    "qa_status_required",
    "future_backtest_must_cite_dataset_id_and_version",
    "data_change_creates_new_dataset_version",
    "manual_edits_invalid_unless_documented_and_revalidated",
    "daily_bars_must_be_utc_normalized",
    "weekday_only_calendars_forbidden",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "allowed_file_formats",
    "forbidden_inputs",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "Dataset manifest approval does not imply edge",
    "QA_PASS does not imply profitability",
    "Clean daily OHLCV data does not imply profit",
    "A manifest cannot authorize backtesting by itself",
    "A manifest cannot authorize paper or live trading",
    "Crypto trend ideas are not profitable until tested",
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
    p = repo_root / MANIFEST_DIR_REL / MANIFEST_JSON
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
        return False, ["dataset_manifest.json is not a JSON object"]

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

    ms = data.get("manifest_schema")
    if not isinstance(ms, dict):
        errors.append("manifest_schema must be a dict")
    else:
        rf = ms.get("required_fields")
        if not isinstance(rf, list) or not rf:
            errors.append("manifest_schema.required_fields must be a non-empty list")
        else:
            rf_set = set(rf)
            for fld in REQUIRED_FUTURE_MANIFEST_FIELDS:
                if fld not in rf_set:
                    errors.append(f"manifest_schema.required_fields missing future field: {fld}")
        # field_count must equal the count of required fields actually listed
        if isinstance(rf, list) and ms.get("field_count") is not None:
            try:
                if int(ms.get("field_count")) != len(rf):
                    errors.append(
                        f"manifest_schema.field_count ({ms.get('field_count')}) "
                        f"does not match len(required_fields) ({len(rf)})"
                    )
            except (TypeError, ValueError):
                errors.append("manifest_schema.field_count must be an integer")

    qa = data.get("qa_status_model")
    if not isinstance(qa, dict):
        errors.append("qa_status_model must be a dict")
    else:
        for status in REQUIRED_QA_STATUSES:
            if status not in qa:
                errors.append(f"qa_status_model missing status: {status}")

    afm = data.get("allowed_file_formats")
    if not isinstance(afm, list) or not afm:
        errors.append("allowed_file_formats must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in afm)
        for needle in REQUIRED_ALLOWED_FILE_FORMAT_NEEDLES:
            if needle not in joined:
                errors.append(f"allowed_file_formats missing format needle: {needle!r}")

    fi = data.get("forbidden_inputs")
    if not isinstance(fi, list) or not fi:
        errors.append("forbidden_inputs must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in fi).lower()
        for needle in ("screenshot", "manually copied", "scraped", "without provenance",
                       "without checksums", "without a manifest", "credentials"):
            if needle not in joined:
                errors.append(f"forbidden_inputs missing needle: {needle!r}")

    fr = data.get("freeze_fields")
    if not isinstance(fr, dict):
        errors.append("freeze_fields must be a dict")
    else:
        for k in REQUIRED_FREEZE_KEYS:
            if k not in fr:
                errors.append(f"freeze_fields missing key: {k}")
        if fr.get("daily_bars_must_be_utc_normalized") is not True:
            errors.append("freeze_fields.daily_bars_must_be_utc_normalized must be True")
        if fr.get("weekday_only_calendars_forbidden") is not True:
            errors.append("freeze_fields.weekday_only_calendars_forbidden must be True")

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

    mpath = repo_root / MANIFEST_DIR_REL / MANIFEST_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"dataset_manifest.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"dataset_manifest.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"dataset_manifest.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"dataset_manifest_id: {data.get('dataset_manifest_id')}")
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
    ms = data.get("manifest_schema") or {}
    rf = ms.get("required_fields") or []
    print(f"manifest_schema.required_fields ({len(rf)}):")
    for fld in rf:
        print(f"  - {fld}")
    qa = data.get("qa_status_model") or {}
    print(f"qa_status_model ({len(qa)}):  {', '.join(qa.keys())}")
    afm = data.get("allowed_file_formats") or []
    print(f"allowed_file_formats ({len(afm)}):")
    for f in afm:
        print(f"  - {f}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Dataset Manifest validator (research-only)",
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
