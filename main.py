from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    # Strona główna z przyciskiem do przesyłania zdjęć z aparatu
    if request.method == 'POST':
        if 'camera_image' not in request.files:
            return jsonify({"error": "Brak pliku obrazu"}), 400
        
        print("odczyt danych")
       
        # return jsonify({"number": numbers})
        return render_template('index.html')
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('index.html', numbers="brak numeru")



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