"""tools/trade_loop_page.py — payload for the dashboard's /trade-loop page.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Collects the learning loop's markdown reports under reports/trade_learning and renders each
with tools/markdown_lite. Fail-closed per section: a missing or unreadable file becomes a
"not generated yet" note, never an exception out of the page.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools import markdown_lite

_REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
BANNER = "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER"

# (key, title, relative path). Order = page order.
SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("status", "Loop status (nightly digest)", "LOOP_STATUS.md"),
    ("ledger", "Hypothesis ledger (forward scores + replay priors)", "hypothesis_ledger.md"),
    ("calibration", "Calibration of the loop itself", "ledger_calibration.md"),
    ("loss_diagnosis", "Why the book is losing and what was applied (2026-10-26)", "loss_diagnosis_2026-10-26.md"),
    ("priors", "Replay priors per hypothesis", "replay_priors.md"),
    ("exit_pairs", "Paired exit experiment (D/F/F2)", "exit_pairs.md"),
    ("rule_search", "Rule search (multiple-testing corrected)", "rule_search.md"),
    ("replay_variants", "Replay study: rules + 4 variants (2026-10-20)", "replay_rules_variants_2026-10-20.md"),
    ("replay_portfolio", "Replay study: portfolio-level rules (2026-10-20)", "replay_portfolio_rules_2026-10-20.md"),
    ("replay_bounce", "Replay study: support-bounce entries the bot does not take (2026-10-21)", "replay_bounce_2026-10-21.md"),
    ("rollback_spec", "Pre-registered rollback procedure (2026-10-18)", "spec_rollback_procedure_2026-10-18.md"),
    ("slots_spec", "Spec: paper slots per strategy (2026-10-20)", "spec_paper_slots_2026-10-20.md"),
)


def load_payload(report_dir: Path | None = None, max_chars: int = 120_000) -> dict[str, Any]:
    rd = report_dir or REPORT_DIR
    sections, errors = [], []
    for key, title, rel in SECTIONS:
        p = rd / rel
        item: dict[str, Any] = {"key": key, "title": title, "path": f"reports/trade_learning/{rel}",
                                "mtime": None, "html": "", "note": "file absent"}
        try:
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="replace")
                if len(text) > max_chars:
                    text = text[:max_chars] + "\n\n_truncated for the page_\n"
                item["html"] = markdown_lite.render(text)
                item["mtime"] = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                item["note"] = ""
        except Exception as exc:  # noqa: BLE001 - fail-closed per section
            item["html"] = ""
            item["note"] = f"{type(exc).__name__}: {exc}"
            errors.append(f"{rel}: {type(exc).__name__}: {exc}")
        sections.append(item)
    return {"status": "OK" if not errors else "PARTIAL", "banner": BANNER,
            "generated_at": datetime.now(timezone.utc).isoformat(), "sections": sections, "errors": errors}
