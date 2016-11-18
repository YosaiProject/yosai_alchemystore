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
import functools
from sqlalchemy import case, cast, func, Text
from sqlalchemy.sql import Alias, ColumnElement
from sqlalchemy.ext.compiler import compiles

from yosai_alchemystore import (
    init_session
)

from yosai_alchemystore.models.models import (
    Credential,
    CredentialType,
    User,
    Domain,
    Action,
    Resource,
    Permission,
    Role,
    role_membership as role_membership_table,
    role_permission as role_permission_table,
)

from yosai.core import (
    account_abcs,
)

# -------------------------------------------------------
# Following is a recipe used to address postgres-json related shortcomings
# in sqlalchemy v1.1.4.  This recipe will eventually be deprecated
# ----------------------------------------------------------


class as_row(ColumnElement):
    def __init__(self, expr):
        assert isinstance(expr, Alias)
        self.expr = expr


@compiles(as_row)
def _gen_as_row(element, compiler, **kw):
    return compiler.visit_alias(element.expr, ashint=True, **kw)


# -------------------------------------------------------
# -------------------------------------------------------


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


class AlchemyAccountStore(account_abcs.CredentialsAccountStore,
                          account_abcs.AuthorizationAccountStore,
                          account_abcs.LockingAccountStore):
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
        if session is None:
            self.Session = init_session(db_url=db_url, settings=settings)
        else:
            self.Session = session

    def _get_user_query(self, session, identifier):
        return session.query(User).filter(User.identifier == identifier)

    def _get_permissions_query(self, session, identifier):
        """
        select domain, json_agg(parts) as permissions from
            (select domain, row_to_json(r) as parts from
                    (select domain, action, array_agg(distinct target) as target from
                        (select (case when domain is null then '*' else domain end) as domain,
                                (case when target is null then '*' else target end) as target,
                                array_agg(distinct (case when action is null then '*' else action end)) as action
                           from permission
                          group by domain, target
                         ) x
                      group by domain, action)
              r) parts
        group by domain;
        """
        thedomain = case([(Domain.name == None, '*')], else_=Domain.name)
        theaction = case([(Action.name == None, '*')], else_=Action.name)
        theresource = case([(Resource.name == None, '*')], else_=Resource.name)

        action_agg = func.array_agg(theaction.distinct())

        stmt1 = (
            session.query(Permission.domain_id,
                          thedomain.label('domain'),
                          Permission.resource_id,
                          theresource.label('resource'),
                          action_agg.label('action')).
            select_from(User).
            join(role_membership_table, User.pk_id == role_membership_table.c.user_id).
            join(role_permission_table, role_membership_table.c.role_id == role_permission_table.c.role_id).
            join(Permission, role_permission_table.c.permission_id == Permission.pk_id).
            outerjoin(Domain, Permission.domain_id == Domain.pk_id).
            outerjoin(Action, Permission.action_id == Action.pk_id).
            outerjoin(Resource, Permission.resource_id == Resource.pk_id).
            filter(User.identifier == identifier).
            group_by(Permission.domain_id, Domain.name, Permission.resource_id, Resource.name)).subquery()

        stmt2 = (session.query(stmt1.c.domain,
                               stmt1.c.action,
                               func.array_agg(stmt1.c.resource.distinct()).label('resource')).
                 select_from(stmt1).
                 group_by(stmt1.c.domain, stmt1.c.action)).subquery()

        stmt3 = (session.query(stmt2.c.domain,
                               func.row_to_json(as_row(stmt2)).label('parts')).
                 select_from(stmt2)).subquery()

        final = (session.query(stmt3.c.domain, cast(func.json_agg(stmt3.c.parts), Text)).
                 select_from(stmt3).
                 group_by(stmt3.c.domain))

        return final

    def _get_roles_query(self, session, identifier):
        """
        :type identifier: string
        """
        return (session.query(Role).
                join(role_membership_table, Role.pk_id == role_membership_table.c.role_id).
                join(User, role_membership_table.c.user_id == User.pk_id).
                filter(User.identifier == identifier))

    def _get_credential_query(self, session, identifier):
        return (session.query(CredentialType.title, Credential.credential).
                join(Credential, CredentialType.pk_id == Credential.credential_type_id).
                join(User, Credential.user_id == User.pk_id).
                filter(User.identifier == identifier))

    @session_context
    def get_authc_info(self, identifier, session=None):
        """
        If an Account requires credentials from multiple data stores, this
        AccountStore is responsible for aggregating them (composite) and returning
        the results in a single account object.

        :returns: a dict of account attributes
        """
        user = self._get_user_query(session, identifier).first()

        creds = self._get_credential_query(session, identifier).all()
        if not creds:
            return None
        authc_info = {cred_type: {'credential': cred_value, 'failed_attempts': []}
                      for cred_type, cred_value in creds}

        if 'totp_key' in authc_info:
            authc_info['totp_key']['2fa_info'] = {'phone_number': user.phone_number}

        return dict(account_locked=user.account_lock_millis, authc_info=authc_info)

    @session_context
    def get_authz_permissions(self, identifier, session=None):
        try:
            return dict(self._get_permissions_query(session, identifier).all())
        except (AttributeError, TypeError):
            return None

    @session_context
    def get_authz_roles(self, identifier, session=None):
        try:
            return [r.title for r in self._get_roles_query(session, identifier).all()]
        except (AttributeError, TypeError):
            return None

    @session_context
    def lock_account(self, identifier, locked_time, session=None):
        session.query(User).\
            filter(User.identifier == identifier).\
            update({User.account_lock_millis: locked_time})

        session.commit()

    @session_context
    def unlock_account(self, identifier, session=None):
        session.query(User).\
            filter(User.identifier == identifier).\
            update({User.account_lock_millis: None})

        session.commit()

#    @session_context
#    def get_account(self, identifier, session=None):
#        """
#        get_account performs the most comprehensive collection of information
#        from the database, including credentials AND authorization information
#
#        :param identifier:  the request object's identifier
#        :returns: dict
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
#        credential = self.credential(cred)
#
#        roles = {self.role(r.title)
#                 for r in self.get_roles_query(session, identifier).all()}
#
#        perms = self.get_permissions_query(session, identifier).all()
#        permissions = {self.permission(permission=p.perm)
#                       for p in perms}
#
#        authz_info = self.authz_info(roles=roles,
#                                              permissions=permissions)
#
#        account = dict(account_id=identifier,
#                          credentials=credential,
#                          authz_info=authz_info)
#
#        return account
