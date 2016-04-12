# Yosai AlchemyStore

This is an *extension* project for [Yosai](http://www.github.com/yosaiproject/yosai) that features a complete ``AccountStore`` data store solution intended for quick-start projects using Yosai.

An ``AccountStore`` is a data access object (DAO) that provides an interface to
a datastore, in this case a relational database.  YosaiAlchemyStore is named as such
to indicate its use of the [SQLAlchemy](http://www.sqlalchemy.org) library to enable all RDBMS connectivity.


# Installation

Install YosaiAlchemyStore from PyPI using pip:
    ``pip install yosai_alchemystore``


## Setup

An AlchemyAccountStore can be configured through one of two ways:

* Option 1: YAML Config File
    1. Define a system environment variable, YOSAI_ALCHEMYSTORE_SETTINGS, that points to 
       the location of alchemystore_settings.yaml file and ensure that the file
       permissions make it readable.
    
    2. Instantiate an AlchemyAccountStore without arguments.  

* Option 2: Passing a dburl argument
    - instantiate an AlchemyAccountStore, passing a "dburl" argument as
      defined by SQLAlchemy:  http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls


## API

The ``AccountStore`` API consists of two abstract base classes within the ``yosai.core.account.abcs`` module.
It's a simple API, consisting of a request method to obtain Account credentials (passwords)
and a request method to obtain Account authorization information (roles and permissions).


## Data Models

Following is the database schema used to facilitate a simple, "flat" Role Based Access Control (RBAC) authorization policy.  This data model enables the most basic form of RBAC.
![](/doc/db_schema.png)


## Dev Status:  as of v0.0.5

The project has been released after being tested as part of yosai integrated testing.
Unit tests are pending development.
