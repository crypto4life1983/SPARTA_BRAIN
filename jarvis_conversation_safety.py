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
    r"\bstart\s+trading\b",
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
    r"\brun\s+git\b",
    r"\bexecute\b.*\b(?:command|script|cmd|report|generator)\b",
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
    r"\bwrite\b.*\bsnapshot\b",
    r"\bsave\b.*\b(?:state|snapshot)\b",
    r"\bclean\b.*\b(?:untracked|tree|files?)\b",
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
    # Natural trading-status phrasings: "how is the trading doing", "trading
    # update", "what's going on with trading", "are we okay with trading", etc.
    # Apostrophe-independent (works for "how's"/"what's"). Forbidden is still
    # checked first, so "...then place a trade" / "...and buy NQ" stay refused.
    r"\btrad(?:e|es|ing)\b.*\b(?:status|update|overview|doing|going)\b",
    r"\b(?:status|update|overview|doing|going)\b.*\btrad(?:e|es|ing)\b",
    r"\bwith\s+trad(?:e|es|ing)\b",
    # Read-only "what changed?" change-summary questions (Step 43). Answered
    # conservatively from current status only: JARVIS keeps no baseline, so it
    # never claims a verified change without a provided snapshot. Forbidden
    # (refresh/run/write/commit/clean/trade) is still checked FIRST, so mixed
    # phrases like "what changed and refresh status" stay refused.
    r"\bchanged\b",
    r"\bchange\s+summary\b",
    r"\bwhat'?s\s+new\b",
    r"\bwhat\s+is\s+new\b",
    r"\bwhat\s+new\b",
    r"\bsummar(?:ize|ise)\s+(?:current\s+)?changes\b",
    r"\bjarvis\s+docs\b",
    r"\bwhat\s+docs\b",
    r"\bdocs\s+exist\b",
    r"\bwhich\s+docs\b",
    r"\bis\s+it\s+read[_\s]?only\b",
    r"\bread[_\s]?only\b",
    # JARVIS Conversational Intelligence v1 — natural greetings, briefings, and
    # status conversation. All read-only and answerable from the existing status
    # aggregate / committed report summaries. Forbidden patterns are still
    # matched FIRST, so mixed phrases like "good morning then buy NQ" or
    # "brief me then place a trade" stay refused.
    r"^(?:hi|hey|hello|hiya|yo|sup|gm|greetings)\b",
    r"^good\s+(?:morning|afternoon|evening|day)\b",
    r"\bgood\s+morning\b",
    r"\bhow\s+are\s+you\b",
    r"\bhow\s+are\s+u\b",
    r"\bhow'?s\s+it\s+going\b",
    r"\bhow\s+(?:are|r)\s+(?:you|u|things)\b",
    r"\bhow\s+you\s+doing\b",
    r"\bbrief(?:ing)?\b",
    r"\bbrief\s+me\b",
    r"\bstrategy\s+factory\b",
    r"\bfactory\s+(?:status|state|update|report|reports|progress|overview|summary)\b",
    r"\b(?:status|state|update|overview|progress)\b.*\bfactory\b",
    r"\bsparta\s+brain\b",
    r"\bbrain\s+status\b",
    r"\bwhat\s+happened\b",
    r"\blast\s+24\b",
    r"\bpast\s+24\b",
    r"\b24\s*hours?\b",
    r"\blast\s+day\b",
    r"\bour\s+trades?\b",
    r"\bmy\s+trades?\b",
    # JARVIS Executive Briefing Mode v1 — read-only overnight/executive
    # briefing intents and conversational follow-ups. All answerable from the
    # existing status aggregate / committed report summaries. Forbidden
    # patterns are still matched FIRST, so "what happened overnight then buy
    # NQ" or "executive summary then run the script" stay refused.
    r"\bovernight\b",
    r"\bexecutive\s+summary\b",
    r"\bsummar(?:ize|ise)\s+the\s+system\b",
    r"\bsummar(?:ize|ise)\b.*\bsystem\b",
    r"\btell\s+me\s+more\b",
    r"\bnext\s+step\b",
    r"\bwhat\s+should\s+we\s+focus\b",
    r"\bwhat\s+to\s+focus\b",
    r"\bfocus\s+on\s+(?:today|now|next)\b",
    # JARVIS Executive Translation Mode v1 — operator-mode triggers that switch
    # a briefing/status answer from the customer-friendly executive default into
    # full technical detail (exact counts, report names, raw warnings, posture
    # flags). All read-only; forbidden patterns are still matched FIRST, so
    # "operator mode then buy NQ" / "show technical details and commit" refuse.
    r"\boperator\s+mode\b",
    r"\bshow\s+(?:me\s+)?(?:the\s+)?(?:technical\s+)?details?\b",
    r"\btechnical\s+details?\b",
    r"\bdiagnostics?\b",
    r"\bexact\s+counts?\b",
    # JARVIS Chief of Staff Mode v1 — read-only strategic + product-demo
    # intents, answered as advice only from the existing status aggregate.
    # Forbidden patterns are still matched FIRST. Note: "sell" stays a forbidden
    # trading token, so "are we ready to sell" deliberately refuses — use
    # "ready to demo / ship / launch" for product-readiness questions.
    r"\bwork\s+on\s+(?:today|next|now)\b",
    r"\bwhat\s+should\s+we\s+work\b",
    r"\bwhat\s+to\s+work\s+on\b",
    r"\bsmartest\b",
    r"\bnext\s+move\b",
    r"\bbest\s+(?:next\s+)?move\b",
    r"\bpriorit(?:y|ies)\b",
    r"\bmost\s+important\b",
    r"\bbig\s+picture\b",
    r"\bwhere\s+(?:we\s+are|are\s+we|do\s+we\s+stand)\b",
    r"\bwhy\b.*\bmatters?\b",
    r"\bwhat\s+should\s+i\s+tell\b",
    r"\bready\s+to\s+(?:demo|ship|launch|pitch)\b",
    r"\bready\s+for\s+a\s+demo\b",
    r"\bdemo\b",
    r"\bpitch\b",
    r"\bdescribe\b",
    r"\bwhat\s+(?:is|are)\s+jarvis\b",
    r"\bwho\s+is\s+jarvis\b",
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
