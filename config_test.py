import config_common as cc

DATAFILENAMES_1 = ["test_data/BYBITBTCUSD_240_2021_one_trade.csv"]
DATAFILENAMES_2 = ["test_data/BYBITBTCUSD_240_2021_three_trades.csv"]
DATAFILENAMES_3 = ["test_data/BYBITBTCUSD_240_2021_33_trades.csv"]
DATAFILENAMES_4 = ["test_data/BYBITBTCUSD_240_2021_five_trades.csv"]
DATAFILENAMES_5 = ["test_data/BYBITBTCUSD_15_from_09_2017_with_T3_4h.csv"]
DATAFILENAMES_6 = ["test_data/btcusd-5m_with_cols_2017_T3.csv"]
DATAFILENAMES_7 = ["test_data/btcusd-5m_with_cols_2017_T3_first_trade_removed.csv"]
DATAFILENAMES_8 = ["test_data/btcusd-5m_with_cols_2017_laguerre.csv"]
DATAFILENAMES_9 = ["test_data/btcusd-5m_with_cols_2017_laguerre_trunc.csv"]
DATAFILENAMES_10 = ["test_data/btcusd-5m_with_cols_2017_laguerre_4h_1D.csv"]
DATAFILENAMES_11 = ["test_data/BYBITBTCUSD_240_2021_one_trade_last_line_removed.csv"]
DATAFILENAMES_12 = [
    "test_data/COINBASE_BTCUSD_15_1h_on_5m_2021.csv",
    "test_data/COINBASE_BTCUSD_1h_on_5m_2021.csv"
]
DATAFILENAMES_13 = [
    "test_data/COINBASE_BTCUSD_2h_on_5m_2020.csv",
    "test_data/COINBASE_BTCUSD_15_2h_on_5m_2021.csv"
]
DATAFILENAMES_14 = [
    "test_data/COINBASE_BTCUSD_all_TFs_on_5m.csv"
]
DB_CONNECTION = "mongodb://localhost:27017"
DB = "bt"
COLL = "btcoll_test"
TAKE_PROFITS_0 = [12]
TAKE_PROFITS_1 = [2]
TAKE_PROFITS_2 = [0.5, 2]
TAKE_PROFITS_3 = [4]
TAKE_PROFITS_4 = [1]
TAKE_PROFITS_5 = [14]
STOP_LOSSES_0 = [12]
STOP_LOSSES_1 = [6]
STOP_LOSSES_2 = [1, 6]
LEVERAGES_0 = [5]
LEVERAGES_1 = [1]
LEVERAGES_2 = [2]
LEVERAGES_3 = [1, 10]
LEVERAGES_4 = [10]
SLS_0 = [cc.SL_1]
SLS_1 = [cc.SL_4]
SLS_2 = [cc.SL_5]
SLS_3 = [cc.SL_2]
SLS_4 = [cc.SL_0, cc.SL_9, cc.SL_2]
SLS_5 = [cc.SL_0, cc.SL_2]
SLS_6 = [cc.SL_0, cc.SL_1, cc.SL_2, cc.SL_3]
SLS_7 = [cc.SL_0]
SLS_8 = [cc.SL_0, cc.SL_1, cc.SL_2, cc.SL_3, cc.SL_7]
SLS_9 = [cc.SL_7]
SLS_10 = [cc.SL_10]
