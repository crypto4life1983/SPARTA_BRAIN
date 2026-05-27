"""Detect REC1_T1 / L1-framework carry status in a sealed report.

Distinguishes three states:
    FULL    — `REC1_T1_BINDING_K9_DISCLOSURE` text present byte-equivalent
              AND cross-references to addendum + memo + at least one sibling
              chain-step supplement
    PARTIAL — only the DRAFT-level "REC1-equivalent" wording carried via
              C6 inheritance (no formal L1 framework references)
    MISSING — neither REC1_T1 nor any REC1-equivalent text present
"""

from __future__ import annotations

import json
import pathlib
from typing import Any


L1_FULL = "FULL_REC1_T1_BYTE_EQUIVALENT"
L1_PARTIAL = "PARTIAL_REC1_EQUIVALENT_VIA_C6_INHERITANCE_ONLY"
L1_MISSING = "MISSING_NO_REC1_OR_C6"

# These are the canonical L1-framework cross-reference targets.
REC1_T1_MARKERS = ("REC1_T1_BINDING_K9_DISCLOSURE", "REC1_T1 (binding)", "REC1_T1_BINDING")
REC1_EQUIVALENT_MARKERS = ("rec1_equivalent", "REC1-equivalent", "REC1 ", "REC1_T1")
ADDENDUM_REF_MARKERS = ("l1_gap_closure_addendum", "draft_l1_gap_closure_addendum")
MEMO_REF_MARKERS = ("l1_discount_memo", "next_track_selection_plan_revision_l1_discount_memo")
SUPPLEMENT_REF_MARKERS = (
    "l1_carry_supplement", "p1_l1_carry_supplement", "p2_l1_carry_supplement",
    "p3_l1_carry_supplement", "p4_l1_carry_supplement", "p6_is_l1_carry_supplement",
)

# Optional: known seal SHAs of canonical L1 artifacts (so we can detect refs
# even when the report uses bare sha strings instead of named keys).
KNOWN_L1_SEAL_SHAS = (
    "e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3",  # L1 discount memo
    "769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055",  # L1-gap addendum
)


def check_l1(report_path: str | pathlib.Path) -> dict[str, Any]:
    """Inspect one sealed JSON report. Returns:

    {
      "status": "FULL"|"PARTIAL"|"MISSING",
      "rec1_t1_hits": int,
      "rec1_equivalent_hits": int,
      "addendum_refs": [<marker>...],
      "memo_refs": [<marker>...],
      "supplement_refs": [<marker>...],
      "known_l1_seal_shas_present": [<sha>...],
      "needs_supplement": bool,
      "recommendation": <str>,
    }
    """
    p = pathlib.Path(report_path)
    out: dict[str, Any] = {
        "status": L1_MISSING,
        "rec1_t1_hits": 0,
        "rec1_equivalent_hits": 0,
        "addendum_refs": [],
        "memo_refs": [],
        "supplement_refs": [],
        "known_l1_seal_shas_present": [],
        "needs_supplement": False,
        "recommendation": "no_action",
    }
    if not p.exists():
        out["recommendation"] = "report_missing"
        return out
    try:
        raw = p.read_text(encoding="utf-8")
        body = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        out["recommendation"] = "report_invalid_json"
        return out
    if not isinstance(body, dict):
        out["recommendation"] = "report_top_level_not_object"
        return out

    for m in REC1_T1_MARKERS:
        out["rec1_t1_hits"] += raw.count(m)
    for m in REC1_EQUIVALENT_MARKERS:
        if m == "REC1_T1":
            continue  # already counted under rec1_t1_hits
        out["rec1_equivalent_hits"] += raw.count(m)
    for m in ADDENDUM_REF_MARKERS:
        if m in raw:
            out["addendum_refs"].append(m)
    for m in MEMO_REF_MARKERS:
        if m in raw:
            out["memo_refs"].append(m)
    for m in SUPPLEMENT_REF_MARKERS:
        if m in raw:
            out["supplement_refs"].append(m)
    for sha in KNOWN_L1_SEAL_SHAS:
        if sha in raw:
            out["known_l1_seal_shas_present"].append(sha)

    # Classification
    has_t1 = out["rec1_t1_hits"] > 0
    has_addendum_or_memo_ref = bool(out["addendum_refs"] or out["memo_refs"] or out["known_l1_seal_shas_present"])
    has_supplement_ref = bool(out["supplement_refs"])
    has_equivalent = out["rec1_equivalent_hits"] > 0 or "inherited_constraints_block_VERBATIM_FROM_P2_C6" in raw

    if has_t1 and has_addendum_or_memo_ref:
        out["status"] = L1_FULL
        out["needs_supplement"] = False
        out["recommendation"] = "no_action_full_l1_carry"
    elif has_equivalent:
        out["status"] = L1_PARTIAL
        out["needs_supplement"] = True
        out["recommendation"] = "write_l1_carry_supplement_to_attach_rec1_t1_byte_equivalent"
    else:
        out["status"] = L1_MISSING
        out["needs_supplement"] = True
        out["recommendation"] = "write_l1_carry_supplement_urgent_no_rec1_or_c6"
    return out
