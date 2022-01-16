from backtester import main
import config_common as cc

HTF_TPS = [[1], [6]]  # these are set
LTF_TPS = [[0.3], [0.5], [4]]  # these are set
LLTF_TPS = [[0.15], [0.3], [0.5], [1]]  # these are set

# max SLs are 25 at 1x, 16 at 2x, 12 at 3x
HTF_SLS = [[11]]
LTF_SLS = [[11]]
LLTF_SLS = [[11]]

HTF_DCAS = [[[[1, 50]]], [[[3, 50]]], [[[4, 50]]]]
LTF_DCAS = LLTF_DCAS = HTF_DCAS


def generate_configs():
        TRI_TAKE_PROFIT_COMBOS = []
        for i in HTF_TPS:
            for j in LTF_TPS:
                for k in LLTF_TPS:
                    if i[0] >= j[0] and j[0] >= k[0]:
                        TRI_TAKE_PROFIT_COMBOS.append([i[0], j[0], k[0]])
        print(TRI_TAKE_PROFIT_COMBOS)

        TRI_STOP_LOSS_COMBOS = []
        for i in HTF_SLS:
            for j in LTF_SLS:
                for k in LLTF_SLS:
                    TRI_STOP_LOSS_COMBOS.append([i[0], j[0], k[0]])
        print(TRI_STOP_LOSS_COMBOS)

        TRI_DCA_COMBOS = []
        for i in HTF_DCAS:
            for j in LTF_DCAS:
                for k in LLTF_DCAS:
                    if i[0][0][0] >= j[0][0][0] and j[0][0][0] >= k[0][0][0]:
                        TRI_DCA_COMBOS.append([i[0], j[0], k[0]])
        print(TRI_DCA_COMBOS)

        return TRI_TAKE_PROFIT_COMBOS, TRI_STOP_LOSS_COMBOS, TRI_DCA_COMBOS


def run_tri_arrow(configs):
    main(
        db_coll=cc.BTC_COLL,
        datafilenames=[
            "data/ready_for_backtester/BYBIT_BTCUSD_1D_45m_5m_on_5m_01_2020.csv",
            #"data/ready_for_backtester/BYBIT_ETHUSD_1D_45m_5m_on_5m_01_2020.csv"
        ],
        enable_qol=False,
        #signal_timeframes=[["1h", "5m"]],
        take_profits=configs[0],
        tps_after_dca=configs[0],
        stop_losses=configs[1],
        dcas=configs[2],
        #leverages=[[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]],
        leverages=[[1, 1, 1]],
        replace_existing_scenarios=True,
        drawdown_limits=[-100],
        multiproc=True
    )


if __name__ == "__main__":
    configs = generate_configs()
    run_tri_arrow(configs=configs)

