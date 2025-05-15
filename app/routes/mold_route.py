from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.mold_service import MoldService
from app.types.schemas import (
    CustomerResponse,
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
    MoldPayload,
    MoldResponde,
    MoldUpdatePayload,
    UserResponse,
)

router = APIRouter(prefix='/mold')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MoldResponde],
)
def create_mold(
    mold: MoldPayload,
    session: Session = Depends(get_session),
    user: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MoldService(session)

    mold.created_by_id = user.id
    db_mold = service.mold_register(mold)

    mold_response = MoldResponde.model_validate(db_mold.to_dict())
    return EntityResponse(message='Mold created with success.', data=mold_response)


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[MoldResponde],
)
def get_all_molds(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MoldService(session)
    molds, total_molds = service.get_all_molds(page, limit, order_by, desc_order)
    total_pages = (total_molds + limit - 1) // limit
    meta = Metadata(
        total=total_molds,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    
    molds_response = []

    for m in molds:
        mold_dict = m.to_dict()
        
        mold_dict["customer"] = CustomerResponse.model_validate(m.customer.to_dict())
        mold_dict["created_by"] = UserResponse.model_validate(m.created_by.to_dict())

        molds_response.append(MoldResponde.model_validate(mold_dict))
        
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
    response_model=EntityResponse[MoldResponde],
)
def get_mold(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MoldService(session)
    mold = service.get_mold(id)
    mold_response = MoldResponde.model_validate(mold.to_dict())
    return EntityResponse(message='Mold found successfully.', data=mold_response)


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MoldResponde],
)
def update_mold(
    id: str,
    mold: MoldUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MoldService(session)
    mold = service.update_mold(id, mold)
    mold_response = MoldResponde.model_validate(mold.to_dict())
    return EntityResponse(message='Mold updated successfully.', data=mold_response)
