"""SPARTA Crypto-D1 Data Source Evaluation Memo -- validator (research-only, stdlib).

Validates `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.json`
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
  * 6 source classes A..F present with explicit status field
  * E status starts with 'REJECTED'
  * F status starts with 'REJECTED'
  * preferred_source_class_for_crypto_d1.preferred_does_not_mean_approved = True
  * decision_matrix has all 6 rows with required field set; every row's
    allowed_now is False
  * approval_gates_before_any_source_use, forbidden_data_sources_or_methods,
    required_provenance_fields, required_future_artifacts, safety_boundaries
    are non-empty lists
  * pass_watch_fail_rules carries PASS / WATCH / FAIL
  * safety_boundaries mentions research-only / no broker / no live / no order
  * MD carries 7 distinction phrases
  * no profitability / live-readiness / backtest-authorize claim in either file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_data_source_evaluation_check.py validate
  python tools/crypto_d1_data_source_evaluation_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR_REL = "reports/crypto_d1_data_source_evaluation_v1"
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
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "lane",
    "target_assets",
    "timeframe",
    "allowed_market_type",
    "forbidden_market_types",
    "evaluation_objective",
    "source_classes",
    "decision_matrix",
    "per_class_status_rationale",
    "approval_gates_before_any_source_use",
    "forbidden_data_sources_or_methods",
    "required_provenance_fields",
    "preferred_source_class_for_crypto_d1",
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
    "backtest_execution_enabled",
    "dataset_processing_enabled",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_SOURCE_CLASS_IDS = (
    "A_exchange_public_historical_archives",
    "B_exchange_public_apis",
    "C_paid_market_data_vendors",
    "D_existing_local_OHLCV_files",
    "E_web_scraped_or_unofficial_tables",
    "F_manually_copied_prices_or_screenshots",
)

REQUIRED_DECISION_MATRIX_FIELDS = (
    "id",
    "class_name",
    "status",
    "allowed_now",
    "spot_daily_supported",
    "btc_eth_sol_coverage_expected",
    "minimum_history_years_realistic",
    "tos_research_use_acceptable_typical",
    "export_format_typical",
    "requires_api_key_at_acquisition_time",
    "requires_credentials_at_acquisition_time",
    "network_call_required_from_sparta_runtime",
    "approval_gate_required",
    "bundle_17_compatible_when_gates_satisfied",
    "known_caveats",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "approval_gates_before_any_source_use",
    "forbidden_data_sources_or_methods",
    "required_provenance_fields",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "Source evaluation does not imply edge",
    "Acceptable source class does not authorize acquisition",
    "Preferred does not mean approved",
    "No data fetch is authorized by this bundle",
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

    sc = data.get("source_classes")
    if not isinstance(sc, list) or len(sc) < 6:
        errors.append("source_classes must be a list of at least 6 entries")
        sc = sc if isinstance(sc, list) else []
    # Always run per-id and per-status checks, even when count is short, so
    # the specific missing id surfaces in the error list.
    present_ids = {c.get("id") for c in sc if isinstance(c, dict)}
    for cid in REQUIRED_SOURCE_CLASS_IDS:
        if cid not in present_ids:
            errors.append(f"source_classes missing required id: {cid}")
    for c in sc:
        if not isinstance(c, dict):
            errors.append("non-dict source_classes entry")
            continue
        if "status" not in c:
            errors.append(f"source_classes entry {c.get('id', '?')!r}: missing 'status' field")
    # E + F must be REJECTED
    e_class = next((c for c in sc if isinstance(c, dict)
                    and c.get("id") == "E_web_scraped_or_unofficial_tables"), None)
    if e_class is not None and not str(e_class.get("status", "")).startswith("REJECTED"):
        errors.append(f"E status must start with REJECTED (got {e_class.get('status')!r})")
    f_class = next((c for c in sc if isinstance(c, dict)
                    and c.get("id") == "F_manually_copied_prices_or_screenshots"), None)
    if f_class is not None and not str(f_class.get("status", "")).startswith("REJECTED"):
        errors.append(f"F status must start with REJECTED (got {f_class.get('status')!r})")

    dm = data.get("decision_matrix")
    if not isinstance(dm, dict):
        errors.append("decision_matrix must be a dict")
        dm = {}
    rows = dm.get("rows")
    if not isinstance(rows, list) or len(rows) < 6:
        errors.append("decision_matrix.rows must be a list of at least 6 entries")
        rows = rows if isinstance(rows, list) else []
    # Always run per-id, per-field, allowed_now checks even if rows are short.
    row_ids = {r.get("id") for r in rows if isinstance(r, dict)}
    for cid in REQUIRED_SOURCE_CLASS_IDS:
        if cid not in row_ids:
            errors.append(f"decision_matrix.rows missing id: {cid}")
    for r in rows:
        if not isinstance(r, dict):
            errors.append("non-dict decision_matrix row")
            continue
        for fld in REQUIRED_DECISION_MATRIX_FIELDS:
            if fld not in r:
                errors.append(
                    f"decision_matrix row {r.get('id', '?')!r}: missing field {fld!r}"
                )
        if r.get("allowed_now") is not False:
            errors.append(
                f"decision_matrix row {r.get('id', '?')!r}: allowed_now must be False"
            )

    pref = data.get("preferred_source_class_for_crypto_d1")
    if not isinstance(pref, dict):
        errors.append("preferred_source_class_for_crypto_d1 must be a dict")
    else:
        if "class_id" not in pref:
            errors.append("preferred_source_class_for_crypto_d1 missing 'class_id'")
        if pref.get("preferred_does_not_mean_approved") is not True:
            errors.append("preferred_source_class_for_crypto_d1.preferred_does_not_mean_approved must be True")
        if pref.get("concrete_vendor_selection_requires_bundle_17_gates") is not True:
            errors.append("preferred_source_class_for_crypto_d1.concrete_vendor_selection_requires_bundle_17_gates must be True")

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
    print(f"evaluation_id:       {data.get('evaluation_id')}")
    print(f"title:               {data.get('title')}")
    print(f"version:             {data.get('version')}")
    print(f"research_only:       {data.get('research_only')}")
    print(f"lane:                {data.get('lane')}")
    print(f"allowed_market_type: {data.get('allowed_market_type')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    sc = data.get("source_classes") or []
    print(f"source_classes ({len(sc)}):")
    for c in sc:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>50}  status={c.get('status')}")
    pref = data.get("preferred_source_class_for_crypto_d1") or {}
    print(f"preferred_class: {pref.get('class_id')}")
    print(f"  preferred_does_not_mean_approved: {pref.get('preferred_does_not_mean_approved')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Data Source Evaluation Memo validator (research-only)",
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
