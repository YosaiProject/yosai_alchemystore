from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine("sqlite:///yosai.db", echo=True)

Session = scoped_session(sessionmaker(bind=engine))
session = Session()
