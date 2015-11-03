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

from .meta import (
    session,
)


class AlchemyAccount:
    pass

# account_abcs.CredentialsAccountStore, account_abcs.AuthorizationAccountStore
class AlchemyAccountStore:
    """
    AlchemyAccountStore provides the realm-facing API.  It parcels query
    results and returns them to its corresponding realm.
    """

    def __init__(self):
        self.handler = QueryHandler()

    def get_account(self, authc_token):
        """
        :param authc_token:  the request object defining the criteria by which
                             to query the account store
        :type authc_token:  AuthenticationToken

        :returns: Account
        """
        credentials = self.handler.get_credentials(...)
        permissions = self.get_permissions(identifiers)
        roles = self.get_roles(identifiers)
        account = AlchemyAccount(account_id=account_id,
                                 credentials=credentials,
                                 permissions=permissions,
                                 roles=roles)

        return account

    def get_credentials(self, authc_token):
        """
        :returns: Account
        """
        account_id = authc_token.account_id
        credentials = self.handler.get_credentials(...)
        account = Account(account_id=account_id,
                          credentials=credentials)

        return account


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

    def get_permissions(self, identifiers):
        self.handler.get_permissions(identifiers)

    def get_roles(self, identifiers):
        self.handler.get_roles(identifiers)


class QueryHandler:
    """
    Facilitates requests from the AccountStore to the Database

    step 1:  generate an orm query
    step 2:  execute the query
    step 3:  return results
    """

    def get_credentials(self, authc_token):
        pass

    def get_permissions(self, identifiers):
        pass

    def get_roles(self, identifiers):
        pass


class QueryGenerator:
    """
    Generates the ORM queries that facilitate the get_xxx requests from the
    AccountStore
    """
    def generate_credentials_query
    def generate_privileges_query
    def generate_roles_query


class QueryExecutor:
    """
    Executes the queries created by the QueryGenerator
    """
    def execute
