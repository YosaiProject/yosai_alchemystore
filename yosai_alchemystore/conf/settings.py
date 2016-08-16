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
            self.account_store_config = settings.ALCHEMY_STORE
            self.engine_config = self.account_store_config['engine_config']
            self.dialect = self.engine_config['dialect']
            self.path = self.engine_config['path']
            self.userid = self.engine_config.get('userid')
            self.password = self.engine_config.get('password')
            self.hostname = self.engine_config.get('hostname')
            self.port = self.engine_config.get('port')
            self.db = self.engine_config.get('db')
            self.echo = self.engine_config.get('echo', False)

        except (AttributeError, TypeError):
            msg = ('yosai_alchemystore AlchemyStoreSettings requires a LazySettings instance '
                   'with complete ALCHEMY_STORE settings')
            raise MisconfiguredException(msg)

    @property
    def url(self):
        return ("{dialect}:{path}{userid}{idpasspath}{password}{hostnamepath}"
                "{hostname}{portpath}{port}{dbpath}{db}".
                format(dialect=self.dialect,
                       path=self.path,
                       userid=self.userid if self.userid is not None else '',
                       idpasspath=':' if self.userid and self.password else '',
                       password=self.password if self.password is not None else '',
                       hostnamepath='@' if self.hostname is not None else '',
                       hostname=self.hostname if self.hostname is not None else '',
                       portpath=':' if self.port is not None else '',
                       port=self.port if self.port is not None else '',
                       dbpath='/' if self.db else '',
                       db=self.db if self.db is not None else ''))
