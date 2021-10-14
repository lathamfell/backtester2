import pymongo
import pytest
import json5

from backtester import main, get_adjusted_leverage

import config_test as c


@pytest.fixture
def coll():
    mongo = pymongo.MongoClient(c.DB_CONNECTION)
    coll = mongo[c.DB][c.COLL]
    coll.drop()
    return coll


def test_main_with_one_trade(coll):
    main(
        db=c.DB,
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_1,
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_1,
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_one_trade.json5")


def test_main_with_one_trade_and_multiple_configs(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_one_trade_and_multiple_configs.json5")


def test_main_with_three_trades(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_3,
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_2,
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_three_trades.json5")


def test_main_with_three_trades_and_reset_sl_no_trailing(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_5,
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_2,
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_1,
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_three_trades_and_reset_sl_no_trailing.json5")


def test_main_with_33_trades_and_good_reset_config_no_trailing(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_3,
        take_profits=c.TAKE_PROFITS_5,
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_4,
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_2,
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_33_trades_good_reset_config_no_trailing.json5")


def test_main_with_invalid_sl_leverage_config(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_4,
        stop_losses=[0.06],
        leverages=[20],
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_6,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_invalid_sl_leverage_config.json5")


def test_main_with_five_trades_and_trailing_reset_sl(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[0.2],
        stop_losses=c.STOP_LOSSES_0,
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_five_trades_and_trailing_reset_sl.json5")


def test_main_with_five_trades_trailing_sl_no_reset(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[0.2],
        stop_losses=[0.12],
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_five_trades_trailing_sl_no_reset.json5")


def test_main_with_five_trades_with_trail_delay(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[0.2],
        stop_losses=c.STOP_LOSSES_0,
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_3,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_five_trades_with_trail_delay.json5")


def test_main_with_scenario_that_covers_signal_exits_in_profit(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[10],
        stop_losses=[0.25],
        leverages=[2],
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_scenario_that_covers_signal_exits_in_profit.json5")


def test_main_with_trail_configs_to_check_validity_function(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[0.12],
        stop_losses=[0.12],
        leverages=[5],
        trailing_sls=[True, False],
        trail_delays=[True, False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_trail_configs_to_check_validity_function.json5")


def test_main_with_15m_chart(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_5,
        take_profits=[0.12],
        stop_losses=[0.11],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[True],
        sls=[[[2, -1]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_15m_chart.json5")


def test_loss_limiter(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.1],
        stop_losses=[0.1],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[True],
        sls=[[[2, -1]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_loss_limiter.json5")


def test_invalid_tp_tsl_combinations(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=[0.005, 0.025, 0.035],
        stop_losses=[0.1],
        leverages=[1],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_4,
        loss_limit_fractions=[0.1],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_invalid_tp_tsl_combinations.json5")


def test_bail_when_win_rate_or_drawdown_falls_below_standard(coll):
    # should screen out on win rate
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.5],
        stop_losses=[0.015],
        leverages=[4],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        write_invalid_to_db=True,
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=20,
        enable_qol=False
    )
    # should not screen out
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.5],
        stop_losses=[0.1],
        leverages=[5],
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-65],
        winrate_floor=50,
        winrate_grace_period=50,
        enable_qol=False
    )
    # should screen out on drawdown
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.005],
        stop_losses=[0.01],
        leverages=[10],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=50,
        enable_qol=False
    )
    
    # screens out during a long stop loss exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.3],
        stop_losses=[0.02],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=20,
        enable_qol=False
    )

    # screens out during a long take profit exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.02],
        stop_losses=[0.01],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=10,
        enable_qol=False
    ),

    # screens out during a long signal exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.3],
        stop_losses=[0.02],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=10,
        enable_qol=False
    )
    # screens out during a short stop loss exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[0.12],
        stop_losses=[0.12],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-60],
        winrate_floor=50,
        winrate_grace_period=50,
        enable_qol=False
    )
    # screens out during a short take profit exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_7,
        take_profits=[0.06],
        stop_losses=[0.03],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_7,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=20,
        enable_qol=False
    )
    # screens out during a short signal exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.4],
        stop_losses=[0.1],
        leverages=[2],
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_9,
        loss_limit_fractions=[0.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-40],
        winrate_floor=50,
        winrate_grace_period=20,
        enable_qol=False
    )
    compare(coll, "db_after_bail_when_win_rate_or_drawdown_falls_below_standard.json5")


def test_leverage_adjustment_with_large_stop_loss(coll):
    # make sure our fix to prevent 0 leverage is working
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_8,
        take_profits=[0.4],
        stop_losses=[0.3],
        leverages=[5],
        trailing_sls=[False],
        trail_delays=[False],
        sls=c.SLS_0,
        multiproc=False,
        write_invalid_to_db=False,
        enable_qol=False
    )
    compare(coll, "db_after_leverage_adjustment_with_large_stop_loss.json5")


def test_invalid_scenarios_not_written_to_db(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=[0.005, 0.025, 0.035],
        stop_losses=[0.1],
        leverages=[1],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_4,
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-33],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=False,
        enable_qol=False
    )
    compare(coll, "db_after_invalid_scenarios_not_written_to_db.json5")


def test_invalid_scenarios_due_to_initial_drawdown_screener(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_9,
        take_profits=[0.4],
        stop_losses=[0.01, 0.04, 0.05, 0.06, 0.1],
        leverages=[5, 10],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_0,
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-49],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


def test_get_adjusted_leverage():
    loss_limit_fractions = [0, 0.1, 0.2, 0.5, 15]
    leverages = [1, 2, 5, 10]
    stop_losses = [0.01, 0.02, 0.04, 0.05, 0.1]
    total_profit_pcts = [-50, 0, 50, 100, 150, 200, 301, 399, 467, 500, 9999]
    results = []

    for llf in loss_limit_fractions:
        for l in leverages:
            for sl in stop_losses:
                for tpp in total_profit_pcts:
                    adj_leverage, loss_limit = get_adjusted_leverage(
                        stop_loss=sl, max_leverage=l, total_profit_pct=tpp,
                        loss_limit_fraction=llf)
                    results.append(
                        {"tpp": tpp,
                         "sl": sl,
                         "l": l,
                         "llf": llf,
                         "adj_leverage": adj_leverage,
                         "loss_limit": loss_limit,
                         "potential_loss": round(sl * adj_leverage, 3)})
    with open("test_data/expected/expected_adjusted_leverages.json5") as _f:
        expected = json5.load(_f)
    assert results == expected


def test_scenarios_already_in_db_are_not_rerun(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")
    # run it again without clearing db, then re-compare
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        winrate_grace_period=50,
        multiproc=False,
        enable_qol=False
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")


def test_multiproc(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_9,
        take_profits=[0.4],
        stop_losses=[0.01, 0.04, 0.05, 0.06, 0.1],
        leverages=[5, 10],
        trailing_sls=[True],
        trail_delays=[True],
        sls=c.SLS_0,
        loss_limit_fractions=[0.2],
        multiproc=True,
        drawdown_limits=[-49],
        winrate_floor=50,
        winrate_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


# htf dataset has short_ltf, long_ltf, short_htf, long_htf columns
# this test mimics an earlier one, using the same file, it just does it with multiprocessing
def test_htf_dataset(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_10,
        take_profits=[.5],
        stop_losses=[0.1],
        leverages=[3],
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[1.5, -1], [3.5, -2], [4, -2.5], [6, -4.5]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-80],
        winrate_floor=10,
        enable_qol=False
    )
    compare(coll, "db_after_htf_dataset.json5")


def test_signal_exits_only(coll):
    # this is an alpha run with a single arrow dataset
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_8,
        take_profits=[0.1],
        stop_losses=[0.1],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        multiproc=False,
        drawdown_limits=[-100],
        loss_limit_fractions=[0],
        signal_exits_only=True,
        winrate_floor=0,
        enable_qol=False,

    )
    compare(coll, "db_after_signal_exits_only.json5")


def test_htf_dataset_with_reentry_on_new_signals(coll):
    # this is an alpha run with an HTF dataset
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_10,
        take_profits=[0.1],
        stop_losses=[0.1],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        sls=[[[]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-80],
        winrate_floor=10,
        enable_qol=False,
        signal_exits_only=True,
        reenter_on_new_signal=True
    )
    compare(coll, "db_after_htf_dataset_with_reentry_on_new_signals.json5")


def compare(_coll, expected):
    actual = list(_coll.find())
    with open("test_data/expected/" + expected) as _f:
        expected = json5.load(_f)
    assert actual == expected
