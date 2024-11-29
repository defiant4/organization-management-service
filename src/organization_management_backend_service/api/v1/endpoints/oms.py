"""
Filename: oms.py
Project: Organization Management System (OMS)
Description: Contains all endpoints for the application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from organization_management_backend_service.schemas.oms_schemas import ErrorData
from organization_management_backend_service.schemas.oms_schemas import ErrorResponse
from organization_management_backend_service.schemas.oms_schemas import OrganizationCreate
from organization_management_backend_service.schemas.oms_schemas import UserLogin
from organization_management_backend_service.services.dependencies import get_oms_service
from organization_management_backend_service.services.oms_service import OmsService

logger = logging.getLogger(__name__)


router = APIRouter(
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.post(
    "/org/create/",
    status_code=HTTPStatus.OK,
    response_model=Any,
    responses={status.HTTP_200_OK: {"model": Any}},
    description="Call for creating organization.",
)
def create_org(org: OrganizationCreate, fast_api_response: Response, oms_service: OmsService = Depends(get_oms_service)):
    try:
        logger.info(f"Called create organization for org: {org.org_name}")
        return oms_service.create_organization(org.org_name, org.admin_email, org.admin_password)
    except Exception as e:
        fast_api_response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            status=HTTPStatus.NOT_FOUND,
            data=ErrorData(failure_code="Failed to create Organization", failure_message=str(e)),
        )


@router.get(
    "/org/get/",
    status_code=HTTPStatus.OK,
    response_model=Any,
    responses={status.HTTP_200_OK: {"model": Any}},
    description="Call for getting organization.",
)
def get_org(org_name: str, fast_api_response: Response, oms_service: OmsService = Depends(get_oms_service)):
    logger.info(f"Called get organization for org: {org_name}")
    org = oms_service.get_organization_by_name(org_name)
    if not org:
        fast_api_response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            status=HTTPStatus.NOT_FOUND,
            data=ErrorData(failure_code="Organization not found", failure_message="Organization not found"),
        )
    return org


@router.post(
    "/admin/login/",
    status_code=HTTPStatus.OK,
    response_model=Any,
    responses={status.HTTP_200_OK: {"model": Any}},
    description="Call for admin login.",
)
def admin_login(credentials: UserLogin, fast_api_response: Response, oms_service: OmsService = Depends(get_oms_service)):
    logger.info(f"Called admin login for user {credentials.user_email}")
    token = oms_service.authenticate_admin(credentials.user_email, credentials.user_password)
    if not token:
        fast_api_response.status_code = status.HTTP_401_UNAUTHORIZED
        return ErrorResponse(
            status=HTTPStatus.UNAUTHORIZED,
            data=ErrorData(failure_code="Invalid credentials", failure_message="Invalid credentials"),
        )

    return {"access_token": token}
