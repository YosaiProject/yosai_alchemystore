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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from yosai_alchemystore import AccountStoreSettings

Base = declarative_base()


def init_engine(db_url=None, echo=False, settings=None):
    """

    You can configure the engine in two ways:
        1) YAML config:
            I) create a yaml config file whose contents is used to construct a
            'Database URL' connection string as supported by SQLAlchemy
            II) define an environment variable, "YOSAI_ALCHEMYSTORE_SETTINGS",
                that points to the location of the config file

        2) pass the engine configuration as a string that is in the
           'Database URL' format as supported by SQLAlchemy:
            http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls

    When a 'Database URL' string isn't passed, the YAML configuration approach
    is attempted by default.

    :type db_url: string
    :type echo: bool
    """
    if db_url is None:
        acct_settings = AccountStoreSettings(settings)
        url = acct_settings.url
    else:
        url = db_url

    engine = create_engine(url, echo=echo)
    return engine


def init_session(db_url=None, echo=False, engine=None, settings=None):
    """
    A SQLAlchemy Session requires that an engine be initialized if one isn't
    provided.
    """
    if engine is None:
        engine = init_engine(db_url=db_url, echo=echo, settings=settings)
    return sessionmaker(bind=engine)
