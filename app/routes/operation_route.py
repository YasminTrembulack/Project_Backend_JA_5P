from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.operation_service import operationService
from app.types.schemas import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
    OperationPayload,
    OperationResponse,
    OperationUpdatePayload,
)

router = APIRouter(prefix='/operation')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[OperationResponse],
)
def create_operation(
    operation: OperationPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = operationService(session)
    db_operation = service.operation_register(operation)
    operation_response = OperationResponse.model_validate(db_operation.to_dict())
    return EntityResponse(
        message='operation created with success.', data=operation_response
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[OperationResponse],
)
def get_all_operations(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = operationService(session)
    operations, total_operations = service.get_all_operations(
        page, limit, order_by, desc_order
    )
    total_pages = (total_operations + limit - 1) // limit
    meta = Metadata(
        total=total_operations,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    operations = [OperationResponse.model_validate(m.to_dict()) for m in operations]
    return GetAllResponse(
        message='operations found successfully.', data=operations, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_operation(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = operationService(session)
    service.delete_operation(id)
    return DeleteResponse(message='operation deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[OperationResponse],
)
def update_operation(
    id: str,
    operation: OperationUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = operationService(session)
    operation = service.update_operation(id, operation)
    operation_response = OperationResponse.model_validate(operation.to_dict())
    return EntityResponse(
        message='operation updated successfully.', data=operation_response
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[OperationResponse],
)
def get_operation(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = operationService(session)
    operation = service.get_operation(id)
    operation_response = OperationResponse.model_validate(operation.to_dict())
    return EntityResponse(
        message='operation found successfully.', data=operation_response
    )
