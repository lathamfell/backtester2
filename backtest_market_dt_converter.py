import pandas as pd
import datetime


def main():
    # for raw BacktestMarket data, delete last column and add header labels:
    #   date, time, open, high, low, close, short, long
    datafilename = "data/ethusd-5m_og_labeled_2017.csv"
    # read in csv
    df = pd.read_csv(datafilename)
    out_df = df.copy(deep=True)

    for row in df.itertuples():
        # overwrite the date col with new isoformat date
        out_df.at[row[0], 'time'] = get_iso_dt(row)
        print(f"converted row {row[0]}")
    out_df = out_df.drop(columns=["date"])
    # write df back to csv
    outfilename = datafilename.split('.')[0] + "_isoformat_time.csv"
    out_df.to_csv(outfilename, index=False)


def get_iso_dt(row):
    # determine whether this is TradingView or BacktestMarket time format
    if getattr(row, 'date') and getattr(row, 'time'):
        # BacktestMarket format: date 01/03/2019, time 00:00:00
        date = getattr(row, 'date')
        day = int(date.split('/')[0])
        month = int(date.split('/')[1])
        year = int(date.split('/')[2])
        t = getattr(row, 'time')
        hour = int(t.split(':')[0])
        minute = int(t.split(':')[1])
        dt = datetime.datetime(year, month, day, hour, minute)
        return dt.isoformat() + 'Z'
    else:
        # TradingView format: 2019-01-03T00:00:00Z
        return getattr(row, 'time')


if __name__ == '__main__':
    main()
