# Spec — daily kill-switch ordering + hypothesis-ledger baseline

Status: **PARTIALLY APPLIED 2026-09-21** (operator: "approved", to the recommendation at the
bottom of this document).

| part | state |
|---|---|
| Item 1 — kill-switch re-evaluation | **APPLIED** in `obsidian-trade-logger/scripts/trade_bot.py` + `tests/test_kill_switch_same_run_2026_09_21.py` (8 tests) |
| Item 2 steps 1–3 — ledger baseline logic | **APPLIED** in `tools/trade_hypothesis_ledger.py` |
| Item 2 step 5 — rendering | **APPLIED** in `trade_hypothesis_ledger.py` + `trade_loop_digest.py` |
| Item 2 step 4 — re-dating the four existing records | **NOT APPLIED — still pending a separate operator decision** |

Because step 4 is pending, the four rules applied 2026-09-11 **still carry their retired
baseline of 0.2508 and are still scored against it**. The code change corrects the machinery
for any future apply; it does not retroactively fix those four. LOOP_STATUS section 2 now
prints `vs ⚠RETIRED base 0.251` and a standing warning naming this document, so the pending
decision is visible every morning rather than buried here.

Author: SPARTA session 2026-09-21.

Two independent items. **Item 1 changes the paper bot's risk control** (external project
`obsidian-trade-logger`) and needs explicit authorization. **Item 2 changes only SPARTA-side
loop bookkeeping** (`tools/trade_hypothesis_ledger.py`) and touches no bot code.

Neither item adds broker code, order code, credentials or live trading. The bot stays
paper-only; live remains BLOCKED at 6 gates regardless of either outcome.

---

## Item 1 — the daily kill switch is read once per run, so same-run losses cannot block entries

### The defect

`scripts/trade_bot.py` evaluates the kill switch **once**, near the top of `main()`:

```python
# ~L1433
kill_switch_blocked = False
if kill_switch:
    from scripts.risk_gates import daily_kill_switch_active
    kill_switch_blocked, ks_reason = daily_kill_switch_active(conn, today)
```

and then passes that **boolean** into every `run_strategy(...)` call in the
per-exchange / per-strategy loop (~L1508). Inside `run_strategy` it is consulted per
signal at ~L1142:

```python
if kill_switch_blocked:
    _gate_log(strategy, sig["direction"], sym, "KILL_SWITCH", "daily kill switch active")
    continue
```

`daily_kill_switch_active()` reads `SELECT pnl_r, outcome FROM trades WHERE close_date = ?`.
Exits are written **later in the same pass** — inside `run_strategy`, in the `if open_pos:`
branch. So a loss that closes during iteration *k* of the loop cannot be seen by the
snapshot taken before iteration 0, and iterations *k+1…n* still open new entries.

### Evidence (2026-09-19, from `logs/live_signals.log`)

```
00:05:02  daily kill switch idle: no closed trades today
00:05:19  STOP-FILL binance Exp F  BCHUSDT ... CLOSED LOSS -40.72
00:05:19  STOP-FILL binance Exp F2 ADAUSDT ... CLOSED LOSS -20.33   -> day now -2.03R
00:05:22  kraken Exp D:  OPENED SOLUSDT long
00:05:22  kraken Exp F:  OPENED ARBUSDT long
00:05:22  kraken Exp F2: OPENED BTCUSDT long
01:00:01  daily kill switch ACTIVE: daily P&L -2.03R <= -2.0R   <- one run too late
```

The configured daily loss limit is −2.0R. The day breached it at 00:05:19 and the bot
opened **three** positions 3 seconds later. All three are still open. The switch only
reported ACTIVE on the next run, 55 minutes later.

This is not a wiring bug — the entry path genuinely honours the flag, and the earlier
`[KILL_SWITCH] ... blocked` lines from 2026-08-21 prove it blocks correctly when the flag
is set. It is purely an evaluation-ordering defect.

### Why the minimal fix is sufficient

`run_strategy` **returns** from the `if open_pos:` branch (`return f"Exp {strategy}: {ev...}"`,
~L1099) before ever reaching the entry scan. A single `run_strategy` call therefore either
manages an exit **or** scans for entries — never both. Re-evaluating the switch immediately
before each call closes the gap completely; no change to `run_strategy` itself is required.

### Proposed change

File: `obsidian-trade-logger/scripts/trade_bot.py`, `main()` only.

1. Delete the one-shot evaluation at ~L1433–L1441. Keep `ks_reason` reporting behaviour.
2. Immediately before each `run_strategy(...)` call in the exchange/strategy loop (~L1508),
   re-evaluate:

```python
if kill_switch:
    kill_switch_blocked, ks_reason = daily_kill_switch_active(conn, today)
    if kill_switch_blocked and not _ks_logged:
        summary_lines.append(f"🛑 KILL SWITCH ACTIVE — {ks_reason} (no new entries today)")
        logging.warning(f"daily kill switch ACTIVE: {ks_reason}")
        _ks_logged = True
```

3. `_ks_logged` is a local bool initialised `False` before the loop, so the summary line and
   the WARNING appear **once per run** exactly as today — no log-format change (analytics
   parse these lines). Log the `idle` line once before the loop as now.
4. Import `daily_kill_switch_active` once at the top of the loop scope rather than per call.

### Explicitly out of scope

- No change to `scripts/risk_gates.py` — the thresholds (`DAILY_LOSS_R_LIMIT`,
  `DAILY_LOSS_COUNT_LIMIT`) and the query stay exactly as they are.
- No change to `run_strategy`'s signature or to the exit-management branch.
- No change to what the switch *does* once active.

### Cost

One extra `SELECT` per strategy/exchange iteration against a local SQLite file — roughly
14 extra reads per run against a table of 50 rows. Negligible.

### Tests (add to `tests/`, repo convention `test_rule_changes_*.py`)

1. Losses closing in iteration *k* block entries in iteration *k+1* — the regression this
   fixes. Build a conn where a strategy closes past the limit, assert a later
   `run_strategy` records a `KILL_SWITCH` block instead of opening.
2. A clean day still opens normally (no false positive).
3. The ACTIVE summary line and WARNING appear **exactly once** per run even though the
   switch is now evaluated many times.
4. `daily_kill_switch_active` itself is unchanged — assert its existing tests still pass.
5. Exit management is unaffected when the switch is active (open trades still managed).

### Verification after applying

- Full bot suite green (`python -m pytest tests -q -p no:cacheprovider`).
- One dry run with the scheduled flags: confirm the `idle`/`ACTIVE` lines appear once and
  the `EXIT-CHECK` / `STOP-FILL` formats are byte-identical to today's.
- Next day a loss closes: confirm a `[KILL_SWITCH] ... blocked` line appears in the **same**
  run, not the following one.

### Rollback

Single-file, single-function change; revert the commit. No data migration, no state.

### Risk

Low, and it fails in the safe direction: the switch can now only block **more**, never less.
The one behavioural change is that a day breaching the limit stops trading immediately
instead of at the next run. Note this will **reduce** entry count on losing days, which
slightly slows evidence accrual — see the interaction note at the bottom.

---

## Item 2 — the applied-rule rollback check is scored against a retired baseline

### The defect

`tools/trade_hypothesis_ledger.py` `mark_applied()` freezes:

```python
before = [ ... trades closed on/before as_of ... ]
"baseline_mean_R": _r(sum(before) / len(before))
```

For all four APPLIED rules the stored values are:

| field | value |
|---|---|
| `applied_as_of` | 2026-09-11 |
| `baseline_n` | 31 |
| `baseline_mean_R` | **0.2508** |
| `n_after` | 2 |
| `mean_R_after` | −1.017 |
| `regression_flag` | False (only because `n_after < APPLIED_MIN_N = 20`) |

The apply date is **2026-09-11**, four days before the **2026-09-15 partial-bar fix**.
Every one of those 31 baseline signals is therefore pre-fix — the record the operator
retired from evidence on 2026-09-19. `_update_applied()` then scores valid post-fix
evidence against it:

```python
ap["regression_flag"] = bool(
    len(after) >= APPLIED_MIN_N and (sum(after)/len(after)) < float(base) - APPLIED_REGRESSION_R
)
```

### Why this has a deadline

At `n_after >= 20` the flag fires automatically if post-fix mean R < `0.2508 − 0.2 = **+0.0508**`.
That threshold was derived from a bot reading stale candles, whose apparent edge came from
**2 WINs against 17 profitable TIMEOUTs**. If the pre-fix record was inflated — which is
precisely why it was retired — then *any* honest post-fix result will read as a
"regression", and the loop will recommend rolling back four rules on evidence that says
nothing about them. The check produces a decision, so a wrong baseline produces a wrong
decision, silently and on schedule.

There is no rush in trading terms (n_after = 2, ~1.5 days/entry-day, so weeks away), but
the fix must land **before** n reaches 20, because after that the flag has already fired
and any change looks like moving the goalposts.

### One piece of good luck

No trade closed between 2026-09-11 (apply) and 2026-09-15 (fix) — verified against
`trades.db`. The only closes on/after the apply date are 2026-09-11 (XRPUSDT, pre-fix open)
and two on 2026-09-19, both post-fix. So the post-apply window and the post-fix window
currently **coincide**; there is no contaminated middle zone to untangle. That will stop
being true the moment a pre-fix-opened trade closes, so this is the cheapest it will ever be.

### Options

**A. Re-freeze the baseline from post-fix trades only.** Honest, but `n = 2` today. A
baseline of 2 is not a baseline, and waiting for 20 post-fix trades *then* needing 20 more
to judge against it doubles an already long wait. **Not recommended.**

**B. Void the baseline, re-date the apply to the fix date, pre-register an absolute
rollback rule.** *(Recommended.)* The relative comparison is unsalvageable, so stop making
it, and replace it with a threshold that can be pre-registered *now*, before the data
exists — which is what preserves falsifiability.

**C. Leave it and reinterpret at n=20.** Rejected: that is a post-hoc decision made after
seeing the number, which is exactly the failure mode the pre-registration discipline exists
to prevent.

### Proposed change (Option B)

SPARTA-side only. File: `tools/trade_hypothesis_ledger.py`.

1. Add a module constant with provenance, mirroring `EVIDENCE_VALID_FROM` in
   `trade_journal_learning_report.py`:
   ```python
   EVIDENCE_VALID_FROM = "2026-09-15"   # partial-bar fix; see the learning report
   ROLLBACK_ABS_MEAN_R = 0.0            # pre-registered 2026-09-21, before the data existed
   ```
2. In `mark_applied()`, compute the baseline from post-`EVIDENCE_VALID_FROM` closes only.
   When fewer than `APPLIED_MIN_N` such closes exist, store
   `baseline_mean_R = None` and `baseline_status = "NOT_EVALUABLE_RETIRED_EVIDENCE"` with
   the reason string, instead of a number.
3. In `_update_applied()`, when `baseline_mean_R is None`, judge against the absolute rule
   instead: at `n_after >= APPLIED_MIN_N`, `regression_flag = mean_R_after < ROLLBACK_ABS_MEAN_R`.
   `p_after_ge_baseline` stays `None` (the existing `if after and base is not None` guard
   already handles this — no crash today, it simply skips).
4. Re-date the four existing APPLIED entries from `2026-09-11` to `2026-09-15` and null
   their baselines, appending a `history` entry recording why. **This is a one-off data
   migration of `data/trade_hypothesis_ledger.json` and must be operator-approved
   separately from the code change** — it rewrites a pre-registered record.
5. Render `baseline_status` in `hypothesis_ledger.md` and in LOOP_STATUS section 2, so the
   table stops printing `vs base 0.251` as if it meant something.

### Pre-registration statement (to lock before any data accrues)

> The four rules applied on 2026-09-11 are re-dated to 2026-09-15, the partial-bar fix, and
> judged only on paper signals closing strictly after that date. Their pre-fix baseline is
> void. At n >= 20 post-fix deduplicated signals: **rollback is recommended if mean R < 0.0**;
> the rules are **not** declared working by this rule — a positive mean only means no
> rollback. Nothing is applied or reverted automatically; the loop emits a recommendation
> and the operator decides. This threshold is fixed on 2026-09-21, before the evidence
> exists, and is not to be revised after seeing it.

### Tests

1. `mark_applied` with only pre-fix closes → `baseline_mean_R is None`,
   `baseline_status == "NOT_EVALUABLE_RETIRED_EVIDENCE"`.
2. `mark_applied` with >= 20 post-fix closes → numeric baseline, existing behaviour intact.
3. `_update_applied` with a null baseline and `n_after >= 20`, `mean_R_after < 0` → flag True.
4. Same with `mean_R_after > 0` → flag False, and **not** silently "confirmed".
5. `n_after < 20` never flags regardless of sign.
6. An existing ledger JSON with a numeric baseline still loads and scores as before
   (backwards compatible).
7. `forbidden_words_found()` clean on the rendered markdown.

### Verification

- `tests/test_trade_hypothesis_ledger.py` + `_applied.py` green.
- Regenerate the ledger and LOOP_STATUS; section 2 shows the null baseline and the absolute
  rule rather than `vs base 0.251`.
- Diff `data/trade_hypothesis_ledger.json` and confirm only the four `applied` blocks and
  their `history` changed.

### Risk

None to trading — the ledger has no broker, no order path, never writes to the journal and
never changes the bot. The real risk is **governance**: step 4 rewrites a pre-registered
record. It is defensible only because the record is being corrected to *exclude* retired
evidence, the correction is logged in `history`, and the replacement threshold is fixed
before the data exists. If that reasoning does not satisfy you, take Option A and accept
the longer wait.

---

## Interaction between the two items

Item 1 will slightly **slow** evidence accrual: days that breach −2.0R will stop opening
entries where today they keep going. That is the correct behaviour and worth the cost, but
note it pushes the n=20 read further out, which makes landing Item 2 before that point
easier, not harder.

Neither item changes any strategy rule, parameter, threshold, gate or the symbol universe —
so **neither voids the 2026-09-16 universe-breadth pre-registration**, whose decision rule
is read on 2026-10-16. That pre-registration explicitly voids itself on
"any rule/parameter/gate change inside the window"; a risk-control ordering repair and a
bookkeeping correction are neither.

## Recommendation

Approve **Item 1** now — it is a genuine risk-control defect, the fix is small, contained and
fails safe. Approve **Item 2 steps 1–3 and 5** (the code change) now, and decide step 4
(the one-off re-dating of the four existing records) separately, since that one rewrites a
pre-registered artifact.
