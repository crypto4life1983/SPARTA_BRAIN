# Factory-D1 (S29-D0) — Reusable Validation Runner · PLAN ONLY

**This is a plan/spec for a reusable validation runner. No code, no backtest, no
IS/OOS run, no optimization, no parameter sweep, no data fetch, no strategy
search, no runner implementation, no raw-artifact cleanup, no staging, no
commit.** The plan is designed from the committed evidence of four already-parked
branches; it does not re-run any analysis.

- **Created:** 2026-05-30
- **Memory commit (context):** `18797fb`
- **HEAD at plan:** `4e21cc4` — a JARVIS-only background commit (app.py,
  docs/jarvis_system_map.json, templates/jarvis.html, tests/test_jarvis_route.py);
  it touched **no** agentic_factory file and `18797fb` remains its ancestor.
- **Context reports read (read-only):** S25-D1 Donchian MC, S26-D18 decision
  gate, S27-D4 IS baseline, S28-D4 IS baseline.

---

## 1. Executive summary

- The validation ladder was built and run **manually, prompt-by-prompt**, across
  four strategy branches.
- It correctly **PARKED all four**: Donchian (reference baseline only), S26
  (PARK_CANDIDATE), S27 (IS_FAIL), S28 (IS_FAIL).
- The highest-value next improvement is **automation/repeatability of that
  ladder — not immediately testing another strategy**.
- This step designs a reusable runner so any future *frozen* strategy can be put
  through the same controlled, anti-overfit ladder with consistent reports and
  identical git/data guardrails.

## 2. Problem being solved

Manual prompt-by-prompt validation is **slow and error-prone**:

- Repeated report patterns hand-authored every step.
- Repeated git guardrails restated every commit.
- Repeated IS/OOS separation logic re-implemented per branch.
- Risk of **accidental OOS peeking** (the 2023–2025 seal is enforced only by
  hand-written asserts today).
- Risk of **mixed commits** from background JARVIS index races.
- Hard to **compare candidates** consistently when every report is bespoke.

## 3. Design goal

A reusable validation runner that takes a **frozen** strategy engine + frozen
spec + a branch ID/commit, and generates the **same decision-record ladder** —
one module at a time, each gated — in a controlled, reproducible, anti-overfit
way, producing uniform `report.json` / `report.md` per module.

## 4. Non-goals (explicit)

- **Not** a strategy optimizer.
- **Not** an agent that mutates strategies until profitable.
- **Not** a paper-trading system.
- **Not** a live-trading system.
- **Not** broker-connected; no network, no data fetch.
- **Not** allowed to change strategy parameters.
- **Not** allowed to touch OOS data until the OOS protocol is committed.
- **Not** allowed to auto-promote a candidate, pick the best variant, or hide
  failed branches.

## 5. Proposed validation ladder modules

| ID | Module | Purpose | Key hard rule |
|---|---|---|---|
| A | `spec_check` | Verify frozen spec exists, params locked, branch ID + spec commit recorded | Block all later modules if params not frozen |
| B | `is_baseline` | Run IS only; enforce IS window; create IS decision record | **OOS files refused**; no param input |
| C | `oos_protocol` | Pre-register pass/watch/fail BEFORE OOS; require commit before OOS | OOS run refused without committed protocol |
| D | `oos_run` | Run OOS **once**; compare strictly to protocol | One-shot; protocol hash must match a commit |
| E | `entry_significance` | Real entries vs same-count random-in-regime; optional vs raw-signal baseline | Fixed horizons; no horizon shopping |
| F | `sequence_risk` | Trade-order Monte Carlo + bootstrap + top-winner dependence | Report prob(R≤0), DD tail, top-3 removal sign |
| G | `regime_breakdown` | Vol/trend/year regimes + concentration analysis | Flag single-year / single-regime dominance |
| H | `multimarket` | NQ primary, ES independent, micros proxy-only | **Micros never independent**; cap at PARTIAL_SUPPORT when independence is by-ticker |
| I | `walk_forward` | Rolling 3yr/5yr windows; common weak windows | Surface shared weak windows (e.g. 2014–2016) |
| J | `friction_stress` | Low/moderate/high/severe R-cost; break-even friction | Report IS **and** OOS at each level |
| K | `readiness_gate` | Map evidence to a readiness tier | Tiers below |
| L | `final_decision` | Final branch disposition | Verdicts below |

- **Readiness tiers (K):** `BLOCKED` → `RESEARCH_CANDIDATE` →
  `VALIDATION_CANDIDATE` → `PAPER_REVIEW_CANDIDATE` → `PAPER_READY` →
  `LIVE_READY`.
- **Final verdicts (L):** `CONTINUE` · `PARK` · `FAIL` · `REDESIGN_REQUIRED`.

## 6. Data safety rules

- **Hard-block OOS files during any IS module** — refuse the run, do not silently
  drop.
- **Hard-block 2026** unless explicitly authorized.
- **No network fetch** anywhere inside the runner.
- **Explicit data inventory** — every input file path recorded.
- The **exact input file list and data window** must be recorded in **every**
  module report.

## 7. Git safety rules (standing)

- **Explicit pathspec commits only.**
- **Never** plain `git commit` when JARVIS may stage files.
- **Never** `git add .`. **Never** `git add trading_research/agentic_factory/`.
- Report the exact staged set (`git diff --cached --name-only`) **before** commit.
- Report `git show --stat HEAD` **after** commit.
- **Raw artifacts** (e.g. `_run.json` / `_run.py`) are **not committed** unless
  explicitly approved.
- When HEAD advances externally, confirm the prior approved commit is still an
  ancestor and the external commit touched no agentic_factory file before
  proceeding; never touch/unstage JARVIS files.

## 8. Report structure standard

Every module report must include: **branch ID · module ID · source commits ·
input files · data window · frozen params · metrics · verdict · caveats · next
allowed step · forbidden actions.**

## 9. Runner architecture proposal (plan only — nothing created)

Suggested future files (NOT created in this step):

- `engine/validation_runner.py`
- `engine/validation_reports.py`
- `engine/validation_gates.py`
- `tests/test_validation_runner.py`
- `docs/validation_ladder.md`

## 10. CLI proposal (proposed only — not implemented)

```
python -m engine.validation_runner --branch S29 --module is_baseline \
    --strategy engine/s29_x.py --market NQ --window IS

python -m engine.validation_runner --branch S29 --module oos_run \
    --protocol-commit <hash>
```

These commands are **proposed only**, not implemented.

## 11. Guardrail against overfitting

The runner must **not**: choose the best variant · mutate parameters · rerun OOS
with changed rules · hide failed branches · combine OOS with IS to justify
promotion · promote based on one metric.

## 12. Lessons from the parked branches

- **Donchian:** profit can **hide** a weak entry and sequence fragility. S24 found
  `ENTRY_EDGE_NOT_SUPPORTED`; S25 found prob(total R≤0) = 20.9%, net flips
  negative removing the top 3, best trade 50–65% of net, and realized DD only at
  the ~11th percentile of shuffles (path luck). **A profitable curve is not an
  edge.**
- **S26:** **OOS PASS is not enough.** NQ+ES OOS both passed and were
  friction-robust, but the thin ~0.06R IS edge was `FRICTION_SENSITIVE`, entry
  significance was `INCONCLUSIVE`, regime was `INCONCLUSIVE` (profitable vol
  regime inconsistent across markets), the record lived entirely in the post-2016
  trend, and OOS was single-year-dominated (NQ 2024 = 61.7%, ES 2025 = 72.8%) →
  `PARK_CANDIDATE`.
- **S27 / S28:** **IS_FAIL must stop before OOS.** Both failed IS net-negative
  with the anti-Donchian top-3 gate failing. Burning the one-shot OOS on an
  IS-failed branch wastes the clean look and invites curve-fitting.
- **Why the ladder is valuable:** it **saves the OOS seal** and prevents emotional
  continuation — converting "this looks promising" into mechanical pass/watch/fail
  against pre-registered floors.

## 13. Proposed implementation sequence

| Step | Scope |
|---|---|
| **Factory-D2** | validation report **schema + report writer ONLY** |
| Factory-D3 | IS runner harness for one **existing** (frozen, parked) engine |
| Factory-D4 | OOS protocol/run enforcement (one-shot + protocol-commit gate) |
| Factory-D5 | entry significance integration |
| Factory-D6 | sequence-risk integration |
| Factory-D7 | regime / walk-forward / friction modules |
| Factory-D8 | final decision dashboard/report |

**No paper/live module until much later**, and only under separate explicit
authorization.

## 14. Final recommendation

**Build Factory-D2 next.** Repeatability should come before more strategy search.
Four branches already proved the ladder works; encoding the **report schema +
writer first** (Factory-D2) is the smallest, lowest-risk increment that removes
the most manual error (bespoke reports, restated guardrails) and makes every
later module consistent. Returning to S29 idea-sourcing now would re-incur the
manual cost on every step.

- **Alternative (if continuing the search instead):** **S29-D1** deeper
  idea-sourcing memo (no code) — valid, but recommended to defer until the runner
  exists.

## 15. Final line

**“Factory-D1 is a plan-only step. No strategy test, optimization, paper trading,
live trading, or runner implementation is authorized.”**

---

### Guardrails

`plan_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api`
· `no_strategy_search` · `no_runner_implementation` · `no_raw_artifact_cleanup` ·
`donchian_s26_s27_s28_read_only` · `jarvis_templates_hydra_untouched` ·
`no_staging` · `no_commit`.

**Trading recommendation:** NONE. Plan-only design step. Donchian, S26, S27, S28
remain PARKED; no new strategy started; the runner is not built.
