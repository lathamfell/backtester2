# map signals from higher tf datasets to the 5m chart
# single arrow is simple, just set HTF to the single arrow TF and leave LTF at 5 and run this
# double arrow requires the above process be run twice, once for each of the arrow datasets, and then
#   manually open the files and copy/paste one file's signal columns to the other

import pandas as pd
import re
from dateutil import parser
from datetime import timedelta

# note: HTF file must have short/long cols labeled
# note: for LTF file use the 5m base file that goes back to the same mo/year as the HTF. It won't be edited
# NOTE: WHEN ADDING FRESH DATA TO BASE FILES DO NOT BRING IN THE 5M SIGNALS TOO!  BASE FILES == NO SIGNALS
PAIRS = [  # tuples of HTF file/LTF file
    #("data/TV_data_exports/BYBIT_BTCUSD_1D_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_10m_06_2021.csv", "data/btcusd-5m_base_05_2021.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_15m_04_2021.csv", "data/btcusd-5m_base_03_2021.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_30m_01_2020.csv", "data/btcusd-5m_base_01_2020.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_45m_01_2020.csv", "data/btcusd-5m_base_01_2020.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_1h_01_2019.csv", "data/btcusd-5m_base_01_2019.csv"),
    ("data/TV_data_exports/BYBIT_BTCUSD_1D_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_45m_11_2018.csv", "data/btcusd-5m_base_01_2018.csv")
    #("data/TV_data_exports/BYBIT_BTCUSD_2h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_3h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_4h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_6h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_8h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv"),
    #("data/TV_data_exports/BYBIT_BTCUSD_12h_11_2018.csv", "data/btcusd-5m_base_01_2018.csv")
]


def main():
    if PAIRS is not None:
        for pair in PAIRS:
            process_pair(htf_datafilename=pair[0], ltf_datafilename=pair[1])


def process_pair(htf_datafilename, ltf_datafilename):
    print(f"processing {htf_datafilename} with base {ltf_datafilename}")
    try:
        htf = htf_datafilename.split("_")[4]
        ltf = 5
        df_htf = pd.read_csv(htf_datafilename)
        df_ltf = pd.read_csv(ltf_datafilename)
        out_df = df_ltf.copy(deep=True)

        for row in df_htf.itertuples():
            sig = get_sig(row)
            if sig:
                dt_htf = parser.parse(getattr(row, 'time'))
                ltf_sig_time = (dt_htf + get_lf_timedelta(htf=htf, ltf=ltf)).isoformat().replace('+00:00', 'Z')
                try:
                    lf_idx = df_ltf.loc[df_ltf['time'] == ltf_sig_time].index[0]
                except IndexError:
                    # LTF time doesn't exist in the LTF file
                    print(f"skipped HTF signal at time {dt_htf}, target {ltf_sig_time} not found in LTF file")
                    continue

                out_df.at[lf_idx, sig] = 1
                print(f"mapped signal at {dt_htf} to LTF {ltf_sig_time}")

        base_month_and_year = ltf_datafilename.split("_")[2] + "_" + ltf_datafilename.split("_")[3].split(".")[0]
        htf_name_wo_year = "_".join([htf_datafilename.split("_")[2].split("/")[1], htf_datafilename.split("_")[3], htf])
        outfilename = f"data/{htf_name_wo_year}_on_5m_{base_month_and_year}.csv"
        out_df.to_csv(outfilename, index=False)
    except:
        print(f"error processing file {htf_datafilename}")
        raise


def get_lf_timedelta(htf, ltf):
    if htf == "1D" and ltf == 5:
        return timedelta(hours=23, minutes=55)
    if htf == "12h" and ltf == 5:
        return timedelta(hours=11, minutes=55)
    if htf == "8h" and ltf == 5:
        return timedelta(hours=7, minutes=55)
    if htf == "6h" and ltf == 5:
        return timedelta(hours=5, minutes=55)
    if htf == "4h" and ltf == 5:
        return timedelta(hours=3, minutes=55)
    if htf == "3h" and ltf == 5:
        return timedelta(hours=2, minutes=55)
    if htf == "2h" and ltf == 5:
        return timedelta(hours=1, minutes=55)
    if htf == "90m" and ltf == 5:
        return timedelta(hours=1, minutes=25)
    if htf == "1h" and ltf == 5:
        return timedelta(hours=0, minutes=55)
    if htf == "45m" and ltf == 5:
        return timedelta(hours=0, minutes=40)
    if htf == "30m" and ltf == 5:
        return timedelta(hours=0, minutes=25)
    if htf == "15m" and ltf == 5:
        return timedelta(hours=0, minutes=10)
    if htf == "10m" and ltf == 5:
        return timedelta(hours=0, minutes=5)
    raise Exception(f"Unknown htf or ltf provided. htf: {htf}, ltf: {ltf}")


def get_sig(row):
    if getattr(row, 'long') == 1:
        return 'long'
    if getattr(row, 'short') == 1:
        return 'short'
    return None


if __name__ == '__main__':
    main()
