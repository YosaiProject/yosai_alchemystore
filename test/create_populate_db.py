from yosai_alchemystore import (
    Base,
    engine,
)

Base.metadata.create_all(engine)

parties = [Party(first_name='George', last_name='Washington'),
           Party(first_name='Mahatma', last_name='Gandhi'),
           Party(first_name='Nelson', last_name='Mandela'),
           Party(first_name='Mao', last_name='Zedong'),
           Party(first_name='Winston', last_name='Churchill')]

users = [User()]
