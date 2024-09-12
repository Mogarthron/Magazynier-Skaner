from app import db
from sqlalchemy import String, Integer, Numeric, SmallInteger, Boolean, Float, DateTime
from datetime import datetime as dt
from sqlalchemy import select

from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(Integer, primary_key=True)
    username = db.Column(String(128), nullable=False)
    haslo = db.Column(String(512), nullable=False)
    rola =  db.Column(String(512), nullable=True)
    nr_prac = db.Column(Integer)

    def __init__(self, username, rola, haslo):
        self.username = username
        self.haslo = haslo
        self.rola = rola

    def get_id(self):
        return self.uid

    def __repr__(self):
        return f"<utowrzono: {self.username} z id {self.uid}, rola: {self.rola}>"

class Dostepy(db.Model):
    __tablename__ = "dostepy"

    did = db.Column(Integer, primary_key=True)
    uid = db.Column(Integer)
    aktualny_stan_magazynu = db.Column(Boolean, default=0)
    magazyn_wozkow = db.Column(Boolean, default=0)
    odczyt_kod_miejsca = db.Column(Boolean, default=0)
    odczyt_kod_wozka = db.Column(Boolean, default=0)
    zabierz_przesun_wozek = db.Column(Boolean, default=0)
    kontrola_czasu = db.Column(Boolean, default=0)
    dodaj_proces = db.Column(Boolean, default=0)
    dodaj_pracownika = db.Column(Boolean, default=0)

class Stan_Mag(db.Model):
    __tablename__ = "stan_mag"

    mid = db.Column("mid", Integer, primary_key=True, autoincrement=True)
    nr_wozka = db.Column("nr_wozka", String(10))
    miejsce = db.Column("miejsce", String(10))
    kto_wstawil = db.Column("kto_wstawil", Integer)
    kto_zabral = db.Column("kto_zabral", Integer)
    # data_wstawienia = db.Column("data_wstawienia", String(19))
    # data_zabrania = db.Column("data_zabrania", String(19))
    data_wstawienia = db.Column("data_wstawienia", DateTime)
    data_zabrania = db.Column("data_zabrania", DateTime)

    def __init__(self, nr_wozka, miejsce, username_uid, data):
        self.nr_wozka = nr_wozka
        self.miejsce = miejsce
        self.kto_wstawil = username_uid
        self.data_wstawienia = data

    def __repr__(self):
        return f"{self.data_wstawienia}| wstowiono wozek nr {self.nr_wozka}, na miejsce {self.miejsce}"

class Procesy(db.Model):
    __tablename__ = "procesy"

    pid = db.Column("pid", Integer, primary_key=True, autoincrement=True)
    proces = db.Column("proces", String(128))
    preferowany_czas_trwania = db.Column("preferowany_czas_trwania", Integer)
    opis = db.Column("opis", String(256))
    numer_procesu = db.Column("numer_procesu", String(7))

    def __init__(self, proces, preferowany_czas_trwania:int=None, opis=None, nr_procesu=None):
        self.proces = proces
        self.preferowany_czas_trwania = preferowany_czas_trwania
        self.opis = opis
        self.numer_procesu = nr_procesu

    def __repr__(self):
        return f"otowrzono{self.proces} o id:{self.pid}"

class Procesy_Przydzielone(db.Model):
    __tablename__ = "procesy_przydzielone"

    pid = db.Column("pid", Integer, primary_key=True, autoincrement=True)
    uid = db.Column("uid", Integer)
    kid = db.Column("kid", Integer)
    proces = db.Column("proces", Integer)
    nazwa_procesu = db.Column("nazwa_procesu", String(128))
    data_utworzenia = db.Column("data_utworzenia", DateTime)
    planowany_dzien_rozpoczecia = db.Column(String(10))    
    priorytet = db.Column(Integer)
    status = db.Column(Integer)
    aktywna = db.Column(Integer)    
    uwagi_kier = db.Column(String(512))
    preferowany_czas_wykonania = db.Column(Integer)

    def __init__(self, uid:int, kid:int, proces:int, nazwa_procesu:str, planowany_dzien_rozpoczecia:str, preferowany_czas_wykonania:int=None):
        self.uid = uid
        self.kid = kid
        self.proces = proces
        self.nazwa_procesu = nazwa_procesu
        self.planowany_dzien_rozpoczecia = planowany_dzien_rozpoczecia
        self.data_utworzenia = dt.now()#.strftime("%Y-%m-%d")
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



class Procesy_w_toku(db.Model):
    __tablename__ = "procesy_w_toku"

    tid = db.Column("tid", Integer, primary_key=True, autoincrement=True)
    ppid = db.Column("ppid", Integer)
    czas_start = db.Column("czas_start", DateTime)
    przerwij = db.Column("przerwij", DateTime)
    zakoncz = db.Column("zakoncz", DateTime)
    uwagi_prac = db.Column("uwagi_pracownika", String(512))

    def __init__(self, ppid):
        self.ppid = ppid
        self.czas_start = dt.now()   
        self.uwagi_prac = ""     

    def przerwij_proces(self):
        self.przerwij = dt.now()

    def zakoncz_proces(self):
        self.zakoncz = dt.now()

    def __repr__(self):
        return f"proces id: {self.ppid}, rozpoczęto: {self.czas_start}"