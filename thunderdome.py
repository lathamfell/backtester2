from backtester import main
import config_common as cc


def accuracy_battle_btc():
    # all single and double timeframes from their earliest date
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=["data/COINBASE_BTCUSD_all_TFs_on_5m.csv"],
        signal_timeframes=cc.SINGLE_TIMEFRAMES + cc.DOUBLE_TIMEFRAMES,
        enable_qol=True,
        accuracy_tester_mode=True,
        take_profits=cc.ACCURACY_TEST_TPS,
        stop_losses=cc.ACCURACY_TEST_SLS,
        signal_exits=[True, False]
    )
    # each single timeframe with later start dates for comparison to lower timeframes
    for tf, start_dates in cc.COMPARISON_START_DATES.items():
        main(
            db_coll=cc.BTC_COLL,
            datafilenames=["data/COINBASE_BTCUSD_all_TFs_on_5m.csv"],
            signal_timeframes=[[tf]],
            signal_start_dates=start_dates,
            enable_qol=False,
            accuracy_tester_mode=True,
            take_profits=cc.ACCURACY_TEST_TPS,
            stop_losses=cc.ACCURACY_TEST_SLS,
            signal_exits=[True, False]
        )


def accuracy_battle_eth():
    # all single and double timeframes from their earliest date
    main(
        db_coll=cc.ETH_COLL,
        datafilenames=["data/COINBASE_ETHUSD_all_TFs_on_5m.csv"],
        signal_timeframes=cc.SINGLE_TIMEFRAMES + cc.DOUBLE_TIMEFRAMES,
        enable_qol=True,
        accuracy_tester_mode=True,
        take_profits=cc.ACCURACY_TEST_TPS,
        stop_losses=cc.ACCURACY_TEST_SLS,
        signal_exits=[True, False]
    )
    # each single timeframe with later start dates for comparison to lower timeframes
    for tf, start_dates in cc.COMPARISON_START_DATES["ETH"].items():
        main(
            db_coll=cc.ETH_COLL,
            datafilenames=["data/COINBASE_ETHUSD_all_TFs_on_5m.csv"],
            signal_timeframes=[[tf]],
            signal_start_dates=start_dates,
            enable_qol=False,
            accuracy_tester_mode=True,
            take_profits=cc.ACCURACY_TEST_TPS,
            stop_losses=cc.ACCURACY_TEST_SLS,
            signal_exits=[True, False]
        )


def reset_battle_btc():
    # all single and double TFs from their earliest date
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=["data/COINBASE_BTCUSD_all_TFs_on_5m.csv"],
        signal_timeframes=cc.SINGLE_TIMEFRAMES + cc.DOUBLE_TIMEFRAMES,
        enable_qol=False,
        take_profits=cc.RESET_TEST_TPS,
        stop_losses=cc.RESET_TEST_SLS,
        drawdown_limits=[-100],
        winrate_floor=0,
        mean_floor=-100,
        median_floor=-100,
        signal_exits=[True, False]
    )
    # each single TF with later start dates for comparison to lower TFs
    for tf, start_dates in cc.COMPARISON_START_DATES["BTC"].items():
        main(
            db_coll=cc.BTC_COLL,
            datafilenames=["data/COINBASE_BTCUSD_all_TFs_on_5m.csv"],
            signal_timeframes=[[tf]],
            signal_start_dates=start_dates,
            enable_qol=False,
            take_profits=cc.RESET_TEST_TPS,
            stop_losses=cc.RESET_TEST_SLS,
            leverages=[1],
            trailing_sls=[False],
            trail_delays=[False],
            trail_last_resets=[False],
            sls=[[[]]],
            drawdown_limits=[-100],
            winrate_floor=0,
            mean_floor=-100,
            median_floor=-100,
            signal_exits=[True, False]
        )


if __name__ == "__main__":
    accuracy_battle_eth()
    #reset_battle_btc()
