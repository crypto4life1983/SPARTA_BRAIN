"""P4 synthetic smoke battery for s21-d1 fresh-universe weekly RS rotation runner. Authored at P3 BUILD; run at P4.
Synthetic data + invariant checks only. NO real CSV reads. Weekly R=5, top-8, fresh 48-name universe."""

import csv

import pytest


def test_T1_modules_import_clean(runner_harness_module):
    assert all(runner_harness_module[k] is not None for k in
               ("main", "execution_guard", "in_sample_driver", "out_of_sample_driver", "walk_forward_driver"))


def test_T2_runner_class_instantiable(runner_harness_module):
    main = runner_harness_module["main"]
    algo = main.Algo(); algo.Initialize()
    assert algo.config["candidate_record_id"] == "s21-d1-broader-universe-weekly-relative-strength-rotation-48name-fresh-large-cap-long-history"
    assert algo._stale_fill_warning_count == 0 and algo.all_safety_warnings_zero() is True and algo.held_count() == 0


def test_T3_trailing_return_126_21(runner_harness_module):
    main = runner_harness_module["main"]
    closes = [float(i + 1) for i in range(260)]
    assert main.trailing_return(closes, 200, 126, 21) == pytest.approx(180.0 / 54.0 - 1.0)
    assert main.trailing_return(closes, 146, 126, 21) is None
    assert main.trailing_return(closes, 147, 126, 21) is not None


def test_T4_cross_sectional_rank(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.cross_sectional_rank({"AAA": 0.1, "BBB": 0.3, "CCC": 0.2, "DDD": None, "EEE": 0.2}) == ["BBB", "CCC", "EEE", "AAA"]


def test_T5_select_top_m_8(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.select_top_m(["A", "B", "C", "D", "E", "F", "G", "H", "I"], 8) == ["A", "B", "C", "D", "E", "F", "G", "H"]


def test_T6_equal_weight_targets_1_over_8(runner_harness_module):
    main = runner_harness_module["main"]
    t = main.equal_weight_targets(["A", "B", "C"], 120000.0, 8)
    assert all(v == pytest.approx(15000.0) for v in t.values())
    t8 = main.equal_weight_targets(list("ABCDEFGH"), 120000.0, 8)
    assert sum(t8.values()) == pytest.approx(120000.0)


def test_T7_is_rebalance_bar_weekly(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.is_rebalance_bar(160, 160, 5) is True
    assert main.is_rebalance_bar(165, 160, 5) is True
    assert main.is_rebalance_bar(163, 160, 5) is False
    assert main.is_rebalance_bar(159, 160, 5) is False


def test_T8_rotation_exits_entries(runner_harness_module):
    main = runner_harness_module["main"]
    prev = list("ABCDEFGH"); new = list("ABCDEFGI")
    assert main.rotation_exits(prev, new) == ["H"]
    assert main.rotation_entries(prev, new) == ["I"]


def test_T9_cost_primitives(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.commission_cost(10, 0.005, 1.0, 1.0) == pytest.approx(1.0)
    assert main.commission_cost(1000, 0.005, 1.0, 1.0) == pytest.approx(5.0)
    assert main.commission_cost(1000, 0.005, 1.0, 0.0) == 0.0
    assert main.slippage_cost(100, 50.0, 1.0, 1.0) == pytest.approx(0.5)


def test_T10_pyramid_short_forbidden(runner_harness_module):
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()
    with pytest.raises(RuntimeError, match="SHORTING_FORBIDDEN"):
        main.open_short_position()


def test_T11_config_locked_weekly_params(runner_harness_module):
    c = runner_harness_module["main"].CONFIG
    assert c["momentum_lookback_L"] == 126 and c["momentum_skip_S"] == 21
    assert c["top_m_held"] == 8 and c["rebalance_cadence_R_days"] == 5
    assert c["exit_rule"] == "ROTATION_RELATIVE_RANK" and c["exit_is_trailing_or_atr_stop"] is False
    assert c["sizing_method"] == "equal_weight" and c["signal_direction"] == "long-only"
    assert c["start_cash_usd"] == 100_000 and c["warmup_days"] == 160


def test_T12_universe_48name_locked(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    assert len(main.CONFIG["universe"]) == 48 and len(set(main.CONFIG["universe"])) == 48
    guard.assert_universe_locked(main.CONFIG)
    bad = dict(main.CONFIG); bad["universe"] = main.CONFIG["universe"][:24]
    with pytest.raises(Exception, match="UNIVERSE_DRIFT"):
        guard.assert_universe_locked(bad)


def test_T13_split_only(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    guard.assert_split_only_convention(main.CONFIG)
    bad = dict(main.CONFIG); bad["adjustment_convention"] = "split_and_dividend"
    with pytest.raises(Exception, match="C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY"):
        guard.assert_split_only_convention(bad)


def test_T14_cost_stress_matrix(runner_harness_module):
    tiers = runner_harness_module["main"].CONFIG["cost_stress_tiers"]
    assert [t["tier"] for t in tiers] == ["S0", "S1", "S2", "S3", "S4"]


def test_T15_validator_harness_pass(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    algo = main.Algo(); algo.Initialize()
    result = guard.full_guard_check(algo.config, safety_counters={"stale_fill_warning_count": algo._stale_fill_warning_count})
    assert result["overall_pass"] is True, f"errors: {result['errors']}"


def test_T16_weekly_cadence_guard(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    guard.assert_weekly_cadence(main.CONFIG)
    bad = dict(main.CONFIG); bad["rebalance_cadence_R_days"] = 10
    with pytest.raises(Exception, match="CADENCE_DRIFT"):
        guard.assert_weekly_cadence(bad)


def test_T17_long_only_equal_weight_guards(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    guard.assert_long_only(main.CONFIG); guard.assert_equal_weight_sizing(main.CONFIG)
    bad = dict(main.CONFIG); bad["shorting_enabled"] = True
    with pytest.raises(Exception, match="SHORTING_ENABLED_MUST_BE_FALSE"):
        guard.assert_long_only(bad)


def test_T18_K13_fold_scheme_locked(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]; wf = runner_harness_module["walk_forward_driver"]
    assert wf.validate_fold_scheme() is True
    guard.assert_k13_fold_scheme_locked(main.CONFIG); guard.assert_no_per_fold_refit(main.CONFIG)
    got = [(f["fold"], f["idx_start"], f["idx_end"]) for f in wf.K13_FOLDS]
    assert got == [("F1", 160, 478), ("F2", 479, 797), ("F3", 798, 1116), ("F4", 1117, 1435), ("F5", 1436, 1758)]


def test_T19_K13_verdict_gate(runner_harness_module):
    wf = runner_harness_module["walk_forward_driver"]
    assert wf.k13_verdict([True, True, True, False, False], 1000.0, True)["k13_pass"] is True
    assert wf.k13_verdict([True, True, False, False, False], 1000.0, True)["verdict"] == "OOS_NOT_ROBUST"
    assert wf.k13_verdict([True, True, True, True, False], -50.0, True)["k13_pass"] is False
    assert wf.k13_verdict([True, True, True, True, True], 1000.0, False)["k13_pass"] is False


def test_T20_driver_stubs_refuse_execution(runner_harness_module):
    with pytest.raises(RuntimeError, match="P6_IS_NOT_AUTHORIZED"):
        runner_harness_module["in_sample_driver"].run_in_sample()
    with pytest.raises(RuntimeError, match="P10_OOS_NOT_AUTHORIZED"):
        runner_harness_module["out_of_sample_driver"].run_out_of_sample()
    with pytest.raises(RuntimeError, match="P6_7_K13_NOT_AUTHORIZED"):
        runner_harness_module["walk_forward_driver"].run_walk_forward()


def test_T21_oos_isolation(runner_harness_module):
    oosd = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oosd, "IN_SAMPLE_START") and not hasattr(oosd, "IN_SAMPLE_END")
    assert oosd.OOS_START.isoformat() == "2024-01-02" and oosd.OOS_END.isoformat() == "2025-12-30"


def test_T22_end_to_end_synthetic_rotation_weekly_invariants(runner_harness_module, synthetic_prices):
    main = runner_harness_module["main"]
    syms = list(synthetic_prices.keys()); n = len(synthetic_prices[syms[0]])
    warmup, R, M, equity = 160, 5, 4, 100000.0
    holdings = []; closed = 0; max_held = 0
    for i in range(n):
        if not main.is_rebalance_bar(i, warmup, R):
            continue
        sigs = {s: main.trailing_return(synthetic_prices[s], i, 126, 21) for s in syms}
        selected = main.select_top_m(main.cross_sectional_rank(sigs), M)
        closed += len(main.rotation_exits(holdings, selected))
        targets = main.equal_weight_targets(selected, equity, M)
        holdings = selected; max_held = max(max_held, len(holdings))
        assert len(holdings) <= M
        assert all(v == pytest.approx(equity / M) for v in targets.values())
    assert max_held == M and closed == 0


def test_T23_synthetic_fixture_parses_if_present(runner_harness_module, synthetic_csv_path):
    if not synthetic_csv_path.exists():
        pytest.skip("synthetic fixture not present")
    main = runner_harness_module["main"]
    by_sym = {}
    with open(synthetic_csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_sym.setdefault(row["symbol"], []).append(float(row["close"]))
    i = min(len(v) for v in by_sym.values()) - 1
    assert isinstance(main.cross_sectional_rank({s: main.trailing_return(v, i, 126, 21) for s, v in by_sym.items()}), list)


def test_T24_clean_generalization_markers(runner_harness_module):
    c = runner_harness_module["main"].CONFIG
    assert c["is_clean_generalization_test"] is True
    assert c["edge_not_inherited_from_s18_s19_s20"] is True
    assert c["is_s18_s19_s20_revN"] is False
    assert c["clean_generalization_no_selection_bias"] is True
    assert (c["momentum_lookback_L"], c["momentum_skip_S"], c["rebalance_cadence_R_days"], c["top_m_held"]) == (126, 21, 5, 8)


def test_T25_calendar_alignment_guard(runner_harness_module):
    guard = runner_harness_module["execution_guard"]
    series = {s: [1.0, 2.0, 3.0] for s in runner_harness_module["main"].CONFIG["universe"]}
    dates = {s: ["2019-01-02", "2019-01-03", "2019-01-04"] for s in series}
    assert guard.assert_calendar_aligned_48(series, dates) is True
    bad = dict(series); bad[list(bad.keys())[0]] = [1.0, 2.0]
    with pytest.raises(Exception, match="CALENDAR_ALIGN_LENGTH_MISMATCH"):
        guard.assert_calendar_aligned_48(bad, None)
