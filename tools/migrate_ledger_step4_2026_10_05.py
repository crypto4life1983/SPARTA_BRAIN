"""One-off migration: spec step 4 of spec_killswitch_and_ledger_baseline_2026-09-21.md.

Re-dates the four APPLIED hypothesis records from 2026-09-11 to 2026-09-15 (the
partial-bar fix) and voids their baselines, which were frozen from retired
pre-fix evidence. The absolute rollback rule (mean R < 0.0 at n >= 20,
pre-registered 2026-09-21 and already implemented in trade_hypothesis_ledger.py)
takes over. Observation-only: touches data/trade_hypothesis_ledger.json and
nothing else. Idempotent: a record already dated 2026-09-15 is skipped.

Run:  .venv\\Scripts\\python tools\\migrate_ledger_step4_2026_10_05.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "data" / "trade_hypothesis_ledger.json"
IDS = ("block_long_in_TREND_DOWN", "enforce_hard_stop",
       "partial_tp_or_trail_2R", "review_pause_D2")
OLD_DATE = "2026-09-11"
NEW_DATE = "2026-09-15"
SPEC = "reports/trade_learning/spec_killswitch_and_ledger_baseline_2026-09-21.md"
RULE = "mean R < 0.0R at n >= 20 (absolute, pre-registered 2026-09-21)"


def migrate(ledger: dict, today: str, sha_before: str, backup: str) -> list[str]:
    changed: list[str] = []
    for sid in IDS:
        hyp = ledger["hypotheses"][sid]
        ap = hyp["applied"]
        if hyp["status"] != "APPLIED":
            raise SystemExit(f"{sid}: status {hyp['status']}, expected APPLIED")
        if ap.get("applied_as_of") == NEW_DATE:
            continue  # already migrated
        if ap.get("applied_as_of") != OLD_DATE:
            raise SystemExit(f"{sid}: applied_as_of {ap.get('applied_as_of')!r}, expected {OLD_DATE}")
        old_base, old_n = ap.get("baseline_mean_R"), ap.get("baseline_n")
        ap["applied_as_of"] = NEW_DATE
        ap["baseline_mean_R"] = None
        ap["baseline_n"] = 0
        ap["baseline_status"] = "NOT_EVALUABLE_RETIRED_EVIDENCE"
        ap["baseline_is_retired_evidence"] = False
        ap["p_after_ge_baseline"] = None
        ap["rollback_rule"] = RULE
        ap["voided_baseline"] = {
            "baseline_mean_R": old_base, "baseline_n": old_n,
            "applied_as_of": OLD_DATE, "voided_as_of": today,
            "reason": "frozen from pre-2026-09-15 partial-bar evidence (retired)",
        }
        hyp["history"].append({
            "as_of": today, "status": "APPLIED",
            "note": (f"spec step 4 migration (operator-approved {today}): applied_as_of "
                     f"re-dated {OLD_DATE} -> {NEW_DATE} (partial-bar fix); retired baseline "
                     f"{old_base} (n={old_n}) voided; rollback judged by the absolute rule "
                     f"{RULE} per {SPEC}; backup {backup}; sha_before {sha_before}"),
        })
        changed.append(sid)
    if changed:
        ledger["last_updated_as_of"] = today
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raw = LEDGER.read_bytes()
    sha_before = hashlib.sha256(raw).hexdigest()[:16]
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup = LEDGER.with_name(f"trade_hypothesis_ledger.pre_step4_migration_{stamp}.json")
    ledger = json.loads(raw.decode("utf-8"))
    today = datetime.now().strftime("%Y-%m-%d")
    changed = migrate(ledger, today, sha_before, backup.name)
    print(f"sha_before={sha_before} changed={changed}")
    if args.dry_run or not changed:
        print("nothing written" if not changed else "dry run: nothing written")
        return 0
    shutil.copyfile(LEDGER, backup)
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"backup={backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
