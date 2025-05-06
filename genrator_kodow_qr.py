from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab_qrcode import QRCodeImage


canvas = Canvas("oznaczenia miesjca.pdf")


def oznaczenie_miejsca_magazynowego(oznacz2, oznacz1):
    """
    funkcja rysujaca stone A4 z dwoma miejscami magazynowymi (nynerem miejsce i kodem QR)
    oznaczenia są rozmoeszczne wertykalnie jedno u góry strony drugie na dole
    """
    canvas.setFont(psfontname="Helvetica-Bold", size=70)

    canvas.drawString(6*cm, 1*cm, oznacz1)
    qr = QRCodeImage(oznacz1, size=10*cm, border=1)
    qr.drawOn(canvas, 6*cm, 3*cm)

    canvas.drawString(6*cm, 17*cm, oznacz2)
    qr = QRCodeImage(oznacz2, size=10*cm, border=1)
    qr.drawOn(canvas, 6*cm, 19*cm)

def oznaczenia_na_wozki(wozek1, wozek2):
    """
    funkcja rysujaca stone A4 z dwoma oznaczenami wózkow (nynerem komisja i kodem QR)
    oznaczenia są rozmoeszczne wertykalnie jedno u góry strony drugie na dole
    """
    canvas.setFont(psfontname="Helvetica-Bold", size=85)

    canvas.drawString(2*cm, 1*cm, wozek1)
    qr = QRCodeImage(wozek1, size=10*cm, border=1)
    qr.drawOn(canvas, 6*cm, 4*cm)

    canvas.drawString(2*cm, 17*cm, wozek2)
    qr = QRCodeImage(wozek2, size=10*cm, border=1)
    qr.drawOn(canvas, 6*cm, 20*cm)







def naklejki_zebra(data:list, cnvs:Canvas, owaty=True, wys=9.6, szer=16.0):

    cnvs.setFont(psfontname="Helvetica", size=10)
    cnvs.setPageSize((szer*cm,wys*cm))
    cnvs.drawString(1*cm, 9*cm, f"NR PARTII: {data[3]}")
    if owaty:
        cnvs.drawString(8*cm, 9*cm, "OWATY")
    else:
        cnvs.drawString(6*cm, 9*cm, f"NR KOMPL: {data[1]}")

    cnvs.drawString(12*cm, 9*cm, f"NR PACZKI: {data[-1]}")

    cnvs.setFont(psfontname="Helvetica-Bold", size=60)
    cnvs.drawString(1*cm, 6*cm, f"{data[0]}")
    if len(data[2])>5:
        cnvs.setFont(psfontname="Helvetica-Bold", size=45)
        cnvs.drawString(1*cm, 4*cm, f"{data[2]}")
    else:
        cnvs.drawString(5*cm, 4*cm, f"{data[2]}")

    cnvs.setFont(psfontname="Helvetica", size=10)
    cnvs.drawString(1*cm, 2*cm, "PACZKA JAKOSC")
    cnvs.drawString(1*cm, 1*cm, "NR PRAC")

    cnvs.drawString(8*cm, 2*cm, "UWAGI")
    cnvs.drawString(12*cm, 2*cm, "NR PAKUJACEGO")

# def naklejki_zebra_pianki(data:list, wys=9.6, szer=16.0):

#     canvas.setFont(psfontname="Helvetica-Bold", size=12)
#     canvas.setPageSize((szer*cm,wys*cm))
#     canvas.drawString(1*cm, 9*cm, f"NR PARTII: {data[3]}")
#     canvas.drawString(6*cm, 9*cm, f"NR KOMPL: {data[1]}")
#     canvas.drawString(12*cm, 9*cm, f"NR PACZKI: {data[-1]}")

#     canvas.setFont(psfontname="Helvetica-Bold", size=60)
#     canvas.drawString(1*cm, 6*cm, f"{data[0]}")
#     if len(data[2])>5:
#         canvas.setFont(psfontname="Helvetica-Bold", size=45)
#         canvas.drawString(1*cm, 4*cm, f"{data[2]}")
#     else:
#         canvas.drawString(5*cm, 4*cm, f"{data[2]}")

#     canvas.setFont(psfontname="Helvetica", size=10)
#     canvas.drawString(1*cm, 2*cm, "PACZKA JAKOSC")
#     canvas.drawString(1*cm, 1*cm, "NR PRAC")

#     canvas.drawString(8*cm, 2*cm, "UWAGI")
#     canvas.drawString(12*cm, 2*cm, "NR PAKUJACEGO")


# from komisje import _komisje
# komisje = [x for x in _komisje.split("\n") if len(x)>0]

# for i in range(0, len(komisje), 2):
  
#     oznaczenia_na_wozki(komisje[i], komisje[i+1])
#     canvas.showPage()


oznaczenie_miejsca_magazynowego("M01.A09", "M01.A08")
canvas.showPage()
oznaczenia_na_wozki("125/12", "125/13")
canvas.showPage()


canvas.save()

