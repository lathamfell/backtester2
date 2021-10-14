Development:
* Activate venv: `.\venv\Scripts\activate.bat`

Running in GitBash:  
`python3 -u backtester.py`  
The -u prevents GitBash from buffering stdout


Useful db filters:
{valid: true, "_id.drawdown_limit": -50, "_id.trailing_sl": false, "_id.sl_reset_points": { $size: 3}}

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
        loss_limit_fractions = [0]
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

