# map signals from a 4h dataset to the 5m chart
import pandas as pd
import re
from dateutil import parser
from datetime import timedelta

# must have long/short cols labeled
HTF_DATAFILENAME = "data/COINBASE_BTCUSD_60_2019_laguerre.csv"
#LOWER_TF_DATAFILENAME = "data/btcusd-5m_with_cols_2017_isoformat_time.csv"
LTF_DATAFILENAME = "data/btcusd-5m_with_cols_2019_laguerre_1h_4h.csv"

# configure these as needed
HTF = "60"
LTF = "5"


def main():
    df_htf = pd.read_csv(HTF_DATAFILENAME)
    df_ltf = pd.read_csv(LTF_DATAFILENAME)
    out_df = df_ltf.copy(deep=True)

    for row in df_htf.itertuples():
        sig = get_sig(row)
        if sig:
            dt_htf = parser.parse(getattr(row, 'time'))
            ltf_sig_time = (dt_htf + get_lf_timedelta(htf=HTF, ltf=LTF)).isoformat().replace('+00:00', 'Z')
            try:
                lf_idx = df_ltf.loc[df_ltf['time'] == ltf_sig_time].index[0]
            except IndexError:
                # LTF time doesn't exist in the LTF file
                print(f"skipped signal at time {dt_htf}, not found in LTF file")
                continue

            out_df.at[lf_idx, sig] = 1
            print(f"mapped signal at {dt_htf} to LTF {ltf_sig_time}")

    outfilename = LTF_DATAFILENAME.split('.')[0] + "_with_signals.csv"
    out_df.to_csv(outfilename, index=False)


def get_lf_timedelta(htf, ltf):
    if htf == "1D" and ltf == 5:
        return timedelta(hours=23, minutes=55)
    if htf == "240" and ltf == "5":
        return timedelta(hours=3, minutes=55)
    if htf == "60" and ltf == "5":
        return timedelta(hours=0, minutes=55)


def get_sig(row):
    if getattr(row, 'long') == 1:
        return 'long'
    if getattr(row, 'short') == 1:
        return 'short'
    return None


if __name__ == '__main__':
    main()
