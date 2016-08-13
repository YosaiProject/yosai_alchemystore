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
from yosai_alchemystore import (
    init_session
)

from yosai_alchemystore.models.models import (
    CredentialModel,
    UserModel,
    DomainModel,
    ActionModel,
    ResourceModel,
    PermissionModel,
    RoleModel,
    role_membership as role_membership_table,
    role_permission as role_permission_table,
)

from yosai.core import (
    Account,
    account_abcs,
    authc_abcs,
    authz_abcs,
)

from sqlalchemy import case, func
import functools


def session_context(fn):
    """
    Handles session setup and teardown
    """
    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        session = args[0].Session()  # obtain from self
        result = fn(*args, session=session, **kwargs)
        session.close()
        return result
    return wrap


class AlchemyAccountStore(authz_abcs.AuthzInfoResolverAware,
                          authz_abcs.PermissionResolverAware,
                          authz_abcs.RoleResolverAware,
                          authc_abcs.CredentialResolverAware,
                          account_abcs.CredentialsAccountStore,
                          account_abcs.AuthorizationAccountStore):
    """
    AccountStore provides the realm-facing API to the relational database
    that is managed through the SQLAlchemy ORM.

    step 1:  generate an orm query
    step 2:  execute the query
    step 3:  return results
    """

    def __init__(self, db_url=None, session=None, settings=None):
        """
        :param db_url: engine configuration that is in the
                       'Database URL' format as supported by SQLAlchemy:
            http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
        :type db_url: string
        """
        self._authz_info_resolver = None
        self._permission_resolver = None  # setter-injected after init
        self._role_resolver = None   # setter-injected after init
        self._credential_resolver = None    # setter-injected after init
        if session is None:
            self.Session = init_session(db_url=db_url, settings=settings)
        else:
            self.Session = session

    @property
    def authz_info_resolver(self):
        return self._authz_info_resolver

    @authz_info_resolver.setter
    def authz_info_resolver(self, authz_info_resolver):
        self._authz_info_resolver = authz_info_resolver

    @property
    def permission_resolver(self):
        return self._permission_resolver

    @permission_resolver.setter
    def permission_resolver(self, permissionresolver):
        self._permission_resolver = permissionresolver

    @property
    def role_resolver(self):
        return self._role_resolver

    @role_resolver.setter
    def role_resolver(self, roleresolver):
        self._role_resolver = roleresolver

    @property
    def credential_resolver(self):
        return self._credential_resolver

    @credential_resolver.setter
    def credential_resolver(self, credentialresolver):
        self._credential_resolver = credentialresolver

    def get_permissions_query(self, session, identifier):
        """
        :type identifier: string
        """
        thedomain = case([(DomainModel.name == None, '*')], else_=DomainModel.name)
        theaction = case([(ActionModel.name == None, '*')], else_=ActionModel.name)
        theresource = case([(ResourceModel.name == None, '*')], else_=ResourceModel.name)

        action_agg = func.group_concat(theaction.distinct())
        resource_agg = func.group_concat(theresource.distinct())
        perm = (thedomain + ':' + action_agg + ':' + resource_agg).label("perm")

        return (session.query(perm).
                select_from(UserModel).
                join(role_membership_table, UserModel.pk_id == role_membership_table.c.user_id).
                join(role_permission_table, role_membership_table.c.role_id == role_permission_table.c.role_id).
                join(PermissionModel, role_permission_table.c.permission_id == PermissionModel.pk_id).
                outerjoin(DomainModel, PermissionModel.domain_id == DomainModel.pk_id).
                outerjoin(ActionModel, PermissionModel.action_id == ActionModel.pk_id).
                outerjoin(ResourceModel, PermissionModel.resource_id == ResourceModel.pk_id).
                filter(UserModel.identifier == identifier).
                group_by(PermissionModel.domain_id, PermissionModel.resource_id))

    def get_roles_query(self, session, identifier):
        """
        :type identifier: string
        """
        return (session.query(RoleModel).
                join(role_membership_table, RoleModel.pk_id == role_membership_table.c.role_id).
                join(UserModel, role_membership_table.c.user_id == UserModel.pk_id).
                filter(UserModel.identifier == identifier))

    def get_credential_query(self, session, identifier):
        return (session.query(CredentialModel.credential).
                join(UserModel, CredentialModel.user_id == UserModel.pk_id).
                filter(UserModel.identifier == identifier))

    @session_context
    def get_credentials(self, identifier, session=None):
        """
        :returns: Account
        """
        creds = self.get_credential_query(session, identifier).scalar()
        credentials = self.credential_resolver.resolve(creds)

        if not credentials:
            return None

        account = Account(account_id=identifier, credentials=credentials)

        return account

    @session_context
    def get_authz_info(self, identifier, session=None):
        """
        :returns: Account
        """

        try:
            perms = self.get_permissions_query(session, identifier).all()

            permissions = {self.permission_resolver(permission=p.perm)
                           for p in perms}
        except (AttributeError, TypeError):
            permissions = None

        try:
            roles = {self.role_resolver(r.title)
                     for r in self.get_roles_query(session, identifier).all()}
        except (AttributeError, TypeError):
            roles = None

        if not permissions and not roles:
            return None

        authz_info = self.authz_info_resolver(roles=roles,
                                              permissions=permissions)

        account = Account(account_id=identifier,
                          authz_info=authz_info)

        return account

#    @session_context
#    def get_account(self, identifier, session=None):
#        """
#        get_account performs the most comprehensive collection of information
#        from the database, including credentials AND authorization information
#
#        :param identifier:  the request object's identifier
#        :returns: Account
#
#        CAUTION
#        --------
#        This method was initially created as part of shiro porting but is
#        not intended for v0.1.0 use due to lack of support for get_or_create_multi
#        dogpile locking. If you would like to use get_account, you *should*
#        implement an appropriate get_or_create_multi caching process (and submit
#        the changes as pull requests to yosai!).  Without dogpile protection,
#        you run the risk of concurrently calling the most expensive creational
#        process
#
#        """
#        cred = self.get_credential_query(session, identifier).scalar()
#        credential = self.credential_resolver(cred)
#
#        roles = {self.role_resolver(r.title)
#                 for r in self.get_roles_query(session, identifier).all()}
#
#        perms = self.get_permissions_query(session, identifier).all()
#        permissions = {self.permission_resolver(permission=p.perm)
#                       for p in perms}
#
#        authz_info = self.authz_info_resolver(roles=roles,
#                                              permissions=permissions)
#
#        account = Account(account_id=identifier,
#                          credentials=credential,
#                          authz_info=authz_info)
#
#        return account
