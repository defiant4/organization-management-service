"""
Filename: middlewares.py
Project: Organization Management System (OMS)
Description: Middleware components for the FastAPI application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

from contextvars import ContextVar
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from .fastapi_globals import ContextVarManager
from .serialization import serialize


# If we want to have the context reset every time a new request is started
class GlobalsMiddleware:
    def __init__(self, app: ASGIApp, *, contextvar_manager: ContextVarManager = None) -> None:
        self.app = app
        if contextvar_manager is None:
            raise RuntimeError("Middleware: GlobalsMiddleware requires a contextvar_manager")
        self._contextvar_manager = contextvar_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # reset the exising context for a new request
        self._contextvar_manager.reset()
        await self.app(scope, receive, send)


# If we want to have the context reset every time a new request is started
class RequestIDTraceMiddleware:
    """
    Adds a request ID to each request available under request.scope["internal_request_id"]
    and scope["internal_request_id_header_name"] has the name of the response header that will be
    sent along with the response if the send_in_response property is set to True
    """

    def __init__(self, app: ASGIApp, *, send_in_response: bool = False, response_header_name: str = "x-request-id") -> None:
        self.app = app
        self._request_id_ctx_var: ContextVar[str] = ContextVar(response_header_name, default=None)
        self._response_header_name: str = response_header_name
        self._send_in_response: bool = send_in_response

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Adds a request ID to each request available under request.scope["internal_request_id"]
        and scope["internal_request_id_header_name"] has the name of the response header that will be
        sent along with the response if the send_in_response property is set to True
        """

        self._request_id_ctx_var.set(serialize(uuid4()))
        scope["internal_request_id"] = self._request_id_ctx_var.get()
        scope["internal_request_id_header_name"] = self._response_header_name
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_extra_headers(message):
            if message["type"] == "http.response.start":
                if self._request_id_ctx_var.get() is not None:
                    # only add the response header if any request_id present
                    headers = MutableHeaders(scope=message)
                    headers.append(self._response_header_name, self._request_id_ctx_var.get())

            await send(message)

        await self.app(scope, receive, send_with_extra_headers if self._send_in_response else send)
