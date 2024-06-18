from flask import Flask, render_template, request, jsonify
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


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


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid) 


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("index.html", user=current_user.username)

@app.route("/login/<uid>")
def login(uid):
    user = User.query.get(uid)
    login_user(user)
    return "Succes"

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

@app.route("/odczytaj_kod", methods=["GET","POST"])
def odczytaj_kod():
    if request.method == 'POST':
        if 'camera_image' not in request.files:
            return jsonify({"error": "Brak pliku obrazu"}), 400
        
        print("odczyt danych")
       
        # return jsonify({"number": numbers})
        return render_template('odczytaj_kod.html')
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('odczytaj_kod.html', numbers="brak numeru")


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
    app.run("127.0.0.1", port=5000, debug=True)