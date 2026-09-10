"""Amazon Affiliate Content Engine.

Picks 3-5 real products from a curated catalog each day and generates
short-form video ideas to promote them. Bound to the operator's allowed
niches (productivity, business, AI, work-from-home, content creation)
so suggestions stay relevant - never random Amazon junk.

For each product the engine emits:

    {
      "product":             "<real product name>",
      "niche":               "<one of the 5 allowed niches>",
      "solves":              "<catalog note - the real pain>",
      "problem_solved":      "<concrete pain it solves>",
      "viral_hook":          "<scroll-stopping first line, <=12 words>",
      "script_30s":          "<~70-word voiceover, full 30s shoot>",
      "content_angle":       "<the framing - demo, comparison, day-in-life, etc.>",
      "cta":                 "<call to action>",
      "link_intro_timing":   "<when in the script to drop the link>",
      "affiliate_url":       "<verbatim from the registry, or empty>",
      "cta_only_mode":       True/False,
      "cta_only_banner":     "NO LINK AVAILABLE - CTA ONLY MODE" if no link,
      "link_warnings":       [<warnings from validate_and_clean>],
      "raw_llm_output":      "<untouched LLM text, for audit>"
    }

Output is run through `_link_guard.validate_and_clean()` so even if the
LLM tries to invent an Amazon URL or a tracking ID, it gets stripped
unless a real registered URL exists for that product.

Catalog is intentionally curated. Adding a new product means appending
to `_PRODUCT_CATALOG` below - no LLM-generated product names, no ASIN
hallucination. Every product listed is widely available on Amazon and
solves a real problem in one of the 5 allowed niches.

If the LLM is unreachable the engine falls back to deterministic
template text (flagged in `raw_llm_output`) so `run_daily` never crashes
the morning-brief scheduler.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date, datetime
from typing import Iterable

from ._shared import DATA_DIR, llm_call, parse_kv_block, save_json, load_json
from ._link_guard import validate_and_clean, NO_LINK_BANNER


ALLOWED_NICHES = ("productivity", "business", "ai", "work_from_home",
                  "content_creation")

# Curated, real, widely-sold Amazon products. {product, niche, solves}.
_PRODUCT_CATALOG: list[dict] = [
    # productivity
    {"product": "Logitech MX Master 3S Wireless Mouse", "niche": "productivity",
     "solves": "Hand fatigue and slow scrolling for people who work in long browser/spreadsheet sessions."},
    {"product": "Logitech MX Keys Advanced Wireless Keyboard", "niche": "productivity",
     "solves": "Cramped, noisy laptop keyboards for knowledge workers typing 6+ hours/day."},
    {"product": "Apple AirPods Pro (2nd generation)", "niche": "productivity",
     "solves": "Open-office and cafe distractions for deep-focus blocks."},
    {"product": "Bose QuietComfort 45 Headphones", "niche": "productivity",
     "solves": "Background noise that wrecks concentration on calls and writing sprints."},
    {"product": "Rocketbook Smart Reusable Notebook", "niche": "productivity",
     "solves": "Throwing out paper notebooks after a week, and never finding old notes."},
    # business
    {"product": "Brother HL-L2350DW Compact Laser Printer", "niche": "business",
     "solves": "Last-minute contract printing and paper invoices for solo operators."},
    {"product": "Fujitsu ScanSnap iX1600 Document Scanner", "niche": "business",
     "solves": "Receipt and contract pile-up for tax season and bookkeeping."},
    {"product": "Dymo LabelWriter 550 Label Printer", "niche": "business",
     "solves": "Hand-writing shipping labels for ecommerce side hustles and Etsy stores."},
    {"product": "Square Reader for contactless and chip", "niche": "business",
     "solves": "Losing in-person sales because you only take cash or e-transfer."},
    {"product": "Anker 737 Power Bank (PowerCore 24K)", "niche": "business",
     "solves": "Dying laptop batteries during client meetings and travel."},
    # ai
    {"product": "NVIDIA GeForce RTX 4060 Ti 16GB GPU", "niche": "ai",
     "solves": "Running local LLMs and Stable Diffusion at home without renting cloud GPUs."},
    {"product": "Raspberry Pi 5 8GB Starter Kit", "niche": "ai",
     "solves": "Building always-on home AI agents and automations on a tiny budget."},
    {"product": "Coral USB Accelerator (Edge TPU)", "niche": "ai",
     "solves": "Running computer-vision AI at the edge without sending video to the cloud."},
    {"product": "Jabra Speak2 75 USB Speakerphone", "niche": "ai",
     "solves": "Garbled audio when using ChatGPT voice / AI meeting assistants in a small office."},
    {"product": "Crucial T700 2TB Gen5 NVMe SSD", "niche": "ai",
     "solves": "Slow load times when fine-tuning models or shuffling huge datasets locally."},
    # work_from_home
    {"product": "Herman Miller Sayl Office Chair", "niche": "work_from_home",
     "solves": "Lower-back pain from 8-hour days in a kitchen-table chair."},
    {"product": "FlexiSpot E7 Pro Standing Desk", "niche": "work_from_home",
     "solves": "Stiffness, slouching, and afternoon energy crashes for full-time remote workers."},
    {"product": "Apollo Horizon Monitor Light Bar", "niche": "work_from_home",
     "solves": "Eye strain from overhead office lighting that glares on the monitor."},
    {"product": "TP-Link Deco XE75 Mesh Wi-Fi 6E System", "niche": "work_from_home",
     "solves": "Dropped Zoom calls and dead spots in apartments and 2-floor homes."},
    {"product": "Logitech C920x HD Pro Webcam", "niche": "work_from_home",
     "solves": "Looking like a potato on Zoom because of laptop's built-in webcam."},
    {"product": "Desk Cable Organizer", "niche": "work_from_home",
     "solves": "Tangled cables under the desk that snag chairs, collect dust, and ruin on-camera setups."},
    # content_creation
    {"product": "Elgato Stream Deck MK.2 (15 keys)", "niche": "content_creation",
     "solves": "Fumbling OBS scenes and tab-switching mid-livestream or mid-recording."},
    {"product": "Rode PodMic USB Microphone", "niche": "content_creation",
     "solves": "Tinny laptop-mic audio that kills retention on Shorts and podcasts."},
    {"product": "DJI Osmo Mobile 6 Smartphone Gimbal", "niche": "content_creation",
     "solves": "Shaky b-roll and walk-and-talk shots that look amateur next to creators using rigs."},
    {"product": "Elgato Key Light Air", "niche": "content_creation",
     "solves": "Dim, yellow webcam footage that sinks ad reads and on-camera presence."},
    {"product": "Insta360 X3 360-Camera", "niche": "content_creation",
     "solves": "Re-shooting clips because you missed the action - one shot captures everything."},
]

# Registry of REAL affiliate URLs: {product: {url, added_at, notes}}.
AFFILIATE_LINKS_PATH = DATA_DIR / "affiliate_links.json"


# ---------- affiliate registry ----------

def _norm_product(name: str) -> str:
    return (name or "").strip().lower()


def load_affiliate_links() -> dict:
    """Load the registry from disk. Always returns a dict (empty if
    missing/corrupt)."""
    data = load_json(AFFILIATE_LINKS_PATH, default={})
    if not isinstance(data, dict):
        return {}
    out: dict = {}
    for k, v in data.items():
        if isinstance(v, dict) and str(v.get("url") or "").strip():
            out[k] = v
        elif isinstance(v, str) and v.strip():
            out[k] = {"url": v.strip(), "added_at": "", "notes": ""}
    return out


def get_affiliate_url(product_name: str) -> str:
    """Return the exact stored URL for a product, or ''. Lookup is
    case-insensitive on the product name; the URL is returned verbatim."""
    target = _norm_product(product_name)
    if not target:
        return ""
    for k, v in load_affiliate_links().items():
        if _norm_product(k) == target:
            return (v.get("url") or "").strip()
    return ""


def register_affiliate_link(product_name: str, url: str, notes: str = "") -> dict:
    """Save (or replace) a product's affiliate URL in the registry.
    The URL is stored EXACTLY as provided - no normalization, no
    parameter rewrites. Returns the registry entry."""
    pname = (product_name or "").strip()
    purl = (url or "").strip()
    if not pname or not purl:
        raise ValueError("Both product_name and url are required.")
    registry = load_affiliate_links()
    existing_key = next(
        (k for k in registry if _norm_product(k) == _norm_product(pname)), None)
    key = existing_key or pname
    registry[key] = {
        "url": purl,
        "added_at": datetime.now().isoformat(timespec="seconds"),
        "notes": (notes or "").strip(),
    }
    save_json(AFFILIATE_LINKS_PATH, registry)
    return registry[key]


def remove_affiliate_link(product_name: str) -> bool:
    """Delete a product from the registry. Returns True if removed."""
    target = _norm_product(product_name)
    registry = load_affiliate_links()
    removed = False
    for k in list(registry):
        if _norm_product(k) == target:
            del registry[k]
            removed = True
    if removed:
        save_json(AFFILIATE_LINKS_PATH, registry)
    return removed


# ---------- catalog + daily pick ----------

def list_catalog(niches: Iterable[str] = ()) -> list[dict]:
    """Return a copy of the catalog, optionally filtered to specific
    niches. Unknown niches are silently ignored. Operator never gets
    products outside ALLOWED_NICHES."""
    wanted = {(n or "").strip().lower() for n in (niches or ())}
    wanted = {n for n in wanted if n in ALLOWED_NICHES}
    return [dict(row) for row in _PRODUCT_CATALOG
            if not wanted or row["niche"] in wanted]


def _seed_for_day(day: date) -> int:
    """Stable per-day seed so the same date always picks the same products
    until the catalog changes. Hash includes the catalog length so adding
    new products doesn't preserve a stale daily pick."""
    h = hashlib.sha256(
        f"{day.isoformat()}|{len(_PRODUCT_CATALOG)}".encode()).hexdigest()
    return int(h[:12], 16)


def pick_products(count: int, day: date | None = None,
                  niches: Iterable[str] = (),
                  exclude_recent_days: int = 7) -> list[dict]:
    """Pick `count` products for a given day, rotating to avoid repeats
    from the last `exclude_recent_days` daily files."""
    day = day or date.today()
    pool = list_catalog(niches)
    if not pool:
        raise ValueError(
            f"No catalog products match niches={list(niches or ())}. "
            f"Allowed niches: {list(ALLOWED_NICHES)}")

    used_recent: set[str] = set()
    base = DATA_DIR / "amazon"
    if base.exists() and exclude_recent_days > 0:
        files = sorted(base.glob("*.json"), reverse=True)
        files = [fp for fp in files if fp.stem != day.isoformat()]
        for fp in files[:exclude_recent_days]:
            data = load_json(fp, default={})
            if not isinstance(data, dict):
                continue
            for idea in data.get("ideas") or []:
                p = (idea.get("product") or "").strip().lower() if isinstance(idea, dict) else ""
                if p:
                    used_recent.add(p)

    rng = random.Random(_seed_for_day(day))
    fresh = [r for r in pool if r["product"].lower() not in used_recent]
    fallback = [r for r in pool if r["product"].lower() in used_recent]
    rng.shuffle(fresh)
    rng.shuffle(fallback)
    count = max(1, count)
    chosen = (fresh + fallback)[:count]
    return chosen


# ---------- LLM generation ----------

_PROMPT = """You are a viral short-form scriptwriter who promotes real Amazon
products to a productivity / business / AI / WFH / content-creation audience.

Write a 30-second video pitch for this product:

PRODUCT:        "{product}"
NICHE:          {niche}
REAL PROBLEM:   {solves}

Output EXACTLY these 6 sections, one per line, uppercase keys:

PROBLEM_SOLVED: <2 sentences max - the SPECIFIC pain the audience feels>
VIRAL_HOOK: <one scroll-stopping first line, <=12 words, no clickbait fluff>
SCRIPT_30S: <~70 words, plain spoken English, 4-6 short sentences. Starts with the hook. Ends just before the CTA.>
CONTENT_ANGLE: <one of: live-demo, comparison, day-in-life, before/after, mistake-reveal, expert-tip - pick the one that fits and explain in 1 line>
CTA: <{cta_directive}>
LINK_INTRO_TIMING: <when in the video to introduce/say the link, e.g. "after the demo at the 22-second mark", or "in the pinned comment", or "skip - CTA only">

HARD RULES:
- {link_rule}
- No invented stats, no "guaranteed", no "doctors hate", no fake urgency.
- No filler ("today I want to talk about", "in this video"). Cut every word that doesn't earn its place.
- Stay inside the {niche} niche. Don't drift into unrelated product categories."""

_IDEA_FIELDS = ("problem_solved", "viral_hook", "script_30s", "content_angle",
                "cta", "link_intro_timing")


def _cta_directive(cta_only: bool) -> str:
    if cta_only:
        return ("the CTA must be one of: Follow for the next pick, Comment with "
                "your setup, DM for the link, or Join the waitlist. Do NOT "
                "mention 'link in bio' or any URL.")
    return ("a 1-line CTA that drives the viewer to the affiliate link without "
            "sounding salesy. Disclose the affiliate relationship in 5 words or less.")


def _link_rule(cta_only: bool) -> str:
    if cta_only:
        return ("NO LINK MODE: there is no affiliate link for this product. Do NOT "
                "invent any URL, ASIN, amzn.to short link, or '#linkinbio' tag. "
                "The system will reject any URL you emit.")
    return ("Do NOT invent an Amazon URL or ASIN. The system will attach the real "
            "affiliate link separately - your job is the script.")


def _fallback_fields(product: str, niche: str, solves: str,
                     cta_only: bool) -> dict:
    """Deterministic template text used when the LLM is unavailable or
    returns nothing usable. Contains no URLs."""
    pain = solves.rstrip(".") or f"the daily friction {product} removes"
    return {
        "problem_solved": f"{pain}. Most people just put up with it.",
        "viral_hook": f"Stop fighting {pain.split(' ')[0].lower()} problems every single day",
        "script_30s": (
            f"{pain} - sound familiar? That's exactly what {product} fixes. "
            f"It's built for the {niche.replace('_', ' ')} crowd: set it up once and "
            f"the problem disappears. No hacks, no workarounds, just the tool that "
            f"does the job. Here's what changed for me the first week."
        ),
        "content_angle": "before/after - show the pain, then the fix in one shot",
        "cta": ("Follow for the next pick" if cta_only
                else "Check description (affiliate link)"),
        "link_intro_timing": ("skip - CTA only mode (no real link)" if cta_only
                              else "after the demo at the 22-second mark"),
    }


def generate_idea(product_row: dict, affiliate_url: str = "",
                  model: str | None = None) -> dict:
    """Generate one full idea dict for a single product row."""
    product = (product_row.get("product") or "").strip()
    niche = (product_row.get("niche") or "").strip()
    solves = (product_row.get("solves") or "").strip()
    affiliate_url = (affiliate_url or "").strip()
    cta_only = not affiliate_url

    prompt = _PROMPT.format(
        product=product, niche=niche, solves=solves,
        cta_directive=_cta_directive(cta_only), link_rule=_link_rule(cta_only),
    )
    try:
        raw = llm_call(prompt, model=model) or ""
    except Exception as e:  # noqa: BLE001 - never crash the brief
        raw = f"FALLBACK: LLM unavailable ({type(e).__name__}: {e})"
    parsed = parse_kv_block(raw)
    fields = {k: (parsed.get(k) or "").strip() for k in _IDEA_FIELDS}
    if not fields["script_30s"] or not fields["viral_hook"]:
        fb = _fallback_fields(product, niche, solves, cta_only)
        for k in _IDEA_FIELDS:
            fields[k] = fields[k] or fb[k]
        if not raw.startswith("FALLBACK:"):
            raw = f"FALLBACK: LLM output unusable\n\n{raw}".strip()

    allowed = [affiliate_url] if affiliate_url else []
    warnings: list[str] = []
    seen: set[str] = set()
    for k in _IDEA_FIELDS:
        cleaned, warns = validate_and_clean(fields[k], allowed)
        fields[k] = cleaned
        for w in warns:
            if w not in seen:
                seen.add(w)
                warnings.append(w)
    if cta_only:
        fields["link_intro_timing"] = "skip - CTA only mode (no real link)"

    return {
        "product": product,
        "niche": niche,
        "solves": solves,
        **fields,
        "affiliate_url": affiliate_url,
        "cta_only_mode": cta_only,
        "cta_only_banner": NO_LINK_BANNER if cta_only else "",
        "link_warnings": warnings,
        "raw_llm_output": raw,
    }


# ---------- daily run ----------

def run_daily(count: int = 3, day: date | None = None,
              niches: Iterable[str] = (),
              affiliate_urls: dict[str, str] | None = None,
              model: str | None = None) -> dict:
    """Generate `count` ideas for `day` (default today) and save to
    `spartacus/data/amazon/YYYY-MM-DD.json` + a `.md` digest.

    **STRICT lock mode** - when a product is locked in
    `config/affiliate_links.json` (`product_lock.get_active_lock()`), the
    entire brief targets that ONE product: all `count` ideas are angle
    variations of the locked product, the catalog is bypassed and the
    niches filter is ignored. With a registered link (`strict_monetized`)
    CTA-only mode is forced OFF; without one (`strict_pending`) every
    idea runs CTA-only until the link is added.

    **Discovery mode** - no product locked: pick `count` products from
    the catalog, attach the registry's link if one exists, fall back to
    CTA-only otherwise.

    `affiliate_urls` is a {product_name -> url} mapping for products
    where the operator has a real link (merged over the registry).
    Anything not covered falls back to CTA-only mode for that product.
    """
    from spartacus import product_lock

    count = max(1, min(5, int(count or 3)))
    day = day or date.today()
    niches = [n for n in (niches or ()) if n]

    lock = product_lock.get_active_lock()
    if lock:
        locked_url = (lock.get("affiliate_link") or "").strip()
        locked_row = {
            "product": (lock.get("name") or lock.get("key") or "").strip(),
            "niche": (lock.get("niche") or "business").strip(),
            "solves": (lock.get("solves") or "").strip(),
        }
        ideas = [generate_idea(locked_row, affiliate_url=locked_url, model=model)
                 for _ in range(count)]
        any_cta_only = not locked_url
        payload = {
            "date": day.isoformat(),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "count": len(ideas),
            "niches_filter": [locked_row["niche"]],
            "lock_state": "strict_monetized" if locked_url else "strict_pending",
            "locked_product": locked_row["product"],
            "any_cta_only_mode": any_cta_only,
            "banner": NO_LINK_BANNER if any_cta_only else "",
            "ideas": ideas,
        }
    else:
        merged: dict[str, str] = {}
        for k, v in load_affiliate_links().items():
            merged[_norm_product(k)] = (v.get("url") or "").strip()
        for k, v in (affiliate_urls or {}).items():
            if (v or "").strip():
                merged[_norm_product(k)] = v.strip()

        chosen = pick_products(count, day=day, niches=niches)
        ideas = []
        for row in chosen:
            url = merged.get(_norm_product(row["product"]), "")
            ideas.append(generate_idea(row, affiliate_url=url, model=model))
        any_cta_only = any(i["cta_only_mode"] for i in ideas)
        payload = {
            "date": day.isoformat(),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "count": len(ideas),
            "niches_filter": niches or list(ALLOWED_NICHES),
            "lock_state": "discovery",
            "any_cta_only_mode": any_cta_only,
            "banner": NO_LINK_BANNER if any_cta_only else "",
            "ideas": ideas,
        }

    out_dir = DATA_DIR / "amazon"
    json_path = out_dir / f"{day.isoformat()}.json"
    md_path = out_dir / f"{day.isoformat()}.md"
    save_json(json_path, payload)
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def _render_markdown(payload: dict) -> str:
    """Operator-facing daily brief."""
    lines = [f"# Amazon Daily Picks - {payload.get('date')}",
             f"*Generated {payload.get('generated_at')}*", ""]
    state = payload.get("lock_state")
    if state == "strict_monetized":
        lines.append(f"> **STRICT LOCK** - all {payload.get('count')} ideas focused on "
                     f"**{payload.get('locked_product')}** (affiliate link attached, "
                     f"monetization on).")
        lines.append("")
    elif state == "strict_pending":
        lines.append("> **STRICT LOCK (pending)** - product is locked but no affiliate "
                     "link registered yet. Running in CTA-only mode until the link is added.")
        lines.append("")
    elif payload.get("any_cta_only_mode"):
        lines.append(f"> **{NO_LINK_BANNER}** - one or more ideas have no real "
                     f"affiliate link. Add the link before publishing.")
        lines.append("")

    for i, idea in enumerate(payload.get("ideas") or [], 1):
        lines.append(f"## {i}. {idea.get('product')}  _({idea.get('niche')})_")
        if idea.get("cta_only_mode"):
            lines.append(f"> {NO_LINK_BANNER}")
        elif idea.get("affiliate_url"):
            lines.append(f"**Affiliate URL:** {idea.get('affiliate_url')}")
        lines.append("")
        lines.append(f"**Problem solved:** {idea.get('problem_solved')}")
        lines.append("")
        lines.append(f"**Hook:** {idea.get('viral_hook')}")
        lines.append("")
        lines.append(f"**Angle:** {idea.get('content_angle')}")
        lines.append("")
        lines.append("**30s script:**")
        lines.append("")
        lines.append(idea.get("script_30s") or "")
        lines.append("")
        lines.append(f"**CTA:** {idea.get('cta')}")
        lines.append("")
        lines.append(f"**Link timing:** {idea.get('link_intro_timing')}")
        if idea.get("link_warnings"):
            lines.append("")
            lines.append(f"_Link guard: {', '.join(idea['link_warnings'])}_")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ---------- readers ----------

def load_day(day: date | None = None) -> dict:
    """Read the saved daily brief. Returns {} if not generated yet."""
    day = day or date.today()
    path = DATA_DIR / "amazon" / f"{day.isoformat()}.json"
    data = load_json(path, default={})
    return data if isinstance(data, dict) else {}


def list_recent(limit: int = 14) -> list[str]:
    """Return ISO dates of the most recent saved daily briefs."""
    base = DATA_DIR / "amazon"
    if not base.exists():
        return []
    return [p.stem for p in sorted(base.glob("*.json"), reverse=True)][:limit]
