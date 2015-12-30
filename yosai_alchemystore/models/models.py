"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

"""
models.py features a basic, non-hierarchical, non-constrained RBAC data model,
also known as a flat model
-- Ref:  http://csrc.nist.gov/rbac/sandhu-ferraiolo-kuhn-00.pdf

+-----------------+          +-------------------+          +---------------+
|                 |          |                   |          |               |
|                 |          |    R o l e        |          |               |
|    R o l e      +----------+    PermissionModel     +----------+   PermissionModel  |
|                 |          |                   |          |               |
+-----------------+          +-------------------+          +---------------+


+-----------------+          +-------------------+          +---------------+
|                 |          |                   |          |               |
|                 |          |    R o l e        |          |               |
|    U s e r      +----------+    Membership     +----------+   R o l e     |
|                 |          |                   |          |               |
+-----------------+          +-------------------+          +---------------+

"""

import itertools
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from yosai_alchemystore import (
    Base
)

role_permission = Table(
    'role_permission', Base.metadata,
    Column('role_id', ForeignKey('role.pk_id'), primary_key=True),
    Column('permission_id', ForeignKey('permission.pk_id'), primary_key=True)
)

role_membership = Table(
    'role_membership', Base.metadata,
    Column('role_id', ForeignKey('role.pk_id'), primary_key=True),
    Column('user_id', ForeignKey('user.pk_id'), primary_key=True)
)


class UserModel(Base):
    __tablename__ = 'user'

    pk_id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    identifier = Column(String(255), nullable=False, unique=True)

    roles = relationship('RoleModel',
                         secondary=role_membership,
                         backref='users')

    perms = association_proxy('roles', 'permissions')

    @property
    def permissions(self):
        return list(itertools.chain(*self.perms))

    def __repr__(self):
        return "UserModel(identifier={0})".format(self.identifier)


class CredentialModel(Base):
    __tablename__ = 'credential'

    pk_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.pk_id'), nullable=False, unique=True)
    credential = Column(String, nullable=False)
    expiration_dt = Column(DateTime(timezone=True), nullable=False)

    user = relationship('UserModel',
                        backref='credential',
                        cascade="all, delete-orphan",
                        single_parent=True)

    def __repr__(self):
        return "CredentialModel(user_id={0})".format(self.user_id)


class DomainModel(Base):
    __tablename__ = 'domain'

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "DomainModel(pk_id={0}, name={1})".format(self.pk_id, self.name)


class ActionModel(Base):
    __tablename__ = 'action'

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "ActionModel(pk_id={0}, name={1})".format(self.pk_id, self.name)


class ResourceModel(Base):
    __tablename__ = 'resource'

    pk_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return "ResourceModel(pk_id={0}, name={1})".format(self.pk_id, self.name)


class PermissionModel(Base):
    __tablename__ = 'permission'

    pk_id = Column(Integer, primary_key=True)
    domain_id = Column(ForeignKey('domain.pk_id'), nullable=True)
    action_id = Column(ForeignKey('action.pk_id'), nullable=True)
    resource_id = Column(ForeignKey('resource.pk_id'), nullable=True)

    domain = relationship('DomainModel',
                          backref='permission')

    action = relationship('ActionModel',
                          backref='permission')

    resource = relationship('ResourceModel',
                            backref='permission')

    roles = relationship('RoleModel', secondary=role_permission,
                         backref='permissions')


    users = association_proxy('roles', 'users')

    def __repr__(self):
        return ("PermissionModel(domain_id={0},action_id={1},resource_id={2})".
                format(self.domain_id, self.action_id, self.resource_id))


# The RoleModel orm model will inherit from yosai.SimpleRoleModel once
# preliminary testing is finished:
class RoleModel(Base):
    __tablename__ = 'role'

    pk_id = Column(Integer, primary_key=True)
    title = Column(String(100))

    def __repr__(self):
        return "RoleModel(title={0})".format(self.title)
