# SPARTA Arbitrage Research Readiness Gate v1 — build report

> **Research-only. Readiness gate / specification only.** No broker, no
> live trading, no paper-order execution, no exchange connection, no API
> keys, no scheduler, no external network calls, **no data fetch, no
> backtest, no dataset processing in this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_research_readiness_gate_v1/readiness_gate.json` | Machine-readable readiness gate (validator source of truth). |
| `reports/arbitrage_research_readiness_gate_v1/readiness_gate.md` | Human-readable gate: audited artifacts table, required artifact checks, validator checks, safety checks, allowed/forbidden next steps, data-collection/backtest/trading gates, PASS/WATCH/BLOCKED/PARKED rules, lane recommendation, safety boundaries. |
| `reports/arbitrage_research_readiness_gate_v1/report.md` | This build report. |
| `reports/arbitrage_research_readiness_gate_v1/report.json` | Build report (machine). |
| `tools/arbitrage_readiness_gate_check.py` | Stdlib-only validator (`validate` / `show` CLI) — schema + safety + path-existence checks. |
| `tests/test_arbitrage_readiness_gate.py` | 22 tests covering schema, safety, registry integration. |
| `tools/strategy_candidate_registry.py` | New STATUS_KEYWORDS rule (`"readiness_gate" → WATCH/MIXED`) + `extra_files` extended with the new gate docs; arbitrage lane now classifies as **WATCH**. |
| `tests/test_arbitrage_research_protocol.py` | Tightened invariant: arbitrage `status` is allowed to be IDEA **or** WATCH (never ACTIVE / STRONG). |
| `tests/test_arbitrage_data_contract.py` | Same tightening. |
| `tests/test_arbitrage_dataset_manifest.py` | Same tightening. |
| `tests/test_arbitrage_qa_harness_spec.py` | Same tightening. |
| `tests/test_arbitrage_data_source_evaluation.py` | Same tightening. |
| `tests/test_arbitrage_sample_dataset_plan.py` | Same tightening. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 10 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 11 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code,
sealed data, Bundle 4/5/6/7/8/9 validator tools, the 6 prior arbitrage
spec/data/manifest/QA/evaluation/plan JSON+MD files, `lessons.md`.

## What the readiness gate decides

# **`readiness_status: WATCH`**

### Final arbitrage foundation status

- All 6 arbitrage documents exist on disk and validate (each prior
  validator returns `validate: OK`).
- All 7 execution / fetch / connection / backtest / dataset-processing
  safety flags are pinned `False`.
- All 8 Strategy Factory and arbitrage validators pass.
- The candidate registry now classifies arbitrage as **WATCH** with 14
  source reports (2 docs × 7 bundles); the lane has **never been
  ACTIVE** and the evidence level has **never reached STRONG**.
- **NO** data has been pulled. **NO** QA report exists. **NO** tested
  edge exists. **NO** evidence exists.
- **No JARVIS / dashboard / paper-or-live execution / sealed-artifact /
  credential** files have been touched by any of the 7 arbitrage
  bundles.

The arbitrage research foundation lane is **COMPLETE** at the
specification level. The next move is operator-driven: author a Data
Collection Authorization Draft (still spec-only) **or** pivot to a
different research lane (e.g., Crypto-D1 Protocol Memo).

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest / dataset-processing
  flags pinned **False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `backtest_enabled`, `dataset_processing_enabled`.
- `research_only: true` asserted.
- `readiness_status` MUST be one of `PASS / WATCH / BLOCKED / PARKED` —
  validator rejects anything else.
- All 6 audited artifact paths MUST exist on disk (validator opens
  `repo_root / path` and checks `.exists()`); each must be
  `exists: True` and `validation_status: OK`.
- Trading gate **explicitly forbidden** —
  `future_authorization_requirements.trading_gate.
  explicitly_forbidden_by_this_readiness_gate` MUST be True; validator
  fails otherwise.
- Data-collection gate MUST include all 6 required approval markers
  (operator authorization, Bundle-8 source class, storage path, no
  credentials, no trading permissions, separate bundle approval).
- Backtest gate MUST include all 7 required pre-conditions (data
  complete, manifest frozen, QA report created, QA_PASS / approved
  QA_WARN, cost assumptions, no lookahead, no execution claims, separate
  bundle).
- `lane_recommendation` MUST declare
  `do_not_promote_to_ACTIVE=True` AND
  `do_not_promote_to_STRONG_evidence=True`.
- MD carries `NOT pure arbitrage`, `RELATIVE_VALUE`, `WATCH does not
  imply edge`, `A price gap is not profit`.
- Validator scans MD + JSON for forbidden capability claims (`guaranteed
  profit`, `risk-free profit`, `live-ready`, `production-ready`, `place
  the order`, `connect to exchange`, `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 207 passed in 2.15s
```

- `test_arbitrage_readiness_gate.py` — **22 new tests** (Bundle 10).
- Bundle 9 (`test_arbitrage_sample_dataset_plan.py`) — 23 still pass
  (assertion tightened from `==IDEA` to `in (IDEA, WATCH)`).
- Bundle 8 (`test_arbitrage_data_source_evaluation.py`) — 23 still pass.
- Bundle 7 (`test_arbitrage_qa_harness_spec.py`) — 22 still pass.
- Bundle 6 (`test_arbitrage_dataset_manifest.py`) — 19 still pass.
- Bundle 5 (`test_arbitrage_data_contract.py`) — 16 still pass.
- Bundle 4 (`test_arbitrage_research_protocol.py`) — 14 still pass.
- Bundle 3 (`test_strategy_candidate_registry.py`) — 16 still pass
  (none of those tests reference the new `readiness_gate` keyword, so
  classifier extension is backward-compatible).
- Bundle 2 (`test_strategy_next_bundle.py`) — 24 still pass.

## JSON validity

```
python tools/arbitrage_readiness_gate_check.py validate         → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate    → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate        → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate       → validate: OK
python tools/arbitrage_data_contract_check.py validate          → validate: OK
python tools/arbitrage_protocol_check.py validate               → validate: OK
python tools/strategy_candidate_registry.py validate            → validate: OK
python tools/strategy_next_bundle.py validate                   → validate: OK
```

## How this closes the arbitrage foundation lane

```
Bundle 4  Arbitrage Research Protocol v1              (30dabc4)
Bundle 5  Arbitrage Data Contract v1                  (c4d4c8b)
Bundle 6  Arbitrage Dataset Manifest v1               (492fcc1)
Bundle 7  Arbitrage QA Harness Spec v1                (8073bf3)
Bundle 8  Arbitrage Data Source Evaluation Memo v1    (4786390)
Bundle 9  Arbitrage Sample Dataset Plan v1            (e1b3741)
Bundle 10 Arbitrage Research Readiness Gate v1        (this bundle) — WATCH
```

Seven bundles. Six specifications. One readiness gate. Zero data pulled.
Zero backtests run. Zero exchange connections. Zero credentials. The
foundation is **closed at the specification level**; the lane is
**research-monitorable** but not cleared for any execution-adjacent
phase.

## Readiness gate validation result

**`validate: OK`** on the committed gate. All required top-level keys
present, all 7 safety flags pinned `False`, `readiness_status` is one of
the allowed values, all 6 audited artifacts exist on disk with
`validation_status: OK`, all six required data-collection-gate markers
present, all seven required backtest-gate markers present, trading gate
explicitly forbidden, `lane_recommendation` forbids ACTIVE / STRONG
promotion, MD carries all 4 required distinction phrases, zero forbidden
capability phrases in either JSON or MD.

## Candidate registry status for arbitrage after build

- **status:** **`WATCH`** ✅ (promoted from IDEA via new STATUS_KEYWORDS
  rule `"readiness_gate" → WATCH`; the rule applies because the seed's
  `extra_files` now includes `readiness_gate.md` / `readiness_gate.json`)
- **evidence_level:** `MIXED` (14 matched docs; no test/baseline/OOS
  evidence; cannot reach `STRONG`)
- **source_reports** (14 files):
  `["data_contract.json", "data_contract.md",
  "data_source_evaluation.json", "data_source_evaluation.md",
  "dataset_manifest.json", "dataset_manifest.md", "protocol.json",
  "protocol.md", "qa_harness_spec.json", "qa_harness_spec.md",
  "readiness_gate.json", "readiness_gate.md",
  "sample_dataset_plan.json", "sample_dataset_plan.md"]`
- **Guard held:** never ACTIVE, never STRONG.

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was NOT
artificially modified; the WATCH bonus added to the registry-aware
scoring (`+15` for WATCH lanes, per Bundle 3) actually *raises* the
arbitrage lane's score, so it remains the top deterministic pick.

This is honest deterministic behaviour, **not** a recommendation to
keep building arbitrage. The operator should consult the readiness
gate's `lane_recommendation` section (which forbids ACTIVE promotion
and explicitly recommends pivoting to a different lane or authoring a
data-collection draft) for the actual next step.

## Recommended next bundle

All three are read-only specs — **no fetch, no backtest, no execution**:

1. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); revisiting requires a NEW hypothesis, not a re-tune.
2. **Arbitrage Data Collection Authorization Draft** — still spec-only;
   proposes the exact source class + instance + venues + symbols + time
   window + storage path for the first tiny sample, citing Bundles 8 and
   9 and this gate. Only worth doing if the operator actually wants to
   move the arbitrage lane past WATCH.
3. **Data QA / Freeze workflow** — cross-cutting QA / freeze workflow
   that benefits multiple lanes.

The readiness gate has done its job: it has named the gates, declared
the lane WATCH, and explicitly forbidden execution-adjacent next steps.
The operator picks the actual Bundle 11.
