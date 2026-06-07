"""Crypto-D1 Local Data Inventory Inspector (Block 140).

A read-only, RESEARCH_ONLY local data inventory inspector. Given caller-supplied
root folders, it LISTS already-downloaded local dataset files and reports what
coverage exists -- file names, extensions, sizes, and the symbol / timeframe /
date-range it can infer *from file and folder names only*. It is the tool a human
uses to see, before deciding whether any Databento read-only access is later
needed, what local data is already on disk.

It is read-only in the strongest sense:
  - It LISTS directory entries and reads file *sizes* (metadata) only.
  - It NEVER opens or reads file CONTENTS.
  - It NEVER reads, inspects, or records any credential / secret / .env file.
  - It NEVER touches the network, calls Databento, or downloads anything.
  - It NEVER writes a file, a manifest, a runtime output, or a dashboard output.
  - It NEVER follows symlinks (it skips them) and bounds its own depth / count.

Inference (symbol / timeframe / date range) is derived purely from filename and
folder-name patterns -- no file content is ever opened. A common layout such as
``SYMBOL_TIMEFRAME_START_END.csv`` (e.g. ``MGC_1d_2019-05-13_2025-12-31.csv``) is
parsed by name alone.

Producing this inventory authorizes nothing. real_data_qa stays BLOCKED, baseline
stays BLOCKED, the paper / micro-live gates stay LOCKED, and every trading /
execution capability flag stays False.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

Public API:
  - INSPECTOR_SCHEMA_VERSION / INSPECTOR_LABEL / INSPECTOR_STATUS / INSPECTOR_MODE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - DEFAULT_INSPECT_ROOTS
  - DEFAULT_REQUESTED_SYMBOLS / DEFAULT_REQUESTED_TIMEFRAMES
  - INSPECTOR_DATA_EXTENSIONS / INSPECTOR_SECRET_NAME_TOKENS / INSPECTOR_SKIP_DIRS
  - INSPECTOR_SAFETY_FLAGS
  - inspect_local_data_inventory(payload=None)
  - validate_local_data_inventory_report(report)
  - render_local_data_inventory_report_markdown(report)
"""

from __future__ import annotations

import os
import re
from typing import Any

INSPECTOR_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_local_data_inventory_inspector.v1"
)
INSPECTOR_LABEL = "Block 140 - Crypto-D1 Local Data Inventory Inspector"
INSPECTOR_STATUS = "READ_ONLY_LOCAL_DATA_INVENTORY"
INSPECTOR_MODE = "RESEARCH_ONLY"

# Mission-flow truth this inspector is anchored to. The companion test cross-checks
# these against the live status module so they cannot drift.
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# Default local roots the inspector intends to list when the caller supplies none.
# Listed by name only; if a folder is absent it is reported as not-found, never an
# error.
DEFAULT_INSPECT_ROOTS: tuple[str, ...] = (
    "data/databento_cache/",
    "data/databento_long_history/",
)

# Default Crypto-D1 coverage the human is asking about.
DEFAULT_REQUESTED_SYMBOLS: tuple[str, ...] = ("BTCUSD", "ETHUSD", "SOLUSD")
DEFAULT_REQUESTED_TIMEFRAMES: tuple[str, ...] = ("1d",)

# Extensions recognised as market-data files. Anything else is skipped (counted).
INSPECTOR_DATA_EXTENSIONS: tuple[str, ...] = (
    ".csv",
    ".tsv",
    ".parquet",
    ".pq",
    ".feather",
    ".json",
    ".jsonl",
    ".h5",
    ".hdf5",
    ".npy",
    ".npz",
    ".zip",
    ".gz",
    ".dbn",
    ".zst",
)

# Any file/dir whose lowercased name contains one of these is treated as a secret
# and skipped WITHOUT being listed, stat-ed for content, or recorded.
INSPECTOR_SECRET_NAME_TOKENS: tuple[str, ...] = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "password",
    "passwd",
    "apikey",
    "api_key",
    "token",
    "private_key",
    "id_rsa",
    "keystore",
    "wallet",
)

# Directory names never descended into.
INSPECTOR_SKIP_DIRS: tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "local_secrets",
)

# Safety bounds so a pathological tree cannot make the inspector run away.
_MAX_DEPTH = 12
_MAX_FILES = 200000

# Timeframe tokens recognised in a filename (lowercased).
_TIMEFRAME_RE = re.compile(r"^\d+(?:s|m|min|h|hr|d|w|mo|y)$")
_KNOWN_TIMEFRAMES = {
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "12h",
    "1d",
    "1w",
    "1mo",
}
# Uppercase symbol token, e.g. BTCUSD, MNQ, MGC, ETHUSD.
_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")

# Read-only safety posture. The posture facts are True; every capability /
# authorization / unlock flag is False.
INSPECTOR_SAFETY_FLAGS: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_required": True,
    "executes": False,
    "opens_file_contents": False,
    "reads_credentials": False,
    "inspects_dotenv": False,
    "calls_databento": False,
    "uses_network": False,
    "downloads_data": False,
    "writes_files": False,
    "writes_manifest": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "authorizes_trading": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_order_placement": False,
    "authorizes_account_control": False,
    "authorizes_strategy_promotion": False,
    "authorizes_automation_trading": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _norm(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    out: list[str] = []
    for item in value:
        text = _norm(item)
        if text:
            out.append(text)
    return out


def _is_secret_name(name: str) -> bool:
    low = name.lower()
    return any(tok in low for tok in INSPECTOR_SECRET_NAME_TOKENS)


def _pair(symbol: str, timeframe: str) -> str:
    return symbol + "@" + timeframe


def _infer_from_name(filename: str, rel_dir: str) -> dict[str, Any]:
    """Infer symbol / timeframe / dates from the file and folder NAMES only.
    Opens nothing. Returns {symbol, timeframe, dates:[...]}-ish dict."""
    stem = os.path.splitext(filename)[0]
    # split on common separators
    tokens = [t for t in re.split(r"[^A-Za-z0-9]+", stem) if t]

    symbol = ""
    timeframe = ""
    # The token split strips the dashes inside an ISO date, so scan the raw stem.
    dates = _all_dates(stem)

    for tok in tokens:
        low = tok.lower()
        if not timeframe and (low in _KNOWN_TIMEFRAMES or _TIMEFRAME_RE.match(low)):
            timeframe = low
            continue
        if not symbol and _SYMBOL_RE.match(tok):
            symbol = tok

    # folder-name fallbacks (e.g. .../BTCUSD/ or .../BTCUSD/1d/)
    if not symbol or not timeframe:
        for part in reversed([p for p in re.split(r"[\\/]+", rel_dir) if p]):
            low = part.lower()
            if not timeframe and (
                low in _KNOWN_TIMEFRAMES or _TIMEFRAME_RE.match(low)
            ):
                timeframe = low
            elif not symbol and _SYMBOL_RE.match(part):
                symbol = part

    return {"symbol": symbol, "timeframe": timeframe, "dates": sorted(dates)}


def _all_dates(text: str) -> list[str]:
    return re.findall(r"\d{4}-\d{2}-\d{2}", text)


# --------------------------------------------------------------------------- #
# read-only listing
# --------------------------------------------------------------------------- #
def _walk_root(base: str, files: list[dict[str, Any]], skipped: dict[str, int]) -> None:
    stack: list[tuple[str, int]] = [(base, 0)]
    while stack:
        if len(files) >= _MAX_FILES:
            return
        current, depth = stack.pop()
        if depth > _MAX_DEPTH:
            continue
        try:
            entries = list(os.scandir(current))
        except (PermissionError, OSError):
            continue
        for entry in sorted(entries, key=lambda e: e.name):
            name = entry.name
            try:
                is_link = entry.is_symlink()
            except OSError:
                is_link = False
            if is_link:
                skipped["symlinks"] += 1
                continue
            if _is_secret_name(name):
                skipped["secret"] += 1
                continue
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError:
                continue
            if is_dir:
                if name in INSPECTOR_SKIP_DIRS:
                    skipped["dirs"] += 1
                    continue
                stack.append((entry.path, depth + 1))
                continue
            if not is_file:
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in INSPECTOR_DATA_EXTENSIONS:
                skipped["non_data"] += 1
                continue
            try:
                size = entry.stat(follow_symlinks=False).st_size
            except OSError:
                size = -1
            rel_path = os.path.relpath(entry.path, base)
            rel_dir = os.path.dirname(rel_path)
            inferred = _infer_from_name(name, rel_dir)
            files.append(
                {
                    "name": name,
                    "ext": ext,
                    "size_bytes": size,
                    "rel_path": rel_path.replace("\\", "/"),
                    "symbol": inferred["symbol"],
                    "timeframe": inferred["timeframe"],
                    "dates": inferred["dates"],
                }
            )
            if len(files) >= _MAX_FILES:
                return


def _aggregate_pairs(
    files: list[dict[str, Any]],
) -> tuple[list[str], dict[str, dict[str, str]]]:
    ranges: dict[str, dict[str, str]] = {}
    for f in files:
        sym = f["symbol"]
        tf = f["timeframe"]
        if not sym or not tf:
            continue
        pair = _pair(sym, tf)
        dates = f.get("dates") or []
        if not dates:
            ranges.setdefault(pair, {"start": "", "end": ""})
            continue
        start, end = dates[0], dates[-1]
        cur = ranges.get(pair)
        if cur is None:
            ranges[pair] = {"start": start, "end": end}
        else:
            if not cur["start"] or (start and start < cur["start"]):
                cur["start"] = start
            if not cur["end"] or (end and end > cur["end"]):
                cur["end"] = end
    discovered = sorted(ranges.keys())
    return discovered, ranges


def inspect_local_data_inventory(payload: Any = None) -> dict[str, Any]:
    """List (read-only) the caller-supplied local dataset roots and report the
    inventory. Opens no file contents, reads no secret, touches no network, writes
    nothing. Returns a fresh in-memory report dict every call."""
    data = dict(payload) if isinstance(payload, dict) else {}

    roots = _as_str_list(data.get("roots")) or list(DEFAULT_INSPECT_ROOTS)
    requested_symbols = _as_str_list(data.get("requested_symbols")) or list(
        DEFAULT_REQUESTED_SYMBOLS
    )
    requested_timeframes = _as_str_list(
        data.get("requested_timeframes")
    ) or list(DEFAULT_REQUESTED_TIMEFRAMES)

    folders_inspected: list[dict[str, Any]] = []
    all_files: list[dict[str, Any]] = []
    skipped_total = {"dirs": 0, "secret": 0, "symlinks": 0, "non_data": 0}

    for root in roots:
        abs_root = os.path.realpath(root)
        exists = os.path.isdir(abs_root)
        files: list[dict[str, Any]] = []
        skipped = {"dirs": 0, "secret": 0, "symlinks": 0, "non_data": 0}
        if exists:
            _walk_root(abs_root, files, skipped)
        for key in skipped_total:
            skipped_total[key] += skipped[key]
        for f in files:
            rec = dict(f)
            rec["root"] = root
            all_files.append(rec)
        folders_inspected.append(
            {
                "root": root,
                "abs_path": abs_root,
                "exists": exists,
                "file_count": len(files),
                "skipped": dict(skipped),
            }
        )

    all_files.sort(key=lambda f: (f["root"], f["rel_path"]))
    discovered_pairs, date_ranges = _aggregate_pairs(all_files)

    requested_pairs: list[str] = []
    seen: set[str] = set()
    for sym in requested_symbols:
        for tf in requested_timeframes:
            p = _pair(sym, tf)
            if p not in seen:
                seen.add(p)
                requested_pairs.append(p)
    discovered_set = set(discovered_pairs)
    missing_pairs = [p for p in requested_pairs if p not in discovered_set]
    covered_pairs = [p for p in requested_pairs if p in discovered_set]

    databento_may_be_needed_later = bool(missing_pairs)

    report: dict[str, Any] = {
        "schema_version": INSPECTOR_SCHEMA_VERSION,
        "label": INSPECTOR_LABEL,
        "status": INSPECTOR_STATUS,
        "mode": INSPECTOR_MODE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "requested_symbols": requested_symbols,
        "requested_timeframes": requested_timeframes,
        "requested_pairs": requested_pairs,
        # 1. folders inspected
        "folders_inspected": folders_inspected,
        # 2. files found
        "files_found": all_files,
        "file_count": len(all_files),
        # 3. symbols / timeframes discovered
        "discovered_pairs": discovered_pairs,
        "covered_pairs": covered_pairs,
        # 4. date ranges discovered (if safely inferable from names)
        "date_ranges": date_ranges,
        # 5. missing symbols / timeframes from requested set
        "missing_pairs": missing_pairs,
        # 6. whether Databento may be needed later
        "databento_may_be_needed_later": databento_may_be_needed_later,
        "skipped_totals": skipped_total,
        # 7. no-write confirmation
        "no_write_confirmation": {
            "wrote_no_files": True,
            "wrote_no_manifest": True,
            "wrote_no_runtime_output": True,
            "wrote_no_dashboard_output": True,
        },
        # 8. no-secret confirmation
        "no_secret_confirmation": {
            "opened_no_file_contents": True,
            "read_no_credentials": True,
            "inspected_no_dotenv": True,
            "recorded_no_secret_file": True,
            "secret_named_entries_skipped": skipped_total["secret"],
        },
        # 9. safety confirmation
        "safety_confirmation": {
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
            "all_trading_execution_flags_false": True,
        },
        "safety_flags": dict(INSPECTOR_SAFETY_FLAGS),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "opens_file_contents": False,
        "reads_credentials": False,
        "inspects_dotenv": False,
        "calls_databento": False,
        "uses_network": False,
        "downloads_data": False,
        "writes_files": False,
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
    }
    return report


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_REPORT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "folders_inspected",
    "files_found",
    "discovered_pairs",
    "date_ranges",
    "missing_pairs",
    "databento_may_be_needed_later",
    "no_write_confirmation",
    "no_secret_confirmation",
    "safety_confirmation",
    "safety_flags",
)

_ALL_FALSE_FLAGS: tuple[str, ...] = (
    "executes",
    "opens_file_contents",
    "reads_credentials",
    "inspects_dotenv",
    "calls_databento",
    "uses_network",
    "downloads_data",
    "writes_files",
    "unlocks_real_data_qa",
)


def validate_local_data_inventory_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a built inventory report. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    r = report if isinstance(report, dict) else {}
    missing_fields = [f for f in _REQUIRED_REPORT_FIELDS if f not in r]

    schema_ok = r.get("schema_version") == INSPECTOR_SCHEMA_VERSION
    label_ok = r.get("label") == INSPECTOR_LABEL
    status_ok = r.get("status") == INSPECTOR_STATUS
    mode_ok = r.get("mode") == INSPECTOR_MODE
    mission_flow_refs_ok = (
        r.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and r.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    read_only = r.get("read_only") is True
    research_only = r.get("research_only") is True
    flags_false = all(r.get(f) is False for f in _ALL_FALSE_FLAGS)
    posture_ok = r.get("safety_flags") == INSPECTOR_SAFETY_FLAGS
    states_blocked_locked = (
        r.get("real_data_qa_state") == "BLOCKED"
        and r.get("baseline_backtest_state") == "BLOCKED"
        and r.get("paper_live_state") == "LOCKED"
    )

    no_write = r.get("no_write_confirmation")
    no_write_ok = isinstance(no_write, dict) and all(
        no_write.get(k) is True
        for k in (
            "wrote_no_files",
            "wrote_no_manifest",
            "wrote_no_runtime_output",
            "wrote_no_dashboard_output",
        )
    )
    no_secret = r.get("no_secret_confirmation")
    no_secret_ok = isinstance(no_secret, dict) and all(
        no_secret.get(k) is True
        for k in (
            "opened_no_file_contents",
            "read_no_credentials",
            "inspected_no_dotenv",
            "recorded_no_secret_file",
        )
    )

    safety = r.get("safety_confirmation")
    safety_ok = isinstance(safety, dict) and (
        safety.get("real_data_qa_state") == "BLOCKED"
        and safety.get("baseline_backtest_state") == "BLOCKED"
        and safety.get("paper_live_state") == "LOCKED"
        and safety.get("all_trading_execution_flags_false") is True
    )

    files = r.get("files_found")
    files_is_list = isinstance(files, list)
    # defense in depth: no listed file is secret-named.
    no_secret_file_listed = files_is_list and not any(
        _is_secret_name(str(f.get("name", ""))) for f in files
    )
    # databento-needed must be a bool consistent with missing pairs.
    db_flag = r.get("databento_may_be_needed_later")
    db_flag_is_bool = isinstance(db_flag, bool)
    missing_pairs = r.get("missing_pairs")
    db_flag_consistent = (
        db_flag_is_bool
        and isinstance(missing_pairs, list)
        and db_flag == bool(missing_pairs)
    )

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "read_only": read_only,
        "research_only": research_only,
        "flags_false": flags_false,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "no_write_ok": no_write_ok,
        "no_secret_ok": no_secret_ok,
        "safety_ok": safety_ok,
        "files_is_list": files_is_list,
        "no_secret_file_listed": no_secret_file_listed,
        "db_flag_is_bool": db_flag_is_bool,
        "db_flag_consistent": db_flag_consistent,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
    return verdict


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def _emit(lines: list[str], heading: str, rows: list[str]) -> None:
    lines.append("")
    lines.append("## " + heading)
    if not rows:
        lines.append("- (none)")
        return
    for row in rows:
        lines.append("- " + row)


def render_local_data_inventory_report_markdown(report: Any) -> str:
    """Render a built inventory report as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Local Data Inventory")
    lines.append("")
    lines.append("- Label: " + str(r.get("label", "")))
    lines.append("- Mode: " + str(r.get("mode", "")))
    lines.append("- Status: " + str(r.get("status", "")))
    lines.append("- File count: " + str(r.get("file_count", 0)))
    lines.append(
        "- real_data_qa: "
        + str(r.get("real_data_qa_state", ""))
        + " | baseline: "
        + str(r.get("baseline_backtest_state", ""))
        + " | paper/live: "
        + str(r.get("paper_live_state", ""))
    )
    lines.append(
        "- Databento may be needed later: "
        + str(r.get("databento_may_be_needed_later", False))
    )

    _emit(
        lines,
        "1. Folders Inspected",
        [
            str(f.get("root"))
            + " (exists="
            + str(f.get("exists"))
            + ", files="
            + str(f.get("file_count"))
            + ")"
            for f in (r.get("folders_inspected") or [])
        ],
    )
    _emit(
        lines,
        "2. Files Found",
        [
            str(f.get("rel_path"))
            + " ["
            + str(f.get("size_bytes"))
            + " bytes]"
            for f in (r.get("files_found") or [])
        ],
    )
    _emit(lines, "3. Symbols / Timeframes Discovered", list(r.get("discovered_pairs") or []))
    _emit(
        lines,
        "4. Date Ranges Discovered",
        [
            str(pair) + ": " + str(rng.get("start", "")) + " -> " + str(rng.get("end", ""))
            for pair, rng in (r.get("date_ranges") or {}).items()
        ],
    )
    _emit(lines, "5. Missing Pairs (requested but absent)", list(r.get("missing_pairs") or []))
    _emit(
        lines,
        "6. Databento Needed Later",
        [str(r.get("databento_may_be_needed_later", False))],
    )
    _emit(
        lines,
        "7. No-Write Confirmation",
        [str(k) + ": " + str(v) for k, v in (r.get("no_write_confirmation") or {}).items()],
    )
    _emit(
        lines,
        "8. No-Secret Confirmation",
        [str(k) + ": " + str(v) for k, v in (r.get("no_secret_confirmation") or {}).items()],
    )
    _emit(
        lines,
        "9. Safety Confirmation",
        [str(k) + ": " + str(v) for k, v in (r.get("safety_confirmation") or {}).items()],
    )
    return "\n".join(lines)
