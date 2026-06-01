"""SPARTA Arbitrage Data Source Evaluation Memo — validator (research-only, stdlib).

Validates `reports/arbitrage_data_source_evaluation_v1/data_source_evaluation.json`
against the required schema and the hard safety contract:
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
  * all six required source classes are evaluated (A..F)
  * the decision matrix has every required field for every row
  * `allowed_now` is False for every real data-fetching source class
  * manually-copied (F) and web-scraped (E) sources are REJECTED for evidence
  * approval gates include explicit operator authorization
  * no profitability claim, no live-readiness claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_data_source_evaluation_check.py validate
  python tools/arbitrage_data_source_evaluation_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR_REL = "reports/arbitrage_data_source_evaluation_v1"
EVAL_JSON = "data_source_evaluation.json"
EVAL_MD = "data_source_evaluation.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "evaluation_id",
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
    "supported_arbitrage_categories",
    "evaluated_source_classes",
    "approval_gates",
    "rejection_rules",
    "required_metadata",
    "expected_risks",
    "source_quality_dimensions",
    "data_source_decision_matrix",
    "future_allowed_source_plan",
    "future_forbidden_source_plan",
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

REQUIRED_SOURCE_CLASS_IDS = (
    "A_exchange_public_historical_archives",
    "B_exchange_public_apis",
    "C_paid_market_data_vendors",
    "D_existing_local_csv_datasets",
    "E_web_scraped_or_unofficial_data",
    "F_manually_copied_prices_or_screenshots",
)

REQUIRED_MATRIX_FIELDS = (
    "source_class",
    "allowed_now",
    "future_possible",
    "requires_operator_authorization",
    "requires_manifest",
    "requires_QA",
    "supports_order_book",
    "supports_fees",
    "supports_funding",
    "timestamp_quality",
    "legal_tos_risk",
    "cost_risk",
    "evidence_quality",
    "recommended_status",
    "notes",
)

ALLOWED_RECOMMENDED_STATUSES = {"PREFERRED", "ACCEPTABLE", "WATCH", "REJECTED"}

# These classes must be REJECTED for evidence per the bundle's policy.
MUST_BE_REJECTED_FOR_EVIDENCE = {
    "E_web_scraped_or_unofficial_data",
    "F_manually_copied_prices_or_screenshots",
}

NON_EMPTY_LIST_SECTIONS = (
    "rejection_rules",
    "required_metadata",
    "expected_risks",
    "source_quality_dimensions",
    "future_allowed_source_plan",
    "future_forbidden_source_plan",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in markdown.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "REJECTED",
    "A data source does not imply edge",
    "Clean data does not imply profit",
    "Source approval does not authorize trading",
)

# Forbidden capability claims. Negative-framed safety language is intentionally
# not in this list (so a sentence like "does NOT authorize trading" can stand).
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
    p = repo_root / EVAL_DIR_REL / EVAL_JSON
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
        return False, ["data_source_evaluation.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Source classes: must contain all six.
    src_classes = data.get("evaluated_source_classes")
    if not isinstance(src_classes, list):
        errors.append("evaluated_source_classes must be a list")
        src_classes = []
    elif len(src_classes) < 6:
        errors.append("evaluated_source_classes must have at least 6 entries")
    ids_present = {c.get("id") for c in src_classes if isinstance(c, dict)}
    for cid in REQUIRED_SOURCE_CLASS_IDS:
        if cid not in ids_present:
            errors.append(f"required source class id missing: {cid}")

    # Decision matrix: required fields + every row well-formed.
    dm = data.get("data_source_decision_matrix")
    if not isinstance(dm, dict):
        errors.append("data_source_decision_matrix must be a dict")
    else:
        fields = dm.get("fields")
        if not isinstance(fields, list):
            errors.append("data_source_decision_matrix.fields must be a list")
        else:
            fset = set(fields)
            for f in REQUIRED_MATRIX_FIELDS:
                if f not in fset:
                    errors.append(f"decision matrix fields missing: {f}")
        rows = dm.get("rows")
        if not isinstance(rows, list) or not rows:
            errors.append("data_source_decision_matrix.rows must be a non-empty list")
        else:
            row_ids = set()
            for row in rows:
                if not isinstance(row, dict):
                    errors.append("non-dict decision matrix row")
                    continue
                for f in REQUIRED_MATRIX_FIELDS:
                    if f not in row:
                        errors.append(f"matrix row {row.get('source_class', '?')!r}: missing field {f}")
                # Validate recommended_status enum.
                rs = row.get("recommended_status")
                if rs not in ALLOWED_RECOMMENDED_STATUSES:
                    errors.append(f"matrix row {row.get('source_class', '?')!r}: invalid recommended_status {rs!r}")
                # allowed_now must be False for every real data-fetching source class.
                if row.get("allowed_now") is not False:
                    errors.append(f"matrix row {row.get('source_class', '?')!r}: allowed_now must be False (got {row.get('allowed_now')!r})")
                # Manually-copied + web-scraped must be REJECTED for evidence.
                sc = row.get("source_class")
                if sc in MUST_BE_REJECTED_FOR_EVIDENCE and rs != "REJECTED":
                    errors.append(f"matrix row {sc!r}: recommended_status must be REJECTED (got {rs!r})")
                row_ids.add(sc)
            for cid in REQUIRED_SOURCE_CLASS_IDS:
                if cid not in row_ids:
                    errors.append(f"decision matrix row missing for source class: {cid}")

    # Approval gates.
    ag = data.get("approval_gates")
    if isinstance(ag, dict):
        gates = ag.get("must_all_be_satisfied_before_any_future_data_collection")
        if not isinstance(gates, list) or not gates:
            errors.append("approval_gates.must_all_be_satisfied_before_any_future_data_collection must be a non-empty list")
        else:
            blob = " ".join(str(x) for x in gates).lower()
            for marker in ("explicit_operator_authorization", "exact_source_named", "data_contract_version_referenced", "dataset_manifest_version_referenced", "qa_harness_spec_version_referenced"):
                if marker not in blob:
                    errors.append(f"approval_gates missing marker: {marker}")
    else:
        errors.append("approval_gates must be a dict")

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # pass_watch_fail_rules.
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

    # safety_boundaries must mention research-only / no broker / no live / no order.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / EVAL_DIR_REL / EVAL_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"data_source_evaluation.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"data_source_evaluation.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # Also scan JSON text for forbidden phrases.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"data_source_evaluation.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"evaluation_id:   {data.get('evaluation_id')}")
    print(f"title:           {data.get('title')}")
    print(f"version:         {data.get('version')}")
    print(f"research_only:   {data.get('research_only')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    sc = data.get("evaluated_source_classes") or []
    print(f"source classes ({len(sc)}):")
    for c in sc:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>45}  {c.get('label')}")
    dm = data.get("data_source_decision_matrix") or {}
    rows = dm.get("rows") or []
    print(f"decision matrix rows: {len(rows)}")
    for r in rows:
        if isinstance(r, dict):
            print(f"  - {str(r.get('source_class', '?')):>45}  allowed_now={r.get('allowed_now')}  status={r.get('recommended_status')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Data Source Evaluation validator (research-only)",
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
