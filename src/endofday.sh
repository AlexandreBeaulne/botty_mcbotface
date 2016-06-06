#!/bin/bash

set -e

DATE=`date +"%Y%m%d"`
LOG=log.$DATE.jsonl

echo "backup $DATE log"
cat $LOG | gzip > $HOME/botty_mcbotface/logs/$LOG.gz

echo "extracting data"
grep DATA $LOG | python src/extract_data.py

echo "back up market data to AWS S3"
aws s3 cp $HOME/botty_mcbotface/logs s3://ltcm

echo "generate report"
python src/report.py --logs $HOME/botty_mcbotface/logs/$LOG.gz

echo "upload report to to AWS S3"
aws s3 sync $HOME/botty_mcbotface/reports s3://ltcm-reports --size-only

echo "Cleaning session logs"
rm $LOG

echo "Done."

