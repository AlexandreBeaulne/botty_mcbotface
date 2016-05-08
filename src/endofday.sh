#!/bin/bash

set -e

DATE=`date +"%Y%m%d"`
LOG=log.$DATE.jsonl
REPORT=report.$DATE.html

echo "backup $DATE log"
cat $LOG | gzip > $HOME/recoil/data/$LOG.gz

echo "Creating report ($REPORT)"
grep DATA $LOG | python src/daily_report.py > $REPORT

echo "Back up market data to AWS S3"
aws s3 sync $HOME/recoil/data s3://ltcm/data --size-only

echo "Cleaning session logs"
rm $LOG

echo "Done."

