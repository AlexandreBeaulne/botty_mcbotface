#!/bin/bash

set -e

DATE=`date +"%Y%m%d"`
LOG=log.$DATE.jsonl
DATA=data.$DATE.jsonl.gz
REPORT=report.$DATE.html

echo "Extracting data from $DATE logs"
grep DATA $LOG | gzip > $HOME/recoil/data/$DATA

echo "Creating report ($REPORT)"
python src/report.py < $LOG > $REPORT

echo "Back up market data to AWS S3"
aws s3 sync $HOME/recoil/data s3://ltcm/data --size-only

# TODO: when going online, stop deleting logs but start storing instead
echo "Cleaning session logs"
rm $LOG

echo "Done."

