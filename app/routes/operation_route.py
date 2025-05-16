from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.operation_service import OperationService
from app.types.base import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
)
from app.types.operation import (
    OperationPayload,
    OperationQueryParams,
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
    service = OperationService(session)
    db_operation = service.operation_register(operation)
    operation_response = OperationResponse.model_validate(db_operation.to_dict())
    return EntityResponse(
        message='Operation created with success.', data=operation_response
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[OperationResponse],
)
def get_all_operations(
    query: OperationQueryParams = Depends(),
    associations: List[Literal['machine']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = OperationService(session)
    operations, total_operations = service.get_all_operations(
        query.page, query.limit, query.order_by, query.desc_order
    )
    total_pages = (total_operations + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_operations,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    operations_response = []

    for op in operations:
        operations_dict = op.to_dict()
        associations_dict = service.configure_associations_response(op, associations)
        combined_dict = {**operations_dict, **associations_dict}

        operations_response.append(OperationResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Operations found successfully.',
        data=operations_response,
        metadata=meta,
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
    service = OperationService(session)
    service.delete_operation(id)
    return DeleteResponse(message='Operation deleted successfully.')


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
    service = OperationService(session)
    operation = service.update_operation(id, operation)
    operation_response = OperationResponse.model_validate(operation.to_dict())
    return EntityResponse(
        message='Operation updated successfully.', data=operation_response
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
    service = OperationService(session)
    operation = service.get_operation(id)
    operation_response = OperationResponse.model_validate(operation.to_dict())
    return EntityResponse(
        message='Operation found successfully.', data=operation_response
    )
