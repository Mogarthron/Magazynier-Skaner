from flask import Flask,render_template, request, jsonify
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
from datetime import datetime as dt

with open("tes_path", "r") as f:
    tes_path = f.read()

pytesseract.pytesseract.tesseract_cmd = tes_path

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    # Strona główna z przyciskiem do przesyłania zdjęć z aparatu
    if request.method == 'POST':
        if 'camera_image' not in request.files:
            return jsonify({"error": "Brak pliku obrazu"}), 400
        print("odczyt danych")
        image = request.files['camera_image']
        image_bytes = io.BytesIO(image.read())
        pil_image = Image.open(image_bytes)
        text = pytesseract.image_to_string(pil_image, lang='eng')
        print(text.strip())
        pil_image.save(f'./static/{dt.now().strftime("%Y-%m-%d_%H%M%S")}.jpg')
        # Przetwarzanie tekstu, aby wyodrębnić numery
        numbers = ''.join(filter(str.isdigit, text))
        print("numbers", numbers, len(numbers))
       
        # return jsonify({"number": numbers})
        return render_template('index.html', numbers=numbers,)
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