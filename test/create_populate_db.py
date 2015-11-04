from yosai_alchemystore import (
    engine,
    Base
)

from sqlalchemy.schema import CreateSchema

Base.metadata.create_all(engine)

engine.execute(CreateSchema('security'))

Party(first_name='George', last_name='Washington'),
           Party(first_name='Mahatma', last_name='Gandhi'),
           Party(first_name='Nelson', last_name='Mandela'),
           Party(first_name='Mao', last_name='Zedong'),
           Party(first_name='Winston', last_name='Churchill')]

users = [User(
