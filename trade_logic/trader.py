import json
from schemas.enums.pozisyon import Pozisyon
from schemas.enums.karar import Karar
from trade_logic.trader_base import TraderBase


class Trader(TraderBase):
    def init(self):
        self.series_1m = self.mum_getir(tip="1m", geribak=1)
        self.series_1h = self.mum_getir(tip="1h", geribak=1)
        self.fiyat_guncelle()

    def karar_calis(self):
        self.islem_fiyati = self.suanki_fiyat
        if self.position == Pozisyon.long:
            if self.suanki_fiyat >= self.islem_fiyati + (0.5 * self.atr_mean):
                if self.piramit <= 3:
                    self.piramit += 1
                    self.karar = Karar.alis
        if self.position == Pozisyon.short:
            if self.suanki_fiyat <= self.islem_fiyati - (0.5 * self.atr_mean):
                if self.piramit <= 3:
                    self.piramit += 1
                    self.karar = Karar.satis

        else:
            if self.turtle_trader.karar == Karar.alis:
                self.karar = Karar.alis
            elif self.turtle_trader.karar == Karar.satis:
                self.karar = Karar.satis
            else:
                self.karar = Karar.notr
                self.islem_fiyati = 0

    def turtle_trader_kur(self):
        self.atr_mean = self.turtle_trader.atr_mean_hesapla(self.series_1h, 10)
        self.islem_miktari = self.turtle_trader.miktar_hesapla(self.equity, self.atr_mean)

    def cikis_kontrol(self):
        self.turtle_trader.cikis_kontrol(self.pozisyon)
        if self.turtle_trader.karar == Karar.cikis:
            self.karar == Karar.cikis

    def kaydet(self):
        kayit_dict = {}
        kayit_dict["islem_fiyati"] = self.islem_fiyati
        kayit_dict["piramit"] = self.piramit
        kayit_dict["pozisyon"] = self.pozisyon.value

        with open("trader_durum.json", "w") as write_file:
            json.dump(kayit_dict, write_file)

    def yukle(self):
        with open("data_file.json", "r") as read_file:
            data = json.loads(read_file)
        self.islem_fiyati = float(data["islem_fiyati"])
        self.piramit = int(data["piramit"])
        self.pozisyon = Pozisyon(int(data["pozisyon"]))