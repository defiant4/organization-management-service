import inspect
import logging
from datetime import datetime
from datetime import timezone
from typing import List

from sqlalchemy import exc

from organization_management_backend_service._exceptions import DataError
from organization_management_backend_service._exceptions import NotFound
from organization_management_backend_service._exceptions import NotNullable
from organization_management_backend_service.db.db_connector import DBConnector
from organization_management_backend_service.db.query_parser import QueryParser
from organization_management_backend_service.models.base_model import GenericBaseModel
from organization_management_backend_service.utils.method_logger import method_logger

log = logging.getLogger(__name__)


class BaseDaoListResponse:
    def __init__(self, items: List, count: int):
        self.items = items
        self.count = count


class BaseDao:
    """Base DAO class that can be customized"""

    def __init__(self, db: DBConnector, model_class: GenericBaseModel, model_ordering_class):
        # validate DBConnector parameter
        if db is None:
            raise Exception("db must be defined")
        if not isinstance(db, DBConnector):
            raise Exception(f"Wrong type for db={type(db)}")
        self._db: DBConnector = db

        # validate model class
        if not model_class:
            raise Exception("model_class must be defined")
        if not inspect.isclass(model_class):
            raise Exception("model_class must be a class")
        if not issubclass(model_class, GenericBaseModel):
            raise Exception(f"Wrong type for model_class={type(model_class)}")
        self._model_class = model_class

        # validate model order by class
        if not model_ordering_class:
            raise Exception("model_ordering_class must be defined")
        if not inspect.isclass(model_ordering_class):
            raise Exception("model_ordering_class must be a class")
        self._model_ordering_class = model_ordering_class

        # extract all non-nullable fields
        self._non_nullable_columns = {column.name for column in self._model_class.__table__.columns if not column.nullable and not column.default}

    def _verify_null_kwargs(self, kwargs):
        for field in kwargs:
            if field in self._non_nullable_columns and kwargs[field] is None:
                exception = NotNullable(self, field)
                log.error(exception.message, exc_info=exception.message)
                raise exception

    def _verify_all_non_nullable_fields_defined(self, kwargs):
        for field in self._non_nullable_columns:
            if field not in kwargs:
                exception = NotNullable(self, field)
                log.error(exception.message, exc_info=exception.message)
                raise exception

    def _get(self, session, id):
        return session.query(self._model_class).filter(self._model_class.get_id_field() == id).one_or_none()

    @method_logger('info')
    def get(self, id):
        """get method for instance"""
        with self._db.session_factory() as session:
            instance = self._get(session, id)

        return instance

    @method_logger('info')
    def create(self, **kwargs):
        """create method for instances"""
        with self._db.session_factory() as session:
            # update kwargs:
            kwargs["updated_by"] = kwargs.get("created_by", None)
            kwargs["updated_at"] = kwargs.get("created_at", None)

            # raise error if a non-nullable field was set to null:
            self._verify_null_kwargs(kwargs)

            # raise error if a non-nullable field was not passed in:
            self._verify_all_non_nullable_fields_defined(kwargs)

            # otherwise create instance:
            instance = self._model_class(**kwargs)
            session.add(instance)
            session.commit()

    @method_logger('info')
    def update(self, id, **kwargs):
        """update method for instances"""

        if not kwargs:
            log.warning("kwargs is empty - possible bug?")
            return

        with self._db.session_factory() as session:
            instance = self._get(session, id)

            # return exception if not found:
            if not instance:
                exception = NotFound(self, id)
                log.error(exception)
                raise exception

            # update record
            # raise error if a non-nullable field was set to null:
            self._verify_null_kwargs(kwargs)

            for field in kwargs:
                setattr(instance, field, kwargs[field])

            # update timestamp
            instance.updated_at = datetime.now(timezone.utc)

            # save changes:
            session.commit()

    @method_logger('info')
    def soft_delete(self, id, updated_by: str, updated_at: datetime):
        """delete method for instance"""

        if not id:
            raise ValueError("id is undefined")

        if not updated_by:
            raise ValueError("updated_by is undefined")

        if not updated_at:
            raise ValueError("updated_at is undefined")

        with self._db.session_factory() as session:
            # try to delete instance:
            instance = self._get(session, id)

            # return error if not found:
            if not instance:
                exception = NotFound(self, id)
                log.error(exception.message, exc_info=exception.message)
                raise exception

            # soft delete instance:
            instance.updated_by = updated_by
            instance.updated_at = updated_at
            instance.is_deleted = True
            session.add(instance)
            session.commit()

    @method_logger('debug')
    def list(
        self, page: int = 0, size: int = 100, order_by: str = "CREATED_AT_DESC", pk_ids: List[str] = [], include_deleted: bool = False, **filter_fields
    ) -> BaseDaoListResponse:
        """list method for instances"""

        # validate inputs:
        if page < 0:
            raise ValueError("page must be >= 0")

        if size < 1 or size > 100:
            raise ValueError("size must be between 1 and 100")

        with self._db.session_factory() as session:
            # try to list instances:
            try:
                # initialize queryset:
                queryset = session.query(self._model_class)

                # remove deleted instances if not requested:
                if not include_deleted:
                    queryset = queryset.filter(getattr(self._model_class, "is_deleted") == False)  # noqa: E712

                # filter by ids if provided:
                if pk_ids:
                    queryset = queryset.filter(self._model_class.get_id_field().in_(pk_ids))

                # handle extra lookup fields:
                for field, value in filter_fields.items():
                    # continue if no value provided:
                    if value is None:
                        continue

                    # update queryset query using queryparser class:
                    queryset = QueryParser(self._model_class, queryset, field, value).construct_queryset()

                # determine count:
                count = queryset.count()

                # apply ordering:
                queryset = queryset.order_by(getattr(self._model_ordering_class, order_by))

                # apply pagination:
                queryset = queryset.limit(size).offset(page * size)
                results = queryset.all()

            # data exception:
            except exc.DataError as e:
                e = DataError(self, field, e)
                log.error(e.message, exc_info=e.message)
                raise e

        # convert to list:
        response = BaseDaoListResponse(results, count)

        # log number retrieved:
        log.debug(f'{self._model_class.__name__}.list() returned {response.count} items')

        return response
