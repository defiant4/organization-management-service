"""
Filename: oms_service.py
Project: Organization Management System (OMS)
Description: Service Layer (Business Logic) for the application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""


import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import uuid4

import bcrypt
import jwt
from sqlalchemy.exc import IntegrityError

from organization_management_backend_service.core.config import OmsSettings
from organization_management_backend_service.dao.oms_dao import OrganizationsDAO
from organization_management_backend_service.dao.oms_dao import UsersDAO
from organization_management_backend_service.schemas.oms_schemas import UserType
from organization_management_backend_service.utils.serialization import serialize
from organization_management_backend_service.utils.utils import fetch_row_based_on_column

logger = logging.getLogger(__name__)


class OmsService:
    def __init__(self, organizations_dao: OrganizationsDAO, users_dao: UsersDAO, settings: OmsSettings):
        """
        Initializes the OMS service.
        """
        self.organizations_dao = organizations_dao
        self.users_dao = users_dao
        self.jwt_secret = settings.JWT_SECRET
        self.jwt_algo = settings.JWT_ALGORITHM
        self.jwt_expiration_mins = settings.JWT_EXPIRATION_MINS
        self.settings = settings

    def _hash_password(self, password: str) -> str:
        """
        Hash the password using bcrypt.
        Args:
            password (str): Plain text password
        Returns:
            str: Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify the password against the hashed password.
        Args:
            plain_password (str): Plain text password
            hashed_password (str): Hashed password
        Returns:
            bool: Password verification result
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def _generate_jwt_token(self, email: str) -> str:
        """
        Generate a JWT token for the user.
        Args:
            email (str): User email
        Returns:
            str: JWT token
        """
        payload = {'email': email, 'exp': datetime.now(timezone.utc) + timedelta(minutes=self.jwt_expiration_mins)}
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algo)

    def create_organization(self, org_name: str, admin_email: str, admin_password: str) -> Dict[str, Any]:
        """
        Create a new organization with an admin user.
        Args:
            org_name (str): Name of the organization
            admin_email (str): Admin email
            admin_password (str): Admin password
        Returns:
            Dict[str, Any]: Created organization details
        Raises:
            ValueError: If organization already exists
        """
        try:
            # Hash the admin password
            hashed_password = self._hash_password(admin_password)
            # Generate unique IDs
            organization_id = serialize(uuid4())
            admin_id = serialize(uuid4())

            # Create organization in the master database
            org_data = {
                'created_at': datetime.now(timezone.utc),
                'created_by': admin_email,
                'created_by_password': hashed_password,
                'organizations_id': organization_id,
                'organization_name': org_name,
            }
            self.organizations_dao.create(**org_data)
            logger.info(f"Created organization with id: {organization_id}")
            # Create admin user in the organization's database
            user_data = {
                'created_at': datetime.now(timezone.utc),
                'created_by': admin_email,
                "users_id": admin_id,
                'user_email': admin_email,
                'user_password': hashed_password,
                'user_type': UserType.ADMIN.value,
            }
            self.users_dao.create(**user_data)
            logger.info(f"Created admin user with id: {admin_id}")

            return {"message": "Organization created successfully", "organization_id": organization_id}
        except IntegrityError as e:
            raise Exception("Organization or Admin with this email already exists") from e
        except Exception as e:
            raise Exception("Failed to create organization") from e

    def get_organization_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an organization by its name.
        Args:
            org_name (str): Name of the organization
        Returns:
            Optional[Dict[str, Any]]: Organization details or None
        """
        records_list: List = fetch_row_based_on_column(dao=self.organizations_dao, column_name='organization_name', column_type_filter_value=org_name)
        if not records_list:
            return None
        logger.info(f"Found organization {org_name} with id: {records_list[0].organizations_id}")
        return {'org_id': records_list[0].organizations_id, 'org_name': records_list[0].organization_name, 'created_by': records_list[0].created_by}

    def authenticate_admin(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate admin user and generate JWT token.
        Args:
            email (str): Admin email
            password (str): Admin password
            org_id (str): Organization ID
        Returns:
            Optional[str]: JWT token if authentication is successful, None otherwise
        """
        records_list: List = fetch_row_based_on_column(dao=self.users_dao, column_name='user_email', column_type_filter_value=email)
        if not records_list or not self._verify_password(password, records_list[0].user_password):
            return None
        logger.info(f"Successfully Logged in user {email}")

        return self._generate_jwt_token(email)
