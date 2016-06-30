#!/bin/bash

set -e

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

DATE=`date +"%Y%m%d"`
LOG=log.$DATE.jsonl

echo "backup $DATE log"
cat $LOG | gzip > $HOME/botty_mcbotface/logs/$LOG.gz

echo "extracting data"
grep RAW $LOG | python -m research.extract_data

echo "back up market data to AWS S3"
aws s3 cp $HOME/botty_mcbotface/logs s3://ltcm --recursive

echo "generate report"
python -m research.report --logs $HOME/botty_mcbotface/logs/$LOG.gz

echo "upload report to to AWS S3"
aws s3 sync $HOME/botty_mcbotface/reports s3://ltcm-reports --size-only

echo "Cleaning session logs"
rm $LOG

echo "Done."

