"""SPARTA Crypto-D1 Data QA / Freeze Spec -- validator (research-only, stdlib).

Validates `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.json` against
the required schema and the hard safety contract:
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
  * QA_check_groups contain A_manifest_integrity / B_timestamp / C_OHLCV /
    D_volume / E_symbol_source / F_fee_slippage / G_freeze
  * each per-group check section (timestamp_QA_checks / OHLCV_QA_checks / ...)
    is a populated dict
  * QA_status_model contains DRAFT/PASS/WARN/FAIL/BLOCKED/RETIRED (qa-prefixed)
  * QA_report_schema.required_fields contains all 26 future report fields
  * freeze_rules require frozen data / checksums / dataset version / UTC
    daily bars / no weekday-only calendars
  * allowed_next_steps + forbidden_next_steps are non-empty lists
  * pass_watch_fail_rules + safety_boundaries are non-empty
  * no profitability / live-readiness / backtest-authorize claim in either
    file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_qa_freeze_spec_check.py validate
  python tools/crypto_d1_qa_freeze_spec_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR_REL = "reports/crypto_d1_qa_freeze_spec_v1"
SPEC_JSON = "qa_freeze_spec.json"
SPEC_MD = "qa_freeze_spec.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "qa_freeze_spec_id",
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
    "required_inputs",
    "forbidden_inputs",
    "QA_check_groups",
    "timestamp_QA_checks",
    "OHLCV_QA_checks",
    "volume_QA_checks",
    "symbol_QA_checks",
    "source_provenance_QA_checks",
    "fee_slippage_QA_checks",
    "missing_data_QA_checks",
    "duplicate_data_QA_checks",
    "outlier_QA_checks",
    "freeze_rules",
    "QA_status_model",
    "QA_report_schema",
    "allowed_next_steps",
    "forbidden_next_steps",
    "pass_watch_fail_rules",
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

REQUIRED_QA_CHECK_GROUPS = (
    "A_manifest_integrity",
    "B_timestamp",
    "C_OHLCV",
    "D_volume",
    "E_symbol_source",
    "F_fee_slippage",
    "G_freeze",
)

# Per-group check sections that must exist as populated dicts.
REQUIRED_PER_GROUP_DICT_SECTIONS = (
    "timestamp_QA_checks",
    "OHLCV_QA_checks",
    "volume_QA_checks",
    "symbol_QA_checks",
    "source_provenance_QA_checks",
    "fee_slippage_QA_checks",
    "missing_data_QA_checks",
    "duplicate_data_QA_checks",
    "outlier_QA_checks",
)

REQUIRED_QA_STATUSES = (
    "QA_DRAFT",
    "QA_PASS",
    "QA_WARN",
    "QA_FAIL",
    "QA_BLOCKED",
    "QA_RETIRED",
)

REQUIRED_QA_REPORT_FIELDS = (
    "qa_report_id",
    "dataset_id",
    "dataset_version",
    "manifest_version",
    "data_contract_version",
    "protocol_version",
    "generated_at",
    "qa_status",
    "checks_run",
    "checks_passed",
    "checks_warned",
    "checks_failed",
    "blocking_failures",
    "warnings",
    "row_count_observed",
    "missing_day_summary",
    "duplicate_summary",
    "timestamp_summary",
    "OHLCV_summary",
    "volume_summary",
    "fee_slippage_summary",
    "source_provenance_summary",
    "freeze_summary",
    "allowed_next_step",
    "forbidden_next_steps",
    "safety_flags",
)

REQUIRED_FREEZE_RULE_KEYS = (
    "no_mutable_data_in_backtest",
    "manifest_required",
    "qa_pass_or_approved_qa_warn_required_before_use",
    "protocol_version_referenced",
    "data_contract_version_referenced",
    "manifest_version_referenced",
    "checksums_required",
    "row_counts_recorded_required",
    "freeze_timestamp_required",
    "future_backtest_must_cite_dataset_id_and_version",
    "data_change_creates_new_dataset_version",
    "manual_edits_invalid_unless_documented_and_revalidated",
    "daily_bars_must_be_utc_normalized",
    "weekday_only_calendars_forbidden",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "required_inputs",
    "forbidden_inputs",
    "allowed_next_steps",
    "forbidden_next_steps",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "QA is not strategy validation",
    "QA_PASS does not imply edge",
    "QA_PASS does not imply profitability",
    "Clean daily OHLCV data does not imply profit",
    "A QA report cannot authorize paper or live trading",
    "A QA report cannot authorize backtesting by itself",
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
    p = repo_root / SPEC_DIR_REL / SPEC_JSON
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
        return False, ["qa_freeze_spec.json is not a JSON object"]

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

    cg = data.get("QA_check_groups")
    if not isinstance(cg, dict):
        errors.append("QA_check_groups must be a dict")
    else:
        for grp in REQUIRED_QA_CHECK_GROUPS:
            if grp not in cg:
                errors.append(f"QA_check_groups missing group: {grp}")

    for section in REQUIRED_PER_GROUP_DICT_SECTIONS:
        v = data.get(section)
        if not isinstance(v, dict) or not v:
            errors.append(f"section {section} must be a non-empty dict")

    qa = data.get("QA_status_model")
    if not isinstance(qa, dict):
        errors.append("QA_status_model must be a dict")
    else:
        for status in REQUIRED_QA_STATUSES:
            if status not in qa:
                errors.append(f"QA_status_model missing status: {status}")

    qrs = data.get("QA_report_schema")
    if not isinstance(qrs, dict):
        errors.append("QA_report_schema must be a dict")
    else:
        rf = qrs.get("required_fields")
        if not isinstance(rf, list) or not rf:
            errors.append("QA_report_schema.required_fields must be a non-empty list")
        else:
            rf_set = set(rf)
            for fld in REQUIRED_QA_REPORT_FIELDS:
                if fld not in rf_set:
                    errors.append(f"QA_report_schema.required_fields missing field: {fld}")
        if isinstance(rf, list) and qrs.get("field_count") is not None:
            try:
                if int(qrs.get("field_count")) != len(rf):
                    errors.append(
                        f"QA_report_schema.field_count ({qrs.get('field_count')}) "
                        f"does not match len(required_fields) ({len(rf)})"
                    )
            except (TypeError, ValueError):
                errors.append("QA_report_schema.field_count must be an integer")

    fr = data.get("freeze_rules")
    if not isinstance(fr, dict):
        errors.append("freeze_rules must be a dict")
    else:
        for k in REQUIRED_FREEZE_RULE_KEYS:
            if k not in fr:
                errors.append(f"freeze_rules missing key: {k}")
        if fr.get("daily_bars_must_be_utc_normalized") is not True:
            errors.append("freeze_rules.daily_bars_must_be_utc_normalized must be True")
        if fr.get("weekday_only_calendars_forbidden") is not True:
            errors.append("freeze_rules.weekday_only_calendars_forbidden must be True")

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

    mpath = repo_root / SPEC_DIR_REL / SPEC_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"qa_freeze_spec.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"qa_freeze_spec.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"qa_freeze_spec.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"qa_freeze_spec_id:   {data.get('qa_freeze_spec_id')}")
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
    cg = data.get("QA_check_groups") or {}
    print(f"QA_check_groups ({len(cg)}):  {', '.join(cg.keys())}")
    qa = data.get("QA_status_model") or {}
    print(f"QA_status_model ({len(qa)}):  {', '.join(qa.keys())}")
    qrs = data.get("QA_report_schema") or {}
    rf = qrs.get("required_fields") or []
    print(f"QA_report_schema.required_fields ({len(rf)})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Data QA / Freeze Spec validator (research-only)",
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
