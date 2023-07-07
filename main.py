import os
from trade_logic.trader import Trader
from trade_logic.utils import islem_tarihi_truncate_min_precision
from datetime import datetime, timezone
import sys
import traceback


def trader_calis(trader):
    trader.init()
    trader.turtle_trader_kur()
    trader.karar_calis()
    trader.cikis_kontrol()


def app_calis():
    islem_tarihi = datetime.utcnow()
    islem_tarihi = islem_tarihi_truncate_min_precision(islem_tarihi, 1)

    trader = Trader(islem_tarihi, "ETH")
    trader.yukle()
    if os.getenv("PYTHON_ENV") != "TEST":
        trader.init_prod()
    trader_calis(trader)
    if os.getenv("PYTHON_ENV") != "TEST":
        trader.borsada_islemleri_hallet()
    trader.kaydet()
    # print_islem_detay(trader)


if __name__ == '__main__':
    try:
        app_calis()
    except Exception as e:
        # TODO:: send_email
        traceback.print_exc()
        print(e)
