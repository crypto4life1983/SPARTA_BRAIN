"""Product-lock helper. Single source of truth for the affiliate
product currently locked across the Shorts pipeline.

Config file: C:\\SPARTA_BRAIN\\config\\affiliate_links.json

Schema:
    {
      "active_product": "<key>",          # null = no lock active
      "bridge_page_url": "...",           # optional Notion/landing page
      "products": {
        "<key>": {
            "name": "...",
            "affiliate_link": "...",       # empty = paste from dashboard
            "cta": "Check the ... here:",
            "disclosure": "As an affiliate, ...",
            "niche": "business",
            "solves": "...",
            "target_keywords": [...]
        }
      }
    }

Usage:
    from spartacus import product_lock
    lock = product_lock.get_active_lock()      # dict or None
    product_lock.set_affiliate_link("amazon_rewards_mastercard", "https://...")

Does NOT touch: shorts_video, shorts_ideation working pipeline,
upload pipeline, link guard. This module is read-only by default
and only writes the affiliate_link / active_product / bridge_page_url
fields when the dashboard updates them. URLs are stored verbatim and
never rewritten. A missing config file means "no lock" (discovery).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "affiliate_links.json"

_NO_LINK_TEASER = "More details soon \U0001F447"


# ---------- raw io ----------

def _load_raw() -> dict:
    empty = {"active_product": None, "products": {}}
    if not CONFIG_PATH.exists():
        return empty
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return empty
    if not isinstance(data, dict):
        return empty
    data.setdefault("active_product", None)
    if not isinstance(data.get("products"), dict):
        data["products"] = {}
    return data


def _save_raw(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                           encoding="utf-8")


# ---------- read side ----------

def list_products() -> dict:
    """Return all configured products keyed by their config key."""
    return dict(_load_raw().get("products") or {})


def get_active_lock() -> dict | None:
    """Return the currently locked product as a dict (with `key` field
    added for convenience), or None if no product is locked / the
    config is missing the active product entry.
    """
    data = _load_raw()
    key = (data.get("active_product") or "").strip()
    if not key:
        return None
    products = data.get("products") or {}
    entry = products.get(key)
    if not isinstance(entry, dict):
        return None
    out = dict(entry)
    out["key"] = key
    return out


def is_locked() -> bool:
    return get_active_lock() is not None


def is_strict_lock() -> bool:
    """STRICT mode = product locked AND has a registered affiliate link.

    When True, every generator must:
      - produce content ONLY for the locked product (no catalog mixing)
      - attach the registered affiliate link
      - NEVER fall back to CTA-only mode

    When False (no lock, or lock with empty link), generators may run
    in discovery mode (multi-product) or CTA-only mode as appropriate.
    """
    lock = get_active_lock()
    return bool(lock and (lock.get("affiliate_link") or "").strip())


def lock_state() -> str:
    """Three-state classifier used by /viral-engine + amazon brief.
    Returns one of: 'strict_monetized', 'strict_pending', 'discovery'."""
    lock = get_active_lock()
    if not lock:
        return "discovery"
    if (lock.get("affiliate_link") or "").strip():
        return "strict_monetized"
    return "strict_pending"


# ---------- write side (dashboard only) ----------

def set_active_product(key: str) -> dict | None:
    """Switch which product is the active lock. Pass empty string to
    disable locking entirely."""
    data = _load_raw()
    key = (key or "").strip()
    products = data.get("products") or {}
    if key and key not in products:
        raise ValueError(
            f"Unknown product key {key!r}. Known: {list(products.keys())}")
    data["active_product"] = key or None
    _save_raw(data)
    return get_active_lock()


def set_affiliate_link(key: str, url: str) -> dict:
    """Update the affiliate_link of one stored product. URL is stored
    EXACTLY as passed - no normalization, no rewrites. Empty string is
    valid (clears the link, returns the pipeline to CTA-only mode)."""
    data = _load_raw()
    products = data.setdefault("products", {})
    if key not in products:
        raise ValueError(
            f"Unknown product key {key!r}. Known: {list(products.keys())}")
    products[key]["affiliate_link"] = (url or "").strip()
    products[key]["affiliate_link_updated_at"] = datetime.now().isoformat(
        timespec="seconds")
    _save_raw(data)
    return dict(products[key])


def update_active_link(url: str) -> dict:
    """Convenience: paste a new affiliate link for whichever product is
    currently active. Used by the dashboard input field."""
    data = _load_raw()
    key = (data.get("active_product") or "").strip()
    if not key:
        raise RuntimeError("No active product is locked - set one first.")
    return set_affiliate_link(key, url)


# ---------- bridge page ----------

def get_bridge_page_url() -> str:
    """Return the configured Notion/landing-page URL, or '' if not set."""
    return (_load_raw().get("bridge_page_url") or "").strip()


def set_bridge_page_url(url: str) -> str:
    """Set (or clear with '') the bridge page URL. Stored verbatim."""
    data = _load_raw()
    data["bridge_page_url"] = (url or "").strip()
    data["bridge_page_url_updated_at"] = datetime.now().isoformat(
        timespec="seconds")
    _save_raw(data)
    return data["bridge_page_url"]


def has_bridge_page() -> bool:
    return bool(get_bridge_page_url())


# ---------- description builder ----------

_LOSS_WORDS = ("losing", "lose", "miss", "missing", "leak", "wasting",
               "robbed", "left", "stolen")


def _loss_hook_for_description(short_cta: str, lock: dict | None) -> str:
    """Pick a short, loss-framed hook for line 1 of the bridge-page
    description. Prefers the per-short CTA if it carries loss energy
    (e.g. "You're losing cashback every order"); otherwise falls back
    to a generic loss line tied to the product."""
    short_cta = (short_cta or "").strip()
    if short_cta and any(w in short_cta.lower() for w in _LOSS_WORDS):
        return short_cta
    return "You're losing money if you don't use this."


def build_description(short_cta: str) -> str:
    """Build the YouTube description for an upload.

    THREE PATHS:

    1. **Bridge-page funnel** (strict_monetized + BRIDGE_PAGE_URL set) -
       4-line locked format that routes ALL traffic through the
       single Notion/landing page. Format:
           Line 1: <loss-framed hook>
           Line 2: <empty>
           Line 3: Check this here 👇
           Line 4: <BRIDGE_PAGE_URL>
       No raw affiliate link, no disclosure block in description (the
       bridge page carries it), no hashtag spam, no extra paragraphs.

    2. **Direct-link funnel** (lock + link, no bridge) - legacy fallback.
       short CTA + product CTA + raw affiliate link + disclosure.
       Used when the operator hasn't set up a bridge page yet.

    3. **Smart-path** (no lock OR no link) - audience builder.
       "More details soon 👇" + short CTA. No URL emitted.

    Called by shorts_video.upload(). Never invents URLs.
    """
    short_cta = (short_cta or "").strip() or "Follow for updates"
    lock = get_active_lock()
    link = (lock.get("affiliate_link") or "").strip() if lock else ""

    # Path 3 - no lock or no link: teaser only, never a URL.
    if not lock or not link:
        return f"{_NO_LINK_TEASER}\n\n{short_cta}"

    # Path 1 - bridge page funnel.
    bridge = get_bridge_page_url()
    if bridge:
        loss_hook = _loss_hook_for_description(short_cta, lock)
        return f"{loss_hook}\n\nCheck this here \U0001F447\n{bridge}"

    # Path 2 - direct link (legacy).
    cta = (lock.get("cta") or "").strip()
    disclosure = (lock.get("disclosure") or "").strip()
    parts = [short_cta, f"{cta} {link}".strip()]
    if disclosure:
        parts.append(disclosure)
    return "\n\n".join(parts)
