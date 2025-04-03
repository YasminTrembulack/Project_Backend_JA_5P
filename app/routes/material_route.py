from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.material_service import MaterialService
from app.types.schemas import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MaterialPayload,
    MaterialResponse,
    MaterialUpdatePayload,
    Metadata,
)

router = APIRouter(prefix='/material')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MaterialResponse],
)
def create_material(
    material: MaterialPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MaterialService(session)
    db_material = service.material_register(material)
    material_response = MaterialResponse.model_validate(db_material.to_dict())
    return EntityResponse(
        message='Material created with success.', data=material_response
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[MaterialResponse],
)
def get_all_materials(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialService(session)
    materials, total_materials = service.get_all_materials(
        page, limit, order_by, desc_order
    )
    total_pages = (total_materials + limit - 1) // limit
    meta = Metadata(
        total=total_materials,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    materials = [MaterialResponse.model_validate(m.to_dict()) for m in materials]
    return GetAllResponse(
        message='Materials found successfully.', data=materials, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_material(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = MaterialService(session)
    service.delete_material(id)
    return DeleteResponse(message='Material deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MaterialResponse],
)
def update_material(
    id: str,
    material: MaterialUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MaterialService(session)
    material = service.update_material(id, material)
    material_response = MaterialResponse.model_validate(material.to_dict())
    return EntityResponse(
        message='Material updated successfully.', data=material_response
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MaterialResponse],
)
def get_material(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialService(session)
    material = service.get_material(id)
    material_response = MaterialResponse.model_validate(material.to_dict())
    return EntityResponse(
        message='Material found successfully.', data=material_response
    )
