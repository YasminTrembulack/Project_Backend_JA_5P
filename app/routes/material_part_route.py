from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.material_part_service import MaterialPartService
from app.types.base import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
)
from app.types.material_part import (
    MaterialPartPayload,
    MaterialPartResponse,
    MaterialPartUpdatePayload,
)

router = APIRouter(prefix='/material_part')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MaterialPartResponse],
)
def create_material_part(
    material_part: MaterialPartPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MaterialPartService(session)
    db_material_part = service.material_part_register(material_part)
    material_part_response = MaterialPartResponse.model_validate(
        db_material_part.to_dict()
    )
    return EntityResponse(
        message='Material Part created with success.',
        data=material_part_response,
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[MaterialPartResponse],
)
def get_all_material_part(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialPartService(session)
    material_parts, total_material_parts = service.get_all_material_parts(
        page, limit, order_by, desc_order
    )
    total_pages = (total_material_parts + limit - 1) // limit
    meta = Metadata(
        total=total_material_parts,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    material_parts = [
        MaterialPartResponse.model_validate(m.to_dict()) for m in material_parts
    ]
    return GetAllResponse(
        message='Material Part found successfully.',
        data=material_parts,
        metadata=meta,
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_material_part(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = MaterialPartService(session)
    service.delete_material_part(id)
    return DeleteResponse(message='Material Part deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MaterialPartResponse],
)
def update_material_part(
    id: str,
    material_part: MaterialPartUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MaterialPartService(session)
    material_part = service.update_material_part(id, material_part)
    material_part_response = MaterialPartResponse.model_validate(
        material_part.to_dict()
    )
    return EntityResponse(
        message='Material Part updated successfully.',
        data=material_part_response,
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MaterialPartResponse],
)
def get_material_part(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialPartService(session)
    material_part = service.get_material_part(id)
    material_part_response = MaterialPartResponse.model_validate(
        material_part.to_dict()
    )
    return EntityResponse(
        message='Material Part found successfully.',
        data=material_part_response,
    )
