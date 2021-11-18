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
TAKE_PROFITS = [0.3, 0.5, 1, 1.5, 2, 3, 4, 5]
STOP_LOSSES = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
LEVERAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# TRAILING_SLS = [True, False]
# TRAIL_DELAYS = [True, False]
TRAILING_SLS = [False]
TRAIL_DELAYS = [False]
TRAIL_LAST_RESETS = [False]
# SLS = [[[]]]
SLS = cc.SLS_ONE_RESET + cc.SLS_TWO_RESETS + cc.SLS_THREE_RESETS
LOSS_LIMIT_FRACTIONS = [1]
MULTIPROCESSING = True  # multi interferes with stepping through multiple scenarios in debug mode
DRAWDOWN_LIMITS = [-50]
WINRATE_FLOOR = 80
MEAN_FLOOR = 2
MEDIAN_FLOOR = 2
FLOOR_GRACE_PERIOD = 50  # number of trades before floors are activated
WRITE_INVALID_TO_DB = True  # don't change this lol.  odd behavior
ENABLE_QOL = True
REPLACE = False
ACCURACY_TESTER_MODE = False  # only runs equal TP/Sl spec; overwrites leverage, trail/delay, sls, dd, winrate floor
SIGNAL_EXITS = [True]

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
