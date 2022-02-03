Development:
* Activate venv: `.\venv\Scripts\activate.bat`

Running in GitBash:  
`python3 -u backtester.py`  
The -u prevents GitBash from buffering stdout


Useful MongoDB Compass filters:
{valid: true, "_id.drawdown_limit": -50, "_id.trailing_sl": false, "_id.sl_reset_points": { $size: 3}}
{ $expr: { $gt: [ "$spent" , "$budget" ] } }  # why doesn't this work??

If PyCharm is truncating test output with ellipsis, reduce the test file size.  PyCharm seems to truncate
output above ~10k lines.

Quick run settings to use for alpha runs:
        signal_exits_only = True
        take_profits = [0.1]  # not used
        stop_losses = [0.1]  # not used
        leverages = [1]
        trailing_sls = [False]
        trail_delays = [False]
        sls = [[[]]]
        multiproc = False
        drawdown_limits = [-100]
        winrate_floor = -1

To connect to Big Bro Backtester (and BetaBot???) on AWS:
Navigate to location of pem file. (~/Documents on Chronos PC)
`ssh -i "alphabot-aws-key-pair.pem" ubuntu@ec2-100-25-132-178.compute-1.amazonaws.com`

To kick off BetaBot:
`cd /home/betabot`
`nohup python3 -u main.py &`
To monitor BetaBot:
`tail -F nohup.out` in the same directory.
To stop BetaBot:
`pgrep -lf python`
`kill <pid>`
BetaBot is a collection of scripts executed as cronjobs.
To update cron schedule:
`crontab -e`


Thunderdome steps:

Phase 1: Single timeframe comparison.
1. Download UTC ISO HA indicator data for 14 timeframes:
1D, two years 
12h, two years
8h, two years
6h, two years
4h, two years
3h, two years
2h, two years
90m, two years
1h, two years
45m, two years
30m, two years
15m, six months
10m, four months
5m, two months

For each single TF dataset: 
a. delete price data prior to desired date range.
b. add short/long column names
c. delete extra columns
d. save as backtester2/data/TV_data_exports/BYBIT_BTCUSD_1D_01_2020 etc.
2. Update 5m base data sheet up to current date.
3. Run each single TF export through the signal remapper.

4. Run accuracy tester multi timeframe on all, with TP/SL up to 20.
Establish peak accuracy TP/SL % for each timeframe.

Phase 2: Double timeframe comparison.
Run accuracy tester with every combination of the single timeframes, with TP/SL up to 20.
Establish peak accuracy TP/SL % for each timeframe.

Phase 3: Triple timeframe comparison.


Phase 4: Combined TF comparisons.


Phase 5: TP/SL/DCA scenario runs.

