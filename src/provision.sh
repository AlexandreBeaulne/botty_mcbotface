#!/bin/bash

sudo yum install -y tmux
sudo yum install -y git
wget http://repo.continuum.io/archive/Anaconda3-4.0.0-Linux-x86_64.sh
bash Anaconda3-4.0.0-Linux-x86_64.sh -b
echo "export PATH=$HOME/anaconda3/bin:$PATH" >> $HOME/.bashrc
git clone https://github.com/blampe/IbPy.git
cd IbPy/ && sudo python setup.py install && cd $HOME
sudo pip install awscli
git clone https://github.com/AlexandreBeaulne/botty_mcbotface.git

# missing:
# * .vimrc # (https://bitbucket.org/AlexandreBeaulne/dev.git)
# * .tmux.conf (https://bitbucket.org/AlexandreBeaulne/dev.git)
# * $ aws configure
# * $ gpg -d botty_mcbotface/src/strategy.py.gpg

