# Factory-D11 — Validation Factory Closeout · MEMO ONLY

**This is a closeout memo. No code, no backtest, no IS/OOS run, no optimization,
no data fetch, no paper/live, no source/engine/test changes, no staging, no
commit.** It records that the core reusable validation factory is complete and
defines the next allowed step.

- **Created:** 2026-05-30
- **HEAD at memo context:** `9523da8` — a descendant of the Factory-D10 commit
  `940e611`. Automation advanced HEAD but touched **no** `trading_research/agentic_factory/`
  file (`git diff --name-only 940e611..HEAD -- trading_research/agentic_factory/`
  is empty).
- **Factory-D10 commit:** `940e611936e1f6f4ef2f39f12b8814475a9cedaa`

---

## 1. Factory completion summary

| Step | Deliverable |
|---|---|
| **D1** | Reusable validation runner **PLAN ONLY** — ladder A–L spec, data/git safety rules, lessons from the four parked branches. |
| **D2** | Standard report **schema + writer** — `engine/validation_reports.py` (`make_report` / `validate_report` / refuse-before-write `write_report` → `report.json` + `report.md`). |
| **D3** | **IS runner** — `engine/validation_is_runner.py`; runs one frozen callable on an explicit IS window with a hard 2023/2024/2025 OOS seal at both path and bar-date layers. |
| **D4** | **OOS enforcement** — `engine/validation_oos_runner.py`; refuses OOS without a committed protocol hash, refuses IS years / 2026 inside an OOS window, one-shot discipline. |
| **D5** | **Entry significance** — `engine/validation_entry_significance.py`; same-count random-entry permutation test over FIXED horizons (no horizon shopping). |
| **D6** | **Sequence risk / Monte Carlo** — `engine/validation_sequence_risk.py`; trade-order shuffle + bootstrap + top-winner dependence (the S25 path-luck lesson). |
| **D7** | **Regime / walk-forward / friction** — `engine/validation_regime.py`, `engine/validation_walk_forward.py`, `engine/validation_friction.py` (the S26 concentration / fragility / thin-edge lessons). |
| **D8** | **Final decision / readiness** — `engine/validation_decision.py`; maps per-module verdicts to one research decision + one readiness level; paper/live tiers unreachable on the default path. |
| **D9** | **CLI wrapper** — `engine/validation_cli.py`; `list-modules` / `describe` / `synthetic-smoke` / `version`; no dynamic import, no real-data run, no paper/live command. |
| **D10** | **Synthetic end-to-end smoke** — `engine/validation_synthetic_smoke.py` + `synthetic-e2e` CLI command; fake in-memory data drives the full ladder into per-module reports; no real strategy, no real market data. |

## 2. What the factory can now do

- Generate a standard, schema-validated `report.json` + `report.md` for any module.
- Run an **IS-only baseline** for a frozen strategy callable with a hard OOS seal.
- Enforce **OOS protocol** pre-registration and **one-shot OOS** against a committed protocol hash.
- Wrap **entry-edge significance** testing across fixed horizons.
- Run **trade-order Monte Carlo / bootstrap** sequence-risk analysis.
- Break a record down by **regime**, by rolling **walk-forward** window, and under a **friction** ladder.
- Map all module verdicts to one conservative **final decision / readiness gate**.
- Offer safe **CLI discovery** (`list-modules` / `describe`) and a **synthetic smoke + end-to-end** demo.

## 3. What the factory cannot do yet

- No real paper trading.
- No live trading.
- No broker adapter.
- No order execution.
- No automatic strategy optimization.
- No automatic parameter mutation.
- No automatic promotion.
- No real-money readiness — `PAPER_READY` / `LIVE_READY` are unreachable without a separate readiness memo with explicit override fields.

## 4. Parked strategy summary

- **Donchian** — PARKED (reference baseline only; profitable curve but `ENTRY_EDGE_NOT_SUPPORTED` + sequence fragility / path luck).
- **S26** — PARKED, `PARK_CANDIDATE` (OOS passed but thin `FRICTION_SENSITIVE` edge, `INCONCLUSIVE` entry/regime, single-year / post-2016 concentration).
- **S27** — PARKED, `IS_FAIL` (net-negative in-sample; stopped before OOS).
- **S28** — PARKED, `IS_FAIL` (net-negative in-sample; stopped before OOS).

**No strategy is paper-ready or live-ready. No active strategy.**

## 5. Safety rules

- Explicit pathspec commits only; never `git add .`; never `git add trading_research/agentic_factory/`.
- No OOS run before a committed OOS protocol hash.
- No strategy tuning after OOS (one-shot OOS discipline).
- No paper/live promotion without a separate readiness memo (explicit override fields required).
- Offline/inert modules only: no network, no broker, no data fetch, no dynamic code loading.
- Hard OOS seal (2023/2024/2025) and 2026 block enforced inside the runners.

## 6. Recommended next step

**Preferred — S29-D1:** a new strategy **idea-sourcing memo** (no code) that uses
the factory lessons. The core factory is now good enough for research use, so the
highest-value next move is sourcing a new frozen hypothesis to run through it.

**Alternative — Factory-D12:** optional docs / CLI polish.

## 7. Final line

**“Factory core is complete for research validation. It is not a paper/live
trading system.”**

---

### Guardrails

`memo_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_data_fetch` · `no_paper_or_live` · `no_broker_or_api` ·
`no_source_engine_test_changes` · `donchian_s26_s27_s28_read_only` ·
`jarvis_templates_hydra_untouched` · `no_staging` · `no_commit`.

**Trading recommendation:** NONE. Closeout memo only. Donchian, S26, S27, S28
remain PARKED; no active strategy; no paper/live system exists or is authorized.
