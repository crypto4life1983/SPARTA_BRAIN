"""SPARTA Arbitrage Sample Dataset Plan — validator (research-only, stdlib).

Validates `reports/arbitrage_sample_dataset_plan_v1/sample_dataset_plan.json`
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
  * proposed_sample_scope is present, TINY, and disclaims data collection
  * naming_convention + storage_plan + freeze_plan exist (no real files)
  * approval_gates include explicit operator authorization AND all five
    upstream version pins (protocol / contract / manifest / qa / evaluation)
  * future_collection_steps include 'explicit_operator_authorization' and
    'data_collection_in_separate_bundle'
  * pure-arbitrage / statistical-relative-value distinction is preserved

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_sample_dataset_plan_check.py validate
  python tools/arbitrage_sample_dataset_plan_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR_REL = "reports/arbitrage_sample_dataset_plan_v1"
PLAN_JSON = "sample_dataset_plan.json"
PLAN_MD = "sample_dataset_plan.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "sample_dataset_plan_id",
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
    "proposed_sample_scope",
    "candidate_venues",
    "candidate_symbols",
    "candidate_time_windows",
    "required_fields",
    "manifest_requirements",
    "QA_requirements",
    "storage_plan",
    "naming_convention",
    "freeze_plan",
    "approval_gates",
    "rejection_rules",
    "future_collection_steps",
    "forbidden_actions",
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

REQUIRED_APPROVAL_GATE_MARKERS = (
    "explicit_operator_authorization",
    "exact_source_named",
    "exact_venue_names",
    "exact_symbols_named",
    "exact_time_window_named",
    "exact_storage_path_named",
    "protocol_version_referenced",
    "data_contract_version_referenced",
    "dataset_manifest_version_referenced",
    "qa_harness_spec_version_referenced",
    "data_source_evaluation_version_referenced",
    "sample_dataset_plan_version_referenced",
    "no_credentials_unless_separately_approved",
    "no_trading_permissions",
    "no_automatic_scheduler",
    "no_live_or_paper_execution",
)

REQUIRED_FUTURE_COLLECTION_STEPS_MARKERS = (
    "explicit_operator_authorization",
    "data_collection_in_separate_bundle",
)

NON_EMPTY_LIST_SECTIONS = (
    "rejection_rules",
    "future_collection_steps",
    "forbidden_actions",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in markdown.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "A sample dataset does not imply edge",
    "A clean sample does not imply profitability",
    "A price gap is not profit",
    "Sample data cannot authorize trading",
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
        return False, ["sample_dataset_plan.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Supported categories include all 5 (informational; statistical labelled NOT pure arbitrage).
    cats = data.get("supported_arbitrage_categories")
    if not isinstance(cats, list) or len(cats) < 5:
        errors.append("supported_arbitrage_categories must be a list with at least 5 entries")
    else:
        ids = {c.get("id") for c in cats if isinstance(c, dict)}
        for cid in ("cross_exchange_spot", "spot_perp_basis_funding", "triangular",
                   "futures_calendar", "statistical_relative_value"):
            if cid not in ids:
                errors.append(f"supported_arbitrage_categories missing: {cid}")
        rv = next((c for c in cats if isinstance(c, dict) and c.get("id") == "statistical_relative_value"), None)
        if rv is not None and "NOT pure arbitrage" not in str(rv.get("label", "")):
            errors.append("statistical_relative_value category label must contain 'NOT pure arbitrage'")

    # Proposed sample scope must exist and be TINY: primary=cross_exchange_spot;
    # symbols list <= 4 (the spec says BTC/USDT and ETH/USDT as examples; allow up to 4 to leave headroom).
    pss = data.get("proposed_sample_scope")
    if not isinstance(pss, dict):
        errors.append("proposed_sample_scope must be a dict")
    else:
        if pss.get("primary_category") != "cross_exchange_spot":
            errors.append("proposed_sample_scope.primary_category must be 'cross_exchange_spot'")
        if pss.get("scope_intent") and "TINY" not in str(pss.get("scope_intent")).upper():
            errors.append("proposed_sample_scope.scope_intent must declare TINY scope")
        sym = pss.get("symbols_example_only")
        if not isinstance(sym, list) or len(sym) == 0:
            errors.append("proposed_sample_scope.symbols_example_only must be a non-empty list")
        elif len(sym) > 4:
            errors.append("proposed_sample_scope.symbols_example_only too broad (>4); scope must stay TINY")
        if not pss.get("explicit_disclaimers"):
            errors.append("proposed_sample_scope.explicit_disclaimers must be present")

    # naming_convention must exist and reference filename patterns + dataset_id_pattern.
    nc = data.get("naming_convention")
    if not isinstance(nc, dict):
        errors.append("naming_convention must be a dict")
    else:
        for k in ("dataset_id_pattern", "dataset_version_pattern", "manifest_filename",
                 "qa_report_filename", "checksum_filename"):
            if k not in nc:
                errors.append(f"naming_convention missing key: {k}")
        if nc.get("files_are_examples_only_no_real_files_in_this_bundle") is not True:
            errors.append("naming_convention.files_are_examples_only_no_real_files_in_this_bundle must be True")

    # storage_plan must exist, forbid network URLs, and forbid real-files-in-this-bundle.
    sp = data.get("storage_plan")
    if not isinstance(sp, dict):
        errors.append("storage_plan must be a dict")
    else:
        if sp.get("no_network_url_allowed") is not True:
            errors.append("storage_plan.no_network_url_allowed must be True")
        if sp.get("no_real_data_files_created_in_this_bundle") is not True:
            errors.append("storage_plan.no_real_data_files_created_in_this_bundle must be True")

    # freeze_plan must exist.
    fp = data.get("freeze_plan")
    if not isinstance(fp, dict):
        errors.append("freeze_plan must be a dict")

    # Approval gates: must include all required markers.
    ag = data.get("approval_gates")
    if not isinstance(ag, dict):
        errors.append("approval_gates must be a dict")
    else:
        gates = ag.get("must_all_be_satisfied_before_any_future_data_collection")
        if not isinstance(gates, list) or not gates:
            errors.append("approval_gates.must_all_be_satisfied_before_any_future_data_collection must be a non-empty list")
        else:
            joined = " ".join(str(g) for g in gates).lower()
            for marker in REQUIRED_APPROVAL_GATE_MARKERS:
                if marker not in joined:
                    errors.append(f"approval_gates missing marker: {marker}")

    # Future collection steps must include the two required markers.
    fcs = data.get("future_collection_steps")
    if not isinstance(fcs, list) or not fcs:
        errors.append("future_collection_steps must be a non-empty list")
    else:
        joined = " ".join(str(s) for s in fcs).lower()
        for marker in REQUIRED_FUTURE_COLLECTION_STEPS_MARKERS:
            if marker not in joined:
                errors.append(f"future_collection_steps missing marker: {marker}")

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
    mpath = repo_root / PLAN_DIR_REL / PLAN_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"sample_dataset_plan.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"sample_dataset_plan.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"sample_dataset_plan.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"sample_dataset_plan_id: {data.get('sample_dataset_plan_id')}")
    print(f"title:                  {data.get('title')}")
    print(f"version:                {data.get('version')}")
    print(f"research_only:          {data.get('research_only')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    pss = data.get("proposed_sample_scope") or {}
    print("proposed sample scope:")
    print(f"  primary_category: {pss.get('primary_category')}")
    print(f"  scope_intent:     {pss.get('scope_intent')}")
    syms = pss.get("symbols_example_only") or []
    print(f"  symbols (example only): {[s.get('canonical') for s in syms if isinstance(s, dict)]}")
    nc = data.get("naming_convention") or {}
    print(f"naming dataset_id_pattern: {nc.get('dataset_id_pattern')}")
    print(f"naming examples:           {nc.get('dataset_id_examples_label_only')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Sample Dataset Plan validator (research-only)",
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
