# import pandas as pd


# komp_pianek= pd.DataFrame(session.query(KOMPLETY_PIANEK.kod, KOMPLETY_PIANEK.magazyn_skladowania).all(), columns=["KOD_ART", "MAGAZYN"]).fillna("BRAK")


# naliczone = pd.read_excel("Z:/450. PLANISTA - ZAOPATRZENIE/DANE_PIANKI_2424.xlsx", sheet_name="NALICZONE", usecols="C,F,Y,Z,AK")
# naliczone["RODZINA"] = naliczone.OPIS_ART.apply(lambda x: x[:3])


CZASY = {
    "ROZLADUNEK_DOSTAWY": ['paczki', 1],
    "ROZLADUNEK_OWATY": ['rolka', 9],
    "WYCINANIE_OWAT": ['metry bierzace', 1.5],
    "WYCINANIE_MEMOWY": 1,
    "SKOSOWANIE_MEMOWY": 1,
    "KONTROLA_JAKOSCI": 12,
    "PAKOWANIE_BOCZKOW": 1.5,
    "DOKLADANIE_OWATY": 1,
    "DOKLADANIE_OWATY_I_MEMORY": 2,
    "ROZŁOZENIE_DOSTAW_NA_MAG": ['wozek', 12],
    "KOMPLETACJA_PACZKI": ['mag', 'bryly'], #czasy zależne od magazynu MAG1:1.4, MAG2:0.9, MAG10:1.1
    "DOCINANIE_ZAMOWIEN_SPECJALNYCH": 1,
    "POPRAWKI_OD_PIANKARZY": 1,
}

# with open("plan_pracy_adam.txt", "r") as f:
#     procesy = f.readlines()

# procesy = {x.split(" ")[0]: x.split(" ")[1].replace("\n", "") for x in procesy}

# _kj = session.query(ZAM_PIANKI.nr_kompletacji, ZAM_PIANKI.opis, ZAM_PIANKI.ile_zam, ZAM_PIANKI.nr_partii).filter(ZAM_PIANKI.nr_partii == procesy["KONTROLA_JAKOSCI"]).all()


def kj_paczki(paczki):
    if paczki <= 10:
        return 1
    elif paczki > 10 and paczki <= 20:
        return 2
    elif paczki > 21 and paczki <= 30:
        return 3
    elif paczki > 31 and paczki <= 40:
        return 4
    elif paczki > 41 and paczki <= 60:
        return 5
    elif paczki > 61 and paczki <= 80:
        return 6
    elif paczki > 81 and paczki <= 100:
        return 7
    elif paczki > 101 and paczki <= 120:
        return 8
    else:
        return 10
    

# kontrola_jakosci = {x[1]: kj_paczki(x[2])*CZASY["KONTROLA_JAKOSCI"] for x in _kj}


def czas_kompletacji(mag,ilosc):
    #czasy zależne od magazynu MAG1:1.4, MAG2:0.9, MAG10:1.1
    if mag == "M1A1" or mag == "M1A2":
        return ilosc * 1.4
    elif mag == "M2":
        return ilosc * 0.9
    elif mag == "M10":
        return ilosc * 1.1
    elif mag == "M11":
        return ilosc * 1
    else:
        return ilosc * 1.1
    
# kompletacja = naliczone[naliczone.LIMIT_NAZWA.str.contains("24/18/01")]#.groupby(["OPIS_ART"])["ZAPOTRZ"].sum().reset_index()
# kompletacja = kompletacja.merge(komp_pianek, on="KOD_ART", how="left")
# kompletacja["CZAS_KOMP"] = kompletacja.apply(lambda x: czas_kompletacji(x.MAGAZYN, x.ZAPOTRZ), axis=1)