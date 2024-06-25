from PIL import Image, ImageEnhance, ImageFilter
import cv2
import io
from datetime import datetime as dt
from qreader import QReader
import numpy as np
import os


def odczyt_numeru(request, username=None):
   
    image = request.files['camera_image']
    image_bytes = io.BytesIO(image.read())
    pil_image = Image.open(image_bytes)
    # pil_image.save(f'./static/{username}_{dt.now().strftime("%Y-%m-%d_%H%M%S")}.jpg')
 
    # img_path = [x for x in os.listdir("./static") if username in x][-1]
    # image = cv2.cvtColor(cv2.imread(os.path.join("./static", img_path)), cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGR2RGB)
     
    qreader = QReader()
    decoded_text = qreader.detect_and_decode(image=image)

    return decoded_text[0]
     
