"""
Filename: _exceptions.py
Project: Organization Management System (OMS)
Description: Maintain Custom Exceptions
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""


class BaseDaoException(Exception):
    def __str__(self):
        return self.message


class InvalidFilterField(BaseDaoException):
    """exception when trying to filter using an invalid field"""

    def __init__(self, model_class, field):
        self.message = f"{field} is not a valid field of {model_class.__name__}, check the model definition for valid field names"


class InvalidFilterMethod(BaseDaoException):
    """exception when trying to filter using an invalid method"""

    def __init__(self, model_class, field, method):
        self.message = f"{method} is not a valid lookup method of {model_class.__name__}.{field}, perhaps you need to add it to the QueryParser class?"


class DataError(BaseDaoException):
    """exception when bad data is passed in to a field"""

    def __init__(self, dao_class, field, exception):
        self.message = f"data error on model {dao_class._model_class.__name__} and field/method {field}"


class NotFound(BaseDaoException):
    """exception when an object is not found"""

    def __init__(self, dao_class, id):
        self.message = f"{dao_class._model_class.__name__} with id {id} not found"


class NotNullable(BaseDaoException):
    """exception when a non-nullable field is set to null"""

    def __init__(self, dao_class, field):
        self.message = f"field {field} on {dao_class._model_class.__name__} cannot be null"
