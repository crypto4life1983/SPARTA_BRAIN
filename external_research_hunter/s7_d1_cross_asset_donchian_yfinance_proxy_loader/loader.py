"""Canonical loader for s7 D1 cross-asset daily-bar CSVs (ETF proxy track).

Read-only adapter over the four sealed CSVs at
data/s7_d1_cross_asset_donchian/raw/ that Step 02b deposited and Step 02c
audited (verdict PASS). Performs sha256 verification on every call against
the pinned values in audit_manifest.json. Returns LoadedSymbol structures
with both close and adj_close preserved separately (per Step 02c audit
finding F1: the manifest's divergence metric is the relative one; close
and adj_close differ and the loader exposes both so downstream chooses).

This loader contains no signal-side logic. It does not compute channel
breakouts, smoothing statistics, exposure decisions, position sizing, or
any backtest step. It does not import vendor SDKs and performs no network
IO. Importing this module performs no file IO; reading happens lazily
inside load_symbol() / load_all().

Refusal modes (LoaderError tree):

  - LoaderManifestMissingError - audit_manifest.json missing, malformed,
    or sha256 does not match the pin.
  - LoaderShaMismatchError - per-symbol CSV sha256 does not match the
    audit_manifest pin.
  - LoaderShapeMismatchError - row count, column set, dtypes, or per-row
    OHLCV invariants violate the spec.
  - LoaderCrossSymbolAlignmentError - load_all detects cross-symbol date
    set mismatch.
  - LoaderError - base class; also raised for unknown symbol input.

Spec anchor:
  docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md
  sha256 a713354bdb81dd10f5621aae18ab8f92adac5c3340a82e9d09bdb5ae1bbe2107
  commit f759251b238cd764fc96e0d62d814fd6c5ab3656
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

# -- Public constants ----------------------------------------------------
SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})
LOCKED_COLS = ("date", "open", "high", "low", "close", "adj_close", "volume")
RAW_DIR = Path("data/s7_d1_cross_asset_donchian/raw")
AUDIT_MANIFEST_PATH = RAW_DIR / "audit_manifest.json"
EXPECTED_ROWS = 3116
EXPECTED_FIRST_DATE = "2014-01-02"
EXPECTED_LAST_DATE = "2026-05-22"

# -- Private constants ---------------------------------------------------
_AUDIT_MANIFEST_PIN_SHA256 = (
    "794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb"
)


# -- Exception tree ------------------------------------------------------
class LoaderError(Exception):
    """Base for every loader refusal mode."""


class LoaderManifestMissingError(LoaderError):
    """audit_manifest.json missing, malformed, or sha256 mismatch."""


class LoaderShaMismatchError(LoaderError):
    """Per-symbol CSV sha256 mismatch against audit_manifest pin."""


class LoaderShapeMismatchError(LoaderError):
    """Row count, column set, dtype, or invariant violation."""


class LoaderCrossSymbolAlignmentError(LoaderError):
    """Cross-symbol date set mismatch (load_all path only)."""


# -- Loaded payload ------------------------------------------------------
@dataclass(frozen=True)
class LoadedSymbol:
    """Immutable per-symbol load result. Tuple fields have length EXPECTED_ROWS."""
    symbol: str
    dates: tuple
    open: tuple
    high: tuple
    low: tuple
    close: tuple
    adj_close: tuple
    volume: tuple
    csv_path: str
    csv_sha256: str


# -- Private helpers -----------------------------------------------------
def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _csv_path_for(symbol: str) -> Path:
    return RAW_DIR / f"{symbol}_1d_2014-01-01_2026-05-25.csv"


def _load_audit_manifest() -> Mapping:
    """Read audit_manifest.json, verify sha256 against pin, parse JSON.
    Raises LoaderManifestMissingError on any failure.
    """
    if not AUDIT_MANIFEST_PATH.exists():
        raise LoaderManifestMissingError(
            f"audit_manifest.json missing at {AUDIT_MANIFEST_PATH}"
        )
    raw = AUDIT_MANIFEST_PATH.read_bytes()
    observed_sha = _sha256_bytes(raw)
    if observed_sha != _AUDIT_MANIFEST_PIN_SHA256:
        raise LoaderManifestMissingError(
            f"audit_manifest.json sha256 mismatch at {AUDIT_MANIFEST_PATH}: "
            f"observed {observed_sha}; pinned {_AUDIT_MANIFEST_PIN_SHA256}"
        )
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise LoaderManifestMissingError(
            f"audit_manifest.json malformed at {AUDIT_MANIFEST_PATH}: {e!r}"
        )


def _verify_price(p_str: str, label: str) -> float:
    try:
        p = float(p_str)
    except ValueError:
        raise LoaderShapeMismatchError(f"{label} not numeric: {p_str!r}")
    if p != p or p == float("inf") or p == float("-inf"):
        raise LoaderShapeMismatchError(f"{label} not finite: {p_str!r}")
    if p <= 0:
        raise LoaderShapeMismatchError(f"{label} not positive: {p_str!r}")
    return p


def _verify_volume(v_str: str) -> int:
    try:
        v = float(v_str)
    except ValueError:
        raise LoaderShapeMismatchError(f"volume not numeric: {v_str!r}")
    if v != v or v == float("inf") or v == float("-inf"):
        raise LoaderShapeMismatchError(f"volume not finite: {v_str!r}")
    if v < 0:
        raise LoaderShapeMismatchError(f"volume negative: {v_str!r}")
    iv = int(v)
    if v != float(iv):
        raise LoaderShapeMismatchError(f"volume has fractional part: {v_str!r}")
    return iv


def _load_symbol_with_manifest(symbol: str, manifest: Mapping) -> LoadedSymbol:
    """Inner load given a parsed manifest dict.  Shared by load_symbol / load_all."""
    if symbol not in SYMBOLS:
        raise LoaderError(
            f"unknown symbol {symbol!r}; expected one of {sorted(SYMBOLS)}"
        )
    per_sym = manifest.get("per_symbol", {}).get(symbol)
    if per_sym is None or not isinstance(per_sym, dict):
        raise LoaderManifestMissingError(
            f"audit_manifest.json has no per_symbol entry for {symbol!r}"
        )
    expected_sha = per_sym.get("observed_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise LoaderManifestMissingError(
            f"audit_manifest.json per_symbol[{symbol}].observed_sha256 "
            f"missing or invalid"
        )
    csv_path = _csv_path_for(symbol)
    if not csv_path.exists():
        raise LoaderShaMismatchError(
            f"CSV missing for {symbol} at {csv_path}; cannot verify sha256"
        )
    csv_bytes = csv_path.read_bytes()
    observed_sha = _sha256_bytes(csv_bytes)
    if observed_sha != expected_sha:
        raise LoaderShaMismatchError(
            f"CSV sha256 mismatch for {symbol} at {csv_path}: "
            f"observed {observed_sha}; pinned {expected_sha}"
        )
    try:
        text = csv_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise LoaderShapeMismatchError(f"{csv_path} not UTF-8: {e!r}")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        raise LoaderShapeMismatchError(f"{csv_path} empty")
    header = tuple(rows[0])
    if header != LOCKED_COLS:
        raise LoaderShapeMismatchError(
            f"{csv_path} header mismatch: observed {header}; expected {LOCKED_COLS}"
        )
    data = rows[1:]
    if len(data) != EXPECTED_ROWS:
        raise LoaderShapeMismatchError(
            f"{csv_path} row count {len(data)} != expected {EXPECTED_ROWS}"
        )
    dates: list = []
    opens: list = []
    highs: list = []
    lows: list = []
    closes: list = []
    adj_closes: list = []
    volumes: list = []
    prev_date = None
    for i, r in enumerate(data):
        if len(r) != 7:
            raise LoaderShapeMismatchError(
                f"{csv_path} row {i} has {len(r)} columns, expected 7"
            )
        d_str, o, h, lo, c, ac, v = r
        if len(d_str) != 10:
            raise LoaderShapeMismatchError(
                f"{csv_path} row {i} date {d_str!r} not 10 chars"
            )
        try:
            d_obj = _dt.date.fromisoformat(d_str)
        except ValueError:
            raise LoaderShapeMismatchError(
                f"{csv_path} row {i} date {d_str!r} not ISO format"
            )
        if prev_date is not None and not (d_obj > prev_date):
            raise LoaderShapeMismatchError(
                f"{csv_path} row {i} date {d_str} not > previous "
                f"{prev_date.isoformat()}"
            )
        prev_date = d_obj
        o_f = _verify_price(o, f"row {i} open")
        h_f = _verify_price(h, f"row {i} high")
        lo_f = _verify_price(lo, f"row {i} low")
        c_f = _verify_price(c, f"row {i} close")
        ac_f = _verify_price(ac, f"row {i} adj_close")
        v_i = _verify_volume(v)
        if not (h_f >= o_f and h_f >= c_f and h_f >= lo_f
                and lo_f <= o_f and lo_f <= c_f):
            raise LoaderShapeMismatchError(
                f"{csv_path} row {i} OHLC invariant violation: "
                f"open={o_f} high={h_f} low={lo_f} close={c_f}"
            )
        dates.append(d_str)
        opens.append(o_f)
        highs.append(h_f)
        lows.append(lo_f)
        closes.append(c_f)
        adj_closes.append(ac_f)
        volumes.append(v_i)
    if dates[0] != EXPECTED_FIRST_DATE:
        raise LoaderShapeMismatchError(
            f"{csv_path} first date {dates[0]} != expected {EXPECTED_FIRST_DATE}"
        )
    if dates[-1] != EXPECTED_LAST_DATE:
        raise LoaderShapeMismatchError(
            f"{csv_path} last date {dates[-1]} != expected {EXPECTED_LAST_DATE}"
        )
    return LoadedSymbol(
        symbol=symbol,
        dates=tuple(dates),
        open=tuple(opens),
        high=tuple(highs),
        low=tuple(lows),
        close=tuple(closes),
        adj_close=tuple(adj_closes),
        volume=tuple(volumes),
        csv_path=str(csv_path),
        csv_sha256=observed_sha,
    )


# -- Public API ----------------------------------------------------------
def load_symbol(symbol: str) -> LoadedSymbol:
    """Load one symbol from the canonical raw CSV.

    Verifies audit_manifest.json sha256, the per-symbol CSV sha256, row
    count, columns, date format, monotonic dates, first/last date pins,
    OHLC invariants, finite positive prices, and non-negative integer
    volume. Raises a LoaderError subclass on any failure.
    """
    manifest = _load_audit_manifest()
    return _load_symbol_with_manifest(symbol, manifest)


def load_all() -> dict:
    """Load all four symbols and verify cross-symbol date alignment.

    Returns a dict keyed by symbol. Raises LoaderCrossSymbolAlignmentError
    if the four date sets are not identical.
    """
    manifest = _load_audit_manifest()
    out: dict = {}
    date_sets: dict = {}
    for sym in sorted(SYMBOLS):
        ls = _load_symbol_with_manifest(sym, manifest)
        out[sym] = ls
        date_sets[sym] = frozenset(ls.dates)
    canonical = None
    canonical_sym = None
    for sym in sorted(SYMBOLS):
        if canonical is None:
            canonical = date_sets[sym]
            canonical_sym = sym
        elif date_sets[sym] != canonical:
            diff = sorted(date_sets[sym] ^ canonical)[:10]
            raise LoaderCrossSymbolAlignmentError(
                f"cross-symbol date set mismatch: {sym} vs {canonical_sym}; "
                f"first 10 symmetric differences: {diff}"
            )
    return out
