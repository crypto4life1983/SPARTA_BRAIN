"""Deterministic, local safety classifier for future JARVIS conversation input.

This module is *preparation only* for a possible, separately-approved
``/api/jarvis/ask`` endpoint. It does **not** create any endpoint, route, or
backend. It is a pure-classification helper: given a plain-language question it
returns which safety class the question falls into and whether it must be
refused.

Safety posture (matches every committed JARVIS step):

- The classifier **executes nothing**. It runs no commands, no scripts, no
  trades; it writes no files; it opens no network connection; it imports no
  broker / trading / subprocess module. It only inspects the text of a string.
- It is **fail-closed**: empty input, ambiguous command-like input, and
  anything not recognised as a known-safe read-only question are refused as
  ``UNSUPPORTED``.
- **Forbidden overrides safe.** If a question mixes a safe phrase with a
  forbidden one (e.g. "explain the trading posture then place a trade"), the
  forbidden classification wins and the question is refused.

The only forbidden-action vocabulary that appears below is *blocked keyword
text* used to recognise and refuse dangerous questions — never to perform them.

Public API: :func:`classify_jarvis_question`.
"""
from __future__ import annotations

import re

__all__ = [
    "classify_jarvis_question",
    "SAFETY_LABELS",
    "SAFE_LABELS",
    "FORBIDDEN_LABELS",
]

# --- label vocabulary ------------------------------------------------------

SAFE_LABELS = (
    "SAFE_INFO",
    "SAFE_EXPLAIN",
    "SAFE_NEXT_REVIEW_STEP",
)
FORBIDDEN_LABELS = (
    "FORBIDDEN_EXECUTION",
    "FORBIDDEN_TRADING",
    "FORBIDDEN_MUTATION",
)
SAFETY_LABELS = SAFE_LABELS + FORBIDDEN_LABELS + ("UNSUPPORTED",)


# --- forbidden patterns (checked first, fail-closed) -----------------------
# Each entry is a compiled regex searched against the lower-cased, whitespace-
# normalised question. The presence of any one of these means the question is
# asking JARVIS to act, so it is refused. Ordering within forbidden is
# TRADING -> EXECUTION -> MUTATION and is deterministic.

_FORBIDDEN_TRADING = tuple(re.compile(p) for p in (
    r"\bplace\s+(?:a\s+|an\s+)?(?:trade|order)\b",
    r"\bsubmit\s+(?:an\s+)?order\b",
    r"\bexecute\s+(?:a\s+)?trade\b",
    r"\bbuy\b",
    r"\bsell\b",
    r"\bgo\s+long\b",
    r"\bgo\s+short\b",
    r"\b(?:open|close)\s+(?:a\s+)?position\b",
    r"\b(?:long|short)\s+position\b",
    r"\benable\s+(?:live|paper)\s+trading\b",
    r"\barm\s+(?:live|paper)\b",
    r"\bconnect\s+(?:to\s+)?(?:my\s+|the\s+)?broker\b",
    r"\bapprove\b.*\bstrateg",
    r"\bpromote\b.*\bstrateg",
))

_FORBIDDEN_EXECUTION = tuple(re.compile(p) for p in (
    r"\brun\b.*\b(?:script|command|cmd|test|tests|probe|tool|pipeline)\b",
    r"\bexecute\b.*\b(?:command|script|cmd)\b",
    r"\b(?:trigger|do|start|kick\s+off)\b.*\brefresh\b",
    r"\brefresh\b",
    r"\bstage\b.*\bcommit\b",
    r"\bstage\s+and\s+commit\b",
    r"\bgit\s+(?:commit|add|push|stage|reset)\b",
    r"\bcommit\b",
    r"\bstage\b",
    r"\bopen\b.*\bterminal\b",
    r"\bopen\s+(?:a\s+|the\s+)?shell\b",
    r"\btrigger\b",
))

_FORBIDDEN_MUTATION = tuple(re.compile(p) for p in (
    r"\bmodify\b",
    r"\b(?:edit|change|update|overwrite)\b.*\b(?:file|app\.py|template|config|code|system)\b",
    r"\bwrite\b.*\b(?:to\s+)?(?:disk|file)\b",
    r"\bwrite\s+to\s+disk\b",
    r"\bedit\s+app\.py\b",
    r"\bupdate\s+(?:the\s+)?template\b",
    r"\bsave\b.*\b(?:chat\s+)?log\b",
    r"\bsave\b.*\bto\s+disk\b",
    r"\bdelete\b",
))

_FORBIDDEN_GROUPS = (
    ("FORBIDDEN_TRADING", _FORBIDDEN_TRADING,
     "asks JARVIS to place, enable, or approve trading — it has no order path."),
    ("FORBIDDEN_EXECUTION", _FORBIDDEN_EXECUTION,
     "asks JARVIS to run, refresh, stage, or commit — it executes nothing."),
    ("FORBIDDEN_MUTATION", _FORBIDDEN_MUTATION,
     "asks JARVIS to write, edit, or delete — it is a read-only surface."),
)


# --- safe patterns (checked only if no forbidden match) --------------------
# Ordering within safe is NEXT_REVIEW_STEP -> EXPLAIN -> INFO so that the more
# specific intent wins before the broad status-info catch.

_SAFE_NEXT_REVIEW = tuple(re.compile(p) for p in (
    r"\bsafest\s+next\b",
    r"\bnext\s+review\s+step\b",
    r"\bnext\s+safe\s+step\b",
    r"\bsafest\s+(?:next\s+)?(?:review\s+)?step\b",
    r"\bwhat\s+(?:should\s+i|to)\s+review\s+next\b",
    r"\breview\s+next\b",
))

_SAFE_EXPLAIN = tuple(re.compile(p) for p in (
    r"\bwhat\s+does\b.*\bmean\b",
    r"\bwhat'?s\b.*\bmean\b",
    r"\bexplain\b",
    r"\bdefine\b",
    r"\bmeaning\s+of\b",
    r"\bwhat\s+is\s+read_only\b",
    r"\bwhat\s+does\s+read_only\b",
))

_SAFE_INFO = tuple(re.compile(p) for p in (
    r"\bwhy\s+is\b.*\bcommander\b",
    r"\bcommander\b.*\byellow\b",
    r"\bwhy\s+is\b.*\byellow\b",
    r"\bneeds?\s+attention\b",
    r"\bwhat\s+needs\b",
    r"\b(?:current|system|overall)\s+(?:status|state)\b",
    r"\bwhat\s+is\s+the\s+status\b",
    r"\bstatus\b",
    r"\btrading\s+posture\b",
    r"\btrading\s+status\b",
    # Read-only trading-posture questions. Forbidden patterns (e.g. "enable
    # paper trading", "connect broker") are matched FIRST, so these only
    # classify safe for genuinely read-only status questions.
    r"\bhow\s+are\s+we\s+doing\b",
    r"\bready\s+for\s+(?:paper|live)\s+trading\b",
    r"\b(?:paper|live)[_\s]?ready\b",
    r"\bbroker[_\s]?control\b",
    r"\bjarvis\s+docs\b",
    r"\bwhat\s+docs\b",
    r"\bdocs\s+exist\b",
    r"\bwhich\s+docs\b",
    r"\bis\s+it\s+read[_\s]?only\b",
    r"\bread[_\s]?only\b",
))

_SAFE_GROUPS = (
    ("SAFE_NEXT_REVIEW_STEP", _SAFE_NEXT_REVIEW,
     "asks for the safest next review step — answerable as docs-only / read-only options."),
    ("SAFE_EXPLAIN", _SAFE_EXPLAIN,
     "asks what a field/panel/doc means — answerable from committed glossary/runbook."),
    ("SAFE_INFO", _SAFE_INFO,
     "answerable from the current read-only status aggregate."),
)


def _normalise(question: str) -> str:
    """Return the question stripped and whitespace-collapsed (original case).

    Pure string normalisation only: no I/O, no evaluation, no execution.
    """
    return re.sub(r"\s+", " ", question.strip())


def classify_jarvis_question(question):
    """Classify a JARVIS conversation question as safe or forbidden.

    This function only *describes* the intent of the supplied text. It performs
    no action of any kind — it does not run commands, trade, refresh, write
    files, or touch the network. It is a pure function of its input.

    Parameters
    ----------
    question:
        The user's plain-language question. Non-string or empty input is
        treated as unanswerable and refused (fail-closed).

    Returns
    -------
    dict
        ``{"safety_class": <one of SAFETY_LABELS>, "refused": <bool>,
        "reason": <str>, "normalized_question": <str>}``.

        ``refused`` is ``False`` only for the three ``SAFE_*`` labels. Forbidden
        and ``UNSUPPORTED`` classifications are always refused.
    """
    if not isinstance(question, str):
        return {
            "safety_class": "UNSUPPORTED",
            "refused": True,
            "reason": "Non-text input cannot be answered from read-only context (fail-closed).",
            "normalized_question": "",
        }

    normalized = _normalise(question)
    if not normalized:
        return {
            "safety_class": "UNSUPPORTED",
            "refused": True,
            "reason": "Empty question cannot be answered from read-only context (fail-closed).",
            "normalized_question": "",
        }

    low = normalized.lower()

    # Forbidden first: forbidden always overrides any co-occurring safe phrase.
    for label, patterns, reason in _FORBIDDEN_GROUPS:
        for pat in patterns:
            if pat.search(low):
                return {
                    "safety_class": label,
                    "refused": True,
                    "reason": "JARVIS is read-only and " + reason,
                    "normalized_question": normalized,
                }

    # Safe next: only recognised read-only intents are allowed through.
    for label, patterns, reason in _SAFE_GROUPS:
        for pat in patterns:
            if pat.search(low):
                return {
                    "safety_class": label,
                    "refused": False,
                    "reason": "Read-only question: " + reason,
                    "normalized_question": normalized,
                }

    # Anything unrecognised (including ambiguous command-like input) is refused.
    return {
        "safety_class": "UNSUPPORTED",
        "refused": True,
        "reason": "Not a recognised read-only question; refused fail-closed.",
        "normalized_question": normalized,
    }
