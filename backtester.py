import pandas as pd
import time
from multiprocessing import Pool, cpu_count
import pymongo
from statistics import mean, median, stdev
from enum import Enum
import copy
from collections import Counter

import config_prod as c
import exceptions as e

# Bybit charges 0.075% for market entry/exit; 0.075 + 0.075 = 0.15%
#   with limit exit the fee is 0.075 - 0.025 = 0.05%
BYBIT_MARKET_FEE = 0.075
BYBIT_LIMIT_FEE = -0.025

# types of exits
STOP_LOSS = "STOP_LOSS"
TAKE_PROFIT = "TAKE_PROFIT"
SIGNAL = "SIGNAL"
CPUS = cpu_count() - 2
CHUNK_SIZE = 100000


class FileType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    TRIPLE = "TRIPLE"
    MULTI = "MULTI"


class EntryTimeframe(Enum):
    HTF = "HTF"
    LTF = "LTF"
    LLTF = "LLTF"


def main(
    db_connection=c.DB_CONNECTION,
    db=c.DB,
    db_coll=c.COLL,
    datafilenames=c.DATAFILENAMES,
    signal_start_dates=[None],
    signal_timeframes=c.SIGNAL_TIMEFRAMES,
    take_profits=c.TAKE_PROFITS,
    tps_after_dca=c.TPS_AFTER_DCA,
    stop_losses=c.STOP_LOSSES,
    leverages=c.LEVERAGES,
    dcas=c.DCAS,
    drawdown_limits=c.DRAWDOWN_LIMITS,
    winrate_floor=c.WINRATE_FLOOR,
    mean_floor=c.MEAN_FLOOR,
    median_floor=c.MEDIAN_FLOOR,
    floor_grace_period=c.FLOOR_GRACE_PERIOD,
    multiproc=c.MULTIPROCESSING,
    clear_db=c.CLEAR_DB,
    write_invalid_to_db=c.WRITE_INVALID_TO_DB,
    enable_qol=c.ENABLE_QOL,  # script has things like sleep, pauses, for human interaction. Disable for testing or whatever
    replace_existing_scenarios=c.REPLACE,  # True to overwrite scenarios with matching id
    accuracy_tester_mode=c.ACCURACY_TESTER_MODE,
    htf_signal_exits=c.HTF_SIGNAL_EXITS,
    check_for_dupes_up_front=False,
):
    start_time = time.perf_counter()

    if accuracy_tester_mode:
        print(f"\nRUNNING IN ACCURACY TESTER MODE\n")
        leverages = [[1, 1, 1]]
        drawdown_limits = [-100]
        winrate_floor = 0
        mean_floor = median_floor = -100

    scenario_count = 0
    specs = []
    spec_ids = []  # used to detect dupe specs

    # db connection
    mongo = pymongo.MongoClient(db_connection)
    bt_coll = mongo[db][db_coll]
    if clear_db:
        print(
            f"Clearing db collection while leaving indexes in place. This may take some time."
        )
        bt_coll.delete_many({})

    # print(f"db connection established at {time.perf_counter() - start_time} seconds")
    # count the scenarios
    for datafilename in datafilenames:
        for signal_timeframe in signal_timeframes:
            for signal_start_date in signal_start_dates:
                for leverage in leverages:
                    for stop_loss in stop_losses:
                        for take_profit in take_profits:
                            for tp_after_dca in tps_after_dca:
                                if accuracy_tester_mode and stop_loss != take_profit:
                                    continue
                                for dca in dcas:
                                    if not dca_check(dca, stop_loss):
                                        continue
                                    for drawdown_limit in drawdown_limits:
                                        for htf_signal_exit in htf_signal_exits:
                                            scenario_count += 1
                                            print(f"{scenario_count}")
    scenario_num = 0

    print(
        f"{scenario_count} scenarios counted at {time.perf_counter() - start_time} seconds"
    )
    for datafilename in datafilenames:
        # derive characteristics from filename and load to dataframe
        try:
            datafilename_only = datafilename.split("/")[-1]
        except IndexError:
            datafilename_only = datafilename
        coin = "BTC" if "BTC" in datafilename_only else "ETH"
        df = pd.read_csv(
            filepath_or_buffer=datafilename,
            parse_dates=["time"],
            dtype={
                "short_htf": str,
                "long_htf": str,
                "short_ltf": str,
                "long_ltf": str,
            },
        )
        interval_timeframe = calculate_interval_timeframe(df=df)
        for signal_timeframe in signal_timeframes:
            file_type = get_file_type(df, signal_timeframe)
            for signal_start_date in signal_start_dates:
                start_date = get_start_date(
                    signal_start_date, file_type, df, signal_timeframe, coin
                )
                for leverage in leverages:
                    print(
                        f"assembling specs for {datafilename_only} signal timeframe {signal_timeframe} leverage {leverage}"
                    )
                    for stop_loss in stop_losses:
                        for take_profit in take_profits:
                            for tp_after_dca in tps_after_dca:
                                if accuracy_tester_mode and stop_loss != take_profit:
                                    continue
                                for dca in dcas:
                                    if not dca_check(dca, stop_loss):
                                        continue
                                    for drawdown_limit in drawdown_limits:
                                        for htf_signal_exit in htf_signal_exits:
                                            scenario_num += 1
                                            spec = {
                                                "scenario_num": scenario_num,
                                                "scenario_count": scenario_count,
                                                "datafilename": datafilename_only,
                                                "start_date": start_date,
                                                "signal_timeframe": signal_timeframe,
                                                "df": df,
                                                "interval_timeframe": interval_timeframe,
                                                "file_type": file_type,
                                                "leverage": leverage,
                                                "stop_loss": stop_loss,
                                                "take_profit": take_profit,
                                                "tp_after_dca": tp_after_dca,
                                                "dca": dca,
                                                "db": db,
                                                "db_coll": db_coll,
                                                "write_invalid_to_db": write_invalid_to_db,
                                                "drawdown_limit": drawdown_limit,
                                                "winrate_floor": winrate_floor,
                                                "mean_floor": mean_floor,
                                                "median_floor": median_floor,
                                                "floor_grace_period": floor_grace_period,
                                                "htf_signal_exit": htf_signal_exit,
                                            }
                                            spec["_id"] = get_unique_composite_key(spec)
                                            specs.append(spec)

                                            if check_for_dupes_up_front:
                                                if spec["_id"] in spec_ids:
                                                    raise ValueError(
                                                        f"spec {spec['_id']} already found"
                                                    )
                                                spec_ids.append(spec["_id"])

    print(f"specs assembled at {time.perf_counter() - start_time} seconds")

    # screen out specs already in db
    specs_not_in_db = []
    specs_in_db = []
    counter = 0
    for spec in specs:
        if scenario_in_db(bt_coll, spec["_id"]):
            specs_in_db.append(spec)
        else:
            specs_not_in_db.append(spec)
        counter += 1
        if counter % 100000 == 0:
            print(f"checked for {counter} specs in db")
    if replace_existing_scenarios:
        # drop the existing scenarios so they can be rerun; easier than trying to update them
        bt_coll.delete_many({"_id": {"$in": [spec["_id"] for spec in specs_in_db]}})
        print(f"Dropped {len(specs_in_db)} scenarios due to replace option received.")
        # now all specs are "not in db!"
        specs_not_in_db += specs_in_db

    print(
        f"{len(specs) - len(specs_not_in_db)} out of {len(specs)} are already in db, "
        f"leaving {len(specs_not_in_db)} to load."
    )
    if enable_qol:
        input("Press enter to continue")

    # print(f"specs created at {time.perf_counter() - start_time} seconds")
    total_scenarios_processed = 0
    for chunk in chunks(specs_not_in_db, CHUNK_SIZE):
        results = []
        if multiproc:
            with Pool(CPUS) as pool:
                results = pool.map(run_single_scenario, chunk)
                pool.close()
                pool.join()
        else:
            for spec in chunk:
                results.append(run_single_scenario(spec))

        print(f"\n\nloading chunk of size {len(chunk)} to db")
        if not write_invalid_to_db:
            # need to filter out the invalid results
            results = list(filter(lambda x: x["valid"], results))
        if results:
            bt_coll.insert_many(results)

        total_scenarios_processed += len(chunk)
        print(f"\n\ntotal scenarios processed so far: {total_scenarios_processed}")

    mongo.close()

    print(f"finished processing in {time.perf_counter() - start_time} seconds")
    return


def calculate_interval_timeframe(df):
    # given a pandas dataframe representing the datafile, calculate timeframe from the first two time values
    return (df.iloc[1]["time"] - df.iloc[0]["time"]).total_seconds() / 60


def get_file_type(df, signal_timeframe):
    row = df.iloc[0]
    if len(signal_timeframe) == 0:
        if row.get("short") and row.get("long"):
            return FileType.SINGLE
        if (
            row.get("short_htf")
            and row.get("long_htf")
            and row.get("short_ltf")
            and row.get("long_ltf")
            and row.get("short_lltf")
            and row.get("long_lltf")
        ):
            return FileType.TRIPLE
        if (
            row.get("short_htf")
            and row.get("long_htf")
            and row.get("short_ltf")
            and row.get("long_ltf")
        ):
            return FileType.DOUBLE
    return FileType.MULTI


def get_start_date(signal_start_date, file_type, df, signal_timeframe, coin):
    if signal_start_date:
        return signal_start_date
    if file_type in [FileType.SINGLE, FileType.DOUBLE, FileType.TRIPLE]:
        # return the first time in the file
        start_date = df.iloc[0]["time"].isoformat().replace("+00:00", "Z")
        return start_date
    if file_type == FileType.MULTI:
        if len(signal_timeframe) == 1:
            # return start date of the single timeframe
            start_date = c.SIGNAL_TIMEFRAME_START_TIMES[coin][signal_timeframe[0]]
            return start_date
        if len(signal_timeframe) == 2:
            # return start date of the LTF
            start_date = c.SIGNAL_TIMEFRAME_START_TIMES[coin][signal_timeframe[1]]
            return start_date


def scenario_in_db(coll, _id):
    return coll.count_documents({"_id": _id}, limit=1)  # 20 sec per 100k docs


def chunks(sequence, chunk_size):
    for j in range(0, len(sequence), chunk_size):
        yield sequence[j : j + chunk_size]


def run_single_scenario(spec):
    return ScenarioRunner(spec).run_scenario()


class ScenarioRunner:
    def __init__(self, spec):
        self.spec = spec
        self.stop_loss = spec["stop_loss"]
        self.long_entry_price = None
        self.short_entry_price = None
        self.entry_price_original = (
            None  # saves pre-DCA entry price, to be put into trade record
        )
        self.assets = 1.0  # main asset tracker
        self.assets_by_timeframe = {'HTF': 1.0, 'LTF': 1.0, 'LLTF': 1.0}  # track by timeframe alongside main combined asset tracker
        self.assets_by_direction = {'long': 1.0, 'short': 1.0}

        self.min_assets = self.max_assets = self.assets
        self.stop_loss_exits_in_profit = 0
        self.stop_loss_exits_at_loss = 0
        self.take_profit_exits = 0
        self.htf_signal_exits_in_profit = 0
        self.htf_signal_exits_at_loss = 0
        self.take_profit = spec["take_profit"]  # may change after DCA
        self.dca = None  # set for each trade depending on TF; mutated as each DCA point is hit
        self.profit_pct = None
        self.trade_history = []
        self.trade = {}
        self.max_drawdown_pct = self.total_profit_pct = 0
        self.total_profit_pct_by_timeframe = {'HTF': 0, 'LTF': 0, 'LLTF': 0}
        self.total_profit_pct_by_direction = {'long': 0, 'short': 0}
        self.total_candles = 0
        self.units = (
            None  # set for each trade depending on the DCA setting for that timeframe
        )
        self.tf_idx = None  # 0: HTF, 1: LTF, 2: LLTF

        self.start_date_ts = pd.to_datetime(self.spec["start_date"])

        self.end_date = (
            self.spec["df"].iloc[-1]["time"].isoformat().replace("+00:00", "Z")
        )
        # self.sl_reset_points_hit = []
        self.candles_spent_in_trade = 0

        self.price_movement_at_candle_high = self.price_movement_at_candle_low = 0
        self.max_profit = self.min_profit = 0
        self.price_movement_high = -1000
        self.price_movement_low = 1000

        self.row = None
        self.win_rate = None
        self.days = None

        #self.entry_timeframe = (
        #    ""  # for each trade, records which timeframe the entry signal fired on
        #)
        self.entry_timeframe = None
        self.htf_shadow = None  # only used in HTF dataset scenarios
        self.ltf_shadow = None  # only used in triple arrow scenarios
        self.set_initial_shadows()
        self.direction = None

    def run_scenario(self):
        # print(f"Running scenario with spec: {self.spec}")
        if not is_valid_scenario(self.spec):
            del self.spec["df"]  # no longer need it, and it doesn't print gracefully
            print(f"invalid spec: {self.spec}")
            return get_invalid_scenario_result(self.spec["_id"], self.end_date)

        for row in self.spec["df"].itertuples():
            if getattr(row, "time") < self.start_date_ts:
                continue
            self.row = row
            self.total_candles += 1
            if self.long_entry_price:
                self.candles_spent_in_trade += 1
                # get the low point of the candle
                self.price_movement_at_candle_low = (
                    (getattr(self.row, "low") / self.long_entry_price) - 1
                ) * 100
                # check for DCA
                if (
                    self.dca and self.dca[0][0] > 0
                    and (
                        self.price_movement_at_candle_low
                        <= (-1 * self.dca[0][0])
                    )
                ):
                    # update the entry price
                    self.long_entry_price = self.get_new_entry_price()
                    # recalculate price movement at candle low with new entry price
                    self.price_movement_at_candle_low = (
                        (getattr(self.row, "low") / self.long_entry_price) - 1
                    ) * 100
                    # set new tp
                    if self.spec["tp_after_dca"] is not None:
                        self.take_profit = self.spec["tp_after_dca"]
                    # allocate more units
                    self.units = round(self.units + get_dca_units(self.dca), 2)
                    # jettison the DCA point so we don't hit it again
                    del self.dca[0]
                # check for a new trade low and min profit and if so save it for later
                self.price_movement_low = min(
                    self.price_movement_low, self.price_movement_at_candle_low
                )
                if self.price_movement_low == self.price_movement_at_candle_low:
                    # new min profit for this trade
                    self.min_profit = self.get_profit_pct_from_exit_pct(
                        exit_pct=self.price_movement_low
                    )[0]
                # check for SL
                if self.price_movement_at_candle_low <= (-1 * self.stop_loss):
                    # we stopped out somewhere in this candle
                    try:
                        self.finish_trade(_type=STOP_LOSS)
                    except (e.TooMuchDrawdown, e.WinRateTooLow, e.MeanOrMedianTooLow, e.DailyProfitTooLow):
                        return self.finish_scenario(failed=True)

                # now check for the good stuff
                if self.long_entry_price:
                    # get the high point of the candle
                    self.price_movement_at_candle_high = (
                        (getattr(self.row, "high") / self.long_entry_price) - 1
                    ) * 100
                    # check for a new trade high
                    self.price_movement_high = max(
                        self.price_movement_high, self.price_movement_at_candle_high
                    )
                    if self.price_movement_high == self.price_movement_at_candle_high:
                        # new max profit for this trade: save it
                        self.max_profit = self.get_profit_pct_from_exit_pct(
                            exit_pct=self.price_movement_high
                        )[0]
                    if (
                        self.price_movement_at_candle_high
                        >= self.take_profit[self.tf_idx]
                    ):
                        # take the profit
                        try:
                            self.finish_trade(_type=TAKE_PROFIT)
                        except (
                            e.TooMuchDrawdown,
                            e.WinRateTooLow,
                            e.MeanOrMedianTooLow,
                            e.DailyProfitTooLow
                        ):
                            return self.finish_scenario(failed=True)

                # check if we need to exit our long due to a signal
                if self.spec["htf_signal_exit"] and self.should_close_long():
                    # exit long
                    try:
                        self.finish_trade(_type=SIGNAL)
                    except (e.TooMuchDrawdown, e.WinRateTooLow, e.MeanOrMedianTooLow, e.DailyProfitTooLow):
                        return self.finish_scenario(failed=True)

            if self.short_entry_price:
                self.candles_spent_in_trade += 1
                # get the high point of the candle
                self.price_movement_at_candle_high = (
                    (getattr(self.row, "high") / self.short_entry_price) - 1
                ) * 100

                # check for DCA - loop through each remaining DCA step
                for dca_pct in self.dca:
                    if (
                        dca_pct and dca_pct[0] > 0
                        and (self.price_movement_at_candle_high >= dca_pct[0])
                    ):
                        # update the entry price
                        self.short_entry_price = self.get_new_entry_price()
                        # recalculate price movement at candle high with new entry price
                        self.price_movement_at_candle_high = (
                            (getattr(self.row, "high") / self.short_entry_price) - 1
                        ) * 100
                        # set new tp
                        if self.spec["tp_after_dca"] is not None:
                            self.take_profit = self.spec["tp_after_dca"]
                        # allocate more units
                        self.units = round(self.units + get_dca_units(self.dca), 2)
                        # jettison the DCA point so we don't hit it again
                        del self.dca[0]
                # check for new trade high (i.e. new min profit in a short)
                self.price_movement_high = max(
                    self.price_movement_high, self.price_movement_at_candle_high
                )
                if self.price_movement_high == self.price_movement_at_candle_high:
                    # new min profit for this trade
                    self.min_profit = self.get_profit_pct_from_exit_pct(
                        exit_pct=(-1 * self.price_movement_high)
                    )[0]
                # check for SL
                if self.price_movement_at_candle_high >= self.stop_loss:
                    # we stopped out somewhere in this candle
                    try:
                        self.finish_trade(_type=STOP_LOSS)
                    except (e.TooMuchDrawdown, e.WinRateTooLow, e.MeanOrMedianTooLow, e.DailyProfitTooLow):
                        return self.finish_scenario(failed=True)

                # now check for the good stuff
                if self.short_entry_price:
                    # get the low point of the candle
                    self.price_movement_at_candle_low = (
                        (getattr(self.row, "low") / self.short_entry_price) - 1
                    ) * 100
                    # check for a new trade low (i.e. new max profit in a short)
                    self.price_movement_low = min(
                        self.price_movement_low, self.price_movement_at_candle_low
                    )
                    if self.price_movement_low == self.price_movement_at_candle_low:
                        # new max profit for this trade
                        self.max_profit = self.get_profit_pct_from_exit_pct(
                            exit_pct=(-1 * self.price_movement_low)
                        )[0]
                    if self.price_movement_at_candle_low <= (
                        self.take_profit[self.tf_idx] * -1
                    ):
                        # take the profit
                        try:
                            self.finish_trade(_type=TAKE_PROFIT)
                        except (
                            e.TooMuchDrawdown,
                            e.WinRateTooLow,
                            e.MeanOrMedianTooLow,
                            e.DailyProfitTooLow
                        ):
                            return self.finish_scenario(failed=True)
                    else:
                        # we didn't TP yet, but check if we hit a reset point
                        # self.check_reset_points(self.price_movement_at_candle_low)
                        pass

                # check if need to exit our short due to a signal
                if self.spec["htf_signal_exit"] and self.should_close_short():
                    try:
                        self.finish_trade(_type=SIGNAL)
                    except (e.TooMuchDrawdown, e.WinRateTooLow, e.MeanOrMedianTooLow, e.DailyProfitTooLow):
                        return self.finish_scenario(failed=True)

            # check for long entry
            if self.should_open_long():
                self.tf_idx = get_tf_idx(self.entry_timeframe)
                self.long_entry_price = self.entry_price_original = getattr(
                    self.row, "close"
                )
                self.direction = "long"
                # reset tp and stop_loss to starting value
                self.take_profit = self.spec["take_profit"]
                self.stop_loss = self.spec["stop_loss"][self.tf_idx]
                self.profit_pct = None
                self.candles_spent_in_trade = 0

                self.price_movement_at_candle_high = (
                    self.price_movement_at_candle_low
                ) = 0
                self.max_profit = self.min_profit = 0
                self.price_movement_high = -1000
                self.price_movement_low = 1000
                self.dca = copy.deepcopy(self.spec["dca"][self.tf_idx])  # get DCA fresh for this trade
                # allocate units as a fraction of 1, depending how many DCA pts there are
                self.units = get_dca_units(self.dca, first_entry=True)

                self.trade = {
                    "entry": getattr(self.row, "time")
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "direction": self.direction,
                    "entry_timeframe": self.entry_timeframe,
                }

            # check for short entry
            if self.should_open_short():
                self.tf_idx = get_tf_idx(self.entry_timeframe)
                self.short_entry_price = self.entry_price_original = getattr(
                    self.row, "close"
                )
                self.direction = "short"
                # reset stop_loss to starting value
                self.take_profit = self.spec["take_profit"]
                self.stop_loss = self.spec["stop_loss"][self.tf_idx]
                self.profit_pct = None
                self.candles_spent_in_trade = 0

                self.price_movement_at_candle_high = (
                    self.price_movement_at_candle_low
                ) = 0
                self.max_profit = self.min_profit = 0
                self.price_movement_high = -1000
                self.price_movement_low = 1000
                self.dca = copy.deepcopy(self.spec["dca"][self.tf_idx])  # get DCA fresh for this trade
                # allocate units as a fraction of 1, depending how many DCA pts there are
                self.units = get_dca_units(self.dca, first_entry=True)

                self.trade = {
                    "entry": getattr(self.row, "time")
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "direction": self.direction,
                    "entry_timeframe": self.entry_timeframe,
                }

        return self.finish_scenario()

    def set_initial_shadows(self):
        if self.spec["file_type"] == FileType.SINGLE or (
            self.spec["file_type"] == FileType.MULTI
            and self.spec["signal_timeframe"] == 1
        ):
            # no need for initial shadow with single timeframes
            return
        if self.spec["file_type"] == FileType.MULTI:
            raise Exception(
                "Backtester needs update to 'check_for_initial_shadow' to handle multi files with multiple TFs"
            )
        row = self.spec["df"].iloc[0]
        if self.spec["file_type"] in [FileType.DOUBLE, FileType.TRIPLE]:
            if not (
                (row["short_htf"] in ["shadow", 1, "1"])
                ^ (row["long_htf"] in ["shadow", 1, "1"])
            ):
                raise Exception(
                    f"Double or triple arrow file {self.spec['datafilename']} provided without proper initial HTF shadow"
                )
            if row["short_htf"] in ["shadow", 1, "1"]:
                self.htf_shadow = "short"
            if row["long_htf"] in ["shadow", 1, "1"]:
                self.htf_shadow = "long"

        if self.spec["file_type"] == FileType.TRIPLE:
            # for triple arrow files, also set LTF shadow
            if not (
                (row["short_ltf"] in ["shadow", 1, "1"])
                ^ (row["long_ltf"] in ["shadow", 1, "1"])
            ):
                raise Exception(
                    f"Triple arrow file {self.spec['datafilename']} provided without proper initial LTF shadow"
                )
            if row["short_ltf"] in ["shadow", 1, "1"]:
                self.ltf_shadow = "short"
            if row["long_ltf"] in ["shadow", 1, "1"]:
                self.ltf_shadow = "long"

    def should_close_short(self):
        if self.spec["file_type"] == FileType.SINGLE:
            return self.should_close_short_single_timeframe(long_header="long")
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 1
        ):
            return self.should_close_short_single_timeframe(
                long_header=f"long_{self.spec['signal_timeframe'][0]}"
            )

        if self.spec["file_type"] in [FileType.DOUBLE, FileType.TRIPLE]:
            return self.should_close_short_double_or_triple_timeframe(
                long_htf_header="long_htf"
            )
        if self.spec["file_type"] == FileType.MULTI:
            return self.should_close_short_double_or_triple_timeframe(
                long_htf_header=f"long_{self.spec['signal_timeframe'][0]}"
            )

    def should_close_short_single_timeframe(self, long_header):
        bot_in_short = self.short_entry_price
        long_signal = getattr(self.row, long_header) in [1, "1"]
        return bot_in_short and long_signal

    def should_close_short_double_or_triple_timeframe(self, long_htf_header):
        bot_in_short = self.short_entry_price
        opposing_htf_signal = getattr(self.row, long_htf_header) in [1, "1"]
        return bot_in_short and opposing_htf_signal

    def should_close_long(self):
        if self.spec["file_type"] == FileType.SINGLE:
            return self.should_close_long_single_timeframe(short_header="short")
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 1
        ):
            return self.should_close_long_single_timeframe(
                short_header=f"short_{self.spec['signal_timeframe'][0]}"
            )

        if self.spec["file_type"] in [FileType.DOUBLE, FileType.TRIPLE]:
            return self.should_close_long_double_or_triple_timeframe(
                short_htf_header="short_htf"
            )
        if self.spec["file_type"] == FileType.MULTI:
            return self.should_close_long_double_or_triple_timeframe(
                short_htf_header=f"short_{self.spec['signal_timeframe'][0]}"
            )

    def should_close_long_single_timeframe(self, short_header):
        bot_in_long = self.long_entry_price
        short_signal = getattr(self.row, short_header) in [1, "1"]
        return bot_in_long and short_signal

    def should_close_long_double_or_triple_timeframe(self, short_htf_header):
        bot_in_long = self.long_entry_price
        opposing_htf_signal = getattr(self.row, short_htf_header) in [1, "1"]
        return bot_in_long and opposing_htf_signal

    def should_open_short(self):
        if self.spec["file_type"] == FileType.SINGLE:
            return self.should_open_short_single_timeframe(short_header="short")
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 1
        ):
            return self.should_open_short_single_timeframe(
                short_header=f"short_{self.spec['signal_timeframe'][0]}"
            )
        if self.spec["file_type"] == FileType.DOUBLE:
            return self.should_open_short_double_timeframe(
                short_htf_header="short_htf",
                short_ltf_header="short_ltf",
                long_htf_header="long_htf",
            )
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 2
        ):
            return self.should_open_short_double_timeframe(
                short_htf_header=f"short_{self.spec['signal_timeframe'][0]}",
                short_ltf_header=f"short_{self.spec['signal_timeframe'][1]}",
                long_htf_header=f"long_{self.spec['signal_timeframe'][0]}",
            )
        if self.spec["file_type"] == FileType.TRIPLE:
            return self.should_open_short_triple_timeframe(
                short_htf_header="short_htf",
                short_ltf_header="short_ltf",
                short_lltf_header="short_lltf",
                long_htf_header="long_htf",
                long_ltf_header="long_ltf",
            )

    def should_open_short_single_timeframe(self, short_header):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        short_signal = getattr(self.row, short_header) in [1, "1"]
        self.entry_timeframe = EntryTimeframe.HTF.name
        if not bot_in_trade and short_signal:
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        return False

    def should_open_short_double_timeframe(
        self, short_htf_header, short_ltf_header, long_htf_header
    ):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        htf_signal = getattr(self.row, short_htf_header) in [1, "1"]
        ltf_signal = getattr(self.row, short_ltf_header) in [1, "1"]
        opposing_htf_signal = getattr(self.row, long_htf_header) in [1, "1"]
        if htf_signal:
            self.htf_shadow = "short"
        if htf_signal and not bot_in_trade:  # should_close_short() already called
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        if (
            ltf_signal
            and self.htf_shadow == "short"
            and not bot_in_trade
            and not opposing_htf_signal
        ):
            self.entry_timeframe = EntryTimeframe.LTF.name
            return True
        return False

    def should_open_short_triple_timeframe(
        self,
        short_htf_header,
        short_ltf_header,
        short_lltf_header,
        long_htf_header,
        long_ltf_header,
    ):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        htf_signal = getattr(self.row, short_htf_header) in [1, "1"]
        ltf_signal = getattr(self.row, short_ltf_header) in [1, "1"]
        lltf_signal = getattr(self.row, short_lltf_header) in [1, "1"]
        opposing_htf_signal = getattr(self.row, long_htf_header) in [1, "1"]
        opposing_ltf_signal = getattr(self.row, long_ltf_header) in [1, "1"]
        # always switch the shadow if there is a signal
        if htf_signal:
            self.htf_shadow = "short"
        if ltf_signal:
            self.ltf_shadow = "short"

        if htf_signal and not bot_in_trade:  # should_close_short() already called
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        if (
            ltf_signal
            and self.htf_shadow == "short"
            and not bot_in_trade
            and not opposing_htf_signal
        ):
            self.entry_timeframe = EntryTimeframe.LTF.name
            return True
        if (
            lltf_signal
            and self.htf_shadow == "short"
            and self.ltf_shadow == "short"
            and not bot_in_trade
            and not opposing_htf_signal
            and not opposing_ltf_signal
        ):
            self.entry_timeframe = EntryTimeframe.LLTF.name
            return True
        return False

    def should_open_long(self):
        if self.spec["file_type"] == FileType.SINGLE:
            return self.should_open_long_single_timeframe(long_header="long")
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 1
        ):
            return self.should_open_long_single_timeframe(
                long_header=f"long_{self.spec['signal_timeframe'][0]}"
            )
        if self.spec["file_type"] == FileType.DOUBLE:
            return self.should_open_long_double_timeframe(
                long_htf_header="long_htf",
                long_ltf_header="long_ltf",
                short_htf_header="short_htf",
            )
        if (
            self.spec["file_type"] == FileType.MULTI
            and len(self.spec["signal_timeframe"]) == 2
        ):
            return self.should_open_long_double_timeframe(
                long_htf_header=f"long_{self.spec['signal_timeframe'][0]}",
                long_ltf_header=f"long_{self.spec['signal_timeframe'][1]}",
                short_htf_header=f"short_{self.spec['signal_timeframe'][0]}",
            )
        if self.spec["file_type"] == FileType.TRIPLE:
            return self.should_open_long_triple_timeframe(
                long_htf_header="long_htf",
                long_ltf_header="long_ltf",
                long_lltf_header="long_lltf",
                short_htf_header="short_htf",
                short_ltf_header="short_ltf",
            )

    def should_open_long_single_timeframe(self, long_header):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        long_signal = getattr(self.row, long_header) in [1, "1"]
        if not bot_in_trade and long_signal:
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        return False

    def should_open_long_double_timeframe(
        self, long_htf_header, long_ltf_header, short_htf_header
    ):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        htf_signal = getattr(self.row, long_htf_header) in [1, "1"]
        ltf_signal = getattr(self.row, long_ltf_header) in [1, "1"]
        opposing_htf_signal = getattr(self.row, short_htf_header) in [1, "1"]
        if htf_signal:
            self.htf_shadow = "long"
        if htf_signal and not bot_in_trade:  # should_close_long() already called
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        if (
            ltf_signal
            and self.htf_shadow == "long"
            and not bot_in_trade
            and not opposing_htf_signal
        ):
            self.entry_timeframe = EntryTimeframe.LTF.name
            return True
        return False

    def should_open_long_triple_timeframe(
        self,
        long_htf_header,
        long_ltf_header,
        long_lltf_header,
        short_htf_header,
        short_ltf_header,
    ):
        bot_in_trade = self.short_entry_price or self.long_entry_price
        htf_signal = getattr(self.row, long_htf_header) in [1, "1"]
        ltf_signal = getattr(self.row, long_ltf_header) in [1, "1"]
        lltf_signal = getattr(self.row, long_lltf_header) in [1, "1"]
        opposing_htf_signal = getattr(self.row, short_htf_header) in [1, "1"]
        opposing_ltf_signal = getattr(self.row, short_ltf_header) in [1, "1"]
        # always switch the shadow if there is a signal
        if htf_signal:
            self.htf_shadow = "long"
        if ltf_signal:
            self.ltf_shadow = "long"

        if htf_signal and not bot_in_trade:  # should_close_short() already called
            self.entry_timeframe = EntryTimeframe.HTF.name
            return True
        if (
            ltf_signal
            and self.htf_shadow == "long"
            and not bot_in_trade
            and not opposing_htf_signal
        ):
            self.ltf_shadow = "long"
            self.entry_timeframe = EntryTimeframe.LTF.name
            return True
        if (
            lltf_signal
            and self.htf_shadow == "long"
            and self.ltf_shadow == "long"
            and not bot_in_trade
            and not opposing_htf_signal
            and not opposing_ltf_signal
        ):
            self.entry_timeframe = EntryTimeframe.LLTF.name
            return True
        return False

    def get_profit_pct_from_exit_price(self, exit_price):
        # takes an exit price like 34,001 and returns profit pct after fees and leverage
        # this only happens on signal exits
        dcas_hit = len(self.spec["dca"][self.tf_idx]) - len(self.dca)
        exit_pct = None
        if self.long_entry_price:
            exit_pct = ((exit_price / self.long_entry_price) - 1) * 100
        elif self.short_entry_price:
            exit_pct = ((exit_price / self.short_entry_price) - 1) * -100
        if dcas_hit > 0:
            # signal exit incurs market fee
            # entry market/limit fee split depends on proportion of DCA entries
            fees = BYBIT_MARKET_FEE / (dcas_hit + 1) + ((BYBIT_LIMIT_FEE * dcas_hit) / (dcas_hit + 1)) + BYBIT_MARKET_FEE
        elif dcas_hit == 0:
            # DCA wasn't configured or wasn't activated
            fees = BYBIT_MARKET_FEE * 2
        else:
            raise Exception(
                "Unexpected exit configuration encountered in get_profit_pct_from_exit_price"
            )
        profit_pct = (
            exit_pct * self.spec["leverage"][self.tf_idx] - fees * self.spec["leverage"][self.tf_idx]
        )
        return profit_pct, exit_pct

    def get_profit_pct_from_exit_pct(self, exit_pct, exit_type=None):
        # takes an exit price based profit pct like 2% and returns final profit pct after fees and leverage
        dcas_hit = len(self.spec["dca"][self.tf_idx]) - len(self.dca)
        exit_pct = min(
            exit_pct, self.take_profit[self.tf_idx]
        )  # cut off anything beyond TP
        exit_pct = max(
            exit_pct, -1 * self.spec["stop_loss"][self.tf_idx]
        )  # cut off anything below SL
        if not exit_type:
            # don't include fees, we are just tracking profit as it would look if we were staring at live trade in ByBit
            fees = 0
        elif exit_type == TAKE_PROFIT and dcas_hit > 0:
            # TP, and DCA was activated
            fees = BYBIT_MARKET_FEE / (dcas_hit + 1) + ((BYBIT_LIMIT_FEE * dcas_hit) / (dcas_hit + 1)) + BYBIT_LIMIT_FEE
        elif exit_type == TAKE_PROFIT and dcas_hit == 0:
            # TP and DCA wasn't configured, or wasn't activated
            fees = BYBIT_MARKET_FEE + BYBIT_LIMIT_FEE
        elif exit_type in [STOP_LOSS, SIGNAL] and dcas_hit > 0:
            # non-TP exit, but DCA was activated
            fees = BYBIT_MARKET_FEE / (dcas_hit + 1) + ((BYBIT_LIMIT_FEE * dcas_hit) / (dcas_hit + 1)) + BYBIT_MARKET_FEE
        elif exit_type in [STOP_LOSS, SIGNAL] and dcas_hit == 0:
            # non-TP exit, and DCA wasn't configured or wasn't activated
            fees = BYBIT_MARKET_FEE * 2
        else:
            raise Exception(
                "Unexpected exit configuration encountered in get_profit_pct_from_exit_pct"
            )
        profit_pct = (
            exit_pct * self.spec["leverage"][self.tf_idx] - fees * self.spec["leverage"][self.tf_idx]
        )
        return profit_pct, exit_pct

    def get_exit_price_from_exit_pct(self, exit_pct):
        # take an exit pct like -2% and returns exit price based on direction and entry price
        if self.long_entry_price:
            return round(self.long_entry_price * (1 + exit_pct / 100), 1)
        if self.short_entry_price:
            return round(self.short_entry_price * (1 - exit_pct / 100), 1)

    def finish_trade(self, _type):
        exit_type = None
        exit_pct = None
        exit_price = None
        if _type == STOP_LOSS:
            self.profit_pct, exit_pct = self.get_profit_pct_from_exit_pct(
                exit_pct=(-1 * self.stop_loss), exit_type=_type
            )
            exit_price = self.get_exit_price_from_exit_pct(
                exit_pct=(-1 * self.stop_loss)
            )
            exit_type = "sl_loss"

        elif _type == TAKE_PROFIT:
            self.profit_pct, exit_pct = self.get_profit_pct_from_exit_pct(
                exit_pct=self.take_profit[self.tf_idx], exit_type=_type
            )
            exit_price = self.get_exit_price_from_exit_pct(
                exit_pct=self.take_profit[self.tf_idx]
            )
            exit_type = "tp"

        elif _type == SIGNAL:
            exit_price = getattr(self.row, "close")
            self.profit_pct, exit_pct = self.get_profit_pct_from_exit_price(
                exit_price=exit_price
            )
            if self.profit_pct > 0:
                exit_type = "sig_profit"
            else:
                exit_type = "sig_loss"

        self.assets *= (1 + self.profit_pct / 100 * self.units)
        self.assets_by_timeframe[self.entry_timeframe] *= (1 + self.profit_pct / 100 * self.units)  # track TF profit
        self.assets_by_direction[self.direction] *= (1 + self.profit_pct / 100 * self.units)  # track direction profit

        self.min_assets = min(self.assets, self.min_assets)
        self.max_assets = max(self.assets, self.max_assets)
        drawdown_pct = round(
            (1 - (self.assets / self.max_assets)) * -100, 1
        )  # e.g. -68 (=68% drawdown from peak)
        self.max_drawdown_pct = min(drawdown_pct, self.max_drawdown_pct)
        self.total_profit_pct = round((self.assets - 1) * 100, 1)  # e.g. 103 (=103% profit)
        self.total_profit_pct_by_timeframe[self.entry_timeframe] = round((self.assets_by_timeframe[self.entry_timeframe] - 1) * 100, 1)
        self.total_profit_pct_by_direction[self.direction] = round((self.assets_by_direction[self.direction] - 1) * 100, 1)

        # update trade history
        self.trade["entry_price_dca"] = round(self.short_entry_price if self.short_entry_price else self.long_entry_price, 2)
        self.trade["entry_price_original"] = self.entry_price_original
        self.trade["exit_price"] = exit_price
        self.trade["exit"] = (
            getattr(self.row, "time").isoformat().replace("+00:00", "Z")
        )
        self.trade["exit_pct"] = round(exit_pct, 3)
        self.trade["final_profit"] = round(self.profit_pct, 3)
        self.trade["duration_hours"] = round(self.candles_spent_in_trade * self.spec["interval_timeframe"] / 60, 1)
        self.trade["assets"] = round(self.assets, 4)
        self.trade["leverage"] = self.spec["leverage"][self.tf_idx]
        self.trade["exit_type"] = exit_type
        self.trade["min_profit_before_fees"] = round(self.min_profit, 3)
        self.trade["max_profit_before_fees"] = round(self.max_profit, 3)
        self.trade["units"] = self.units
        self.trade_history.append(self.trade)
        self.entry_timeframe = self.direction = None  # ensure no carryover to the next trade

        # check drawdown
        if self.max_drawdown_pct < self.spec["drawdown_limit"]:
            raise e.TooMuchDrawdown

        # check floors
        if len(self.trade_history) >= self.spec["floor_grace_period"]:
            self.calculate_win_rate()
            if self.win_rate < self.spec["winrate_floor"]:
                raise e.WinRateTooLow
            mean_profit = mean(self.get_profits())
            if mean_profit < self.spec["mean_floor"]:
                raise e.MeanOrMedianTooLow
            median_profit = median(self.get_profits())
            if median_profit < self.spec["median_floor"]:
                raise e.MeanOrMedianTooLow

        # clear both prices for convenience, even though only one is set
        self.short_entry_price = self.long_entry_price = self.tf_idx = None

    def finish_scenario(self, failed=False):

        mean_profit = median_profit = mean_hrs_in_trade_htf = mean_hrs_in_trade_ltf = mean_hrs_in_trade_lltf = None
        self.calculate_daily_profit_pct_avg()
        if len(self.trade_history) > 0:
            self.calculate_win_rate()
            mean_profit = round(mean(self.get_profits()), 2)
            median_profit = round(median(self.get_profits()), 2)
            durations = self.get_durations()
            if len(durations['HTF']):
                mean_hrs_in_trade_htf = round(mean(durations['HTF']), 1)
            if len(durations['LTF']):
                mean_hrs_in_trade_ltf = round(mean(durations['LTF']), 1)
            if len(durations['LLTF']):
                mean_hrs_in_trade_lltf = round(mean(durations['LLTF']), 1)

        del self.spec["df"]  # no longer need it, and it doesn't print gracefully
        if failed:
            print(f"failed strat {self.spec}")
        else:
            print(
                f"{self.daily_profit_pct_avg:1.2f} {len(self.trade_history):3} daily profit/trades from spec: {self.spec}"
            )

        result = {
            "_id": self.spec["_id"],
            "end_date": self.trade_history[-1]["exit"],
            "trade_history": self.trade_history,
            "htf_profit_pct": self.total_profit_pct_by_timeframe[EntryTimeframe.HTF.name],
            "ltf_profit_pct": self.total_profit_pct_by_timeframe[EntryTimeframe.LTF.name],
            "lltf_profit_pct": self.total_profit_pct_by_timeframe[EntryTimeframe.LLTF.name],
            "short_profit_pct": self.total_profit_pct_by_direction["short"],
            "long_profit_pct": self.total_profit_pct_by_direction["long"],
            "total_profit_pct": self.total_profit_pct,
            "daily_profit_pct_avg": self.daily_profit_pct_avg,
            "max_drawdown_pct": self.max_drawdown_pct,
            "win_rate": self.win_rate,
            "trades": len(self.trade_history),
            "stop_loss_exits_in_profit": self.get_exit_type_count("sl_profit"),
            "stop_loss_exits_at_loss": self.get_exit_type_count("sl_loss"),
            "take_profit_exits": self.get_exit_type_count("tp"),
            "htf_signal_exits_in_profit": self.get_exit_type_count("sig_profit"),
            "htf_signal_exits_at_loss": self.get_exit_type_count("sig_loss"),
            "mean_profit": mean_profit,
            "median_profit": median_profit,
            "mean * trades": round(mean_profit * len(self.trade_history), 2),
            "days": self.days,
            "mean_hrs_in_trade_htf": mean_hrs_in_trade_htf,
            "mean_hrs_in_trade_ltf": mean_hrs_in_trade_ltf,
            "mean_hrs_in_trade_lltf": mean_hrs_in_trade_lltf,
            "valid": not failed,
            "final_assets": round(self.assets, 2),
            "min_assets": round(self.min_assets, 2),
            "max_assets": round(self.max_assets, 2)
        }

        return result

    def calculate_win_rate(self):
        self.win_rate = round(
            (len(self.get_positive_profits()) / len(self.get_durations()['all']) * 100), 1
        )

    def calculate_days(self):
        minutes = self.total_candles * int(self.spec["interval_timeframe"])
        self.days = round(minutes / 1440, 1)

    def calculate_daily_profit_pct_avg(self):
        self.calculate_days()
        self.daily_profit_pct_avg = round((self.assets ** (1 / float(self.days)) - 1) * 100, 2)

    def get_positive_profits(self):
        return [
            trade["final_profit"]
            for trade in self.trade_history
            if trade["final_profit"] > 0
        ]

    def get_profits(self):
        return [trade["final_profit"] for trade in self.trade_history]

    def get_exit_type_count(self, exit_type):
        return len(
            [
                trade["exit_type"]
                for trade in self.trade_history
                if trade["exit_type"] == exit_type
            ]
        )

    def get_durations(self):
        durations = {
            'HTF': [trade["duration_hours"] for trade in self.trade_history if trade['entry_timeframe'] == 'HTF'],
            'LTF': [trade["duration_hours"] for trade in self.trade_history if trade['entry_timeframe'] == 'LTF'],
            'LLTF': [trade["duration_hours"] for trade in self.trade_history if trade['entry_timeframe'] == 'LLTF'],
            'all': [trade["duration_hours"] for trade in self.trade_history]}
        return durations

    def get_new_entry_price(self):
        cur_entry_price = self.short_entry_price if self.short_entry_price else self.long_entry_price
        sign = 1 if self.short_entry_price else -1
        dca_entry_price = cur_entry_price * (1 + sign * self.dca[0][0] / 100)
        total_units = self.units + self.dca[0][1] / 100
        new_entry_price = ((cur_entry_price * self.units) + (dca_entry_price * self.dca[0][1] / 100)) / total_units
        return new_entry_price


def is_valid_scenario(spec):
    protected = False
    drawdown_valid = False
    # a valid scenario is protected from liquidation
    for i, tf_sl in enumerate(spec["stop_loss"]):
        if tf_sl / 100 < (1 / (1 + spec["leverage"][i])):
            protected = True
        # a valid scenario is protected from hitting drawdown limit in a single trade
        if -1 * (tf_sl * spec["leverage"][i]) >= spec["drawdown_limit"]:
            drawdown_valid = True

        if not (protected and drawdown_valid):
            return False
    return True


def get_unique_composite_key(spec):
    unique_composite_key = {
        "datafilename": spec["datafilename"],
        "start_date": spec["start_date"],
        "signal_timeframe": spec["signal_timeframe"],
        "leverage": spec["leverage"],
        "stop_loss": spec["stop_loss"],
        "take_profit": spec["take_profit"],
        "tp_after_dca": spec["tp_after_dca"],
        "dca": spec["dca"],
        "drawdown_limit": spec["drawdown_limit"],
        "winrate_floor": spec["winrate_floor"],
        "median_floor": spec["median_floor"],
        "mean_floor": spec["mean_floor"],
        "floor_grace_period": spec["floor_grace_period"],
        "htf_signal_exit": spec["htf_signal_exit"],
    }
    return unique_composite_key


def get_invalid_scenario_result(_id, end_date):
    result = {
        "_id": _id,
        "end_date": end_date,
        "trade_history": None,
        "total_profit_pct": None,
        "daily_profit_pct_avg": None,
        "max_drawdown_pct": None,
        "win_rate": None,
        "trades": None,
        "stop_loss_exits_in_profit": None,
        "stop_loss_exits_at_loss": None,
        "take_profit_exits": None,
        "htf_signal_exits_in_profit": None,
        "htf_signal_exits_at_loss": None,
        "mean_profit": None,
        "median_profit": None,
        "days": None,
        "mean_hrs_in_trade_htf": None,
        "mean_hrs_in_trade_ltf": None,
        "mean_hrs_in_trade_lltf": None,
        "valid": False,
        "final_assets": None,
        "min_assets": None,
        "max_assets": None,
    }
    return result


def get_tf_idx(tf):
    if tf == "HTF":
        return 0
    elif tf == "LTF":
        return 1
    elif tf == "LLTF":
        return 2
    else:
        raise ValueError(f"Improper argument {tf} passed to get_tf_idx")


def dca_check(dca, stop_loss):
    for i, tf_dcas in enumerate(dca):
        for dca_pct in tf_dcas:
            # make sure we don't have a DCA set at stop loss or beyond
            if dca_pct[0] >= stop_loss[i]:
                return False
        # make sure the DCA pcts are in increasing order
        for j in range(1, len(tf_dcas)):
            assert tf_dcas[j - 1][0] < tf_dcas[j][0], f"DCA points {tf_dcas} are not monotonically increasing"
        # make sure the weights do not exceed 99 (leaving at least 1% for entry weight)
        total_dca_weight = 0
        for dca in tf_dcas:
            if not dca[0]:  # no DCA configured for this TF
                continue
            total_dca_weight += dca[1]
        assert total_dca_weight < 100, f"DCA weights in {tf_dcas} are too high"
    return True


def get_dca_units(dca, first_entry=False):
    # the number of units allocated to each DCA entry
    if not dca[0][0]:  # no DCA configured, go all in at entry
        return 1.0
    if first_entry:
        # calculate weight of first entry based on the other weights
        total_dca_weight = 0
        for dca_pt in dca:
            total_dca_weight += dca_pt[1]
        entry_weight = 100 - total_dca_weight
        return round(entry_weight / 100, 2)
    return round(dca[0][1] / 100, 2)


if __name__ == "__main__":
    print("running main")
    main()
