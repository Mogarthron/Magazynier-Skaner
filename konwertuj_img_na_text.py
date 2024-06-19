# import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import io
from datetime import datetime as dt
from qreader import QReader
import numpy as np
import os



# with open("tes_path", "r") as f:
#     tes_path = f.read()

# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files (x86)/Tesseract-OCR/tesseract"

def odczyt_numeru(request):
   
    image = request.files['camera_image']
    image_bytes = io.BytesIO(image.read())
    pil_image = Image.open(image_bytes)
    pil_image.save(f'./static/{dt.now().strftime("%Y-%m-%d_%H%M%S")}.jpg')
    # text = pytesseract.image_to_string(pil_image, lang='eng')
    # print(text.strip())
    img_path = os.listdir("./static")[-2]
    image = cv2.cvtColor(cv2.imread(os.path.join("./static", img_path)), cv2.COLOR_BGR2RGB)
    # nparr = np.fromstring(image_bytes, np.uint8)
    # image = cv2.cvtColor(pil_image, cv2.COLOR_BGR2RGB)
    
    
    qreader = QReader()
    decoded_text = qreader.detect_and_decode(image=image)

    # print(decoded_text)


    return decoded_text[0]
     
