#!/bin/bash

sudo yum install -y tmux
sudo yum install -y git
wget http://repo.continuum.io/archive/Anaconda3-4.1.0-Linux-x86_64.sh
bash Anaconda3-4.1.0-Linux-x86_64.sh -b
echo "export PATH=$HOME/anaconda3/bin:$PATH" >> $HOME/.bashrc
git clone https://github.com/blampe/IbPy.git
cd IbPy/ && sudo python setup.py install && cd $HOME
$HOME/anaconda3/bin/pip install awscli
$HOME/anaconda3/bin/conda install -y pylint
git clone https://github.com/AlexandreBeaulne/botty_mcbotface.git
cd $HOME/botty_mcbotface/bot/ && git submodule add https://bitbucket.org/AlexandreBeaulne/strategies.git && cd $HOME
git clone https://bitbucket.org/AlexandreBeaulne/dev.git
cp dev/.vimrc .
cp dev/.tmux.conf
git config --global user.name "Alexandre Beaulne"
git config --global user.email "alexandre.beaulne@gmail.com"

# missing:
# * $ aws configure
# * setup crontab:
# 10 13 * * 1-5 cd ~/botty_mcbotface/ && git pull origin master >> cron.log 2>&1
# 20 13 * * * cd ~/botty_mcbotface/ && ~/anaconda3/bin/python -m bot.bot --config config.json >> cron.log 2>&1
#
# might be useful: http://serverfault.com/a/595256

