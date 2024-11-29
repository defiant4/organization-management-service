"""
Filename: serialization.py
Project: Organization Management System (OMS)
Description: Serialize various types of objects to a format suitable for JSON serialization
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

from collections.abc import Iterable
from collections.abc import Mapping
from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

primitive = (int, float, str, bool)


def is_primitive(thing):
    return isinstance(thing, primitive)


def serialize(obj, decoder="utf8"):
    if obj is None:
        return None
    if isinstance(obj, BaseModel):
        return serialize(obj.dict())
    if callable(obj):
        return repr(obj)
    if isinstance(obj, Enum):
        return obj.value
    if is_primitive(obj):
        return obj
    if isinstance(obj, datetime) or isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, bytes):
        return str(obj.decode(decoder))
    if isinstance(obj, Mapping):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, Iterable):
        return [serialize(v) for v in obj]

    return repr(obj)  # wildacrd if its not a known type
