class Account:
    pass


class AlchemyAccountStore:
    """
    AlchemyAccountStore provides the realm-facing API.  It parcels query
    results and returns them to its corresponding realm.
    """

    def __init__(self):
        self.handler = QueryHandler()

    def get_account(self, request):
        """
        :param request:  the request object defining the criteria by which
                         to query the account store
        :type request:  AuthenticationToken or Account

        :returns: Account
        """
        account_id = request.account_id
        credentials = self.handler.get_credentials(...)
        privileges = self.handler.get_privileges(...)
        roles = self.handler.get_roles(...)
        account = Account(account_id=account_id,
                          credentials=credentials,
                          permissions=privileges,
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
        privileges = self.handler.get_privileges(...)
        roles = self.handler.get_roles(...)
        account = Account(account_id=account_id,
                          permissions=privileges,
                          roles=roles)
        return account


class QueryHandler:
    """
    Facilitates requests from the AccountStore to the Database

    step 1:  generate an orm query
    step 2:  execute the query
    step 3:  return results
    """

    def get_account(self, request):
        pass

    def get_credentials(self, authc_token):
        pass

    def get_privileges(self, identifiers):
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
