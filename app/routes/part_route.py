from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.part_service import PartService
from app.types.base import Metadata
from app.types.payload import (
    PartPayload,
    PartQueryParams,
    PartUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    PartResponse,
)

router = APIRouter(prefix='/part')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[PartResponse],
)
def create_part(
    part: PartPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = PartService(session)

    db_part = service.part_register(part)

    part_response = PartResponse.model_validate(db_part.to_dict())
    return EntityResponse(message='Part created with success.', data=part_response)


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[PartResponse],
)
def get_all_parts(
    q: PartQueryParams = Depends(),
    associations: List[
        Literal['mold', 'operation_associations', 'material_associations']
    ] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = PartService(session)
    parts, total_parts = service.get_all_parts(
        q.page, q.limit, q.order_by, q.desc_order, q.field, q.value
    )
    total_pages = (total_parts + q.limit - 1) // q.limit
    meta = Metadata(
        total=total_parts,
        limit=q.limit,
        page=q.page,
        total_pages=total_pages,
        has_next=q.page < total_pages,
        has_previous=q.page > 1,
        order_by=q.order_by,
        desc_order=q.desc_order,
    )

    parts_reponse = []

    for p in parts:
        part_dict = p.to_dict()
        associations_dict = service.configure_associations_response(p, associations)
        combined_dict = {**part_dict, **associations_dict}

        parts_reponse.append(PartResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Parts found successfully.', data=parts_reponse, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_part(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = PartService(session)
    service.delete_part(id)
    return DeleteResponse(message='Part deleted successfully.')


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[PartResponse],
)
def get_part(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = PartService(session)
    part = service.get_part(id)
    part_response = PartResponse.model_validate(part.to_dict())
    return EntityResponse(message='Part found successfully.', data=part_response)


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[PartResponse],
)
def update_part(
    id: str,
    part: PartUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = PartService(session)
    part = service.update_part(id, part)
    part_response = PartResponse.model_validate(part.to_dict())
    return EntityResponse(message='Part updated successfully.', data=part_response)
