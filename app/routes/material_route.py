from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.material_service import MaterialService
from app.types.base import Metadata
from app.types.payload import (
    MaterialPayload,
    MaterialQueryParams,
    MaterialUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MaterialResponse,
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
    query: MaterialQueryParams = Depends(),
    associations: List[Literal['parts', 'part_associations']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialService(session)
    materials, total_materials = service.get_all_materials(query)
    total_pages = (total_materials + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_materials,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
        value=query.value,
        field=query.field
    )

    materials_response = []

    for m in materials:
        material_part_dict = m.to_dict()
        associations_dict = service.configure_associations_response(m, associations)
        combined_dict = {**material_part_dict, **associations_dict}

        materials_response.append(MaterialResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Materials found successfully.',
        data=materials_response,
        metadata=meta,
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
