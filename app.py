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
            return redirect(url_for("login"))

@app.route("/logout")
def logout():
    logout_user()
    return render_template("index.html")

@app.route("/dodaj_urzytkownika/", methods=["POST", "GET"])
@login_required
def dodaj_urzytkownika():

    if current_user.rola == "admin":


        if request.method == "POST":
            user = request.form.getlist('userName')[0]
            rola = request.form.getlist('userRole')[0]
            haslo = request.form.getlist('haslo')[0]

            if db.session(User).filter(User.username == user):
                return render_template("dodaj_urzytkownika.html", urzytkownik_istnieje = user)
            else:
                new_user = User(user, rola, haslo)
                db.session.add(new_user)
                db.session.commit()
        
            return render_template("dodaj_urzytkownika.html", urzytkownik_istnieje = False)
    
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
           
            if mip_session.query(Stan_Mag).filter(Stan_Mag.nr_wozka == numer_wozka).all():           
                redirect_url = url_for('zabierz_przesun_wozek', numer_wozka=numer_wozka.replace("/", "_"))
                return jsonify({"redirect_url": redirect_url}), 200
            
            else:
                redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
                return jsonify({"redirect_url": redirect_url}), 200
            
        except:
            numer_wozka = "BRAK NUMERU"
            

            redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
            return jsonify({"redirect_url": redirect_url}), 200

        # if mip_session.query(Stan_Mag).filter(Stan_Mag.nr_wozka == numer_wozka).all():           
        #     redirect_url = url_for('zabierz_przesun_wozek', numer_wozka=numer_wozka.replace("/", "_"))
        #     return jsonify({"redirect_url": redirect_url}), 200
        
        # else: 
        #     redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
        #     return jsonify({"redirect_url": redirect_url}), 200
    
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

            sant_mag = Stan_Mag(request.form.get('nurmerWozka').replace("_", "/"), request.form.get('kodMiejsca'), current_user.uid, dt.now().strftime("%Y-%m-%d %H:%M:%S"))
            mip_session.add(sant_mag)
            mip_session.commit()

            return redirect(url_for('kod_wozka'))
        
        else:
            return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('odczytaj_kod_miejsca.html',title="KOD MIEJSCA", numer_wozka=numer_wozka, kod_miejsca="JESZCZE NIE WYBRANO")


@app.route("/podsumowanie_procesow", methods=["GET", "POST"])
@login_required
def podsumowanie_procesow():

    return render_template("podsumowanie_procesow.html")

@app.route("/podglad_procesow", methods=["GET", "POST"])
@login_required
def podglad_procesow():

    pp_aktywne = mip_session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 1
    ).all()

    pp_wstrzymane = mip_session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 2
    ).all()

    pp_nierozpoczete = mip_session.query(Procesy_Przydzielone.pid, Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.uid, Procesy_Przydzielone.planowany_dzien_rozpoczecia, Procesy_Przydzielone.preferowany_czas_wykonania).filter(
        Procesy_Przydzielone.status == 0
    ).all()



    if request.method == "POST":
        
        if "edytuj" in list(request.form.keys())[0]:
            return redirect(url_for("edytuj_proces", pid=int(list(request.form.keys())[0].replace("edytuj_", ""))))
        
        if "zakoncz" in list(request.form.keys())[0]:
            pp_zakoncz = mip_session.query(Procesy_Przydzielone).filter(
                Procesy_Przydzielone.pid == int(list(request.form.keys())[0].replace("zakoncz_", ""))).first()
            
            if pp_zakoncz.uwagi_kier:
                pp_zakoncz.uwagi_kier += f", ZAKONCZONO Z TABELI PROCESOW {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                pp_zakoncz.uwagi_kier = f", ZAKONCZONO Z TABELI PROCESOW {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"

            pp_zakoncz.zakoncz_proces()
            mip_session.commit()

            return redirect(url_for("podglad_procesow"))

    return render_template("podglad_procesow.html", pp_aktywne=pp_aktywne, pp_wstrzymane=pp_wstrzymane, pp_nierozpoczete=pp_nierozpoczete)


@app.route("/edytuj_proces/<pid>", methods=["GET", "POST"])
@login_required
def edytuj_proces(pid):   

    proces = mip_session.query(Procesy_Przydzielone).filter(
        Procesy_Przydzielone.pid == pid).first()

    lista_pracownikow = [x[0] for x in db.session.query(User.username).filter(User.uid != proces.uid, User.rola.in_(("rozkroj", "agencja")))]

    if request.method == "POST":
        
        proces.nazwa_procesu = request.form['nazwa_procesu']
        prac_uid = db.session.query(User.uid).filter(User.username == request.form['pracownik']).first()[0]
      
        proces.uid = prac_uid
        proces.preferowany_czas_wykonania = int(request.form['preferowany_czas_wykonania'])
        # if proces.uwagi_kier:
        proces.uwagi_kier = request.form['uwagi_kierownika']
        # print(type(request.form['uwagi_kierownika']))

        proces.planowany_dzien_rozpoczecia = request.form['planowana_data_rozpoczecia']

        # mip_session.add(proces)
        mip_session.commit()

        return redirect(url_for('podglad_procesow'))


    return render_template("edytuj_proces.html", 
                           proces=proces,
                           lista_pracownikow=lista_pracownikow, 
                           przypisany_pracownik=db.session.query(User.username).filter(User.uid == proces.uid).first()[0]
                           )

@app.route("/dodaj_proces", methods=["GET", "POST"])
def dodaj_proces(): 
    

    lista_procesow = [x[0] for x in mip_session.query(Procesy.proces).all()]
    lista_pracownikow = [x[0] for x in db.session.query(User.username).filter(User.rola.in_(("rozkroj", "agencja")))]


    if request.method == "POST":
        
        uid = db.session.query(User.uid, User.username).filter(User.username == request.form["pracownik"]).first()[0] 
        proces_id = mip_session.query(Procesy.pid).filter(Procesy.proces == request.form["proces"]).first()[0]


        try:
            pre_czas_wyk = int(request.form["preferowany_czas_wykonania"])
        except:
            pre_czas_wyk = 10


        pp = Procesy_Przydzielone(uid, current_user.uid, proces_id, request.form["nazwa_procesu"], request.form["planowana_data_rozpoczecia"], 
                                  pre_czas_wyk)
        mip_session.add(pp)
        mip_session.commit()

        return redirect(url_for("podsumowanie_procesow"))

    
    
    return render_template("dodaj_proces.html", title="DODAJ PROCES", lista_procesow=lista_procesow, lista_pracownikow=lista_pracownikow)

@app.route("/kontrola_czasu/", methods=["GET", "POST"],  defaults={"id_proces": None})
@app.route("/kontrola_czasu/<id_proces>", methods=["GET", "POST"])
@login_required
def kontrola_czasu(id_proces=None):    
    
    if id_proces:
        wybrany_proces = mip_session.query(Procesy.proces).filter(Procesy.pid == int(id_proces)).first()[0]
    else:
        wybrany_proces = "FILTRUJ PROCESY"
    
    procesy_lista = mip_session.query(Procesy.pid, Procesy.proces, Procesy.numer_procesu).all()

    print(procesy_lista)

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
    uwaga = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    uwaga.uwagi_prac += f", {uwaga_text}"
    mip_session.commit()

def rozpoczecie_procesu(ppid):
    
    mip_session.add(Procesy_w_toku(ppid=int(ppid)))
    przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

    przydzielony_porces.rozpocznij_proces()

    mip_session.commit()


def przerwanie_procesu(ppid):
     
    przerwany_proces = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]
                
    przerwany_proces.przerwij_proces()
    przydzielony_porces.przerwij_proces()
               
    mip_session.commit()

def zakonczenie_procesu(ppid):

    zakonczony_proces = mip_session.query(Procesy_w_toku).filter(Procesy_w_toku.ppid == int(ppid)).all()[-1]
    przydzielony_porces = mip_session.query(Procesy_Przydzielone).filter(Procesy_Przydzielone.pid == int(ppid)).all()[-1]

    zakonczony_proces.zakoncz_proces()
    przydzielony_porces.zakoncz_proces()

    mip_session.commit()

def odswierz_procesy(id_procesu=None):
    
    if id_procesu:
        procesy_przydzielone_query = mip_session.query(Procesy_Przydzielone.pid ,Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.status).filter(
                                Procesy_Przydzielone.proces == int(id_procesu), Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).all()
    else:
        procesy_przydzielone_query = mip_session.query(Procesy_Przydzielone.pid ,Procesy_Przydzielone.nazwa_procesu, Procesy_Przydzielone.status).filter(
                                Procesy_Przydzielone.uid == current_user.uid, Procesy_Przydzielone.status < 3).all()
        
    procesy_przydzielone = []

    for pp in procesy_przydzielone_query:
        
        rozpoczete_procesy_w_toku = mip_session.query(Procesy_w_toku.ppid, Procesy_w_toku.czas_start, Procesy_w_toku.przerwij, Procesy_w_toku.zakoncz, Procesy_w_toku.uwagi_prac).filter(Procesy_w_toku.ppid == pp[0], Procesy_w_toku.zakoncz == None).all()
   
        if len(rozpoczete_procesy_w_toku)>0:
        
            if pp[0] == rozpoczete_procesy_w_toku[-1][0]:
               
                procesy_przydzielone.append(list(pp) + list(rozpoczete_procesy_w_toku[-1])[1:])
        
        else:
            procesy_przydzielone.append(list(pp) + [None,None,None,None])

    return procesy_przydzielone

