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

from accountstore import (
    Session,
)

from models import (
    Party,
    User,
    Credential,
    Domain,
    Action,
    Resource,
    Permission,
    Role,
    role_permission,
    role_membership,
    authz_abcs,
)

from sqlalchemy import case, func
import functools


class AlchemyAccount:
    pass


def session_context(fn):
    """
    Handles session setup and teardown
    """
    @functools.wraps(fn)
    def wrap(*args, **kwargs):

        session = Session()
        fn(*args, session=session, **kwargs)
        session.close()

    return wrap


# account_abcs.CredentialsAccountStore, account_abcs.AuthorizationAccountStore
class AlchemyAccountStore(authz_abcs.PermissionResolverAware,
                          authz_abcs.RoleResolverAware):
    """
    AlchemyAccountStore provides the realm-facing API to the relational database
    that is managed through the SQLAlchemy ORM.

    step 1:  generate an orm query
    step 2:  execute the query
    step 3:  return results
    """

    def __init__(self, permission_resolver=None, role_resolver=None):
        """
        Since KeyedTuple permissions records have to be converted to an object
        that yosai can use, it might as well be actual Permission objects.
        """
        self._permission_resolver = None  # setter-injected after init
        self._role_resolver = None   # setter-injected after init

    @property
    def permission_resolver(self):
        return self._permission_resolver

    @permission_resolver.setter
    def permission_resolver(self, permissionresolver):
        self._permission_resolver = permissionresolver

    def get_permissions_query(self, session, identifier):
        """
        :type identifier: string
        """
        thedomain = case([(Domain.name == None, '*')], else_=Domain.name)
        theaction = case([(Action.name == None, '*')], else_=Action.name)
        theresource = case([(Resource.name == None, '*')], else_=Resource.name)

        action_agg = func.group_concat(theaction.distinct())
        resource_agg = func.group_concat(theresource.distinct())
        perm = (thedomain + ':' + action_agg + ':' + resource_agg).label("perm")

        return (session.query(perm).
                select_from(User).
                join(role_membership, User.pk_id == role_membership.c.user_id).
                join(role_permission, role_membership.c.role_id == role_permission.c.role_id).
                join(Permission, role_permission.c.permission_id == Permission.pk_id).
                outerjoin(Domain, Permission.domain_id == Domain.pk_id).
                outerjoin(Action, Permission.action_id == Action.pk_id).
                outerjoin(Resource, Permission.resource_id == Resource.pk_id).
                filter(User.identifier == identifier).
                group_by(Permission.domain_id, Permission.resource_id))


    def get_roles_query(self, session, identifier):
        """
        :type identifier: string
        """
        return (session.query(Role).
                join(role_membership, Role.pk_id == role_membership.role_id).
                join(User, role_membership.user_id == User.pk_id).
                filter(User.identifier == identifier))

    def get_credential_query(self, session, identifier):
        return (session.query(Credential.password).
                join(User, Credential.user_id == User.pk_id).
                filter(User.identifier == identifier))

    @session_context
    def get_account(self, authc_token, session=None):
        """
        :param authc_token:  the request object defining the criteria by which
                             to query the account store
        :type authc_token:  AuthenticationToken

        :returns: Account
        """
        identifier = authc_token.identifier

        credential = (self.get_credential_query(session, identifier).
                      scalar().credential)

        perms = self.get_permissions_query(session, identifier).all()
        permissions = {self.permission_resolver(permission=p.perm)
                       for p in perms}

        roles = {self.role_resolver(title=r.title)
                 for r in self.get_roles_query(session, identifier).all()}

        account = AlchemyAccount(account_id=identifier,
                                 credentials=credential,
                                 permissions=permissions,
                                 roles=roles)

        return account

    @session_context
    def get_credentials(self, authc_token, session=None):
        """
        :returns: Account
        """
        identifier = authc_token.identifier

        credential = self.get_credential_query(session, identifier).scalar()

        account = AlchemyAccount(account_id=identifier,
                                 credentials=credential)

        return account

    @session_context
    def get_authz_info(self, identifier, session=None):
        """
        :returns: Account
        """
        identifier = authc_token.identifier

        permissions = self.get_permissions_query(session, identifier).all()
        roles = self.get_roles_query(session, identifier).all()

        account = AlchemyAccount(account_id=identifier,
                                 permissions=permissions,
                                 roles=roles)

        return account
