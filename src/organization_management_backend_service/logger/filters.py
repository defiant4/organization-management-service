"""
Filename: filters.py
Project: Organization Management System (OMS)
Description: Logger Filters
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

import logging
import traceback


class AddContextualFieldFilter(logging.Filter):
    def __init__(self, field_name: str, field_value: str) -> None:
        self._field_name = field_name
        self._field_value = field_value

    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__[self._field_name] = self._field_value
        return True


def _sanitize_stacktrace_for_json_fields(type, value, tb) -> str:
    # Sanitize it for our json formatting
    return "".join(traceback.format_exception(type, value, tb))
