import config_common as cc

CLEAR_DB = False

# every analysis of varying date must have a unique filename!  no varying start date
#   analyses on same file!  e.g. if you want to run a subset of trades for a file,
#   create a new file with the trades you want and run that
DATAFILENAMES = [
    "data/btcusd-5m_with_cols_2017_laguerre.csv"  # 4h laguerre back to 09-2017; don't rename b/c this filename uniquely identifies scenarios in db
    #"data/btcusd-5m_with_cols_2017_laguerre_4h_1D.csv",
    #"data/btcusd-5m_with_cols_2019_laguerre_4h_1D.csv",
    #"data/btcusd-5m_with_cols_2019_laguerre_1h_4h.csv"
    #"data/btcusd-5m_with_cols_2019_laguerre.csv"  #4h laguerre back to 01-2019
]
DB_CONNECTION = "mongodb://localhost:27017"
DB = "bt"
COLL = "btcoll_prod"
TAKE_PROFITS = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
STOP_LOSSES = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.1]
LEVERAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#TRAILING_SLS = [True, False]
#TRAIL_DELAYS = [True, False]
TRAILING_SLS = [False]  # should run trailing someday
TRAIL_DELAYS = [False]
#SLS = [cc.SL_0, cc.SL_1, cc.SL_2, cc.SL_3, cc.SL_7]
#SLS = [cc.SL_1]
#SLS = [cc.SL_0]
#SLS = cc.SLS_11 + cc.SLS_12 + cc.SLS_13 + cc.SLS_14  # SLS do not need wrapping [ ]
SLS = cc.ALL_4H_BEST_RESETS

#LOSS_LIMIT_FRACTIONS = [0, .1, .2, .3, .5]  # 0 means no loss limit
LOSS_LIMIT_FRACTIONS = [.2]
MULTIPROCESSING = True  # multi interferes with stepping through multiple scenarios in debug mode
#MULTIPROCESSING = False
#DRAWDOWN_LIMITS = [-20, -30, -40, -50, -80]
DRAWDOWN_LIMITS = [-50]
#DRAWDOWN_LIMITS = [-100]  # no limits
WINRATE_FLOOR = 50  # floor below which strat is invalidated
WINRATE_GRACE_PERIOD = 50  # number of trades before winrate floor is activated
WRITE_INVALID_TO_DB = True  # don't change this lol.  odd behavior
ENABLE_QOL = False
