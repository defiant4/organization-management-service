"""
Filename: logger.py
Project: Organization Management System (OMS)
Description: Custom Logger Implementation to handle all scenarios for the application
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
import os
import sys
from traceback import TracebackException
from typing import Tuple

from .filters import AddContextualFieldFilter
from .filters import _sanitize_stacktrace_for_json_fields
from .formatters import ConsoleFormatter
from .formatters import JSONFormatter


def _uncaught_exception_logger(type: BaseException, exc: Exception, traceback: TracebackException):
    exception_string = _sanitize_stacktrace_for_json_fields(type, exc, traceback)
    # raise to root logger where it will be consumed by the formatter attached to our handler
    logging.getLogger().error(exception_string)


def enable_file_logging(log_dir_path: str) -> Tuple[logging.FileHandler, logging.FileHandler]:
    """
    Enable file logging to the dir specified by log_dir_path. If the log_dir doesn't exits
    the process will create it

    :params log_dir_path: The absolute path of the log dir
    """
    log_folder = log_dir_path

    if not os.path.exists(log_folder):  # Make the log_dir if it doesn't exist
        os.makedirs(log_folder)  # Make all dir in the path that don't exist

    info_handler = logging.FileHandler(os.path.join(log_folder, "info.log"), mode="a")
    info_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler(os.path.join(log_folder, "error.log"), mode="a")
    error_handler.setLevel(logging.ERROR)

    return info_handler, error_handler


def configure_logging(
    logger_name: str,
    application_name: str,
    level: str = "INFO",
    log_format: str = "console",
    log_dir: str = None,
    debug_out: bool = False,
) -> logging.Logger:
    """
    A function to setup logging

    :param logger_name: str, The name of the logger
    :param application_name: str, The name of the application. All logs will be tagged by this
    name for easier filtering
    :param level: str, default=INFO. The log level for the logger
    :param log_format: str, A possible value of "console" or "json". Default is console
    :param log_dir: str = None, The path of the log dir in case you want to enable file logging
    debug_out: bool = False, The logs are pretty printed in case of json logging
    """
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        # this is a subsequent call
        return logging.getLogger(logger_name)

    # If its the first call
    root_logger.addHandler(logging.StreamHandler())
    root_logger.setLevel(level)

    # If file logging required
    if log_dir:
        info_handler, error_handler = enable_file_logging(log_dir)
        root_logger.addHandler(info_handler)
        root_logger.addHandler(error_handler)

    assert root_logger.hasHandlers()
    for handler in root_logger.handlers:
        if log_format != "console":
            json_formatter_obj = JSONFormatter()
            json_formatter_obj.debug_out = debug_out
            handler.setFormatter(json_formatter_obj)
        else:
            handler.setFormatter(ConsoleFormatter())

        # Adds a marker for all log lines so its easier to filter in combined logs
        handler.addFilter(AddContextualFieldFilter("application_name", application_name))

    # For exceptions that were edge cases and not caught
    sys.excepthook = _uncaught_exception_logger

    return logging.getLogger(logger_name)
