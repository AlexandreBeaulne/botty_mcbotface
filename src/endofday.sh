#!/bin/bash

set -e

DATE=`date +"%Y%m%d"`
LOG=log.$DATE.jsonl

echo "backup $DATE log"
cat $LOG | gzip > $HOME/recoil/logs/$LOG.gz

echo "extracting data"
grep DATA $LOG | pytho src/extract_data.py

echo "back up market data to AWS S3"
aws s3 sync $HOME/recoil/logs s3://ltcm --size-only

echo "generate report"
python src/report.py --logs $LOG

echo "upload report to to AWS S3"
aws s3 sync $HOME/recoil/reports s3://ltcm-reports --size-only

echo "Cleaning session logs"
rm $LOG

echo "Done."

