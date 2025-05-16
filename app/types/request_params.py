from typing import List

from pydantic import BaseModel, field_validator

MAX_LIMIT = 50
MIN_LIMIT = 1

def create_query_params_class(
    name: str,
    allowed_associations: List[str],
    allowed_order_by: List[str]
):
    class QueryParams(BaseModel):
        page: int = 1
        limit: int = 10
        order_by: str = 'created_at'
        desc_order: bool = False
        associations: List[str] = []

        @field_validator('limit')
        def check_limit(cls, v):
            if v < MIN_LIMIT or v > MAX_LIMIT:
                raise ValueError(f'Limit must be between {MIN_LIMIT} and {MAX_LIMIT}')
            return v
        
        @field_validator('associations', each_item=True)
        def check_association(cls, v):
            if v not in allowed_associations:
                raise ValueError(f"Invalid association '{v}'. Allowed: {allowed_associations}")
            return v

        @field_validator('order_by')
        def check_order_by(cls, v):
            if v not in allowed_order_by:
                raise ValueError(f"Invalid order_by '{v}'. Allowed: {allowed_order_by}")
            return v

    QueryParams.__name__ = name
    return QueryParams


