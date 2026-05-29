"""Append-only paper ledgers. paper_orders.jsonl + paper_trades_closed.jsonl are NEVER truncated or rewritten."""

import json as _json
import pathlib as _pathlib


class AppendOnlyViolation(RuntimeError):
    pass


def _append_jsonl(path, record):
    p = _pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # APPEND-ONLY: open strictly in append mode; never 'w'/'r+'.
    with open(p, "a", encoding="utf-8") as f:
        f.write(_json.dumps(record, sort_keys=True, ensure_ascii=False, default=str) + "\n")
    return str(p)


def append_order_record(path, record):
    return _append_jsonl(path, record)


def append_closed_trade(path, record):
    return _append_jsonl(path, record)


def assert_append_only(mode):
    """Guard: only 'a' (append) is permitted for the ledgers; refuse any truncating/overwriting mode."""
    if mode not in ("a", "ab", "a+"):
        raise AppendOnlyViolation("APPEND_ONLY: ledger open mode %r is forbidden; only append ('a') is allowed." % mode)
    return True


def read_all(path):
    p = _pathlib.Path(path)
    if not p.exists():
        return []
    return [_json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
