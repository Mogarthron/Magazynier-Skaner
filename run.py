from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from konwertuj_img_na_text import odczyt_numeru

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

    def __init__(self, username, rola, haslo):
        self.username = username
        self.haslo = haslo
        self.rola = rola

    def get_id(self):
        return self.uid

    def __repr__(self):
        return f"<utowrzono: {self.username} z id {self.uid}, rola: {self.rola}>"

class Stan_Mag(db.Model):
    __tablename__ = "stan_mag"

    mid = db.Column(db.Integer, primary_key=True)
    nr_wozka = db.Column(db.String(10))
    miejsce = db.Column(db.String(10))
    kto_wstawil = db.Column(db.Integer)
    kto_zabral = db.Column(db.Integer)
    data_wstawienia = db.Column(db.String(19))
    data_zabrania = db.Column(db.String(19))

    def __init__(self, nr_wozka, miejsce, username_uid, data):
        self.nr_wozka = nr_wozka
        self.miejsce = miejsce
        self.kto_wstawil = username_uid
        self.data_wstawienia = data

    def __repr__(self):
        return f"{self.data_wstawienia}| wstowiono wozek nr {self.nr_wozka}, na miejsce {self.miejsce}"

class Procesy(db.Model):
    __tablename__ = "procesy"

    pid = db.Column(db.Integer, primary_key=True)
    proces = db.Column(db.String())
    preferowany_czas_trwania = db.Column(db.String)
    opis = db.Column(db.String)

class Procesy_Przydzielone(db.Model):
    __tablename__ = "procesy_przydzielone"

    pid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    kid = db.Column(db.Integer)
    proces = db.Column(db.String())
    nazwa_procesu = db.Column(db.String())
    data_utworzenia = db.Column(db.String(19))
    dzien_rozpoczecia = db.Column(db.String(10))
    czas_start = db.Column(db.String(19))
    czas_stop = db.Column(db.String(19))
    priorytet = db.Column(db.Integer)
    status = db.Column(db.Integer)
    aktywna = db.Column(db.Integer)
    uwagi_prac = db.Column(db.String)
    uwagi_kier = db.Column(db.String)

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

    stan_magazynu = db.session.query(Stan_Mag).filter(Stan_Mag.data_zabrania == None).order_by(Stan_Mag.nr_wozka).all()
    
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

@app.route("/dodaj_urzytkownika/<tajne_haslo>", methods=["POST", "GET"])
def dodaj_urzytkownika(tajne_haslo):

    if tajne_haslo == "TAJNE_HASLO" and request.method == "POST":
        user = request.form.getlist('userName')[0]
        rola = request.form.getlist('userRole')[0]
        haslo = request.form.getlist('haslo')[0]

       
        new_user = User(user, rola, haslo)
        db.session.add(new_user)
        db.session.commit()
    
        return render_template("dodaj_urzytkownika.html")
    
    if tajne_haslo == "LISTA":
        return render_template("dodaj_urzytkownika.html", lista=db.session.query(User).all())

    return render_template("dodaj_urzytkownika.html")

@app.route("/kod_wozka", methods=["GET","POST"])
@login_required
def kod_wozka():
    if request.method == 'POST':
        if 'camera_image' not in request.files:            
            return jsonify({"error": "Brak pliku obrazu"}), 400        
        
        ## requesty obsługiwane przez javascript!!!!!!
        print(dt.now(), request.form.keys())
        
        numer_wozka = odczyt_numeru(request, current_user.username)

        if db.session.query(Stan_Mag).filter(Stan_Mag.nr_wozka == numer_wozka).all():
           
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
            db.session.add(sant_mag)
            db.session.commit()

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
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 1,5", "preferowany_czas_wykonania": "120min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 1, "aktywna": 1},
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 2,5", "preferowany_czas_wykonania": "20min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 2, "aktywna": 1},
        {"id_prac":5, "proces": "DOKLADANIE OWAT I PIANEK", "nazwa_procesu": "26/01 STONE 3", "preferowany_czas_wykonania": "40min", "status": "NIE ROZPOCZETE", "czas_start":None, "czas_stop":None, "priorytet": 4, "aktywna": 1},
    ]
    
    return render_template("dodaj_proces.html", title="DODAJ PROCES", procesy_przydzielone=procesy_przydzielone)

@app.route("/kontrola_czasu", methods=["GET", "POST"])
def kontrola_czasu():
    user_name = "PAN ADAM"
    procesy = [{"id":1, "nazwa":"ROZLADUNEK DOSTAWY NR PARTII: 20/01"},
               {"id":2, "nazwa":"KONTROLA JAKOSCI NR PARTII: 20/01"},
               {"id":3, "nazwa":"DOKLADANIE MEMORY NR PARTII: 20/01"},
               {"id":4, "nazwa":"DOKLADANIE OWAT NR PARTII: 20/01"},
               ]
    
    if request.method == "POST":
        print(request.form.keys())
    
    return render_template("kontrola_czasu.html", title="KONTROLA CZASU PRACY", user_name=user_name, procesy=procesy)





if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)