"""
Filename: method_logger.py
Project: Organization Management System (OMS)
Description: Custom Decorator to log class methods and inputs
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import inspect
import logging
from functools import wraps

from .serialization import serialize

log = logging.getLogger(__name__)


def method_logger(level):
    """simple decorator to log class methods and inputs"""

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            # This in case the decorated method is a coroutine. Then use async/await
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                parent = type(args[0]).__name__
                getattr(log, level)(
                    f'{func.__name__} called by {parent} with args {args[1:]} and kwargs {kwargs}',
                    extra={
                        "passed_args": serialize(args[1:]),
                        "passed_kwargs": serialize(kwargs),
                        # add these extras to signify decorated methods and correct logging
                        "wrapped_module_name": func.__module__.split(".")[-1],
                        "wrapped_fn_name": func.__name__,
                        "decorating_async_method": True,
                    },
                )
                result = await func(*args, **kwargs)
                return result

            return async_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            parent = type(args[0]).__name__
            getattr(log, level)(
                f'{func.__name__} called by {parent} with args {args[1:]} and kwargs {kwargs}',
                extra={
                    "passed_args": serialize(args[1:]),
                    "passed_kwargs": serialize(kwargs),
                    # add these extras to signify decorated methods and correct logging
                    "wrapped_module_name": func.__module__.split(".")[-1],
                    "wrapped_fn_name": func.__name__,
                    "decorating_async_method": False,
                },
            )
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
