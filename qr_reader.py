from qreader import QReader
import cv2


# Create a QReader instance
qreader = QReader()

# Get the image that contains the QR code
image = cv2.cvtColor(cv2.imread("./static/2024-06-19_112039.jpg"), cv2.COLOR_BGR2RGB)

# Use the detect_and_decode function to get the decoded QR data
decoded_text = qreader.detect_and_decode(image=image)

print(decoded_text[0])