#  Default settings for production runs
#  Do not modify these often.  For runs with particular settings, use a script like thunderdome.py

import config_common as cc

CLEAR_DB = False

DATAFILENAMES = [
    "data/COINBASE_BTCUSD_1D_45m_on_5m_2020.csv"
]

SIGNAL_TIMEFRAMES = [[]]
DB_CONNECTION = "mongodb://localhost:27017"
DB = "bt"
COLL = cc.BTC_COLL
TAKE_PROFITS = [[0.15], [0.3], [0.5], [1], [2], [4], [6], [8]]
TPS_AFTER_DCA = [[0.15], [0.3], [0.5], [1], [2], [4], [6], [8]]
#TPS_AFTER_DCA = [None]  # None means TP % after DCA is same as before. Use [1, 1, 1] instead of None, e.g. [[1,1,1]] to move TP %
#STOP_LOSSES = [[2], [3], [4], [6], [8], [10]]
STOP_LOSSES = [[10]]
DCAS = [[[[0]]], [[[0.5, 50]]], [[[1, 50]]], [[[2, 50]]], [[[3, 50]]], [[[4, 50]]], [[[6, 50]]], [[[8, 50]]], [[[10, 50]]]]
DCA_WEIGHTS = [None]  # None means equal weights
LEVERAGES = [[1]]
MULTIPROCESSING = True  # multi interferes with stepping through multiple scenarios in debug mode
DRAWDOWN_LIMITS = [-50]
WINRATE_FLOOR = 90
MEAN_FLOOR = 0
MEDIAN_FLOOR = 0
FLOOR_GRACE_PERIOD = 50  # number of trades before floors are activated
WRITE_INVALID_TO_DB = True  # don't change this lol.  odd behavior
ENABLE_QOL = True
REPLACE = False
ACCURACY_TESTER_MODE = False  # only runs equal TP/Sl spec; overwrites leverage, dd, winrate floor
HTF_SIGNAL_EXITS = [True]
SIGNAL_DCAS = [False]

SIGNAL_TIMEFRAME_START_TIMES = {
    "BTC": {
        "1D": "2015-01-01T00:00:00Z",
        "12h": "2015-01-01T00:00:00Z",
        "8h": "2015-01-01T00:00:00Z",
        "6h": "2015-01-01T00:00:00Z",
        "4h": "2015-01-01T00:00:00Z",
        "3h": "2015-01-01T00:00:00Z",
        "2h": "2017-01-01T00:00:00Z",
        "90m": "2018-01-01T00:00:00Z",
        "1h": "2019-01-01T00:00:00Z",
        "45m": "2020-01-01T00:00:00Z",
        "30m": "2020-01-01T00:00:00Z",
        "15m": "2021-03-01T00:00:00Z",
        "10m": "2021-05-31T00:00:00Z",
        "5m": "2021-08-09T00:00:00Z"
    },
    "ETH": {
        "1D": "2017-12-11T00:10:00Z",
        "12h": "2017-12-11T00:10:00Z",
        "8h": "2017-12-11T00:10:00Z",
        "6h": "2017-12-11T00:10:00Z",
        "4h": "2017-12-11T00:10:00Z",
        "3h": "2017-12-11T00:10:00Z",
        "2h": "2017-12-11T00:10:00Z",
        "90m": "2018-01-01T00:00:00Z",
        "1h": "2019-01-01T00:00:00Z",
        "45m": "2020-01-01T00:00:00Z",
        "30m": "2020-01-01T00:00:00Z",
        "15m": "2021-03-01T00:00:00Z",
        "10m": "2021-06-07T00:00:00Z",
        "5m": "2021-08-16T00:00:00Z"
    }
}
