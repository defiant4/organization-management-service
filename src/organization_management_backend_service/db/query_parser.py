import logging

from organization_management_backend_service._exceptions import InvalidFilterField
from organization_management_backend_service._exceptions import InvalidFilterMethod

log = logging.getLogger(__name__)


class QueryParser:
    """this class acts as a mapper to create filter methods"""

    def __init__(self, model, queryset, field, value):
        """the init method validates the filter_field dictionary"""

        # set queryset:
        self.model_class = model
        self.queryset = queryset

        # extract field and value:
        field_string = field
        field_value = value

        # get args:
        args = field_string.split('__')

        # determine if this is a method lookup:
        self.is_method_lookup = len(args) > 1

        # get lookup field:
        field = getattr(self.model_class, args[0], None)

        # raise error if field is not part of model:
        if not field:
            exception = InvalidFilterField(model, args[0])
            log.error(exception.message, exc_info=exception.message)
            raise exception

        # set field and value:
        self.field = field
        self.value = field_value
        self.method = args[1] if self.is_method_lookup else None

    def construct_queryset(self):
        """this method converts a keyword argument and value into a SQLAlchemy filter statement"""

        # unpack:
        field = self.field
        value = self.value
        method = self.method
        queryset = self.queryset

        # simple lookup:
        if not self.is_method_lookup:
            return queryset.filter(field == value)

        # list includes lookup:
        elif method == "in":
            return queryset.filter(field.in_(value))

        # str contains lookup:
        elif method == "contains":
            return queryset.filter(field.contains(value))

        # str contains lookup:
        elif method == "icontains":
            print(field, value, method)
            return queryset.filter(field.ilike(f"%{value}%"))

        # greater than lookup:
        elif method == "gt":
            return self.queryset.filter(field > value)

        # greater than equal to lookup:
        elif method == "gte":
            return self.queryset.filter(field >= value)

        # greater than lookup:
        elif method == "lt":
            return self.queryset.filter(field < value)

        # greater than equal to lookup:
        elif method == "lte":
            return self.queryset.filter(field <= value)

        # raise exception on invalid method:
        else:
            exception = InvalidFilterMethod(self.model_class, field, method)
            log.error(exception.message, exc_info=exception.message)
            raise exception
