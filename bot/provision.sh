#!/bin/bash

sudo yum install -y wget which bzip2 git tmux
wget http://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
bash Anaconda3-4.2.0-Linux-x86_64.sh -b
echo "export PATH=$HOME/anaconda3/bin:$PATH" >> $HOME/.bashrc
git clone https://github.com/blampe/IbPy.git
cd IbPy/ && $HOME/anaconda3/bin/python setup.py install && cd $HOME
$HOME/anaconda3/bin/pip install awscli
git clone https://github.com/AlexandreBeaulne/botty_mcbotface.git
conda install -y feather-format -c conda-forge

# missing:
# * $ aws configure
# * setup crontab:
# 10 13 * * 1-5 cd ~/botty_mcbotface/ && git pull origin master >> cron.log 2>&1
# 20 13 * * 1-5 cd ~/botty_mcbotface/ && ~/anaconda3/bin/python -m bot.bot --config config.json >> cron.log 2>&1
#
# might be useful: http://serverfault.com/a/595256
# how to: $ ssh -i misc/BottyMcbotface.pem ec2-user@ec2-54-84-26-142.compute-1.amazonaws.com "$(< bot/provision.sh)"

