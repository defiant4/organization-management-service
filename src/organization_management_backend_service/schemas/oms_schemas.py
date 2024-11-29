"""
Filename: oms_schemas.py
Project: Organization Management System (OMS)
Description: Defines data schemas used throughout the application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

from enum import Enum
from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel


class ErrorData(BaseModel):
    failure_code: str
    failure_message: str


class ErrorResponse(BaseModel):
    status: HTTPStatus
    data: Optional[ErrorData]


class OrganizationCreate(BaseModel):
    org_name: str
    admin_email: str
    admin_password: str


class UserLogin(BaseModel):
    user_email: str
    user_password: str


class UserType(Enum):
    ADMIN = "ADMIN"
    SUPER = "SUPERUSER"
    MANAGER = "MANAGER"
    OPERATORS = "OPERATORS"
    ORDINARY = "ORDINARY"
