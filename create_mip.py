from baza_mip import mip_engine, mip_session, Base
from baza_mip.models import *


Base.metadata.create_all(bind=mip_engine)

#procesy piankowanie
# mip_session.add(Procesy("ROZLADUNEK DOSTAWY PACZEK PIANEK", 1, "ROZLADUNEK PACZEK PIANEK Z SAMOCHODU OKOLO 1MIN NA PACZKE", "160_01"))
# mip_session.add(Procesy("KONTROLA JAKOSCI PACZEK PIANEK", 12, "KANTROLA JAKOSCI PACZEK Z DOSTAWY", "160_02"))
# mip_session.add(Procesy("DOKLADANIE OWAT I PIENEK", 1, "DOKLADANIE OWAT DO PACZEK PIANEK", "160_03"))
# mip_session.add(Procesy("DOKLADANIE OWAT, PIENEK I MEMORY", 2, "DOKLADANIE OWAT I WYCIETYCH FORAMTEK MEMORY DO PACZEK PIANEK", "160_04"))
# mip_session.add(Procesy("ROZLOZENIE NA MAGAZYNIE PACZEK PIANEK", None, "ALOKACJA PACZEK PIANEK NA MAGAZYNACH", "160_05"))
# mip_session.add(Procesy("KOMPLETACJA POD STELARZE PACZEK PIANEK", None, "KOMPLETACJA PACZEK WG ZLECENIA", "160_06"))
# mip_session.add(Procesy("DOCINANIE ZAMOWIEN SPECJALNYCH, REKLAMACJE", None, None, "160_07"))
# mip_session.add(Procesy("POPRAWKI OD PIANKARZY", None, "NR PIANKARZA, NR WADY, OPIS", "160_08"))
# mip_session.add(Procesy("WYCINANIE OWAT", None, "1.5MIN NA METR BIERZACY", "160_09"))
# mip_session.add(Procesy("WYCINANIE MEMORY", None, "1MIN NA PACZKE", "160_10"))
# mip_session.add(Procesy("ROZLADUNEK DOSTAWY OWAT", 9, "ROZLADUNEK ROLEK OWAT Z SAMOCHODU OKOLO 9 MINUT NA ROLKE", "160_11"))

#procesy Inne
# mip_session.add(Procesy("ODPADY", None, "", "000_01"))
mip_session.commit()