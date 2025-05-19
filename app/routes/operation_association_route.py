from typing import List, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.operation_association_service import OperationAssociationService
from app.types.base import Metadata
from app.types.payload import (
    OperationAssociationPayload,
    OperationAssociationQueryParams,
    OperationAssociationUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    OperationAssociationResponse,
)

router = APIRouter(prefix='/operation_association')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[OperationAssociationResponse],
)
def create_operation_association(
    operation_association: OperationAssociationPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = OperationAssociationService(session)
    db_operation_association = service.operation_association_register(
        operation_association
    )
    operation_association_response = OperationAssociationResponse.model_validate(
        db_operation_association.to_dict()
    )
    return EntityResponse(
        message='Operation Association created with success.',
        data=operation_association_response,
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[OperationAssociationResponse],
)
def get_all_operation_association(
    query: OperationAssociationQueryParams = Depends(),
    associations: List[Literal['operation', 'part', 'model']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = OperationAssociationService(session)
    operation_associations, total_operation_associations = (
        service.get_all_operation_associations(
            query.page, query.limit, query.order_by, query.desc_order
        )
    )
    total_pages = (total_operation_associations + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_operation_associations,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    operation_associations_response = []

    for oa in operation_associations:
        operation_associations_dict = oa.to_dict()
        associations_dict = service.configure_associations_response(oa, associations)
        combined_dict = {**operation_associations_dict, **associations_dict}

        operation_associations_response.append(
            OperationAssociationResponse.model_validate(combined_dict)
        )
        
    return GetAllResponse(
        message='Operation Associations found successfully.',
        data=operation_associations_response,
        metadata=meta,
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_operation_association(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = OperationAssociationService(session)
    service.delete_operation_association(id)
    return DeleteResponse(message='Operation Association deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[OperationAssociationResponse],
)
def update_operation_association(
    id: str,
    operation_association: OperationAssociationUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = OperationAssociationService(session)
    operation_association = service.update_operation_association(
        id, operation_association
    )
    operation_association_response = OperationAssociationResponse.model_validate(
        operation_association.to_dict()
    )
    return EntityResponse(
        message='Operation Association updated successfully.',
        data=operation_association_response,
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[OperationAssociationResponse],
)
def get_operation_association(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = OperationAssociationService(session)
    operation_association = service.get_operation_association(id)
    operation_association_response = OperationAssociationResponse.model_validate(
        operation_association.to_dict()
    )
    return EntityResponse(
        message='Operation Association found successfully.',
        data=operation_association_response,
    )
