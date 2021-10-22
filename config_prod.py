import config_common as cc

CLEAR_DB = False

# every analysis of varying date must have a unique filename!  no varying start date
#   analyses on same file!  e.g. if you want to run a subset of trades for a file,
#   create a new file with the trades you want and run that
DATAFILENAMES = [  # these will be run
    "data/COINBASE_BTCUSD_30_2h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_30_2h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_15_2h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2019.csv",
]

DATAFILENAMES_ALL = [  # for reference
    "data/COINBASE_BTCUSD_30_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_30_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_30_2h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_30_2h_on_5m_2020.csv",
    "#data/COINBASE_BTCUSD_15_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_15_2h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_15_1h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_12h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_12h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_12h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_12h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_12h_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_8h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_8h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_8h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_8h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_8h_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_8h_1D_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_8h_1D_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_8h_1D_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_8h_1D_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_8h_1D_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_4h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_4h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_4h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_4h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_4h_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_4h_12h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_4h_12h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_4h_12h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_4h_12h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_4h_12h_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_4h_1D_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_4h_1D_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_4h_1D_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_4h_1D_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_4h_1D_on_5m_2015.csv",
    "data/COINBASE_BTCUSD_2h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_2h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_2h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_2h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_2h_8h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_2h_8h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_2h_8h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_2h_8h_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_1h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_1h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_1h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_1h_4h_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_1D_on_5m_2021.csv",
    "data/COINBASE_BTCUSD_1D_on_5m_2020.csv",
    "data/COINBASE_BTCUSD_1D_on_5m_2019.csv",
    "data/COINBASE_BTCUSD_1D_on_5m_2017.csv",
    "data/COINBASE_BTCUSD_1D_on_5m_2015.csv",
]
SIGNAL_TIMEFRAMES = [[]]
DB_CONNECTION = "mongodb://localhost:27017"
DB = "bt"
COLL = "btcoll_prod"
TAKE_PROFITS = [0.5, 1, 2, 3, 4, 5, 7.5, 10]
STOP_LOSSES = [1, 2, 3, 4, 5, 7.5]
#TF_ANALYSIS_TPS = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 5.75, 6, 6.25, 6.5, 6.75, 7, 7.25, 7.5, 7.75, 8, 8.25, 8.5, 8.75, 9, 9.25, 9.5, 9.75, 10, 10.25, 10.5, 10.75, 11, 11.25, 11.5, 11.75, 12, 12.25, 12.5, 12.75, 13, 13.25, 13.5, 13.75, 14, 14.25, 14.5, 14.75, 15, 15.25, 15.5, 15.75, 16, 16.25, 16.5, 16.75, 17, 17.25, 17.5, 17.75, 18, 18.25, 18.5, 18.75, 19, 19.25, 19.5, 19.75, 20]
#TAKE_PROFITS = TF_ANALYSIS_TPS
#STOP_LOSSES = TAKE_PROFITS
#TAKE_PROFITS = [5]
#STOP_LOSSES = [4]
LEVERAGES = [2, 3, 4, 5, 7, 10]
#LEVERAGES = [10]
#TRAILING_SLS = [True, False]
#TRAIL_DELAYS = [True, False]
TRAILING_SLS = [False]  # should run trailing someday
TRAIL_DELAYS = [False]
#SLS = [cc.SL_0, cc.SL_1, cc.SL_2, cc.SL_3, cc.SL_7]
#SLS = [cc.SL_1]
#SLS = [cc.SL_0]
#SLS = cc.SLS_11 + cc.SLS_12 + cc.SLS_13 + cc.SLS_14  # SLS do not need wrapping [ ]
#SLS = cc.ALL_4H_BEST_RESETS
#SLS = [[[]]]
SLS = cc.SLS_ONE_RESET + cc.SLS_TWO_RESETS + cc.SLS_THREE_RESETS + cc.SLS_FOUR_RESETS
LOSS_LIMIT_FRACTIONS = [0.2]
MULTIPROCESSING = True  # multi interferes with stepping through multiple scenarios in debug mode
DRAWDOWN_LIMITS = [-50]
#DRAWDOWN_LIMITS = [-100]  # no limits
WINRATE_FLOOR = 60  # floor below which strat is invalidated
WINRATE_GRACE_PERIOD = 50  # number of trades before winrate floor is activated
WRITE_INVALID_TO_DB = True  # don't change this lol.  odd behavior
ENABLE_QOL = True
REPLACE = False
ACCURACY_TESTER_MODE = False  # only runs equal TP/Sl spec; overwrites leverage, trail/delay, sls, dd, winrate floor
PURE_DELTA_MODE = False  # measures pure delta with max TP and SL; overwrites most other settings
