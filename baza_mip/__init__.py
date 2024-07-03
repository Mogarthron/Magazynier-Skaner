from sqlalchemy import create_engine, text
from sqlalchemy import update, insert, delete
from sqlalchemy import URL

from sqlalchemy.orm import sessionmaker, declarative_base

# url_obj = URL.create("mysql+pymysql",
url_obj = URL.create("mysql+mysqlconnector",
                     username="root",
                     password="password",
                     host="127.0.0.1",
                     port="3306",
                     database="BAZA_MIP"
                     )

mip_engine = create_engine(url_obj, echo=False)

# mip_engine = create_engine("mysql+mysqlconnector://root:password@127.0.0.1/BAZA_MIP", echo=False)

# mip_engine = create_engine("sqlite:///Z:/450. PLANISTA - ZAOPATRZENIE/BAZA_MIP.db", echo=False)

Base = declarative_base()



Base.metadata.create_all(bind=mip_engine)

Session = sessionmaker(bind=mip_engine)
mip_session = Session()
