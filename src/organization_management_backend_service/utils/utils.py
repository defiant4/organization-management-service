import logging
from typing import Any
from typing import Union

from organization_management_backend_service.dao.base_dao import BaseDaoListResponse
from organization_management_backend_service.dao.oms_dao import OrganizationsDAO
from organization_management_backend_service.dao.oms_dao import UsersDAO

logger = logging.getLogger(__name__)


def fetch_row_based_on_column(
    dao: Union[OrganizationsDAO, UsersDAO],
    column_name: str,
    column_type_filter_value: str,
    page_offset: int = 0,
    max_pages: int = 10,
    order_by: str = "CREATED_AT_ASC",
) -> Any:
    """
    Fetch the desired row based on column filter value.
    """
    records_list = []
    max_pages: int = 10
    page_offset: int = 0
    order_by: str = "CREATED_AT_ASC"
    while max_pages > 0:
        logger.info(f"Fetching page: {page_offset}")
        users_response: BaseDaoListResponse = dao.list(page=page_offset, order_by=order_by, **{column_name: column_type_filter_value})
        logger.info(f"For page: {page_offset} fetched items count: {users_response.count}")
        if users_response.count > 0:
            records_list.extend(users_response.items)
            break
        page_offset += 1
        # this to cap runs at a default to avoid infinite loops
        max_pages -= 1
        logger.info(f"Fetching page: {page_offset} next")
    return records_list
