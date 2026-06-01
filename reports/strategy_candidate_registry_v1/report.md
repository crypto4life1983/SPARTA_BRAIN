# SPARTA Strategy Candidate Registry v1

A tiny, deterministic, **research-only** registry of every strategy/lane SPARTA
has tested, parked, failed, or wants to test next — the central memory of
candidate status so future research and JARVIS work does not re-do retired or
failed lanes.

Tool: [`tools/strategy_candidate_registry.py`](../../tools/strategy_candidate_registry.py)
(Python standard library only).

## What was built

- `tools/strategy_candidate_registry.py` — read-only registry with
  `build` / `show` / `validate` CLI commands.
- `tests/test_strategy_candidate_registry.py` — 16 tests covering safety
  contract, missing/empty inputs, classifier branches, schema, gitignore,
  determinism.
- `tools/strategy_next_bundle.py` — extended to (optionally) read
  `candidates.json`: drops queue lanes marked **FAILED**/**RETIRED**, and adds
  small scoring bonuses for **ACTIVE** (+25) / **WATCH** (+15).
- `tests/test_strategy_next_bundle.py` — 5 new integration tests; total 24
  pass.
- `.gitignore` — added
  `reports/strategy_factory_routines/candidate_registry/` so generated outputs
  stay local runtime artifacts.
- Tracked docs at `reports/strategy_candidate_registry_v1/` (this `report.md`
  + `report.json`).

## Candidate schema

Each candidate object includes:

| Field | Description |
|---|---|
| `candidate_id` | Slug, deterministic and stable across runs. |
| `title` | Human-readable name. |
| `lane` | Maps to the Routine Layer queue's `lane`. |
| `market` | `CRYPTO` / `FUTURES` / `MULTI` / `N_A`. |
| `timeframe` | `D1` / `4H` / `N_A`. |
| `hypothesis` | One-sentence research claim (no profitability promises). |
| `status` | one of `IDEA` / `ACTIVE` / `WATCH` / `FAILED` / `PARKED` / `BLOCKED` / `RETIRED`. |
| `evidence_level` | `NONE` / `WEAK` / `MIXED` / `STRONG` (auto-build never claims `STRONG`). |
| `last_tested_at` | YYYY-MM-DD extracted from latest matching report filename, else `null`. |
| `source_reports` | Deterministically-sorted list of report folder/file names that matched the lane. |
| `best_result_summary` | Never populated by auto-build (must be added by a human only). |
| `failure_reason` | Populated when a matched report name carries `failed_*` / `rejected`. |
| `blockers` | Synthesized from the queue's `required_inputs` + `blocked=True`. |
| `next_action` | Either the queue's `next_bundle_suggestion` or a status-aware default. |
| `priority` | From queue if available, else `5`. |
| `safety_level` | Always `research_only`. |
| `allowed_next_steps` | Pinned research-only language. |
| `forbidden_next_steps` | Pinned forbidden language (no live/broker/paper/keys/scheduler/network/exec edits). |
| `notes` | Free-text; empty by default. |

## Classification rules (conservative, deterministic)

For each seed lane the tool scans `trading_research/agentic_factory/reports/`
folder/file names and applies these substring rules in order, keeping the
**most severe** signal seen:

| Substring | Status | Evidence | Failure reason |
|---|---|---|---|
| `failed_` | **FAILED** | WEAK | "report name contains 'failed_'" |
| `rejected` | **FAILED** | WEAK | "report name contains 'rejected'" |
| `retire` | **RETIRED** | WEAK | — |
| `park` | **PARKED** | MIXED | — |
| `closeout` | **PARKED** | MIXED | — |
| `block` | **BLOCKED** | NONE | "report name contains 'block'" |
| `watch` | **WATCH** | MIXED | — |
| `oos_result` | **WATCH** | MIXED | — |
| `is_baseline` / `baseline` | **ACTIVE** | MIXED | — |
| `spec` / `protocol` / `plan` | **IDEA** | NONE | — |

Status precedence (higher wins across multiple matched reports):
`RETIRED > FAILED > BLOCKED > PARKED > WATCH > ACTIVE > IDEA`.

**Hard guardrails (enforced by `validate`):**
- `evidence_level == "STRONG"` is **never** allowed from the auto-build path —
  a tampered `STRONG` value fails `validate`.
- `safety_level` is always `research_only`.
- The three trading-safety flags (`live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`) are pinned
  `False` and asserted by `validate`.

## Files changed (Bundle 3)

| File | Change |
|---|---|
| `tools/strategy_candidate_registry.py` | NEW — the registry tool. |
| `tests/test_strategy_candidate_registry.py` | NEW — 16 tests. |
| `tools/strategy_next_bundle.py` | MODIFIED — optional registry read + filter + bonus. |
| `tests/test_strategy_next_bundle.py` | MODIFIED — 5 new registry-integration tests. |
| `.gitignore` | MODIFIED — adds `reports/strategy_factory_routines/candidate_registry/`. |
| `reports/strategy_candidate_registry_v1/report.md` | NEW — tracked doc (this file). |
| `reports/strategy_candidate_registry_v1/report.json` | NEW — tracked doc. |
| `brain_memory/projects/trading_bot/decisions.md` | append-only Bundle 3 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | append-only Bundle 4 candidate list. |

**Not touched:** `app.py`, `templates/jarvis.html`, paper/live execution code,
sealed data, `brain_memory/projects/trading_bot/lessons.md`.

## Safety guarantees (enforced by tests)

- Standard-library only (no `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ` / `getenv`).
- Writes only inside
  `reports/strategy_factory_routines/candidate_registry/` (test enumerates the
  temp tree after build).
- Three trading-safety flags pinned `False` (and asserted by `validate`).
- Auto-build never produces `STRONG` evidence (validation hard rule).
- Deterministic: two consecutive builds produce identical candidates (modulo
  `generated_at`).

## Tests run

```bash
python -m pytest tests/test_strategy_candidate_registry.py --rootdir=tests -q   # 16 passed
python -m pytest tests/test_strategy_next_bundle.py     --rootdir=tests -q   # 24 passed (19 existing + 5 new)
```

## JSON validity

```bash
python tools/strategy_candidate_registry.py validate    # validate: OK
python tools/strategy_next_bundle.py validate           # validate: OK
```

## How it integrates with Next Bundle Generator

The Next Bundle Generator now reads the registry from
`reports/strategy_factory_routines/candidate_registry/candidates.json` **if
present**. The integration is **purely additive**:

- **Filter:** any queue item whose lane matches a registry candidate with
  status `FAILED` or `RETIRED` is dropped from selection and removed from the
  ranked candidates list.
- **Score bonus:** `ACTIVE` candidates get **+25**, `WATCH` candidates get
  **+15**. Other statuses contribute zero (no penalty for `IDEA` / `PARKED` /
  `BLOCKED` — the existing scoring axes already handle those signals).
- **Missing registry:** unchanged Bundle 2 behaviour. The
  `source_files_read[]` row for the registry is reported as `missing` or
  `missing_or_invalid` but not added to `warnings` (the registry is optional
  by design).

## What Bundle 4 should likely be

Read-only, JARVIS-surface and research-quality upgrades that build on the
registry:

1. **Registry tile in the JARVIS Strategy Factory panel** — a small read-only
   summary (counts by status, top 3 candidates by priority, last build time).
2. **Status-diff line** — "what changed since the previous registry build"
   (lane was IDEA → PARKED, etc.). Pure visibility / change-audit.
3. **Manual override file** — operator-curated YAML/JSON layered on top of the
   auto-build so a human can promote a candidate to `STRONG` or mark a clear
   `RETIRED` decision. Auto-build still cannot produce `STRONG`.

All three are read-only, no execution, no broker, no paper/live. Operator
picks.
