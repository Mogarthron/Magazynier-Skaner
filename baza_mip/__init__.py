from sqlalchemy import create_engine, text
from sqlalchemy import update, insert, delete
from sqlalchemy import URL

from sqlalchemy.orm import sessionmaker, declarative_base
import json

with open("config.json", "r") as c:
    mip_url = json.load(c)["MIP_URL"]

url_obj = URL.create("mysql+mysqlconnector",
                     username=mip_url["username"],
                     password=mip_url["password"],
                     host=mip_url["host"],
                     port=mip_url["port"],
                     database=mip_url["database"]
                     )

mip_engine = create_engine(url_obj, echo=False, pool_pre_ping=True)

# mip_engine = create_engine("sqlite:///BAZA_MIP.db", echo=False)

Base = declarative_base()



Base.metadata.create_all(bind=mip_engine)

Session = sessionmaker(bind=mip_engine)
mip_session = Session()
