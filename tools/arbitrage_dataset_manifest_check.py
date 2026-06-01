"""SPARTA Arbitrage Dataset Manifest — validator (research-only, stdlib).

Validates `reports/arbitrage_dataset_manifest_v1/dataset_manifest.json` against
the required schema and the hard safety contract:
  * research_only is True
  * six execution / fetch / connection / backtest flags are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      backtest_enabled
  * the five required arbitrage categories are present with category-specific
    manifest requirements
  * the manifest_schema lists every required future-manifest field
  * the QA status model contains all 7 statuses (DRAFT/FROZEN/QA_PASS/
    QA_WARN/QA_FAIL/RETIRED/BLOCKED)
  * freeze rules are documented and pinned-False flags are intact
  * the pure-arbitrage / statistical-relative-value distinction is preserved
  * no profitability claim, no live-readiness claim, no fetch claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_dataset_manifest_check.py validate
  python tools/arbitrage_dataset_manifest_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR_REL = "reports/arbitrage_dataset_manifest_v1"
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
    "supported_arbitrage_categories",
    "manifest_schema",
    "dataset_identity_fields",
    "venue_fields",
    "instrument_fields",
    "time_range_fields",
    "timestamp_fields",
    "quote_fields",
    "order_book_fields",
    "trade_print_fields",
    "fee_fields",
    "funding_fields",
    "liquidity_fields",
    "latency_fields",
    "provenance_fields",
    "normalization_fields",
    "data_quality_fields",
    "freeze_fields",
    "validation_fields",
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
    "category_specific_manifest_requirements",
)

REQUIRED_FUTURE_MANIFEST_FIELDS = (
    "dataset_id",
    "dataset_version",
    "created_at",
    "created_by",
    "research_lane",
    "arbitrage_category",
    "venues",
    "symbols",
    "instruments",
    "time_start",
    "time_end",
    "timezone",
    "data_frequency",
    "quote_type",
    "order_book_depth",
    "fee_schedule_reference",
    "funding_schedule_reference",
    "source_type",
    "source_location",
    "checksum_policy",
    "row_count_expected",
    "row_count_actual",
    "missing_data_policy",
    "duplicate_policy",
    "stale_quote_policy",
    "clock_skew_policy",
    "normalization_policy",
    "freeze_status",
    "qa_status",
    "allowed_use",
    "forbidden_use",
    "notes",
)

REQUIRED_QA_STATUSES = (
    "DRAFT", "FROZEN", "QA_PASS", "QA_WARN", "QA_FAIL", "RETIRED", "BLOCKED",
)

NON_EMPTY_DICT_OR_LIST_SECTIONS = (
    "manifest_schema",
    "dataset_identity_fields",
    "venue_fields",
    "instrument_fields",
    "time_range_fields",
    "timestamp_fields",
    "fee_fields",
    "funding_fields",
    "liquidity_fields",
    "latency_fields",
    "provenance_fields",
    "normalization_fields",
    "data_quality_fields",
    "freeze_fields",
    "validation_fields",
)

NON_EMPTY_LIST_SECTIONS = (
    "quote_fields",
    "order_book_fields",
    "trade_print_fields",
    "allowed_file_formats",
    "forbidden_inputs",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear somewhere in the markdown.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "RELATIVE_VALUE",
    "price gap is not profit",
    "QA_PASS does not imply profitability",
)

# Forbidden capability claims. Negative-framed safety language ("DO NOT
# require a live API connection") must remain expressible, so substrings that
# only ever appear in negative framings are intentionally NOT listed here.
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

    # Top-level required keys.
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    # Pinned-False execution / connection / fetch / backtest flags.
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
        reqs = c.get("category_specific_manifest_requirements")
        if not isinstance(reqs, list) or not reqs:
            errors.append(f"category {c.get('id', '?')!r}: category_specific_manifest_requirements must be a non-empty list")

    # statistical_relative_value self-label.
    rv = next((c for c in categories if isinstance(c, dict) and c.get("id") == "statistical_relative_value"), None)
    if rv is not None and "NOT pure arbitrage" not in str(rv.get("label", "")):
        errors.append("statistical_relative_value category label must contain 'NOT pure arbitrage'")

    # manifest_schema.required_future_manifest_fields completeness.
    ms = data.get("manifest_schema")
    if isinstance(ms, dict):
        req = ms.get("required_future_manifest_fields")
        if not isinstance(req, list):
            errors.append("manifest_schema.required_future_manifest_fields must be a list")
        else:
            req_set = set(req)
            for f in REQUIRED_FUTURE_MANIFEST_FIELDS:
                if f not in req_set:
                    errors.append(f"manifest_schema.required_future_manifest_fields missing: {f}")
        fd = ms.get("field_descriptions")
        if not isinstance(fd, dict) or not fd:
            errors.append("manifest_schema.field_descriptions must be a non-empty dict")
    else:
        errors.append("manifest_schema must be a dict")

    # QA status model: all 7 statuses present.
    qa = data.get("qa_status_model")
    if isinstance(qa, dict):
        for s in REQUIRED_QA_STATUSES:
            if s not in qa:
                errors.append(f"qa_status_model missing status: {s}")
    else:
        errors.append("qa_status_model must be a dict (with all 7 statuses)")

    # Freeze rules: non-empty list mentioning FROZEN.
    fr = data.get("data_freeze_rules")
    if not isinstance(fr, list) or not fr:
        errors.append("data_freeze_rules must be a non-empty list")
    else:
        if "FROZEN" not in " ".join(str(x) for x in fr):
            errors.append("data_freeze_rules must mention FROZEN")

    # Non-empty dict-or-list sections.
    for k in NON_EMPTY_DICT_OR_LIST_SECTIONS:
        v = data.get(k)
        if isinstance(v, dict):
            if not v:
                errors.append(f"section {k} must be a non-empty dict")
        elif isinstance(v, list):
            if not v:
                errors.append(f"section {k} must be a non-empty list")
        else:
            errors.append(f"section {k} must be a dict or list")

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # pass_watch_fail_rules: dict with PASS/WATCH/FAIL keys (or list mentioning them).
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

    # Distinction phrases in markdown (if present).
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

    # Also scan JSON text for forbidden phrases.
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
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    cats = data.get("supported_arbitrage_categories") or []
    print(f"categories ({len(cats)}):")
    for c in cats:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>30}  {c.get('label')}")
    ms = data.get("manifest_schema") or {}
    req = ms.get("required_future_manifest_fields") or []
    print(f"required future manifest fields: {len(req)}")
    qa = data.get("qa_status_model") or {}
    print(f"qa_status_model statuses: {sorted(qa.keys())}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Dataset Manifest validator (research-only)",
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
