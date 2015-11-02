from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine("sqlite:///yosai.db", echo=True)

Session = sessionmaker(bind=engine)
session = Session()
