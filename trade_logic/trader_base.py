from datetime import timedelta, datetime
import pandas as pd
from trade_logic.traders.turtle_trader import TurtleTrader
from config import *
from turkish_gekko_packages.binance_service import TurkishGekkoBinanceService
from config_users import users
from schemas.enums.pozisyon import Pozisyon
from schemas.enums.karar import Karar
from dotenv import load_dotenv


class TraderBase:
    def __init__(self, islem_tarihi, symbol):
        self.secrets = {"API_KEY": API_KEY, "API_SECRET": API_SECRET}
        load_dotenv()
        self.config = {
            "symbol": symbol, "coin": f'{symbol}USDT', "doldur": True,
            "wallet": {symbol: 0, "USDT": 1000}
        }
        self.binance_wallet = None
        self.secrets.update(self.config)
        self.wallet = None
        self.equity = None  # TODO::
        self.suanki_fiyat, self.running_price = 0, 0
        self.karar = Karar.notr
        self.pozisyon = Pozisyon.notr  # 0-baslangic, 1 long, -1 short
        self.islem_ts = 0
        self.islem_miktari = 0
        self.piramit = 0
        self.islem_fiyati = 0
        self.islem_tarihi = islem_tarihi
        self.islem_tarihi_str = datetime.strftime(islem_tarihi, '%Y-%m-%d %H:%M:%S')
        self.series_1m = None
        self.series_1h = None
        self.binance_service = TurkishGekkoBinanceService(self.secrets)
        self.turtle_trader = TurtleTrader()

    def fiyat_guncelle(self):
        data = self.series_1h
        self.suanki_fiyat = self.series_1m.Close[-1]
        self.turtle_trader.son20_highest = max(data.Close[-20:])
        self.turtle_trader.son20_lowest = min(data.Close[-20:])
        self.turtle_trader.son10_highest = max(data.Close[-10:])
        self.turtle_trader.son10_lowest = min(data.Close[-10:])
        self.turtle_trader.suanki_fiyat = self.suanki_fiyat

    def mum_getir(self, tip, geribak):
        coin = self.config.get('coin')
        baslangic_gunu = self.islem_tarihi - timedelta(days=geribak)
        bitis_gunu = self.islem_tarihi

        data = self.binance_service.get_client().get_historical_klines(
            symbol=coin, interval=tip,
            start_str=str(baslangic_gunu), end_str=str(bitis_gunu), limit=500
        )
        data = self.datayi_dikine_kes(data)
        df = pd.DataFrame(data[:-1], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
        return df

    def datayi_dikine_kes(self, tempdata):
        data = []
        for i in range(len(tempdata)):
            row = (int(tempdata[i][0]), float(tempdata[i][1]),
                   float(tempdata[i][2]), float(tempdata[i][3]),
                   float(tempdata[i][4]), float(tempdata[i][5])
                   )
            data.append(row)
        return data

    def init_prod(self):
        self.binance_wallet = self.binance_service.futures_hesap_bakiyesi()
        self.wallet_isle()

    def wallet_isle(self):
        for symbol in self.binance_wallet:
            self.config["wallet"][symbol.get("asset")] = symbol.get("balance")
        self.dolar = float(self.config["wallet"].get('USDT'))
        self.coin = float(self.config["wallet"].get(self.config.get('symbol')))

    def kullanici_bakiye_hesapla(self, _service):
        self.binance_wallet = _service.futures_hesap_bakiyesi()
        self.wallet_isle()

    def kullanicilari_don(self, _taraf=None):
        _exit_, yon, pos, leverage = None, None, None, None
        for user in users:
            user_secrets = users.get(user)
            c = 5
            while c > 0:
                try:
                    _service = TurkishGekkoBinanceService(user_secrets)
                    self.kullanici_bakiye_hesapla(_service)
                    _exit_, yon = _service.futures_market_exit(self.config.get("coin"))
                    if _taraf:
                        pos, leverage = _service.futures_market_islem(self.config.get("coin"), taraf=_taraf,
                                                                      miktar=self.islem_miktari, kaldirac=2)
                    print(f"{user} - ### ---> {_taraf} {yon} {pos} {_exit_}")
                    c = 0
                except Exception as e:
                    print(f"kullanici donerken hata olustu!!!!!!")
                    print("\n")
                    print(str(e))
                    c -= 1
        return yon

    def borsada_islemleri_hallet(self):
        if self.karar == Karar.alis:
            self.kullanicilari_don('BUY')
            self.pozisyon = Pozisyon(1)
        elif self.karar == Karar.satis:
            self.kullanicilari_don('SELL')
            self.pozisyon = Pozisyon(-1)
        elif self.karar == Karar.cikis:
            self.kullanicilari_don(None)
            self.reset_trader()

    def reset_trader(self):
        self.pozisyon = Pozisyon(0)
        self.karar = Karar(0)
        self.islem_fiyati = 0
        self.islem_miktari = 0
        self.piramit = 0
