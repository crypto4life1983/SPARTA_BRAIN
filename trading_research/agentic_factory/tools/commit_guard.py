"""Strategy Factory commit guard (offline, stdlib-only, read-only).

Purpose
-------
A pre-commit safety check that inspects a set of repo-relative file paths (by
default the git staged set) and BLOCKS the commit when it would include files
that do not belong to the Strategy Factory research-documentation lane:

  * JARVIS workstream files (separate lane, races HEAD on master)
  * runtime snapshots / generated live-state artifacts
  * market data / frozen datasets
  * broker / live / paper-trading / credential / exchange-API files
  * strategy-engine / config / spec changes (allowed ONLY with explicit
    authorization, because they mutate trading logic)

Anything not matched by a deny rule (e.g. report.md / report.json under
``reports/``, the guard itself under ``tools/``) is allowed.

Design notes
------------
* Deny patterns live in the sibling ``commit_guard_rules.json`` (NOT in this
  ``.py``) so the factory's own forbidden-token source scanner
  (``tests/test_safety_guards.py``) never trips on the vendor / credential
  substrings used as match patterns.
* The importable core (:func:`classify_path`, :func:`check_paths`) is pure: it
  performs no I/O beyond loading the rules file and runs no subprocess. Reading
  the git staged set is confined to :func:`_staged_paths`, used only by the CLI.
* No network, no broker, no order placement, no data fetch. Read-only.

The guard *reports*; it does not auto-install, auto-stage, or auto-commit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_RULES_PATH = os.path.join(_THIS_DIR, "commit_guard_rules.json")

# Categories that can be allowed by an explicit authorization flag.
_OVERRIDABLE = "overridable"


def load_rules(rules_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load and compile the deny categories from the JSON rules file."""
    path = rules_path or _RULES_PATH
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    categories = data.get("categories", [])
    for cat in categories:
        cat["_compiled"] = [re.compile(p, re.IGNORECASE) for p in cat.get("patterns", [])]
    return categories


def _normalize(path: str) -> str:
    """Normalize a path to forward slashes, no leading ``./``, lowercased."""
    norm = path.replace("\\", "/").strip()
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.lower()


def classify_path(
    path: str,
    categories: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, str]]:
    """Return the first matching deny category for ``path``, else ``None``.

    The returned dict has ``name``, ``severity`` and ``reason`` keys. A ``None``
    result means the path is allowed (not matched by any deny rule).
    """
    if categories is None:
        categories = load_rules()
    norm = _normalize(path)
    for cat in categories:
        for rx in cat.get("_compiled", []):
            if rx.search(norm):
                return {
                    "name": cat["name"],
                    "severity": cat.get("severity", "hard"),
                    "reason": cat.get("reason", ""),
                }
    return None


def check_paths(
    paths: List[str],
    *,
    allow_strategy: bool = False,
    categories: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Classify every path and decide whether the commit is allowed.

    ``allow_strategy`` only relaxes the single ``overridable`` category
    (strategy-logic changes). Hard categories (JARVIS, data, runtime snapshot,
    broker/live/paper/credential) can NEVER be overridden.
    """
    if categories is None:
        categories = load_rules()

    blocked: List[Dict[str, str]] = []
    overridden: List[Dict[str, str]] = []
    allowed: List[Dict[str, str]] = []

    for path in paths:
        hit = classify_path(path, categories)
        if hit is None:
            allowed.append({"path": path, "category": "factory_doc"})
            continue
        if hit["severity"] == _OVERRIDABLE and allow_strategy:
            overridden.append({"path": path, "category": hit["name"], "reason": hit["reason"]})
            continue
        blocked.append(
            {"path": path, "category": hit["name"], "severity": hit["severity"], "reason": hit["reason"]}
        )

    return {
        "ok": len(blocked) == 0,
        "checked": len(paths),
        "allow_strategy": bool(allow_strategy),
        "blocked": blocked,
        "overridden": overridden,
        "allowed": allowed,
    }


def _staged_paths() -> List[str]:
    """Return the git staged set (CLI use only). Local, read-only git call."""
    import subprocess  # local import: keep the importable core subprocess-free

    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _format_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    verdict = "PASS" if result["ok"] else "BLOCKED"
    lines.append(f"commit-guard: {verdict} (checked {result['checked']} path(s))")
    if result["blocked"]:
        lines.append("  BLOCKED:")
        for b in result["blocked"]:
            lines.append(f"    - [{b['category']}] {b['path']} :: {b['reason']}")
    if result["overridden"]:
        lines.append("  ALLOWED BY OVERRIDE (--allow-strategy):")
        for o in result["overridden"]:
            lines.append(f"    - [{o['category']}] {o['path']}")
    if result["allowed"]:
        lines.append(f"  ALLOWED: {len(result['allowed'])} factory-doc path(s)")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strategy Factory commit guard: block cross-lane / data / "
        "broker / strategy files from a factory commit.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Repo-relative paths to check. If omitted, the git staged set is used.",
    )
    parser.add_argument(
        "--allow-strategy",
        action="store_true",
        help="Authorize strategy-logic (engine/config/spec) changes for this commit.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    paths = args.paths if args.paths else _staged_paths()
    result = check_paths(paths, allow_strategy=args.allow_strategy)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_report(result))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
