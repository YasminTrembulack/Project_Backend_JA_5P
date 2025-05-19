from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.mold_service import MoldService
from app.types.base import Metadata
from app.types.payload import (
    MoldPayload,
    MoldQueryParams,
    MoldUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MoldResponse,
)

router = APIRouter(prefix='/mold')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MoldResponse],
)
def create_mold(
    mold: MoldPayload,
    session: Session = Depends(get_session),
    user: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MoldService(session)

    mold.created_by_id = user.id
    db_mold = service.mold_register(mold)

    mold_response = MoldResponse.model_validate(db_mold.to_dict())
    return EntityResponse(message='Mold created with success.', data=mold_response)


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[MoldResponse],
)
def get_all_molds(
    query: MoldQueryParams = Depends(),
    associations: List[
        Literal['customer', 'mold_parts', 'operation_associations', 'created_by']
    ] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MoldService(session)
    molds, total_molds = service.get_all_molds(
        query.page, query.limit, query.order_by, query.desc_order
    )
    total_pages = (total_molds + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_molds,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    molds_response = []

    for m in molds:
        mold_dict = m.to_dict()
        associations_dict = service.configure_associations_response(m, associations)
        combined_dict = {**mold_dict, **associations_dict}

        molds_response.append(MoldResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Molds found successfully.', data=molds_response, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_mold(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = MoldService(session)
    service.delete_mold(id)
    return DeleteResponse(message='Mold deleted successfully.')


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MoldResponse],
)
def get_mold(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MoldService(session)
    mold = service.get_mold(id)
    mold_response = MoldResponse.model_validate(mold.to_dict())
    return EntityResponse(message='Mold found successfully.', data=mold_response)


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MoldResponse],
)
def update_mold(
    id: str,
    mold: MoldUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MoldService(session)
    mold = service.update_mold(id, mold)
    mold_response = MoldResponse.model_validate(mold.to_dict())
    return EntityResponse(message='Mold updated successfully.', data=mold_response)
