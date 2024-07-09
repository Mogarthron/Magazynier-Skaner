from baza_mip import mip_session
from baza_mip.models import Procesy_Przydzielone
from sqlalchemy import create_engine, text
from Plan_Pracy.plan_pracy import kj_paczki

gen_engine = create_engine("sqlite:///Z:/450. PLANISTA - ZAOPATRZENIE/GENERATORY.db", echo=False)

#dostawy
with gen_engine.begin() as conn:
    suma_paczek = conn.execute(text("select SUM(ILE_ZAMOWIONE) from ZAM_PIANKI where nr_SAMOCHODU == 'PIANPOL 14_24*'")).fetchall()[0][0]
    zamowione_paczki = conn.execute(text("select NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE, ZAM1, ZAM2 from ZAM_PIANKI where nr_SAMOCHODU == 'PIANPOL 14_24*'")).fetchall()



def dodaj_KJ(zamowione_paczki):
    for row in zamowione_paczki:
        # print(row[0], row[1], row[2], row[3], row[4])
        print(f"KONTROLA JAKOSCI: {row[1]} - {row[2]}| NR_DOS {row[3]}", ",", kj_paczki(row[2])*12)

print("KONTROLA JAKOSCI:")
dodaj_KJ(zamowione_paczki)
print()
# print(suma_paczek, suma_paczek/2)
# print(zamowione_paczki)

#eliza 5
#adamr 4
#piotrl 8

# mip_session.add(Procesy_Przydzielone(4, 5, 1, "ROZLADUNEK PIANPOL 14_24*", "2024-07-09", 155))
# mip_session.add(Procesy_Przydzielone(8, 5, 1, "ROZLADUNEK PIANPOL 14_24*", "2024-07-09", 155))
# mip_session.add(Procesy_Przydzielone(4, 5, 1, "KONTROLA JAKOSCI: LENOX [1o] - 70| NR_DOS 24/0583", "2024-07-09", 72))
# mip_session.add(Procesy_Przydzielone(4, 5, 1, "KONTROLA JAKOSCI: LENOX [1H] - 120| NR_DOS 24/0583", "2024-07-09", 96))

#mip_session.commit()
