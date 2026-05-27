"""Extract `parent_references` from sealed reports and verify against canonical chain.

A canonical chain is the operator-blessed sequence of commits (SEAL-A pattern).
A duplicate chain is the parallel SEAL-B pattern that the operator has
consistently chosen to acknowledge but not anchor.

Anchor mismatch = report references commits that are NOT in the candidate's
canonical_chain and ARE in the duplicate_chain or are unrecognized. HIGH risk.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any


RISK_OK = "OK"
RISK_NONE = "NONE"
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"


def extract_parent_references(report_path: str | pathlib.Path) -> dict[str, Any]:
    """Read parent_references / linked_seals_at_init / chain_anchors_byte_stable_at_park.

    Returns {} on parse failure.
    """
    p = pathlib.Path(report_path)
    if not p.exists():
        return {}
    try:
        body = json.loads(p.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if not isinstance(body, dict):
        return {}
    out: dict[str, Any] = {}
    for key in ("parent_references", "linked_seals_at_init", "chain_anchors_byte_stable_at_park"):
        if isinstance(body.get(key), dict):
            out.update(body[key])
    return out


def _extract_commit_shas_from_refs(refs: dict[str, Any]) -> set[str]:
    """Return all values that look like git short-shas (7+ hex chars)."""
    import re
    sha_pattern = re.compile(r"^[0-9a-f]{7,40}$")
    out: set[str] = set()
    for v in refs.values():
        if isinstance(v, str):
            # Match the bare sha or pull leading sha out of strings like "ecbd001 (TERMINAL)"
            tok = v.split()[0].strip() if v.split() else ""
            if sha_pattern.match(tok):
                out.add(tok[:7])
    return out


def verify_anchors(
    report_path: str | pathlib.Path,
    canonical_chain: list[str],
    duplicate_chain: list[str],
) -> dict[str, Any]:
    """Compare a report's parent_references against the candidate's chains.

    Returns:
        {
          "risk": "HIGH"|"MEDIUM"|"LOW"|"NONE",
          "anchors_found": [<short_sha>, ...],
          "anchors_in_canonical": [<sha>, ...],
          "anchors_in_duplicate": [<sha>, ...],
          "anchors_unknown": [<sha>, ...],
          "canonical_missing": [<sha>, ...],   # canonical chain commits NOT referenced
        }
    """
    refs = extract_parent_references(report_path)
    found = _extract_commit_shas_from_refs(refs)
    canonical_short = {c[:7] for c in canonical_chain}
    duplicate_short = {c[:7] for c in duplicate_chain}

    in_canonical = sorted(found & canonical_short)
    in_duplicate = sorted(found & duplicate_short)
    unknown = sorted(found - canonical_short - duplicate_short)
    missing = sorted(canonical_short - found)

    if in_duplicate:
        risk = RISK_HIGH
    elif unknown and not in_canonical:
        risk = RISK_HIGH
    elif unknown:
        risk = RISK_MEDIUM
    elif missing and len(missing) >= max(1, len(canonical_chain) // 2):
        risk = RISK_MEDIUM
    elif missing:
        risk = RISK_LOW
    else:
        risk = RISK_NONE

    return {
        "risk": risk,
        "anchors_found": sorted(found),
        "anchors_in_canonical": in_canonical,
        "anchors_in_duplicate": in_duplicate,
        "anchors_unknown": unknown,
        "canonical_missing": missing,
        "parent_references_keys": sorted(refs.keys()),
    }
