from sqlalchemy import (Column, Date, DateTime, ForeignKey, Integer, String, 
                        Text, text)
from sqlalchemy.orm import relationship
from meta import Base


class Party(Base):
    __tablename__ = 'party'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('party.party_pk_id_seq'::regclass)"))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('security.user_pk_id_seq'::regclass)"))
    party_id = Column(ForeignKey('party.party.pk_id'), nullable=False, unique=True)
    identifier = Column(String(255), nullable=False, unique=True)

    party = relationship('Party')


class Credentials(Base):
    __tablename__ = 'credentials'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('security.credentials_pk_id_seq'::regclass)"))
    user_id = Column(ForeignKey('security.user.pk_id'), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    expiration_dt = Column(DateTime(timezone=True), nullable=False)

    user = relationship('User')


class Permission(Base):
    __tablename__ = 'permission'
    __table_args__ = (
        {'schema': 'security'}
    )

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('security.permission_pk_id_seq'::regclass)"))
    domain = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    instance = Column(String(100), nullable=False)


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('security.role_pk_id_seq'::regclass)"))
    title = Column(String(100))


class Privilege(Base):
    __tablename__ = 'privilege'
    __table_args__ = (
        {'schema': 'security'}
    )

    pk_id = Column(Integer, primary_key=True, server_default=text("nextval('security.privilege_pk_id_seq'::regclass)"))
    role_id = Column(ForeignKey('security.role.pk_id'), nullable=False)
    permission_id = Column(ForeignKey('security.permission.pk_id'), nullable=False)

    permission = relationship('Permission')
    role = relationship('Role')

    def __repr__(self):
        return "<Privilege(pk_id={0},role_id={1},permission_id={2},"\
               .format(self.pk_id, self.role_id, self.permission_id)

