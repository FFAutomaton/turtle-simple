import math
import statistics
from schemas.enums.karar import Karar
from schemas.enums.pozisyon import Pozisyon
import pandas_ta as ta


class TurtleTrader:
    def __init__(self):
        pass
        self.son20_highest = None
        self.son20_lowest = None
        self.son10_highest = None
        self.son10_lowest = None

        self.suanki_fiyat = None
        self.giris_fiyat = None
        self.karar = 0
        self.piramit = 0
        self.risk_ratio = 0.002

    def init_strategy(self, data):
        self.reset()

    def karar_hesapla(self):
        if self.suanki_fiyat >= self.son20_highest:
            self.karar = Karar.alis

        elif self.suanki_fiyat <= self.son20_lowest:
            self.karar = Karar.satis

    def cikis_kontrol(self, pozisyon):
        if pozisyon == Pozisyon.long:
            if self.suanki_fiyat <= self.son10_lowest:
                self.karar = Karar.cikis

        if pozisyon == Pozisyon.short:
            if self.suanki_fiyat >= self.son10_highest:
                self.karar = Karar.cikis

    def miktar_hesapla(self, equity, atr_mean):
        miktar = equity * self.risk_ratio * (1 / (atr_mean * 2))
        return math.ceil(miktar)

    def atr_mean_hesapla(self, series, window):
        indicator = ta.atr(high=series["High"], low=series["Low"], close=series["Close"], length=window)
        values = []
        i = 0
        while i < window:
            if indicator.data[-i] > 0:
                values.append(indicator.data[-i])
            i += 1
        return statistics.mean(values)

    def reset(self):
        self.karar = 0
        self.piramit = 0