import pymongo
import pytest
import json5
import os

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
        dcas=[0],
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_1,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_one_trade.json5")


def test_main_with_one_trade_and_multiple_configs(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_one_trade_and_multiple_configs.json5")


def test_main_with_three_trades(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_3,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_2,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_three_trades.json5")


def test_main_with_three_trades_and_reset_sl_no_trailing(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_5,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_2,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_1,
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_three_trades_and_reset_sl_no_trailing.json5")


def test_main_with_33_trades_and_good_reset_config_no_trailing(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_3,
        take_profits=c.TAKE_PROFITS_5,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_1,
        leverages=c.LEVERAGES_4,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_2,
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_33_trades_good_reset_config_no_trailing.json5")


def test_main_with_invalid_sl_leverage_config(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_2,
        take_profits=c.TAKE_PROFITS_4,
        dcas=[0],
        stop_losses=[6],
        leverages=[20],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]], [["2.5", "-0.5"]], [["2", "-1"], ["3", "-2.5"]], [["1", "-0.5"]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_invalid_sl_leverage_config.json5")


def test_main_with_five_trades_and_trailing_reset_sl(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[20],
        dcas=[0],
        stop_losses=c.STOP_LOSSES_0,
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_five_trades_and_trailing_reset_sl.json5")


def test_main_with_five_trades_trailing_sl_no_reset(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[20],
        dcas=[0],
        stop_losses=[12],
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_five_trades_trailing_sl_no_reset.json5")


def test_main_with_five_trades_with_trail_delay(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[20],
        dcas=[0],
        stop_losses=c.STOP_LOSSES_0,
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_five_trades_with_trail_delay.json5")


def test_main_with_scenario_that_covers_signal_exits_in_profit(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[1000],
        dcas=[0],
        stop_losses=[25],
        leverages=[2],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_scenario_that_covers_signal_exits_in_profit.json5")


def test_main_with_trail_configs_to_check_validity_function(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[12],
        dcas=[0],
        stop_losses=[12],
        leverages=[5],
        trailing_sls=[True, False],
        trail_delays=[True, False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_trail_configs_to_check_validity_function.json5")


def test_main_with_15m_chart(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_5,
        take_profits=[12],
        dcas=[0],
        stop_losses=[11],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=[[[2, -1]]],
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_15m_chart.json5")

"""
def test_loss_limiter(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[10],
        stop_losses=[10],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=[[[2, -1]]],
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_loss_limiter.json5")
"""

def test_invalid_tp_tsl_combinations(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=[0.5, 2.5, 3.5],
        dcas=[0],
        stop_losses=[10],
        leverages=[1],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_4,
        loss_limit_fractions=[.1],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_invalid_tp_tsl_combinations.json5")


def test_bail_when_win_rate_or_drawdown_falls_below_standard(coll):
    # should screen out on win rate
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[50],
        dcas=[0],
        stop_losses=[1.5],
        leverages=[4],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        write_invalid_to_db=True,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    # should not screen out
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[50],
        dcas=[0],
        stop_losses=[10],
        leverages=[5],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-65],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    # should screen out on drawdown
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[0.5],
        dcas=[0],
        stop_losses=[1],
        leverages=[10],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    
    # screens out during a long stop loss exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[30],
        dcas=[0],
        stop_losses=[2],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )

    # screens out during a long take profit exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[2],
        dcas=[0],
        stop_losses=[1],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=10,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    ),

    # screens out during a long signal exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[30],
        dcas=[0],
        stop_losses=[2],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=10,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    # screens out during a short stop loss exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        take_profits=[12],
        dcas=[0],
        stop_losses=[12],
        leverages=[5],
        trailing_sls=[True],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-60],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    # screens out during a short take profit exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_7,
        take_profits=[6],
        dcas=[0],
        stop_losses=[3],
        leverages=[2],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_7,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    # screens out during a short signal exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_6,
        take_profits=[40],
        dcas=[0],
        stop_losses=[10],
        leverages=[2],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_9,
        loss_limit_fractions=[.2],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-40],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_bail_when_win_rate_or_drawdown_falls_below_standard.json5")


def test_leverage_adjustment_with_large_stop_loss(coll):
    # make sure our fix to prevent 0 leverage is working
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_8,
        take_profits=[40],
        dcas=[0],
        stop_losses=[30],
        leverages=[5],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_0,
        multiproc=False,
        write_invalid_to_db=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_leverage_adjustment_with_large_stop_loss.json5")


def test_invalid_scenarios_not_written_to_db(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=[0.5, 2.5, 3.5],
        dcas=[0],
        stop_losses=[10],
        leverages=[1],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_4,
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-33],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_not_written_to_db.json5")


def test_invalid_scenarios_due_to_initial_drawdown_screener(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_9,
        take_profits=[40],
        dcas=[0],
        stop_losses=[1, 4, 5, 6, 10],
        leverages=[5, 10],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_0,
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-49],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


def test_scenarios_already_in_db_are_not_rerun(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")
    # run it again without clearing db, then re-compare
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=c.TAKE_PROFITS_2,
        dcas=[0],
        stop_losses=c.STOP_LOSSES_2,
        leverages=c.LEVERAGES_3,
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")


def test_scenarios_already_in_db_are_rerun_with_replace_option(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_1,
        take_profits=[0.5, 2, 3, 4],
        dcas=[0],
        stop_losses=[1],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_rerun_with_replace_option_1.json5")
    # preserve original file
    os.rename(c.DATAFILENAMES_1[0], f"{c.DATAFILENAMES_1[0]}_orig")
    # rename the altered version of the original file so that it will produce the same scenario id
    os.rename(c.DATAFILENAMES_11[0], c.DATAFILENAMES_1[0])

    try:
        main(
            db_coll=c.COLL,
            datafilenames=c.DATAFILENAMES_1,
            take_profits=[3, 4, 5, 6],
            dcas=[0],
            stop_losses=[1],
            leverages=[1],
            trailing_sls=[False],
            trail_delays=[False],
            trail_last_resets=[False],
            sls=[[[]]],
            loss_limit_fractions=[0],
            drawdown_limits=[-100],
            winrate_floor=50,
            mean_floor=4,
            median_floor=4,
            floor_grace_period=50,
            multiproc=False,
            enable_qol=False,
            replace_existing_scenarios=True,
            accuracy_tester_mode=False,
            signal_exits=[True]
        )
        compare(coll, "db_after_scenarios_already_in_db_are_rerun_with_replace_option_2.json5")
    finally:
        # put filenames back to the way they were
        os.rename(c.DATAFILENAMES_1[0], c.DATAFILENAMES_11[0])
        os.rename(f"{c.DATAFILENAMES_1[0]}_orig", c.DATAFILENAMES_1[0])


def test_multiproc(coll):
    # this test mimics an earlier one, using the same file, it just does it with multiprocessing
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_9,
        take_profits=[40],
        dcas=[0],
        stop_losses=[1, 4, 5, 6, 10],
        leverages=[5, 10],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=c.SLS_0,
        loss_limit_fractions=[.2],
        multiproc=True,
        drawdown_limits=[-49],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


# htf dataset has short_ltf, long_ltf, short_htf, long_htf columns
def test_htf_dataset(coll):
    # this scenario is calibrated to produce at least one of each type of exit
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_10,
        take_profits=[50],
        dcas=[0],
        stop_losses=[10],
        leverages=[3],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[["1.5", "-1"], ["3.5", "-2"], ["4", "-2.5"], ["6", "-4.5"]]],
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-80],
        winrate_floor=10,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_htf_dataset.json5")


def test_multiple_datafilenames(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_12,
        take_profits=[5],
        dcas=[0],
        stop_losses=[5],
        leverages=[3],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[".3", "-.15"], [".6", "-.35"], ["1.5", "-1"], ["4", "-3"]]],
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-80],
        winrate_floor=10,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_multiple_datafilenames.json5")


def test_accuracy_tester_mode(coll):
    # in accuracy tester mode, only scenarios with equal TP and SL are run, others are skipped
    #   additionally, the following settings are overwritten to the following values
    #     leverages: [1]
    #     trailing_sls: [False]
    #     trail_delays: [False]
    #     sls: [[[]]]
    #     drawdown_limits: [-100]
    #     winrate_floor: 0
    main(
        db_coll=c.COLL,
        datafilenames=[c.DATAFILENAMES_12[0]],
        take_profits=[1, 3],
        dcas=[0],
        stop_losses=[1, 3],
        leverages=[25],
        trailing_sls=[True],
        trail_delays=[True],
        trail_last_resets=[False],
        sls=[[[0.5, -0.25]]],
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-2],
        winrate_floor=99,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=True,
        signal_exits=[True]
    )
    compare(coll, "db_after_accuracy_tester_mode.json5")

"""
def test_timeframe_specific_column_headers(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_14,
        signal_timeframes=[["12h"], ["15m"], ["90m", "30m"]],
        take_profits=[10],
        stop_losses=[10],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[.2],
        multiproc=False,
        drawdown_limits=[-90],
        winrate_floor=20,
        mean_floor=-5,
        median_floor=-5,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_timeframe_specific_column_headers.json5")
"""

def test_configurable_start_date(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_4,
        signal_start_dates=["2021-01-29T00:00:00Z"],
        take_profits=[20],
        dcas=[0],
        stop_losses=c.STOP_LOSSES_0,
        leverages=c.LEVERAGES_0,
        trailing_sls=[True],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=c.SLS_3,
        loss_limit_fractions=[0],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_configurable_start_date.json5")

"""
def test_no_signal_exit_option(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_14,
        signal_timeframes=[["5m"]],
        take_profits=[2],
        stop_losses=[2],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=-5,
        median_floor=-5,
        enable_qol=False,
        signal_exits=[False]
    )
    compare(coll, "db_after_no_signal_exit_option.json5")
"""

def test_duplicate_scenarios_are_rejected(coll):
    with pytest.raises(ValueError):
        main(
            db_coll=c.COLL,
            datafilenames=c.DATAFILENAMES_15,
            take_profits=[5, 5],
            dcas=[0],
            stop_losses=[1],
            leverages=[2],
            sls=[[[]]],
            enable_qol=False,
            check_for_dupes_up_front=True
        )


def test_bail_when_mean_or_median_falls_below_standard(coll):
    # this should bail out on mean
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_15,
        take_profits=[5],
        dcas=[0],
        stop_losses=[5],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=4,
        median_floor=4,
        enable_qol=False,
        signal_exits=[True]
    )
    # this should bail out on median
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_15,
        take_profits=[5],
        dcas=[0],
        stop_losses=[5],
        leverages=[1],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=0.2,
        median_floor=5,
        enable_qol=False,
        signal_exits=[True]
    )
    # this should not bail out because it maintains mean and median
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_15,
        take_profits=[5],
        dcas=[0],
        stop_losses=[7],
        leverages=[4],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[False],
        sls=[[[1.5, -1]]],
        loss_limit_fractions=[0.2],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=1,
        median_floor=0.5,
        enable_qol=False,
        signal_exits=[True]
    )
    compare(coll, "db_after_bail_when_mean_or_median_falls_below_standard.json5")


def test_when_ltf_and_htf_print_signal_in_same_row(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_16,
        take_profits=[0.25],
        dcas=[0],
        stop_losses=[2],
        leverages=[2],
        sls=[[[]]],
        multiproc=False,
        enable_qol=False,
        trail_last_resets=[False],
        signal_exits=[True],
        loss_limit_fractions=[0.2]
    )
    compare(coll, "db_after_test_when_ltf_and_htf_print_signal_in_same_row.json5")


def test_last_reset_trailing_option(coll):
    main(
        db_coll=c.COLL,
        datafilenames=c.DATAFILENAMES_15,
        take_profits=[10000],
        dcas=[0],
        stop_losses=[7],
        leverages=[4],
        sls=[[[2, -0.5], [3, -2], [4, -2.5]]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        trailing_sls=[False],
        trail_delays=[False],
        trail_last_resets=[True],
        signal_exits=[True],
        loss_limit_fractions=[0.2]
    )
    compare(coll, "db_after_last_reset_trailing_option.json5")

"""
def test_tri_arrow(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_09_2021.csv"],
        take_profits=[1.5],
        stop_losses=[8],
        leverages=[1],
        sls=[[[]]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        trailing_sls=[False],
        trail_delays=[False]
    )
    compare(coll, "db_after_tri_arrow.json5")
"""

def test_exception_is_thrown_when_initial_entry_is_not_present_in_double_or_triple_file(coll):
    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv"  # Triple arrow, no HTF or LTF shadow indication
            ],
            take_profits=[1.5],
            dcas=[0],
            stop_losses=[8],
            leverages=[1],
            sls=[[[]]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            trailing_sls=[False],
            trail_delays=[False],
            signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021_missing_shadows.csv"  # Double arrow, no HTF shadow indication
            ],
            take_profits=[1.5],
            dcas=[0],
            stop_losses=[8],
            leverages=[1],
            sls=[[[]]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            trailing_sls=[False],
            trail_delays=[False],
            signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_on_5m_05_2021_missing_shadows.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_initial_HTF.csv"  # Triple arrow, no LTF shadow ind.
            ],
            take_profits=[1.5],
            dcas=[0],
            stop_losses=[8],
            leverages=[1],
            sls=[[[]]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            trailing_sls=[False],
            trail_delays=[False],
            signal_exits=[False]
        )
    assert str(e_info.value) == "Triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_initial_HTF.csv provided without proper initial LTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                # Triple arrow, too many HTF shadow indications
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_HTF.csv"
            ],
            take_profits=[1.5],
            dcas=[0],
            stop_losses=[8],
            leverages=[1],
            sls=[[[]]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            trailing_sls=[False],
            trail_delays=[False],
            signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_HTF.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                # Triple arrow, too many LTF shadow indications
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_LTF.csv"
            ],
            take_profits=[1.5],
            dcas=[0],
            stop_losses=[8],
            leverages=[1],
            sls=[[[]]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            trailing_sls=[False],
            trail_delays=[False],
            signal_exits=[False]
        )
    assert str(e_info.value) == "Triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_LTF.csv provided without proper initial LTF shadow"


def test_dca(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021.csv"
        ],
        take_profits=[1.5],
        stop_losses=[8],
        leverages=[1],
        sls=[[[]]],
        dcas=[0, 0.5, 1, 8],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        signal_exits=[False]
    )
    compare(coll, "db_after_dca.json5")


def test_tf_specific_configs(coll):
    """
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021.csv",
            "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv"
        ],
        take_profits=[1.5],
        stop_losses=[8],
        leverages=[1],
        sls=[[[]]],
        dcas=[0],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        signal_exits=[True]
    )
    """
    pass


def test_exception_is_thrown_when_initial_htf_entry_is_not_present_in_multi_file(coll):
    # this will need to be done before the next time we use a multi file
    pass


def test_get_adjusted_leverage():
    loss_limit_fractions = [0, .1, .2, .5]
    leverages = [1, 2, 5, 10]
    stop_losses = [1, 2, 4, 5, 10]
    total_profit_pcts = [-50, 0, 50, 100, 150, 200, 301, 399, 467, 500]
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


def compare(_coll, expected):
    actual = list(_coll.find())
    with open("test_data/expected/" + expected) as _f:
        expected = json5.load(_f)
    assert actual == expected
