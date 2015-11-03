from sqlalchemy import (Column, Date, DateTime, ForeignKey, Integer, String, 
                        Text, text)
from sqlalchemy.orm import relationship
from meta import Base
# from yosai import DefaultPermission, SimpleRole

class Party(Base):
    __tablename__ = 'party'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    party_id = Column(ForeignKey('security.party.pk_id'), nullable=False, unique=True)
    identifier = Column(String(255), nullable=False, unique=True)

    party = relationship('Party')


class Credentials(Base):
    __tablename__ = 'credentials'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('security.user.pk_id'), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    expiration_dt = Column(DateTime(timezone=True), nullable=False)

    user = relationship('User')


class Domain(Base):
    __tablename__ = 'domain'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "Domain(name={0})".format(self.name)


class Action(Base):
    __tablename__ = 'action'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "Action(name={0})".format(self.name)


class Resource(Base):
    __tablename__ = 'resource'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "Resource(name={0})".format(self.name)

# The Permission orm model will inherit from yosai.DefaultPermission once
# preliminary testing is finished:
class Permission(Base):
    __tablename__ = 'permission'
    __table_args__ = (
        {'schema': 'security'}
    )

    pk_id = Column(Integer, primary_key=True)
    domain = Column(Column(ForeignKey('security.domain.pk_id'), nullable=False)
    action = Column(Column(ForeignKey('security.action.pk_id'), nullable=False)
    resource = Column(Column(ForeignKey('security.resource.pk_id'), nullable=False)


# The Role orm model will inherit from yosai.SimpleRole once
# preliminary testing is finished:
class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'security'}

    pk_id = Column(Integer, primary_key=True)
    title = Column(String(100))


class RolePermission(Base):
    __tablename__ = 'role_permission'
    __table_args__ = (
        {'schema': 'security'}
    )

    pk_id = Column(Integer, primary_key=True)
    role_id = Column(ForeignKey('security.role.pk_id'), nullable=False)
    permission_id = Column(ForeignKey('security.permission.pk_id'), nullable=False)

    permission = relationship('Permission')
    role = relationship('Role')

    def __repr__(self):
        return "<RolePermission(pk_id={0},role_id={1},permission_id={2},"\
               .format(self.pk_id, self.role_id, self.permission_id)


class RoleMembership(Base):
    __tablename__ = 'role_membership'
    __table_args__ = (
        {'schema': 'security'}
    )

    pk_id = Column(Integer, primary_key=True)
    role_id = Column(ForeignKey('security.role.pk_id'), nullable=False)
    user_id = Column(ForeignKey('security.user.pk_id'), nullable=False)

    def __repr__(self):
        return "<RoleMembership(pk_id={0},role_id={1},user_id={2},"\
               .format(self.pk_id, self.role_id, self.user_id)

