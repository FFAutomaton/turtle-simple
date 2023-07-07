import pandas as pd
from datetime import datetime, timezone
import csv


# TODO:: bu iki fonksiyonu birlestir video bile cekilir
def islem_tarihi_truncate_min_precision(islem_tarihi, arttir):
    _m = islem_tarihi.minute - (islem_tarihi.minute % arttir)
    islem_tarihi = islem_tarihi.replace(minute=_m, second=0, microsecond=0)
    return islem_tarihi.replace(tzinfo=timezone.utc)


def islem_doldur(islem, wallet):
    islem["alis"] = float("nan")
    islem["satis"] = float("nan")
    islem["cikis"] = float("nan")

    islem["high"] = float("nan")
    islem["low"] = float("nan")
    islem["open"] = islem.get("open")

    islem["eth"] = wallet["ETH"]
    islem["usdt"] = wallet["USDT"]

    return islem


def okunur_date_yap(unix_ts):
    return datetime.utcfromtimestamp(unix_ts/1000).strftime("%Y-%m-%d %H:%M:%S")


def integer_date_yap(date_str):
    # if os.getenv("PYTHON_ENV") == "TEST":
    return int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())


# def print_islem_detay(trader):
#     print(f"bot calisti {str(trader.islem_tarihi)} - {trader.suanki_fiyat} tp: {trader.super_trend_strategy.onceki_tp}")
#     if islem.get('alis') > 0:
#         print(f"islem detaylar ==> ds: {islem.get('ds')}\t\t\t\t ==> alis: {islem.get('alis')}")
#     if islem.get('satis') > 0:
#         print(f"islem detaylar ==> ds: {islem.get('ds')}\t\t\t\t ==> satis: {islem.get('satis')}")
#     if islem.get('cikis') > 0:
#         print(f"islem detaylar ==> ds: {islem.get('ds')}\t\t\t\t ==> cikis: {islem.get('cikis')}")


if __name__ == '__main__':
    bugun = '2021-12-06'
