"""2D Animation Engine — script → animated MP4.

Pipeline:
  1. Split script into lines (one scene per line)
  2. Detect emotion + visual prop per line (keyword matching)
  3. Generate TTS audio per scene via edge-tts
  4. Build Remotion FunnyFinance2D props JSON
  5. Shell out to Remotion render
  6. Return final MP4 path + metadata

HYDRA RULE (permanent standard):
  Every generated video must be treated like a 2D animated show, not static
  illustrated slides. Every scene requires character motion, background motion,
  camera motion, and at least one animated visual event when possible.
  — Narrator scenes: enforced via RuntimeError if visualEvent/bg/action missing.
  — Civilian/wallet scenes: fallback visual event assigned when no keyword matches.
  — Spartan scenes: always dark_void + freeze_moment or money_drain + step_forward.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import time
import math
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from subtitle_sanitizer import (
    assert_english_subtitle_text,
    clean_subtitle_text,
    qa_clean_subtitle_payload,
)
from director_mode import (
    repair_script_for_director_mode,
    repair_scene_life,
    scene_life_issues,
    spartan_wallet_kaizen_report,
)
from spartacus.audio_timeline import validate_voice_master_timeline

try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except Exception:
    pass

SPARTA_ROOT   = Path(r"C:\SPARTA_BRAIN")
REMOTION_DIR  = SPARTA_ROOT / "remotion"
REMOTION_SRC  = REMOTION_DIR / "src" / "index.ts"
REMOTION_PUB  = REMOTION_DIR / "public"
STORAGE_DIR   = SPARTA_ROOT / "storage" / "animation"

# ─── Project mode ─────────────────────────────────────────────────────────────
# ENTERTAINMENT — story-driven animated show; all commerce logic disabled
# AFFILIATE     — monetised product content; Amazon + affiliate engine active
PROJECT_MODE: str = os.getenv("PROJECT_MODE", "ENTERTAINMENT").upper()

_ENTERTAINMENT_BLOCKED_EVENTS: frozenset[str] = frozenset({
    "cart_add", "checkout", "order", "product_display",
})

FPS           = 30
SCENE_GAP_F   = 0      # voice-master timeline: no implicit gaps or overlaps
SCENE_VOICE_BUFFER_SEC = 0.40
AUDIO_TAIL    = SCENE_VOICE_BUFFER_SEC
# Per-transition-type crossfade overlap (frames at 30 fps)
_CROSS_FADE = {"continuation": 0, "cause_effect": 0, "break": 0}
PAUSE_DUR          = 0.05   # max intentional pre-audio silence
CLEAN_ENTRY_DELAY  = 0.05   # clean entry without audible dead air
WALLET_ENTRY_DELAY = 0.04   # Wallet interruption: quick overlap/resistance beat
IMPACT_MIN         = 2.00   # minimum scene duration for impact cards (seconds)
ENDING_HOLD_F      = round((0.50 - SCENE_VOICE_BUFFER_SEC) * FPS)
CAPTION_MIN_SEC    = 1.20   # readable subtitle chunk minimum
CAPTION_MAX_WORDS  = 6      # short chunks, max two visual lines
CAPTION_MAX_WPM    = 220    # leave margin below audit threshold

DEFAULT_VOICE   = "en-US-AndrewMultilingualNeural"
SPARTAN_VOICE   = "en-US-GuyNeural"
CIVILIAN_VOICE  = "en-US-AndrewMultilingualNeural"
NARRATOR_VOICE  = "en-US-ChristopherNeural"   # deep, calm, cinematic
WALLET_VOICE    = "en-US-AriaNeural"

ELEVENLABS_FIXED_VOICES = {
    "civilian": "P2VjEv8OzkIbLWt2GcTI",       # casual tone, en-US script only
    "wallet":   "P2VjEv8OzkIbLWt2GcTI",       # expressive settings + speed
    "spartan":  "XGE25spxRHxRRxwvrdCl",       # final line uses narrator voice for consistent clarity
    "narrator": "XGE25spxRHxRRxwvrdCl",       # calm male
}

# ─── Emotion detection ────────────────────────────────────────────────────────
_EMOTION_MAP: list[tuple[str, list[str]]] = [
    ("shocked",  ["cost you", "never told", "no one told", "never knew",
                  "actually", "000", "ruined", "destroyed", "just cost",
                  "that's right", "percent", "rate:", "interest rate",
                  "he earned zero", "she earned zero", "earned zero",
                  "that difference", "different number", "never happened",
                  "the other is still", "has $", "that is how ignorance",
                  "nobody told", "nobody told him", "nobody told her"]),
    ("sad",      ["broke", "debt", "poor", "losing", "wasted", "bad news",
                  "never taught", "ruins your", "ruining", "costing you",
                  "could not afford", "he did not know", "she did not know",
                  "forgot about it", "still working", "zero",
                  "not because", "he had never", "she had never"]),
    ("happy",    ["invest", "grow", "rich", "follow", "learn", "worth it",
                  "earned", "gains", "freedom", "retired", "retired early",
                  "has $681", "check the", "link is in", "in the description"]),
    ("thinking", ["a man in", "a woman in", "a 2", "two cowork",
                  "both 23", "both earning", "in january", "in 2025",
                  "total spent", "ten years", "same day", "same car",
                  "same income", "sits at", "opens his", "opens her",
                  "a kitchen table", "a car dealership"]),
]

def _detect_emotion(line: str) -> str:
    low = line.lower()
    for emotion, keywords in _EMOTION_MAP:
        if any(kw in low for kw in keywords):
            return emotion
    return "neutral"

# ─── Prop detection ───────────────────────────────────────────────────────────
_PROP_MAP: list[tuple[str, list[str]]] = [
    ("coffee",   ["coffee", "latte", "morning", "cup", "café", "espresso"]),
    ("house",    ["house", "home", "property", "mortgage", "rent"]),
    ("chart_up", ["invest", "return", "grow", "compound", "interest",
                  "gains", "profit", "market"]),
    ("coin",     ["money", "dollar", "$", "saving", "cash", "bank",
                  "income", "salary", "earn", "pay"]),
]

def _detect_prop(line: str) -> str:
    low = line.lower()
    for prop, keywords in _PROP_MAP:
        if any(kw in low for kw in keywords):
            return prop
    return "none"

# ─── Scene type detection ─────────────────────────────────────────────────────
_SCENE_MAP: list[tuple[str, list[str]]] = [
    ("dealership", ["car dealership", "car lot", "showroom", "dealer", "buying a car",
                    "car payment", "financed", "vehicle", "drove off", "test drive",
                    "new car", "used car", "auto loan", "automobile"]),
    ("office",     ["office", "coworker", "cubicle", "at work", "their desk",
                    "his desk", "her desk", "9 to 5", "both 23", "same income",
                    "both earning", "workday", "colleague", "cowork"]),
    ("street",     ["street", "city", "downtown", "sidewalk", "commute",
                    "the streets", "city block", "traffic light"]),
    ("home",       ["kitchen", "living room", "bedroom", "couch", "at home",
                    "kitchen table", "their apartment", "his apartment", "her apartment",
                    "their home", "his home", "her home", "mortgage", "rent"]),
    ("phone",      ["phone", "scroll", "screen", "browser", "digital", "click"]),
    ("coffee",     ["coffee", "latte", "morning cup", "café", "espresso",
                    "barista", "starbucks", "coffee shop", "daily coffee"]),
    ("bank",       ["bank", "atm", "savings account", "checking account",
                    "interest rate", "bank account", "apr", "loan rate"]),
]

def _detect_scene_type(line: str) -> str:
    low = line.lower()
    for scene_type, keywords in _SCENE_MAP:
        if any(kw in low for kw in keywords):
            return scene_type
    return "default"

# ─── Duo / stat helpers ───────────────────────────────────────────────────────
_DUO_KEYWORDS = [
    "two cowork", "both 23", "both earning", "same car", "same income",
    "same day", "person a", "person b", "one invested", "one saved",
    "the other is", "the other had", "the other still", "his twin",
    "a man and a woman", "side by side",
]

def _has_duo(line: str) -> bool:
    low = line.lower()
    return any(kw in low for kw in _DUO_KEYWORDS)

def _has_stat(line: str) -> bool:
    """True if line contains a prominent number, dollar amount, or percentage."""
    return bool(re.search(r'\$[\d,]+k?|\d+(?:\.\d+)?\s*%|\d{4,}', line, re.I))

# ─── Director Mode ────────────────────────────────────────────────────────────
_CAMERA_CYCLE = [
    "zoom_in",    # push forward
    "pan_left",   # lateral slide
    "slow_push",  # subtle creep
    "pan_right",  # slide back
    "zoom_out",   # pull back
    "shake",      # punctuation beat
    "zoom_in",    # push again
    "slow_push",  # hold tension
]

# Visual events for character scenes — ordered by priority (first match wins)
_VISUAL_EVENTS: list[tuple[str, list[str]]] = [
    # Spartan authority / freeze — highest priority
    ("freeze_moment", ["impressive", "you lose control", "lose control",
                       "you don't lose", "control your money"]),
    # Salary alarm (wallet finale)
    ("salary_alert",  ["not again"]),
    # Wallet collision burst — wallet_hit before salary_pop so "we just got paid" → hit not pop
    ("wallet_hit",    ["we just got paid", "no. we just", "no. we"]),
    # Salary celebration
    ("salary_pop",    ["salary received", "got paid", "payday", "paycheck",
                       "just received", "deposit hit"]),
    # Phone offer popup — impulse buy moment
    ("offer_flash",   ["one thing", "maybe one", "maybe this", "one more thing",
                       "just one", "okay maybe", "percent off", "fifty percent", "one purchase"]),
    # Phone screen glow — phone still in hand, scrolling
    ("phone_glow",    ["small", "it's small", "relax", "fine", "just this",
                       "it's fine", "just a"]),
    # Boxes piling up — chaos escalation
    ("boxes_spawn",   ["you said that", "you say that", "last time", "again and", "this always",
                       "boxes stack", "stack over", "cart became", "cart becomes",
                       "cart is growing", "monster"]),
    # Money drain — value leaving
    ("money_drain",   ["wasted", "spent it all", "removed it", "and removed",
                       "income and", "you lose", "drain", "rent disappear",
                       "drain my account"]),
]

# Visual events triggered by narrator text — ordered by priority (first match wins)
_NARRATOR_VISUAL_MAP: list[tuple[str, list[str]]] = [
    # Freeze — Spartan dimension
    ("freeze_moment", ["impressive", "lose control", "you lose", "frozen",
                       "time stops", "nothing moves"]),
    # Salary celebration
    ("salary_pop",    ["earned", "salary", "paycheck", "got paid", "just got paid",
                       "income", "deposited", "payday", "thousand a month",
                       "every month", "paid today", "receives", "watch this",
                       "he just got paid"]),
    # Full-screen salary alarm
    ("salary_alert",  ["not again", "every time", "always happens", "still happening",
                       "every month again"]),
    # Offer popup — phone temptation moment
    ("offer_flash",   ["a bad one", "bad one", "bad decision", "a bad",
                       "one thing", "temptation", "phone offer",
                       "it appears", "appears", "limited offer", "notification"]),
    # Boxes chaos
    ("boxes_spawn",   ["where it goes wrong", "goes wrong", "went wrong",
                       "chaos starts", "boxes", "piling up", "cart became",
                       "cart becomes", "cart monster", "monster"]),
    # Money drain — value leaving, general "going wrong"
    ("money_drain",   ["spent", "spending", "wasted", "bought", "vanished",
                       "disappeared", "gone", "empty", "nothing left",
                       "wrong", "bad", "mistake", "habit", "where it goes",
                       "decision", "danger", "losing", "lost",
                       "problem", "struggle", "chaos", "out of control",
                       "this is where", "but then", "went wrong",
                       "broke", "zero", "removed"]),
]

# Camera style per narrator visual event — overrides slow_push default
_NARRATOR_CAM_FOR_EVENT: dict[str, str] = {
    "salary_pop":   "zoom_in",    # excitement — push into action
    "money_drain":  "shake",      # chaos + tension
    "wallet_hit":   "shake",
    "salary_alert": "zoom_in",    # alarm urgency
    "offer_flash":  "zoom_in",    # push into phone screen
    "boxes_spawn":  "zoom_out",   # pull back to reveal chaos
    "freeze_moment":"slow_push",  # Spartan entrance — controlled
}

# Background overrides driven by narrator content
_NARRATOR_BG_MAP: list[tuple[str, list[str]]] = [
    ("salary",  ["salary", "paycheck", "got paid", "earned", "payday",
                 "income", "just got paid", "thousand", "deposit"]),
    ("bank",    ["bank", "savings", "account", "balance", "transfer", "zero"]),
    ("office",  ["office", "work", "job", "desk", "coworker", "company",
                 "boss", "promotion"]),
    ("street",  ["street", "city", "outside", "walking", "driving", "commute",
                 "store", "mall", "shopping"]),
    ("home",    ["home", "apartment", "kitchen", "couch", "bedroom", "living",
                 "bad", "wrong", "habit", "decision", "mistake", "control",
                 "where it", "this is where", "here it"]),
]

# Scene type rotation pool (no dealership — not relevant to this project)
_SCENE_TYPE_POOL = ["home", "office", "street", "bank", "coffee", "salary", "default"]


def _director(
    idx:       int,
    role:      str | None,
    text:      str,
    scene_type: str,
    has_pause: bool,
    is_impact: bool,
    prev_role: str | None,
) -> dict:
    """Return director annotations for one scene."""
    text_low = text.lower()
    is_caps  = text == text.upper() and len(text.strip()) > 4

    # ── Visual event — one clear 2D cause/effect beat per scene.
    # Shared trait from top animation channels: action must trigger a
    # visible reaction, not just sit under narration.
    vis: str | None = None
    if not is_impact:
        event_map = _NARRATOR_VISUAL_MAP if role == "narrator" else _VISUAL_EVENTS
        for event, keywords in event_map:
            if PROJECT_MODE == "ENTERTAINMENT" and event in _ENTERTAINMENT_BLOCKED_EVENTS:
                continue
            if any(kw in text_low for kw in keywords):
                vis = event
                break
        # Narrator MUST have a visual event — fallback = money_drain (ominous default)
        if role == "narrator" and vis is None:
            vis = "money_drain"

        # Civilian/wallet: fallback ensures every scene has at least one visual event (Hydra Rule)
        if role in ("civilian", "wallet") and vis is None and not is_impact:
            if any(kw in text_low for kw in ["tap", "phone", "screen", "scroll"]):
                vis = "phone_glow"
            elif any(kw in text_low for kw in ["box", "order", "buy", "bought", "cart", "monster"]):
                vis = "boxes_spawn"
            elif any(kw in text_low for kw in ["wait", "stop", "freeze", "spartan"]):
                vis = "freeze_moment"
            else:
                vis = "salary_pop" if any(kw in text_low for kw in [
                "saving", "saved", "save ", "budget", "invest",
            ]) else "money_drain"

    # ── Camera
    if is_impact:
        cam = "zoom_in"
    elif role == "narrator":
        # Camera follows the visual event for full impact
        cam = _NARRATOR_CAM_FOR_EVENT.get(vis or "", "slow_push")
    elif role == "spartan":
        # Spartan freeze entrance = zoom_in; authority speech = slow_push
        cam = "zoom_in" if vis == "freeze_moment" else "slow_push"
    elif role == "wallet" and (is_caps or "not again" in text_low):
        cam = "shake"
    elif role == "wallet":
        # Second beat of a split line ("We just got paid!") gets authority zoom
        cam = "zoom_in" if any(kw in text_low for kw in [
            "we just got paid", "we earned", "discipline", "control", "this is ours"
        ]) else "shake"
    else:
        cam = _CAMERA_CYCLE[idx % len(_CAMERA_CYCLE)]

    # ── Civilian action
    civ = "idle"
    if role == "narrator" and not is_impact:
        # Narrator scenes: civilian ALWAYS performs an active action — never idle
        if vis == "salary_pop":
            civ = "react"           # civilian reacts to salary notification
        elif vis == "offer_flash":
            civ = "pick_up_phone"   # civilian finger moving toward phone
        elif vis in ("boxes_spawn", "money_drain"):
            civ = "pick_up_phone"   # buying things on phone = chaos
        elif vis == "freeze_moment":
            civ = "react"           # civilian reacts to Spartan appearance
        elif any(kw in text_low for kw in ["spent", "spending", "bought", "phone",
                                            "scroll", "shopping", "app"]):
            civ = "pick_up_phone"
        elif any(kw in text_low for kw in ["salary", "paycheck", "earned",
                                            "got paid", "income", "just got paid"]):
            civ = "react"
        else:
            civ = "walk_in"         # default: always enter, never be static
    elif role == "wallet" and not is_impact:
        civ = "react"   # civilian listens while wallet speaks in duo
    elif role in ("civilian", None) and not is_impact:
        if scene_type == "phone" or "phone" in text_low or "tap" in text_low or "scroll" in text_low:
            civ = "pick_up_phone"
            _buy_kws = ["buying", "i'm buying", "buy it", "i'll buy"]
            if vis in ("offer_flash", "phone_glow") and any(kw in text_low for kw in _buy_kws):
                vis = "boxes_spawn"   # actual purchase moment → cascade
        elif prev_role not in ("civilian",):
            civ = "walk_in"
        elif vis == "salary_pop":
            civ = "react"
        elif prev_role in ("wallet", "spartan"):
            civ = "react"

    # ── Spartan action
    spt = "step_forward" if (role == "spartan" and has_pause) else "hold"

    # ── Background override
    bg_override: str | None = None
    if role == "narrator":
        # Event-driven bg (semantic: where does THIS event happen?)
        _EVENT_BG: dict[str, str] = {
            "salary_pop":   "salary",
            "salary_alert": "home",
            "offer_flash":  "phone",    # phone UI — the temptation screen
            "boxes_spawn":  "home",     # room chaos
            "money_drain":  "home",     # chaos at home
            "wallet_hit":   "home",
            "freeze_moment":"dark_void",
        }
        if vis and vis in _EVENT_BG:
            bg_override = _EVENT_BG[vis]
        else:
            # Keyword-driven bg fallback
            for bg_type, keywords in _NARRATOR_BG_MAP:
                if any(kw in text_low for kw in keywords):
                    bg_override = bg_type
                    break
        # Narrator MUST have a bg — fallback = pool rotation
        if bg_override is None:
            bg_override = _SCENE_TYPE_POOL[idx % len(_SCENE_TYPE_POOL)]
    elif role == "spartan":
        bg_override = "dark_void"   # Spartan always occupies the authority dimension
    elif role == "wallet":
        bg_override = "home"        # Wallet always argues from the home dimension
    elif vis == "salary_pop":
        bg_override = "salary"

    return {
        "cameraAction":   cam,
        "visualEvent":    vis,
        "civilianAction": civ,
        "spartanAction":  spt,
        "bgOverride":     bg_override,
    }


# ─── Role tag parser ──────────────────────────────────────────────────────────
_SUBTITLE_REPLACEMENTS: list[tuple[str, str]] = [
    ("…", "..."),   # … HORIZONTAL ELLIPSIS
    ("—", " - "),   # — EM DASH
    ("–", " - "),   # – EN DASH
    ("‘", "'"),     # ' LEFT SINGLE QUOTATION MARK
    ("’", "'"),     # ' RIGHT SINGLE QUOTATION MARK
    ("“", '"'),     # " LEFT DOUBLE QUOTATION MARK
    ("”", '"'),     # " RIGHT DOUBLE QUOTATION MARK
    (" ", " "),     # NON-BREAKING SPACE
    ("•", "-"),     # • BULLET
    ("‒", "-"),     # FIGURE DASH
    ("«", '"'),     # « LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    ("»", '"'),     # » RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
]


def _sanitize_subtitle(text: str) -> str:
    """Normalize subtitles without inserting placeholder glyphs."""
    for uni, asc in _SUBTITLE_REPLACEMENTS:
        text = text.replace(uni, asc)
    return clean_subtitle_text(text)


def _subtitle_chunks(text: str, start_f: int, end_f: int, max_end_f: int | None = None) -> list[dict]:
    """Split one spoken line into caption chunks that fill the voice-master scene."""
    clean = _sanitize_subtitle(text)
    words = clean.split()
    if not words or end_f <= start_f:
        return []
    max_end = max_end_f if max_end_f is not None else end_f
    max_end = max(start_f + 1, max_end)
    available_f = max(1, max_end - start_f)
    target_chunks = max(1, math.ceil(len(words) / CAPTION_MAX_WORDS))

    total_wpm = len(words) / (available_f / FPS) * 60
    if len(clean) <= 38 and total_wpm <= CAPTION_MAX_WPM:
        return [{"text": clean, "start": start_f, "end": max_end}]

    if target_chunks <= 1:
        return [{"text": clean, "start": start_f, "end": max_end}]

    chunks: list[list[str]] = []
    per_chunk = math.ceil(len(words) / target_chunks)
    for i in range(0, len(words), per_chunk):
        chunks.append(words[i:i + per_chunk])
    while len(chunks) > target_chunks:
        chunks[-2].extend(chunks[-1])
        chunks.pop()

    min_chunk_f = round(CAPTION_MIN_SEC * FPS)
    required_f = sum(max(min_chunk_f, math.ceil((len(chunk) / CAPTION_MAX_WPM) * 60 * FPS)) for chunk in chunks)
    durations: list[int] = []
    for chunk in chunks:
        base = max(min_chunk_f, math.ceil((len(chunk) / CAPTION_MAX_WPM) * 60 * FPS))
        if required_f > available_f:
            base = max(1, math.floor(base * available_f / required_f))
        durations.append(base)
    while sum(durations) > available_f and max(durations) > 1:
        idx = durations.index(max(durations))
        durations[idx] -= 1
    while sum(durations) < available_f:
        idx = durations.index(max(durations))
        durations[idx] += 1

    cursor = start_f
    out: list[dict] = []
    for idx, chunk_words in enumerate(chunks):
        chunk_end = max(cursor + 1, cursor + durations[idx])
        if idx == len(chunks) - 1:
            chunk_end = max_end
        out.append({"text": " ".join(chunk_words), "start": cursor, "end": chunk_end})
        cursor = chunk_end
    return out


def _subtitle_frame_budget(text: str) -> int:
    """Minimum frame budget needed for readable chunked captions."""
    words = _sanitize_subtitle(text).split()
    if not words:
        return 0
    chunks = max(1, math.ceil(len(words) / CAPTION_MAX_WORDS))
    min_by_chunks = chunks * round(CAPTION_MIN_SEC * FPS)
    min_by_wpm = math.ceil((len(words) / CAPTION_MAX_WPM) * 60 * FPS)
    return max(min_by_chunks, min_by_wpm)


def _transition_type(i: int, scenes: list[dict], role: str | None, is_impact: bool) -> str | None:
    """Classify how scene i enters relative to i-1.

    continuation  — same visual world, smooth dissolve (narrator/civilian chain)
    cause_effect  — scene i is the direct consequence of i-1 (tap → impact card)
    break         — hard interruption by an authority character (wallet/spartan)
    """
    if i == 0 or not scenes:
        return None
    prev = scenes[-1]
    # Spartan: absolute authority = hard cut, no overlap
    if role == "spartan":
        return "break"
    # Wallet: interruption snap (dialogue back-and-forth)
    if role == "wallet":
        return "cause_effect"
    # Civilian responding to wallet = quick retort snap
    if role == "civilian" and prev.get("speakerRole") == "wallet":
        return "cause_effect"
    # Impact card immediately after a civilian phone-tap = cause-effect snap cut
    if is_impact and prev.get("civilianAction") == "pick_up_phone":
        return "cause_effect"
    # Narrator consequence after civilian actually tapped (boxes already in motion) = snap cut
    if role == "narrator" and prev.get("civilianAction") == "pick_up_phone" and prev.get("visualEvent") == "boxes_spawn":
        return "cause_effect"
    # Everything else in the same visual world = smooth continuation dissolve
    return "continuation"


_ROLE_RE = re.compile(
    r'^\[(?P<role>SPARTAN|CIVILIAN|IMPACT|WALLET|FUTURE|NARRATOR)(?::(?P<scene>[a-z_]+))?(?:\|(?P<mods>[a-z,]+))?\]\s*',
    re.IGNORECASE,
)

def _parse_role(raw: str) -> tuple[str, str | None, str | None, bool]:
    """Strip leading role tag and return (clean_text, role, scene_override, has_pause).

    Examples:
      "[SPARTAN:bank] Discipline."    -> ("Discipline.", "spartan", "bank",  False)
      "[SPARTAN:bank|pause] Control." -> ("Control.",    "spartan", "bank",  True)
      "[IMPACT] STAY BROKE"           -> ("STAY BROKE",  "impact",  None,   False)
      "No tag here"                   -> ("No tag here", None,      None,   False)
    """
    m = _ROLE_RE.match(raw)
    if not m:
        return raw, None, None, False
    role      = m.group("role").lower()
    scene     = m.group("scene")
    mods      = (m.group("mods") or "").lower()
    has_pause = "pause" in mods
    text      = raw[m.end():]
    return text, role, scene, has_pause

# ─── Background colors per emotion ───────────────────────────────────────────
_BG: dict[str, list[str]] = {
    "neutral":  ["#0a0514", "#1a0a2e"],
    "happy":    ["#041408", "#0b3516"],
    "sad":      ["#04081a", "#0c1e3e"],
    "shocked":  ["#1a0404", "#3c0a0a"],
    "thinking": ["#060414", "#0f0a38"],
}

# ─── TTS helpers ─────────────────────────────────────────────────────────────
def _measure_duration(path: Path) -> float:
    """Return exact MP3 duration in seconds.

    Tries mutagen.mp3.MP3 first (handles VBR Xing/VBRI header correctly),
    then generic mutagen, then falls back to file-size estimation.
    """
    try:
        from mutagen.mp3 import MP3
        dur = float(MP3(str(path)).info.length)
        if dur > 0.05:
            return dur
    except Exception:
        pass
    try:
        from mutagen import File
        af = File(str(path))
        if af and af.info.length > 0.05:
            return float(af.info.length)
    except Exception:
        pass
    # File-size estimate: edge-tts produces ~24 kbps VBR speech
    try:
        return max(0.3, path.stat().st_size / 3_000)
    except Exception:
        return 1.0


async def _synth(text: str, voice: str, out: Path) -> float:
    """Generate TTS to `out` and return EXACT audio duration in seconds."""
    import edge_tts
    if not voice.startswith("en-US-"):
        raise RuntimeError(f"Non en-US Edge voice blocked: {voice}")
    text = assert_english_subtitle_text(text, field="edge dialogue")
    comm = edge_tts.Communicate(
        text=text, voice=voice, rate="-5%",
        pitch="+0Hz", volume="+0%", boundary="WordBoundary",
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fh:
        async for chunk in comm.stream():
            if chunk.get("type") == "audio":
                fh.write(chunk["data"])
    return _measure_duration(out)


def _synth_sync(text: str, voice: str, out: Path) -> float:
    return asyncio.run(_synth(text, voice, out))


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _normalize_voice_audio(path: Path) -> None:
    """Denoise and normalize every voice line without trimming spoken tails."""
    try:
        tmp = path.with_suffix(".norm_tmp.mp3")
        cmd = [
            _ffmpeg_exe(), "-y", "-i", str(path),
            "-af", (
                "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,"
                "loudnorm=I=-14:LRA=8:TP=-1.5"
            ),
            "-c:a", "libmp3lame", "-q:a", "4",
            str(tmp),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            tmp.replace(path)
        elif tmp.exists():
            tmp.unlink()
    except Exception:
        pass


def _voice_mean_volume_db(path: Path) -> float | None:
    """Return ffmpeg volumedetect mean_volume in dB, if available."""
    try:
        cmd = [
            _ffmpeg_exe(), "-i", str(path),
            "-af", "volumedetect",
            "-f", "null", "-",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = (result.stderr or "") + (result.stdout or "")
        m = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB", output)
        return float(m.group(1)) if m else None
    except Exception:
        return None


def _tts(
    text:       str,
    role:       str | None,
    edge_voice: str,
    out:        Path,
    log:        Callable[[str], None],
) -> tuple[float, str]:
    """Route TTS to ElevenLabs (Spartan/impact) or edge-tts (Civilian/default).

    Returns (duration_sec, voice_id_used).
    Falls back to edge-tts silently if ElevenLabs is unavailable or errors.
    """
    def _el_api_key() -> str:
        """Check env first, then DB — so both .env and Settings page work."""
        k = os.getenv("ELEVENLABS_API_KEY", "").strip()
        if k:
            return k
        try:
            import database as _db
            return (_db.get_setting("elevenlabs_api_key") or "").strip()
        except Exception:
            return ""

    def _el_provider() -> str:
        p = os.getenv("VOICE_PROVIDER", "").strip().lower()
        if p:
            return p
        try:
            import database as _db
            return (_db.get_setting("voice_provider") or "edge-tts").strip().lower()
        except Exception:
            return "edge-tts"

    text = assert_english_subtitle_text(text, field=f"{role or 'default'} dialogue")
    role_key = "spartan" if role in ("spartan", "impact") else (
        "narrator" if role == "narrator" else (
            "wallet" if role == "wallet" else "civilian"
        )
    )
    api_key     = _el_api_key()
    provider    = _el_provider()

    use_elevenlabs = provider == "elevenlabs"

    if use_elevenlabs:
        if not api_key:
            raise RuntimeError("ElevenLabs selected, but ELEVENLABS_API_KEY is missing")
        from spartacus.voice.elevenlabs_provider import (
            generate_voice_line,
            CIVILIAN_SETTINGS, WALLET_SETTINGS, WALLET_SPEED, NARRATOR_SETTINGS,
        )
        if role_key == "spartan":
            settings = NARRATOR_SETTINGS
            speed = 1.0
        elif role_key == "narrator":
            settings = NARRATOR_SETTINGS
            speed = 1.0
        elif role_key == "wallet":
            settings = WALLET_SETTINGS
            speed = WALLET_SPEED
        else:
            settings = CIVILIAN_SETTINGS
            speed = 1.0
        voice_id = ELEVENLABS_FIXED_VOICES[role_key]
        result = generate_voice_line(
            text, voice_id, out,
            api_key=api_key, voice_settings=settings, speed=speed,
        )
        char_label = role_key.title()
        log(f"    [ElevenLabs:{char_label}:en-US] {voice_id} spd={speed} -> {result['duration']:.3f}s")
        _normalize_voice_audio(out)
        result["duration"] = _measure_duration(out)
        mean_db = _voice_mean_volume_db(out)
        if mean_db is not None:
            log(f"    [audio-normalized] mean={mean_db:.1f}dB")
            if mean_db < -24.0:
                raise RuntimeError(f"Voice QA failed: {role_key} audio too low ({mean_db:.1f}dB)")
        return result["duration"], f"el:{voice_id}:en-US"

    edge_voice = {
        "civilian": CIVILIAN_VOICE,
        "wallet": WALLET_VOICE,
        "spartan": NARRATOR_VOICE,
        "narrator": NARRATOR_VOICE,
    }[role_key]
    dur = _synth_sync(text, edge_voice, out)
    _normalize_voice_audio(out)
    dur = _measure_duration(out)
    mean_db = _voice_mean_volume_db(out)
    if mean_db is not None:
        log(f"    [audio-normalized] mean={mean_db:.1f}dB")
        if mean_db < -24.0:
            raise RuntimeError(f"Voice QA failed: {role_key} audio too low ({mean_db:.1f}dB)")
    return dur, f"edge:{edge_voice}:en-US"



# ─── Main entry point ─────────────────────────────────────────────────────────
def generate(
    script: str,
    voice: str = DEFAULT_VOICE,
    log: Optional[Callable[[str], None]] = None,
    concurrency: int = 4,
    scene_hold: float = 0.0,
) -> dict:
    """Convert a multi-line script into a 2D animated MP4.

    Returns a dict with keys:
      run_id, video_path, video_url, duration_sec, scenes (int), props
    """
    log = log or print
    script = repair_script_for_director_mode(script)

    # ── 1. Parse lines
    lines = [l.strip() for l in script.strip().splitlines() if l.strip()]
    if not lines:
        raise ValueError("Script is empty")

    run_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
    pub_dir = REMOTION_PUB / f"anim_{run_id}"
    out_dir = STORAGE_DIR / run_id
    pub_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    log(f"[anim] {len(lines)} scenes  run_id={run_id}")

    # ── 2 & 3. TTS + scene data
    scenes        = []
    start_frame   = 0
    wallet_entered = False   # tracks once wallet has spoken (enables duo layout)

    for i, raw_line in enumerate(lines):
        text, role, scene_override, has_pause = _parse_role(raw_line)
        text = assert_english_subtitle_text(text, field=f"scene {i + 1} dialogue")
        if role == "wallet":
            wallet_entered = True

        is_impact    = role == "impact"
        is_narrator  = role == "narrator"
        speaker_role = role if role in ("spartan", "civilian", "wallet", "future", "narrator") else None

        # Choose TTS voice
        if is_impact or role == "spartan":
            tts_voice = SPARTAN_VOICE
        elif role in ("civilian", "wallet", "future"):
            tts_voice = CIVILIAN_VOICE
        elif is_narrator:
            tts_voice = NARRATOR_VOICE
        else:
            tts_voice = voice  # fallback to caller-supplied default

        audio_name = f"scene_{i}.mp3"
        audio_path = pub_dir / audio_name

        log(f"  TTS [{i+1}/{len(lines)}] [{role or 'default'}]: {text[:50]}...")
        audio_dur, voice_id_used = _tts(text, role, tts_voice, audio_path, log)

        # ── Voice-master timing ─────────────────────────────────────────────
        # The generated voice file defines the scene duration. Visuals and
        # subtitles stretch to this window; transitions never overlap it.
        pause_sec = 0.0
        raw_dur   = audio_dur + SCENE_VOICE_BUFFER_SEC
        if is_impact:
            raw_dur = max(raw_dur, IMPACT_MIN)

        dur_frames = math.ceil(raw_dur * FPS) + SCENE_GAP_F

        # Subtitle window in frames (relative to this scene's frame 0)
        sub_start_f = round(pause_sec * FPS)
        sub_end_f   = round((pause_sec + audio_dur) * FPS)

        has_wallet_duo = wallet_entered and role in ("civilian", "wallet") and not is_impact

        emotion    = _detect_emotion(text)
        prop       = _detect_prop(text)
        scene_type = scene_override or (_detect_scene_type(text) if not is_impact else "default")
        # Decision moment: phone civilian shows hesitation expression
        if role in ("civilian", None) and (scene_type == "phone" or prop == "phone"):
            emotion = "thinking"
        bg         = _BG.get(emotion, _BG["neutral"])
        duo        = _has_duo(text)
        stat       = _has_stat(text)

        # ── Director annotations
        prev_role = scenes[-1].get("speakerRole") if scenes else None
        director  = _director(i, role, text, scene_type, has_pause, is_impact, prev_role)
        if director["bgOverride"]:
            scene_type = director["bgOverride"]
        if role in ("civilian", None) and director.get("visualEvent") in ("boxes_spawn", "money_drain"):
            emotion = "sad" if any(kw in text.lower() for kw in ["regret", "rent", "watched", "mistake"]) else "shocked"

        # ── Deduplicate consecutive sceneType — force variety
        # Skip dedup for explicit scene tags and for Spartan (always dark_void)
        if not is_impact and not scene_override and role not in ("spartan", "wallet"):
            prev_st = scenes[-1].get("sceneType") if scenes else None
            if scene_type == prev_st:
                for candidate in _SCENE_TYPE_POOL:
                    if candidate != prev_st:
                        scene_type = candidate
                        break

        entry: dict = {
            "text":             _sanitize_subtitle(text),
            "emotion":          emotion,
            "bgColors":         bg,
            "propIcon":         prop,
            "sceneType":        scene_type,
            "hasDuo":           duo,
            "hasWalletDuo":     has_wallet_duo,
            "hasStat":          stat,
            "audioSrc":         f"anim_{run_id}/{audio_name}",
            "startFrame":       start_frame,
            "durationInFrames": dur_frames,
            # Audio-sync metadata
            "audioDuration":    round(audio_dur, 3),
            "sceneDuration":    round(dur_frames / FPS, 3),
            "subtitleStart":    sub_start_f,
            "subtitleEnd":      sub_end_f,
            "subtitleChunks":    _subtitle_chunks(text, sub_start_f, sub_end_f, dur_frames - 1),
            "voiceId":          voice_id_used,
            "cameraAction":     director["cameraAction"],
        }
        if speaker_role:
            entry["speakerRole"] = speaker_role
        if is_impact:
            entry["isImpact"] = True
        if role == "wallet":
            entry["walletRole"] = True
        if role == "future":
            entry["futureRole"] = True
        if is_narrator:
            entry["narratorRole"] = True
        entry["audioDelay"] = 0.0
        if director["visualEvent"]:
            entry["visualEvent"] = director["visualEvent"]
        # Emit civilianAction for narrator, civilian, and wallet scenes
        # (wallet: civilian is the listening character in the duo frame)
        if is_narrator and director["civilianAction"]:
            entry["civilianAction"] = director["civilianAction"]
        elif speaker_role == "civilian" and director["civilianAction"]:
            entry["civilianAction"] = director["civilianAction"]
        elif role == "wallet" and director["civilianAction"]:
            entry["civilianAction"] = director["civilianAction"]
        if speaker_role == "spartan" and director["spartanAction"]:
            entry["spartanAction"] = director["spartanAction"]
        t_type = _transition_type(i, scenes, role, is_impact)
        if t_type:
            entry["transitionIn"] = t_type

        # ── FAIL CONDITION: narrator scenes must have visual event + background + action
        if is_narrator:
            missing = []
            if not entry.get("visualEvent"):
                missing.append("visualEvent")
            if not entry.get("sceneType") or entry.get("sceneType") == "default":
                missing.append("sceneType(non-default)")
            if not entry.get("civilianAction") or entry.get("civilianAction") == "idle":
                missing.append("civilianAction(non-idle)")
            if missing:
                raise RuntimeError(
                    f"Narrator scene {i} FAIL — missing: {', '.join(missing)} | "
                    f"text={text!r} | Fix: add keywords to _NARRATOR_VISUAL_MAP/_NARRATOR_BG_MAP"
                )

        scenes.append(entry)
        flags = (f"[{role}] " if role else "") + ("DUO " if duo else "") + ("STAT" if stat else "")
        log(f"    audio={audio_dur:.2f}s  scene={raw_dur:.2f}s ({dur_frames}f)  "
            f"sub=[{sub_start_f}:{sub_end_f}f]  {flags}{emotion}/{scene_type}"
            + (f"  event={entry.get('visualEvent')}  civ={entry.get('civilianAction')}" if is_narrator else ""))
        start_frame += dur_frames

    if scenes and scenes[-1].get("speakerRole") == "spartan":
        scenes[-1]["durationInFrames"] += ENDING_HOLD_F
        scenes[-1]["sceneDuration"] = round(scenes[-1]["durationInFrames"] / FPS, 3)

    # ── Timeline: voice is the master clock; no scene starts before the previous
    # voice and post-voice buffer have completed.
    _cf = 0
    for _i, _s in enumerate(scenes):
        _s["startFrame"] = _cf
        _next_t = scenes[_i + 1].get("transitionIn") if _i + 1 < len(scenes) else None
        _lap    = _CROSS_FADE.get(_next_t or "", 0)
        _cf    += _s["durationInFrames"] - (_lap if _i < len(scenes) - 1 else 0)
    scenes = repair_scene_life(scenes)
    life_issues = scene_life_issues(scenes)
    if life_issues:
        log("[director] scene life repaired: " + "; ".join(life_issues[:6]))
    total_frames = _cf
    validate_voice_master_timeline(scenes, FPS)

    # ── 4. Props JSON
    props = {
        "scenes":                scenes,
        "totalDurationInFrames": total_frames,
        "fps":                   FPS,
        "enableSfx":             True,
        "enableBackgroundMusic": True,
        "channelMode":           "SPARTAN_WALLET",
    }
    props = qa_clean_subtitle_payload(props)
    kaizen_report = spartan_wallet_kaizen_report(props)
    props["kaizenReport"] = kaizen_report
    props_path = out_dir / "props.json"
    props_path.write_text(
        json.dumps(props, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(f"[anim] total {total_frames}f = {total_frames/FPS:.1f}s")
    log(
        "[kaizen] SPARTAN_WALLET "
        + ("accepted" if kaizen_report["accepted"] else "review: " + ", ".join(kaizen_report["reject_reasons"][:6]))
    )

    # ── 5. Remotion render
    out_mp4 = out_dir / "video.mp4"
    cmd = [
        "npm", "exec", "--", "remotion", "render",
        str(REMOTION_SRC),
        "FunnyFinance2D",
        str(out_mp4),
        f"--props={props_path}",
        f"--frames=0-{total_frames - 1}",
        f"--concurrency={concurrency}",
    ]
    log(f"[anim] $ {' '.join(str(c) for c in cmd)}")

    t0 = time.monotonic()
    render_log_lines: list[str] = []
    proc = subprocess.Popen(
        cmd,
        cwd=str(REMOTION_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
        bufsize=1,
        shell=True,
    )
    try:
        while True:
            line_ = proc.stdout.readline() if proc.stdout else ""
            if not line_:
                if proc.poll() is not None:
                    break
                continue
            render_log_lines.append(line_.rstrip())
            log(f"  [remotion] {line_.rstrip()}")
        rc = proc.wait()
    finally:
        if proc.stdout:
            proc.stdout.close()

    elapsed = time.monotonic() - t0

    if rc != 0:
        raise RuntimeError(
            f"Remotion render failed (exit {rc}). Check logs above."
        )
    if not out_mp4.exists() or out_mp4.stat().st_size == 0:
        raise RuntimeError(f"Render claimed OK but {out_mp4} is missing/empty")

    size_mb = out_mp4.stat().st_size / 1024 / 1024
    log(f"[anim] render OK -> {size_mb:.1f}MB in {elapsed:.1f}s")

    # ── 6. Timing manifest ──────────────────────────────────────────────────
    manifest = {
        "run_id":             run_id,
        "video_path":         str(out_mp4),
        "total_duration_sec": round(total_frames / FPS, 3),
        "fps":                FPS,
        "generated_at":       datetime.now().isoformat(timespec="seconds"),
        "voice_provider":     os.getenv("VOICE_PROVIDER", "edge-tts"),
        "scenes": [
            {
                "index":          i,
                "text":           s["text"],
                "role":           (
                    "impact" if s.get("isImpact")
                    else s.get("speakerRole", "default")
                ),
                "voice_id":       s.get("voiceId", ""),
                "audio_path":     str(pub_dir / f"scene_{i}.mp3"),
                "audio_duration": s.get("audioDuration"),
                "scene_start":    round(s["startFrame"] / FPS, 3),
                "scene_end":      round((s["startFrame"] + s["durationInFrames"]) / FPS, 3),
                "subtitle_start": round(s.get("subtitleStart", 0) / FPS, 3),
                "subtitle_end":   round(s.get("subtitleEnd",   s["durationInFrames"]) / FPS, 3),
                "pause_before":   s.get("audioDelay", 0.0),
            }
            for i, s in enumerate(scenes)
        ],
    }
    manifest_path = out_dir / "timing_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(f"[anim] timing manifest -> {manifest_path.name}")

    quality_dir = STORAGE_DIR / "quality_reports"
    quality_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "kaizen_report.json"
    report_path.write_text(
        json.dumps(kaizen_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (quality_dir / f"{run_id}_kaizen.json").write_text(
        json.dumps(kaizen_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # ── 7. Read-only self-audit report ─────────────────────────────────────
    try:
        from video_audit.audit_engine import audit_video

        audit_report = audit_video(
            out_mp4,
            props_path=props_path,
            manifest_path=manifest_path,
            log_text="\n".join(render_log_lines),
            save=True,
        )
        audit_path = out_dir / "video_audit_report.json"
        audit_path.write_text(
            json.dumps(audit_report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log(
            "[audit] "
            f"{audit_report.get('status')} overall={audit_report.get('score', {}).get('overall')} "
            f"issues={len(audit_report.get('issues', []))} -> {audit_path.name}"
        )
        for issue in audit_report.get("issues", [])[:5]:
            log(
                "[audit] "
                f"{issue.get('severity')} {issue.get('type')} {issue.get('timestamp')}: "
                f"{issue.get('description')}"
            )
        for line in json.dumps(audit_report, indent=2, ensure_ascii=False).splitlines():
            log(f"[audit-json] {line}")
    except Exception as exc:
        log(f"[audit] skipped: {exc}")

    return {
        "run_id":       run_id,
        "video_path":   str(out_mp4),
        "video_url":    f"/storage/animation/{run_id}/video.mp4",
        "duration_sec": round(total_frames / FPS, 1),
        "scenes":       len(scenes),
        "props":        props,
    }
