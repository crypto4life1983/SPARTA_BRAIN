# SPARTA Strategy Factory — Next Bundle Generator v1

A tiny, deterministic, **research-only** local generator that reads existing
Strategy Factory Routine Layer runtime outputs and produces the exact next
Claude/Codex prompt bundle for the highest-value next research or JARVIS task.

Tool: [`tools/strategy_next_bundle.py`](../../tools/strategy_next_bundle.py)
(Python standard library only).

## What was built

- `tools/strategy_next_bundle.py` — read-only generator with `generate` /
  `show` / `validate` CLI commands.
- `tests/test_strategy_next_bundle.py` — 19 tests covering safety contract,
  graceful failure modes, deterministic selection, JSON schema, prompt content.
- `.gitignore` — added `reports/strategy_factory_routines/next_bundle/` so
  generated runtime outputs are never accidentally committed.
- Tracked docs at `reports/strategy_factory_next_bundle_generator/`
  (`report.md` + `report.json`).

## What it reads (read-only inputs)

- `reports/strategy_factory_routines/strategy_queue/queue.json`
- `reports/strategy_factory_routines/daily_state/latest_state.json`
- `reports/strategy_factory_routines/weekly_review/latest_weekly_review.json`
- `storage/jarvis/strategy_factory/latest_strategy_factory_snapshot.json`

Missing or invalid files **never crash the generator**: they are surfaced under
`warnings` and `source_files_read[].state`.

## What it writes (gitignored runtime artifacts)

`reports/strategy_factory_routines/next_bundle/`:

- `next_bundle.json` — full bundle payload (selected item + ranked candidates
  + safety + acceptance criteria + source provenance).
- `next_bundle.md` — human-readable summary.
- `next_claude_prompt.txt` — **ready-to-paste** Claude/Codex prompt for the
  selected bundle.

## How selection works (deterministic)

Each queue item is filtered then scored.

**Hard filter (any one drops the item):**
- `blocked == True`
- `safety_level` not in `{research_only, analysis_only, read_only}`
- Defense-in-depth keyword scan: any "broker", "live trading", "paper order",
  "place order", "alpaca / ibkr / binance / exchange api", "credential / api
  key", "scheduler / cron install" string in the item's title/lane/reason/
  expected_output/next_bundle_suggestion/required_inputs.

**Score (integer; deterministic):**

| Axis | Effect |
|---|---|
| Priority (1 best) | `(10 - priority) * 10` |
| Lane == weekly's `lane_deserving_next_deep_bundle` | +50 |
| Lane appears in daily `active_lanes` | +20 |
| Lane in weekly `lanes_wasting_time` | −30 |
| Title/lane/reason matches copy-paste-reducing hints | +25 |
| Matches validation-quality hints | +20 |
| Matches "evidence/edge/OOS" hints | +15 |
| Matches "protocol/spec/prereg" hints | +30 |
| Matches "data QA/freeze/contract" hints | +30 |
| JARVIS/automation hint (with/without active lane) | +10 / +5 |
| Crypto hint while non-crypto lane is active | −15 |
| Danger keyword leaked past filter | −200 |

**Tiebreak:** score desc → lane asc → title asc (stable, deterministic).

## Safety guarantees (enforced by tests)

- Standard-library only. No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ` / `getenv`.
- The three trading-safety flags `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled` are pinned `False`
  as module constants, embedded in every JSON payload, and asserted False by
  `validate`.
- The generator only writes inside
  `reports/strategy_factory_routines/next_bundle/`; a test enumerates the temp
  repo tree after a run and fails on any file outside the output folder.
- The generated prompt MUST contain every safety phrase (`No broker control`,
  `No live trading`, `No paper order execution`, `Do not stage`,
  `TESTS REQUIRED`) — asserted by the test suite.
- Deterministic: same inputs → byte-identical payload (modulo `generated_at`).

## CLI

```bash
python tools/strategy_next_bundle.py generate    # writes the 3 runtime files
python tools/strategy_next_bundle.py show        # short summary + prompt path
python tools/strategy_next_bundle.py validate    # schema + safety checks; rc=0 ok, rc=2 fail
```

Optional `--repo-root PATH` redirects to a different checkout (used by the
tests against a temp tree).

## Tests

```bash
python -m pytest tests/test_strategy_next_bundle.py --rootdir=tests -q
```

**Result (initial build): 19 passed in 0.26s.**

## How to use it

1. Run the Strategy Factory Routine Layer if the inputs are stale:
   `python tools/strategy_factory_routines.py all`
2. Run `python tools/strategy_next_bundle.py generate`.
3. Paste the contents of
   `reports/strategy_factory_routines/next_bundle/next_claude_prompt.txt` into
   Claude/Codex as the next bundle.
4. (Optional) `python tools/strategy_next_bundle.py validate` re-asserts the
   safety contract on the latest generated bundle.

## What Bundle 3 should likely be

Based on the current selection (`Arbitrage research protocol`, priority 3,
research-only) and the broader state (factory color YELLOW, lane
`futures_donchian` deserves the next deep bundle but its protocol prereg is
not yet in queue), the most likely candidates for Bundle 3 — in priority
order — are:

1. **Strategy queue refresh + scoring transparency** — surface the
   `ranked_candidates` breakdown directly in the JARVIS panel so the operator
   can see _why_ the generator picked what it picked. Pure visibility upgrade;
   reduces operator copy-paste on bundle selection.
2. **Next-bundle diff between successive snapshots** — a read-only "what
   changed between yesterday's bundle and today's" line on the JARVIS panel,
   to catch silent priority drift across factory snapshots.
3. **Auto-derived "research direction" memo** — pull the top-3 ranked
   candidates + the weekly_review next_action_recommendation into a single
   read-only memo so a human reviewer doesn't re-read four JSON files.

All three are read-only, JARVIS-surface improvements that match the routine
layer's purpose (cut copy-paste; no execution). The operator picks.
