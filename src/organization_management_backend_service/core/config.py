"""
Filename: config.py
Project: Organization Management System (OMS)
Description: Maintains all configurations for the application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import secrets
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional
from uuid import uuid4

from pydantic import Field
from pydantic import PostgresDsn
from pydantic import field_validator
from pydantic_settings import BaseSettings


class OmsSettings(BaseSettings):
    PROFILE: str
    SERVICE_NAME: str
    SERVICE_ACRONYM: str
    LOG_LEVEL: str = "INFO"
    LOG_OUTPUT_FORMAT: Literal["json", "console"] = "console"
    # Database Related Items
    DB_TYPE: str = "postgresql"
    DB_CREDS_SECRET_NAME: str = "dev/database/oms"
    RECREATE_DB_TABLES: bool = False
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None  # validator present
    SQLALCHEMY_DB_CONNECTION_POOL_SIZE: int = Field(default=5, ge=1, description="This value is the sqlalchemy db connection pool size.")

    @field_validator('SQLALCHEMY_DATABASE_URI', mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v or values.get("DB_CREDS_SECRET_NAME"):
            return v
        if not v and not values.get("DB_CREDS_SECRET_NAME"):
            raise ValueError("When DB_TYPE=postgresql then either DB_CREDS_SECRET_NAME or SQLALCHEMY_DATABASE_URI needs to be set.")

    # JWT Configuration (Fetch JWT details via SecretManager in dev/prod)
    JWT_SECRET: str = f"ORG_MGT_{uuid4().hex}_SECRET_{secrets.token_hex(8)}"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINS: int = Field(default=120, ge=1, description="This value is the maximum expiration for a JWT token in minutes.")
