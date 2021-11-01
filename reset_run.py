from backtester import main
import config_common as cc


def run_btc_custom_reset_pts():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=["data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
        enable_qol=True,
        take_profits=[8],
        sls=cc.SLS_BTC_7PCT_RESETS_ONE_RESET_NEW +
            cc.SLS_BTC_7PCT_RESETS_TWO_RESETS_NEW +
            cc.SLS_BTC_7PCT_RESETS_THREE_RESETS_NEW +
            cc.SLS_BTC_7PCT_RESETS_FOUR_RESETS_NEW +
            cc.SLS_BTC_7PCT_RESETS_FIVE_RESETS_NEW +
            cc.SLS_BTC_7PCT_RESETS_SIX_RESETS_NEW +
            cc.SLS_BTC_7PCT_RESETS_SEVEN_RESETS_NEW
    )


def run_btc_standard_reset_pts():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=["data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"],
        enable_qol=False,
        #mean_floor=4,
        #median_floor=4,
        #winrate_floor=80,
        #winrate_floor=90,
        winrate_floor=80,
        drawdown_limits=[-50],
        #mean_floor=3,
        #median_floor=3,
        mean_floor=3,
        median_floor=3,
        take_profits=[1000],
        sls=cc.SLS_ONE_RESET
        + cc.SLS_TWO_RESETS
        + cc.SLS_THREE_RESETS
        + cc.SLS_FOUR_RESETS
        + cc.SLS_FIVE_RESETS
        + cc.SLS_SIX_RESETS
    )


def run_eth_reset_pts():
    main(
        db_coll=cc.ETH_COLL,
        datafilenames=["data/COINBASE_ETHUSD_all_TFs_on_5m.csv"],
        signal_timeframes=[["2h"], ["3h"], ["1D", "2h"], ["1D", "3h"]],
        enable_qol=True,
        signal_exits=[True, False]
    )


if __name__ == "__main__":
    # run_eth_reset_pts()
    # run_btc_reset_pts()
    run_btc_standard_reset_pts()
