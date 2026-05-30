"""Generate a cached JARVIS route smoke report (manual, offline).

Probes a small set of important LOCAL GET routes ONCE, captures only the HTTP
status / timing / size, and writes a summary to
storage/jarvis/route_smoke_report.json. The web app only ever READS that file —
it never probes routes itself. Run this by hand (or from a trusted scheduler)
against a locally running SPARTA server whenever you want the /jarvis console to
show fresh route status:

    python tools/jarvis_route_smoke_report.py
    python tools/jarvis_route_smoke_report.py --base-url http://127.0.0.1:8765 --timeout 5

Exit code is 0 only if every REQUIRED route responds OK; nonzero otherwise.
GET-only. Standard library only (urllib). No credentials, no session headers,
no environment dumps, and no response bodies are ever written — only path, url,
status_code, ok, duration, and content length.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "storage" / "jarvis"
REPORT_PATH = REPORT_DIR / "route_smoke_report.json"

DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_TIMEOUT = 5.0

# Routes probed. `required` ones gate the exit code / overall verdict; the rest
# are reported for visibility but never fail the run if they are absent.
ROUTES = [
    {"path": "/", "required": True},
    {"path": "/jarvis", "required": True},
    {"path": "/api/jarvis/status", "required": True},
    {"path": "/settings", "required": False},
    {"path": "/performance", "required": False},
    {"path": "/learning", "required": False},
    {"path": "/safety", "required": False},
    {"path": "/money-spartan", "required": False},
    {"path": "/hydra", "required": False},
    {"path": "/victory", "required": False},
]


def _probe(base_url: str, path: str, timeout: float) -> dict:
    """GET a single route and capture status/timing/size only. Never raises."""
    url = base_url.rstrip("/") + path
    started = time.monotonic()
    result: dict = {"path": path, "url": url}
    # Explicit GET; no credentials, no session headers, default redirect policy.
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()  # read to measure size; body is NEVER stored
            result["status_code"] = resp.status
            result["ok"] = 200 <= resp.status < 400
            cl = resp.headers.get("Content-Length")
            result["content_length"] = int(cl) if cl and cl.isdigit() else len(body)
            result["error"] = None
    except urllib.error.HTTPError as exc:
        # The server answered with a 4xx/5xx — a real status, not a transport fail.
        result["status_code"] = exc.code
        result["ok"] = False
        result["content_length"] = None
        result["error"] = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 — transport/timeout: fail-closed
        result["status_code"] = None
        result["ok"] = False
        result["content_length"] = None
        result["error"] = f"{type(exc).__name__}: {exc}"
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def build_report(base_url: str, timeout: float) -> dict:
    """Probe every route and assemble the inert summary. Pure of file I/O."""
    routes = [{**_probe(base_url, r["path"], timeout), "required": r["required"]}
              for r in ROUTES]
    passed = sum(1 for r in routes if r["ok"])
    failed = sum(1 for r in routes if not r["ok"])
    required_ok = all(r["ok"] for r in routes if r["required"])
    return {
        "state": "ready",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "overall": "pass" if required_ok else "fail",
        "counts": {"total": len(routes), "pass": passed, "fail": failed},
        "routes": routes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS cached route smoke report")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    report = build_report(args.base_url, args.timeout)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[jarvis_route_smoke_report] overall={report['overall']} "
          f"({report['counts']['pass']}/{report['counts']['total']} ok) -> {REPORT_PATH}")
    for r in report["routes"]:
        flag = "ok" if r["ok"] else "FAIL"
        sc = r["status_code"] if r["status_code"] is not None else "-"
        req = " [required]" if r["required"] else ""
        print(f"  - {r['path']}: {flag} (status {sc}){req}")
    return 0 if report["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
