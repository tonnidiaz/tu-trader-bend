from classes.binance import Binance
from utils.constants import dfs_dir, klines_dir
from utils.functions import chandelier_exit, date_str_to_timestamp, heikin_ashi, parse_klines, tu_path
import os

# ETH -> 2021 -> 2022
# BTC -> 2022
symbols = ['SOLUSDT']
years = [ 2021]
intervals = [15]


def main():
    print("Begin download...")
    _bin: Binance = Binance()

    for year in years:
        print(f'\nYear {year}')

        for symb in symbols:
            print(f"SYMB: {symb}")
            for interval in intervals:
                print(f"interval: {interval}\n")
                fname = f"{symb}_{interval}m"

                fp = f"{dfs_dir}/{year}"
                klines_fp = f"{klines_dir}/{year}"

                if not os.path.exists(tu_path(fp)):
                    print("CREARTING DIR...")
                    os.mkdir(tu_path(fp))
                if not os.path.exists(tu_path(klines_fp)):
                    print("CREARTING DIR...")
                    os.mkdir(tu_path(klines_fp))

                fp = tu_path(f"{fp}/{fname}.csv")
                klines_fp = tu_path(f"{klines_fp}/{fname}.json")

                klines = _bin.get_klines(symb, start=date_str_to_timestamp(
                    f"{year}-01-01 00:00:00"), end=date_str_to_timestamp(f"{year}-12-31 23:59:00"), interval=interval, save_fp=klines_fp)
                df = chandelier_exit(heikin_ashi(parse_klines(klines)))
                df.to_csv(fp)
                print(f"DONE interval: {interval}\n")

            print(f"DONE SYMB: {symb}\n")

        print(f'DONE Year {year}\n')

    print("DOWNLOADER FINISHED")


main()