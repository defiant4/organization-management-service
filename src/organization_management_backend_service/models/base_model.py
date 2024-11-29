"""
Filename: base_model.py
Project: Organization Management System (OMS)
Description: Manage MongoDB database and collections
Author: arnabadhikari93@gmail.com
Date Created: 2024-11-29
Last Modified: 2024-11-29
Version: 1.0.0

Copyright (c) 2024-2025 Arnab Adhikari. All rights reserved.
"""

from __future__ import annotations

import logging
import re
from typing import Any
from typing import Dict

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

logger = logging.getLogger(__name__)


class GenericBaseModel(Base):
    __abstract__ = True
    __table_args__ = {"keep_existing": True}

    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_by = Column(String, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    updated_by = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    @classmethod
    def get_id_field(cls):
        """generic class method that acts as an alias for each <model-name>_id field"""

        return getattr(cls, re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "_id")

    @classmethod
    def model_to_dict(cls, model: GenericBaseModel) -> Dict[str, Any]:
        if model is None:
            logger.error("Model cannot be None")
            raise ValueError("Model cannot be None")

        if not isinstance(model, GenericBaseModel):
            logger.error(f"Model needs to be subclass of GenericBaseModel but got: {type(model)}")
            raise ValueError(f"Model needs to be subclass of GenericBaseModel but got: {type(model)}")

        return {field.name: getattr(model, field.name) for field in model.__table__.c}

    def to_dict(self) -> Dict[str, Any]:
        if self is None:
            logger.error("Model cannot be None")
            raise ValueError("Model cannot be None")

        if not isinstance(self, GenericBaseModel):
            logger.error(f"Model needs to be subclass of GenericBaseModel but got: {type(self)}")
            raise ValueError(f"Model needs to be subclass of GenericBaseModel but got: {type(self)}")

        return {field.name: getattr(self, field.name) for field in self.__table__.c}
