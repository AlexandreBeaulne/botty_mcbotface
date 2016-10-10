
BBOS_CSV=$1
TRDS_CSV=$2

DATES=($(cat $BBOS_CSV | tail -n +2 | cut -c 1-10 | uniq))

for DATE in "${DATES[@]}"
do
    DATE_STR=`date -jf '%Y-%m-%d' $DATE +'%Y%m%d'`

    # BBOS
    head -n 1 $BBOS_CSV > bbos.$DATE_STR.csv
    grep $DATE $BBOS_CSV >> bbos.$DATE_STR.csv
    python csv2feather.py bbos $DATE_STR

    # TRADES
    head -n 1 $TRDS_CSV > trds.$DATE_STR.csv
    grep $DATE $TRDS_CSV >> trds.$DATE_STR.csv
    python csv2feather.py trds $DATE_STR

done

