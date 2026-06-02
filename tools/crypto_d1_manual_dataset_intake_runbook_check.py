"""SPARTA Crypto-D1 Manual Dataset Intake Runbook -- validator (research-only, stdlib).

Validates `reports/crypto_d1_manual_dataset_intake_runbook_v1/runbook.json`
against the required schema and the hard safety contract:
  * research_only is True
  * the execution / fetch / connection / order / backtest-execution /
    dataset-processing / scheduler / network / credential flags are False
  * lane == 'crypto_d1_protocol'
  * target_assets == BTC, ETH, SOL; allowed_market_type == 'spot';
    timeframe == '1d'; session_calendar == '24/7'
  * required_csv_columns are the 9 canonical Bundle-12 columns
  * authorization_disclaimer pins the six "authorizes nothing" booleans
  * operator_decisions_before_data_enters non-empty
  * source_class_dispositions cover all 6 Bundle-18 classes with E + F rejected
  * required_concrete_inputs cover the mandated fields
  * qa_cli_commands carry the three Bundle-19 commands
  * qa_status_meanings carry all 6 QA statuses
  * forbidden_list covers the mandated forbidden categories
  * safety_boundaries / no_profit_claim_policy non-empty lists
  * MD carries required distinction phrases
  * no profitability / live-readiness / fetch-authorize claim in either file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_manual_dataset_intake_runbook_check.py validate
  python tools/crypto_d1_manual_dataset_intake_runbook_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNBOOK_DIR_REL = "reports/crypto_d1_manual_dataset_intake_runbook_v1"
RUNBOOK_JSON = "runbook.json"
RUNBOOK_MD = "runbook.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "runbook_id",
    "title",
    "version",
    "kind",
    "read_only",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "order_placement_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "scheduler_enabled",
    "network_calls_enabled",
    "credentials_required",
    "lane",
    "companion_documents",
    "runbook_objective",
    "authorization_disclaimer",
    "target_assets",
    "allowed_market_type",
    "timeframe",
    "session_calendar",
    "required_csv_columns",
    "operator_decisions_before_data_enters",
    "source_class_dispositions",
    "required_concrete_inputs",
    "file_placement_procedure",
    "qa_cli_commands",
    "qa_status_meanings",
    "why_qa_pass_authorizes_nothing",
    "post_qa_before_baseline_results",
    "forbidden_list",
    "pipeline_safety_repeatable_auditable",
    "candidate_registry_status_after_doc",
    "safety_boundaries",
    "no_profit_claim_policy",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "order_placement_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "scheduler_enabled",
    "network_calls_enabled",
    "credentials_required",
)

REQUIRED_DISCLAIMER_FLAGS = (
    "authorizes_nothing_operational",
    "does_not_authorize_fetching",
    "does_not_authorize_qa_on_real_data_by_itself",
    "qa_pass_does_not_authorize_automatic_backtesting",
    "qa_pass_does_not_authorize_paper_trading",
    "qa_pass_does_not_authorize_live_trading",
    "real_data_enters_only_through_explicit_operator_action_and_bundle_17_gates",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_CSV_COLUMNS = (
    "timestamp", "open", "high", "low", "close", "volume",
    "symbol", "source", "quote_currency",
)

REQUIRED_SOURCE_CLASS_IDS = (
    "A_exchange_public_historical_archives",
    "B_exchange_public_apis",
    "C_paid_market_data_vendors",
    "D_existing_local_OHLCV_files",
    "E_web_scraped_or_unofficial_tables",
    "F_manually_copied_prices_or_screenshots",
)

REQUIRED_QA_STATUSES = (
    "QA_DRAFT", "QA_PASS", "QA_WARN", "QA_FAIL", "QA_BLOCKED", "QA_RETIRED",
)

REQUIRED_QA_CLI_KEYS = ("validate_spec", "show_spec", "run")

REQUIRED_CONCRETE_INPUT_FIELDS = (
    "source_name",
    "source_class",
    "license_or_tos_reference",
    "assets",
    "market_type",
    "timeframe",
    "date_range",
    "file_naming_convention",
    "storage_path",
    "dataset_id",
    "dataset_version",
    "sha256_checksums",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees_slippage_declaration",
)

NON_EMPTY_LIST_SECTIONS = (
    "operator_decisions_before_data_enters",
    "required_concrete_inputs",
    "file_placement_procedure",
    "why_qa_pass_authorizes_nothing",
    "post_qa_before_baseline_results",
    "forbidden_list",
    "pipeline_safety_repeatable_auditable",
    "safety_boundaries",
    "no_profit_claim_policy",
)

# Forbidden-list category needles (lowercased).
FORBIDDEN_LIST_NEEDLES = (
    "perp",
    "leverage",
    "intraday",
    "scraping",
    "screenshot",
    "broker",
    "credentials",
    "network automation",
)

# Distinction phrases that must appear in the markdown for word discipline.
# The first 8 entries are the verbatim "must clearly state" statements
# required by the Bundle 20 spec; the trailing "24/7" entry is a separate
# 24/7-calendar guarantee that this validator has enforced since v1.
DISTINCTION_PHRASES = (
    "A runbook is a procedure, not an authorization",
    "No data fetch is authorized by this runbook",
    "Real data may enter only through explicit operator action and Bundle 17 gates",
    "QA_PASS does not authorize live trading",
    "QA_PASS does not authorize paper trading",
    "QA_PASS does not authorize automatic backtesting",
    "Crypto trend ideas are not profitable until tested",
    "A good historical chart does not imply future returns",
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
    p = repo_root / RUNBOOK_DIR_REL / RUNBOOK_JSON
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
        return False, ["runbook.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")
    if data.get("read_only") is not True:
        errors.append("read_only must be True")

    if data.get("lane") != "crypto_d1_protocol":
        errors.append(f"lane must be 'crypto_d1_protocol' (got {data.get('lane')!r})")

    tas = data.get("target_assets")
    if not isinstance(tas, list) or not tas:
        errors.append("target_assets must be a non-empty list")
    else:
        for asset in REQUIRED_TARGET_ASSETS:
            if asset not in tas:
                errors.append(f"target_assets missing required symbol: {asset}")

    if data.get("allowed_market_type") != "spot":
        errors.append(f"allowed_market_type must be 'spot' (got {data.get('allowed_market_type')!r})")
    if data.get("timeframe") != "1d":
        errors.append(f"timeframe must be '1d' (got {data.get('timeframe')!r})")
    if str(data.get("session_calendar")) != "24/7":
        errors.append(f"session_calendar must be '24/7' (got {data.get('session_calendar')!r})")

    cols = data.get("required_csv_columns")
    if not isinstance(cols, list):
        errors.append("required_csv_columns must be a list")
    else:
        for c in REQUIRED_CSV_COLUMNS:
            if c not in cols:
                errors.append(f"required_csv_columns missing column: {c}")

    disc = data.get("authorization_disclaimer")
    if not isinstance(disc, dict):
        errors.append("authorization_disclaimer must be a dict")
    else:
        for flag in REQUIRED_DISCLAIMER_FLAGS:
            if disc.get(flag) is not True:
                errors.append(f"authorization_disclaimer.{flag} must be True (got {disc.get(flag)!r})")
        if not str(disc.get("statement", "")).strip():
            errors.append("authorization_disclaimer.statement must be a non-empty string")

    # source_class_dispositions: all 6 classes present; E + F rejected.
    scd = data.get("source_class_dispositions")
    present_ids = set()
    rejected_ids = set()
    if not isinstance(scd, dict):
        errors.append("source_class_dispositions must be a dict")
    else:
        for bucket in ("preferred", "acceptable", "watch", "rejected"):
            entries = scd.get(bucket)
            if not isinstance(entries, list):
                errors.append(f"source_class_dispositions.{bucket} must be a list")
                continue
            for e in entries:
                if isinstance(e, dict) and e.get("id"):
                    present_ids.add(e["id"])
                    if bucket == "rejected":
                        rejected_ids.add(e["id"])
        for cid in REQUIRED_SOURCE_CLASS_IDS:
            if cid not in present_ids:
                errors.append(f"source_class_dispositions missing class: {cid}")
        for cid in ("E_web_scraped_or_unofficial_tables",
                    "F_manually_copied_prices_or_screenshots"):
            if cid not in rejected_ids:
                errors.append(f"source class {cid} must be in the 'rejected' bucket")

    # required_concrete_inputs cover the mandated fields.
    rci = data.get("required_concrete_inputs")
    if not isinstance(rci, list):
        errors.append("required_concrete_inputs must be a list")
    else:
        rci_fields = {e.get("field") for e in rci if isinstance(e, dict)}
        for fld in REQUIRED_CONCRETE_INPUT_FIELDS:
            if fld not in rci_fields:
                errors.append(f"required_concrete_inputs missing field: {fld}")

    # qa_cli_commands carry the three Bundle-19 commands.
    cli = data.get("qa_cli_commands")
    if not isinstance(cli, dict):
        errors.append("qa_cli_commands must be a dict")
    else:
        for k in REQUIRED_QA_CLI_KEYS:
            if not str(cli.get(k, "")).strip():
                errors.append(f"qa_cli_commands missing command: {k}")
        run_cmd = str(cli.get("run", ""))
        if "--dataset-dir" not in run_cmd or "--out-dir" not in run_cmd:
            errors.append("qa_cli_commands.run must reference --dataset-dir and --out-dir")

    # qa_status_meanings carry all 6 QA statuses.
    qsm = data.get("qa_status_meanings")
    if not isinstance(qsm, dict):
        errors.append("qa_status_meanings must be a dict")
    else:
        for st in REQUIRED_QA_STATUSES:
            if st not in qsm:
                errors.append(f"qa_status_meanings missing status: {st}")

    # forbidden_list covers mandated categories.
    fl = data.get("forbidden_list")
    if not isinstance(fl, list) or not fl:
        errors.append("forbidden_list must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in fl).lower()
        for needle in FORBIDDEN_LIST_NEEDLES:
            if needle not in joined:
                errors.append(f"forbidden_list missing category: {needle!r}")

    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    crs = data.get("candidate_registry_status_after_doc")
    if not isinstance(crs, dict):
        errors.append("candidate_registry_status_after_doc must be a dict")
    else:
        if crs.get("status") != "WATCH":
            errors.append("candidate_registry_status_after_doc.status must be 'WATCH'")
        if crs.get("evidence_level") == "STRONG":
            errors.append("candidate_registry_status_after_doc.evidence_level must NOT be STRONG")

    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no data fetch"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    mpath = repo_root / RUNBOOK_DIR_REL / RUNBOOK_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"runbook.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"runbook.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"runbook.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"runbook_id:          {data.get('runbook_id')}")
    print(f"title:               {data.get('title')}")
    print(f"version:             {data.get('version')}")
    print(f"research_only:       {data.get('research_only')}")
    print(f"lane:                {data.get('lane')}")
    print(f"allowed_market_type: {data.get('allowed_market_type')}")
    print(f"timeframe:           {data.get('timeframe')}")
    print(f"session_calendar:    {data.get('session_calendar')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    disc = data.get("authorization_disclaimer") or {}
    print("authorization_disclaimer (must all be True):")
    for f in REQUIRED_DISCLAIMER_FLAGS:
        print(f"  {f}: {disc.get(f)}")
    qsm = data.get("qa_status_meanings") or {}
    print(f"qa_status_meanings ({len(qsm)}): {', '.join(sorted(qsm))}")
    crs = data.get("candidate_registry_status_after_doc") or {}
    print(f"registry status: {crs.get('status')}  evidence_level: {crs.get('evidence_level')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Manual Dataset Intake Runbook validator (research-only)",
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
