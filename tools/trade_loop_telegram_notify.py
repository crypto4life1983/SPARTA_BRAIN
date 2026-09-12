"""Send the trading loop's morning decision queue to Telegram.

Reads reports/trade_learning/LOOP_STATUS.md (written at 01:30 by
tools/trade_loop_digest.py) and sends a short message containing section 5,
"Decisions only a human can take", plus a one-line health summary.

Outbound transport is REUSED from tools/brain_telegram_notify.py — this module
adds no new network code and no new credential path. Read-only over the repo;
the only side effect is one Telegram message to the operator's own chat.

It always sends, even when the queue is empty: a missing morning message is then
a signal that the loop itself did not run.

CLI:
    python tools/trade_loop_telegram_notify.py --dry-run   # print, send nothing
    python tools/trade_loop_telegram_notify.py             # send
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.brain_telegram_notify import send_telegram_message  # noqa: E402  (reuse transport)

STATUS_PATH = _REPO_ROOT / "reports" / "trade_learning" / "LOOP_STATUS.md"
LEDGER_PATH = _REPO_ROOT / "data" / "trade_hypothesis_ledger.json"
SCORECARD_PATH = _REPO_ROOT / "reports" / "trade_learning" / "paper_systems_scorecard.json"
HISTORY_PATH = _REPO_ROOT / "reports" / "trade_learning" / "telegram_notify_history.jsonl"
QUEUE_HEADING = "## 5. Decisions only a human can take"
NOTHING_TODAY = "none today — the loop is accumulating forward evidence"
MAX_QUEUE_ITEMS = 6
MAX_CHARS = 3500  # Telegram hard limit is 4096; leave headroom


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_queue(status_md: str) -> list[str]:
    """Bullets under the 'Decisions only a human can take' heading."""
    out: list[str] = []
    in_section = False
    for line in status_md.splitlines():
        s = line.strip()
        if s.startswith(QUEUE_HEADING):
            in_section = True
            continue
        if in_section and s.startswith("## "):
            break
        if in_section and s.startswith("- "):
            out.append(s[2:].strip())
    return out


def health_line(ledger, scorecard) -> str:
    """One line: how many hypotheses in each state, how many paper lines resolved."""
    parts: list[str] = []
    hyps = (ledger or {}).get("hypotheses", {})
    if hyps:
        counts: dict[str, int] = {}
        for h in hyps.values():
            counts[h.get("status", "?")] = counts.get(h.get("status", "?"), 0) + 1
        parts.append("hypotheses " + ", ".join(f"{n} {s.lower()}" for s, n in sorted(counts.items())))
    recs = scorecard if isinstance(scorecard, list) else (
        (scorecard or {}).get("lines") or (scorecard or {}).get("records") or (scorecard or {}).get("systems"))
    if recs:
        scounts: dict[str, int] = {}
        for r in recs:
            scounts[r.get("status", "?")] = scounts.get(r.get("status", "?"), 0) + 1
        parts.append("paper lines " + ", ".join(f"{n} {s.lower()}" for s, n in sorted(scounts.items())))
    return " | ".join(parts) if parts else "loop artifacts not found"


def build_message(status_md: str, ledger, scorecard, *, now: datetime | None = None) -> str:
    now = now or datetime.now()
    if not status_md.strip():
        return (f"SPARTA trading loop - {now.strftime('%Y-%m-%d %H:%M')}\n\n"
                "LOOP_STATUS.md is missing. The nightly loop did not produce a status page; "
                "check the scheduled tasks.")
    queue = extract_queue(status_md)
    actionable = [q for q in queue if not q.lower().startswith("none today")]
    lines = [f"SPARTA trading loop - {now.strftime('%Y-%m-%d %H:%M')}", ""]
    if actionable:
        lines.append(f"Your decisions ({len(actionable)}):")
        for q in actionable[:MAX_QUEUE_ITEMS]:
            lines.append(f"- {q}")
        if len(actionable) > MAX_QUEUE_ITEMS:
            lines.append(f"- (+{len(actionable) - MAX_QUEUE_ITEMS} more on the page)")
    else:
        lines.append("No decisions for you today. The loop is accumulating forward evidence.")
    lines += ["", health_line(ledger, scorecard), "",
              "Full page: reports/trade_learning/LOOP_STATUS.md",
              "Observation only - nothing was applied or traded."]
    msg = "\n".join(lines)
    return msg if len(msg) <= MAX_CHARS else msg[:MAX_CHARS - 3] + "..."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Telegram the trading loop's morning decision queue")
    ap.add_argument("--dry-run", action="store_true", help="print the message, send nothing")
    ap.add_argument("--status", default=str(STATUS_PATH))
    args = ap.parse_args(argv)

    status_md = read_text(Path(args.status))
    msg = build_message(status_md, read_json(LEDGER_PATH), read_json(SCORECARD_PATH))
    if args.dry_run:
        print(msg)
        return 0
    sent = send_telegram_message(msg)
    print(f"telegram sent: {sent}")
    try:
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "sent": bool(sent),
                "chars": len(msg),
                "queue_items": len([q for q in extract_queue(status_md) if not q.lower().startswith("none today")]),
            }) + "\n")
    except Exception:
        pass
    return 0 if sent else 1


if __name__ == "__main__":
    raise SystemExit(main())
