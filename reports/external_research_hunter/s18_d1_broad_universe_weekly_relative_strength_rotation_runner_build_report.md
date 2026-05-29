# s18-d1 weekly RS rotation — P3 BUILD report: runner (sealed)

**Authored (UTC):** `2026-05-29T02:11:14.380996Z` · **report_seal:** `ec51c287c3e09d5870722d92b9cb576452cbb10f44791658209eb1bce5021a53`
**Component:** runner harness (main.py) + execution_guard + synthetic fixture

Weekly RS primitives (trailing_return 126-21, cross_sectional_rank, select_top_8, equal_weight_targets 1/8, is_rebalance_bar R=5, rotation_exits/entries, cost) + CONFIG byte-equivalent to SEAL DA1-DA22 (weekly R=5, top-8) + Algo stub (live refusal). full_guard_check overall_pass=True. NO execution.

## Files built
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/main.py` — sha `ace47a8ae8de8c15…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/execution_guard.py` — sha `6ea20a759c917d00…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/__init__.py` — sha `592240e73f843d0d…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/tests/__init__.py` — sha `e3b0c44298fc1c14…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/tests/conftest.py` — sha `63c5eaeb6ecaf182…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/tests/test_smoke.py` — sha `1ade517d0f0c67b9…`
- `external_research_hunter/s18_d1_broad_universe_weekly_relative_strength_rotation_runner_harness/tests/fixtures/synthetic_weekly_universe_daily.csv` — sha `8bef773dcd962676…`

## Build validation
py_compile PASS · full_guard_check overall_pass True · K13 fold scheme valid · NO backtest/real-CSV/signal/pytest.

## Next
`Authorize s18-d1 broad-universe weekly relative-strength rotation P4 synthetic smoke only.`
