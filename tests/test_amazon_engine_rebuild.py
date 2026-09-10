"""Tests for the rebuilt spartacus/agents/amazon_engine.py.

All disk writes go to tmp (DATA_DIR + registry + product-lock config are
monkeypatched) and the LLM is faked - nothing touches Ollama or the real
spartacus/data tree.
"""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spartacus import product_lock  # noqa: E402
from spartacus.agents import amazon_engine as ae  # noqa: E402
from spartacus.agents._link_guard import NO_LINK_BANNER  # noqa: E402

IDEA_KEYS = {
    "product", "niche", "solves", "problem_solved", "viral_hook", "script_30s",
    "content_angle", "cta", "link_intro_timing", "affiliate_url",
    "cta_only_mode", "cta_only_banner", "link_warnings", "raw_llm_output",
}
TOP_KEYS = {"date", "generated_at", "count", "niches_filter", "lock_state",
            "any_cta_only_mode", "banner", "ideas"}

FAKE_LLM = (
    "PROBLEM_SOLVED: Shaky footage looks amateur.\n"
    "VIRAL_HOOK: Stop wobbling your phone!\n"
    "SCRIPT_30S: Here is a clean 30 second script. Check https://example.com/buy "
    "and https://amzn.to/fake123 for [link].\n"
    "CONTENT_ANGLE: live-demo\n"
    "CTA: Follow for the next pick\n"
    "LINK_INTRO_TIMING: after the demo at the 22-second mark\n"
)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(ae, "DATA_DIR", tmp_path)
    monkeypatch.setattr(ae, "AFFILIATE_LINKS_PATH", tmp_path / "affiliate_links.json")
    monkeypatch.setattr(product_lock, "CONFIG_PATH", tmp_path / "config" / "affiliate_links.json")
    monkeypatch.setattr(ae, "llm_call", lambda prompt, model=None: FAKE_LLM)
    return tmp_path


# ---------- catalog ----------

def test_catalog_is_curated_and_niche_locked():
    cat = ae.list_catalog()
    assert len(cat) == 26
    assert {r["niche"] for r in cat} == set(ae.ALLOWED_NICHES)
    assert all({"product", "niche", "solves"} <= set(r) for r in cat)
    assert len({r["product"] for r in cat}) == 26
    assert ae.list_catalog(["ai"]) == [r for r in cat if r["niche"] == "ai"]
    assert ae.list_catalog(["bogus"]) == cat            # unknown niche ignored
    cat[0]["product"] = "mutated"
    assert ae.list_catalog()[0]["product"] != "mutated"  # copies, not the live rows


def test_pick_products_deterministic_and_avoids_recent(sandbox):
    d = date(2030, 1, 15)
    a = ae.pick_products(3, day=d)
    b = ae.pick_products(3, day=d)
    assert [r["product"] for r in a] == [r["product"] for r in b]
    assert len({r["product"] for r in a}) == 3
    # Save a fake brief for yesterday using the same products -> all rotate out.
    (sandbox / "amazon").mkdir()
    (sandbox / "amazon" / "2030-01-14.json").write_text(
        json.dumps({"ideas": [{"product": r["product"]} for r in a]}), encoding="utf-8")
    c = ae.pick_products(3, day=d)
    assert not ({r["product"] for r in a} & {r["product"] for r in c})



def test_pick_products_raises_on_empty_pool(sandbox, monkeypatch):
    monkeypatch.setattr(ae, "_PRODUCT_CATALOG", [])
    with pytest.raises(ValueError):
        ae.pick_products(3, day=date(2030, 1, 15))


def test_pick_products_falls_back_when_pool_exhausted(sandbox):
    d = date(2030, 2, 1)
    (sandbox / "amazon").mkdir()
    (sandbox / "amazon" / "2030-01-31.json").write_text(
        json.dumps({"ideas": [{"product": r["product"]} for r in ae.list_catalog(["ai"])]}),
        encoding="utf-8")
    got = ae.pick_products(5, day=d, niches=["ai"])
    assert len(got) == 5 and all(r["niche"] == "ai" for r in got)


# ---------- registry ----------

def test_registry_roundtrip_verbatim(sandbox):
    assert ae.load_affiliate_links() == {}
    assert ae.get_affiliate_url("Desk Cable Organizer") == ""
    url = "https://www.amazon.ca/dp/B07MJM4F44?externalReferenceId=abc&plattr=raflink"
    entry = ae.register_affiliate_link("Desk Cable Organizer", url, notes="ca")
    assert entry["url"] == url and entry["added_at"] and entry["notes"] == "ca"
    reg = ae.load_affiliate_links()
    assert reg["Desk Cable Organizer"]["url"] == url
    assert ae.get_affiliate_url("desk cable organizer") == url   # case-insensitive, verbatim URL
    # Replace keeps one key.
    ae.register_affiliate_link("DESK cable organizer", url + "&v=2")
    assert list(ae.load_affiliate_links()) == ["Desk Cable Organizer"]
    assert ae.get_affiliate_url("Desk Cable Organizer") == url + "&v=2"
    assert ae.remove_affiliate_link("desk cable organizer") is True
    assert ae.remove_affiliate_link("desk cable organizer") is False
    assert ae.load_affiliate_links() == {}
    with pytest.raises(ValueError):
        ae.register_affiliate_link("X", "")


# ---------- generate_idea ----------

def test_generate_idea_cta_only_strips_every_url(sandbox):
    row = ae.list_catalog(["content_creation"])[2]
    idea = ae.generate_idea(row)
    assert set(idea) == IDEA_KEYS
    assert idea["cta_only_mode"] is True
    assert idea["cta_only_banner"] == NO_LINK_BANNER
    assert idea["affiliate_url"] == ""
    assert idea["link_intro_timing"] == "skip - CTA only mode (no real link)"
    for k in ("problem_solved", "viral_hook", "script_30s", "content_angle", "cta"):
        assert "http" not in idea[k] and "[link]" not in idea[k]
    assert idea["link_warnings"]
    assert idea["raw_llm_output"] == FAKE_LLM


def test_generate_idea_keeps_only_registered_url(sandbox, monkeypatch):
    real = "https://www.amazon.ca/dp/B07MJM4F44?plattr=raflink"
    monkeypatch.setattr(ae, "llm_call", lambda p, model=None:
                        FAKE_LLM.replace("https://example.com/buy", real))
    idea = ae.generate_idea(ae.list_catalog()[0], affiliate_url=real)
    assert idea["cta_only_mode"] is False and idea["cta_only_banner"] == ""
    assert idea["affiliate_url"] == real
    assert real in idea["script_30s"]
    assert "amzn.to/fake123" not in idea["script_30s"]


def test_generate_idea_falls_back_when_llm_down(sandbox, monkeypatch):
    def boom(prompt, model=None):
        raise ConnectionError("ollama down")
    monkeypatch.setattr(ae, "llm_call", boom)
    idea = ae.generate_idea(ae.list_catalog()[0])
    assert set(idea) == IDEA_KEYS
    assert idea["raw_llm_output"].startswith("FALLBACK:")
    assert idea["viral_hook"] and idea["script_30s"] and idea["cta"]
    assert "http" not in idea["script_30s"]


# ---------- run_daily ----------

def test_run_daily_discovery_mode_writes_json_and_md(sandbox):
    d = date(2000, 1, 1)
    payload = ae.run_daily(count=3, niches=["ai"], day=d)
    assert TOP_KEYS <= set(payload)
    assert payload["lock_state"] == "discovery"
    assert "locked_product" not in payload
    assert payload["count"] == 3 and len(payload["ideas"]) == 3
    assert payload["niches_filter"] == ["ai"]
    assert all(i["niche"] == "ai" for i in payload["ideas"])
    assert payload["any_cta_only_mode"] is True
    assert payload["banner"] == NO_LINK_BANNER
    jp, mp = Path(payload["json_path"]), Path(payload["md_path"])
    assert jp == sandbox / "amazon" / "2000-01-01.json" and jp.exists() and mp.exists()
    on_disk = json.loads(jp.read_text(encoding="utf-8"))
    assert "json_path" not in on_disk and on_disk["ideas"][0].keys() == payload["ideas"][0].keys()
    md = mp.read_text(encoding="utf-8")
    assert md.startswith("# Amazon Daily Picks - 2000-01-01")
    assert f"> **{NO_LINK_BANNER}**" in md and "**Affiliate URL:**" not in md
    assert ae.load_day(d) == on_disk
    assert ae.list_recent(14) == ["2000-01-01"]
    assert ae.load_day(date(1999, 1, 1)) == {}


def test_run_daily_registry_link_attached_and_count_clamped(sandbox, monkeypatch):
    real = "https://www.amazon.ca/dp/B07MJM4F44?plattr=raflink"
    for r in ae.list_catalog():
        ae.register_affiliate_link(r["product"], real)
    payload = ae.run_daily(count=9, day=date(2000, 1, 2))
    assert payload["count"] == 5                          # clamped to the 3-5 spec ceiling
    assert payload["any_cta_only_mode"] is False and payload["banner"] == ""
    assert all(i["affiliate_url"] == real for i in payload["ideas"])
    assert payload["niches_filter"] == list(ae.ALLOWED_NICHES)
    assert "**Affiliate URL:** " + real in Path(payload["md_path"]).read_text(encoding="utf-8")
    # Explicit affiliate_urls override merges over the registry.
    p2 = ae.run_daily(count=1, day=date(2000, 1, 3),
                      affiliate_urls={payload["ideas"][0]["product"].upper(): real + "&o=1"})
    urls = {i["affiliate_url"] for i in p2["ideas"]}
    assert urls <= {real, real + "&o=1"}


def test_run_daily_strict_monetized(sandbox):
    product_lock.CONFIG_PATH.parent.mkdir(parents=True)
    product_lock.CONFIG_PATH.write_text(json.dumps({
        "active_product": "arm",
        "products": {"arm": {"name": "Amazon Rewards Mastercard",
                             "affiliate_link": "https://amzn.to/real?tag=ryah-20",
                             "niche": "business", "solves": "Cashback on Amazon."}},
    }), encoding="utf-8")
    payload = ae.run_daily(count=3, niches=["ai"], day=date(2000, 1, 4))
    assert payload["lock_state"] == "strict_monetized"
    assert payload["locked_product"] == "Amazon Rewards Mastercard"
    assert payload["niches_filter"] == ["business"]           # catalog + niches bypassed
    assert payload["any_cta_only_mode"] is False and payload["banner"] == ""
    assert len(payload["ideas"]) == 3
    for i in payload["ideas"]:
        assert i["product"] == "Amazon Rewards Mastercard"
        assert i["affiliate_url"] == "https://amzn.to/real?tag=ryah-20"
        assert i["cta_only_mode"] is False
    md = Path(payload["md_path"]).read_text(encoding="utf-8")
    assert "> **STRICT LOCK** - all 3 ideas focused on **Amazon Rewards Mastercard**" in md


def test_run_daily_strict_pending_is_cta_only(sandbox):
    product_lock.CONFIG_PATH.parent.mkdir(parents=True)
    product_lock.CONFIG_PATH.write_text(json.dumps({
        "active_product": "arm",
        "products": {"arm": {"name": "Amazon Rewards Mastercard", "affiliate_link": "",
                             "niche": "business", "solves": "Cashback on Amazon."}},
    }), encoding="utf-8")
    payload = ae.run_daily(count=2, day=date(2000, 1, 5))
    assert payload["lock_state"] == "strict_pending"
    assert payload["locked_product"] == "Amazon Rewards Mastercard"
    assert payload["any_cta_only_mode"] is True
    assert all(i["cta_only_mode"] and i["affiliate_url"] == "" for i in payload["ideas"])
    assert "> **STRICT LOCK (pending)**" in Path(payload["md_path"]).read_text(encoding="utf-8")


def test_run_daily_never_crashes_when_llm_down(sandbox, monkeypatch):
    def boom(prompt, model=None):
        raise TimeoutError("ollama timeout")
    monkeypatch.setattr(ae, "llm_call", boom)
    payload = ae.run_daily(count=3, day=date(2000, 1, 6))
    assert len(payload["ideas"]) == 3
    assert all(i["raw_llm_output"].startswith("FALLBACK:") for i in payload["ideas"])
    assert Path(payload["json_path"]).exists()
