from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from konwertuj_img_na_text import odczyt_numeru
from baza_mip.models import *

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./appdb.db"
app.secret_key = "SUPER SECRET KEY"


login_manager = LoginManager()
login_manager.init_app(app=app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    haslo = db.Column(db.String, nullable=False)
    rola =  db.Column(db.String, nullable=True)
    nr_prac = db.Column(db.Integer)

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

    did = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    aktualny_stan_magazynu = db.Column(db.Integer, default=0)
    magazyn_wozkow = db.Column(db.Integer, default=0)
    odczyt_kod_miejsca = db.Column(db.Integer, default=0)
    odczyt_kod_wozka = db.Column(db.Integer, default=0)
    zabierz_przesun_wozek = db.Column(db.Integer, default=0)
    kontrola_czasu = db.Column(db.Integer, default=0)
    dodaj_proces = db.Column(db.Integer, default=0)
    

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(uid):
    
    return db.session.query(User).get(uid) 


@app.route('/', methods=["GET", "POST"])
def index():    
    
    return render_template("index.html", user=current_user)

@app.route("/aktualny_stan_magazynu", methods=["GET", "POST"])
def aktualny_stan_magazynu():

    stan_magazynu = mip_session.query(Stan_Mag).filter(Stan_Mag.data_zabrania == None).order_by(Stan_Mag.nr_wozka).all()
    
    return render_template("aktualny_stan_magazynu.html", stan_magazynu=stan_magazynu)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("userName")
        haslo = request.form.get("password")

        # user = User.query.filter(User.username == username).first()        
        user = db.session.query(User).filter(User.username == username).first()        

        if user.haslo == haslo:
            login_user(user)
            return render_template("index.html")
        else:
            return "FILED!!!!!!!"

@app.route("/logout")
def logout():
    logout_user()
    return render_template("index.html")

# @app.route("/dodaj_urzytkownika/<tajne_haslo>", methods=["POST", "GET"])
# def dodaj_urzytkownika(tajne_haslo):

#     if tajne_haslo == "TAJNE_HASLO" and request.method == "POST":
#         user = request.form.getlist('userName')[0]
#         rola = request.form.getlist('userRole')[0]
#         haslo = request.form.getlist('haslo')[0]

       
#         new_user = User(user, rola, haslo)
#         db.session.add(new_user)
#         db.session.commit()
    
#         return render_template("dodaj_urzytkownika.html")
    
#     if tajne_haslo == "LISTA":
#         return render_template("dodaj_urzytkownika.html", lista=db.session.query(User).all())

#     return render_template("dodaj_urzytkownika.html")

@app.route("/kod_wozka", methods=["GET","POST"])
@login_required
def kod_wozka():
    if request.method == 'POST':
        if 'camera_image' not in request.files:            
            return jsonify({"error": "Brak pliku obrazu"}), 400        
        
        ## requesty obsługiwane przez javascript!!!!!!
        print(dt.now(), request.form.keys())
        
        numer_wozka = odczyt_numeru(request, current_user.username)

        if mip_session.query(Stan_Mag).filter(Stan_Mag.nr_wozka == numer_wozka).all():
           
            redirect_url = url_for('zabierz_przesun_wozek', numer_wozka=numer_wozka.replace("/", "_"))
            return jsonify({"redirect_url": redirect_url}), 200
        
        else: 

            redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
            return jsonify({"redirect_url": redirect_url}), 200
    
    else:
     
        return render_template('odczytaj_kod_wozka.html', title="KOD WÓZKA")

@app.route("/zabierz_przesun_wozek/<numer_wozka>", methods=["GET","POST"])
@login_required
def zabierz_przesun_wozek(numer_wozka):
    _numer_wozka = numer_wozka.replace("_","/")
  
    kod_miejsca = mip_session.query(Stan_Mag.miejsce).filter(Stan_Mag.nr_wozka == _numer_wozka, Stan_Mag.data_zabrania == None).all()
         
 
    if request.method == "POST" and len(kod_miejsca) > 0:
        id_wozka_w_bazie = mip_session.query(Stan_Mag.mid).filter(Stan_Mag.nr_wozka == _numer_wozka).all()[-1][0]

        wozek = mip_session.query(Stan_Mag).get(id_wozka_w_bazie)
        wozek.kto_zabral = current_user.uid
        wozek.data_zabrania = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "zabierz" in request.form.keys():
            
            mip_session.commit()

            return redirect(url_for('kod_wozka'))
            

        if "przesun" in request.form.keys():
                                 
            mip_session.commit()

            return redirect(url_for('kod_miejsca', numer_wozka=numer_wozka))        
        
    if len(kod_miejsca) == 0:     
        return render_template("zabierz_przesun_wozek.html", title=f"WÓZEK nr {numer_wozka}",numer_wozka=_numer_wozka, kod_miejsca="BRAK")
    
    return render_template("zabierz_przesun_wozek.html", title=f"WÓZEK nr {numer_wozka}",numer_wozka=_numer_wozka, kod_miejsca=kod_miejsca[-1][0])

# @app.route("/kod_miejsca/<numer_wozka>/", methods=["GET", "POST"], defaults={"kod_miejsca": None})
# @app.route("/kod_miejsca/<numer_wozka>/<kod_miejsca>", methods=["GET","POST"])
# # @login_required
# def kod_miejsca(numer_wozka, kod_miejsca):
#     _numer_wozka = numer_wozka.replace("_", "/")
    
#     if request.method == 'POST':
#         if 'camera_image' in request.files:
#             if 'camera_image' not in request.files:            
#                 return jsonify({"error": "Brak pliku obrazu"}), 400
            
#             kod_miejsca = odczyt_numeru(request)  # Implementacja funkcji odczyt_numeru
#             print("odczyt danych:", _numer_wozka, kod_miejsca, request.form.keys())        

#             # return render_template('odczytaj_kod_miejsca.html', numer_wozka=_numer_wozka, kod_miejsca=kod_miejsca)
#             return redirect(url_for('kod_miejsca', numer_wozka=numer_wozka, kod_miejsca=kod_miejsca))
        
#         elif kod_miejsca and 'miejsce_wozek' in request.form.keys():
#             print("!!")
#             kod_miejsca = request.form.get('kodMiejsca')
#             if kod_miejsca and "JESZCZE NIE WYBRANO" not in kod_miejsca:
#                 # Process the kod_miejsca and numer_wozka as needed
#                 print("Confirming place:", _numer_wozka, kod_miejsca)

#                 # Here you can add the logic to handle the confirmed place, e.g., save to database

#                 return redirect(url_for('kod_wozka'))
#             # else:
#             #     return render_template('odczytaj_kod_miejsca.html', title="KOD MIEJSCA", numer_wozka=_numer_wozka, kod_miejsca="JESCZE NIE WYBRANO")
#     # else:
        
#     return render_template('odczytaj_kod_miejsca.html', title="KOD MIEJSCA", numer_wozka=_numer_wozka, kod_miejsca="JESCZE NIE WYBRANO")

@app.route("/kod_miejsca/<numer_wozka>", methods=["GET","POST"])
@login_required
def kod_miejsca(numer_wozka):
    if request.method == 'POST':
        if "zaladuj_miejsce" in list(request.form.keys())[0]:
            if 'camera_image' not in request.files:            
                return jsonify({"error": "Brak pliku obrazu"}), 400
            
            kod_miejsca = odczyt_numeru(request, current_user.username)
            numer_wozka = numer_wozka.replace("_", "/")
            print("odczyt danych:", numer_wozka,  kod_miejsca)
        
            # return jsonify({"number": numbers})
            return render_template('odczytaj_kod_miejsca.html', numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
        elif "miejsce_wozek" in list(request.form.keys()):
            # print("miejsc wózek!!!!", request.form.keys())

            sant_mag = Stan_Mag(request.form.get('nurmerWozka'), request.form.get('kodMiejsca'), current_user.uid, dt.now().strftime("%Y-%m-%d %H:%M:%S"))
            mip_session.add(sant_mag)
            mip_session.commit()

            return redirect(url_for('kod_wozka'))
        
        else:
            return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca="JESZCZE NIE WYBRANO")



@app.route("/magazyn_wozkow")
def magazyn_wozkow():

    rozklad_magazynu = [
        ["1"]+ ["" for x in range(8)],
        ["2"]+ ["", "", "", "", "AVA/111222", "","",""],
        ["3"]+ ["" for x in range(8)],
    ]

    return render_template("magazyn_wozkow.html", rozklad_magazynu=rozklad_magazynu)


@app.route("/dodaj_proces", methods=["GET", "POST"])
def dodaj_proces():

    procesy_przydzielone = [
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 1,5", "preferowany_czas_wykonania": "120min", "status": "ZAKONCZONE", "czas_start":None, "czas_stop":None, "priorytet": 1, "aktywna": 1},
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 2,5", "preferowany_czas_wykonania": "20min", "status": "W TRAKCIE", "czas_start":None, "czas_stop":None, "priorytet": 2, "aktywna": 1},
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 3", "preferowany_czas_wykonania": "40min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 4, "aktywna": 1},
        {"id_prac":4, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 WILLOW 1", "preferowany_czas_wykonania": "60min", "status": "PRZERWANE", "czas_start":None, "czas_stop":None, "priorytet": 1, "aktywna": 1},
        {"id_prac":4, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 WILLOW ]", "preferowany_czas_wykonania": "10min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 2, "aktywna": 1},
        {"id_prac":4, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 WILLOW [", "preferowany_czas_wykonania": "10min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 4, "aktywna": 1},
    
    ]
    
    return render_template("dodaj_proces.html", title="DODAJ PROCES", procesy_przydzielone=procesy_przydzielone)

@app.route("/kontrola_czasu", methods=["GET", "POST"])
@login_required
def kontrola_czasu():
            
    if request.method == "POST":
        print(request.form.keys())
        if 'uwagiDoProcesu' in list(request.form.keys()):
            ppid = list(request.form.keys())[-1].split("_")[1]

            print(ppid, request.form["uwagiDoProcesu"])
            uwaga = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]

            uwaga.uwagi_prac += f", {request.form['uwagiDoProcesu']}"
            mip_session.commit()
        
        else:

            akcja, ppid = list(request.form.keys())[0].split("_")
            if akcja == "start":
             
                mip_session.add(Procesy_w_toku(ppid=int(ppid)))
                przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

                przydzielony_porces.rozpocznij_proces()

                mip_session.commit()

            elif akcja == "wznow":

                mip_session.add(Procesy_w_toku(ppid=int(ppid)))
                przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

                przydzielony_porces.rozpocznij_proces()

                mip_session.commit()


            elif akcja == "przerwij":

                przerwany_proces = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
                przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]
                
                przerwany_proces.przerwij_proces()
                przydzielony_porces.przerwij_proces()
               
                mip_session.commit()

            elif akcja == "zakoncz":

                zakonczony_proces = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
                przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

                zakonczony_proces.zakoncz_proces()
                przydzielony_porces.zakoncz_proces()

                mip_session.commit()
             
            return redirect(url_for("kontrola_czasu"))#, title="KONTROLA CZASU PRACY", user_name=current_user.username, procesy=odswierz_procesy()))

    return render_template("kontrola_czasu.html", title="KONTROLA CZASU PRACY", user_name=current_user.username, procesy=odswierz_procesy())


def odswierz_procesy():
    procesy_przydzielone = []

    for pp in mip_session.query(Procesy_Przydzielone.pid ,Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.status).filter(Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).all():
        
        rozpoczete_procesy_w_toku = mip_session.query(Procesy_w_toku.ppid, Procesy_w_toku.czas_start, Procesy_w_toku.przerwij, Procesy_w_toku.zakoncz, Procesy_w_toku.uwagi_prac).filter(Procesy_w_toku.ppid == pp[0], Procesy_w_toku.zakoncz == None).all()
   
        if len(rozpoczete_procesy_w_toku)>0:
        
            if pp[0] == rozpoczete_procesy_w_toku[-1][0]:
               
                procesy_przydzielone.append(list(pp) + list(rozpoczete_procesy_w_toku[-1])[1:])
        
        else:
            procesy_przydzielone.append(list(pp) + [None,None,None,None])

    return procesy_przydzielone



if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)