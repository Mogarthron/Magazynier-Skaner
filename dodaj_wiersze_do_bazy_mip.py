from baza_mip import mip_engine, Base, mip_session
from baza_mip.models import *

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

pianpol = [
["GOYA 1",	20],
["GOYA 1,5",	20],
["GOYA [1",	30],
["GOYA [1,5",	30],
["GOYA N",	20],
["GOYA [L/[LH",	20],
["GOYA P112x100",	10],
["GOYA P112x80",	10],
["OVAL [1o]",	150]
]


for p in pianpol:
    nazwa_procesu = f"KJ PIANPOL 14_24 {p[0]}, {p[1]}SZT"
    print(p, kj_paczki(p[1])*12, nazwa_procesu)
    # mip_session.add(Procesy_Przydzielone(4,5,2,nazwa_procesu, "2024-07-05", kj_paczki(p[1])*12))


# mip_session.add(Procesy_Przydzielone(4,5,1,"KONTROLA JAKOSCI 23/01 NR SAMOCHODU VITA 09_24", "2024-07-08"))
# mip_session.add(Procesy_Przydzielone(4,5,2,"KONTROLA JAKOSCI 23/01 NR SAMOCHODU VITA 09_24", "2024-07-08"))

mip_session.commit()