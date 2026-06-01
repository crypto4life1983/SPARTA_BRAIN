"""SPARTA Arbitrage Data Contract — validator (research-only, stdlib).

Validates `reports/arbitrage_data_contract_v1/data_contract.json` against the
required schema and the hard safety contract:
  * research_only is True
  * five execution / fetch / connection flags are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
  * the five required arbitrage categories are present and well-formed
  * pure-arbitrage / statistical-relative-value distinction is preserved
  * timestamp / order-book / quote / fee / funding / liquidity / latency /
    data-quality / normalization / minimum-viable-dataset / future-allowed-
    sources / forbidden-sources / required-future-artifacts / pass-watch-fail
    rules / safety boundaries / no-profit-claim policy are present
  * no profitability claim, no live-readiness claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_data_contract_check.py validate
  python tools/arbitrage_data_contract_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_DIR_REL = "reports/arbitrage_data_contract_v1"
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
    "supported_arbitrage_categories",
    "venue_requirements",
    "instrument_requirements",
    "timestamp_requirements",
    "order_book_requirements",
    "trade_print_requirements",
    "quote_requirements",
    "fee_requirements",
    "funding_requirements",
    "withdrawal_deposit_requirements",
    "liquidity_requirements",
    "latency_requirements",
    "data_quality_rules",
    "normalization_rules",
    "minimum_viable_dataset",
    "future_allowed_data_sources",
    "forbidden_data_sources_or_methods",
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
    "data_needed",
    "category_specific_validity",
)

# Each subsection that must be a non-empty dict (or non-empty list).
NON_EMPTY_DICT_OR_LIST_SECTIONS = (
    "venue_requirements",
    "instrument_requirements",
    "timestamp_requirements",
    "order_book_requirements",
    "trade_print_requirements",
    "quote_requirements",
    "fee_requirements",
    "funding_requirements",
    "withdrawal_deposit_requirements",
    "liquidity_requirements",
    "latency_requirements",
    "data_quality_rules",
    "normalization_rules",
    "minimum_viable_dataset",
)

NON_EMPTY_LIST_SECTIONS = (
    "future_allowed_data_sources",
    "forbidden_data_sources_or_methods",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "RELATIVE_VALUE",
    "price gap is not profit",
    "Apparent edge",
    "Apparent edge ≠ profit",  # note: also accepted as the ASCII fallback below
)
DISTINCTION_PHRASES_ASCII_FALLBACK = (
    "Apparent edge != profit",
)

# Forbidden phrases (profitability / live / connection claims). These are claims
# of capability ("we can / we will / we do"); negative-framed safety language
# ("DO NOT require a live API connection") must remain expressible, so phrases
# that only ever appear in negative framings are intentionally NOT listed here.
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

    # Top-level required keys.
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    # Pinned-False execution / connection / fetch flags.
    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")

    # research_only must be True.
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Categories: all five present with required fields.
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
        # data_needed and category_specific_validity must be non-empty lists.
        for lk in ("data_needed", "category_specific_validity"):
            v = c.get(lk)
            if not isinstance(v, list) or not v:
                errors.append(f"category {c.get('id', '?')!r}: {lk} must be a non-empty list")

    # statistical_relative_value must self-label NOT pure arbitrage.
    rv = next((c for c in categories if isinstance(c, dict) and c.get("id") == "statistical_relative_value"), None)
    if rv is not None and "NOT pure arbitrage" not in str(rv.get("label", "")):
        errors.append("statistical_relative_value category label must contain 'NOT pure arbitrage'")

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

    # timestamp_requirements should include primary_clock + accepted_timestamp_fields + max_skew_allowed.
    ts = data.get("timestamp_requirements") or {}
    if isinstance(ts, dict):
        for k in ("primary_clock", "accepted_timestamp_fields", "max_skew_allowed", "stale_quote_rule"):
            if k not in ts:
                errors.append(f"timestamp_requirements missing key: {k}")

    # fee_requirements should include maker + taker + withdrawal_fees.
    fr = data.get("fee_requirements") or {}
    if isinstance(fr, dict):
        for k in ("maker_fee_bps", "taker_fee_bps", "withdrawal_fees"):
            if k not in fr:
                errors.append(f"fee_requirements missing key: {k}")

    # Distinction phrases must appear in the markdown (if present).
    mpath = repo_root / CONTRACT_DIR_REL / CONTRACT_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        # Each distinction must appear in either UTF-8 form or its ASCII fallback.
        for phrase in DISTINCTION_PHRASES:
            if phrase in md:
                continue
            # If this phrase has an ASCII fallback, allow it.
            ascii_pair = [p for p in DISTINCTION_PHRASES_ASCII_FALLBACK if p in md]
            if phrase.endswith("≠ profit") and ascii_pair:
                continue
            errors.append(f"data_contract.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"data_contract.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # Also scan JSON text for forbidden phrases (defense in depth).
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
    print(f"data_contract_id: {data.get('data_contract_id')}")
    print(f"title:            {data.get('title')}")
    print(f"version:          {data.get('version')}")
    print(f"research_only:    {data.get('research_only')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    cats = data.get("supported_arbitrage_categories") or []
    print(f"categories ({len(cats)}):")
    for c in cats:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>30}  {c.get('label')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Data Contract validator (research-only)",
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
