from baza_mip import *
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, Boolean, Float, DateTime
from datetime import datetime as dt
from sqlalchemy import select

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

class Procesy_Przydzielone(Base):
    __tablename__ = "procesy_przydzielone"

    pid = Column("pid", Integer, primary_key=True)
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

class Procesy_w_toku(Base):
    __tablename__ = "procesy_w_toku"

    tid = Column("tid", Integer, primary_key=True, autoincrement=True)
    pid = Column("pid", Integer)
    czas_start = Column("czas_start", String(19))
    przerwij = Column("przerwij", String(19))
    zakoncz = Column("zakoncz", String(19))
    uwagi_prac = Column("uwagi_pracownika", String(512))