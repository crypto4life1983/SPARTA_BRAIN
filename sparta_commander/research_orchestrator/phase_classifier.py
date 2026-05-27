"""Classify a commit by lifecycle phase.

Heuristic: subject-line keywords + file-path patterns. Conservative; falls
back to UNKNOWN rather than guess.
"""

from __future__ import annotations

import re

from .state import (
    PHASE_DRAFT, PHASE_DUPLICATE_CHAIN, PHASE_OBSERVATION, PHASE_P1, PHASE_P10_OOS,
    PHASE_P11_LIFECYCLE, PHASE_P2, PHASE_P3_BUILD, PHASE_P4_SMOKE, PHASE_P6_5_COST_STRESS,
    PHASE_P6_IS, PHASE_P7_DECISION, PHASE_PLAN, PHASE_SEAL, PHASE_SUPPLEMENT, PHASE_UNKNOWN,
)


# Order matters: more specific patterns first.
_PHASE_RULES: list[tuple[str, list[re.Pattern[str]], list[re.Pattern[str]]]] = [
    # (phase, subject_patterns, file_patterns)
    (PHASE_SUPPLEMENT, [
        re.compile(r"l1[\s_-]?carry[\s_-]?(forward[\s_-]?)?supplement", re.I),
        re.compile(r"l1[\s_-]?gap[\s_-]?(closure[\s_-]?)?addendum", re.I),
        re.compile(r"l1[\s_-]?discount[\s_-]?memo", re.I),
        re.compile(r"carry[\s_-]?supplement", re.I),
    ], [
        re.compile(r"_l1_carry_supplement_sealed\.(json|md)$"),
        re.compile(r"_l1_gap_closure_addendum_sealed\.(json|md)$"),
        re.compile(r"_l1_discount_memo_sealed\.(json|md)$"),
    ]),
    (PHASE_P11_LIFECYCLE, [
        re.compile(r"\bp11\b", re.I),
        re.compile(r"lifecycle\s*(park|decision)\s*memo", re.I),
        re.compile(r"\bPARK\b"),
        re.compile(r"PARKED_SAFE_BUT_", re.I),
    ], [
        re.compile(r"_p11_lifecycle_(park|memo).*sealed\.(json|md)$"),
        re.compile(r"_p11_lifecycle_park_decision_sealed\.(json|md)$"),
    ]),
    (PHASE_P10_OOS, [
        re.compile(r"\bp10\b", re.I),
        re.compile(r"oos\s*(gate|diagnostic)", re.I),
    ], [
        re.compile(r"_p10_oos_gate_sealed\.(json|md)$"),
        re.compile(r"_out_of_sample_(diagnostic|gate)_result_sealed\.(json|md)$"),
    ]),
    (PHASE_P7_DECISION, [
        re.compile(r"\bp7\b", re.I),
        re.compile(r"decision\s*memo", re.I),
    ], [
        re.compile(r"_p7_decision_memo_sealed\.(json|md)$"),
    ]),
    (PHASE_P6_5_COST_STRESS, [
        re.compile(r"\bp6[._]5\b", re.I),
        re.compile(r"cost[\s_-]?stress\s*(matrix|sweep)", re.I),
    ], [
        re.compile(r"_cost_stress_matrix_result_sealed\.(json|md)$"),
        re.compile(r"_p6_5_cost_stress.*sealed\.(json|md)$"),
    ]),
    (PHASE_P6_IS, [
        re.compile(r"\bp6\s*is\s*(diagnostic|run|result)", re.I),
        re.compile(r"in[\s_-]?sample\s*diagnostic", re.I),
    ], [
        re.compile(r"_in_sample_diagnostic_result_sealed\.(json|md)$"),
        re.compile(r"_p6_is_diagnostic_result.*sealed\.(json|md)$"),
    ]),
    (PHASE_P4_SMOKE, [
        re.compile(r"\bp4\s*(synthetic\s*)?smoke", re.I),
        re.compile(r"smoke\s*t1[\s_-]?t15", re.I),
        re.compile(r"synthetic\s*smoke", re.I),
    ], [
        re.compile(r"_smoke_t1_t15_report\.(json|md)$"),
        re.compile(r"_p4_synthetic_smoke_report\.(json|md)$"),
    ]),
    (PHASE_P3_BUILD, [
        re.compile(r"\bp3\s*build", re.I),
        re.compile(r"runner\s*harness", re.I),
        re.compile(r"BUILD\s+s\d+[\s_-]?d\d+", re.I),
    ], [
        re.compile(r"_runner_harness/"),
        re.compile(r"_runner_build_report\.(json|md)$"),
        re.compile(r"_(in|out_of)_sample_driver_build_report\.(json|md)$"),
    ]),
    (PHASE_P2, [
        re.compile(r"\bp2\b", re.I),
        re.compile(r"phase[\s_-]?2[\s_-]?plan", re.I),
    ], [
        re.compile(r"_p2_phase2_plan_sealed\.(json|md)$"),
        re.compile(r"_p2_phase_2_plan.*sealed\.(json|md)$"),
    ]),
    (PHASE_P1, [
        re.compile(r"\bp1\b", re.I),
        re.compile(r"plan[\s_-]?lock", re.I),
    ], [
        re.compile(r"_p1_plan_lock_sealed\.(json|md)$"),
        re.compile(r"_p1_plan_lock\.md$"),
    ]),
    (PHASE_SEAL, [
        re.compile(r"\bSEAL\b"),
        re.compile(r"tier[\s_-]?n\s*spec", re.I),
        re.compile(r"sealed\s*at\s*operator[\s_-]?authorized\s*paths", re.I),
    ], [
        re.compile(r"_tier_n_spec_sealed\.(json|md)$"),
        re.compile(r"_tier_n_spec\.md$"),
    ]),
    (PHASE_DRAFT, [
        re.compile(r"\bDRAFT\b"),
    ], [
        re.compile(r"_DRAFT\.md$"),
        re.compile(r"_tier_n_spec_DRAFT\.md$"),
    ]),
    (PHASE_PLAN, [
        re.compile(r"\bPLAN\b"),
        re.compile(r"selection\s*plan", re.I),
        re.compile(r"tier[\s_-]?n\s*spec\s*PLAN", re.I),
    ], [
        re.compile(r"_tier_n_spec_plan\.md$"),
        re.compile(r"_plan\.md$"),
        re.compile(r"next_research_track_selection_plan.*\.md$"),
    ]),
    (PHASE_OBSERVATION, [
        re.compile(r"observation\s*memo", re.I),
        re.compile(r"comparison\s*memo", re.I),
        re.compile(r"disambiguation\s*memo", re.I),
        re.compile(r"path[\s_-]?status\s*memo", re.I),
    ], [
        re.compile(r"_observation.*sealed\.(json|md)$"),
        re.compile(r"_comparison.*sealed\.(json|md)$"),
        re.compile(r"_disambiguation.*sealed\.(json|md)$"),
        re.compile(r"_path_status.*sealed\.(json|md)$"),
    ]),
]


def classify(subject: str, files: list[str]) -> str:
    """Return the best-matching phase string. UNKNOWN if no rule matches.

    Duplicate-chain takes precedence when ALL committed files use the SEAL-B
    short-slug naming convention (no `databento_long_history` infix).
    """
    if files and _looks_like_duplicate_chain(files):
        return PHASE_DUPLICATE_CHAIN

    for phase, subject_patterns, file_patterns in _PHASE_RULES:
        for pat in subject_patterns:
            if pat.search(subject):
                return phase
        for pat in file_patterns:
            for f in files:
                if pat.search(f):
                    return phase
    return PHASE_UNKNOWN


def _looks_like_duplicate_chain(files: list[str]) -> bool:
    """True iff every file uses SEAL-B short-slug convention.

    Heuristic: SEAL-B artifacts live at `reports/<short_slug>_*sealed.{json,md}`
    (top-level reports/, no `databento_long_history` infix). SEAL-A artifacts
    live at `reports/external_research_hunter/<long_slug>_databento_long_history_*sealed.{json,md}`.
    """
    if not files:
        return False
    report_files = [f for f in files if f.endswith(".json") or f.endswith(".md")]
    if not report_files:
        return False
    # All report files must look like duplicate chain (top-level reports/, no long-history infix)
    for f in report_files:
        if "external_research_hunter" in f:
            return False
        if "databento_long_history" in f:
            return False
        if not f.startswith("reports/"):
            return False
    return True
