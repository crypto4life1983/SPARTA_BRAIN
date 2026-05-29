# PLAN — Weekly RS s21 Paper-Cycle Notification + Dashboard Integration

> **PLAN ONLY. Nothing here is built, run, sent, fetched, or wired yet.**
> Scope: design a *safe* notification + dashboard view for the **broker-free** weekly RS s21
> paper process. **DIAGNOSTIC_ONLY · FRC NEVER_GRANTED · Live BLOCKED_AT_6_GATES · Trading PAUSED.**
> No broker, no live trading, no paper-via-broker, no FRC, no Strategy Lab promotion.
> The notification layer is **observe-and-alert only** — it can NEVER start a cycle, fetch data, place an
> order, or send anything except a text status alert the operator explicitly enabled.

Reuses what already exists rather than inventing new transport:
- **Dashboard:** FastAPI `app.py` + Jinja2 `templates/`, mirroring the existing **read-only `/command`** viewer
  (GET-only, localhost-only, no buttons, no execution). Manual row via `db.upsert_manual_entry()` (feeds `/guide`).
- **Telegram transport:** existing `tools/brain_telegram_notify.py` (`send_telegram_message`, `load_telegram_config`,
  `--dry-run`) — already loads token from env/local config, never prints it, fails safe on missing config.
- **Dry-run boundary precedent:** `sparta_commander/notification_channels.py::send_notification` (returns `dry_run`
  unless explicitly enabled) and the `_SECRET_SHAPE` scrub regex in `telegram_adapter.py`.
- **Status source of truth:** harness `manifest.py` (status/thresholds/DATA_SOURCES/weekly anchor),
  `cycle.py` stale-data logic, and `runs/dry_cycle_NNN/` outputs.

---

## 1. Recommended files to CREATE (BUILD phase — not now)

| File | Type | Purpose |
|---|---|---|
| `paper_trading/weekly_rs_s21_forward_paper_harness/status.py` | NEW, read-only | Single read-only aggregator. Reads `manifest.py` + newest `runs/dry_cycle_NNN/` (orders, closed trades, `killswitch_status.json`, weekly report) + active `DATA_SOURCES` last_date. Returns one dict consumed by BOTH the dashboard card and the Telegram notifier. **Never runs a cycle, never fetches, never sends.** Pure functions: `paper_status()`, `is_next_cycle_ready()` → `READY`/`STALE`. |
| `paper_trading/weekly_rs_s21_forward_paper_harness/notify.py` | NEW | Builds alert text from `status.py` + decides which event fired. Sending is **dry-run by default**; real send only via the existing `tools/brain_telegram_notify.send_telegram_message` transport, token from `local_secrets/`/env only. Operator-run (manual or a read-only scheduled *check*); the harness itself never calls it. |
| `paper_trading/weekly_rs_s21_forward_paper_harness/runs/notify_state.json` | NEW, local | Append/track which events were already alerted (anti-spam: don't re-alert the same cycle/anchor). Local only. |
| `local_secrets/weekly_rs_paper_telegram.json` | NEW, **gitignored** | `{ "token": "...", "chat_id": "..." }`. Operator-created, never committed. `local_secrets/` is already gitignored. |
| `tests/test_weekly_rs_s21_paper_notify.py` | NEW | Asserts: dry-run by default; no real send without explicit enable; no secret-shaped string in any message; READY/STALE logic; notifier cannot trigger a cycle; DIAGNOSTIC_ONLY footer present. |

## Files to MODIFY (BUILD phase — not now, minimal surgical)

| File | Change |
|---|---|
| `app.py` | Add ONE read-only `@app.get("/paper")` route (mirror `page_*` pattern) rendering a new template from `status.paper_status()`. **No POST, no button, no cycle trigger.** Add ONE `db.upsert_manual_entry("weekly_rs_s21_paper", ...)` so `/guide` stays true. |
| `templates/weekly_rs_s21_paper.html` (NEW template) | The card markup (read-only). |

**Not touched:** harness mechanic code (`signal.py`/`portfolio.py`/`cycle.py`/`manifest.py`/`killswitch.py`), sealed artifacts, `brain_memory/.../lessons.md`, any broker/live path.

---

## 2. Data source for the dashboard card
All fields come from `status.paper_status()` (read-only), which reads:

| Card field | Source |
|---|---|
| Current paper status | `MANIFEST["status"]` (`paper_state`, `trading_status`, `live_status`, `frc_status`, `research_label`) |
| Last cycle number | highest `runs/dry_cycle_NNN/` index present |
| Last anchor date | `signal_date` in newest `paper_weekly_report_NNN.md` / cycle record |
| Next expected weekly anchor | last anchor + R=5 trading-day cadence (from `locked_mechanic`), computed read-only |
| Latest paper equity | equity line in newest weekly report / `paper_book` snapshot in the run dir |
| Current holdings | latest selection (≤8 names) from newest `paper_orders.jsonl` / report |
| Last cycle verdict | summary/verdict line in newest weekly report |
| Kill-switch status | newest `runs/dry_cycle_NNN/killswitch_status.json` (`status` + `reasons`) |
| Next cycle READY / STALE | `is_next_cycle_ready()`: compares active `DATA_SOURCES[...]["last_date"]` and latest local bar vs last cycle anchor + cadence (same rule as `cycle.StaleDataError`); **READY** only if a new anchor strictly newer than the last cycle exists and data covers it, else **STALE** |
| Reminder banner | static constants: `DIAGNOSTIC_ONLY`, `FRC NEVER_GRANTED`, `Live BLOCKED_AT_6_GATES`, `Trading PAUSED` |

The card is a pure **view** of files the cycle already writes. It computes nothing tradable and triggers nothing.

---

## 3. Telegram message templates (all carry the safety footer; no secrets ever)
Footer on every message: `[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]`

**A. Next weekly anchor READY**
```
SPARTA Weekly RS s21 — Paper
READY: new weekly anchor available ({next_anchor})
Last cycle: #{last_n} @ {last_anchor}
Action: operator may authorize cycle #{next_n} (broker-free dry run). Nothing runs automatically.
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

**B. Stale-data / NO-TRADE halt**
```
SPARTA Weekly RS s21 — Paper
NO-TRADE (STALE): no new anchor newer than {last_anchor}  (or data last bar {last_bar} < required {required})
No cycle created. This is expected behavior, not an error.
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

**C. Cycle completed**
```
SPARTA Weekly RS s21 — Paper
Cycle #{n} complete @ {anchor}
Equity: {equity}  ·  Holdings (≤8): {tickers}
Verdict: {verdict}  ·  Kill-switch: {ks_status}
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

**D. Kill-switch WARN / REVIEW / KILL**
```
SPARTA Weekly RS s21 — Paper
KILL-SWITCH {level}: {reasons}
Cycle #{n} @ {anchor}.  {('HALT — paper test stopped; no auto-resume.' if level=='TRIGGERED' else 'Review required; not auto-halted.')}
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

**E. Data refresh failed**
```
SPARTA Weekly RS s21 — Paper
DATA REFRESH FAILED: {short_reason}
Active source unchanged ({source_key}, last {last_date}). Sealed baseline untouched. No cycle run.
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

**F. Push / commit completed (optional, only if relevant)**
```
SPARTA Weekly RS s21 — Paper
Repo update: {commit_or_push_summary}  (HEAD {short_hash})
[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]
```

All `{...}` are plain status values. The builder runs `_SECRET_SHAPE`-style scrub before send; if any secret-shaped token is detected, the message is blocked, not sent.

---

## 4. Schedule / check logic
The notifier is a **read-only check**, not a runner. Suggested operator flow (manual, or a read-only scheduled *check* that only alerts):

1. `status.paper_status()` reads manifest + newest run dir + active data source (no fetch).
2. Determine fired events vs `notify_state.json` (anti-spam):
   - New anchor available & not yet alerted → **A (READY)**.
   - Check requested but no new anchor / data stale → **B (STALE)** (alert at most once per stale window).
   - New `runs/dry_cycle_NNN/` since last notify → **C (cycle completed)** + read its `killswitch_status.json`.
   - `killswitch_status.json` status ∈ {WARN, REVIEW, TRIGGERED} → **D**.
   - A refresh attempt left a failure marker → **E**.
   - A commit/push just completed (optional hook the operator passes in) → **F**.
3. For each fired event: build text → scrub → (dry-run print) OR send via existing transport if explicitly enabled → record in `notify_state.json`.
4. **The check never creates a cycle, never fetches, never refreshes.** READY just *tells* the operator a cycle is authorizable; running it remains a separate explicit `operator_authorized_dry_run=True` authorization.

Cadence: align to the locked weekly anchor (e.g., a read-only check after the anchor session). Default dry-run; real send only after the operator enables it.

---

## 5. Safety guards (must all hold in BUILD)
- **Read-only dashboard:** GET-only, localhost-only, no button/form, mirrors `/command`. The card cannot start/refresh/stop a cycle.
- **Notifier cannot act:** no broker, no order, no fetch, no cycle trigger, no FRC, no Strategy Lab — it only reads status and emits text.
- **Dry-run by default:** real send requires an explicit enable flag AND a present token; missing token → skip (never crash, never block a cycle).
- **Secrets:** token + chat_id read **only** from `local_secrets/` (gitignored) or environment. **Never printed, never logged, never committed, never placed in message bodies.** `local_secrets/` stays gitignored.
- **Secret-shape scrub:** every outgoing message passes a `_SECRET_SHAPE`-style check; a token-shaped match blocks the send.
- **Harness gate intact:** `run_weekly_paper_cycle` still refuses unless `operator_authorized_dry_run=True`; notifier never sets it.
- **Sealed/immutable:** sealed baseline data and `lessons.md` never touched; mechanic code unmodified.
- **Anti-spam state is local** and contains no secrets.
- **No network on the dashboard path**; the only network call in the whole design is the optional Telegram `sendMessage`, behind the dry-run + token gate.

---

## 6. Exact next authorization (BUILD only)
> **Authorize weekly RS s21 paper-cycle notification + dashboard BUILD only.**
> Build the read-only status aggregator `status.py`, the dry-run-default `notify.py` (+ `notify_state.json`),
> the read-only `/paper` dashboard route + `templates/weekly_rs_s21_paper.html`, one `db.upsert_manual_entry`
> row, and `tests/test_weekly_rs_s21_paper_notify.py`.
> Telegram defaults to **dry-run**; real send only via the existing `tools/brain_telegram_notify` transport
> with token/chat_id read from `local_secrets/` or environment, never printed, never committed; `local_secrets/`
> stays gitignored; no secret in any message body.
> Do NOT send any real Telegram message, do NOT run a cycle, do NOT fetch data, do NOT modify harness mechanic
> code or sealed artifacts or `lessons.md`, do NOT connect a broker, do NOT live trade, do NOT grant FRC, do NOT
> promote to Strategy Lab. Commit only if tests pass and only under a separate commit authorization.

(After BUILD: separate authorizations, each its own turn, for (i) committing, (ii) a one-time **dry-run** notification test that prints templates without sending, and only much later (iii) enabling a real send.)
