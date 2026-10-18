# Spec — per-rule rollback procedure for the five APPLIED ledger rules

Status: **RECORDED 2026-10-18** (operator: "ok yes sure do that", to suggestion 2 of the
2026-10-18 morning review). SPARTA-side bookkeeping only. Touches no bot code, no broker,
no order path, no credentials. Nothing here changes what the paper bot does.

Author: SPARTA session 2026-10-18.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

## Disclosure: when this was written

This procedure is written with the post-fix sample at **n = 12 closes, sum -6.63R, mean
-0.55R** already known. The trigger below is therefore **not** changed: it stays exactly as
pre-registered on 2026-09-21 (`ROLLBACK_ABS_MEAN_R = 0.0` at `APPLIED_MIN_N = 20`). What this
document adds is the *response* to that trigger, decided per rule before the twentieth close
exists, so that the decision is not made under the pressure of a drawdown and not made as
one joint revert of five unrelated rules.

The next eight closes would need to average about +0.83R for the trigger not to fire. That
is unlikely. This document is the plan for the likely case.

## The problem with one trigger for five rules

All five APPLIED rules carry the same rollback line, `mean R < 0.0R at n >= 20 (absolute)`,
because none of them has an admissible baseline (the pre-2026-09-15 evidence is retired, and
the post-fix sample is below 20). That line answers one question only: *is the system as a
whole losing on admissible evidence?* It says nothing about any single rule, and the five
rules are of three different kinds:

| rule | kind | what the mean-R trigger can tell about it |
|---|---|---|
| `enforce_hard_stop` | risk control (loss cap -1.5R) | nothing: a cap cannot make the mean negative; it bounds the tail |
| `block_long_in_TREND_DOWN` | entry block | nothing: blocked trades are not in the sample at all |
| `review_pause_D2` | entry block (strategy quarantine) | nothing: same |
| `partial_tp_or_trail_2R` | exit rule, **superseded 2026-10-14**, not live anywhere | nothing to roll back |
| `partial_tp_or_trail_1R` | exit rule, live since 2026-10-14 | only through its own counterfactual delta_R |

Reverting all five because the system's mean is negative would revert a working loss cap and
two blocks whose own evidence points the other way. That is the failure this document prevents.

## What happens when the trigger fires

1. The ledger sets `regression_flag = true` on every APPLIED rule (unchanged machinery). The
   digest prints it. **Nothing is reverted automatically; the loop applies nothing.**
2. The operator reviews **each rule on its own verdict rule below**, in the order listed.
3. Every verdict is written to the rule's `history` with the numbers it rested on. A rule whose
   own evidence is still below its n is **kept** (status quo), not reverted, and re-reviewed at
   the next 10 closes.

## Per-rule verdict rules (decided 2026-10-18)

### 1. `enforce_hard_stop` — KEEP unless its own counterfactual says otherwise

- Evidence it is doing its job (as of 2026-10-18): every one of the 7 post-fix losses closed
  between -1.01R and -1.11R; zero breaches of the -1.5R cap. Before the fix, 7 breaches cost
  6.06R of excess loss (frozen in-sample evidence).
- **Rollback only if** both hold at n >= 20 post-fix stop-outs: (a) a hindsight re-run of the
  stopped trades to their original exit (same method as `tools/trade_timeout_hindsight.py`,
  no cap) shows sum delta_R > 0 with bootstrap p_positive >= 0.9, **and** (b) a cap breach has
  actually been needed, i.e. the realized loss would have exceeded -1.5R without the cap in at
  least one of those trades. Absent (b) the cap is inert and there is nothing to roll back.
- A bug (any post-fix close below -1.5R with the cap on) is a **fix**, not a rollback.

### 2. `block_long_in_TREND_DOWN` — KEEP until its unblock twin is CONFIRMED

- Its exact counterfactual is already registered: `unblock__TREND_DOWN_BLOCKS_LONG` (SHADOW,
  forward n = 0 as of 2026-10-18) scores the trades this block refused, from
  `reports/observation_mode/missed_opportunity_outcomes.jsonl` (`counted_reason =
  TREND_DOWN_BLOCKS_LONG`).
- **Rollback only if** that twin reaches CONFIRMED on its own pre-registered bar (n >= 20
  forward resolved blocks, p_positive >= 0.9). REJECTED on the twin means the block stays
  indefinitely. Anything else: keep, re-review at the next 10 closes.

### 3. `review_pause_D2` — KEEP; its counterfactual is not yet resolvable

- D2 entries are refused by the allocation quarantine, not by a regime gate, so they do not
  appear in `missed_opportunity_outcomes.jsonl` (checked 2026-10-18: no D2 rows). They exist
  only as `[ALLOCATION COUNTERFACTUAL] ... D2 ... would have opened at` lines in the bot log.
- **Rollback only if** those lines are resolved the same way the missed-opportunity resolver
  resolves regime blocks (hyp stop and target from the logged entry and ATR, 20-day horizon)
  and the resolved set shows mean hyp R > 0 with p_positive >= 0.9 at n >= 20. Building that
  resolver is a separate, later task (see next_actions 2026-10-18); until it exists the
  verdict is KEEP and no number is invented in its place.
- The frozen in-sample reason for the pause stands on record: D2 avg -0.839R over 11 trades.

### 4. `partial_tp_or_trail_2R` — NOT APPLICABLE

- Superseded 2026-10-14 for every manage_de strategy (bot 63ecd30, 26ef50d). There is no
  live 2R trigger to roll back. The record stays APPLIED for history; the verdict is written
  as `N/A — superseded`.

### 5. `partial_tp_or_trail_1R` — judged on its own delta_R, not on mean R

- Its counterfactual is the ledger's own forward score for the rule: per closed signal after
  2026-10-14 with an excursion row, delta_R = (0.5 x 1R + 0.5 x max(R, 0)) - R(realized) when
  max_favorable_R >= 1, else 0. Note the ledger's `n_after` for this rule counts closes after
  **2026-10-14**, not after 2026-09-15, so at the system-wide n = 20 it will typically have
  fewer than 20 of its own.
- **Rollback only if** at n >= 20 closes after 2026-10-14 the forward delta_R has mean < 0 with
  p_positive <= 0.5 (the ledger's REJECTED bar applied to the live rule). Until then: keep.
- A positive delta_R does not declare the rule working. It only means no rollback.

## What this does NOT do

- Does not change `ROLLBACK_ABS_MEAN_R`, `APPLIED_MIN_N`, any threshold, any baseline, or any
  frozen evidence.
- Does not register a hypothesis. (Operator freeze "register nothing more" respected.)
- Does not touch `obsidian-trade-logger`.

## Where it lives

- This file.
- `data/trade_hypothesis_ledger.json`: each of the five rules' `applied.rollback_procedure`
  (`as_of`, `verdict_rule`, `evidence_source`, `spec`), plus a `history` line dated 2026-10-18.
- `tools/trade_hypothesis_ledger.py` `_next_threshold`: when a rule carries a procedure, the
  "next threshold" cell names this spec so the nightly ledger and digest surface it on the
  morning the trigger fires.
