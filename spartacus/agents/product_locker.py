"""Product Locker - bind a topic to one main affiliate offer.

MVP: manual input. The user passes the affiliate product info; this
agent stores the mapping and emits the spec-shaped record.

The `offer_url` is operator-supplied and stored EXACTLY as given (or
empty = CTA-only downstream). The free-text rationale is run through
the link guard so no placeholder / non-registered URL can ride along.
"""

from __future__ import annotations

from ._shared import append_record
from ._link_guard import validate_and_clean


def lock(topic: str, *, primary_product: str, affiliate_program: str = "",
         offer_url: str = "", commission_type: str = "",
         support_products: list[str] | None = None,
         why_this_product_matches_topic: str = "") -> dict:
    """Save the topic <-> product binding to data/products.json.
    Returns the saved record (with `id` and `created_at` injected)."""
    offer_url = (offer_url or "").strip()
    why, _warnings = validate_and_clean(
        why_this_product_matches_topic or "",
        allowed_urls=[offer_url] if offer_url else [],
    )
    record = {
        "topic": topic,
        "primary_product": primary_product,
        "affiliate_program": affiliate_program,
        "offer_url": offer_url,
        "commission_type": commission_type,
        "support_products": list(support_products or []),
        "why_this_product_matches_topic": why,
    }
    return append_record("products.json", record)
