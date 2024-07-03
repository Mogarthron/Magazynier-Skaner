from baza_mip import mip_engine, Base
from baza_mip.models import *


Base.metadata.create_all(bind=mip_engine)