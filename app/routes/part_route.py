from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.part_service import PartService
from app.types.schemas import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
    PartPayload,
    PartResponse,
    PartUpdatePayload,
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
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = PartService(session)
    parts, total_parts = service.get_all_parts(page, limit, order_by, desc_order)
    total_pages = (total_parts + limit - 1) // limit
    meta = Metadata(
        total=total_parts,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    parts = [PartResponse.model_validate(m.to_dict()) for m in parts]
    return GetAllResponse(
        message='Parts found successfully.', data=parts, metadata=meta
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
