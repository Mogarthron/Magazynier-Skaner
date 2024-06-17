import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
from datetime import datetime as dt



with open("tes_path", "r") as f:
    tes_path = f.read()

pytesseract.pytesseract.tesseract_cmd = tes_path

def odczyt_numeru(request):
   
    image = request.files['camera_image']
    image_bytes = io.BytesIO(image.read())
    pil_image = Image.open(image_bytes)
    text = pytesseract.image_to_string(pil_image, lang='eng')
    print(text.strip())
    pil_image.save(f'./static/{dt.now().strftime("%Y-%m-%d_%H%M%S")}.jpg')
    # Przetwarzanie tekstu, aby wyodrębnić numery
    numbers = ''.join(filter(str.isdigit, text))
    print("numbers", numbers, len(numbers))

    return numbers
     

    