from baza_mip import *
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, Boolean, Float, DateTime
from datetime import datetime as dt
from sqlalchemy import select
from datetime import datetime as dt

class Stan_Mag(Base):
    __tablename__ = "stan_mag"

    mid = Column("mid", Integer, primary_key=True, autoincrement=True)
    nr_wozka = Column("nr_wozka", String(10))
    miejsce = Column("miejsce", String(10))
    kto_wstawil = Column("kto_wstawil", Integer)
    kto_zabral = Column("kto_zabral", Integer)
    data_wstawienia = Column("data_wstawienia", String(19))
    data_zabrania = Column("data_zabrania", String(19))

    def __init__(self, nr_wozka, miejsce, username_uid, data):
        self.nr_wozka = nr_wozka
        self.miejsce = miejsce
        self.kto_wstawil = username_uid
        self.data_wstawienia = data

    def __repr__(self):
        return f"{self.data_wstawienia}| wstowiono wozek nr {self.nr_wozka}, na miejsce {self.miejsce}"

class Procesy(Base):
    __tablename__ = "procesy"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    proces = Column("proces", String(128))
    preferowany_czas_trwania = Column("preferowany_czas_trwania", Integer)
    opis = Column("opis", String(256))
    numer_procesu = Column("numer_procesu", String(7))

    def __init__(self, proces, preferowany_czas_trwania:int=None, opis=None, nr_procesu=None):
        self.proces = proces
        self.preferowany_czas_trwania = preferowany_czas_trwania
        self.opis = opis
        self.numer_procesu = nr_procesu

    def __repr__(self):
        return f"otowrzono{self.proces} o id:{self.pid}"

class Procesy_Przydzielone(Base):
    __tablename__ = "procesy_przydzielone"

    pid = Column("pid", Integer, primary_key=True, autoincrement=True)
    uid = Column("uid", Integer)
    kid = Column("kid", Integer)
    proces = Column("proces", Integer)
    nazwa_procesu = Column("nazwa_procesu", String(128))
    data_utworzenia = Column("data_utworzenia", String(19))
    planowany_dzien_rozpoczecia = Column(String(10))    
    priorytet = Column(Integer)
    status = Column(Integer)
    aktywna = Column(Integer)    
    uwagi_kier = Column(String(512))
    preferowany_czas_wykonania = Column(Integer)

    def __init__(self, uid:int, kid:int, proces:int, nazwa_procesu:str, planowany_dzien_rozpoczecia:str, preferowany_czas_wykonania:int=None):
        self.uid = uid
        self.kid = kid
        self.proces = proces
        self.nazwa_procesu = nazwa_procesu
        self.planowany_dzien_rozpoczecia = planowany_dzien_rozpoczecia
        self.data_utworzenia = dt.now().strftime("%Y-%m-%d")
        self.status = 0 #0 - NIE ROZPOCZETY, 1 - W TRAKCIE, 2- PRZERWANY, 3 - ZAKONCZONY
        self.aktywna = 1
        self.priorytet = 1
        self.preferowany_czas_wykonania = preferowany_czas_wykonania

    def rozpocznij_proces(self):
        self.status = 1

    def przerwij_proces(self):
        self.status = 2

    def zakoncz_proces(self):
        self.status = 3



class Procesy_w_toku(Base):
    __tablename__ = "procesy_w_toku"

    tid = Column("tid", Integer, primary_key=True, autoincrement=True)
    ppid = Column("ppid", Integer)
    czas_start = Column("czas_start", String(19))
    przerwij = Column("przerwij", String(19))
    zakoncz = Column("zakoncz", String(19))
    uwagi_prac = Column("uwagi_pracownika", String(512))

    def __init__(self, ppid):
        self.ppid = ppid
        self.czas_start = dt.now().strftime("%Y-%m-%d %H:%M:%S")   
        self.uwagi_prac = ""     

    def przerwij_proces(self):
        self.przerwij = dt.now().strftime("%Y-%m-%d %H:%M:%S")

    def zakoncz_proces(self):
        self.zakoncz = dt.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"proces id: {self.ppid}, rozpoczęto: {self.czas_start}"