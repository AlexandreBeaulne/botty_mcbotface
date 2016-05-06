#!/bin/bash

set -e

#DATE=`date +"%Y%m%d`
DATE=20160505

echo "Extracting data from $DATE logs"
grep DATA session.$DATE.jsonl | gzip > $HOME/recoil/data/data.$DATE.jsonl.gz

echo "Creating report (report.$DATE.html)"
python src/report.py < session.$DATE.jsonl > report.$DATE.html

echo "Back up market data to AWS S3"
aws s3 sync $HOME/recoil/data s3://ltcm/data --size-only

echo "Done."

