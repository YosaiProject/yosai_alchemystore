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
    Credentials,
    Domain,
    Action,
    Resource,
    Permission,
    Role,
    RolePermission,
    RoleMembership,
)

from sqlalchemy import case


class AlchemyAccount:
    pass


def session_context(fn):
    """
    Handles session setup and teardown
    """
    @functools.wraps(fn)
    def wrap(*args, **kwargs):

        session = Session()
        fn(session, *args, **kwargs)
        session.close()

    return wrap


# account_abcs.CredentialsAccountStore, account_abcs.AuthorizationAccountStore
class AlchemyAccountStore:
    """
    AlchemyAccountStore provides the realm-facing API to the relational database
    that is managed through the SQLAlchemy ORM.

    step 1:  generate an orm query
    step 2:  execute the query
    step 3:  return results
    """

    def __init__(self, session):
        pass

    @session_context
    def get_account(self, session, authc_token):
        """
        :param authc_token:  the request object defining the criteria by which
                             to query the account store
        :type authc_token:  AuthenticationToken

        :returns: Account
        """
        identifier = authc_token.identifier

        credential_query = session.query(Credential.password).filter(
            Credential.user_id == identifier)
        credential = credential_query.scalar()

        permissions_query = session.query(Permission).
            join(RolePermission, Permission.pk_id == RolePermission.role_id)

        account = AlchemyAccount(account_id=identifier,
                                 credentials=credentials,
                                 permissions=permissions,
                                 roles=roles)

        return account

    @session_context
    def get_credentials(self, authc_token):
        """
        :returns: Account
        """
        credentials_query = session.query(Credential.password).filter(
            Credential.user_id == identifier)

        credentials = credentials_query.scalar()

        credentials = self.handler.get_credentials(...)
        account = Account(account_id=account_id,
                          credentials=credentials)

        return account


    @session_context
    def get_authz_info(self, identifiers):
        """
        :returns: Account
        """
        permissions = self.get_permissions(identifiers)
        roles = self.get_roles(identifiers)
        account = Account(account_id=account_id,
                          permissions=privileges,
                          roles=roles)
        return account

    @session_context
    def get_permissions(self, identifiers):
        self.handler.get_permissions(identifiers)

    @session_context
    def get_roles(self, identifiers):
        self.handler.get_roles(identifiers)

    def get_permissions_query(self):

        domain = case([(domain.c.name is None, '*')], else_=domain.c.name)
        action = case([(action.c.name is None, '*')], else_=action.c.name)
        resource = case([(resource.c.name is None, '*')], else_=resource.c.name)


SELECT ( CASE WHEN DOMAIN.name IS NULL THEN '*' ELSE DOMAIN.name END )
        || ':' ||
        group_concat ( DISTINCT ( CASE WHEN ACTION.name IS NULL THEN '*' ELSE ACTION.name END ) )
        || ':' ||
        group_concat ( DISTINCT ( CASE WHEN RESOURCE.name IS NULL THEN '*' ELSE RESOURCE.name END ) ) AS PERMISSION
FROM
    PERMISSION
    LEFT OUTER JOIN ACTION ON PERMISSION.action_id = ACTION.pk_id
    LEFT OUTER JOIN DOMAIN ON PERMISSION.domain_id = DOMAIN.pk_id
    LEFT OUTER JOIN RESOURCE ON PERMISSION.resource_id = RESOURCE.pk_id
GROUP BY
    PERMISSION.domain_id,
    PERMISSION.resource_id;
