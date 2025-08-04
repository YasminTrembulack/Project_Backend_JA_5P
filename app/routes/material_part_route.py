from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.material_part_service import MaterialPartService
from app.types.base import Metadata
from app.types.payload import (
    MaterialPartPayload,
    MaterialPartQueryParams,
    MaterialPartUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MaterialPartResponse,
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
    query: MaterialPartQueryParams = Depends(),
    associations: List[Literal['material', 'part']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MaterialPartService(session)
    material_parts, total_material_parts = service.get_all_material_parts(
        query.page, query.limit, query.order_by, query.desc_order
    )
    total_pages = (total_material_parts + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_material_parts,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    material_parts_response = []

    for mp in material_parts:
        material_part_dict = mp.to_dict()
        associations_dict = service.configure_associations_response(mp, associations)
        combined_dict = {**material_part_dict, **associations_dict}

        material_parts_response.append(
            MaterialPartResponse.model_validate(combined_dict)
        )

    return GetAllResponse(
        message='Material Part found successfully.',
        data=material_parts_response,
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
