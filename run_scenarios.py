from backtester import main
import config_common as cc


def run():
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=[
            "data/ready_for_backtester/BYBIT_BTCUSD_1D_45m_5m_on_5m_01_2020.csv",
        ],
        enable_qol=False,
        #mean_floor=4,
        #median_floor=4,
        #winrate_floor=80,
        #winrate_floor=90,
        winrate_floor=60,
        drawdown_limits=[-100],
        #signal_timeframes=[["1h", "5m"]],
        #mean_floor=3,
        #median_floor=3,
        mean_floor=-100,
        median_floor=-100,
        take_profits=[[1, 0.5, 0.3]],
        stop_losses=[[10, 10, 10]],
        dcas=[[[[4, 50]], [[2, 50]], [[0.5, 50]]]],
        tps_after_dca=[[2, 1, 0.2]],
        leverages=[[5, 5, 5]],
        htf_signal_exits=[True],
        replace_existing_scenarios=True
        #multiproc=False
    )


if __name__ == "__main__":
    run()
