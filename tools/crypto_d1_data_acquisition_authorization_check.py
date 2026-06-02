"""SPARTA Crypto-D1 Local Data Acquisition Authorization Plan -- validator.

Validates `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.json`
against the required schema and the hard safety contract:
  * research_only is True
  * seven execution / fetch / connection / backtest-execution /
    dataset-processing flags are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      backtest_execution_enabled
      dataset_processing_enabled
  * lane == 'crypto_d1_protocol'
  * target_assets include BTC, ETH, SOL
  * allowed_market_type == 'spot'; perp_futures + dated_futures + options +
    leveraged in forbidden_market_types
  * timeframe.primary == '1d'; intraday is explicitly out of scope
  * approved_data_scope declares spot / 1d / forbids perps + intraday
  * required_csv_schema.required_columns contains all 9 Bundle-12 fields
  * expected_file_layout documents the placeholder filenames + asserts
    no_real_files_created_in_this_bundle = True
  * approval_gates include operator authorization, manifest, CHECKSUMS,
    QA / freeze, no-credentials, no-paper/live-trading
  * manifest_requirements pin Bundle 11/12/13/14 versions
  * QA_freeze_requirements pin Bundle 14 spec + QA_PASS-or-approved-WARN
  * checksum_requirements declare sha256-per-file + FREEZE_RECORD format
  * forbidden_actions + allowed_next_steps + forbidden_next_steps non-empty
  * safety_boundaries carries research-only / no broker / no live / no order
  * no profitability / live-readiness / backtest-authorize claim in either file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_data_acquisition_authorization_check.py validate
  python tools/crypto_d1_data_acquisition_authorization_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR_REL = "reports/crypto_d1_data_acquisition_authorization_v1"
PLAN_JSON = "authorization_plan.json"
PLAN_MD = "authorization_plan.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "authorization_plan_id",
    "title",
    "version",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "lane",
    "target_assets",
    "timeframe",
    "allowed_market_type",
    "forbidden_market_types",
    "approved_data_scope",
    "operator_manual_steps",
    "required_csv_schema",
    "expected_file_layout",
    "storage_path_plan",
    "manifest_requirements",
    "QA_freeze_requirements",
    "checksum_requirements",
    "forbidden_actions",
    "approval_gates",
    "allowed_next_steps",
    "forbidden_next_steps",
    "required_future_artifacts",
    "safety_boundaries",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_CSV_COLUMNS = (
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

REQUIRED_FILE_LAYOUT_NEEDLES = (
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "qa_report.json",
)

# Phrases that EVERY approval gate set must collectively mention. These are
# substring matches against the lowercase joined approval_gates list.
REQUIRED_APPROVAL_GATE_NEEDLES = (
    "operator authorization",
    "manifest",
    "checksums.txt",
    "freeze_record.txt",
    "qa_report.json",
    "qa_status",
    "no credentials",
    "no live trading",
    "no paper",
    "no broker",
)

REQUIRED_QA_FREEZE_KEYS = (
    "must_follow",
    "qa_status_must_be",
    "qa_fail_blocks_runner_use",
    "qa_blocked_blocks_runner_use",
    "checks_required_in_qa_report",
    "no_lookahead_check_must_be_in_checks_passed",
)

REQUIRED_CHECKSUM_KEYS = (
    "sha256_per_file_required",
    "checksums_txt_format",
    "checksums_must_match_at_runner_startup",
    "freeze_record_txt_format",
    "file_hash_verification_before_runner_use",
)

REQUIRED_MANIFEST_REQ_KEYS = (
    "must_validate_against",
    "must_reference_protocol_version",
    "must_reference_data_contract_version",
    "must_reference_qa_freeze_spec_version",
    "must_reference_backtest_plan_version",
    "must_reference_runner_version",
    "dataset_id_naming_pattern",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "operator_manual_steps",
    "forbidden_actions",
    "approval_gates",
    "allowed_next_steps",
    "forbidden_next_steps",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "Data acquisition does not imply edge",
    "Clean data does not imply profit",
    "Running the backtest does not authorize trading",
    "Backtest output will still require separate review",
    "No paper/live trading is authorized",
    "No data fetch is authorized",
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
    p = repo_root / PLAN_DIR_REL / PLAN_JSON
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
        return False, ["authorization_plan.json is not a JSON object"]

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

    ads = data.get("approved_data_scope")
    if not isinstance(ads, dict):
        errors.append("approved_data_scope must be a dict")
    else:
        if ads.get("market_type") != "spot":
            errors.append("approved_data_scope.market_type must be 'spot'")
        if ads.get("timeframe") != "1d":
            errors.append("approved_data_scope.timeframe must be '1d'")
        if ads.get("perps_dated_options_leveraged_margin_FORBIDDEN") is not True:
            errors.append("approved_data_scope must FORBID perps/dated/options/leveraged/margin")
        if ads.get("intraday_FORBIDDEN_in_this_bundle") is not True:
            errors.append("approved_data_scope must FORBID intraday in this bundle")
        assets = ads.get("assets") or []
        for a in REQUIRED_TARGET_ASSETS:
            if a not in assets:
                errors.append(f"approved_data_scope.assets missing: {a}")

    rcs = data.get("required_csv_schema")
    if not isinstance(rcs, dict):
        errors.append("required_csv_schema must be a dict")
    else:
        rc = rcs.get("required_columns")
        if not isinstance(rc, list) or not rc:
            errors.append("required_csv_schema.required_columns must be a non-empty list")
        else:
            rc_set = {str(c).strip().lower() for c in rc}
            for col in REQUIRED_CSV_COLUMNS:
                if col not in rc_set:
                    errors.append(f"required_csv_schema.required_columns missing: {col}")

    efl = data.get("expected_file_layout")
    if not isinstance(efl, dict):
        errors.append("expected_file_layout must be a dict")
    else:
        joined = json.dumps(efl, ensure_ascii=False)
        for needle in REQUIRED_FILE_LAYOUT_NEEDLES:
            if needle not in joined:
                errors.append(f"expected_file_layout missing reference to {needle!r}")
        if efl.get("no_real_files_created_in_this_bundle") is not True:
            errors.append("expected_file_layout.no_real_files_created_in_this_bundle must be True")
        if efl.get("no_data_directory_created_in_this_bundle") is not True:
            errors.append("expected_file_layout.no_data_directory_created_in_this_bundle must be True")

    spp = data.get("storage_path_plan")
    if not isinstance(spp, dict):
        errors.append("storage_path_plan must be a dict")
    else:
        rp = str(spp.get("root_pattern", ""))
        if "data/crypto_d1_research" not in rp:
            errors.append("storage_path_plan.root_pattern must start with 'data/crypto_d1_research'")
        if spp.get("no_real_storage_directory_created_in_this_bundle") is not True:
            errors.append("storage_path_plan.no_real_storage_directory_created_in_this_bundle must be True")
        if spp.get("no_urls_required_local_only") is not True:
            errors.append("storage_path_plan.no_urls_required_local_only must be True")

    mr = data.get("manifest_requirements")
    if not isinstance(mr, dict):
        errors.append("manifest_requirements must be a dict")
    else:
        for k in REQUIRED_MANIFEST_REQ_KEYS:
            if k not in mr:
                errors.append(f"manifest_requirements missing key: {k}")

    qa = data.get("QA_freeze_requirements")
    if not isinstance(qa, dict):
        errors.append("QA_freeze_requirements must be a dict")
    else:
        for k in REQUIRED_QA_FREEZE_KEYS:
            if k not in qa:
                errors.append(f"QA_freeze_requirements missing key: {k}")
        if qa.get("qa_fail_blocks_runner_use") is not True:
            errors.append("QA_freeze_requirements.qa_fail_blocks_runner_use must be True")
        if qa.get("qa_blocked_blocks_runner_use") is not True:
            errors.append("QA_freeze_requirements.qa_blocked_blocks_runner_use must be True")
        if qa.get("no_lookahead_check_must_be_in_checks_passed") is not True:
            errors.append("QA_freeze_requirements.no_lookahead_check_must_be_in_checks_passed must be True")

    cs = data.get("checksum_requirements")
    if not isinstance(cs, dict):
        errors.append("checksum_requirements must be a dict")
    else:
        for k in REQUIRED_CHECKSUM_KEYS:
            if k not in cs:
                errors.append(f"checksum_requirements missing key: {k}")
        if cs.get("sha256_per_file_required") is not True:
            errors.append("checksum_requirements.sha256_per_file_required must be True")
        if cs.get("file_hash_verification_before_runner_use") is not True:
            errors.append("checksum_requirements.file_hash_verification_before_runner_use must be True")

    gates = data.get("approval_gates")
    if not isinstance(gates, list) or not gates:
        errors.append("approval_gates must be a non-empty list")
    else:
        joined = " ".join(str(g) for g in gates).lower()
        for needle in REQUIRED_APPROVAL_GATE_NEEDLES:
            if needle not in joined:
                errors.append(f"approval_gates missing required phrase: {needle!r}")

    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    mpath = repo_root / PLAN_DIR_REL / PLAN_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"authorization_plan.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"authorization_plan.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"authorization_plan.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"authorization_plan_id: {data.get('authorization_plan_id')}")
    print(f"title:                 {data.get('title')}")
    print(f"version:               {data.get('version')}")
    print(f"research_only:         {data.get('research_only')}")
    print(f"lane:                  {data.get('lane')}")
    print(f"allowed_market_type:   {data.get('allowed_market_type')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    tas = data.get("target_assets") or []
    print(f"target_assets ({len(tas)}):")
    for a in tas:
        if isinstance(a, dict):
            print(f"  - {a.get('symbol_canonical')}  {a.get('label')}  required={a.get('required')}")
    rcs = data.get("required_csv_schema") or {}
    rc = rcs.get("required_columns") or []
    print(f"required_csv_schema.required_columns ({len(rc)}):  {', '.join(str(c) for c in rc)}")
    steps = data.get("operator_manual_steps") or []
    print(f"operator_manual_steps ({len(steps)})")
    gates = data.get("approval_gates") or []
    print(f"approval_gates ({len(gates)})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Local Data Acquisition Authorization validator (research-only)",
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
