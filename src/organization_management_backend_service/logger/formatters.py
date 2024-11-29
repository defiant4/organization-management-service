"""
Filename: formatters.py
Project: Organization Management System (OMS)
Description: Logger Formatters for JSON and Console
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import json
import logging
from contextvars import ContextVar
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from organization_management_backend_service.utils.fastapi_globals import get_contextvar_context_by_name
from organization_management_backend_service.utils.fastapi_globals import get_contextvar_context_by_names

from .filters import _sanitize_stacktrace_for_json_fields


def _expand_contextvar_names(default_namespace: str, contextvar_extras: Optional[List[Union[str, Tuple[str, str]]]]) -> List[str]:
    if contextvar_extras is None or not isinstance(contextvar_extras, list) or len(contextvar_extras) == 0:
        return None

    result: List[str] = []
    for item in contextvar_extras:
        if not isinstance(item, str) and not isinstance(item, tuple):
            raise NotImplementedError(f"contextvar_extra items need to be str or tuple got: {type(item)}")

        if isinstance(item, str):
            result.append(f"{default_namespace}:{item}")
        else:
            if len(item) != 2:
                raise ValueError(f"Expected each contextVar extra to be len 2 got: {len(item)}, {item}")

            result.append(f"{item[1]}:{item[0]}")

    return result


def set_available_context_vars(log_record: logging.LogRecord, context_var_name_list: List[str]):
    result: List[Union[ContextVar, RuntimeError]] = get_contextvar_context_by_names(contextvar_name_list=context_var_name_list, ignore_namespace=True)
    for index, var_name in enumerate(context_var_name_list):
        if isinstance(result[index], RuntimeError):
            continue  # skip variables not found

        if result[index].get() is None:
            continue  # Don't log empty fieldss

        # set it on the items __dict__ if non null
        setattr(log_record, var_name, result[index].get())


def set_request_id_if_available(log_record: logging.LogRecord, request_id_var_name: str):
    try:
        request_id: ContextVar = get_contextvar_context_by_name(contextvar_name=request_id_var_name, ignore_namespace=True)
        request_id_value = request_id.get()
        if request_id_value is None:
            return

        setattr(log_record, "request_id", request_id_value)
    except RuntimeError:
        # no request_id set or contextvar not founds
        return


def _update_info_for_decorated_methods(record: logging.LogRecord, extras: Dict[str, Any]) -> Tuple[str, str]:
    module_name: str = record.module
    fn_name: str = record.funcName

    if extras.get("wrapped_module_name"):
        module_name = extras["wrapped_module_name"]
    if extras.get("wrapped_fn_name"):
        fn_name = extras["wrapped_fn_name"]

    return module_name, fn_name


class ConsoleFormatter(logging.Formatter):
    def __init__(
        self,
        contextvar_extras: Optional[List[Union[str, Tuple[str, str]]]] = None,
        default_namespace: str = "globals",
        request_id_var_name: str = "x-request-id",
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style="%",
        validate: bool = True,
    ) -> None:
        """
        Optionally provide contextvars to log as extras to your logs if they are available in the current context
        and not None
        :param contextvar_extras: A list of either str contextvar names or a tuple of (var_name, namespace)
        If no namespace is provided the default namespace is searched
        :param default_namespace: The default namespace to lookup for context vars that don't have a namespace provided
        :param request_id_var_name: The contextvar that holds the request_id. A request_id field would be added as extra if a request
        id is set on the current context. If request trace middleware is used all logs part of same thread will automagically have the
        request_id for that request
        """
        super().__init__(fmt, datefmt, style, validate)
        self._request_id_var_name: str = request_id_var_name
        self._contextvar_name_list: Optional[List[str]] = _expand_contextvar_names(default_namespace=default_namespace, contextvar_extras=contextvar_extras)

    def format(self, record: logging.LogRecord) -> str:
        if self._contextvar_name_list is not None:
            set_available_context_vars(log_record=record, context_var_name_list=self._contextvar_name_list)

        level = record.levelname
        timestamp = self.formatTime(record, "%H:%M:%S")
        message = record.getMessage()
        if record.__dict__.get("application_name"):
            service_name = record.__dict__.get("application_name")
            del record.__dict__["application_name"]
        else:
            service_name = ""

        set_request_id_if_available(log_record=record, request_id_var_name=self._request_id_var_name)

        extra_fields = self._extract_extra_fields(record)

        module_name, fn_name = _update_info_for_decorated_methods(record=record, extras=extra_fields)

        # create string for extra objects
        extra_txt = " ".join([f"{k}={v}" for k, v in extra_fields.items()])
        funcname = f"[{service_name}] ({module_name}.{fn_name})" if service_name else f"({module_name}.{fn_name})"

        final_msg_without_exc_processing = (
            f"[{level}] -- {timestamp} :: {funcname} :: {message} [{extra_txt}]" if extra_fields else f"[{level}] -- {timestamp} :: {funcname} :: {message}"
        )

        # process exceptions and format them
        stack_trace = None
        if record.exc_info:
            stack_trace = _sanitize_stacktrace_for_json_fields(*record.exc_info)

        return final_msg_without_exc_processing if stack_trace is None else f"{final_msg_without_exc_processing}\n{stack_trace}"

    def _extract_extra_fields(self, record: logging.LogRecord) -> dict:
        dummy_record = logging.LogRecord(*["dummy"] * 7)
        default_fields = dummy_record.__dict__.keys()
        return {k: v for k, v in record.__dict__.items() if k not in default_fields and k != "message"}


class JSONFormatter(logging.Formatter):
    # When using this formatter make sure any Extra info logged is serialized
    # so that json.dumps doesn't raise any error

    def __init__(
        self,
        contextvar_extras: Optional[List[Union[str, Tuple[str, str]]]] = None,
        default_namespace: str = "globals",
        request_id_var_name: str = "x-request-id",
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style="%",
        validate: bool = True,
    ) -> None:
        """
        Optionally provide contextvars to log as extras to your logs if they are available in the current context
        and not None
        :param contextvar_extras: A list of either str contextvar names or a tuple of (var_name, namespace)
        If no namespace is provided the default namespace is searched
        :param default_namespace: The default namespace to lookup for context vars that don't have a namespace provided
        :param request_id_var_name: The contextvar that holds the request_id. A request_id field would be added as extra if a request
        id is set on the current context. If request trace middleware is used all logs part of same thread will automagically have the
        request_id for that request
        """
        super().__init__(fmt, datefmt, style, validate)
        self._request_id_var_name: str = request_id_var_name
        self._contextvar_name_list: Optional[List[str]] = _expand_contextvar_names(default_namespace=default_namespace, contextvar_extras=contextvar_extras)

    def format(self, record: logging.LogRecord) -> str:
        if self._contextvar_name_list is not None:
            set_available_context_vars(log_record=record, context_var_name_list=self._contextvar_name_list)

        set_request_id_if_available(log_record=record, request_id_var_name=self._request_id_var_name)

        json_dict = {}
        json_dict.update(record.__dict__)

        # update module and fn_name if its logged from a decorated method
        module_name, fn_name = _update_info_for_decorated_methods(record=record, extras=json_dict)
        json_dict["module"] = module_name
        json_dict["funcName"] = fn_name

        if record.exc_info:
            json_dict["stack_trace"] = _sanitize_stacktrace_for_json_fields(*record.exc_info)

            # mark exception info as none to consume the exception here and stop propogation
            # where it might get logged to sys.stderr.
            # If we need to reraise it we can log it as an exception on the root logger
            # record.exc_info = None  # we are not marking it as None
            # as we need the exception to propogate because we have more than 1 handler
            json_dict["exc_info"] = None

            # This field indicates if the current log message as a stacktrace
            # For easier filtering of stack traces raised
            json_dict["has_stacktrace"] = True
        else:
            json_dict["has_stacktrace"] = False

        # Already replaced this with 'stack_trace', no longer needed
        assert json_dict["exc_info"] is None
        del json_dict["exc_info"]

        # We don't need these 2 fields as message field has msg % args now
        json_dict["message"] = record.getMessage()
        del json_dict["msg"]
        del json_dict["args"]

        json_dict["level"] = json_dict["levelname"]
        # TODO: Decide whether to dump this or not?
        del json_dict["levelname"]

        try:
            if self.debug_out:
                return json.dumps(json_dict, indent=4)
            return json.dumps(json_dict)
            # Use below if you're debugging the logs locally
            # return json.dumps(json_dict, indent=4)
        except (TypeError, OverflowError) as e:
            stack_trace = _sanitize_stacktrace_for_json_fields(type(e), e, e.__traceback__)
            return json.dumps(
                {
                    "message": "An unrecoverable exception occured while logging",
                    "stack_trace": stack_trace,
                    "has_stacktrace": True,
                    "original_message": json_dict["message"],
                }
            )
