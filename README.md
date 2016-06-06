
## PREREQS

* vim
* tmux: `sudo yum install tmux`
* .vimrc and .tmuxconf: https://bitbucket.org/AlexandreBeaulne/dev.git
* git: `sudo yum install git`
* Anaconda python 3: https://www.continuum.io/downloads
* IBPy: https://github.com/blampe/IbPy
* awscli: `sudo pip install awscli`
* Botty Mcbotface: https://github.com/AlexandreBeaulne/botty_mcbotface.git

## Origin of name

http://www.theguardian.com/environment/2016/apr/17/boaty-mcboatface-wins-poll-to-name-polar-research-vessel

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
* ~~perform grid search on parameters for optimization~~
* carve off and abstract strategies to be plug-and-play
* add minimum price rules to current strat
* add 'since' (instead of 'as-of'), moving average and parabolic curve fit strategies
* optimize gridsearch
* develop a market scanner to dynamically scan for instruments to watch
* Move from IB TWS to IB Gateway
* develop order management system (i.e. order triggering, position mgmt, stop losses, etc)

