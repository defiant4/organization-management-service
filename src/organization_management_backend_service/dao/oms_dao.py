"""
Filename: oms_dao.py
Project: Organization Management System (OMS)
Description: Defines the Data Access Object (DAO) layer for the application.
            It will contain classes and methods for performing CRUD (Create, Read, Update, Delete) operations on the MongoDB collections.
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

from organization_management_backend_service.dao.base_dao import BaseDao
from organization_management_backend_service.db.db_connector import DBConnector
from organization_management_backend_service.models.oms_models import Organizations
from organization_management_backend_service.models.oms_models import OrganizationsOrdering
from organization_management_backend_service.models.oms_models import Users
from organization_management_backend_service.models.oms_models import UsersOrdering


class OrganizationsDAO(BaseDao):
    def __init__(self, db: DBConnector) -> None:
        super().__init__(db=db, model_class=Organizations, model_ordering_class=OrganizationsOrdering)


class UsersDAO(BaseDao):
    def __init__(self, db: DBConnector) -> None:
        super().__init__(db=db, model_class=Users, model_ordering_class=UsersOrdering)
