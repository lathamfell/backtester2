import pandas as pd
import time
from multiprocessing import Pool, cpu_count
import pymongo
from statistics import mean, median
import re
from time import sleep

import config_prod as c
import config_common as cc
import exceptions as e

FEES = 0.0015  # Bybit charges 0.075% for market entry/exit
# types of exits
STOP_LOSS = "STOP_LOSS"
TAKE_PROFIT = "TAKE_PROFIT"
SIGNAL = "SIGNAL"
CPUS = cpu_count() - 2
CHUNK_SIZE = 1000000

# valid combinations of trail_sl and trail_delay are:
# 1. T T: trailing with delay
# 2. T F: trailing without delay
# 3. F F: no trailing
VALID_TRAIL_CONFIGS = [(True, True), (True, False), (False, False)]

QUICK_RUN = False  # configure below; will print after run


def main(
    db_connection=c.DB_CONNECTION,
    db=c.DB,
    db_coll=c.COLL,
    datafilenames=c.DATAFILENAMES,
    take_profits=c.TAKE_PROFITS,
    stop_losses=c.STOP_LOSSES,
    leverages=c.LEVERAGES,
    trailing_sls=c.TRAILING_SLS,
    trail_delays=c.TRAIL_DELAYS,
    reenter_on_new_signal=False,  # only relevant for HTF arrow sets
    signal_exits_only=False,  # True to ignore TP/SL & only exit on signals (useful for alpha runs...and more?)
    sls=c.SLS,
    loss_limit_fractions=c.LOSS_LIMIT_FRACTIONS,
    drawdown_limits=c.DRAWDOWN_LIMITS,
    winrate_floor=c.WINRATE_FLOOR,
    winrate_grace_period=c.WINRATE_GRACE_PERIOD,
    multiproc=c.MULTIPROCESSING,
    clear_db=c.CLEAR_DB,
    write_invalid_to_db=c.WRITE_INVALID_TO_DB,
    enable_qol=c.ENABLE_QOL  # script has things like sleep, pauses, for human interaction. Disable for testing or whatever
):
    start_time = time.perf_counter()

    if QUICK_RUN:  # switch for a convenient run of a particular set
        take_profits = [0.1]
        stop_losses = [0.1]
        leverages = [1]
        trailing_sls = [False]
        trail_delays = [False]
        sls = [[[]]]
        multiproc = False
        drawdown_limits = [-100]
        loss_limit_fractions = [0]
        signal_exits_only = True
        winrate_floor = -1

    scenario_count = 0
    specs = []

    # db connection
    mongo = pymongo.MongoClient(db_connection)
    bt_coll = mongo[db][db_coll]
    if clear_db:
        bt_coll.drop()

    # print(f"db connection established at {time.perf_counter() - start_time} seconds")
    # count the scenarios
    for datafilename in datafilenames:
        for leverage in leverages:
            for stop_loss in stop_losses:
                for take_profit in take_profits:
                    for trailing_sl in trailing_sls:
                        for trail_delay in trail_delays:
                            for sl in sls:
                                for drawdown_limit in drawdown_limits:
                                    for loss_limit_fraction in loss_limit_fractions:
                                        scenario_count += 1
    scenario_num = 0

    print(f"{scenario_count} scenarios counted at {time.perf_counter() - start_time} seconds")
    for datafilename in datafilenames:
        # derive characteristics from filename and load to dataframe
        try:
            datafilename_only = datafilename.split("/")[1]
        except IndexError:
            datafilename_only = datafilename
        timeframe = int(re.split("[-m_]", datafilename_only)[1])
        df = pd.read_csv(filepath_or_buffer=datafilename, parse_dates=["time"])
        for leverage in leverages:
            print(f"assembling specs for leverage {leverage}")
            for stop_loss in stop_losses:
                for take_profit in take_profits:
                    for trailing_sl in trailing_sls:
                        for trail_delay in trail_delays:
                            for sl in sls:
                                for drawdown_limit in drawdown_limits:
                                    for loss_limit_fraction in loss_limit_fractions:
                                        scenario_num += 1
                                        spec = {
                                            "scenario_num": scenario_num,
                                            "scenario_count": scenario_count,
                                            "datafilename": datafilename,
                                            "df": df,
                                            "timeframe": timeframe,
                                            "leverage": leverage,
                                            "stop_loss": stop_loss,
                                            "take_profit": take_profit,
                                            "trailing_sl": trailing_sl,
                                            "sl_reset_points": sl,
                                            "trail_delay": trail_delay,
                                            "db": db,
                                            "db_coll": db_coll,
                                            "write_invalid_to_db": write_invalid_to_db,
                                            "loss_limit_fraction": loss_limit_fraction,
                                            "drawdown_limit": drawdown_limit,
                                            "winrate_floor": winrate_floor,
                                            "winrate_grace_period": winrate_grace_period,
                                            "signal_exits_only": signal_exits_only,
                                            "reenter_on_new_signal": reenter_on_new_signal
                                        }
                                        spec["_id"] = get_unique_composite_key(spec)
                                        specs.append(spec)
    print(f"specs assembled at {time.perf_counter() - start_time} seconds")

    # screen out specs already in db
    if not QUICK_RUN:
        specs_not_in_db = []
        counter = 0
        for spec in specs:
            if not scenario_in_db(bt_coll, spec["_id"]):
                specs_not_in_db.append(spec)
            counter += 1
            if counter % 100000 == 0:
                print(f"checked for {counter} specs in db")
    else:
        specs_not_in_db = specs

    print(f"finished initial db check in {time.perf_counter() - start_time} seconds, "
          f"{len(specs) - len(specs_not_in_db)} out of {len(specs)} are already in db, "
          f"leaving {len(specs_not_in_db)} to load.")
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


def scenario_in_db(coll, _id):
    return coll.count_documents({"_id": _id}, limit=1)  # 20 sec per 100k docs


def chunks(sequence, chunk_size):
    for j in range(0, len(sequence), chunk_size):
        yield sequence[j:j + chunk_size]


def run_single_scenario(spec):
    return ScenarioRunner(spec).run_scenario()


class ScenarioRunner:
    def __init__(self, spec):
        self.spec = spec
        self.stop_loss = self.sl_trail = spec["stop_loss"]
        self.trailing_on = spec["trailing_sl"] and not spec["trail_delay"]
        self.sig_exits_only = spec["signal_exits_only"]

        # calculate number of days
        candle_count = len(spec["df"].index)
        minutes = candle_count * int(spec["timeframe"])
        self.days = round(minutes / 1440, 1)

        self.long_entry_price = None
        self.short_entry_price = None
        self.assets = 1.0
        self.min_assets = self.max_assets = self.assets
        self.entries = 0
        self.stop_loss_exits_in_profit = 0
        self.stop_loss_exits_at_loss = 0
        self.take_profit_exits = 0
        self.signal_exits_in_profit = 0
        self.signal_exits_at_loss = 0
        self.leverage = spec["leverage"]
        self.profit_pct = None
        self.trade_history = []
        self.trade = {}
        self.max_drawdown_pct = self.total_profit_pct = 0

        self.start_date = spec["df"].iloc[0]["time"].isoformat().replace("+00:00", "Z")
        self.end_date = spec["df"].iloc[-1]["time"].isoformat().replace("+00:00", "Z")
        self.sl_reset_points_hit = []
        self.candles_spent_in_trade = 0

        self.price_movement_at_candle_low = 0
        self.price_movement_at_candle_high = 0
        self.min_price_movement_at_candle_low = 1
        self.max_price_movement_at_candle_high = -1
        self.price_movement_low = 0
        self.price_movement_high = 0
        self.max_profit = 0
        self.min_profit = 0
        self.alpha = None
        self.beta = None

        self.row = None
        self.win_rate = None

        self.htf_shadow = None  # only used in HTF dataset scenarios

    def run_scenario(self):
        if not is_valid_scenario(self.spec):
            del self.spec["df"]  # no longer need it, and it doesn't print gracefully
            print(f"invalid spec: {self.spec}")
            return get_invalid_scenario_result(
                self.spec["_id"], self.start_date, self.end_date)

        for row in self.spec["df"].itertuples():
            self.row = row
            if self.long_entry_price:
                self.candles_spent_in_trade += 1
                # get the low point of the candle
                self.price_movement_at_candle_low = (
                    getattr(self.row, "low") / self.long_entry_price
                ) - 1
                # check for a new trade low and min profit and if so save it for later
                self.price_movement_low = min(self.price_movement_low, self.price_movement_at_candle_low)
                if self.price_movement_low == self.price_movement_at_candle_low:
                    # new min profit for this trade
                    self.min_profit = self.get_profit_pct_from_exit_pct(exit_pct=self.price_movement_low)
                # check for SL
                if self.price_movement_at_candle_low <= (-1 * self.stop_loss) and not self.sig_exits_only:
                    # we stopped out somewhere in this candle
                    try:
                        self.finish_trade(_type=STOP_LOSS)
                    except (e.TooMuchDrawdown, e.WinRateTooLow):
                        return self.finish_scenario(failed=True)
                if self.long_entry_price:
                    # get the high point of the candle
                    self.price_movement_at_candle_high = (
                        getattr(self.row, "high") / self.long_entry_price
                    ) - 1
                    # check for a new trade high
                    self.price_movement_high = max(self.price_movement_high, self.price_movement_at_candle_high)
                    if self.price_movement_high == self.price_movement_at_candle_high:
                        # new max profit for this trade: save it, and reset trailing if applicable
                        self.max_profit = self.get_profit_pct_from_exit_pct(exit_pct=self.price_movement_high)
                        if self.trailing_on:
                            # this is a new max, need to move trailing SL
                            self.stop_loss = (
                                self.sl_trail - self.price_movement_at_candle_high
                            )
                    if self.price_movement_at_candle_high >= self.spec["take_profit"] and not self.sig_exits_only:
                        # take the profit
                        try:
                            self.finish_trade(_type=TAKE_PROFIT)
                        except (e.TooMuchDrawdown, e.WinRateTooLow):
                            return self.finish_scenario(failed=True)
                    else:
                        # we didn't TP yet, but check if we hit a reset point
                        self.check_reset_points(self.price_movement_at_candle_high)

                # check if we need to exit our long due to a signal
                if self.should_close_long():
                    # exit long
                    try:
                        self.finish_trade(_type=SIGNAL)
                    except (e.TooMuchDrawdown, e.WinRateTooLow):
                        return self.finish_scenario(failed=True)

            if self.short_entry_price:
                self.candles_spent_in_trade += 1
                # get the high point of the candle
                self.price_movement_at_candle_high = (
                    getattr(self.row, "high") / self.short_entry_price
                ) - 1
                # check for new trade high (i.e. new min profit in a short)
                self.price_movement_high = max(self.price_movement_high, self.price_movement_at_candle_high)
                if self.price_movement_high == self.price_movement_at_candle_high:
                    # new min profit for this trade
                    self.min_profit = self.get_profit_pct_from_exit_pct(exit_pct=(-1 * self.price_movement_high))
                # check for SL
                if self.price_movement_at_candle_high >= self.stop_loss and not self.sig_exits_only:
                    # we stopped out somewhere in this candle
                    try:
                        self.finish_trade(_type=STOP_LOSS)
                    except (e.TooMuchDrawdown, e.WinRateTooLow):
                        return self.finish_scenario(failed=True)

                if self.short_entry_price:
                    # get the low point of the candle
                    self.price_movement_at_candle_low = (
                        getattr(self.row, "low") / self.short_entry_price
                    ) - 1
                    # check for a new trade low (i.e. new max profit in a short)
                    self.price_movement_low = min(self.price_movement_low, self.price_movement_at_candle_low)
                    if self.price_movement_low == self.price_movement_at_candle_low:
                        # new max profit for this trade
                        self.max_profit = self.get_profit_pct_from_exit_pct(exit_pct=(-1 * self.price_movement_low))
                        if self.trailing_on:
                            # this is a new min, need to move trailing SL
                            self.stop_loss = (
                                self.sl_trail + self.price_movement_at_candle_low
                            )  # adjust sl
                    if self.price_movement_at_candle_low <= (
                        self.spec["take_profit"] * -1
                    ) and not self.sig_exits_only:
                        # take the profit
                        try:
                            self.finish_trade(_type=TAKE_PROFIT)
                        except (e.TooMuchDrawdown, e.WinRateTooLow):
                            return self.finish_scenario(failed=True)
                    else:
                        # we didn't TP yet, but check if we hit a reset point
                        self.check_reset_points(self.price_movement_at_candle_low)

                # check if need to exit our short due to a signal
                if self.should_close_short():
                    try:
                        self.finish_trade(_type=SIGNAL)
                    except (e.TooMuchDrawdown, e.WinRateTooLow):
                        return self.finish_scenario(failed=True)

            # check for long entry
            if self.should_open_long():
                self.long_entry_price = getattr(self.row, "close")
                self.entries += 1
                self.sl_reset_points_hit = (
                    []
                )  # clear out sl reset points for the next trade
                self.stop_loss = self.sl_trail = self.spec[
                    "stop_loss"
                ]  # reset stop_loss to starting value
                self.trailing_on = (
                    self.spec["trailing_sl"] and not self.spec["trail_delay"]
                )
                self.profit_pct = None
                self.candles_spent_in_trade = 0
                self.price_movement_at_candle_high = self.price_movement_high = self.max_profit = 0
                self.price_movement_at_candle_low = self.price_movement_low = self.min_profit = 0
                self.max_price_movement_at_candle_high = -1
                self.min_price_movement_at_candle_low = 1

                self.leverage = get_adjusted_leverage(
                    stop_loss=self.stop_loss,
                    max_leverage=self.spec["leverage"],
                    total_profit_pct=self.total_profit_pct,
                    loss_limit_fraction=self.spec["loss_limit_fraction"])[0]
                self.trade = {
                    "entry": getattr(self.row, 'time').isoformat().replace('+00:00', 'Z'),
                    "direction": "long"
                }

            # check for short entry
            if self.should_open_short():
                self.short_entry_price = getattr(self.row, "close")
                self.entries += 1
                self.sl_reset_points_hit = (
                    []
                )  # clear out sl reset points for the next trade
                self.stop_loss = self.sl_trail = self.spec[
                    "stop_loss"
                ]  # reset stop_loss to starting value
                self.trailing_on = (
                    self.spec["trailing_sl"] and not self.spec["trail_delay"]
                )
                self.profit_pct = None
                self.candles_spent_in_trade = 0
                self.price_movement_at_candle_high = self.price_movement_high = self.min_profit = 0
                self.price_movement_at_candle_low = self.price_movement_low = self.max_profit = 0
                self.max_price_movement_at_candle_high = -1
                self.min_price_movement_at_candle_low = 1

                self.leverage = get_adjusted_leverage(
                    stop_loss=self.stop_loss,
                    max_leverage=self.spec["leverage"],
                    total_profit_pct=self.total_profit_pct,
                    loss_limit_fraction=self.spec["loss_limit_fraction"])[0]
                self.trade = {
                    "entry": getattr(self.row, 'time').isoformat().replace('+00:00', 'Z'),
                    "direction": "short"
                }

        return self.finish_scenario()

    def should_open_short(self):
        bot_in_trade = self.short_entry_price
        try:
            short_signal = getattr(self.row, "short") == 1
            return not bot_in_trade and short_signal
        except AttributeError:
            pass

        htf_signal = getattr(self.row, "short_htf") == 1
        ltf_signal = getattr(self.row, "short_ltf") == 1
        if htf_signal and not bot_in_trade:
            self.htf_shadow = "short"
            return True
        if ltf_signal and self.htf_shadow == "short" and not bot_in_trade:
            return True
        return False

    def should_open_long(self):
        bot_in_trade = self.long_entry_price
        try:
            long_signal = getattr(self.row, "long") == 1
            return not bot_in_trade and long_signal
        except AttributeError:
            pass

        htf_signal = getattr(self.row, "long_htf") == 1
        ltf_signal = getattr(self.row, "long_ltf") == 1
        if htf_signal and not bot_in_trade:
            self.htf_shadow = "long"
            return True
        if ltf_signal and self.htf_shadow == "long" and not bot_in_trade:
            return True
        return False

    def should_close_short(self):
        bot_in_trade = self.short_entry_price
        try:
            long_signal = getattr(self.row, "long") == 1
            return bot_in_trade and long_signal
        except AttributeError:
            pass

        opposing_htf_signal = getattr(self.row, "long_htf") == 1
        if bot_in_trade and opposing_htf_signal:
            return True
        return False

    def should_close_long(self):
        bot_in_trade = self.long_entry_price
        try:
            short_signal = getattr(self.row, "short") == 1
            return bot_in_trade and short_signal
        except AttributeError:
            pass

        opposing_htf_signal = getattr(self.row, "short_htf") == 1
        if bot_in_trade and opposing_htf_signal:
            return True
        return False

    def get_profit_pct_from_exit_price(self, exit_price):
        # takes an exit price like 34,001 and returns profit pct after fees and leverage
        if self.long_entry_price:
            return ((exit_price / self.long_entry_price) - 1) * self.leverage - FEES * self.leverage
        if self.short_entry_price:
            return ((exit_price / self.short_entry_price) - 1) * -1 * self.leverage - FEES * self.leverage

    def get_profit_pct_from_exit_pct(self, exit_pct):
        # takes an exit price based profit pct like 2% and returns final profit pct after fees and leverage
        exit_pct = min(exit_pct, self.spec["take_profit"])  # cut off anything beyond TP
        exit_pct = max(exit_pct, -1 * self.spec["stop_loss"])  # cut off anything below SL
        return exit_pct * self.leverage - FEES * self.leverage

    def finish_trade(self, _type):
        exit_price = getattr(self.row, "close")
        exit_type = None
        if _type == STOP_LOSS:
            self.profit_pct = self.get_profit_pct_from_exit_pct(exit_pct=(-1 * self.stop_loss))
            if self.profit_pct > 0:
                exit_type = "sl_profit"
            else:
                exit_type = "sl_loss"

        elif _type == TAKE_PROFIT:
            self.profit_pct = self.get_profit_pct_from_exit_pct(exit_pct=self.spec["take_profit"])
            exit_type = "tp"

        elif _type == SIGNAL:
            self.profit_pct = self.get_profit_pct_from_exit_price(exit_price=exit_price)
            if self.profit_pct > 0:
                exit_type = "sig_profit"
            else:
                exit_type = "sig_loss"

        self.short_entry_price = (
            None  # clear both for convenience, even though only one is set
        )
        self.long_entry_price = None
        self.assets *= 1 + self.profit_pct
        self.min_assets = min(self.assets, self.min_assets)
        self.max_assets = max(self.assets, self.max_assets)
        drawdown_pct = int((1 - (self.assets / self.max_assets)) * -100)  # e.g. -68 (=68% drawdown from peak)
        self.max_drawdown_pct = min(drawdown_pct, self.max_drawdown_pct)
        self.total_profit_pct = int((self.assets - 1) * 100)  # e.g. 103 (=103% profit)

        # update trade history
        self.trade["exit"] = getattr(self.row, "time").isoformat().replace("+00:00", "Z")
        self.trade["profit"] = round(self.profit_pct, 4)
        self.trade["duration"] = self.candles_spent_in_trade
        self.trade["assets"] = round(self.assets, 2)
        self.trade["leverage"] = self.leverage
        self.trade["exit_type"] = exit_type
        self.trade["min_profit"] = round(self.min_profit, 4)
        self.trade["max_profit"] = round(self.max_profit, 4)
        self.trade_history.append(self.trade)

        if self.max_drawdown_pct < self.spec["drawdown_limit"]:
            raise e.TooMuchDrawdown

        if len(self.trade_history) >= self.spec["winrate_grace_period"]:
            self.calculate_win_rate()
            if self.win_rate < self.spec["winrate_floor"]:
                raise e.WinRateTooLow

    def finish_scenario(self, failed=False):
        daily_profit_pct_avg = round(
            (self.assets ** (1 / float(self.days)) - 1) * 100, 2
        )

        mean_profit = None
        median_profit = None
        mean_hrs_in_trade = None

        if len(self.trade_history) > 0:
            self.calculate_win_rate()
            mean_profit = round(mean(self.get_profits()), 3)
            median_profit = round(median(self.get_profits()), 3)
            mean_hrs_in_trade = round(
                mean(self.get_durations()) * int(self.spec["timeframe"]) / 60, 2
            )
            self.alpha = self.calculate_alpha()
            self.beta = round(mean_profit * len(self.trade_history) * 100, 3)

        del self.spec["df"]  # no longer need it, and it doesn't print gracefully
        print(
            f"{median_profit} median profit from spec: {self.spec}"
        )

        result = {
            "_id": self.spec["_id"],
            "start_date": self.start_date,
            "end_date": self.end_date,
            "trade_history": self.trade_history,
            "total_profit_pct": self.total_profit_pct,
            "daily_profit_pct_avg": daily_profit_pct_avg,
            "max_drawdown_pct": self.max_drawdown_pct,
            "win_rate": self.win_rate,
            "entries": self.entries,
            "finished_entries": len(self.trade_history),
            "stop_loss_exits_in_profit": self.get_exit_type_count('sl_profit'),
            "stop_loss_exits_at_loss": self.get_exit_type_count('sl_loss'),
            "take_profit_exits": self.get_exit_type_count('tp'),
            "signal_exits_in_profit": self.get_exit_type_count('sig_profit'),
            "signal_exits_at_loss": self.get_exit_type_count('sig_loss'),
            "mean_profit": mean_profit,
            "median_profit": median_profit,
            "days": self.days,
            "mean_hrs_in_trade": mean_hrs_in_trade,
            "valid": not failed,
            "final_assets": round(self.assets, 2),
            "min_assets": round(self.min_assets, 2),
            "max_assets": round(self.max_assets, 2),
            "mean+median": round(mean_profit + median_profit, 3),
            "alpha": self.alpha,
            "beta": self.beta
        }
        if QUICK_RUN:
            print(f"result for spec {self.spec['_id']}: \n{result}")

        return result

    def calculate_win_rate(self):
        self.win_rate = int(len(self.get_positive_profits()) / len(self.get_durations()) * 100)

    def get_positive_profits(self):
        return [trade['profit'] for trade in self.trade_history if trade['profit'] > 0]

    def get_profits(self):
        return [trade['profit'] for trade in self.trade_history]

    def get_exit_type_count(self, exit_type):
        return len([trade['exit_type'] for trade in self.trade_history if trade['exit_type'] == exit_type])

    def get_durations(self):
        return [trade['duration'] for trade in self.trade_history]

    def calculate_alpha(self):
        return round(sum([trade["max_profit"] + trade["min_profit"] for trade in self.trade_history]) * 100, 3)

    def check_reset_points(self, price_movement):
        for sl_reset_point in self.spec["sl_reset_points"]:
            if len(sl_reset_point) == 2:  # so it skips over the empty reset list
                sl_trigger = sl_reset_point[0]
                new_sl = sl_reset_point[1]
                if sl_trigger not in self.sl_reset_points_hit:
                    # haven't hit this one yet, check if we have reached it now
                    if self.short_entry_price:
                        trigger_hit = price_movement <= (-1 * sl_trigger) / 100
                    elif self.long_entry_price:
                        trigger_hit = price_movement >= sl_trigger / 100
                    else:
                        raise Exception("check_reset_points called w/o live trade")
                    if trigger_hit:
                        # we hit it somewhere in this candle!  change the stop loss
                        self.stop_loss = new_sl / 100
                        # record that we hit it, so we don't repeat
                        self.sl_reset_points_hit.append(sl_trigger)
                        if self.spec["trailing_sl"]:
                            # update the trail
                            self.sl_trail = (sl_trigger + new_sl) / 100
                            # update current sl with trail
                            if self.short_entry_price:
                                self.stop_loss = price_movement + self.sl_trail
                            elif self.long_entry_price:
                                self.stop_loss = self.sl_trail - price_movement
                            # flip on trailing
                            self.trailing_on = True
                    else:
                        return


def get_adjusted_leverage(stop_loss, max_leverage, total_profit_pct, loss_limit_fraction):
    if loss_limit_fraction == 0:  # no loss limit desired
        return max_leverage, 0
    pct_of_starting_assets = total_profit_pct + 100
    loss_limit = max(0.1, round(pct_of_starting_assets * loss_limit_fraction / 100, 3))
    potential_loss = stop_loss * max_leverage
    if (potential_loss <= loss_limit) or max_leverage == 1:
        # there are no problems.  leverage is fine
        return max_leverage, loss_limit
    # max with 1 to avoid sub-1 lev. Multiple both by 100 to avoid float division imprecision
    adj_leverage = max(1, (loss_limit * 100) // (stop_loss * 100))
    adj_leverage = min(max_leverage, adj_leverage)  # make sure we don't exceed configured lev
    return int(adj_leverage), loss_limit


def is_valid_scenario(spec):
    protected = False
    trail_config_valid = False
    tp_tsl_valid = False
    drawdown_valid = False
    # a valid scenario is protected from liquidation
    if spec["stop_loss"] < (1 / (1 + spec["leverage"])):
        protected = True
    # a valid scenario uses one of the valid trail/trail delay configs
    config = (spec["trailing_sl"], spec["trail_delay"])
    if config in VALID_TRAIL_CONFIGS:
        trail_config_valid = True
    # a valid scenario has a TP higher than the highest reset trigger
    if not len(spec["sl_reset_points"][-1]):
        tp_tsl_valid = True
    elif spec["take_profit"] > spec["sl_reset_points"][-1][0] / 100:
        tp_tsl_valid = True
    # a valid scenario is protected from hitting drawdown limit in a single trade
    if -1 * (spec["stop_loss"] * 100 * spec["leverage"]) >= spec["drawdown_limit"]:
        drawdown_valid = True

    return protected and trail_config_valid and tp_tsl_valid and drawdown_valid


def get_unique_composite_key(spec):
    unique_composite_key = {
        "datafilename": spec["datafilename"],
        "leverage": spec["leverage"],
        "stop_loss": spec["stop_loss"],
        "take_profit": spec["take_profit"],
        "trailing_sl": spec["trailing_sl"],
        "sl_reset_points": spec["sl_reset_points"],
        "trail_delay": spec["trail_delay"],
        "loss_limit_fraction": spec["loss_limit_fraction"],
        "drawdown_limit": spec["drawdown_limit"],
        "winrate_floor": spec["winrate_floor"],
        "winrate_grace_period": spec["winrate_grace_period"],
        "signal_exits_only": spec["signal_exits_only"],
        "reenter_on_new_signal": spec["reenter_on_new_signal"]
    }
    return unique_composite_key


def get_invalid_scenario_result(_id, start_date, end_date):
    result = {
        "_id": _id,
        "start_date": start_date,
        "end_date": end_date,
        "trade_history": None,
        "total_profit_pct": None,
        "daily_profit_pct_avg": None,
        "max_drawdown_pct": None,
        "win_rate": None,
        "entries": None,
        "finished_entries": None,
        "stop_loss_exits_in_profit": None,
        "stop_loss_exits_at_loss": None,
        "take_profit_exits": None,
        "signal_exits_in_profit": None,
        "signal_exits_at_loss": None,
        "mean_profit": None,
        "median_profit": None,
        "days": None,
        "mean_hrs_in_trade": None,
        "valid": False,
        "final_assets": None,
        "min_assets": None,
        "max_assets": None,
        "mean+median": None,
        "alpha": None,
        "beta": None
    }
    return result


if __name__ == "__main__":
    print("running main")
    main()
