from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.user_service import UserService
from app.types.schemas import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    Metadata,
    UserPayload,
    UserResponse,
    UserUpdatePayload,
)

router = APIRouter(prefix='/user')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[UserResponse],
)
def create_user(
    user: UserPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = UserService(session)
    db_user = service.user_register(user)
    user_response = UserResponse.model_validate(db_user.to_dict())
    return EntityResponse(message='User created with success.', data=user_response)


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[UserResponse],
)
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('full_name'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = UserService(session)
    users, total_users = service.get_all_users(page, limit, order_by, desc_order)
    total_pages = (total_users + limit - 1) // limit
    meta = Metadata(
        total=total_users,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    users = (user.to_dict() for user in users)
    return GetAllResponse(
        message='Users found successfully.', data=users, metadata=meta
    )


@router.delete(
    '/delete',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_user(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = UserService(session)
    service.delete_user(id)
    return DeleteResponse(message='User deleted successfully.')


@router.patch(
    '/update',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[UserResponse],
)
def update_user(
    id: str,
    user: UserUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = UserService(session)
    user = service.update_user(id, user)
    user_response = UserResponse.model_validate(user.to_dict())
    return EntityResponse(message='User updated successfully.', data=user_response)
