"""SPARTA Arbitrage QA Harness Spec — validator (research-only, stdlib).

Validates `reports/arbitrage_qa_harness_spec_v1/qa_harness_spec.json` against
the required schema and the hard safety contract:
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
  * the five required arbitrage categories are present with category-specific
    QA checks
  * all 8 QA check groups (A_manifest_integrity .. H_anomaly_detection) are
    documented
  * the QA status model contains all 6 required statuses (QA_DRAFT/QA_PASS/
    QA_WARN/QA_FAIL/QA_BLOCKED/QA_RETIRED)
  * the report schema lists every required future QA report field
  * the pure-arbitrage / statistical-relative-value distinction is preserved
  * no profitability claim, no live-readiness claim, no backtest-authorize claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_qa_harness_spec_check.py validate
  python tools/arbitrage_qa_harness_spec_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR_REL = "reports/arbitrage_qa_harness_spec_v1"
SPEC_JSON = "qa_harness_spec.json"
SPEC_MD = "qa_harness_spec.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "qa_harness_spec_id",
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
    "required_inputs",
    "forbidden_inputs",
    "qa_check_groups",
    "category_specific_qa_checks",
    "manifest_validation_checks",
    "timestamp_qa_checks",
    "quote_qa_checks",
    "order_book_qa_checks",
    "trade_print_qa_checks",
    "fee_funding_qa_checks",
    "liquidity_qa_checks",
    "latency_qa_checks",
    "provenance_qa_checks",
    "normalization_qa_checks",
    "anomaly_detection_checks",
    "qa_status_rules",
    "report_schema",
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

REQUIRED_CATEGORY_IDS = (
    "cross_exchange_spot",
    "spot_perp_basis_funding",
    "triangular",
    "futures_calendar",
    "statistical_relative_value",
)

REQUIRED_CATEGORY_FIELDS = (
    "id",
    "label",
    "category_specific_qa_checks",
)

REQUIRED_QA_CHECK_GROUPS = (
    "A_manifest_integrity",
    "B_timestamp_and_synchronization",
    "C_quote_and_spread",
    "D_order_book_and_depth",
    "E_trade_print",
    "F_fee_funding_cost",
    "G_liquidity_and_latency",
    "H_anomaly_detection",
)

REQUIRED_QA_STATUSES = (
    "QA_DRAFT", "QA_PASS", "QA_WARN", "QA_FAIL", "QA_BLOCKED", "QA_RETIRED",
)

REQUIRED_QA_REPORT_FIELDS = (
    "qa_report_id",
    "dataset_id",
    "dataset_version",
    "manifest_version",
    "data_contract_version",
    "generated_at",
    "qa_status",
    "checks_run",
    "checks_passed",
    "checks_warned",
    "checks_failed",
    "blocking_failures",
    "warnings",
    "row_count_observed",
    "missing_data_summary",
    "timestamp_summary",
    "quote_summary",
    "fee_funding_summary",
    "liquidity_summary",
    "category_specific_summary",
    "allowed_next_step",
    "forbidden_next_steps",
    "safety_flags",
)

NON_EMPTY_LIST_SECTIONS = (
    "required_inputs",
    "forbidden_inputs",
    "manifest_validation_checks",
    "provenance_qa_checks",
    "normalization_qa_checks",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in markdown.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "RELATIVE_VALUE",
    "price gap is not profit",
    "QA is not strategy validation",
    "QA_PASS does NOT",
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
    "qa_pass implies profit",
    "qa_pass authorizes backtest",
    "qa_pass authorizes live",
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
        return False, ["qa_harness_spec.json is not a JSON object"]

    # Top-level required keys.
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    # Pinned-False execution / fetch / connection / backtest / dataset-processing flags.
    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Categories.
    categories = data.get("supported_arbitrage_categories")
    if not isinstance(categories, list):
        errors.append("supported_arbitrage_categories must be a list")
        categories = []
    elif len(categories) < 5:
        errors.append("supported_arbitrage_categories must have at least 5 entries")
    ids_present = {c.get("id") for c in categories if isinstance(c, dict)}
    for cid in REQUIRED_CATEGORY_IDS:
        if cid not in ids_present:
            errors.append(f"required category id missing: {cid}")
    for c in categories:
        if not isinstance(c, dict):
            errors.append("non-dict category entry")
            continue
        for f in REQUIRED_CATEGORY_FIELDS:
            if f not in c:
                errors.append(f"category {c.get('id', '?')!r}: missing field {f}")
        v = c.get("category_specific_qa_checks")
        if not isinstance(v, list) or not v:
            errors.append(f"category {c.get('id', '?')!r}: category_specific_qa_checks must be a non-empty list")

    # statistical_relative_value self-label.
    rv = next((c for c in categories if isinstance(c, dict) and c.get("id") == "statistical_relative_value"), None)
    if rv is not None and "NOT pure arbitrage" not in str(rv.get("label", "")):
        errors.append("statistical_relative_value category label must contain 'NOT pure arbitrage'")

    # QA check groups: all 8 present with non-empty `checks` lists.
    qcg = data.get("qa_check_groups")
    if not isinstance(qcg, dict):
        errors.append("qa_check_groups must be a dict")
    else:
        for grp in REQUIRED_QA_CHECK_GROUPS:
            if grp not in qcg:
                errors.append(f"qa_check_groups missing group: {grp}")
                continue
            g = qcg[grp]
            if not isinstance(g, dict) or "checks" not in g or not isinstance(g["checks"], list) or not g["checks"]:
                errors.append(f"qa_check_groups[{grp}] must be a dict with non-empty 'checks' list")

    # QA status model.
    qsr = data.get("qa_status_rules")
    if not isinstance(qsr, dict):
        errors.append("qa_status_rules must be a dict")
    else:
        for s in REQUIRED_QA_STATUSES:
            if s not in qsr:
                errors.append(f"qa_status_rules missing status: {s}")

    # Report schema completeness.
    rs = data.get("report_schema")
    if not isinstance(rs, dict):
        errors.append("report_schema must be a dict")
    else:
        req = rs.get("required_future_qa_report_fields")
        if not isinstance(req, list):
            errors.append("report_schema.required_future_qa_report_fields must be a list")
        else:
            req_set = set(req)
            for f in REQUIRED_QA_REPORT_FIELDS:
                if f not in req_set:
                    errors.append(f"report_schema.required_future_qa_report_fields missing: {f}")

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
    mpath = repo_root / SPEC_DIR_REL / SPEC_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"qa_harness_spec.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"qa_harness_spec.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # Also scan JSON text for forbidden phrases.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"qa_harness_spec.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"qa_harness_spec_id: {data.get('qa_harness_spec_id')}")
    print(f"title:              {data.get('title')}")
    print(f"version:            {data.get('version')}")
    print(f"research_only:      {data.get('research_only')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    cats = data.get("supported_arbitrage_categories") or []
    print(f"categories ({len(cats)}):")
    for c in cats:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>30}  {c.get('label')}")
    qcg = data.get("qa_check_groups") or {}
    print(f"qa_check_groups ({len(qcg)}):")
    for k in sorted(qcg.keys()):
        ch = qcg[k].get("checks") if isinstance(qcg[k], dict) else None
        n = len(ch) if isinstance(ch, list) else 0
        print(f"  - {k}: {n} checks")
    qsr = data.get("qa_status_rules") or {}
    print(f"qa_status_rules statuses: {sorted(qsr.keys())}")
    rs = data.get("report_schema") or {}
    fields = rs.get("required_future_qa_report_fields") or []
    print(f"report_schema.required_future_qa_report_fields: {len(fields)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage QA Harness Spec validator (research-only)",
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
