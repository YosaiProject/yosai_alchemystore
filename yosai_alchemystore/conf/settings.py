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

from yosai.core import MisconfiguredException


class AccountStoreSettings:

    def __init__(self, settings):
        try:
            account_store_config = settings.ALCHEMY_STORE

            engine_config = account_store_config['engine_config']
            dialect = engine_config['dialect']
            path = engine_config['path']
            userid = engine_config.get('userid')
            password = engine_config.get('password')
            hostname = engine_config.get('hostname')
            port = engine_config.get('port')
            db = engine_config.get('db')

            self.echo = engine_config.get('echo', False)

            self.url = "{dialect}:{path}{userid}{idpasspath}{password}{hostnamepath}{hostname}{portpath}{port}{dbpath}{db}".\
                format(dialect=dialect,
                       path=path,
                       userid=userid if userid is not None else '',
                       idpasspath=':' if userid and password else '',
                       password=password if password is not None else '',
                       hostnamepath='@' if hostname is not None else '',
                       hostname=hostname if hostname is not None else '',
                       portpath=':' if port is not None else '',
                       port=port if port is not None else '',
                       dbpath='/' if db else '',
                       db=db if db is not None else '')

        except (AttributeError, TypeError):
            msg = ('yosai_alchemystore AlchemyStoreSettings requires a LazySettings instance '
                   'with complete ALCHEMY_STORE settings')
            raise MisconfiguredException(msg)
