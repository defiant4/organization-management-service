"""
Filename: dependencies.py
Project: Organization Management System (OMS)
Description: Definitions and management for the application's dependencies
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
import os

import sqlalchemy as sa
from fastapi import Depends
from pydantic import PostgresDsn
from sqlalchemy.engine import Engine

from organization_management_backend_service.core.config import OmsSettings
from organization_management_backend_service.dao.oms_dao import OrganizationsDAO
from organization_management_backend_service.dao.oms_dao import UsersDAO
from organization_management_backend_service.db.db_connector import DBConnector
from organization_management_backend_service.models.base_model import Base
from organization_management_backend_service.services.oms_service import OmsService

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    @staticmethod
    def create_db(engine: Engine, recreate_db: bool):
        if recreate_db:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


def get_settings() -> OmsSettings:
    settings = OmsSettings(_env_file=f"env/{os.getenv('PROFILE', 'local')}.env")
    return settings


settings = get_settings()


def get_db_connector() -> DBConnector:
    if settings.DB_TYPE == "postgresql":
        assert settings.DB_CREDS_SECRET_NAME is not None or settings.SQLALCHEMY_DATABASE_URI is not None
        if settings.SQLALCHEMY_DATABASE_URI or settings.PROFILE in ["local"]:
            dsn: PostgresDsn = settings.SQLALCHEMY_DATABASE_URI.hosts()[0]
            db_connector = DBConnector(
                db_type="postgresql",
                database=settings.SQLALCHEMY_DATABASE_URI.path[1:],
                user_name=dsn["username"],
                password=dsn["password"],
                host_name=dsn["host"],
                port=dsn["port"],
                poolclass_type=sa.pool.NullPool,  # disable pooling for local and tests
            )
        else:
            # Fetch DB details via DB Secret CREDs (via SecretManager in dev/prod)
            pass

        logger.info("Using Postgresql DB")
        return db_connector
    else:
        raise NotImplementedError(f"Unsupported database {settings.DB_TYPE}")


def get_db_engine(db_connector: DBConnector = get_db_connector()) -> Engine:
    return db_connector.engine


def get_organizations_dao(db_connector: DBConnector = Depends(get_db_connector)) -> OrganizationsDAO:
    return OrganizationsDAO(db=db_connector)


def get_users_dao(db_connector: DBConnector = Depends(get_db_connector)) -> UsersDAO:
    return UsersDAO(db=db_connector)


def get_oms_service(
    organizations_dao: OrganizationsDAO = Depends(get_organizations_dao),
    users_dao: UsersDAO = Depends(get_users_dao),
    settings: OmsSettings = Depends(get_settings),
) -> OmsService:
    return OmsService(organizations_dao=organizations_dao, users_dao=users_dao, settings=settings)
