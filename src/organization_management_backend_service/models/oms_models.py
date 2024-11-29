"""
Filename: oms_models.py
Project: Organization Management System (OMS)
Description: Manage custom MongoDB collections
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""


from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from organization_management_backend_service.models.base_model import GenericBaseModel


class OmsModels:
    pass


# Organization Model
class Organizations(GenericBaseModel):
    __tablename__ = "organizations_data"
    __table_args__ = {"keep_existing": True}

    organizations_id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_name: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_by_password: Mapped[str] = mapped_column(String, unique=True)


class OrganizationsOrdering:
    CREATED_AT_ASC = Organizations.created_at.asc()
    CREATED_AT_DESC = Organizations.created_at.desc()


# User Model
class Users(GenericBaseModel):
    __tablename__ = "users_data"
    __table_args__ = {"keep_existing": True}

    users_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_email: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_password: Mapped[str] = mapped_column(String, nullable=False)
    user_type: Mapped[str] = mapped_column(String, nullable=False, index=True)


class UsersOrdering:
    CREATED_AT_ASC = Users.created_at.asc()
    CREATED_AT_DESC = Users.created_at.desc()
