"""
Filename: db_connector.py
Project: Organization Management System (OMS)
Description: Database connector for the application.
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
from typing import Dict
from typing import Optional
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import Pool


class DBConnector:
    """
    Object-relational mapper (ORM), using which classes can be mapped to the database.
    Allowing the object model and database schema to develop in a cleanly decoupled manner.
    """

    def __init__(
        self,
        db_type: str,
        database: str,
        host_name: str = None,
        user_name: str = None,
        password: str = None,
        port: int = 5432,
        path: str = None,
        autocommit: bool = False,
        autoflush: bool = False,
        expire_on_commit: bool = True,
        is_async: bool = False,
        base=declarative_base(),
        pool_size=5,
        max_overflow=10,
        poolclass_type: Pool = None,
    ) -> None:
        """
        :param db_type: str, Type of database. For Postgres database, its postgresql
        :param hostname: str, Host detail of database instance
        :param username: str, User name of database instance
        :param password: str, password of database instance
        :param port=5432: int, port of database instance
        :param database: str, database name of the instance
        :param path: str, path for sqlite db
        :param autocommit: bool, enable/disable auto commit
        :param autoflush: bool, enable/disable auto flush
        :param expire_on_commit: bool, enable/disable when commit expire
        :param is_async: bool, enable/disable when async functionality is required. By default, it is false. Ex: "sqlite+aiosqlite" is db_type for sqlite DB
        :param pool_size: engine DB connection pool size (default 5); same as SqlAlchemy default
        :param max_overflow: max overflow DB connection size (default 10); same as SqlAlchemy default
        :param poolclass_type: Default None. We can provide any acceptable poolclass here from sqlachemy's supported pools. ex: set to NullPool to allow for
        async pytest to work correctly with postgres+asyncpg and fastapi. When None is provided the create_engine auto picks the best pool for dialect.
        Most cases a QueuePool. docs: https://docs.sqlalchemy.org/en/20/core/pooling.html
        """

        self._db_type = db_type
        self._username = user_name
        self._password = password
        self._hostname = host_name
        self._port = port
        self._database = database
        self._path = path
        self._autocommit = autocommit
        self._autoflush = autoflush
        self._expire_on_commit = expire_on_commit
        self._logger = logging.getLogger(__name__)
        self._engine: Optional[Union[AsyncEngine, Engine]] = None
        # Declarative_base() that returns a class.
        # We will inherit returned class to create each of the database models or classes (the ORM models).
        self.base = base
        self._session_factory = None
        self._is_async = is_async
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        if poolclass_type is not None and not issubclass(poolclass_type, Pool):
            raise ValueError(f"Invalid poolclass_type provided. Expected a subclass of Pool got: {type(poolclass_type)}")
        self._poolclass_type = poolclass_type

    @property
    def engine(self) -> Optional[Union[Engine, AsyncEngine]]:
        """
        Engine references both a Dialect and a Pool,
        which together interpret the DBAPI's module functions as well as the behavior of the database.
        """
        try:
            # Checking for engine instance avialability based on engine type
            if self._engine is None:
                if self._hostname and self._username and self._password and self._hostname:
                    if self._is_async:
                        if self._poolclass_type:
                            self._engine = create_async_engine(
                                url=f"{self._db_type}://{self._username}:{self._password}@{self._hostname}:{self._port}/{self._database}",
                                poolclass=self._poolclass_type,
                            )
                        else:
                            self._engine = create_async_engine(
                                url=f"{self._db_type}://{self._username}:{self._password}@{self._hostname}:{self._port}/{self._database}",
                                pool_size=self._pool_size,
                                max_overflow=self._max_overflow,
                            )
                    else:
                        if self._poolclass_type:
                            self._engine = create_engine(
                                url=f"{self._db_type}://{self._username}:{self._password}@{self._hostname}:{self._port}/{self._database}",
                                poolclass=self._poolclass_type,
                            )
                        else:
                            self._engine = create_engine(
                                url=f"{self._db_type}://{self._username}:{self._password}@{self._hostname}:{self._port}/{self._database}",
                                pool_size=self._pool_size,
                                max_overflow=self._max_overflow,
                            )
                else:
                    self._logger.error(f"Required parameters are missing for creation of {self._db_type} engine")
                    raise ValueError(f"Required parameters are missing for creation of {self._db_type} engine")
            return self._engine
        except Exception as e:
            self._logger.error(
                f"Error while creating database engine for {self._database}",
                extra={"failure_reason": "DB_ENGINE_CREATION_ERROR"},
                exc_info=e,
            )
            raise e

    def get_db_connection_params(self) -> Dict:
        """
        Get the db's connection params passed as part of init
        This method is to be used only when you want to clone the instance anew
        """
        return {
            "db_type": self._db_type,
            "database": self._database,
            "host_name": self._hostname,
            "user_name": self._username,
            "password": self._password,
            "port": self._port,
            "path": self._path,
            "autocommit": self._autocommit,
            "autoflush": self._autoflush,
            "expire_on_commit": self._expire_on_commit,
        }

    def _mk_session_factory(self) -> Optional[sessionmaker]:
        """
        This method is used to create a top level Session configuration
        which can then be used throughout the application without
        the need to repeat the configurational arguments.
        """
        try:
            session_factory = sessionmaker(
                autocommit=self._autocommit,
                autoflush=self._autoflush,
                expire_on_commit=self._expire_on_commit,
                bind=self.engine,
                class_=AsyncSession if self._is_async else Session,
            )
            return session_factory
        except Exception as e:
            self._logger.error(
                "Error while creating database session",
                extra={"failure_reason": "DB_SESSION_FACTORY_CREATION_ERROR"},
                exc_info=e,
            )

    @property
    def session_factory(self):
        """
        This method will create new session generator function/method.
        If it doesn't exist a new session factory/generator will be instantiated
        """
        if self._session_factory is None:
            self._session_factory = self._mk_session_factory()
        return self._session_factory

    def mk_db_session(self):
        """
        This method creates independent database session(Session_factory) per request,
        use same session through all the request and then close it after the request is finished.
        And then a new session will be created for the next request.
        """
        try:
            db = self.session_factory()
            yield db
        except Exception as e:
            self._logger.error(
                "Error while creating database session",
                extra={"failure_reason": "DB_SESSION_CREATION_FAILED"},
                exc_info=e,
            )
        finally:
            db.close()
