# SPARTA Trading — Self-Improving Learning Loop (design + phase plan)

Operator instruction 2026-09-11: "SPARTA BRAIN for all trading, we need a self-improving learning machine."

Non-negotiables carried forward: research/paper only; live trading stays BLOCKED at the 6 gates;
no LLM or agent ever holds exchange keys or places orders; every promotion is evidence-gated and
pre-registered; nothing is softened, re-tuned in place, or rescued.

## What "self-improving" means here

A loop that, without a human in the middle, (1) observes every new outcome, (2) turns each
observation into candidate rules, (3) tests each rule FORWARD on outcomes that arrive after the
rule was written, (4) promotes rules that keep working and kills rules that do not, and (5) hands
a short list of confirmed rules to the operator for the one step that must stay human: changing
what the paper bot does. When the operator applies a rule, the loop keeps scoring it, so a rule
that stops working gets demoted again.

The loop is honest by construction: a rule is scored only on trades that closed after it was
registered, so in-sample fitting cannot promote anything.

## Data sources the loop learns from

| Source | Cadence | What it teaches |
|---|---|---|
| Journal paper bot (D/E/F/G, 11 pairs) | every closed trade | entry rules, regime alignment, stop/exit behaviour |
| Frozen-stack paper bot (BTC/ETH/XRP 1D) | daily, now with fresh 1m cache | whether the strongest historical engine still fires and pays |
| Funding-carry paper | daily | cost-bound carry yield, regime dependence |
| NQ ORB / GC ICT paper | daily | whether pre-registered windows resolve to sign+ or sign− |
| s21 weekly RS harness | weekly once data is refreshed | equity rotation edge forward |
| Research candidates (C-series, frozen) | per lane | family-level negative knowledge (already 26 rejected) |

## Phases

**Phase 1 — Hypothesis ledger + forward shadow scoring (built 2026-09-11).**
`tools/trade_hypothesis_ledger.py`. Every suggestion from the daily learning report becomes a
hypothesis registered with a date and frozen in-sample evidence. Each new closed journal trade
is scored against every open hypothesis as a counterfactual delta in R (blocked entry, stop cap,
2R partial). Bootstrap p(mean delta > 0) over forward trades. CONFIRMED at n ≥ 20 forward signals
and p ≥ 0.90; REJECTED at n ≥ 20 and p ≤ 0.50; otherwise SHADOW. Runs daily after the 01:15
learning report. Output: `reports/trade_learning/hypothesis_ledger.md`.

**Phase 2 — Paper-system scorers (next).** One scorer per paper line reading its own tracker
(funding carry, NQ ORB, GC ICT, frozen stack, s21) and mapping the pre-registered window/gates to
the same status vocabulary (SHADOW / CONFIRMED / REJECTED). Auto-writes a closure recommendation
when a window ends. No new gates invented; each scorer cites the line's own criteria file.

**Phase 3 — Rule generation beyond the fixed list.** The learning report currently emits a fixed
set of suggestion families. Phase 3 adds a small search over the journal for rule candidates
(regime × strategy × direction × weekday × holding-day cuts) with a multiple-testing correction
(deflated by the number of cuts tried) before anything enters the ledger. Cap: at most 3 new
hypotheses per week, so the ledger cannot flood itself.

**Phase 4 — Apply/rollback with the operator (permissioned).** When a rule is CONFIRMED, the loop
produces a patch spec for the paper bot (like `bot_rule_changes_spec_2026-09-11.md`). If the
operator grants edit permission for the bot repo, SPARTA applies it, tags the change with the
hypothesis id, and keeps scoring; a CONFIRMED rule that falls to p ≤ 0.50 forward is flagged for
rollback. Still paper. Live stays blocked.

**Phase 5 — Capital-efficiency advisory.** Uses the already-specified P0–P5 portfolio
capital-efficiency ladder (spec-only today) to rank confirmed lines by marginal contribution.
Advisory memo only.

## Guardrails that stay fixed

- Forward-only scoring; registration evidence is frozen and never used for promotion.
- Thresholds are constants in code, changed only by commit, never by the loop.
- Mirrored exchange rows count once (dedup by open_date+symbol+direction).
- Every artifact carries the READ ONLY / OBSERVATION ONLY banner; forbidden words enforced by test.
- Nothing in this loop can send an order, hold a key, or edit the bot without a human grant.
