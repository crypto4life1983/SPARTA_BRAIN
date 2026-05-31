"""SPARTA Brain Knowledge Map v1 — READ-ONLY module map for JARVIS.

This is a *pure data + rendering* module. It carries no side effects: it runs
no command, opens no broker/paper/live path, uploads nothing, generates no
content, writes no file, and reads no live state. It exists so JARVIS can answer
"what does SPARTA Brain do / explain all modules / what is the YouTube builder /
what is Hydra / what is the affiliate system / what automation do we have / what
is the moving company workflow / what is brain memory / what dashboards exist /
what is the roadmap" from a single committed inventory.

Every answer is descriptive only and ends by stating it authorizes no action.
Status values are honest: ``shipped`` / ``shipped (partial)`` / ``planned``.
When a module's status is not known it is reported as ``unknown`` — never
invented. Capabilities that do not exist (live trading, order placement, real
uploads, content-generation jobs) are listed under ``cannot`` so JARVIS never
implies a capability it does not have.

Wording deliberately avoids fabricated-performance tokens (no profit / pnl /
win rate / return / "ready to trade" / "validated" / "approved" / "earned"),
so knowledge-map answers satisfy the JARVIS no-fake-performance contract.
"""
from __future__ import annotations

from typing import Optional, Tuple, List, Dict


# --- the inventory --------------------------------------------------------
# Each module: key, name, keywords (lowercase substrings matched in the
# question), purpose, status, can (what JARVIS can describe), cannot (hard
# limits), safety (read-only note), demo (plain-language one-liner), location
# (committed evidence, shown only in operator detail).

MODULES: List[Dict] = [
    {
        "key": "jarvis",
        "name": "JARVIS",
        "keywords": ["jarvis"],
        "purpose": ("the read-only voice and chief-of-staff interface — you ask "
                    "in plain language and it answers from aggregated system "
                    "state."),
        "status": "shipped",
        "can": ("explain the system, summarise read-only status, and give "
                "advice-only chief-of-staff guidance"),
        "cannot": ("place trades, run jobs, refresh, commit, upload, generate "
                   "content, or write any file"),
        "safety": "Observe-only; every answer authorizes no action.",
        "demo": ("Think Iron Man's JARVIS, but strictly read-only: it reports "
                 "and advises, it never acts."),
        "location": "app.py /api/jarvis/ask + /api/jarvis/status, templates/jarvis.html",
    },
    {
        "key": "strategy_factory",
        "name": "Strategy Factory",
        "keywords": ["strategy factory", "factory"],
        "purpose": ("the research engine that produces and reviews trading "
                    "strategy candidates as dry-run research only."),
        "status": "shipped",
        "can": ("describe committed research reports and the latest read-only "
                "research decisions"),
        "cannot": ("run a Factory job, place trades, or move a candidate toward "
                   "paper or live trading"),
        "safety": ("Research/candidate only — nothing here trades; JARVIS runs "
                   "no Factory job."),
        "demo": ("A lab that drafts and reviews strategy ideas on paper, so "
                 "only researched candidates are ever discussed."),
        "location": "tools/strategy_factory_routines.py",
    },
    {
        "key": "trading_research",
        "name": "Trading Research",
        "keywords": ["trading research", "research os", "agentic factory",
                     "research engine"],
        "purpose": ("the advisory research layer that studies markets and tracks "
                    "research candidates — observation-only, never an order path."),
        "status": "shipped (partial)",
        "can": ("describe how many research candidates are tracked and the "
                "read-only trading posture"),
        "cannot": ("enable paper or live trading, connect a broker, or place an "
                   "order"),
        "safety": ("Trading is locked to observation-only "
                   "(read_only=true, paper_ready=false, live_ready=false, "
                   "broker_control=false)."),
        "demo": ("A market-study desk: it researches and watches, it does not "
                 "buy or sell anything."),
        "location": "trading_research/, agentic_factory/",
    },
    {
        "key": "youtube_builder",
        "name": "YouTube Builder",
        "keywords": ["youtube"],
        "purpose": ("the YouTube publishing pipeline (client, uploader, and "
                    "autopilot wiring) for the channel."),
        "status": "shipped",
        "can": ("describe what the builder is for and that a safety gate guards "
                "publishing"),
        "cannot": ("upload, publish, or schedule any video from JARVIS — JARVIS "
                   "triggers no upload"),
        "safety": ("Publishing is gated by a compliance safety check; JARVIS is "
                   "description-only and starts no upload."),
        "demo": ("The tool that prepares and (elsewhere, gated) publishes "
                 "channel videos — JARVIS only talks about it."),
        "location": "youtube_uploader.py, youtube_client.py, hydra/youtube_autopilot.py",
    },
    {
        "key": "hydra",
        "name": "Hydra / Video Engine",
        "keywords": ["hydra", "video engine", "animation engine", "video"],
        "purpose": ("the 2D animated-video engine that turns scripts into "
                    "Spartan Wallet story renders with director-mode QA."),
        "status": "shipped",
        "can": ("describe the engine, the Spartan Wallet story rules, and the "
                "Kaizen QA checks"),
        "cannot": ("render, produce, or publish a video from JARVIS — JARVIS "
                   "runs no render job"),
        "safety": "Description-only here; JARVIS starts no render and writes nothing.",
        "demo": ("An animation studio for short money-discipline stories — "
                 "JARVIS describes it but does not run it."),
        "location": "hydra/, hydra_video/, director_mode.py, animation_engine.py",
    },
    {
        "key": "affiliate",
        "name": "Affiliate System",
        "keywords": ["affiliate"],
        "purpose": ("the affiliate-tracking layer that organises offers and "
                    "links in the dashboard."),
        "status": "shipped",
        "can": "describe what the affiliate layer is for at a high level",
        "cannot": ("post, publish, send, or run any affiliate campaign from "
                   "JARVIS; it claims no income figures"),
        "safety": ("Read-only description; JARVIS quotes no income and runs no "
                   "campaign."),
        "demo": ("A place to organise affiliate offers and links — JARVIS only "
                 "describes it, with no income claims."),
        "location": "app.py (affiliate dashboard routes)",
    },
    {
        "key": "automation",
        "name": "Automation Workflows",
        "keywords": ["automation", "auto brain", "scheduler", "auto cycle"],
        "purpose": ("the batch/scheduler scripts that run brain cycles and "
                    "startup tasks on the machine."),
        "status": "shipped",
        "can": ("describe which automation scripts exist and what they are "
                "intended to do"),
        "cannot": ("start, stop, trigger, or schedule any automation from "
                   "JARVIS — JARVIS executes nothing"),
        "safety": "Description-only; JARVIS triggers no script and changes no schedule.",
        "demo": ("The background routines that keep the brain ticking — JARVIS "
                 "talks about them but never launches them."),
        "location": "auto_brain_cycle.bat, auto_start.bat, tools/brain_*",
    },
    {
        "key": "moving_company",
        "name": "Moving Company Workflow",
        "keywords": ["moving company", "moving", "removals"],
        "purpose": ("a business-workflow idea for the moving company, currently "
                    "only a brain-memory project folder and a placeholder."),
        "status": "planned",
        "can": ("confirm it is planned and point to the brain-memory project "
                "notes"),
        "cannot": ("operate, quote, schedule, or run any moving-company workflow "
                   "— none is built yet"),
        "safety": "Planned only — no working workflow exists; JARVIS invents none.",
        "demo": ("An idea on the roadmap, not a working tool yet — JARVIS is "
                 "honest that it is not built."),
        "location": "brain_memory/projects/moving_company/ (notes + placeholder)",
    },
    {
        "key": "brain_memory",
        "name": "Brain Memory",
        "keywords": ["brain memory", "memory system", "brain index"],
        "purpose": ("the file-based memory store of identity, operating rules, "
                    "and per-project notes the brain reads before working."),
        "status": "shipped",
        "can": ("describe the memory layout and which project notes exist"),
        "cannot": "rewrite credentials, trading logic, or production flows",
        "safety": "Read-only here; JARVIS reads memory but writes none from this surface.",
        "demo": ("The brain's long-term notebook — who it is, its rules, and "
                 "each project's context."),
        "location": "brain_memory/ (identity.md, operating_rules.md, projects/)",
    },
    {
        "key": "dashboards",
        "name": "Dashboards",
        "keywords": ["dashboard", "dashboards", "guide page", "clone page"],
        "purpose": ("the local web surfaces: /guide (module map), /clone (style "
                    "clone), and /jarvis (the assistant)."),
        "status": "shipped",
        "can": "list which dashboards exist and what each is for",
        "cannot": "execute actions; the dashboards JARVIS exposes are read-only",
        "safety": "Read-only views; the JARVIS surface adds no execution control.",
        "demo": ("The screens you actually open: a system guide, a style clone, "
                 "and the JARVIS assistant."),
        "location": "app.py routes /guide, /clone, /jarvis",
    },
    {
        "key": "safety",
        "name": "Safety & Governance",
        "keywords": ["safety", "governance", "compliance", "guardrail",
                     "classifier", "knowledge map"],
        "purpose": ("the guardrails: the JARVIS question classifier, the YouTube "
                    "compliance gate, and the operating rules."),
        "status": "shipped",
        "can": ("explain how forbidden commands are refused and how read-only "
                "defaults are enforced"),
        "cannot": "be bypassed to grant trading, execution, upload, or write access",
        "safety": ("This is the layer that keeps everything read-only and "
                   "refuses action requests."),
        "demo": ("The seatbelts: a classifier that refuses risky asks and rules "
                 "that keep the system observe-only."),
        "location": ("jarvis_conversation_safety.py, compliance/youtube_safety_gate.py, "
                     "brain_memory/operating_rules.md"),
    },
]

_MODULE_BY_KEY = {m["key"]: m for m in MODULES}

# Roadmap = planned, not-built items drawn from committed notes (CLAUDE.md
# clone-engine "future extensions" + the moving-company placeholder).
ROADMAP: List[Dict] = [
    {"name": "Clone Engine importers (Gmail / WhatsApp / Instagram)",
     "status": "planned", "note": "auto-populate the training inbox; not built."},
    {"name": "ElevenLabs voice clone", "status": "planned",
     "note": "matching audio output; not built."},
    {"name": "HeyGen video avatar", "status": "planned",
     "note": "video replies; not built."},
    {"name": "Daily auto-training scheduler", "status": "planned",
     "note": "scheduled Clone Engine training; not built."},
    {"name": "Moving Company workflow", "status": "planned",
     "note": "business workflow; only a brain-memory placeholder exists."},
]


# --- detection helpers ----------------------------------------------------

_DEFINITIONAL = (
    "what is", "what's", "whats", "what are", "what're",
    "explain", "describe", "tell me about", "tell me what",
    "overview of", "what does", "how does", "who is", "what can",
    "give me a rundown", "walk me through",
)

_STATUS_WORDS = ("status", "progress", "how is", "how's", "hows", "how are",
                 "update on", "state of")

# Non-definitional inquiry phrasings ("what automation do we have", "what
# dashboards exist", "tell me about the affiliate system") that still ask
# *about* a module rather than its live status.
_INQUIRY = ("do we have", "do you have", "have we", "we have", "exist",
            "is there", "are there", "what about", "tell me", "got any",
            "list", "show me", "which", "what features")

_DEMO_FRAMES = (
    "to a customer", "to a client", "to a friend", "to an investor",
    "to a buyer", "for a customer", "for an investor", "for a demo",
    "like i'm 5", "like im 5", "in simple terms", "in plain english",
    "explain it to", "pitch", "sell it to", "for a friend",
)

_OPERATOR_FRAMES = (
    "operator mode", "operator detail", "technical detail", "show technical",
    "diagnostic", "exact", "under the hood",
)

_ALL_MODULES = (
    "all modules", "all the modules", "every module", "all features",
    "all the features", "list modules", "list the modules", "list features",
    "what modules", "which modules", "all parts", "everything sparta",
    "what does sparta brain do", "what does sparta do",
    "what can sparta brain do", "what can sparta do", "what can you do",
    "what do you do", "all of sparta", "the whole system", "all components",
    "full map", "knowledge map", "rundown of sparta", "all your modules",
)

_ROADMAP = ("roadmap", "what's planned", "whats planned", "what is planned",
            "future plans", "what's next on the roadmap", "what's coming",
            "whats coming", "planned features", "not built yet", "future extensions")


def _has(q: str, needles) -> bool:
    return any(n in q for n in needles)


def is_definitional(q: str) -> bool:
    """A 'what is / explain / describe' style question without a status frame."""
    return _has(q, _DEFINITIONAL) and not _has(q, _STATUS_WORDS)


def asks_about_module(q: str) -> bool:
    """A definitional OR inquiry question about a module, but never a live-status
    frame (those route to the dedicated status branches)."""
    if _has(q, _STATUS_WORDS):
        return False
    return _has(q, _DEFINITIONAL) or _has(q, _INQUIRY)


def is_all_modules_query(q: str) -> bool:
    return _has(q, _ALL_MODULES)


def is_roadmap_query(q: str) -> bool:
    return _has(q, _ROADMAP) and "knowledge map" not in q


def wants_operator(q: str) -> bool:
    return _has(q, _OPERATOR_FRAMES)


def wants_demo(q: str) -> bool:
    return _has(q, _DEMO_FRAMES)


def find_module(q: str) -> Optional[Dict]:
    """Return the single best-matching module for a definitional question, or
    None. Longer keyword matches win (so 'strategy factory' beats 'factory').
    Modules already owned by dedicated status branches (jarvis, strategy
    factory, trading, sparta brain) are intentionally NOT matched here unless
    the question is clearly a per-module definition handled upstream — callers
    gate on is_definitional()."""
    best = None
    best_len = 0
    for m in MODULES:
        for kw in m["keywords"]:
            if kw in q and len(kw) > best_len:
                best = m
                best_len = len(kw)
    return best


# --- rendering ------------------------------------------------------------

_NO_ACTION = "This is a read-only description and authorizes no action."


def _module_executive(m: Dict) -> str:
    return (f"{m['name']} (read-only overview). {m['purpose'].capitalize()} "
            f"Current status: {m['status']}. It can {m['can']}. It cannot "
            f"{m['cannot']}. {m['safety']} {_NO_ACTION}")


def _module_operator(m: Dict) -> str:
    return (f"{m['name']} (read-only, operator detail). Module key: {m['key']}; "
            f"status: {m['status']}; known location: {m['location']}. "
            f"Purpose: {m['purpose']} It can {m['can']}. It cannot {m['cannot']}. "
            f"{m['safety']} {_NO_ACTION}")


def _module_demo(m: Dict) -> str:
    return (f"{m['name']} — {m['demo']} (Status: {m['status']}.) "
            f"Read-only: SPARTA Brain describes it and runs nothing here.")


def _render_module(m: Dict, operator: bool, demo: bool) -> str:
    if demo:
        return _module_demo(m)
    if operator:
        return _module_operator(m)
    return _module_executive(m)


def _all_modules_executive() -> str:
    lines = "; ".join(f"{m['name']} ({m['status']})" for m in MODULES)
    return ("SPARTA Brain is a local, read-only AI command center. Its main "
            f"modules are: {lines}. JARVIS is the assistant you are talking to; "
            "trading stays observation-only and nothing here executes, uploads, "
            "or trades. Ask 'what is the <module>' for detail, or add 'operator "
            f"mode' for technical detail. {_NO_ACTION}")


def _all_modules_operator() -> str:
    lines = " | ".join(f"{m['key']}: {m['name']} [{m['status']}] @ {m['location']}"
                       for m in MODULES)
    return ("SPARTA Brain module map (read-only, operator detail). " + lines +
            f". All surfaces are observe-only; JARVIS executes, uploads, and "
            f"trades nothing. {_NO_ACTION}")


def _all_modules_demo() -> str:
    bits = " ".join(f"{m['name']}: {m['demo']}" for m in MODULES)
    return ("Here's SPARTA Brain in plain language — one local AI command center "
            "made of a few parts. " + bits + " Everything JARVIS shows is "
            "read-only: it describes and advises, it never acts.")


def _roadmap_answer(operator: bool, demo: bool) -> Tuple[str, List[str]]:
    items = "; ".join(f"{r['name']} ({r['status']}{' — ' + r['note'] if operator else ''})"
                      for r in ROADMAP)
    if demo:
        body = ("On the roadmap (planned, not built yet): " +
                "; ".join(r["name"] for r in ROADMAP) + ". "
                "These are ideas we have not shipped, and JARVIS is honest that "
                "they do not work yet.")
    else:
        body = ("SPARTA Brain roadmap — planned items that are NOT built yet: " +
                items + ". JARVIS invents no capability for these; they are "
                f"planned only. {_NO_ACTION}")
    return (body, ["knowledge_map"])


def build_knowledge_map_answer(q: str, operator: bool = False,
                               demo: bool = False) -> Optional[Tuple[str, List[str]]]:
    """Return (answer, sources) for a knowledge-map intent, or None to fall
    through to the existing answer branches.

    Engages ONLY for: all-modules questions, the roadmap, or a definitional
    per-module question. It deliberately does NOT engage on status frames
    ('factory status', 'trading status', 'sparta brain status'), so the existing
    status branches keep their behavior. Read-only; reads no live state.
    """
    q = (q or "").lower()
    operator = operator or wants_operator(q)
    demo = demo or wants_demo(q)

    if is_roadmap_query(q):
        return _roadmap_answer(operator, demo)

    if is_all_modules_query(q):
        if demo:
            return (_all_modules_demo(), ["knowledge_map"])
        if operator:
            return (_all_modules_operator(), ["knowledge_map"])
        return (_all_modules_executive(), ["knowledge_map"])

    if asks_about_module(q):
        m = find_module(q)
        if m is not None:
            return (_render_module(m, operator, demo), ["knowledge_map"])

    return None
