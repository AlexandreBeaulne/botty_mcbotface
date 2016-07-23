
## Rundown of executables

### bot/bot.py: run the bot
    $ python -m bot.bot --config config.json

### research/endofday.sh: bash script to complete end of day tasks (backup, report, etc)
    $ bash research/endofday.sh

### research/tests.py: run some unit tests
    $ python -m research.tests

### research/extract_data.py: extract market data from log file and append it to CSVs
    $ grep RAW logs/log.YYYYMMDD.jsonl | python -m research.extract_data

### research/report.py: create a report from a set of log
    $ python -m research.report --logs log.20180101.jsonl.gz log.20180102.jsonl.gz

### research/backtest.py: backtest a single parameter set on history of data
    $ python -m research.backtest --bbos logs/bbos.csv.gz --trds logs/trds.csv.gz --config config.json

### research/gridsearch.py: runs a brute force on parameters space
    $ python -m research.gridsearch --bbos logs/bbos.csv.gz --trds logs/trds.csv.gz

### research/gridsearch_analysis.py: group gridsearch results by parameters set
    $ python -m research.gridsearch_analysis

### bot/provision.sh: sketch of a bash script to provision a server for bot
    $ bash bot/provision.sh

## TODO
* ~~setup connection with IB's TWS~~
* ~~handle inbound market data~~
* ~~log if trading signal is triggered~~
* ~~setup configuration of instruments in config file~~
* ~~store market data, to do feature testing, backtesting and/or parameter optimization later~~
* ~~write script to translate the bot's logs into pretty human readable report~~
* ~~develop a mock TWS server to test bot during off hours, backtesting, scenarios, etc~~
* ~~start running live~~
* ~~end-of-day script that produce report and backup data (S3?)~~
* ~~sort out timezones situation~~
* ~~improve daily report~~
* ~~add scaled and lined up graph with stats~~
* ~~host to Amazon AWS~~
* ~~move report hosting from github to S3~~
* ~~refactor and consolidate report scripts (Jinja templating, etc)~~
* ~~add summary stats to aggregated report: biggest winner and loser, PnL ($ & %)~~
* ~~carve out signal module and move to github~~
* ~~build user-friendly backtesting module~~
* ~~optimize backtesting module~~
* ~~add max spread condition~~
* ~~sort out issue with live vs backtest~~
* ~~add minimum price rules to recoil strat~~
* ~~optimize gridsearch (run-time wise)~~
* ~~split bot and research code~~
* ~~ensure report works when no signal~~
* ~~perform grid search on parameters for strategy optimization~~
* ~~carve off and abstract strategies to be plug-and-play~~
* ~~run automatically without intervention (update config + run)~~
* ~~add 'since' (instead of 'as-of') strategy~~
* ~~differentiate long and short signal~~
* fix y-axis of volume in reports' graph
* split historical data in daily files
* develop position management system
* one-click provisioning of server
* move IB TWS from windows to linux machine (t2.small)
* add moving average strategy
* develop a market scanner to dynamically scan for instruments to watch

## Origin of name

http://www.theguardian.com/environment/2016/apr/17/boaty-mcboatface-wins-poll-to-name-polar-research-vessel

