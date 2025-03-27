from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.customer_service import CustomerService
from app.types.schemas import (
    CustomerPayload,
    CustomerResponse,
    CustomerUpdatePayload,
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
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
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('full_name'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = CustomerService(session)
    customers, total_customers = service.get_all_customers(
        page, limit, order_by, desc_order
    )
    total_pages = (total_customers + limit - 1) // limit
    meta = Metadata(
        total=total_customers,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    customers = [
        CustomerResponse.model_validate(user.to_dict()) for user in customers
    ]
    return GetAllResponse(
        message='Customers found successfully.', data=customers, metadata=meta
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
