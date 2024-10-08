from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from datetime import datetime as dt, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from konwertuj_img_na_text import odczyt_numeru

import pandas as pd
from sqlalchemy import URL
import json

with open("config.json", "r") as c:
    mip_url = json.load(c)["MIP_URL"]

url_obj = URL.create("mysql+mysqlconnector",
                     username=mip_url["username"],
                     password=mip_url["password"],
                     host=mip_url["host"],
                     port=mip_url["port"],
                     database=mip_url["database"]
                     )

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = url_obj
app.secret_key = "SUPER SECRET KEY"


login_manager = LoginManager()
login_manager.init_app(app=app)


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

from baza_mip.models_db import *

with app.app_context():
    db.create_all()


migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(uid):
    
    return db.session.query(User).get(uid)   


@app.route('/', methods=["GET", "POST"])
def index():    

    dostepy_admin = [[url_for('kod_wozka'), "SKANER KODÓW"],        
                [url_for('aktualny_stan_magazynu'), "AKTUALNY STAN MAGAZYNU"],               
                [url_for('kontrola_czasu'), "KONTROLA CZASU"],        
                [url_for('podglad_procesow'), "PODGLAD PROCESOW"],        
                [url_for('podsumowanie_procesow'), "PODSUMOWANIE PROCESOW"],        
                [url_for('dodaj_proces'), "DODAJ PROCES"],        
                [url_for('dodaj_urzytkownika'), "DODAJ URZYTKOWNIKA"],
                [url_for('pobierz_stan_mag'), "POBIERZ STAN MAGAZYNU"]]
    
    procesy = 0

    if current_user.is_authenticated:

        procesy = db.session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).count()
        
        

    return render_template("index.html", user=current_user, dostepy=dostepy_admin, procesy=procesy)

@app.route("/aktualny_stan_magazynu", methods=["GET", "POST"])
def aktualny_stan_magazynu():

    stan_magazynu = db.session.query(Stan_Mag).filter(Stan_Mag.data_zabrania == None).order_by(Stan_Mag.nr_wozka).all()
    wolne_miejsca_mag, ilosc_miejsc = wolne_miejsca()
    return render_template("aktualny_stan_magazynu.html", stan_magazynu=stan_magazynu, wolne_miejsca_mag=wolne_miejsca_mag, ilosc_miejsc=ilosc_miejsc)


def wolne_miejsca():

    _miejsca_zajete = db.session.query(Stan_Mag.miejsce).distinct().filter(Stan_Mag.kto_zabral == None).all()
    miejsca_zajete = [x[0] for x in _miejsca_zajete]

    miejsca = {"A": range(1, 11),
                "B": range(1, 11),
                "C": range(1, 11),
                "D": range(1, 11),
                "E": range(1, 11),
                "F": range(1, 10),
                "G": range(1, 10),
                "H": range(1, 9),
                "I": range(1, 8),
                "J": range(1, 9),
                "K": range(1, 8),
                "L": range(1, 9),
                "M": range(1, 8),
                "N": range(1, 9),
                "O": range(1, 8),
                }

    wolne_miejsca_mag = list()
    for key in miejsca.keys():
        for p in miejsca[key]:
            nr_miejsca = f"M01.{key}{p}" if p > 9 else f"M01.{key}0{p}"
            if nr_miejsca not in miejsca_zajete:
                wolne_miejsca_mag.append(f"M01.{key}{p}" if p > 9 else f"M01.{key}0{p}")
    
    suma_miejsc = sum([max(miejsca[x]) for x in miejsca])

    return wolne_miejsca_mag, suma_miejsc

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("userName")
        haslo = request.form.get("password")

        
        user = db.session.query(User).filter(User.username == username).first()           
                

        if user.haslo == haslo:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))

@app.route("/logout")
def logout():
    logout_user()
    return render_template("index.html")

@app.route("/dodaj_urzytkownika/", methods=["POST", "GET"])
@login_required
def dodaj_urzytkownika():

    if current_user.rola == "admin":
        
        dostepne_role = [x[0] for x in db.session.query(User.rola).distinct()]

        if request.method == "POST":
            user = request.form.getlist('userName')[0]

            if request.form["userRole"] == "ROLA":
                rola = request.form["newUserRole"]
            else:
                rola = request.form["userRole"]

            haslo = request.form.getlist('haslo')[0]

            if db.session.query(User).filter(User.username == user).first():
                return render_template("dodaj_urzytkownika.html", urzytkownik_istnieje = user)
            else:
                print(user, rola, haslo)
                new_user = User(user, rola, haslo)
                db.session.add(new_user)
                db.session.commit()
        
        return render_template("dodaj_urzytkownika.html", urzytkownik_istnieje = False, dostepne_role=dostepne_role)
    
    else:
        return redirect(url_for("index"))


@app.route("/kod_wozka", methods=["GET","POST"])
@login_required
def kod_wozka():
    if request.method == 'POST':
        if 'camera_image' not in request.files:            
            return jsonify({"error": "Brak pliku obrazu"}), 400        
        
        ## requesty obsługiwane przez javascript!!!!!!
       
        try:
            numer_wozka = odczyt_numeru(request, current_user.username)
           
            if db.session.query(Stan_Mag).filter(Stan_Mag.nr_wozka == numer_wozka).all():           
                redirect_url = url_for('zabierz_przesun_wozek', numer_wozka=numer_wozka.replace("/", "_"))
                return jsonify({"redirect_url": redirect_url}), 200
            
            else:
                redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
                return jsonify({"redirect_url": redirect_url}), 200
            
        except:
            numer_wozka = "BRAK NUMERU"
            

            redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
            return jsonify({"redirect_url": redirect_url}), 200
    
    else:
     
        return render_template('odczytaj_kod_wozka.html', title="KOD WÓZKA")

@app.route("/zabierz_przesun_wozek/<numer_wozka>", methods=["GET","POST"])
@login_required
def zabierz_przesun_wozek(numer_wozka):
    _numer_wozka = numer_wozka.replace("_","/")
  
    kod_miejsca = db.session.query(Stan_Mag.miejsce).filter(Stan_Mag.nr_wozka == _numer_wozka, Stan_Mag.data_zabrania == None).all()
         
 
    if request.method == "POST" and len(kod_miejsca) > 0:
        
        id_wozka_w_bazie = db.session.query(Stan_Mag.mid).filter(Stan_Mag.nr_wozka == _numer_wozka).all()[-1][0]

  
        wozek = db.session.query(Stan_Mag).get(id_wozka_w_bazie)
        wozek.kto_zabral = current_user.uid
        wozek.data_zabrania = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "zabierz" in request.form.keys():
      
            db.session.commit()

            return redirect(url_for('kod_wozka'))
            

        if "przesun" in request.form.keys():
                                 
      
            db.session.commit()

            return redirect(url_for('kod_miejsca', numer_wozka=numer_wozka))        
        
    if len(kod_miejsca) == 0:     
        return render_template("zabierz_przesun_wozek.html", title=f"WÓZEK nr {numer_wozka}",numer_wozka=_numer_wozka, kod_miejsca="BRAK")
    
    return render_template("zabierz_przesun_wozek.html", title=f"WÓZEK nr {numer_wozka}",numer_wozka=_numer_wozka, kod_miejsca=kod_miejsca[-1][0])

#Kod z OBSŁUGĄ JAVA SCRIPT
@app.route("/kod_miejsca/<numer_wozka>/", methods=["GET", "POST"], defaults={"kod_miejsca": None})
@app.route("/kod_miejsca/<numer_wozka>/<kod_miejsca>", methods=["GET", "POST"])
def kod_miejsca(numer_wozka, kod_miejsca):
    _numer_wozka = numer_wozka.replace("_", "/")

    if request.method == 'POST':
        if 'camera_image' in request.files:
            image = request.files['camera_image']

            if image.filename == '':
                return jsonify({"error": "Nie wybrano pliku obrazu"}), 400

            # Procesowanie obrazu tutaj, np. zapis pliku lub przetwarzanie
            kod_miejsca = odczyt_numeru(request)  # Implementacja funkcji odczyt_numeru
            print("Odczyt danych:", _numer_wozka, kod_miejsca)

            # Przekierowanie do strony z kodem miejsca
            return jsonify({"redirect_url": url_for('kod_miejsca', numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)})

        elif kod_miejsca and 'miejsce_wozek' in request.form:
            kod_miejsca = request.form.get('kodMiejsca')
            print("Potwierdzono miejsce:", _numer_wozka, kod_miejsca)

            sant_mag = Stan_Mag(_numer_wozka.replace("_", "/"), kod_miejsca, current_user.uid, dt.now())
           
            db.session.add(sant_mag)
            db.session.commit()


            return redirect(url_for('kod_wozka'))

    return render_template('odczytaj_kod_miejsca.html', title="KOD MIEJSCA", numer_wozka=_numer_wozka, kod_miejsca=kod_miejsca or "JESZCZE NIE WYBRANO")

# #Kod BEZ obsługi javascript
# @app.route("/kod_miejsca/<numer_wozka>", methods=["GET","POST"])
# @login_required
# def kod_miejsca(numer_wozka):
#     if request.method == 'POST':
#         if "zaladuj_miejsce" in list(request.form.keys())[0]:
#             if 'camera_image' not in request.files:            
#                 return jsonify({"error": "Brak pliku obrazu"}), 400
           
#             kod_miejsca = odczyt_numeru(request, current_user.username)              

#             numer_wozka = numer_wozka.replace("_", "/")
#             print("odczyt danych:", numer_wozka,  kod_miejsca)
        

#             return render_template('odczytaj_kod_miejsca.html', numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
#         elif "miejsce_wozek" in list(request.form.keys()):
           
#             sant_mag = Stan_Mag(request.form.get('nurmerWozka').replace("_", "/"), request.form.get('kodMiejsca'), current_user.uid, dt.now())
           
#             db.session.add(sant_mag)
#             db.session.commit()

#             return redirect(url_for('kod_wozka'))
        
#         else:
#             return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
#     else:
        
#         return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca="JESZCZE NIE WYBRANO")


# def oblicz_czas(start, stop):
#     """zwraca czas w minutach"""

#     if stop.day == start.day:
    
#         dziesiata =  dt(stop.year, stop.month, stop.day, 10)
#         trzynasta =  dt(stop.year, stop.month, stop.day, 13)
    
#         if stop <= dziesiata and start <= dziesiata:
#             czas_pracy = (stop - start).seconds/60
#             return czas_pracy
        
#         if (stop > dziesiata and stop <= trzynasta) and (start > dziesiata and start <= trzynasta):
#             czas_pracy = (stop - start).seconds/60
#             return czas_pracy
        
#         if (stop > trzynasta and start > trzynasta):
#             czas_pracy = (stop - start).seconds/60
#             return czas_pracy
        
#         if start < dziesiata and stop >dziesiata and stop < trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15)).seconds/60
#             return czas_pracy
        
#         if start < dziesiata and stop >= trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=30)).seconds/60
#             return czas_pracy
        
#         if start > dziesiata and start < trzynasta and stop >= trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15)).seconds/60
#             return czas_pracy
  
#     if (stop.day - start.day) == 1:      
#         start_dziesiata =  dt(start.year, start.month, start.day, 10, 5)  
#         start_trzynasta =  dt(start.year, start.month, start.day, 13, 5)  
#         stop_dziesiata =  dt(stop.year, stop.month, stop.day, 10, 5)  
#         stop_trzynasta =  dt(stop.year, stop.month, stop.day, 13, 5)  

#         if start >= start_dziesiata and start < start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_dziesiata and start < start_trzynasta and stop >= stop_dziesiata and stop < stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=30) - timedelta(hours=15, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop > stop_dziesiata and stop <= stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_trzynasta and stop > stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=30) - timedelta(hours=15, minutes=45)).seconds/60
#             return czas_pracy

#         return 111111
    
#     if (stop.day - start.day) > 1 and (stop.day - start.day) < 3:

#         start_siudma = dt(start.year, start.month, start.day, 7, 0) 
#         start_dziesiata =  dt(start.year, start.month, start.day, 10, 5)  
#         start_trzynasta =  dt(start.year, start.month, start.day, 13, 5)  
#         stop_dziesiata =  dt(stop.year, stop.month, stop.day, 10, 5)  
#         stop_trzynasta =  dt(stop.year, stop.month, stop.day, 13, 5)  

#         if start >= start_siudma and start < start_dziesiata and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=30)*2 - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_siudma and start < start_dziesiata and stop >= stop_dziesiata and stop < stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15)*5 - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_siudma and start < start_dziesiata and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=30)*2 - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_siudma and start < start_dziesiata and stop >= stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15)*6 - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_dziesiata and start < start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         if start >= start_dziesiata and start < start_trzynasta and stop >= stop_dziesiata and stop < stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=30) - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop > stop_dziesiata and stop <= stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+48, minutes=45)).seconds/60
#             return czas_pracy

#         return 222222

#     if (stop.day - start.day) == 3:

#         start_dziesiata =  dt(start.year, start.month, start.day, 10, 5)  
#         start_trzynasta =  dt(start.year, start.month, start.day, 13, 5)  
#         stop_dziesiata =  dt(stop.year, stop.month, stop.day, 10, 5)  
#         stop_trzynasta =  dt(stop.year, stop.month, stop.day, 13, 5)  

#         if start >= start_dziesiata and start < start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+72, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_dziesiata and start < start_trzynasta and stop >= stop_dziesiata and stop < stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=30) - timedelta(hours=15+72, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop < stop_dziesiata:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+72, minutes=45)).seconds/60
#             return czas_pracy
        
#         if start >= start_trzynasta and stop > stop_dziesiata and stop <= stop_trzynasta:
#             czas_pracy = (stop - start - timedelta(minutes=15) - timedelta(hours=15+72, minutes=45)).seconds/60
#             return czas_pracy
#         return 333333
#     return 999999




def oblicz_czas(start, stop):
    """Zwraca czas pracy w minutach"""
    
    # Przerwy
    przerwa_krotka = timedelta(minutes=15)
    przerwa_dluga = timedelta(minutes=30)
    
    # Godziny przerw
    dziesiata = dt(start.year, start.month, start.day, 10)
    trzynasta = dt(start.year, start.month, start.day, 13)

    def czas_miedzy(start, stop, przerwa):
        """Oblicza czas pracy między start i stop z uwzględnieniem przerw."""
        return (stop - start - przerwa).seconds / 60
    
    def oblicz_przerwy(start, stop):
        """Zwraca odpowiednią długość przerwy w zależności od godzin pracy."""
        if start < dziesiata and stop > dziesiata and stop <= trzynasta:
            return przerwa_krotka
        if start < dziesiata and stop > trzynasta:
            return przerwa_dluga
        if start >= dziesiata and start <= trzynasta and stop > trzynasta:
            return przerwa_krotka
        return timedelta(0)

    # Obsługa przypadku, gdy start i stop są tego samego dnia
    if stop.day == start.day:
        przerwa = oblicz_przerwy(start, stop)
        return czas_miedzy(start, stop, przerwa)
    
    # Obsługa przypadku, gdy start i stop są na różnych dniach
    elif stop.day > start.day:
        total_czas_pracy = 0
        current_start = start

        # Iteracja przez każdy dzień od start do stop
        while current_start.date() <= stop.date():
            if current_start.date() == start.date():
                # Dzień rozpoczęcia pracy
                dzien_stop = dt(current_start.year, current_start.month, current_start.day, 23, 59, 59)
                przerwa = oblicz_przerwy(current_start, dzien_stop)
                total_czas_pracy += czas_miedzy(current_start, dzien_stop, przerwa)
            elif current_start.date() == stop.date():
                # Dzień zakończenia pracy
                przerwa = oblicz_przerwy(dt(stop.year, stop.month, stop.day, 0, 0), stop)
                total_czas_pracy += czas_miedzy(dt(stop.year, stop.month, stop.day, 0, 0), stop, przerwa)
            else:
                # Pełne dni między start i stop (bez przerw)
                total_czas_pracy += 24 * 60  # 24 godziny w minutach
            
            # Przejście do następnego dnia
            current_start += timedelta(days=1)

        return total_czas_pracy
    
    return 0


@app.route("/podsumowanie_procesow", methods=["GET", "POST"])
@login_required
def podsumowanie_procesow():

    # pwt = mip_session.query(Procesy_w_toku.ppid, 
    pwt = db.session.query(Procesy_w_toku.ppid, 
                            Procesy_Przydzielone.uid, 
                            Procesy.numer_procesu, 
                            Procesy_Przydzielone.nazwa_procesu, 
                            Procesy_w_toku.czas_start, 
                            Procesy_w_toku.przerwij, 
                            Procesy_w_toku.zakoncz).join(
    Procesy_Przydzielone, Procesy_Przydzielone.pid == Procesy_w_toku.ppid).join(Procesy, Procesy.pid == Procesy_Przydzielone.proces).filter(Procesy_Przydzielone.status == 3).order_by(Procesy_w_toku.ppid).all()
    
    df_pwt = pd.DataFrame(pwt)
    df_pwt["czas_start"] = pd.to_datetime(df_pwt["czas_start"], format="%Y-%m-%d %H:%M:%S")
    df_pwt["przerwij"] = pd.to_datetime(df_pwt["przerwij"], format="%Y-%m-%d %H:%M:%S")
    df_pwt["zakoncz"] = pd.to_datetime(df_pwt["zakoncz"], format="%Y-%m-%d %H:%M:%S")

    def przydziel_czas(przerwij, zakoncz):
        if pd.isna(przerwij):
            return zakoncz
        return przerwij

    df_pwt["_stop"] = df_pwt.apply(lambda x: przydziel_czas(x.przerwij, x.zakoncz), axis=1)
    df_pwt["czas_czastkowy"] = df_pwt.apply(lambda x: oblicz_czas(x.czas_start, x._stop), axis=1)
    
    df_pwt_gb = df_pwt.groupby(["numer_procesu", "nazwa_procesu", "uid"]).agg(
    {"czas_start":"min", "_stop":"max", "czas_czastkowy": "sum", "ppid":"count"}
    ).rename(
        columns={"ppid": "ILOSC_PRZERW", "_stop": "CZAS_STOP", "czas_czastkowy":"CZAS_TRWANIA_PROCESU", "czas_start": "CZAS_START"}).reset_index()

    df_pwt_gb["CZAS_CALOWITY"] = df_pwt_gb.apply(lambda x: oblicz_czas(x.CZAS_START, x.CZAS_STOP), axis=1)

    return render_template("podsumowanie_procesow.html", procesy_w_toku = df_pwt_gb.round(2))

@app.route("/pobierz_raport")
def pobierz_raport():
   
    pwt = db.session.query(Procesy_w_toku.ppid, 
                            Procesy_Przydzielone.uid, 
                            Procesy.numer_procesu,
                            Procesy.proces, 
                            Procesy_Przydzielone.nazwa_procesu, 
                            Procesy_Przydzielone.preferowany_czas_wykonania,
                            Procesy_w_toku.czas_start, 
                            Procesy_w_toku.przerwij, 
                            Procesy_w_toku.zakoncz).join(
                            Procesy_Przydzielone, Procesy_Przydzielone.pid == Procesy_w_toku.ppid).join(
                            Procesy, Procesy.pid == Procesy_Przydzielone.proces).join(
                            User, User.uid == Procesy_Przydzielone.uid).filter(
                            Procesy_Przydzielone.status == 3).order_by(Procesy_w_toku.ppid).all()
    
    df_pwt = pd.DataFrame(pwt)
    df_pwt["numer_procesu"] = df_pwt.numer_procesu.apply(lambda x: int(x.split("_")[1]))

    def nr_partii(x):
        try:
            return x.split("PARTII ")[1][:5]
        except:
            return "BRAK NUMERU PARTII"
    df_pwt["nr_partii"] = df_pwt.nazwa_procesu.apply(nr_partii)
    df_pwt["czas_start"] = pd.to_datetime(df_pwt["czas_start"], format="%Y-%m-%d %H:%M:%S")
    df_pwt["przerwij"] = pd.to_datetime(df_pwt["przerwij"], format="%Y-%m-%d %H:%M:%S")
    df_pwt["zakoncz"] = pd.to_datetime(df_pwt["zakoncz"], format="%Y-%m-%d %H:%M:%S")

    def przydziel_czas(przerwij, zakoncz):
        if pd.isna(przerwij):
            return zakoncz
        return przerwij

    df_pwt["_stop"] = df_pwt.apply(lambda x: przydziel_czas(x.przerwij, x.zakoncz), axis=1)
    df_pwt["czas_czastkowy"] = df_pwt.apply(lambda x: oblicz_czas(x.czas_start, x._stop), axis=1)

    import openpyxl
    from openpyxl.utils.dataframe import dataframe_to_rows

    wb = openpyxl.Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df_pwt, index=False, header=True):
        ws.append(r)
    # ws.append(df_pwt)
    wb.save(f"raport_procesow.xlsx")

    return send_file(f"raport_procesow.xlsx")

@app.route("/podglad_procesow", methods=["GET", "POST"])
@login_required
def podglad_procesow():

    pp_aktywne = db.session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 1
    ).all()

    pp_wstrzymane = db.session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 2
    ).all()

    pp_nierozpoczete = db.session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 0
    ).all()

    if request.method == "POST":
        
        if "edytuj" in list(request.form.keys())[0]:
            return redirect(url_for("edytuj_proces", pid=int(list(request.form.keys())[0].replace("edytuj_", ""))))
        
        if "zakoncz" in list(request.form.keys())[0]:
            # pp_zakoncz = mip_session.query(Procesy_Przydzielone).filter(
            pp_zakoncz = db.session.query(Procesy_Przydzielone).filter(
                Procesy_Przydzielone.pid == int(list(request.form.keys())[0].replace("zakoncz_", ""))).first()
            
            if pp_zakoncz.uwagi_kier:
                pp_zakoncz.uwagi_kier += f", ZAKONCZONO Z TABELI PROCESOW {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                pp_zakoncz.uwagi_kier = f", ZAKONCZONO Z TABELI PROCESOW {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"

            pp_zakoncz.zakoncz_proces()
            
            db.session.commit()

            return redirect(url_for("podglad_procesow"))

    return render_template("podglad_procesow.html", pp_aktywne=pp_aktywne, pp_wstrzymane=pp_wstrzymane, pp_nierozpoczete=pp_nierozpoczete)


@app.route("/edytuj_proces/<pid>", methods=["GET", "POST"])
@login_required
def edytuj_proces(pid):   
    
    proces = db.session.query(Procesy_Przydzielone).filter(
        Procesy_Przydzielone.pid == pid).first()

    lista_pracownikow = [x[0] for x in db.session.query(User.username).filter(User.uid != proces.uid, User.rola.in_(("rozkroj", "agencja", "logistyka")))]

    if request.method == "POST":
        
        proces.nazwa_procesu = request.form['nazwa_procesu']
        prac_uid = db.session.query(User.uid).filter(User.username == request.form['pracownik']).first()[0]
      
        proces.uid = prac_uid
        proces.preferowany_czas_wykonania = int(request.form['preferowany_czas_wykonania'])
       
        proces.uwagi_kier = request.form['uwagi_kierownika']


        proces.planowany_dzien_rozpoczecia = request.form['planowana_data_rozpoczecia']

        db.session.commit()

        return redirect(url_for('podglad_procesow'))


    return render_template("edytuj_proces.html", 
                           proces=proces,
                           lista_pracownikow=lista_pracownikow, 
                           przypisany_pracownik=db.session.query(User.username).filter(User.uid == proces.uid).first()[0]
                           )

@app.route("/dodaj_proces", methods=["GET", "POST"])
def dodaj_proces(): 
        
    lista_procesow = [x[0] for x in db.session.query(Procesy.proces).all()]
    lista_pracownikow = [x[0] for x in db.session.query(User.username).filter(User.rola.in_(("rozkroj", "agencja", "logistyka")))]


    if request.method == "POST":
        
        uid = db.session.query(User.uid, User.username).filter(User.username == request.form["pracownik"]).first()[0] 
        proces_id = db.session.query(Procesy.pid).filter(Procesy.proces == request.form["proces"]).first()[0]


        try:
            pre_czas_wyk = int(request.form["preferowany_czas_wykonania"])
        except:
            pre_czas_wyk = 10


        pp = Procesy_Przydzielone(uid, current_user.uid, proces_id, request.form["nazwa_procesu"], request.form["planowana_data_rozpoczecia"], 
                                  pre_czas_wyk)
        
        db.session.add(pp)
        db.session.commit()

        return redirect(url_for("podglad_procesow"))

    
    
    return render_template("dodaj_proces.html", title="DODAJ PROCES", lista_procesow=lista_procesow, lista_pracownikow=lista_pracownikow)

@app.route("/kontrola_czasu/", methods=["GET", "POST"],  defaults={"id_proces": None})
@app.route("/kontrola_czasu/<id_proces>", methods=["GET", "POST"])
@login_required
def kontrola_czasu(id_proces=None):    
    
    if id_proces:       
        wybrany_proces = db.session.query(Procesy.proces).filter(Procesy.pid == int(id_proces)).first()[0]
    else:
        wybrany_proces = "FILTRUJ PROCESY"
    
    procesy_lista = db.session.query(Procesy.pid, Procesy.proces, Procesy.numer_procesu).all()

    # print(procesy_lista)

    if request.method == "POST":
        
        if 'filtruj_procesy' in list(request.form.keys()):
            
            print(request.form["filtruj_procesy"][0])

            return redirect(url_for("kontrola_czasu", id_proces=request.form["filtruj_procesy"][0]))

        
        if 'uwagiDoProcesu' in list(request.form.keys()):

            ppid = list(request.form.keys())[-1].split("_")[1]
            dodaj_uwage(ppid, request.form['uwagiDoProcesu'])
                  
        else:

            akcja, ppid = list(request.form.keys())[0].split("_")

            if akcja == "start":
                rozpoczecie_procesu(ppid)              

            elif akcja == "wznow":
                rozpoczecie_procesu(ppid)
                
            elif akcja == "przerwij":
                przerwanie_procesu(ppid)

            elif akcja == "zakoncz":
                zakonczenie_procesu(ppid)
             
        return redirect(url_for("kontrola_czasu", id_proces=id_proces))

    return render_template("kontrola_czasu.html", 
                           title="KONTROLA CZASU PRACY", 
                           user_name=current_user.username, 
                           procesy=odswierz_procesy(id_proces), 
                           procesy_lista=procesy_lista, 
                           wybrany_proces=wybrany_proces)



def dodaj_uwage(ppid, uwaga_text):
    uwaga = db.session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    uwaga.uwagi_prac += f", {uwaga_text}"

    db.session.commit()

def rozpoczecie_procesu(ppid):
    
    db.session.add(Procesy_w_toku(ppid=int(ppid)))
    przydzielony_porces = db.session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

    przydzielony_porces.rozpocznij_proces()

    db.session.commit()


def przerwanie_procesu(ppid):

    przerwany_proces = db.session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    przydzielony_porces = db.session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]
                
    przerwany_proces.przerwij_proces()
    przydzielony_porces.przerwij_proces()

    db.session.commit()

def zakonczenie_procesu(ppid):

    zakonczony_proces = db.session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    przydzielony_porces = db.session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

    zakonczony_proces.zakoncz_proces()
    przydzielony_porces.zakoncz_proces()

    db.session.commit()

def odswierz_procesy(id_procesu=None):
    
    if id_procesu:
        procesy_przydzielone_query = db.session.query(Procesy_Przydzielone.pid ,Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.status).filter(
                                Procesy_Przydzielone.proces == int(id_procesu), Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).all()
    else:
        procesy_przydzielone_query = db.session.query(Procesy_Przydzielone.pid ,Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.status).filter(
                                Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).all()
        
    procesy_przydzielone = []

    for pp in procesy_przydzielone_query:

        rozpoczete_procesy_w_toku = db.session.query(Procesy_w_toku.ppid, Procesy_w_toku.czas_start, Procesy_w_toku.przerwij, Procesy_w_toku.zakoncz, Procesy_w_toku.uwagi_prac).filter(Procesy_w_toku.ppid == pp[0], Procesy_w_toku.zakoncz == None).all()
   
        if len(rozpoczete_procesy_w_toku)>0:
        
            if pp[0] == rozpoczete_procesy_w_toku[-1][0]:
               
                procesy_przydzielone.append(list(pp) + list(rozpoczete_procesy_w_toku[-1])[1:])
        
        else:
            procesy_przydzielone.append(list(pp) + [None,None,None,None])

    return procesy_przydzielone

@app.route("/pobierz_stan_mag", methods=["GET", "POST"])
@login_required 
def pobierz_stan_mag():
          
    stan_mag = pd.DataFrame(db.session.query(Stan_Mag.miejsce, Stan_Mag.nr_wozka, Stan_Mag.kto_wstawil, Stan_Mag.data_wstawienia, Stan_Mag.kto_zabral, Stan_Mag.data_zabrania).all())

    users = pd.DataFrame(db.session.query(User.uid, User.username).all())

    stan_mag["kto_wstawil"] = stan_mag.kto_wstawil.apply(lambda x: users[users.uid == x].username.values)
    stan_mag["kto_zabral"] = stan_mag.kto_zabral.apply(lambda x: users[users.uid == x].username.values)

    stan_mag.to_excel("stan_mag.xlsx", index=False)

    return send_file(f"stan_mag.xlsx")
    # return stan_mag.to_html(index=False)

@app.route("/skaner_qr")
def skaner_qr():

    
    return render_template("skaner_qr.html")

