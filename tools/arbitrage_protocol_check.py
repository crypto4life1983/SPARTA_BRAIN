"""SPARTA Arbitrage Research Protocol — validator (research-only, stdlib).

Validates `reports/arbitrage_research_protocol_v1/protocol.json` against the
required schema and the hard safety contract:
  * research_only is True
  * five execution-related flags are False:
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      exchange_connection_enabled
      data_fetch_enabled
  * the five required arbitrage categories are present and labelled
  * pure-arbitrage / statistical-relative-value distinction is preserved
  * no profitability claim, no live-readiness claim
  * required validation phases / pass-watch-fail rules / safety boundaries /
    required-future-artifacts are present

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_protocol_check.py validate
  python tools/arbitrage_protocol_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTOCOL_DIR_REL = "reports/arbitrage_research_protocol_v1"
PROTOCOL_JSON = "protocol.json"
PROTOCOL_MD = "protocol.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "protocol_id",
    "title",
    "version",
    "research_only",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "exchange_connection_enabled",
    "data_fetch_enabled",
    "categories",
    "out_of_scope",
    "validation_phases",
    "pass_watch_fail_rules",
    "safety_boundaries",
    "required_future_artifacts",
)

MUST_BE_FALSE_FLAGS = (
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "exchange_connection_enabled",
    "data_fetch_enabled",
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
    "hypothesis",
    "data_needed",
    "minimum_viable_test",
    "main_costs",
    "main_risks",
    "likely_feasibility",
    "why_it_may_fail",
    "first_safe_research_step",
)

# Phrases that must appear somewhere in the protocol to keep word discipline.
DISTINCTION_PHRASES = (
    "Pure arbitrage",
    "NOT pure arbitrage",
    "statistical_relative_value",
    "Apparent edge",  # apparent_edge_is_not_profit definition + section
)

# Phrases that must NOT appear (catch accidental profitability claims).
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
)


def _load_protocol(repo_root: Path):
    p = repo_root / PROTOCOL_DIR_REL / PROTOCOL_JSON
    if not p.exists():
        return None, f"missing: {p.as_posix()}"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid JSON ({type(exc).__name__}): {p.as_posix()}"


def validate(repo_root: Path = REPO_ROOT):
    errors: list = []
    data, err = _load_protocol(repo_root)
    if err:
        return False, [err]
    if not isinstance(data, dict):
        return False, ["protocol.json is not a JSON object"]

    # Top-level required keys.
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    # Pinned-False execution flags.
    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"execution flag {flag} must be False (got {data.get(flag)!r})")

    # research_only must be True.
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # Categories: must contain all five with the required fields.
    categories = data.get("categories")
    if not isinstance(categories, list):
        errors.append("categories must be a list")
        categories = []
    elif len(categories) < 5:
        errors.append("categories must be a list with at least 5 entries")
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

    # Pure vs statistical distinction: relative_value category must self-label.
    rv = next((c for c in (categories or []) if isinstance(c, dict) and c.get("id") == "statistical_relative_value"), None)
    if rv is not None:
        label = str(rv.get("label", ""))
        if "NOT pure arbitrage" not in label:
            errors.append("statistical_relative_value category label must contain 'NOT pure arbitrage'")

    # Out of scope: non-empty list.
    oos = data.get("out_of_scope")
    if not isinstance(oos, list) or not oos:
        errors.append("out_of_scope must be a non-empty list")

    # Validation phases: must include P0..P5 markers + the negative phase.
    phases = data.get("validation_phases")
    if not isinstance(phases, list) or not phases:
        errors.append("validation_phases must be a non-empty list")
    else:
        phase_ids = {str(p.get("phase")) for p in phases if isinstance(p, dict)}
        for required_phase in ("P0_protocol", "P1_data_contract", "P3_offline_replay", "P4_holdout_oos", "P_NONE_live_or_paper"):
            if required_phase not in phase_ids:
                errors.append(f"validation_phases missing required phase: {required_phase}")

    # Pass/Watch/Fail rules: dict-like or list-like, but at minimum must contain PASS/WATCH/FAIL keys.
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

    # Safety boundaries: non-empty list mentioning research-only / no broker.
    sb = data.get("safety_boundaries")
    if not isinstance(sb, list) or not sb:
        errors.append("safety_boundaries must be a non-empty list")
    else:
        sb_join = " ".join(str(x) for x in sb).lower()
        for needle in ("research-only", "no broker", "no live", "no order"):
            if needle not in sb_join:
                errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Required future artifacts: non-empty list.
    rfa = data.get("required_future_artifacts")
    if not isinstance(rfa, list) or not rfa:
        errors.append("required_future_artifacts must be a non-empty list")

    # Distinction phrases must appear in the markdown (if present).
    mpath = repo_root / PROTOCOL_DIR_REL / PROTOCOL_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"protocol.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"protocol.md contains forbidden profitability/live phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # Also scan the JSON text for forbidden phrases (defense in depth).
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"protocol.json contains forbidden profitability/live phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load_protocol(repo_root)
    if err:
        print(err)
        return 1
    print(f"protocol_id: {data.get('protocol_id')}")
    print(f"title:       {data.get('title')}")
    print(f"version:     {data.get('version')}")
    print(f"research_only: {data.get('research_only')}")
    print("execution flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    cats = data.get("categories") or []
    print(f"categories ({len(cats)}):")
    for c in cats:
        if isinstance(c, dict):
            print(f"  - {c.get('id'):>30}  {c.get('label')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Research Protocol validator (research-only)",
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
