from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    data_wstawienia = db.Column(db.String(10))
    data_zabrania = db.Column(db.String(10))

    def __init__(self, nr_wozka, miejsce, username_uid, data):
        self.nr_wozka = nr_wozka
        self.miejsce = miejsce
        self.kto_wstawil = username_uid
        self.data_wstawienia = data

    def __repr__(self):
        return f"{self.data_wstawienia}| wstowiono wozek nr {self.nr_wozka}, na miejsce {self.miejsce}"

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(uid):
    # return User.query.get(uid) 
    return db.session.query(User).get(uid) 


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("index.html", user=current_user)

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
# @login_required
def kod_wozka():
    if request.method == 'POST':
        if 'camera_image' not in request.files:            
            return jsonify({"error": "Brak pliku obrazu"}), 400
        
        
        numer_wozka = odczyt_numeru(request, current_user.username)
        
        print("odczyt danych:", numer_wozka)
       
        # return jsonify({"number": numer_wozka})
        # return redirect(url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_")))
        redirect_url = url_for('kod_miejsca', numer_wozka=numer_wozka.replace("/", "_"))
    
        # Return the redirect URL in JSON response
        return jsonify({"redirect_url": redirect_url}), 200
    
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('odczytaj_kod_wozka.html')

@app.route("/kod_miejsca/<numer_wozka>", methods=["GET","POST"])
# @login_required
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

            sant_mag = Stan_Mag(request.form.get('nurmerWozka'), request.form.get('kodMiejsca'), current_user.uid, dt.now().strftime("%Y-%m-%d"))
            db.session.add(sant_mag)
            db.session.commit()

            return redirect(url_for('kod_wozka'))
        
        else:
            return render_template('odczytaj_kod_miejsca.html', numer_wozka=numer_wozka, kod_miejsca=kod_miejsca)
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('odczytaj_kod_miejsca.html', numer_wozka=numer_wozka, kod_miejsca="JESCZE NIE WYBRANO")

@app.route("/magazyn_wozkow")
def magazyn_wozkow():

    rozklad_magazynu = [
        ["1"]+ ["" for x in range(8)],
        ["2"]+ ["", "", "", "", "AA/111222", "","",""],
        ["3"]+ ["" for x in range(8)],
    ]

    return render_template("magazyn_wozkow.html", rozklad_magazynu=rozklad_magazynu)

@app.route("/kontrola_czasu", methods=["GET", "POST"])
def kontrola_czasu():
    user_name = "PAN ADAM"
    procesy = [["ROZLADUNEK DOSTAWY NR PARTII: 20/01"],
               ["KONTROLA JAKOSCI NR PARTII: 20/01"],
               ["DOKLADANIE MEMORY NR PARTII: 20/01"],
               ["DOKLADANIE OWAT NR PARTII: 20/01"],
               ]
    
    if request.method == "POST":
        print(request.form.keys())
    
    return render_template("kontrola_czasu.html", user_name=user_name, procesy=procesy)





if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)