
import datetime
import feather
import pandas
import sys

if __name__ == '__main__':

    _, type_, date = sys.argv

    csv_file = '{}.{}.csv'.format(type_, date)
    df = pandas.DataFrame.from_csv(csv_file).reset_index()

    feather_file = '{}.{}.feather'.format(type_, date)
    feather.write_dataframe(df, feather_file)

    print('{} {} {} done'.format(datetime.datetime.now(), type_, date))
