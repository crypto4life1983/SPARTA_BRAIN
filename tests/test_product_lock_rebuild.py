"""Tests for the rebuilt spartacus/product_lock.py (config-backed lock)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spartacus import product_lock  # noqa: E402


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    path = tmp_path / "config" / "affiliate_links.json"
    monkeypatch.setattr(product_lock, "CONFIG_PATH", path)
    return path


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


LOCKED = {
    "active_product": "arm",
    "products": {
        "arm": {
            "name": "Amazon Rewards Mastercard",
            "affiliate_link": "https://amzn.to/real-link",
            "cta": "Apply here:",
            "disclosure": "As an affiliate I earn from qualifying sign-ups.",
            "niche": "business",
            "solves": "Cashback on Amazon purchases.",
        },
        "other": {"name": "Other", "affiliate_link": ""},
    },
}


def test_missing_config_is_discovery(cfg):
    assert not cfg.exists()
    assert product_lock.get_active_lock() is None
    assert product_lock.is_locked() is False
    assert product_lock.is_strict_lock() is False
    assert product_lock.lock_state() == "discovery"
    assert product_lock.list_products() == {}
    assert product_lock.get_bridge_page_url() == ""
    assert product_lock.has_bridge_page() is False


def test_corrupt_config_is_discovery(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text("{not json", encoding="utf-8")
    assert product_lock.get_active_lock() is None
    assert product_lock.lock_state() == "discovery"


def test_strict_monetized_lock(cfg):
    _write(cfg, LOCKED)
    lock = product_lock.get_active_lock()
    assert lock["key"] == "arm"
    assert lock["name"] == "Amazon Rewards Mastercard"
    assert lock["affiliate_link"] == "https://amzn.to/real-link"
    assert product_lock.is_locked() is True
    assert product_lock.is_strict_lock() is True
    assert product_lock.lock_state() == "strict_monetized"
    assert set(product_lock.list_products()) == {"arm", "other"}


def test_strict_pending_when_link_empty(cfg):
    _write(cfg, {**LOCKED, "active_product": "other"})
    assert product_lock.is_locked() is True
    assert product_lock.is_strict_lock() is False
    assert product_lock.lock_state() == "strict_pending"


def test_set_active_product_and_clear(cfg):
    _write(cfg, {**LOCKED, "active_product": None})
    assert product_lock.get_active_lock() is None
    out = product_lock.set_active_product("arm")
    assert out["key"] == "arm"
    assert product_lock.lock_state() == "strict_monetized"
    with pytest.raises(ValueError):
        product_lock.set_active_product("nope")
    assert product_lock.set_active_product("") is None
    assert json.loads(cfg.read_text(encoding="utf-8"))["active_product"] is None


def test_update_active_link_verbatim_and_clear(cfg):
    _write(cfg, LOCKED)
    url = "https://www.amazon.ca/dp/B07MJM4F44?tag=Mixed-Case_20&x=1 "
    entry = product_lock.update_active_link(url)
    assert entry["affiliate_link"] == url.strip()          # verbatim, only stripped
    assert entry["affiliate_link_updated_at"]
    assert product_lock.lock_state() == "strict_monetized"
    product_lock.update_active_link("")
    assert product_lock.lock_state() == "strict_pending"
    with pytest.raises(ValueError):
        product_lock.set_affiliate_link("nope", "https://x")


def test_update_active_link_requires_lock(cfg):
    with pytest.raises(RuntimeError):
        product_lock.update_active_link("https://x")


def test_bridge_page_roundtrip(cfg):
    _write(cfg, LOCKED)
    assert product_lock.set_bridge_page_url(" https://notion.site/bridge ") == "https://notion.site/bridge"
    assert product_lock.has_bridge_page() is True
    assert product_lock.get_bridge_page_url() == "https://notion.site/bridge"
    product_lock.set_bridge_page_url("")
    assert product_lock.has_bridge_page() is False


def test_build_description_no_lock_is_teaser_without_url(cfg):
    desc = product_lock.build_description("Follow for updates")
    assert desc.startswith("More details soon")
    assert "Follow for updates" in desc
    assert "http" not in desc


def test_build_description_pending_has_no_url(cfg):
    _write(cfg, {**LOCKED, "active_product": "other"})
    desc = product_lock.build_description("")
    assert "http" not in desc
    assert "Follow for updates" in desc


def test_build_description_direct_link_path(cfg):
    _write(cfg, LOCKED)
    desc = product_lock.build_description("Check description")
    lines = desc.split("\n\n")
    assert lines[0] == "Check description"
    assert lines[1] == "Apply here: https://amzn.to/real-link"
    assert lines[2].startswith("As an affiliate")
    assert desc.count("https://amzn.to/real-link") == 1


def test_build_description_bridge_path_is_four_lines(cfg):
    _write(cfg, {**LOCKED, "bridge_page_url": "https://notion.site/bridge"})
    desc = product_lock.build_description("You're losing cashback every order")
    lines = desc.split("\n")
    assert lines == [
        "You're losing cashback every order",
        "",
        "Check this here \U0001F447",
        "https://notion.site/bridge",
    ]
    assert "amzn.to" not in desc                    # raw affiliate link never leaks
    # Non-loss CTA falls back to the generic loss hook.
    desc2 = product_lock.build_description("Check description")
    assert desc2.split("\n")[0] == "You're losing money if you don't use this."
