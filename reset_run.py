from backtester import main
import config_common as cc


def run_btc_custom_reset_pts():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=[
            "data/COINBASE_BTCUSD_1D_45m_on_5m_01_2020.csv",
        #    "data/COINBASE_BTCUSD_4h_30m_on_5m_01_2020.csv",
        #    "data/COINBASE_BTCUSD_1D_10m_on_5m_05_2021.csv"
        ],
        enable_qol=True,
        take_profits=[20, 2],
        stop_losses=[7.5],
        winrate_floor=0,
        mean_floor=-50,
        median_floor=-50,
        drawdown_limits=[-97]
    )


def run_btc_standard_reset_pts():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=[
            "data/ready_for_backtester/BYBIT_BTCUSD_1D_45m_5m_on_5m_05_2021.csv",
            #"data/ready_for_backtester/BYBIT_BTCUSD_1D_5m_on_5m_05_2021.csv",
            #"data/ready_for_backtester/BYBIT_BTCUSD_1D_45m_on_5m_01_2020.csv"
        ],
        enable_qol=False,
        #mean_floor=4,
        #median_floor=4,
        #winrate_floor=80,
        #winrate_floor=90,
        winrate_floor=0,
        drawdown_limits=[-100],
        #signal_timeframes=[["1h", "5m"]],
        #mean_floor=3,
        #median_floor=3,
        mean_floor=-100,
        median_floor=-100,
        take_profits=[0.3],
        stop_losses=[13],
        dcas=[0.5],
        leverages=[2],
        htf_signal_exits=[True],
        replace_existing_scenarios=True
        #multiproc=False
    )


def run_eth_reset_pts():
    main(
        db_coll=cc.ETH_COLL,
        datafilenames=["data/COINBASE_ETHUSD_all_TFs_on_5m.csv"],
        #signal_timeframes=[["2h", "45m"], ["90m"], ["3h", "45m"], ["8h", "45m"], ["1D", "45m"]],
        signal_timeframes=[["2h", "45m"]],
        signal_start_dates=["2020-01-01T00:00:00Z"],
        #take_profits=[2, 3, 4],
        #take_profits=[2],
        #stop_losses=[7.5, 11.25, 15],
        enable_qol=True,
        htf_signal_exits=[True, False],
        mean_floor=-100,
        median_floor=-100,
        winrate_floor=0,
        drawdown_limits=[-100]
    )


if __name__ == "__main__":
    #run_eth_reset_pts()
    #run_btc_custom_reset_pts()
    run_btc_standard_reset_pts()
