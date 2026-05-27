"""Recompute the LESSON_HUNTER_004 canonical seal.

Recipe (from the chain-wide sealing standard):
    body = json.loads(file)
    body_check = {k: v for k, v in body.items()
                  if k not in ('report_seal_sha256', 'seal_method')}
    canonical = json.dumps(body_check, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False, default=str)
    expected_sha = sha256(canonical.encode('utf-8'))

Never alters files. Pure verification.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any


STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_MISSING = "MISSING"
STATUS_INVALID = "INVALID"


def canonical_recompute(body: dict[str, Any]) -> str:
    """LESSON_HUNTER_004 canonical recipe."""
    body_check = {k: v for k, v in body.items() if k not in ("report_seal_sha256", "seal_method")}
    canonical = json.dumps(
        body_check, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_seal(report_path: str | pathlib.Path) -> dict[str, Any]:
    """Verify a single sealed JSON report.

    Returns:
        {
          "status": "PASS"|"FAIL"|"MISSING"|"INVALID",
          "declared": <sha or None>,
          "recomputed": <sha or None>,
          "path": <str>,
          "bytes": <int or None>,
          "error": <str or None>,
        }
    """
    p = pathlib.Path(report_path)
    result: dict[str, Any] = {
        "status": STATUS_INVALID,
        "declared": None,
        "recomputed": None,
        "path": str(p),
        "bytes": None,
        "error": None,
    }
    if not p.exists():
        result["status"] = STATUS_MISSING
        result["error"] = "file does not exist"
        return result
    try:
        raw = p.read_text(encoding="utf-8")
        result["bytes"] = len(raw)
        body = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        result["status"] = STATUS_INVALID
        result["error"] = f"json parse: {e!s}"
        return result
    if not isinstance(body, dict):
        result["status"] = STATUS_INVALID
        result["error"] = "top-level JSON is not an object"
        return result
    declared = body.get("report_seal_sha256")
    result["declared"] = declared
    if declared is None:
        result["status"] = STATUS_MISSING
        result["error"] = "no report_seal_sha256 field"
        return result
    try:
        recomputed = canonical_recompute(body)
    except (TypeError, ValueError) as e:
        result["status"] = STATUS_INVALID
        result["error"] = f"canonical recompute: {e!s}"
        return result
    result["recomputed"] = recomputed
    result["status"] = STATUS_PASS if declared == recomputed else STATUS_FAIL
    return result


def verify_all(report_paths: list[str | pathlib.Path]) -> list[dict[str, Any]]:
    return [verify_seal(p) for p in report_paths]
