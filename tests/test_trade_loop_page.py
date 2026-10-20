"""tools/trade_loop_page.py payload: every section fails closed, rendered html is escaped."""
import sys

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools import trade_loop_page as tlp  # noqa: E402


def test_missing_files_become_notes_not_errors(tmp_path):
    p = tlp.load_payload(tmp_path)
    assert p["status"] == "OK" and p["errors"] == []
    assert len(p["sections"]) == len(tlp.SECTIONS)
    assert all(s["html"] == "" and s["note"] == "file absent" for s in p["sections"])
    assert p["banner"].startswith("READ ONLY")


def test_present_file_is_rendered_and_truncated(tmp_path):
    (tmp_path / "LOOP_STATUS.md").write_text("# Loop\n\n| a | b |\n|---|---|\n| 1 | 2 |\n<b>x</b>", encoding="utf-8")
    p = tlp.load_payload(tmp_path, max_chars=20)
    s = next(x for x in p["sections"] if x["key"] == "status")
    assert "<h1>Loop</h1>" in s["html"] and s["mtime"] and s["note"] == ""
    assert "truncated for the page" in s["html"]
    (tmp_path / "LOOP_STATUS.md").write_text("<script>alert(1)</script>", encoding="utf-8")
    s = next(x for x in tlp.load_payload(tmp_path)["sections"] if x["key"] == "status")
    assert "<script>" not in s["html"] and "&lt;script&gt;" in s["html"]


def test_route_renders_read_only_and_has_no_controls():
    import pytest
    pytest.importorskip("fastapi")
    import app as app_module
    from fastapi.testclient import TestClient
    r = TestClient(app_module.app).get("/trade-loop")
    assert r.status_code == 200
    assert "READ ONLY" in r.text and "Trade Loop" in r.text
    low = r.text.lower()
    assert "<form" not in low and "hx-post" not in low


def test_section_order_matches_the_page_contract(tmp_path):
    keys = [k for k, _, _ in tlp.SECTIONS]
    assert keys[:3] == ["status", "ledger", "calibration"]
    assert [s["key"] for s in tlp.load_payload(tmp_path)["sections"]] == keys
