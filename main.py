from flask import Flask,render_template, request, jsonify
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io

with open("tes_path", "r") as f:
    tes_path = f.read()

pytesseract.pytesseract.tesseract_cmd = tes_path

app = Flask(__name__)

@app.route('/')
def index():
    # Strona główna z przyciskiem do przesyłania zdjęć z aparatu
    return render_template('index.html')

@app.route('/read-number', methods=['POST'])
def read_number():
    if 'image' not in request.files:
        return jsonify({"error": "Brak pliku obrazu"}), 400

    image = request.files['image']
    image_bytes = io.BytesIO(image.read())
    pil_image = Image.open(image_bytes)
    text = pytesseract.image_to_string(pil_image, lang='eng')

    # Przetwarzanie tekstu, aby wyodrębnić numery
    numbers = ''.join(filter(str.isdigit, text))

    return jsonify({"number": numbers})

@app.route('/upload-from-camera', methods=['GET', 'POST'])
def upload_from_camera():
    if request.method == 'POST':
        if 'camera_image' not in request.files:
            return jsonify({"error": "Brak pliku obrazu"}), 400

        image = request.files['camera_image']
        image_bytes = io.BytesIO(image.read())
        pil_image = Image.open(image_bytes)
        text = pytesseract.image_to_string(pil_image, lang='pol')

        # Przetwarzanie tekstu, aby wyodrębnić numery
        numbers = ''.join(filter(str.isdigit, text))

        return jsonify({"number": numbers})
    else:
        # Renderowanie strony HTML z możliwością przesyłania zdjęć
        return render_template('upload_from_camera.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)