from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.customer_service import CustomerService
from app.types.base import Metadata
from app.types.payload import (
    CustomerPayload,
    CustomerQueryParams,
    CustomerUpdatePayload,
)
from app.types.response import (
    CustomerResponse,
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
)

router = APIRouter(prefix='/customer')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[CustomerResponse],
)
def create_customer(
    customer: CustomerPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = CustomerService(session)
    db_customer = service.customer_register(customer)
    customer_response = CustomerResponse.model_validate(db_customer.to_dict())
    return EntityResponse(
        message='Customer created with success.', data=customer_response
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[CustomerResponse],
)
def get_all_customers(
    query: CustomerQueryParams = Depends(),
    associations: List[Literal['molds']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = CustomerService(session)
    customers, total_customers = service.get_all_customers(
        query.page, query.limit, query.order_by, query.desc_order
    )
    total_pages = (total_customers + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_customers,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    customer_response = []

    for c in customers:
        customer_dict = c.to_dict()
        associations_dict = service.configure_associations_response(c, associations)
        combined_dict = {**customer_dict, **associations_dict}

        customer_response.append(CustomerResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Customers found successfully.',
        data=customer_response,
        metadata=meta,
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_customer(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = CustomerService(session)
    service.delete_customer(id)
    return DeleteResponse(message='Customer deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[CustomerResponse],
)
def update_customer(
    id: str,
    customer: CustomerUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = CustomerService(session)
    customer = service.update_customer(id, customer)
    customer_response = CustomerResponse.model_validate(customer.to_dict())
    return EntityResponse(
        message='Customer updated successfully.', data=customer_response
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[CustomerResponse],
)
def get_customer(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = CustomerService(session)
    customer = service.get_customer(id)
    customer_response = CustomerResponse.model_validate(customer.to_dict())
    return EntityResponse(
        message='Customer found successfully.', data=customer_response
    )
