import qrcode

# qr = qrcode.QRCode(version=1, box_size=10, border=5)

# # Define the vCard data
# vcard = """BEGIN:VCARD
# VERSION:4.0
# FN:John Smith
# ORG:Example Company
# TITLE:CEO
# TEL;TYPE=WORK,VOICE:(555) 555-5555
# EMAIL;TYPE=PREF,INTERNET:john.smith@example.com
# URL:https://www.example.com
# END:VCARD"""

# # Add the vCard data to the QR code object
# qr.add_data(vcard)

# # Make the QR code
# qr.make(fit=True)

# # Create an image from the QR code
# img = qr.make_image(fill_color="black", back_color="white")

# # Save the QR code image
# img.save("qr_code_vcard.png")

kody = ["AVA/123654", "AVA/456987", "MAX/963258", "OVA/741258", "WIL/654239", "HOR/125687", "GOY/555555"]
for kod in kody:
    img = qrcode.make(kod)
    # type(img)  # qrcode.image.pil.PilImage
    img.save(f"{kod.replace('/', '_')}.png")