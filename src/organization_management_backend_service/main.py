"""
Filename: main.py
Project: Organization Management System (OMS)
Description: Main entry point for the FastAPI application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from organization_management_backend_service.api.v1.endpoints.oms import router as oms_router
from organization_management_backend_service.logger.logger import configure_logging
from organization_management_backend_service.services.dependencies import DatabaseInitializer
from organization_management_backend_service.services.dependencies import get_db_engine
from organization_management_backend_service.services.dependencies import settings
from organization_management_backend_service.utils.middlewares import RequestIDTraceMiddleware


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and "api" in str(record.args[2])


configure_logging(
    logger_name=__name__,
    application_name=settings.SERVICE_ACRONYM.upper(),
    level=settings.LOG_LEVEL,
    log_format=settings.LOG_OUTPUT_FORMAT,
)
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# to reduce logging noise set Log level to CRITICAL

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        DatabaseInitializer.create_db(get_db_engine(), settings.RECREATE_DB_TABLES)
        yield
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise


app = FastAPI(lifespan=lifespan, title=settings.SERVICE_NAME.lower())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specifies the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# add a request_id to each request and all of its logs
app.add_middleware(RequestIDTraceMiddleware, send_in_response=True)

app.include_router(oms_router, tags=["organization_management_backend_service"])
