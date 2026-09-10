"""Tests for the rebuilt spartacus/agents/product_locker.py."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spartacus.agents import _shared, product_locker  # noqa: E402


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    # append_record resolves DATA_DIR at call time via the _shared module global.
    monkeypatch.setattr(_shared, "DATA_DIR", tmp_path)
    return tmp_path


def test_lock_persists_spec_shaped_record(data_dir):
    rec = product_locker.lock(
        topic="AI tools to make money online review",
        primary_product="Notion AI",
        offer_url="https://www.notion.so/product/ai",
        affiliate_program="(MVP: fill manually)",
        commission_type="(MVP: fill manually)",
        why_this_product_matches_topic="Notion AI is the best-fit affiliate offer.",
    )
    for k in ("id", "created_at", "topic", "primary_product", "affiliate_program",
              "offer_url", "commission_type", "support_products",
              "why_this_product_matches_topic"):
        assert k in rec, k
    assert rec["id"] == 1
    assert rec["offer_url"] == "https://www.notion.so/product/ai"   # verbatim
    assert rec["support_products"] == []

    saved = json.loads((data_dir / "products.json").read_text(encoding="utf-8"))
    assert saved[0]["primary_product"] == "Notion AI"

    rec2 = product_locker.lock(topic="t2", primary_product="P2",
                               support_products=["A", "B"])
    assert rec2["id"] == 2
    assert rec2["offer_url"] == ""
    assert rec2["support_products"] == ["A", "B"]


def test_lock_strips_fake_links_from_rationale(data_dir):
    rec = product_locker.lock(
        topic="t", primary_product="P",
        why_this_product_matches_topic="Great fit, see https://example.com/buy and [link]",
    )
    assert "example.com" not in rec["why_this_product_matches_topic"]
    assert "[link]" not in rec["why_this_product_matches_topic"]
    assert rec["why_this_product_matches_topic"].startswith("Great fit")


def test_lock_keeps_registered_offer_url_in_rationale(data_dir):
    url = "https://www.notion.so/product/ai"
    rec = product_locker.lock(
        topic="t", primary_product="P", offer_url=url,
        why_this_product_matches_topic=f"Offer lives at {url}",
    )
    assert url in rec["why_this_product_matches_topic"]


def test_lock_requires_keyword_only_product(data_dir):
    with pytest.raises(TypeError):
        product_locker.lock("topic", "Notion AI")  # type: ignore[misc]
