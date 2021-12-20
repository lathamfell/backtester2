import pymongo
import pytest
import json5
import os

from backtester import main

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
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[6]],
        leverages=[[1]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_one_trade.json5")


def test_main_with_one_trade_and_multiple_configs(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[0.5], [2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1], [6]],
        leverages=[[1], [10]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_one_trade_and_multiple_configs.json5")


def test_main_with_three_trades(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_three_trades.csv"],
        take_profits=[[4]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[6]],
        leverages=[[2]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_three_trades.json5")


def test_main_with_invalid_sl_leverage_config(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_three_trades.csv"],
        take_profits=[[1]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[6]],
        leverages=[[20]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_invalid_sl_leverage_config.json5")


def test_main_with_scenario_that_covers_signal_exits_in_profit(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_five_trades.csv"],
        take_profits=[[1000]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[25]],
        leverages=[[2]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_scenario_that_covers_signal_exits_in_profit.json5")


def test_main_with_15m_chart(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_15_from_09_2017_with_T3_4h.csv"],
        take_profits=[[2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[6]],
        leverages=[[5]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_15m_chart.json5")


def test_screen_out_on_win_rate(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[50]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1.5]],
        leverages=[[4]],
        multiproc=False,
        write_invalid_to_db=True,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_on_win_rate.json5")


def test_screen_out_on_drawdown(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[0.5]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1]],
        leverages=[[10]],
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
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_on_drawdown.json5")


def test_screen_out_during_long_stop_loss_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[30]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[2]],
        leverages=[[2]],
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
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_long_stop_loss_exit.json5")


def test_screen_out_during_long_take_profit_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1]],
        leverages=[[2]],
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
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_long_take_profit_exit.json5")


def test_screen_out_during_long_signal_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[30]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[2]],
        leverages=[[2]],
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
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_long_signal_exit.json5")


def test_screen_out_during_short_stop_loss_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_five_trades.csv"],
        take_profits=[[12]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[3]],
        leverages=[[5]],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-50],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_short_stop_loss_exit.json5")


def test_screen_out_during_short_take_profit_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3_first_trade_removed.csv"],
        take_profits=[[6]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[3]],
        leverages=[[2]],
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
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_short_take_profit_exit.json5")


def test_screen_out_during_short_signal_exit(coll):
    # either win rate or dd screen out
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_T3.csv"],
        take_profits=[[0.5]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[8]],
        leverages=[[1]],
        multiproc=False,
        clear_db=False,
        write_invalid_to_db=True,
        drawdown_limits=[-11],
        winrate_floor=50,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=20,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_during_short_signal_exit.json5")


def test_leverage_adjustment_with_large_stop_loss(coll):
    # make sure the fix to prevent 0 leverage bug is working
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_laguerre.csv"],
        take_profits=[[40]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[30]],
        leverages=[[5]],
        multiproc=False,
        write_invalid_to_db=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_leverage_adjustment_with_large_stop_loss.json5")


def test_invalid_scenarios_not_written_to_db(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[30], [2.5], [3.5]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[10]],
        leverages=[[1]],
        multiproc=False,
        drawdown_limits=[-10],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_not_written_to_db.json5")


def test_invalid_scenarios_due_to_initial_drawdown_screener(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_laguerre_trunc.csv"],
        take_profits=[[40]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1], [4], [5], [6], [10]],
        leverages=[[5], [10]],
        multiproc=False,
        drawdown_limits=[-49],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


def test_scenarios_already_in_db_are_not_rerun(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[0.5], [2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1], [6]],
        leverages=[[1], [10]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")
    # run it again without clearing db, then re-compare
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[0.5], [2]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1], [6]],
        leverages=[[1], [10]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_not_rerun.json5")


def test_scenarios_already_in_db_are_rerun_with_replace_option(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
        take_profits=[[0.5], [2], [3], [4]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1]],
        leverages=[[1]],
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        multiproc=False,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_scenarios_already_in_db_are_rerun_with_replace_option_1.json5")
    # preserve original file
    os.rename(["test_data/BYBITBTCUSD_240_2021_one_trade.csv"][0], f"test_data/BYBITBTCUSD_240_2021_one_trade.csv_orig")
    # rename the altered version of the original file so that it will produce the same scenario id
    os.rename("test_data/BYBITBTCUSD_240_2021_one_trade_last_line_removed.csv", "test_data/BYBITBTCUSD_240_2021_one_trade.csv")

    try:
        main(
            db_coll=c.COLL,
            datafilenames=["test_data/BYBITBTCUSD_240_2021_one_trade.csv"],
            take_profits=[[3], [4], [5], [6]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[1]],
            leverages=[[1]],
            drawdown_limits=[-100],
            winrate_floor=50,
            mean_floor=4,
            median_floor=4,
            floor_grace_period=50,
            multiproc=False,
            enable_qol=False,
            replace_existing_scenarios=True,
            accuracy_tester_mode=False,
            htf_signal_exits=[True]
        )
        compare(coll, "db_after_scenarios_already_in_db_are_rerun_with_replace_option_2.json5")
    finally:
        # put filenames back to the way they were
        os.rename(["test_data/BYBITBTCUSD_240_2021_one_trade.csv"][0], ["test_data/BYBITBTCUSD_240_2021_one_trade_last_line_removed.csv"][0])
        os.rename(f"test_data/BYBITBTCUSD_240_2021_one_trade.csv_orig", ["test_data/BYBITBTCUSD_240_2021_one_trade.csv"][0])


def test_multiproc(coll):
    # this test mimics an earlier one, using the same file, it just does it with multiprocessing
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_laguerre_trunc.csv"],
        take_profits=[[40]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[1], [4], [5], [6], [10]],
        leverages=[[5], [10]],
        multiproc=True,
        drawdown_limits=[-49],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_invalid_scenarios_due_to_initial_drawdown_screener.json5")


# htf dataset has short_ltf, long_ltf, short_htf, long_htf columns
def test_dub_a(coll):
    # this scenario is calibrated to produce at least one of each type of exit
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/btcusd-5m_with_cols_2017_laguerre_4h_1D.csv"],
        take_profits=[[2, 1]],
        tps_after_dca=[None],
        dcas=[[0, 1]],
        stop_losses=[[4, 2]],
        leverages=[[4, 2]],
        multiproc=False,
        drawdown_limits=[-80],
        winrate_floor=10,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_dub_a.json5")


def test_multiple_datafilenames(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/COINBASE_BTCUSD_15_1h_on_5m_2021.csv",
            "test_data/COINBASE_BTCUSD_1h_on_5m_2021.csv"
        ],
        take_profits=[[5, 5]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[5, 5]],
        leverages=[[3, 3]],
        multiproc=False,
        drawdown_limits=[-90],
        winrate_floor=10,
        mean_floor=-5,
        median_floor=-5,
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_multiple_datafilenames.json5")


def test_accuracy_tester_mode(coll):
    # in accuracy tester mode, only scenarios with equal TP and SL are run, others are skipped
    #   additionally, the following settings are overwritten to the following values
    #     leverages: [1]
    #     drawdown_limits: [-100]
    #     winrate_floor: 0
    #     mean_floor, median_floor: -100
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/COINBASE_BTCUSD_15_1h_on_5m_2021.csv"],
        take_profits=[[1, 1], [3, 3]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[1, 1], [3, 3]],
        leverages=[[25, 25]],  # overwritten
        multiproc=False,
        drawdown_limits=[-2],  # overwritten
        winrate_floor=99,  # overwritten
        mean_floor=4,  # overwritten
        median_floor=4,  # overwritten
        floor_grace_period=50,
        enable_qol=False,
        accuracy_tester_mode=True,
        htf_signal_exits=[True]
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
        datafilenames=["test_data/BYBITBTCUSD_240_2021_five_trades.csv"],
        signal_start_dates=["2021-01-29T00:00:00Z"],
        take_profits=[[20]],
        tps_after_dca=[None],
        dcas=[[0]],
        stop_losses=[[12]],
        leverages=[[5]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=50,
        mean_floor=4,
        median_floor=4,
        floor_grace_period=50,
        write_invalid_to_db=True,
        enable_qol=False,
        accuracy_tester_mode=False,
        htf_signal_exits=[True]
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
            datafilenames=["test_data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
            take_profits=[[5], [5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[1]],
            leverages=[[2]],
            enable_qol=False,
            check_for_dupes_up_front=True
        )


def test_screen_out_on_mean(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
        take_profits=[[5, 5]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[5, 5]],
        leverages=[[1, 1]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=4,
        median_floor=4,
        enable_qol=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_test_screen_out_on_mean.json5")


def test_screen_out_on_median(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
        take_profits=[[5, 5]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[5, 5]],
        leverages=[[1, 1]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=0.05,
        median_floor=2,
        enable_qol=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_screen_out_on_median.json5")


def test_does_not_screen_out_mean_or_median(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
        take_profits=[[5, 5]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[7, 7]],
        leverages=[[4, 4]],
        multiproc=False,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=1,
        median_floor=0.5,
        enable_qol=False,
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_does_not_screen_out_mean_or_median.json5")


def test_when_ltf_and_htf_print_signal_in_same_row(coll):
    main(
        db_coll=c.COLL,
        datafilenames=["test_data/COINBASE_BTCUSD_1D_45m_on_5m_2020_fake_truncated.csv"],
        take_profits=[[0.25, 0.25]],
        tps_after_dca=[None],
        dcas=[[0, 0]],
        stop_losses=[[2, 2]],
        leverages=[[2, 2]],
        multiproc=False,
        enable_qol=False,
        htf_signal_exits=[True],
    )
    compare(coll, "db_after_when_ltf_and_htf_print_signal_in_same_row.json5")


def test_tri_arrow(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_09_2021.csv",
            "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_09_2021_with_initial_ltf_shadow_flipped.csv"
        ],
        take_profits=[[1.6, 1.5, 1.4]],
        tps_after_dca=[None],
        stop_losses=[[9, 8, 7]],
        dcas=[[2, 1, 0.5]],
        leverages=[[3, 2, 1]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
    )
    compare(coll, "db_after_tri_arrow.json5")


def test_exception_is_thrown_when_initial_entry_is_not_present_in_double_or_triple_file(coll):
    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv"  # Triple arrow, no HTF or LTF shadow indication
            ],
            take_profits=[[1.5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[8]],
            leverages=[[1]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            htf_signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021_missing_shadows.csv"  # Double arrow, no HTF shadow indication
            ],
            take_profits=[[1.5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[8]],
            leverages=[[1]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            htf_signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_on_5m_05_2021_missing_shadows.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_initial_HTF.csv"  # Triple arrow, no LTF shadow ind.
            ],
            take_profits=[[1.5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[8]],
            leverages=[[1]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            htf_signal_exits=[False]
        )
    assert str(e_info.value) == "Triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_initial_HTF.csv provided without proper initial LTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                # Triple arrow, too many HTF shadow indications
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_HTF.csv"
            ],
            take_profits=[[1.5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[8]],
            leverages=[[1]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            htf_signal_exits=[False]
        )
    assert str(e_info.value) == "Double or triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_HTF.csv provided without proper initial HTF shadow"

    with pytest.raises(Exception) as e_info:
        main(
            db_coll=c.COLL,
            datafilenames=[
                # Triple arrow, too many LTF shadow indications
                "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_LTF.csv"
            ],
            take_profits=[[1.5]],
            tps_after_dca=[None],
            dcas=[[0]],
            stop_losses=[[8]],
            leverages=[[1]],
            multiproc=False,
            enable_qol=False,
            winrate_floor=0,
            mean_floor=-10,
            median_floor=-10,
            drawdown_limits=[-100],
            htf_signal_exits=[False]
        )
    assert str(e_info.value) == "Triple arrow file BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021_with_double_LTF.csv provided without proper initial LTF shadow"


def test_dca(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021.csv",
        ],
        take_profits=[[1.5, 1.5]],
        tps_after_dca=[None],
        stop_losses=[[8, 8]],
        leverages=[[1, 1]],
        dcas=[[0, 0], [0.5, 0.5], [1, 1], [7, 7]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        htf_signal_exits=[False],
    )
    compare(coll, "db_after_dca.json5")


def test_dca_with_sig_exit(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021.csv",
        ],
        take_profits=[[10, 10]],
        tps_after_dca=[None],
        stop_losses=[[20, 20]],
        leverages=[[1, 1]],
        dcas=[[0.25, 0.25]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_dca_with_sig_exit.json5")


def test_screen_out_scenarios_where_dca_greater_than_or_eq_sl(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_on_5m_05_2021.csv"
        ],
        take_profits=[[1.5, 1.5]],
        tps_after_dca=[None],
        dcas=[[1, 12], [10, 10]],
        stop_losses=[[1, 1], [12, 12]],
        leverages=[[1, 1]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        htf_signal_exits=[False],
    )
    compare(coll, "db_after_screen_out_scenarios_where_dca_greater_than_or_eq_sl.json5")


def test_move_tp_after_dca(coll):
    main(
        db_coll=c.COLL,
        datafilenames=[
            "test_data/BYBIT_BTCUSD_1D_45m_5m_on_5m_09_2021.csv"
        ],
        take_profits=[[2, 1, 0.5]],
        dcas=[[0.75, 1, 0.5]],
        tps_after_dca=[[0.5, 0.5, 0.5], [3, 2, 1], None],
        stop_losses=[[10, 10, 10]],
        leverages=[[3, 2, 1]],
        multiproc=False,
        enable_qol=False,
        winrate_floor=0,
        mean_floor=-10,
        median_floor=-10,
        drawdown_limits=[-100],
        htf_signal_exits=[True]
    )
    compare(coll, "db_after_move_tp_after_dca.json5")


def test_exception_is_thrown_when_initial_htf_entry_is_not_present_in_multi_file(coll):
    # this will need to be done before the next time we use a multi file
    pass


def compare(_coll, expected):
    actual = list(_coll.find())
    with open("test_data/expected/" + expected) as _f:
        expected = json5.load(_f)
    assert actual == expected
