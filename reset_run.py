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
        sls=[cc.SL_COMFORT] + [cc.SL_MALCOLM],
        winrate_floor=0,
        mean_floor=-50,
        median_floor=-50,
        drawdown_limits=[-97]
    )


def run_btc_standard_reset_pts():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=[
            "data/ready_for_backtester/BYBIT_BTCUSD_1D_45m_5mTF_on_5m_11_2018.csv",
            #"data/COINBASE_BTCUSD_1D_45m_on_5m_01_2020.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_1D_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_12h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_8h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_6h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_4h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_3h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_2h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_90m_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_1h_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_45m_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_30m_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_15m_5m_on_5m_08_2021.csv",
            #"data/ready_for_analysis/BYBIT_BTCUSD_10m_5m_on_5m_08_2021.csv",
        ],
        enable_qol=False,
        #mean_floor=4,
        #median_floor=4,
        #winrate_floor=80,
        #winrate_floor=90,
        winrate_floor=60,
        drawdown_limits=[-90],
        #signal_timeframes=[["1h", "5m"]],
        #mean_floor=3,
        #median_floor=3,
        mean_floor=0,
        median_floor=0,
        #take_profits=[2],
        #stop_losses=[0.5],
        #leverages=[1],
        sls=[[[]]]
        + cc.SLS_ONE_RESET
        + cc.SLS_TWO_RESETS
        + cc.SLS_THREE_RESETS
        + cc.SLS_FOUR_RESETS
        #sls=[[[0.5, -0.25], [1.5, -0.5]]],
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
        sls=[cc.SL_MALCOLM] + [[[]]],
        #sls=[cc.SL_MALCOLM] + [cc.SL_MALCOLM_AND_A_HALF] + [cc.SL_MALCOLM_DOUBLE],
        enable_qol=True,
        signal_exits=[True, False],
        mean_floor=-100,
        median_floor=-100,
        winrate_floor=0,
        drawdown_limits=[-100]
    )


if __name__ == "__main__":
    #run_eth_reset_pts()
    #run_btc_custom_reset_pts()
    run_btc_standard_reset_pts()
