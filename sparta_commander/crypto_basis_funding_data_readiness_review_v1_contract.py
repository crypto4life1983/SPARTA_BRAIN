"""Crypto spot/perp basis + funding DATA-READINESS REVIEW v1
(PURE, READ-ONLY, RESEARCH ONLY).

Records and validates the frozen, PUBLIC, research-only spot/perp/funding dataset
fetched by tools/crypto_basis_funding_public_fetch_once.py (approved via
HUMAN_APPROVED_FETCH_PUBLIC_PERP_SPOT_BASIS_AND_FUNDING_DATA_RESEARCH_ONLY). It PINS the
per-file SHA256 provenance, row counts, date ranges, and columns, plus the common
tradeable window for a future basis/funding study -- so the dataset is frozen and
auditable.

It is a DATA-READINESS REVIEW ONLY: it does NOT assign C20, creates no candidate, builds
no detector/labels/replay, runs no optimization/tuning, computes no PnL, and writes no
paper/live/broker/order/trading code. The fetched data artifacts are GITIGNORED and NOT
committed; this contract only pins their SHAs. Turning this dataset into a candidate
needs a separate explicit human open-candidate token. Every capability flag is pinned
False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

DR_VERSION = "v1"
DR_MODE = "RESEARCH_ONLY"
DR_LANE = "crypto_d1_auto_research"

FETCHED_BY = "tools/crypto_basis_funding_public_fetch_once.py"
DATA_DIR = "data/crypto_basis_funding_research/raw"
MANIFEST_PATH = "data/crypto_basis_funding_research/raw/fetch_manifest.json"
MANIFEST_SHA256 = (
    "45f1f07e37c795f24497a0b9a646bd545a90d85d719176991bd409c01fdf5cbe")

FETCH_WINDOW = ("2020-01-01", "2026-06-08")
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
KLINES_COLUMNS = ("date", "open", "high", "low", "close", "volume")
FUNDING_COLUMNS = ("datetime", "funding_time_ms", "symbol", "funding_rate",
                   "mark_price")

# pinned frozen per-file provenance (PUBLIC data; gitignored; SHA-pinned, NOT committed)
FILES = {
    "BTCUSDT_spot": {
        "path": "data/crypto_basis_funding_research/raw/BTCUSDT_spot_1d.csv",
        "kind": "spot", "rows": 2350, "first": "2020-01-02", "last": "2026-06-08",
        "sha256": "0a214e5fae7f7b73b632193c23d633ab87114b7559e75111fa9ed7f1ef998f1a"},
    "BTCUSDT_perp": {
        "path": "data/crypto_basis_funding_research/raw/BTCUSDT_perp_1d.csv",
        "kind": "perp", "rows": 2350, "first": "2020-01-02", "last": "2026-06-08",
        "sha256": "bfbaccb9056b2ea4c2136182333040bf9efca612f0440de902f79e5c31068a95"},
    "BTCUSDT_funding": {
        "path": "data/crypto_basis_funding_research/raw/BTCUSDT_funding.csv",
        "kind": "funding", "rows": 7050, "first": "2020-01-01", "last": "2026-06-08",
        "sha256": "7071f1484b3cd2e8d1ebe4abd1df93434f99646b1c9fd464a12251ac72d6869e"},
    "ETHUSDT_spot": {
        "path": "data/crypto_basis_funding_research/raw/ETHUSDT_spot_1d.csv",
        "kind": "spot", "rows": 2350, "first": "2020-01-02", "last": "2026-06-08",
        "sha256": "45e6616e0753f7edf2c0e3aae03c9435e08a06999a6876c728a8b8237093554b"},
    "ETHUSDT_perp": {
        "path": "data/crypto_basis_funding_research/raw/ETHUSDT_perp_1d.csv",
        "kind": "perp", "rows": 2350, "first": "2020-01-02", "last": "2026-06-08",
        "sha256": "e02bb1a874001932064ac00a31eafcdd41d7841702c2ac0d315c87a2b4cb5bed"},
    "ETHUSDT_funding": {
        "path": "data/crypto_basis_funding_research/raw/ETHUSDT_funding.csv",
        "kind": "funding", "rows": 7050, "first": "2020-01-01", "last": "2026-06-08",
        "sha256": "32804816434bcab09709086d7171c46136b2986affba5c19b7b0ef5b898531ed"},
    "SOLUSDT_spot": {
        "path": "data/crypto_basis_funding_research/raw/SOLUSDT_spot_1d.csv",
        "kind": "spot", "rows": 2128, "first": "2020-08-11", "last": "2026-06-08",
        "sha256": "b1ac44dc763eb987b03265ca6d293b0ce2f29acdb6ab02eca1fbe744e55bb227"},
    "SOLUSDT_perp": {
        "path": "data/crypto_basis_funding_research/raw/SOLUSDT_perp_1d.csv",
        "kind": "perp", "rows": 2094, "first": "2020-09-14", "last": "2026-06-08",
        "sha256": "a9810dfab32f210d18dd6a428f424a769eaf9c5449367adf795c95374c7c49a0"},
    "SOLUSDT_funding": {
        "path": "data/crypto_basis_funding_research/raw/SOLUSDT_funding.csv",
        "kind": "funding", "rows": 6356, "first": "2020-09-13", "last": "2026-06-08",
        "sha256": "520d28ebdd8142967bc1f9159a16934dc606621ad4c530315af6f2f608dcc759"},
}

# the common tradeable window where spot + perp + funding all exist for all symbols
# (gated by the SOL perp / funding start) -- the window a future basis/funding study
# would use.
COMMON_BASIS_WINDOW = ("2020-09-14", "2026-06-08")

ALL_TIMESTAMPS_MONOTONIC = True
ALL_COLUMNS_VALID = True

NEXT_REQUIRED_ACTION = (
    "AWAIT_HUMAN_DECISION__BASIS_FUNDING_DATA_READY__NO_C20_ASSIGNED__"
    "OPENING_A_CANDIDATE_NEEDS_EXPLICIT_TOKEN")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "assigns_c20", "opens_candidate", "creates_candidate",
    "creates_family_proposal", "fetches_data", "re_fetches", "runs_detector",
    "runs_labels", "runs_replay", "computes_pnl", "applies_cost_model",
    "optimizes_parameters", "tunes_parameters", "runs_rescue", "mutates_data",
    "stages_data", "commits_data_artifact", "auto_commits", "auto_pushes",
    "uses_credentials", "uses_network", "calls_api", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "adds_new_instrument_class", "uses_xauusd", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_data_readiness_label() -> str:
    return (
        "Crypto basis/funding data-readiness review v1 (READ-ONLY, RESEARCH ONLY). "
        "Frozen PUBLIC BTC/ETH/SOL spot + USDT-perp + funding (fetch window "
        "2020-01-01..2026-06-08; common spot+perp+funding window 2020-09-14.."
        "2026-06-08), SHA-pinned, monotonic, columns validated -- gitignored and NOT "
        "committed. Data-readiness only: assigns no C20, creates no candidate, builds "
        "no detector/labels/replay, runs no optimization. Opening a candidate needs a "
        "separate explicit human token. NOT a profitability claim.")


def get_data_readiness_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_data_readiness_review() -> dict[str, Any]:
    """Assemble the frozen data-readiness review record. Pure; no I/O; pins the
    fetched-dataset provenance. Assigns no C20; creates no candidate; fetches nothing;
    commits no data artifact."""
    total_rows = sum(f["rows"] for f in FILES.values())
    record: dict[str, Any] = {
        "version": DR_VERSION, "mode": DR_MODE, "lane": DR_LANE,
        "is_data_readiness_review_only": True,
        "label": get_data_readiness_label(),
        # hard guarantees
        "assigns_c20": False, "c20_assigned": False, "candidate_id": None,
        "opens_candidate": False, "creates_family_proposal": False,
        "builds_detector_labels_or_replay": False, "optimizes_or_tunes": False,
        "fetched_more_data_here": False,
        # provenance
        "fetched_by": FETCHED_BY, "data_dir": DATA_DIR,
        "fetch_window": list(FETCH_WINDOW), "symbols": list(SYMBOLS),
        "klines_columns": list(KLINES_COLUMNS),
        "funding_columns": list(FUNDING_COLUMNS),
        "manifest_path": MANIFEST_PATH, "manifest_sha256": MANIFEST_SHA256,
        "files": {k: dict(v) for k, v in FILES.items()},
        "file_count": len(FILES),
        "total_rows": total_rows,
        "common_basis_window": list(COMMON_BASIS_WINDOW),
        # validation summary (from the Phase-2 read-only checks)
        "all_timestamps_monotonic": ALL_TIMESTAMPS_MONOTONIC,
        "all_columns_valid": ALL_COLUMNS_VALID,
        "public_data_only_no_credentials": True,
        # the data is gitignored + NOT committed
        "artifacts_gitignored_not_committed": True,
        # readiness verdict
        "readiness_verdict": "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY",
        "ready_for_future_basis_funding_research": True,
        "supports_recommended_first_target": "perp_basis_spot_perp_spread",
        # human gates preserved
        "requires_human_approval_before_c20": True,
        "opening_c20_requires_explicit_open_candidate_token": True,
        "human_review_required": True,
        "current_loop_stage": "data_readiness_review",
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_assign_c20": True,
        "no_open_candidate": True, "no_create_candidate": True,
        "no_family_proposal": True, "no_fetch": True, "no_re_fetch": True,
        "no_detector": True, "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_tuning": True, "no_data_commit": True,
        "no_data_mutation": True, "no_credentials": True, "no_network": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_data_readiness_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only,
    data-readiness-only, assigns NO C20 / opens no candidate / builds no
    detector-labels-replay / runs no optimization / fetches nothing more, pins all
    nine PUBLIC files with 64-char SHAs + row counts + date ranges + monotonic +
    valid columns, marks the data gitignored-and-not-committed, declares the data
    frozen and ready, preserves the C20 human gate, and pins every capability flag
    False with the scope locks."""
    failures: list = []
    if record.get("mode") != DR_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_data_readiness_review_only") is not True:
        failures.append("not_data_readiness_review_only")

    # hard guarantees
    for k in ("assigns_c20", "c20_assigned", "opens_candidate",
              "creates_family_proposal", "builds_detector_labels_or_replay",
              "optimizes_or_tunes", "fetched_more_data_here"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)
    if record.get("candidate_id") is not None:
        failures.append("candidate_id_must_be_none")

    # provenance: nine files, each with a 64-char SHA, rows, dates
    files = record.get("files") or {}
    if len(files) != 9:
        failures.append("expected_nine_files")
    for key, exp in FILES.items():
        f = files.get(key) or {}
        if f.get("sha256") != exp["sha256"]:
            failures.append("sha_tampered_%s" % key)
        if not (isinstance(f.get("sha256"), str) and len(f["sha256"]) == 64):
            failures.append("sha_bad_%s" % key)
        if f.get("rows") != exp["rows"]:
            failures.append("rows_tampered_%s" % key)
        if f.get("first") != exp["first"] or f.get("last") != exp["last"]:
            failures.append("dates_tampered_%s" % key)
        if not str(f.get("path", "")).startswith("data/crypto_basis_funding_research/"):
            failures.append("path_not_under_research_dir_%s" % key)
    if record.get("manifest_sha256") != MANIFEST_SHA256:
        failures.append("manifest_sha_tampered")
    if record.get("total_rows") != sum(v["rows"] for v in FILES.values()):
        failures.append("total_rows_wrong")
    if record.get("common_basis_window") != list(COMMON_BASIS_WINDOW):
        failures.append("common_window_tampered")

    # validation summary + public/no-creds + gitignored
    if record.get("all_timestamps_monotonic") is not True:
        failures.append("timestamps_not_monotonic")
    if record.get("all_columns_valid") is not True:
        failures.append("columns_not_valid")
    if record.get("public_data_only_no_credentials") is not True:
        failures.append("not_public_no_creds")
    if record.get("artifacts_gitignored_not_committed") is not True:
        failures.append("artifacts_not_gitignored")

    # readiness verdict + human gates
    if record.get("readiness_verdict") != (
            "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY"):
        failures.append("verdict_wrong")
    if record.get("requires_human_approval_before_c20") is not True:
        failures.append("c20_gate_missing")
    if record.get("opening_c20_requires_explicit_open_candidate_token") is not True:
        failures.append("c20_open_token_requirement_missing")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_assign_c20", "no_open_candidate", "no_fetch",
                "no_detector", "no_labels", "no_replay", "no_optimization",
                "no_data_commit", "no_credentials", "no_network", "no_xauusd",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
